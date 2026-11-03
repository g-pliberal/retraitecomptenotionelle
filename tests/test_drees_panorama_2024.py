"""Les chiffres de 2024 du panorama de la DREES, édition 2026, recoupés au dépôt.

L'action 178, étape 2 : chaque total que le panorama « Les retraités et les
retraites » publie d'une source que le dépôt lit déjà est recoupé au fichier
qu'il lit, à l'arrondi de la publication. Ces sources sont l'EACR, par son
cadrage (``data/reference/regimes/effectifs_retraites.csv``) et par ses
tables B, C et H (``tests/temoins/drees_eacr_tables_2026.json``), et les
comptes de la protection sociale (``data/reference/macro/depenses_retraite.csv``).

Les valeurs attendues sont lues dans le PDF, à la page imprimée que chaque test
cite ; celles qu'il ne chiffre pas, dans le classeur de la fiche, le membre
``fiche_NN.xlsx`` de l'archive ``drees_panorama_retraites_2026_classeurs``, à
la feuille citée. Ce que le dépôt ne porte pas, ou porte autrement, est dit
dans la note de l'étape (``docs/feuille_de_route/178/``) : les effectifs de la
réversion, dont le dépôt ne garde que la masse ; les pensions de retraite au
sens strict, 395,3 milliards, dont il n'a pas les sous-postes.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
EACR = RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json"
EFFECTIFS = RACINE / "data" / "reference" / "regimes" / "effectifs_retraites.csv"
DEPENSES = RACINE / "data" / "reference" / "macro" / "depenses_retraite.csv"


def _lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


@pytest.fixture(scope="module")
def eacr() -> dict:
    return json.loads(EACR.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def effectifs() -> dict[tuple[int, str], float]:
    return {(int(l["annee"]), l["caisse"]): float(l["effectifs"]) for l in _lire(EFFECTIFS)}


#: Fiche 1, tableau 1 (page 21) : les retraités de droit direct tous régimes,
#: ensemble, en milliers, fin de chaque année.
RETRAITES_TOUS_REGIMES = {
    2004: 12_961, 2005: 13_263, 2006: 13_636, 2007: 14_022, 2008: 14_418,
    2009: 14_743, 2010: 15_082, 2011: 15_291, 2012: 15_349, 2013: 15_629,
    2014: 15_828, 2015: 15_980, 2016: 16_135, 2017: 16_252, 2018: 16_496,
    2019: 16_712, 2020: 16_674, 2021: 16_801, 2022: 16_975, 2023: 17_184,
    2024: 17_298,
}


def test_les_retraites_de_droit_direct_de_2004_a_2024_sont_ceux_du_cadrage(effectifs):
    """Les 17,3 millions de retraités de droit direct de fin 2024, et chaque
    année depuis 2004 : la ligne « Tous régimes » (code 0000) du cadrage de
    l'EACR, à mille près. Le panorama les tire de l'EIR et d'Ancetre, que le
    cadrage reprend tous régimes."""
    for annee, milliers in RETRAITES_TOUS_REGIMES.items():
        assert effectifs[(annee, "tous_regimes")] / 1000 == pytest.approx(milliers, abs=0.5), annee


#: Fiche 1, tableau 2 (page 23) : les retraités de droit direct de fin 2024,
#: par régime, en milliers ; les lignes qui sont une caisse du cadrage. Les
#: régimes spéciaux (663) et les professions libérales (493) en réunissent
#: plusieurs, dont certaines que le cadrage ne porte pas (Altadis, Retrep).
RETRAITES_PAR_REGIME_2024 = {
    "cnav": 14_745, "agirc_arrco": 12_796, "msa_salaries": 1_679,
    "msa_exploitants": 1_023, "fonction_publique_etat_civile": 1_641,
    "ircantec": 2_109, "cnracl": 1_393,
}


def test_les_retraites_de_2024_par_regime_sont_ceux_du_cadrage(effectifs):
    for caisse, milliers in RETRAITES_PAR_REGIME_2024.items():
        assert effectifs[(2024, caisse)] / 1000 == pytest.approx(milliers, abs=0.5), caisse


def test_les_retraites_de_2024_par_sexe_et_leur_pension_sont_ceux_de_la_table_c(eacr):
    """Fiche 1, tableau 1 (page 21) : 9 192 000 femmes et 8 106 000 hommes ;
    fiche 5, feuille « F05_Tableau 1 compl_bis », les retraités résidant en
    France ou à l'étranger : une pension de droit direct de 1 647 euros bruts
    par mois en moyenne, hors majoration pour trois enfants, 1 320 pour les
    femmes, 2 017 pour les hommes. La table C de l'EACR (Ancetre 2024) porte
    les mêmes têtes et les mêmes montants."""
    serie = eacr["droits_directs_par_age"]["series"]["ddir"]
    for sexe, milliers, euros in (("F", 9_192, 1_320), ("H", 8_106, 2_017),
                                  ("ensemble", 17_298, 1_647)):
        tetes, montant = serie[sexe]["Ensemble"]
        assert tetes / 1000 == pytest.approx(milliers, abs=0.5), sexe
        assert montant == pytest.approx(euros, abs=0.5), sexe


def test_les_liquidants_de_2024_sont_ceux_des_tables_b_et_c(eacr):
    """Fiche 2, tableau 1 (page 30) : 858 000 assurés ont liquidé un droit
    direct en 2024, 435 000 femmes et 423 000 hommes — le champ ``nl_ddir`` de
    la table C, à mille près pour les hommes, 422 466, que le tableau porte à
    423 000 quand femmes et hommes y font l'ensemble ; les 718 000
    primo-liquidants, que l'EIR seul compte, n'ont pas d'équivalent dans
    l'EACR. Fiche 2, tableau 2 (page 33), colonne 2024 : 648 000 au régime
    général, 43 000 à la MSA salariés, 30 000 à la MSA non-salariés et 63 000
    à la CNRACL — les liquidants de la table B."""
    serie = eacr["droits_directs_par_age"]["series"]["nl_ddir"]
    for sexe, milliers, ecart in (("F", 435, 0.5), ("H", 423, 1.0), ("ensemble", 858, 0.5)):
        assert serie[sexe]["Ensemble"][0] / 1000 == pytest.approx(milliers, abs=ecart), sexe
    table_b = eacr["liquidants_par_age"]["series"]
    for code, milliers in (("0015", 648), ("0021", 43), ("0022", 30), ("0032", 63)):
        assert table_b[code]["Ensemble"] / 1000 == pytest.approx(milliers, abs=0.5), code


#: Fiche 16, feuille « F16_Graphique 3 » : la répartition des nouveaux
#: retraités de 2024 selon leur âge au 31 décembre, en %, par régime.
TRANCHES = ("moins de 57", "57 à 59", "60", "61", "62", "63 à 64", "65", "66", "plus de 66")
REPARTITION_PAR_AGE_2024 = {
    "0015": (0.1, 0.2, 5.5, 9.6, 28.5, 27.8, 7.2, 4.5, 16.7),    # régime général
    "0021": (0.1, 0.2, 5.4, 11.2, 26.8, 24.5, 6.9, 3.9, 21.0),   # MSA salariés
    "0022": (0.0, 0.1, 3.4, 11.2, 23.0, 25.4, 6.6, 4.9, 25.2),   # MSA non-salariés
    "0032": (0.2, 5.2, 6.4, 9.9, 29.0, 30.9, 6.7, 3.9, 7.8),     # CNRACL
}


def _tranche(age: str) -> str:
    if not age.isdigit():
        return {">70": "plus de 66"}.get(age, "moins de 57")  # « <50 », « 50 à 54 »
    age = int(age)
    if age < 57:
        return "moins de 57"
    if age <= 59:
        return "57 à 59"
    if age in (63, 64):
        return "63 à 64"
    return str(age) if age <= 66 else "plus de 66"


def test_l_age_des_nouveaux_retraites_de_2024_est_celui_de_la_table_b(eacr):
    """La table B compte les liquidants de chaque caisse par âge ; regroupés
    comme le graphique, ils en redonnent chaque part, au dixième près."""
    table_b = eacr["liquidants_par_age"]["series"]
    for code, parts in REPARTITION_PAR_AGE_2024.items():
        serie = table_b[code]
        compte = dict.fromkeys(TRANCHES, 0.0)
        for age, tetes in serie.items():
            if age != "Ensemble":
                compte[_tranche(age)] += tetes
        for tranche, part in zip(TRANCHES, parts):
            assert 100 * compte[tranche] / serie["Ensemble"] == pytest.approx(part, abs=0.051), (
                code, tranche)


#: Fiche 17, feuilles « F17_Tableau compl - Decote » et « … - Surcote » : la
#: part des nouveaux retraités de 2024 partis avec une décote, puis avec une
#: surcote, en %, et le code de la caisse dans la table H.
DECOTE_SURCOTE_2024 = {
    "0015": (13.4, 18.9),   # régime général
    "0021": (6.6, 18.3),    # MSA salariés
    "0022": (5.0, 33.9),    # MSA non-salariés
    "0012": (18.4, 37.6),   # FPE civils
}


def test_la_decote_et_la_surcote_des_nouveaux_retraites_de_2024_sont_celles_de_la_table_h(eacr):
    """Les liquidants de 2024 de la table H, partis avec une décote ou une
    surcote, rapportés à l'ensemble : les parts du panorama au dixième près,
    sauf une. La surcote des fonctionnaires civils de l'État y est de 38,9 %
    (le cube du SRE de 2024), et de 37,6 % au panorama : l'écart est déclaré,
    non expliqué, et ce test le tient pour qu'il ne change pas en silence."""
    table_h = eacr["conditions_liquidation"]["series"]
    for code, (decote, surcote) in DECOTE_SURCOTE_2024.items():
        flux = table_h[code]["flux"]["ensemble"]["2024"]
        assert 100 * flux["decote"] / flux["ensemble"] == pytest.approx(decote, abs=0.051), code
        mesure = 100 * flux["surcote"] / flux["ensemble"]
        if code == "0012":
            assert mesure == pytest.approx(38.9, abs=0.051)
            assert mesure - surcote == pytest.approx(1.3, abs=0.06)
        else:
            assert mesure == pytest.approx(surcote, abs=0.051), code


