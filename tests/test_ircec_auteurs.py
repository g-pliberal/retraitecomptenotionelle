"""Ce que les règlements de l'IRCEC servent aux auteurs, au-delà de la minoration.

Le barème de minoration des trois régimes de l'IRCEC est tenu par
`tests/test_simulateur.py`. Ce fichier tient ce que la même lecture des
règlements a ajouté ensuite, le 22 septembre 2026.

**La majoration pour trois enfants.** « Il est majoré de 10 % au profit de
l'adhérent ayant eu au moins trois enfants » : l'article 28 du règlement du
RAAP, dans la rédaction de l'arrêté du 21 novembre 2013 (JORFARTI000028254004),
et l'article 23 de celui du RACD, que l'arrêté du 17 avril 2024
(JORFARTI000049490796) a complété de la même phrase. Le règlement du RACL n'en
porte pas. Aucune des trois fiches ne la déclarait.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int,
              debut: float, liquidation: float, enfants: int = 0):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance,
        sexe="H",
        metiers=[Metier(affiliation=affiliation, age_debut=debut,
                        niveau_salaire=1.0)],
        age_liquidation=liquidation,
        macro=simulateur.macro,
        nombre_enfants=enfants,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return resultat, {p.regime: p for p in resultat.pensions_par_regime}


def _majoration(resultat) -> float:
    return sum(a.montant for a in resultat.avantages_appliques
               if a.code == "majoration_enfants")


@pytest.mark.parametrize("statut,majorees", [
    ("artiste_auteur", ("regime_general", "ircec_raap")),
    ("auteur_dramatique", ("regime_general", "ircec_raap", "ircec_racd")),
    ("auteur_lyrique", ("regime_general", "ircec_raap")),
])
def test_trois_enfants_majorent_le_raap_et_le_racd_mais_pas_le_racl(
        simulateur, statut, majorees):
    """Un départ en 2037, à soixante-sept ans : 10 % des pensions qui la doivent.

    La majoration du régime général s'y ajoute comme à tout assuré ; celle du
    RACL n'existe pas, et le compte ne doit pas la contenir.
    """
    resultat, pensions = _calculer(simulateur, statut, 1970, 21.0, 67.0,
                                   enfants=3)
    attendu = 0.10 * sum(pensions[code].montant for code in majorees)
    assert _majoration(resultat) == pytest.approx(attendu, rel=1e-9)


def test_le_racd_ne_majorait_rien_avant_2024(simulateur):
    """Un auteur dramatique parti en 2020 : le RAAP majore, le RACD pas encore.

    L'article 23 du règlement du RACD n'a reçu sa majoration qu'avec l'arrêté
    du 17 avril 2024.
    """
    resultat, pensions = _calculer(simulateur, "auteur_dramatique", 1953, 21.0,
                                   67.0, enfants=3)
    assert "ircec_racd" in pensions
    attendu = 0.10 * (pensions["regime_general"].montant
                      + pensions["ircec_raap"].montant)
    assert _majoration(resultat) == pytest.approx(attendu, rel=1e-9)


def test_sans_trois_enfants_rien_n_est_majore(simulateur):
    """Deux enfants ne font rien : ni le RAAP ni le RACD n'ont de barème à deux."""
    resultat, _ = _calculer(simulateur, "auteur_dramatique", 1970, 21.0, 67.0,
                            enfants=2)
    assert _majoration(resultat) == 0.0
