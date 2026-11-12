"""L'indexation du programme pour le seul scénario 6 (action 186, chantier 5).

Le facteur démographique (décision 41), le plancher en euros avec rattrapage
(décision 44), payé par les retraités par une dette au taux de la masse
salariale (décision 46), rendue au plus vite (décision 49), et les trois voies
neuves pour le stock (note ``186/2026-11-07-indexation-scenario-6.md``). Les
valeurs attendues sont posées à la main : l'exemple du propriétaire, et la
série des cotisants par retraité que le COR publie.
"""

from __future__ import annotations

import math
from dataclasses import replace

import pytest

from retraite_notionnelle import indexation_programme as I


# -- le plancher, sur l'exemple du propriétaire ---------------------------------
#
# La règle fait −2 % une année, +5 % la suivante, puis +3 % ; la masse
# salariale −1 %, +6 %, puis +3,5 % (note de l'indexation, « L'assurance payée
# par les retraités »). Une quatrième année, +3 % et +3,5 %, montre le retour à
# la règle.
REGLE = (-0.02, 0.05, 0.03, 0.03)
MASSE = (-0.01, 0.06, 0.035, 0.035)


def test_la_dette_reprise_sur_la_moitie_de_la_hausse_refait_le_tableau_du_proprietaire():
    chemin = I.suivre(REGLE, MASSE, "dette", reprise=0.5)
    # La règle : 0,98, puis 0,98 × 1,05 = 1,029, puis × 1,03 = 1,05987.
    assert chemin.regle[:3] == pytest.approx((0.98, 1.029, 1.05987))
    # Gelée, puis la moitié de la hausse (2,9 % → 1,45 %), puis le reste de la
    # dette : 1,05987 − 0,0067 × 1,035 = 1,0529355.
    assert chemin.servi == pytest.approx((1.0, 1.0145, 1.0529355, 1.05987 * 1.03))
    # 2 % d'une année de pension ; 2 % × 1,06 − 1,45 % = 0,67 % ; rendue.
    assert chemin.dette == pytest.approx((0.02, 0.0067, 0.0, 0.0), abs=1e-12)


def test_la_dette_reprise_sur_toute_la_hausse_sert_1_0078_la_deuxieme_annee():
    """Décision 49 : la dette se rend le plus vite possible."""
    chemin = I.suivre(REGLE, MASSE, "dette", reprise=1.0)
    # 1,029 − 0,02 × 1,06 = 1,0078 ; la troisième année revient à la règle.
    assert chemin.servi == pytest.approx((1.0, 1.0078, 1.05987, 1.05987 * 1.03))
    assert chemin.dette == pytest.approx((0.02, 0.0, 0.0, 0.0), abs=1e-12)


def test_sans_rattrapage_le_plancher_donne_pour_toujours_ce_qu_il_evite():
    """L. 161-25 : « Si ce coefficient est inférieur à un, il est porté à
    cette valeur. » Ce que le gel évite n'est jamais repris."""
    chemin = I.suivre(REGLE, MASSE, "sans_rattrapage")
    assert chemin.servi == pytest.approx((1.0, 1.05, 1.0815, 1.0815 * 1.03))
    assert chemin.dette == (0.0, 0.0, 0.0, 0.0)


def test_la_reserve_paie_le_plancher_et_la_pension_rejoint_la_regle_des_qu_elle_la_depasse():
    """Voie 1 : ce que le plancher sert au-dessus de la règle, une réserve le
    paie ; la pension retrouve la règle dès que la règle repasse au-dessus."""
    chemin = I.suivre(REGLE, MASSE, "reserve")
    assert chemin.servi == pytest.approx((1.0, 1.029, 1.05987, 1.05987 * 1.03))
    assert chemin.dette == (0.0, 0.0, 0.0, 0.0)
    assert chemin.au_dessus == pytest.approx((0.02, 0.0, 0.0, 0.0), abs=1e-12)


def test_sans_plancher_la_pension_suit_la_regle():
    chemin = I.suivre(REGLE, MASSE, "aucun")
    assert chemin.servi == pytest.approx(chemin.regle)


