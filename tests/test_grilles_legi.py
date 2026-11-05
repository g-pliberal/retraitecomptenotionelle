"""Les grilles indiciaires de la territoriale et de l'hospitalière, lues au LEGI (action 158, étape 2).

La base LEGI garde chaque version des articles qui fixent l'échelonnement
indiciaire d'un cadre d'emplois ou d'un corps, mais l'index du dépôt
(``scripts/fetch/dila_index.py``) en ôte les balises : un tableau n'y est plus
qu'une suite de mots et de nombres. ``scripts/fetch/dila_legi_grilles.py`` le
relit. Les textes des essais sont ceux de l'index, recopiés tels quels ou
abrégés de quelques lignes ; chaque attendu se lit dans le texte de l'essai.
Puis la donnée, sous ``data/reference/grilles/``, confrontée à des grilles
qu'une source publiée affiche, qui ne la recopie pas.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]


def _charger(nom: str):
    chemin = RACINE / "scripts" / "fetch" / f"{nom}.py"
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
# La lecture d'un tableau aplati
# ---------------------------------------------------------------------------

#: Décret n° 2016-604, article 1er, version du 1er janvier 2017
#: (LEGIARTI000032545076) : les dates en colonnes, les échelles en groupes,
#: « Néant » pour l'échelon qui n'existe pas encore.
C_TERRITORIALE_2017 = (
    "L'échelonnement indiciaire applicable aux cadres d'emplois des fonctionnaires "
    "territoriaux de catégorie C, comportant trois échelles de rémunération C1, C2 et "
    "C3, est fixé ainsi qu'il suit : ÉCHELLES ET ÉCHELONS INDICES BRUTS A compter du "
    "1er janvier 2017 A compter du 1er janvier 2018 A compter du 1er janvier 2019 A "
    "compter du 1er janvier 2020 Echelle C 3 10e échelon 548 548 548 558 9e échelon 518 "
    "525 525 525 8e échelon 499 499 499 499 7e échelon 475 478 478 478 6e échelon 457 "
    "460 460 460 5e échelon 445 448 448 448 4e échelon 422 430 430 430 3e échelon 404 "
    "412 412 412 2e échelon 388 393 393 393 1er échelon 374 380 380 380 Echelle C 2 12e "
    "échelon 479 483 483 486 11e échelon 471 471 471 473 10e échelon 459 459 459 461 9e "
    "échelon 444 444 444 446 8e échelon 430 430 430 430 7e échelon 403 403 403 404 6e "
    "échelon 380 381 381 387 5e échelon 372 374 374 376 4e échelon 362 362 362 364 3e "
    "échelon 357 358 358 362 2e échelon 354 354 354 359 1er échelon 351 351 353 356 "
    "Echelle C 1 12e échelon Néant Néant Néant 432 11e échelon 407 407 412 419 10e "
    "échelon 386 386 389 401 9e échelon 370 372 376 387 8e échelon 362 366 370 378 7e "
    "échelon 356 361 365 370 6e échelon 354 356 359 363 5e échelon 352 354 356 361 4e "
    "échelon 351 353 354 358 3e échelon 349 351 353 356 2e échelon 348 350 351 355 1er "
    "échelon 347 348 350 354")


def test_les_dates_en_colonnes_et_les_echelles_en_groupes():
    tableau = grilles.lire_tableau(C_TERRITORIALE_2017)
    assert tableau.refus == ""
    assert tableau.groupes == ["Echelle C 3", "Echelle C 2", "Echelle C 1"]
    assert tableau.dates == ["2017-01-01", "2018-01-01", "2019-01-01", "2020-01-01"]
    assert _valeurs(tableau, "Echelle C 3", "2017-01-01")["1"] == 374
    assert _valeurs(tableau, "Echelle C 3", "2020-01-01")["10"] == 558
    assert _valeurs(tableau, "Echelle C 2", "2019-01-01")["1"] == 353
    # « Néant » : l'échelon n'existe qu'à la quatrième date.
    assert "12" not in _valeurs(tableau, "Echelle C 1", "2019-01-01")
    assert _valeurs(tableau, "Echelle C 1", "2020-01-01")["12"] == 432
    assert len(tableau.cellules) == 4 * (10 + 12 + 12) - 3


#: Décret n° 2010-330, article 1er, version du 1er février 2014
#: (LEGIARTI000028542671), abrégée : une colonne sans date, celle de la
#: version, puis une colonne « Au 1er janvier 2015 ».
B_TERRITORIALE_2014 = (
    "L'échelonnement indiciaire applicable aux membres des cadres d'emplois régis par "
    "le décret du 22 mars 2010 susvisé est fixé ainsi qu'il suit : ÉCHELONS INDICES "
    "BRUTS Au 1er janvier 2015 Troisième grade 11e échelon 675 675 10e échelon 646 646 "
    "2e échelon 430 430 1er échelon 404 404 Premier grade 13e échelon 576 576 3e "
    "échelon 347 356 2e échelon 342 352 1er échelon 340 348")


def test_une_colonne_de_plus_que_de_dates_est_celle_de_la_version():
    tableau = grilles.lire_tableau(B_TERRITORIALE_2014)
    assert tableau.refus == ""
    assert tableau.dates == ["", "2015-01-01"]
    assert _valeurs(tableau, "Premier grade", "")["1"] == 340
    assert _valeurs(tableau, "Premier grade", "2015-01-01")["1"] == 348
    assert _valeurs(tableau, "Troisième grade", "")["11"] == 675


#: Décret n° 2021-1267, article 1er, version du 1er octobre 2021
#: (LEGIARTI000044131698) : le rang nu devant son indice.
AIDES_SOIGNANTS_2021 = (
    "L'échelonnement indiciaire applicable aux membres du corps des aides-soignants et "
    "des auxiliaires de puériculture de la fonction publique hospitalière, régis par le "
    "décret du 29 septembre 2021 susvisé, est fixé ainsi qu'il suit : Echelons Indices "
    "bruts Classe supérieure du corps des aides-soignants et des auxiliaires de "
    "puériculture 11 665 10 638 9 612 8 585 7 561 6 532 5 508 4 484 3 464 2 449 1 433 "
    "Classe normale du corps du corps des aides-soignants et des auxiliaires de "
    "puériculture 12 610 11 567 10 535 9 510 8 491 7 468 6 452 5 434 4 416 3 395 2 380 "
    "1 372")


def test_le_rang_nu_devant_son_indice():
    tableau = grilles.lire_tableau(AIDES_SOIGNANTS_2021)
    assert tableau.refus == ""
    superieure = ("Classe supérieure du corps des aides-soignants et des auxiliaires "
                  "de puériculture")
    normale = ("Classe normale du corps du corps des aides-soignants et des auxiliaires "
               "de puériculture")
    assert tableau.groupes == [superieure, normale]
    assert _valeurs(tableau, superieure) == {
        str(r): v for r, v in zip(range(11, 0, -1),
                                  (665, 638, 612, 585, 561, 532, 508, 484, 464, 449, 433))}
    assert _valeurs(tableau, normale)["12"] == 610
    assert _valeurs(tableau, normale)["1"] == 372


#: Décret n° 87-1108, article 1er, version du 1er juillet 2008
#: (LEGIARTI000020047843), abrégée : les échelles en colonnes.
C_TERRITORIALE_2008 = (
    "L'échelonnement indiciaire applicable aux échelles 3, 4 et 5 de rémunération "
    "instituées par le décret n° 87-1107 du 30 décembre 1987 susvisé est fixé ainsi "
    "qu'il suit : ÉCHELONS INDICES BRUTS Echelle 3 Echelle 4 Echelle 5 11e échelon 388 "
    "413 446 10e échelon 364 389 427 2e échelon 298 299 302 1er échelon 297 298 299")


def test_les_echelles_en_colonnes():
    tableau = grilles.lire_tableau(C_TERRITORIALE_2008)
    assert tableau.refus == ""
    assert tableau.groupes == ["Echelle 3", "Echelle 4", "Echelle 5"]
    assert tableau.dates == [""]
    assert _valeurs(tableau, "Echelle 3") == {"11": 388, "10": 364, "2": 298, "1": 297}
    assert _valeurs(tableau, "Echelle 5") == {"11": 446, "10": 427, "2": 302, "1": 299}


#: Décret n° 87-1108, article 1er, version du 1er février 2014
#: (LEGIARTI000028542668), abrégée : deux tableaux, le second daté, le rang
#: nu, la barre oblique pour l'échelon qu'une échelle n'a pas.
C_TERRITORIALE_2014 = (
    "L'échelonnement indiciaire applicable aux échelles 3, 4 et 5 de rémunération "
    "instituées par le décret n° 87-1107 du 30 décembre 1987 susvisé est fixé ainsi "
    "qu'il suit : ÉCHELONS INDICES BRUTS Echelle 3 Echelle 4 Echelle 5 Echelle 6 12 / "
    "424 459 / 11 393 416 447 / 9 358 379 417 536 1 330 336 340 358 ÉCHELONS INDICES "
    "BRUTS AU 1er JANVIER 2015 Echelle 3 Echelle 4 Echelle 5 Echelle 6 12 / 432 465 / "
    "11 400 422 454 / 9 364 386 423 543 1 340 342 348 364")


def test_deux_tableaux_le_second_date_et_la_barre_oblique():
    tableau = grilles.lire_tableau(C_TERRITORIALE_2014)
    assert tableau.refus == ""
    assert tableau.groupes == ["Echelle 3", "Echelle 4", "Echelle 5", "Echelle 6"]
    assert tableau.dates == ["", "2015-01-01"]
    assert _valeurs(tableau, "Echelle 3", "") == {"11": 393, "9": 358, "1": 330}
    assert _valeurs(tableau, "Echelle 6", "") == {"9": 536, "1": 358}
    assert _valeurs(tableau, "Echelle 4", "2015-01-01") == {"12": 432, "11": 422, "9": 386,
                                                            "1": 342}


#: Arrêté du 19 mai 2016 (catégorie C de l'hospitalière), article 1er, version
#: du 22 mai 2016 (LEGIARTI000032575056), abrégée : la ligne d'un échelon créé
#: à la dernière date n'a qu'une valeur, la case vide n'ayant pas de texte.
C1_HOSPITALIERE_2016 = (
    "L'échelonnement indiciaire applicable à l'échelle de rémunération C1 instituée à "
    "l'article 1er du décret n° 2016-644 du 19 mai 2016 susvisé est fixé ainsi qu'il "
    "suit : Echelle de rémunération C1 Indices bruts A compter du 1er janvier 2017 A "
    "compter du 1er janvier 2018 A compter du 1er janvier 2019 A compter du 1er janvier "
    "2020 12e échelon 432 11e échelon 407 407 412 419 10e échelon 386 386 389 401 2e "
    "échelon 348 350 351 355 1er échelon 347 348 350 354")


def test_l_echelon_cree_a_la_derniere_date_prend_la_derniere_colonne():
    tableau = grilles.lire_tableau(C1_HOSPITALIERE_2016)
    assert tableau.refus == ""
    groupe = "Echelle de rémunération C1"
    assert "12" not in _valeurs(tableau, groupe, "2019-01-01")
    assert _valeurs(tableau, groupe, "2020-01-01")["12"] == 432
    assert any("12" in alerte for alerte in tableau.alertes)
    # 432 dépasse le 11e échelon à toutes les dates : l'indice seul ne dit pas
    # la colonne, qui est présumée.
    (douzieme,) = [c for c in tableau.cellules if c.echelon == "12"]
    assert douzieme.lecture == "presumee"
    assert {c.lecture for c in tableau.cellules if c.echelon != "12"} == {""}


#: Arrêté du 19 mai 2016 (personnels de rééducation et médico-techniques de
#: catégorie B de l'hospitalière), article 1er, version du 22 mai 2016
#: (LEGIARTI000032573417), abrégée : l'échelon 8 de la classe supérieure est
#: créé en 2017, l'échelon 9 de la classe normale supprimé la même année. À
#: droite, 621 passerait sous les 638 du 8e échelon de 2018 : il est à gauche.
B_HOSPITALIERE_2016 = (
    "L'échelonnement indiciaire applicable aux corps est fixé ainsi qu'il suit : "
    "Echelons Indices bruts A compter du 1er janvier 2016 A compter du 1er janvier 2017 "
    "A compter du 1er janvier 2018 Classe supérieure Echelon 8 701 707 Echelon 7 683 684 "
    "684 Echelon 1 498 508 518 Classe normale Echelon 9 621 Echelon 8 579 631 638 "
    "Echelon 1 358 377 389")


def test_l_echelon_supprime_garde_la_premiere_colonne_quand_l_indice_le_dit():
    tableau = grilles.lire_tableau(B_HOSPITALIERE_2016)
    assert tableau.refus == ""
    assert _valeurs(tableau, "Classe normale", "2016-01-01")["9"] == 621
    assert "9" not in _valeurs(tableau, "Classe normale", "2018-01-01")
    (neuvieme,) = [c for c in tableau.cellules if c.echelon == "9"]
    assert neuvieme.lecture == "deduite"
    # 701 et 707 vont aux deux dernières colonnes comme aux deux premières :
    # rien ne tranche, la place est présumée, à droite.
    huitieme = {c.date: (c.indice, c.lecture) for c in tableau.cellules
                if c.groupe == "Classe supérieure" and c.echelon == "8"}
    assert huitieme == {"2017-01-01": (701, "presumee"), "2018-01-01": (707, "presumee")}


#: Décret n° 91-844, article 1er, version du 1er janvier 2010
#: (LEGIARTI000021501866) : l'ordinal seul, sans le mot « échelon ».
ATTACHES_CONSERVATION_2010 = (
    "L'échelonnement indiciaire applicable aux attachés territoriaux de conservation du "
    "patrimoine est fixé ainsi qu'il suit : ÉCHELONS INDICES BRUTS 11e 801 10e 750 9e 701 "
    "8e 659 7e 616 6e 593 5e 550 4e 510 3e 465 2e 423 1er 379")


def test_l_ordinal_seul_devant_son_indice():
    tableau = grilles.lire_tableau(ATTACHES_CONSERVATION_2010)
    assert tableau.refus == ""
    assert tableau.groupes == ["attachés territoriaux de conservation du patrimoine"]
    assert _valeurs(tableau, "attachés territoriaux de conservation du patrimoine") == {
        "11": 801, "10": 750, "9": 701, "8": 659, "7": 616, "6": 593, "5": 550, "4": 510,
        "3": 465, "2": 423, "1": 379}


#: Décret n° 87-1102, article 1er, version du 29 décembre 1994
#: (LEGIARTI000006370617), abrégée : le rang, deux points, l'indice écrit
#: « 1.000 ».
EMPLOIS_DE_DIRECTION_1994 = (
    "L'échelonnement indiciaire des emplois de secrétaire général de ville et de directeur "
    "d'office public d'H.L.M. institué par le décret n° 87-1101 du 30 décembre 1987 est fixé "
    "ainsi qu'il suit : EMPLOIS : Secrétaire général de ville ou directeur d'office public "
    "d'H.L.M : - de plus de 400.000 habitants. - ECHELONS (indices bruts) : 1 : 1.000 2 : HEA "
    "3 : HEB 4 : HEC EMPLOIS : Secrétaire général de ville ou directeur d'office public "
    "d'H.L.M : - de 150.000 à 400.000 habitants - ECHELONS (indices bruts) : 1 : 885 2 : 910 "
    "3 : 940")


def test_le_rang_deux_points_et_l_indice_ecrit_avec_un_point():
    tableau = grilles.lire_tableau(EMPLOIS_DE_DIRECTION_1994)
    assert tableau.refus == ""
    assert tableau.dates == [""]
    premier, second = tableau.groupes
    assert _valeurs(tableau, premier) == {"1": 1000, "2": "A", "3": "B", "4": "C"}
    assert _valeurs(tableau, second) == {"1": 885, "2": 910, "3": 940}


#: Décret n° 87-1100 (attachés territoriaux), article 1er, version du
#: 1er janvier 2017 (LEGIARTI000033677724), abrégée : le millier séparé par
#: une espace, la lettre de hors-échelle répétée dans chaque colonne.
ATTACHES_2017 = (
    "L'échelonnement indiciaire applicable au cadre d'emplois des attachés territoriaux est "
    "fixé ainsi qu'il suit : GRADES ET ÉCHELONS INDICES BRUTS à compter du 1er janvier 2017 "
    "INDICES BRUTS à compter du 1er janvier 2018 INDICES BRUTS à compter du 1er janvier 2019 "
    "INDICES BRUTS à compter du 1er janvier 2020 Attaché hors classe Echelon spécial HEA HEA "
    "HEA HEA 6e échelon 1 022 1 027 1 027 1 027 5e échelon 979 985 995 995 4e échelon 929 "
    "935 946 946 3e échelon 882 888 896 896 2e échelon 834 841 850 850 1er échelon 784 790 "
    "797 797")


def test_le_millier_separe_par_une_espace():
    tableau = grilles.lire_tableau(ATTACHES_2017)
    assert tableau.refus == ""
    assert _valeurs(tableau, "Attaché hors classe", "2017-01-01") == {
        "special": "A", "6": 1022, "5": 979, "4": 929, "3": 882, "2": 834, "1": 784}
    assert _valeurs(tableau, "Attaché hors classe", "2020-01-01")["6"] == 1027


#: Décret n° 2025-832 (administrateurs de la Ville de Paris), article 1er,
#: version du 22 août 2025 (LEGIARTI000052121400), abrégée : depuis la réforme
#: de la haute fonction publique, des indices bruts au-delà de 1 027.
ADMINISTRATEURS_PARIS_2025 = (
    "L'échelonnement indiciaire applicable aux administrateurs de la Ville de Paris est fixé "
    "ainsi qu'il suit : Echelons Indices bruts Administrateurs de la Ville de Paris "
    "Administrateurs du troisième grade 30 2074 29 2068 28 2062 3 1427 2 1367 1 1309 "
    "Administrateurs du deuxième grade 32 1806 31 1799 2 860 1 808")


def test_les_indices_bruts_de_la_haute_fonction_publique():
    tableau = grilles.lire_tableau(ADMINISTRATEURS_PARIS_2025)
    assert tableau.refus == ""
    troisieme = "Administrateurs de la Ville de Paris Administrateurs du troisième grade"
    assert _valeurs(tableau, troisieme) == {"30": 2074, "29": 2068, "28": 2062, "3": 1427,
                                            "2": 1367, "1": 1309}
    assert _valeurs(tableau, "Administrateurs du deuxième grade") == {
        "32": 1806, "31": 1799, "2": 860, "1": 808}


#: Décret n° 2024-54, article 1er, version du 1er février 2024
#: (LEGIARTI000049064197), abrégée : l'échelon spécial et les lettres de la
#: hors-échelle.
INGENIEURS_EN_CHEF_2024 = (
    "L'échelonnement indiciaire est fixé ainsi qu'il suit : GRADES INDICES BRUTS "
    "Ingénieur en chef de classe exceptionnelle Echelon spécial HEE 6e échelon HED 5e "
    "échelon HEC 4e échelon HEB bis 3e échelon HEB 2e échelon HEA 1e échelon 1027 "
    "Ingénieur en chef 2e échelon 525 1er échelon 461")


def test_l_echelon_special_et_la_hors_echelle():
    tableau = grilles.lire_tableau(INGENIEURS_EN_CHEF_2024)
    assert tableau.refus == ""
    assert _valeurs(tableau, "Ingénieur en chef de classe exceptionnelle") == {
        "special": "E", "6": "D", "5": "C", "4": "B bis", "3": "B", "2": "A", "1": 1027}
    assert _valeurs(tableau, "Ingénieur en chef") == {"2": 525, "1": 461}


#: Arrêté du 19 mai 2016 (infirmiers anesthésistes), article 1er, version du
#: 1er janvier 2018 (LEGIARTI000036501105), abrégée : « Echelon 7 ».
ANESTHESISTES_2018 = (
    "L'échelonnement indiciaire applicable aux membres du corps des infirmiers "
    "anesthésistes est fixé comme suit : Echelons Indices bruts A compter du 1er "
    "janvier 2016 A compter du 1er janvier 2017 A compter du 1er janvier 2019 A compter "
    "du 1er janvier 2020 Infirmier(ère) anesthésiste de classe supérieure Echelon 7 736 "
    "743 747 761 Echelon 6 685 694 698 706 Echelon 1 539 545 549 554")


def test_l_echelon_ecrit_avant_son_rang():
    tableau = grilles.lire_tableau(ANESTHESISTES_2018)
    assert tableau.refus == ""
    groupe = "Infirmier(ère) anesthésiste de classe supérieure"
    assert _valeurs(tableau, groupe, "2020-01-01") == {"7": 761, "6": 706, "1": 554}


#: Décret n° 2021-1827, article 1er, version du 1er janvier 2022
#: (LEGIARTI000044635479) : le tableau ne nomme pas l'échelle, la phrase qui
#: l'introduit la nomme.
C3_HOSPITALIERE_2022 = (
    "L'échelonnement indiciaire applicable à l'échelle de rémunération C3 mentionnée à "
    "l'article 2 du décret du 19 mai 2016 susvisé est fixé ainsi qu'il suit : ÉCHELONS "
    "INDICES BRUTS à compter du 1er janvier 2022 10e échelon 558 9e échelon 525 8e "
    "échelon 499 7e échelon 478 6e échelon 460 5e échelon 448 4e échelon 430 3e échelon "
    "412 2e échelon 397 1er échelon 388")


def test_sans_groupe_dans_le_tableau_la_phrase_qui_l_introduit_le_nomme():
    tableau = grilles.lire_tableau(C3_HOSPITALIERE_2022)
    assert tableau.refus == ""
    assert tableau.groupes == ["échelle de rémunération C3"]
    assert _valeurs(tableau, "échelle de rémunération C3", "2022-01-01")["1"] == 388


#: Décret n° 87-1108, article 1er, version du 1er août 1990
#: (LEGIARTI000006370843), abrégée : une liste par échelle et par date.
C_TERRITORIALE_1990 = (
    "L'échelonnement indiciaire applicable aux échelles de rémunération institués par "
    "le décret n° 87-1107 du 30 décembre 1987 susvisé est fixé ainsi qu'il suit: 1. En "
    "ce qui concerne l'échelle 1 Indices bruts à compter du 1er août 1990 1er échelon : "
    "209 2e échelon : 220 3e échelon : 229 Indices bruts à compter du 1er août 1991 1er "
    "échelon : 209 2e échelon : 220 3e échelon : 229 2. En ce qui concerne l'échelle 2 "
    "Indices bruts à compter du 1er août 1990 1er échelon : 220 2e échelon : 241")


def test_la_liste_par_echelle_et_par_date():
    tableau = grilles.lire_tableau(C_TERRITORIALE_1990)
    assert tableau.refus == ""
    # « En ce qui concerne l' » ôté, l'échelle a la clé de celles des versions
    # suivantes, écrites « Echelle 2 » en tête de colonne (action 158, l'État).
    assert tableau.groupes == ["échelle 1", "échelle 2"]
    assert _valeurs(tableau, "échelle 1", "1991-08-01") == {"1": 209, "2": 220, "3": 229}
    assert _valeurs(tableau, "échelle 2", "1990-08-01") == {"1": 220, "2": 241}


#: Arrêté du 31 décembre 2001 (personnels infirmiers de l'hospitalière),
#: article 1er, version du 2 janvier 2002 (LEGIARTI000019419872) : deux grades
#: côte à côte, dont l'aplatissement entrelace les lignes.
INFIRMIERS_2002 = (
    "L'échelonnement indiciaire est fixé ainsi qu'il suit : CORPS DES INFIRMIERS "
    "ÉCHELONS Infirmiers de classe normale INDICES BRUTS ÉCHELONS Infirmiers de classe "
    "supérieure INDICES BRUTS 8e 568 7e 519 6e 480 6e 638 5e 443 5e 613 4e 407 4e 580 3e "
    "372 3e 548 2e 346 2e 514 1er 322 1er 471")


def test_deux_grades_cote_a_cote():
    tableau = grilles.lire_tableau(INFIRMIERS_2002)
    assert tableau.refus == ""
    normale = "CORPS DES INFIRMIERS – Infirmiers de classe normale"
    superieure = "CORPS DES INFIRMIERS – Infirmiers de classe supérieure"
    assert tableau.groupes == [normale, superieure]
    assert _valeurs(tableau, normale) == {"8": 568, "7": 519, "6": 480, "5": 443, "4": 407,
                                          "3": 372, "2": 346, "1": 322}
    assert _valeurs(tableau, superieure) == {"6": 638, "5": 613, "4": 580, "3": 548, "2": 514,
                                             "1": 471}


#: Décret n° 2013-493 (moniteurs-éducateurs territoriaux), article 1er,
#: version du 1er janvier 2016 (LEGIARTI000032546881), abrégée : le LEGI colle
#: « Indices bruts » à « à compter du ».
MONITEURS_EDUCATEURS_2016 = (
    "L'échelonnement indiciaire applicable au cadre d'emplois des moniteurs-éducateurs et "
    "intervenants familiaux territoriaux est fixé ainsi qu'il suit : GRADE ET ÉCHELON "
    "Moniteur-éducateur et intervenant familial principal Indices brutsà compter du 1er "
    "janvier 2016 Indices brutsà compter du 1er janvier 2017 Indices brutsà compter du 1er "
    "janvier 2018 13e échelon 621 631 638 12e échelon 589 593 599")


def test_les_mots_colles_par_le_legi():
    tableau = grilles.lire_tableau(MONITEURS_EDUCATEURS_2016)
    assert tableau.refus == ""
    assert tableau.dates == ["2016-01-01", "2017-01-01", "2018-01-01"]
    assert tableau.groupes == ["Moniteur-éducateur et intervenant familial principal"]


#: Arrêté du 29 septembre 2010 (infirmiers en soins généraux et spécialisés),
#: article 1er, version du 1er juillet 2012 (LEGIARTI000022870385), abrégée :
#: la date d'effet entre « suit » et les deux-points.
ISGS_2012 = (
    "L'échelonnement indiciaire applicable au corps des infirmiers en soins généraux et "
    "spécialisés de la fonction publique hospitalière est fixé ainsi qu'il suit à compter "
    "du 1er juillet 2012 : GRADES ET ÉCHELONS INDICE BRUT Quatrième grade 7e échelon 758 "
    "6e échelon 735 1er échelon 580 Troisième grade 11e échelon 740 10e échelon 716")


def test_la_date_d_effet_entre_suit_et_les_deux_points():
    tableau = grilles.lire_tableau(ISGS_2012)
    assert tableau.refus == ""
    assert tableau.groupes == ["Quatrième grade", "Troisième grade"]
    assert tableau.dates == ["2012-07-01"]


#: Décret n° 88-548 (agents de maîtrise territoriaux), article 1er, version du
#: 1er janvier 2022 (LEGIARTI000044811879), abrégée : « 8eéchelon ».
AGENTS_DE_MAITRISE_2022 = (
    "L'échelonnement indiciaire applicable aux membres du cadre d'emplois des agents de "
    "maîtrise est fixé ainsi qu'il suit : GRADES ET ÉCHELONS INDICES BRUTS à compter du 1er "
    "janvier 2022 Agent de maîtrise 13e échelon 562 9e échelon 465 8eéchelon 449 7e échelon "
    "437 1er échelon 372")


def test_l_ordinal_colle_a_l_echelon():
    tableau = grilles.lire_tableau(AGENTS_DE_MAITRISE_2022)
    assert tableau.refus == ""
    assert _valeurs(tableau, "Agent de maîtrise", "2022-01-01") == {
        "13": 562, "9": 465, "8": 449, "7": 437, "1": 372}


@pytest.mark.parametrize("libelle, hors", [
    ("de 150.000 à 400.000 habitants", False),
    ("de 40 .000 à 80 .000 habitants", False),
    ("De 20 000 à moins de 40 000 habitants", False),
    ("Surveillants grade provisoire du 1er janvier 2002 jusqu'au 31 décembre 2003", False),
    ("décret n° 87-1107 du 30 décembre 1987", False),
    # Des indices bruts à la suite ne sont pas un nombre écrit par milliers.
    ("8 eéchelon 445 447 449 449", True),
    ("Attaché principal Echelon provisoire :558.", True),
])
def test_un_libelle_ne_garde_pas_d_indice(libelle, hors):
    assert grilles._hors_des_lignes(libelle) is hors


#: Arrêté du 3 août 2007 (agents chefs de l'hospitalière), article 1er,
#: version du 25 juin 2007 (LEGIARTI000019416706), abrégée : « conformément
#: au tableau ci-après : ».
AGENTS_CHEFS_2007 = (
    "L'échelle indiciaire applicable au corps des agents chefs est fixée conformément au "
    "tableau ci-après : Agent chef de classe exceptionnelle ÉCHELONS INDICES BRUTS 7e "
    "échelon 612 6e échelon 580 1er échelon 425 Agent chef de 1re catégorie ÉCHELONS "
    "INDICES BRUTS 8e échelon 579 7e échelon 547 1er échelon 399")


def test_le_tableau_ci_apres():
    tableau = grilles.lire_tableau(AGENTS_CHEFS_2007)
    assert tableau.refus == ""
    assert tableau.groupes == ["Agent chef de classe exceptionnelle",
                               "Agent chef de 1re catégorie"]


#: Arrêté du 31 décembre 2001 (personnels d'encadrement de l'hospitalière),
#: version du 2 janvier 2002 (LEGIARTI000019419889) : « du » et « jusqu'au »
#: bornent un grade provisoire, sans ouvrir de colonne.
SURVEILLANTS_2002 = (
    "L'échelonnement indiciaire est fixé ainsi qu'il suit : CORPS DES SURVEILLANTS ÉCHELONS "
    "INDICES BRUTS Surveillants grade provisoire du 1er janvier 2002 jusqu'au 31 décembre "
    "2003 7e 638 6e 595 5e 557 4e 522 3e 485 2e 455 1er 422")


def test_du_et_jusqu_au_n_ouvrent_pas_de_colonne():
    tableau = grilles.lire_tableau(SURVEILLANTS_2002)
    assert tableau.refus == ""
    assert tableau.dates == [""]
    (groupe,) = tableau.groupes
    assert groupe.startswith("CORPS DES SURVEILLANTS Surveillants grade provisoire")
    assert _valeurs(tableau, groupe)["7"] == 638


@pytest.mark.parametrize("texte, motif", [
    # Arrêté du 29 novembre 1973, un tableau de reclassement (LEGIARTI000006719723).
    ("Les agents visés à l'article 1er du présent arrêté et occupant un emploi "
     "d'infirmier ou d'infirmière sont reclassés dans l'échelle figurant au tableau "
     "annexe 1 conformément au tableau ci-après : SITUATION ACTUELLE : Echelon "
     "exceptionnel (IB 405), Après 6 ans SITUATION NOUVELLE, ANCIENNETE : 11 éch "
     "(IB 427), Ancienneté acquise diminuée de 6 ans.", "reclassement"),
    # Décret n° 87-1108, version du 31 décembre 1987 : un tableau dessiné en
    # caractères, que l'analyseur ne lit pas encore.
    ("L'échelonnement indiciaire applicable aux groupes de rémunération institués par "
     "le décret n° 87-1107 du 30 décembre 1987 est fixé ainsi qu'il suit : "
     ":------------------------------: : ECHELLES ECHELONS : : ET : : : GROUPES : 1 : "
     "2 : 3 : : : : : : : Echelle I : 209 : 220 : 229 :", "caractères"),
    # Une ligne de plus de valeurs que de colonnes : l'analyseur s'abstient.
    ("L'échelonnement indiciaire est fixé ainsi qu'il suit : ÉCHELONS INDICES BRUTS A "
     "compter du 1er janvier 2017 Grade 2e échelon 380 390 1er échelon 370", "colonnes"),
    # Un indice qui baisse quand l'échelon monte : une lecture fausse.
    ("L'échelonnement indiciaire est fixé ainsi qu'il suit : ÉCHELONS INDICES BRUTS "
     "Grade 3e échelon 412 2e échelon 430 1er échelon 388", "monte"),
    # Arrêté du 11 avril 1985 (LEGIARTI000006720241), abrégé : la date d'un texte
    # cité n'est pas celle d'une colonne ; les deux valeurs de chaque ligne sont
    # l'indice brut et l'indice nouveau majoré.
    ("abrogé implicitement par l'arrêté du 1er septembre 1989 TABLEAU ANNEXE CLASSE "
     "FONCTIONNELLE (1) Echelon Indices Durée Ancienneté moyenne (à/c du 01-01-1985) bruts "
     "nouveaux 6e 579 480 5e 538 448 4 ans 4e 501 423 4 ans 3e 464 396 4 ans", "majorés"),
    # Décret n° 86-480, article 1er, version du 16 mars 1986 (LEGIARTI000006369962),
    # abrégé : « 681/660 », deux indices d'un même échelon, dont le second
    # tomberait dans le libellé du groupe suivant.
    ("L'échelonnement indiciaire est fixé ainsi qu'il suit : Directeur de service "
     "administratif Classe normale : Indices bruts : 6ème échelon : 871 5ème échelon : 841 "
     "3ème échelon provisoire : 681/660 2ème échelon provisoire : 642/632 1er échelon "
     "provisoire : 597.", "hors des lignes"),
    # Décret n° 2011-662, version du 16 juin 2011 (LEGIARTI000024174826) : les
    # indices extrêmes de chaque grade, sans ses échelons.
    ("Le classement indiciaire est fixé ainsi qu'il suit : Indices bruts : GRADES À "
     "COMPTER DU 1er JANVIER 2012 Premier grade 325-576 325-576 Deuxième grade 350-614 "
     "350-614", "extrêmes"),
])
def test_ce_qui_n_est_pas_une_grille_lisible_est_refuse(texte, motif):
    tableau = grilles.lire_tableau(texte)
    assert motif in tableau.refus
    assert tableau.cellules == []


def test_la_cle_d_un_groupe_ignore_l_espace_et_la_remuneration():
    assert (grilles.cle_groupe("Echelle C 3") == grilles.cle_groupe("Echelle C3")
            == grilles.cle_groupe("échelle de rémunération C3")
            == grilles.cle_groupe("Echelle de rémunération C3") == "echelle-c3")
    assert grilles.cle_groupe("Ingénieur en chef de classe exceptionnelle") == \
        "ingenieur-en-chef-de-classe-exceptionnelle"
    # Le décret n° 2021-1267 écrit « du corps du corps » dans sa version de 2021,
    # « du corps » dans celle de 2022 : le même grade.
    assert grilles.cle_groupe(
        "Classe normale du corps du corps des aides-soignants et des auxiliaires de "
        "puériculture") == grilles.cle_groupe(
        "Classe normale du corps des aides-soignants et des auxiliaires de puériculture")


# ---------------------------------------------------------------------------
# Les versions d'un article, composées en périodes
# ---------------------------------------------------------------------------

#: Décret n° 2016-604, article 1er, version du 1er janvier 2022
#: (LEGIARTI000044811902), que le décret n° 2021-1819 écrit : la note du LEGI
#: devant la phrase, une seule colonne.
C_TERRITORIALE_2022 = (
    "Conformément à l'article 5 du décret n° 2021-1819 du 24 décembre 2021, ces "
    "dispositions entrent en vigueur le 1er janvier 2022. L'échelonnement indiciaire "
    "applicable aux cadres d'emplois des fonctionnaires territoriaux de catégorie C, "
    "comportant trois échelles de rémunération C1, C2 et C3, est fixé ainsi qu'il suit : "
    "ÉCHELLES ET ÉCHELONS INDICES BRUTS à compter du 1er janvier 2022 Echelle C3 10e "
    "échelon 558 9e échelon 525 8e échelon 499 7e échelon 478 6e échelon 460 5e échelon "
    "448 4e échelon 430 3e échelon 412 2e échelon 397 1er échelon 388 Echelle C2 12e "
    "échelon 486 11e échelon 473 10e échelon 461 9e échelon 446 8e échelon 430 7e "
    "échelon 416 6e échelon 404 5e échelon 396 4e échelon 387 3e échelon 376 2e échelon "
    "371 1er échelon 368 Echelle C1 11e échelon 432 10e échelon 419 9e échelon 401 8e "
    "échelon 387 7e échelon 381 6e échelon 378 5e échelon 374 4e échelon 371 3e échelon "
    "370 2e échelon 368 1er échelon 367")

def test_les_versions_et_leurs_colonnes_font_des_periodes():
    """Décret n° 2016-604, article 1er : la version de 2017 annonce quatre dates,
    celle de 2018 (décret n° 2017-1737, article 116, qui reporte d'un an le
    protocole PPCR) les décale, celle de 2022 (décret n° 2021-1819) refait les échelles. Une colonne
    ne vaut que dans sa version : les dates de 2018 à 2020 de la première ne
    s'appliquent jamais."""
    v2018 = C_TERRITORIALE_2017.replace(
        "1er janvier 2018 A compter du 1er janvier 2019 A compter du 1er janvier 2020",
        "1er janvier 2019 A compter du 1er janvier 2020 A compter du 1er janvier 2021")
    v2022 = C_TERRITORIALE_2022
    versions = [
        grilles.Version("LEGIARTI000032545076", "2017-01-01", "2018-01-01",
                        grilles.lire_tableau(C_TERRITORIALE_2017)),
        grilles.Version("LEGIARTI000036490555", "2018-01-01", "2022-01-01",
                        grilles.lire_tableau(v2018)),
        grilles.Version("LEGIARTI000044811902", "2022-01-01", "2999-01-01",
                        grilles.lire_tableau(v2022)),
    ]
    periodes = grilles.composer(versions)
    c3 = [(p.debut, p.fin, p.indice, p.article) for p in periodes
          if p.groupe == "echelle-c3" and p.echelon == "1"]
    assert c3 == [("2017-01-01", "2018-12-31", 374, "LEGIARTI000032545076"),
                  ("2019-01-01", "2021-12-31", 380, "LEGIARTI000036490555"),
                  ("2022-01-01", "", 388, "LEGIARTI000044811902")]
    douzieme = [(p.debut, p.fin, p.indice) for p in periodes
                if p.groupe == "echelle-c1" and p.echelon == "12"]
    assert douzieme == [("2021-01-01", "2021-12-31", 432)]
    assert [p.libelle for p in periodes if p.groupe == "echelle-c3" and p.echelon == "1"] == [
        "Echelle C 3", "Echelle C 3", "Echelle C3"]


