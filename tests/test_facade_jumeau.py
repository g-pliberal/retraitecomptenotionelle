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
import enum
import json
import shutil

import pytest

from retraite_notionnelle import pont
from retraite_notionnelle import simulateur as simulateur_python
from retraite_notionnelle.carriere import Carriere as CarrierePython
from retraite_notionnelle.carriere import LigneRelevee, Metier
from retraite_notionnelle.config import RACINE_PROJET

import facade
from outils_pont import TOLERANCE_DU_MOTEUR_PYTHON, ecarts_d_ecriture

TEMOINS = RACINE_PROJET / "tests" / "temoins" / "simulations.json"

#: Les types du résultat du scénario 1 que peu de carrières portent : la
#: confrontation entière doit avoir relu chacun au moins une fois.
TYPES_RARES = {"DepartServi", "DemandeExaminee", "ProgressiveServie", "Cumul",
               "DroitsApresDepart", "NouvellePension", "MinimumEcrete", "PetitePension",
               "ChefDExploitation", "ExploitantAgricole", "EligibleAgricole",
               "AvantageApplique", "PensionRegime"}


def _a_plat(valeur, types: set[str]):
    """Un résultat en données, pour le comparer : un dataclass par ses champs
    et son type, une carrière comme le pont l'écrit, un membre d'énumération
    par sa valeur ; chaque nombre en flottant — le jumeau rend « 0 », entier,
    le zéro d'une somme vide là où le type dit un flottant, que la lecture
    stricte rend « 0.0 ». ``types`` reçoit le nom de chaque type rencontré."""
    if isinstance(valeur, CarrierePython):
        return pont.carriere_en_donnees(valeur)
    if dataclasses.is_dataclass(valeur) and not isinstance(valeur, type):
        types.add(type(valeur).__name__)
        return {"type": type(valeur).__name__,
                **{champ.name: _a_plat(getattr(valeur, champ.name), types)
                   for champ in dataclasses.fields(valeur)}}
    if isinstance(valeur, enum.Enum):
        return valeur.value
    if isinstance(valeur, (list, tuple)):
        return [_a_plat(element, types) for element in valeur]
    if isinstance(valeur, dict):
        return {str(cle): _a_plat(element, types) for cle, element in valeur.items()}
    if type(valeur) is int:
        return float(valeur)
    return valeur


def _ecarts_du_scenario_1(pas: int) -> tuple[list[str], set[str], int]:
    """Un témoin sur ``pas`` : sa carrière, que le portage bâtit de sa requête,
    liquidée par la façade et par le moteur Python, sous ses paramètres. Les
    écarts, les types relus, et le nombre de carrières."""
    temoins = json.loads(TEMOINS.read_text(encoding="utf-8"))
    carrieres, refus = pont.carrieres_des_saisies(
        [{"cle": nom, "requete": temoins[nom]["requete"]} for nom in sorted(temoins)[::pas]])
    assert refus == {}
    ecarts, types = [], set()
    for nom, (parametres, carriere) in carrieres.items():
        servi = facade.Simulateur(parametres).scenario_actuel.calculer(carriere)
        refait = simulateur_python.Simulateur(parametres).scenario_actuel.calculer(carriere)
        assert type(servi) is type(refait)
        ecarts += ecarts_d_ecriture(_a_plat(refait, set()), _a_plat(servi, types), (nom,),
                                    tolerance=TOLERANCE_DU_MOTEUR_PYTHON)
    return ecarts, types, len(carrieres)


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


#: Un salarié né en 1965, entré à 23 ans, parti à 64 ans.
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
