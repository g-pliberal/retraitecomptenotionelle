#!/usr/bin/env python3
"""La base de législation de la Cnav, entière, et son registre.

    python scripts/fetch/cnav_legislation.py           # lit la base, tient le registre
    python scripts/fetch/cnav_legislation.py --tout    # redemande aussi chaque référence

POURQUOI IL EXISTE (action 175, étape 1). Dix récupérateurs lisaient chacun
quelques barèmes de la base, et rien ne disait ce qu'elle sert d'autre : le
29 octobre 2026, le dépôt en citait 29 barèmes sur 386. Ce récupérateur la lit
entière, et tient le registre où chaque barème, exposé, liste, référence et
fenêtre d'information a son sort : l'exhaustivité se mesure à ce qui y reste
``a_lire``.

CE QU'IL LIT. Les trois collections de l'API, d'un appel chacune — ``/baremes``,
``/expose``, ``/liste`` — ; ses deux menus, ``/menu/menuBareme`` et
``/menu/menuReglementation`` ; les barèmes de chaque entrée du premier
(``/baremes/baremesByMenuId/<id>``), qui en donnent le thème ; les fenêtres
d'information que ses objets ouvrent (``#/infosupp/``, servies par
``/main/findPopupDetailsByFileLeafRef/<nom>``), exemples, lexique et
compléments, relues chaque fois : elles sont peu. Puis, une à une
(``/reference/referencesByFileLeafRef/<nom>``), les références que les
collections et les fenêtres lient — circulaires, lettres, décrets, règlements
et conventions, par la route du site ou en PDF sous ``/Pdf/`` —, et celles que
ces références citent à leur tour, de proche en proche : le 29 octobre 2026,
2 298 références liées en citaient 2 020 autres, sur quatre rangs. Une
référence ne se redemande que si le registre ne la porte pas, ou sans titre,
ou si un objet qui la lie est neuf ou que sa date de modification dit changé ;
ce que les autres citent, le registre le garde (``citations.csv``).
``--tout`` les redemande toutes.

CE QU'IL ÉCRIT. Les réponses, dans ``data/brut/cnav_legislation/``, que git
ignore : elles ne se versionnent pas. Le registre, dans
``data/reference/legislation/cnav/``, un fichier par genre — ``baremes.csv``,
``exposes.csv``, ``listes.csv``, ``references.csv``, ``fenetres.csv`` —, qui ne
garde que des noms, des titres, des thèmes et des dates, la nature d'une
fenêtre, et le sort de chaque objet, que la session qui le lit écrit à la
main ; ce script le garde, avec la date de la version qui l'a reçu. Ce que la
base sert de neuf entre ``a_lire`` ; ce qui attend encore prend ce que la base
en dit ; ce qui en disparaît, ou que plus rien n'atteint, sort du registre
s'il n'a pas été lu, et y reste sinon. Le script dit ce qui a changé depuis son
sort, et ce qui a disparu. ``citations.csv``, enfin, qu'il écrit seul : qui
cite qui parmi les références.

LES NOMS sont ceux de l'API, extension comprise : ``.aspx`` pour un barème, un
exposé, une liste, une fenêtre ou une référence que la route du site ouvre,
``.pdf`` pour un PDF de ``/Pdf/``. La base lie quelques références sous une
casse fautive, « Circulaire_cnav_… », que l'API ne sert qu'en minuscules : le
registre les porte sous le nom servi.

LE THÈME. Celui d'un barème est l'entrée du menu des barèmes qui le nomme, la
première dans l'ordre du menu ; le menu n'en nomme que les pages d'accueil, qui
passent le leur aux éditions qu'elles lient. Celui d'un exposé est l'entrée du
menu de la réglementation que son ``menuId`` désigne. Une liste, une fenêtre et
une référence n'ont pas de menu : elles prennent le premier niveau du thème de
chaque objet qui les lie. Une référence que seules d'autres références citent
n'en a pas : passé de citation en citation, le thème en donnait seize à un
article de code que toute la base cite ; ``citations.csv`` dit qui la cite.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cnav_api  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
REGISTRE = RACINE / "data" / "reference" / "legislation" / "cnav"
BRUT = RACINE / "data" / "brut" / "cnav_legislation"
GENRES = ("baremes", "exposes", "listes", "references", "fenetres")
#: La date que le registre garde de chaque genre : la date de modification
#: d'un barème, d'un exposé ou d'une fenêtre, que la veille compare à la base ;
#: le jour d'une référence. Une liste n'en a pas : l'API ne la date pas.
DATES = {"baremes": "modifie_le", "exposes": "modifie_le", "listes": None,
         "references": "date_texte", "fenetres": "modifie_le"}
#: Les genres qu'aucun menu ne range, et qui prennent le thème de ce qui les lie.
SANS_MENU = ("listes", "references", "fenetres")
SORTS = ("branche", "recoupe", "limite", "hors_modele", "a_lire")
#: Qui cite qui parmi les références : écrit par ce script seul.
CITATIONS = "citations.csv"
#: La nature d'une fenêtre, sous la clé où l'API la sert.
NATURES = {"exemple": "exemple", "lexique": "lexique", "complementInformation": "complement"}
#: Les requêtes qui partent ensemble : la base répond en une demi-seconde, et
#: deux mille références se lisent ainsi en quelques minutes.
EN_PARALLELE = 4

_LIEN = re.compile(r'href="([^"]*)"')
_ROUTE = re.compile(r"#/(bareme|expose|references-reglementaires)\?file_leaf_ref=([^#&?]+)")
_FENETRE = re.compile(r"#/infosupp/([^?#]+)")
_PDF = re.compile(r"/Pdf/([^?#]+)")
ROUTES = {"bareme": "bareme", "expose": "expose", "references-reglementaires": "reference"}

ENTETE = """\
# {titre}
# {trait}
# Action 175 de la feuille de route. La base, legislation.lassuranceretraite.fr,
# se lit par son API (scripts/fetch/cnav_api.py) ; ce fichier et les autres du
# dossier en portent chaque objet une fois, rangé par nom, avec son sort.
#
# Les colonnes {colonnes} sont écrites par
# scripts/fetch/cnav_legislation.py, qui relit la base ; sort, renvoi et
# script, par la session qui lit l'objet, et le script les garde.
#
# {propre}
#
# LE SORT, que tests/test_cnav_legislation.py tient :
#   branche      renvoi : la ou les séries que l'objet nourrit ; script : le ou
#                les scripts qui le lisent, et qui le nomment
#   recoupe      renvoi : le test qui le confronte (tests/test_x.py::test_y)
#   limite       renvoi : la fiche ou la limite qui dit ce que le modèle n'en
#                sert pas
#   hors_modele  renvoi : la raison
#   a_lire       rien encore
# Plusieurs renvois se séparent par « ; ».
"""
#: Ce que chaque fichier dit de ses objets, sous l'en-tête commun, ligne à ligne.
PROPRES = {
    "baremes": ("les barèmes", (
        "LE THÈME est l'entrée du menu des barèmes qui nomme le barème, ou celle",
        "de la page d'accueil qui le lie ; vide, aucune ne l'atteint. LA DATE de",
        "modification est celle de la version qui a reçu le sort : le script la",
        "garde, et la veille la compare à la base.")),
    "exposes": ("les exposés", (
        "LE THÈME est l'entrée du menu de la réglementation que l'exposé désigne ;",
        "vide, l'exposé est hors du menu. LA DATE de modification est celle de la",
        "version qui a reçu le sort : le script la garde, et la veille la compare",
        "à la base.")),
    "listes": ("les listes de références", (
        "LE THÈME est le premier niveau du thème de chaque objet qui lie la liste.",
        "L'API ne date pas une liste.")),
    "references": ("les références", (
        "Une référence entre au registre liée par une collection ou une fenêtre,",
        "ou citée par une autre référence, de proche en proche : qui cite qui est",
        "dans citations.csv. LE THÈME est le premier niveau du thème de chaque",
        "objet qui la lie ; vide, seules d'autres références la citent. Le titre",
        "et la date du texte sont ceux que l'API en donne ; un titre vide dit une",
        "référence liée qu'elle ne sert pas.")),
    "fenetres": ("les fenêtres d'information", (
        "Une fenêtre s'ouvre d'un exposé, d'un barème ou d'une liste (#/infosupp/).",
        "LA NATURE est celle que l'API lui donne : exemple, lexique ou complement.",
        "LE THÈME est le premier niveau du thème de chaque objet qui la lie. LA",
        "DATE de modification est celle de la version qui a reçu le sort : le",
        "script la garde, et la veille la compare à la base. Un titre vide dit une",
        "fenêtre liée que l'API ne sert pas.")),
}
ENTETE_CITATIONS = """\
# Registre de la base de législation de la Cnav : les citations
# -------------------------------------------------------------
# Action 175 de la feuille de route. Une ligne par texte qu'une référence du
# registre cite : la base ne le dit qu'en lisant chaque référence, une à une,
# et ce fichier permet de la relire sans redemander ce qui n'a pas changé.
# Écrit par scripts/fetch/cnav_legislation.py, et par lui seul.
"""


# -- ce que dit un contenu --------------------------------------------------


def liens(contenu: str) -> list[tuple[str, str]]:
    """Ce que vise chaque lien d'un contenu, une fois chacun, dans l'ordre :
    ``(route, nom)``, la route étant ``bareme`` — un barème ou une liste, que le
    site ouvre par la même —, ``expose``, ``fenetre`` ou ``reference``,
    référence de la base ou PDF de ``/Pdf/``."""
    vus: list[tuple[str, str]] = []
    for adresse in _LIEN.findall(contenu):
        adresse = html.unescape(adresse)
        if route := _ROUTE.search(adresse):
            cible = (ROUTES[route.group(1)], route.group(2))
        elif fenetre := _FENETRE.search(adresse):
            cible = ("fenetre", fenetre.group(1))
        elif (pdf := _PDF.search(adresse)) and not adresse.startswith(("http:", "https:")):
            cible = ("reference", pdf.group(1))
        else:
            continue
        cible = (cible[0], urllib.parse.unquote(cible[1]).split("/")[-1].strip())
        if cible[1] and cible not in vus:
            vus.append(cible)
    return vus


def chemins(menu: list[dict]) -> dict[str, str]:
    """Le chemin de chaque entrée d'un menu, par son identifiant, dans l'ordre
    du menu : « Carrière > Cotisations-salaires > Taux de cotisations »."""
    trouves: dict[str, str] = {}
    for entree in menu:
        haut = entree["libelle"].strip()
        trouves[entree["id"]] = haut
        for theme in entree.get("themes") or []:
            milieu = f"{haut} > {theme['libelle'].strip()}"
            trouves[theme["id"]] = milieu
            for sous in theme.get("sousThemes") or []:
                trouves[sous["id"]] = f"{milieu} > {sous['libelle'].strip()}"
    return trouves


def themes_des_baremes(menu: list[dict], par_menu: dict[str, list[dict]],
                       contenus: dict[str, str]) -> dict[str, str]:
    """Le thème de chaque barème que le menu atteint : celui de la première
    entrée qui le nomme, sinon, de proche en proche, celui du barème qui le
    lie."""
    chemin = chemins(menu)
    themes: dict[str, str] = {}
    for ident, libelle in chemin.items():
        for fiche in par_menu.get(ident) or []:
            themes.setdefault(fiche["fileLeafRef"], libelle)
    file = list(themes)
    while file:
        nom = file.pop(0)
        for route, cible in liens(contenus.get(nom, "")):
            if route == "bareme" and cible in contenus and cible not in themes:
                themes[cible] = themes[nom]
                file.append(cible)
    return themes


def themes_lies(liens_par_objet: dict[tuple[str, str], list[tuple[str, str]]],
                themes: dict[tuple[str, str], str]) -> dict[tuple[str, str], str]:
    """Le thème d'une liste, d'une référence ou d'une fenêtre : le premier
    niveau du thème de chaque objet qui la lie, rangés et joints par « ; », une
    liste ou une fenêtre passant les siens à ce qu'elle lie à son tour. Une
    référence ne passe pas les siens aux textes qu'elle cite : de citation en
    citation, un article de code que toute la base cite les prendrait tous."""
    premiers: dict[tuple[str, str], set[str]] = defaultdict(set)
    for objet, theme in themes.items():
        if theme:
            premiers[objet].add(theme.split(" > ")[0])
    change = True
    while change:
        change = False
        for source, cibles in liens_par_objet.items():
            if source[0] == "references":
                continue
            for cible in cibles:
                if cible[0] in SANS_MENU and not premiers.get(source, set()) <= premiers[cible]:
                    premiers[cible] |= premiers[source]
                    change = True
    return {objet: " ; ".join(sorted(valeurs)) for objet, valeurs in premiers.items()
            if objet[0] in SANS_MENU and valeurs}


def fermeture(liens_par_objet: dict[tuple[str, str], list[tuple[str, str]]]) -> set[str]:
    """Les références de la base : celles que lient ses collections et ses
    fenêtres, puis, de proche en proche, celles que ces références citent."""
    atteintes = {nom for (genre, _), cibles in liens_par_objet.items() if genre != "references"
                 for cible_genre, nom in cibles if cible_genre == "references"}
    file = list(atteintes)
    while file:
        for genre, cible in liens_par_objet.get(("references", file.pop()), []):
            if genre == "references" and cible not in atteintes:
                atteintes.add(cible)
                file.append(cible)
    return atteintes


def instant(valeur: str) -> str:
    """Une date de modification, sans la zone que l'API y accroche."""
    return valeur.split("[")[0]


