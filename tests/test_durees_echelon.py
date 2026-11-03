"""La durée de chaque échelon des grilles, lue au LEGI (action 158).

Les statuts fixent, grade par grade, le temps à passer dans chaque échelon
avant le suivant : une durée unique depuis 2017, une durée moyenne et une
durée minimale à l'État auparavant, une durée maximale et une durée minimale
à la territoriale. L'index LEGI du dépôt garde ces tableaux aplatis — une
suite d'échelons et de durées, sans les cases —, et
``scripts/fetch/dila_legi_durees.py`` les relit. Les textes des tests sont
ceux des articles du LEGI, recopiés ; les valeurs attendues, lues dans ces
mêmes articles, à la main, et non dans ce que rend le script.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))

import dila_legi_durees as dur  # noqa: E402

DOSSIER = RACINE / "data" / "reference" / "grilles" / "durees"

#: Décret n° 92-1436 du 30 décembre 1992, statut particulier des techniciens
#: sanitaires (État), article 11, version du 31 décembre 1992 au 1er août 1993
#: (LEGIARTI000006470031) : une durée moyenne et une durée minimale, après une
#: phrase qui renvoie à un autre décret.
TECHNICIENS_SANITAIRES = (
    "La durée moyenne et la durée minimale du temps passé dans chacun des échelons du grade de "
    "technicien sanitaire sont fixées à l'article 4 du décret du 20 septembre 1973 susvisé. La "
    "durée moyenne et la durée minimale du temps passé dans chacun des échelons des grades de "
    "technicien principal et de technicien en chef sont fixées ainsi qu'il suit : ÉCHELONS DURÉE "
    "Moyenne Minimale 6e échelon. 4 ans 3 ans 5e échelon. 3 ans 6 mois 2 ans 9 mois 4e échelon. "
    "3 ans 6 mois 2 ans 9 mois 3e échelon. 3 ans 2 ans 3 mois 2e échelon. 3 ans 2 ans 3 mois 1er "
    "échelon. 3 ans 2 ans 3 mois")

#: Décret n° 83-1260 du 30 décembre 1983, corps des EPST (État), article 91,
#: version du 1er septembre 2017 au 1er janvier 2021 (LEGIARTI000034794372) :
#: la durée unique, deux grades ; l'échelon le plus haut n'a pas de durée.
INGENIEURS_D_ETUDES = (
    "La durée du temps passé dans chacun des échelons du corps des ingénieurs d'études est fixée "
    "conformément au tableau ci-après : GRADES ET ÉCHELONS DURÉE Ingénieur d'études hors classe "
    "9e échelon 8e échelon 3 ans 7e échelon 2 ans 6 mois 6e échelon 2 ans 6 mois 5e échelon 2 ans "
    "6 mois 4e échelon 2 ans 6 mois 3e échelon 2 ans 6 mois 2e échelon 2 ans 1er échelon 2 ans "
    "Ingénieur d'études de classe normale 14e échelon 13e échelon 3 ans 12e échelon 2 ans 11e "
    "échelon 2 ans 10e échelon 2 ans 9e échelon 2 ans 8e échelon 2 ans 7e échelon 1 an 6 mois 6e "
    "échelon 1 an 6 mois 5e échelon 1 an 6 mois 4e échelon 1 an 6 mois 3e échelon 1 an 6 mois 2e "
    "échelon 1 an 6 mois 1er échelon 1 an")

#: Décret n° 93-145 du 3 février 1993, personnels techniques de l'Assistance
#: publique-hôpitaux de Paris (hospitalière), article 6, version du
#: 1er janvier 2017 au 19 novembre 2018 (LEGIARTI000037623011) : le plus haut
#: échelon marqué d'un tiret.
INGENIEURS_HOSPITALIERS = (
    "Conformément aux dispositions de l'article 41 du décret n° 2018-999 du 16 novembre 2018 : "
    "Le décret n° 93-145 du 3 février 1993 portant statuts particuliers des personnels techniques "
    "de la catégorie A de l'Assistance publique-hôpitaux de Paris est abrogé. Ses dispositions "
    "restent en vigueur à seule fin de mettre en œuvre les opérations résultant du titre Ier. La "
    "durée du temps passé dans chacun des échelons des différents grades est fixée ainsi qu'il "
    "suit : GRADES ET ÉCHELONS DURÉES Ingénieur hospitalier en chef de classe exceptionnelle 7e "
    "échelon - 6e échelon 3 ans 6 mois 5e échelon 3 ans 4e échelon 2 ans 6 mois 3e échelon 2 ans "
    "6 mois 2e échelon 2 ans 1er échelon 2 ans Ingénieur hospitalier en chef de classe normale "
    "10e échelon - 9e échelon 3 ans 6 mois 8e échelon 3 ans 6 mois 7e échelon 3 ans 6e échelon "
    "2 ans 6 mois 5e échelon 2 ans 6 mois 4e échelon 2 ans 3e échelon 2 ans 6 mois 2e échelon "
    "1 an 6 mois 1er échelon 1 an Ingénieur hospitalier principal 8e échelon - 7e échelon 3 ans "
    "6e échelon 3 ans 5e échelon 3 ans 4e échelon 3 ans 3e échelon 3 ans 2e échelon 2 ans 6 mois "
    "1er échelon 2 ans Ingénieur hospitalier 10e échelon - 9e échelon 4 ans 8e échelon 4 ans 7e "
    "échelon 4 ans 6e échelon 4 ans 5e échelon 3 ans 4e échelon 2 ans 6 mois 3e échelon 2 ans 2e "
    "échelon 2 ans 1er échelon 1 an 6 mois")

#: Décret n° 2008-952 du 12 septembre 2008, sous-officiers de gendarmerie,
#: article 6-1, version du 5 janvier 2013 au 1er janvier 2019
#: (LEGIARTI000026912312) : les échelons sans le mot « échelon », le plus haut
#: barré, et une phrase qui suit le tableau.
GENDARMES = (
    "Les conditions d'accès aux échelons du grade de gendarme sont déterminées conformément au "
    "tableau suivant : GRADE ÉCHELLE DE SOLDE ÉCHELON ANCIENNETÉ EXIGÉE dans l'échelon pour "
    "accéder à l'échelon supérieur Gendarme Echelle de solde spécifique des gendarmes 13e / 12e "
    "3 ans 11e 2 ans et six mois 10e 2 ans et six mois 9e 2 ans et six mois 8e 2 ans et six mois "
    "7e 2 ans et six mois 6e 2 ans et six mois 5e 2 ans et six mois 4e 2 ans 3e 2 ans 2e 2 ans "
    "1er 2 ans Les gendarmes, qui ont eu auparavant la qualité de volontaire dans les armées ou "
    "d'adjoint de sécurité recruté en application de l' article 36 de la loi n° 95-73 du "
    "21 janvier 1995 d'orientation et de programmation relative à la sécurité, sont classés, lors "
    "de leur nomination au grade de gendarme, avec une reprise d'ancienneté égale aux trois "
    "quarts des services accomplis en cette qualité.")


def _un_tableau(article: str) -> dur.Tableau:
    extraits = dur.tableaux(article)
    assert len(extraits) == 1, [e.intro for e in extraits]
    return dur.lire_tableau(extraits[0])


def _durees(tableau: dur.Tableau, colonne: str) -> dict[tuple[str, str], int | None]:
    return {(l.groupe, l.echelon): getattr(l, colonne) for l in tableau.lignes}


def test_une_duree_se_compte_en_mois():
    assert dur.mois("3 ans 6 mois") == 42
    assert dur.mois("2 ans et six mois") == 30
    assert dur.mois("1 an et 6 mois") == 18
    assert dur.mois("un an et demi") == 18
    assert dur.mois("18 mois") == 18
    assert dur.mois("deux ans") == 24


def test_la_duree_moyenne_et_la_duree_minimale_de_l_etat():
    tableau = _un_tableau(TECHNICIENS_SANITAIRES)
    assert not tableau.refus
    assert tableau.colonnes == ("moyenne", "minimale")
    moyenne = _durees(tableau, "duree_moyenne")
    minimale = _durees(tableau, "duree_minimale")
    assert moyenne == {("", "6"): 48, ("", "5"): 42, ("", "4"): 42, ("", "3"): 36,
                       ("", "2"): 36, ("", "1"): 36}
    assert minimale == {("", "6"): 36, ("", "5"): 33, ("", "4"): 33, ("", "3"): 27,
                        ("", "2"): 27, ("", "1"): 27}


def test_la_duree_unique_grade_par_grade():
    tableau = _un_tableau(INGENIEURS_D_ETUDES)
    assert not tableau.refus
    assert tableau.colonnes == ("unique",)
    hc, cn = "Ingénieur d'études hors classe", "Ingénieur d'études de classe normale"
    durees = _durees(tableau, "duree")
    assert durees[(hc, "9")] is None and durees[(cn, "14")] is None
    assert [durees[(hc, str(e))] for e in range(8, 0, -1)] == [36, 30, 30, 30, 30, 30, 24, 24]
    assert [durees[(cn, str(e))] for e in range(13, 0, -1)] == [
        36, 24, 24, 24, 24, 24, 18, 18, 18, 18, 18, 18, 12]
    assert len(tableau.lignes) == 9 + 14


def test_le_plus_haut_echelon_marque_d_un_tiret():
    tableau = _un_tableau(INGENIEURS_HOSPITALIERS)
    assert not tableau.refus
    durees = _durees(tableau, "duree")
    exc = "Ingénieur hospitalier en chef de classe exceptionnelle"
    assert durees[(exc, "7")] is None
    assert [durees[(exc, str(e))] for e in range(6, 0, -1)] == [42, 36, 30, 30, 24, 24]
    assert [durees[("Ingénieur hospitalier", str(e))] for e in range(9, 0, -1)] == [
        48, 48, 48, 48, 36, 30, 24, 24, 18]
    assert len({l.groupe for l in tableau.lignes}) == 4


def test_les_echelons_des_militaires_sans_le_mot_echelon():
    tableau = _un_tableau(GENDARMES)
    assert not tableau.refus
    durees = _durees(tableau, "duree")
    groupe = "Gendarme Echelle de solde spécifique des gendarmes"
    assert durees[(groupe, "13")] is None
    assert [durees[(groupe, str(e))] for e in range(12, 0, -1)] == [
        36, 30, 30, 30, 30, 30, 30, 30, 24, 24, 24, 24]
    assert len(tableau.lignes) == 13          # la phrase qui suit n'est pas une ligne


#: Décret n° 56-448 du 30 avril 1956, corps du service de dessin des postes,
#: télégraphes et téléphones (État), article 9, en vigueur depuis le
#: 29 février 2016 (LEGIARTI000032192685) : plusieurs échelons d'une même durée
#: sur une ligne.
DESSINATEURS = (
    "La durée du temps passé dans chacun des échelons du grade de dessinateur-projeteur et de "
    "chef dessinateur est fixée ainsi qu'il suit : ÉCHELONS DURÉE Dessinateur-projeteur 14e "
    "échelon 3 ans 13e échelon 4 ans 7e, 8e, 9e, 10e, 11e et 12e échelons 3 ans 6e échelon 2 ans "
    "2e, 3e, 4e et 5e échelons 1 an 6 mois 1er échelon 1 an Chef dessinateur 2e, 3e, 4e, 5e, 6e "
    "et 7e échelons 3 ans 1er échelon 2 ans .")


def test_plusieurs_echelons_d_une_meme_duree():
    tableau = _un_tableau(DESSINATEURS)
    assert not tableau.refus
    durees = _durees(tableau, "duree")
    assert [durees[("Dessinateur-projeteur", str(e))] for e in range(14, 0, -1)] == [
        36, 48, 36, 36, 36, 36, 36, 36, 24, 18, 18, 18, 18, 12]
    assert [durees[("Chef dessinateur", str(e))] for e in range(7, 0, -1)] == [
        36, 36, 36, 36, 36, 36, 24]


#: Décret n° 95-952 du 25 août 1995, cadre d'emplois des contrôleurs de travaux
#: (territoriale), article 17, version du 3 février 2004 au 1er décembre 2010
#: (LEGIARTI000006377526), son début, jusqu'au premier grade : « 2 ans 9mois »,
#: sans espace.
CONTROLEURS = (
    "La durée maximale et la durée minimale du temps passé dans chacun des échelons des grades "
    "sont fixées ainsi qu'il suit : GRADES ET ECHELONS DUREES Maximale Minimale Contrôleur en "
    "chef 8e échelon - - 7e échelon 4 ans 3 ans 6e échelon 3 ans 6 mois 2 ans 9mois 5e échelon "
    "2 ans 6 mois 2 ans 4e échelon 2 ans 6 mois 2 ans 3e échelon 2 ans 1 an 6 mois 2e échelon "
    "2 ans 1 an 6 mois 1er échelon 1 an 6 mois 1 an 6 mois")

#: Décret n° 95-83 du 19 janvier 1995, article 32 (LEGIARTI000006476831) : le
#: plus haut échelon dit « Echelon terminal » dans ses deux cases, et une
#: phrase suit le tableau.
TERMINAL = (
    "Les agents appartenant au grade provisoire peuvent bénéficier d'une réduction de la durée "
    "moyenne d'échelon dans les conditions fixées à l'article 118 du décret du 30 décembre 1983 "
    "susvisé : ÉCHELONS DURÉE Moyenne Minimale 7e échelon Echelon terminal Echelon terminal 6e "
    "échelon 3 ans 2 ans 6 mois 5e échelon 3 ans 2 ans 6 mois 4e échelon 2 ans 6 mois 2 ans 3e "
    "échelon 2 ans 6 mois 2 ans 2e échelon 2 ans 1 an 6 mois 1er échelon 2 ans 1 an 6 mois Sont "
    "intégrés, au 1er août 1994, dans ce grade provisoire, les techniciens de la recherche de 1re "
    "classe qui n'ont pas bénéficié des dispositions de l'article 31 ci-dessus.")

#: Décret n° 98-1262 du 29 décembre 1998, personnels de l'Office national des
#: forêts, article 32, du 1er janvier 1999 au 1er janvier 2017
#: (LEGIARTI000006509643) : des échelons groupés au singulier (« 2e ,3e et 4e
#: échelon »), dans l'ordre croissant.
ONF = (
    "La durée moyenne et la durée minimale du temps passé dans chaque échelon sont fixées ainsi "
    "qu'il suit : CLASSES, ECHELONS DUREE Moyenne Minimale Hors-classe 1er échelon 2 ans 6 mois "
    "2 ans 2e et 3e échelon 3 ans 2 ans 3 mois 1re classe 1er échelon 1 an 1 an 2e ,3e et 4e "
    "échelon 2 ans 6 mois 2 ans 5e échelon 3 ans 2 ans 3 mois 2e classe 1er et 2e échelon 1 an "
    "1 an 3e ,4e et 5e échelon 2 ans 1 an 6 mois 6e échelon 2 ans 6 mois 2 ans 7e, 8e ,9e et 10e "
    "échelon 3 ans 2 ans 3 mois 11e échelon 4 ans 3 ans")


def test_une_duree_sans_espace_avant_mois():
    tableau = _un_tableau(CONTROLEURS)
    assert not tableau.refus
    assert tableau.colonnes == ("maximale", "minimale")
    chef = "Contrôleur en chef"
    maxi, mini = _durees(tableau, "duree_maximale"), _durees(tableau, "duree_minimale")
    assert [maxi[(chef, str(e))] for e in range(8, 0, -1)] == [None, 48, 42, 30, 30, 24, 24, 18]
    assert [mini[(chef, str(e))] for e in range(8, 0, -1)] == [None, 36, 33, 24, 24, 18, 18, 18]
    assert {l.groupe for l in tableau.lignes} == {chef}


def test_echelon_terminal_n_est_pas_un_grade():
    tableau = _un_tableau(TERMINAL)
    assert not tableau.refus
    assert {l.groupe for l in tableau.lignes} == {""}
    moy, mini = _durees(tableau, "duree_moyenne"), _durees(tableau, "duree_minimale")
    assert [moy[("", str(e))] for e in range(7, 0, -1)] == [None, 36, 36, 30, 30, 24, 24]
    assert [mini[("", str(e))] for e in range(7, 0, -1)] == [None, 30, 30, 24, 24, 18, 18]


def test_echelons_groupes_au_singulier_dans_l_ordre_croissant():
    tableau = _un_tableau(ONF)
    assert not tableau.refus
    moy, mini = _durees(tableau, "duree_moyenne"), _durees(tableau, "duree_minimale")
    assert [moy[("Hors-classe", str(e))] for e in (1, 2, 3)] == [30, 36, 36]
    assert [mini[("1re classe", str(e))] for e in range(1, 6)] == [12, 24, 24, 24, 27]
    assert [moy[("2e classe", str(e))] for e in range(1, 12)] == [
        12, 12, 24, 24, 24, 30, 36, 36, 36, 36, 48]
    assert [mini[("2e classe", str(e))] for e in range(1, 12)] == [
        12, 12, 18, 18, 18, 24, 27, 27, 27, 27, 36]


#: Décret n° 92-867 du 28 août 1992, cadre d'emplois des biologistes,
#: vétérinaires et pharmaciens territoriaux, article 11, en vigueur depuis le
#: 1er janvier 2017 (LEGIARTI000034434471) : la phrase qui suit le tableau nomme
#: un échelon.
BIOLOGISTES = (
    "La durée du temps passé dans chacun des échelons des grades est fixée ainsi qu'il suit : "
    "GRADES ET ÉCHELONS DURÉE Biologistes, vétérinaires et pharmaciens de classe exceptionnelle "
    "8e échelon - 7e échelon 4 ans 6e échelon 3 ans 6 mois 5e échelon 3 ans 6 mois 4e échelon "
    "2 ans 6 mois 3e échelon 2 ans 6 mois 2e échelon 2 ans 6 mois 1er échelon 2 ans Biologistes, "
    "vétérinaires et pharmaciens hors classe 6e échelon - 5e échelon 3 ans 3 mois 4e échelon "
    "3 ans 3 mois 3e échelon 2 ans 2 mois 2e échelon 2 ans 2 mois 1er échelon 2 ans 2 mois "
    "Biologistes, vétérinaires et pharmaciens de classe normale 11e échelon - 10e échelon 2 ans "
    "2 mois 9e échelon 2 ans 2 mois 8e échelon 2 ans 2 mois 7e échelon 2 ans 2 mois 6e échelon "
    "2 ans 2 mois 5e échelon 2 ans 2 mois 4e échelon 2 ans 2 mois 3e échelon 1 an 9 mois 2e "
    "échelon 1 an 1er échelon 1 an Le 8e échelon de la classe exceptionnelle est accessible aux "
    "biologistes, vétérinaires et pharmaciens exerçant les fonctions de directeur de laboratoire.")


def test_la_phrase_qui_suit_le_tableau_n_y_ajoute_pas_de_ligne():
    tableau = _un_tableau(BIOLOGISTES)
    assert not tableau.refus
    debut = "Biologistes, vétérinaires et pharmaciens "
    assert {l.groupe for l in tableau.lignes} == {
        debut + "de classe exceptionnelle", debut + "hors classe", debut + "de classe normale"}
    assert len(tableau.lignes) == 8 + 6 + 11
    durees = _durees(tableau, "duree")
    assert [durees[(debut + "de classe exceptionnelle", str(e))] for e in range(8, 0, -1)] == [
        None, 48, 42, 42, 30, 30, 30, 24]
    assert durees[(debut + "hors classe", "5")] == 39
    assert [durees[(debut + "de classe normale", str(e))] for e in (3, 2, 1)] == [21, 12, 12]


#: Décret n° 91-857 du 2 septembre 1991, cadre d'emplois des professeurs
#: territoriaux d'enseignement artistique, article 18, du 1er août 1996 au
#: 1er janvier 2017 (LEGIARTI000006374077) : l'en-tête redit avant le second
#: grade.
PROFESSEURS_ARTISTIQUES = (
    "La durée maximale et la durée minimale du temps passé dans chacun des échelons des grades "
    "sont fixées ainsi qu'il suit : GRADE ET ECHELONS DUREE Maximale Minimale Professeur "
    "d'enseignement artistique hors classe 7e échelon - - 6e échelon 3 ans 1 mois 2 ans 11 mois "
    "5e échelon 3 ans 1 mois 2 ans 11 mois 4e échelon 2 ans 7 mois 2 ans 5 mois 3e échelon 2 ans "
    "7 mois 2 ans 5 mois 2e échelon 2 ans 7 mois 2 ans 5 mois 1er échelon 2 ans 7 mois 2 ans "
    "5 mois . . GRADE ET ECHELONS DUREE Maximale Minimale Professeur d'enseignement artistique de "
    "classe normale 9e échelon - - 8e échelon 3 ans 6 mois 3 ans 7e échelon 3 ans 6 mois 3 ans 6e "
    "échelon 3 ans 6 mois 3 ans 5e échelon 3 ans 2 ans 6 mois 4e échelon 3 ans 2 ans 6 mois 3e "
    "échelon 3 ans 2 ans 6 mois 2e échelon 2 ans 6 mois 2 ans 1er échelon 1 an 6 mois 1 an")


def test_l_en_tete_redit_n_est_pas_du_grade():
    tableau = _un_tableau(PROFESSEURS_ARTISTIQUES)
    assert not tableau.refus
    hc, cn = ("Professeur d'enseignement artistique hors classe",
              "Professeur d'enseignement artistique de classe normale")
    assert {l.groupe for l in tableau.lignes} == {hc, cn}
    maxi, mini = _durees(tableau, "duree_maximale"), _durees(tableau, "duree_minimale")
    assert (maxi[(hc, "6")], mini[(hc, "6")]) == (37, 35)
    assert [maxi[(cn, str(e))] for e in range(9, 0, -1)] == [None, 42, 42, 42, 36, 36, 36, 30, 18]
    assert [mini[(cn, str(e))] for e in range(9, 0, -1)] == [None, 36, 36, 36, 30, 30, 30, 24, 12]


def test_un_en_tete_redit_dans_un_autre_ordre_se_refuse():
    """Le même tableau, l'en-tête redit en « Minimale Maximale » : les durées
    du second grade seraient lues à l'envers si l'on gardait l'ordre du
    premier."""
    inverse = PROFESSEURS_ARTISTIQUES.replace(
        ". . GRADE ET ECHELONS DUREE Maximale Minimale", ". . GRADE ET ECHELONS DUREE Minimale Maximale")
    assert "l'en-tête change d'ordre" in dur.lire_tableau(dur.tableaux(inverse)[0]).refus


def test_un_tableau_de_reclassement_n_est_pas_un_tableau_de_durees():
    article = (
        "Les fonctionnaires sont reclassés conformément au tableau suivant : SITUATION ANCIENNE "
        "SITUATION NOUVELLE Ancienneté conservée dans la limite de la durée de l'échelon 5e "
        "échelon 4e échelon Ancienneté acquise 4e échelon 3e échelon Ancienneté acquise 3e "
        "échelon 2e échelon Sans ancienneté")
    assert dur.tableaux(article) == []


def test_d_un_echelon_au_suivant_se_refuse():
    """« Du 1er au 2e échelon : 2 ans » donne la durée du 1er : lue comme une
    ligne du 2e, elle serait décalée d'un échelon."""
    article = ("La durée du temps passé dans chacun des échelons est fixée ainsi qu'il suit : "
               "du 1er au 2e échelon : 1 an ; du 2e au 3e échelon : 2 ans ; du 3e au 4e "
               "échelon : 2 ans ; du 4e au 5e échelon : 3 ans.")
    assert dur.lire_tableau(dur.tableaux(article)[0]).refus


