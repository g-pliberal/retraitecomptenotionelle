#!/usr/bin/env python3
"""Fabrique les neuf pages du site, toutes faites (action 174).

    python scripts/construire_pages.py             # écrit les pages
    python scripts/construire_pages.py --verifier  # n'écrit rien : échoue si l'une est périmée

Le problème qu'il traite
------------------------

Le serveur ne voit pas ce qui suit un ``#`` : les neuf pages du site n'étaient
qu'une, ``index.html``, qui choisissait la sienne une fois ses scripts chargés,
le paquet de données reçu et le moteur prêt — huit secondes sur un téléphone, à
Lighthouse, avant que rien ne s'affiche. Chaque page a désormais son adresse
(``cout/``, ``simuler/``…) et, dans son dossier, un ``index.html`` qui porte
déjà son contenu : le serveur l'envoie tel quel, il s'affiche avec la feuille
de style et les polices, et se lit sans un octet de script. Tout serveur
statique le sert à ``…/cout/`` sans réglage, ce que la copie du site du parti
exige (``docs/integration-partiliberalfrancais.md``).

Ce qu'il écrit
--------------

* **Neuf pages** : l'accueil, ``index.html`` à la racine, et les huit autres
  chacune dans son dossier. Chacune est le gabarit ``moteur/page.html`` — le
  titre de l'onglet, la description, l'adresse canonique de la copie du parti,
  le bandeau, le pied, le routeur — autour du rendu de la page pour ses réglages
  par défaut, celui que ``rendre`` de ``moteur/js/pages.js`` écrirait. Le rendu
  vient de node, par ``retraite_notionnelle.web.site`` : rien n'est écrit ici
  qu'ailleurs on lirait autrement.
* **Les tracés, deux fois.** Coût et Droits non cotisés dessinent leurs
  graphiques à la largeur de la colonne, que le serveur ne connaît pas, et les
  deux schémas de Sankey d'une carte vont de front au large. La page est donc
  rendue pour une colonne de téléphone et pour une colonne de portable, le gabarit marquant
  chaque tracé pour qu'on le retrouve (``marquerLesTraces``), et les deux
  rendus sont fusionnés : tout ce qui n'est pas un tracé doit être identique, et
  chaque tracé est écrit pour les deux écrans, ``variante-etroite`` et
  ``variante-large``, dont la feuille de style montre un seul.
* **Le plan du site**, ``sitemap.xml``, qui liste les neuf adresses de la copie
  du parti : celles que les moteurs de recherche retiennent.

Ce qui les rafraîchit
---------------------

``regenerer.py`` les refait après le paquet et les mesures de l'accueil, dont
le rendu lit les chiffres ; ``tests/test_pages_en_dossier.py`` refuse celles
qui sont périmées, et ``.gitattributes`` les déclare fabriquées. On retouche le
gabarit, jamais une page.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.web.site import module, rendre  # noqa: E402

GABARIT = RACINE / "moteur" / "page.html"

#: Ce que la page porte en tête, pour qui voudrait la retoucher à la main.
MENTION = ("<!-- Page fabriquée par scripts/construire_pages.py, depuis moteur/page.html : "
           "ne la retouchez pas, refaites-la. -->")

#: Le titre de l'onglet de l'accueil : celui qu'un moteur de recherche affiche.
TITRE_DE_L_ACCUEIL = "Retraite à comptes notionnels — programme et simulateur"
#: Celui des autres pages : leur titre, puis le nom du site.
SUFFIXE_DU_TITRE = "Retraite en comptes notionnels"

SITEMAP = "sitemap.xml"


def _echapper(texte: str) -> str:
    """Un texte pour un attribut entre guillemets ou pour le corps d'une balise."""
    return html.escape(texte, quote=False).replace('"', "&quot;")


# -- la fusion des deux rendus ----------------------------------------------------

_MARQUE = re.compile(r"<!--(/?)trace-->")


