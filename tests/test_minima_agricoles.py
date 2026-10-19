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
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.donnees.chargement import Fiabilite
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
    """Un chef né le 15 de son mois, que le test déclare au lieu de le présumer
    (action 135, levier 2) : né un 1er, il partirait un mois plus tôt
    (R. 351-37), en décembre plutôt qu'en janvier, ou le 1er janvier, sans
    l'année du départ, que L. 731-10-1 compte entière dès qu'il y travaille."""
    kwargs.setdefault("jour_naissance", 15)
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

def _recuperateur_de_la_pmr():
    """Le script qui écrit ``pension_majoree_reference.csv``."""
    chemin = RACINE / "scripts" / "fetch" / "dila_legi_pension_majoree.py"
    spec = importlib.util.spec_from_file_location("dila_legi_pension_majoree", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_les_montants_de_la_pmr_se_refont_de_leurs_ancres():
    """Le fichier est ce que son récupérateur écrit : les ancres de D. 732-111
    et D. 732-113, revalorisées par les coefficients de l'article L. 161-23-1
    au centime inférieur. Le plafond de juillet 2022 retrouve celui que la MSA
    publie, et la PMR des pensions de septembre 2023 vaut le minimum
    contributif majoré, que la loi lui fait suivre."""
    module = _recuperateur_de_la_pmr()
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


def test_la_pmr_et_le_plafond_d_avant_septembre_2023_suivent_les_pensions_de_base():
    """Les échéances d'après août 2023 des pensions prises avant septembre 2023
    lisent leur PMR et leur plafond (la PMR unique, la révision) : D. 732-111
    revalorise leur PMRmax comme les pensions de base ; leur plafond aussi, par
    le second alinéa de D. 732-113 de 2009, que le décret n° 2023-754 laisse
    au I en n'en remplaçant que le premier, la phrase du SMIC étant le second
    alinéa de son II (« Au premier alinéa du II », décret n° 2025-1410).
    8 970,86 € et 11 533,02 € de janvier 2023, revalorisés de 5,3, 2,2 et
    0,9 %, au centime inférieur : le plafond reste l'ASPA d'une personne
    seule, son minimum (L. 732-54-3), 1 012,02 € par mois en 2024. Le plafond
    du II suit le SMIC en 2026, quand se révisent les pensions prises de
    septembre 2023 à 2025 : 12 732,96 € menés comme le plafond de L. 173-2,
    de 1 352,23 à 1 410,89 € par mois."""
    valeurs = {(mesure, jour): valeur
               for mesure, jour, valeur, _ in _recuperateur_de_la_pmr().serie()}
    janviers = [f"{annee}-01-01" for annee in (2024, 2025, 2026)]
    assert [valeurs[("pmr_chef", jour)] for jour in janviers] == [9446.31, 9654.12, 9741.00]
    assert [valeurs[("plafond", jour)] for jour in janviers] == [12144.27, 12411.44, 12523.14]
    assert round(valeurs[("plafond", "2024-01-01")] / 12, 2) == 1012.02
    assert valeurs[("plafond_depuis_septembre_2023", "2026-01-01")] == 13285.31


def test_au_dela_du_dernier_bareme_la_pmr_d_avant_septembre_2023_suit_les_prix(simulateur):
    """En décembre 2026, la PMR entière des pensions prises avant septembre
    2023 est celle de la série, 9 741,00 €, et non les 9 567,86 € que le SMIC
    faisait de janvier 2023. Au-delà du dernier barème, elle et son plafond
    suivent les pensions de base, que le modèle revalorise sur les prix
    (D. 732-111, D. 732-113, I) ; la PMR et le plafond des pensions prises
    depuis, le SMIC, comme le minimum contributif et le plafond de L. 173-2."""
    pmr = simulateur.scenario_actuel.pension_majoree_reference
    macro = simulateur.macro
    assert pmr.montant("pmr_chef", 2026, 12) == (9741.00, Fiabilite.MOYENNE)
    assert pmr.montant("plafond", 2026, 12) == (12523.14, Fiabilite.MOYENNE)
    for mesure, en_2026 in (("pmr_chef", 9741.00), ("plafond", 12523.14)):
        valeur, fiabilite = pmr.montant(mesure, 2030, 6)
        assert valeur == pytest.approx(en_2026 * macro.coefficient_prix(2026, 2030), abs=1e-9)
        assert fiabilite == Fiabilite.ESTIMEE
    valeur, _ = pmr.montant("pmr_depuis_septembre_2023", 2030, 6)
    assert valeur == pytest.approx(10847.22 * macro.coefficient_smic(2026, 2030), abs=1e-9)
    valeur, _ = pmr.montant("plafond_depuis_septembre_2023", 2030, 6)
    assert valeur == pytest.approx(13605.47 * macro.coefficient_smic(2026, 2030), abs=1e-9)
    assert macro.coefficient_prix(2026, 2030) != macro.coefficient_smic(2026, 2030)


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
    en 2001 (décret n° 2001-170). Le chef de 2001 naît en décembre et part le
    1er janvier : parti en février, il compterait les trente points de l'année
    entière où il cesse (L. 731-10-1), et sa moyenne passerait les seize."""
    for naissance, mois, age, minimum, part in (
            (1935, 1, 62, 26.933, 1 / 3), (1937, 1, 61, 26.933, 2 / 3),
            (1939, 1, 60, 26.933, 1.0), (1940, 12, 60, 29.23, 1.0)):
        majoration, _ = _majoration(simulateur, _chef(simulateur, naissance, age,
                                                      mois_naissance=mois))
        assert majoration is not None, naissance
        assert f"({minimum:.3f} - " in majoration.detail
        assert majoration.detail.startswith(
            f"{(minimum - 16.0) * 37.5 * part:,.2f} points"), majoration.detail


def test_les_points_se_minorent_sous_vingt_deux_ans_et_demi_de_chef(simulateur):
    """Vingt et un ans de chef en 1999, après vingt de salarié — vingt, et
    l'année du départ, que le chef compte entière (L. 731-10-1) — : il en
    manque un et demi, 15 + la moitié de 15 %, vingt-deux et demi pour cent
    de moins."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 40.0, niveau_salaire=0.3)]
    majoration, _ = _majoration(simulateur, _chef(
        simulateur, 1939, 60, metiers=metiers, mois_naissance=1, jour_naissance=15))
    assert majoration is not None
    points = float(majoration.detail.split(" points")[0].replace(",", ""))
    minimum, moyenne = (float(x) for x in
                        majoration.detail.split("(")[1].split(")")[0].split(" - "))
    assert majoration.detail.endswith("× 21 ans de chef")
    assert points == pytest.approx((minimum - moyenne) * 21 * 0.775, abs=0.02)


def test_ni_plan_avant_1997_ni_sans_le_taux_plein(simulateur):
    """Une pension de 1996 n'a pas le minimum à la liquidation ; vingt ans de
    chef partis à soixante ans en 2000, sans la durée requise, non plus."""
    majoration, _ = _majoration(simulateur, _chef(simulateur, 1934, 62))
    assert majoration is None
    majoration, _ = _majoration(simulateur, _chef(simulateur, 1940, 60, debut=40.0))
    assert majoration is None


def test_le_forfait_que_les_plans_retranchent_ne_compte_pas_les_annees_secondaires(simulateur):
    """Salarié, chef à titre secondaire de 1982 à 1985, puis à titre principal,
    parti en 2005 : ses années secondaires n'ouvrent que la retraite
    proportionnelle (L. 732-28). La moyenne n des plans se lit sur la pension
    moins le forfait qu'elle porte, qui ne les compte pas, en points par année
    d'assurance (décret n° 2002-297, article 4 ; D. 732-144)."""
    from retraite_notionnelle.droit import ouvrir, releve
    from retraite_notionnelle.droit.commun import periode_de_liquidation

    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 42.0, niveau_salaire=0.3, cumul=True,
                      age_fin=46.0),
               Metier("exploitant_agricole", 46.0, niveau_salaire=0.5)]
    carriere = _chef(simulateur, 1940, 65, metiers=metiers)
    par_annee = releve.construire(simulateur.scenario_actuel, carriere).durees.par_annee[
        "assurance"]["msa_non_salaries"]
    secondaires = [a for a in par_annee if carriere.qualite_agricole(a) == "chef_secondaire"]
    assert secondaires == list(range(1982, 1986)) and min(par_annee) == 1982
    resultat, avantages, _ = _resultat(simulateur, carriere)
    exploitant = resultat.exploitant_agricole
    periode = periode_de_liquidation(simulateur.scenario_actuel.catalogue[exploitant.regime],
                                     carriere.date_liquidation)
    requis, _ = ouvrir.duree_requise(simulateur.scenario_actuel, periode, carriere)
    points = _points_au_compte(simulateur, resultat,
                               sum(min(par_annee[a], 4) for a in secondaires))
    # Les points de la liquidation, à la valeur d'une année de la durée requise.
    moyenne = points * requis / 4.0 / 37.5 / min(exploitant.trimestres / 4.0, 37.5)
    assert moyenne > 16.0
    assert f" - {moyenne:.3f}) × " in avantages["majoration_retraite_proportionnelle"].detail


def _base(vivante):
    return next(r for r in vivante.regimes if r.regime == "msa_non_salaries")


