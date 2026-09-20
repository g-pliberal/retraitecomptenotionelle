"""Les trois postes écartés, reconduits un par un : l'arithmétique doit tenir.

Ce script ne touche à aucun moteur : il recompose ``ressources_de`` terme à
terme. Le premier test est donc le seul qui compte vraiment — si la référence
du script ne redonne pas le solde de la page à l'exact, tous ses chiffrages
sont faux d'autant, et silencieusement.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle.config import Parametres

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import postes_ecartes  # noqa: E402

LIBERAL = postes_ecartes.LIBERAL


@pytest.fixture(scope="module")
def calcul():
    return postes_ecartes.calculer(Parametres())


@pytest.fixture(scope="module")
def chiffrages(calcul):
    return {chiffrage.cle: chiffrage for chiffrage in calcul[1]}


def test_la_reference_redonne_exactement_le_solde_de_la_page(calcul, chiffrages):
    """Aucun poste reconduit : le script doit retrouver la page à l'exact.

    C'est l'ancrage de tout le reste. Une référence qui dériverait d'un
    millième ferait un écart de un pour mille sur chaque chiffrage, et rien
    ne le dirait.
    """
    solde = calcul[0].solde
    reference = chiffrages["reference"]
    assert reference.postes == ()
    for ligne in solde.projetees():
        if ligne.annee > C.HORIZON:
            continue
        assert reference.soldes[ligne.annee] == pytest.approx(
            ligne.solde(LIBERAL), abs=1e-15), ligne.annee
    assert reference.solde_moyen == pytest.approx(
        solde.solde_moyen(LIBERAL, 2026, C.HORIZON), abs=1e-15)


def test_reconduire_un_poste_ne_peut_qu_ameliorer_le_solde(chiffrages):
    """Une recette rendue est une recette de plus : le sens ne se discute pas."""
    reference = chiffrages["reference"]
    for poste, _ in postes_ecartes.POSTES:
        chiffrage = chiffrages[poste]
        for annee, valeur in chiffrage.soldes.items():
            assert valeur > reference.soldes[annee], (poste, annee)


def test_la_depense_ne_bouge_dans_aucun_chiffrage(calcul, chiffrages):
    """Seule la recette change. Un chiffrage qui bougerait la dépense dirait
    que la proposition coûte moins, ce qui serait faux et flatteur."""
    solde = calcul[0].solde
    for chiffrage in chiffrages.values():
        for annee, ressources in chiffrage.ressources.items():
            depense = solde.annee(annee).depense(LIBERAL)
            assert (ressources - depense) == pytest.approx(
                chiffrage.soldes[annee], abs=1e-15), (chiffrage.cle, annee)
            assert depense == pytest.approx(
                solde.annee(annee).depense(LIBERAL), abs=1e-15)


def test_les_trois_postes_ensemble_font_la_somme_des_trois(chiffrages):
    """Les postes ne se recouvrent pas : leurs gains s'additionnent."""
    reference = chiffrages["reference"]
    tous = chiffrages["tous"]
    for annee, valeur in tous.soldes.items():
        gains = sum(chiffrages[poste].soldes[annee] - reference.soldes[annee]
                    for poste, _ in postes_ecartes.POSTES)
        assert valeur == pytest.approx(reference.soldes[annee] + gains, abs=1e-15), annee


def test_le_poste_des_impots_se_lit_net_de_la_csg_du_fonds(calcul):
    """Brut moins net vaut exactement ce que le fonds verse par l'impôt.

    C'est la seule subtilité du calcul, et celle qui retourne la conclusion :
    contre le poste publié la proposition demande moins que ce que le système
    actuel y met, contre le poste net elle demande plus.
    """
    solde = calcul[0].solde
    for ligne in solde.projetees():
        brut = postes_ecartes.montant_brut(ligne, postes_ecartes.POSTE_IMPOTS)
        net = postes_ecartes.montant(ligne, postes_ecartes.POSTE_IMPOTS)
        assert brut - net == pytest.approx(ligne.retrait_par_impot, abs=1e-15)
        assert net > 0.0
    # Les deux autres postes n'ont pas ce double compte.
    for poste in (postes_ecartes.POSTE_CONTRIBUTION, postes_ecartes.POSTE_SUBVENTIONS):
        for ligne in solde.projetees():
            assert (postes_ecartes.montant_brut(ligne, poste)
                    == postes_ecartes.montant(ligne, poste))


def test_le_besoin_est_le_deficit_rapporte_au_poste(calcul):
    """La part demandée une année est le manque divisé par ce qui est disponible."""
    cout, _, besoins = calcul
    solde = cout.solde
    for besoin in besoins:
        mesure = (postes_ecartes.montant_brut if besoin.brut
                  else postes_ecartes.montant)
        for annee, part in besoin.parts.items():
            ligne = solde.annee(annee)
            manque = -(ligne.ressources_de(LIBERAL) - ligne.depense(LIBERAL))
            assert part == pytest.approx(
                manque / mesure(ligne, besoin.poste), abs=1e-12), (besoin.poste, annee)
        assert besoin.part_critique == max(besoin.parts.values())
        assert besoin.suffit_toujours == (besoin.part_critique <= 1.0)


def test_un_poste_inconnu_est_refuse():
    """Le script nomme ses trois postes et refuse le reste, plutôt que de
    rendre zéro — un zéro silencieux ferait un chiffrage qui ne chiffre rien."""
    class Fausse:
        ressources = 1.0
        part_impots = 0.1
        part_subventions = 0.1
        parts = {"contribution_equilibre_etat": 0.1}
        retrait_par_impot = 0.01

    with pytest.raises(ValueError, match="poste inconnu"):
        postes_ecartes.montant(Fausse(), "produits_financiers")


def test_le_tableau_dit_le_verdict_des_deux_lectures_des_impots(calcul):
    """La sortie doit porter les deux réponses, pas seulement la plus flatteuse."""
    texte = postes_ecartes.tableau(*calcul)
    assert "poste publié" in texte
    assert "MOINS que ce que le système actuel y met" in texte
    assert "PLUS que ce que le système actuel y met" in texte
    # La garantie est imprimée : c'est elle qui explique à quoi la CSG du
    # fonds de solidarité est déjà promise.
    assert "Garantie vieillesse" in texte
