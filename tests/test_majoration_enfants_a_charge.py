"""La majoration de l'Agirc-Arrco pour enfants à charge (action 138, étape 17).

Le participant qui a un enfant à charge à la date d'effet de sa retraite
complémentaire voit son allocation majorée de 5 % par enfant à charge, tant
qu'il le reste, au lieu de la majoration pour enfants nés ou élevés quand elle
est plus forte : à l'Arrco depuis 1999, à l'Agirc depuis 2012, à l'Agirc-Arrco
depuis 2019, sur les droits sans le coefficient d'anticipation depuis 2012
(fiche ``majoration_enfants_a_charge_agirc_arrco``).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.droit import completer
from retraite_notionnelle.droit.commun import (AvantageApplique, fusionner_les_charges,
                                               parts_de_la_majoration)
from retraite_notionnelle.revalorisation import faire_vivre
from retraite_notionnelle.saisie import Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]

#: Les carrières d'un cadre du privé, que la saisie décrit.
CADRE = {"statut": "salarie_prive_cadre", "debut": "22"}


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


def _simuler(contexte, **requete):
    saisie = Saisie.depuis_requete({**CADRE, **requete})
    return saisie, contexte.simuler(saisie)


def _majoration(comparaison) -> AvantageApplique | None:
    return next((a for a in comparaison.actuel.avantages_appliques
                 if a.code == "majoration_enfants"), None)


def _pensions(comparaison) -> dict[str, float]:
    return {p.regime: p.montant for p in comparaison.actuel.pensions_par_regime}


# -- la fiche --------------------------------------------------------------------

def test_la_fiche_date_l_arrco_l_agirc_et_le_regime_unifie(contexte):
    """Rien avant 1999 ; l'Arrco seule, sur l'allocation, jusqu'en 2011 ;
    l'Arrco et l'Agirc chacune sur ses droits bruts de 2012 à 2018 ; une seule
    allocation depuis 2019."""
    fiches = Simulateur().scenario_actuel.fiches_datees
    nom = completer.FICHE_DES_ENFANTS_A_CHARGE
    assert not fiches.regle(nom, "1998-12-01")["existe"]
    regles = [fiches.regle(nom, date) for date in ("1999-01-01", "2012-01-01", "2019-01-01")]
    assert [r["assiette"] for r in regles] == ["allocation", "droits_bruts", "droits_bruts"]
    assert [len(r["allocations"]) for r in regles] == [1, 2, 1]
    assert {r["taux_par_enfant"] for r in regles} == {0.05}
    assert {r["age"] for r in regles} == {18}
    assert "agirc" not in regles[0]["allocations"][0]["regimes"]


# -- la date d'effet --------------------------------------------------------------

def test_l_arrco_sert_5_pour_cent_par_enfant_a_charge_depuis_1999(contexte):
    """Parti en avril 2005 avec deux enfants de moins de dix-huit ans : l'Arrco
    majorée de 10 %, l'Agirc rien ; puis de 5 % au premier anniversaire, et
    plus rien au second."""
    _, comparaison = _simuler(contexte, naissance="1943-03-15", liquidation="2005-04",
                              enfants="2", naissances="1990,1995-05")
    majoration = _majoration(comparaison)
    arrco = _pensions(comparaison)["arrco"]
    assert dict(majoration.par_regime) == pytest.approx({"arrco": 0.10 * arrco})
    assert [depuis for depuis, _ in majoration.a_charge] == [
        "2005-04-01", "2008-01-01", "2013-05-01"]
    assert dict(majoration.a_charge[1][1]) == pytest.approx({"arrco": 0.05 * arrco})
    assert majoration.a_charge[-1][1] == ()
    assert "2 enfants à charge" in majoration.detail
    assert "jusqu'en mai 2013" in majoration.detail


def test_l_agirc_la_sert_depuis_2012_chacune_sur_son_allocation(contexte):
    _, comparaison = _simuler(contexte, naissance="1950-03-15", liquidation="2015-04",
                              enfants="2", naissances="1995,2002-05")
    pensions = _pensions(comparaison)
    assert dict(_majoration(comparaison).par_regime) == pytest.approx(
        {"arrco": 0.05 * pensions["arrco"], "agirc": 0.05 * pensions["agirc"]})


def test_la_majoration_se_calcule_sans_le_coefficient_d_anticipation(contexte):
    """Parti en 2039 avec un enfant de quatorze ans et une décote : 5 % des
    droits que le coefficient d'anticipation n'a pas réduits, le même pour
    tous les régimes de la complémentaire, et rien au régime général."""
    _, comparaison = _simuler(contexte, naissance="1975-03-15", liquidation="2039-04",
                              enfants="1", naissances="2025-06")
    parts = dict(_majoration(comparaison).par_regime)
    pensions = _pensions(comparaison)
    assert "regime_general" not in parts
    assert set(parts) == {"agirc_arrco", "arrco", "agirc"}
    rapports = [part / (0.05 * pensions[code]) for code, part in parts.items()]
    assert min(rapports) > 1.01
    assert max(rapports) == pytest.approx(min(rapports))


def test_la_plus_forte_des_deux_majorations_est_servie(contexte):
    """Trois enfants, dont un de moins de dix-huit ans : les 10 % des enfants
    nés ou élevés passent les 5 % du seul enfant à charge, et sont seuls
    servis ; avec trois enfants à charge, les 15 % l'emportent."""
    _, un = _simuler(contexte, naissance="1975-03-15", liquidation="2039-04",
                     enfants="3", naissances="2005,2010,2025-06")
    assert _majoration(un).a_charge == ()
    _, trois = _simuler(contexte, naissance="1975-03-15", liquidation="2039-04",
                        enfants="3", naissances="2022,2024,2025-06")
    majoration = _majoration(trois)
    assert majoration.a_charge
    assert majoration.montant > _majoration(un).montant
    assert "3 enfants à charge" in majoration.detail


