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
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _simple(simulateur: Simulateur, statut: str, naissance: int, depart: float,
            **kwargs) -> Carriere:
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
    """Le salarié, l'agent des IEG, et le cheminot recruté depuis la fermeture
    du régime spécial, salarié de droit commun, ne sont pas radiés."""
    moteur = simulateur.scenario_actuel
    for statut, naissance in (("salarie_prive_non_cadre", 1990), ("agent_ieg", 1990),
                              ("agent_sncf", 2000)):
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

