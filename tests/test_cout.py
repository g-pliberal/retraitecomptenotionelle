"""Tests de la page « Coût » : les dépenses observées et les cinq contrefactuels.

Deux choses distinctes s'y vérifient. D'abord que les DONNÉES tiennent : la
ventilation rend le total, les codes de systèmes du modèle sont ceux
qu'écrit le vérificateur, les couvertures annoncées sont les couvertures
réelles. Ensuite que l'AGRÉGATION dit ce qu'elle prétend dire : le coût du
système actuel est la dépense observée, sans correction, et une réforme
prospective ne déplace rien avant sa bascule.
"""

from __future__ import annotations

import csv
import math
from dataclasses import replace

import pytest

from retraite_notionnelle import Parametres, memoire
from retraite_notionnelle.castypes import (
    AGENT_SEDENTAIRE_CNRACL,
    CAS_TYPES,
    DEPARTS_CNAV_2020_2024,
    DEPARTS_CNRACL_2025,
    DEPARTS_ETAT_CIVILS_2025,
    EX_INVALIDE_CNAV,
    FONCTIONNAIRE_ACTIF_ETAT,
    FONCTIONNAIRE_SUPER_ACTIF_ETAT,
    GENERATIONS,
    GRILLE_DU_COUT,
    INAPTE_CNAV,
    PART_ACTIVE_CNRACL,
    PART_ACTIVE_ETAT,
    PART_EX_INVALIDES_CNAV,
    PART_INAPTES_CNAV,
    PART_SUPER_ACTIVE_ETAT,
    cas_type_affiche,
    parts_des_caisses,
    poids_effectifs,
    poids_egaux,
)
from retraite_notionnelle.config import RACINE_DONNEES, RevalorisationStock
from retraite_notionnelle.cout import (
    _ponderation,
    CONVENTION_ASSIETTE,
    CONVENTION_RAPPORT,
    COMPOSANTE_GARANTIE,
    DERNIERE_GENERATION,
    HORIZON,
    PAS_GENERATIONS,
    PREMIERE_GENERATION,
    SCENARIOS,
    calculer_cout,
    financer,
    generations,
)
from retraite_notionnelle.cout import (
    CLES_PROSPECTIVES,
    COMPOSANTE_GARANTIE,
    CONVENTION_REVERSION_SERVIE,
    CONVENTION_REVERSION_SUPPRIMEE,
    REGLE_PRIX,
    REGLE_PROSPECTIVE,
    REGLE_STOCK,
    Dette,
    calculer_dette,
    calculer_engagements,
    masse_du_scenario,
    regle_revalorisation,
)
from retraite_notionnelle.donnees.assiette import (
    POSTES_ASSIETTE,
    AssietteActivite,
)
from retraite_notionnelle.donnees.bilan import charger_bilan
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.donnees.distribution import DistributionPensions, part_femmes
from retraite_notionnelle.donnees.cotisants import (
    COTISANTS_ETAT_2025,
    EffectifsCotisants,
)
from retraite_notionnelle.donnees.effectifs import EffectifsRetraites
from retraite_notionnelle.donnees.depenses import (
    CODES_SYSTEMES,
    SYSTEMES,
    DepensesRetraite,
)
from retraite_notionnelle.donnees.equilibre import (
    CODES_POSTES,
    CODES_TRANSFERTS,
    GROUPES,
    GROUPES_DU_MODELE,
    ORGANISMES,
    POSTES,
    POSTES_TRANSFERTS,
    REGIMES_DU_MODELE,
    REGIMES_HORS_GROUPES,
    VARIANTE_REFERENCE,
    ComptesRetraite,
    depense_maximale_toutes_variantes,
    variante_du_scenario,
    variantes_disponibles,
)
from retraite_notionnelle.donnees.population import Population
from retraite_notionnelle.garantie import (
    cout_garantie,
    cout_garantie_par_sexe,
)
from retraite_notionnelle.revalorisation import RevalorisationServie
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.droit import ouvrir


@pytest.fixture(scope="module")
def depenses() -> DepensesRetraite:
    return DepensesRetraite(RACINE_DONNEES)


@pytest.fixture(scope="module")
def population() -> Population:
    return Population(RACINE_DONNEES)


@pytest.fixture(scope="module")
def comptes() -> ComptesRetraite:
    return ComptesRetraite(RACINE_DONNEES)


@pytest.fixture(scope="module")
def cout():
    return memoire.cout(Parametres(), assiette=False, convention_recette=CONVENTION_RAPPORT)


@pytest.fixture(scope="module")
def avenir(cout):
    return cout.avenir


@pytest.fixture(scope="module")
def solde(cout):
    return cout.solde


# -- les données -------------------------------------------------------------


def test_le_total_couvre_1959_a_aujourd_hui(depenses: DepensesRetraite):
    assert depenses.premiere_annee == 1959
    assert depenses.derniere_annee >= 2024
    annees = list(depenses.total.annees())
    assert annees == list(range(depenses.premiere_annee, depenses.derniere_annee + 1))


def test_la_ventilation_commence_en_1990(depenses: DepensesRetraite):
    """De 1981 à 1989 la DREES publie une autre nomenclature : c'est une impasse
    assumée, et le fichier ne doit pas prétendre le contraire."""
    assert depenses.premiere_annee_ventilee == 1990
    for systeme in SYSTEMES:
        serie = depenses.systemes[systeme.code]
        assert serie.premiere_annee == 1990, systeme.code
        assert serie.derniere_annee == depenses.derniere_annee, systeme.code


def test_la_ventilation_rend_le_total(depenses: DepensesRetraite):
    """Le seul contrôle qui vaille sur un regroupement : rien d'oublié, rien de
    compté deux fois."""
    for annee in depenses.annees_ventilees():
        somme = sum(depenses.depense_systeme(s.code, annee) for s in SYSTEMES)
        # Un dixième de million d'euros par système : l'arrondi d'écriture, et
        # rien de plus.
        assert somme == pytest.approx(depenses.depense(annee),
                                      abs=0.1 * len(SYSTEMES)), annee


def test_les_systemes_couvrent_la_ventilation():
    """Les codes du modèle et ceux qu'écrit le vérificateur ne peuvent pas
    diverger : le fichier de référence serait lu à moitié, en silence."""
    chemin = RACINE_DONNEES / "reference" / "macro" / "depenses_retraite_regimes.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        codes = {ligne["regime"] for ligne in csv.DictReader(lignes)}
    assert codes == set(CODES_SYSTEMES)
    assert len(CODES_SYSTEMES) == len(set(CODES_SYSTEMES))


def test_la_repartition_est_le_total_moins_ce_qui_n_en_releve_pas(
        depenses: DepensesRetraite):
    derniere = depenses.derniere_annee
    hors = sum(depenses.depense_systeme(s.code, derniere)
               for s in SYSTEMES if not s.repartition)
    assert depenses.repartition(derniere) + hors == pytest.approx(
        depenses.depense(derniere), abs=0.1 * len(SYSTEMES))
    # La répartition obligatoire pèse l'essentiel du risque, mais pas tout.
    part = depenses.repartition(derniere) / depenses.depense(derniere)
    assert 0.90 < part < 0.97


def test_la_depense_rapportee_au_pib_a_triple(depenses: DepensesRetraite):
    """Ordre de grandeur, pas prédiction : 5 % du PIB en 1959, 14 à 15 % depuis."""
    assert 0.04 < depenses.part_pib(1959) < 0.07
    assert 0.13 < depenses.part_pib(depenses.derniere_annee) < 0.16


def test_la_depense_est_certifiee(depenses: DepensesRetraite):
    for annee in depenses.annees():
        assert depenses.fiabilite(annee) == Fiabilite.CERTIFIEE, annee


# -- l'agrégation ------------------------------------------------------------


def test_les_generations_couvrent_la_fenetre():
    """Assez de générations pour que la moyenne pondérée ait un sens, et
    toutes celles dont une cohorte part avant l'horizon : le militaire, le
    départ le plus précoce, part l'année de ses 48 ans. La génération 2020,
    dont les militaires nés de 2018 à 2022 partent de 2066 à 2070, en est ; la
    suivante, dont le premier partirait en 2071, non. La grille s'arrêtait à
    2015, pour un départ au plus tôt à 52 ans (action 138, étape 3)."""
    liste = generations()
    assert liste[0] == PREMIERE_GENERATION
    assert liste[-1] <= DERNIERE_GENERATION
    assert len(liste) >= 15
    plus_tot = 48
    assert liste[-1] - PAS_GENERATIONS // 2 + plus_tot <= HORIZON
    assert liste[-1] + PAS_GENERATIONS - PAS_GENERATIONS // 2 + plus_tot > HORIZON


def test_le_cout_du_systeme_actuel_est_la_depense_observee(cout):
    """L'étalon n'est pas corrigé : son rapport vaut un, année après année, et
    son coût est la dépense de pensions observée."""
    for ligne in cout.annees:
        assert ligne.rapports["actuel"] == 1.0
        assert ligne.cout("actuel") == ligne.pensions
    assert cout.cumul("actuel") == pytest.approx(
        sum(ligne.pensions * ligne.coefficient_constants for ligne in cout.annees))


def test_le_rapport_ne_touche_que_les_pensions_de_repartition(cout, depenses):
    """L'aide à l'autonomie, la retraite supplémentaire et le minimum vieillesse
    sont dans le risque vieillesse-survie, et ne sont la pension d'aucun système.
    Le rapport de masses ne les multiplie donc pas : la base de tous les
    systèmes est la répartition obligatoire, lue sur la ventilation, et sa part
    de 1990 avant que la ventilation commence. Jusqu'au 23 septembre 2026, le
    rapport multipliait le total, et les économies du passé en étaient grossies
    de près d'un dixième."""
    premiere = depenses.premiere_annee_ventilee
    part_premiere = depenses.repartition(premiere) / depenses.depense(premiere)
    for ligne in cout.annees:
        if ligne.annee >= premiere:
            assert ligne.pensions == pytest.approx(depenses.repartition(ligne.annee))
        else:
            assert ligne.part_repartition == pytest.approx(part_premiere)
        assert 0.85 < ligne.part_repartition < 0.95, ligne.annee
        # Ce qui n'est pas une pension reste hors du compte : le coût d'un
        # système est la base, droits directs multipliés, et rien d'autre.
        assert ligne.cout("notionnel_retroactif") == pytest.approx(
            ligne.pensions * (1.0 - ligne.part_derives)
            * ligne.rapports["notionnel_retroactif"])
    # L'économie du passé est une économie de pensions : elle ne dépasse pas
    # les pensions observées, et elle est plus petite que si le rapport
    # multipliait le total.
    economie = cout.cumul("actuel") - cout.cumul("notionnel_retroactif")
    sur_le_total = sum(
        (ligne.observee - masse_du_scenario(
            ligne.observee, ligne.part_derives, ligne.rapports["notionnel_retroactif"],
            "notionnel_retroactif", ligne.reversion_servie, ligne.reforme_en_vigueur))
        * ligne.coefficient_constants for ligne in cout.annees)
    assert 0.0 < economie < cout.cumul("actuel")
    assert 0.05 < 1.0 - economie / sur_le_total < 0.15


def test_une_reforme_prospective_ne_deplace_rien_avant_sa_bascule(cout):
    """Les droits acquis sont conservés : aucune pension liquidée avant la
    bascule n'est modifiée, donc aucun euro n'est économisé sur le passé."""
    assert cout.derniere_annee < Parametres().annee_bascule
    assert set(cout.confondus_avec_actuel()) == {
        "notionnel_prospectif", "notionnel_prospectif_employeur",
    }
    for scenario in cout.confondus_avec_actuel():
        assert cout.cumul(scenario) == cout.cumul("actuel")


def test_la_part_patronale_coute_toujours_plus_que_la_seule_part_salariale(cout):
    """Le scénario 4 est le scénario 2 plus la cotisation de l'employeur : il ne
    peut pas coûter moins, aucune année."""
    for ligne in cout.annees:
        assert (ligne.rapports["notionnel_retroactif_employeur"]
                >= ligne.rapports["notionnel_retroactif"]), ligne.annee


def test_le_notionnel_retroactif_coute_moins_que_le_systeme_actuel(cout):
    """Résultat attendu du modèle, et non hypothèse : la part salariale seule,
    revalorisée sur la masse salariale, ne reconstitue pas les pensions servies."""
    for ligne in cout.annees:
        assert 0.0 < ligne.rapports["notionnel_retroactif"] < 1.0, ligne.annee
    assert cout.cumul("notionnel_retroactif") < cout.cumul("actuel")


def test_le_contrefactuel_ne_se_donne_jamais_pour_certifie(cout):
    """La dépense est certifiée, ce qu'on en tire ne l'est pas et ne peut
    pas l'être : aucune institution ne publie le coût d'un système qui n'a pas
    existé."""
    assert cout.fiabilite == Fiabilite.ESTIMEE


def test_les_cumuls_sont_en_euros_constants(cout):
    """Un cumul en euros courants additionnerait des unités incomparables. Le
    contrôle : le cumul dépasse largement la somme des montants nominaux, parce
    que les euros anciens valent plus que les euros récents."""
    nominal = sum(ligne.observee for ligne in cout.annees)
    assert cout.cumul_observe() > nominal * 1.5


def test_chaque_scenario_a_une_courbe_et_un_libelle(cout):
    codes = {scenario for scenario, _ in SCENARIOS} | {COMPOSANTE_GARANTIE}
    for ligne in cout.annees:
        assert set(ligne.rapports) == codes
    assert len(SCENARIOS) == 6


def test_la_garantie_vieillesse_est_comptee_dans_le_6_et_redite_a_part(cout, avenir):
    """La part que l'impôt finance est une composante du scénario 6, jamais plus
    grosse que lui, et jamais négative.

    Elle n'est plus bornée par le scénario, et c'est la nature d'une allocation
    différentielle : sur une pension minuscule, ce qui manque pour atteindre un
    plancher dépasse ce qui est servi. Les premières années de la fenêtre, où
    les comptes notionnels rétroactifs ne rendent presque rien, le montrent
    sans détour — le rapport y passe au-dessus de un. Ce qui reste vrai partout
    est qu'elle n'est jamais négative, et qu'elle DÉCROÎT sur la projection, à
    mesure que les pensions montent face à un plancher indexé sur les prix.

    Elle n'est plus nulle non plus. Depuis que la garantie est servie à 65 ans
    à qui a liquidé plus tôt, la trajectoire en porte une : c'était zéro de
    2030 à 2070, ce qui était le chiffre le plus faux de la page.
    """
    for ligne in cout.annees + avenir.annees:
        assert ligne.rapports[COMPOSANTE_GARANTIE] >= 0.0, ligne.annee
    assert cout.cumul(COMPOSANTE_GARANTIE) > 0.0
    projetees = avenir.projetees()
    assert all(ligne.rapports[COMPOSANTE_GARANTIE] > 0.0 for ligne in projetees)
    # Décroissante sur la projection : la dernière décennie sous la première,
    # et l'horizon sous l'entrée. Le test exigeait auparavant que l'horizon
    # tombe sous la MOITIÉ de l'entrée — un instantané du modèle, pas une
    # propriété : la correction des lois de mortalité projetées l'a posé à
    # 50,4 % sans que le mécanisme décrit ci-dessus ait changé de sens.
    garantie = [ligne.rapports[COMPOSANTE_GARANTIE] for ligne in projetees]
    assert sum(garantie[-10:]) < sum(garantie[:10])
    assert garantie[-1] < garantie[0]


# -- la pyramide des âges ----------------------------------------------------


def test_la_pyramide_couvre_le_passe_et_l_avenir(population: Population):
    assert population.premiere_annee == 1962
    assert population.derniere_annee == HORIZON
    assert population.age_maximal == 104


def test_la_pyramide_est_observee_puis_projetee(population: Population):
    """L'INSEE date lui-même la frontière : estimations jusqu'en 2023."""
    assert population.fiabilite(2023) == Fiabilite.CERTIFIEE
    assert population.fiabilite(2024) == Fiabilite.ESTIMEE
    assert population.fiabilite(HORIZON) == Fiabilite.ESTIMEE
    # Hors de la plage publiée, la valeur est empruntée : elle ne peut pas
    # valoir mieux qu'estimée.
    assert population.fiabilite(1959) == Fiabilite.ESTIMEE


def test_la_pyramide_dit_le_vieillissement(population: Population):
    """Contrôle de vraisemblance, pas prédiction : le nombre de personnes de
    65 ans et plus augmente de moitié d'ici l'horizon, la population d'âge
    actif recule."""
    vieux_2024 = population.effectif_tranche(65, population.age_maximal, 2024)
    vieux_horizon = population.effectif_tranche(65, population.age_maximal, HORIZON)
    assert 1.3 < vieux_horizon / vieux_2024 < 1.6
    assert population.actifs(HORIZON) < population.actifs(2024)


def test_les_effectifs_hors_plage_sont_nuls(population: Population):
    assert population.effectif(47, 2024) == 0.0
    assert population.effectif(200, 2024) == 0.0


def test_le_militaire_sert_sa_pension_des_l_annee_de_ses_48_ans(population: Population):
    """Radié à 48 ans et demi (action 152), le militaire de la grille part
    l'année de ses 48 ans, à chaque génération. Ses têtes comptent dès cette
    année-là et la suivante, au système actuel comme dans son régime : les
    personnes de 48 et de 49 ans au 1er janvier, que l'INSEE publie, 830 132 et
    871 081 en 2024. La pyramide commençait à 50 ans, et les lui retirait
    (action 138, étape 3)."""
    from retraite_notionnelle.cout import (
        CLES_CAS_TYPES, TETES_TOUTES, Pensionne, VoletLiberal, _masses, _masses_regimes)

    simulateur = Simulateur(Parametres()).pour_la_projection()
    revalorisation = RevalorisationServie(simulateur, 2000, 2030)
    volet = VoletLiberal(annee_liquidation=2040, annee_ouverture_garantie=2040,
                         pension=1.0, ressources_garantie=1.0)
    # La génération 1974 de la grille : ses cinq cohortes, nées de 1972 à 1976,
    # partent de 2020 à 2024, et ont de 52 à 48 ans en 2024.
    militaire = Pensionne(code="militaire", generation=1974, annee_liquidation=2022,
                          pensions={cle: 1.0 for cle in CLES_CAS_TYPES}, propre=volet,
                          parts_regimes={"fonction_publique_etat": 1.0})
    attendu = 830132 + 871081 + population.effectif_tranche(50, 52, 2024)
    _, _, tetes = _masses([militaire], population, 2024, {"militaire": 1.0}, revalorisation)
    assert tetes[TETES_TOUTES] == pytest.approx(attendu, rel=1e-12)
    _, par_regime = _masses_regimes([militaire], population, 2024, {"militaire": 1.0},
                                    revalorisation)
    assert par_regime["fonction_publique_etat"] == pytest.approx(attendu, rel=1e-12)


def test_la_recette_ne_compte_ses_cotisants_qu_a_partir_de_50_ans(population: Population):
    """La recette pèse ses cotisants par la même pyramide, qui commence à 48 ans
    pour le militaire : elle ne compte toujours aucun cotisant de moins de 50
    ans, ni à son compte ni à son pilier. Ce biais, qui fausse le facteur
    d'assiette du scénario 6, est au propriétaire (action 138, étape 19,
    « Trouvé en chemin » de la note du 14 octobre) : le militaire ne le déplace
    pas."""
    from retraite_notionnelle.cout import (
        ASSIETTE_ACTUELLE, CLES_ASSIETTES, CLES_CAS_TYPES, CLES_RECETTES, TAUX_REELS,
        Pensionne, VoletLiberal, _masses_cotisations, _masses_pilier)

    annees = range(2015, 2031)
    volet = VoletLiberal(annee_liquidation=2040, annee_ouverture_garantie=2040,
                         pension=1.0, ressources_garantie=1.0,
                         cotisations={annee: 1.0 for annee in annees},
                         assiette={annee: 1.0 for annee in annees},
                         pilier={annee: (1.0, 0.0, 0.0, 1.0) for annee in annees})
    # La génération 1976 de la grille : en 2024, ses cinq cohortes ont de 50 à
    # 46 ans, et cotisent toutes.
    cotisant = Pensionne(code="x", generation=1976, annee_liquidation=2040,
                         pensions={cle: 1.0 for cle in CLES_CAS_TYPES}, propre=volet,
                         cotisations={cle: {annee: 1.0 for annee in annees}
                                      for cle in (TAUX_REELS, ASSIETTE_ACTUELLE)})
    cinquante_ans = population.effectif(50, 2024)
    masses = _masses_cotisations([cotisant], population, 2024, {"x": 1.0})
    for cle in CLES_RECETTES + CLES_ASSIETTES:
        assert masses[cle] == pytest.approx(cinquante_ans, rel=1e-12), cle
    pilier = _masses_pilier([cotisant], population, 2024, {"x": 1.0}, {"x": 1.0})
    assert pilier["versements"] == pytest.approx(cinquante_ans, rel=1e-12)
    assert pilier["encours"] == pytest.approx(cinquante_ans, rel=1e-12)


def test_la_pyramide_emprunte_avant_1962_et_refuse_apres_l_horizon(
        population: Population):
    """La borne basse emprunte, la haute REFUSE, et l'asymétrie est le sujet.

    EN DEÇÀ, la dépense observée commence trois ans avant la pyramide, et ces
    trois années empruntent celle de 1962 : une approximation assumée, sur des
    années dont la dépense pèse un demi pour cent de celle d'aujourd'hui.

    AU-DELÀ, emprunter changerait de COHORTE. La pyramide s'indexe par âge :
    rendre l'effectif des 85 ans de 2070 sous le nom des 85 ans de 2085, c'est
    rendre des gens nés quinze ans plus tôt, et morts. Reconduire la valeur de
    bord d'une série annuelle ne change qu'un niveau ; reconduire un âge change
    de population.

    CE QUI REND LE REFUS NÉCESSAIRE, c'est que le chiffre emprunté est
    PLAUSIBLE. Le 20 septembre 2026, il a fait tomber l'engagement acquis du
    dépôt de 579 à 478 % du PIB, et rien ne l'a signalé sinon une incohérence
    interne du calcul. Une cohorte déjà née se prolonge par sa propre survie,
    et ``cout._courbes_survie`` fait ce geste-là.
    """
    assert population.effectif(80, 1959) == population.effectif(80, 1962)
    assert population.effectif_tranche(65, 80, 1959) == pytest.approx(
        population.effectif_tranche(65, 80, 1962))
    assert population.effectif(80, HORIZON) > 0.0

    with pytest.raises(ValueError, match="au-delà"):
        population.effectif(85, HORIZON + 15)
    # La tranche refuse aussi, et pour la même raison : elle lit la même
    # pyramide. Une tranche VIDE refuse également, sans quoi l'année passerait
    # sans être regardée.
    with pytest.raises(ValueError, match="au-delà"):
        population.effectif_tranche(65, 80, HORIZON + 1)
    with pytest.raises(ValueError, match="au-delà"):
        population.effectif_tranche(80, 65, HORIZON + 1)


# -- la trajectoire projetée -------------------------------------------------


def test_l_avenir_va_de_la_ventilation_a_l_horizon(avenir, depenses):
    assert avenir.premiere_annee == depenses.premiere_annee_ventilee
    assert avenir.derniere_annee == HORIZON
    assert avenir.premiere_annee_projetee == depenses.derniere_annee + 1


def test_la_jonction_ne_saute_pas(avenir, depenses):
    """L'ancrage est fait pour ça : la dernière année publiée et la première
    année projetée doivent se suivre, non se succéder par un ressaut.

    Le contrôle porte sur la dernière année OBSERVÉE, dont le coût doit être
    exactement la dépense de répartition publiée, puis sur l'écart relatif à
    l'année suivante, qui ne peut pas dépasser ce qu'une année de démographie
    déplace.
    """
    derniere = depenses.derniere_annee
    observee = avenir.annee(derniere)
    assert not observee.projete
    assert observee.cout("actuel") == pytest.approx(
        depenses.repartition(derniere), rel=1e-9)

    premiere = avenir.annee(derniere + 1)
    assert premiere.projete
    saut = premiere.cout_constants("actuel") / observee.cout_constants("actuel") - 1
    assert abs(saut) < 0.05, f"ressaut de {saut:.1%} à la jonction"


def test_les_scenarios_prospectifs_se_detachent_apres_la_bascule(avenir):
    """C'est tout l'objet de la projection : avant la bascule les droits acquis
    sont conservés et presque rien ne bouge ; après, l'écart se creuse.

    « Presque » et non « rien » : la grille échantillonne une génération sur
    cinq, et chacune en représente cinq, décalées d'un an à deux ans. Une
    cohorte qui liquide juste avant la bascule est donc représentée par une
    génération qui, elle, liquide juste après, et hérite de son traitement. Le
    résidu se mesure — moins d'un demi pour cent — et il est le prix du pas de
    la grille, qui commande le temps de calcul de la page.
    """
    bascule = avenir.annee_bascule
    for ligne in avenir.annees:
        if ligne.annee < bascule:
            assert ligne.rapports["notionnel_prospectif"] == pytest.approx(
                1.0, abs=0.005), ligne.annee
    fin = avenir.annee(avenir.derniere_annee)
    assert fin.rapports["notionnel_prospectif"] < 0.7


def test_l_ecart_des_scenarios_prospectifs_se_creuse_sans_retour(avenir):
    """Une réforme prospective ne revient pas en arrière — passé son premier pas.

    Chaque année supplémentaire remplace des pensions anciennes par des
    pensions nouvelles, plus basses, et l'écart au système actuel se creuse
    sans se refermer. C'était vrai dès la bascule tant que les pensions servies
    restaient figées en euros constants ; ça ne l'est plus dès la première
    année, parce que la réforme fait DEUX choses le même jour : elle ferme
    l'ancien barème aux nouveaux liquidants, et elle fait passer TOUT LE STOCK
    des pensions en cours à l'indexation sur la masse salariale, plus
    généreuse que les prix du système actuel. La seconde joue à la hausse et se
    voit tout de suite ; la première joue à la baisse et met une génération à
    peser. Le rapport monte donc d'abord — jusqu'à dépasser 1 pour le
    scénario 5, qui porte le plus de droits — avant de tomber.

    CE PREMIER TEMPS DURAIT CINQ ANS — le pas de la grille de générations —
    tant que les droits acquis se convertissaient au diviseur de 67 ans. Il en
    dure jusqu'à DIX depuis deux corrections qui vont dans le même sens.
    L'âge de référence fixé à 64 ans à partir de la bascule fait prendre à la
    conversion un diviseur plus élevé, donc un capital d'ouverture plus gros,
    et ce cadeau va tout entier aux générations de transition — celles-là mêmes
    qui liquident pendant le premier temps. Le profil salarial lu chez l'INSEE
    y ajoute sa part : moins pentu d'un tiers, il relève le salaire des
    premières années de carrière, donc les droits des cohortes qui basculent
    en cours de route. Le scénario 5, qui porte en plus la part patronale,
    reçoit les deux et culminait à 3,4 % au-dessus du système actuel en 2036 ;
    le 3 culminait à 1,6 % en 2031. Passé le sommet, la décroissance est stricte
    jusqu'à l'horizon, et c'est elle que ce test garde.

    DEPUIS LE 20 SEPTEMBRE 2026, L'EMPLOI PROJETÉ SUIT LE COR, et le sommet a
    monté et reculé : la masse salariale, sur laquelle le stock est indexé,
    croît d'un demi-point de plus par an jusqu'en 2040, le temps que le
    chômage tombe à 7 % et que la population active atteigne son maximum. Le
    scénario 5 culminait à 7,5 % au-dessus du système actuel en 2039, le 3 à
    4,9 % en 2034 ; à emploi constant, les anciens sommets se retrouvaient. Le
    recul de l'emploi après 2040 fait ensuite tomber le rapport plus bas
    qu'avant : 0,78 en 2070 pour le 5 contre 0,84 à emploi constant.

    ET LE MÊME JOUR, LE STOCK A CESSÉ D'ÊTRE RÉINDEXÉ : par défaut, les
    pensions déjà servies à la bascule gardent les prix que le droit leur
    promet (``revalorisation_stock=PRIX``), et la bosse n'est plus qu'un
    souvenir — le 5 culmine à 1,1 % en 2039, le 3 ne dépasse plus jamais le
    système actuel. La variante ``REINDEXE`` la fait revenir, et le test
    d'après tient les deux.

    Le sommet est donc CHERCHÉ et non supposé : fixer son année d'avance
    ferait passer le test pour un contrôle alors qu'il ne serait qu'un
    enregistrement.
    """
    for scenario in ("notionnel_prospectif", "notionnel_prospectif_employeur"):
        lignes = [l for l in avenir.annees if l.annee >= avenir.annee_bascule]
        # Le sursaut initial existe, et il reste petit : la réforme ne coûte
        # pas plus de dix pour cent de plus que le système qu'elle remplace.
        sommet = max(lignes, key=lambda l: l.rapports[scenario])
        assert sommet.rapports[scenario] < 1.10, scenario
        # Et il est borné dans le temps : au plus trois pas de grille — la
        # bosse d'emploi du COR s'achève en 2040, et le sommet avec elle.
        assert sommet.annee <= avenir.annee_bascule + 3 * PAS_GENERATIONS, scenario
        # La décroissance se lit d'un PAS DE GRILLE à l'autre, et non d'une
        # année à l'autre : la grille échantillonne une génération sur cinq,
        # et la courbe ondule d'un ou deux dixièmes de point à l'intérieur du
        # pas — un autre test le borne. Comparer chaque année à celle d'un
        # pas plus tôt efface l'ondulation et garde la pente.
        #
        # Depuis que l'âge de référence est à 65 ans, le sursaut du scénario 5
        # a disparu : son sommet est la bascule elle-même, et la bosse d'emploi
        # n'y laisse qu'un plateau de deux millièmes jusqu'en 2035. La pente se
        # lit donc au-delà de la bosse, et non d'un pas après le sommet.
        par_annee = {l.annee: l.rapports[scenario] for l in lignes}
        fin_de_bosse = max(sommet.annee + PAS_GENERATIONS,
                           avenir.annee_bascule + 3 * PAS_GENERATIONS)
        for ligne in lignes:
            if ligne.annee < fin_de_bosse:
                continue
            assert ligne.rapports[scenario] <= (
                par_annee[ligne.annee - PAS_GENERATIONS] + 1e-12
            ), (scenario, ligne.annee)
        assert lignes[-1].rapports[scenario] < 0.85, scenario


def test_le_stock_sur_les_prix_efface_la_bosse_sans_toucher_l_horizon(avenir):
    """Réindexer le stock à la bascule creuse une bosse jusque vers 2040 et rien
    d'autre.

    Sous ``REINDEXE``, les pensions servies avant la bascule passent à la masse
    salariale le jour où la réforme s'applique, et le rapport des prospectifs
    au système actuel monte au-dessus de celui du défaut jusqu'à ce que ce
    stock s'éteigne. À l'horizon, les deux réglages se rejoignent au millième :
    tout ce qui reste vient des comptes, pas du stock. Avant la bascule, les
    prospectifs sont le système actuel dans les deux cas.
    """
    reindexe = memoire.cout(
        Parametres(revalorisation_stock=RevalorisationStock.REINDEXE),
        assiette=False, convention_recette=CONVENTION_RAPPORT,
    ).avenir
    defaut = {l.annee: l for l in avenir.annees}
    bascule = avenir.annee_bascule
    for ligne in reindexe.annees:
        for scenario in CLES_PROSPECTIVES:
            if ligne.annee < bascule:
                # La règle du stock ne peut rien AVANT la bascule : les deux
                # réglages y sont identiques, au pas de grille près, qu'un
                # autre test borne.
                assert ligne.rapports[scenario] == pytest.approx(
                    defaut[ligne.annee].rapports[scenario])
            elif bascule < ligne.annee <= bascule + 10:
                assert ligne.rapports[scenario] > defaut[ligne.annee].rapports[scenario], (
                    scenario, ligne.annee)
    for scenario in CLES_PROSPECTIVES:
        assert reindexe.annees[-1].rapports[scenario] == pytest.approx(
            defaut[reindexe.annees[-1].annee].rapports[scenario], abs=1e-3)
    # Et la bosse elle-même : sous le défaut, le scénario 3 ne dépasse plus le
    # système actuel, quand la variante le lui fait dépasser de 3,7 % — 4,9 %
    # tant que l'âge de référence était à 64 ans, dont le capital d'ouverture
    # était plus gros.
    assert max(l.rapports["notionnel_prospectif"]
               for l in avenir.annees if l.annee >= bascule) < 1.0
    assert max(l.rapports["notionnel_prospectif"]
               for l in reindexe.annees if l.annee >= bascule) > 1.03


def test_la_part_du_pib_reste_dans_un_ordre_de_grandeur_plausible(avenir, comptes):
    """Contrôle de vraisemblance externe, et l'écart qu'il mesure aujourd'hui.

    *Mis à jour le 23 septembre 2026.* Le COR projette, dans son rapport de juin
    2026 que le dépôt lit, 13,9 % du PIB en 2024 et 15,3 % en 2070 pour le
    système actuel ; le dépôt trouve 18,3 % en 2070, trois points de plus. La
    fourchette de 10 à 20 % ci-dessous est un garde-fou de méthode, et elle a
    suivi le modèle une fois — sa borne haute était de 18 % avant le
    14 septembre 2026 ; c'est pourquoi l'ÉCART AU COR, lu dans son compte et
    non écrit ici, est tenu à part, sous le seuil que la page Coût et
    ``limites.md`` § 5 ter commentent.

    Ce qui suit est l'histoire de cet écart, à sa date. Le COR projetait 13,9 %
    en 2024 et 14,2 % en 2070 dans son rapport de juin 2025. Le dépôt trouvait
    13,6 % au départ et 19,3 % à l'arrivée : cinq points d'écart, contre quatre avant que chaque cas
    type ne liquide à l'âge de SA génération, et deux avant que les cas types ne
    soient pondérés par les effectifs de retraités de leur caisse.

    **L'écart s'est creusé en corrigeant un défaut, et c'est le résultat de
    l'action 8, non son échec.** La feuille de route tenait l'âge de liquidation
    écrit dans la grille pour la principale cause de cet écart : un cas type
    liquidait à 64 ans quelle que soit sa génération, si bien que le stock de
    retraités du modèle suivait la population des 64 ans et plus, laquelle croît
    de 41 % d'ici 2070 quand celle des 52 ans et plus n'en gagne que 25. Le
    diagnostic était juste sur le défaut et faux sur son SENS : en faisant
    liquider chaque génération sous son propre droit, la trajectoire 2070 monte
    de 18,3 à 19,3 % au lieu de redescendre vers 14,2.

    Ce que la mesure apprend, et que `docs/limites.md` §5 ter développe : ce qui
    sépare le dépôt du COR n'est pas l'âge de départ. Les générations d'après
    1970 liquidaient déjà, dans l'ancienne grille, à peu près à l'âge que le
    droit leur ouvre ; la correction a surtout déplacé les anciennes, et ce sont
    les récentes qui font 2070. L'écart restant tient à ce que le modèle ne
    porte pas : le recul du taux de remplacement que le COR projette, produit
    d'une indexation des pensions sur les prix quand les salaires montent plus
    vite.

    UN POINT DE CET ÉCART ÉTAIT UN EFFET DE DÉNOMINATEUR, mesuré le 20 septembre
    2026 : la page rapportait sa dépense à un PIB qu'elle se fabriquait — le
    rythme du COR corrigé par la population des 20-64 ans, qui recule de 10 %
    quand l'emploi projeté par le COR recule de 6 %. Elle lit maintenant le même
    PIB que l'indexation des comptes, et la trajectoire 2070 passe de 19,4 à
    18,35 % sans qu'une seule pension ait bougé.

    La fourchette reste un garde-fou : elle ne dit pas que la trajectoire est
    juste, elle dit qu'une trajectoire qui en sortirait relèverait d'une erreur
    de méthode et non d'un désaccord d'hypothèses. Elle n'a pas bougé — la
    borne haute de 20 % tient de 1,65 point.

    *Le 5 octobre 2026*, la trajectoire que la page affiche est devenue celle
    du COR (``test_la_trajectoire_du_systeme_actuel_est_celle_du_cor``), et ce
    test tient désormais celle que le modèle se donne lui-même
    (``base_modele``) : c'est elle que l'écart mesure, et elle seule qui
    puisse dériver.
    """
    for ligne in avenir.annees:
        part = ligne.part_pib("actuel")
        assert 0.10 < part < 0.20, f"{ligne.annee} : {part:.1%}"
    # La trajectoire propre du modèle sur les années projetées ; sur les années
    # publiées, c'est la reconstitution qui la tient, sous son cliquet.
    for ligne in avenir.projetees():
        propre = ligne.base_modele / ligne.coefficient_constants / ligne.pib
        assert 0.10 < propre < 0.20, f"{ligne.annee} : {propre:.1%}"
    # L'écart au COR à l'horizon, lu dans son compte : deux points et demi
    # jusqu'à l'étape 8 de l'action 147, moins d'un jusqu'à l'étape 10, et
    # 0,4 point SOUS le COR depuis l'étape 11, qui compte les arrivées
    # tardives : la base du modèle part d'un demi-point sous lui (la dépense de
    # la DREES, sans gestion ni minimum vieillesse) et croît désormais comme
    # lui. Une dérive au-delà de trois et demi relèverait d'une erreur de
    # méthode plutôt que d'un désaccord d'hypothèses.
    horizon = avenir.annees[-1]
    propre = horizon.base_modele / horizon.coefficient_constants / horizon.pib
    ecart = propre - comptes.depense(horizon.annee)
    assert -0.01 < ecart < 0.035, f"{horizon.annee} : écart au COR {ecart:.2%}"


def test_la_trajectoire_du_systeme_actuel_est_celle_du_cor(avenir, comptes):
    """Au-delà de la dernière année publiée, le système actuel coûte ce que le
    COR projette, à la part de PIB près — et donc au chiffre de son rapport.

    Décision du 5 octobre 2026 (action 147) : la page portait deux dépenses pour
    le même système, celle du COR dans les cartes du haut et celle que le modèle
    se donne dans le dépliant des quatre systèmes, 17,8 % du PIB en 2070 contre
    15,3. Le lecteur qui refaisait le calcul ne retrouvait pas le chiffre
    officiel. La trajectoire prend désormais la dépense du COR, et les autres
    systèmes en tirent la leur par le rapport de masses, comme le bilan.
    """
    projetees = avenir.projetees()
    assert projetees
    for ligne in projetees:
        assert ligne.part_pib("actuel") == pytest.approx(
            comptes.depense(ligne.annee), rel=1e-12), ligne.annee
        # Le rapport s'applique à cette dépense-là, part dérivée à part.
        assert ligne.cout_constants("notionnel_liberal") == pytest.approx(
            ligne.base * (1.0 - ligne.part_derives) * ligne.rapports["notionnel_liberal"],
            rel=1e-12), ligne.annee


