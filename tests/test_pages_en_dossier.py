"""Chaque page du site est un fichier tout fait, à son adresse (action 174).

L'accueil est ``index.html``, à la racine ; les huit autres pages ont chacune un
dossier — ``cout/``, ``simuler/``… — qui porte son ``index.html``. Un serveur
envoie à ``…/cout/`` le fichier de ce dossier : c'est ce qui donne à chaque page
son adresse, son titre, sa description, et son contenu avant qu'aucun script
ne tourne. Ces fichiers sont fabriqués par ``scripts/construire_pages.py``,
depuis le gabarit de page ``moteur/page.html`` et le rendu de chaque page pour
ses réglages par défaut ; ils ne se retouchent pas et ne se fusionnent pas.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import pytest

from retraite_notionnelle.web.site import disponible, module, rendre

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import construire_pages  # noqa: E402
import regenerer  # noqa: E402

pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : les pages du site ne se lisent pas sans lui")

#: Les huit pages en dossier, avec leur titre — l'accueil est la racine.
DOSSIERS = {
    "simuler": "Simuler", "cout": "Coût", "risque": "Pourquoi changer",
    "partager": "Partager", "saviez-vous": "Le saviez-vous ?",
    "cas-types": "Carrières types", "avantages": "Droits non cotisés",
    "methode": "Méthode et sources",
}

#: Le titre de l'onglet de l'accueil : celui qu'un moteur de recherche affiche.
TITRE_DE_L_ACCUEIL = "Retraite à comptes notionnels — programme et simulateur"

#: Les pages qui dessinent des tracés, donc deux dessins.
AVEC_TRACES = ("cout", "avantages")

g = module("gabarit")


@pytest.fixture(scope="module")
def attendues() -> dict[str, str]:
    """Les pages telles que le générateur les écrirait : rendues une fois."""
    return construire_pages.attendues()


def _route(chemin: str) -> str:
    return "/" if chemin == "index.html" else "/" + chemin.split("/")[0]


def _page(chemin: str) -> str:
    return (RACINE / chemin).read_text(encoding="utf-8")


def _chemins() -> list[str]:
    return ["index.html"] + [f"{dossier}/index.html" for dossier in DOSSIERS]


def test_les_pages_toutes_faites_sont_celles_du_site(attendues):
    """Une page par route du site, l'accueil à la racine, chacune à son dossier,
    et le plan du site qui les liste."""
    titres = module("pages").TITRES
    assert {route.lstrip("/"): titre for route, titre in titres.items() if route != "/"} \
        == DOSSIERS
    assert sorted(attendues) == sorted([*_chemins(), "sitemap.xml"])


@pytest.mark.parametrize("chemin", [*_chemins(), "sitemap.xml"])
def test_une_page_toute_faite_est_a_jour(attendues, chemin):
    """Le fichier du dépôt est celui que le script fabriquerait : une retouche du
    gabarit, d'un titre, d'une description, d'une page ou du modèle doit le
    refaire."""
    assert _page(chemin) == attendues[chemin]
    assert construire_pages.perimees(attendues) == []


@pytest.mark.parametrize("chemin", _chemins())
def test_une_page_porte_son_titre_sa_description_et_son_adresse_canonique(chemin):
    """Le titre de l'onglet, la description et l'adresse qui fait foi sont dans le
    HTML : un moteur de recherche qui ne lit pas les scripts sait déjà de quelle
    page il s'agit, et quelle adresse retenir — celle de la copie du parti."""
    route, texte = _route(chemin), _page(chemin)
    titre = TITRE_DE_L_ACCUEIL if route == "/" else \
        f"{DOSSIERS[route.lstrip('/')]} — Retraite en comptes notionnels"
    assert f"<title>{titre}</title>" in texte
    description = module("pages").DESCRIPTIONS[route]
    assert f'<meta name="description" content="{description}">' in texte
    dossier = "" if route == "/" else route.lstrip("/") + "/"
    assert f'<link rel="canonical" href="https://partiliberalfrancais.fr/retraite/{dossier}">' \
        in texte
    assert texte.count("<title>") == 1 and texte.count('name="description"') == 1
    assert texte.count('rel="canonical"') == 1 and '<html lang="fr">' in texte


#: L'image d'aperçu, la même pour les neuf pages, et l'adresse d'où les réseaux
#: la prennent : la copie du parti, comme l'adresse canonique. Le partage renvoie
#: au site du parti, jamais à GitHub Pages (décision du propriétaire,
#: 28 octobre 2026).
APERCU = RACINE / "moteur" / "apercu.png"
IMAGE_APERCU = "https://partiliberalfrancais.fr/retraite/moteur/apercu.png"


