"""Les indicateurs de cycle de vie : leurs définitions, sur des flux faits à la main.

``retraite_notionnelle.cycle_de_vie`` voit une carrière, sous chacun des six
systèmes, comme deux chroniques — ce qu'elle verse, ce qu'elle reçoit — et en
tire la durée de retraite, le taux de récupération, le rendement interne et le
patrimoine retraite (action 138, étape 9). Ce module tient les définitions :
un rendement qu'on connaît d'avance se retrouve, une durée de retraite est
celle que la convention dit, un taux de récupération est le rapport de deux
sommes, et chaque système reçoit et verse ce que le modèle lui prête ; à
chaque âge de départ, de l'âge d'ouverture à l'annulation de la décote, en
net, sous les trois productivités du COR ; l'âge d'équilibre, où une
génération retrouve le diviseur ou la part de vie de la référence du compte.
La confrontation aux chiffres publiés par le COR, TRAJECTOiRE, l'OCDE, l'ETK
et le simulateur du COR est dans ``tests/test_cycle_de_vie_references.py``.
"""

from __future__ import annotations

import math

import pytest

from retraite_notionnelle import cycle_de_vie
from retraite_notionnelle.castypes import CAS_TYPES
from retraite_notionnelle.config import RACINE_DONNEES, Parametres
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.remuneration import fiche_depuis_brut
from retraite_notionnelle.revalorisation import faire_vivre
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _comparaison(simulateur, generation: int, age_liquidation: float = 64,
                 affiliation: str = "salarie_prive_non_cadre", sexe: str = "H"):
    return simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=generation, sexe=sexe, affiliation=affiliation,
        age_debut=21, age_liquidation=age_liquidation, niveau_salaire=1.0))


@pytest.fixture(scope="module")
def parti_en_2014(simulateur):
    """Un salarié né en 1950, parti en 2014 : avant la bascule."""
    return _comparaison(simulateur, 1950)


@pytest.fixture(scope="module")
def parti_en_2044(simulateur):
    """Un salarié né en 1980, parti en 2044 : après elle."""
    return _comparaison(simulateur, 1980)


def _flux_a_la_main(simulateur, rendement: float) -> cycle_de_vie.Flux:
    """Dix ans de cotisations constantes en termes réels, de 2000 à 2009, puis
    dix ans de pension constante en termes réels, de 2010 à 2019 : la pension
    vaut la cotisation fois ``(1 + rendement)^10``, ce qui fait de
    ``rendement`` le rendement interne réel, exactement."""
    macro = simulateur.macro

    def euros(annee: int) -> float:
        return 1000.0 * macro.coefficient_prix(2000, annee)

    facteur = (1.0 + rendement) ** 10
    return cycle_de_vie.Flux(
        scenario="actuel",
        cotisations={annee: euros(annee) for annee in range(2000, 2010)},
        revenus={annee: 4.0 * euros(annee) for annee in range(2000, 2010)},
        niveaux={annee: facteur * euros(annee) for annee in range(2010, 2030)},
        debut=2010.0, age=60.0, sexe="H",
        dernier_revenu=4.0 * euros(2010),
    )


# -- le rendement interne ------------------------------------------------------


def test_le_rendement_d_un_placement_se_retrouve():
    assert cycle_de_vie.rendement_interne([(0.0, -100.0), (1.0, 105.0)]) == pytest.approx(0.05, abs=1e-9)
    assert cycle_de_vie.rendement_interne(
        [(2000.5, -100.0), (2010.5, 100.0 * 1.03 ** 10)]) == pytest.approx(0.03, abs=1e-9)


def test_sans_taux_qui_egalise_les_flux_aucun_rendement_n_est_rendu():
    """Des cotisations sans pension n'ont pas de rendement : ``None``, et non
    un nombre qu'aucune page ne saurait écrire."""
    assert cycle_de_vie.rendement_interne([(0.0, -100.0), (1.0, -5.0)]) is None
    assert cycle_de_vie.rendement_interne([]) is None


def test_un_rendement_connu_d_avance_se_retrouve_sur_des_flux_dates(simulateur):
    """Les cotisations au milieu de leur année, les pensions au milieu de la
    part servie : dix ans d'écart entre chaque cotisation et la pension qui
    lui répond, et un rendement réel de 2 % exactement."""
    flux = _flux_a_la_main(simulateur, 0.02)
    convention = cycle_de_vie.Convention(age_deces=70.0)
    resultat = cycle_de_vie.indicateurs(flux, simulateur, convention)
    assert resultat.rendement_reel == pytest.approx(0.02, abs=1e-9)
    assert resultat.duree_retraite == pytest.approx(10.0)
    assert resultat.duree_carriere == 10