#: Première année que la reconstitution du passé contrôle. Les années 1990,
#: que la DREES ventile aussi, s'écartent davantage encore (-24,5 % en 1990) :
#: le cliquet ne les tient pas.
RECONSTITUTION_DEPUIS = 2000
#: Le pire écart admis, depuis 2000, entre la base du modèle et la dépense
#: observée. Un cliquet, qui ne doit que descendre : -19,2 % en 2009, le
#: 5 octobre 2026 ; -19,8 % le même jour, l'étape 138.16 ayant corrigé un
#: défaut qui en compensait un autre (voir le test) ; -17,1 % le même jour,
#: l'étape 8 de l'action 147 ayant corrigé la comptabilité de la base ;
#: -14,3 % le même jour, l'étape 10 comptant l'Agirc-Arrco au taux moyen des
#: entreprises ; -16,1 % le 6 octobre, l'étape 14 pesant chaque génération de
#: sa durée validée : les carrières plus courtes des femmes nées avant 1945
#: abaissent le passé, que d'autres défauts tenaient déjà trop bas ; -16,6 %
#: le 11 octobre, l'action 136 retirant de la grille de la page le minimum
#: vieillesse des premiers non-salariés, que la dépense observée ne compte pas
#: — un défaut qui en compensait un autre (voir le test) ; -13,9 % le
#: 14 octobre, l'étape 19 servant au scénario 1 les revalorisations que son
#: droit a servies, et non les prix ; -14,1 % le même jour, l'étape 138.18
#: servant en points, et non plus en annuités, les années d'avant 1973 des
#: artisans et des commerçants : sous le plafond, l'équivalence de D. 634-8
#: leur ouvre moins que la classe minimale des commerçants (voir la fiche
#: ``points_avant_1973_independants``), et les premières générations baissent ;
#: -13,1 % le 17 octobre (-13,2 % la veille), l'étape 138.7 faisant vivre
#: chaque cas type au rythme du vingtile de son diviseur, à nombre de décès
#: égal : les plus fortes pensions pèsent davantage aux grands âges ; -11,9 %
#: le 18 octobre, l'étape 138.3 faisant partir chaque cohorte de la grille
#: l'année que le droit de sa génération lui donne : la masse de 2024 que
#: l'ancrage rend égale à la dépense ne compte plus les cohortes que la grille
#: faisait partir trop tôt, et le passé se refait d'autant mieux ; -11,0 % le
#: 19 octobre, l'étape 138.7 donnant aux inaptes de la Cnav leur part de la
#: caisse, et -10,7 % le même jour, aux ex-invalides la leur ; -11,0 % le
#: 24 octobre (-10,6 % la veille), l'étape 138.3 divisant chaque caisse par
#: les têtes de ses cas types — un défaut qui en compensait un autre (voir le
#: test).
RECONSTITUTION_CLIQUET = 0.115
#: Ce que vise le cliquet : quelques pour cent, chaque année.
RECONSTITUTION_CIBLE = 0.05


def test_la_projection_refait_le_passe(avenir, depenses):
    """La mécanique qui projette le système actuel doit savoir refaire le passé.

    Au-delà de la dernière année publiée, le coût du système actuel est la
    masse de pensions des cas types, multipliée par l'ancrage qui la rend égale
    à la dépense observée cette année-là. La même formule, appliquée aux années
    publiées, devrait retrouver ce qui a été dépensé
    (:meth:`Avenir.reconstitution`) : c'est le seul contrôle que la
    trajectoire puisse recevoir de faits, et non d'une autre projection.

    *Le 5 octobre 2026*, elle ne les retrouve pas : la base du modèle vaut
    81,5 % de la dépense observée en 2000, 80 % en 2009, 95 % en 2020, et
    72,6 % en 1990. La masse du modèle croît plus vite que la dépense réelle, et
    l'ancrage reporte cette dérive sur l'avenir : c'est le symptôme le plus
    direct de l'écart au COR en 2070, que
    ``test_la_part_du_pib_reste_dans_un_ordre_de_grandeur_plausible`` tient à
    part. L'ancrage suppose deux choses sans les vérifier : que l'écart du
    modèle au réel est le même pour toutes les générations, et que la part de
    la réversion reste celle de l'année d'ancrage.

    Le seuil est donc un CLIQUET, qui ne doit que descendre jusqu'à la cible
    de quelques pour cent. Un écart qui le dépasse est une régression de la
    projection, ou la correction d'un défaut qui en compensait un autre : le
    dire ici avant de toucher au chiffre. Un écart qui passe d'un point sous
    lui demande de l'abaisser.

    *Le même jour*, l'étape 138.16 le relève de -19,2 % à -19,8 % en 2009,
    et c'est le second cas. Elle sert à chaque liquidation la colonne de
    revalorisation en vigueur à sa date, et non plus le rapport de deux
    valeurs de la colonne de 2017, qui ajoutait aux départs d'avant 1993 une
    revalorisation de janvier que la caisse ne leur servait pas, de 4 à 16 %.
    Les pensions anciennes du modèle baissent, sa masse de 2009 avec elles,
    et l'ancrage de 2024 n'en reporte que mieux la dérive : neutralisée
    seule, la colonne rend 0,54 point des 0,62, les autres causes de
    l'étape le reste. Le défaut corrigé masquait une part de celui que ce
    test mesure.

    *Le même jour*, l'étape 8 de l'action 147 le ramène à -17,1 % en 2009
    (-14,9 % en 2000, -4,4 % en 2020, -23,1 % en 1990) : la base porte la
    réversion à la part de chaque année, et les poids des cas types sont
    calés sur la dépense de chaque groupe du COR.

    *Le même jour*, l'étape 10 le ramène à -14,3 % en 2009 (-11,5 % en 2000,
    -3,3 % en 2020, -20,0 % en 1990) : l'Agirc-Arrco compte ses points au taux
    moyen des entreprises, et non au minimum de l'accord, plus haut d'un tiers
    avant 1999 ; les pensions des générations anciennes remontent, et la
    masse du passé avec elles.

    *Le 11 octobre 2026*, l'action 136 le relève de -16,4 % à -16,6 % en 2009
    (-15,3 % en 2000, -25,4 % en 1990), et c'est encore le second cas : la
    grille de la page ne sert plus le minimum vieillesse, que la dépense
    observée ne compte pas, aux non-salariés des premières générations. Il
    grossissait la masse des plus vieilles cohortes, et masquait d'autant la
    dérive que ce test mesure.

    *Le 24 octobre 2026*, l'étape 138.3 le relève de -10,6 % à -11,0 % en
    2009, et c'est encore le second cas : chaque caisse se divise par les
    têtes de ses cas types. Pesés de la part de leur caisse dans le stock,
    appliquée à chaque génération, le militaire, l'agent de conduite, celui
    des IEG comptaient d'autant plus d'années de retraite qu'ils partent tôt
    — le militaire 3,4 % des retraités de la grille en 2010 et 2,9 % en 2024,
    pour 1,9 et 1,6 % à sa caisse —, et une part qui reculait de 2009 à 2024
    freinait d'autant la croissance des têtes du modèle : en 2009, leur écart
    passe de -5,0 à -5,5 %, celui de la pension par tête reste à -5,8 %.
    """
    reconstitution = avenir.reconstitution()
    # L'année d'ancrage est refaite par construction : sinon, la formule de
    # la projection n'est plus celle que la reconstitution applique.
    assert reconstitution[depenses.derniere_annee] == pytest.approx(1.0, rel=1e-12)
    ecarts = {annee: rapport - 1.0 for annee, rapport in reconstitution.items()
              if annee >= RECONSTITUTION_DEPUIS}
    assert min(ecarts) == RECONSTITUTION_DEPUIS, sorted(ecarts)
    pire = max(ecarts, key=lambda annee: abs(ecarts[annee]))
    ecart = abs(ecarts[pire])
    assert ecart <= RECONSTITUTION_CLIQUET, (
        f"{pire} : la projection refait le passé à {ecarts[pire]:+.1%}, le "
        f"cliquet en admet {RECONSTITUTION_CLIQUET:.1%} "
        f"(cible : {RECONSTITUTION_CIBLE:.0%})")
    assert ecart > RECONSTITUTION_CLIQUET - 0.01, (
        f"{pire} : {ecarts[pire]:+.1%}, l'écart a baissé : abaisser le cliquet "
        f"à {math.ceil(ecart * 200) / 200:.1%}")


#: Ce que la décomposition de la reconstitution admet, depuis la première
#: année de l'enquête auprès des caisses (2004), facteur par facteur. Mesuré
#: le 14 octobre 2026 (action 147, étape 18) : les têtes -6,1 % au pire (2009
#: et 2010), la pension de droit direct par tête -11,8 % (2007), la réversion
#: -1,9 % (2004, la part du COR reconduite avant 2010). Des cliquets, qui ne
#: doivent que descendre ; une session qui les fait passer sous eux d'un point
#: les abaisse.
RECONSTITUTION_TETES = 0.065
RECONSTITUTION_PENSION = 0.10
RECONSTITUTION_REVERSION = 0.02


def test_la_reconstitution_se_decompose_en_tetes_pension_et_reversion(avenir, depenses):
    """Le passé refait, en ses trois facteurs : d'où viennent les -16 % de 2009.

    L'enquête annuelle auprès des caisses compte, depuis 2004, les personnes
    qui touchent un droit direct, tous régimes réunis, et la masse de la
    réversion (:meth:`Avenir.reconstitution_decomposee`). L'écart de la
    reconstitution est, au produit près, celui des têtes, celui de la pension
    de droit direct par tête et celui de la réversion.

    *Le 14 octobre 2026*, en 2009, le pire depuis 2000 : -6,1 % de têtes,
    -11,0 % de pension par tête, -0,1 % de réversion. Les têtes suivent
    l'enquête en 2004 (+0,2 %), s'en écartent jusqu'en 2009 et y reviennent
    ensuite : c'est le dessin des départs anticipés pour carrière longue, de
    2004 à 2008, que la grille ne connaît pas (ses cas types partent à l'âge
    du taux plein) — l'âge conjoncturel de départ des hommes tombe de 60,06 à
    59,88 ans de 2004 à 2008 (DREES). La pension par tête, elle, croît plus
    vite dans le modèle que dans les comptes, de dix points de 2004 à 2024 :
    le défaut que la décomposition du COR situe déjà dans l'avenir. Les
    revalorisations servies en faisaient une part, que le scénario 1 servait
    sur les prix : depuis l'étape 19, il sert celles de son droit, et 2009
    passe à -13,9 % (-6,1 % de têtes, -8,3 % de pension par tête), mais la
    dérive de 2070 de 1,008 à 1,033.
    """
    effectifs = EffectifsRetraites(RACINE_DONNEES)
    decompose = avenir.reconstitution_decomposee(
        effectifs.serie(EffectifsRetraites.TOUS_REGIMES), depenses.droits_derives)
    reconstitution = avenir.reconstitution()
    assert min(decompose) == 2004 and max(decompose) == depenses.derniere_annee, sorted(decompose)
    for annee, (tetes, pension, reversion) in decompose.items():
        assert tetes * pension * reversion == pytest.approx(reconstitution[annee], rel=1e-12), annee
    assert decompose[depenses.derniere_annee] == pytest.approx((1.0, 1.0, 1.0), rel=1e-12)
    for rang, (nom, cliquet) in enumerate((("têtes", RECONSTITUTION_TETES),
                                           ("pension par tête", RECONSTITUTION_PENSION),
                                           ("réversion", RECONSTITUTION_REVERSION))):
        pire = max(decompose, key=lambda annee: abs(decompose[annee][rang] - 1.0))
        ecart = decompose[pire][rang] - 1.0
        assert abs(ecart) <= cliquet, (
            f"{pire} : {nom} {ecart:+.1%}, le cliquet en admet {cliquet:.1%}")


def test_le_scenario_1_sert_les_revalorisations_de_son_droit(avenir):
    """Action 147, étape 19 : la masse du scénario 1 sert, jusqu'au dernier
    barème, ce que le droit a servi (:meth:`RevalorisationServie.coefficient_historique`),
    et non les prix. Une pension du régime général liquidée en 2000 vaut, en
    2024, 4,7 % de moins que la même revalorisée sur les prix — le gel de
    2014, les 0,3 % de 2019 ; celle de la fonction publique, dont le point
    d'indice a décroché des prix avant 2004, 7,6 % de moins. Le RAFP, hors
    répartition, n'est pas dans la masse, et sa part ne se revalorise pas. Au-delà
    du dernier barème, les prix : un départ à venir garde un coefficient de un.
    Et les réformes prospectives, qui servent à qui est parti avant elles la
    pension du scénario 1, la servent sous son droit jusqu'à la bascule : leur
    stock est toute la masse du scénario 1 sur les années publiées (après,
    les cohortes de la grille qui partent après la bascule en sortent)."""
    simulateur = Simulateur(Parametres()).pour_la_projection()
    revalorisation = RevalorisationServie(simulateur, 2000, 2070)
    general = revalorisation.coefficient_historique("regime_general", 2000, 2024)
    assert 0.94 < general < 0.96, general
    publique = revalorisation.coefficient_historique("fonction_publique_etat", 2000, 2024)
    assert 0.91 < publique < 0.93, publique
    assert revalorisation.coefficient_historique("rafp", 2010, 2024) == 1.0
    assert revalorisation.coefficient_historique("regime_general", 2030, 2050) == 1.0
    # Figé au dernier barème : la projection lit les prix au-delà.
    assert revalorisation.coefficient_historique("regime_general", 2000, 2040) == (
        revalorisation.coefficient_historique("regime_general", 2000, 2060))
    for ligne in avenir.annees:
        if not ligne.projete:
            assert ligne.part_stock == pytest.approx(1.0, rel=1e-12), ligne.annee


#: Ce que le contrôle par la décomposition du COR tolère sur les EFFECTIFS de
#: retraités, à chaque fin de sous-période du COR, la dernière année observée du
#: compte valant un. Mesuré le 5 octobre 2026 : +2,3 % en 2030, -1,0 % en 2045,
#: -0,8 % en 2070.
DECOMPOSITION_TETES = 0.03
#: Le cliquet de la PENSION MOYENNE RELATIVE à l'horizon : le modèle la fait
#: reculer de 3,3 % de 2025 à 2070, le COR de 17,2 % ; 16,8 % de trop, le
#: 5 octobre 2026, puis 14,0 % le même jour, une fois suivies les deux
#: conventions du COR (rendement de l'Agirc-Arrco, primes des fonctionnaires,
#: action 147, étape 4), puis 13,1 % (le modèle -6,3 %), les poids calés
#: groupe par groupe sur la dépense du COR (étape 8), puis 10,4 %, la fonction
#: publique suivant les retraités et le traitement indiciaire du COR (étape
#: 9), puis 6,2 % (le modèle -12,0 %), l'Agirc-Arrco au taux moyen des
#: entreprises (étape 10), puis 3,1 % (le modèle -14,6 %), la masse de chaque
#: génération portant ses arrivées tardives et le fonctionnaire de l'État
#: entrant tard dans son régime (étape 11). L'étape 13 le relève à 5,3 % (le
#: modèle -12,7 %) : les exploitants agricoles, la SNCF et les IEG suivent les
#: retraités du COR, et leurs têtes vont aux carrières du privé, mieux payées
#: que celles des exploitants — la correction d'un défaut qui en masquait un
#: autre, l'écart passant de -2,3 à -0,4 % en 2050. L'étape 14 le ramène à
#: 2,4 % (le modèle -15,2 %), à la cible : la complétude de chaque génération
#: porte les carrières incomplètes des natifs, plus courtes à chaque
#: génération après 1965. L'étape 19 le relève à 4,9 % (le modèle -13,4 %) :
#: le scénario 1 sert les revalorisations de son droit, le stock de 2025,
#: érodé par le gel de 2014 et les revalorisations sous les prix, pèse moins
#: dans l'ancrage, et la masse remonte quand il s'éteint — la correction d'un
#: défaut qui en masquait un autre, celui de la pension par tête qui croît trop
#: vite (étape 18). Les grilles de chaque époque de la Cipav et de la CAVEC
#: (action 131, 14 octobre) le relèvent à 5,4 % (le modèle -12,7 %) : la
#: complémentaire du libéral de la population, seul de la Cipav pour les dix
#: sections (action 152), baisse d'un tiers en 2025, et le calage sur la
#: dépense des groupes du COR lui rend 18 % de têtes, et 2 % de masse à
#: l'Agirc-Arrco, qu'ils gardent jusqu'en 2070. Le partage de la CNRACL entre
#: ses départs actifs et sédentaires (action 138, étape 3, 16 octobre) le
#: relève à 5,7 % : quatre agents sur cinq partent désormais au taux plein des
#: sédentaires, trois ans après l'actif, comme le jaune pensions le dit, et
#: leur pension est plus haute d'autant. Il ne doit que descendre.
DECOMPOSITION_PENSION_CLIQUET = 0.06
DECOMPOSITION_PENSION_CIBLE = 0.03


def test_la_projection_compte_les_retraites_du_cor(avenir, comptes):
    """La trajectoire du système actuel refait les EFFECTIFS du COR.

    La masse des pensions est un nombre de retraités multiplié par une pension
    moyenne. Le COR publie le rythme du premier, sous-période par sous-période
    (tableau 2.1 du rapport de juin 2026) ; le modèle compte les siens, cohorte
    par cohorte, à l'âge de départ de chaque cas type
    (:meth:`Avenir.decomposition`). Les deux se suivent à quelques pour cent
    près, sur un horizon où les retraités croissent d'un quart : ce n'est pas
    par les têtes que la projection s'écarte du COR.
    """
    depuis = comptes.derniere_annee_observee
    modele = avenir.decomposition(depuis)
    cor = comptes.decomposition
    fins = [fin for debut, fin in cor.periodes() if debut >= depuis]
    assert fins, "décomposition du COR absente ou sans sous-période projetée"
    for fin in fins:
        attendu = cor.indice_croissance("retraites", depuis, fin)
        assert attendu is not None, fin
        ecart = modele[fin][0] / attendu - 1.0
        assert abs(ecart) <= DECOMPOSITION_TETES, (
            f"{fin} : le modèle compte {modele[fin][0]:.3f} fois les retraités de "
            f"{depuis}, le COR {attendu:.3f} ({ecart:+.1%})")


def test_la_pension_moyenne_relative_s_ecarte_de_celle_du_cor(avenir, comptes):
    """Ce qui sépare la trajectoire du COR : la pension moyenne relative.

    Le COR la fait reculer de 17 % de 2025 à 2070 — l'indexation des droits sur
    les prix, la baisse du rendement de l'Agirc-Arrco, la part croissante des
    primes des fonctionnaires, que sa figure 2.7 lit régime par régime ; le
    modèle, de 14,6 %, depuis qu'il suit les deux dernières conventions, que
    ses poids sont calés sur la dépense des groupes du COR, que la fonction
    publique suit ses retraités et son traitement indiciaire, que
    l'Agirc-Arrco compte ses points au taux moyen des entreprises et que la
    masse de chaque génération porte ses arrivées tardives (de 3,5 % avant,
    puis de 5,6 %, de 6,3 %, de 8,6 %, de 12,0 %). C'est l'écart tout entier :
    les effectifs, eux, se suivent
    (``test_la_projection_compte_les_retraites_du_cor``). Le même défaut fait
    la reconstitution du passé (``test_la_projection_refait_le_passe``) : la
    pension relative du modèle croît de 11,4 % de 2005 à 2025 (17,5 % avant
    l'étape 10), celle du COR de 8,9 %.

    Le seuil est un CLIQUET, comme celui de la reconstitution : il ne doit que
    descendre, et un écart qui passe d'un point sous lui demande de l'abaisser.
    """
    depuis = comptes.derniere_annee_observee
    horizon = avenir.derniere_annee
    modele = avenir.decomposition(depuis)[horizon][1]
    attendu = comptes.decomposition.indice("pension_relative", "ensemble", depuis, horizon)
    assert attendu is not None
    ecart = modele / attendu - 1.0
    assert ecart <= DECOMPOSITION_PENSION_CLIQUET, (
        f"{horizon} : pension relative du modèle {modele:.3f}, du COR {attendu:.3f} "
        f"({ecart:+.1%}, cliquet {DECOMPOSITION_PENSION_CLIQUET:.0%}, cible "
        f"{DECOMPOSITION_PENSION_CIBLE:.0%})")
    assert ecart > DECOMPOSITION_PENSION_CLIQUET - 0.01, (
        f"{ecart:+.1%} : l'écart a baissé, abaisser le cliquet à "
        f"{math.ceil(ecart * 100) / 100:.0%}")


#: Groupe par groupe de régimes, ce que la projection SUIT du COR, à
#: l'horizon, depuis la dernière année observée : l'écart toléré, dans les deux
#: sens. Mesuré le 5 octobre 2026 (action 147, étape 5) : pension moyenne
#: relative de la Cnav -0,5 % ; dépense en part de PIB de LURA +1,6 %, de la
#: CNRACL -3,4 %. À l'étape 9, LURA passe à +4,2 % : la fonction publique
#: suivant les retraités que le COR lui projette, le privé pèse plus. La
#: CNRACL quitte la liste : ses têtes suivent celles du COR, et sa dépense
#: rend l'écart de sa pension moyenne, que ses têtes trop lentes masquaient.
#: À l'étape 10, les complémentaires y entrent, à -0,1 % : l'Agirc-Arrco
#: compte ses points au taux moyen des entreprises. À l'étape 13, la dépense
#: du modèle porte sa réversion comme celle du COR (LURA +3,4 %, complémentaires
#: -1,7 %), et les non-salariés y entrent, à +0,2 % : les exploitants
#: agricoles suivent les retraités que le COR leur projette. À l'étape 14,
#: les carrières incomplètes des natifs portées : LURA +0,5 %, Cnav +0,2 %,
#: non-salariés -2,7 %, complémentaires -4,4 %, que les polypensionnés,
#: absents de la grille, laissent sous le COR (tolérance relevée à 5 %). À
#: l'étape 16, l'ancrage du salaire moyen lu dans les données (+2,2 %) et le
#: cas type au SMIC payé au SMIC de chaque année : LURA +0,6 %, Cnav +0,3 %,
#: complémentaires -4,0 %, non-salariés -3,2 % (tolérance relevée à 4 %).
#: Le 7 octobre, la pension majorée de référence des exploitants (action 138,
#: étape 8) : non-salariés -5,2 %, complémentaires -4,4 % (tolérance des
#: non-salariés relevée à 6 %). Elle relève en 2025 les pensions des
#: générations que leurs revenus agricoles laissaient basses, et lie moins
#: celles qui suivent : la pension relative du groupe ne croît plus que de
#: 3 % jusqu'en 2070, au lieu de 6. Le 19 octobre, l'inapte de la Cnav, puis
#: l'ex-invalide (action 138, étape 7) : complémentaires +5,2 %, non-salariés
#: +8,2 %, +6,0 avec le seul inapte (tolérances relevées à 6 et 9 %).
#: L'ex-invalide sert LURA et les complémentaires dans d'autres proportions que
#: les quatre carrières du privé dont il prend la part, et déplace le calage
#: des poids par groupe (``_poids_par_groupe``) : sous la table commune même,
#: les non-salariés pèsent 2,4 % de plus en 2070. Le 20 octobre, la valeur de
#: service de l'Agirc-Arrco relevée de 1,4 % au 1er novembre 2026 (décision du
#: 14 octobre), que le dépôt reconduisait gelée : complémentaires de +5,2 à
#: +6,3 % (tolérance relevée à 7 %). Le 24 octobre, chaque caisse divisée par
#: les têtes de ses cas types (action 138, étape 3) : complémentaires de +6,4 à
#: +7,9 %, non-salariés de +7,5 à +10,8 % (tolérances relevées à 8 et 11 %),
#: LURA de +2,4 à +3,1 %, pension relative de la Cnav de -0,2 à +0,8 %. Les
#: caisses que le dépôt reconduit gardent désormais dans la grille la part de
#: leurs retraités, et non plus celle-ci fois les années que leurs cas types
#: passent en retraite : partis après les autres, l'artisan, le libéral et le
#: contractuel de l'Ircantec pèsent plus en 2025 — 5,2, 2,0 et 9,1 % des têtes
#: au lieu de 4,6, 1,6 et 8,1 —, et la reconduction de leur part davantage dans
#: leurs groupes : les non-salariés, dont le COR fait reculer la dépense avec
#: celle des exploitants, et les complémentaires.
DECOMPOSITION_GROUPES_SUIVIS = {
    ("pension_relative", "cnav"): 0.04,
    ("depense_part_pib", "lura"): 0.05,
    ("depense_part_pib", "complementaires"): 0.08,
    ("depense_part_pib", "non_salaries_base"): 0.11,
}
#: Et ce qu'elle ne suit pas encore : des CLIQUETS, qui ne doivent que
#: descendre, comme celui de la pension moyenne relative de l'ensemble. Mesurés
#: le même jour : pension relative de la FPE +37,6 %, de la CNRACL +12,3 %, de
#: l'Agirc-Arrco +46,3 % ; dépense de la FPE +92,4 %, des non-salariés +129,7 %,
#: des régimes spéciaux +81,4 %, des complémentaires +12,0 %. Les complémentaires
#: passent à +13,3 % à l'étape 8 : le calage des poids sur la dépense des
#: groupes du COR alourdit le cadre, dont l'Agirc croît plus vite ; la
#: correction d'un défaut qui en masquait un autre. L'étape 9 fait suivre aux
#: caisses de la fonction publique les retraités que le COR leur projette, et
#: au traitement indiciaire son décrochage de 2019 à 2025 : pension relative de
#: la FPE +16,8 %, de la CNRACL +8,8 % ; dépense de la FPE +38,1 %, de la
#: CNRACL +11,1 %. La part que l'État perd revient aux autres cas types, dont
#: l'écart s'en alourdit : non-salariés +133,2 %, régimes spéciaux +84,5 %,
#: complémentaires +15,3 % — encore un défaut qui en masquait d'autres.
#: L'étape 10 compte l'Agirc-Arrco au taux moyen des entreprises : pension
#: relative de l'Agirc-Arrco +23,9 %, dépense des complémentaires -0,1 %, qui
#: passent aux groupes suivis ; le calage des poids sur la dépense des groupes
#: en reporte un peu sur les non-salariés, +134,7 %. L'étape 11 fait entrer le
#: fonctionnaire de l'État dans son régime deux ans après le début de sa
#: carrière, huit pour la génération 2000, et porte à la masse de chaque
#: génération ses arrivées tardives : pension relative de la FPE +3,8 %, de la
#: CNRACL +6,1 %, de l'Agirc-Arrco +20,4 % ; dépense de la FPE +23,1 %, de la
#: CNRACL +8,4 %, des non-salariés +128,4 %, des régimes spéciaux +80,0 %.
#: L'étape 13 compare la dépense du modèle réversion comprise, comme celle du
#: COR, et fait suivre aux exploitants agricoles, à la SNCF et aux IEG les
#: retraités qu'il leur projette, ce qu'ils perdent allant aux caisses
#: reconduites : dépense de la FPE +19,1 %, de la CNRACL +4,8 % ; les régimes
#: spéciaux passent sous le COR, à -32,7 %, la grille n'ayant que la SNCF et
#: les IEG, qui se ferment plus vite que la RATP, les notaires ou la Banque de
#: France ; les non-salariés passent aux groupes suivis. Le cliquet porte sur
#: l'écart en valeur absolue. L'étape 14 pèse chaque génération de sa durée
#: validée : pension relative de la FPE +1,0 %, de la CNRACL +3,2 %, de
#: l'Agirc-Arrco +17,1 % ; dépense de la FPE +15,8 %, de la CNRACL +1,9 %, des
#: régimes spéciaux -34,4 %. L'étape 16 lit l'ancrage du salaire moyen dans les
#: données et paie le cas type au SMIC le SMIC de chaque année : la pension
#: relative de la FPE passe de +0,97 à +1,01 %, au-dessus du cliquet de 1 %,
#: qui remonte d'un point ; celle de l'Agirc-Arrco à +17,6 %. L'étape 17 de
#: l'action 138 sert la bonification du cinquième des militaires (L. 12, i) :
#: vingt trimestres au cas type militaire, dont la pension monte d'un cinquième.
#: La pension relative de la FPE passe de +1,0 à +4,2 %, sa dépense de +15,8 à
#: +19,2 %, et les deux cliquets remontent : la règle est le droit, et le cas
#: type, vingt-cinq ans de services, en reçoit le plafond, quand le militaire
#: qui liquide en 2023 en reçoit 16,4 trimestres (jaune, tableau 50).
#: L'étape 1 de l'action 152 fait du cas type militaire le militaire moyen du
#: jaune, radié à quarante-huit ans et demi après vingt-sept ans et demi de
#: services, à 1,15 salaire moyen, quand il partait à quarante-quatre ans à
#: 0,95 : la pension relative de la FPE passe de +4,2 à +9,3 %, sa dépense de
#: +19,2 à +24,8 %, et les deux cliquets remontent. Plus haute d'un tiers, la
#: pension militaire baisse aussi moins d'ici l'horizon : partie en 2028, quand
#: le traitement indiciaire a déjà décroché de 5 %, elle perd 7 % rapportée au
#: salaire moyen jusqu'aux départs de 2048, quand celle qui partait en 2024
#: perdait 12 % jusqu'à ceux de 2044. L'étape 5 de l'action 159 recale les
#: deux civils sur les départs de 2025 du jaune pensions annexé au PLF 2027 :
#: le sédentaire entre dans l'État après six ans sous contrat pour la
#: génération 1961, deux pour la génération 1944, douze pour la génération
#: 2000 ; l'agent de la CNRACL part au taux plein et non plus à l'âge
#: d'ouverture, à 0,9 salaire moyen et non plus 1,1, après six ans sous
#: contrat. La pension relative de la FPE passe de +9,3 à +5,2 %, sa dépense de
#: +24,8 à +19,9 % ; celle de la CNRACL de +3,2 à +0,2 %, et sa dépense de
#: +1,5 à +10,9 % : ce cliquet-là remonte. Les têtes de la CNRACL croissaient
#: de 4 % de moins que les retraités que le COR lui projette d'ici l'horizon,
#: et sa pension relative de 3 % de plus ; ses têtes croissent désormais de
#: 7 % de plus. Le cas type porte toute la caisse en catégorie active, parti
#: à soixante-deux ans, quand le COR fait monter l'âge moyen de départ à la
#: CNRACL de 61,5 à 64,3 ans avec ses sédentaires (Canopée, au registre,
#: chantier 138.3) : encore un défaut qui en masquait un autre. L'étape 19
#: de l'action 147, le scénario 1 servant les revalorisations de son droit,
#: relève les pensions relatives à l'horizon — FPE +8,0 %, CNRACL +3,4 %,
#: Agirc-Arrco +22,2 % — et les dépenses — FPE +23,1 %, CNRACL +13,7 %,
#: régimes spéciaux -33,1 % — : le
#: stock de 2025, revalorisé au point d'indice, par décret ou à une valeur de
#: service gelée, sous les prix, pèse moins dans l'ancrage, et s'éteint.
#: L'agent sédentaire de la CNRACL, qui porte quatre cinquièmes de la caisse
#: et part trois ans après l'actif (action 138, étape 3), y suit enfin la
#: montée de l'âge de départ que le COR projette : la dépense de la CNRACL
#: passe de +13,3 à +7,5 %, sa pension relative de +3,4 à +3,5 %. Les deux
#: actifs de l'État, qui portent un départ civil sur cinq et partent de deux à
#: huit ans avant le sédentaire (même étape), y font de même pour la FPE : sa
#: pension relative passe de +8,0 à +5,1 %, sa dépense de +22,3 à +19,3 %.
#: L'étape 7 de l'action 138, le 17 octobre, fait vivre chaque cas type au
#: rythme du vingtile de son diviseur, à nombre de décès égal : la pension
#: relative de l'Agirc-Arrco passe de +22,2 à +21,4 %, la dépense de la FPE de
#: +19,3 à +18,9 %, celle des régimes spéciaux de -33,6 à -32,3 %. L'étape 3,
#: le 18 octobre, fait partir chaque cohorte de la grille l'année que le droit
#: de sa génération lui donne, et le cliquet de l'Agirc-Arrco remonte, comme
#: celui de la reconstitution le 5 octobre, parce qu'un défaut en masquait un
#: autre : sa pension relative passe de +21,4 à +23,8 %, la dépense de la FPE
#: de +18,9 à +22,4 %, celle de la CNRACL de +7,5 à +11,2 %. En 2025, d'où la
#: mesure part, la grille faisait partir le cadre de 1961, le fonctionnaire
#: sédentaire de l'État et l'agent sédentaire de la CNRACL de 1962, qui
#: partent en 2026, à 168 et 169 trimestres : la pension moyenne de
#: l'Agirc-Arrco et la dépense des deux fonctions publiques y étaient trop
#: hautes, et leur croissance jusqu'à l'horizon trop basse. L'étape 7, le
#: 19 octobre, donne à la Cnav ses inaptes, à leur part de ses départs et à
#: leur mortalité : la dépense de la FPE passe de +22,4 à +22,0 %, celle de la
#: CNRACL de +11,2 à +10,9 %. Le 20 octobre, la valeur de service de
#: l'Agirc-Arrco relevée de 1,4 % au 1er novembre 2026, que le dépôt
#: reconduisait gelée : sa pension relative passe de +23,1 à +24,8 %, et son
#: cliquet remonte : la règle est le droit. L'étape 3, le 24 octobre, compte
#: le militaire dès l'année de ses 48 ans, quand la pyramide, qui commençait à
#: 50 ans, lui retirait ses deux premières années de pension, et fait entrer
#: dans la grille la génération 2020, dont les militaires partent de 2066 à
#: 2070 : la dépense de la FPE passe de +21,4 à +26,5 %, sa pension relative de
#: +5,6 à +6,1 %, et leurs cliquets remontent, comme le 18 octobre, parce
#: qu'un défaut en masquait un autre : l'année du calage, 2025, comptait le
#: militaire à partir de 50 ans, l'horizon sans ses cinq cohortes les plus
#: jeunes. La grille le pèse, jusqu'en 2070, de la part de sa caisse en 2024.
#: Le même jour, chaque caisse se divise par les têtes de ses cas types
#: (action 138, étape 3) : pesé de la part de sa caisse dans le stock,
#: appliquée à chaque génération, un cas type qui part tôt comptait d'autant
#: plus de retraités qu'il passe plus d'années en retraite. Le militaire
#: faisait 30,3 % des retraités de l'État de la grille en 2030, 44,5 % en
#: 2070, pour 19,5 et 32,8 % que le COR donne à sa caisse ; l'agent de
#: conduite 1,03 % des têtes en 2025 et 0,16 % en 2070, quand le COR fait
#: reculer sa caisse de 0,65 à 0,16 %. La dépense de la FPE passe de +26,5 à
#: +17,6 %, sa pension relative de +6,1 à +4,9 %, la dépense de la CNRACL de
#: +10,3 à +8,4 %, celle des régimes spéciaux de -32,5 à -4,5 %, et leurs
#: cliquets descendent.
DECOMPOSITION_GROUPES_CLIQUETS = {
    ("pension_relative", "fpe"): 0.05,
    ("pension_relative", "cnracl"): 0.04,
    ("pension_relative", "agirc_arrco"): 0.25,
    ("depense_part_pib", "fpe"): 0.18,
    ("depense_part_pib", "cnracl"): 0.09,
    ("depense_part_pib", "regimes_speciaux"): 0.05,
}


def _ecarts_par_groupe(avenir, comptes) -> dict[tuple[str, str], float]:
    """L'écart du modèle au COR à l'horizon, grandeur par grandeur et groupe
    par groupe, chacun depuis la dernière année observée — ou la suivante,
    quand le COR ne publie le groupe qu'à partir d'elle (la CNRACL)."""
    depuis = comptes.derniere_annee_observee
    horizon = avenir.derniere_annee
    cor = comptes.decomposition
    ecarts: dict[tuple[str, str], float] = {}
    for grandeur, groupes, rang in (("pension_relative", REGIMES_DU_MODELE, 1),
                                    ("depense_part_pib", GROUPES_DU_MODELE, 2)):
        for groupe, regimes in groupes.items():
            base = depuis if cor.valeur(grandeur, groupe, depuis) is not None else depuis + 1
            attendu = cor.indice(grandeur, groupe, base, horizon)
            assert attendu is not None, (grandeur, groupe)
            modele = avenir.decomposition_groupes(base, {groupe: regimes})[groupe][horizon][rang]
            ecarts[(grandeur, groupe)] = modele / attendu - 1.0
    return ecarts


def test_la_fonction_publique_suit_ses_retraites_et_son_traitement_au_cor():
    """Les deux corrections de l'étape 9 de l'action 147, et leur jumeau.

    LES RETRAITÉS. Au-delà de la dernière enquête de la DREES, la répartition
    de 2024 était reconduite : les civils de l'État gardaient leur part des
    retraités jusqu'en 2070, quand le COR la fait reculer d'un tiers. Les
    caisses de la fonction publique suivent désormais la croissance que le
    classeur par régime du COR donne à leurs retraités, rapportée à celle de
    tous les retraités ; les autres gardent leur effectif de bord, à ce
    qu'elles se partagent près depuis l'étape 13
    (``test_les_caisses_qui_se_ferment_rendent_leur_part_au_prive``).

    LE TRAITEMENT. Le traitement indiciaire relatif valait un avant 2025 ; il
    porte désormais le décrochage que la figure 1.14 du rapport de juin 2026
    publie de 2019 à 2024, le premier point reconduit avant lui.
    """
    from retraite_notionnelle.donnees.chargement import charger_yaml
    from retraite_notionnelle.donnees.macro import DonneesMacro

    effectifs = EffectifsRetraites(RACINE_DONNEES)
    reconduits = EffectifsRetraites(RACINE_DONNEES, projetees=())
    chemin = RACINE_DONNEES / "reference" / "regimes" / "retraites_projetes.csv"
    with chemin.open(encoding="utf-8") as flux:
        cor: dict[str, dict[int, float]] = {}
        for ligne in csv.DictReader(l for l in flux if not l.startswith("#")):
            cor.setdefault(ligne["caisse"], {})[int(ligne["annee"])] = float(ligne["retraites"])
    personnes = ComptesRetraite(RACINE_DONNEES).decomposition.indice_croissance(
        "retraites", 2030, 2070)
    assert personnes is not None and personnes > 1.0
    for caisse in EffectifsRetraites.CAISSES_PROJETEES:
        assert effectifs.effectif(caisse, 2024) == reconduits.effectif(caisse, 2024)
        assert effectifs.fiabilite(caisse, 2070) == Fiabilite.ESTIMEE
        assert effectifs.effectif(caisse, 2070) / effectifs.effectif(caisse, 2030) \
            == pytest.approx(cor[caisse][2070] / cor[caisse][2030] / personnes, rel=1e-12)
    assert effectifs.effectif("cnav", 2024) == reconduits.effectif("cnav", 2024)
    poids, avant = poids_effectifs(effectifs, 2070), poids_effectifs(reconduits, 2070)
    assert poids["fonctionnaire_sedentaire"] < 0.7 * avant["fonctionnaire_sedentaire"]
    assert poids["fonctionnaire_actif"] > avant["fonctionnaire_actif"]

    macro = DonneesMacro(RACINE_DONNEES)
    passe = charger_yaml(RACINE_DONNEES / "reference" / "macro"
                         / "hypotheses_projection.yaml")["traitement_indiciaire"]["passe"]
    attendus = {int(annee): traitement / revenu for annee, traitement, revenu
                in zip(passe["annees"], passe["traitement"], passe["revenu_moyen"])}
    premiere = min(attendus)
    attendus[premiere - 20] = attendus[premiere]
    for annee, valeur in attendus.items():
        assert macro.traitement_indiciaire_relatif(annee) == pytest.approx(valeur, rel=1e-12)
    # Le décrochage déjà fait : 4 % depuis 2019, le revenu moyen de 2020
    # plongeant avec l'activité partielle.
    assert 1.03 < attendus[2019] < 1.05 < attendus[2020]
    assert macro.traitement_indiciaire_relatif(2025) == 1.0
    # Le portage JavaScript le refaisait, et un test l'y confrontait : il ne
    # servait qu'au coût, figé depuis le 11 octobre 2026 (action 150).


