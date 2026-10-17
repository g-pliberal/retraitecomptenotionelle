"""Le test d'abord (`CLAUDE.md`, « Travailler » ; feuille de route, action
162) : le hook qui rappelle, avant de toucher au code, d'écrire le test et de
le voir échouer (`.claude/hooks/tdd.py`), et ce que pytest lui dit du rouge vu
(`tests/conftest.py`). Le hook est appelé comme Claude Code l'appelle, un
appel en JSON sur son entrée standard, la réponse sur sa sortie, dans un dépôt
git monté dans un dossier temporaire."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import conftest

RACINE = Path(__file__).resolve().parents[1]
HOOK = RACINE / ".claude" / "hooks" / "tdd.py"
sys.path.insert(0, str(HOOK.parent))

import tdd  # noqa: E402


def _git(depot: Path, *arguments: str) -> None:
    subprocess.run(["git", "-C", str(depot), "-c", "user.name=essai",
                    "-c", "user.email=essai@example.invalid", "-c", "commit.gpgsign=false",
                    *arguments], capture_output=True, check=True)


def _commit(depot: Path, message: str) -> None:
    _git(depot, "add", "-A")
    _git(depot, "commit", "-q", "-m", message)


@pytest.fixture(scope="module")
def modele(tmp_path_factory):
    """Un dépôt réduit à ce que le hook regarde : un module du modèle, son
    test, un témoin fabriqué (``-merge``), une note. Monté une fois, copié
    pour chaque test : un git coûte cher sous Windows."""
    racine = tmp_path_factory.mktemp("modele") / "depot"
    for chemin, texte in {
        "src/regle.py": "def taux():\n    return 1\n",
        "tests/test_regle.py": "def test_taux():\n    assert True\n",
        "tests/temoins/pages.json": "{}\n",
        "docs/note.md": "# Note\n",
        ".gitattributes": "tests/temoins/pages.json -merge\n",
        ".gitignore": ".cache/\n",
    }.items():
        (racine / chemin).parent.mkdir(parents=True, exist_ok=True)
        (racine / chemin).write_text(texte, encoding="utf-8")
    _git(racine, "init", "-q")
    _commit(racine, "départ")
    return racine


@pytest.fixture
def depot(modele, tmp_path):
    return Path(shutil.copytree(modele, tmp_path / "depot"))


def _appel(chemin: Path, outil: str = "Edit", seance: str = "s1") -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": outil, "session_id": seance,
            "cwd": "/", "tool_input": {"file_path": str(chemin)}}


def _lancer(entree: str) -> str:
    sortie = subprocess.run([sys.executable, str(HOOK)], input=entree.encode("utf-8"),
                            capture_output=True, check=True)
    return sortie.stdout.decode("utf-8")


def _refuse(reponse: dict | None) -> bool:
    return bool(reponse) and reponse["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_le_code_touche_sans_rouge_vu_est_refuse_une_fois_par_commit(depot):
    code = depot / "src" / "regle.py"
    reponse = json.loads(_lancer(json.dumps(_appel(code))))["hookSpecificOutput"]
    assert reponse["hookEventName"] == "PreToolUse"
    assert reponse["permissionDecision"] == "deny"
    raison = reponse["permissionDecisionReason"]
    assert "test" in raison and "rouge" in raison and "python -m pytest" in raison
    # Refaite telle quelle, la retouche passe : un remaniement n'a pas de test neuf.
    assert _lancer(json.dumps(_appel(code))) == ""
    # Une autre session a son propre rappel.
    assert _refuse(tdd.decision(_appel(code, seance="s2")))
    # Le commit clôt le cycle : la retouche suivante rouvre le suivant.
    code.write_text("def taux():\n    return 2\n", encoding="utf-8")
    _commit(depot, "remaniement")
    assert _refuse(tdd.decision(_appel(code, seance="s2")))


@pytest.mark.parametrize("ecrit", ["tests/test_regle.py", "tests/js/neuf.test.js"])
def test_un_rouge_vu_pendant_qu_un_test_s_ecrit_laisse_toucher_au_code(depot, ecrit):
    (depot / ecrit).parent.mkdir(parents=True, exist_ok=True)
    (depot / ecrit).write_text("// le comportement attendu, qui échoue\n", encoding="utf-8")
    assert tdd.noter_le_rouge(depot)
    code = depot / "src" / "regle.py"
    assert tdd.decision(_appel(code)) is None
    assert tdd.decision(_appel(depot / "src" / "neuf" / "module.py", outil="Write")) is None
    _commit(depot, "le comportement, vert")
    assert _refuse(tdd.decision(_appel(code)))


def test_un_temoin_fabrique_n_est_pas_un_test_qui_s_ecrit(depot):
    assert not tdd.noter_le_rouge(depot)
    (depot / "tests" / "temoins" / "pages.json").write_text('{"page": 1}\n', encoding="utf-8")
    assert not tdd.noter_le_rouge(depot)
    assert _refuse(tdd.decision(_appel(depot / "src" / "regle.py")))


@pytest.mark.parametrize("chemin", [
    "src/regle.py", "src/neuf/module.py", "moteur/js/pages.js", "moteur/js/essai.mjs",
    "scripts/outil.py", "scripts/pousser.sh", ".claude/hooks/lecture.py"])
def test_le_code_du_depot_est_garde(depot, chemin):
    assert _refuse(tdd.decision(_appel(depot / chemin, outil="Write")))


@pytest.mark.parametrize("cas", ["test", "prose", "donnee", "style", "hors_depot", "autre_outil"])
def test_le_reste_passe(depot, tmp_path, cas):
    appel = {
        "test": _appel(depot / "tests" / "test_regle.py"),
        "prose": _appel(depot / "docs" / "note.md"),
        "donnee": _appel(depot / "data" / "regles" / "taux.yaml", outil="Write"),
        "style": _appel(depot / "moteur" / "style.css"),
        "hors_depot": _appel(tmp_path / "brouillon.py", outil="Write"),
        "autre_outil": {**_appel(depot / "src" / "regle.py"), "tool_name": "Read"},
    }[cas]
    assert _lancer(json.dumps(appel)) == ""


def test_un_chemin_relatif_se_lit_depuis_le_dossier_de_la_session(depot):
    appel = {**_appel(Path("src") / "regle.py"), "cwd": str(depot)}
    assert _refuse(tdd.decision(appel))


@pytest.mark.parametrize("entree", ["", "pas du json", "[1, 2]", '{"tool_name": "Edit"}'])
def test_une_entree_illisible_laisse_passer(entree):
    assert _lancer(entree) == ""


def test_une_seance_de_pytest_qui_echoue_note_le_rouge(depot):
    """Le maître seul, sous xdist, et seulement quand un test a échoué."""
    (depot / "tests" / "test_regle.py").write_text("def test_taux():\n    assert False\n",
                                                  encoding="utf-8")
    code = _appel(depot / "src" / "regle.py")
    verte = SimpleNamespace(testsfailed=0, config=SimpleNamespace(rootpath=depot))
    ouvriere = SimpleNamespace(testsfailed=1,
                               config=SimpleNamespace(rootpath=depot, workerinput={}))
    for seance in (verte, ouvriere):
        conftest.pytest_sessionfinish(seance, 0)
    assert _refuse(tdd.decision(code))
    rouge = SimpleNamespace(testsfailed=1, config=SimpleNamespace(rootpath=depot))
    conftest.pytest_sessionfinish(rouge, 1)
    assert tdd.decision({**code, "session_id": "s2"}) is None


def test_le_hook_est_declare_pour_edit_et_write():
    reglages = json.loads((RACINE / ".claude" / "settings.json").read_text(encoding="utf-8"))
    declares = [h["command"] for bloc in reglages["hooks"]["PreToolUse"]
                if {"Edit", "Write"} <= set(bloc["matcher"].split("|"))
                for h in bloc["hooks"]]
    assert any("tdd.py" in commande for commande in declares)


def test_le_code_garde_est_celui_du_depot_et_ses_marques_ne_se_commitent_pas():
    for dossier in tdd.CODE:
        assert (RACINE / dossier).is_dir(), dossier
    for marque in (tdd.ROUGE, tdd.RAPPEL):
        ignore = subprocess.run(["git", "-C", str(RACINE), "check-ignore", "-q", marque])
        assert ignore.returncode == 0, marque
