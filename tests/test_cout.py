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
from dataclasses import replace

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.castypes import (
    CAS_TYPES,
    GENERATIONS,
    poids_effectifs,
    poids_egaux,
)
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.cout import (
    COMPOSANTE_GARANTIE,
    DERNIERE_GENERATION,
    HORIZON,
    PREMIERE_GENERATION,
    SCENARIOS,
    calculer_cout,
    generations,
)
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.donnees.distribution import DistributionPensions
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
    ORGANISMES,
    POSTES,
    POSTES_TRANSFERTS,
    ComptesRetraite,
)
from retraite_notionnelle.donnees.population import Population
from retraite_notionnelle.garantie import cout_garantie
from retraite_notionnelle.simulateur import Simulateur


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
def cout(depenses: DepensesRetraite, population: Population,
         comptes: ComptesRetraite):
    return calculer_cout(Simulateur(Parametres()), depenses, population, comptes)


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
    liste = generations()
    assert liste[0] == PREMIERE_GENERATION
    assert liste[-1] <= DERNIERE_GENERATION
    # Assez de générations pour que la moyenne pondérée ait un sens, et assez
    # récentes pour qu'une pension soit encore servie à l'horizon.
    assert len(liste) >= 15
    assert liste[-1] + 52 <= HORIZON


def test_le_cout_du_systeme_actuel_est_la_depense_observee(cout):
    """L'étalon n'est pas corrigé : son rapport vaut un, année après année."""
    for ligne in cout.annees:
        assert ligne.rapports["actuel"] == 1.0
        assert ligne.cout("actuel") == ligne.observee
    assert cout.cumul("actuel") == pytest.approx(cout.cumul_observe())


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

    Sur la fenêtre observée elle reste une fraction du scénario, parce que seuls
    les cas types qui liquident à 65 ans ou après la touchent : cinq des treize
    aux générations récentes, aucun à celles d'avant 1955. La borne était à 5 %
    tant que les cas types partaient tous à l'âge écrit dans la grille — ils
    partaient alors trop tôt pour voir la garantie, et un seul la voyait. Elle
    est à 15 % depuis qu'ils partent au taux plein de leur génération : le
    chiffre lu est 8,6 %, et il vient d'un défaut corrigé, non d'un défaut
    introduit.
    """
    for ligne in cout.annees + avenir.annees:
        assert 0.0 <= ligne.rapports[COMPOSANTE_GARANTIE] <= ligne.rapports["notionnel_liberal"]
    assert cout.cumul(COMPOSANTE_GARANTIE) > 0.0
    assert cout.cumul(COMPOSANTE_GARANTIE) < 0.15 * cout.cumul("notionnel_liberal")


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
    assert population.effectif(49, 2024) == 0.0
    assert population.effectif(200, 2024) == 0.0


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
    """Une réforme prospective ne peut pas revenir en arrière : chaque année
    supplémentaire remplace des pensions anciennes par des pensions nouvelles,
    et l'écart ne se referme jamais."""
    precedent = 1.0
    for ligne in avenir.annees:
        if ligne.annee < avenir.annee_bascule:
            continue
        rapport = ligne.rapports["notionnel_prospectif"]
        assert rapport <= precedent + 1e-9, ligne.annee
        precedent = rapport


def test_la_part_du_pib_reste_dans_un_ordre_de_grandeur_plausible(avenir):
    """Contrôle de vraisemblance externe, et l'écart qu'il mesure aujourd'hui.

    Le COR projette 13,9 % du PIB en 2024 et 14,2 % en 2070 pour le système
    actuel (rapport annuel de juin 2025). Le dépôt trouve 13,6 % au départ et
    19,3 % à l'arrivée : cinq points d'écart, contre quatre avant que chaque cas
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

    La fourchette reste un garde-fou : elle ne dit pas que la trajectoire est
    juste, elle dit qu'une trajectoire qui en sortirait relèverait d'une erreur
    de méthode et non d'un désaccord d'hypothèses. Elle n'a pas bougé — la
    borne haute de 20 % tient encore, de sept dixièmes de point.
    """
    for ligne in avenir.annees:
        part = ligne.part_pib("actuel")
        assert 0.10 < part < 0.20, f"{ligne.annee} : {part:.1%}"


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


