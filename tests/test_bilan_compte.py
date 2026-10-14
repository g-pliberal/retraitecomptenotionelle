"""Le bilan du compte notionnel, à la manière suédoise (action 138, étape 19)."""

from __future__ import annotations

import pytest

from retraite_notionnelle.bilan_compte import (
    BilanCompte,
    ProfilParAge,
    Reserves,
    age_moyen,
    calculer_bilans,
    effectif_cotisant,
)
from retraite_notionnelle.castypes import CAS_TYPES
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.population import AGE_MINIMAL, Population


def test_la_duree_de_rotation_d_un_systeme_stationnaire():
    """Des cotisations égales de 20 à 64 ans, des pensions égales de 65 à 84 :
    l'euro cotisé à 42,5 ans en moyenne est servi à 75, trente-deux ans et
    demi plus tard."""
    profil = ProfilParAge(
        2025,
        cotisations={age: 1.0 for age in range(20, 65)},
        pensions={age: 3.0 for age in range(65, 85)},
    )
    assert profil.age_cotisations == pytest.approx(42.5)
    assert profil.age_pensions == pytest.approx(75.0)
    assert profil.duree_rotation == pytest.approx(32.5)
    assert age_moyen({}) == 0.0


def test_le_bilan_tient_ses_identites():
    """L'actif est la cotisation fois la durée, plus les réserves ; le taux de
    cotisation d'équilibre ajoute au taux d'aujourd'hui le manque sur
    l'assiette."""
    bilan = BilanCompte(annee=2025, scenario="actuel", cotisations=0.10,
                        age_cotisations=45.0, age_pensions=75.0, reserves=0.08,
                        dette=4.0, depense=0.14, ressources=0.137, assiette=0.42)
    assert bilan.duree_rotation == pytest.approx(30.0)
    assert bilan.actif_cotisation == pytest.approx(3.0)
    assert bilan.ratio_equilibre == pytest.approx(3.08 / 4.0)
    assert bilan.taux_equilibre == pytest.approx(0.14 / 0.42)
    assert bilan.taux_cotisation_equilibre == pytest.approx(
        bilan.taux_cotisation + (0.14 - 0.137) / 0.42)


def test_les_reserves_du_cor_se_somment_et_rapportent():
    """Le tableau 2.3 du COR : les réserves des régimes et le FRR font le
    total qu'il écrit ; les produits financiers nets de 2025 sur le stock de
    fin 2024 donnent un rendement comptable de l'ordre de 1,6 %."""
    reserves = Reserves.charger(RACINE_DONNEES)
    for annee in reserves.annees():
        total = reserves.montant(annee, "reserves_regimes") + reserves.montant(annee, "frr")
        assert total == pytest.approx(reserves.montant(annee), abs=0.05), annee
    assert reserves.part_pib(2025) == pytest.approx(0.082)
    assert reserves.rendement(2025) == pytest.approx(3.8 / 234.2)
    assert reserves.rendement(2024) is None


def test_un_cotisant_de_moins_de_50_ans_est_compte_a_ses_50_ans():
    population = Population(RACINE_DONNEES)
    assert effectif_cotisant(population, 60, 2025) == population.effectif(60, 2025)
    assert population.effectif(30, 2025) == 0.0
    assert effectif_cotisant(population, 30, 2025) == population.effectif(
        AGE_MINIMAL, 2045)
    assert effectif_cotisant(population, -1, 2025) == 0.0


def test_la_grille_donne_une_duree_de_rotation_a_la_suedoise():
    """Sur la grille, la durée de rotation du système actuel est celle d'un
    système mûr : une trentaine d'années, comme les 31 ans que publie
    Pensionsmyndigheten, des cotisations versées vers 45 ans, des pensions
    servies vers 75."""
    from retraite_notionnelle.contexte import Contexte

    bilans = calculer_bilans(Contexte(), 2025, ["actuel", "notionnel_liberal"],
                             cas_types=CAS_TYPES, engagement=lambda cle: 4.0)
    actuel = bilans["actuel"]
    assert 40.0 < actuel.age_cotisations < 50.0
    assert 70.0 < actuel.age_pensions < 80.0
    assert 25.0 < actuel.duree_rotation < 35.0
    assert actuel.reserves == pytest.approx(0.082)
    assert 0.05 < actuel.cotisations < 0.15
    assert actuel.ratio_equilibre == pytest.approx(
        (actuel.actif_cotisation + actuel.reserves) / 4.0)
