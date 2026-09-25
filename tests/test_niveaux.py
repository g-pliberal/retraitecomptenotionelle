"""Les niveaux de la suite : ce que `tests/conftest.py` range, et où.

La suite rapide (`python -m pytest -m rapide`) ne vaut que si son partage est
juste. Deux divorces la trahiraient sans bruit : un fichier renommé que la
table nomme encore, et qui retomberait dans la suite rapide avec tout son
poids ; une exception qui vise un test disparu, et ne vise plus rien. C'est la
mécanique de `zones.yaml` : la table et les fichiers se tiennent l'un l'autre.
"""

from __future__ import annotations

import ast
from pathlib import Path

import conftest

TESTS = Path(__file__).resolve().parent


def _fonctions(fichier: str) -> set[str]:
    arbre = ast.parse((TESTS / fichier).read_text(encoding="utf-8"))
    return {n.name for n in ast.walk(arbre) if isinstance(n, ast.FunctionDef)}


def test_chaque_fichier_range_existe():
    absents = sorted(f for f in conftest.COMPLETS | conftest.CONTROLES
                     if not (TESTS / f).is_file())
    assert not absents, f"{absents} : la table de tests/conftest.py nomme des fichiers disparus"


def test_un_fichier_n_a_qu_un_niveau():
    assert not conftest.COMPLETS & conftest.CONTROLES


def test_chaque_exception_vise_un_test_qui_existe():
    perdues = [(f, t) for (f, t) in conftest.EXCEPTIONS
               if not (TESTS / f).is_file() or t not in _fonctions(f)]
    assert not perdues, f"{perdues} : ces exceptions ne visent plus aucun test"


def test_chaque_niveau_est_un_niveau_connu():
    assert set(conftest.EXCEPTIONS.values()) <= set(conftest.NIVEAUX)


def test_un_fichier_que_rien_ne_nomme_est_rapide():
    """Une règle nouvelle entre dans la suite rapide sans qu'on y pense."""
    assert conftest.niveau("test_une_regle_nouvelle.py", "test_elle_se_lit_au_texte") == "rapide"
    assert conftest.niveau("test_web.py", "test_quelconque") == "complet"
    assert conftest.niveau("test_oracle.py",
                           "test_les_exemples_publies_par_les_caisses_sont_reproduits") == "rapide"
