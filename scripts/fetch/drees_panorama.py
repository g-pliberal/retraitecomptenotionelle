#!/usr/bin/env python3
"""Le relevé du panorama « Les retraités et les retraites » de la DREES, édition 2026.

    python scripts/fetch/drees_panorama.py            # tests/temoins/drees_panorama_2026.json
    python scripts/fetch/drees_panorama.py --fichier ~/Téléchargements/….pdf

POURQUOI IL EXISTE. L'action 178 exploite le panorama en entier : chacune de
ses trente-quatre fiches, chacun de ses tableaux et de ses graphiques, à sa
place dans le dépôt. Le relevé en est la liste, refaite du PDF lui-même, pour
que le suivi (``data/reference/drees_panorama_2026.yaml``) n'en oublie
aucune : ``tests/test_drees_panorama.py`` refuse une fiche du relevé qui n'y a
pas son statut.

CE QU'IL RELÈVE, de chaque page que ``pdftotext -layout`` rend :

* sa **rubrique**, par la ligne de tête : le numéro de la fiche, à gauche
  (« 01  Les effectifs… ») ou à droite (« …de droit direct  01 ») selon la
  parité de la page, « Annexe N », ou « Vue d'ensemble » ;
* son **numéro imprimé**, par le pied de page (« 21 » ou « 22 », de part ou
  d'autre de « Les retraités et les retraites > Édition 2026 > Drees ») ;
* chaque **figure** — tableau, graphique, carte, schéma — et chaque
  **encadré**, par la ligne qui commence par son nom et son numéro, et son
  titre, avec la ligne suivante quand elle le prolonge ;
* la **source** de chacune, la ligne « Source(s) > » qui la suit, avec ses
  lignes de suite. Une source vaut pour toutes les figures relevées depuis la
  précédente : deux tableaux qui la partagent la reçoivent tous deux.

Le **sommaire** donne le titre et la première page de chaque fiche et de
chaque annexe. Le témoin range les figures sous leur fiche, la vue d'ensemble
et les annexes à part, avec l'empreinte du document lu : un relevé ne vaut
que pour l'édition dont il porte l'empreinte.

Le document vient de ``data/brut/`` ou, à défaut, du miroir que le manifeste
déclare (``drees_panorama_retraites_2026``) : le site de la DREES refuse le
cloud. ``pdftotext`` (poppler) est requis, comme pour
``cnav_points_avant_1973.py``.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from source_locale import (  # noqa: E402
    empreinte, lire_ou_telecharger, option_fichier, telecharger,
)

RACINE = Path(__file__).resolve().parents[2]
MANIFESTE = RACINE / "data" / "sources.yaml"
SORTIE = RACINE / "tests" / "temoins" / "drees_panorama_2026.json"
JEU = "drees_panorama_retraites_2026"

#: Le pied de chaque page, où son numéro imprimé est à gauche ou à droite.
PIED = re.compile(
    r"^\s*(?:(\d+)\s+)?Les retraités et les retraites > Édition \d{4} > Drees(?:\s+(\d+))?\s*$")

#: Une figure ou un encadré : son nom, son numéro (« 1 », « 2a », « A »), son
#: titre.
FIGURE = re.compile(
    r"^(Tableau|Graphique|Carte|Schéma|Encadré)\s+(\d+[a-z]?|[A-Z])\s+(\S.*)$")

#: La ligne des sources d'une figure.
SOURCES = re.compile(r"^Sources?\s*>\s*(.*)$")

#: Une ligne du sommaire : « Fiche 01 • Titre ........ 20 ».
LIGNE_DU_SOMMAIRE = re.compile(r"^(Fiche|Annexe)\s+(\d+)\s+•\s+(.*)$")
PAGE_AU_BOUT = re.compile(r"^(.*?)[\s.]*\.[\s.]*(\d+)$")


def _espaces(ligne: str) -> str:
    return " ".join(ligne.split())


#: Les libellés qui ouvrent une ligne des notes d'une figure.
LIBELLE = re.compile(r"^(Notes?|Lecture|Champ|Sources?)\s*>")

#: Une note numérotée (« 6. Les euros courants… ») ou l'étiquette d'un volet
#: (« 4a. Ensemble des retraités »).
NOTE_OU_VOLET = re.compile(r"^\d+[a-z]?\.\s")


def _texte_courant(ligne: str) -> bool:
    """Une ligne de texte suivi : ni libellé, ni titre de figure, ni note
    numérotée ou volet, ni pied de page, ni ligne de tableau ou de légende
    — des blancs larges, ou une rangée de nombres seuls (« 1930 1932
    1934… »), que « 2010, 2014, 2017 et 2021. » n'est pas."""
    nette = ligne.strip()
    if (not nette or LIBELLE.match(nette) or FIGURE.match(nette)
            or NOTE_OU_VOLET.match(nette) or PIED.match(ligne)
            or re.search(r"\S\s{3,}\S", nette)):
        return False
    jetons = nette.split()
    return len(jetons) < 4 or not all(re.fullmatch(r"[\d,.%]+", jeton) for jeton in jetons)


