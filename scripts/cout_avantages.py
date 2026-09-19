#!/usr/bin/env python3
"""Ce que coûte chaque avantage non contributif, année par année.

    python scripts/cout_avantages.py                 # 1959 → dernière publiée
    python scripts/cout_avantages.py --depuis 1990
    python scripts/cout_avantages.py --csv sortie.csv
    python scripts/cout_avantages.py --ponderation egale

CE QU'IL MESURE
---------------
La cascade du scénario 1 rend, pour chaque carrière, le montant EN EUROS de
chaque avantage non contributif qu'elle déclenche, et la somme de ces montants
vaut exactement ``pension_annuelle - total_contributif``. Ce script porte cette
décomposition de l'individu à la masse, par la méthode de ``cout.py`` et sans
en changer une ligne :

    coût de l'avantage A en t = dépense OBSERVÉE en t × (masse A / masse totale)

La dépense observée vient de la DREES et n'est pas modélisée ; seule la PART
l'est. Une part est bien plus robuste qu'un niveau — les erreurs de niveau du
scénario 1 se retrouvent au dénominateur et s'annulent en grande partie.

Les poids sont ceux de ``cout.py`` et pas d'autres : l'effectif INSEE de chaque
classe d'âge pour la génération, les effectifs de caisse de la DREES pour le cas
type. Le scénario 1 garde son poids en têtes, le droit l'indexant sur les prix.

CE QU'IL NE MESURE PAS, ET C'EST L'ESSENTIEL
---------------------------------------------
Huit avantages sur trente-neuf. L'inventaire
``data/reference/legislation/avantages_non_contributifs.yaml`` porte les
trente-neuf et dit, ligne par ligne, pourquoi les trente et un autres
n'apparaissent pas ici :

  - onze sont INTÉGRÉS — le modèle les sert, mais leur effet passe par un
    trimestre, un âge ou une assiette, et ne s'isole qu'en recalculant la
    pension une seconde fois, avantage retiré. Ils sont chiffrables ; ils ne
    sont pas chiffrés.
  - trois sont DÉCLARÉS par une fiche sans qu'aucun code ne les serve.
  - dix-sept sont ABSENTS, la réversion en tête — qui est, à elle seule, la
    première dépense non contributive du système, et que ce modèle ne peut pas
    voir parce qu'il décrit une carrière et non un ménage.

Le total imprimé en bas est donc un PLANCHER, et il le dit.
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
from retraite_notionnelle.castypes import CAS_TYPES, calculer_cas_types  # noqa: E402
from retraite_notionnelle.config import RACINE_DONNEES  # noqa: E402
from retraite_notionnelle.cout import (  # noqa: E402
    _DEMI_TRANCHE, _ponderation, generations,
)
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

#: La part contributive, sous une clé qui ne peut être celle d'aucun avantage.
CONTRIBUTIF = "_contributif"


def libelles() -> dict[str, str]:
    """Le libellé de chaque ligne de cascade, lu dans l'inventaire.

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
    return {ligne: " / ".join(sorted(parts)) for ligne, parts in noms.items()}


