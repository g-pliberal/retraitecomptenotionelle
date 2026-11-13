"""La façade des tests confrontée au jumeau Python, tant qu'il vit (action 161).

``tests/test_facade.py`` dit ce que la façade doit rendre ; ici, ce qu'elle
rend est refait par le moteur Python, sur les carrières des témoins de
simulations : le résultat entier, sous ses types, champ par champ, au bit près
sous Linux x86_64. C'est la preuve que la lecture stricte ne perd ni ne change
rien — une confrontation de deux moteurs, qui part avec le jumeau, et dont ce
fichier est le seul de la façade à exécuter une règle Python.
"""

from __future__ import annotations

import dataclasses
import datetime
import enum
import json
import shutil
from pathlib import Path

import pytest

from retraite_notionnelle import pont
from retraite_notionnelle import simulateur as simulateur_python
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere as CarrierePython
from retraite_notionnelle.carriere import LigneRelevee, Metier
from retraite_notionnelle.config import RACINE_PROJET, Parametres
from retraite_notionnelle.droit import liquider as liquider_python
from retraite_notionnelle.droit import ouvrir as ouvrir_python
from retraite_notionnelle.journal import Journal

import facade
from outils_pont import TOLERANCE_DU_MOTEUR_PYTHON, ecarts_d_ecriture

TEMOINS = RACINE_PROJET / "tests" / "temoins" / "simulations.json"

#: Les types du résultat du scénario 1 que peu de carrières portent : la
#: confrontation entière doit avoir relu chacun au moins une fois.
TYPES_RARES = {"DepartServi", "DemandeExaminee", "ProgressiveServie", "MinimumEcrete",
               "PetitePension", "ChefDExploitation", "ExploitantAgricole", "EligibleAgricole",
               "AvantageApplique", "PensionRegime"}

#: Ceux de la comparaison, de même : le cumul et les droits d'après le départ,
#: que l'échéancier ajoute au scénario 1, la fiche de paie de l'actif, la
#: pension d'aujourd'hui de qui est parti, la réversion, le pilier, la
#: garantie, et ce que le journal inscrit.
TYPES_DE_LA_COMPARAISON = {"Comparaison", "ResultatActuel", "ResultatNotionnel", "Cumul",
                           "DroitsApresDepart", "NouvellePension",
                           "CompteNotionnel", "CotisationAnnuelle", "CoefficientConversion",
                           "EcartAge", "Capitalisation", "AnneeCapitalisation",
                           "GarantieVieillesse", "RegimeFusionne", "RemunerationActif",
                           "AnneeComparee", "FicheDePaie", "PensionAujourdhui",
                           "Reversion", "Evenement", "Foyer", "Revalorisee"}

#: Les témoins où le jumeau Python ne refait pas la fiche de paie que le
#: portage calcule sous la proposition, certaines années à venir : son brut
#: s'écarte du dernier chiffre, et la réduction générale des cotisations
#: patronales, dont le coefficient s'arrondit, de quelques euros, le coût du
#: travail avec elle. Le portage fait foi, et aucun témoin n'écrit ces
#: années : l'écart, trouvé le 12 novembre 2026 par cette confrontation, part
#: avec ``remuneration.py``. Un témoin qui n'en a plus quitte la liste.
FICHES_QUE_LE_JUMEAU_NE_REFAIT_PAS = ("assimilee_apprenti_paye_peu",
                                      "projection_cor_productivite_basse",
                                      "rattachement_pension_smic", "salaire_0.55")