def test_les_arrivees_tardives_se_lisent_dans_la_pyramide():
    """Action 147, étape 11 : ce que les arrivées après 21 ans retirent à la
    pension d'une génération, tiré du classeur de l'INSEE que lit déjà la
    pyramide (``arrivees_tardives.csv``). Le manque double des générations
    d'après-guerre à celles des années 1990 — 2,9 % en moyenne de 1941 à 1955,
    6,0 % de 1986 à 2005 —, que l'hypothèse de solde migratoire de + 150 000
    par an fait arriver adultes ; hors de la série, la valeur du bord."""
    from retraite_notionnelle.donnees.population import ArriveesTardives

    arrivees = ArriveesTardives(RACINE_DONNEES)
    assert (arrivees.premiere_generation, arrivees.derniere_generation) == (1941, 2005)
    manque = {g: 1.0 - arrivees.completude(g) for g in range(1941, 2006)}
    assert all(0.0 < valeur < 0.08 for valeur in manque.values()), manque
    anciennes = sum(manque[g] for g in range(1941, 1956)) / 15
    recentes = sum(manque[g] for g in range(1986, 2006)) / 20
    assert anciennes < 0.035 and recentes > 0.055, (anciennes, recentes)
    assert arrivees.completude(1900) == arrivees.completude(1941)
    assert arrivees.completude(2015) == arrivees.completude(2005)


def test_les_carrieres_incompletes_des_natifs():
    """Action 147, étape 14 : la grille fait partir chacune de ses carrières
    au taux plein, avec la durée requise de sa génération ; les retraités
    d'une génération résidant en France en ont validé, en moyenne, ce que
    publie le COR (figure 3.22 du rapport de juin 2026). La complétude d'une
    génération est cette durée, moyenne des deux sexes, rapportée à sa durée
    requise : elle porte déjà les arrivées tardives, et le facteur des natifs
    en est le reste.

    Le profil est celui que la DREES et TRAJECTOiRE décrivent : les natifs
    nés vers 1940 — les femmes surtout, 133 trimestres pour la génération
    1940 — touchent moins que la grille, ceux de 1950 à 1965 un peu plus,
    leurs carrières dépassant la durée requise, et ceux nés après 1975 de
    moins en moins, entrés plus tard dans la vie active sous une durée requise
    qui s'allonge."""
    from retraite_notionnelle.donnees.chargement import (charger_table_par_generation,
                                                         valeur_par_generation)
    from retraite_notionnelle.donnees.population import CarrieresIncompletes

    carrieres = CarrieresIncompletes(RACINE_DONNEES)
    assert (carrieres.premiere_generation, carrieres.derniere_generation) == (1940, 2005)
    with (RACINE_DONNEES / "reference" / "macro"
          / "duree_assurance_generations.csv").open(encoding="utf-8") as flux:
        durees: dict[int, dict[str, float]] = {}
        for ligne in csv.DictReader(l for l in flux if not l.startswith("#")):
            durees.setdefault(int(ligne["generation"]), {})[ligne["sexe"]] = float(
                ligne["trimestres"])
    assert min(durees) == 1940 and max(durees) == 2000
    assert durees[1940]["femmes"] < durees[1940]["hommes"] - 25
    requises, generations = charger_table_par_generation(
        RACINE_DONNEES / "reference" / "legislation" / "duree_assurance_requise.csv",
        "trimestres")
    for generation, sexes in durees.items():
        moyenne = (sexes["femmes"] + sexes["hommes"]) / 2
        requise = valeur_par_generation(requises, generations, generation)[0]
        assert carrieres.completude(generation) == pytest.approx(moyenne / requise,
                                                                 rel=1e-12), generation
        assert carrieres.completude(generation) == pytest.approx(
            carrieres.arrivees.completude(generation) * carrieres.natifs(generation),
            rel=1e-15), generation
    # Une génération que la figure laisse vide prend la moyenne de ses voisines.
    assert 1941 not in durees and 1943 not in durees
    assert durees[1942]["hommes"] != durees[1940]["hommes"]
    assert all(carrieres.completude(g) < 1.0 for g in range(1900, 2016))
    natifs = {g: carrieres.natifs(g) for g in range(1940, 2001)}
    assert max(natifs, key=natifs.get) in range(1950, 1966)
    assert natifs[1940] < 0.98 and all(natifs[g] < 0.99 for g in range(1980, 2001))
    assert all(natifs[g] > 1.0 for g in range(1953, 1964))
    assert carrieres.natifs(1900) == carrieres.natifs(1940)
    assert carrieres.natifs(2015) == carrieres.natifs(2000)


def test_les_arrivees_tardives_pesent_les_masses_et_non_les_tetes(population):
    """La complétude d'une cohorte pèse sa masse de pensions, dans tous les
    systèmes et dans chaque régime, et non ses têtes : un arrivé tard est un
    retraité, à la pension plus courte (``Pensionne.completude``)."""
    from retraite_notionnelle.cout import (
        CLES_CAS_TYPES, RESSOURCES_GARANTIE, TETES_TOUTES, Pensionne, VoletLiberal,
        _masses, _masses_regimes, coefficient_servi)

    simulateur = Simulateur(Parametres()).pour_la_projection()
    revalorisation = RevalorisationServie(simulateur, 2000, 2030)
    volet = VoletLiberal(annee_liquidation=2010, annee_ouverture_garantie=2011,
                         pension=1.0, ressources_garantie=1.0)
    entiere = Pensionne(code="x", generation=1950, annee_liquidation=2010,
                        pensions={cle: 1.0 for cle in CLES_CAS_TYPES}, propre=volet,
                        parts_regimes={"regime_general": 1.0})
    completudes = (0.90, 0.92, 0.94, 0.96, 0.98)
    raccourcie = replace(entiere, completudes=completudes)
    effectifs = [population.effectif(2020 - 1950 - decalage, 2020)
                 for decalage in range(-2, 3)]
    attendu = sum(e * k for e, k in zip(effectifs, completudes)) / sum(effectifs)
    masses, _, tetes = _masses([entiere], population, 2020, {"x": 1.0}, revalorisation)
    courtes, _, tetes_courtes = _masses([raccourcie], population, 2020, {"x": 1.0},
                                        revalorisation)
    assert tetes_courtes[TETES_TOUTES] == tetes[TETES_TOUTES] == pytest.approx(
        sum(effectifs), rel=1e-12)
    # Au système actuel, la moyenne des complétudes que pèsent les effectifs
    # et ce que le droit a servi à chaque cohorte depuis son départ (action
    # 147, étape 19) ; aux autres, dont la revalorisation dépend aussi de
    # l'année de départ de chaque cohorte, une moyenne entre la plus courte et
    # la plus longue.
    servis = [coefficient_servi({"regime_general": 1.0}, revalorisation,
                                2010 + decalage, 2020) for decalage in range(-2, 3)]
    assert courtes["actuel"] == pytest.approx(
        masses["actuel"] * sum(e * k * c for e, k, c in zip(effectifs, completudes, servis))
        / sum(e * c for e, c in zip(effectifs, servis)), rel=1e-12)
    assert courtes["actuel"] != pytest.approx(masses["actuel"] * attendu, rel=1e-6)
    for cle in ("notionnel_retroactif", "notionnel_liberal", RESSOURCES_GARANTIE):
        assert 0.90 < courtes[cle] / masses[cle] < 0.98, cle
    regimes, tetes_regimes = _masses_regimes([entiere], population, 2020, {"x": 1.0},
                                             revalorisation)
    courts, tetes_courts = _masses_regimes([raccourcie], population, 2020, {"x": 1.0},
                                           revalorisation)
    assert tetes_courts == tetes_regimes
    assert courts["regime_general"] == pytest.approx(
        regimes["regime_general"] * courtes["actuel"] / masses["actuel"], rel=1e-12)
    # Sans complétudes, la pension entière : la grille du simulateur individuel.
    assert entiere.completude(-2) == entiere.completude(2) == 1.0


def test_chaque_cohorte_survit_au_rythme_de_sa_population(population):
    """Les cas types ne vivent plus tous comme la population générale (action
    138, étape 7, la mortalité différentielle), mais à nombre de décès égal :
    passé sa liquidation, chaque cohorte garde les survivants que la pyramide
    lui donne, répartis entre ses cas types au rythme de leur survie
    (``Pensionne.survie``), divisée par leur moyenne pesée comme la grille les
    pèse. Têtes et masses, dans tous les systèmes et dans chaque régime — le
    calage des groupes compris, qui pèse les cas types un à un —, ce que
    versent ceux qui travaillent encore et les rentes de leur pilier, chacun à
    ses poids. Avant la liquidation, et pour un cas type seul de sa grille,
    rien ne change."""
    from retraite_notionnelle.cout import (
        CLES_CAS_TYPES, RESSOURCES_GARANTIE, TETES_TOUTES, Pensionne, VoletLiberal,
        _masses, _masses_cotisations, _masses_pilier, _masses_regimes,
        coefficient_servi)

    simulateur = Simulateur(Parametres()).pour_la_projection()
    revalorisation = RevalorisationServie(simulateur, 2000, 2030)

    def couple(code: str, montant: float) -> Pensionne:
        # La proposition part cinq ans après le droit en vigueur, et cotise
        # jusque-là, à son compte et à son pilier.
        volet = VoletLiberal(
            annee_liquidation=2015, annee_ouverture_garantie=2015, pension=montant,
            ressources_garantie=montant,
            cotisations={a: montant for a in range(1990, 2016)},
            pilier={a: (montant, 0.1, 0.01, 10.0) for a in range(1990, 2016)},
            rente_pilier=(2.0 * montant, 1.5 * montant))
        return Pensionne(code=code, generation=1950, annee_liquidation=2010,
                         pensions={cle: montant for cle in CLES_CAS_TYPES}, propre=volet,
                         parts_regimes={"regime_general": 1.0})

    # « a » survit deux centièmes de mieux que la population générale par
    # année passée depuis la liquidation de sa cohorte, « b » un centième de
    # moins : en 2020, 1,24 et 0,88 pour la cohorte née en 1948, partie en 2008.
    communes = {"a": couple("a", 2.0), "b": couple("b", 1.0)}
    pentes = {"a": 0.02, "b": -0.01}
    propres = {code: replace(pensionne, survies=tuple(
        tuple(1.0 + pentes[code] * rang for rang in range(60)) for _ in range(5)))
        for code, pensionne in communes.items()}
    poids = {"a": 0.25, "b": 0.75}
    decalages = range(-2, 3)

    def alignes(annee: int, montant, poids_cas: dict[str, float]) -> float:
        """La somme posée à la main : l'effectif de la pyramide, réparti
        entre « a » et « b » au rythme de leur survie, rapportée à leur
        moyenne pesée."""
        total = 0.0
        for d in decalages:
            survies = {c: 1.0 + pentes[c] * (annee - 2010 - d) for c in poids_cas}
            moyenne = (sum(poids_cas[c] * survies[c] for c in poids_cas)
                       / sum(poids_cas.values()))
            total += population.effectif(annee - 1950 - d, annee) * sum(
                poids_cas[c] * montant(c, d) * survies[c] / moyenne for c in poids_cas)
        return total

    assert communes["a"].survie(0, 2030) == 1.0
    assert propres["a"].survie(0, 2005) == propres["a"].survie(0, 2010) == 1.0
    assert propres["a"].survie(-2, 2020) == pytest.approx(1.24, rel=1e-12)
    assert propres["b"].survie(-2, 2020) == pytest.approx(0.88, rel=1e-12)

    grille, sans = list(propres.values()), list(communes.values())
    servis = {d: coefficient_servi({"regime_general": 1.0}, revalorisation, 2010 + d, 2020)
              for d in decalages}
    masses, _, tetes = _masses(grille, population, 2020, poids, revalorisation)
    communes_masses, _, tetes_communes = _masses(sans, population, 2020, poids,
                                                 revalorisation)
    # Les survivants sont ceux de la pyramide ; ce qu'ils touchent ne l'est plus.
    assert tetes[TETES_TOUTES] == pytest.approx(tetes_communes[TETES_TOUTES], rel=1e-12)
    assert masses["actuel"] == pytest.approx(alignes(
        2020, lambda c, d: communes[c].pensions["actuel"] * servis[d], poids), rel=1e-12)
    for cle in ("notionnel_retroactif", "notionnel_liberal", RESSOURCES_GARANTIE):
        assert masses[cle] > 1.03 * communes_masses[cle], cle
    regimes, tetes_regimes = _masses_regimes(grille, population, 2020, poids, revalorisation)
    assert sum(tetes_regimes.values()) == pytest.approx(tetes[TETES_TOUTES], rel=1e-12)
    assert sum(regimes.values()) == pytest.approx(masses["actuel"], rel=1e-12)
    # Le calage pèse les cas types un à un, et les aligne sur toute la grille.
    un_a_un = [_masses_regimes(grille, population, 2020, {code: part}, revalorisation,
                               poids_alignement=poids)[0]["regime_general"]
               for code, part in poids.items()]
    assert sum(un_a_un) == pytest.approx(regimes["regime_general"], rel=1e-12)
    # Seul de sa grille, un cas type vit comme la pyramide.
    seul, _, _ = _masses([propres["a"]], population, 2020, {"a": 1.0}, revalorisation)
    commun, _, _ = _masses([communes["a"]], population, 2020, {"a": 1.0}, revalorisation)
    assert seul["actuel"] == pytest.approx(commun["actuel"], rel=1e-12)

    # Avant toute liquidation, la pyramide telle quelle ; après celle du droit
    # en vigueur, la proposition fait encore cotiser des survivants, et son
    # pilier sert des rentes, chacun aligné à ses poids.
    cotisants = {"a": 0.5, "b": 0.5}
    assert (_masses_cotisations(grille, population, 2005, cotisants)
            == _masses_cotisations(sans, population, 2005, cotisants))
    versees = _masses_cotisations(grille, population, 2013, cotisants)
    assert versees["notionnel_liberal"] == pytest.approx(alignes(
        2013, lambda c, d: communes[c].propre.cotisations[2013 - d], cotisants), rel=1e-12)
    assert (_masses_pilier(grille, population, 2005, cotisants, poids)
            == _masses_pilier(sans, population, 2005, cotisants, poids))
    rentes = _masses_pilier(grille, population, 2020, cotisants, poids)
    assert rentes["rentes"] == pytest.approx(alignes(
        2020, lambda c, d: communes[c].propre.rente_pilier[1], poids), rel=1e-12)


def test_la_survie_d_un_cas_type_est_celle_du_vingtile_de_son_diviseur():
    """La population qui fait vivre un cas type dans le coût est celle que son
    diviseur lui rattache par défaut : le vingtile de niveau de vie où son
    salaire le range, le quatrième pour le SMIC et le dix-neuvième pour le
    cadre (docs/methodologie.md, § 5). Sa survie se rapporte, cohorte par
    cohorte et depuis sa liquidation, à celle de la population générale,
    unisexe et par génération comme la pyramide qu'elle corrige : l'INSEE
    fait mourir le premier plus tôt, le second plus tard. Sous la table
    commune (``population_conversion=None``), la population générale. Chaque
    cohorte part l'année et à l'âge que le droit de sa génération lui donne
    (action 138, étape 3) : entré à 23 ans, le cadre de 1960 part à 64 ans et
    9 mois, en 2024, celui de 1961, à 168 trimestres au lieu de 167, à 65
    ans, en 2026."""
    from retraite_notionnelle.cout import _pensionnes

    simulateur = Simulateur(Parametres())
    mortalite = simulateur.mortalite
    par_code = {cas.code: cas for cas in CAS_TYPES}
    vingtiles = {"smic_carriere_complete": "niveau_de_vie_v04",
                 "cadre": "niveau_de_vie_v19"}
    pensionnes, _ = _pensionnes(simulateur, tuple(par_code[code] for code in vingtiles),
                                "droit")
    de_1960 = {p.code: p for p in pensionnes if p.generation == 1960}
    assert set(de_1960) == set(vingtiles)
    assert (de_1960["cadre"].liquidation(0), de_1960["cadre"].liquidation(1)) == (2024, 2026)
    for code, pensionne in de_1960.items():
        for decalage in range(-2, 3):
            depart = pensionne.liquidation(decalage)
            age = float(depart - 1960 - decalage)
            generale = mortalite.courbe(age, float(depart), None, True, None)
            propre = mortalite.courbe(age, float(depart), None, True, vingtiles[code])
            assert pensionne.survie(decalage, depart) == 1.0
            for rang in (10, 25):
                assert pensionne.survie(decalage, depart + rang) == pytest.approx(
                    propre[rang] / generale[rang], rel=1e-12), (code, decalage, rang)
    smic, cadre = de_1960["smic_carriere_complete"], de_1960["cadre"]
    assert (smic.survie(0, smic.annee_liquidation + 25) < 1.0
            < cadre.survie(0, cadre.annee_liquidation + 25))

    commune = Simulateur(replace(Parametres(), population_conversion=None))
    sans, _ = _pensionnes(commune, (par_code["cadre"],), "droit")
    assert sans and all(p.survies == () for p in sans)


def test_l_inapte_vit_au_rythme_des_inaptes_de_la_cnav():
    """L'inapte de la grille du coût ne vit pas comme le vingtile où son
    salaire le range, mais comme les retraités pour inaptitude de la Cnav, qui
    vivent quatre ans de moins que les pensions normales (Cadr'@ge n° 40 ;
    action 138, étape 7) : sa survie, cohorte par cohorte et depuis sa
    liquidation, est celle de la population ``cnav_inaptitude`` rapportée à
    la population générale, unisexe et par génération. Il meurt plus vite que
    le salarié au SMIC, le plus modeste de la grille ; son diviseur, lui,
    garde le vingtile de son salaire. Sous la table commune
    (``population_conversion=None``), la pyramide seule, comme tous."""
    from retraite_notionnelle.cout import _pensionnes

    simulateur = Simulateur(Parametres())
    mortalite = simulateur.mortalite
    smic = next(cas for cas in CAS_TYPES if cas.code == "smic_carriere_complete")
    pensionnes, _ = _pensionnes(simulateur, (smic, INAPTE_CNAV), "droit")
    de_1960 = {p.code: p for p in pensionnes if p.generation == 1960}
    inapte = de_1960[INAPTE_CNAV.code]
    for decalage in range(-2, 3):
        depart = inapte.liquidation(decalage)
        age = float(depart - 1960 - decalage)
        generale = mortalite.courbe(age, float(depart), None, True, None)
        propre = mortalite.courbe(age, float(depart), None, True, "cnav_inaptitude")
        assert inapte.survie(decalage, depart) == 1.0
        for rang in (10, 25):
            assert inapte.survie(decalage, depart + rang) == pytest.approx(
                propre[rang] / generale[rang], rel=1e-12), (decalage, rang)
    smic_1960 = de_1960["smic_carriere_complete"]
    assert (inapte.survie(0, inapte.annee_liquidation + 25)
            < smic_1960.survie(0, smic_1960.annee_liquidation + 25) < 1.0)
    assert simulateur.convertisseur.population_de(
        INAPTE_CNAV.construire(simulateur, 1960)).startswith("niveau_de_vie_v")
    commune = Simulateur(Parametres(population_conversion=None))
    pensionnes, _ = _pensionnes(commune, (INAPTE_CNAV,), "droit")
    assert pensionnes and not any(p.survies for p in pensionnes)


def test_l_ex_invalide_vit_au_rythme_des_ex_invalides_de_la_cnav():
    """L'ex-invalide de la grille du coût ne vit pas comme le vingtile où son
    salaire le range, mais comme les ex-invalides de la Cnav, qui vivent, à
    soixante-deux ans, 6,2 ans de moins que les pensions normales chez les
    hommes et 4,4 chez les femmes, quand les inaptes en vivent 4,7 et 4,1 de
    moins (Cadr'@ge n° 40 ; action 138, étape 7) : sa survie, cohorte par
    cohorte et depuis sa liquidation, est celle de la population
    ``cnav_ex_invalide`` rapportée à la population générale, unisexe et par
    génération. Parti la même année que l'inapte, au même âge, il meurt plus
    vite que lui, et l'inapte que le salarié au SMIC ; son diviseur, lui,
    garde le vingtile de son salaire. Sous la table commune
    (``population_conversion=None``), la pyramide seule, comme tous."""
    from retraite_notionnelle.cout import _pensionnes

    simulateur = Simulateur(Parametres())
    mortalite = simulateur.mortalite
    smic = next(cas for cas in CAS_TYPES if cas.code == "smic_carriere_complete")
    pensionnes, _ = _pensionnes(simulateur, (smic, INAPTE_CNAV, EX_INVALIDE_CNAV), "droit")
    de_1960 = {p.code: p for p in pensionnes if p.generation == 1960}
    ex_invalide, inapte = de_1960[EX_INVALIDE_CNAV.code], de_1960[INAPTE_CNAV.code]
    for decalage in range(-2, 3):
        depart = ex_invalide.liquidation(decalage)
        age = float(depart - 1960 - decalage)
        generale = mortalite.courbe(age, float(depart), None, True, None)
        propre = mortalite.courbe(age, float(depart), None, True, "cnav_ex_invalide")
        assert ex_invalide.survie(decalage, depart) == 1.0
        for rang in (10, 25):
            assert ex_invalide.survie(decalage, depart + rang) == pytest.approx(
                propre[rang] / generale[rang], rel=1e-12), (decalage, rang)
    smic_1960 = de_1960["smic_carriere_complete"]
    assert ex_invalide.annee_liquidation == inapte.annee_liquidation == 2022
    assert (ex_invalide.survie(0, 2047) < inapte.survie(0, 2047)
            < smic_1960.survie(0, smic_1960.annee_liquidation + 25) < 1.0)
    assert simulateur.convertisseur.population_de(
        EX_INVALIDE_CNAV.construire(simulateur, 1960)).startswith("niveau_de_vie_v")
    commune = Simulateur(Parametres(population_conversion=None))
    pensionnes, _ = _pensionnes(commune, (EX_INVALIDE_CNAV,), "droit")
    assert pensionnes and not any(p.survies for p in pensionnes)


def test_les_fonctionnaires_civils_entrent_tard_dans_leur_regime():
    """Action 147, étape 11, puis action 159, étape 5 : sous les conventions
    du COR, les deux fonctionnaires civils commencent leur carrière
    contractuels. Le sédentaire, deux ans pour la génération 1944, six pour la
    génération 1961 — ce qui sépare sa carrière, à son départ de 2004 et de
    2025, des services que le jaune pensions annexé au PLF 2027 mesure
    (tableau 95) —, douze pour la génération 2000 (six ans de services en
    moins, note 69 du rapport du COR de juin 2026), en ligne droite d'un point
    à l'autre ; l'agent de la CNRACL, six ans pour toutes les générations, le
    jaune ne mesurant ses services qu'en 2025. Ils partent au même âge, leur
    pension seule se partage ; le simulateur individuel et la page Cas types
    gardent la carrière d'un seul statut. Le sédentaire seul entrait tard,
    deux ans pour la génération 1962 et huit pour la génération 2000, jusqu'au
    14 octobre 2026."""
    from retraite_notionnelle.donnees.macro import DonneesMacro

    macro = DonneesMacro(RACINE_DONNEES)
    assert macro.delai_entree_fonction_publique(1940) == 2.0
    assert macro.delai_entree_fonction_publique(1944) == 2.0
    assert macro.delai_entree_fonction_publique(1961) == 6.0
    assert macro.delai_entree_fonction_publique(1981) == pytest.approx(6.0 + 6.0 * 20 / 39,
                                                                       rel=1e-12)
    assert macro.delai_entree_fonction_publique(2000) == 12.0
    assert macro.delai_entree_fonction_publique(2015) == 12.0
    assert {macro.delai_entree("entree_cnracl", generation)
            for generation in (1930, 1963, 2000, 2015)} == {6.0}
    assert {c.code: c.serie_entree for c in CAS_TYPES if c.affiliation_avant_entree} == {
        "fonctionnaire_sedentaire": "entree_fonction_publique",
        "fonctionnaire_actif": "entree_cnracl"}
    individuel = Simulateur(Parametres())
    projection = individuel.pour_la_projection()
    for cas in (c for c in CAS_TYPES if c.affiliation_avant_entree):
        for generation in (1945, 1980, 2000):
            seul = cas.construire(individuel, generation)
            tard = cas.construire(projection, generation)
            assert {ligne.affiliation for ligne in seul.lignes} == {cas.affiliation}
            assert tard.annee_liquidation == seul.annee_liquidation, (cas.code, generation)
            avant = [ligne for ligne in tard.lignes
                     if ligne.affiliation == "contractuel_public"]
            delai = macro.delai_entree(cas.serie_entree, generation)
            assert sum(ligne.fraction_annee for ligne in avant) == pytest.approx(
                delai, abs=1.0), (cas.code, generation)
            assert all(ligne.annee < generation + cas.age_debut + delai + 1
                       for ligne in avant)
    # Le portage JavaScript refaisait le délai et la complétude des carrières,
    # et un test l'y confrontait : ils ne servaient qu'au coût, figé depuis le
    # 11 octobre 2026 (action 150).


def test_la_page_ne_sert_pas_le_minimum_vieillesse():
    """Action 136 : le scénario 1 du simulateur sert l'ASPA aux non-salariés
    des premières générations, que leurs régimes, nés après la guerre,
    servaient mal — à l'artisan et à l'exploitant agricole nés en 1905, à
    l'exploitant né en 1920. La grille de la page Coût ne la sert pas : la
    dépense qu'elle multiplie ne compte pas le minimum vieillesse
    (``part_repartition``), et la masse du système actuel qu'elle lui oppose
    ne le compte pas davantage. Jusqu'au 11 octobre 2026, elle le comptait, et
    l'économie des années observées en était grossie."""
    from retraite_notionnelle.castypes import calculer_cas_types

    individuel = Simulateur(Parametres())
    projection = individuel.pour_la_projection()
    assert projection.pour_la_projection() is projection
    assert projection.parametres.conventions_cor
    cas_types = tuple(c for c in CAS_TYPES if c.code in ("artisan", "exploitant_agricole"))

    def servie(simulateur) -> dict:
        grille = calculer_cas_types(simulateur, cas_types, (1905, 1920))
        return {cle: sum(a.montant for a in comparaison.actuel.avantages_appliques
                         if a.code == "minimum_vieillesse")
                for cle, comparaison in grille.resultats.items()}

    assert any(servie(individuel).values())
    assert not any(servie(projection).values())


def test_les_caisses_qui_se_ferment_rendent_leur_part_au_prive():
    """L'étape 13 de l'action 147 : les exploitants agricoles, la SNCF et les
    IEG suivent, comme la fonction publique, les retraités que le COR leur
    projette ; ce que les caisses projetées perdent, les caisses reconduites
    de la grille se le partagent au prorata de leur effectif de bord, si bien
    que le total que les poids normalisent reste celui de la dernière enquête.

    Leur part de 2024, reconduite, gardait aux non-salariés une dépense qui
    doublait celle du COR en 2050, aux régimes spéciaux une dépense moitié plus
    haute, et en privait le salariat privé : la dépense des complémentaires
    finissait 7 % sous celle du COR en 2050, celle de LURA 3 % — un défaut qui
    en compensait un autre (``test_l_ecart_au_cor_groupe_par_groupe``).
    """
    effectifs = EffectifsRetraites(RACINE_DONNEES)
    grille = EffectifsRetraites.CAISSES_DE_LA_GRILLE
    assert set(grille) == {caisse for cas in CAS_TYPES for caisse in cas.caisses}
    assert {"msa_exploitants", "sncf", "cnieg"} <= set(effectifs.projetees)
    # La dernière année de l'enquête : au-delà, tout est estimé.
    bord = max(annee for annee in range(2000, 2071)
               if effectifs.fiabilite("cnav", annee) != Fiabilite.ESTIMEE)
    assert bord >= 2024

    def total(annee: int) -> float:
        return sum(effectifs.effectif(caisse, annee) for caisse in grille)

    for annee in (2025, 2040, 2070, 2080):
        assert total(annee) == pytest.approx(total(bord), rel=1e-12), annee
    reconduites = [caisse for caisse in grille if caisse not in effectifs.projetees]
    for annee in (2040, 2070):
        partages = [effectifs.effectif(caisse, annee) / effectifs.effectif(caisse, bord)
                    for caisse in reconduites]
        assert max(partages) == pytest.approx(min(partages), rel=1e-12), annee
        assert min(partages) > 1.0, annee
    poids_bord, poids_2070 = poids_effectifs(effectifs, bord), poids_effectifs(effectifs, 2070)
    assert poids_2070["exploitant_agricole"] < 0.5 * poids_bord["exploitant_agricole"]
    assert poids_2070["agent_sncf_conduite"] < 0.5 * poids_bord["agent_sncf_conduite"]
    assert poids_2070["salaire_moyen"] > poids_bord["salaire_moyen"]


def test_la_masse_se_decompose_regime_par_regime(avenir):
    """Les masses par régime de :attr:`AvenirAnnuel.masses_regimes` refont la
    base du modèle, et chaque régime qui sert une pension projetée est dans un
    groupe du COR, ou déclaré hors de tous.

    Une part de pension qui tomberait hors des groupes fausserait leur
    confrontation au COR sans bruit : c'est ce que ce test empêche.
    """
    dans_un_groupe = {regime for regimes in GROUPES_DU_MODELE.values() for regime in regimes}
    for ligne in avenir.projetees():
        assert set(ligne.masses_regimes) <= dans_un_groupe | set(REGIMES_HORS_GROUPES), (
            ligne.annee, sorted(set(ligne.masses_regimes) - dans_un_groupe))
        somme = sum(masse for regime, masse in ligne.masses_regimes.items()
                    if regime in dans_un_groupe)
        # Au cent-millième : les non-salariés des premières générations ont
        # une part de pension servie par des régimes disparus que la grille ne
        # détaille pas — 3 millionièmes de la masse en 2025, rien après. La
        # base porte la réversion, que les masses par régime n'ont pas. Le
        # RAFP, hors répartition, n'est pas dans la pension du scénario 1 :
        # sa part s'y ajoute, et la somme ne le compte pas.
        assert somme == pytest.approx(ligne.base_modele / ligne.facteur_reversion,
                                      rel=1e-5), ligne.annee


def test_la_projection_suit_le_cor_groupe_par_groupe(avenir, comptes):
    """Groupe de régimes par groupe, ce que la projection suit du COR.

    La Cnav garde sa pension moyenne relative, au COR comme dans le modèle ;
    la dépense de LURA, rapportée au PIB, se suit à quelques pour cent, et
    celle des complémentaires depuis que l'Agirc-Arrco compte ses points au
    taux moyen des entreprises (action 147, étape 10). L'écart de la pension
    moyenne relative de l'ensemble
    (``test_la_pension_moyenne_relative_s_ecarte_de_celle_du_cor``) n'est donc
    ni dans le régime général ni dans les complémentaires du privé.
    """
    ecarts = _ecarts_par_groupe(avenir, comptes)
    for cle, tolerance in DECOMPOSITION_GROUPES_SUIVIS.items():
        assert abs(ecarts[cle]) <= tolerance, (
            f"{cle} : {ecarts[cle]:+.1%} du COR à l'horizon, tolérance {tolerance:.0%}")


def test_l_ecart_au_cor_groupe_par_groupe(avenir, comptes):
    """Ce que la projection ne suit pas encore du COR, groupe par groupe.

    Deux mesures, qui ne disent pas la même chose. La PENSION MOYENNE RELATIVE
    d'un régime (figure 2.7 du COR) divise sa masse par ses retraités, et un
    retraité de régime n'est pas une personne : le COR fait croître ceux de
    l'Agirc-Arrco d'un tiers de plus que ceux de la Cnav, ce que la grille,
    dont chaque carrière du privé a les deux, ne peut pas faire ; l'écart de
    sa pension moyenne (+46 %, +24 % depuis l'étape 10, qui compte ses points
    au taux moyen des entreprises) est donc pour l'essentiel un écart de têtes.
    La DÉPENSE EN PART DE PIB (figure 2.6) ne dépend pas de ce compte : c'est
    elle qui dit ce que chaque groupe pèse dans l'écart. Il était dans la
    fonction publique d'État, où le COR fait baisser la pension relative par
    la proratisation (des entrées plus tardives, six ans de services en moins
    jusqu'à la génération 2000) : ses effectifs, la grille les suit depuis
    l'étape 9 de l'action 147, le décrochage de son traitement depuis 2019, et
    ses entrées tardives depuis l'étape 11, si bien qu'il n'en reste que sa
    dépense, que le COR compte réversion comprise. Il est surtout dans les
    régimes qui se ferment ou s'éteignent — non-salariés agricoles, régimes
    spéciaux —, que la grille pèse aux effectifs de 2024.

    Des CLIQUETS : un écart qui passe d'un point sous le sien demande de
    l'abaisser.
    """
    ecarts = _ecarts_par_groupe(avenir, comptes)
    for cle, cliquet in DECOMPOSITION_GROUPES_CLIQUETS.items():
        assert abs(ecarts[cle]) <= cliquet, (
            f"{cle} : {ecarts[cle]:+.1%} du COR à l'horizon, cliquet {cliquet:.0%}")
        assert abs(ecarts[cle]) > cliquet - 0.01, (
            f"{cle} : {ecarts[cle]:+.1%}, l'écart a baissé : abaisser le cliquet "
            f"à {math.ceil(abs(ecarts[cle]) * 100) / 100:.2f}")


def test_la_derive_mesure_l_ecart_de_la_masse_du_modele_au_cor(avenir, comptes):
    """La dérive d'une année projetée est la croissance de la masse que le
    modèle se donne, rapportée à celle de la dépense du COR, depuis la première
    année projetée : un à cette jonction et sur les années publiées. Elle
    valait 1,203 en 2070 le 5 octobre 2026, le modèle ne faisant pas reculer sa
    pension moyenne comme le COR ; elle passe sous un, de peu, de 2031 à 2067
    depuis le 6 octobre (action 147, étape 11), de 2031 à 2058 depuis que les
    régimes qui se ferment rendent leur part au privé (étape 13), de 2031 à
    l'horizon depuis que chaque génération pèse sa durée validée (étape 14).
    """
    jonction = avenir.annee(avenir.premiere_annee_projetee)
    assert jonction.derive == 1.0
    for ligne in avenir.annees:
        if not ligne.projete:
            assert ligne.derive == 1.0, ligne.annee
            continue
        attendue = (ligne.base_modele / ligne.base) / (jonction.base_modele / jonction.base)
        assert ligne.derive == pytest.approx(attendue, rel=1e-12), ligne.annee
    horizon = avenir.annee(avenir.derniere_annee)
    # 1,200 jusqu'à l'étape 4 de l'action 147, 1,174 jusqu'à l'étape 8, qui
    # corrige deux écarts de comptabilité à la dépense du COR — la part de la
    # réversion, l'ancrage unique — et la ramène à 1,097, puis 1,080 à l'étape
    # 9, la fonction publique suivant les retraités et le traitement indiciaire
    # du COR, puis 1,039 à l'étape 10, l'Agirc-Arrco comptant ses points au taux
    # moyen des entreprises, puis 1,008 à l'étape 11, la masse de chaque
    # génération portant ses arrivées tardives, puis 1,028 à l'étape 13, les
    # exploitants agricoles, la SNCF et les IEG rendant au privé, mieux payé,
    # la part que le COR leur retire — ce que les carrières incomplètes des
    # natifs, plus courtes à chaque génération, doivent reprendre — et
    # reprennent à l'étape 14 : 0,999, puis 1,008, et 1,033 à l'étape 19, le
    # scénario 1 servant les revalorisations de son droit : son stock de 2025,
    # érodé, pèse moins dans l'ancrage, et la masse du modèle remonte sur
    # celle du COR quand il s'éteint. Puis 1,050 le 18 octobre 2026, chaque
    # cohorte de la grille partant l'année que le droit de sa génération lui
    # donne (action 138, étape 3) : en 2025, d'où la dérive se compte, la
    # grille comptait 0,25 million de retraités partis un an trop tôt, et la
    # masse d'où elle part en était grossie. Puis 1,057 le 24 octobre, et
    # 1,060 le même jour, chaque caisse se divisant par les têtes de ses cas
    # types (action 138, étape 3) : les régimes spéciaux suivent les retraités
    # que le COR leur projette, leur dépense passant de -32,5 à -4,5 % de la
    # sienne, et les non-salariés et les complémentaires, dont des caisses sont
    # reconduites, s'en écartent un peu plus (``DECOMPOSITION_GROUPES_SUIVIS``) :
    # le premier défaut compensait les seconds. Un écart à un de plus de six
    # points et demi dirait qu'un défaut est revenu.
    assert 0.99 < horizon.derive < 1.065, horizon.derive
    # Les arrivées tardives et les carrières incomplètes des natifs pèsent dès
    # 2035 : la dérive passe sous un, au plus bas à 0,975 en 2054 (0,977 avant
    # l'étape 13, quand les régimes qui se ferment privaient le privé de leur
    # part, et 0,985 en 2034 avant l'étape 14). Depuis l'étape 19, elle reste
    # au-dessus de 0,99 et monte à 1,033 à l'horizon, 1,050 depuis le 18
    # octobre 2026, 1,060 depuis le 24. Une dérive qui s'en écarterait de plus
    # de 6,5 % dirait un défaut, non un écart d'hypothèses.
    for ligne in avenir.projetees():
        assert 0.97 < ligne.derive < 1.065, (ligne.annee, ligne.derive)