def test_la_ponderation_egale_reproduit_l_ancienne_convention(depenses, population):
    """Un poids uniforme se simplifie dans le rapport des masses.

    C'est ce qui rend la variante utilisable comme TÉMOIN : si elle ne rendait
    pas exactement ce que rendait le dépôt avant la pondération, elle ne dirait
    rien de ce que celle-ci a déplacé.
    """
    egale = calculer_cout(Simulateur(Parametres()), depenses, population,
                          ponderation="egale")
    assert egale.ponderation == "egale"
    assert all(poids == pytest.approx(1 / len(CAS_TYPES))
               for poids in egale.poids.values())
    # Les deux pondérations ne donnent pas le même rapport — sans quoi l'action
    # n'aurait rien déplacé — et elles l'écartent dans des sens opposés selon
    # que la part patronale entre au compte ou non.
    reference = calculer_cout(Simulateur(Parametres()), depenses, population)
    assert (reference.cumul("notionnel_retroactif") / reference.cumul("actuel")
            < egale.cumul("notionnel_retroactif") / egale.cumul("actuel"))
    assert (reference.cumul("notionnel_retroactif_employeur")
            / reference.cumul("actuel")
            > egale.cumul("notionnel_retroactif_employeur") / egale.cumul("actuel"))


def test_une_ponderation_inconnue_est_refusee(depenses, population):
    with pytest.raises(ValueError, match="pondération inconnue"):
        calculer_cout(Simulateur(Parametres()), depenses, population,
                      ponderation="au_hasard")


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
    # 60 ans sous le décret de 2012, 60 ans et 9 mois pour la génération 1965
    # (D. 351-1-1, II, suspension de 2026 comprise), 62 ans à compter de 1971.
    for generation, attendu in ((1955, 60.0), (1960, 60.0), (1965, 60.75), (1975, 62.0)):
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
        assert age == pytest.approx(actuel.age_ouverture_droit(carriere))
        resultat = actuel.calculer(carriere)
        assert resultat.liquidation_ouverte
        assert resultat.taux_liquidation == pytest.approx(0.5)
        assert resultat.trimestres_valides >= resultat.trimestres_requis
        plus_tot = actuel.calculer(cas._carriere(simulateur, generation, age - 0.25))
        assert not plus_tot.liquidation_ouverte


def test_la_variante_absolue_reproduit_l_ancienne_grille(depenses, population):
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
    absolu = calculer_cout(simulateur, depenses, population, liquidation="absolu")
    droit = calculer_cout(simulateur, depenses, population)
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


def test_la_garantie_vue_par_les_cas_types_est_bien_plus_basse(cout, distribution):
    """Le constat qui a motivé le chiffrage sur la distribution, et ce qu'il est
    devenu.

    Les cas types ne voient la garantie que par ceux d'entre eux qui liquident à
    65 ans ou après. Le facteur qui séparait les deux chiffres se comptait en
    dizaines tant qu'un seul y parvenait ; il est de deux depuis que chaque cas
    type liquide à l'âge de SA génération, cinq des treize atteignant alors
    soixante-cinq ans. La correction a donc retiré l'essentiel de l'écart — et
    ce qui reste ne se comblera pas, parce qu'il ne vient plus d'un âge mais de
    la nature d'une grille : une allocation différentielle ne coûte que ce que
    coûte la queue basse de la distribution, et treize carrières choisies pour
    couvrir les configurations du système n'en ont pas.
    """
    annees = cout.derniere_annee - cout.premiere_annee + 1
    par_an_vu_des_cas_types = cout.cumul(COMPOSANTE_GARANTIE) / annees
    par_an_sur_la_distribution = cout_garantie(
        distribution, 16e6, 800.0).cout_annuel_meur
    assert par_an_sur_la_distribution > 1.8 * par_an_vu_des_cas_types


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


def test_le_systeme_actuel_ne_s_equilibre_jamais_et_le_notionnel_si(solde):
    """Le résultat de fond de cette section, et il tient en une ligne.

    Le système actuel reste déficitaire sur toute la fenêtre projetée du COR ;
    les deux réformes applicables — droits acquis conservés, règles nouvelles
    ensuite — repassent à l'équilibre, et le font d'autant plus vite que la
    part patronale entre au compte.
    """
    assert solde.premiere_annee_equilibree("actuel") is None
    assert solde.solde_moyen("actuel", solde.premiere_annee_projetee,
                             solde.derniere_annee) < 0.0
    for scenario in ("notionnel_prospectif", "notionnel_prospectif_employeur"):
        annee = solde.premiere_annee_equilibree(scenario)
        assert annee is not None and annee >= solde.premiere_annee_projetee
        assert solde.solde_moyen(scenario, solde.premiere_annee_projetee,
                                 solde.derniere_annee) > 0.0
    # Le scénario 5 porte plus de droits que le 3 : il s'équilibre plus tard.
    assert (solde.premiere_annee_equilibree("notionnel_prospectif_employeur")
            >= solde.premiere_annee_equilibree("notionnel_prospectif"))


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


