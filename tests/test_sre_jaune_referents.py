"""Le lecteur des tableaux référents du jaune pensions du PLF 2027, et ce que
ses tableaux certifiés disent les uns des autres (action 159, étape 4).

Les pages d'essai sont celles du document, aux abscisses que
``lecture_pdf.fragments_par_page`` en rend, ramenées à quelques lignes. Les
tests des tableaux certifiés relisent ce que ``scripts/verifier_donnees.py``
a versé — le JSON du document n'est pas au dépôt — : le stock et le flux dans
``caracteristiques_fonction_publique.csv``, le B-22 et le tableau 50 dans
``bonifications_jaune.csv``.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import sre_jaune_referents as ref  # noqa: E402
from sre_jaune_pensions import incoherences_50  # noqa: E402

NB = " "  # l'insécable des milliers, telle que le lecteur la garde
CARACTERISTIQUES = RACINE / "data/reference/macro/caracteristiques_fonction_publique.csv"
BONIFICATIONS = RACINE / "data/reference/legislation/bonifications_jaune.csv"
POINT = RACINE / "data/reference/legislation/point_indice_fonction_publique.csv"


def _lignes(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as fichier:
        return list(csv.DictReader(l for l in fichier if not l.lstrip().startswith("#")))


def _nombre(texte: str) -> float | int:
    valeur = float(texte)
    return int(valeur) if valeur.is_integer() else valeur


@pytest.fixture(scope="module")
def certifies() -> dict:
    """Les référents certifiés, comme le lecteur les rend : {tableau:
    {(population, champ, modalite, indicateur): valeur}}, le B-22 compris."""
    lu: dict = {}
    for l in _lignes(CARACTERISTIQUES):
        lu.setdefault(l["tableau"], {})[
            (l["population"], l["champ"], l["modalite"], l["indicateur"])] = _nombre(l["valeur"])
    for l in _lignes(BONIFICATIONS):
        if l["tableau"] == "B-22":
            lu.setdefault("B-22", {})[
                (l["population"], l["ligne"], "ensemble", l["mesure"])] = _nombre(l["valeur"])
    return lu


@pytest.fixture(scope="module")
def tableau_50() -> dict:
    """Le tableau 50 certifié, comme ``sre_jaune_pensions.tableau_50`` le rend."""
    lu: dict = {}
    for l in _lignes(BONIFICATIONS):
        if l["tableau"] == "50":
            lu.setdefault(l["mesure"], {}).setdefault(l["population"], {})[l["ligne"]] = (
                _nombre(l["valeur"]))
    return lu


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

GABARIT_B1_ESSAI = ref.Gabarit(
    "B-1", "tableau n°b - 1", tuple({"population": p} for p in ref.POPULATIONS_B1), (
        *ref._effectifs(r"ensemble des d"),
        *ref._effectifs(r"carri\w*re longue", champ="carriere_longue"),
        ref._l(r"perte mensuelle", "perte_decote_eur"),
        ref._l(r"pensions avec surcote", "part_surcote"),
        ref._l(r"taux moyen de liquidation(?! hors)", "taux_liquidation"),
        ref._l(r"taux de 80", "part_taux_80"),
        ref._l(r"indice moyen", "indice_liquidation"),
    ))


def _b1(population: str, indicateur: str, champ: str = "ensemble") -> tuple[str, ...]:
    return (population, champ, "ensemble", indicateur)


def test_les_jetons_tiennent_les_milliers_le_signe_et_les_cases_sans_objet():
    """Les abscisses du jaune du PLF 2027, telles que le lecteur PDF les rend.
    Au tableau A-1, l'insécable des milliers est à quatorze points et demi
    de « 343 » : elle tient pourtant le nombre. Au B-3 bis, le signe moins
    est posé deux points avant ses chiffres, et le tiret d'une case sans
    objet, suivi de l'espace de sa case, reste seul."""
    a1 = [(1.8, "Effectif"), (233.6, "1"), (237.2, NB), (239.0, "343"), (253.4, NB),
          (255.2, "118"), (303.9, "1"), (307.4, NB), (309.2, "656"), (323.7, NB), (325.5, "399")]
    assert ref._jetons(a1) == [(1.8, "Effectif"), (233.6, f"1{NB}343{NB}118"),
                               (303.9, f"1{NB}656{NB}399")]
    b3bis = [(200.1, " "), (226.5, "-"), (228.4, "105,6"), (243.5, " "), (319.5, "-"),
             (321.4, " "), (343.4, "-"), (345.3, "127,4")]
    assert ref._jetons(b3bis) == [(226.5, "-105,6"), (319.5, "-"), (343.4, "-127,4")]
    # Les chiffres posés un à un, le « % » qu'une espace détache, un renvoi.
    b1 = [(40.0, "Taux moyen de surcote (5)"), (138.3, " "), (226.4, "10,"), (226.4, "7 "),
          (226.4, "%"), (244.5, " "), (272.2, "1"), (272.2, "0,"), (272.2, "4%"),
          (288.8, " "), (300.0, "(10)")]
    intitule, cases = ref._cases(b1, seuil=200.0)
    assert intitule == "Taux moyen de surcote (5)"
    assert [texte for _, texte in cases] == ["10,7%", "10,4%"]
    # L'évolution d'une série porte son signe.
    assert [ref._valeur_case(t) for t in ("10,7%", f"23{NB}780", "1230", "-212,2", "n.d.(10)",
                                          "n.s.", "-", "+2,85%")] == [
        0.107, 23780, 1230, -212.2, None, None, None, 0.0285]


