#!/usr/bin/env python3
"""La dépense de retraite en ses quatre facteurs, confrontée à l'Ageing Report de 2024.

    python scripts/facteurs_depense.py              # le système actuel contre l'AWG
    python scripts/facteurs_depense.py --systemes   # et les six systèmes
    python scripts/facteurs_depense.py --json f.json

Ce que l'Ageing Report de 2024 publie pour la France — la dépense de pensions
de 2022 à 2070, décomposée en dépendance, couverture, prestation et marché du
travail (``tests/temoins/ageing_report_france.json``) — contre la même
décomposition de la trajectoire propre du modèle
(``retraite_notionnelle.facteurs_depense``), sous deux jeux d'hypothèses du
COR : sa référence, une productivité de 0,7 % par an, celle de la page Coût ;
et sa variante haute, 1,0 %, la plus proche des 1,03 % de l'AWG. Les tableaux
s'écrivent en Markdown, en points de PIB, sous-période par sous-période comme
le tableau 9 de la fiche France ; les variations des facteurs, en pour cent,
se comparent sans dépendre du niveau de la dépense, que les deux périmètres ne
partagent pas (action 138, étape 3).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.facteurs_depense import (  # noqa: E402
    FACTEURS,
    GRILLE_AWG,
    PERIODES_AWG,
    annees_du_modele,
    decomposer,
)

TEMOIN = RACINE / "tests" / "temoins" / "ageing_report_france.json"
#: Les jeux d'hypothèses du COR que le script décompose.
PROJECTIONS = (("cor_reference", "modèle, productivité 0,7 %"),
               ("cor_productivite_haute", "modèle, productivité 1,0 %"))
NOMS = {"variation": "Dépense", "dependance": "Dépendance", "couverture": "Couverture",
        "prestation": "Prestation", "marche_du_travail": "Marché du travail",
        "residu": "Résidu"}


def awg() -> dict:
    """La décomposition publiée, par sous-période, et ses facteurs de 2022 et
    de 2070 : ceux que l'annexe permet de refaire."""
    temoin = json.loads(TEMOIN.read_text(encoding="utf-8"))
    publiee = {cle: {int(annee): valeur for annee, valeur in serie.items()}
               for cle, serie in temoin["decomposition"].items()}
    series = {cle: {int(annee): valeur for annee, valeur in serie.items()}
              for cle, serie in temoin["series"].items()}

    def cumul(cle: str, annee: int) -> float:
        return 0.0 if annee == 2022 else publiee[cle][annee]

    periodes = {}
    for debut, fin in PERIODES_AWG:
        periodes[f"{debut}-{fin}"] = {
            nom: cumul("depense" if nom == "variation" else nom, fin)
            - cumul("depense" if nom == "variation" else nom, debut)
            for nom in NOMS}

    def facteurs(annee: int) -> dict[str, float]:
        plus_de_65 = series["rapport_de_dependance"][annee] / 100 * series["population_20_64"][annee]
        return {"dependance": series["rapport_de_dependance"][annee] / 100,
                "couverture": series["pensionnes"][annee] / plus_de_65,
                "taux_emploi": series["population_20_64"][annee] / series["emploi_20_64"][annee]}

    return {"part_pib": {annee: series["depense_brute"][annee] for annee in (2022, 2070)},
            "periodes": periodes, "facteurs": {2022: facteurs(2022), 2070: facteurs(2070)}}


def modele(projection: str, scenario: str = "actuel") -> dict:
    """La décomposition du modèle sous ce jeu d'hypothèses, pour ce système."""
    from retraite_notionnelle import Parametres, memoire
    from retraite_notionnelle.donnees.population import Population
    from retraite_notionnelle.simulateur import Simulateur

    parametres = Parametres(scenario_projection=projection)
    annees = annees_du_modele(memoire.cout(parametres).avenir,
                              Population(parametres.racine_donnees),
                              Simulateur(parametres).macro, scenario)
    decomposition = decomposer(annees)
    return {
        "part_pib": {annee: decomposition.part_pib[annee] for annee in (2022, 2070)},
        "periodes": {f"{debut}-{fin}": decomposition.entre(debut, fin)
                     for debut, fin in PERIODES_AWG},
        "variations": {nom: getattr(annees[2070], nom) / getattr(annees[2022], nom) - 1
                       for nom in FACTEURS},
        "niveaux": {annee: {"retraites": annees[annee].retraites,
                            "population_65": annees[annee].population_65,
                            "dependance": annees[annee].dependance,
                            "couverture": annees[annee].couverture}
                    for annee in (2022, 2070)},
    }


