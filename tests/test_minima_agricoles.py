"""Les deux minima des exploitants agricoles (action 138, étape 8).

La pension majorée de référence relève la pension de base des non-salariés
agricoles liquidée au taux plein (L. 732-54-1 à L. 732-54-4 du code rural) ;
le complément différentiel ajoute des points de RCO jusqu'à un pourcentage du
SMIC net agricole (L. 732-63). Leurs fiches — ``pension_majoree_reference`` et
``complement_differentiel_rco`` — disent la règle de chaque date d'effet ; ces
tests la rejouent sur des chefs d'exploitation à faible revenu, dans les deux
moteurs. Depuis le 1er septembre 2023, le taux plein ouvre aussi les points
gratuits et le complément aux pensions prises avant sans la durée requise
(fiche ``relevement_des_exploitants_2023``) : « faire vivre » les sert.
"""

from __future__ import annotations

import importlib.util
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import completer
from retraite_notionnelle.droit.liquider import valeur_du_point
from retraite_notionnelle.echeancier import Echeancier
from retraite_notionnelle.revalorisation import faire_vivre
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _chef(simulateur: Simulateur, naissance: int, liquidation: float, niveau: float = 0.3,
          debut: float = 20.0, metiers: list[Metier] | None = None, **kwargs) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=kwargs.pop("sexe", "H"),
        metiers=metiers or [Metier("exploitant_agricole", debut, niveau_salaire=niveau)],
        age_liquidation=liquidation, macro=simulateur.macro, **kwargs)


def _resultat(simulateur: Simulateur, carriere: Carriere):
    resultat = simulateur.scenario_actuel.calculer(carriere)
    avantages = {a.code: a for a in resultat.avantages_appliques}
    pensions = {p.regime: p.montant for p in resultat.pensions_par_regime}
    return resultat, avantages, pensions


def _cible(simulateur: Simulateur, carriere: Carriere) -> float:
    """Le montant minimal d'une carrière complète, pourcentage × 1 820 × SMIC
    net agricole, de la règle de la date d'effet."""
    actuel = simulateur.scenario_actuel
    regle = actuel.complement_differentiel_rco.regle(
        f"{carriere.annee_liquidation:04d}-{carriere.mois_liquidation:02d}-01")
    smic, _ = actuel.complement_differentiel_rco.smic_net(carriere.annee_liquidation)
    return regle["pourcentage"] * completer.HEURES_DU_COMPLEMENT * smic


# -- les données et les règles ------------------------------------------------

