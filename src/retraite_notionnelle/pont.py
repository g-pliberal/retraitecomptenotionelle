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
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
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
