"""Rien de perdu : ce qui se déplace se retrouve dans le nouveau rangement.

    python scripts/conservation.py                  # contre la référence figée
    python scripts/conservation.py --depuis HEAD    # un déplacement, avant de le commiter
    python scripts/conservation.py --figer          # fige la référence

``docs/architecture.md`` (§ 12) le demande pour les phases 1 à 8, qui
réorganisent le dépôt sans changer un résultat : « Un script de conservation
vérifie que chaque paragraphe des documents et chaque entrée des registres
d'aujourd'hui se retrouvent dans le nouveau rangement. Il se retire après la
phase 8, quand plus rien ne se déplace. »

Il sert de deux façons.

**Un déplacement, avant de le commiter.** ``--depuis HEAD`` compare le dernier
commit au répertoire de travail : chaque paragraphe de chaque document, et
chaque entrée de chaque registre, doit se retrouver quelque part, à
l'identique. Un déplacement ne réécrit rien ; ce qui manque est perdu. Le
script le dit, fichier par fichier, et rend 1. ``--depuis`` prend n'importe
quelle révision : ``--depuis phase-0`` montre tout ce qui a changé depuis le
début de la réorganisation, réécritures légitimes comprises.

**Le filet, que le test joue à chaque envoi.** La référence figée,
``tests/temoins/conservation.json``, ne tient que ce qui ne doit plus bouger :
les paragraphes des RÉCITS (``data/reference/prose/zones.yaml``), des notes de
décision et des archives — hors les actions de la feuille de route encore en
cours, qui vivent, et les tableaux que ``scripts/chiffrage_plf.py`` réécrit —,
et l'identifiant de chaque entrée des registres. Un récit est gelé : s'il
manque, il a été perdu ou réécrit. Une section d'état, elle, change avec le
dépôt, et l'historique git garde ses versions. La référence ne se fige pas par
dessus une perte : ``--figer`` refuse tant que le filet n'est pas vert.

Deux paragraphes sont les mêmes s'ils ne diffèrent que par les blancs, les
dièses d'un titre, ou la valeur d'un chiffre ancré, que
``scripts/verifier_prose.py --corriger`` récrit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
REFERENCE = RACINE / "tests" / "temoins" / "conservation.json"
ZONES = "data/reference/prose/zones.yaml"
FEUILLE = "docs/feuille_de_route.md"

sys.path.insert(0, str(RACINE / "scripts"))
from verifier_prose import (  # noqa: E402
    Zonage, _blocs_de_code, decouper, paragraphes_geles)

#: Les registres, et ce qui identifie une entrée dans chacun : une clé, ou
#: plusieurs jointes. Une section qui est un dictionnaire s'identifie par ses
#: clés.
REGISTRES = {
    "data/reference/legislation/veille.yaml": {
        "entrees": ("id",), "journal": ("date", "session"),
        "sources_a_consulter": ("nom",)},
    "data/sources_a_explorer.yaml": {"sources": ("id",)},
    "data/reference/legislation/reformes.yaml": {"reformes": ("code",)},
    "data/reference/regimes/inventaire.yaml": {"inventaire": ("code",)},
    "data/reference/regimes/pivots.yaml": {"pivots": None},
    "data/reference/legislation/frontiere_contributive.yaml": {
        "pivots": ("article",), "bascules": ("code",), "bascules_hors_legi": ("code",)},
    "data/reference/site/affirmations.yaml": {"affirmations": ("id",)},
    "data/sources.yaml": {"institutions": None, "institutions/*/jeux": ("id",)},
}

#: Où une entrée peut aller quand elle se déplace : les archives d'un
#: registre (docs/architecture.md, annexe B). Un registre qui n'en a pas
#: garde ses entrées.
ARCHIVES_DES_REGISTRES: dict[str, list[str]] = {}

#: Les documents dont les tableaux sont écrits par un script : leurs tableaux
#: changent avec le modèle, leur prose non.
TABLEAUX_PRODUITS = {"docs/chiffrage_plf.md"}

ANCRE = re.compile(r"(<!--chiffre:[^>]*-->).*?(<!--/-->)", re.DOTALL)


# --------------------------------------------------------------------------
# Lire un état du dépôt : le répertoire de travail, ou une révision.
# --------------------------------------------------------------------------


class Arbre:
    """Les fichiers du dépôt, tels que le répertoire de travail ou une
    révision git les porte."""

    def __init__(self, revision: str | None = None, racine: Path = RACINE):
        self.revision, self.racine = revision, racine

    def documents(self) -> list[str]:
        """Les documents : ``CLAUDE.md``, ``README.md`` et ``docs/``."""
        if self.revision is None:
            chemins = [p.relative_to(self.racine).as_posix()
                       for motif in ("*.md", "docs/**/*.md")
                       for p in self.racine.glob(motif)]
        else:
            sortie = subprocess.run(
                ["git", "ls-tree", "-r", "--name-only", self.revision],
                cwd=self.racine, capture_output=True, text=True, check=True).stdout
            chemins = [c for c in sortie.splitlines() if c.endswith(".md")
                       and ("/" not in c or c.startswith("docs/"))]
        return sorted(set(chemins))

    def lire(self, chemin: str) -> str | None:
        if self.revision is None:
            fichier = self.racine / chemin
            return fichier.read_text(encoding="utf-8") if fichier.is_file() else None
        lu = subprocess.run(["git", "show", f"{self.revision}:{chemin}"],
                            cwd=self.racine, capture_output=True)
        return lu.stdout.decode("utf-8") if lu.returncode == 0 else None


# --------------------------------------------------------------------------
# Les paragraphes.
# --------------------------------------------------------------------------


def normaliser(bloc: str) -> str:
    """Un paragraphe aux blancs, aux dièses de titre et aux chiffres ancrés près."""
    texte = ANCRE.sub(r"\1\2", bloc)
    texte = re.sub(r"^#{1,6}\s+", "", texte.strip())
    return " ".join(texte.split())


def empreinte(bloc: str) -> str:
    return hashlib.sha1(normaliser(bloc).encode("utf-8")).hexdigest()[:16]


def paragraphes(texte: str) -> list[tuple[int, int, str]]:
    """Les paragraphes d'un document : première ligne, dernière, texte.

    Un titre est un paragraphe à lui seul. Un bloc de code clôturé en est un,
    blancs compris : couper un programme à ses lignes vides n'aurait pas de
    sens.
    """
    lignes = texte.split("\n")
    sortie, courant, debut, dans_code = [], [], 0, False

    def clore(fin: int):
        if courant and normaliser("\n".join(courant)).strip("-*_ "):
            sortie.append((debut, fin, "\n".join(courant)))
        courant.clear()

    for numero, ligne in enumerate(lignes, 1):
        cloture = ligne.lstrip().startswith("```")
        if not dans_code and (not ligne.strip() or re.match(r"#{1,6} ", ligne)):
            clore(numero - 1)
            if ligne.strip():
                debut = numero
                courant.append(ligne)
                clore(numero)
            continue
        if not courant:
            debut = numero
        courant.append(ligne)
        if cloture:
            dans_code = not dans_code
    clore(len(lignes))
    return sortie


def _vivantes(texte: str) -> set[int]:
    """Les lignes des actions de la feuille de route qui ne sont pas closes :
    une action `en cours` s'écrit encore."""
    vivantes, dedans, code = set(), False, _blocs_de_code(texte)
    for numero, ligne in enumerate(texte.split("\n"), 1):
        titre = None if numero in code else re.match(r"(#{1,3}) ", ligne)
        if titre:
            action = re.match(r"### \d+\..* — `([^`]*)`\s*$", ligne)
            if action or len(titre.group(1)) < 3:
                dedans = bool(action) and action.group(1) not in (
                    "fait", "abandonnée", "archivée")
        if dedans:
            vivantes.add(numero)
    return vivantes


