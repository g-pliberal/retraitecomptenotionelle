"""Les reclassements d'une grille à la suivante, lus au LEGI (action 158).

Quand un texte refait une grille, il dit, échelon par échelon, où passe
l'agent de l'ancienne : « conformément au tableau de correspondance suivant ».
L'index LEGI du dépôt garde ces tableaux aplatis — une suite d'échelons et de
phrases d'ancienneté, sans les cases —, et
``scripts/fetch/dila_legi_reclassements.py`` les relit. Les textes des tests
sont ceux des articles du LEGI, recopiés ; les valeurs attendues, lues dans
ces mêmes articles, et non dans ce que rend le script.
"""

from __future__ import annotations

import csv
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))

import dila_legi_reclassements as rec  # noqa: E402

DOSSIER = RACINE / "data" / "reference" / "grilles" / "reclassements"

#: Décret n° 2016-596 du 12 mai 2016, article 15 (LEGIARTI000032540886) : les
#: grades de l'échelle 4 de la territoriale passent en échelle C2 au
#: 1er janvier 2017.
ECHELLE_4_EN_C2 = (
    "Les fonctionnaires de catégorie C appartenant à un grade relevant de l'échelle 4 de "
    "rémunération instituée par le décret du 30 décembre 1987 précité, ainsi que les "
    "fonctionnaires détachés dans l'un de ces grades, sont reclassés dans un grade relevant de "
    "l'échelle de rémunération C2 mentionnée à l'article 1er, conformément au tableau suivant : "
    "SITUATION dans le grade en échelle 4 SITUATION dans le grade en échelle C2 ANCIENNETÉ "
    "D'ÉCHELON conservée dans la limite de la durée d'échelon 12e échelon 9e échelon Ancienneté "
    "acquise 11e échelon 8e échelon 1/2 de l'ancienneté acquise 10e échelon 8e échelon Sans "
    "ancienneté 9e échelon 7e échelon 2/3 de l'ancienneté acquise 8e échelon 6e échelon 2/3 de "
    "l'ancienneté acquise 7e échelon 5e échelon Ancienneté acquise 6e échelon 4e échelon "
    "Ancienneté acquise 5e échelon 3e échelon Ancienneté acquise 4e échelon 2e échelon "
    "Ancienneté acquise 3e échelon 2e échelon Sans ancienneté 2e échelon 1er échelon Ancienneté "
    "acquise 1er échelon 1er échelon Sans ancienneté")

#: Décret n° 2016-219 du 26 février 2016, les contremaîtres de France Télécom
#: (LEGIARTI000032128530) : le 12e échelon se partage selon l'ancienneté qu'on
#: y a, et l'ancienneté conservée s'augmente de mois.
CONTREMAITRES = (
    "ANCIENNE SITUATION SITUATION NOUVELLE Echelon Ancienneté conservée dans la limite de la "
    "durée de l'échelon Contremaître Contremaître 12e échelon - à partir de 4 ans 8e échelon "
    "Ancienneté acquise au-delà de 4 ans - avant 4 ans 7e échelon Ancienneté acquise 11e échelon "
    "6e échelon Ancienneté acquise 10e échelon 5e échelon Ancienneté acquise 6e échelon 1er "
    "échelon 1/12 de l'ancienneté acquise augmenté de 33 mois 5e échelon 1er échelon 1/12 de "
    "l'ancienneté acquise augmenté de 30 mois")

#: Décret n° 95-230 du 28 février 1995, les ingénieurs des travaux ruraux
#: (LEGIARTI000006477704) : deux grades d'origine, nommés entre les lignes.
INGENIEURS = (
    "SITUATION ANCIENNE SITUATION NOUVELLE Ingénieur de classe exceptionnelle Ingénieur Echelon "
    "unique 9e échelon : ancienneté acquise dans la limite de 3 ans. Ingénieur de classe normale "
    "Ingénieur 8e échelon 8e échelon : ancienneté acquise majorée de 1 an dans la limite de "
    "4 ans. 7e échelon : - après 3 ans 8e échelon : ancienneté acquise diminuée de 3 ans. - "
    "avant 3 ans 7e échelon : ancienneté acquise majorée de 1 an.")


def _corps(article: str) -> str:
    return article.split("tableau suivant :", 1)[1]


def test_un_tableau_de_correspondance_se_lit_ligne_a_ligne():
    tableau = rec.lire_tableau(_corps(ECHELLE_4_EN_C2))
    assert not tableau.refus
    assert tableau.entete == ("SITUATION dans le grade en échelle 4 SITUATION dans le grade en "
                              "échelle C2 ANCIENNETÉ D'ÉCHELON conservée dans la limite de la "
                              "durée d'échelon")
    assert [(l.origine, l.nouveau, l.anciennete) for l in tableau.lignes] == [
        ("12", "9", "Ancienneté acquise"),
        ("11", "8", "1/2 de l'ancienneté acquise"),
        ("10", "8", "Sans ancienneté"),
        ("9", "7", "2/3 de l'ancienneté acquise"),
        ("8", "6", "2/3 de l'ancienneté acquise"),
        ("7", "5", "Ancienneté acquise"),
        ("6", "4", "Ancienneté acquise"),
        ("5", "3", "Ancienneté acquise"),
        ("4", "2", "Ancienneté acquise"),
        ("3", "2", "Sans ancienneté"),
        ("2", "1", "Ancienneté acquise"),
        ("1", "1", "Sans ancienneté"),
    ]
    assert {(l.groupe, l.condition) for l in tableau.lignes} == {("", "")}


def test_un_echelon_partage_selon_l_anciennete_donne_deux_lignes():
    tableau = rec.lire_tableau(CONTREMAITRES)
    assert not tableau.refus
    assert tableau.entete == ("ANCIENNE SITUATION SITUATION NOUVELLE Echelon Ancienneté "
                              "conservée dans la limite de la durée de l'échelon")
    assert [(l.groupe, l.origine, l.condition, l.nouveau, l.anciennete)
            for l in tableau.lignes] == [
        ("Contremaître Contremaître", "12", "à partir de 4 ans", "8",
         "Ancienneté acquise au-delà de 4 ans"),
        ("Contremaître Contremaître", "12", "avant 4 ans", "7", "Ancienneté acquise"),
        ("Contremaître Contremaître", "11", "", "6", "Ancienneté acquise"),
        ("Contremaître Contremaître", "10", "", "5", "Ancienneté acquise"),
        # « augmenté de 33 mois » finit la phrase d'ancienneté : ce n'est pas
        # le nom d'un grade qui ouvrirait la ligne suivante.
        ("Contremaître Contremaître", "6", "", "1",
         "1/12 de l'ancienneté acquise augmenté de 33 mois"),
        ("Contremaître Contremaître", "5", "", "1",
         "1/12 de l'ancienneté acquise augmenté de 30 mois"),
    ]


def test_les_grades_nommes_entre_les_lignes_font_les_groupes():
    tableau = rec.lire_tableau(INGENIEURS)
    assert not tableau.refus
    assert tableau.entete == "SITUATION ANCIENNE SITUATION NOUVELLE"
    exceptionnelle = "Ingénieur de classe exceptionnelle Ingénieur"
    normale = "Ingénieur de classe normale Ingénieur"
    assert [(l.groupe, l.origine, l.condition, l.nouveau, l.anciennete)
            for l in tableau.lignes] == [
        (exceptionnelle, "unique", "", "9", "ancienneté acquise dans la limite de 3 ans"),
        (normale, "8", "", "8", "ancienneté acquise majorée de 1 an dans la limite de 4 ans"),
        (normale, "7", "après 3 ans", "8", "ancienneté acquise diminuée de 3 ans"),
        (normale, "7", "avant 3 ans", "7", "ancienneté acquise majorée de 1 an"),
    ]


@pytest.mark.parametrize("corps, attendu", [
    # Les sages-femmes surveillantes-chefs (LEGIARTI000006706152) : chaque
    # ligne redit les titres de ses colonnes, qui ne sont pas une condition.
    ("SITUATION ACTUELLE = Sage-femme surveillante chef SITUATION NOUVELLE = Sage-femme "
     "surveillante-chef SITUATION ACTUELLE : 7e échelon SITUATION NOUVELLE : 5e échelon "
     "Ancienneté acquise dans la limite de trois ans. SITUATION ACTUELLE : 6e échelon SITUATION "
     "NOUVELLE : 4e échelon Ancienneté acquise dans la limite de trois ans.",
     [("7", "", "5", "Ancienneté acquise dans la limite de trois ans"),
      ("6", "", "4", "Ancienneté acquise dans la limite de trois ans")]),
    # Les contrôleurs des finances publiques (LEGIARTI000022751573) : « A partir »
    # sans accent, et l'en-tête qui finit par « l'échelon d'accueil ».
    ("ANCIENNE SITUATION NOUVELLE SITUATION Contrôleur principal Echelons Ancienneté conservée "
     "dans la limite de l'échelon d'accueil 1er échelon 3e échelon Ancienneté acquise. 2e "
     "échelon : A partir d'un an 5e échelon 4/3 de l'ancienneté acquise au-delà d'un an. ― avant "
     "un an 4e échelon Deux fois l'ancienneté acquise.",
     [("1", "", "3", "Ancienneté acquise"),
      ("2", "A partir d'un an", "5", "4/3 de l'ancienneté acquise au-delà d'un an"),
      ("2", "avant un an", "4", "Deux fois l'ancienneté acquise")]),
    # LEGIARTI000006473364 : « moins 3 ans » finit la phrase d'ancienneté.
    ("SITUATION ANCIENNE SITUATION NOUVELLE 9e échelon à partir de 3 ans d'ancienneté 10e "
     "échelon Ancienneté acquise moins 3 ans. 9e échelon avec moins de 3 ans d'ancienneté 9e "
     "échelon Ancienneté acquise. 8e échelon 8e échelon Ancienneté acquise.",
     [("9", "à partir de 3 ans d'ancienneté", "10", "Ancienneté acquise moins 3 ans"),
      ("9", "avec moins de 3 ans d'ancienneté", "9", "Ancienneté acquise"),
      ("8", "", "8", "Ancienneté acquise")]),
    # LEGIARTI000006414233 : le titre de la colonne d'ancienneté, redit à chaque
    # ligne, précède la valeur de la case.
    ("SITUATION ANCIENNE Echelon 4e échelon Ancienneté SITUATION NOUVELLE Echelon 4e échelon "
     "Ancienneté conservée, dans la limite de la durée de l'échelon Ancienneté acquise majorée "
     "de 1 an. SITUATION ANCIENNE Echelon 3e échelon Ancienneté SITUATION NOUVELLE Echelon 3e "
     "échelon Ancienneté conservée, dans la limite de la durée de l'échelon Ancienneté acquise.",
     [("4", "", "4", "Ancienneté acquise majorée de 1 an"), ("3", "", "3", "Ancienneté acquise")]),
    # LEGIARTI000023051220 : « la durée maximale de l'échelon d'accueil » finit
    # l'en-tête ; les grades qui suivent sont le groupe.
    ("GRADE D'ORIGINE GRADE D'INTÉGRATION ANCIENNETÉ D'ÉCHELON CONSERVÉE dans la limite de la "
     "durée maximale de l'échelon d'accueil Contrôleur de travaux en chef Technicien principal "
     "de 1re classe 8e échelon 9e échelon Ancienneté acquise 7e échelon 8e échelon 1/4 de "
     "l'ancienneté acquise, majoré de deux ans",
     [("8", "", "9", "Ancienneté acquise"), ("7", "", "8", "1/4 de l'ancienneté acquise, majoré "
                                                         "de deux ans")]),
    # La limite écrite entre parenthèses finit aussi l'en-tête.
    ("GRADE D'ORIGINE GRADE D'INTÉGRATION ANCIENNETÉ D'ÉCHELON CONSERVÉE (dans la limite de la "
     "durée de l'échelon d'accueil) Contrôleur de travaux en chef Technicien principal de 1re "
     "classe 8e échelon 9e échelon Ancienneté acquise 7e échelon 8e échelon Sans ancienneté",
     [("8", "", "9", "Ancienneté acquise"), ("7", "", "8", "Sans ancienneté")]),
    # LEGIARTI000006413831 : « ANCIENNETE CONSERVEE dans le nouveau grade ».
    ("ECHELONS DANS le grade le plus élevé dans l'ancienne situation ANCIENNETE CONSERVEE dans "
     "le nouveau grade 1er échelon 5e échelon Ancienneté acquise. 2e échelon 6e échelon Sans "
     "ancienneté. 3e échelon. 6e échelon Ancienneté acquise dans la limite de 4 ans.",
     [("1", "", "5", "Ancienneté acquise"), ("2", "", "6", "Sans ancienneté"),
      ("3", "", "6", "Ancienneté acquise dans la limite de 4 ans")]),
])
def test_les_titres_de_colonnes_et_les_fins_de_phrase_restent_a_leur_place(corps, attendu):
    tableau = rec.lire_tableau(corps)
    assert not tableau.refus
    assert [(l.origine, l.condition, l.nouveau, l.anciennete) for l in tableau.lignes] == attendu
    assert {l.groupe for l in tableau.lignes} <= {
        "", "Sage-femme surveillante-chef",
        "Contrôleur de travaux en chef Technicien principal de 1re classe"}


