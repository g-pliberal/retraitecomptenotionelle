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

from retraite_notionnelle import carriere as carriere_python
from retraite_notionnelle import pont
from retraite_notionnelle import revalorisation as revalorisation_python
from retraite_notionnelle import simulateur as simulateur_python
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere as CarrierePython
from retraite_notionnelle.carriere import LigneRelevee, Metier
from retraite_notionnelle.config import RACINE_PROJET, ContributionEtat, Parametres
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.droit import acquerir as acquerir_python
from retraite_notionnelle.droit import categories as categories_python
from retraite_notionnelle.droit import commun as commun_python
from retraite_notionnelle.droit import completer as completer_python
from retraite_notionnelle.moteur import compte as compte_python
from retraite_notionnelle.droit import compter as compter_python
from retraite_notionnelle.droit import cultes as cultes_python
from retraite_notionnelle.droit import cumul as cumul_python
from retraite_notionnelle.droit import departs as departs_python
from retraite_notionnelle.droit import foyer as foyer_python
from retraite_notionnelle.droit import invalidite as invalidite_python
from retraite_notionnelle.droit import limite_age as limite_age_python
from retraite_notionnelle.droit import liquidation as liquidation_python
from retraite_notionnelle.droit import liquider as liquider_python
from retraite_notionnelle.droit import ouvrir as ouvrir_python
from retraite_notionnelle.droit import progressive as progressive_python
from retraite_notionnelle.droit import reversion as reversion_python
from retraite_notionnelle.droit import releve as releve_python
from retraite_notionnelle.droit.commun import PensionRegime
from retraite_notionnelle.droit.liquider import EligibleMinimum
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


#: Les parts entre lesquelles se découpe la confrontation de tous les témoins :
#: chacune est un cas, que les processus de la suite se partagent (action 135).
#: D'un seul tenant, la comparaison durait de quatre à six minutes sur une
#: machine de GitHub, et fermait la tranche qui la portait.
PARTS = 8


def _noms(pas: int, part: int = 0, parts: int = 1) -> list[str]:
    """Un témoin sur ``pas``, dans l'ordre des noms, puis la part ``part`` des
    ``parts``."""
    return sorted(json.loads(TEMOINS.read_text(encoding="utf-8")))[::pas][part::parts]


def _carrieres(pas: int, part: int = 0, parts: int = 1) -> dict:
    """Les témoins de :func:`_noms` : la carrière de chacun, que le portage
    bâtit de sa requête, et ses paramètres."""
    temoins = json.loads(TEMOINS.read_text(encoding="utf-8"))
    carrieres, refus = pont.carrieres_des_saisies(
        [{"cle": nom, "requete": temoins[nom]["requete"]} for nom in _noms(pas, part, parts)])
    assert refus == {}
    return carrieres


def _ecarts(pas: int, entree, part: int = 0,
            parts: int = 1) -> tuple[list[str], set[str], int]:
    """Les carrières de :func:`_carrieres`, passées à ``entree`` — liquidées,
    ou simulées — sur le simulateur de la façade et sur celui du Python, sous
    leurs paramètres. Les écarts, les types relus, et le nombre de carrières."""
    carrieres = _carrieres(pas, part, parts)
    ecarts, types = [], set()
    for nom, (parametres, carriere) in carrieres.items():
        servi = entree(facade.Simulateur(parametres), carriere)
        refait = entree(simulateur_python.Simulateur(parametres), carriere)
        assert type(servi) is type(refait)
        ecarts += ecarts_d_ecriture(_a_plat(refait, set()), _a_plat(servi, types), (nom,),
                                    tolerance=TOLERANCE_DU_MOTEUR_PYTHON)
    return ecarts, types, len(carrieres)


def _scenario_1(simulateur, carriere):
    return simulateur.scenario_actuel.calculer(carriere)


def _comparaison(simulateur, carriere):
    return simulateur.simuler(carriere)


def test_le_jumeau_refait_le_scenario_1_que_la_facade_sert_sur_un_temoin_sur_vingt():
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ecarts, _, nombre = _ecarts(20, _scenario_1)
    assert nombre >= 40
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"


@pytest.mark.parametrize("part", range(PARTS))
def test_le_jumeau_refait_le_scenario_1_que_la_facade_sert_sur_chaque_temoin(part):
    """Tous les témoins, en :data:`PARTS` parts : deux minutes de moteur
    Python en tout. Que chaque type du résultat y soit relu, les plus rares
    compris, :func:`test_la_facade_sert_chaque_type_sur_l_ensemble_des_temoins`
    le dit."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ecarts, _, nombre = _ecarts(1, _scenario_1, part, PARTS)
    assert nombre >= 900 // PARTS
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"


def test_le_jumeau_refait_la_comparaison_que_la_facade_sert_sur_un_temoin_sur_quarante():
    """La comparaison entière — la carrière, les six scénarios, la fiche de
    paie, le journal, hors du contenu de la liquidation, qui ne passe pas."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ecarts, _, nombre = _ecarts(40, _comparaison)
    assert nombre >= 20
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"


@pytest.mark.parametrize("part", range(PARTS))
def test_le_jumeau_refait_la_comparaison_que_la_facade_sert_sur_chaque_temoin(part):
    """Tous les témoins, en :data:`PARTS` parts : quatre minutes de moteur
    Python en tout. La fiche de paie de quatre témoins s'en écartait sous la
    proposition, de 3 à 6 € de réduction générale : le portage arrondissait
    mal son coefficient (``tests/js/reduction-generale.test.js``)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ecarts, _, nombre = _ecarts(1, _comparaison, part, PARTS)
    assert nombre >= 900 // PARTS
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"


def test_les_parts_couvrent_chaque_temoin_une_fois():
    """Les parts, réunies, sont tous les témoins, chacun une fois."""
    temoins = _noms(1)
    parts = [_noms(1, part, PARTS) for part in range(PARTS)]
    assert sorted(nom for part in parts for nom in part) == temoins
    assert len(temoins) >= 900


def test_la_facade_sert_chaque_type_sur_l_ensemble_des_temoins():
    """Sur tous les témoins, la façade sert au moins une fois chaque type du
    scénario 1, les plus rares compris, et chaque type de la comparaison :
    chaque part confrontant au jumeau, champ par champ, tout ce que la façade
    sert, chacun de ces types y est confronté. La façade seule : une minute
    de node, sans le moteur Python."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    du_scenario_1, de_la_comparaison = set(), set()
    for parametres, carriere in _carrieres(1).values():
        simulateur = facade.Simulateur(parametres)
        _a_plat(_scenario_1(simulateur, carriere), du_scenario_1)
        _a_plat(_comparaison(simulateur, carriere), de_la_comparaison)
    assert TYPES_RARES <= du_scenario_1
    assert TYPES_RARES | TYPES_DE_LA_COMPARAISON <= de_la_comparaison


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
    """Chaque batisseur du simulateur, et ceux de ``Carriere`` sur ses séries :
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
    de_carriere = {"carriere_simple": "depuis_profil", "carriere_parcours": "depuis_parcours",
                   "carriere_releve": "depuis_releve"}
    if batisseur in de_carriere:
        directe = getattr(facade.Carriere, de_carriere[batisseur])(**options, macro=servi.macro)
        assert ecarts_d_ecriture(pont.carriere_en_donnees(directe), attendue,
                                 tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == []


# -- les tables du moteur --------------------------------------------------------------

def _mere_partie_tot(simulateur):
    return simulateur.carriere_simple(
        annee_naissance=1965, sexe="F", affiliation="salarie_prive_non_cadre", age_debut=18,
        age_liquidation=62, nombre_enfants=2)


def _entre_a_seize_ans(simulateur):
    """Un fonctionnaire de l'État né en 1946, entré à seize ans, parti en
    2005 : les portes de la carrière longue des fonctionnaires."""
    return simulateur.carriere_simple(
        annee_naissance=1946, sexe="H", affiliation="fonctionnaire_etat", age_debut=16,
        age_liquidation=59.0)


def _parti_en_2000(simulateur):
    """Un salarié parti en 2000, avant toute porte de la carrière longue."""
    return simulateur.carriere_simple(
        annee_naissance=1940, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=16,
        age_liquidation=60.0)


def _entre_a_quinze_ans(simulateur):
    """Un fonctionnaire de l'État né en 1955, entré à quinze ans, parti en
    2014 : sa carrière longue s'ouvre avant le départ."""
    return simulateur.carriere_simple(
        annee_naissance=1955, sexe="H", affiliation="fonctionnaire_etat", age_debut=15,
        age_liquidation=59.0)


def _tranche_b(simulateur, annee: int):
    (periode,) = [periode for periode in simulateur.catalogue["agirc"].periodes_actives(annee)
                  if periode.assiette == "tranche_b"]
    return periode


#: Des appels de chaque méthode de table que la façade sert
#: (``pont.TABLES_DE_LA_FACADE``) : ``(table, méthode, arguments)``, les
#: arguments bâtis sur le simulateur de chaque côté — sa carrière, ses séries,
#: une période de son catalogue.
def _salaire_moyen(simulateur):
    """Le salaire moyen des séries du simulateur : sa marque à la façade, une
    fonction de l'année au jumeau."""
    if isinstance(simulateur, facade.Simulateur):
        return facade.SALAIRE_MOYEN
    return lambda annee: carriere_python.salaire_moyen_annuel(simulateur.macro, annee)


