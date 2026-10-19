"""La limite d'âge des agents publics et ses exceptions (action 151, étapes 3
et 4 ;
fiches ``limite_age_fonction_publique``, ``limite_age_militaires``,
``recul_limite_age_enfants``, ``prolongation_activite_carriere_incomplete``,
``prolongation_activite_categorie_active``,
``maintien_en_fonctions_jusqu_a_70_ans`` et
``plafond_limite_age_fonction_publique``).

Le fonctionnaire dont le départ saisi passe sa limite d'âge est radié des
cadres à la limite, reculée de droit pour ses enfants, et prolongée — présumée
demandée et accordée autant que le départ le demande — pour carrière
incomplète, pour l'actif jusqu'à la limite des sédentaires, et pour le
sédentaire jusqu'à soixante-dix ans ; sa pension part de ce jour, et ce qui
suit n'est plus du service. Le militaire prend la limite la plus haute de sa
catégorie. Le portage JavaScript se compare par les témoins de simulation
(``limite_age_*``, ``scripts/construire_temoins.py``).
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import departs, limite_age
from retraite_notionnelle.noyau import carte
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _simple(simulateur: Simulateur, statut: str, naissance: int, depart: float,
            **kwargs) -> Carriere:
    """Un assuré né le 15 de son mois, que le test déclare au lieu de le
    présumer (action 135, levier 2) : né un 1er, ses âges se compteraient du
    mois de sa naissance (R. 351-37), et chaque date racontée reculerait d'un
    mois."""
    kwargs.setdefault("jour_naissance", 15)
    return simulateur.carriere_simple(naissance, "H", statut, 22, depart, **kwargs)


def _reculs(radiation) -> list[tuple[str, float, float, bool]]:
    return [(r.nom, r.depuis, round(r.jusqu_a, 4), r.presumee) for r in radiation.reculs]


def test_le_sedentaire_est_maintenu_jusqu_a_soixante_dix_ans_puis_radie(simulateur):
    """Né en 1990, il atteint soixante-sept ans en 2057 : le maintien de L.
    556-1, que le départ à soixante-quinze ans demande, est présumé accordé, et
    il est radié à soixante-dix ans, sa pension partant de ce jour."""
    moteur = simulateur.scenario_actuel
    carriere = _simple(simulateur, "fonctionnaire_etat", 1990, 75)
    radiation = limite_age.radiation(moteur, carriere)
    assert (radiation.limite, radiation.age, radiation.version) == (67.0, 70.0, "reforme_2023")
    assert radiation.forcee and radiation.date == carriere.date_de_l_age(70)
    assert _reculs(radiation) == [(limite_age.MAINTIEN, 67.0, 70.0, True)]
    assert [(d.date, sorted(d.regimes), d.motif) for d in departs.departs(moteur, carriere)] \
        == [(radiation.date, ["fonction_publique_etat"], departs.MOTIF_LIMITE)]


def test_la_pension_radiee_ne_compte_pas_les_services_d_apres_la_limite(simulateur):
    """Partir à soixante-quinze ou à quatre-vingt-dix ans sert la pension d'un
    départ à soixante-dix : les services s'arrêtent à la radiation."""
    moteur = simulateur.scenario_actuel

    def a_l_effet(depart: float) -> float:
        resultat = moteur.calculer(_simple(simulateur, "fonctionnaire_etat", 1990, depart))
        return sum(p.montant_a_l_effet or p.montant for p in resultat.pensions_par_regime)

    assert a_l_effet(75) == pytest.approx(a_l_effet(70))
    assert a_l_effet(90) == pytest.approx(a_l_effet(70))
    assert a_l_effet(69) < a_l_effet(70)


def test_avant_la_limite_rien_ne_change(simulateur):
    moteur = simulateur.scenario_actuel
    for depart in (62, 67):
        carriere = _simple(simulateur, "fonctionnaire_etat", 1990, depart)
        assert limite_age.radiation(moteur, carriere) is None
        assert limite_age.radier(moteur, carriere) is carriere