@pytest.mark.parametrize("corps, motif", [
    # Décret n° 2002-121, article 21 : l'assimilation pour la pension, sans
    # colonne d'ancienneté ; l'analyseur ne sait pas où finit chaque ligne.
    ("SITUATION ANCIENNE SITUATION NOUVELLE Echelle 1 Echelle 2 8e échelon : - après 5 ans "
     "11e échelon - entre 1 et 5 ans 10e échelon - jusqu'à 1 an 9e échelon 7e échelon : - après "
     "1 an 9e échelon - jusqu'à 1 an 8e échelon", "sans ancienneté"),
    # Un échelon nouveau qui baisse quand l'ancien monte : une lecture fausse.
    ("SITUATION ANCIENNE SITUATION NOUVELLE 3e échelon 3e échelon Ancienneté acquise "
     "2e échelon 4e échelon Ancienneté acquise 1er échelon 1er échelon Sans ancienneté",
     "baisse"),
    # Les tableaux dessinés en caractères, d'avant 1995.
    (":-------------------: 2e échelon : 1er échelon : Ancienneté acquise : 1er échelon : "
     "1er échelon : Sans ancienneté :", "caractères"),
    # Une seule ligne ne fait pas un tableau.
    ("SITUATION ANCIENNE SITUATION NOUVELLE 1er échelon 1er échelon Ancienneté acquise",
     "moins de deux lignes"),
])
def test_un_tableau_douteux_est_refuse_plutot_que_lu_de_travers(corps, motif):
    assert motif in rec.lire_tableau(corps).refus


def test_seul_le_reclassement_d_une_grille_a_la_suivante_est_retenu():
    """Le même tableau sert aux promotions (article 11 du même décret) : ce
    n'est pas le passage d'une grille à la suivante."""
    promotion = (
        "Les fonctionnaires relevant d'un grade classé en échelle de rémunération C1, promus dans "
        "un grade d'avancement situé en échelle de rémunération C2, sont classés dans ce grade "
        "conformément au tableau suivant : " + _corps(ECHELLE_4_EN_C2))
    # LEGIARTI000006564057 : un promu « reclassé » dans son nouveau grade n'a pas
    # changé de grille.
    promu_reclasse = (
        "Les agents promus au grade d'adjoint de contrôle principal de 1ère classe de la "
        "concurrence, de consommation et de la répression des fraudes sont reclassés dans ce "
        "grade conformément au tableau ci-après : " + _corps(ECHELLE_4_EN_C2))
    assert [extrait.reclassement for extrait in rec.tableaux(ECHELLE_4_EN_C2)] == [True]
    assert [extrait.reclassement for extrait in rec.tableaux(promotion)] == [False]
    assert [extrait.reclassement for extrait in rec.tableaux(promu_reclasse)] == [False]
    extrait, = rec.tableaux(ECHELLE_4_EN_C2)
    assert extrait.corps.strip().startswith("SITUATION dans le grade en échelle 4")
    assert extrait.intro.startswith("Les fonctionnaires de catégorie C appartenant")


@pytest.mark.parametrize("intro, attendu", [
    ("Les ingénieurs des travaux ruraux de classe exceptionnelle et de classe normale sont, au "
     "1er août 1993, intégrés dans le grade d'ingénieur des travaux ruraux créé par le présent "
     "décret et reclassés conformément au tableau ci-dessous :", "1993-08-01"),
    ("A compter du 1er janvier 2017, les fonctionnaires sont reclassés conformément au tableau "
     "suivant :", "2017-01-01"),
    # La date d'un texte cité n'est pas celle du reclassement.
    (ECHELLE_4_EN_C2.split(" SITUATION")[0], ""),
    # Action 158, B5 : la date qui suit le verbe. Décret n° 2017-194, art. 117
    # (LEGIARTI000034054901, en vigueur depuis le 2017-02-18), mot pour mot :
    ("Les ingénieurs des travaux publics de l'Etat ainsi que les fonctionnaires détachés dans "
     "ce corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance "
     "suivant :", "2017-01-01"),
    # Décret n° 98-416, art. 4 (LEGIARTI000006507125, depuis le 1996-09-01), sans virgule :
    ("Les professeurs des écoles nationales d'art hors classe sont reclassés au 1er septembre "
     "1996 conformément au tableau de correspondance ci-après :", "1996-09-01"),
    # Décret n° 95-720, art. 15 (LEGIARTI000006479055, depuis le 1995-08-01) : les dates
    # des textes cités précèdent celle du reclassement, qui suit le verbe.
    ("Les fonctionnaires titulaires des grades de greffier et de premier greffier, régis par "
     "le décret du 30 avril 1992 susvisé et placés dans l'une des positions prévues à "
     "l'article 32 de la loi du 11 janvier 1984 susvisée, sont reclassés, au 1er août 1995, "
     "dans le troisième grade conformément au tableau de correspondance ci-après :",
     "1995-08-01"),
    # Décret n° 2017-297, art. 13 (LEGIARTI000034158145, depuis le 2017-03-10) :
    ("Les ingénieurs des systèmes d'information et de communication ainsi que les "
     "fonctionnaires détachés dans le corps des ingénieurs des systèmes d'information et de "
     "communication sont nommés et reclassés, au 1er janvier 2017, conformément au tableau "
     "de correspondance suivant :", "2017-01-01"),
    # « intégrés dans » n'est pas suivi d'une date : celle qui compte suit « reclassés ».
    # Décret n° 2018-282, art. 4 (LEGIARTI000036821740, depuis le 2018-04-21) :
    ("Les inspecteurs des affaires maritimes intégrés dans le corps des ingénieurs des travaux "
     "publics de l'Etat sont reclassés, au 1er janvier 2017, conformément au tableau de "
     "correspondance suivant :", "2017-01-01"),
    # Décret n° 2017-182, art. 3 (LEGIARTI000034036681, depuis le 2017-02-16) :
    ("Les fonctionnaires relevant du troisième grade mentionné au même article sont reclassés "
     "avec effet au 1er janvier 2017 dans leur grade conformément au tableau de correspondance "
     "suivant :", "2017-01-01"),
    # Décret n° 2010-1139, art. 31 (LEGIARTI000022869523, du 2010-12-01 au 2017-01-01) :
    ("Avec une date d'effet au 1er juillet 2012, les personnels mentionnés au I qui auront "
     "accepté la proposition d'intégration prévue au II sont reclassés conformément aux "
     "tableaux de correspondance suivants :", "2012-07-01"),
    # Décret n° 96-980, art. 10 (LEGIARTI000006483170, depuis le 1995-08-01) : la date
    # suit le grade d'accueil, et le reclassement vient un an après l'entrée en vigueur.
    ("Les titulaires du grade provisoire de chef dessinateur prévu à l'article 9 ci-dessus, "
     "placés dans une situation prévue à l'article 32 de la loi du 11 janvier 1984 susvisée, "
     "sont reclassés dans le grade de dessinateur projeteur en chef au 1er août 1996, "
     "conformément au tableau de correspondance ci-après :", "1996-08-01"),
    # La phrase ne date pas le reclassement : « nommés au » (n° 98-268, art. 17,
    # LEGIARTI000006506606), « placés au » (n° 2001-325, art. 14, LEGIARTI000006567682).
    # Un autre article de leur décret le date (B5-bis, DATES_D_UN_AUTRE_ARTICLE).
    ("Les bibliothécaires de 1re et de 2e classes, placés au 1er janvier 1997 dans l'une des "
     "positions prévues à l'article 32 de la loi du 11 janvier 1984 susvisée, sont reclassés "
     "dans le grade de bibliothécaire conformément au tableau", ""),
])
def test_la_date_du_reclassement_est_celle_que_la_phrase_ecrit(intro, attendu):
    assert rec.date_effet(intro) == attendu


def _lire(nom: str) -> list[dict]:
    with (DOSSIER / f"{nom}.csv").open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.startswith("#")))


def _lignes(article: str) -> list[tuple]:
    return [(l["origine"], l["condition"], l["nouveau"], l["anciennete"])
            for l in sorted((l for l in _lire("lignes") if l["article"] == article),
                            key=lambda l: (int(l["tableau"]), int(l["ligne"])))]


def test_le_passage_de_l_echelle_4_en_c2_de_la_territoriale_est_dans_le_depot():
    """Recoupement au texte : l'article 15 du décret n° 2016-596, tel que le
    LEGI l'écrit, relu dans les fichiers de référence."""
    assert _lignes("LEGIARTI000032540886") == [
        ("12", "", "9", "Ancienneté acquise"),
        ("11", "", "8", "1/2 de l'ancienneté acquise"),
        ("10", "", "8", "Sans ancienneté"),
        ("9", "", "7", "2/3 de l'ancienneté acquise"),
        ("8", "", "6", "2/3 de l'ancienneté acquise"),
        ("7", "", "5", "Ancienneté acquise"),
        ("6", "", "4", "Ancienneté acquise"),
        ("5", "", "3", "Ancienneté acquise"),
        ("4", "", "2", "Ancienneté acquise"),
        ("3", "", "2", "Sans ancienneté"),
        ("2", "", "1", "Ancienneté acquise"),
        ("1", "", "1", "Sans ancienneté"),
    ]
    tableau, = [t for t in _lire("tableaux") if t["article"] == "LEGIARTI000032540886"]
    assert (tableau["texte"], tableau["numero"], tableau["debut"]) == (
        "LEGITEXT000032540869", "15", "2017-01-01")
    texte, = [t for t in _lire("textes") if t["texte"] == "LEGITEXT000032540869"]
    assert (texte["versant"], texte["numero"]) == ("territoriale", "2016-596")


def test_le_passage_de_l_ancienne_echelle_4_de_l_etat_en_2005_est_dans_le_depot():
    """Recoupement au texte : le décret n° 2005-1228, qui refait les échelles
    de la catégorie C de l'État au 1er octobre 2005, reclasse l'ancienne
    échelle 4 dans la nouvelle un échelon plus bas (LEGIARTI000006413829)."""
    assert _lignes("LEGIARTI000006413829") == [
        ("1", "", "1", "Sans ancienneté"),
        ("2", "", "1", "1/2 de l'ancienneté acquise"),
        *((str(n), "", str(n - 1), "Ancienneté acquise") for n in range(3, 12)),
    ]
    tableau, = [t for t in _lire("tableaux") if t["article"] == "LEGIARTI000006413829"]
    texte, = [t for t in _lire("textes") if t["texte"] == tableau["texte"]]
    assert (texte["versant"], texte["numero"], tableau["debut"]) == (
        "etat", "2005-1228", "2005-10-01")