def test_le_taux_de_recuperation_est_le_rapport_des_deux_sommes_en_salaire_moyen(simulateur):
    """La définition de TRAJECTOiRE (``txRecuperation``) : la somme des
    pensions sur la somme des cotisations, chaque montant divisé par le
    salaire moyen par tête de son année ; le taux d'annuité, la même chose
    sur les revenus d'activité."""
    flux = _flux_a_la_main(simulateur, 0.02)
    resultat = cycle_de_vie.indicateurs(flux, simulateur,
                                        cycle_de_vie.Convention(age_deces=70.0))
    macro = simulateur.macro

    def en_salaire_moyen(montants: dict[int, float]) -> float:
        return sum(montant / macro.coefficient_salaire_moyen(2000, annee)
                   for annee, montant in montants.items())

    pensions = en_salaire_moyen({annee: niveau for annee, niveau in flux.niveaux.items()
                                 if annee < 2020})
    assert resultat.taux_recuperation == pytest.approx(
        pensions / en_salaire_moyen(flux.cotisations), rel=1e-12)
    assert resultat.taux_annuite == pytest.approx(
        pensions / en_salaire_moyen(flux.revenus), rel=1e-12)
    assert resultat.taux_remplacement_cycle == pytest.approx(
        (pensions / 10.0) / (en_salaire_moyen(flux.revenus) / 10.0), rel=1e-12)


def test_le_patrimoine_sans_actualisation_est_la_somme_des_pensions_reelles(simulateur):
    """À un taux nul, la valeur au départ des pensions est leur somme en
    euros du départ : dix années de 1,02^10 fois la cotisation, rapportées à
    un dernier revenu de quatre cotisations."""
    flux = _flux_a_la_main(simulateur, 0.02)
    resultat = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(
        age_deces=70.0, taux_actualisation=0.0))
    assert resultat.patrimoine == pytest.approx(10.0 * 1.02 ** 10 / 4.0, rel=1e-12)


def test_au_taux_du_rendement_interne_la_valeur_nette_est_nulle(simulateur):
    """La valeur actuelle nette d'être couvert (PROST) : les pensions moins
    les cotisations, ramenées au départ au même taux réel. Au rendement
    interne réel, elles s'égalisent, par définition."""
    flux = _flux_a_la_main(simulateur, 0.02)
    au_rendement = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(
        age_deces=70.0, taux_actualisation=0.02))
    assert au_rendement.valeur_nette == pytest.approx(0.0, abs=1e-9)
    plus_bas = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(
        age_deces=70.0, taux_actualisation=0.01))
    assert plus_bas.valeur_nette > 0.0


def test_le_remplacement_au_deces_est_la_derniere_pension_contre_le_salaire_d_alors(
        simulateur, parti_en_2044):
    """La pension de la dernière année servie, rapportée au dernier revenu
    mené jusqu'à elle par le salaire moyen. Une pension du scénario 1 suit les
    prix, que les salaires dépassent : elle finit sous son taux du départ."""
    flux = _flux_a_la_main(simulateur, 0.02)
    resultat = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(age_deces=70.0))
    macro = simulateur.macro
    attendu = flux.niveaux[2019] / (flux.dernier_revenu
                                    * macro.coefficient_salaire_moyen(2010, 2019))
    assert resultat.remplacement_au_deces == pytest.approx(attendu, rel=1e-12)
    actuel = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2044)["actuel"]
    au_deces = cycle_de_vie.indicateurs(actuel, simulateur).remplacement_au_deces
    assert 0.0 < au_deces < parti_en_2044.taux_remplacement_actuel


def test_une_pension_nette_retire_le_prelevement_et_baisse_le_rendement(simulateur):
    flux = _flux_a_la_main(simulateur, 0.02)
    brute = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(age_deces=70.0))
    nette = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(
        age_deces=70.0, prelevement=0.1))
    assert nette.taux_recuperation == pytest.approx(0.9 * brute.taux_recuperation)
    assert nette.rendement_reel < brute.rendement_reel
    assert nette.duree_retraite == brute.duree_retraite


# -- la fin de la retraite -------------------------------------------------------


def test_sous_un_age_de_deces_fixe_la_retraite_dure_jusqu_a_lui(simulateur, parti_en_2044):
    flux = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2044)["actuel"]
    resultat = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(age_deces=87.5))
    assert resultat.duree_retraite == pytest.approx(87.5 - flux.age, abs=1e-9)
    assert resultat.part_de_vie == pytest.approx(resultat.duree_retraite / 87.5)


