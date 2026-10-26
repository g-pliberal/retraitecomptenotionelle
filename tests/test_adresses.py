"""Les adresses du site (action 174, étape 4) : la page dans le chemin, le
lecteur derrière le ``#`` — sa carrière, ses réglages —, que le navigateur ne
transmet à aucun serveur ; et l'ancienne forme, la page derrière le ``#``
(``#/cout?indexation=prix``), que portent les partages publiés avant le
changement. ``moteur/js/adresses.js`` les lit toutes deux, et le routeur ne
lit plus les adresses qu'à travers lui ; il écrit aussi la nouvelle forme d'une
adresse ancienne, et le gabarit dit où va chaque page (son dossier) et comment
on y va depuis une autre, par un chemin relatif.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

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


#: Les neuf pages du site, dans l'ordre du bandeau.
PAGES = ["/", "/simuler", "/cout", "/risque", "/partager", "/saviez-vous",
         "/cas-types", "/avantages", "/methode"]


def test_les_pages_du_site_sont_celles_du_bandeau():
    """Une seule liste des pages : celle du bandeau, que les titres suivent."""
    g = module("gabarit")
    assert g.PAGES == [chemin for chemin, _ in g.LIENS] == PAGES
    assert list(module("pages").TITRES) == PAGES


@pytest.mark.parametrize("page, dossier", [
    ("/", ""), ("/simuler", "simuler/"), ("/cout", "cout/"), ("/risque", "risque/"),
    ("/partager", "partager/"), ("/saviez-vous", "saviez-vous/"),
    ("/cas-types", "cas-types/"), ("/avantages", "avantages/"), ("/methode", "methode/"),
])
def test_une_page_a_son_dossier(page, dossier):
    """L'accueil est la racine du site ; une page, un dossier de son nom, qui
    porte son ``index.html`` : tout serveur statique le sert sans réglage."""
    assert module("gabarit").dossierDe(page) == dossier


@pytest.mark.parametrize("depuis, vers, attendu", [
    ("/", "/", "./"),
    ("/", "/cout", "cout/"),
    ("/", "/saviez-vous", "saviez-vous/"),
    ("/cout", "/", "../"),
    ("/cout", "/risque", "../risque/"),
    ("/cout", "/cout", "./"),
    ("/simuler", "/simuler", "./"),
])
def test_un_lien_relatif_va_d_une_page_a_l_autre(depuis, vers, attendu):
    assert module("gabarit").versLaPage(depuis, vers) == attendu


@pytest.mark.parametrize("hote", ["https://exemple.org/", "https://exemple.org/retraite/",
                                  "https://g-pliberal.github.io/retraitecomptenotionelle/"])
def test_tout_lien_relatif_se_resout_sur_la_page_visee(hote):
    """L'étalon est la résolution des adresses relatives (RFC 3986), non ce que
    le code écrit : de toute page à toute page, sur la racine d'un hôte comme
    sous le dossier où le site est copié, le lien aboutit au dossier visé. C'est
    ce qui permet à la même page de servir à GitHub Pages et à la copie du
    parti."""
    g = module("gabarit")
    for depuis in PAGES:
        for vers in PAGES:
            assert urljoin(hote + g.dossierDe(depuis), g.versLaPage(depuis, vers)) \
                == hote + g.dossierDe(vers), (depuis, vers)


@pytest.mark.parametrize("chemin, ancre, attendu", [
    # L'ancienne forme prend la nouvelle : la page dans le chemin, le lecteur
    # derrière le `#`.
    ("", "#/cout?indexation=prix", "cout/#indexation=prix"),
    ("", f"/simuler?{CARRIERE}", f"simuler/#{CARRIERE}"),
    ("", "/risque", "risque/"),
    ("", "/", ""),
    ("", "/?indexation=prix", "#indexation=prix"),
    # La simulation de l'accueil d'avant le programme mène au simulateur.
    ("", f"/?{CARRIERE}", f"simuler/#{CARRIERE}"),
    # Les deux pages fondues le 23 septembre 2026 mènent à ce qui les a remplacées.
    ("", f"/trajectoire?{CARRIERE}", f"simuler/#cumul&{CARRIERE}"),
    ("", "/donnees", "methode/#sources"),
    # Une page qui n'existe pas : le routeur rend l'accueil, et l'adresse aussi.
    ("", "/cuot", ""),
    ("", "/cuot?indexation=prix", "#indexation=prix"),
    # La nouvelle forme s'écrit telle qu'elle est lue.
    ("cout/", "#indexation=prix", "cout/#indexation=prix"),
    ("simuler/", f"cumul&{CARRIERE}", f"simuler/#cumul&{CARRIERE}"),
    ("", "", ""),
])
def test_une_adresse_s_ecrit_sous_la_nouvelle_forme(chemin, ancre, attendu):
    adresses = module("adresses")
    assert adresses.ecrireAdresse(adresses.lireAdresse(chemin, ancre)) == attendu


@pytest.mark.parametrize("ancre", ["#/cout?indexation=prix", f"/simuler?{CARRIERE}",
                                   f"/trajectoire?{CARRIERE}", "/donnees", "/?indexation=prix"])
def test_l_adresse_ecrite_se_relit_a_l_identique(ancre):
    """Écrire puis relire ne change ni la page, ni la requête, ni la section :
    la redirection d'une ancienne adresse n'en perd rien."""
    adresses = module("adresses")
    lue = adresses.lireAdresse("", ancre)
    dossier, _, fragment = adresses.ecrireAdresse(lue).partition("#")
    relue = adresses.lireAdresse(dossier, fragment)
    assert (relue["chemin"], relue["requete"], relue["section"], relue["ancienne"]) \
        == (lue["chemin"], lue["requete"], lue["section"], False)
