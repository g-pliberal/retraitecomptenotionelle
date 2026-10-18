"""Le niveau de pension des cas types, confronté à Ancetre, régime principal par régime principal.

Le modèle Ancetre de la DREES publie la pension brute moyenne de droit direct
par régime principal, fin 2024 (rapport annuel du COR de juin 2026, tableau
3.2) ; ``retraite_notionnelle.controle_ancetre`` lui confronte ce que la grille
de la page Coût sert la même année (action 138, étape 3). Ce module tient
trois choses :

* LE TÉMOIN (``tests/temoins/cor_pension_regime_principal_2026.json``,
  ``scripts/fetch/cor_pension_regime_principal.py``), et ce qu'il tient de
  lui-même ;
* LA MESURE, sur une grille d'essai : le poids des cohortes, le rangement par
  régime principal, une caisse neuve qui ne sort pas du contrôle sans bruit ;
* LA CONFRONTATION, sur la grille du dépôt : l'ensemble des carrières
  complètes à moins d'un dixième, et chaque écart de régime dans le sens que
  la note du 16 octobre 2026 décrit.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from retraite_notionnelle.castypes import CAS_TYPES
from retraite_notionnelle.controle_ancetre import (
    ENSEMBLE,
    REGIME_PRINCIPAL,
    confronter,
    controle,
    par_regime_principal,
    pensions_mensuelles,
)

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "cor_pension_regime_principal_2026.json"
LECTEUR = RACINE / "scripts" / "fetch" / "cor_pension_regime_principal.py"


@pytest.fixture(scope="module")
def ancetre() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


def _lecteur():
    spec = importlib.util.spec_from_file_location("cor_pension_regime_principal", LECTEUR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_le_temoin_d_ancetre_dit_sa_source_et_redonne_le_rapport(ancetre):
    """La source et le champ de 2024 ; les montants que le registre cite ;
    chaque ligne du tableau, ses six colonnes ; et l'ensemble au-dessus de
    tous ses régimes de salariés du privé, au-dessous de la fonction publique :
    une ligne déplacée d'une colonne se verrait."""
    assert "Ancetre" in ancetre["source"]["producteur"]
    assert ancetre["annee"] == 2024 and "2024" in ancetre["champ"]
    assert _lecteur().controler(ancetre) == []
    for cle, _ in _lecteur().LIGNES:
        ligne = ancetre["pensions"][cle]
        assert set(ligne) == {"tous", "carriere_complete"}
        for champ in ligne.values():
            assert set(champ) == {"ensemble", "femmes", "hommes"}
            assert champ["femmes"] < champ["hommes"] or cle == "cnracl"
            assert champ["femmes"] <= champ["ensemble"] <= champ["hommes"]
    pensions = ancetre["pensions"]
    assert (pensions["regime_general"]["tous"]["ensemble"]
            < pensions["ensemble"]["tous"]["ensemble"]
            < pensions["fpe_civils"]["tous"]["ensemble"])


def test_chaque_caisse_de_la_grille_a_son_regime_principal(ancetre):
    """Toute caisse d'un cas type a sa ligne au tableau : un cas type neuf
    entre au contrôle, ou le fait lever."""
    for cas in CAS_TYPES:
        assert cas.caisses, cas.code
        assert REGIME_PRINCIPAL[cas.caisses[0]] in ancetre["pensions"], cas.code
    with pytest.raises(KeyError, match="régime principal"):
        par_regime_principal({"x": 1000.0}, {"x": 1.0}, {"x": "inconnue"})


