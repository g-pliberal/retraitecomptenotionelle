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


# -- l'édition 2027 : même tableaux, autre mise en page ------------------------

#: L'insécable des milliers posée à part : le lecteur l'entoure de deux espaces.
EP = f" {NB} "

PAGE_50_2027 = [
    "Tableau 50 : Pourcentage de retraités bénéficiaires d’une bonification de pension et gain moyen associé, dans les 3 fonctions publiques",
    "Pour Pour campagne arien ou enseignem Du cinquime Bonifications Ensemble",
    "FPE Civils 8,7% 4,0% 0,9% 0,4% 0,3% 0,0% 7,7% 56,7%",
    "Proportion dans Militaires 0,0% 2,5% 79,4% 57,6% 0,0% 99,0% 3,4% 99,7%",
    "les liquidants",
    "FPT 2,8 % 45,1 % 0,8% 0,4% n.p. n.p. n.p. 49,2 %",
    "FPH 2,7% 63,0 % 0,4% 0,0% n.p. n.p. n.p. 66,2%",
    "Gain en FPE Civils 19,8 7,9 3,5 13,6 17,1 ns 19,7 12,1",
    "dure Militaires n.p. 6,4 12,8 12,2 n.p. 16,5 5,5 34",
    "FPT 35,8 7,4 3,2 9,4 n.p. n.p. n.p. 8,96",
    "126",
]
PAGE_SUIVANTE_2027 = [
    "(en",
    "trimestres) FPH 33,9 7,6 2,8 2,9 n.p. n.p. n.p. 8,7",
    "FPE Civils 285 € 191 € 53 € 155 € 360 € n.p. 301 € 241 €",
    "Militaires n.p. 65 € 107 € 78 € n.p. 146 € 46 € 324 €",
    "pension FPT n.d n.d n.d n.d n.d n.d n.d n.d",
    "FPH n.d n.d n.d n.d n.d n.d n.d n.d",
    "Sources : DGFiP, Service des retraites de l’Etat, base des pensions – CNRACl",
    "FPT 1,0 2,0 3,0 4,0 5,0 6,0 7,0 8,0",
]


def test_l_insecable_posee_a_part_se_recolle_a_ses_chiffres():
    """« 1 \\u00a0 343 \\u00a0 118 » : l'édition 2027 pose l'insécable des
    milliers à part, et le lecteur l'entoure de deux espaces de position."""
    ligne = f"Effectif total du régime 1{EP}343{EP}118 1{EP}656{EP}399 408{EP}750 830{EP}114 640{EP}195"
    assert [jaune._valeur(c) for c in jaune._cellules(ligne)] == [
        1343118, 1656399, 408750, 830114, 640195]
    # Deux nombres voisins restent deux cellules.
    assert jaune._cellules(f"bénéficiaires 13{EP}419 13{EP}419 39 n.d. n.d.") == [
        f"13{NB}419", f"13{NB}419", "39", "n.d.", "n.d."]


def test_le_tableau_50_de_2027_se_suit_sur_la_page_d_apres():
    """Coupé entre deux pages, l'intitulé du bloc devant la population
    (« Gain en FPE Civils … ») : la lecture passe à la page suivante et
    s'arrête à « Sources », sans prendre ce qui la suit."""
    lu = jaune.tableau_50([PAGE_50_2027, PAGE_SUIVANTE_2027])
    assert lu["proportion"]["fpe_civils"]["depaysement"] == 0.087
    assert lu["gain_trimestres"]["fpe_civils"]["hors_l12"] == 19.7
    assert lu["gain_trimestres"]["fph"]["ensemble"] == 8.7
    assert lu["gain_mensuel_eur"]["fpe_militaires"]["cinquieme_l12"] == 146
    assert lu["gain_mensuel_eur"]["fpt"]["ensemble"] is None


