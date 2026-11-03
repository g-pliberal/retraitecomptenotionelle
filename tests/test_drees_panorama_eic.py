"""L'échantillon interrégimes de cotisants de 2021, du panorama de la DREES.

L'action 178, étape 3 : les fiches 12 (« Les durées d'assurance validées par
les actifs pour leur retraite ») et 21 (« La situation des assurés en fin de
carrière ») du panorama « Les retraités et les retraites », édition 2026, la
première à se servir de l'EIC de 2021 quand le dépôt lit celle de 2017. Leurs
séries sont lues dans le « fichier Excel associé » à chaque fiche par
``scripts/fetch/drees_panorama_classeurs.py``, puis certifiées par
``scripts/verifier_donnees.py`` dans ``durees_validees_actifs.csv`` et
``fins_de_carriere.csv``.

Comme pour l'étape 6 (``tests/test_drees_panorama_series.py``) : des feuilles
réduites à quelques cases, telles que le classeur les écrit, disent comment le
lecteur les lit ; les fichiers de référence sont lus à des valeurs que le PDF
imprime, à la page citée ; et, quand ``data/brut/`` porte l'archive, les
figures se recoupent entre elles, à la source.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
MACRO = RACINE / "data" / "reference" / "macro"
ARCHIVE = RACINE / "data" / "brut" / "drees_panorama_retraites_2026_classeurs.zip"


def _lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def _valeurs(nom: str) -> dict[tuple, float]:
    return {(int(l["generation"]), l["champ"], l["groupe"], l["modalite"], l["sexe"],
             l["indicateur"]): float(l["valeur"]) for l in _lire(MACRO / nom)}


def _classeurs():
    chemin = RACINE / "scripts" / "fetch" / "drees_panorama_classeurs.py"
    specification = importlib.util.spec_from_file_location("drees_panorama_classeurs", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["drees_panorama_classeurs"] = module
    specification.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Fiche 12 : les durées validées, lues dans les feuilles du classeur
# ---------------------------------------------------------------------------

def test_le_debut_de_carriere_se_lit_par_grandeur_puis_par_sexe():
    """« F12_Graphique 1 » : trois grandeurs côte à côte, chacune sur trois
    colonnes de sexe ; les trimestres à 30 ans vont aux cumuls, l'âge de la
    première année complète et la part de ceux qui n'en ont aucune au début
    de carrière. Une grandeur sans son en-tête arrête la lecture."""
    module = _classeurs()
    grille = {
        (1, 1): "Graphique 1. Nombre moyen de trimestres validés à 30 ans et âge de début "
                "de carrière, par sexe et par génération",
        (4, 2): "Nombre moyen de trimestres validés à 30 ans",
        (4, 5): "Âge moyen de première validation d'une année complète",
        (4, 8): "Part d'affiliés n'ayant pas validé d'année complète avant ou en 2021 (en %)",
        (5, 2): "Femmes - nombre moyen de trimestres validés à 30 ans",
        (5, 3): "Hommes - nombre moyen de trimestres validés à 30 ans", (5, 4): "Ensemble",
        (5, 5): "Femmes - âge moyen de première validation d'une année complète ",
        (5, 6): "Hommes - âge moyen de première validation d'une année complète",
        (5, 7): "Ensemble", (5, 8): "Femmes", (5, 9): "Hommes", (5, 10): "Ensemble",
        (6, 1): 1942.0, (6, 2): 34.0, (6, 3): 42.3, (6, 4): 38.3, (6, 5): 19.7, (6, 6): 19.6,
        (6, 7): 19.6, (6, 8): 1.6, (6, 9): 0.9, (6, 10): 1.2,
    }
    sexes = ("F", "H", "ensemble")
    attendu = {}
    for (champ, groupe, indicateur), valeurs in {
            ("cumul", "30", "trimestres"): (34.0, 42.3, 38.3),
            ("debut_de_carriere", "ensemble", "age_premiere_annee_complete"): (19.7, 19.6, 19.6),
            ("debut_de_carriere", "ensemble", "part_sans_annee_complete_pct"): (1.6, 0.9, 1.2),
    }.items():
        for sexe, valeur in zip(sexes, valeurs):
            attendu[("1942", champ, groupe, "toutes", sexe, indicateur)] = valeur
    assert module.lire_debut_de_carriere(grille) == attendu
    del grille[(4, 5)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_debut_de_carriere(grille)


TRANCHES = ("Entre 20 et 24 ans", "Entre 25 et 29 ans", "Entre 30 et 34 ans",
            "Entre 35 et 39 ans", "Entre 40 et 44 ans", "Entre 45 et 49 ans",
            "Entre 50 et 54 ans", "Entre 55 et 59 ans", "Entre 40 et 49 ans",
            "Entre 30 et 49 ans", "Entre 50 et 59 ans", "À 49 ans")


def test_le_rythme_de_validation_se_lit_par_tranche_dans_le_bloc_de_chaque_sexe():
    """« F12_Graphique 2 » : un bloc par sexe, chacun sa colonne de
    générations — l'étiquette « Hommes » est décalée d'une colonne dans son
    bloc —, puis l'écart entre les deux, qui ne se lit pas : il se déduit.
    « À 49 ans » est un cumul, non un rythme quinquennal."""
    module = _classeurs()
    grille = {(1, 1): "Graphique 2. Rythmes moyens de validation des trimestres par tranche de "
                      "cinq ans, au fil des générations",
              (3, 2): "Femmes", (3, 18): "Hommes", (3, 30): "Écart entre les femmes et les hommes",
              (4, 33): "À 49 ans",
              (5, 1): 1942.0, (5, 2): 11.8, (5, 13): 89.2, (5, 16): 1942.0, (5, 17): 13.8,
              (5, 28): 104.4, (5, 33): -15.2,
              (31, 1): 1994.0, (31, 2): 11.1, (31, 16): 1994.0, (31, 17): 10.8}
    for rang, libelle in enumerate(TRANCHES):
        grille[(4, 2 + rang)] = grille[(4, 17 + rang)] = libelle
    assert module.lire_rythme_validation(grille) == {
        ("1942", "rythme", "20_24", "toutes", "F", "trimestres"): 11.8,
        ("1942", "cumul", "49", "toutes", "F", "trimestres"): 89.2,
        ("1942", "rythme", "20_24", "toutes", "H", "trimestres"): 13.8,
        ("1942", "cumul", "49", "toutes", "H", "trimestres"): 104.4,
        ("1994", "rythme", "20_24", "toutes", "F", "trimestres"): 11.1,
        ("1994", "rythme", "20_24", "toutes", "H", "trimestres"): 10.8,
    }
    del grille[(3, 18)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_rythme_validation(grille)


def test_la_nature_des_trimestres_se_lit_par_sexe_et_par_age_d_observation():
    """« F12_Graphique 3 » : la génération que nomme le titre, le sexe en
    tête de son bloc, l'âge en deuxième colonne ; six natures en part des
    trimestres validés, et leur nombre moyen, qui va aux cumuls."""
    module = _classeurs()
    grille = {
        (1, 1): "Graphique 3. Composition des trimestres validés à différents âges "
                "d’observation, pour la génération née en 1966",
        (5, 3): "Trimestres cotisés (en %)", (5, 4): "Trimestres d'AVPF (en %)",
        (5, 5): "Trimestres de maladie, maternité, invalidité, accidents du travail (en %)",
        (5, 6): "Trimestres de chômage, formation, reconversion, préretraite \n(en %)",
        (5, 7): "Trimestres de service national (en %)",
        (5, 8): "Autres trimestres (trimestres équivalents, rachats, trimestres gratuits "
                "pour autres motifs",
        (5, 9): "Nombre moyen de trimestres validés",
        (6, 1): "Femmes", (6, 2): "25 ans", (6, 3): 79.1, (6, 4): 13.3, (6, 9): 18.6,
        (13, 1): "Hommes", (13, 2): "25 ans", (13, 7): 11.8,
        (14, 2): "30 ans", (14, 3): 87.4, (14, 9): 37.3,
    }
    assert module.lire_composition_trimestres(grille) == {
        ("1966", "composition", "25", "cotises", "F", "part_pct"): 79.1,
        ("1966", "composition", "25", "avpf", "F", "part_pct"): 13.3,
        ("1966", "cumul", "25", "toutes", "F", "trimestres"): 18.6,
        ("1966", "composition", "25", "service_national", "H", "part_pct"): 11.8,
        ("1966", "composition", "30", "cotises", "H", "part_pct"): 87.4,
        ("1966", "cumul", "30", "toutes", "H", "trimestres"): 37.3,
    }
    del grille[(5, 7)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_composition_trimestres(grille)


def test_le_chomage_cumule_se_lit_par_generation_et_par_age():
    """« F12_Graphique 4 » : les générations en lignes, les âges en
    colonnes ; les deux sexes ensemble."""
    module = _classeurs()
    grille = {(1, 1): "Graphique 4. Durée moyenne validée au titre du chômage, de la "
                      "préretraite, de la reconversion et de la formation",
              (3, 2): "20 ans", (3, 10): "60 ans",
              (4, 1): 1942.0, (4, 2): 0.0, (4, 10): 4.4, (32, 1): 1998.0, (32, 2): 0.1}
    cle = ("cumul",)
    assert module.lire_chomage_cumule(grille) == {
        ("1942", *cle, "20", "chomage", "ensemble", "trimestres"): 0.0,
        ("1942", *cle, "60", "chomage", "ensemble", "trimestres"): 4.4,
        ("1998", *cle, "20", "chomage", "ensemble", "trimestres"): 0.1,
    }
    del grille[(3, 2)], grille[(3, 10)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_chomage_cumule(grille)


def test_les_validations_de_l_annee_se_lisent_a_la_generation_paire_de_chaque_age():
    """« F12_Graphique 5 » : un bloc par sexe, les âges de 22 à 62 ans vus en
    2020 ou en 2021, chacun dans la génération paire, la seule que suive
    l'échantillon, qui l'avait l'une de ces deux années : 1998 à 22 et 23 ans,
    1958 à 62 (la note dit « 1958 pour 61 et 62 ans », ce que la règle
    qu'elle énonce dément pour 61 ans, l'âge de 1960 en 2021)."""
    module = _classeurs()
    grille = {(1, 1): "Graphique 5. Nombre moyen et nature des trimestres validés selon l’âge, "
                      "en\xa02020 et\xa02021",
              (3, 1): "Femmes", (3, 7): "Hommes",
              (4, 1): "Âge (en années)", (4, 7): "Âge",
              (5, 1): 22.0, (5, 2): 2.3, (5, 3): 0.2, (5, 7): 22.0, (5, 8): 2.5,
              (6, 1): 23.0, (6, 2): 2.6, (6, 7): 23.0, (6, 8): 2.8,
              (44, 1): 61.0, (44, 5): 0.3, (45, 1): 62.0, (45, 2): 2.0, (45, 7): 62.0,
              (45, 10): 0.2}
    for debut in (1, 7):
        for rang, libelle in enumerate(("Trimestres cotisés au titre de l'emploi", "AVPF",
                                        "Chômage, formation, préretraite, reconversion",
                                        "Maladie, maternité, invalidité, accidents du travail")):
            grille[(4, debut + 1 + rang)] = libelle
    cle = ("validations_de_l_annee",)
    assert module.lire_validations_de_l_annee(grille) == {
        ("1998", *cle, "22", "cotises", "F", "trimestres"): 2.3,
        ("1998", *cle, "22", "avpf", "F", "trimestres"): 0.2,
        ("1998", *cle, "22", "cotises", "H", "trimestres"): 2.5,
        ("1998", *cle, "23", "cotises", "F", "trimestres"): 2.6,
        ("1998", *cle, "23", "cotises", "H", "trimestres"): 2.8,
        ("1960", *cle, "61", "maladie", "F", "trimestres"): 0.3,
        ("1958", *cle, "62", "cotises", "F", "trimestres"): 2.0,
        ("1958", *cle, "62", "chomage", "H", "trimestres"): 0.2,
    }


def test_deux_figures_qui_se_contredisent_arretent_la_lecture():
    """Une même grandeur que deux figures donnent — les trimestres à 30 ans
    de la génération 1966, aux graphiques 1 et 3 de la fiche 12 ; la
    génération 1954 à 59 ans, aux graphiques 1 et 2 de la fiche 21 — se
    réunit si elles disent la même valeur, et arrête la lecture sinon."""
    module = _classeurs()
    cle = ("1966", "cumul", "30", "toutes", "F", "trimestres")
    autre = ("1966", "cumul", "25", "toutes", "F", "trimestres")
    assert module.reunir({cle: 34.2}, {cle: 34.2, autre: 18.6}) == {cle: 34.2, autre: 18.6}
    with pytest.raises(module.FeuilleIllisible):
        module.reunir({cle: 34.2}, {cle: 34.3})


# ---------------------------------------------------------------------------
# Fiche 21 : la fin de carrière, lue dans les feuilles du classeur
# ---------------------------------------------------------------------------

SITUATIONS = ("Absence", "AVPF", "Chômage", "En emploi", "Maladie ou invalidité",
              "Préretraite", "Retraite", "Cumul emploi-retraite, retraite progressive")
CLES_SITUATIONS = ("absence", "avpf", "chomage", "emploi", "maladie_invalidite",
                   "preretraite", "retraite", "cumul_emploi_retraite")


def _bloc_de_situations(grille, ligne, sexe, premiere_colonne, lignes):
    """Un bloc de « F21_Graphique 1 » ou 2 : le sexe, l'en-tête, les lignes."""
    grille[(ligne, 1)] = sexe
    grille[(ligne + 2, 1)] = premiere_colonne
    for rang, libelle in enumerate(SITUATIONS):
        grille[(ligne + 2, 2 + rang)] = libelle
    for decalage, (cle, valeurs) in enumerate(lignes, start=3):
        grille[(ligne + decalage, 1)] = cle
        for rang, valeur in enumerate(valeurs):
            grille[(ligne + decalage, 2 + rang)] = valeur


