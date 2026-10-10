"""La retraite progressive (fiche ``retraite_progressive`` ; ``droit/progressive.py``).

L'assuré qui garde en fin de carrière une activité à temps partiel touche
une fraction de sa pension, liquidée à titre provisoire ; au départ, sa
pension complète se recalcule, et ne descend pas sous la provisoire
revalorisée — avant le décret du 8 juin 2006, elle l'était. La demande
s'ouvre selon sa date : l'âge, la durée, la quotité, et le régime où l'assuré
travaille à temps partiel ; elle liquide à titre provisoire les régimes que
nomme L. 351-15, puis tous. Les années à temps partiel portent leur quotité :
les services de la fonction publique la comptent, le traitement de référence
se lit à temps plein.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import liquidation, liquider, progressive
from retraite_notionnelle.droit.compter import services_a_temps_partiel
from retraite_notionnelle.saisie import ErreurSaisie, Saisie
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur: Simulateur, metiers: list[Metier], naissance: int = 1965,
              liquidation: float = 64, sexe: str = "F", **kwargs) -> Carriere:
    """La carrière d'un assuré né le 15 janvier : le jour se déclare, puisque
    les dates de la demande et du départ se comptent depuis lui ; celui que
    la présomption pose a son test (``test_chronologie.py`` ; feuille de
    route, action 135, levier 2)."""
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe, metiers=metiers,
        age_liquidation=liquidation, macro=simulateur.macro, jour_naissance=15, **kwargs)


def _salariee(simulateur: Simulateur, age: float | None = 60.75, quotite: float = 0.6,
              **kwargs) -> Carriere:
    demande = None if age is None else {"age": age, "quotite": quotite}
    return _carriere(simulateur, [Metier("salarie_prive_non_cadre", 20.0)],
                     retraite_progressive=demande, **kwargs)


# -- la règle, version par version ------------------------------------------------

@pytest.mark.parametrize("date, attendu", [
    (DateMois(1990, 6), "legal"),
    (DateMois(2014, 6), "au_moins_60"),
    (DateMois(2024, 3), "legal_moins_deux"),
    (DateMois(2025, 11), 60.0),
])
def test_l_age_qui_ouvre_la_retraite_progressive(simulateur, date, attendu):
    moteur = simulateur.scenario_actuel
    carriere = _salariee(simulateur)
    legal = progressive._departs.age_legal(moteur, carriere)
    valeur = progressive.age_minimum(moteur, carriere, date)
    if attendu == "legal":
        assert valeur == legal
    elif attendu == "au_moins_60":
        assert valeur == max(60.0, legal - 2.0)
    elif attendu == "legal_moins_deux":
        assert valeur == legal - 2.0
    else:
        assert valeur == attendu


def test_la_duree_exigee_et_les_regimes_suivent_leurs_textes():
    assert progressive.duree_requise(DateMois(1990, 1)) == 150
    assert progressive.duree_requise(DateMois(2000, 1)) == 160
    assert progressive.duree_requise(DateMois(2010, 1)) == 150
    # Le libéral ne la demande qu'en 2023 : le décret de L. 643-8-1 n'a
    # jamais paru. Mais L. 351-15 liquide sa pension avec celle du salarié.
    assert "cnavpl" not in progressive.regimes_ouverts(DateMois(2015, 1))
    assert "cnavpl" in progressive.regimes_liquides(DateMois(1990, 1))
    assert "cnbf" not in progressive.regimes_liquides(DateMois(2015, 1))
    assert {"cnavpl", "cnbf", "crpcen"} <= progressive.regimes_ouverts(DateMois(2023, 9))
    assert "fonction_publique_etat" not in progressive.regimes_ouverts(DateMois(2023, 8))
    assert "cnracl" in progressive.regimes_ouverts(DateMois(2023, 9))
    # Les IEG aussi, par leur statut (annexe 3, article 21-1, depuis le
    # 1er septembre 2023) ; la SNCF et la RATP, dont les décrets ne sont pas
    # relus, non.
    assert "ieg" not in progressive.regimes_ouverts(DateMois(2023, 8))
    assert "ieg" in progressive.regimes_ouverts(DateMois(2023, 9))
    assert "sncf" not in progressive.regimes_ouverts(DateMois(2023, 9))
    assert progressive.regimes_liquides(DateMois(2023, 9)) is None


@pytest.mark.parametrize("date, quotite, fonctionnaire, fraction", [
    # Avant le 18 décembre 2014 : trois tranches (R. 351-41).
    (DateMois(2000, 1), 0.7, False, 0.3),
    (DateMois(2000, 1), 0.5, False, 0.5),
    (DateMois(2000, 1), 0.3, False, 0.7),
    (DateMois(2000, 1), 0.9, False, None),
    # Depuis : 100 % moins la quotité, de 40 à 80 %, arrondie à l'unité, la
    # moitié comptée pour un.
    (DateMois(2020, 1), 0.6, False, 0.4),
    (DateMois(2020, 1), 0.3, False, None),
    (DateMois(2020, 1), 0.85, False, None),
    (DateMois(2020, 1), 0.625, False, 0.37),
    (DateMois(2020, 1), 0.395, False, 0.6),
    (DateMois(2020, 1), 0.805, False, None),
    # Le fonctionnaire, de 50 à 90 % (son temps partiel).
    (DateMois(2024, 1), 0.9, True, 0.1),
    (DateMois(2024, 1), 0.45, True, None),
])
def test_la_fraction_servie(date, quotite, fonctionnaire, fraction):
    trouvee = progressive.fraction(date, quotite, fonctionnaire)
    assert trouvee == (None if fraction is None else pytest.approx(fraction))


# -- la carrière à temps partiel --------------------------------------------------

def test_les_annees_de_retraite_progressive_portent_leur_quotite(simulateur):
    """De novembre 2025 au départ, l'activité se poursuit à 60 % : le revenu
    de ces mois est réduit d'autant, et la ligne porte la quotité moyenne de
    ses mois."""
    avec = {l.annee: l for l in _salariee(simulateur).lignes}
    sans = {l.annee: l for l in _salariee(simulateur, age=None).lignes}
    assert avec[2024].quotite == 1.0 and avec[2024].revenu == sans[2024].revenu
    assert avec[2025].quotite == pytest.approx((10 + 2 * 0.6) / 12)
    assert avec[2027].quotite == pytest.approx(0.6)
    assert avec[2027].revenu == pytest.approx(0.6 * sans[2027].revenu)


@pytest.mark.parametrize("trimestres, quotite, services", [
    (4, 1.0, 4), (4, 0.7, 3), (4, 0.6, 2), (4, 0.625, 3), (2, 0.5, 1),
])
def test_les_services_d_un_temps_partiel_comptent_leur_duree_reelle(
        trimestres, quotite, services):
    assert services_a_temps_partiel(trimestres, quotite) == services


def test_le_fonctionnaire_liquide_son_traitement_a_temps_plein(simulateur):
    """Le temps partiel réduit ses services, pas son traitement indiciaire."""
    moteur = simulateur.scenario_actuel
    metiers = [Metier("fonctionnaire_etat", 23.0)]
    avec = moteur.calculer(_carriere(simulateur, metiers, naissance=1963, part_primes=0.2,
                                     retraite_progressive={"age": 61.0, "quotite": 0.7}))
    sans = moteur.calculer(_carriere(simulateur, metiers, naissance=1963, part_primes=0.2))
    [etat_avec] = [p for p in avec.pensions_par_regime if p.regime == "fonction_publique_etat"]
    [etat_sans] = [p for p in sans.pensions_par_regime if p.regime == "fonction_publique_etat"]
    assert etat_avec.detail.split(" × ")[0] == etat_sans.detail.split(" × ")[0]
    assert etat_avec.montant < etat_sans.montant


def test_la_pension_complete_du_fonctionnaire_n_a_pas_de_plancher(simulateur):
    """Le code des pensions liquide la pension complète « dans les conditions
    et selon les modalités de calcul applicables à sa date d'effet » (D. 37-3,
    et de même la CNRACL et les ouvriers de l'État) : la pension provisoire ne
    la borne pas, comme elle borne celle du régime général (D. 161-2-24-7)."""
    moteur = simulateur.scenario_actuel
    carriere = _carriere(simulateur, [Metier("salarie_prive_non_cadre", 23.0),
                                      Metier("fonctionnaire_etat", 35.0)],
                         naissance=1963, part_primes=0.2,
                         retraite_progressive={"age": 61.0, "quotite": 0.7})
    examinee = progressive.examiner(moteur, carriere)
    assert examinee.ouverte
    assert {"fonction_publique_etat", "regime_general"} <= examinee.bases
    provisoire = progressive.liquider(moteur, carriere, liquidation.Contexte(moteur), examinee)
    bornees = dict(progressive.initiales(moteur, examinee, provisoire,
                                         carriere.date_liquidation))
    assert "regime_general" in bornees and "fonction_publique_etat" not in bornees


# -- la demande, ouverte ou fermée ------------------------------------------------

def test_la_demande_ouverte_sert_sa_fraction(simulateur):
    moteur = simulateur.scenario_actuel
    resultat = moteur.calculer(_salariee(simulateur))
    servie = resultat.retraite_progressive
    assert servie.ouverte and servie.recalculee
    assert servie.date_effet == "2025-11-01"
    assert servie.fraction == pytest.approx(0.4)
    assert servie.montant_servi == pytest.approx(0.4 * servie.montant_provisoire)
    assert "regime_general" in servie.regimes and "agirc_arrco" in servie.regimes
    assert servie.trimestres >= servie.duree_requise == 150


@pytest.mark.parametrize("carriere, motif", [
    (dict(age=58.25), progressive.AGE),
    (dict(age=60.75, quotite=0.9), progressive.QUOTITE),
    (dict(age=60.75, naissance=1925, liquidation=63), progressive.AVANT_1988),
    (dict(age=60.75, interruptions={2025: "chomage_indemnise"}), progressive.SANS_ACTIVITE),
])
def test_la_demande_fermee_dit_pourquoi(simulateur, carriere, motif):
    moteur = simulateur.scenario_actuel
    servie = moteur.calculer(_salariee(simulateur, **carriere)).retraite_progressive
    assert servie.motif == motif
    assert servie.fraction == 0.0 and servie.montant_servi == 0.0


def test_le_regime_du_temps_partiel_ouvre_la_demande(simulateur):
    """En 2016, le libéral qui réduit son activité n'a pas de retraite
    progressive ; la salariée qui l'a été liquide sa pension de libérale avec
    celle du régime général (L. 351-15), non ses points de complémentaire."""
    moteur = simulateur.scenario_actuel
    demande = {"age": 60.25, "quotite": 0.5}
    liberal = _carriere(simulateur, [Metier("profession_liberale", 25.0)], naissance=1956,
                        liquidation=63, retraite_progressive=demande)
    assert moteur.calculer(liberal).retraite_progressive.motif == progressive.SANS_REGIME
    salariee = _carriere(simulateur, [Metier("profession_liberale", 22.0),
                                      Metier("salarie_prive_non_cadre", 35.0)],
                         naissance=1956, liquidation=63, retraite_progressive=demande)
    servie = moteur.calculer(salariee).retraite_progressive
    assert servie.ouverte
    assert {"regime_general", "cnavpl", "arrco"} <= set(servie.regimes)
    assert not any(code.endswith("_complementaire") for code in servie.regimes)
    fonctionnaire = _carriere(simulateur, [Metier("fonctionnaire_etat", 23.0)],
                              naissance=1958, liquidation=63,
                              retraite_progressive={"age": 61.0, "quotite": 0.7})
    assert moteur.calculer(fonctionnaire).retraite_progressive.motif == progressive.SANS_REGIME


def test_sans_la_duree_la_demande_est_fermee(simulateur):
    """Entrée à quarante ans, la salariée n'a pas cent cinquante trimestres."""
    moteur = simulateur.scenario_actuel
    carriere = _carriere(simulateur, [Metier("salarie_prive_non_cadre", 40.0)],
                         retraite_progressive={"age": 60.75, "quotite": 0.6})
    servie = moteur.calculer(carriere).retraite_progressive
    assert servie.motif == progressive.DUREE
    assert servie.trimestres < servie.duree_requise