def test_l_echelon_special_se_range_au_dessus_du_plus_haut():
    tableau = grilles.lire_tableau(INGENIEURS_EN_CHEF_2024)
    rangs = {c.echelon: c.rang for c in tableau.cellules
             if c.groupe == "Ingénieur en chef de classe exceptionnelle"}
    assert rangs == {"special": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2, "1": 1}


def test_une_periode_presumee_ne_se_fond_pas_dans_une_periode_lue():
    """L'arrêté hospitalier de 2016 présume la colonne du 12e échelon de C1 ; la
    version suivante, qui ne le présume plus, ne s'y fond pas."""
    lu = C1_HOSPITALIERE_2016.replace("2020 12e échelon 432", "2020 12e échelon - - - 432")
    periodes = grilles.composer([
        grilles.Version("A1", "2017-01-01", "2020-06-01", grilles.lire_tableau(C1_HOSPITALIERE_2016)),
        grilles.Version("A2", "2020-06-01", "2022-01-01", grilles.lire_tableau(lu)),
    ])
    douzieme = [(p.debut, p.fin, p.indice, p.lecture) for p in periodes if p.echelon == "12"]
    assert douzieme == [("2020-01-01", "2020-05-31", 432, "presumee"),
                        ("2020-06-01", "2021-12-31", 432, "")]


