#!/usr/bin/env python3
"""Le partage des 23 points entre le salarié et l'employeur : qui gagne quoi, et quand.

    python scripts/partage_taux_unique.py                  # les quatre partages, salarié non cadre
    python scripts/partage_taux_unique.py --volontaire     # le net après les 5 % rendus, placés
    python scripts/partage_taux_unique.py --niveaux 1 1.3 2 # d'autres niveaux, en SMIC
    python scripts/partage_taux_unique.py --statut salarie_prive_cadre

LA QUESTION
-----------
La proposition prélève 23 points sur la rémunération — 18 de répartition,
5 capitalisés — là où un salarié du privé en verse aujourd'hui 27,98 : 11,31
sur sa fiche, 16,67 chez son employeur, contributions d'équilibre comprises.
Elle dit « salariale et patronale additionnées » et ne dit pas qui porte quoi.
Le modèle partage moitié-moitié (``Parametres.part_salariale_taux_unique``),
et ``remuneration.py`` a montré que ce partage n'est pas neutre. Ce script
répond à la question suivante : **quel partage sert le mieux le salaire, de
façon réaliste, sans promettre ce qu'on ne peut pas tenir ?**

DEUX HORIZONS, ET LES DEUX SONT VRAIS
--------------------------------------
``jour 1`` — le salaire brut ne bouge pas. C'est la fiche de paie du
    lendemain de la réforme : le salarié voit sa part changer, l'employeur
    voit la sienne changer, et rien d'autre. C'est :data:`Incidence.ASSIETTE`.
``long terme`` — le coût du travail ne bouge pas. Ce que l'employeur ne verse
    plus finit dans le brut, après quelques années de négociations et
    d'embauches : c'est l'incidence intégrale du site,
    :data:`Incidence.COUT_DU_TRAVAIL`, et c'est une hypothèse.

Une baisse de la part SALARIALE arrive au jour 1 et reste. Une baisse de la
part PATRONALE profite d'abord à l'employeur, puis remonte dans le brut — et
en remontant, elle grossit l'assiette de la CSG (9,7 %) et des cotisations des
autres branches (26 points de maladie, famille, chômage, AT-MP…) : un quart
en fuit vers elles avant d'arriver au net. Le tableau « qui paie » le mesure.

LE COULOIR
----------
Quatre partages, bornés par deux évidences :

    A  la part patronale ne bouge pas (16,67 points), toute la baisse va au
       salarié, dont la part tombe de 11,31 à 6,33 ;
    B  la clé d'aujourd'hui, 40,4 % : chaque part baisse d'un cinquième ;
    C  la part salariale ne bouge pas (11,31), toute la baisse va à
       l'employeur, dont la part tombe de 16,67 à 11,69 ;
    D  moitié-moitié, le défaut du dépôt : la part salariale MONTE de 11,31
       à 11,50, et la fiche de paie du jour 1 baisse.

En deçà de A l'employeur paie plus qu'aujourd'hui ; au-delà de C le salarié
paie plus qu'aujourd'hui. Pour A, B et C, une variante ``'`` porte les cinq
points capitalisés sur le seul salarié — c'est son capital, transmissible — et
ajuste le partage des 18 pour garder la même part salariale totale ; elle
retire le seul cas où le coût du travail monte au jour 1, au SMIC, parce que
le pilier capitalisé n'entre pas dans le périmètre de la réduction générale.

Depuis l'action 55, les cinq points RENDUS ne sont plus une retenue sur la
fiche : ``--volontaire`` les retranche du net, comme un placement, et ne touche
ni au brut ni au coût du travail.

Le crédit au compte — 23 % du brut, ce qui devient pension et capital — suit
le brut : il monte avec la part patronale au long terme, et ne change pas au
jour 1. Tous les montants sont mensuels, en euros de l'année de la bascule,
pour un salarié dont l'employeur compte cinquante salariés et plus.
"""

from __future__ import annotations

import argparse

from retraite_notionnelle import Parametres
from retraite_notionnelle.carriere import Affiliations
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.remuneration import (
    BlocRetraite,
    ComposanteRetraite,
    ConstructeurFiche,
    Segment,
    bloc_droit_en_vigueur,
    bloc_taux_unique,
    charger_prelevements,
    smic_annuel,
)

