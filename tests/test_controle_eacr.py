"""L'âge des retraités de la page Coût, l'âge où ils partent et leurs conditions de départ, confrontés à l'EACR.

Les tables H, B et C de l'EACR du 26 mai 2026 comptent, caisse par caisse ou
tous régimes, les retraités par âge, les nouveaux retraités par âge de
liquidation, et ceux qui partent au taux plein, avec une décote ou une
surcote (``tests/temoins/drees_eacr_tables_2026.json``,
``scripts/fetch/drees_eacr_tables.py``) ; ``retraite_notionnelle.controle_eacr``
leur confronte la grille de la page Coût en 2024 (action 138, étape 3). Ce
module tient trois choses :

* LE TÉMOIN, et ce qu'il tient de lui-même : chaque table redonne son total ;
* LA MESURE, sur une grille d'essai : les tranches, les cohortes, les parts ;
* LA CONFRONTATION, sur la grille du dépôt, dans le sens que la note du 16
  octobre 2026 décrit.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from retraite_notionnelle import controle_eacr as M

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json"


@pytest.fixture(scope="module")
def eacr() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


def test_le_temoin_de_l_eacr_dit_sa_source_et_redonne_ses_totaux(eacr):
    """La version du 26 mai 2026 ; dans la table C, les âges détaillés et
    « plus de 95 » redonnent l'ensemble à un pour cent près (quelques âges
    secrétisés manquent), les femmes et les hommes l'ensemble, à l'arrondi
    près ; dans la table H, les trois conditions de la Cnav redonnent sa
    ligne « Ensemble » ; dans la table B, les âges redonnent les liquidants de
    chaque caisse."""
    assert all("26 mai 2026" in fichier for fichier in eacr["fichiers"])
    c = eacr["droits_directs_par_age"]
    assert c["annee"] == M.ANNEE_EACR and c["sources"] == ["Ancetre 2024"]
    for champ in ("ddir", "nl_ddir"):
        serie = c["series"][champ]
        total = serie["ensemble"]["Ensemble"][0]
        detail = sum(e for age, (e, _) in serie["ensemble"].items() if age != "Ensemble")
        assert detail == pytest.approx(total, rel=0.01), champ
        assert serie["F"]["Ensemble"][0] + serie["H"]["Ensemble"][0] == pytest.approx(total, abs=2)
    assert 17.0e6 < c["series"]["ddir"]["ensemble"]["Ensemble"][0] < 17.6e6
    cnav = eacr["conditions_liquidation"]["series"]["0015"]
    for champ in ("flux", "stock"):
        ligne = cnav[champ]["ensemble"][str(M.ANNEE_EACR)]
        assert ligne["taux_plein"] + ligne["decote"] + ligne["surcote"] == ligne["ensemble"]
    b = eacr["liquidants_par_age"]
    assert b["annee"] == M.ANNEE_EACR
    for code, serie in b["series"].items():
        assert sum(e for age, e in serie.items() if age != "Ensemble") == serie["Ensemble"], code


def test_les_tranches_couvrent_tous_les_ages():
    assert M.tranche_de(22) == "moins_60" and M.tranche_de(64) == "60_64"
    assert M.tranche_de(95) == "90_95" and M.tranche_de(96) == "plus_95"
    assert [M.cle_de_depart(a) for a in (55, 60, 67, 68, 80)] == [
        "moins_60", "60", "67", "68_plus", "68_plus"]
    publie = M.publie_par_tranche({"61": [3.0, 1000.0], "63": [1.0, 2000.0],
                                   M.PLUS_DE_95: [2.0, 500.0], "Ensemble": [99.0, 0.0]})
    assert publie == {"60_64": (4.0, 1250.0), "plus_95": (2.0, 500.0)}


def test_une_cohorte_compte_ses_tetes_et_dit_si_elle_part_l_annee_meme():
    """Un cas type de la génération 1960 parti en 2022 : ses cinq cohortes,
    nées de 1958 à 1962, partent de 2020 à 2024 ; la dernière est nouvelle en
    2024. Chacune pèse le poids du cas type fois son effectif ; la pension
    est mensuelle, en euros de l'année ; un cas type sans poids n'y est pas."""
    population = SimpleNamespace(effectif=lambda age, annee: 10.0 if annee == 2024 else 0.0)
    pensionne = SimpleNamespace(
        code="essai", generation=1960, annee_liquidation=2022,
        pensions={"actuel": 12_000.0}, parts_regimes={}, completude=lambda decalage: 1.0)
    absent = SimpleNamespace(**{**vars(pensionne), "code": "absent"})
    lot = M.cohortes([pensionne, absent], {"essai": 0.5}, population, None, 2.0, annee=2024)
    assert sorted(c.age for c in lot) == [62, 63, 64, 65, 66]
    assert {c.age_liquidation for c in lot} == {62}
    assert [c.nouvelle for c in sorted(lot, key=lambda c: -c.tetes)].count(True) == 1
    assert all(c.tetes == 5.0 and c.pension == pytest.approx(2000.0) for c in lot)
    assert M.grille_par_age(lot) == {"62": (5.0, pytest.approx(2000.0))}
    assert M.age_moyen(lot) == 62


def test_les_conditions_de_depart_se_lisent_en_parts(eacr):
    """Chaque caisse de la table H en 2024, flux et stock : ses parts font un,
    la surcote absente à l'Agirc-Arrco, qui n'en sert pas ; les nouveaux
    retraités de la Cnav partent plus souvent décotés et surcotés que tous ses
    retraités, la loi de 2003 ayant ouvert la surcote et élargi la décote aux
    générations récentes."""
    conditions = {(c.caisse, c.champ): c for c in M.conditions_publiees(eacr)}
    for c in conditions.values():
        assert c.taux_plein + c.decote + (c.surcote or 0.0) == pytest.approx(1.0)
    assert conditions[("5600", "flux")].surcote is None
    flux, stock = conditions[("0015", "flux")], conditions[("0015", "stock")]
    assert flux.decote > stock.decote > 0.05 and flux.surcote > stock.surcote > 0.05


@pytest.fixture(scope="module")
def grille():
    return M.controle()


def test_la_grille_compte_ses_retraites_aux_ages_de_l_eacr(grille, eacr):
    """La part de chaque tranche d'âge dans le stock de 2024 à moins de deux
    points et demi de celle de l'EACR (1,6 point au plus le 16 octobre
    2026), et le profil de la pension selon l'âge qui descend, comme celui de
    l'EACR, au-delà de 85 ans : les générations anciennes touchent moins."""
    stock = M.parts(M.grille_par_tranche(grille))
    publie = M.parts(M.publie_par_tranche(eacr["droits_directs_par_age"]["series"]["ddir"]["ensemble"]))
    for nom in publie:
        assert abs(stock.get(nom, 0.0) - publie[nom]) < 0.025, nom
    profil = M.grille_par_tranche(grille)
    moyenne = M.moyenne(profil)
    assert profil["85_89"][1] / moyenne < 0.92 and profil["plus_95"][1] / moyenne < 0.80


def test_la_grille_part_trop_tot_et_trop_groupee(grille, eacr):
    """Les nouveaux retraités de la grille en 2024 : un âge moyen de
    liquidation plus jeune que celui de l'EACR, d'un demi à un an et demi
    (62,7 contre 63,6 le 16 octobre 2026), plus du tiers à 62 ans pour un
    quart — presque la moitié avant que l'agent sédentaire de la CNRACL ne
    porte quatre cinquièmes de sa caisse —, et aucun à 60 ans (carrières longues), ni à 66 ou au-delà de 67
    (carrières incomplètes qui attendent le taux plein). Un écart qui se
    referme dit que la population de l'étape 14 a remplacé la grille, ou
    qu'un âge a bougé."""
    serie = eacr["droits_directs_par_age"]["series"]["nl_ddir"]["ensemble"]
    ecart = M.age_moyen_publie(serie) - M.age_moyen(grille)
    assert 0.5 < ecart < 1.5
    flux, publie = M.parts(M.grille_par_age(grille)), M.parts(M.publie_par_depart(serie))
    assert flux["62"] > 1.3 * publie["62"]
    for cle in ("60", "66", "68_plus"):
        assert flux.get(cle, 0.0) < 0.01 < publie[cle], cle
