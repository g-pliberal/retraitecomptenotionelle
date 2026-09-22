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

**Le RAAP à la moitié du taux pour qui cotise au RACD ou au RACL.** Le II de
l'article 2 du décret n° 62-420, depuis le 1er janvier 2016 : « Pour les
personnes tenues de cotiser aux régimes […] institués par les décrets
n° 61-1304 [le RACL] et n° 64-226 [le RACD], le taux de la cotisation au
régime institué par le présent décret est égal à la moitié de celui prévu au
I ». Le modèle prélevait 8 % aux auteurs dramatiques et aux compositeurs, et
leur servait donc le double des points du RAAP qu'ils acquièrent.
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


#: Les deux fiches du RAAP — au taux plein et au taux aménagé des auteurs du
#: RACD et du RACL — servent des points du même régime, et la même majoration.
RAAP = ("ircec_raap", "ircec_raap_taux_amenage")


@pytest.mark.parametrize("statut,majorees", [
    ("artiste_auteur", ("regime_general", *RAAP)),
    ("auteur_dramatique", ("regime_general", *RAAP, "ircec_racd")),
    ("auteur_lyrique", ("regime_general", *RAAP)),
])
def test_trois_enfants_majorent_le_raap_et_le_racd_mais_pas_le_racl(
        simulateur, statut, majorees):
    """Un départ en 2037, à soixante-sept ans : 10 % des pensions qui la doivent.

    La majoration du régime général s'y ajoute comme à tout assuré ; celle du
    RACL n'existe pas, et le compte ne doit pas la contenir.
    """
    resultat, pensions = _calculer(simulateur, statut, 1970, 21.0, 67.0,
                                   enfants=3)
    attendu = 0.10 * sum(pensions[code].montant for code in majorees
                         if code in pensions)
    assert _majoration(resultat) == pytest.approx(attendu, rel=1e-9)


def test_le_racd_ne_majorait_rien_avant_2024(simulateur):
    """Un auteur dramatique parti en 2020 : le RAAP majore, le RACD pas encore.

    L'article 23 du règlement du RACD n'a reçu sa majoration qu'avec l'arrêté
    du 17 avril 2024.
    """
    resultat, pensions = _calculer(simulateur, "auteur_dramatique", 1953, 21.0,
                                   67.0, enfants=3)
    assert "ircec_racd" in pensions
    attendu = 0.10 * sum(pensions[code].montant
                         for code in ("regime_general", *RAAP))
    assert _majoration(resultat) == pytest.approx(attendu, rel=1e-9)


def test_sans_trois_enfants_rien_n_est_majore(simulateur):
    """Deux enfants ne font rien : ni le RAAP ni le RACD n'ont de barème à deux."""
    resultat, _ = _calculer(simulateur, "auteur_dramatique", 1970, 21.0, 67.0,
                            enfants=2)
    assert _majoration(resultat) == 0.0


@pytest.mark.parametrize("statut", ["auteur_dramatique", "auteur_lyrique"])
def test_le_raap_des_auteurs_du_racd_et_du_racl_est_a_la_moitie_du_taux(
        simulateur, statut):
    """Une carrière entière depuis 2016 : exactement la moitié du RAAP d'un
    artiste-auteur au même revenu — la moitié de la cotisation, donc la moitié
    des points, au même rendement et à la même minoration."""
    _, artiste = _calculer(simulateur, "artiste_auteur", 1994, 22.0, 64.0)
    _, auteur = _calculer(simulateur, statut, 1994, 22.0, 64.0)
    assert "ircec_raap" not in auteur
    assert auteur["ircec_raap_taux_amenage"].montant == pytest.approx(
        artiste["ircec_raap"].montant / 2, rel=1e-9)


def test_avant_2016_le_raap_des_auteurs_n_est_pas_divise(simulateur):
    """Le II de l'article 2 date de la réforme de 2016 : une carrière qui la
    traverse garde ses points d'avant au RAAP, et ne divise que la suite."""
    _, artiste = _calculer(simulateur, "artiste_auteur", 1975, 22.0, 64.0)
    _, auteur = _calculer(simulateur, "auteur_dramatique", 1975, 22.0, 64.0)
    avant, apres = auteur["ircec_raap"].montant, auteur["ircec_raap_taux_amenage"].montant
    assert avant > 0 and apres > 0
    assert avant + 2 * apres == pytest.approx(artiste["ircec_raap"].montant, rel=1e-9)


def test_la_fiche_au_taux_amenage_emprunte_le_rendement_du_raap(simulateur):
    """Le rendement fait partie du barème du point : une fiche qui emprunte ce
    barème (`points_de`) l'emprunte aussi. Lu sous son propre code, il n'aurait
    trouvé aucune ligne, et la pension serait tombée à zéro sans rien dire."""
    _, auteur = _calculer(simulateur, "auteur_lyrique", 1994, 22.0, 64.0)
    assert "rendement 10.80%" in auteur["ircec_raap_taux_amenage"].detail
