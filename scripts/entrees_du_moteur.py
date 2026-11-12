#!/usr/bin/env python3
"""Ce qui entre dans le moteur Python d'une carrière quand un script tourne.

    python scripts/entrees_du_moteur.py                    # chaque étape de la fabrique
    python scripts/entrees_du_moteur.py scripts/x.py --a   # un script, et ses arguments

Le problème qu'il traite
------------------------

Le moteur d'une carrière n'aura qu'un exemplaire, en JavaScript ; son jumeau
Python part quand plus rien n'y entre (action 161). Les imports ne le disent
pas : ``Simulateur`` charge aussi les données, que la fabrique lit sans
simuler, et un script entre dans le moteur par un module qui reste, les cas
types par exemple, sans en nommer une fonction. Ce script le mesure en
faisant tourner : il lance un script du dépôt sous une sonde
(``sys.monitoring``, ou ``sys.settrace`` avant Python 3.12) et relève chaque
appel qui entre dans le moteur du dehors — aucune fonction du moteur n'est
alors en cours.

Ce qu'il compte
---------------

Une entrée est l'appel, du dehors, d'une règle du moteur : toute fonction
d'un fichier qui ne porte que des règles (:data:`REGLES`), et, dans les
fichiers qui portent aussi des chargeurs et des types (note de décision
0006), les portes par lesquelles une carrière se bâtit ou se liquide
(:data:`PORTES`). Elle se range sous le fichier du dépôt qui appelle.

Ce qu'il ne voit pas
--------------------

Une règle d'un fichier mêlé qui n'est pas une porte, appelée directement
(``remuneration.py``, ``revalorisation.py``, ``chronologie.py``) : elle
s'ajoute à :data:`PORTES` quand un script s'en sert. Ce qu'un script fait
calculer à un autre processus. Ce que fait un calcul que la mémoire des
calculs garde (``memoire.memoriser`` : le coût, ses variantes, le coût des
avantages) : déjà fait, il ne se refait pas, et le relevé changerait avec
l'état de la mémoire ; le coût date, bâtit et simule sa grille au portage, ce
que ``tests/test_pont.py`` tient par ses propres tests.

``tests/test_entrees_du_moteur.py`` tient la liste de la fabrique, qui ne
fait que décroître.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
PAQUET = RACINE / "src" / "retraite_notionnelle"

#: Les fichiers du moteur d'une carrière qui ne portent que des règles, sous
#: ``src/retraite_notionnelle/`` : un dossier, ou un fichier.
REGLES = ("droit/", "moteur/", "scenarios/notionnel.py", "echeancier.py", "pilote.py",
          "journal.py")

#: Les fichiers du moteur qui mêlent des règles à des chargeurs et à des types
#: que le pont échange, et les portes de chacun : ce par quoi une carrière se
#: bâtit, se liquide, se simule ; et les règles que les sondes de la prose y
#: appelaient directement, le 12 novembre 2026 — le salaire moyen d'une
#: année, la fiche de paie d'une simulation, la pension d'aujourd'hui, le
#: partage de la restitution, qui part avec le moteur (note de décision 0007).
PORTES = {
    "simulateur.py": ("Simulateur.simuler", "Simulateur.carriere_simple",
                      "Simulateur.carriere_parcours", "Simulateur.carriere_releve",
                      "Simulateur.carriere_proposition"),
    "scenarios/actuel.py": ("ScenarioActuel.calculer",),
    "carriere.py": ("Carriere.depuis_releve", "Carriere.depuis_profil",
                    "Carriere.depuis_parcours", "Carriere.depuis_chronologie",
                    "salaire_moyen_annuel"),
    "chronologie.py": (),
    "remuneration.py": ("RemunerationActif.reference",
                        "RemunerationActif.indemnite_csg_mensuelle", "AnneeComparee.gain_net",
                        "FicheDePaie.retraite_salarie", "FicheDePaie.retraite_employeur"),
    "revalorisation.py": ("ActuelAujourdhui.pension_annuelle",),
    "restitution.py": ("Restitution.part_du_poste", "Restitution.annuelle"),
}

#: Le fichier et la fonction sous lesquels tourne un calcul que la mémoire des
#: calculs garde : ce qui s'y appelle ne se relève pas.
MEMOIRE = (str(PAQUET / "memoire.py"), "memoriser")

#: La variable d'environnement qui fait relever par ``sys.settrace`` là où
#: ``sys.monitoring`` existe : la voie de Python 3.11, que GitHub emprunte.
PAR_TRACE = "ENTREES_PAR_TRACE"

#: Ce qui fait tourner les mesures de la prose dans ce processus, que la sonde
#: voit, et non dans ceux qu'elles lancent (``scripts/mesures_prose.py``).
UN_SEUL_PROCESSUS = {"MESURES_PROCESSUS": "1"}


def fichiers_du_moteur(paquet: Path = PAQUET) -> dict[str, str]:
    """Chaque fichier du moteur d'une carrière, sous le nom que son code porte
    (``co_filename``), et son chemin dans le paquet."""
    relatifs = set(PORTES)
    for regle in REGLES:
        if regle.endswith("/"):
            relatifs |= {fichier.relative_to(paquet).as_posix()
                         for fichier in (paquet / regle).glob("*.py")}
        else:
            relatifs.add(regle)
    return {str(paquet / relatif): relatif for relatif in sorted(relatifs)}


class Sonde:
    """Les entrées dans le moteur Python de ce processus : par
    ``sys.monitoring``, qui ne regarde que les fonctions du moteur, là où il
    existe (Python 3.12) ; sinon par ``sys.settrace``, qui voit passer chaque
    appel — plus lent, et le même relevé. GitHub lance la suite sous 3.11."""

    def __init__(self, script: Path, surveillance: bool | None = None):
        self.script = str(script)
        self.entrees: dict[str, set[str]] = defaultdict(set)
        self.moteur = fichiers_du_moteur()
        self.portes = {str(PAQUET / fichier): frozenset(noms) for fichier, noms in PORTES.items()}
        #: Par ``sys.monitoring`` ? Par défaut, dès qu'il existe.
        self.surveillance = (hasattr(sys, "monitoring") and not os.environ.get(PAR_TRACE)
                             if surveillance is None else surveillance)

    def _regarde(self, code) -> bool:
        """``code`` est-il une règle du moteur, dont l'appel peut être une
        entrée ? Non hors du moteur, pour le corps d'un module, ni, dans un
        fichier mêlé, pour ce qui n'est pas une porte."""
        fichier = code.co_filename
        return (fichier in self.moteur and code.co_name != "<module>"
                and code.co_qualname in self.portes.get(fichier, (code.co_qualname,)))

    def _relever(self, code, appelant) -> None:
        """Relève l'appel de ``code``, une règle du moteur, depuis le cadre
        ``appelant``, s'il entre du dehors : aucune fonction du moteur n'est en
        cours, ni aucun calcul gardé."""
        moteur = self.moteur
        cadre = appelant
        while cadre is not None:
            appele = cadre.f_code
            if appele.co_filename in moteur or (appele.co_filename, appele.co_name) == MEMOIRE:
                return
            cadre = cadre.f_back
        self.entrees[self._du_depot(appelant)].add(
            f"{moteur[code.co_filename]}:{code.co_qualname}")

    def demarrer(self) -> "Sonde":
        regarde, relever = self._regarde, self._relever
        if not self.surveillance:
            def trace(cadre, _evenement, _argument):
                # Chaque appel d'une fonction Python passe ici ; ne rien rendre
                # dispense de suivre ses lignes.
                if regarde(cadre.f_code):
                    relever(cadre.f_code, cadre.f_back)

            threading.settrace(trace)
            sys.settrace(trace)
            return self
        surveillance = sys.monitoring
        self.outil = next(i for i in (surveillance.PROFILER_ID, 0, 3, 4)
                          if surveillance.get_tool(i) is None)
        surveillance.use_tool_id(self.outil, "entrees_du_moteur")
        desactiver, cadre_de = surveillance.DISABLE, sys._getframe

        def debut(code, _position):
            # Ce qui n'est pas une règle du moteur ne se regarde plus.
            if not regarde(code):
                return desactiver
            relever(code, cadre_de(1).f_back)
            return None

        surveillance.register_callback(self.outil, surveillance.events.PY_START, debut)
        surveillance.set_events(self.outil, surveillance.events.PY_START)
        return self

    def arreter(self) -> None:
        if not self.surveillance:
            sys.settrace(None)
            threading.settrace(None)
            return
        surveillance = sys.monitoring
        surveillance.set_events(self.outil, 0)
        surveillance.register_callback(self.outil, surveillance.events.PY_START, None)
        surveillance.free_tool_id(self.outil)

    def _du_depot(self, cadre) -> str:
        """Le fichier du dépôt qui appelle : le premier, en remontant, qui soit
        du dépôt ou le script lancé — et non la bibliothèque standard ni une
        fonction écrite dans une autre, par où passe un appel décoré
        (``dans_un_instantane``)."""
        while cadre is not None:
            fichier = cadre.f_code.co_filename
            if fichier == self.script:
                break
            if (fichier.startswith(str(RACINE) + os.sep)
                    and "<locals>" not in cadre.f_code.co_qualname):
                return Path(fichier).relative_to(RACINE).as_posix()
            cadre = cadre.f_back
        script = Path(self.script)
        return (script.relative_to(RACINE).as_posix() if script.is_relative_to(RACINE)
                else script.name)

    def rendu(self) -> dict[str, list[str]]:
        return {appelant: sorted(entrees) for appelant, entrees in sorted(self.entrees.items())}