def test_sous_la_survie_la_duree_est_l_esperance_du_diviseur(simulateur, parti_en_2044):
    """L'intégrale de la survie à force constante par cellule, celle que
    suppose ``survie_annuelle`` : l'espérance de vie résiduelle de la table de
    génération, que ``esperance_residuelle`` calcule au trapèze, à un
    centième d'année près."""
    flux = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2044)["actuel"]
    resultat = cycle_de_vie.indicateurs(flux, simulateur)
    attendue = simulateur.mortalite.esperance_residuelle(flux.age, flux.debut, flux.sexe)
    assert resultat.duree_retraite == pytest.approx(attendue, abs=0.02)
    unisexe = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(unisexe=True))
    assert unisexe.duree_retraite > resultat.duree_retraite


def test_l_age_de_deces_du_cor_est_soixante_ans_et_l_esperance_de_vie_a_soixante_ans(simulateur):
    """« 60 + l'espérance de vie à 60 ans de la génération », les deux sexes
    réunis : la moyenne des deux espérances, puisque la table unisexe moyenne
    les deux survies."""
    mortalite = simulateur.mortalite
    hommes = mortalite.esperance_residuelle(60.0, 2020.0, "H")
    femmes = mortalite.esperance_residuelle(60.0, 2020.0, "F")
    assert cycle_de_vie.age_de_deces_cor(mortalite, 1960) == pytest.approx(
        60.0 + (hommes + femmes) / 2.0, abs=1e-9)


def test_la_convention_par_defaut_est_celle_de_l_ocde():
    convention = cycle_de_vie.Convention()
    assert (convention.age_deces, convention.unisexe, convention.taux_actualisation,
            convention.prelevement) == (None, False, 0.015, 0.0)


# -- ce que chaque système verse et reçoit ---------------------------------------


def test_les_scenarios_2_a_5_versent_ce_que_preleve_le_compte_du_scenario_4(simulateur):
    """Ils changent ce qui est porté au compte, pas ce que la paie supporte :
    ce que verse le scénario 1 jusqu'à la bascule, le taux du régime fusionné
    ensuite. Pour un agent de l'État parti après elle, c'est moins que la part
    de la contribution de l'État que le scénario 1 rattache à sa retraite."""
    comparaison = _comparaison(simulateur, 1980, affiliation="fonctionnaire_etat")
    flux = cycle_de_vie.flux_des_systemes(simulateur, comparaison)
    compte = {ligne.annee: ligne.cotisation
              for ligne in comparaison.notionnel_retroactif_employeur.compte.cotisations}
    bascule = simulateur.parametres.annee_bascule
    for scenario in cycle_de_vie.SCENARIOS[1:5]:
        assert flux[scenario].cotisations == {a: m for a, m in compte.items() if m}
    for annee, montant in flux["actuel"].cotisations.items():
        if annee < bascule:
            assert flux["notionnel_retroactif"].cotisations[annee] == pytest.approx(montant)
        else:
            assert flux["notionnel_retroactif"].cotisations[annee] < montant


def test_le_salarie_du_prive_verse_aussi_les_contributions_d_equilibre(
        simulateur, parti_en_2044):
    """Le compte ne porte pas les contributions d'équilibre de l'Agirc-Arrco ;
    la paie les supporte. Le scénario 1 les verse toute la carrière, en plus
    de ce que le compte prélève ; les scénarios 2 à 5 jusqu'à la bascule
    seulement, où le régime fusionné remplace la complémentaire et ses
    contributions."""
    flux = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2044)
    carriere = parti_en_2044.carriere
    equilibre = cycle_de_vie.contributions_d_une_carriere(simulateur, carriere)
    bascule = simulateur.parametres.annee_bascule
    assert min(equilibre) < bascule <= max(equilibre)
    compte = simulateur.constructeur_employeur.construire(
        carriere, annee_liquidation=carriere.annee_liquidation,
        annee_debut=carriere.premiere_annee)
    sans = {ligne.annee: ligne.cotisation for ligne in compte.cotisations}
    for annee, montant in equilibre.items():
        assert flux["actuel"].cotisations[annee] == pytest.approx(sans[annee] + montant)
    reforme = {ligne.annee: ligne.cotisation
               for ligne in parti_en_2044.notionnel_retroactif_employeur.compte.cotisations}
    for scenario in cycle_de_vie.SCENARIOS[1:5]:
        for annee, montant in flux[scenario].cotisations.items():
            avant = equilibre.get(annee, 0.0) if annee < bascule else 0.0
            assert montant == pytest.approx(reforme[annee] + avant), (scenario, annee)


