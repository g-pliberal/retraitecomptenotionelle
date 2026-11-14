"""Le hook de l'outil Bash (`.claude/hooks/bash.py`, feuille de route,
action 135) : il refuse le `cat` d'un gros fichier texte, que le hook de
`Read` ne voit pas, à la même règle et au même seuil, et ne rend que la queue
d'un pytest lancé nu. Appelé comme Claude Code l'appelle : un appel
en JSON sur son entrée standard, la réponse sur sa sortie."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
HOOK = RACINE / ".claude" / "hooks" / "bash.py"
sys.path.insert(0, str(HOOK.parent))

import bash  # noqa: E402
import lecture  # noqa: E402


def _lancer(entree: str, comportement: str) -> str:
    sortie = subprocess.run([sys.executable, str(HOOK), comportement],
                            input=entree.encode("utf-8"), capture_output=True, check=True)
    return sortie.stdout.decode("utf-8")


def _appel(commande: str, dossier="/", **entree) -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": str(dossier),
            "tool_input": {"command": commande, **entree}}


@pytest.fixture
def dossier(tmp_path):
    """Un gros fichier texte, un petit, deux moyens qui ne passent le seuil
    qu'ensemble, et une grosse image."""
    (tmp_path / "gros.json").write_text("x" * (lecture.SEUIL + 1), encoding="utf-8")
    (tmp_path / "petit.md").write_text("x" * lecture.SEUIL, encoding="utf-8")
    for nom in ("moyen_a.txt", "moyen_b.txt"):
        (tmp_path / nom).write_text("x" * 30_000, encoding="utf-8")
    (tmp_path / "grosse.png").write_bytes(b"\0" * (lecture.SEUIL * 2))
    return tmp_path


def _refuse(commande: str, dossier) -> str | None:
    """La raison du refus, ou None si la commande passe."""
    reponse = bash.refus_du_cat(_appel(commande, dossier))
    if reponse is None:
        return None
    assert reponse["hookSpecificOutput"]["permissionDecision"] == "deny"
    return reponse["hookSpecificOutput"]["permissionDecisionReason"]


def test_le_cat_d_un_gros_fichier_est_refuse(dossier):
    appel = _appel(f"cat {dossier / 'gros.json'}")
    reponse = json.loads(_lancer(json.dumps(appel), "cat"))["hookSpecificOutput"]
    assert reponse["hookEventName"] == "PreToolUse"
    assert reponse["permissionDecision"] == "deny"
    raison = reponse["permissionDecisionReason"]
    assert "gros.json" in raison and "50 001 octets" in raison
    # Quoi faire à la place.
    assert "Grep" in raison and "sed -n" in raison and "limit" in raison


@pytest.mark.parametrize("commande", [
    "cat gros.json",                       # un chemin relatif au dossier de la session
    "cat -n gros.json",
    "cat -- gros.json",
    "LC_ALL=C cat gros.json",
    "cat petit.md gros.json",              # plusieurs fichiers
    "cat gro?.json",                       # un motif que le shell étend
    "cat < gros.json",
    "cat gros.json 2>/dev/null",           # l'erreur seule est détournée
    "cat gros.json >&2",
    "cd . && cat gros.json",               # dans une commande composée
    "echo debut; cat gros.json; echo fin",
    "echo debut\ncat gros.json\necho fin",
    "test -f gros.json || cat gros.json",
    "(cat gros.json)",
    "if true; then cat gros.json; fi",
    "wc -c petit.md | cat gros.json",      # au bout d'un tube, c'est lui qui écrit
    "cat 'gros.json'",
    "cat gros.json &",
])
def test_le_cat_est_vu_ou_qu_il_soit_dans_la_commande(dossier, commande):
    assert "gros.json" in _refuse(commande, dossier)