def test_une_case_du_tableau_50_que_son_ensemble_dement_est_signalee():
    """4,0 % des civils liquidants à la bonification pour enfant, quand
    l'ensemble est à 56,7 % : la case est fausse — 44,0 % d'après le tableau
    B-22 —, la lecture la garde telle qu'imprimée et le dit. L'édition 2026
    ne dit rien de tel."""
    messages = jaune.incoherences_50(jaune.tableau_50([PAGE_50_2027, PAGE_SUIVANTE_2027]))
    assert len(messages) == 1 and "fpe_civils" in messages[0] and "56,7 %" in messages[0]
    assert jaune.incoherences_50(jaune.tableau_50([PAGE_50])) == []


def test_le_tableau_b1_de_2027_garde_son_libelle_et_ses_huit_valeurs():
    page = [f"Ensemble des départs 39{EP}146 47{EP}104 10{EP}691 57{EP}795 1{EP}382 "
            f"46{EP}897 22{EP}753 69{EP}650",
            "Hommes (en %) 41,8% 43,8% 83,4% 51,1% 84,5% 40,7% 19,3% 33,7%"]
    lu = jaune.tableau_b1([page])
    assert list(lu) == ["ensemble_des_departs"]
    assert lu["ensemble_des_departs"]["libelle"] == "Ensemble des départs"
    assert lu["ensemble_des_departs"]["valeurs"]["cnracl_total"] == 69650


def test_chaque_edition_a_son_jeu_du_manifeste_et_son_fichier():
    import yaml

    racine = Path(__file__).resolve().parents[1]
    manifeste = yaml.safe_load((racine / "data" / "sources.yaml").read_text(encoding="utf-8"))
    ids = {jeu["id"] for institution in manifeste["institutions"].values()
           for jeu in institution.get("jeux", [])}
    assert {e["identifiant"] for e in jaune.EDITIONS.values()} <= ids
    assert len({e["sortie"] for e in jaune.EDITIONS.values()}) == len(jaune.EDITIONS)
    assert jaune.IDENTIFIANT == jaune.EDITIONS[jaune.EDITION]["identifiant"]


#: Le tableau des taux de contribution employeur, tel que le lecteur PDF le
#: rend de l'édition 2027 (tableau 14) : trois taux avant 2006, six ensuite,
#: les renvois « * » et « ** » collés ou non, « 35,01% » sans espace.
PAGE_TAUX_EMPLOYEUR = [
    "Tableau 14 : Taux de contribution employeur des fonctionnaires et des ouvriers d’État",
    "* Ces taux sont plus élevés de 0,10 point en novembre et décembre, en application "
    "du décret du 2 juillet 2012.",
    "civils, et agents CNRACL FSPOEIE",
    "Anne dtachs 49 au titre des ATI militaires cadre",
    "2000 25,60 % 24,00 % 15,50 %",
    "2012 68,59 % 0,33 % 121,55 % 27,30 % * 33,00 % * 15,60 % *",
    "2013 71,78 % ** 0,32 % 126,07 % 28,85 % 33,23 % 15,70 %",
    "2022 74,28 % 0,32 % 126,07 % 30,65 % 35,01% 16,46 %",
    "2026 82,28 % 0,32 % 126,07 % 37,65 % 35,01% 16,67 %",
    "** Taux moyen sur l’année, prenant en compte la baisse ponctuelle de décembre 2013.",
    "En 2020, d’après l’échantillon interrégimes de retraités (EIR), la proportion de "
    "polypensionnés, parmi les",
]