def test_une_condition_de_grade_n_est_pas_une_duree():
    """« Après 13 ans de grade » ouvre l'échelon exceptionnel : ce n'est pas
    sa durée."""
    article = (
        "Les conditions de durée d'échelon et d'accès aux échelons exceptionnels sont "
        "déterminées par grade et par échelle de solde conformément au tableau suivant : GRADE "
        "ÉCHELLE DE SOLDE DÉSIGNATION des échelons DURÉE de l'échelon et CONDITIONS D'ACCÈS à "
        "l'échelon exceptionnel RÈGLES particulières Lieutenant-colonel Echelle de solde n° 2 "
        "Echelon exceptionnel Après 13 ans de grade et avant 17 ans de grade Echelon attribué "
        "dans la limite de 10 % de l'effectif du grade en échelle de solde n° 2 (1) 10 e échelon "
        "9 e échelon 1 an 8 e échelon 1 an 7 e échelon 1 an 6 e échelon 1 an 5 e échelon 1 an "
        "4 e échelon 2 ans 3 e échelon 2 ans 2 e échelon 2 ans 1 er échelon 1 an")
    tableau = _un_tableau(article)
    assert not tableau.refus
    lignes = {l.echelon: l for l in tableau.lignes}
    assert lignes["exceptionnel"].duree is None
    assert lignes["exceptionnel"].condition.startswith("Après 13 ans de grade et avant 17 ans")
    assert lignes["10"].duree is None
    assert [lignes[str(e)].duree for e in range(9, 0, -1)] == [12, 12, 12, 12, 12, 24, 24, 24, 12]
    assert {l.groupe for l in tableau.lignes} == {"Lieutenant-colonel Echelle de solde n° 2"}


