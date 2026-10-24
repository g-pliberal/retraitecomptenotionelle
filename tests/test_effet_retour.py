"""L'effet retour de la page Coût (action 138, étape 5) : l'ASPA que les
petites pensions des scénarios 2 à 5 déclenchent, et les prélèvements que
leurs pensions ne paient plus, rapportés à l'économie des régimes. L'IPP
(Perspectives budgétaires 2027, juin 2026) trouve un gain public « inférieur
d'environ 20 % à 25 % » à l'économie des régimes."""

import pytest

from retraite_notionnelle import memoire
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.donnees.impot_revenu import FRANC
from retraite_notionnelle.effet_retour import (
    SCENARIOS_EFFET_RETOUR,
    SCENARIOS_PROSPECTIFS,
    SeuilsCsg,
    _deformer,
    _points,
    charger_seuils_csg,
    complement_minimum,
    tranche_csg,
)
from retraite_notionnelle.garantie import pension_moyenne
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.somme import somme_ordonnee


@pytest.fixture(scope="module")
def avenir():
    return memoire.cout(Parametres()).avenir


def test_chaque_annee_de_la_trajectoire_a_son_effet_retour(avenir):
    """Depuis le 16 octobre 2026, chaque année a son barème de CSG : rien
    avant 2019 n'est plus laissé à zéro. Avant février 1991, sans CSG, les
    prélèvements ne sont que l'impôt ; la CSG les fait monter ensuite."""
    taux = {}
    for annee in (avenir.annees[0].annee, 1995, 2005, 2015, 2025):
        effet = avenir.annee(annee).effet_retour
        assert set(effet.prelevements) == set(SCENARIOS_EFFET_RETOUR)
        assert avenir.annee(annee).effet_retour_constants("notionnel_retroactif") > 0.0
        taux[annee] = effet.prelevements["notionnel_retroactif"]
    assert avenir.annees[0].annee < 1991
    annees = sorted(taux)
    assert all(taux[a] < taux[b] for a, b in zip(annees, annees[1:]))
    assert 0.0 < taux[annees[0]] < 0.08


@pytest.mark.parametrize("scenario", ("notionnel_retroactif", "notionnel_retroactif_employeur"))
def test_les_annees_passees_dans_l_ordre_de_grandeur(avenir, scenario):
    """De 1990 à 2018, sous des barèmes plus légers, l'effet retour reprend
    un peu moins de l'économie qu'après 2026, mais garde l'ordre de l'IPP."""
    passe = avenir.part_effet_retour(scenario, 1990, 2018)
    assert passe is not None and 0.15 < passe < avenir.part_effet_retour(scenario, 2026, 2070)


def test_les_seuils_de_chaque_annee():
    seuils = charger_seuils_csg(Simulateur(Parametres()).parametres.racine_donnees)
    assert min(seuils) == 1991 and max(seuils) == 2025
    assert set(range(1991, 2026)) == set(seuils)
    assert {seuils[a].regle for a in range(1991, 1998)} == {"impot"}
    assert {seuils[a].regle for a in range(1998, 2015)} == {"impot_et_revenu"}
    assert {seuils[a].regle for a in range(2015, 2026)} == {"revenu"}
    # Le franc converti ; 10 224 € pour 2014, 10 633 € et 13 900 € pour 2015,
    # que L. 136-8 écrit ; le taux médian depuis 2019.
    assert seuils[1998].exoneration == pytest.approx(43080 / FRANC)
    assert seuils[2014].exoneration == 10224
    assert (seuils[2015].exoneration, seuils[2015].reduit) == (10633, 13900)
    assert seuils[2018].median is None and seuils[2019].median == 22580
    # Le seuil monte chaque année, sauf la réforme de 2006, qui le relève
    # d'un quart en fondant l'abattement de 20 % dans le barème, et le gel
    # de 2012.
    for annee in range(1999, 2026):
        assert seuils[annee].exoneration >= seuils[annee - 1].exoneration
    assert seuils[2008].exoneration / seuils[2007].exoneration > 1.25


