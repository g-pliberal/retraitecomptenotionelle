#!/usr/bin/env python3
"""La dépense de pensions de la France et ses facteurs, projetés par l'Ageing Report de 2024.

    python scripts/fetch/ageing_report.py
    python scripts/fetch/ageing_report.py --fichier 2024_Ageing_Report-Statistical_annex_all_countryfiches.xlsx

POURQUOI CE TÉMOIN. La Commission européenne et le Comité de politique
économique (le groupe de travail sur le vieillissement, l'AWG) projettent tous
les trois ans la dépense de pensions de chaque État, avec le modèle de cet
État — Destinie pour la France — sous des hypothèses communes, et la
DÉCOMPOSENT en quatre facteurs (volume 1, encadré I.1.1 ; fiche France,
figure 4) :

    dépense / PIB = (65 ans et plus / 20-64 ans)              dépendance
                  × (pensionnés / 65 ans et plus)             couverture
                  × (pension moyenne / PIB par heure 20-74)   prestation
                  × (20-64 ans / heures travaillées 20-74)    marché du travail

Le dépôt fait la même chose de sa propre trajectoire
(``src/retraite_notionnelle/facteurs_depense.py``, action 138, étape 3), et
``tests/test_facteurs_depense.py`` s'y confronte.

LA SOURCE. L'annexe statistique des fiches pays, un classeur par feuilles
d'État : « FRa » (démographie, hypothèses macroéconomiques, marché du
travail, rapports de dépendance) et « FRb » (dépense, indicateurs, scénarios,
décomposition). Elle porte, année par année de 2022 à 2070 et sans arrondi,
ce que la fiche France imprime au dixième dans ses tableaux 7 à 11, et la
décomposition cumulée depuis 2022 de cinq ans en cinq ans. C'est elle qui a
permis de retrouver comment l'AWG chiffre un effet, que ni la fiche ni le
volume 1 n'écrivent : la somme, pas à pas — 2022, 2025, 2030, …, 2070 —, de
la dépense en part de PIB au début du pas multipliée par la variation
relative du facteur sur le pas ; le résidu est ce que la somme des effets
laisse de la variation. Appliquée aux séries de l'annexe, la formule redonne
les effets publiés de la dépendance, de la couverture, de la couverture des
65 ans et plus et du taux d'emploi au dix-millième de point.

Ce que l'annexe ne publie pas, et que la décomposition demande : les heures
travaillées et le PIB en niveau, qui font la prestation et le marché du
travail. Leurs effets se lisent donc tels quels, sans se refaire.

Le site de la Commission répond parfois 429 à un téléchargement trop proche
d'un autre : ``--fichier`` lit le classeur déjà téléchargé. Le témoin est
versionné : les tests le relisent sans réseau.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
URL = ("https://economy-finance.ec.europa.eu/document/download/"
       "e248db46-f876-4e72-8821-efae678e81ea_en?filename="
       "2024_Ageing_Report-Statistical_annex_all_countryfiches.xlsx")
FICHE = ("https://economy-finance.ec.europa.eu/document/download/"
         "e412927a-ea31-406d-bb6c-c925914123e9_en?filename="
         "2024-ageing-report-country-fiche-France.pdf")
SORTIE = RACINE / "tests" / "temoins" / "ageing_report_france.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
ANNEES = tuple(range(2022, 2071))
#: Les années où l'annexe publie la décomposition cumulée depuis 2022.
PAS = tuple(range(2025, 2071, 5))

#: Ce que le témoin garde, par sa clé : la feuille, la section (l'intitulé de
#: la ligne d'en-tête des années), l'intitulé de la ligne et son rang dans la
#: section. Les intitulés se répètent : « males » donne l'espérance de vie à la
#: naissance, puis, au second rang, celle à 65 ans.
SERIES: dict[str, tuple[str, str, str, int]] = {
    # La dépense, en % du PIB.
    "depense_brute": ("FRb", "Baseline as % of GDP", "Public pensions, gross", 1),
    "depense_vieillesse": ("FRb", "Baseline as % of GDP",
                           "Of which: Old-age and early pensions", 1),
    "depense_invalidite": ("FRb", "Baseline as % of GDP", "Disability pensions", 1),
    "depense_survivants": ("FRb", "Baseline as % of GDP", "Survivors' pensions", 1),
    "depense_contributive": ("FRb", "Baseline as % of GDP",
                             "Earnings-related pensions, gross", 1),
    "depense_nouvelles_pensions": ("FRb", "Baseline as % of GDP",
                                   "New old-age and early pensions, gross", 1),
    "cotisations": ("FRb", "Baseline as % of GDP", "Public pensions, contributions", 1),
    "solde": ("FRb", "Baseline as % of GDP",
              "Balance of the pension system (contributions - gross expenditure)", 1),
    "recettes_fiscales": ("FRb", "Baseline as % of GDP",
                          "Public pension scheme, tax revenues", 1),
    # Les indicateurs : des milliers de personnes, des pour-cent, des années.
    "pensionnes": ("FRb", "Additional indicators", "Pensioners (public, 1000 persons)", 1),
    "pensionnes_65_plus": ("FRb", "Additional indicators",
                           "Pensioners aged 65+ (1000 persons)", 1),
    "taux_de_prestation": ("FRb", "Additional indicators",
                           "Benefit ratio (total public pensions, gross)", 1),
    "taux_de_remplacement": ("FRb", "Additional indicators",
                             "Gross replacement rate at retirement "
                             "(earnings-related public pensions)", 1),
    "taux_d_acquisition": ("FRb", "Additional indicators",
                           "Average accrual rate (new earnings-related pensions)", 1),
    "duree_de_cotisation": ("FRb", "Additional indicators",
                            "Average contributory period (new earnings-related pensions)", 1),
    "cotisants": ("FRb", "Additional indicators",
                  "Contributors (public pensions, 1000 persons)", 1),
    # La démographie et le marché du travail.
    "fecondite": ("FRa", "Demographic projections - EUROPOP2023 (Eurostat)",
                  "Fertility rate", 1),
    "esperance_65_hommes": ("FRa", "Demographic projections - EUROPOP2023 (Eurostat)",
                            "males", 2),
    "esperance_65_femmes": ("FRa", "Demographic projections - EUROPOP2023 (Eurostat)",
                            "females", 2),
    "solde_migratoire": ("FRa", "Demographic projections - EUROPOP2023 (Eurostat)",
                         "Net migration (thousands)", 1),
    "population_20_64": ("FRa", "Labour force assumptions",
                         "Working-age population (20-64y; thousands)", 1),
    "rapport_de_dependance": ("FRa", "Dependency ratios", "Old-age dependency ratio (3)", 1),
    "emploi_20_64": ("FRa", "Labour force assumptions", "Employment (20-64y; millions)", 1),
    "emploi_20_74": ("FRa", "Labour force assumptions", "Employment (20-74y; millions)", 1),
    "chomage_20_64": ("FRa", "Labour force assumptions", "Unemployment rate (20-64y)", 1),
    "age_de_sortie": ("FRa", "Labour force assumptions",
                      "Average labour market exit age (1)", 1),
    "productivite_horaire": ("FRa", "Macroeconomic assumptions",
                             "Labour productivity per hour (growth rate)", 1),
    "heures_travaillees": ("FRa", "Macroeconomic assumptions",
                           "Labour input: hours worked (growth rate)", 1),
}

#: La décomposition cumulée depuis 2022, en points de PIB, par sa clé.
SECTION_DECOMPOSITION = ("Breakdown of the increase (in pps) in public pension "
                         "expenditure - cumulated change from 2022")
DECOMPOSITION: dict[str, str] = {
    "depense": "Public pensions, gross as % of GDP - pps change from 2022",
    "dependance": "Dependency ratio",
    "couverture": "Coverage ratio",
    "couverture_vieillesse": "Of which: Old-age",
    "couverture_precoce": "Early-age",
    "effet_cohorte": "Cohort effect",
    "prestation": "Benefit ratio",
    "marche_du_travail": "Labour market ratio",
    "taux_emploi": "Of which: Employment rate",
    "intensite": "Labour intensity",
    "carriere": "Career shift",
    "residu": "Interaction effect (residual)",
}


def lignes_de(grille: dict) -> dict[tuple[str, str, int], dict[int, float]]:
    """Les lignes d'une feuille par (section, intitulé, rang), chacune ses
    valeurs par année.

    Une section s'ouvre sur sa ligne d'en-tête, qui porte 2022 puis 2023 dans
    les colonnes des années ; le rang compte les lignes de même intitulé
    depuis cet en-tête. Une ligne sans valeur — un sous-titre — reste rendue,
    vide.
    """
    if not grille:
        return {}
    hauteur = max(ligne for ligne, _ in grille) + 1
    largeur = max(colonne for _, colonne in grille) + 1
    resultat: dict[tuple[str, str, int], dict[int, float]] = {}
    section = ""
    colonnes: dict[int, int] = {}
    rangs: dict[str, int] = {}
    for numero in range(hauteur):
        cellules = [grille.get((numero, colonne)) for colonne in range(largeur)]
        intitule = cellules[1] if largeur > 1 else None
        if not isinstance(intitule, str):
            continue
        intitule = intitule.strip()
        if largeur > 4 and cellules[3] == 2022.0 and cellules[4] == 2023.0:
            section = intitule
            colonnes = {colonne: int(valeur) for colonne, valeur in enumerate(cellules)
                        if colonne >= 3 and isinstance(valeur, float)}
            rangs = {}
            continue
        rangs[intitule] = rangs.get(intitule, 0) + 1
        resultat[(section, intitule, rangs[intitule])] = {
            annee: cellules[colonne] for colonne, annee in colonnes.items()
            if isinstance(cellules[colonne], float)}
    return resultat


def lire(grilles: dict[str, dict]) -> dict:
    """Les séries et la décomposition de la France, des feuilles FRa et FRb."""
    par_feuille = {nom: lignes_de(grilles[nom]) for nom in ("FRa", "FRb")}
    series: dict[str, dict[str, float]] = {}
    for cle, (feuille, section, intitule, rang) in SERIES.items():
        valeurs = par_feuille[feuille].get((section, intitule, rang))
        if valeurs is None:
            raise ValueError(f"{feuille} : ligne absente — {section} / {intitule} ({rang})")
        series[cle] = {str(annee): valeurs[annee] for annee in ANNEES if annee in valeurs}
    decomposition: dict[str, dict[str, float]] = {}
    for cle, intitule in DECOMPOSITION.items():
        valeurs = par_feuille["FRb"].get((SECTION_DECOMPOSITION, intitule, 1))
        if valeurs is None:
            raise ValueError(f"FRb : ligne de la décomposition absente — {intitule}")
        decomposition[cle] = {str(annee): valeurs[annee] for annee in PAS if annee in valeurs}
    return {"series": series, "decomposition": decomposition}


def controler(temoin: dict) -> list[str]:
    """La forme que les tests supposent, et deux identités que l'annexe tient."""
    erreurs = []
    attendues = [str(annee) for annee in ANNEES]
    for cle, serie in temoin["series"].items():
        if sorted(serie, key=int) != attendues:
            erreurs.append(f"{cle} : années {sorted(serie, key=int)[:2]}…")
    for cle, serie in temoin["decomposition"].items():
        if sorted(serie, key=int) != [str(annee) for annee in PAS]:
            erreurs.append(f"décomposition, {cle} : années {sorted(serie, key=int)[:2]}…")
    if erreurs:
        return erreurs
    series, decomposition = temoin["series"], temoin["decomposition"]
    for annee in map(str, PAS):
        variation = series["depense_brute"][annee] - series["depense_brute"]["2022"]
        if abs(decomposition["depense"][annee] - variation) > 1e-3:
            erreurs.append(f"{annee} : la variation publiée n'est pas celle de la dépense")
        somme = sum(decomposition[cle][annee] for cle in
                    ("dependance", "couverture", "prestation", "marche_du_travail", "residu"))
        if abs(somme - decomposition["depense"][annee]) > 1e-3:
            erreurs.append(f"{annee} : les effets et le résidu ne font pas la variation")
    return erreurs