def _slogan() -> str:
    """Le titre de l'affiche de l'accueil, sans ses balises : ce que l'image dit."""
    titre = re.search(r'<div class="affiche">.*?<h1>(.*?)</h1>', _page("index.html"), re.S)
    return re.sub(r"<[^>]+>", "", titre.group(1))


@pytest.mark.parametrize("chemin", _chemins())
def test_une_page_porte_son_apercu_de_partage(chemin):
    """Collée dans WhatsApp, X, LinkedIn ou Facebook, l'adresse d'une page
    s'affiche avec son titre, sa description et une image, et non comme un lien
    nu : sans ces balises, la rubrique « Faire connaître » partage des adresses
    que personne ne voit. Le titre et la description sont ceux de l'onglet ;
    l'adresse (``og:url``) et l'image sont celles de la copie du parti : le
    partage renvoie au site du parti, jamais à GitHub Pages, qu'aucune page ne
    nomme. L'aperçu ne s'affiche donc qu'une fois la copie refaite."""
    route, texte = _route(chemin), _page(chemin)
    titre = TITRE_DE_L_ACCUEIL if route == "/" else \
        f"{DOSSIERS[route.lstrip('/')]} — Retraite en comptes notionnels"
    dossier = "" if route == "/" else route.lstrip("/") + "/"
    attendues = {
        "og:type": "website",
        "og:locale": "fr_FR",
        "og:site_name": "Retraite à comptes notionnels",
        "og:url": f"https://partiliberalfrancais.fr/retraite/{dossier}",
        "og:title": titre,
        "og:description": module("pages").DESCRIPTIONS[route],
        "og:image": IMAGE_APERCU,
        "og:image:width": "1200",
        "og:image:height": "630",
    }
    for propriete, valeur in attendues.items():
        assert f'<meta property="{propriete}" content="{valeur}">' in texte, (chemin, propriete)
        assert texte.count(f'property="{propriete}"') == 1, (chemin, propriete)
    # Le texte de remplacement dit ce que l'image montre : le titre de l'affiche.
    alternatif = re.search(r'<meta property="og:image:alt" content="([^"]+)">', texte)
    assert alternatif and _slogan() in alternatif.group(1), chemin
    assert '<meta name="twitter:card" content="summary_large_image">' in texte
    assert "github.io" not in texte, chemin