def test_plusieurs_fichiers_se_pesent_ensemble(dossier):
    """Ce qui entre dans le contexte, c'est ce que `cat` écrit : deux fichiers
    de 30 000 octets en font 60 000."""
    assert _refuse("cat moyen_a.txt", dossier) is None
    raison = _refuse("cat moyen_a.txt moyen_b.txt", dossier)
    assert "2 fichiers" in raison and "60 000 octets" in raison
    assert "60 000 octets" in _refuse("cat moyen_*.txt", dossier)


@pytest.mark.parametrize("commande", [
    "cat petit.md",
    "cat grosse.png",                      # ce que `lecture.py` ne tient pas pour du texte
    "cat absent.txt",
    'cat "$fichier"',                      # ce que le hook ne sait pas résoudre passe
    "cat gros.json | tail -n 30",          # la sortie va à une autre commande
    "cat gros.json | grep -c x",
    "cat gros.json 2>&1 | tail -n 30",
    "cat gros.json |& tail -n 30",
    "cat gros.json > copie.json",          # ou dans un fichier
    "cat gros.json >> copie.json",
    "cat gros.json 1> copie.json",
    "cat gros.json &> copie.json",
    "cat petit.md > gros.json",
    "taille=$(cat gros.json)",             # ou dans une variable
    'echo "$(cat gros.json | wc -c)"',
    "diff <(cat gros.json) petit.md",
    "echo 'cat gros.json'",                # un mot entre guillemets n'est pas une commande
    "grep -c cat gros.json",
    "wc -c gros.json",
    "/bin/cat gros.json",                  # ce que le champ `if` ne lance pas
    "cat > note.md <<'FIN'\ncat gros.json\nFIN",   # le texte d'un document en ligne
    "cat 'gros.json",                      # une commande que le hook ne sait pas lire
    "",
])
def test_le_reste_passe(dossier, commande):
    assert _refuse(commande, dossier) is None
    assert _lancer(json.dumps(_appel(commande, dossier)), "cat") == ""


def test_un_autre_outil_passe(dossier):
    appel = {**_appel("cat gros.json", dossier), "tool_name": "Read"}
    assert bash.refus_du_cat(appel) is None


@pytest.mark.parametrize("entree", ["", "pas du json", "[1, 2]", '{"tool_name": "Bash"}',
                                    '{"tool_name": "Bash", "tool_input": {"command": 3}}'])
def test_une_entree_illisible_laisse_passer(entree):
    assert _lancer(entree, "cat") == ""


def _declares() -> list[dict]:
    reglages = json.loads((RACINE / ".claude" / "settings.json").read_text(encoding="utf-8"))
    return [h for bloc in reglages["hooks"]["PreToolUse"]
            if bloc["matcher"] == "Bash" for h in bloc["hooks"]]


def test_le_refus_du_cat_est_declare_pour_bash():
    """Le champ `if` ne lance le script que si une sous-commande est un `cat`
    (https://code.claude.com/docs/en/hooks.md, « How `if` patterns match Bash
    commands »)."""
    [declare] = [h for h in _declares() if h.get("if") == "Bash(cat *)"]
    assert declare["command"].endswith('bash.py" cat')


# La queue d'un pytest nu (`CLAUDE.md`, « Les sorties longues passent par
# `tail` ou `grep` »).

def _recrite(commande: str, **entree) -> dict | None:
    reponse = bash.queue_des_sorties(_appel(commande, **entree))
    return None if reponse is None else reponse["hookSpecificOutput"]


@pytest.mark.parametrize("commande", [
    "python -m pytest",
    "python -m pytest -m rapide",
    "python -m pytest tests/test_hook_bash.py::test_un_autre_outil_passe -x -q",
    "python -m pytest -k 'cat and not tube'",
    "PYTEST_SANS_XDIST=1 python -m pytest -m site",
])
def test_un_pytest_lance_nu_passe_par_tail(commande):
    reponse = _recrite(commande, timeout=600_000, description="Lancer")
    assert reponse["hookEventName"] == "PreToolUse"
    # L'entrée entière est remplacée : ce que le hook ne change pas s'y recopie.
    assert reponse["updatedInput"] == {
        "command": f"set -o pipefail; {commande} 2>&1 | tail -n 30",
        "timeout": 600_000, "description": "Lancer"}
    # Le hook récrit sans approuver : la commande récrite garde son contrôle
    # de permission.
    assert "permissionDecision" not in reponse
    # La session ne voit pas sa commande changée : le hook le lui dit.
    assert "30 dernières lignes" in reponse["additionalContext"]