def test_le_tableau_des_taux_employeur_se_lit_par_annee():
    """Six taux par année, les trois derniers avant 2006, quand l'État
    n'appelait rien ; les renvois ne sont pas des valeurs, et une ligne de
    texte qui commence par une année sans taux n'est pas une ligne du
    tableau."""
    lu = jaune.tableau_taux_employeur([PAGE_TAUX_EMPLOYEUR])
    assert list(lu) == ["2000", "2012", "2013", "2022", "2026"]
    assert lu["2000"] == {"cnracl": 0.256, "fspoeie": 0.24, "droit_commun_non_cadre": 0.155}
    assert lu["2012"]["fspoeie"] == 0.33 and lu["2012"]["fpe_militaires"] == 1.2155
    assert lu["2013"]["fpe_civils"] == 0.7178 and lu["2013"]["fspoeie"] == 0.3323
    assert lu["2022"]["fspoeie"] == 0.3501
    assert lu["2026"] == {"fpe_civils": 0.8228, "fpe_ati": 0.0032, "fpe_militaires": 1.2607,
                          "cnracl": 0.3765, "fspoeie": 0.3501,
                          "droit_commun_non_cadre": 0.1667}


def test_le_tableau_des_taux_employeur_se_trouve_a_son_titre_et_refuse_une_ligne_boiteuse():
    """Le numéro du tableau change d'une édition à l'autre — 12 en 2026, 14
    en 2027 — : il se trouve à son titre. Une ligne qui n'a ni trois ni six
    taux ne se range pas sans deviner : la lecture échoue."""
    page_2026 = ["Tableau 12 : Taux de contribution employeur des fonctionnaires et des "
                 "ouvriers d’État", *PAGE_TAUX_EMPLOYEUR[1:]]
    assert jaune.tableau_taux_employeur([page_2026])["2026"]["fspoeie"] == 0.3501
    with pytest.raises(ValueError, match="2014"):
        jaune.tableau_taux_employeur([[*PAGE_TAUX_EMPLOYEUR, "2014 74,28 % 0,32 % 30,40 %"
                                                             " 33,87 %"]])
    with pytest.raises(LookupError):
        jaune.tableau_taux_employeur([PAGE_A7])


# -- les référents : le stock et le flux de 2025, case par case ----------------


def _rangee(intitule: str, *cases: tuple[float, str]) -> list[tuple[float, str]]:
    """Une ligne telle que ``lecture_pdf.fragments_par_page`` la rend du jaune
    du PLF 2027 : l'intitulé à gauche, puis chaque case à son abscisse,
    suivie de l'espace que le document pose au bord de sa case."""
    fragments = [(40.0, intitule)] if intitule else []
    for x, texte in cases:
        fragments += [(x, texte), (x + 16.0, " ")]
    return fragments


def test_les_jetons_tiennent_les_milliers_le_signe_et_les_cases_sans_objet():
    """Les abscisses du jaune du PLF 2027, telles que le lecteur PDF les rend.
    Au tableau A-1, l'insécable des milliers est à quatorze points et demi
    de « 343 » : elle tient pourtant le nombre. Au B-3 bis, le signe moins
    est posé deux points avant ses chiffres, et le tiret d'une case sans
    objet, suivi de l'espace de sa case, reste seul."""
    a1 = [(1.8, "Effectif"), (233.6, "1"), (237.2, NB), (239.0, "343"), (253.4, NB),
          (255.2, "118"), (303.9, "1"), (307.4, NB), (309.2, "656"), (323.7, NB), (325.5, "399")]
    assert jaune._jetons(a1) == [(1.8, "Effectif"), (233.6, f"1{NB}343{NB}118"),
                                 (303.9, f"1{NB}656{NB}399")]
    b3bis = [(200.1, " "), (226.5, "-"), (228.4, "105,6"), (243.5, " "), (319.5, "-"),
             (321.4, " "), (343.4, "-"), (345.3, "127,4")]
    assert jaune._jetons(b3bis) == [(226.5, "-105,6"), (319.5, "-"), (343.4, "-127,4")]
    # Les chiffres posés un à un, le « % » qu'une espace détache, un renvoi.
    b1 = [(40.0, "Taux moyen de surcote (5)"), (138.3, " "), (226.4, "10,"), (226.4, "7 "),
          (226.4, "%"), (244.5, " "), (272.2, "1"), (272.2, "0,"), (272.2, "4%"),
          (288.8, " "), (300.0, "(10)")]
    intitule, cases = jaune._cases(b1, seuil=200.0)
    assert intitule == "Taux moyen de surcote (5)"
    assert [texte for _, texte in cases] == ["10,7%", "10,4%"]
    assert [jaune._valeur_case(t) for t in ("10,7%", f"23{NB}780", "1230", "-212,2", "n.d.(10)",
                                            "n.s.", "-")] == [0.107, 23780, 1230, -212.2,
                                                              None, None, None]