def test_le_maintien_n_est_presume_que_jusqu_au_depart(simulateur):
    """Parti à soixante-neuf ans, le sédentaire n'est pas radié par la limite :
    le maintien présumé le garde jusqu'à son départ, qui date sa pension."""
    moteur = simulateur.scenario_actuel
    carriere = _simple(simulateur, "fonctionnaire_etat", 1990, 69)
    radiation = limite_age.radiation(moteur, carriere)
    assert not radiation.forcee and radiation.age == 69.0
    assert _reculs(radiation) == [(limite_age.MAINTIEN, 67.0, 69.0, True)]
    assert departs.departs(moteur, carriere)[0].unique


def test_le_policier_est_prolonge_jusqu_a_la_limite_des_sedentaires(simulateur):
    """Cinquante-sept ans pour la police (L. 556-8), la prolongation pour
    carrière incomplète, dix trimestres, puis celle de l'actif jusqu'à
    soixante-sept ans (L. 556-7) ; pas de maintien jusqu'à soixante-dix."""
    moteur = simulateur.scenario_actuel
    radiation = limite_age.radiation(moteur, _simple(simulateur, "policier", 1990, 75))
    assert (radiation.classe, radiation.limite, radiation.age) == (
        limite_age.POLICE_PENITENTIAIRE, 57.0, 67.0)
    assert _reculs(radiation) == [
        (limite_age.CARRIERE_INCOMPLETE, 57.0, 59.5, True),
        (limite_age.PROLONGATION_ACTIVE, 59.5, 67.0, True)]


def test_le_parent_de_trois_enfants_a_un_an_de_droit(simulateur):
    """Trois enfants nés à ses trente ans, présumés : aucun n'est à charge à
    soixante-sept ans, mais il en avait trois vivants à cinquante, et son
    recul est de droit ; le maintien le mène ensuite jusqu'à soixante-dix ans,
    sans le dépasser (L. 556-1)."""
    moteur = simulateur.scenario_actuel
    carriere = _simple(simulateur, "fonctionnaire_etat", 1990, 75, nombre_enfants=3)
    radiation = limite_age.radiation(moteur, carriere)
    assert radiation.age == 70.0
    assert _reculs(radiation) == [
        (limite_age.RECUL_PARENT_DE_TROIS, 67.0, 68.0, False),
        (limite_age.MAINTIEN, 68.0, 70.0, True)]
    assert [r.nom for r in radiation.presumees] == [limite_age.MAINTIEN]


def test_un_enfant_a_charge_recule_la_limite_d_un_an(simulateur):
    """Un enfant de seize ans quand la limite est atteinte : un an de droit."""
    moteur = simulateur.scenario_actuel
    carriere = Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F", metiers=[Metier("fonctionnaire_etat", 22.0)],
        age_liquidation=75, macro=simulateur.macro, nombre_enfants=1,
        naissances_enfants=("2011-05-01",))
    radiation = limite_age.radiation(moteur, carriere)
    assert _reculs(radiation)[0] == (limite_age.RECUL_ENFANTS, 67.0, 68.0, False)


def test_avant_2023_le_sedentaire_est_radie_a_sa_limite(simulateur):
    """Né en 1952, sa limite est soixante-cinq ans et neuf mois (loi n°
    2010-1330, article 28) : en 2017, aucun maintien jusqu'à soixante-dix ans,
    et sa carrière complète n'ouvre aucune prolongation."""
    moteur = simulateur.scenario_actuel
    radiation = limite_age.radiation(moteur, _simple(simulateur, "fonctionnaire_etat", 1952, 70))
    assert (radiation.limite, radiation.age, radiation.version, radiation.reculs) == (
        65.75, 65.75, "loi_de_2010", ())


def test_la_loi_de_1975_ramene_la_limite_a_soixante_huit_ans(simulateur):
    """Né en 1912, le sédentaire du corps le plus haut, soixante-dix ans avant
    1976, atteint en 1980 la limite de soixante-huit ans (loi n° 75-1280)."""
    moteur = simulateur.scenario_actuel
    radiation = limite_age.radiation(moteur, _simple(simulateur, "fonctionnaire_etat", 1912, 72))
    assert (radiation.age, radiation.version) == (68.0, "loi_de_1975")


