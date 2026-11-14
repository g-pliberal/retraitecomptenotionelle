"""Refuse le `cat` d'un gros fichier texte, et ne rend que la queue d'un
pytest nu (feuille de route, action 135).

Hook `PreToolUse` de Claude Code, pour l'outil `Bash` : il reçoit l'appel en
JSON sur son entrée standard, et son argument nomme le comportement voulu,
que le champ `if` de sa déclaration réserve aux commandes qu'il regarde.

`cat` : un `cat` qui écrirait à la session plus de `lecture.SEUIL` octets de
fichiers texte est refusé, à la règle et au seuil du hook de `Read`
(`lecture.py`), avec une raison que le modèle lit. Le `cat` dont la sortie va
à un tube, à un fichier ou à une variable passe.

`queue` : un `python -m pytest` lancé nu est récrit pour ne rendre que ses
trente dernières lignes, avec son code de sortie.

Jamais de blocage sur un doute : une commande que le hook ne sait pas lire,
un chemin qu'il ne sait pas résoudre laissent passer.
"""

from __future__ import annotations

import glob
import os
import re
import shlex
import sys

import lecture

#: Les opérateurs du shell, les plus longs d'abord : `shlex` rend d'un bloc
#: une suite de signes (`);`, `)|`), qui se redécoupe ici.
OPERATEUR = re.compile(r"<<<|<<-?|&>>|&>|>>|>&|<&|>\||<>|\|\||&&|\|&|;;|[();<>|&\n]")
SIGNES = "();<>|&\n"

#: Ce qui finit une commande simple ; un tube envoie sa sortie à la suivante.
TUBES = {"|", "|&"}
FINS = {";", ";;", "&&", "||", "&", "\n", "(", ")"} | TUBES
#: Les redirections vers un fichier, et celles qui lisent.
VERS_UN_FICHIER = {">", ">>", ">|", "&>", "&>>"}
LECTURES = {"<", "<>", "<&", "<<<"}
#: Un document en ligne : son texte n'est pas une commande, la lecture s'arrête.
DOCUMENTS = {"<<", "<<-"}

#: Ce qui précède une commande sans en être une.
AFFECTATION = re.compile(r"[A-Za-z_]\w*=")
MOTS_CLES = {"do", "then", "else", "{", "!", "time"}


def _lexemes(commande: str):
    """Les mots et les opérateurs de la commande, des couples (texte,
    est_un_operateur), jusqu'à ce que `shlex` ne sache plus lire."""
    lecteur = shlex.shlex(commande, posix=True, punctuation_chars=SIGNES)
    lecteur.whitespace = " \t\r"
    lecteur.whitespace_split = True
    try:
        for mot in lecteur:
            if mot and all(signe in SIGNES for signe in mot):
                for operateur in OPERATEUR.findall(mot):
                    yield operateur, True
            else:
                yield mot, False
    except ValueError:
        return


def _fichiers_des_cat(commande: str) -> list[list[str]]:
    """Pour chaque `cat` de la commande qui écrit à la session, ses fichiers."""
    trouves: list[list[str]] = []
    mots: list[str] = []
    lus: list[str] = []
    detournee = False
    substitution = 0
    avant = ("", False)

    def finir(tube: bool) -> None:
        nonlocal mots, lus, detournee
        while mots and (AFFECTATION.match(mots[0]) or mots[0] in MOTS_CLES):
            mots = mots[1:]
        if mots and mots[0] == "cat" and not tube and not detournee:
            fichiers, options = [], True
            for mot in mots[1:]:
                if options and mot == "--":
                    options = False
                elif not (options and mot.startswith("-")):
                    fichiers.append(mot)
            trouves.append(fichiers + lus)
        mots, lus, detournee = [], [], False

    def descripteur() -> str | None:
        return mots.pop() if mots and mots[-1].isdigit() else None

    lexemes = _lexemes(commande)
    for texte, operateur in lexemes:
        precedent, avant = avant, (texte, operateur)
        if substitution:
            # `$(…)`, `<(…)` : ce qui s'y écrit ne va pas à la session.
            if operateur and texte in "()":
                substitution += 1 if texte == "(" else -1
        elif not operateur:
            mots.append(texte)
        elif texte == "(" and (precedent[0].endswith("$") and not precedent[1]
                               or precedent in {("<", True), (">", True)}):
            substitution = 1
        elif texte in DOCUMENTS:
            break
        elif texte in FINS:
            finir(texte in TUBES)
        else:
            de = descripteur()
            cible, cible_operateur = next(lexemes, ("", True))
            if cible_operateur:
                # `<(…)` : la cible est une substitution, relue au tour suivant.
                avant = (texte, True)
                if cible == "(":
                    substitution = 1
                continue
            if texte in VERS_UN_FICHIER or (
                    texte == ">&" and not cible.isdigit() and cible != "-"):
                detournee = detournee or texte.startswith("&") or de in (None, "1")
            elif texte == "<" and de in (None, "0"):
                lus.append(cible)
    finir(False)
    return trouves


