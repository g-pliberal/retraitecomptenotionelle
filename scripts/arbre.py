#!/usr/bin/env python3
"""L'arbre du dépôt : chaque fichier, avec ses lignes et ses caractères.

    python scripts/arbre.py                    # tout le dépôt, du plus lourd au plus léger
    python scripts/arbre.py src moteur/js      # ces dossiers seulement
    python scripts/arbre.py --profondeur 2     # deux niveaux : où est le poids, d'un coup d'œil
    python scripts/arbre.py --plus-gros 30     # les trente plus gros fichiers, chemin entier

POURQUOI
--------
Chaque appel d'outil relit toute la conversation (``CLAUDE.md``, « Économiser
le contexte ») : un fichier lu se repaie à chaque geste suivant. Savoir où sont
les gros fichiers, c'est savoir ce qui ne se lit qu'en fenêtre, et ce qui
gagnerait à être découpé (feuille de route, action 135).

CE QUI SE COMPTE
----------------
Les fichiers que git suit, et ceux qu'un ``git add -A`` ajouterait ; rien de ce
qu'il ignore. Les lignes sont celles qu'un éditeur montre, la dernière comptée
même sans retour à la ligne ; les caractères, ceux du texte décodé et non ses
octets : un « é » en vaut un. Chaque dossier porte la somme des siens, et chaque
niveau va du plus lourd au plus léger, en caractères. Un fichier qui n'est pas
du texte UTF-8 est binaire : il n'a ni lignes ni caractères, et donne ses
octets. Une ligne de plus de dix mille caractères se signale : un ``grep`` qui
tombe dessus la rend entière.

Ces chiffres changent à chaque commit : comme le coût du travail
(``tableau_de_bord.py --cout``), ils s'impriment à la demande et ne s'écrivent
dans aucun document (``docs/architecture.md``, § 9.3). L'arbre entier fait plus
de mille lignes : une session le lit par dossier, par ``--profondeur`` ou par
``--plus-gros``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

RACINE = Path(__file__).resolve().parents[1]

#: Au-delà, une ligne se signale : un ``grep`` qui tombe dessus la rend entière.
LIGNE_DEMESUREE = 10_000


@dataclass
class Noeud:
    """Un fichier, ou un dossier et la somme de ce qu'il contient."""

    nom: str
    lignes: int = 0
    caracteres: int = 0
    #: Les octets d'un fichier binaire ; ``None`` pour du texte, et un dossier.
    octets: int | None = None
    #: La plus longue ligne d'un fichier texte, en caractères.
    plus_longue: int = 0
    #: Ce que contient un dossier ; ``None`` pour un fichier.
    enfants: dict[str, Noeud] | None = None

    @property
    def dossier(self) -> bool:
        return self.enfants is not None


def fichiers(racine: Path) -> list[str]:
    """Ce que git suit, et ce qu'un ``git add -A`` ajouterait : rien de ce
    qu'il ignore, ni un fichier effacé que l'index porte encore."""
    sortie = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=racine, capture_output=True, check=True).stdout.decode("utf-8")
    return sorted({c for c in sortie.split("\0") if c and (racine / c).is_file()})


def mesurer(chemin: Path, nom: str) -> Noeud:
    """Un fichier : ses lignes et ses caractères, ou ses octets s'il est binaire."""
    octets = chemin.read_bytes()
    try:
        texte = octets.decode("utf-8")
    except UnicodeDecodeError:
        texte = "\0"
    if "\0" in texte:
        return Noeud(nom, octets=len(octets))
    lignes = texte.count("\n") + (1 if texte and not texte.endswith("\n") else 0)
    return Noeud(nom, lignes, len(texte),
                 plus_longue=max(len(ligne) for ligne in texte.split("\n")))


def construire(chemins: list[str], racine: Path) -> Noeud:
    """L'arbre de ces fichiers, chaque dossier portant la somme des siens."""
    tronc = Noeud(".", enfants={})
    for chemin in chemins:
        *dossiers, nom = chemin.split("/")
        noeud = tronc
        for dossier in dossiers:
            noeud = noeud.enfants.setdefault(dossier, Noeud(dossier, enfants={}))
        noeud.enfants[nom] = mesurer(racine / chemin, nom)
    _sommer(tronc)
    return tronc


def _sommer(dossier: Noeud) -> None:
    for enfant in dossier.enfants.values():
        if enfant.dossier:
            _sommer(enfant)
        dossier.lignes += enfant.lignes
        dossier.caracteres += enfant.caracteres


def _du_plus_lourd(noeuds) -> list[Noeud]:
    return sorted(noeuds, key=lambda n: (-n.caracteres, -(n.octets or 0), n.nom))


