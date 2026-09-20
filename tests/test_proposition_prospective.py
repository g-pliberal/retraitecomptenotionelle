"""La proposition prospective : le scénario 5 à 18 %, et rien d'autre ne bouge."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.donnees.assiette import AssietteActivite
from retraite_notionnelle.donnees.depenses import DepensesRetraite
from retraite_notionnelle.donnees.equilibre import ComptesRetraite
from retraite_notionnelle.donnees.population import Population
from retraite_notionnelle.scenarios.notionnel import ScenarioNotionnel
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import proposition_prospective  # noqa: E402

PARAMETRES = Parametres()
RACINE = PARAMETRES.racine_donnees


@pytest.fixture(scope="module")
def donnees():
    return (DepensesRetraite(RACINE), Population(RACINE), ComptesRetraite(RACINE),
            AssietteActivite(RACINE))


@pytest.fixture(scope="module")
def reference(donnees):
    return proposition_prospective.calculer(False, PARAMETRES, *donnees)


@pytest.fixture(scope="module")
def prospective(donnees):
    return proposition_prospective.calculer(True, PARAMETRES, *donnees)


def test_les_cinq_autres_systemes_ne_bougent_pas(reference, prospective):
    for scenario, _ in C.SCENARIOS:
        if scenario == proposition_prospective.LIBERAL:
            continue
        for annee, solde in reference.lectures[scenario].soldes.items():
            assert prospective.lectures[scenario].soldes[annee] == pytest.approx(solde, abs=1e-12)


def test_avant_la_bascule_la_proposition_prospective_est_le_scenario_5(prospective):
    # Le solde se lit paresseusement, et sa règle de réversion regarde
    # ``CLES_PROSPECTIVES`` à la lecture : on relit donc dans le contexte. La
    # tolérance est celle de l'effet de bord de la grille : la cohorte née deux
    # ans avant une génération qui liquide juste après la bascule entre dans la
    # masse deux ans plus tôt, avec un an de compte à 18 % au lieu de 25,83 %.
    solde = prospective.cout.solde
    with proposition_prospective.PropositionProspective():
        for ligne in solde.annees:
            if ligne.annee >= PARAMETRES.annee_bascule:
                continue
            assert ligne.depense(proposition_prospective.LIBERAL) == pytest.approx(
                ligne.depense("notionnel_prospectif_employeur"), rel=1e-3)
            assert ligne.solde(proposition_prospective.LIBERAL) == pytest.approx(
                ligne.solde("notionnel_prospectif_employeur"), abs=1e-4)


def test_le_stock_est_intact_et_les_actifs_recoivent_18_pour_cent(reference, prospective):
    simulateur = Simulateur(PARAMETRES)
    retraite = simulateur.carriere_simple(1950, "H", "salarie_prive_non_cadre", 20.0, 62.0)
    actif = simulateur.carriere_simple(1985, "H", "salarie_prive_non_cadre", 22.0, 64.0)
    with proposition_prospective.PropositionProspective():
        deja = simulateur.simuler(retraite)
        futur = simulateur.simuler(actif)
    liberal = deja.notionnel_liberal
    assert liberal.pension_annuelle - liberal.garantie_vieillesse.complement * (
        1 if liberal.garantie_vieillesse.servie_a_la_liquidation else 0
    ) == pytest.approx(deja.actuel.pension_annuelle)
    # L'actif : des droits acquis figés, puis un compte alimenté à 18 %.
    assert futur.notionnel_liberal.capital_droits_acquis > 0
    assert futur.notionnel_liberal.droits_acquis is not None
    apres = [c for c in futur.notionnel_liberal.compte.cotisations
             if c.annee >= PARAMETRES.annee_bascule and c.cotisation > 0]
    assert apres and all(c.taux_effectif == pytest.approx(PARAMETRES.taux_cotisation_liberal)
                         for c in apres)
    # Et la page le voit : le solde de 2026 paie tout le stock, à 18 %.
    assert (prospective.lectures[proposition_prospective.LIBERAL].soldes[2026]
            < reference.lectures[proposition_prospective.LIBERAL].soldes[2026])


def test_le_contexte_rend_ses_attributs():
    avant = (ScenarioNotionnel.liberal, C.CLES_PROSPECTIVES)
    with proposition_prospective.PropositionProspective():
        assert proposition_prospective.LIBERAL in C.CLES_PROSPECTIVES
        assert ScenarioNotionnel.liberal is not avant[0]
    assert (ScenarioNotionnel.liberal, C.CLES_PROSPECTIVES) == avant
