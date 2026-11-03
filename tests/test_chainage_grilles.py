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


def test_la_preuve_article_cite_les_versions_en_vigueur_sur_la_periode(durees):
    # Relecture R-B3, point 1 c. Arrêté LEGITEXT000031320442 (greffiers des
    # services judiciaires), art. 3 : LEGIARTI000048278636 du 2023-11-01 au
    # 2024-03-01, puis LEGIARTI000049196634 depuis le 2024-03-01, chacune « régi par
    # le décret n° 2015-1275 du 13 octobre 2015 susvisé est fixé ainsi qu'il suit ».
    # Le rattachement de « Greffier » depuis le 2024-03-01 cite la seconde, non la
    # première.
    (ligne,) = [d for d in durees if d["texte_grille"] == "LEGITEXT000031320442"
                and d["groupe"] == "Greffier" and d["debut"] == "2024-03-01"
                and d["statut"] == "rattache"]
    assert "LEGIARTI000049196634" in ligne["preuve"]
    assert "LEGIARTI000048278636" not in ligne["preuve"]
    # LEGITEXT000026383946 (professeurs techniques de l'enseignement maritime),
    # art. 5 : LEGIARTI000041912445 du 2017-01-01 au 2025-03-20, puis
    # LEGIARTI000051351757 depuis le 2025-03-20, chacune « régis par le décret du
    # 29 mars 1993 susvisé » : le rattachement ouvert depuis le 2024-12-29 cite les deux.
    (ligne,) = [d for d in durees if d["texte_grille"] == "LEGITEXT000026383946"
                and d["groupe"] == "Professeur technique de classe normale"
                and d["debut"] == "2024-12-29" and d["statut"] == "rattache"]
    assert "LEGIARTI000041912445" in ligne["preuve"]
    assert "LEGIARTI000051351757" in ligne["preuve"]


def test_la_preuve_dit_pourquoi_la_grille_du_meme_nom_est_ecartee(durees):
    # Relecture R-B3, point 1 c. Décret n° 2021-1264 (LEGITEXT000044130353) : son
    # art. 1 (LEGIARTI000044130360) fixe une « Classe supérieure » de dix échelons
    # pour « les corps de pédicures-podologues, ergothérapeutes, psychomotriciens et
    # orthoptistes », son art. 2 (LEGIARTI000044130362) une « Classe supérieure » de
    # neuf pour « les corps de masseurs-kinésithérapeutes et d'orthophonistes ». Le
    # tableau 2 de durées du n° 2015-1048 (LEGIARTI000044133226) se rattache à la
    # première, le tableau 3 à la seconde : les échelons seuls les départagent, et
    # la preuve le dit.
    for tableau, gardee, ecartee in (("2", "classe-superieure-article-1",
                                      "classe-superieure-article-2"),
                                     ("3", "classe-superieure-article-2",
                                      "classe-superieure-article-1")):
        (ligne,) = [d for d in durees if d["article"] == "LEGIARTI000044133226"
                    and d["tableau"] == tableau and d["statut"] == "rattache"]
        assert ligne["grille"] == gardee
        assert f"la grille {ecartee}" in ligne["preuve"] and "écartée" in ligne["preuve"]
        assert "échelons" in ligne["preuve"].split(ecartee)[1]


def test_un_texte_commun_a_plusieurs_corps_ne_rattache_pas_sur_le_seul_libelle(durees):
    # Décret n° 95-370 (agriculture), art. 25 (LEGIARTI000034773631) : « Ingénieur
    # de recherche hors classe : Echelon spécial 4e échelon - 3e échelon 3 ans
    # […] ». Le décret n° 2017-171 (LEGITEXT000034028389) vise le n° 95-370 parmi
    # d'autres statuts, mais son art. 116 (LEGIARTI000034028850) fixe la grille du
    # même nom pour un autre corps : « L'échelonnement indiciaire applicable au
    # corps des ingénieurs de recherche régi par le décret du 31 décembre 1985
    # susvisé est fixé ainsi qu'il suit », et quatre échelons, non cinq.
    lignes = _lignes_de(durees, "LEGIARTI000034773631", "Ingénieur de recherche hors classe")
    assert lignes
    assert not [d for d in lignes if d["statut"] == "rattache"
                and d["texte_grille"] == "LEGITEXT000034028389"]