def test_une_case_vide_se_reconnait_a_sa_place():
    """« Départs pour carrière longue » a six cases pour huit colonnes : ni
    les militaires ni le total de l'État n'en ont. La place de chaque case
    dit sa colonne ; la ligne de référence, « Ensemble des départs », a
    donné la place de chacune."""
    lu = ref.tableau_referent([PAGE_B1_2027, PAGE_B1_2027_SUITE], GABARIT_B1_ESSAI)
    assert lu[_b1("fpe_civils_hors_poste_orange", "departs")] == 39146
    assert lu[_b1("cnracl_total", "part_femmes")] == 0.663
    longues = {(p, i): v for (p, c, _, i), v in lu.items() if c == "carriere_longue"}
    assert {i: v for (p, i), v in longues.items() if p == "ouvriers_etat"} == {
        "departs": 198, "part_hommes": 0.914, "part_femmes": 0.086}
    assert not any(p in ("fpe_militaires", "fpe_total") for p, _ in longues)
    assert lu[_b1("fpe_militaires", "perte_decote_eur")] == -99.1
    assert _b1("fpe_total", "perte_decote_eur") not in lu
    assert lu[_b1("fpt", "part_surcote")] == 0.234
    assert _b1("fpe_militaires", "part_surcote") not in lu


def test_l_intitule_se_lit_au_dessus_au_dessous_ou_de_part_et_d_autre_des_cases():
    """Le jaune pose l'intitulé du taux de liquidation sous ses cases, celui
    des pensions au taux de 80 % de part et d'autre ; une case « n.d » n'a
    pas de valeur, son renvoi n'est pas une case. La lecture passe à la page
    suivante, saute son numéro, et s'arrête à « Sources »."""
    lu = ref.tableau_referent([PAGE_B1_2027, PAGE_B1_2027_SUITE], GABARIT_B1_ESSAI)
    assert lu[_b1("fpe_militaires", "taux_liquidation")] == 0.653
    assert _b1("fpe_total", "taux_liquidation") not in lu
    assert lu[_b1("cnracl_total", "part_taux_80")] == 0.014
    assert lu[_b1("fpe_civils", "indice_liquidation")] == 726
    assert lu[_b1("ouvriers_etat", "indice_liquidation")] is None