def test_l_image_d_apercu_est_au_format_des_reseaux():
    """Un PNG de 1 200 × 630 points, le format d'une grande image d'aperçu chez
    Facebook, LinkedIn et X, et léger : WhatsApp ne montre pas une image d'aperçu
    trop lourde, et 300 Ko est le seuil sûr."""
    octets = APERCU.read_bytes()
    assert octets[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", octets[16:24]) == (1200, 630)
    assert len(octets) < 300_000


@pytest.mark.parametrize("chemin", _chemins())
def test_une_page_toute_faite_est_la_page_entiere(chemin):
    """Le bandeau, la page et le pied sont dans le HTML servi : rien ne les
    attend. Pas d'écran d'attente, pas de précharge du moteur : la page s'affiche
    avec son propre style et les deux polices, et le routeur ne charge le
    moteur que s'il en a besoin."""
    route, texte = _route(chemin), _page(chemin)
    assert '<div id="entete"><a class="evitement"' in texte
    assert f'<main id="contenu" tabindex="-1" data-prerendu="{route}">' in texte
    assert "<footer>" in texte and texte.count("<footer>") == 1
    assert "amorce" not in texte and 'rel="modulepreload"' not in texte
    assert 'rel="preload" href="' in texte and texte.count('rel="preload"') == 2
    assert 'as="font"' in texte and "donnees.json" not in texte
    racine = "" if route == "/" else "../"
    assert f'<script type="module" src="{racine}moteur/js/routeur.js"></script>' in texte


@pytest.mark.parametrize("chemin", _chemins())
def test_une_page_porte_son_style_et_charge_la_feuille_entiere_sans_bloquer(chemin):
    """La page se peint avec les règles qui la touchent, écrites dans son en-tête
    (``scripts/feuille_de_page.py``) : la feuille entière, qui bloquait
    l'affichage, suit sans le retenir. Déclarée pour l'impression, elle ne bloque
    rien ; son chargement la rend effective, par son ``onload`` ou par le
    routeur ; sans script, le lien ordinaire du ``<noscript>`` la charge."""
    route, texte = _route(chemin), _page(chemin)
    racine = "" if route == "/" else "../"
    tete = texte[:texte.index("</head>")]
    assert tete.count("<style>") == 1 and texte.count("<style") == 1
    style = tete[tete.index("<style>") + len("<style>"):tete.index("</style>")]
    feuille = (RACINE / "moteur" / "style.css").read_text(encoding="utf-8")
    assert 0 < len(style) < len(feuille) / 2, len(style)
    assert "@media print" not in style and f"url({racine}moteur/polices/" in style
    assert (f'<link rel="stylesheet" href="{racine}moteur/style.css" media="print" '
            f'onload="this.media=\'all\'" data-feuille>') in tete
    assert f'<noscript><link rel="stylesheet" href="{racine}moteur/style.css"></noscript>' in tete
    assert tete.count('rel="stylesheet"') == 2
    # Les chemins sont ceux de la page : un niveau plus haut dans un dossier.
    mal_remontes = re.findall(r'(?:href|src)="(?:\.\./)?moteur/', texte)
    assert all(chemin.endswith(f'="{racine}moteur/') for chemin in mal_remontes), mal_remontes


@pytest.mark.parametrize("chemin", _chemins())
def test_le_corps_d_une_page_toute_faite_est_son_rendu(chemin):
    """Ce que la page contient est ce que le routeur écrirait pour ses réglages
    par défaut : mot pour mot, tracés compris. Les deux pages qui dessinent des
    tracés les portent deux fois, pour un téléphone et pour le large, et un seul
    se voit (``moteur/style.css``)."""
    route, texte = _route(chemin), _page(chemin)
    corps = texte[texte.index('data-prerendu="'):]
    corps = corps[corps.index(">") + 1:corps.index("</main>")]
    if route.lstrip("/") not in AVEC_TRACES:
        assert corps == rendre(route, {})[1]
        return
    assert "variante-etroite" in corps and "variante-large" in corps
    # Dépouillé de l'un ou de l'autre, le corps retrouve le rendu de son écran.
    for variante, largeur in (("etroite", g.ECRAN_ETROIT_PRERENDU),
                              ("large", g.COLONNE_LARGE_PRERENDUE)):
        assert construire_pages.sans_variantes(corps, variante) == rendre(route, {}, largeur)[1], \
            (route, variante)


@pytest.mark.parametrize("chemin", _chemins())
def test_les_liens_d_une_page_toute_faite_vont_aux_pages_du_site(chemin):
    """Résolu depuis le dossier de la page, tout lien interne mène à l'une des
    neuf pages ; le bandeau et la signature n'y renvoient pas par une adresse
    absolue, que la copie du parti ne servirait pas."""
    route, texte = _route(chemin), _page(chemin)
    dossier = "" if route == "/" else route.lstrip("/") + "/"
    hote = "https://exemple.org/retraite/"
    pages = {"" if r == "/" else r.lstrip("/") + "/" for r in module("pages").TITRES}
    for adresse in re.findall(r'<a\b[^>]*\bhref="([^"]*)"', texte):
        cible = urlsplit(urljoin(hote + dossier, adresse))
        if cible.scheme != "https" or cible.netloc != "exemple.org":
            continue
        assert cible.path[len("/retraite/"):] in pages, f"{chemin} : {adresse!r}"


@pytest.mark.parametrize("chemin", _chemins())
def test_tout_ce_que_une_page_toute_faite_charge_existe(chemin):
    """Un chemin relatif mal remonté ne charge rien : chaque ressource que la
    page nomme, résolue depuis son dossier, est un fichier du dépôt."""
    texte = _page(chemin)
    dossier = "" if chemin == "index.html" else chemin.split("/")[0] + "/"
    chargees = re.findall(r'<(?:link|script)\b[^>]*\b(?:href|src)="([^"]+)"', texte)
    assert len(chargees) >= 5
    for adresse in chargees:
        cible = urlsplit(urljoin(f"https://exemple.org/{dossier}", adresse))
        if cible.netloc != "exemple.org":
            continue          # l'adresse canonique est celle du parti
        assert (RACINE / cible.path.lstrip("/")).is_file(), f"{chemin} : {adresse} n'existe pas"


def test_le_plan_du_site_liste_les_neuf_pages_a_l_adresse_canonique():
    """Une adresse par page, celle de la copie du parti, et rien d'autre."""
    plan = _page("sitemap.xml")
    adresses = re.findall(r"<loc>([^<]+)</loc>", plan)
    attendues = ["https://partiliberalfrancais.fr/retraite/"] + [
        f"https://partiliberalfrancais.fr/retraite/{d}/" for d in DOSSIERS]
    assert adresses == attendues
    assert plan.startswith('<?xml version="1.0" encoding="UTF-8"?>')


def test_les_pages_toutes_faites_se_fabriquent_et_ne_se_fusionnent_pas():
    """Un fichier fabriqué ne se fusionne pas ligne à ligne (``.gitattributes``)
    et a son étape dans ``regenerer.py`` : deux sessions qui les refont
    chacune de leur côté ne doivent pas en faire un fichier que personne n'a
    produit. L'étape les écrit après le paquet, dont elles lisent les chiffres."""
    fabriques = {ligne.split()[0] for ligne in
                 (RACINE / ".gitattributes").read_text(encoding="utf-8").splitlines()
                 if ligne.strip() and not ligne.startswith("#") and ligne.split()[-1] == "-merge"}
    for chemin in [*_chemins(), "sitemap.xml"]:
        assert chemin in fabriques
        assert chemin in regenerer.PAGES.ecrit
    ordre = [etape for branches in regenerer.TEMPS for branche in branches for etape in branche]
    assert ordre.index(regenerer.PAGES) > ordre.index(regenerer.PAQUET)
    assert ordre.index(regenerer.PAGES) > ordre.index(regenerer.ACCUEIL)
    assert ordre.index(regenerer.PAGES) < ordre.index(regenerer.PROSE)


# -- la fusion des deux rendus ---------------------------------------------------

DEBUT, FIN = "<!--trace-->", "<!--/trace-->"


def test_deux_rendus_se_fusionnent_en_deux_variantes_par_trace():
    etroit = f"<p>avant</p>{DEBUT}<svg>E</svg>{FIN}<p>entre</p>{DEBUT}<svg>F</svg>{FIN}<p>après</p>"
    large = f"<p>avant</p>{DEBUT}<svg>EE</svg>{FIN}<p>entre</p>{DEBUT}<svg>FF</svg>{FIN}<p>après</p>"
    assert construire_pages.fusionner(etroit, large) == (
        '<p>avant</p><div class="variante-etroite"><svg>E</svg></div>'
        '<div class="variante-large"><svg>EE</svg></div><p>entre</p>'
        '<div class="variante-etroite"><svg>F</svg></div>'
        '<div class="variante-large"><svg>FF</svg></div><p>après</p>')


def test_les_marques_imbriquees_sont_ôtées_et_le_groupe_reste_un_seul_tracé():
    """Un schéma de front et ses deux tracés : une région au niveau de la page,
    les marques du dedans retirées."""
    etroit = f"{DEBUT}{DEBUT}<svg>A</svg>{FIN}{DEBUT}<svg>B</svg>{FIN}{FIN}"
    large = (f'{DEBUT}<div class="de-front"><div>{DEBUT}<svg>A</svg>{FIN}</div>'
             f"<div>{DEBUT}<svg>B</svg>{FIN}</div></div>{FIN}")
    fusion = construire_pages.fusionner(etroit, large)
    assert "<!--" not in fusion
    assert fusion.count('class="variante-etroite"') == fusion.count('class="variante-large"') == 1
    assert '<div class="variante-etroite"><svg>A</svg><svg>B</svg></div>' in fusion


def test_une_page_sans_trace_est_gardee_telle_qu_elle_est():
    assert construire_pages.fusionner("<p>a</p>", "<p>a</p>") == "<p>a</p>"


@pytest.mark.parametrize("etroit, large", [
    ("<p>a</p>", "<p>b</p>"),                                    # du texte qui dépend de l'écran
    (f"<p>a</p>{DEBUT}x{FIN}", "<p>a</p>"),                      # un tracé de moins
    (f"<p>a</p>{DEBUT}x{FIN}<p>b</p>", f"<p>a</p>{DEBUT}x{FIN}<p>c</p>"),
    (f"<p>a</p>{DEBUT}x", f"<p>a</p>{DEBUT}x{FIN}"),             # une marque jamais fermée
])
def test_deux_rendus_qui_ne_s_accordent_pas_ne_se_fusionnent_pas(etroit, large):
    """Tout ce qui n'est pas un tracé doit être le même aux deux écrans ; sinon
    la page toute faite mentirait à l'un d'eux, et le générateur le dit."""
    with pytest.raises(ValueError):
        construire_pages.fusionner(etroit, large)


def test_sans_variantes_retrouve_le_rendu_d_un_ecran():
    fusion = ('<p>a</p><div class="variante-etroite"><svg>E</svg></div>'
              '<div class="variante-large"><svg>L</svg></div><p>b</p>')
    assert construire_pages.sans_variantes(fusion, "etroite") == "<p>a</p><svg>E</svg><p>b</p>"
    assert construire_pages.sans_variantes(fusion, "large") == "<p>a</p><svg>L</svg><p>b</p>"