@pytest.fixture(scope="module")
def noyau() -> dict:
    """Les lignes du Noyau RH (``grilles/etat/``) qui citent chaque texte : de
    quel corps ou de quel grade, et à quelles dates (fin incluse)."""
    textes = {t["texte"]: t for t in _lire(GRILLES / "etat" / "textes.csv")}
    citations: dict[tuple, list[tuple]] = {}
    for nom, colonne in (("corps", "corps"), ("grades", "grade")):
        for ligne in _lire(GRILLES / "etat" / f"{nom}.csv"):
            for reference in ligne["textes"].split():
                ident = reference.split(":")[0]
                qui = (f"le corps {ligne['corps']}" if colonne == "corps"
                       else f"le grade {ligne['grade']} du corps {ligne['corps']}")
                citations.setdefault((qui, ident), []).append((ligne["debut"], ligne["fin"]))
    numeros = {}
    for (qui, ident) in citations:
        numeros.setdefault(textes.get(ident, {}).get("numero", ""), set()).add(qui)
    return {"textes": textes, "citations": citations, "numeros": numeros}


def _couvert(intervalles, debut, fin_exclue) -> bool:
    """[debut, fin_exclue) est couvert par la réunion des intervalles (fin incluse)."""
    import datetime
    jour = debut
    fin_exclue = fin_exclue or "9999-12-31"
    for d, f in sorted(intervalles):
        if d <= jour and (not f or f >= jour):
            if not f:
                return True
            jour = (datetime.date.fromisoformat(f) + datetime.timedelta(days=1)).isoformat()
            if jour >= fin_exclue:
                return True
    return jour >= fin_exclue


def test_le_noyau_cite_un_statut_par_ses_corps_comme_par_ses_grades(durees, noyau):
    # Relecture R-B3, point 1 d : les corps de `corps.csv` et ceux des grades de
    # `grades.csv` étaient réunis dans un seul dictionnaire, indexé par le code du
    # corps ; les grades écrasaient le corps. Le n° 2011-1317 (attachés, texte du
    # noyau), le n° 2012-1098 (assistants de service social), le n° 2015-576
    # (ingénieurs des systèmes d'information et de communication) et le n° 99-911
    # sont pourtant cités au noyau : aucune raison ne doit dire le contraire.
    for d in durees:
        if d["statut"] != "declare":
            continue
        for numero in __import__("re").findall(r"le Noyau RH ne cite le n° (\S+) pour aucun corps",
                                               d["raison"]):
            assert not noyau["numeros"].get(numero), (numero, sorted(noyau["numeros"][numero])[:3])


def test_deux_corps_qui_citent_le_statut_et_ont_les_memes_grades_ne_se_rattachent_pas(durees):
    # Décret n° 2012-762 (texte 1142 du noyau, « portant dispositions statutaires
    # communes aux corps d'infirmiers de catégorie A des administrations de l'Etat ») :
    # `corps.csv` le cite pour le corps 01102 (« Infirmiers des administrations de
    # l'Etat ») et pour le corps 01153 (« Infirmiers de la défense »), qui ont, du
    # 2012-06-01 au 2021-12-31, les mêmes grades aux mêmes grilles (« Infirmier hors
    # classe » 02947 puis 03214, « … de classe supérieure » 02948 puis 03215, « … de
    # classe normale » 02949 puis 03216). Un seul corps au noyau : aucun rattachement.
    statuts = {t["texte"]: t["numero"] for t in _lire(GRILLES / "durees" / "textes.csv")}
    assert not [d for d in durees if statuts[d["texte"]] == "2012-762"
                and d["statut"] == "rattache" and d["lien"] == "noyau"]


def _citations_de_la_preuve(preuve: str):
    import re
    return re.findall(r"(le (?:corps|grade \d{5} du corps) \d{5}) cite le texte (\d+)", preuve)