APPELS_DES_TABLES = [
    ("grilles", "forfait", lambda s: ("marins", 2024, 40000.0, _salaire_moyen(s))),
    ("grilles", "forfait", lambda s: ("marins", 2040, 52000.0, _salaire_moyen(s))),
    ("grilles", "forfait", lambda s: ("marins", 2001, 15000.0, _salaire_moyen(s))),
    ("ages_categorie_active", "derogation", lambda s: ("active", 1960.0)),
    ("ages_jouissance_militaire", "age", lambda s: (1965,)),
    ("ages_jouissance_militaire", "age", lambda s: (1950.5,)),
    ("durees_services_militaires", "annees_requises", lambda s: ("non_officier", 2012.5)),
    ("durees_services_militaires", "annees_requises", lambda s: ("inconnue", 2020)),
    ("durees_services_militaires", "duree_de_base", lambda s: ("officier",)),
    ("durees_services_actifs", "annees_requises", lambda s: ("super_active", 2020)),
    ("durees_services_actifs", "duree_de_base", lambda s: ("active",)),
    ("durees_services_actifs", "duree_de_base", lambda s: ("inconnue",)),
    ("ages_categorie_active", "derogation", lambda s: ("active", 1980.0)),
    ("ages_categorie_active", "derogation", lambda s: ("super_active", 1970.0)),
    ("ages_categorie_active", "derogation", lambda s: ("sedentaire", 1960.0)),
    ("carriere_longue", "_portes", lambda s: (_entre_a_seize_ans(s), True)),
    ("carriere_longue", "_portes", lambda s: (_parti_en_2000(s),)),
    ("ages_annulation_decote", "age", lambda s: (1955.0,)),
    ("ages_annulation_decote", "age", lambda s: (1951.5,)),
    ("ages_ouverture", "age", lambda s: (1955.0,)),
    ("ages_ouverture", "age", lambda s: (1968.0,)),
    ("ages_ouverture", "age", lambda s: (1930.0,)),
    ("invalidites", "version", lambda s: ("inaptitude", "2024-03-01")),
    ("invalidites", "version", lambda s: ("inaptitude", "1960-01-01")),
    ("carriere_longue", "cotises_reputes", lambda s: (_mere_partie_tot(s), 160, 8)),
    ("carriere_longue", "cotises_reputes", lambda s: (_mere_partie_tot(s), 160, 0)),
    ("conversions_points", "echelle", lambda s: ("agirc", 1990, 2026)),
    ("conversions_points", "echelle", lambda s: ("arrco", 1990, 2026)),
    ("conversions_points", "fusion", lambda s: ("arrco", "agirc_arrco")),
    ("conversions_points", "fusion", lambda s: ("regime_general", "agirc_arrco")),
    ("durees_requises", "trimestres", lambda s: (1955,)),
    ("maximum_des_cultes", "valeur", lambda s: (1978,)),
    ("maximum_des_cultes", "valeur", lambda s: (1990,)),
    ("maximum_des_cultes", "valeur", lambda s: (2002,)),
    ("maximum_des_cultes", "valeur", lambda s: (2030,)),
    ("durees_requises", "trimestres", lambda s: (1965.75,)),
    ("minimum_contributif", "regle", lambda s: ("2026-01-01",)),
    ("minimum_contributif", "regle", lambda s: ("1990-01-01",)),
    ("minimum_contributif", "valeurs", lambda s: (2024,)),
    ("minimum_contributif", "valeurs", lambda s: (2023, 9)),
    ("minimum_garanti", "montant", lambda s: (2024, 120)),
    ("minimum_garanti", "montant", lambda s: (2024, 160, 168, 7)),
    ("minimum_garanti", "reference", lambda s: (2024,)),
    ("minimum_garanti", "reference", lambda s: (2010, 7)),
    ("complement_differentiel_rco", "regle", lambda s: ("2014-12-01",)),
    ("complement_differentiel_rco", "regle", lambda s: ("2023-09-01",)),
    ("complement_differentiel_rco", "smic_net", lambda s: (2021,)),
    ("complement_differentiel_rco", "smic_net", lambda s: (2035,)),
    ("complement_differentiel_rco", "smic_net", lambda s: (1990,)),
    ("minimum_vieillesse", "deux_etages", lambda s: (1950,)),
    ("minimum_vieillesse", "deux_etages", lambda s: (2005,)),
    ("minimum_vieillesse", "deux_etages", lambda s: (2007,)),
    ("pension_majoree_reference", "montant", lambda s: ("pmr_chef", 2026, 12)),
    ("pension_majoree_reference", "montant", lambda s: ("pmr_chef", 2030, 6)),
    ("pension_majoree_reference", "montant", lambda s: ("plafond_depuis_septembre_2023", 2030)),
    ("pension_majoree_reference", "montant", lambda s: ("mesure_inconnue", 2026)),
    ("pension_majoree_reference", "regle", lambda s: ("2008-12-01",)),
    ("pension_majoree_reference", "regle", lambda s: ("2026-06-01",)),
    ("minimum_vieillesse", "plafond", lambda s: (2025,)),
    ("minimum_vieillesse", "plafond", lambda s: (1930,)),
    ("minimum_vieillesse", "plafond_couple", lambda s: (2026,)),
    ("minimum_vieillesse", "plafond_couple", lambda s: (1990,)),
    ("revalorisations_pensions", "generale",
     lambda s: (datetime.date(1986, 12, 31), datetime.date(1988, 12, 31), False, None)),
    ("revalorisations_pensions", "generale",
     lambda s: (datetime.date(2017, 12, 31), datetime.date(2024, 12, 31), True, 1500.0)),
    ("reversions", "fiche_du_regime", lambda s: ("regime_general",)),
    ("reversions", "fiche_du_regime", lambda s: ("regime_lunaire",)),
    ("reversions", "limite_cumul", lambda s: (2001,)),
    ("reversions", "majoration_enfant", lambda s: (2010,)),
    ("reversions", "minimum", lambda s: (2025,)),
    ("reversions", "minimum", lambda s: (1940,)),
    ("reversions", "plafond_majoration", lambda s: (2010,)),
    ("reversions", "version", lambda s: (
        s.scenario_actuel.reversions.fiche_du_regime("regime_general"), "1985-01-01", "1984-06-15")),
    ("reversions", "version", lambda s: (
        s.scenario_actuel.reversions.fiche_du_regime("fonction_publique_etat"), "2026-01-01",
        "2025-11-02")),
    ("valeurs_point", "achat", lambda s: ("agirc_arrco", 2024)),
    ("valeurs_point", "achat", lambda s: ("agirc", 1990)),
    ("valeurs_point", "achat", lambda s: ("agirc_arrco", 2090)),
    ("valeurs_point", "achat_prolonge", lambda s: ("agirc_arrco", 2046, s.macro)),
    ("valeurs_point", "garantie", lambda s: ("agirc", _tranche_b(s, 1995), 1995, 1.0, 1.0)),
    ("valeurs_point", "garantie", lambda s: ("agirc", _tranche_b(s, 2010), 2010, 0.5, 0.8)),
    ("valeurs_point", "regimes_convenus", lambda s: ("valeur_service",)),
    ("valeurs_point", "service", lambda s: ("cnavpl", 2022)),
    ("fiches_datees", "regle", lambda s: ("pension_maximale_regime_general", "1965-01-01")),
    ("fiches_datees", "regle", lambda s: ("pension_maximale_regime_general", "2026-01-01")),
    ("fiches_datees", "regle", lambda s: ("majoration_conjoint_a_charge", "1990-01-01")),
    ("fiches_datees", "regle", lambda s: ("fiche_lunaire", "2026-01-01")),
    ("fiches_datees", "version",
     lambda s: ("majoration_enfants_plafond_fonction_publique", "1963-12-01")),
    ("fiches_datees", "version",
     lambda s: ("majoration_enfants_plafond_fonction_publique", "2021-01-01")),
    ("fiches_datees", "version", lambda s: ("fiche_lunaire", "2026-01-01")),
    ("minimum_contributif", "pension_minimum", lambda s: (1983, 3)),
    ("minimum_contributif", "pension_minimum", lambda s: (1970, 1)),
    ("minimum_contributif", "pension_minimum", lambda s: (1944, 12)),
    ("minimum_contributif", "avts", lambda s: (2025,)),
    ("minimum_contributif", "avts", lambda s: (1950, 6)),
    ("valeurs_point", "service", lambda s: ("agirc_arrco", 2045)),
    ("valeurs_point", "service", lambda s: ("regime_lunaire", 2020)),
    ("valeurs_point", "service_au", lambda s: ("organic_avant_1973", 1995, 1)),
    ("valeurs_point", "service_au", lambda s: ("agirc_arrco", 2022, 1)),
    ("valeurs_point", "service_au", lambda s: ("agirc_arrco", 2022, 11)),
    ("valeurs_point", "_en_vigueur", lambda s: ("agirc", "cotisation_garantie", 1996)),
    ("valeurs_point", "_en_vigueur", lambda s: ("ircantec", "valeur_service", 2090)),
    ("valeurs_point", "_en_vigueur", lambda s: ("agirc", "cotisation_garantie", 1950)),
    ("valeurs_point", "derniere_annee_servie", lambda s: ("agirc",)),
    ("valeurs_point", "derniere_annee_servie", lambda s: ("regime_lunaire",)),
    ("annees_salaire_reference", "annees", lambda s: (1940,)),
    ("annees_salaire_reference", "annees", lambda s: (1975,)),
    ("coefficients_minoration", "coefficient", lambda s: (1948,)),
    ("coefficients_minoration", "coefficient", lambda s: (1990,)),
    ("majorations_enfants_points", "taux", lambda s: ("arrco", 1985, 3)),
    ("majorations_enfants_points", "taux", lambda s: ("agirc", 2005, 4)),
    ("majorations_enfants_points", "taux", lambda s: ("agirc_arrco", 2022, 3, 2030)),
    ("majorations_enfants_points", "taux", lambda s: ("regime_lunaire", 2022, 3)),
    ("rendements", "rendement", lambda s: ("ircantec", 1975)),
    ("rendements", "rendement", lambda s: ("msa_non_salaries", 2040)),
    ("minimum_garanti", "ratio_point_indice", lambda s: (2019, 2020)),
    ("minimum_garanti", "ratio_point_indice", lambda s: (2010, 2024)),
    ("majorations_enfants", "par_enfant",
     lambda s: ("bonifications", "F", "2005-03-01", "2026-09-01", ["2005-03-01"])),
    ("majorations_enfants", "par_enfant",
     lambda s: ("mda", "F", "1980-05-01", "2020-01-01", ["1980-05-01"])),
    ("majorations_enfants", "par_enfant",
     lambda s: ("dispositif_lunaire", "F", "1980-05-01", "2020-01-01", ["1980-05-01"])),
    ("baremes_trimestre", "valeurs", lambda s: ("mines", DateMois(2009, 4))),
    ("baremes_trimestre", "valeurs", lambda s: ("mines", DateMois(1992, 6))),
    ("baremes_trimestre", "valeurs", lambda s: ("mines", DateMois(2028, 1))),
    ("ages_regimes", "ages", lambda s: ("ieg_actif_2011", 1960.0)),
    ("ages_regimes", "ages", lambda s: ("ieg_actif_2011", 1975.5)),
    ("ages_regimes", "ages", lambda s: ("table_lunaire", 1960.0)),
    ("ages_surcote_regimes_speciaux", "age", lambda s: (1965.0,)),
    ("ages_surcote_regimes_speciaux", "age", lambda s: (1940.0,)),
    ("calendriers_duree_requise", "trimestres", lambda s: ("regimes_speciaux_2008", 24120)),
    ("calendriers_duree_requise", "trimestres", lambda s: ("regimes_speciaux_2008", 23000)),
    ("decote_regimes_speciaux", "parametres", lambda s: (2012,)),
    ("decote_regimes_speciaux", "parametres", lambda s: (2005,)),
    ("durees_requises_regimes", "ligne", lambda s: ("ieg_2014", 1965.0, 24300)),
    ("durees_requises_regimes", "ligne", lambda s: ("ieg_2014", 1963 + 10 / 12, 24234)),
    ("surcote_baremes", "connait", lambda s: ("cnbf",)),
    ("services_ouvrant_pension", "annees", lambda s: ("fonction_publique_etat", "2020-01-01",
                                                        False)),
    ("services_ouvrant_pension", "annees", lambda s: ("sncf", "2000-01-01", False)),
    ("services_ouvrant_pension", "annees", lambda s: ("port_strasbourg", "2020-01-01", False)),
    ("surcote_baremes", "connait", lambda s: ("bareme_lunaire",)),
    ("surcote_baremes", "coefficient",
     lambda s: ("cnbf", [(DateMois(2010, 4), False), (DateMois(2010, 7), False)])),
    ("surcote_baremes", "coefficient",
     lambda s: ("cnbf", [(DateMois(2013, 1), True), (DateMois(2013, 4), True)])),
]


def test_chaque_methode_de_table_servie_a_son_appel_confronte():
    assert {(table, methode) for table, methode, _ in APPELS_DES_TABLES} == {
        (table, methode) for table, methodes in pont.TABLES_DE_LA_FACADE.items()
        for methode in methodes}


@pytest.mark.parametrize("parametres", [
    Parametres(), Parametres(conventions_cor=True),
    Parametres().avec(droit_contrefactuel="au_31_aout_2023")],
    ids=["reference", "conventions_cor", "au_31_aout_2023"])
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


def _maintenu(simulateur):
    """Un fonctionnaire né en 1990 qui demande à partir à soixante-quinze ans :
    radié à soixante-dix, au terme du maintien qu'on lui présume."""
    return simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="fonctionnaire_etat", age_debut=22,
        age_liquidation=75, jour_naissance=15)


def _policier(simulateur):
    """Un policier né en 1960, entré à 19 ans, parti à 52 ans : la
    super-active."""
    return simulateur.carriere_parcours(
        1960, "H", [Metier("fonctionnaire_etat_super_actif", 19.0, 1.0)], 52.0)


def _inapte(simulateur):
    """Un salarié né en 1952, inapte, parti à soixante-deux ans : l'âge de
    l'ASPA de sa version."""
    return simulateur.carriere_parcours(
        1952, "H", [Metier("salarie_prive_non_cadre", 21.0)], 62.0, mois_naissance=6,
        invalidite={"pension": None, "inaptitude": True, "radiation": None})


def _ex_invalide(annee_naissance, debut, salaire, fin, liquidation, declaree=None):
    """Un salarié né le 15 mars, invalide de ``fin`` à son départ, ou qui dit
    sa pension d'invalidité (``declaree``)."""
    def carriere(simulateur):
        return simulateur.carriere_parcours(
            annee_naissance, "H", [Metier("salarie_prive_non_cadre", debut, salaire)],
            liquidation, mois_naissance=3, jour_naissance=15,
            interruptions={annee: "invalidite"
                           for annee in range(fin, annee_naissance + int(liquidation) + 1)},
            invalidite=declaree)
    return carriere


#: L'ex-invalide de 2022 porté à l'AVTS ; celui de 1982, que sa pension
#: d'invalidité de deuxième catégorie relève ; le même, qui la dit de première.
_A_L_AVTS = _ex_invalide(1960, 47.5, 0.5, 2009, 62.0)
_DE_1982 = _ex_invalide(1942, 20.0, 1.0, 1982, 60.0)
_DE_PREMIERE = _ex_invalide(1942, 20.0, 1.0, 1982, 60.0,
                            {"pension": 39 + 10 / 12, "categorie": 1})


def _handicape(simulateur):
    """Né en 1973, cent quarante trimestres cotisés en situation de handicap à
    soixante-deux ans : le départ des handicapés."""
    return simulateur.carriere_parcours(
        1973, "H", [Metier("salarie_prive_non_cadre", 26.0 + 10 / 12, 1.0)], 62.0,
        mois_naissance=6, jour_naissance=1,
        invalidite={"pension": None, "inaptitude": False, "radiation": None,
                    "handicap": 21.0 + 7 / 12})


def _cadre_de_1925(simulateur):
    """Un cadre au quintuple du salaire moyen, parti en 1990 : le maximum des
    pensions du régime général."""
    return simulateur.carriere_simple(
        annee_naissance=1925, sexe="H", affiliation="salarie_prive_cadre", age_debut=20,
        age_liquidation=65, niveau_salaire=5.0)


def _salarie_agricole_de_1907(simulateur):
    """Un salarié agricole parti en 1972 : le maximum de son régime, le premier."""
    return simulateur.carriere_simple(
        annee_naissance=1907, sexe="H", affiliation="salarie_agricole", age_debut=20,
        age_liquidation=65, niveau_salaire=5.0)


def _du_regime(regime: str, annee: int, carriere, *suite):
    """Les arguments d'une règle qui lit le moteur, une période et une
    carrière : la période du régime à cette année, dans le catalogue du
    simulateur."""
    return lambda s: (s.scenario_actuel, s.catalogue[regime].periode(annee), carriere(s), *suite)


def _artisan(simulateur):
    return simulateur.carriere_simple(
        annee_naissance=1945, sexe="H", affiliation="artisan", age_debut=20, age_liquidation=62)


def _aligne(carriere, membres: tuple[str, ...]):
    """Les arguments de ``liquider.duree_du_regime_aligne`` : la carrière, les
    durées de son relevé, que chaque côté construit sur son moteur, et les
    régimes."""
    def arguments(s):
        construite = carriere(s)
        construire = (facade.releve if isinstance(s, facade.Simulateur)
                      else releve_python).construire
        return construite, construire(s.scenario_actuel, construite).durees, membres
    return arguments


def _mere_sous_l_avpf(simulateur):
    """Une mère née en 1962, au salaire bas, qui a élevé ses enfants de 1985 à
    2002 sous l'AVPF."""
    return simulateur.carriere_simple(
        annee_naissance=1962, sexe="F", affiliation="salarie_prive_non_cadre", age_debut=20,
        age_liquidation=64.5, niveau_salaire=0.3, profil_carriere="plat",
        interruptions={annee: "education_enfant" for annee in range(1985, 2003)})


def _pension(regime: str, maximum: bool) -> PensionRegime:
    """Une pension de régime, prise ou non sur la durée maximum."""
    return PensionRegime(regime=regime, montant=1000.0, type_calcul="annuites", detail="",
                         fiabilite=Fiabilite.CERTIFIEE, sur_la_duree_maximum=maximum)


def _ligne_de(carriere, annee: int):
    """Les arguments de ``commun.ligne_cotisee`` : le moteur, la carrière, et
    sa ligne de l'année."""
    def arguments(s):
        construite = carriere(s)
        return s.scenario_actuel, construite, next(
            ligne for ligne in construite.lignes if ligne.annee == annee)
    return arguments


#: Deux régimes porteurs du minimum : un artisan dont les droits d'avant 1973
#: bornent le minimum (D. 634-6), un polypensionné du régime général au-delà
#: de la durée requise.
_ARTISAN = EligibleMinimum(
    indice=0, prorata_assurance=100 / 166, prorata_cotise=53 / 166, taux_plein=True,
    duree_regime=100, cotisee_regime=53, proratisation=166, requis=166,
    duree_tous_regimes=167, cotisee_tous_regimes=120, bornee_avec=("cancava_avant_1973",))
_POLYPENSIONNE = EligibleMinimum(
    indice=1, prorata_assurance=1.0, prorata_cotise=90 / 161, taux_plein=True, surcote=1.025,
    duree_regime=100, cotisee_regime=90, proratisation=161, requis=161,
    duree_tous_regimes=156, cotisee_tous_regimes=144, porte_avpf=True,
    bornee_au_minimum_entier=True)
_PERIODES_COTISEES = {"majoration": "periodes_cotisees", "seuil_trimestres_cotises": 120}


def _mere(s, affiliation: str, enfants: int = 2):
    """Une mère née en 1958, partie à 62 ans, de ``enfants`` enfants."""
    return s.carriere_simple(1958, "F", affiliation, 20.0, 62.0, nombre_enfants=enfants)


def _en_couple(s, annee: int, conjoint: str | None = None):
    """Un salarié qui a 66 ans en ``annee``, marié à une conjointe née en
    ``conjoint`` qui déclare 4 000 € de ressources, ou seul."""
    return s.carriere_simple(
        annee_naissance=annee - 66, sexe="H", affiliation="salarie_prive_non_cadre",
        age_liquidation=66.0, age_debut=20.0, niveau_salaire=0.3,
        conjoint=None if conjoint is None else {
            "naissance": conjoint, "sexe": "F", "mariage": None, "ressources": 4000.0,
            "invalidite": None})


def _enfants_a_charge(simulateur):
    """Un cadre né en 1943, parti en 2005, père de quatre enfants : l'un
    majeur au départ, deux à charge, le dernier né après."""
    return simulateur.carriere_simple(
        annee_naissance=1943, sexe="H", affiliation="salarie_prive_cadre", age_debut=22.0,
        age_liquidation=62.0, nombre_enfants=4,
        naissances_enfants=("1985-01-01", "1990-06-01", "1992-11-01", "2006-01-01"))