NIVEAUX_PAR_DEFAUT = (1.0, 1.2, 1.5, 2.0, 3.0, 4.0)


def bloc_propose(parametres: Parametres, part_salariale: float,
                 part_salariale_capitalisation: float | None = None,
                 ) -> BlocRetraite:
    """Le bloc de la proposition, avec un partage propre au pilier capitalisé si demandé.

    Les cinq points VOLONTAIRES n'y sont pas, depuis l'action 55 : ils ne sont
    pas une retenue mais un placement pris sur le net, et ``--volontaire`` les
    retranche du net au lieu de les prélever sur le brut.
    """
    bloc = bloc_taux_unique(
        parametres.taux_cotisation_liberal,
        parametres.taux_capitalisation_obligatoire,
        part_salariale,
    )
    if part_salariale_capitalisation is None:
        return bloc
    taux = parametres.taux_capitalisation_obligatoire
    composantes = []
    for composante in bloc.composantes:
        if composante.code == "capitalisation":
            composante = ComposanteRetraite(
                code=composante.code, libelle=composante.libelle,
                salarie=(Segment(0.0, None, taux * part_salariale_capitalisation),),
                employeur=(Segment(0.0, None,
                                   taux * (1.0 - part_salariale_capitalisation)),),
                dans_la_reduction_generale=False,
            )
        composantes.append(composante)
    return BlocRetraite(libelle=bloc.libelle, composantes=tuple(composantes),
                        remplace_les_contributions_d_equilibre=True)


def _csg(fiche) -> float:
    return sum(ligne.salarie for ligne in fiche.lignes if ligne.code == "csg_crds")


def _autres_patronales(fiche) -> float:
    return sum(ligne.employeur for ligne in fiche.lignes if not ligne.retraite)


def _retraite(fiche) -> float:
    return fiche.retraite_salarie + fiche.retraite_employeur