@pytest.mark.parametrize("titre, versant", [
    ("Décret n° 2016-604 du 12 mai 2016 fixant les différentes échelles de rémunération pour "
     "les fonctionnaires de catégorie C de la fonction publique territoriale", "territoriale"),
    ("Décret n° 2022-627 du 22 avril 2022 relatif à l'échelonnement indiciaire des techniciens "
     "de laboratoire médical, des préparateurs en pharmacie hospitalière et des diététiciens de "
     "la fonction publique territoriale", "territoriale"),
    ("Décret n° 2022-55 du 24 janvier 2022 relatif à l'échelonnement indiciaire des techniciens "
     "de laboratoire médical, des préparateurs en pharmacie hospitalière et des diététiciens de "
     "la fonction publique hospitalière", "hospitaliere"),
    ("Arrêté du 1 février 1963 relatif au classement et à l'échelonnement indiciaires de certains "
     "grades et emplois du personnel des établissements d'hospitalisation, de soins ou de cure "
     "publics", "hospitaliere"),
    ("Décret n° 2024-54 du 30 janvier 2024 relatif à l'échelonnement indiciaire du corps des "
     "ingénieurs en chef hospitaliers et des emplois d'ingénieurs généraux", "hospitaliere"),
    # Des agents de l'État, au ministère qui a les collectivités territoriales.
    ("Décret n° 2009-369 du 1er avril 2009 fixant l'échelonnement indiciaire de certains "
     "personnels relevant du ministère de l'intérieur, de l'outre-mer et des collectivités "
     "territoriales", "etat"),
    # Les trois versants à la fois : un décret qui en modifie d'autres.
    ("Décret n° 2017-1737 du 21 décembre 2017 modifiant l'échelonnement indiciaire de divers "
     "corps, cadres d'emplois et emplois de la fonction publique de l'Etat, de la fonction "
     "publique territoriale et de la fonction publique hospitalière", ""),
    ("Décret n° 2010-1007 du 26 août 2010 fixant l'échelonnement indiciaire des personnels "
     "enseignants", "etat"),
    # Les personnels enseignants et hospitaliers des CHU sont des corps de l'État.
    ("Décret n° 2013-304 du 10 avril 2013 relatif à l'échelonnement indiciaire applicable aux "
     "personnels enseignants et hospitaliers des centres hospitaliers et universitaires", "etat"),
])
def test_le_versant_se_lit_au_titre(titre, versant):
    assert grilles.versant(titre) == versant