def test_le_scenario_6_verse_son_taux_unique_et_son_pilier_apres_la_bascule(
        simulateur, parti_en_2044):
    flux = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2044)
    liberal = parti_en_2044.notionnel_liberal
    bascule = simulateur.parametres.annee_bascule
    versees = flux["notionnel_liberal"].cotisations
    for annee, montant in flux["actuel"].cotisations.items():
        if annee < bascule:
            assert versees[annee] == montant
    compte = {ligne.annee: ligne.cotisation for ligne in liberal.compte.cotisations}
    pilier = {annee.annee: annee.versement_brut for annee in liberal.capitalisation.annees}
    annee = bascule + 5
    assert versees[annee] == pytest.approx(compte[annee] + pilier[annee])
    assert pilier[annee] > 0.0


def test_le_scenario_1_sert_ce_que_le_droit_a_servi_jusqu_a_aujourd_hui(simulateur, parti_en_2014):
    """Jusqu'à l'année courante, la pension du scénario 1 est celle que
    l'étape « faire vivre » mène par les textes de chaque régime."""
    flux = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2014)["actuel"]
    courante = simulateur.parametres.annee_courante
    vivante = faire_vivre(simulateur, parti_en_2014.carriere, parti_en_2014.actuel, courante)
    servie = (sum(r.aujourd_hui for r in vivante.regimes if not r.hors_repartition)
              + vivante.majoration_enfants * vivante.coefficient_majoration)
    assert flux.niveaux[courante] == pytest.approx(servie, rel=1e-12)
    assert flux.niveaux[2014] < flux.niveaux[courante]


def test_une_reforme_prospective_garde_la_pension_de_qui_est_parti_avant_elle(
        simulateur, parti_en_2014):
    flux = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2014)
    bascule = simulateur.parametres.annee_bascule
    for scenario in ("notionnel_prospectif", "notionnel_prospectif_employeur"):
        for annee in range(2014, bascule + 1):
            assert flux[scenario].niveaux[annee] == flux["actuel"].niveaux[annee]


def test_une_pension_notionnelle_suit_la_regle_de_son_compte(simulateur, parti_en_2044):
    """De la liquidation à toute année, la pension du scénario 4 est sa
    pension de départ revalorisée par la règle du compte : les prix fois le
    coefficient réel de :class:`RevalorisationServie`, sur toute la retraite,
    et non jusqu'à l'année courante seulement."""
    flux = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2044)["notionnel_retroactif_employeur"]
    liquidation = parti_en_2044.carriere.annee_liquidation
    depart = parti_en_2044.notionnel_retroactif_employeur.pension_annuelle
    assert flux.niveaux[liquidation] == pytest.approx(depart)
    reel = flux.niveaux[liquidation + 20] / simulateur.macro.coefficient_prix(
        liquidation, liquidation + 20) / depart
    assert reel > 1.05


def test_la_pension_nette_retire_le_taux_plein_et_la_maladie_des_complementaires(
        simulateur, parti_en_2044):
    actuel = parti_en_2044.actuel
    complementaire = sum(p.montant for p in actuel.pensions_par_regime
                         if p.regime.startswith(("agirc", "arrco")))
    taux = cycle_de_vie.taux_de_prelevement(simulateur, actuel)
    assert taux == pytest.approx(0.091 + 0.01 * complementaire / actuel.pension_annuelle)


def test_les_indicateurs_de_chaque_systeme_se_calculent(simulateur, parti_en_2044):
    resultats = cycle_de_vie.indicateurs_des_systemes(simulateur, parti_en_2044)
    assert list(resultats) == list(cycle_de_vie.SCENARIOS)
    for scenario, resultat in resultats.items():
        assert resultat.rendement_reel is not None, scenario
        assert 0.0 < resultat.taux_recuperation < 5.0, scenario
        assert 0.0 < resultat.patrimoine < 30.0, scenario
        assert math.isfinite(resultat.duree_relative)


# -- le jeu d'hypothèses de l'OCDE ------------------------------------------------


def test_le_jeu_de_l_ocde_se_nomme_comme_un_scenario_de_projection():
    """Prix +2 %, salaires réels +1,25 % : 3,275 % de salaire nominal, le
    produit que l'OCDE écrit, et non la somme des scénarios du COR."""
    macro = DonneesMacro(RACINE_DONNEES, scenario_projection="ocde_2025")
    assert macro.inflation(2050) == pytest.approx(0.02)
    assert macro.salaire_moyen(2050) == pytest.approx(0.03275)
    assert macro.inflation(2020) == DonneesMacro(RACINE_DONNEES).inflation(2020)


