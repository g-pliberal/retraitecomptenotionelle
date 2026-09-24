"""L'État, la CNRACL et le FSPOEIE : trois régimes, une pension.

Les trois régimes du code des pensions sont INTERPÉNÉTRÉS. Chacun compte, pour
la constitution du droit comme pour la liquidation, les services accomplis dans
les deux autres : L. 5 et L. 11 du code des pensions pour l'État, articles 8
et 13 du décret n° 2003-1306 pour la CNRACL, articles 4 et 10 du décret
n° 2004-1056 pour les ouvriers de l'État. Le régime de la dernière affiliation
sert donc une PENSION UNIQUE, qui « rémunère l'ensemble de sa carrière »
(juris-cnracl, « Règles de coordination avec les autres régimes »), sur le
traitement des six derniers mois de la carrière publique entière.

Le modèle liquidait chaque régime sur ses seules années : le fonctionnaire de
l'État devenu territorial touchait deux pensions, dont une de l'État calculée
sur son traitement de départ. La passe du 24 septembre 2026 a lu ces articles
dans leurs versions, jusqu'à celles de 1964 et de 1965, et l'article 64 du
décret n° 2003-1306, qui annule le rétablissement au régime général de qui
revient dans un régime interpénétré. Ce fichier tient ce qu'elle a corrigé.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur: Simulateur, metiers: list[tuple[str, float]],
              naissance: int = 1962, liquidation: float = 64,
              enfants: int = 0, sexe: str = "H") -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe,
        metiers=[Metier(affiliation=statut, age_debut=debut) for statut, debut in metiers],
        age_liquidation=liquidation, macro=simulateur.macro, nombre_enfants=enfants,
    )


def _pensions(simulateur: Simulateur, carriere: Carriere) -> dict:
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return {p.regime: p for p in resultat.pensions_par_regime if p.montant}


# -- la pension unique --------------------------------------------------------

def test_l_etat_puis_la_cnracl_une_pension_unique(simulateur):
    """Dix-huit ans à l'État, vingt-quatre dans la territoriale : la CNRACL
    liquide les cent soixante-huit trimestres sur son dernier traitement. Le
    modèle servait deux pensions, dont une de l'État sur le traitement de
    2001 : 28 123 € au lieu de 32 731."""
    pensions = _pensions(simulateur, _carriere(simulateur, [
        ("fonctionnaire_etat", 22), ("fonctionnaire_territorial_hospitalier", 40)]))
    assert "fonction_publique_etat" not in pensions
    unique = pensions["cnracl"]
    assert unique.detail.startswith("SR 44,457.21 € × taux 74.063% × 168/169")
    assert unique.detail.endswith(
        "2 caisses liquidées ensemble (fonction_publique_etat puis cnracl)")
    assert unique.montant == pytest.approx(44_457.21 * 0.740625 * 168 / 169, abs=0.01)


def test_c_est_le_dernier_regime_qui_liquide(simulateur):
    """Dans l'autre sens, c'est l'État : la pension se liquide sous les règles
    et sur le traitement du régime de la dernière affiliation."""
    pensions = _pensions(simulateur, _carriere(simulateur, [
        ("fonctionnaire_territorial_hospitalier", 22), ("fonctionnaire_etat", 40)]))
    assert set(pensions) == {"fonction_publique_etat"}
    assert pensions["fonction_publique_etat"].detail.endswith(
        "2 caisses liquidées ensemble (cnracl puis fonction_publique_etat)")


def test_l_ouvrier_d_etat_devenu_fonctionnaire(simulateur):
    """Les services d'ouvrier de l'État entrent dans la pension civile (L. 5,
    3°) : une pension, liquidée par l'État sur cent soixante-huit trimestres."""
    pensions = _pensions(simulateur, _carriere(simulateur, [
        ("ouvrier_etat", 22), ("fonctionnaire_etat", 45)]))
    assert set(pensions) == {"fonction_publique_etat"}
    assert "× 168/169" in pensions["fonction_publique_etat"].detail


def test_meme_separes_par_le_prive(simulateur):
    """Huit ans à l'État, quinze au privé, dix-neuf à l'hôpital. Partie en
    1992 avec moins de quinze ans, l'agente aurait été rétablie au régime
    général ; revenue dans un régime interpénétré, elle « bénéficie, pour la
    retraite, de la totalité des services accomplis », et le rétablissement
    est annulé (article 64, II, du décret n° 2003-1306). Le régime général
    garde, lui, ses quinze ans de privé."""
    pensions = _pensions(simulateur, _carriere(simulateur, [
        ("fonctionnaire_etat", 22), ("salarie_prive_non_cadre", 30),
        ("fonctionnaire_territorial_hospitalier", 45)]))
    assert "fonction_publique_etat" not in pensions
    assert "× 108/169" in pensions["cnracl"].detail
    assert "× 60/169" in pensions["regime_general"].detail