def test_le_militaire_prend_la_limite_la_plus_haute_de_sa_categorie(simulateur):
    """Cinquante-neuf ans pour le non-officier, soixante-six pour l'officier
    (L. 4139-16), deux de moins avant la loi de 2010, et aucun recul."""
    moteur = simulateur.scenario_actuel
    for statut, naissance, attendue in (("militaire", 1990, 59.0),
                                        ("militaire_officier", 1990, 66.0),
                                        ("militaire_officier", 1940, 64.0)):
        radiation = limite_age.radiation(moteur, _simple(simulateur, statut, naissance, 75))
        assert (radiation.age, radiation.reculs) == (attendue, ()), statut


def test_le_metier_d_apres_la_radiation_part_au_depart_saisi(simulateur):
    """Né le 15 janvier 1990, fonctionnaire jusqu'à soixante-douze ans, puis
    salarié : radié à soixante-dix ans, il touche sa pension de fonctionnaire
    dès lors, et celle du régime général à son départ, à soixante-quinze ans.
    Les années de fonctionnaire d'après la radiation ne sont plus du service."""
    moteur = simulateur.scenario_actuel
    carriere = Carriere.depuis_parcours(
        annee_naissance=1990, mois_naissance=1, jour_naissance=15, sexe="H",
        age_liquidation=75, macro=simulateur.macro,
        metiers=[Metier("fonctionnaire_etat", 22.0), Metier("salarie_prive_non_cadre", 72.0)])
    radiation = limite_age.radiation(moteur, carriere)
    assert radiation.forcee and radiation.age == 70.0
    liste = departs.departs(moteur, carriere)
    assert [(d.date, d.motif) for d in liste] == [
        (radiation.date, departs.MOTIF_LIMITE), (carriere.date_liquidation, departs.MOTIF_DEPART)]
    radiee = limite_age.radier(moteur, carriere)
    fonctionnaire = [l.annee for l in radiee.lignes if l.affiliation == "fonctionnaire_etat"]
    assert max(fonctionnaire) == radiation.date.annee
    assert any(l.affiliation == "salarie_prive_non_cadre" for l in radiee.lignes)


def test_radier_est_idempotent(simulateur):
    moteur = simulateur.scenario_actuel
    carriere = _simple(simulateur, "fonctionnaire_etat", 1990, 80,
                       mois_naissance=1, jour_naissance=15)
    radiee = limite_age.radier(moteur, carriere)
    assert radiee is not carriere
    assert max(l.annee for l in radiee.lignes) == 2060
    assert limite_age.radier(moteur, radiee) is radiee
    assert limite_age.radiation(moteur, radiee).date == DateMois(2060, 2)
    assert limite_age.radiation(moteur, radiee).forcee


def test_les_statuts_sans_limite_au_modele_n_en_ont_pas(simulateur):
    """Le salarié, l'agent des IEG, le cheminot, l'agent de la Banque de France
    et le mineur recrutés depuis la fermeture de leur régime spécial, salariés
    de droit commun, ne sont pas radiés, ni les régimes spéciaux dont le statut
    n'est pas lu ou n'a pas de limite (étape 6)."""
    moteur = simulateur.scenario_actuel
    for statut, naissance in (("salarie_prive_non_cadre", 1990), ("agent_ieg", 2005),
                              ("agent_sncf", 2000), ("agent_banque_de_france", 2005),
                              ("clerc_de_notaire", 1960), ("mineur", 1995), ("marin", 1990),
                              ("personnel_comedie_francaise", 1990),
                              ("agent_port_strasbourg", 1990)):
        carriere = _simple(simulateur, statut, naissance, 75)
        assert limite_age.radiation(moteur, carriere) is None, statut


# --- Action 151, étape 4 : les contractuels, les ouvriers de l'État, la SNCF
# et la RATP (fiches ``limite_age_contractuels``, ``limite_age_ouvriers_etat``
# et ``limite_age_sncf_ratp``).

