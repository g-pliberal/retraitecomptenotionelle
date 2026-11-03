"""Les séries des classeurs du panorama de la DREES, édition 2026, à leur place.

L'action 178, étape 6 : les séries des graphiques et des tableaux que le PDF
ne chiffre pas, lues dans le « fichier Excel associé » à chaque fiche — le
membre ``fiche_NN.xlsx`` de l'archive ``drees_panorama_retraites_2026_classeurs``
— par ``scripts/fetch/drees_panorama_classeurs.py``, puis certifiées dans
``data/reference/`` par ``scripts/verifier_donnees.py``, chacune à la place
que le suivi (``data/reference/drees_panorama_2026.yaml``) lui donne.

Deux sortes de tests. Les premiers lisent une feuille réduite à quelques
cases, telles que le classeur les écrit, et disent comment le lecteur la lit :
par ses libellés, un libellé qui manque arrêtant la lecture. Les seconds
lisent le fichier de référence, et leurs valeurs attendues viennent de la
source : le PDF, à la page imprimée citée, ou le classeur, à la feuille citée.
Quand ``data/brut/`` porte l'archive, un dernier groupe recoupe les séries
entre elles, à la source.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
MACRO = RACINE / "data" / "reference" / "macro"
ARCHIVE = RACINE / "data" / "brut" / "drees_panorama_retraites_2026_classeurs.zip"


def _lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def _classeurs():
    chemin = RACINE / "scripts" / "fetch" / "drees_panorama_classeurs.py"
    specification = importlib.util.spec_from_file_location("drees_panorama_classeurs", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["drees_panorama_classeurs"] = module
    specification.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# La retraite progressive au régime général depuis 1989 (fiche 22, graphique 1)
# ---------------------------------------------------------------------------

def test_la_retraite_progressive_de_la_cnav_se_lit_annee_par_annee():
    """La feuille « F22_Graphique1 », réduite à deux années : une ligne par
    année, sous l'en-tête « Effectifs » ; sans lui, la lecture s'arrête."""
    module = _classeurs()
    grille = {
        (1, 1): " Graphique 1.  Évolution des effectifs d’assurés en retraite progressive "
                "au régime général",
        (3, 1): "Année", (3, 2): "Effectifs",
        (4, 1): 1989.0, (4, 2): 660.0, (39, 1): 2024.0, (39, 2): 31370.0,
        (41, 1): "Champ > Retraites progressives en cours de paiement, par année. "
                 "Source > CNAV, Recueil statistique.",
    }
    assert module.lire_retraite_progressive_cnav(grille) == {"1989": 660.0, "2024": 31370.0}
    del grille[(3, 2)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_retraite_progressive_cnav(grille)


def test_la_retraite_progressive_du_regime_general_remonte_a_1989():
    """Fiche 22, graphique 1 (page 196) : le PDF n'en chiffre que deux
    points, 3 060 assurés en 2014 et 31 370 en 2024 ; le classeur donne
    chaque année depuis 1989, 660 assurés, et 530 en 2006, au plus bas avant
    l'assouplissement du 1er juillet 2006 (encadré 1). Les trois années du
    tableau 2, de l'EACR, gardent leur source ; les autres viennent du recueil
    de la Cnav, que la DREES reprend : ``haute``, comme une transcription."""
    lignes = [l for l in _lire(MACRO / "cumul_emploi_retraite.csv")
              if (l["dispositif"], l["regime"], l["indicateur"])
              == ("retraite_progressive", "regime_general", "beneficiaires")]
    serie = {int(l["annee"]): float(l["valeur"]) for l in lignes}
    assert sorted(serie) == list(range(1989, 2025))
    assert (serie[1989], serie[2006], serie[2014], serie[2024]) == (660, 530, 3_060, 31_370)
    assert {int(l["annee"]): l["fiabilite"] for l in lignes if l["fiabilite"] == "certifiee"} == {
        2015: "certifiee", 2023: "certifiee", 2024: "certifiee"}
    assert {l["fiabilite"] for l in lignes if int(l["annee"]) not in (2015, 2023, 2024)} == {
        "haute"}


# ---------------------------------------------------------------------------
# Les pensions d'invalidité par âge (fiche 25, graphique 2 et son complément)
# ---------------------------------------------------------------------------

def _invalidite_par_age():
    graphique = {
        (1, 1): "Graphique 2. Nombre et part des bénéficiaires d’une pension d’invalidité de "
                "droit direct dans la population, par âge, en 2024",
        (2, 1): "Âge (en années)", (2, 2): "Bénéficiaires d'une pension d'invalidité de droit direct",
        (2, 4): "Population française",
        (3, 2): "Nombre de bénéficiaires  (en milliers)", (3, 3): "Part dans la population (en %)",
        (4, 1): 20.0, (4, 2): 20.0, (4, 3): 0.0, (4, 4): 798385.0,
        (44, 1): 60.0, (44, 2): 76720.0, (44, 3): 9.4, (44, 4): 816000.0,
        (54, 1): 70.0, (54, 2): 0.0, (54, 3): 0.0, (54, 4): 753143.0,
        (55, 1): "Note > Le champ des pensions d’invalidité retenu correspond à la convention Drees",
    }
    complement = {
        (1, 1): "Graphique 2 complémentaire. Évolution du nombre de bénéficiaires de pensions "
                "d'invalidité par âge et par sexe",
        (3, 1): "Âge  (en années)", (3, 2): "Femmes", (3, 13): "Hommes",
        (4, 2): 2014.0, (4, 12): 2024.0, (4, 13): 2014.0, (4, 23): 2024.0,
        (5, 1): 20.0, (5, 2): 0.0, (5, 12): 10.0, (5, 13): 20.0, (5, 23): 20.0,
        (52, 1): 67.0, (52, 12): 90.0, (52, 23): 60.0,
        (54, 1): 69.0,
        (56, 1): "Note > Le champ des pensions d’invalidité retenu correspond à la convention Drees",
    }
    return graphique, complement


def test_l_invalidite_par_age_se_lit_par_annee_par_sexe_et_par_age():
    """Les feuilles « F25_Graphique 2 » et « F25_Graphique 2 compl », réduites
    à quelques âges : le graphique, l'ensemble de 2024 ; son complément, les
    femmes et les hommes, une colonne par année sous l'en-tête de leur sexe.
    Une case vide n'est pas un zéro ; un zéro écrit en est un."""
    module = _classeurs()
    graphique, complement = _invalidite_par_age()
    assert module.lire_invalidite_par_age(graphique, complement) == {
        "2014": {"F": {"20": 0.0}, "H": {"20": 20.0}},
        "2024": {"ensemble": {"20": 20.0, "60": 76720.0, "70": 0.0},
                 "F": {"20": 10.0, "67": 90.0}, "H": {"20": 20.0, "67": 60.0}},
    }