def test_un_reclassement_publie_avant_son_effet_prend_la_date_que_le_texte_ecrit():
    """Recoupement au texte : le décret n° 2016-634, publié en mai 2016, reclasse
    les cadres supérieurs socio-éducatifs de l'hospitalière « A compter du
    1er janvier 2017 », un échelon plus haut (article 5, LEGIARTI000032562625)."""
    assert _lignes("LEGIARTI000032562625") == [
        (str(n), "", str(n + 1), "Ancienneté acquise") for n in range(7, 0, -1)]
    tableau, = [t for t in _lire("tableaux") if t["article"] == "LEGIARTI000032562625"]
    texte, = [t for t in _lire("textes") if t["texte"] == tableau["texte"]]
    assert (texte["versant"], texte["numero"]) == ("hospitaliere", "2016-634")
    assert (tableau["debut"], tableau["effet"]) == ("2016-05-22", "2017-01-01")


#: Action 158, B5 : les 30 tableaux dont la phrase écrit la date après le verbe
#: (« sont reclassés, au 1er janvier 2017, conformément au tableau »), chaque article
#: lu en vigueur à l'index LEGI ; la phrase de chacun est citée dans
#: docs/feuille_de_route/158/2026-11-05-b5-la-date-apres-reclasses.md.
DATES_APRES_LE_VERBE = {
    ("LEGIARTI000006479000", "1"): "1993-08-01",  # n° 95-691, art. 6
    ("LEGIARTI000006479055", "1"): "1995-08-01",  # n° 95-720, art. 15
    ("LEGIARTI000006484915", "1"): "1995-01-01",  # n° 97-571, art. 3
    ("LEGIARTI000006506641", "1"): "1996-08-01",  # n° 98-280, art. 4
    ("LEGIARTI000006507125", "1"): "1996-09-01",  # n° 98-416, art. 4
    ("LEGIARTI000033667099", "1"): "2017-01-01",  # n° 2016-1798, art. 27
    ("LEGIARTI000033708276", "1"): "2017-01-01",  # n° 2016-1881, art. 25
    ("LEGIARTI000033711235", "1"): "2017-01-01",  # n° 2016-1880, art. 11
    ("LEGIARTI000034054785", "1"): "2017-01-01",  # n° 2017-194, art. 23
    ("LEGIARTI000034054815", "1"): "2017-01-01",  # n° 2017-194, art. 46
    ("LEGIARTI000034054841", "1"): "2017-01-01",  # n° 2017-194, art. 68
    ("LEGIARTI000034054901", "1"): "2017-01-01",  # n° 2017-194, art. 117
    ("LEGIARTI000034054935", "1"): "2017-01-01",  # n° 2017-194, art. 144
    ("LEGIARTI000034158145", "1"): "2017-01-01",  # n° 2017-297, art. 13
    ("LEGIARTI000034167768", "1"): "2017-01-01",  # n° 2017-310, art. 16
    ("LEGIARTI000034302299", "1"): "2017-01-01",  # n° 2017-418, art. 18
    ("LEGIARTI000034460214", "1"): "2017-01-01",  # n° 2017-593, art. 6
    ("LEGIARTI000034460216", "1"): "2017-01-01",  # n° 2017-593, art. 7
    ("LEGIARTI000035590914", "1"): "2017-09-01",  # n° 2017-1350, art. 15
    ("LEGIARTI000035591052", "1"): "2017-09-01",  # n° 2017-1351, art. 14
    ("LEGIARTI000035591460", "1"): "2017-09-01",  # n° 2017-1352, art. 15
    ("LEGIARTI000035603897", "1"): "2017-01-01",  # n° 2017-1376, art. 20
    ("LEGIARTI000035646727", "1"): "2017-01-01",  # n° 2017-1404, art. 20
    ("LEGIARTI000035646835", "1"): "2017-01-01",  # n° 2017-1405, art. 16
    ("LEGIARTI000036729702", "1"): "2017-01-01",  # n° 2018-188, art. 13
    ("LEGIARTI000036821740", "1"): "2017-01-01",  # n° 2018-282, art. 4
    ("LEGIARTI000036821740", "2"): "2017-01-01",  # n° 2018-282, art. 4
    ("LEGIARTI000037214195", "1"): "2017-01-01",  # n° 2018-619, art. 19
    ("LEGIARTI000042506911", "1"): "2017-01-01",  # n° 2020-1362, art. 9
    ("LEGIARTI000042559783", "1"): "2017-09-01",  # n° 2020-1435, art. 9
    # « reclassés avec effet au », « Avec une date d'effet au », « reclassés dans le
    # grade de … au » :
    ("LEGIARTI000034036681", "1"): "2017-01-01",  # n° 2017-182, art. 3, I
    ("LEGIARTI000034036681", "3"): "2017-01-01",  # n° 2017-182, art. 3
    ("LEGIARTI000022913217", "1"): "2010-12-01",  # n° 88-1077, art. 50-1
    ("LEGIARTI000022869520", "1"): "2010-12-01",  # n° 2010-1139, art. 30
    ("LEGIARTI000022869523", "1"): "2012-07-01",  # n° 2010-1139, art. 31
    ("LEGIARTI000006483170", "1"): "1996-08-01",  # n° 96-980, art. 10
}


def test_la_date_qui_suit_le_verbe_est_la_date_du_reclassement():
    """Action 158, B5. Ces 36 tableaux restaient datés de l'entrée en vigueur de leur
    article : le lecteur ne lisait la date qu'avant « reclassés ». Vingt-deux la
    précèdent (reclassement rétroactif : le n° 2020-1362, en vigueur le 2020-11-09,
    reclasse au 1er janvier 2017), dix la redisent, quatre la suivent (n° 2016-1880,
    n° 2010-1139 deux fois, n° 96-980 : un an après)."""
    tableaux = {(t["article"], t["tableau"]): t for t in _lire("tableaux")}
    assert {cle: tableaux[cle]["effet"] for cle in DATES_APRES_LE_VERBE} == DATES_APRES_LE_VERBE
    # Aucun autre tableau sans date n'écrit la sienne juste après le verbe.
    import re
    apres = re.compile(r"(?:reclass|int[ée]gr)\w*\s*,?\s+(?:avec\s+effet\s+)?(?:au|[àa]\s+compter\s+du)\s+"
                       + rec._DATE, re.IGNORECASE)
    assert [cle for cle, t in tableaux.items() if not t["effet"] and apres.search(t["intro"])] == []


#: Action 158, B5-bis : les tableaux dont la phrase n'écrit pas la date, et qu'un autre
#: article du même décret date ; chacun lu à l'index LEGI, à la version qui couvre celle
#: du tableau (la citation dans dila_legi_reclassements.DATES_D_UN_AUTRE_ARTICLE et dans
#: docs/feuille_de_route/158/2026-11-05-b5-bis-corrections-de-r-b5.md).
DATES_D_UN_AUTRE_ARTICLE = {
    # n° 98-268, art. 28 : « Les articles 17, 18, 21 et 22 du présent décret prennent
    # effet au 1er août 1995. »
    ("LEGIARTI000006506606", "1"): "1995-08-01",  # n° 98-268, art. 17
    # n° 2001-325, art. 17 : « Les dispositions des articles 1er, 4, 5, 6 du I de
    # l'article 7, des articles 8, 9, 10, 11, 14 et 15 du présent décret prennent effet
    # au 1er janvier 1997. »
    ("LEGIARTI000006567682", "1"): "1997-01-01",  # n° 2001-325, art. 14
    # n° 2017-1367, art. 28 : « […] et les articles 23 à 25 entrent en vigueur le
    # 1er janvier 2017. »
    ("LEGIARTI000035601659", "1"): "2017-01-01",  # n° 2017-1367, art. 23
    # n° 2017-1494, art. 15 : « […] et les dispositions du I de l'article 13 entrent en
    # vigueur le 1er janvier 2017. » Le tableau est dans le I.
    ("LEGIARTI000035900888", "1"): "2017-01-01",  # n° 2017-1494, art. 13
    # n° 98-896, art. 10 (LEGIARTI000006508631, JORFARTI000002486581) : « Les dispositions
    # des articles 1er, 6, 7 et 8 du présent décret sont applicables à compter du 1er août
    # 1996. » Le n° 2002-378, art. 1er (JORFARTI000002416455), ne fait qu'ôter « en
    # fonctions à la date du présent décret » de l'art. 8, sans clause d'effet : le
    # tableau reste celui de 1996 (action 158, B6, relecture R-B6).
    ("LEGIARTI000006508629", "1"): "1996-08-01",  # n° 98-896, art. 8
}


def test_un_tableau_que_date_un_autre_article_de_son_decret_prend_cette_date():
    """Action 158, B5-bis (relecture R-B5). Ces quatre tableaux étaient datés de
    l'entrée en vigueur de leur version (2003-06-21, 2001-04-15, 2017-09-23,
    2017-10-28) ; le décret les fait prendre effet plus tôt. Le n° 98-268, art. 20, reste
    sans date, déclaré : il échelonne l'accès au grade (« au 1er août 1994, au 1er août
    1995, au 1er août 1996 et au 1er janvier 1997 »). L'art. 8 du n° 98-896, récrit par le
    n° 2002-378 sans que son tableau change, prend la date de l'art. 10 (B6)."""
    tableaux = {(t["article"], t["tableau"]): t for t in _lire("tableaux")}
    assert ({cle: tableaux[cle]["effet"] for cle in DATES_D_UN_AUTRE_ARTICLE}
            == DATES_D_UN_AUTRE_ARTICLE)
    assert tableaux[("LEGIARTI000006506612", "1")]["effet"] == ""  # n° 98-268, art. 20
    assert set(rec.DATES_D_UN_AUTRE_ARTICLE) == {article for article, _ in DATES_D_UN_AUTRE_ARTICLE}


