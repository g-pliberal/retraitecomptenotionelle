"""Ce qu'un script exécute du moteur Python (action 161, le retrait).

    python scripts/sonde_moteur_python.py scripts/recours_aspa.py [ses arguments…]

Le moteur Python d'une carrière se retire par le haut : avant de couper ses
règles, chaque script et chaque module qui bâtit encore un ``Simulateur``
doit n'en lire que les données, ou demander le calcul au pont. La lecture
seule des imports ne le dit pas : un module qui garde deux chemins, l'un au
portage, l'autre « en Python sinon », importe les règles sans forcément les
exécuter. La sonde lance le script tel quel (``runpy``), sous
``sys.monitoring``, et relève chaque fonction des fichiers de règles qui
s'exécute — ``droit/``, ``moteur/``, ``scenarios/``, ``echeancier.py``,
``journal.py``, ``pilote.py``, ``carriere.py``, ``revalorisation.py``,
``simulateur.py`` —, hors du code de leurs modules et de leurs classes, de ce qui s'exécute
pendant qu'on les importe, et hors des chargeurs de
données du simulateur (:data:`DONNEES_DU_SIMULATEUR`), qui restent.

Elle imprime ces fonctions, une par ligne, ou « aucune règle du moteur
Python » ; ``--json`` les écrit en liste. Chaque fonction ne se relève
qu'une fois (``sys.monitoring.DISABLE``) : la sonde ne ralentit presque pas
le script.
"""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path
from typing import Callable

PAQUET = Path(__file__).resolve().parents[1] / "src" / "retraite_notionnelle"

#: Les fichiers de règles du moteur Python, et ceux qui tiennent ses entrées
#: (``tests/test_fichiers_sur_le_moteur_python.py``, ``MOTEUR_PYTHON``), avec
#: ``revalorisation.py``, jumeau de la revalorisation des pensions servies.
DOSSIERS = ("droit", "moteur", "scenarios")
FICHIERS = ("echeancier.py", "journal.py", "pilote.py", "carriere.py",
            "revalorisation.py", "simulateur.py")

#: Ce que le simulateur Python fait sans règle : se bâtir, charger ses
#: données et se refaire sous les conventions de projection. Ses autres
#: méthodes calculent.
DONNEES_DU_SIMULATEUR = frozenset({
    "Simulateur.__init__", "Simulateur.macro", "Simulateur.mortalite",
    "Simulateur.courbe_taux", "Simulateur.courbe_taux_pilier", "Simulateur.catalogue",
    "Simulateur.effectifs", "Simulateur.cotisants", "Simulateur.distribution",
    "Simulateur.distributions_par_sexe", "Simulateur.caracteristiques",
    "Simulateur.patrimoine", "Simulateur.vie_en_couple", "Simulateur.financement_regimes",
    "Simulateur.affiliations", "Simulateur.revalorisations",
    "Simulateur.pour_la_projection"})

_OUTIL = 4  # sys.monitoring.PROFILER_ID est 2, DEBUGGER_ID 0 ; 4 est libre.


def est_une_regle(fichier: str, nom: str) -> str | None:
    """Le nom qualifié de la fonction, relatif au paquet, si elle est une
    règle du moteur Python ; ``None`` sinon."""
    try:
        relatif = Path(fichier).resolve().relative_to(PAQUET)
    except ValueError:
        return None
    if nom == "<module>":
        return None
    if not (relatif.parts[0] in DOSSIERS or str(relatif) in FICHIERS):
        return None
    if relatif.name == "simulateur.py" and nom in DONNEES_DU_SIMULATEUR:
        return None
    module = ".".join(relatif.with_suffix("").parts)
    return f"{module}.{nom}"


_CO_OPTIMIZED = 0x0001


def _a_l_import(cadre) -> bool:
    """Si ce cadre s'exécute sous le code d'un module du paquet, c'est-à-dire
    pendant qu'on l'importe : une constante bâtie par une fonction n'est pas
    un calcul du script."""
    while cadre is not None:
        if cadre.f_code.co_name == "<module>" and Path(
                cadre.f_code.co_filename).resolve().is_relative_to(PAQUET):
            return True
        cadre = cadre.f_back
    return False


def sonder(fonction: Callable[[], object]) -> list[str]:
    """Les règles du moteur Python que ``fonction()`` exécute, triées."""
    monitoring = getattr(sys, "monitoring", None)
    if monitoring is None:  # Python 3.11, celui de GitHub
        return _sonder_par_profil(fonction)
    relevees: set[str] = set()

    def au_debut(code, _decalage):
        if not code.co_flags & _CO_OPTIMIZED:  # le corps d'une classe
            return monitoring.DISABLE
        regle = est_une_regle(code.co_filename, code.co_qualname)
        if regle is None:
            return monitoring.DISABLE
        if _a_l_import(sys._getframe(1)):
            return None  # relevée plus tard, si elle s'exécute hors d'un import
        relevees.add(regle)
        return monitoring.DISABLE

    monitoring.use_tool_id(_OUTIL, "sonde_moteur_python")
    try:
        monitoring.register_callback(_OUTIL, monitoring.events.PY_START, au_debut)
        monitoring.set_events(_OUTIL, monitoring.events.PY_START)
        try:
            fonction()
        finally:
            monitoring.set_events(_OUTIL, 0)
            monitoring.register_callback(_OUTIL, monitoring.events.PY_START, None)
    finally:
        monitoring.free_tool_id(_OUTIL)
    return sorted(relevees)


def _sonder_par_profil(fonction: Callable[[], object]) -> list[str]:
    """La même sonde sous ``sys.setprofile``, sans ``sys.monitoring`` : plus
    lente, chaque appel passant par elle."""
    relevees: set[str] = set()
    ecartes: set[object] = set()

    def au_debut(cadre, evenement, _argument):
        if evenement != "call":
            return
        code = cadre.f_code
        if code in ecartes:
            return
        nom = getattr(code, "co_qualname", code.co_name)
        if not code.co_flags & _CO_OPTIMIZED:
            ecartes.add(code)
            return
        regle = est_une_regle(code.co_filename, nom)
        if regle is None:
            ecartes.add(code)
            return
        if _a_l_import(cadre.f_back):
            return
        relevees.add(regle)
        ecartes.add(code)

    precedent = sys.getprofile()
    sys.setprofile(au_debut)
    try:
        fonction()
    finally:
        sys.setprofile(precedent)
    return sorted(relevees)


def main(arguments: list[str]) -> int:
    en_json = "--json" in arguments[:1]
    if en_json:
        arguments = arguments[1:]
    if not arguments:
        print(__doc__)
        return 2
    script, *reste = arguments
    sys.argv = [script, *reste]
    sys.path.insert(0, str(Path(script).resolve().parent))

    def lancer():
        try:
            runpy.run_path(script, run_name="__main__")
        except SystemExit as sortie:
            if sortie.code not in (None, 0):
                raise

    regles = sonder(lancer)
    if en_json:
        print(json.dumps(regles, ensure_ascii=False))
    elif regles:
        print(f"{len(regles)} règle(s) du moteur Python exécutée(s) :")
        for regle in regles:
            print(f"  {regle}")
    else:
        print("aucune règle du moteur Python")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
