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
# Le profil des cumulants (fiche 23)
# ---------------------------------------------------------------------------

ENTETES_AGE = ("Effectifs de cumulants", "Part parmi la population entière (en %)",
               "Part parmi les retraités (en %)", "Part parmi les personnes en emploi (en %)",
               "Répartition par âge des cumulants (en %)", "Proportion de femmes (en %)")


def _bloc_par_age(grille, ligne, annee, lignes):
    """Un bloc annuel de « F23_Tableau 1 compl. » : la France métropolitaine
    à gauche, la France hors Mayotte à droite, sous l'année et les en-têtes."""
    grille.update({(ligne, 2): annee, (ligne, 10): annee})
    for decalage, entete in enumerate(ENTETES_AGE):
        grille[(ligne + 1, 2 + decalage)] = grille[(ligne + 1, 10 + decalage)] = entete
    grille.update({(ligne + 2, 1): "France métropolitaine", (ligne + 2, 9): "France (hors Mayotte)"})
    for rang, (libelle, metropole, france) in enumerate(lignes):
        grille[(ligne + 3 + rang, 1)] = grille[(ligne + 3 + rang, 9)] = libelle
        for decalage, (gauche, droite) in enumerate(zip(metropole, france)):
            grille[(ligne + 3 + rang, 2 + decalage)] = gauche
            grille[(ligne + 3 + rang, 10 + decalage)] = droite


def test_le_cumul_par_age_se_lit_annee_par_annee_en_france_hors_mayotte():
    """La feuille « F23_Tableau 1 compl. », réduite à deux années : un bloc
    par année, la France métropolitaine à gauche, la France hors Mayotte à
    droite, celle du tableau 1, seule lue. L'année de 2014 porte son renvoi en
    note, « 20141 » : 2014, et le renvoi 1."""
    grille = {(1, 1): "Tableau 1 complémentaire. Effectifs des personnes en cumul emploi-retraite, "
                      "par tranche d'âge, et proportion dans l'ensemble de la population des 55 ans "
                      "ou plus"}
    _bloc_par_age(grille, 3, "20141", [
        ("De 55 à 59 ans", (58000.0, 1.4, 18.6, 2.1, 12.8, 49.9), (59000.0, 1.4, 18.6, 2.1, 12.9, 50.1)),
        ("De 60 à 64 ans, dont :", (211000.0,) * 6, (212000.0, 5.2, 8.3, 19.6, 46.5, 47.8))])
    _bloc_par_age(grille, 14, 2024.0, [
        ("55 ans ou plus", (601000.0,) * 6, (619000.0, 2.6, 4.2, 10.7, 100.0, 44.1))])
    lu = _classeurs().lire_cumul_par_age(grille)
    assert lu == {
        ("2014", "age", "tous_regimes", "55_59", "ensemble", "cumulants"): 59000.0,
        ("2014", "age", "tous_regimes", "55_59", "ensemble", "part_population_pct"): 1.4,
        ("2014", "age", "tous_regimes", "55_59", "ensemble", "part_retraites_pct"): 18.6,
        ("2014", "age", "tous_regimes", "55_59", "ensemble", "part_emploi_pct"): 2.1,
        ("2014", "age", "tous_regimes", "55_59", "ensemble", "repartition_pct"): 12.9,
        ("2014", "age", "tous_regimes", "55_59", "ensemble", "part_femmes_pct"): 50.1,
        ("2014", "age", "tous_regimes", "60_64", "ensemble", "cumulants"): 212000.0,
        ("2014", "age", "tous_regimes", "60_64", "ensemble", "part_population_pct"): 5.2,
        ("2014", "age", "tous_regimes", "60_64", "ensemble", "part_retraites_pct"): 8.3,
        ("2014", "age", "tous_regimes", "60_64", "ensemble", "part_emploi_pct"): 19.6,
        ("2014", "age", "tous_regimes", "60_64", "ensemble", "repartition_pct"): 46.5,
        ("2014", "age", "tous_regimes", "60_64", "ensemble", "part_femmes_pct"): 47.8,
        ("2024", "age", "tous_regimes", "55_plus", "ensemble", "cumulants"): 619000.0,
        ("2024", "age", "tous_regimes", "55_plus", "ensemble", "part_population_pct"): 2.6,
        ("2024", "age", "tous_regimes", "55_plus", "ensemble", "part_retraites_pct"): 4.2,
        ("2024", "age", "tous_regimes", "55_plus", "ensemble", "part_emploi_pct"): 10.7,
        ("2024", "age", "tous_regimes", "55_plus", "ensemble", "repartition_pct"): 100.0,
        ("2024", "age", "tous_regimes", "55_plus", "ensemble", "part_femmes_pct"): 44.1,
    }