def test_le_risque_vieillesse_survie_de_2024_est_celui_des_comptes():
    """Fiche 10, encadré 1 (page 99) : 426,7 milliards d'euros de prestations
    du risque vieillesse-survie en 2024, dont 395,3 de pensions de retraite des
    régimes obligatoires (le champ du tableau 1, page 100). Le dépôt porte le
    poste E11-2 entier, qui est le premier chiffre."""
    depenses = {int(l["annee"]): float(l["depenses_meur"]) for l in _lire(DEPENSES)}
    assert depenses[2024] / 1000 == pytest.approx(426.7, abs=0.05)


# ---------------------------------------------------------------------------
# Ce que le dépôt n'avait pas : les séries des classeurs, que
# ``scripts/fetch/drees_panorama_classeurs.py`` lit et dépose, et que
# ``scripts/verifier_donnees.py`` certifie dans ``data/reference/``.
# ---------------------------------------------------------------------------

def _classeurs():
    chemin = RACINE / "scripts" / "fetch" / "drees_panorama_classeurs.py"
    specification = importlib.util.spec_from_file_location("drees_panorama_classeurs", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["drees_panorama_classeurs"] = module
    specification.loader.exec_module(module)
    return module


def test_l_age_conjoncturel_se_lit_par_sexe_sous_la_ligne_des_annees():
    """La feuille « F15_Graphique 1 », réduite à deux années : la ligne des
    années, puis une ligne par sexe, nommée dans la première colonne."""
    grille = {
        (1, 1): "Graphique 1. Âge conjoncturel moyen de départ à la retraite, selon le sexe, "
                "entre 2004 et 2024",
        (3, 2): 2004.0, (3, 22): 2024.0,
        (4, 1): "Femmes", (4, 2): 61.11, (4, 22): 63.29,
        (5, 1): "Hommes", (5, 2): 60.06, (5, 22): 62.59,
        (6, 1): "Ensemble", (6, 2): 60.58, (6, 22): 62.95,
        (8, 1): "Champ > Personnes résidant en France",
    }
    assert _classeurs().lire_age_conjoncturel(grille) == {
        "2004": {"F": 61.11, "H": 60.06, "ensemble": 60.58},
        "2024": {"F": 63.29, "H": 62.59, "ensemble": 62.95},
    }


def test_le_cumul_et_la_retraite_progressive_se_lisent_par_leurs_libelles():
    """Les feuilles « F22_Tableau1 » et « F22_Tableau2 », réduites à une
    année et à deux régimes ; une case « nd » n'est pas une valeur."""
    module = _classeurs()
    cumul = {
        (1, 1): " Tableau 1. Effectifs de retraités en situation de cumul d’une activité "
                "avec la retraite, de 2014 à 2024",
        (2, 1): "Année", (2, 2): "Effectifs de cumulants\n(en milliers)1, 2",
        (2, 3): "Part parmi les retraités\n (en %)1, 2", (2, 4): "Proportion de femmes\n(en %)1, 2",
        (13, 1): 2024.0, (13, 2): 619.0, (13, 3): 4.2, (13, 4): 44.0,
        (14, 1): "1. Y compris retraite progressive.",
    }
    assert module.lire_cumul(cumul) == {
        "2024": {"cumulants_milliers": 619.0, "part_retraites_pct": 4.2, "part_femmes_pct": 44.0}}
    progressive = {
        (1, 2): "Tableau 2. Effectifs de bénéficiaires de la retraite progressive, en 2024",
        (3, 3): "Effectifs", (3, 9): "Part parmi les retraités de l'année ayant entre 60 et 69 ans (en %)",
        (3, 12): "Âge moyen (en années)",
        (4, 3): "Ensemble", (4, 6): "Femmes", (4, 7): "Hommes", (4, 8): "Part des\nfemmes\n(en %)",
        (5, 3): 2015.0, (5, 4): 2023.0, (5, 5): 2024.0,
        (6, 2): "Régime général", (6, 3): 5210.0, (6, 4): 26820.0, (6, 5): 31370.0, (6, 6): 20860.0,
        (6, 7): 10510.0, (6, 8): 67.0, (6, 9): 5.0, (6, 12): 62.2,
        (8, 2): "FPE civils", (8, 4): "nd", (8, 5): 5990.0, (8, 6): 3940.0, (8, 7): 2040.0,
        (8, 8): 66.0, (8, 9): 13.7, (8, 12): 62.5,
        (10, 2): "Ensemble", (10, 3): 5750.0, (10, 4): 27650.0, (10, 5): 42440.0, (10, 6): 28660.0,
        (10, 7): 13780.0, (10, 8): 68.0, (10, 9): 5.5, (10, 12): 62.3,
    }
    assert module.lire_retraite_progressive(progressive) == {
        "regime_general": {"2015": {"beneficiaires": 5210.0}, "2023": {"beneficiaires": 26820.0},
                           "2024": {"beneficiaires": 31370.0, "femmes": 20860.0, "hommes": 10510.0,
                                    "part_femmes_pct": 67.0, "part_retraites_60_69_pct": 5.0,
                                    "age_moyen": 62.2}},
        "fonction_publique_etat_civile": {
            "2024": {"beneficiaires": 5990.0, "femmes": 3940.0, "hommes": 2040.0,
                     "part_femmes_pct": 66.0, "part_retraites_60_69_pct": 13.7, "age_moyen": 62.5}},
        "ensemble": {"2015": {"beneficiaires": 5750.0}, "2023": {"beneficiaires": 27650.0},
                     "2024": {"beneficiaires": 42440.0, "femmes": 28660.0, "hommes": 13780.0,
                              "part_femmes_pct": 68.0, "part_retraites_60_69_pct": 5.5,
                              "age_moyen": 62.3}},
    }


def test_l_invalidite_se_lit_par_regime_et_par_annee():
    """Les feuilles de la fiche 25, réduites à l'ensemble et à un régime : une
    virgule décimale écrite en texte (« 54,5 ») est un nombre, « <1 » ou
    « - » ne le sont pas."""
    module = _classeurs()
    regimes = {(4, 1): "Régimes dans le champ de l’invalidité retenu par la Drees1",
               (5, 1): "Régime général (CNAM)", (8, 1): "MSA non-salariés"}
    beneficiaires = {**regimes, (1, 1): "Tableau 1. Bénéficiaires d’une pension d’invalidité, fin 2024",
                     (3, 2): "Effectifs\n(en milliers)", (3, 3): "Âge moyen", (3, 4): "Part \ndes femmes (en %)",
                     (4, 2): 843.4, (4, 3): 53.1, (4, 4): 56.0, (5, 2): 718.5, (5, 3): 53.5, (5, 4): 57.0,
                     (8, 2): 8.9, (8, 3): "56,1", (8, 4): 39.0}
    nouveaux = {**regimes, (1, 1): "Tableau 2. Nouveaux bénéficiaires d’une pension d’invalidité, en 2024",
                (4, 2): "Effectifs\n(en milliers)", (5, 2): 105.8, (6, 2): 90.6}
    nouveaux = {(ligne + 1 if ligne >= 4 and colonne == 1 else ligne, colonne): valeur
                for (ligne, colonne), valeur in nouveaux.items()}
    montants = {**regimes, (1, 1): "Tableau 3. Montant mensuel des pensions d’invalidité, fin 2024",
                (3, 2): "Pension d’invalidité\nde droit direct", (4, 2): 900.0, (5, 2): 909.8423,
                (8, 2): 580.0}
    depenses = {**regimes, (1, 1): "Tableau 4. Dépenses de pensions d’invalidité, fin 2024",
                (3, 6): "Total des pensions de droit direct", (3, 8): "Total",
                (4, 6): 9100.0, (4, 8): 9110.0, (5, 8): 7820.0, (8, 8): "<10"}
    evolution = {(1, 1): "Graphique 1. Évolution du nombre de bénéficiaires d’une pension d’invalidité",
                 (2, 2): "Effectifs de bénéficiaires\nd'une pension d'invalidité\nde droit direct \n(en milliers)\n",
                 (2, 3): "Pension d'invalidité de droit direct moyenne \n(en euros constants de 2024)",
                 (3, 1): 2015.0, (3, 2): 780.0, (3, 3): 903.291, (12, 1): 2024.0, (12, 2): 843.4,
                 (12, 3): 898.2425}
    lu = module.lire_invalidite(beneficiaires, nouveaux, montants, depenses, evolution)
    assert lu["2024"]["ensemble"] == {"beneficiaires_milliers": 843.4, "age_moyen": 53.1,
                                      "part_femmes_pct": 56.0, "nouveaux_milliers": 105.8,
                                      "montant_mensuel_euros": 900.0, "depenses_meur": 9110.0,
                                      "pension_moyenne_euros_2024": 898.24}
    assert lu["2024"]["msa_exploitants"] == {"beneficiaires_milliers": 8.9, "age_moyen": 56.1,
                                             "part_femmes_pct": 39.0, "montant_mensuel_euros": 580.0}
    # Le tableau 3 affiche ses montants à l'euro, et en garde un, 939,84, non arrondi.
    assert lu["2024"]["regime_general"]["montant_mensuel_euros"] == 910.0
    assert lu["2015"]["ensemble"] == {"beneficiaires_milliers": 780.0,
                                      "pension_moyenne_euros_2024": 903.29}


MACRO = RACINE / "data" / "reference" / "macro"


def test_l_age_conjoncturel_de_2023_et_2024_vient_du_panorama():
    """Fiche 15, page 138 : « Fin 2024, l'âge moyen conjoncturel de départ à
    la retraite s'élève à 62 ans et 11 mois » ; la feuille « F15_Graphique 1 »
    le chiffre, 62,95 ans, 63,29 pour les femmes, 62,59 pour les hommes, et
    62,75, 63,08 et 62,37 en 2023. Le jeu du portail de données, que le
    fichier certifie, s'arrête à 2022 : le panorama apporte les deux années
    qui suivent, en source d'appoint, au même niveau."""
    lignes = _lire(MACRO / "age_conjoncturel_depart.csv")
    ages = {(int(l["annee"]), l["sexe"]): float(l["age"]) for l in lignes}
    assert {(2023, "F"): 63.08, (2023, "H"): 62.37, (2023, "ensemble"): 62.75,
            (2024, "F"): 63.29, (2024, "H"): 62.59, (2024, "ensemble"): 62.95} == {
        cle: ages[cle] for cle in ages if cle[0] >= 2023}
    annees, mois = divmod(ages[(2024, "ensemble")] * 12, 12)
    assert (annees, int(mois)) == (62, 11)
    assert all(l["fiabilite"] == "certifiee" for l in lignes)


def test_le_cumul_emploi_retraite_et_la_retraite_progressive_viennent_du_panorama():
    """Fiche 22, tableau 1 (page 194) : les cumulants de 2014 à 2024, en
    milliers, 4,2 % des retraités et 44 % de femmes en 2024 ; tableau 2
    (page 195) : « fin 2024, environ 42 400 personnes » en retraite
    progressive, 31 370 au régime général, 5 210 et 26 820 en 2015 et 2023."""
    lignes = _lire(MACRO / "cumul_emploi_retraite.csv")
    valeurs = {(int(l["annee"]), l["dispositif"], l["regime"], l["indicateur"]): float(l["valeur"])
               for l in lignes}
    cumulants = {annee: v for (annee, dispositif, _, indicateur), v in valeurs.items()
                 if dispositif == "cumul" and indicateur == "cumulants_milliers"}
    assert cumulants == {2014: 456, 2015: 462, 2016: 452, 2017: 450, 2018: 466, 2019: 502,
                         2020: 487, 2021: 506, 2022: 543, 2023: 607, 2024: 619}
    assert valeurs[(2024, "cumul", "tous_regimes", "part_retraites_pct")] == 4.2
    assert valeurs[(2024, "cumul", "tous_regimes", "part_femmes_pct")] == 44
    progressive = {(annee, regime, indicateur): v
                   for (annee, dispositif, regime, indicateur), v in valeurs.items()
                   if dispositif == "retraite_progressive"}
    assert progressive[(2024, "ensemble", "beneficiaires")] == 42_440
    assert progressive[(2024, "ensemble", "femmes")] + progressive[(2024, "ensemble", "hommes")] == 42_440
    assert [progressive[(annee, "regime_general", "beneficiaires")]
            for annee in (2015, 2023, 2024)] == [5_210, 26_820, 31_370]
    assert progressive[(2024, "regime_general", "age_moyen")] == 62.2
    # L'enquête Emploi est un sondage : le cumul n'est que ``haute`` ; l'EACR
    # compte les bénéficiaires de la retraite progressive. Les autres années
    # du régime général, que la DREES reprend du recueil de la Cnav, sont
    # ``haute`` aussi (étape 6, ``tests/test_drees_panorama_series.py``).
    assert {(l["dispositif"], l["fiabilite"]) for l in lignes} == {
        ("cumul", "haute"), ("retraite_progressive", "certifiee"),
        ("retraite_progressive", "haute")}
    assert {l["regime"] for l in lignes
            if (l["dispositif"], l["fiabilite"]) == ("retraite_progressive", "haute")} == {
        "regime_general"}


def test_les_pensions_d_invalidite_de_2024_viennent_du_panorama():
    """Fiche 25, page 212 : « Fin 2024, 843 400 personnes bénéficient d'une
    pension d'invalidité de droit direct […]. Parmi elles, 106 000 sont de
    nouveaux bénéficiaires » ; tableau 1 (page 213), 718 500 au régime
    général, 53,1 ans en moyenne, 56 % de femmes ; tableau 3 (page 216),
    900 euros bruts par mois ; tableau 4 (page 217), 9 110 millions d'euros
    de dépense annualisée."""
    lignes = _lire(MACRO / "pensions_invalidite.csv")
    valeurs = {(int(l["annee"]), l["regime"], l["indicateur"]): float(l["valeur"]) for l in lignes}
    ensemble = {indicateur: v for (annee, regime, indicateur), v in valeurs.items()
                if (annee, regime) == (2024, "ensemble")}
    assert ensemble["beneficiaires_milliers"] == 843.4
    assert round(ensemble["nouveaux_milliers"]) == 106
    assert ensemble["age_moyen"] == 53.1 and ensemble["part_femmes_pct"] == 56
    assert ensemble["montant_mensuel_euros"] == 900
    assert ensemble["depenses_meur"] == 9_110
    assert valeurs[(2024, "regime_general", "beneficiaires_milliers")] == 718.5
    assert {annee for annee, _, _ in valeurs} == set(range(2015, 2025))
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}


