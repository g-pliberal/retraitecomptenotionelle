#!/usr/bin/env python3
"""Le chiffrage budgétaire de la proposition, année par année, pour un PLF.

    python scripts/chiffrage_plf.py             # réécrit le document et la série
    python scripts/chiffrage_plf.py --verifier  # échoue s'ils sont périmés

CE QU'IL PRODUIT
----------------
``docs/chiffrage_plf.md`` porte la prose — les conventions de lecture, la
pondération du recensement, les hypothèses fragiles —, et ce script y écrit
entre repères tout ce qui est un chiffre : le fait central, le tableau des
arbitrages, les quatre tableaux annuels, les prélèvements et les agrégats. La
série annuelle complète part dans ``docs/chiffrage_plf.csv``, séparateur ``;``
et virgule décimale, pour un tableur.

POURQUOI UN SCRIPT ET NON UNE PROSE ÉCRITE À LA MAIN
----------------------------------------------------
C'est le geste de ``construire_tableaux_md.py`` et de
``construire_regimes_md.py``, et il vaut ici plus qu'ailleurs : un chiffrage
budgétaire est exactement le genre de document que personne ne relit après une
modification du modèle, et dont les chiffres se périment en silence. Ceux-ci
sont recalculés, et ``tests/test_prose.py`` refuse un document qui ne serait
plus celui que ce script produit.

CE QU'IL CHIFFRE, ET LES DEUX VARIANTES
----------------------------------------
Le scénario 6 — taux unique de 18 % en répartition, 5 % de capitalisation
obligatoire en plus, garantie vieillesse financée par l'impôt — sous ses deux
formes :

- **rétroactive**, la convention par défaut du dépôt : toutes les pensions,
  déjà liquidées comprises, sont recalculées en comptes notionnels depuis 1941 ;
- **prospective**, empruntée à ``scripts/proposition_prospective.py`` : les
  droits acquis sont figés à la bascule, et aucune pension en cours ne bouge.

L'écart entre les deux est le premier fait budgétaire du dossier, et c'est
pourquoi les deux sont dans le document plutôt qu'une seule.

CE QU'IL NE FAIT PAS
--------------------
Il ne calcule rien qui ne soit déjà dans ``cout.calculer_cout`` : il lit un
``Solde`` et un ``Avenir`` aux paramètres par défaut, et les met en tableau. Un
chiffre qui bouge ici a bougé dans le modèle.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts"))

from proposition_prospective import PropositionProspective  # noqa: E402
from retraite_notionnelle import cout as C  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.equilibre import ComptesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

LIBERAL = "notionnel_liberal"

DOCUMENT = "docs/chiffrage_plf.md"
SERIE = "docs/chiffrage_plf.csv"

#: L'horizon du triennal budgétaire d'un PLF, puis la trajectoire longue. Les
#: années annuelles s'arrêtent à 2040 parce qu'au-delà un tableau annuel ne se
#: lit plus ; la série complète est dans le CSV.
ANNEES_ANNUELLES: tuple[int, ...] = tuple(range(2026, 2041))
ANNEES_LONGUES: tuple[int, ...] = (2045, 2050, 2055, 2060, 2065, 2070)
ANNEES_PRELEVEMENTS: tuple[int, ...] = (2026, 2030, 2035, 2040, 2050, 2060, 2070)

#: Première année du chiffrage : celle de la bascule. Avant elle, le scénario 6
#: prélève les taux réels et ses masses sont un contrefactuel du passé, qui
#: n'a rien à faire dans un projet de loi de finances.
PREMIERE_ANNEE = 2026


def nombre(valeur: float, decimales: int = 1, signe: bool = False) -> str:
    """« 1 538,2 » : virgule décimale, espace ordinaire pour les milliers.

    C'est la typographie du dépôt, celle que `verifier_prose.py` sait relire.
    """
    format_ = f"{{:{'+' if signe else ''},.{decimales}f}}"
    return format_.format(valeur).replace(",", " ").replace(".", ",")


class Chiffrage:
    """Les deux variantes, lues une fois, et ce qu'on en tire.

    Les grandeurs annuelles viennent de deux objets qui ne portent pas la même
    chose. ``Solde`` tient les parts de PIB — ressources, dépenses, solde,
    coefficient d'équilibre — et met le PIB à zéro hors de la fenêtre publiée,
    à dessein. ``Avenir`` tient la garantie vieillesse, les reprises sur
    succession et un PIB nominal PROJETÉ. Les euros de ce document viennent
    donc du second, et portent l'hypothèse de croissance que le premier refuse
    d'endosser : c'est écrit dans les conventions de lecture du document.
    """

    def __init__(self, prospective: bool) -> None:
        parametres = Parametres()
        racine = parametres.racine_donnees
        simulateur = Simulateur(parametres)
        contexte = PropositionProspective() if prospective else None
        if contexte is not None:
            contexte.__enter__()
        try:
            cout = C.calculer_cout(
                simulateur, DepensesRetraite(racine), Population(racine),
                ComptesRetraite(racine), assiette=AssietteActivite(racine),
            )
            self.parametres = parametres
            self.prospective = prospective
            self.solde = {l.annee: l for l in cout.solde.annees}
            self.avenir = {l.annee: l for l in cout.avenir.annees}
            self.dette = cout.dette
            self.annees = tuple(a for a in sorted(self.solde)
                                if a >= PREMIERE_ANNEE and a in self.avenir)
            self.solde_moyen = cout.solde.solde_moyen(LIBERAL, PREMIERE_ANNEE, C.HORIZON)
            self.solde_moyen_actuel = cout.solde.solde_moyen("actuel", PREMIERE_ANNEE,
                                                             C.HORIZON)
            self.equilibre = cout.solde.premiere_annee_equilibree(LIBERAL)
            self.dette_horizon = cout.dette.horizon(LIBERAL)
            self.dette_horizon_actuel = cout.dette.horizon("actuel")
            # Les cumuls portent tous la MÊME fenêtre, celle de la bascule à
            # l'horizon : ``Avenir.cumul`` commence un an plus tôt, à la
            # première année projetée, et mêler les deux ferait un tableau dont
            # les lignes ne se comparent pas. L'écart vaut une quinzaine de
            # milliards sur la garantie, ce qui se voit.
            # ET LA MÊME BASE que les tableaux annuels, celle du COR que porte
            # ``Solde``. ``Avenir`` porte la sienne, la dépense que le modèle
            # projette lui-même, plus haute de trois points de PIB en 2070 :
            # cumuler sur elle surestimait l'économie d'environ neuf pour cent,
            # jusqu'au 23 septembre 2026.
            self.cumul_depense = sum(self.pensions_constants(a, LIBERAL)
                                     for a in self.annees)
            self.cumul_depense_actuel = sum(self.pensions_constants(a, "actuel")
                                            for a in self.annees)
            self.cumul_garantie = sum(
                self.avenir[a].cout_constants(C.COMPOSANTE_GARANTIE)
                for a in self.annees)
            self.cumul_reprises = sum(self.avenir[a].reprises_constants()
                                      for a in self.annees)
            self.annee_euros = cout.annee_euros
        finally:
            if contexte is not None:
                contexte.__exit__(None, None, None)

    # -- une année, grandeur par grandeur ------------------------------------

    def pib(self, annee: int) -> float:
        """PIB en milliards d'euros courants, observé jusqu'en 2025, projeté après."""
        return self.avenir[annee].pib / 1000.0

    def md(self, annee: int, part: float) -> float:
        """Une part de PIB en milliards d'euros courants de l'année."""
        return part * self.pib(annee)

    def pensions(self, annee: int) -> float:
        return self.solde[annee].depense(LIBERAL)

    def pensions_constants(self, annee: int, scenario: str) -> float:
        """La dépense de pensions d'un système, en millions d'euros constants.

        Sur la base du COR, celle des tableaux annuels : la part de PIB que
        ``Solde`` porte, multipliée par le PIB projeté et ramenée aux euros
        constants par le coefficient de l'année.
        """
        ligne = self.avenir[annee]
        return (self.solde[annee].depense(scenario) * ligne.pib
                * ligne.coefficient_constants)

    def garantie(self, annee: int) -> float:
        """La garantie vieillesse NETTE de ce que les successions en reprennent."""
        ligne = self.avenir[annee]
        return ligne.part_pib(C.COMPOSANTE_GARANTIE) - ligne.part_pib_reprises()

    def depense(self, annee: int) -> float:
        """Ce que la proposition coûte en tout : les pensions et la garantie."""
        return self.pensions(annee) + self.garantie(annee)

    def recettes(self, annee: int) -> float:
        return self.solde[annee].ressources_de(LIBERAL)

    def solde_regime(self, annee: int) -> float:
        return self.solde[annee].solde(LIBERAL)

    def solde_elargi(self, annee: int) -> float:
        """Le solde du régime, diminué de la garantie que le contribuable porte.

        Ce n'est PAS un solde toutes administrations publiques, pour deux
        raisons. Les impôts et taxes affectés que la proposition cesse
        d'encaisser sortent du compte de la retraite sans que le programme dise
        si l'État cesse de les lever — le document le dit en tête de ses
        hypothèses fragiles. Et ce que l'État et la branche famille cessent de
        verser, ``versements_publics_retires``, est une recette en moins pour
        la retraite mais une dépense en moins pour eux.
        """
        return self.solde_regime(annee) - self.garantie(annee)

    def solde_actuel(self, annee: int) -> float:
        return self.solde[annee].solde("actuel")

    def ecart(self, annee: int) -> float:
        return self.solde_elargi(annee) - self.solde_actuel(annee)

    def coefficient(self, annee: int) -> float:
        return self.solde[annee].coefficient(LIBERAL)

    def poste_recette(self, annee: int, poste: str, scenario: str) -> float:
        return self.solde[annee].postes_ressources(scenario)[poste]

    def retire(self, annee: int, poste: str) -> float:
        """Ce que la proposition retire d'un poste de recettes, en part de PIB."""
        return (self.poste_recette(annee, poste, LIBERAL)
                - self.poste_recette(annee, poste, "actuel"))

    def versements_publics_retires(self, annee: int) -> float:
        """Ce que d'autres administrations cessent de verser au système.

        La contribution d'équilibre de l'État employeur, les subventions
        d'équilibre de son budget, et ce que la branche famille verse pour
        l'assurance vieillesse des parents au foyer. Ce sont des recettes pour
        la retraite, mais des DÉPENSES pour leur payeur : au niveau des
        administrations publiques consolidées, elles s'annulent. Le solde du
        document est celui de la retraite, garantie comprise, et non le solde
        public ; c'est ce poste qui fait la différence la plus nette entre les
        deux. Il n'est pas tout ce que l'État garde : employeur, il paie aussi
        sa part du taux unique, qui est dans les cotisations du scénario 6, et
        le modèle ne sépare pas les employeurs publics des autres.
        """
        return (self.retire(annee, "contribution_equilibre_etat")
                + self.retire(annee, "subventions_equilibre")
                + self.retire(annee, "transferts_famille"))

    def pilier_obligatoire(self, annee: int) -> float:
        """Les 5 % capitalisés imposés, en part de PIB.

        Le pilier n'est ni une recette ni une dépense de la répartition : il
        constitue un capital au nom de chacun. Il est chiffré ici parce qu'un
        PLF raisonne en taux de prélèvements obligatoires, et que la
        proposition rend ces cinq points obligatoires. Les cinq points
        VOLONTAIRES n'y sont pas : ils ne sont pas imposés.
        """
        taux = self.parametres.taux_capitalisation_obligatoire
        cotisations = self.poste_recette(annee, "cotisations", LIBERAL)
        return cotisations * taux / self.parametres.taux_cotisation_liberal

    def prelevements_actuels(self, annee: int) -> float:
        """Ce que le système actuel prélève : les cotisations et les impôts affectés.

        La contribution d'équilibre de l'État et ses subventions n'en sont pas :
        ce sont des dépenses de son budget, financées par l'impôt général, et la
        comptabilité nationale ne compte pas la première — une cotisation
        IMPUTÉE — parmi les prélèvements obligatoires. Elles les grossissaient
        de près de deux points de PIB jusqu'au 23 septembre 2026.
        """
        postes = self.solde[annee].postes_ressources("actuel")
        return postes["cotisations"] + postes["impots_et_taxes"]

    def versements_etat(self, annee: int) -> float:
        """Ce que le budget de l'État verse au système actuel : contribution et subventions."""
        postes = self.solde[annee].postes_ressources("actuel")
        return postes["contribution_equilibre_etat"] + postes["subventions_equilibre"]

    def prelevements_proposes(self, annee: int) -> float:
        return self.poste_recette(annee, "cotisations", LIBERAL) + self.pilier_obligatoire(annee)


