#!/usr/bin/env python3
"""Le bloc « Reprise » d'une action en cours, et ceux de ses étapes.

    python scripts/reprise.py              # le sommaire des actions en cours
    python scripts/reprise.py 138          # une action : ses blocs, ses dernières notes
    python scripts/reprise.py 138 --toutes # la même, toutes ses notes listées

Une session qui cherche quoi faire ne lit que ces blocs (``CLAUDE.md``,
« Économiser le contexte »). Chaque action `en cours` de
``docs/feuille_de_route.md`` s'ouvre sur le sien. Ses notes, une par fichier
depuis l'action 148, sont dans ``docs/feuille_de_route/<numéro>/`` ; quand
ses étapes se mènent en parallèle, chacune tient son propre bloc, en tête du
fichier de sa note, tant qu'elle n'est pas finie. Ce script met bout à bout
les blocs d'une action, sans rien lire d'autre ; ``tests/test_prose.py`` en
tient la forme et la mesure, que :func:`fautes_d_un_bloc` dit.

Ce qu'il imprime doit entrer en entier dans le contexte de la session qui le
lance, et l'outil Bash écarte une sortie de :data:`SORTIE_AU_PLUS` caractères
(action 135, notes du 13 novembre 2026). Sans numéro, il n'imprime donc que
le sommaire, une ligne par action ; avec un numéro, il ne liste que les
:data:`NOTES_LISTEES` dernières notes, sauf ``--toutes``.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from dataclasses import dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
FEUILLE = "docs/feuille_de_route.md"
#: Les actions closes, que la feuille de route ne porte plus.
ARCHIVE = "docs/archives/feuille_de_route.md"
#: Les notes des actions ouvertes, un dossier par action ; celles des actions
#: closes passent, avec leur dossier, sous ``docs/archives/feuille_de_route/``.
NOTES = "docs/feuille_de_route"
ARCHIVE_DES_NOTES = "docs/archives/feuille_de_route"

TITRE_D_ACTION = re.compile(r"^### (\d+)\. (.*) — `([^`]+)`\s*$", re.M)
#: Les états d'une action, le mot entre accents graves de son titre, et nul
#: autre (action 190, étape 4) : à faire, puis en cours, puis clos — fait,
#: abandonnée ou archivée —, l'action passant alors à l'archive. Le tableau
#: de bord, la conservation et ``tests/test_prose.py`` les lisent ici.
A_FAIRE = "à faire"
EN_COURS = "en cours"
CLOS = ("fait", "abandonnée", "archivée")
ETATS = (A_FAIRE, EN_COURS, *CLOS)
#: Le nom d'une note : sa date, puis son sujet (« etape-2 »), sans majuscule
#: ni accent.
NOM_DE_NOTE = re.compile(r"(\d{4}-\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md")
#: L'ouverture d'un bloc « Reprise », avec sa date : « **Reprise, au
#: 1er décembre 2026.** ».
OUVERTURE = re.compile(r"\*\*Reprise, au (\d{1,2})(?:er)? (\w+) (\d{4})\.\*\*")
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre")
#: La mesure d'un bloc « Reprise » (``CLAUDE.md``, « Économiser le
#: contexte » ; action 135, note du 11 novembre 2026 sur le bloc lisible) :
#: 150 mots au plus, en lignes de largeur ordinaire. Les « dix lignes au
#: plus » d'avant se tenaient à la lettre par des lignes de plus de mille
#: caractères ; un bloc daté d'avant la règle les garde, jusqu'à ce que la
#: session qui avance son action le récrive, daté du jour.
MOTS_AU_PLUS = 150
LARGEUR_AU_PLUS = 100
EN_MOTS_DEPUIS = datetime.date(2026, 11, 11)
LIGNES_D_AVANT = 10
#: Ce que l'outil Bash d'une session laisse entrer d'une sortie, en
#: caractères : au-delà, il la range dans un fichier et n'en montre que les
#: deux premiers kilo-octets. Constaté le 13 novembre 2026 à 31 000
#: caractères ; 30 000 est la valeur par défaut de Claude Code.
SORTIE_AU_PLUS = 30_000
#: Les notes qu'une action liste, les plus récentes : les 272 de l'action 138
#: portaient sa sortie à 58 916 caractères.
NOTES_LISTEES = 30


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


def etats_inconnus(texte: str) -> list[str]:
    """Les titres d'action, ``### <numéro>.``, dont l'état n'est pas l'un de
    :data:`ETATS` ou ne s'écrit pas entre accents graves : une telle action
    ne serait ni ouverte ni close."""
    return [ligne for ligne in re.findall(r"^### \d+\..*$", texte, re.M)
            if not (trouve := TITRE_D_ACTION.match(ligne)) or trouve.group(3) not in ETATS]


def mots(bloc: list[str]) -> int:
    """Les mots d'un bloc : ce qu'un blanc sépare, sans la ponctuation isolée
    (« : », « ; », le tiret, les guillemets)."""
    return len([mot for mot in " ".join(bloc).split() if re.search(r"\w", mot)])


def date_d_un_bloc(bloc: list[str]) -> datetime.date | None:
    """La date qui ouvre un bloc « Reprise » ; ``None`` s'il ne s'ouvre pas
    sur « **Reprise, au <jour> <mois> <année>.** »."""
    trouve = OUVERTURE.match(bloc[0]) if bloc else None
    if not trouve or trouve.group(2) not in MOIS:
        return None
    try:
        return datetime.date(int(trouve.group(3)), MOIS.index(trouve.group(2)) + 1,
                             int(trouve.group(1)))
    except ValueError:
        return None


def fautes_d_un_bloc(bloc: list[str]) -> list[str]:
    """Ce qu'un bloc « Reprise », donné par ses lignes, enfreint : sa forme,
    puis sa mesure, celle de la règle en vigueur à sa date."""
    date = date_d_un_bloc(bloc)
    if date is None:
        return ["ne s'ouvre pas sur « **Reprise, au <jour> <mois> <année>.** »"]
    if date < EN_MOTS_DEPUIS:
        if len(bloc) > LIGNES_D_AVANT:
            return [f"{len(bloc)} lignes de reprise, {LIGNES_D_AVANT} au plus"]
        return []
    fautes = []
    if mots(bloc) > MOTS_AU_PLUS:
        fautes.append(f"{mots(bloc)} mots de reprise, {MOTS_AU_PLUS} au plus : "
                      "ce qui ne tient pas va dans la note")
    large = max(map(len, bloc))
    if large > LARGEUR_AU_PLUS:
        fautes.append(f"une ligne de {large} caractères, {LARGEUR_AU_PLUS} au plus : "
                      "la couper comme le reste de la prose")
    return fautes


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


def etapes_en_cours(fichiers: list[Path]) -> list[tuple[Path, list[str]]]:
    """Les notes qui portent un bloc « Reprise », chacune avec le sien."""
    blocs = [(chemin, reprise_d_une_note(chemin.read_text(encoding="utf-8")))
             for chemin in fichiers]
    return [(chemin, bloc) for chemin, bloc in blocs if bloc]


def ligne_du_sommaire(action: Action, racine: Path = RACINE) -> str:
    """Une action en une ligne : son numéro, son titre, la date de son bloc,
    ses notes et ses étapes inachevées."""
    trouve = OUVERTURE.match(action.ouverture[0]) if action.ouverture else None
    date = (trouve.group(0)[len("**Reprise, "):-len(".**")] if trouve
            else "sans bloc « Reprise »")
    fichiers = notes(action.numero, racine)
    suite = (f"{len(fichiers)} note{'s' if len(fichiers) > 1 else ''}" if fichiers
             else "aucune note")
    etapes = len(etapes_en_cours(fichiers))
    if etapes:
        suite += f", {etapes} étape{'s' if etapes > 1 else ''} en cours"
    return f"{action.numero}. {action.titre} — {date} ; {suite}"


def sommaire(choisies: list[Action], racine: Path = RACINE) -> list[str]:
    return [f"Actions en cours : {len(choisies)}. Le bloc « Reprise » d'une action, "
            "ses notes et les blocs",
            "de ses étapes : `python scripts/reprise.py <numéro>`.", "",
            *(ligne_du_sommaire(action, racine) for action in choisies)]


def imprimer(action: Action, racine: Path = RACINE, toutes: bool = False) -> list[str]:
    """Le bloc d'une action, la liste de ses notes — les dernières, sauf
    ``toutes`` —, puis les blocs de ses étapes inachevées."""
    sortie = [f"### {action.numero}. {action.titre} — `{action.etat}`",
              f"({FEUILLE}:{action.ligne})", "", *action.ouverture]
    fichiers = notes(action.numero, racine)
    if not fichiers:
        return sortie
    listees = fichiers if toutes else fichiers[-NOTES_LISTEES:]
    entete = f"Notes, dans {NOTES}/{action.numero}/ :"
    if len(listees) < len(fichiers):
        entete += (f" les {len(listees)} dernières de {len(fichiers)} "
                   "(`--toutes` les liste toutes).")
    sortie += ["", entete]
    for chemin in listees:
        sortie.append(f"  {chemin.name} — {titre_d_une_note(chemin.read_text(encoding='utf-8'))}")
    for chemin, bloc in etapes_en_cours(fichiers):
        sortie += ["", f"Étape en cours, {chemin.relative_to(racine).as_posix()} :", *bloc]
    return sortie


def main(argv: list[str] | None = None, racine: Path = RACINE) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("numeros", nargs="*",
                           help="les actions à imprimer (sans numéro, le sommaire)")
    analyseur.add_argument("--toutes", action="store_true",
                           help="lister toutes les notes, et non les dernières")
    arguments = analyseur.parse_args(argv)
    texte = (racine / FEUILLE).read_text(encoding="utf-8")
    choisies = [a for a in actions(texte) if a.etat == EN_COURS
                and (not arguments.numeros or a.numero in arguments.numeros)]
    if not choisies:
        print("Aucune action en cours sous ces numéros.")
        return 1
    if not arguments.numeros:
        print("\n".join(sommaire(choisies, racine)))
        return 0
    blocs = ["\n".join(imprimer(action, racine, arguments.toutes)) for action in choisies]
    print("\n\n".join(blocs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
