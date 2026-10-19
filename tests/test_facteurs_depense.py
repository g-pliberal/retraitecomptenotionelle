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
  l'emploi du COR, et à la couverture, qui recule moins de 2022 à 2030. L'AWG
  compte deux fois plus de pensionnés de moins de 65 ans, mais près de la
  moitié — l'invalidité, l'AAH, la réversion seule, mesurées le 17 octobre
  2026 (``tests/test_pensionnes_de_l_awg.py``) — ne recule pas avec l'âge
  légal : le périmètre fait peu de l'écart ; les retraités de moins de 65 ans
  du modèle, qui reculent plus tard, le plus ; puis les 65 ans et plus et la
  suspension de 2026 (notes du 16 et du 17 octobre 2026). Ceux-là reculent
  plus tard surtout parce que la grille fait partir les cohortes de 1966 et
  1967 aux conditions de la génération 1965 (note du 18 octobre 2026) ; ce
  qui en restait, parce qu'elle les fait entrer dans l'emploi au même âge à
  chaque génération (note du 19 octobre 2026, « l'entrée dans l'emploi »).
"""

from __future__ import annotations

import importlib.util
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


def test_chaque_cohorte_se_compte_des_l_annee_de_son_depart():
    """Une génération de la grille représente cinq cohortes, et ``cout.py``
    fait partir chacune l'année que le droit de sa génération lui donne
    (``Pensionne.liquidation``) : les deux plus jeunes, ici, un an plus tard
    que la génération du milieu, décalée d'autant. L'année de son départ,
    2030, la plus jeune n'est pas comptée, ni les deux plus jeunes en 2029.
    Les 65 ans et plus se comptent à leur âge de l'année ; un cas type sans
    poids ne compte pas."""
    from types import SimpleNamespace

    from retraite_notionnelle.facteurs_depense import compter_retraites, depart_de_la_grille

    propres = {-2: 2026, -1: 2027, 0: 2028, 1: 2030, 2: 2031}
    pensionnes = [SimpleNamespace(code="a", generation=1965, liquidation=propres.get),
                  SimpleNamespace(code="b", generation=1965,
                                  liquidation=lambda decalage: 2020 + decalage)]
    population = SimpleNamespace(effectif=lambda age, annee: 1000.0 + age)
    poids = {"a": 0.75, "b": 0.0}

    def compte(annee: int, age: int = 0) -> float:
        return compter_retraites(pensionnes, population, annee, poids, depart_de_la_grille,
                                 age)

    # En 2030, les cohortes de 1963 à 1967 ont de 67 à 63 ans.
    assert compte(2030) == 0.75 * (1067 + 1066 + 1065 + 1064)
    assert compte(2029) == 0.75 * (1066 + 1065 + 1064)
    assert compte(2030, 65) == 0.75 * (1067 + 1066 + 1065)
    assert compte(2025) == 0.0


def test_nee_toute_l_annee_une_cohorte_n_a_que_ses_partis_l_annee_de_son_depart():
    """La grille fait naître ses cas types en janvier : partie en octobre, une
    cohorte se compte toute au 31 décembre. Née toute l'année, au même âge,
    elle n'a encore que ses natifs de janvier à mars de partis, le quart, et
    toute l'année suivante ; partie en février, les onze douzièmes, son natif
    de décembre partant en janvier. ``mois`` dit le mois du départ de chaque
    cohorte, née en janvier ; celle qu'il ne nomme pas se compte toute."""
    from types import SimpleNamespace

    from retraite_notionnelle.facteurs_depense import compter_retraites, depart_de_la_grille

    propres = {-2: 2026, -1: 2027, 0: 2028, 1: 2030, 2: 2031}
    pensionnes = [SimpleNamespace(code="a", generation=1965, liquidation=propres.get)]
    population = SimpleNamespace(effectif=lambda age, annee: 1000.0 + age)
    mois = {("a", 1965, 1): 10, ("a", 1965, 2): 2}

    def compte(annee: int, age: int = 0) -> float:
        return compter_retraites(pensionnes, population, annee, {"a": 1.0},
                                 depart_de_la_grille, age, mois=mois)

    # En 2030, la cohorte de 1966 a 64 ans et part en octobre ; celle de 1967,
    # en février 2031, à 64 ans.
    assert compte(2030) == pytest.approx(1067 + 1066 + 1065 + 1064 * 3 / 12)
    assert compte(2031) == pytest.approx(1068 + 1067 + 1066 + 1065 + 1064 * 11 / 12)
    assert compte(2031, 65) == pytest.approx(1068 + 1067 + 1066 + 1065)
    assert compte(2028) == pytest.approx(1065 + 1064 + 1063)


