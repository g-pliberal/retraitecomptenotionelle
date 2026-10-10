"""L'histoire des prélèvements sur les pensions et sur les salaires.

``prelevements_historiques.yaml``, qu'écrit ``scripts/fetch/ipp_prelevements_sociaux.py``
depuis les barèmes de l'IPP, donne aux indicateurs de cycle de vie nets les taux
de chaque année (action 138, étape 9). Ce module tient trois choses : que la
dernière marche de chaque série est le barème de l'année courante que le site
applique (``prelevements_remuneration.yaml``) ; que les marches connues y sont,
suppressions comprises ; que le salaire net de l'année courante est celui de la
fiche de paie, et qu'une année ancienne en change ce que l'histoire dit.
"""

from __future__ import annotations

import datetime as dt

import pytest

from retraite_notionnelle import cycle_de_vie
from retraite_notionnelle.config import RACINE_DONNEES, Parametres
from retraite_notionnelle.donnees.prelevements_historiques import (
    charger_prelevements_historiques,
)
from retraite_notionnelle.remuneration import charger_prelevements, fiche_depuis_brut
from retraite_notionnelle.simulateur import Simulateur

APRES = dt.date(2026, 6, 1)


@pytest.fixture(scope="module")
def historique():
    return charger_prelevements_historiques(RACINE_DONNEES)


@pytest.fixture(scope="module")
def courants():
    return charger_prelevements(RACINE_DONNEES)


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def test_la_derniere_marche_des_pensions_est_le_bareme_du_site(historique, courants):
    """La CSG au taux plein, médian et réduit, la CRDS, la CASA et la maladie
    des complémentaires de l'année courante sont celles que le site prélève ;
    la maladie des pensions du régime général n'existe plus depuis 1998."""
    pensions = courants.pensions
    taux = {tranche.libelle: tranche.taux for tranche in pensions.bareme_csg}
    assert historique.taux_csg_pension(APRES, "plein") == pytest.approx(taux["taux plein"])
    assert historique.taux_csg_pension(APRES, "median") == pytest.approx(taux["taux médian"])
    assert historique.taux_csg_pension(APRES, "reduit") == pytest.approx(taux["taux réduit"])
    assert historique.pensions["crds"].valeur(APRES) == pytest.approx(pensions.crds)
    assert historique.pensions["casa"].valeur(APRES) == pytest.approx(pensions.casa)
    assert historique.pensions["maladie_complementaires"].valeur(APRES) == pytest.approx(
        pensions.maladie_complementaire)
    assert historique.pensions["maladie_regime_general"].valeur(APRES) == 0.0


def test_la_derniere_marche_des_salaires_est_la_fiche_du_site(historique, courants):
    """La CSG et la CRDS d'activité, et leur abattement jusqu'à quatre
    plafonds, sont celles de la fiche de paie ; la maladie, le veuvage, le
    chômage salariés et la solidarité des agents publics n'existent plus."""
    profil = courants.profil("salarie_prive")
    csg = historique.salaires["csg"].en_vigueur(APRES)
    assert csg["taux"] == pytest.approx(profil.csg)
    assert historique.salaires["crds"].valeur(APRES) == pytest.approx(profil.crds)
    abattement = profil.abattement_frais[0]
    assert (abattement.haut_en_plafonds, abattement.taux) == (
        4.0, pytest.approx(csg["abattement_jusqu_a_quatre_plafonds"]))
    for serie in ("maladie_prive", "veuvage_prive", "chomage_prive", "maladie_etat",
                  "maladie_collectivites", "solidarite_public"):
        assert not any(historique.salaires[serie].en_vigueur(APRES).values()), serie