def test_l_invalidite_par_age_refuse_une_feuille_sans_ses_libelles():
    """Sans l'en-tête « Hommes », la colonne d'une année ne dit plus son sexe ;
    sans « Nombre de bénéficiaires », le graphique ne dit plus où lire."""
    module = _classeurs()
    graphique, complement = _invalidite_par_age()
    del complement[(3, 13)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_invalidite_par_age(graphique, complement)
    graphique, complement = _invalidite_par_age()
    del graphique[(3, 2)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_invalidite_par_age(graphique, complement)


def test_les_pensions_d_invalidite_par_age_viennent_du_panorama():
    """Fiche 25, page 214 : « Fin 2024, 9 540 d'entre elles ont 40 ans,
    26 000 ont 50 ans et 76 720 ont 60 ans (graphique 2). » La feuille porte
    des personnes, quoi qu'en dise son en-tête (« en milliers ») : ses âges
    font 843 430 bénéficiaires, les 843 400 du tableau 1 (page 213). Le
    complément, par sexe, de 2014 à 2024, arrondi à la dizaine : 843 460 en
    2024, dont 56 % de femmes, la part du tableau 1."""
    lignes = _lire(MACRO / "pensions_invalidite_age.csv")
    valeurs = {(int(l["annee"]), l["sexe"], int(l["age"])): float(l["beneficiaires"])
               for l in lignes}
    ensemble = {age: v for (annee, sexe, age), v in valeurs.items()
                if (annee, sexe) == (2024, "ensemble")}
    assert (ensemble[40], ensemble[50], ensemble[60]) == (9_540, 26_000, 76_720)
    assert sorted(ensemble) == list(range(20, 71))
    assert sum(ensemble.values()) == 843_430
    femmes = sum(v for (annee, sexe, _), v in valeurs.items() if (annee, sexe) == (2024, "F"))
    hommes = sum(v for (annee, sexe, _), v in valeurs.items() if (annee, sexe) == (2024, "H"))
    assert (femmes, hommes) == (472_050, 371_410)
    assert round(100 * femmes / (femmes + hommes)) == 56
    assert {annee for annee, sexe, _ in valeurs if sexe != "ensemble"} == set(range(2014, 2025))
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}


# ---------------------------------------------------------------------------
# Le minimum vieillesse par régime, fin 2024, et depuis 1960 (fiche 27)
# ---------------------------------------------------------------------------

def _minimum_vieillesse_regimes():
    return {
        (1, 1): "Tableau 1. Nombre d’allocataires du minimum vieillesse et de l'allocation "
                "supplémentaire d'invalidité, selon le régime de versement, fin 2024",
        (3, 3): "Toutes allocations dites de premier étage1 permettant d’atteindre l’AVTS",
        (3, 4): "Allocations permettant d’atteindre le seuil du minimum vieillesse",
        (3, 9): "Allocation supplémentaire d'invalidité (art. L. 815-24)",
        (4, 4): "ASV (ancien art. L. 815-2)", (4, 5): "Aspa (L. 815-1)", (4, 6): "ASV et Aspa",
        (4, 7): "Évolution de l'ASV et  de l'Aspa depuis 2023 (en %)",
        (4, 8): "Part des bénéficiaires de l’ASV ou Aspa par caisse (en %)",
        (5, 1): "Régime général2", (5, 3): 75770.0, (5, 4): 81580.0, (5, 5): 571970.0,
        (5, 6): 653550.0, (5, 7): 5.02, (5, 8): 86.6244115027357, (5, 9): 60080.0,
        (6, 1): "Métropole", (6, 3): 71010.0, (6, 4): 67660.0, (6, 5): 527190.0,
        (6, 6): 594850.0, (6, 7): "-", (6, 8): "-", (6, 9): "-",
        (7, 1): "DROM3", (7, 3): 4760.0, (7, 4): 13920.0, (7, 5): 44780.0, (7, 6): 58700.0,
        (13, 1): "Cavimac (cultes)", (13, 3): "<100", (13, 4): 1120.0, (13, 5): 1090.0,
        (13, 6): 2210.0, (13, 7): -9.2, (13, 8): 0.3, (13, 9): "<100",
        (16, 1): "SNCF", (16, 3): "0", (16, 4): "<100", (16, 8): "<0,1",
        (23, 1): "Total  ", (23, 3): 93280.0, (23, 4): 101990.0, (23, 5): 652470.0,
        (23, 6): 754460.0, (23, 7): 4.3, (23, 8): 100.0, (23, 9): 66940.0,
        (26, 1): "Total champ enquête Drees6", (26, 3): 91630.0, (26, 6): 753910.0,
        (28, 1): "Aspa : allocation de solidarité aux personnes âgées ; ASV : allocation "
                 "spéciale vieillesse ; AVTS : allocation aux vieux travailleurs salariés.",
    }


def test_le_minimum_vieillesse_se_lit_par_regime_et_par_territoire():
    """La feuille « F27_Tableau 1 », réduite à quelques lignes : un régime par
    ligne, ses lignes « Métropole » et « DROM » sous lui ; les évolutions et
    les parts, que les effectifs donnent ou qu'une autre année porte, ne se
    lisent pas ; « <100 » n'est pas une valeur, « 0 » en est une."""
    lu = _classeurs().lire_minimum_vieillesse_regimes(_minimum_vieillesse_regimes())
    assert lu == {
        "regime_general": {
            "ensemble": {"premier_etage": 75770.0, "asv": 81580.0, "aspa": 571970.0,
                         "asv_aspa": 653550.0, "asi": 60080.0},
            "metropole": {"premier_etage": 71010.0, "asv": 67660.0, "aspa": 527190.0,
                          "asv_aspa": 594850.0},
            "drom": {"premier_etage": 4760.0, "asv": 13920.0, "aspa": 44780.0,
                     "asv_aspa": 58700.0}},
        "cavimac": {"ensemble": {"asv": 1120.0, "aspa": 1090.0, "asv_aspa": 2210.0}},
        "sncf": {"ensemble": {"premier_etage": 0.0}},
        "ensemble": {"ensemble": {"premier_etage": 93280.0, "asv": 101990.0, "aspa": 652470.0,
                                  "asv_aspa": 754460.0, "asi": 66940.0}},
        "champ_enquete_drees": {"ensemble": {"premier_etage": 91630.0, "asv_aspa": 753910.0}},
    }


def test_le_minimum_vieillesse_refuse_un_tableau_sans_son_total():
    """Sans la ligne « Total », rien ne dit plus que les régimes lus sont tous
    là ; sans l'en-tête « ASV et Aspa », la colonne de l'effectif se perd."""
    module = _classeurs()
    grille = _minimum_vieillesse_regimes()
    del grille[(23, 1)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_minimum_vieillesse_regimes(grille)
    grille = _minimum_vieillesse_regimes()
    del grille[(4, 6)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_minimum_vieillesse_regimes(grille)


def test_les_allocataires_depuis_1960_se_lisent_annee_par_annee():
    """La feuille « F27_Graphique 1 », réduite à trois années : le nombre
    d'allocataires depuis 1960, leur part parmi les 60 ans ou plus depuis
    1990, parmi les 65 ans ou plus depuis 2009 ; une case vide ne se lit pas."""
    grille = {
        (1, 1): "Graphique 1. Évolution du nombre d’allocataires de l’ASV ou de l’Aspa (depuis "
                "1960) et de leur part parmi la population âgée de 60 ans ou plus (depuis 1990)",
        (4, 1): "Années", (4, 2): "Nombre d'allocataires (en milliers)",
        (4, 3): "Part d'allocataires dans la population âgée de 60 ans ou plus (en %)",
        (4, 4): "Part d'allocataires dans la population âgée de 65 ans ou plus (en %)",
        (5, 1): 1960.0, (5, 2): 2468.9, (35, 1): 1990.0, (35, 2): 1212.9, (35, 3): 11.1,
        (69, 1): 2024.0, (69, 2): 754.0, (69, 3): 3.9, (69, 4): 4.6,
    }
    assert _classeurs().lire_minimum_vieillesse_effectifs(grille) == {
        "1960": {"allocataires_milliers": 2468.9},
        "1990": {"allocataires_milliers": 1212.9, "part_60_plus_pct": 11.1},
        "2024": {"allocataires_milliers": 754.0, "part_60_plus_pct": 3.9, "part_65_plus_pct": 4.6},
    }


def test_le_minimum_vieillesse_de_2024_par_regime_vient_du_panorama():
    """Fiche 27, page 226 : « Fin 2024, 754 460 personnes perçoivent
    l'allocation supplémentaire du minimum vieillesse (ASV) ou l'allocation
    de solidarité aux personnes âgées (Aspa) » ; page 228 : de l'allocation
    supplémentaire d'invalidité, « 66 940 personnes en bénéficient avant
    l'AOD ». Le tableau 1 (page 227) : 653 550 au régime général, dont
    58 700 dans les DROM ; les régimes font le total, l'ASV et l'Aspa aussi."""
    lignes = _lire(MACRO / "minimum_vieillesse_regimes.csv")
    valeurs = {(int(l["annee"]), l["regime"], l["territoire"], l["allocation"]):
               float(l["allocataires"]) for l in lignes}
    assert valeurs[(2024, "ensemble", "ensemble", "asv_aspa")] == 754_460
    assert valeurs[(2024, "ensemble", "ensemble", "asi")] == 66_940
    assert valeurs[(2024, "regime_general", "ensemble", "asv_aspa")] == 653_550
    assert valeurs[(2024, "regime_general", "drom", "asv_aspa")] == 58_700
    regimes = ("regime_general", "saspa", "msa_exploitants", "msa_salaries", "cavimac",
               "professions_liberales", "regimes_speciaux")
    assert sum(valeurs[(2024, r, "ensemble", "asv_aspa")] for r in regimes) == 754_460
    assert (valeurs[(2024, "ensemble", "ensemble", "asv")]
            + valeurs[(2024, "ensemble", "ensemble", "aspa")]) == 754_460
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}


def test_les_allocataires_du_minimum_vieillesse_remontent_a_1960():
    """Fiche 27, graphique 1 (page 229), dont le PDF n'imprime que quelques
    points : 2 469 milliers d'allocataires en 1960, 2 210 en 1970, 1 754 en
    1980, 1 213 en 1990, 766 en 2000, 576 en 2010 et 754 en 2024 ; 11,1 % des
    60 ans ou plus en 1990, 6,2 % en 2000, 3,9 % en 2010 et en 2024 ; 4,6 %
    des 65 ans ou plus en 2024. Le classeur donne chaque année."""
    lignes = _lire(MACRO / "minimum_vieillesse_effectifs.csv")
    valeurs = {(int(l["annee"]), l["indicateur"]): float(l["valeur"]) for l in lignes}
    allocataires = {annee: v for (annee, indicateur), v in valeurs.items()
                    if indicateur == "allocataires_milliers"}
    assert sorted(allocataires) == list(range(1960, 2025))
    assert [round(allocataires[annee]) for annee in (1960, 1970, 1980, 1990, 2000, 2010, 2024)] == [
        2_469, 2_210, 1_754, 1_213, 766, 576, 754]
    assert [valeurs[(annee, "part_60_plus_pct")] for annee in (1990, 2000, 2010, 2024)] == [
        11.1, 6.2, 3.9, 3.9]
    assert valeurs[(2024, "part_65_plus_pct")] == 4.6
    assert min(annee for annee, indicateur in valeurs if indicateur == "part_60_plus_pct") == 1990
    assert min(annee for annee, indicateur in valeurs if indicateur == "part_65_plus_pct") == 2009
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}


# ---------------------------------------------------------------------------
# À la source : les séries recoupées entre elles, quand l'archive est là
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def lu():
    if not ARCHIVE.is_file():
        pytest.skip("l'archive des classeurs n'est pas dans data/brut/ : "
                    "python scripts/fetch/source_locale.py --recuperer")
    module = _classeurs()
    return module.lire(ARCHIVE, module._jeu())


def test_la_serie_de_la_cnav_redonne_les_annees_du_tableau_2(lu):
    """Fiche 22 : le graphique 1, du recueil de la Cnav, et le tableau 2, de
    l'EACR, disent les mêmes effectifs du régime général en 2015, 2023 et
    2024 ; d'où une seule source par année, sans écart à trancher."""
    cnav = lu["retraite_progressive_cnav"]
    eacr = lu["retraite_progressive"]["regime_general"]
    assert {annee: cnav[annee] for annee in eacr} == {
        annee: grandeurs["beneficiaires"] for annee, grandeurs in eacr.items()}


def test_l_invalidite_par_age_redonne_le_total_du_tableau_1(lu):
    """Fiche 25 : les âges du graphique 2 font l'effectif de fin 2024 du
    tableau 1, au millier près ; les sexes du complément, à la dizaine
    d'arrondi près de chaque case."""
    par_age = lu["invalidite_par_age"]["2024"]
    total = lu["invalidite"]["2024"]["ensemble"]["beneficiaires_milliers"]
    assert sum(par_age["ensemble"].values()) / 1000 == pytest.approx(total, abs=0.05)
    sexes = sum(sum(par_age[sexe].values()) for sexe in ("F", "H"))
    assert abs(sexes - sum(par_age["ensemble"].values())) <= 10 * len(par_age["ensemble"])


def test_le_graphique_du_minimum_vieillesse_arrondit_le_total_du_tableau(lu):
    """Fiche 27 : le graphique 1 donne 754 milliers d'allocataires fin 2024,
    les 754 460 du tableau 1 arrondis au millier."""
    total = lu["minimum_vieillesse_regimes"]["2024"]["ensemble"]["ensemble"]["asv_aspa"]
    assert lu["minimum_vieillesse_effectifs"]["2024"]["allocataires_milliers"] == round(total / 1000)