def date_du_texte(valeur: str) -> str:
    """Le jour d'un texte. L'API le date de son minuit à Paris, rendu en temps
    universel la veille au soir, à une ou deux heures près : douze heures de
    plus tombent dans le bon jour."""
    if not valeur:
        return ""
    moment = datetime.fromisoformat(instant(valeur).replace("Z", "+00:00"))
    return (moment + timedelta(hours=12)).date().isoformat()


# -- le registre ------------------------------------------------------------


def colonnes(genre: str) -> list[str]:
    nature = ["nature"] if genre == "fenetres" else []
    date = [DATES[genre]] if DATES[genre] else []
    return ["nom", "titre", *nature, "theme", *date, "sort", "renvoi", "script"]


def lire_registre(genre: str, dossier: Path = REGISTRE) -> dict[str, dict]:
    chemin = dossier / f"{genre}.csv"
    if not chemin.exists():
        return {}
    lignes = (ligne for ligne in chemin.read_text(encoding="utf-8").splitlines()
              if not ligne.startswith("#"))
    return {ligne["nom"]: ligne for ligne in csv.DictReader(lignes)}


def ecrire_registre(genre: str, registre: dict[str, dict], dossier: Path = REGISTRE) -> None:
    quoi, propre = PROPRES[genre]
    titre = f"Registre de la base de législation de la Cnav : {quoi}"
    ecrites = colonnes(genre)[:-3]
    entete = ENTETE.format(titre=titre, trait="-" * len(titre),
                           colonnes=", ".join(ecrites[:-1]) + " et " + ecrites[-1],
                           propre="\n# ".join(propre))
    flux = io.StringIO()
    ecrivain = csv.DictWriter(flux, fieldnames=colonnes(genre), lineterminator="\n",
                              extrasaction="ignore")
    ecrivain.writeheader()
    for nom in sorted(registre):
        ecrivain.writerow(registre[nom])
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / f"{genre}.csv").write_text(entete + flux.getvalue(), encoding="utf-8")


