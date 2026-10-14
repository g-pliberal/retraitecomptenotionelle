"""L'effet retour de la page Coût (action 138, étape 5) : l'ASPA que les
petites pensions des scénarios 2 à 5 déclenchent, et les prélèvements que
leurs pensions ne paient plus, rapportés à l'économie des régimes. L'IPP
(Perspectives budgétaires 2027, juin 2026) trouve un gain public « inférieur
d'environ 20 % à 25 % » à l'économie des régimes."""

import pytest

from retraite_notionnelle import memoire
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.effet_retour import (
    PREMIERE_ANNEE_EFFET_RETOUR,
    SCENARIOS_EFFET_RETOUR,
    _points,
)
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.somme import somme_ordonnee


@pytest.fixture(scope="module")
def avenir():
    return memoire.cout(Parametres()).avenir


def test_rien_avant_le_bareme_a_quatre_taux(avenir):
    avant = avenir.annee(PREMIERE_ANNEE_EFFET_RETOUR - 1)
    assert avant is not None and avant.effet_retour is not None
    assert avant.effet_retour.taux("notionnel_retroactif") == 0.0
    assert avant.effet_retour_constants("notionnel_retroactif") == 0.0
    apres = avenir.annee(PREMIERE_ANNEE_EFFET_RETOUR)
    assert set(apres.effet_retour.prelevements) == set(SCENARIOS_EFFET_RETOUR)


def test_le_scenario_6_n_en_a_pas(avenir):
    """Sa garantie vieillesse, qui remplace l'ASPA, est chiffrée à part."""
    ligne = avenir.annee(2050)
    assert ligne.effet_retour.taux("notionnel_liberal") == 0.0
    assert ligne.gain_public_constants("notionnel_liberal") == pytest.approx(
        ligne.economie_constants("notionnel_liberal"))


def test_le_gain_public_est_l_economie_moins_l_effet_retour(avenir):
    for annee in (2030, 2050, 2070):
        ligne = avenir.annee(annee)
        for scenario in SCENARIOS_EFFET_RETOUR:
            economie = ligne.economie_constants(scenario)
            assert ligne.gain_public_constants(scenario) == pytest.approx(
                economie - ligne.effet_retour.taux(scenario) * economie)


@pytest.mark.parametrize("scenario", SCENARIOS_EFFET_RETOUR)
def test_l_ordre_de_grandeur_de_l_ipp(avenir, scenario):
    """De 2026 à 2070, l'effet retour reprend entre 15 et 35 % de
    l'économie : l'IPP en trouve 20 à 25, sur un calage de l'ASPA qu'il dit
    grossier."""
    part = avenir.part_effet_retour(scenario, 2026, 2070)
    assert part is not None and 0.15 < part < 0.35


@pytest.mark.parametrize("scenario", SCENARIOS_EFFET_RETOUR)
def test_chaque_euro_economise_paie_au_moins_la_csg(avenir, scenario):
    """Une pension qui baisse perd au moins ce que le taux réduit prélève,
    au plus la CSG pleine, la CRDS, la CASA et la tranche à 45 %."""
    ligne = avenir.annee(2060)
    if ligne.economie_constants(scenario) <= 0.0:
        pytest.skip("le scénario n'épargne rien cette année-là")
    assert 0.04 < ligne.effet_retour.prelevements[scenario] < 0.55
    assert ligne.effet_retour.aspa[scenario] >= 0.0


def test_la_tranche_ouverte_redonne_la_moyenne_publiee():
    simulateur = Simulateur(Parametres())
    distribution = simulateur.distribution
    moyenne = simulateur.caracteristiques.valeur("pension_droit_direct_majorations", "ensemble")
    points = _points(distribution, moyenne)
    total = somme_ordonnee(part for _, part in points)
    assert somme_ordonnee(m * p for m, p in points) / total == pytest.approx(moyenne)
    assert points[-1][0] > distribution.tranches[-1].borne_inferieure