def test_l_entree_dans_l_emploi_recule_d_un_an_de_la_generation_1960_a_1966():
    """La grille fait entrer ses cas types au même âge à chaque génération
    (limite n° 2 de ``cout.py``) ; l'échantillon interrégimes de cotisants de
    2017 voit les générations entrer plus tard (``macro/premier_trimestre.csv``,
    ses affiliés d'avant 23 ans). Né en 1960, un homme sur deux avait cotisé un
    trimestre à 17 ans et 10 mois : 42,7 % à la fin de l'année de ses 17 ans,
    atteinte en moyenne à 17 ans et demi, 63,8 % à celle de ses 18 ans ; né en
    1966, à 18 ans et 10 mois (45,6 et 59,3 % à 18 et 19 ans) : un an plus
    tard, au trimestre près ; une femme née en 1966, à 19 ans et demi (33,2 et
    50,1 %). Une génération que l'EIC ne suit pas lit ses deux voisines, 1967
    entre 1966 et 1968 (19,22 ans) ; une génération d'avant la première, la
    première."""
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.facteurs_depense import (
        ages_medians_du_premier_trimestre,
        decalage_d_entree,
    )

    medianes = ages_medians_du_premier_trimestre(RACINE_DONNEES)
    assert medianes[("H", 1960)] == pytest.approx(17.5 + 7.3 / 21.1)
    assert medianes[("H", 1966)] == pytest.approx(18.5 + 4.4 / 13.7)
    assert medianes[("F", 1966)] == pytest.approx(18.5 + 16.8 / 16.9)
    assert decalage_d_entree(medianes, "H", 1960, 1960) == 0.0
    assert decalage_d_entree(medianes, "H", 1966, 1960) == 1.0
    assert decalage_d_entree(medianes, "H", 1967, 1960) == 1.25
    assert (decalage_d_entree(medianes, "F", 1930, 1960)
            == decalage_d_entree(medianes, "F", 1942, 1960))


def test_entre_plus_tard_le_salarie_part_plus_tard_et_le_militaire_a_son_heure():
    """Entré à 21 ans, le salarié au salaire moyen né en janvier 1966 doit 172
    trimestres (L. 161-17-3), 43 ans : il part à 64 ans, en 2030, la cohorte de
    1966 que la génération 1965 de la grille représente. Entré un an plus tard,
    comme sa génération après celle de 1960, il part à 65 ans, douze mois plus
    tard, en 2031. Le mois, celui qui suit son anniversaire ou le sien s'il est
    né le premier (R. 351-37), tient au jour de naissance que la grille présume,
    et le test ne le dit pas. Le militaire, qui part après ses services et non
    au taux plein, garde sa date."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.castypes import GRILLE_DU_COUT
    from retraite_notionnelle.facteurs_depense import dates_des_departs

    cas = tuple(c for c in GRILLE_DU_COUT if c.code in ("salaire_moyen", "militaire"))
    parametres = Parametres(scenario_projection="cor_reference")
    grille = dates_des_departs(parametres, cas_types=cas, generations=(1965,))
    entree = dates_des_departs(parametres, entree_depuis=1960, cas_types=cas,
                               generations=(1965,))
    assert grille[("salaire_moyen", 1965, 1)].annee == 2030
    assert entree[("salaire_moyen", 1965, 1)].annee == 2031
    assert entree[("salaire_moyen", 1965, 1)].rang - grille[("salaire_moyen", 1965, 1)].rang == 12
    assert all(entree[("militaire", 1965, decalage)] == grille[("militaire", 1965, decalage)]
               for decalage in range(-2, 3))


def _script():
    spec = importlib.util.spec_from_file_location(
        "script_facteurs_depense", RACINE / "scripts" / "facteurs_depense.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_le_departage_compte_les_naissances_de_l_annee_avant_ce_qui_reste():
    """``--naissances`` ajoute la réforme entière aux cohortes nées toute
    l'année (``retraites_par_age(..., nes_toute_l_annee=True)``) : le
    départage de 2022-2030 la place après la suspension, et ce qui reste se
    compte depuis elle ; l'écart, lui, ne change pas."""
    script = _script()

    def part(agees: float, jeunes: float) -> dict:
        return {"2022-2030": {"vieillesse": agees, "precoce": jeunes,
                              "couverture": agees + jeunes}}

    stables = "et 48 % stables, mesurés"
    parts = {"Ageing Report 2024": part(-0.22, -1.16), "modèle": part(-0.08, -0.92),
             stables: part(-0.07, -1.02), script.SANS_SUSPENSION: part(-0.14, -1.02)}
    sans_naissances = script.departage(parts, stables)
    parts[script.NES_TOUTE_L_ANNEE] = part(-0.17, -0.99)
    ecarts = script.departage(parts, stables)
    assert list(ecarts) == ["le périmètre", "la suspension", "les naissances de l'année",
                            "ce qui reste", "l'écart"]
    assert ecarts["les naissances de l'année"]["vieillesse"] == pytest.approx(0.03)
    assert ecarts["les naissances de l'année"]["precoce"] == pytest.approx(-0.03)
    assert ecarts["ce qui reste"]["vieillesse"] == pytest.approx(0.05)
    assert ecarts["ce qui reste"]["precoce"] == pytest.approx(0.17)
    assert ecarts["l'écart"] == sans_naissances["l'écart"]