# -- les blocs que le script écrit dans le document --------------------------


def _ligne_annuelle(retro: Chiffrage, annee: int) -> str:
    def part_et_euros(valeur: float, signe: bool = False) -> str:
        return (f"{nombre(valeur * 100, 2, signe)} "
                f"({nombre(retro.md(annee, valeur), 0, signe)})")

    return (
        f"| {annee} | {part_et_euros(retro.pensions(annee))} "
        f"| {part_et_euros(retro.garantie(annee))} "
        f"| {part_et_euros(retro.depense(annee))} "
        f"| {part_et_euros(retro.recettes(annee))} "
        f"| {part_et_euros(retro.solde_regime(annee), True)} "
        f"| {part_et_euros(retro.solde_elargi(annee), True)} "
        f"| {part_et_euros(retro.solde_actuel(annee), True)} "
        f"| {nombre(retro.ecart(annee) * 100, 2, True)} |"
    )


def tableau_annuel(chiffrage: Chiffrage, annees: tuple[int, ...]) -> str:
    lignes = [
        "| Année | Pensions | Garantie nette | Dépense totale | Recettes "
        "| Solde régime | Solde + garantie | Rappel sc. 1 | Écart |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    lignes += [_ligne_annuelle(chiffrage, annee) for annee in annees]
    return "\n".join(lignes)


def tableau_fait_central(retro: Chiffrage, prosp: Chiffrage) -> str:
    """Les chiffres qu'un rapporteur retient, l'année de la bascule.

    Les recettes retirées sont décomposées, parce qu'elles ne sont pas de même
    nature : des cotisations et des impôts, que des ménages et des entreprises
    cessent de payer, et des versements que d'autres administrations cessent
    de faire, et qu'elles gardent. L'écart est celui du système de retraite,
    garantie comprise — pas le solde public, que le document ne chiffre pas.
    """
    an = PREMIERE_ANNEE
    recettes = retro.recettes(an) - retro.solde[an].ressources_de("actuel")
    depense = retro.depense(an) - retro.solde[an].depense("actuel")

    def ligne(libelle: str, valeur: float, gras: bool = False) -> str:
        part = nombre(valeur * 100, 2, True)
        euros = nombre(retro.md(an, valeur), 0, True)
        if gras:
            return f"| **{libelle}** | **{part}** | **{euros}** |"
        return f"| {libelle} | {part} | {euros} |"

    lignes = [
        f"| En {an} | Points de PIB | Milliards d'euros |",
        "|---|---:|---:|",
        ligne("Recettes retirées au système de retraite", recettes),
        ligne("dont cotisations, au taux unique", retro.retire(an, "cotisations")),
        ligne("dont impôts et taxes affectés", retro.retire(an, "impots_et_taxes")),
        ligne("dont versements de l'État et de la branche famille",
              retro.versements_publics_retires(an)),
        ligne("Dépense publique retirée (pensions et garantie)", depense),
        ligne("Écart de solde de la retraite, garantie comprise, variante rétroactive",
              retro.ecart(an), gras=True),
        f"| **Écart de solde de la retraite, garantie comprise, variante prospective** "
        f"| **{nombre(prosp.ecart(an) * 100, 2, True)}** "
        f"| **{nombre(prosp.md(an, prosp.ecart(an)), 0, True)}** |",
    ]
    return "\n".join(lignes)


def tableau_arbitrages(retro: Chiffrage, prosp: Chiffrage) -> str:
    """Ce que chaque arbitrage ouvert déplace, en points de PIB de l'année de bascule."""
    an = PREMIERE_ANNEE
    impots = retro.poste_recette(an, "impots_et_taxes", "actuel")
    subventions = retro.poste_recette(an, "subventions_equilibre", "actuel")
    retroactivite = prosp.depense(an) - retro.depense(an)
    pilotage = 1.0 - retro.coefficient(an)
    lignes = [
        f"| Arbitrage ouvert | Ce qu'il déplace en {an} | En milliards |",
        "|---|---:|---:|",
        f"| Impôts et taxes affectés, si l'État continue de les lever "
        f"| {nombre(impots * 100, 2, True)} pt | {nombre(retro.md(an, impots), 0, True)} |",
        f"| Subventions d'équilibre, même question "
        f"| {nombre(subventions * 100, 2, True)} pt "
        f"| {nombre(retro.md(an, subventions), 0, True)} |",
        f"| Renoncer à la rétroactivité (variante prospective) "
        f"| {nombre(-retroactivite * 100, 2, True)} pt "
        f"| {nombre(-retro.md(an, retroactivite), 0, True)} |",
        f"| Appliquer le coefficient d'équilibre, non appliqué ici "
        f"| {nombre(retro.coefficient(an), 2)} sur toutes les pensions "
        f"| soit {nombre(pilotage * 100, 1)} % de moins |",
    ]
    return "\n".join(lignes)


def tableau_prelevements(retro: Chiffrage) -> str:
    """Ce que chaque système prélève, et, à part, ce que l'État lui verse.

    Les totaux et l'écart ne portent que sur les prélèvements : la
    contribution d'équilibre et les subventions sont des dépenses du budget de
    l'État, et le tableau les montre pour qu'on voie qu'elles disparaissent,
    pas pour les compter.
    """
    lignes = [
        "| Année | Cotisations (sc. 1) | Impôts et taxes affectés (sc. 1) "
        "| **Prélèvements sc. 1** | Cotisations 18 % (sc. 6) "
        "| Pilier obligatoire 5 % (sc. 6) | **Prélèvements sc. 6** | Écart "
        "| Versé par l'État au sc. 1, hors prélèvements |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for annee in ANNEES_PRELEVEMENTS:
        postes = retro.solde[annee].postes_ressources("actuel")
        cotisations = postes["cotisations"]
        impots = postes["impots_et_taxes"]
        etat = retro.versements_etat(annee)
        total_actuel = retro.prelevements_actuels(annee)
        propose = retro.poste_recette(annee, "cotisations", LIBERAL)
        pilier = retro.pilier_obligatoire(annee)
        total_propose = retro.prelevements_proposes(annee)

        def cellule(valeur: float, gras: bool = False) -> str:
            rendu = (f"{nombre(valeur * 100, 2)} "
                     f"({nombre(retro.md(annee, valeur), 0)})")
            return f"**{rendu}**" if gras else rendu

        lignes.append(
            f"| {annee} | {cellule(cotisations)} | {cellule(impots)} "
            f"| {cellule(total_actuel, True)} "
            f"| {cellule(propose)} | {cellule(pilier)} "
            f"| {cellule(total_propose, True)} "
            f"| {nombre((total_propose - total_actuel) * 100, 2, True)} "
            f"| {cellule(etat)} |"
        )
    return "\n".join(lignes)


def tableau_agregats(retro: Chiffrage, prosp: Chiffrage) -> str:
    """Les cumuls sur la projection, en milliards d'euros constants de référence."""
    def milliards(valeur: float, signe: bool = False) -> str:
        return nombre(valeur / 1000.0, 0, signe)

    lignes = [
        f"| Sur {PREMIERE_ANNEE}-{C.HORIZON} | Rétroactive | Prospective | Système actuel |",
        "|---|---:|---:|---:|",
        f"| Dépense de pensions cumulée, Md € constants de {retro.annee_euros} "
        f"| {milliards(retro.cumul_depense)} | {milliards(prosp.cumul_depense)} "
        f"| {milliards(retro.cumul_depense_actuel)} |",
        f"| Écart de dépense au système actuel "
        f"| {milliards(retro.cumul_depense - retro.cumul_depense_actuel, True)} "
        f"| {milliards(prosp.cumul_depense - prosp.cumul_depense_actuel, True)} | — |",
        f"| Garantie vieillesse brute cumulée | {milliards(retro.cumul_garantie)} "
        f"| {milliards(prosp.cumul_garantie)} | — |",
        f"| Reprises sur succession | {milliards(-retro.cumul_reprises, True)} "
        f"| {milliards(-prosp.cumul_reprises, True)} | — |",
        f"| Garantie nette cumulée "
        f"| {milliards(retro.cumul_garantie - retro.cumul_reprises)} "
        f"| {milliards(prosp.cumul_garantie - prosp.cumul_reprises)} | — |",
        f"| Solde moyen, points de PIB | {nombre(retro.solde_moyen * 100, 2, True)} "
        f"| {nombre(prosp.solde_moyen * 100, 2, True)} "
        f"| {nombre(retro.solde_moyen_actuel * 100, 2, True)} |",
        f"| Dette accumulée en {C.HORIZON}, points de PIB "
        f"| {nombre(retro.dette_horizon * 100, 0, True)} "
        f"| {nombre(prosp.dette_horizon * 100, 0, True)} "
        f"| {nombre(retro.dette_horizon_actuel * 100, 0, True)} |",
        f"| Première année d'équilibre | {retro.equilibre or 'jamais'} "
        f"| {prosp.equilibre or 'jamais'} | {'jamais'} |",
    ]
    return "\n".join(lignes)


# -- la série annuelle complète, pour un tableur -----------------------------

COLONNES: tuple[str, ...] = (
    "annee", "variante", "pib_mdeur_courants", "pensions_pib", "garantie_brute_pib",
    "reprises_pib", "depense_totale_pib", "recettes_pib", "cotisations_pib",
    "pilier_obligatoire_pib", "solde_regime_pib", "solde_regime_plus_garantie_pib",
    "coefficient_equilibre", "dette_pib", "sc1_depenses_pib", "sc1_recettes_pib",
    "sc1_solde_pib", "ecart_de_solde_pib",
)


def serie(retro: Chiffrage, prosp: Chiffrage) -> str:
    """La série annuelle des deux variantes, séparateur ``;`` et virgule décimale.

    Toutes les colonnes ``_pib`` sont en POINTS de PIB — donc déjà multipliées
    par cent —, et le PIB lui-même en milliards d'euros courants. Une seule
    unité par colonne, parce qu'un tableur ne lit pas les notes de bas de page.
    """
    lignes = [";".join(COLONNES)]
    for nom, chiffrage in (("retroactive", retro), ("prospective", prosp)):
        for annee in chiffrage.annees:
            ligne = chiffrage.solde[annee]
            dette = chiffrage.dette.annee(annee)
            valeurs = [
                str(annee), nom, f"{chiffrage.pib(annee):.1f}",
                f"{chiffrage.pensions(annee) * 100:.3f}",
                f"{chiffrage.avenir[annee].part_pib(C.COMPOSANTE_GARANTIE) * 100:.3f}",
                f"{chiffrage.avenir[annee].part_pib_reprises() * 100:.3f}",
                f"{chiffrage.depense(annee) * 100:.3f}",
                f"{chiffrage.recettes(annee) * 100:.3f}",
                f"{chiffrage.poste_recette(annee, 'cotisations', LIBERAL) * 100:.3f}",
                f"{chiffrage.pilier_obligatoire(annee) * 100:.3f}",
                f"{chiffrage.solde_regime(annee) * 100:.3f}",
                f"{chiffrage.solde_elargi(annee) * 100:.3f}",
                f"{chiffrage.coefficient(annee):.3f}",
                f"{dette.stock(LIBERAL) * 100:.3f}" if dette else "",
                f"{ligne.depense('actuel') * 100:.3f}",
                f"{ligne.ressources_de('actuel') * 100:.3f}",
                f"{chiffrage.solde_actuel(annee) * 100:.3f}",
                f"{chiffrage.ecart(annee) * 100:.3f}",
            ]
            lignes.append(";".join(valeurs).replace(".", ","))
    return "\n".join(lignes) + "\n"


# -- l'écriture, et le contrôle de péremption --------------------------------


def remplacer(texte: str, repere: str, contenu: str) -> str:
    debut, fin = f"<!-- {repere}:debut -->", f"<!-- {repere}:fin -->"
    if debut not in texte or fin not in texte:
        raise SystemExit(f"repères « {repere} » absents de {DOCUMENT}")
    avant = texte.split(debut)[0]
    apres = texte.split(fin, 1)[1]
    return f"{avant}{debut}\n{contenu}\n{fin}{apres}"


def blocs(retro: Chiffrage, prosp: Chiffrage) -> dict[str, str]:
    return {
        "fait_central": tableau_fait_central(retro, prosp),
        "arbitrages": tableau_arbitrages(retro, prosp),
        "annuel_retroactif": tableau_annuel(retro, ANNEES_ANNUELLES),
        "horizon_retroactif": tableau_annuel(retro, ANNEES_LONGUES),
        "annuel_prospectif": tableau_annuel(prosp, ANNEES_ANNUELLES),
        "horizon_prospectif": tableau_annuel(prosp, ANNEES_LONGUES),
        "prelevements": tableau_prelevements(retro),
        "agregats": tableau_agregats(retro, prosp),
    }


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="échoue si le document ou la série sont périmés")
    arguments = analyseur.parse_args(argv)

    retro, prosp = Chiffrage(False), Chiffrage(True)

    chemin = RACINE / DOCUMENT
    texte = voulu = chemin.read_text(encoding="utf-8")
    for repere, contenu in blocs(retro, prosp).items():
        voulu = remplacer(voulu, repere, contenu)
    chemin_serie = RACINE / SERIE
    serie_voulue = serie(retro, prosp)
    serie_actuelle = (chemin_serie.read_text(encoding="utf-8")
                      if chemin_serie.exists() else "")

    perimes = [nom for nom, perime in ((DOCUMENT, voulu != texte),
                                       (SERIE, serie_voulue != serie_actuelle)) if perime]
    if arguments.verifier:
        if perimes:
            print("périmé : " + ", ".join(perimes)
                  + " — lancer python scripts/chiffrage_plf.py")
            return 1
        print("le chiffrage est à jour")
        return 0
    if voulu != texte:
        chemin.write_text(voulu, encoding="utf-8", newline="\n")
    if serie_voulue != serie_actuelle:
        chemin_serie.write_text(serie_voulue, encoding="utf-8", newline="\n")
    print("réécrit : " + (", ".join(perimes) if perimes else "rien à changer"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