def test_les_montants_de_la_pmr_se_refont_de_leurs_ancres():
    """Le fichier est ce que son récupérateur écrit : les ancres de D. 732-111
    et D. 732-113, revalorisées par les coefficients de l'article L. 161-23-1
    au centime inférieur. Le plafond de juillet 2022 retrouve celui que la MSA
    publie, et la PMR des pensions de septembre 2023 vaut le minimum
    contributif majoré, que la loi lui fait suivre."""
    chemin = RACINE / "scripts" / "fetch" / "dila_legi_pension_majoree.py"
    spec = importlib.util.spec_from_file_location("dila_legi_pension_majoree", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    lues = [(l["mesure"], l["date"], float(l["valeur"]), l["fiabilite"])
            for l in module._lignes(module.SORTIE)]
    assert lues == module.serie()
    valeurs = {(mesure, jour): valeur for mesure, jour, valeur, _ in lues}
    assert valeurs[("pmr_chef", "2009-01-01")] == 7596.00
    assert valeurs[("pmr_conjoint", "2009-01-01")] == 6036.00
    assert valeurs[("plafond", "2022-07-01")] == 11441.49
    majore = dict((jour, valeur) for jour, valeur, _ in
                  module.mesure_du_minimum("montant_majore"))
    for (mesure, jour), valeur in valeurs.items():
        if mesure == "pmr_depuis_septembre_2023":
            assert valeur == majore[jour], jour


def test_la_pmr_suit_la_version_de_sa_date_d_effet(simulateur):
    """Rien avant 2009 ; vingt-deux ans et demi exigés jusqu'en 2010,
    dix-sept et demi jusqu'en janvier 2014, aucun ensuite ; deux montants
    jusqu'en 2021 ; le montant de septembre 2023 ; le plafond de l'article
    L. 173-2 et les trimestres pour enfants depuis 2026."""
    pmr = simulateur.scenario_actuel.pension_majoree_reference
    assert not pmr.regle("2008-12-01")["existe"]
    assert pmr.regle("2010-06-01")["duree_minimale"] == 90
    assert pmr.regle("2012-06-01")["duree_minimale"] == 70
    assert pmr.regle("2015-06-01")["duree_minimale"] == 0
    assert pmr.regle("2015-06-01")["montant_reduit"] == "pmr_conjoint"
    assert pmr.regle("2022-06-01")["montant_reduit"] is None
    assert pmr.regle("2023-08-01")["montant"] == "pmr_chef"
    assert pmr.regle("2023-09-01")["montant"] == "pmr_depuis_septembre_2023"
    assert pmr.regle("2026-06-01")["plafond"] == "minimum_contributif"
    assert pmr.regle("2026-06-01")["majorations_de_duree"]
    assert pmr.montant("pmr_chef", 2019, 2) == (8272.80, pmr.montant("pmr_chef", 2019, 1)[1])


def test_le_complement_suit_la_version_de_sa_date_d_effet(simulateur):
    """Rien avant 2015 ; 73, 74 puis 75 % d'une carrière complète ; 85 % et
    la formule différentielle depuis novembre 2021 ; le taux plein au lieu de
    la durée requise depuis septembre 2023."""
    complement = simulateur.scenario_actuel.complement_differentiel_rco
    assert not complement.regle("2014-12-01")["existe"]
    assert complement.regle("2015-06-01")["pourcentage"] == 0.73
    assert complement.regle("2016-06-01")["pourcentage"] == 0.74
    assert complement.regle("2019-02-01")["formule"] == "carriere_complete"
    regle = complement.regle("2021-11-01")
    assert (regle["pourcentage"], regle["formule"], regle["condition"]) == (
        0.85, "differentielle", "duree_requise")
    assert regle["plafond_tous_regimes"]
    assert complement.regle("2023-09-01")["condition"] == "taux_plein"
    # Les montants que la MSA publie se refont au centime : 1 035,57 € par
    # mois pour 2021, 1 138,63 € au 1er janvier 2023, 1 214,40 € en 2026.
    for annee, mensuel in ((2021, 1035.57), (2023, 1138.63), (2026, 1214.40)):
        smic, _ = complement.smic_net(annee)
        assert int(0.85 * 1820 * smic / 12 * 100) / 100 == mensuel



def _smic_net_agricole():
    chemin = RACINE / "scripts" / "fetch" / "msa_smic_net_agricole.py"
    spec = importlib.util.spec_from_file_location("msa_smic_net_agricole", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_le_smic_net_agricole_se_refait_des_taux_salariaux():
    """La MSA déduit du SMIC brut les taux salariaux d'un non cadre de la
    production agricole — AGRICA à 3,93 % et non 3,15, l'AFNCA à 0,01 % — :
    21,63025 % depuis 2019, 22,845 % en 2015. Le calcul redonne au centime
    chaque montant publié, le fichier s'en écarte de moins de 0,0002 € de
    l'heure (2024 à part), et son niveau dit qui l'a publié."""
    module = _smic_net_agricole()
    assert module.confronter() == []
    assert module.taux_deduit(2019) == pytest.approx(21.63025)
    assert module.taux_deduit(2015) == pytest.approx(22.845)
    brut, lues = module.smic_brut(), module.fichier()
    assert set(lues) == set(range(2015, 2027))
    for annee, (valeur, _) in lues.items():
        tolerance = 0.0002 + module.ECARTS_CONNUS.get(annee, 0.0) / (
            0.85 * module.HEURES_PAR_MOIS)
        assert abs(valeur - module.calcule(annee, brut)) <= tolerance, annee
    publies = {annee: (part, montant, producteur)
               for annee, part, montant, _, producteur, *_ in module.PUBLIES
               if montant != int(montant)}
    for annee, (part, montant, producteur) in publies.items():
        assert lues[annee][0] == module.horaire_publie(part, montant), annee
        assert lues[annee][1] == ("certifiee" if producteur else "haute"), annee
    certifiees = {annee for annee, (_, niveau) in lues.items() if niveau == "certifiee"}
    assert certifiees == {annee for annee, (*_, producteur) in publies.items() if producteur}


def test_les_montants_mensuels_que_la_msa_publie_sortent_des_tables(simulateur):
    """Ce que la MSA et le ministère écrivent par mois, au centime inférieur :
    681,20 € et 541,30 € de PMR au 1er avril 2013, sous un plafond de
    852,39 € (ministère de l'agriculture, page du 11 février 2015) ; 699,07 €
    et 874,76 € en 2021, 747,57 € et 961,08 € au 1er janvier 2023 (la MSA au
    COR, 26 janvier 2023)."""
    pmr = simulateur.scenario_actuel.pension_majoree_reference

    def mois(mesure, annee, mois_):
        return math.floor(pmr.montant(mesure, annee, mois_)[0] / 12 * 100 + 1e-6) / 100

    assert (mois("pmr_chef", 2013, 4), mois("pmr_conjoint", 2013, 4),
            mois("plafond", 2013, 4)) == (681.20, 541.30, 852.39)
    assert (mois("pmr_chef", 2021, 1), mois("plafond", 2021, 1)) == (699.07, 874.76)
    assert (mois("pmr_chef", 2023, 1), mois("plafond", 2023, 1)) == (747.57, 961.08)


def test_une_carriere_complete_de_chef_partie_en_2022_touche_la_garantie_publiee(simulateur):
    """La MSA écrit la garantie d'une carrière complète de chef au
    1er janvier 2022 : 1 067,91 € par mois. Quarante-deux ans de chef à
    faible revenu, parti à 62 ans en 2022 au taux plein : ses deux pensions
    agricoles la valent, au centime près."""
    carriere = _chef(simulateur, 1960, 62)
    assert carriere.annee_liquidation == 2022
    _, avantages, pensions = _resultat(simulateur, carriere)
    assert {"pension_majoree_reference", "complement_differentiel_rco"} <= set(avantages)
    assert math.floor(_cible(simulateur, carriere) / 12 * 100 + 1e-6) / 100 == 1067.91
    agricoles = pensions["msa_non_salaries"] + pensions["msa_rco"]
    assert agricoles / 12 == pytest.approx(1067.91, abs=0.02)


# -- le scénario 1 --------------------------------------------------------------

def test_un_chef_parti_en_2019_atteint_75_pour_cent_du_smic_net(simulateur):
    """Quarante-quatre ans de chef d'exploitation à faible revenu, au taux
    plein : la PMR porte la pension de base, avant surcote, à 8 272,80 € ; le
    complément de la RCO porte les deux pensions agricoles à 75 % de 1 820
    heures au SMIC net agricole, à un demi-point près."""
    carriere = _chef(simulateur, 1955, 64)
    resultat, avantages, pensions = _resultat(simulateur, carriere)
    pmr = avantages["pension_majoree_reference"]
    assert pmr.montant > 0
    assert "PMR 8,272.80 €" in pmr.detail
    assert "complement_differentiel_rco" in avantages
    valeur = 0.3392
    agricoles = pensions["msa_non_salaries"] + pensions["msa_rco"]
    assert abs(agricoles - _cible(simulateur, carriere)) <= valeur / 2 + 1e-6
    assert resultat.pension_annuelle == pytest.approx(
        resultat.total_contributif + sum(a.montant for a in resultat.avantages_appliques))


def test_un_chef_parti_en_2024_atteint_85_pour_cent(simulateur):
    """En 2024, la cible est de 85 %, et le plafond de toutes les pensions
    s'y ajoute : les deux pensions agricoles l'atteignent à un demi-point
    près."""
    carriere = _chef(simulateur, 1958, 66)
    _, avantages, pensions = _resultat(simulateur, carriere)
    assert {"pension_majoree_reference", "complement_differentiel_rco"} <= set(avantages)
    agricoles = pensions["msa_non_salaries"] + pensions["msa_rco"]
    assert agricoles == pytest.approx(_cible(simulateur, carriere), abs=0.2)


def test_ni_pmr_avant_2009_ni_complement_avant_2015(simulateur):
    _, avantages, _ = _resultat(simulateur, _chef(simulateur, 1945, 63))
    assert not {"pension_majoree_reference", "complement_differentiel_rco"} & set(avantages)
    _, avantages, _ = _resultat(simulateur, _chef(simulateur, 1950, 62))
    assert "pension_majoree_reference" in avantages
    assert "complement_differentiel_rco" not in avantages


# -- les plans de revalorisation de 1997 à 2008 --------------------------------

def _majoration(simulateur: Simulateur, carriere: Carriere):
    _, avantages, pensions = _resultat(simulateur, carriere)
    return avantages.get("majoration_retraite_proportionnelle"), pensions


def test_les_plans_portent_une_carriere_complete_au_minimum_vieillesse(simulateur):
    """Depuis 2002, A = (MV1 - AVTS) / (37,5 × VP) : la retraite forfaitaire
    et la proportionnelle d'une carrière complète de chef valent le minimum
    vieillesse d'une personne seule, 6 832,58 € en 2002 (décret n° 2002-298,
    article 3)."""
    majoration, pensions = _majoration(simulateur, _chef(simulateur, 1942, 60))
    assert majoration is not None
    etages = simulateur.scenario_actuel.minimum_vieillesse.deux_etages(2002)
    assert pensions["msa_non_salaries"] == pytest.approx(
        etages.avts + etages.supplementaire, abs=0.01)


def test_les_points_de_1997_ne_sont_servis_qu_au_tiers(simulateur):
    """26,933 points par année de chef, servis au tiers en 1997, aux deux
    tiers en 1998, entiers en 1999 (décret n° 97-163, articles 1er et 3) ; 29,23
    en 2001 (décret n° 2001-170)."""
    for naissance, age, minimum, part in ((1935, 62, 26.933, 1 / 3), (1937, 61, 26.933, 2 / 3),
                                          (1939, 60, 26.933, 1.0), (1941, 60, 29.23, 1.0)):
        majoration, _ = _majoration(simulateur, _chef(simulateur, naissance, age))
        assert majoration is not None, naissance
        assert f"({minimum:.3f} - " in majoration.detail
        assert majoration.detail.startswith(
            f"{(minimum - 16.0) * 37.5 * part:,.2f} points"), majoration.detail


def test_les_points_se_minorent_sous_vingt_deux_ans_et_demi_de_chef(simulateur):
    """Vingt ans de chef en 1999, après vingt de salarié : il en manque deux
    et demi, 15 + 15 + la moitié de 20 %, quarante pour cent de moins."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 40.0, niveau_salaire=0.3)]
    majoration, _ = _majoration(simulateur, _chef(simulateur, 1939, 60, metiers=metiers))
    assert majoration is not None
    points = float(majoration.detail.split(" points")[0].replace(",", ""))
    minimum, moyenne = (float(x) for x in
                        majoration.detail.split("(")[1].split(")")[0].split(" - "))
    assert majoration.detail.endswith("× 20 ans de chef")
    assert points == pytest.approx((minimum - moyenne) * 20 * 0.6, abs=0.02)


def test_ni_plan_avant_1997_ni_sans_le_taux_plein(simulateur):
    """Une pension de 1996 n'a pas le minimum à la liquidation ; vingt ans de
    chef partis à soixante ans en 2000, sans la durée requise, non plus."""
    majoration, _ = _majoration(simulateur, _chef(simulateur, 1934, 62))
    assert majoration is None
    majoration, _ = _majoration(simulateur, _chef(simulateur, 1940, 60, debut=40.0))
    assert majoration is None


def test_le_chef_de_moins_de_dix_sept_ans_et_demi_a_le_minimum_du_couple(simulateur):
    """Depuis 2002, douze ans de chef après trente de conjoint collaborateur :
    C = (MV2 - AVTS) / (37,5 × VP), MV2 étant l'écart entre le minimum d'un
    couple et celui d'une personne seule (D. 732-146)."""
    metiers = [Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 50.0, niveau_salaire=0.3)]
    carriere = _chef(simulateur, 1943, 62, metiers=metiers)
    majoration, _ = _majoration(simulateur, carriere)
    assert majoration is not None and majoration.detail.endswith("× 12 ans de chef")
    etages = simulateur.scenario_actuel.minimum_vieillesse.deux_etages(2005)
    seule = etages.avts + etages.supplementaire
    mv2 = 2 * etages.avts + etages.supplementaire_menage - seule
    assert mv2 < seule
    minimum = float(majoration.detail.split("(")[1].split(" - ")[0])
    assert minimum < 26.933


def test_une_pension_decotee_n_a_ni_pmr_ni_complement(simulateur):
    """Trente-deux ans de carrière à 62 ans : la décote, et aucun des deux
    minima, qui ne s'ouvrent qu'au taux plein."""
    _, avantages, _ = _resultat(simulateur, _chef(simulateur, 1957, 62, debut=30.0))
    assert not {"pension_majoree_reference", "complement_differentiel_rco"} & set(avantages)


def test_les_autres_pensions_ecretent_les_deux_minima(simulateur):
    """Vingt ans de salarié bien payé, puis vingt-quatre de chef
    d'exploitation : sa pension du régime général dépasse le plafond, et ni
    la PMR ni le complément, qui le regardent depuis 2021, ne lui sont
    servis."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=1.5),
               Metier("exploitant_agricole", 40.0, niveau_salaire=0.3)]
    _, avantages, _ = _resultat(simulateur, _chef(simulateur, 1958, 66, metiers=metiers))
    assert not {"pension_majoree_reference", "complement_differentiel_rco"} & set(avantages)


def test_la_majoration_pour_enfants_ne_porte_pas_sur_la_pmr(simulateur):
    """Une mère de trois enfants : les 10 % de D. 732-38 portent sur la
    pension calculée, non sur la majoration de L. 732-54-1 ; la PMR, elle,
    compte la majoration pour enfants dans les ressources qu'elle écrête."""
    carriere = _chef(simulateur, 1958, 66, sexe="F", nombre_enfants=3)
    _, avantages, pensions = _resultat(simulateur, carriere)
    pmr = avantages["pension_majoree_reference"].montant
    part = dict(avantages["majoration_enfants"].par_regime)["msa_non_salaries"]
    assert part == pytest.approx(0.10 * (pensions["msa_non_salaries"] - pmr))


# -- le statut : chef, collaborateur, chef à titre secondaire -------------------

def test_la_conjointe_collaboratrice_recoit_pmr2_et_ni_complement_ni_points(simulateur):
    """Quarante-quatre ans de conjointe collaboratrice, partie en 2016 au taux
    plein : la PMR au montant réduit, PMR2, sur toute sa durée (D. 732-111) ;
    ni les points gratuits de la RCO ni son complément différentiel, réservés
    aux années de chef (L. 732-56, II ; L. 732-63)."""
    metiers = [Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3)]
    carriere = _chef(simulateur, 1952, 64, sexe="F", metiers=metiers)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    pmr = simulateur.scenario_actuel.pension_majoree_reference
    reduite, _ = pmr.montant("pmr_conjoint", 2016, carriere.mois_liquidation)
    assert f"+ {reduite:,.2f} € × " in avantages["pension_majoree_reference"].detail
    assert not {"points_gratuits_rco", "complement_differentiel_rco"} & set(avantages)
    eligible = resultat.chef_d_exploitation.eligible
    assert eligible.chef == 0 and eligible.duree > 0