def test_la_borne_haute_ne_touche_que_les_systemes_notionnels(cout):
    """La fourchette ne déplace ni le système actuel, dont le rapport vaut un,
    ni la garantie, lue sur la distribution des pensions ; elle multiplie la
    dépense de chaque système notionnel par la dérive de l'année, et déplace
    d'autant la dette de la proposition."""
    for haute, basse in zip(cout.solde_derive.annees, cout.solde.annees):
        assert haute.annee == basse.annee
        assert haute.solde("actuel") == pytest.approx(basse.solde("actuel"), rel=1e-12)
        assert haute.depense(COMPOSANTE_GARANTIE) == pytest.approx(
            basse.depense(COMPOSANTE_GARANTIE), rel=1e-12)
        derive = cout.avenir.annee(haute.annee).derive
        assert haute.rapports["notionnel_liberal"] == pytest.approx(
            basse.rapports["notionnel_liberal"] * derive, rel=1e-12)
    assert cout.dette_derive.horizon("actuel") == pytest.approx(
        cout.dette.horizon("actuel"), rel=1e-12)
    # Dix points de PIB de plus jusqu'à l'étape 10 de l'action 147, un et demi
    # jusqu'à l'étape 11, la dérive de 2070 y tombant de 8 à 4 %. Depuis, la
    # dérive passe sous un au milieu de la période, et la seconde lecture
    # ALLÈGE la dette de la proposition : de huit points jusqu'à l'étape 12,
    # d'un à l'étape 13, la dérive repassant au-dessus d'un après 2058, de sept
    # depuis l'étape 14, qui la tient sous un de 2031 à l'horizon, de deux
    # depuis l'étape 5 de l'action 159, qui recale les fonctionnaires civils
    # sur le jaune pensions et rapproche la masse du modèle de la dépense du
    # COR. Depuis l'étape 19 de l'action 147, le scénario 1 servant les
    # revalorisations de son droit, la dérive repasse au-dessus d'un après
    # 2027, et la seconde lecture ALOURDIT la dette de sept points ; de cinq
    # depuis les civils de l'État pesés sur leurs départs actifs (action 138,
    # étape 3) ; de seize depuis que chaque cohorte de la grille part l'année
    # du droit de sa génération (même étape, 18 octobre 2026), la dérive de
    # 2070 passant de 1,033 à 1,050. Les deux lectures encadrent encore la
    # vérité.
    ecart = cout.dette_derive.horizon("notionnel_liberal") - cout.dette.horizon(
        "notionnel_liberal")
    assert 0.12 < ecart < 0.20, ecart


def test_le_pib_projete_croit_moins_vite_que_l_hypothese_nominale(avenir):
    """Le PIB suit le rythme nominal du COR CORRIGÉ de la population d'âge
    actif, qui recule. Il doit donc croître moins vite que l'hypothèse brute —
    faute de quoi la correction n'aurait pas été appliquée."""
    depart = avenir.annee(avenir.premiere_annee_projetee - 1)
    fin = avenir.annee(avenir.derniere_annee)
    annees = fin.annee - depart.annee
    croissance = (fin.pib / depart.pib) ** (1 / annees) - 1
    assert 0.0 < croissance < 0.0245


def test_le_cumul_projete_ne_porte_que_sur_l_avenir(avenir):
    assert all(ligne.projete for ligne in avenir.projetees())
    assert len(avenir.projetees()) == (
        avenir.derniere_annee - avenir.premiere_annee_projetee + 1
    )
    for scenario, _ in SCENARIOS:
        assert avenir.cumul(scenario) > 0


def test_une_reforme_prospective_economise_moins_qu_un_contrefactuel(avenir):
    """Le scénario 3 conserve les droits acquis, le scénario 2 non : le premier
    ne peut pas économiser autant que le second, jamais."""
    assert avenir.ecart_cumule("notionnel_prospectif") < 0
    assert (avenir.ecart_cumule("notionnel_prospectif")
            > avenir.ecart_cumule("notionnel_retroactif"))
    assert avenir.ecart_cumule("actuel") == 0.0


def test_la_trajectoire_ne_se_donne_jamais_pour_certifiee(avenir):
    assert avenir.fiabilite == Fiabilite.ESTIMEE


# -- la pondération des cas types --------------------------------------------


def test_chaque_cas_type_nomme_au_moins_une_caisse():
    """Un cas type sans caisse reçoit un poids nul et disparaît de l'agrégat.

    Ce serait une erreur SILENCIEUSE : la page continuerait d'afficher douze
    lignes et n'en pèserait que onze. C'est la raison d'être de ce test, et la
    raison pour laquelle ``poids_effectifs`` ne comble pas l'absence par une
    valeur par défaut.
    """
    effectifs = EffectifsRetraites(RACINE_DONNEES)
    connues = set(effectifs.caisses())
    for cas in CAS_TYPES:
        assert cas.caisses, f"{cas.code} : aucune caisse"
        for caisse in cas.caisses:
            assert caisse in connues, f"{cas.code} : caisse inconnue {caisse!r}"


def test_les_poids_somment_a_un_et_reflètent_les_effectifs():
    effectifs = EffectifsRetraites(RACINE_DONNEES)
    poids = poids_effectifs(effectifs, 2024)
    assert sum(poids.values()) == pytest.approx(1.0)
    assert all(valeur > 0 for valeur in poids.values())
    # La Cnav est partagée entre les quatre carrières du privé, qui reçoivent
    # donc le même poids ; la SNCF compte cent fois moins de retraités.
    prive = {poids[code] for code in
             ("smic_carriere_complete", "salaire_moyen", "cadre",
              "carriere_interrompue")}
    assert len(prive) == 1
    assert poids["agent_sncf_conduite"] < poids["salaire_moyen"] / 10
    assert sum(poids_egaux().values()) == pytest.approx(1.0)


def test_la_cnracl_se_partage_entre_ses_departs_actifs_et_sedentaires():
    """La CNRACL n'était pesée que sur l'agent de catégorie active, au départ
    le plus précoce de la caisse ; un départ sur cinq l'est (action 138,
    étape 3). La grille du coût la partage dans la proportion des départs du
    jaune pensions, que ce test relit ; la page Cas types, qui n'a que l'actif,
    lui donne la caisse entière."""
    lignes = {
        row["champ"]: float(row["valeur"])
        for row in csv.DictReader(
            ligne for ligne in open(RACINE_DONNEES / "reference" / "macro"
                                    / "caracteristiques_fonction_publique.csv",
                                    encoding="utf-8")
            if not ligne.startswith("#"))
        if row["tableau"] == "B-5" and row["population"] == "cnracl_total"
        and row["indicateur"] == "departs"
    }
    assert lignes == {champ: float(n) for champ, n in DEPARTS_CNRACL_2025.items()}
    assert 0.15 < PART_ACTIVE_CNRACL < 0.25
    parts = parts_des_caisses(GRILLE_DU_COUT)
    assert parts[("fonctionnaire_actif", "cnracl")] == pytest.approx(PART_ACTIVE_CNRACL)
    assert parts[(AGENT_SEDENTAIRE_CNRACL.code, "cnracl")] == pytest.approx(
        1.0 - PART_ACTIVE_CNRACL)
    assert parts_des_caisses(CAS_TYPES)[("fonctionnaire_actif", "cnracl")] == 1.0
    # La Cnav, que ses quatre carrières du privé partagent également, une fois
    # ses inaptes et ses ex-invalides servis.
    assert parts[("cadre", "cnav")] == pytest.approx(
        (1.0 - PART_INAPTES_CNAV - PART_EX_INVALIDES_CNAV) / 4)
    effectifs = EffectifsRetraites(RACINE_DONNEES)
    grille, page = poids_effectifs(effectifs, 2024, GRILLE_DU_COUT), poids_effectifs(effectifs, 2024)
    assert (grille["fonctionnaire_actif"] + grille[AGENT_SEDENTAIRE_CNRACL.code]
            == pytest.approx(page["fonctionnaire_actif"]))
    assert cas_type_affiche(AGENT_SEDENTAIRE_CNRACL.code) == "fonctionnaire_actif"
    assert AGENT_SEDENTAIRE_CNRACL not in CAS_TYPES


def test_l_inapte_porte_la_part_de_la_cnav_que_ses_departs_lui_donnent():
    """La Cnav n'avait que des pensions normales, quand un nouveau retraité du
    régime général sur douze part pour inaptitude au travail (action 138,
    étape 7). Les séries labellisées de la Cnav comptent les nouveaux retraités
    de droit direct par type de pension, que ce test relit et recoupe par
    leurs totaux publiés : les trois types font le total, et les deux sexes
    l'ensemble. De 2020 à 2024, 284 204 des 3 397 470 sont partis pour
    inaptitude, 8,4 %, et 298 196 en ex-invalides, 8,8 %. La grille du coût
    donne sa part de la caisse à l'inapte et à l'ex-invalide — leur part à la
    liquidation, leur mortalité faisant ensuite le stock —, les quatre
    carrières du privé se partageant également le reste ; la page Cas types,
    qui n'a ni l'un ni l'autre, garde le partage égal."""
    lues: dict[tuple[int, str, str, str], int] = {}
    with open(RACINE_DONNEES / "reference" / "regimes" / "nouveaux_retraites_cnav.csv",
              encoding="utf-8") as flux:
        for row in csv.DictReader(l for l in flux if not l.startswith("#")):
            lues[(int(row["annee"]), row["champ"], row["sexe"], row["type_pension"])] = (
                int(row["effectif"]))
    types = ("normale", "ex_invalide", "inaptitude")
    for annee, champ, sexe, type_pension in lues:
        if type_pension == "droits_directs":
            assert sum(lues[(annee, champ, sexe, t)] for t in types) == (
                lues[(annee, champ, sexe, type_pension)]), (annee, champ, sexe)
        if sexe == "ensemble":
            assert (lues[(annee, champ, "H", type_pension)]
                    + lues[(annee, champ, "F", type_pension)]
                    == lues[(annee, champ, sexe, type_pension)]), (annee, type_pension)
    assert {annee for annee, champ, _, _ in lues if champ == "salaries"} == set(range(2003, 2020))
    assert {annee for annee, champ, _, _ in lues
            if champ == "salaries_independants"} == set(range(2019, 2025))
    assert lues[(2024, "salaries_independants", "ensemble", "inaptitude")] == 60_468
    depuis_2020 = {t: sum(lues[(annee, "salaries_independants", "ensemble", t)]
                          for annee in range(2020, 2025))
                   for t in types + ("droits_directs",)}
    assert DEPARTS_CNAV_2020_2024 == {t: depuis_2020[t] for t in types}
    assert (depuis_2020["inaptitude"], depuis_2020["ex_invalide"]) == (284_204, 298_196)
    assert PART_INAPTES_CNAV == pytest.approx(284_204 / 3_397_470)
    assert PART_EX_INVALIDES_CNAV == pytest.approx(298_196 / 3_397_470)
    parts = parts_des_caisses(GRILLE_DU_COUT)
    assert parts[(INAPTE_CNAV.code, "cnav")] == pytest.approx(PART_INAPTES_CNAV)
    assert parts[(EX_INVALIDE_CNAV.code, "cnav")] == pytest.approx(PART_EX_INVALIDES_CNAV)
    reste = 1.0 - PART_INAPTES_CNAV - PART_EX_INVALIDES_CNAV
    page = parts_des_caisses(CAS_TYPES)
    for code in ("smic_carriere_complete", "salaire_moyen", "cadre", "carriere_interrompue"):
        assert parts[(code, "cnav")] == pytest.approx(reste / 4), code
        assert page[(code, "cnav")] == pytest.approx(0.25), code
    effectifs = EffectifsRetraites(RACINE_DONNEES)
    grille = poids_effectifs(effectifs, 2024, GRILLE_DU_COUT)
    for cas, part in ((INAPTE_CNAV, PART_INAPTES_CNAV), (EX_INVALIDE_CNAV, PART_EX_INVALIDES_CNAV)):
        assert cas_type_affiche(cas.code) == "smic_carriere_complete"
        assert cas in GRILLE_DU_COUT and cas not in CAS_TYPES
        assert grille[cas.code] == pytest.approx(part * 4 * grille["cadre"] / reste)


def test_les_civils_de_l_etat_se_partagent_entre_leurs_trois_departs():
    """Les civils de l'État n'étaient pesés que sur le sédentaire de catégorie
    B ; un départ sur cinq est actif, ouvert à cinquante-sept ou à cinquante-deux
    ans (action 138, étape 3). La grille du coût partage la caisse dans la
    proportion des départs du tableau B-4, que ce test relit, et que les
    actifs du tableau B-3 confirment ; chaque actif part au taux plein de sa
    catégorie, avant le sédentaire."""
    def departs(tableau, champs):
        return {
            row["champ"]: float(row["valeur"])
            for row in csv.DictReader(
                ligne for ligne in open(RACINE_DONNEES / "reference" / "macro"
                                        / "caracteristiques_fonction_publique.csv",
                                        encoding="utf-8")
                if not ligne.startswith("#"))
            if row["tableau"] == tableau and row["population"] == "fpe_civils"
            and row["indicateur"] == "departs" and row["champ"] in champs
        }
    lignes = departs("B-4", DEPARTS_ETAT_CIVILS_2025)
    assert lignes == {champ: float(n) for champ, n in DEPARTS_ETAT_CIVILS_2025.items()}
    b3 = departs("B-3", ("anciennete", "categorie_active"))
    assert b3["anciennete"] == sum(lignes.values())
    assert b3["categorie_active"] == lignes["active_57"] + lignes["active_52"]
    parts = parts_des_caisses(GRILLE_DU_COUT)
    caisse = "fonction_publique_etat_civile"
    assert parts[(FONCTIONNAIRE_ACTIF_ETAT.code, caisse)] == pytest.approx(PART_ACTIVE_ETAT)
    assert parts[(FONCTIONNAIRE_SUPER_ACTIF_ETAT.code, caisse)] == pytest.approx(
        PART_SUPER_ACTIVE_ETAT)
    assert parts[("fonctionnaire_sedentaire", caisse)] == pytest.approx(
        1.0 - PART_ACTIVE_ETAT - PART_SUPER_ACTIVE_ETAT)
    assert parts_des_caisses(CAS_TYPES)[("fonctionnaire_sedentaire", caisse)] == 1.0
    effectifs = EffectifsRetraites(RACINE_DONNEES)
    grille, page = poids_effectifs(effectifs, 2024, GRILLE_DU_COUT), poids_effectifs(effectifs, 2024)
    codes = ("fonctionnaire_sedentaire", FONCTIONNAIRE_ACTIF_ETAT.code,
             FONCTIONNAIRE_SUPER_ACTIF_ETAT.code)
    assert (sum(grille[code] for code in codes)
            == pytest.approx(page["fonctionnaire_sedentaire"]))
    assert {cas_type_affiche(code) for code in codes} == {"fonctionnaire_sedentaire"}
    projection = Simulateur(Parametres()).pour_la_projection()
    sedentaire = next(cas for cas in CAS_TYPES if cas.code == "fonctionnaire_sedentaire")
    ages = [cas.age_liquidation_pour(projection, 1963)
            for cas in (FONCTIONNAIRE_SUPER_ACTIF_ETAT, FONCTIONNAIRE_ACTIF_ETAT, sedentaire)]
    assert ages == sorted(ages) and ages[0] < ages[1] < ages[2]


def test_un_partage_a_demi_declare_leve():
    actif = next(cas for cas in CAS_TYPES if cas.code == "fonctionnaire_actif")
    muet = replace(AGENT_SEDENTAIRE_CNRACL, parts_caisses=())
    with pytest.raises(ValueError):
        parts_des_caisses((actif, muet))


def test_chaque_caisse_se_divise_par_les_tetes_de_ses_cas_types():
    """Le poids s'applique à chaque génération entière, et un cas type qui
    part tôt y compte plus d'années de retraite : pesé de la part de sa caisse
    dans le stock, le militaire de la grille, radié à 48 ans, faisait 29,5 %
    des retraités de l'État en 2024, pour 18,7 % (action 138, étape 3). Les
    têtes que la pyramide donne à chaque cas type pour un poids d'un, l'année
    même, divisent sa caisse ; une caisse partagée, par celles de ses cas
    types pesées de leurs parts, qui restent celles de leurs départs.

    Posé à la main : la caisse A, 300 retraités, au seul X, qui compte 1 000
    têtes ; la caisse B, 100 retraités, partagée aux trois quarts pour Y, qui
    part tôt et en compte 2 000, au quart pour Z, qui en compte 1 000. B se
    divise par 0,75 × 2 000 + 0,25 × 1 000 = 1 750 : X 0,3, Y 0,75 / 17,5,
    Z 0,25 / 17,5, soit 0,84, 0,12 et 0,04 une fois sommés à un ; la grille
    compte 840 têtes à A, 240 + 40 = 280 à B, trois fois moins, comme leurs
    retraités. Sans les têtes, la part du stock : 0,75, 0,1875, 0,0625."""
    modele = next(cas for cas in CAS_TYPES if cas.code == "salaire_moyen")
    cas_types = (replace(modele, code="X", caisses=("A",), parts_caisses=()),
                 replace(modele, code="Y", caisses=("B",), parts_caisses=(("B", 0.75),)),
                 replace(modele, code="Z", caisses=("B",), parts_caisses=(("B", 0.25),)))

    class Effectifs:
        def effectif(self, caisse: str, annee: int) -> float:
            return {"A": 300.0, "B": 100.0}[caisse]

    poids = poids_effectifs(Effectifs(), 2024, cas_types,
                            tetes={"X": 1_000.0, "Y": 2_000.0, "Z": 1_000.0})
    assert poids == pytest.approx({"X": 0.84, "Y": 0.12, "Z": 0.04})
    assert poids_effectifs(Effectifs(), 2024, cas_types) == pytest.approx(
        {"X": 0.75, "Y": 0.1875, "Z": 0.0625})
    # Une caisse dont aucun cas type n'a encore de retraité cette année-là ne
    # se divise pas par zéro : elle ne pèse rien.
    assert poids_effectifs(Effectifs(), 2024, cas_types,
                           tetes={"X": 1_000.0, "Y": 0.0, "Z": 0.0}) == pytest.approx(
        {"X": 1.0, "Y": 0.0, "Z": 0.0})


def test_les_tetes_d_un_cas_type_sont_ses_cohortes_deja_parties():
    """Ce qui divise sa caisse (``cout._tetes_par_poids``) : l'effectif que
    la pyramide donne, l'année même, à chacune de ses cohortes déjà partie,
    comme ``cout._masses`` les compte pour un poids d'un. Posé à la main, une
    pyramide de dix personnes par année d'âge : X, génération 1960, part à
    60 ans, ses cinq cohortes de 2018 à 2022 — 66 + 65 + 64 + 63 + 62 ans en
    2024, 3 200 têtes — ; sa génération 1965, à partir de 2025, aucune ; Y,
    génération 1960, part de 2021 à 2025, ses quatre premières cohortes en
    2024 — 66 + 65 + 64 + 63 ans, 2 580 têtes. Au-delà de la dernière année
    que la pyramide projette, celles de cette année-là : l'engagement acquis
    et les facteurs de la dépense demandent leurs poids jusqu'à l'horizon, et
    les effectifs des caisses y sont reconduits."""
    from types import SimpleNamespace

    from retraite_notionnelle.cout import _tetes_par_poids

    def pensionne(code: str, generation: int, premier_depart: int) -> SimpleNamespace:
        return SimpleNamespace(code=code, generation=generation,
                               liquidation=lambda decalage: premier_depart + 2 + decalage)

    class Pyramide:
        derniere_annee = 2024

        def effectif(self, age: int, annee: int) -> float:
            assert annee <= self.derniere_annee
            return 10.0 * age

    tetes = _tetes_par_poids([pensionne("X", 1960, 2018), pensionne("X", 1965, 2025),
                              pensionne("Y", 1960, 2021)], Pyramide())
    assert tetes(2024) == pytest.approx({"X": 3_200.0, "Y": 2_580.0})
    assert tetes(2071) == tetes(2024)


def test_les_poids_cotisants_somment_a_un_et_ne_sont_pas_ceux_des_retraites():
    """Le côté recette pèse les cotisants, et ce n'est pas le même poids.

    La SNCF et les IEG ont plus de retraités que de cotisants, et n'auront plus
    de cotisants du tout en 2070 ; la MSA des exploitants compte trois fois
    plus de retraités que de cotisants. Les peser par leurs retraités du côté
    de la recette était le biais que `limites.md` décrivait.
    """
    cotisants = EffectifsCotisants(RACINE_DONNEES)
    retraites = EffectifsRetraites(RACINE_DONNEES)
    poids = poids_effectifs(cotisants, 2024)
    reference = poids_effectifs(retraites, 2024)
    assert sum(poids.values()) == pytest.approx(1.0)
    assert all(valeur > 0 for valeur in poids.values())
    for code in ("agent_sncf_conduite", "agent_ieg", "exploitant_agricole"):
        assert poids[code] < reference[code]
    # Les régimes fermés par la réforme de 2023 s'éteignent dans la projection,
    # ce qu'aucune reconduction de retraités n'imite.
    assert cotisants.effectif("sncf", 2070) == 0.0
    assert cotisants.effectif("sncf", 2024) > 100_000
    # La fonction publique d'État, d'un seul tenant chez le COR, est partagée
    # entre civils et militaires à la clé du jaune budgétaire, et la clé se lit
    # dans les poids : le militaire pèse ce que le sédentaire pèse, fois le
    # rapport des deux effectifs de fin 2025.
    attendu = (COTISANTS_ETAT_2025["fonction_publique_etat_militaire"]
               / COTISANTS_ETAT_2025["fonction_publique_etat_civile"])
    assert poids["militaire"] / poids["fonctionnaire_sedentaire"] == pytest.approx(attendu)
    assert (cotisants.effectif("fonction_publique_etat_civile", 2030)
            + cotisants.effectif("fonction_publique_etat_militaire", 2030)
            == pytest.approx(cotisants.effectif("fonction_publique_etat", 2030)))
    assert cotisants.fiabilite("fonction_publique_etat", 2030) == Fiabilite.HAUTE
    assert cotisants.fiabilite("fonction_publique_etat_civile", 2030) == Fiabilite.ESTIMEE


def test_la_recette_pese_les_cotisants_et_la_depense_les_retraites(cout: Cout):
    """Chaque côté du bilan a son poids, et le rapport de recettes s'en ressent.

    Peser la recette par les retraités surreprésentait les régimes qui
    s'éteignent, dont les taux sont les plus élevés, et poussait le rapport
    vers le bas — d'où un taux moyen implicite de 29,5 % là où le COR publie
    27,9 % pour un salarié du privé. Les cotisants le ramènent à 28 %.
    """
    assert sum(cout.poids_cotisants.values()) == pytest.approx(1.0)
    assert cout.poids_cotisants != cout.poids
    assert cout.poids_cotisants["agent_sncf_conduite"] < cout.poids["agent_sncf_conduite"]

    # L'ancienne convention, reproduite : les retraités des deux côtés, à la
    # répartition de la dernière enquête — la fonction publique ne suivait pas
    # encore ceux que le COR lui projette (action 147, étape 9). Sur un
    # simulateur retouché, que la clé du coût ne décrit pas : le calcul se
    # garde sous la sienne, et retouche lui-même un simulateur neuf.
    def ancienne_convention():
        simulateur = Simulateur(Parametres())
        simulateur.__dict__["cotisants"] = EffectifsRetraites(RACINE_DONNEES, projetees=())
        return calculer_cout(simulateur, DepensesRetraite(RACINE_DONNEES),
                             Population(RACINE_DONNEES), ComptesRetraite(RACINE_DONNEES),
                             convention_recette=CONVENTION_RAPPORT)

    ancien = memoire.memoriser_pour(
        Parametres(), ("cout_retraites_des_deux_cotes", Parametres(), CONVENTION_RAPPORT),
        ancienne_convention)
    # Les cotisants y pèsent la part de chaque caisse dans le stock des
    # retraités, sans les têtes qui divisent les caisses des pensions ni leur
    # calage sur la dépense de chaque groupe du COR (action 138, étape 3).
    assert ancien.poids_cotisants == poids_effectifs(
        EffectifsRetraites(RACINE_DONNEES), DepensesRetraite(RACINE_DONNEES).derniere_annee,
        GRILLE_DU_COUT)
    for annee in (2030, 2050, 2070):
        ligne = cout.avenir.annee(annee)
        nouveau = ligne.rapports_recettes["notionnel_liberal"]
        vieux = ancien.avenir.annee(annee).rapports_recettes["notionnel_liberal"]
        assert nouveau > vieux
        # Le taux implicite du droit en vigueur, à assiette égale : le rapport
        # de recettes porte aussi l'emploi que l'âge légal de la proposition
        # ajoute, et le facteur d'assiette le lui retire.
        assert 0.27 < 0.18 * ligne.facteur_assiette_liberal / nouveau < 0.29
    # Sous la convention `rapport`, le solde du scénario 6 en profite ; les
    # autres scénarios, dont le rapport vaut un, ne bougent pas.
    assert (cout.solde.solde_moyen("notionnel_liberal", 2026, 2070)
            > ancien.solde.solde_moyen("notionnel_liberal", 2026, 2070))
    assert (cout.solde.solde_moyen("actuel", 2026, 2070)
            == pytest.approx(ancien.solde.solde_moyen("actuel", 2026, 2070)))


def test_un_cote_de_ponderation_inconnu_est_refuse():
    with pytest.raises(ValueError, match="côté inconnu"):
        _ponderation(Simulateur(Parametres()), "effectifs", CAS_TYPES, "ni_l_un_ni_l_autre")


def test_la_ponderation_egale_reproduit_l_ancienne_convention():
    """Un poids uniforme se simplifie dans le rapport des masses.

    C'est ce qui rend la variante utilisable comme TÉMOIN : si elle ne rendait
    pas exactement ce que rendait le dépôt avant la pondération, elle ne dirait
    rien de ce que celle-ci a déplacé.
    """
    egale = memoire.cout(Parametres(), comptes=False, assiette=False, ponderation="egale")
    assert egale.ponderation == "egale"
    assert all(poids == pytest.approx(1 / len(GRILLE_DU_COUT))
               for poids in egale.poids.values())
    assert egale.poids_cotisants == egale.poids
    # Les deux pondérations ne donnent pas le même rapport — sans quoi l'action
    # n'aurait rien déplacé. L'égale, qui surreprésente les départs très
    # précoces, que le compte notionnel ampute le plus, en fait un plancher, que
    # la part patronale entre au compte ou non : de peu au scénario 2, 0,199
    # pour 0,201, les carrières du privé, que le compte salarial seul pénalise
    # davantage encore, pesant plus aux effectifs. Elle en faisait un plafond,
    # 0,199 pour 0,195, jusqu'au 24 octobre 2026, quand la part de chaque caisse
    # dans le stock, appliquée à chaque génération, donnait encore aux départs
    # précoces les années de retraite qu'ils ont de plus (action 138, étape 3).
    reference = memoire.cout(Parametres(), comptes=False, assiette=False)
    assert (reference.cumul("notionnel_retroactif") / reference.cumul("actuel")
            > egale.cumul("notionnel_retroactif") / egale.cumul("actuel"))
    assert (reference.cumul("notionnel_retroactif_employeur")
            / reference.cumul("actuel")
            > egale.cumul("notionnel_retroactif_employeur") / egale.cumul("actuel"))


def test_une_ponderation_inconnue_est_refusee(depenses, population):
    with pytest.raises(ValueError, match="pondération inconnue"):
        calculer_cout(Simulateur(Parametres()), depenses, population,
                      ponderation="au_hasard")


# -- l'engagement acquis -------------------------------------------------------


def test_chaque_systeme_revalorise_ce_qu_il_sert_selon_sa_regle():
    """Le système actuel sur les prix, les notionnels sur la règle du compte."""
    assert regle_revalorisation("actuel") == REGLE_PRIX
    for cle, _ in SCENARIOS:
        if cle == "actuel":
            continue
        attendue = REGLE_PROSPECTIVE if cle in CLES_PROSPECTIVES else REGLE_STOCK
        assert regle_revalorisation(cle) == attendue, cle


def test_l_engagement_revalorise_comme_les_masses(depenses, population, monkeypatch):
    """L'engagement acquis revalorise ce qu'un système sert comme ses masses.

    Le système actuel est indexé sur les prix : en euros constants, une pension
    servie n'y bouge pas, et l'ancrage qui convertit ses masses en euros le
    suppose. Jusqu'au 23 septembre 2026, l'engagement le revalorisait pourtant
    sur la règle notionnelle, et le grossissait d'un dixième. On DOUBLE ici la
    règle notionnelle : l'engagement du système actuel ne doit pas bouger, celui
    d'un système notionnel, rétroactif ou prospectif, doit doubler exactement.
    Deux cas types suffisent, la règle ne dépend pas de la carrière.
    """
    simulateur = Simulateur(Parametres())
    cas = CAS_TYPES[:2]
    scenarios = ["actuel", "notionnel_liberal", *sorted(CLES_PROSPECTIVES)[:1]]
    reference = calculer_engagements(simulateur, depenses, population, 2021,
                                     scenarios, cas_types=cas)
    regle = RevalorisationServie.coefficient_stock
    monkeypatch.setattr(
        RevalorisationServie, "coefficient_stock",
        lambda soi, liquidation, annee, prospectif:
            2.0 * regle(soi, liquidation, annee, prospectif),
    )
    double = calculer_engagements(simulateur, depenses, population, 2021,
                                  scenarios, cas_types=cas)
    assert double.part_pib("actuel") == pytest.approx(
        reference.part_pib("actuel"), rel=1e-12)
    for cle in scenarios[1:]:
        assert double.part_pib(cle) == pytest.approx(
            2.0 * reference.part_pib(cle), rel=1e-12), cle


def test_l_engagement_compte_les_survivants_de_chaque_population(depenses, population,
                                                                  monkeypatch):
    """L'engagement acquis est la somme des masses à venir : il compte, comme
    elles, les survivants de chaque cohorte au rythme de sa population, à
    nombre de décès égal (``Pensionne.survie``, action 138, étape 7). Une
    survie divisée par deux pour tous, à partir de 2030, ne change rien : la
    pyramide garde ses morts. Pour le seul salarié au SMIC, elle reporte ses
    survivants sur le salarié moyen, dont la pension est plus haute :
    l'engagement monte dans chaque système, au-delà de la pyramide aussi."""
    from retraite_notionnelle.cout import Pensionne

    simulateur = Simulateur(Parametres())
    cas = CAS_TYPES[:2]
    assert [c.code for c in cas] == ["smic_carriere_complete", "salaire_moyen"]
    scenarios = ["actuel", "notionnel_liberal"]
    reference = calculer_engagements(simulateur, depenses, population, 2021,
                                     scenarios, cas_types=cas)
    survie = Pensionne.survie

    def engagement(qui):
        monkeypatch.setattr(
            Pensionne, "survie",
            lambda soi, decalage, annee: survie(soi, decalage, annee)
            * (0.5 if annee >= 2030 and qui(soi.code) else 1.0))
        return calculer_engagements(simulateur, depenses, population, 2021,
                                    scenarios, cas_types=cas)

    tous = engagement(lambda code: True)
    smic = engagement(lambda code: code == "smic_carriere_complete")
    assert reference.hors_projection > 0.0
    for cle in scenarios:
        assert tous.part_pib(cle) == pytest.approx(reference.part_pib(cle), rel=1e-12), cle
        assert smic.part_pib(cle) > 1.01 * reference.part_pib(cle), cle
    assert tous.hors_projection == pytest.approx(reference.hors_projection, rel=1e-12)
    assert smic.hors_projection > reference.hors_projection


# -- l'âge auquel chaque cas type liquide ------------------------------------


def test_chaque_generation_liquide_sous_son_propre_droit():
    """Le défaut que l'action 8 corrige, et ce qu'il faut pour qu'il le reste.

    Un cas type ne porte plus un âge mais une RÈGLE. Le contrôle est celui
    qu'aucun nombre écrit à la main ne passerait : l'âge du salarié au salaire
    moyen doit MONTER d'une génération à la suivante, parce que les deux lois
    qui l'ont déplacé — 2010 puis 2023 — n'ont fait que le relever, et il doit
    rester sous celui du cadre, qui entre deux ans plus tard dans la vie active
    et met donc deux ans de plus à réunir sa durée.
    """
    simulateur = Simulateur(Parametres())
    par_code = {cas.code: cas for cas in CAS_TYPES}
    ages = {
        code: [par_code[code].age_liquidation_pour(simulateur, generation)
               for generation in GENERATIONS]
        for code in ("salaire_moyen", "cadre", "fonctionnaire_actif")
    }
    for code, serie in ages.items():
        assert serie == sorted(serie), f"{code} : {serie}"
        assert serie[0] < serie[-1], f"{code} : {serie}"
    for moyen, cadre in zip(ages["salaire_moyen"], ages["cadre"]):
        assert moyen < cadre
    # La catégorie active part avant le droit commun, à toutes les générations :
    # c'est ce que le classement de l'emploi lui ouvre, et le cas type n'existe
    # que pour le montrer.
    for actif, moyen in zip(ages["fonctionnaire_actif"], ages["salaire_moyen"]):
        assert actif < moyen


def test_le_militaire_part_a_une_duree_et_non_a_un_age():
    """L. 24, II : la pension militaire s'ouvre à une durée de services. Son âge
    de départ ne bouge donc d'aucune génération, et c'est un résultat et non un
    oubli — la règle du cas type le dit en toutes lettres."""
    simulateur = Simulateur(Parametres())
    militaire = next(cas for cas in CAS_TYPES if cas.code == "militaire")
    assert militaire.regle_liquidation == "services"
    ages = {militaire.age_liquidation_pour(simulateur, generation)
            for generation in GENERATIONS}
    assert ages == {militaire.age_debut + militaire.ecart_liquidation}


def test_un_regime_ferme_rend_ses_generations_au_droit_commun():
    """La conséquence la moins attendue de la règle, et la plus juste.

    La SNCF n'embauche plus au statut depuis 2020 : la génération 2000, entrée
    après, n'a pas de régime spécial et ne peut donc pas partir à cinquante-deux
    ans. L'âge écrit l'y faisait partir quand même — une pension que le droit
    n'ouvrait à personne. La règle lit la fermeture dans le catalogue et rend
    cette génération au régime général.
    """
    simulateur = Simulateur(Parametres())
    sncf = next(cas for cas in CAS_TYPES if cas.code == "agent_sncf_conduite")
    moyen = next(cas for cas in CAS_TYPES if cas.code == "salaire_moyen")
    assert sncf.age_liquidation_pour(simulateur, 1960) < 55
    # Même âge qu'un salarié du privé entré comme lui à vingt ans : c'est
    # soixante-trois ans, par la porte des vingt et un ans de la carrière
    # longue, et non les soixante-quatre du salarié entré à vingt et un.
    entre_a_vingt = replace(moyen, age_debut=sncf.age_debut)
    assert (sncf.age_liquidation_pour(simulateur, 2000)
            == entre_a_vingt.age_liquidation_pour(simulateur, 2000)
            == pytest.approx(63.0))
    assert moyen.age_liquidation_pour(simulateur, 2000) == pytest.approx(64.0)
    # La variante garde l'ancien comportement intact : c'est à cela qu'elle sert.
    assert sncf.age_liquidation_pour(simulateur, 2000, "absolu") == 52


def test_la_carriere_longue_date_le_depart_du_cas_type_qui_y_a_droit():
    """Le salarié au SMIC entre à dix-huit ans : le droit lui ouvre un départ
    anticipé AU TAUX PLEIN, à soixante ans sous le décret de 2012, puis à l'âge
    que sa génération tire de l'article D. 351-1-1. La règle le lui proposait à l'âge légal,
    faisant attendre celui-là même que la loi en dispense ; elle propose
    maintenant l'âge que `calculer` confirme, et sous le motif qui le dit."""
    simulateur = Simulateur(Parametres())
    actuel = simulateur.scenario_actuel
    smic = next(cas for cas in CAS_TYPES if cas.code == "smic_carriere_complete")
    # 60 ans sous le décret de 2012, 62 ans à compter de 1971. La génération
    # 1965 aurait 60 ans et 9 mois sous la règle de septembre 2026 — mais cet
    # âge tombe en octobre 2025, quand la loi de 2023 exige encore 172
    # trimestres, que le salarié entré à dix-huit ans n'a qu'en janvier 2026 :
    # 61 ans. Le test attendait 60 ans et 9 mois, sous une règle pas encore
    # applicable à cette date.
    for generation, attendu in ((1955, 60.0), (1960, 60.0), (1965, 61.0), (1975, 62.0)):
        assert smic.age_liquidation_pour(simulateur, generation) == pytest.approx(attendu)
        resultat = actuel.calculer(smic.construire(simulateur, generation))
        assert resultat.liquidation_ouverte
        assert resultat.motif_ouverture == "carriere_longue"
        assert resultat.taux_liquidation == pytest.approx(0.5)


def test_les_trimestres_pour_enfants_datent_le_taux_plein():
    """La mère de deux enfants a sa durée dès l'âge légal grâce à la majoration
    de durée d'assurance. La règle ne comptait que les trimestres des lignes de
    carrière et la datait jusqu'à trois ans plus tard, en surcote : elle part
    maintenant à l'âge d'ouverture, au taux plein exactement — ni décote, ni
    surcote —, et un trimestre plus tôt le droit ne l'ouvrirait pas."""
    simulateur = Simulateur(Parametres())
    actuel = simulateur.scenario_actuel
    cas = next(c for c in CAS_TYPES if c.code == "carriere_interrompue")
    assert cas.nombre_enfants == 2
    for generation in (1950, 1960, 1965, 1975):
        age = cas.age_liquidation_pour(simulateur, generation)
        carriere = cas.construire(simulateur, generation)
        assert age == pytest.approx(ouvrir.age_ouverture_droit(actuel, carriere))
        resultat = actuel.calculer(carriere)
        assert resultat.liquidation_ouverte
        assert resultat.taux_liquidation == pytest.approx(0.5)
        assert resultat.trimestres_valides >= resultat.trimestres_requis
        plus_tot = actuel.calculer(cas._carriere(simulateur, generation, age - 0.25))
        assert not plus_tot.liquidation_ouverte