@pytest.mark.parametrize("titre, numero", [
    ("Décret n° 2016-604 du 12 mai 2016 fixant les différentes échelles", "2016-604"),
    ("Décret n°87-1108 du 30 décembre 1987 fixant les différentes échelles", "87-1108"),
    # Le numéro d'un arrêté n'est pas celui de la loi qu'il cite.
    ("Arrêté du 11 mars 2010 modifiant l'arrêté du 2 août 2005 modifié relatif à "
     "l'échelonnement indiciaire applicable aux emplois fonctionnels des établissements "
     "mentionnés à l'article 2 (1° et 7°) de la loi n° 86-33 du 9 janvier 1986", ""),
])
def test_le_numero_d_un_texte_ouvre_son_titre(titre, numero):
    assert grilles.numero(titre) == numero


def test_deux_articles_qui_nomment_pareil_deux_grilles_en_meme_temps_sont_distingues():
    texte = ("L'échelonnement indiciaire est fixé ainsi qu'il suit : ÉCHELONS INDICES BRUTS "
             "Premier grade 2e échelon {} 1er échelon {}")
    versions = grilles.desambiguer([
        grilles.Version("A1", "2011-01-01", EN, grilles.lire_tableau(texte.format(400, 350)), "1"),
        grilles.Version("A2", "2011-01-01", EN, grilles.lire_tableau(texte.format(500, 450)), "2"),
    ])
    assert [v.tableau.groupes for v in versions] == [["Premier grade (article 1)"],
                                                     ["Premier grade (article 2)"]]
    # Décret n° 2021-1262 : l'article 2 donne les échelons provisoires du grade
    # dont l'article 1er donne les autres ; aucun échelon n'est en double.
    provisoires = ("L'échelonnement indiciaire est fixé ainsi qu'il suit : Echelons Indices "
                   "bruts Premier grade 2ème échelon provisoire 580 1er échelon provisoire 548")
    ensemble = grilles.desambiguer([
        grilles.Version("A1", "2021-10-01", EN, grilles.lire_tableau(texte.format(500, 450)), "1"),
        grilles.Version("A2", "2021-10-01", EN, grilles.lire_tableau(provisoires), "2"),
    ])
    assert [v.tableau.groupes for v in ensemble] == [["Premier grade"], ["Premier grade"]]
    # La même grille passée d'un article à l'autre garde son nom.
    suite = grilles.desambiguer([
        grilles.Version("A1", "2011-01-01", "2014-02-01",
                        grilles.lire_tableau(texte.format(400, 350)), "2"),
        grilles.Version("A2", "2014-02-01", EN, grilles.lire_tableau(texte.format(410, 360)), "1"),
    ])
    assert [v.tableau.groupes for v in suite] == [["Premier grade"], ["Premier grade"]]


