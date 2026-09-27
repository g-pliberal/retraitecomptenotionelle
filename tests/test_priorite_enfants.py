"""Un seul régime accorde les trimestres des enfants, et R. 173-15 dit lequel.

Le modèle retenait, parmi les régimes d'une carrière, celui qui accordait le
plus : une fonctionnaire passée par le privé y recevait les huit trimestres par
enfant du régime général, quand la CNRACL lui accorde sa bonification et
qu'elle ne peut pas y renoncer (juris-cnracl, « Règles de coordination avec les
autres régimes » ; TA Amiens, 2 juin 2017, n° 1501559). L'article R. 173-15 du
code de la sécurité sociale (LEGIARTI000034595998, et déjà la version de 1985)
suit un ordre :

1. le RÉGIME SPÉCIAL, « si celui-ci est susceptible d'accorder en vertu de ses
   propres règles une pension à l'intéressé » — c'est-à-dire si elle y a servi
   la durée qu'il exige, que porte ``legislation/services_ouvrant_pension.csv``
   — et si le droit y est ouvert pour ses enfants ;
2. sinon le RÉGIME GÉNÉRAL, prioritaire parmi les régimes alignés ;
3. sans lui, le régime de la dernière affiliation.

La passe du 24 septembre 2026 a lu R. 173-15 dans ses six versions, R. 13 du
code des pensions dans les siennes, L. 4 et R. 4-1, les articles qui fixent la
durée de services de chaque régime spécial, les pages de la CNRACL sur la
coordination et sur la bonification, et les fiches du COR sur la SNCF et la
RATP. Ce fichier tient ce qu'elle a corrigé.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.droit import compter
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur: Simulateur, naissance: int, metiers: list[tuple[str, float]],
              liquidation: float, enfants: int = 2, sexe: str = "F",
              naissances: tuple[str, ...] = ()) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe,
        metiers=[Metier(affiliation=statut, age_debut=debut) for statut, debut in metiers],
        age_liquidation=liquidation, macro=simulateur.macro, nombre_enfants=enfants,
        naissances_enfants=naissances,
    )


def _regimes(simulateur: Simulateur, carriere: Carriere) -> dict[str, int]:
    """Les régimes que la carrière traverse, comme :meth:`calculer` les route."""
    actuel = simulateur.scenario_actuel
    regimes: dict[str, int] = {}
    for ligne in carriere.lignes:
        if ligne.annee > carriere.annee_liquidation:
            continue
        for code in actuel.affiliations.regimes(
                ligne.affiliation, ligne.annee, carriere.date_entree(ligne.affiliation),
                revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
                plafond=actuel.macro.plafond_securite_sociale(ligne.annee)):
            if code in actuel.catalogue:
                regimes[code] = regimes.get(code, 0) + 4
    return regimes


def _majoration(simulateur: Simulateur, naissance: int, metiers: list[tuple[str, float]],
                liquidation: float, **kwargs):
    carriere = _carriere(simulateur, naissance, metiers, liquidation, **kwargs)
    return compter.majoration_pour_enfants(
        simulateur.scenario_actuel, carriere, _regimes(simulateur, carriere), carriere.annee_liquidation)


def _seul(valeurs: list[str]) -> str:
    """Le seul régime, ou le seul dispositif, que portent tous les enfants."""
    (valeur,) = valeurs
    return valeur


def _pension(resultat, regime: str):
    return next(p for p in resultat.pensions_par_regime if p.regime == regime)


# -- la table des durées ------------------------------------------------------

@pytest.mark.parametrize("regime, radiation, en_fonctions, annees", [
    # L. 4 du code des pensions, puis R. 4-1 pour les radiés depuis 2011.
    ("fonction_publique_etat", "2010-12-01", False, 15),
    ("fonction_publique_etat", "2011-01-01", False, 2),
    ("cnracl", "2010-01-01", False, 15),
    ("cnracl", "2026-09-01", False, 2),
    ("fspoeie", "2011-01-01", False, 2),
    # Les réformes de 2008 : un an pour qui part depuis le 1er juillet.
    ("sncf", "2008-06-01", False, 15),
    ("sncf", "2008-07-01", False, 1),
    ("ratp", "2008-07-01", False, 1),
    ("ieg", "2000-01-01", False, 15),
    ("ieg", "2009-01-01", False, 1),
    ("opera_de_paris", "2009-01-01", False, 1),
    ("comedie_francaise", "2009-01-01", False, 0),
    # La Banque de France n'exige plus rien depuis le 9 mai 2012.
    ("banque_de_france", "2012-05-01", False, 15),
    ("banque_de_france", "2012-06-01", False, 0),
    # La SEITA : quinze ans pour partir avant l'âge, rien à qui l'atteint en
    # fonctions (articles 112 et 110 du décret n° 62-766).
    ("seita", "1990-01-01", False, 15),
    ("seita", "1990-01-01", True, 0),
    # La pension spéciale des marins ne demande aucune durée.
    ("marins", "2020-01-01", False, 0),
])
def test_la_table_porte_la_duree_de_chaque_texte(simulateur, regime, radiation,
                                                  en_fonctions, annees):
    table = simulateur.scenario_actuel.services_ouvrant_pension
    exigees, _ = table.annees(regime, radiation, en_fonctions)
    assert exigees == annees


def test_un_regime_absent_de_la_table_n_y_est_pas_invente(simulateur):
    """Le port de Strasbourg n'est pas dans l'index : la table se tait, et le
    moteur présume la pension possible au niveau ``estimee``."""
    table = simulateur.scenario_actuel.services_ouvrant_pension
    assert table.annees("port_strasbourg", "2020-01-01", False) is None
    # Les deux lignes tirées des fiches du COR, non d'un texte lu, le disent.
    assert table.annees("sncf", "2000-01-01", False)[1] == Fiabilite.MOYENNE
    assert table.annees("ratp", "2000-01-01", False)[1] == Fiabilite.MOYENNE


# -- le régime spécial d'abord ------------------------------------------------

def test_la_fonctionnaire_passee_au_prive_garde_sa_bonification(simulateur):
    """Vingt-huit ans à l'État, puis le privé jusqu'à soixante-quatre ans : la
    bonification de l'État, quatre trimestres par enfant né avant 2004, et non
    les huit de la MDA du régime général, que le modèle lui servait. Moins
    favorable, et c'est le droit : l'agent ne peut pas y renoncer."""
    carriere = _carriere(simulateur, 1962, [("fonctionnaire_etat", 22),
                                            ("salarie_prive_non_cadre", 50)], 64)
    actuel = simulateur.scenario_actuel
    majoration = compter.majoration_pour_enfants(
        actuel, carriere, _regimes(simulateur, carriere), carriere.annee_liquidation)
    assert (_seul(majoration.regimes), _seul(majoration.dispositifs)) == ("fonction_publique_etat",
                                                          "bonifications")
    assert (majoration.trimestres, majoration.services) == (8, 8)
    # Le régime général en aurait accordé deux fois plus.
    mda = actuel.majorations_enfants.par_enfant("mda", "F", "1992-01-01", "2026-01-01",
                                                 ["1992-01-01", "1992-01-01"])
    assert mda.trimestres * 2 == 16 > majoration.trimestres
    resultat = actuel.calculer(carriere)
    assert _pension(resultat, "fonction_publique_etat").detail.endswith("× 120/169")
    assert _pension(resultat, "regime_general").detail.endswith("× 56/169")


def test_deux_ans_de_services_suffisent_depuis_2011(simulateur):
    """Deux années à l'État, de 2010 à 2011, radiée au 1er janvier 2012 : R. 4-1
    lui ouvre une pension, et c'est donc l'État qui accorde."""
    majoration = _majoration(simulateur, 1962, [
        ("salarie_prive_non_cadre", 22), ("fonctionnaire_etat", 48),
        ("salarie_prive_non_cadre", 50)], 64)
    assert _seul(majoration.regimes) == "fonction_publique_etat"


@pytest.mark.parametrize("metiers", [
    # Une année à l'État en 2010 : moins des deux ans de R. 4-1.
    [("salarie_prive_non_cadre", 22), ("fonctionnaire_etat", 48),
     ("salarie_prive_non_cadre", 49)],
    # Treize ans, radiée au 1er janvier 2009 : moins des quinze ans de L. 4.
    [("salarie_prive_non_cadre", 22), ("fonctionnaire_etat", 34),
     ("salarie_prive_non_cadre", 47)],
])
def test_sans_la_duree_le_regime_general_accorde(simulateur, metiers):
    """Le régime spécial qui ne peut pas pensionner rétablit l'agent au régime
    général : c'est lui qui accorde, et ses huit trimestres par enfant."""
    majoration = _majoration(simulateur, 1962, metiers, 64)
    assert (_seul(majoration.regimes), _seul(majoration.dispositifs)) == ("regime_general", "mda")
    assert majoration.trimestres == 16