#: Décret n° 72-583 du 4 juillet 1972, statut particulier des adjoints
#: d'enseignement, article 6, en vigueur depuis le 29 octobre 2021
#: (LEGIARTI000044268513), en entier : le tableau, complet, est suivi d'un « II.- »
#: en phrases qui nomme le 6e et le 8e échelon.
ADJOINTS_D_ENSEIGNEMENT = (
    "I.-La durée du temps passé dans chacun des échelons du corps des adjoints d'enseignement"
    " est fixée, sous réserve des dispositions du II, ainsi qu'il suit : ÉCHELON DURÉE 11e "
    "échelon - 10e échelon 4 ans 6 mois 9e échelon 3 ans 6 mois 8e échelon 3 ans 6 mois 7e "
    "échelon 3 ans 6e échelon 3 ans 5e échelon 3 ans 4e échelon 2 ans 3e échelon 1 an 2e "
    "échelon 1 an 1er échelon 1 an II.-Les anciennetés détenues dans les 6e et 8e échelons de"
    " la classe normale peuvent être bonifiées de 9 mois. Le recteur d'académie établit, pour"
    " chaque année scolaire, d'une part, la liste des adjoints d'enseignement qui sont dans "
    "la deuxième année du 6e échelon de la classe normale et, d'autre part, la liste des "
    "adjoints d'enseignement qui justifient d'une ancienneté dans le 8e échelon de la classe "
    "normale comprise en 18 et 30 mois. Le recteur d'académie attribue les bonifications "
    "d'ancienneté à hauteur de 30 % de l'effectif des adjoints d'enseignement inscrits sur "
    "chacune de ces deux listes. Pour chaque liste, lorsque le nombre de bonifications "
    "attribuées n'est pas un entier, la décimale est ajoutée au nombre calculé au titre de "
    "l'année suivante. Le nombre de bonifications attribuées au cours de ces deux années ne "
    "peut dépasser 30 % de l'effectif des adjoints d'enseignement inscrits sur la liste au "
    "cours de cette même période."
)


