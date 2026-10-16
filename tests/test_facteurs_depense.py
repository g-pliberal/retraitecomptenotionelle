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
  l'emploi du COR, et à la couverture, qui recule moins de 2022 à 2030 : le
  périmètre surtout — l'AWG compte deux fois plus de pensionnés de moins de 65
  ans —, puis les 65 ans et plus et la suspension de 2026 (note du 16 octobre
  2026, « la couverture de 2022-2030 »).
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
    au_perimetre,
    decomposer,
    effet,
    partager_couverture,
    retraites_par_age,
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


def _couverture_de_l_awg(awg) -> tuple[dict, dict, dict, dict]:
    """La dépense, les pensionnés, ceux de 65 ans et plus et les 65 ans et
    plus de l'annexe, aux années de la grille."""
    series = awg["series"]
    population_65 = {annee: series["rapport_de_dependance"][annee] / 100
                     * series["population_20_64"][annee] for annee in GRILLE_AWG}
    return ({annee: series["depense_brute"][annee] for annee in GRILLE_AWG},
            {annee: series["pensionnes"][annee] for annee in GRILLE_AWG},
            {annee: series["pensionnes_65_plus"][annee] for annee in GRILLE_AWG},
            population_65)


def test_la_couverture_se_partage_exactement_entre_les_ages(awg):
    """Sur les séries de l'annexe, les deux parts de la couverture refont son
    effet à chaque année de la grille, au bit d'arrondi près, et celui-ci est
    l'effet publié : de 2022 à 2030, les moins de 65 ans en font les cinq
    sixièmes. Une trajectoire portée à son propre périmètre reste elle-même ;
    portée avec ses plus jeunes tout stables, ils n'ont plus d'effet."""
    part_pib, pensionnes, agees, population_65 = _couverture_de_l_awg(awg)
    parts = partager_couverture(part_pib, pensionnes, agees, population_65)
    couverture = effet(part_pib, {annee: pensionnes[annee] / population_65[annee]
                                  for annee in GRILLE_AWG})
    for annee in GRILLE_AWG[1:]:
        assert parts["vieillesse"][annee] + parts["precoce"][annee] == pytest.approx(
            couverture[annee], abs=1e-12)
        assert couverture[annee] == pytest.approx(awg["decomposition"]["couverture"][annee],
                                                  abs=1e-3)
    assert parts["precoce"][2030] / couverture[2030] > 0.8

    premiere = GRILLE_AWG[0]
    vieux = agees[premiere] / population_65[premiere]
    jeunes = pensionnes[premiere] / population_65[premiere] - vieux
    meme, memes_agees = au_perimetre(population_65, vieux, jeunes, pensionnes, agees,
                                     population_65)
    for annee in GRILLE_AWG:
        assert meme[annee] == pytest.approx(pensionnes[annee], rel=1e-12)
        assert memes_agees[annee] == pytest.approx(agees[annee], rel=1e-12)
    figes = partager_couverture(part_pib, *au_perimetre(
        population_65, vieux, jeunes, pensionnes, agees, population_65, stable=1.0),
        population_65)
    assert all(abs(valeur) < 1e-12 for valeur in figes["precoce"].values())


def test_les_retraites_par_age_refont_les_tetes_du_cout():
    """Le geste de ``retraites_par_age`` est celui de ``cout.py`` : tous âges,
    ses retraités sont les têtes de la trajectoire, chaque année de la
    grille ; ceux de 65 ans et plus sont moins nombreux, et presque toutes les
    personnes de cet âge — la limite n° 2 de ``cout.py`` : chaque cohorte est
    retraitée à l'âge de départ de son cas type."""
    from retraite_notionnelle import Parametres

    annees, _decomposition_ = _decomposition("cor_reference", "actuel")
    par_age = retraites_par_age(Parametres(scenario_projection="cor_reference"), GRILLE_AWG)
    for annee in GRILLE_AWG:
        toutes, agees = par_age[annee]
        assert toutes == pytest.approx(annees[annee].retraites, rel=1e-12), annee
        assert agees < toutes
        assert 0.97 < agees / annees[annee].population_65 < 1.01, annee


def test_la_couverture_de_2022_2030_tient_au_perimetre_de_l_awg(awg):
    """De 2022 à 2030, la couverture du modèle recule de 0,84 point de PIB et
    celle de l'AWG de 1,38 (note du 16 octobre 2026). Ses moins de 65 ans
    reculent autant, rapportés aux 65 ans et plus — 36 % contre 33 % —, mais
    l'AWG en compte deux fois plus, l'invalidité comprise : portée à son
    périmètre, la dynamique du modèle refait l'essentiel de son effet."""
    from retraite_notionnelle import Parametres

    annees, decomposition = _decomposition("cor_reference", "actuel")
    par_age = retraites_par_age(Parametres(scenario_projection="cor_reference"), GRILLE_AWG)
    retraites = {annee: par_age[annee][0] for annee in GRILLE_AWG}
    agees = {annee: par_age[annee][1] for annee in GRILLE_AWG}
    population_65 = {annee: annees[annee].population_65 for annee in GRILLE_AWG}
    part_pib, pensionnes, pensionnes_agees, population_65_awg = _couverture_de_l_awg(awg)

    def jeunes(tous, vieux, population, annee):
        return (tous[annee] - vieux[annee]) / population[annee]

    recul_modele = (jeunes(retraites, agees, population_65, 2030)
                    / jeunes(retraites, agees, population_65, 2022))
    recul_awg = (jeunes(pensionnes, pensionnes_agees, population_65_awg, 2030)
                 / jeunes(pensionnes, pensionnes_agees, population_65_awg, 2022))
    assert recul_modele < recul_awg
    assert (jeunes(pensionnes, pensionnes_agees, population_65_awg, 2022)
            > 1.5 * jeunes(retraites, agees, population_65, 2022))

    publiee = awg["decomposition"]["couverture"][2030]
    ecart = decomposition.effets["couverture"][2030] - publiee
    premiere = GRILLE_AWG[0]
    vieux = pensionnes_agees[premiere] / population_65_awg[premiere]
    plus_jeunes = pensionnes[premiere] / population_65_awg[premiere] - vieux
    portee = partager_couverture(part_pib, *au_perimetre(
        population_65_awg, vieux, plus_jeunes, retraites, agees, population_65),
        population_65_awg)
    assert ecart > 0.4
    assert abs(portee["vieillesse"][2030] + portee["precoce"][2030] - publiee) < ecart / 2

