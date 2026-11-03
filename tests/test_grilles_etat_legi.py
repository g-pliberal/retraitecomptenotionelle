"""Les grilles de l'État d'avant le Noyau RH, lues au LEGI (action 158, étape 2).

Le Noyau RH du CISIRH (``data/reference/grilles/etat/``) ne date les grilles de
l'État que depuis 1989-1990 pour les enseignants, depuis 2005 à 2011 pour les
autres grands corps. Avant, leur source est le texte qui fixe l'échelonnement
indiciaire de chaque corps, que la base LEGI garde depuis sa première version
consolidée : ``scripts/fetch/dila_legi_grilles.py`` les relit comme ceux de la
territoriale, de l'hospitalière et des militaires, et les écrit sous
``data/reference/grilles/etat_legi/``. Un texte dont le titre ne dit pas le
versant se lit à ses visas : l'arrêté du 11 mai 2007 « fixant l'échelonnement
indiciaire des grades et emplois de la catégorie C » est de l'hospitalière.
Avant 1990, ni le LEGI ni le JORF de la DILA ne reproduisent les tableaux.

Les textes des essais sont ceux de l'index, recopiés tels quels ; chaque attendu
se lit dans le texte de l'essai. Puis la donnée, confrontée à la territoriale,
dont les échelles de la catégorie C valaient celles de l'État en 1998, et au
Noyau RH, là où les deux couvrent les mêmes années.
"""

from __future__ import annotations

import csv
import importlib.util
import re
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]


def _charger(nom: str, chemin: Path | None = None):
    chemin = chemin or RACINE / "scripts" / "fetch" / f"{nom}.py"
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules[nom] = module
    specification.loader.exec_module(module)
    return module


grilles = _charger("dila_legi_grilles")


def _valeurs(tableau, groupe: str, colonne: str = "") -> dict[str, int | str | None]:
    """L'échelon et sa valeur, pour un groupe et une colonne du tableau lu."""
    return {c.echelon: (c.hors_echelle or c.indice) for c in tableau.cellules
            if c.groupe == groupe and c.date == colonne}


# ---------------------------------------------------------------------------
# La lecture des tableaux de l'État
# ---------------------------------------------------------------------------

#: Arrêté du 1er avril 1998 fixant l'échelonnement indiciaire des grades et
#: emplois des catégories C et D, article 1er (LEGIARTI000019674624), tel quel :
#: l'échelle 1 en lignes, puis les échelles 2 à 5 en colonnes, chacune
#: annoncée par son numéro d'ordre, « 1° », « 2° ».
CATEGORIES_C_ET_D_1998 = (
    "L'échelonnement indiciaire applicable aux échelles 1, 2, 3, 4 et 5 de rémunération des "
    "catégories C et D instituées par l'article 1er du décret n° 70-78 du 27 janvier 1970 "
    "susvisé est fixé ainsi qu'il suit à compter du 1er avril 1998 : 1° En ce qui concerne "
    "l'échelle 1 : Echelons Indices bruts 1er échelon 244 2e échelon 250 3e échelon 260 4e "
    "échelon 268 5e échelon 280 6e échelon 293 7e échelon 303 8e échelon 314 2° En ce qui "
    "concerne les autres échelles : Echelons Indices bruts Echelle 2 Echelle 3 Echelle 4 "
    "Echelle 5 11e échelon 343 364 382 427 10e échelon 321 347 374 396 9e échelon 314 333 "
    "360 379 8e échelon 303 324 345 363 7e échelon 294 311 333 347 6e échelon 289 301 320 "
    "334 5e échelon 277 290 307 321 4e échelon 267 274 294 306 3e échelon 260 263 277 291 2e "
    "échelon 253 257 268 274 1er échelon 245 251 259 267")


