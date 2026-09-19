#!/usr/bin/env python3
"""Ce que coûte chaque avantage non contributif, année par année.

    python scripts/cout_avantages.py                 # la décomposition annuelle
    python scripts/cout_avantages.py --depuis 1990
    python scripts/cout_avantages.py --csv sortie.csv
    python scripts/cout_avantages.py --duree         # le coût des départs anticipés
    python scripts/cout_avantages.py --par-carriere  # ce que chaque avantage vaut
                                                     # à un assuré, cas type par cas type

CE QU'IL MESURE
---------------
La cascade du scénario 1 rend, pour chaque carrière, le montant EN EUROS de
huit avantages non contributifs. Deux autres — les périodes assimilées et la
catégorie active — sont SERVIS par le scénario 1 sans que la cascade les isole :
leur effet passe par un trimestre ou par un âge. Ce script les mesure par
RECALCUL, qui est le principe même de la cascade : on refait la pension sans
l'avantage, à date de liquidation inchangée, et l'écart est la ligne.

Les dix lignes sont ensuite portées de l'individu à la masse par la méthode de
``cout.py``, sans en changer une ligne :

    coût de l'avantage A en t = dépense OBSERVÉE en t × (masse A / masse totale)

La dépense observée vient de la DREES et n'est pas modélisée ; seule la PART
l'est. Les poids sont ceux de ``cout.py`` : l'effectif INSEE de chaque classe
d'âge pour la génération, les effectifs de caisse de la DREES pour le cas type.

DEUX EFFETS, ET IL NE FAUT PAS LES CONFONDRE
---------------------------------------------
Un avantage d'ÂGE — catégorie active, jouissance militaire, carrière longue —
agit deux fois, et la seconde est la plus lourde :

1. *sur le MONTANT*, en épargnant tout ou partie de la décote. C'est ce que la
   décomposition annuelle mesure, et c'est PETIT : la décote est plafonnée à
   vingt trimestres, si bien qu'un agent parti cinq ans avant l'âge légal et un
   agent sédentaire parti le même jour butent tous deux sur le même plafond.
2. *sur la DURÉE*, en faisant servir la pension cinq, dix ou vingt ans de plus.
   C'est ce que ``--duree`` mesure, et c'est là qu'est l'argent. Un compte
   notionnel le fait payer par son coefficient de conversion ; le droit actuel
   ne le fait payer par rien.

CE QU'IL NE MESURE PAS
----------------------
Dix avantages sur les trente-neuf de l'inventaire
``data/reference/legislation/avantages_non_contributifs.yaml``, qui dit
ligne par ligne pourquoi les vingt-neuf autres n'y sont pas — la réversion en
tête, qui est à elle seule la première dépense non contributive du système et
que ce modèle ne peut pas voir, décrivant une carrière et non un ménage.

Et surtout : **la grille de cas types n'est pas une population.** Un seul de
ses treize cas types a des enfants, un seul porte des interruptions, et aucun
ne connaît le chômage. Les agrégats de droits familiaux et de périodes
assimilées qu'on en tire sont donc des planchers très bas, et ``--par-carriere``
existe pour donner le chiffre qui, lui, a un sens : ce que l'avantage vaut à
un assuré qui le touche.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import replace
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))

import yaml  # noqa: E402

from retraite_notionnelle import Parametres  # noqa: E402
from retraite_notionnelle.avantages import (  # noqa: E402
    CONTRIBUTIF, LIGNES_LUES, MOTIFS, NEUTRALISATIONS, calculer_avantages,
    carriere_variante, decomposer,
    masses, masses_anticipees, recalculer, scenarios_neutralises,
)
from retraite_notionnelle.castypes import CAS_TYPES  # noqa: E402
from retraite_notionnelle.config import RACINE_DONNEES  # noqa: E402
from retraite_notionnelle.cout import _ponderation  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

#: La dose d'interruption appliquée par ``--par-carriere`` à des carrières qui
#: n'en portent aucune. Cinq ans, c'est-à-dire vingt trimestres : l'ordre de
#: grandeur d'une carrière touchée par le chômage ou la maladie, et il est
#: affiché comme une HYPOTHÈSE et non comme une mesure — la grille ne dit rien
#: de la fréquence réelle, faute d'une structure de population.
DOSE_INTERRUPTION = 5


def _codes_mesures() -> frozenset[str]:
    """Les codes qui portent une ligne de coût sans porter de ligne de cascade.

    Deux sources, et elles ne se recouvrent pas : ceux que le modèle mesure en
    RETIRANT l'avantage et en refaisant la pension, et ceux dont le montant est
    LU dans un poste publié. Les premiers sont des contrefactuelles, les seconds
    des comptes ; la table des libellés a besoin des deux.
    """
    return frozenset({n.code for n in NEUTRALISATIONS} | set(LIGNES_LUES))


def libelles() -> dict[str, str]:
    """Le libellé de chaque ligne, lu dans l'inventaire.

    L'inventaire est l'autorité sur les noms : deux dispositifs peuvent
    partager une ligne de cascade — la MDA et la bonification de la fonction
    publique en sont un cas —, et c'est lui qui le dit.
    """
    chemin = RACINE_DONNEES / "reference" / "legislation" / "avantages_non_contributifs.yaml"
    with chemin.open(encoding="utf-8") as flux:
        inventaire = yaml.safe_load(flux)
    noms: dict[str, list[str]] = {}
    for avantage in inventaire["avantages"]:
        ligne = avantage["ligne_cascade"]
        if ligne is not None:
            noms.setdefault(ligne, []).append(avantage["libelle"])
        elif avantage["code"] in _codes_mesures():
            noms.setdefault(avantage["code"], []).append(avantage["libelle"])
    return {ligne: " / ".join(sorted(parts)) for ligne, parts in noms.items()}


def par_carriere(simulateur: Simulateur, generation: int):
    """Ce que chaque avantage vaut à un assuré, cas type par cas type.

    C'est le chiffre qui a un sens quand l'agrégat n'en a pas — et c'est ici le
    cas pour la moitié des lignes. Quatre des neuf avantages mesurés par
    recalcul ne pèsent RIEN sur la fenêtre que la DREES publie, chacune pour une
    raison qui lui est propre et qui n'a rien d'un défaut de mesure :

    * le salaire de référence des parents ne s'applique qu'aux pensions
      prenant effet à compter de septembre 2026 ;
    * la garantie minimale de points ne mord que sur des carrières dont les
      premières années tombent entre 1989 et 2018, et qui liquident après 2024 ;
    * la carrière longue ne vaut rien sur le MONTANT — son prix est entièrement
      dans la durée, que ``--duree`` mesure ;
    * le service national et les points gratuits de complémentaire ne sont
      portés par aucun cas type de la grille, dont un seul connaît une
      interruption.

    Cette table lève les deux derniers obstacles en appliquant à chaque carrière
    une DOSE COMMUNE : cinq années de chômage indemnisé au milieu de la vie
    active, et une année de service national au début. C'est une hypothèse,
    affichée comme telle, et non une mesure de ce que la population a vécu.
    """
    variantes = scenarios_neutralises(simulateur)
    lignes = []
    for cas in CAS_TYPES:
        try:
            age = cas.age_liquidation_pour(simulateur, generation)
        except (ValueError, KeyError):
            continue
        # La dose est posée en DÉCALAGES depuis l'âge d'entrée, comme les
        # interruptions d'un cas type : le chômage au milieu de la vie active,
        # là où il coûte le plus cher au salaire de référence, et le service
        # national à vingt ans.
        milieu = max(1, int((age - cas.age_debut) / 2))
        dose = tuple(
            [(milieu + rang, "chomage_indemnise") for rang in range(DOSE_INTERRUPTION)]
            + [(max(0, int(20 - cas.age_debut)), "service_militaire")]
        )
        charge = replace(cas, interruptions_relatives=dose)
        try:
            reelle = simulateur.scenario_actuel.calculer(
                carriere_variante(simulateur, cas, generation, age))
            chargee = simulateur.scenario_actuel.calculer(
                carriere_variante(simulateur, charge, generation, age))
        except (ValueError, KeyError):
            continue
        # Deux mesures pour deux questions : ce que la carrière RÉELLE du cas
        # type porte, et ce que la même carrière porterait si elle avait connu
        # la dose. Les deux sont rendues, et la seconde est signalée.
        propres, refus = recalculer(simulateur, cas, generation, age, reelle, variantes)
        sous_dose, _ = recalculer(simulateur, charge, generation, age, chargee, variantes)
        lignes.append((cas, age, reelle.pension_annuelle, chargee.pension_annuelle,
                       propres, sous_dose, refus))
    return lignes


def _dire_les_refus(refus: dict[str, str]) -> None:
    """Imprime ce que le garde-fou a refusé de mesurer, et pourquoi.

    Un refus est un résultat : il dit qu'une contrefactuelle existe mais ne
    vaut rien, ce qui est une information plus sûre qu'un chiffre plausible.
    """
    if not refus:
        return
    print()
    print("NON MESURÉ, et la raison est écrite :")
    for ligne, raison in sorted(refus.items()):
        print(f"  {ligne} — {raison}")


def _table_annuelle(lignes, noms, pas: int) -> None:
    cles = sorted(
        {cle for _, _, parts in lignes for cle in parts if cle != CONTRIBUTIF},
        key=lambda cle: -lignes[-1][2].get(cle, (0.0, 0.0))[1],
    )
    entete = "Année  Dépense observée  " + "".join(
        f"{noms.get(cle, cle)[:14]:>16s}" for cle in cles
    ) + f"{'Total gratuit':>16s}{'Part':>8s}"
    print(entete)
    print("-" * len(entete))
    for annee, observee, parts in lignes:
        if annee % pas and annee != lignes[-1][0]:
            continue
        gratuit = sum(euros for cle, (_, euros) in parts.items() if cle != CONTRIBUTIF)
        cellules = "".join(
            f"{parts.get(cle, (0.0, 0.0))[1] / 1000:>15.1f}G" for cle in cles
        )
        print(f"{annee}  {observee / 1000:>13.1f}G  {cellules}"
              f"{gratuit / 1000:>15.1f}G{gratuit / observee:>7.1%}")


def main() -> int:
    analyseur = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--depuis", type=int, default=None,
                           help="première année imprimée (défaut : la première servie)")
    analyseur.add_argument("--jusqu", type=int, default=None)
    analyseur.add_argument("--ponderation", default="effectifs", choices=("effectifs", "egale"))
    analyseur.add_argument("--liquidation", default="droit", choices=("droit", "absolu"))
    analyseur.add_argument("--csv", type=Path, default=None,
                           help="écrire la série complète dans ce fichier")
    analyseur.add_argument("--pas", type=int, default=5,
                           help="pas d'impression du tableau, en années (défaut : 5)")
    analyseur.add_argument("--duree", action="store_true",
                           help="le coût des pensions servies avant l'âge légal")
    analyseur.add_argument("--par-carriere", action="store_true",
                           help="ce que chaque avantage vaut à un assuré")
    analyseur.add_argument("--generation", type=int, default=1960,
                           help="génération de --par-carriere (défaut : 1960)")
    options = analyseur.parse_args()

    parametres = Parametres()
    simulateur = Simulateur(parametres)

    if options.par_carriere:
        lignes = par_carriere(simulateur, options.generation)
        codes = [n.code for n in NEUTRALISATIONS]
        presents = [c for c in codes
                    if any(c in propres or c in dose
                           for _, _, _, _, propres, dose, _ in lignes)]
        print(f"Ce que chaque avantage vaut à un assuré — génération "
              f"{options.generation}")
        print("Pensions annuelles en euros courants de l'année de liquidation.")
        print("Une ligne par cas type ; en dessous, la même carrière sous la dose.")
        print()
        entete = (f"{'Cas type':30s}{'Âge':>4s}{'Pension':>10s}"
                  + "".join(f"{code[:13]:>15s}" for code in presents))
        print(entete)
        print("-" * len(entete))
        refus: dict[str, str] = {}
        for cas, age, pension, chargee, propres, dose, refuses in lignes:
            refus.update(refuses)
            print(f"{cas.code:30s}{age:>4.0f}{pension:>10.0f}"
                  + "".join(f"{propres.get(code, 0.0):>15.0f}" for code in presents))
            if dose != propres:
                print(f"{'  └ sous la dose':30s}{'':>4s}{chargee:>10.0f}"
                      + "".join(f"{dose.get(code, 0.0):>15.0f}" for code in presents))
        print()
        print("LA DOSE est une HYPOTHÈSE et non une mesure : cinq années de chômage")
        print("indemnisé au milieu de la vie active, et une année de service national")
        print("à vingt ans. La grille ne dit rien de la fréquence réelle de l'un ni")
        print("de l'autre ; elle dit ce qu'ils valent à qui les a connus.")
        print()
        print("CE QUE CHAQUE COLONNE MESURE, c'est le retrait de l'avantage à date de")
        print("liquidation inchangée. Les valeurs ne s'additionnent pas : la décote")
        print("est plafonnée, et deux retraits qui butent sur le même plafond ne font")
        print("pas deux fois le premier.")
        for neutralisation in NEUTRALISATIONS:
            if neutralisation.code in presents:
                print(f"  {neutralisation.code} — {neutralisation.quoi}")
        _dire_les_refus(refus)
        return 0

    depenses = DepensesRetraite(parametres.racine_donnees)
    population = Population(parametres.racine_donnees)
    poids = _ponderation(simulateur, options.ponderation, CAS_TYPES)
    pensionnes, refus = decomposer(simulateur, options.liquidation)
    noms = libelles()

    if options.duree:
        print("Le coût des pensions servies AVANT l'âge légal de droit commun")
        print(f"pondération {options.ponderation}, liquidation {options.liquidation}")
        print()
        entete = (f"{'Année':6s}{'Dépense':>12s}{'Anticipée':>12s}{'Part':>7s}"
                  f"{'Carrière longue':>17s}{'Classement':>13s}{'Rég. spéciaux':>15s}")
        print(entete)
        print("-" * len(entete))
        for annee in depenses.annees():
            if options.depuis is not None and annee < options.depuis:
                continue
            if options.jusqu is not None and annee > options.jusqu:
                continue
            if annee % options.pas and annee != depenses.derniere_annee:
                continue
            totale, par_motif = masses_anticipees(
                pensionnes, simulateur, population, annee, poids(annee))
            if totale <= 0.0:
                continue
            observee = depenses.depense(annee)
            anticipee = sum(par_motif.values())
            cellules = "".join(
                f"{observee * par_motif[motif] / totale / 1000:>14.1f}G"
                for motif in MOTIFS
            )
            print(f"{annee:6d}{observee / 1000:>11.1f}G"
                  f"{observee * anticipee / totale / 1000:>11.1f}G"
                  f"{anticipee / totale:>7.1%}{cellules}")
        print()
        print("Une pension servie avant l'âge légal est une annuité que personne n'a")
        print("cotisée et qu'aucune décote ne rattrape, celle-ci étant plafonnée à")
        print("vingt trimestres. C'est le second effet des avantages d'âge — catégorie")
        print("active, régimes spéciaux, jouissance militaire, carrière longue — et")
        print("c'est le plus lourd. Les trois dernières colonnes disent d'où il vient,")
        print("et la réponse change au cours du temps : des statuts classés et des")
        print("régimes spéciaux hier, de la carrière longue aujourd'hui, à mesure que")
        print("l'âge légal monte au-dessus de l'âge auquel une carrière commencée tôt")
        print("réunit sa durée.")
        print()
        print("RÉSERVE. Ce partage compte des ANNUITÉS anticipées, pas un surcoût net :")
        print("partir tôt, c'est aussi cotiser moins et mourir plus tôt en moyenne. Le")
        print("chiffre dit ce que le système verse avant l'âge légal, non ce qu'il")
        print("économiserait à supprimer ces départs.")
        _dire_les_refus(refus)
        return 0

    # LE TABLEAU EST CELUI DU SITE, et pas un second calcul qui lui ressemble.
    # Cette commande a longtemps refait la décomposition pour elle seule, à
    # partir des seules masses du modèle ; elle annonçait 12,6 milliards quand
    # la page en annonçait 93,9, et l'écart n'était pas une erreur de calcul
    # mais une différence de périmètre — les postes LUS dans les comptes
    # manquaient ici. Un chiffre qui dépend de la porte par laquelle on entre
    # n'est pas un chiffre. Le calcul vit désormais dans le modèle, les deux
    # portes y mènent, et la fenêtre se taille après coup.
    cout = calculer_avantages(simulateur, depenses, population,
                              options.ponderation, options.liquidation)
    refus = cout.refus
    lignes = [
        (ligne.annee, ligne.observee,
         {cle: (euros / ligne.observee, euros)
          for cle, euros in ligne.lignes.items()})
        for ligne in cout.annees
        if (options.depuis is None or ligne.annee >= options.depuis)
        and (options.jusqu is None or ligne.annee <= options.jusqu)
    ]

    if not lignes:
        print("aucune année servie sur la fenêtre demandée", file=sys.stderr)
        return 1

    print("Coût des avantages non contributifs chiffrables du scénario 1")
    print(f"pondération {options.ponderation}, liquidation {options.liquidation}, "
          f"{len(pensionnes)} couples (cas type, génération)")
    print()
    _table_annuelle(lignes, noms, options.pas)
    print()
    print("Montants en milliards d'euros COURANTS de chaque année. « Part » est la")
    print("fraction de la dépense observée que ces avantages expliquent.")
    print()
    print("LES COLONNES NE VIENNENT PAS TOUTES DU MÊME ENDROIT. Certaines sont")
    print("LUES dans les comptes de la protection sociale ou dans l'enquête de la")
    print("DREES auprès des caisses : elles comptent des personnes réelles. Les")
    print("autres sont REFAITES par le modèle, en retirant l'avantage de la")
    print("cascade et en rapportant l'écart à la dépense observée ; elles reposent")
    print("sur treize carrières types, dont un seul a des enfants et aucun ne")
    print("connaît le chômage. Là où les deux existaient, le poste publié a")
    print("remplacé la ligne calculée.")
    print()
    print("C'EST TOUT DE MÊME UN PLANCHER. Les bonifications de service, les")
    print("départs anticipés pour handicap et le congé parental ne sont ni")
    print("calculés ni publiés séparément. Voir --par-carriere pour ce que chaque")
    print("avantage vaut à un assuré, et --duree pour le second effet des")
    print("avantages d'âge, qui se compte en annuités et non en euros.")

    _dire_les_refus(refus)

    if options.csv is not None:
        cles = sorted({cle for _, _, parts in lignes for cle in parts
                       if cle != CONTRIBUTIF})
        with options.csv.open("w", encoding="utf-8", newline="") as flux:
            plume = csv.writer(flux)
            plume.writerow(["annee", "depense_observee_meur", "poste", "part", "cout_meur"])
            for annee, observee, parts in lignes:
                for cle in [CONTRIBUTIF, *cles]:
                    fraction, euros = parts.get(cle, (0.0, 0.0))
                    plume.writerow([annee, f"{observee:.1f}", cle,
                                    f"{fraction:.6f}", f"{euros:.1f}"])
        print(f"\n{options.csv} écrit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