def main() -> None:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analyseur.add_argument("--statut", default="salarie_prive_non_cadre")
    analyseur.add_argument("--niveaux", nargs="+", type=float,
                           default=NIVEAUX_PAR_DEFAUT, metavar="SMIC")
    analyseur.add_argument("--volontaire", action="store_true",
                           help="retranche du net les 5 %% rendus, placés par l'assuré")
    analyseur.add_argument("--detail", type=float, default=2.0, metavar="SMIC",
                           help="niveau auquel décomposer « qui paie » (défaut : 2 SMIC)")
    args = analyseur.parse_args()

    parametres = Parametres()
    annee = parametres.annee_bascule
    macro = DonneesMacro(parametres.racine_donnees, parametres.scenario_projection)
    catalogue = CatalogueRegimes(parametres.racine_donnees)
    affiliations = Affiliations(parametres.racine_donnees)
    profil = charger_prelevements(parametres.racine_donnees).profil("salarie_prive")
    constructeur = ConstructeurFiche(profil)
    plafond = macro.plafond_securite_sociale(annee)
    smic = smic_annuel(macro, annee)
    cadre = "cadre" in args.statut and "non_cadre" not in args.statut
    actuel = bloc_droit_en_vigueur(catalogue, affiliations, args.statut, annee)
    taux_volontaire = (parametres.taux_capitalisation_volontaire
                       if args.volontaire else 0.0)

    repartition = parametres.taux_cotisation_liberal
    capitalise = parametres.taux_capitalisation_obligatoire
    total = repartition + capitalise

    # Les parts d'aujourd'hui, lues sur la fiche de paie sous le plafond.
    temoin = constructeur.fiche(annee, 1.5 * smic, plafond, smic, actuel, cadre)
    part_salarie = temoin.retraite_salarie / temoin.brut
    part_employeur = temoin.retraite_employeur / temoin.brut

    partages = [
        ("A  part patronale inchangée", 1.0 - part_employeur / total, None),
        ("B  clé d'aujourd'hui", part_salarie / (part_salarie + part_employeur), None),
        ("C  part salariale inchangée", part_salarie / total, None),
        ("D  moitié-moitié (défaut du dépôt)", 0.5, None),
    ]
    variantes = []
    for nom, part, _ in partages[:3]:
        part_18 = (total * part - capitalise) / repartition
        if 0.0 <= part_18 <= 1.0:
            variantes.append((nom.replace("  ", "' ", 1) + ", capitalisé au seul salarié",
                              part_18, 1.0))
    partages = partages[:3] + variantes + partages[3:]

    print(f"Année {annee}, {args.statut}. SMIC {smic:,.0f} €/an, plafond {plafond:,.0f} €.")
    print(f"Aujourd'hui, sous le plafond : salarié {part_salarie * 100:.2f} points, "
          f"employeur {part_employeur * 100:.2f}, total {(part_salarie + part_employeur) * 100:.2f}.")
    print(f"Proposition : {total * 100:.0f} points ({repartition * 100:.0f} de répartition, "
          f"{capitalise * 100:.0f} capitalisés)"
          + (f", plus {taux_volontaire * 100:.0f} points rendus que l'assuré replace "
             "sur son net." if taux_volontaire else "."))
    print("Montants mensuels en euros courants ; « jour 1 » à brut fixe, "
          "« long terme » à coût du travail fixe.\n")

    for nom, part, part_cap in partages:
        bloc = bloc_propose(parametres, part, part_cap)
        salarie_pts = sum(s.taux for c in bloc.composantes for s in c.salarie) * 100
        employeur_pts = sum(s.taux for c in bloc.composantes for s in c.employeur) * 100
        print(f"=== {nom} — salarié {salarie_pts:.2f} pts, employeur {employeur_pts:.2f} pts")
        print(f"  {'SMIC':>5} {'brut':>6} {'net':>6} | {'J1 Δnet':>8} {'J1 Δcoût':>9} | "
              f"{'LT Δbrut':>9} {'LT Δnet':>8} | {'crédit J1':>9} {'crédit LT':>9}")
        detail = None
        for niveau in args.niveaux:
            brut = niveau * smic
            avant = constructeur.fiche(annee, brut, plafond, smic, actuel, cadre)
            jour_1 = constructeur.fiche(annee, brut, plafond, smic, bloc, cadre)
            brut_lt = constructeur.brut_a_cout_donne(
                avant.cout_du_travail, plafond, smic, bloc, cadre)
            long_terme = constructeur.fiche(annee, brut_lt, plafond, smic, bloc, cadre)
            m = 12.0
            # Le placement volontaire est pris sur le net, sur l'assiette de la
            # proposition : il ne touche ni au brut, ni au coût du travail.
            net_j1 = jour_1.net - taux_volontaire * jour_1.brut
            net_lt = long_terme.net - taux_volontaire * long_terme.brut
            alerte = ("  brut < SMIC, impossible en droit"
                      if brut_lt < smic * (1 - 1e-4) else "")
            print(f"  {niveau:>5.1f} {brut / m:>6.0f} {avant.net / m:>6.0f} | "
                  f"{(net_j1 - avant.net) / m:>+8.0f} "
                  f"{(jour_1.cout_du_travail - avant.cout_du_travail) / m:>+9.0f} | "
                  f"{(brut_lt / brut - 1) * 100:>+8.1f}% {(net_lt - avant.net) / m:>+8.0f} | "
                  f"{total * brut / m:>9.0f} {total * brut_lt / m:>9.0f}{alerte}")
            if abs(niveau - args.detail) < 1e-9:
                detail = (avant, long_terme, net_lt)
        if detail is not None:
            avant, apres, net_lt = detail
            m = 12.0
            d_retraite = (_retraite(apres) - _retraite(avant)) / m
            d_csg = (_csg(apres) - _csg(avant)) / m
            d_autres = (_autres_patronales(apres) - _autres_patronales(avant)) / m
            d_reduction = (apres.reduction_generale - avant.reduction_generale) / m
            d_net = (net_lt - avant.net) / m
            d_place = -taux_volontaire * apres.brut / m
            print(f"  Qui paie le net du long terme, à {args.detail:g} SMIC : "
                  f"la retraite prélève {d_retraite:+.0f} ; "
                  f"la CSG-CRDS {d_csg:+.0f}, les autres branches {d_autres:+.0f} "
                  f"(l'assiette a bougé) ; l'allègement bas salaires {d_reduction:+.0f} "
                  f"(l'État) ; "
                  + (f"le placement volontaire {d_place:+.0f} ; " if taux_volontaire else "")
                  + f"reste au salarié {d_net:+.0f}.")
        print()


if __name__ == "__main__":
    main()