def test_une_carriere_melee_recoit_pmr1_et_pmr2_au_prorata(simulateur):
    """Vingt ans de collaborateur, puis vingt-quatre de chef, parti en 2019 :
    PMR1 sur les années de chef, retenues d'abord, PMR2 sur le reste ; le
    complément ne compte que les années de chef, et ses points gratuits celles
    de chef d'avant 2003."""
    metiers = [Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 40.0, niveau_salaire=0.3)]
    carriere = _chef(simulateur, 1955, 64, metiers=metiers)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    eligible = resultat.chef_d_exploitation.eligible
    assert 0 < eligible.chef < eligible.duree
    pmr = simulateur.scenario_actuel.pension_majoree_reference
    pleine, _ = pmr.montant("pmr_chef", 2019, carriere.mois_liquidation)
    reduite, _ = pmr.montant("pmr_conjoint", 2019, carriere.mois_liquidation)
    retenue = min(eligible.duree, eligible.reference)
    attendue = (pleine * eligible.chef + reduite * (retenue - eligible.chef)) / eligible.reference
    base = completer.pension_majoree(
        simulateur.scenario_actuel, carriere, eligible,
        SimpleNamespace(montant=0.0001), 0.0)
    assert base.avant_ecretement == pytest.approx(attendue, abs=1e-3)
    assert f"PMR {pleine:,.2f} € × {eligible.chef}/" in avantages[
        "pension_majoree_reference"].detail
    assert "× " + str(eligible.chef) + "/" in avantages["complement_differentiel_rco"].detail