#: Le tableau B-1 de l'édition 2027, aux abscisses du document, ramené à
#: quelques lignes : des cases vides (le total de l'État, les militaires),
#: un intitulé posé sous ses cases, un autre de part et d'autre, une case
#: « n.d » et son renvoi, la page coupée par son numéro.
PAGE_B1_2027 = [
    _rangee("Tableau n°B - 1"),
    _rangee("Pensions de droit direct entrées en paiement en 2025 dans les régimes des pensions"),
    [(40.0, "Ensemble des départs"), (103.8, " "), (226.1, "39"), (233.3, NB), (234.5, "146"),
     (244.5, " "), (270.4, f"47{NB}104"), (315.6, f"10{NB}691"), (358.6, f"57{NB}795"),
     (407.4, f"1{NB}382"), (447.2, f"46{NB}897"), (491.7, f"22{NB}753"), (536.3, f"69{NB}650")],
    _rangee("Hommes (en %)", (228.1, "41,8%"), (271.4, "43,8%"), (315.8, "83,4%"),
            (362.2, "51,1%"), (404.7, "84,5%"), (449.0, "40,7%"), (494.5, "19,3%"),
            (538.1, "33,7%")),
    _rangee("Femmes (en %)", (228.1, "58,2%"), (271.4, "56,2%"), (315.8, "16,6%"),
            (362.2, "48,9%"), (404.7, "15,5%"), (449.0, "59,3%"), (494.5, "80,7%"),
            (538.1, "66,3%")),
    _rangee("Dparts pour carrire longue", (229.7, f"2{NB}617"), (273.2, f"4{NB}704"),
            (412.1, "198"), (448.9, f"12{NB}512"), (495.3, f"2{NB}542"), (537.1, f"15{NB}054")),
    _rangee("Hommes (en %)", (227.1, "43,0%"), (271.4, "48,8%"), (405.7, "91,4%"),
            (449.0, "63,2%"), (493.5, "47,4%"), (538.1, "60,5%")),
    _rangee("Femmes (en %)", (227.1, "57,0%"), (271.4, "51,2%"), (406.7, "8,6%"),
            (449.0, "36,8%"), (493.5, "52,6%"), (538.1, "39,5%")),
    _rangee("Décote et surcote"),
    [(40.0, "Perte mensuelle moyenne lie la dcote (en euros) (5)"), (200.1, " "), (226.6, "-"),
     (228.5, "229,2"), (244.5, " "), (271.7, "-"), (273.6, "217,8"), (288.8, " "),
     (319.7, "-"), (321.6, "99,1"), (333.2, " "), (405.1, "-"), (407.0, "120,5"),
     (422.1, " "), (449.4, "-"), (451.3, "109,8"), (466.4, " "), (493.9, "-"),
     (495.8, "135,2"), (510.9, " "), (539.3, "-"), (541.2, "117,9")],
    [(290.0, "208")],
]
PAGE_B1_2027_SUITE = [
    _rangee("Part des pensions avec surcote (5)", (227.1, "36,9%"), (271.4, "35,2%"),
            (405.6, "17,7%"), (449.0, "23,4%"), (494.4, "17,6%"), (538.9, "21,5%")),
    _rangee("Taux de liquidation"),
    _rangee("", (227.1, "66,3%"), (271.4, "67,1%"), (315.8, "65,3%"), (404.7, "61,1%"),
            (449.0, "50,7%"), (493.5, "53,5%"), (538.1, "51,6%")),
    _rangee("Taux moyen de liquidation (5)"),
    _rangee("Pensions au taux de 80 % (hors surcote, dcote et"),
    _rangee("", (229.0, "4,0%"), (272.0, "3,5%"), (315.8, "33,1%"), (406.0, "0,5%"),
            (450.0, "1,4%"), (495.0, "1,5%"), (539.0, "1,4%")),
    _rangee("minimum garanti)"),
    [(40.0, "Indice moyen la liquidation (5)"), (230.0, "751"), (246.0, " "), (274.0, "726"),
     (290.0, " "), (318.0, "600"), (334.0, " "), (405.0, "n.d"), (410.0, " "), (412.0, "(10)"),
     (430.0, " "), (450.0, "476"), (494.0, "500"), (539.0, "484")],
    _rangee("Sources : DGFiP (Service des retraites de l'État), Caisse des dépôts et consignations"),
    _rangee("Hommes (en %)", (228.1, "1,0%")),
]

