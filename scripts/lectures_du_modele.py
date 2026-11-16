#!/usr/bin/env python3
"""Ce que lisent les calculs que la mémoire garde : fichiers, dossiers, modules.

    python scripts/lectures_du_modele.py           # le relevé, dossier par dossier
    python scripts/lectures_du_modele.py --json    # en entier

La mémoire des calculs (``retraite_notionnelle.memoire``) s'indexe sur ce que
git voit sous ``src/`` et ``data/``, hors de ce qu'aucun calcul gardé ne lit
(``HORS_DU_MODELE``). Ce script le relève : dans un processus neuf, sans
mémoire, il bâtit le paquet des données par la fabrique, fait simuler au
portage deux carrières par statut d'affiliation, calcule le coût agrégé et le
coût des avantages, et note chaque fichier du dépôt ouvert, chaque dossier
listé et chaque module chargé, et, de chaque fiche de règles, les champs lus.
Le moteur qui calcule est le JavaScript, qui ne lit que le paquet : de la
fabrique, le relevé ne retient que ce qu'elle lit pour bâtir les clés du
paquet que le moteur lit (``RELEVE_DU_PAQUET`` de ``pont.mjs``, action 161). Il échoue si l'un d'eux est hors du modèle, ou si un calcul lit
un champ documentaire d'une fiche, que l'empreinte ignore aussi
(``CHAMPS_DOCUMENTAIRES``) ; ``tests/test_outillage.py`` l'exige aussi
(feuille de route, action 135).
"""

from __future__ import annotations

import argparse
import ast
import builtins
import collections
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
# Le modèle ne s'importe qu'à la demande : la sonde doit voir ce qu'il lit
# dès son chargement.
sys.path.insert(0, str(RACINE / "src"))


def hors_du_modele(chemin: str) -> bool:
    """Un fichier ou un dossier des sources que l'empreinte ignore."""
    from retraite_notionnelle.memoire import du_modele

    return (chemin.startswith(("src/", "data/"))
            and not (du_modele(chemin) and du_modele(chemin.rstrip("/") + "/_")))


def champs_documentaires_lus(releve: dict) -> dict[str, list[str]]:
    """Les fiches de règles dont un calcul gardé lit un champ que l'empreinte
    ignore (``memoire.CHAMPS_DOCUMENTAIRES``), ou qu'il parcourt en entier."""
    from retraite_notionnelle.memoire import CHAMPS_DOCUMENTAIRES

    return {chemin: lus for chemin, noms in releve.get("champs", {}).items()
            if (lus := [n for n in noms if n == TOUT or n in CHAMPS_DOCUMENTAIRES])}


def relever() -> dict[str, list[str]]:
    """Le relevé, fait dans un processus neuf : aucune mémoire de celui-ci, ni
    des chargeurs ni des calculs, n'y cache une lecture."""
    environnement = {**os.environ, "CALCULS_SANS_MEMOIRE": "1", "PYTHONPATH": os.pathsep.join(
        filter(None, [str(RACINE / "src"), os.environ.get("PYTHONPATH")]))}
    acheve = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--sonde"],
                            cwd=RACINE, env=environnement, capture_output=True,
                            text=True, encoding="utf-8", check=False)
    if acheve.returncode:
        raise RuntimeError("le relevé a échoué :\n" + acheve.stderr[-3000:])
    return json.loads(acheve.stdout)