#: Action 158, B6 : les tableaux dont la phrase date le reclassement de l'entrée en
#: vigueur de leur décret (« A la date d'entrée en vigueur du présent décret », « à la
#: date d'effet du présent décret »), et la date que le décret fixe lui-même ; chaque
#: clause lue à l'index LEGI (seule version) et au JORF (texte signé), le jour de
#: publication lu au JORF (docs/feuille_de_route/158/2026-11-06-b6-dates-relatives-au-decret.md).
DATES_DU_DECRET = {
    # n° 98-809 (LEGIARTI000006508229) : « Le présent décret prend effet au 1er août 1995,
    # à l'exception des articles 3 et 4. » JO du 12 septembre 1998 ; la date est écrite :
    # 1er août 1995.
    ("LEGIARTI000006508227", "1"): "1995-08-01",  # art. 10
    # n° 2011-964 (LEGIARTI000024477652) : « Le présent décret entre en vigueur le premier
    # jour du mois suivant sa publication. » JO du 18 août 2011 → 1er septembre 2011.
    ("LEGIARTI000024477660", "1"): "2011-09-01",  # art. 21
    ("LEGIARTI000024477662", "1"): "2011-09-01",  # art. 22
    # n° 2011-1140 (LEGIARTI000024581626) : « Le présent décret prend effet à compter du 1er
    # jour du mois qui suit sa publication. » JO du 23 septembre 2011 → 1er octobre 2011. Le
    # décret ne dit qu'une fois quand il s'applique (cet art. 35) et nomme « la date
    # d'entrée en vigueur du présent décret » dans ses art. 21 et 22 : voir PRISES_D_EFFET.
    ("LEGIARTI000024581630", "1"): "2011-10-01",  # art. 21
    ("LEGIARTI000024581632", "1"): "2011-10-01",  # art. 22
    # n° 2011-1642 (LEGIARTI000024847365) : « Le présent décret entre en vigueur le
    # premier jour du mois qui suit celui de sa publication. » JO du 25 novembre 2011 →
    # 1er décembre 2011.
    ("LEGIARTI000024847333", "1"): "2011-12-01",  # art. 18
    ("LEGIARTI000024847335", "1"): "2011-12-01",  # art. 19
    # n° 2011-1987 (LEGIARTI000025072735) : « Les dispositions du présent décret entrent
    # en vigueur le 1er janvier 2012. » JO du 29 décembre 2011 ; la date est écrite : 1er
    # janvier 2012.
    ("LEGIARTI000025072785", "1"): "2012-01-01",  # art. 24
    # n° 2011-1988 (LEGIARTI000025073321) : « Les dispositions du présent décret entrent
    # en vigueur le 1er janvier 2012. » JO du 29 décembre 2011 ; la date est écrite : 1er
    # janvier 2012.
    ("LEGIARTI000025073303", "1"): "2012-01-01",  # art. 22
    # n° 2012-230 (LEGIARTI000025378144) : « Les dispositions du présent décret entrent en
    # vigueur le 1er mars 2012. » JO du 18 février 2012 ; la date est écrite : 1er mars
    # 2012.
    ("LEGIARTI000025378134", "1"): "2012-03-01",  # art. 19
    # n° 2012-379 (LEGIARTI000025546343) : « Le présent décret entre en vigueur le premier
    # jour du mois suivant sa publication au Journal officiel de la République française.
    # » JO du 21 mars 2012 → 1er avril 2012.
    ("LEGIARTI000025546325", "1"): "2012-04-01",  # art. 16
    # n° 2012-924 (LEGIARTI000026237262) : « Le présent décret entre en vigueur le premier
    # jour du mois qui suit celui de sa publication. » JO du 31 juillet 2012 → 1er août
    # 2012.
    ("LEGIARTI000026237250", "1"): "2012-08-01",  # art. 19
    # n° 2012-984 (LEGIARTI000026311285) : « Le présent décret entre en vigueur le premier
    # jour du mois suivant sa publication. » JO du 24 août 2012 → 1er septembre 2012.
    ("LEGIARTI000026311271", "1"): "2012-09-01",  # art. 21
    # n° 2012-1099 (LEGIARTI000026428567) : « Le présent décret entre en vigueur le 1er
    # octobre 2012. » JO du 30 septembre 2012 ; la date est écrite : 1er octobre 2012.
    ("LEGIARTI000026428541", "1"): "2012-10-01",  # art. 16
    # n° 2012-1161 (LEGIARTI000026508387) : « Le présent décret entre en vigueur le
    # premier jour du mois suivant celui de sa publication au Journal officiel de la
    # République française. » JO du 19 octobre 2012 → 1er novembre 2012.
    ("LEGIARTI000026508372", "1"): "2012-11-01",  # art. 35
    # n° 2012-1419 (LEGIARTI000026797414) : « Le présent décret entre en vigueur à compter
    # du premier jour du mois qui suit sa publication. » JO du 20 décembre 2012 → 1er
    # janvier 2013.
    ("LEGIARTI000026797412", "1"): "2013-01-01",  # art. 6
    # n° 2012-1420 (LEGIARTI000026796792) : « Le présent décret entre en vigueur à compter
    # du premier jour du mois qui suit sa publication. » JO du 20 décembre 2012 → 1er
    # janvier 2013.
    ("LEGIARTI000026796776", "1"): "2013-01-01",  # art. 26
    # n° 2013-830 (LEGIARTI000027962726) : « Les dispositions du présent décret entrent en
    # vigueur le premier jour du mois suivant sa publication. » JO du 18 septembre 2013 →
    # 1er octobre 2013.
    ("LEGIARTI000027962708", "1"): "2013-10-01",  # art. 16
    # n° 2014-75 (LEGIARTI000028540391) : « Les dispositions du présent décret entrent en
    # vigueur le premier jour du mois suivant sa publication. » JO du 31 janvier 2014 →
    # 1er février 2014.
    ("LEGIARTI000028540405", "1"): "2014-02-01",  # art. 6
    ("LEGIARTI000028540405", "2"): "2014-02-01",  # art. 6
    # n° 2014-76 (LEGIARTI000028540771) : « Le présent décret entre en vigueur le premier
    # jour du mois suivant sa date de publication. » JO du 31 janvier 2014 → 1er février
    # 2014.
    ("LEGIARTI000028540761", "1"): "2014-02-01",  # art. 8
    ("LEGIARTI000028540763", "1"): "2014-02-01",  # art. 9
    ("LEGIARTI000028540765", "1"): "2014-02-01",  # art. 10
    ("LEGIARTI000028540767", "1"): "2014-02-01",  # art. 11
    # n° 2014-79 (LEGIARTI000028540862) : « Les dispositions du présent décret entrent en
    # vigueur le premier jour du mois suivant sa publication. » JO du 31 janvier 2014 →
    # 1er février 2014.
    ("LEGIARTI000028540858", "1"): "2014-02-01",  # art. 6
    ("LEGIARTI000028540858", "2"): "2014-02-01",  # art. 6
    # n° 2014-81 (LEGIARTI000028541522) : « Les dispositions du présent décret entrent en
    # vigueur le premier jour du mois suivant sa date de publication. » JO du 31 janvier
    # 2014 → 1er février 2014.
    ("LEGIARTI000028541518", "1"): "2014-02-01",  # art. 6
    # n° 2014-922 (LEGIARTI000029384148) : « Le présent décret entre en vigueur le premier
    # jour du mois qui suit sa publication. » JO du 21 août 2014 → 1er septembre 2014.
    ("LEGIARTI000029384142", "1"): "2014-09-01",  # art. 16
    # n° 2014-1164 (LEGIARTI000029563614) : « Le présent décret entre en vigueur le
    # premier jour du mois suivant sa publication au Journal officiel de la République
    # française. » JO du 11 octobre 2014 → 1er novembre 2014.
    ("LEGIARTI000029563606", "1"): "2014-11-01",  # art. 10
    # n° 2015-303 (LEGIARTI000030371580) : « Le présent décret entre en vigueur le premier
    # jour du mois qui suit sa publication. » JO du 19 mars 2015 → 1er avril 2015.
    ("LEGIARTI000030371569", "1"): "2015-04-01",  # art. 24
    # n° 2015-1275 (LEGIARTI000031317655) : « Le présent décret entre en vigueur le
    # premier jour du mois suivant sa publication au Journal officiel de la République
    # française. » JO du 15 octobre 2015 → 1er novembre 2015.
    ("LEGIARTI000031317649", "1"): "2015-11-01",  # art. 35
    # n° 2016-219 (LEGIARTI000032128540) : « Le présent décret entre en vigueur le premier
    # jour du mois suivant celui de sa publication. » JO du 28 février 2016 → 1er mars
    # 2016.
    ("LEGIARTI000032128528", "1"): "2016-03-01",  # art. 6
    ("LEGIARTI000032128530", "1"): "2016-03-01",  # art. 7
    # n° 2016-336 (LEGIARTI000032276866) : « Le présent décret entre en vigueur à compter
    # du premier jour du mois qui suit celui de sa publication. » JO du 22 mars 2016 → 1er
    # avril 2016.
    ("LEGIARTI000032276852", "1"): "2016-04-01",  # art. 27
    # n° 2016-2002 (LEGIARTI000033792205) : « Le présent décret entre en vigueur le 1er
    # janvier 2017. » JO du 31 décembre 2016 ; la date est écrite : 1er janvier 2017.
    ("LEGIARTI000033792187", "1"): "2017-01-01",  # art. 23
    # n° 2017-180 (LEGIARTI000034036522) : « Le présent décret entre en vigueur le 1er
    # janvier 2017. » JO du 15 février 2017 ; la date est écrite : 1er janvier 2017.
    ("LEGIARTI000034036512", "1"): "2017-01-01",  # art. 20
    # n° 2017-233 (LEGIARTI000034082772) : « Le présent décret entre en vigueur le premier
    # jour du mois qui suit celui de sa publication. » JO du 25 février 2017 → 1er mars
    # 2017.
    ("LEGIARTI000034082758", "1"): "2017-03-01",  # art. 17
    # n° 2020-1174 (LEGIARTI000042368622) : « Le présent décret entre en vigueur le
    # premier jour du mois qui suit celui de sa publication. » JO du 27 septembre 2020 →
    # 1er octobre 2020.
    ("LEGIARTI000042368604", "1"): "2020-10-01",  # art. 25
    # n° 2020-1175 (LEGIARTI000042368942) : « Le présent décret entre en vigueur le
    # premier jour du mois qui suit celui de sa publication. » JO du 27 septembre 2020 →
    # 1er octobre 2020.
    ("LEGIARTI000042368924", "1"): "2020-10-01",  # art. 25
    # n° 2021-1818 (LEGIARTI000044804898) : « Les dispositions du présent décret entrent
    # en vigueur le 1er janvier 2022. Elles ne s'appliquent pas aux auxiliaires de
    # puériculture relevant, au 31 décembre 2021, du cadre d'emplois régi par le décret
    # n° 92-865 du 28 août 1992 susvisé ni aux auxiliaires de soins relevant, à la même
    # date, de la spécialité aide-soignant du cadre d'emplois régi par le décret n° 92-866
    # du 28 août 1992 susvisé. » JO du 28 décembre 2021 ; la date est écrite : 1er janvier
    # 2022 ; la seconde phrase écarte des personnes, non des articles.
    ("LEGIARTI000044804888", "1"): "2022-01-01",  # art. 7
    ("LEGIARTI000044804890", "1"): "2022-01-01",  # art. 8
    ("LEGIARTI000044804892", "1"): "2022-01-01",  # art. 9
    # n° 2021-1826 (LEGIARTI000044799842) : « Les dispositions du présent décret entrent
    # en vigueur le 1er janvier 2022. » JO du 28 décembre 2021 ; la date est écrite : 1er
    # janvier 2022.
    ("LEGIARTI000044799836", "1"): "2022-01-01",  # art. 6
    # n° 2021-1834 (LEGIARTI000044804034) : « Les dispositions du présent décret entrent
    # en vigueur le 1er janvier 2022. » JO du 28 décembre 2021 ; la date est écrite : 1er
    # janvier 2022.
    ("LEGIARTI000044804028", "1"): "2022-01-01",  # art. 3
    # n° 2022-516 (LEGIARTI000045540046) : « Les dispositions du présent décret entrent en
    # vigueur le premier jour du mois suivant celui de sa publication. » JO du 10 avril
    # 2022 → 1er mai 2022.
    ("LEGIARTI000045540040", "1"): "2022-05-01",  # art. 4
    # n° 2022-1093 (LEGIARTI000046121303) : « Le présent décret entre en vigueur le
    # premier jour du mois suivant celui de sa publication. » JO du 31 juillet 2022 → 1er
    # août 2022.
    ("LEGIARTI000046121299", "1"): "2022-08-01",  # art. 9
    # n° 2022-1200 (LEGIARTI000046243434) : « Les dispositions du présent décret entrent
    # en vigueur le 1er septembre 2022. » JO du 1er septembre 2022 ; la date est écrite :
    # 1er septembre 2022.
    ("LEGIARTI000046243448", "1"): "2022-09-01",  # art. 6
    ("LEGIARTI000046243452", "1"): "2022-09-01",  # art. 8
    ("LEGIARTI000046243454", "1"): "2022-09-01",  # art. 9
    # n° 2022-1206 (LEGIARTI000046243814) : « Les dispositions du présent décret entrent
    # en vigueur le 1er septembre 2022. » JO du 1er septembre 2022 ; la date est écrite :
    # 1er septembre 2022.
    ("LEGIARTI000046243822", "1"): "2022-09-01",  # art. 4
    ("LEGIARTI000046243824", "1"): "2022-09-01",  # art. 5
    ("LEGIARTI000046243826", "1"): "2022-09-01",  # art. 6
    # n° 2022-1209 (LEGIARTI000046243977) : « Le présent décret entre en vigueur le 1er
    # septembre 2022. » JO du 1er septembre 2022 ; la date est écrite : 1er septembre
    # 2022.
    ("LEGIARTI000046243983", "1"): "2022-09-01",  # art. 2
    # n° 2023-527 (LEGIARTI000047766737) : « Le présent décret entre en vigueur le premier
    # jour du mois qui suit celui de sa publication. » JO du 30 juin 2023 → 1er juillet
    # 2023.
    ("LEGIARTI000047766733", "1"): "2023-07-01",  # art. 10
    # n° 2023-709 (LEGIARTI000047917296) : « Les dispositions du présent décret entrent en
    # vigueur le 1er septembre 2023 à l'exception de celles de l'article 11 qui
    # s'appliquent aux procédures engagées à compter du 1er janvier 2024. » JO du 2 août
    # 2023 ; la date est écrite : 1er septembre 2023.
    ("LEGIARTI000047917292", "1"): "2023-09-01",  # art. 28
    # n° 2023-1092 (LEGIARTI000048461730) : « Le présent décret entre en vigueur le
    # premier jour du mois suivant celui de sa publication. » JO du 26 novembre 2023 → 1er
    # décembre 2023.
    ("LEGIARTI000048461728", "1"): "2023-12-01",  # art. 3
    # n° 2023-1336 (LEGIARTI000048842648) : « Le présent décret entre en vigueur le
    # premier jour du mois suivant celui de sa publication. » JO du 30 décembre 2023 → 1er
    # janvier 2024.
    ("LEGIARTI000048842644", "1"): "2024-01-01",  # art. 9
    # n° 2024-51 (LEGIARTI000049063869) : « Le présent décret entre en vigueur le premier
    # jour du mois suivant celui de sa publication. » JO du 31 janvier 2024 → 1er février
    # 2024.
    ("LEGIARTI000049063861", "1"): "2024-02-01",  # art. 27
    ("LEGIARTI000049063907", "1"): "2024-02-01",  # art. 18
    # n° 2024-282 (LEGIARTI000049350387) : « Le présent décret entre en vigueur le premier
    # jour du mois suivant celui de sa publication. » JO du 30 mars 2024 → 1er avril 2024.
    ("LEGIARTI000049350385", "1"): "2024-04-01",  # art. 9
    # n° 2025-1002 (LEGIARTI000052461403) : « Le présent décret entre en vigueur le
    # premier jour du mois qui suit celui de sa publication. » JO du 30 octobre 2025 → 1er
    # novembre 2025.
    ("LEGIARTI000052461401", "1"): "2025-11-01",  # art. 11
    # n° 2025-1003 (LEGIARTI000052461514) : « Le présent décret entre en vigueur le
    # premier jour du mois qui suit celui de sa publication. » JO du 30 octobre 2025 → 1er
    # novembre 2025.
    ("LEGIARTI000052461512", "1"): "2025-11-01",  # art. 7
    # n° 2025-1327 (LEGIARTI000053186037) : « Le présent décret entre en vigueur le 1 er
    # janvier 2026. » JO du 27 décembre 2025 ; la date est écrite : 1er janvier 2026.
    ("LEGIARTI000053185999", "1"): "2026-01-01",  # art. 31
    ("LEGIARTI000053186007", "1"): "2026-01-01",  # art. 35
    # Action 158, B7 : les tableaux de textes publiés depuis le 1er juin 2004
    # (docs/feuille_de_route/158/2026-11-06-b7-dates-d-apres-juin-2004.md). La règle :
    # code civil, art. 1er (rec.ARTICLE_1ER_DU_CODE_CIVIL) : « à la date qu'ils fixent
    # ou, à défaut, le lendemain de leur publication ».
    # — La date que le décret fixe, sa clause lue à l'index LEGI et au JORF :
    # n° 2005-939, art. 28 : « […] de l'exécution du présent décret, qui prendra effet au
    # 1er janvier 2006 […] » (JO du 6 août 2005) ; voir PRISES_D_EFFET.
    ("LEGIARTI000006413791", "1"): "2006-01-01",  # art. 20
    # n° 2005-1304, art. 43 : « […] qui prendra effet au 1er novembre 2005 […] » (JO du
    # 22 octobre 2005) ; le tableau n'écrit pas la date du reclassement (« qui se
    # trouvent, à la date de publication du présent décret, dans l'une des positions »).
    ("LEGIARTI000006414050", "1"): "2005-11-01",  # art. 36
    # n° 2010-982, art. 39 : « II. - Les dispositions du titre II entrent en vigueur le
    # 1er septembre 2010. » ; l'art. 33 est au titre II (art. 31 à 38, Légifrance) et dit
    # « à la date d'entrée en vigueur du présent titre ».
    ("LEGIARTI000022751573", "1"): "2010-09-01",  # art. 33
    # n° 2010-1719, art. 23, et n° 2010-1720, art. 27 : « […] de l'exécution du présent
    # décret, qui entrera en vigueur au 1er janvier 2011 […] ».
    ("LEGIARTI000023400750", "1"): "2011-01-01",  # n° 2010-1719, art. 14
    ("LEGIARTI000023410135", "1"): "2011-01-01",  # n° 2010-1720, art. 14
    # n° 2011-215, art. 21 : « Les dispositions du présent décret prennent effet le
    # premier jour du mois suivant celui de sa publication. » JO du 27 février 2011 :
    # le mois qui suit février est mars → 1er mars 2011 ; voir PRISES_D_EFFET.
    ("LEGIARTI000023632819", "1"): "2011-03-01",  # art. 13
    # n° 2012-761, art. 17, et n° 2012-762, art. 37 : « […] et entrera en vigueur le
    # premier jour du mois qui suit sa publication. » JO du 10 mai 2012 → 1er juin 2012
    # (le LEGI ouvre les deux versions le 2012-05-11).
    ("LEGIARTI000025855090", "1"): "2012-06-01",  # n° 2012-761, art. 10
    ("LEGIARTI000025855187", "1"): "2012-06-01",  # n° 2012-762, art. 22
    # n° 2012-1002, art. 14 : « […] et entrera en vigueur le premier jour du mois suivant
    # sa publication. » JO du 30 août 2012 → 1er septembre 2012.
    ("LEGIARTI000026327465", "1"): "2012-09-01",  # art. 8
    # n° 2013-176, art. 39, et n° 2013-875, art. 18 : « Les dispositions du présent décret
    # entreront en vigueur le premier jour du mois suivant sa publication au Journal
    # officiel de la République française. » JO du 28 février 2013 → 1er mars 2013 ; JO
    # du 29 septembre 2013 → 1er octobre 2013.
    ("LEGIARTI000027115984", "1"): "2013-03-01",  # n° 2013-176, art. 27
    ("LEGIARTI000027998167", "1"): "2013-10-01",  # n° 2013-875, art. 10
    # n° 2013-974, art. 32 : « Le présent décret entrera en vigueur le premier jour du mois
    # suivant sa publication. » JO du 31 octobre 2013 → 1er novembre 2013.
    ("LEGIARTI000028140216", "1"): "2013-11-01",  # art. 23
    # n° 2016-2008, art. 29 : « Sous réserve des dispositions de l'article 12,le présent
    # décret entre en vigueur le 1er janvier 2017. » ; l'art. 12 n'est pas l'art. 21.
    ("LEGIARTI000033792401", "1"): "2017-01-01",  # art. 21
    # n° 2018-648, art. 8 : « Les dispositions du présent décret entrent en vigueur le 1er
    # janvier 2017, à l'exception de celles des articles 1er, 5 et 6. » ; l'art. 7 n'en est
    # pas (JO du 25 juillet 2018 : un effet antérieur à la publication).
    ("LEGIARTI000037246483", "1"): "2017-01-01",  # art. 7
    # — La clause lue à Légifrance (article absent des deux index) :
    # n° 2012-1139, art. 68 : « Les dispositions du présent décret entrent en vigueur le
    # premier jour du mois suivant celui de sa publication au Journal officiel de la
    # République française. » JO du 11 octobre 2012 → 1er novembre 2012.
    ("LEGIARTI000026477976", "1"): "2012-11-01",  # art. 50
    # n° 2015-363, art. 14 : « Le présent décret entre en vigueur le premier jour du mois
    # qui suit sa publication. » JO du 31 mars 2015 → 1er avril 2015.
    ("LEGIARTI000030420449", "1"): "2015-04-01",  # art. 12
    ("LEGIARTI000030420449", "2"): "2015-04-01",
    # — Aucune clause : le lendemain du JO (date lue au JORF, champ DATE_PUBLI).
    ("LEGIARTI000006264680", "1"): "2007-05-14",  # n° 2007-835, art. 4 ; JO du 13 mai 2007
    ("LEGIARTI000022338220", "1"): "2010-06-14",  # n° 2010-647, art. 12 ; JO du 13 juin 2010
    ("LEGIARTI000023947863", "1"): "2011-05-06",  # n° 2011-489, art. 24 ; JO du 5 mai 2011
    ("LEGIARTI000024272771", "1"): "2011-06-30",  # n° 2011-744, art. 11 ; JO du 29 juin 2011
    ("LEGIARTI000024272771", "2"): "2011-06-30",
    ("LEGIARTI000024581275", "1"): "2011-09-24",  # n° 2011-1139, art. 18 ; JO du 23 sept. 2011
    ("LEGIARTI000024581277", "1"): "2011-09-24",  # n° 2011-1139, art. 19
    ("LEGIARTI000025196191", "1"): "2012-01-26",  # n° 2012-78, art. 11 ; JO du 25 janv. 2012
    ("LEGIARTI000025196191", "2"): "2012-01-26",
    ("LEGIARTI000025377504", "1"): "2012-02-19",  # n° 2012-229, art. 18 ; JO du 18 févr. 2012
    ("LEGIARTI000027535136", "1"): "2013-06-13",  # n° 2013-489, art. 23 ; JO du 12 juin 2013
    ("LEGIARTI000028342387", "1"): "2013-12-20",  # n° 2013-1173, art. 17 ; JO du 19 déc. 2013
    ("LEGIARTI000028540018", "1"): "2014-02-01",  # n° 2014-71, art. 12 ; JO du 31 janv. 2014
    ("LEGIARTI000028540020", "1"): "2014-02-01",  # n° 2014-71, art. 13
    ("LEGIARTI000031826959", "1"): "2015-12-31",  # n° 2015-1792, art. 11 ; JO du 30 déc. 2015
    ("LEGIARTI000033078337", "1"): "2016-09-01",  # n° 2016-1177, art. 22 ; JO du 31 août 2016
    ("LEGIARTI000039363229", "1"): "2019-11-11",  # n° 2019-1160, art. 5 ; JO du 10 nov. 2019
}

