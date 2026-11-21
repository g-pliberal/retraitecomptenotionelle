"""Les points de retraite proportionnelle des exploitants agricoles de 1981 à
1989, au revenu cadastral (action 131).

LE BARÈME. Décret n° 80-808 du 14 octobre 1980, article 8
(LEGIARTI000006769209, en vigueur du 1er janvier 1981 au 21 septembre 1990) :
« le nombre de points acquis chaque année par les intéressés en fonction des
cotisations versées en application du 1°, b, de l'article 1123 du Code rural
est déterminé suivant le barème annexé au présent décret ». Annexe
(LEGIARTI000006769235) : revenu cadastral « au plus égal à 1 180 F », 15
points ; « de 1 180 F à 5 571 F », 30 ; « de 5 571 F à 9 830 F », 45 ;
« supérieur à 9 830 F », 60. R. 732-69 du code rural (LEGIARTI000006597478)
le reprend « pour les années 1981 et suivantes », et R. 732-73 porte à seize,
pour les pensions de 1994 à 2025, les points acquis « en application des
articles R. 732-69 à R. 732-72 ».

LE REVENU CADASTRAL, que le simulateur n'a pas, se déduit du revenu à « 5,54 F
de revenu professionnel pour 1 F de revenu cadastral » (décret n° 92-793,
article 20, LEGIARTI000006776481) : une convention, décidée par le
propriétaire le 20 novembre 2026. Les années d'avant 1981 relèvent de décrets
non lus, et restent au rendement de leurs cotisations.

Les valeurs attendues sont posées à la main depuis l'annexe : 6 000 F de
revenu font 1 083 F cadastraux, 15 points ; 30 000 F, 5 415 F, 30 points ;
35 000 F, 6 318 F, 45 points ; 60 000 F, 10 830 F, 60 points.
"""
from __future__ import annotations

import pytest

from facade import Carriere, Simulateur, acquerir, compter, coordonner
from retraite_notionnelle.types_du_pont.carriere import AnneeCarriere

FRANC = 6.55957

#: Le revenu de l'année, en francs, et les points que l'annexe lui donne.
ANNEES = {
    1980: (30_000.0, None),
    1981: (6_000.0, 15.0),
    1982: (30_000.0, 30.0),
    1983: (35_000.0, 45.0),
    1984: (60_000.0, 60.0),
    1985: (30_000.0, 30.0),
    1986: (35_000.0, 45.0),
    1987: (6_000.0, 15.0),
    1988: (60_000.0, 60.0),
    1989: (30_000.0, 30.0),
}


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _chef(naissance: int, age: float = 65.0, fin: int = 1989,
          affiliation: str = "exploitant_agricole") -> Carriere:
    """Chef d'exploitation de 1980 à `fin`, aux revenus de `ANNEES`."""
    return Carriere(
        annee_naissance=naissance, mois_naissance=1, jour_naissance=15, sexe="H",
        age_liquidation=age,
        lignes=[AnneeCarriere(annee=annee, revenu=francs / FRANC,
                              affiliation=affiliation)
                for annee, (francs, _) in ANNEES.items() if annee <= fin])


def _droits(simulateur, carriere):
    actuel = simulateur.scenario_actuel
    coordination = coordonner.coordonner(actuel, carriere)
    return acquerir.acquerir(actuel, coordination, compter.compter(actuel, coordination))


def test_les_annees_1981_a_1989_ont_les_points_du_bareme_au_revenu_cadastral(simulateur):
    """Parti en 1993, avant le plancher de seize points : les points de
    l'annexe, année par année, et rien que la cotisation pour 1980."""
    droits = _droits(simulateur, _chef(1928))
    points = {annee: valeur for regime, annee, valeur, _ in droits.points
              if regime == "msa_non_salaries"}
    assert points == {annee: attendu for annee, (_, attendu) in ANNEES.items()
                      if attendu is not None}
    cotisees = {annee for regime, annee, _ in droits.cotisations
                if regime == "msa_non_salaries"}
    assert cotisees == {1980}


def test_le_plancher_de_seize_points_vaut_pour_les_points_de_r_732_69(simulateur):
    """R. 732-73 : seize points au moins pour une pension de 1994 à 2025."""
    droits = _droits(simulateur, _chef(1930))
    points = {annee: valeur for regime, annee, valeur, _ in droits.points
              if regime == "msa_non_salaries"}
    assert points[1981] == points[1987] == 16.0
    assert points[1982] == 30.0 and points[1984] == 60.0


def test_la_pension_sert_ces_points_a_la_valeur_du_point(simulateur):
    """330 points de 1981 à 1989 (15 + 30 + 45 + 60 + 30 + 45 + 15 + 60 + 30),
    332 au plancher de seize, qui relève 1981 et 1987 : la pension du
    chef parti en 1995 les sert à la valeur de service de la fiche, au
    rapport de 37,5 années à la durée requise, et ne garde au rendement que la
    cotisation de 1980 : 30 000 F × 8,5 %, revalorisés."""
    carriere = _chef(1930)
    scenario = simulateur.scenario_actuel
    pension = next(p for p in scenario.calculer(carriere).pensions_par_regime
                   if p.regime == "msa_non_salaries")
    assert "332.00 points × valeur de service" in pension.detail, pension.detail
    cotisation = 30_000.0 / FRANC * 0.085 * scenario.macro.coefficient_prix(1980, 1995)
    assert f"cotisations revalorisées {cotisation:,.0f} €" in pension.detail, pension.detail


def test_une_pension_de_1984_sert_ses_points_de_1981_a_1983(simulateur):
    """Le chef qui cesse fin 1983 et part à soixante-cinq ans en 1984 : 15 + 30
    + 45 points, servis à la valeur du point, et non perdus faute de valeur à
    la période."""
    carriere = _chef(1919, fin=1983)
    pension = next(p for p in simulateur.scenario_actuel.calculer(carriere).pensions_par_regime
                   if p.regime == "msa_non_salaries")
    assert "90.00 points × valeur de service" in pension.detail, pension.detail


def test_le_bareme_ne_vaut_que_pour_le_chef_d_exploitation(simulateur):
    """Le barème compte les points des cotisations « du 1°, b, de l'article
    1123 », celles du chef. Le conjoint et l'aide familial, que le modèle ne
    distingue pas avant 2004, n'y entrent pas : leurs années restent où elles
    étaient, au rendement de leurs cotisations."""
    droits = _droits(simulateur, _chef(1928, affiliation="collaborateur_agricole"))
    assert not [annee for regime, annee, _, _ in droits.points
                if regime == "msa_non_salaries"]
    cotisees = {annee for regime, annee, _ in droits.cotisations
                if regime == "msa_non_salaries"}
    assert cotisees == set(ANNEES)
