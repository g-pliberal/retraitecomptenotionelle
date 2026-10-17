"""Rappelle d'écrire le test, et de le voir échouer, avant de toucher au code
(`CLAUDE.md`, « Travailler » : le test d'abord ; feuille de route, action 162).

Hook `PreToolUse` de Claude Code, pour `Edit` et `Write` : il reçoit l'appel
en JSON sur son entrée standard. Une retouche du code du dépôt (`CODE`) est
refusée une fois, avec une raison que le modèle lit, quand aucun test n'a été
vu échouer depuis le dernier commit. Refaite telle quelle, elle passe : un
remaniement ou un commentaire n'ont pas de test neuf. Le rappel ne revient
qu'au commit suivant, ou dans une autre session.

Le rouge vu, c'est pytest qui le dit : une séance qui échoue pendant qu'un
test s'écrit — un fichier de `tests/` changé dans le dossier de travail, hors
des fichiers fabriqués, que `.gitattributes` marque `-merge` — le note par
`noter_le_rouge`, que `tests/conftest.py` appelle au bout de chaque séance.
Les deux marques tiennent une ligne chacune, sous `.cache/`, que git ignore.
Jamais de blocage sur une erreur : une entrée illisible, un fichier hors d'un
dépôt, un git absent laissent passer.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

#: Le code du dépôt, par dossier et par extension : ce qui ne se touche
#: qu'après un test vu rouge. Les tests, la prose, les données et le style
#: n'en sont pas.
CODE = {
    "src": (".py",),
    "moteur": (".js", ".mjs"),
    "scripts": (".py", ".sh", ".mjs"),
    ".claude/hooks": (".py", ".sh"),
}

#: Le commit auquel pytest a vu le rouge ; la session et le commit du dernier
#: rappel.
ROUGE = ".cache/tdd/rouge"
RAPPEL = ".cache/tdd/rappel"

RAISON = (
    "Le test d'abord (CLAUDE.md, « Travailler ») : aucun test n'a été vu"
    " échouer depuis le dernier commit. Écrire d'abord le test qui dit le"
    " comportement attendu, sa valeur tirée de la source et non du code, le"
    " lancer seul (python -m pytest tests/<fichier>.py::<test>) et le voir"
    " rouge pour la raison attendue ; puis revenir au code. Une retouche qui ne"
    " change aucun comportement (remaniement sous des tests verts, commentaire,"
    " message), ou dont le rouge s'est vu hors de pytest (node --test), se"
    " refait telle quelle : ce rappel ne revient qu'après le prochain commit."
)

_EXTENSIONS = tuple(sorted({e for extensions in CODE.values() for e in extensions}))


def _git(dossier: str, *arguments: str) -> str | None:
    """La sortie d'un git lancé dans ce dossier, ou None s'il échoue. Sans
    verrou facultatif : il ne réécrit pas l'index d'un git qui tourne."""
    try:
        acheve = subprocess.run(["git", "--no-optional-locks", "-C", dossier, *arguments],
                                capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return None if acheve.returncode else acheve.stdout.decode("utf-8", "replace")


def _depot(dossier: str) -> tuple[str, str] | None:
    """La racine du dépôt qui contient ce dossier, et son commit."""
    lignes = (_git(dossier, "rev-parse", "--show-toplevel", "HEAD") or "").splitlines()
    return (lignes[0], lignes[1]) if len(lignes) >= 2 else None


def _lire(racine: str, marque: str) -> str:
    try:
        with open(os.path.join(racine, marque), encoding="utf-8") as fichier:
            return fichier.read().strip()
    except OSError:
        return ""


def _ecrire(racine: str, marque: str, texte: str) -> None:
    chemin = os.path.join(racine, marque)
    try:
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8") as fichier:
            fichier.write(texte + "\n")
    except OSError:
        pass


def _tests_qui_s_ecrivent(racine: str) -> list[str]:
    """Les fichiers de `tests/` changés dans le dossier de travail, nouveaux
    compris, hors des fabriqués."""
    champs = (_git(racine, "status", "--porcelain", "-z", "--untracked-files=all",
                   "--", "tests") or "").split("\0")
    chemins, rang = [], 0
    while rang < len(champs):
        entree = champs[rang]
        rang += 1
        if len(entree) > 3:
            chemins.append(entree[3:])
            if {"R", "C"} & set(entree[:2]):
                rang += 1                   # le nom d'avant le renommage
    if not chemins:
        return []
    attributs = (_git(racine, "check-attr", "-z", "merge", "--", *chemins) or "").split("\0")
    fabriques = {attributs[i] for i in range(0, len(attributs) - 2, 3)
                 if attributs[i + 2] == "unset"}
    return [chemin for chemin in chemins if chemin not in fabriques]


def noter_le_rouge(dossier) -> bool:
    """Au bout d'une séance de pytest qui a échoué : si un test s'écrit dans
    le dépôt de ce dossier, le rouge est vu à son commit. Rend True s'il l'est."""
    depot = _depot(os.fspath(dossier))
    if depot is None or not _tests_qui_s_ecrivent(depot[0]):
        return False
    _ecrire(depot[0], ROUGE, depot[1])
    return True


def decision(appel: dict) -> dict | None:
    """La réponse du hook à un appel, ou None pour le laisser passer."""
    if appel.get("tool_name") not in ("Edit", "Write"):
        return None
    entree = appel.get("tool_input")
    chemin = entree.get("file_path") if isinstance(entree, dict) else None
    if not isinstance(chemin, str) or not chemin.endswith(_EXTENSIONS):
        return None
    if not os.path.isabs(chemin):
        chemin = os.path.join(appel.get("cwd") or os.getcwd(), chemin)
    chemin = os.path.realpath(chemin)
    dossier = os.path.dirname(chemin)
    while not os.path.isdir(dossier):       # un fichier neuf, dans un dossier neuf
        if os.path.dirname(dossier) == dossier:
            return None
        dossier = os.path.dirname(dossier)
    depot = _depot(dossier)
    if depot is None:
        return None
    racine, tete = depot
    try:
        relatif = os.path.relpath(chemin, os.path.realpath(racine)).replace(os.sep, "/")
    except ValueError:                      # un autre lecteur, sous Windows
        return None
    if not any(relatif.startswith(f"{sous}/") and relatif.endswith(extensions)
               for sous, extensions in CODE.items()):
        return None
    rappel = f"{appel.get('session_id') or '-'} {tete}"
    if _lire(racine, ROUGE) == tete or _lire(racine, RAPPEL) == rappel:
        return None
    _ecrire(racine, RAPPEL, rappel)
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": RAISON,
        }
    }


def main() -> int:
    try:
        appel = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (ValueError, OSError):
        return 0
    reponse = decision(appel) if isinstance(appel, dict) else None
    if reponse is not None:
        sys.stdout.buffer.write(json.dumps(reponse, ensure_ascii=False).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