EN = "2999-01-01"


@pytest.fixture
def index(tmp_path: Path) -> Path:
    """Un index LEGI de quelques documents, au schéma de ``dila_index.py`` :
    le décret n° 2016-604, trois versions de son article 1er, son article 3 et
    un tableau de reclassement ; un décret de l'État, qui ne compte pas."""
    dila = _charger("dila_index")
    chemin = tmp_path / "legi.sqlite"
    db = dila.ouvrir(chemin)
    titre = ("Décret n° 2016-604 du 12 mai 2016 fixant les différentes échelles de "
             "rémunération pour les fonctionnaires de catégorie C de la fonction publique "
             "territoriale")
    v2018 = C_TERRITORIALE_2017.replace(
        "1er janvier 2018 A compter du 1er janvier 2019 A compter du 1er janvier 2020",
        "1er janvier 2019 A compter du 1er janvier 2020 A compter du 1er janvier 2021")
    lignes = [
        ("LEGITEXT000032545071", "2017-01-01", EN, "DECRET", "", titre, "Le Premier ministre…"),
        ("LEGIARTI000032545076", "2017-01-01", "2018-01-01", "Article DECRET", "1", titre,
         C_TERRITORIALE_2017),
        ("LEGIARTI000036490555", "2018-01-01", "2022-01-01", "Article DECRET", "1", titre, v2018),
        ("LEGIARTI000044811902", "2022-01-01", EN, "Article DECRET", "1", titre,
         C_TERRITORIALE_2022),
        ("LEGIARTI000032545080", "2017-01-01", EN, "Article DECRET", "3", titre,
         "Le présent décret entre en vigueur au 1er janvier 2017."),
        ("LEGIARTI000099999999", "2017-01-01", EN, "Article DECRET", "5", titre,
         "Les fonctionnaires sont reclassés conformément au tableau suivant : SITUATION "
         "ACTUELLE 5e échelon 380 SITUATION NOUVELLE 4e échelon 390 ancienneté acquise"),
        ("LEGITEXT000022752205", "2010-09-01", EN, "DECRET", "",
         "Décret n° 2010-1007 du 26 août 2010 fixant l'échelonnement indiciaire des "
         "personnels enseignants", "…"),
    ]
    db.executemany("INSERT INTO doc VALUES (?,?,?,?,?,?,?)", lignes)
    db.execute("INSERT INTO meta VALUES ('dump', 'Freemium_legi_global_20250713-140000.tar.gz')")
    db.execute("INSERT INTO meta VALUES ('dernier_increment', '20261102-213929')")
    db.commit()
    db.close()
    return chemin