def test_la_sncf_quittee_avant_juillet_2008_sans_quinze_ans(simulateur):
    """Treize ans à la SNCF, partie en 1997 : le règlement d'alors exigeait
    quinze ans, et c'est le régime général qui accorde. La même agente partie
    en 2015 après cinq ans a sa pension proportionnelle (article 3 du décret
    n° 2008-639) : la SNCF accorde."""
    avant = _majoration(simulateur, 1962, [("agent_sncf", 22),
                                           ("salarie_prive_non_cadre", 35)], 64)
    assert _seul(avant.regimes) == "regime_general"
    # La ligne d'avant 2008 vient de la fiche du COR : le résultat le dit.
    assert avant.fiabilite == Fiabilite.MOYENNE
    apres = _majoration(simulateur, 1970, [
        ("salarie_prive_non_cadre", 22), ("agent_sncf", 40),
        ("salarie_prive_non_cadre", 45)], 64)
    assert (_seul(apres.regimes), _seul(apres.dispositifs)) == ("sncf", "bonifications")


@pytest.mark.parametrize("fin_seita, regime", [(60, "seita"), (58, "regime_general")])
def test_la_seita_ne_demande_rien_a_qui_part_en_fonctions(simulateur, fin_seita, regime):
    """Douze ans à la SEITA jusqu'à soixante ans : l'article 110 ouvre la
    pension sans durée. Partie à cinquante-huit ans après dix ans, il lui en
    fallait quinze (article 112)."""
    metiers = [("salarie_prive_non_cadre", 22), ("agent_seita", 48)]
    if fin_seita < 60:
        metiers.append(("salarie_prive_non_cadre", fin_seita))
    assert _seul(_majoration(simulateur, 1930, metiers, 60).regimes) == regime