@pytest.mark.parametrize("plancher", ["sans_rattrapage", "dette", "reserve"])
@pytest.mark.parametrize("reprise", [0.5, 1.0])
def test_une_pension_ne_baisse_jamais_en_euros(plancher, reprise):
    regle = (-0.02, -0.01, 0.004, -0.003, 0.02, -0.015, 0.01, 0.03, 0.0, -0.001)
    masse = (-0.01, 0.0, 0.01, 0.005, 0.03, -0.02, 0.02, 0.035, 0.01, 0.002)
    chemin = I.suivre(regle, masse, plancher, reprise=reprise)
    precedent = 1.0
    for servi in chemin.servi:
        assert servi >= precedent - 1e-15
        precedent = servi


def test_la_dette_porte_interet_au_taux_de_la_masse_salariale():
    """Décision 46 : la dette suit la masse salariale, celle du compte."""
    chemin = I.suivre((-0.02, -0.01), (0.03, 0.04), "dette")
    # 0,02, puis 0,02 × 1,04 + (1 − 0,98 × 0,99).
    assert chemin.dette == pytest.approx((0.02, 0.02 * 1.04 + 1.0 - 0.98 * 0.99))


# -- les calibrages : la baisse d'avance (voie 2), la prime (voie 1) ------------


def test_la_baisse_d_avance_egale_ce_que_la_regle_retire_au_stock_sur_sa_vie():
    """Deux années de stock, de masses 1 et 1, la masse salariale à +2 % ;
    la règle garde 1 puis 0,9. Actualisé à la masse salariale, le stock perd
    0,1 / 1,02 sur 1 + 1 / 1,02."""
    baisse = I.baisse_d_effort({2026: 1.0, 2027: 1.0}, {2026: 1.0, 2027: 0.9},
                               {2027: 1.02})
    assert baisse == pytest.approx((0.1 / 1.02) / (1.0 + 1.0 / 1.02))


def test_la_prime_d_equilibre_paie_exactement_ce_que_le_plancher_sert_au_dessus_de_la_regle():
    """La règle sert 1 puis 1, le plancher 1 puis 1,1 : la réserve reçoit la
    règle et paie la pension diminuée de la prime ; elle finit à zéro quand la
    prime vaut 1 − 2 / 2,1, sans actualisation."""
    prime = I.prime_d_equilibre({2026: 1.0, 2027: 1.0}, {2026: 1.0, 2027: 1.1},
                                {2027: 1.0})
    assert prime == pytest.approx(1.0 - 2.0 / 2.1)


# -- la voie 1 décidée : la prime rendue en route, la réserve qui manque ---------
#
# Décision 75 : « la prime baisse dès que la réserve dépasse ce que le plancher
# peut encore coûter » ; décision 76 : « si la réserve manque, le stock la rend
# par une dette », reprise sur ses hausses comme sous la décision 46. Ce que le
# plancher peut encore coûter, et l'assiette de la prime qui reste à venir, sont
# posés à la main, rang par rang : le modèle les mesure sous la crise assurée.


def _besoin(valeurs):
    return lambda rang, plancher, regle, prix: [valeurs[rang]]