def test_le_chef_de_moins_de_dix_sept_ans_et_demi_recoit_pmr1_depuis_2011(simulateur):
    """La condition de dix-sept ans et demi de chef pour PMR1 n'a valu que de
    2009 à 2010 (D. 732-110, II, 1°, rédaction de 2009) : un chef de seize ans,
    au taux plein par l'âge en 2016, reçoit PMR1."""
    carriere = _chef(simulateur, 1950, 66, debut=50.0)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    eligible = resultat.chef_d_exploitation.eligible
    assert eligible.chef == eligible.duree < 70
    assert "+ " not in avantages["pension_majoree_reference"].detail.split(", au taux")[0]


def test_le_chef_a_titre_secondaire_ne_compte_que_depuis_2026(simulateur):
    """Salarié, et chef d'exploitation à côté : ses années de chef à titre
    secondaire n'entrent dans les durées des deux minima qu'à compter de 2026
    (D. 732-110, D. 732-166-1), ni jamais dans les points gratuits."""
    for naissance, liquidation, depuis_2026 in ((1958, 66, False), (1965, 65, True)):
        metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
                   Metier("exploitant_agricole", 30.0, niveau_salaire=0.1, cumul=True)]
        carriere = _chef(simulateur, naissance, liquidation, metiers=metiers)
        annees = [a for a in range(carriere.lignes[0].annee, carriere.annee_liquidation)
                  if carriere.qualite_agricole(a) == "chef_secondaire"]
        assert annees and all(carriere.qualite_agricole(a) != "chef" for a in annees)
        resultat, avantages, _ = _resultat(simulateur, carriere)
        eligible = resultat.chef_d_exploitation.eligible
        assert eligible.chef == eligible.duree
        assert (eligible.duree > 0) == depuis_2026, (naissance, eligible)
        assert eligible.duree <= 4 * sum(1 for a in annees if a >= 2026)
        assert "points_gratuits_rco" not in avantages