#: Décret n° 72-580 du 4 juillet 1972, statut particulier des professeurs agrégés,
#: article 13, du 29 octobre 2021 au 2 septembre 2024 (LEGIARTI000044268441),
#: jusqu'à la deuxième phrase du II : une phrase, puis le « II.- ».
AGREGES = (
    "I.-La durée du temps passé dans chacun des échelons des grades du corps des professeurs "
    "agrégés est fixée, sous réserve des dispositions du II, ainsi qu'il suit : GRADES "
    "ÉCHELONS DURÉE Agrégé de classe exceptionnelle 3e échelon - 2e échelon 3 ans 1er échelon"
    " 2 ans 6 mois Agrégé hors classe 4e échelon - 3e échelon 3 ans 2e échelon 2 ans 1er "
    "échelon 2 ans Agrégé de classe normale 11e échelon ― 10e échelon 4 ans 9e échelon 4 ans "
    "8e échelon 3 ans 6 mois 7e échelon 3 ans 6e échelon 3 ans 5e échelon 2 ans 6 mois 4e "
    "échelon 2 ans 3e échelon 2 ans 2e échelon 1 an 1er échelon 1 an Le ministre prononce les"
    " promotions des professeurs agrégés. II.-Les anciennetés détenues dans les 6e et 8e "
    "échelons de la classe normale peuvent être bonifiées d'un an. Le ministre établit pour "
    "chaque année scolaire, dans chaque discipline, d'une part, la liste des professeurs "
    "agrégés qui sont dans la deuxième année du 6e échelon de la classe normale, d'autre "
    "part, la liste des professeurs agrégés qui justifient d'une ancienneté dans le 8e "
    "échelon de la classe normale comprise entre 18 et 30 mois."
)