def test_les_echelles_annoncees_par_leur_numero_d_ordre():
    tableau = grilles.lire_tableau(CATEGORIES_C_ET_D_1998)
    assert not tableau.refus, tableau.refus
    assert [grilles.cle_groupe(g) for g in tableau.groupes] == [
        "echelle-1", "echelle-2", "echelle-3", "echelle-4", "echelle-5"]
    assert _valeurs(tableau, tableau.groupes[0], "1998-04-01") == {
        "1": 244, "2": 250, "3": 260, "4": 268, "5": 280, "6": 293, "7": 303, "8": 314}
    # La date d'effet de la phrase vaut pour les deux tableaux de l'article.
    assert _valeurs(tableau, "Echelle 2", "1998-04-01") == {
        "11": 343, "10": 321, "9": 314, "8": 303, "7": 294, "6": 289, "5": 277, "4": 267,
        "3": 260, "2": 253, "1": 245}
    assert _valeurs(tableau, "Echelle 5", "1998-04-01")["11"] == 427
    assert _valeurs(tableau, "Echelle 5", "1998-04-01")["1"] == 267


#: Arrêté du 22 août 1990 fixant l'échelonnement indiciaire applicable aux
#: professeurs des écoles, article 2 (LEGIARTI000019764438), tel quel : la date
#: d'effet s'écrit entre « applicable » et le groupe.
PROFESSEURS_DES_ECOLES_1990 = (
    "L'échelonnement indiciaire applicable à compter du 1er septembre 1990 aux professeurs "
    "des écoles de classe normale est fixé, en indices bruts, ainsi qu'il suit : Indices bruts "
    "11e échelon 801 10e échelon 741 9e échelon 682 8e échelon 634 7e échelon 587 6e échelon "
    "550 5e échelon 510 4e échelon 480 3e échelon 450 2e échelon 423 1er échelon 379")


def test_la_date_entre_applicable_et_le_groupe_n_est_pas_le_groupe():
    tableau = grilles.lire_tableau(PROFESSEURS_DES_ECOLES_1990)
    assert tableau.groupes == ["professeurs des écoles de classe normale"]
    assert _valeurs(tableau, tableau.groupes[0])["11"] == 801
    assert _valeurs(tableau, tableau.groupes[0])["1"] == 379


#: Décret n° 2010-1007 du 26 août 2010, article 6, version du 1er septembre 2010
#: (LEGIARTI000022782199), tel quel : l'en-tête « CLASSES ET ÉCHELONS ».
PROFESSEURS_DES_ECOLES_2010 = (
    "L'échelonnement indiciaire applicable aux professeurs des écoles régis par le décret n° "
    "90-680 du 1er août 1990 susvisé est fixé, en indices bruts, ainsi qu'il suit : CLASSES ET "
    "ÉCHELONS INDICES BRUTS Professeur des écoles hors classe 7e échelon 966 6e échelon 910 5e "
    "échelon 850 4e échelon 780 3e échelon 726 2e échelon 672 1er échelon 587 Professeur des "
    "écoles de classe normale 11e échelon 801 10e échelon 741 9e échelon 682 8e échelon 634 7e "
    "échelon 587 6e échelon 550 5e échelon 529 4e échelon 500 3e échelon 469 2e échelon 423 1er "
    "échelon 379")


def test_l_en_tete_classes_et_echelons_ne_nomme_aucun_groupe():
    tableau = grilles.lire_tableau(PROFESSEURS_DES_ECOLES_2010)
    assert tableau.groupes == ["Professeur des écoles hors classe",
                               "Professeur des écoles de classe normale"]
    assert _valeurs(tableau, "Professeur des écoles de classe normale")["5"] == 529


#: Arrêté du 3 février 1993 relatif à l'échelonnement indiciaire des personnels
#: techniques de l'Assistance publique - hôpitaux de Paris, version du 1er janvier
#: 2017 (LEGIARTI000037626639), abrégé de ses deux derniers grades : le LEGI met
#: en tête la note qui dit pourquoi la version reste en vigueur.
INGENIEURS_APHP_2017 = (
    "Conformément aux dispositions de l'article 5 de l’arrêté du 16 novembre 2018 : L’arrêté du "
    "3 février 1993 relatif à l'échelonnement indiciaire du corps des ingénieurs hospitaliers de "
    "l'Assistance publique-hôpitaux de Paris est abrogé. Ses dispositions restent en vigueur à "
    "seule fin de mettre en œuvre l'article 1er du présent arrêté. GRADES ET ÉCHELONS INDICES "
    "BRUTS à compter du 1er janvier 2017 Ingénieur hospitalier en chef de classe exceptionnelle "
    "7e échelon HEB 6e échelon HEA 5e échelon 1 021 4e échelon 971 3e échelon 906 2e échelon 835 "
    "1er échelon 755")


