"""La mémoire des calculs lourds, sur le disque, sous l'empreinte des sources.

    from retraite_notionnelle import memoire

    cout = memoire.cout(Parametres())                  # le coût de la page Coût
    sans = memoire.cout(Parametres(), comptes=False, assiette=False)
    avantages = memoire.avantages(Parametres())

POURQUOI
--------
Le coût agrégé prend vingt secondes, et la suite des tests faisait cinquante-cinq
calculs du coût ou des avantages, dix-sept minutes en tout : vingt fois le même
coût, celui de la page Coût, dans neuf fichiers et quatre processus, huit fois
le même coût des avantages. Près des deux tiers de ces dix-sept minutes
refaisaient un calcul déjà fait (feuille de route, action 135). Chaque fichier
gardait le sien dans une fixture, et aucun ne pouvait prendre celui d'un autre.

CE QUI SE GARDE, ET SOUS QUOI
-----------------------------
Un calcul se garde sous sa CLÉ — ses paramètres, ses options, ce qu'il ne
tient pas des sources — et sous l'EMPREINTE des sources : tout ce que git voit
sous ``src/``, ``data/`` et ``scripts/``, octet par octet, et la version de
Python. Qu'un de ces fichiers bouge, et tout se refait ; un calcul pendant
lequel l'un d'eux a bougé ne se garde pas. Il se relit d'abord du processus,
puis de ``.cache/calculs/<empreinte>/``, que git ignore ; les quatre empreintes
les plus récentes y restent. Chaque lecture rend un objet neuf, comme
``charger_yaml`` rend une copie : ce qu'un appelant en fait ne touche pas les
autres. ``CALCULS_SANS_MEMOIRE=1`` fait tout recalculer.

LA RÈGLE
--------
La mémoire ne connaît que le modèle INTACT. Un contexte qui en remplace une
fonction — la proposition prospective, le stock à l'âge légal, le régime
unique des scripts — s'ouvre sous ``modele_modifie()``, et la mémoire se tait
tant qu'il est ouvert : rien ne s'y lit, rien ne s'y écrit. Un test qui prend
``monkeypatch`` en fait autant (``tests/conftest.py``). Et ``cout()`` comme
``avantages()`` construisent elles-mêmes, depuis les paramètres, le simulateur
et les données de leur calcul : venus d'ailleurs, ils pourraient ne pas être
ceux que la clé décrit. Un script qui garde un calcul à lui
(``memoriser_pour``) fait de même.
"""

from __future__ import annotations

import hashlib
import os
import pickle
import shutil
import subprocess
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, TypeVar

from .config import RACINE_DONNEES, RACINE_PROJET, Parametres

T = TypeVar("T")

#: Où les calculs se gardent : un dossier par empreinte.
DOSSIER = RACINE_PROJET / ".cache" / "calculs"
#: Posée, cette variable d'environnement fait tout recalculer, sans rien lire
#: ni écrire.
SANS_MEMOIRE = "CALCULS_SANS_MEMOIRE"
#: Les empreintes gardées, les plus récentes : de quoi aller et venir entre deux
#: états du dépôt sans tout refaire.
EMPREINTES_GARDEES = 4
#: Ce dont un calcul dépend, tel que git le voit. Ce qu'il ignore n'en est pas :
#: ``data/brut``, les téléchargements, ne se lit que par les scripts de
#: récupération. Les scripts en sont : certains calculs gardés y sont écrits.
SOURCES = ("src", "data", "scripts")

#: Les calculs de ce processus, par leur nom : l'objet picklé, dont chaque
#: lecture tire un objet neuf.
_EN_MEMOIRE: dict[str, bytes] = {}
#: Les remplacements du modèle ouverts : ils valent pour tout le processus.
_MODIFICATIONS = 0
#: La lecture seule, elle, ne vaut que pour le fil qui la demande.
_FIL = threading.local()


def _en_lecture_seule() -> bool:
    return getattr(_FIL, "lecture_seule", 0) > 0


class Absent(Exception):
    """En lecture seule : le calcul n'est pas gardé, et ne se fait pas ici."""


def _sources() -> list[bytes] | None:
    try:
        listes = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard",
             "--", *SOURCES], cwd=RACINE_PROJET, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return sorted(set(filter(None, listes.split(b"\0"))))


