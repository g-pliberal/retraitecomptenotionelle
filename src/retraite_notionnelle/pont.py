"""Le pont : ce que la fabrique fait calculer au moteur JavaScript, par node.

Le moteur d'une carrière n'aura qu'un exemplaire, en JavaScript, puisque le
site le fait tourner chez son lecteur ; la fabrique, le coût et les études le
feront tourner par node au lieu de son jumeau Python (note de décision 0003,
action 161, étape 5). Le pont doit tenir six conditions : les données des
contrats les mêmes dans un sens et dans l'autre ; les témoins et les agrégats
identiques à l'octet ; le budget de calcul tenu ; la mémoire des calculs
indexée sur le portage ; sans node, la fabrique qui s'arrête, sans repli sur
un moteur périmé ; aucune dépendance nouvelle.

Ce module lance ``pont.mjs`` et lui passe une demande. La fabrique y lit
d'abord la grille des carrières types de la table des agrégats, et les deux
départs que compare Droits non cotisés (``scripts/construire_donnees.py``) ;
puis, pour le bilan figé, la même grille, dont elle tire les écarts médians,
et les carrières d'exemple de « Pourquoi changer », des saisies. Le portage
calcule ses exponentielles comme la libm de Linux (``moteur/js/libm.js``) :
ce qu'il rend est, au bit près, ce que le moteur Python calcule, et
``tests/test_agregats.py``, ``tests/test_cout.py`` et
``tests/test_affirmations.py`` l'exigent des deux tables.

La grille du coût passe le pont autrement : sous les conventions de
projection du COR, la carrière d'un cas type se déforme en Python — l'entrée
tardive d'un fonctionnaire, la part des primes que le décrochage du
traitement porte (``castypes.primes_projetees``) —, et le portage, qui n'en
garde pas de copie, la reçoit en données (:func:`carriere_en_donnees`), sous
les paramètres du simulateur (:func:`parametres_en_donnees`), sur le paquet
des données du jour (:func:`paquet_des_donnees`).
"""

from __future__ import annotations

import dataclasses
import enum
import functools
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .config import RACINE_PROJET

#: Le programme que node fait tourner.
PROGRAMME = Path(__file__).with_name("pont.mjs")


class PontIndisponible(RuntimeError):
    """Node manque : ce que le pont calcule ne se calcule pas, et rien ne prend
    le relais."""


def _demander(demande: dict, paquet: bytes | None) -> dict:
    """La réponse du portage à une demande, calculée sur ``paquet`` — les
    octets d'un paquet de données —, ou sur ``moteur/donnees.json`` sans lui."""
    if shutil.which("node") is None:
        raise PontIndisponible(
            "node absent : la fabrique calcule par le portage JavaScript "
            "(retraite_notionnelle/pont.mjs), sans repli sur le moteur Python")
    entree = (b'{"paquet":' + (b"null" if paquet is None else paquet)
              + b',"demande":' + json.dumps(demande).encode("utf-8") + b"}")
    execution = subprocess.run(["node", str(PROGRAMME)], input=entree, cwd=RACINE_PROJET,
                               capture_output=True, check=False)
    if execution.returncode != 0:
        raise RuntimeError(f"{PROGRAMME.name} : "
                           + execution.stderr.decode("utf-8", "replace").strip())
    return json.loads(execution.stdout)


def _flottant(valeur) -> float:
    """Un nombre que le Python tient pour un flottant : node écrit 2.0 « 2 »,
    et un nombre non fini « null »."""
    return math.nan if valeur is None else float(valeur)


def _par_scenario(lus: dict) -> dict[str, float]:
    return {scenario: _flottant(nombre) for scenario, nombre in lus.items()}


def _aujourd_hui(lu: dict | None) -> dict | None:
    if lu is None:
        return None
    return {
        "pension_annuelle": _flottant(lu["pension_annuelle"]),
        "pensions_totales": _par_scenario(lu["pensions_totales"]),
        "rente_capitalisee_volontaire": _flottant(lu["rente_capitalisee_volontaire"]),
    }


