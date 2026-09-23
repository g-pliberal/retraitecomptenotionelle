"""Ce que les règlements des sections juridiques servent, lus au texte.

La passe du 23 septembre 2026 sur les professions juridiques (action 89) a lu
les statuts et les règlements de la CAVOM et de la CPRN au Journal officiel,
et les barèmes de la CNBF. Ce fichier tient ce qu'elle a corrigé.

**La CAVOM a ses âges.** L'article 14 de ses statuts dans la rédaction de
l'arrêté du 12 décembre 2024, puis l'article 1er du règlement que l'arrêté du
10 juillet 2026 approuve, les écrivent génération par génération : ouverture à
soixante ans et taux plein à soixante-cinq avant la génération 1956, six mois
de plus par génération jusqu'à 62 et 67 ans pour celle de 1959, puis
l'ouverture portée à 64 ans de 1965 à 1968. La fiche lisait les tables du
régime général.

**Sa minoration compte des années, et seul l'âge l'annule.** « Ce coefficient
est fixé à 5 % par année manquante entre l'âge auquel est demandée la
liquidation de la retraite […] et l'âge prévu au 2°. Ce coefficient n'est pas
susceptible de fractionnement. » La fiche lui opposait la décote du régime de
base, que la durée d'assurance annule : un officier ministériel parti à
soixante-quatre ans avec sa durée ne perdait rien de sa complémentaire.

**Son plafond est monté par marches.** Le décret n° 2015-1875 appelle la
cotisation proportionnelle de 2016 dans la limite de quatre plafonds, puis
cinq, six et sept, avant les huit de 2020 ; l'assiette ne peut descendre sous
le quart du plafond, puis sous 19 % depuis 2019.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int,
              debut: float, liquidation: float, enfants: int = 0,
              niveau: float = 1.5):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance,
        sexe="H",
        metiers=[Metier(affiliation=affiliation, age_debut=debut,
                        niveau_salaire=niveau)],
        age_liquidation=liquidation,
        macro=simulateur.macro,
        nombre_enfants=enfants,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return resultat, {p.regime: p for p in resultat.pensions_par_regime}


def _coefficient(detail: str) -> float:
    """Le coefficient d'anticipation écrit dans le détail, 1 s'il n'y en a pas."""
    marque = "coefficient d'anticipation "
    if marque not in detail:
        return 1.0
    return float(detail.split(marque)[1].split()[0])


# -- la CAVOM ------------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # Avant 1956 : taux plein à 65 ans, quelle que soit la génération.
    (1945, 64.0, 0.95),
    (1955, 62.0, 0.85),
    (1955, 65.0, 1.0),
    # 66 ans pour la génération 1957 : quatre années manquantes à 62 ans.
    (1957, 62.0, 0.80),
    # 67 ans depuis 1959, et la durée n'y change rien.
    (1962, 64.0, 0.85),
    (1968, 64.0, 0.85),
    (1968, 67.0, 1.0),
])
def test_la_cavom_minore_de_cinq_pour_cent_par_annee_jusqu_a_son_age(
        simulateur, naissance, liquidation, coefficient):
    """Carrière complète commencée à 22 ans : la durée est réunie partout.

    C'est précisément le cas où la fiche ne minorait rien — la décote du
    régime de base s'annule par la durée. Le règlement de la CAVOM ne
    connaît que l'âge.
    """
    resultat, pensions = _calculer(simulateur, "officier_ministeriel",
                                   naissance, 22.0, liquidation)
    assert resultat.liquidation_ouverte
    cavom = pensions["cavom_complementaire"]
    assert cavom.montant > 0
    assert _coefficient(cavom.detail) == pytest.approx(coefficient)


def test_l_annee_entamee_compte_entiere(simulateur):
    """Deux ans et neuf mois avant l'âge du taux plein : trois années, 15 %.

    « Ce coefficient n'est pas susceptible de fractionnement » : le texte ne
    dit pas davantage, et le modèle compte l'année entamée, comme l'IRCEC
    l'écrit en toutes lettres pour la même règle.
    """
    _, pensions = _calculer(simulateur, "officier_ministeriel",
                            1962, 22.0, 64.25)
    assert _coefficient(pensions["cavom_complementaire"].detail) == pytest.approx(0.85)


def test_la_complementaire_ne_decide_pas_de_l_ouverture_du_droit(simulateur):
    """Un officier ministériel né en 1955 ne liquide pas à soixante ans.

    Sa complémentaire s'ouvre à soixante ans, son régime de base à
    soixante-deux : c'est le second qui dit quand le droit s'ouvre, et le
    modèle, qui liquide tous les régimes à la même date, le suit.
    """
    resultat, _ = _calculer(simulateur, "officier_ministeriel", 1955, 22.0, 60.0)
    assert not resultat.liquidation_ouverte
    assert resultat.age_ouverture_opposable == pytest.approx(62.0)


def test_le_plafond_de_la_cavom_monte_par_marches(simulateur):
    """Quatre plafonds en 2016, huit en 2020 ; un minimum d'assiette partout."""
    regime = simulateur.catalogue["cavom_complementaire"]
    attendus = {
        2016: (4.0, 0.25), 2017: (5.0, 0.25), 2018: (6.0, 0.25),
        2019: (7.0, 0.19), 2020: (8.0, 0.19), 2026: (8.0, 0.19),
    }
    for annee, (plafonds, minimum) in attendus.items():
        (periode,) = regime.periodes_actives(annee)
        assert periode.bornes_assiette_en_pass() == (0.0, plafonds), annee
        assert periode.assiette_minimale_pass == pytest.approx(minimum), annee
        assert periode.taux_cotisation_retraite == pytest.approx(0.125), annee