def empreinte() -> str | None:
    """L'empreinte des sources, en un vingtième de seconde ; ``None`` hors d'un
    dépôt git, et rien ne se garde."""
    chemins = _sources()
    if chemins is None:
        return None
    somme = hashlib.sha256(sys.version.encode())
    for chemin in chemins:
        somme.update(chemin + b"\0")
        try:
            contenu = (RACINE_PROJET / os.fsdecode(chemin)).read_bytes()
        except OSError:          # au registre de git, mais effacé du répertoire
            somme.update(b"-")
            continue
        somme.update(b"+" + len(contenu).to_bytes(8, "little") + contenu)
    return somme.hexdigest()[:24]


def _code_retouche() -> bool:
    """Un fichier Python des sources a-t-il changé depuis que ce processus a
    chargé le modèle ? Son calcul s'est peut-être fait avec l'ancien code, et
    l'empreinte, qui lit le nouveau, le garderait sous un nom qui n'est pas le
    sien."""
    from . import CHARGE_A

    for chemin in _sources() or ():
        if chemin.endswith(b".py"):
            try:
                if (RACINE_PROJET / os.fsdecode(chemin)).stat().st_mtime > CHARGE_A:
                    return True
            except OSError:
                continue
    return False


def nom(cle: tuple) -> str:
    """Le nom de fichier d'une clé : son genre, lisible, et l'empreinte de sa
    représentation, qui doit être complète — des valeurs simples, des
    dataclasses comme ``Parametres``, jamais un objet qui s'écrit par son
    adresse."""
    return f"{cle[0]}-{hashlib.sha256(repr(cle).encode()).hexdigest()[:16]}"


def _active() -> bool:
    return not _MODIFICATIONS and not os.environ.get(SANS_MEMOIRE)


def _relire(empreinte_: str | None, nom_: str) -> bytes | None:
    if empreinte_ is None:
        return None
    try:
        return (DOSSIER / empreinte_ / f"{nom_}.pickle").read_bytes()
    except OSError:
        return None


def _garder(empreinte_: str | None, nom_: str, donnees: bytes) -> None:
    """Garde un calcul sous l'empreinte d'avant lui, si c'est encore celle des
    sources et que le code chargé est le leur ; efface les empreintes les plus
    anciennes."""
    if empreinte_ is None or empreinte() != empreinte_ or _code_retouche():
        return
    dossier = DOSSIER / empreinte_
    try:
        dossier.mkdir(parents=True, exist_ok=True)
        provisoire = dossier / f".{nom_}.{os.getpid()}"
        provisoire.write_bytes(donnees)
        os.replace(provisoire, dossier / f"{nom_}.pickle")
        anciens = sorted((d for d in DOSSIER.iterdir() if d.is_dir() and d != dossier),
                         key=lambda d: d.stat().st_mtime, reverse=True)
        for ancien in anciens[EMPREINTES_GARDEES - 1:]:
            shutil.rmtree(ancien, ignore_errors=True)
    except OSError as souci:     # la mémoire n'est qu'un raccourci
        print(f"memoire : {nom_} non gardé ({souci})", file=sys.stderr)