def _a_plat(valeur, types: set[str]):
    """Un résultat en données, pour le comparer : un dataclass par ses champs
    et son type, une carrière comme le pont l'écrit, un membre d'énumération
    par sa valeur ; chaque nombre en flottant — le jumeau rend « 0 », entier,
    le zéro d'une somme vide là où le type dit un flottant, que la lecture
    stricte rend « 0.0 ». ``types`` reçoit le nom de chaque type rencontré."""
    if isinstance(valeur, CarrierePython):
        return pont.carriere_en_donnees(valeur)
    if isinstance(valeur, Journal):
        # Le contenu d'une liquidation ne passe pas le pont : ce qui la date,
        # seulement.
        return [{"id": entree.id, "evenement": entree.evenement, "sorte": entree.sorte,
                 "inscrite_le": entree.inscrite_le, "effet": [entree.debut, entree.fin],
                 "remplace": entree.remplace, "annule": entree.annule,
                 "contenu": None if entree.sorte == "liquidation"
                 else _a_plat(entree.contenu, types)}
                for entree in valeur]
    if dataclasses.is_dataclass(valeur) and not isinstance(valeur, type):
        types.add(type(valeur).__name__)
        return {"type": type(valeur).__name__,
                **{champ.name: _a_plat(getattr(valeur, champ.name), types)
                   for champ in dataclasses.fields(valeur)}}
    if isinstance(valeur, enum.Enum):
        return valeur.value
    if isinstance(valeur, Path):
        return str(valeur)
    if isinstance(valeur, (list, tuple)):
        return [_a_plat(element, types) for element in valeur]
    if isinstance(valeur, dict):
        return {str(cle): _a_plat(element, types) for cle, element in valeur.items()}
    if type(valeur) is int:
        return float(valeur)
    return valeur


def _ecarts(pas: int, entree) -> tuple[list[str], set[str], int]:
    """Un témoin sur ``pas`` : sa carrière, que le portage bâtit de sa requête,
    passée à ``entree`` — liquidée, ou simulée — sur le simulateur de la façade
    et sur celui du Python, sous ses paramètres. Les écarts, les types relus,
    et le nombre de carrières."""
    temoins = json.loads(TEMOINS.read_text(encoding="utf-8"))
    carrieres, refus = pont.carrieres_des_saisies(
        [{"cle": nom, "requete": temoins[nom]["requete"]} for nom in sorted(temoins)[::pas]])
    assert refus == {}
    ecarts, types = [], set()
    for nom, (parametres, carriere) in carrieres.items():
        servi = entree(facade.Simulateur(parametres), carriere)
        refait = entree(simulateur_python.Simulateur(parametres), carriere)
        assert type(servi) is type(refait)
        ecarts += ecarts_d_ecriture(_a_plat(refait, set()), _a_plat(servi, types), (nom,),
                                    tolerance=TOLERANCE_DU_MOTEUR_PYTHON)
    return ecarts, types, len(carrieres)


def _ecarts_du_scenario_1(pas: int) -> tuple[list[str], set[str], int]:
    return _ecarts(pas, lambda simulateur, carriere: simulateur.scenario_actuel.calculer(carriere))


def _ecarts_de_la_comparaison(pas: int) -> tuple[list[str], set[str], int]:
    return _ecarts(pas, lambda simulateur, carriere: simulateur.simuler(carriere))


def test_le_jumeau_refait_le_scenario_1_que_la_facade_sert_sur_un_temoin_sur_vingt():
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ecarts, _, nombre = _ecarts_du_scenario_1(20)
    assert nombre >= 40
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"


def test_le_jumeau_refait_le_scenario_1_que_la_facade_sert_sur_chaque_temoin():
    """Tous les témoins, deux minutes de moteur Python : chaque type du
    résultat y est relu au moins une fois, les plus rares compris."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ecarts, types, nombre = _ecarts_du_scenario_1(1)
    assert nombre >= 900
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"
    assert TYPES_RARES <= types


def test_le_jumeau_refait_la_comparaison_que_la_facade_sert_sur_un_temoin_sur_quarante():
    """La comparaison entière — la carrière, les six scénarios, la fiche de
    paie, le journal, hors du contenu de la liquidation, qui ne passe pas."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ecarts, _, nombre = _ecarts_de_la_comparaison(40)
    assert nombre >= 20
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"