def test_la_variante_absolue_reproduit_l_ancienne_grille():
    """L'âge écrit reste disponible, non comme repli mais comme témoin.

    Sans lui, ce que la règle déplace ne se mesurerait pas : il faudrait le
    croire. Le contrôle fige les deux bouts — la variante rend exactement les
    âges écrits, et la trajectoire qu'elle produit n'est pas celle de la règle.
    """
    simulateur = Simulateur(Parametres())
    for cas in CAS_TYPES:
        for generation in GENERATIONS:
            assert (cas.age_liquidation_pour(simulateur, generation, "absolu")
                    == cas.age_liquidation)
    absolu = memoire.cout(Parametres(), comptes=False, assiette=False, liquidation="absolu")
    droit = memoire.cout(Parametres(), comptes=False, assiette=False)
    assert absolu.liquidation == "absolu"
    assert droit.liquidation == "droit"
    # La dépense OBSERVÉE est la même des deux côtés — c'est la série de la
    # DREES, que rien du modèle ne déplace. Ce que la règle déplace est la
    # projection, qui est celle du modèle : elle finit un point de PIB plus
    # haut, et `limites.md` §5 ter dit pourquoi.
    assert absolu.cumul("actuel") == droit.cumul("actuel")
    fin_absolu = absolu.avenir.annee(absolu.avenir.derniere_annee)
    fin_droit = droit.avenir.annee(droit.avenir.derniere_annee)
    assert fin_droit.part_pib("actuel") > fin_absolu.part_pib("actuel")


def test_une_variante_de_liquidation_inconnue_est_refusee(depenses, population):
    with pytest.raises(ValueError, match="variante de liquidation inconnue"):
        calculer_cout(Simulateur(Parametres()), depenses, population,
                      liquidation="au_hasard")


def test_la_page_cout_suit_l_hypothese_d_esperance_de_vie(depenses):
    """Sous l'hypothèse d'espérance de vie basse ou haute (action 138, étape
    7), la page compte ses retraités dans la pyramide de la même hypothèse,
    et la dépense du COR suit ce que cette pyramide change à la masse du
    système actuel : un et quart à un et un tiers de point de PIB en 2070,
    dans les deux sens, l'ordre de grandeur que le COR publie. La
    proposition, dont le diviseur absorbe la longévité, bouge vingt fois
    moins, en dépense comme en solde. Rien ne bouge avant 2026 ; et une
    pyramide d'une autre hypothèse que le simulateur est refusée."""
    couts = {h: memoire.cout(Parametres(hypothese_esperance_vie=h))
             for h in ("basse", "centrale", "haute")}
    fins = {h: {a.annee: a for a in c.avenir.annees} for h, c in couts.items()}
    soldes = {h: {s.annee: s for s in c.solde.annees} for h, c in couts.items()}
    for annee in (2010, 2024):
        assert len({fins[h][annee].part_pib("actuel") for h in fins}) == 1
        assert {fins[h][annee].facteur_pyramide for h in fins} == {1.0}
    assert {a.facteur_pyramide for a in fins["centrale"].values()} == {1.0}
    assert {a.facteur_pib for a in fins["centrale"].values()} == {1.0}
    actuel = {h: fins[h][2070].part_pib("actuel") for h in fins}
    liberal = {h: fins[h][2070].part_pib("notionnel_liberal") for h in fins}
    assert actuel["basse"] < actuel["centrale"] < actuel["haute"]
    for h in ("basse", "haute"):
        assert 0.010 < abs(actuel[h] - actuel["centrale"]) < 0.016, h
        assert abs(liberal[h] - liberal["centrale"]) < 0.001, h
        assert abs(soldes[h][2070].solde("notionnel_liberal")
                   - soldes["centrale"][2070].solde("notionnel_liberal")) < 0.001, h
        assert (soldes[h][2070].solde("actuel") - soldes["centrale"][2070].solde("actuel")
                == pytest.approx(actuel["centrale"] - actuel[h], abs=0.002)), h
    with pytest.raises(ValueError, match="hypothèse d'espérance de vie"):
        calculer_cout(Simulateur(Parametres(hypothese_esperance_vie="haute")), depenses,
                      Population(RACINE_DONNEES))


def test_la_page_cout_suit_la_fecondite_et_les_migrations(depenses):
    """Sous une variante de fécondité ou de migrations de l'INSEE (action 138,
    étape 7), que le diviseur ne lit pas, la dépense du COR suit ce que la
    pyramide de la variante change à la masse du système actuel, et son PIB,
    ce qu'elle change aux 20-64 ans. En 2070, le système actuel est à quelques
    dixièmes de point de ce que le COR publie (rapport annuel de 2026, fig.
    2.18 à 2.20) : 16,34 et 14,34 % du PIB sous la fécondité basse et haute,
    16,40 et 14,16 % sous les migrations basses et hautes. La fécondité ne
    touche que le PIB, et rien ne bouge avant 2026 que les arrivées tardives
    des migrations de 2024 et 2025, de deux dix-millièmes."""
    publie = {"fecondite_basse": 0.1634, "fecondite_haute": 0.1434,
              "migrations_basse": 0.1640, "migrations_haute": 0.1416}
    centrale = memoire.cout(Parametres())
    for demographie, cor in publie.items():
        cout = memoire.cout(Parametres(), demographie=demographie)
        fins = {a.annee: a for a in cout.avenir.annees}
        assert fins[2024].part_pib("actuel") == centrale.avenir.annee(2024).part_pib("actuel")
        # Les arrivées de 2024 et 2025 de la variante, ses seules jusque-là.
        assert fins[2025].facteur_pib == 1.0
        assert fins[2025].facteur_pyramide == pytest.approx(1.0, abs=5e-4)
        assert cout.solde.annee(2070).depense("actuel") == pytest.approx(cor, abs=0.003)
        assert fins[2070].part_pib("actuel") == pytest.approx(
            cout.solde.annee(2070).depense("actuel"), abs=1e-9), demographie
        if demographie.startswith("fecondite"):
            assert {a.facteur_pyramide for a in fins.values()} == {1.0}
        else:
            assert fins[2070].facteur_pyramide != 1.0
    with pytest.raises(ValueError, match="une composante"):
        memoire.cout(Parametres(hypothese_esperance_vie="haute"),
                     demographie="fecondite_haute")


def test_la_proposition_s_indexe_sur_la_masse_de_la_variante(population):
    """Sous une variante démographique (action 138, étape 7), le compte de la
    proposition et sa pension servie suivent la masse salariale de la
    variante : celle du central multipliée, chaque année, par ce que la
    variante change aux 20-64 ans. Une cotisation de ``a`` liquidée en ``L``
    gagne ``f(L) / f(a)``, la pension servie de ``L`` à ``t``, ``f(t) / f(L)`` ;
    le diviseur ne bouge pas, et les autres systèmes non plus."""
    from types import SimpleNamespace

    from retraite_notionnelle.cout import (
        CLES_CAS_TYPES, RESSOURCES_GARANTIE, Pensionne, VoletLiberal,
        _capitaux_sous_la_variante, _masses)

    def facteur(annee):
        return 1.0 if annee < 2030 else 1.1

    # Deux cotisations égales, de 2020 et de 2040, sans rendement : la
    # première gagne 1,1, la seconde rien ; celle d'après le départ ne compte
    # pas.
    volet = VoletLiberal(annee_liquidation=2050, annee_ouverture_garantie=2050,
                         pension=1.0, ressources_garantie=1.0,
                         cotisations={2020: 100.0, 2040: 100.0, 2051: 50.0})
    pensionne = Pensionne(code="x", generation=1985, annee_liquidation=2050,
                          pensions={cle: 1.0 for cle in CLES_CAS_TYPES}, propre=volet)
    neutre = SimpleNamespace(indexation=SimpleNamespace(coefficient=lambda a, b: 1.0))
    capitaux = _capitaux_sous_la_variante(neutre, pensionne, facteur)
    assert capitaux[2] == pytest.approx(1.05, rel=1e-12)
    # La cohorte née deux ans plus tôt cotise en 2018 et en 2038, liquide en
    # 2048, et gagne autant.
    assert capitaux[0] == pytest.approx(1.05, rel=1e-12)
    assert Pensionne(code="x", generation=1985, annee_liquidation=2050,
                     pensions={}, propre=volet).capital(0) == 1.0

    simulateur = Simulateur(Parametres()).pour_la_projection()
    centrale = RevalorisationServie(simulateur, 2000, 2070)
    assert centrale.proposition is centrale
    variante = centrale.pour_la_proposition(facteur)
    assert variante.coefficient(2010, 2060) == centrale.coefficient(2010, 2060)
    assert variante.proposition.coefficient(2010, 2060) == pytest.approx(
        centrale.coefficient(2010, 2060) * 1.1, rel=1e-12)
    assert variante.proposition.coefficient(2040, 2060) == pytest.approx(
        centrale.coefficient(2040, 2060), rel=1e-12)

    simple = Pensionne(code="x", generation=1950, annee_liquidation=2010,
                       pensions={cle: 1.0 for cle in CLES_CAS_TYPES},
                       propre=VoletLiberal(annee_liquidation=2010,
                                           annee_ouverture_garantie=2015,
                                           pension=1.0, ressources_garantie=1.0),
                       parts_regimes={"regime_general": 1.0})
    portee = replace(simple, capitaux=(1.2,) * 5)
    masses, _, _ = _masses([simple], population, 2050, {"x": 1.0}, centrale)
    sous, _, _ = _masses([portee], population, 2050, {"x": 1.0}, variante)
    assert sous["notionnel_liberal"] == pytest.approx(
        masses["notionnel_liberal"] * 1.2, rel=1e-12)
    for cle in CLES_CAS_TYPES:
        if cle not in ("notionnel_liberal", RESSOURCES_GARANTIE):
            assert sous[cle] == masses[cle], cle


# -- la garantie vieillesse, chiffrée sur la distribution ---------------------


@pytest.fixture(scope="module")
def distribution() -> DistributionPensions:
    return DistributionPensions(RACINE_DONNEES)


def test_la_distribution_couvre_toute_la_population(distribution):
    assert distribution.somme_des_parts == pytest.approx(1.0, abs=1e-3)
    assert distribution.tranches[0].borne_inferieure == 0.0
    assert distribution.tranches[-1].ouverte
    assert all(not tranche.ouverte for tranche in distribution.tranches[:-1])


def test_un_plancher_nul_ne_coute_rien(distribution):
    chiffre = cout_garantie(distribution, 16e6, 0.0)
    assert chiffre.beneficiaires == 0.0
    assert chiffre.cout_annuel_meur == 0.0


def test_le_cout_de_la_garantie_croit_avec_le_plancher(distribution):
    montants = [
        cout_garantie(distribution, 16e6, plancher).cout_annuel_meur
        for plancher in (400.0, 800.0, 1050.0, 1400.0)
    ]
    assert montants == sorted(montants)
    assert all(montant > 0 for montant in montants[1:])


def test_un_plancher_au_dessus_de_tout_sert_a_tout_le_monde(distribution):
    """Contrôle de bout en bout du barème différentiel.

    Un plancher qui dépasse la dernière tranche ouverte est servi à chacun, et
    ce qu'il coûte est exactement ``plancher - pension moyenne`` par personne.
    La moyenne se recalcule ici à la main, tranche par tranche, faute de quoi
    le test ne contrôlerait que la cohérence du module avec lui-même.
    """
    plancher = 9000.0
    chiffre = cout_garantie(distribution, 1e6, plancher)
    assert chiffre.part_beneficiaires == pytest.approx(
        distribution.somme_des_parts)
    moyenne = sum(
        tranche.part * (
            tranche.borne_inferieure if tranche.ouverte
            else (tranche.borne_inferieure + tranche.borne_superieure) / 2
        )
        for tranche in distribution.tranches
    )
    attendu = (plancher * distribution.somme_des_parts - moyenne) * 1e6 * 12 / 1e6
    assert chiffre.cout_annuel_meur == pytest.approx(attendu)


def test_deplacer_les_pensions_vers_le_bas_coute_plus_cher(distribution):
    entier = cout_garantie(distribution, 16e6, 800.0, 1.0)
    reduit = cout_garantie(distribution, 16e6, 800.0, 0.6)
    assert reduit.cout_annuel_meur > entier.cout_annuel_meur
    assert reduit.beneficiaires > entier.beneficiaires
    with pytest.raises(ValueError, match="strictement positif"):
        cout_garantie(distribution, 16e6, 800.0, 0.0)


def test_les_deux_sexes_recomposent_la_colonne_dont_le_cout_est_tire(distribution):
    """Peser les sexes autrement que l'enquête, c'est parler d'une autre population.

    Le coût de la garantie est lu sur la colonne « ensemble » de l'EIR ; les
    avances, elles, sont suivies avec la mortalité des deux sexes, pesés par
    une part de femmes. Si cette part n'est pas celle de l'enquête, le modèle
    décrit deux populations différentes dans le même calcul — et c'est ce qu'il
    faisait jusqu'au 21 septembre 2026, avec les 56,0 % que les courbes de
    survie donnent en population stationnaire là où l'enquête dit 52,8 %.

    Ce test refait le raccord : à ce poids-là, et à lui seul, le mélange des
    deux colonnes de sexe redonne la colonne « ensemble », à l'arrondi de
    publication près — sur les parts, et sur ce qui en découle, la part des
    retraités sous le plancher.
    """
    racine = Parametres().racine_donnees
    poids = part_femmes(racine, distribution.millesime)
    assert 0.5 < poids < 0.6
    colonnes = {
        sexe: DistributionPensions(racine, sexe=sexe,
                                   millesime=distribution.millesime)
        for sexe in ("F", "H", "ensemble")
    }
    for rang, tranche in enumerate(colonnes["ensemble"].tranches):
        melange = (poids * colonnes["F"].tranches[rang].part
                   + (1.0 - poids) * colonnes["H"].tranches[rang].part)
        # La DREES publie au centième de point : l'écart ne peut pas le dépasser.
        assert abs(melange - tranche.part) <= 1e-4, tranche.borne_inferieure
    # Et sur la grandeur qui sert : la part sous le plancher, aux pensions
    # d'aujourd'hui comme à celles du scénario 6.
    base = Parametres()
    vers = Simulateur(base).macro.coefficient_prix(
        base.annee_euros_garantie_vieillesse, distribution.millesime)
    plancher = (base.garantie_vieillesse_mensuelle
                + base.allocation_isolement_mensuelle) * vers
    for facteur in (1.0, 0.6):
        parts = {
            sexe: cout_garantie(colonnes[sexe], 1.0, plancher, facteur).part_beneficiaires
            for sexe in ("F", "H", "ensemble")
        }
        melange = poids * parts["F"] + (1.0 - poids) * parts["H"]
        assert melange == pytest.approx(parts["ensemble"], abs=5e-4), facteur


def _quantiles(distribution: DistributionPensions, rangs) -> list[float]:
    """Les quantiles d'une distribution par tranches, uniforme dans chacune."""
    resultat = []
    for rang in rangs:
        cumul = 0.0
        for tranche in distribution.tranches:
            if tranche.part > 0 and cumul + tranche.part >= rang and not tranche.ouverte:
                largeur = tranche.borne_superieure - tranche.borne_inferieure
                resultat.append(tranche.borne_inferieure
                                + (rang - cumul) / tranche.part * largeur)
                break
            cumul += tranche.part
    return resultat


def test_la_distribution_des_residents_redonne_les_deciles_publies():
    """Retirer les résidents à l'étranger redonne la distribution de ceux de France.

    La garantie ne sert que les résidents, comme l'ASPA qu'elle remplace
    (article L. 815-1), et le tableau de l'enquête compte aussi les autres.
    La DREES ne publie pas la distribution des résidents par tranches ; elle
    publie leurs quantiles, et ceux des résidents à l'étranger. Le dépôt retire
    donc de chaque tranche ce que les seconds y mettent — et ce test est le
    contrôle externe : les déciles qui en sortent sont ceux que l'enquête
    publie pour les résidents en France, à trente euros près, pour chaque
    sexe, une fois les deux grandeurs ramenées l'une à l'autre.
    """
    from retraite_notionnelle.donnees.distribution import (
        QUANTILES_PUBLIES, ResidenceRetraites,
    )
    residence = ResidenceRetraites(RACINE_DONNEES)
    for sexe in ("ensemble", "F", "H"):
        residents = DistributionPensions(RACINE_DONNEES, sexe=sexe, residence="france")
        assert residents.somme_des_parts == pytest.approx(1.0, abs=1e-9)
        assert residents.part_residents == pytest.approx(
            residence.valeur("france", "effectifs", sexe)
            / residence.valeur("ensemble", "effectifs", sexe))
        echelle = (residence.valeur("france", "pension_droit_direct", sexe)
                   / residence.valeur("france", "pension_droit_direct_majorations", sexe))
        obtenus = _quantiles(residents, [rang for _, rang in QUANTILES_PUBLIES])
        for (code, _), obtenu in zip(QUANTILES_PUBLIES, obtenus):
            publie = residence.valeur("france", code, sexe) * echelle
            assert obtenu == pytest.approx(publie, abs=30.0), (sexe, code)
        # Et ils pèsent sur la queue basse : sous 700 €, les résidents sont
        # nettement moins nombreux que les retraités de l'enquête — en
        # effectif, rapporté à ceux-ci.
        tous = DistributionPensions(RACINE_DONNEES, sexe=sexe)
        assert (residents.part_sous(700.0) * residents.part_residents
                < tous.part_sous(700.0) - 0.025), sexe
    assert 0.93 < DistributionPensions(RACINE_DONNEES, residence="france").part_residents < 0.96


def test_la_garantie_de_la_trajectoire_est_lue_sur_la_distribution(cout, distribution):
    """La ligne « dont garantie » ne vient plus des cas types.

    Une allocation différentielle ne coûte que ce que coûte la queue basse de
    la distribution des pensions, et treize carrières choisies pour couvrir
    les configurations du système n'en ont pas. La trajectoire applique donc
    le barème à la distribution de l'EIR, déplacée d'un facteur que la grille
    donne ; ce test refait le calcul de l'année de l'enquête à la main, avec le
    module ``garantie`` et les nombres que la ligne annuelle expose.
    """
    simulateur = Simulateur(Parametres())
    parametres = simulateur.parametres
    millesime = distribution.millesime
    ligne = cout.annee(millesime)
    projetee = ligne.garantie
    assert projetee is not None
    # Le facteur dit de combien les pensions du scénario 6 sont plus basses que
    # celles servies : un compte rétroactif ne rend que ce qui a été cotisé.
    assert 0.5 < projetee.facteur < 0.9
    # Le plancher est celui des paramètres — majoré, le foyer par défaut étant
    # une personne seule —, dans les euros de l'enquête.
    plancher = parametres.garantie_vieillesse_mensuelle
    vers_enquete = simulateur.macro.coefficient_prix(
        parametres.annee_euros_garantie_vieillesse, millesime)
    # DEUX FACTEURS ET NON UN, depuis le 21 septembre 2026 : le scénario retire
    # les droits non cotisés, dont les femmes détiennent une part mesurée, et
    # chaque sexe est déplacé du sien sous contrainte que la moyenne d'ensemble
    # bouge du facteur que la grille donne. Le test refait ce calcul-là.
    caracteristiques = simulateur.caracteristiques
    # DEUX PLANCHERS AUSSI, depuis le 21 septembre 2026 : la garantie vaut
    # 800 € par personne plus 250 € à qui vit seul, et le recensement dit qui
    # vit seul. ``plancher`` est donc celui de qui vit à deux, et le majoré
    # s'applique dans la proportion que le recensement mesure, sexe par sexe.
    # La MÊME table que le calage : celle des bénéficiaires, et non celle de la
    # population générale. Qui vit seul dépend de l'âge, et combien d'années
    # on passe à chaque âge dépend de la mortalité.
    bascule = cout.avenir.annee(parametres.annee_bascule)
    population = bascule.garantie.population_mortalite if bascule is not None else None
    part_seule = {
        sexe: 1.0 - simulateur.vie_en_couple.part_moyenne(
            sexe,
            list(simulateur.mortalite.courbe_survie(
                65, parametres.annee_bascule, sexe, True, population)),
        )
        for sexe in ("F", "H")
    }
    attendu = cout_garantie_par_sexe(
        simulateur.distributions_par_sexe["F"],
        simulateur.distributions_par_sexe["H"],
        simulateur.distribution.part_femmes_residents, projetee.effectif,
        plancher * vers_enquete, projetee.facteur,
        caracteristiques.rapport_deplacement(),
        (plancher + parametres.allocation_isolement_mensuelle) * vers_enquete,
        part_seule,
    )
    # Un ayant droit sur deux réclame : les bénéficiaires et le coût sont
    # ceux qui réclament, les ayants droit tous ceux qui sont sous le plancher.
    taux = parametres.taux_recours_garantie
    assert projetee.taux_recours == taux
    assert projetee.ayants_droit == pytest.approx(attendu.beneficiaires)
    assert projetee.beneficiaires == pytest.approx(attendu.beneficiaires * taux)
    vers_constants = simulateur.macro.coefficient_prix(
        millesime, parametres.annee_euros_constants)
    assert projetee.cout_constants == pytest.approx(
        attendu.cout_annuel_meur * vers_constants * taux)
    # Et c'est ce coût que le rapport de la composante redonne, appliqué aux
    # droits directs de la dépense observée.
    assert ligne.cout_constants(COMPOSANTE_GARANTIE) == pytest.approx(
        projetee.cout_constants, rel=1e-9)
    # L'effectif est celui des retraités de 65 ans et plus, sur l'échelle de
    # la DREES : moins que tous les retraités de l'enquête.
    tous = simulateur.effectifs.effectif("tous_regimes", millesime)
    assert 0.7 * tous < projetee.effectif < tous


def test_la_garantie_decroit_quand_les_pensions_montent_face_au_plancher(cout, avenir):
    """Le facteur monte avec les salaires, le plancher suit les prix : la
    garantie décroît, en part des retraités qui l'attendent comme en part du
    PIB, sans jamais s'annuler — une queue basse ne disparaît pas. Le nombre
    de ses bénéficiaires, lui, tient à peu près : les têtes de 65 ans et plus
    croissent d'un tiers de 2025 à 2070. Il reculait de 0,6 % jusqu'au
    24 octobre 2026, et croît de 0,2 % depuis que chaque caisse se divise par
    les têtes de ses cas types (action 138, étape 3) : en 2025, les départs
    précoces, dont le compte notionnel ampute le plus la pension, pèsent
    moins, et le facteur passe de 0,7440 à 0,7495 ; en 2070, il ne bouge
    pas."""
    projetees = avenir.projetees()
    premiere, derniere = projetees[0], projetees[-1]
    assert derniere.garantie.facteur > premiere.garantie.facteur
    assert (derniere.garantie.beneficiaires / derniere.garantie.effectif
            < premiere.garantie.beneficiaires / premiere.garantie.effectif)
    assert derniere.part_pib(COMPOSANTE_GARANTIE) < premiere.part_pib(COMPOSANTE_GARANTIE)
    assert derniere.part_pib(COMPOSANTE_GARANTIE) > 0.002
    # Et l'ordre de grandeur est celui du barème appliqué à la distribution,
    # non plus celui d'une grille sans queue basse — à un ayant droit sur deux.
    assert 0.003 < premiere.part_pib(COMPOSANTE_GARANTIE) < 0.02


def test_regrouper_les_avances_par_succession_abaisse_la_couverture(cout):
    """Deux avances sur une succession sont moins bien couvertes qu'une seule :
    le patrimoine ne double pas avec elles. Le nombre d'avances par succession
    doit donc faire baisser la part reprise, et un test le vérifie sur les
    distributions du dépôt plutôt que sur le seul chiffre du jour."""
    from retraite_notionnelle.donnees.patrimoine import PatrimoineMenages

    projetee = cout.avenir.annee(cout.avenir.annee_bascule).garantie
    patrimoine = PatrimoineMenages(RACINE_DONNEES)
    for population in ("retraites_q1", "retraites"):
        distribution = patrimoine.distribution(population)
        seule = distribution.couverture(100_000.0)
        groupee = distribution.couverture(100_000.0 * projetee.avances_par_succession)
        assert groupee < seule


def test_la_vie_en_couple_pese_les_avances_par_succession():
    """Les parts publiées sont des pourcentages, les hommes vivent plus
    souvent en couple que les femmes à tout âge, et la moyenne sur une
    exposition reste entre le minimum et le maximum de la table."""
    from retraite_notionnelle.donnees.vie_en_couple import VieEnCouple

    couple = VieEnCouple(RACINE_DONNEES)
    assert couple.annee >= 2021
    assert couple.age_minimal == 65 and couple.age_maximal >= 95
    assert couple.fiabilite == Fiabilite.HAUTE
    for age in range(couple.age_minimal, couple.age_maximal + 1):
        for sexe in ("F", "H"):
            assert 0.0 <= couple.part(age, sexe) <= 1.0
            assert 0.0 <= couple.part(age, sexe, "seul") <= 1.0
            assert couple.part(age, sexe) + couple.part(age, sexe, "seul") <= 1.0
        assert couple.part(age, "H") > couple.part(age, "F"), age
    # Hors de la table, le bord est reconduit.
    assert couple.part(50, "F") == couple.part(couple.age_minimal, "F")
    assert couple.part(120, "H") == couple.part(couple.age_maximal, "H")
    # Une exposition plate donne la moyenne simple des âges couverts.
    plate = [1.0] * 5
    attendue = sum(couple.part(65 + k, "F") for k in range(5)) / 5
    assert couple.part_moyenne("F", plate) == pytest.approx(attendue)
    # Et une exposition décroissante, celle d'une table de mortalité, reste
    # entre les bornes de la table.
    decroissante = [1.0, 0.8, 0.5, 0.2, 0.05]
    moyenne = couple.part_moyenne("H", decroissante)
    parts = [couple.part(65 + k, "H") for k in range(5)]
    assert min(parts) <= moyenne <= max(parts)


def test_les_reprises_sur_succession_suivent_les_avances(cout):
    """La garantie est une avance : rien n'est repris avant la bascule, les
    reprises sont la part couverte des avances que les décès libèrent, le net
    est le versé moins les reprises, et le stock d'avances monte avec les
    générations servies avant que les reprises ne rattrapent le versé."""
    avenir = cout.avenir
    bascule = avenir.annee_bascule
    # Sans réglage, la part est calculée sur le patrimoine des retraités : la
    # même pour toute la trajectoire, et entre le quart et les trois quarts.
    assert Parametres().part_reprise_garantie is None
    part = avenir.annee(bascule).garantie.part_reprise
    assert 0.25 < part < 0.75
    for ligne in avenir.annees:
        projetee = ligne.garantie
        if ligne.annee < bascule:
            assert projetee.reprises_constants == 0.0
            assert projetee.stock_avances_constants == 0.0
            continue
        assert projetee.avances_liberees_constants >= 0.0
        # Ce qui est rendu au décès, plus ce que le logement des couples rend
        # des avances libérées ``report_annees`` plus tôt, intérêts courus.
        anterieure = avenir.annee(ligne.annee - projetee.report_annees)
        liberees_avant = (anterieure.garantie.avances_liberees_constants
                          if anterieure is not None and anterieure.annee >= bascule
                          else 0.0)
        assert projetee.reprises_constants == pytest.approx(
            projetee.part_reprise_immediate * projetee.avances_liberees_constants
            + (projetee.part_reprise - projetee.part_reprise_immediate)
            * projetee.facteur_report * liberees_avant)
        assert ligne.garantie_nette_constants() == pytest.approx(
            ligne.cout_constants(COMPOSANTE_GARANTIE) - projetee.reprises_constants)
        assert -0.05 < projetee.taux_reel < 0.05
        assert projetee.part_reprise == part
        # Les bénéficiaires meurent plus tôt que la population générale : leur
        # avance dure moins que l'espérance de vie à 65 ans de tous.
        assert 15.0 < projetee.duree_avances < 24.0
        assert projetee.population_mortalite is not None
        # Les femmes ont les pensions les plus basses : elles sont la majorité
        # sous le plancher, et leur longévité allonge les avances. Quatre sur
        # cinq depuis que la garantie ne compte que les résidents en France
        # (23 septembre 2026) : les résidents à l'étranger qu'elle comptait,
        # dont la pension française est petite, sont surtout des hommes.
        assert 0.55 < projetee.part_femmes < 0.85
        # Un couple de deux bénéficiaires laisse deux avances sur une
        # succession : le nombre moyen est entre un et deux, et strictement
        # au-dessus de un puisque des bénéficiaires vivent en couple.
        assert 1.0 < projetee.avances_par_succession < 2.0
    premiere = avenir.annee(bascule)
    derniere = avenir.annees[-1]
    # La première année, les décès ne libèrent presque rien : personne n'a
    # encore d'avance. À l'horizon, les reprises sont une part sensible du versé.
    assert premiere.reprises_constants() < 0.05 * premiere.cout_constants(COMPOSANTE_GARANTIE)
    assert derniere.reprises_constants() > 0.3 * derniere.cout_constants(COMPOSANTE_GARANTIE)
    assert derniere.garantie.stock_avances_constants > premiere.garantie.stock_avances_constants > 0.0
    assert 0.0 < avenir.cumul_reprises() < avenir.cumul(COMPOSANTE_GARANTIE)


def test_sans_les_trois_regles_la_grille_rend_la_couverture_fermee():
    """Les trois règles coupées et l'assurance-vie ramenée à zéro, le
    recouvrement sur la grille est l'espérance fermée de ``couverture`` : la
    convention d'avant le 22 septembre 2026, au millième près."""
    from dataclasses import replace
    from pathlib import Path
    from retraite_notionnelle.cout import _recouvrement
    from retraite_notionnelle.donnees.patrimoine import PatrimoineMenages
    parametres = replace(Parametres(), reprise_report_logement=False,
                         reprise_donations=False, reprise_assurance_vie=False,
                         part_assurance_vie_patrimoine=0.0)
    patrimoine = PatrimoineMenages(Path(parametres.racine_donnees))
    for population in ("retraites_q1", "retraites"):
        distribution = patrimoine.distribution(population)
        for creance in (10_000.0, 60_000.0, 150_000.0, 400_000.0):
            immediat, differe = _recouvrement(
                creance, distribution.grille, parametres, 0.35, 1.3, 0.1, 50_000.0)
            assert differe == 0.0
            assert immediat == pytest.approx(distribution.couverture(creance), abs=1e-3)


def test_le_logement_d_un_couple_ne_rend_que_ce_qu_il_vaut():
    """Au premier décès d'un couple, la créance est prise sur ce qui n'est pas
    le logement, et le reste attend le survivant : grossi des intérêts, il
    n'est jamais pris au-delà du logement, et un locataire n'a rien à attendre."""
    from dataclasses import replace
    from retraite_notionnelle.cout import _recouvrement
    parametres = replace(Parametres(), reprise_donations=False,
                         reprise_assurance_vie=False, part_assurance_vie_patrimoine=0.0,
                         part_logement_proprietaires=0.75,
                         patrimoine_minimal_proprietaire=80_000.0)
    # Un propriétaire de 200 000 €, dont 150 000 de logement, tout en couple :
    # 50 000 tout de suite, puis 100 000 × 1,3 = 130 000 sur le logement.
    immediat, differe = _recouvrement(150_000.0, [200_000.0], parametres, 1.0, 1.3, 0.0, 0.0)
    assert immediat * 150_000.0 == pytest.approx(50_000.0)
    assert differe * 150_000.0 == pytest.approx(130_000.0)
    # Une créance plus grosse bute sur le logement.
    immediat, differe = _recouvrement(400_000.0, [200_000.0], parametres, 1.0, 1.3, 0.0, 0.0)
    assert differe * 400_000.0 == pytest.approx(150_000.0)
    # Un locataire de 50 000 € rend tout de suite ce qu'il a, et rien après.
    immediat, differe = _recouvrement(150_000.0, [50_000.0], parametres, 1.0, 1.3, 0.0, 0.0)
    assert immediat * 150_000.0 == pytest.approx(50_000.0) and differe == 0.0


def test_le_recours_reduit_le_cout_de_la_garantie_dans_la_meme_proportion(cout, distribution):
    """Un recours complet doublerait le coût du réglage par défaut, un sur deux ;
    les ayants droit, eux, ne bougent pas, et un taux hors de ]0, 1] est refusé."""
    from retraite_notionnelle.cout import GarantieDistribution
    millesime = distribution.millesime
    projetee = cout.annee(millesime).garantie
    assert projetee.taux_recours == 0.5
    assert projetee.beneficiaires == pytest.approx(projetee.ayants_droit * 0.5)
    with pytest.raises(ValueError):
        GarantieDistribution(distribution, 800.0, 1000.0, 1.0, 1.0, taux_recours=0.0)
    with pytest.raises(ValueError):
        GarantieDistribution(distribution, 800.0, 1000.0, 1.0, 1.0, taux_recours=1.5)


# -- le solde : ce qui rentre, face à ce qui sort ----------------------------


def test_le_compte_du_cor_couvre_2002_a_l_horizon(comptes: ComptesRetraite):
    """La fenêtre est celle de la source, et rien d'autre ne la borne.

    Elle commence en 2002 parce que c'est le premier rapport à la Commission
    des comptes de la Sécurité sociale que le COR consolide, et finit à son
    horizon de projection.
    """
    assert comptes.premiere_annee == 2002
    assert comptes.derniere_annee >= 2070
    assert comptes.annees() == list(
        range(comptes.premiere_annee, comptes.derniere_annee + 1))
    for annee in comptes.annees():
        assert comptes.depense(annee) > 0.0, annee
        assert comptes.ressource(annee) > 0.0, annee


def test_le_compte_observe_vaut_haute_et_le_projete_estime(comptes: ComptesRetraite):
    """Le critère 1 plafonne une consolidation ; le critère 2 dégrade une projection.

    Le COR n'est pas producteur des comptes de chaque régime — ce sont ceux des
    rapports à la CCSS — mais il est le seul à les consolider : c'est exactement
    la position d'OpenFisca, et elle vaut `haute`, jamais `certifiee`.
    """
    observee = comptes.derniere_annee_observee
    assert observee >= 2024
    assert comptes.fiabilite(observee) == Fiabilite.HAUTE
    assert comptes.fiabilite(comptes.premiere_annee) == Fiabilite.HAUTE
    assert comptes.fiabilite(observee + 1) == Fiabilite.ESTIMEE
    assert comptes.fiabilite(comptes.derniere_annee) == Fiabilite.ESTIMEE


def test_les_deux_perimetres_se_recoupent(comptes: ComptesRetraite,
                                          depenses: DepensesRetraite):
    """Le contrôle externe de cette section, et le seul dont elle dispose.

    Le COR compte les régimes légalement obligatoires, FSV compris ; la DREES
    compte la répartition obligatoire du risque vieillesse-survie. Deux
    comptabilités indépendantes, deux périmètres voisins : si l'écart dépassait
    le point de PIB, l'une des deux séries serait mal lue. Le COR est un peu
    au-dessus — le FSV, que la ventilation de la DREES range hors répartition.
    """
    for annee in range(2002, depenses.derniere_annee + 1):
        drees = depenses.repartition(annee) / depenses.pib(annee)
        cor = comptes.depense(annee)
        assert cor - drees == pytest.approx(0.0, abs=0.01), annee
        assert cor > drees, annee
        # Et le risque entier, lui, est toujours au-dessus des deux.
        assert depenses.part_pib(annee) > cor, annee


def test_le_solde_du_systeme_actuel_est_celui_que_le_cor_publie(solde, comptes):
    """Le rapport du scénario 1 vaut un : son solde doit être le solde publié.

    C'est ce qui dit que le raccord entre deux périmètres ne triche pas — la
    dépense du système actuel reste celle du COR de bout en bout, et le modèle
    ne s'y glisse nulle part.
    """
    for ligne in solde.annees:
        assert ligne.rapports["actuel"] == 1.0, ligne.annee
        assert ligne.solde("actuel") == pytest.approx(
            comptes.solde(ligne.annee)), ligne.annee
    # 2025 : le COR annonce un besoin de financement de 5,1 milliards d'euros.
    dernier = solde.annee(solde.derniere_annee_observee)
    assert dernier.solde_meur("actuel") / 1000 == pytest.approx(-5.1, abs=0.2)


def test_le_coefficient_dit_exactement_ce_que_dit_le_solde(solde):
    """Deux écritures d'une même chose : un coefficient sous un signe.

    Le coefficient vaut un quand le solde est nul, moins de un quand il est
    négatif. Un test d'équivalence vaut mieux qu'un test de valeur : il tient
    quel que soit le millésime du rapport.
    """
    for ligne in solde.annees:
        for scenario, _ in SCENARIOS:
            excedent = ligne.solde(scenario) > 0.0
            assert (ligne.coefficient(scenario) > 1.0) is excedent, (
                ligne.annee, scenario)
            # Et le coefficient ramène bien la dépense sur les ressources QUE
            # CE SYSTÈME PEUT COMPTER : tout pour le système actuel, moins la
            # recette non acquise pour les autres.
            assert ligne.depense(scenario) * ligne.coefficient(scenario) == (
                pytest.approx(ligne.ressources_de(scenario)))


def test_le_bilan_porte_le_taux_effectif_et_la_depense_nette(solde, depenses):
    """Chaque année du bilan porte le taux que les prélèvements sociaux prennent
    à la masse des pensions, tel que ``DepensesRetraite`` le lit pour elle dans
    les montants certifiés de la DREES — 6,8 % en 2022 et après, 6,2 % en
    2008 et avant —, et la dépense nette de chaque système en est sa dépense,
    diminuée (action 138, étape 3)."""
    for ligne in solde.annees:
        assert ligne.taux_effectif == depenses.taux_effectif(ligne.annee), ligne.annee
        assert ligne.annee_taux_effectif == depenses.annee_du_taux_effectif(ligne.annee)
        for scenario, _ in SCENARIOS:
            assert ligne.depense_nette(scenario) == pytest.approx(
                ligne.depense(scenario) * (1.0 - ligne.taux_effectif)), (ligne.annee, scenario)
    assert solde.annee(2070).annee_taux_effectif == 2022
    assert solde.annee(2070).taux_effectif == pytest.approx(0.068, abs=5e-4)
    assert solde.annee(2008).taux_effectif == pytest.approx(0.062, abs=5e-4)


