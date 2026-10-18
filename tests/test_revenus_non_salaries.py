"""Les revenus des non-salariés et la pension des anciens non-salariés : lus dans trois fiches de l'INSEE, certifiés dans deux CSV.

`revenus_non_salaries.csv` et `pensions_non_salaries.csv` sont écrits par
`scripts/verifier_donnees.py` depuis ce que
`scripts/fetch/insee_revenus_independants.py` lit dans les classeurs de trois
fiches d'« Emploi et revenus des indépendants », édition 2025 : la 1.3, les
revenus des non-salariés classiques par secteur ; la 1.6, par sexe ; la 1.11,
la pension des anciens non-salariés dans l'EIR de 2020. Les classeurs restent
dans `data/brut/` : le lecteur se teste sur des grilles rendues comme les
leurs, et les fichiers certifiés sur ce que les fiches impriment.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
MACRO = RACINE / "data" / "reference" / "macro"

sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import insee_revenus_independants as recuperateur  # noqa: E402


def _grille(lignes: list[list]) -> dict[tuple[int, int], float | str]:
    """Une feuille comme ``lecture_xlsx.feuilles`` la rend : les cellules vides
    absentes."""
    return {(r, c): v for r, ligne in enumerate(lignes) for c, v in enumerate(ligne)
            if v is not None}


#: La figure 4 de la fiche 1.6, telle que le classeur la rend.
FIGURE_SEXE = [
    ["Figure 4 – Distribution des revenus mensuels des non-salariés classiques par sexe "
     "en 2022"],
    [],
    ["Sexe", "Part de revenus nuls  ou déficitaires \n(en %)",
     "Distribution hors revenus nuls ou déficitaires\n (en euros)", None, None, None, None,
     "Indicateurs d’inégalités \n(hors revenus nuls \nou déficitaires)"],
    [None, None, "D1", "Q1", "Médiane", "Q3", "D9", "Q3/Q1", "D9/D1"],
    ["Femmes", 9.4, 640.0, 1460.0, 2760.0, 4620.0, 7630.0, 3.2, 11.9],
    ["Hommes", 11.3, 660.0, 1560.0, 3000.0, 5630.0, 10460.0, 3.6, 15.8],
    ["Ensemble des non-salariés classiques", 10.6, 650.0, 1520.0, 2900.0, 5190.0, 9320.0,
     3.4, 14.3],
    ["Lecture : Parmi l'ensemble des femmes non-salariées classiques percevant un revenu "
     "positif, une sur dix gagne plus de 7 630 euros par mois."],
    ["Source\xa0: Insee, base Non-salariés 2022."],
]

#: Le haut de la figure 1 de la même fiche.
FIGURE_MOYENNES = [
    ["Figure 1 –  Effectifs et revenus d’activité mensuels selon le sexe en 2022"],
    [],
    ["Secteur", "Effectifs \nau 31/12 \n(en milliers)", "Part des femmes \n(en %)",
     "Revenu mensuel moyen"],
    [None, None, None, "Femmes", "Hommes", "Écart \n(en %)"],
    [None, None, None, "(en euros)"],
    ["Non-salariés classiques", 1850.0, 37.4, 3470.0, 4360.0, -20.4],
    ["Industrie (hors artisanat commercial)", 66.0, 19.5, 1950.0, 3500.0, -44.3],
    ["Micro-entrepreneurs", 1766.0, 44.5, 600.0, 720.0, -16.7],
    ["Ensemble", 3615.0, 40.9, 1980.0, 2720.0, -27.2],
]

#: La figure 1 de la fiche 1.3.
FIGURE_SECTEURS = [
    ["Figure 1 – Dispersion des revenus d’activité mensuels des non-salariés classiques "
     "en 2022"],
    [],
    ["Secteur d'activité", "Effectifs au 31/12 \n(en milliers)",
     "Part des revenus nuls ou déficitaires \n(en %)",
     "Dispersion des revenus hors revenus nuls ou déficitaires \n(en euros)"],
    [None, None, None, "1er décile", "1er quartile", "Médiane", "3e quartile", "9e décile",
     "99e centile"],
    ["Industrie (hors artisanat commercial)", 66.0, 13.8, 440.0, 1140.0, 2480.0, 4510.0,
     7760.0, 22020.0],
    ["Construction", 235.0, 8.7, 800.0, 1610.0, 2560.0, 3880.0, 5940.0, 14800.0],
    ["Commerce et artisanat commercial", 321.0, 13.9, 460.0, 1170.0, 2400.0, 4380.0,
     7630.0, 21770.0],
    ["Transports et entreposage", 62.0, 12.4, 500.0, 950.0, 1670.0, 2790.0, 4520.0,
     13230.0],
    ["Services aux entreprises et services mixtes", 394.0, 13.4, 710.0, 1870.0, 3740.0,
     6850.0, 12290.0, 39730.0],
    ["Services aux particuliers", 297.0, 15.5, 350.0, 850.0, 1610.0, 2660.0, 4370.0,
     12680.0],
    ["Santé et action sociale", 474.0, 2.5, 1460.0, 2550.0, 4050.0, 6940.0, 12080.0,
     31070.0],
    ["Ensemble", 1850.0, 10.6, 650.0, 1520.0, 2900.0, 5190.0, 9320.0, 27950.0],
    ["Lecture : En 2022, 8,7 % des non-salariés de la construction ont un revenu nul ou "
     "déficitaire."],
]

#: La figure 1 de la fiche 1.11.
FIGURE_PENSIONS = [
    ["Figure 1 – Montant total de pension de droit direct brute fin 2020 selon le régime "
     "principal de carrière"],
    [None, None, None, None, None, None, "en euros"],
    ["Régime principal1", "Effectifs\nau 31/12 \n(en milliers)",
     "Pension de droit direct brute2"],
    [None, None, "Moyenne", "1er quartile (Q1)", "Médiane", "3e quartile (Q3)", "Q3/Q1"],
    ["Artisans et commerçants", 500.0, 1230.0, 870.0, 1300.0, 1720.0, 2.0],
    ["Femmes", 140.0, 820.0, 520.0, 870.0, 1230.0, 2.4],
    ["Hommes", 360.0, 1380.0, 1030.0, 1440.0, 1800.0, 1.7],
    ["Exploitants agricoles", 710.0, 810.0, 710.0, 870.0, 990.0, 1.4],
    ["Femmes", 390.0, 670.0, 580.0, 750.0, 870.0, 1.5],
    ["Hommes", 320.0, 970.0, 860.0, 940.0, 1080.0, 1.3],
    ["Professions libérales", 180.0, 2570.0, 1610.0, 2330.0, 3410.0, 2.1],
    ["Femmes", 60.0, 1890.0, 1350.0, 1770.0, 2420.0, 1.8],
    ["Hommes", 120.0, 2930.0, 1930.0, 2870.0, 3780.0, 2.0],
    ["Ensemble des non-salariés", 1390.0, 1180.0, 800.0, 1040.0, 1630.0, 2.0],
    ["Femmes", 590.0, 840.0, 600.0, 830.0, 1130.0, 1.9],
    ["Hommes", 800.0, 1440.0, 910.0, 1210.0, 1790.0, 2.0],
    ["Ensemble des retraités", 15650.0, 1540.0, 920.0, 1440.0, 2050.0, 2.2],
    ["Femmes", 8450.0, 1180.0, 730.0, 1140.0, 1720.0, 2.4],
    ["Hommes", 7200.0, 1960.0, 1270.0, 1730.0, 2330.0, 1.8],
    ["1. Les assurés qui perçoivent plusieurs pensions de régimes différents sont "
     "comptabilisés une seule fois, dans le régime dans lequel ils ont effectué la plus "
     "grande partie de leur carrière."],
    ["Source : Drees, EIR 2020."],
]


def _lire_csv(nom: str, cles: tuple[str, ...]) -> dict[tuple[str, ...], tuple[float, str]]:
    with (MACRO / nom).open(encoding="utf-8") as flux:
        lignes = csv.DictReader(l for l in flux if not l.startswith("#"))
        return {tuple(l[c] for c in cles): (float(l["valeur"]), l["fiabilite"])
                for l in lignes}


def test_la_distribution_par_sexe_se_lit_comme_le_classeur_la_rend():
    """Six valeurs par ligne : la part des revenus nuls ou déficitaires, puis
    les cinq quantiles des revenus positifs, en euros par mois."""
    serie = recuperateur.lire_sexe(_grille(FIGURE_SEXE))
    assert len(serie) == 3 * 6
    assert serie["ensemble|F|d1"] == 640.0
    assert serie["ensemble|F|d9"] == 7630.0
    assert serie["ensemble|H|mediane"] == 3000.0
    assert serie["ensemble|H|part_nuls"] == 11.3
    assert serie["ensemble|ensemble|q3"] == 5190.0


def test_un_quantile_mal_lu_arrete_tout():
    """Les rapports que la figure publie, Q3/Q1 et D9/D1, trahissent une
    colonne décalée ; des quantiles qui ne croissent pas, de même."""
    decalee = [list(ligne) for ligne in FIGURE_SEXE]
    decalee[4] = ["Femmes", 9.4, 640.0, 2760.0, 1460.0, 4620.0, 7630.0, 3.2, 11.9]
    with pytest.raises(ValueError, match="croissent"):
        recuperateur.lire_sexe(_grille(decalee))
    decalee[4] = ["Femmes", 9.4, 640.0, 1460.0, 2760.0, 4620.0, 9320.0, 3.2, 11.9]
    with pytest.raises(ValueError, match="D9/D1"):
        recuperateur.lire_sexe(_grille(decalee))


def test_la_moyenne_de_chaque_sexe_est_celle_des_non_salaries_classiques():
    """La première ligne de la figure 1, revenus nuls compris, et non celle de
    l'ensemble, micro-entrepreneurs compris."""
    serie = recuperateur.lire_moyennes(_grille(FIGURE_MOYENNES))
    assert serie == {"ensemble|F|moyenne": 3470.0, "ensemble|H|moyenne": 4360.0,
                     "ensemble|ensemble|effectifs": 1850.0}