def lire_citations(dossier: Path = REGISTRE) -> dict[str, list[str]]:
    """Ce que chaque référence du registre cite, tel que la dernière lecture
    l'a vu."""
    chemin = dossier / CITATIONS
    if not chemin.exists():
        return {}
    cites: dict[str, list[str]] = defaultdict(list)
    lignes = (ligne for ligne in chemin.read_text(encoding="utf-8").splitlines()
              if not ligne.startswith("#"))
    for ligne in csv.DictReader(lignes):
        cites[ligne["reference"]].append(ligne["cite"])
    return dict(cites)


def ecrire_citations(citations: dict[str, list[str]], dossier: Path = REGISTRE) -> None:
    flux = io.StringIO()
    ecrivain = csv.writer(flux, lineterminator="\n")
    ecrivain.writerow(["reference", "cite"])
    for reference in sorted(citations):
        for cite in sorted(set(citations[reference])):
            ecrivain.writerow([reference, cite])
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / CITATIONS).write_text(ENTETE_CITATIONS + flux.getvalue(), encoding="utf-8")


def inscrire(registre: dict[str, dict], lus: dict[str, dict],
             cle_date: str | None) -> tuple[dict[str, dict], dict[str, list[str]]]:
    """Le registre d'un genre après une lecture de la base, et ce qu'elle y a
    trouvé de neuf, de changé depuis son sort et de disparu."""
    nouveau: dict[str, dict] = {}
    rapport: dict[str, list[str]] = {"nouveaux": [], "modifies": [], "disparus": []}
    for nom, lu in lus.items():
        ancien = registre.get(nom)
        if ancien is None:
            nouveau[nom] = {"nom": nom, **lu, "sort": "a_lire", "renvoi": "", "script": ""}
            rapport["nouveaux"].append(nom)
        elif ancien["sort"] == "a_lire":
            nouveau[nom] = {**ancien, **lu}
        else:
            nouveau[nom] = {**ancien, "titre": lu["titre"], "theme": lu["theme"]}
            if cle_date and lu.get(cle_date) != ancien.get(cle_date):
                rapport["modifies"].append(nom)
    for nom, ancien in registre.items():
        if nom not in lus:
            rapport["disparus"].append(nom)
            if ancien["sort"] != "a_lire":
                nouveau[nom] = ancien
    for noms in rapport.values():
        noms.sort()
    return dict(sorted(nouveau.items())), rapport