@pytest.mark.parametrize("commande", [
    "python -m pytest 2>&1 | tail -n 80",          # la session a choisi sa fenêtre
    "python -m pytest | grep -c passed",
    "python -m pytest > /tmp/sortie.txt",
    "python -m pytest 2>&1",
    "python -m pytest -m rapide && git commit -m x",   # une commande composée
    "cd moteur; python -m pytest",
    "python -m pytest &",
    "python -m pytest $(git diff --name-only)",
    "python -m pytest `ls tests`",
    "python -m pytest\npython -m pytest -m site",
    "python -m pytest # tout",
    "python -m pytestx",
    "python3 -m pytest",                           # ce que le champ `if` ne lance pas
    "pytest",
    "python scripts/regenerer.py",                 # l'accord du 14 novembre 2026 dit pytest
    "python scripts/resumer_temoins.py tests/temoins/carrieres.json",
    "python scripts/reprise.py 135",               # une sortie courte
    "python -c 'import pytest'",
    "echo python -m pytest",
    "",
])
def test_une_commande_composee_ou_deja_filtree_reste_telle_quelle(commande):
    assert _recrite(commande) is None
    assert _lancer(json.dumps(_appel(commande)), "queue") == ""


def test_la_commande_recrite_garde_son_code_de_sortie(tmp_path):
    """Un tube rend le code de sortie de `tail` : sans `pipefail`, un pytest
    rouge passerait pour vert. pytest sort en 1 quand un test échoue."""
    (tmp_path / "test_rouge.py").write_text(
        "def test_rouge():\n    for i in range(100):\n        print('ligne', i)\n"
        "    assert 1 == 2\n", encoding="utf-8")
    appel = _appel("python -m pytest test_rouge.py -p no:cacheprovider", tmp_path)
    recrite = json.loads(_lancer(json.dumps(appel), "queue"))["hookSpecificOutput"]
    # `python` est celui de la suite, que le poste ait ou non un `python`.
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "python").write_text(
        f'#!/bin/sh\nexec "{sys.executable}" "$@"\n', encoding="utf-8")
    (tmp_path / "bin" / "python").chmod(0o755)
    env = {**os.environ, "PATH": f"{tmp_path / 'bin'}{os.pathsep}{os.environ['PATH']}"}
    env = {nom: valeur for nom, valeur in env.items() if not nom.startswith("PYTEST_")}
    sortie = subprocess.run(["bash", "-c", recrite["updatedInput"]["command"]],
                            cwd=tmp_path, env=env, capture_output=True, text=True)
    assert sortie.returncode == 1
    lignes = sortie.stdout.splitlines()
    assert len(lignes) == 30 and "ligne 99" in lignes and "ligne 60" not in lignes
    assert "1 failed" in lignes[-1]


def test_un_cat_n_est_pas_recrit_et_un_pytest_n_est_pas_refuse(dossier):
    """Chaque déclaration ne lance que son comportement."""
    assert _lancer(json.dumps(_appel("cat gros.json", dossier)), "queue") == ""
    assert _lancer(json.dumps(_appel("python -m pytest", dossier)), "cat") == ""


def test_la_queue_est_declaree_pour_bash():
    """Un champ `if` ne tient qu'une règle : le script se lance sur toute
    commande `python`, et choisit."""
    [declare] = [h for h in _declares() if h.get("if") == "Bash(python *)"]
    assert declare["command"].endswith('bash.py" queue')