def decouper(texte: str) -> list[tuple[str, str]]:
    """Un rendu marqué, coupé en morceaux qui alternent : du texte, un tracé, du
    texte… Les marques d'un tracé imbriqué dans un autre — le couple de schémas
    de front et ses deux Sankey — sont ôtées : seul compte le niveau de la page."""
    morceaux: list[tuple[str, str]] = []
    fragments: list[str] = []
    profondeur = 0
    dernier = 0
    for marque in _MARQUE.finditer(texte):
        fragments.append(texte[dernier:marque.start()])
        dernier = marque.end()
        ouvre = marque.group(1) == ""
        if profondeur == 0:
            if not ouvre:
                raise ValueError("une marque de fin de tracé sans début")
            morceaux.append(("texte", "".join(fragments)))
            fragments, profondeur = [], 1
        elif ouvre:
            profondeur += 1
        else:
            profondeur -= 1
            if profondeur == 0:
                morceaux.append(("trace", "".join(fragments)))
                fragments = []
    if profondeur:
        raise ValueError("une marque de début de tracé jamais fermée")
    morceaux.append(("texte", "".join(fragments) + texte[dernier:]))
    return morceaux


def _extrait(texte: str, autre: str) -> str:
    """Où deux textes cessent de se ressembler, pour le message d'une erreur."""
    i = 0
    while i < min(len(texte), len(autre)) and texte[i] == autre[i]:
        i += 1
    return f"…{texte[max(0, i - 40):i + 60]!r} ≠ …{autre[max(0, i - 40):i + 60]!r}"


def fusionner(etroit: str, large: str) -> str:
    """Les deux rendus d'une page, un pour une colonne de téléphone et un pour une
    colonne de portable, en un seul HTML : tout ce qui n'est pas un tracé est le même aux
    deux écrans, et chaque tracé est écrit deux fois, que la feuille de style
    départage. Un tracé que les deux écrans dessinent pareil n'est écrit qu'une
    fois. Une page dont les deux rendus ne s'accordent pas hors des tracés
    mentirait à l'un des écrans : la fusion le refuse."""
    a, b = decouper(etroit), decouper(large)
    if len(a) != len(b):
        raise ValueError(f"les deux rendus n'ont pas les mêmes tracés ({len(a) // 2} contre "
                         f"{len(b) // 2})")
    sortie = []
    for (genre, dedans), (_, ailleurs) in zip(a, b):
        if genre == "texte":
            if dedans != ailleurs:
                raise ValueError("hors des tracés, les deux rendus diffèrent : "
                                 + _extrait(dedans, ailleurs))
            sortie.append(dedans)
        elif dedans == ailleurs:
            sortie.append(dedans)
        else:
            sortie.append(f'<div class="variante-etroite">{dedans}</div>'
                          f'<div class="variante-large">{ailleurs}</div>')
    return "".join(sortie)


def _fin_du_bloc(texte: str, debut: int) -> int:
    """L'indice qui suit le ``</div>`` fermant le ``<div>`` ouvert à ``debut``."""
    profondeur = 0
    for balise in re.finditer(r"<div[\s>]|</div>", texte[debut:]):
        profondeur += 1 if balise.group(0).startswith("<div") else -1
        if profondeur == 0:
            return debut + balise.end()
    raise ValueError("un <div> jamais fermé")


def sans_variantes(page: str, variante: str) -> str:
    """Ce que la page serait pour un seul écran, ``etroite`` ou ``large`` : la
    variante gardée sans son enveloppe, l'autre ôtée. C'est le rendu de cet écran."""
    sortie, position = [], 0
    ouverture = re.compile(r'<div class="variante-(etroite|large)">')
    while (trouve := ouverture.search(page, position)):
        sortie.append(page[position:trouve.start()])
        fin = _fin_du_bloc(page, trouve.start())
        if trouve.group(1) == variante:
            sortie.append(page[trouve.end():fin - len("</div>")])
        position = fin
    sortie.append(page[position:])
    return "".join(sortie)


# -- les pages --------------------------------------------------------------------