def test_les_plans_se_servent_aux_pensions_deja_liquidees(simulateur):
    """Partie en 1997 : les points ajoutés, servis au tiers à la liquidation, le
    sont aux deux tiers en 1998, entiers en 1999, à 29,23 en 2001, au minimum
    vieillesse de chaque année depuis 2002 (décret n° 97-163, article 3 ; décret
    n° 2001-170, article 3 ; décret n° 2002-297, article 4) ; ceux de 2008
    restent, et suivent la valeur du point (D. 732-112)."""
    carriere = _chef(simulateur, 1935, 62)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    assert avantages["majoration_retraite_proportionnelle"].detail.startswith(
        f"{(26.933 - 16.0) * 37.5 / 3:,.2f} points")
    assert faire_vivre(simulateur, carriere, resultat, 1997).exploitant is None
    for annee, minimum, part in ((1998, 26.933, 2 / 3), (1999, 26.933, 1.0),
                                 (2001, 29.23, 1.0)):
        revision = faire_vivre(simulateur, carriere, resultat, annee).exploitant
        assert revision.annee_des_plans == annee
        assert revision.points_servis == pytest.approx((minimum - 16.0) * 37.5 * part,
                                                       rel=1e-12)
    en_2008 = faire_vivre(simulateur, carriere, resultat, 2008)
    en_2026 = faire_vivre(simulateur, carriere, resultat, 2026)
    assert en_2008.exploitant.points_servis > (29.23 - 16.0) * 37.5
    assert en_2026.exploitant.annee_des_plans == 2008
    assert en_2026.exploitant.points_servis == en_2008.exploitant.points_servis
    # Les points de 2008, et non ceux de la liquidation, suivent le coefficient.
    plans = (_base(en_2008).plans + avantages["majoration_retraite_proportionnelle"].montant
             * _base(en_2008).coefficient)
    assert _base(en_2026).plans + (avantages["majoration_retraite_proportionnelle"].montant
                                   * _base(en_2026).coefficient) == pytest.approx(
        plans * _base(en_2026).coefficient / _base(en_2008).coefficient, rel=1e-9)


def test_la_minoration_tombe_en_2001(simulateur):
    """Vingt et un ans de chef, partis en 1999 (l'année du départ comptée
    entière, L. 731-10-1) : les points minorés à la liquidation ne le sont
    plus depuis 2001, « le IV de l'article 1er
    est supprimé » (décret n° 2001-170, article 3)."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 40.0, niveau_salaire=0.3)]
    carriere = _chef(simulateur, 1939, 60, metiers=metiers, mois_naissance=1,
                     jour_naissance=15)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    detail = avantages["majoration_retraite_proportionnelle"].detail
    moyenne = float(detail.split("(")[1].split(")")[0].split(" - ")[1])
    revision = faire_vivre(simulateur, carriere, resultat, 2001).exploitant
    assert revision.points_servis == pytest.approx((29.23 - moyenne) * 21, abs=0.02)


# -- les pensions prises avant 1997, révisées de 1997 à 2008 ---------------------

def _points_au_compte(simulateur: Simulateur, resultat, hors_forfait: int = 0) -> float:
    """Les points de retraite proportionnelle au compte de la liquidation : la
    pension avant surcote, moins la retraite forfaitaire qu'elle porte, à la
    valeur du point de la liquidation. Le forfait ne compte pas les
    ``hors_forfait`` trimestres de chef à titre secondaire (L. 732-28)."""
    from retraite_notionnelle.droit import liquider, ouvrir
    from retraite_notionnelle.droit.commun import periode_de_liquidation

    actuel = simulateur.scenario_actuel
    exploitant = resultat.exploitant_agricole
    carriere = exploitant.carriere
    periode = periode_de_liquidation(actuel.catalogue[exploitant.regime],
                                     carriere.date_liquidation)
    requis, _ = ouvrir.duree_requise(actuel, periode, carriere)
    proratisation, _ = liquider.duree_proratisation(actuel, periode, carriere, requis)
    forfait = periode.pension_forfaitaire_annuelle * actuel.macro.coefficient_prix(
        periode.pension_forfaitaire_annee, carriere.annee_liquidation)
    lu = valeur_du_point(actuel, exploitant.regime, carriere.date_liquidation)
    valeur = (lu[0] if lu is not None
              else liquider.valeur_point_fiche(actuel, periode, carriere.annee_liquidation))
    return (exploitant.pension.montant / exploitant.eligible.surcote
            - forfait * min(exploitant.trimestres - hors_forfait, proratisation)
            / proratisation) / valeur


def _servis(simulateur: Simulateur, carriere: Carriere, resultat, annee: int) -> float:
    """Les points des plans servis à l'échéance de ``annee``."""
    revision = faire_vivre(simulateur, carriere, resultat, annee).exploitant
    assert revision is not None, annee
    assert revision.annee_des_plans == min(annee, 2008), annee
    return revision.points_servis


def _a_moins_seize(simulateur: Simulateur, annee: int) -> float:
    """A - 16 des pensions dues en ``annee`` depuis 2002 : celui d'une carrière
    complète de chef partie en 1997, que les plans portent à (A - 16) × 37,5
    points ; le décret n° 2002-297 donne le même A aux pensions prises avant
    1997 (article 5) et à celles prises de 1997 à 2001 (article 4)."""
    carriere = _chef(simulateur, 1935, 62)
    resultat, _, _ = _resultat(simulateur, carriere)
    return _servis(simulateur, carriere, resultat, annee) / 37.5


def test_les_pensions_prises_avant_1997_sont_revisees_des_1997(simulateur):
    """Une carrière complète de chef partie en 1995 à faible revenu : sa durée
    de chef se reconstitue de ses points divisés par seize, et la moyenne n
    vaut donc seize ; P = (A - n) × d, A valant 20 en 1997 — servis au tiers —
    et en 1998 — aux deux tiers —, 23,9 en 1999, 26,96 en 2000, 29,23 en 2001
    (décret n° 97-163, articles 2 et 3 ; décret n° 99-141 ; décret
    n° 2000-261 ; décret n° 2001-170 et son rectificatif), puis
    (MV1 - AVTS) / (37,5 × VP) (décret n° 2002-297, article 5 ; D. 732-116) ;
    les points de 2008 restent."""
    carriere = _chef(simulateur, 1930, 65)
    resultat, _, _ = _resultat(simulateur, carriere)
    assert resultat.exploitant_agricole.plans is None
    assert faire_vivre(simulateur, carriere, resultat, 1996).exploitant is None
    duree = _points_au_compte(simulateur, resultat) / 16.0
    assert 17.5 < duree < resultat.exploitant_agricole.eligible.duree / 4.0
    for annee, minimum_moins_seize, part in ((1997, 4.0, 1 / 3), (1998, 4.0, 2 / 3),
                                             (1999, 7.9, 1.0), (2000, 10.96, 1.0),
                                             (2001, 13.23, 1.0)):
        assert _servis(simulateur, carriere, resultat, annee) == pytest.approx(
            minimum_moins_seize * duree * part, rel=1e-9), annee
    for annee in (2002, 2008):
        assert _servis(simulateur, carriere, resultat, annee) == pytest.approx(
            _a_moins_seize(simulateur, annee) * duree, rel=1e-9), annee
    assert (_servis(simulateur, carriere, resultat, 2026)
            == _servis(simulateur, carriere, resultat, 2008))


def test_la_duree_reconstituee_se_borne_a_la_duree_agricole(simulateur):
    """Plus de seize points par an : la durée reconstituée dépasse les
    quarante-quatre ans d'activité agricole, et y est ramenée ; n est alors
    les points divisés par cette durée, d en retient trente-sept et demie
    (décret n° 97-163, article 2, I et II). Depuis 2002, la durée est ramenée
    à trente-sept ans et demi au plus, et n se divise par elle (décret
    n° 2002-297, article 5)."""
    carriere = _chef(simulateur, 1930, 65, niveau=0.6)
    resultat, _, _ = _resultat(simulateur, carriere)
    points = _points_au_compte(simulateur, resultat)
    agricole = resultat.exploitant_agricole.eligible.duree / 4.0
    assert points / 16.0 > agricole > 37.5 and points / agricole < 20.0
    for annee, minimum, part in ((1997, 20.0, 1 / 3), (1999, 23.9, 1.0)):
        assert _servis(simulateur, carriere, resultat, annee) == pytest.approx(
            (minimum - points / agricole) * 37.5 * part, rel=1e-9), annee
    assert _servis(simulateur, carriere, resultat, 2002) == pytest.approx(
        (_a_moins_seize(simulateur, 2002) + 16.0 - points / 37.5) * 37.5, rel=1e-9)


def test_la_revision_veut_trente_deux_ans_et_demi_puis_vingt_deux_et_demi(simulateur):
    """Vingt-six ans de chef partis en 1995 : rien tant que la révision veut
    trente-deux ans et demi d'activité agricole ; depuis 2007, vingt-deux et
    demi, les points minorés de 5,5 % par année manquante sous trente-sept et
    demie, de 4 % en 2008 (décret n° 2006-1638, article 2 ; D. 732-115,
    D. 732-117). Le taux plein n'est pas demandé."""
    carriere = _chef(simulateur, 1930, 65, debut=40.0)
    resultat, _, _ = _resultat(simulateur, carriere)
    agricole = resultat.exploitant_agricole.eligible.duree / 4.0
    duree = _points_au_compte(simulateur, resultat) / 16.0
    assert 22.5 <= agricole < 32.5 and 17.5 < duree < agricole
    for annee in (1997, 2001, 2006):
        assert faire_vivre(simulateur, carriere, resultat, annee).exploitant is None, annee
    for annee, taux in ((2007, 0.055), (2008, 0.04)):
        assert _servis(simulateur, carriere, resultat, annee) == pytest.approx(
            _a_moins_seize(simulateur, annee) * duree * (1.0 - taux * (37.5 - agricole)),
            rel=1e-9), annee


