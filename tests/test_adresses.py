"""Les adresses du site (action 174, étape 4) : la page dans le chemin, le
lecteur derrière le ``#`` — sa carrière, ses réglages —, que le navigateur ne
transmet à aucun serveur ; et l'ancienne forme, la page derrière le ``#``
(``#/cout?indexation=prix``), que portent les partages publiés avant le
changement. ``moteur/js/adresses.js`` les lit toutes deux, et le routeur ne
lit plus les adresses qu'à travers lui.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from retraite_notionnelle.web.site import disponible, module

#: Les adresses se lisent par node : sans lui, rien ne se lit.
pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : les adresses du site ne se lisent pas sans lui")

RACINE = Path(__file__).resolve().parents[1]
CARRIERE = "naissance=1965-03-01&sexe=H"
LUE = {"naissance": "1965-03-01", "sexe": "H"}


@pytest.mark.parametrize("chemin, ancre, page, parametres, section", [
    # La nouvelle forme : la page dans le chemin, relatif à la racine du site.
    ("", "", "/", {}, ""),
    ("index.html", "", "/", {}, ""),
    ("cout/", "", "/cout", {}, ""),
    ("cout/index.html", "", "/cout", {}, ""),
    ("cout", "", "/cout", {}, ""),
    ("cout/", "#indexation=prix", "/cout", {"indexation": "prix"}, ""),
    ("simuler/", CARRIERE, "/simuler", LUE, ""),
    ("", "indexation=prix", "/", {"indexation": "prix"}, ""),
    # Un mot sans « = » derrière le `#` désigne une section de la page.
    ("cout/", "cout-depenses", "/cout", {}, "cout-depenses"),
    ("simuler/", f"cumul&{CARRIERE}", "/simuler", LUE, "cumul"),
    ("", "contenu", "/", {}, "contenu"),
    # L'ancienne forme : tout derrière le `#`, la page en tête.
    ("", "#/cout?indexation=prix", "/cout", {"indexation": "prix"}, ""),
    ("", f"/simuler?{CARRIERE}", "/simuler", LUE, ""),
    ("", "/", "/", {}, ""),
    ("", "/?indexation=prix", "/", {"indexation": "prix"}, ""),
    # Une simulation sur l'accueil, d'avant que l'accueil devienne le programme.
    ("", f"/?{CARRIERE}", "/simuler", LUE, ""),
    # Les deux pages fondues le 23 septembre 2026, et la section qui les tient.
    ("", f"/trajectoire?{CARRIERE}", "/simuler", LUE, "cumul"),
    ("", "/donnees", "/methode", {}, "sources"),
])
def test_une_adresse_dit_sa_page_son_lecteur_et_sa_section(chemin, ancre, page, parametres,
                                                            section):
    adresse = module("adresses").lireAdresse(chemin, ancre)
    assert (adresse["chemin"], adresse["parametres"], adresse["section"]) \
        == (page, parametres, section)
    assert adresse["ancienne"] is ancre.lstrip("#").startswith("/")


def test_la_requete_d_une_adresse_se_garde_telle_qu_elle_est_ecrite():
    """La mémoire du simulateur compare la requête au caractère près : elle
    sort de l'adresse telle qu'elle y est écrite, sous les deux formes, sans la
    section."""
    lire = module("adresses").lireAdresse
    assert lire("simuler/", f"cumul&{CARRIERE}")["requete"] == CARRIERE
    assert lire("", f"/simuler?{CARRIERE}")["requete"] == CARRIERE
    assert lire("cout/", "")["requete"] == ""


def test_les_anciennes_routes_vivent_avec_les_adresses():
    """Les deux pages fondues sont des adresses : elles vivent dans le module des
    adresses, que les pages relisent, et que le moteur peut lire sans charger
    le texte des pages."""
    adresses, pages = module("adresses"), module("pages")
    assert adresses.ANCIENNES_ROUTES == pages.ANCIENNES_ROUTES == {
        "/trajectoire": ["/simuler", "cumul"], "/donnees": ["/methode", "sources"]}


def test_le_routeur_ne_lit_les_adresses_que_par_leur_module():
    """Une seule lecture des adresses : celle du module, que le routeur importe."""
    routeur = (RACINE / "moteur" / "js" / "routeur.js").read_text(encoding="utf-8")
    assert "function lireAdresse" not in routeur
    assert 'from "./adresses.js"' in routeur