def test_sans_comptes_le_cout_est_calcule_a_l_identique(depenses, population,
                                                        comptes, cout):
    """Les ressources sont un ajout, jamais une correction de ce qui précède."""
    sans = calculer_cout(Simulateur(Parametres()), depenses, population)
    assert sans.solde.annees == []
    assert sans.cumul("notionnel_retroactif") == pytest.approx(
        cout.cumul("notionnel_retroactif"))
    assert sans.avenir.cumul("actuel") == pytest.approx(cout.avenir.cumul("actuel"))


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
    parts presque égales —, l'Unédic trois à quatre. Ensemble, un demi-point
    de PIB que les scénarios notionnels comptent sans servir les droits que
    cela paie.
    """
    annee = comptes.derniere_annee_transferts
    assert 9_000 < comptes.transfert_organisme("famille", annee) < 13_000
    assert 2_500 < comptes.transfert_organisme("chomage", annee) < 5_000
    avpf = comptes.transfert("cnaf_avpf", annee)
    majorations = comptes.transfert("cnaf_majorations", annee)
    assert 0.7 < avpf / majorations < 1.3
    assert 0.004 < comptes.transfert_supprime_part_pib(annee) < 0.007
    # Les deux caisses ont un droit supprimé : la recette suit le droit.
    assert all(organisme.droit_supprime for organisme in ORGANISMES)


def test_les_deux_caisses_n_expliquent_pas_tout_le_poste_transferts(
        comptes: ComptesRetraite):
    """La ventilation est une partie du poste, jamais plus, et plus de la moitié.

    Le poste « transferts » du COR contient aussi l'assurance maladie, l'État
    et quelques versements plus petits : la branche famille et l'assurance
    chômage doivent en expliquer l'essentiel sans le dépasser. Un dépassement
    dirait que les deux séries n'ont plus le même périmètre.
    """
    for annee in comptes.annees_transferts():
        if annee > comptes.derniere_annee_ventilee:
            continue
        ventilee = sum(comptes.transfert_part_ressources(o.code, annee)
                       for o in ORGANISMES)
        poste = comptes.part("transferts", annee)
        assert 0.5 * poste < ventilee < poste, annee


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
    """Les scénarios notionnels ne comptent pas ce que la CNAF et l'Unédic versent.

    Le système actuel encaisse tout, et son solde reste celui du COR. Un
    scénario notionnel se voit retirer, année par année, ce que la branche
    famille et l'assurance chômage versent pour des droits qu'il ne sert pas ;
    avant la bascule, où il sert encore les pensions du système actuel, son
    solde est donc celui du COR MOINS cette recette, et rien d'autre.
    """
    solde = cout.solde
    for annee in comptes.annees_transferts():
        ligne = solde.annee(annee)
        assert ligne.retrait == pytest.approx(comptes.transfert_supprime_part_pib(annee))
        assert ligne.ressources_de("actuel") == ligne.ressources
        assert ligne.solde("actuel") == pytest.approx(ligne.ressources - ligne.depenses)
        for scenario in ("notionnel_prospectif", "notionnel_prospectif_employeur"):
            assert ligne.rapports[scenario] == pytest.approx(1.0)
            assert ligne.solde(scenario) == pytest.approx(
                ligne.solde("actuel") - ligne.retrait)
            assert ligne.coefficient(scenario) < ligne.coefficient("actuel")
    # Un demi-point de PIB, toutes les années connues.
    for annee in comptes.annees_transferts():
        assert 0.004 < solde.annee(annee).retrait < 0.007, annee


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
        attendu = cotisees * rapport + (ligne.ressources - cotisees) - ligne.retrait
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
            assert ligne.ressources_de(scenario) == pytest.approx(
                ligne.ressources - ligne.retrait), (ligne.annee, scenario)


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
    reactif = cout.solde.solde_moyen("notionnel_liberal", bascule, fin)
    fige = sum(
        ligne.ressources - ligne.retrait - ligne.depense("notionnel_liberal")
        for ligne in cout.solde.annees if bascule <= ligne.annee <= fin
    ) / len([l for l in cout.solde.annees if bascule <= l.annee <= fin])
    # Trois points de PIB de moins, et un excédent moyen qui disparaît.
    assert fige - reactif > 0.03
    assert fige > 0.03
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