def _sonder() -> dict[str, list[str]]:
    racine = RACINE.resolve()
    lus: set[str] = set()
    listes: set[str] = set()

    def noter(ensemble: set[str], chemin) -> None:
        try:
            absolu = Path(os.fsdecode(chemin)).resolve()
        except (TypeError, ValueError, OSError):
            return
        if absolu.is_relative_to(racine):
            ensemble.add(absolu.relative_to(racine).as_posix())

    ouvrir, parcourir, lister = io.open, os.scandir, os.listdir

    def ouvrir_en_notant(fichier, *args, **kwargs):
        if not isinstance(fichier, int):
            noter(lus, fichier)
        return ouvrir(fichier, *args, **kwargs)

    def parcourir_en_notant(chemin="."):
        noter(listes, chemin)
        return parcourir(chemin)

    def lister_en_notant(chemin="."):
        noter(listes, chemin)
        return lister(chemin)

    builtins.open = io.open = ouvrir_en_notant
    os.scandir, os.listdir = parcourir_en_notant, lister_en_notant

    from retraite_notionnelle import memoire
    from retraite_notionnelle.donnees import chargement

    champs: dict[str, set[str]] = collections.defaultdict(set)

    def suivre(chemin, contenu):
        try:
            relatif = Path(chemin).resolve().relative_to(racine).as_posix()
        except ValueError:
            return contenu
        if not memoire.est_une_fiche(relatif) or type(contenu) is not dict:
            return contenu
        return _ChampsNotes(contenu, champs[relatif])

    chargement.SUIVI = suivre
    from retraite_notionnelle import pont
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.donnees.simulateur import SimulateurDeDonnees

    releve_du_paquet = Path(tempfile.mkdtemp()) / "cles"
    releve_du_paquet.touch()
    os.environ["RELEVE_DU_PAQUET"] = str(releve_du_paquet)

    # Les carrières, le portage les bâtit de leurs requêtes et les simule.
    cas = [{"cle": f"{statut}_{naissance}",
            "requete": {"statut": statut, "naissance": naissance}}
           for statut in SimulateurDeDonnees(Parametres()).affiliations.codes
           for naissance in ("1950", "1975")]
    pont.simulations(cas, pont.paquet_des_donnees())
    memoire.cout(Parametres())
    memoire.avantages(Parametres())
    src = (racine / "src").resolve()
    modules = {Path(module.__file__).resolve().relative_to(racine).as_posix()
               for module in list(sys.modules.values())
               if getattr(module, "__file__", None)
               and Path(module.__file__).resolve().is_relative_to(src)}
    # Le moteur ne lit que le paquet, et du paquet, les clés qu'il a notées :
    # la fabrique les rebâtit ici, elles seules, et ce qu'elle lit pour elles
    # se note comme le reste.
    pont.fermer()
    cles_lues = set(releve_du_paquet.read_text(encoding="utf-8").split())
    cles = _construire_les_cles_lues(cles_lues)
    # Une fiche ouverte sans passer par ``charger_yaml`` a pu être lue en entier.
    for chemin in lus:
        if memoire.est_une_fiche(chemin) and chemin not in champs:
            champs[chemin].add(TOUT)
    return {"lus": sorted(lus), "listes": sorted(listes), "modules": sorted(modules),
            "champs": {chemin: sorted(noms) for chemin, noms in sorted(champs.items())},
            "paquet": {"lues": sorted(cles_lues), "non_lues": sorted(cles - cles_lues)}}


def _construire_les_cles_lues(cles_lues: set[str]) -> set[str]:
    """Les clés que la fabrique écrit au paquet (``construire`` de
    ``scripts/construire_donnees.py``, sans le bilan ni les agrégats, comme
    ``pont.paquet_des_donnees``), après avoir bâti, d'elles, celles que le
    moteur lit, ``cles_lues``, et elles seules : une autre reste à ``None``,
    sans que rien de ce qu'elle lirait ne se lise. Une valeur étalée (``**``)
    se bâtit toujours, ses clés ne se sachant qu'après."""
    import importlib.util

    from retraite_notionnelle import pont

    spec = importlib.util.spec_from_file_location("construire_donnees", pont.FABRIQUE)
    fabrique = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = fabrique
    spec.loader.exec_module(fabrique)
    arbre = ast.parse(textwrap.dedent(_source(fabrique.construire)))
    dictionnaire = next(noeud.value for noeud in ast.walk(arbre)
                        if isinstance(noeud, ast.Assign) and isinstance(noeud.value, ast.Dict)
                        and [c.id for c in noeud.targets if isinstance(c, ast.Name)] == ["paquet"])
    ecrites = {cle.value for cle in dictionnaire.keys if isinstance(cle, ast.Constant)}
    dictionnaire.values = [
        valeur if cle is None or not isinstance(cle, ast.Constant) or cle.value in cles_lues
        else ast.Constant(None)
        for cle, valeur in zip(dictionnaire.keys, dictionnaire.values)]
    ast.fix_missing_locations(arbre)
    exec(compile(arbre, pont.FABRIQUE, "exec"), fabrique.__dict__)  # noqa: S102
    paquet = json.loads(fabrique.construire(b"{}", b"{}"))
    return ecrites | set(paquet)


