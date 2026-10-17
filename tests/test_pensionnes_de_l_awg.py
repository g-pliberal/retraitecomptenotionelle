"""Les pensionnés de moins de 65 ans de l'Ageing Report, comptés à leurs sources.

L'AWG compte 4,87 millions de pensionnés de moins de 65 ans en 2022, le modèle
2,56 millions de retraités (note du 16 octobre 2026, « la couverture de
2022-2030 ») ; une part des premiers ne recule pas avec l'âge légal, que la
note calait à 20,7 %, 1,01 million, pour refaire leur effet de 2022 à 2070.
Ce module la MESURE (action 138, étape 3, note du 17 octobre 2026), sur le
témoin ``tests/temoins/pensionnes_de_2022.json``
(``scripts/fetch/pensionnes_de_2022.py``) : les retraités de droit direct et
de réversion seule de l'EACR, tous régimes (Ancetre 2022), ses pensionnés
d'invalidité et ses rentiers d'accident du travail, caisse par caisse, les
bénéficiaires de l'AAH de la CNAF, au 31 décembre 2022.

Il tient quatre choses :

* LE TÉMOIN redonne les totaux que ses sources publient ;
* CE QUE L'AWG COMPTE. Sa fiche France range dans l'invalidité l'AAH, les
  rentes d'accident du travail et les pensions d'invalidité (§ 3.1), et
  publie, par tranche d'âge, ses pensionnés rapportés à la population
  (tableau 12). Les retraités, l'invalidité et l'AAH refont ses moins de 60
  ans à moins de 3 % près ; les rentes d'accident du travail en plus, ils les
  dépassent de plus de 10 % : l'AWG ne compte pas leurs rentiers, ou les
  compte ailleurs ;
* LA PART STABLE, MESURÉE : l'invalidité, l'AAH et la réversion seule, que
  l'âge légal ne fait pas reculer, 2,33 millions, 48 % de ses moins de 65 ans,
  plus du double de la part calée ;
* SA DYNAMIQUE : stable, elle garde son rapport à sa population, les 20-64
  ans (``au_perimetre``, ``population_stable``), et non aux 65 ans et plus.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from retraite_notionnelle.facteurs_depense import (
    GRILLE_AWG,
    JEUNES,
    STABLES,
    au_perimetre,
    partager_couverture,
    pensionnes_de_2022,
)

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "pensionnes_de_2022.json"
AWG = RACINE / "tests" / "temoins" / "ageing_report_france.json"
POPULATION = RACINE / "data" / "reference" / "macro" / "population_par_age.csv"


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def awg() -> dict:
    """Les séries de l'annexe de l'AWG, leurs années en entiers."""
    series = json.loads(AWG.read_text(encoding="utf-8"))["series"]
    return {cle: {int(annee): valeur for annee, valeur in serie.items()}
            for cle, serie in series.items()}


def _jeunes_de_l_awg(awg: dict) -> float:
    """Les pensionnés de moins de 65 ans de l'AWG en 2022, en personnes."""
    return (awg["pensionnes"][2022] - awg["pensionnes_65_plus"][2022]) * 1000


def _population_de_2022(premier: int, dernier: int) -> float:
    """La population de ces âges au milieu de 2022, la moyenne de ses 1er
    janvier 2022 et 2023 (INSEE) : c'est celle de l'AWG, dont les 65 ans et
    plus de 2022, 14 350 milliers, sont à 0,02 % de cette moyenne."""
    effectifs = {2022: 0.0, 2023: 0.0}
    with POPULATION.open(encoding="utf-8") as fichier:
        for ligne in csv.reader(l for l in fichier if not l.startswith("#")):
            if ligne[0] in ("2022", "2023") and premier <= int(ligne[1]) <= dernier:
                effectifs[int(ligne[0])] += float(ligne[2])
    return (effectifs[2022] + effectifs[2023]) / 2