def test_la_prime_baisse_des_que_la_reserve_et_les_primes_a_venir_suffisent():
    """Une prime de 10 %, sans mort, sans intérêt, sans inflation ; la règle
    ne baisse pas. À la bascule, la réserve reçoit 0,1 ; il reste 0,15 à
    couvrir sur une assiette de 2 : la prime tombe à (0,15 − 0,1) / 2 = 2,5 %.
    L'année suivante, la réserve vaut 0,125 et le plancher ne peut plus rien
    coûter : la prime devient −12,5 %, un supplément qui rend la réserve."""
    assurance = I.assurer((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (1.0, 1.0, 1.0), 0.10,
                          _besoin({0: (0.15, 2.0), 1: (0.0, 1.0), 2: (0.0, 0.0)}))
    assert assurance.prime == pytest.approx((0.10, 0.025, -0.125))
    assert assurance.reserve == pytest.approx((0.10, 0.125, 0.0), abs=1e-15)
    assert assurance.servi == pytest.approx((0.90, 0.975, 1.125))
    assert assurance.dette == (0.0, 0.0, 0.0)


def test_au_seuil_la_prime_ne_baisse_que_quand_la_reserve_seule_suffit():
    """La lecture à la lettre : la prime reste entière tant que la réserve ne
    dépasse pas ce que le plancher peut encore coûter, puis rend l'excédent."""
    assurance = I.assurer((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (1.0, 1.0, 1.0), 0.10,
                          _besoin({0: (0.15, 2.0), 1: (0.0, 1.0), 2: (0.0, 0.0)}),
                          retour="au_seuil")
    assert assurance.prime == pytest.approx((0.10, 0.10, -0.20))
    assert assurance.reserve == pytest.approx((0.10, 0.20, 0.0), abs=1e-15)
    assert assurance.servi == pytest.approx((0.90, 0.90, 1.20))


def test_sous_deux_risques_la_prime_couvre_le_plus_exigeant():
    """La réserve vaut 0,1 à la bascule. Le premier risque laisse 0,05 à
    couvrir sur une assiette de 2 (2,5 %), le second 0,2 sur 4 (5 %) : la
    prime tombe à 5 %, et ce que le plancher peut encore coûter est 0,3."""
    assurance = I.assurer((0.0,), (0.0,), (0.0,), (1.0, 1.0), 0.10,
                          lambda rang, *_: [(0.15, 2.0), (0.3, 4.0)] if rang == 0 else [])
    assert assurance.prime == pytest.approx((0.10, 0.05))
    assert assurance.cout_restant[0] == pytest.approx(0.3)


def test_la_reserve_qui_manque_devient_une_dette_du_stock_reprise_sur_ses_hausses():
    """Une prime de 2 % qui ne baisse pas (le plancher peut encore coûter 1).
    La règle perd 5 %, ne bouge pas, puis gagne 10 %. La première année, la
    réserve, 0,02 + 0,02, paie 0,04 des 0,05 que le plancher sert au-dessus de
    la règle : 0,01 devient la dette de chaque euro. La deuxième, 0,03 de plus.
    La troisième, la règle, 1,045, repasse au-dessus du plancher : la hausse
    rend les 0,04, la pension avant prime passe à 1,005, et la prime refait la
    réserve."""
    assurance = I.assurer((-0.05, 0.0, 0.10), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
                          (1.0, 1.0, 1.0, 1.0), 0.02,
                          _besoin({rang: (1.0, 1.0) for rang in range(4)}))
    assert assurance.prime == pytest.approx((0.02,) * 4)
    assert assurance.dette == pytest.approx((0.0, 0.01, 0.04, 0.0), abs=1e-15)
    assert assurance.reserve == pytest.approx((0.02, 0.0, 0.0, 0.0201), abs=1e-15)
    assert assurance.plancher == pytest.approx((1.0, 1.0, 1.0, 1.005))
    assert assurance.servi == pytest.approx((0.98, 0.98, 0.98, 0.98 * 1.005))


def test_la_dette_de_la_reserve_porte_interet_au_taux_de_la_masse_salariale():
    """Le manque se répartit sur les euros qui vivent encore : la moitié du
    stock morte, 0,01 de manque fait 0,02 de dette par euro, en euros courants
    (2 % d'inflation), puis porte intérêt à la masse salariale (+3 %)."""
    assurance = I.assurer((-0.05, -0.0), (0.03, 0.03), (0.02, 0.02),
                          (1.0, 0.5, 0.5), 0.0,
                          _besoin({rang: (1.0, 1.0) for rang in range(3)}))
    # Rang 1 : le plancher sert 0,05 au-dessus de la règle à la moitié
    # vivante, 0,025 en euros courants, que rien ne paie.
    assert assurance.dette[1] == pytest.approx(0.05)
    assert assurance.dette[2] == pytest.approx(0.05 * 1.03 + 0.05)


def test_une_reserve_a_soi_ne_recoit_rien_des_morts():
    """Une prime de 10 %, la moitié du stock morte la première année, sans
    plancher qui joue. En commun, la réserve du groupe vaut 0,1 + 0,5 × 0,1 =
    0,15 de la masse de départ, soit 0,3 par euro vivant : les survivants
    héritent des primes des morts. À soi, chaque euro vivant a payé 0,1 deux
    fois, et garde 0,2 ; la réserve des morts sort du stock."""
    besoin = _besoin({0: (1.0, 1.0), 1: (1.0, 1.0)})
    commun = I.assurer((0.0,), (0.0,), (0.0,), (1.0, 0.5), 0.10, besoin)
    a_soi = I.assurer((0.0,), (0.0,), (0.0,), (1.0, 0.5), 0.10, besoin, en_commun=False)
    assert commun.reserve == pytest.approx((0.10, 0.15))
    assert a_soi.reserve == pytest.approx((0.10, 0.20))


def test_a_soi_le_besoin_se_mesure_pour_un_survivant():
    """Ce que le plancher peut encore coûter, mesuré sur le groupe, se divise
    par ce qui en vit : 0,05 sur une assiette de 0,5, pour une moitié vivante,
    font 0,1 sur 1 par survivant. Sa réserve de 0,2 dépasse : la prime devient
    (0,1 − 0,2) / 1 = −10 %, un supplément."""
    besoin = _besoin({0: (1.0, 1.0), 1: (0.05, 0.5), 2: (0.0, 0.0)})
    a_soi = I.assurer((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (1.0, 0.5, 0.5), 0.10, besoin,
                      en_commun=False)
    assert a_soi.prime == pytest.approx((0.10, 0.10, -0.10))


def test_a_soi_le_manque_est_la_dette_du_seul_retraite():
    """La moitié du stock morte, la règle −5 % : le plancher sert 0,05 à
    chaque euro vivant, que sa réserve de 0,02 + 0,02 ne couvre qu'en partie."""
    a_soi = I.assurer((-0.05,), (0.0,), (0.0,), (1.0, 0.5), 0.02,
                      _besoin({0: (1.0, 1.0), 1: (1.0, 1.0)}), en_commun=False)
    assert a_soi.dette == pytest.approx((0.0, 0.01))
    assert a_soi.reserve == pytest.approx((0.02, 0.0))


def test_sans_dette_la_reserve_qui_manque_reste_aux_cotisants():
    """La convention de l'étude, avant la décision 76 : la pension suit le
    plancher, et la réserve, négative, dit ce que les cotisants avancent."""
    assurance = I.assurer((-0.05, 0.0, 0.10), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
                          (1.0, 1.0, 1.0, 1.0), 0.02,
                          _besoin({rang: (1.0, 1.0) for rang in range(4)}),
                          manque="cotisants")
    assert assurance.dette == (0.0, 0.0, 0.0, 0.0)
    assert assurance.reserve == pytest.approx((0.02, -0.01, -0.04, -0.04 + 0.02 * 1.045))
    assert assurance.servi == pytest.approx((0.98, 0.98, 0.98, 0.98 * 1.045))


@pytest.mark.parametrize("retour", ["progressif", "au_seuil"])
def test_une_pension_assuree_ne_baisse_jamais_en_euros_apres_la_bascule(retour):
    regle = (-0.02, -0.01, 0.004, -0.003, 0.02, -0.015, 0.01, 0.03, 0.0, -0.001)
    masse = (-0.01, 0.0, 0.01, 0.005, 0.03, -0.02, 0.02, 0.035, 0.01, 0.002)
    survie = tuple(0.9 ** rang for rang in range(11))
    # Ce que le plancher peut encore coûter fond avec le stock ; la prime
    # baisse, devient un supplément, et la réserve finit par manquer.
    besoin = lambda rang, plancher, regle, prix: [(0.05 * survie[rang], 2.0 * survie[rang])]
    assurance = I.assurer(regle, masse, (0.01,) * 10, survie, 0.03, besoin, retour=retour)
    for avant, apres in zip(assurance.servi, assurance.servi[1:]):
        assert apres >= avant - 1e-15
    for avant, apres in zip(assurance.prime, assurance.prime[1:]):
        assert apres <= avant


# -- les voies et les trajectoires, lues dans les données ------------------------


def test_les_voies_et_les_trajectoires_sont_celles_de_la_note():
    voies, trajectoires = I.charger()
    assert list(voies) == ["avant", "regle", "decidee", "voie_1", "voie_2", "voie_3",
                           "voie_1_crise_a_ses_dates", "voie_1_crise_recommencee"]
    avant, regle, decidee = voies["avant"], voies["regle"], voies["decidee"]
    # La règle d'avant : la masse salariale pour les nouvelles (décision 10),
    # les prix pour le stock (action 48), sans facteur.
    assert (avant.nouvelles.base, avant.stock.base,
            avant.stock.facteur_demographique) == ("masse_salariale", "prix", 0.0)
    # α = 1 : la masse salariale par retraité, les prix moins la hausse du
    # rapport retraités/cotisants (décision 41).
    assert (regle.nouvelles.base, regle.stock.base,
            regle.stock.facteur_demographique) == (
        "masse_salariale_par_retraite", "prix", 1.0)
    assert (regle.nouvelles.plancher, regle.stock.plancher) == ("aucun", "aucun")
    # Décisions 44, 46 et 49 : le plancher et sa dette, rendue sur toute la hausse.
    assert (decidee.stock.plancher, decidee.stock.reprise) == ("dette", 1.0)
    assert voies["voie_1"].stock.prime == "calibree"
    assert voies["voie_1"].stock.plancher == "reserve"
    assert voies["voie_2"].stock.baisse_transition == "effort_demographique"
    assert (voies["voie_2"].stock.base, voies["voie_2"].stock.facteur_demographique) == (
        "prix", 0.0)
    assert voies["voie_3"].stock.base == "masse_salariale_par_retraite"
    # La voie 1 décidée (décisions 73 à 77) : la règle de la décision 41, une
    # prime de 2,15 % qui couvre la crise de l'emploi, rendue en route, et la
    # dette du stock quand la réserve manque. Ses deux lectures ne diffèrent
    # que par ce que mesure « ce que le plancher peut encore coûter ».
    for nom, mesure in (("voie_1_crise_a_ses_dates", "crise_a_ses_dates"),
                        ("voie_1_crise_recommencee", "crise_recommencee")):
        stock = voies[nom].stock
        assert (stock.base, stock.facteur_demographique, stock.plancher) == (
            "prix", 1.0, "reserve")
        assert (stock.prime, stock.crise_assuree, stock.reserve_rendue,
                stock.reserve_manquante) == (0.0215, ("emploi_ia",), mesure, "dette")
    assert voies["voie_1"].stock.reserve_rendue == "jamais"
    assert voies["voie_1"].stock.reserve_manquante == "cotisants"
    # Les pensions nouvelles suivent la même règle sous toutes les voies.
    for nom in ("voie_1", "voie_2", "voie_3", "voie_1_crise_a_ses_dates",
                "voie_1_crise_recommencee"):
        assert voies[nom].nouvelles == decidee.nouvelles
    assert list(trajectoires) == ["cor", "inflation_basse", "emploi_ia"]
    assert trajectoires["inflation_basse"].inflation == 0.005
    assert (trajectoires["emploi_ia"].inflation, trajectoires["emploi_ia"].emploi) == (
        0.01, (2030, 2039, -0.01))


def test_le_choc_de_l_emploi_retire_un_pour_cent_par_an_de_2030_a_2039():
    _, trajectoires = I.charger()
    ia = trajectoires["emploi_ia"]
    assert ia.facteur_emploi(2029) == 1.0
    assert ia.facteur_emploi(2030) == pytest.approx(0.99)
    assert ia.facteur_emploi(2039) == pytest.approx(0.99 ** 10)
    assert ia.facteur_emploi(2070) == pytest.approx(0.99 ** 10)
    assert trajectoires["cor"].facteur_emploi(2050) == 1.0


def test_une_voie_a_calibrer_ne_se_calcule_pas():
    voies, trajectoires = I.charger()
    with pytest.raises(ValueError, match="calibr"):
        I.IndexationLiberale(voies["voie_2"], trajectoires["cor"])
    calibree = voies["voie_2"].calibree(baisse=0.07)
    assert calibree.stock.baisse_transition == 0.07
    I.IndexationLiberale(calibree, trajectoires["cor"])


# -- sur le modèle : le stock et les nouvelles sous α = 1 ------------------------


@pytest.fixture(scope="module")
def projection():
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.revalorisation_servie import RevalorisationServie
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres()).pour_la_projection()
    return simulateur, RevalorisationServie(simulateur, 1990, 2070)


def _servies(voie: str, trajectoire: str, projection):
    simulateur, revalorisation = projection
    voies, trajectoires = I.charger()
    indexation = I.IndexationLiberale(voies[voie], trajectoires[trajectoire])
    return indexation.appliquer(revalorisation, simulateur).proposition


def test_la_regle_d_avant_redonne_les_coefficients_du_modele(projection):
    """Sans plancher qui joue, la règle d'avant est celle que le modèle sert :
    le stock gelé aux prix à la bascule, les nouvelles sur la masse salariale."""
    _, revalorisation = projection
    servies = _servies("avant", "cor", projection)
    for liquidation, annee in ((2000, 2020), (2010, 2026), (2010, 2040), (2025, 2070),
                               (2026, 2026), (2026, 2050), (2040, 2070)):
        assert servies.coefficient_stock(liquidation, annee, prospectif=False) == (
            pytest.approx(revalorisation.coefficient_stock(liquidation, annee,
                                                           prospectif=False), rel=1e-12))


def test_sous_alpha_un_le_stock_perd_la_hausse_des_retraites_par_cotisant(projection):
    """Le stock suit les prix moins la hausse du nombre de retraités par
    cotisant : de 2026 à 2027, le COR passe de 1,7591831 à 1,7515306 cotisant
    par retraité (``decomposition_depense_retraite.csv``), et la pension du
    stock perd ce rapport en euros constants ; sous une inflation de 1,75 %,
    le plancher ne joue pas."""
    _, revalorisation = projection
    servies = _servies("regle", "cor", projection)
    gele = revalorisation.coefficient_stock(2010, 2026, prospectif=False)
    assert servies.coefficient_stock(2010, 2026, prospectif=False) == pytest.approx(gele)
    assert servies.coefficient_stock(2010, 2027, prospectif=False) == pytest.approx(
        gele * 1.7515306 / 1.7591831, rel=1e-9)
    assert servies.coefficient_stock(2010, 2070, prospectif=False) == pytest.approx(
        gele * 1.3045490 / 1.7591831, rel=1e-9)


def test_sous_alpha_un_la_pension_nouvelle_suit_la_masse_salariale_par_retraite(projection):
    """La masse salariale par retraité : le salaire moyen du COR, 2,45 % en
    euros courants sous 1,75 % d'inflation, divisé par la hausse du nombre de
    retraités par cotisant."""
    servies = _servies("regle", "cor", projection)
    salaire = 1.0245 / 1.0175
    attendu = salaire * 1.7515306 / 1.7591831
    assert servies.coefficient_stock(2026, 2027, prospectif=False) == pytest.approx(
        attendu, rel=1e-9)
    assert servies.coefficient_stock(2030, 2030, prospectif=False) == 1.0


def test_sous_une_inflation_de_0_5_pour_cent_le_plancher_retient_le_stock(projection):
    """De 2027 à 2032, la règle du stock monte encore en euros courants, le
    nombre de retraités par cotisant croissant moins vite que 0,5 %. En 2033,
    il croît de 0,81 % (le COR passe de 1,7365638 à 1,7225890 cotisant par
    retraité) : la règle baisse de 0,31 % en euros courants, le plancher la
    gèle, et ce qu'il sert au-dessus d'elle entre dans la dette."""
    _, revalorisation = projection
    servies = _servies("decidee", "inflation_basse", projection)
    gele = revalorisation.coefficient_stock(2010, 2026, prospectif=False)
    niveau_2032 = 1.005 ** 6 * 1.7365638 / 1.7591831
    assert servies.coefficient_stock(2010, 2032, prospectif=False) == pytest.approx(
        gele * 1.7365638 / 1.7591831, rel=1e-9)
    # Gelée en euros courants : en euros constants, les prix seuls l'érodent.
    assert servies.coefficient_stock(2010, 2033, prospectif=False) == pytest.approx(
        gele * 1.7365638 / 1.7591831 / 1.005, rel=1e-9)
    detail = servies.detail_stock()
    assert detail.dette[2032] == 0.0
    assert detail.dette[2033] == pytest.approx(
        niveau_2032 * (1.0 - 1.005 * 1.7225890 / 1.7365638), rel=1e-9)


def test_une_seule_part_se_mesure(projection):
    """Pour dire la masse du stock et celle des nouvelles, la part qu'on ne
    mesure pas ne sert rien."""
    simulateur, revalorisation = projection
    voies, trajectoires = I.charger()
    stock = I.IndexationLiberale(voies["regle"], trajectoires["cor"], seulement="stock")
    servies = stock.appliquer(revalorisation, simulateur).proposition
    assert servies.coefficient_stock(2030, 2040, prospectif=False) == 0.0
    assert servies.coefficient_stock(2010, 2040, prospectif=False) > 0.0
    nouvelles = I.IndexationLiberale(voies["regle"], trajectoires["cor"],
                                     seulement="nouvelles")
    servies = nouvelles.appliquer(revalorisation, simulateur).proposition
    assert servies.coefficient_stock(2010, 2040, prospectif=False) == 0.0
    assert math.isclose(servies.coefficient_stock(2030, 2030, prospectif=False), 1.0)


# -- sur le modèle : la voie 1 décidée -------------------------------------------
#
# Un stock qui fond de 7 % par an : les propriétés qui suivent tiennent pour
# toute survie, le coût donnant la sienne (``scripts/indexation_scenario_6.py``).
SURVIE = tuple((annee, 0.93 ** (annee - 2026)) for annee in range(2026, 2071))


def _assuree(nom: str, trajectoire: str, projection, prime: float | None = None,
             **regle):
    simulateur, revalorisation = projection
    voies, trajectoires = I.charger()
    voie = voies[nom] if prime is None else voies[nom].calibree(prime=prime)
    if regle:
        voie = replace(voie, stock=replace(voie.stock, **regle))
    choc = trajectoires[trajectoire]
    if choc.emploi is not None:
        revalorisation = revalorisation.pour_la_proposition(choc.facteur_emploi)
    indexation = I.IndexationLiberale(voie, choc, masses_stock=SURVIE)
    return indexation.appliquer(revalorisation, simulateur).proposition


def _prime_sous_la_crise(projection) -> float:
    """La prime qui finance exactement le plancher de ce stock sous la crise
    de l'emploi : le calibrage de la décision 74, sur cette survie."""
    survie = dict(SURVIE)
    etalon = _assuree("regle", "emploi_ia", projection)
    sans_prime = _assuree("voie_1", "emploi_ia", projection, prime=0.0)
    return I.prime_d_equilibre(
        {a: m * etalon.detail_stock().servi[a] for a, m in survie.items()},
        {a: m * sans_prime.detail_stock().servi[a] for a, m in survie.items()},
        {a: etalon.masse(a) for a in range(2027, 2071)})


def test_la_voie_1_decidee_demande_la_masse_du_stock():
    voies, trajectoires = I.charger()
    with pytest.raises(ValueError, match="masse"):
        I.IndexationLiberale(voies["voie_1_crise_a_ses_dates"], trajectoires["cor"])


def test_sous_la_crise_assuree_a_ses_dates_la_prime_ne_baisse_pas_et_la_reserve_finit_vide(
        projection):
    """Quand la crise assurée arrive à ses dates, la réserve suit ce que le
    calibrage prévoyait : la prime ne baisse jamais, et la réserve finit vide.
    Le calibrage équilibre la réserve sur l'horizon, non à chaque date : elle
    passe un temps sous zéro, que les cotisants avancent sans la décision 76."""
    prime = _prime_sous_la_crise(projection)
    assert 0.0 < prime < 0.05
    detail = _assuree("voie_1_crise_a_ses_dates", "emploi_ia", projection, prime=prime,
                      reserve_manquante="cotisants").detail_stock()
    for annee in range(2026, 2071):
        assert detail.prime[annee] == pytest.approx(prime, abs=1e-12), annee
        assert detail.dette[annee] == 0.0, annee
    assert max(detail.reserve.values()) > 0.05
    assert min(detail.reserve.values()) < 0.0
    assert detail.reserve[2070] == pytest.approx(0.0, abs=1e-12)


def test_sous_la_decision_76_le_creux_de_la_reserve_devient_une_dette_du_stock(projection):
    """La même crise, le manque payé par le stock : quand la réserve touche
    zéro, ce que le plancher sert au-dessus de la règle devient sa dette ; la
    hausse de la règle la reprend, et ce que les primes ont mis de trop en
    réserve revient au stock, la prime baissant."""
    prime = _prime_sous_la_crise(projection)
    detail = _assuree("voie_1_crise_a_ses_dates", "emploi_ia", projection,
                      prime=prime).detail_stock()
    assert min(detail.reserve.values()) == 0.0
    assert max(detail.dette.values()) > 0.0
    assert detail.dette[2070] == pytest.approx(0.0, abs=1e-12)
    assert detail.prime[2070] < prime


def test_les_deux_lectures_partent_de_la_meme_mesure_puis_divergent(projection):
    """À la bascule, la crise recommencée est la crise à ses dates : ce que le
    plancher peut encore coûter, et la prime de l'année suivante, sont les
    mêmes. Sous le COR, la crise à ses dates passe sans venir, et sa prime
    baisse plus vite que celle d'une crise qui recommence toujours."""
    a_ses_dates = _assuree("voie_1_crise_a_ses_dates", "cor", projection).detail_stock()
    recommencee = _assuree("voie_1_crise_recommencee", "cor", projection).detail_stock()
    assert a_ses_dates.prime[2026] == recommencee.prime[2026] == 0.0215
    assert a_ses_dates.cout_restant[2026] == pytest.approx(recommencee.cout_restant[2026],
                                                           rel=1e-12)
    assert a_ses_dates.prime[2027] == pytest.approx(recommencee.prime[2027], rel=1e-12)
    assert a_ses_dates.prime[2035] < recommencee.prime[2035] < 0.0215


def test_sous_le_cor_la_reserve_est_rendue_au_stock(projection):
    """Sous le COR, le plancher ne joue jamais. Une fois la crise assurée
    passée, à ses dates, il ne peut presque plus rien coûter : la prime devient
    un supplément, la réserve se rend au stock, et ne garde à la fin que ce
    que le plancher pouvait encore coûter la dernière année, sous la crise."""
    detail = _assuree("voie_1_crise_a_ses_dates", "cor", projection).detail_stock()
    regle = _servies("regle", "cor", projection).detail_stock()
    for annee in range(2040, 2071):
        assert detail.prime[annee] < 0.0, annee
        assert detail.servi[annee] > regle.servi[annee], annee
    assert 0.0 < detail.reserve[2070] < 1e-3 * max(detail.reserve.values())
    assert all(dette == 0.0 for dette in detail.dette.values())


@pytest.mark.parametrize("nom", ["voie_1_crise_a_ses_dates", "voie_1_crise_recommencee"])
@pytest.mark.parametrize("retour", ["progressif", "au_seuil"])
def test_la_pension_du_stock_assuree_ne_baisse_jamais_en_euros(nom, retour, projection):
    """Promesse 4 (décision 45), sous une inflation durable de 0,5 % : de la
    bascule à l'horizon, la pension du stock ne baisse pas en euros courants,
    et la prime ne remonte jamais."""
    detail = _assuree(nom, "inflation_basse", projection, retour=retour).detail_stock()
    precedente = detail.servi[2026]
    for annee in range(2027, 2071):
        courante = detail.servi[annee] * 1.005 ** (annee - 2026)
        assert courante >= precedente * (1 - 1e-12), annee
        assert detail.prime[annee] <= detail.prime[annee - 1], annee
        precedente = courante


def test_une_contribution_permanente_ne_baisse_jamais_et_la_reserve_garde_tout(projection):
    """« Contribution de 1 % tout le temps » : rien ne se mesure, la prime
    reste ; sous le COR, le plancher ne joue pas et la réserve grossit."""
    detail = _assuree("voie_1_crise_a_ses_dates", "cor", projection, prime=0.01,
                      reserve_rendue="jamais", crise_assuree=()).detail_stock()
    assert set(detail.prime.values()) == {0.01}
    assert all(dette == 0.0 for dette in detail.dette.values())
    reserves = [detail.reserve[a] for a in range(2026, 2071)]
    assert reserves == sorted(reserves)


def test_une_reserve_personnelle_est_celle_d_un_seul_retraite(projection):
    """Une réserve à soi : la survie vaut un, rien ne passe des morts aux
    vivants. Sous le COR, sans plancher qui joue, elle est la somme des primes
    d'un euro de pension, placées au taux de la masse salariale."""
    simulateur, revalorisation = projection
    voies, trajectoires = I.charger()
    voie = voies["voie_1_crise_a_ses_dates"].calibree(prime=0.01)
    voie = replace(voie, stock=replace(voie.stock, reserve_rendue="jamais", crise_assuree=()))
    une = tuple((annee, 1.0) for annee in range(2026, 2071))
    pensions = I.IndexationLiberale(voie, trajectoires["cor"], masses_stock=une).appliquer(
        revalorisation, simulateur).proposition
    detail = pensions.detail_stock()
    attendue = 0.0
    for annee in range(2026, 2041):
        if annee > 2026:
            attendue *= pensions.masse(annee)
        attendue += 0.01 * detail.servi[annee] / 0.99
    assert detail.reserve[2040] == pytest.approx(attendue, rel=1e-12)