def test_entre_deux_regimes_speciaux_le_dernier_servi(simulateur):
    majoration = _majoration(simulateur, 1962, [
        ("fonctionnaire_territorial_hospitalier", 22), ("fonctionnaire_etat", 40)], 64)
    assert _seul(majoration.regimes) == "fonction_publique_etat"


# -- le droit ouvert ----------------------------------------------------------

def test_l_enfant_ne_depuis_2004_avant_le_recrutement(simulateur):
    """Recrutée à quarante ans, en 2020, mère d'enfants que le modèle fait
    naître en 2010 : L. 12 bis ne sert que les femmes « ayant accouché
    postérieurement à leur recrutement ». Le droit est fermé à l'État, et le
    régime général accorde — au niveau ``moyenne``, puisque tout se joue sur la
    date de naissance que le modèle prête aux enfants."""
    majoration = _majoration(simulateur, 1980, [("salarie_prive_non_cadre", 22),
                                                ("fonctionnaire_etat", 40)], 64)
    assert (_seul(majoration.regimes), majoration.trimestres) == ("regime_general", 16)
    assert majoration.fiabilite == Fiabilite.MOYENNE


@pytest.mark.parametrize("naissance, liquidation, regime", [
    # Jusqu'en 2003, la bonification vaut pour chacun des enfants.
    (1940, 62, "fonction_publique_etat"),
    # De 2004 à 2010, R. 13 n'admet que les congés du statut : l'enfant né en
    # 1975, avant le recrutement de 1980, n'ouvre rien.
    (1945, 62, "regime_general"),
    # Depuis 2011, le congé de maternité du code de la sécurité sociale
    # suffit : le même enfant ouvre la bonification.
    (1945, 66, "fonction_publique_etat"),
])
def test_l_enfant_ne_avant_2004_selon_la_version_de_r13(simulateur, naissance,
                                                        liquidation, regime):
    majoration = _majoration(simulateur, naissance, [
        ("salarie_prive_non_cadre", 22), ("fonctionnaire_etat", 35)], liquidation)
    assert _seul(majoration.regimes) == regime


