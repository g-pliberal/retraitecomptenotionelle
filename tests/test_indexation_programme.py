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


# -- les voies et les trajectoires, lues dans les données ------------------------


def test_les_voies_et_les_trajectoires_sont_celles_de_la_note():
    voies, trajectoires = I.charger()
    assert list(voies) == ["avant", "regle", "decidee", "voie_1", "voie_2", "voie_3"]
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
    # Les pensions nouvelles suivent la même règle sous les trois voies.
    for nom in ("voie_1", "voie_2", "voie_3"):
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
    from retraite_notionnelle.revalorisation import RevalorisationServie
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
