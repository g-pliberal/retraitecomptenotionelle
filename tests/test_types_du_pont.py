"""Les types que le pont échange, hors des fichiers de règles (action 161,
étape 1 du retrait des règles Python).

Le pont relit ce que calcule le moteur JavaScript sous des types Python. Ils
logeaient dans les fichiers de règles, que le retrait supprimera : ils ont
désormais leur module, ``types_du_pont``, qui ne charge aucun fichier de
règles, et les fichiers de règles les réimportent le temps du retrait.
``Carriere`` y loge nue, ses champs et ses lectures du calendrier : ses
règles restent dans ``carriere.py``, sur une classe qui en hérite, le temps
du retrait (étape 1 bis).
"""

import importlib
import subprocess
import sys

import pytest

PAQUET = "retraite_notionnelle"

#: Chaque type que le pont relit, ou qu'un type qu'il relit porte dans ses
#: champs, sous le fichier de règles qui le définissait : il y reste
#: accessible, et c'est le même objet.
TYPES = {
    "carriere": ["AnneeCarriere"],
    "droit.commun": ["PensionRegime", "AvantageApplique"],
    "droit.completer": ["MinimumEcrete", "PetitePension", "ChefDExploitation",
                        "ExploitantAgricole", "MajorationProportionnelle"],
    "droit.cumul": ["Cumul", "TrancheDeCumul", "PensionEnCumul"],
    "droit.departs": ["DemandeExaminee"],
    "droit.foyer": ["Foyer"],
    "droit.liquidation": ["Demande", "Mesure"],
    "droit.liquider": ["EligiblePlafondEnfants"],
    "droit.reversion": ["Reversion", "ReversionRegime"],
    "droit.seconde": ["DroitsApresDepart", "PeriodeDeDroits", "NouvellePension",
                      "PensionDeRegimeNouveau"],
    "echeancier": ["Evenement"],
    "journal": ["Entree", "Journal"],
    "moteur.age_reference": ["EcartAge"],
    "moteur.capitalisation": ["Capitalisation", "AnneeCapitalisation"],
    "moteur.compte": ["CompteNotionnel", "CotisationAnnuelle"],
    "moteur.conversion": ["CoefficientConversion"],
    "moteur.fusion": ["RegimeFusionne"],
    "moteur.indexation": ["TauxIndexation"],
    "revalorisation": ["ActuelAujourdhui", "RegimeServi", "MajorationExceptionnelle",
                       "PensionAujourdhui", "Revalorisee", "RelevementAgricole",
                       "RevisionAgricole"],
    "scenarios.actuel": ["ResultatActuel", "DepartServi", "ProgressiveServie"],
    "scenarios.notionnel": ["GarantieVieillesse", "ResultatNotionnel", "DroitsAcquis"],
    "simulateur": ["Comparaison", "ContributionEmployeur"],
}

#: Les fichiers de règles que le retrait supprimera (note de l'inventaire,
#: « Le périmètre »).
REGLES = ("droit", "moteur", "scenarios", "carriere", "revalorisation", "simulateur",
          "echeancier", "pilote", "journal")


@pytest.mark.parametrize("module, nom", [(module, nom) for module, noms in TYPES.items()
                                         for nom in noms])
def test_chaque_type_du_pont_loge_hors_des_regles(module, nom):
    type_ = getattr(importlib.import_module(f"{PAQUET}.{module}"), nom)
    assert type_.__module__.startswith(f"{PAQUET}.types_du_pont."), type_.__module__


def test_les_types_du_pont_ne_chargent_aucun_fichier_de_regles():
    programme = (
        "import sys, importlib, pkgutil\n"
        f"import {PAQUET}.types_du_pont as t\n"
        "for m in pkgutil.iter_modules(t.__path__):\n"
        f"    importlib.import_module('{PAQUET}.types_du_pont.' + m.name)\n"
        f"print('\\n'.join(n for n in sys.modules if n.startswith('{PAQUET}.')))\n")
    charges = subprocess.run([sys.executable, "-c", programme], capture_output=True,
                             text=True, check=True).stdout.split()
    regles = [nom for nom in charges
              if nom.removeprefix(f"{PAQUET}.").split(".")[0] in REGLES]
    assert regles == []


def test_le_pont_relit_le_journal_sous_les_types_du_pont():
    from retraite_notionnelle.pont import CONTENUS_DU_JOURNAL

    for declare in CONTENUS_DU_JOURNAL.values():
        if declare is not None:
            assert declare[0].startswith("types_du_pont."), declare


#: Ce que la carrière nue porte, hors de ses champs : des lectures de ses
#: lignes, du calendrier et de sa chronologie, aucune règle du droit.
LECTURES_DE_LA_CARRIERE = {
    "__post_init__", "premiere_annee", "derniere_annee", "date_naissance",
    "jour_de_naissance", "origine_des_ages", "date_de_l_age", "mois_de_l_anniversaire",
    "age_au", "generation", "date_liquidation", "annee_liquidation", "mois_liquidation",
    "fraction_annee_liquidation", "annees_cotisees", "_lignes_par_annee", "lignes_de",
    "ligne", "affiliations_utilisees",
}


def test_la_carriere_nue_loge_hors_des_regles_et_ne_porte_aucune_regle():
    carriere = importlib.import_module(f"{PAQUET}.carriere")
    from retraite_notionnelle.types_du_pont import carriere as nue

    assert issubclass(carriere.Carriere, nue.Carriere)
    assert carriere.Carriere is not nue.Carriere
    propres = {nom for nom in vars(nue.Carriere)
               if not nom.startswith("__") or nom == "__post_init__"}
    champs = set(nue.Carriere.__dataclass_fields__)
    assert propres - champs - {"__dataclass_fields__", "__dataclass_params__",
                               "__match_args__"} == LECTURES_DE_LA_CARRIERE


def test_le_pont_relit_la_carriere_sous_le_type_nu():
    import typing

    from retraite_notionnelle.types_du_pont import carriere as nue
    from retraite_notionnelle.types_du_pont.comparaison import Comparaison

    indices = typing.get_type_hints(Comparaison)
    assert indices["carriere"] is nue.Carriere
