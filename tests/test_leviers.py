"""Les trois leviers qui équilibreraient le système, confrontés au COR.

Le rapport annuel du COR de juin 2026 chiffre ce que la pension, le taux de
prélèvement ou l'âge devrait faire, seul, pour équilibrer chaque année
(figure 2.24), et l'ajustement immédiat qui équilibrerait en moyenne jusqu'en
2030, 2045, 2050 ou 2070 (tableau 2.11) ; le dépôt fait de même de son bilan
(``retraite_notionnelle.leviers`` ; action 138, étape 3). Ce module tient
trois choses :

* LE TÉMOIN (``tests/temoins/cor_leviers_2026.json``,
  ``scripts/fetch/cor_leviers.py``), et ce qu'il tient de lui-même.
* LE GESTE DE L'ÂGE. Le COR n'écrit pas comment il passe d'un manque à un
  âge. Appliqué à ses propres séries, celui du module redonne ses âges
  d'équilibre à moins d'un dixième d'année, chaque année de 2030 à 2070,
  quand les deux tiers de ceux que le recul retient comptent parmi les
  cotisants ; tous, il en demanderait moins, la moitié — la part que le dépôt
  a lue dans les évaluations de 2010 —, un peu plus.
* LA CONFRONTATION du système actuel : sous la référence du COR, ses trois
  leviers et son tax gap sont ceux du COR, à l'arrondi de quelques centièmes.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

import pytest

from retraite_notionnelle.leviers import (
    HORIZONS_COR,
    Demographie,
    ecarts_sur_horizon,
    leviers,
    population_entre,
    releve_age,
)

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "cor_leviers_2026.json"
ANNEES = tuple(range(2030, 2071, 5))

#: Les retraités de droit direct, fin 2023, que la DREES compte (17,2
#: millions) : le COR ne publie ses effectifs qu'en croissance (tableau 2.1).
#: Un demi-million de plus ou de moins déplace d'un vingtième la part des
#: retenus en emploi qui refait ses âges.
RETRAITES_2023 = 17.2e6


@pytest.fixture(scope="module")
def cor() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


def test_le_temoin_du_cor_dit_sa_source_et_redonne_le_rapport(cor):
    """La source écrite ; chaque levier de 2024 à 2070, spontané et
    d'équilibre ; les quatre horizons ; et ce que le rapport imprime (p. 124
    et 126) : 67,6 ans en 2070 au lieu de 64,6, la pension relative de 45,3 à
    37,9 %, le pension gap de 8,6 % et le tax gap de 2,8 points en 2070. Le
    tax gap et le pension gap ont le rapport des revenus d'activité aux
    pensions, un peu plus de trois, à chaque horizon."""
    for champ in ("editeur", "reference", "url", "lu_le"):
        assert cor["source"].get(champ), champ
    for levier in ("pension_relative", "age", "taux_prelevement"):
        for serie in ("spontane", "equilibre"):
            assert sorted(map(int, cor["leviers"][levier][serie])) == list(range(2024, 2071))
    age, pension = cor["leviers"]["age"], cor["leviers"]["pension_relative"]
    assert round(age["equilibre"]["2070"], 1) == 67.6
    assert round(age["spontane"]["2070"], 1) == 64.6
    assert round(pension["spontane"]["2070"], 3) == 0.453
    assert round(pension["equilibre"]["2070"], 3) == 0.379
    ecarts = cor["ecarts_sur_horizon"]
    assert sorted(map(int, ecarts["pension_gap"])) == list(HORIZONS_COR)
    assert round(ecarts["pension_gap"]["2070"], 3) == -0.086
    assert round(ecarts["tax_gap"]["2070"], 1) == 2.8
    for horizon in map(str, HORIZONS_COR):
        rapport = -ecarts["tax_gap"][horizon] / 100 / ecarts["pension_gap"][horizon]
        assert 0.30 < rapport < 0.34, horizon


class _Population:
    """Une pyramide plate : ``par_age`` personnes à chaque âge."""

    def __init__(self, par_age: float) -> None:
        self.par_age = par_age

    def effectif(self, age: int, annee: int) -> float:
        return self.par_age


def test_le_recul_deplace_des_generations_entieres_et_avance_sur_une_marge():
    """Sur une pyramide plate de 800 000 personnes par âge, la population
    entre deux âges fractionnaires est leur écart fois une génération ; le
    recul qui relève le rapport des cotisants aux retraités se lit à la main :
    reculer d'un an, la moitié des retenus en emploi, fait de 30 millions de
    cotisants pour 20 millions de retraités 30,4 pour 19,2. Sans manque, pas
    de recul ; avec une marge, l'âge avance."""
    plate = _Population(800_000.0)
    assert population_entre(plate, 2050, 64.5, 66.0) == pytest.approx(1.2e6)
    assert population_entre(plate, 2050, 66.0, 64.5) == pytest.approx(-1.2e6)
    rapport = (30.4 / 19.2) / (30.0 / 20.0)
    assert releve_age(rapport, 20e6, 30e6, plate, 2050, 64.5, 0.5) == pytest.approx(1.0, abs=1e-5)
    assert releve_age(1.0, 20e6, 30e6, plate, 2050) == pytest.approx(0.0, abs=1e-5)
    assert releve_age(0.95, 20e6, 30e6, plate, 2050) < 0.0
    assert (releve_age(1.1, 20e6, 30e6, plate, 2050, part_en_emploi=1.0)
            < releve_age(1.1, 20e6, 30e6, plate, 2050, part_en_emploi=0.5))