def _chemins(fichier: str, dossier: str | None) -> list[tuple[str, str]]:
    """Le fichier, ou ceux que le shell tirerait de son motif : le nom à dire
    et le chemin à peser."""
    dossier = dossier or os.getcwd()
    chemin = os.path.join(dossier, os.path.expanduser(fichier))
    if not any(signe in fichier for signe in "*?["):
        return [(fichier, chemin)]
    return [(os.path.relpath(trouve, dossier), trouve) for trouve in sorted(glob.glob(chemin))]


def refus_du_cat(appel: dict) -> dict | None:
    """Le refus d'un `cat` qui écrirait un gros fichier texte à la session, ou
    None pour laisser passer l'appel."""
    if appel.get("tool_name") != "Bash":
        return None
    commande = (appel.get("tool_input") or {}).get("command")
    if not isinstance(commande, str) or "cat" not in commande:
        return None
    dossier = appel.get("cwd")
    for fichiers in _fichiers_des_cat(commande):
        pesees = [(lecture.poids(chemin, dossier), nom)
                  for fichier in fichiers for nom, chemin in _chemins(fichier, dossier)]
        pesees = [(taille, nom) for taille, nom in pesees if taille]
        total = sum(taille for taille, _ in pesees)
        if total <= lecture.SEUIL:
            continue
        if len(pesees) == 1:
            quoi = f"{pesees[0][1]} pèse {lecture.milliers(total)} octets"
        else:
            quoi = (f"{len(pesees)} fichiers ({max(pesees)[1]} est le plus gros)"
                    f" pèsent ensemble {lecture.milliers(total)} octets")
        return lecture.refus(
            f"cat : {quoi}, plus de {lecture.milliers(lecture.SEUIL)} : cela ne"
            " se lit pas d'un bloc. Chercher d'abord (outil Grep, avec -n), puis"
            " ne lire que la fenêtre utile, par Read avec offset et limit ou par"
            " sed -n 'debut,finp'."
        )
    return None


#: Un pytest lancé nu : ni tube, ni redirection, ni commande composée, ni rien
#: que le shell étendrait. Le motif est celui de
#: https://code.claude.com/docs/en/costs.md, « Offload processing to hooks and
#: skills ». `python` seul : le champ `if` de la déclaration, `Bash(python *)`,
#: ne lance pas le script sur `python3` ni sur `pytest`.
LONGUE = re.compile(
    r"(?:[A-Za-z_]\w*=[\w./:-]* )*"
    r"python -m pytest"
    r"(?: [^;&|<>`$#\\\x00-\x1f\x7f]*)?"
)
QUEUE = 30


def queue_des_sorties(appel: dict) -> dict | None:
    """L'appel récrit pour ne rendre que la queue d'un pytest nu, ou None
    pour le laisser tel quel. `pipefail` garde à la commande son code de
    sortie, que le tube donnerait à `tail`."""
    if appel.get("tool_name") != "Bash":
        return None
    entree = appel.get("tool_input") or {}
    commande = entree.get("command")
    if not isinstance(commande, str) or not LONGUE.fullmatch(commande.strip()):
        return None
    recrite = f"set -o pipefail; {commande.strip()} 2>&1 | tail -n {QUEUE}"
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {**entree, "command": recrite},
            "additionalContext": (
                f"Hook : sortie réduite à ses {QUEUE} dernières lignes"
                f" (`2>&1 | tail -n {QUEUE}`, code de sortie gardé) ; pour en"
                " voir plus, écrire soi-même le tube."
            ),
        }
    }


COMPORTEMENTS = {"cat": refus_du_cat, "queue": queue_des_sorties}


def decision(appel: dict, comportements=tuple(COMPORTEMENTS)) -> dict | None:
    """La réponse du premier comportement qui en a une."""
    for nom in comportements:
        reponse = COMPORTEMENTS[nom](appel) if nom in COMPORTEMENTS else None
        if reponse is not None:
            return reponse
    return None


if __name__ == "__main__":
    voulus = tuple(sys.argv[1:]) or tuple(COMPORTEMENTS)
    sys.exit(lecture.repondre(lambda appel: decision(appel, voulus)))