def _prolonge(ligne: str) -> bool:
    """Une ligne qui prolonge un titre : du texte suivi, avec au moins un mot
    — une graduation d'axe (« 35 000 ») n'en a pas —, qui commence par une
    minuscule, un chiffre ou une parenthèse."""
    nette = ligne.strip()
    return (_texte_courant(ligne) and bool(re.search(r"[^\W\d_]", nette))
            and (nette[0].islower() or nette[0].isdigit() or nette[0] in "(«"))


def _rubrique(tete: str) -> str | None:
    """La rubrique d'une page, par sa ligne de tête."""
    nette = tete.strip()
    if nette.startswith("Vue d’ensemble") or nette.startswith("Vue d'ensemble"):
        return "vue_d_ensemble"
    annexe = re.match(r"^Annexe\s+(\d+)\b", nette)
    if annexe:
        return f"annexe_{annexe.group(1)}"
    gauche = re.match(r"^(\d\d)\s+\D", nette)
    if gauche:
        return gauche.group(1)
    droite = re.search(r"\D\s{2,}(\d\d)$", nette)
    if droite:
        return droite.group(1)
    return None


def _page_imprimee(lignes: list[str]) -> int | None:
    for ligne in reversed(lignes[-3:]):
        pied = PIED.match(ligne)
        if pied and (pied.group(1) or pied.group(2)):
            return int(pied.group(1) or pied.group(2))
    return None


def relever_figures(texte: str) -> list[dict]:
    """Chaque figure et chaque encadré du texte, sa rubrique, sa page
    imprimée, son titre et sa source, dans l'ordre du document."""
    releve: list[dict] = []
    en_attente: list[dict] = []
    rubrique = None
    page = None
    for brute in texte.split("\f"):
        lignes = [ligne for ligne in brute.splitlines() if ligne.strip()]
        if not lignes:
            continue
        rubrique = _rubrique(lignes[0]) or rubrique
        imprimee = _page_imprimee(lignes)
        page = imprimee if imprimee is not None else (page + 1 if page is not None else None)
        i = 0
        while i < len(lignes):
            nette = lignes[i].strip()
            figure = FIGURE.match(nette)
            source = SOURCES.match(nette)
            if figure:
                titre = figure.group(3)
                while (not titre.rstrip().endswith(".") and i + 1 < len(lignes)
                       and _prolonge(lignes[i + 1])):
                    i += 1
                    titre += " " + lignes[i].strip()
                element = {"fiche": rubrique, "page": page, "nature": figure.group(1),
                           "numero": figure.group(2), "titre": _espaces(titre).rstrip(" :"),
                           "sources": ""}
                releve.append(element)
                # Un encadré n'attend sa source que jusqu'à la figure suivante.
                en_attente = [e for e in en_attente if e["nature"] != "Encadré"]
                en_attente.append(element)
            elif source:
                texte_source = source.group(1)
                while (not texte_source.rstrip().endswith(".") and i + 1 < len(lignes)
                       and _texte_courant(lignes[i + 1])):
                    i += 1
                    texte_source += " " + lignes[i].strip()
                for element in en_attente:
                    element["sources"] = _espaces(texte_source)
                en_attente = []
            i += 1
    return releve


