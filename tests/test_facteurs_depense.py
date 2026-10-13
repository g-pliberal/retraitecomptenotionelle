"""La dépense en ses quatre facteurs, confrontée à l'Ageing Report de 2024.

L'Ageing Report décompose la dépense de pensions de la France en dépendance,
couverture, prestation et marché du travail ; le dépôt fait de même de sa
trajectoire (``retraite_notionnelle.facteurs_depense`` ; action 138, étape 3).
Ce module tient trois choses :

* LA FORMULE. Ni la fiche France ni le volume 1 n'écrivent comment un effet se
  chiffre. Appliquée aux séries de l'annexe statistique
  (``tests/temoins/ageing_report_france.json``,
  ``scripts/fetch/ageing_report.py``), celle du module redonne les effets
  publiés au dix-millième de point, l'arrondi de l'annexe.
* L'IDENTITÉ. Les quatre facteurs refont la part de PIB du modèle, chaque année
  et chaque système, à l'arrondi près.
* LA CONFRONTATION, qui se lit dans la note du 13 octobre 2026
  (``docs/feuille_de_route/138/``). Le modèle fait monter la dépense de 2022 à
  2070, l'AWG la fait baisser. Sous une productivité proche de la sienne, la
  prestation du modèle recule autant que la sienne ; le reste tient à la
  démographie de l'INSEE de 2026, plus vieille que celle d'Eurostat de 2023, à
  l'emploi du COR, et à la couverture, qui recule moins de 2022 à 2030, pour
  des causes à départager.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import pytest

from retraite_notionnelle.facteurs_depense import (
    FACTEURS,
    GRILLE_AWG,
    AnneeDepense,
    annees_du_modele,
    decomposer,
    effet,
)

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "ageing_report_france.json"


@pytest.fixture(scope="module")
def awg() -> dict:
    """Le témoin, ses années en entiers."""
    temoin = json.loads(TEMOIN.read_text(encoding="utf-8"))
    for partie in ("series", "decomposition"):
        temoin[partie] = {cle: {int(annee): valeur for annee, valeur in serie.items()}
                          for cle, serie in temoin[partie].items()}
    return temoin


def test_le_temoin_de_l_ageing_report_dit_sa_source_et_tient_ses_identites(awg):
    """La source et ses conventions écrites, toutes les années de 2022 à 2070,
    et ce que l'annexe tient d'elle-même : la variation publiée est celle de la
    dépense, et les effets et le résidu la font."""
    for champ in ("editeur", "reference", "url", "lu_le"):
        assert awg["source"].get(champ), champ
    for champ in ("decomposition", "effets", "perimetre", "hypotheses"):
        assert awg["conventions"].get(champ), champ
    for cle, serie in awg["series"].items():
        assert sorted(serie) == list(range(2022, 2071)), cle
    publiee = awg["decomposition"]
    for annee in GRILLE_AWG[1:]:
        depense = awg["series"]["depense_brute"]
        assert publiee["depense"][annee] == pytest.approx(depense[annee] - depense[2022],
                                                          abs=2e-4)
        somme = sum(publiee[cle][annee] for cle in
                    ("dependance", "couverture", "prestation", "marche_du_travail", "residu"))
        assert somme == pytest.approx(publiee["depense"][annee], abs=2e-4)


def test_la_formule_de_l_awg_refait_ses_effets_publies(awg):
    """Pas à pas, la dépense au début du pas fois la variation relative du
    facteur : les effets de la dépendance, de la couverture, de la couverture
    des 65 ans et plus et du taux d'emploi, refaits des séries que l'annexe
    publie, sont les siens au dix-millième de point. Le logarithme de la
    variation, sur les mêmes pas, s'en écarterait de 0,17 point pour la
    dépendance, et un seul pas de 2022 à 2070 de 1,4 point.

    Les deux autres effets ne se refont pas : la prestation et le marché du
    travail se rapportent aux heures travaillées et au PIB en niveau, que
    l'annexe ne publie pas."""
    series = awg["series"]
    depense = series["depense_brute"]
    plus_de_65 = {annee: series["rapport_de_dependance"][annee] / 100
                  * series["population_20_64"][annee] for annee in depense}
    facteurs = {
        "dependance": series["rapport_de_dependance"],
        "couverture": {annee: series["pensionnes"][annee] / plus_de_65[annee]
                       for annee in depense},
        "couverture_vieillesse": {annee: series["pensionnes_65_plus"][annee]
                                  / plus_de_65[annee] for annee in depense},
        "taux_emploi": {annee: series["population_20_64"][annee]
                        / series["emploi_20_64"][annee] for annee in depense},
    }
    for nom, facteur in facteurs.items():
        refait = effet(depense, facteur)
        for annee in GRILLE_AWG[1:]:
            assert refait[annee] == pytest.approx(awg["decomposition"][nom][annee],
                                                  abs=1e-4), (nom, annee)
    # La dépendance, sous deux conventions qu'on aurait pu croire siennes.
    dependance, publie = facteurs["dependance"], awg["decomposition"]["dependance"][2070]
    logarithme = sum(depense[debut] * math.log(dependance[fin] / dependance[debut])
                     for debut, fin in zip(GRILLE_AWG, GRILLE_AWG[1:]))
    un_seul_pas = depense[2022] * (dependance[2070] / dependance[2022] - 1)
    assert abs(logarithme - publie) > 0.1
    assert abs(un_seul_pas - publie) > 1.0


def _annee(annee: int, **grandeurs: float) -> AnneeDepense:
    valeurs = dict(depense=10.0, pib=100.0, retraites=10.0, population_65=10.0,
                   population_20_64=40.0, emploi=30.0)
    valeurs.update(grandeurs)
    return AnneeDepense(annee=annee, **valeurs)


