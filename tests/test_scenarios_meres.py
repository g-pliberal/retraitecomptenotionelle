"""La grille des mères : ce que chaque système sert au titre des enfants."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import scenarios_meres  # noqa: E402


@pytest.fixture(scope="module")
def lignes() -> list[scenarios_meres.Ligne]:
    grille = scenarios_meres.Grille(1966, 0.9, "salarie_prive_non_cadre", 21)
    return [grille.calculer(s) for s in scenarios_meres.SITUATIONS]


def test_le_scenario_6_ne_sert_rien_au_titre_des_enfants(lignes):
    # Le compte notionnel ne porte que ce qui a été cotisé : à date de départ
    # égale, une mère et une femme sans enfant y ont la même pension.
    for ligne in lignes:
        assert abs(ligne.effet_enfants_liberal) < 1e-6, ligne.situation.code


def test_le_scenario_1_sert_a_chaque_mere_et_rien_sans_enfant(lignes):
    for ligne in lignes:
        if ligne.situation.nombre_enfants == 0:
            assert abs(ligne.effet_enfants_actuel) < 1e-6, ligne.situation.code
        else:
            assert ligne.effet_enfants_actuel > 0, ligne.situation.code


def test_la_majoration_de_10_pour_cent_n_apparait_qu_a_trois_enfants(lignes):
    par_code = {l.situation.code: l for l in lignes}
    assert not any("trois enfants" in a for a in par_code["complete_2"].avantages)
    assert any("trois enfants" in a for a in par_code["complete_3"].avantages)
    assert par_code["complete_3"].effet_enfants_actuel > par_code["complete_2"].effet_enfants_actuel


def test_la_garantie_vieillesse_porte_le_mi_temps_au_plancher_a_65_ans(lignes):
    par_code = {l.situation.code: l for l in lignes}
    avant = par_code["mitemps_arret6_3"]
    a_65 = par_code["mitemps_65_arret6_3"]
    assert avant.garantie > 0 and not avant.garantie_servie
    assert a_65.garantie_servie
    # 800 + 250 € par mois pour une personne seule, en euros de 2026.
    assert abs(a_65.liberal - 1050.0) < 1.0


def test_la_mere_atteint_le_taux_plein_avant_la_femme_sans_enfant(lignes):
    par_code = {l.situation.code: l for l in lignes}
    assert par_code["complete_2"].age_liquidation < par_code["complete_0"].age_liquidation
    assert par_code["complete_2"].taux >= 0.5


def test_le_script_ecrit_son_csv(tmp_path):
    sortie = tmp_path / "meres.csv"
    assert scenarios_meres.main(["--csv", str(sortie)]) == 0
    with sortie.open(encoding="utf-8") as flux:
        lignes = list(csv.DictReader(flux))
    assert [l["code"] for l in lignes] == [s.code for s in scenarios_meres.SITUATIONS]


def test_l_aide_a_la_naissance_ne_va_qu_aux_meres_et_vaut_moins_que_le_droit(lignes):
    for ligne in lignes:
        if ligne.situation.nombre_enfants == 0:
            assert ligne.aide_recue == 0 and ligne.aide_en_pension == 0
        else:
            assert ligne.aide_recue > 0 and ligne.aide_en_pension > 0
            # L'aide, portée au compte, ne rattrape jamais ce que le droit
            # sert à une mère qui s'est arrêtée : l'AVPF est concentrée sur
            # elle, l'aide est répartie sur toutes les naissances.
            if ligne.situation.annees_arret:
                assert ligne.aide_en_pension < ligne.effet_enfants_actuel


def test_le_solde_vie_entiere_se_recompose(lignes):
    for ligne in lignes:
        assert ligne.annees_pension > 20
        attendu = ligne.liberal_vie + ligne.aide_recue - ligne.actuel_vie
        assert abs(ligne.solde_vie - attendu) < 1e-6