def test_l_enfant_ne_apres_la_radiation(simulateur):
    """Un an à l'État à vingt-deux ans, des enfants à trente : nés après la
    radiation, ils n'ouvrent pas la bonification (juris-cnracl)."""
    carriere = _carriere(simulateur, 1962, [("fonctionnaire_etat", 22),
                                            ("salarie_prive_non_cadre", 23)], 64)
    actuel = simulateur.scenario_actuel
    periode = actuel.catalogue["fonction_publique_etat"].periode(2026)
    pension, ouvert, _ = compter.droit_regime_special(
        actuel, periode, carriere, 2026, "ne_avant_radiation", 1992)
    assert not ouvert and not pension


# -- les régimes alignés ------------------------------------------------------

def test_le_regime_general_passe_avant_le_regime_des_artisans(simulateur):
    """Vingt-huit ans d'artisanat, douze de salariat, liquidés en 2012 — avant
    la liquidation unique, qui ne vaut qu'à partir de la génération 1953 :
    R. 173-15 donne la majoration au régime général, là où le modèle la
    donnait au régime qui comptait le plus de trimestres."""
    majoration = _majoration(simulateur, 1950, [("artisan", 22),
                                                ("salarie_prive_non_cadre", 50)], 62)
    assert _seul(majoration.regimes) == "regime_general"


def test_sans_regime_general_le_regime_de_la_derniere_affiliation(simulateur):
    majoration = _majoration(simulateur, 1950, [("salarie_agricole", 22),
                                                ("artisan", 40)], 62)
    assert _seul(majoration.regimes) == "rsi"


def test_une_carriere_d_un_seul_regime_ne_bouge_pas(simulateur):
    """Le cas ordinaire : une fonctionnaire de toute une carrière, une salariée
    du privé. Rien ne change pour elles."""
    fonctionnaire = _majoration(simulateur, 1962, [("fonctionnaire_etat", 22)], 64)
    assert (_seul(fonctionnaire.regimes), fonctionnaire.trimestres) == ("fonction_publique_etat", 8)
    salariee = _majoration(simulateur, 1962, [("salarie_prive_non_cadre", 22)], 64)
    assert (_seul(salariee.regimes), salariee.trimestres) == ("regime_general", 16)


# -- chaque enfant compte à sa date -------------------------------------------
#
# Le domaine « les dates des enfants » (docs/architecture.md, § 11) : la
# priorité se lit enfant par enfant. Le régime général est compétent « si un ou
# plusieurs enfants n'ouvrent pas droit à majoration » dans le régime spécial
# (circulaire Cnav 2017-01, fiches n° 6.2a et 6.2b, point 3 « Compétence »).