def test_le_tableau_s_arrete_au_paragraphe_qui_le_suit():
    tableau = _un_tableau(ADJOINTS_D_ENSEIGNEMENT)
    assert not tableau.refus
    durees = _durees(tableau, "duree")
    assert [durees[("", str(e))] for e in range(11, 0, -1)] == [
        None, 54, 42, 42, 36, 36, 36, 24, 12, 12, 12]
    tableau = _un_tableau(AGREGES)
    assert not tableau.refus
    durees = _durees(tableau, "duree")
    assert len(tableau.lignes) == 3 + 4 + 11
    assert [durees[("Agrégé de classe exceptionnelle", str(e))] for e in (3, 2, 1)] == [
        None, 36, 30]
    assert [durees[("Agrégé hors classe", str(e))] for e in (4, 3, 2, 1)] == [None, 36, 24, 24]
    assert [durees[("Agrégé de classe normale", str(e))] for e in range(11, 0, -1)] == [
        None, 48, 48, 42, 36, 36, 30, 24, 24, 12, 12]


#: Décret n° 90-680 du 1er août 1990, statut particulier des professeurs des écoles,
#: article 24, du 1er septembre 2017 au 1er janvier 2021 (LEGIARTI000034947965),
#: jusqu'à la phrase qui suit le tableau : la case « Spécial » est l'échelon spécial
#: de la classe exceptionnelle, au-dessus du 4e.
PROFESSEURS_DES_ECOLES = (
    "I.-La durée du temps passé dans chacun des échelons des grades du corps des professeurs "
    "des écoles est fixée, sous réserve des dispositions du II, comme suit : GRADES ÉCHELONS "
    "DURÉE Professeur des écoles de classe exceptionnelle Spécial ― 4e échelon ― 3e échelon 2"
    " ans 6 mois 2e échelon 2 ans 1er échelon 2 ans Professeur des écoles hors classe 6e "
    "échelon - 5e échelon 3 ans 4e échelon 2 ans 6 mois 3e échelon 2 ans 6 mois 2e échelon 2 "
    "ans 1er échelon 2 ans Professeur des écoles de classe normale 11e échelon ― 10e échelon "
    "4 ans 9e échelon 4 ans 8e échelon 3 ans 6 mois 7e échelon 3 ans 6e échelon 3 ans 5e "
    "échelon 2 ans 6 mois 4e échelon 2 ans 3e échelon 2 ans 2e échelon 1 an 1er échelon 1 an "
    "Le recteur prononce, pour chaque année scolaire, les promotions des professeurs des "
    "écoles."
)

