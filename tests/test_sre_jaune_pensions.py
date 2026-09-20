"""Le lecteur du jaune pensions, sur les lignes que le lecteur PDF lui rend.

Aucun test n'ouvre le document : les lignes ci-dessous sont celles que
`lecture_pdf.lignes_par_page` a rendues du jaune du PLF 2026 le 20 septembre
2026, accents manquants compris — la table Unicode d'une police du document
ne les a pas, et le lecteur ne les invente pas. Les milliers tiennent par une
espace insécable, les cellules sont séparées d'une espace ordinaire.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "fetch"))
import sre_jaune_pensions as jaune  # noqa: E402

NB = " "  # l'insécable des milliers, telle que le lecteur la garde

PAGE_A7 = [
    "FPE - Pensions civiles",
    "FPE - Toutes FPE - Pensions Pensions de la FPT Pensions de la FPH",
    f"Effectif total du rgime 1{NB}339{NB}945 1{NB}654{NB}863 406{NB}645 800{NB}833 630{NB}149",
    f"bnficiaires 165{NB}086 180{NB}010 447 39{NB}933 23{NB}874",
    "bonifications pour services hors d'Europe (\"de dpaysement\")",
    "dure moyenne 17,2 17,3 4,2 18,7 22,1",
    f"bnficiaires 661{NB}815 786{NB}167 24{NB}603 341{NB}086 415{NB}564",
    "bonifications pour enfant",
    "dure moyenne 8,4 8,3 7,7 8,1 8,6",
    f"bnficiaires 62{NB}772 88{NB}932 404{NB}478 6{NB}559 2{NB}339",
    "bonifications pour bnfices de campagne ou du cinquime",
    "dure moyenne 4,9 4,9 27,4 3,2 3,1",
    f"bnficiaires 7{NB}351 8{NB}415 202{NB}113 2{NB}708 54",
    "bonifications pour services ariens ou sous-marins (SASM)",
    "dure moyenne 7,7 7,0 16,9 9,0 5,6",
    f"bnficiaires 13{NB}893 13{NB}893 39 n.d. n.d.",
    "bonifications pour enseignement technique",
    "dure moyenne 16,1 16,1 12,9 n.d. n.d.",
    f"bnficiaires 108{NB}181 108{NB}453 8{NB}126 n.d. n.d.",
    "bonifications ne relevant pas de l'article L12 du CPCMR (2)",
    "dure moyenne 19,1 19,1 5,5 n.d. n.d.",
]

PAGE_50 = [
    "Tableau 50 : Pourcentage de retraités bénéficiaires d’une bonification de pension et",
    "gain moyen associé, dans les 3 fonctions publiques",
    "FPE Civils 9,0% 45,0% 0,9% 0,4% 0,4% 0,0% 6,6% 56,9%",
    "Militaires 0,0% 3,0% 79,4% 58,3% 0,0% 98,4% 2,9% 99,6%",
    "Proportion dans les",
    "FPT liquidants 2,9% 45,2% 1,0% 0,4% n.p. n.p. n.p. 48,3%",
    "FPH 2,4% 64,6% 0,5% 0,0% n.p. n.p. n.p. 66,2%",
    "FPE Civils 19,8 7,9 3,5 11,9 16,2 ns 19,4 11,9",
    "Gain en durée Militaires n.p. 6,4 13,1 11,0 n.p. 16,4 5,8 33,5",
    "d'assurance (en",
    "FPT 36,7 7,4 3,4 9,7 n.p. n.p. n.p. 10,0 trimestres)",
    "FPH 34,8 7,7 2,7 7,2 n.p. n.p. n.p. 8,9",
    "FPE Civils 266 € 195 € 56 € 157 € 330 € n.p. 312 € 246 €",
    "Militaires n.p. 59 € 101 € 69 € n.p. 146 € 59 € 315 €",
    "Gain sur le montant",
    "FPT mensuel de la pension n.d n.d n.d n.d n.d n.d n.d n.d",
    "FPH n.d n.d n.d n.d n.d n.d n.d n.d",
]

PAGE_B1 = [
    "rgime des PCMR de la fonction publique de l'État rgime de la CNRACL",
    f"Ensemble des dparts 38{NB}791 46{NB}932 11{NB}817 58{NB}749 1{NB}326 42{NB}981 19{NB}767 62{NB}748",
    "Hommes (en %) 41,7% 43,8% 84,4% 51,9% 84,5% 41,0% 20,1% 34,4%",
    f"Dparts pour carrire longue 2{NB}649 4{NB}516 99 12{NB}140 2{NB}399 14{NB}539",
    f"Dpart avec bnfice d'une catgorie active (4) 7{NB}913 8{NB}884 n.d (10) 2{NB}151 7{NB}466 9{NB}617",
]


def test_les_valeurs_du_tableau_se_lisent_avec_leurs_unites():
    assert jaune._valeur(f"1{NB}339{NB}945") == 1339945
    assert jaune._valeur("1 339 945") == 1339945
    assert jaune._valeur("27,4") == 27.4
    assert jaune._valeur("9,0%") == 0.09
    assert jaune._valeur("10,4 %") == 0.104
    assert jaune._valeur("266 €") == 266
    assert jaune._valeur("n.d.") is None and jaune._valeur("n.p.") is None
    with pytest.raises(ValueError):
        jaune._valeur("trimestres)")


def test_les_cellules_d_une_ligne_sont_les_nombres_et_les_absences():
    assert jaune._cellules(f"bnficiaires 165{NB}086 180{NB}010 447 39{NB}933 23{NB}874") == [
        f"165{NB}086", f"180{NB}010", "447", f"39{NB}933", f"23{NB}874"]
    assert jaune._cellules("FPE Civils 266 € 195 € 56 € n.p. 312 € 246 €") == [
        "266 €", "195 €", "56 €", "n.p.", "312 €", "246 €"]
    # Un appel de note « (10) » n'est pas une cellule ; « n.d » sans point en est une.
    assert jaune._cellules("actif (4) 7 n.d (10) 2") == ["7", "n.d", "2"]


def test_le_tableau_a7_donne_effectif_beneficiaires_et_durees():
    lu = jaune.tableau_a7([["autre page"], PAGE_A7])
    assert lu["effectif"]["fpe_militaires"] == 406645
    campagne = lu["bonifications"]["campagne_ou_cinquieme"]
    assert campagne["beneficiaires"]["fpe_militaires"] == 404478
    assert campagne["duree_trimestres"]["fpe_militaires"] == 27.4
    assert lu["bonifications"]["hors_l12"]["beneficiaires"]["fpt"] is None
    assert lu["bonifications"]["depaysement"]["duree_trimestres"]["fpt"] == 18.7
    assert list(lu["bonifications"]) == [code for code, _ in jaune.BONIFICATIONS_A7]


def test_le_tableau_a7_refuse_plus_de_beneficiaires_que_de_pensions():
    page = list(PAGE_A7)
    page[3] = f"bnficiaires 165{NB}086 180{NB}010 999{NB}999 39{NB}933 23{NB}874"
    with pytest.raises(ValueError, match="bénéficiaires pour"):
        jaune.tableau_a7([page])


def test_le_tableau_50_range_trois_blocs_par_population():
    lu = jaune.tableau_50([PAGE_50])
    assert lu["proportion"]["fpe_militaires"]["cinquieme_l12"] == 0.984
    assert lu["gain_trimestres"]["fpe_militaires"]["cinquieme_l12"] == 16.4
    assert lu["gain_mensuel_eur"]["fpe_militaires"]["cinquieme_l12"] == 146
    assert lu["gain_mensuel_eur"]["fpe_civils"]["hors_l12"] == 312
    assert lu["gain_mensuel_eur"]["fpt"]["ensemble"] is None
    assert lu["proportion"]["fph"]["enfant"] == 0.646


def test_le_tableau_50_refuse_un_ensemble_sous_une_bonification_seule():
    page = list(PAGE_50)
    page[2] = "FPE Civils 9,0% 45,0% 0,9% 0,4% 0,4% 0,0% 6,6% 40,0%"
    with pytest.raises(ValueError, match="ensemble"):
        jaune.tableau_50([page])


def test_le_tableau_b1_ne_garde_que_les_lignes_completes():
    lu = jaune.tableau_b1([PAGE_B1])
    assert list(lu) == ["ensemble_des_dparts"]
    assert lu["ensemble_des_dparts"]["valeurs"]["cnracl_total"] == 62748
    assert lu["ensemble_des_dparts"]["libelle"] == "Ensemble des dparts"


def test_les_chiffres_cites_par_une_note_sont_ceux_du_jaune():
    note = ("Dénombrée sur le stock : 180 010 des 1 654 863 pensions civiles de "
            "l'État en paiement en 2024 portent une bonification, de 17,3 trimestres "
            "en moyenne (jaune budgétaire, tableau A-7). Le gain est de 266 € "
            "(tableau 50, flux 2023) ; 98,4 % des militaires.")
    assert jaune.chiffres_cites(note) == ["180 010", "1 654 863", "17,3", "266", "98,4"]


def test_la_confrontation_retrouve_les_chiffres_ou_les_nomme(tmp_path):
    tables = {"A-7": jaune.tableau_a7([PAGE_A7]), "50": jaune.tableau_50([PAGE_50]),
              "B-1": jaune.tableau_b1([PAGE_B1])}
    fichier = tmp_path / "avantages.yaml"
    fichier.write_text(
        "avantages:\n"
        "  - code: juste\n"
        "    note: le jaune en compte 404 478 sur 406 645, à 27,4 trimestres, 146 € par mois\n"
        "  - code: faux\n"
        "    note: le jaune en compte 404 479\n"
        "  - code: sans_rapport\n"
        "    note: 12 345 assurés d'après une autre source\n",
        encoding="utf-8")
    trouves, manquants = jaune.confronter(tables, fichier)
    assert trouves == ["juste : 404 478", "juste : 406 645", "juste : 27,4", "juste : 146"]
    assert manquants == ["faux : 404 479"]
