"""Le recours à l'ASPA par type de ménage, sur la population (action 138, étape 14).

Ines cale le recours à l'ASPA sur les effectifs servis, type de ménage par type
de ménage. ``scripts/recours_aspa.py`` compte les ayants droit de la population
de ``grille_large.py`` par type de ménage et en tire le recours que les
allocataires servis impliquent. Ces tests en tiennent les données, recoupées à
leur source, et le calcul, posé à la main ; la mesure demande la simulation de
la population et se lance à part.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import recours_aspa as R  # noqa: E402

MACRO = RACINE / "data" / "reference" / "macro"


def _lire(nom: str) -> list[dict[str, str]]:
    with (MACRO / nom).open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def test_les_allocataires_somment_au_total_que_la_drees_publie():
    """Le tableau de l'INSEE reprend l'enquête de la DREES sur les allocations du
    minimum vieillesse : isolés et en couple somment à l'ensemble, tranche par
    tranche, à trois cents allocataires près — les années 2009 à 2017, que
    l'enquête répartit et arrondit à part —, à dix près depuis 2018 ; et
    l'ensemble de 2024 est le total
    que la DREES publie, 754 460 allocataires de l'ASV ou de l'Aspa au
    31 décembre 2024 (classeur 2024, tableau A1), à mille près."""
    valeurs = {(int(l["annee"]), l["tranche"], l["sexe"], l["menage"]): float(l["milliers"])
               for l in _lire("allocataires_minimum_vieillesse.csv")}
    assert set(range(2005, 2025)) <= {annee for annee, *_ in valeurs}
    ensembles = [cle for cle in valeurs if cle[3] == "ensemble"]
    assert len(ensembles) == 20 * 7 * 2
    for annee, tranche, sexe, _ in ensembles:
        assert (valeurs[(annee, tranche, sexe, "isoles")]
                + valeurs[(annee, tranche, sexe, "couple")]
                == pytest.approx(valeurs[(annee, tranche, sexe, "ensemble")],
                                 abs=0.31 if annee < 2018 else 0.011))
    total = sum(v for (annee, _, _, menage), v in valeurs.items()
                if annee == 2024 and menage == "ensemble")
    assert total * 1000 == pytest.approx(754_460, abs=1000)


def test_l_etat_matrimonial_redonne_la_population_de_chaque_age():
    """Les quatre états matrimoniaux des deux sexes somment, à chaque âge de 60
    à 89 ans, à la population que le modèle lit (``population_par_age.csv``) :
    deux tableaux de la même estimation de l'INSEE ; et ceux de 90 ans ou plus
    à sa population de 90 à 104 ans, plus les 105 ans ou plus qu'il laisse
    dehors, moins de 0,5 % d'entre eux."""
    population: dict[tuple[int, int], int] = {}
    for l in _lire("population_par_age.csv"):
        population[(int(l["annee"]), int(l["age"]))] = int(l["effectif"])
    sommes: dict[tuple[int, str], int] = {}
    for l in _lire("etat_matrimonial.csv"):
        cle = (int(l["annee"]), l["age"])
        sommes[cle] = sommes.get(cle, 0) + int(l["effectif"])
    assert {2016, 2020} <= {annee for annee, _ in sommes}
    for (annee, age), somme in sommes.items():
        if age == "90_plus":
            jusqu_a_104 = sum(e for (a, g), e in population.items() if a == annee and g >= 90)
            assert 0 < somme - jusqu_a_104 < 0.005 * somme, annee
        else:
            assert somme == population[(annee, int(age))], (annee, age)


def test_les_veuves_se_lisent_parmi_ceux_qui_ne_vivent_pas_en_couple():
    """En 2020, 102 181 des 236 738 femmes de 80 ans sont veuves (INSEE), et
    41,5 % des femmes de 80 ans vivent en couple (recensement de 2021) : parmi
    celles qui ne vivent pas en couple, 0,4316 / 0,585, soit 73,8 %."""
    veuves = R.veuves_parmi_les_seules(RACINE / "data", 2020)
    assert veuves(80, "F") == pytest.approx(102_181 / 236_738 / (1 - 0.415))
    assert 0.0 < veuves(95, "F") <= 1.0
    servis = R.servis(RACINE / "data", 2024)
    assert servis[("isoles", "F", "90+")] == pytest.approx(26_708)
    assert servis[("couple", "H", "65-69")] == pytest.approx(31_476)


def _en_couple(parts):
    return lambda age, sexe: parts[sexe]