def test_le_departage_compte_l_entree_dans_l_emploi_apres_les_naissances():
    """``--entree`` fait en outre entrer chaque génération dans l'emploi à son
    âge, celui que l'EIC lui donne : le départage la place après les
    naissances, et ce qui reste se compte depuis elle."""
    script = _script()

    def part(agees: float, jeunes: float) -> dict:
        return {"2022-2030": {"vieillesse": agees, "precoce": jeunes,
                              "couverture": agees + jeunes}}

    stables = "et 48 % stables, mesurés"
    parts = {"Ageing Report 2024": part(-0.22, -1.16), "modèle": part(-0.08, -0.92),
             stables: part(-0.07, -1.02), script.SANS_SUSPENSION: part(-0.14, -1.02),
             script.NES_TOUTE_L_ANNEE: part(-0.17, -0.99),
             script.ENTREE_SELON_LA_GENERATION: part(-0.28, -1.15)}
    ecarts = script.departage(parts, stables)
    assert list(ecarts) == ["le périmètre", "la suspension", "les naissances de l'année",
                            "l'entrée dans l'emploi", "ce qui reste", "l'écart"]
    assert ecarts["l'entrée dans l'emploi"]["vieillesse"] == pytest.approx(0.11)
    assert ecarts["l'entrée dans l'emploi"]["precoce"] == pytest.approx(0.16)
    assert ecarts["ce qui reste"]["couverture"] == pytest.approx(-0.06 + 0.01)


def test_la_couverture_de_2022_2030_tient_au_perimetre_de_l_awg(awg):
    """De 2022 à 2030, la couverture du modèle recule de 0,84 point de PIB et
    celle de l'AWG de 1,38 (note du 16 octobre 2026) ; de 1,04 depuis que
    chaque cohorte de la grille part l'année que le droit de sa génération lui
    donne (note du 18 octobre 2026, « la date de chaque cohorte »). Ses moins
    de 65 ans reculent plus, rapportés aux 65 ans et plus, mais l'AWG en
    compte deux fois plus, l'invalidité comprise : portée à son périmètre, la
    dynamique du modèle refaisait l'essentiel de son effet, si tous la
    suivaient ; datée à chaque génération, elle le dépasse de trois dixièmes
    de point. Près de la moitié ne la suit pas (test suivant)."""
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
    assert ecart > 0.3
    assert publiee - 0.4 < portee["vieillesse"][2030] + portee["precoce"][2030] < publiee


