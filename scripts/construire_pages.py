#!/usr/bin/env python3
"""Fabrique les pages du site, une par dossier (action 174).

    python scripts/construire_pages.py             # écrit les pages
    python scripts/construire_pages.py --verifier  # n'écrit rien : échoue si l'une est périmée

Le problème qu'il traite
------------------------

Le serveur ne voit pas ce qui suit un ``#`` : les neuf pages du site n'étaient
qu'une, ``index.html``, qui choisissait la sienne une fois ses scripts chargés.
Il ne pouvait donc rien servir de propre à chacune — ni son titre, ni sa
description, et bientôt son contenu tout fait. Chaque page a désormais son
dossier (``cout/``, ``simuler/``…) et, dedans, son ``index.html`` : tout serveur
statique le sert à ``…/cout/`` sans réglage, ce que la copie du site du parti
exige (``docs/integration-partiliberalfrancais.md``).

Ce qu'il écrit
--------------

Pour chaque page autre que l'accueil, la coquille de ``index.html`` : le même
routeur, la même feuille de style, les mêmes préchargements, leurs chemins
remontés d'un cran (``../moteur/``), avec le titre de l'onglet et la
description de la page — ceux que le routeur y posera de toute façon, mais que
lit déjà qui ne lance pas de script. Le titre et la description viennent de
``moteur/js/pages.js`` (``TITRES``, ``DESCRIPTIONS``), le dossier du gabarit
(``dossierDe``) : rien n'est écrit ici qu'ailleurs on lirait autrement.

``index.html`` reste la source : c'est lui qu'on retouche, jamais une page de
dossier. ``regenerer.py`` refait celles-ci, ``tests/test_pages_en_dossier.py``
refuse celles qui sont périmées, et ``.gitattributes`` les déclare fabriquées.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.web.site import module  # noqa: E402

#: Ce que la page porte en tête, pour qui voudrait la retoucher à la main.
MENTION = ("<!-- Page fabriquée par scripts/construire_pages.py depuis index.html : "
           "ne la retouchez pas, refaites-la. -->")

#: Le titre de l'onglet, tel que le routeur le pose après le rendu.
SUFFIXE_DU_TITRE = "Retraite en comptes notionnels"


def _echapper(texte: str) -> str:
    """Un texte pour un attribut entre guillemets ou pour le corps d'une balise."""
    return html.escape(texte, quote=False).replace('"', "&quot;")


def page_du_dossier(accueil: str, titre: str, description: str) -> str:
    """La coquille de l'accueil, posée un dossier plus bas : ses chemins
    remontés d'un cran, le titre et la description de la page à la place des
    siens."""
    texte = re.sub(r'\b(href|src)="moteur/', r'\1="../moteur/', accueil)
    texte, titres = re.subn(r"<title>[^<]*</title>",
                            lambda _: f"<title>{_echapper(titre)} — {SUFFIXE_DU_TITRE}</title>",
                            texte)
    texte, descriptions = re.subn(
        r'<meta name="description" content="[^"]*">',
        lambda _: f'<meta name="description" content="{_echapper(description)}">', texte)
    if (titres, descriptions) != (1, 1):
        raise ValueError("index.html doit porter un titre et une description")
    return texte.replace("<!doctype html>\n", f"<!doctype html>\n{MENTION}\n", 1)


def attendues() -> dict[str, str]:
    """Les pages en dossier, telles que le dépôt doit les porter : chemin
    relatif à la racine, puis contenu."""
    accueil = (RACINE / "index.html").read_text(encoding="utf-8")
    pages, gabarit = module("pages"), module("gabarit")
    return {
        f"{gabarit.dossierDe(route)}index.html": page_du_dossier(
            accueil, titre, pages.DESCRIPTIONS[route])
        for route, titre in pages.TITRES.items() if route != "/"
    }


def perimees() -> list[str]:
    """Les pages dont le fichier manque ou n'est pas celui que le script écrirait."""
    perimees = []
    for chemin, contenu in attendues().items():
        fichier = RACINE / chemin
        if not fichier.is_file() or fichier.read_text(encoding="utf-8") != contenu:
            perimees.append(chemin)
    return perimees


def ecrire() -> list[str]:
    """Écrit les pages périmées ; rend leurs chemins."""
    faites = []
    for chemin, contenu in attendues().items():
        fichier = RACINE / chemin
        if fichier.is_file() and fichier.read_text(encoding="utf-8") == contenu:
            continue
        fichier.parent.mkdir(parents=True, exist_ok=True)
        fichier.write_text(contenu, encoding="utf-8", newline="\n")
        faites.append(chemin)
    return faites


def main() -> int:
    analyse = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyse.add_argument("--verifier", action="store_true",
                         help="n'écrit rien : échoue si une page est périmée")
    arguments = analyse.parse_args()
    if arguments.verifier:
        peri = perimees()
        for chemin in peri:
            print(f"périmée : {chemin} — python scripts/construire_pages.py", file=sys.stderr)
        return 1 if peri else 0
    faites = ecrire()
    print(f"{len(faites)} page(s) écrite(s)" + (f" : {', '.join(faites)}" if faites else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