# -- les deux moteurs -------------------------------------------------------------

#: Des chefs d'exploitation à faible revenu, de 2010 à 2030 : la PMR seule,
#: écrêtée ou non, le complément de 2015 et celui de 2021, une mère de trois
#: enfants avant et après 2026, une pension décotée.
# -- le relèvement des pensions prises avant septembre 2023 --------------------

def _rco_et_base(vivante):
    regimes = {r.regime: r for r in vivante.regimes}
    return regimes["msa_rco"], regimes["msa_non_salaries"]


def test_le_taux_plein_ouvre_en_2023_ce_que_la_duree_refusait(simulateur):
    """Parti en février 2016 au taux plein par l'âge, avec 124 trimestres de chef
    et sans la durée requise tous régimes : ni points gratuits ni complément à la
    liquidation. Le 1er septembre 2023, cent points par année de chef d'avant
    2003, et le complément différentiel au SMIC net agricole de ce jour, que
    portent ses deux pensions agricoles jusqu'à la cible proratisée
    (D. 732-166-5) ; ensuite, la valeur du point. Rien avant."""
    carriere = _chef(simulateur, 1950, 66, debut=35)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    assert not {"points_gratuits_rco", "complement_differentiel_rco"} & set(avantages)
    chef = resultat.chef_d_exploitation
    assert chef.eligible.taux_plein and not chef.eligible.duree_requise_atteinte
    assert (chef.gratuits, chef.complement) == (1800.0, False)
    assert faire_vivre(simulateur, carriere, resultat, 2022).relevement is None
    vivante = faire_vivre(simulateur, carriere, resultat, 2023)
    relevement = vivante.relevement
    assert (relevement.date, relevement.points_gratuits, relevement.smic_net) == (
        "2023-09-01", 1800.0, 9.0282)
    assert relevement.points_complement > 0
    valeur = valeur_du_point(simulateur.scenario_actuel, "msa_rco", carriere.date_liquidation)[0]
    rco, base = _rco_et_base(vivante)
    assert rco.relevement == pytest.approx(
        (1800 + relevement.points_complement) * relevement.valeur_point, rel=1e-12)
    # La formule de D. 732-166-4 au SMIC net de septembre 2023 et à la PMR des
    # pensions prises avant, 8 970,86 €, sous la cible proratisée : le point de
    # RCO et la pension de base ne bougent pas de septembre à décembre 2023.
    prorata = chef.eligible.duree / chef.eligible.reference
    cible = 0.85 * completer.HEURES_DU_COMPLEMENT * 9.0282
    vp = relevement.valeur_point
    formule = (cible - 8970.86) * prorata - (chef.points + 1800) * vp
    sous_la_cible = cible * prorata - (base.aujourd_hui + rco.au_depart * rco.coefficient
                                       + 1800 * vp)
    assert relevement.points_complement == math.floor(min(formule, sous_la_cible) / vp + 0.5)
    assert rco.aujourd_hui + base.aujourd_hui <= cible * prorata + vp
    assert rco.au_depart == pytest.approx(chef.points * valeur, rel=1e-9)
    en_2026 = faire_vivre(simulateur, carriere, resultat, 2026)
    assert _rco_et_base(en_2026)[0].relevement == pytest.approx(
        rco.relevement * en_2026.relevement.coefficient, rel=1e-12)