def test_la_pension_d_un_cas_type_pese_ses_cohortes_parties():
    """Deux cohortes parties, l'une deux fois plus nombreuse : la moyenne les
    pèse ; une cohorte qui n'est pas encore partie n'y est pas ; la complétude
    rogne la pension ; l'unité est le mois, en euros de l'année."""
    from retraite_notionnelle.cout import _DEMI_TRANCHE

    effectifs = {(70, 2024): 2.0, (69, 2024): 1.0}
    population = SimpleNamespace(effectif=lambda age, annee: effectifs.get((age, annee), 0.0))
    completudes = [1.0] * (2 * _DEMI_TRANCHE + 1)
    completudes[_DEMI_TRANCHE + 1] = 0.5
    pensionne = SimpleNamespace(
        code="essai", generation=1954, annee_liquidation=2018,
        liquidation=lambda decalage: 2018 + decalage,
        pensions={"actuel": 24_000.0}, parts_regimes={},
        completude=lambda decalage: completudes[decalage + _DEMI_TRANCHE])
    # Né en 1954, parti en 2018 : 70 ans en 2024 ; la cohorte suivante, née en
    # 1955, part en 2019 à demi-carrière ; celles d'après n'ont pas d'effectif.
    pensions = pensions_mensuelles([pensionne], population, None, 1.5, annee=2024)
    assert pensions["essai"] == pytest.approx((2 * 2000.0 + 1 * 1000.0) / 3 * 1.5)
    # Une cohorte part l'année que le droit de sa génération lui donne
    # (``cout.Pensionne.liquidation``) : née en 1955, partie en 2025, elle n'y
    # est pas.
    tardive = SimpleNamespace(**{**vars(pensionne), "liquidation": lambda decalage: {
        0: 2018, 1: 2025}.get(decalage, 2018 + decalage)})
    pensions = pensions_mensuelles([tardive], population, None, 1.5, annee=2024)
    assert pensions["essai"] == pytest.approx(2000.0 * 1.5)


def test_un_regime_principal_moyenne_ses_cas_types_a_leur_poids():
    pensions = {"a": 1000.0, "b": 2000.0, "c": 3000.0, "d": 9999.0}
    poids = {"a": 3.0, "b": 1.0, "c": 1.0, "d": 0.0}
    caisses = {"a": "cnav", "b": "rci_complementaire", "c": "cnracl", "d": "cnavpl"}
    resultat = par_regime_principal(pensions, poids, caisses)
    assert resultat == pytest.approx({"regime_general": 1250.0, "cnracl": 3000.0,
                                      ENSEMBLE: 1600.0})


@pytest.fixture(scope="module")
def confrontation(ancetre):
    _, regimes = controle()
    return {ecart.ligne: ecart for ecart in confronter(regimes, ancetre)}


def test_la_grille_retrouve_la_pension_des_carrieres_completes(confrontation):
    """L'ensemble de la grille, au poids de la page, à moins d'un dixième de
    la pension des carrières complètes d'Ancetre (−3 % le 16 octobre 2026), et
    au-dessus de celle de tous les retraités, dont la grille n'a pas les
    carrières courtes."""
    ensemble = confrontation[ENSEMBLE]
    assert abs(ensemble.rapport - 1.0) < 0.10
    assert ensemble.rapport_tous > 1.05


def test_chaque_regime_principal_s_ecarte_dans_le_sens_decrit(confrontation):
    """Le régime général, quatre carrières du privé et l'artisan, à moins d'un
    dixième de ses carrières complètes ; chaque régime qu'un seul cas type
    représente au-dessous des siennes, de 10 à 45 % : le cas type est une
    carrière modeste de son régime (la catégorie B, l'aide-soignant, le
    militaire du rang), que la page, calée sur la dépense de chaque groupe du
    COR, compense par des têtes. Un écart qui change de sens dit qu'une règle
    ou une donnée a bougé."""
    assert set(confrontation) == set(REGIME_PRINCIPAL.values()) | {ENSEMBLE}
    assert abs(confrontation["regime_general"].rapport - 1.0) < 0.10
    for ligne, ecart in confrontation.items():
        if ligne in (ENSEMBLE, "regime_general"):
            continue
        assert 0.55 < ecart.rapport < 0.90, (ligne, ecart)