def test_une_ligne_qui_n_est_pas_celle_attendue_arrete_la_lecture():
    """Le gabarit dit l'ordre des lignes : une ligne prise pour une autre, une
    ligne qui manque avant « Sources », une ligne de cases qu'il n'attend
    pas sur la page de sa dernière ligne, font échouer la lecture plutôt
    qu'une valeur rangée sous un autre nom, ou perdue."""
    lignes = GABARIT_B1_ESSAI.lignes
    inverse = ref.Gabarit("X-1", "tableau n°b - 1", GABARIT_B1_ESSAI.colonnes, (
        *lignes[:6], ref._l(r"pensions avec surcote", "part_surcote")))
    with pytest.raises(ValueError, match="« pensions avec surcote » était attendu"):
        ref.tableau_referent([PAGE_B1_2027, PAGE_B1_2027_SUITE], inverse)
    trop = ref.Gabarit("X-1", "tableau n°b - 1", GABARIT_B1_ESSAI.colonnes, (
        *lignes, ref._l(r"au minimum garanti", "part_minimum_garanti")))
    with pytest.raises(ValueError, match="au minimum garanti » manque"):
        ref.tableau_referent([PAGE_B1_2027, PAGE_B1_2027_SUITE], trop)
    oubli = ref.Gabarit("X-1", "tableau n°b - 1", GABARIT_B1_ESSAI.colonnes, lignes[:-1])
    with pytest.raises(ValueError, match="Indice moyen.*n'attend pas"):
        ref.tableau_referent([PAGE_B1_2027, PAGE_B1_2027_SUITE], oubli)


def test_le_tableau_finit_a_sa_source_au_titre_suivant_ou_avec_sa_page():
    """Le jaune pose certains corps de tableau sur une page à eux, leur titre
    et leurs sources sur une autre : le tableau A-3 finit avec sa page, et le
    corps du A-4 vient ensuite, sans titre ni source entre eux. Un tableau
    finit aussi au titre du suivant. Sur sa propre page, une ligne de trop
    reste une erreur."""
    gabarit = ref.Gabarit("X-1", "tableau n°x - 1", ({"population": "fpt"},
                                                     {"population": "fph"}),
                          (ref._l(r"^effectif", "effectif"),))
    corps = _rangee("Effectif", (230.0, "10"), (300.0, "20"))
    suivant = _rangee("Effectif", (230.0, "30"), (300.0, "40"))
    attendu = {("fpt", "ensemble", "ensemble", "effectif"): 10,
               ("fph", "ensemble", "ensemble", "effectif"): 20}
    titre = [_rangee("Tableau n°X - 1"), _rangee("Sources : DGFiP")]
    assert ref.tableau_referent([titre, [corps], [suivant]], gabarit) == attendu
    assert ref.tableau_referent(
        [[_rangee("Tableau n°X - 1"), corps, _rangee("Tableau n°X - 2"), suivant]],
        gabarit) == attendu
    with pytest.raises(ValueError, match="n'attend pas"):
        ref.tableau_referent([[_rangee("Tableau n°X - 1"), corps, suivant]], gabarit)