#: Action 158, B7 : les tableaux que le texte ne date pas d'une seule lecture ; effet
#: reste vide, et la note de B7 cite les deux lectures. « A compter de la date de
#: publication du présent décret » (n° 2005-1132, art. 18, JO du 10 septembre 2005) et « à
#: la date de publication du présent décret » (n° 2006-8, art. 32 et 33, JO du 5 janvier
#: 2006), quand aucun de ces décrets ne fixe son entrée en vigueur : le jour du JO, ou le
#: lendemain. n° 2010-989, art. 26 (« A la date d'entrée en vigueur du présent décret »),
#: au chapitre III, quand l'art. 36 date les chapitres Ier et III du 1er septembre 2010 et
#: le chapitre II du 1er janvier 2011. n° 2010-302, art. 9 : « A la date d'entrée en
#: vigueur du décret portant inscription de leur corps au sein de l'annexe du présent
#: décret […] », une date par corps, qu'un autre décret fixe.
#: B7 : la ligne de tableaux.csv du n° 2004-1439, art. 23 (version du 2023-08-01), joint la
#: phrase du I (« A la date de l'entrée en vigueur du décret n° 2023-676 ») au tableau du II
#: (« II.-Au 1er janvier 2024, les brigadiers-chefs de classe normale, les brigadiers-chefs
#: de classe supérieure et les majors sont reclassés ») : effet reste vide, à relire.
A_RELIRE = {("LEGIARTI000047908641", "1")}