def test_un_scenario_inconnu_reste_refuse():
    with pytest.raises(KeyError, match="ocde_2025"):
        DonneesMacro(RACINE_DONNEES, scenario_projection="inexistant").inflation(2050)


# -- en net ------------------------------------------------------------------------


def test_en_net_la_pension_nette_se_rapporte_au_revenu_net(simulateur, parti_en_2044):
    """Sous une convention nette, ce qui rapporte la pension à un revenu
    d'activité la rapporte au revenu net : le taux d'annuité net est le brut,
    fois la part de la pension qui reste, divisé par la part du revenu qui
    reste. Le patrimoine reste en années de dernier revenu brut, comme l'OCDE
    l'exprime."""
    flux = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2044, nets=True)["actuel"]
    brute = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(age_deces=87.0))
    nette = cycle_de_vie.indicateurs(flux, simulateur, cycle_de_vie.Convention(
        age_deces=87.0, prelevement=0.1))
    macro = simulateur.macro

    def en_salaire_moyen(montants: dict[int, float]) -> float:
        return sum(montant / macro.coefficient_salaire_moyen(2000, annee)
                   for annee, montant in montants.items())

    rapport = en_salaire_moyen(flux.revenus) / en_salaire_moyen(flux.revenus_nets)
    assert 1.2 < rapport < 1.3
    assert nette.taux_annuite == pytest.approx(0.9 * brute.taux_annuite * rapport, rel=1e-12)
    assert nette.taux_remplacement_cycle == pytest.approx(
        0.9 * brute.taux_remplacement_cycle * rapport, rel=1e-12)
    assert nette.patrimoine == pytest.approx(0.9 * brute.patrimoine, rel=1e-12)
    sans_net = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2044)["actuel"]
    assert sans_net.revenus_nets is None
    assert cycle_de_vie.indicateurs(sans_net, simulateur, cycle_de_vie.Convention(
        age_deces=87.0, prelevement=0.1)).taux_annuite is None


def test_le_scenario_6_lit_son_net_sur_la_fiche_de_la_proposition(simulateur, parti_en_2044):
    """Après la bascule, le revenu net du scénario 6 est celui que la fiche de
    paie de la proposition laisse du même brut — son rapport du net au brut,
    comme le site l'applique à son taux de remplacement net
    (``contexte.Montants``) ; les scénarios 1 à 5 gardent la fiche du droit en
    vigueur, et tous la gardent avant la bascule."""
    flux = cycle_de_vie.flux_des_systemes(simulateur, parti_en_2044, nets=True)
    bascule = simulateur.parametres.annee_bascule
    annee = bascule + 5
    remuneration = next(a for a in parti_en_2044.remuneration.annees if a.annee == annee)
    brut = flux["actuel"].revenus[annee]
    assert flux["notionnel_liberal"].revenus_nets[annee] == pytest.approx(
        brut * remuneration.proposition.net / remuneration.proposition.brut, rel=1e-12)
    assert flux["notionnel_liberal"].revenus_nets[annee] > flux["actuel"].revenus_nets[annee]
    for scenario in cycle_de_vie.SCENARIOS[1:5]:
        assert flux[scenario].revenus_nets == flux["actuel"].revenus_nets, scenario
    assert flux["notionnel_liberal"].revenus_nets[bascule - 1] == pytest.approx(
        flux["actuel"].revenus_nets[bascule - 1])


def test_les_primes_d_un_fonctionnaire_ne_paient_pas_la_retenue(simulateur):
    """La fiche de paie d'un fonctionnaire a pour assiette son traitement. À
    revenu égal, un quart de primes laisse un net plus fort, de la retenue
    pour pension que la loi n'assied pas sur elles."""
    def carriere(part_primes: float):
        return simulateur.carriere_simple(
            annee_naissance=1980, sexe="H", affiliation="fonctionnaire_etat", age_debut=22,
            age_liquidation=64, niveau_salaire=1.0, part_primes=part_primes)

    sans, avec = carriere(0.0), carriere(0.25)
    annee = 2030
    revenu = cycle_de_vie.revenus_d_activite(sans)[annee]
    assert cycle_de_vie.revenus_d_activite(avec)[annee] == pytest.approx(revenu)
    fiche = fiche_depuis_brut(simulateur.parametres.racine_donnees, simulateur.macro,
                              simulateur.catalogue, simulateur.affiliations,
                              "fonctionnaire_etat", annee, revenu)
    retenue = fiche.retraite_salarie / fiche.brut
    assert retenue > 0.1
    ecart = (cycle_de_vie.revenus_nets(simulateur, avec)[annee]
             - cycle_de_vie.revenus_nets(simulateur, sans)[annee])
    assert ecart == pytest.approx(0.25 * revenu * retenue, rel=1e-9)