def test_le_temoin_des_pensionnes_de_2022_redonne_les_totaux_de_ses_sources(temoin):
    """Chaque table redonne le total que sa source publie : Ancetre, ses
    retraités de droit direct et de réversion seule, résidents en France ou
    non ; chaque caisse de l'EACR, ses pensionnés d'invalidité ; la CNAF, ses
    bénéficiaires de l'AAH de décembre 2022 (s_ben_nat), que la DREES porte à
    la France entière, MSA comprise. Les âges secrétisés laissent quelques
    unités d'écart."""
    assert temoin["date"] == "2022-12-31"
    assert set(temoin["source"]) >= {"eacr", "aah", "aah_france", "ageing_report", "lu_le"}
    assert tuple(temoin["tranches"][:4]) == JEUNES

    def somme(tranches: dict) -> float:
        return sum(tranches[nom] for nom in temoin["tranches"])

    publies = {"droit_direct": (16_974_753, 16_061_968), "reversion_seule": (914_435, 480_024)}
    for categorie, (ensemble, residents) in publies.items():
        assert temoin[categorie]["total"] == ensemble
        assert temoin[categorie]["residents"]["total"] == residents
        assert somme(temoin[categorie]["tranches"]) == pytest.approx(ensemble, abs=10)
        assert somme(temoin[categorie]["residents"]["tranches"]) == pytest.approx(residents,
                                                                                 abs=10)

    invalidite = temoin["invalidite"]["caisses"]
    assert invalidite["0015"]["total"] == 720_914
    for caisse in invalidite.values():
        assert somme(caisse["tranches"]) == pytest.approx(caisse["total"], abs=10)
    assert sum(caisse["total"] for caisse in invalidite.values()) == 842_298

    aah = temoin["aah"]
    assert somme(aah["tranches"]) + aah["indetermine"] == aah["total"] == 1_258_267
    assert aah["total_france"] == 1_294_700
    assert temoin["ageing_report"]["2022"] == {"moins_de_55": 3.1, "55_59": 17.4, "60_64": 64.1}


def test_l_awg_compte_l_invalidite_et_l_aah_mais_pas_les_rentiers_d_accident_du_travail(
        temoin, awg):
    """Le tableau 12 de la fiche France rapporte les pensionnés de 2022 à la
    population de leur âge : 17,4 % des 55-59 ans, 64,1 % des 60-64 ans ; les
    moins de 55 ans sont le reste de ses 4,87 millions de moins de 65 ans.
    Retraités de droit direct, résidents ou non, réversions seules,
    pensionnés d'invalidité et bénéficiaires de l'AAH refont ses moins de 55
    ans et ses 55-59 ans à moins de 3 % ; les rentiers d'accident du travail
    en plus, les dépassent de plus de 10 %. Aux 60-64 ans, il en manque de 4 à
    8 % ; et tous âges, les 65 ans et plus compris, la mesure est à 2 % de ses
    20,26 millions."""
    parts = temoin["ageing_report"]["2022"]
    jeunes = _jeunes_de_l_awg(awg)
    cinquante_cinq = parts["55_59"] / 100 * _population_de_2022(55, 59)
    soixante = parts["60_64"] / 100 * _population_de_2022(60, 64)
    de_l_awg = {"moins_de_55": jeunes - cinquante_cinq - soixante,
                "55_59": cinquante_cinq, "60_64": soixante}

    def par_tranche(mesures: dict) -> dict[str, float]:
        resultat = {nom: sum(categorie[nom] for categorie in mesures.values())
                    for nom in ("moins_de_55", "55_59", "65_et_plus")}
        resultat["60_64"] = sum(categorie["60_61"] + categorie["62_64"]
                                for categorie in mesures.values())
        return resultat

    sans = par_tranche(pensionnes_de_2022(temoin))
    avec = par_tranche(pensionnes_de_2022(temoin, rentes_at_mp=True))
    for tranche in ("moins_de_55", "55_59"):
        assert sans[tranche] == pytest.approx(de_l_awg[tranche], rel=0.03), tranche
        assert avec[tranche] > 1.10 * de_l_awg[tranche], tranche
    assert 0.92 * de_l_awg["60_64"] < sans["60_64"] < 0.96 * de_l_awg["60_64"]
    tous = sum(sans.values())
    assert tous == pytest.approx(awg["pensionnes"][2022] * 1000, rel=0.02)


