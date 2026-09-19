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
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))

import yaml  # noqa: E402

from retraite_notionnelle import Parametres  # noqa: E402
from retraite_notionnelle.castypes import CAS_TYPES, CasType, calculer_cas_types  # noqa: E402
from retraite_notionnelle.config import RACINE_DONNEES  # noqa: E402
from retraite_notionnelle.cout import (  # noqa: E402
    _DEMI_TRANCHE, _ponderation, generations,
)
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

#: La part contributive, sous une clé qui ne peut être celle d'aucun avantage.
CONTRIBUTIF = "_contributif"

#: Les avantages que le scénario 1 sert mais que la cascade N'ISOLE PAS, et
#: qu'on mesure donc par recalcul. Leur montant est PRIS SUR la part
#: contributive : la cascade, elle, ne les y avait pas comptés comme des
#: avantages, faute de savoir les séparer.
RECALCULS: tuple[str, ...] = (
    "periodes_assimilees",
    "categorie_active",
    "age_jouissance_militaire",
)

#: Pour chaque statut CLASSÉ, le statut sédentaire de mêmes régimes.
#:
#: Le classement tient à l'emploi et non à la personne : la contrefactuelle
#: d'un agent de catégorie active est le même agent, même caisse, même
#: traitement, dont l'emploi ne serait pas classé. Les régimes sont identiques
#: des deux côtés — un test l'exige —, si bien que l'écart ne porte que sur
#: l'âge opposé et sur ce qui en découle.
#:
#: Les militaires y figurent sous leur propre ligne : ce n'est pas un
#: classement d'emploi, c'est une pension qui s'ouvre à une DURÉE DE SERVICES
#: et non à un âge. Leur contrefactuelle est le fonctionnaire d'État, qui
#: relève des mêmes régimes qu'eux.
SEDENTAIRE: dict[str, tuple[str, str]] = {
    "fonctionnaire_etat_actif": ("fonctionnaire_etat", "categorie_active"),
    "fonctionnaire_etat_super_actif": ("fonctionnaire_etat", "categorie_active"),
    "fonctionnaire_territorial_hospitalier_actif": (
        "fonctionnaire_territorial_hospitalier", "categorie_active"),
    "fonctionnaire_territorial_hospitalier_super_actif": (
        "fonctionnaire_territorial_hospitalier", "categorie_active"),
    "ouvrier_etat_actif": ("ouvrier_etat", "categorie_active"),
    "militaire": ("fonctionnaire_etat", "age_jouissance_militaire"),
    "militaire_officier": ("fonctionnaire_etat", "age_jouissance_militaire"),
}

#: La dose d'interruption appliquée par ``--par-carriere`` à des carrières qui
#: n'en portent aucune. Cinq ans, c'est-à-dire vingt trimestres : l'ordre de
#: grandeur d'une carrière touchée par le chômage ou la maladie, et il est
#: affiché comme une HYPOTHÈSE et non comme une mesure — la grille ne dit rien
#: de la fréquence réelle, faute d'une structure de population.
DOSE_INTERRUPTION = 5


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
        elif avantage["code"] in RECALCULS:
            noms.setdefault(avantage["code"], []).append(avantage["libelle"])
    return {ligne: " / ".join(sorted(parts)) for ligne, parts in noms.items()}


#: Les trois familles de départ anticipé, et ce qui les sépare. Elles ne se
#: recouvrent pas : un départ est ouvert par un motif et un seul.
MOTIFS: tuple[str, ...] = ("carriere_longue", "classement", "regime_special")


