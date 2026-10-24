"""La CSG effective et la dépense nette, confrontées à la DREES et à l'Ageing Report.

La page Coût chiffre la dépense en brut ; l'Ageing Report publie, à côté, ce
que l'État en reprend. Le dépôt lit ce que les prélèvements sociaux retirent
vraiment à la masse des pensions dans deux moyennes de la DREES, la pension
brute et la nette (``tests/temoins/drees_pension_nette.json``,
``scripts/fetch/drees_pension_nette.py`` ; ``retraite_notionnelle.depense_nette``,
action 138, étape 3). Ce module tient :

* LE TÉMOIN, sa source et ses années ;
* LE TAUX EFFECTIF, entre deux bornes chaque année : au-dessus du taux que
  paieraient les retraités, par tête, à leur taux de CSG, au-dessous du taux
  plein et de la cotisation maladie entière ; et il suit le barème — la
  hausse de la CSG de 2018, le taux médian de 2019 ;
* LA PART DE L'AWG, constante, plus large que le taux effectif de l'impôt sur
  le revenu des pensions ;
* LA DÉPENSE NETTE, au taux tenu après la dernière année publiée ;
* LE TAUX DANS LE MODÈLE (138.3, le 24 octobre 2026) : les montants du
  tableau 2.1-a, certifiés dans ``data/reference/macro/pensions_brutes_nettes.csv``
  sur ce que le récupérateur dépose dans ``data/brut/`` ; ``DepensesRetraite``
  les lit, et le bilan de la page Coût en tire la dépense nette de chaque
  système.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.depense_nette import (
    borne_par_les_tetes,
    depense_nette,
    part_reprise_par_l_awg,
    taux_du_bareme,
    taux_effectifs,
    taux_projetes,
)
from retraite_notionnelle.donnees.prelevements_historiques import (
    charger_prelevements_historiques,
)

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "drees_pension_nette.json"
AWG = RACINE / "tests" / "temoins" / "ageing_report_france.json"
FICHIER = RACINE / "data" / "reference" / "macro" / "pensions_brutes_nettes.csv"

sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import drees_pension_nette as recuperateur  # noqa: E402


def _grille(lignes: list[list]) -> dict[tuple[int, int], float | str]:
    """Une feuille comme ``lecture_xlsx.feuilles`` la rend : les cellules vides
    absentes."""
    return {(r, c): v for r, ligne in enumerate(lignes) for c, v in enumerate(ligne)
            if v is not None}


#: Le tableau 2.1-a tel qu'il se lit : les intitulés aux lignes 4 et 5, puis
#: une ligne par année, la pension moyenne brute et la nette de droit direct
#: aux colonnes 7 et 10, toutes pensions comprises aux colonnes 13 et 16.
MONTANTS = [[None] * 17 for _ in range(6)] + [
    ["2021", *[None] * 6, 1482.0, None, None, 1380.0, None, None, 1629.0, None, None, 1519.0],
    ["2022", *[None] * 6, 1565.0, None, None, 1457.0, None, None, 1719.0, None, None, 1602.0],
]
for _colonne, _intitule in ((7, "brute"), (10, "nette"), (13, "brute"), (16, "nette")):
    MONTANTS[4][_colonne] = _intitule
MONTANTS[5][7] = MONTANTS[5][16] = "Ensemble"

#: La feuille ``A-Prelev_sociaux`` de l'EACR : une ligne tous régimes par
#: droit, et une d'une caisse, que le lecteur écarte.
CSG = [
    ["CC", "PSoc", "Année", "Droit", "exonération", "txRéduit", "txMédian", "txPlein",
     "txInconnu", "ensemble", "Source"],
    ["0000", "CSG", 2022, "Direct", 3000.0, 2000.0, 3000.0, 6000.0, 0.0, 14000.0, "Ancetre"],
    ["0000", "CSG", 2022, "Dérivé", 1500.0, 500.0, 500.0, 1000.0, 0.0, 3500.0, "Ancetre"],
    ["5000", "CSG", 2022, "Direct", 1.0, 1.0, 1.0, 1.0, 0.0, 4.0, "EACR"],
]


@pytest.fixture(scope="module")
def drees() -> dict:
    temoin = json.loads(TEMOIN.read_text(encoding="utf-8"))
    for partie in ("montants", "csg"):
        temoin[partie] = {int(annee): valeurs for annee, valeurs in temoin[partie].items()}
    return temoin


@pytest.fixture(scope="module")
def prelevements():
    return charger_prelevements_historiques(RACINE / "data")


def test_le_temoin_de_la_drees_dit_sa_source_et_ses_annees(drees):
    """Les montants de 2008 à 2022, la nette sous la brute ; les têtes de 2012 à
    2024, droit direct et droit dérivé, dont les taux font l'ensemble."""
    for champ in ("editeur", "montants", "url_montants", "csg", "url_csg", "lu_le"):
        assert drees["source"][champ], champ
    assert sorted(drees["montants"]) == list(range(2008, 2023))
    for valeurs in drees["montants"].values():
        assert 0.0 < valeurs["nette_directe"] < valeurs["brute_directe"] < valeurs["brute_totale"]
        assert valeurs["nette_directe"] < valeurs["nette_totale"] < valeurs["brute_totale"]
    assert sorted(drees["csg"]) == list(range(2012, 2025))
    for annee, droits in drees["csg"].items():
        for droit in ("direct", "derive"):
            r = droits[droit]
            somme = r["exonere"] + r["reduit"] + r["median"] + r["plein"] + r["inconnu"]
            assert somme == pytest.approx(r["ensemble"], abs=1.0), (annee, droit)
            assert (r["median"] > 0.0) == (annee >= 2019), (annee, droit)
    # Ancetre 2024 : 22,1 % d'exonérés, 13,4 % au taux réduit, 21,6 % au médian.
    direct = drees["csg"][2024]["direct"]
    parts = [round(direct[t] / direct["ensemble"], 3) for t in ("exonere", "reduit", "median")]
    assert parts == [0.221, 0.134, 0.216]