#: Décret n° 68-503 du 30 mai 1968, professeurs de chaires supérieures, article 4,
#: du 1er septembre 2018 au 6 août 2023 (LEGIARTI000038669047), depuis la phrase qui
#: dit « six échelons et un échelon spécial » : « Spécial » juste après l'en-tête.
CHAIRES_SUPERIEURES = (
    "Le corps des professeurs de chaires supérieures comporte six échelons et un échelon "
    "spécial. La durée du temps passé dans chacun des échelons est fixée ainsi qu'il suit : "
    "ÉCHELONS DURÉE Spécial - 6e échelon - 5e échelon 4 ans 6 mois 4e échelon 2 ans 3e "
    "échelon 2 ans 2e échelon 2ans 1er échelon 2 ans"
)

#: Décret n° 2014-923 du 18 août 2014, cadre d'emplois des puéricultrices
#: territoriales, article 25, en vigueur depuis le 1er janvier 2017
#: (LEGIARTI000037468710), en entier : « Avant le 1er échelon de la classe
#: supérieure » nomme les quatre échelons provisoires, il n'est pas une ligne.
PUERICULTRICES = (
    "Afin de permettre l'intégration des puéricultrices territoriales dans le présent cadre "
    "d'emplois, sont créés quatre échelons provisoires avant le 1er échelon de la classe "
    "supérieure du même grade. La durée du temps passé dans ces échelons est fixée ainsi "
    "qu'il suit : ÉCHELONS PROVISOIRES dans le grade de puéricultrice DURÉE Avant le 1er "
    "échelon de la classe supérieure 4e échelon provisoire 2 ans 3e échelon provisoire 2 ans "
    "2e échelon provisoire 2 ans 1er échelon provisoire 2 ans"
)


def test_la_case_special_est_l_echelon_special():
    tableau = _un_tableau(PROFESSEURS_DES_ECOLES)
    assert not tableau.refus
    ce = "Professeur des écoles de classe exceptionnelle"
    assert {l.groupe for l in tableau.lignes} == {
        ce, "Professeur des écoles hors classe", "Professeur des écoles de classe normale"}
    durees = _durees(tableau, "duree")
    assert [durees[(ce, e)] for e in ("special", "4", "3", "2", "1")] == [None, None, 30, 24, 24]
    assert len(tableau.lignes) == 5 + 6 + 11
    tableau = _un_tableau(CHAIRES_SUPERIEURES)
    assert not tableau.refus
    durees = _durees(tableau, "duree")
    assert [durees[("", e)] for e in ("special", "6", "5", "4", "3", "2", "1")] == [
        None, None, 54, 24, 24, 24, 24]


def test_avant_le_1er_echelon_n_est_pas_une_ligne():
    tableau = _un_tableau(PUERICULTRICES)
    assert not tableau.refus
    groupe = "Avant le 1er échelon de la classe supérieure"
    assert [(l.groupe, l.echelon, l.duree) for l in tableau.lignes] == [
        (groupe, f"{e}-provisoire", 24) for e in (4, 3, 2, 1)]


#: Décret n° 2016-2003 du 30 décembre 2016, emplois de directeur départemental et de
#: directeur départemental adjoint des services d'incendie et de secours, article 13,
#: en vigueur depuis le 17 avril 2022 (LEGIARTI000045657613), en entier : chaque
#: emploi est nommé avant l'en-tête de son tableau, « ÉCHELONS DURÉE ».
SDIS = (
    "La durée du temps passé dans chacun des échelons afférents aux catégories de service "
    "d'incendie et de secours et aux emplois en relevant sont fixées en application du "
    "tableau suivant : Directeur départemental des services d'incendie et de secours de "
    "catégorie A : ÉCHELONS DURÉE 7e échelon - 6e échelon 3 ans 5e échelon 3 ans 4e échelon 3"
    " ans 3e échelon 2 ans 6 mois 2e échelon 2 ans 1er échelon 1 an 6 mois Directeur "
    "départemental des services d'incendie et de secours de catégorie B : ÉCHELONS DURÉE 7e "
    "échelon - 6e échelon 3 ans 5e échelon 3 ans 4e échelon 3 ans 3e échelon 2 ans 6 mois 2e "
    "échelon 2 ans 1er échelon 1 an 6 mois Directeur départemental des services d'incendie et"
    " de secours de catégorie C : ÉCHELONS DURÉE 8e échelon - 7e échelon 3 ans 6e échelon 3 "
    "ans 5e échelon 3 ans 4e échelon 2 ans 6 mois 3e échelon 2 ans 2e échelon 1 an 6 mois 1er"
    " échelon 1 an 6 mois Directeur départemental adjoint des services d'incendie et de "
    "secours de catégorie A : ÉCHELONS DURÉE 8e échelon - 7e échelon 3 ans 6e échelon 3 ans "
    "5e échelon 3 ans 4e échelon 2 ans 6 mois 3e échelon 2 ans 2e échelon 1 an 6 mois 1er "
    "échelon 1 an 6 mois Directeur départemental adjoint des services d'incendie et de "
    "secours de catégorie B : ÉCHELONS DURÉE 7e échelon - 6e échelon 3 ans 5e échelon 3 ans "
    "4e échelon 2 ans 6 mois 3e échelon 2 ans 2e échelon 1 an 6 mois 1er échelon 1 an 6 mois "
    "Directeur départemental adjoint des services d'incendie et de secours de catégorie C : "
    "ÉCHELONS DURÉE 8e échelon - 7e échelon 3 ans 6e échelon 3 ans 5e échelon 3 ans 4e "
    "échelon 2 ans 6 mois 3e échelon 2 ans 2e échelon 1 an 6 mois 1er échelon 1 an 6 mois"
)


