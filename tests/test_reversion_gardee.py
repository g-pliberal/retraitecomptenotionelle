"""Les réversions déjà servies à la bascule, gardées jusqu'à extinction.

Décision 16 du programme (``docs/feuille_de_route_programme.md``) : « on garde
les réversions déjà servies jusqu'à extinction », au seul scénario 6
(décision 28) ; les scénarios 2 à 5 ne servent que les parts contributives.
Le propriétaire a précisé le 7 novembre 2026 que ces réversions se
revalorisent sur les prix, comme aujourd'hui, et que la règle se lit
« décès avant la bascule : réversion du droit actuel » : le scénario 6,
rétroactif, la sert donc entière avant la bascule
(``docs/feuille_de_route/186/2026-11-07-reversion-scenario-6-plan.md``).

Les valeurs attendues viennent de l'étude du 7 novembre
(``docs/feuille_de_route/186/2026-11-07-reversion-etude-et-couts.md``) : le
stock, « d'un âge moyen de 80 ans, s'éteint de moitié en neuf ans », et ne
vaut presque plus rien en 2070 ; il est versé « à 91,5 % à des femmes » (COR,
rapport de novembre 2025).
"""
from __future__ import annotations

import pytest

from retraite_notionnelle.config import Parametres
from retraite_notionnelle.cout import COMPOSANTE_GARANTIE, SCENARIOS, masse_du_scenario
from retraite_notionnelle.donnees.mortalite import DonneesMortalite
from retraite_notionnelle.reversion_gardee import PART_DES_FEMMES, StockDeReversion

LIBERAL = "notionnel_liberal"


@pytest.fixture(scope="module")
def stock() -> StockDeReversion:
    parametres = Parametres()
    racine = parametres.racine_donnees
    return StockDeReversion(racine, DonneesMortalite(racine), parametres.annee_bascule)


def test_le_scenario_6_sert_la_part_gardee_de_la_reversion_et_lui_seul():
    base, derives, rapport = 1000.0, 0.1, 0.8
    directe = base * (1.0 - derives) * rapport
    # Le scénario 6 sert, en plus de ses droits directs, la part de la
    # réversion du droit actuel qu'il garde.
    assert masse_du_scenario(base, derives, rapport, LIBERAL,
                             part_gardee=0.4) == pytest.approx(directe + 40.0)
    # Les scénarios 2 à 5 n'en servent rien (décision 28), et le système
    # actuel sert toute la sienne.
    for scenario, _ in SCENARIOS:
        if scenario in ("actuel", LIBERAL):
            continue
        assert masse_du_scenario(base, derives, rapport, scenario,
                                 part_gardee=0.4) == pytest.approx(directe), scenario
    assert masse_du_scenario(base, derives, rapport, "actuel", part_gardee=0.4) == base
    # La garantie vieillesse n'a pas de veuve.
    assert masse_du_scenario(base, derives, rapport, COMPOSANTE_GARANTIE,
                             part_gardee=0.4) == pytest.approx(directe)
    # Sans part gardée, la convention d'avant : rien.
    assert masse_du_scenario(base, derives, rapport, LIBERAL) == pytest.approx(directe)
    # Sous la convention ``servie``, toute la réversion, comme avant.
    assert masse_du_scenario(base, derives, rapport, LIBERAL, reversion_servie=True,
                             part_gardee=0.4) == pytest.approx(directe + 100.0)


def test_avant_la_bascule_tout_le_stock_est_servi(stock: StockDeReversion):
    bascule = Parametres().annee_bascule
    for annee in (2010, bascule - 1):
        assert stock.survie(annee) == 1.0, annee


def test_le_stock_s_eteint_de_moitie_en_neuf_ans(stock: StockDeReversion):
    bascule = Parametres().annee_bascule
    survies = [stock.survie(annee) for annee in range(bascule, 2071)]
    # La première année, on ne perd que les morts du premier semestre, en
    # moyenne : à 80 ans, quelques pour cent.
    assert 0.94 < survies[0] < 1.0, survies[0]
    # « Il s'éteint de moitié en neuf ans. »
    assert 0.42 < stock.survie(bascule + 9) < 0.58, stock.survie(bascule + 9)
    # Puis il fond : un sixième au plus en 2050, presque rien en 2060, et
    # « ≈ 0 » en 2070.
    assert stock.survie(2050) < 0.2, stock.survie(2050)
    assert stock.survie(2060) < 0.05, stock.survie(2060)
    assert stock.survie(2070) < 0.01, stock.survie(2070)
    # Une réversion servie avant la bascule ne renaît jamais.
    assert all(suivante < courante for courante, suivante in zip(survies, survies[1:]))


def test_le_stock_a_l_age_et_le_sexe_des_survivants_servis(stock: StockDeReversion):
    # « D'un âge moyen de 80 ans. »
    assert 78.0 < stock.age_moyen < 82.0, stock.age_moyen
    # Versé « à 91,5 % à des femmes » (COR, novembre 2025).
    assert PART_DES_FEMMES == 0.915
    assert stock.part_du_sexe("F") == pytest.approx(PART_DES_FEMMES)
    assert stock.part_du_sexe("F") + stock.part_du_sexe("H") == pytest.approx(1.0)