def test_le_contractuel_est_maintenu_jusqu_a_soixante_dix_ans(simulateur):
    """L. 556-11 : soixante-sept ans, et, depuis le 14 juin 2023, le maintien
    sur autorisation jusqu'à soixante-dix ans ; ses pensions du régime général
    et de l'Ircantec partent de la fin du contrat."""
    moteur = simulateur.scenario_actuel
    carriere = _simple(simulateur, "contractuel_public", 1990, 75)
    radiation = limite_age.radiation(moteur, carriere)
    assert (radiation.fiche, radiation.limite, radiation.age, radiation.version) \
        == (limite_age.FICHE_DES_CONTRACTUELS, 67.0, 70.0, "reforme_2023")
    assert _reculs(radiation) == [(limite_age.MAINTIEN, 67.0, 70.0, True)]
    assert [(d.date, sorted(d.regimes), d.motif) for d in departs.departs(moteur, carriere)] \
        == [(carriere.date_de_l_age(70), ["ircantec", "regime_general"], departs.MOTIF_LIMITE)]


def test_avant_2023_le_contractuel_part_a_sa_limite(simulateur):
    """Né en 1950, il atteint soixante-cinq ans en 2015 : sa limite n'est pas
    relevée (il a eu soixante ans en 2010), et rien ne la prolonge ; avant 2012,
    le maintien de la loi de 1947 s'arrêtait aussi à soixante-cinq ans."""
    moteur = simulateur.scenario_actuel
    for naissance, version in ((1950, "loi_de_2012"), (1940, "loi_de_1947")):
        radiation = limite_age.radiation(
            moteur, _simple(simulateur, "contractuel_public", naissance, 70))
        assert (radiation.limite, radiation.age, radiation.version, radiation.reculs) \
            == (65.0, 65.0, version, ())


def test_l_ouvrier_suit_les_paliers_du_decret_de_2004(simulateur):
    """Né en 1945, l'ouvrier a soixante et un ans et demi en 2006, la limite de
    cette année-là (décret n° 2004-1057, article 2) ; l'insalubre, soixante ans
    en 2005, la sienne (article 3)."""
    moteur = simulateur.scenario_actuel
    for statut, limite in (("ouvrier_etat", 61.5), ("ouvrier_etat_actif", 60.0)):
        radiation = limite_age.radiation(moteur, _simple(simulateur, statut, 1945, 68))
        assert (radiation.fiche, radiation.limite, radiation.age, radiation.version) \
            == (limite_age.FICHE_DES_OUVRIERS, limite, limite, "decret_de_2004")
        assert sorted(radiation.regimes) == ["fspoeie"]


def test_depuis_2023_l_ouvrier_insalubre_est_prolonge_jusqu_a_la_limite_des_autres(simulateur):
    """Né en 1990, l'ouvrier insalubre atteint soixante-deux ans en 2052 : la
    prolongation pour carrière incomplète, puis celle de L. 556-7, que le décret
    lui ouvre depuis le 1er septembre 2023, le mènent à soixante-sept ans ; le
    sédentaire est maintenu jusqu'à soixante-dix ans."""
    moteur = simulateur.scenario_actuel
    actif = limite_age.radiation(moteur, _simple(simulateur, "ouvrier_etat_actif", 1990, 75))
    assert (actif.limite, actif.age) == (62.0, 67.0)
    assert [r.nom for r in actif.reculs] == [limite_age.CARRIERE_INCOMPLETE,
                                            limite_age.PROLONGATION_ACTIVE]
    sedentaire = limite_age.radiation(moteur, _simple(simulateur, "ouvrier_etat", 1990, 75))
    assert (sedentaire.limite, sedentaire.age) == (67.0, 70.0)


def test_le_cheminot_recrute_avant_2020_a_la_limite_de_sa_generation(simulateur):
    """Né en 1950, il est admis à la retraite à soixante-cinq ans ; né en 1960,
    sa limite est relevée de seize mois (présumé), et le maintien jusqu'à
    soixante-dix ans lui est ouvert depuis le 1er septembre 2023 ; sa pension du
    régime spécial part de la limite."""
    moteur = simulateur.scenario_actuel
    ancien = limite_age.radiation(moteur, _simple(simulateur, "agent_sncf", 1950, 68))
    assert (ancien.fiche, ancien.limite, ancien.age, sorted(ancien.regimes)) \
        == (limite_age.FICHE_SNCF_RATP, 65.0, 65.0, ["sncf"])
    carriere = _simple(simulateur, "agent_sncf", 1960, 75)
    recent = limite_age.radiation(moteur, carriere)
    assert (round(recent.limite, 4), recent.age) == (round(65 + 16 / 12, 4), 70.0)
    assert [d.motif for d in departs.departs(moteur, carriere)] == [departs.MOTIF_LIMITE]