def test_l_emploi_nomme_avant_l_en_tete_est_le_groupe():
    tableaux = [dur.lire_tableau(e) for e in dur.tableaux(SDIS)]
    emploi = "Directeur départemental{} des services d'incendie et de secours de catégorie {}"
    assert [{l.groupe for l in t.lignes} for t in tableaux] == [
        {emploi.format(adjoint, c)} for adjoint in ("", " adjoint") for c in "ABC"]
    assert all(t.entete == "ÉCHELONS DURÉE" and not t.refus for t in tableaux)
    durees = [[l.duree for l in t.lignes] for t in tableaux]
    assert durees[0] == [None, 36, 36, 36, 30, 24, 18]
    assert durees[2] == [None, 36, 36, 36, 30, 24, 18, 18]
    assert durees[4] == [None, 36, 36, 30, 24, 18, 18]


# ---------------------------------------------------------------------------
# Les fichiers du dépôt, recoupés aux articles du LEGI lus à la main
# ---------------------------------------------------------------------------

def _lire(nom: str) -> list[dict]:
    chemin = DOSSIER / f"{nom}.csv"
    if not chemin.exists():
        pytest.fail(f"{chemin} absent : python scripts/fetch/dila_legi_durees.py")
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.startswith("#")))


@pytest.fixture(scope="module")
def lignes() -> list[dict]:
    return _lire("lignes")


@pytest.fixture(scope="module")
def tableaux_lus() -> list[dict]:
    return _lire("tableaux")


def _ligne(lignes, article: str, groupe: str, echelon: str) -> dict:
    trouves = [l for l in lignes if l["article"] == article and l["groupe"] == groupe
               and l["echelon"] == echelon]
    assert len(trouves) == 1, (article, groupe, echelon, len(trouves))
    return trouves[0]


def _versions(tableaux_lus, article: str) -> list[dict]:
    return [t for t in tableaux_lus if t["article"] == article]


def test_la_territoriale_du_decret_2010_329_minimale_puis_maximale(lignes, tableaux_lus):
    """Article 24 du décret n° 2010-329, le premier grade d'avant 2014
    (LEGIARTI000022021243, du 27 mars 2010 au 1er février 2014) : « DURÉES
    Minimale Maximale », « 10e échelon 2 ans 5 mois 3 ans »."""
    article = "LEGIARTI000022021243"
    (version,) = _versions(tableaux_lus, article)
    assert (version["debut"], version["fin"], version["colonnes"]) == (
        "2010-03-27", "2014-02-01", "minimale maximale")
    dixieme = _ligne(lignes, article, "Troisième grade", "10")
    assert (dixieme["duree_minimale"], dixieme["duree_maximale"]) == ("29", "36")
    douzieme = _ligne(lignes, article, "Deuxième grade", "12")
    assert (douzieme["duree_minimale"], douzieme["duree_maximale"]) == ("39", "48")
    assert _ligne(lignes, article, "Troisième grade", "11")["duree_maximale"] == ""


def test_la_territoriale_du_decret_2010_329_maximale_puis_minimale(lignes, tableaux_lus):
    """La version suivante (LEGIARTI000028542716, du 1er février 2014 au
    15 mai 2016) écrit « MAXIMALE MINIMALE » : « 10e échelon 3 ans 2 ans
    5 mois »."""
    article = "LEGIARTI000028542716"
    (version,) = _versions(tableaux_lus, article)
    assert version["colonnes"] == "maximale minimale"
    dixieme = _ligne(lignes, article, "Troisième grade", "10")
    assert (dixieme["duree_maximale"], dixieme["duree_minimale"]) == ("36", "29")
    septieme = _ligne(lignes, article, "Deuxième grade", "7")
    assert (septieme["duree_maximale"], septieme["duree_minimale"]) == ("24", "20")


def test_la_territoriale_du_decret_2010_329_duree_unique(lignes, tableaux_lus):
    """Puis la durée unique (LEGIARTI000032542276, du 15 mai 2016 au
    1er janvier 2017) : « Deuxième grade 13e échelon 12e échelon 4 ans »."""
    article = "LEGIARTI000032542276"
    (version,) = _versions(tableaux_lus, article)
    assert (version["debut"], version["fin"], version["colonnes"]) == (
        "2016-05-15", "2017-01-01", "unique")
    assert _ligne(lignes, article, "Deuxième grade", "12")["duree"] == "48"
    assert _ligne(lignes, article, "Troisième grade", "6")["duree"] == "24"
    assert _ligne(lignes, article, "Premier grade", "1")["duree"] == "12"


def test_l_etat_hospitaliere_et_militaires_au_depot(lignes, tableaux_lus):
    assert _ligne(lignes, "LEGIARTI000006470031", "", "5")["duree_moyenne"] == "42"
    assert _ligne(lignes, "LEGIARTI000034794372", "Ingénieur d'études de classe normale",
                  "13")["duree"] == "36"
    assert _ligne(lignes, "LEGIARTI000037623011", "Ingénieur hospitalier principal",
                  "2")["duree"] == "30"
    # La version du 5 janvier 2013 redit le tableau de celle du 1er janvier 2012 :
    # une seule période, qui nomme les deux versions.
    (gendarmes,) = [t for t in tableaux_lus if "LEGIARTI000026912312" in t["versions"].split()]
    assert gendarmes["versions"].split()[:2] == ["LEGIARTI000025074407", "LEGIARTI000026912312"]
    assert _ligne(lignes, gendarmes["article"],
                  "Gendarme Echelle de solde spécifique des gendarmes", "12")["duree"] == "36"