def test_le_taux_effectif_tient_entre_les_tetes_et_le_taux_plein(drees, prelevements):
    """Chaque année où les deux sources se recouvrent, le taux sur la masse
    passe le taux par tête — les exonérés ont les plus petites pensions — et
    reste sous le taux plein, cotisation maladie des complémentaires comprise
    en entier ; en 2022, 6,8 % contre 9,1 % au taux plein."""
    effectifs = taux_effectifs(drees["montants"])
    communes = sorted(set(effectifs) & set(drees["csg"]))
    assert communes == list(range(2012, 2023))
    for annee in communes:
        jour = dt.date(annee, 12, 31)
        bas = borne_par_les_tetes(drees["csg"][annee]["direct"], prelevements, jour)
        haut = taux_du_bareme(prelevements, jour, "plein") + 0.01
        assert bas < effectifs[annee] < haut, (annee, bas, effectifs[annee], haut)
    assert effectifs[2022] == pytest.approx(0.068, abs=5e-4)
    assert taux_du_bareme(prelevements, dt.date(2022, 12, 31), "plein") == pytest.approx(0.091)


def test_le_taux_effectif_suit_le_bareme(drees):
    """La hausse de la CSG de 1,7 point au 1er janvier 2018 relève le taux
    effectif de plus d'un point ; le taux médian, au 1er janvier 2019, en
    reprend une partie, et il ne revient pas à celui de 2017."""
    effectifs = taux_effectifs(drees["montants"])
    assert effectifs[2018] > effectifs[2017] + 0.01
    assert effectifs[2017] < effectifs[2019] < effectifs[2018]
    assert effectifs[2022] > effectifs[2017]


def test_l_awg_reprend_une_part_constante_et_plus_large():
    """L'Ageing Report reprend 11,1 % de la dépense brute, chaque année de 2022
    à 2070 ; la DREES ôte 6,8 % de prélèvements sociaux. L'écart, un peu plus
    de quatre points, est l'impôt sur le revenu des pensions, que la pension
    nette de la DREES ne retire pas : environ 0,6 point de PIB en 2022."""
    awg = json.loads(AWG.read_text(encoding="utf-8"))
    series = {cle: {int(annee): valeur for annee, valeur in serie.items()}
              for cle, serie in awg["series"].items()}
    parts = part_reprise_par_l_awg(series)
    assert sorted(parts) == list(range(2022, 2071))
    assert max(parts.values()) - min(parts.values()) < 1e-4
    assert parts[2022] == pytest.approx(0.111, abs=5e-4)
    drees = json.loads(TEMOIN.read_text(encoding="utf-8"))
    effectif = taux_effectifs({int(a): v for a, v in drees["montants"].items()})[2022]
    impot = (parts[2022] - effectif) * series["depense_brute"][2022]
    assert 0.035 < parts[2022] - effectif < 0.05
    assert impot == pytest.approx(0.6, abs=0.1)