def test_les_categories_et_le_temps_de_travail_se_lisent_sous_le_sexe():
    """Les feuilles « F23_Tableau 2 » et « F23_Tableau 3 », réduites à deux
    lignes : deux colonnes sous chaque sexe, la part parmi les cumulants et
    parmi les personnes en emploi non retraitées, l'apostrophe droite ou
    courbe ; « 80 % » et « 50 % », que le classeur écrit en nombres (0,8 et
    0,5), sont des durées du temps partiel."""
    module = _classeurs()
    sexes = {(3, 2): "Femmes", (3, 4): "Hommes", (3, 6): "Ensemble"}
    for colonne in (2, 4, 6):
        sexes[(4, colonne)] = "Part parmi l’ensemble des cumulants"
        sexes[(4, colonne + 1)] = "Part parmi l'ensemble des personnes en emploi et non retraitées"
    categories = {**sexes, (1, 1): "Tableau 2. Répartition par catégorie socioprofessionnelle des "
                                   "personnes ayant cumulé un emploi et une retraite, en 2024",
                  (4, 1): "Catégorie socioprofessionnelle",
                  (5, 1): "Agriculteurs exploitants", (5, 2): 1.4, (5, 3): 1.3, (5, 4): 4.0,
                  (5, 5): 4.0, (5, 6): 2.8, (5, 7): 2.6}
    assert module.lire_cumul_repartition(categories) == {
        ("2024", "csp", "tous_regimes", "agriculteurs_exploitants", sexe, indicateur): valeur
        for sexe, valeurs in (("F", (1.4, 1.3)), ("H", (4.0, 4.0)), ("ensemble", (2.8, 2.6)))
        for indicateur, valeur in zip(("part_cumulants_pct", "part_emploi_non_retraites_pct"),
                                      valeurs)}
    temps = {**sexes, (1, 1): "Tableau 3. Répartition des personnes ayant cumulé un emploi et une "
                              "retraite, selon la durée du temps de travail, en 2024",
             (4, 1): "Temps de travail", (8, 1): 0.8, (8, 2): 4.1, (8, 3): 6.0, (8, 4): 2.5,
             (8, 5): 1.6, (8, 6): 3.2, (8, 7): 3.8}
    lu = module.lire_cumul_repartition(temps)
    assert lu[("2024", "temps_travail", "tous_regimes", "80_pct", "ensemble",
               "part_cumulants_pct")] == 3.2
    assert len(lu) == 6
    del categories[(3, 4)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_cumul_repartition(categories)


def test_le_cumul_dans_un_meme_regime_se_lit_par_caisse_et_par_age():
    """Les feuilles « F23_Tableau 4 » et « F23_Graphique 1 », réduites : les
    effectifs de quatre années, la part des femmes et la part des cumulants
    par sexe de la dernière ; par âge, la part des cumulants de chaque caisse,
    en 2024, sauf la Cnav, en 2022, comme le dit la note du graphique."""
    module = _classeurs()
    tableau = {
        (1, 1): "Tableau 4. Retraités de droit direct cumulant un emploi et une retraite dans un "
                "même régime",
        (3, 2): "Nombre de personnes cumulant une pension de retraite et un revenu d'activité",
        (3, 7): "Part des femmes parmi les cumulants (en %)",
        (3, 8): "Part des cumulants au sein des retraités du régime, hors nouveaux retraités de "
                "l’année2 (en %)",
        (4, 2): "Effectifs (en milliers)", (4, 6): "Évolution (en %)", (4, 7): 2024.0,
        (4, 8): "Femmes", (4, 9): "Hommes", (4, 10): "Ensemble",
        (5, 2): 2013.0, (5, 3): 2022.0, (5, 4): 2023.0, (5, 5): 2024.0, (5, 6): "2023-2024",
        (5, 8): 2024.0,
        (6, 1): "Régime général1", (6, 2): 351.1, (6, 3): 425.4, (6, 4): "nd", (6, 5): "nd",
        (6, 6): "nd", (6, 7): "nd", (6, 8): "nd", (6, 9): "nd", (6, 10): "nd",
        (7, 1): "CNAVPL", (7, 2): "nd", (7, 3): 37.9, (7, 4): 46.8, (7, 5): 46.8, (7, 6): 0.0,
        (7, 7): 33.0, (7, 8): 8.3, (7, 9): 11.5, (7, 10): 10.2,
    }
    graphique = {
        (1, 1): "Graphique 1. Part des retraités de droit direct cumulant un emploi et une "
                "retraite au sein du même régime, par sexe et par âge, hors nouveaux retraités "
                "de l’année",
        (3, 1): "Âge (en années)", (3, 2): "CNAV1", (3, 3): "CNAVPL", (3, 4): "MSA salariés",
        (3, 5): "MSA non-salariés",
        (4, 1): 61.0, (4, 2): 8.4, (4, 3): 24.7, (4, 4): 22.0, (4, 5): 20.9,
        (25, 1): "1. Le régime général intègre les indépendants de l’ex-SSI depuis 2020. Les "
                 "données concernent 2024, sauf celles de la CNAV, qui portent sur 2022, "
                 "dernière année connue.",
    }
    cle = ("meme_regime",)
    assert module.lire_cumul_meme_regime(tableau, graphique) == {
        ("2013", *cle, "regime_general", "ensemble", "ensemble", "cumulants_milliers"): 351.1,
        ("2022", *cle, "regime_general", "ensemble", "ensemble", "cumulants_milliers"): 425.4,
        ("2022", *cle, "cnavpl", "ensemble", "ensemble", "cumulants_milliers"): 37.9,
        ("2023", *cle, "cnavpl", "ensemble", "ensemble", "cumulants_milliers"): 46.8,
        ("2024", *cle, "cnavpl", "ensemble", "ensemble", "cumulants_milliers"): 46.8,
        ("2024", *cle, "cnavpl", "ensemble", "ensemble", "part_femmes_pct"): 33.0,
        ("2024", *cle, "cnavpl", "ensemble", "F", "part_retraites_pct"): 8.3,
        ("2024", *cle, "cnavpl", "ensemble", "H", "part_retraites_pct"): 11.5,
        ("2024", *cle, "cnavpl", "ensemble", "ensemble", "part_retraites_pct"): 10.2,
        ("2022", *cle, "regime_general", "61", "ensemble", "part_retraites_pct"): 8.4,
        ("2024", *cle, "cnavpl", "61", "ensemble", "part_retraites_pct"): 24.7,
        ("2024", *cle, "msa_salaries", "61", "ensemble", "part_retraites_pct"): 22.0,
        ("2024", *cle, "msa_exploitants", "61", "ensemble", "part_retraites_pct"): 20.9,
    }
    graphique[(25, 1)] = "1. Le régime général intègre les indépendants de l’ex-SSI depuis 2020."
    with pytest.raises(module.FeuilleIllisible):
        module.lire_cumul_meme_regime(tableau, graphique)


def test_le_cumul_de_la_generation_1950_se_lit_par_regime():
    """Les feuilles « F23_Tableau 5 » et « F23_Tableau 6 », réduites : la part
    des retraités nés en 1950 qui ont cumulé, par régime de retraite (en
    colonnes) et d'emploi (en lignes) ; dans la fonction publique, par sexe,
    « ns » n'étant pas une valeur. L'année est celle où l'échantillon les voit
    vivants, que dit le champ : le 31 décembre 2020."""
    module = _classeurs()
    regimes = {
        (1, 1): "Tableau 5. Part des retraités nés en 1950 ayant cumulé un emploi et une retraite "
                "depuis leur départ à la retraite, selon le régime principal de retraite et d’emploi",
        (4, 1): "Régime d'emploi principal", (4, 2): "Régime de retraite principal",
        (5, 2): "Régime général", (5, 3): "Fonction publique1", (5, 4): "Professions libérales",
        (5, 5): "MSA, salariés et non-salariés", (5, 6): "Ensemble des retraités",
        (8, 1): "Fonction publique1", (8, 2): 0.6, (8, 3): 11.7, (8, 4): 0.2, (8, 5): 0.2, (8, 6): 2.7,
        (11, 1): "Tous régimes d'emploi confondus", (11, 2): 20.1, (11, 3): 32.0, (11, 4): 36.5,
        (11, 5): 21.7, (11, 6): 22.7,
        (13, 1): "1. FPE, CNRACL et régimes spéciaux. Champ > Retraités de droit direct d’un "
                 "régime de base, nés en 1950, vivants au 31 décembre 2020. Sources > Drees, "
                 "EIC 2020, EIR 2021.",
    }
    fonction_publique = {
        (1, 1): "Tableau 6. Part des retraités des régimes de la FPE et de la CNRACL nés en 1950 "
                "ayant cumulé un emploi et une retraite",
        (3, 2): "Femmes", (3, 3): "Hommes", (3, 4): "Ensemble",
        (5, 1): "FPE militaires1", (5, 2): "ns", (5, 3): 70.0, (5, 4): 68.0,
        (7, 1): "Fonctionnaires civils partis avant 60 ans2", (7, 2): 29.0, (7, 3): 27.0, (7, 4): 28.0,
        (10, 1): "ns : non significatif. Champ > Retraités de droit direct de la FPE et de la "
                 "CNRACL, nés en 1950, vivants au 31 décembre 2020. Sources > Drees, EIC 2020, "
                 "EIR 2021.",
    }
    cle = ("2020", "generation_1950")
    lu = module.lire_cumul_generation_1950(regimes, fonction_publique)
    assert lu == {
        **{(*cle, regime, "emploi_fonction_publique", "ensemble", "part_ayant_cumule_pct"): v
           for regime, v in (("regime_general", 0.6), ("fonction_publique", 11.7),
                             ("professions_liberales", 0.2), ("msa", 0.2), ("ensemble", 2.7))},
        **{(*cle, regime, "emploi_tous_regimes", "ensemble", "part_ayant_cumule_pct"): v
           for regime, v in (("regime_general", 20.1), ("fonction_publique", 32.0),
                             ("professions_liberales", 36.5), ("msa", 21.7), ("ensemble", 22.7))},
        (*cle, "fpe_militaires", "ensemble", "H", "part_ayant_cumule_pct"): 70.0,
        (*cle, "fpe_militaires", "ensemble", "ensemble", "part_ayant_cumule_pct"): 68.0,
        (*cle, "fonctionnaires_civils", "partis_avant_60", "F", "part_ayant_cumule_pct"): 29.0,
        (*cle, "fonctionnaires_civils", "partis_avant_60", "H", "part_ayant_cumule_pct"): 27.0,
        (*cle, "fonctionnaires_civils", "partis_avant_60", "ensemble", "part_ayant_cumule_pct"): 28.0,
    }


def _profil():
    lignes = _lire(MACRO / "cumul_emploi_retraite_profil.csv")
    return lignes, {(int(l["annee"]), l["champ"], l["regime"], l["modalite"], l["sexe"],
                     l["indicateur"]): float(l["valeur"]) for l in lignes}


def test_le_profil_des_cumulants_de_2024_vient_du_panorama():
    """Fiche 23, page 198 : « En 2024, […] 619 000 personnes âgées de 55 ans
    ou plus résidant en France déclarent exercer une activité professionnelle
    tout en percevant une pension de retraite, soit 4,2 % des retraités.
    Parmi eux, 43 % sont cadres ou indépendants » ; tableau 1 (page 201) :
    54 000 de 55 à 59 ans, 35,3 % des retraités de cet âge ; tableau 3 (page
    202) : « 70,5 % des personnes cumulant un emploi et une retraite
    travaillent à temps partiel, dont 40,1 % d'entre elles moins d'un
    mi-temps ». L'enquête Emploi est un sondage : ``haute``."""
    lignes, valeurs = _profil()
    age = ("age", "tous_regimes")
    assert valeurs[(2024, *age, "55_plus", "ensemble", "cumulants")] == 619_000
    assert valeurs[(2024, *age, "55_plus", "ensemble", "part_retraites_pct")] == 4.2
    assert valeurs[(2024, *age, "55_59", "ensemble", "cumulants")] == 54_000
    assert valeurs[(2024, *age, "55_59", "ensemble", "part_retraites_pct")] == 35.3
    assert {annee for annee, champ, *_ in valeurs if champ == "age"} == set(range(2014, 2025))
    csp = {modalite: v for (annee, champ, _, modalite, sexe, indicateur), v in valeurs.items()
           if (champ, sexe, indicateur) == ("csp", "ensemble", "part_cumulants_pct")}
    assert csp["cadres"] + csp["artisans_commercants_chefs_entreprise"] == 43.0
    temps = ("temps_travail", "tous_regimes")
    assert valeurs[(2024, *temps, "temps_partiel", "ensemble", "part_cumulants_pct")] == 70.5
    assert valeurs[(2024, *temps, "moins_mi_temps", "ensemble", "part_cumulants_pct")] == 40.1
    assert {l["fiabilite"] for l in lignes if l["champ"] in ("age", "csp", "temps_travail")} == {
        "haute"}


def test_le_cumul_dans_un_meme_regime_et_celui_de_la_generation_1950_viennent_du_panorama():
    """Fiche 23, page 204 : « 22,7 % des retraités de la génération 1950 ont
    cumulé un emploi et une retraite avant 67 ans », le tableau 5 ; le chapeau
    de la page 198 en dit 21,4 %, que rien d'autre ne porte. Le tableau 6
    (page 205) : « 25 % des femmes pensionnées de la CNRACL nées en 1950 ont
    cumulé ». Le
    tableau 4 : 351 100 cumulants au régime général en 2013, 425 400 en
    2022, rien depuis ; page 204, la part des cumulants « sous de 2 % au-delà
    de 75 ans au régime général » (graphique 1, 2022). L'EACR, l'EIC et l'EIR
    sont des comptages : ``certifiee``."""
    lignes, valeurs = _profil()
    generation = ("generation_1950",)
    assert valeurs[(2020, *generation, "ensemble", "emploi_tous_regimes", "ensemble",
                    "part_ayant_cumule_pct")] == 22.7
    assert valeurs[(2020, *generation, "cnracl", "ensemble", "F", "part_ayant_cumule_pct")] == 25
    meme = ("meme_regime", "regime_general", "ensemble", "ensemble", "cumulants_milliers")
    assert {annee: v for (annee, *reste), v in valeurs.items() if tuple(reste) == meme} == {
        2013: 351.1, 2022: 425.4}
    agees = {int(modalite): v for (annee, champ, regime, modalite, _, _), v in valeurs.items()
             if (annee, champ, regime) == (2022, "meme_regime", "regime_general")
             and modalite.isdigit()}
    assert min(agees) == 61 and all(v < 2 for age, v in agees.items() if age > 75)
    assert {l["fiabilite"] for l in lignes
            if l["champ"] in ("meme_regime", "generation_1950")} == {"certifiee"}


# ---------------------------------------------------------------------------
# Aux référents : les séries des fiches 1, 3, 16 et 17
# ---------------------------------------------------------------------------

def test_le_rapport_entre_emploi_et_retraites_se_lit_par_annee():
    """La feuille « F01_Graphique 1 », réduite à deux années, dont l'une
    porte son renvoi en note (« 20181 ») : les retraités, résidant en France
    ou à l'étranger puis en France seulement, et l'emploi intérieur ; le
    rapport, que ces effectifs donnent, ne se lit pas."""
    grille = {
        (1, 1): "Graphique 1. Rapport entre les effectifs de personnes en emploi et les effectifs "
                "de retraités de droit direct, résidant en France ou à l’étranger",
        (3, 2): "Effectifs de retraités de droits directs  (en milliers)",
        (3, 4): "Emploi intérieur (en milliers)", (3, 5): "Rapport entre cotisants et retraités",
        (4, 2): "Résidant en France ou à l'étranger", (4, 3): "Résidant en France uniquement",
        (4, 5): "Résidant en France ou à l'étranger", (4, 6): "Résidant en France uniquement",
        (19, 1): "20181", (19, 2): 16496.0, (19, 3): 15346.0, (19, 4): 28327.8, (19, 5): 1.717,
        (25, 1): 2024.0, (25, 2): 17298.0, (25, 3): 16429.0, (25, 4): 30623.3, (25, 5): 1.770,
    }
    assert _classeurs().lire_rapport_emploi_retraites(grille) == {
        "2018": {"retraites_milliers": 16496.0, "retraites_france_milliers": 15346.0,
                 "emploi_interieur_milliers": 28327.8},
        "2024": {"retraites_milliers": 17298.0, "retraites_france_milliers": 16429.0,
                 "emploi_interieur_milliers": 30623.3},
    }


def test_les_series_par_generation_se_lisent_en_lignes_ou_en_colonnes():
    """Les générations se lisent en lignes (« F01_Graphique 3 », « F17_Graphique
    4 ») ou en colonnes (« F16_Graphique 5 », « F17_Graphique 3 ») ; une
    génération sans valeur, comme 1927, n'a pas de ligne."""
    module = _classeurs()
    poly = {(1, 1): "Graphique 3. Part des polypensionnés, par génération et par sexe",
            (3, 1): "Génération", (3, 2): "Femmes", (3, 3): "Hommes", (3, 4): "Ensemble",
            (4, 1): 1926.0, (4, 2): 26.8, (4, 3): 51.5, (4, 4): 39.9, (5, 1): 1927.0}
    assert module.lire_polypensionnes(poly) == {
        ("1926", "polypension", "tous_regimes", "ensemble", sexe, "part_pct"): v
        for sexe, v in (("F", 26.8), ("H", 51.5), ("ensemble", 39.9))}
    ages = {(1, 1): "Graphique 5. Répartition des retraités, selon la génération et l’âge à la "
                    "première liquidation",
            (3, 2): 1930.0, (3, 14): 1953.0, (4, 1): "Moins de 55 ans", (4, 2): 3.0, (4, 14): 3.0,
            (12, 1): "66 ans ou plus", (12, 2): 3.0, (12, 14): 11.0}
    premiere = {(1, 1): "Tableau 1. Répartition des retraités nés en 1953, selon l’âge à la "
                        "première liquidation",
                (3, 3): "Femmes", (3, 6): "Hommes", (3, 8): "Ensemble",
                (4, 2): "résidant en France", (4, 3): "résidant à l'étranger", (4, 4): "Ensemble",
                (4, 5): "résidant en France", (4, 6): "résidant à l'étranger", (4, 7): "Ensemble",
                (9, 1): "61 ans", (9, 2): 45.0, (9, 3): 29.0, (9, 4): 44.0, (9, 5): 31.0,
                (9, 6): 31.0, (9, 7): 31.0, (9, 8): 38.0,
                (15, 1): "Âge moyen à la première liquidation", (15, 4): 61.7, (15, 7): 60.9,
                (15, 8): 61.3}
    lu = module.lire_age_premiere_liquidation(premiere, ages)
    cle = ("age_premiere_liquidation", "tous_regimes")
    assert lu == {
        ("1930", *cle, "moins_55", "ensemble", "part_pct"): 3.0,
        ("1930", *cle, "66_plus", "ensemble", "part_pct"): 3.0,
        ("1953", *cle, "61", "F", "part_pct"): 44.0, ("1953", *cle, "61", "H", "part_pct"): 31.0,
        ("1953", *cle, "61", "ensemble", "part_pct"): 38.0,
        ("1953", *cle, "ensemble", "F", "age_moyen"): 61.7,
        ("1953", *cle, "ensemble", "H", "age_moyen"): 60.9,
        ("1953", *cle, "ensemble", "ensemble", "age_moyen"): 61.3,
    }


def test_le_depart_des_nes_en_1953_se_lit_par_regime_principal():
    """La feuille « F16_Tableau 2 », réduite à une ligne : l'âge moyen, avec et
    sans les départs avant l'âge d'ouverture des droits, la répartition par
    âge, dont les en-têtes sont des nombres (55, 60…) ou des textes
    (« 56-59 »), et la part parmi les retraités ; « 0,0 » est un nombre."""
    grille = {
        (1, 1): "Tableau 2. Âge de départ à la retraite et répartition des retraités nés en "
                "1953, selon le régime principal",
        (3, 2): "Âge moyen à la liquidation dans le régime principal",
        (3, 4): "Répartition par âge (en années) à la liquidation dans le régime principal (en %)",
        (3, 13): "Part parmi les retraités (en %)",
        (4, 2): "Ensemble", (4, 3): "Après neutralisation des départs avant l'AOD",
        (4, 4): "Moins de 55", (4, 5): 55.0, (4, 6): "56-59", (4, 12): "67 ou plus",
        (5, 1): "Régime général", (5, 2): 62.0, (5, 3): 62.3, (5, 4): "0,0", (5, 5): 0.1,
        (5, 6): 8.3, (5, 12): 1.1, (5, 13): 72.9,
    }
    cle = ("1953", "age_liquidation_regime_principal", "regime_general")
    assert _classeurs().lire_liquidation_regime_principal(grille) == {
        (*cle, "ensemble", "ensemble", "age_moyen"): 62.0,
        (*cle, "ensemble", "ensemble", "age_moyen_hors_departs_avant_aod"): 62.3,
        (*cle, "moins_55", "ensemble", "part_pct"): 0.0, (*cle, "55", "ensemble", "part_pct"): 0.1,
        (*cle, "56_59", "ensemble", "part_pct"): 8.3, (*cle, "67_plus", "ensemble", "part_pct"): 1.1,
        (*cle, "ensemble", "ensemble", "part_retraites_pct"): 72.9,
    }


def test_le_taux_de_liquidation_se_lit_par_motif_et_par_generation():
    """Les feuilles « F17_Graphique 1 » (les nés en 1953, par sexe ; les
    colonnes de résidence ne se lisent pas ; la génération est celle qui suit
    « née en », non l'année de l'échantillon qui clôt le titre),
    « F17_Graphique 3 » (par génération) et « F17_Graphique 4 » (la décote
    par régime)."""
    module = _classeurs()
    generation_1953 = {
        (1, 1): "Graphique 1. Répartition des retraités de la génération née en 1953, selon le "
                "taux de liquidation dans le régime de base principal et le motif d'obtention du "
                "taux plein le cas échéant, en 2020",
        (4, 2): "Femmes", (4, 3): "Hommes", (4, 4): "Retraités résidant  en France",
        (4, 5): "Retraités résidant  à l'étranger", (4, 6): "Ensemble",
        (5, 1): "Départ avec décote", (5, 2): 12.5, (5, 3): 8.7, (5, 4): 10.0, (5, 5): 31.9,
        (5, 6): 10.7,
        (12, 1): "Départ au taux plein (sans surcote) par la durée (y compris carrière longue "
                 "mais hors invalidité ou inaptitude)", (12, 6): 45.2,
    }
    par_generation = {
        (1, 1): "Graphique 3. Répartition des retraités, selon la génération et le taux de "
                "liquidation dans le régime de base principal et le motif d'obtention du taux",
        (3, 2): 1928.0, (3, 13): 1952.0,
        (12, 1): "Départ avec surcote", (12, 2): 0.2, (12, 13): 14.9,
    }
    cle = ("taux_liquidation", "tous_regimes")
    assert module.lire_taux_liquidation(generation_1953, par_generation) == {
        ("1953", *cle, "decote", "F", "part_pct"): 12.5,
        ("1953", *cle, "decote", "H", "part_pct"): 8.7,
        ("1953", *cle, "decote", "ensemble", "part_pct"): 10.7,
        ("1953", *cle, "taux_plein_duree", "ensemble", "part_pct"): 45.2,
        ("1928", *cle, "surcote", "ensemble", "part_pct"): 0.2,
        ("1952", *cle, "surcote", "ensemble", "part_pct"): 14.9,
    }
    decote = {(1, 1): "Graphique 4. Part des retraités ayant liquidé leurs droits avec une "
                      "décote, par génération",
              (3, 2): "Régime général1", (3, 5): "FPE civils", (3, 7): "Tous régimes",
              (4, 1): 1938.0, (4, 2): 7.9, (4, 7): 6.1,
              (19, 1): 1953.0, (19, 2): 11.6, (19, 5): 18.2, (19, 7): 10.7}
    surcote = {(1, 1): "Graphique 5. Part des retraités ayant liquidé leurs droits avec une "
                       "surcote, par génération",
               (3, 2): "Régime général1", (3, 5): "Tous régimes",
               (17, 1): 1953.0, (17, 2): 13.8, (17, 5): 15.8}
    assert module.lire_decote_surcote(decote, surcote) == {
        ("1938", "decote", "regime_general", "ensemble", "ensemble", "part_pct"): 7.9,
        ("1938", "decote", "tous_regimes", "ensemble", "ensemble", "part_pct"): 6.1,
        ("1953", "decote", "regime_general", "ensemble", "ensemble", "part_pct"): 11.6,
        ("1953", "decote", "fonction_publique_etat_civile", "ensemble", "ensemble",
         "part_pct"): 18.2,
        ("1953", "decote", "tous_regimes", "ensemble", "ensemble", "part_pct"): 10.7,
        ("1953", "surcote", "regime_general", "ensemble", "ensemble", "part_pct"): 13.8,
        ("1953", "surcote", "tous_regimes", "ensemble", "ensemble", "part_pct"): 15.8,
    }


def test_la_reversion_se_lit_par_annee_et_par_generation():
    """Les feuilles « F03_Graphique 2 » (les femmes de 60 ans ou plus, par
    année) et « F03_Graphique 4 » (par groupe de générations et par âge)."""
    module = _classeurs()
    femmes = {(1, 1): "Graphique 2. Part des retraitées d’une pension de droit dérivé parmi les "
                      "femmes âgées de 60 ans ou plus résidant en France",
              (3, 2): "Bénéficiaires d'une pension de droit dérivé cumulée à une pension de droit "
                      "direct", (3, 3): "Bénéficiaires  d'une pension de droit dérivé seule",
              (24, 1): 2024.0, (24, 2): 26.8, (24, 3): 3.1}
    generations = {(1, 1): "Graphique 4. Part des personnes bénéficiant d’une pension de droit "
                           "dérivé, selon l’âge et la génération",
                   (3, 1): "Génération", (3, 2): "Moins de 50 ans", (3, 5): "60 à 64 ans",
                   (4, 1): "Avant 1935", (4, 2): 1.8, (4, 5): 14.0,
                   (7, 1): "De 1946 à 1950", (7, 2): 1.1, (7, 5): 9.2}
    assert module.lire_reversion(femmes, generations) == {
        ("femmes_60_plus", "2024", "reversion_et_droit_direct", "part_pct"): 26.8,
        ("femmes_60_plus", "2024", "reversion_seule", "part_pct"): 3.1,
        ("generations", "avant_1935", "moins_50", "part_pct"): 1.8,
        ("generations", "avant_1935", "60_64", "part_pct"): 14.0,
        ("generations", "1946_1950", "moins_50", "part_pct"): 1.1,
        ("generations", "1946_1950", "60_64", "part_pct"): 9.2,
    }


def test_le_rapport_entre_emploi_et_retraites_vient_du_panorama():
    """Fiche 1, page 20 : « 1,77 actif en emploi pour un retraité en 2024,
    contre 1,78 en 2012 » ; 16,4 millions de retraités de droit direct vivent
    en France. Le graphique 1 (page 22) n'imprime pas ses effectifs, que le
    classeur donne de 2004 à 2024."""
    valeurs = {(int(l["annee"]), l["indicateur"]): float(l["valeur"])
               for l in _lire(MACRO / "rapport_emploi_retraites.csv")}
    rapport = {annee: valeurs[(annee, "emploi_interieur_milliers")]
               / valeurs[(annee, "retraites_milliers")] for annee in (2012, 2024)}
    assert (round(rapport[2012], 2), round(rapport[2024], 2)) == (1.78, 1.77)
    assert round(valeurs[(2024, "retraites_france_milliers")] / 1000, 1) == 16.4
    assert {annee for annee, _ in valeurs} == set(range(2004, 2025))


def test_les_series_par_generation_viennent_du_panorama():
    """Fiche 1, graphique 3 (page 26) : la part des polypensionnés, de la
    génération 1926 à 1957, celles d'après 1953 estimées par Ancetre
    (``haute``). Fiche 16, tableau 1 (page 150) : les nés en 1953 sont partis
    à 61,3 ans en moyenne à leur première liquidation, 38 % à 61 ans ;
    tableau 2 (page 153) : 62,0 ans au régime général, 61,4 tous régimes.
    Fiche 17, graphique 1 (page 155) : 10,7 % des nés en 1953 sont partis avec
    une décote, 14,5 % avec une surcote ; graphique 4 (page 158) : la décote
    tous régimes de 1953, la même."""
    lignes = _lire(MACRO / "retraites_generations.csv")
    valeurs = {(int(l["generation"]), l["champ"], l["regime"], l["modalite"], l["sexe"],
                l["indicateur"]): float(l["valeur"]) for l in lignes}
    poly = {generation: v for (generation, champ, _, _, sexe, _), v in valeurs.items()
            if (champ, sexe) == ("polypension", "ensemble")}
    assert min(poly) == 1926 and max(poly) == 1957 and poly[1950] == 37.5
    assert {l["fiabilite"] for l in lignes if l["champ"] == "polypension"
            and int(l["generation"]) > 1953} == {"haute"}
    assert {l["fiabilite"] for l in lignes if not (l["champ"] == "polypension"
                                                     and int(l["generation"]) > 1953)} == {
        "certifiee"}
    premiere = ("age_premiere_liquidation", "tous_regimes")
    assert valeurs[(1953, *premiere, "ensemble", "ensemble", "age_moyen")] == 61.3
    assert valeurs[(1953, *premiere, "61", "ensemble", "part_pct")] == 38
    principal = ("age_liquidation_regime_principal",)
    assert valeurs[(1953, *principal, "regime_general", "ensemble", "ensemble", "age_moyen")] == 62
    assert valeurs[(1953, *principal, "ensemble", "ensemble", "ensemble", "age_moyen")] == 61.4
    taux = ("taux_liquidation", "tous_regimes")
    assert valeurs[(1953, *taux, "decote", "ensemble", "part_pct")] == 10.7
    assert valeurs[(1953, *taux, "surcote", "ensemble", "part_pct")] == 14.5
    assert valeurs[(1953, "decote", "tous_regimes", "ensemble", "ensemble", "part_pct")] == 10.7


def test_la_reversion_vient_du_panorama():
    """Fiche 3, page 39 : « Fin 2024, 3,1 % des femmes âgées de 60 ans ou
    plus résidant en France bénéficient d'une pension de droit dérivé sans
    bénéficier d'une pension de droit direct, et 26,8 % bénéficient d'une
    pension de droit dérivé cumulée à une pension de droit direct » ; page
    40 : « Parmi les personnes vivantes en 2020 et nées avant 1935, 14 % ont
    touché une pension de réversion entre 60 et 64 ans (contre 9,2 % des
    personnes nées entre 1946 et 1950). »"""
    lignes = _lire(MACRO / "reversion_beneficiaires.csv")
    valeurs = {(l["champ"], l["periode"], l["modalite"]): float(l["part_pct"]) for l in lignes}
    assert valeurs[("femmes_60_plus", "2024", "reversion_seule")] == 3.1
    assert valeurs[("femmes_60_plus", "2024", "reversion_et_droit_direct")] == 26.8
    assert valeurs[("generations", "avant_1935", "60_64")] == 14
    assert valeurs[("generations", "1946_1950", "60_64")] == 9.2
    assert {int(periode) for champ, periode, _ in valeurs if champ == "femmes_60_plus"} == set(
        range(2004, 2025))
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


def test_le_tableau_1_est_son_complement_en_2014_et_en_2024(lu):
    """Fiche 23 : le tableau 1 (2014 et 2024, France hors Mayotte) est le
    bloc de droite de son complément, pour ces deux années ; les cumulants
    de 55 ans ou plus sont ceux de la fiche 22, en milliers."""
    with zipfile.ZipFile(ARCHIVE) as archive:
        module = _classeurs()
        tableau = module._classeur(archive, module._jeu(), "fiche_23.xlsx")["F23_Tableau 1"]
    principal = module.lire_cumul_par_age(tableau)
    profil = {tuple(cle): valeur for *cle, valeur in lu["cumul_profil"]}
    assert principal and {cle: profil[cle] for cle in principal} == principal
    assert {cle[0] for cle in principal} == {"2014", "2024"}
    for annee in ("2014", "2024"):
        assert profil[(annee, "age", "tous_regimes", "55_plus", "ensemble", "cumulants")] == (
            1000 * lu["cumul"][annee]["cumulants_milliers"])
