"""Le témoin des valeurs : ce que le portage rend à une fonction Python, figé
sous son empreinte (action 161, étape 8d).

Les confrontations de ``tests/test_pont.py`` faisaient refaire au moteur
Python ce que le portage rend à travers le pont — une grille du coût, les
dates d'une grille, des cas servis. :func:`valeur_figee` confronte la valeur
au témoin, ``tests/temoins/valeurs.json``, qui porte, sous le nom du fichier
de tests et celui que le test lui donne, l'empreinte de la valeur mise en
données (:func:`en_donnees`), chaque flottant lu à douze chiffres
significatifs, comme le témoin des sorties (``outils_sorties``).
``scripts/construire_temoins.py --valeurs`` le refait en relançant, sous
``FIGER_VALEURS=1``, chaque fichier qui en fige une (:func:`fichiers_qui_figent`).
"""

from __future__ import annotations

import dataclasses
import enum
import functools
import json
import os
import tempfile
from pathlib import Path

from outils_sorties import _arrondie, _empreinte

RACINE_DES_TESTS = Path(__file__).resolve().parent

#: Le témoin des valeurs : sous ``<fichier de tests>::<nom>``, l'empreinte de
#: la valeur (:func:`empreinte_de_la_valeur`). Une variable d'environnement du
#: même nom le déplace, pour que ``construire_temoins.py`` le refasse à part.
TEMOIN_DES_VALEURS = Path(os.environ.get(
    "TEMOIN_DES_VALEURS", RACINE_DES_TESTS / "temoins" / "valeurs.json"))


def en_donnees(valeur):
    """La valeur en données JSON, sans rien perdre de ce qu'une confrontation
    comparait : une classe de données, le dictionnaire de ses champs sous le
    nom de sa classe ; une énumération, sa valeur ; un tuple, une liste ; un
    ensemble, la liste triée de ses éléments ; un dictionnaire aux clés qui ne
    sont pas toutes des chaînes, la liste de ses couples triés."""
    if dataclasses.is_dataclass(valeur) and not isinstance(valeur, type):
        return {"__classe__": type(valeur).__name__,
                **{champ.name: en_donnees(getattr(valeur, champ.name))
                   for champ in dataclasses.fields(valeur)}}
    if isinstance(valeur, enum.Enum):
        return en_donnees(valeur.value)
    if isinstance(valeur, dict):
        if all(isinstance(cle, str) for cle in valeur):
            return {cle: en_donnees(v) for cle, v in valeur.items()}
        return sorted(([en_donnees(cle), en_donnees(v)] for cle, v in valeur.items()),
                      key=lambda couple: json.dumps(couple, sort_keys=True))
    if isinstance(valeur, (set, frozenset)):
        return sorted((en_donnees(v) for v in valeur),
                      key=lambda v: json.dumps(v, sort_keys=True))
    if isinstance(valeur, (list, tuple)):
        return [en_donnees(v) for v in valeur]
    if valeur is None or isinstance(valeur, (bool, int, float, str)):
        return valeur
    raise TypeError(f"une valeur de type {type(valeur).__name__} ne se fige pas")


def empreinte_de_la_valeur(valeur) -> str:
    """L'empreinte de la valeur mise en données, chaque flottant lu à douze
    chiffres significatifs."""
    return _empreinte(_arrondie(en_donnees(valeur)))


@functools.cache
def valeurs_figees() -> dict[str, dict]:
    """Le témoin des valeurs, tel que le fichier le porte."""
    if not TEMOIN_DES_VALEURS.exists():
        return {}
    return json.loads(TEMOIN_DES_VALEURS.read_text(encoding="utf-8"))


def ecrire(figes: dict[str, dict]) -> str:
    """Le texte du témoin."""
    return json.dumps(figes, ensure_ascii=False, sort_keys=True, indent=1) + "\n"