def test_les_secteurs_se_lisent_et_recoupent_la_fiche_par_sexe():
    """Huit lignes de huit valeurs, le 99e centile en plus ; leur ensemble est
    celui de la fiche par sexe, et la somme des secteurs, leur effectif."""
    secteurs = recuperateur.lire_secteurs(_grille(FIGURE_SECTEURS))
    assert len(secteurs) == 8 * 8
    assert secteurs["construction|ensemble|d1"] == 800.0
    assert secteurs["ensemble|ensemble|c99"] == 27950.0
    assert secteurs["sante|ensemble|part_nuls"] == 2.5
    serie = recuperateur.fusionner(recuperateur.lire_sexe(_grille(FIGURE_SEXE)),
                                   recuperateur.lire_moyennes(_grille(FIGURE_MOYENNES)),
                                   secteurs)
    assert serie["ensemble|ensemble|mediane"] == 2900.0
    assert serie["ensemble|ensemble|effectifs"] == 1850.0
    autre = dict(secteurs, **{"ensemble|ensemble|mediane": 2910.0})
    with pytest.raises(ValueError, match="mediane"):
        recuperateur.fusionner(recuperateur.lire_sexe(_grille(FIGURE_SEXE)), autre)


def test_la_pension_des_anciens_non_salaries_se_lit_regime_par_regime():
    """Cinq régimes principaux, chacun suivi de ses femmes et de ses hommes,
    de cinq valeurs : l'effectif, en milliers, puis la moyenne et les trois
    quartiles de la pension de droit direct, en euros bruts par mois."""
    serie = recuperateur.lire_pensions(_grille(FIGURE_PENSIONS))
    assert len(serie) == 5 * 3 * 5
    assert serie["artisans_commercants|ensemble|effectifs"] == 500.0
    assert serie["artisans_commercants|H|mediane"] == 1440.0
    assert serie["artisans_commercants|F|q1"] == 520.0
    assert serie["exploitants_agricoles|F|moyenne"] == 670.0
    assert serie["ensemble|H|q3"] == 2330.0