def test_la_tranche_selon_la_regle_de_l_annee():
    avant_1998 = SeuilsCsg(1995, "impot")
    assert tranche_csg(avant_1998, 1e9, impot_recouvre=False) == "exonere"
    assert tranche_csg(avant_1998, 0.0, impot_recouvre=True) == "plein"
    mixte = SeuilsCsg(2010, "impot_et_revenu", exoneration=9837.0)
    assert tranche_csg(mixte, 9837.0, impot_recouvre=False) == "exonere"
    assert tranche_csg(mixte, 9838.0, impot_recouvre=False) == "reduit"
    assert tranche_csg(mixte, 9838.0, impot_recouvre=True) == "plein"
    revenu = SeuilsCsg(2019, "revenu", 11128.0, 14548.0, 22580.0)
    assert [tranche_csg(revenu, r, impot_recouvre=False)
            for r in (11128.0, 14000.0, 20000.0, 22580.0)] == [
        "exonere", "reduit", "median", "plein"]
    assert tranche_csg(SeuilsCsg(2016, "revenu", 10676.0, 13956.0), 20000.0, False) == "plein"


def test_au_deuxieme_seuil_la_caisse_garde_le_taux_reduit_depuis_2019():
    """Au deuxième seuil même : le taux plein jusqu'en 2018, le réduit depuis ;
    au troisième, le plein. Les barèmes de la Cnav de 2015 à 2025 (« Seuils de
    revenus pour assujettissement et taux de la CSG », circulaires 2015/3 à
    2024/35) mettent le taux normal au revenu « au moins égal » au deuxième
    seuil jusqu'en 2018, au troisième depuis, et le médian au revenu qui
    « dépasse » le deuxième. L. 136-8, III, l'écrit « inférieurs ou égaux »
    depuis le 16 décembre 2020 (LEGIARTI000042683546) ; en 2019 et en 2020, son
    « inférieurs à » et le « excèdent » du III bis ne rangeaient le deuxième
    seuil sous aucun des deux taux, et la caisse l'a laissé au réduit (action
    137, EUROMOD rejoué)."""
    seuils = charger_seuils_csg(Simulateur(Parametres()).parametres.racine_donnees)
    for annee in range(2015, 2026):
        s = seuils[annee]
        if annee < 2019:
            assert tranche_csg(s, s.reduit, False) == "plein", annee
        else:
            assert [tranche_csg(s, r, False) for r in (s.reduit, s.reduit + 1, s.median)] == [
                "reduit", "median", "plein"], annee


def test_le_scenario_6_n_en_a_pas(avenir):
    """Sa garantie vieillesse, qui remplace l'ASPA, est chiffrée à part."""
    ligne = avenir.annee(2050)
    assert ligne.effet_retour.taux("notionnel_liberal") == 0.0
    assert ligne.gain_public_constants("notionnel_liberal") == pytest.approx(
        ligne.economie_constants("notionnel_liberal"))


def test_le_gain_public_est_l_economie_moins_l_effet_retour(avenir):
    for annee in (2030, 2050, 2070):
        ligne = avenir.annee(annee)
        for scenario in SCENARIOS_EFFET_RETOUR:
            economie = ligne.economie_constants(scenario)
            effet = ligne.effet_retour
            assert ligne.gain_public_constants(scenario) == pytest.approx(
                economie - effet.taux(scenario) * economie
                - effet.aspa_deformation[scenario]
                * ligne.pensions_propres_constants(scenario))


@pytest.mark.parametrize("scenario", SCENARIOS_EFFET_RETOUR)
def test_l_ordre_de_grandeur_de_l_ipp(avenir, scenario):
    """De 2026 à 2070, l'effet retour reprend entre 15 et 35 % de
    l'économie : l'IPP en trouve 20 à 25, sur un calage de l'ASPA qu'il dit
    grossier."""
    part = avenir.part_effet_retour(scenario, 2026, 2070)
    assert part is not None and 0.15 < part < 0.35


