"""Greffon pytest : la suite complète se répartit d'elle-même sur les cœurs.

Chargé par ``-p retraite_notionnelle.pytest_parallele`` (voir ``addopts`` dans
``pyproject.toml``). Il faut un greffon, et non un ``conftest.py`` : les
conftest sont chargés *par* ``pytest_load_initial_conftests``, donc trop tard
pour s'y inscrire, alors qu'un greffon ``-p`` est enregistré avant.

La suite tient sept minutes en série. Répartie sur quatre cœurs par paquets
fixés d'avance, elle en tenait encore près de quatre, un processus finissant
seul les tests longs ; avec le vol de tâches (``--dist worksteal``), deux,
quand la mémoire des calculs lourds est chaude — la première suite après une
retouche de ``src/``, ``data/`` ou ``scripts/`` en tient cinq, le temps de les
refaire (mesuré le 30 septembre 2026).

La course de GitHub la découpe en plus en tranches, une par travail
(``--tranche 2/4``, action 135) : sans mémoire des calculs, elle tenait
trente-six minutes sur les quatre cœurs d'une seule machine, le 14 novembre
2026. Une tranche joue des fichiers entiers — les tests d'un fichier partagent
des calculs lourds, que deux machines feraient deux fois —, répartis selon ce
que chacun a duré à la dernière course sans mémoire (:data:`DUREES`).
"""

from __future__ import annotations

import os
from pathlib import Path

#: Le poids, en octets, au-delà duquel des fichiers visés se répartissent eux
#: aussi : ``test_web.py`` visé seul tenait près de quatre minutes en série, le
#: 30 septembre 2026, quand démarrer quatre processus coûte quelques secondes.
#: En deçà, un fichier de règle se lance plus vite en série.
POIDS_REPARTI = 60_000

#: Ce que chaque fichier de tests a duré, en secondes de processus, à la
#: dernière course de GitHub partie sans mémoire des calculs : la course
#: l'écrit (``scripts/durees_suite.py``, ``scripts/publier_fabrique.sh``), les
#: tranches s'y pèsent.
DUREES = Path(".github") / "durees_suite.tsv"

#: Ce que pèse, en secondes, un fichier que la dernière mesure ne connaît pas.
DUREE_INCONNUE = 1.0


def pytest_addoption(parser):
    parser.addoption(
        "--tranche", default=None, metavar="RANG/NOMBRE",
        help="ne jouer que la tranche RANG des NOMBRE tranches de la suite (2/4)")


def lire_tranche(choix: str) -> tuple[int, int]:
    """``2/4`` : la deuxième de quatre tranches."""
    import pytest

    try:
        rang, nombre = (int(partie) for partie in choix.split("/"))
    except ValueError:
        raise pytest.UsageError(f"--tranche {choix} : attendu RANG/NOMBRE, comme 2/4") from None
    if not 1 <= rang <= nombre:
        raise pytest.UsageError(f"--tranche {choix} : le rang va de 1 à {max(nombre, 1)}")
    return rang, nombre


def lire_durees(texte: str) -> dict[str, float]:
    """Le tableau des durées : un fichier et ses secondes par ligne, séparés
    d'une tabulation ; une ligne vide ou de commentaire (``#``) ne compte pas."""
    durees = {}
    for ligne in texte.splitlines():
        if ligne.strip() and not ligne.startswith("#"):
            fichier, secondes = ligne.split("\t")[:2]
            durees[fichier] = float(secondes)
    return durees


def repartir(fichiers, durees, tranches: int) -> dict[str, int]:
    """La tranche de chaque fichier, de 1 à ``tranches`` : le plus long
    d'abord, chacun dans la tranche la moins chargée, la première à égalité ;
    à durée égale, dans l'ordre des noms. La même liste et les mêmes durées
    donnent le même partage sur chaque machine de la course."""
    charges = [0.0] * tranches
    partage = {}
    poids = {fichier: durees.get(fichier, DUREE_INCONNUE) for fichier in fichiers}
    for fichier in sorted(poids, key=lambda f: (-poids[f], f)):
        rang = charges.index(min(charges))
        charges[rang] += poids[fichier]
        partage[fichier] = rang + 1
    return partage


def pytest_collection_modifyitems(config, items):
    """Sous ``--tranche``, n'en garde que les tests ; les autres sont écartés,
    et comptés comme tels."""
    choix = config.getoption("tranche", None)
    if not choix:
        return
    rang, nombre = lire_tranche(choix)
    tableau = Path(config.rootpath) / DUREES
    durees = lire_durees(tableau.read_text(encoding="utf-8")) if tableau.is_file() else {}
    fichier = {item: item.nodeid.split("::")[0] for item in items}
    partage = repartir(sorted(set(fichier.values())), durees, nombre)
    gardes = [item for item in items if partage[fichier[item]] == rang]
    ecartes = [item for item in items if partage[fichier[item]] != rang]
    if ecartes:
        config.hook.pytest_deselected(items=ecartes)
        items[:] = gardes


def pytest_load_initial_conftests(early_config, parser, args):
    """Ajoute ``-n auto --dist worksteal`` quand on lance toute la suite, ou des
    fichiers lourds.

    Quatre garde-fous, parce que le parallélisme n'est pas toujours un gain :

    - sans ``pytest-xdist`` installé, on ne touche à rien et la suite tourne en
      série comme avant : le dépôt ne gagne pas de dépendance dure ;
    - si l'appelant a déjà dit ce qu'il voulait (``-n``, ``PYTEST_SANS_XDIST``),
      il commande ;
    - si l'appelant vise un cas précis (``fichier::test``, ``-k``), ou des
      fichiers légers, on reste en série : démarrer quatre processus pour un
      test coûte plus cher que de l'exécuter, et la sortie d'un run parallèle
      se lit moins bien ; des fichiers entiers qui pèsent plus de
      :data:`POIDS_REPARTI` se répartissent, comme la suite ;
    - sur une machine à un cœur, il n'y a rien à répartir.
    """
    if any(a == "-n" or a.startswith(("-n", "--numprocesses")) for a in args):
        return
    if os.environ.get("PYTEST_SANS_XDIST"):
        return
    try:
        import xdist  # noqa: F401
    except ImportError:
        return
    # Une cible explicite, c'est un argument positionnel. On le lit sur
    # l'analyse que pytest a déjà faite, et non en relisant `args` à la main :
    # la valeur d'une option (le nom de greffon derrière `-p`, par exemple) y
    # ressemble à s'y méprendre.
    options = early_config.known_args_namespace
    cibles = getattr(options, "file_or_dir", [])
    if cibles and (getattr(options, "keyword", "") or not _lourdes(cibles)):
        return
    if (os.cpu_count() or 1) < 2:
        return
    args[:] = ["-n", "auto", "--dist", "worksteal", *args]


def _lourdes(cibles: list[str]) -> bool:
    """Des fichiers entiers, aucun cas précis, qui pèsent assez pour valoir
    le démarrage de quatre processus ; un dossier visé vaut une suite."""
    poids = 0
    for cible in cibles:
        if "::" in cible:
            return False
        chemin = Path(cible)
        if chemin.is_dir():
            return True
        if chemin.is_file():
            poids += chemin.stat().st_size
    return poids > POIDS_REPARTI