def _source(fonction) -> str:
    import inspect

    return inspect.getsource(fonction)


#: Le champ noté quand une fiche est parcourue en entier.
TOUT = "*"


class _ChampsNotes(dict):
    """Le dictionnaire d'une fiche, qui note chacun de ses champs lus ; le
    parcourir, le copier ou le comparer en entier note :data:`TOUT`. Python
    passe par ``keys`` et ``__getitem__`` pour copier une sous-classe dont
    ``__iter__`` est redéfini : ``dict(f)`` et ``{**f}`` sont vus."""

    def __init__(self, contenu: dict, notes: set[str]) -> None:
        super().__init__(contenu)
        self._notes = notes

    def __getitem__(self, cle):
        self._notes.add(cle)
        return super().__getitem__(cle)

    def get(self, cle, defaut=None):
        self._notes.add(cle)
        return super().get(cle, defaut)

    def __contains__(self, cle):
        self._notes.add(cle)
        return super().__contains__(cle)

    def pop(self, cle, *defaut):
        self._notes.add(cle)
        return super().pop(cle, *defaut)

    def setdefault(self, cle, defaut=None):
        self._notes.add(cle)
        return super().setdefault(cle, defaut)

    def _tout(self):
        self._notes.add(TOUT)

    def __iter__(self):
        self._tout()
        return super().__iter__()

    def keys(self):
        self._tout()
        return super().keys()

    def values(self):
        self._tout()
        return super().values()

    def items(self):
        self._tout()
        return super().items()

    def copy(self):
        self._tout()
        return dict(super().items())

    def __eq__(self, autre):
        self._tout()
        return super().__eq__(autre)

    __hash__ = None

    def __reduce_ex__(self, protocole):
        self._tout()
        return (dict, (dict(super().items()),))


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--json", action="store_true", help="le relevé en entier")
    analyseur.add_argument("--sonde", action="store_true", help=argparse.SUPPRESS)
    options = analyseur.parse_args(arguments)
    if options.sonde:
        json.dump(_sonder(), sys.stdout)
        return 0
    releve = relever()
    hors = [c for cle in ("lus", "listes", "modules") for c in releve[cle] if hors_du_modele(c)]
    documentaires = champs_documentaires_lus(releve)
    echec = 1 if hors or documentaires else 0
    if options.json:
        json.dump({**releve, "hors_du_modele": hors, "champs_documentaires_lus": documentaires},
                  sys.stdout, ensure_ascii=False, indent=1)
        print()
        return echec
    print(f"{len(releve['lus'])} fichiers lus, {len(releve['listes'])} dossiers listés, "
          f"{len(releve['modules'])} modules chargés")
    for dossier, nombre in sorted(collections.Counter(
            c.rsplit("/", 1)[0] for c in releve["lus"]).items()):
        print(f"  {nombre:4d}  {dossier}/")
    print("hors du modèle : " + (", ".join(hors) if hors else "rien"))
    print(f"{len(releve['champs'])} fiches de règles lues, champs : " + ", ".join(sorted(
        {n for noms in releve["champs"].values() for n in noms})))
    print("champs documentaires lus : " + (", ".join(
        f"{c} ({', '.join(n)})" for c, n in documentaires.items()) if documentaires else "aucun"))
    return echec


if __name__ == "__main__":
    sys.exit(main())