def test_la_note_du_legi_en_tete_de_l_article_ne_nomme_pas_le_groupe():
    tableau = grilles.lire_tableau(INGENIEURS_APHP_2017)
    assert tableau.groupes == ["Ingénieur hospitalier en chef de classe exceptionnelle"]
    assert _valeurs(tableau, tableau.groupes[0], "2017-01-01") == {
        "7": "B", "6": "A", "5": 1021, "4": 971, "3": 906, "2": 835, "1": 755}


#: Décret n° 2008-836 du 22 août 2008, article 10, version du 25 août 2008
#: (LEGIARTI000019373430), tel quel : deux tableaux, chacun introduit par sa
#: phrase.
MAYOTTE_2008 = (
    "1. L'échelonnement indiciaire applicable aux agents techniques de Mayotte régis par le "
    "décret n° 2005-138 du 17 février 2005 susvisé est fixé ainsi qu'il suit : GRADES ET "
    "ÉCHELONS INDICES BRUTS Agent technique principal 5e échelon 250 4e échelon 222 3e échelon "
    "190 2e échelon 169 1er échelon 128 Agent technique 8e échelon 237 7e échelon 209 6e "
    "échelon 178 5e échelon 149 4e échelon 127 3e échelon 117 2e échelon 108 1er échelon 100 "
    "2. L'échelonnement indiciaire applicable aux agents administratifs de Mayotte régis par le "
    "décret n° 2005-139 du 17 février 2005 susvisé est fixé ainsi qu'il suit : GRADES ET "
    "ÉCHELONS INDICES BRUTS Agent administratif principal 5e échelon 250 4e échelon 222 3e "
    "échelon 190 2e échelon 169 1er échelon 128 Agent administratif 8e échelon 237 7e échelon "
    "209 6e échelon 178 5e échelon 149 4e échelon 127 3e échelon 117 2e échelon 108 1er "
    "échelon 100")


def test_le_second_tableau_d_un_article_est_nomme_apres_sa_phrase():
    tableau = grilles.lire_tableau(MAYOTTE_2008)
    assert tableau.groupes == ["Agent technique principal", "Agent technique",
                               "Agent administratif principal", "Agent administratif"]
    assert _valeurs(tableau, "Agent administratif")["8"] == 237


#: Arrêté du 29 janvier 2014 relatif à l'échelonnement indiciaire de la catégorie C
#: de l'hospitalière, article 1er, version du 1er février 2014
#: (LEGIARTI000028541999), abrégé des échelons 3 à 10 : le second tableau met les
#: échelles 4 et 5 en colonnes.
ECHELLES_HOSPITALIERES_2014 = (
    "I. ― L'échelonnement indiciaire applicable à l'échelle 3 de rémunération de la catégorie C "
    "instituée par l'article 1er du décret n° 2006-228 du 24 février 2006 susvisé est fixé "
    "ainsi qu'il suit : ÉCHELONS INDICES BRUTS Echelle 3 11e échelon 393 2e échelon 334 1er "
    "échelon 330 II. - L'échelonnement indiciaire applicable aux échelles 4 et 5 de "
    "rémunération de la catégorie C instituées par l'article 1er du décret n° 2006-228 du 24 "
    "février 2006 susvisé est fixé ainsi qu'il suit : ÉCHELONS INDICES BRUTS Echelle 4 "
    "Echelle 5 12e échelon 424 459 11e échelon 416 447 2e échelon 333 342 1er échelon 331 336")


def test_les_echelles_en_colonnes_du_second_tableau():
    tableau = grilles.lire_tableau(ECHELLES_HOSPITALIERES_2014)
    assert not tableau.refus, tableau.refus
    assert tableau.groupes == ["Echelle 3", "Echelle 4", "Echelle 5"]
    assert _valeurs(tableau, "Echelle 4") == {"12": 424, "11": 416, "2": 333, "1": 331}
    assert _valeurs(tableau, "Echelle 5") == {"12": 459, "11": 447, "2": 342, "1": 336}