def test_la_preuve_du_noyau_dit_qui_cite_le_statut_et_vaut_sur_toute_la_periode(durees, noyau):
    # Relecture R-B3, point 1 d : « le corps … cite » quand seul un grade cite ;
    # et une citation de 1984 à 1995 (grades 03762 à 03764 du corps 00550, texte
    # 1135, n° 83-1260) prise pour toute la période 2002-2020. La preuve nomme qui
    # cite (le corps, ou tel grade du corps), et ses versions qui citent le texte
    # couvrent la période du rattachement.
    lignes = [d for d in durees if d["statut"] == "rattache" and d["lien"] == "noyau"]
    assert lignes
    for d in lignes:
        citations = _citations_de_la_preuve(d["preuve"])
        assert citations, d["preuve"]
        intervalles = [i for qui, ident in citations
                       for i in noyau["citations"].get((qui, ident), [])]
        assert intervalles, (d["preuve"], citations)
        assert _couvert(intervalles, d["debut"], d["fin"]), (d["texte"], d["groupe"], d["debut"],
                                                             d["fin"], citations)


def test_la_preuve_d_un_reclassement_dit_qui_cite_le_statut_a_sa_date(reclassements, noyau):
    import datetime
    lignes = [r for r in reclassements if r["statut"] == "rattache"]
    assert lignes
    for r in lignes:
        citations = _citations_de_la_preuve(r["preuve"])
        assert citations, r["preuve"]
        veille = (datetime.date.fromisoformat(r["date"]) - datetime.timedelta(days=1)).isoformat()
        for qui, ident in citations:
            intervalles = noyau["citations"].get((qui, ident), [])
            assert any(d <= jour and (not f or jour <= f)
                       for d, f in intervalles for jour in (veille, r["date"])), (r, qui, ident)


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


def test_un_grade_n_a_qu_une_grille_a_la_fois_par_source(durees):
    # Règle 5 de l'étape 3, que la relecture R-B3 (point 1 c) a vue enfreinte au
    # noyau (« Infirmier de classe supérieure », grilles 02948 et 03215 le
    # 2017-01-01) : par source (le LEGI, le noyau), deux rattachements d'un même
    # grade de tableau ne se recouvrent pas.
    par_grade: dict[tuple, list[dict]] = {}
    for d in durees:
        if d["statut"] == "rattache":
            cle = (d["texte"], d["article"], d["tableau"], d["groupe"], d["source"] == "etat")
            par_grade.setdefault(cle, []).append(d)
    for cle, lignes in par_grade.items():
        lignes.sort(key=lambda d: d["debut"])
        for a, b in zip(lignes, lignes[1:]):
            assert a["fin"] and b["debut"] >= a["fin"], (cle, a["grille"], b["grille"])


def _echelons_en_vigueur(echelons, jour):
    return [e for e in echelons if e["debut"] <= jour and (not e["fin"] or jour <= e["fin"])]


def test_les_echelons_de_la_grille_sont_ceux_du_tableau_a_chaque_date(durees):
    # Relecture R-B3-bis, partie 2 : le chaînage réunissait les échelons de
    # toute la période, et rattachait sur des jours où la grille n'a pas ceux du
    # tableau. Chaque jour où les échelons de la grille changent, sur la période
    # rattachée, elle a les rangs du tableau : au LEGI, ceux de son fichier
    # d'échelons ; au noyau, leur nombre, élève, stagiaire et provisoires mis à
    # part (le rang du noyau ordonne sans numéroter).
    import datetime
    tableau: dict[tuple, set[int]] = {}
    for l in _lire(GRILLES / "durees" / "lignes.csv"):
        rangs = tableau.setdefault((l["texte"], l["article"], l["tableau"], l["groupe"]), set())
        if l["rang"] != "0":
            rangs.add(int(l["rang"]))
    legi: dict[tuple, list[dict]] = {}
    for versant in ("etat_legi", "territoriale", "hospitaliere", "militaires"):
        for e in _lire(GRILLES / versant / "echelons.csv"):
            if e["rang"] != "0":
                legi.setdefault((versant, e["texte"], e["grille"]), []).append(e)
    noyau: dict[str, list[dict]] = {}
    for e in _lire(GRILLES / "etat" / "echelons.csv"):
        if e["nature"] not in ("stagiaire", "eleve", "provisoire") and e["rang"] not in ("", "0"):
            noyau.setdefault(e["grille"], []).append(e)
    ecarts = []
    for d in durees:
        if d["statut"] != "rattache":
            continue
        echelons = (noyau.get(d["grille"], []) if d["source"] == "etat"
                    else legi.get((d["source"], d["texte_grille"], d["grille"]), []))
        fin = d["fin"] or "9999-12-31"
        jours = {d["debut"]} | {j for e in echelons for j in (
            e["debut"], (datetime.date.fromisoformat(e["fin"]) + datetime.timedelta(days=1))
            .isoformat() if e["fin"] else "9999-12-31") if d["debut"] < j < fin}
        for jour in sorted(jours):
            presents = {int(e["rang"]) for e in _echelons_en_vigueur(echelons, jour)}
            if d["source"] == "etat":
                presents = set(range(1, len(presents) + 1))
            if presents != tableau[(d["texte"], d["article"], d["tableau"], d["groupe"])]:
                ecarts.append((d["groupe"], d["grille"], d["debut"], d["fin"], jour))
    assert not ecarts, ecarts[:8]


