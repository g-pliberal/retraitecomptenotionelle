"""Les types que le pont échange, sous ``types_du_pont`` (action 161).

Le pont relit ce que calcule le moteur JavaScript sous des types Python. Ils
logeaient dans les fichiers de règles Python, que le retrait a supprimés :
ils ont leur module, ``types_du_pont``, qui ne charge aucun fichier de
règles. ``Carriere`` y loge nue, ses champs et ses lectures du calendrier.
"""

import importlib
import subprocess
import sys

import pytest

PAQUET = "retraite_notionnelle"

#: Chaque type que le pont relit, ou qu'un type qu'il relit porte dans ses
#: champs — ceux que rendent les règles que la façade sert compris —, sous son
#: module de ``types_du_pont``.
TYPES = {
    "carriere": ["AnneeCarriere", "LigneRelevee", "Metier"],
    "comparaison": ["Comparaison", "ContributionEmployeur"],
    "droit": ["PensionRegime", "AvantageApplique", "MinimumEcrete", "PetitePension",
              "ChefDExploitation", "ExploitantAgricole", "MajorationProportionnelle",
              "PensionMajoree", "MajorationEnfants", "TrimestresEnfant", "Cumul",
              "TrancheDeCumul", "PensionEnCumul", "DureesDesCultes", "DemandeExaminee", "Depart",
              "Foyer", "Demande", "Mesure", "PlancherDeLaSubstitution", "Radiation", "Recul",
              "EligiblePlafondEnfants", "EligibleMinimum", "PrestationRafp",
              "DepartParentTroisEnfants", "Progressive", "RevenuDesPoints", "Reversion",
              "ReversionRegime", "DroitsApresDepart", "PeriodeDeDroits", "NouvellePension",
              "PensionDeRegimeNouveau", "ConversionPoint", "DerogationActive",
              "TrimestresAccordes", "EligibleAgricole"],
    "journal": ["Evenement", "Entree", "Journal"],
    "moteur": ["EcartAge", "Capitalisation", "AnneeCapitalisation", "CompteNotionnel",
               "CotisationAnnuelle", "CoefficientConversion", "RegimeFusionne",
               "TauxIndexation"],
    "resultats": ["ResultatActuel", "DepartServi", "ProgressiveServie", "GarantieVieillesse",
                  "ResultatNotionnel", "DroitsAcquis"],
    "revalorisation": ["ActuelAujourdhui", "RegimeServi", "MajorationExceptionnelle",
                       "PensionAujourdhui", "Revalorisee", "RelevementAgricole",
                       "RevisionAgricole"],
}

#: Les fichiers de règles que le retrait a supprimés (note de l'inventaire,
#: « Le périmètre »).
REGLES = ("droit", "moteur", "scenarios", "carriere", "revalorisation", "simulateur",
          "echeancier", "pilote", "journal")


@pytest.mark.parametrize("module, nom", [(module, nom) for module, noms in TYPES.items()
                                         for nom in noms])
def test_chaque_type_du_pont_loge_sous_types_du_pont(module, nom):
    type_ = getattr(importlib.import_module(f"{PAQUET}.types_du_pont.{module}"), nom)
    assert type_.__module__ == f"{PAQUET}.types_du_pont.{module}", type_.__module__


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


def test_la_carriere_nue_ne_porte_aucune_regle():
    from retraite_notionnelle.types_du_pont import carriere as nue

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
