"""Refuse de lire d'un bloc un gros fichier texte (feuille de route, action 135,
étape 2 du contexte).

Hook `PreToolUse` de Claude Code, pour l'outil `Read` : il reçoit l'appel en
JSON sur son entrée standard. Sans `limit`, un fichier texte de plus de
`SEUIL` octets est refusé, avec une raison que le modèle lit : chercher
d'abord, puis lire la fenêtre utile. Un seul `stat`, et jamais de blocage sur
une erreur : une entrée illisible, un fichier absent laissent passer.
"""

from __future__ import annotations

import json
import os
import sys

#: Au-delà, un fichier texte ne se lit que par fenêtre. Des octets, presque
#: égaux aux caractères ici.
SEUIL = 50_000

#: Ce que `Read` lit autrement que comme du texte.
NON_TEXTE = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".pdf", ".ipynb"}


def milliers(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def poids(chemin: str, dossier: str | None) -> int | None:
    """Les octets d'un fichier texte, lu depuis le dossier de la session, ou
    None : ce que `Read` lit autrement que comme du texte, un fichier absent."""
    if os.path.splitext(chemin)[1].lower() in NON_TEXTE:
        return None
    if not os.path.isabs(chemin):
        chemin = os.path.join(dossier or os.getcwd(), chemin)
    try:
        return os.stat(chemin).st_size
    except OSError:
        return None


def refus(raison: str) -> dict:
    """La réponse qui refuse l'appel, avec la raison que le modèle lit."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": raison,
        }
    }


def decision(appel: dict) -> dict | None:
    """La réponse du hook à un appel, ou None pour le laisser passer."""
    if appel.get("tool_name") != "Read":
        return None
    entree = appel.get("tool_input") or {}
    chemin = entree.get("file_path")
    if not isinstance(chemin, str) or not chemin or entree.get("limit"):
        return None
    taille = poids(chemin, appel.get("cwd"))
    if taille is None or taille <= SEUIL:
        return None
    return refus(
        f"{chemin} pèse {milliers(taille)} octets, plus de"
        f" {milliers(SEUIL)} : il ne se lit pas d'un bloc."
        " Chercher d'abord (outil Grep, avec -n), puis ne lire que la fenêtre"
        " utile, par Read avec offset et limit."
    )


def repondre(decision) -> int:
    """Lit l'appel sur l'entrée standard, écrit la réponse de `decision`."""
    try:
        appel = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except (ValueError, OSError):
        return 0
    reponse = decision(appel) if isinstance(appel, dict) else None
    if reponse is not None:
        sys.stdout.buffer.write(json.dumps(reponse, ensure_ascii=False).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(repondre(decision))