#: Le même arrêté, article 2, même version (LEGIARTI000028542001), abrégé : les
#: valeurs du 1er janvier 2015, date que chaque phrase écrit avant « suit : ».
ECHELLES_HOSPITALIERES_2015 = (
    "I. ― A compter du 1er janvier 2015, l'échelonnement indiciaire applicable à l'échelle 3 de "
    "rémunération de la catégorie C instituée par l'article 1er du décret n° 2006-228 du 24 "
    "février 2006 susvisé est fixé ainsi qu'il suit : ÉCHELONS INDICES BRUTS Echelle 3 11e "
    "échelon 400 2e échelon 341 1er échelon 340 II. - A compter du 1er janvier 2015, "
    "l'échelonnement indiciaire applicable aux échelles 4 et 5 de rémunération de la catégorie C "
    "instituées par l'article 1er du décret n° 2006-228 du 24 février 2006 susvisé est fixé "
    "ainsi qu'il suit : ÉCHELONS INDICES BRUTS Echelle 4 Echelle 5 12e échelon 432 465 1er "
    "échelon 342 348")


def test_la_date_que_la_phrase_ecrit_avant_suit_date_le_tableau():
    tableau = grilles.lire_tableau(ECHELLES_HOSPITALIERES_2015)
    assert not tableau.refus, tableau.refus
    assert _valeurs(tableau, "Echelle 3", "2015-01-01") == {"11": 400, "2": 341, "1": 340}
    assert _valeurs(tableau, "Echelle 4", "2015-01-01") == {"12": 432, "1": 342}
    assert _valeurs(tableau, "Echelle 3") == {}


#: Arrêté relatif à l'échelonnement indiciaire des moniteurs-éducateurs de
#: l'hospitalière, article 1er, version du 7 février 2014 (LEGIARTI000028567695),
#: abrégé des échelons 3 à 12 : la première colonne dit sa date en mots.
MONITEURS_EDUCATEURS_2014 = (
    "L'échelonnement indiciaire applicable aux deux grades du corps des moniteurs-éducateurs de "
    "la fonction publique hospitalière est fixé ainsi qu'il suit à compter de la date d'entrée "
    "en vigueur du décret n° 2014-103 du 4 février 2014 susvisé : ÉCHELONS INDICES BRUTS A "
    "compter de la date d'entrée en vigueur du présent arrêté A compter du 1er janvier 2015 "
    "Grade des moniteurs-éducateurs principaux 13e échelon 614 614 2e échelon 357 357 1er "
    "échelon 350 350 Grade des moniteurs-éducateurs 13e échelon 576 576 1er échelon 340 342")


def test_la_date_d_entree_en_vigueur_ecrite_en_mots_ne_nomme_aucun_groupe():
    tableau = grilles.lire_tableau(MONITEURS_EDUCATEURS_2014)
    assert tableau.groupes == ["Grade des moniteurs-éducateurs principaux",
                               "Grade des moniteurs-éducateurs"]
    assert _valeurs(tableau, "Grade des moniteurs-éducateurs")["1"] == 340
    assert _valeurs(tableau, "Grade des moniteurs-éducateurs", "2015-01-01")["1"] == 342