def test_un_grade_n_est_pas_rattache_les_jours_ou_sa_grille_n_a_pas_ses_echelons(durees):
    # Relecture R-B3-bis, partie 2. Décret n° 2015-1275, art. 18
    # (LEGIARTI000035606314, du 2017-01-01 au 2024-03-01) : « Greffier 13e échelon
    # - 12e échelon 4 ans […] ». La grille, décret n° 2015-1277, art. 3 : ses
    # versions LEGIARTI000035603091 (du 2016-01-01 au 2018-01-01) et
    # LEGIARTI000036489952 (du 2018-01-01 au 2023-11-01) ne sont pas lues
    # (`etat_legi/non_lus.csv` : « valeurs hors des lignes ») ; la suivante,
    # LEGIARTI000048278636, en vigueur le 1er novembre 2023 : « Greffier
    # 13e échelon 651 12e échelon 612 […] 1er échelon 426 ». Rattaché du
    # 2023-11-01 au 2024-03-01 ; avant, déclaré, la grille sans échelon.
    lignes = _lignes_de(durees, "LEGIARTI000035606314", "Greffier")
    (rattache,) = [d for d in lignes if d["statut"] == "rattache"]
    assert (rattache["grille"], rattache["debut"], rattache["fin"]) == (
        "greffier", "2023-11-01", "2024-03-01")
    assert "LEGIARTI000048278636" in rattache["preuve"]
    assert "LEGIARTI000035603091" not in rattache["preuve"]
    assert "LEGIARTI000036489952" not in rattache["preuve"]
    (declare,) = [d for d in lignes if d["statut"] == "declare"]
    assert (declare["debut"], declare["fin"]) == ("2017-01-01", "2023-11-01")
    assert "aucun échelon" in declare["raison"] and "greffier" in declare["raison"]
    # Décret n° 2016-2008, art. 12 (LEGIARTI000033792383) : « Lieutenant-colonel
    # 8e échelon - 7e échelon 3 ans et 6 mois […] » ; « Commandant 9e échelon -
    # 8e échelon 3 ans et 6 mois […] ». La grille du dépôt (n° 2016-2007,
    # art. 3, LEGIARTI000033792732 : « 8 1015 7 979 985 995 995 », une valeur
    # seule au 8e échelon sous quatre colonnes datées) n'a le 8e échelon des
    # lieutenants-colonels, et le 9e des commandants, qu'au 2021-01-01.
    for groupe, grille in (("Lieutenant-colonel", "lieutenants-colonels"),
                           ("Commandant", "commandants")):
        lignes = _lignes_de(durees, "LEGIARTI000033792383", groupe)
        (rattache,) = [d for d in lignes if d["statut"] == "rattache"]
        assert (rattache["grille"], rattache["debut"], rattache["fin"]) == (
            grille, "2021-01-01", "2025-06-14")
        (declare,) = [d for d in lignes if d["statut"] == "declare"]
        assert (declare["debut"], declare["fin"]) == ("2017-01-01", "2021-01-01")
        assert "échelons diffèrent" in declare["raison"]