def test_les_marches_connues_y_sont(historique):
    """Quelques marches, et les suppressions que l'IPP marque d'une ligne aux
    cellules vides."""
    pensions, salaires = historique.pensions, historique.salaires
    assert historique.taux_csg_pension(dt.date(2017, 6, 1), "plein") == pytest.approx(0.066)
    assert historique.taux_csg_pension(dt.date(2018, 6, 1), "plein") == pytest.approx(0.083)
    assert historique.taux_csg_pension(dt.date(1990, 6, 1), "plein") == 0.0
    assert historique.taux_csg_pension(dt.date(2018, 6, 1), "median") == 0.0
    assert pensions["maladie_regime_general"].valeur(dt.date(1997, 6, 1)) == pytest.approx(0.028)
    assert pensions["maladie_complementaires"].valeur(dt.date(1997, 6, 1)) == pytest.approx(0.038)
    assert pensions["maladie_complementaires"].valeur(dt.date(1998, 6, 1)) == pytest.approx(0.01)
    assert pensions["maladie_complementaires"].valeur(dt.date(1980, 6, 1)) == 0.0
    assert salaires["maladie_prive"].valeur(dt.date(1995, 6, 1), "tout_salaire") == pytest.approx(0.068)
    assert salaires["maladie_prive"].valeur(dt.date(2018, 6, 1), "tout_salaire") == 0.0
    assert salaires["chomage_prive"].valeur(dt.date(2018, 6, 1), "sous_plafond") == pytest.approx(0.0095)
    assert salaires["chomage_prive"].valeur(dt.date(2018, 11, 1), "sous_plafond") == 0.0
    assert salaires["veuvage_prive"].valeur(dt.date(2004, 6, 1), "tout_salaire") == pytest.approx(0.001)
    assert salaires["veuvage_prive"].valeur(dt.date(2004, 8, 1), "tout_salaire") == 0.0
    assert salaires["solidarite_public"].valeur(dt.date(2010, 6, 1)) == pytest.approx(0.01)


def test_la_maladie_d_avant_1967_tient_les_taux_de_1967(historique):
    """Les barèmes de l'IPP prennent la maladie en 1967 ; elle existait
    avant : ses premiers taux valent en deçà, et la donnée le dit. La CSG,
    née en 1991, ne prélève rien avant."""
    maladie = historique.salaires["maladie_prive"]
    assert maladie.en_vigueur(dt.date(1960, 1, 1)) == maladie.marches[0][1]
    assert historique.salaires["csg"].en_vigueur(dt.date(1960, 1, 1)) == {}


def test_une_annee_qui_change_de_taux_preleve_la_moyenne_de_ses_mois(historique):
    """La maladie des pensions naît le 1er juillet 1980 : 1 % sur le régime
    général, 2 % sur les complémentaires, la moitié de l'année."""
    assert historique.taux_pension_annuel(1980, 0.6, 0.4) == pytest.approx(
        0.5 * (0.01 * 0.6 + 0.02 * 0.4))
    assert historique.taux_pension_annuel(1979, 0.6, 0.4) == 0.0


def test_le_prive_de_1995_paie_maladie_veuvage_chomage_et_csg(historique, simulateur):
    """Sous le plafond, en 1995 : la CSG de 2,4 % sur tout le brut, que l'IPP
    n'abat pas avant 1998, la maladie de 6,8 %, le veuvage de 0,1 %, le
    chômage de 2,42 %."""
    plafond = simulateur.macro.plafond_securite_sociale(1995)
    brut = 0.8 * plafond
    assert historique.hors_retraite_annuel("prive", 1995, brut, plafond) == pytest.approx(
        brut * (0.024 + 0.068 + 0.001 + 0.0242))


