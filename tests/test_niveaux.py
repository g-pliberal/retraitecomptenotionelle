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


def test_le_filet_du_site_vise_des_tests_qui_existent():
    """Un test du filet renommé ou déplacé n'y serait plus, sans bruit."""
    perdus = [(f, t) for (f, t) in conftest.SITE
              if not (TESTS / f).is_file() or t not in _fonctions(f)]
    assert not perdus, f"{perdus} : le filet du site ne vise plus ces tests"


def test_chaque_niveau_est_un_niveau_connu():
    assert set(conftest.EXCEPTIONS.values()) <= set(conftest.NIVEAUX)


def test_un_fichier_que_rien_ne_nomme_est_rapide():
    """Une règle nouvelle entre dans la suite rapide sans qu'on y pense."""
    assert conftest.niveau("test_une_regle_nouvelle.py", "test_elle_se_lit_au_texte") == "rapide"
    assert conftest.niveau("test_web.py", "test_quelconque") == "complet"
    assert conftest.niveau("test_oracle.py",
                           "test_les_exemples_publies_par_les_caisses_sont_reproduits") == "rapide"


# -- les fichiers isolés -------------------------------------------------------


def test_chaque_fichier_isole_et_ce_qu_il_lit_existent():
    racine = TESTS.parent
    absents = sorted(f for f in conftest.ISOLES if not (TESTS / f).is_file())
    absents += sorted(c for lus in conftest.ISOLES.values() for c in lus
                      if not (racine / c).is_file())
    assert not absents, f"{absents} : la table des fichiers isolés nomme des fichiers disparus"


def test_un_fichier_isole_n_importe_rien_du_depot():
    """Isolé, il ne lit que ce qu'il déclare : un import du modèle, ou d'un
    module des tests, ferait dépendre son résultat de ce que son empreinte
    ne lit pas."""
    for fichier in conftest.ISOLES:
        arbre = ast.parse((TESTS / fichier).read_text(encoding="utf-8"))
        modules = {alias.name.split(".")[0] for n in ast.walk(arbre)
                   if isinstance(n, ast.Import) for alias in n.names}
        modules |= {(n.module or "").split(".")[0] for n in ast.walk(arbre)
                    if isinstance(n, ast.ImportFrom) and not n.level}
        assert modules <= {"__future__", "pathlib", "pytest", "shutil", "subprocess"}, (
            fichier, sorted(modules))


def test_l_empreinte_d_un_fichier_isole_suit_ce_qu_il_lit(monkeypatch, tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_isole.py").write_text("def test_x(): pass\n", encoding="utf-8")
    (tmp_path / "tests" / "conftest.py").write_text("", encoding="utf-8")
    (tmp_path / "script.sh").write_text("echo 1\n", encoding="utf-8")
    monkeypatch.setattr(conftest, "RACINE", tmp_path)
    monkeypatch.setattr(conftest, "ISOLES", {"test_isole.py": ("script.sh",)})
    monkeypatch.setattr(conftest, "OUTILS_DES_ISOLES", ())
    monkeypatch.setattr(conftest, "_EMPREINTES", {})
    avant = conftest.empreinte_isolee("test_isole.py")
    (tmp_path / "script.sh").write_text("echo 2\n", encoding="utf-8")
    assert conftest.empreinte_isolee("test_isole.py") == avant      # une fois par processus
    monkeypatch.setattr(conftest, "_EMPREINTES", {})
    apres = conftest.empreinte_isolee("test_isole.py")
    assert apres != avant
    assert (conftest.marque_de_reussite(apres, "tests/test_isole.py::test_x")
            != conftest.marque_de_reussite(avant, "tests/test_isole.py::test_x"))
