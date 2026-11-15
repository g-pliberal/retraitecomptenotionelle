"""Le témoin des sorties : ce que les scripts de comparaison du portage
(``tests/js/*.mjs``) écrivent de chaque entrée, figé sous son empreinte
(action 161, étape 8c).

Un script de comparaison lit un fichier JSON, une liste d'entrées — des
requêtes du formulaire, des chronologies —, et écrit sur la sortie standard la
liste de ce qu'il en tire, une sortie par entrée, chacune indépendante des
autres. Les confrontations la faisaient refaire au moteur Python ;
:func:`sortie_figee` la confronte au témoin, ``tests/temoins/sorties.json``,
qui porte pour chaque entrée son script, l'entrée elle-même et l'empreinte de
sa sortie (:func:`empreinte_de_la_sortie`). ``scripts/construire_temoins.py``
le refait en relançant chaque script sur ses entrées (:func:`refaire`).
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SCRIPTS = RACINE / "tests" / "js"

#: Le témoin des sorties : sous l'empreinte de chaque entrée
#: (:func:`empreinte_de_l_entree`), son script, l'entrée, et l'empreinte de ce
#: que le script en écrit.
TEMOIN_DES_SORTIES = RACINE / "tests" / "temoins" / "sorties.json"

#: Les chiffres significatifs d'un flottant que l'empreinte d'une sortie lit :
#: assez pour un millionième de centime, trop peu pour le dernier bit qu'une
#: autre libm que celle de Linux x86_64 déplace.
CHIFFRES = 12


def _empreinte(valeur) -> str:
    texte = json.dumps(valeur, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()[:16]


def empreinte_de_l_entree(script: str, entree) -> str:
    """L'empreinte d'une entrée donnée à un script : la clé du témoin."""
    return _empreinte([script, entree])


def _arrondie(valeur):
    if isinstance(valeur, float):
        return float(format(valeur, f".{CHIFFRES}g"))
    if isinstance(valeur, dict):
        return {cle: _arrondie(v) for cle, v in valeur.items()}
    if isinstance(valeur, list):
        return [_arrondie(v) for v in valeur]
    return valeur


def empreinte_de_la_sortie(sortie) -> str:
    """L'empreinte de ce qu'un script écrit d'une entrée, chaque flottant lu à
    :data:`CHIFFRES` chiffres significatifs."""
    return _empreinte(_arrondie(sortie))


def lancer(script: str, entrees: list) -> list:
    """Ce que ``node tests/js/<script>`` écrit des entrées, une sortie par
    entrée."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(entrees, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(["node", str(SCRIPTS / script), chemin], cwd=RACINE,
                                   capture_output=True, text=True, encoding="utf-8",
                                   check=False)
    finally:
        Path(chemin).unlink()
    if execution.returncode != 0:
        raise AssertionError(f"{script} : {execution.stderr[-2000:]}")
    sorties = json.loads(execution.stdout)
    if len(sorties) != len(entrees):
        raise AssertionError(f"{script} : {len(sorties)} sorties pour {len(entrees)} entrées")
    return sorties


@functools.cache
def sorties_figees() -> dict[str, dict]:
    """Le témoin des sorties, tel que le fichier le porte."""
    return json.loads(TEMOIN_DES_SORTIES.read_text(encoding="utf-8"))


def ecrire(figes: dict[str, dict]) -> str:
    """Le texte du témoin."""
    return json.dumps(figes, ensure_ascii=False, sort_keys=True, indent=1) + "\n"


def _figer(entrees: dict[str, dict]) -> None:
    """Ajoute des entrées au témoin, sous verrou, et le remplace d'un coup :
    les processus de la suite peuvent figer, et le lire, en même temps."""
    import fcntl  # POSIX seul : figer ne se fait que sous Linux ou macOS

    verrou = Path(tempfile.gettempdir()) / "temoin_des_sorties.verrou"
    with open(verrou, "a", encoding="utf-8") as tenu:
        fcntl.flock(tenu, fcntl.LOCK_EX)
        figes = json.loads(TEMOIN_DES_SORTIES.read_text(encoding="utf-8"))
        figes.update(entrees)
        provisoire = TEMOIN_DES_SORTIES.with_suffix(f".{os.getpid()}.provisoire")
        provisoire.write_text(ecrire(figes), encoding="utf-8")
        os.replace(provisoire, TEMOIN_DES_SORTIES)
    sorties_figees.cache_clear()


def sortie_figee(script: str, entrees: list) -> list:
    """Ce que ``node tests/js/<script>`` écrit des entrées, confronté au
    témoin des sorties : chaque entrée doit y être, sous l'empreinte de ce que
    le script en écrit aujourd'hui. Il tient la place du moteur Python qui
    refaisait chaque sortie tant qu'il gardait ses jumeaux (action 161,
    étape 8c). Sous ``FIGER_SORTIES=1``, une entrée absente s'y ajoute."""
    sorties = lancer(script, entrees)
    figes = sorties_figees()
    absentes, bougees = {}, []
    for rang, (entree, sortie) in enumerate(zip(entrees, sorties)):
        cle, empreinte = empreinte_de_l_entree(script, entree), empreinte_de_la_sortie(sortie)
        if cle not in figes:
            absentes[cle] = {"script": script, "entree": entree, "sortie": empreinte}
        elif figes[cle]["sortie"] != empreinte:
            bougees.append(f"entrée {rang} ({cle})")
    if absentes and os.environ.get("FIGER_SORTIES") == "1":
        _figer(absentes)
    elif absentes:
        raise AssertionError(
            f"{len(absentes)} entrée(s) de {script} absente(s) du témoin des sorties : les y "
            "ajouter par FIGER_SORTIES=1 python -m pytest <ce fichier>")
    if bougees:
        raise AssertionError(
            f"{script} n'écrit plus ce que le témoin des sorties porte ({len(bougees)} "
            f"entrée(s), dont {', '.join(bougees[:5])}) ; si le déplacement est voulu, le "
            "témoin se refait par python scripts/construire_temoins.py --sorties")
    return sorties


def refaire(figes: dict[str, dict]) -> dict[str, dict]:
    """Chaque entrée du témoin, son script relancé : l'empreinte de ce qu'il
    en écrit aujourd'hui."""
    par_script: dict[str, list[str]] = {}
    for cle, entree in figes.items():
        par_script.setdefault(entree["script"], []).append(cle)
    refaits = {}
    for script, cles in sorted(par_script.items()):
        sorties = lancer(script, [figes[cle]["entree"] for cle in cles])
        for cle, sortie in zip(cles, sorties):
            refaits[cle] = {**figes[cle], "sortie": empreinte_de_la_sortie(sortie)}
    return refaits