def _motif(cas: CasType, actuel) -> str:
    """Ce qui ouvre ce départ, quand il est anticipé.

    Le droit ouvre un départ avant l'âge légal de trois façons, et confondre
    les trois est la meilleure manière de se tromper de réforme :

    * la CARRIÈRE LONGUE, ouverte à qui a commencé tôt et cotisé assez — c'est
      le seul des trois qui regarde la durée cotisée, donc le moins éloigné
      d'un principe contributif ;
    * le CLASSEMENT de l'emploi, catégorie active ou super-active de la
      fonction publique, qui ne regarde ni la durée ni la pénibilité réelle
      mais le corps d'appartenance ;
    * l'âge propre d'un RÉGIME SPÉCIAL — cinquante ans à la conduite SNCF,
      cinquante-cinq aux IEG, une durée de services chez les militaires.

    Le modèle nomme le premier lui-même (``motif_ouverture``) ; les deux autres
    se lisent au statut, le classement étant celui des sept affiliations que
    ``legislation/affiliations.yaml`` marque.
    """
    if actuel.motif_ouverture == "carriere_longue":
        return "carriere_longue"
    if cas.affiliation in SEDENTAIRE:
        return "classement"
    return "regime_special"


def carriere_variante(simulateur: Simulateur, cas: CasType, generation: int,
                      age: float, affiliation: str | None = None,
                      interruptions: dict[int, str] | None = None):
    """La carrière d'un cas type, avec une variante possible.

    Reprend ``CasType._carriere`` à deux libertés près, qui sont exactement les
    deux contrefactuelles : le statut d'affiliation, et le motif des périodes
    non travaillées. L'âge de liquidation est passé et non recalculé — c'est ce
    qui tient les deux pensions comparables.
    """
    reelles = {
        int(generation + cas.age_debut + decalage): motif
        for decalage, motif in cas.interruptions_relatives
    }
    return simulateur.carriere_simple(
        annee_naissance=generation,
        sexe=cas.sexe,
        affiliation=affiliation or cas.affiliation,
        age_debut=cas.age_debut,
        age_liquidation=age,
        niveau_salaire=cas.niveau_salaire,
        profil_carriere=cas.profil_carriere,
        interruptions=reelles if interruptions is None else interruptions,
        nombre_enfants=cas.nombre_enfants,
        part_primes=cas.part_primes,
        identifiant=f"{cas.libelle} (génération {generation})",
    )


def recalculer(simulateur: Simulateur, cas: CasType, generation: int,
               age: float, reelle) -> dict[str, float]:
    """Les avantages non isolés par la cascade, mesurés par recalcul.

    Rend un dictionnaire VIDE quand la carrière n'en porte aucun, plutôt qu'un
    zéro : la plupart des cas types sont dans ce cas, et un zéro écrit
    laisserait croire à une mesure là où il n'y a rien à mesurer.

    DEUX PRÉCAUTIONS.

    La première évite un double compte. Neutraliser les périodes non
    travaillées retire les trimestres assimilés ET l'AVPF, que la cascade
    chiffre déjà sous sa propre ligne. On la retranche donc de l'écart brut.

    La seconde est une interaction qu'on ne mesure pas. Retirer deux avantages
    d'âge à la fois n'est pas la somme de deux retraits — la décote est
    plafonnée, et deux pénalités qui butent sur le même plafond ne
    s'additionnent pas. Aucun cas type de la grille ne porte les deux
    (les interruptions sont sur une carrière du privé, le classement sur des
    carrières publiques), et un test l'exige ; si cela changeait, ce calcul
    devrait changer aussi.

    ET UN GARDE-FOU, qui refuse plutôt que de rendre un chiffre faux. Un
    changement de statut ne vaut comme contrefactuelle que s'il ne déplace QUE
    l'âge opposé. Quand il déplace aussi la DURÉE REQUISE, le rapport de
    proratisation change avec lui et l'écart ne mesure plus l'avantage : c'est
    le cas du militaire, dont la pension exige 167 trimestres là où le
    fonctionnaire civil en exige 152, si bien que la contrefactuelle civile
    rend une pension PLUS FORTE et l'avantage un montant négatif. La fonction
    d'appel reçoit alors le refus et sa raison, et l'imprime : ce que la
    jouissance militaire coûte est une affaire d'annuités servies, que
    ``--duree`` mesure et que celle-ci ne mesurera jamais.
    """
    parts: dict[str, float] = {}
    refus: dict[str, str] = {}
    if cas.interruptions_relatives:
        sans = simulateur.scenario_actuel.calculer(carriere_variante(
            simulateur, cas, generation, age,
            interruptions={
                int(generation + cas.age_debut + decalage): "sans_activite"
                for decalage, _ in cas.interruptions_relatives
            },
        ))
        avpf = sum(a.montant for a in reelle.avantages_appliques if a.code == "avpf")
        ecart = reelle.pension_annuelle - sans.pension_annuelle - avpf
        if ecart > 0.0:
            parts["periodes_assimilees"] = ecart
    if cas.affiliation in SEDENTAIRE:
        temoin, ligne = SEDENTAIRE[cas.affiliation]
        sans = simulateur.scenario_actuel.calculer(
            carriere_variante(simulateur, cas, generation, age, affiliation=temoin)
        )
        if sans.trimestres_requis != reelle.trimestres_requis:
            refus[ligne] = (
                f"{cas.code} : la contrefactuelle {temoin} exige "
                f"{sans.trimestres_requis} trimestres contre "
                f"{reelle.trimestres_requis} — la proratisation change avec le "
                f"statut, l'écart ne mesure plus l'âge"
            )
        else:
            ecart = reelle.pension_annuelle - sans.pension_annuelle
            if ecart > 0.0:
                parts[ligne] = ecart
    return parts, refus


