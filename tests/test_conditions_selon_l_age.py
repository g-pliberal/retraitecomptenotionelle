"""La condition de liquidation des retraités résidant en France, selon leur âge : lue dans le classeur des résidents de l'EIR, certifiée dans un CSV.

`conditions_selon_l_age_residents.csv` est écrit par `scripts/verifier_donnees.py`
depuis ce que `scripts/fetch/drees_caracteristiques_retraites.py` lit dans le
classeur « Caractéristiques de tous les retraités résidant en France » de la
DREES, feuille « CondLiquidation » : pour chaque condition de liquidation, et
pour tous, l'effectif et la part de chaque tranche d'âge au 31 décembre de
l'enquête. La population de la page Coût y prend la décote des générations
que l'EIR ne suit pas une à une, celles d'avant 1950 (action 138, étape 14).
Le classeur reste dans `data/brut/` : le lecteur se teste sur une grille rendue
comme la sienne, et le fichier certifié sur ce que le classeur imprime.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
FICHIER = RACINE / "data" / "reference" / "macro" / "conditions_selon_l_age_residents.csv"

sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import drees_caracteristiques_retraites as recuperateur  # noqa: E402

_ENTETES = ["Carrière longue", "Décote", "Décote non applicable", "Surcote",
            "Taux plein invalidité", "Taux plein inaptitude", "Taux plein autres motifs",
            "Taux plein par âge", "Taux plein par la durée (hors surcote et RACL)",
            "Ensemble"]
_AGE = "Âge au 31 décembre 2020"

#: La feuille « CondLiquidation » du classeur des résidents de 2020, telle
#: qu'elle se lit : les effectifs, une ligne qui ne se lit pas, et l'âge au 31
#: décembre, son âge moyen et ses neuf tranches, une case vide se lisant zéro.
_LIGNES: list[tuple[str, str, str, list]] = [
    ("Ensemble", "Effectifs", "Effectifs (en milliers)",
     [1888.0, 1062.0, 1093.0, 1335.0, 1000.0, 1181.0, 123.0, 2397.0, 5427.0, 15647.0]),
    ("Femme", "Effectifs", "Effectifs (en milliers)",
     [571.0, 741.0, 625.0, 662.0, 565.0, 811.0, 64.0, 1703.0, 2674.0, 8452.0]),
    ("Homme", "Effectifs", "Effectifs (en milliers)",
     [1317.0, 321.0, 468.0, 674.0, 435.0, 370.0, 58.0, 694.0, 2754.0, 7196.0]),
    ("Femme", "Minimum vieillesse", "Part d'assurés au minimum vieillesse (en %)",
     [0.0, 4.2, 0.0, 0.2, 5.3, 17.8, 0.3, 4.3, 0.5, 3.5]),
    ("Ensemble", _AGE, "Âge moyen au 31 décembre 2020 (en années)",
     [66.6, 71.9, 77.3, 70.9, 71.7, 75.7, 66.8, 78.4, 75.0, 73.9]),
    ("Femme", _AGE, "Âge moyen au 31 décembre 2020 (en années)",
     [66.1, 73.1, 77.5, 70.5, 72.1, 77.0, 67.5, 79.5, 74.6, 74.8]),
    ("Homme", _AGE, "Âge moyen au 31 décembre 2020 (en années)",
     [66.8, 69.2, 77.0, 71.2, 71.1, 72.8, 66.1, 75.6, 75.3, 72.7]),
    ("Ensemble", _AGE, "Inférieur à 50 ans",
     [None, 0.3, 0.0, None, 0.0, None, 0.1, 0.0, 0.9, 0.3]),
    ("Femme", _AGE, "Inférieur à 50 ans",
     [None, 0.5, 0.0, None, 0.0, None, 0.1, 0.0, 0.2, 0.1]),
    ("Homme", _AGE, "Inférieur à 50 ans",
     [None, None, None, None, None, None, None, 0.0, 1.6, 0.6]),
    ("Ensemble", _AGE, "Entre 50 et 55 ans (non inclus)",
     [None, 0.5, 0.4, None, 0.1, None, 1.2, 0.3, 0.6, 0.3]),
    ("Femme", _AGE, "Entre 50 et 55 ans (non inclus)",
     [None, 0.7, 0.7, None, 0.0, None, 2.0, 0.1, 0.2, 0.2]),
    ("Homme", _AGE, "Entre 50 et 55 ans (non inclus)",
     [None, 0.1, 0.0, None, 0.1, None, 0.3, 1.0, 0.9, 0.5]),
    ("Ensemble", _AGE, "Entre 55 et 60 ans (non inclus)",
     [0.0, 1.7, 1.7, None, 0.8, None, 6.3, 1.2, 1.3, 1.0]),
    ("Femme", _AGE, "Entre 55 et 60 ans (non inclus)",
     [None, 1.4, 2.5, None, 0.6, None, 9.7, 0.2, 0.9, 0.8]),
    ("Homme", _AGE, "Entre 55 et 60 ans (non inclus)",
     [0.0, 2.2, 0.5, None, 1.0, None, 2.5, 3.8, 1.7, 1.3]),
    ("Ensemble", _AGE, "Entre 60 et 65 ans (non inclus)",
     [39.8, 17.9, 4.6, 7.8, 20.1, 10.8, 38.6, 2.2, 10.5, 13.5]),
    ("Femme", _AGE, "Entre 60 et 65 ans (non inclus)",
     [43.0, 15.7, 6.3, 9.0, 19.3, 8.7, 35.1, 0.6, 12.5, 12.0]),
    ("Homme", _AGE, "Entre 60 et 65 ans (non inclus)",
     [38.4, 23.1, 2.2, 6.7, 21.1, 15.4, 42.3, 6.3, 8.5, 15.3]),
    ("Ensemble", _AGE, "Entre 65 et 70 ans (non inclus)",
     [38.1, 33.4, 10.2, 37.1, 30.0, 20.6, 42.1, 12.0, 18.2, 22.9]),
    ("Femme", _AGE, "Entre 65 et 70 ans (non inclus)",
     [40.8, 30.3, 7.4, 39.0, 29.5, 17.6, 35.7, 10.6, 21.2, 22.0]),
    ("Homme", _AGE, "Entre 65 et 70 ans (non inclus)",
     [36.9, 40.4, 13.9, 35.1, 30.8, 27.3, 49.2, 15.3, 15.2, 23.9]),
    ("Ensemble", _AGE, "Entre 70 et 75 ans (non inclus)",
     [20.2, 19.3, 20.5, 39.7, 21.5, 21.8, 2.7, 22.4, 22.3, 23.0]),
    ("Femme", _AGE, "Entre 70 et 75 ans (non inclus)",
     [15.2, 18.8, 17.9, 38.7, 21.5, 20.8, 4.8, 22.5, 23.3, 22.4]),
    ("Homme", _AGE, "Entre 70 et 75 ans (non inclus)",
     [22.4, 20.4, 24.0, 40.7, 21.5, 24.2, 0.4, 22.4, 21.2, 23.6]),
    ("Ensemble", _AGE, "Entre 75 et 80 ans (non inclus)",
     [1.9, 7.0, 25.5, 13.0, 11.2, 15.9, 0.6, 19.6, 15.8, 14.1]),
    ("Femme", _AGE, "Entre 75 et 80 ans (non inclus)",
     [1.0, 7.4, 25.2, 11.0, 11.1, 16.1, 1.1, 19.9, 13.6, 14.1]),
    ("Homme", _AGE, "Entre 75 et 80 ans (non inclus)",
     [2.3, 5.9, 26.0, 14.9, 11.3, 15.3, 0.1, 19.0, 17.9, 14.1]),
    ("Ensemble", _AGE, "Entre 80 et 85 ans (non inclus)",
     [None, 7.1, 18.7, 2.0, 8.2, 12.1, 2.8, 18.5, 14.1, 11.2]),
    ("Femme", _AGE, "Entre 80 et 85 ans (non inclus)",
     [None, 8.6, 19.6, 1.7, 8.3, 13.7, 3.3, 19.4, 11.8, 11.9]),
    ("Homme", _AGE, "Entre 80 et 85 ans (non inclus)",
     [None, 3.5, 17.5, 2.3, 8.0, 8.7, 2.2, 16.5, 16.3, 10.4]),
    ("Ensemble", _AGE, "Au moins 85 ans",
     [None, 12.9, 18.4, 0.4, 8.2, 18.7, 5.7, 23.6, 16.4, 13.6]),
    ("Femme", _AGE, "Au moins 85 ans",
     [None, 16.6, 20.3, 0.5, 9.7, 23.1, 8.2, 26.9, 16.2, 16.5]),
    ("Homme", _AGE, "Au moins 85 ans",
     [None, 4.2, 15.8, 0.4, 6.2, 9.1, 3.0, 15.7, 16.6, 10.2]),
]


def _grille(lignes: list[tuple[str, str, str, list]]) -> dict[tuple[int, int], float | str]:
    """La feuille comme ``lecture_xlsx.feuilles`` la rend : les cellules vides
    absentes."""
    rangs = [["sexe", "Variable", "Intitulé", *_ENTETES]] + [
        [sexe, variable, intitule, *valeurs] for sexe, variable, intitule, valeurs in lignes]
    return {(r, c): v for r, ligne in enumerate(rangs) for c, v in enumerate(ligne)
            if v is not None}


def test_le_lecteur_lit_l_age_des_retraites_de_chaque_condition():
    """Chaque condition sous son code, et l'ensemble : l'effectif, l'âge moyen,
    la part de chaque tranche d'âge au 31 décembre, une case vide se lisant
    zéro ; le reste de la feuille ne se lit pas. 16,6 % des résidentes parties
    avec une décote ont 85 ans et plus, 16,5 % de toutes."""
    lu = recuperateur.conditions_selon_l_age(_grille(_LIGNES))
    assert sorted(lu) == sorted(["carriere_longue", "decote", "decote_inapplicable",
                                 "surcote", "invalidite", "inaptitude", "autres_motifs",
                                 "taux_plein_age", "taux_plein_duree", "ensemble"])
    assert sorted(lu["decote"]) == sorted(
        ["effectifs", "age_moyen", "age_moins_50", "age_50_55", "age_55_60", "age_60_65",
         "age_65_70", "age_70_75", "age_75_80", "age_80_85", "age_85_plus"])
    assert lu["decote"]["effectifs"]["F"] == 741.0
    assert lu["decote"]["age_85_plus"]["F"] == 16.6
    assert lu["ensemble"]["age_85_plus"]["F"] == 16.5
    assert lu["decote"]["age_moins_50"]["H"] == 0.0
    assert lu["carriere_longue"]["age_80_85"]["ensemble"] == 0.0
    assert lu["ensemble"]["age_moyen"]["H"] == 72.7
    assert lu["taux_plein_duree"]["age_70_75"]["F"] == 23.3


def test_le_lecteur_refuse_une_condition_dont_les_ages_ne_font_pas_cent():
    """Les tranches d'âge d'une condition font cent, à l'arrondi près ; les
    conditions comptent les retraités de l'ensemble, un sur cent n'en ayant
    pas, et les deux sexes redonnent l'ensemble."""
    casse = [list(ligne) for ligne in _LIGNES]
    casse[-2] = ("Femme", _AGE, "Au moins 85 ans",
                 [None, 26.6, 20.3, 0.5, 9.7, 23.1, 8.2, 26.9, 16.2, 16.5])
    with pytest.raises(RuntimeError, match="tranches"):
        recuperateur.conditions_selon_l_age(_grille(casse))
    casse = [list(ligne) for ligne in _LIGNES]
    casse[1] = ("Femme", "Effectifs", "Effectifs (en milliers)",
                [571.0, 741.0, 625.0, 662.0, 565.0, 811.0, 64.0, 1703.0, 2674.0, 9452.0])
    with pytest.raises(RuntimeError, match="effectifs"):
        recuperateur.conditions_selon_l_age(_grille(casse))