def test_un_grade_se_rattache_les_jours_ou_sa_grille_a_ses_echelons(durees):
    # Relecture R-B3-bis, partie 2 : comparés date par date, les échelons
    # rattachent aussi les jours où la grille a ceux du tableau, quand elle ne
    # les a pas sur toute la période.
    def rattaches(article, groupe):
        return sorted((d["grille"], d["debut"], d["fin"]) for d in _lignes_de(durees, article, groupe)
                      if d["statut"] == "rattache")

    # Décret n° 83-1260, art. 34 (LEGIARTI000034794301, du 2017-09-01 au
    # 2024-01-01) : « Chargés de recherche hors classe 7e échelon - 6e échelon
    # 5 ans […] 1er échelon 1 an ». Décret n° 2012-1162, art. 2, « régis par le
    # décret du 30 décembre 1983 susvisé » : LEGIARTI000034774290 et
    # LEGIARTI000036489856, jusqu'au 2022-05-01, « Chargé de recherche hors
    # classe 7e échelon HEA HEA HEA 6e échelon 1021 […] 1er échelon 767 » ;
    # LEGIARTI000045731731, depuis le 2022-05-01, « Chargé de recherche hors
    # classe Echelon exceptionnel HEB 7e échelon HEA […] ».
    assert rattaches("LEGIARTI000034794301", "Chargés de recherche hors classe") == [
        ("charge-de-recherche-hors-classe", "2017-09-01", "2022-05-01")]
    # Décret n° 2012-1420, art. 18 (LEGIARTI000026796816, du 2013-01-01 au
    # 2016-05-15) : « Infirmier en soins généraux hors classe 11e échelon ― ―
    # 10e échelon 4 ans […] ». Décret n° 2012-1421, art. 1 : LEGIARTI000026797761,
    # jusqu'au 2016-01-01, « Infirmier en soins généraux hors classe 11e échelon
    # 700 730 […] 1er échelon 439 444 » ; LEGIARTI000032546841, depuis, « Infirmiers
    # en soins généraux hors classe 11e échelon 736 - - - 10e échelon […] ». Le
    # lecteur des grilles en fait deux grilles ; chacune a les onze échelons sur
    # son morceau, et l'autre aucun.
    assert rattaches("LEGIARTI000026796816", "Infirmier en soins généraux hors classe") == [
        ("infirmier-en-soins-generaux-hors-classe", "2013-01-01", "2016-01-01"),
        ("infirmiers-en-soins-generaux-hors-classe", "2016-01-01", "2016-05-15")]
    # Décret n° 2016-2008, art. 24 : LEGIARTI000033792407, « Jusqu'au
    # 31 décembre 2019 : […] 3° Le grade de lieutenant-colonel comprend sept
    # échelons » ; LEGIARTI000036439940, depuis le 2017-12-24, « Jusqu'au
    # 31 décembre 2020 », puis « Lieutenant-colonel 7e échelon - 6e échelon
    # 3 ans et 3 mois […] ». La grille du dépôt a sept échelons jusqu'au
    # 2020-12-31 ; l'art. 12, LEGIARTI000036439942, « A compter du 1er janvier
    # 2021 », en donne huit.
    for groupe, grille in (("Lieutenant-colonel", "lieutenants-colonels"),
                           ("Commandant", "commandants")):
        assert rattaches("LEGIARTI000033792407", groupe) == [(grille, "2017-01-01", "2021-01-01")]


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


def test_l_echelon_exceptionnel_se_range_a_sa_place_dans_la_grille():
    # Relecture R-B3-bis, partie 1. Le noyau ordonne les échelons sans les
    # numéroter ; le n-ième, élève, stagiaire et provisoires mis à part, est
    # l'échelon n. Un échelon numéroté garde son numéro, s'il n'est pas
    # l'exceptionnel de la grille ; le spécial ou l'exceptionnel du tableau est
    # l'unique échelon exceptionnel de la grille (le noyau n'a pas de nature
    # « spécial »), à son rang, quel que soit celui que le lecteur lui donne.
    # Grille 02777 le 2011-07-01 : 581, 598, 616, 620, puis 631 exceptionnel.
    natures = ["", "", "", "", "exceptionnel"]
    place = chainage.rang_dans_la_grille
    assert place("exceptionnel", 4, natures) == 5
    assert place("special", 4, natures) == 5
    assert place("4", 4, natures) == 4
    assert place("5", 5, natures) is None
    assert place("6", 6, natures) is None
    assert place("exceptionnel", 4, ["", "", ""]) is None
    assert place("exceptionnel", 2, ["", "exceptionnel", "exceptionnel"]) is None