# ---------------------------------------------------------------------------
# Le versant : au titre, puis aux visas
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("titre, versant", [
    ("Arrêté du 1er avril 1998 fixant l'échelonnement indiciaire des grades et emplois des "
     "catégories C et D", "etat"),
    ("Arrêté du 23 août 1995 fixant l'échelonnement indiciaire applicable aux attachés "
     "d'administration centrale", "etat"),
    # Les fonctionnaires de La Poste et de France Télécom sont de l'État.
    ("Arrêté du 11 septembre 1992 fixant l'échelonnement indiciaire applicable aux grades de "
     "contrôleur de La Poste et de contrôleur de France Télécom", "etat"),
    # Un cadre d'emplois, la police municipale, les sapeurs-pompiers professionnels,
    # la Ville de Paris : la territoriale, sans que le titre la nomme.
    ("Décret n°94-733 du 24 août 1994 portant échelonnement indiciaire applicable aux "
     "brigadiers-chefs principaux et aux chefs de police municipale", "territoriale"),
    ("Décret n°2000-44 du 20 janvier 2000 portant échelonnement indiciaire applicable au cadre "
     "d'emplois des chefs de service de police municipale", "territoriale"),
    ("Décret n° 2016-1237 du 20 septembre 2016 portant échelonnement indiciaire applicable aux "
     "médecins et pharmaciens de sapeurs-pompiers professionnels", "territoriale"),
    ("Arrêté du 28 mai 1997 fixant l'échelonnement indiciaire applicable au corps des attachés "
     "d'administration de la ville de Paris", "territoriale"),
    # L'Assistance publique - hôpitaux de Paris, les directeurs d'hôpital : l'hospitalière.
    ("Arrêté du 3 février 1993 relatif à l'échelonnement indiciaire des personnels techniques "
     "de l'Assistance publique - hôpitaux de Paris", "hospitaliere"),
    ("Décret n° 2025-1146 du 27 novembre 2025 fixant l'échelonnement indiciaire applicable aux "
     "directeurs d'hôpital", "hospitaliere"),
])
def test_le_versant_de_l_etat_se_lit_au_titre(titre, versant):
    assert grilles.versant(titre) == versant
    assert grilles.TITRE_GRILLE.search(titre)


TITRE_CATEGORIE_C_2007 = ("Arrêté du 11 mai 2007 fixant l'échelonnement indiciaire des grades "
                          "et emplois de la catégorie C")
#: Les visas de l'arrêté du 11 mai 2007 (LEGITEXT000019416904), abrégés : ceux de
#: l'hospitalière.
VISAS_CATEGORIE_C_2007 = (
    "Le ministre de l'économie, des finances et de l'industrie, le ministre de la fonction "
    "publique, le ministre de la santé et des solidarités et le ministre délégué au budget et à "
    "la réforme de l'Etat, porte-parole du Gouvernement, Vu le décret n° 2006-227 du 24 février "
    "2006 relatif à l'organisation des carrières des fonctionnaires hospitaliers de catégorie C, "
    "modifié par le décret n° 2007-836 du 11 mai 2007 ; Vu le décret n° 2006-228 du 24 février "
    "2006 instituant différentes échelles de rémunération pour les fonctionnaires hospitaliers "
    "de catégorie C, modifié par le décret n° 2007-838 du 11 mai 2007, Arrêtent : Fait à Paris, "
    "le 11 mai 2007.")
TITRE_CATEGORIES_C_ET_D_1998 = ("Arrêté du 1er avril 1998 fixant l'échelonnement indiciaire des "
                                "grades et emplois des catégories C et D")
#: Les visas de l'arrêté du 1er avril 1998 (LEGITEXT000019674620), abrégés : ceux
#: de l'État.
VISAS_CATEGORIES_C_ET_D_1998 = (
    "Le ministre de l'économie, des finances et de l'industrie, le ministre de la fonction "
    "publique, de la réforme de l'Etat et de la décentralisation et le secrétaire d'Etat au "
    "budget, Vu le décret n° 48-1108 du 10 juillet 1948 modifié portant classement hiérarchique "
    "des grades et emplois des personnels civils et militaires de l'Etat relevant du régime "
    "général des retraites ; Vu le décret n° 70-78 du 27 janvier 1970 modifié instituant "
    "différentes échelles de rémunération pour les catégories C et D des fonctionnaires de "
    "l'Etat ; Vu le décret n° 70-79 du 27 janvier 1970 modifié relatif à l'organisation des "
    "carrières des fonctionnaires des catégories C et D ; Vu l'arrêté du 27 janvier 1970 "
    "modifié fixant l'échelonnement indiciaire des grades et emplois des catégories C et D, "
    "Arrêtent : Fait à Paris, le 1er avril 1998.")