#: Les étapes de deux majorations pour enfants à charge, à réunir.
_ETAPES_A_CHARGE = (("2010-01-01", (("arrco", 10.0),)), ("2012-06-01", (("arrco", 4.0),)),
                    ("2015-01-01", ()))
_AUTRES_ETAPES = (("2011-01-01", (("agirc", 2.0),)), ("2013-01-01", ()))


def _majoration_a_charge():
    from retraite_notionnelle.droit.commun import AvantageApplique

    return AvantageApplique(code="majoration_enfants", libelle="", montant=30.0,
                            par_regime=(("regime_general", 20.0), ("arrco", 10.0)),
                            a_charge=_ETAPES_A_CHARGE)


#: Des appels de chaque règle du droit que la façade sert
#: (``pont.REGLES_DE_LA_FACADE``) : ``(module, règle, arguments)``, les
#: arguments bâtis sur le simulateur de chaque côté — son moteur, une période
#: de son catalogue, sa carrière.
def _ministre(simulateur, naissance=1940, debut=20, depart=70, affiliation="ministre_du_culte"):
    return simulateur.carriere_simple(
        annee_naissance=naissance, sexe="H", affiliation=affiliation, mois_naissance=1,
        jour_naissance=15, age_debut=debut, age_liquidation=depart, niveau_salaire=1.0,
        profil_carriere="plat")


def _durees_du_ministre(*options):
    """Les durées du relevé d'un ministre du culte, sur le relevé de la
    façade ou sur celui du jumeau, selon le simulateur."""
    def durees(simulateur):
        module = facade.releve if isinstance(simulateur, facade.Simulateur) else releve_python
        return module.construire(simulateur.scenario_actuel,
                                 _ministre(simulateur, *options)).durees
    return durees


def _chomeur(naissance=1958, debut=20, depart=66, annees=range(2016, 2025)):
    """Un cadre au chômage indemnisé ces années-là, que la coupure au taux
    plein borne, ou non."""
    def carriere(simulateur):
        return simulateur.carriere_simple(
            annee_naissance=naissance, sexe="H", affiliation="salarie_prive_cadre",
            mois_naissance=1, jour_naissance=15, age_debut=debut, age_liquidation=depart,
            niveau_salaire=1.5, profil_carriere="plat",
            interruptions={annee: "chomage_indemnise" for annee in annees})
    return carriere


def _agricole(naissance, depart, metiers=(("exploitant_agricole", 20.0),)):
    """Un exploitant agricole à faible revenu, bâti sur le simulateur."""
    def carriere(simulateur):
        return simulateur.carriere_parcours(
            annee_naissance=naissance, sexe="H", jour_naissance=15,
            metiers=[Metier(code, debut, niveau_salaire=0.3) for code, debut in metiers],
            age_liquidation=depart)
    return carriere


def _plans(naissance, depart, quand=None):
    """Les arguments des plans de revalorisation d'un exploitant : ceux que
    sa liquidation a lus."""
    def arguments(simulateur):
        carriere = _agricole(naissance, depart)(simulateur)
        exploitant = simulateur.scenario_actuel.calculer(carriere).exploitant_agricole
        return (simulateur.scenario_actuel, carriere, exploitant.eligible, exploitant.pension,
                exploitant.trimestres, quand)
    return arguments


def _pmr(naissance, depart, ressources=0.0, metiers=(("exploitant_agricole", 20.0),)):
    """Les arguments de la pension majorée de référence d'un exploitant, sur
    une pension de base presque nulle."""
    def arguments(simulateur):
        carriere = _agricole(naissance, depart, metiers)(simulateur)
        eligible = simulateur.scenario_actuel.calculer(carriere).chef_d_exploitation.eligible
        return (simulateur.scenario_actuel, carriere, eligible,
                PensionRegime("msa_non_salaries", 0.0001, "annuites", "", Fiabilite.CERTIFIEE),
                ressources)
    return arguments


def _points_de_chef(naissance, depart, metiers):
    """Les droits du relevé d'un exploitant, et sa carrière."""
    def arguments(simulateur):
        carriere = _agricole(naissance, depart, metiers)(simulateur)
        construire = (facade.releve if isinstance(simulateur, facade.Simulateur)
                      else releve_python).construire
        return construire(simulateur.scenario_actuel, carriere).droits, carriere
    return arguments


def _point_de_la_fiche(annee):
    def arguments(simulateur):
        regime = simulateur.catalogue["msa_non_salaries"]
        return (simulateur.scenario_actuel,
                commun_python.periode_de_liquidation(regime, DateMois(annee, 1)), annee)
    return arguments



def _points_msa(annee, revenu):
    """Les points de R. 732-71 d'un revenu, sur la période de l'année du
    régime des non-salariés agricoles."""
    def arguments(simulateur):
        periode = simulateur.catalogue["msa_non_salaries"].periode(annee)
        return (simulateur.scenario_actuel, periode, annee, revenu)
    return arguments

#: Un relevé de fonctionnaire qui finit en 2024 à 80 %, et un autre qui
#: cumule un emploi et un chômage indemnisé, une ligne de trimestres
#: fractionnaires.
_RELEVE_A_80 = (LigneRelevee(2024, "fonctionnaire_etat", 16000.0, 4, quotite=0.8),)
_RELEVE_CUMULE = (LigneRelevee(2023, "salarie_prive_cadre", 30000.0),
                  LigneRelevee(2023, "salarie_prive_non_cadre", 5000.0, 1.5,
                               type_periode="chomage_indemnise"))

def _majores(**durees):
    """``liquider.duree_majoree_apres_taux_plein`` sur des durées posées : un
    assuré de soixante-cinq ans et sept mois en mai 2004 (circulaire Cnav
    n° 2004/20, point 45)."""
    carriere = CarrierePython(annee_naissance=1938, sexe="H", mois_naissance=10,
                              jour_naissance=1, age_liquidation=65 + 7 / 12)
    return lambda s: (s.scenario_actuel, s.catalogue["regime_general"].periode(2004), carriere,
                      pont.DureesPosees(durees), ("regime_general",),
                      durees["regime_general"], 150, 65.0)


def _assiette(affiliation, regime, annee):
    """``liquider.assiette_de_reference`` sur la ligne d'une année d'une
    carrière simple, sous la période de l'année du régime."""
    def arguments(simulateur):
        carriere = simulateur.carriere_simple(
            annee_naissance=1958, sexe="H", affiliation=affiliation, age_debut=25,
            age_liquidation=67, niveau_salaire=1.0, jour_naissance=1)
        ligne = next(ligne for ligne in carriere.lignes if ligne.annee == annee)
        if isinstance(simulateur, facade.Simulateur):
            ligne = facade.ligne_de(carriere, ligne)
        return (simulateur.scenario_actuel, simulateur.catalogue[regime].periode(annee), ligne)
    return arguments


def _fonctionnaire_parti_a_60_ans(simulateur):
    return simulateur.carriere_simple(
        annee_naissance=1970, sexe="H", affiliation="fonctionnaire_etat", age_debut=22,
        age_liquidation=60, niveau_salaire=1.0, jour_naissance=15, mois_naissance=6)


def _ancien_combattant(date, naissance, mois):
    """``categories.age_des_anciens_combattants`` : la règle datée de la fiche,
    une carrière de salarié, les mois de captivité et de services."""
    def arguments(simulateur):
        carriere = simulateur.carriere_simple(
            annee_naissance=naissance, sexe="H", affiliation="salarie_prive_non_cadre",
            age_debut=20, age_liquidation=62)
        regle = simulateur.scenario_actuel.fiches_datees.regle(
            "taux_plein_anciens_combattants_prisonniers", date)
        return simulateur.scenario_actuel, regle, carriere, mois
    return arguments