def test_le_systeme_actuel_ne_s_equilibre_jamais_et_le_notionnel_si(solde):
    """Le résultat de fond de cette section, réduit à ce qui en est une PROPRIÉTÉ.

    Le système actuel reste déficitaire sur toute la fenêtre projetée du COR :
    c'est son compte, lu, et le seul énoncé de ce test qui n'ait jamais bougé.
    Le scénario 3 fait mieux que lui, et le scénario 5 fait moins bien que le 3,
    parce qu'il porte la part patronale au compte, donc des droits, donc une
    dépense : deux propriétés de construction, que les règles ne déplacent pas.

    CE TEST A ÉTÉ RÉÉCRIT SEPT FOIS, dont six le 19 septembre 2026, parce qu'il
    affirmait aussi des RÉSULTATS — le signe de la moyenne du 3, celui du 5, le
    rang du 5 face au système actuel — et que chaque changement du modèle les
    déplaçait, et le test avec eux : il ne tenait plus rien. Ces résultats sont
    désormais dits par la prose, ancrés sur des sondes qui les recalculent
    (``solde_moyen`` dans le README), et plus par un test qui les suit.
    """
    debut, fin = solde.premiere_annee_projetee, solde.derniere_annee
    assert solde.premiere_annee_equilibree("actuel") is None
    assert all(ligne.solde("actuel") < 0.0 for ligne in solde.projetees())
    assert solde.solde_moyen("actuel", debut, fin) < 0.0
    # Le 3 fait mieux que le système actuel : il ne sert que ce qui a été
    # cotisé, part salariale seule.
    assert (solde.solde_moyen("notionnel_prospectif", debut, fin)
            > solde.solde_moyen("actuel", debut, fin))
    # Le 5 porte plus de droits que le 3 : il coûte davantage, chaque année.
    for ligne in solde.projetees():
        assert (ligne.solde("notionnel_prospectif_employeur")
                <= ligne.solde("notionnel_prospectif") + 1e-12), ligne.annee


def test_le_solde_en_euros_s_arrete_ou_le_pib_publie_s_arrete(solde, depenses):
    """Au-delà, un montant en milliards serait une hypothèse de croissance.

    La part de PIB, elle, court jusqu'à l'horizon : c'est l'unité du COR, et
    c'est la seule qui ne suppose rien.
    """
    for ligne in solde.annees:
        if ligne.annee <= depenses.pib.derniere_annee:
            assert ligne.pib == pytest.approx(depenses.pib(ligne.annee))
            assert ligne.solde_meur("actuel") == pytest.approx(
                ligne.solde("actuel") * depenses.pib(ligne.annee))
        else:
            assert ligne.pib == 0.0, ligne.annee
            assert ligne.solde_meur("actuel") == 0.0, ligne.annee
    # Un solde en euros n'est jamais nul par accident de fenêtre : 2023 l'est
    # parce que le COR y trouve l'équilibre au milliardième de PIB près.
    assert abs(solde.annee(2010).solde_meur("actuel")) > 1000.0


def test_le_solde_ne_se_donne_jamais_pour_certifie(solde):
    """Le compte observé vaut « haute » ; tout ce qui passe par un rapport, non."""
    assert solde.fiabilite_observee == Fiabilite.HAUTE
    assert solde.fiabilite == Fiabilite.ESTIMEE


def test_sans_comptes_le_cout_est_calcule_a_l_identique(comptes, cout):
    """Les ressources sont un ajout, jamais une correction de ce qui précède.

    Une exception, et elle est voulue depuis le 5 octobre 2026 : au-delà de la
    dernière année publiée, la dépense du système actuel EST celle du compte du
    COR (action 147). Sans compte, la trajectoire retombe sur celle que le
    modèle se donne lui-même ; les rapports entre systèmes, eux, ne bougent pas,
    ni le passé, ni la trajectoire propre du modèle.
    """
    sans = memoire.cout(Parametres(), comptes=False, assiette=False)
    assert sans.solde.annees == []
    assert sans.cumul("notionnel_retroactif") == pytest.approx(
        cout.cumul("notionnel_retroactif"))
    assert len(sans.avenir.annees) == len(cout.avenir.annees)
    for seule, avec in zip(sans.avenir.annees, cout.avenir.annees):
        assert seule.annee == avec.annee
        assert seule.base_modele == pytest.approx(avec.base_modele, rel=1e-12)
        for scenario, _ in SCENARIOS:
            assert seule.rapports[scenario] == pytest.approx(
                avec.rapports[scenario], rel=1e-12), (seule.annee, scenario)
        if seule.projete:
            assert seule.base == pytest.approx(seule.base_modele, rel=1e-12)
        else:
            assert seule.base == pytest.approx(avec.base, rel=1e-12)


def test_les_postes_couvrent_la_structure_des_ressources():
    """Les codes du modèle et ceux qu'écrit le vérificateur ne peuvent pas diverger."""
    chemin = (RACINE_DONNEES / "reference" / "macro"
              / "structure_ressources_retraite.csv")
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        codes = {ligne["poste"] for ligne in csv.DictReader(lignes)}
    assert codes == set(CODES_POSTES)
    assert len(CODES_POSTES) == len(set(CODES_POSTES))


def test_les_parts_des_ressources_somment_a_un(comptes: ComptesRetraite):
    """Le seul contrôle qui vaille sur une décomposition : rien d'oublié."""
    premiere = max(comptes.structure[p.code].premiere_annee for p in POSTES)
    for annee in range(premiere, comptes.derniere_annee_observee + 1):
        somme = sum(comptes.part(poste.code, annee) for poste in POSTES)
        assert somme == pytest.approx(1.0, abs=1e-5 * len(POSTES)), annee


def test_la_part_cotisee_domine_mais_recule(comptes: ComptesRetraite):
    """Les trois quarts des ressources sont cotisées, et cette part diminue.

    L'impôt a pris le relais des cotisations patronales allégées : c'est ce que
    la page doit pouvoir dire, et c'est ce qui borne la lecture du coefficient
    d'équilibre — un compte notionnel ne sait créditer que la part cotisée.
    """
    premiere = max(comptes.structure[p.code].premiere_annee for p in POSTES)
    derniere = comptes.derniere_annee_observee
    assert 0.70 < comptes.part_contributive(derniere) < 0.85
    assert comptes.part_contributive(derniere) < comptes.part_contributive(premiere)
    assert comptes.part("impots_et_taxes", derniere) > comptes.part(
        "impots_et_taxes", premiere)
    # Deux postes seulement sont cotisés, et ce sont les deux premiers.
    assert [poste.code for poste in POSTES if poste.contributive] == [
        "cotisations", "contribution_equilibre_etat"]


def test_les_quatre_groupes_repartissent_les_six_postes_sans_reste(
        comptes: ComptesRetraite):
    """La page montre quatre parts là où le COR en publie six : rien ne se perd.

    Un empilement à six bandes ne se lit pas, et « contribution d'équilibre de
    l'État » ne dit rien à qui n'a pas fait d'économie. Le regroupement est donc
    une affaire de lecture — jamais de comptabilité : chaque poste est dans un
    groupe et un seul, et la somme des quatre est la somme des six.
    """
    dans_un_groupe = [poste for groupe in GROUPES for poste in groupe.postes]
    assert sorted(dans_un_groupe) == sorted(CODES_POSTES), (
        "un poste manque à l'appel, ou compte deux fois"
    )
    for annee in (comptes.premiere_annee_ventilee, comptes.derniere_annee_ventilee):
        parts = sum(comptes.part_groupe(groupe.code, annee) for groupe in GROUPES)
        assert parts == pytest.approx(1.0, abs=1e-5 * len(POSTES)), annee
        # Et la même chose une fois rapportée au PIB, ce que le graphique empile.
        pib = sum(comptes.ressource_groupe(groupe.code, annee) for groupe in GROUPES)
        assert pib == pytest.approx(comptes.ressource(annee), rel=1e-4), annee


def test_la_ventilation_couvre_moins_d_annees_que_le_total(comptes: ComptesRetraite):
    """Le total des ressources remonte plus haut et va plus loin que son détail.

    C'est pourquoi la carte « d'où vient cet argent » s'arrête là où la carte
    du bilan continue, et pourquoi les deux bornes se lisent dans les séries
    plutôt que dans une constante écrite dans le code : le rapport suivant du
    COR les décalera d'un an.
    """
    assert comptes.premiere_annee_ventilee >= comptes.premiere_annee
    assert comptes.derniere_annee_ventilee <= comptes.derniere_annee
    assert comptes.annees_ventilees()[0] == comptes.premiere_annee_ventilee
    assert comptes.annees_ventilees()[-1] == comptes.derniere_annee_ventilee
    # La ventilation est observée, jamais projetée : le COR ne publie pas la
    # structure de ressources qu'il projette.
    assert comptes.derniere_annee_ventilee <= comptes.derniere_annee_observee


def test_les_postes_de_transfert_couvrent_la_serie():
    """Les codes du modèle et ceux qu'écrit le vérificateur ne peuvent pas diverger."""
    chemin = RACINE_DONNEES / "reference" / "macro" / "transferts_retraite.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        codes = {ligne["poste"] for ligne in csv.DictReader(lignes)}
    assert codes == set(CODES_TRANSFERTS)
    assert len(CODES_TRANSFERTS) == len(set(CODES_TRANSFERTS))
    # Chaque ligne a un payeur, et chaque payeur a au moins une ligne.
    organismes = {organisme.code for organisme in ORGANISMES}
    assert {poste.organisme for poste in POSTES_TRANSFERTS} == organismes


def test_la_branche_famille_verse_dix_milliards(comptes: ComptesRetraite):
    """L'ordre de grandeur que la page doit pouvoir dire, et qui borne le coefficient.

    La CNAF verse une dizaine de milliards par an — AVPF et majorations, à
    parts presque égales —, l'Unédic trois à quatre. Les scénarios notionnels
    ne servent pas les droits que la première paie ; ils portent au compte les
    cotisations que la seconde verse, et gardent donc sa recette.
    """
    annee = comptes.derniere_annee_transferts
    assert 9_000 < comptes.transfert_organisme("famille", annee) < 13_000
    assert 2_500 < comptes.transfert_organisme("chomage", annee) < 5_000
    avpf = comptes.transfert("cnaf_avpf", annee)
    majorations = comptes.transfert("cnaf_majorations", annee)
    assert 0.7 < avpf / majorations < 1.3
    # Le fonds de solidarité vieillesse s'y est ajouté le 19 septembre 2026, et
    # il pèse plus que les deux autres réunis : le retrait total est passé d'un
    # demi-point de PIB à plus d'un point.
    assert 18_000 < comptes.transfert_organisme("solidarite", annee) < 25_000
    assert (comptes.transfert_organisme("solidarite", annee)
            > comptes.transfert_organisme("famille", annee)
            + comptes.transfert_organisme("chomage", annee))
    assert 0.009 < comptes.transfert_supprime_part_pib(annee) < 0.015
    # La branche famille et le fonds ont un droit supprimé ; l'assurance
    # chômage non, le compte portant ce qu'elle verse. La recette suit le
    # droit, dans les deux sens.
    assert {o.code for o in ORGANISMES if o.droit_supprime} == {"famille", "solidarite"}
    assert comptes.transfert_supprime_part_pib(annee) == pytest.approx(
        comptes.transfert_part_pib("famille", annee)
        + comptes.transfert_part_pib("solidarite", annee))


def test_les_deux_caisses_n_expliquent_pas_tout_le_poste_transferts(
        comptes: ComptesRetraite):
    """La ventilation est une partie du poste, jamais plus, et plus de la moitié.

    Le poste « transferts » du COR contient aussi l'assurance maladie, l'État
    et quelques versements plus petits : la branche famille et l'assurance
    chômage doivent en expliquer l'essentiel sans le dépasser. Un dépassement
    dirait que les deux séries n'ont plus le même périmètre.

    Le fonds de solidarité vieillesse est hors de ce contrôle, et c'est tout
    son intérêt : sa recette n'arrive pas par un transfert mais par l'impôt —
    elle est dans le poste « impôts et taxes affectés ». C'est pour cela que la
    règle « la recette suit le droit » l'avait manqué pendant un an.
    """
    par_transfert = ("famille", "chomage")
    for annee in comptes.annees_transferts():
        if annee > comptes.derniere_annee_ventilee:
            continue
        ventilee = sum(comptes.transfert_part_ressources(code, annee)
                       for code in par_transfert)
        poste = comptes.part("transferts", annee)
        assert 0.5 * poste < ventilee < poste, annee
    # Et le fonds, lui, pèse une bonne part du poste des impôts et taxes : 38 %
    # en 2024, ce que la page doit pouvoir dire.
    annee = comptes.derniere_annee_transferts
    part = (comptes.transfert_part_ressources("solidarite", annee)
            / comptes.part("impots_et_taxes", annee))
    assert 0.25 < part < 0.55, part


def test_la_ventilation_recoupe_le_dont_du_cor(comptes: ComptesRetraite):
    """Ce que le COR publie depuis 2023 doit se retrouver, chez celui qui paie.

    Le « dont Unédic » du COR est exactement la somme des lignes Agirc-Arrco et
    Ircantec des rapports à la CCSS ; son « dont CNAF » s'écarte de quelques
    pour cent de ce que la CNAF déclare verser, dans un sens ou dans l'autre —
    consolidé du côté des régimes qui reçoivent. Les valeurs sont celles des
    tableaux 2.2 des rapports annuels de 2023 à 2025, en millions d'euros, et
    figées ici : ``data/brut/`` n'est pas versionné.
    """
    publie = {
        2022: (9961.8, 3346.5),
        2023: (10290.1, 3730.3),
        2024: (11300.7, 3949.2),
    }
    for annee, (cnaf, unedic) in publie.items():
        assert comptes.transfert_organisme("chomage", annee) == pytest.approx(
            unedic, rel=0.005), annee
        assert comptes.transfert_organisme("famille", annee) == pytest.approx(
            cnaf, rel=0.05), annee


def test_la_fenetre_des_transferts_est_observee(comptes: ComptesRetraite):
    """Les quatre lignes se lisent sur des années arrêtées, jamais projetées."""
    assert comptes.premiere_annee_transferts >= comptes.premiere_annee_ventilee
    assert comptes.derniere_annee_transferts <= comptes.derniere_annee_observee
    assert comptes.annees_transferts()[0] == comptes.premiere_annee_transferts
    assert comptes.annees_transferts()[-1] == comptes.derniere_annee_transferts
    # Dix ans au moins : sans série, la part constante que la page reporte à
    # l'horizon du COR ne serait qu'un chiffre.
    assert len(comptes.annees_transferts()) >= 10


def test_la_recette_suit_le_droit(cout: Cout, comptes: ComptesRetraite):
    """Un scénario ne perd une recette qu'à partir du jour où il cesse d'en servir le droit.

    Le système actuel encaisse tout, et son solde reste celui du COR. Un
    scénario rétroactif se voit retirer, année par année, ce que la branche
    famille et l'assurance chômage versent pour des droits qu'il ne sert pas.
    Un scénario « dès la bascule », lui, EST le système actuel avant elle : il
    en sert les pensions, en encaisse toutes les recettes, et son solde y est
    celui du COR, exactement. Jusqu'au 23 septembre 2026, ce test exigeait le
    solde du COR MOINS la recette retirée : il tenait l'erreur de
    construction qui prêtait aux scénarios 3 et 5 un déficit de plus d'un point
    de PIB avant qu'aucune de leurs règles eût changé.
    """
    solde = cout.solde
    bascule = Parametres().annee_bascule
    for annee in comptes.annees_transferts():
        assert annee < bascule
        ligne = solde.annee(annee)
        assert ligne.retrait == pytest.approx(comptes.transfert_supprime_part_pib(annee))
        assert ligne.ressources_de("actuel") == ligne.ressources
        assert ligne.solde("actuel") == pytest.approx(ligne.ressources - ligne.depenses)
        for scenario in ("notionnel_prospectif", "notionnel_prospectif_employeur"):
            assert ligne.rapports[scenario] == pytest.approx(1.0)
            assert ligne.ressources_de(scenario) == ligne.ressources
            assert ligne.solde(scenario) == pytest.approx(ligne.solde("actuel"))
            assert ligne.coefficient(scenario) == pytest.approx(ligne.coefficient("actuel"))
        for scenario in ("notionnel_retroactif", "notionnel_retroactif_employeur"):
            rapport = ligne.rapports_recettes.get(scenario, 1.0)
            cotisees = ligne.ressources * ligne.part_contributive
            assert ligne.ressources_de(scenario) == pytest.approx(
                cotisees * rapport + ligne.ressources - cotisees - ligne.retrait)
            # Ce que l'Unédic verse leur reste : le compte en porte les
            # cotisations. Le « dont » du poste le dit.
            postes = ligne.postes_ressources(scenario)
            assert postes["transferts_chomage"] == pytest.approx(ligne.versements["chomage"])
            assert postes["transferts_famille"] == 0.0
        assert ligne.versements["chomage"] > 0.0
        assert ligne.retrait == pytest.approx(
            ligne.versements["famille"] + ligne.versements["solidarite"])
    # À la bascule, la recette leur est retirée comme aux autres, sauf ce que
    # la branche famille rembourse des majorations des pensions qu'ils servent
    # encore — ``test_une_reforme_prospective_garde_le_remboursement_des_
    # majorations_qu_elle_sert`` en tient le montant. Jusqu'au 23 septembre
    # 2026, ce test exigeait le retrait entier.
    ligne = solde.annee(bascule)
    assert ligne.majorations_stock > 0.0
    for scenario in ("notionnel_prospectif", "notionnel_prospectif_employeur"):
        rapport = ligne.rapports_recettes.get(scenario, 1.0)
        cotisees = ligne.ressources * ligne.part_contributive
        assert ligne.ressources_de(scenario) == pytest.approx(
            cotisees * rapport + ligne.ressources - cotisees - ligne.retrait
            + ligne.majorations_stock)
    # Plus d'un point de PIB, toutes les années connues, depuis que le fonds
    # de solidarité vieillesse est entré dans le compte.
    for annee in comptes.annees_transferts():
        assert 0.009 < solde.annee(annee).retrait < 0.018, annee


@pytest.fixture(scope="module")
def assiette() -> AssietteActivite:
    return AssietteActivite(RACINE_DONNEES)


@pytest.fixture(scope="module")
def cout_assiette():
    """Le coût sous la convention du programme : le taux plein sur l'assiette."""
    return memoire.cout(Parametres(), convention_recette=CONVENTION_ASSIETTE)


def test_l_assiette_se_recoupe_avec_celle_que_le_cor_implique(
        assiette: AssietteActivite, comptes: ComptesRetraite):
    """Deux routes indépendantes vers la même grandeur, et elles se rejoignent.

    Le tableau 2.11 du rapport annuel du COR chiffre l'ajustement nécessaire à
    l'équilibre deux fois : en pour-cent de la masse de pension et en points de
    taux de prélèvement. Le rapport des deux donne son assiette sans qu'il ait
    eu à la publier — 3,19 fois la masse de pension. L'assiette mesurée ici ne
    doit rien au COR, et lui ne doit rien à l'INSEE : qu'elles tombent à
    quelques pour cent l'une de l'autre est le seul contrôle externe dont cette
    grandeur dispose.
    """
    # 2020 est écarté : le PIB s'est effondré sans que la masse de pension
    # suive, et le rapport des deux ne dit cette année-là que le confinement.
    for annee in (2022, 2023, 2024):
        implicite = 3.19 * comptes.depense(annee)
        mesuree = assiette.part_pib(annee)
        assert mesuree == pytest.approx(implicite, rel=0.08), annee
    # Et elle est stable : une assiette qui sauterait d'une année à l'autre
    # dirait qu'un des deux postes a changé de définition.
    parts = [assiette.part_pib(a) for a in range(2016, 2025)]
    assert max(parts) - min(parts) < 0.012, parts


def test_le_taux_projete_est_lu_chez_le_cor_et_non_gele_au_bord(
        assiette: AssietteActivite, comptes: ComptesRetraite):
    """Le profil du taux vient du COR ; le niveau reste celui que le dépôt mesure.

    Sur les années où l'assiette est publiée, le profil vaut un : ces années-là
    sont mesurées, et rien ne doit les déplacer. Au-delà, il suit la figure des
    déterminants des ressources, que le COR projette — un taux qui BAISSE.
    """
    derniere = assiette.derniere_annee
    for annee in range(derniere - 6, derniere + 1):
        assert comptes.profil_taux(annee, annee) == 1.0, annee

    # Le taux du COR baisse sur l'horizon : c'est le fait que cette série
    # apporte, et le dépôt supposait l'inverse.
    assert comptes.taux_prelevement(2070) < comptes.taux_prelevement(derniere)
    profil = comptes.profil_taux(2070, derniere)
    assert profil == pytest.approx(
        comptes.taux_prelevement(2070) / comptes.taux_prelevement(derniere))
    assert 0.90 < profil < 0.97, profil


def test_l_assiette_projetee_garde_sa_part_de_pib(
        assiette: AssietteActivite, comptes: ComptesRetraite):
    """L'assiette que la projection implique ne doit pas fondre.

    C'EST LE CONTRÔLE DE FOND DE CETTE SÉRIE. Les ressources du COR reculent en
    part de PIB ; l'assiette sur laquelle la proposition prélève ses 18 % est
    le quotient de ces ressources par le taux de prélèvement, et tout ce que le
    taux ne porte pas, l'assiette le porte. En gelant le taux au bord, le dépôt
    faisait tomber son assiette de 42,5 % du PIB à 39,3 % — une déformation du
    partage de la valeur ajoutée que `hypotheses_projection.yaml` s'interdit
    explicitement par ailleurs, et que le COR ne projette pas.

    Le taux lu chez le producteur la rend stable. La borne est large — un point
    et demi de PIB — parce que ce test n'a pas à reproduire la trajectoire du
    COR, seulement à refuser qu'elle reparte à la dérive.
    """
    derniere = assiette.derniere_annee
    mesuree = assiette.part_pib(derniere)
    for annee in range(derniere + 1, 2071):
        reference = assiette.annee_de_reference(annee)
        taux = (assiette.taux_prelevement(comptes.ressource(reference), reference)
                * comptes.profil_taux(annee, reference))
        implicite = comptes.ressource(annee) / taux
        assert abs(implicite - mesuree) < 0.015, (annee, implicite, mesuree)


def test_l_assiette_porte_ses_deux_postes_sur_toute_la_fenetre(
        assiette: AssietteActivite):
    """Une assiette amputée d'un de ses postes ne serait pas une assiette."""
    assert {code for code, _ in POSTES_ASSIETTE} == set(assiette.postes)
    assert assiette.premiere_annee <= 1949
    assert assiette.derniere_annee >= 2024
    for annee in (1949, 1980, 2024):
        for code, _ in POSTES_ASSIETTE:
            assert assiette.poste(code, annee) > 0.0, (annee, code)
        assert assiette.fiabilite(annee) is Fiabilite.CERTIFIEE, annee
    # Les salaires pèsent l'essentiel, le revenu mixte le reste : l'inverse
    # dirait que les deux postes ont été intervertis.
    assert (assiette.poste("salaires_bruts", 2024)
            > 5 * assiette.poste("revenu_mixte", 2024))


def test_la_recette_du_scenario_6_est_son_taux_sur_l_assiette(cout_assiette: Cout):
    """La convention du programme, écrite autrement que dans le code.

    Le scénario 6 encaisse son taux plein sur l'assiette mesurée, et rien de ce
    qui n'est pas assis sur un revenu d'activité : ni la contribution
    d'équilibre de l'État, que les 18 % remplacent ; ni les subventions
    d'équilibre, dont la fusion supprime l'objet ; ni les impôts et taxes
    affectés, qui n'acquièrent de droits à personne. Restent les transferts et
    les autres produits, moins la recette non acquise.
    """
    bascule = Parametres().annee_bascule
    taux = Parametres().taux_cotisation_liberal
    vues = 0
    for ligne in cout_assiette.solde.annees:
        if ligne.annee < bascule:
            # Avant la bascule, rien n'a changé : le scénario 6 prélève les
            # taux réels, et ne perd que la recette non acquise.
            assert not ligne.recette_par_assiette, ligne.annee
            assert ligne.ressources_de("notionnel_liberal") == pytest.approx(
                ligne.ressources - ligne.retrait), ligne.annee
            continue
        vues += 1
        assert ligne.recette_par_assiette, ligne.annee
        assert ligne.taux_liberal == taux
        # L'assiette mesurée, élargie de ce que l'âge légal de la proposition
        # fait cotiser en plus.
        pleine = ligne.ressources * taux / ligne.taux_prelevement * ligne.facteur_assiette
        # Trois postes sortent, tous le 19 septembre 2026 : la contribution
        # d'équilibre (remplacée par les 18 % sur les traitements), les
        # subventions (la fusion des régimes en supprime l'objet), les impôts
        # affectés (aucun droit acquis). Le retrait, lui, rend la part qui
        # vient de sortir avec l'impôt, pour ne pas la retirer deux fois.
        autres = ligne.ressources * (1.0 - ligne.part_contributive
                                     - ligne.part_subventions
                                     - ligne.part_impots)
        # Et la TVA à taux unique, depuis le 23 septembre 2026 : ce qui en reste
        # une fois la garantie payée. Elle n'est pas une cotisation, et le
        # taux plein ne la contient pas.
        assert ligne.ressources_de("notionnel_liberal") == pytest.approx(
            pleine + autres - (ligne.retrait - ligne.retrait_par_impot)
            + ligne.tva_de("notionnel_liberal")), ligne.annee
        if ligne.annee >= bascule + 3:
            # Une fois le décalage de la grille éteint, le taux plein rapporte
            # PLUS que le rapport de taux légaux ne le disait : c'est la
            # déperdition que l'ancienne convention prêtait à tort au
            # scénario. Ce qu'il perd est ailleurs, dans l'impôt retiré.
            assert pleine > ligne.ressources * ligne.part_contributive * (
                ligne.rapports_recettes["notionnel_liberal"]), ligne.annee
    assert vues > 40


def test_les_deux_conventions_de_recette_se_mesurent(cout: Cout, cout_assiette: Cout):
    """Ce que la convention du programme déplace, et dans quel sens.

    L'ancienne convention reste calculable, comme la pondération égale des cas
    types : c'est ce qui permet de dire de combien elle se trompait plutôt que
    d'en discuter. Elle est désormais la PLUS FAVORABLE au scénario 6, et
    l'écart ne vient pas de son taux. Deux effets s'y opposent :

    * le TAUX. Le taux plein prélevé sur l'assiette mesurée rapporte plus que
      le rapport de taux légaux appliqué à la part cotisée, parce que ce
      rapport prête au scénario la déperdition du système actuel — deux points
      et demi d'assiette qu'un taux prélevé à plat ne perd pas. Cet effet joue
      pour la convention du programme, et ``test_la_recette_du_scenario_6_est_
      son_taux_sur_l_assiette`` le tient.
    * les POSTES NON RECONDUITS. Seule la convention du programme fait sortir
      la contribution d'équilibre, les subventions et les impôts affectés :
      l'ancienne les encaisse tous. Ce second effet est le plus gros, et c'est
      lui qui renverse le signe de l'écart.

    L'ancienne convention n'est donc plus « l'ancienne façon de calculer le
    taux » : c'est un chemin qui ne porte AUCUNE des décisions de septembre
    2026. On la garde comme repère, pas comme variante.
    """
    assert cout.convention_recette == CONVENTION_RAPPORT
    assert cout_assiette.convention_recette == CONVENTION_ASSIETTE
    bascule = Parametres().annee_bascule
    fin = cout.solde.derniere_annee
    ancien = cout.solde.solde_moyen("notionnel_liberal", bascule, fin)
    nouveau = cout_assiette.solde.solde_moyen("notionnel_liberal", bascule, fin)
    # La convention du programme est la plus sévère, de près d'un point de PIB.
    assert ancien - nouveau > 0.005, (ancien, nouveau)
    # Et ce n'est pas son taux qui la rend sévère : à postes reconduits égaux,
    # le taux plein sur l'assiette rapporterait PLUS. On le vérifie année par
    # année en redonnant au scénario les trois postes qu'il ne reconduit pas.
    for annee in (2030, 2050, 2070):
        point = cout_assiette.solde.annee(annee)
        rendus = point.ressources * (point.part_contributive
                                     + point.part_subventions
                                     + point.part_impots)
        sans_decisions = (point.ressources_de("notionnel_liberal") + rendus
                          - point.retrait_par_impot)
        assert sans_decisions > cout.solde.annee(annee).ressources_de(
            "notionnel_liberal"), annee
    # Les cinq autres systèmes ne bougent pas d'un iota : la convention ne
    # touche qu'au seul scénario dont le TAUX change.
    for scenario, _ in SCENARIOS:
        if scenario == "notionnel_liberal":
            continue
        for annee in (2030, 2050, 2070):
            assert (cout.solde.annee(annee).ressources_de(scenario)
                    == pytest.approx(
                        cout_assiette.solde.annee(annee).ressources_de(scenario)))


def test_une_convention_de_recette_inconnue_est_refusee(
        depenses: DepensesRetraite, population: Population):
    with pytest.raises(ValueError, match="convention de recette inconnue"):
        calculer_cout(Simulateur(Parametres()), depenses, population,
                      convention_recette="au_doigt_mouille")


def test_la_recette_suit_le_taux(cout: Cout):
    """Le scénario 6 prélève 18 % : il ne peut pas encaisser ce qu'un système à 29 % encaisse.

    C'est la seconde façon dont une recette suit ce que le système fait, et
    elle ne joue que sur la part COTISÉE des ressources — un quart du total est
    de l'impôt affecté et des subventions, sur quoi un taux de cotisation n'a
    aucune prise.
    """
    bascule = Parametres().annee_bascule
    for ligne in cout.solde.annees:
        rapport = ligne.rapports_recettes["notionnel_liberal"]
        if ligne.annee < bascule:
            assert rapport == 1.0, ligne.annee
            continue
        assert 0.5 < rapport < 0.8, ligne.annee
        # Ce que la formule doit rendre, écrit autrement qu'elle.
        cotisees = ligne.ressources * ligne.part_contributive
        # La TVA à taux unique s'ajoute, sous l'une et l'autre convention.
        attendu = (cotisees * rapport + (ligne.ressources - cotisees) - ligne.retrait
                   + ligne.tva_de("notionnel_liberal"))
        assert ligne.ressources_de("notionnel_liberal") == pytest.approx(attendu)
        assert ligne.ressources_de("notionnel_liberal") < ligne.ressources_de(
            "notionnel_retroactif_employeur"), ligne.annee


def test_seul_le_scenario_6_change_ce_qui_est_preleve(cout: Cout):
    """Les scénarios 2 à 5 changent ce qui est PORTÉ AU COMPTE, pas ce qui est PRÉLEVÉ.

    L'employeur verse sa part dans tous les cas ; sous les scénarios 2 et 3,
    elle finance le système sans ouvrir de droit à celui qui la voit passer.
    Prêter à ces scénarios une recette diminuée serait un contresens, et c'est
    pourquoi leur rapport de recettes est écrit à un plutôt que calculé.
    """
    for ligne in cout.solde.annees:
        for scenario, _ in SCENARIOS:
            if scenario == "notionnel_liberal":
                continue
            assert ligne.rapports_recettes[scenario] == 1.0, (ligne.annee, scenario)
        for scenario in ("notionnel_retroactif", "notionnel_prospectif",
                         "notionnel_retroactif_employeur",
                         "notionnel_prospectif_employeur"):
            # Avant la bascule, les scénarios 3 et 5 sont le système actuel,
            # et n'ont rien à retirer : voir `test_la_recette_suit_le_droit`.
            # Après, ils gardent les majorations du stock qu'ils servent encore.
            prospectif = scenario in CLES_PROSPECTIVES
            avant = prospectif and ligne.annee < ligne.annee_bascule
            garde = ligne.majorations_stock if prospectif else 0.0
            attendu = (ligne.ressources if avant
                       else ligne.ressources - ligne.retrait + garde)
            assert ligne.ressources_de(scenario) == pytest.approx(attendu), (
                ligne.annee, scenario)


def test_le_taux_moyen_que_le_rapport_implique_est_celui_que_le_cor_publie(cout: Cout):
    """Contrôle externe : 18 % divisés par le rapport doivent redonner un taux réel.

    Le COR publie le taux de cotisation retraite d'un salarié non-cadre du
    privé sous le plafond, parts salariale et employeur : 27,9 % en 2025
    (figure 3.1 de son rapport annuel). La grille du dépôt mêle à ce salarié
    des fonctionnaires, dont l'employeur verse 74 % du traitement, et des
    non-salariés, qui cotisent moins : le taux moyen qu'elle implique doit
    donc TOMBER AUTOUR de ce chiffre, un peu au-dessus, et jamais loin.
    """
    bascule = Parametres().annee_bascule
    lignes = [l for l in cout.solde.annees if l.annee >= bascule + 5]
    assert lignes
    for ligne in lignes:
        taux_implique = 0.18 / ligne.rapports_recettes["notionnel_liberal"]
        assert 0.25 < taux_implique < 0.34, (ligne.annee, taux_implique)


def test_les_recettes_reactives_deplacent_le_solde_du_scenario_6(cout: Cout):
    """Ce que le chantier a déplacé, mesuré et non raconté.

    L'ancienne convention laissait au scénario 6 les ressources d'un système
    dont il remplace tous les taux. Un dictionnaire de rapports vide la
    reproduit exactement, et l'écart entre les deux est ce que la réaction des
    recettes coûte au scénario.
    """
    bascule = Parametres().annee_bascule
    fin = cout.solde.derniere_annee
    # Ce que la réaction des recettes coûte, sans la TVA à taux unique : elle
    # est une recette ajoutée, non une recette qui réagit.
    periode = [l for l in cout.solde.annees if bascule <= l.annee <= fin]
    tva = sum(l.tva_de("notionnel_liberal") for l in periode) / len(periode)
    reactif = cout.solde.solde_moyen("notionnel_liberal", bascule, fin) - tva
    fige = sum(
        ligne.ressources - ligne.retrait - ligne.depense("notionnel_liberal")
        for ligne in cout.solde.annees if bascule <= ligne.annee <= fin
    ) / len([l for l in cout.solde.annees if bascule <= l.annee <= fin])
    # Près de quatre points de PIB d'écart, et un excédent moyen qui disparaît.
    # L'excédent que l'ancienne convention affichait valait plus de trois
    # points de PIB tant que les pensions servies restaient figées en euros
    # constants ; revalorisées sur la masse salariale, elles en reprennent un.
    # Il en reste 1,8 point depuis que le volet C a cessé de faire recalculer
    # par le rapport une réversion que le modèle ne calcule pas : c'est la
    # DÉPENSE que cette correction-là déplace, et elle déplace donc les deux
    # termes de la même quantité. L'ÉCART, lui, ne mesure que la recette, et
    # n'a pas bougé.
    assert fige - reactif > 0.03
    assert fige > 0.015
    assert reactif < 0.005


def test_le_retrait_est_a_part_constante_hors_de_la_fenetre(
        cout: Cout, comptes: ComptesRetraite):
    """Avant 2013 et après la dernière année connue, la part des ressources ne bouge pas.

    Personne ne projette ce que la CNAF versera en 2070 ; une part constante
    des ressources est l'hypothèse qui n'en ajoute aucune autre, et elle se
    raccorde sans marche à l'année connue la plus proche.
    """
    solde = cout.solde
    premiere, derniere = comptes.premiere_annee_transferts, comptes.derniere_annee_transferts
    part_debut = comptes.transfert_supprime_part_pib(premiere) / comptes.ressource(premiere)
    part_fin = comptes.transfert_supprime_part_pib(derniere) / comptes.ressource(derniere)
    for ligne in solde.annees:
        part = ligne.retrait / ligne.ressources
        if ligne.annee < premiere:
            assert part == pytest.approx(part_debut), ligne.annee
        elif ligne.annee > derniere:
            assert part == pytest.approx(part_fin), ligne.annee
    assert solde.annee(solde.derniere_annee).retrait > 0.0


def test_le_bilan_se_dit_aussi_en_euros(cout: Cout):
    """« Part du PIB » ne parle qu'à qui sait ce qu'est le PIB.

    Les trois chiffres d'ouverture de la page sont donc en euros, et ils
    doivent se recomposer : ce qui rentre moins ce qui sort est le solde, et le
    PIB manquant rend zéro plutôt qu'un montant inventé.
    """
    observe = cout.solde.annee(cout.solde.derniere_annee_observee)
    assert observe.ressources_meur() == pytest.approx(observe.ressources * observe.pib)
    assert observe.depense_meur("actuel") - observe.ressources_meur() == pytest.approx(
        -observe.solde_meur("actuel"))
    # Le dernier millésime projeté est hors de la fenêtre où le PIB est publié.
    horizon = cout.solde.annee(cout.solde.derniere_annee)
    assert horizon.pib == 0.0
    assert horizon.ressources_meur() == 0.0
    assert horizon.depense_meur("actuel") == 0.0


def test_le_scenario_6_ne_reconduit_pas_la_contribution_d_equilibre_de_l_Etat(
        cout_assiette, comptes: ComptesRetraite):
    """L'État cotise à 18 % comme tout employeur, et ne verse plus d'équilibre.

    Décision du Parti libéral du 19 septembre 2026. Elle était jusque-là vraie
    par accident : la contribution d'équilibre est marquée `contributive` dans
    `equilibre.py`, donc comprise dans `part_contributive`, donc remplacée par
    les 18 % — sans que rien ne l'écrive ni ne l'empêche de changer. Ce test la
    tient.

    Le raccord n'est juste que parce que l'assiette couvre TOUTES les branches :
    les traitements des fonctionnaires y sont, et les 18 % qu'on leur applique
    sont ce que l'État verse désormais. Reconduire la contribution en plus la
    compterait deux fois.
    """
    annees = [a for a in cout_assiette.solde.annees if a.recette_par_assiette]
    assert annees, "aucune année ne suit la convention du programme"

    for point in annees:
        # 1. La contribution d'équilibre est DANS la part contributive : la
        #    part contributive dépasse donc les seules cotisations.
        part_cotisations = comptes.part("cotisations", point.annee)
        assert point.part_contributive > part_cotisations + 1e-9, (
            f"{point.annee} : la contribution d'équilibre est sortie de la part "
            "contributive, le scénario 6 la reconduirait en plus des 18 %"
        )

        # 2. Ce que le scénario 6 reconduit, c'est le COMPLÉMENT de la part
        #    contributive, des subventions d'équilibre et des impôts affectés
        #    — donc ni les cotisations, ni la contribution de l'État, ni les
        #    subventions, ni l'impôt.
        attendu = (point.ressources * point.taux_liberal / point.taux_prelevement
                   * point.facteur_assiette
                   + point.ressources * (1.0 - point.part_contributive
                                         - point.part_subventions
                                         - point.part_impots)
                   - (point.retrait - point.retrait_par_impot)
                   # La TVA à taux unique, qui n'est ni l'un ni l'autre.
                   + point.tva_de("notionnel_liberal"))
        assert point.ressources_de("notionnel_liberal") == pytest.approx(attendu)

        # 3. Les subventions d'équilibre existent bel et bien dans le système
        #    actuel : le test n'est pas vide de sens.
        assert point.part_subventions > 0.0


