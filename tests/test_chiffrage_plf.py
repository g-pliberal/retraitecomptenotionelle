"""Le chiffrage budgétaire : ce que ses tableaux additionnent, et sur quelle base.

``tests/test_prose.py`` tient le document à jour du modèle ; ces tests tiennent
ce que ses lignes veulent dire. Les trois ont une histoire : jusqu'au
23 septembre 2026, le document appelait « solde public » le solde de la seule
retraite, comptait des dépenses de l'État parmi les prélèvements obligatoires,
et cumulait son tableau F sur une autre base de dépense que ses tableaux
annuels.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import chiffrage_plf  # noqa: E402

LIBERAL = chiffrage_plf.LIBERAL


@pytest.fixture(scope="module")
def retro() -> chiffrage_plf.Chiffrage:
    return chiffrage_plf.Chiffrage(False)


def test_les_recettes_retirees_se_decomposent_sans_reste(retro):
    """Cotisations, impôts affectés, versements de l'État et de la branche
    famille : les trois « dont » du fait central font le tout, chaque année.
    Un poste qu'on cesserait de reconduire sans l'y ranger ferait un reste, et
    le tableau cesserait de dire d'où vient l'écart."""
    for annee in retro.annees:
        # La TVA à taux unique n'est pas une recette retirée mais ajoutée : le
        # fait central la met sur sa ligne, hors des trois « dont ».
        total = (retro.recettes(annee) - retro.tva(annee)
                 - retro.solde[annee].ressources_de("actuel"))
        dont = (retro.retire(annee, "cotisations")
                + retro.retire(annee, "impots_et_taxes")
                - retro.retire(annee, "impots_tva")
                + retro.versements_publics_retires(annee))
        assert dont == pytest.approx(total, abs=1e-12), annee
        # Ce que l'État et la branche famille cessent de verser est un retrait,
        # et il est de l'ordre de deux points de PIB.
        assert -0.03 < retro.versements_publics_retires(annee) < -0.015, annee


def test_les_prelevements_ne_comptent_pas_les_depenses_de_l_etat(retro):
    """La contribution d'équilibre de l'État employeur et ses subventions sont
    des dépenses de son budget : le tableau E les montre à part, hors des
    prélèvements, et tout ce que la retraite reçoit se retrouve dans l'une des
    trois colonnes — prélèvements, versements de l'État, et le reste
    (transferts d'autres organismes, produits divers)."""
    for annee in chiffrage_plf.ANNEES_PRELEVEMENTS:
        postes = retro.solde[annee].postes_ressources("actuel")
        assert retro.prelevements_actuels(annee) == pytest.approx(
            postes["cotisations"] + postes["impots_et_taxes"])
        reste = postes["transferts"] + postes["autres_produits"]
        # Au millième de point de PIB : le COR publie ses postes arrondis, et
        # leur somme ne redonne son total qu'à cet arrondi près.
        assert (retro.prelevements_actuels(annee) + retro.versements_etat(annee)
                + reste) == pytest.approx(retro.solde[annee].ressources_de("actuel"),
                                          abs=1e-5)


def test_le_tableau_f_cumule_les_ecarts_des_tableaux_annuels(retro):
    """L'économie cumulée est la somme des écarts annuels que les tableaux A et
    B affichent, en part de PIB, ramenés aux euros constants — la base du COR,
    et non la dépense que le modèle projette lui-même, plus haute de trois
    points de PIB en 2070, qui la surestimait d'environ neuf pour cent."""
    attendu = sum(
        (retro.pensions(annee) - retro.solde[annee].depense("actuel"))
        * retro.avenir[annee].pib * retro.avenir[annee].coefficient_constants
        for annee in retro.annees)
    assert retro.cumul_depense - retro.cumul_depense_actuel == pytest.approx(attendu)
    projetee = sum(retro.avenir[annee].cout_constants(LIBERAL)
                   - retro.avenir[annee].cout_constants("actuel")
                   for annee in retro.annees)
    # Les deux bases ne se confondent pas : si elles se rejoignaient, ce test
    # ne distinguerait plus rien.
    assert abs(projetee / attendu - 1.0) > 0.03