def test_la_revision_se_minore_au_plus_fort_des_deux_coefficients(simulateur):
    """Sous vingt-deux ans et demi de chef reconstitués, et sous trente-sept
    et demi d'activité agricole, deux coefficients : seul le plus élevé
    s'applique (décret n° 97-163, article 2, III à V), de 15 %, 15 %, 20 %…
    par année manquante en 1997, de 15 %, 15 %, 10 %… depuis 1999 (décret
    n° 99-141) ; le premier tombe en 2001 (décret n° 2001-170). Sous dix-sept
    ans et demi reconstitués, rien, quels que soient les ans de chef."""
    def minoration(coefficients, manque):
        return sum(c * min(1.0, manque - rang)
                   for rang, c in enumerate(coefficients) if manque > rang)

    de_1997, de_1999 = [0.15, 0.15, 0.20, 0.20, 0.20, 0.10], [0.15, 0.15, 0.10, 0.10, 0.10, 0.40]
    for debut, niveau in ((26.0, 0.3), (29.0, 0.8)):
        carriere = _chef(simulateur, 1932, 62, niveau=niveau, debut=debut)
        resultat, _, _ = _resultat(simulateur, carriere)
        agricole = resultat.exploitant_agricole.eligible.duree / 4.0
        duree = _points_au_compte(simulateur, resultat) / 16.0
        assert 32.5 <= agricole < 37.5 and 17.5 <= duree < agricole
        for annee, minimum_moins_seize, part, du_chef, de_la_duree in (
                (1997, 4.0, 1 / 3, de_1997, de_1997), (1999, 7.9, 1.0, de_1999, de_1999),
                (2001, 13.23, 1.0, [], de_1999)):
            taux = max(minoration(du_chef, 22.5 - duree),
                       minoration(de_la_duree, 37.5 - agricole))
            assert _servis(simulateur, carriere, resultat, annee) == pytest.approx(
                minimum_moins_seize * duree * part * (1.0 - taux), rel=1e-9), (debut, annee)
    # Aux cinquante-cinq centièmes du salaire moyen : aux six dixièmes, les
    # points de 1994, l'année entière où il cesse (L. 731-10-1), passeraient
    # les dix-sept ans et demi.
    carriere = _chef(simulateur, 1932, 62, niveau=0.55, debut=29.0)
    resultat, _, _ = _resultat(simulateur, carriere)
    assert _points_au_compte(simulateur, resultat) / 16.0 < 17.5
    assert faire_vivre(simulateur, carriere, resultat, 2008).exploitant is None


def _pmr_sur_la_duree_reconstituee(simulateur: Simulateur, annee: int, chef: float,
                                   agricole: float) -> float:
    """La PMR de décembre de ``annee``, de 2009 à 2021 : PMR1 sur la durée de
    chef, en années, PMR2 sur le reste de la durée agricole, l'une et l'autre
    sur les trente-sept ans et demi de DR, DM1 retenue en priorité et DM1 + DM2
    au plus DR (D. 732-111)."""
    pmr = simulateur.scenario_actuel.pension_majoree_reference
    retenue = min(agricole, 37.5)
    return (pmr.montant("pmr_chef", annee, 12)[0] * min(chef, retenue)
            + pmr.montant("pmr_conjoint", annee, 12)[0] * (retenue - min(chef, retenue))) / 37.5


def test_la_pmr_de_2009_s_ouvre_aux_pensions_prises_avant(simulateur):
    """Une carrière complète de chef partie en 1995, que les plans révisent de
    1997 à 2008, est portée le 1er janvier 2009 à la pension majorée de
    référence (loi n° 2008-1330, article 77 ; D. 732-109 à D. 732-112) ; rien
    avant. Sa durée de chef est celle que ses points au compte, divisés par
    seize, reconstituent : trente ans sur ses quarante-quatre, PMR1 sur eux,
    PMR2 sur le reste de DR (D. 732-110, III ; D. 732-111) ; depuis 2022, la
    PMR unique, entière."""
    carriere = _chef(simulateur, 1930, 65)
    resultat, _, _ = _resultat(simulateur, carriere)
    assert resultat.exploitant_agricole.plans is None
    en_2008 = faire_vivre(simulateur, carriere, resultat, 2008).exploitant
    assert en_2008.plans > 0 and en_2008.pmr == 0 and en_2008.pmr_entiere is None
    chef = _points_au_compte(simulateur, resultat) / 16.0
    agricole = resultat.exploitant_agricole.eligible.duree / 4.0
    assert 17.5 < chef < 37.5 < agricole
    for annee in (2009, 2021):
        vivante = faire_vivre(simulateur, carriere, resultat, annee)
        assert vivante.exploitant.pmr > 0
        assert _base(vivante).aujourd_hui == pytest.approx(
            _pmr_sur_la_duree_reconstituee(simulateur, annee, chef, agricole), rel=1e-12), annee
    vivante = faire_vivre(simulateur, carriere, resultat, 2026)
    assert vivante.exploitant.pmr > 0
    assert _base(vivante).aujourd_hui == pytest.approx(vivante.exploitant.pmr_entiere,
                                                       rel=1e-12)
    pmr = simulateur.scenario_actuel.pension_majoree_reference.montant("pmr_chef", 2026, 12)
    assert vivante.exploitant.pmr_entiere == pytest.approx(pmr[0], rel=1e-12)


def test_sous_dix_sept_ans_et_demi_reconstitues_la_pmr_de_2009_ne_sert_que_pmr2(simulateur):
    """Vingt-huit ans et trois quarts de chef partis en 1995 à faible revenu :
    leurs points au compte ne reconstituent pas treize ans de chef, sous les
    dix-sept ans et demi qu'exige le 1° de D. 732-110, II, dans sa rédaction
    de 2009 ; en 2009 et 2010, toute la durée est servie à PMR2 (D. 732-110,
    II, 4°, et III). Depuis 2011, la condition tombée, PMR1 sur la durée
    reconstituée, PMR2 sur le reste ; depuis 2022, la PMR unique."""
    carriere = _chef(simulateur, 1930, 65, niveau=0.1)
    resultat, _, _ = _resultat(simulateur, carriere)
    chef = _points_au_compte(simulateur, resultat) / 16.0
    agricole = resultat.exploitant_agricole.eligible.duree / 4.0
    assert chef < 17.5 <= 22.5 <= agricole < 37.5
    for annee, retenue in ((2009, 0.0), (2010, 0.0), (2011, chef), (2021, chef)):
        vivante = faire_vivre(simulateur, carriere, resultat, annee)
        assert _base(vivante).aujourd_hui == pytest.approx(
            _pmr_sur_la_duree_reconstituee(simulateur, annee, retenue, agricole),
            rel=1e-12), annee
    vivante = faire_vivre(simulateur, carriere, resultat, 2022)
    assert _base(vivante).aujourd_hui == pytest.approx(
        vivante.exploitant.pmr_entiere * agricole / 37.5, rel=1e-12)


def test_la_duree_reconstituee_perd_quinze_points_par_annee_secondaire(simulateur):
    """Salarié, chef à titre secondaire de 1982 à 1986, sans le forfait
    (L. 732-28), puis chef à titre principal, parti en 1996 : la durée de chef
    se reconstitue des points au compte moins quinze par année secondaire sans
    forfait, divisés par seize (D. 732-110, III) — sans la minoration, elle
    dépasserait la durée agricole et y serait ramenée. Servie depuis février
    2014, quand la PMR ne demande plus de durée minimale (D. 732-109)."""
    from retraite_notionnelle.droit import releve

    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 51.0, niveau_salaire=0.1, cumul=True,
                      age_fin=56.0),
               Metier("exploitant_agricole", 56.0, niveau_salaire=0.1)]
    carriere = _chef(simulateur, 1931, 65, metiers=metiers)
    assert carriere.annee_liquidation == 1996
    par_annee = releve.construire(simulateur.scenario_actuel, carriere).durees.par_annee[
        "assurance"]["msa_non_salaries"]
    secondaires = [a for a in par_annee if carriere.qualite_agricole(a) == "chef_secondaire"]
    assert secondaires == list(range(1982, 1987)) and min(par_annee) == 1982
    resultat, _, _ = _resultat(simulateur, carriere)
    points = _points_au_compte(simulateur, resultat,
                               sum(min(par_annee[a], 4) for a in secondaires))
    chef = (points - 15.0 * len(secondaires)) / 16.0
    agricole = resultat.exploitant_agricole.eligible.duree / 4.0
    assert 0.0 < chef < agricole < points / 16.0
    for annee in (2015, 2021):
        vivante = faire_vivre(simulateur, carriere, resultat, annee)
        assert vivante.exploitant.pmr > 0
        assert _base(vivante).aujourd_hui == pytest.approx(
            _pmr_sur_la_duree_reconstituee(simulateur, annee, chef, agricole),
            rel=1e-12), annee


def test_la_pmr_d_une_pension_d_avant_2002_ne_veut_pas_le_taux_plein(simulateur):
    """Vingt ans de chef partis à soixante ans en 2000 sans la durée requise :
    ni plans, ni PMR en 2009 et 2010, faute de vingt-deux ans et demi dans le
    régime ; depuis 2011, dix-sept ans et demi suffisent, et le taux plein
    n'est pas demandé aux pensions prises avant 2002 (D. 732-109, 1°). Partie
    en 2004 sans lui, la même carrière n'a rien (D. 732-109, 2°)."""
    carriere = _chef(simulateur, 1940, 60, debut=40.0)
    resultat, _, _ = _resultat(simulateur, carriere)
    assert not resultat.exploitant_agricole.eligible.taux_plein
    assert faire_vivre(simulateur, carriere, resultat, 2010).exploitant is None
    vivante = faire_vivre(simulateur, carriere, resultat, 2011)
    eligible = resultat.exploitant_agricole.eligible
    assert _base(vivante).aujourd_hui == pytest.approx(
        vivante.exploitant.pmr_entiere * eligible.duree / eligible.reference, rel=1e-12)
    carriere = _chef(simulateur, 1944, 60, debut=40.0)
    resultat, _, _ = _resultat(simulateur, carriere)
    assert not resultat.exploitant_agricole.eligible.taux_plein
    assert faire_vivre(simulateur, carriere, resultat, 2026).exploitant is None



def test_la_pmr_unique_de_2022_se_sert_aux_pensions_prises_depuis_2009(simulateur):
    """Une conjointe collaboratrice partie en 2016 à PMR2, et vingt ans de
    collaborateur puis vingt-quatre de chef partis en 2019 : leur majoration,
    calculée au départ et menée par le coefficient, se refait depuis le
    1er janvier 2022 au montant unique (loi n° 2021-1679, article 1er, II ;
    décret n° 2021-1919, article 2) ; rien ne change en 2021. La carrière
    complète sans surcote est portée à la PMR entière."""
    pmr = simulateur.scenario_actuel.pension_majoree_reference
    collaboratrice = _chef(simulateur, 1952, 64, sexe="F", metiers=[
        Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3)])
    melee = _chef(simulateur, 1957, 62, metiers=[
        Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3),
        Metier("exploitant_agricole", 40.0, niveau_salaire=0.3)])
    for carriere in (collaboratrice, melee):
        resultat, avantages, _ = _resultat(simulateur, carriere)
        assert resultat.exploitant_agricole.pmr == pytest.approx(
            avantages["pension_majoree_reference"].montant, rel=1e-12)
        assert faire_vivre(simulateur, carriere, resultat, 2021).exploitant is None
        for annee in (2022, 2026):
            vivante = faire_vivre(simulateur, carriere, resultat, annee)
            assert vivante.exploitant.pmr > 0
            assert vivante.exploitant.pmr_entiere == pytest.approx(
                pmr.montant("pmr_chef", annee, 12)[0], rel=1e-12)
    assert _base(vivante).aujourd_hui == pytest.approx(vivante.exploitant.pmr_entiere,
                                                       rel=1e-12)


