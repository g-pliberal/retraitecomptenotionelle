"""Les fichiers fabriqués, écrits sans ligne géante
(``src/retraite_notionnelle/lignes.py`` ; feuille de route, action 135, étape 4
du contexte) : le paquet du site, le bilan figé et le témoin des pages."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.lignes import html_en_morceaux, json_en_lignes

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import arbre  # noqa: E402


def _compact(valeur) -> str:
    return json.dumps(valeur, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# -- le JSON -------------------------------------------------------------------


def test_un_json_court_reste_sur_sa_ligne():
    valeur = {"annee": 2026, "taux": [0.1, 0.2], "nom": "été", "vide": None}
    assert json_en_lignes(valeur) == _compact(valeur)


def test_un_json_long_passe_a_la_ligne_et_se_relit_a_l_identique():
    valeur = {
        "series": {str(annee): [annee * 0.5, None, True, "é"] for annee in range(1940, 2071)},
        "regimes": [{"code": f"r{rang}", "taux": rang / 7, "periodes": list(range(rang))}
                    for rang in range(60)],
        "vide": {},
        "court": [1, 2],
    }
    texte = json_en_lignes(valeur, largeur=80)
    assert texte.count("\n") > 100
    # Ôter les retours à la ligne redonne le JSON compact, à l'octet.
    assert texte.replace("\n", "") == _compact(valeur)
    assert json.loads(texte) == valeur
    # Une ligne : une clé, puis ce qui tient en 80 caractères, et sa virgule.
    assert max(len(ligne) for ligne in texte.split("\n")) <= 80 + len('"periodes":,')
    # Ce qui tient reste entier.
    assert '"court":[1,2],' in texte.split("\n")
    assert '"1940":[970.0,null,true,"é"],' in texte.split("\n")


def test_les_cles_se_rangent_comme_json_les_range():
    """Des clés entières se rangent avant d'être écrites en chaînes : 2 avant 10."""
    valeur = {10: "x" * 50, 2: "y" * 50, 33: "z" * 50}
    texte = json_en_lignes(valeur, largeur=40)
    assert texte.replace("\n", "") == _compact(valeur)
    assert [ligne[:4] for ligne in texte.split("\n")] == ["{", '"2":', '"10"', '"33"', "}"]


def test_un_tuple_s_ecrit_comme_une_liste():
    valeur = {"paires": tuple((rang, rang + 1) for rang in range(40))}
    texte = json_en_lignes(valeur, largeur=30)
    assert texte.replace("\n", "") == _compact(valeur)
    assert "[0,1]," in texte.split("\n")


def test_une_chaine_trop_longue_ne_se_coupe_pas():
    texte = json_en_lignes(["a" * 500, "b"], largeur=100)
    assert texte.split("\n") == ["[", '"' + "a" * 500 + '",', '"b"', "]"]


# -- le HTML -------------------------------------------------------------------

#: Une page en miniature : deux lignes courtes, une ligne géante — un tableau
#: d'une ligne par année, un paragraphe —, et la fin.
PAGE = (
    "<main>\n"
    "  <h1>Titre</h1>\n"
    + "<table><caption>Les années</caption><tbody>"
    + "".join(f'<tr><th scope="row">{annee}</th><td class="nombre">{annee % 7},5 %</td></tr>'
              for annee in range(2026, 2071))
    + "</tbody></table>"
    + '<p>Un texte <strong>fort</strong>, <br>et <img src="x.png" alt=""> une image.</p>\n'
    + "</main>\n"
)