def test_le_militaire_garde_sa_pension_militaire(simulateur):
    """Vingt ans sous l'uniforme, puis la territoriale : le militaire garde sa
    pension, et ne la troque contre une pension unique que par une renonciation
    expresse (L. 77). Le modèle suit ce défaut : deux pensions."""
    pensions = _pensions(simulateur, _carriere(simulateur, [
        ("militaire", 18), ("fonctionnaire_territorial_hospitalier", 38)]))
    assert set(pensions) >= {"fonction_publique_etat", "cnracl"}
    assert "caisses liquidées ensemble" not in pensions["cnracl"].detail


def test_un_fonctionnaire_civil_de_l_etat_est_reuni_meme_ancien_militaire(simulateur):
    """Des services civils à l'État suffisent : la pension de l'État, que le
    catalogue ne scinde pas entre services civils et militaires, rejoint la
    pension unique."""
    pensions = _pensions(simulateur, _carriere(simulateur, [
        ("militaire", 18), ("fonctionnaire_etat", 28),
        ("fonctionnaire_territorial_hospitalier", 40)]))
    assert "fonction_publique_etat" not in pensions
    assert pensions["cnracl"].detail.endswith("puis cnracl)")


def test_un_regime_special_qui_n_est_pas_interpenetre_reste_a_part(simulateur):
    """La SNCF n'est pas interpénétrée avec la CNRACL : deux pensions."""
    pensions = _pensions(simulateur, _carriere(simulateur, [
        ("agent_sncf", 22), ("fonctionnaire_territorial_hospitalier", 40)]))
    assert {"sncf", "cnracl"} <= set(pensions)


# -- ce qui se compte ensemble -------------------------------------------------

def test_les_services_actifs_se_comptent_indifferemment(simulateur):
    """Dix-huit ans de services actifs à l'État, puis la territoriale en
    sédentaire : la faculté de partir cinq ans avant l'âge est ouverte à qui
    compte « dix-sept ans de services accomplis indifféremment dans de tels
    emplois » (L. 24 du code des pensions, article 25 du décret
    n° 2003-1306). La CNRACL, qui liquide, l'ouvre donc ; une territoriale
    sédentaire de toute une carrière attend l'âge légal."""
    active = _carriere(simulateur, [("fonctionnaire_etat_actif", 22),
                                     ("fonctionnaire_territorial_hospitalier", 40)],
                       liquidation=58)
    sedentaire = _carriere(simulateur, [("fonctionnaire_territorial_hospitalier", 22)],
                           liquidation=58)
    actuel = simulateur.scenario_actuel
    assert actuel.calculer(active).liquidation_ouverte
    assert not actuel.calculer(sedentaire).liquidation_ouverte


def test_la_priorite_des_enfants_compte_les_services_ensemble(simulateur):
    """Un an à l'État en 2003, un an à la CNRACL en 2020 : chacun seul n'a pas
    les deux ans de R. 4-1, les deux ensemble les ont. C'est donc le régime
    spécial qui accorde les trimestres de ses enfants nés en 2010 (R. 173-15),
    et le dernier servi : la CNRACL, deux trimestres par enfant."""
    carriere = _carriere(simulateur, [
        ("salarie_prive_non_cadre", 22), ("fonctionnaire_etat", 23),
        ("salarie_prive_non_cadre", 24), ("fonctionnaire_territorial_hospitalier", 40),
        ("salarie_prive_non_cadre", 41)], naissance=1980, enfants=2, sexe="F")
    resultat = simulateur.scenario_actuel.calculer(carriere)
    majoration = next(a for a in resultat.avantages_appliques
                      if a.code == "majoration_duree_assurance")
    assert majoration.detail == "4 trimestres pour 2 enfants, au titre du régime « cnracl »"
    unique = next(p for p in resultat.pensions_par_regime if p.regime == "cnracl")
    # Huit trimestres de services et, pour une pension de 2044, un trimestre
    # de bonification par enfant (b ter de L. 12).
    assert "× 10/172" in unique.detail
