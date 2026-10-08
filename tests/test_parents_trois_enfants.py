"""Le départ anticipé du fonctionnaire parent de trois enfants.

Action 138, étape 17 : Destinie 2 ouvre la liquidation anticipée de la mère
fonctionnaire de trois enfants qui a quinze ans de services avant 2012, avec la
durée et la décote de l'année des conditions si elle était à moins de cinq ans
de son âge d'ouverture en 2011, celles de sa génération sinon ; le dépôt ne
servait ce départ à personne (registre, 138.17). Fiche
``depart_anticipe_parents_trois_enfants``.

Le code des pensions sert la pension, à tout âge, au fonctionnaire parent de
trois enfants qui a quinze ans de services (L. 24, I, 3°), à la durée et au
barème de décote de l'« Année au cours de laquelle sont réunies les conditions »
(loi n° 2003-775, article 66, II et III). La loi du 9 novembre 2010 n'en garde
le bénéfice qu'à qui les réunit avant 2012, et retient alors l'année de ses
soixante ans, ou de l'âge de sa catégorie active (article 44, III et IV) — sauf
à qui l'avait demandé avant 2011 pour partir au plus tard le 1er juillet 2011,
et à qui était à moins de cinq ans de son âge d'ouverture au 1er janvier 2011,
qui gardent l'ancien calcul et l'ancien minimum garanti.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import ouvrir
from retraite_notionnelle.simulateur import Simulateur

ETAT = "fonctionnaire_etat"
HOSPITALIERE_ACTIVE = "fonctionnaire_hospitalier_actif"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur: Simulateur, naissance: int, debut: float, liquidation: float,
              naissances: tuple[str, ...], sexe: str = "F", statut: str = ETAT,
              salaire: float = 1.0) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe, metiers=[Metier(statut, debut, salaire)],
        age_liquidation=liquidation, macro=simulateur.macro, mois_naissance=1,
        part_primes=0.15, nombre_enfants=len(naissances), naissances_enfants=naissances)


def _depart(simulateur: Simulateur, carriere: Carriere, regime: str = "fonction_publique_etat"):
    actuel = simulateur.scenario_actuel
    periode = actuel.catalogue[regime].periode(carriere.annee_liquidation)
    return ouvrir.depart_parent_trois_enfants(actuel, periode, carriere)


def _pension(simulateur: Simulateur, carriere: Carriere, regime: str = "fonction_publique_etat"):
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return resultat, {p.regime: p for p in resultat.pensions_par_regime}[regime]


def test_la_mere_partie_a_cinquante_ans_en_2000_a_150_trimestres_sans_decote(simulateur):
    """Née en 1950, fonctionnaire de l'État depuis 1975, trois enfants de 1976 à
    1981 : ses quinze ans de services, en décembre 1989, réunissent les
    conditions. Partie à cinquante ans, en 2000, son droit est ouvert ; la
    durée est celle d'avant 2004, 150 trimestres, sans décote. Le premier cas
    de Destinie 2 : l'ouverture à la date des conditions."""
    carriere = _carriere(simulateur, 1950, 25.0, 50.0, ("1976", "1978", "1981"))
    depart = _depart(simulateur, carriere)
    assert depart is not None
    assert (depart.annee_des_parametres, depart.ancien_calcul, depart.version) == (
        1989, True, "code_de_1982")
    assert depart.age_ouverture == pytest.approx(39 + 10 / 12)
    resultat, pension = _pension(simulateur, carriere)
    assert (resultat.motif_ouverture, resultat.liquidation_ouverte) == ("age_legal", True)
    assert resultat.trimestres_requis == 150
    assert "× taux 75.000% × 112/150" in pension.detail


def test_le_pere_n_y_a_rien(simulateur):
    """La même carrière, au père : l'interruption d'activité pour chaque enfant
    est présumée de la mère seule, et le départ à cinquante ans n'est pas
    ouvert."""
    carriere = _carriere(simulateur, 1950, 25.0, 50.0, ("1976", "1978", "1981"), sexe="H")
    assert _depart(simulateur, carriere) is None
    resultat, _ = _pension(simulateur, carriere)
    assert (resultat.motif_ouverture, resultat.liquidation_ouverte) == ("non_ouverte", False)


def test_l_ancien_calcul_garde_la_duree_et_la_decote_de_l_annee_des_conditions(simulateur):
    """Née en 1955, entrée à trente-huit ans, ses quinze ans en décembre 2007 :
    au 1er janvier 2011, elle était à moins de cinq ans de soixante ans, et
    garde la durée et la décote de 2007 — 158 trimestres, 0,25 % par
    trimestre, l'âge d'annulation à la limite d'âge moins quatorze trimestres
    —, partie à cinquante-six ans en 2011. Le deuxième cas de Destinie 2, qui
    ne lui sert pourtant aucune décote."""
    carriere = _carriere(simulateur, 1955, 38.0, 56.0, ("1980", "1982", "1985"))
    depart = _depart(simulateur, carriere)
    assert (depart.annee_des_parametres, depart.ancien_calcul) == (2007, True)
    resultat, pension = _pension(simulateur, carriere)
    assert resultat.liquidation_ouverte
    assert resultat.trimestres_requis == 158
    assert "× taux 71.250% ×" in pension.detail