def references_a_lire(liens_par_objet: dict[tuple[str, str], list[tuple[str, str]]],
                      registre: dict[str, dict], changes: set[tuple[str, str]]) -> set[str]:
    """Les références à demander à l'API : celles que le registre ne porte
    pas, ou sans titre, et celles que lie un objet neuf ou changé."""
    a_lire: set[str] = set()
    for objet, cibles in liens_par_objet.items():
        for genre, nom in cibles:
            if genre == "references" and (
                    objet in changes or not (registre.get(nom) or {}).get("titre")):
                a_lire.add(nom)
    return a_lire


# -- la lecture -------------------------------------------------------------


def _obtenir(route: str, essais: int = 4):
    """Une route de l'API. La base flanche parfois — le 29 octobre 2026, elle a
    répondu 500 à ``/expose`` deux fois de suite, puis l'a servi — : la route
    se redemande, après une pause qui double à chaque essai."""
    for essai in range(1, essais + 1):
        try:
            return cnav_api.obtenir(route, delai=120)
        except (urllib.error.URLError, TimeoutError, OSError):
            if essai == essais:
                raise
            time.sleep(2 ** essai)


def _reference(nom: str) -> tuple[str, dict | None]:
    """Une référence, ou rien si l'API ne la sert pas : elle répond alors 500,
    à chaque fois, et la référence ne se redemande qu'une fois. La base en lie
    quelques-unes sous une casse fautive, « Circulaire_cnav_… », que l'API sert
    en minuscules : la fiche dit alors le nom servi."""
    for essai in dict.fromkeys((nom, nom.lower())):
        try:
            fiche = _obtenir("/reference/referencesByFileLeafRef/" + urllib.parse.quote(essai),
                             essais=2)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            continue
        if fiche := (fiche[0] if isinstance(fiche, list) and fiche else fiche):
            return nom, fiche
    return nom, None