def dessiner(noeud: Noeud, titre: str, profondeur: int | None = None) -> list[tuple[str, Noeud]]:
    """Les rangs de l'arbre : le texte de gauche, et le nœud dont il porte les
    chiffres. Un dossier au-delà de ``profondeur`` garde sa somme, sans son
    contenu."""
    rangs = [(titre, noeud)]

    def descendre(dossier: Noeud, prefixe: str, niveau: int) -> None:
        enfants = _du_plus_lourd(dossier.enfants.values())
        for rang, enfant in enumerate(enfants):
            dernier = rang == len(enfants) - 1
            rangs.append((prefixe + ("└── " if dernier else "├── ") + enfant.nom
                          + ("/" if enfant.dossier else ""), enfant))
            if enfant.dossier and (profondeur is None or niveau < profondeur):
                descendre(enfant, prefixe + ("    " if dernier else "│   "), niveau + 1)

    if noeud.dossier and (profondeur is None or profondeur > 0):
        descendre(noeud, "", 1)
    return rangs


def plus_gros(noeud: Noeud, nombre: int) -> list[tuple[str, Noeud]]:
    """Les ``nombre`` plus gros fichiers de l'arbre, sous leur chemin entier."""
    feuilles: list[tuple[str, Noeud]] = []

    def parcourir(dossier: Noeud, prefixe: str) -> None:
        for enfant in dossier.enfants.values():
            if enfant.dossier:
                parcourir(enfant, prefixe + enfant.nom + "/")
            else:
                feuilles.append((prefixe + enfant.nom, enfant))

    parcourir(noeud, "")
    return sorted(feuilles, key=lambda f: (-f[1].caracteres, -(f[1].octets or 0), f[0]))[:nombre]


def milliers(n: int) -> str:
    """Les milliers séparés d'une espace simple, qui garde les colonnes alignées."""
    return f"{n:,}".replace(",", " ")


def tableau(rangs: list[tuple[str, Noeud]], entete: str = "") -> str:
    """Les rangs en colonnes : le texte, puis les lignes et les caractères."""
    gauche = max([len(entete), *(len(texte) for texte, _ in rangs)])
    lignes = max([len("lignes"), *(len(milliers(n.lignes)) for _, n in rangs)])
    caracteres = max([len("caractères"), *(len(milliers(n.caracteres)) for _, n in rangs)])
    sortie = [f"{entete:<{gauche}}  {'lignes':>{lignes}}  {'caractères':>{caracteres}}"]
    for texte, noeud in rangs:
        if noeud.octets is not None:
            chiffres = (f"{'—':>{lignes}}  {'—':>{caracteres}}"
                        f"  binaire, {milliers(noeud.octets)} octets")
        else:
            chiffres = (f"{milliers(noeud.lignes):>{lignes}}"
                        f"  {milliers(noeud.caracteres):>{caracteres}}")
            if noeud.plus_longue > LIGNE_DEMESUREE:
                chiffres += f"  plus longue ligne : {milliers(noeud.plus_longue)}"
        sortie.append(f"{texte:<{gauche}}  {chiffres}")
    return "\n".join(ligne.rstrip() for ligne in sortie)


def _normaliser(chemin: str) -> str:
    """``./src/``, ``src`` et ``src\\`` sous Windows nomment le même dossier."""
    return PurePosixPath(chemin.replace("\\", "/")).as_posix()


def _sous(fichier: str, chemin: str) -> bool:
    return chemin == "." or fichier == chemin or fichier.startswith(chemin + "/")


def _trouver(tronc: Noeud, chemin: str) -> Noeud:
    noeud = tronc
    for partie in PurePosixPath(chemin).parts:
        noeud = noeud.enfants[partie]
    return noeud


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("chemins", nargs="*", metavar="chemin",
                           help="un dossier ou un fichier, depuis la racine du dépôt ; "
                                "par défaut, tout le dépôt")
    analyseur.add_argument("--profondeur", type=int, metavar="N",
                           help="ne descend pas au-delà de N niveaux ; les dossiers "
                                "plus bas gardent leur somme")
    analyseur.add_argument("--plus-gros", type=int, metavar="N",
                           help="les N plus gros fichiers, chemin entier, au lieu de l'arbre")
    arguments = analyseur.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # la console de Windows lit cp1252

    chemins = [_normaliser(c) for c in arguments.chemins] or ["."]
    tous = fichiers(RACINE)
    absents = [c for c in chemins if not any(_sous(f, c) for f in tous)]
    if absents:
        print(f"{', '.join(absents)} : rien que git suive", file=sys.stderr)
        return 2
    tronc = construire([f for f in tous if any(_sous(f, c) for c in chemins)], RACINE)

    if arguments.plus_gros is not None:
        print(tableau(plus_gros(tronc, arguments.plus_gros), "fichier"))
        return 0
    blocs = []
    for chemin in chemins:
        noeud = _trouver(tronc, chemin)
        titre = chemin + ("/" if noeud.dossier and chemin != "." else "")
        blocs.append(tableau(dessiner(noeud, titre, arguments.profondeur)))
    print("\n\n".join(blocs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
