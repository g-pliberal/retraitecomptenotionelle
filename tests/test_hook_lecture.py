"""Le hook qui refuse de lire d'un bloc un gros fichier texte
(`.claude/hooks/lecture.py`, feuille de route, action 135, étape 2 du
contexte), appelé comme Claude Code l'appelle : un appel en JSON sur son entrée
standard, la réponse sur sa sortie."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
HOOK = RACINE / ".claude" / "hooks" / "lecture.py"
sys.path.insert(0, str(HOOK.parent))

import lecture  # noqa: E402


def _lancer(entree: str) -> str:
    sortie = subprocess.run([sys.executable, str(HOOK)], input=entree.encode("utf-8"),
                            capture_output=True, check=True)
    return sortie.stdout.decode("utf-8")


def _appel(chemin, **entree) -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": "Read", "cwd": "/",
            "tool_input": {"file_path": str(chemin), **entree}}


@pytest.fixture
def gros(tmp_path):
    chemin = tmp_path / "gros.json"
    chemin.write_text("x" * (lecture.SEUIL + 1), encoding="utf-8")
    return chemin


def test_un_gros_fichier_texte_lu_d_un_bloc_est_refuse(gros):
    reponse = json.loads(_lancer(json.dumps(_appel(gros))))["hookSpecificOutput"]
    assert reponse["hookEventName"] == "PreToolUse"
    assert reponse["permissionDecision"] == "deny"
    raison = reponse["permissionDecisionReason"]
    assert "50 001 octets" in raison and "offset" in raison and "limit" in raison


@pytest.mark.parametrize("cas", ["fenetre", "petit", "image", "absent", "autre_outil"])
def test_le_reste_passe(gros, tmp_path, cas):
    petit = tmp_path / "petit.md"
    petit.write_text("x" * lecture.SEUIL, encoding="utf-8")
    image = tmp_path / "grosse.png"
    image.write_bytes(b"\0" * (lecture.SEUIL * 2))
    appel = {
        "fenetre": _appel(gros, offset=1, limit=100),
        "petit": _appel(petit),
        "image": _appel(image),
        "absent": _appel(tmp_path / "absent.txt"),
        "autre_outil": {**_appel(gros), "tool_name": "Edit"},
    }[cas]
    assert _lancer(json.dumps(appel)) == ""


def test_un_chemin_relatif_se_lit_depuis_le_dossier_de_la_session(gros):
    appel = {**_appel(gros.name), "cwd": str(gros.parent)}
    assert lecture.decision(appel)["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize("entree", ["", "pas du json", "[1, 2]", '{"tool_name": "Read"}'])
def test_une_entree_illisible_laisse_passer(entree):
    assert _lancer(entree) == ""


def test_le_hook_est_declare_pour_read():
    reglages = json.loads((RACINE / ".claude" / "settings.json").read_text(encoding="utf-8"))
    declares = [h["command"] for bloc in reglages["hooks"]["PreToolUse"]
                if bloc["matcher"] == "Read" for h in bloc["hooks"]]
    assert any("lecture.py" in commande for commande in declares)
