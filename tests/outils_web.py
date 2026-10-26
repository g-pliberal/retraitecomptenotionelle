"""Ce que les tests du site se partagent.

Le site lu par node, ses pages et leurs titres, la feuille de style, le
contexte du modèle et les saisies que le pont bâtit, le rendu d'une page
entière, et quelques lectures du texte rendu. Les trois fichiers qui testent le site — ``test_web.py``,
``test_web_saisie.py`` et ``test_web_revues.py`` — les importent d'ici ;
ce module n'est pas un fichier de tests, et pytest ne le collecte pas.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

import pytest

from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.web.site import disponible, module, site
from outils_pont import Saisies, saisie_du_portage

g = module("gabarit")
pages = module("pages")
#: Les pages et les pages agrégées, que des tests parcourent : lues à la
#: collecte, puisque ``parametrize`` les demande.
TITRES = pages.TITRES if disponible() else {}
PAGES_AGREGEES = pages.PAGES_AGREGEES if disponible() else {}
#: La feuille de style du site, telle qu'il la charge.
FEUILLE_DE_STYLE = (Path(__file__).resolve().parents[1] / "moteur" / "style.css").read_text(
    encoding="utf-8")


def page_et_routeur() -> str:
    """``index.html`` et son routeur, ``moteur/js/routeur.js``, bout à bout : ce
    que les tests lisent du script de la page, depuis qu'il en est sorti dans
    son module (action 174)."""
    racine = Path(__file__).resolve().parents[1]
    return "\n".join((racine / chemin).read_text(encoding="utf-8")
                     for chemin in ("index.html", "moteur/js/routeur.js"))


#: Le contexte et les pages rendues, un par processus : les trois fichiers du
#: site partagent ce que le seul ``test_web.py`` partageait avant son
#: découpage, sans quoi chaque processus les refaisait trois fois — une minute
#: de plus pour la suite, mesurée le 30 septembre 2026.
_PARTAGES: dict = {}


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    """Le contexte Python : le centre du coût, que le portage n'a pas — le
    coût, les comptes, la dépense, le bilan. La saisie, elle, se lit dans le
    portage (``outils_pont``, action 161, étape 6)."""
    if "contexte" not in _PARTAGES:
        _PARTAGES["contexte"] = Contexte()
    return _PARTAGES["contexte"]


@pytest.fixture(scope="module")
def saisies() -> Saisies:
    """Les saisies des tests : la carrière qu'en bâtit le portage, par le pont,
    et le moteur Python qui la simule, un simulateur par jeu de paramètres."""
    if "saisies" not in _PARTAGES:
        _PARTAGES["saisies"] = Saisies()
    return _PARTAGES["saisies"]


def montants_du_portage(requete: dict, simuler: bool = True):
    """Les montants que la page applique à une saisie, ceux du portage
    (``Montants.depuis``, ``moteur/js/contexte.js``) : sur sa simulation, qui
    fixe le taux de la personne, ou, ``simuler=False``, sans elle, comme la
    page prend ceux d'un départ de l'estimation."""
    saisie, portage = saisie_du_portage(requete), site().contexte
    simulateur = portage.simulateur(saisie.parametres(portage.base))
    if not simuler:
        return module("contexte").Montants.depuis(saisie, simulateur)
    return module("contexte").Montants.depuis(saisie, simulateur, portage.simuler(saisie))


def _echelle():
    """L'échelle des salaires du jeu de paramètres par défaut, celle du portage.

    ``Saisie.parcours`` en a besoin depuis que le formulaire accepte des euros :
    convertir « 2 500 € par mois » en multiple suppose le salaire moyen.
    """
    return site().contexte.echelle(saisie_du_portage({"montants": "brut"}))


@pytest.fixture(scope="module")
def page():
    """Rend une page entière, comme le fait ``index.html`` dans le navigateur.

    Le site n'assemble jamais autre chose : l'en-tête, le corps rendu, le pied.
    """
    # Le rendu est mémorisé : une trentaine de tests demandent la même page,
    # et `/cout` coûtait trois secondes et demie à chaque fois. Rendre deux
    # fois la même adresse donne la même chaîne — et une chaîne ne se modifie
    # pas, donc la partager ne peut pas faire communiquer deux tests.
    memo: dict[tuple, str] = _PARTAGES.setdefault("pages", {})

    def rendu(chemin: str = "/simuler", **parametres: object) -> str:
        arguments = {nom: str(valeur) for nom, valeur in parametres.items()}
        cle = (chemin, tuple(sorted(arguments.items())))
        if cle not in memo:
            memo[cle] = site().page(chemin, arguments)
        return memo[cle]

    return rendu


def _sans_blocs(corps: str, balise: str, ouverture: str) -> str:
    """``corps`` sans les blocs ``<balise …>`` reconnus par ``ouverture``.

    Les blocs s'imbriquent — le tableau de points d'un graphique vit dans une
    carte, elle-même parfois dans une section repliée —, et une expression
    régulière non gourmande s'arrêterait à la première fermeture. On apparie
    donc les balises, en comptant chaque ``<balise`` ouverte dans le bloc.
    """
    morceaux = []
    position = 0
    debut = re.compile(ouverture)
    bornes = re.compile(rf"<{balise}\b|</{balise}>")
    while position < len(corps):
        trouve = debut.search(corps, position)
        if not trouve:
            morceaux.append(corps[position:])
            break
        morceaux.append(corps[position:trouve.start()])
        profondeur = 0
        fin = len(corps)
        for borne in bornes.finditer(corps, trouve.start()):
            profondeur += -1 if borne.group(0).startswith("</") else 1
            if profondeur == 0:
                fin = borne.end()
                break
        position = fin
    return "".join(morceaux)


def _hors_depliants(corps: str) -> str:
    """Ce que la page montre sans qu'on ait rien déplié.

    Les sections repliées, les panneaux d'onglets que la feuille de style
    cache tant que leur onglet n'est pas choisi, et les bulles du glossaire,
    fermées tant qu'on ne les demande pas : rien de tout cela ne se lit à
    l'ouverture de la page.

    LES OPTIONS D'UN MENU DÉROULANT non plus. Un ``<select>`` fermé occupe une
    ligne et montre un libellé, quel que soit le nombre d'options qu'il porte ;
    les compter reviendrait à imputer au lecteur de l'accueil les soixante-dix
    statuts d'affiliation du catalogue — quatre cent cinquante mots qu'il ne
    voit pas, et qui feraient dépasser son budget au simple fait que le site
    connaît beaucoup de régimes. Le menu est donc réduit à ce qu'il montre.
    """
    sans_bulles = re.sub(r'<span class="bulle"[^>]*hidden>.*?</span>', " ", corps,
                         flags=re.S)
    sans_options = re.sub(r"<select\b[^>]*>.*?</select>", "<select></select>",
                          sans_bulles, flags=re.S)
    return _sans_blocs(
        _sans_blocs(sans_options, "details", r"<details\b"),
        "div", r'<div class="panneau"[^>]*\bhidden>',
    )


#: Une carrière ordinaire, qui déclenche les sept sections de détail de la page
#: de résultats : salarié du privé, départ après la bascule, indexation par
#: défaut. C'est la simulation sur laquelle se mesure la discipline de cette
#: page, que le budget de lecture ci-dessus ne voit pas — il rend « /simuler »
#: sans paramètres, donc sans résultats.
SIMULATION_TEMOIN = {
    "naissance": "1975-01-01",
    "debut": "1996-01-01",
    "liquidation": "2039-01-01",
    "statut": "salarie_prive_non_cadre",
    "unite_revenu": "euros_mois",
    "salaire": "3500",
}


def _prose(corps: str) -> str:
    """Le texte d'une page hors de ses tableaux, où « — » est une case vide."""
    sans_tables = re.sub(r"<table.*?</table>", " ", corps, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", sans_tables)))