def _certifie() -> dict[tuple[str, str, str, str], float]:
    with FICHIER.open(encoding="utf-8") as flux:
        lignes = [ligne for ligne in flux if not ligne.startswith("#")]
    return {(l["annee"], l["condition"], l["indicateur"], l["sexe"]): float(l["valeur"])
            for l in csv.DictReader(lignes)}


def test_le_fichier_certifie_redonne_ce_que_le_classeur_imprime():
    """Ce que le classeur des résidents de 2020 imprime : 741 milliers de
    résidentes parties avec une décote, 8 452 milliers en tout ; 16,6 % des
    premières ont 85 ans et plus, 15,7 % de 60 à 64 ans ; 23,1 % des résidents
    partis avec une décote ont de 60 à 64 ans."""
    lu = _certifie()
    assert lu[("2020", "decote", "effectifs", "F")] == 741.0
    assert lu[("2020", "ensemble", "effectifs", "F")] == 8452.0
    assert lu[("2020", "decote", "age_85_plus", "F")] == 16.6
    assert lu[("2020", "decote", "age_60_65", "F")] == 15.7
    assert lu[("2020", "decote", "age_60_65", "H")] == 23.1
    assert lu[("2020", "ensemble", "age_70_75", "H")] == 23.6
    assert lu[("2020", "decote", "age_moyen", "F")] == 73.1