def cascades(simulateur: Simulateur, liquidation: str):
    """Pour chaque couple (cas type, génération) : la décomposition du scénario 1.

    En euros constants de l'année de référence, comme les pensions de
    ``cout.py``, et par la même conversion. Les montants recalculés sont PRIS
    SUR la part contributive, où la cascade les avait laissés faute de savoir
    les séparer — la somme des parts vaut donc toujours la pension entière.
    """
    grille = calculer_cas_types(simulateur, CAS_TYPES, generations(), liquidation)
    par_code = {cas.code: cas for cas in CAS_TYPES}
    couples = []
    refus: dict[str, str] = {}
    for (code, generation), comparaison in grille.resultats.items():
        actuel = comparaison.actuel
        parts = {CONTRIBUTIF: actuel.total_contributif}
        for avantage in actuel.avantages_appliques:
            parts[avantage.code] = parts.get(avantage.code, 0.0) + avantage.montant
        recalculs, refuses = recalculer(simulateur, par_code[code], generation,
                                        comparaison.carriere.age_liquidation, actuel)
        refus.update(refuses)
        for ligne, montant in recalculs.items():
            parts[ligne] = parts.get(ligne, 0.0) + montant
            parts[CONTRIBUTIF] -= montant
        parts = {cle: comparaison.en_euros_constants(valeur)
                 for cle, valeur in parts.items()}
        couples.append((code, generation, comparaison.carriere.annee_liquidation,
                        comparaison.carriere.age_liquidation, parts,
                        _motif(par_code[code], actuel)))
    # LE REFUS EST CONTAGIEUX, et il doit l'être. La durée requise d'un statut
    # varie par génération : une contrefactuelle peut être propre pour les unes
    # et faussée pour les autres. Garder les premières donnerait une série qui
    # ne porte qu'un morceau de sa population — un agrégat biaisé, et dont le
    # biais serait invisible. Une ligne refusée quelque part est donc retirée
    # PARTOUT, et son montant rendu à la part contributive d'où il venait.
    for code, generation, annee, age, parts, motif in couples:
        for ligne in list(refus):
            montant = parts.pop(ligne, 0.0)
            parts[CONTRIBUTIF] += montant
    return couples, grille, refus


def masses(couples, population: Population, annee: int,
           poids_cas: dict[str, float]) -> dict[str, float]:
    """La masse de chaque part une année donnée.

    Copie fidèle de la pondération de ``cout._masses`` pour le scénario 1 :
    chaque génération de la grille en représente cinq, parcourues une à une,
    chacune liquidant sa propre année. Le scénario 1 n'est pas revalorisé — le
    droit l'indexe sur les prix et les masses sont déjà en euros constants —,
    si bien qu'un seul poids suffit, celui des têtes.
    """
    total: dict[str, float] = {}
    for code, generation, annee_liquidation, _, parts, _motif_ in couples:
        part_cas = poids_cas.get(code, 0.0)
        if part_cas <= 0.0:
            continue
        poids = 0.0
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            if annee < annee_liquidation + decalage:
                continue
            poids += population.effectif(annee - generation - decalage, annee)
        if poids <= 0.0:
            continue
        for cle, montant in parts.items():
            total[cle] = total.get(cle, 0.0) + part_cas * poids * montant
    return total


