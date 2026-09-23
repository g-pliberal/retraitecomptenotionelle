"""Le stock converti à 64 ans pour qui est parti à l'âge légal : ce que le script
déplace, et rien d'autre."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.donnees.assiette import AssietteActivite
from retraite_notionnelle.donnees.depenses import DepensesRetraite
from retraite_notionnelle.donnees.equilibre import ComptesRetraite
from retraite_notionnelle.donnees.population import Population
from retraite_notionnelle.scenarios.notionnel import ScenarioNotionnel
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import stock_age_legal  # noqa: E402

PARAMETRES = Parametres()
RACINE = PARAMETRES.racine_donnees


@pytest.fixture(scope="module")
def donnees():
    return (DepensesRetraite(RACINE), Population(RACINE), ComptesRetraite(RACINE),
            AssietteActivite(RACINE))


@pytest.fixture(scope="module")
def reference(donnees):
    return stock_age_legal.calculer("reference", PARAMETRES, *donnees)


@pytest.fixture(scope="module")
def droit_commun(donnees):
    return stock_age_legal.calculer("droit_commun", PARAMETRES, *donnees)


def test_la_variante_de_reference_est_la_page(reference, donnees):
    depenses, population, comptes, assiette = donnees
    page = C.calculer_cout(Simulateur(PARAMETRES), depenses, population, comptes,
                           assiette=assiette)
    assert reference.touches == 0
    for ligne in page.solde.projetees():
        for scenario, _ in C.SCENARIOS:
            assert reference.lectures[scenario].soldes[ligne.annee] == pytest.approx(
                ligne.solde(scenario), abs=1e-12)


def test_le_stock_ne_peut_que_monter_et_les_prospectifs_ne_bougent_pas(reference, droit_commun):
    assert droit_commun.touches > 0
    for cle, pensions in reference.pensions.items():
        for scenario in stock_age_legal.RETROACTIFS:
            assert droit_commun.pensions[cle][scenario] >= pensions[scenario] - 1e-9, (cle, scenario)
        for scenario in stock_age_legal.PROSPECTIFS + ("actuel",):
            assert droit_commun.pensions[cle][scenario] == pytest.approx(pensions[scenario])
    # Le retraité de 1950 au salaire moyen est parti à 60 ans, l'âge légal de
    # sa génération : c'est lui que la variante relève.
    assert droit_commun.pensions["salaire_moyen|1950"]["notionnel_liberal"] > (
        reference.pensions["salaire_moyen|1950"]["notionnel_liberal"])


def test_le_solde_de_la_proposition_baisse_puis_rejoint_la_reference(reference, droit_commun):
    avant = reference.lectures["notionnel_liberal"].soldes
    apres = droit_commun.lectures["notionnel_liberal"].soldes
    assert apres[2026] < avant[2026]
    assert all(apres[a] <= avant[a] + 1e-12 for a in avant)
    # Le stock s'éteint : à l'horizon, l'écart est nul au centième de point.
    assert apres[C.HORIZON] == pytest.approx(avant[C.HORIZON], abs=1e-4)


def test_l_age_legal_est_celui_de_la_generation_ou_du_droit_de_l_assure():
    simulateur = Simulateur(PARAMETRES)
    commun = stock_age_legal.StockALAgeLegal("droit_commun", simulateur)
    tout = stock_age_legal.StockALAgeLegal("tout_droit", simulateur)
    conduite = simulateur.carriere_simple(1960, "H", "agent_sncf", 20.0, 52.0)
    assert commun.age_legal(conduite) == pytest.approx(62.0)
    assert tout.age_legal(conduite) < 62.0
    with pytest.raises(ValueError):
        stock_age_legal.StockALAgeLegal("inconnue", simulateur)


def test_le_contexte_rend_ses_attributs():
    simulateur = Simulateur(PARAMETRES)
    avant = (ScenarioNotionnel.retroactif, ScenarioNotionnel._droits_acquis)
    with stock_age_legal.StockALAgeLegal("tout_droit", simulateur):
        assert ScenarioNotionnel.retroactif is not avant[0]
    assert (ScenarioNotionnel.retroactif, ScenarioNotionnel._droits_acquis) == avant


def test_l_accueil_cite_ce_que_coute_le_diviseur_de_l_age_de_l_assure(reference, droit_commun):
    """Un dixième de point de PIB par an en moyenne, et plus rien en 2050 : la
    phrase de l'accueil, recalculée."""
    from retraite_notionnelle.web.pages import MESURES_BLOCAGES

    liberal = "notionnel_liberal"
    ecart = (reference.lectures[liberal].solde_moyen
             - droit_commun.lectures[liberal].solde_moyen) * 100
    assert round(ecart, 1) == MESURES_BLOCAGES["cout_diviseur_age_legal"]
    en_2050 = (reference.lectures[liberal].soldes[2050]
               - droit_commun.lectures[liberal].soldes[2050]) * 100
    assert abs(en_2050) < 0.05