def _fenetre(nom: str) -> tuple[str, dict | None]:
    """Une fenêtre d'information, avec sa nature — que son nom ne dit pas :
    ``ex_delai.aspx`` est un complément —, ou rien si l'API ne la sert pas."""
    try:
        reponse = _obtenir("/main/findPopupDetailsByFileLeafRef/" + urllib.parse.quote(nom),
                           essais=2)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return nom, None
    for cle, nature in NATURES.items():
        if isinstance(reponse, dict) and isinstance(reponse.get(cle), dict):
            return nom, {**reponse[cle], "nature": nature}
    return nom, None


def renommer(liens_par_objet: dict[tuple[str, str], list[tuple[str, str]]],
             noms: dict[str, str]) -> dict[tuple[str, str], list[tuple[str, str]]]:
    """Les liens, chaque référence sous le nom que l'API lui sert, une fois ;
    une référence renommée garde ce qu'elle cite."""
    renommes: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for (genre, nom), cibles in liens_par_objet.items():
        objet = (genre, noms.get(nom, nom) if genre == "references" else nom)
        renommes[objet] = list(dict.fromkeys([*renommes.get(objet, []), *(
            (cible_genre, noms.get(cible, cible) if cible_genre == "references" else cible)
            for cible_genre, cible in cibles)]))
    return renommes