def lire_sommaire(texte: str, nature: str = "Fiche") -> dict[str, dict]:
    """Le titre et la première page de chaque fiche (ou de chaque annexe,
    ``nature="Annexe"``) que le sommaire annonce."""
    entrees: dict[str, dict] = {}
    lignes = [ligne.strip() for ligne in texte.splitlines() if ligne.strip()]
    i = 0
    while i < len(lignes):
        entree = LIGNE_DU_SOMMAIRE.match(lignes[i])
        if entree and entree.group(1) == nature:
            reste = entree.group(3)
            au_bout = PAGE_AU_BOUT.match(reste)
            while au_bout is None and i + 1 < len(lignes):
                i += 1
                reste += " " + lignes[i]
                au_bout = PAGE_AU_BOUT.match(reste)
            if au_bout is not None:
                numero = entree.group(2)
                entrees[numero] = {"titre": _espaces(au_bout.group(1)).rstrip(" ."),
                                   "page": int(au_bout.group(2))}
        i += 1
    return entrees


def relever(texte: str) -> dict:
    """Le relevé du document : ses fiches, sa vue d'ensemble et ses annexes,
    chacune avec ses figures et ses encadrés."""
    pages = texte.split("\f")
    debut = next(i for i, page in enumerate(pages) if "Sommaire" in page and "Fiche 01" in page)
    suite = [debut]
    while suite[-1] + 1 < len(pages) and any(
            LIGNE_DU_SOMMAIRE.match(ligne.strip())
            for ligne in pages[suite[-1] + 1].splitlines()):
        suite.append(suite[-1] + 1)
    sommaire = "\n".join(pages[i] for i in suite)
    fiches = {numero: {**entree, "figures": [], "encadres": []}
              for numero, entree in lire_sommaire(sommaire).items()}
    annexes = {f"annexe_{numero}": {**entree, "figures": [], "encadres": []}
               for numero, entree in lire_sommaire(sommaire, "Annexe").items()}
    vue = {"figures": [], "encadres": []}
    hors = []
    for element in relever_figures(texte):
        rubrique = element.pop("fiche")
        cible = fiches.get(rubrique) or annexes.get(rubrique) or (
            vue if rubrique == "vue_d_ensemble" else None)
        if cible is None:
            hors.append({"rubrique": rubrique, **element})
            continue
        cle = "encadres" if element["nature"] == "Encadré" else "figures"
        cible[cle].append(element)
    # pdftotext clôt chaque page d'un saut de page, les blanches comprises.
    return {"pages": texte.count("\f"),
            "vue_d_ensemble": vue, "fiches": fiches, "annexes": annexes,
            "hors_rubrique": hors}


def _pdftotext(octets: bytes) -> str:
    if shutil.which("pdftotext") is None:
        raise SystemExit("pdftotext (poppler) est requis pour lire le panorama")
    with tempfile.TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "panorama.pdf"
        chemin.write_bytes(octets)
        return subprocess.run(["pdftotext", "-layout", str(chemin), "-"],
                              check=True, capture_output=True, text=True).stdout


def _jeu() -> dict:
    import yaml

    manifeste = yaml.safe_load(MANIFESTE.read_text(encoding="utf-8"))
    return next(jeu for institution in manifeste["institutions"].values()
                for jeu in institution.get("jeux", []) if jeu["id"] == JEU)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    option_fichier(analyseur)
    options = analyseur.parse_args(argv)
    jeu = _jeu()
    octets = lire_ou_telecharger(jeu["url"], telecharger, options.fichier,
                                 nom_local=jeu["fichier_local"], miroir=jeu["miroir"],
                                 sha256=jeu["sha256"])
    releve = {"source": jeu["url"], "miroir": jeu["miroir"], "sha256": empreinte(octets),
              **relever(_pdftotext(octets))}
    SORTIE.write_text(json.dumps(releve, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    figures = sum(len(fiche["figures"]) for fiche in releve["fiches"].values())
    encadres = sum(len(fiche["encadres"]) for fiche in releve["fiches"].values())
    print(f"Écrit {SORTIE.relative_to(RACINE)} : {len(releve['fiches'])} fiches, "
          f"{figures} figures et {encadres} encadrés, "
          f"{len(releve['hors_rubrique'])} hors rubrique")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