GABARIT_B1_ESSAI = jaune.Gabarit(
    "B-1", "tableau n°b - 1", tuple((p, "ensemble") for p in jaune.COLONNES_B1), (
        *jaune._effectifs(None, r"ensemble des d"),
        *jaune._effectifs("carriere_longue", r"carri\w*re longue"),
        (None, "perte_decote_eur", r"perte mensuelle"),
        (None, "part_surcote", r"pensions avec surcote"),
        (None, "taux_liquidation", r"taux moyen de liquidation(?! hors)"),
        (None, "part_taux_80", r"taux de 80"),
        (None, "indice_liquidation", r"indice moyen"),
    ))


def test_une_case_vide_se_reconnait_a_sa_place():
    """« Départs pour carrière longue » a six cases pour huit colonnes : ni
    les militaires ni le total de l'État n'en ont. La place de chaque case
    dit sa colonne ; la ligne de référence, « Ensemble des départs », a
    donné la place de chacune."""
    lu = jaune.tableau_referent([PAGE_B1_2027, PAGE_B1_2027_SUITE], GABARIT_B1_ESSAI)
    assert lu["fpe_civils_hors_poste_orange"]["ensemble"]["departs"] == 39146
    assert lu["cnracl_total"]["ensemble"]["part_femmes"] == 0.663
    longues = {p: champs.get("carriere_longue", {}) for p, champs in lu.items()}
    assert longues["ouvriers_etat"] == {"departs": 198, "part_hommes": 0.914, "part_femmes": 0.086}
    assert longues["fpe_militaires"] == longues["fpe_total"] == {}
    assert lu["fpe_militaires"]["ensemble"]["perte_decote_eur"] == -99.1
    assert "perte_decote_eur" not in lu["fpe_total"]["ensemble"]
    assert lu["fpt"]["ensemble"]["part_surcote"] == 0.234
    assert "part_surcote" not in lu["fpe_militaires"]["ensemble"]


def test_l_intitule_se_lit_au_dessus_au_dessous_ou_de_part_et_d_autre_des_cases():
    """Le jaune pose l'intitulé du taux de liquidation sous ses cases, celui
    des pensions au taux de 80 % de part et d'autre ; une case « n.d » n'a
    pas de valeur, son renvoi n'est pas une case. La lecture passe à la page
    suivante, saute son numéro, et s'arrête à « Sources »."""
    lu = jaune.tableau_referent([PAGE_B1_2027, PAGE_B1_2027_SUITE], GABARIT_B1_ESSAI)
    assert lu["fpe_militaires"]["ensemble"]["taux_liquidation"] == 0.653
    assert "taux_liquidation" not in lu["fpe_total"]["ensemble"]
    assert lu["cnracl_total"]["ensemble"]["part_taux_80"] == 0.014
    assert lu["fpe_civils"]["ensemble"]["indice_liquidation"] == 726
    assert lu["ouvriers_etat"]["ensemble"]["indice_liquidation"] is None