APPELS_DES_REGLES = [
    ("categories", "age_legal", lambda s: (s.scenario_actuel, _salarie(s))),
    ("categories", "age_des_anciens_combattants", _ancien_combattant("1990-01-01", 1925, 18)),
    ("categories", "age_des_anciens_combattants", _ancien_combattant("2020-01-01", 1955, 6)),
    ("categories", "age_des_anciens_combattants", _ancien_combattant("2026-03-01", 1960, 42)),
    ("categories", "age_des_anciens_combattants", _ancien_combattant("2026-03-01", 1960, 5)),
    ("liquider", "majoration_rafp", lambda s: (64.0, DateMois(2015, 2))),
    ("liquider", "majoration_rafp", lambda s: (68 + 4 / 12, DateMois(2027, 1))),
    ("liquider", "conversion_capital_rafp", lambda s: (62.0, DateMois(2021, 12))),
    ("liquider", "conversion_capital_rafp", lambda s: (64.5, DateMois(2031, 1))),
    ("liquider", "prestation_rafp", lambda s: (1200.0, 4900, 5125, 64.0, DateMois(2024, 4), 0)),
    ("liquider", "prestation_rafp", lambda s: (1200.0, 5125, 5125, 64.0, DateMois(2024, 4), 0)),
    ("liquider", "prestation_rafp", lambda s: (1200.0, 4700, 5125, 64.0, DateMois(2024, 3), 16)),
    ("liquider", "mois_apres_le_depart", lambda s: (_fonctionnaire_parti_a_60_ans(s), 64.0)),
    ("liquider", "mois_apres_le_depart", lambda s: (_fonctionnaire_parti_a_60_ans(s), 60.0)),
    ("liquider", "assiette_de_reference", _assiette("ministre_du_culte", "cavimac", 2008)),
    ("liquider", "assiette_de_reference", _assiette("ministre_du_culte", "cavimac", 1990)),
    ("liquider", "assiette_de_reference", _assiette("salarie_prive_non_cadre", "regime_general", 2010)),
    ("liquider", "duree_majoree_apres_taux_plein", _majores(regime_general=130, msa_salaries=10)),
    ("liquider", "duree_majoree_apres_taux_plein", _majores(regime_general=140, msa_salaries=5)),
    ("liquider", "duree_majoree_apres_taux_plein",
     _majores(regime_general=136, msa_salaries=2, cnavpl=10)),
    ("acquerir", "points_msa_retenus", lambda s: (15.0, 1993)),
    ("acquerir", "points_msa_retenus", lambda s: (15.0, 2000)),
    # Les quatre marches de R. 732-71, et le plafond, où M lit l'AVTS.
    ("acquerir", "points_msa", _points_msa(2025, 5_000.0)),
    ("acquerir", "points_msa", _points_msa(2025, 7_500.0)),
    ("acquerir", "points_msa", _points_msa(2025, 12_000.0)),
    ("acquerir", "points_msa", _points_msa(2025, 20_000.0)),
    ("acquerir", "points_msa", _points_msa(2025, 40_000.0)),
    ("acquerir", "points_msa", _points_msa(2025, 47_100.0)),
    ("acquerir", "points_msa", _points_msa(2002, 15_000.0)),
    ("liquider", "_coefficient_anticipation", lambda s: (12, 20)),
    ("liquider", "_coefficient_anticipation", lambda s: (15 + 1 / 3, 40)),
    ("liquider", "_coefficient_anticipation", lambda s: (21, 20)),
    ("ouvrir", "ouverture_carriere_longue",
     _du_regime("fonction_publique_etat", 2014, _entre_a_quinze_ans)),
    ("ouvrir", "ouverture_carriere_longue",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire)),
    ("liquider", "nombre_d_annees_retenues", _du_regime("regime_general", 2005, _salarie, 1940)),
    ("liquider", "nombre_d_annees_retenues", _du_regime("regime_general", 2029, _salarie, 1965)),
    ("liquider", "nombre_d_annees_retenues", _du_regime("rsi", 2007, _artisan, 1945)),
    ("carriere", "prolonger_releve",
     lambda s: (list(_RELEVE_A_80), DateMois(2028, 1), s.macro, None, None, {2026: 0.5})),
    ("carriere", "prolonger_releve",
     lambda s: (list(_RELEVE_CUMULE), DateMois(2026, 7), s.macro, {2025: "chomage_indemnise"},
                None, {2024: 0.6}, {2024: "apprenti"})),
    ("carriere", "salaire_moyen_annuel", lambda s: (s.macro, 1990)),
    ("carriere", "salaire_moyen_annuel", lambda s: (s.macro, 2030)),
    ("compter", "arrondir_les_services", lambda s: (20 * 360 + 45, {"unite_jours": 90, "seuil_jours": 45})),
    ("compter", "arrondir_les_services", lambda s: (180 + 89, {"unite_jours": 180, "seuil_jours": 90})),
    ("compter", "bonification_ouverte", lambda s: ("tout_enfant", 1990, 2000, 2010)),
    ("compter", "services_a_temps_partiel", lambda s: (4, 0.625)),
    ("compter", "services_a_temps_partiel", lambda s: (2, 0.5)),
    ("progressive", "regle", lambda s: (s.scenario_actuel, DateMois(2024, 3))),
    ("progressive", "regle", lambda s: (s.scenario_actuel, DateMois(1988, 4))),
    ("progressive", "age_minimum",
     lambda s: (s.scenario_actuel, _progressive(s), DateMois(2014, 6))),
    ("progressive", "age_minimum",
     lambda s: (s.scenario_actuel, _progressive(s), DateMois(2024, 3))),
    ("progressive", "duree_requise", lambda s: (s.scenario_actuel, DateMois(2000, 1))),
    ("progressive", "duree_requise", lambda s: (s.scenario_actuel, DateMois(1988, 4))),
    ("progressive", "regimes_ouverts", lambda s: (s.scenario_actuel, DateMois(2023, 9))),
    ("progressive", "regimes_liquides", lambda s: (s.scenario_actuel, DateMois(1990, 1))),
    ("progressive", "regimes_liquides", lambda s: (s.scenario_actuel, DateMois(2023, 9))),
    ("progressive", "fraction", lambda s: (s.scenario_actuel, DateMois(2000, 1), 0.5, False)),
    ("progressive", "fraction", lambda s: (s.scenario_actuel, DateMois(2020, 1), 0.625, False)),
    ("progressive", "fraction", lambda s: (s.scenario_actuel, DateMois(2024, 1), 0.45, True)),
    ("progressive", "recalculee", lambda s: (s.scenario_actuel, DateMois(2006, 6))),
    ("progressive", "recalculee", lambda s: (s.scenario_actuel, DateMois(2006, 7))),
    ("progressive", "examiner", lambda s: (s.scenario_actuel, _progressive(s))),
    ("progressive", "examiner", lambda s: (s.scenario_actuel, _progressive(s, quotite=0.9))),
    ("progressive", "examiner", lambda s: (s.scenario_actuel, _progressive(s, demande=None))),
    ("compter", "bonification_ouverte", lambda s: ("ne_avant_radiation", 2012, 1984, 2010)),
    ("compter", "droit_regime_special",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire, 2022, "ne_avant_radiation", 1992)),
    ("compter", "droit_regime_special",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire, 2022, "tout_enfant", 2030)),
    ("compter", "majoration_pour_enfants",
     lambda s: (s.scenario_actuel, _mere(s, "profession_liberale"), {"cnavpl": 160}, 2020)),
    ("compter", "majoration_pour_enfants",
     lambda s: (s.scenario_actuel, _mere(s, "salarie_prive_non_cadre"), {"mines": 160}, 2020)),
    ("compter", "majoration_pour_enfants",
     lambda s: (s.scenario_actuel, _mere(s, "fonctionnaire_etat", 3),
                {"regime_general": 40, "fonction_publique_etat": 120}, 2020)),
    ("completer", "_taux_majoration_enfants",
     lambda s: (s.catalogue["cipav_complementaire"], 3,
                s.catalogue["cipav_complementaire"].periode(2020))),
    ("completer", "_taux_majoration_enfants",
     lambda s: (s.catalogue["fonction_publique_etat"], 5)),
    ("completer", "_taux_majoration_enfants", lambda s: (s.catalogue["regime_general"], 2)),
    # Le versement unique : le seuil du régime général à sa date, avant et après
    # le premier ; le coefficient de l'Agirc-Arrco à l'âge révolu, dans la table
    # et au-delà.
    ("completer", "_seuil_a_la_date",
     lambda s: (s.scenario_actuel.fiches_datees.regle(
         "versement_forfaitaire_unique", "2015-09-01")["seuils"], "2015-10-01")),
    ("completer", "_seuil_a_la_date", lambda s: ([["1974-07-01", 26.68]], "1974-06-01")),
    # Le plafond de L. 18 : la surcote dans le plafond, puis hors de lui.
    ("completer", "majoration_sous_le_traitement",
     lambda s: (104.0, 10.4, 100.0, 24.0, False)),
    ("completer", "majoration_sous_le_traitement",
     lambda s: (104.0, 10.4, 100.0, 24.0, True)),
    ("completer", "coefficient_du_versement",
     lambda s: (s.scenario_actuel.fiches_datees.regle(
         "versement_unique_agirc_arrco", "2026-03-01"), 65.75)),
    ("completer", "coefficient_du_versement",
     lambda s: (s.scenario_actuel.fiches_datees.regle(
         "versement_unique_agirc_arrco", "2026-03-01"), 104.0)),
    # Le barème par tranches du régime unique, sous, entre et au-delà de ses
    # bornes, et sur un revenu nul.
    ("compte", "taux_du_bareme",
     lambda s: (((1.0, 0.2, 0.1), (8.0, 0.1, 0.05), (None, 0.05, 0.02)), 20_000.0, 47_100.0)),
    ("compte", "taux_du_bareme",
     lambda s: (((1.0, 0.2, 0.1), (8.0, 0.1, 0.05), (None, 0.05, 0.02)), 900_000.0, 47_100.0)),
    ("compte", "taux_du_bareme", lambda s: (((None, 0.2, 0.1),), 0.0, 47_100.0)),
    ("completer", "majoration_retraite_proportionnelle", _plans(1942, 60)),
    ("completer", "majoration_retraite_proportionnelle", _plans(1930, 65)),
    ("completer", "majoration_retraite_proportionnelle", _plans(1942, 60, "2005-01-01")),
    ("completer", "pension_majoree", _pmr(1955, 64)),
    ("completer", "pension_majoree", _pmr(1955, 64, 9000.0)),
    ("completer", "pension_majoree",
     _pmr(1955, 64, 0.0, (("collaborateur_agricole", 20.0), ("exploitant_agricole", 40.0)))),
    ("completer", "points_rco_de_chef", _points_de_chef(
        1962, 64, (("exploitant_agricole", 20.0), ("collaborateur_agricole", 49.0)))),
    ("completer", "points_rco_de_chef", _points_de_chef(1955, 64, (("exploitant_agricole", 20.0),))),
    ("releve", "points_de_l_annee",
     lambda s: (s.scenario_actuel, "salarie_prive_cadre", 2018, "complementaire", 52_000.0)),
    ("releve", "points_de_l_annee",
     lambda s: (s.scenario_actuel, "exploitant_agricole", 2018, "base", 9_000.0, 4)),
    ("releve", "revenu_des_points",
     lambda s: (s.scenario_actuel, "exploitant_agricole", 2018, "complementaire", 221.89, 4)),
    ("releve", "revenu_des_points",
     lambda s: (s.scenario_actuel, "medecin_liberal", 2015, "base", 550, 4)),
    ("releve", "revenu_des_points",
     lambda s: (s.scenario_actuel, "medecin_liberal", 2003, "base", 400, 4)),
    ("liquider", "valeur_point_fiche", _point_de_la_fiche(2002)),
    ("liquider", "valeur_point_fiche", _point_de_la_fiche(1995)),
    # Le plafond du salaire de référence des marins (R. 11, 3°) : à l'indice
    # 100 de 2026, avant le décret n° 85-1148, au régime général qui n'en a
    # pas ; et la part au-delà de lui, comptée pour moitié.
    ("liquider", "plafond_du_salaire_de_reference", lambda s: (
        s.scenario_actuel, s.catalogue["marins"].periode(2026), 2026, 1)),
    ("liquider", "plafond_du_salaire_de_reference", lambda s: (
        s.scenario_actuel, s.catalogue["marins"].periode(1985), 1985, 10)),
    ("liquider", "plafond_du_salaire_de_reference", lambda s: (
        s.scenario_actuel, s.catalogue["regime_general"].periode(2008), 2008, 7)),
    ("liquider", "abattre_au_dela_du_plafond", lambda s: (100000.0, 98298.1376, 0.5)),
    ("liquider", "abattre_au_dela_du_plafond", lambda s: (76867.05, 98298.1376, 0.5)),
    ("ouvrir", "fin_indemnisation", lambda s: (s.scenario_actuel, _chomeur()(s))),
    ("ouvrir", "fin_indemnisation",
     lambda s: (s.scenario_actuel, _chomeur(1950, 30, 67, range(2008, 2018))(s))),
    ("ouvrir", "fin_indemnisation",
     lambda s: (s.scenario_actuel, _chomeur(1921, 18, 65, range(1980, 1987))(s))),
    ("ouvrir", "indemnisation_bornee", lambda s: (s.scenario_actuel, _chomeur()(s))),
    ("ouvrir", "indemnisation_bornee",
     lambda s: (s.scenario_actuel, _chomeur(1950, 30, 67, range(2008, 2018))(s))),
    ("ouvrir", "indemnisation_bornee",
     lambda s: (s.scenario_actuel, _chomeur(annees=(2000,))(s))),
    ("cultes", "part_de_l_ecart", lambda s: (1938,)),
    ("cultes", "part_de_l_ecart", lambda s: (1941,)),
    ("cultes", "part_de_l_ecart", lambda s: (1950,)),
    ("cultes", "durees", lambda s: (_durees_du_ministre()(s), ("cavimac",), True)),
    ("cultes", "durees", lambda s: (_durees_du_ministre(1975, 21, 64)(s), ("cavimac",), False)),
    ("cultes", "durees", lambda s: (
        _durees_du_ministre(1955, 30, 62, "membre_congregation")(s), ("cavimac",), True)),
    ("commun", "ligne_cotisee", _ligne_de(_mere_sous_l_avpf, 1984)),
    ("commun", "ligne_cotisee", _ligne_de(_mere_sous_l_avpf, 1990)),
    ("completer", "avpf_retenue",
     lambda s: (s.scenario_actuel, _mere_sous_l_avpf(s), 24)),
    ("completer", "avpf_retenue",
     lambda s: (s.scenario_actuel, _mere_sous_l_avpf(s), 0)),
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
    ("liquider", "duree_du_regime_aligne", _aligne(_salarie, ("regime_general",))),
    ("liquider", "duree_du_regime_aligne",
     _aligne(_artisan, ("cancava_avant_1973", "cancava"))),
    ("liquider", "duree_proratisation", _du_regime("regime_general", 2029, _salarie, 172)),
    ("liquider", "duree_proratisation",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire, 168)),
    ("liquider", "moyenne_des_meilleures_annees",
     lambda s: ([30, 30, 30, 29, 30, 30, 24, 30, 30, 33, 40, 30, 30, 24, 30, 30, 23, 30, 16, 24,
                 30, 30], 13)),
    ("liquider", "moyenne_des_meilleures_annees", lambda s: ([12.5, 40.25, 7.0], 2)),
    ("liquider", "majorer_les_points_de_1952_a_1972",
     lambda s: ({**{annee: 40.0 for annee in range(1955, 1961)},
                 **{annee: 15.0 for annee in range(1961, 1967)},
                 **{annee: 30.0 for annee in range(1967, 1974)}}, list(range(1961, 1974)))),
    ("liquider", "majorer_les_points_de_1952_a_1972",
     lambda s: ({1960: 14.5, 1961: 13.25}, [1960, 1961])),
    ("liquider", "majoration_des_points_de_1952_a_1972_d_avant_2026",
     lambda s: ([(1960, 1000.0), (1965, 600.0), (1965, 400.0), (1973, 1000.0)],
                list(range(1960, 1975)), 0.06, 3.0)),
    ("liquider", "majoration_des_points_de_1952_a_1972_d_avant_2026",
     lambda s: ([(1972, 2000.0)], (1972,), 0.06, 3.0)),
    ("liquider", "repartir_les_annees",
     lambda s: (25, {"alignes": 170, "msa_non_salaries": 2}, {"msa_non_salaries": 2},
                ("msa_non_salaries", "alignes"))),
    ("liquider", "repartir_les_annees",
     lambda s: (25, {"alignes": 0, "msa_non_salaries": 100})),
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
    ("liquider", "coefficient_surcote_datee",
     _du_regime("regime_general", 2029, _salarie, 180, 172, 8, 62.0)),
    ("liquider", "coefficient_surcote_datee",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire, 172, 168, 4, 60.0)),
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
    ("liquider", "pension_maximale", lambda s: (s.scenario_actuel, "regime_general",
                                                 _cadre_de_1925(s))),
    ("liquider", "pension_maximale", lambda s: (s.scenario_actuel, "msa_salaries",
                                                 _salarie_agricole_de_1907(s))),
    ("liquider", "pension_maximale", lambda s: (s.scenario_actuel, "cnav_pl",
                                                 _cadre_de_1925(s))),
    # La part du brut que retient la CSG, avant et après 2005 ; le premier jour
    # d'un mois.
    ("cumul", "assiette_csg", lambda s: (1998,)),
    ("cumul", "assiette_csg", lambda s: (2012,)),
    ("cumul", "assiette_csg", lambda s: (2025,)),
    ("cumul", "jour", lambda s: (DateMois(2025, 2),)),
    # La radiation par limite d'âge : un sédentaire maintenu jusqu'à soixante-dix
    # ans, un actif, une carrière qui finit avant sa limite.
    ("limite_age", "radiation", lambda s: (s.scenario_actuel, _maintenu(s))),
    ("limite_age", "radiation", lambda s: (s.scenario_actuel, _policier(s))),
    ("limite_age", "radiation", lambda s: (s.scenario_actuel, _fonctionnaire(s))),
    ("limite_age", "radier", lambda s: (s.scenario_actuel, _maintenu(s))),
    ("limite_age", "radier", lambda s: (s.scenario_actuel, _fonctionnaire(s))),
    ("liquider", "taux_acquis_l_emporte", lambda s: (0.55, 117, 0.5, 132, 87.7, 0.5, 1.0)),
    ("liquider", "taux_acquis_l_emporte", lambda s: (0.55, 60, 0.5, 68, 68.1, 0.5, 1.0)),
    ("liquider", "taux_acquis_l_emporte", lambda s: (0.55, 117, 0.5, 132, None, 0.5, 1.0)),
    ("invalidite", "age_de_l_aspa", lambda s: (s.scenario_actuel, _inapte(s))),
    ("invalidite", "rente_viagere_d_invalidite", lambda s: (30_000.0, 0.5, 40_000.0)),
    ("invalidite", "rente_viagere_d_invalidite", lambda s: (70_000.0, 0.65, 40_000.0)),
    ("invalidite", "rente_viagere_d_invalidite", lambda s: (900_000.0, 1.0, 40_000.0)),
    ("ouvrir", "age_taux_plein_droit", lambda s: (s.scenario_actuel, _handicape(s))),
    ("ouvrir", "age_taux_plein_droit", lambda s: (s.scenario_actuel, _salarie(s))),
    ("ouvrir", "age_annulation_droit", lambda s: (s.scenario_actuel, _handicape(s))),
    ("ouvrir", "age_annulation_droit", lambda s: (s.scenario_actuel, _salarie(s))),
    ("invalidite", "age_de_l_aspa", lambda s: (s.scenario_actuel, _salarie(s))),
    ("invalidite", "categorie_de_la_pension", lambda s: (s.scenario_actuel, _DE_1982(s))),
    ("invalidite", "categorie_de_la_pension", lambda s: (s.scenario_actuel, _DE_PREMIERE(s))),
    ("invalidite", "plancher_de_la_substitution",
     lambda s: (s.scenario_actuel, _A_L_AVTS(s), ["regime_general"])),
    ("invalidite", "plancher_de_la_substitution",
     lambda s: (s.scenario_actuel, _DE_1982(s), ["regime_general"])),
    ("invalidite", "plancher_de_la_substitution",
     lambda s: (s.scenario_actuel, _DE_PREMIERE(s), ["regime_general"])),
    ("invalidite", "plancher_de_la_substitution",
     lambda s: (s.scenario_actuel, _salarie(s), ["regime_general"])),
    ("completer", "fins_de_charge", lambda s: (_enfants_a_charge(s), {"age": 18}, "2005-04-01")),
    ("completer", "fins_de_charge", lambda s: (_enfants_a_charge(s), {"age": 25}, "2015-04-01")),
    ("commun", "parts_de_la_majoration", lambda s: ([_majoration_a_charge()],)),
    ("commun", "parts_de_la_majoration", lambda s: ([_majoration_a_charge()], "2013-12-31")),
    ("commun", "parts_de_la_majoration",
     lambda s: ([_majoration_a_charge()], "2013-12-31", False)),
    ("commun", "fusionner_les_charges", lambda s: (_ETAPES_A_CHARGE, _AUTRES_ETAPES)),
    ("commun", "fusionner_les_charges", lambda s: ((), _AUTRES_ETAPES)),
    ("commun", "date_d_effet", lambda s: (_cadre_de_1925(s),)),
    ("commun", "date_d_effet", lambda s: (_salarie(s),)),
    ("commun", "majoration_du_conjoint",
     lambda s: ((("1976-01-01", 609.80), ("2002-01-01", 609.80)), "1975-06-01")),
    ("commun", "majoration_du_conjoint",
     lambda s: ((("1976-01-01", 609.79), ("2002-01-01", 609.80)), "1999-06-01")),
    ("liquider", "maximum_des_pensions",
     lambda s: (s.scenario_actuel, "regime_general", "1965-01-01", 1965)),
    ("liquider", "maximum_des_pensions",
     lambda s: (s.scenario_actuel, "regime_general", "2026-01-01", 2026)),
    ("liquider", "maximum_des_pensions",
     lambda s: (s.scenario_actuel, "agirc_arrco", "2026-01-01", 2026)),
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
    ("ouvrir", "depart_parent_trois_enfants",
     _du_regime("fonction_publique_etat", 2022, _fonctionnaire)),
    ("ouvrir", "depart_parent_trois_enfants", _du_regime("regime_general", 2029, _salarie)),
    ("ouvrir", "derogation_active", _du_regime("fonction_publique_etat", 2012, _policier)),
    ("ouvrir", "derogation_active", _du_regime("fonction_publique_etat", 2022, _fonctionnaire)),
    ("ouvrir", "duree_requise", _du_regime("regime_general", 2029, _salarie)),
    ("ouvrir", "duree_requise", _du_regime("fonction_publique_etat", 2022, _fonctionnaire)),
    ("ouvrir", "duree_requise", _du_regime("sncf", 2009, _agent)),
    ("ouvrir", "mois_ouverture_des_droits", _du_regime("regime_general", 2029, _salarie)),
    ("ouvrir", "mois_ouverture_des_droits", _du_regime("sncf", 2009, _agent)),
    ("completer", "borne_avec_les_droits_d_avant_1973",
     lambda s: (4700.0, _ARTISAN, 0.0, 0, 0, 7831.22, 8557.38, True, _PERIODES_COTISEES, 0)),
    ("completer", "borne_avec_les_droits_d_avant_1973",
     lambda s: (4700.0, _ARTISAN, 120.5, 12, 8, 7831.22, 8557.38, True, _PERIODES_COTISEES, 0)),
    ("completer", "borne_avec_les_droits_d_avant_1973",
     lambda s: (9000.0, _POLYPENSIONNE, 10.0, 4, 4, 7831.22, 8557.38, False,
                {"majoration": "aucune"}, 0)),
    ("completer", "complement_minimum", lambda s: (621.0, 645.07, 1.025, (2009, 10))),
    ("completer", "complement_minimum", lambda s: (621.0, 633.61, 1.015, (2008, 1))),
    ("completer", "complement_minimum", lambda s: (0.0, 633.61, 1.015, (2008, 1))),
    ("completer", "majoration_ouverte", lambda s: (_PERIODES_COTISEES, 118)),
    ("completer", "majoration_ouverte", lambda s: (_PERIODES_COTISEES, 144)),
    ("completer", "majoration_ouverte", lambda s: ({"majoration": "aucune"}, 160)),
    ("completer", "plancher_du_regime", lambda s: (_ARTISAN, 7831.22, 8557.38, True, True)),
    ("completer", "plancher_du_regime",
     lambda s: (_POLYPENSIONNE, 584.48, 638.68, True, False)),
    ("completer", "selon_la_regle", lambda s: (_ARTISAN, {"majoration": "sans_distinction"}, 0)),
    ("completer", "selon_la_regle", lambda s: (_POLYPENSIONNE, _PERIODES_COTISEES, 24)),
    ("completer", "selon_la_regle", lambda s: (_ARTISAN, _PERIODES_COTISEES, 24)),
    ("foyer", "foyer_et_net", lambda s: (s.scenario_actuel, "assure", "2026-06-01", 2026,
                                         6000.0, True)),
    ("foyer", "foyer_et_net", lambda s: (s.scenario_actuel, "assure", "2026-06-01", 2026,
                                         6000.0, True, None, _en_couple(s, 2026, "1970"))),
    ("foyer", "foyer_et_net", lambda s: (s.scenario_actuel, "assure", "2026-06-01", 2026,
                                         1000.0, True, None, _en_couple(s, 2026, "1956"))),
    ("foyer", "foyer_et_net", lambda s: (s.scenario_actuel, "assure", "1990-06-01", 1990,
                                         0.0, True, None, _en_couple(s, 1990, "1940"))),
    ("foyer", "foyer_et_net", lambda s: (s.scenario_actuel, "assure", "1970-06-01", 1970,
                                         300.0, True, None, _en_couple(s, 1970))),
    ("foyer", "foyer_et_net", lambda s: (s.scenario_actuel, "assure", None, 2026, 6000.0,
                                         False)),
    ("reversion", "mois_de_mariage", lambda s: ("1990-06-15", "2000-03-15")),
    ("reversion", "mois_de_mariage", lambda s: ("2000-06-01", "1999-05-01")),
    ("reversion", "_cumuler",
     lambda s: ({"cumul": "limite", "cumul_taux": 0.52}, 1000.0, 50000.0, 65973.0, None, 1)),
    ("reversion", "_cumuler", lambda s: ({"cumul": "aucun"}, 3000.0, 2000.0, 0.0, None, 2)),
    ("reversion", "_cumuler",
     lambda s: ({"cumul": "limite", "cumul_taux": 0.5}, 8000.0, 9000.0, 3000.0, 15000.0, 2)),
    ("reversion", "_cumuler", lambda s: ({}, 8000.0, 9000.0, 3000.0, None, 1)),
    ("revalorisation", "majorations_forfaitaires",
     lambda s: (s.scenario_actuel, _pension("regime_general", True), "1970-02-01")),
    ("revalorisation", "majorations_forfaitaires",
     lambda s: (s.scenario_actuel, _pension("msa_salaries", True), "1970-02-01")),
    ("revalorisation", "majorations_forfaitaires",
     lambda s: (s.scenario_actuel, _pension("regime_general", False), "1972-02-01")),
    ("revalorisation", "majorations_forfaitaires",
     lambda s: (s.scenario_actuel, _pension("regime_general", True), "1980-02-01")),
    # Les départs : le policier dont la retraite additionnelle attend l'âge
    # légal, l'aide-soignante dont le régime général l'attend, la salariée
    # venue du privé qui demande sa pension plus tard, ou dans un régime où
    # elle n'a rien.
    ("departs", "age_legal", lambda s: (s.scenario_actuel, _policier(s))),
    ("departs", "departs", lambda s: (s.scenario_actuel, _policier(s))),
    ("departs", "departs", lambda s: (s.scenario_actuel, _soignante(s))),
    ("departs", "demandes", lambda s: (s.scenario_actuel, _venue_du_prive(s, arrco=59))),
    ("departs", "departs_et_demandes",
     lambda s: (s.scenario_actuel, _venue_du_prive(s, regime_general=67))),
    ("departs", "departs_et_demandes",
     lambda s: (s.scenario_actuel, _venue_du_prive(s, mines=64))),
]