def test_la_situation_principale_se_lit_par_sexe_et_par_generation_ou_par_age():
    """« F21_Graphique 1 » : à l'âge que le titre nomme, une ligne par
    génération ; « F21_Graphique 2 » : la génération que le titre nomme, une
    ligne par âge, l'en-tête du bloc « Ensemble » commençant par « Ensemble »
    et non par « Âge ». Dans les deux, un bloc par sexe, que son étiquette
    ouvre."""
    module = _classeurs()
    f1954 = (11.45, 0.13, 7.8, 68.1, 6.5, 0.03, 5.9, 0.08)
    h1954 = (8.01, 0.14, 7.32, 68.47, 5.9, 0.09, 9.76, 0.33)
    e1954 = (9.71, 0.13, 7.55, 68.29, 6.19, 0.06, 7.86, 0.21)
    generations = {(1, 1): "Graphique 1. Situation principale d’activité à 59 ans, par sexe et "
                           "par génération", (38, 4): "<"}
    for ligne, sexe, valeurs in ((3, "Femmes", f1954), (15, "Hommes", h1954),
                                 (27, "Ensemble", e1954)):
        _bloc_de_situations(generations, ligne, sexe, "Génération", [(1954.0, valeurs)])
    attendu = {("1954", "situation_par_age", "59", situation, sexe, "part_pct"): valeur
               for sexe, valeurs in (("F", f1954), ("H", h1954), ("ensemble", e1954))
               for situation, valeur in zip(CLES_SITUATIONS, valeurs)}
    assert module.lire_situation_a_un_age(generations) == attendu
    ages = {(1, 1): "Graphique 2. Situations principales successives, de 50 à 67 ans, pour les "
                    "femmes et\xa0les hommes de la génération née en 1954"}
    for ligne, sexe, entete, valeurs in ((3, "Femmes", "Âge ", f1954), (25, "Hommes", "Âge ", h1954),
                                         (47, "Ensemble", "Ensemble", e1954)):
        _bloc_de_situations(ages, ligne, sexe, entete, [(59.0, valeurs)])
    assert module.lire_situations_successives(ages) == attendu
    del ages[(25, 1)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_situations_successives(ages)


def test_la_situation_avant_la_liquidation_se_lit_par_generation_et_par_groupe():
    """« F21_Tableau 1 » : l'étiquette « Génération 1942 » est sur la ligne
    des hommes, celle de « Génération 1954 » sur celle des femmes ; chaque
    génération couvre ses lignes jusqu'aux femmes de la suivante, et les
    groupes de la génération 1954 — selon l'âge de départ, selon le travail
    après 50 ans — sont des deux sexes. L'absence comprend l'AVPF (note 1)."""
    module = _classeurs()
    grille = {(1, 1): "Tableau 1. Situation principale d’activité au cours de l’année précédant "
                      "la liquidation des droits à la retraite, pour les générations nées en "
                      "1942, 1946, 1950 et 1954",
              (3, 3): "En emploi", (3, 4): "Préretraite", (3, 5): "Maladie ou invalidité",
              (3, 6): "Chômage", (3, 7): "Absence1", (3, 8): "Total",
              (4, 2): "Femmes", (4, 3): 46.69, (4, 8): 100.0,
              (5, 1): "Génération 1942", (5, 2): "Hommes", (5, 4): 14.26,
              (6, 2): "Ensemble", (6, 7): 14.77,
              (13, 1): "Génération 1954", (13, 2): "Femmes", (13, 3): 67.69,
              (14, 2): "Hommes", (14, 3): 73.98, (15, 2): "Ensemble", (15, 3): 70.86,
              (16, 2): "Départ avant 61 ans et 7 mois", (16, 3): 92.64,
              (17, 2): "Départ à 61 ans et 7 mois (AOD pour la génération 1954)", (17, 5): 24.46,
              (18, 2): "Départ après 61 ans et 7 mois et avant 66 ans et 7 mois", (18, 6): 6.67,
              (19, 2): "Départ à partir de 66 ans et 7 mois (AAD pour la génération 1954)",
              (19, 7): 25.92,
              (20, 2): "Ayant travaillé après 50 ans", (20, 3): 74.19,
              (21, 2): "N'ayant pas travaillé après 50 ans", (21, 7): 38.52}
    cle = ("situation_avant_liquidation",)
    assert module.lire_situation_avant_liquidation(grille) == {
        ("1942", *cle, "ensemble", "emploi", "F", "part_pct"): 46.69,
        ("1942", *cle, "ensemble", "preretraite", "H", "part_pct"): 14.26,
        ("1942", *cle, "ensemble", "absence", "ensemble", "part_pct"): 14.77,
        ("1954", *cle, "ensemble", "emploi", "F", "part_pct"): 67.69,
        ("1954", *cle, "ensemble", "emploi", "H", "part_pct"): 73.98,
        ("1954", *cle, "ensemble", "emploi", "ensemble", "part_pct"): 70.86,
        ("1954", *cle, "depart_avant_aod", "emploi", "ensemble", "part_pct"): 92.64,
        ("1954", *cle, "depart_a_l_aod", "maladie_invalidite", "ensemble", "part_pct"): 24.46,
        ("1954", *cle, "depart_entre_aod_et_aad", "chomage", "ensemble", "part_pct"): 6.67,
        ("1954", *cle, "depart_a_l_aad_ou_apres", "absence", "ensemble", "part_pct"): 25.92,
        ("1954", *cle, "travail_apres_50_ans", "emploi", "ensemble", "part_pct"): 74.19,
        ("1954", *cle, "sans_travail_apres_50_ans", "absence", "ensemble", "part_pct"): 38.52,
    }
    del grille[(13, 1)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_situation_avant_liquidation(grille)


def test_les_trajectoires_et_les_transitions_se_lisent_par_sexe():
    """« F21_Tableau 2 » : une ligne par trajectoire, retraits compris, la
    ligne « Ensemble » (100) omise ; « F21_Tableau 3 » : le nombre de
    transitions, y compris ou hors celles entre retraite et cumul, chacune sur
    ses trois sexes, et leur nombre moyen ; la ligne « Ensemble », qui somme
    les parts à l'arrondi près, omise."""
    module = _classeurs()
    trajectoires = {
        (1, 1): "Tableau 2. Trajectoires les plus fréquentes à partir de 50 ans, pour la "
                "génération née en 1954",
        (3, 2): "Femmes", (3, 3): "Hommes", (3, 4): "Ensemble",
        (4, 1): "Trajectoires sans années de non-emploi avant le départ à la retraite1 "
                "(passage direct de l'emploi à la retraite)", (4, 2): 54.87,
        (8, 1): "      Emploi, puis chômage, puis retraite", (8, 3): 8.11,
        (13, 1): "Trajectoires sans départ à la retraite à 67 ans ou avant", (13, 4): 4.81,
        (14, 1): "  Personnes continûment en emploi, pas encore retraitées à 67 ans",
        (14, 2): 1.72,
        (15, 1): "Ensemble", (15, 2): 100.0}
    cle = ("trajectoire", "ensemble")
    assert module.lire_trajectoires(trajectoires) == {
        ("1954", *cle, "sans_non_emploi", "F", "part_pct"): 54.87,
        ("1954", *cle, "emploi_chomage_retraite", "H", "part_pct"): 8.11,
        ("1954", *cle, "sans_depart_a_67_ans", "ensemble", "part_pct"): 4.81,
        ("1954", *cle, "emploi_continu_sans_depart", "F", "part_pct"): 1.72,
    }
    transitions = {
        (1, 1): "Tableau 3. Nombre de transitions entre situations principales de 50 à 67 ans, "
                "pour\xa0les personnes nées en 1954 et retraitées à 67 ans ou avant",
        (3, 1): "Nombre de transitions entre 50 et 67 ans",
        (3, 2): "Y compris transitions entre retraite et cumul emploi-retraite",
        (3, 5): "Hors transitions entre retraite et cumul emploi-retraite",
        (4, 2): "Femmes", (4, 3): "Hommes", (4, 4): "Ensemble",
        (4, 5): "Femmes", (4, 6): "Hommes", (4, 7): "Ensemble",
        (5, 1): 1.0, (5, 2): 51.93, (5, 6): 67.08, (10, 1): "6 ou plus", (10, 4): 2.87,
        (11, 1): "Ensemble", (11, 2): 99.97,
        (12, 1): "Nombre moyen de transitions", (12, 2): 1.97, (12, 7): 1.73}
    assert module.lire_transitions(transitions) == {
        ("1954", "transitions", "avec_cumul", "1", "F", "part_pct"): 51.93,
        ("1954", "transitions", "hors_cumul", "1", "H", "part_pct"): 67.08,
        ("1954", "transitions", "avec_cumul", "6_plus", "ensemble", "part_pct"): 2.87,
        ("1954", "transitions", "avec_cumul", "ensemble", "F", "nombre_moyen"): 1.97,
        ("1954", "transitions", "hors_cumul", "ensemble", "ensemble", "nombre_moyen"): 1.73,
    }
    del transitions[(3, 5)]
    with pytest.raises(module.FeuilleIllisible):
        module.lire_transitions(transitions)


# ---------------------------------------------------------------------------
# Les fichiers de référence, aux valeurs que le PDF imprime
# ---------------------------------------------------------------------------

def test_les_trimestres_valides_a_30_ans_viennent_du_panorama():
    """Fiche 12, pages 113 à 115 : la durée validée à 30 ans « atteignant
    42,8 trimestres […] pour les affiliés nés en 1950, elle se réduit à 31,9
    trimestres […] pour la génération 1976 et à 30,5 […] pour la génération
    1990 » ; de 1942 à 1950, elle « est passée de 38,3 trimestres à 42,8 »,
    « +6,4 trimestres » pour les femmes, « +2,9 » pour les hommes ; à 30 ans,
    les femmes nées en 1950 ont validé « 4,8 trimestres de moins que les
    hommes », celles nées en 1976 « 1,9 de moins », en 1986 « 0,4 de moins »,
    et celles nées en 1990 « 30,6 trimestres contre 30,4 ». L'âge de la
    première année complète : 19,3 ans pour les femmes et 18,9 pour les
    hommes nés en 1950, 23,0 et 22,2 pour ceux nés en 1976 ; la lecture du
    graphique 1 (page 114) : 37,4 et 44,0 trimestres, 19,3 et 19,1 ans, pour
    la génération 1946. La génération 1942 vient de l'EIC de 2013."""
    valeurs = _valeurs("durees_validees_actifs.csv")

    def a_30_ans(generation, sexe):
        return valeurs[(generation, "cumul", "30", "toutes", sexe, "trimestres")]

    def age(generation, sexe):
        return valeurs[(generation, "debut_de_carriere", "ensemble", "toutes", sexe,
                        "age_premiere_annee_complete")]

    assert [a_30_ans(g, "ensemble") for g in (1942, 1950, 1976, 1990)] == [38.3, 42.8, 31.9, 30.5]
    assert round(a_30_ans(1950, "F") - a_30_ans(1942, "F"), 1) == 6.4
    assert round(a_30_ans(1950, "H") - a_30_ans(1942, "H"), 1) == 2.9
    assert [round(a_30_ans(g, "H") - a_30_ans(g, "F"), 1) for g in (1950, 1976, 1986)] == [
        4.8, 1.9, 0.4]
    assert (a_30_ans(1990, "F"), a_30_ans(1990, "H")) == (30.6, 30.4)
    assert (a_30_ans(1946, "F"), a_30_ans(1946, "H")) == (37.4, 44.0)
    assert [age(g, s) for g in (1946, 1950, 1976) for s in ("F", "H")] == [
        19.3, 19.1, 19.3, 18.9, 23.0, 22.2]
    generations = {g for g, champ, *_ in valeurs if champ == "debut_de_carriere"}
    assert generations == {1942, 1946, 1950, *range(1954, 1991, 2)}
    assert {l["fiabilite"] for l in _lire(MACRO / "durees_validees_actifs.csv")} == {"certifiee"}


def test_le_rythme_de_validation_et_la_nature_des_trimestres_viennent_du_panorama():
    """Fiche 12. Page 115 : entre 20 et 24 ans, « un pic pour la génération
    1954 (en moyenne, 13,9 trimestres validés sur les 20 possibles pour les
    femmes et 15,1 trimestres pour les hommes) » ; entre 25 et 29 ans, les
    femmes des générations « 1942 (10,3 trimestres validés en moyenne) et
    1956 (15,0 trimestres) », et, pour les hommes, « la génération 1946 (16,6
    trimestres) » ; de 30 à 49 ans, « les femmes nées en 1946 valident en
    moyenne 55,8 trimestres […] contre 63,7 trimestres pour celles nées en
    1972 ». Page 117 : à 49 ans, « les hommes de la génération 1946 valident
    103,5 trimestres contre 88,3 trimestres pour les femmes », ceux de 1972
    « 91,4 contre 89,8 » ; les femmes nées en 1966 « ont ainsi validé en
    moyenne 2,5 trimestres [d'AVPF] à 25 ans, et 7,7 trimestres à 35 ans ».
    Page 118 : la lecture du graphique 3, à 25 ans « 79 % » et « 83 % » des
    trimestres cotisés, 19 et 21 trimestres validés ; le chômage validé à
    30 ans, « quasi nul (0,1 trimestre), jusqu'à la génération 1966 (2,2
    trimestres) ». Pages 119 et 120 : les lectures des graphiques 4 (4,7
    trimestres à 60 ans pour les nés en 1946) et 5 (2,3 et 2,5 trimestres
    cotisés à 22 ans)."""
    valeurs = _valeurs("durees_validees_actifs.csv")

    def rythme(generation, tranche, sexe):
        return valeurs[(generation, "rythme", tranche, "toutes", sexe, "trimestres")]

    assert (rythme(1954, "20_24", "F"), rythme(1954, "20_24", "H")) == (13.9, 15.1)
    assert (rythme(1942, "25_29", "F"), rythme(1956, "25_29", "F")) == (10.3, 15.0)
    assert rythme(1946, "25_29", "H") == 16.6
    assert (rythme(1946, "30_49", "F"), rythme(1972, "30_49", "F")) == (55.8, 63.7)
    cumul = {(g, s): valeurs[(g, "cumul", "49", "toutes", s, "trimestres")]
             for g in (1946, 1972) for s in ("F", "H")}
    assert cumul == {(1946, "H"): 103.5, (1946, "F"): 88.3, (1972, "H"): 91.4, (1972, "F"): 89.8}

    def part(age, nature, sexe):
        return valeurs[(1966, "composition", age, nature, sexe, "part_pct")]

    def total(age, sexe):
        return valeurs[(1966, "cumul", age, "toutes", sexe, "trimestres")]

    assert [round(part(a, "avpf", "F") * total(a, "F") / 100, 1) for a in ("25", "35")] == [2.5, 7.7]
    assert (round(part("25", "cotises", "F")), round(part("25", "cotises", "H"))) == (79, 83)
    assert (round(total("25", "F")), round(total("25", "H"))) == (19, 21)
    chomage = {g: valeurs[(g, "cumul", "30", "chomage", "ensemble", "trimestres")]
               for g in (1946, 1966)}
    assert chomage == {1946: 0.1, 1966: 2.2}
    assert valeurs[(1946, "cumul", "60", "chomage", "ensemble", "trimestres")] == 4.7
    annee = {s: valeurs[(1998, "validations_de_l_annee", "22", "cotises", s, "trimestres")]
             for s in ("F", "H")}
    assert annee == {"F": 2.3, "H": 2.5}


def test_la_situation_en_fin_de_carriere_vient_du_panorama():
    """Fiche 21. Page 183 : à 59 ans, en emploi, « 74 % des femmes » et
    « 76 % des hommes » nés en 1962 ; au chômage, « près de 16 % des femmes
    et environ 17 % des hommes nés en 1942 […] contre 6 % de celles et ceux
    nés en 1962 » ; en préretraite, « 13 % parmi les hommes nés cette
    année-là [1942], à seulement 2 % parmi ceux nés [en 1946] ». Page 184,
    la lecture du graphique 1 : « 51 % des femmes nées en 1946 sont en emploi,
    contre 74 % des femmes nées en 1962 ». Page 186, celle du tableau 1 :
    « 68 % des femmes nées en 1954 étaient principalement en emploi au cours
    de l'année précédant leur départ […], contre 74 % des hommes » ; et la
    page 187 : le passage direct de l'emploi à la retraite « ne concerne que
    55 % des femmes et 62 % des hommes nés en 1954 (tableau 2) ». Page 188,
    la lecture du graphique 2 : « À 50 ans, 84 % des femmes nées en 1954
    occupent un emploi, 7 % sont absentes du marché du travail, 4 % sont au
    chômage, 2 % en maladie ou invalidité et 2 % perçoivent l'AVPF […] 89 %
    des hommes ». Page 189, le tableau 3 : une seule transition pour 52 % des
    femmes et 56 % des hommes, 60 % et 67 % hors cumul ; le nombre moyen,
    1,97, 1,90, 1,93, puis 1,79, 1,66, 1,73."""
    valeurs = _valeurs("fins_de_carriere.csv")

    def a(generation, age, situation, sexe):
        return round(valeurs[(generation, "situation_par_age", str(age), situation, sexe,
                              "part_pct")])

    assert (a(1962, 59, "emploi", "F"), a(1962, 59, "emploi", "H")) == (74, 76)
    assert (a(1942, 59, "chomage", "F"), a(1942, 59, "chomage", "H")) == (16, 17)
    assert (a(1962, 59, "chomage", "F"), a(1962, 59, "chomage", "H")) == (6, 6)
    assert (a(1942, 59, "preretraite", "H"), a(1946, 59, "preretraite", "H")) == (13, 2)
    assert a(1946, 59, "emploi", "F") == 51
    assert [a(1954, 50, s, "F") for s in ("emploi", "absence", "chomage", "maladie_invalidite",
                                          "avpf")] == [84, 7, 4, 2, 2]
    assert a(1954, 50, "emploi", "H") == 89
    avant = {s: round(valeurs[(1954, "situation_avant_liquidation", "ensemble", "emploi", s,
                               "part_pct")]) for s in ("F", "H")}
    assert avant == {"F": 68, "H": 74}
    direct = {s: round(valeurs[(1954, "trajectoire", "ensemble", "sans_non_emploi", s,
                                "part_pct")]) for s in ("F", "H")}
    assert direct == {"F": 55, "H": 62}
    une = [round(valeurs[(1954, "transitions", groupe, "1", s, "part_pct")])
           for groupe in ("avec_cumul", "hors_cumul") for s in ("F", "H")]
    assert une == [52, 56, 60, 67]
    moyen = [valeurs[(1954, "transitions", groupe, "ensemble", s, "nombre_moyen")]
             for groupe in ("avec_cumul", "hors_cumul") for s in ("F", "H", "ensemble")]
    assert moyen == [1.97, 1.90, 1.93, 1.79, 1.66, 1.73]
    assert {g for g, champ, groupe, *_ in valeurs if (champ, groupe) == (
        "situation_par_age", "59")} == {1942, 1946, 1950, 1954, 1956, 1958, 1960, 1962}
    assert {l["fiabilite"] for l in _lire(MACRO / "fins_de_carriere.csv")} == {"certifiee"}


# ---------------------------------------------------------------------------
# À la source : les figures recoupées entre elles, quand l'archive est là
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def lu():
    if not ARCHIVE.is_file():
        pytest.skip("l'archive des classeurs n'est pas dans data/brut/ : "
                    "python scripts/fetch/source_locale.py --recuperer")
    module = _classeurs()
    charge = module.lire(ARCHIVE, module._jeu())
    return {nom: {tuple(cle): valeur for *cle, valeur in charge[nom]}
            for nom in ("durees_validees", "fins_de_carriere")}


def test_les_partis_a_67_ans_sont_le_complement_du_tableau_2(lu):
    """Fiche 21 : à 67 ans, la part des retraités et celle des cumulants
    (graphique 2) font les liquidants de 67 ans ou avant, que le tableau 2
    complète par ceux qui n'ont pas liquidé — 95 %, dit la note du graphique,
    pour la génération 1954."""
    fins = lu["fins_de_carriere"]
    for sexe in ("F", "H", "ensemble"):
        partis = sum(fins[("1954", "situation_par_age", "67", situation, sexe, "part_pct")]
                     for situation in ("retraite", "cumul_emploi_retraite"))
        restes = fins[("1954", "trajectoire", "ensemble", "sans_depart_a_67_ans", sexe,
                       "part_pct")]
        assert partis + restes == pytest.approx(100, abs=0.011), sexe


def test_le_chomage_de_la_generation_1966_est_entre_celui_des_femmes_et_des_hommes(lu):
    """Fiche 12 : le chômage cumulé des deux sexes (graphique 4) est, à chaque
    âge, entre ceux que la composition de la génération 1966 (graphique 3)
    donne à chaque sexe, sa part rapportée au nombre de trimestres validés —
    à l'arrondi de la décimale près."""
    durees = lu["durees_validees"]
    for age in ("25", "30", "35", "40", "45", "50", "55"):
        par_sexe = [durees[("1966", "composition", age, "chomage", sexe, "part_pct")]
                    * durees[("1966", "cumul", age, "toutes", sexe, "trimestres")] / 100
                    for sexe in ("F", "H")]
        ensemble = durees[("1966", "cumul", age, "chomage", "ensemble", "trimestres")]
        assert min(par_sexe) - 0.05 <= ensemble <= max(par_sexe) + 0.05, age