def carrieres(cas: list[dict], scenarios, paquet: bytes | None = None,
              ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque carrière d'un seul statut, ``{"cle", "options"}`` aux options de
    ``carriere_simple``, simulée par le portage sous les réglages de
    référence : sous sa clé, l'année de son départ et celle de chaque
    scénario, l'écart de chacun au système actuel, pilier capitalisé compris
    (``variation_totale``), la pension du système actuel et la durée qu'il
    requiert ; la pension de chaque scénario, pilier capitalisé compris
    (``pension_totale``), et la rente des points volontaires
    (``rente_capitalisee_volontaire``) ; et, pour qui est déjà parti, ce que
    le système actuel et chaque scénario lui servent aujourd'hui
    (``Comparaison.aujourd_hui``), sinon ``None``. Puis, sous leur clé, les
    motifs des carrières que le portage refuse."""
    reponse = _demander({"carrieres": {"cas": cas, "scenarios": list(scenarios)}}, paquet)
    resultats = {
        cle: {
            "annee_liquidation": lu["annee_liquidation"],
            "annees_liquidation": dict(lu["annees_liquidation"]),
            "variations": _par_scenario(lu["variations"]),
            "pension_annuelle": _flottant(lu["pension_annuelle"]),
            "trimestres_requis": lu["trimestres_requis"],
            "pensions_totales": _par_scenario(lu["pensions_totales"]),
            "rentes_volontaires": _par_scenario(lu["rentes_volontaires"]),
            "aujourd_hui": _aujourd_hui(lu["aujourd_hui"]),
        }
        for cle, lu in reponse["resultats"].items()
    }
    return resultats, reponse["echecs"]


def _en_donnees(valeur):
    """Une valeur telle que JSON l'écrit et que le portage la lit : un membre
    d'énumération par sa valeur, un dataclass par ses champs, une suite en
    liste."""
    if isinstance(valeur, enum.Enum):
        return valeur.value
    if dataclasses.is_dataclass(valeur):
        return {champ.name: _en_donnees(getattr(valeur, champ.name))
                for champ in dataclasses.fields(valeur)}
    if isinstance(valeur, (list, tuple)):
        return [_en_donnees(element) for element in valeur]
    if isinstance(valeur, dict):
        return {cle: _en_donnees(element) for cle, element in valeur.items()}
    return valeur


def parametres_en_donnees(parametres) -> dict:
    """Les paramètres d'un simulateur tels que le portage les lit, sous les
    mêmes noms (``PARAMETRES_DEFAUT`` de ``moteur/js/config.js``) : tous, sauf
    la racine des données, dont le paquet tient lieu."""
    return {champ.name: _en_donnees(getattr(parametres, champ.name))
            for champ in dataclasses.fields(parametres) if champ.name != "racine_donnees"}


def carriere_en_donnees(carriere) -> dict:
    """La carrière telle que le portage la relit (``carriereDesDonnees`` de
    ``pont.mjs``) : chacun de ses champs, chacune de ses lignes entière, et la
    chronologie dont elle est la vue, telle que le Python l'a complétée. Ce que
    le Python a fait de la carrière passe ainsi tel quel, et le portage n'en
    garde pas de copie."""
    donnees = {}
    for champ in dataclasses.fields(carriere):
        valeur = getattr(carriere, champ.name)
        if champ.name == "dates_entree":
            valeur = {statut: [date.annee, date.mois] for statut, date in valeur.items()}
        donnees[champ.name] = _en_donnees(valeur)
    return donnees


#: Le programme qui bâtit le paquet des données du jour, dans un processus à lui.
_BATIR_LE_PAQUET = """\
import importlib.util, sys
spec = importlib.util.spec_from_file_location("construire_donnees", sys.argv[1])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
sys.stdout.buffer.write(module.construire(b"{}", b"{}"))
"""


@functools.cache
def paquet_des_donnees() -> bytes:
    """Le paquet des données du jour, tel que la fabrique l'écrira, sans le
    bilan ni les agrégats, que la simulation d'une carrière ne lit pas : celui
    sur lequel le coût fait simuler sa grille.

    Il ne se lit pas dans ``moteur/donnees.json`` : une retouche des données
    n'y entre qu'à la fabrique suivante, et la fabrique, qui l'écrit pendant
    que d'autres étapes calculent le coût, le leur donnerait à demi écrit. Il
    se bâtit donc depuis ``data/``, une fois par processus, par la fabrique
    elle-même (``scripts/construire_donnees.py``), dans un processus à elle,
    comme node fait tourner le moteur JavaScript dans le sien : ce qu'elle lit
    pour le site seul — les crédits des ministères, le manifeste des sources,
    qu'aucun calcul ne lit — n'entre ni dans les mémoires des chargeurs de ce
    processus-ci, ni dans le relevé de ce que lisent les calculs gardés
    (``memoire.HORS_DU_MODELE``)."""
    environnement = {**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, (
        str(RACINE_PROJET / "src"), os.environ.get("PYTHONPATH"))))}
    execution = subprocess.run(
        [sys.executable, "-c", _BATIR_LE_PAQUET,
         str(RACINE_PROJET / "scripts" / "construire_donnees.py")],
        cwd=RACINE_PROJET, env=environnement, capture_output=True, check=False)
    if execution.returncode != 0:
        raise RuntimeError("le paquet des données du jour ne se bâtit pas : "
                           + execution.stderr.decode("utf-8", "replace").strip()[-2000:])
    return execution.stdout


def _serie(paires) -> dict[int, float]:
    return {annee: _flottant(nombre) for annee, nombre in paires}


def _volet_du_cout(lu: dict) -> dict:
    garantie, pilier = lu["garantie"], lu["pilier"]
    return {
        "annee_liquidation": lu["annee_liquidation"],
        "revenus": _serie(lu["revenus"]),
        "garantie": {
            "annee_ouverture": garantie["annee_ouverture"],
            **{champ: _flottant(garantie[champ])
               for champ in ("pension_contributive", "ressources", "rente_capitalisee")},
        },
        "cotisations": _serie(lu["cotisations"]),
        "pilier": None if pilier is None else {
            "annees": {annee: tuple(_flottant(nombre) for nombre in flux)
                       for annee, *flux in pilier["annees"]},
            **{champ: _flottant(pilier[champ])
               for champ in ("capital", "diviseur", "rente_annuelle")},
        },
    }


def grille_du_cout(cas: list[dict], scenarios, parametres, paquet: bytes | None = None,
                   ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque case de la grille du coût, ``{"cle", "carriere",
    "propositions"}`` — sa carrière, et celles, nommées, sur lesquelles le coût
    calcule la proposition seule —, simulée par le portage sous
    ``parametres``, ceux de la projection : sous sa clé, ce que le coût en lit,
    tel que ``cout._simulations_en_python`` le tire du moteur Python, son
    jumeau. Puis, sous leur clé, les motifs des cases que le portage refuse."""
    reponse = _demander({"grille_du_cout": {
        "parametres": parametres_en_donnees(parametres),
        "scenarios": list(scenarios),
        "cas": [{"cle": un["cle"], "carriere": carriere_en_donnees(un["carriere"]),
                 "propositions": {nom: carriere_en_donnees(carriere)
                                  for nom, carriere in un["propositions"].items()}}
                for un in cas],
    }}, paquet)
    resultats = {
        cle: {
            "pensions": _par_scenario(lu["pensions"]),
            "depart_reporte": lu["depart_reporte"],
            "liberal": _volet_du_cout(lu["liberal"]),
            "coefficient_liberal": _flottant(lu["coefficient_liberal"]),
            "prelevement": _serie(lu["prelevement"]),
            "pension_actuelle": _flottant(lu["pension_actuelle"]),
            "pensions_par_regime": [(regime, _flottant(montant))
                                    for regime, montant in lu["pensions_par_regime"]],
            "population": lu["population"],
            "propositions": {nom: _volet_du_cout(volet)
                             for nom, volet in lu["propositions"].items()},
        }
        for cle, lu in reponse["resultats"].items()
    }
    return resultats, reponse["echecs"]


def saisies(cas: list[dict], scenarios, paquet: bytes | None = None,
            ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque saisie, ``{"cle", "saisie"}`` aux champs de ``Saisie``, simulée
    par le portage comme le site la simule (``Contexte.simuler``) : sous sa
    clé, la fiche de paie de l'année de référence sous le droit en vigueur
    (``remuneration.reference.droit_en_vigueur``), ou ``None`` sans fiche, le
    passage aux euros constants, la pension du système actuel et celle de
    chaque scénario. Puis, sous leur clé, les motifs des saisies que le
    portage refuse."""
    reponse = _demander({"saisies": {"cas": cas, "scenarios": list(scenarios)}}, paquet)
    resultats = {}
    for cle, lu in reponse["resultats"].items():
        fiche = lu["fiche"]
        resultats[cle] = {
            "fiche": None if fiche is None else {
                "annee": fiche["annee"],
                **{champ: _flottant(fiche[champ])
                   for champ in ("brut", "net", "retraite_totale", "retraite_employeur")},
            },
            "coefficient_euros_constants": _flottant(lu["coefficient_euros_constants"]),
            "pension_annuelle": _flottant(lu["pension_annuelle"]),
            "pensions": _par_scenario(lu["pensions"]),
        }
    return resultats, reponse["echecs"]