def test_le_salaire_net_de_l_annee_courante_est_celui_de_la_fiche(simulateur):
    """L'année courante, l'histoire et la fiche de paie disent la même chose ;
    une année ancienne retire ce que ses taux retiraient de plus."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1970, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=21,
        age_liquidation=67, niveau_salaire=1.0)
    nets = cycle_de_vie.revenus_nets(simulateur, carriere)
    bruts = cycle_de_vie.revenus_d_activite(carriere)
    courante = simulateur.parametres.annee_courante
    fiche = fiche_depuis_brut(simulateur.parametres.racine_donnees, simulateur.macro,
                              simulateur.catalogue, simulateur.affiliations,
                              "salarie_prive_non_cadre", courante, bruts[courante])
    assert nets[courante] == pytest.approx(fiche.net, rel=1e-12)
    assert nets[1995] / bruts[1995] < nets[courante] / bruts[courante]


#: Les postes de la fiche d'un indépendant que l'histoire refait.
REFAITS = ("maladie_maternite", "indemnites_journalieres", "famille", "csg_crds")


def test_l_annee_courante_d_un_independant_est_la_fiche_du_site(historique, courants,
                                                                 simulateur):
    """L'année courante, la maladie et l'indemnité journalière des artisans et
    commerçants, les allocations familiales, la CSG et la CRDS de l'histoire
    sont, au centime, celles de la fiche de paie, du taux réduit des petits
    revenus aux tranches des plus grands."""
    annee = courants.annee
    plafond = simulateur.macro.plafond_securite_sociale(annee)
    for niveau in (0.1, 0.3, 0.5, 0.8, 1.2, 1.6, 2.5, 3.5, 6.0):
        revenu = niveau * plafond
        fiche = fiche_depuis_brut(RACINE_DONNEES, simulateur.macro, simulateur.catalogue,
                                  simulateur.affiliations, "commercant", annee, revenu)
        refaits = sum(l.salarie for l in fiche.lignes if l.code in REFAITS)
        autres = sum(l.salarie for l in fiche.lignes if l.code not in REFAITS)
        assert historique.hors_retraite_annuel("commercant", annee, revenu, plafond, autres) == (
            pytest.approx(refaits, rel=1e-9)), niveau


def test_les_marches_des_independants_y_sont(historique):
    """Les tranches de l'IPP qui s'ajoutent, ses marches corrigées par les
    décrets, et les barèmes des textes depuis 2013 ; l'indemnité journalière des
    seuls artisans de 1995 à 2000, des libéraux depuis 2021, que l'avocat ne
    paie pas."""
    plafond = 40_000.0

    def taux(famille, jour, niveau):
        revenu = niveau * plafond
        return historique.maladie_independant(famille, jour, revenu, plafond) / revenu

    assert taux("commercant", dt.date(1985, 6, 1), 0.8) == pytest.approx(0.031 + 0.0845)
    assert taux("commercant", dt.date(1985, 6, 1), 2.0) == pytest.approx(
        (0.031 + 0.0845 * 2.0) / 2.0)
    # Le décret n° 91-745 vaut à l'échéance du 1er octobre 1991, et le décret
    # n° 92-295 porte 9,75 % à celle du 1er octobre 1992 : l'IPP les avance.
    assert taux("commercant", dt.date(1991, 9, 1), 0.8) == pytest.approx(0.031 + 0.0885)
    assert taux("commercant", dt.date(1991, 11, 1), 0.8) == pytest.approx(0.031 + 0.0915)
    assert taux("commercant", dt.date(1993, 6, 1), 0.8) == pytest.approx(0.031 + 0.0975)
    assert taux("liberal", dt.date(1984, 6, 1), 0.8) == pytest.approx(0.037 + 0.0795)
    assert taux("liberal", dt.date(1984, 11, 1), 0.8) == pytest.approx(0.031 + 0.0845)
    assert taux("artisan", dt.date(1996, 6, 1), 0.8) - taux("commercant", dt.date(1996, 6, 1),
                                                             0.8) == pytest.approx(0.005)
    assert taux("commercant", dt.date(2015, 6, 1), 0.8) == pytest.approx(0.065 + 0.007)
    # 2018 : le taux réduit sous 40 % du plafond, et 6,5 % sur tout le revenu
    # au-delà de cinq plafonds ; la fraction au-delà seulement depuis mai 2020.
    assert taux("commercant", dt.date(2018, 6, 1), 0.2) == pytest.approx(
        0.0085 + (0.022 + 0.05 / 1.1 * 0.4 - 0.0085) / 2.0)
    assert taux("commercant", dt.date(2018, 6, 1), 6.0) == pytest.approx(0.065)
    assert taux("commercant", dt.date(2021, 6, 1), 6.0) == pytest.approx(
        (0.072 * 5.0 + 0.065) / 6.0)
    assert taux("liberal", dt.date(2022, 6, 1), 0.3) == pytest.approx(0.003)
    assert taux("avocat", dt.date(2022, 6, 1), 0.3) == 0.0
    assert taux("commercant", dt.date(1969, 6, 1), 0.8) == 0.0

    def famille(jour, niveau):
        revenu = niveau * plafond
        return historique.famille_independant(jour, revenu, plafond) / revenu

    assert famille(dt.date(1990, 6, 1), 0.8) == pytest.approx(0.021 + 0.049)
    assert famille(dt.date(2010, 6, 1), 0.8) == pytest.approx(0.054)
    assert famille(dt.date(2016, 6, 1), 1.25) == pytest.approx(0.0215 + 0.031 / 2.0)
    assert famille(dt.date(2016, 6, 1), 0.8) == pytest.approx(0.0215)
    # Forfaitaire avant 1974, que l'IPP ne chiffre pas : ses taux de 1974 valent
    # en deçà.
    assert famille(dt.date(1970, 6, 1), 0.8) == famille(dt.date(1975, 6, 1), 0.8)


def test_la_csg_d_un_independant_porte_sur_ses_cotisations_jusqu_en_2024(historique):
    """Jusqu'en 2024, la CSG et la CRDS d'un indépendant portent sur son revenu
    augmenté de ses cotisations personnelles (L. 136-3) ; depuis l'assiette
    unique, sur son revenu."""
    plafond, revenu, autres = 46_000.0, 40_000.0, 9_000.0
    for annee, ajoutees in ((1995, True), (2024, True), (2025, False)):
        jour = dt.date(annee, 6, 1)
        cotisations = (historique.maladie_independant("commercant", jour, revenu, plafond)
                       + historique.famille_independant(jour, revenu, plafond))
        taux = historique.salaires["csg"].valeur(jour) + historique.salaires["crds"].valeur(jour)
        assiette = revenu + (autres + cotisations if ajoutees else 0.0)
        assert historique.hors_retraite("commercant", jour, revenu, plafond, autres) == (
            pytest.approx(cotisations + taux * assiette)), annee


def test_le_net_d_un_independant_suit_les_prelevements_de_son_annee(simulateur):
    """L'année courante, le net d'un commerçant est celui de sa fiche de paie ;
    en 1985, il perd 11,55 % de maladie et 9 % d'allocations familiales sous le
    plafond, et pas de CSG."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1950, sexe="H", affiliation="commercant", age_debut=21,
        age_liquidation=64, niveau_salaire=1.0)
    nets = cycle_de_vie.revenus_nets(simulateur, carriere)
    bruts = cycle_de_vie.revenus_d_activite(carriere)
    courante = simulateur.parametres.annee_courante
    jeune = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="commercant", age_debut=25,
        age_liquidation=64, niveau_salaire=1.0)
    revenu = cycle_de_vie.revenus_d_activite(jeune)[courante]
    fiche = fiche_depuis_brut(simulateur.parametres.racine_donnees, simulateur.macro,
                              simulateur.catalogue, simulateur.affiliations, "commercant",
                              courante, revenu)
    assert cycle_de_vie.revenus_nets(simulateur, jeune)[courante] == pytest.approx(
        fiche.net, rel=1e-12)
    ligne = next(l for l in carriere.lignes if l.annee == 1985)
    fiche_1985 = fiche_depuis_brut(simulateur.parametres.racine_donnees, simulateur.macro,
                                   simulateur.catalogue, simulateur.affiliations,
                                   "commercant", 1985, ligne.revenu_annualise)
    refaits = sum(l.salarie for l in fiche_1985.lignes if l.code in REFAITS)
    plafond = simulateur.macro.plafond_securite_sociale(1985)
    assert ligne.revenu_annualise < plafond
    attendu = fiche_1985.net + refaits - ligne.revenu_annualise * (0.031 + 0.0845 + 0.09)
    assert nets[1985] == pytest.approx(attendu * ligne.fraction_annee, rel=1e-9)


def test_une_pension_nette_suit_les_prelevements_de_chaque_annee(simulateur):
    """Partie en 2014 : sa pension perd 7,4 % et la maladie des
    complémentaires en 2015, 9,1 % et la même maladie depuis 2018, dernière
    marche tenue au-delà."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1950, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=21,
        age_liquidation=64, niveau_salaire=1.0))
    taux = cycle_de_vie.prelevements_par_annee(simulateur, comparaison)
    courant = cycle_de_vie.taux_de_prelevement(simulateur, comparaison.actuel)
    maladie = courant - 0.091
    assert taux[2015] == pytest.approx(0.066 + 0.005 + 0.003 + maladie)
    assert taux[2040] == pytest.approx(courant)
    convention = cycle_de_vie.convention_nette(simulateur, comparaison)
    assert convention.nette
    assert convention.retenu(2015) == pytest.approx(1.0 - taux[2015])
