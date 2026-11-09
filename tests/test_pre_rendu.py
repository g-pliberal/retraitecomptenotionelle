"""Le pré-rendu des pages (action 174, étape 4 (c)) : chaque page du site est
écrite toute faite, pour ses réglages par défaut, par ``scripts/construire_pages.py``.

Le serveur ne lui sert que ce HTML : il se lit et s'affiche sans attendre le
moteur. Deux choses y dépendent de l'écran — les graphiques de Coût et de
Droits non cotisés, que le gabarit dessine à la largeur de la colonne, et les
deux schémas de Sankey que le large pose de front. La page toute faite porte
donc chaque tracé deux fois, dessiné pour un téléphone et pour le large, et la
feuille de style montre l'un ou l'autre.

Ces tests tiennent les pièces : ce que le gabarit marque pour que le générateur
retrouve les tracés, la tolérance qui dit si un dessin convient à une colonne,
et la fusion des deux rendus.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.web.site import disponible, module, rendre

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

pytestmark = pytest.mark.skipif(not disponible(),
                                reason="node absent : les pages du site ne se lisent pas sans lui")

g = module("gabarit")

#: Les deux pages qui dessinent des tracés, et combien de tracés au niveau de la
#: page : les autres n'en ont aucun, et leur rendu ne dépend pas de la largeur.
#: La page Coût compte dix figures, dont les deux schémas de Sankey d'une même
#: carte, que le large pose de front : neuf tracés, le couple pour un.
TRACES = {"/cout": 9, "/avantages": 5}


def test_les_constantes_du_pre_rendu_sont_celles_du_gabarit():
    """Le dessin étroit est celui d'une colonne de téléphone (un écran de 390
    points moins ses deux marges de 19) ; le dessin large, celui d'une colonne de
    portable, où les schémas de front prennent chacun 480 points : entre les
    432 d'une colonne de 944 points, un écran de 1 024, et les 532 d'une colonne
    de 1 200, un écran de 1 440, que le gabarit ne dépasse pas. Un graphique
    y prend la largeur de sa carte, la colonne moins deux retraits de 28 points
    (action 189, étape 6) : 984 unités, entre les 888 d'un écran de 1 024 et
    les 1 100 que le gabarit ne dépasse pas."""
    assert g.ECRAN_ETROIT_PRERENDU == 360
    assert g.COLONNE_LARGE_PRERENDUE == 1040
    assert g.ecransDe(g.COLONNE_LARGE_PRERENDUE) == [None, 480, 984]
    assert g.ecransDe(944) == [None, 432, 888] and g.ecransDe(1200) == [None, 532, 1100]
    assert g.ecransDe(720) == [None, 320, 664]
    assert g.ecransDe(g.ECRAN_ETROIT_PRERENDU) == [360, None, None]
    assert g.ecransDe(None) == [None, None, None]
    assert g.ADRESSE_CANONIQUE == "https://partiliberalfrancais.fr/retraite/"


@pytest.mark.parametrize("attendue, demi, convient", [
    # Les téléphones courants : colonne de 320 à 400 points, le dessin de 360.
    (360, None, True), (372, None, True), (350, None, True), (332, None, True),
    (401, None, True), (409, None, True),
    # Plus étroit ou plus large que 12 % : le tracé serait lu à une autre taille.
    (320, None, False), (280, None, False), (420, None, False), (600, None, False),
    # Le large : le dessin fixe, sauf pour les schémas de front, dont la moitié de
    # carte dépend de la colonne.
    (None, 480, True), (None, 532, True), (None, 432, True), (None, 440, True),
    (None, 420, False), (None, 324, False), (None, 250, False),
])
def test_un_dessin_convient_a_la_colonne_dans_la_tolerance(attendue, demi, convient):
    assert g.tracesConviennent(attendue, demi) is convient


@pytest.mark.parametrize("large, convient", [
    # Le graphique tout fait, dessiné à 984 unités, convient à la carte d'un
    # écran de 1 024 points (888) comme à celle d'un bureau (1 100, la borne).
    (984, True), (888, True), (1100, True), (880, True),
    # Une tablette en hauteur, une fenêtre étroite : ses textes y feraient
    # moins de onze pixels, la fenêtre le redessine.
    (870, False), (744, False), (664, False),
])
def test_un_graphique_convient_a_sa_carte_dans_la_tolerance(large, convient):
    """Au large, un graphique se dessine à la largeur de sa carte (action 189,
    étape 6) : le dessin tout fait convient à 12 % près, comme les autres."""
    assert g.tracesConviennent(None, None, large) is convient


def test_au_large_un_graphique_se_dessine_a_la_largeur_de_sa_carte():
    """Chez le parti, le graphique prend toute la largeur de sa carte. Tenu à
    720 unités et étiré, ses textes de treize unités en feraient vingt à
    l'écran : il se dessine donc à la largeur de la carte, un peu plus haut.
    Sans écran — un témoin, le Python qui lit la page —, il garde son cadre de
    toujours, 720 sur 300."""
    cadres = lambda html: set(re.findall(  # noqa: E731
        r'<figure class="graphique"[^>]*><svg viewBox="0 0 (\d+) (\d+)"', html))
    assert cadres(rendre("/avantages", {}, g.COLONNE_LARGE_PRERENDUE)[1]) == {("984", "335")}
    assert cadres(rendre("/avantages", {}, 1200)[1]) == {("1100", "374")}
    assert cadres(rendre("/avantages", {})[1]) == {("720", "300")}
    cascades = lambda html: set(re.findall(  # noqa: E731
        r'<figure class="cascade"[^>]*><svg viewBox="0 0 (\d+) ', html))
    assert cascades(rendre("/cout", {}, g.COLONNE_LARGE_PRERENDUE)[1]) == {"984"}
    assert cascades(rendre("/cout", {})[1]) == {"720"}


def test_une_page_rendue_pour_un_ecran_ne_le_laisse_pas_au_gabarit():
    """Le Python qui appelle le gabarit sans passer par une page — un
    graphique d'essai, dont il lit le cadre de toujours — le trouve sans écran,
    quelle que soit la page rendue avant lui : l'écran est un état du module,
    et un graphique d'essai se dessinait à 984 unités quand un autre test
    venait de rendre une page au large."""
    for largeur in (g.COLONNE_LARGE_PRERENDUE, g.ECRAN_ETROIT_PRERENDU):
        rendre("/avantages", {}, largeur)
        assert (g.ecran(), g.demiColonne(), g.large()) == (None, None, None)


@pytest.mark.parametrize("colonne, traces, de_front, convient", [
    # Une page sans tracé convient à toute colonne : rien n'y dépend de l'écran,
    # pas même sur une tablette en hauteur, dont la colonne tombe entre deux.
    (300, False, False, True), (688, False, False, True), (720, False, False, True),
    (780, False, False, True), (1200, False, False, True),
    # Des graphiques sans schémas de front : le dessin large, fait pour une
    # carte de 984 points, sert dès un écran de 1 024 points ; en deçà, la
    # carte est trop étroite pour lui (action 189, étape 6).
    (720, True, False, False), (780, True, False, False), (944, True, False, True),
    (1200, True, False, True),
    # Des schémas de front : leur demi-colonne compte.
    (720, True, True, False), (780, True, True, False), (944, True, True, True),
    (1200, True, True, True),
    # Le téléphone : sa colonne compte, de front ou non.
    (360, True, False, True), (372, True, True, True), (600, True, False, False),
])
def test_une_page_toute_faite_convient_a_la_colonne_selon_ses_traces(colonne, traces, de_front,
                                                                       convient):
    """La page toute faite se garde quand rien de ce qu'elle dessine ne dépend de
    la colonne qu'on mesure : le routeur ne la recalculait pas seulement pour un
    tracé trop loin de sa colonne, mais pour toute page, tracés ou non, dès que la
    demi-colonne du large s'écartait de 480 — sur une tablette en hauteur, chaque
    page chargeait le moteur."""
    assert g.dessinConvient(colonne, traces, de_front) is convient


def test_une_colonne_inconnue_convient_a_tout_dessin():
    """Sans mesure — le Python qui lit la page, un témoin — rien ne s'oppose au
    dessin tout fait."""
    assert g.tracesConviennent(None, None) is True


def test_les_traces_ne_sont_marques_que_quand_le_generateur_les_demande():
    """Un rendu ordinaire n'a aucune marque ; le générateur les demande pour
    retrouver chaque tracé, et les ôte du HTML qu'il écrit."""
    g.marquerLesTraces(False)
    assert "<!--trace-->" not in rendre("/cout", {}, 360)[1]
    g.marquerLesTraces(True)
    try:
        corps = rendre("/cout", {}, 360)[1]
        assert corps.count("<!--trace-->") == corps.count("<!--/trace-->") > 0
    finally:
        g.marquerLesTraces(False)