def test_la_part_stable_mesuree_garde_sa_prevalence_parmi_les_20_64_ans(awg):
    """Mesurée (``tests/test_pensionnes_de_l_awg.py``), la part stable des
    moins de 65 ans de l'AWG est de 48 % : l'invalidité, l'AAH, la réversion
    seule. Si elle gardait son rapport aux 65 ans et plus, comme la note du 16
    octobre le supposait, la dynamique du modèle, portée au périmètre de l'AWG,
    manquerait de plus d'un demi-point l'effet de ses moins de 65 ans de 2022
    à 2070 ; gardant sa prévalence parmi les 20-64 ans, elle le refait à 0,2
    point près — 0,12 le 18 octobre, 0,16 depuis que l'ex-invalide de la Cnav
    part à soixante-deux ans dans la grille (action 138, étape 7). Reste
    2022-2030 : les retraités du modèle reculent plus tard, et en laissaient
    plus de 0,2 point (note du 17 octobre 2026), dont la grille faisait 0,18
    (note du 18 octobre, « la grille ») ; datés chacun à sa génération, ils en
    laissent 0,14, et 0,17 avec l'ex-invalide (test suivant)."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.facteurs_depense import JEUNES, STABLES, pensionnes_de_2022

    annees, _decomposition_ = _decomposition("cor_reference", "actuel")
    par_age = retraites_par_age(Parametres(scenario_projection="cor_reference"), GRILLE_AWG)
    retraites = {annee: par_age[annee][0] for annee in GRILLE_AWG}
    agees = {annee: par_age[annee][1] for annee in GRILLE_AWG}
    population_65 = {annee: annees[annee].population_65 for annee in GRILLE_AWG}
    part_pib, pensionnes, pensionnes_agees, population_65_awg = _couverture_de_l_awg(awg)
    population_20_64 = {annee: awg["series"]["population_20_64"][annee] for annee in GRILLE_AWG}
    mesures = pensionnes_de_2022(json.loads(
        (RACINE / "tests" / "temoins" / "pensionnes_de_2022.json").read_text(encoding="utf-8")))
    premiere = GRILLE_AWG[0]
    stable = (sum(mesures[categorie][tranche] for categorie in STABLES for tranche in JEUNES)
              / ((pensionnes[premiere] - pensionnes_agees[premiere]) * 1000))
    vieux = pensionnes_agees[premiere] / population_65_awg[premiere]
    plus_jeunes = pensionnes[premiere] / population_65_awg[premiere] - vieux

    def precoce(population_stable=None) -> dict:
        return partager_couverture(part_pib, *au_perimetre(
            population_65_awg, vieux, plus_jeunes, retraites, agees, population_65,
            stable=stable, population_stable=population_stable),
            population_65_awg)["precoce"]

    publie = partager_couverture(part_pib, pensionnes, pensionnes_agees,
                                 population_65_awg)["precoce"]
    aux_65_ans, aux_20_64_ans = precoce(), precoce(population_20_64)
    assert aux_65_ans[2070] - publie[2070] > 0.5
    assert abs(aux_20_64_ans[2070] - publie[2070]) < 0.2
    assert aux_20_64_ans[2030] - publie[2030] > 0.05


def test_datee_a_sa_generation_chaque_cohorte_part_l_annee_de_son_droit(awg):
    """La grille faisait partir les cohortes de 1963 à 1967 aux conditions de
    la génération 1965, née en janvier, que la suspension de la loi de
    financement pour 2026 tient à 170 trimestres (L. 161-17-3) : entré à 21
    ans, le salarié au salaire moyen part à 63 ans et demi, en 2028, et sa
    cohorte de 1967 deux ans plus tard. Née en 1967, il lui en faut 172,
    43 ans : il part à 64 ans, en 2031, et ``cout.py`` le fait désormais
    partir là (``Pensionne.departs``). Moins de cohortes de moins de 65 ans
    sont parties en 2030 : de 2022 à 2030, leur effet, porté au périmètre de
    l'AWG, s'écarte de celui de l'AWG de 0,14 point, quand la grille l'en
    écartait de 0,29 (notes du 18 octobre 2026, « la grille » et « la date de
    chaque cohorte ») ; de 0,17 depuis que l'ex-invalide de la Cnav part à
    soixante-deux ans dans la grille (action 138, étape 7)."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.facteurs_depense import JEUNES, STABLES, pensionnes_de_2022

    parametres = Parametres(scenario_projection="cor_reference")
    annees, _decomposition_ = _decomposition("cor_reference", "actuel")
    population_65 = {annee: annees[annee].population_65 for annee in GRILLE_AWG}
    part_pib, pensionnes, pensionnes_agees, population_65_awg = _couverture_de_l_awg(awg)
    population_20_64 = {annee: awg["series"]["population_20_64"][annee] for annee in GRILLE_AWG}
    mesures = pensionnes_de_2022(json.loads(
        (RACINE / "tests" / "temoins" / "pensionnes_de_2022.json").read_text(encoding="utf-8")))
    premiere = GRILLE_AWG[0]
    stable = (sum(mesures[categorie][tranche] for categorie in STABLES for tranche in JEUNES)
              / ((pensionnes[premiere] - pensionnes_agees[premiere]) * 1000))
    vieux = pensionnes_agees[premiere] / population_65_awg[premiere]
    plus_jeunes = pensionnes[premiere] / population_65_awg[premiere] - vieux

    par_age = retraites_par_age(parametres, GRILLE_AWG)
    datee = partager_couverture(part_pib, *au_perimetre(
        population_65_awg, vieux, plus_jeunes,
        {annee: par_age[annee][0] for annee in GRILLE_AWG},
        {annee: par_age[annee][1] for annee in GRILLE_AWG}, population_65,
        stable=stable, population_stable=population_20_64),
        population_65_awg)["precoce"]
    publie = partager_couverture(part_pib, pensionnes, pensionnes_agees,
                                 population_65_awg)["precoce"]
    assert abs(datee[2030] - publie[2030]) < 0.2


