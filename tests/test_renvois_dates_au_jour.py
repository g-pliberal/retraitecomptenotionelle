"""Les renvois d'âge des régimes, datés au jour du texte qui les fait.

La note de décision 0009 compte dix renvois d'un régime aux fiches d'âge dont
la date peut changer un résultat ; leur relecture au texte, le 17 novembre
2026 (`docs/feuille_de_route/191/2026-11-17-dix-renvois-sensibles.md`), en a
trouvé quatre coupés à l'année quand le texte coupe au jour. Chaque attendu
vient du texte.

- **Banque de France.** Décret n° 2007-262 du 27 février 2007, article 1er
  (JORFARTI000001483411) : « Le régime de retraite des agents titulaires de
  la Banque de France est fixé à compter du 1er avril 2007 par le règlement
  annexé au présent décret » ; règlement, article 26 a
  (LEGIARTI000006778516) : « au moins l'âge de soixante ans ».
- **Artisans et commerçants d'avant 1973.** Décret n° 73-937, article 3 :
  « à compter de l'âge de soixante ans » jusqu'au 6 octobre 2012
  (LEGIARTI000006765819), « à compter de l'âge prévu par l'article
  L. 161-17-2 » depuis le 7 (LEGIARTI000026474703), le décret n° 2012-1129,
  publié le 6 octobre 2012, entrant en vigueur « le lendemain de sa
  publication ».
- **Cavimac.** Décret n° 2006-1325 du 31 octobre 2006, article 2, I
  (JORFARTI000001085913), publié le 1er novembre 2006 sans date propre :
  l'âge de la pension des périodes d'avant 1998 « est également abaissé à
  soixante ans » depuis le 2 novembre 2006.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.types_du_pont.carriere import Metier

from facade import Carriere, Simulateur, commun, ouvrir

date_d_effet = commun.date_d_effet
periode_de_liquidation = commun.periode_de_liquidation


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur: Simulateur, affiliation: str, naissance: int, mois: int,
              liquidation: float, debut: float = 20.0) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, mois_naissance=mois, jour_naissance=15, sexe="H",
        metiers=[Metier(affiliation=affiliation, age_debut=debut, niveau_salaire=1.0)],
        age_liquidation=liquidation, macro=simulateur.macro,
    )


def _ouverture(simulateur: Simulateur, regime: str, carriere: Carriere) -> float:
    """L'âge d'ouverture que le régime oppose à la date d'effet de la pension."""
    periode = periode_de_liquidation(
        simulateur.catalogue[regime], carriere.date_liquidation)
    return ouvrir.age_ouverture(simulateur.scenario_actuel, periode, carriere)


# -- la Banque de France, le 1er avril 2007 ---------------------------------------


def test_la_banque_de_france_ouvre_a_soixante_ans_des_le_1er_avril_2007(simulateur):
    """Le règlement de 2007 vaut « à compter du 1er avril 2007 » : la pension
    du 1er mars relève encore de l'ancien régime, celle du 1er avril de
    soixante ans. Le dépôt gardait cinquante-cinq ans jusqu'en décembre."""
    mars = _carriere(simulateur, "agent_banque_de_france", 1950, 2, 57.0)
    assert date_d_effet(mars) == "2007-03-01"
    assert _ouverture(simulateur, "banque_de_france", mars) == pytest.approx(55.0)
    avril = _carriere(simulateur, "agent_banque_de_france", 1950, 3, 57.0)
    assert date_d_effet(avril) == "2007-04-01"
    assert _ouverture(simulateur, "banque_de_france", avril) == pytest.approx(60.0)
    decembre = _carriere(simulateur, "agent_banque_de_france", 1950, 11, 57.0)
    assert date_d_effet(decembre) == "2007-12-01"
    assert _ouverture(simulateur, "banque_de_france", decembre) == pytest.approx(60.0)


