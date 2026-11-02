"""La proposition prospective : le scénario 5 à 18 %, et rien d'autre ne bouge."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.scenarios.notionnel import ScenarioNotionnel
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import proposition_prospective  # noqa: E402

PARAMETRES = Parametres()


@pytest.fixture(scope="module")
def reference():
    return proposition_prospective.calculer(False, PARAMETRES)


@pytest.fixture(scope="module")
def prospective():
    return proposition_prospective.calculer(True, PARAMETRES)


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
    """Le portage calcule la variante, que la demande au pont lui passe
    (action 161) : ``tests/js/univers.test.js`` en tient le compte, le pilier
    et la garantie ; ici, ce que l'étude en lit, l'écart au système actuel."""
    from retraite_notionnelle import pont

    simulateur = proposition_prospective.simulateur(PARAMETRES)
    profil = {"sexe": "H", "affiliation": "salarie_prive_non_cadre"}
    cas = [{"cle": "retraite", "options": {**profil, "annee_naissance": 1950,
                                           "age_debut": 20.0, "age_liquidation": 62.0}},
           {"cle": "actif", "options": {**profil, "annee_naissance": 1985,
                                        "age_debut": 22.0, "age_liquidation": 65.0}}]
    scenario_5 = "notionnel_prospectif_employeur"
    lus, echecs = pont.carrieres(cas, (proposition_prospective.LIBERAL, scenario_5),
                                 pont.paquet_des_donnees(),
                                 univers=simulateur.univers_de_la_demande)
    assert not echecs
    # Le retraité : sa pension ne bouge pas, comme au scénario 5, et elle est
    # au-dessus du plancher de la garantie.
    for scenario in (proposition_prospective.LIBERAL, scenario_5):
        assert lus["retraite"]["ecarts"][scenario] == pytest.approx(0.0, abs=1e-12), scenario
    # L'actif, parti à l'âge légal de la proposition : les droits figés à la
    # bascule du scénario 5, puis un compte alimenté à 18 % au lieu de 25,83 %.
    assert lus["actif"]["ecarts"][proposition_prospective.LIBERAL] < lus["actif"]["ecarts"][
        scenario_5]
    # Et la page le voit : le solde de 2026 paie tout le stock, à 18 %.
    assert (prospective.lectures[proposition_prospective.LIBERAL].soldes[2026]
            < reference.lectures[proposition_prospective.LIBERAL].soldes[2026])


def test_le_contexte_rend_ses_attributs():
    """Le contexte ne remplace plus que la liste du coût ; le moteur, il le
    laisse intact : la variante est un univers, que le simulateur de l'étude
    calcule à la place du scénario 6 (action 161)."""
    avant = (ScenarioNotionnel.liberal, C.CLES_PROSPECTIVES)
    with proposition_prospective.PropositionProspective():
        assert proposition_prospective.LIBERAL in C.CLES_PROSPECTIVES
        assert ScenarioNotionnel.liberal is avant[0]
    assert (ScenarioNotionnel.liberal, C.CLES_PROSPECTIVES) == avant
    simulateur = proposition_prospective.simulateur(PARAMETRES)
    assert simulateur.univers[proposition_prospective.LIBERAL].id == "notionnel_liberal_prospectif"
    assert Simulateur(PARAMETRES).univers[proposition_prospective.LIBERAL].id == (
        proposition_prospective.LIBERAL)


def test_l_accueil_cite_le_solde_de_la_variante_prospective(prospective):
    """L'accueil l'écarte comme infinançable, chiffre à l'appui : ce chiffre doit
    être celui que le script rend. Il y était écrit −3,9 jusqu'au 23 septembre
    2026, quand le modèle donnait −3,5."""
    from retraite_notionnelle.web.site import disponible, module

    if not disponible():
        pytest.skip("node absent : le site ne se lit pas sans lui")
    MESURES_BLOCAGES = module("pages").MESURES_BLOCAGES

    moyen = prospective.lectures[proposition_prospective.LIBERAL].solde_moyen
    assert round(moyen * 100, 1) == MESURES_BLOCAGES["solde_moyen_prospectif"]