def cascades(simulateur: Simulateur, ponderation: str, liquidation: str):
    """Pour chaque couple (cas type, génération) : la décomposition du scénario 1.

    En euros constants de l'année de référence, comme les pensions de
    ``cout.py``, et par la même conversion.
    """
    grille = calculer_cas_types(simulateur, CAS_TYPES, generations(), liquidation)
    couples = []
    for (code, generation), comparaison in grille.resultats.items():
        actuel = comparaison.actuel
        parts = {CONTRIBUTIF: comparaison.en_euros_constants(actuel.total_contributif)}
        for avantage in actuel.avantages_appliques:
            parts[avantage.code] = parts.get(avantage.code, 0.0) + (
                comparaison.en_euros_constants(avantage.montant)
            )
        couples.append((code, generation, comparaison.carriere.annee_liquidation, parts))
    return couples, grille


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
    for code, generation, annee_liquidation, parts in couples:
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


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--depuis", type=int, default=None,
                           help="première année imprimée (défaut : la première servie)")
    analyseur.add_argument("--jusqu", type=int, default=None)
    analyseur.add_argument("--ponderation", default="effectifs", choices=("effectifs", "egale"))
    analyseur.add_argument("--liquidation", default="droit", choices=("droit", "absolu"))
    analyseur.add_argument("--csv", type=Path, default=None,
                           help="écrire la série complète dans ce fichier")
    analyseur.add_argument("--pas", type=int, default=5,
                           help="pas d'impression du tableau, en années (défaut : 5)")
    options = analyseur.parse_args()

    parametres = Parametres()
    simulateur = Simulateur(parametres)
    depenses = DepensesRetraite(parametres.racine_donnees)
    population = Population(parametres.racine_donnees)
    poids = _ponderation(simulateur, options.ponderation, CAS_TYPES)

    couples, grille = cascades(simulateur, options.ponderation, options.liquidation)
    noms = libelles()

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

    # Les colonnes sont celles de la DERNIÈRE année, par coût décroissant : une
    # cascade ne rend que ce qu'une carrière déclenche, et les avantages
    # n'apparaissent pas tous aux mêmes dates.
    cles = sorted(
        {cle for _, _, parts in lignes for cle in parts if cle != CONTRIBUTIF},
        key=lambda cle: -lignes[-1][2].get(cle, (0.0, 0.0))[1],
    )

    largeur = max(len(noms.get(cle, cle)) for cle in cles) if cles else 0
    print(f"Coût des avantages non contributifs chiffrables du scénario 1")
    print(f"pondération {options.ponderation}, liquidation {options.liquidation}, "
          f"{len(couples)} couples (cas type, génération)")
    print()
    entete = "Année  Dépense observée   " + "".join(
        f"{noms.get(cle, cle)[:14]:>16s}" for cle in cles
    ) + f"{'Total gratuit':>16s}{'Part':>8s}"
    print(entete)
    print("-" * len(entete))
    for annee, observee, parts in lignes:
        if annee % options.pas and annee != lignes[-1][0]:
            continue
        gratuit = sum(euros for cle, (_, euros) in parts.items() if cle != CONTRIBUTIF)
        cellules = "".join(
            f"{parts.get(cle, (0.0, 0.0))[1] / 1000:>15.1f}G" for cle in cles
        )
        print(f"{annee}  {observee / 1000:>13.1f}G   {cellules}"
              f"{gratuit / 1000:>15.1f}G{gratuit / observee:>7.1%}")

    print()
    print("Montants en milliards d'euros COURANTS de chaque année. « Part » est la")
    print("fraction de la dépense observée que ces avantages expliquent.")
    print()
    print("C'EST UN PLANCHER. Huit avantages sur les trente-neuf de l'inventaire")
    print("sont chiffrés ici ; la réversion, les bonifications de service, les")
    print("périodes assimilées et les départs anticipés n'y sont pas. Le COR")
    print("chiffre l'ensemble des droits de solidarité à « de l'ordre d'un")
    print("cinquième des retraites tous régimes » (rapport du 27 janvier 2010).")

    if grille.echecs:
        print(f"\n{len(grille.echecs)} couples non calculés, "
              f"comme dans cout.py — mêmes motifs.")

    if options.csv is not None:
        with options.csv.open("w", encoding="utf-8", newline="") as flux:
            plume = csv.writer(flux)
            plume.writerow(["annee", "depense_observee_meur", "poste",
                            "part", "cout_meur"])
            for annee, observee, parts in lignes:
                for cle in [CONTRIBUTIF, *cles]:
                    fraction, euros = parts.get(cle, (0.0, 0.0))
                    plume.writerow([annee, f"{observee:.1f}", cle,
                                    f"{fraction:.6f}", f"{euros:.1f}"])
        print(f"\n{options.csv} écrit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
