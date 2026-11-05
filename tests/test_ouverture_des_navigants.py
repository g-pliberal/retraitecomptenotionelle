"""L'âge où s'ouvrent la CRPNPAC et le régime général du navigant (action 130, file N).

La CRPNPAC : « Une pension de retraite est servie à l'affilié qui demande la
liquidation de ses droits à pension [...] dès lors qu'il réunit cumulativement
à la date d'effet de la pension les conditions suivantes : 1° Avoir atteint
l'âge de cinquante ans ; 2° Justifier de vingt annuités acquises au titre des
services valables pour la retraite » (code de l'aviation civile, R. 426-11, I,
LEGIARTI000024795153, du 1er janvier 2012 au 16 décembre 2021). Rien n'y
demande que le régime général soit liquidé ; R. 426-16-1 (LEGIARTI000036880164,
du 7 mai 2018 au 1er novembre 2023) majore même la pension : « Pour la période
de jouissance comprise entre l'âge auquel l'affilié aura atteint le nombre
d'annuités nécessaires pour l'ouverture du droit à pension, et ce au plus tôt
à l'âge mentionné au 1° du A du II de l'article R. 426-11, et l'âge mentionné
à l'article L. 161-17-2 du code de la sécurité sociale, la pension mensuelle
est assortie d'une majoration ».

Le régime général : « L'assurance vieillesse garantit une pension de retraite à
l'assuré qui en demande la liquidation à partir de l'âge mentionné à l'article
L. 161-17-2 » (L. 351-1, LEGIARTI000023035688) ; cet âge est « fixé à
soixante-deux ans pour les assurés nés à compter du 1er janvier 1955 »
(L. 161-17-2, LEGIARTI000025014605, du 23 décembre 2011 au 31 août 2023), puis,
pour les pensions prenant effet à compter du 1er septembre 2026, « 3°
Soixante-deux ans et neuf mois, pour les assurés nés entre le 1er janvier 1963
et le 31 mars 1965 » (L. 161-17-2, LEGIARTI000053280889). Né en 1964, le
navigant n'a ni la carrière longue, ouverte au plus tôt « à cinquante-huit ans
[...] aux assurés nés à compter du 1er janvier 1960 » qui ont « débuté leur
activité avant l'âge de seize ans » (D. 351-1-1, II, LEGIARTI000026139949), ni
le départ des assurés handicapés, qui demande « une incapacité permanente d'au
moins 50 % » (L. 351-1-3, LEGIARTI000028498841).

Le modèle prenait l'âge de la CRPNPAC, complémentaire en annuités, pour celui
de tout le départ : parti à cinquante-cinq ans, le navigant touchait le régime
général et l'Agirc-Arrco avec elle. Chaque cas part de la requête du
simulateur, servi par le portage et refait par le moteur Python
(``servi_et_refait``) : un navigant né le 10 février 1964, entré à vingt-deux
ans. Une pension prend effet au premier jour du mois qui suit l'anniversaire
de son âge. Les dates, posées à la main, sont dans la note
``docs/feuille_de_route/130/2026-11-05-crpnpac-et-regime-general.md``.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import departs
from retraite_notionnelle.simulateur import Simulateur

from outils_pont import servi_et_refait

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "22", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "primes": "0", "profil": "plat", "projection": "cor_reference",
    "salaire": "2", "sexe": "H", "stock": "prix", "table": "unisexe",
    "statut": "personnel_navigant", "naissance": "1964-02-10",
}

#: L'âge du départ demandé, et les départs attendus : la CRPNPAC au départ, le
#: régime général le 1er décembre 2026 (62 ans et 9 mois le 10 novembre 2026,
#: une pension qui prend effet après le 1er septembre 2026).
DEPARTS = {
    # 55 ans le 10 février 2019 : 1er mars 2019 ; 33 annuités.
    "55": [{"date_effet": "2019-03-01", "motif": "depart"},
           {"date_effet": "2026-12-01", "motif": "ouverture"}],
    # 50 ans le 10 février 2014 : 1er mars 2014 ; 28 annuités, plus de vingt.
    "50": [{"date_effet": "2014-03-01", "motif": "depart"},
           {"date_effet": "2026-12-01", "motif": "ouverture"}],
    # 63 ans le 10 février 2027 : le régime général est ouvert, un seul départ.
    "63": [],
}


@pytest.fixture(scope="module")
def servis():
    cas = [{"cle": age, "requete": {**REQUETE, "liquidation": age}} for age in DEPARTS]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


@pytest.mark.parametrize("age", DEPARTS)
def test_la_crpnpac_se_sert_a_son_age_et_le_regime_general_au_sien(servis, age):
    actuel = servis[age]
    assert actuel["liquidation_ouverte"], actuel["motif_ouverture"]
    assert actuel["departs"] == DEPARTS[age]


def test_le_premier_depart_ne_liquide_que_la_crpnpac():
    """Le jumeau Python : à cinquante-cinq ans, les deux tranches de la
    CRPNPAC ; le 1er décembre 2026, le régime général, et l'Agirc-Arrco qui le
    suit, comme toute complémentaire des salariés que le modèle fait liquider
    avec sa base."""
    simulateur = Simulateur()
    carriere = Carriere.depuis_parcours(
        annee_naissance=1964, sexe="H", metiers=[Metier("personnel_navigant", 22.0)],
        age_liquidation=55, macro=simulateur.macro, jour_naissance=10, mois_naissance=2)
    lus = [(depart.date, sorted(depart.regimes), depart.motif)
           for depart in departs.departs(simulateur.scenario_actuel, carriere)]
    assert lus[0] == (DateMois(2019, 3), ["crpnpac", "crpnpac_tranche_2"],
                      departs.MOTIF_DEPART)
    assert lus[1][0] == DateMois(2026, 12) and lus[1][2] == departs.MOTIF_OUVERTURE
    assert "regime_general" in lus[1][1]
    assert len(lus) == 2