def memoriser(cle: tuple, calcul: Callable[[], T]) -> T:
    """``calcul()``, fait une fois : relu du processus, puis du disque, tant que
    les sources ne bougent pas.

    ``cle`` dit tout ce dont le calcul dépend hors des sources, en commençant
    par son genre (``("cout", parametres, …)``) ; deux calculs qui ne font pas
    la même chose ne partagent jamais une clé. Un objet que pickle ne sait pas
    écrire se rend sans se garder.
    """
    if not _active():
        if _en_lecture_seule():
            raise Absent(cle[0])
        return calcul()
    nom_ = nom(cle)
    if nom_ in _EN_MEMOIRE:
        return pickle.loads(_EN_MEMOIRE[nom_])
    empreinte_ = empreinte()
    donnees = _relire(empreinte_, nom_)
    if donnees is not None:
        try:
            objet = pickle.loads(donnees)
        except Exception:        # noqa: BLE001 — tronqué, illisible : à refaire
            pass
        else:
            _EN_MEMOIRE[nom_] = donnees
            return objet
    if _en_lecture_seule():
        raise Absent(nom_)
    objet = calcul()
    try:
        donnees = pickle.dumps(objet, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:            # noqa: BLE001 — un objet qui ne s'écrit pas
        return objet
    _EN_MEMOIRE[nom_] = donnees
    _garder(empreinte_, nom_, donnees)
    return objet


@contextmanager
def modele_modifie():
    """Le temps d'un remplacement d'une fonction du modèle : la mémoire se tait."""
    global _MODIFICATIONS
    _MODIFICATIONS += 1
    try:
        yield
    finally:
        _MODIFICATIONS -= 1


@contextmanager
def lecture_seule():
    """Ne rend que ce qui est gardé ; le reste lève ``Absent`` au lieu de se
    calculer. Le précalcul des chiffres ancrés s'en sert pour savoir ce qu'il
    doit confier à ses processus (``scripts/mesures_prose.py``)."""
    _FIL.lecture_seule = getattr(_FIL, "lecture_seule", 0) + 1
    try:
        yield
    finally:
        _FIL.lecture_seule -= 1


# -- les calculs gardés --------------------------------------------------------

#: Les options de ``calculer_cout`` que la clé porte, avec leur défaut.
OPTIONS_DU_COUT = ("ponderation", "liquidation", "convention_recette",
                   "convention_reversion")


def memoriser_pour(parametres: Parametres, cle: tuple, calcul: Callable[[], T]) -> T:
    """``memoriser``, si ces paramètres lisent les données du dépôt : la clé ne
    décrit qu'elles, et une copie ailleurs, que l'on aurait modifiée, se
    calcule sans mémoire. La clé doit porter ``parametres``."""
    try:
        du_depot = Path(parametres.racine_donnees).resolve() == RACINE_DONNEES.resolve()
    except OSError:
        du_depot = False
    if du_depot:
        return memoriser(cle, calcul)
    if _en_lecture_seule():
        raise Absent(cle[0])
    return calcul()


def _reglages(fonction, noms: tuple[str, ...], options: dict) -> dict:
    """Les options, défaut compris : écrite ou non, une option par défaut est
    le même calcul, et la même clé."""
    import inspect

    inconnues = set(options) - set(noms)
    if inconnues:
        raise TypeError(f"{fonction.__name__} : options inconnues {sorted(inconnues)}")
    signature = inspect.signature(fonction).parameters
    return {nom_: options.get(nom_, signature[nom_].default) for nom_ in noms}


def cout(parametres: Parametres | None = None, *, comptes: bool = True,
         assiette: bool = True, cas_types: tuple | None = None, **options):
    """``calculer_cout`` sous ces paramètres, sur les données du dépôt.

    ``comptes`` et ``assiette`` : avec les comptes du COR et l'assiette des
    prélèvements, comme la page Coût, ou sans ; les comptes sont ceux du
    scénario de projection des paramètres, comme sur la page. ``cas_types`` :
    une autre grille que celle du dépôt. Les autres options sont celles de
    ``calculer_cout``, et la clé les porte toutes, défaut compris :
    ``convention_recette`` écrite ou non, c'est le même calcul.
    """
    from .castypes import CAS_TYPES
    from .cout import calculer_cout

    parametres = parametres if parametres is not None else Parametres()
    reglages = _reglages(calculer_cout, OPTIONS_DU_COUT, options)
    grille = tuple(cas_types) if cas_types is not None else CAS_TYPES

    def calcul():
        from .donnees.assiette import AssietteActivite
        from .donnees.depenses import DepensesRetraite
        from .donnees.equilibre import ComptesRetraite, variante_du_scenario
        from .donnees.population import Population
        from .simulateur import Simulateur

        racine = parametres.racine_donnees
        variante = variante_du_scenario(parametres.scenario_projection,
                                        racine / "reference" / "macro")
        return calculer_cout(
            Simulateur(parametres), DepensesRetraite(racine), Population(racine),
            ComptesRetraite(racine, variante=variante) if comptes else None,
            cas_types=grille, assiette=AssietteActivite(racine) if assiette else None,
            **reglages)

    return memoriser_pour(parametres, ("cout", parametres, comptes, assiette, grille,
                                  tuple(sorted(reglages.items()))), calcul)


def avantages(parametres: Parametres | None = None, **options):
    """``calculer_avantages`` sous ces paramètres, sur les données du dépôt."""
    from .avantages import calculer_avantages

    parametres = parametres if parametres is not None else Parametres()
    reglages = _reglages(calculer_avantages, ("ponderation", "liquidation"), options)

    def calcul():
        from .donnees.depenses import DepensesRetraite
        from .donnees.population import Population
        from .simulateur import Simulateur

        racine = parametres.racine_donnees
        return calculer_avantages(Simulateur(parametres), DepensesRetraite(racine),
                                  Population(racine), **reglages)

    return memoriser_pour(parametres, ("avantages", parametres, tuple(sorted(reglages.items()))),
                     calcul)