def geles(arbre: Arbre) -> dict[str, dict[str, list[str]]]:
    """Les paragraphes qui ne doivent plus bouger, par document et par section.

    Ceux des récits, des notes de décision (``docs/decisions/``) et des
    archives (``docs/archives/``), hors les actions vivantes de la feuille de
    route et les tableaux qu'un script écrit.
    """
    zonage = Zonage(yaml.safe_load(arbre.lire(ZONES) or "") or {})
    sortie: dict[str, dict[str, list[str]]] = {}
    for chemin in arbre.documents():
        texte = arbre.lire(chemin)
        if texte is None:
            continue
        tout_gele = chemin.startswith(("docs/decisions/", "docs/archives/"))
        if not tout_gele and chemin not in zonage.fichiers:
            continue
        lignes = texte.split("\n")
        sections = decouper(texte)
        recits = paragraphes_geles(lignes, zonage.prefixes_recit(chemin))
        vivantes = _vivantes(texte) if chemin == FEUILLE else set()
        for debut, fin, bloc in paragraphes(texte):
            section = next(s for s in sections if s.debut <= debut <= s.fin)
            regime = "recit" if tout_gele else zonage.regime(chemin, section)
            if regime != "recit" and debut not in recits:
                continue
            if debut in vivantes:
                continue
            if chemin in TABLEAUX_PRODUITS and bloc.lstrip().startswith("|"):
                continue
            sortie.setdefault(chemin, {}).setdefault(section.titre, []).append(
                empreinte(bloc))
    return sortie