@pytest.mark.parametrize("scenario", SCENARIOS_EFFET_RETOUR)
def test_chaque_euro_economise_paie_au_moins_la_csg(avenir, scenario):
    """Une pension qui baisse perd au moins ce que le taux réduit prélève,
    au plus la CSG pleine, la CRDS, la CASA et la tranche à 45 %."""
    ligne = avenir.annee(2060)
    if ligne.economie_constants(scenario) <= 0.0:
        pytest.skip("le scénario n'épargne rien cette année-là")
    assert 0.04 < ligne.effet_retour.prelevements[scenario] < 0.55
    assert ligne.effet_retour.aspa[scenario] >= 0.0


def test_la_tranche_ouverte_redonne_la_moyenne_publiee():
    simulateur = Simulateur(Parametres())
    distribution = simulateur.distribution
    moyenne = simulateur.caracteristiques.valeur("pension_droit_direct_majorations", "ensemble")
    points = _points(distribution, moyenne)
    total = somme_ordonnee(part for _, part in points)
    assert somme_ordonnee(m * p for m, p in points) / total == pytest.approx(moyenne)
    assert points[-1][0] > distribution.tranches[-1].borne_inferieure


@pytest.mark.parametrize("scenario", SCENARIOS_EFFET_RETOUR)
def test_sans_minimum_l_aspa_coute_plus_a_pension_egale(avenir, scenario):
    """La distribution d'un scénario sans minimum est déformée : à pension
    moyenne égale, son ASPA dépasse celle de la distribution déplacée, d'un
    peu moins de 2 % de ses pensions propres."""
    for annee in (2030, 2050, 2070):
        deformation = avenir.annee(annee).effet_retour.aspa_deformation[scenario]
        assert 0.0 <= deformation < 0.02


def test_les_prospectifs_gardent_le_minimum_de_leur_stock(avenir):
    """Juste après la bascule, presque tout ce que les scénarios prospectifs
    servent l'est encore au droit actuel, minimum compris."""
    debut, fin = avenir.annee(2026).effet_retour, avenir.annee(2070).effet_retour
    for scenario in SCENARIOS_PROSPECTIFS:
        assert debut.aspa_deformation[scenario] < 0.25 * fin.aspa_deformation[scenario]
    assert debut.aspa_deformation["notionnel_retroactif"] > 0.005


def test_la_deformation_retire_le_complement_au_bas_sans_toucher_la_moyenne():
    simulateur = Simulateur(Parametres())
    distribution = simulateur.distribution
    complement = complement_minimum(simulateur.parametres.racine_donnees,
                                    distribution.millesime)
    assert complement == pytest.approx(122.2)
    caracteristiques = simulateur.caracteristiques
    part = (caracteristiques.beneficiaires_minimum("ensemble")
            / caracteristiques.valeur("effectifs", "ensemble"))
    deformee = _deformer(distribution, part, complement)
    assert deformee.part_minimum == pytest.approx(part)
    assert somme_ordonnee(t.part for t in deformee.tranches) == pytest.approx(1.0)
    assert pension_moyenne(deformee) == pytest.approx(pension_moyenne(distribution))
    # Le bas perd le complément, en moyenne ; le haut gagne ce qu'il perd.
    assert deformee.facteur_bas < 1.0 < deformee.facteur_haut
    bas = [t for t in deformee.tranches[:len(distribution.tranches)]
           if t.borne_superieure is not None][:5]
    origine = distribution.tranches[:5]
    assert all(d.borne_superieure < o.borne_superieure for d, o in zip(bas, origine))
    assert _deformer(distribution, 0.0, complement).tranches == distribution.tranches
