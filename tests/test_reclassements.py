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
import sys
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
}


def test_un_tableau_que_date_un_autre_article_de_son_decret_prend_cette_date():
    """Action 158, B5-bis (relecture R-B5). Ces quatre tableaux étaient datés de
    l'entrée en vigueur de leur version (2003-06-21, 2001-04-15, 2017-09-23,
    2017-10-28) ; le décret les fait prendre effet plus tôt. Deux restent sans date,
    déclarés : le n° 98-268, art. 20, échelonne l'accès au grade (« au 1er août 1994,
    au 1er août 1995, au 1er août 1996 et au 1er janvier 1997 ») ; l'art. 8 du n° 98-896,
    récrit par le n° 2002-378, qui ne dit pas quand sa rédaction prend effet."""
    tableaux = {(t["article"], t["tableau"]): t for t in _lire("tableaux")}
    assert ({cle: tableaux[cle]["effet"] for cle in DATES_D_UN_AUTRE_ARTICLE}
            == DATES_D_UN_AUTRE_ARTICLE)
    assert tableaux[("LEGIARTI000006506612", "1")]["effet"] == ""  # n° 98-268, art. 20
    assert tableaux[("LEGIARTI000006508629", "1")]["effet"] == ""  # n° 98-896, art. 8
    assert set(rec.DATES_D_UN_AUTRE_ARTICLE) == {article for article, _ in DATES_D_UN_AUTRE_ARTICLE}


def test_chaque_ligne_lue_est_certifiee_et_chaque_refus_motive():
    lignes = _lire("lignes")
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}
    assert all(r["motif"] for r in _lire("non_lus"))
    # Chaque ligne a son tableau, chaque tableau son texte.
    tableaux = {(t["article"], t["tableau"]) for t in _lire("tableaux")}
    assert {(l["article"], l["tableau"]) for l in lignes} == tableaux
    assert {t["texte"] for t in _lire("tableaux")} <= {t["texte"] for t in _lire("textes")}