def masses_anticipees(couples, simulateur: Simulateur, population: Population,
                      annee: int, poids_cas: dict[str, float]
                      ) -> tuple[float, dict[str, float]]:
    """La masse servie AVANT l'âge légal de droit commun, ventilée par motif.

    C'est le second effet d'un avantage d'âge, et le plus lourd : non plus ce
    qu'il ajoute au montant, mais ce qu'il coûte en ANNÉES DE SERVICE. Une
    pension servie de cinquante-deux à soixante-quatre ans est douze annuités
    que personne n'a cotisées et qu'aucune décote ne rattrape — la décote étant
    plafonnée à vingt trimestres.

    La comparaison se fait à l'âge légal de la GÉNÉRATION, lu dans
    ``legislation/age_ouverture_requis.csv``, et non à un âge fixe : opposer
    soixante-quatre ans à une génération qui relevait de soixante compterait
    comme anticipé un départ que le droit de l'époque disait à l'heure.

    La ventilation par motif est l'essentiel du résultat. Le coût des départs
    anticipés n'a pas la même origine selon l'époque : il vient des statuts
    classés et des régimes spéciaux tant que ceux-ci pèsent, puis de la
    carrière longue à mesure que l'âge légal monte au-dessus de l'âge auquel
    les carrières commencées tôt réunissent leur durée.
    """
    ages = simulateur.scenario_actuel.ages_ouverture
    totale = 0.0
    par_motif: dict[str, float] = {motif: 0.0 for motif in MOTIFS}
    for code, generation, annee_liquidation, _, parts, motif in couples:
        part_cas = poids_cas.get(code, 0.0)
        if part_cas <= 0.0:
            continue
        pension = sum(parts.values())
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            cohorte = generation + decalage
            if annee < annee_liquidation + decalage:
                continue
            age_atteint = annee - cohorte
            effectif = population.effectif(age_atteint, annee)
            if effectif <= 0.0:
                continue
            masse = part_cas * effectif * pension
            totale += masse
            legal = ages.age(cohorte)
            if legal is not None and age_atteint < legal[0]:
                par_motif[motif] += masse
    return totale, par_motif