def test_l_echelon_exceptionnel_des_majors_de_police_est_le_cinquieme_a_l_accueil(
        reclassements):
    # Relecture R-B3-bis, partie 1. Décret n° 2004-1439, art. 23-1
    # (LEGIARTI000023734900) : « Major de police Major de police Echelon
    # exceptionnel Echelon exceptionnel Ancienneté acquise 3e échelon 3e échelon
    # […] » ; la colonne d'accueil n'écrit pas de 4e échelon, et le lecteur des
    # reclassements range l'exceptionnel au-dessus du plus haut écrit, au 4.
    # Décret n° 2010-564, art. 5, la veille (LEGIARTI000023402803, du 2011-01-01
    # au 2011-07-01) : « Major de police Echelon exceptionnel (1) 3e échelon
    # 2e échelon 1er échelon 630 615 597 579 » : l'exceptionnel est le 4e ; le
    # jour (LEGIARTI000023750120, du 2011-07-01 au 2012-01-01) : « Major de police
    # Echelon exceptionnel (1) 4e échelon 3e échelon 2e échelon 1er échelon
    # 631 620 616 598 581 » : il est le 5e, le 4e est l'indice brut 620. Pour les
    # gardiens de la paix, la veille : « Gardien de la paix Exceptionnel (4)
    # 11e échelon […] 1er échelon » : l'exceptionnel est le 12e.
    par_groupe = {r["groupe"]: r for r in reclassements
                  if r["article"] == "LEGIARTI000023734900"}
    majors = par_groupe["Major de police Major de police"]
    assert majors["statut"] == "rattache"
    assert majors["rangs_grille"] == "origine exceptionnel 4 ; accueil exceptionnel 5"
    assert par_groupe["Gardien de la paix Gardien de la paix"]["rangs_grille"] == (
        "origine exceptionnel 12")
    assert par_groupe["Brigadier-chef de police Brigadier-chef de police"]["rangs_grille"] == ""


#: Les visas du décret n° 2016-581 (LEGITEXT000032523056) qui portent un statut
#: de géomètres, lus dans l'index LEGI du dépôt (incrément 20261102-213929).
VISAS_2016_581 = [
    "Vu le décret n° 67-91 du 20 janvier 1967 modifié relatif au statut particulier des "
    "géomètres de l'Institut national de l'information géographique et forestière",
    "Vu le décret n° 2010-983 du 26 août 2010 portant statut particulier du corps des "
    "géomètres-cadastreurs des finances publiques",
]


def test_les_visas_resolvent_la_date_d_un_statut_en_son_numero():
    # « régi par le décret du 20 janvier 1967 susvisé » (n° 2016-581, art. 12,
    # LEGIARTI000032523172) : parmi les visas, seul le n° 67-91 porte cette date.
    assert chainage.decrets_de_la_date(VISAS_2016_581, "1967-01-20") == {"67-91"}
    assert chainage.decrets_de_la_date(VISAS_2016_581, "2010-08-26") == {"2010-983"}
    assert chainage.decrets_de_la_date(VISAS_2016_581, "1990-08-01") == set()
    # Un visa qui nomme le décret qui a modifié le statut ne compte que le statut
    # visé par sa date : arrêté du 28 septembre 2000 (LEGITEXT000019669914).
    visa = ("Vu le décret n° 90-973 du 30 octobre 1990 portant statut particulier du corps "
            "des ingénieurs du génie sanitaire, modifié par le décret n° 2000-972 du "
            "28 septembre 2000")
    assert chainage.decrets_de_la_date([visa], "1990-10-30") == {"90-973"}
    # Deux décrets du même jour : la date ne résout rien seule.
    assert chainage.decrets_de_la_date(
        ["Vu le décret n° 91-1 du 14 mai 1991 portant statut particulier",
         "Vu le décret n° 91-2 du 14 mai 1991 portant statut particulier"],
        "1991-05-14") == {"91-1", "91-2"}


