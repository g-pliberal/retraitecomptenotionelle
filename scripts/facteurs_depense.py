#!/usr/bin/env python3
"""La dépense de retraite en ses quatre facteurs, confrontée à l'Ageing Report de 2024.

    python scripts/facteurs_depense.py              # le système actuel contre l'AWG
    python scripts/facteurs_depense.py --systemes   # et les six systèmes
    python scripts/facteurs_depense.py --sans-suspension  # et la réforme de 2023 entière
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

La couverture se partage ensuite entre les retraités de 65 ans et plus et les
plus jeunes, des deux côtés, puis la dynamique du modèle se porte au
périmètre de l'AWG (``au_perimetre``) : ce qui reste de l'écart est celle-ci,
ce qui part, le périmètre ; la part des pensionnés de moins de 65 ans de
l'AWG que l'âge légal ne fait pas reculer — l'invalidité, l'AAH, la réversion
seule — y garde sa prévalence parmi les 20-64 ans, à la mesure qu'en donnent
leurs sources (``tests/temoins/pensionnes_de_2022.json``).
``--sans-suspension`` refait le modèle sur une copie
des données où la réforme de 2023 s'applique entière, sans la suspension de
la loi de financement pour 2026 (``REFORME_2023_ENTIERE``) : l'univers de
l'AWG, qui l'a précédée.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.facteurs_depense import (  # noqa: E402
    FACTEURS,
    GRILLE_AWG,
    JEUNES,
    PERIODES_AWG,
    STABLES,
    annees_du_modele,
    au_perimetre,
    decomposer,
    partager_couverture,
    pensionnes_de_2022,
    retraites_par_age,
)
from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

TEMOIN = RACINE / "tests" / "temoins" / "ageing_report_france.json"
PENSIONNES = RACINE / "tests" / "temoins" / "pensionnes_de_2022.json"
#: Les jeux d'hypothèses du COR que le script décompose.
PROJECTIONS = (("cor_reference", "modèle, productivité 0,7 %"),
               ("cor_productivite_haute", "modèle, productivité 1,0 %"))
NOMS = {"variation": "Dépense", "dependance": "Dépendance", "couverture": "Couverture",
        "prestation": "Prestation", "marche_du_travail": "Marché du travail",
        "residu": "Résidu"}
#: Les deux parts de la couverture (``partager_couverture``).
PARTS = {"vieillesse": "65 ans et plus", "precoce": "Moins de 65 ans"}
#: Les sous-périodes où la couverture se partage.
PERIODES_COUVERTURE = ((2022, 2030), (2030, 2070), (2022, 2070))
#: Les pensionnés de 2022, par catégorie (``pensionnes_de_2022``).
CATEGORIES = {"droit_direct": "droit direct", "reversion_seule": "réversion seule",
              "invalidite": "invalidité", "aah": "AAH"}

#: La réforme de 2023 entière, telle que l'AWG l'a projetée avant la
#: suspension : l'âge d'ouverture et la durée requise des générations que la
#: loi n° 2025-1403 (article 105) a retardées, de L. 161-17-2 et L. 161-17-3
#: dans leur version du 1er septembre 2023 (``duree_requise_avant_suspension.csv``
#: pour la durée). Les lignes de la génération 1965 au 1er avril, que la
#: suspension a créées, disparaissent.
REFORME_2023_ENTIERE = {
    "age_ouverture_requis.csv": {"1964": "63.00", "1965": "63.25", "1966": "63.50",
                                 "1967": "63.75", "1968": "64.00"},
    "duree_assurance_requise.csv": {"1964": "171", "1965": "172"},
}


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

    population_65 = {annee: series["rapport_de_dependance"][annee] / 100
                     * series["population_20_64"][annee] for annee in GRILLE_AWG}
    couverture = {"part_pib": {annee: series["depense_brute"][annee] for annee in GRILLE_AWG},
                  "retraites": {annee: series["pensionnes"][annee] for annee in GRILLE_AWG},
                  "retraites_agees": {annee: series["pensionnes_65_plus"][annee]
                                      for annee in GRILLE_AWG},
                  "population_65": population_65,
                  "population_20_64": {annee: series["population_20_64"][annee]
                                       for annee in GRILLE_AWG}}
    return {"part_pib": {annee: series["depense_brute"][annee] for annee in (2022, 2070)},
            "periodes": periodes, "facteurs": {2022: facteurs(2022), 2070: facteurs(2070)},
            "couverture": couverture}


def parts_de_couverture(series: dict) -> dict[str, dict[str, float]]:
    """Les deux parts de la couverture et leur somme, par sous-période."""
    parts = partager_couverture(series["part_pib"], series["retraites"],
                                series["retraites_agees"], series["population_65"])

    def cumul(serie: dict[int, float], annee: int) -> float:
        return 0.0 if annee == GRILLE_AWG[0] else serie[annee]

    resultat = {}
    for debut, fin in PERIODES_COUVERTURE:
        ligne = {nom: cumul(serie, fin) - cumul(serie, debut) for nom, serie in parts.items()}
        ligne["couverture"] = somme_ordonnee(ligne.values())
        resultat[f"{debut}-{fin}"] = ligne
    return resultat


def porte_au_perimetre(propre: dict, autre: dict, stable: float = 0.0,
                       population_stable: dict | None = None) -> dict:
    """Les séries de couverture d'une trajectoire, portées au périmètre d'une
    autre : ses niveaux de 2022 et sa dépense, la dynamique de la première,
    sauf la part ``stable`` des plus jeunes, qui garde son rapport à
    ``population_stable`` (``au_perimetre``)."""
    premiere = GRILLE_AWG[0]
    agees = autre["retraites_agees"][premiere] / autre["population_65"][premiere]
    jeunes = autre["retraites"][premiere] / autre["population_65"][premiere] - agees
    retraites, retraites_agees = au_perimetre(
        autre["population_65"], agees, jeunes, propre["retraites"],
        propre["retraites_agees"], propre["population_65"], stable=stable,
        population_stable=population_stable)
    return {"part_pib": autre["part_pib"], "retraites": retraites,
            "retraites_agees": retraites_agees, "population_65": autre["population_65"]}


def part_stable(propre: dict, autre: dict, periode: str = "2022-2070",
                population_stable: dict | None = None) -> float:
    """La part stable des plus jeunes de ``autre`` qui, portée au périmètre,
    refait leur effet sur ``periode`` : l'effet recule à mesure qu'elle
    croît, et la dichotomie la trouve entre zéro et un."""
    cible = parts_de_couverture(autre)[periode]["precoce"]
    bas, haut = 0.0, 1.0
    for _ in range(50):
        milieu = (bas + haut) / 2
        porte = parts_de_couverture(porte_au_perimetre(propre, autre, milieu,
                                                       population_stable))
        if porte[periode]["precoce"] < cible:
            bas = milieu
        else:
            haut = milieu
    return (bas + haut) / 2


def part_stable_mesuree(autre: dict) -> tuple[float, dict[str, float]]:
    """La part stable des plus jeunes de ``autre`` (l'AWG), mesurée : ses
    pensionnés de moins de 65 ans que l'âge légal ne fait pas reculer, comptés
    à leurs sources au 31 décembre 2022 (``pensionnes_de_2022``), rapportés aux
    siens ; et ses moins de 65 ans par catégorie, en personnes."""
    mesures = pensionnes_de_2022(json.loads(PENSIONNES.read_text(encoding="utf-8")))
    par_categorie = {categorie: somme_ordonnee(tranches[t] for t in JEUNES)
                     for categorie, tranches in mesures.items()}
    premiere = GRILLE_AWG[0]
    jeunes = (autre["retraites"][premiere] - autre["retraites_agees"][premiere]) * 1000
    return somme_ordonnee(par_categorie[c] for c in STABLES) / jeunes, par_categorie


def reforme_entiere(racine: Path, destination: Path) -> Path:
    """Une copie des données de ``racine`` sous la réforme de 2023 entière
    (``REFORME_2023_ENTIERE``)."""
    copie = destination / "data"
    shutil.copytree(racine, copie)
    for nom, valeurs in REFORME_2023_ENTIERE.items():
        fichier = copie / "reference" / "legislation" / nom
        texte = fichier.read_text(encoding="utf-8")
        texte, ote = re.subn(r"^1965\.25,.*\n", "", texte, flags=re.M)
        if ote != 1:
            raise ValueError(f"{nom} : la ligne de la génération 1965 au 1er avril manque")
        for generation, valeur in valeurs.items():
            texte, remplace = re.subn(rf"^{generation},[^,]+,", f"{generation},{valeur},",
                                      texte, flags=re.M)
            if remplace != 1:
                raise ValueError(f"{nom} : la génération {generation} manque")
        fichier.write_text(texte, encoding="utf-8")
    return copie


def modele(projection: str, scenario: str = "actuel", racine: Path | None = None) -> dict:
    """La décomposition du modèle sous ce jeu d'hypothèses, pour ce système,
    sur les données de ``racine`` (celles du dépôt par défaut)."""
    from retraite_notionnelle import Parametres, memoire
    from retraite_notionnelle.donnees.population import Population
    from retraite_notionnelle.simulateur import Simulateur

    parametres = Parametres(scenario_projection=projection)
    if racine is not None:
        parametres = Parametres(scenario_projection=projection, racine_donnees=racine)
    annees = annees_du_modele(memoire.cout(parametres).avenir,
                              Population(parametres.racine_donnees),
                              Simulateur(parametres).macro, scenario)
    decomposition = decomposer(annees)
    couverture = None
    if scenario == "actuel":
        par_age = retraites_par_age(parametres, GRILLE_AWG)
        couverture = {"part_pib": dict(decomposition.part_pib),
                      "retraites": {annee: par_age[annee][0] for annee in GRILLE_AWG},
                      "retraites_agees": {annee: par_age[annee][1] for annee in GRILLE_AWG},
                      "population_65": {annee: annees[annee].population_65
                                        for annee in GRILLE_AWG}}
    return {"couverture": couverture,
            
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
    analyseur.add_argument("--sans-suspension", action="store_true",
                           help="refait le modèle sous la réforme de 2023 entière")
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

    publiee = colonnes["Ageing Report 2024"]["couverture"]
    colonnes_couverture = {
        "Ageing Report 2024": publiee,
        "modèle": reference["couverture"],
        "modèle au périmètre de l'AWG": porte_au_perimetre(reference["couverture"], publiee),
    }
    stable = part_stable(reference["couverture"], publiee)
    calee = part_stable(reference["couverture"], publiee,
                        population_stable=publiee["population_20_64"])
    mesuree, par_categorie = part_stable_mesuree(publiee)
    resultats.update(part_stable=stable, part_stable_20_64=calee, part_stable_mesuree=mesuree)
    colonnes_couverture[f"et {_nombre(mesuree * 100, 0)} % stables, mesurés"] = (
        porte_au_perimetre(reference["couverture"], publiee, mesuree,
                           publiee["population_20_64"]))
    if arguments.sans_suspension:
        from retraite_notionnelle.config import RACINE_DONNEES

        with tempfile.TemporaryDirectory() as dossier:
            sans = modele(PROJECTIONS[0][0], racine=reforme_entiere(RACINE_DONNEES, Path(dossier)))
        resultats["sans_suspension"] = sans
        colonnes_couverture["modèle sans la suspension"] = sans["couverture"]
        print()
        print("Sans la suspension, la référence du COR (dépense de 2022 → 2070 : "
              f"{_nombre(sans['part_pib'][2022])} → {_nombre(sans['part_pib'][2070])})")
        print()
        print("\n".join(tableau({"modèle": reference, "modèle sans la suspension": sans},
                                "2022-2030")))
    parts = {nom: parts_de_couverture(series) for nom, series in colonnes_couverture.items()}
    resultats["couverture"] = parts

    def jeunes(series: dict, par: float) -> float:
        return (series["retraites"][2022] - series["retraites_agees"][2022]) / par

    propre = reference["couverture"]
    print()
    print("Retraités de moins de 65 ans en 2022, en millions : modèle "
          f"{_nombre(jeunes(propre, 1e6))}, AWG {_nombre(jeunes(publiee, 1e3))} ; par "
          f"personne de 65 ans et plus : modèle "
          f"{_nombre(jeunes(propre, propre['population_65'][2022]), 3)}, AWG "
          f"{_nombre(jeunes(publiee, publiee['population_65'][2022]), 3)}")
    print("Pensionnés de moins de 65 ans au 31 décembre 2022, mesurés, en millions : "
          + ", ".join(f"{CATEGORIES[nom]} {_nombre(effectif / 1e6)}"
                      for nom, effectif in par_categorie.items())
          + f" ; part stable (invalidité, AAH, réversion seule) : {_nombre(mesuree * 100, 1)} %,"
          f" {_nombre(jeunes(publiee, 1e3) * mesuree)} millions. Calée pour refaire l'effet "
          f"des moins de 65 ans de l'AWG de 2022-2070 : {_nombre(calee * 100, 1)} % si elle "
          f"garde sa prévalence parmi les 20-64 ans, {_nombre(stable * 100, 1)} % si elle "
          f"garde son rapport aux 65 ans et plus")
    for periode in (f"{debut}-{fin}" for debut, fin in PERIODES_COUVERTURE):
        print()
        print(f"| Couverture, {periode} | " + " | ".join(parts) + " |")
        print("|---|" + "---|" * len(parts))
        for nom, libelle in (*PARTS.items(), ("couverture", "Couverture")):
            print(f"| {libelle} | " + " | ".join(
                _signe(source[periode][nom]) for source in parts.values()) + " |")

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