def test_le_rapport_ne_multiplie_que_les_droits_directs(
        cout_assiette: Cout, depenses: DepensesRetraite):
    """Volet C : la base porte la réversion, le rapport ne la décrit pas.

    Le rapport de masses est le quotient de deux masses calculées sur treize
    cas types, qui n'ont ni conjoint ni survivant : aucune réversion n'y entre,
    et ``config.py`` range la réversion depuis toujours parmi les droits que
    même l'étalon ne sert pas. La base, elle, porte les deux. Les multiplier
    l'une par l'autre revenait à recalculer à la baisse une pension que
    personne n'avait recalculée.
    """
    lignes = [l for l in cout_assiette.solde.annees if l.annee >= 2026]
    assert lignes

    for point in lignes:
        assert point.part_derives == pytest.approx(
            depenses.part_droits_derives(point.annee)), point.annee
        # Elle pèse, et elle recule : entre un vingtième et un huitième.
        assert 0.05 < point.part_derives < 0.13, point.annee

        for scenario, _ in SCENARIOS:
            directe = (point.depenses * (1.0 - point.part_derives)
                       * point.rapports[scenario])
            if scenario == "actuel":
                attendu = point.depenses
            elif scenario in CLES_PROSPECTIVES and not point.reforme_en_vigueur:
                # Avant sa bascule, une réforme prospective EST le système
                # actuel : elle en sert la réversion comme le reste.
                attendu = directe + point.depenses * point.part_derives
            else:
                attendu = directe
            assert point.depense(scenario) == pytest.approx(attendu), (
                point.annee, scenario)

    # La réversion recule sur l'horizon : c'est la projection du COR, et un
    # modèle qui la figerait dirait autre chose qu'elle.
    assert (cout_assiette.solde.annee(2070).part_derives
            < cout_assiette.solde.annee(2026).part_derives - 0.03)


def test_une_reforme_prospective_ne_retire_la_reversion_qu_a_compter_de_sa_bascule(
        cout_assiette: Cout):
    """Une réforme qui commence en 2026 n'a rien pu changer en 2010.

    Les scénarios 3 et 5 sont, par construction, le système actuel jusqu'à leur
    bascule : ils y recopient ses pensions, et
    ``test_une_reforme_prospective_ne_deplace_rien_avant_sa_bascule`` tient
    l'égalité de leurs courbes à l'euro près. Ils y servent donc sa réversion
    comme le reste.

    À compter de la bascule, ils ne la servent plus, et à personne : c'est un
    avantage non contributif, et ces scénarios les retirent tous. Les
    rétroactifs, eux, recalculent tout le monde depuis 1941 et ne la servent
    jamais.
    """
    bascule = Parametres().annee_bascule
    avant = [l for l in cout_assiette.solde.annees if l.annee < bascule]
    apres = [l for l in cout_assiette.solde.annees if l.annee >= bascule]
    assert avant and apres

    for point in avant:
        assert not point.reforme_en_vigueur, point.annee
        for scenario in CLES_PROSPECTIVES:
            entiere = (point.depenses * (1.0 - point.part_derives)
                       * point.rapports[scenario]
                       + point.depenses * point.part_derives)
            assert point.depense(scenario) == pytest.approx(entiere), (
                point.annee, scenario)

    # Et à partir de la bascule, les cinq scénarios notionnels sont logés à la
    # même enseigne : plus un euro de réversion, prospectifs compris.
    for point in apres:
        assert point.reforme_en_vigueur, point.annee
        for scenario, _ in SCENARIOS:
            if scenario == "actuel":
                continue
            assert point.depense(scenario) == pytest.approx(
                point.depenses * (1.0 - point.part_derives)
                * point.rapports[scenario]), (point.annee, scenario)


def test_une_reforme_prospective_garde_le_remboursement_des_majorations_qu_elle_sert(
        cout_assiette: Cout, comptes: ComptesRetraite):
    """La recette suit le droit, et le droit du stock survit à la bascule.

    Les scénarios 3 et 5 rendent telles quelles les pensions liquidées au plus
    tard l'année de leur bascule, majorations pour enfants comprises : ils les
    servent donc encore, et la branche famille continue de les leur
    rembourser, au prorata de ce que ces pensions pèsent dans la masse. Ils
    perdaient tout le remboursement jusqu'au 23 septembre 2026, près de deux
    dixièmes de point de PIB l'année de la bascule. Un scénario rétroactif, qui
    recalcule tout le monde, n'en garde rien.
    """
    bascule = Parametres().annee_bascule
    avenir = cout_assiette.avenir
    parts = [avenir.annee(a).part_stock for a in range(bascule, HORIZON + 1)]
    # Presque tout le stock la première année, rien à l'horizon, et jamais de
    # retour : une pension liquidée avant la bascule ne se crée pas après.
    assert parts[0] > 0.9, parts[0]
    assert parts[-1] < 0.01, parts[-1]
    assert all(suivante <= courante + 1e-12
               for courante, suivante in zip(parts, parts[1:])), parts

    ligne = cout_assiette.solde.annee(bascule)
    attendu = (comptes.versement_ligne(bascule, "cnaf_majorations")
               * avenir.annee(bascule).part_stock)
    assert ligne.majorations_stock == pytest.approx(attendu, rel=1e-12)
    assert 0.001 < ligne.majorations_stock < ligne.versements["famille"]
    for scenario in CLES_PROSPECTIVES:
        # Même rapport de recette qu'un rétroactif : l'écart est ce
        # remboursement, et lui seul, rangé dans la ligne de la famille.
        assert ligne.ressources_de(scenario) == pytest.approx(
            ligne.ressources_de("notionnel_retroactif") + ligne.majorations_stock,
            rel=1e-12), scenario
        assert ligne.postes_ressources(scenario)["transferts_famille"] == pytest.approx(
            ligne.majorations_stock, rel=1e-12), scenario
    assert ligne.postes_ressources("notionnel_retroactif")["transferts_famille"] == 0.0


def test_le_systeme_actuel_garde_sa_base_intacte(cout_assiette: Cout):
    """La ventilation ne doit rien déplacer du scénario 1, qui est le réel.

    Son rapport vaut un partout ; la formule le rendrait de toute façon, mais
    une identité qui tient par accident d'arrondi n'est pas une identité. Le
    solde du scénario 1 est le solde PUBLIÉ par le COR, et c'est ce qui permet
    de lire les cinq autres à côté de lui.
    """
    for point in cout_assiette.solde.annees:
        assert point.depense("actuel") == point.depenses, point.annee
        assert point.rapports["actuel"] == 1.0, point.annee
    for point in cout_assiette.annees:
        assert point.cout("actuel") == point.pensions, point.annee


def test_les_postes_somment_au_total_de_chaque_systeme(cout_assiette: Cout):
    """Le tableau poste par poste est le bilan écrit ligne à ligne, rien d'autre.

    Pour chaque système et chaque année, les six postes du COR somment aux
    ressources que ``ressources_de`` compte, et droit direct plus réversion
    somment à la dépense. Les « dont » ventilent un poste sans s'y ajouter. Un
    dix-millième de tolérance : les parts publiées par le COR sont arrondies au
    cent-millième et ne somment à un qu'à cela près.

    Aucune ligne n'est négative, mais cela n'est exigé qu'à compter de la
    première année où les payeurs sont lus : avant, le fonds de solidarité
    vieillesse est reconduit à sa part de 2013, année où il finançait encore
    le minimum contributif, sur un poste « impôts » qui faisait alors moitié
    moins, et ce qui reste de ce poste une fois le fonds retiré passe sous
    zéro de cinq centièmes de point en 2002-2004. La page ne montre jamais
    ces années-là ; le tableau est celui de la bascule.
    """
    from retraite_notionnelle.cout import (
        DONT_IMPOTS, DONT_TRANSFERTS, POSTES_DEPENSES, POSTES_RESSOURCES,
    )
    premiere_lue = ComptesRetraite(RACINE_DONNEES).premiere_annee_transferts
    for point in cout_assiette.solde.annees:
        for scenario, _ in SCENARIOS:
            postes = point.postes_ressources(scenario)
            assert set(postes) == set(POSTES_RESSOURCES) | set(DONT_TRANSFERTS) | set(DONT_IMPOTS)
            somme = sum(postes[code] for code in POSTES_RESSOURCES)
            assert somme == pytest.approx(point.ressources_de(scenario), rel=1e-4), (
                point.annee, scenario)
            assert sum(postes[code] for code in DONT_TRANSFERTS) == pytest.approx(
                postes["transferts"], abs=1e-12)
            assert sum(postes[code] for code in DONT_IMPOTS) == pytest.approx(
                postes["impots_et_taxes"], abs=1e-12)
            if point.annee >= premiere_lue:
                for code in POSTES_RESSOURCES + DONT_TRANSFERTS + DONT_IMPOTS:
                    assert postes[code] >= -1e-12, (point.annee, scenario, code)
            depenses_ = point.postes_depenses(scenario)
            assert set(depenses_) == set(POSTES_DEPENSES)
            assert depenses_["droits_directs"] + depenses_["droits_derives"] == pytest.approx(
                point.depense(scenario), abs=1e-12)
            assert depenses_["garantie_vieillesse"] >= 0.0


def test_la_proposition_ne_compte_que_les_cotisations_et_deux_restes(cout_assiette: Cout):
    """Ce que le tableau montre de la proposition, décision par décision.

    À compter de la bascule, sous la convention de l'assiette : la contribution
    d'équilibre, les subventions et les impôts affectés sont à zéro ; les
    cotisations valent 18 % de l'assiette, c'est-à-dire les ressources
    multipliées par le rapport des deux taux ; ce que la branche famille verse
    est retiré des transferts, ce que l'assurance chômage verse y reste — le
    compte porte les cotisations qu'elle paie —, et les autres produits sont
    reconduits tels quels. Avant la bascule, la proposition prélève les taux
    réels comme tout le monde, et sa réversion n'est jamais servie.
    """
    bascule = cout_assiette.solde.annees[0].annee_bascule
    for point in cout_assiette.solde.annees:
        postes = point.postes_ressources("notionnel_liberal")
        actuel = point.postes_ressources("actuel")
        assert postes["transferts_famille"] == 0.0
        assert postes["transferts_chomage"] == pytest.approx(actuel["transferts_chomage"])
        assert postes["transferts_chomage"] > 0.0
        assert postes["transferts_autres"] == pytest.approx(actuel["transferts_autres"])
        assert postes["autres_produits"] == pytest.approx(actuel["autres_produits"])
        assert point.postes_depenses("notionnel_liberal")["droits_derives"] == 0.0
        if point.annee >= bascule:
            assert point.recette_par_assiette
            assert postes["contribution_equilibre_etat"] == 0.0
            assert postes["subventions_equilibre"] == 0.0
            # Des impôts, la seule TVA à taux unique (23 septembre 2026).
            assert postes["impots_et_taxes"] == postes["impots_tva"]
            assert postes["cotisations"] == pytest.approx(
                point.ressources * point.taux_liberal / point.taux_prelevement
                * point.facteur_assiette)
            assert point.postes_depenses("notionnel_liberal")["garantie_vieillesse"] > 0.0
        else:
            assert postes["cotisations"] == pytest.approx(actuel["cotisations"])
            assert postes["contribution_equilibre_etat"] == pytest.approx(
                actuel["contribution_equilibre_etat"])
            assert postes["impots_solidarite"] == 0.0
            assert postes["impots_et_taxes"] == pytest.approx(
                actuel["impots_et_taxes"] - actuel["impots_solidarite"])


def test_le_systeme_actuel_encaisse_chaque_poste_du_cor(cout_assiette: Cout, comptes):
    """Pour l'étalon, le tableau redonne la structure publiée, et ses « dont »
    sont ce que chaque payeur a réellement versé la dernière année connue."""
    derniere = comptes.derniere_annee_transferts
    point = cout_assiette.solde.annee(derniere)
    postes = point.postes_ressources("actuel")
    for code in CODES_POSTES:
        assert postes[code] == pytest.approx(comptes.part(code, derniere) * point.ressources)
    assert postes["transferts_famille"] == pytest.approx(
        comptes.transfert_part_pib("famille", derniere))
    assert postes["transferts_chomage"] == pytest.approx(
        comptes.transfert_part_pib("chomage", derniere))
    assert postes["impots_solidarite"] == pytest.approx(
        comptes.transfert_part_pib("solidarite", derniere))
    # Le retrait ne compte que les payeurs dont le droit est supprimé : la
    # branche famille et le fonds, et non l'assurance chômage.
    assert postes["transferts_famille"] + postes[
        "impots_solidarite"] == pytest.approx(point.retrait)
    assert point.postes_depenses("actuel")["droits_derives"] == pytest.approx(
        point.depenses * point.part_derives)
    assert point.postes_depenses("actuel")["garantie_vieillesse"] == 0.0


def test_la_garantie_vieillesse_ne_recoit_aucune_reversion(cout_assiette: Cout):
    """Elle n'est pas un système, et une allocation différentielle n'a pas de veuve.

    La garantie est calculée, comme les rapports, sur les seuls droits directs
    des cas types : son rapport multiplie donc la part directe de la base, et
    rien ne lui est ajouté. Lui ajouter la réversion la gonflerait d'un
    dixième sans qu'aucun calcul l'ait produite.
    """
    for point in cout_assiette.solde.annees:
        attendu = (point.depenses * (1.0 - point.part_derives)
                   * point.rapports[COMPOSANTE_GARANTIE])
        assert point.depense(COMPOSANTE_GARANTIE) == pytest.approx(attendu)
        # Et elle est strictement plus petite que si on la lui ajoutait.
        if point.part_derives > 0.0 and point.rapports[COMPOSANTE_GARANTIE] > 0.0:
            assert point.depense(COMPOSANTE_GARANTIE) < point.depenses


def test_les_deux_conventions_de_reversion_se_mesurent():
    """Ce que le choix suédois rend au regard du choix italien.

    Le dépôt NE sert PAS la réversion dans les scénarios notionnels : c'est un
    avantage non contributif, et ils les retirent tous. C'est le chemin de la
    Suède, où un compte notionnel ne verse qu'à son titulaire. Celui de
    l'Italie, qui partage le capital du défunt, reste calculable pour qu'on
    sache ce qu'il vaut — comme `convention_recette="rapport"`.

    Il vaut cher, et il vaut la MÊME chose pour les cinq : 1,19 point de PIB
    chacun. Ce n'est pas une coïncidence. La réversion retirée ne dépend
    d'aucun rapport de masses — c'est une part de la base, la même pour tous —,
    et les cinq scénarios la retirent sur la même fenêtre, celle qui commence à
    la bascule. Le solde moyen de la projection ne commence pas avant.
    """
    def fait(convention: str) -> Cout:
        return memoire.cout(Parametres(), convention_recette=CONVENTION_ASSIETTE,
                            convention_reversion=convention)

    servie = fait(CONVENTION_REVERSION_SERVIE).solde
    supprimee = fait(CONVENTION_REVERSION_SUPPRIMEE).solde
    debut, fin = servie.premiere_annee_projetee, servie.derniere_annee

    # Le scénario 1 ne bouge pas d'un iota : la convention ne porte que sur les
    # systèmes notionnels, le réel servant évidemment la réversion.
    assert (servie.solde_moyen("actuel", debut, fin)
            == pytest.approx(supprimee.solde_moyen("actuel", debut, fin)))

    # Les cinq autres y gagnent, et tous exactement la même chose : la
    # réversion retirée est une part de la BASE, qui ne dépend d'aucun rapport.
    gains = []
    for scenario, _ in SCENARIOS:
        if scenario == "actuel":
            continue
        gains.append(supprimee.solde_moyen(scenario, debut, fin)
                     - servie.solde_moyen(scenario, debut, fin))
    assert max(gains) - min(gains) < 1e-9, gains
    assert 0.011 < gains[0] < 0.013, gains[0]


def test_une_convention_de_reversion_inconnue_est_refusee(
        depenses: DepensesRetraite, population: Population):
    with pytest.raises(ValueError, match="convention de réversion inconnue"):
        calculer_cout(Simulateur(Parametres()), depenses, population,
                      convention_reversion="partagee")


def test_les_deux_producteurs_trouvent_la_meme_part_de_reversion(
        depenses: DepensesRetraite):
    """Le seul contrôle externe dont cette part dispose, et il est bon.

    ``part_droits_derives`` est construite à partir du classeur du COR ;
    ``pensions_droits`` est la ventilation que la DREES publie elle-même, et
    la DREES est le producteur de la dépense. Deux enquêtes, deux périmètres,
    deux nomenclatures, cinq années communes — et les parts s'écartent de six
    centièmes de point au plus.

    C'est ce qui permet de se servir de la première sur 2010-2070 sans la
    prendre pour argent comptant : là où on peut la vérifier, elle tient.
    """
    communes = range(2020, 2025)
    pire = 0.0
    for annee in communes:
        direct = depenses.pensions_droit("direct", annee)
        derive = depenses.pensions_droit("derive", annee)
        assert direct > 0.0 and derive > 0.0, annee
        part_drees = derive / (direct + derive)
        pire = max(pire, abs(part_drees - depenses.part_droits_derives(annee)))
    assert pire < 0.001, pire

    # Et la somme des deux n'est pas le risque entier : il porte aussi le
    # minimum vieillesse, la dépendance et la retraite supplémentaire.
    pensions = (depenses.pensions_droit("direct", 2024)
                + depenses.pensions_droit("derive", 2024))
    assert pensions < depenses.depense(2024)
    assert pensions > 0.9 * depenses.depense(2024)


def test_le_scenario_6_ne_reconduit_pas_les_impots_et_taxes_affectes(
        cout_assiette, comptes: ComptesRetraite):
    """Un impôt affecté n'acquiert de droits à personne.

    Décision du Parti libéral du 19 septembre 2026, et il faut dire par quel
    argument elle NE passe PAS : on avait cru un temps que ce poste compensait
    les allègements généraux de cotisations patronales, qu'un système sans
    exonération ne consent pas. Le dépôt a établi que c'est faux — la TVA qui
    compense ces allègements finance la branche maladie, et le compte de la
    CNAV n'en porte aucune ligne. L'argument qui vaut est celui des 18 % : un
    compte notionnel ne crédite que ce qui est assis sur un revenu d'activité.

    Le poste pèse 14,1 % des ressources, 57 milliards en 2024, et le retirer
    coûte 1,40 point de PIB au solde moyen du scénario 6.
    """
    annees = [a for a in cout_assiette.solde.annees if a.recette_par_assiette]
    assert annees

    for point in annees:
        assert point.part_impots == pytest.approx(
            comptes.part("impots_et_taxes", point.annee))
        assert point.part_impots > 0.10, point.annee
        # Le poste est bien sorti : le rendre au scénario lui redonne sa
        # taille exacte, moins la CSG du fonds de solidarité, qui repartirait
        # alors dans le retrait. Plus d'un point de PIB, toutes années.
        sans = point.ressources_de("notionnel_liberal")
        rendu = point.ressources * point.part_impots - point.retrait_par_impot
        assert rendu > 0.01, point.annee
        assert sans + rendu > sans


def test_la_csg_du_fonds_de_solidarite_ne_sort_qu_une_fois(
        cout_assiette, comptes: ComptesRetraite):
    """Elle est dans le poste retiré ET dans le retrait : on la compterait deux fois.

    Ce que le fonds de solidarité vieillesse verse aux régimes est financé par
    une CSG qui est DANS les impôts et taxes affectés — 34 % du poste en 2024.
    Tant que le poste restait, retirer le versement était la seule façon de
    faire sortir cette CSG ; maintenant que le poste s'en va en entier, le
    retirer encore la ferait sortir deux fois. ``retrait_par_impot`` est cette
    somme, et le retrait la rend.
    """
    annees = [a for a in cout_assiette.solde.annees if a.recette_par_assiette]
    assert annees

    for point in annees:
        attendu = comptes.recette_non_acquise(point.annee, par_impot=True)
        assert point.retrait_par_impot == pytest.approx(attendu), point.annee
        # Elle est une part réelle du retrait, jamais sa totalité : la CNAF
        # verse, elle, par un transfert, et sa recette est dans le poste
        # « transferts », qui reste.
        assert 0.0 < point.retrait_par_impot < point.retrait, point.annee
        hors_impot = comptes.recette_non_acquise(point.annee, par_impot=False)
        assert (point.retrait_par_impot + hors_impot
                == pytest.approx(point.retrait)), point.annee
        # Et c'est bien le seul organisme dans ce cas.
        par_impot = [o.code for o in ORGANISMES if o.recette_par_impot]
        assert par_impot == ["solidarite"]


def test_le_scenario_6_ne_reconduit_pas_les_subventions_d_equilibre(
        cout_assiette, comptes: ComptesRetraite):
    """La fusion des régimes fait disparaître l'objet même de la subvention.

    Une subvention d'équilibre comble le compte d'un régime dont les cotisants
    ont disparu avant les retraités — la SNCF, les mines, les marins. Le
    scénario 6 fusionne tous les régimes : **il n'y a plus de retraité sans
    cotisants dès lors qu'il n'y a plus qu'un régime**, et donc plus rien à
    équilibrer par le budget. Décision du Parti libéral du 19 septembre 2026.

    Elle coûte 0,24 point de PIB au solde moyen du scénario 6 — de −0,88 % à
    −1,12 % —, et c'est la mesure de ce que l'ancienne hypothèse lui offrait.
    """
    annees = [a for a in cout_assiette.solde.annees if a.recette_par_assiette]
    assert annees

    for point in annees:
        # Ce que le scénario 6 encaisse, plus les subventions, redonne ce qu'il
        # encaissait quand on les lui reconduisait : l'écart est exactement
        # elles, et rien d'autre.
        sans = point.ressources_de("notionnel_liberal")
        avec = sans + point.ressources * point.part_subventions
        assert avec > sans, f"{point.annee} : les subventions ne pèsent rien"
        assert point.part_subventions == pytest.approx(
            comptes.part("subventions_equilibre", point.annee))


# -- la dette : ce que le solde accumule, si rien ne s'ajuste ------------------


@pytest.fixture(scope="module")
def dette(cout):
    return cout.dette


def test_la_dette_part_de_zero_a_la_derniere_annee_observee(dette, solde):
    """Le stock ne compte que les soldes À VENIR : il commence à zéro.

    Ni la dette ni les réserves d'aujourd'hui n'y sont, et la première ligne
    est la première année projetée du solde.
    """
    assert dette.annee_depart == solde.derniere_annee_observee
    assert dette.premiere_annee == solde.premiere_annee_projetee
    assert dette.derniere_annee == solde.derniere_annee
    for scenario, _ in SCENARIOS:
        assert dette.stock(scenario, dette.annee_depart) == 0.0


def test_la_recurrence_de_la_dette_se_verifie_ligne_a_ligne(dette, solde):
    """stock(t) = stock(t−1) ÷ (1 + n) + intérêts(t) − solde(t), et rien d'autre.

    Les intérêts sont ceux du stock de l'année précédente au taux de l'année,
    érodés par la croissance ; le solde est exactement celui de ``Solde``.
    """
    precedent = {scenario: 0.0 for scenario, _ in SCENARIOS}
    for ligne in dette.annees:
        attendu = solde.annee(ligne.annee)
        assert attendu is not None and attendu.projete
        for scenario, _ in SCENARIOS:
            assert ligne.solde(scenario) == attendu.solde(scenario)
            assert ligne.interet(scenario) == pytest.approx(
                precedent[scenario] * ligne.taux / (1.0 + ligne.croissance))
            assert ligne.stock(scenario) == pytest.approx(
                precedent[scenario] / (1.0 + ligne.croissance)
                + ligne.interet(scenario) - ligne.solde(scenario))
            precedent[scenario] = ligne.stock(scenario)


def test_le_taux_est_celui_de_la_courbe_et_la_croissance_celle_du_pib(dette, avenir):
    """Rien n'est prévu : le taux est le forward à un an, le PIB celui d'Avenir."""
    courbe = Simulateur(Parametres()).courbe_taux
    assert dette.date_courbe == courbe.date
    assert dette.derniere_annee_cotee == courbe.annee + courbe.maturite_maximale
    for ligne in dette.annees:
        assert ligne.taux == courbe.placement(ligne.annee - 1, 1).taux
        assert ligne.croissance == pytest.approx(
            avenir.annee(ligne.annee).pib / avenir.annee(ligne.annee - 1).pib - 1.0)
    # Au-delà de la dernière maturité cotée, le taux est prolongé à plat et la
    # fiabilité tombe ; le stock, lui, n'est jamais mieux qu'estimé.
    assert dette.derniere_annee > dette.derniere_annee_cotee
    assert dette.fiabilite_taux == Fiabilite.ESTIMEE
    assert dette.fiabilite == Fiabilite.ESTIMEE


def test_la_dette_publique_est_posee_sous_le_stock_sans_y_entrer(
        dette, solde, comptes: ComptesRetraite):
    """Ce que le pays doit déjà, lu chez l'INSEE, et ce que chaque système y ajoute.

    La série observée est recopiée telle quelle jusqu'à l'année de départ, et
    pas au-delà : le stock d'un système ne se cumule pas dans une dette qu'il
    n'a pas faite. Le point de départ est la dernière valeur publiée avant ou
    à l'année de départ, et ``dette_publique`` n'est rien d'autre que ce point
    plus le stock — tenu à plat, sans intérêts ni croissance propres, parce que
    le reste des administrations publiques n'est pas modélisé.
    """
    observee = dette.dette_publique_observee
    assert observee, "la série de l'INSEE n'est pas arrivée jusqu'à la dette"
    assert min(observee) == comptes.dette_publique.premiere_annee == 1995
    assert max(observee) <= dette.annee_depart
    assert dette.annee_dette_publique == max(observee)
    for annee, valeur in observee.items():
        assert valeur == pytest.approx(comptes.dette_publique(annee)), annee
        # Une part de PIB, jamais un pourcentage : elle s'additionne au stock.
        assert 0.5 < valeur < 1.5, annee
    depart = dette.dette_publique_depart
    assert depart == pytest.approx(observee[dette.annee_dette_publique])
    for scenario, _ in SCENARIOS:
        assert dette.dette_publique(scenario, dette.annee_depart) == pytest.approx(depart)
        for ligne in dette.annees:
            assert dette.dette_publique(scenario, ligne.annee) == pytest.approx(
                depart + ligne.stock(scenario)), (scenario, ligne.annee)
    # L'écart entre deux systèmes, à l'échelle du pays, est exactement l'écart
    # entre leurs stocks : la dette de départ, commune, s'efface.
    fin = dette.derniere_annee
    assert (dette.dette_publique("notionnel_liberal", fin)
            - dette.dette_publique("actuel", fin)) == pytest.approx(
        dette.horizon("notionnel_liberal") - dette.horizon("actuel"))


def test_sans_serie_la_dette_publique_est_nulle_et_le_stock_intact(
        dette, solde, avenir):
    """La série est un ornement du stock, jamais une condition de son calcul."""
    courbe = Simulateur(Parametres()).courbe_taux
    sans = calculer_dette(solde, avenir, courbe)
    assert sans.dette_publique_observee == {}
    assert sans.annee_dette_publique == 0
    assert sans.dette_publique_depart == 0.0
    for scenario, _ in SCENARIOS:
        assert sans.horizon(scenario) == pytest.approx(dette.horizon(scenario))
        assert sans.dette_publique(scenario, sans.derniere_annee) == pytest.approx(
            dette.horizon(scenario))


def test_le_systeme_actuel_accumule_une_dette_et_les_notionnels_l_inverse(dette, solde):
    """Un solde toujours négatif fait une dette qui ne cesse de croître.

    Le système actuel est en déficit chaque année projetée : son stock monte
    d'année en année, culmine à l'horizon, et dépasse ce que les seuls déficits
    additionnés donneraient — c'est l'effet des intérêts. Les deux systèmes
    notionnels rétroactifs encaissent plus qu'ils ne servent : leur stock est
    une réserve, négative, et ils n'ont pas de pic.
    """
    stocks = [ligne.stock("actuel") for ligne in dette.annees]
    assert all(b > a for a, b in zip(stocks, stocks[1:]))
    assert dette.pic("actuel").annee == dette.derniere_annee
    assert dette.premiere_annee_decroissance("actuel") is None
    assert dette.horizon("actuel") > dette.cumul_soldes("actuel") > 0.0
    assert dette.cumul_interets("actuel") > 0.0
    for scenario in ("notionnel_retroactif", "notionnel_retroactif_employeur"):
        assert solde.premiere_annee_equilibree(scenario) == dette.premiere_annee
        assert dette.horizon(scenario) < 0.0
        assert dette.pic(scenario) is None


def test_un_point_de_taux_deplace_la_dette_dans_le_sens_attendu(cout):
    """Plus le taux est haut, plus une dette grossit et plus une réserve rapporte."""
    courbe = Simulateur(Parametres()).courbe_taux
    moins = calculer_dette(cout.solde, cout.avenir, courbe, -0.01)
    plus = calculer_dette(cout.solde, cout.avenir, courbe, 0.01)
    assert moins.ecart_taux == -0.01 and plus.ecart_taux == 0.01
    for ligne, bas, haut in zip(cout.dette.annees, moins.annees, plus.annees):
        assert bas.taux == pytest.approx(ligne.taux - 0.01)
        assert haut.taux == pytest.approx(ligne.taux + 0.01)
    assert moins.horizon("actuel") < cout.dette.horizon("actuel") < plus.horizon("actuel")
    assert (moins.horizon("notionnel_retroactif")
            > cout.dette.horizon("notionnel_retroactif")
            > plus.horizon("notionnel_retroactif"))


def test_sans_solde_la_dette_est_vide():
    """Sans comptes, pas de solde ; sans solde, pas de stock — et rien ne plante."""
    sans = memoire.cout(Parametres(), comptes=False, assiette=False)
    assert sans.solde.annees == []
    assert sans.dette.annees == []
    assert isinstance(sans.dette, Dette)
    assert sans.dette.horizon("actuel") == 0.0


# -- le pilier capitalisé de tous les cotisants -------------------------------


def test_le_pilier_de_tous_les_cotisants_est_donne_par_euro_verse(cout):
    """Rien avant la bascule ; ensuite des rapports, jamais un niveau : les
    frais sont une fraction des versements, l'encours grossit, les rentes
    montent avec les liquidations."""
    from retraite_notionnelle.config import Parametres
    bascule = Parametres().annee_bascule
    avenir = cout.avenir
    assert all(ligne.pilier is None for ligne in avenir.annees if ligne.annee < bascule)
    lignes = [ligne for ligne in avenir.annees if ligne.annee >= bascule]
    assert lignes and all(ligne.pilier is not None for ligne in lignes)
    premier = lignes[0].pilier
    assert 0.0 < premier.frais_versement < 0.02
    assert premier.encours == pytest.approx(1.0 - premier.frais_versement, rel=1e-6)
    # L'encours par euro versé grossit d'une décennie à l'autre — pas
    # forcément d'une année à l'autre, la démographie des versements bouge.
    encours = {ligne.annee: ligne.pilier.encours for ligne in lignes}
    assert encours[2030] < encours[2040] < encours[2050] < encours[2060] < encours[2070]
    assert encours[2070] > 20.0
    rentes = [ligne.pilier.rentes for ligne in lignes]
    assert rentes[0] < 0.01 and rentes[-1] > 1.0
    for ligne in lignes:
        pilier = ligne.pilier
        assert 0.0 <= pilier.frais_rentes <= pilier.rentes_brutes
        assert pilier.frais_gestion >= 0.0
        assert pilier.niveaux(100.0)["versements"] == 100.0
        assert pilier.niveaux(100.0)["frais"] == pytest.approx(100.0 * pilier.frais)


def test_le_taux_de_frais_sur_l_encours_baisse_avec_les_paliers(cout):
    """Par euro d'encours, la gestion coûte moins en 2070 qu'en 2030 : les
    paliers et la convergence du stock font leur travail dans l'agrégat."""
    avenir = cout.avenir
    tot_2030 = avenir.annee(2030).pilier.taux_frais_encours
    tot_2070 = avenir.annee(2070).pilier.taux_frais_encours
    assert 0.004 < tot_2030 < 0.008
    assert tot_2070 < tot_2030 / 2


# -- ce que les comptes financent d'une pension promise -----------------------


def _poids_plats(annees: int) -> tuple[float, ...]:
    """Une courbe de survie qui ne décroît pas : chaque année pèse autant.

    Elle isole ce que la fonction fait du BILAN de ce qu'elle fait de la
    MORTALITÉ. Les tests qui portent sur la pondération se donnent une courbe
    décroissante, et disent alors dans quel sens elle déplace le résultat.
    """
    return tuple(1.0 for _ in range(annees))


def test_le_coefficient_servi_est_la_moyenne_des_annees_de_service(solde):
    """Une pension se sert vingt ans : le coefficient de la seule année du
    départ FLATTE qui part tôt, puisqu'il ignore les années où le déficit se
    creuse. C'est exactement ce que la moyenne corrige, et le test le mesure
    plutôt que de l'affirmer."""
    assiette = AssietteActivite(RACINE_DONNEES)
    part = financer(solde, assiette, "actuel", 2030, _poids_plats(20))
    attendu = sum(solde.annee(annee).coefficient("actuel")
                  for annee in range(2030, 2050)) / 20
    assert part.coefficient == pytest.approx(attendu, rel=1e-12)
    assert part.coefficient_depart == pytest.approx(
        solde.annee(2030).coefficient("actuel"), rel=1e-12)
    # Le déficit se creuse : la moyenne est sous le coefficient du départ.
    assert part.coefficient < part.coefficient_depart
    assert part.depart_couvert and part.entiere


def test_la_survie_pese_les_premieres_annees_plus_que_les_dernieres(solde):
    """Une courbe décroissante ramène le coefficient VERS celui du départ :
    les années lointaines, où le manque est le plus grand, sont celles où il
    reste le moins de monde pour le subir. Le sens de l'effet est le seul
    résultat attendu ici, et il doit être celui-là."""
    assiette = AssietteActivite(RACINE_DONNEES)
    plats = financer(solde, assiette, "actuel", 2030, _poids_plats(20))
    decroissants = financer(solde, assiette, "actuel", 2030,
                            tuple(1.0 - rang / 20 for rang in range(20)))
    assert plats.coefficient < decroissants.coefficient < plats.coefficient_depart


def test_la_fenetre_s_arrete_a_l_horizon_du_COR_et_le_dit(solde):
    """Une pension liquidée en 2060 se sert au-delà de 2070, que le COR ne
    projette pas. Les années manquantes ne sont pas inventées : elles sortent
    de la moyenne, et ``part_couverte`` dit combien de la rente elles pèsent —
    sans quoi la page afficherait un coefficient tiré de trois années sur
    trente sans le dire."""
    assiette = AssietteActivite(RACINE_DONNEES)
    part = financer(solde, assiette, "actuel", 2060, _poids_plats(30))
    assert part.derniere_annee == solde.derniere_annee
    assert part.part_couverte == pytest.approx(11 / 30, rel=1e-12)
    assert not part.entiere


def test_un_depart_anterieur_aux_comptes_ne_rend_rien_de_son_annee(solde):
    """Les comptes du COR commencent en 2002. Un départ de 1990 n'a donc rien
    à lire à sa date, et la fonction le dit de deux façons : la fenêtre
    commence à la première année couverte, et ``depart_couvert`` est faux. Un
    départ que même la fin du service ne rattrape pas ne rend rien du tout."""
    assiette = AssietteActivite(RACINE_DONNEES)
    part = financer(solde, assiette, "actuel", 1990, _poids_plats(30))
    assert part.premiere_annee == solde.premiere_annee
    assert not part.depart_couvert
    assert financer(solde, assiette, "actuel", 1950, _poids_plats(20)) is None


def test_les_trois_leviers_comblent_le_meme_trou(solde):
    """Rogner les pensions, lever des cotisations, emprunter : trois lectures
    d'un seul manque, et la page les affiche côte à côte. Ce test vérifie
    qu'elles se déduisent bien l'une de l'autre, faute de quoi elles
    diraient trois tailles différentes du même écart."""
    assiette = AssietteActivite(RACINE_DONNEES)
    part = financer(solde, assiette, "actuel", 2050, _poids_plats(20))
    ligne = solde.annee(2050)
    assert part.manque_pib == pytest.approx(-ligne.solde("actuel"), rel=1e-12)
    # Le manque, ramené à la dépense, EST ce que le coefficient de l'année
    # retire : c'est la même division, écrite dans l'autre sens.
    assert part.manque_pib / ligne.depense("actuel") == pytest.approx(
        1 - part.coefficient_depart, rel=1e-12)
    assert part.points_assiette == pytest.approx(
        part.manque_pib / assiette.part_pib(assiette.derniere_annee), rel=1e-12)
    assert part.hausse_cotisations == pytest.approx(
        part.manque_pib / (ligne.ressources_de("actuel") * ligne.part_contributive),
        rel=1e-12)


def test_la_capitalisation_ne_porte_pas_le_manque_de_la_repartition(solde):
    """Une rente capitalisée sort d'un placement déjà constitué : un déficit
    de la répartition ne l'atteint pas. La multiplier par le coefficient
    ferait porter à l'épargne le manque du système qui ne la détient pas."""
    assiette = AssietteActivite(RACINE_DONNEES)
    part = financer(solde, assiette, "notionnel_liberal", 2050, _poids_plats(20))
    assert part.servie(1000.0, 0.0) == pytest.approx(1000.0 * part.coefficient)
    assert part.servie(1000.0, 1000.0) == pytest.approx(1000.0)
    assert part.servie(1000.0, 400.0) == pytest.approx(
        600.0 * part.coefficient + 400.0)


def test_le_bilan_fige_dit_ce_que_le_modele_calcule(solde):
    """La table de ``data/derive/equilibre.json`` est relue par les deux côtés
    du portage, et le calcul complet ne se refait jamais chez le lecteur. Elle
    doit donc dire EXACTEMENT ce que le modèle calcule — au dixième de
    millième près, ce qui est la précision d'un JSON écrit puis relu.

    Le solde de ce module suit la convention de recette par RAPPORT, celui du
    site la convention par ASSIETTE : seule la colonne de la proposition en
    dépend, et le test ne compare donc que les trois autres. Ce que la table
    ne peut pas porter, un test de bout en bout le tient — le paquet est
    reconstruit et comparé octet par octet dans ``tests/test_web.py``.
    """
    bilan = charger_bilan(RACINE_DONNEES)
    assert bilan.premiere_annee == solde.premiere_annee
    assert bilan.derniere_annee == solde.derniere_annee
    assert bilan.premiere_annee_projetee == solde.premiere_annee_projetee
    for scenario in ("actuel", "notionnel_retroactif",
                     "notionnel_retroactif_employeur"):
        for annee in (solde.premiere_annee, 2026, 2050, solde.derniere_annee):
            attendu = solde.annee(annee).coefficient(scenario)
            assert bilan.annee(annee).coefficient(scenario) == pytest.approx(
                attendu, rel=1e-9), f"{scenario} en {annee}"
            assert bilan.annee(annee).depense(scenario) == pytest.approx(
                solde.annee(annee).depense(scenario), rel=1e-9), f"{scenario} en {annee}"
    # Ce que « Pourquoi changer » et « Partager » lisent du système actuel,
    # sans plus refaire le coût : la recette, le PIB publié et le solde en
    # euros de la dernière année observée.
    for annee in (solde.premiere_annee, solde.derniere_annee_observee, 2050,
                  solde.derniere_annee):
        ligne, figee = solde.annee(annee), bilan.annee(annee)
        assert figee.ressources == pytest.approx(ligne.ressources, rel=1e-9)
        assert figee.pib == pytest.approx(ligne.pib, rel=1e-9)
        assert figee.solde_meur("actuel") == pytest.approx(
            ligne.solde_meur("actuel"), rel=1e-9), annee
    assert bilan.annee(solde.derniere_annee_observee).pib > 0
    assert bilan.annee(solde.derniere_annee).pib == 0.0