def test_la_liquidation_fictive_ne_voit_pas_la_retraite_progressive(simulateur):
    moteur = simulateur.scenario_actuel
    assert moteur.calculer(_salariee(simulateur), nature="fictive").retraite_progressive is None


@pytest.mark.parametrize("naissance", [1955, 1958, 1962])
def test_la_decote_de_la_pension_provisoire_ne_depasse_pas_25_pour_cent(
        simulateur, naissance):
    """Du 18 décembre 2014 au 1er septembre 2023, la décote de la pension
    provisoire ne dépasse pas 25 % (R. 351-41, D. 634-19, D. 732-167). Aucun
    code ne l'écrit : chaque régime de 1988 borne sa décote à vingt trimestres,
    et les générations qui la demandaient alors perdent 1,25 % par trimestre.
    Liquidée à soixante ans, loin de la durée et de l'âge du taux plein, la
    pension provisoire du régime général tombe à 37,5 %, pas en dessous."""
    moteur = simulateur.scenario_actuel
    carriere = _carriere(simulateur, [Metier("salarie_prive_non_cadre", 28.0)],
                         naissance=naissance, liquidation=63)
    a_soixante = carriere.liquidee_au(DateMois(naissance + 60, 2))
    assert "2014-12-18" <= f"{naissance + 60}-02-01" < "2023-09-01"
    for code in progressive.REGIMES_1988:
        periode = moteur.catalogue[code].periode(naissance + 60)
        if periode is None or not periode.decote_par_trimestre:
            continue
        decote, _, _ = liquider.decote_opposable(moteur, periode, a_soixante, naissance + 60)
        assert decote * periode.decote_trimestres_maximum <= 0.25 + 1e-12, code
    ouverte = progressive.Progressive(
        DateMois(naissance + 60, 2), 0.5, progressive.OUVERTE, fraction=0.5,
        bases=frozenset({"regime_general"}))
    provisoire = progressive.liquider(moteur, carriere, liquidation.Contexte(moteur), ouverte)
    [general] = [p for p in provisoire.regimes if p.regime == "regime_general"]
    assert "taux 37.500%" in general.detail