NON_TRANCHES = {
    ("LEGIARTI000006413884", "1"), ("LEGIARTI000006413884", "2"),
    ("LEGIARTI000006413884", "3"),                       # n° 2005-1132, art. 18
    ("LEGIARTI000006414364", "1"), ("LEGIARTI000006414365", "1"),  # n° 2006-8, art. 32, 33
    ("LEGIARTI000022755950", "1"),                       # n° 2010-989, art. 26
    ("LEGIARTI000022007850", "1"),                       # n° 2010-302, art. 9
}


def test_un_tableau_date_de_l_entree_en_vigueur_de_son_decret_prend_la_date_qu_il_fixe():
    """Action 158, B6. Ces tableaux étaient datés de l'entrée en vigueur de leur version
    au LEGI, qui s'écarte parfois du texte : le n° 2012-379 (2012-03-22, pour le 1er avril
    2012), le n° 2022-1200 (2022-09-02), le n° 2025-1327 (2025-12-28, pour le 1er janvier
    2026), le n° 2017-180 (2017-02-16, pour le 1er janvier 2017). Le n° 2011-1140, dont le
    tableau dit « date d'entrée en vigueur » quand le décret dit « prend effet à compter du
    1er jour du mois qui suit sa publication », prend le 1er octobre 2011 (relecture R-B7,
    écart 2 ; B6-bis)."""
    tableaux = {(t["article"], t["tableau"]): t for t in _lire("tableaux")}
    assert {cle: tableaux[cle]["effet"] for cle in DATES_DU_DECRET} == DATES_DU_DECRET
    assert set(rec.DATES_DU_DECRET) == {article for article, _ in DATES_DU_DECRET}


def test_un_tableau_que_le_texte_ne_date_pas_d_une_seule_lecture_reste_sans_effet():
    """Action 158, B7 : les sept tableaux de NON_TRANCHES gardent effet vide, et le script
    les nomme, avec leurs deux lectures."""
    tableaux = {(t["article"], t["tableau"]): t for t in _lire("tableaux")}
    assert {cle: tableaux[cle]["effet"] for cle in NON_TRANCHES} == dict.fromkeys(NON_TRANCHES, "")
    assert set(rec.NON_TRANCHES) == {article for article, _ in NON_TRANCHES}
    assert not set(rec.NON_TRANCHES) & set(rec.DATES_DU_DECRET)
    # Le tableau mal découpé : la phrase dit le I, les lignes sont celles du II.
    assert {cle: tableaux[cle]["effet"] for cle in A_RELIRE} == dict.fromkeys(A_RELIRE, "")
    assert set(rec.A_RELIRE) == {article for article, _ in A_RELIRE}
    assert not set(rec.A_RELIRE) & set(rec.DATES_DU_DECRET)
    intro = tableaux[("LEGIARTI000047908641", "1")]["intro"]
    assert intro.startswith("I.-A la date de l'entrée en vigueur du décret n° 2023-676")
    assert ("II.-Au 1er janvier 2024, les brigadiers-chefs de classe normale, les "
            "brigadiers-chefs de classe supérieure et les majors sont reclassés") in intro
    groupes = {l["groupe"] for l in _lire("lignes") if l["article"] == "LEGIARTI000047908641"}
    assert "Major de police Major de police" in groupes


#: Code civil, art. 1er, dans sa rédaction issue de l'ordonnance n° 2004-164 du 20 février
#: 2004, art. 1er (JORF du 21 février 2004), « En vigueur depuis le 01 juin 2004 » : lu à
#: Légifrance le 6 novembre 2026 (LEGIARTI000006419280 ; l'article n'est dans aucun des deux
#: index du dépôt, filtrés sur le champ social).
ARTICLE_1ER = ("Les lois et, lorsqu'ils sont publiés au Journal officiel de la République "
               "française, les actes administratifs entrent en vigueur à la date qu'ils fixent "
               "ou, à défaut, le lendemain de leur publication. Toutefois, l'entrée en vigueur "
               "de celles de leurs dispositions dont l'exécution nécessite des mesures "
               "d'application est reportée à la date d'entrée en vigueur de ces mesures. "
               "En cas d'urgence, entrent en vigueur dès leur publication les lois dont le "
               "décret de promulgation le prescrit et les actes administratifs pour lesquels le "
               "Gouvernement l'ordonne par une disposition spéciale. "
               "Les dispositions du présent article ne sont pas applicables aux actes "
               "individuels.")


def test_l_entete_cite_l_article_1er_du_code_civil_et_les_tableaux_non_tranches():
    """Action 158, B7 : la règle d'entrée en vigueur d'un texte publié depuis le 1er juin
    2004, citée entière, une fois, à l'en-tête de tableaux.csv ; et les tableaux que le
    texte ne date pas d'une seule lecture."""
    assert rec.ARTICLE_1ER_DU_CODE_CIVIL == ARTICLE_1ER
    chemin = RACINE / "data" / "reference" / "grilles" / "reclassements" / "tableaux.csv"
    entete = chemin.read_text(encoding="utf-8").split("\n")[0]
    assert entete.count(ARTICLE_1ER) == 1
    for dit in ("code civil, art. 1er", "ordonnance n° 2004-164", "1er juin 2004",
                "LEGIARTI000006419280", "n° 2005-1132, art. 18", "n° 2006-8, art. 32 et 33",
                "n° 2010-989, art. 26", "n° 2010-302, art. 9", "effet vide",
                "n° 2004-1439, art. 23 (version du 2023-08-01)", "à relire"):
        assert dit in entete, dit


#: Les décrets dont la clause dit « prend effet à compter du 1er jour du mois qui suit sa
#: publication » quand leurs tableaux disent « la date d'entrée en vigueur du présent
#: décret » : n° 2011-1140, art. 35 (LEGIARTI000024581626), art. 21 et 22 ; les art. 25 et 26
#: disent « la date de publication du présent décret », deux dates que le décret distingue.
PRISES_D_EFFET = {"2011-1140",
                  # B7 : n° 2011-215, art. 21 (« prennent effet le premier jour du mois
                  # suivant celui de sa publication »), art. 13 ; n° 2005-939, art. 28
                  # (« qui prendra effet au 1er janvier 2006 »), art. 20 ; n° 2005-1304,
                  # art. 43 (« qui prendra effet au 1er novembre 2005 »), art. 36, dont la
                  # phrase n'écrit pas la date du reclassement (SANS_DATE_ECRITE).
                  "2011-215", "2005-939", "2005-1304"}

#: Le tableau dont la phrase n'écrit pas la date du reclassement, seulement celle d'une
#: condition (B7) : il vaut quand son décret s'applique, à la date que ce décret fixe.
SANS_DATE_ECRITE = {"LEGIARTI000006414050": "qui se trouvent, à la date de publication du "
                                            "présent décret, dans l'une des positions"}

#: L'article d'un décret publié au JO que l'index n'a pas (filtre thématique), lu à
#: Légifrance le 6 novembre 2026 (B7) : n° 2014-71, art. 3 (lu sur la page du texte au
#: JORF, JORFTEXT000028539091), 8 (page de l'article, JORFARTI000028539120), 14
#: (JORFARTI000028539137) et 15 (JORFARTI000028539142).
LUS_A_LEGIFRANCE = {
    ("2014-71", "3"): "A l'article 3-1 du décret n° 2006-227 du 24 février 2006 susvisé, les "
                      "mots : « du troisième alinéa de l'article 1er, du II et du III de "
                      "l'article 2 » sont remplacés par les mots : « du troisième alinéa du II "
                      "de l'article 1er, du III de l'article 2 ».",
    ("2014-71", "8"): "Les fonctionnaires inscrits sur un tableau d'avancement établi au titre "
                      "de l'année 2014, promus dans l'un des grades d'avancement d'un corps régi "
                      "par le décret n° 2006-227 du 24 février 2006 susvisé, postérieurement à la "
                      "date d'entrée en vigueur du présent décret, sont classés dans le grade "
                      "d'avancement en tenant compte de la situation qui aurait été la leur "
                      "s'ils avaient poursuivi, jusqu'à la date de leur promotion, leur carrière "
                      "et avaient été classés dans ce grade selon les dispositions applicables "
                      "avant l'entrée en vigueur du présent décret, puis reclassés à la date de "
                      "leur promotion dans les conditions fixées par les tableaux correspondant "
                      "à leur grade, figurant sous l'un des articles 5, 6 ou 7 du présent "
                      "décret.",
    ("2014-71", "14"): "I. ― Les agents inscrits sur un tableau d'avancement établis au titre de "
                       "l'année 2014, promus dans l'un des grades d'avancement d'un corps régi "
                       "par le décret du 14 juin 2011 susvisé postérieurement à la date "
                       "d'entrée en vigueur du présent décret, sont classés dans le grade "
                       "d'avancement en tenant compte de la situation qui aurait été la leur "
                       "s'ils n'avaient cessé de relever, jusqu'à la date de leur promotion, "
                       "des dispositions du chapitre IV du décret du 14 juin 2011 précité, dans "
                       "sa rédaction antérieure au présent décret, puis s'ils avaient été "
                       "reclassés, à la date de leur promotion, en application des dispositions "
                       "des articles 12 et 13 du présent décret. II. ― Les lauréats des examens "
                       "professionnels d'accès aux grades d'avancement des corps régis par le "
                       "décret du 14 juin 2011 susvisé, dont les arrêtés d'ouverture ont été "
                       "publiés avant la date d'entrée en vigueur du présent décret, sont "
                       "classés dans le grade d'avancement en tenant compte de la situation qui "
                       "aurait été la leur s'ils n'avaient cessé de relever, jusqu'à la date de "
                       "leur promotion, des dispositions du chapitre IV du décret du 14 juin "
                       "2011 précité, dans sa rédaction antérieure au présent décret, puis s'ils "
                       "avaient été reclassés, à la date de leur promotion, en application des "
                       "dispositions des articles 12 et 13.",
    ("2014-71", "15"): "Le ministre de l'économie et des finances, la ministre des affaires "
                       "sociales et de la santé, la ministre de la réforme de l'Etat, de la "
                       "décentralisation et de la fonction publique et le ministre délégué "
                       "auprès du ministre de l'économie et des finances, chargé du budget, sont "
                       "chargés, chacun en ce qui le concerne, de l'exécution du présent décret, "
                       "qui sera publié au Journal officiel de la République française.",
}

#: Une clause qui dit quand un texte, ou une partie, s'applique : le verbe conjugué
#: (non « la date d'entrée en vigueur »), après le texte ou ses dispositions ; l'effet
#: rétroactif ; l'urgence (code civil, art. 1er, deuxième alinéa) (B7).
CLAUSE = re.compile(
    r"(?:pr[ée]sent\s+(?:d[ée]cret|titre|chapitre)|dispositions|articles?\s+\d)[^.]{0,160}?"
    r"\b(?:entr(?:e|ent|era|eront)\s+en\s+vigueur|pren(?:d|nent|dra|dront)\s+effet"
    r"|produi\w*\s+(?:leurs?\s+|ses\s+)?effets?"
    r"|(?:sont|est|seront|sera)\s+applicables?\s+(?:[àa]\s+compter|[àa]\s+partir|au\b|le\b))"
    r"|r[ée]troacti|\burgence\b", re.IGNORECASE)