def test_les_officiers_du_cadre_special_echelle_par_echelle(lignes):
    """Décret n° 76-1001, article 14, en vigueur depuis le 15 décembre 2025
    (LEGIARTI000052465264) : le colonel en échelle de solde n° 3, « 12 e
    échelon 1 an et 6 mois », puis en échelle n° 2, « 14 e échelon 1 an »."""
    article = "LEGIARTI000052465264"
    assert _ligne(lignes, article, "Colonel Echelle de solde n° 3", "12")["duree"] == "18"
    assert _ligne(lignes, article, "Colonel Echelle de solde n° 2", "14")["duree"] == "12"
    assert _ligne(lignes, article, "Colonel Echelle de solde n° 2", "12")["duree"] == "18"


#: Les versions que le LEGI date d'une fin antérieure ou égale à leur début, que
#: ``dila_cherche.py legi --num … --diff`` marque « (jamais en vigueur) » : n° 99-669,
#: art. 17, du 1er janvier 2021 au 1er juin 2020 ; n° 83-1260, art. 34, du
#: 8 janvier 1984 au 4 août 1980 ; n° 91-868, art. 7, du 1er janvier 2021 au
#: 19 novembre 2018 ; n° 91-290, art. 14-4, du 1er septembre 2014 au 30 août 2012 ;
#: n° 2014-923, art. 25, n° 92-851, art. 14, du 1er janvier 2017 au même jour ;
#: n° 2014-1455, art. 22, du 15 décembre 2025 au même jour.
JAMAIS_EN_VIGUEUR = {
    "LEGIARTI000034810141", "LEGIARTI000027940471", "LEGIARTI000035606585",
    "LEGIARTI000025845550", "LEGIARTI000032578591", "LEGIARTI000034434459",
    "LEGIARTI000052465286"}


def test_une_version_jamais_en_vigueur_se_reconnait_a_ses_dates():
    assert dur.jamais_en_vigueur("2021-01-01", "2020-06-01")
    assert dur.jamais_en_vigueur("2017-01-01", "2017-01-01")
    assert not dur.jamais_en_vigueur("2021-01-01", "2026-01-01")
    assert not dur.jamais_en_vigueur("2017-01-01", "2999-01-01")
    assert not dur.jamais_en_vigueur("2017-01-01", "")


def test_une_version_jamais_en_vigueur_n_est_pas_lue(lignes, tableaux_lus):
    """Elle n'est ni dans les tableaux ni dans les lignes, même réunie à la
    suivante (n° 92-851, art. 14) ; ``non_lus.csv`` la consigne avec sa raison."""
    assert not [t["article"] for t in tableaux_lus if set(t["versions"].split()) & JAMAIS_EN_VIGUEUR]
    assert not [l["article"] for l in lignes if l["article"] in JAMAIS_EN_VIGUEUR]
    assert all(not t["fin"] or t["fin"] > t["debut"] for t in tableaux_lus)
    consignees = {n["article"] for n in _lire("non_lus")
                  if n["motif"].startswith("version jamais en vigueur")}
    assert JAMAIS_EN_VIGUEUR <= consignees


def test_la_version_en_vigueur_a_ces_dates_est_lue(lignes, tableaux_lus):
    """N° 99-669, art. 17, en vigueur du 1er janvier 2021 au 1er janvier 2026
    (LEGIARTI000041916038) : « Directeur technique de classe exceptionnelle
    Echelon spécial - 5e échelon - 4e échelon 3 ans 3e échelon 2 ans 6 mois »,
    classe que la version jamais en vigueur n'écrit pas. N° 2014-923, art. 25,
    en vigueur depuis le 1er janvier 2017 (LEGIARTI000037468710) : « 4e échelon
    provisoire 2 ans ». N° 2014-1455, art. 22, en vigueur depuis le
    15 décembre 2025 (LEGIARTI000053027219) : « Général de brigade Echelle de
    solde n° 3 … 1 er échelon 1 an ». N° 92-851, art. 14, en vigueur depuis le
    1er janvier 2017 (LEGIARTI000037468701) : « Médecin hors classe … 4e échelon
    3 ans »."""
    ce = "Directeur technique de classe exceptionnelle"
    (penitentiaire,) = [t for t in tableaux_lus
                        if "LEGIARTI000041916038" in t["versions"].split()]
    assert penitentiaire["fin"] == "2026-01-01"
    assert _ligne(lignes, penitentiaire["article"], ce, "4")["duree"] == "36"
    assert _ligne(lignes, penitentiaire["article"], ce, "3")["duree"] == "30"
    assert [l["duree"] for l in lignes if l["article"] == "LEGIARTI000037468710"
            and l["echelon"] == "4-provisoire"] == ["24"]
    assert _ligne(lignes, "LEGIARTI000053027219", "Général de brigade Echelle de solde n° 3",
                  "1")["duree"] == "12"
    (medecins,) = [t for t in tableaux_lus if "LEGIARTI000037468701" in t["versions"].split()]
    assert (medecins["article"], medecins["debut"]) == ("LEGIARTI000037468701", "2017-01-01")
    assert _ligne(lignes, "LEGIARTI000037468701", "Médecin hors classe", "4")["duree"] == "36"


def test_aucun_libelle_ne_garde_la_case_d_un_echelon(lignes):
    """Décret n° 2011-1317, article 18, du 20 octobre 2011 au 2 octobre 2013
    (LEGIARTI000024684456) : « Attaché hors classe Spécial 7e ― 6e 3 ans » ; le
    grade est « Attaché hors classe », et son échelon spécial une ligne."""
    assert not [l["groupe"] for l in lignes
                if l["groupe"].lower().endswith(("spécial", "special")) or l["groupe"] == "Avant le"]
    attache = [l for l in lignes if l["article"] == "LEGIARTI000024684456"
               and l["groupe"] == "Attaché hors classe"]
    assert [(l["echelon"], l["rang"], l["duree"]) for l in attache][:3] == [
        ("special", "8", ""), ("7", "7", ""), ("6", "6", "36")]


def test_chaque_ligne_est_certifiee_et_datee(lignes, tableaux_lus):
    assert lignes and all(l["fiabilite"] == "certifiee" for l in lignes)
    assert all(t["debut"] and t["article"].startswith("LEGIARTI") for t in tableaux_lus)
    textes = {t["texte"] for t in _lire("textes")}
    assert {l["texte"] for l in lignes} <= textes