def _progressive(s, quotite=0.6, demande="2025-11"):
    """La salariée née le 15 janvier 1965, partie à soixante-quatre ans, qui
    demande la retraite progressive en novembre 2025, à cette quotité, ou ne
    la demande pas."""
    return s.carriere_parcours(
        1965, "F", [Metier("salarie_prive_non_cadre", 20.0)], 64, jour_naissance=15,
        retraite_progressive=None if demande is None else {"age": 60.75, "quotite": quotite})


def _policier(s):
    return s.carriere_parcours(1970, "H", [Metier("fonctionnaire_etat_super_actif", 22.0)], 54,
                               part_primes=0.25)


def _soignante(s):
    return s.carriere_parcours(1965, "F", [Metier("salarie_prive_non_cadre", 20.0),
                                           Metier("fonctionnaire_territorial_hospitalier_actif",
                                                  30.0)], 57, jour_naissance=15)


def _venue_du_prive(s, **demandes):
    return s.carriere_parcours(1960, "F", [Metier("salarie_prive_non_cadre", 25.25),
                                           Metier("fonctionnaire_etat", 38.25)], 62,
                               demandes_de_pension=demandes)


def _ensembles_tries(objet):
    """Le dataclass, ses ensembles en suites triées."""
    return dataclasses.replace(objet, **{
        champ.name: tuple(sorted(getattr(objet, champ.name)))
        for champ in dataclasses.fields(objet)
        if isinstance(getattr(objet, champ.name), frozenset)})


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
    modules = {"acquerir": acquerir_python, "carriere": carriere_python, "commun": commun_python, "completer": completer_python,
               "compte": compte_python, "compter": compter_python, "foyer": foyer_python, "liquider": liquider_python, "ouvrir": ouvrir_python,
               "reversion": reversion_python, "revalorisation": revalorisation_python,
               "cultes": cultes_python, "departs": departs_python, "releve": releve_python,
               "invalidite": invalidite_python, "categories": categories_python,
               "limite_age": limite_age_python, "cumul": cumul_python,
               "progressive": progressive_python}
    ecarts = []
    for module, regle, arguments in APPELS_DES_REGLES:
        lu = getattr(facade.regles_de_la_reversion if module == "reversion"
                     else getattr(facade, module), regle)(*arguments(servi))
        refait = getattr(modules[module], regle)(*arguments(jumeau))
        if isinstance(refait, CarrierePython):
            # Une carrière que la règle rend : elle se compare comme celle
            # d'un bâtisseur, champ par champ, ses lignes comprises.
            # Relue comme le pont la relit : l'âge que le jumeau tient en
            # entier, la carrière du portage le tient en nombre.
            relue = pont.carriere_des_donnees(
                json.loads(json.dumps(pont.carriere_en_donnees(refait))))
            ecart = ecarts_d_ecriture(pont.carriere_en_donnees(lu),
                                      pont.carriere_en_donnees(relue),
                                      tolerance=TOLERANCE_DU_MOTEUR_PYTHON)
            if ecart:
                ecarts.append(f"{module}.{regle} : {ecart}")
            continue
        if dataclasses.is_dataclass(refait):
            # Un éligible ou un foyer que le jumeau rend : le portage l'écrit
            # sous ses noms, que la façade a lus ; il se compare champ à champ.
            # Une somme vide du jumeau vaut l'entier 0, que la façade lit 0.0,
            # sous le type que le champ annonce : la valeur seule se compare.
            refait = dataclasses.replace(refait, **{
                champ.name: float(getattr(refait, champ.name))
                for champ in dataclasses.fields(refait)
                if type(getattr(refait, champ.name)) is int
                and type(getattr(lu, champ.name)) is float})
            # Un ensemble (``Progressive.bases``) s'écrit dans l'ordre de son
            # hachage, qui change d'un processus à l'autre : il se compare trié.
            if repr(_ensembles_tries(lu)) != repr(_ensembles_tries(refait)):
                ecarts.append(f"{module}.{regle} : la façade lit {lu!r}, le jumeau rend "
                              f"{refait!r}")
            continue
        if type(refait) is dict:
            # La règle d'une fiche (``progressive.regle``) : un dictionnaire,
            # que le pont rend sous ses clés triées ; l'ordre ne compte pas.
            if json.dumps(lu, sort_keys=True) != json.dumps(refait, sort_keys=True):
                ecarts.append(f"{module}.{regle} : la façade lit {lu!r}, le jumeau rend "
                              f"{refait!r}")
            continue
        if repr(lu) != repr(pont.lu_strictement(
                facade._type_rendu(getattr(modules[module], regle), vars(modules[module])),
                json.loads(json.dumps(pont._en_donnees(refait))), f"{module}.{regle}")):
            ecarts.append(f"{module}.{regle} : la façade lit {lu!r}, le jumeau rend {refait!r}")
    assert not ecarts, "\n".join(ecarts)


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_rend_le_releve_que_la_facade_lit(parametres):
    """Le relevé des droits d'un salarié, d'un artisan d'avant 1973 et d'une
    fonctionnaire mère de trois enfants, construit par le portage et par le
    jumeau : les mêmes durées, par compte, régime et année, le même plafond
    de chaque année, les mêmes durées de régime et tous régimes, les mêmes
    points, au bit près."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    for carriere in (_salarie, _artisan, _fonctionnaire):
        lu = facade.releve.construire(servi.scenario_actuel, carriere(servi))
        construite = carriere(jumeau)
        refait = releve_python.construire(jumeau.scenario_actuel, construite)
        nom = carriere.__name__
        assert lu.durees.par_annee == {
            compte: {code: annees for code, annees in regimes.items()}
            for compte, regimes in refait.durees.par_annee.items()}, nom
        premiere = min(ligne.annee for ligne in construite.lignes)
        for compte in refait.durees.par_annee:
            assert [lu.durees.plafond(compte, annee) for annee in range(
                premiere, construite.date_liquidation.annee + 1)] == [
                refait.durees.plafond(compte, annee) for annee in range(
                    premiere, construite.date_liquidation.annee + 1)], (nom, compte)
        assert lu.durees.trimestres_par_regime == refait.durees.trimestres_par_regime, nom
        assert lu.durees.trimestres == refait.durees.trimestres, nom
        assert repr(lu.droits.points) == repr(pont.lu_strictement(
            tuple[tuple[str, int, float, float | None], ...],
            json.loads(json.dumps(pont._en_donnees(refait.droits.points))), nom)), nom
        assert repr(lu.droits.cotisations) == repr(pont.lu_strictement(
            tuple[tuple[str, int, float], ...],
            json.loads(json.dumps(pont._en_donnees(refait.droits.cotisations))), nom)), nom


#: Les drapeaux du relevé que la façade transmet, un à un.
DRAPEAUX_DU_RELEVE = ({}, {"avantages_non_contributifs": False}, {"points_gratuits": False},
                      {"liquider_successions": False})


def _en_json(valeur):
    return json.loads(json.dumps(pont._en_donnees(valeur)))


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_rend_le_releve_entier_et_ses_etapes_que_la_facade_lit(parametres):
    """Le relevé du salarié, de l'artisan d'avant 1973 et de la fonctionnaire
    mère de trois enfants, sous chacun de ses drapeaux, et chacune de ses
    étapes demandée seule : la même enveloppe du contrat C.5, les mêmes
    groupes, la même coordination, les mêmes durées et les mêmes droits sous
    leur schéma, les mêmes points acquis, plafonds et points gratuits, le
    même cumul plafonné de tous les régimes, au bit près."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.droit import acquerir as acquerir_python
    from retraite_notionnelle.droit import compter as compter_python
    from retraite_notionnelle.droit import coordonner as coordonner_python

    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    for carriere in (_salarie, _artisan, _fonctionnaire):
        lue, construite = carriere(servi), carriere(jumeau)
        for drapeaux in DRAPEAUX_DU_RELEVE:
            nom = (carriere.__name__, tuple(drapeaux))
            lu = facade.releve.construire(servi.scenario_actuel, lue, **drapeaux)
            refait = releve_python.construire(jumeau.scenario_actuel, construite, **drapeaux)
            assert lu.donnees() == _en_json(refait.donnees()), nom
            assert lu.groupes == refait.groupes, nom
            for etape in ("coordination", "durees", "droits"):
                assert getattr(lu, etape).donnees() == _en_json(
                    getattr(refait, etape).donnees()), (nom, etape)
            assert lu.coordination.regimes == refait.coordination.regimes, nom
            assert lu.durees.hors_annee == refait.durees.hors_annee, nom
            assert lu.droits.points_acquis == refait.droits.points_acquis, nom
            assert lu.droits.majoration_points == refait.droits.majoration_points, nom
            assert lu.droits.plafonds == tuple(refait.droits.plafonds), nom
            assert lu.droits.gratuits == refait.droits.gratuits, nom
        coordination = facade.coordonner.coordonner(servi.scenario_actuel, lue)
        refaite = coordonner_python.coordonner(jumeau.scenario_actuel, construite)
        assert coordination.donnees() == _en_json(refaite.donnees()), carriere.__name__
        for avantages in (True, False):
            durees = facade.compter.compter(servi.scenario_actuel, coordination, avantages)
            refaites = compter_python.compter(jumeau.scenario_actuel, refaite, avantages)
            assert durees.donnees() == _en_json(refaites.donnees()), carriere.__name__
            tous = tuple(refaites.par_annee["assurance"])
            assert durees.cumul_plafonne("assurance", tous) == refaites.cumul_plafonne(
                "assurance", tous), carriere.__name__
            for table in ("assurance", "cotises"):
                assert durees.cumul_plafonne(table, tous, lambda a: a % 3 == 0) == (
                    refaites.cumul_plafonne(table, tous, lambda a: a % 3 == 0)), (
                    carriere.__name__, table)
            droits = facade.acquerir.acquerir(servi.scenario_actuel, coordination, durees)
            assert droits.donnees() == _en_json(acquerir_python.acquerir(
                jumeau.scenario_actuel, refaite, refaites).donnees()), carriere.__name__