def tous_les_paragraphes(arbre: Arbre) -> dict[str, list[tuple[str, int, str]]]:
    """Chaque paragraphe de chaque document, par empreinte : où il est."""
    index: dict[str, list[tuple[str, int, str]]] = {}
    for chemin in arbre.documents():
        texte = arbre.lire(chemin)
        if texte is None:
            continue
        for debut, _, bloc in paragraphes(texte):
            index.setdefault(empreinte(bloc), []).append((chemin, debut, bloc))
    return index


# --------------------------------------------------------------------------
# Les entrées des registres.
# --------------------------------------------------------------------------


def _cle(entree, champs: tuple[str, ...]) -> str:
    return " | ".join(str(entree.get(c)) for c in champs)


def _descendre(donnees: dict, section: str):
    """Une section d'un registre ; ``*`` parcourt les valeurs d'un
    dictionnaire et met bout à bout les listes qu'elles portent."""
    niveaux = [donnees]
    for pas in section.split("/"):
        suivants = []
        for n in niveaux:
            if not isinstance(n, dict):
                continue
            suivants.extend(n.values() if pas == "*" else [n.get(pas)])
        niveaux = [n for n in suivants if n is not None]
    if not niveaux:
        return None
    if "*" not in section:
        return niveaux[0]
    return [e for n in niveaux for e in n]


def entrees(arbre: Arbre) -> dict[str, dict[str, str]]:
    """Les entrées de chaque registre, par identifiant : l'empreinte de leur
    contenu. La clé de premier niveau est ``fichier:section``."""
    sortie: dict[str, dict[str, str]] = {}
    for fichier, sections in REGISTRES.items():
        lieux = [fichier] + ARCHIVES_DES_REGISTRES.get(fichier, [])
        for lieu in lieux:
            texte = arbre.lire(lieu)
            if texte is None:
                continue
            donnees = yaml.safe_load(texte) or {}
            for section, champs in sections.items():
                contenu = _descendre(donnees, section)
                if contenu is None:
                    continue
                elements = (contenu.items() if champs is None else
                            ((_cle(e, champs), e) for e in contenu))
                cible = sortie.setdefault(f"{fichier}:{section}", {})
                for cle, valeur in elements:
                    cible[str(cle)] = hashlib.sha1(json.dumps(
                        valeur, sort_keys=True, ensure_ascii=False, default=str
                    ).encode("utf-8")).hexdigest()[:16]
    return sortie


# --------------------------------------------------------------------------
# Comparer.
# --------------------------------------------------------------------------