def _bilan(soldes: dict[int, float], depenses: dict[int, float]):
    """Un bilan minimal : un solde et une dépense par année, en part de PIB."""
    lignes = {annee: SimpleNamespace(
        annee=annee,
        solde=lambda scenario, s=soldes[annee]: s,
        depense=lambda scenario, d=depenses[annee]: d,
        coefficient=lambda scenario, s=soldes[annee], d=depenses[annee]: (d + s) / d)
        for annee in soldes}
    return SimpleNamespace(annee=lignes.get)


def test_les_leviers_et_les_ecarts_se_lisent_dans_le_bilan():
    """Un système qui dépense 14 % du PIB et en encaisse 12,6 : la pension
    doit perdre 10 %, le taux gagner 1,4 point de PIB rapporté aux revenus
    d'activité, 3,5 points quand ils font 40 % du PIB. Sur deux années de même
    PIB, l'une juste, l'autre ainsi, le pension gap est la moitié du manque
    sur la dépense, et le tax gap la moitié du manque sur les revenus."""
    bilan = _bilan({2030: 0.0, 2031: -0.014}, {2030: 0.14, 2031: 0.14})
    plate = _Population(800_000.0)
    demographie = {annee: Demographie(retraites=20e6, cotisants=30e6) for annee in (2030, 2031)}
    resultat = leviers(bilan, "actuel", 0.4, demographie, plate, (2030, 2031))
    assert resultat[2031].pension == pytest.approx(-0.1)
    assert resultat[2031].prelevement == pytest.approx(0.035)
    assert resultat[2030].age == pytest.approx(0.0, abs=1e-5)
    assert resultat[2031].age > 0.0
    ecarts = ecarts_sur_horizon(bilan, "actuel", 0.4, {2030: 1.0, 2031: 1.0}, 2030, 2031)
    assert ecarts.pension_gap == pytest.approx(-0.05)
    assert ecarts.tax_gap == pytest.approx(0.0175)


def _retraites_par_taux(annee: int) -> float:
    """Les retraités de droit direct que le COR compte, à l'année : ceux de
    la DREES fin 2023, qui croissent comme le COR les fait croître
    (``croissance_depense_retraite.csv``), sous-période par sous-période ; la
    première, 2002-2025, vaut pour 2024 et 2025."""
    import csv

    chemin = RACINE / "data" / "reference" / "macro" / "croissance_depense_retraite.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = [ligne for ligne in csv.DictReader(l for l in flux if not l.startswith("#"))
                  if ligne["grandeur"] == "retraites"]
    retraites = RETRAITES_2023
    for ligne in lignes:
        debut, fin = map(int, ligne["periode"].split("-"))
        debut = max(debut, 2023)
        retraites *= (1.0 + float(ligne["taux"])) ** max(0, min(annee, fin) - debut)
    return retraites


