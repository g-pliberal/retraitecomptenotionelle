"""Les chiffres de 2024 du panorama de la DREES, édition 2026, recoupés au dépôt.

L'action 178, étape 2 : chaque total que le panorama « Les retraités et les
retraites » publie d'une source que le dépôt lit déjà est recoupé au fichier
qu'il lit, à l'arrondi de la publication. Ces sources sont l'EACR, par son
cadrage (``data/reference/regimes/effectifs_retraites.csv``) et par ses
tables B, C et H (``tests/temoins/drees_eacr_tables_2026.json``), et les
comptes de la protection sociale (``data/reference/macro/depenses_retraite.csv``).

Les valeurs attendues sont lues dans le PDF, à la page imprimée que chaque test
cite ; celles qu'il ne chiffre pas, dans le classeur de la fiche, le membre
``fiche_NN.xlsx`` de l'archive ``drees_panorama_retraites_2026_classeurs``, à
la feuille citée. Ce que le dépôt ne porte pas, ou porte autrement, est dit
dans la note de l'étape (``docs/feuille_de_route/178/``) : les effectifs de la
réversion, dont le dépôt ne garde que la masse ; les pensions de retraite au
sens strict, 395,3 milliards, dont il n'a pas les sous-postes.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
EACR = RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json"
EFFECTIFS = RACINE / "data" / "reference" / "regimes" / "effectifs_retraites.csv"
DEPENSES = RACINE / "data" / "reference" / "macro" / "depenses_retraite.csv"


def _lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


@pytest.fixture(scope="module")
def eacr() -> dict:
    return json.loads(EACR.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def effectifs() -> dict[tuple[int, str], float]:
    return {(int(l["annee"]), l["caisse"]): float(l["effectifs"]) for l in _lire(EFFECTIFS)}


#: Fiche 1, tableau 1 (page 21) : les retraités de droit direct tous régimes,
#: ensemble, en milliers, fin de chaque année.
RETRAITES_TOUS_REGIMES = {
    2004: 12_961, 2005: 13_263, 2006: 13_636, 2007: 14_022, 2008: 14_418,
    2009: 14_743, 2010: 15_082, 2011: 15_291, 2012: 15_349, 2013: 15_629,
    2014: 15_828, 2015: 15_980, 2016: 16_135, 2017: 16_252, 2018: 16_496,
    2019: 16_712, 2020: 16_674, 2021: 16_801, 2022: 16_975, 2023: 17_184,
    2024: 17_298,
}


def test_les_retraites_de_droit_direct_de_2004_a_2024_sont_ceux_du_cadrage(effectifs):
    """Les 17,3 millions de retraités de droit direct de fin 2024, et chaque
    année depuis 2004 : la ligne « Tous régimes » (code 0000) du cadrage de
    l'EACR, à mille près. Le panorama les tire de l'EIR et d'Ancetre, que le
    cadrage reprend tous régimes."""
    for annee, milliers in RETRAITES_TOUS_REGIMES.items():
        assert effectifs[(annee, "tous_regimes")] / 1000 == pytest.approx(milliers, abs=0.5), annee


#: Fiche 1, tableau 2 (page 23) : les retraités de droit direct de fin 2024,
#: par régime, en milliers ; les lignes qui sont une caisse du cadrage. Les
#: régimes spéciaux (663) et les professions libérales (493) en réunissent
#: plusieurs, dont certaines que le cadrage ne porte pas (Altadis, Retrep).
RETRAITES_PAR_REGIME_2024 = {
    "cnav": 14_745, "agirc_arrco": 12_796, "msa_salaries": 1_679,
    "msa_exploitants": 1_023, "fonction_publique_etat_civile": 1_641,
    "ircantec": 2_109, "cnracl": 1_393,
}


def test_les_retraites_de_2024_par_regime_sont_ceux_du_cadrage(effectifs):
    for caisse, milliers in RETRAITES_PAR_REGIME_2024.items():
        assert effectifs[(2024, caisse)] / 1000 == pytest.approx(milliers, abs=0.5), caisse


def test_les_retraites_de_2024_par_sexe_et_leur_pension_sont_ceux_de_la_table_c(eacr):
    """Fiche 1, tableau 1 (page 21) : 9 192 000 femmes et 8 106 000 hommes ;
    fiche 5, feuille « F05_Tableau 1 compl_bis », les retraités résidant en
    France ou à l'étranger : une pension de droit direct de 1 647 euros bruts
    par mois en moyenne, hors majoration pour trois enfants, 1 320 pour les
    femmes, 2 017 pour les hommes. La table C de l'EACR (Ancetre 2024) porte
    les mêmes têtes et les mêmes montants."""
    serie = eacr["droits_directs_par_age"]["series"]["ddir"]
    for sexe, milliers, euros in (("F", 9_192, 1_320), ("H", 8_106, 2_017),
                                  ("ensemble", 17_298, 1_647)):
        tetes, montant = serie[sexe]["Ensemble"]
        assert tetes / 1000 == pytest.approx(milliers, abs=0.5), sexe
        assert montant == pytest.approx(euros, abs=0.5), sexe


def test_les_liquidants_de_2024_sont_ceux_des_tables_b_et_c(eacr):
    """Fiche 2, tableau 1 (page 30) : 858 000 assurés ont liquidé un droit
    direct en 2024, 435 000 femmes et 423 000 hommes — le champ ``nl_ddir`` de
    la table C, à mille près pour les hommes, 422 466, que le tableau porte à
    423 000 quand femmes et hommes y font l'ensemble ; les 718 000
    primo-liquidants, que l'EIR seul compte, n'ont pas d'équivalent dans
    l'EACR. Fiche 2, tableau 2 (page 33), colonne 2024 : 648 000 au régime
    général, 43 000 à la MSA salariés, 30 000 à la MSA non-salariés et 63 000
    à la CNRACL — les liquidants de la table B."""
    serie = eacr["droits_directs_par_age"]["series"]["nl_ddir"]
    for sexe, milliers, ecart in (("F", 435, 0.5), ("H", 423, 1.0), ("ensemble", 858, 0.5)):
        assert serie[sexe]["Ensemble"][0] / 1000 == pytest.approx(milliers, abs=ecart), sexe
    table_b = eacr["liquidants_par_age"]["series"]
    for code, milliers in (("0015", 648), ("0021", 43), ("0022", 30), ("0032", 63)):
        assert table_b[code]["Ensemble"] / 1000 == pytest.approx(milliers, abs=0.5), code


#: Fiche 16, feuille « F16_Graphique 3 » : la répartition des nouveaux
#: retraités de 2024 selon leur âge au 31 décembre, en %, par régime.
TRANCHES = ("moins de 57", "57 à 59", "60", "61", "62", "63 à 64", "65", "66", "plus de 66")
REPARTITION_PAR_AGE_2024 = {
    "0015": (0.1, 0.2, 5.5, 9.6, 28.5, 27.8, 7.2, 4.5, 16.7),    # régime général
    "0021": (0.1, 0.2, 5.4, 11.2, 26.8, 24.5, 6.9, 3.9, 21.0),   # MSA salariés
    "0022": (0.0, 0.1, 3.4, 11.2, 23.0, 25.4, 6.6, 4.9, 25.2),   # MSA non-salariés
    "0032": (0.2, 5.2, 6.4, 9.9, 29.0, 30.9, 6.7, 3.9, 7.8),     # CNRACL
}


def _tranche(age: str) -> str:
    if not age.isdigit():
        return {">70": "plus de 66"}.get(age, "moins de 57")  # « <50 », « 50 à 54 »
    age = int(age)
    if age < 57:
        return "moins de 57"
    if age <= 59:
        return "57 à 59"
    if age in (63, 64):
        return "63 à 64"
    return str(age) if age <= 66 else "plus de 66"


def test_l_age_des_nouveaux_retraites_de_2024_est_celui_de_la_table_b(eacr):
    """La table B compte les liquidants de chaque caisse par âge ; regroupés
    comme le graphique, ils en redonnent chaque part, au dixième près."""
    table_b = eacr["liquidants_par_age"]["series"]
    for code, parts in REPARTITION_PAR_AGE_2024.items():
        serie = table_b[code]
        compte = dict.fromkeys(TRANCHES, 0.0)
        for age, tetes in serie.items():
            if age != "Ensemble":
                compte[_tranche(age)] += tetes
        for tranche, part in zip(TRANCHES, parts):
            assert 100 * compte[tranche] / serie["Ensemble"] == pytest.approx(part, abs=0.051), (
                code, tranche)


#: Fiche 17, feuilles « F17_Tableau compl - Decote » et « … - Surcote » : la
#: part des nouveaux retraités de 2024 partis avec une décote, puis avec une
#: surcote, en %, et le code de la caisse dans la table H.
DECOTE_SURCOTE_2024 = {
    "0015": (13.4, 18.9),   # régime général
    "0021": (6.6, 18.3),    # MSA salariés
    "0022": (5.0, 33.9),    # MSA non-salariés
    "0012": (18.4, 37.6),   # FPE civils
}


def test_la_decote_et_la_surcote_des_nouveaux_retraites_de_2024_sont_celles_de_la_table_h(eacr):
    """Les liquidants de 2024 de la table H, partis avec une décote ou une
    surcote, rapportés à l'ensemble : les parts du panorama au dixième près,
    sauf une. La surcote des fonctionnaires civils de l'État y est de 38,9 %
    (le cube du SRE de 2024), et de 37,6 % au panorama : l'écart est déclaré,
    non expliqué, et ce test le tient pour qu'il ne change pas en silence."""
    table_h = eacr["conditions_liquidation"]["series"]
    for code, (decote, surcote) in DECOTE_SURCOTE_2024.items():
        flux = table_h[code]["flux"]["ensemble"]["2024"]
        assert 100 * flux["decote"] / flux["ensemble"] == pytest.approx(decote, abs=0.051), code
        mesure = 100 * flux["surcote"] / flux["ensemble"]
        if code == "0012":
            assert mesure == pytest.approx(38.9, abs=0.051)
            assert mesure - surcote == pytest.approx(1.3, abs=0.06)
        else:
            assert mesure == pytest.approx(surcote, abs=0.051), code


def test_le_risque_vieillesse_survie_de_2024_est_celui_des_comptes():
    """Fiche 10, encadré 1 (page 99) : 426,7 milliards d'euros de prestations
    du risque vieillesse-survie en 2024, dont 395,3 de pensions de retraite des
    régimes obligatoires (le champ du tableau 1, page 100). Le dépôt porte le
    poste E11-2 entier, qui est le premier chiffre."""
    depenses = {int(l["annee"]): float(l["depenses_meur"]) for l in _lire(DEPENSES)}
    assert depenses[2024] / 1000 == pytest.approx(426.7, abs=0.05)