def test_le_jumeau_compte_les_contrats_et_les_jours_que_la_facade_lit():
    """Les trimestres d'un contrat d'apprentissage et les jours d'une période,
    année par année, pour des bornes de chaque sorte — un premier du mois ou
    non, un trimestre civil entier ou non, un contrat court, des jours
    déclarés ou non : les mêmes."""
    import datetime

    from retraite_notionnelle.droit import compter as compter_python

    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    jour = datetime.date
    bornes = [(jour(2014, 11, 15), jour(2016, 2, 15)), (jour(2020, 1, 1), jour(2020, 3, 30)),
              (jour(2019, 9, 1), jour(2020, 9, 1)), (jour(2013, 7, 16), jour(2017, 1, 1)),
              (jour(2015, 12, 20), jour(2017, 1, 10))]
    for debut, fin in bornes:
        assert facade.compter.trimestres_du_contrat(debut, fin) == (
            compter_python.trimestres_du_contrat(debut, fin)), debut
        for jours in (None, 37, 100):
            assert facade.compter.jours_par_annee(debut, fin, jours) == (
                compter_python.jours_par_annee(debut, fin, jours)), (debut, jours)


def test_le_jumeau_rend_la_periode_de_liquidation_que_la_facade_lit():
    """La période qui liquide une pension, demandée au portage par son rang :
    celle du catalogue que le jumeau rend, la même, pour plusieurs régimes et
    plusieurs dates, au-delà de la dernière année comprise."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur()
    for code in ("msa_non_salaries", "regime_general", "agirc_arrco", "fonction_publique_etat"):
        regime = servi.catalogue[code]
        for date in (DateMois(1975, 1), DateMois(2002, 7), DateMois(2019, 9),
                     DateMois(2100, 1)):
            assert facade.commun.periode_de_liquidation(regime, date) is (
                commun_python.periode_de_liquidation(regime, date)), (code, date)


# -- faire vivre ------------------------------------------------------------------------

def _exploitant(naissance, depart, metiers=(("exploitant_agricole", 20.0, 0.3),), **options):
    """Une carrière d'exploitant agricole, que « faire vivre » révise."""
    def carriere(simulateur):
        return simulateur.carriere_parcours(
            annee_naissance=naissance, sexe=options.pop("sexe", "H"), jour_naissance=15,
            metiers=[Metier(code, debut, niveau_salaire=niveau)
                     for code, debut, niveau in metiers],
            age_liquidation=depart, **options)
    return carriere


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_fait_vivre_ce_que_la_facade_lit(parametres):
    """« Faire vivre » des chefs d'exploitation partis en 1995, 2005, 2015 et
    2019, d'une conjointe collaboratrice et d'un salarié, à plusieurs
    échéances : la même ``Revalorisee``, champ par champ, au bit près du
    jumeau ; et le même ``ActuelAujourdhui``, le système 1 servi."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    cas = [(_exploitant(1930, 65), (1996, 1997, 2001, 2008, 2026)),
           (_exploitant(1943, 62), (2005, 2009, 2026)),
           (_exploitant(1953, 62), (2016, 2023, 2026)),
           (_exploitant(1957, 62, sexe="F",
                        metiers=(("collaborateur_agricole", 20.0, 0.3),)), (2020, 2026)),
           (_exploitant(1957, 62, metiers=(("salarie_prive_non_cadre", 20.0, 1.0),)), (2026,))]
    ecarts = []
    for carriere, annees in cas:
        lue, refaite = carriere(servi), carriere(jumeau)
        resultat = servi.scenario_actuel.calculer(lue)
        resultat_jumeau = jumeau.scenario_actuel.calculer(refaite)
        for annee in annees:
            lu = facade.faire_vivre(servi, lue, resultat, annee)
            refait = revalorisation_python.faire_vivre(jumeau, refaite, resultat_jumeau, annee)
            # Relue comme le pont la relit : la majoration d'une carrière sans
            # enfant, le jumeau l'écrit « 0 », une somme vide.
            relue = pont.lu_strictement(revalorisation_python.Revalorisee, json.loads(
                json.dumps(pont._en_donnees(refait))), "Revalorisee")
            ecart = ecarts_d_ecriture(lu, relue, tolerance=TOLERANCE_DU_MOTEUR_PYTHON)
            if ecart:
                ecarts.append(f"{lue.annee_naissance}, {annee} : {ecart}")
            # Et le système 1 servi cette année-là, l'ASPA d'aujourd'hui comprise.
            lu = facade.actuel_aujourd_hui(servi, lue, resultat, annee)
            refait = revalorisation_python.actuel_aujourd_hui(
                jumeau, refaite, resultat_jumeau, annee)
            relue = pont.lu_strictement(revalorisation_python.ActuelAujourdhui, json.loads(
                json.dumps(pont._en_donnees(refait))), "ActuelAujourdhui")
            ecart = ecarts_d_ecriture(lu, relue, tolerance=TOLERANCE_DU_MOTEUR_PYTHON)
            if ecart:
                ecarts.append(f"{lue.annee_naissance}, {annee}, aujourd'hui : {ecart}")
    assert not ecarts, "\n".join(ecarts)


# -- la liquidation ---------------------------------------------------------------------

@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_rend_la_liquidation_que_la_facade_lit(parametres):
    """La liquidation d'un salarié, d'un agent de la SNCF, d'un artisan d'avant
    1973 et d'une fonctionnaire mère de trois enfants, au départ de leur
    carrière, et celle, vivant, de la carrière d'un assuré mort avant son
    départ : le même taux, la même pension de chaque régime, au bit près."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    for carriere in (_salarie, _agent, _artisan, _fonctionnaire, _mort_avant, _mere_avpf):
        lue, refaite = carriere(servi), carriere(jumeau)
        nom = carriere.__name__
        demande = facade.liquidation.demande_de_depart(lue)
        assert demande == liquidation_python.demande_de_depart(refaite), nom
        for neutralisations in ((), ("avantages_non_contributifs",), ("avpf",),
                                ("points_gratuits", "decote_surcote")):
            avant, avant_jumeau = facade.liquidation.appels(), liquidation_python.appels()
            lu = facade.liquidation.liquider(
                demande, facade.liquidation.Etat(lue),
                facade.liquidation.Contexte(servi.scenario_actuel, frozenset(neutralisations)))
            refait = liquidation_python.liquider(
                liquidation_python.demande_de_depart(refaite), liquidation_python.Etat(refaite),
                liquidation_python.Contexte(jumeau.scenario_actuel, frozenset(neutralisations)))
            cas = (nom, neutralisations)
            assert lu.pensions.taux == refait.pensions.taux, cas
            assert repr(lu.regimes) == repr(pont.lu_strictement(
                tuple[PensionRegime, ...], json.loads(json.dumps(pont._en_donnees(refait.regimes))),
                nom)), cas
            assert lu.donnees() == _en_json(refait.donnees()), cas
            assert lu.releve.lignes() == _en_json(refait.releve.lignes()), cas
            assert (lu.total, lu.hors_repartition, lu.total_contributif) == (
                refait.total, refait.hors_repartition, refait.total_contributif), cas
            assert lu.fiabilite == refait.fiabilite, cas
            assert lu.mesures == refait.mesures, cas
            assert lu.avantages == tuple(refait.avantages), cas
            assert repr(lu.pensions.regimes) == repr(pont.lu_strictement(
                tuple[PensionRegime, ...],
                json.loads(json.dumps(pont._en_donnees(refait.pensions.regimes))), nom)), cas
            assert lu.pensions.plafonds == tuple(refait.pensions.plafonds), cas
            assert repr(lu.complements.regimes) == repr(pont.lu_strictement(
                tuple[PensionRegime, ...],
                json.loads(json.dumps(pont._en_donnees(refait.complements.regimes))), nom)), cas
            assert lu.complements.avantages == tuple(refait.complements.avantages), cas
            assert (facade.liquidation.appels() - avant
                    == liquidation_python.appels() - avant_jumeau), cas


def test_le_jumeau_rend_la_retraite_progressive_que_la_facade_lit():
    """La liquidation provisoire de la retraite progressive, les pensions
    provisoires que la pension complète ne peut descendre sous, et la pension
    complète relevée à l'une d'elles : la salariée devenue fonctionnaire, puis
    la mère de deux enfants, dont la surcote parentale se compare au plancher.
    Les mêmes pensions, au bit près."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi, jumeau = facade.Simulateur(), simulateur_python.Simulateur()

    def regimes(liquidee):
        return pont.lu_strictement(tuple[PensionRegime, ...],
                                   json.loads(json.dumps(pont._en_donnees(liquidee.regimes))),
                                   "regimes")

    def fonctionnaire(s):
        return s.carriere_parcours(1963, "F", [Metier("salarie_prive_non_cadre", 23.0),
                                               Metier("fonctionnaire_etat", 35.0)], 64,
                                   jour_naissance=15, part_primes=0.2,
                                   retraite_progressive={"age": 61.0, "quotite": 0.7})
    lue, refaite = fonctionnaire(servi), fonctionnaire(jumeau)
    examinee = facade.progressive.examiner(servi.scenario_actuel, lue)
    assert examinee == progressive_python.examiner(jumeau.scenario_actuel, refaite)
    provisoire = facade.progressive.liquider(
        servi.scenario_actuel, lue, facade.liquidation.Contexte(servi.scenario_actuel), examinee)
    refait = progressive_python.liquider(
        jumeau.scenario_actuel, refaite, liquidation_python.Contexte(jumeau.scenario_actuel),
        examinee)
    assert repr(provisoire.regimes) == repr(regimes(refait))
    assert provisoire.donnees() == _en_json(refait.donnees())
    for regimes_du_depart in (None, frozenset({"regime_general"})):
        assert facade.progressive.initiales(
            servi.scenario_actuel, examinee, provisoire, lue.date_liquidation,
            regimes_du_depart) == progressive_python.initiales(
            jumeau.scenario_actuel, examinee, refait, refaite.date_liquidation, regimes_du_depart)

    def mere(s):
        return s.carriere_simple(annee_naissance=1969, mois_naissance=1, jour_naissance=1,
                                 sexe="F", affiliation="salarie_prive_non_cadre", age_debut=18,
                                 age_liquidation=64, nombre_enfants=2)
    lue, refaite = mere(servi), mere(jumeau)
    libre = liquidation_python.liquider(
        liquidation_python.demande_de_depart(refaite), liquidation_python.Etat(refaite),
        liquidation_python.Contexte(jumeau.scenario_actuel))
    [complete] = [p for p in libre.regimes if p.regime == "regime_general"]
    for initiales in ((("regime_general", complete.montant - 1.0),),
                      (("regime_general", complete.montant + 1000.0),)):
        lu = facade.liquidation.liquider(
            facade.liquidation.demande_de_depart(lue),
            facade.liquidation.Etat(lue, initiales=initiales),
            facade.liquidation.Contexte(servi.scenario_actuel))
        refait = liquidation_python.liquider(
            liquidation_python.demande_de_depart(refaite),
            liquidation_python.Etat(refaite, initiales=initiales),
            liquidation_python.Contexte(jumeau.scenario_actuel))
        assert repr(lu.regimes) == repr(regimes(refait)), initiales
        assert lu.complements.plancher == refait.complements.plancher, initiales
        assert (lu.total, lu.total_contributif) == (refait.total, refait.total_contributif)
        assert lu.donnees() == _en_json(refait.donnees()), initiales


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_rend_les_etapes_de_la_liquidation_que_la_facade_lit(parametres):
    """Les étapes de la liquidation, chacune seule, sur le relevé du salarié,
    de l'agent de la SNCF, de l'artisan d'avant 1973, de la fonctionnaire
    mère de trois enfants et de la mère sous l'AVPF, sous quatre contextes, et
    le foyer de chacun sous ce contexte : la même ouverture, les mêmes
    pensions, les mêmes compléments et le même foyer, au bit près."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)

    def pensions_lues(pensions, cas):
        return repr(pont.lu_strictement(tuple[PensionRegime, ...], json.loads(json.dumps(
            pont._en_donnees(pensions))), str(cas)))

    for carriere in (_salarie, _agent, _artisan, _fonctionnaire, _mere_avpf):
        lue, refaite = carriere(servi), carriere(jumeau)
        releve = facade.releve.construire(servi.scenario_actuel, lue)
        refait = releve_python.construire(jumeau.scenario_actuel, refaite)
        ouverture = facade.ouvrir.ouvrir(servi.scenario_actuel, releve)
        ouverte = ouvrir_python.ouvrir(jumeau.scenario_actuel, refait)
        assert ouverture.donnees() == _en_json(ouverte.donnees()), carriere.__name__
        assert (ouverture.requis, ouverture.age, ouverture.motif,
                ouverture.trimestres_cotises) == (ouverte.requis, ouverte.age, ouverte.motif,
                                                  ouverte.trimestres_cotises)
        for neutralisations in (None, (), ("avantages_non_contributifs",), ("avpf",),
                                ("points_gratuits", "decote_surcote")):
            cas = (carriere.__name__, neutralisations)
            contexte, contexte_jumeau = (None, None) if neutralisations is None else (
                liquidation_python.Contexte(servi.scenario_actuel, frozenset(neutralisations)),
                liquidation_python.Contexte(jumeau.scenario_actuel, frozenset(neutralisations)))
            pensions = facade.liquider.liquider_chaque_regime(
                servi.scenario_actuel, releve, ouverture, contexte)
            liquidees = liquider_python.liquider_chaque_regime(
                jumeau.scenario_actuel, refait, ouverte, contexte_jumeau)
            assert pensions.donnees() == _en_json(liquidees.donnees()), cas
            assert pensions.taux == liquidees.taux, cas
            assert repr(pensions.regimes) == pensions_lues(liquidees.regimes, cas), cas
            complements = facade.completer.completer(
                servi.scenario_actuel, releve, ouverture, pensions, contexte)
            completees = completer_python.completer(
                jumeau.scenario_actuel, refait, ouverte, liquidees, contexte_jumeau)
            assert complements.donnees() == _en_json(completees.donnees()), cas
            assert complements.total == completees.total, cas
            assert repr(complements.regimes) == pensions_lues(completees.regimes, cas), cas
            date = ouverture.donnees()["date_effet"]
            lu = facade.foyer.foyer_et_net(servi.scenario_actuel, lue.personne, date,
                                           lue.annee_liquidation, complements.total, True,
                                           contexte)
            foyer_refait = foyer_python.foyer_et_net(
                jumeau.scenario_actuel, refaite.personne, date, refaite.annee_liquidation,
                completees.total, True, contexte_jumeau)
            assert lu.donnees() == _en_json(foyer_refait.donnees()), cas