def test_l_extraction_ecrit_les_textes_les_grilles_les_echelons_et_les_refus(index, tmp_path):
    extrait = grilles.extraire(index)
    fpt = extrait["territoriale"]
    assert extrait["hospitaliere"]["textes"] == []
    (texte,) = fpt["textes"]
    assert texte == {"texte": "LEGITEXT000032545071", "numero": "2016-604", "nature": "DECRET",
                     "signature": "2016-05-12", "debut": "2017-01-01", "fin": "",
                     "titre": texte["titre"], "articles_lus": "3", "articles_non_lus": "1"}
    assert [g["grille"] for g in fpt["grilles"]] == ["echelle-c1", "echelle-c2", "echelle-c3"]
    c3 = {g["grille"]: g for g in fpt["grilles"]}["echelle-c3"]
    assert (c3["libelle"], c3["debut"], c3["fin"], c3["echelons"]) == (
        "Echelle C3", "2017-01-01", "", "10")
    premier = [(e["debut"], e["fin"], e["indice"], e["article"]) for e in fpt["echelons"]
               if e["grille"] == "echelle-c3" and e["echelon"] == "1"]
    assert premier == [("2017-01-01", "2018-12-31", "374", "LEGIARTI000032545076"),
                       ("2019-01-01", "2021-12-31", "380", "LEGIARTI000036490555"),
                       ("2022-01-01", "", "388", "LEGIARTI000044811902")]
    (refus,) = fpt["non_lus"]
    assert (refus["article"], refus["motif"]) == ("LEGIARTI000099999999",
                                                  "tableau de reclassement, pas une grille")
    brut = grilles.brut(extrait, source="essai")
    assert brut["territoriale"]["indice"]["LEGITEXT000032545071|echelle-c3|1|2022-01-01"] == 388
    assert brut["territoriale"]["rang"]["LEGITEXT000032545071|echelle-c3|1|2022-01-01"] == 1
    assert brut["hospitaliere"]["indice"] == {}

    grilles.ecrire_reference(extrait, tmp_path / "grilles")
    with (tmp_path / "grilles" / "territoriale" / "echelons.csv").open(encoding="utf-8") as flux:
        entete = [l for l in flux if l.startswith("#")]
    assert any("source_id: dila_legi_grilles" in l for l in entete)