def test_le_jumeau_refait_la_comparaison_que_la_facade_sert_sur_chaque_temoin():
    """Tous les témoins, quatre minutes de moteur Python : chaque type de la
    comparaison y est relu au moins une fois. Seule s'écarte la fiche de paie
    de quatre témoins, où le jumeau ne suit pas le portage
    (:data:`FICHES_QUE_LE_JUMEAU_NE_REFAIT_PAS`)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ecarts, types, nombre = _ecarts_de_la_comparaison(1)
    assert nombre >= 900
    connus = {nom: [ecart for ecart in ecarts
                    if ecart.startswith(f"{nom}.remuneration.annees.")
                    and ".proposition." in ecart]
              for nom in FICHES_QUE_LE_JUMEAU_NE_REFAIT_PAS}
    autres = [ecart for ecart in ecarts if not any(ecart in fiche for fiche in connus.values())]
    assert not autres, f"{len(autres)} écart(s), dont : {autres[:5]}"
    assert TYPES_RARES | TYPES_DE_LA_COMPARAISON <= types
    if not TOLERANCE_DU_MOTEUR_PYTHON:
        assert all(connus.values()), [nom for nom, fiche in connus.items() if not fiche]


#: Une salariée née en 1965, partie à 64 ans.
COMMUN = dict(annee_naissance=1965, sexe="F", age_liquidation=64.0)

BATISSEURS = {
    "simple": ("carriere_simple", dict(
        **COMMUN, affiliation="salarie_prive_non_cadre", age_debut=23.0, niveau_salaire=1.4,
        nombre_enfants=2, naissances_enfants=("1992-03-10", "1995-07-02"), jour_naissance=14,
        mois_naissance=5, part_primes=0.0, profil_carriere="plat",
        interruptions={annee: "education_enfant" for annee in range(1995, 1998)},
        temps_partiel={2000: 0.5, 2001: 0.8})),
    "fonctionnaire": ("carriere_simple", dict(
        **COMMUN, affiliation="fonctionnaire_etat", age_debut=25.0, part_primes=0.2)),
    "veuve": ("carriere_simple", dict(
        annee_naissance=1920, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=21.0,
        age_liquidation=60.0, conjoint={"naissance": "1925", "sexe": "F"}, deces="1982-10-15")),
    "parcours": ("carriere_parcours", dict(
        **COMMUN, metiers=[Metier("salarie_prive_non_cadre", 21.0), Metier("artisan", 40.0, 0.8),
                           Metier("profession_liberale", 45.0, 0.3, cumul=True, age_fin=50.0)])),
    "releve": ("carriere_releve", dict(
        **COMMUN, releve=[LigneRelevee(1990, "salarie_prive_non_cadre", 15000.0),
                          LigneRelevee(1991, "artisan", 18000.0, trimestres=3),
                          LigneRelevee(1992, "salarie_prive_non_cadre", 21000.5)])),
}


@pytest.mark.parametrize("cas", sorted(BATISSEURS))
def test_le_jumeau_batit_la_carriere_que_la_facade_sert(cas):
    """Chaque bâtisseur du simulateur, et ceux de ``Carriere`` sur ses séries :
    la carrière du portage, relue, est celle que le Python bâtit des mêmes
    arguments, champ par champ."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    batisseur, options = BATISSEURS[cas]
    servi = facade.Simulateur()
    refait = simulateur_python.Simulateur()
    attendue = pont.carriere_en_donnees(getattr(refait, batisseur)(**options))
    assert ecarts_d_ecriture(pont.carriere_en_donnees(getattr(servi, batisseur)(**options)),
                             attendue, tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == []
    de_carriere = {"carriere_simple": "depuis_profil", "carriere_parcours": "depuis_parcours"}
    if batisseur in de_carriere:
        directe = getattr(facade.Carriere, de_carriere[batisseur])(**options, macro=servi.macro)
        assert ecarts_d_ecriture(pont.carriere_en_donnees(directe), attendue,
                                 tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == []


# -- les tables du moteur --------------------------------------------------------------

def _mere_partie_tot(simulateur):
    return simulateur.carriere_simple(
        annee_naissance=1965, sexe="F", affiliation="salarie_prive_non_cadre", age_debut=18,
        age_liquidation=62, nombre_enfants=2)


def _tranche_b(simulateur, annee: int):
    (periode,) = [periode for periode in simulateur.catalogue["agirc"].periodes_actives(annee)
                  if periode.assiette == "tranche_b"]
    return periode


#: Des appels de chaque méthode de table que la façade sert
#: (``pont.TABLES_DE_LA_FACADE``) : ``(table, méthode, arguments)``, les
#: arguments bâtis sur le simulateur de chaque côté — sa carrière, ses séries,
#: une période de son catalogue.
APPELS_DES_TABLES = [
    ("carriere_longue", "cotises_reputes", lambda s: (_mere_partie_tot(s), 160, 8)),
    ("carriere_longue", "cotises_reputes", lambda s: (_mere_partie_tot(s), 160, 0)),
    ("conversions_points", "echelle", lambda s: ("agirc", 1990, 2026)),
    ("conversions_points", "echelle", lambda s: ("arrco", 1990, 2026)),
    ("conversions_points", "fusion", lambda s: ("arrco", "agirc_arrco")),
    ("conversions_points", "fusion", lambda s: ("regime_general", "agirc_arrco")),
    ("durees_requises", "trimestres", lambda s: (1955,)),
    ("durees_requises", "trimestres", lambda s: (1965.75,)),
    ("minimum_contributif", "regle", lambda s: ("2026-01-01",)),
    ("minimum_contributif", "regle", lambda s: ("1990-01-01",)),
    ("minimum_contributif", "valeurs", lambda s: (2024,)),
    ("minimum_contributif", "valeurs", lambda s: (2023, 9)),
    ("minimum_garanti", "montant", lambda s: (2024, 120)),
    ("minimum_garanti", "montant", lambda s: (2024, 160, 168, 7)),
    ("minimum_garanti", "reference", lambda s: (2024,)),
    ("minimum_garanti", "reference", lambda s: (2010, 7)),
    ("minimum_vieillesse", "plafond", lambda s: (2025,)),
    ("minimum_vieillesse", "plafond", lambda s: (1930,)),
    ("revalorisations_pensions", "generale",
     lambda s: (datetime.date(1986, 12, 31), datetime.date(1988, 12, 31), False, None)),
    ("revalorisations_pensions", "generale",
     lambda s: (datetime.date(2017, 12, 31), datetime.date(2024, 12, 31), True, 1500.0)),
    ("reversions", "limite_cumul", lambda s: (2001,)),
    ("reversions", "majoration_enfant", lambda s: (2010,)),
    ("reversions", "minimum", lambda s: (2025,)),
    ("reversions", "minimum", lambda s: (1940,)),
    ("reversions", "plafond_majoration", lambda s: (2010,)),
    ("valeurs_point", "achat", lambda s: ("agirc_arrco", 2024)),
    ("valeurs_point", "achat", lambda s: ("agirc", 1990)),
    ("valeurs_point", "achat", lambda s: ("agirc_arrco", 2090)),
    ("valeurs_point", "achat_prolonge", lambda s: ("agirc_arrco", 2046, s.macro)),
    ("valeurs_point", "garantie", lambda s: ("agirc", _tranche_b(s, 1995), 1995, 1.0, 1.0)),
    ("valeurs_point", "garantie", lambda s: ("agirc", _tranche_b(s, 2010), 2010, 0.5, 0.8)),
    ("valeurs_point", "regimes_convenus", lambda s: ("valeur_service",)),
]


def test_chaque_methode_de_table_servie_a_son_appel_confronte():
    assert {(table, methode) for table, methode, _ in APPELS_DES_TABLES} == {
        (table, methode) for table, methodes in pont.TABLES_DE_LA_FACADE.items()
        for methode in methodes}


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_rend_ce_que_la_facade_lit_dans_les_tables_du_moteur(parametres):
    """Chaque méthode de table que la façade sert, appelée par le portage sur
    sa table et par le jumeau sur la sienne : la même valeur, au bit près, sous
    les mêmes types."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    ecarts = []
    for table, methode, arguments in APPELS_DES_TABLES:
        lu = getattr(getattr(servi.scenario_actuel, table), methode)(*arguments(servi))
        refait = getattr(getattr(jumeau.scenario_actuel, table), methode)(*arguments(jumeau))
        if lu != refait or (not isinstance(refait, dict) and repr(lu) != repr(refait)):
            ecarts.append(f"{table}.{methode} : la façade lit {lu!r}, le jumeau rend {refait!r}")
    assert not ecarts, "\n".join(ecarts)


# -- les règles du droit ---------------------------------------------------------------

def _salarie(simulateur):
    return simulateur.carriere_simple(
        annee_naissance=1965, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=23,
        age_liquidation=64)


def _agent(simulateur):
    return simulateur.carriere_simple(
        annee_naissance=1945, sexe="H", affiliation="agent_sncf", age_debut=21,
        age_liquidation=64.0)


def _fonctionnaire(simulateur):
    return simulateur.carriere_simple(
        annee_naissance=1962, sexe="F", affiliation="fonctionnaire_etat", age_debut=22,
        age_liquidation=60, nombre_enfants=3)


def _du_regime(regime: str, annee: int, carriere, *suite):
    """Les arguments d'une règle qui lit le moteur, une période et une
    carrière : la période du régime à cette année, dans le catalogue du
    simulateur."""
    return lambda s: (s.scenario_actuel, s.catalogue[regime].periode(annee), carriere(s), *suite)


#: Des appels de chaque règle du droit que la façade sert
#: (``pont.REGLES_DE_LA_FACADE``) : ``(module, règle, arguments)``, les
#: arguments bâtis sur le simulateur de chaque côté — son moteur, une période
#: de son catalogue, sa carrière.
APPELS_DES_REGLES = [
    ("liquider", "abattement_points",
     _du_regime("agirc_arrco", 2019, _salarie, 100, 172, 57.0, 2022)),
    ("liquider", "abattement_points",
     _du_regime("agirc_arrco", 2019, _salarie, 172, 172, 62.0, 2027, 120, True, "active")),
    ("liquider", "abattement_points",
     _du_regime("ircantec", 2029, _salarie, 150, 172, 62.0, 2027)),
    ("liquider", "age_de_la_duree_atteinte",
     _du_regime("agirc_arrco", 2029, _salarie, 176, 172, 64.0)),
    ("liquider", "age_de_la_duree_atteinte",
     _du_regime("agirc_arrco", 2029, _salarie, 150, 172, 64.0)),
    ("liquider", "annees_au_prorata", lambda s: (21, 126, 174)),
    ("liquider", "annees_au_prorata", lambda s: (25, 1, 400)),
    ("liquider", "borne_de_la_duree", _du_regime("regime_general", 2029, _salarie, 172)),
    ("liquider", "borne_de_la_duree", _du_regime("sncf", 2009, _agent, 160)),
    ("liquider", "decote_opposable", _du_regime("regime_general", 2029, _salarie, 2029)),
    ("liquider", "decote_opposable", _du_regime("sncf", 2009, _agent, 2009)),
    ("liquider", "decote_opposable",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire, 2022)),
    ("liquider", "duree_proratisation", _du_regime("regime_general", 2029, _salarie, 172)),
    ("liquider", "duree_proratisation",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire, 168)),
    ("liquider", "moyenne_des_meilleures_annees",
     lambda s: ([30, 30, 30, 29, 30, 30, 24, 30, 30, 33, 40, 30, 30, 24, 30, 30, 23, 30, 16, 24,
                 30, 30], 13)),
    ("liquider", "moyenne_des_meilleures_annees", lambda s: ([12.5, 40.25, 7.0], 2)),
    ("liquider", "retranche_decote", _du_regime("regime_general", 2029, _salarie)),
    ("liquider", "retranche_decote",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire)),
    ("liquider", "revenu_des_cotisations_minimales", lambda s: (2016, 3000.0, 9.67)),
    ("liquider", "revenu_des_cotisations_minimales", lambda s: (2020, 9000.0, 10.15, 0.5)),
    ("liquider", "salaire_de_reference",
     lambda s: (s.scenario_actuel, "regime_general", _salarie(s),
                s.catalogue["regime_general"].periode(2029), 2029, True)),
    ("liquider", "salaire_de_reference",
     lambda s: (s.scenario_actuel, "regime_general", _salarie(s),
                s.catalogue["regime_general"].periode(2029), 2029, False, 1965, False,
                ("regime_general", "msa_salaries"), 2, 2000, 10, True, True)),
    ("liquider", "taux_de_majoration_de_1952_a_1972", lambda s: (15.0,)),
    ("liquider", "taux_de_majoration_de_1952_a_1972", lambda s: (22.5,)),
    ("liquider", "trimestres_de_decote",
     _du_regime("regime_general", 2029, _salarie, 150, 172, 62.0, 67.0)),
    ("liquider", "trimestres_de_decote",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire, 150, 168, 60.0, 65.0)),
    ("liquider", "trimestres_de_surcote_regimes_speciaux", lambda s: (_agent(s), 172, 160, 55.0)),
    ("liquider", "trimestres_de_surcote_regimes_speciaux", lambda s: (_agent(s), 159, 150, 55.0)),
    ("liquider", "valeur_du_point", lambda s: (s.scenario_actuel, "agirc_arrco", 2023)),
    ("liquider", "valeur_du_point",
     lambda s: (s.scenario_actuel, "agirc_arrco", DateMois(2023, 10))),
    ("liquider", "valeur_du_point", lambda s: (s.scenario_actuel, "arrco", 2022)),
    ("liquider", "valeur_du_point", lambda s: (s.scenario_actuel, "agirc_arrco", 2045)),
    ("liquider", "valeur_du_point", lambda s: (s.scenario_actuel, "regime_general", 2023)),
    ("ouvrir", "age_ouverture", _du_regime("regime_general", 2029, _salarie)),
    ("ouvrir", "age_ouverture",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire, False, False)),
    ("ouvrir", "age_ouverture", _du_regime("sncf", 2009, _agent)),
    ("ouvrir", "age_ouverture_commun", _du_regime("regime_general", 2029, _salarie)),
    ("ouvrir", "age_ouverture_commun",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire)),
    ("ouvrir", "age_ouverture_droit", lambda s: (s.scenario_actuel, _salarie(s))),
    ("ouvrir", "age_ouverture_droit", lambda s: (s.scenario_actuel, _fonctionnaire(s))),
    ("ouvrir", "age_surcote", _du_regime("regime_general", 2029, _salarie)),
    ("ouvrir", "age_surcote", _du_regime("sncf", 2009, _agent)),
    ("ouvrir", "age_taux_plein", _du_regime("regime_general", 2029, _salarie)),
    ("ouvrir", "age_taux_plein", _du_regime("fonction_publique_etat", 2022, _fonctionnaire)),
    ("ouvrir", "duree_requise", _du_regime("regime_general", 2029, _salarie)),
    ("ouvrir", "duree_requise", _du_regime("fonction_publique_etat", 2022, _fonctionnaire)),
    ("ouvrir", "duree_requise", _du_regime("sncf", 2009, _agent)),
]


def test_chaque_regle_du_droit_servie_a_son_appel_confronte():
    assert {(module, regle) for module, regle, _ in APPELS_DES_REGLES} == {
        (module, regle) for module, regles in pont.REGLES_DE_LA_FACADE.items()
        for regle in regles}


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_rend_ce_que_la_facade_lit_des_regles_du_droit(parametres):
    """Chaque règle du droit que la façade sert, appelée par le portage et par
    le jumeau, chacun sur son moteur : la même valeur, au bit près, sous le
    type que la règle annonce — un âge entier que le jumeau rend « 62 » revient
    « 62.0 » de la façade, qui le lit sous ce type."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    modules = {"liquider": liquider_python, "ouvrir": ouvrir_python}
    ecarts = []
    for module, regle, arguments in APPELS_DES_REGLES:
        lu = getattr(getattr(facade, module), regle)(*arguments(servi))
        refait = getattr(modules[module], regle)(*arguments(jumeau))
        if repr(lu) != repr(pont.lu_strictement(
                facade._type_rendu(getattr(modules[module], regle), vars(modules[module])),
                json.loads(json.dumps(pont._en_donnees(refait))), f"{module}.{regle}")):
            ecarts.append(f"{module}.{regle} : la façade lit {lu!r}, le jumeau rend {refait!r}")
    assert not ecarts, "\n".join(ecarts)