def test_une_pension_d_avant_2015_n_a_que_les_points_gratuits(simulateur):
    """Partie en 2012 : le modèle ne servant le complément qu'aux pensions prises
    depuis 2015, à leur liquidation, le relèvement n'ouvre que les points
    gratuits, comme il les ouvre depuis 2003 à qui avait la durée requise."""
    carriere = _chef(simulateur, 1945, 67, debut=40)
    resultat, _, _ = _resultat(simulateur, carriere)
    relevement = faire_vivre(simulateur, carriere, resultat, 2026).relevement
    assert (relevement.points_gratuits, relevement.points_complement) == (1800.0, 0)


def test_ce_que_la_duree_ouvrait_deja_n_est_pas_releve(simulateur):
    """La durée requise atteinte, les points gratuits et le complément sont ceux
    de la liquidation ; une pension prise depuis septembre 2023 les a reçus du
    taux plein. Ni l'une ni l'autre n'est relevée."""
    for carriere in (_chef(simulateur, 1950, 66, debut=20), _chef(simulateur, 1958, 67, debut=45)):
        resultat, _, _ = _resultat(simulateur, carriere)
        assert faire_vivre(simulateur, carriere, resultat, 2026).relevement is None


def test_l_echeancier_inscrit_le_relevement_a_sa_date(simulateur):
    """Un début de composante, que la loi induit, le 1er septembre 2023 : les
    points gratuits et ceux du complément, à la valeur du point de ce jour."""
    carriere = _chef(simulateur, 1950, 66, debut=35)
    echeancier = Echeancier(simulateur)
    entrees = {e.id: e for e in echeancier.parcourir(carriere, 2026)}
    evenement = entrees["relevement_des_exploitants_" + carriere.personne]
    assert (evenement.debut, evenement.contenu.sorte, evenement.contenu.origine) == (
        "2023-09-01", "debut_de_composante", "induit")
    relevement = faire_vivre(simulateur, carriere, echeancier.au_depart, 2026).relevement
    composante = entrees["relevement_msa_rco"].contenu
    assert composante["montant"]["annuel"] == pytest.approx(
        (relevement.points_gratuits + relevement.points_complement)
        * relevement.valeur_point, rel=1e-12)


REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "20", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "64", "naissance": "1955", "primes": "0",
    "profil": "ascendant", "projection": "cor_reference", "salaire": "0.3", "sexe": "H",
    "statut": "exploitant_agricole", "stock": "prix", "table": "unisexe",
}
CAS = [
    {"naissance": "1945", "liquidation": "65"},
    {"naissance": "1950", "liquidation": "62"},
    {"naissance": "1955"},
    {"naissance": "1958", "liquidation": "66", "enfants": "3", "sexe": "F"},
    {"naissance": "1962", "liquidation": "67", "salaire": "0.15", "debut": "35"},
    {"naissance": "1957", "liquidation": "62", "debut": "30"},
    {"naissance": "1965", "liquidation": "65", "enfants": "3", "sexe": "F"},
    # Le relèvement de septembre 2023 : au taux plein par l'âge, sans la durée
    # requise, parti en 2016 et en 2012.
    {"naissance": "1950", "liquidation": "66", "debut": "35"},
    {"naissance": "1945", "liquidation": "67", "debut": "40"},
    # La garantie que la MSA publie au 1er janvier 2022, 1 067,91 € par mois.
    {"naissance": "1960", "liquidation": "62"},
    # Le statut (étape 8) : une conjointe collaboratrice partie en 2016, à PMR2 ;
    # vingt ans de collaborateur puis de chef, en 2019 ; un salarié chef à titre
    # secondaire, parti en 2024 et en 2030.
    {"naissance": "1952", "sexe": "F", "statut": "collaborateur_agricole"},
    {"naissance": "1955", "statut": "collaborateur_agricole", "metier2_debut": "40",
     "metier2_statut": "exploitant_agricole", "metier2_salaire": "0.3"},
    {"naissance": "1958", "liquidation": "66", "statut": "salarie_prive_non_cadre",
     "metier2_debut": "30", "metier2_statut": "exploitant_agricole",
     "metier2_salaire": "0.1", "metier2_cumul": "oui"},
    {"naissance": "1965", "liquidation": "65", "statut": "salarie_prive_non_cadre",
     "metier2_debut": "30", "metier2_statut": "exploitant_agricole",
     "metier2_salaire": "0.1", "metier2_cumul": "oui"},
    # Les plans de revalorisation : au tiers en 1997, minorés sous vingt-deux
    # ans et demi en 1999, au minimum vieillesse en 2002, au minimum du couple
    # pour douze ans de chef en 2005.
    {"naissance": "1935", "liquidation": "62"},
    {"naissance": "1939", "liquidation": "60", "statut": "salarie_prive_non_cadre",
     "metier2_debut": "40", "metier2_statut": "exploitant_agricole", "metier2_salaire": "0.3"},
    {"naissance": "1942", "liquidation": "60"},
    {"naissance": "1943", "liquidation": "62", "statut": "collaborateur_agricole",
     "metier2_debut": "50", "metier2_statut": "exploitant_agricole", "metier2_salaire": "0.3"},
]


def test_les_deux_moteurs_servent_les_memes_minima_agricoles():
    """Chaque étape de la liquidation écrit la même donnée en Python et en
    JavaScript, minima des exploitants compris."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from test_liquidation import _ecarts, _python

    requetes = [{**REQUETE, **cas} for cas in CAS]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-liquidation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus, attendus = json.loads(execution.stdout), _python(requetes)
    codes = {d["code"] for a in attendus for l in a["liquidations"]
             for d in l["complements"]["dispositifs"]}
    assert {"pension_majoree_reference", "complement_differentiel_rco",
            "majoration_retraite_proportionnelle"} <= codes
    assert sum(any(e["id"] == "relevement_msa_rco" for e in a["journal"])
               for a in attendus) == 2
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