def test_la_pmr_unique_garde_la_duree_minimale_du_depart(simulateur):
    """Quinze ans de chef après une carrière de salarié, parti au taux plein en
    2012 : sous les soixante-dix trimestres que D. 732-109 demandait alors, ni
    PMR au départ, ni en 2022, la règle unique n'ouvrant pas une majoration
    refusée à la liquidation."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 47.0, niveau_salaire=0.3)]
    carriere = _chef(simulateur, 1950, 62, metiers=metiers)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    assert resultat.exploitant_agricole.eligible.taux_plein
    assert resultat.exploitant_agricole.eligible.duree < 70
    assert "pension_majoree_reference" not in avantages
    assert faire_vivre(simulateur, carriere, resultat, 2022).exploitant is None

def test_le_chef_de_moins_de_dix_sept_ans_et_demi_a_le_minimum_du_couple(simulateur):
    """Depuis 2002, treize ans de chef — douze, et l'année du départ, comptée
    entière (L. 731-10-1) — après trente de conjoint collaborateur :
    C = (MV2 - AVTS) / (37,5 × VP), MV2 étant l'écart entre le minimum d'un
    couple et celui d'une personne seule (D. 732-146)."""
    metiers = [Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 50.0, niveau_salaire=0.3)]
    carriere = _chef(simulateur, 1943, 62, metiers=metiers, mois_naissance=1,
                     jour_naissance=15)
    majoration, _ = _majoration(simulateur, carriere)
    assert majoration is not None and "× 13 ans de chef + " in majoration.detail
    etages = simulateur.scenario_actuel.minimum_vieillesse.deux_etages(2005)
    seule = etages.avts + etages.supplementaire
    mv2 = 2 * etages.avts + etages.supplementaire_menage - seule
    assert mv2 < seule
    minimum = float(majoration.detail.split("(")[1].split(" - ")[0])
    assert minimum < 26.933


def _annee_des_conjoints(carriere: Carriere) -> int:
    """L'année d'effet des revalorisations des conjoints : celle d'avant, pour
    une pension prise un 1er janvier (D. 732-120, D. 732-142)."""
    from retraite_notionnelle.droit.commun import date_d_effet
    effet = date_d_effet(carriere)
    return int(effet[:4]) - (1 if effet[5:] == "01-01" else 0)


def _plans(simulateur: Simulateur, carriere: Carriere, quand: str | None = None):
    """Les plans de ``carriere``, à la liquidation ou dus au 1er janvier ``quand``."""
    exploitant = simulateur.scenario_actuel.calculer(carriere).exploitant_agricole
    return exploitant, completer.majoration_retraite_proportionnelle(
        simulateur.scenario_actuel, carriere, exploitant.eligible, exploitant.pension,
        exploitant.trimestres, quand=quand)


def test_les_annees_de_conjoint_recoivent_b_moins_seize_points(simulateur):
    """Quarante-deux ans de conjointe collaboratrice, partie en 2005 au taux
    plein : chaque année reçoit B - 16 points, B = (MV2 - AVTS) / (37,5 × VP),
    le C du chef de moins de dix-sept ans et demi (D. 732-145, D. 732-146) ;
    celles d'avant 1999 se minorent de six, l'écart de 2005 à 1999 : six ans
    depuis 1999, trente avant (D. 732-142)."""
    conjointe = _chef(simulateur, 1943, 62, sexe="F",
                      metiers=[Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3)])
    exploitant, plans = _plans(simulateur, conjointe)
    eligible, an = exploitant.eligible, _annee_des_conjoints(conjointe)
    assert eligible.chef == 0 and conjointe.annee_liquidation == 2005
    attendues = (eligible.collaborateur_regularise / 4
                 + min(eligible.conjoint_avant_1999 / 4 - (an - 1999), 37.5 - (an - 1998)))
    assert plans.duree == 0.0 and 35.0 <= attendues <= 37.0
    assert plans.conjoint_annees == pytest.approx(attendues, abs=1e-12)
    assert plans.points == pytest.approx((plans.conjoint_minimum - 16.0) * attendues,
                                         rel=1e-12)
    melee = _chef(simulateur, 1943, 62, metiers=[
        Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3),
        Metier("exploitant_agricole", 50.0, niveau_salaire=0.3)],
        mois_naissance=1, jour_naissance=15)
    du_chef, plans_du_chef = _plans(simulateur, melee)
    assert plans_du_chef.minimum == pytest.approx(plans.conjoint_minimum, rel=1e-12)
    # Treize ans de chef d'abord, l'année du départ comptée entière
    # (L. 731-10-1), puis trente d'avant 1999 moins six.
    assert du_chef.eligible.chef == 52 and du_chef.eligible.conjoint_avant_1999 == 120
    assert plans_du_chef.conjoint_annees == 30 - (_annee_des_conjoints(melee) - 1999)
    majoration, _ = _majoration(simulateur, conjointe)
    assert majoration.detail.endswith(f"- 16) × {attendues:g} ans de conjoint")


def test_les_conjoints_partis_avant_2002_sont_servis_depuis_2002(simulateur):
    """Trente ans de conjointe, partie en 2000 : rien à la liquidation ; depuis
    2002, B - 16 points par année, minorés de 15, 15, 10, 10 et 10 % sous
    trente-sept ans et demi, vingt-sept et demi suffisant à quinze ans de
    conjoint sans autre pension, sans rien au-delà de la cinquième année
    manquante (décret n° 2002-297, articles 6 et 8) ; 5,5 % par année
    manquante en 2007, 4 % en 2008 (D. 732-131). Salariée d'abord, il lui
    faut trente-deux ans et demi jusqu'en 2006, vingt-deux et demi depuis
    (D. 732-118)."""
    seule = _chef(simulateur, 1938, 62, sexe="F",
                  metiers=[Metier("collaborateur_agricole", 32.0, niveau_salaire=0.3)])
    exploitant, plans = _plans(simulateur, seule)
    eligible = exploitant.eligible
    manque = 37.5 - eligible.duree / 4
    assert plans is None and seule.annee_liquidation == 2000 and 5.0 < manque < 10.0
    # Depuis 1999, et avant, moins un (rien, partie le 1er janvier 2000).
    annees = (eligible.collaborateur_regularise / 4 + eligible.conjoint_avant_1999 / 4
              - max(0, _annee_des_conjoints(seule) - 1999))
    for quand, minoration in (("2002-01-01", 0.6), ("2007-01-01", 0.055 * manque),
                              ("2008-01-01", 0.04 * manque)):
        _, plans = _plans(simulateur, seule, quand)
        assert plans.conjoint_annees == pytest.approx(annees, abs=1e-12)
        assert plans.points == pytest.approx(
            (plans.conjoint_minimum - 16.0) * annees * (1.0 - minoration), rel=1e-12), quand
    salariee = _chef(simulateur, 1938, 62, sexe="F", metiers=[
        Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
        Metier("collaborateur_agricole", 32.0, niveau_salaire=0.3)])
    assert _plans(simulateur, salariee, "2006-01-01")[1] is None
    _, plans = _plans(simulateur, salariee, "2007-01-01")
    assert plans.points == pytest.approx(
        (plans.conjoint_minimum - 16.0) * annees * (1.0 - 0.055 * manque), rel=1e-12)
    revision = faire_vivre(simulateur, seule, simulateur.scenario_actuel.calculer(seule),
                           2005).exploitant
    assert revision.annee_des_plans == 2005 and revision.points_servis > 0.0


def test_les_annees_de_conjoint_d_avant_1999_se_bornent_a_l_ecart_avec_1998(simulateur):
    """Quarante-deux ans de conjointe, partie en 2001 : quarante avant 1999,
    moins deux, et au plus trente-sept et demie moins trois ; deux depuis
    (D. 732-119, D. 732-123) — un an de moins à chaque écart, partie le 1er
    janvier."""
    conjointe = _chef(simulateur, 1939, 62, sexe="F",
                      metiers=[Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3)])
    exploitant, plans = _plans(simulateur, conjointe, "2002-01-01")
    eligible, an = exploitant.eligible, _annee_des_conjoints(conjointe)
    assert conjointe.annee_liquidation == 2001
    assert eligible.conjoint_avant_1999 / 4 - (an - 1999) > 37.5 - (an - 1998)
    assert plans.conjoint_annees == pytest.approx(
        37.5 - (an - 1998) + eligible.collaborateur_regularise / 4, abs=1e-12)


