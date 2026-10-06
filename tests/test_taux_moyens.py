"""Le taux moyen de l'Agirc-Arrco, que la page Coût substitue au taux minimal.

Les fiches de l'Arrco et de l'Agirc portent le taux contractuel MINIMAL de
l'accord ; les cas types du COR cotisent au taux MOYEN des entreprises, et la
page Coût, sous ses conventions, aussi (``taux_moyens_agirc_arrco.csv``,
``donnees/regimes.py``, ``dater_les_taux_moyens`` ; action 147 de la feuille
de route, étape 10).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from retraite_notionnelle.config import Parametres
from retraite_notionnelle.donnees.regimes import CatalogueRegimes, charger_taux_moyens

RACINE = Path(__file__).resolve().parents[1]
DONNEES = Parametres().racine_donnees


@pytest.fixture(scope="module")
def catalogues() -> tuple[CatalogueRegimes, CatalogueRegimes]:
    return CatalogueRegimes(DONNEES), CatalogueRegimes(DONNEES, taux_moyens=True)


def _taux(catalogue: CatalogueRegimes, code: str, assiette: str, annee: int):
    return next(p for p in catalogue[code].periodes_actives(annee) if p.assiette == assiette)


def test_le_simulateur_individuel_garde_le_taux_minimal():
    """La convention est celle de la page Coût : le simulateur individuel
    cotise au minimum de l'accord, 4 % appelés à 120 % en 1990 ; son jumeau de
    projection au taux moyen de Trajectoire, 5,42 %."""
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur()
    assert not simulateur.catalogue.taux_moyens
    assert _taux(simulateur.catalogue, "arrco", "tranche_1", 1990
                 ).taux_cotisation_retraite == pytest.approx(0.048)
    projection = simulateur.pour_la_projection()
    assert projection.catalogue.taux_moyens
    assert _taux(projection.catalogue, "arrco", "tranche_1", 1990
                 ).taux_cotisation_retraite == pytest.approx(0.054157 * 1.2)


def test_le_taux_moyen_ne_descend_jamais_sous_le_minimum(catalogues):
    """Une moyenne d'entreprises qui cotisent au moins le minimum ne peut pas
    lui être inférieure : année par année, chaque tranche redatée cotise au
    moins ce que la fiche impose, et les autres régimes ne bougent pas."""
    base, moyen = catalogues
    redates = {code for code, _ in charger_taux_moyens(DONNEES)}
    for regime in base:
        if regime.code not in redates:
            assert moyen[regime.code].periodes == regime.periodes, regime.code
            continue
        for periode in regime.periodes:
            fin = periode.fin if periode.fin is not None else periode.debut + 10
            for annee in range(periode.debut, fin + 1):
                redatee = _taux(moyen, regime.code, periode.assiette, annee)
                assert redatee.taux_cotisation_retraite >= periode.taux_cotisation_retraite - 1e-12, (
                    regime.code, periode.assiette, annee)


def test_les_points_de_2019_se_comptent_au_taux_moyen(catalogues):
    """Depuis 2019, l'Agirc-Arrco calcule ses points sur un taux (6,20 %) et en
    appelle 127 % : sous la convention, le taux de calcul devient le taux
    moyen (6,61 %), et l'appel reste le même."""
    base, moyen = catalogues
    for annee in (2019, 2026, 2060):
        minimal = _taux(base, "agirc_arrco", "tranche_1", annee)
        redate = _taux(moyen, "agirc_arrco", "tranche_1", annee)
        assert redate.taux_calcul_points == pytest.approx(0.0661)
        assert (redate.taux_cotisation_retraite / redate.taux_calcul_points
                == pytest.approx(minimal.taux_cotisation_retraite / minimal.taux_calcul_points))
        assert _taux(moyen, "agirc_arrco", "tranche_2", annee) == _taux(
            base, "agirc_arrco", "tranche_2", annee)


def test_la_tranche_1_rend_l_ecart_de_la_figure_3_1_du_cor(catalogues):
    """La figure 3.1 du rapport du COR de juin 2026 trace le taux de cotisation
    d'un non-cadre sous le plafond, « avec taux minimum obligatoire » et « avec
    taux moyen » de l'Agirc-Arrco, de 1990 à 2025 : leur écart est celui de la
    tranche 1, appel compris. La série de Trajectoire, redatée par le modèle
    sur ses propres minimums et taux d'appel, le rend à un centième de point
    près chaque année — 1,70 point en 1990, 2,00 en 1995, 0,52 depuis 2019 —,
    ce qui dit aussi que le COR de 2026 emploie la même série."""
    base, moyen = catalogues
    cor = json.loads((RACINE / "tests" / "temoins" / "cor_taux_cotisation.json"
                      ).read_text(encoding="utf-8"))
    assert sorted(cor["moyen"]) == [str(annee) for annee in range(1990, 2026)]
    for annee in range(1990, 2026):
        code = "arrco" if annee <= 2018 else "agirc_arrco"
        ecart = (_taux(moyen, code, "tranche_1", annee).taux_cotisation_retraite
                 - _taux(base, code, "tranche_1", annee).taux_cotisation_retraite)
        publie = cor["moyen"][str(annee)] - cor["minimum"][str(annee)]
        assert ecart == pytest.approx(publie, abs=1e-4), annee