def test_un_titre_qui_tait_le_versant_se_lit_a_ses_visas():
    assert grilles.versant(TITRE_CATEGORIE_C_2007, VISAS_CATEGORIE_C_2007) == "hospitaliere"
    assert grilles.versant(TITRE_CATEGORIES_C_ET_D_1998,
                           VISAS_CATEGORIES_C_ET_D_1998) == "etat"
    # Sans visas, le titre muet est de l'État ; les visas ne priment pas sur le titre.
    assert grilles.versant(TITRE_CATEGORIE_C_2007) == "etat"
    assert grilles.versant(
        "Décret n° 2009-369 du 1er avril 2009 fixant l'échelonnement indiciaire de certains "
        "personnels relevant du ministère de l'intérieur, de l'outre-mer et des collectivités "
        "territoriales", VISAS_CATEGORIE_C_2007) == "etat"


# ---------------------------------------------------------------------------
# L'extraction et la certification
# ---------------------------------------------------------------------------

EN = "2999-01-01"

#: Arrêté du 11 mai 2007, article 1er (LEGIARTI000019416905), tel quel.
CATEGORIE_C_2007 = (
    "L'échelonnement indiciaire applicable aux échelles 3, 4 et 5 de rémunération de la "
    "catégorie C instituées par l'article 1er du décret du 24 février 2006 susvisé est fixé "
    "ainsi qu'il suit : ÉCHELONS INDICES BRUTS Echelle 3 Echelle 4 Echelle 5 11e échelon 388 "
    "409 446 10e échelon 364 382 427 9e échelon 347 374 396 8e échelon 333 360 379 7e échelon "
    "324 343 363 6e échelon 314 333 347 5e échelon 305 320 334 4e échelon 298 307 321 3e "
    "échelon 293 298 307 2e échelon 287 290 298 1er échelon 281 287 290")


@pytest.fixture
def index(tmp_path: Path) -> Path:
    """Un index LEGI de quelques documents, au schéma de ``dila_index.py`` : l'arrêté
    du 1er avril 1998, de l'État, et l'arrêté du 11 mai 2007, de l'hospitalière par
    ses visas, chacun avec son article 1er ; un décret des trois versants, qui ne
    compte pas."""
    dila = _charger("dila_index")
    chemin = tmp_path / "legi.sqlite"
    db = dila.ouvrir(chemin)
    lignes = [
        ("LEGITEXT000019674620", "1998-04-03", EN, "ARRETE", "", TITRE_CATEGORIES_C_ET_D_1998,
         VISAS_CATEGORIES_C_ET_D_1998),
        ("LEGIARTI000019674624", "1998-04-03", EN, "Article ARRETE", "1",
         TITRE_CATEGORIES_C_ET_D_1998, CATEGORIES_C_ET_D_1998),
        ("LEGIARTI000019674623", "1998-04-03", EN, "Article ARRETE", "2",
         TITRE_CATEGORIES_C_ET_D_1998,
         "Le présent arrêté sera publié au Journal officiel de la République française."),
        ("LEGITEXT000019416904", "2006-11-01", "2008-07-01", "ARRETE", "",
         TITRE_CATEGORIE_C_2007, VISAS_CATEGORIE_C_2007),
        ("LEGIARTI000019416905", "2006-11-01", "2008-07-01", "Article ARRETE", "1",
         TITRE_CATEGORIE_C_2007, CATEGORIE_C_2007),
        ("LEGITEXT000036280786", "2018-01-01", EN, "DECRET", "",
         "Décret n° 2017-1737 du 21 décembre 2017 modifiant l'échelonnement indiciaire de divers "
         "corps, cadres d'emplois et emplois de la fonction publique de l'Etat, de la fonction "
         "publique territoriale, et de la fonction publique hospitalière", "…"),
    ]
    db.executemany("INSERT INTO doc VALUES (?,?,?,?,?,?,?)", lignes)
    db.execute("INSERT INTO meta VALUES ('dump', 'Freemium_legi_global_20250713-140000.tar.gz')")
    db.execute("INSERT INTO meta VALUES ('dernier_increment', '20261102-213929')")
    db.commit()
    db.close()
    return chemin