def test_l_entete_dit_les_effets_anterieurs_a_la_publication_et_l_elargissement_de_2002():
    """Relecture R-B7, écarts 4 et 6. Trois des dates que B6 donne précèdent la publication
    de leur décret, et le texte les date ainsi : n° 98-809 (art. 12 : « prend effet au 1er
    août 1995 », JO du 12 septembre 1998, JORFTEXT000000194869) ; n° 98-896 (art. 10 :
    « applicables à compter du 1er août 1996 », JO du 9 octobre 1998, JORFTEXT000000573079) ;
    n° 2017-180 (art. 25 : « entre en vigueur le 1er janvier 2017 », JO du 15 février 2017,
    JORFTEXT000034035533). L'en-tête de tableaux.csv les dit, et dit que l'élargissement du
    n° 2002-378 (JO du 21 mars 2002, JORFTEXT000000586605) n'est pas dans la donnée."""
    anterieurs = {numero for numero, (jour, _, _, publication, _) in rec.ENTREES_EN_VIGUEUR.items()
                  if jour < publication}
    # B7 : n° 2018-648, art. 8 (« entrent en vigueur le 1er janvier 2017, à l'exception de
    # celles des articles 1er, 5 et 6 »), JO du 25 juillet 2018 (JORFTEXT000037245707).
    assert anterieurs == {"98-809", "2017-180", "2018-648"}
    assert all(jour > publication for jour, _, _, publication, _
               in rec.ENTREES_LUES_A_LEGIFRANCE.values())
    assert all(jour > publication for jour, _, publication
               in rec.LENDEMAINS_DE_PUBLICATION.values())
    assert rec.DATES_D_UN_AUTRE_ARTICLE["LEGIARTI000006508629"][0] < "1998-10-09"
    chemin = RACINE / "data" / "reference" / "grilles" / "reclassements" / "tableaux.csv"
    entete = chemin.read_text(encoding="utf-8").split("\n")[0]
    assert entete == f"# {rec.ENTETES['tableaux']}"
    for dit in ("Quatre effets précèdent la publication",
                "n° 98-809 (1er août 1995, JO du 12 septembre 1998)",
                "n° 98-896 (1er août 1996, JO du 9 octobre 1998)",
                "n° 2017-180 (1er janvier 2017, JO du 15 février 2017)",
                "n° 2018-648 (1er janvier 2017, JO du 25 juillet 2018)",
                "« en fonctions à la date du présent décret »",
                "n° 2002-378 (JO du 21 mars 2002)", "pas dans la donnée"):
        assert dit in entete, dit


INDEX_LEGI = RACINE / "data" / "brut" / "dila" / "legi.sqlite"
INDEX_JORF = RACINE / "data" / "brut" / "dila" / "jorf.sqlite"


def _plat(texte: str) -> str:
    return re.sub(r"\s+", " ", texte.replace("\u00a0", " ").replace("’", "'")).strip()


def _est_l_article(citation: str, texte: str, jorf: bool = False) -> bool:
    """La citation de la clause est l'article entier (espaces normalisés) ; au JORF, avec
    « Art. 12. - » devant (relecture R-B7, écart 1), ou la formule de signature après
    (« Fait le 30 décembre 2010. », n° 2010-1719 et 2010-1720, B7)."""
    devant = r"(?:Art\. \S+ - )?" if jorf else ""
    apres = r"(?: Fait le (?:1er|\d{1,2}) \w+ \d{4}\.)?" if jorf else ""
    return re.fullmatch(devant + re.escape(_plat(citation)) + apres, _plat(texte)) is not None


def _est_de_phrases_entieres(citation: str, texte: str) -> bool:
    """La citation d'une phrase d'un article qui en compte d'autres est faite de phrases
    entières de cet article, du premier mot de la première au point de la dernière."""
    citation, texte = _plat(citation), _plat(texte)
    debut = texte.find(citation)
    if debut < 0 or not citation.endswith("."):
        return False
    fin = debut + len(citation)
    return (debut == 0 or texte[:debut].endswith(". ")) and (fin == len(texte)
                                                            or texte[fin] == " ")


def _dates_ecrites(citation: str) -> set[str]:
    return {date(int(t.group("annee")), rec.MOIS[rec._sans_accents(t.group("mois")).lower()],
                 1 if re.match(r"1\s*er", t.group("jour")) else int(t.group("jour"))).isoformat()
            for t in re.finditer(rec._DATE, citation, re.IGNORECASE)}


def test_la_garde_des_citations_refuse_une_citation_tronquee():
    """Relecture R-B7, écart 1 : B6 citait du n° 2021-1818 sa seule première phrase, et la
    garde (« la citation est dans l'article ») la laissait passer. Les textes sont ceux de
    l'index, lus le 6 novembre 2026 : l'art. 12 du n° 2021-1818 (LEGIARTI000044804898 ;
    JORFARTI000044571768), deux phrases ; l'art. 12 du n° 98-809 (LEGIARTI000006508229),
    que le JORF fait précéder de « Art. 12. - »."""
    entier = ("Les dispositions du présent décret entrent en vigueur le 1er janvier 2022. "
              "Elles ne s'appliquent pas aux auxiliaires de puériculture relevant, au 31 "
              "décembre 2021, du cadre d'emplois régi par le décret n° 92-865 du 28 août 1992 "
              "susvisé ni aux auxiliaires de soins relevant, à la même date, de la spécialité "
              "aide-soignant du cadre d'emplois régi par le décret n° 92-866 du 28 août 1992 "
              "susvisé.")
    assert _est_l_article(entier, entier)
    assert _est_l_article(entier.replace(" ", "  ", 3), entier)  # espaces normalisés
    assert _est_l_article(entier, "Art. 12. - " + entier, jorf=True)
    assert not _est_l_article(entier, "Art. 12. - " + entier)  # hors JORF, rien devant
    premiere = entier.split(". ")[0] + "."
    for coupee in (premiere,                              # la première phrase seule
                   premiere[:-1],                         # sans son point
                   entier.split(". ", 1)[1],              # la seconde seule
                   entier[:-len(" susvisé.")],            # sans ses derniers mots
                   entier.replace("Les dispositions du ", "")):  # sans son début
        assert not _est_l_article(coupee, entier), coupee
        assert not _est_l_article(coupee, "Art. 12. - " + entier, jorf=True), coupee
    # B7 : au JORF seulement, la formule de signature peut suivre l'article ; elle ne
    # couvre pas une citation coupée.
    signe = entier + " Fait le 30 décembre 2010."
    assert _est_l_article(entier, signe, jorf=True)
    assert not _est_l_article(entier, signe)
    assert not _est_l_article(premiere, signe, jorf=True)
    assert not _est_l_article(entier, entier + " Fait à Paris.", jorf=True)
    clause = "Le présent décret prend effet au 1er août 1995, à l'exception des articles 3 et 4."
    assert _est_l_article(clause, clause)
    assert _est_l_article(clause, "Art. 12. - " + clause, jorf=True)
    assert not _est_l_article("Le présent décret prend effet au 1er août 1995.", clause)


def test_la_garde_d_un_autre_article_refuse_une_phrase_coupee():
    """Même relecture : la clause qu'un autre article donne est une ou plusieurs phrases
    entières de cet article (le texte ci-dessous : LEGIARTI000006506628, lu à l'index)."""
    deux = ("Les articles 17, 18, 21 et 22 du présent décret prennent effet au 1er août 1995. "
            "Les articles 19 et 20 prennent effet au 1er août 1994.")
    premiere, seconde = deux.split(". ")[0] + ".", deux.split(". ", 1)[1]
    for juste in (premiere, seconde, deux):
        assert _est_de_phrases_entieres(juste, deux), juste
    for coupee in (premiere[:-1],                          # sans son point
                   premiere[:-len(" 1995.")],              # coupée avant la date
                   "du présent décret prennent effet au 1er août 1995.",  # sans son début
                   "Les articles 19 et 20 prennent effet au 1er août 1994"):
        assert not _est_de_phrases_entieres(coupee, deux), coupee


@pytest.mark.skipif(not (INDEX_LEGI.exists() and INDEX_JORF.exists()),
                    reason="index DILA absent : python scripts/fetch/dila_index.py legi|jorf --recuperer")
def test_chaque_date_lue_a_la_main_est_citee_mot_pour_mot_dans_son_texte():
    """Relecture R-B6, point 4 : les citations de DATES_D_UN_AUTRE_ARTICLE et
    d'ENTREES_EN_VIGUEUR confrontées au texte. Chaque citation est dans l'article qu'elle
    nomme, au LEGI, du même décret que le tableau, et la date en est tirée : écrite dans la
    citation, ou « le premier jour du mois suivant » le jour de publication, lu au JORF, où
    la clause est aussi, au texte signé. La phrase du tableau dit le mot de la clause :
    « entrée en vigueur » pour « entre en vigueur », « effet » pour « prend effet »."""
    legi = sqlite3.connect(f"file:{INDEX_LEGI}?mode=ro", uri=True)
    jorf = sqlite3.connect(f"file:{INDEX_JORF}?mode=ro", uri=True)

    def article(ident: str) -> tuple[str, str]:
        trouve = legi.execute("select titre, texte from doc where id = ?", (ident,)).fetchone()
        assert trouve, ident
        return trouve[0], _plat(trouve[1])

    for tableau, (jour, effet, citation) in rec.DATES_D_UN_AUTRE_ARTICLE.items():
        titre, texte = article(effet)
        assert titre == article(tableau)[0], tableau
        assert _est_de_phrases_entieres(citation, texte), tableau
        assert jour in _dates_ecrites(citation), tableau
    for numero, (jour, effet, jorftexte, publication, citation) in rec.ENTREES_EN_VIGUEUR.items():
        titre, texte = article(effet)
        assert re.match(rf"D[ée]cret n\s*°\s*{re.escape(numero)} du ", titre), numero
        assert _est_l_article(citation, texte), numero
        signe = jorf.execute("select date, titre from doc where id = ?", (jorftexte,)).fetchone()
        assert signe and signe[0] == publication and numero in signe[1], numero
        articles = jorf.execute("select texte from doc where nature like 'Article%' and date = ?"
                                " and titre like ?", (publication, f"%{numero} %")).fetchall()
        assert any(_est_l_article(citation, t, jorf=True) for (t,) in articles), numero
        if re.search(r"premier jour du mois|1er jour du mois", citation):
            p = date.fromisoformat(publication)
            assert jour == date(p.year + (p.month == 12), p.month % 12 + 1, 1).isoformat(), numero
        else:
            assert jour in _dates_ecrites(citation), numero
    def seule_clause(numero: str, titre: str, clause: str) -> list[str]:
        """Les autres articles du décret, au LEGI et au JORF, qui disent quand il s'applique
        (relecture R-B7, écart 2 ; B7 : le JORF aussi, et le verbe à tout temps). Au LEGI, les
        versions ouvertes au plus tard à la date retenue : les suivantes viennent d'autres
        décrets, dont le LEGI note la date (« Conformément à l'article 12 du décret n° 2023-527
        du 29 juin 2023, ces dispositions entrent en vigueur le 1er juillet 2023 »)."""
        jour, _, _, publication, citation = rec.ENTREES_EN_VIGUEUR[numero]
        autres = [i for (i, t) in legi.execute(
            "select id, texte from doc where nature like 'Article%' and titre = ? and date <= ?",
            (titre, jour)) if i != clause and CLAUSE.search(_plat(t))]
        autres += [i for (i, t) in jorf.execute(
            "select id, texte from doc where nature like 'Article%' and date = ? and titre like ?",
            (publication, f"%{numero} %"))
            if not _est_l_article(citation, t, jorf=True) and CLAUSE.search(_plat(t))]
        return autres

    for tableau, numero in rec.DATES_DU_DECRET.items():
        titre, texte = article(tableau)
        if numero in rec.LENDEMAINS_DE_PUBLICATION or numero in rec.ENTREES_LUES_A_LEGIFRANCE:
            # Le texte au JORF et l'absence de clause : test_un_decret_sans_clause_… et
            # test_une_clause_lue_a_legifrance_… ; ici, la phrase du tableau.
            assert re.match(rf"D[ée]cret n\s*°\s*{re.escape(numero)} du ", titre), tableau
            assert "date d'entrée en vigueur du présent décret" in texte or (
                "date de publication du présent décret" in texte
                and "en fonctions à la date de publication du présent décret" in texte), tableau
            continue
        citation = rec.ENTREES_EN_VIGUEUR[numero][4]
        assert titre == article(rec.ENTREES_EN_VIGUEUR[numero][1])[0], tableau
        if "date d'effet du présent décret" in texte:
            assert "prend effet" in citation, tableau
        elif "date d'entrée en vigueur du présent titre" in texte:
            # B7 : n° 2010-982, art. 33, au titre II (art. 31 à 38, table des matières du
            # texte au JORF, Légifrance) ; la clause date chaque titre.
            assert numero == "2010-982" and tableau == "LEGIARTI000022751573", tableau
            assert ("Les dispositions du titre II entrent en vigueur le 1er septembre 2010."
                    in citation), tableau
        elif tableau in SANS_DATE_ECRITE:
            # La phrase ne date qu'une condition ; la seule clause du décret le date (B7).
            assert SANS_DATE_ECRITE[tableau] in texte, tableau
            assert numero in PRISES_D_EFFET and re.search(r"pren\w* effet", citation), tableau
            autres = seule_clause(numero, titre, rec.ENTREES_EN_VIGUEUR[numero][1])
            assert not autres, (tableau, autres)
        else:
            assert "date d'entrée en vigueur du présent décret" in texte, tableau
            if numero in PRISES_D_EFFET:
                # Le tableau dit l'entrée en vigueur, la clause « prend effet » : l'équivalence
                # ne vaut que si cette clause est la seule du décret qui dise quand il
                # s'applique (relecture R-B7, écart 2).
                assert re.search(r"pren\w* effet", citation), tableau
                autres = seule_clause(numero, titre, rec.ENTREES_EN_VIGUEUR[numero][1])
                assert not autres, (tableau, autres)
            else:
                assert "en vigueur" in citation, tableau