def test_un_statut_sans_fiche_de_paie_n_a_pas_de_revenu_net(simulateur):
    exploitant = simulateur.carriere_simple(
        annee_naissance=1980, sexe="H", affiliation="exploitant_agricole", age_debut=20,
        age_liquidation=64, niveau_salaire=0.5)
    assert cycle_de_vie.revenus_nets(simulateur, exploitant) is None


# -- à chaque âge de départ ---------------------------------------------------------


def _cas(code: str):
    return next(cas for cas in CAS_TYPES if cas.code == code)


@pytest.fixture(scope="module")
def balayage_1970(simulateur):
    """Le salarié au salaire moyen né en 1970, à chacun de ses âges de départ."""
    return cycle_de_vie.balayage(simulateur, _cas("salaire_moyen"), 1970)


def test_les_ages_vont_de_l_ouverture_a_l_annulation_de_la_decote_par_trimestre(
        simulateur, balayage_1970):
    """De trimestre en trimestre, comme TRAJECTOiRE, de l'âge d'ouverture à
    l'âge d'annulation de la décote : 64 et 67 ans pour la génération 1970,
    sous la loi du 14 avril 2023. La carrière longue ouvre le droit plus tôt,
    et le balayage avec elle."""
    assert [depart.age for depart in balayage_1970] == [64.0 + 0.25 * rang for rang in range(13)]
    assert all(depart.annee == 1970 + int(depart.age) for depart in balayage_1970)
    longue = cycle_de_vie.ages_de_depart(simulateur, _cas("smic_carriere_complete"), 1970)
    assert longue[0] < 64.0
    assert longue[-1] == 67.0


def test_partir_plus_tard_raccourcit_la_retraite_et_releve_la_pension(balayage_1970):
    """Chaque trimestre de plus : une retraite plus courte, une pension nette
    plus forte, plus haut sur le minimum vieillesse, un taux de remplacement
    net plus fort."""
    for avant, apres in zip(balayage_1970, balayage_1970[1:]):
        assert (apres.indicateurs["actuel"].duree_retraite
                < avant.indicateurs["actuel"].duree_retraite)
        assert apres.pensions_nettes["actuel"] > avant.pensions_nettes["actuel"]
        assert apres.pensions_aspa["actuel"] > avant.pensions_aspa["actuel"]
        assert (apres.remplacements["actuel"].salaire_moyen
                >= avant.remplacements["actuel"].salaire_moyen)


def test_la_pension_nette_se_rapporte_au_minimum_vieillesse_de_son_annee(
        simulateur, balayage_1970):
    """La pension brute du premier mois servi, moins le taux plein de l'année
    courante et la maladie de sa part complémentaire, sur le minimum
    vieillesse d'une personne seule de l'année du départ. Le scénario 6, que
    son âge légal fait partir à 65 ans, se rapporte à celui de son année."""
    cas = _cas("salaire_moyen")
    depart = balayage_1970[0]
    comparaison = simulateur.simuler(cas.carriere_a(simulateur, 1970, depart.age))
    taux = cycle_de_vie.taux_de_prelevement(simulateur, comparaison.actuel)
    for scenario in cycle_de_vie.SCENARIOS:
        brute = cycle_de_vie.pension_au_depart(simulateur, comparaison, scenario)
        annee = comparaison.carriere_de(scenario).annee_liquidation
        assert depart.pensions_nettes[scenario] == pytest.approx(brute * (1.0 - taux))
        assert depart.pensions_aspa[scenario] == pytest.approx(
            depart.pensions_nettes[scenario] / cycle_de_vie.minimum_vieillesse(simulateur, annee))
    assert comparaison.depart_reporte
    assert comparaison.carriere_de("notionnel_liberal").annee_liquidation == 2035


def test_le_minimum_vieillesse_est_l_aspa_ou_ses_deux_etages(simulateur):
    bareme = simulateur.scenario_actuel.minimum_vieillesse
    assert cycle_de_vie.minimum_vieillesse(simulateur, 2026) == bareme.plafond(2026)[0]
    etages = bareme.deux_etages(2005)
    assert cycle_de_vie.minimum_vieillesse(simulateur, 2005) == pytest.approx(
        etages.avts + etages.supplementaire)
    assert cycle_de_vie.minimum_vieillesse(simulateur, 1930) is None