def test_le_decret_qui_a_modifie_le_statut_n_est_pas_un_second_statut():
    # Arrêté du 28 septembre 2000 (LEGITEXT000019669914), « fixant l'échelonnement
    # indiciaire du corps des ingénieurs du génie sanitaire » ; ses visas, lus dans
    # l'index LEGI : « Vu le décret n° 48-1108 du 10 juillet 1948 portant classement
    # hiérarchique des grades et emplois […] » et « Vu le décret n° 90-973 du
    # 30 octobre 1990 portant statut particulier du corps des ingénieurs du génie
    # sanitaire, modifié par le décret n° 2000-972 du 28 septembre 2000, Arrêtent : ».
    # Un seul statut est visé (relecture R-B3, point 2).
    visas = ["Vu le décret n° 48-1108 du 10 juillet 1948 portant classement hiérarchique des "
             "grades et emplois des personnels civils et militaires de l'Etat relevant du "
             "régime général des retraites, ensemble les textes qui l'ont complété ou modifié",
             "Vu le décret n° 90-973 du 30 octobre 1990 portant statut particulier du corps "
             "des ingénieurs du génie sanitaire, modifié par le décret n° 2000-972 du "
             "28 septembre 2000, Arrêtent :"]
    assert chainage._visas_statutaires(visas) == {"90-973"}
    # Arrêté LEGITEXT000019591133 : « Vu le décret n° 94-1020 du 23 novembre 1994
    # fixant les dispositions statutaires communes applicables aux corps des
    # infirmières et infirmiers des services médicaux des administrations de l'Etat,
    # modifié par les décrets n° 96-60 du 24 janvier 1996, n° 98-936 du 13 octobre
    # 1998 et n° 2003-695 du 28 juillet 2003, Arrêtent : ».
    assert chainage._visas_statutaires([
        "Vu le décret n° 94-1020 du 23 novembre 1994 fixant les dispositions statutaires "
        "communes applicables aux corps des infirmières et infirmiers des services médicaux "
        "des administrations de l'Etat, modifié par les décrets n° 96-60 du 24 janvier 1996, "
        "n° 98-936 du 13 octobre 1998 et n° 2003-695 du 28 juillet 2003, Arrêtent :"]) == {
        "94-1020"}
    # Deux statuts visés ensemble restent deux.
    assert chainage._visas_statutaires([
        "Vu le décret n° 2016-201 du 26 février 2016 portant statut particulier du cadre "
        "d'emplois des ingénieurs territoriaux",
        "Vu le décret n° 2016-200 du 26 février 2016 portant statut particulier du cadre "
        "d'emplois des ingénieurs en chef territoriaux"]) == {"2016-201", "2016-200"}


def test_les_geometres_de_l_ign_ne_se_rattachent_pas_aux_geometres_cadastreurs(reclassements):
    # Décret n° 2016-581, art. 12 (LEGIARTI000032523172) : « I. - Au 1er janvier
    # 2016, les fonctionnaires appartenant au corps des géomètres de l'Institut
    # national de l'information géographique et forestière régi par le décret du
    # 20 janvier 1967 susvisé […] sont reclassés dans ce même corps ». Le visa :
    # « Vu le décret n° 67-91 du 20 janvier 1967 modifié relatif au statut
    # particulier des géomètres de l'Institut national de l'information
    # géographique et forestière ». Noyau RH : ce statut (texte 944) est cité par
    # les grades du corps 00395, « Géomètres de l'Institut national de
    # l'information géographique et forestière » ; le corps 01005 des
    # géomètres-cadastreurs des finances publiques ne le cite pas.
    lignes = [r for r in reclassements if r["article"] == "LEGIARTI000032523172"]
    assert len(lignes) == 3
    for r in lignes:
        assert r["statut"] == "declare" and r["corps"] != "01005", r
        assert "67-91" in r["raison"] and "01005" not in r["raison"], r