def _classeur(fichier: Path | None) -> bytes:
    """Le classeur déjà téléchargé, ou celui du réseau."""
    if fichier:
        return fichier.read_bytes()
    requete = urllib.request.Request(URL, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=300) as reponse:
        return reponse.read()


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--fichier", type=Path,
                           help="annexe statistique déjà téléchargée, lue au lieu du réseau")
    arguments = analyseur.parse_args(argv)
    lu = lire(feuilles(_classeur(arguments.fichier), noms=("FRa", "FRb")))
    temoin = {
        "source": {
            "editeur": "Commission européenne (DG ECFIN) et Comité de politique "
                       "économique (groupe de travail sur le vieillissement, AWG)",
            "reference": "2024 Ageing Report, annexe statistique des fiches pays, "
                         "feuilles FRa et FRb ; fiche France, tableaux 7 à 11 et "
                         "figure 4 ; volume 1 (Institutional Paper 279), encadré I.1.1",
            "url": URL,
            "fiche": FICHE,
            "lu_le": "2026-10-13",
        },
        "conventions": {
            "decomposition": (
                "dépense / PIB = (65 ans et plus / 20-64 ans) × (pensionnés / 65 ans "
                "et plus) × (pension moyenne / PIB par heure travaillée des 20-74 ans) "
                "× (20-64 ans / heures travaillées des 20-74 ans) ; la couverture se "
                "décompose en celle des 65 ans et plus, plus celle des moins de 65 ans "
                "rapportée aux 50-64 ans fois l'effet de cohorte (50-64 / 65 ans et "
                "plus), et le marché du travail en taux d'emploi des 20-64 ans, "
                "intensité du travail et allongement des carrières au-delà de 64 ans"),
            "effets": (
                "cumulés depuis 2022, en points de PIB : la somme, pas à pas (2022, "
                "2025, 2030, …, 2070), de la dépense brute en % du PIB au début du pas "
                "multipliée par la variation relative du facteur sur le pas ; le "
                "résidu, ou effet d'interaction, est la variation de la dépense moins "
                "la somme des effets. Les sous-effets de la couverture ne s'ajoutent "
                "pas"),
            "perimetre": (
                "pensions publiques brutes : vieillesse et anticipées, minimum "
                "vieillesse compris, invalidité (AAH, rentes d'accident du travail, "
                "pensions d'invalidité) et survivants ; pensionnés résidant ou non en "
                "France"),
            "unites": (
                "dépense et décomposition en % et en points de PIB ; personnes en "
                "milliers, emploi en millions ; taux et rapports en % ; croissances "
                "en % par an ; espérance de vie en années"),
            "hypotheses": (
                "population EUROPOP2023 d'Eurostat ; productivité horaire de 1,03 % "
                "par an en moyenne de 2022 à 2070, la PTF convergeant vers 0,8 % ; "
                "législation d'avant la loi de financement de la sécurité sociale "
                "pour 2026, qui décale le calendrier de la réforme de 2023"),
        },
        **lu,
    }
    erreurs = controler(temoin)
    if erreurs:
        print("Annexe refusée :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    SORTIE.write_text(json.dumps(temoin, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    print(f"Témoin écrit dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
