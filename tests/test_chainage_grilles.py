"""Le chaînage des durées d'échelon et des reclassements aux grilles du dépôt
(action 158, étape 3), recoupé aux textes.

Chaque valeur attendue vient d'un article ou d'une notice lus dans l'index LEGI
du dépôt (incrément 20261102-213929), ou d'une ligne du Noyau RH du CISIRH,
le 3 novembre 2026, et recopiée ici avec sa référence. Les périodes attendues
sont posées à la main : l'intersection de la période du tableau (fin exclue)
et de celle de la grille (fin incluse, soit le lendemain exclu).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
GRILLES = RACINE / "data" / "reference" / "grilles"
CHAINAGE = GRILLES / "chainage"
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))

import dila_legi_chainage as chainage  # noqa: E402


def _lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.startswith("#")))


@pytest.fixture(scope="module")
def durees() -> list[dict]:
    return _lire(CHAINAGE / "durees.csv")


@pytest.fixture(scope="module")
def reclassements() -> list[dict]:
    return _lire(CHAINAGE / "reclassements.csv")


@pytest.fixture(scope="module")
def a_lire() -> list[dict]:
    return _lire(CHAINAGE / "a_lire_au_jorf.csv")


# ---------------------------------------------------------------------------
# Les règles, une à une
# ---------------------------------------------------------------------------

def test_un_libelle_se_compare_sans_accents_ni_pluriel_ni_article_du_lecteur():
    # Le tableau de durées du n° 94-464 écrit « Conseillers techniques
    # d'éducation spécialisée » ; une grille, « Conseiller technique… » ; le
    # lecteur des grilles distingue deux grilles du même nom par « (article 2) ».
    n = chainage.normaliser
    assert n("Conseillers techniques d'éducation spécialisée") == n(
        "Conseiller technique d'education specialisee")
    assert n("brigadiers-chefs principaux") == n("Brigadier-chef principal")
    assert n("Ingénieur principal (article 2)") == n("Ingénieur principal")
    assert n("Ingénieur principal") != n("Ingénieur")
    assert n("") == ""


def test_l_article_d_une_grille_nomme_son_statut_par_son_numero_ou_sa_date():
    # Décret n° 2017-171, art. 116 (LEGIARTI000034028850), version du 13 février 2017.
    article = ("I. - L'échelonnement indiciaire applicable au corps des ingénieurs de "
               "recherche régi par le décret du 31 décembre 1985 susvisé est fixé ainsi "
               "qu'il suit :")
    assert chainage.nomme(article, "95-370", "1995-04-06") == ""
    assert chainage.nomme(article, "", "1985-12-31") == "date"
    assert chainage.nomme("régi par le décret n° 95-370 du 6 avril 1995", "95-370",
                          "1995-04-06") == "numero"
    # « décret du 1er août 1990 » : le premier du mois s'écrit « 1er ».
    assert chainage.nomme("régi par le décret du 1er août 1990 susvisé", "90-680",
                          "1990-08-01") == "date"


def test_la_date_qui_ouvre_la_phrase_du_reclassement():
    # Décret n° 2004-1439, art. 23-1 (LEGIARTI000023734900) ; décret n° 2017-786
    # (LEGIARTI000034750747).
    assert chainage.date_de_la_phrase(
        "Au 1er juillet 2011, les membres du corps d'encadrement et d'application de la "
        "police nationale sont reclassés") == "2011-07-01"
    assert chainage.date_de_la_phrase(
        "Au 1er septembre 2017, les fonctionnaires appartenant au corps des professeurs "
        "certifiés régi par le décret n° 72-581 du 4 juillet 1972 susvisé") == "2017-09-01"
    # La date d'un texte cité n'est pas celle du reclassement.
    assert chainage.date_de_la_phrase(
        "Les membres du corps régi par le décret du 4 juillet 1972 sont reclassés") == ""


# ---------------------------------------------------------------------------
# Les durées
# ---------------------------------------------------------------------------

def _lignes_de(durees, article, groupe):
    return [d for d in durees if d["article"] == article and d["groupe"] == groupe]


def test_une_duree_territoriale_se_rattache_a_sa_grille_par_le_visa(durees):
    # Décret n° 2016-201 (LEGITEXT000032117021), art. 24 (LEGIARTI000032117092),
    # du 1er mars 2016 au 1er janvier 2017 : « Ingénieur hors classe Echelon spécial
    # - - 5e échelon - - 4e échelon 2 ans et 9 mois 3 ans […] 1er échelon 1 an et
    # 9 mois 2 ans ». Décret n° 2016-203 (LEGITEXT000032116807), « portant
    # échelonnement indiciaire applicable aux ingénieurs territoriaux », ne vise
    # qu'un statut : « Vu le décret n° 2016-201 du 26 février 2016 portant statut
    # particulier du cadre d'emplois des ingénieurs territoriaux » ; son art. 1
    # (LEGIARTI000032116817), du 1er mars 2016 : « Ingénieur hors classe Echelon
    # spécial HEA 5e échelon 1015 […] 1er échelon 871 ». Six échelons de part et
    # d'autre. Période : [2016-03-01, 2017-01-01) ∩ [2016-03-01, …) .
    (ligne,) = [d for d in _lignes_de(durees, "LEGIARTI000032117092", "Ingénieur hors classe")
                if d["statut"] == "rattache"]
    assert ligne["texte"] == "LEGITEXT000032117021"
    assert (ligne["source"], ligne["texte_grille"], ligne["grille"]) == (
        "territoriale", "LEGITEXT000032116807", "ingenieur-hors-classe")
    assert (ligne["debut"], ligne["fin"]) == ("2016-03-01", "2017-01-01")
    assert ligne["lien"] == "visa"
    assert ("Vu le décret n° 2016-201 du 26 février 2016 portant statut particulier du "
            "cadre d'emplois des ingénieurs territoriaux") in ligne["preuve"]


def test_une_duree_de_l_etat_se_rattache_au_corps_du_noyau(durees):
    # Décret n° 90-680 (LEGITEXT000006076298), art. 24 (LEGIARTI000034948501), du
    # 1er janvier 2021 au 6 août 2023 au dépôt : « Professeur des écoles de classe
    # exceptionnelle Spécial ― 4e échelon ― 3e échelon 2 ans 6 mois 2e échelon
    # 2 ans 1er échelon 2 ans ». Noyau RH : le texte 160, « Décret n° 90-680 du
    # 1er août 1990 relatif au statut particulier des professeurs des écoles »,
    # origine du corps 00021 et de son grade 04235, « Professeur des écoles de
    # classe exceptionnelle », grille 03313, depuis le 1er septembre 2017 ; ses
    # échelons de rang 1 à 5 (le 5e, « exceptionnel », lettre A). Période :
    # [2021-01-01, 2023-08-06) ∩ [2017-09-01, …).
    (ligne,) = [d for d in _lignes_de(durees, "LEGIARTI000034948501",
                                       "Professeur des écoles de classe exceptionnelle")
                if d["statut"] == "rattache" and d["source"] == "etat"]
    assert (ligne["corps"], ligne["grade"], ligne["grille"]) == ("00021", "04235", "03313")
    assert (ligne["debut"], ligne["fin"]) == ("2021-01-01", "2023-08-06")
    assert ligne["lien"] == "noyau"
    assert "90-680" in ligne["preuve"]


def test_un_texte_commun_a_plusieurs_corps_ne_rattache_pas_sur_le_seul_libelle(durees):
    # Décret n° 95-370 (agriculture), art. 25 (LEGIARTI000034773631) : « Ingénieur
    # de recherche hors classe : Echelon spécial 4e échelon - 3e échelon 3 ans
    # […] ». Le décret n° 2017-171 (LEGITEXT000034028389) vise le n° 95-370 parmi
    # d'autres statuts, mais son art. 116 fixe la grille du même nom pour « le
    # corps des ingénieurs de recherche régi par le décret du 31 décembre 1985 » :
    # un autre corps, et quatre échelons, non cinq.
    lignes = _lignes_de(durees, "LEGIARTI000034773631", "Ingénieur de recherche hors classe")
    assert lignes
    assert not [d for d in lignes if d["statut"] == "rattache"
                and d["texte_grille"] == "LEGITEXT000034028389"]


def test_chaque_grade_de_chaque_tableau_est_rattache_ou_declare(durees):
    attendus = {(l["texte"], l["article"], l["tableau"], l["groupe"])
                for l in _lire(GRILLES / "durees" / "lignes.csv")}
    assert {(d["texte"], d["article"], d["tableau"], d["groupe"]) for d in durees} == attendus
    for d in durees:
        assert d["statut"] in {"rattache", "declare"}
        if d["statut"] == "rattache":
            assert d["preuve"] and d["grille"] and d["debut"] < (d["fin"] or "9999")
        else:
            assert d["raison"]


def test_les_versions_qui_se_chevauchent_ne_se_rattachent_pas_sur_leur_recouvrement(durees):
    # Les trois paires de `tableaux.csv` (colonne chevauche) : deux versions du
    # même article en vigueur ensemble aux dates du LEGI ; le chaînage ne choisit
    # pas entre elles.
    tableaux = _lire(GRILLES / "durees" / "tableaux.csv")
    par_article = {(t["article"], t["tableau"]): t for t in tableaux}
    paires = 0
    for t in tableaux:
        if not t["chevauche"]:
            continue
        autre = par_article[(t["chevauche"], t["tableau"])]
        debut = max(t["debut"], autre["debut"])
        fin = min(t["fin"] or "9999", autre["fin"] or "9999")
        assert debut < fin
        paires += 1
        for d in durees:
            if d["article"] == t["article"] and d["statut"] == "rattache":
                assert d["fin"] and d["fin"] <= debut or d["debut"] >= fin, d
    assert paires == 6


# ---------------------------------------------------------------------------
# Les reclassements
# ---------------------------------------------------------------------------

def test_un_reclassement_de_l_etat_se_rattache_aux_grilles_du_noyau(reclassements):
    # Décret n° 2004-1439, art. 23-1 (LEGIARTI000023734900) : « Au 1er juillet
    # 2011, les membres du corps d'encadrement et d'application de la police
    # nationale sont reclassés […] Gardien de la paix Gardien de la paix Echelon
    # exceptionnel 12e échelon […] ». Noyau RH : le texte 296 (n° 2004-1439),
    # origine du grade 02780 « Gardien de la paix », du corps 00172 ; sa grille,
    # 00422 jusqu'au 30 juin 2011, 02783 depuis le 1er juillet 2011.
    (ligne,) = [r for r in reclassements if r["article"] == "LEGIARTI000023734900"
                and r["groupe"] == "Gardien de la paix Gardien de la paix"]
    assert ligne["statut"] == "rattache"
    assert ligne["date"] == "2011-07-01"
    assert ligne["corps"] == "00172"
    assert (ligne["grade_origine"], ligne["grille_origine"]) == ("02780", "00422")
    assert (ligne["grade_accueil"], ligne["grille_accueil"]) == ("02780", "02783")


def test_chaque_groupe_de_chaque_reclassement_est_rattache_ou_declare(reclassements):
    attendus = {(l["texte"], l["article"], l["tableau"], l["groupe"])
                for l in _lire(GRILLES / "reclassements" / "lignes.csv")}
    assert {(r["texte"], r["article"], r["tableau"], r["groupe"])
            for r in reclassements} == attendus
    for r in reclassements:
        assert r["statut"] in {"rattache", "declare"}
        assert r["preuve"] if r["statut"] == "rattache" else r["raison"]


# ---------------------------------------------------------------------------
# Ce qu'une lecture au Journal officiel viserait
# ---------------------------------------------------------------------------

def test_un_tableau_que_le_legi_abime_est_a_lire_au_jorf(a_lire):
    # Décret n° 96-1113, art. 14 (LEGIARTI000042571828), depuis le 1er janvier
    # 2021 : « Professeur technique hors classe 7e échelon - 6e échelon 3 ans
    # 4e échelon 2 ans 6 mois […] » ; le 5e échelon manque.
    (ligne,) = [a for a in a_lire if a["texte"] == "LEGITEXT000005622310"
                and a["cas"] == "abime"]
    assert "LEGIARTI000042571828" in ligne["articles"]
    assert ligne["numero"] == "96-1113"