def test_les_professeurs_des_ecoles_de_polynesie_ne_se_rattachent_pas_a_la_metropole(
        reclassements):
    # Décret n° 2017-786, art. 164 (LEGIARTI000034750879) : « Au 1er septembre
    # 2017, les fonctionnaires appartenant au corps des professeurs des écoles régi
    # par le décret du 23 décembre 2003 susvisé […] » ; le visa : « Vu le décret
    # n° 2003-1260 du 23 décembre 2003 modifié fixant les dispositions statutaires
    # applicables aux professeurs des écoles du corps de l'Etat créé pour la
    # Polynésie française ». Le corps 00021 (métropole) ne cite pas ce statut.
    lignes = [r for r in reclassements if r["article"] == "LEGIARTI000034750879"]
    assert len(lignes) == 2
    for r in lignes:
        assert r["statut"] == "declare" and r["corps"] != "00021", r
        assert "2003-1260" in r["raison"], r


def test_le_statut_nomme_par_sa_date_est_identifie_dans_la_preuve(reclassements):
    # Décret n° 2017-786, art. 139 (LEGIARTI000034750757) : « régi par le décret
    # du 1er août 1990 susvisé » ; le visa : « Vu le décret n° 90-680 du 1er août
    # 1990 modifié relatif au statut particulier des professeurs des écoles » ; au
    # LEGI, LEGITEXT000006076298, « Décret n°90-680 du 1 août 1990 relatif au
    # statut particulier des professeurs des écoles » ; au Noyau RH, le texte 160,
    # cité par le corps 00021.
    (ligne,) = [r for r in reclassements if r["article"] == "LEGIARTI000034750757"
                and r["groupe"] == "Professeur des écoles hors classe"]
    assert ligne["statut"] == "rattache" and ligne["corps"] == "00021"
    assert "décret du 1er août 1990" in ligne["preuve"]
    assert "n° 90-680" in ligne["preuve"] and "LEGITEXT000006076298" in ligne["preuve"]
    assert "texte 160" in ligne["preuve"]


def test_une_phrase_qui_ne_nomme_pas_le_statut_d_un_decret_modificatif_est_declaree(
        reclassements):
    # Décret n° 95-108 (LEGITEXT000005617679), « modifiant le décret n° 92-1204
    # du 10 novembre 1992 portant statut particulier du corps des inspecteurs des
    # affaires maritimes » ; art. LEGIARTI000006476949 : « A compter du 1er août
    # 1993, les inspecteurs de 1re et de 2e classe des affaires maritimes sont
    # reclassés dans le grade d'inspecteur » : la phrase ne nomme aucun statut,
    # et le texte n'est pas lui-même un statut particulier.
    lignes = [r for r in reclassements if r["article"] == "LEGIARTI000006476949"]
    assert lignes
    for r in lignes:
        assert r["statut"] == "declare"
        assert "ne nomme pas le statut" in r["raison"], r


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


def test_un_article_de_durees_que_le_lecteur_n_a_pas_lu_ne_se_dit_pas_absent_du_legi(a_lire):
    # Décret n° 87-1103 (LEGITEXT000006065787), art. 15 (LEGIARTI000006370660),
    # du 1987-12-31 au 1996-02-08 au LEGI : « La durée maximale et la durée minimale
    # du temps passé dans chacun des échelons sont fixées ainsi qu'il suit : GRADES
    # ET ÉCHELONS DUREE Maximale Minimale 7e échelon 3 ans 6 mois 3 ans […] » ; le
    # lecteur des durées ne l'a pas lu (`durees/non_lus.csv` : « échelons dans le
    # désordre »). Le tableau n'y manque pas : il n'est pas lu (relecture R-B3,
    # point 6).
    (ligne,) = [a for a in a_lire if a["texte"] == "LEGITEXT000006065787"]
    assert ligne["cas"] == "non_lu"
    assert "LEGIARTI000006370660" in ligne["detail"]
    assert "échelons dans le désordre" in ligne["detail"]
    # Aucun cas `manque` n'a d'article de durées non lu avant son premier tableau lu.
    premier = {}
    for t in _lire(GRILLES / "durees" / "tableaux.csv"):
        premier[t["texte"]] = min(premier.get(t["texte"], t["debut"]), t["debut"])
    non_lus = _lire(GRILLES / "durees" / "non_lus.csv")
    for a in a_lire:
        if a["cas"] == "manque":
            assert not [n for n in non_lus if n["texte"] == a["texte"]
                        and n["debut"] < premier[a["texte"]]], a
            assert "LEGI" not in a["detail"].split(";")[-1], a