def test_l_enfant_ne_avant_le_recrutement_compte_au_regime_general(simulateur):
    """Salariée à vingt-deux ans, fonctionnaire à trente, en 2010 : l'enfant
    né en 2006 précède son recrutement, et L. 12 bis ne va qu'à la femme qui a
    accouché après ; le régime général lui sert ses huit trimestres. L'enfant
    né en 2012 ouvre la majoration de l'État : deux trimestres, dont un de
    services depuis le b ter."""
    majoration = _majoration(simulateur, 1980, [("salarie_prive_non_cadre", 22),
                                                ("fonctionnaire_etat", 30)], 64,
                             naissances=("2006", "2012"))
    assert [(e.enfant, e.regime, e.version, e.trimestres, e.services)
            for e in majoration.enfants] == [
        ("enfant_1", "regime_general", "mda_2010_nes_avant", 8, 8),
        ("enfant_2", "fonction_publique_etat", "l12bter", 2, 1)]
    assert majoration.par_regime() == {"regime_general": (8, 8),
                                       "fonction_publique_etat": (2, 1)}
    assert majoration.dispositifs == ["mda", "bonifications"]


def test_deux_enfants_de_part_et_d_autre_de_2004(simulateur):
    """Une fonctionnaire de toute une carrière : l'enfant né en 1999 reçoit la
    bonification de L. 12 b, un an en services ; celui né en 2006, la
    majoration de L. 12 bis. La présomption, qui les faisait naître la même
    année, ne savait servir que l'une ou l'autre aux deux."""
    majoration = _majoration(simulateur, 1970, [("fonctionnaire_etat", 22)], 64,
                             naissances=("1999-05", "2006-02"))
    assert [(e.version, e.trimestres, e.services) for e in majoration.enfants] == [
        ("l12b_2011", 4, 4), ("l12bter", 2, 1)]
    assert (majoration.trimestres, majoration.services) == (6, 5)


def test_un_enfant_ne_apres_la_date_d_effet_n_ouvre_rien(simulateur):
    """Le vocabulaire tient pour impossible un enfant né après la date d'effet
    de la pension (§ 4.2) : le moteur ne lui compte rien, et compte les
    autres. La date d'effet est prise en 2011, où aucune version n'exige plus
    un âge de l'enfant : de 1972 à 2003, l'enfant d'un an n'aurait rien ouvert
    pour une autre raison, n'ayant pas été élevé neuf ans."""
    carriere = _carriere(simulateur, 1962, [("salarie_prive_non_cadre", 22)], 64,
                         naissances=("1990", "2012"))
    avant = compter.majoration_pour_enfants(
        simulateur.scenario_actuel, carriere, _regimes(simulateur, carriere),
        carriere.annee_liquidation)
    apres = compter.majoration_pour_enfants(
        simulateur.scenario_actuel, carriere, _regimes(simulateur, carriere), 2011)
    assert [e.enfant for e in avant.enfants] == ["enfant_1", "enfant_2"]
    assert [e.enfant for e in apres.enfants] == ["enfant_1"]


def test_la_liquidation_nomme_les_deux_regimes(simulateur):
    """L'avantage que la cascade mesure dit les deux dispositifs et les deux
    régimes, quand les enfants en relèvent de deux."""
    carriere = _carriere(simulateur, 1980, [("salarie_prive_non_cadre", 22),
                                            ("fonctionnaire_etat", 30)], 64,
                         naissances=("2006", "2012"))
    resultat = simulateur.scenario_actuel.calculer(carriere)
    avantage = next(a for a in resultat.avantages_appliques
                    if a.code == "majoration_duree_assurance")
    assert avantage.libelle == ("Majoration de durée d'assurance et bonification "
                                "pour enfants")
    assert avantage.detail.endswith("au titre des régimes « regime_general » et "
                                    "« fonction_publique_etat »")


def test_une_condition_inconnue_arrete_le_moteur():
    """Une version qui pose à l'enfant une condition que le moteur ne connaît
    pas l'arrête, plutôt que de la traiter en silence comme une autre (§ 6.7)."""
    assert compter.bonification_ouverte("tout_enfant", 1990, 2000, 2010)
    with pytest.raises(ValueError, match="condition inconnue"):
        compter.bonification_ouverte("ne_un_dimanche", 1990, 2000, 2010)