def rendu_des_deux_ecrans(route: str) -> str:
    """Le corps d'une page pour ses réglages par défaut, tracés écrits pour les
    deux écrans."""
    g = module("gabarit")
    g.marquerLesTraces(True)
    try:
        etroit = rendre(route, {}, g.ECRAN_ETROIT_PRERENDU)[1]
        large = rendre(route, {}, g.COLONNE_LARGE_PRERENDUE)[1]
    finally:
        g.marquerLesTraces(False)
    try:
        return fusionner(etroit, large)
    except ValueError as erreur:
        raise ValueError(f"{route} : {erreur}") from None


def _sans_commentaires(texte: str) -> str:
    """Le gabarit documente ses choix en commentaires ; la page servie n'en porte
    pas, que sa mention."""
    sans = re.sub(r"<!--.*?-->\n?", "", texte, flags=re.S)
    return sans.replace("<!doctype html>\n", f"<!doctype html>\n{MENTION}\n", 1)


def page(route: str, gabarit: str | None = None) -> str:
    """La page toute faite d'une route : le gabarit autour de son rendu."""
    g, pages = module("gabarit"), module("pages")
    gabarit = GABARIT.read_text(encoding="utf-8") if gabarit is None else gabarit
    dossier = g.dossierDe(route)
    contenu = rendu_des_deux_ecrans(route)
    g.poserOptions("")
    titre = (TITRE_DE_L_ACCUEIL if route == "/"
             else f"{pages.TITRES[route]} — {SUFFIXE_DU_TITRE}")
    valeurs = {
        "titre": _echapper(titre),
        "description": _echapper(pages.DESCRIPTIONS[route]),
        "canonique": f"{g.ADRESSE_CANONIQUE}{dossier}",
        "racine": "" if route == "/" else "../",
        "route": route,
        "entete": g.entete(route),
        "contenu": contenu,
        "pied": g.pied(),
    }
    # Un champ du gabarit que le générateur ne remplit pas est une erreur (KeyError) ;
    # ce qu'on insère n'est pas relu.
    return re.sub(r"\{\{(\w+)\}\}", lambda m: valeurs[m.group(1)], _sans_commentaires(gabarit))


def plan_du_site() -> str:
    """``sitemap.xml`` : les neuf adresses de la copie du parti."""
    g = module("gabarit")
    adresses = [f"{g.ADRESSE_CANONIQUE}{g.dossierDe(route)}" for route in g.PAGES]
    lignes = "".join(f"  <url><loc>{adresse}</loc></url>\n" for adresse in adresses)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{lignes}</urlset>\n")


def attendues() -> dict[str, str]:
    """Les fichiers que le dépôt doit porter : chemin relatif à la racine, puis
    contenu. L'accueil d'abord, les pages dans l'ordre du bandeau, le plan."""
    g = module("gabarit")
    gabarit = GABARIT.read_text(encoding="utf-8")
    fichiers = {f"{g.dossierDe(route)}index.html": page(route, gabarit) for route in g.PAGES}
    fichiers[SITEMAP] = plan_du_site()
    return fichiers


def perimees(voulues: dict[str, str] | None = None) -> list[str]:
    """Les fichiers dont le contenu manque ou n'est pas celui que le script écrirait."""
    voulues = attendues() if voulues is None else voulues
    perimees = []
    for chemin, contenu in voulues.items():
        fichier = RACINE / chemin
        if not fichier.is_file() or fichier.read_text(encoding="utf-8") != contenu:
            perimees.append(chemin)
    return perimees


def ecrire() -> list[str]:
    """Écrit les fichiers périmés ; rend leurs chemins."""
    voulues = attendues()
    faites = []
    for chemin in perimees(voulues):
        fichier = RACINE / chemin
        fichier.parent.mkdir(parents=True, exist_ok=True)
        fichier.write_text(voulues[chemin], encoding="utf-8", newline="\n")
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
    print(f"{len(faites)} fichier(s) écrit(s)" + (f" : {', '.join(faites)}" if faites else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