@pytest.mark.parametrize("chemin, attendus", TRACES.items())
def test_chaque_tracé_est_marque_une_fois_au_niveau_de_la_page(chemin, attendus):
    """Les marques de premier niveau sont les tracés de la page, un schéma de
    front et ses deux tracés comptant pour un."""
    g.marquerLesTraces(True)
    try:
        for largeur in (360, 1040):
            corps = rendre(chemin, {}, largeur)[1]
            niveau, regions = 0, 0
            for marque in re.finditer(r"<!--(/?)trace-->", corps):
                if marque.group(1) == "":
                    regions += niveau == 0
                    niveau += 1
                else:
                    niveau -= 1
                assert niveau >= 0
            assert niveau == 0
            assert regions == attendus, (chemin, largeur, regions)
    finally:
        g.marquerLesTraces(False)


@pytest.mark.parametrize("chemin", ["/", "/simuler", "/risque", "/partager", "/saviez-vous",
                                    "/cas-types", "/methode"])
def test_une_page_sans_trace_se_rend_de_la_meme_facon_a_toute_largeur(chemin):
    """Les pages sans graphique ne dépendent pas de l'écran : le pré-rendu les
    écrit une fois."""
    assert rendre(chemin, {}, 360)[1] == rendre(chemin, {}, 1040)[1] == rendre(chemin, {})[1]


def test_la_feuille_de_style_montre_un_seul_dessin_a_la_fois():
    """Le dessin étroit se cache au large, le large sous 800 points d'écran : le
    seuil du gabarit, une colonne de 720 points et ses deux marges de 40, que la
    marge atteint dès 800 points (``clamp(1.125rem, 5vw, 2.5rem)``)."""
    feuille = (RACINE / "moteur" / "style.css").read_text(encoding="utf-8")
    assert ".variante-etroite { display: none; }" in feuille
    assert re.search(r"@media \(max-width: 799\.98px\) \{\s*"
                     r"\.variante-etroite \{ display: block; \}\s*"
                     r"\.variante-large \{ display: none; \}", feuille)
    assert g.LARGEUR_TRACE + 2 * 40 == 800