def test_une_ligne_qui_n_est_pas_celle_attendue_arrete_la_lecture():
    """Le gabarit dit l'ordre des lignes : une ligne prise pour une autre, ou
    une ligne qui manque avant « Sources », fait échouer la lecture plutôt
    qu'une valeur rangée sous un autre nom."""
    inverse = jaune.Gabarit("B-1", "tableau n°b - 1", GABARIT_B1_ESSAI.colonnes, (
        *GABARIT_B1_ESSAI.lignes[:6], (None, "part_surcote", r"pensions avec surcote")))
    with pytest.raises(ValueError, match="part_surcote"):
        jaune.tableau_referent([PAGE_B1_2027, PAGE_B1_2027_SUITE], inverse)
    trop = jaune.Gabarit("B-1", "tableau n°b - 1", GABARIT_B1_ESSAI.colonnes, (
        *GABARIT_B1_ESSAI.lignes, (None, "part_minimum_garanti", r"au minimum garanti")))
    with pytest.raises(ValueError, match="part_minimum_garanti. manque|part_minimum_garanti » manque"):
        jaune.tableau_referent([PAGE_B1_2027, PAGE_B1_2027_SUITE], trop)


def test_le_titre_se_reconnait_a_la_ligne_entiere_et_le_droit_derive_suit_le_direct():
    """« Tableau n°B - 3 » n'est pas « Tableau n°B - 3bis ». Le tableau A-1
    porte deux blocs, chacun avec sa ligne « Effectif » : le droit dérivé
    est la seconde."""
    with pytest.raises(LookupError):
        jaune._apres_le_titre([[_rangee("Tableau n°B - 3bis")]], "tableau n°b - 3")
    page = [
        _rangee("Tableau n°A - 1"),
        _rangee("Effectifs de retraités des régimes des pensions civiles et militaires"),
        _rangee("Effectif", (233.6, f"1{NB}343{NB}118"), (303.9, f"1{NB}656{NB}399")),
        _rangee("Âge moyen", (240.0, "75,4"), (310.0, "75,2")),
        _rangee("Effectif", (236.0, f"258{NB}660"), (306.0, f"330{NB}546")),
        _rangee("Âge moyen", (240.0, "78,1"), (310.0, "78,5")),
    ]
    lignes = ((None, "effectif", r"^effectif\b"), (None, "age_moyen", r"age moyen(?! de)"))
    colonnes = (("fpe_civils_hors_poste_orange", "x"), ("fpe_civils", "x"))
    direct = jaune.tableau_referent([page], jaune.Gabarit("A-1", "tableau n°a - 1", colonnes, lignes))
    derive = jaune.tableau_referent([page], jaune.Gabarit("A-1", "tableau n°a - 1", colonnes,
                                                          lignes, rang=1))
    assert direct["fpe_civils"]["x"] == {"effectif": 1656399, "age_moyen": 75.2}
    assert derive["fpe_civils"]["x"] == {"effectif": 330546, "age_moyen": 78.5}