def depuis(revision: str) -> list[str]:
    """Ce qu'une révision portait et que le répertoire de travail n'a plus."""
    avant, apres = Arbre(revision), Arbre()
    ici = tous_les_paragraphes(apres)
    pertes = []
    for chemin in avant.documents():
        texte = avant.lire(chemin)
        for debut, _, bloc in paragraphes(texte or ""):
            if empreinte(bloc) not in ici:
                apercu = " ".join(bloc.split())
                pertes.append(f"{chemin}:{debut} : {apercu[:110]}")
    registres_apres = entrees(apres)
    for registre, cles in entrees(avant).items():
        present = registres_apres.get(registre, {})
        for cle, contenu in cles.items():
            if cle not in present:
                pertes.append(f"{registre} : l'entrée « {cle} » a disparu")
            elif present[cle] != contenu:
                pertes.append(f"{registre} : l'entrée « {cle} » a changé")
    return pertes


def figer(arbre: Arbre | None = None) -> dict:
    """La référence : les paragraphes gelés et les identifiants des registres."""
    arbre = arbre or Arbre()
    return {
        "paragraphes": geles(arbre),
        "entrees": {registre: sorted(cles) for registre, cles in entrees(arbre).items()},
    }


def verifier(reference: dict | None = None, arbre: Arbre | None = None) -> list[str]:
    """Ce que la référence figée tient et que le dépôt n'a plus."""
    if reference is None:
        reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    arbre = arbre or Arbre()
    ici = tous_les_paragraphes(arbre)
    pertes = []
    for chemin, sections in reference["paragraphes"].items():
        for section, empreintes in sections.items():
            perdus = [e for e in empreintes if e not in ici]
            if perdus:
                pertes.append(f"{chemin}, « {section} » : {len(perdus)} paragraphe(s) "
                              "gelé(s) introuvable(s) — perdu(s) ou réécrit(s)")
    registres = entrees(arbre)
    for registre, cles in reference["entrees"].items():
        disparues = sorted(set(cles) - set(registres.get(registre, {})))
        for cle in disparues:
            pertes.append(f"{registre} : l'entrée « {cle} » a disparu")
    return pertes


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--depuis", metavar="REVISION",
                           help="compare cette révision au répertoire de travail")
    analyseur.add_argument("--figer", action="store_true",
                           help="écrit la référence figée, si rien n'est perdu")
    analyseur.add_argument("--accepter-les-pertes", action="store_true",
                           help="avec --figer : fige quand même, en listant ce qu'on "
                                "abandonne, pour le dire dans le commit")
    arguments = analyseur.parse_args()

    if arguments.depuis:
        pertes = depuis(arguments.depuis)
        for perte in pertes:
            print(perte)
        print(f"{len(pertes)} perte(s) depuis {arguments.depuis}" if pertes else
              f"rien de perdu depuis {arguments.depuis}")
        return 1 if pertes else 0

    if arguments.figer:
        pertes = verifier() if REFERENCE.is_file() else []
        for perte in pertes:
            print(perte)
        if pertes and not arguments.accepter_les_pertes:
            print("la référence ne se fige pas par-dessus une perte : retrouver ces "
                  "paragraphes, ou, s'ils ont été réécrits exprès, refiger avec "
                  "--accepter-les-pertes et dire pourquoi dans le commit")
            return 1
        reference = figer()
        REFERENCE.write_text(json.dumps(reference, ensure_ascii=False, indent=1,
                                        sort_keys=True) + "\n", encoding="utf-8")
        n = sum(len(e) for s in reference["paragraphes"].values() for e in s.values())
        m = sum(len(c) for c in reference["entrees"].values())
        print(f"référence figée : {n} paragraphes gelés, {m} entrées de registres")
        return 0

    pertes = verifier()
    for perte in pertes:
        print(perte)
    print(f"{len(pertes)} perte(s)" if pertes else "rien de perdu")
    return 1 if pertes else 0


if __name__ == "__main__":
    sys.exit(main())