def _mere_avpf(simulateur):
    """Une salariée née en 1970, deux enfants et deux années d'éducation qui
    ouvrent l'AVPF : la cascade mesure ses trimestres d'enfants, puis
    l'AVPF."""
    return simulateur.carriere_parcours(
        1970, "F", [Metier("salarie_prive_non_cadre", 21.0)], 64, nombre_enfants=2,
        interruptions={1998: "education_enfant", 1999: "education_enfant"})


def _mort_avant(simulateur):
    """Un salarié né en 1970 liquidé à cinquante-quatre ans, avant que son
    droit ne s'ouvre : la liquidation d'un vivant, décotée, que la réversion
    d'un assuré mort avant son départ compare à la sienne."""
    return simulateur.carriere_simple(
        annee_naissance=1970, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=22,
        age_liquidation=54)


# -- le constructeur du compte -----------------------------------------------------------

def _periode_active(regime: str, annee: int):
    """La première période active du régime cette année, dans le catalogue
    du simulateur."""
    return lambda s: next(iter(s.catalogue[regime].periodes_actives(annee)))


def _cumul(simulateur):
    """Un salarié du privé qui est aussi artisan en 2010 : deux activités la
    même année, que ``cotisation_annuelle`` additionne."""
    from retraite_notionnelle.carriere import AnneeCarriere, Carriere

    return Carriere(annee_naissance=1970, sexe="H", age_liquidation=64.0, lignes=[
        AnneeCarriere(annee=2010, revenu=30000.0, affiliation="salarie_prive_non_cadre"),
        AnneeCarriere(annee=2010, revenu=12000.0, affiliation="artisan")])


def _compte_entier(carriere, annee_debut=None):
    """Les arguments de ``construire`` : le compte de la carrière jusqu'à sa
    liquidation, ouvert à son début ou à ``annee_debut``."""
    return carriere, carriere.annee_liquidation, annee_debut


def _apres_la_bascule(simulateur):
    """Une fonctionnaire de l'État liquidée en 2039 : son compte passe au
    régime unique en 2026."""
    return simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat", age_debut=23,
        age_liquidation=64)


#: Des appels de chaque méthode de constructeur que la façade sert
#: (``pont.CONSTRUCTEURS_DE_LA_FACADE``) : ``(constructeur, méthode,
#: arguments)``, bâtis sur le simulateur de chaque côté.
APPELS_DES_CONSTRUCTEURS = [
    ("constructeur", "cotisation_annuelle", lambda s: (_salarie(s), 2000)),
    ("constructeur", "cotisation_annuelle", lambda s: (_cumul(s), 2010)),
    ("constructeur", "taux_effectif", lambda s: (
        "regime_general", _periode_active("regime_general", 2020)(s), 2020)),
    ("constructeur_employeur", "cotisation_annuelle", lambda s: (_fonctionnaire(s), 2010)),
    ("constructeur_employeur", "cotisation_annuelle", lambda s: (_artisan(s), 1970)),
    ("constructeur_employeur", "taux_effectif", lambda s: (
        "fonction_publique_etat", _periode_active("fonction_publique_etat", 2010)(s), 2010,
        False, False, True)),
    ("constructeur_employeur", "taux_effectif", lambda s: (
        "fonction_publique_etat", _periode_active("fonction_publique_etat", 2000)(s), 2000)),
    ("constructeur", "construire", lambda s: _compte_entier(_salarie(s))),
    ("constructeur", "construire", lambda s: _compte_entier(_cumul(s))),
    ("constructeur_employeur", "construire", lambda s: _compte_entier(_fonctionnaire(s))),
    ("constructeur_employeur", "construire", lambda s: _compte_entier(_artisan(s), 1975)),
    ("constructeur_prelevement", "cotisation_annuelle", lambda s: (_fonctionnaire(s), 2010)),
    ("constructeur_prelevement", "taux_effectif", lambda s: (
        "fonction_publique_etat", _periode_active("fonction_publique_etat", 2025)(s), 2025)),
    ("constructeur_prelevement", "construire", lambda s: _compte_entier(_fonctionnaire(s))),
    ("constructeur", "construire", lambda s: (
        *_compte_entier(_apres_la_bascule(s)), s.regime_fusionne)),
    ("constructeur_employeur", "construire", lambda s: (
        *_compte_entier(_apres_la_bascule(s)), s.regime_fusionne)),
    ("convertisseur", "population_de", lambda s: (_salarie(s),)),
    ("convertisseur", "population_de", lambda s: (_fonctionnaire(s),)),
    ("convertisseur", "population_de", lambda s: (None,)),
]


def test_chaque_methode_de_constructeur_servie_a_son_appel_confronte():
    assert {(nom, methode) for nom, methode, _ in APPELS_DES_CONSTRUCTEURS} == {
        (nom, methode) for nom, methodes in pont.CONSTRUCTEURS_DE_LA_FACADE.items()
        for methode in methodes}


@pytest.mark.parametrize("parametres", [
    Parametres(), Parametres(contribution_etat=ContributionEtat.ENTIERE)],
    ids=["reference", "etat_entiere"])
def test_le_jumeau_rend_ce_que_la_facade_lit_des_constructeurs(parametres):
    """Chaque méthode de constructeur que la façade sert, appelée par le
    portage sur son constructeur et par le jumeau sur le sien : la même
    valeur, au bit près, sous les mêmes types."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    ecarts = []
    for nom, methode, arguments in APPELS_DES_CONSTRUCTEURS:
        lu = getattr(getattr(servi, nom), methode)(*arguments(servi))
        refait = getattr(getattr(jumeau, nom), methode)(*arguments(jumeau))
        if repr(lu) != repr(refait):
            ecarts.append(f"{nom}.{methode} : la façade lit {lu!r}, le jumeau rend {refait!r}")
    assert not ecarts, "\n".join(ecarts)


def test_le_jumeau_rend_ce_que_lit_un_constructeur_bati_sous_d_autres_parametres():
    """Le constructeur du compte bâti des données d'un simulateur sous
    d'autres paramètres — la part de la cotisation, la contribution de
    l'État —, par le portage et par le jumeau : la même cotisation, le même
    compte, au bit près."""
    from retraite_notionnelle.config import PartCotisation
    from retraite_notionnelle.moteur.compte import ConstructeurCompte

    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur()
    jumeau = simulateur_python.Simulateur()
    ecarts = []
    for modifications in ({"part_cotisation": PartCotisation.TOTALE},
                          {"part_cotisation": PartCotisation.SALARIALE},
                          {"contribution_etat": ContributionEtat.ENTIERE}):
        def bati(s, batisseur):
            return batisseur(s.macro, s.catalogue, s.affiliations, s.indexation,
                             s.parametres.avec(**modifications))
        lu, refait = bati(servi, facade.ConstructeurCompte), bati(jumeau, ConstructeurCompte)
        for carriere in (_ministre, _fonctionnaire):
            for annee in (1970, 1990, 2000, 2010):
                a, b = (lu.cotisation_annuelle(carriere(servi), annee),
                        refait.cotisation_annuelle(carriere(jumeau), annee))
                if repr(a) != repr(b):
                    ecarts.append(f"{modifications} {annee} : {a!r} != {b!r}")
            a = lu.construire(*_compte_entier(carriere(servi)))
            b = refait.construire(*_compte_entier(carriere(jumeau)))
            if repr(a) != repr(b):
                ecarts.append(f"{modifications} construire : {a!r} != {b!r}")
    assert not ecarts, "\n".join(ecarts)


@pytest.mark.parametrize("parametres", [
    Parametres(), Parametres(annee_bascule=2035)], ids=["reference", "bascule_2035"])
def test_le_jumeau_rend_le_regime_unique_que_la_facade_lit(parametres):
    """Le régime unique du simulateur, fusionné par le portage et par le
    jumeau : le même, au bit près, sous les mêmes types."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    lu = facade.Simulateur(parametres).regime_fusionne
    refait = simulateur_python.Simulateur(parametres).regime_fusionne
    assert repr(lu) == repr(refait)


def test_le_jumeau_majore_les_petites_pensions_que_la_facade_lit():
    """Les exemples de la circulaire Cnav n° 2023-21 que
    ``test_majoration_exceptionnelle.py`` rejoue — une liquidation unique, des
    régimes d'avant elle, le plafond tous régimes : les mêmes régimes servis et
    le même calcul de la caisse, au bit près du jumeau."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from types import SimpleNamespace

    servi = facade.Simulateur()
    jumeau = simulateur_python.Simulateur()
    debut = datetime.date(2023, 8, 1)

    def petite(regime, validee, cotisee, maximum, tous):
        return completer_python.PetitePension(
            regime=regime, taux_plein=True, cotisee=cotisee, validee=validee,
            maximum=maximum, cotises_tous_regimes=tous)

    cas = [
        ([("regime_general", 710.94, "annuites")], [petite("regime_general", 170, 146, 167, 146)]),
        ([("regime_general", 740.0, "annuites"), ("rsi", 250.0, "annuites"),
          ("agirc_arrco", 250.0, "points"), ("rci", 40.0, "points")],
         [petite("regime_general", 120, 115, 165, 165), petite("rsi", 55, 50, 165, 165)]),
        ([("regime_general", 500.0, "annuites"), ("rsi", 300.0, "annuites"),
          ("agirc_arrco", 502.23, "points")],
         [petite("regime_general", 160, 96, 160, 144), petite("rsi", 160, 48, 160, 144)]),
    ]
    for pensions, petites in cas:
        regimes = [PensionRegime(code, mensuel * 12.0, calcul, "", Fiabilite.CERTIFIEE)
                   for code, mensuel, calcul in pensions]
        datees = [(p, 2023, debut, p.montant) for p in regimes]
        servis = [revalorisation_python.RegimeServi(p.regime, p.montant, 1.0, "regime_general",
                                                    Fiabilite.CERTIFIEE) for p in regimes]
        resultat = SimpleNamespace(petites_pensions=tuple(petites), avantages_appliques=[])
        fin = datetime.date(2026, 12, 31)
        lu = facade.majorer_les_petites_pensions(
            servi.scenario_actuel, resultat, datees, servis, facade.PensionServie(servi), {},
            None, fin)
        refait = revalorisation_python.majorer_les_petites_pensions(
            jumeau.scenario_actuel, resultat, datees, servis,
            revalorisation_python.PensionServie(jumeau), {}, None, fin)
        assert lu[1], pensions
        assert not ecarts_d_ecriture(list(lu[0]), list(refait[0]),
                                     tolerance=TOLERANCE_DU_MOTEUR_PYTHON), pensions
        assert not ecarts_d_ecriture(list(lu[1]), list(refait[1]),
                                     tolerance=TOLERANCE_DU_MOTEUR_PYTHON), pensions


#: Les appels de la mortalité du simulateur : un quotient observé, un âge et
#: une date fractionnaires, une année projetée, une année au-delà des tables ;
#: et les types de pension de la Cnav, publiés à plusieurs âges, dont les
#: facteurs sont par tranche d'âge (``facteurs_par_age``).
APPELS_DE_LA_MORTALITE = [
    ("survie_annuelle", (70, 1950, "H")),
    ("survie_annuelle", (63 + 4 / 12, 2038.5, "F")),
    ("survie_annuelle", (85.0, 2060, "H")),
    ("survie_annuelle", (95.25, 2130, "F")),
    ("courbe", (62.0, 2031.0, None, True, None)),
    ("courbe", (66.0, 2045.0, None, True, "niveau_de_vie_v03")),
    ("courbe", (60.5, 2028.25, "F", True, "fonctionnaires_civils_etat")),
    ("courbe", (70.0, 2020.0, "H", False, None)),
    ("courbe", (62.0, 2017.0, "H", False, "cnav_inaptitude")),
    ("courbe", (63 + 4 / 12, 2030.5, None, True, "cnav_ex_invalide")),
    ("courbe", (58.75, 2024.25, "F", True, "cnav_pension_normale")),
    ("survie", (62.0, 2030, 15, "H")),
    ("survie", (64.5, 2041, 40, "F", False)),
    ("esperance_residuelle", (60.0, 2024.0)),
    ("esperance_residuelle", (62.0, 2017.0, "H", False, "cnav_inaptitude")),
    ("esperance_residuelle", (65.25, 2035.5, "F", True, "fonctionnaires_civils_etat")),
    ("courbe_survie", (65, 2025, "F", True, None)),
    ("courbe_survie", (62.5, 2031.25, "H", True, "niveau_de_vie_v07")),
    ("courbe_survie", (60.0, 2017.0, "H", False, "cnav_inaptitude")),
    ("population_niveau_de_vie_euros", (1450.0,)),
    ("population_niveau_de_vie_euros", (0.0,)),
]


def test_chaque_methode_de_la_mortalite_servie_a_son_appel_confronte():
    assert {methode for methode, _ in APPELS_DE_LA_MORTALITE} == set(
        pont.MORTALITE_DE_LA_FACADE)


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_rend_la_mortalite_que_la_facade_lit(parametres):
    """La survie d'une année, calculée par le portage et par le jumeau sur les
    données de mortalité de leur simulateur : la même, au bit près."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(parametres).mortalite
    jumeau = simulateur_python.Simulateur(parametres).mortalite
    for methode, arguments in APPELS_DE_LA_MORTALITE:
        assert getattr(servi, methode)(*arguments) == getattr(jumeau, methode)(*arguments), (
            methode, arguments)


def _ecart_des_carrieres(lue, refaite) -> str | None:
    """Deux carrières comparées comme celles d'un bâtisseur, champ par champ,
    la refaite relue comme le pont la relit."""
    relue = pont.carriere_des_donnees(json.loads(json.dumps(pont.carriere_en_donnees(refaite))))
    return ecarts_d_ecriture(pont.carriere_en_donnees(lue), pont.carriere_en_donnees(relue),
                             tolerance=TOLERANCE_DU_MOTEUR_PYTHON)