def test_la_depense_nette_tient_le_dernier_taux_observe(drees):
    """Après 2022, le taux de 2022 ; avant 2008, celui de 2008 ; la dépense
    nette en est la brute, diminuée de ce taux."""
    effectifs = taux_effectifs(drees["montants"])
    taux = taux_projetes(effectifs, range(2000, 2071))
    assert taux[2070] == taux[2023] == effectifs[2022]
    assert taux[2000] == effectifs[2008]
    assert taux[2015] == effectifs[2015]
    nette = depense_nette({2022: 14.0, 2070: 13.0}, taux)
    assert nette[2070] == pytest.approx(13.0 * (1.0 - effectifs[2022]))
    with pytest.raises(ValueError):
        taux_projetes({}, [2022])


# -- le taux dans le modèle : la source, le fichier certifié -------------------


def test_le_recuperateur_depose_les_montants_que_la_certification_relit(
        tmp_path, monkeypatch):
    """Le récupérateur écrit le témoin, et dépose dans ``data/brut/``, que git
    ignore, les montants du tableau 2.1-a tels qu'il les lit : la source que
    ``scripts/verifier_donnees.py`` confronte à ``pensions_brutes_nettes.csv``.
    Il lit des classeurs déjà téléchargés, le portail de la DREES coupant
    souvent ses connexions."""
    grilles = {recuperateur.FEUILLE_MONTANTS: _grille(MONTANTS),
               recuperateur.FEUILLE_CSG: _grille(CSG)}
    monkeypatch.setattr(recuperateur, "feuilles",
                        lambda contenu, noms: {nom: grilles[nom] for nom in noms})
    monkeypatch.setattr(recuperateur, "SORTIE", tmp_path / "temoin.json")
    depot = tmp_path / "brut" / "drees_pension_nette.json"
    monkeypatch.setattr(recuperateur, "BRUT", depot)
    for nom in ("montants.xlsx", "eacr.xlsx"):
        (tmp_path / nom).write_bytes(b"")
    assert recuperateur.main(["--montants", str(tmp_path / "montants.xlsx"),
                              "--eacr", str(tmp_path / "eacr.xlsx")]) == 0
    brut = json.loads(depot.read_text(encoding="utf-8"))
    assert brut["montants"] == {
        "2021": {"brute_directe": 1482.0, "nette_directe": 1380.0,
                 "brute_totale": 1629.0, "nette_totale": 1519.0},
        "2022": {"brute_directe": 1565.0, "nette_directe": 1457.0,
                 "brute_totale": 1719.0, "nette_totale": 1602.0},
    }
    assert brut["source"]["url"] == recuperateur.URL_MONTANTS
    assert brut["source"]["lu_le"] == dt.date.today().isoformat()
    temoin = json.loads((tmp_path / "temoin.json").read_text(encoding="utf-8"))
    assert temoin["montants"] == brut["montants"]
    assert temoin["csg"]["2022"]["direct"]["plein"] == 6000.0


def _certifie() -> dict[tuple[int, str], tuple[float, str]]:
    with FICHIER.open(encoding="utf-8") as flux:
        lignes = [ligne for ligne in flux if not ligne.startswith("#")]
    return {(int(l["annee"]), l["indicateur"]): (float(l["valeur"]), l["fiabilite"])
            for l in csv.DictReader(lignes)}


def test_le_fichier_certifie_redonne_le_tableau_de_la_drees(drees):
    """Les quatre montants de chaque année de 2008 à 2022, ceux que le
    récupérateur a lus dans le tableau 2.1-a le 14 octobre 2026 et que le
    témoin garde, certifiés le 24 sur le classeur relu : en 2022, 1 719 €
    bruts et 1 602 € nets par mois, toutes pensions comprises, 1 565 € et
    1 457 € de droit direct ; en 2008, 1 343 € et 1 260 €."""
    lu = _certifie()
    assert {fiabilite for _valeur, fiabilite in lu.values()} == {"certifiee"}
    attendu = {(annee, indicateur): valeur
               for annee, valeurs in drees["montants"].items()
               for indicateur, valeur in valeurs.items()}
    assert {cle: valeur for cle, (valeur, _fiabilite) in lu.items()} == attendu
    assert lu[(2022, "brute_totale")][0] == 1719.0
    assert lu[(2022, "nette_totale")][0] == 1602.0
    assert lu[(2022, "brute_directe")][0] == 1565.0
    assert lu[(2022, "nette_directe")][0] == 1457.0
    assert lu[(2008, "brute_totale")][0] == 1343.0
    assert lu[(2008, "nette_totale")][0] == 1260.0