def test_seul_compte_l_enfant_a_charge_a_la_date_d_effet():
    """L'enfant qui a dix-huit ans au départ n'est plus à charge, celui qui
    naît après ne l'est pas encore (article 93) ; chacun cesse de l'être à son
    anniversaire."""
    class Carriere:
        naissances_des_enfants = (("aine", "1985-01-01"), ("cadet", "1990-06-01"),
                                  ("benjamin", "1992-11-01"), ("posthume", "2006-01-01"))

    assert completer.fins_de_charge(Carriere, {"age": 18}, "2005-04-01") == [
        "2008-06-01", "2010-11-01"]


def test_avant_1999_rien(contexte):
    _, comparaison = _simuler(contexte, naissance="1935-03-15", liquidation="1997-04",
                              enfants="1", naissances="1985")
    assert _majoration(comparaison) is None


# -- les échéances ----------------------------------------------------------------

def test_la_majoration_cesse_avec_la_charge(contexte):
    """La revalorisation retire, à chaque échéance, la part des enfants qui ne
    sont plus à charge : toute en 2007, la moitié de 2008 à 2012, rien
    ensuite."""
    saisie, comparaison = _simuler(contexte, naissance="1943-03-15", liquidation="2005-04",
                                   enfants="2", naissances="1990,1995-05")
    simulateur = contexte.simulateur(saisie.parametres(contexte.base))
    servies = {}
    for annee in (2007, 2008, 2012, 2013, 2020):
        vivante = faire_vivre(simulateur, comparaison.carriere, comparaison.actuel, annee)
        arrco = next(r.coefficient for r in vivante.regimes if r.regime == "arrco")
        servies[annee] = vivante.majoration_enfants * vivante.coefficient_majoration / arrco
    majoration = _majoration(comparaison).montant
    assert servies[2007] == pytest.approx(majoration)
    assert servies[2008] == pytest.approx(majoration / 2)
    assert servies[2012] == pytest.approx(majoration / 2)
    assert servies[2013] == pytest.approx(0.0, abs=1e-9)
    assert servies[2020] == pytest.approx(0.0, abs=1e-9)


def test_les_parts_a_une_date_et_la_reunion_de_deux_departs():
    etapes = (("2010-01-01", (("arrco", 10.0),)), ("2012-06-01", (("arrco", 4.0),)),
              ("2015-01-01", ()))
    avantage = AvantageApplique(code="majoration_enfants", libelle="", montant=30.0,
                                par_regime=(("regime_general", 20.0), ("arrco", 10.0)),
                                a_charge=etapes)
    assert parts_de_la_majoration([avantage]) == [("regime_general", 20.0), ("arrco", 10.0)]
    assert parts_de_la_majoration([avantage], "2011-12-31") == [
        ("regime_general", 20.0), ("arrco", 10.0)]
    total = {}
    for code, part in parts_de_la_majoration([avantage], "2013-12-31"):
        total[code] = total.get(code, 0.0) + part
    assert total == {"regime_general": 20.0, "arrco": 4.0}
    autres = (("2011-01-01", (("agirc", 2.0),)), ("2013-01-01", ()))
    assert fusionner_les_charges(etapes, autres) == (
        ("2010-01-01", (("arrco", 10.0), ("agirc", 2.0))),
        ("2011-01-01", (("arrco", 10.0), ("agirc", 2.0))),
        ("2012-06-01", (("arrco", 4.0), ("agirc", 2.0))),
        ("2013-01-01", (("arrco", 4.0),)),
        ("2015-01-01", ()),
    )
    assert fusionner_les_charges((), autres) == autres


# -- les deux moteurs ---------------------------------------------------------------

CAS = [
    {"naissance": "1943-03-15", "liquidation": "2005-04", "enfants": "2",
     "naissances": "1990,1995-05"},
    {"naissance": "1950-03-15", "liquidation": "2015-04", "enfants": "2",
     "naissances": "1995,2002-05"},
    {"naissance": "1975-03-15", "liquidation": "2039-04", "enfants": "1",
     "naissances": "2025-06"},
    {"naissance": "1960-03-15", "liquidation": "2022-04", "enfants": "2",
     "naissances": "2008,2012-05", "statut": "salarie_prive_non_cadre"},
]


def test_les_deux_moteurs_servent_la_meme_majoration(contexte):
    """Le résultat entier, aujourd'hui compris — où la majoration a perdu
    l'enfant qui n'est plus à charge —, est le même en Python et en
    JavaScript."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini

    attendus = []
    for cas in CAS:
        saisie = Saisie.depuis_requete({**CADRE, **cas})
        attendus.append({"requete": {**CADRE, **cas},
                         "resultat": _fini(contexte.simuler(saisie).dictionnaire())})
    texte = json.dumps(attendus, ensure_ascii=False)
    assert "enfant à charge" in texte and "enfants à charge" in texte
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(texte)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]