def test_une_personne_seule_a_droit_sous_son_plafond_et_sa_reversion_l_en_sort():
    """Une femme de 70 ans, 600 € par mois, cent têtes, qui ne vit pas en
    couple ; la moitié des femmes seules de son âge sont veuves. Plafond d'une
    personne seule : 1 000 € ; réversion : 55 % de la pension du mari, qui
    aurait 72,6 ans — 40 % du poids à 72 ans, 60 % à 73. Les hommes de 72 ans
    touchent 500 ou 2 000 €, dix têtes chacun ; ceux de 73 ans, 500 €.

    Cinquante non veuves ont droit : 600 € sous 1 000, 400 € d'ASPA chacune.
    Une veuve a droit si 600 + 0,55 × p' reste sous 1 000, p' sous 727,27 € :
    les maris de 500 €, une moitié à 72 ans, tous à 73 ans, soit 0,4 × 0,5 +
    0,6 = 0,8 des cinquante veuves, quarante, chacune à 1 000 − 875 = 125 €."""
    lignes = [R.Ligne("F", 70, 600.0, 100.0), R.Ligne("H", 72, 500.0, 10.0),
              R.Ligne("H", 72, 2000.0, 10.0), R.Ligne("H", 73, 500.0, 20.0)]
    droits = R.ayants_droit(lignes, plafond_seul=1000.0, plafond_couple=1500.0,
                            en_couple=_en_couple({"F": 0.0, "H": 1.0}),
                            veuves=lambda age, sexe: 0.5, taux_reversion=0.55, ecart=2.6)
    assert droits.seules[("F", "70-74")] == pytest.approx(90.0)
    assert droits.seules_veuves[("F", "70-74")] == pytest.approx(40.0)
    assert droits.montants["seules"] == pytest.approx(50 * 400.0 + 40 * 125.0)


def test_un_couple_a_droit_sous_le_plafond_du_couple_ses_deux_pensions_comptees():
    """Tous vivent en couple ; plafond du couple : 1 500 €. Le mari a 2,6 ans de
    plus que sa femme.

    L'homme de 66 ans, 700 €, cent têtes : sa femme a 63,4 ans, 60 % du poids à
    63 ans, 40 % à 64. À 63 ans, une femme sur deux touche 500 €, l'autre
    1 200 € ; à 64 ans, toutes 600 €. Le couple a droit sous 1 500 € :
    0,6 × 0,5 + 0,4 = 0,7, soixante-dix couples, à un seul membre en âge de
    l'allocation ; elle leur sert ce qui manque, au plus le montant d'une
    personne seule : 300 € (1 200 €), 200 € (1 300 €).

    L'homme de 68 ans, 900 €, cinquante têtes : sa femme a 65,4 ans, 60 % à 65
    ans (500 €), 40 % à 66 (700 €). 1 400 € ont droit, 1 600 non : trente
    couples, à deux membres en âge, 100 € à partager.

    Côté des femmes de 65 ans et plus : celle de 65 ans, 500 €, dont le mari
    aurait 67,6 ans — seuls ceux de 68 ans sont là, 900 € : 1 400 €, dix têtes
    ont droit ; celle de 66 ans, 700 €, mari de 68 ans : 1 600 €, aucune."""
    lignes = [R.Ligne("H", 66, 700.0, 100.0), R.Ligne("H", 68, 900.0, 50.0),
              R.Ligne("F", 63, 500.0, 10.0), R.Ligne("F", 63, 1200.0, 10.0),
              R.Ligne("F", 64, 600.0, 20.0), R.Ligne("F", 65, 500.0, 10.0),
              R.Ligne("F", 66, 700.0, 10.0)]
    droits = R.ayants_droit(lignes, plafond_seul=1000.0, plafond_couple=1500.0,
                            en_couple=_en_couple({"F": 1.0, "H": 1.0}),
                            veuves=lambda age, sexe: 0.0, taux_reversion=0.55, ecart=2.6)
    assert droits.couples_un == pytest.approx(70.0)
    assert droits.couples_deux == pytest.approx(30.0)
    assert droits.en_couple[("H", "65-69")] == pytest.approx(100.0)
    assert droits.en_couple[("F", "65-69")] == pytest.approx(10.0)
    assert sum(droits.seules.values()) == 0.0
    assert droits.montants["couples"] == pytest.approx(
        100 * (0.6 * 0.5 * 300.0 + 0.4 * 200.0) + 50 * 0.6 * 100.0)


def test_le_recours_rapporte_les_foyers_servis_aux_foyers_qui_ont_droit():
    """130 000 hommes et 43 000 femmes servis en couple font 173 000 couples si
    aucun n'a deux allocataires, 130 000 si chaque femme servie l'est avec son
    mari ; 10 % de couples à deux allocataires en font 173 000 / 1,1. Un
    recours est ce que les servis sont aux ayants droit."""
    assert R.couples_servis(130_000, 43_000, 0.0) == pytest.approx(173_000)
    assert R.couples_servis(130_000, 43_000, 43_000 / 130_000) == pytest.approx(130_000)
    assert R.couples_servis(130_000, 43_000, 0.1) == pytest.approx(173_000 / 1.1)
    assert R.recours(581_000, 1_162_000) == pytest.approx(0.5)
