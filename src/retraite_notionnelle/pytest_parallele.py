"""Greffon pytest : la suite complète se répartit d'elle-même sur les cœurs.

Chargé par ``-p retraite_notionnelle.pytest_parallele`` (voir ``addopts`` dans
``pyproject.toml``). Il faut un greffon, et non un ``conftest.py`` : les
conftest sont chargés *par* ``pytest_load_initial_conftests``, donc trop tard
pour s'y inscrire, alors qu'un greffon ``-p`` est enregistré avant.

La suite tient sept minutes en série, moins d'une répartie sur quatre cœurs.
"""

from __future__ import annotations

import os


def pytest_load_initial_conftests(early_config, parser, args):
    """Ajoute ``-n auto`` quand on lance toute la suite, et seulement alors.

    Quatre garde-fous, parce que le parallélisme n'est pas toujours un gain :

    - sans ``pytest-xdist`` installé, on ne touche à rien et la suite tourne en
      série comme avant : le dépôt ne gagne pas de dépendance dure ;
    - si l'appelant a déjà dit ce qu'il voulait (``-n``, ``PYTEST_SANS_XDIST``),
      il commande ;
    - si l'appelant vise un fichier ou un cas précis, on reste en série :
      démarrer quatre processus pour un test coûte plus cher que de l'exécuter,
      et la sortie d'un run parallèle se lit moins bien ;
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
    cibles = getattr(early_config.known_args_namespace, "file_or_dir", [])
    if cibles:
        return
    if (os.cpu_count() or 1) < 2:
        return
    args[:] = ["-n", "auto", *args]