def test_les_trois_remplacements_nets_ne_different_que_par_le_deflateur(
        simulateur, balayage_1970):
    """La pension nette du départ sur le revenu net de la dernière année
    travaillée en entier : en euros courants, constants, en salaire moyen."""
    macro = simulateur.macro
    cas = _cas("salaire_moyen")
    for depart in balayage_1970[::4]:
        carriere = cas.carriere_a(simulateur, 1970, depart.age)
        annee = cycle_de_vie.derniere_annee_pleine(carriere)
        assert annee == depart.annee - 1
        remplacement = depart.remplacements["actuel"]
        nets = cycle_de_vie.revenus_nets(simulateur, carriere)
        assert remplacement.courants == pytest.approx(
            depart.pensions_nettes["actuel"] / nets[annee], rel=1e-12)
        assert remplacement.constants == pytest.approx(
            remplacement.courants / macro.coefficient_prix(annee, depart.annee), rel=1e-12)
        assert remplacement.salaire_moyen == pytest.approx(
            remplacement.courants / macro.coefficient_salaire_moyen(annee, depart.annee),
            rel=1e-12)


def test_les_hypotheses_de_productivite_sont_les_trois_du_cor():
    assert cycle_de_vie.hypotheses_de_productivite(RACINE_DONNEES) == (
        "cor_productivite_basse", "cor_reference", "cor_productivite_haute")


def test_sous_une_productivite_plus_forte_la_pension_monte_sur_l_aspa():
    """La génération 2000, partie à 64 ans en 2064. Plus la productivité est
    forte, plus les salaires dépassent les prix : sa pension, qui suit les
    salaires jusqu'au départ, monte sur le minimum vieillesse, qui suit les
    prix ; ses pensions, qui suivent les prix ensuite, rendent moins en
    salaire moyen."""
    cas = _cas("salaire_moyen")
    departs = []
    for nom in cycle_de_vie.hypotheses_de_productivite(RACINE_DONNEES):
        simulateur = Simulateur(Parametres(scenario_projection=nom))
        comparaison = simulateur.simuler(cas.carriere_a(simulateur, 2000, 64.0))
        departs.append(cycle_de_vie.depart(simulateur, comparaison))
    aspa = [depart.pensions_aspa["actuel"] for depart in departs]
    recuperation = [depart.indicateurs["actuel"].taux_recuperation for depart in departs]
    assert aspa[0] < aspa[1] < aspa[2]
    assert recuperation[0] > recuperation[1] > recuperation[2]


# ---------------------------------------------------------------------------
# L'âge d'équilibre
# ---------------------------------------------------------------------------


def test_la_reference_est_la_generation_qui_a_l_age_de_reference_a_la_bascule(simulateur):
    """Le diviseur de référence est celui que le compte prend pour convertir
    les droits acquis : l'âge de référence, 65 ans, au 1er janvier de l'année
    de la bascule, 2026 ; la génération 1961 y retrouve le sien à 65 ans
    exactement."""
    reference = cycle_de_vie.reference_du_compte(simulateur)
    assert (reference.naissance, reference.age, reference.annee) == (1961.0, 65.0, 2026)
    equilibre = cycle_de_vie.age_d_equilibre(simulateur, 1961)
    assert equilibre.diviseur_reference == simulateur.convertisseur.coefficient(
        65.0, 2026).diviseur
    assert (equilibre.age, equilibre.au_mois, equilibre.coefficient) == (65.0, 65.0, 1.0)


def test_a_l_age_d_equilibre_le_capital_rend_la_pension_de_la_reference(simulateur):
    """Au premier mois de l'âge d'équilibre, le diviseur ne dépasse plus celui
    de la référence : à capital égal, la pension l'atteint ; le mois d'avant,
    non. Les générations nées avant la référence y sont plus tôt qu'elle, les
    suivantes plus tard, d'autant plus qu'elles vivront plus longtemps."""
    ages = []
    for generation in (1940, 1950, 1970, 1980, 2000):
        equilibre = cycle_de_vie.age_d_equilibre(simulateur, generation)
        au_mois = equilibre.au_mois
        assert (cycle_de_vie.diviseur_a(simulateur, generation, au_mois)
                <= equilibre.diviseur_reference
                < cycle_de_vie.diviseur_a(simulateur, generation, au_mois - 1 / 12))
        assert au_mois - 1 / 12 < equilibre.age <= au_mois
        assert (equilibre.coefficient > 1.0) == (generation < 1961)
        ages.append(equilibre.age)
    assert ages == sorted(ages)
    assert ages[0] < 65.0 < ages[2]


