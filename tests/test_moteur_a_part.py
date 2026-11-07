"""Le moteur à part du site (action 187, étape 2).

Le moteur d'une carrière doit servir sans le site : à la fabrique déjà, que
``pont.mjs`` fait calculer par node, et demain à d'autres, qui l'importeront
chez eux (décisions 34 et 35 du programme). Le partage est simple : le site
importe le calcul pour le montrer ; le calcul n'importe rien du site. Aucun
fichier ne se déplace pour cela : la liste des modules du site, ici, et ces
tests le gardent.

Ces tests lisent les imports des modules, sans navigateur, comme
``test_demarrage.py`` ; ils ne laissent passer aucun import dont la cible se
calcule, qu'ils ne sauraient lire.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from retraite_notionnelle.web.site import disponible, module

RACINE = Path(__file__).resolve().parents[1]
JS = RACINE / "moteur" / "js"
PONT = RACINE / "src" / "retraite_notionnelle" / "pont.mjs"

#: Les modules du site, dans ``moteur/js/`` : ils montrent — le texte des pages,
#: le gabarit et ses tracés, le routeur qui anime la page, la lecture des
#: adresses —, et importent le calcul. Tout autre module du dossier est du
#: calcul. ``cles.js`` en est : il ne porte que le vocabulaire de la saisie —
#: les motifs sans emploi, les clés qui décrivent les règles —, sans aucun
#: import, et quiconque décrit une carrière au moteur en a besoin ; le
#: démarrage du site le lit, comme il lit ``format.js`` et ``calendrier.js``.
SITE = {"pages.js", "gabarit.js", "routeur.js", "adresses.js"}

#: Une cible d'import écrite en clair, entre guillemets simples, doubles ou
#: obliques, sans rien d'interpolé.
_CIBLE = r"""(["'`])([^"'`$]+)\1"""
#: ``import … from "x"``, ``export … from "x"``, ``import "x"``.
STATIQUES = (re.compile(r"^\s*(?:import|export)\b[^;]*?\bfrom\s*" + _CIBLE, re.M),
             re.compile(r"^\s*import\s*" + _CIBLE, re.M))
#: ``import("x")`` ; et tout ``import(``, pour trouver ceux dont la cible se
#: calcule.
DYNAMIQUE = re.compile(r"\bimport\s*\(\s*" + _CIBLE + r"\s*\)")
TOUT_DYNAMIQUE = re.compile(r"\bimport\s*\(")


def _code(chemin: Path) -> str:
    """Le code d'un module, sans ses commentaires : un import cité dans une
    phrase n'en est pas un."""
    texte = chemin.read_text(encoding="utf-8")
    texte = re.sub(r"/\*.*?\*/", "", texte, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", texte)


def imports(chemin: Path) -> set[Path]:
    """Les modules qu'un module importe, statiquement ou à la demande, résolus
    en chemins ; les modules de node (``node:fs``) n'en sont pas."""
    code = _code(chemin)
    cibles = [m.group(2) for motif in (*STATIQUES, DYNAMIQUE) for m in motif.finditer(code)]
    return {(chemin.parent / cible).resolve() for cible in cibles if cible.startswith(".")}


def calcules(chemin: Path) -> int:
    """Combien d'imports à la demande d'un module ont une cible calculée."""
    code = _code(chemin)
    return len(TOUT_DYNAMIQUE.findall(code)) - len(DYNAMIQUE.findall(code))


def du_site(chemin: Path) -> bool:
    return chemin.resolve() in {(JS / nom).resolve() for nom in SITE}


def modules_du_calcul() -> list[Path]:
    return sorted(chemin for chemin in JS.rglob("*.js") if not du_site(chemin))


def nom(chemin: Path) -> str:
    return chemin.resolve().relative_to(RACINE).as_posix()


def test_les_modules_du_site_existent():
    """Un module du site renommé ou parti laisserait la garde sans objet."""
    assert all((JS / module_js).is_file() for module_js in SITE)
    assert len(modules_du_calcul()) > 50


def test_aucun_module_du_calcul_n_importe_le_site():
    """Le site importe le calcul ; l'inverse lierait le moteur au site, et qui
    voudrait l'appeler ailleurs devrait emporter les pages avec lui."""
    liens = {nom(chemin): sorted(nom(cible) for cible in imports(chemin) if du_site(cible))
             for chemin in modules_du_calcul()}
    assert {module_js: cibles for module_js, cibles in liens.items() if cibles} == {}


def test_aucun_import_du_calcul_n_a_de_cible_calculee():
    """Un ``import(variable)`` ne se lit pas sans l'exécuter : la garde ne
    saurait dire s'il tire le site."""
    assert {nom(chemin): n for chemin in modules_du_calcul() if (n := calcules(chemin))} == {}


def test_le_pont_ne_tire_rien_du_site():
    """Le pont fait calculer le moteur par node pour la fabrique : premier client
    qui n'est pas le site, il ne charge rien de lui."""
    vus, a_voir = set(), [PONT.resolve()]
    while a_voir:
        courant = a_voir.pop()
        if courant not in vus:
            vus.add(courant)
            a_voir.extend(imports(courant))
    assert sorted(nom(chemin) for chemin in vus if du_site(chemin)) == []
    assert calcules(PONT) == 0


@pytest.mark.skipif(not disponible(), reason="node absent : les modules ne se lisent pas sans lui")
def test_le_calcul_ecrit_ses_nombres_a_la_francaise():
    """Les refus de la saisie et du contexte disent leurs montants en français :
    virgule décimale, espace fine insécable des milliers et devant l'euro. Le
    calcul les écrit par ``format.js``, que le gabarit reprend tel quel."""
    fine = " "
    formats, gabarit = module("format"), module("gabarit")
    assert formats.nombre(1234.5) == f"1{fine}234,50"
    assert formats.nombre(2.675, 0) == "3"
    assert formats.euros(1234567.4) == f"1{fine}234{fine}567{fine}€"
    for valeur in (0.5, 1.5, 999.995, 12345.678):
        assert gabarit.nombre(valeur, 2) == formats.nombre(valeur, 2)
        assert gabarit.euros(valeur) == formats.euros(valeur)
