"""Les indicateurs de cycle de vie : leurs définitions, sur des flux faits à la main.

``retraite_notionnelle.cycle_de_vie`` voit une carrière, sous chacun des six
systèmes, comme deux chroniques — ce qu'elle verse, ce qu'elle reçoit — et en
tire la durée de retraite, le taux de récupération, le rendement interne et le
patrimoine retraite (action 138, étape 9). Ce module tient les définitions :
un rendement qu'on connaît d'avance se retrouve, une durée de retraite est
celle que la convention dit, un taux de récupération est le rapport de deux
sommes, et chaque système reçoit et verse ce que le modèle lui prête. La
confrontation aux chiffres publiés par le COR, TRAJECTOiRE et l'OCDE est dans
``tests/test_cycle_de_vie_references.py``.
"""

from __future__ import annotations

import math

import pytest

from retraite_notionnelle import cycle_de_vie
from retraite_notionnelle.config import RACINE_DONNEES, Parametres
from retraite_notionnelle.donnees.macro import DonneesMacro
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
