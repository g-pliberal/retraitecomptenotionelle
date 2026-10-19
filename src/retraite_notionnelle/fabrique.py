"""Ce que ``scripts/regenerer.py`` a déjà fabriqué, et sur quoi.

Les étapes lourdes de la régénération — le paquet, les témoins, le chiffrage,
les chiffres ancrés — lisent des sources et écrivent des fichiers. Quand une
régénération finit sans échec, l'empreinte de ce que chacune lit et écrit se
garde dans ``.cache/fabrique.json``, que git ignore. Tant qu'elle ne bouge
pas, l'étape n'a rien à refaire, et les tests qui vérifient qu'un fichier
fabriqué est à jour n'ont pas à le refabriquer : une retouche du site ne
refait ni le paquet ni le chiffrage, et la suite ne refait pas ce que la
régénération vient de faire.

Sur une machine neuve — celle de GitHub —, rien n'est gardé : tout se refait,
et tout se vérifie. ``FABRIQUE_SANS_MEMOIRE=1`` fait de même ici.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import threading

from .config import RACINE_PROJET
from .pont import version_de_node

FICHIER = RACINE_PROJET / ".cache" / "fabrique.json"
SANS_MEMOIRE = "FABRIQUE_SANS_MEMOIRE"

#: Ce que chaque étape lit et écrit, en chemins du dépôt : un dossier vaut tout
#: ce que git y suit ou y verrait. Large à dessein : une entrée oubliée
#: laisserait passer ici un fichier périmé, que GitHub seul verrait. Le paquet
#: lit le moteur du portage, qui calcule une part de ses agrégats (action 161,
#: étape 5), sauf le texte des pages, dont il ne prend qu'un extrait ; le
#: chiffrage aussi, le coût faisant simuler sa grille au portage.
ETAPES: dict[str, tuple[str, ...]] = {
    "paquet": ("src", "data", "scripts", "moteur/donnees.json", "moteur/js",
               ":(exclude)moteur/js/pages.js"),
    "témoins": ("src", "data", "scripts", "moteur", "index.html",
                "tests/temoins/simulations.json", "tests/temoins/pages.json"),
    "chiffrage": ("src", "data", "scripts", "moteur/js", ":(exclude)moteur/js/pages.js",
                  "docs/chiffrage_plf.md", "docs/chiffrage_plf.csv"),
    "prose": ("src", "data", "scripts", "moteur", "index.html", "tests", "docs",
              "README.md", "CLAUDE.md"),
}

#: Ce que ``construire_donnees.py`` lit de ``pages.js`` : les systèmes que le
#: site montre et ceux du bilan, le classement comparé, l'écart de taux de la
#: dette, les années des variantes d'espérance de vie, et la saisie des
#: carrières d'exemple du bilan figé, avec les constantes qu'elle nomme.
_LU_DE_PAGES = ("SCENARIOS_MONTRES", "SYSTEMES_BILAN", "CLASSEMENT_COMPARE",
                "ECART_TAUX_DETTE", "ANNEES_ESPERANCE_VIE", "NIVEAUX_RISQUE",
                "NAISSANCE_RISQUE", "STATUT_RISQUE", "DEBUT_RISQUE", "LIQUIDATION_RISQUE")

#: Ce qu'une étape lit d'un fichier sans le lire tout entier : le paquet ne
#: prend de ``pages.js`` que ce que la fabrique y lit, une déclaration à la
#: fois. Sans motif retrouvé, tout le fichier compte.
EXTRAITS: dict[str, tuple[tuple[str, str], ...]] = {
    "paquet": tuple(("moteur/js/pages.js", rf"export const {nom} = .*?;\n")
                    for nom in _LU_DE_PAGES)
              + (("moteur/js/pages.js", r"export function saisieRisque\(.*?\n\}\n"),),
}

_VERROU = threading.Lock()


def extrait(texte: str, motif: str) -> str:
    """Ce que le motif retient du texte ; le texte entier s'il ne retient rien."""
    trouve = re.search(motif, texte, re.DOTALL)
    return trouve.group(0) if trouve else texte


def fichiers(etape: str) -> set[str] | None:
    """Les fichiers que l'étape lit et écrit, en chemins du dépôt, tels que git
    les suit ou les verrait ; ``None`` hors d'un dépôt git."""
    try:
        listes = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard",
             "--", *ETAPES[etape]], cwd=RACINE_PROJET, capture_output=True,
            check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {os.fsdecode(chemin) for chemin in listes.split(b"\0") if chemin}


def empreinte(etape: str) -> str | None:
    """L'empreinte de ce que l'étape lit et écrit ; ``None`` hors d'un dépôt git."""
    lus = fichiers(etape)
    if lus is None:
        return None
    somme = hashlib.sha256(sys.version.encode() + version_de_node())
    for nom in sorted(lus, key=os.fsencode):
        chemin = os.fsencode(nom)
        somme.update(chemin + b"\0")
        try:
            contenu = (RACINE_PROJET / nom).read_bytes()
        except OSError:          # au registre de git, mais effacé du répertoire
            somme.update(b"-")
            continue
        somme.update(b"+" + len(contenu).to_bytes(8, "little") + contenu)
    for chemin, motif in EXTRAITS.get(etape, ()):
        try:
            texte = (RACINE_PROJET / chemin).read_text(encoding="utf-8")
        except OSError:
            texte = ""
        somme.update(extrait(texte, motif).encode("utf-8"))
    return somme.hexdigest()[:24]


def _registre() -> dict:
    try:
        return json.loads(FICHIER.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def a_jour(etape: str) -> bool:
    """L'étape a-t-elle déjà fabriqué, sans échec, ce que ses fichiers portent ?"""
    if os.environ.get(SANS_MEMOIRE):
        return False
    gardee = _registre().get(etape)
    return gardee is not None and gardee == empreinte(etape)


def retenir(etape: str) -> None:
    """L'étape vient de réussir, et tout ce qui la suit aussi : son empreinte
    se garde, sous verrou, les branches de la régénération finissant ensemble."""
    if os.environ.get(SANS_MEMOIRE):
        return
    valeur = empreinte(etape)
    if valeur is None:
        return
    with _VERROU:
        registre = _registre()
        registre[etape] = valeur
        FICHIER.parent.mkdir(parents=True, exist_ok=True)
        FICHIER.write_text(json.dumps(registre, ensure_ascii=False, indent=1,
                                      sort_keys=True) + "\n", encoding="utf-8")
