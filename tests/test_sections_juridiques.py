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

**La décote de la CPRN ne connaît que l'âge.** « 1,25 % par trimestre séparant
l'âge de l'affilié à la date de liquidation de l'âge du taux plein », écrivent
ses statuts depuis 2014 ; la fiche laissait la durée d'assurance l'annuler. Et
de 2014 à 2023, cet âge n'était pas celui du régime général : l'âge légal
« différé de vingt-quatre mois », et le taux plein cinq ans plus tard — 64 et
69 ans pour les générations nées depuis 1955. Depuis 2024, une majoration de
10 % pour trois enfants.

**La surcote des avocats a deux taux.** 0,75 % par trimestre accompli de 2004
au 30 juin 2010, 1,25 % depuis le 1er juillet 2010 (R. 723-39 puis R. 653-3) ;
la fiche servait 0,75 % à tous.

**Trois enfants majorent aussi la base des libéraux et des avocats.** La loi
du 14 avril 2023 leur étend L. 351-12 (L. 643-1-1 et L. 653-3), et le
règlement de la complémentaire des avocats l'a suivie en 2024 ; aucune des
trois fiches ne la portait.
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


# -- la CPRN -------------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # 2014-2023 : nés avant 1954, 60 et 65 ans.
    (1952, 62.0, 0.85),
    # 2014-2023 : génération 1958, taux plein à 69 ans ; vingt trimestres au
    # plus, soit 25 %.
    (1958, 64.0, 0.75),
    # Depuis 2024 : l'âge du 1° de L. 351-8, 67 ans ; la durée n'y change rien.
    (1958, 66.0, 0.95),
    (1962, 64.0, 0.85),
])
def test_la_decote_de_la_cprn_ne_connait_que_l_age(
        simulateur, naissance, liquidation, coefficient):
    """« 1,25 % par trimestre séparant l'âge de l'affilié à la date de
    liquidation de l'âge du taux plein » : une carrière complète n'y change
    rien, et l'âge du taux plein est celui des statuts de l'année."""
    resultat, pensions = _calculer(simulateur, "notaire", naissance, 22.0,
                                   liquidation)
    assert resultat.liquidation_ouverte
    cprn = pensions["cprn_complementaire"]
    assert cprn.montant > 0
    assert _coefficient(cprn.detail) == pytest.approx(coefficient)


def test_la_cprn_majore_de_dix_pour_cent_pour_trois_enfants_depuis_2024(simulateur):
    """Article 23 des statuts depuis l'arrêté du 29 novembre 2023."""
    avec, pensions = _calculer(simulateur, "notaire", 1962, 22.0, 67.0,
                               enfants=3)
    majoration = sum(a.montant for a in avec.avantages_appliques
                     if a.code == "majoration_enfants")
    assert majoration > 0
    assert majoration >= 0.10 * pensions["cprn_complementaire"].montant - 0.01
    sans, _ = _calculer(simulateur, "notaire", 1962, 22.0, 67.0, enfants=2)
    assert not [a for a in sans.avantages_appliques
                if a.code == "majoration_enfants"]


# -- la CNBF -------------------------------------------------------------------


def test_la_surcote_des_avocats_passe_a_un_quart_le_1er_juillet_2010(simulateur):
    """R. 653-3 : « 0,75 % par trimestre accompli à compter du 1er janvier
    2004 et avant le 1er juillet 2010 et [...] 1,25 % par trimestre accompli à
    compter du 1er juillet 2010 ». La fiche servait 0,75 % à tous."""
    from retraite_notionnelle.calendrier import DateMois

    baremes = simulateur.scenario_actuel.surcote_baremes
    assert baremes.connait("cnbf")
    avril, juillet = DateMois(2010, 4), DateMois(2010, 7)
    coefficient, _ = baremes.coefficient("cnbf", [(avril, False), (juillet, False)])
    assert coefficient == pytest.approx(1.0 + 0.0075 + 0.0125)
    (periode,) = simulateur.catalogue["cnbf"].periodes_actives(2026)
    assert periode.surcote_bareme == "cnbf"


def test_un_avocat_qui_prolonge_au_dela_de_2010_surcote_aux_deux_taux(simulateur):
    """Né en 1945, entré à vingt ans, parti à soixante-huit ans en 2013 : la
    surcote court depuis 2005, vingt et un trimestres à 0,75 % puis dix à
    1,25 %, soit 28,25 % — là où la fiche en servait 24 %."""
    _, pensions = _calculer(simulateur, "avocat", 1945, 20.0, 68.0)
    assert "taux 128.250%" in pensions["cnbf"].detail


@pytest.mark.parametrize("statut,majorees", [
    # L. 653-3 pour la base, article 16-1 du règlement pour la complémentaire.
    ("avocat", ("cnbf", "cnbf_complementaire")),
    # L. 643-1-1 pour la base ; le règlement de la CAVOM n'en porte aucune.
    ("officier_ministeriel", ("cnavpl",)),
    # La CPRN depuis 2024, et la base avec elle.
    ("notaire", ("cnavpl", "cprn_complementaire")),
])
def test_trois_enfants_majorent_la_base_des_liberaux_et_des_avocats(
        simulateur, statut, majorees):
    """La loi du 14 avril 2023 étend L. 351-12 aux professions libérales et
    aux avocats, pour les pensions prenant effet depuis le 1er septembre 2023.
    Aucune des trois fiches ne la portait."""
    resultat, pensions = _calculer(simulateur, statut, 1962, 22.0, 67.0,
                                   enfants=3)
    majoration = sum(a.montant for a in resultat.avantages_appliques
                     if a.code == "majoration_enfants")
    attendue = 0.10 * sum(pensions[code].montant for code in majorees)
    assert majoration == pytest.approx(attendue, rel=1e-6)