def _lire_csv(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def _charger_verifier():
    chemin = RACINE / "scripts" / "verifier_donnees.py"
    specification = importlib.util.spec_from_file_location("verifier_donnees", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["verifier_donnees"] = module
    specification.loader.exec_module(module)
    return module


def test_verifier_donnees_certifie_le_rang_et_l_indice_des_echelons(index, tmp_path, monkeypatch):
    """La certification relit le fichier brut du récupérateur : le rang et
    l'indice de chaque période lue passent ``certifiee``, ceux d'une période
    dont la colonne est présumée ``estimee`` ; aucune ligne ne bouge."""
    import dataclasses
    import json

    verifier = _charger_verifier()
    monkeypatch.setattr(verifier, "BRUT", tmp_path)
    extrait = grilles.extraire(index)
    # Une période présumée, pour que les quatre séries aient à dire.
    presumee = dict(extrait["territoriale"]["echelons"][0], lecture="presumee",
                    debut="2016-01-01", fin="2016-12-31")
    extrait["territoriale"]["echelons"].append(presumee)
    (tmp_path / "dila_legi_grilles.json").write_text(
        json.dumps(grilles.brut(extrait, source="essai")), encoding="utf-8")
    dossier = tmp_path / "grilles"
    grilles.ecrire_reference(extrait, dossier)
    chemin = dossier / "territoriale" / "echelons.csv"
    ordre = [grilles._cle_echelon(l) for l in _lire_csv(chemin)]

    certifications = [c for c in verifier.CERTIFICATIONS
                      if c.nom.startswith(("grilles_territoriale_", "grilles_hospitaliere_"))]
    assert sorted(c.nom for c in certifications) == sorted(
        f"grilles_{versant}_{serie}" for versant in ("territoriale", "hospitaliere")
        for serie in ("rang", "indice", "rang_presume", "indice_presume"))
    for certification in certifications:
        versant = certification.chemin.parent.name
        assert certification.chemin == RACINE / "data" / "reference" / "grilles" / versant / \
            "echelons.csv"
        messages, trace = dataclasses.replace(
            certification, chemin=dossier / versant / "echelons.csv").confronter(appliquer=True)
        assert messages[0].startswith(("OK", "RIEN")), messages
        if trace:
            assert trace["corrigees"] == trace["ajoutees"] == 0, messages
    certifie = _lire_csv(chemin)
    assert {(l["lecture"], l["fiabilite"]) for l in certifie} == {
        ("", "certifiee"), ("presumee", "estimee")}
    assert [grilles._cle_echelon(l) for l in certifie] == ordre


# ---------------------------------------------------------------------------
# La donnée, confrontée à des grilles publiées
# ---------------------------------------------------------------------------

GRILLES = RACINE / "data" / "reference" / "grilles"


def _en_vigueur(lignes: list[dict[str, str]], le: str) -> list[dict[str, str]]:
    return [l for l in lignes if l["debut"] <= le and (not l["fin"] or le <= l["fin"])]


def _indices(versant: str, texte: str, grille: str, le: str) -> list[int]:
    """Les indices bruts d'une grille à une date, du 1er échelon au dernier."""
    lignes = [l for l in _en_vigueur(_lire_csv(GRILLES / versant / "echelons.csv"), le)
              if l["texte"] == texte and l["grille"] == grille]
    assert all(l["fiabilite"] == "certifiee" for l in lignes), grille
    return [int(l["indice"]) for l in sorted(lignes, key=lambda l: int(l["rang"]))]


def _bareme(le: str) -> dict[int, int]:
    """Le barème de l'indice brut à l'indice majoré à une date, celui du Noyau RH
    (``grilles/etat/indices.csv``), commun aux trois versants."""
    return {int(l["indice_brut"]): int(l["indice_majore"])
            for l in _en_vigueur(_lire_csv(GRILLES / "etat" / "indices.csv"), le)}


def _suite(texte: str) -> list[int]:
    return [int(n) for n in texte.split()]


#: « Échelles de rémunération de catégorie C, à compter du 1er janvier 2024 »,
#: centre de gestion de la fonction publique territoriale du Nord (cdg59.fr,
#: echelles_de_remunération_de_categorie_C_au_01-01-2022.pdf, lu le
#: 3 novembre 2026), page 1 pour les échelles C1 à C3 des décrets n° 2016-596 et
#: 2016-604, page 2 pour les agents de maîtrise du décret n° 88-548 : par
#: échelon, l'indice brut en vigueur depuis le 1er janvier 2022, puis l'indice
#: majoré au 1er janvier 2022, au 1er juillet 2023 et au 1er janvier 2024
#: (décret n° 2023-519). Le minimum de traitement, que ses renvois rappellent,
#: n'y est pas porté.
CDG59 = {
    ("LEGITEXT000032545071", "echelle-c1"): (
        "367 368 370 371 374 378 381 387 401 419 432",
        "340 341 342 343 345 348 351 354 363 372 382",
        "361 362 363 364 365 366 367 368 371 372 382",
        "366 367 368 369 370 371 372 373 376 377 387"),
    ("LEGITEXT000032545071", "echelle-c2"): (
        "368 371 376 387 396 404 416 430 446 461 473 486",
        "341 343 346 354 360 365 370 380 392 404 412 420",
        "362 364 365 368 369 371 372 380 392 404 412 420",
        "367 369 370 373 374 376 377 385 397 409 417 425"),
    ("LEGITEXT000032545071", "echelle-c3"): (
        "388 397 412 430 448 460 478 499 525 558",
        "355 361 368 380 393 403 415 430 450 473",
        "368 370 371 380 393 403 415 430 450 473",
        "373 375 376 385 398 408 420 435 455 478"),
    ("LEGITEXT000006066666", "agent-de-maitrise"): (
        "372 375 380 388 397 415 437 449 465 479 499 525 562",
        "343 346 350 355 361 369 385 394 407 416 430 450 476",
        "364 365 366 368 370 372 385 394 407 416 430 450 476",
        "369 370 371 373 375 377 390 399 412 421 435 455 481"),
    ("LEGITEXT000006066666", "agent-de-maitrise-principal"): (
        "390 400 420 446 468 492 505 526 563 597",
        "357 363 373 392 409 425 435 451 477 503",
        "368 371 373 392 409 425 435 451 477 503",
        "373 376 378 397 414 430 440 456 482 508"),
}


@pytest.mark.parametrize("texte, grille", sorted(CDG59))
def test_la_territoriale_recompose_les_indices_que_le_centre_de_gestion_publie(texte, grille):
    bruts, majores_2022, majores_2023, majores_2024 = (_suite(s) for s in CDG59[(texte, grille)])
    for le in ("2022-01-01", "2024-01-01"):
        assert _indices("territoriale", texte, grille, le) == bruts, le
    for le, majores in (("2022-01-01", majores_2022), ("2023-07-01", majores_2023),
                        ("2024-01-01", majores_2024)):
        bareme = _bareme(le)
        assert [bareme[b] for b in bruts] == majores, le


#: Fédération UNSA Santé et Sociaux, « Fonction publique hospitalière,
#: personnel stagiaire et titulaire », mise à jour du 25 janvier 2022
#: (unsa-fp.org, 621f3a437b917.pdf, lu le 3 novembre 2026), « valeur Indice
#: Majoré 4.6860 € » : par échelon, du premier au dernier, l'indice majoré
#: payé — les échelles C1 à C3 « Situation au 01 01 2022 » (pages 2 et 3), les
#: deux grades des aides-soignants « Situation au 01 10 2021 » (page 4).
UNSA = {
    ("2022-01-01", "LEGITEXT000044635475", "echelle-c1"):
        "343 343 343 343 345 348 351 354 363 372 382",
    ("2022-01-01", "LEGITEXT000044635475", "echelle-c2"):
        "343 343 346 354 360 365 370 380 392 404 412 420",
    ("2022-01-01", "LEGITEXT000044635475", "echelle-c3"):
        "355 361 368 380 393 403 415 430 450 473",
    ("2021-10-01", "LEGITEXT000044131693",
     "classe-normale-du-corps-des-aides-soignants-et-des-auxiliaires-de-puericulture"):
        "343 350 359 370 383 396 409 424 439 456 480 512",
    ("2021-10-01", "LEGITEXT000044131693",
     "classe-superieure-du-corps-des-aides-soignants-et-des-auxiliaires-de-puericulture"):
        "382 394 406 419 437 455 475 494 514 534 555",
}
#: Le minimum de traitement : l'indice majoré 340 du 1er octobre 2021, 343 du
#: 1er janvier 2022 (décret n° 85-1148, article 8, versions LEGIARTI000044129999
#: et LEGIARTI000044617596, cette dernière écrite par le décret n° 2021-1749).
MINIMUM = {"2021-10-01": 340, "2022-01-01": 343}


@pytest.mark.parametrize("le, texte, grille", sorted(UNSA))
def test_l_hospitaliere_recompose_les_indices_que_la_federation_publie(le, texte, grille):
    bareme = _bareme(le)
    payes = [max(bareme[b], MINIMUM[le]) for b in _indices("hospitaliere", texte, grille, le)]
    assert payes == _suite(UNSA[(le, texte, grille)])


def test_le_point_de_la_federation_est_celui_du_depot():
    chemin = RACINE / "data" / "reference" / "legislation" / "point_indice_fonction_publique.csv"
    point = {int(l["annee"]): float(l["valeur"]) for l in _lire_csv(chemin)}
    assert round(point[2022] / 12, 4) == 4.6860


def test_la_grille_de_2017_des_ieeac_est_celle_du_decret_2018_610():
    """Décret n° 2009-1322, article 2 : le LEGI garde en vigueur ensemble, du
    2017-01-01 au 2018-01-01, la version que le décret n° 2017-171 écrit (art. 39,
    « en vigueur le 1er janvier 2017 », art. 126) et celle du décret n° 2018-610 du
    12 juillet 2018, qui « remplace » l'article (art. 1er) et « entre en vigueur le
    1er janvier 2017 » (art. 2). En 2017, la classe normale est celle du n° 2018-610,
    colonne « Au 1er janvier 2017 » : 2e 483, 3e 508, 4e 525, 5e 565, 6e 610, 7e 649,
    8e 686, 9e 727, 10e 744, 11e 774 ; son « 1er » (434) est au grade d'ingénieur
    stagiaire. Rien ne reste du n° 2017-171 : ni le 1er échelon à 421, ni sa hors
    classe (971, 1021, HEA). Le Noyau RH porte les mêmes indices (grille 03500)."""
    lignes = _lire_csv(GRILLES / "etat_legi" / "echelons.csv")
    assert not [l for l in lignes if l["article"] == "LEGIARTI000034034492"]
    normale = sorted((int(l["rang"]), int(l["indice"]), l["article"])
                     for l in _en_vigueur(lignes, "2017-06-30")
                     if l["texte"] == "LEGITEXT000021214923" and l["grille"] ==
                     "ingenieur-des-etudes-et-de-l-exploitation-de-l-aviation-civile-de-classe-normale")
    assert normale == [(rang, indice, "LEGIARTI000037196211") for rang, indice in
                       zip(range(2, 12), (483, 508, 525, 565, 610, 649, 686, 727, 744, 774))]


def _grille(versant: str, texte: str, grille: str, le: str) -> list[tuple[str, str, str]]:
    """(échelon, indice ou lettre, article) d'une grille à une date, triés par rang."""
    lignes = [l for l in _en_vigueur(_lire_csv(GRILLES / versant / "echelons.csv"), le)
              if l["texte"] == texte and l["grille"] == grille]
    return [(l["echelon"], l["indice"] or l["hors_echelle"], l["article"])
            for l in sorted(lignes, key=lambda l: int(l["rang"]))]


def test_les_secretaires_de_mairie_changent_de_grille_au_1er_aout_1995():
    """Décret n° 87-1104, article 1er : le décret n° 96-101 du 6 février 1996 remplace
    son tableau (art. 3), et « prennent effet au 1er août 1995 » ses articles 2 (I à
    XII), 3, 17, 18, 37 et 38 (art. 39, II), lus à Légifrance le 5 novembre 2026. Le
    LEGI garde pourtant l'ancienne version jusqu'au 8 février 1996, sa date de
    publication : ses trois échelons provisoires, 274, 301 et 328, y survivaient six
    mois à côté de la grille à douze échelons."""
    texte, grille = "LEGITEXT000006065788", "secretaires-de-mairie"
    assert [(e, i) for e, i, _ in _grille("etat_legi", texte, grille, "1995-07-31")
            if "provisoire" in e] == [
        ("1-provisoire", "274"), ("2-provisoire", "301"), ("3-provisoire", "328")]
    assert [i for _, i, _ in _grille("etat_legi", texte, grille, "1995-08-01")] == [
        "374", "410", "435", "461", "481", "504", "535", "566", "597", "628", "660", "695"]


def test_la_grille_du_chef_de_projet_sric_de_2016_cesse_au_1er_janvier_2017():
    """Décret n° 2008-836, article 14-1-1 (le chef de projet en systèmes et réseaux
    d'information et de communication) : le LEGI garde la version du décret n° 2016-82
    (art. 1er, JORFARTI000031942010 ; « Le présent décret entre en vigueur le 1er février
    2016. », art. 3) en vigueur jusqu'au 2017-02-13, à côté de celle qui vaut dès le
    2017-01-01 : le tableau que le décret n° 2017-171 « remplace » (art. 8,
    JORFARTI000034026698 ; en vigueur le 1er janvier 2017, art. 126), dont le décret
    n° 2017-1381 change la seule ligne « 10 HEA HEA » en « ES HEA HEA » (art. 2,
    JORFARTI000035600863 ; « Les dispositions du présent décret entrent en vigueur le 1er
    janvier 2017. », art. 7). La grille du n° 2016-82 vaut jusqu'au 31 décembre 2016 ;
    le 15 janvier 2017, celle du n° 2017-171, colonne « A compter du 1er janvier 2017 »,
    avec la ligne « ES HEA HEA » du n° 2017-1381 : neuf échelons, 656 à 1021, puis
    l'échelon spécial, à HEA, que le n° 2016-82 écrit « Echelon spécial HEA » ; « ES »
    n'est pas un bout du nom de la grille."""
    texte = "LEGITEXT000019373379"
    ancienne = ("fonctionnaires-detaches-sur-l-emploi-de-chef-de-projet-en-systemes-et-reseaux-"
                "d-information-et-de-communication-des-administrations-de-l-etat")
    assert [i for _, i, _ in _grille("etat_legi", texte, ancienne, "2016-12-31")] == [
        "650", "700", "750", "800", "850", "901", "946", "985", "1015", "A"]
    assert _grille("etat_legi", texte, ancienne, "2017-01-01") == []
    nouvelle = ("chef-de-projet-en-systemes-et-reseaux-d-information-et-de-communication-des-"
                "administrations-de-l-etat")
    assert [(e, i) for e, i, _ in _grille("etat_legi", texte, nouvelle, "2017-01-15")] == [
        ("1", "656"), ("2", "705"), ("3", "755"), ("4", "805"), ("5", "855"), ("6", "906"),
        ("7", "951"), ("8", "990"), ("9", "1021"), ("special", "A")]
    assert _grille("etat_legi", texte, nouvelle + "-es-hea-hea", "2017-01-15") == []


#: Décret n° 2012-1058, article 4 (chargés et directeurs de recherche du
#: développement durable), lu au JORF le 5 novembre 2026 : le décret n° 2017-171
#: le remplace (art. 36, JORFARTI000034026745), en vigueur le 1er janvier 2017
#: (art. 126) ; le décret n° 2018-917 du 25 octobre 2018 (art. 1er,
#: JORFARTI000037532992) : « I.-Au 1er janvier 2017, la rubrique relative aux chargés
#: de recherche du tableau figurant à l'article 4 […] est remplacée par le tableau
#: suivant » ; « II.-Au 1er septembre 2017, le tableau figurant à l'article 4 […] est
#: remplacé par les tableaux suivants ».
DD = "LEGITEXT000026383946"


def test_les_chercheurs_du_developpement_durable_en_2017_suivent_le_decret_2018_917():
    """Du 1er janvier au 31 août 2017 : les chargés de recherche, au tableau du I du
    n° 2018-917 (1re classe : 574, 612, 690, 767, 833, 894, 933, 978, 1021 ; 2e classe :
    544, 554, 592, 629, 664, 690), non à celui du n° 2017-171 (567… ; 539…), qui ne vaut
    à aucune date ; le directeur de recherche de 2e classe, à la colonne « A compter du
    1er janvier 2017 » du n° 2017-171 (807, 857, 906, 962, 1021, HEA), sans le 7e échelon
    ni le 963 que le LEGI tient du II (LEGIARTI000037538214). Dès le 1er septembre 2017,
    le tableau du II seul : ni chargé de recherche de 1re ou de 2e classe, et le directeur
    de recherche de 2e classe a son 7e échelon (HEB) et un 4e à 963."""
    le = "2017-06-30"
    premiere = "charges-de-recherche-charge-de-recherche-de-1re-classe"
    seconde = "charge-de-recherche-de-2e-classe"
    assert [i for _, i, _ in _grille("etat_legi", DD, premiere, le)] == [
        "574", "612", "690", "767", "833", "894", "933", "978", "1021"]
    assert [i for _, i, _ in _grille("etat_legi", DD, seconde, le)] == [
        "544", "554", "592", "629", "664", "690"]
    dr2 = "directeur-de-recherche-de-2e-classe"
    assert [(e, i) for e, i, _ in _grille("etat_legi", DD, dr2, le)] == [
        ("1", "807"), ("2", "857"), ("3", "906"), ("4", "962"), ("5", "1021"), ("6", "A")]
    for grille in (premiere, seconde,
                   "directeurs-de-recherche-directeur-de-recherche-de-classe-exceptionnelle"):
        assert _grille("etat_legi", DD, grille, "2017-09-01") == []
    assert [(e, i) for e, i, _ in _grille("etat_legi", DD, dr2, "2017-09-01")] == [
        ("1", "807"), ("2", "857"), ("3", "906"), ("4", "963"), ("5", "1021"), ("6", "A"),
        ("7", "B")]