def test_les_pensions_dues_de_1998_a_2001_servent_les_points_de_leurs_decrets(simulateur):
    """Trente-cinq ans et demi de conjointe, partie en juillet 1998 : 8,63
    points par année revalorisable en 1998 (décret n° 99-875, article 3),
    11,44 en 1999 (article 4), 16 en 2000 (décret n° 2000-261, article 5, IV) —
    que les seize points que le modèle donne déjà à chacune de ses années
    dépassent ou égalent : rien —, puis, en 2001, seize points et le
    différentiel de 3,2 (décret n° 2001-170, article 5, III) : 3,2 de plus par
    année, minorés de 15 % pour chacune des deux années qui manquent à
    trente-sept et demie (article 2-2). Trente et un ans de conjointe, partie
    en février 2000 : vingt-sept ans et demi suffisent depuis les pensions
    dues en 2000 à qui a quinze ans de conjoint sans autre pension, sans
    coefficient au-delà de la cinquième année manquante, et ses années d'avant
    1999 perdent l'écart avec 1999 (articles 2 et 2-2)."""
    conjointe = _chef(simulateur, 1936, 62, sexe="F", mois_naissance=6,
                      metiers=[Metier("collaborateur_agricole", 27.0, niveau_salaire=0.3)])
    exploitant, plans = _plans(simulateur, conjointe)
    eligible = exploitant.eligible
    assert (conjointe.annee_liquidation, conjointe.mois_liquidation) == (1998, 7)
    assert eligible.duree == eligible.conjoint_avant_1999 == 142 and plans is None
    for quand in ("1999-01-01", "2000-01-01"):
        assert _plans(simulateur, conjointe, quand)[1] is None, quand
    _, plans = _plans(simulateur, conjointe, "2001-01-01")
    assert plans.conjoint_minimum == pytest.approx(19.2, abs=1e-12)
    assert plans.conjoint_annees == 35.5
    assert plans.points == pytest.approx(3.2 * 35.5 * (1.0 - 0.15 - 0.15), rel=1e-12)
    seule = _chef(simulateur, 1938, 62, sexe="F", mois_naissance=1,
                  metiers=[Metier("collaborateur_agricole", 32.0, niveau_salaire=0.3)])
    exploitant, plans = _plans(simulateur, seule, "2001-01-01")
    eligible = exploitant.eligible
    assert (seule.annee_liquidation, seule.mois_liquidation) == (2000, 2)
    assert (eligible.duree, eligible.conjoint_avant_1999) == (124, 116)
    # Deux années depuis 1999, et vingt-neuf avant, moins l'écart de 2000 à 1999.
    assert plans.conjoint_annees == 2.0 + 29.0 - 1.0
    assert plans.points == pytest.approx(3.2 * 30.0 * (1.0 - 0.6), rel=1e-12)


# -- la réversion du régime, aux plans de 1997 à 2008 ---------------------------

def _conjointe_de_2000(simulateur: Simulateur, reversion: dict | None = None) -> Carriere:
    """Trente et un ans de conjointe, partie le 1er février 2000, et la
    réversion que le régime lui sert, veuve d'un de ses assurés, si elle en a
    une."""
    return _chef(simulateur, 1938, 62, sexe="F", mois_naissance=1,
                 metiers=[Metier("collaborateur_agricole", 32.0, niveau_salaire=0.3)],
                 reversion_agricole=reversion)


def test_qui_est_titulaire_d_une_reversion_a_son_depart_n_a_pas_les_points_des_conjoints(
        simulateur):
    """Les plans des pensions prises de 1998 à 2001 ne vont qu'à qui n'est pas
    titulaire, à la date d'effet de sa pension, d'une réversion du régime
    (L. 732-31, puis L. 732-54-2, I ; D. 732-118) : la conjointe de 2000, veuve
    depuis mai 1999, n'a aucun point, ni en 2001, ni depuis 2002 ; sa réversion
    absorbée par ses ressources, déclarée nulle, ne l'en prive pas."""
    seule = _conjointe_de_2000(simulateur)
    veuve = _conjointe_de_2000(simulateur, {"debut": "1999-05", "mensuel": 120.0})
    absorbee = _conjointe_de_2000(simulateur, {"debut": "1999-05", "mensuel": 0.0})
    for quand in ("2001-01-01", "2002-01-01", "2007-01-01", "2008-01-01"):
        servis = _plans(simulateur, seule, quand)[1]
        assert servis is not None and servis.conjoint_points > 0.0, quand
        assert _plans(simulateur, veuve, quand)[1] is None, quand
        assert _plans(simulateur, absorbee, quand)[1].points == pytest.approx(
            servis.points, rel=1e-12), quand


def test_une_reversion_venue_apres_le_depart_plafonne_les_points_des_conjoints(simulateur):
    """« En cas d'obtention d'une pension de réversion [...] postérieurement à
    l'attribution de points de retraite proportionnelle gratuits, le nombre de
    points gratuits est plafonné, à compter du 1er janvier de l'année qui suit
    cette obtention, au niveau atteint durant l'année au cours de laquelle a
    pris effet la pension de réversion » (L. 732-31, puis L. 732-54-2, II ;
    D. 732-126 à D. 732-130) : veuve en juin 2001, la conjointe de 2000 garde
    les seize points et le différentiel de 3,2 de 2001, minorés de 60 %
    (D. 732-127) ; veuve en juin 2003, B de 2003, minoré de 60 %, au lieu des
    5,5 % puis 4 % par année manquante de 2007 et 2008 (D. 732-131)."""
    seule = _conjointe_de_2000(simulateur)
    en_2001 = _conjointe_de_2000(simulateur, {"debut": "2001-06", "mensuel": 120.0})
    en_2003 = _conjointe_de_2000(simulateur, {"debut": "2003-06", "mensuel": 120.0})
    niveaux = {}
    for veuve, annee in ((en_2001, 2001), (en_2003, 2003)):
        niveaux[annee] = _plans(simulateur, seule, f"{annee}-01-01")[1].points
        assert _plans(simulateur, veuve, f"{annee}-01-01")[1].points == pytest.approx(
            niveaux[annee], rel=1e-12)
        assert _plans(simulateur, veuve, "2008-01-01")[1].points == pytest.approx(
            niveaux[annee], rel=1e-12), annee
        for quand in range(annee + 1, 2008):
            servis = _plans(simulateur, seule, f"{quand}-01-01")[1].points
            assert _plans(simulateur, veuve, f"{quand}-01-01")[1].points == pytest.approx(
                min(servis, niveaux[annee]), rel=1e-12), (annee, quand)
    assert niveaux[2001] == pytest.approx(3.2 * 30.0 * (1.0 - 0.6), rel=1e-12)
    assert _plans(simulateur, seule, "2008-01-01")[1].points > niveaux[2003] > niveaux[2001]
    assert _plans(simulateur, en_2003, "2002-01-01")[1].points == pytest.approx(
        _plans(simulateur, seule, "2002-01-01")[1].points, rel=1e-12)


def test_le_veuf_d_avant_1995_parti_avant_1997_garde_vingt_points(simulateur):
    """Le titulaire d'une réversion du régime entrée en jouissance avant 1995
    qui a sa propre pension reçoit la majoration forfaitaire de L. 732-46, IV
    (D. 732-97), que L. 732-33, II, puis L. 732-54-4, relèvent depuis 1999 à qui
    a trente-deux ans et demi d'activité agricole (décret n° 2002-297, article
    11 ; D. 732-139). Elle s'applique en priorité depuis 2000, et la pension
    prise avant 1997 garde alors P = (20 - n) × d (décret n° 2000-261, article
    1er ; décret n° 2001-170, article 3 ; décret n° 2002-297, article 5 ;
    D. 732-116) ; en 1999, la majoration de la retraite passait la première, à
    23,9 (L. 732-33, II). Veuf depuis 1996, sous L. 732-41, le chef parti en
    1995 a les plans de tous."""
    sans = _chef(simulateur, 1930, 65)
    resultat, _, _ = _resultat(simulateur, sans)
    duree = _points_au_compte(simulateur, resultat) / 16.0
    veuf = _chef(simulateur, 1930, 65, reversion_agricole={"debut": "1990-03", "mensuel": 150.0})
    depuis_1996 = _chef(simulateur, 1930, 65,
                        reversion_agricole={"debut": "1996-03", "mensuel": 150.0})
    for carriere, avec in ((veuf, True), (depuis_1996, False)):
        resultat, _, _ = _resultat(simulateur, carriere)
        for annee, minimum_moins_seize, part in ((1997, 4.0, 1 / 3), (1998, 4.0, 2 / 3),
                                                 (1999, 7.9, 1.0)):
            assert _servis(simulateur, carriere, resultat, annee) == pytest.approx(
                minimum_moins_seize * duree * part, rel=1e-9), (avec, annee)
        for annee, autres in ((2000, 10.96), (2001, 13.23), (2002, None), (2008, None)):
            if autres is None:
                autres = _a_moins_seize(simulateur, annee)
            assert _servis(simulateur, carriere, resultat, annee) == pytest.approx(
                (4.0 if avec else autres) * duree, rel=1e-9), (avec, annee)


def test_le_veuf_d_avant_1995_parti_de_1997_a_2001_garde_26_933_points(simulateur):
    """Aux pensions prises de 1997 à 2001, qui peut bénéficier de la
    revalorisation de la majoration forfaitaire de sa réversion garde
    A = 26,933, quand celui des autres passe à 29,23 en 2001, puis au minimum
    vieillesse de chaque année (L. 732-54-1, II ; décret n° 2001-170, article
    3 ; décret n° 2002-297, article 4 ; D. 732-113)."""
    veuf = _chef(simulateur, 1935, 62, reversion_agricole={"debut": "1993-03", "mensuel": 150.0})
    resultat, avantages, _ = _resultat(simulateur, veuf)
    assert avantages["majoration_retraite_proportionnelle"].detail.startswith(
        f"{(26.933 - 16.0) * 37.5 / 3:,.2f} points")
    for annee in (1999, 2001, 2002, 2008):
        assert _servis(simulateur, veuf, resultat, annee) == pytest.approx(
            (26.933 - 16.0) * 37.5, rel=1e-12), annee
    assert _a_moins_seize(simulateur, 2002) > 26.933 - 16.0


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


def test_le_collaborateur_de_1999_a_2008_recoit_pmr1(simulateur):
    """Les périodes de collaborateur cotisées de 1999 à 2008 par qui a
    régularisé sa situation entrent dans DM1, avec celles du chef, et sont
    retenues en priorité (D. 732-110, II, 3° ; D. 732-111) : la conjointe
    collaboratrice partie en 2016 reçoit PMR1 sur ces dix ans, PMR2 sur le
    reste."""
    metiers = [Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3)]
    carriere = _chef(simulateur, 1952, 64, sexe="F", metiers=metiers)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    eligible = resultat.chef_d_exploitation.eligible
    assert eligible.chef == 0 and eligible.collaborateur_regularise == 40
    pmr = simulateur.scenario_actuel.pension_majoree_reference
    pleine, _ = pmr.montant("pmr_chef", 2016, carriere.mois_liquidation)
    reduite, _ = pmr.montant("pmr_conjoint", 2016, carriere.mois_liquidation)
    reste = eligible.reference - 40
    assert (f"PMR {pleine:,.2f} € × 40/{eligible.reference} + {reduite:,.2f} € × "
            f"{reste}/") in avantages["pension_majoree_reference"].detail