def test_le_titre_se_reconnait_a_la_ligne_entiere_et_le_droit_derive_suit_le_direct():
    """« Tableau n°B - 3 » n'est pas « Tableau n°B - 3bis ». Le tableau A-1
    porte deux blocs, chacun avec sa ligne « Effectif » : le droit dérivé
    est la seconde, et le droit direct s'arrête où il commence."""
    with pytest.raises(LookupError):
        ref._apres_le_titre([[_rangee("Tableau n°B - 3bis")]], "tableau n°b - 3")
    page = [
        _rangee("Tableau n°A - 1"),
        _rangee("Effectifs de retraités des régimes des pensions civiles et militaires"),
        _rangee("Effectif", (233.6, f"1{NB}343{NB}118"), (303.9, f"1{NB}656{NB}399")),
        _rangee("Âge moyen", (240.0, "75,4"), (310.0, "75,2")),
        _rangee("Effectif", (236.0, f"258{NB}660"), (306.0, f"330{NB}546")),
        _rangee("Âge moyen", (240.0, "78,1"), (310.0, "78,5")),
    ]
    lignes = (ref._l(r"^effectif\b", "effectif"), ref._l(r"age moyen(?! de)", "age_moyen"))
    colonnes = ({"population": "fpe_civils_hors_poste_orange"}, {"population": "fpe_civils"})
    direct = ref.tableau_referent([page], ref.Gabarit("A-1", "tableau n°a - 1", colonnes, lignes,
                                                      defaut={"champ": "droit_direct"}))
    derive = ref.tableau_referent([page], ref.Gabarit("A-1", "tableau n°a - 1", colonnes, lignes,
                                                      rang=1, defaut={"champ": "droit_derive"}))
    assert {(c, i): v for (p, c, _, i), v in {**direct, **derive}.items()
            if p == "fpe_civils"} == {
        ("droit_direct", "effectif"): 1656399, ("droit_direct", "age_moyen"): 75.2,
        ("droit_derive", "effectif"): 330546, ("droit_derive", "age_moyen"): 78.5}


def test_une_ligne_au_champ_impose_ne_prend_qu_une_case_par_population():
    """« Départ avec bénéfice d'une catégorie active » n'a de cases, au B-3,
    qu'aux départs pour ancienneté : elles se rangent sous le champ
    ``categorie_active``. Une seconde case de la même population y
    écraserait la première ; la lecture la refuse."""
    colonnes = tuple({"population": "fpe_civils", "champ": m} for m in ref.MOTIFS_DE_DEPART)
    gabarit = ref.Gabarit("B-3", "tableau n°b - 3", colonnes, (
        ref._l(r"ensemble des d", "departs"),
        ref._l(r"cat\w*gorie active", "departs", champ="categorie_active")))
    page = [_rangee("Tableau n°B - 3"),
            _rangee("Ensemble des départs", (226.0, f"41{NB}812"), (276.0, f"2{NB}545"),
                    (326.0, f"2{NB}747")),
            _rangee("Dpart avec bnfice d'une catgorie active (3) (9)", (228.0, f"8{NB}899"))]
    lu = ref.tableau_referent([page], gabarit)
    assert lu[("fpe_civils", "categorie_active", "ensemble", "departs")] == 8899
    page[-1] = _rangee("Dpart avec bnfice d'une catgorie active", (228.0, f"8{NB}899"),
                       (278.0, "12"))
    with pytest.raises(ValueError, match="deux cases"):
        ref.tableau_referent([page], gabarit)


