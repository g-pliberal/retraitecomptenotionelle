"""Le stock converti à l'âge de référence pour qui est parti à l'âge légal : ce que le script
déplace, et rien d'autre. La règle est au moteur, sous ``Parametres.stock_age_legal``
(action 161) : ``tests/js/stock-age-legal.test.js`` la tient carrière par carrière,
``tests/test_pont.py`` son jumeau ; ici, ce que l'étude en lit, calculé par le portage."""

from __future__ import annotations

import shutil
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle import memoire, pont
from retraite_notionnelle.config import Parametres, StockAgeLegal
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import stock_age_legal  # noqa: E402

PARAMETRES = Parametres()


@pytest.fixture(scope="module")
def reference():
    return stock_age_legal.calculer("reference", PARAMETRES)


@pytest.fixture(scope="module")
def droit_commun():
    return stock_age_legal.calculer("droit_commun", PARAMETRES)


def test_la_variante_de_reference_est_la_page(reference):
    page = memoire.cout(PARAMETRES)
    for ligne in page.solde.projetees():
        for scenario, _ in C.SCENARIOS:
            assert reference.lectures[scenario].soldes[ligne.annee] == pytest.approx(
                ligne.solde(scenario), abs=1e-12)


def test_le_stock_ne_peut_que_monter_et_les_prospectifs_ne_bougent_pas(reference, droit_commun):
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


def test_chaque_variante_est_une_regle_du_moteur():
    """Une variante de l'étude est la règle du stock que le moteur applique
    (``Parametres.stock_age_legal``) : l'étude ne remplace plus aucune
    fonction du moteur le temps d'un calcul. La référence n'en pose aucune."""
    assert stock_age_legal.parametres_de("reference", PARAMETRES) == PARAMETRES
    for variante in ("droit_commun", "tout_droit", "acquis"):
        assert stock_age_legal.parametres_de(variante, PARAMETRES) == replace(
            PARAMETRES, stock_age_legal=StockAgeLegal(variante))
    with pytest.raises(ValueError):
        stock_age_legal.parametres_de("inconnue", PARAMETRES)


def test_les_cas_types_passent_par_le_portage_au_bit_pres_du_jumeau(monkeypatch):
    """Les cas types de l'étude se datent et se simulent par le portage, la
    règle du stock dans les paramètres de la demande (action 161) : la pension
    de chaque système, en euros constants, au bit près de ce que le jumeau
    Python en simule sous la même règle et ``pont.par_le_jumeau()`` — sans que
    le moteur Python ne calcule rien."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne calcule pas ici")
    from outils_pont import empecher_les_jumeaux_du_cout
    from retraite_notionnelle.castypes import CAS_TYPES, calculer_cas_types

    codes = {code for code, _ in stock_age_legal.CAS_STOCK}
    generations = tuple(sorted({generation for _, generation in stock_age_legal.CAS_STOCK}))
    simulateurs = {variante: Simulateur(stock_age_legal.parametres_de(variante, PARAMETRES))
                   for variante in ("droit_commun", "tout_droit")}
    attendus = {}
    with pont.par_le_jumeau():
        for variante, simulateur in simulateurs.items():
            grille = calculer_cas_types(
                simulateur, tuple(cas for cas in CAS_TYPES if cas.code in codes), generations)
            attendus[variante] = {
                f"{code}|{generation}": {
                    scenario: comparaison.en_euros_constants(
                        getattr(comparaison, scenario).pension_annuelle, scenario)
                    for scenario, _ in C.SCENARIOS}
                for code, generation in stock_age_legal.CAS_STOCK
                if (comparaison := grille.resultats.get((code, generation))) is not None}
    empecher_les_jumeaux_du_cout(monkeypatch)
    for variante, simulateur in simulateurs.items():
        lues = stock_age_legal.pensions_des_cas(simulateur)
        assert lues == attendus[variante], variante
        assert list(lues) == [f"{code}|{generation}"
                              for code, generation in stock_age_legal.CAS_STOCK], variante
    # Un agent de conduite parti à cinquante-deux ans : le droit commun le
    # laisse au diviseur de son âge, son propre droit le relève.
    conduite = "agent_sncf_conduite|1960"
    assert (attendus["tout_droit"][conduite]["notionnel_liberal"]
            > attendus["droit_commun"][conduite]["notionnel_liberal"])


def test_l_accueil_cite_ce_que_coute_le_diviseur_de_l_age_de_l_assure(reference, droit_commun):
    """Deux dixièmes de point de PIB par an en moyenne, et plus rien à partir
    de 2060 : la phrase de l'accueil, recalculée. C'était un dixième, et plus
    rien dès 2050, avant que la proposition ne fixe son âge légal à 65 ans :
    le report garde plus longtemps dans le compte ceux que le diviseur de leur
    âge avantageait."""
    from retraite_notionnelle.web.site import disponible, module

    if not disponible():
        pytest.skip("node absent : le site ne se lit pas sans lui")
    MESURES_BLOCAGES = module("pages").MESURES_BLOCAGES

    liberal = "notionnel_liberal"
    ecart = (reference.lectures[liberal].solde_moyen
             - droit_commun.lectures[liberal].solde_moyen) * 100
    assert round(ecart, 1) == MESURES_BLOCAGES["cout_diviseur_age_legal"]
    for annee in (2060, 2070):
        ecart_annee = (reference.lectures[liberal].soldes[annee]
                       - droit_commun.lectures[liberal].soldes[annee]) * 100
        assert abs(ecart_annee) < 0.05, annee
