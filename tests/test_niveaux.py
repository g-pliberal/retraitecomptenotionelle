"""Les niveaux de la suite : ce que `tests/conftest.py` range, et où.

La suite rapide (`python -m pytest -m rapide`) ne vaut que si son partage est
juste. Deux divorces la trahiraient sans bruit : un fichier renommé que la
table nomme encore, et qui retomberait dans la suite rapide avec tout son
poids ; une exception qui vise un test disparu, et ne vise plus rien. C'est la
mécanique de `zones.yaml` : la table et les fichiers se tiennent l'un l'autre.
"""

from __future__ import annotations

import ast
import builtins
from pathlib import Path

import conftest

TESTS = Path(__file__).resolve().parent


def _fonctions(fichier: str) -> set[str]:
    arbre = ast.parse((TESTS / fichier).read_text(encoding="utf-8"))
    return {n.name for n in ast.walk(arbre) if isinstance(n, ast.FunctionDef)}


#: Les tests d'une seconde qui ont rougi main, du 6 au 17 octobre 2026, sans
#: qu'aucune session les ait joués : leurs fichiers ne sont pas de la suite
#: rapide (action 163, garde 3), et le dernier garde les comptes du parcours.
GARDES_RAPIDES = (
    ("test_web.py", "test_les_modules_sont_tous_precharges"),
    ("test_web.py", "test_le_README_n_ecrit_a_la_main_ni_statuts_ni_regimes"),
    ("test_web_revues.py", "test_le_menu_des_statuts_est_groupe_par_famille"),
    ("test_niveaux.py", "test_chaque_exception_vise_un_test_qui_existe"),
    ("test_niveaux.py", "test_un_fichier_isole_n_importe_rien_du_depot"),
    ("test_prose.py", "test_chaque_action_en_cours_s_ouvre_sur_son_bloc_reprise"),
    ("test_prose.py", "test_les_notes_de_la_feuille_de_route_se_rangent_par_action"),
    ("test_parcours.py", "test_aucun_compte_du_parcours_ne_s_ecrit_a_la_main"),
)


def test_les_gardes_d_une_seconde_sont_de_la_suite_rapide():
    """Ensemble, une seconde et demie : la suite rapide, que chaque session
    joue avant d'envoyer, les porte désormais."""
    assert [garde for garde in GARDES_RAPIDES if conftest.niveau(*garde) != "rapide"] == []


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
    absents = sorted(c for c in conftest.ISOLES if not (TESTS / c.split("::")[0]).is_file())
    absents += sorted(c for c in conftest.ISOLES if "::" in c
                      and c.split("::")[1] not in _fonctions(c.split("::")[0]))
    absents += sorted(c for lus in conftest.ISOLES.values() for c in lus
                      if not (racine / c).exists())
    assert not absents, f"{absents} : la table des fichiers isolés nomme des fichiers disparus"


def _arbre_isole(cle: str) -> ast.AST:
    """Le fichier isolé, ou la seule fonction du test isolé."""
    fichier, _, test = cle.partition("::")
    arbre = ast.parse((TESTS / fichier).read_text(encoding="utf-8"))
    if not test:
        return arbre
    return next(n for n in arbre.body if isinstance(n, ast.FunctionDef) and n.name == test)


def test_un_test_isole_ne_lit_rien_de_son_fichier():
    """Déclaré seul, un test ne demande aucune fixture ni ne lit aucun nom de
    son module, hors ``pytest`` et ``__file__`` : son fichier, qui lit le modèle, entre dans
    son empreinte, mais pas les modules qu'il importe."""
    for cle in (c for c in conftest.ISOLES if "::" in c):
        fonction = _arbre_isole(cle)
        assert not fonction.args.args, (cle, "demande une fixture")
        locaux = {n.id for n in ast.walk(fonction)
                  if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
        locaux |= {alias.asname or alias.name.split(".")[0] for n in ast.walk(fonction)
                   if isinstance(n, (ast.Import, ast.ImportFrom)) for alias in n.names}
        lus = {n.id for n in ast.walk(fonction)
               if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        lus |= {n.target.id for n in ast.walk(fonction) if isinstance(n, ast.comprehension)
                and isinstance(n.target, ast.Name)}
        externes = lus - locaux - set(dir(builtins))
        assert externes <= {"pytest", "__file__"}, (cle, sorted(externes))


def test_un_fichier_isole_n_importe_rien_du_depot():
    """Isolé, il ne lit que ce qu'il déclare : un import du modèle, ou d'un
    module des tests, ferait dépendre son résultat de ce que son empreinte
    ne lit pas. Déclaré seul, un test n'importe, lui, rien du dépôt."""
    for fichier in conftest.ISOLES:
        arbre = _arbre_isole(fichier)
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


def test_l_empreinte_d_un_test_isole_suit_les_dossiers_qu_il_lit(monkeypatch, tmp_path):
    """Un fichier retouché, né ou disparu, à toute profondeur du dossier
    déclaré, relance le test ; le test seul prime sur son fichier."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_isole.py").write_text("def test_x(): pass\n", encoding="utf-8")
    (tmp_path / "tests" / "conftest.py").write_text("", encoding="utf-8")
    (tmp_path / "moteur" / "js").mkdir(parents=True)
    (tmp_path / "moteur" / "js" / "a.js").write_text("1\n", encoding="utf-8")
    monkeypatch.setattr(conftest, "RACINE", tmp_path)
    monkeypatch.setattr(conftest, "ISOLES", {"test_isole.py::test_x": ("moteur",)})
    monkeypatch.setattr(conftest, "OUTILS_DES_ISOLES", ())
    assert conftest.cle_isolee("test_isole.py", "test_x") == "test_isole.py::test_x"
    assert conftest.cle_isolee("test_isole.py", "test_y") is None

    def empreinte():
        monkeypatch.setattr(conftest, "_EMPREINTES", {})
        return conftest.empreinte_isolee("test_isole.py::test_x")

    vues = [empreinte()]
    (tmp_path / "moteur" / "js" / "a.js").write_text("2\n", encoding="utf-8")
    vues.append(empreinte())
    (tmp_path / "moteur" / "js" / "b.js").write_text("", encoding="utf-8")
    vues.append(empreinte())
    (tmp_path / "moteur" / "js" / "b.js").unlink()
    (tmp_path / "moteur" / "js" / "c.js").write_text("", encoding="utf-8")
    vues.append(empreinte())
    (tmp_path / "moteur" / "js" / "c.js").unlink()
    (tmp_path / "moteur" / "js" / "__pycache__").mkdir()
    (tmp_path / "moteur" / "js" / "__pycache__" / "x.pyc").write_bytes(b"")
    assert len(set(vues)) == 4 and empreinte() == vues[1]