# --- Action 151, étape 6 : les industries électriques et gazières, l'Opéra
# national de Paris et la SEITA (fiches ``limite_age_ieg``,
# ``limite_age_opera`` et ``limite_age_seita``).

def test_l_agent_des_ieg_est_mis_en_inactivite_a_sa_limite(simulateur):
    """Né en 1953, il a soixante-cinq ans en 2018 ; né en 1960, sa limite est
    de soixante-six ans et quatre mois (dispositions transitoires de 2011), et
    le maintien jusqu'à soixante-dix ans lui est ouvert depuis le 1er
    septembre 2023. Né en 1950, il avait cinquante-cinq ans en 2005 : le
    décret n° 54-50 le mettait alors en inactivité (test suivant)."""
    moteur = simulateur.scenario_actuel
    ancien = limite_age.radiation(moteur, _simple(simulateur, "agent_ieg", 1953, 68))
    assert (ancien.fiche, ancien.limite, ancien.age, ancien.version, sorted(ancien.regimes)) \
        == (limite_age.FICHE_IEG, 65.0, 65.0, "decret_de_2011", ["ieg"])
    recent = limite_age.radiation(moteur, _simple(simulateur, "agent_ieg", 1960, 75))
    assert (round(recent.limite, 4), recent.age, recent.version) \
        == (round(66 + 4 / 12, 4), 70.0, "decret_de_2023")
    assert [r.nom for r in recent.reculs] == [limite_age.MAINTIEN]


def test_avant_2008_l_agent_des_ieg_est_mis_en_inactivite_a_l_ouverture_de_ses_droits(simulateur):
    """Décret n° 54-50, article 2 : « l'admission à la retraite est prononcée
    d'office quand l'intéressé a atteint l'âge d'ouverture du droit à pension
    d'ancienneté » s'il a les vingt-cinq ans de services que le statut requiert
    (annexe 3, article 3), et, sinon, à l'âge des sédentaires, soixante ans.
    L'agent des IEG, que le modèle liquide comme actif, ouvre son droit à
    cinquante-cinq ans. Né le 1er janvier 1945 et entré à vingt-deux ans, il a
    cinquante-cinq ans le 1er janvier 2000 : sa pension part de janvier 2000,
    l'âge d'un assuré né le 1er se comptant du mois de sa naissance. Né le 1er
    janvier 1940 et entré le 1er janvier 1972, il réunit ses vingt-cinq ans de
    services le 31 décembre 1996 : sa pension part de janvier 1997, à
    cinquante-sept ans. Entré en 1980, il ne les a pas à soixante ans : il est
    mis en inactivité à soixante ans, en janvier 2000."""
    moteur = simulateur.scenario_actuel
    for naissance, debut, date, age in ((1945, 22, DateMois(2000, 1), 55.0),
                                        (1940, 32, DateMois(1997, 1), 57.0),
                                        (1940, 40, DateMois(2000, 1), 60.0)):
        carriere = simulateur.carriere_simple(naissance, "H", "agent_ieg", debut, 68,
                                              jour_naissance=1)
        radiation = limite_age.radiation(moteur, carriere)
        assert (radiation.fiche, radiation.version, radiation.date, radiation.reculs) \
            == (limite_age.FICHE_IEG, "decret_de_1954", date, ()), (naissance, debut)
        assert (round(radiation.limite, 4), round(radiation.age, 4)) \
            == (round(age, 4), round(age, 4)), (naissance, debut)
        assert radiation.forcee and sorted(radiation.regimes) == ["ieg"]
        assert [(d.date, d.motif) for d in departs.departs(moteur, carriere)] \
            == [(date, departs.MOTIF_LIMITE)]