def test_une_pension_mal_lue_arrete_tout():
    """Les femmes et les hommes font l'effectif de leur régime, et les trois
    régimes de non-salariés celui de leur ensemble."""
    faussee = [list(ligne) for ligne in FIGURE_PENSIONS]
    faussee[6] = ["Hommes", 460.0, 1380.0, 1030.0, 1440.0, 1800.0, 1.7]
    with pytest.raises(ValueError, match="artisans_commercants"):
        recuperateur.lire_pensions(_grille(faussee))


def test_les_fichiers_certifies_redonnent_les_fiches():
    """Ce que les trois fiches impriment, au niveau ``certifiee``."""
    revenus = _lire_csv("revenus_non_salaries.csv", ("annee", "secteur", "sexe", "indicateur"))
    assert revenus[("2022", "ensemble", "F", "d9")] == (7630.0, "certifiee")
    assert revenus[("2022", "ensemble", "H", "mediane")] == (3000.0, "certifiee")
    assert revenus[("2022", "ensemble", "ensemble", "c99")] == (27950.0, "certifiee")
    assert revenus[("2022", "construction", "ensemble", "d1")] == (800.0, "certifiee")
    assert revenus[("2022", "ensemble", "F", "moyenne")] == (3470.0, "certifiee")
    # La fiche par sexe, ses moyennes, les secteurs, moins ce qu'elles partagent.
    assert len(revenus) == 18 + 3 + 8 * 8 - 6 - 1
    pensions = _lire_csv("pensions_non_salaries.csv",
                         ("annee", "regime_principal", "sexe", "indicateur"))
    assert pensions[("2020", "artisans_commercants", "H", "mediane")] == (1440.0, "certifiee")
    assert pensions[("2020", "artisans_commercants", "F", "effectifs")] == (140.0, "certifiee")
    assert len(pensions) == 75


def test_l_ensemble_des_retraites_de_la_fiche_est_celui_de_la_drees():
    """La fiche 1.11 et le classeur de la DREES comptent les mêmes retraités
    résidant en France fin 2020 : les mêmes effectifs et la même moyenne, aux
    dizaines près où la fiche arrondit."""
    pensions = _lire_csv("pensions_non_salaries.csv",
                         ("annee", "regime_principal", "sexe", "indicateur"))
    drees = {}
    with (MACRO / "pensions_residence.csv").open(encoding="utf-8") as flux:
        for l in csv.DictReader(l for l in flux if not l.startswith("#")):
            if l["annee"] == "2020" and l["residence"] == "france":
                drees[(l["indicateur"], l["sexe"])] = float(l["valeur"])
    for sexe in ("F", "H", "ensemble"):
        assert pensions[("2020", "ensemble", sexe, "effectifs")][0] == pytest.approx(
            drees[("effectifs", sexe)], abs=5)
        assert pensions[("2020", "ensemble", sexe, "moyenne")][0] == pytest.approx(
            drees[("pension_droit_direct_majorations", sexe)], abs=5)