def test_le_fichier_certifie_redonne_la_decote_des_quintiles():
    """Les tranches de chaque condition font cent ; et la part des décotés
    parmi les résidents, que l'effectif de chaque colonne donne, est celle que
    la feuille des quintiles imprime (``quintiles_eqcc_residents.csv``) : 8,8 %
    des femmes, 4,5 % des hommes."""
    lu = _certifie()
    tranches = ("moins_50", "50_55", "55_60", "60_65", "65_70", "70_75", "75_80",
                "80_85", "85_plus")
    conditions = {c for (_, c, _, _) in lu}
    assert "decote" in conditions and "ensemble" in conditions
    for condition in conditions:
        for sexe in ("ensemble", "F", "H"):
            total = sum(lu[("2020", condition, f"age_{t}", sexe)] for t in tranches)
            assert total == pytest.approx(100.0, abs=0.6), (condition, sexe)
    with (RACINE / "data" / "reference" / "macro" / "quintiles_eqcc_residents.csv").open(
            encoding="utf-8") as flux:
        quintiles = {(l["quintile"], l["indicateur"], l["sexe"]): float(l["valeur"])
                     for l in csv.DictReader(l for l in flux if not l.startswith("#"))}
    for sexe in ("F", "H", "ensemble"):
        part = 100.0 * lu[("2020", "decote", "effectifs", sexe)] / lu[
            ("2020", "ensemble", "effectifs", sexe)]
        assert part == pytest.approx(quintiles[("ensemble", "part_decote", sexe)],
                                     abs=0.06), sexe