def test_l_extraction_ecrit_les_grilles_de_l_etat_a_part_du_noyau_rh(index, tmp_path):
    extrait = grilles.extraire(index)
    etat = extrait["etat_legi"]
    (texte,) = etat["textes"]
    assert (texte["texte"], texte["numero"], texte["signature"], texte["articles_lus"]) == (
        "LEGITEXT000019674620", "", "1998-04-01", "1")
    assert [g["grille"] for g in etat["grilles"]] == [
        "echelle-1", "echelle-2", "echelle-3", "echelle-4", "echelle-5"]
    premier = [(e["debut"], e["fin"], e["indice"], e["article"]) for e in etat["echelons"]
               if e["grille"] == "echelle-1" and e["echelon"] == "1"]
    assert premier == [("1998-04-03", "", "244", "LEGIARTI000019674624")]
    # L'arrêté du 11 mai 2007, muet au titre, est de l'hospitalière par ses visas.
    (hospitalier,) = extrait["hospitaliere"]["textes"]
    assert hospitalier["texte"] == "LEGITEXT000019416904"
    assert extrait["territoriale"]["textes"] == extrait["militaires"]["textes"] == []

    brut = grilles.brut(extrait, source="essai")
    cle = "LEGITEXT000019674620|echelle-5|11|1998-04-03"
    assert (brut["etat_legi"]["indice"][cle], brut["etat_legi"]["rang"][cle]) == (427, 11)
    # Le dossier ``etat``, celui du Noyau RH, n'est pas touché.
    grilles.ecrire_reference(extrait, tmp_path / "grilles")
    assert sorted(p.name for p in (tmp_path / "grilles").iterdir()) == [
        "etat_legi", "hospitaliere", "militaires", "territoriale"]