def _veuve(simulateur: Simulateur, reversion: dict | None) -> Carriere:
    """La conjointe collaboratrice de vingt à soixante-quatre ans, partie le
    1er février 2016, et la réversion que le régime lui sert, veuve d'un de
    ses assurés, si elle en a une."""
    metiers = [Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3)]
    return _chef(simulateur, 1952, 64, sexe="F", metiers=metiers,
                 reversion_agricole=reversion)


#: 150 € par mois de réversion depuis mars 2010, revalorisés comme les pensions
#: de base jusqu'au 1er février 2016 : les coefficients publiés par la Cnav
#: d'avril 2010, 2011, 2012 et 2013 et d'octobre 2015 (L. 161-23-1).
REVERSION_EN_2016 = 150 * 12 * 1.009 * 1.021 * 1.021 * 1.013 * 1.001
#: Et depuis juin 2018 jusqu'en décembre 2026 : janvier 2019, 2020 (la tranche
#: des pensions de 2 000 € par mois au plus), 2021 et 2022, juillet 2022,
#: janvier 2023, 2024, 2025 et 2026.
REVERSION_EN_2026 = (150 * 12 * 1.003 * 1.01 * 1.004 * 1.011 * 1.04 * 1.008 * 1.053
                     * 1.022 * 1.009)


def test_qui_peut_pretendre_a_une_reversion_du_regime_recoit_pmr1_partout(simulateur):
    """La conjointe collaboratrice partie en 2016, veuve d'un exploitant depuis
    2010 : toutes ses périodes entrent dans DM1, au montant du chef (D. 732-110,
    II, 2° ; D. 732-111), même quand sa réversion est nulle, ses ressources
    l'absorbant — elle reste « susceptible d'en bénéficier ». Sans réversion,
    elle n'a PMR1 que sur ses années de 1999 à 2008."""
    carriere = _veuve(simulateur, {"debut": "2010-03", "mensuel": 0.0})
    assert (carriere.annee_liquidation, carriere.mois_liquidation) == (2016, 2)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    eligible = resultat.exploitant_agricole.eligible
    pleine, _ = simulateur.scenario_actuel.pension_majoree_reference.montant(
        "pmr_chef", 2016, 2)
    retenue = min(eligible.duree, eligible.reference)
    assert avantages["pension_majoree_reference"].detail.startswith(
        f"PMR {pleine:,.2f} € × {retenue}/{eligible.reference}, au taux plein")
    majoree = completer.pension_majoree(simulateur.scenario_actuel, carriere, eligible,
                                        SimpleNamespace(montant=0.0001), 0.0)
    assert majoree.duree_reduite == 0
    assert majoree.avant_ecretement == pytest.approx(
        pleine * retenue / eligible.reference, abs=1e-3)
    sans = completer.pension_majoree(simulateur.scenario_actuel, _veuve(simulateur, None),
                                     eligible, SimpleNamespace(montant=0.0001), 0.0)
    assert sans.duree_reduite == retenue - 40


def test_la_reversion_du_regime_se_retranche_de_la_pmr_et_compte_au_plafond(simulateur):
    """La majoration est l'écart entre la PMR et « la somme des pensions de
    retraite et de réversion, servies à l'assuré par le régime » (D. 732-112) ;
    le plafond compte « l'ensemble des pensions de retraite et des pensions de
    réversion servies à l'assuré » (D. 732-114). La réversion de 150 € par mois
    de mars 2010 compte pour ce qu'elle sert en février 2016, revalorisée."""
    carriere = _veuve(simulateur, {"debut": "2010-03", "mensuel": 150.0})
    resultat, avantages, _ = _resultat(simulateur, carriere)
    eligible = resultat.exploitant_agricole.eligible
    pleine, _ = simulateur.scenario_actuel.pension_majoree_reference.montant(
        "pmr_chef", 2016, 2)
    retenue = min(eligible.duree, eligible.reference)
    moteur = simulateur.scenario_actuel
    majoree = completer.pension_majoree(moteur, carriere, eligible,
                                        SimpleNamespace(montant=0.0001), 0.0)
    assert majoree.reversion == pytest.approx(REVERSION_EN_2016, rel=1e-12)
    assert majoree.avant_ecretement == pytest.approx(
        pleine * retenue / eligible.reference - REVERSION_EN_2016, abs=1e-3)
    ecretee = completer.pension_majoree(moteur, carriere, eligible,
                                        SimpleNamespace(montant=0.0001),
                                        majoree.plafond - 2500.0)
    assert ecretee.complement == pytest.approx(2500.0 - REVERSION_EN_2016, rel=1e-12)
    assert f", moins {REVERSION_EN_2016:,.2f} € de réversion du régime" in avantages[
        "pension_majoree_reference"].detail


#: Et depuis juin 2018 jusqu'en décembre 2021 : janvier 2019, 2020 (la tranche
#: des pensions de 2 000 € par mois au plus) et 2021.
REVERSION_EN_2021 = 150 * 12 * 1.003 * 1.01 * 1.004


def _revisee(simulateur: Simulateur, resultat, vivante, annee: int,
             reversion: float) -> float:
    """La majoration de décembre de ``annee``, refaite de son texte : la PMR du
    chef ce mois-là sur la durée retenue, moins la pension de base avant
    surcote menée à l'échéance et la réversion du régime qu'elle sert
    (D. 732-110 à D. 732-112), sans écrêtement."""
    exploitant = resultat.exploitant_agricole
    eligible = exploitant.eligible
    pleine, _ = simulateur.scenario_actuel.pension_majoree_reference.montant(
        "pmr_chef", annee, 12)
    base = exploitant.pension.montant * _base(vivante).coefficient
    return (pleine * min(eligible.duree, eligible.reference) / eligible.reference
            - base / eligible.surcote - reversion)


def test_une_reversion_ouverte_apres_le_depart_revise_la_majoration(simulateur):
    """Veuve en juin 2018, deux ans après son départ : « Toute modification de
    la situation familiale ou du montant des ressources donne lieu à une
    révision de la majoration de pension » (D. 732-114). Dès le mois où sa
    réversion commence, qui suit le décès, le 2° de D. 732-110, II, porte
    toutes ses périodes au montant du chef, et la réversion se retranche de la
    PMR (D. 732-112) : 468,91 € en décembre 2018, au lieu des 988,13 € de la
    liquidation menés par le coefficient. Rien ne change avant, ni sans
    réversion ; depuis 2022, la PMR unique la retranche de même."""
    sans, veuve = _veuve(simulateur, None), _veuve(simulateur, {"debut": "2018-06",
                                                                 "mensuel": 150.0})
    resultats = [_resultat(simulateur, carriere) for carriere in (sans, veuve)]
    assert (resultats[0][1]["pension_majoree_reference"].montant
            == resultats[1][1]["pension_majoree_reference"].montant)
    resultat = resultats[1][0]
    assert faire_vivre(simulateur, sans, resultats[0][0], 2021).exploitant is None
    assert faire_vivre(simulateur, veuve, resultat, 2017).exploitant is None
    for annee, reversion in ((2018, 150 * 12), (2021, REVERSION_EN_2021)):
        vivante = faire_vivre(simulateur, veuve, resultat, annee)
        revisee = _revisee(simulateur, resultat, vivante, annee, reversion)
        menee = resultat.exploitant_agricole.pmr * _base(vivante).coefficient
        assert vivante.exploitant.pmr == pytest.approx(revisee - menee, abs=1e-6)
        if annee == 2018:
            assert (round(revisee, 2), round(menee, 2)) == (468.91, 988.13)
    vivantes = {carriere is veuve: faire_vivre(simulateur, carriere, r, 2026)
                for carriere, (r, _, _) in zip((sans, veuve), resultats)}
    assert vivantes[True].exploitant.pmr < vivantes[False].exploitant.pmr
    assert (_base(vivantes[False]).aujourd_hui - _base(vivantes[True]).aujourd_hui
            == pytest.approx(REVERSION_EN_2026, rel=1e-9))


def test_la_revision_prend_effet_le_mois_qui_suit_la_modification(simulateur):
    """Une pension allemande de 500 € par mois, commencée en décembre 2017 :
    « La majoration de pension recalculée prend effet à compter du premier jour
    du mois suivant la date à laquelle est constatée la modification »
    (D. 732-114), en janvier 2018. Le plafond compte les pensions « français[es]
    et étranger[e]s » (L. 732-54-3) : elle écrête la majoration entière."""
    carriere = _chef(simulateur, 1952, 64, sexe="F", metiers=[
        Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3)],
        etranger={"pensions": [{"pays": "DE", "age": 65 + 11 / 12, "mensuel": 500.0}]})
    assert [(p.debut.annee, p.debut.mois) for p in carriere.pensions_etrangeres] == [
        (2017, 12)]
    resultat, _, _ = _resultat(simulateur, carriere)
    exploitant = resultat.exploitant_agricole
    assert exploitant.pmr > 0
    assert faire_vivre(simulateur, carriere, resultat, 2017).exploitant is None
    vivante = faire_vivre(simulateur, carriere, resultat, 2018)
    coefficient = _base(vivante).coefficient
    assert vivante.exploitant.pmr == pytest.approx(-exploitant.pmr * coefficient, rel=1e-12)
    assert _base(vivante).aujourd_hui == pytest.approx(
        exploitant.pension.montant * coefficient, rel=1e-12)


