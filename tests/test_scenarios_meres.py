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
    """La mère qui partait avant 65 ans part à 65 ans sous la proposition,
    son âge légal : la garantie lui est donc due dès la liquidation, comme à
    celle qui partait déjà à cet âge — elle n'était jusque-là que différée."""
    par_code = {l.situation.code: l for l in lignes}
    avant = par_code["mitemps_arret6_3"]
    a_65 = par_code["mitemps_65_arret6_3"]
    assert avant.garantie > 0 and avant.garantie_servie
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


# --- La bonification de la fonction publique, et la case où elle tombe -----

def _par_enfant(dispositif: str, naissance_mere: int, liquidation: int):
    """Ce que la table accorde à une mère, en durée et en services."""
    from retraite_notionnelle import chronologie
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.scenarios.actuel import MajorationsPourEnfants

    naissance_des_enfants = naissance_mere + chronologie.valeur("naissance_des_enfants")
    return MajorationsPourEnfants(RACINE_DONNEES).par_enfant(
        dispositif, "F", naissance_des_enfants, liquidation, 2)


def test_la_majoration_de_la_fonction_publique_ne_compte_pas_en_services():
    """L. 12 bis accorde une MAJORATION DE DURÉE, non une bonification.

    Une bonification s'ajoute aux services et relève donc le prorata, c'est-à-
    dire la pension ; une majoration de durée d'assurance ne joue que sur la
    décote et la durée tous régimes. Le modèle les confondait, et créditait
    les mères fonctionnaires de deux trimestres de SERVICES par enfant né
    depuis 2004 que le droit ne leur accorde pas.

    Les mères sont datées par convention à trente ans à la naissance : une
    mère née en 1985 a ses enfants en 2015, donc sous L. 12 bis.
    """
    trimestres, services, _ = _par_enfant("bonifications", 1985, 2045)
    assert trimestres == 2
    assert services == 1, (
        "depuis septembre 2026, UN des deux trimestres est une bonification "
        "au titre du b ter de L. 12 — pas deux, et pas zéro")


def test_avant_2026_aucun_des_deux_trimestres_n_est_un_service():
    """La conversion a une date, et elle est de liquidation.

    Le b ter vaut « pour les pensions prenant effet à compter du 1er septembre
    2026 ». Avant, les deux trimestres de L. 12 bis ne sont qu'une majoration
    de durée : le prorata du régime n'en voit aucun.
    """
    trimestres, services, _ = _par_enfant("bonifications", 1985, 2025)
    assert (trimestres, services) == (2, 0)


def test_la_bonification_d_avant_2004_compte_entierement_en_services():
    """L. 12 b accorde bien une bonification : un an par enfant, aux services.

    C'est le contrôle qui empêche de « corriger » trop loin. La distinction
    introduite ici ne vaut que pour L. 12 bis ; la bonification qui la précède
    entrait aux services, et doit continuer d'y entrer.
    """
    trimestres, services, _ = _par_enfant("bonifications", 1960, 2024)
    assert (trimestres, services) == (4, 4)


def test_la_mda_du_prive_compte_entierement_dans_le_prorata():
    """La MDA relève le prorata du régime général, et c'est le droit.

    L'article L. 351-4 accorde des trimestres de durée d'assurance DU RÉGIME,
    qui entrent donc à son numérateur. La distinction ne doit pas déborder sur
    lui.
    """
    trimestres, services, _ = _par_enfant("mda", 1985, 2045)
    assert (trimestres, services) == (8, 8)