def test_entree_selon_sa_generation_la_grille_recule_comme_l_awg_avant_65_ans(awg):
    """La grille fait entrer ses cas types au même âge à chaque génération,
    quand l'EIC de 2017 voit celles de 1966 à 1970 entrer un an après celle de
    1960 (test du recul de l'entrée) ; Destinie, le modèle de l'AWG pour la
    France, fait partir plus tard ceux qui ont fini leurs études plus tard
    (fiche France, § 3.3). Nées toute l'année, puis entrées selon leur
    génération depuis 1960, les cohortes de la grille ont de 2022 à 2030 une
    couverture qui, portée au périmètre de l'AWG, recule de plus de 0,15 point
    de PIB de plus : ce qui restait de l'écart. Leurs moins de 65 ans reculent
    alors comme ceux de l'AWG, à 0,1 point près, de 2022 à 2030 comme de 2030 à
    2070 ; leurs 65 ans et plus, de 2030 à 2070, de plus de 0,1 point de plus :
    la grille fait partir chacun au taux plein, au-delà de 65 ans quand il
    entre plus tard (note du 19 octobre 2026, « l'entrée dans l'emploi »)."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.facteurs_depense import JEUNES, STABLES, pensionnes_de_2022

    parametres = Parametres(scenario_projection="cor_reference")
    annees, _decomposition_ = _decomposition("cor_reference", "actuel")
    population_65 = {annee: annees[annee].population_65 for annee in GRILLE_AWG}
    part_pib, pensionnes, pensionnes_agees, population_65_awg = _couverture_de_l_awg(awg)
    population_20_64 = {annee: awg["series"]["population_20_64"][annee] for annee in GRILLE_AWG}
    mesures = pensionnes_de_2022(json.loads(
        (RACINE / "tests" / "temoins" / "pensionnes_de_2022.json").read_text(encoding="utf-8")))
    premiere = GRILLE_AWG[0]
    stable = (sum(mesures[categorie][tranche] for categorie in STABLES for tranche in JEUNES)
              / ((pensionnes[premiere] - pensionnes_agees[premiere]) * 1000))
    vieux = pensionnes_agees[premiere] / population_65_awg[premiere]
    plus_jeunes = pensionnes[premiere] / population_65_awg[premiere] - vieux

    def portee(**options) -> dict:
        par_age = retraites_par_age(parametres, GRILLE_AWG, nes_toute_l_annee=True, **options)
        return partager_couverture(part_pib, *au_perimetre(
            population_65_awg, vieux, plus_jeunes,
            {annee: par_age[annee][0] for annee in GRILLE_AWG},
            {annee: par_age[annee][1] for annee in GRILLE_AWG}, population_65,
            stable=stable, population_stable=population_20_64),
            population_65_awg)

    def entre(serie: dict, debut: int, fin: int) -> float:
        return serie[fin] - (serie[debut] if debut > premiere else 0.0)

    nes, entres = portee(), portee(entree_depuis=1960)
    publie = partager_couverture(part_pib, pensionnes, pensionnes_agees, population_65_awg)
    assert (sum(nes[part][2030] for part in nes)
            - sum(entres[part][2030] for part in entres)) > 0.15
    for debut, fin in ((2022, 2030), (2030, 2070)):
        assert abs(entre(entres["precoce"], debut, fin)
                   - entre(publie["precoce"], debut, fin)) < 0.1, (debut, fin)
    assert (entre(entres["vieillesse"], 2030, 2070)
            < entre(publie["vieillesse"], 2030, 2070) - 0.1)