def test_les_referents_se_recoupent_entre_eux():
    """Les sexes font l'effectif, ou cent pour cent ; les régimes, leur total ;
    les motifs de départ du B-3, l'ensemble du B-1 ; les âges du flux, leur
    total. Une colonne lue de travers s'y verrait. Un tableau que la lecture
    n'a pas rendu ne se recoupe pas."""
    def flux(departs, hommes=0.4):
        return {"departs": departs, "part_hommes": hommes, "part_femmes": round(1 - hommes, 6)}

    def cases(colonnes: dict, modalite: str = "ensemble") -> dict:
        return {(p, c, modalite, i): v for (p, c), indicateurs in colonnes.items()
                for i, v in indicateurs.items()}

    lu = {
        "A-1": cases({("fpe_civils", "droit_direct"): {"effectif": 10, "effectif_hommes": 4,
                                                       "effectif_femmes": 6}}),
        "B-1": cases({("fpe_civils", "ensemble"): flux(100),
                      ("fpe_militaires", "ensemble"): flux(20),
                      ("fpe_total", "ensemble"): flux(120), ("fpt", "ensemble"): flux(30),
                      ("fph", "ensemble"): flux(10), ("cnracl_total", "ensemble"): flux(40)}),
        "B-3": cases({("fpe_civils", "anciennete"): flux(90),
                      ("fpe_civils", "motifs_familiaux"): flux(4),
                      ("fpe_civils", "invalidite"): flux(6),
                      ("fpe_militaires", "anciennete"): flux(18),
                      ("fpe_militaires", "motifs_familiaux"): flux(0),
                      ("fpe_militaires", "invalidite"): flux(2)}),
        "B-3bis": cases({("cnracl_total", "anciennete"): flux(30),
                         ("cnracl_total", "motifs_familiaux"): flux(4),
                         ("cnracl_total", "invalidite"): flux(6)}),
        "B-4": cases({("fpe_civils", c): flux(d) for c, d in (
            ("sedentaire", 60), ("active_57", 15), ("active_52", 5), ("carriere_longue", 10))}),
        "B-9": {**cases({("fph", "ensemble"): {"departs": 10},
                         ("fph", "anciennete_familiaux"): {"departs": 8},
                         ("fph", "invalidite"): {"departs": 2}}),
                **cases({("fph", "ensemble"): {"departs": 7}}, modalite="62"),
                **cases({("fph", "ensemble"): {"departs": 3}}, modalite="63")},
    }
    assert ref.incoherences_referents(lu) == []
    lu["B-4"][("fpe_civils", "sedentaire", "ensemble", "departs")] = 61
    lu["B-1"][("fpt", "ensemble", "ensemble", "part_femmes")] = 0.5
    lu["B-1"][("fpe_total", "ensemble", "ensemble", "departs")] = 121
    lu["B-9"][("fph", "ensemble", "63", "departs")] = 4
    messages = ref.incoherences_referents(lu)
    assert sorted(messages) == sorted([
        "B-1, fpt, ensemble, ensemble : 40,0 % d'hommes et 50,0 % de femmes",
        "B-1, fpe_total, ensemble, ensemble, departs : 121, et 120 dans fpe_civils et "
        "fpe_militaires",
        "B-3 / fpe_civils / anciennete / ensemble / departs : 90, et 91 dans B-4, B-4, B-4, B-4",
        "B-9, fph, ensemble, departs : 10 au total, 11 dans ses modalités",
    ]), messages


def test_une_incoherence_se_declare_et_ne_couvre_que_ses_messages():
    """Une incohérence déclarée explique les messages de son motif ; un autre
    message reste inattendu, et une déclaration que plus rien ne montre se
    voit."""
    messages = ["B-17, fph, invalidite, departs : 3346 au total, 3344 dans ses modalités",
                "B-17, fpt, invalidite, departs : 8516 au total, 8515 dans ses modalités"]
    inattendues, disparues = ref.incoherences_declarees(messages)
    assert inattendues == messages[1:]
    assert len(disparues) == len(ref.INCOHERENCES_DU_DOCUMENT) - 1
    assert all("B-17" not in d for d in disparues)


def test_les_gabarits_couvrent_les_annexes_et_le_flux_ses_vingt_quatre_caracteristiques():
    """Les annexes A et B, sauf l'A-7 que ``sre_jaune_pensions`` lit depuis
    l'étape 2 ; les tableaux du flux par colonne disent tous les mêmes
    vingt-quatre caractéristiques, dans le même ordre."""
    numeros = {g.numero for g in ref.GABARITS}
    assert numeros == {f"A-{n}" for n in (1, 2, 3, 4, 5, 6, 8)} | {
        f"B-{n}" for n in range(1, 23)} | {"B-3bis"}
    for gabarit in ref.GABARITS:
        if gabarit.numero in ("B-1", "B-2", "B-3", "B-3bis", "B-4", "B-5"):
            assert gabarit.lignes[-24:] == ref.CARACTERISTIQUES_DU_FLUX, gabarit.numero


# -- ce que les tableaux certifiés disent --------------------------------------