def test_les_exemples_figes_sont_ce_que_le_modele_simule():
    """Les carrières d'exemple de « Pourquoi changer », simulées une fois par
    ``scripts/construire_donnees.py``, par le portage (action 161, étape 5) :
    la page les lit sans simuler, et elles doivent donc dire, au bit près, ce
    que le portage simule pour leur saisie, gardée avec chacune en champs, que
    ``pont.saisies`` lit comme le site (étape 6) ; la confrontation du portage
    au moteur Python, pour une saisie, est à ``tests/test_pont.py``. Que la
    page en demande une autre, elle ne trouve rien et simule ; le test du
    paquet, dans ``tests/test_web.py``, dit alors que le paquet est à refaire."""
    from retraite_notionnelle import pont
    from retraite_notionnelle.donnees.bilan import SCENARIO_FINANCE, FicheFigee

    bilan = charger_bilan(RACINE_DONNEES)
    assert len(bilan.exemples) == 3
    lus, refus = pont.saisies([{"cle": str(rang), "saisie": dict(figee.saisie)}
                               for rang, figee in enumerate(bilan.exemples)],
                              [SCENARIO_FINANCE])
    assert not refus
    for rang, figee in enumerate(bilan.exemples):
        lu = lus[str(rang)]
        assert bilan.exemple(dict(figee.saisie)) is figee
        assert figee.fiche == FicheFigee(**lu["fiche"]), figee.saisie
        assert (figee.coefficient_euros_constants, figee.pension_actuel,
                figee.pension_financee) == (
            lu["coefficient_euros_constants"], lu["pension_annuelle"],
            lu["pensions"][SCENARIO_FINANCE]), figee.saisie
    assert bilan.exemple({**bilan.exemples[0].saisie, "naissance": 1991}) is None


def test_le_systeme_actuel_promet_plus_qu_il_n_encaisse_sur_tout_l_horizon(solde):
    """Le fait que le site affiche, et qui a motivé le second chiffre : le
    système actuel est en déficit toutes les années projetées, et le manque
    grandit. Si cela cessait d'être vrai — un COR qui reviendrait à
    l'équilibre —, la page dirait autre chose, et ce test doit tomber pour
    qu'on s'en aperçoive plutôt que de le lire sur le site."""
    projetees = solde.projetees()
    assert all(ligne.coefficient("actuel") < 1.0 for ligne in projetees)
    assert (projetees[-1].coefficient("actuel")
            < projetees[0].coefficient("actuel"))
    assert solde.premiere_annee_equilibree("actuel") is None


# -- les variantes de compte du COR -------------------------------------------
#
# Le dépôt lisait le scénario de référence quel que soit le scénario demandé.
# La croissance déplaçait donc la dépense des systèmes notionnels, qui est
# CALCULÉE, sans déplacer celle du droit en vigueur, qui est EMPRUNTÉE — et le
# rapport des deux, qui monte à juste titre, était appliqué à un niveau gelé.


def test_les_variantes_declarees_sont_celles_du_fichier():
    """Les noms de variantes SONT les noms de scénarios du fichier d'hypothèses.

    C'est ce qui permet à ``variante_du_scenario`` de se passer d'une table de
    correspondance : un scénario qui n'est pas une variante est, par
    construction, celui sous lequel le compte principal est publié.
    """
    import yaml

    macro = RACINE_DONNEES / "reference" / "macro"
    hypotheses = yaml.safe_load(
        (macro / "hypotheses_projection.yaml").read_text(encoding="utf-8"))
    attendues = set(hypotheses["scenarios"]) - {hypotheses["scenario_par_defaut"]}
    attendues |= set(hypotheses.get("variantes_chomage") or {})
    assert set(variantes_disponibles(macro)) == attendues


def test_le_scenario_de_reference_ne_prend_aucune_variante():
    macro = RACINE_DONNEES / "reference" / "macro"
    assert variante_du_scenario("cor_reference", macro) == VARIANTE_REFERENCE
    assert variante_du_scenario(None, macro) == VARIANTE_REFERENCE
    for nom in variantes_disponibles(macro):
        assert variante_du_scenario(nom, macro) == nom


def test_une_variante_inconnue_est_refusee():
    """Jamais un repli silencieux sur la référence : il rendrait deux courbes
    identiques sans que rien ne le dise, ce qui est le défaut qu'on répare."""
    with pytest.raises(ValueError, match="variante de compte inconnue"):
        ComptesRetraite(RACINE_DONNEES, variante="cor_productivite_moyenne")


def test_une_variante_ne_touche_pas_aux_annees_observees(comptes):
    """Ce que le passé a été ne dépend d'aucune hypothèse."""
    for nom in variantes_disponibles(RACINE_DONNEES / "reference" / "macro"):
        variante = ComptesRetraite(RACINE_DONNEES, variante=nom)
        for annee in range(comptes.premiere_annee, comptes.derniere_annee_observee + 1):
            assert variante.depense(annee) == comptes.depense(annee), (nom, annee)
            assert variante.ressource(annee) == comptes.ressource(annee), (nom, annee)


def test_une_variante_deplace_la_depense_projetee(comptes):
    """Et dans le sens que le COR publie : plus de productivité, moins de
    dépense en part de PIB — une pension indexée sur les prix décroche d'un PIB
    qui accélère. Plus de chômage, davantage de dépense."""
    horizon = comptes.derniere_annee
    haute = ComptesRetraite(RACINE_DONNEES, variante="cor_productivite_haute")
    basse = ComptesRetraite(RACINE_DONNEES, variante="cor_productivite_basse")
    assert haute.depense(horizon) < comptes.depense(horizon) < basse.depense(horizon)
    chomage_bas = ComptesRetraite(RACINE_DONNEES, variante="cor_chomage_bas")
    chomage_haut = ComptesRetraite(RACINE_DONNEES, variante="cor_chomage_haut")
    assert (chomage_bas.depense(horizon) < comptes.depense(horizon)
            < chomage_haut.depense(horizon))


def test_la_recette_ne_gagne_presque_rien_a_la_croissance(comptes):
    """LE RÉSULTAT QUI SURPREND, ET QUI EST JUSTE.

    On attend d'une croissance plus forte qu'elle apporte plus de recettes.
    En euros, oui. En PART DE PIB — l'unité de tout le bilan —, non : l'assiette
    et le PIB montent du même pas, et le fichier d'hypothèses s'interdit de
    déformer le partage de la valeur ajoutée. Le COR trouve même un léger
    RECUL, parce que sous sa convention EPR l'État verse ce qu'il faut pour
    équilibrer les régimes de fonctionnaires, et qu'il leur en faut moins.

    Le test borne l'effet plutôt que de le figer : ce qui doit tenir est qu'il
    reste d'un ordre de grandeur en dessous de ce que la dépense fait.
    """
    horizon = comptes.derniere_annee
    haute = ComptesRetraite(RACINE_DONNEES, variante="cor_productivite_haute")
    sur_la_recette = abs(haute.ressource(horizon) - comptes.ressource(horizon))
    sur_la_depense = abs(haute.depense(horizon) - comptes.depense(horizon))
    assert sur_la_recette < 0.002
    assert sur_la_depense > 5 * sur_la_recette


def test_le_solde_d_une_variante_est_celui_de_sa_variante(comptes):
    """``solde`` passe par les accesseurs et non par les séries : les prendre
    aux séries redonnerait le solde de la référence sous toutes les variantes."""
    horizon = comptes.derniere_annee
    haute = ComptesRetraite(RACINE_DONNEES, variante="cor_productivite_haute")
    assert haute.solde(horizon) == pytest.approx(
        haute.ressource(horizon) - haute.depense(horizon))
    assert haute.solde(horizon) > comptes.solde(horizon)


def test_la_proposition_ne_perd_plus_un_point_a_la_croissance():
    """CE QUE LA CORRECTION VALAIT, ET POURQUOI IL EN RESTE.

    Sous l'ancien raccord, le solde de la proposition en 2070 allait de +0,42 à
    −0,72 point de PIB entre les variantes basse et haute de productivité : la
    croissance coûtait 1,14 point à la proposition sans qu'aucun mécanisme
    économique le justifie. Sous le compte de chaque variante, l'amplitude
    tombe sous le demi-point.

    IL EN RESTE, ET C'EST ATTENDU. Un compte notionnel indexé sur la masse
    salariale est neutre à la croissance en part de PIB ; le droit en vigueur,
    indexé sur les prix, en profite. La proposition gagne donc MOINS que le
    droit constant à ce que la croissance soit forte, et ce résultat-là lui
    appartient. Ce que le test borne est l'amplitude résiduelle, pas son signe.

    ELLE A GRANDI LE 4 OCTOBRE 2026, POUR LA MÊME RAISON. Au-delà du dernier
    barème, la valeur d'achat du point Agirc-Arrco suit désormais le salaire
    moyen, comme ses accords le veulent (fiche ``agirc_arrco_valeur_achat``) :
    une croissance plus forte n'achète plus de points de surcroît au droit en
    vigueur, dont la valeur de service suit les prix. Sa masse recule donc
    davantage en part de PIB quand la croissance est forte, le rapport de la
    proposition à elle monte d'autant, et l'amplitude est passée de 0,44 à
    0,61 point. La borne suit, aux trois quarts d'un point : loin du 1,14 de
    l'ancien raccord, qu'elle doit continuer d'attraper.
    """
    soldes = {}
    for scenario in ("cor_productivite_basse", "cor_reference",
                     "cor_productivite_haute"):
        # Les comptes du COR de chaque scénario, comme la page : la mémoire les
        # prend dans la variante que le scénario réclame (variante_du_scenario).
        cout = memoire.cout(Parametres().avec(scenario_projection=scenario))
        ligne = cout.solde.annees[-1]
        soldes[scenario] = ligne.solde("notionnel_liberal")
    amplitude = soldes["cor_productivite_basse"] - soldes["cor_productivite_haute"]
    assert 0.0 < amplitude < 0.0075, soldes


def test_le_plafond_de_l_axe_est_lu_sur_les_variantes():
    """Et non écrit en dur : un 20 % figé tiendrait jusqu'au prochain rapport
    du COR, puis mentirait en silence. Le plafond doit couvrir la variante la
    plus dépensière, et c'est elle qui le fixe."""
    macro = RACINE_DONNEES / "reference" / "macro"
    plafond = depense_maximale_toutes_variantes(RACINE_DONNEES)
    comptes = ComptesRetraite(RACINE_DONNEES)
    sommets = [comptes.depense(a) for a in comptes.annees()]
    for nom in variantes_disponibles(macro):
        variante = ComptesRetraite(RACINE_DONNEES, variante=nom)
        sommets += [variante.depense(a) for a in comptes.annees()]
    assert plafond == pytest.approx(max(sommets))
    assert plafond > comptes.depense(comptes.derniere_annee)


# -- l'âge légal de la proposition -------------------------------------------


@pytest.fixture(scope="module")
def cout_sans_age_legal():
    """La page Coût sans l'âge légal de 65 ans : la proposition part aux âges
    du scénario 4."""
    return memoire.cout(Parametres(age_legal_liberal=None),
                        convention_recette=CONVENTION_ASSIETTE)


def test_l_age_legal_ne_touche_rien_avant_la_bascule(cout_assiette, cout_sans_age_legal):
    """Une cohorte partie avant la bascule l'est sans report, même quand sa
    génération de la grille, elle, est reportée : les années d'avant la
    réforme restent au centime ce qu'elles étaient."""
    bascule = Parametres().annee_bascule
    avec, sans = cout_assiette.solde, cout_sans_age_legal.solde
    for ligne in avec.annees:
        if ligne.annee >= bascule:
            continue
        autre = sans.annee(ligne.annee)
        for scenario, _ in SCENARIOS:
            assert ligne.solde(scenario) == pytest.approx(autre.solde(scenario), abs=1e-12)
        assert ligne.facteur_assiette == 1.0


def test_l_age_legal_ne_touche_que_la_proposition(cout_assiette, cout_sans_age_legal):
    for ligne in cout_assiette.solde.projetees():
        autre = cout_sans_age_legal.solde.annee(ligne.annee)
        for scenario, _ in SCENARIOS:
            if scenario == "notionnel_liberal":
                continue
            assert ligne.solde(scenario) == pytest.approx(autre.solde(scenario), abs=1e-12)


def test_l_age_legal_ameliore_le_solde_de_la_proposition(cout_assiette, cout_sans_age_legal):
    """Moins de pensions servies, plus de cotisations encaissées : le solde
    moyen de la proposition s'améliore, et l'assiette s'élargit après la
    bascule."""
    avec, sans = cout_assiette.solde, cout_sans_age_legal.solde
    debut, fin = avec.premiere_annee_projetee, avec.derniere_annee
    assert (avec.solde_moyen("notionnel_liberal", debut, fin)
            > sans.solde_moyen("notionnel_liberal", debut, fin) + 0.002)
    bascule = Parametres().annee_bascule
    apres = [ligne for ligne in avec.annees if ligne.annee > bascule]
    assert apres and all(ligne.facteur_assiette > 1.0 for ligne in apres)
    for ligne in apres:
        autre = sans.annee(ligne.annee)
        assert autre.facteur_assiette == 1.0
        assert (ligne.ressources_de("notionnel_liberal")
                > autre.ressources_de("notionnel_liberal"))


def test_une_cohorte_prend_le_volet_de_son_cote_de_la_bascule():
    """La génération de la grille part en 2027 et se reporte ; la cohorte née
    deux ans plus tôt part en 2025, avant la bascule, et ne se reporte pas."""
    from retraite_notionnelle.cout import Pensionne, VoletLiberal

    reporte = VoletLiberal(annee_liquidation=2030, annee_ouverture_garantie=2030,
                           pension=2.0, ressources_garantie=2.0)
    sans_report = VoletLiberal(annee_liquidation=2027, annee_ouverture_garantie=2030,
                               pension=1.0, ressources_garantie=1.0)
    pensionne = Pensionne(code="x", generation=1965, annee_liquidation=2027,
                          pensions={}, propre=reporte, autre=sans_report,
                          bascule=2026)
    assert pensionne.volet(-2) is sans_report
    assert pensionne.volet(-1) is reporte
    assert pensionne.volet(0) is reporte
    assert pensionne.volet(2) is reporte
    seul = replace(pensionne, autre=None)
    assert seul.volet(-2) is reporte


def test_chaque_cohorte_part_l_annee_que_lui_donne_le_droit_de_sa_generation(population):
    """La grille ne simule qu'une génération sur cinq, et faisait partir les
    cinq cohortes qu'elle représente à son âge de départ, la date décalée
    d'autant : le salarié de janvier 1965 part en 2028 avec 170 trimestres,
    sous la suspension de 2026, quand nés en 1966 et 1967 il lui en faut 172,
    et la grille comptait leurs départs un an trop tôt (note du 18 octobre
    2026, « la grille »). Chaque cohorte part désormais l'année que le droit
    de sa génération lui donne (``Pensionne.departs``) : têtes et masses ne la
    comptent qu'à partir de là, dans tous les systèmes et dans chaque régime,
    sa pension se revalorise depuis et sa survie se compte de là. La
    proposition la reporte à l'âge légal, le sien, quand elle reporte la
    génération de la grille, et la fait partir avec elle sinon ; le côté de la
    bascule est celui de son départ. Sans dates, celles de la grille."""
    from retraite_notionnelle.cout import (
        CLES_CAS_TYPES, TETES_TOUTES, Pensionne, VoletLiberal, _masses, _masses_regimes,
        coefficient_servi)

    simulateur = Simulateur(Parametres()).pour_la_projection()
    revalorisation = RevalorisationServie(simulateur, 2000, 2040)
    # Le salarié de 1965 part à 63 ans et demi, en 2028 ; la proposition le
    # reporte à 65 ans, en 2030.
    reporte = VoletLiberal(annee_liquidation=2030, annee_ouverture_garantie=2030,
                           pension=1.0, ressources_garantie=1.0)
    grille = Pensionne(code="x", generation=1965, annee_liquidation=2028,
                       pensions={cle: 1.0 for cle in CLES_CAS_TYPES}, propre=reporte,
                       parts_regimes={"regime_general": 1.0}, bascule=2026)
    datee = replace(grille, departs=(2026, 2027, 2028, 2030, 2031))
    decalages = range(-2, 3)
    assert [grille.liquidation(d) for d in decalages] == [2026, 2027, 2028, 2029, 2030]
    assert [datee.liquidation(d) for d in decalages] == [2026, 2027, 2028, 2030, 2031]
    for pensionne in (grille, datee):
        assert [pensionne.depart_liberal(d) for d in decalages] == [
            2028, 2029, 2030, 2031, 2032]

    # En 2030, la cohorte de 1967 n'est pas encore partie.
    effectifs = [population.effectif(2030 - 1965 - d, 2030) for d in decalages]
    masses, _, tetes = _masses([grille], population, 2030, {"x": 1.0}, revalorisation)
    datees, _, tetes_datees = _masses([datee], population, 2030, {"x": 1.0}, revalorisation)
    assert tetes[TETES_TOUTES] == pytest.approx(sum(effectifs), rel=1e-12)
    assert tetes_datees[TETES_TOUTES] == pytest.approx(sum(effectifs[:4]), rel=1e-12)
    parties = (2026, 2027, 2028, 2030)
    servis = [coefficient_servi({"regime_general": 1.0}, revalorisation, depart, 2030)
              for depart in parties]
    assert datees["actuel"] == pytest.approx(
        sum(e * c for e, c in zip(effectifs, servis)), rel=1e-12)
    assert regle_revalorisation("notionnel_retroactif") == REGLE_STOCK
    stock = [revalorisation.coefficient_stock(depart, 2030, prospectif=False)
             for depart in parties]
    assert datees["notionnel_retroactif"] == pytest.approx(
        sum(e * c for e, c in zip(effectifs, stock)), rel=1e-12)
    # La proposition part à 65 ans des deux façons.
    assert datees["notionnel_liberal"] == pytest.approx(masses["notionnel_liberal"], rel=1e-12)
    regimes, tetes_regimes = _masses_regimes([datee], population, 2030, {"x": 1.0},
                                             revalorisation)
    assert sum(tetes_regimes.values()) == pytest.approx(sum(effectifs[:4]), rel=1e-12)
    assert sum(regimes.values()) == pytest.approx(datees["actuel"], rel=1e-12)

    # Le cadre de 1965 part à 65 ans, en 2030, et la proposition avec lui ;
    # né en 1966 ou en 1967, il part à 66 ans : en 2032, la cohorte de 1967
    # n'est partie dans aucun système.
    avec_lui = VoletLiberal(annee_liquidation=2030, annee_ouverture_garantie=2030,
                            pension=1.0, ressources_garantie=1.0)
    cadre = replace(grille, annee_liquidation=2030, propre=avec_lui,
                    departs=(2028, 2029, 2030, 2032, 2033))
    assert [cadre.depart_liberal(d) for d in decalages] == [2028, 2029, 2030, 2032, 2033]
    effectifs = [population.effectif(2032 - 1965 - d, 2032) for d in decalages]
    masses, _, tetes = _masses([cadre], population, 2032, {"x": 1.0}, revalorisation)
    assert tetes[TETES_TOUTES] == pytest.approx(sum(effectifs[:4]), rel=1e-12)
    assert regle_revalorisation("notionnel_liberal") == REGLE_STOCK
    assert masses["notionnel_liberal"] == pytest.approx(
        masses["notionnel_retroactif"], rel=1e-12)
    _, _, tetes = _masses([replace(cadre, departs=())], population, 2032, {"x": 1.0},
                          revalorisation)
    assert tetes[TETES_TOUTES] == pytest.approx(sum(effectifs), rel=1e-12)

    # Le cadre de 1960 part à 64 ans, en 2024 ; né en 1961, il part en 2026,
    # après la bascule, et non en 2025 : la proposition le reporte à 65 ans.
    avant = VoletLiberal(annee_liquidation=2024, annee_ouverture_garantie=2025,
                         pension=1.0, ressources_garantie=1.0)
    apres = VoletLiberal(annee_liquidation=2025, annee_ouverture_garantie=2025,
                         pension=2.0, ressources_garantie=2.0)
    cadre_1960 = Pensionne(code="x", generation=1960, annee_liquidation=2024, pensions={},
                           propre=avant, autre=apres, bascule=2026,
                           departs=(2022, 2023, 2024, 2026, 2027))
    assert [cadre_1960.volet(d) is apres for d in decalages] == [
        False, False, False, True, True]
    assert [replace(cadre_1960, departs=()).volet(d) is apres for d in decalages] == [
        False, False, False, False, True]
    assert [cadre_1960.depart_liberal(d) for d in decalages] == [2022, 2023, 2024, 2026, 2027]

    # La survie se compte depuis le départ de la cohorte.
    vivante = replace(datee, survies=((1.0, 0.9, 0.8, 0.7),) * 5)
    assert (vivante.survie(2, 2031), vivante.survie(2, 2032)) == (1.0, 0.9)
    assert replace(vivante, departs=()).survie(2, 2032) == 0.8


def test_la_grille_date_chaque_cohorte_au_droit_de_sa_generation():
    """Le salarié au salaire moyen entré à 21 ans : né en janvier 1963, 1964
    ou 1965, la suspension de la loi de financement pour 2026 lui demande 170
    trimestres (L. 161-17-3) — il part à 63 ans et demi, en 2026, 2027 et
    2028 ; né en 1966 ou en 1967, il lui en faut 172, 43 ans — il part à 64
    ans, en 2030 et en 2031. La grille, qui ne simule que la génération 1965,
    faisait partir ces deux-là en 2029 et en 2030."""
    from retraite_notionnelle.cout import _departs

    simulateur = Simulateur(Parametres()).pour_la_projection()
    salarie = next(cas for cas in GRILLE_DU_COUT if cas.code == "salaire_moyen")
    assert _departs(simulateur, salarie, 1965, 2028) == (2026, 2027, 2028, 2030, 2031)


def test_nee_toute_l_annee_une_cohorte_ne_compte_que_ce_qui_en_est_parti(population):
    """La grille fait naître ses cas types en janvier, et chaque cohorte compte
    toute l'année de son départ, dans ses têtes comme dans ses masses : partie
    en novembre, elle compte au 31 décembre tous ses retraités, et une année
    entière de leur pension (note « l'entrée dans l'emploi » du 19 octobre
    2026, point 3). Née toute l'année (``calculer_cout(naissances=
    "toute_l_annee")``), sa part née le mois ``b`` part le mois ``m + b - 1``,
    ``m`` étant celui de sa part née en janvier, et touche chaque année les
    mois qui suivent son départ.

    Posé à la main. Partie en novembre (m = 11) : au 31 décembre, ses nés de
    janvier et de février, deux douzièmes ; servis cette année-là, deux mois
    et un mois, trois mois sur cent quarante-quatre, 1/48 d'une année de
    pension ; l'année suivante, douze mois à ces deux-là, puis de douze à
    trois aux nés de mars à décembre, 99/144. Partie en février (m = 2), à un
    âge rond : onze douzièmes, 66/144, puis l'année entière. Au total, la
    cohorte part en moyenne m - 1 + 5,5 mois après le 1er janvier, et c'est ce
    que ses masses perdent.

    Puis un couple : ses cohortes parties en 2026, 2027, 2028, 2030 et 2031,
    celles de 2027 et de 2028 en novembre ; la proposition reporte à son âge
    légal, en février, celle de 2026, et sa garantie s'ouvre avec ce départ.
    En 2028 : les têtes et les masses de chaque système, celles de chaque
    régime, et les têtes qui divisent sa caisse. Sans mois, la grille."""
    from retraite_notionnelle.cout import (
        CLES_CAS_TYPES, TETES_GARANTIE, TETES_TOUTES, Pensionne, VoletLiberal, _masses,
        _masses_regimes, _partie, _servie, _tetes_par_poids, coefficient_servi)

    assert [_partie(annee, 2028, 11) for annee in (2027, 2028, 2029)] == [
        0.0, pytest.approx(2 / 12), 1.0]
    assert [_servie(annee, 2028, 11) for annee in (2027, 2028, 2029, 2030)] == [
        0.0, pytest.approx(1 / 48), pytest.approx(99 / 144), 1.0]
    assert _partie(2028, 2028, 2) == pytest.approx(11 / 12)
    assert [_servie(annee, 2028, 2) for annee in (2028, 2029)] == [
        pytest.approx(66 / 144), 1.0]
    for mois in range(1, 13):
        perdu = sum(1.0 - _servie(annee, 2028, mois) for annee in range(2028, 2032))
        assert perdu == pytest.approx((mois - 1 + 5.5) / 12), mois
    assert [_partie(annee, 2028, None) for annee in (2027, 2028)] == [0.0, 1.0]
    assert [_servie(annee, 2028, None) for annee in (2027, 2028)] == [0.0, 1.0]

    simulateur = Simulateur(Parametres()).pour_la_projection()
    revalorisation = RevalorisationServie(simulateur, 2000, 2040)
    reporte = VoletLiberal(annee_liquidation=2030, annee_ouverture_garantie=2030,
                           pension=1.0, ressources_garantie=1.0)
    grille = Pensionne(code="x", generation=1965, annee_liquidation=2028,
                       pensions={cle: 1.0 for cle in CLES_CAS_TYPES}, propre=reporte,
                       parts_regimes={"regime_general": 1.0}, bascule=2026,
                       departs=(2026, 2027, 2028, 2030, 2031))
    nee = replace(grille, mois=(8, 11, 11, 2, 2), mois_age_legal=2, mois_65_ans=2)
    decalages = range(-2, 3)
    assert [nee.depart_liberal(d) for d in decalages] == [2028, 2029, 2030, 2031, 2032]
    effectifs = [population.effectif(2028 - 1965 - d, 2028) for d in decalages]
    parties = (1.0, 1.0, 2 / 12, 0.0, 0.0)
    servies = (1.0, 99 / 144, 1 / 48, 0.0, 0.0)
    departs = (2026, 2027, 2028)

    masses, _, tetes = _masses([grille], population, 2028, {"x": 1.0}, revalorisation)
    nees, _, tetes_nees = _masses([nee], population, 2028, {"x": 1.0}, revalorisation)
    assert tetes[TETES_TOUTES] == pytest.approx(sum(effectifs[:3]), rel=1e-12)
    assert tetes_nees[TETES_TOUTES] == pytest.approx(
        sum(e * p for e, p in zip(effectifs, parties)), rel=1e-12)
    servis = [coefficient_servi({"regime_general": 1.0}, revalorisation, depart, 2028)
              for depart in departs]
    assert masses["actuel"] == pytest.approx(
        sum(e * c for e, c in zip(effectifs, servis)), rel=1e-12)
    assert nees["actuel"] == pytest.approx(
        sum(e * s * c for e, s, c in zip(effectifs, servies, servis)), rel=1e-12)
    stock = [revalorisation.coefficient_stock(depart, 2028, prospectif=False)
             for depart in departs]
    assert nees["notionnel_retroactif"] == pytest.approx(
        sum(e * s * c for e, s, c in zip(effectifs, servies, stock)), rel=1e-12)
    # La proposition ne sert en 2028 que la cohorte de 2026, partie en février.
    assert nees["notionnel_liberal"] == pytest.approx(
        masses["notionnel_liberal"] * 66 / 144, rel=1e-12)
    assert tetes[TETES_GARANTIE] == pytest.approx(effectifs[0], rel=1e-12)
    assert tetes_nees[TETES_GARANTIE] == pytest.approx(effectifs[0] * 11 / 12, rel=1e-12)

    regimes, tetes_regimes = _masses_regimes([nee], population, 2028, {"x": 1.0},
                                             revalorisation)
    assert sum(tetes_regimes.values()) == pytest.approx(tetes_nees[TETES_TOUTES], rel=1e-12)
    assert sum(regimes.values()) == pytest.approx(nees["actuel"], rel=1e-12)
    assert _tetes_par_poids([nee], population)(2028) == pytest.approx(
        {"x": tetes_nees[TETES_TOUTES]}, rel=1e-12)
    assert _tetes_par_poids([grille], population)(2028) == pytest.approx(
        {"x": tetes[TETES_TOUTES]}, rel=1e-12)


def test_nee_toute_l_annee_chaque_cohorte_part_le_mois_que_lui_donne_son_droit():
    """Les mois d'une cohorte née toute l'année sont ceux que le droit de sa
    génération donne à sa part née en janvier, comme la grille
    (``cout._nees_toute_l_annee``) : le salarié au salaire moyen né de 1963 à
    1965 part à 63 ans et demi, né en 1966 et 1967 à 64 ans (L. 161-17-3,
    sous la suspension de 2026, ``test_la_grille_date_chaque_cohorte_au_droit_de_sa_generation``) ;
    la proposition le reporte à 65 ans, âge où sa garantie s'ouvre. Une
    pension prend effet le premier jour d'un mois, au plus tôt celui qui suit
    l'âge atteint, ou le jour même pour l'assuré né le 1er (R. 351-37) : né le
    jour du mois que le vocabulaire présume, en août et en février, ou, né le
    1er, en juillet et en janvier. Rien d'autre ne change."""
    from retraite_notionnelle.cout import Pensionne, VoletLiberal, _nees_toute_l_annee
    from retraite_notionnelle.noyau import vocabulaire

    salarie = next(cas for cas in GRILLE_DU_COUT if cas.code == "salaire_moyen")
    volet = VoletLiberal(annee_liquidation=2030, annee_ouverture_garantie=2030,
                         pension=1.0, ressources_garantie=1.0)
    grille = Pensionne(code="salaire_moyen", generation=1965, annee_liquidation=2028,
                       pensions={}, propre=volet, departs=(2026, 2027, 2028, 2030, 2031))
    [nee] = _nees_toute_l_annee(Simulateur(Parametres()), (salarie,), [grille], "droit")
    le_premier = vocabulaire.presomptions()["jour_de_naissance"]["valeur"] == 1
    demi, rond = (7, 1) if le_premier else (8, 2)
    assert nee.mois == (demi, demi, demi, rond, rond)
    assert (nee.mois_age_legal, nee.mois_65_ans) == (rond, rond)
    assert replace(nee, mois=(), mois_age_legal=0, mois_65_ans=0) == grille


def test_une_convention_de_naissance_inconnue_est_refusee(depenses, population):
    with pytest.raises(ValueError, match="naissances inconnues"):
        calculer_cout(Simulateur(Parametres()), depenses, population,
                      naissances="en_mars")


def test_une_cohorte_partie_avant_la_bascule_recoit_le_scenario_4():
    """La génération de la grille part au 1er février 2026, la cohorte née un
    an plus tôt en février 2025 : sa proposition est le scénario 4 — ni mois
    au taux unique, ni pilier —, et la garantie ne regarde que cette pension.
    Jusqu'au 28 septembre 2026, elle héritait de la grille son mois de 2026
    au taux unique et son pilier."""
    from retraite_notionnelle.cout import VoletLiberal, _avant_la_bascule

    grille = VoletLiberal(
        annee_liquidation=2026, annee_ouverture_garantie=2026, pension=1.01,
        ressources_garantie=1.02, cotisations={2025: 8.0, 2026: 0.7},
        assiette={2025: 40.0, 2026: 3.3}, pilier={2026: (0.4, 0.0, 0.0, 0.4)},
        rente_pilier=(0.02, 0.01), rente_garantie=0.01)
    avant = _avant_la_bascule(grille, 1.0)
    assert (avant.pension, avant.ressources_garantie, avant.rente_garantie) == (
        1.0, 1.0, 0.0)
    assert avant.pilier == {} and avant.rente_pilier == (0.0, 0.0)
    assert (avant.annee_liquidation, avant.annee_ouverture_garantie) == (2026, 2026)
    assert avant.cotisations == grille.cotisations


def test_avant_la_bascule_la_proposition_depense_ce_que_depense_le_scenario_4(
        cout_assiette):
    """Aucun retraité d'avant la bascule n'a de droit au taux unique : la
    dépense contributive des deux scénarios est la même, au centime, chaque
    année qui la précède. La garantie, financée par l'impôt, est à part."""
    bascule = Parametres().annee_bascule
    avant = [ligne for ligne in cout_assiette.solde.annees if ligne.annee < bascule]
    assert avant
    for ligne in avant:
        assert ligne.depense_meur("notionnel_liberal") == pytest.approx(
            ligne.depense_meur("notionnel_retroactif_employeur"), rel=1e-12), ligne.annee


# -- la part des reportés en emploi ------------------------------------------


def test_deux_volets_se_melent_par_tete():
    """Une cohorte dont le quart travaille jusqu'à l'âge légal et le reste
    l'attend sans activité : chaque montant est la moyenne pondérée des deux,
    année par année, et un volet pris en entier est rendu tel quel."""
    from retraite_notionnelle.cout import VoletLiberal

    en_emploi = VoletLiberal(
        annee_liquidation=2030, annee_ouverture_garantie=2030, pension=4.0,
        ressources_garantie=5.0, cotisations={2028: 8.0, 2029: 8.0},
        assiette={2028: 40.0, 2029: 40.0}, pilier={2029: (4.0, 0.4, 0.2, 40.0)},
        rente_pilier=(2.0, 1.6), rente_garantie=1.0)
    sans_activite = VoletLiberal(
        annee_liquidation=2030, annee_ouverture_garantie=2030, pension=2.0,
        ressources_garantie=3.0, cotisations={2028: 8.0}, assiette={2028: 40.0},
        pilier={2029: (0.0, 0.0, 0.2, 36.0)}, rente_pilier=(1.0, 0.8),
        rente_garantie=0.5)
    quart = en_emploi.melange(sans_activite, 0.25)
    assert quart.pension == pytest.approx(2.5)
    assert quart.ressources_garantie == pytest.approx(3.5)
    assert quart.cotisations == pytest.approx({2028: 8.0, 2029: 2.0})
    assert quart.assiette == pytest.approx({2028: 40.0, 2029: 10.0})
    assert quart.pilier[2029] == pytest.approx((1.0, 0.1, 0.2, 37.0))
    assert quart.rente_pilier == pytest.approx((1.25, 1.0))
    assert quart.rente_garantie == pytest.approx(0.625)
    assert en_emploi.melange(sans_activite, 1.0) is en_emploi
    assert en_emploi.melange(sans_activite, 0.0) is sans_activite
    with pytest.raises(ValueError):
        en_emploi.melange(replace(sans_activite, annee_liquidation=2031), 0.5)


@pytest.fixture(scope="module")
def cout_tous_en_emploi():
    """Le coût quand tous les reportés travaillent : le plafond, défaut
    jusqu'au 7 octobre 2026."""
    return memoire.cout(Parametres(part_reportes_en_emploi=1.0),
                        convention_recette=CONVENTION_ASSIETTE)


def test_la_part_des_reportes_en_emploi_est_celle_que_2010_a_mesuree():
    """La moitié des reportés en emploi, ce qu'a fait le recul de l'âge légal
    de 60 à 62 ans (IPP, rapport n° 61, 2025), et non plus le plafond de un,
    dans les deux moteurs ; la page Coût ne cite la source qu'à cette valeur."""
    import re
    from pathlib import Path

    js = Path(__file__).resolve().parents[1] / "moteur" / "js"
    lue = re.search(r"part_reportes_en_emploi: ([0-9.]+),",
                    (js / "config.js").read_text(encoding="utf-8"))
    assert Parametres().part_reportes_en_emploi == 0.5
    assert lue and float(lue.group(1)) == Parametres().part_reportes_en_emploi
    assert "part === 0.5" in (js / "pages.js").read_text(encoding="utf-8")


def test_la_part_des_reportes_en_emploi_elargit_l_assiette_en_proportion(
        cout_assiette, cout_tous_en_emploi, cout_sans_age_legal):
    """La moitié des reportés en emploi, le défaut : l'assiette s'élargit
    deux fois moins que quand tous travaillent, et le solde de la proposition
    se range entre celui où tous travaillent et celui où elle n'a pas d'âge
    légal. Les cinq autres systèmes ne bougent pas : la part ne touche que la
    proposition."""
    tous, moitie, sans = (cout_tous_en_emploi.solde, cout_assiette.solde,
                          cout_sans_age_legal.solde)
    for ligne in moitie.projetees():
        plein = tous.annee(ligne.annee)
        assert ligne.facteur_assiette - 1.0 == pytest.approx(
            0.5 * (plein.facteur_assiette - 1.0), abs=1e-12), ligne.annee
        for scenario, _ in SCENARIOS:
            if scenario != "notionnel_liberal":
                assert ligne.solde(scenario) == pytest.approx(
                    plein.solde(scenario), abs=1e-12), (ligne.annee, scenario)
    debut, fin = moitie.premiere_annee_projetee, moitie.derniere_annee
    moyens = [s.solde_moyen("notionnel_liberal", debut, fin) for s in (sans, moitie, tous)]
    assert moyens == sorted(moyens) and len(set(moyens)) == 3, moyens


# -- la TVA, que la proposition ne réforme plus -------------------------------


def test_par_defaut_rien_de_la_tva_ne_va_aux_retraites(cout_assiette):
    """La proposition garde les quatre taux de TVA d'aujourd'hui depuis le
    24 septembre 2026, et rien de la TVA ne va aux retraites : aucun système
    n'en reçoit, aucune année, et l'indicateur du taux qui couvrirait le
    déficit se tait."""
    from retraite_notionnelle.cout import taux_tva_requis
    from retraite_notionnelle.donnees.tva import AssietteTva

    parametres = Parametres()
    assert parametres.taux_tva_liberal == 0.0
    for ligne in cout_assiette.solde.annees:
        for scenario, _ in SCENARIOS:
            assert ligne.tva_de(scenario) == 0.0 == ligne.tva_garantie(scenario), (
                ligne.annee, scenario)
    assert taux_tva_requis(cout_assiette.solde, parametres,
                           AssietteTva(RACINE_DONNEES)) == (0.0, 0)
