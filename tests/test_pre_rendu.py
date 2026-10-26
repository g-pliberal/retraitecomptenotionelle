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
    de 1 200, un écran de 1 440, que le gabarit ne dépasse pas."""
    assert g.ECRAN_ETROIT_PRERENDU == 360
    assert g.COLONNE_LARGE_PRERENDUE == 1040
    assert g.ecransDe(g.COLONNE_LARGE_PRERENDUE) == [None, 480]
    assert g.ecransDe(944) == [None, 432] and g.ecransDe(1200) == [None, 532]
    assert g.ecransDe(g.ECRAN_ETROIT_PRERENDU) == [360, None]
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