@pytest.mark.parametrize("mois,effet,requis", [
    # Article 69, I : « Jusqu'au 31 mars 2007. 2e trimestre 2007. 2e semestre
    # 2007. » — « 150 151 152 », à la date où l'agent peut liquider, ici ses
    # soixante ans : le 15 mars, le 15 avril, le 15 août 2007.
    (3, "2007-04-01", 150),
    (4, "2007-05-01", 151),
    (8, "2007-09-01", 152),
])
def test_la_banque_de_france_doit_la_duree_de_son_calendrier_en_2007(
        simulateur, mois, effet, requis):
    carriere = _carriere(simulateur, "agent_banque_de_france", 1947, mois, 60.0)
    assert date_d_effet(carriere) == effet
    resultat = simulateur.scenario_actuel.calculer(carriere)
    assert resultat.trimestres_requis == requis


def test_la_banque_de_france_ne_decote_ni_ne_surcote_les_pensions_de_2007(simulateur):
    """Article 70 : « Jusqu'au 31 décembre 2008. Sans objet » ; article 33 :
    la surcote ne compte que les trimestres « effectués après le 1er avril
    2007 », aucun pour la pension du 1er avril."""
    courte = _carriere(simulateur, "agent_banque_de_france", 1947, 3, 60.0, debut=25.0)
    assert date_d_effet(courte) == "2007-04-01"
    resultat = simulateur.scenario_actuel.calculer(courte)
    assert resultat.trimestres_valides < resultat.trimestres_requis
    assert resultat.taux_liquidation == pytest.approx(0.75)
    longue = _carriere(simulateur, "agent_banque_de_france", 1947, 3, 60.0, debut=20.0)
    assert simulateur.scenario_actuel.calculer(longue).taux_liquidation == pytest.approx(0.75)


# -- les artisans et les commerçants d'avant 1973, le 7 octobre 2012 --------------


@pytest.mark.parametrize("affiliation,regime", [
    ("commercant", "organic_avant_1973"),
    ("artisan", "cancava_avant_1973"),
])
def test_les_droits_d_avant_1973_passent_a_l_age_legal_le_7_octobre_2012(
        simulateur, affiliation, regime):
    """Né en 1952, l'âge de L. 161-17-2 est de soixante ans et neuf mois
    (D. 161-2-1-9, 3°), et celui de L. 351-8, 1°, cinq ans plus tard. La
    pension du 1er octobre 2012 relève encore de « soixante ans » et du
    « soixante-cinquième anniversaire » ; celle du 1er novembre, de la
    rédaction du 7 octobre. Le dépôt gardait l'ancienne jusqu'en décembre."""
    octobre = _carriere(simulateur, affiliation, 1952, 9, 60.0, debut=16.0)
    assert date_d_effet(octobre) == "2012-10-01"
    periode = periode_de_liquidation(simulateur.catalogue[regime], octobre.date_liquidation)
    assert ouvrir.age_ouverture(simulateur.scenario_actuel, periode, octobre) == pytest.approx(60.0)
    assert ouvrir.age_taux_plein(simulateur.scenario_actuel, periode, octobre) == pytest.approx(65.0)

    novembre = _carriere(simulateur, affiliation, 1952, 10, 60.0, debut=16.0)
    assert date_d_effet(novembre) == "2012-11-01"
    periode = periode_de_liquidation(simulateur.catalogue[regime], novembre.date_liquidation)
    assert ouvrir.age_ouverture(simulateur.scenario_actuel, periode, novembre) == pytest.approx(60.75)
    assert ouvrir.age_taux_plein(simulateur.scenario_actuel, periode, novembre) == pytest.approx(65.75)


# -- la Cavimac, le 2 novembre 2006 -----------------------------------------------


def test_la_cavimac_ouvre_a_soixante_ans_des_le_2_novembre_2006(simulateur):
    """Le décret n° 2006-1325, publié le 1er novembre 2006, abaisse « à
    soixante ans » l'âge de la pension des périodes d'avant 1998 : la pension
    du 1er novembre relève encore de soixante-cinq ans (D. 721-6), celle du
    1er décembre de l'âge légal. Le dépôt attendait janvier 2007."""
    novembre = _carriere(simulateur, "ministre_du_culte", 1946, 10, 60.0)
    assert date_d_effet(novembre) == "2006-11-01"
    assert _ouverture(simulateur, "cavimac", novembre) == pytest.approx(65.0)
    decembre = _carriere(simulateur, "ministre_du_culte", 1946, 11, 60.0)
    assert date_d_effet(decembre) == "2006-12-01"
    assert _ouverture(simulateur, "cavimac", decembre) == pytest.approx(60.0)