def par_carriere(simulateur: Simulateur, generation: int):
    """Ce que chaque avantage vaut à un assuré, cas type par cas type.

    C'est le chiffre qui a un sens quand l'agrégat n'en a pas. La grille ne
    porte qu'une carrière interrompue sur treize et aucun chômage ; elle ne
    peut donc pas dire ce que les périodes assimilées COÛTENT au système, faute
    de savoir combien d'assurés en ont. Elle peut parfaitement dire ce qu'elles
    RAPPORTENT à qui en a, et c'est ce que cette table mesure, en appliquant à
    chaque carrière une dose commune de chômage indemnisé.
    """
    lignes = []
    for cas in CAS_TYPES:
        try:
            age = cas.age_liquidation_pour(simulateur, generation)
            reelle = simulateur.scenario_actuel.calculer(
                carriere_variante(simulateur, cas, generation, age)
            )
        except (ValueError, KeyError):
            continue
        # La dose de chômage est appliquée au milieu de la carrière active,
        # là où elle coûte le plus cher au salaire de référence.
        debut = int(generation + (cas.age_debut + age) / 2)
        chomage = {debut + k: "chomage_indemnise" for k in range(DOSE_INTERRUPTION)}
        neant = {annee: "sans_activite" for annee in chomage}
        avec = simulateur.scenario_actuel.calculer(
            carriere_variante(simulateur, cas, generation, age, interruptions=chomage))
        sans = simulateur.scenario_actuel.calculer(
            carriere_variante(simulateur, cas, generation, age, interruptions=neant))
        recalculs, refuses = recalculer(simulateur, cas, generation, age, reelle)
        lignes.append((cas, age, reelle.pension_annuelle,
                       avec.pension_annuelle - sans.pension_annuelle,
                       recalculs, refuses))
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
        print(f"Ce que chaque avantage vaut à un assuré — génération {options.generation}")
        print(f"Pensions annuelles en euros courants de l'année de liquidation.")
        print()
        entete = (f"{'Cas type':34s}{'Âge':>5s}{'Pension':>10s}"
                  f"{'Assimilées':>12s}{'Classement':>12s}")
        print(entete)
        print("-" * len(entete))
        refus: dict[str, str] = {}
        for cas, age, pension, chomage, recalculs, refuses in par_carriere(
                simulateur, options.generation):
            refus.update(refuses)
            classement = sum(recalculs.get(cle, 0.0) for cle in
                             ("categorie_active", "age_jouissance_militaire"))
            print(f"{cas.code:34s}{age:>5.0f}{pension:>10.0f}"
                  f"{chomage:>12.0f}{classement:>12.0f}")
        print()
        print(f"« Assimilées » : ce que valent {DOSE_INTERRUPTION} années de chômage")
        print("indemnisé au milieu de la carrière, comparées aux mêmes années sans")
        print("aucune validation. C'est une HYPOTHÈSE de dose, pas une mesure : la")
        print("grille ne dit rien de la fréquence réelle du chômage.")
        print()
        print("« Classement » : ce que vaut la catégorie active — ou, pour le")
        print("militaire, la jouissance immédiate — à date de départ INCHANGÉE.")
        print("Le chiffre est petit, et ce n'est pas une erreur : la décote est")
        print("plafonnée à vingt trimestres, si bien que l'agent classé et l'agent")
        print("sédentaire partis le même jour butent tous deux sur le même plafond.")
        print("Ce que le classement coûte vraiment est dans --duree.")
        _dire_les_refus(refus)
        return 0

    depenses = DepensesRetraite(parametres.racine_donnees)
    population = Population(parametres.racine_donnees)
    poids = _ponderation(simulateur, options.ponderation, CAS_TYPES)
    couples, grille, refus = cascades(simulateur, options.liquidation)
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
                couples, simulateur, population, annee, poids(annee))
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

    lignes = []
    for annee in depenses.annees():
        if options.depuis is not None and annee < options.depuis:
            continue
        if options.jusqu is not None and annee > options.jusqu:
            continue
        part = masses(couples, population, annee, poids(annee))
        totale = sum(part.values())
        if totale <= 0.0:
            continue
        observee = depenses.depense(annee)
        lignes.append((annee, observee, {
            cle: (valeur / totale, observee * valeur / totale)
            for cle, valeur in part.items()
        }))

    if not lignes:
        print("aucune année servie sur la fenêtre demandée", file=sys.stderr)
        return 1

    print("Coût des avantages non contributifs chiffrables du scénario 1")
    print(f"pondération {options.ponderation}, liquidation {options.liquidation}, "
          f"{len(couples)} couples (cas type, génération)")
    print()
    _table_annuelle(lignes, noms, options.pas)
    print()
    print("Montants en milliards d'euros COURANTS de chaque année. « Part » est la")
    print("fraction de la dépense observée que ces avantages expliquent.")
    print()
    print("C'EST UN PLANCHER, et très bas. Dix avantages sur les trente-neuf de")
    print("l'inventaire sont chiffrés ici ; la réversion, les bonifications de")
    print("service et les départs anticipés pour handicap ou inaptitude n'y sont")
    print("pas. Surtout, la grille de cas types n'est pas une population : un seul")
    print("de ses treize cas types a des enfants, un seul porte des interruptions,")
    print("aucun ne connaît le chômage. Voir --par-carriere pour le chiffre qui a")
    print("un sens, et --duree pour le second effet des avantages d'âge.")

    _dire_les_refus(refus)

    if grille.echecs:
        print(f"\n{len(grille.echecs)} couples non calculés, comme dans cout.py.")

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