def test_les_beneficiaires_de_2022_sont_ceux_des_tables_de_l_eacr():
    """Fiche 25, graphique 1 (page 213) : 842 300 bénéficiaires fin 2022. Les
    caisses de la table I de l'EACR, que le dépôt lit pour 2022
    (``tests/temoins/pensionnes_de_2022.json``), en font 842 298 : le champ
    de la DREES est le leur, sans la SNCF ni la RATP."""
    temoin = json.loads((RACINE / "tests" / "temoins" / "pensionnes_de_2022.json")
                        .read_text(encoding="utf-8"))
    somme = sum(caisse["total"] for caisse in temoin["invalidite"]["caisses"].values())
    assert somme / 1000 == pytest.approx(842.3, abs=0.05)
    lignes = _lire(MACRO / "pensions_invalidite.csv")
    assert {float(l["valeur"]) for l in lignes
            if (l["annee"], l["regime"], l["indicateur"]) == ("2022", "ensemble",
                                                                "beneficiaires_milliers")} == {842.3}


def _verificateur():
    chemin = RACINE / "scripts" / "verifier_donnees.py"
    specification = importlib.util.spec_from_file_location("verifier_donnees_panorama", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["verifier_donnees_panorama"] = module  # ses dataclasses s'y cherchent
    specification.loader.exec_module(module)
    return module


def test_le_panorama_ne_prend_le_relais_du_portail_qu_apres_sa_derniere_annee(monkeypatch):
    """L'âge conjoncturel a deux sources, le jeu du portail et le panorama :
    une année n'en a jamais deux. Le panorama ne donne que les années qui
    suivent la dernière du portail — 2022 s'il n'est pas là —, et plus rien
    quand le portail les a."""
    verificateur = _verificateur()
    panorama = {"age_conjoncturel": {str(a): {"F": 63.0, "H": 62.0, "ensemble": 62.5}
                                     for a in range(2004, 2025)}}
    monkeypatch.setattr(verificateur, "_panorama_2026", lambda: panorama)

    def portail(derniere):
        return lambda: {(str(a), s): 62.0 for a in range(2004, derniere + 1)
                        for s in ("F", "H", "ensemble")}

    monkeypatch.setattr(verificateur, "source_age_conjoncturel", portail(2022))
    assert sorted(verificateur.source_age_conjoncturel_panorama()) == [
        (a, s) for a in ("2023", "2024") for s in ("F", "H", "ensemble")]
    monkeypatch.setattr(verificateur, "source_age_conjoncturel", portail(2024))
    assert verificateur.source_age_conjoncturel_panorama() == {}

    def absent():
        raise verificateur.SourceAbsente("le jeu du portail")

    monkeypatch.setattr(verificateur, "source_age_conjoncturel", absent)
    assert {a for a, _ in verificateur.source_age_conjoncturel_panorama()} == {"2023", "2024"}


#: Fiche 8, feuille « F08_Graphique 1 » : la part des nouveaux retraités dont
#: la pension a été portée à un minimum, en %, de 2020 à 2024 (2024
#: provisoire).
PORTES_AU_MINIMUM = {
    "cnav": {2020: 17.8, 2021: 17.5, 2022: 18.3, 2023: 17.9, 2024: 17.4},
    "msa_salaries": {2020: 27.3, 2021: 25.1, 2022: 28.6, 2023: 33.1, 2024: 35.6},
}


def test_la_part_des_nouveaux_retraites_au_minimum_est_celle_de_l_eacr():
    """Le graphique 1 de la fiche 8 (page 83) : 17 % au régime général en
    2024. Le dépôt la certifie de la feuille E-Minima de l'EACR, rapportée aux
    liquidants du cadrage (``minimum_contributif_liquidants.csv``) : les mêmes
    parts au dixième, de 2020 à 2024. Avant, le panorama les dit de 0,2 à
    0,8 point plus hautes de 2012 à 2017, et de 1,1 point au régime général
    en 2019 : un autre compte, que la note de l'étape laisse à l'étape 4."""
    lignes = _lire(RACINE / "data" / "reference" / "regimes" / "minimum_contributif_liquidants.csv")
    parts = {(l["caisse"], int(l["annee"])): float(l["part"]) for l in lignes
             if l["sexe"] == "ensemble"}
    for caisse, serie in PORTES_AU_MINIMUM.items():
        for annee, part in serie.items():
            assert parts[(caisse, annee)] == pytest.approx(part, abs=0.051), (caisse, annee)


def test_la_pension_moyenne_du_depot_est_celle_du_panorama_jusqu_en_2022():
    """Fiche 5, feuille « F05_Tableau 1 compl_bis » : la pension moyenne des
    retraités résidant en France ou à l'étranger, le champ de
    ``pensions_brutes_nettes.csv`` (le tableau 1 imprimé, page 55, est celui
    des seuls résidents en France). Fin 2022, 1 565 euros bruts de droit
    direct, 1 457 nets, 1 719 et 1 602 toutes pensions : les montants que le
    dépôt certifie du tableau 2.1-a, comme ceux de 2008 à 2021. Le panorama
    chiffre aussi 2023 et 2024, que le fichier n'a pas : les y porter attend
    le propriétaire (note de l'étape 2)."""
    lignes = _lire(MACRO / "pensions_brutes_nettes.csv")
    valeurs = {(int(l["annee"]), l["indicateur"]): float(l["valeur"]) for l in lignes}
    assert {indicateur: v for (annee, indicateur), v in valeurs.items() if annee == 2022} == {
        "brute_directe": 1565, "nette_directe": 1457, "brute_totale": 1719, "nette_totale": 1602}