def test_les_quatre_facteurs_font_la_part_de_pib_et_un_seul_qui_bouge_fait_tout():
    """Le produit des facteurs est la part de PIB, en pour cent. Que les 65 ans
    et plus doublent, retraités et dépense avec eux, et tout l'effet va à la
    dépendance : la part de PIB au début du pas, fois un — et le résidu est
    nul, un seul facteur ayant bougé."""
    debut = _annee(2022)
    fin = _annee(2025, population_65=20.0, retraites=20.0, depense=20.0)
    for annee in (debut, fin):
        produit = (annee.dependance * annee.couverture * annee.prestation
                   * annee.marche_du_travail * 100)
        assert produit == pytest.approx(annee.part_pib, rel=1e-12)
    decomposition = decomposer({2022: debut, 2025: fin}, grille=(2022, 2025))
    assert decomposition.variation[2025] == pytest.approx(10.0)
    assert decomposition.effets["dependance"][2025] == pytest.approx(10.0)
    for nom in ("couverture", "prestation", "marche_du_travail"):
        assert decomposition.effets[nom][2025] == pytest.approx(0.0, abs=1e-12)
    assert decomposition.residu[2025] == pytest.approx(0.0, abs=1e-12)
    # Deux facteurs qui se croisent laissent un résidu, négatif.
    croises = decomposer({2022: debut, 2025: _annee(2025, population_65=20.0,
                                                    retraites=15.0, depense=15.0)},
                         grille=(2022, 2025))
    assert croises.residu[2025] < 0.0
    assert croises.entre(2022, 2025)["couverture"] == pytest.approx(
        croises.effets["couverture"][2025])


@lru_cache(maxsize=None)
def _decomposition(scenario_projection: str, scenario: str):
    """La décomposition du modèle sous ce scénario de projection, pour ce
    système, et ses années — sur le coût de la page, gardé en mémoire."""
    from retraite_notionnelle import Parametres, memoire
    from retraite_notionnelle.donnees.population import Population
    from retraite_notionnelle.simulateur import Simulateur

    parametres = Parametres(scenario_projection=scenario_projection)
    cout = memoire.cout(parametres)
    annees = annees_du_modele(cout.avenir, Population(parametres.racine_donnees),
                              Simulateur(parametres).macro, scenario)
    return annees, decomposer(annees)


def test_les_quatre_facteurs_refont_la_part_de_pib_du_modele():
    """Chaque année, et pour chaque système, le produit des quatre facteurs est
    la part de PIB de la trajectoire propre du modèle ; le premier système
    garde les retraités du droit en vigueur, et la même démographie que les
    autres."""
    from retraite_notionnelle.cout import SCENARIOS

    for scenario, _ in SCENARIOS:
        annees, _decompose = _decomposition("cor_reference", scenario)
        assert set(GRILLE_AWG) <= set(annees), scenario
        for annee in annees.values():
            produit = (annee.dependance * annee.couverture * annee.prestation
                       * annee.marche_du_travail * 100)
            assert produit == pytest.approx(annee.part_pib, rel=1e-12), (scenario, annee.annee)
    actuel, _ = _decomposition("cor_reference", "actuel")
    liberal, _ = _decomposition("cor_reference", "notionnel_liberal")
    for annee in GRILLE_AWG:
        assert liberal[annee].dependance == actuel[annee].dependance
        assert liberal[annee].couverture == actuel[annee].couverture


def test_la_trajectoire_du_modele_se_decompose_comme_celle_de_l_awg(awg):
    """De 2022 à 2070, chaque effet du système actuel a le signe de celui de
    l'AWG, et sa grandeur à moitié près : la dépendance pousse, la couverture,
    la prestation et le marché du travail retiennent, le résidu est négatif.
    La dépendance du modèle pousse plus fort : les 65 ans et plus des
    projections de l'INSEE de 2026 croissent plus vite, rapportés aux 20-64
    ans, que ceux d'Eurostat de 2023 — un effet des données, que le modèle ne
    choisit pas."""
    _annees, decomposition = _decomposition("cor_reference", "actuel")
    publiee = awg["decomposition"]
    for nom in (*FACTEURS, "residu"):
        modele = (decomposition.residu if nom == "residu" else decomposition.effets[nom])[2070]
        reference = publiee[nom][2070]
        assert modele * reference > 0.0, nom
        assert 0.5 < modele / reference < 1.5, (nom, round(modele, 2), reference)
    assert decomposition.effets["dependance"][2070] > publiee["dependance"][2070]
    insee = _annees[2070].dependance / _annees[2022].dependance
    eurostat = (awg["series"]["rapport_de_dependance"][2070]
                / awg["series"]["rapport_de_dependance"][2022])
    assert insee > eurostat + 0.1


def test_a_productivite_proche_la_prestation_recule_comme_chez_l_awg(awg):
    """L'AWG projette une productivité horaire de 1,03 % par an en moyenne, le
    COR de 0,7 % dans sa référence et de 1,0 % dans sa variante haute. Sous
    celle-ci, l'effet de la prestation du système actuel est celui de l'AWG à
    un demi-point près : la mécanique du modèle — pensions sur les prix,
    pilotage de l'Agirc-Arrco que le COR projette — retient la dépense comme
    Destinie. Sous la référence, il retient moins : la productivité seule
    déplace l'effet de plus de quatre dixièmes de point."""
    publiee = awg["decomposition"]["prestation"][2070]
    _annees, haute = _decomposition("cor_productivite_haute", "actuel")
    _annees, reference = _decomposition("cor_reference", "actuel")
    assert abs(haute.effets["prestation"][2070] - publiee) < 0.5
    assert reference.effets["prestation"][2070] > haute.effets["prestation"][2070] + 0.4