def _figer(nom: str, empreinte: str) -> None:
    """Écrit une valeur au témoin, sous verrou, et le remplace d'un coup : les
    processus de la suite peuvent figer, et le lire, en même temps."""
    import fcntl  # POSIX seul : figer ne se fait que sous Linux ou macOS

    verrou = Path(tempfile.gettempdir()) / "temoin_des_valeurs.verrou"
    with open(verrou, "a", encoding="utf-8") as tenu:
        fcntl.flock(tenu, fcntl.LOCK_EX)
        figes = (json.loads(TEMOIN_DES_VALEURS.read_text(encoding="utf-8"))
                 if TEMOIN_DES_VALEURS.exists() else {})
        figes[nom] = {"valeur": empreinte}
        provisoire = TEMOIN_DES_VALEURS.with_suffix(f".{os.getpid()}.provisoire")
        provisoire.write_text(ecrire(figes), encoding="utf-8")
        os.replace(provisoire, TEMOIN_DES_VALEURS)
    valeurs_figees.cache_clear()


def _fichier_du_test() -> str:
    """Le fichier du test qui tourne, tel que pytest le nomme."""
    courant = os.environ.get("PYTEST_CURRENT_TEST", "")
    return Path(courant.partition("::")[0]).name or "hors_de_pytest"


def valeur_figee(nom: str, valeur):
    """La valeur, confrontée au témoin des valeurs sous
    ``<fichier du test>::<nom>`` : elle doit y être, sous l'empreinte de ce
    que le portage rend aujourd'hui. Elle tient la place du moteur Python qui
    la refaisait tant qu'il gardait ses jumeaux (action 161, étape 8d). Sous
    ``FIGER_VALEURS=1``, une valeur absente s'y ajoute, et une valeur qui a
    bougé s'y refait. Sous la garde des présomptions
    (``PRESOMPTIONS_DECALEES``, ``tests/conftest.py``), qui décale ce que le
    témoin a figé, il n'est ni lu ni écrit."""
    if os.environ.get("PRESOMPTIONS_DECALEES"):
        return valeur
    cle = f"{_fichier_du_test()}::{nom}"
    empreinte = empreinte_de_la_valeur(valeur)
    figee = valeurs_figees().get(cle)
    if figee is not None and figee["valeur"] == empreinte:
        return valeur
    if os.environ.get("FIGER_VALEURS") == "1":
        _figer(cle, empreinte)
        return valeur
    if figee is None:
        raise AssertionError(
            f"{cle} absente du témoin des valeurs : l'y ajouter par FIGER_VALEURS=1 "
            "python -m pytest <ce fichier>")
    raise AssertionError(
        f"{cle} n'est plus ce que le témoin des valeurs porte ; si le déplacement est "
        "voulu, le témoin se refait par python scripts/construire_temoins.py --valeurs")


def fichiers_qui_figent() -> list[str]:
    """Les fichiers de tests qui figent une valeur, nommés sous ``tests/``."""
    return sorted({chemin.partition("::")[0] for chemin in tests_qui_figent()})


def tests_qui_figent() -> list[str]:
    """Les tests qui figent une valeur, ``<fichier>::<test>`` sous ``tests/`` :
    ceux dont le corps appelle :func:`valeur_figee`, et que
    ``construire_temoins.py --valeurs`` relance, eux seuls."""
    import ast

    propres = {"outils_valeurs.py", "test_valeurs_figees.py"}
    trouves = []
    for chemin in sorted(RACINE_DES_TESTS.glob("test_*.py")):
        texte = chemin.read_text(encoding="utf-8")
        if chemin.name in propres or "valeur_figee(" not in texte:
            continue
        for noeud in ast.parse(texte).body:
            if (isinstance(noeud, ast.FunctionDef) and noeud.name.startswith("test_")
                    and any(isinstance(appel, ast.Call) and isinstance(appel.func, ast.Name)
                            and appel.func.id == "valeur_figee" for appel in ast.walk(noeud))):
                trouves.append(f"{chemin.name}::{noeud.name}")
    return trouves