def _lire_csv(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def test_verifier_donnees_certifie_les_grilles_de_l_etat_lues_au_legi(index, tmp_path,
                                                                      monkeypatch):
    import dataclasses
    import json

    verifier = _charger("verifier_donnees", RACINE / "scripts" / "verifier_donnees.py")
    monkeypatch.setattr(verifier, "BRUT", tmp_path)
    extrait = grilles.extraire(index)
    (tmp_path / "dila_legi_grilles.json").write_text(
        json.dumps(grilles.brut(extrait, source="essai")), encoding="utf-8")
    dossier = tmp_path / "grilles"
    grilles.ecrire_reference(extrait, dossier)

    certifications = [c for c in verifier.CERTIFICATIONS if c.nom.startswith("grilles_etat_legi_")]
    assert sorted(c.nom for c in certifications) == sorted(
        f"grilles_etat_legi_{serie}"
        for serie in ("rang", "indice", "rang_presume", "indice_presume"))
    for certification in certifications:
        assert certification.chemin == RACINE / "data" / "reference" / "grilles" / "etat_legi" / \
            "echelons.csv"
        messages, trace = dataclasses.replace(
            certification, chemin=dossier / "etat_legi" / "echelons.csv").confronter(
                appliquer=True)
        assert messages[0].startswith(("OK", "RIEN")), messages
    assert {l["fiabilite"] for l in _lire_csv(dossier / "etat_legi" / "echelons.csv")} == {
        "certifiee"}


# ---------------------------------------------------------------------------
# La donnée, confrontée à la territoriale et au Noyau RH
# ---------------------------------------------------------------------------

GRILLES = RACINE / "data" / "reference" / "grilles"


def _en_vigueur(lignes: list[dict[str, str]], le: str) -> list[dict[str, str]]:
    return [l for l in lignes if l["debut"] <= le and (not l["fin"] or le <= l["fin"])]


def _hauteurs(lignes: list[dict[str, str]]) -> list[str]:
    """Les indices d'une grille, ou ses lettres de hors-échelle, du plus bas au
    plus haut : le noyau ne numérote pas toujours les échelons comme le texte."""
    return sorted((l["indice"] or f"HE{l['hors_echelle']}") for l in lignes)


def _legi(texte: str, grille: str, le: str) -> list[dict[str, str]]:
    lignes = [l for l in _en_vigueur(_lire_csv(GRILLES / "etat_legi" / "echelons.csv"), le)
              if l["texte"] == texte and l["grille"] == grille]
    assert lignes and all(l["fiabilite"] == "certifiee" for l in lignes), (grille, le)
    return lignes


def _noyau(grille: str, le: str) -> list[dict[str, str]]:
    """Les échelons d'une grille du noyau, sans ceux du stagiaire, de l'élève ni
    l'échelon provisoire, que les textes de ces grilles n'écrivent pas."""
    lignes = [l for l in _en_vigueur(_lire_csv(GRILLES / "etat" / "echelons.csv"), le)
              if l["grille"] == grille and l["nature"] not in ("stagiaire", "eleve", "provisoire")]
    assert lignes, (grille, le)
    return lignes


#: Des grilles du Noyau RH (CISIRH, juillet 2026 : ``grilles/etat/``), par leur
#: identifiant, et celles du LEGI qui leur répondent, aux dates où les deux
#: couvrent le même corps : les arrêtés du 22 août 1990 (professeurs des écoles)
#: et du 30 mai 1990 (certifiés, agrégés), que le noyau ne rattache qu'au décret
#: de 2010 ; l'arrêté du 23 août 1995 des attachés d'administration centrale,
#: dont le noyau ne date la grille que d'octobre 2011, mais qui vaut, indice pour
#: indice, celle des attachés d'administration de recherche et de formation,
#: qu'il porte depuis 1993.
NOYAU = {
    ("00050", "LEGITEXT000019764435", "professeurs-des-ecoles-de-classe-normale"):
        ("1995-06-01", "2005-06-01"),
    ("01155", "LEGITEXT000019764403", "professeurs-certifies-de-classe-normale"):
        ("1995-06-01", "2005-06-01"),
    ("01189", "LEGITEXT000019762700",
     "professeurs-agreges-de-classe-normale-et-aux-professeurs-assimiles-secretaires-generaux-et-"
     "directeurs-des-etudes-de-l-ecole-francaise-d-archeologie-d-athenes"):
        ("1990-06-01", "2000-06-01", "2009-06-01"),
    ("01103", "LEGITEXT000019720224", "attache"): ("2000-06-01", "2009-06-01"),
}


@pytest.mark.parametrize("noyau, texte, grille", sorted(NOYAU))
def test_les_grilles_de_l_etat_lues_au_legi_redonnent_celles_du_noyau_rh(noyau, texte, grille):
    for le in NOYAU[(noyau, texte, grille)]:
        assert _hauteurs(_legi(texte, grille, le)) == _hauteurs(_noyau(noyau, le)), le


def test_les_echelles_de_1998_precedent_le_noyau_et_valent_celles_de_la_territoriale():
    """Les échelles 2 à 5 de la catégorie C de l'État, au 1er avril 1998 (arrêté
    du 1er avril 1998), sont celles de la territoriale au même jour (décret
    n° 87-1108, lu au LEGI à part) ; le noyau ne date les échelles de la
    catégorie C de l'État que du 1er novembre 2006."""
    territoriale = _en_vigueur(_lire_csv(GRILLES / "territoriale" / "echelons.csv"), "1998-06-01")
    for echelle in ("echelle-2", "echelle-3", "echelle-4", "echelle-5"):
        etat = _legi("LEGITEXT000019674620", echelle, "1998-06-01")
        assert _hauteurs(etat) == _hauteurs(
            [l for l in territoriale if l["texte"] == "LEGITEXT000006065792"
             and l["grille"] == echelle]), echelle
    assert _hauteurs(_legi("LEGITEXT000019674620", "echelle-3", "1998-06-01")) == [
        "251", "257", "263", "274", "290", "301", "311", "324", "333", "347", "364"]
    noyau = _lire_csv(GRILLES / "etat" / "grilles.csv")
    assert {l["grille"]: l["debut"] for l in noyau if re.fullmatch(
        r"Grille partagée de catégorie C échelle \d", l["libelle"])} == {
        "01906": "2006-11-01", "01890": "2006-11-01", "01900": "2006-11-01",
        "01903": "2006-11-01", "01927": "2006-11-01"}