def test_les_referents_se_recoupent_entre_eux():
    """Les sexes font l'effectif, ou cent pour cent ; les totaux, leurs parts ;
    les motifs de départ du B-3, l'ensemble du B-1. Une colonne lue de
    travers s'y verrait."""
    def flux(departs, hommes=0.4):
        return {"departs": departs, "part_hommes": hommes, "part_femmes": round(1 - hommes, 6)}

    lu = {
        "A-1": {"fpe_civils": {"droit_direct": {"effectif": 10, "effectif_hommes": 4,
                                                "effectif_femmes": 6}}},
        "B-1": {"fpe_civils": {"ensemble": flux(100)}, "fpe_militaires": {"ensemble": flux(20)},
                "fpe_total": {"ensemble": flux(120)}, "fpt": {"ensemble": flux(30)},
                "fph": {"ensemble": flux(10)}, "cnracl_total": {"ensemble": flux(40)}},
        "B-3": {"fpe_civils": {"anciennete": flux(90), "motifs_familiaux": flux(4),
                               "invalidite": flux(6)},
                "fpe_militaires": {"anciennete": flux(18), "motifs_familiaux": flux(0),
                                   "invalidite": flux(2)}},
        "B-3bis": {"cnracl_total": {"anciennete": flux(30), "motifs_familiaux": flux(4),
                                    "invalidite": flux(6)}},
        "B-4": {"fpe_civils": {"sedentaire": flux(60), "active_57": flux(15),
                               "active_52": flux(5), "carriere_longue": flux(10)}},
    }
    assert jaune.incoherences_referents(lu) == []
    lu["B-4"]["fpe_civils"]["sedentaire"]["departs"] = 61
    lu["B-1"]["fpt"]["ensemble"]["part_femmes"] = 0.5
    messages = jaune.incoherences_referents(lu)
    assert len(messages) == 2
    assert any("B-3, fpe_civils, anciennete : 90 départs, 91" in m for m in messages)
    assert any("B-1, fpt, ensemble" in m for m in messages)


def test_les_gabarits_de_2027_rangent_chaque_valeur_sous_une_cle_a_elle():
    """Un gabarit ne range pas deux valeurs sous la même clé (population,
    champ, indicateur) — une ligne au champ imposé, qui pourrait le faire,
    est refusée à la lecture (test suivant) — ; sa première ligne est celle
    qui place les colonnes ; les tableaux du flux disent tous les mêmes
    vingt-quatre caractéristiques."""
    for gabarit in jaune.GABARITS:
        assert len(set(gabarit.colonnes)) == len(gabarit.colonnes), gabarit.numero
        cles = [(population, champ, indicateur)
                for population, champ in gabarit.colonnes
                for impose, indicateur, _ in gabarit.lignes if impose is None]
        assert len(set(cles)) == len(cles), gabarit.numero
        assert gabarit.lignes[0][1] in ("departs", "effectif"), gabarit.numero
        if gabarit.numero.startswith("B"):
            assert gabarit.lignes[-24:] == jaune.CARACTERISTIQUES_DU_FLUX, gabarit.numero
    assert [g.numero for g in jaune.GABARITS] == ["A-1", "A-1", "B-1", "B-3", "B-3bis", "B-4", "B-5"]


def test_une_ligne_au_champ_impose_ne_prend_qu_une_case_par_population():
    """« Départ avec bénéfice d'une catégorie active » n'a de cases, au B-3,
    qu'aux départs pour ancienneté : elles se rangent sous le champ
    ``categorie_active``. Une seconde case de la même population y
    écraserait la première ; la lecture la refuse."""
    colonnes = tuple(("fpe_civils", m) for m in jaune.MOTIFS_DE_DEPART)
    gabarit = jaune.Gabarit("B-3", "tableau n°b - 3", colonnes, (
        (None, "departs", r"ensemble des d"),
        ("categorie_active", "departs", r"cat\w*gorie active")))
    page = [_rangee("Tableau n°B - 3"),
            _rangee("Ensemble des départs", (226.0, f"41{NB}812"), (276.0, f"2{NB}545"),
                    (326.0, f"2{NB}747")),
            _rangee("Dpart avec bnfice d'une catgorie active (3) (9)", (228.0, f"8{NB}899"))]
    lu = jaune.tableau_referent([page], gabarit)
    assert lu["fpe_civils"]["categorie_active"] == {"departs": 8899}
    page[-1] = _rangee("Dpart avec bnfice d'une catgorie active", (228.0, f"8{NB}899"),
                       (278.0, "12"))
    with pytest.raises(ValueError, match="deux cases"):
        jaune.tableau_referent([page], gabarit)