def lancer(script: Path, arguments: list[str], sortie: Path) -> int:
    """Lance ``script`` dans ce processus, sous la sonde, et écrit ce qu'elle
    relève ; un script qui s'arrête sur une erreur l'écrit aussi."""
    import runpy

    script = script.resolve()
    sys.argv = [str(script), *arguments]
    sys.path.insert(0, str(script.parent))
    sonde = Sonde(script).demarrer()
    erreur = None
    code = 0
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as fin:
        code = fin.code if isinstance(fin.code, int) else int(bool(fin.code))
    except BaseException as levee:      # noqa: BLE001 — dite à qui a lancé, puis relancée
        erreur = f"{type(levee).__name__} : {levee}"
        raise
    finally:
        sonde.arreter()
        sortie.write_text(json.dumps({"entrees": sonde.rendu(), "erreur": erreur}),
                          encoding="utf-8")
    return code


def relever(script: Path | str, arguments=(),
            par_trace: bool = False) -> dict[str, list[str]]:
    """Ce qui entre dans le moteur Python quand ``script`` tourne avec
    ``arguments``, dans un processus à lui : sous chaque fichier qui appelle,
    les règles du moteur qu'il appelle du dehors, triées. Le code de retour du
    script ne compte pas — une étape de la fabrique lancée pour vérifier rend 1
    quand son fichier est périmé —, mais un script qui s'arrête sur une erreur
    n'a pas tout fait tourner, et le relevé s'arrête avec lui. ``par_trace``
    fait relever par ``sys.settrace`` même là où ``sys.monitoring`` existe."""
    with tempfile.TemporaryDirectory() as dossier:
        sortie = Path(dossier) / "entrees.json"
        rendu = subprocess.run(
            [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "--ecrire", str(sortie),
             str(script), *arguments],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, **UN_SEUL_PROCESSUS,
                 **({PAR_TRACE: "1"} if par_trace else {})})
        lu = json.loads(sortie.read_text(encoding="utf-8")) if sortie.exists() else None
    if lu is None or lu["erreur"] is not None:
        raise RuntimeError(f"{script} ne tourne pas sous la sonde : "
                           + (rendu.stderr[-2000:] if lu is None else lu["erreur"]))
    return lu["entrees"]


def dire(nom: str, entrees: dict[str, list[str]]) -> str:
    if not entrees:
        return f"{nom} : rien"
    lignes = [nom]
    for appelant, regles in entrees.items():
        lignes.append(f"  {appelant}")
        lignes += [f"    {regle}" for regle in regles]
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--ecrire", type=Path, help=argparse.SUPPRESS)
    analyseur.add_argument("script", nargs="?", type=Path,
                           help="un script du dépôt ; sans lui, chaque étape de la fabrique")
    analyseur.add_argument("arguments", nargs=argparse.REMAINDER,
                           help="les arguments du script")
    choix = analyseur.parse_args(argv)
    if choix.ecrire is not None:
        return lancer(choix.script, choix.arguments, choix.ecrire)
    if choix.script is not None:
        print(dire(str(choix.script), relever(choix.script, choix.arguments)))
        return 0
    import regenerer

    for etape in regenerer.etapes():
        print(dire(etape.script, relever(RACINE / "scripts" / etape.script, etape.verifier)),
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