#: Les décrets sans clause d'entrée en vigueur (B7) : le lendemain du JO (code civil,
#: art. 1er). Le jour du JO est lu au JORF (DATE_PUBLI du texte signé) ; calcul à la main.
LENDEMAINS = {
    "2007-835": ("2007-05-14", "2007-05-13"), "2010-647": ("2010-06-14", "2010-06-13"),
    "2011-489": ("2011-05-06", "2011-05-05"), "2011-744": ("2011-06-30", "2011-06-29"),
    "2011-1139": ("2011-09-24", "2011-09-23"), "2012-78": ("2012-01-26", "2012-01-25"),
    "2012-229": ("2012-02-19", "2012-02-18"), "2013-489": ("2013-06-13", "2013-06-12"),
    "2013-1173": ("2013-12-20", "2013-12-19"), "2014-71": ("2014-02-01", "2014-01-31"),
    "2015-1792": ("2015-12-31", "2015-12-30"), "2016-1177": ("2016-09-01", "2016-08-31"),
    "2019-1160": ("2019-11-11", "2019-11-10"),
}


@pytest.mark.skipif(not (INDEX_LEGI.exists() and INDEX_JORF.exists()),
                    reason="index DILA absent : python scripts/fetch/dila_index.py legi|jorf --recuperer")
def test_un_decret_sans_clause_entre_en_vigueur_le_lendemain_de_sa_publication():
    """Action 158, B7. Chaque décret de LENDEMAINS_DE_PUBLICATION est lu en entier : tous ses
    articles, du 1er à celui qui le charge d'exécution, au JORF (à l'index, ou à Légifrance
    pour ceux que l'index n'a pas, LUS_A_LEGIFRANCE), et ceux du LEGI ; aucun ne dit quand il
    s'applique (CLAUSE). Il entre donc en vigueur le lendemain de sa publication."""
    legi = sqlite3.connect(f"file:{INDEX_LEGI}?mode=ro", uri=True)
    jorf = sqlite3.connect(f"file:{INDEX_JORF}?mode=ro", uri=True)
    assert {n: (j, p) for n, (j, _, p) in rec.LENDEMAINS_DE_PUBLICATION.items()} == LENDEMAINS
    for numero, (jour, jorftexte, publication) in rec.LENDEMAINS_DE_PUBLICATION.items():
        p = date.fromisoformat(publication)
        assert jour == date.fromordinal(p.toordinal() + 1).isoformat(), numero
        signe = jorf.execute("select date, titre from doc where id = ?", (jorftexte,)).fetchone()
        assert signe and signe[0] == publication, numero
        assert re.match(rf"D[ée]cret n\s*°\s*{re.escape(numero)} du ", signe[1]), numero
        articles = {(n or "").replace("er", ""): _plat(t) for n, t in jorf.execute(
            "select num, texte from doc where nature like 'Article%' and date = ? and titre like ?",
            (publication, f"%{numero} %"))}
        articles.update({n: _plat(t) for (d, n), t in LUS_A_LEGIFRANCE.items() if d == numero})
        dernier = max(int(n) for n in articles)
        assert set(articles) == {str(k) for k in range(1, dernier + 1)}, numero
        # « de l'exécution du présent, qui sera publié » : le n° 2013-489 au JORF
        # (JORFARTI000027534187), où le mot « décret » manque.
        assert re.search(r"chargés?,? chacun en ce qui le concerne,? de l'exécution du présent"
                         r"(?: décret)?,", articles[str(dernier)]), numero
        for n, texte in articles.items():
            assert not CLAUSE.search(texte), (numero, n)
        titres = {t for (t,) in legi.execute(
            "select distinct titre from doc where nature like 'Article%' and id in "
            f"({','.join('?' * len(rec.DATES_DU_DECRET))})", list(rec.DATES_DU_DECRET))
            if re.match(rf"D[ée]cret n\s*°\s*{re.escape(numero)} du ", t)}
        assert len(titres) == 1, numero
        # Au LEGI, les versions ouvertes au plus tard le lendemain (voir seule_clause).
        for i, texte in legi.execute("select id, texte from doc where nature like 'Article%' "
                                     "and titre = ? and date <= ?", (titres.pop(), jour)):
            assert not CLAUSE.search(_plat(texte)), (numero, i)


def test_la_clause_reconnait_ce_qui_date_un_texte_et_non_le_reste():
    """B7 : CLAUSE trouve chaque clause relevée (citations d'ENTREES_EN_VIGUEUR, de
    DATES_D_UN_AUTRE_ARTICLE, d'ENTREES_LUES_A_LEGIFRANCE), et ne prend ni « la date d'entrée
    en vigueur du présent décret », ni la titularisation qui « prend effet » (n° 2016-1177,
    art. 7, JORFARTI000033076708), ni les concours auxquels un article est « applicable »."""
    for _, _, _, _, citation in rec.ENTREES_EN_VIGUEUR.values():
        assert CLAUSE.search(citation), citation
    for _, _, citation in rec.DATES_D_UN_AUTRE_ARTICLE.values():
        assert CLAUSE.search(citation), citation
    for _, _, _, _, citation in rec.ENTREES_LUES_A_LEGIFRANCE.values():
        assert CLAUSE.search(citation), citation
    for neutre in ("A la date d'entrée en vigueur du présent décret, les techniciens sont "
                   "reclassés conformément au tableau suivant :",
                   "Toutefois, la titularisation prend effet à la date prévue de fin de stage "
                   "compte non tenu de la prolongation de celui-ci.",
                   "Les dispositions des articles 5 et 8 du décret du 11 novembre 2009 susvisé "
                   "sont applicables aux concours mentionnés aux 1°, 2° et 3° du I."):
        assert not CLAUSE.search(neutre), neutre


#: Les clauses lues à Légifrance (B7), page de l'article au JORF, le 6 novembre 2026 : ni
#: l'index LEGI ni l'index JORF ne les ont (filtre thématique).
LUES_A_LEGIFRANCE_CLAUSES = {
    "2012-1139": ("2012-11-01", "JORFARTI000026477172", "JORFTEXT000026477051", "2012-10-11",
                  "Les dispositions du présent décret entrent en vigueur le premier jour du mois "
                  "suivant celui de sa publication au Journal officiel de la République "
                  "française."),
    "2015-363": ("2015-04-01", "JORFARTI000030419590", "JORFTEXT000030419563", "2015-03-31",
                 "Le présent décret entre en vigueur le premier jour du mois qui suit sa "
                 "publication."),
}


@pytest.mark.skipif(not (INDEX_LEGI.exists() and INDEX_JORF.exists()),
                    reason="index DILA absent : python scripts/fetch/dila_index.py legi|jorf --recuperer")
def test_une_clause_lue_a_legifrance_est_absente_des_index_et_recoupee_par_la_notice():
    """B7 : la clause des n° 2012-1139 (art. 68) et 2015-363 (art. 14), lue à Légifrance ; à
    l'index, le texte signé (son jour de publication) et sa notice (« Entrée en vigueur : »),
    qui donne la même date ; le premier jour du mois qui suit, calculé ici."""
    legi = sqlite3.connect(f"file:{INDEX_LEGI}?mode=ro", uri=True)
    jorf = sqlite3.connect(f"file:{INDEX_JORF}?mode=ro", uri=True)
    assert rec.ENTREES_LUES_A_LEGIFRANCE == LUES_A_LEGIFRANCE_CLAUSES
    notices = {"2012-1139": "Entrée en vigueur : le texte entre en vigueur le 1er novembre 2012.",
               "2015-363": "Entrée en vigueur : le décret entre en vigueur le 1er avril 2015."}
    for numero, (jour, jorfarti, jorftexte, publication, citation) in LUES_A_LEGIFRANCE_CLAUSES.items():
        assert not jorf.execute("select 1 from doc where id = ?", (jorfarti,)).fetchone(), numero
        assert not [t for (t,) in legi.execute(
            "select texte from doc where titre like ? and nature like 'Article%'",
            (f"Décret n° {numero} du%",)) if _plat(citation) in _plat(t)], numero
        signe = jorf.execute("select date, titre, texte from doc where id = ?",
                             (jorftexte,)).fetchone()
        assert signe and signe[0] == publication and numero in signe[1], numero
        assert notices[numero] in _plat(signe[2]), numero
        p = date.fromisoformat(publication)
        assert jour == date(p.year + (p.month == 12), p.month % 12 + 1, 1).isoformat(), numero


def test_chaque_ligne_lue_est_certifiee_et_chaque_refus_motive():
    lignes = _lire("lignes")
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}
    assert all(r["motif"] for r in _lire("non_lus"))
    # Chaque ligne a son tableau, chaque tableau son texte.
    tableaux = {(t["article"], t["tableau"]) for t in _lire("tableaux")}
    assert {(l["article"], l["tableau"]) for l in lignes} == tableaux
    assert {t["texte"] for t in _lire("tableaux")} <= {t["texte"] for t in _lire("textes")}