def test_une_pension_demandee_apres_la_pension_agricole_revise_la_majoration(simulateur):
    """Vingt ans de salarié puis vingt-deux de chef, parti en février 2012, son
    régime général demandé à soixante-cinq ans : la majoration de la
    liquidation, que seules les pensions agricoles écrêtaient, se révise en
    mars 2015, le mois qui suit le régime général et l'Arrco, que le plafond
    compte (D. 732-114) — rien n'en reste."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=1.0),
               Metier("exploitant_agricole", 40.0, niveau_salaire=0.3)]
    carriere = _chef(simulateur, 1950, 62, metiers=metiers,
                     demandes_de_pension={"regime_general": 65})
    resultat, _, _ = _resultat(simulateur, carriere)
    exploitant = resultat.exploitant_agricole
    assert exploitant.pmr > 0
    assert {p.regime: p.date_effet for p in resultat.pensions_par_regime}[
        "regime_general"] == "2015-02-01"
    assert faire_vivre(simulateur, carriere, resultat, 2014).exploitant is None
    pmr = simulateur.scenario_actuel.pension_majoree_reference
    for annee in (2015, 2021):
        vivante = faire_vivre(simulateur, carriere, resultat, annee)
        coefficient = _base(vivante).coefficient
        assert vivante.exploitant.pmr == pytest.approx(-exploitant.pmr * coefficient,
                                                       rel=1e-12)
        assert sum(r.aujourd_hui for r in vivante.regimes) > pmr.montant(
            "plafond", annee, 12)[0]


def test_une_pension_prise_depuis_2022_se_revise_aussi(simulateur):
    """La conjointe collaboratrice partie en février 2022, au montant unique,
    veuve en mars 2023 : sa majoration se révise (D. 732-114) et perd ce que
    sa réversion sert, 1 800 € par an en décembre 2023 (D. 732-112)."""
    carriere = _chef(simulateur, 1960, 62, sexe="F", metiers=[
        Metier("collaborateur_agricole", 20.0, niveau_salaire=0.3)],
        reversion_agricole={"debut": "2023-03", "mensuel": 150.0})
    assert (carriere.annee_liquidation, carriere.mois_liquidation) == (2022, 2)
    resultat, _, _ = _resultat(simulateur, carriere)
    assert faire_vivre(simulateur, carriere, resultat, 2022).exploitant is None
    vivante = faire_vivre(simulateur, carriere, resultat, 2023)
    revisee = _revisee(simulateur, resultat, vivante, 2023, 150 * 12)
    menee = resultat.exploitant_agricole.pmr * _base(vivante).coefficient
    assert vivante.exploitant.pmr == pytest.approx(revisee - menee, abs=1e-6)
    assert vivante.exploitant.pmr == pytest.approx(-1800.0, abs=0.05)


#: Le jumeau JavaScript de « faire vivre » : chaque carrière, construite de ses
#: options, liquidée, puis menée à l'année dite.
_JUMEAU_DES_REVISIONS = """
import { readFileSync } from "node:fs";
import { Simulateur } from "./moteur/js/simulateur.js";
import { faireVivre } from "./moteur/js/revalorisation.js";
const cas = JSON.parse(process.argv[1]);
const simulateur = new Simulateur(JSON.parse(readFileSync("./moteur/donnees.json", "utf8")));
process.stdout.write(JSON.stringify(cas.map(([options, annee]) => {
  const carriere = simulateur.carriereParcours(options);
  const resultat = simulateur.scenarioActuel.calculer(carriere);
  const vivante = faireVivre(simulateur, carriere, resultat, annee);
  return { donnees: vivante.donnees(), exploitant: vivante.exploitant };
})));
"""

#: Les carrières des quatre révisions, telles que les deux moteurs les construisent.
_COLLABORATRICE = {"sexe": "F", "age_liquidation": 64, "jour_naissance": 15,
                   "metiers": [{"affiliation": "collaborateur_agricole", "age_debut": 20,
                                "niveau_salaire": 0.3}]}
_CHEF_D_AVANT_1997 = {"annee_naissance": 1930, "sexe": "H", "age_liquidation": 65,
                      "jour_naissance": 15}
_REVISIONS = [
    ({**_COLLABORATRICE, "annee_naissance": 1952,
      "reversion_agricole": {"debut": "2018-06", "mensuel": 150.0}}, 2018),
    ({**_COLLABORATRICE, "annee_naissance": 1952,
      "reversion_agricole": {"debut": "2018-06", "mensuel": 150.0}}, 2021),
    ({**_COLLABORATRICE, "annee_naissance": 1952, "etranger": {
        "pensions": [{"pays": "DE", "age": 65 + 11 / 12, "mensuel": 500.0}]}}, 2017),
    ({**_COLLABORATRICE, "annee_naissance": 1952, "etranger": {
        "pensions": [{"pays": "DE", "age": 65 + 11 / 12, "mensuel": 500.0}]}}, 2018),
    ({"annee_naissance": 1950, "sexe": "H", "age_liquidation": 62, "jour_naissance": 15,
      "metiers": [{"affiliation": "salarie_prive_non_cadre", "age_debut": 20,
                   "niveau_salaire": 1.0},
                  {"affiliation": "exploitant_agricole", "age_debut": 40,
                   "niveau_salaire": 0.3}],
      "demandes_de_pension": {"regime_general": 65}}, 2015),
    ({**_COLLABORATRICE, "annee_naissance": 1960, "age_liquidation": 62,
      "reversion_agricole": {"debut": "2023-03", "mensuel": 150.0}}, 2023),
    ({**_COLLABORATRICE, "annee_naissance": 1960, "age_liquidation": 62,
      "reversion_agricole": {"debut": "2023-03", "mensuel": 150.0}}, 2026),
    ({**_COLLABORATRICE, "annee_naissance": 1960, "age_liquidation": 62,
      "reversion_agricole": {"debut": "2023-03", "mensuel": 150.0}}, 2030),
    # La PMR de 2009 des pensions prises avant 1997, sur la durée de chef que
    # leurs points reconstituent (D. 732-110, III) : trente ans sur quarante-
    # quatre ; moins de dix-sept ans et demi, à PMR2 en 2010 ; le chef à titre
    # secondaire de 1982 à 1986, quinze points de moins par année.
    ({**_CHEF_D_AVANT_1997, "metiers": [
        {"affiliation": "exploitant_agricole", "age_debut": 20, "niveau_salaire": 0.3}]}, 2009),
    ({**_CHEF_D_AVANT_1997, "metiers": [
        {"affiliation": "exploitant_agricole", "age_debut": 20, "niveau_salaire": 0.1}]}, 2010),
    ({**_CHEF_D_AVANT_1997, "annee_naissance": 1931, "metiers": [
        {"affiliation": "salarie_prive_non_cadre", "age_debut": 20, "niveau_salaire": 0.3},
        {"affiliation": "exploitant_agricole", "age_debut": 51, "niveau_salaire": 0.1,
         "cumul": True, "age_fin": 56},
        {"affiliation": "exploitant_agricole", "age_debut": 56, "niveau_salaire": 0.1}]}, 2015),
    # La réversion du régime aux plans : la conjointe de 2000, veuve avant son
    # départ, sans les points des conjoints (D. 732-118), puis veuve en 2001,
    # ses points plafonnés à ceux de 2001 (L. 732-54-2, II) ; le chef parti en
    # 1995, veuf depuis 1990, à vingt points (D. 732-116), celui parti en 1997,
    # veuf depuis 1993, à 26,933 (D. 732-113).
    ({**_COLLABORATRICE, "annee_naissance": 1938, "age_liquidation": 62, "mois_naissance": 1,
      "metiers": [{"affiliation": "collaborateur_agricole", "age_debut": 32,
                   "niveau_salaire": 0.3}],
      "reversion_agricole": {"debut": "1999-05", "mensuel": 120.0}}, 2012),
    ({**_COLLABORATRICE, "annee_naissance": 1938, "age_liquidation": 62, "mois_naissance": 1,
      "metiers": [{"affiliation": "collaborateur_agricole", "age_debut": 32,
                   "niveau_salaire": 0.3}],
      "reversion_agricole": {"debut": "2001-06", "mensuel": 120.0}}, 2008),
    ({**_CHEF_D_AVANT_1997, "metiers": [
        {"affiliation": "exploitant_agricole", "age_debut": 20, "niveau_salaire": 0.3}],
      "reversion_agricole": {"debut": "1990-03", "mensuel": 150.0}}, 2005),
    ({**_CHEF_D_AVANT_1997, "annee_naissance": 1935, "age_liquidation": 62, "metiers": [
        {"affiliation": "exploitant_agricole", "age_debut": 20, "niveau_salaire": 0.3}],
      "reversion_agricole": {"debut": "1993-03", "mensuel": 150.0}}, 2004),
]


def test_les_deux_moteurs_revisent_la_meme_majoration(simulateur):
    """La révision de D. 732-114, à l'échéance : la réversion qui commence
    après le départ, la pension étrangère le mois qui suit, le régime général
    demandé plus tard, la pension prise depuis 2022, jusqu'au-delà du dernier
    barème, où sa PMR et son plafond suivent les prix ; la PMR de 2009 des
    pensions prises avant 1997, sur leur durée de chef reconstituée ; la
    réversion du régime aux plans de 1997 à 2008 ; la revalorisation de chaque
    régime et la révision de l'exploitant, en Python et en JavaScript."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from dataclasses import asdict

    from test_liquidation import _ecarts

    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU_DES_REVISIONS,
         json.dumps(_REVISIONS)],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    ecarts: list[str] = []
    revisees = 0
    for rang, ((options, annee), obtenu) in enumerate(zip(_REVISIONS,
                                                          json.loads(execution.stdout))):
        metiers = [Metier(m["affiliation"], m["age_debut"], niveau_salaire=m["niveau_salaire"],
                          cumul=m.get("cumul", False), age_fin=m.get("age_fin"))
                   for m in options["metiers"]]
        carriere = Carriere.depuis_parcours(
            **{cle: valeur for cle, valeur in options.items() if cle != "metiers"},
            metiers=metiers, macro=simulateur.macro)
        resultat = simulateur.scenario_actuel.calculer(carriere)
        vivante = faire_vivre(simulateur, carriere, resultat, annee)
        attendu = json.loads(json.dumps({
            "donnees": vivante.donnees(),
            "exploitant": None if vivante.exploitant is None else asdict(vivante.exploitant)}))
        revisees += attendu["exploitant"] is not None
        _ecarts(obtenu, attendu, f"révision {rang}", ecarts)
    assert revisees == 14
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])