def test_une_page_coupee_se_recoud_a_l_octet():
    morceaux = html_en_morceaux(PAGE, largeur=120)
    assert "".join(morceaux) == PAGE
    # Les lignes courtes restent entières, leur fin de ligne comprise.
    assert morceaux[:2] == ["<main>\n", "  <h1>Titre</h1>\n"]
    assert morceaux[-1] == "</main>\n"
    # La ligne géante se coupe entre ses éléments : une ligne de tableau par
    # morceau, le paragraphe entier, qui garde la fin de sa ligne.
    assert morceaux[2:6] == ["<table>", "<caption>Les années</caption>", "<tbody>",
                             '<tr><th scope="row">2026</th><td class="nombre">3,5 %</td></tr>']
    assert morceaux[-4:-1] == [
        "</tbody>", "</table>",
        '<p>Un texte <strong>fort</strong>, <br>et <img src="x.png" alt=""> une image.</p>\n']
    # Un morceau ne passe à la ligne qu'à sa fin, et tient dans la largeur.
    assert all("\n" not in morceau[:-1] for morceau in morceaux)
    assert max(map(len, morceaux)) <= 120


def test_un_element_trop_long_se_coupe_entre_ses_enfants():
    cellule = '<td class="nombre">' + "9" * 30 + "</td>"
    assert html_en_morceaux("<tr>" + cellule * 5 + "</tr>", largeur=100) == [
        "<tr>", *[cellule] * 5, "</tr>"]
    # Un texte ne se coupe pas, si long soit-il.
    texte = "mot " * 100
    assert html_en_morceaux(f"<p>{texte}</p>", largeur=100) == ["<p>", texte, "</p>"]


def test_un_element_sans_fin_ne_cherche_pas_sa_balise_fermante():
    ligne = ('<svg viewBox="0 0 10 10">' + '<rect x="1" y="2"/>' * 10
             + "<!-- note --><br><input type=\"text\"></svg>")
    assert html_en_morceaux(ligne, largeur=60) == [
        '<svg viewBox="0 0 10 10">', *['<rect x="1" y="2"/>'] * 10,
        "<!-- note -->", "<br>", '<input type="text">', "</svg>"]


def test_une_ligne_ferme_ce_qu_une_autre_a_ouvert():
    """Une balise dont la partenaire est sur une autre ligne reste seule."""
    ligne = ('</div></section><div class="suite">' + "<span>x</span>" * 20
             + '<div class="ouverte">texte')
    morceaux = html_en_morceaux(ligne, largeur=50)
    assert "".join(morceaux) == ligne
    assert morceaux == ["</div>", "</section>", '<div class="suite">',
                        *["<span>x</span>"] * 20, '<div class="ouverte">', "texte"]


def test_un_blanc_entre_deux_elements_va_avec_le_suivant():
    ligne = "    " + "<b>gras</b> " * 30
    morceaux = html_en_morceaux(ligne + "\n", largeur=50)
    assert morceaux == ["    <b>gras</b>", *[" <b>gras</b>"] * 28, " <b>gras</b> \n"]


def test_rien_ne_se_perd_aux_bords():
    assert html_en_morceaux("") == []
    assert html_en_morceaux("\n\n") == ["\n", "\n"]
    assert html_en_morceaux("a\nb") == ["a\n", "b"]
    assert html_en_morceaux(" " * 400, largeur=10) == [" " * 400]


# -- les fichiers du dépôt -----------------------------------------------------


@pytest.mark.parametrize("chemin", ["moteur/donnees.json", "data/derive/equilibre.json",
                                    "tests/temoins/pages.json"])
def test_aucun_fichier_fabrique_n_a_de_ligne_demesuree(chemin):
    """Le paquet, le bilan et le témoin des pages tenaient chacun une ligne de
    55 000 à 4 millions de caractères. Qu'un écrivain revienne au JSON compact,
    et ``scripts/arbre.py`` la signalerait de nouveau ; ce test le dit avant."""
    with (RACINE / chemin).open(encoding="utf-8") as fichier:
        longueur, rang = max((len(ligne.rstrip("\n")), rang)
                             for rang, ligne in enumerate(fichier, 1))
    assert longueur <= arbre.LIGNE_DEMESUREE, (
        f"{chemin}, ligne {rang} : {longueur} caractères — l'écrire par "
        "retraite_notionnelle.lignes")