def test_sans_prefinancement_l_age_d_equilibre_tient_la_duree_de_retraite(simulateur):
    """Le taux de préfinancement étant nul, le diviseur est l'espérance de vie
    résiduelle : à l'âge d'équilibre, chaque génération espère la retraite de
    la référence, en années, à l'interpolation entre deux mois près."""
    mortalite = simulateur.mortalite
    attendue = mortalite.esperance_residuelle(65.0, 2026.0, None)
    for generation in (1940, 1970, 2000):
        age = cycle_de_vie.age_d_equilibre(simulateur, generation).age
        assert mortalite.esperance_residuelle(age, generation + age, None) == pytest.approx(
            attendue, abs=0.001)


def test_l_age_de_part_de_vie_constante_est_celui_que_croise_le_balayage(
        simulateur, balayage_1970):
    """La part de vie de :func:`part_de_vie` est celle que le balayage calcule
    à chaque âge de départ, au millionième ; l'âge où elle rejoint celle de la
    référence, un homme de la génération 1961 parti à 65 ans, est celui où la
    courbe du balayage la croise, à l'interpolation entre deux trimestres
    près."""
    cas = _cas("salaire_moyen")
    cible = cycle_de_vie.part_de_vie(simulateur, 65.0, 2026.0, "H")
    points = []
    for depart in balayage_1970:
        carriere = cas.carriere_a(simulateur, 1970, depart.age)
        debut = carriere.annee_liquidation + carriere.fraction_annee_liquidation
        part = depart.indicateurs["actuel"].part_de_vie
        assert cycle_de_vie.part_de_vie(simulateur, depart.age, debut, "H") == pytest.approx(
            part, abs=1e-6)
        points.append((depart.age, part, debut - depart.age))
    (age_avant, avant, naissance), (age_apres, apres, _) = next(
        (un, deux) for un, deux in zip(points, points[1:]) if un[1] > cible >= deux[1])
    croisement = age_avant + (avant - cible) / (avant - apres) * (age_apres - age_avant)
    assert cycle_de_vie.age_de_part_de_vie_constante(simulateur, naissance, "H") == pytest.approx(
        croisement, abs=0.002)


def test_sous_la_convention_du_cor_l_age_suit_l_age_de_deces(simulateur):
    """Sous la convention du COR, la part de vie est (D − âge) / D : l'âge qui
    la tient est celui de référence fois le rapport des âges de décès."""
    mortalite = simulateur.mortalite
    for generation in (1940, 2000):
        age = cycle_de_vie.age_de_part_de_vie_constante(simulateur, generation, cor=True)
        assert age == pytest.approx(65.0 * cycle_de_vie.age_de_deces_cor(mortalite, generation)
                                    / cycle_de_vie.age_de_deces_cor(mortalite, 1961), abs=1e-12)
        assert cycle_de_vie.part_de_vie(simulateur, age, generation + age, cor=True) == (
            pytest.approx(cycle_de_vie.part_de_vie(simulateur, 65.0, 2026.0, cor=True),
                          abs=1e-12))


def test_les_ages_d_un_cas_type_ne_tiennent_qu_a_sa_mortalite(simulateur):
    """Le cas type n'entre dans ses âges d'équilibre que par la mortalité de
    son diviseur, la population où son salaire le range, et par son sexe pour
    la part de vie : le salarié au salaire moyen et le fonctionnaire de
    catégorie active, du même vingtile, ont les mêmes âges, à des âges de
    départ que cinq années séparent. Le salarié au SMIC, d'un vingtile qui
    vit moins longtemps, retrouve plus tard la référence : de 1961 à 2000,
    son diviseur à 65 ans gagne 3,58 ans, contre 3,38, et il baisse moins
    vite avec l'âge, de 0,83 an par an, contre 0,88."""
    moyen = cycle_de_vie.ages_d_equilibre(simulateur, _cas("salaire_moyen"), 2000)
    actif = cycle_de_vie.ages_d_equilibre(simulateur, _cas("fonctionnaire_actif"), 2000)
    smic = cycle_de_vie.ages_d_equilibre(simulateur, _cas("smic_carriere_complete"), 2000)
    assert moyen.population == actif.population == "niveau_de_vie_v14"
    assert moyen.age_de_depart - actif.age_de_depart == 5.0
    assert (moyen.diviseur, moyen.part_de_vie) == (actif.diviseur, actif.part_de_vie)
    assert moyen.diviseur == cycle_de_vie.age_d_equilibre(simulateur, 2000, "H", moyen.population)
    assert smic.population == "niveau_de_vie_v04"
    assert smic.diviseur.age > moyen.diviseur.age
    assert smic.part_de_vie > moyen.part_de_vie