# -- la pension complète ------------------------------------------------------------

def test_la_pension_complete_ne_descend_pas_sous_la_provisoire(simulateur):
    """Le plancher de D. 161-2-24-7 : une pension provisoire plus haute que
    la pension complète la relève, et le total contributif la compte."""
    moteur = simulateur.scenario_actuel
    carriere = _salariee(simulateur, age=None)
    demande = liquidation.demande_de_depart(carriere)
    contexte = liquidation.Contexte(moteur)
    libre = liquidation.liquider(demande, liquidation.Etat(carriere), contexte)
    [general] = [p for p in libre.regimes if p.regime == "regime_general"]
    haute = general.montant + 1000.0
    relevee = liquidation.liquider(
        demande, liquidation.Etat(carriere, initiales=(("regime_general", haute),)), contexte)
    [releve] = [p for p in relevee.regimes if p.regime == "regime_general"]
    assert releve.montant == pytest.approx(haute)
    assert "porté à la pension provisoire revalorisée" in releve.detail
    assert relevee.total == pytest.approx(libre.total + 1000.0)
    assert relevee.total_contributif == pytest.approx(libre.total_contributif + 1000.0)
    basse = liquidation.liquider(
        demande, liquidation.Etat(carriere, initiales=(("regime_general", 10.0),)), contexte)
    assert basse.total == pytest.approx(libre.total)