def test_depuis_le_28_novembre_2007_l_agent_des_ieg_poursuit_s_il_le_souhaite(simulateur):
    """La recommandation patronale du 28 novembre 2007 laisse l'agent qui le
    souhaite poursuivre au-delà de l'ouverture de ses droits (réponse
    ministérielle, JO AN du 14 octobre 2008) : né en novembre 1952, il a
    cinquante-cinq ans le 15 novembre 2007 et il est mis en inactivité ; né un
    mois plus tard, il part à soixante-deux ans, comme il le demande, avant la
    limite de soixante-cinq ans du statut de 2008."""
    moteur = simulateur.scenario_actuel
    avant = limite_age.radiation(moteur, _simple(simulateur, "agent_ieg", 1952, 62,
                                                 mois_naissance=11))
    assert (avant.version, avant.date, avant.limite) == ("decret_de_1954", DateMois(2007, 12), 55.0)
    apres = _simple(simulateur, "agent_ieg", 1952, 62, mois_naissance=12)
    assert limite_age.radiation(moteur, apres) is None


def test_la_prolongation_de_l_agent_des_ieg_s_arrete_a_cent_cinquante_trimestres(simulateur):
    """La carrière incomplète ne prolonge pas au-delà de la durée du taux
    maximum moins cent cinquante trimestres : quatre trimestres pour le né en
    1955, à qui le modèle demande 154 trimestres ; rien pour le né en 1950, à
    qui il en demande 150 ; le né en 1965, à qui il en demande 168, est arrêté
    à soixante-dix ans par le plafond de 2023."""
    moteur = simulateur.scenario_actuel
    for naissance, debut, depart, age in ((1955, 40, 72, 66.0), (1950, 45, 70, 65.0),
                                          (1965, 45, 75, 70.0)):
        carriere = simulateur.carriere_simple(naissance, "H", "agent_ieg", debut, depart)
        radiation = limite_age.radiation(moteur, carriere)
        assert radiation.age == age, naissance
        assert all(r.fiche == limite_age.FICHE_IEG for r in radiation.reculs)


def test_le_personnel_de_l_opera_cesse_ses_fonctions_a_sa_limite(simulateur):
    """Soixante-cinq ans pour le né en 1950, soixante-sept pour le né en 1990
    (décret n° 2008-240, article 2) ; entré à quarante-cinq ans, sa carrière
    incomplète le maintient dix trimestres de plus."""
    moteur = simulateur.scenario_actuel
    for naissance, debut, depart, limite, age in ((1950, 22, 68, 65.0, 65.0),
                                                  (1990, 22, 75, 67.0, 67.0),
                                                  (1950, 45, 70, 65.0, 67.5)):
        carriere = simulateur.carriere_simple(naissance, "H", "personnel_opera", debut, depart)
        radiation = limite_age.radiation(moteur, carriere)
        assert (radiation.fiche, radiation.limite, radiation.age, sorted(radiation.regimes)) \
            == (limite_age.FICHE_OPERA, limite, age, ["opera_de_paris"]), naissance


def test_la_limite_de_l_opera_ne_vaut_que_du_1er_juillet_2008(simulateur):
    """« Le présent décret entre en vigueur au 1er juillet 2008 » (décret
    n° 2008-240, article 3) : son article 2 aussi, que LEGI date du 10 mars.
    Né le 15 mai 1943, l'agent a soixante-cinq ans le 15 mai 2008 et cesse ses
    fonctions le 1er juillet, sa pension partant de juillet ; né le 15 janvier
    1938 et parti en mai 2008, il n'a pas de limite. Avant, seul l'artiste du
    ballet, que la saisie ne distingue pas, pouvait être mis à la retraite
    (décret n° 68-382, article 6, IV, depuis 2002)."""
    moteur = simulateur.scenario_actuel
    radiation = limite_age.radiation(
        moteur, _simple(simulateur, "personnel_opera", 1943, 67, mois_naissance=5))
    assert (radiation.version, radiation.date) == ("decret_de_2008", DateMois(2008, 7))
    parti = _simple(simulateur, "personnel_opera", 1938, 70 + 4 / 12)
    assert DateMois(2008, 3) < parti.date_liquidation < DateMois(2008, 7)
    assert limite_age.radiation(moteur, parti) is None


def test_l_agent_de_la_seita_est_retraite_a_soixante_cinq_ans(simulateur):
    """Le statut de 1962 (article 111) : soixante-cinq ans, sans exception."""
    moteur = simulateur.scenario_actuel
    radiation = limite_age.radiation(moteur, _simple(simulateur, "agent_seita", 1940, 68))
    assert (radiation.fiche, radiation.limite, radiation.age, radiation.version,
            radiation.reculs) == (limite_age.FICHE_SEITA, 65.0, 65.0, "statut_de_1962", ())