def _signe(valeur: float, decimales: int = 2) -> str:
    return f"{valeur:+.{decimales}f}".replace("-", "−").replace(".", ",")


def _nombre(valeur: float, decimales: int = 2) -> str:
    return f"{valeur:.{decimales}f}".replace(".", ",")


def tableau(colonnes: dict[str, dict], periode: str = "2022-2070") -> list[str]:
    """Une ligne par effet, une colonne par source, sur une sous-période."""
    lignes = ["| " + periode + " | " + " | ".join(colonnes) + " |",
              "|---|" + "---|" * len(colonnes)]
    for nom, libelle in NOMS.items():
        lignes.append(f"| {libelle} | " + " | ".join(
            _signe(source["periodes"][periode][nom]) for source in colonnes.values()) + " |")
    return lignes


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--systemes", action="store_true",
                           help="décompose aussi les six systèmes, sous la référence du COR")
    analyseur.add_argument("--json", type=Path, help="écrit les résultats dans ce fichier")
    arguments = analyseur.parse_args(argv)

    colonnes = {"Ageing Report 2024": awg()}
    for projection, libelle in PROJECTIONS:
        colonnes[libelle] = modele(projection)
    resultats: dict = {"actuel": colonnes}

    print("Dépense de 2022 et de 2070, en % du PIB : " + " ; ".join(
        f"{nom} {_nombre(source['part_pib'][2022])} → {_nombre(source['part_pib'][2070])}"
        for nom, source in colonnes.items()))
    print()
    for debut, fin in PERIODES_AWG:
        print("\n".join(tableau(colonnes, f"{debut}-{fin}")))
        print()
    reference = colonnes[PROJECTIONS[0][1]]
    publie = colonnes["Ageing Report 2024"]["facteurs"]
    print("Variations des facteurs de 2022 à 2070, en % — modèle (0,7 %) : " + ", ".join(
        f"{NOMS[nom].lower()} {_signe(variation * 100, 1)}"
        for nom, variation in reference["variations"].items()))
    print("AWG : " + ", ".join(
        f"{NOMS.get(nom, 'taux d’emploi inverse').lower()} "
        f"{_signe((publie[2070][nom] / publie[2022][nom] - 1) * 100, 1)}"
        for nom in publie[2022]))
    niveaux = reference["niveaux"]
    print(f"Couverture du modèle : {_nombre(niveaux[2022]['couverture'], 3)} → "
          f"{_nombre(niveaux[2070]['couverture'], 3)} ({_nombre(niveaux[2022]['retraites'] / 1e6)}"
          f" → {_nombre(niveaux[2070]['retraites'] / 1e6)} millions de retraités) ; de l'AWG : "
          f"{_nombre(publie[2022]['couverture'], 3)} → {_nombre(publie[2070]['couverture'], 3)}")

    if arguments.systemes:
        from retraite_notionnelle.cout import SCENARIOS

        systemes = {libelle: modele(PROJECTIONS[0][0], scenario)
                    for scenario, libelle in SCENARIOS}
        resultats["systemes"] = systemes
        print()
        print("Les six systèmes, sous la référence du COR (dépense de 2022 → 2070 : " + " ; ".join(
            f"{libelle.split('.')[0]}. {_nombre(source['part_pib'][2022])} → "
            f"{_nombre(source['part_pib'][2070])}" for libelle, source in systemes.items()) + ")")
        print()
        print("\n".join(tableau({libelle.split(".")[0] + ".": source
                                 for libelle, source in systemes.items()})))

    if arguments.json:
        arguments.json.write_text(json.dumps(resultats, ensure_ascii=False, indent=1,
                                             default=str) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