def test_le_jumeau_rend_la_proposition_que_la_facade_lit():
    """Le départ de la proposition, la carrière prolongée, sans activité ou
    travaillée, et le scénario 6 : ce que le portage rend, le jumeau le
    refait."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(Parametres())
    jumeau = simulateur_python.Simulateur(Parametres())
    precoce = servi.carriere_simple(annee_naissance=1970, sexe="F",
                                    affiliation="salarie_prive_cadre", age_debut=23,
                                    age_liquidation=62.5, mois_naissance=7)
    ecarts = []
    reportee = servi.carriere_proposition(precoce)
    ecarts.append(_ecart_des_carrieres(reportee, jumeau.carriere_proposition(precoce)))
    for attente in (True, False):
        ecarts.append(_ecart_des_carrieres(
            facade.prolongee(precoce, 64.25, servi.macro, attente),
            precoce.prolongee(64.25, jumeau.macro, attente)))
    assert [e for e in ecarts if e] == []
    lu = servi.proposition(reportee)
    refait = jumeau.proposition(reportee)
    assert lu.pension_annuelle == pytest.approx(refait.pension_annuelle,
                                                rel=TOLERANCE_DU_MOTEUR_PYTHON)
    assert lu.conversion.diviseur == pytest.approx(refait.conversion.diviseur,
                                                   rel=TOLERANCE_DU_MOTEUR_PYTHON)


def test_chaque_constante_du_droit_lue_au_portage_est_celle_du_jumeau():
    """Une constante que la façade lit au portage
    (``pont.CONSTANTES_DE_LA_FACADE``) : la même que celle du jumeau, que le
    moteur Python du scénario 1 tient."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.scenarios.actuel import ScenarioActuel

    assert pont.CONSTANTES_DE_LA_FACADE == {"liquider": ("SURCOTE_AGE_MAJORE",)}
    assert pont.constante_du_droit("liquider", "SURCOTE_AGE_MAJORE") == (
        ScenarioActuel.SURCOTE_AGE_MAJORE)


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_rend_la_garantie_vieillesse_que_la_facade_lit(parametres):
    """La garantie vieillesse de la proposition, sur une carrière liquidée à
    soixante-six ans et une autre à soixante-deux, sous plusieurs pensions et
    une rente : la même, au bit près."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    for age in (66, 62):
        def carriere(simulateur):
            return simulateur.carriere_simple(
                annee_naissance=1960, sexe="F", affiliation="salarie_prive_non_cadre",
                age_debut=22, age_liquidation=age, niveau_salaire=0.3)
        lue, refaite = carriere(servi), carriere(jumeau)
        for pension, rente in ((3600.0, 0.0), (10800.0, 0.0), (60000.0, 0.0), (3600.0, 1200.0)):
            assert servi.scenario_liberal._garantie_vieillesse(lue, pension, rente) == (
                jumeau.scenario_liberal._garantie_vieillesse(refaite, pension, rente)), (
                age, pension, rente)


# -- l'échéancier, le journal et le pilote ----------------------------------------------

def _retraite_de_2005(simulateur):
    """Un salarié né en 1945 parti en 2005 : l'échéance de l'année courante
    fait vivre sa pension et revoit son ASPA."""
    return simulateur.carriere_parcours(1945, "H", [Metier("salarie_prive_non_cadre", 20.0)], 60)


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_parcourt_l_echeancier_que_la_facade_lit(parametres):
    """L'échéancier du salarié, de l'agent de la SNCF, de la fonctionnaire,
    de la mère que l'AVPF couvre et du retraité de 2005, parcouru jusqu'à
    l'échéance de l'année courante : le même journal — chaque entrée, ce qui
    la date, et son contenu quand il passe —, le même scénario 1 au départ et
    aujourd'hui, les mêmes appels de ``liquider`` ; le même départ tiré de la
    carrière ; et, sur ce journal, ce que le journal sert à chaque date."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import echeancier as echeancier_python

    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    annee = parametres.annee_courante
    for carriere in (_salarie, _agent, _fonctionnaire, _mere_avpf, _retraite_de_2005):
        lue, refaite = carriere(servi), carriere(jumeau)
        nom = carriere.__name__
        assert facade.echeancier.depart_de(lue) == echeancier_python.depart_de(refaite), nom
        lu, refait = facade.echeancier.Echeancier(servi), echeancier_python.Echeancier(jumeau)
        avant, avant_jumeau = facade.liquidation.appels(), liquidation_python.appels()
        journal = lu.parcourir(lue, echeance=annee)
        journal_jumeau = refait.parcourir(refaite, echeance=annee)
        assert (facade.liquidation.appels() - avant
                == liquidation_python.appels() - avant_jumeau), nom
        assert [(e.id, e.evenement, e.inscrite_le, e.debut, e.fin, e.sorte, e.remplace)
                for e in journal] == [
            (e.id, e.evenement, e.inscrite_le, e.debut, e.fin, e.sorte, e.remplace)
            for e in journal_jumeau], nom
        for entree, refaite_entree in zip(journal, journal_jumeau):
            assert entree.donnees() == _en_json(refaite_entree.donnees()), (nom, entree.id)
        assert lu.au_depart == pont.resultat_actuel_des_donnees(_en_json(refait.au_depart)), nom
        assert (lu.aujourd_hui is None) == (refait.aujourd_hui is None), nom
        for date in ("2004-12-31", "2005-06-01", f"{annee:04d}-12-31"):
            for sorte in (None, "composante", "foyer"):
                assert [e.id for e in journal.servi(date, sorte=sorte)] == [
                    e.id for e in journal_jumeau.servi(date, sorte=sorte)], (nom, date, sorte)
            assert [e.id for e in journal.etat_au(date)] == [
                e.id for e in journal_jumeau.etat_au(date)], (nom, date)
    # Ce que chaque sorte appelle, que le paquet garde du vocabulaire, sans
    # ce qui la dit.
    assert facade.echeancier.SORTES == {
        nom: {cle: sorte[cle] for cle in ("liquider", "motif", "nature") if cle in sorte}
        for nom, sorte in echeancier_python.SORTES.items()}


@pytest.mark.parametrize("parametres", [Parametres(), Parametres(conventions_cor=True)],
                         ids=["reference", "conventions_cor"])
def test_le_jumeau_date_le_depart_que_le_pilote_de_la_facade_lit(parametres):
    """L'âge de départ des six premiers cas types, nés en 1950, 1960 et 1975,
    sous la règle du droit et l'âge écrit : le même que le pilote du jumeau."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import pilote as pilote_python
    from retraite_notionnelle.castypes import CAS_TYPES

    servi = facade.Simulateur(parametres)
    jumeau = simulateur_python.Simulateur(parametres)
    for cas in CAS_TYPES[:6]:
        for generation in (1950, 1960, 1975):
            for variante in ("droit", "absolu"):
                assert facade.pilote.age_de_depart(servi, cas, generation, variante) == (
                    pilote_python.age_de_depart(jumeau, cas, generation, variante)), (
                    cas.code, generation, variante)


# -- le profil de rémunération ----------------------------------------------------------

_PROFILS_JS = """
import { readFileSync } from "node:fs";
import { bornesDeformation, profilSalaire } from "./moteur/js/carriere.js";
const [profils, ages, annees] = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
process.stdout.write(JSON.stringify(profils.map(([profil, affiliation]) => [
  bornesDeformation(paquet, profil, affiliation),
  annees.map((annee) => ages.map((age) => profilSalaire(paquet, profil, age, annee, affiliation))),
])));
"""


def test_les_deux_jumeaux_lisent_le_meme_profil_au_bit_pres():
    """Le profil de chaque métier, chaque année d'une carrière : le Python le
    lit pour les carrières types du coût, le portage pour celles du site. Ils
    l'écrivaient de deux façons, qui différaient au dernier bit à quatre âges
    entiers (`tests/js/profil-salaire.test.js`), et une ligne de revenu d'autant. Ils rendent
    les mêmes flottants à chaque demi-année de 14 à 80 ans, sous la modulation
    de huit années, pour chaque profil nommé et le profil déduit de chaque
    affiliation que les tables nomment, et les bornes que la page affiche."""
    import subprocess

    from retraite_notionnelle.carriere import (
        PROFIL_AUTOMATIQUE, PROFIL_PAR_AFFILIATION, PROFIL_SECTEUR_PAR_AFFILIATION,
        PROFILS_CATEGORIE, bornes_deformation, profil_salaire)
    from retraite_notionnelle.config import RACINE_DONNEES

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    profils = [(nom, None) for nom in PROFILS_CATEGORIE] + [
        (PROFIL_AUTOMATIQUE, affiliation) for affiliation in sorted(
            {*PROFIL_PAR_AFFILIATION, *PROFIL_SECTEUR_PAR_AFFILIATION,
             "salarie_prive_non_cadre"})]
    ages = [demi / 2 for demi in range(28, 162)]
    annees = [1950, 1962, 1975, 1993, 2000, 2010, 2024, 2040]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _PROFILS_JS,
         json.dumps([profils, ages, annees])],
        cwd=RACINE_PROJET, capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    ecarts = []
    for (profil, affiliation), (bornes, par_annee) in zip(
            profils, json.loads(execution.stdout), strict=True):
        if list(bornes_deformation(RACINE_DONNEES, profil, affiliation)) != bornes:
            ecarts.append(f"bornes de {profil} ({affiliation})")
        for annee, valeurs in zip(annees, par_annee, strict=True):
            for age, valeur in zip(ages, valeurs, strict=True):
                attendu = profil_salaire(RACINE_DONNEES, profil, age, annee, affiliation)
                if valeur != attendu:
                    ecarts.append(f"{profil} ({affiliation}), {age} ans en {annee} : "
                                  f"python={attendu!r} portage={valeur!r}")
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:12])


# -- les noms hérités du prototype (venu de test_moteur.py) -------------------


#: Les noms que tout objet de JavaScript hérite de son prototype.
NOMS_HERITES = ("constructor", "toString", "__proto__", "hasOwnProperty", "valueOf")

_NOMS_HERITES_JS = """
import { readFileSync } from "node:fs";
import {
  Carriere, bornesDeformation, chomageComplementaires, dispenseAssietteMinimale,
  forfaitMicro, profilDeLAffiliation, profilSalaire,
} from "./moteur/js/carriere.js";
import { DonneesMacro } from "./moteur/js/macro.js";
import { Affiliations } from "./moteur/js/regimes.js";
const noms = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
const macro = new DonneesMacro(paquet);
const chomage = chomageComplementaires(paquet);
const affiliations = new Affiliations(paquet);
const lu = (calcul) => {
  try {
    const valeur = calcul();
    return ["valeur", typeof valeur === "function" ? "une fonction" : valeur ?? null];
  } catch (erreur) {
    return ["refus", erreur.constructor.name === "TypeError" ? erreur.message : ""];
  }
};
process.stdout.write(JSON.stringify(noms.map((nom) => ({
  profil: lu(() => profilSalaire(paquet, nom, 30, 2000)),
  bornes: lu(() => bornesDeformation(paquet, nom)),
  groupe: lu(() => profilDeLAffiliation(nom)),
  dispense: lu(() => dispenseAssietteMinimale(paquet, nom, "artisan", 2020)),
  nature: lu(() => chomage.nature(nom, 2000)),
  part: lu(() => chomage.partValidee(nom, 2000, nom)),
  solidarite: lu(() => chomage.tauxSolidarite(nom, 2000, true)),
  forfait: lu(() => forfaitMicro(macro, nom, 2020)),
  releve: lu(() => Carriere.depuisReleve({
    annee_naissance: 1960, sexe: "H", age_liquidation: 62, macro,
    releve: [{ annee: 2000, affiliation: "salarie_prive_non_cadre", revenu: 20000,
               trimestres: null, type_periode: "emploi" },
             { annee: 2001, affiliation: "salarie_prive_non_cadre", revenu: 20000,
               trimestres: null, type_periode: nom }],
  }).lignes.map((ligne) => [ligne.trimestres_valides, ligne.services_fonction_publique,
    ligne.services_plafond_trimestres_par_enfant, ligne.reputes_cotises_nature])),
  libelle: lu(() => affiliations.libelle(nom)),
  periodes: lu(() => affiliations.periodes(nom)),
  regimes: lu(() => affiliations.regimes(nom, 2000)),
}))));
"""


def _noms_herites_en_python(noms) -> list[dict]:
    """Ce que le Python rend sous chacun de ces noms, comme le lit le portage :
    une valeur, ou un refus — un ``ValueError`` ou un ``KeyError``, et jamais
    une ``TypeError``, qui serait une faute de programme."""
    from retraite_notionnelle.carriere import (
        Affiliations, Carriere, LigneRelevee, bornes_deformation, profil_de_l_affiliation)
    from retraite_notionnelle.donnees.chargement import (
        charger_chomage_complementaires, charger_cotisation_micro,
        charger_dispenses_assiette_minimale, dispense_assiette_minimale, forfait_micro)
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.macro import DonneesMacro

    macro = DonneesMacro(RACINE_DONNEES)
    chomage = charger_chomage_complementaires(RACINE_DONNEES)
    affiliations = Affiliations(RACINE_DONNEES)

    def lu(calcul):
        try:
            return ["valeur", calcul()]
        except (KeyError, ValueError):
            return ["refus", ""]

    def releve(nom):
        lignes = [LigneRelevee(2000, "salarie_prive_non_cadre", 20000.0),
                  LigneRelevee(2001, "salarie_prive_non_cadre", 20000.0, type_periode=nom)]
        return [[ligne.trimestres_valides, ligne.services_fonction_publique,
                 ligne.services_plafond_trimestres_par_enfant, ligne.reputes_cotises_nature]
                for ligne in Carriere.depuis_releve(1960, "H", lignes, 62, macro).lignes]

    return [{
        "profil": lu(lambda: carriere_python.profil_salaire(RACINE_DONNEES, nom, 30, 2000)),
        "bornes": lu(lambda: list(bornes_deformation(RACINE_DONNEES, nom))),
        "groupe": lu(lambda: profil_de_l_affiliation(nom)),
        "dispense": lu(lambda: dispense_assiette_minimale(
            charger_dispenses_assiette_minimale(RACINE_DONNEES), nom, "artisan", 2020)),
        "nature": lu(lambda: chomage.nature(nom, 2000)),
        "part": lu(lambda: chomage.part_validee(nom, 2000, nom)),
        "solidarite": lu(lambda: chomage.taux_solidarite(nom, 2000, True)),
        "forfait": lu(lambda: forfait_micro(charger_cotisation_micro(RACINE_DONNEES), nom, 2020)),
        "releve": lu(lambda: releve(nom)),
        "libelle": lu(lambda: affiliations.libelle(nom)),
        "periodes": lu(lambda: list(affiliations.periodes(nom))),
        "regimes": lu(lambda: list(affiliations.regimes(nom, 2000))),
    } for nom in noms]


def test_un_nom_herite_du_prototype_n_est_dans_aucune_table_du_portage():
    """Le portage lit ses tables dans des objets de JavaScript, qui héritent
    de leur prototype : ``constructor`` ou ``toString`` y sont des clés, que
    ``in`` et ``table[nom]`` trouvent ; le Python, qui lit des dictionnaires,
    ne les connaît pas. Sous un tel nom, le portage calculait un profil au lieu
    de le refuser, levait une ``TypeError`` sur une dispense, une part validée
    du chômage ou le forfait d'un micro-entrepreneur, donnait au chômage une
    nature qui est une fonction, et des trimestres NaN à l'année d'un relevé
    que le Python tient sans activité ; une affiliation de ce nom avait un
    libellé et des régimes. Aucune saisie n'y mène — la page ne laisse passer
    que les noms de ses listes, que ``contient`` vérifie —, mais le jumeau qui
    reste rend ce que rend le Python (action 161, étape 6)."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _NOMS_HERITES_JS, json.dumps(NOMS_HERITES)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    portage = json.loads(execution.stdout)
    python = json.loads(json.dumps(_noms_herites_en_python(NOMS_HERITES)))
    ecarts = [f"{nom}, {lecture} : python={python[rang][lecture]} portage={valeur}"
              for rang, nom in enumerate(NOMS_HERITES)
              for lecture, valeur in portage[rang].items()
              if valeur != python[rang][lecture]]
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts)
