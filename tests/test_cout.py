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
    Dette,
    calculer_dette,
)
from retraite_notionnelle.donnees.assiette import (
    POSTES_ASSIETTE,
    AssietteActivite,
)
from retraite_notionnelle.donnees.bilan import charger_bilan
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.donnees.distribution import DistributionPensions, part_femmes
from retraite_notionnelle.donnees.cotisants import (
    COTISANTS_ETAT_2024,
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
    ORGANISMES,
    POSTES,
    POSTES_TRANSFERTS,
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
    return calculer_cout(Simulateur(Parametres()), depenses, population, comptes,
                         convention_recette=CONVENTION_RAPPORT)


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
    assert population.effectif(49, 2024) == 0.0
    assert population.effectif(200, 2024) == 0.0


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
        par_annee = {l.annee: l.rapports[scenario] for l in lignes}
        for ligne in lignes:
            if ligne.annee < sommet.annee + PAS_GENERATIONS:
                continue
            assert ligne.rapports[scenario] <= (
                par_annee[ligne.annee - PAS_GENERATIONS] + 1e-12
            ), (scenario, ligne.annee)
        assert lignes[-1].rapports[scenario] < 0.85, scenario


def test_le_stock_sur_les_prix_efface_la_bosse_sans_toucher_l_horizon(
        avenir, depenses, population, comptes):
    """Réindexer le stock à la bascule creuse une bosse jusque vers 2040 et rien
    d'autre.

    Sous ``REINDEXE``, les pensions servies avant la bascule passent à la masse
    salariale le jour où la réforme s'applique, et le rapport des prospectifs
    au système actuel monte au-dessus de celui du défaut jusqu'à ce que ce
    stock s'éteigne. À l'horizon, les deux réglages se rejoignent au millième :
    tout ce qui reste vient des comptes, pas du stock. Avant la bascule, les
    prospectifs sont le système actuel dans les deux cas.
    """
    reindexe = calculer_cout(
        Simulateur(Parametres(revalorisation_stock=RevalorisationStock.REINDEXE)),
        depenses, population, comptes, convention_recette=CONVENTION_RAPPORT,
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
    # système actuel, quand la variante le lui faisait dépasser de 4,9 %.
    assert max(l.rapports["notionnel_prospectif"]
               for l in avenir.annees if l.annee >= bascule) < 1.0
    assert max(l.rapports["notionnel_prospectif"]
               for l in reindexe.annees if l.annee >= bascule) > 1.04


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
    # rapport des deux effectifs de 2024.
    attendu = (COTISANTS_ETAT_2024["fonction_publique_etat_militaire"]
               / COTISANTS_ETAT_2024["fonction_publique_etat_civile"])
    assert poids["militaire"] / poids["fonctionnaire_sedentaire"] == pytest.approx(attendu)
    assert (cotisants.effectif("fonction_publique_etat_civile", 2030)
            + cotisants.effectif("fonction_publique_etat_militaire", 2030)
            == pytest.approx(cotisants.effectif("fonction_publique_etat", 2030)))
    assert cotisants.fiabilite("fonction_publique_etat", 2030) == Fiabilite.HAUTE
    assert cotisants.fiabilite("fonction_publique_etat_civile", 2030) == Fiabilite.ESTIMEE


def test_la_recette_pese_les_cotisants_et_la_depense_les_retraites(
        cout: Cout, depenses, population, comptes):
    """Chaque côté du bilan a son poids, et le rapport de recettes s'en ressent.

    Peser la recette par les retraités surreprésentait les régimes qui
    s'éteignent, dont les taux sont les plus élevés, et poussait le rapport
    vers le bas — d'où un taux moyen implicite de 29,5 % là où le COR publie
    27,9 % pour un salarié du privé. Les cotisants le ramènent à 28 %.
    """
    assert sum(cout.poids_cotisants.values()) == pytest.approx(1.0)
    assert cout.poids_cotisants != cout.poids
    assert cout.poids_cotisants["agent_sncf_conduite"] < cout.poids["agent_sncf_conduite"]

    # L'ancienne convention, reproduite : les retraités des deux côtés.
    simulateur = Simulateur(Parametres())
    simulateur.__dict__["cotisants"] = simulateur.effectifs
    ancien = calculer_cout(simulateur, depenses, population, comptes,
                           convention_recette=CONVENTION_RAPPORT)
    assert ancien.poids_cotisants == ancien.poids
    for annee in (2030, 2050, 2070):
        nouveau = cout.avenir.annee(annee).rapports_recettes["notionnel_liberal"]
        vieux = ancien.avenir.annee(annee).rapports_recettes["notionnel_liberal"]
        assert nouveau > vieux
        assert 0.27 < 0.18 / nouveau < 0.29
    # Sous la convention `rapport`, le solde du scénario 6 en profite ; les
    # autres scénarios, dont le rapport vaut un, ne bougent pas.
    assert (cout.solde.solde_moyen("notionnel_liberal", 2026, 2070)
            > ancien.solde.solde_moyen("notionnel_liberal", 2026, 2070))
    assert (cout.solde.solde_moyen("actuel", 2026, 2070)
            == pytest.approx(ancien.solde.solde_moyen("actuel", 2026, 2070)))


def test_un_cote_de_ponderation_inconnu_est_refuse():
    with pytest.raises(ValueError, match="côté inconnu"):
        _ponderation(Simulateur(Parametres()), "effectifs", CAS_TYPES, "ni_l_un_ni_l_autre")


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
    assert egale.poids_cotisants == egale.poids
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
        caracteristiques.part_femmes, projetee.effectif,
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
    garantie décroît, en bénéficiaires comme en part du PIB, sans jamais
    s'annuler — une queue basse ne disparaît pas."""
    projetees = avenir.projetees()
    premiere, derniere = projetees[0], projetees[-1]
    assert derniere.garantie.facteur > premiere.garantie.facteur
    assert derniere.garantie.beneficiaires < premiere.garantie.beneficiaires
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
        # sous le plancher, et leur longévité allonge les avances.
        assert 0.55 < projetee.part_femmes < 0.8
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


def test_le_systeme_actuel_ne_s_equilibre_jamais_et_le_notionnel_si(solde):
    """Le résultat de fond de cette section, et il a changé de forme.

    Le système actuel reste déficitaire sur toute la fenêtre projetée du COR,
    et c'est le seul énoncé de ce test qui n'a jamais bougé. Les deux réformes
    prospectives s'équilibrent dès la bascule. Ce qui les sépare est ce
    qu'elles portent au compte : le 5 y ajoute la part patronale, donc des
    droits, donc une dépense, et sa moyenne reste négative là où celle du 3 est
    excédentaire.

    LE SCÉNARIO 5 EST PASSÉ SOUS LE SYSTÈME ACTUEL, puis repassé au-dessus, et
    les deux mouvements se nomment. Il est tombé dessous quand l'âge de
    référence a été fixé à 64 ans à partir de la bascule : converti à 64 ans et
    non à 67, un droit déjà acquis prend un diviseur plus élevé, donc un
    capital d'ouverture plus gros, et les deux réformes prospectives coûtent
    chacune un demi-point de PIB de plus. Il est remonté quand les scénarios
    notionnels ont cessé de servir la réversion — un avantage non contributif
    de plus, retiré comme les trente-huit autres —, ce qui lui rend 1,19 point
    de PIB, soit plus que ce que l'âge de référence lui avait coûté.

    Il s'équilibre donc dès la bascule, comme les trois autres réformes, et sa
    MOYENNE reste pourtant négative : l'équilibre des premières années ne tient
    pas la charge des années 2040 et 2050. C'est elle qui compte, et c'est ce
    qui le sépare encore des scénarios 2, 3 et 4.
    """
    debut, fin = solde.premiere_annee_projetee, solde.derniere_annee
    assert solde.premiere_annee_equilibree("actuel") is None
    assert solde.solde_moyen("actuel", debut, fin) < 0.0
    # Le 3 s'équilibre, reste excédentaire en moyenne, et reste au-dessus du
    # système actuel.
    annee = solde.premiere_annee_equilibree("notionnel_prospectif")
    assert annee is not None and annee >= debut
    assert solde.solde_moyen("notionnel_prospectif", debut, fin) > 0.0
    assert (solde.solde_moyen("notionnel_prospectif", debut, fin)
            > solde.solde_moyen("actuel", debut, fin))
    # Le 5 s'équilibre dès la bascule, reste déficitaire EN MOYENNE, et repasse
    # au-dessus du système actuel. Le dire vaut mieux que de l'arrondir dans un
    # sens ou dans l'autre : une réforme qui porte la part patronale au compte
    # porte des droits, et des droits se paient — mais elle ne sert plus la
    # réversion, et cela lui rend 1,19 point de PIB.
    annee_5 = solde.premiere_annee_equilibree("notionnel_prospectif_employeur")
    assert annee_5 is not None and annee_5 >= debut, annee_5
    assert solde.solde_moyen("actuel", debut, fin) < solde.solde_moyen(
        "notionnel_prospectif_employeur", debut, fin) < 0.0
    # Le scénario 5 porte plus de droits que le 3 : il coûte davantage.
    assert (solde.solde_moyen("notionnel_prospectif_employeur", debut, fin)
            < solde.solde_moyen("notionnel_prospectif", debut, fin))


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
    # Le fonds de solidarité vieillesse s'y est ajouté le 19 septembre 2026, et
    # il pèse plus que les deux autres réunis : le retrait total est passé d'un
    # demi-point de PIB à plus d'un point.
    assert 18_000 < comptes.transfert_organisme("solidarite", annee) < 25_000
    assert (comptes.transfert_organisme("solidarite", annee)
            > comptes.transfert_organisme("famille", annee)
            + comptes.transfert_organisme("chomage", annee))
    assert 0.010 < comptes.transfert_supprime_part_pib(annee) < 0.015
    # Les trois organismes ont un droit supprimé : la recette suit le droit.
    assert all(organisme.droit_supprime for organisme in ORGANISMES)


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
    # À la bascule, la recette leur est retirée comme aux autres.
    ligne = solde.annee(bascule)
    for scenario in ("notionnel_prospectif", "notionnel_prospectif_employeur"):
        rapport = ligne.rapports_recettes.get(scenario, 1.0)
        cotisees = ligne.ressources * ligne.part_contributive
        assert ligne.ressources_de(scenario) == pytest.approx(
            cotisees * rapport + ligne.ressources - cotisees - ligne.retrait)
    # Plus d'un point de PIB, toutes les années connues, depuis que le fonds
    # de solidarité vieillesse est entré dans le compte.
    for annee in comptes.annees_transferts():
        assert 0.009 < solde.annee(annee).retrait < 0.018, annee


@pytest.fixture(scope="module")
def assiette() -> AssietteActivite:
    return AssietteActivite(RACINE_DONNEES)


@pytest.fixture(scope="module")
def cout_assiette(depenses: DepensesRetraite, population: Population,
                  comptes: ComptesRetraite, assiette: AssietteActivite):
    """Le coût sous la convention du programme : le taux plein sur l'assiette."""
    return calculer_cout(Simulateur(Parametres()), depenses, population, comptes,
                         assiette=assiette,
                         convention_recette=CONVENTION_ASSIETTE)


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
        pleine = ligne.ressources * taux / ligne.taux_prelevement
        # Trois postes sortent, tous le 19 septembre 2026 : la contribution
        # d'équilibre (remplacée par les 18 % sur les traitements), les
        # subventions (la fusion des régimes en supprime l'objet), les impôts
        # affectés (aucun droit acquis). Le retrait, lui, rend la part qui
        # vient de sortir avec l'impôt, pour ne pas la retirer deux fois.
        autres = ligne.ressources * (1.0 - ligne.part_contributive
                                     - ligne.part_subventions
                                     - ligne.part_impots)
        assert ligne.ressources_de("notionnel_liberal") == pytest.approx(
            pleine + autres - (ligne.retrait - ligne.retrait_par_impot)), ligne.annee
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
            # Avant la bascule, les scénarios 3 et 5 sont le système actuel,
            # et n'ont rien à retirer : voir `test_la_recette_suit_le_droit`.
            avant = (scenario in CLES_PROSPECTIVES
                     and ligne.annee < ligne.annee_bascule)
            attendu = ligne.ressources if avant else ligne.ressources - ligne.retrait
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
    reactif = cout.solde.solde_moyen("notionnel_liberal", bascule, fin)
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
                   + point.ressources * (1.0 - point.part_contributive
                                         - point.part_subventions
                                         - point.part_impots)
                   - (point.retrait - point.retrait_par_impot))
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
        assert point.cout("actuel") == point.observee, point.annee


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
    multipliées par le rapport des deux taux ; ce que la branche famille et
    l'assurance chômage versent est retiré des transferts, et les autres
    produits sont reconduits tels quels. Avant la bascule, la proposition
    prélève les taux réels comme tout le monde, et sa réversion n'est jamais
    servie.
    """
    bascule = cout_assiette.solde.annees[0].annee_bascule
    for point in cout_assiette.solde.annees:
        postes = point.postes_ressources("notionnel_liberal")
        actuel = point.postes_ressources("actuel")
        assert postes["transferts_famille"] == 0.0
        assert postes["transferts_chomage"] == 0.0
        assert postes["transferts_autres"] == pytest.approx(actuel["transferts_autres"])
        assert postes["autres_produits"] == pytest.approx(actuel["autres_produits"])
        assert point.postes_depenses("notionnel_liberal")["droits_derives"] == 0.0
        if point.annee >= bascule:
            assert point.recette_par_assiette
            assert postes["contribution_equilibre_etat"] == 0.0
            assert postes["subventions_equilibre"] == 0.0
            assert postes["impots_et_taxes"] == 0.0
            assert postes["cotisations"] == pytest.approx(
                point.ressources * point.taux_liberal / point.taux_prelevement)
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
    assert postes["transferts_famille"] + postes["transferts_chomage"] + postes[
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


def test_les_deux_conventions_de_reversion_se_mesurent(
        depenses: DepensesRetraite, population: Population,
        comptes: ComptesRetraite, assiette: AssietteActivite):
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
        return calculer_cout(Simulateur(Parametres()), depenses, population,
                             comptes, assiette=assiette,
                             convention_recette=CONVENTION_ASSIETTE,
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
        # Elle est une part réelle du retrait, jamais sa totalité : la CNAF et
        # l'Unédic versent, eux, par un transfert, et leur recette est dans le
        # poste « transferts », qui reste.
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


def test_sans_solde_la_dette_est_vide(depenses, population):
    """Sans comptes, pas de solde ; sans solde, pas de stock — et rien ne plante."""
    sans = calculer_cout(Simulateur(Parametres()), depenses, population)
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
    bascule = Parametres().annee_debut_capitalisation
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


def test_la_proposition_ne_perd_plus_un_point_a_la_croissance(
        depenses, population, assiette):
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
    """
    soldes = {}
    for scenario in ("cor_productivite_basse", "cor_reference",
                     "cor_productivite_haute"):
        comptes = ComptesRetraite(
            RACINE_DONNEES,
            variante=variante_du_scenario(
                scenario, RACINE_DONNEES / "reference" / "macro"))
        cout = calculer_cout(
            Simulateur(Parametres().avec(scenario_projection=scenario)),
            depenses, population, comptes, assiette=assiette)
        ligne = cout.solde.annees[-1]
        soldes[scenario] = ligne.solde("notionnel_liberal")
    amplitude = soldes["cor_productivite_basse"] - soldes["cor_productivite_haute"]
    assert 0.0 < amplitude < 0.005, soldes


def test_la_carte_du_solde_garde_le_meme_axe_sous_tous_les_scenarios():
    """UN AXE QUI SUIT SES DONNÉES TROMPE L'ŒIL DÈS QU'ON COMPARE.

    La carte du solde est la seule du site qu'un réglage redessine ET qu'on
    lit en comparant deux réglages : l'écart entre les deux courbes EST son
    sujet. Le 21 septembre 2026, elle montait à 20 % du PIB sous le scénario
    de référence et à 15 % sous la variante haute de productivité. L'écart de
    2070 perdait alors 29 % de sa valeur entre les deux tracés — 2,39 point
    contre 1,69 — et 5 % seulement de sa hauteur à l'écran. Le chiffre disait
    le vrai, le dessin le contredisait.

    Le test lit les graduations rendues, et non le paramètre : ce qui doit
    tenir est ce que le lecteur voit.
    """
    import re

    from retraite_notionnelle.web.pages import Contexte, rendre

    contexte = Contexte(Parametres())
    axes = {}
    for scenario in ("cor_reference", "cor_productivite_haute",
                     "cor_productivite_basse"):
        _, corps = rendre(contexte, "/cout", {"projection": scenario})
        carte = next(
            m.group(0) for m in re.finditer(r"<svg\b.*?</svg>", corps, re.S)
            if "% du PIB" in m.group(0) and "projection" in m.group(0)
        )
        axes[scenario] = re.findall(
            r'<text class="graduation"[^>]*>([^<]*)</text>', carte)[:6]
    assert len(set(map(tuple, axes.values()))) == 1, axes


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
