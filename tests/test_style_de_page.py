"""Le style de chaque page, dans son HTML (action 174, proposition du 27 octobre
2026, que le propriétaire a retenue).

La feuille de style bloquait l'affichage : 37 Ko compressés, dont chaque page
n'utilise que le cinquième à l'ouverture. Chaque page porte désormais en tête
les règles de ``moteur/style.css`` qui peuvent la toucher, et la feuille entière
se charge sans retenir l'affichage. ``scripts/feuille_de_page.py`` choisit ces
règles, sans navigateur et sans dépendance : une règle est gardée quand chaque
classe, chaque identifiant, chaque balise et chaque attribut de l'un de ses
sélecteurs paraît dans la page, ou dans les chaînes du routeur, qui en ajoute à
l'ouverture. C'est un sur-ensemble de ce qui touche la page ; les tests des
écrans vérifient qu'il n'y manque rien.
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

from feuille_de_page import feuille_de_la_page, jetons  # noqa: E402


def _garde(css: str, page: str, routeur: str = "", racine: str = "") -> str:
    return feuille_de_la_page(css, jetons(page, routeur), racine)


def test_une_regle_est_gardee_quand_tout_son_selecteur_parait_dans_la_page():
    css = (".a .b { color: red; }\n.a .c { color: blue; }\n#d > p { margin: 0; }\n"
           "section.e { padding: 0; }\n")
    garde = _garde(css, '<div class="a"><span class="b x"></span></div><p id="d"></p>')
    assert ".a .b {" in garde and "#d > p {" in garde
    assert ".a .c" not in garde and "section.e" not in garde


def test_une_regle_a_plusieurs_selecteurs_est_gardee_entiere_si_l_un_paraît():
    """La règle reste telle qu'elle est écrite : la cascade est celle de la
    feuille entière."""
    garde = _garde(".z, .a { color: red; }\n", '<p class="a"></p>')
    assert ".z, .a { color: red; }" in garde


def test_les_pseudo_classes_et_les_negations_ne_demandent_rien():
    css = ("a:hover { color: red; }\n.x:not(.y) { color: blue; }\n"
           ":is(.z, .w) p { margin: 0; }\n.x::before { content: \"\"; }\n:root { --c: red; }\n"
           "* { box-sizing: border-box; }\n")
    garde = _garde(css, '<a href="#"></a><p class="x"></p>')
    for selecteur in ("a:hover", ".x:not(.y)", ":is(.z, .w) p", ".x::before", ":root", "* {"):
        assert selecteur in garde, selecteur


def test_un_attribut_est_demande_par_son_nom():
    css = "[hidden] { display: none; }\nbutton[aria-expanded=\"true\"] { color: red; }\n"
    assert "[hidden]" in _garde(css, "<p hidden></p>")
    assert "aria-expanded" not in _garde(css, "<p hidden></p><button></button>")
    assert "aria-expanded" in _garde(css, '<button aria-expanded="false"></button>')


def test_les_requetes_media_gardent_leurs_regles_et_leur_condition():
    css = ("@media (max-width: 600px) {\n  .a { width: 1px; }\n  .z { width: 2px; }\n}\n"
           "@media (min-width: 900px) {\n  .z { height: 1px; }\n}\n"
           "@supports (display: grid) {\n  .a { display: grid; }\n}\n")
    garde = _garde(css, '<p class="a"></p>')
    assert "@media (max-width: 600px)" in garde and ".a { width: 1px; }" in garde
    assert ".z" not in garde and "min-width: 900px" not in garde
    assert "@supports (display: grid)" in garde


def test_l_impression_reste_a_la_feuille_entiere():
    """La feuille entière est déclarée pour l'impression avant d'être chargée :
    ce qui sert au papier n'a rien à faire en tête de page."""
    garde = _garde("@media print {\n  .a { color: black; }\n}\n.a { color: red; }\n",
                   '<p class="a"></p>')
    assert "print" not in garde and ".a { color: red; }" in garde


def test_les_polices_sont_toujours_declarees():
    css = '@font-face {\n  font-family: "X"; src: url(polices/x.woff2) format("woff2");\n}\n'
    assert '@font-face' in _garde(css, "<p></p>")


def test_une_animation_n_est_gardee_que_si_une_regle_gardee_la_nomme():
    css = ("@keyframes glisse {\n  from { left: 0; }\n  to { left: 10px; }\n}\n"
           ".chargement { animation: glisse 1.4s infinite; }\n")
    assert "@keyframes" not in _garde(css, "<p></p>")
    garde = _garde(css, '<div class="chargement"></div>')
    assert "@keyframes glisse" in garde and "from { left: 0; }" in garde


def test_les_adresses_de_la_feuille_se_lisent_depuis_la_page():
    """La feuille vit dans ``moteur/`` : ses adresses relatives y menaient, et la
    page qui la porte en tête est à la racine ou un dossier plus bas."""
    css = '@font-face { src: url(polices/x.woff2) format("woff2"); }\n.a { background: url("data:image/svg+xml;utf8,<svg/>"); }\n'
    assert "url(moteur/polices/x.woff2)" in _garde(css, '<p class="a"></p>')
    dossier = _garde(css, '<p class="a"></p>', racine="../")
    assert "url(../moteur/polices/x.woff2)" in dossier and 'url("data:image/svg+xml' in dossier


def test_le_routeur_compte_parmi_ce_qui_touche_la_page():
    """Le routeur pose des classes à l'ouverture — un tableau replié, un champ
    caché : leurs règles doivent être là avant la feuille entière."""
    css = ".plie { display: block; }\n"
    assert ".plie" not in _garde(css, "<p></p>")
    assert ".plie" in _garde(css, "<p></p>", routeur='tableau.classList.add("plie");')


def test_un_attribut_que_le_routeur_pose_par_dataset_compte_aussi():
    """Le routeur replie un tableau trop large en lui posant ``data-pli`` par
    ``table.dataset.pli`` : le nom de l'attribut n'est écrit nulle part en toutes
    lettres, et ses règles manquaient à la page sur un téléphone."""
    css = 'table[data-pli="cartes"] td { display: block; }\n[data-vue-courante] { color: red; }\n'
    routeur = 'table.dataset.pli = table._pli;\nel.dataset.vueCourante = "1";'
    garde = _garde(css, "<table><td></td></table>", routeur=routeur)
    assert 'table[data-pli="cartes"] td' in garde and "[data-vue-courante]" in garde


def test_les_commentaires_ne_passent_pas():
    garde = _garde("/* une note { } */\n.a { color: red; } /* fin */\n", '<p class="a"></p>')
    assert "note" not in garde and "fin" not in garde and ".a { color: red; }" in garde