# --- Action 151, étape 8 : la Banque de France (fiche
# ``limite_age_banque_de_france``), statut du personnel, articles 241 à 242-1.

def test_l_agent_de_la_banque_de_france_prend_sa_retraite_a_sa_limite(simulateur):
    """Le tableau de l'article 241 : soixante-quatre ans et neuf mois pour le
    né au premier semestre de 1955, soixante-six ans et trois mois pour celui
    de 1958, soixante-sept ans depuis le second semestre de 1959 ; le né en
    1950 avait passé la sienne quand l'article est né, le 26 juillet 2012."""
    moteur = simulateur.scenario_actuel
    for naissance, depart, limite, version in ((1955, 70, 64.75, "statut_de_2019"),
                                               (1958, 70, 66.25, "statut_de_2019"),
                                               (1960, 72, 67.0, "statut_de_2019")):
        radiation = limite_age.radiation(
            moteur, _simple(simulateur, "agent_banque_de_france", naissance, depart))
        assert (radiation.fiche, radiation.limite, radiation.age, radiation.version,
                sorted(radiation.regimes), radiation.reculs) == (
            limite_age.FICHE_BANQUE_DE_FRANCE, limite, limite, version,
            ["banque_de_france"], ()), naissance
    premier = limite_age.radiation(moteur, _simple(simulateur, "agent_banque_de_france",
                                                   1950, 68, mois_naissance=1,
                                                   jour_naissance=15))
    assert (premier.version, premier.date) == ("statut_de_2012", DateMois(2012, 8))


def test_la_banque_de_france_proroge_pour_enfants_selon_son_statut(simulateur):
    """Article 242 : deux ans pour trois enfants à charge, ou deux à charge et
    un autre élevé ; un an pour deux à charge ; rien pour un seul ; et la
    prolongation pour carrière incomplète, qui ne s'y cumule pas, la remplace
    quand elle mène plus loin."""
    moteur = simulateur.scenario_actuel

    def radiation(naissances, debut=22.0):
        carriere = Carriere.depuis_parcours(
            annee_naissance=1960, sexe="F", metiers=[Metier("agent_banque_de_france", debut)],
            age_liquidation=75, macro=simulateur.macro, nombre_enfants=len(naissances),
            naissances_enfants=naissances)
        return limite_age.radiation(moteur, carriere)

    for naissances, age in ((("2012-01-01", "2014-01-01", "2016-01-01"), 69.0),
                            (("1990-01-01", "2014-01-01", "2016-01-01"), 69.0),
                            (("2014-01-01", "2016-01-01"), 68.0),
                            (("1985-01-01", "1990-01-01", "2016-01-01"), 68.0),
                            (("2016-01-01",), 67.0)):
        lue = radiation(naissances)
        assert lue.age == age, naissances
        assert all(r.fiche == limite_age.FICHE_BANQUE_DE_FRANCE and not r.presumee
                   for r in lue.reculs)
    incomplete = radiation(("2014-01-01", "2016-01-01"), debut=45.0)
    assert [(r.nom, r.depuis, r.jusqu_a) for r in incomplete.reculs] == [
        (limite_age.CARRIERE_INCOMPLETE, 67.0, 69.5)]


def test_l_exception_se_lit_au_jour_ou_la_limite_nait(simulateur):
    """Né le 15 janvier 1950, l'agent de la Banque avait passé sa limite,
    soixante-deux ans et trois mois, quand le statut l'a créée, le 26 juillet
    2012 : il l'atteint ce jour-là, à soixante-deux ans et six mois, et les
    exceptions se lisent ce jour-là, dans ce statut, et non à l'anniversaire du
    15 juillet, qui précède. Ses deux enfants, nés en 2000 et en 2002, sont à
    sa charge : un an de prorogation (article 242), et il prend sa retraite en
    août 2013, à soixante-trois ans et six mois (action 151, étape 10)."""
    moteur = simulateur.scenario_actuel
    carriere = _simple(simulateur, "agent_banque_de_france", 1950, 68, nombre_enfants=2,
                       naissances_enfants=("2000-01-01", "2002-01-01"))
    radiation = limite_age.radiation(moteur, carriere)
    assert (radiation.version, radiation.limite, radiation.age, radiation.date) \
        == ("statut_de_2012", 62.5, 63.5, DateMois(2013, 8))
    assert _reculs(radiation) == [(limite_age.RECUL_ENFANTS, 62.5, 63.5, False)]
    assert radiation.reculs[0].fiche == limite_age.FICHE_BANQUE_DE_FRANCE