def _garder(nom: str, donnees) -> None:
    BRUT.mkdir(parents=True, exist_ok=True)
    (BRUT / nom).write_text(json.dumps(donnees, ensure_ascii=False), encoding="utf-8")


def _titre(texte: str) -> str:
    return " ".join((texte or "").split())


def _index(fiches: list[dict], cle: str) -> dict[str, list[dict]]:
    """Les fiches d'une collection par leur nom : l'API en sert quelques-unes
    deux fois, à l'identique le plus souvent."""
    par_nom: dict[str, list[dict]] = defaultdict(list)
    for fiche in fiches:
        if fiche["id"] not in {f["id"] for f in par_nom[fiche[cle]]}:
            par_nom[fiche[cle]].append(fiche)
    return dict(par_nom)


def _resumer(noms: list[str]) -> str:
    return ", ".join(noms[:12]) + (" …" if len(noms) > 12 else "")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--tout", action="store_true",
                           help="redemande chaque référence, même inchangée")
    arguments = analyseur.parse_args(argv)

    collections = {"baremes": _obtenir("/baremes"), "exposes": _obtenir("/expose"),
                   "listes": _obtenir("/liste")}
    menu_baremes = _obtenir("/menu/menuBareme")
    menu_reglementation = _obtenir("/menu/menuReglementation")
    with ThreadPoolExecutor(EN_PARALLELE) as pool:
        identifiants = list(chemins(menu_baremes))
        par_menu = dict(zip(identifiants, pool.map(
            lambda ident: _obtenir(f"/baremes/baremesByMenuId/{ident}"), identifiants)))
    for nom, donnees in (("baremes.json", collections["baremes"]),
                         ("expose.json", collections["exposes"]),
                         ("liste.json", collections["listes"]),
                         ("menuBareme.json", menu_baremes),
                         ("menuReglementation.json", menu_reglementation),
                         ("baremes_par_menu.json", par_menu)):
        _garder(nom, donnees)

    objets = {"baremes": _index(collections["baremes"], "fileLeafRef"),
              "exposes": _index(collections["exposes"], "fileLeafRef"),
              "listes": _index(collections["listes"], "file_leaf_ref")}
    contenus = {genre: {nom: "".join(f["contenu"] for f in fiches)
                        for nom, fiches in par_nom.items()}
                for genre, par_nom in objets.items()}

    # Ce que chaque objet lie, rangé par genre ; ce qui ne mène à rien.
    minuscules = {genre: {nom.lower(): nom for nom in par_nom}
                  for genre, par_nom in objets.items()}

    def trouver(genres: tuple[str, ...], cible: str) -> tuple[str, str] | None:
        for genre in genres:
            if cible in objets[genre]:
                return genre, cible
        for genre in genres:
            if cible.lower() in minuscules[genre]:
                return genre, minuscules[genre][cible.lower()]
        return None

    liens_par_objet: dict[tuple[str, str], list[tuple[str, str]]] = {}
    morts: set[tuple[str, str]] = set()

    def ranger(genre: str, nom: str, contenu: str) -> None:
        cibles: list[tuple[str, str]] = []
        for route, cible in liens(contenu):
            if route in ("reference", "fenetre"):
                trouve = (f"{route}s", cible)
            else:
                trouve = trouver(("baremes", "listes") if route == "bareme" else ("exposes",),
                                 cible)
            if trouve is None:
                morts.add((route, cible))
            elif trouve != (genre, nom) and trouve not in cibles:
                cibles.append(trouve)
        liens_par_objet[(genre, nom)] = cibles

    for genre, par_nom in contenus.items():
        for nom, contenu in par_nom.items():
            ranger(genre, nom, contenu)

    # Les fenêtres : peu nombreuses, relues chaque fois, avec ce qu'elles lient.
    fenetres: dict[str, dict | None] = {}
    a_ouvrir = {nom for cibles in liens_par_objet.values()
                for genre, nom in cibles if genre == "fenetres"}
    while a_ouvrir:
        with ThreadPoolExecutor(EN_PARALLELE) as pool:
            for nom, fiche in pool.map(_fenetre, sorted(a_ouvrir)):
                fenetres[nom] = fiche
                ranger("fenetres", nom, (fiche or {}).get("contenu") or "")
        a_ouvrir = {nom for (source, _), cibles in liens_par_objet.items() if source == "fenetres"
                    for genre, nom in cibles if genre == "fenetres"} - set(fenetres)
    _garder("fenetres.json", fenetres)

    # Les thèmes que donnent les menus.
    themes_baremes = themes_des_baremes(menu_baremes, par_menu, contenus["baremes"])
    chemin_reglementation = chemins(menu_reglementation)
    themes = {("baremes", nom): theme for nom, theme in themes_baremes.items()}
    themes |= {("exposes", nom): chemin_reglementation.get(fiches[0].get("menuId") or "", "")
               for nom, fiches in objets["exposes"].items()}

    # Le registre, sous les noms qu'il connaît, et ce que ses références citent.
    registre = {genre: lire_registre(genre) for genre in GENRES}
    connues = {nom.lower(): nom for nom in registre["references"]}

    def connue(nom: str) -> str:
        return nom if nom in registre["references"] else connues.get(nom.lower(), nom)

    liens_par_objet = renommer(liens_par_objet, {
        nom: connue(nom) for cibles in liens_par_objet.values()
        for genre, nom in cibles if genre == "references" and connue(nom) != nom})
    for reference, cites in lire_citations().items():
        liens_par_objet[("references", reference)] = [("references", cite) for cite in cites]

    # Ce qui a changé depuis le registre, et les références à redemander, de
    # proche en proche : ce qu'une référence relue cite remplace ce que le
    # registre en gardait.
    changes = {(genre, nom) for genre in ("baremes", "exposes")
               for nom, fiches in objets[genre].items()
               if (registre[genre].get(nom) or {}).get("modifie_le")
               != instant(max(f["dateModification"] for f in fiches))}
    changes |= {("listes", nom) for nom in objets["listes"] if nom not in registre["listes"]}
    changes |= {("fenetres", nom) for nom, fiche in fenetres.items()
                if (registre["fenetres"].get(nom) or {}).get("modifie_le")
                != instant((fiche or {}).get("date_modification") or "")}
    a_lire = fermeture(liens_par_objet) if arguments.tout else references_a_lire(
        liens_par_objet, registre["references"], changes)
    gardees = {}
    if (BRUT / "references.json").exists():
        gardees = json.loads((BRUT / "references.json").read_text(encoding="utf-8"))
    lues: dict[str, dict | None] = {}
    while a_lire:
        print(f"{len(a_lire)} références à demander à l'API")
        with ThreadPoolExecutor(EN_PARALLELE) as pool:
            for rang, (nom, fiche) in enumerate(pool.map(_reference, sorted(a_lire)), 1):
                lues[nom] = fiche
                if fiche is not None:
                    gardees[fiche.get("file_leaf_ref") or nom] = fiche
                    liens_par_objet[("references", nom)] = list(dict.fromkeys(
                        ("references", connue(cible))
                        for route, cible in liens(fiche.get("contenu") or "")
                        if route == "reference" and cible.lower() != nom.lower()))
                if rang % 250 == 0:
                    print(f"  {rang} / {len(a_lire)}")
        a_lire = {cible for nom in a_lire for genre, cible in liens_par_objet.get(("references", nom), [])
                  if arguments.tout or not (registre["references"].get(cible) or {}).get("titre")
                  } - set(lues)
    _garder("references.json", gardees)
    servis = {nom: fiche["file_leaf_ref"] for nom, fiche in lues.items()
              if fiche and fiche.get("file_leaf_ref", nom).lower() == nom.lower()
              and fiche["file_leaf_ref"] != nom}
    liens_par_objet = renommer(liens_par_objet, servis)
    lues = {servis.get(nom, nom): fiche for nom, fiche in lues.items()}
    atteintes = fermeture(liens_par_objet)
    themes |= themes_lies(liens_par_objet, themes)

    # Ce que la base dit de chaque objet, et le registre qui s'en suit.
    lus: dict[str, dict[str, dict]] = {genre: {} for genre in GENRES}
    for genre in ("baremes", "exposes"):
        for nom, fiches in objets[genre].items():
            lus[genre][nom] = {"titre": _titre(fiches[0]["titre"]),
                               "theme": themes.get((genre, nom), ""),
                               "modifie_le": instant(max(f["dateModification"] for f in fiches))}
    for nom, fiches in objets["listes"].items():
        lus["listes"][nom] = {"titre": " / ".join(dict.fromkeys(_titre(f["titre"]) for f in fiches)),
                              "theme": themes.get(("listes", nom), "")}
    for nom in sorted(atteintes):
        if nom in lues:
            fiche = lues[nom] or {}
            titre, date = _titre(fiche.get("titre", "")), date_du_texte(fiche.get("date_textes", ""))
        else:
            ancienne = registre["references"].get(nom) or {}
            titre, date = ancienne.get("titre", ""), ancienne.get("date_texte", "")
        lus["references"][nom] = {"titre": titre, "theme": themes.get(("references", nom), ""),
                                  "date_texte": date}
    for nom, fiche in sorted(fenetres.items()):
        fiche = fiche or {}
        lus["fenetres"][nom] = {"titre": _titre(fiche.get("titre", "")),
                                "nature": fiche.get("nature", ""),
                                "theme": themes.get(("fenetres", nom), ""),
                                "modifie_le": instant(fiche.get("date_modification") or "")}

    for genre in GENRES:
        nouveau, rapport = inscrire(registre[genre], lus[genre], DATES[genre])
        ecrire_registre(genre, nouveau)
        sorts = defaultdict(int)
        for ligne in nouveau.values():
            sorts[ligne["sort"]] += 1
        print(f"{genre} : {len(nouveau)} — " + ", ".join(
            f"{sorts[sort]} {sort}" for sort in SORTS if sorts[sort]))
        for quoi, noms in rapport.items():
            if noms:
                print(f"  {len(noms)} {quoi} : {_resumer(noms)}")
    citations = {nom: [cible for genre, cible in liens_par_objet.get(("references", nom), [])
                       if genre == "references" and cible in atteintes and cible != nom]
                 for nom in atteintes}
    ecrire_citations({nom: cites for nom, cites in citations.items() if cites})
    print(f"{sum(len(set(cites)) for cites in citations.values())} citations entre références")
    if morts:
        print(f"{len(morts)} liens ne mènent à aucun objet de la base : "
              + _resumer([f"{route}:{cible}" for route, cible in sorted(morts)]))
    illisibles = sorted(nom for nom, fiche in [*lues.items(), *fenetres.items()] if not fiche)
    if illisibles:
        print(f"{len(illisibles)} objets liés que l'API ne sert pas : {_resumer(illisibles)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