def test_avant_2006_la_pension_complete_est_la_provisoire(simulateur):
    """Avant le décret du 8 juin 2006, la pension complète ne se recalcule
    pas : le temps partiel n'y ajoute rien."""
    moteur = simulateur.scenario_actuel
    avec = moteur.calculer(_salariee(simulateur, naissance=1930, liquidation=63,
                                     quotite=0.5, age=60.25))
    assert not avec.retraite_progressive.recalculee
    [general] = [p for p in avec.pensions_par_regime if p.regime == "regime_general"]
    assert "ne se recalcule pas avant le 8 juin 2006" in general.detail


# -- l'échéancier -------------------------------------------------------------------

def test_l_echeancier_inscrit_la_fraction_puis_la_pension_complete(simulateur):
    journal = simulateur.echeancier(_salariee(simulateur)).journal
    entrees = {e.id: e for e in journal}
    evenement = entrees["retraite_progressive_assure"].contenu
    assert evenement.sorte == "retraite_progressive" and evenement.date == "2025-11-01"
    provisoire = entrees["liquidation_retraite_progressive_assure"].contenu
    assert provisoire.demande.nature == "provisoire"
    servie = entrees["progressive_pension_regime_general"].contenu
    entiere = next(c for c in provisoire.composantes() if c["id"] == "pension_regime_general")
    assert servie["montant"]["annuel"] == pytest.approx(0.4 * entiere["montant"]["annuel"])
    assert entrees["pension_regime_general"].remplace == "progressive_pension_regime_general"
    assert entrees["depart_assure"].contenu.sorte == "pension_definitive"


# -- la saisie ----------------------------------------------------------------------

def test_la_saisie_porte_la_retraite_progressive():
    base = {"naissance": "1965-01-15", "sexe": "F", "debut": "20", "liquidation": "64"}
    saisie = Saisie.depuis_requete({**base, "progressive": "2025-11", "quotite": "60"})
    assert saisie.retraite_progressive_declaree() == {
        "age": pytest.approx(60.75), "quotite": pytest.approx(0.6)}
    assert "progressive=2025-11&quotite=60" in saisie.requete()
    with pytest.raises(ErreurSaisie, match="quotite"):
        Saisie.depuis_requete({**base, "quotite": "60"})
    with pytest.raises(ErreurSaisie, match="précède le départ"):
        Saisie.depuis_requete({**base, "progressive": "2030-01", "quotite": "60"})
    with pytest.raises(ErreurSaisie, match="entre 1 et 99"):
        Saisie.depuis_requete({**base, "progressive": "2025-11", "quotite": "0"})
