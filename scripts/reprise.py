#!/usr/bin/env python3
"""Le bloc « Reprise » de chaque action en cours, et ceux de ses étapes.

    python scripts/reprise.py          # toutes les actions en cours
    python scripts/reprise.py 138      # une action

Une session qui cherche quoi faire ne lit que ces blocs (``CLAUDE.md``,
« Économiser le contexte »). Chaque action `en cours` de
``docs/feuille_de_route.md`` s'ouvre sur le sien. Ses notes, une par fichier
depuis l'action 148, sont dans ``docs/feuille_de_route/<numéro>/`` ; quand
ses étapes se mènent en parallèle, chacune tient son propre bloc, en tête du
fichier de sa note, tant qu'elle n'est pas finie. Ce script met ces blocs
bout à bout, avec la liste des notes de chaque action, sans rien lire
d'autre ; ``tests/test_prose.py`` en tient la forme.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
FEUILLE = "docs/feuille_de_route.md"
#: Les notes des actions ouvertes, un dossier par action ; celles des actions
#: closes passent, avec leur dossier, sous ``docs/archives/feuille_de_route/``.
NOTES = "docs/feuille_de_route"
ARCHIVE_DES_NOTES = "docs/archives/feuille_de_route"

TITRE_D_ACTION = re.compile(r"^### (\d+)\. (.*) — `([^`]+)`\s*$", re.M)
#: Le nom d'une note : sa date, puis son sujet (« etape-2 »), sans majuscule
#: ni accent.
NOM_DE_NOTE = re.compile(r"(\d{4}-\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md")


@dataclass
class Action:
    numero: str
    titre: str
    etat: str
    ligne: int
    #: Le premier paragraphe sous le titre, qui doit être le bloc « Reprise ».
    ouverture: list[str]


def paragraphe(lignes: list[str], debut: int) -> list[str]:
    """Le paragraphe qui commence à la ligne ``debut`` (comptée depuis 0)."""
    fin = debut
    while fin < len(lignes) and lignes[fin].strip():
        fin += 1
    return lignes[debut:fin]


def actions(texte: str) -> list[Action]:
    """Les actions de la feuille de route, chacune avec son premier paragraphe."""
    lignes = texte.split("\n")
    sortie = []
    for trouve in TITRE_D_ACTION.finditer(texte):
        numero = texte.count("\n", 0, trouve.start())
        suite = numero + 1
        while suite < len(lignes) and not lignes[suite].strip():
            suite += 1
        ouverture = [] if suite >= len(lignes) or lignes[suite].startswith("#") else (
            paragraphe(lignes, suite))
        sortie.append(Action(trouve.group(1), trouve.group(2), trouve.group(3),
                             numero + 1, ouverture))
    return sortie


def reprise_d_une_note(texte: str) -> list[str]:
    """Le bloc « Reprise » d'une étape en cours, en tête de sa note ; vide si
    la note n'en porte pas, c'est-à-dire si l'étape est finie."""
    lignes = texte.split("\n")
    for numero, ligne in enumerate(lignes):
        if ligne.startswith("**Reprise"):
            return paragraphe(lignes, numero)
    return []


def notes(numero: str, racine: Path = RACINE) -> list[Path]:
    """Les notes d'une action ouverte, dans l'ordre de leurs dates."""
    dossier = racine / NOTES / numero
    return sorted(dossier.glob("*.md")) if dossier.is_dir() else []


def titre_d_une_note(texte: str) -> str:
    premiere = texte.split("\n", 1)[0]
    return premiere[2:].strip() if premiere.startswith("# ") else premiere.strip()


def imprimer(action: Action, racine: Path = RACINE) -> list[str]:
    sortie = [f"### {action.numero}. {action.titre} — `{action.etat}`",
              f"({FEUILLE}:{action.ligne})", "", *action.ouverture]
    fichiers = notes(action.numero, racine)
    if not fichiers:
        return sortie
    en_cours = []
    sortie += ["", f"Notes, dans {NOTES}/{action.numero}/ :"]
    for chemin in fichiers:
        texte = chemin.read_text(encoding="utf-8")
        sortie.append(f"  {chemin.name} — {titre_d_une_note(texte)}")
        bloc = reprise_d_une_note(texte)
        if bloc:
            en_cours.append((chemin, bloc))
    for chemin, bloc in en_cours:
        sortie += ["", f"Étape en cours, {chemin.relative_to(racine).as_posix()} :", *bloc]
    return sortie


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("numeros", nargs="*", help="les actions à imprimer (toutes par défaut)")
    arguments = analyseur.parse_args(argv)
    texte = (RACINE / FEUILLE).read_text(encoding="utf-8")
    choisies = [a for a in actions(texte) if a.etat == "en cours"
                and (not arguments.numeros or a.numero in arguments.numeros)]
    if not choisies:
        print("Aucune action en cours sous ces numéros.")
        return 1
    blocs = ["\n".join(imprimer(action)) for action in choisies]
    print("\n\n".join(blocs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