def test_le_nouveau_calcul_prend_l_annee_des_soixante_ans(simulateur):
    """Née en 1965, ses conditions réunies en 2002, partie à cinquante ans en
    2015 : ni à moins de cinq ans de soixante ans en 2011, ni partie avant
    juillet 2011, elle a la durée et la décote de 2025, l'année de ses soixante
    ans — 169 trimestres, ceux de la génération 1965 avant la loi du 14 avril
    2023, et vingt trimestres de décote à 1,25 %. Le troisième cas de Destinie
    2 : la durée de la génération."""
    carriere = _carriere(simulateur, 1965, 23.0, 50.0, ("1990", "1992", "1995"))
    depart = _depart(simulateur, carriere)
    assert (depart.annee_des_parametres, depart.ancien_calcul) == (2025, False)
    resultat, pension = _pension(simulateur, carriere)
    assert (resultat.motif_ouverture, resultat.liquidation_ouverte) == ("age_legal", True)
    assert resultat.trimestres_requis == 169
    assert "× taux 56.250% ×" in pension.detail


@pytest.mark.parametrize(("liquidation", "ancien"), [(50 + 5 / 12, True), (50.5, False)])
def test_la_pension_de_juillet_2011_garde_l_ancien_calcul_celle_d_aout_non(
        simulateur, liquidation, ancien):
    """Née en janvier 1961, sédentaire : à plus de cinq ans de soixante ans au
    1er janvier 2011. Partie en juillet 2011, sa demande est présumée faite
    avant 2011 (IV, 1°) et l'ancien calcul demeure ; partie en août, non."""
    carriere = _carriere(simulateur, 1961, 22.0, liquidation, ("1984", "1986", "1988"))
    assert carriere.date_liquidation.mois == (7 if ancien else 8)
    depart = _depart(simulateur, carriere)
    assert depart.ancien_calcul is ancien
    assert depart.annee_des_parametres == (1997 if ancien else 2021)


def test_l_active_garde_l_ancien_calcul_jusqu_a_1960_et_l_age_de_57_ans_ensuite(simulateur):
    """L'hospitalière active née en 1966 n'était pas à moins de cinq ans de
    cinquante-cinq ans en 2011 : partie à cinquante ans en 2016, elle a la
    durée de l'année de ses cinquante-sept ans (article 22 de la loi), 2023,
    168 trimestres. Née en 1960, elle y était, et garde l'année de ses
    conditions."""
    jeune = _carriere(simulateur, 1966, 22.0, 50.0, ("1989", "1991", "1994"),
                      statut=HOSPITALIERE_ACTIVE)
    depart = _depart(simulateur, jeune, "cnracl")
    assert (depart.annee_des_parametres, depart.ancien_calcul) == (2023, False)
    resultat, _ = _pension(simulateur, jeune, "cnracl")
    assert resultat.trimestres_requis == 168
    ainee = _carriere(simulateur, 1960, 22.0, 52.0, ("1983", "1985", "1987"),
                      statut=HOSPITALIERE_ACTIVE)
    depart = _depart(simulateur, ainee, "cnracl")
    assert (depart.annee_des_parametres, depart.ancien_calcul) == (1996, True)


@pytest.mark.parametrize("naissances", [("1988", "1990", "2012-02"), ("2001", "2003", "2005")])
def test_les_conditions_se_reunissent_avant_2012(simulateur, naissances):
    """Le troisième enfant né en février 2012, ou les quinze ans de services
    atteints en décembre 2014 (entrée à vingt-cinq ans en 2000) : rien."""
    naissance, debut = (1962, 25.0) if naissances[-1] == "2012-02" else (1975, 25.0)
    carriere = _carriere(simulateur, naissance, debut, 50.0, naissances)
    assert _depart(simulateur, carriere) is None
    resultat, _ = _pension(simulateur, carriere)
    assert not resultat.liquidation_ouverte


def test_l_ancien_calcul_garde_le_minimum_garanti_sans_condition(simulateur):
    """L'ancien calcul garde l'article L. 17 d'avant la loi de 2010 : la mère
    née en 1955, décotée, a le minimum garanti ; celle née en 1965, décotée
    sans avoir sa durée ni l'âge d'annulation, ne l'a pas."""
    ancien = _carriere(simulateur, 1955, 38.0, 56.0, ("1980", "1982", "1985"), salaire=0.4)
    _, pension = _pension(simulateur, ancien)
    assert "porté au minimum garanti" in pension.detail
    nouveau = _carriere(simulateur, 1965, 23.0, 50.0, ("1990", "1992", "1995"), salaire=0.4)
    _, pension = _pension(simulateur, nouveau)
    assert "porté au minimum garanti" not in pension.detail


def test_un_militaire_n_y_a_rien(simulateur):
    """La pension militaire s'ouvre à sa durée de services : le départ du
    parent de trois enfants n'est pas servi au militaire (approximation de la
    fiche)."""
    carriere = _carriere(simulateur, 1960, 20.0, 45.0, ("1984", "1986", "1988"),
                         statut="militaire")
    assert _depart(simulateur, carriere) is None