def test_les_tableaux_certifies_ne_se_contredisent_qu_aux_points_declares(certifies, tableau_50):
    """Le stock et le flux certifiés se recoupent, sauf aux douze points où
    le document se contredit, et au tableau 50 : chacun est déclaré, et
    chaque déclaration se lit encore. Les recoupements ne passent pas à
    vide : seules quatre cases totales manquent au document — l'indice des
    ouvriers de l'État, les militaires partis pour carrière longue ou en
    catégorie active, les ouvriers en catégorie active."""
    messages = incoherences_50(tableau_50) + ref.incoherences_referents(certifies)
    assert ref.incoherences_declarees(messages) == ([], [])
    assert len(ref.INCOHERENCES_DU_DOCUMENT) == 13
    vides = [total for total, _ in ref._recoupements()
             if total[1:] not in certifies.get(total[0], {})]
    assert vides == [
        ("B-1", "ouvriers_etat", "ensemble", "ensemble", "indice_liquidation"),
        ("B-1", "fpe_militaires", "carriere_longue", "ensemble", "departs"),
        ("B-1", "fpe_militaires", "categorie_active", "ensemble", "departs"),
        ("B-1", "ouvriers_etat", "categorie_active", "ensemble", "departs"),
    ]
    assert len(ref._recoupements()) > 400


def test_le_b22_retrouve_les_parts_du_tableau_50_sauf_sa_case_fausse(certifies, tableau_50):
    """Le tableau 50 ne date pas son flux ; le B-22 le dénombre : chaque part
    du 50 est celle de ses bénéficiaires dans les départs de 2025, à
    l'arrondi près, et chaque gain en durée, sa durée moyenne. Sauf la
    bonification pour enfant des civils de l'État : 4,0 % au tableau 50,
    20 736 sur 47 104 au B-22, 44,0 %."""
    b22 = certifies["B-22"]
    comparees = 0
    for population, parts in tableau_50["proportion"].items():
        effectif = b22[(population, "ensemble", "ensemble", "effectif")]
        for code, part in parts.items():
            beneficiaires = b22.get((population, code, "ensemble", "beneficiaires"))
            if code == "ensemble" or beneficiaires is None:
                continue
            if (population, code) == ("fpe_civils", "enfant"):
                assert (part, round(beneficiaires / effectif, 3)) == (0.04, 0.44)
                continue
            assert abs(beneficiaires / effectif - part) <= 0.001, (population, code)
            duree = b22.get((population, code, "ensemble", "duree_trimestres"))
            gain = tableau_50["gain_trimestres"][population].get(code)
            if duree is not None and gain is not None:
                assert abs(duree - gain) <= 0.1 + 1e-9, (population, code)
            comparees += 1
    assert comparees == 20


def test_la_valeur_du_point_du_b14_reste_en_2024_et_2025_a_la_moyenne_de_2023(certifies):
    """La « valeur annuelle moyenne du point d'indice » du B-14 est celle que
    font, en 2022 et en 2023, les relèvements du 1er juillet de chaque année :
    la moitié de l'ancienne valeur et la moitié de la nouvelle. Elle reste
    pourtant à 58,64 € en 2024 et en 2025, quand le point vaut 59,07 € toute
    l'année depuis le 1er juillet 2023 : le document recopie 2023. La case
    reste telle qu'il l'imprime (l'en-tête du fichier certifié le dit)."""
    b14 = {m: v for (p, _, m, i), v in certifies["B-14"].items()
           if i == "valeur_point_annuelle_eur"}
    point = {int(l["annee"]): float(l["valeur"]) for l in _lignes(POINT)}
    for annee in (2022, 2023):
        assert round((point[annee] + point[annee + 1]) / 2, 2) == b14[str(annee)], annee
    assert b14["2024"] == b14["2025"] == b14["2023"] == 58.64
    assert point[2024] == point[2025] == 59.0734
