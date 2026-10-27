"""Ce qu'une page charge en s'ouvrant (action 174, étape 5).

Chaque page arrive toute faite : pour la lire, le routeur n'a qu'à l'animer —
replier ses tableaux, brancher ses formulaires, ouvrir la section que l'adresse
nomme. Il importait pourtant, dès l'ouverture, tout le moteur et le texte des
neuf pages : soixante-seize modules, 3,3 Mo bruts, dont trois seulement
servaient (mesuré le 26 octobre 2026 dans Chromium, sur Pourquoi changer). Le
reste se charge désormais au premier calcul, ou au premier geste qui en a
besoin.

Ces tests lisent les imports des modules, sans navigateur ;
``test_adresses_navigateur.py`` vérifie ce que le navigateur demande vraiment.
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path

import pytest

from retraite_notionnelle.web.site import disponible, module

JS = Path(__file__).resolve().parents[1] / "moteur" / "js"

#: Ce que le démarrage importe, et rien d'autre : le routeur, la lecture des
#: adresses, les clés que la saisie partage avec elles, le gabarit (les tracés,
#: les liens, les images à partager), son format, et le calendrier.
AU_DEMARRAGE = {"routeur.js", "adresses.js", "cles.js", "gabarit.js", "format.js",
                "calendrier.js"}

#: Ce que le routeur importe au premier calcul : la saisie, le contexte du
#: moteur, le texte des pages et la lecture du relevé.
A_LA_DEMANDE = {"saisie.js", "contexte.js", "pages.js", "droit/releve.js"}

#: Un import statique, sur une ou plusieurs lignes : ``import … from "./x.js"``,
#: ``export … from "./x.js"``, ou ``import "./x.js"``.
STATIQUES = (re.compile(r'^\s*(?:import|export)\b[^;]*?\bfrom\s*"(\.{1,2}/[^"]+)"', re.M),
             re.compile(r'^\s*import\s*"(\.{1,2}/[^"]+)"', re.M))
#: Un import à la demande : ``import("./x.js")``.
DYNAMIQUE = re.compile(r'\bimport\(\s*"(\.{1,2}/[^"]+)"\s*\)')


def _code(module_js: str) -> str:
    """Le code d'un module, sans ses commentaires : un import cité dans une
    phrase n'en est pas un."""
    texte = (JS / module_js).read_text(encoding="utf-8")
    texte = re.sub(r"/\*.*?\*/", "", texte, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", texte)


def _resolus(module_js: str, cibles) -> set[str]:
    dossier = posixpath.dirname(module_js)
    return {posixpath.normpath(posixpath.join(dossier, cible)) for cible in cibles}


def statiques(module_js: str) -> set[str]:
    code = _code(module_js)
    return _resolus(module_js, [cible for motif in STATIQUES for cible in motif.findall(code)])


def dynamiques(module_js: str) -> set[str]:
    return _resolus(module_js, DYNAMIQUE.findall(_code(module_js)))


def fermeture(depart: str = "routeur.js") -> set[str]:
    """Tout ce que le navigateur charge avec ce module, avant d'en exécuter une
    ligne : ses imports statiques, et les leurs."""
    vus, a_voir = set(), [depart]
    while a_voir:
        courant = a_voir.pop()
        if courant not in vus:
            vus.add(courant)
            a_voir.extend(statiques(courant))
    return vus


def test_le_demarrage_n_importe_que_de_quoi_animer_la_page():
    """Le simulateur, les étapes du droit, la saisie et le texte des neuf pages
    n'en sont pas : une page toute faite se lit et s'anime sans eux."""
    assert fermeture() == AU_DEMARRAGE


def test_le_moteur_et_le_texte_des_pages_se_chargent_a_la_demande():
    """Le routeur les importe à la demande, et rien de ce que le démarrage charge
    ne les importe autrement."""
    assert A_LA_DEMANDE <= dynamiques("routeur.js")
    assert not A_LA_DEMANDE & fermeture()


@pytest.mark.skipif(not disponible(), reason="node absent : les modules ne se lisent pas sans lui")
def test_la_saisie_reprend_les_cles_que_le_demarrage_lit():
    """Les clés des règles et les motifs sans emploi vivent dans ``cles.js``, que
    le démarrage lit ; la saisie les reprend telles quelles pour ses autres
    lecteurs — le texte des pages, le portage, les tests."""
    cles, saisie = module("cles"), module("saisie")
    assert list(saisie.CLES_MODELISATION) == list(cles.CLES_MODELISATION)
    assert list(saisie.SANS_EMPLOI) == list(cles.SANS_EMPLOI)
    assert "indexation" in cles.CLES_MODELISATION and "naissance" not in cles.CLES_MODELISATION
