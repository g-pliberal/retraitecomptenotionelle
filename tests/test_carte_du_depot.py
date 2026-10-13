"""La carte du dépôt dit vrai, et elle reste hors du site.

`docs/carte_du_depot.md` est la vue d'ensemble du dépôt, en schémas, écrite à
la main pour qu'on s'y retrouve. Ses chiffres sont ancrés (`zones.yaml`, régime
`etat`) et se recalculent seuls ; le reste de ce qu'elle affirme, ce test le
confronte au dépôt : les fichiers qu'elle cite existent, ses adresses sont
celles du site, et chaque scénario y porte les couches de son univers, dans
l'ordre où elles se posent. Un fichier renommé, une page ou une couche de plus,
et la carte doit suivre.

Elle sert à suivre le dépôt, pas au lecteur du simulateur : le propriétaire l'a
voulue hors du site (13 octobre 2026). Le dernier test y veille.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
CARTE = RACINE / "docs" / "carte_du_depot.md"

#: Une incise de code : un chemin, une commande, une adresse, un identifiant.
CODE = re.compile(r"`([^`\n]+)`")
#: Ce qui fait d'un mot un nom de fichier, quand il ne porte pas de « / ».
EXTENSIONS = (".py", ".js", ".mjs", ".md", ".yaml", ".yml", ".json", ".sh", ".css",
              ".html", ".csv")


def _texte() -> str:
    return CARTE.read_text(encoding="utf-8")


def _hors_schemas(texte: str) -> str:
    """La prose et les tableaux, sans les blocs clôturés des schémas."""
    return re.sub(r"```.*?```", "", texte, flags=re.DOTALL)


def _chemins(texte: str) -> list[str]:
    """Les chemins que la carte cite en incise : ``docs/etat.md``, et ceux des
    commandes, ``python scripts/reprise.py 138``. Un gabarit,
    ``docs/feuille_de_route/<action>/``, vaut pour le dossier qui le précède."""
    chemins = []
    for incise in CODE.findall(_hors_schemas(texte)):
        for mot in incise.split():
            mot = mot.rstrip(".,;:")
            if mot.startswith(("#", "<!--", "http")):
                continue
            if "/" not in mot and not mot.endswith(EXTENSIONS):
                continue
            chemins.append(mot.split("<", 1)[0])
    return chemins


def _tableau(texte: str, entete: str) -> list[list[str]]:
    """Les lignes du tableau dont l'en-tête commence par ``entete``, cellule
    par cellule, sans la ligne de séparation."""
    lignes = texte.splitlines()
    debut = next(i for i, ligne in enumerate(lignes) if ligne.startswith(f"| {entete}"))
    rangees = []
    for ligne in lignes[debut:]:
        if not ligne.startswith("|"):
            break
        rangees.append([cellule.strip() for cellule in ligne.strip().strip("|").split("|")])
    return [rangees[0]] + rangees[2:]


def test_chaque_chemin_que_la_carte_cite_existe():
    chemins = _chemins(_texte())
    assert len(chemins) > 20, "la carte ne cite presque plus rien : la lecture a dérivé"
    absents = sorted({c for c in chemins if not (RACINE / c).exists()})
    assert not absents, (
        f"la carte cite des fichiers qui n'existent plus : {absents} — le dépôt a "
        "bougé, et docs/carte_du_depot.md doit suivre")


def test_les_pages_de_la_carte_sont_celles_du_site():
    js = (RACINE / "moteur" / "js" / "pages.js").read_text(encoding="utf-8")
    bloc = re.search(r"export const TITRES = \{(.*?)\};", js, re.DOTALL)
    assert bloc, "TITRES introuvable dans moteur/js/pages.js"
    site = dict(re.findall(r'"([^"]+)":\s*"([^"]+)"', bloc.group(1)))
    carte = {}
    for page, adresse, *_ in _tableau(_texte(), "Page |")[1:]:
        route = re.fullmatch(r"`#(/[^`]*)`", adresse)
        assert route, f"« {adresse} » n'est pas une adresse du site"
        carte[route.group(1)] = page
    assert carte == site, (
        "les pages de la carte ne sont plus celles du site (TITRES, "
        f"moteur/js/pages.js) : carte {carte}, site {site}")


def test_chaque_scenario_porte_les_couches_de_son_univers():
    univers = {}
    for chemin in sorted((RACINE / "data" / "reference" / "univers").glob("*.yaml")):
        donnees = yaml.safe_load(chemin.read_text(encoding="utf-8"))
        univers[donnees["numero"]] = donnees["couches"]
    tableau = _tableau(_texte(), "Couche")
    numeros = [int(re.match(r"\d+", cellule).group(0)) for cellule in tableau[0][1:]]
    assert numeros == sorted(univers), (
        f"la carte montre les scénarios {numeros}, les univers sont {sorted(univers)}")
    ordre, coches = [], {}
    for rangee in tableau[1:]:
        couche = re.match(r"`(\w+)`", rangee[0])
        assert couche, f"« {rangee[0]} » ne nomme pas sa couche"
        ordre.append(couche.group(1))
        coches[couche.group(1)] = {n for n, case in zip(numeros, rangee[1:]) if case == "●"}
    toutes = {c for couches in univers.values() for c in couches}
    assert set(ordre) == toutes, (
        f"couches de la carte {sorted(ordre)}, couches des univers {sorted(toutes)}")
    for numero, couches in univers.items():
        portees = {c for c, ou in coches.items() if numero in ou}
        assert portees == set(couches), (
            f"scénario {numero} : la carte coche {sorted(portees)}, "
            f"son univers pose {couches}")
        rangs = [ordre.index(c) for c in couches]
        assert rangs == sorted(rangs), (
            f"scénario {numero} : la carte ne range pas ses couches dans l'ordre où "
            f"elles se posent, {couches}")


def test_la_carte_n_est_pas_une_page_du_site():
    """Rien de ce que charge le navigateur ne la nomme : ni `index.html`, ni le
    moteur et le texte des pages, ni la feuille de style."""
    charge = [RACINE / "index.html", RACINE / "moteur" / "style.css",
              *sorted((RACINE / "moteur" / "js").rglob("*.js"))]
    la_nomment = [str(f.relative_to(RACINE)) for f in charge
                  if "carte_du_depot" in f.read_text(encoding="utf-8")]
    assert not la_nomment, f"le site renvoie à la carte du dépôt : {la_nomment}"