# --- Action 151, étape 10 : le mineur (fiche ``limite_age_mines``), décret
# n° 54-51 du 16 janvier 1954, articles 2 et 3.

def test_le_mineur_passe_sa_limite_dans_l_interet_du_service(simulateur):
    """Article 2 : « L'âge limite de maintien en activité » du mineur « est
    l'âge fixé pour l'ouverture du droit à rente ou pension de retraite par les
    dispositions du premier alinéa de l'article 146 » du décret n° 46-2769, qui
    la garantit « aux affiliés âgés de cinquante-cinq ans » ; depuis 1993,
    l'article 125 la leur garantit au même âge. Article 3 : « Tout agent peut,
    dans l'intérêt du service, être admis à rester en activité au delà de l'âge
    limite », maintien sans borne, présumé accordé autant que le départ saisi
    le demande. Né en 1930, il a cinquante-cinq ans en 1985, et né en 1950, en
    2005 : parti à soixante ans, il n'est pas radié, et sa pension part de son
    départ."""
    moteur = simulateur.scenario_actuel
    for naissance, version in ((1930, "decret_de_1954"), (1950, "article_125_de_1993")):
        carriere = _simple(simulateur, "mineur", naissance, 60)
        radiation = limite_age.radiation(moteur, carriere)
        assert (radiation.fiche, radiation.version, radiation.limite, radiation.age,
                sorted(radiation.regimes)) \
            == (limite_age.FICHE_MINES, version, 55.0, 60.0, ["mines"]), naissance
        assert not radiation.forcee and radiation.date == carriere.date_liquidation
        assert _reculs(radiation) == [
            (limite_age.MAINTIEN_DANS_L_INTERET_DU_SERVICE, 55.0, 60.0, True)]
        assert departs.departs(moteur, carriere)[0].unique
        assert limite_age.radier(moteur, carriere) is carriere


def test_avant_le_decret_de_1954_le_mineur_n_a_pas_de_limite(simulateur):
    """Le décret n° 54-51 vaut du 18 janvier 1954 : né le 15 janvier 1898, le
    mineur parti en août 1953, à cinquante-cinq ans et demi, n'a pas de limite ;
    parti à cinquante-huit ans, il atteint la sienne ce jour-là, à cinquante-six
    ans, et le maintien le garde jusqu'à son départ."""
    moteur = simulateur.scenario_actuel
    avant = _simple(simulateur, "mineur", 1898, 55.5)
    assert avant.date_liquidation == DateMois(1953, 8)
    assert limite_age.radiation(moteur, avant) is None
    apres = limite_age.radiation(moteur, _simple(simulateur, "mineur", 1898, 58))
    assert (apres.version, apres.limite, apres.forcee) == ("decret_de_1954", 56.0, False)
    assert _reculs(apres) == [
        (limite_age.MAINTIEN_DANS_L_INTERET_DU_SERVICE, 56.0, 58.0, True)]


# --- Action 130, la carte des fiches : les quinze fiches que ce module lit,
# mûres (contrat C.2, ``data/reference/contrats/fiche.yaml``).

def test_les_fiches_de_la_limite_d_age_sont_mures():
    """Rien ne manque aux quinze fiches de ce que leur contrat exige. Chaque
    approchée dit ses approximations, dans des versions qu'elle porte. Le code
    de chacune nomme, dans chaque moteur, des fonctions qui sont dans les
    fichiers qu'il nomme (« fichier : fonction, Classe.méthode ; … »), les
    paramètres que ses versions portent, tous et rien d'autre, et des tests qui
    existent."""
    from outils_carte import ecarts

    fiches = carte.fiches()
    manques = carte.manques()
    assert {nom: manques[nom] for nom in limite_age.FICHES if nom in manques} == {}
    assert [e for nom in limite_age.FICHES for e in ecarts(fiches[nom])] == []