#: Le jumeau JavaScript : la conjointe collaboratrice de :func:`_veuve`,
#: simulée entière, sous chacune des réversions déclarées.
_JUMEAU_DES_VEUVES = """
import { readFileSync } from "node:fs";
import { Simulateur } from "./moteur/js/simulateur.js";
const cas = JSON.parse(process.argv[1]);
const simulateur = new Simulateur(JSON.parse(readFileSync("./moteur/donnees.json", "utf8")));
process.stdout.write(JSON.stringify(cas.map((reversion) => simulateur.simuler(
  simulateur.carriereParcours({
    annee_naissance: 1952, sexe: "F", age_liquidation: 64, jour_naissance: 15,
    metiers: [{ affiliation: "collaborateur_agricole", age_debut: 20, niveau_salaire: 0.3 }],
    reversion_agricole: reversion,
  })).dictionnaire())));
"""


def test_les_deux_moteurs_servent_la_meme_pmr_aux_veuves(simulateur):
    """Le 2° de D. 732-110, II, et la réversion retranchée et comptée au
    plafond, au départ et à chaque échéance : le résultat entier, en Python et
    en JavaScript, des veuves de 2010, à la réversion nulle ou de 150 € par
    mois, et de celle de 2018."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini
    from test_liquidation import _ecarts

    cas = [{"debut": "2010-03", "mensuel": 0.0}, {"debut": "2010-03", "mensuel": 150.0},
           {"debut": "2018-06", "mensuel": 150.0}]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU_DES_VEUVES, json.dumps(cas)],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    ecarts: list[str] = []
    for rang, (reversion, obtenu) in enumerate(zip(cas, json.loads(execution.stdout))):
        attendu = json.loads(json.dumps(_fini(
            simulateur.simuler(_veuve(simulateur, reversion)).dictionnaire())))
        _ecarts(obtenu, attendu, f"veuve {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])


def test_le_complement_ne_retranche_que_les_points_de_chef(simulateur):
    """Vingt-neuf ans de chef, puis quinze de collaborateur, à la RCO depuis
    2011, parti en 2026 : la formule de D. 732-166-4 ne retranche que N, les
    points acquis au titre des périodes de chef, gratuits compris ; ceux du
    collaborateur n'en sont pas, et le complément les laisse en sus."""
    from retraite_notionnelle.droit import releve
    metiers = [Metier("exploitant_agricole", 20.0, niveau_salaire=0.3),
               Metier("collaborateur_agricole", 49.0, niveau_salaire=0.3)]
    carriere = _chef(simulateur, 1962, 64, metiers=metiers)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    droits = releve.construire(simulateur.scenario_actuel, carriere).droits
    qualite = carriere.qualite_agricole
    credits = [(annee, p) for code, annee, p, _ in droits.points if code == completer.RCO]
    de_chef = sum(p for annee, p in credits if qualite(annee) == "chef")
    du_collaborateur = sum(p for annee, p in credits if qualite(annee) == "collaborateur")
    gratuits = droits.gratuits[completer.RCO][0]
    assert de_chef > 0 and du_collaborateur > 0 and gratuits > 0
    n = completer.points_rco_de_chef(droits, carriere)
    assert n == pytest.approx(gratuits + de_chef)
    assert resultat.chef_d_exploitation.points == n
    differentiel = avantages["complement_differentiel_rco"]
    valeur = differentiel.montant / int(differentiel.detail.split(" points")[0].replace(",", ""))
    tous = droits.points_acquis[completer.RCO]
    assert tous == pytest.approx(n + du_collaborateur)
    # Retrancher tous les points de la RCO en ôterait ceux du collaborateur.
    assert round(du_collaborateur) >= 1
    assert differentiel.montant > (du_collaborateur - 1) * valeur


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


def _points(simulateur: Simulateur, carriere: Carriere) -> dict[tuple[str, int], float]:
    from retraite_notionnelle.droit import releve
    points: dict[tuple[str, int], float] = {}
    for code, annee, nombre, _ in releve.construire(
            simulateur.scenario_actuel, carriere).droits.points:
        points[code, annee] = points.get((code, annee), 0.0) + nombre
    return points


def test_le_collaborateur_cotise_sur_l_assiette_forfaitaire(simulateur):
    """Le collaborateur et l'aide familial cotisent sur un forfait, non sur
    leur revenu : au régime de base, 400 SMIC horaires depuis 2004
    (D. 731-123), qui ouvrent quinze points, portés à seize (R. 732-73) ; à la
    RCO, 1 200 SMIC depuis 2011, 66 points jusqu'en 2016, 77 en 2017, 88
    depuis (D. 732-155, II). Le revenu saisi n'y change rien depuis 2004."""
    resultats = []
    for niveau in (0.3, 1.5):
        metiers = [Metier("collaborateur_agricole", 20.0, niveau_salaire=niveau)]
        carriere = _chef(simulateur, 1960, 64, sexe="F", metiers=metiers)
        assert carriere.annee_liquidation < 2026
        points = _points(simulateur, carriere)
        for annee in range(2004, 2024):
            assert points["msa_non_salaries", annee] == 16.0, annee
        assert ("msa_rco", 2010) not in points
        assert [points["msa_rco", annee] for annee in (2011, 2016, 2017, 2018, 2023)] == [
            66.0, 66.0, 77.0, 88.0, 88.0]
        resultats.append(_resultat(simulateur, carriere)[2]["msa_rco"])
    # Avant 2004, la cotisation se prenait des revenus du chef, que le modèle
    # ne connaît pas : seule la RCO est entière au forfait.
    assert resultats[0] == resultats[1]


def test_le_chef_a_titre_secondaire_n_a_pas_de_forfait_avant_2026(simulateur):
    """Salarié, et chef d'exploitation à côté depuis 1988 : avant 2026, ses
    années de chef à titre accessoire ne lui ouvrent que la retraite
    proportionnelle (L. 732-28), et le forfait ne les compte pas. Qui était
    déjà chef avant 1981 le garde (R. 732-65)."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
               Metier("exploitant_agricole", 30.0, niveau_salaire=0.1, cumul=True)]
    carriere = _chef(simulateur, 1958, 66, metiers=metiers)
    assert carriere.annee_liquidation < 2026
    resultat, _, pensions = _resultat(simulateur, carriere)
    detail = {p.regime: p.detail for p in resultat.pensions_par_regime}["msa_non_salaries"]
    assert "forfait" not in detail and pensions["msa_non_salaries"] > 0
    ancien = _chef(simulateur, 1945, 65, metiers=[
        Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=0.3),
        Metier("exploitant_agricole", 30.0, niveau_salaire=0.1, cumul=True)])
    resultat, _, _ = _resultat(simulateur, ancien)
    assert "forfait" in {p.regime: p.detail
                         for p in resultat.pensions_par_regime}["msa_non_salaries"]


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
    # La pension majorée de référence de 2009 : une carrière complète partie
    # en 1995, vingt ans de chef partis sans le taux plein en 2000.
    {"naissance": "1930", "liquidation": "65"},
    {"naissance": "1940", "liquidation": "60", "debut": "40"},
    # Les pensions prises avant 1997, révisées de 1997 à 2008 : vingt-six ans
    # de chef, servis depuis 2007 ; trente-six partis sans le taux plein en
    # 1994, minorés ; plus de seize points par an, la durée reconstituée
    # ramenée à la durée agricole.
    {"naissance": "1930", "liquidation": "65", "debut": "40"},
    {"naissance": "1932", "liquidation": "62", "debut": "26"},
    {"naissance": "1930", "liquidation": "65", "salaire": "0.6"},
    # La PMR unique de 2022, aux pensions prises depuis 2009 : quinze ans de
    # chef après le salariat, partis en 2012 sous la durée minimale.
    {"naissance": "1950", "liquidation": "62", "statut": "salarie_prive_non_cadre",
     "metier2_debut": "47", "metier2_statut": "exploitant_agricole", "metier2_salaire": "0.3"},
    # Les points de RCO de chef seuls dans le complément (D. 732-166-4) :
    # vingt-neuf ans de chef, puis quinze de collaborateur, parti en 2026.
    {"naissance": "1962", "metier2_debut": "49", "metier2_statut": "collaborateur_agricole",
     "metier2_salaire": "0.3"},
    # Les points des conjoints des plans (D. 732-118 à D. 732-146) : une conjointe
    # collaboratrice partie en 2005 ; une autre, trente ans de conjointe, partie
    # en 2000, servie depuis 2002 ; quarante-deux ans de conjointe, partie en 2001.
    {"naissance": "1943", "liquidation": "62", "sexe": "F", "statut": "collaborateur_agricole"},
    {"naissance": "1938", "liquidation": "62", "sexe": "F", "statut": "collaborateur_agricole",
     "debut": "32"},
    {"naissance": "1939", "liquidation": "62", "sexe": "F", "statut": "collaborateur_agricole"},
    # Les pensions dues de 1998 à 2001 (décrets n° 99-875, 2000-261 et 2001-170) :
    # trente-cinq ans et demi de conjointe, partie en juillet 1998.
    {"naissance": "1936", "naissance_mois": "6", "liquidation": "62", "sexe": "F",
     "statut": "collaborateur_agricole", "debut": "27"},
    # Le forfait que les plans retranchent, sans les années de chef à titre
    # secondaire (L. 732-28) : chef à côté du salariat de 1982 à 1985, puis à
    # titre principal, parti en 2005.
    {"naissance": "1940", "liquidation": "65", "statut": "salarie_prive_non_cadre",
     "metier2_debut": "42", "metier2_statut": "exploitant_agricole", "metier2_salaire": "0.3",
     "metier2_cumul": "oui", "metier2_fin": "46", "metier3_debut": "46",
     "metier3_statut": "exploitant_agricole", "metier3_salaire": "0.5"},
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
    revises = [{cle for e in a["journal"] if "regimes" in e["contenu"].get("donnee", {})
                for r in e["contenu"]["donnee"]["regimes"] for cle in r}
               for a in attendus]
    assert sum("pension_majoree_de_2009" in cles for cles in revises) >= 3
    assert sum("plans_de_revalorisation" in cles for cles in revises) >= 3
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