def test_la_part_stable_mesuree_est_plus_du_double_de_la_part_calee(temoin, awg):
    """L'invalidité (839 731 de moins de 65 ans), l'AAH avant 62 ans (1 140 097
    à la CNAF, portés à la France entière par 1 294 700 / 1 258 267 : après,
    ses bénéficiaires sont aussi retraités) et la réversion seule (315 001) :
    2,33 millions, 47,8 % des moins de 65 ans de l'AWG — la note du 16
    octobre en calait 1,01 million, 20,7 %. Les doubles comptes de l'AAH et
    de l'invalidité, que rien ne mesure ici, la diminueraient."""
    mesures = pensionnes_de_2022(temoin)
    stables = sum(mesures[categorie][tranche] for categorie in STABLES for tranche in JEUNES)
    assert stables == pytest.approx(839_731 + 1_140_097 * 1_294_700 / 1_258_267 + 315_001,
                                    abs=50)
    part = stables / _jeunes_de_l_awg(awg)
    assert 0.46 < part < 0.50
    assert stables > 2 * 1.01e6


def test_la_part_stable_garde_son_rapport_a_sa_population(awg):
    """Rapportée aux 65 ans et plus par défaut, la part stable n'a pas d'effet
    de couverture ; rapportée aux 20-64 ans, elle garde sa prévalence parmi
    eux, et recule, rapportée aux 65 ans et plus, à mesure qu'ils croissent
    plus vite : tout stables, les plus jeunes de l'AWG font, à chaque pas,
    l'effet du rapport des 20-64 ans aux 65 ans et plus, à la mesure de leur
    part de la couverture — plus d'un demi-point de 2022 à 2070."""
    population_65 = {annee: awg["rapport_de_dependance"][annee] / 100
                     * awg["population_20_64"][annee] for annee in GRILLE_AWG}
    population_20_64 = {annee: awg["population_20_64"][annee] for annee in GRILLE_AWG}
    pensionnes = {annee: awg["pensionnes"][annee] for annee in GRILLE_AWG}
    agees = {annee: awg["pensionnes_65_plus"][annee] for annee in GRILLE_AWG}
    part_pib = {annee: awg["depense_brute"][annee] for annee in GRILLE_AWG}
    premiere = GRILLE_AWG[0]
    vieux = agees[premiere] / population_65[premiere]
    jeunes = pensionnes[premiere] / population_65[premiere] - vieux
    arguments = (population_65, vieux, jeunes, pensionnes, agees, population_65)

    for stable in (0.0, 0.48, 1.0):
        defaut = au_perimetre(*arguments, stable=stable)
        explicite = au_perimetre(*arguments, stable=stable, population_stable=population_65)
        for annee in GRILLE_AWG:
            assert explicite[0][annee] == pytest.approx(defaut[0][annee], rel=1e-12)

    tous, tous_ages = au_perimetre(*arguments, stable=1.0, population_stable=population_20_64)
    for annee in GRILLE_AWG:
        assert tous[annee] - tous_ages[annee] == pytest.approx(
            jeunes * population_65[premiere] * population_20_64[annee]
            / population_20_64[premiere], rel=1e-12)
    parts = partager_couverture(part_pib, tous, tous_ages, population_65)
    rapport = {annee: population_20_64[annee] / population_65[annee] for annee in GRILLE_AWG}
    for debut, fin in zip(GRILLE_AWG, GRILLE_AWG[1:]):
        pas = parts["precoce"][fin] - (parts["precoce"][debut] if debut != premiere else 0.0)
        part_des_jeunes = (tous[debut] - tous_ages[debut]) / tous[debut]
        attendu = part_pib[debut] * part_des_jeunes * (rapport[fin] / rapport[debut] - 1.0)
        assert pas == pytest.approx(attendu, rel=1e-9)
    assert parts["precoce"][2070] < -0.5
