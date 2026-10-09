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