@pytest.mark.parametrize("part_en_emploi, ecart_minimal, ecart_maximal", [
    (0.65, -0.1, 0.1),
    (0.5, 0.0, 0.3),
    (1.0, -0.4, 0.0),
])
def test_le_geste_de_l_age_refait_les_ages_d_equilibre_du_cor(
        cor, part_en_emploi, ecart_minimal, ecart_maximal):
    """Sur les séries du COR seules — ses cotisants par retraité, sa pension
    relative spontanée et d'équilibre, son âge spontané, où se prend la
    génération déplacée —, le recul du module redonne l'âge d'équilibre du
    COR à un dixième d'année près, chaque année de 2030 à 2070, quand les deux
    tiers des retenus comptent parmi les cotisants. La moitié, la part que le
    dépôt a lue (``Parametres.part_reportes_en_emploi``), demande un peu plus
    d'âge, jusqu'à 0,3 an en 2070 ; tous, un peu moins."""
    from retraite_notionnelle.donnees.equilibre import DecompositionDepense
    from retraite_notionnelle.donnees.population import Population

    population = Population(RACINE / "data")
    decomposition = DecompositionDepense(RACINE / "data" / "reference" / "macro")
    age, pension = cor["leviers"]["age"], cor["leviers"]["pension_relative"]
    for annee in ANNEES:
        cle = str(annee)
        rapport = pension["spontane"][cle] / pension["equilibre"][cle]
        retraites = _retraites_par_taux(annee)
        cotisants = decomposition.valeur("cotisants_par_retraite", "ensemble", annee) * retraites
        recul = releve_age(rapport, retraites, cotisants, population, annee,
                           age["spontane"][cle], part_en_emploi)
        publie = age["equilibre"][cle] - age["spontane"][cle]
        assert ecart_minimal <= recul - publie <= ecart_maximal, (annee, recul, publie)


@lru_cache(maxsize=None)
def _leviers(scenario: str):
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.leviers import leviers_du_modele

    return leviers_du_modele(Parametres(), scenario)


def test_les_leviers_du_systeme_actuel_sont_ceux_du_cor(cor):
    """Sous la référence du COR, chaque année de 2030 à 2070 : le recul de
    l'âge du système actuel est celui du COR à 0,1 an près (3,06 ans en 2070,
    3,02 au COR) ; le relèvement du taux, à 0,15 point (5,63 points en 2070,
    5,56) ; la baisse de la pension, à un point, le modèle rognant un peu
    moins — sa dépense compte, avec les pensions, ce que le levier n'atteint
    pas."""
    annuels = _leviers("actuel").annuels
    leviers_cor = cor["leviers"]
    for annee in ANNEES:
        cle = str(annee)
        modele = annuels[annee]
        age = leviers_cor["age"]["equilibre"][cle] - leviers_cor["age"]["spontane"][cle]
        taux = (leviers_cor["taux_prelevement"]["equilibre"][cle]
                - leviers_cor["taux_prelevement"]["spontane"][cle])
        pension = (leviers_cor["pension_relative"]["equilibre"][cle]
                   / leviers_cor["pension_relative"]["spontane"][cle] - 1.0)
        assert abs(modele.age - age) < 0.1, (annee, modele.age, age)
        assert abs(modele.prelevement - taux) < 0.0015, (annee, modele.prelevement, taux)
        assert 0.0 <= modele.pension - pension < 0.01, (annee, modele.pension, pension)


def test_le_tax_gap_du_systeme_actuel_est_celui_du_cor(cor):
    """Sur les quatre horizons du tableau 2.11, cumulés en euros constants
    depuis 2026 : le tax gap du système actuel est celui du COR à 0,1 point
    près (2,78 points en 2070, 2,76 au COR) ; le pension gap, à un
    demi-point, le modèle rognant un peu moins (8,2 % en 2070, 8,6 %)."""
    horizons = _leviers("actuel").horizons
    ecarts = cor["ecarts_sur_horizon"]
    for fin in HORIZONS_COR:
        modele = horizons[fin]
        assert abs(100 * modele.tax_gap - ecarts["tax_gap"][str(fin)]) < 0.1, fin
        assert 0.0 <= modele.pension_gap - ecarts["pension_gap"][str(fin)] < 0.005, fin


def test_la_proposition_s_equilibre_en_2070_sans_levier():
    """La proposition, qui suit son compte, finit sa trajectoire à
    l'équilibre : en 2070, aucun levier n'a à bouger d'un point ni d'un an.
    Son manque est celui de la transition : sur 2026-2070, son tax gap
    approche celui du système actuel."""
    liberal = _leviers("notionnel_liberal")
    fin = liberal.annuels[2070]
    assert abs(fin.pension) < 0.02 and abs(fin.prelevement) < 0.01 and abs(fin.age) < 0.5
    assert liberal.horizons[2070].tax_gap > 0.0
