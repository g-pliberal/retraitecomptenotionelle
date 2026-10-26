"""Chaque page du site a son dossier (action 174, étape 4) : ``cout/index.html``,
``simuler/index.html``… L'accueil reste ``index.html``, à la racine.

Un serveur envoie à ``…/cout/`` le fichier de ce dossier : c'est ce qui donne à
chaque page sa propre adresse, et ce qui permettra de lui servir son contenu
tout fait. Ces fichiers sont fabriqués par ``scripts/construire_pages.py``, depuis
``index.html`` : la même coquille, ses chemins un niveau plus bas, le titre et
la description de la page. Ils ne se retouchent pas, et ne se fusionnent pas.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import pytest

from retraite_notionnelle.web.site import disponible, module

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import construire_pages  # noqa: E402
import regenerer  # noqa: E402

pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : les pages du site ne se lisent pas sans lui")

#: Les huit pages qui ont un dossier, avec leur titre — l'accueil est la racine.
DOSSIERS = {
    "simuler": "Simuler", "cout": "Coût", "risque": "Pourquoi changer",
    "partager": "Partager", "saviez-vous": "Le saviez-vous ?",
    "cas-types": "Carrières types", "avantages": "Droits non cotisés",
    "methode": "Méthode et sources",
}


def _page(dossier: str) -> str:
    return (RACINE / dossier / "index.html").read_text(encoding="utf-8")


def test_les_pages_en_dossier_sont_celles_du_site():
    """Une page par route du site, l'accueil excepté, chacune à son dossier."""
    titres = module("pages").TITRES
    assert {route.lstrip("/"): titre for route, titre in titres.items() if route != "/"} \
        == DOSSIERS
    assert sorted(construire_pages.attendues()) == sorted(f"{d}/index.html" for d in DOSSIERS)


@pytest.mark.parametrize("dossier", DOSSIERS)
def test_une_page_en_dossier_est_a_jour(dossier):
    """Le fichier du dépôt est celui que le script fabriquerait : une retouche de
    la coquille, d'un titre ou d'une description, doit les refaire."""
    assert _page(dossier) == construire_pages.attendues()[f"{dossier}/index.html"]
    assert construire_pages.perimees() == []


@pytest.mark.parametrize("dossier, titre", DOSSIERS.items())
def test_une_page_porte_son_titre_et_sa_description(dossier, titre):
    """Le titre de l'onglet est celui que le routeur y posera, la description
    celle de la page : un moteur de recherche qui ne lit pas les scripts voit
    déjà de quelle page il s'agit."""
    texte = _page(dossier)
    assert f"<title>{titre} — Retraite en comptes notionnels</title>" in texte
    description = module("pages").DESCRIPTIONS[f"/{dossier}"]
    assert f'<meta name="description" content="{description}">' in texte
    assert texte.count("<title>") == 1 and texte.count('name="description"') == 1


@pytest.mark.parametrize("dossier", DOSSIERS)
def test_une_page_en_dossier_charge_le_site_un_niveau_plus_haut(dossier):
    """La coquille est celle de l'accueil, ses chemins remontés d'un cran : le
    même routeur, la même feuille de style, les mêmes préchargements. Le corps
    n'a pas changé."""
    accueil = (RACINE / "index.html").read_text(encoding="utf-8")
    texte = _page(dossier)
    assert re.findall(r'(?:href|src)="(?!\.\./)moteur/', texte) == []
    assert '<script type="module" src="../moteur/js/routeur.js"></script>' in texte
    assert '<link rel="stylesheet" href="../moteur/style.css">' in texte
    assert '<link rel="preload" href="../moteur/donnees.json" as="fetch" crossorigin>' in texte

    def precharges(page: str) -> list[str]:
        return re.findall(r'<link rel="modulepreload" href="(?:\.\./)?(moteur/[^"]+)">', page)

    assert precharges(texte) == precharges(accueil) and precharges(texte)
    # Le corps est le même, au chemin du routeur près.
    assert texte[texte.index("<body>"):].replace('src="../moteur/', 'src="moteur/') \
        == accueil[accueil.index("<body>"):]


@pytest.mark.parametrize("dossier", DOSSIERS)
def test_tout_ce_que_une_page_en_dossier_charge_existe(dossier):
    """Un chemin relatif mal remonté ne charge rien, et la page reste sur son
    écran d'attente : chaque ressource que la coquille nomme, résolue depuis le
    dossier de la page, est un fichier du dépôt."""
    texte = _page(dossier)
    chargees = re.findall(r'<(?:link|script)\b[^>]*\b(?:href|src)="([^"]+)"', texte)
    assert len(chargees) > 60, "la coquille ne précharge plus le portage"
    for adresse in chargees:
        cible = urlsplit(urljoin(f"https://exemple.org/{dossier}/", adresse))
        assert cible.netloc == "exemple.org", f"{dossier} charge {adresse}, hors du site"
        assert (RACINE / cible.path.lstrip("/")).is_file(), f"{dossier} : {adresse} n'existe pas"


def test_les_pages_en_dossier_se_fabriquent_et_ne_se_fusionnent_pas():
    """Un fichier fabriqué ne se fusionne pas ligne à ligne (``.gitattributes``)
    et a son étape dans ``regenerer.py`` : deux sessions qui les refont
    chacune de leur côté ne doivent pas en faire un fichier que personne n'a
    produit."""
    fabriques = {ligne.split()[0] for ligne in
                 (RACINE / ".gitattributes").read_text(encoding="utf-8").splitlines()
                 if ligne.strip() and not ligne.startswith("#") and ligne.split()[-1] == "-merge"}
    for dossier in DOSSIERS:
        assert f"{dossier}/index.html" in fabriques
        assert f"{dossier}/index.html" in regenerer.PAGES.ecrit
    assert any(regenerer.PAGES in branche for branches in regenerer.TEMPS for branche in branches)
