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
  Entrées selon leur génération, ses 65 ans et plus reculent plus que ceux de
  l'AWG ; partie pour une part à l'âge légal avec une décote, comme la
  génération 1953, la grille les en rapproche sous la réforme de 2023 entière
  avant 2030, non après (note du 19 octobre 2026, « les départs hors du taux
  plein »). Après 2030, ni la décote selon la génération, qui n'en rend qu'un
  centième, ni l'entrée lue sur la durée validée, qui les fait reculer plus
  encore, ne les expliquent (note du 23 octobre 2026, « les 65 ans et plus
  d'après 2030 »). Ni l'âge où la grille fait partir chaque génération, pesée
  à ses poids : entrée selon sa génération, elle part à l'âge moyen que le COR
  projette ; c'est la forme de ses départs qui diffère de celle de la France
  (note du 24 octobre 2026, « l'âge de départ de chaque génération »).
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
TEMOIN_EIC = RACINE / "tests" / "temoins" / "drees_duree_validee_2017.json"
TEMOIN_COR_AGES = RACINE / "tests" / "temoins" / "cor_age_depart_generations_2026.json"


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


def test_une_part_de_la_cohorte_part_avant_son_taux_plein_avec_une_decote():
    """La grille fait partir chacun au taux plein ; ``decotes`` fait partir
    une part de la cohorte plus tôt, avec une décote, à la date qu'il lui
    donne, et le reste au taux plein. La cohorte qu'il ne nomme pas part toute
    au taux plein. Née toute l'année, la part décotée n'a de partis, l'année
    de son départ, que ses natifs des premiers mois, comme le reste ; née en
    janvier, elle se compte toute dès cette année-là."""
    from types import SimpleNamespace

    from retraite_notionnelle.facteurs_depense import compter_retraites, depart_de_la_grille

    propres = {-2: 2026, -1: 2027, 0: 2028, 1: 2030, 2: 2031}
    pensionnes = [SimpleNamespace(code="a", generation=1965, liquidation=propres.get)]
    population = SimpleNamespace(effectif=lambda age, annee: 1000.0 + age)
    # La cohorte de 1967 part au taux plein en février 2031, à 64 ans ; un
    # cinquième part en octobre 2029, à 62 ans, avec une décote.
    decotes = {("a", 1965, 2): (0.2, 2029, 10)}

    def compte(annee: int, age: int = 0, mois: dict | None = None) -> float:
        return compter_retraites(pensionnes, population, annee, {"a": 1.0},
                                 depart_de_la_grille, age, mois=mois, decotes=decotes)

    # En 2029, les cohortes de 1963 à 1967 ont de 66 à 62 ans.
    assert compte(2029) == pytest.approx(1066 + 1065 + 1064 + 0.2 * 1062)
    assert compte(2030) == pytest.approx(1067 + 1066 + 1065 + 1064 + 0.2 * 1063)
    assert compte(2031) == pytest.approx(1068 + 1067 + 1066 + 1065 + 1064)
    assert compte(2029, 65) == pytest.approx(1066 + 1065)
    nes = {("a", 1965, 2): 2}
    assert compte(2029, mois=nes) == pytest.approx(1066 + 1065 + 1064 + 0.2 * 1062 * 3 / 12)
    assert compte(2031, mois=nes) == pytest.approx(
        1068 + 1067 + 1066 + 1065 + 1064 * (0.8 * 11 / 12 + 0.2))


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


def test_la_pyramide_compte_chaque_cohorte_de_la_grille_des_son_depart():
    """Chacune des cinq cohortes de chaque couple de la grille du coût part,
    sous le droit de sa génération, l'année d'un âge que la pyramide compte :
    son plancher ne retire à aucune ses premières années de pension. Le plus
    précoce, le militaire radié à 48 ans et demi (action 152), part l'année de
    ses 48 ans, à chaque génération ; l'agent de conduite de la SNCF, à 50 ans
    au plus tôt, sous le droit des générations d'avant 1950 (action 138, étape
    3)."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.donnees.population import AGE_MINIMAL
    from retraite_notionnelle.facteurs_depense import dates_des_departs

    dates = dates_des_departs(Parametres(scenario_projection="cor_reference"))
    ages = {}
    for (code, generation, decalage), date in dates.items():
        ages.setdefault(code, set()).add(date.annee - generation - decalage)
    assert min(min(par_cas) for par_cas in ages.values()) >= AGE_MINIMAL
    assert ages["militaire"] == {48}
    assert min(ages["agent_sncf_conduite"]) == 50


def test_le_temoin_de_l_eic_dit_sa_source_et_redonne_ses_cumuls():
    """Le cumul des trimestres validés par affilié d'avant 23 ans, à la fin de
    l'année de chaque âge, que la DREES tire de l'échantillon interrégimes de
    cotisants de 2017 (``tests/temoins/drees_duree_validee_2017.json``,
    ``scripts/fetch/drees_duree_validee.py``) : les hommes nés en 1960 en
    avaient validé 102,9 à 47 ans, ceux nés en 1970 96,3 ; les femmes nées en
    1966, 106,3 à 51 ans. Chaque génération y est suivie de 16 ans à son âge de
    2017, 71 ans au plus ; un cumul ne baisse pas d'un âge au suivant, et n'y
    gagne pas plus des quatre trimestres d'une année."""
    from retraite_notionnelle.facteurs_depense import durees_validees

    temoin = json.loads(TEMOIN_EIC.read_text(encoding="utf-8"))
    assert "2596_les-droits-valides-au-cours-de-la-carriere" in temoin["source"]
    assert temoin["champ"] == "Aff_avant_23ans" and temoin["annee_de_l_echantillon"] == 2017
    durees = durees_validees(temoin)
    assert durees[("H", 1960)][47] == 102.9
    assert durees[("H", 1970)][47] == 96.3
    assert durees[("F", 1966)][51] == 106.3
    assert {generation for _sexe, generation in durees} == {1942, 1946, 1950,
                                                           *range(1954, 1995, 2)}
    for (sexe, generation), cumuls in durees.items():
        assert sorted(cumuls) == list(range(16, min(71, 2017 - generation) + 1)), (sexe, generation)
        for age in sorted(cumuls)[1:]:
            assert 0.0 <= cumuls[age] - cumuls[age - 1] <= 4.0, (sexe, generation, age)


def test_lue_sur_la_duree_validee_l_entree_recule_plus_chez_les_hommes():
    """Au dernier âge que l'EIC voit chez l'une et l'autre, la génération 1970
    a validé 6,6 trimestres de moins que celle de 1960 chez les hommes, à 47
    ans (96,3 et 102,9) : un an et trois quarts, au trimestre près, quand son
    premier trimestre cotisé ne recule que d'un an et quart (test du recul de
    l'entrée) ; chez les femmes, 3,0 (92,5 et 95,5) : trois quarts d'an, pour
    un an et demi. Née en 1954, la génération en avait validé 4,2 de plus à 57
    ans (140,7 et 136,5) : un an plus tôt. La génération 1967 lit ses deux
    voisines, 1,3 et 1,5 an ; celle de 2000, la dernière que l'EIC suive,
    1994, qui avait validé 8,8 trimestres de moins à 23 ans (10,2 et 19,0)."""
    from retraite_notionnelle.facteurs_depense import decalage_par_la_duree, durees_validees

    durees = durees_validees(json.loads(TEMOIN_EIC.read_text(encoding="utf-8")))
    assert decalage_par_la_duree(durees, "H", 1960, 1960) == 0.0
    assert decalage_par_la_duree(durees, "H", 1970, 1960) == 1.75
    assert decalage_par_la_duree(durees, "F", 1970, 1960) == 0.75
    assert decalage_par_la_duree(durees, "H", 1954, 1960) == -1.0
    assert decalage_par_la_duree(durees, "H", 1967, 1960) == 1.5
    assert decalage_par_la_duree(durees, "H", 2000, 1960) == 2.25


def test_entre_selon_sa_duree_validee_le_salarie_de_1966_part_trois_mois_plus_tard():
    """Né en 1966, un homme avait validé à 51 ans 5,2 trimestres de moins que
    celui de 1960 (111,5 et 116,7) : entré un an et quart plus tard, et non un
    an comme son premier trimestre cotisé le dit, le salarié au salaire moyen
    part quinze mois après la date de la grille, et non douze, la grille
    comptant ses trimestres depuis le mois de son entrée (172 trimestres,
    L. 161-17-3). Le militaire, qui part après ses services, garde sa date."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.castypes import GRILLE_DU_COUT
    from retraite_notionnelle.facteurs_depense import dates_des_departs, durees_validees

    cas = tuple(c for c in GRILLE_DU_COUT if c.code in ("salaire_moyen", "militaire"))
    parametres = Parametres(scenario_projection="cor_reference")
    durees = durees_validees(json.loads(TEMOIN_EIC.read_text(encoding="utf-8")))
    grille = dates_des_departs(parametres, cas_types=cas, generations=(1965,))
    duree = dates_des_departs(parametres, entree_depuis=1960, cas_types=cas,
                              generations=(1965,), durees=durees)
    assert duree[("salaire_moyen", 1965, 1)].rang - grille[("salaire_moyen", 1965, 1)].rang == 15
    assert all(duree[("militaire", 1965, decalage)] == grille[("militaire", 1965, decalage)]
               for decalage in range(-2, 3))


def test_la_generation_1953_est_partie_decotee_des_l_age_legal_a_9_4_pour_cent():
    """L'EIR de 2020 range les retraités nés en 1953 par la place de leur
    départ (``macro/departs_generations.csv``, certifiée) : 31,2 % à l'âge
    légal, dont 13,8 % avec une décote ; 26,6 % entre lui et l'âge
    d'annulation de la décote, dont 19,0 % ; 8,3 % à cet âge, dont 0,2 % ;
    3,1 % après, dont 0,1 % — 9,4 % de la génération, des 10,6 % de départs
    décotés qu'elle compte. Les autres, 3,9 % des 30,9 % partis avant l'âge
    légal, relèvent des régimes qui ouvrent plus tôt, catégories actives et
    régimes spéciaux."""
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.facteurs_depense import part_decotee_des_l_age_legal

    assert part_decotee_des_l_age_legal(RACINE_DONNEES) == pytest.approx(
        (31.2 * 13.8 + 26.6 * 19.0 + 8.3 * 0.2 + 3.1 * 0.1) / 1e4)


def test_la_part_decotee_se_rapporte_aux_cohortes_qui_peuvent_decoter():
    """La grille ne peut faire partir avec une décote que les cohortes dont le
    taux plein vient après l'âge légal : la part de la génération partie ainsi
    se rapporte à leur poids parmi toutes les siennes, comme la population de
    l'étape 14 rapporte la part de l'EIR à ses carrières incomplètes. 9,4 % de
    la génération, quand ses cohortes qui peuvent décoter en pèsent les trois
    quarts : 12,5 % de chacune ; aucune ne le pouvant, rien ; et jamais plus
    que toutes."""
    from retraite_notionnelle.facteurs_depense import part_avec_decote

    poids = {("a", 1955, -2): 0.5, ("b", 1955, -2): 0.25, ("c", 1955, -2): 0.25}
    assert part_avec_decote(0.094, poids, {("a", 1955, -2), ("b", 1955, -2)}) == pytest.approx(
        0.094 / 0.75)
    assert part_avec_decote(0.094, poids, set()) == 0.0
    assert part_avec_decote(0.9, poids, {("c", 1955, -2)}) == 1.0


def test_la_cnav_a_decote_13_4_pour_cent_de_ses_liquidants_de_2024():
    """L'EIR ne suit pas les générations d'après 1953. L'EACR compte, année par
    année, les liquidants de chaque caisse selon leurs conditions de départ
    (table H, ``tests/temoins/drees_eacr_tables_2026.json``) : en 2024, la Cnav
    en a 439 202 au taux plein, 86 776 avec une décote, 122 368 avec une
    surcote — 13,4 % de décotés, quand la génération 1953 l'a été à 10,6 %."""
    from retraite_notionnelle.facteurs_depense import part_decotee_du_flux

    temoin = json.loads((RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json")
                        .read_text(encoding="utf-8"))
    assert part_decotee_du_flux(temoin) == pytest.approx(86776 / (439202 + 86776 + 122368))


def test_la_part_decotee_suit_la_generation_de_1953_au_flux_de_2024():
    """La part d'une génération partie avec une décote dès l'âge légal : 9,4 %
    jusqu'à la génération 1953, que l'EIR voit partie ; 13,4 % depuis la
    génération 1960, celle des liquidants de la Cnav de 2024 à l'âge moyen des
    nouveaux retraités de l'année, 63,6 ans tous régimes (table C de l'EACR) ;
    entre les deux, en droite ligne : 11,7 % pour la génération 1957, aux
    quatre septièmes du chemin."""
    from retraite_notionnelle.facteurs_depense import part_decotee_de_la_generation

    assert part_decotee_de_la_generation(1950, 0.094, 0.134) == 0.094
    assert part_decotee_de_la_generation(1953, 0.094, 0.134) == 0.094
    assert part_decotee_de_la_generation(1957, 0.094, 0.134) == pytest.approx(
        0.094 + 0.040 * 4 / 7)
    assert part_decotee_de_la_generation(1960, 0.094, 0.134) == 0.134
    assert part_decotee_de_la_generation(1990, 0.094, 0.134) == 0.134


def test_a_l_age_legal_peut_partir_celui_dont_le_taux_plein_vient_apres():
    """Entré à 22 ans, comme sa génération après celle de 1960, le salarié au
    salaire moyen né en janvier 1966 n'a le taux plein qu'à 65 ans, en 2031
    (172 trimestres, L. 161-17-3) ; son droit s'ouvre à 63 ans et 3 mois,
    l'âge légal de sa génération sous la suspension de 2026 (L. 161-17-2) : il
    peut partir en 2029, avec une décote. L'agent actif de la CNRACL, que son
    classement ouvre à 57 ans, garde son départ ; de même le salarié au SMIC
    entré à 18 ans, qui a le taux plein dès l'ouverture, en carrière longue, et
    le militaire, qui part après ses services."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.castypes import GRILLE_DU_COUT
    from retraite_notionnelle.facteurs_depense import dates_a_l_age_legal

    codes = ("salaire_moyen", "fonctionnaire_actif", "smic_carriere_complete", "militaire")
    cas = tuple(c for c in GRILLE_DU_COUT if c.code in codes)
    legales = dates_a_l_age_legal(Parametres(scenario_projection="cor_reference"),
                                  entree_depuis=1960, cas_types=cas, generations=(1965,))
    assert legales[("salaire_moyen", 1965, 1)].annee == 2029
    assert {code for code, _generation, _decalage in legales} == {"salaire_moyen"}


def test_le_temoin_du_cor_dit_sa_source_et_redonne_ses_ages_de_depart():
    """L'âge moyen de départ à la retraite de chaque génération, que le COR
    publie en juin 2026 (figure 4.5, ``tests/temoins/cor_age_depart_generations_2026.json``,
    ``scripts/fetch/cor_age_depart_generations.py``) : observé jusqu'à la
    génération 1954, projeté depuis elle, sous la suspension de 2026 ; 64,2 ans
    pour la génération 1906, 60,9 pour celle de 1932, comme le rapport l'écrit
    (p. 215), puis « autour de 64,6 ans à partir des générations nées dans les
    années 1975 ». La part de chaque génération déjà partie, avant son âge
    légal, à la fin de l'année de chaque âge (figure 4.7) : 15 % de la
    génération 1949 à 57 ans, 22 % à 59 ans, son pic ; 30 % de celle de 1953
    à 60 ans, quand elle n'ouvre qu'à 61 (p. 219-220). La part des résidents
    de chaque âge déjà partie au 31 décembre 2024 (figure 4.6) : 48,1 % des 62
    ans (p. 218)."""
    temoin = json.loads(TEMOIN_COR_AGES.read_text(encoding="utf-8"))
    assert "Données_RA2026_P4_0.xlsx" in temoin["source"]["reference"]
    ages = temoin["age_moyen_de_depart"]
    assert round(ages["observe"]["1906"], 1) == 64.2
    assert round(ages["observe"]["1932"], 1) == 60.9
    assert ages["projete"]["1954"] == ages["observe"]["1954"]
    assert all(abs(ages["projete"][str(generation)] - 64.6) < 0.2
               for generation in range(1975, 2001))
    partis = temoin["retraites_avant_l_age_legal"]
    assert round(partis["57"]["1949"], 2) == 0.15
    assert round(partis["59"]["1949"], 2) == 0.22
    assert round(partis["60"]["1953"], 1) == 0.3
    assert round(temoin["retraites_par_age_en_2024"]["ensemble"]["62"], 3) == 0.481


def test_l_age_moyen_de_depart_pese_chaque_cohorte_du_poids_de_son_cas_type_a_65_ans():
    """L'âge moyen de départ d'une génération de la grille : celui de ses
    cohortes, nées en janvier, chacune à l'âge du mois où elle part, pesée du
    poids de son cas type l'année où sa génération atteint 65 ans — comme le
    COR compte chaque liquidant, sans l'effectif de la pyramide, qui ne
    commence qu'à 50 ans, quand le militaire part à 48. Nées en 1970, la
    cohorte du cas a part en mars 2034, à 64 ans et 2 mois, celle du cas b en
    janvier 2037, à 67 ans ; pesées en 2035, 0,75 et 0,25 : 64,875 ans. Nées
    en 1971, en mars 2035 et en juillet 2038, pesées en 2036, à moitié :
    65,833 ans. Que 40 % de la cohorte du cas b de 1970 parte à l'âge légal,
    en janvier 2034, avec une décote : elle part en moyenne à 65,8 ans, et la
    génération à 64,575."""
    from retraite_notionnelle.calendrier import DateMois
    from retraite_notionnelle.facteurs_depense import ages_moyens_de_depart

    departs = {("a", 1970, 0): DateMois(2034, 3), ("b", 1970, 0): DateMois(2037, 1),
               ("a", 1970, 1): DateMois(2035, 3), ("b", 1970, 1): DateMois(2038, 7)}
    poids = {2035: {"a": 0.75, "b": 0.25}, 2036: {"a": 0.5, "b": 0.5}}
    ages = ages_moyens_de_depart(departs, poids.__getitem__)
    assert ages == pytest.approx({1970: 64.875, 1971: (64 + 2 / 12 + 67.5) / 2})
    decotes = {("b", 1970, 0): (0.4, DateMois(2034, 1))}
    assert ages_moyens_de_depart(departs, poids.__getitem__, decotes)[1970] == pytest.approx(
        0.75 * (64 + 2 / 12) + 0.25 * (0.6 * 67 + 0.4 * 64))


def test_la_part_partie_a_chaque_age_compte_les_natifs_de_toute_l_annee():
    """La part d'une génération de la grille partie au 31 décembre de l'année
    de chaque âge, comme le COR compte ses retraités (figures 4.6 et 4.7) : ses
    cohortes pesées comme pour l'âge moyen, nées toute l'année et non en
    janvier (:func:`compter_retraites`). Née en 1970, la cohorte du cas a, qui
    part en mars 2034 née en janvier, n'en a au 31 décembre 2034 que les dix
    douzièmes de partis : 0,75 × 10/12, 62,5 % de la génération à 64 ans ; 75 %
    à 66 ans ; celle du cas b, partie en janvier 2037 née en janvier, l'est
    toute à 67 ans. Que 40 % de la cohorte du cas b parte en janvier 2034,
    avec une décote : 72,5 % de la génération à 64 ans."""
    from retraite_notionnelle.calendrier import DateMois
    from retraite_notionnelle.facteurs_depense import parts_parties

    departs = {("a", 1970, 0): DateMois(2034, 3), ("b", 1970, 0): DateMois(2037, 1)}
    poids = {2035: {"a": 0.75, "b": 0.25}}
    assert parts_parties(departs, poids.__getitem__, (64, 66, 67)) == pytest.approx(
        {(1970, 64): 0.625, (1970, 66): 0.75, (1970, 67): 1.0})
    decotes = {("b", 1970, 0): (0.4, DateMois(2034, 1))}
    assert parts_parties(departs, poids.__getitem__, (64,), decotes) == pytest.approx(
        {(1970, 64): 0.725})


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


def test_le_departage_compte_les_departs_hors_du_taux_plein_apres_l_entree():
    """``--decote`` fait en outre partir à l'âge légal, avec une décote, une
    part des cohortes qui n'ont le taux plein qu'après lui : le départage la
    place après l'entrée dans l'emploi, et ce qui reste se compte depuis elle ;
    l'écart ne change pas."""
    script = _script()

    def part(agees: float, jeunes: float) -> dict:
        return {"2022-2030": {"vieillesse": agees, "precoce": jeunes,
                              "couverture": agees + jeunes}}

    stables = "et 48 % stables, mesurés"
    parts = {"Ageing Report 2024": part(-0.22, -1.16), "modèle": part(-0.08, -0.92),
             stables: part(-0.07, -1.02), script.SANS_SUSPENSION: part(-0.14, -1.02),
             script.NES_TOUTE_L_ANNEE: part(-0.17, -0.99),
             script.ENTREE_SELON_LA_GENERATION: part(-0.28, -1.15)}
    sans_decote = script.departage(parts, stables)
    parts[script.AVEC_DECOTE] = part(-0.25, -1.18)
    ecarts = script.departage(parts, stables)
    assert list(ecarts) == ["le périmètre", "la suspension", "les naissances de l'année",
                            "l'entrée dans l'emploi", "les départs hors du taux plein",
                            "ce qui reste", "l'écart"]
    assert ecarts["les départs hors du taux plein"]["vieillesse"] == pytest.approx(-0.03)
    assert ecarts["les départs hors du taux plein"]["precoce"] == pytest.approx(0.03)
    assert ecarts["ce qui reste"]["vieillesse"] == pytest.approx(-0.03)
    assert ecarts["ce qui reste"]["precoce"] == pytest.approx(-0.02)
    assert ecarts["l'écart"] == sans_decote["l'écart"]


def test_le_departage_compte_la_decote_selon_la_generation_apres_celle_de_1953():
    """``--decote-generation`` fait suivre à la part décotée sa génération, de
    celle de 1953 au flux de la Cnav de 2024 : le départage la place après les
    départs hors du taux plein, et ce qui reste se compte depuis elle ;
    l'écart ne change pas."""
    script = _script()

    def part(agees: float, jeunes: float) -> dict:
        return {"2022-2030": {"vieillesse": agees, "precoce": jeunes,
                              "couverture": agees + jeunes}}

    stables = "et 48 % stables, mesurés"
    parts = {"Ageing Report 2024": part(-0.22, -1.16), "modèle": part(-0.08, -0.92),
             stables: part(-0.07, -1.02), script.SANS_SUSPENSION: part(-0.14, -1.02),
             script.NES_TOUTE_L_ANNEE: part(-0.17, -0.99),
             script.ENTREE_SELON_LA_GENERATION: part(-0.28, -1.15),
             script.AVEC_DECOTE: part(-0.25, -1.18)}
    sans_generation = script.departage(parts, stables)
    parts[script.DECOTE_SELON_LA_GENERATION] = part(-0.24, -1.18)
    ecarts = script.departage(parts, stables)
    assert list(ecarts) == ["le périmètre", "la suspension", "les naissances de l'année",
                            "l'entrée dans l'emploi", "les départs hors du taux plein",
                            "la décote selon la génération", "ce qui reste", "l'écart"]
    assert ecarts["la décote selon la génération"]["vieillesse"] == pytest.approx(-0.01)
    assert ecarts["la décote selon la génération"]["precoce"] == pytest.approx(0.0)
    assert ecarts["ce qui reste"]["vieillesse"] == pytest.approx(-0.02)
    assert ecarts["l'écart"] == sans_generation["l'écart"]


def test_le_departage_compte_l_entree_selon_la_duree_validee_apres_la_decote():
    """``--duree`` lit en outre l'entrée de chaque génération sur sa durée
    validée et non sur son premier trimestre cotisé : le départage la place
    après la décote selon la génération, et ce qui reste se compte depuis
    elle ; l'écart ne change pas."""
    script = _script()

    def part(agees: float, jeunes: float) -> dict:
        return {"2022-2030": {"vieillesse": agees, "precoce": jeunes,
                              "couverture": agees + jeunes}}

    stables = "et 48 % stables, mesurés"
    parts = {"Ageing Report 2024": part(-0.22, -1.16), "modèle": part(-0.08, -0.92),
             stables: part(-0.07, -1.02), script.SANS_SUSPENSION: part(-0.14, -1.02),
             script.NES_TOUTE_L_ANNEE: part(-0.17, -0.99),
             script.ENTREE_SELON_LA_GENERATION: part(-0.28, -1.15),
             script.AVEC_DECOTE: part(-0.25, -1.18),
             script.DECOTE_SELON_LA_GENERATION: part(-0.24, -1.18)}
    sans_duree = script.departage(parts, stables)
    parts[script.ENTREE_PAR_LA_DUREE] = part(-0.27, -1.20)
    ecarts = script.departage(parts, stables)
    assert list(ecarts) == ["le périmètre", "la suspension", "les naissances de l'année",
                            "l'entrée dans l'emploi", "les départs hors du taux plein",
                            "la décote selon la génération", "l'entrée selon la durée validée",
                            "ce qui reste", "l'écart"]
    assert ecarts["l'entrée selon la durée validée"]["vieillesse"] == pytest.approx(0.03)
    assert ecarts["l'entrée selon la durée validée"]["precoce"] == pytest.approx(0.02)
    assert ecarts["ce qui reste"]["vieillesse"] == pytest.approx(-0.05)
    assert ecarts["l'écart"] == sans_duree["l'écart"]


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
    à 2070 ; gardant sa prévalence parmi les 20-64 ans, elle le refait à un
    quart de point près — 0,12 le 18 octobre, 0,16 depuis que l'ex-invalide de
    la Cnav part à soixante-deux ans dans la grille (action 138, étape 7), 0,22
    depuis que le militaire y compte dès l'année de ses 48 ans, et à l'horizon
    ceux de la génération 2020 (étape 3, 24 octobre). Reste
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
    assert abs(aux_20_64_ans[2070] - publie[2070]) < 0.25
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


def test_partis_a_l_age_legal_avec_une_decote_les_65_ans_et_plus_reculent_moins(awg):
    """Entrée selon sa génération, la grille porte au-delà de 65 ans le taux
    plein du salarié au salaire moyen, du fonctionnaire sédentaire et du cadre
    (test précédent). La génération 1953 est partie avec une décote dès l'âge
    légal à 9,4 % (EIR) : la même part de la génération, prise à ses cohortes
    de la grille qui n'ont le taux plein qu'après lui, part à l'âge légal
    (``avec_decote``). Chaque année compte au moins autant de retraités ; leurs
    65 ans et plus, portés au périmètre de l'AWG, reculent de 0,02 point de
    PIB de moins au moins, de 2022 à 2030 comme de 2030 à 2070, mais toujours
    de plus de 0,1 point de plus que ceux de l'AWG après 2030 ; leurs moins de
    65 ans bougent de moins de 0,03 point (note du 19 octobre 2026, « les
    départs hors du taux plein »)."""
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
    comptes = {decote: retraites_par_age(parametres, GRILLE_AWG, nes_toute_l_annee=True,
                                         entree_depuis=1960, avec_decote=decote)
               for decote in (False, True)}
    for annee in GRILLE_AWG:
        assert all(avec >= sans - 1e-6 for avec, sans in zip(comptes[True][annee],
                                                              comptes[False][annee])), annee

    def portee(par_age: dict) -> dict:
        return partager_couverture(part_pib, *au_perimetre(
            population_65_awg, vieux, plus_jeunes,
            {annee: par_age[annee][0] for annee in GRILLE_AWG},
            {annee: par_age[annee][1] for annee in GRILLE_AWG}, population_65,
            stable=stable, population_stable=population_20_64),
            population_65_awg)

    def entre(serie: dict, debut: int, fin: int) -> float:
        return serie[fin] - (serie[debut] if debut > premiere else 0.0)

    entres, decotes = portee(comptes[False]), portee(comptes[True])
    publie = partager_couverture(part_pib, pensionnes, pensionnes_agees, population_65_awg)
    for debut, fin in ((2022, 2030), (2030, 2070)):
        assert (entre(decotes["vieillesse"], debut, fin)
                > entre(entres["vieillesse"], debut, fin) + 0.02), (debut, fin)
        assert abs(entre(decotes["precoce"], debut, fin)
                   - entre(entres["precoce"], debut, fin)) < 0.03, (debut, fin)
    assert (entre(decotes["vieillesse"], 2030, 2070)
            < entre(publie["vieillesse"], 2030, 2070) - 0.1)


def test_selon_sa_generation_la_decote_rend_peu_aux_65_ans_et_plus_apres_2030(awg):
    """La génération 1953 est partie avec une décote dès l'âge légal à 9,4 %
    (EIR) ; la Cnav a décoté 13,4 % de ses liquidants de 2024 (EACR). Prise à
    la part de sa génération, de l'une à l'autre (``decote_du_flux``), la
    décote fait partir à l'âge légal 1,4 fois plus des cohortes d'après 1960
    qui n'ont le taux plein qu'après lui. Le compte est linéaire en cette part :
    les 0,03 point de PIB que celle de 1953 rendait aux 65 ans et plus de 2030
    à 2070 en deviennent 0,04. Chaque année compte au moins autant de
    retraités ; de 2030 à 2070, les 65 ans et plus, portés au périmètre de
    l'AWG, reculent de 0,005 point de moins au moins, et de 0,03 au plus, mais
    toujours de plus de 0,07 point de plus que ceux de l'AWG (note du 23
    octobre 2026, « la décote selon la génération »)."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.facteurs_depense import (
        JEUNES,
        STABLES,
        part_decotee_du_flux,
        pensionnes_de_2022,
    )

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
    du_flux = part_decotee_du_flux(json.loads(
        (RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json").read_text(encoding="utf-8")))
    comptes = {flux: retraites_par_age(parametres, GRILLE_AWG, nes_toute_l_annee=True,
                                       entree_depuis=1960, avec_decote=True,
                                       decote_du_flux=flux)
               for flux in (None, du_flux)}
    for annee in GRILLE_AWG:
        assert all(selon >= de_1953 - 1e-6 for selon, de_1953 in zip(comptes[du_flux][annee],
                                                                     comptes[None][annee])), annee

    def portee(par_age: dict) -> dict:
        return partager_couverture(part_pib, *au_perimetre(
            population_65_awg, vieux, plus_jeunes,
            {annee: par_age[annee][0] for annee in GRILLE_AWG},
            {annee: par_age[annee][1] for annee in GRILLE_AWG}, population_65,
            stable=stable, population_stable=population_20_64),
            population_65_awg)

    def entre(serie: dict, debut: int, fin: int) -> float:
        return serie[fin] - (serie[debut] if debut > premiere else 0.0)

    de_1953, selon = portee(comptes[None]), portee(comptes[du_flux])
    publie = partager_couverture(part_pib, pensionnes, pensionnes_agees, population_65_awg)
    gain = entre(selon["vieillesse"], 2030, 2070) - entre(de_1953["vieillesse"], 2030, 2070)
    assert 0.005 < gain < 0.03
    assert (entre(selon["vieillesse"], 2030, 2070)
            < entre(publie["vieillesse"], 2030, 2070) - 0.07)


def test_entree_selon_sa_duree_validee_les_65_ans_et_plus_reculent_plus_tot(awg):
    """Lue sur la durée validée au dernier âge que l'EIC voit, l'entrée des
    hommes recule plus que leur premier trimestre cotisé à chaque génération de
    1964 à 1992 ; la génération 1954, qui avait validé plus que celle de 1960,
    entre un an plus tôt, et non six mois ; au-delà de 1994, la dernière que
    l'EIC suive, les deux lectures donnent son retard, deux ans et quart (test
    de l'entrée lue sur la durée validée). Les cas types de la grille sont des
    hommes, sauf la carrière interrompue, au taux plein dès l'ouverture.
    Parties pour la part de leur génération à l'âge légal avec une décote
    (``decote_du_flux``), les cohortes de la grille comptent dès 2030 chaque
    année au plus autant de retraités, et en 2070 autant : nés de 2003 à 2005,
    ses 65 à 67 ans ont le même retard sous les deux lectures, et les plus
    vieux sont tous partis. Ceux de 2030, nés de 1963 à 1965, entrent plus
    tard sous la durée validée ; ceux de 2022, nés de 1955 à 1957, plus tôt :
    portés au périmètre de l'AWG, les 65 ans et plus reculent de plus de 0,02
    point de PIB de plus de 2022 à 2030, et de plus de 0,02 point de moins de
    2030 à 2070. La durée validée avance leur recul (note du 23 octobre 2026,
    « les 65 ans et plus d'après 2030 »)."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.facteurs_depense import (
        JEUNES,
        STABLES,
        durees_validees,
        part_decotee_du_flux,
        pensionnes_de_2022,
    )

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
    du_flux = part_decotee_du_flux(json.loads(
        (RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json").read_text(encoding="utf-8")))
    durees = durees_validees(json.loads(TEMOIN_EIC.read_text(encoding="utf-8")))
    comptes = {lue: retraites_par_age(parametres, GRILLE_AWG, nes_toute_l_annee=True,
                                      entree_depuis=1960, avec_decote=True,
                                      decote_du_flux=du_flux, durees=durees if lue else None)
               for lue in (False, True)}
    for annee in (annee for annee in GRILLE_AWG if annee >= 2030):
        assert all(duree <= trimestre + 1e-6 for duree, trimestre in zip(
            comptes[True][annee], comptes[False][annee])), annee
    assert comptes[True][2070] == pytest.approx(comptes[False][2070], rel=1e-9)

    def portee(par_age: dict) -> dict:
        return partager_couverture(part_pib, *au_perimetre(
            population_65_awg, vieux, plus_jeunes,
            {annee: par_age[annee][0] for annee in GRILLE_AWG},
            {annee: par_age[annee][1] for annee in GRILLE_AWG}, population_65,
            stable=stable, population_stable=population_20_64),
            population_65_awg)

    def entre(serie: dict, debut: int, fin: int) -> float:
        return serie[fin] - (serie[debut] if debut > premiere else 0.0)

    trimestre, duree = portee(comptes[False]), portee(comptes[True])
    assert (entre(duree["vieillesse"], 2022, 2030)
            < entre(trimestre["vieillesse"], 2022, 2030) - 0.02)
    assert (entre(duree["vieillesse"], 2030, 2070)
            > entre(trimestre["vieillesse"], 2030, 2070) + 0.02)


@lru_cache(maxsize=None)
def _departs_des_mesures() -> dict:
    """Les départs de la grille sous chaque mesure du départage, cumulées,
    comme ``scripts/facteurs_depense.py --ages`` les confronte au COR."""
    return _script().departs_des_mesures(1960)


def _ages_du_cor() -> dict[int, float]:
    temoin = json.loads(TEMOIN_COR_AGES.read_text(encoding="utf-8"))
    return {int(generation): age for serie in ("observe", "projete")
            for generation, age in temoin["age_moyen_de_depart"][serie].items()}


def test_pesee_a_ses_poids_la_grille_part_avant_le_cor_et_entree_selon_sa_generation_apres_lui():
    """L'âge moyen de départ de chaque génération de la grille, pesée à ses
    poids, contre celui du COR (figure 4.5 du rapport de juin 2026), sous le
    droit en vigueur, la suspension comprise (note du 24 octobre 2026, « l'âge
    de départ de chaque génération »). Telle que ``cout.py`` la fait partir,
    chaque génération entrée au même âge, la grille fait partir celles de 1975
    à 2000 à 64,0 ans en moyenne, un demi-an avant le COR, et chacune avant
    lui : ses militaires, ses agents de conduite et des IEG, ses actifs, ses
    inaptes, ses ex-invalides et son salarié au SMIC, en carrière longue, près
    d'un tiers de ses poids, partent avant 63 ans. Entrées dans l'emploi selon
    leur génération, elles partent deux dixièmes d'an après lui, à 64,7 ans ;
    selon leur durée validée, partie pour une part avec une décote, avec lui,
    à deux centièmes près. Le cadre, l'artisan, le contractuel et le libéral,
    qui partent alors à 67 ans, ne font pas partir la grille plus tard que la
    France.

    Jusqu'au 24 octobre 2026, elle les faisait partir à 63,8 ans, sept
    dixièmes d'an avant le COR, avec lui l'entrée selon la génération, à deux
    dixièmes l'entrée selon la durée validée : chaque cas type recevait la
    part de sa caisse dans le stock des retraités, que les départs précoces
    grossissent de leurs années de retraite de plus. Le poids d'une génération
    est une part de ses départs, que chaque caisse divisée par les têtes de ses
    cas types lui donne (action 138, étape 3) : le militaire y pèse 1,5 % en
    2045, et non plus 2,3 %."""
    from retraite_notionnelle.facteurs_depense import ages_moyens_de_depart

    script = _script()
    publie = _ages_du_cor()
    ages = {nom: ages_moyens_de_depart(*mesure) for nom, mesure in _departs_des_mesures().items()}
    projetees = range(1975, 2001)

    def ecart(nom: str) -> float:
        return sum(ages[nom][generation] - publie[generation]
                   for generation in projetees) / len(projetees)

    assert -0.7 < ecart(script.GRILLE_DE_COUT) < -0.35
    assert all(ages[script.GRILLE_DE_COUT][generation] < publie[generation]
               for generation in projetees)
    assert 0.1 < ecart(script.ENTREE_SELON_LA_GENERATION) < 0.3
    assert abs(ecart(script.ENTREE_PAR_LA_DUREE)) < 0.1


def test_la_grille_fait_partir_moins_que_la_france_avant_l_age_legal_et_tous_a_67_ans():
    """La forme des départs, là où le COR la publie : la grille, telle que
    ``cout.py`` la fait partir, a moins de départs que la France avant l'âge
    légal, et n'en a presque plus après 66 ans. À 61 ans, les générations 1955
    à 1960 sont parties à 26 à 34 % en France (figure 4.7), où les carrières
    longues partent dès 60 ans, à 16 à 20 % dans la grille, qui n'en a qu'une,
    le salarié au SMIC entré à 18 ans. Au 31 décembre 2024, la France a 48 % de
    retraités à 62 ans, 71 % à 63 (figure 4.6), la grille 34 et 54 % ; à 66 et
    67 ans, la France 87 et 94 %, la grille 98 et 100 % : ses cas types partent
    tous au taux plein, aucun au-delà, ni surcote ni départ tardif. La grille
    en avait 17 à 22 % à 61 ans, 36 et 57 % à 62 et 63 ans, jusqu'à ce que
    chaque caisse se divise par les têtes de ses cas types, le 24 octobre 2026
    (action 138, étape 3) : ses départs précoces y pesaient la part de leurs
    caisses dans le stock des retraités, plus que dans leurs départs."""
    from retraite_notionnelle.facteurs_depense import parts_parties

    temoin = json.loads(TEMOIN_COR_AGES.read_text(encoding="utf-8"))
    avant = temoin["retraites_avant_l_age_legal"]["61"]
    en_2024 = temoin["retraites_par_age_en_2024"]["ensemble"]
    departs, poids, _decotes = _departs_des_mesures()[_script().GRILLE_DE_COUT]
    parties = parts_parties(departs, poids, range(55, 71))
    assert all(avant[str(generation)] - parties[(generation, 61)] > 0.05
               for generation in range(1955, 1961))
    assert all(en_2024[str(age)] - parties[(2024 - age, age)] > 0.10 for age in (62, 63))
    assert all(parties[(2024 - age, age)] - en_2024[str(age)] > 0.05 for age in (66, 67))
