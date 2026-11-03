"""Le solde sous quatre régimes uniques : ce que le script déplace, et rien d'autre. Le
barème est au moteur, sous ``Parametres.bareme_regime_unique`` (action 161) :
``tests/js/bareme-regime-unique.test.js`` le tient ligne par ligne, ``tests/test_pont.py``
son jumeau ; ici, ce que l'étude en lit, calculé par le portage."""

from __future__ import annotations

import shutil
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle import memoire, pont
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.moteur.compte import ConstructeurCompte, taux_du_bareme
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import solde_fusion  # noqa: E402

PARAMETRES = Parametres()


@pytest.fixture(scope="module")
def reference():
    """La page Coût telle qu'elle est : le point de comparaison."""
    return memoire.cout(Parametres())


@pytest.fixture(scope="module")
def hypotheses():
    """Les barèmes du simulateur de la page Coût, sous ses conventions."""
    simulateur = Simulateur(Parametres()).pour_la_projection()
    return simulateur, solde_fusion.hypotheses(simulateur.catalogue, 2026)


@pytest.fixture(scope="module")
def resultat_a(hypotheses):
    _, toutes = hypotheses
    return solde_fusion.calculer(toutes["A"], Parametres())


def test_le_bareme_par_tranches_se_lit_tranche_par_tranche(hypotheses):
    """Le barème B, tel que le moteur le lit (``taux_du_bareme``, le jumeau de
    ``tauxDuBareme``)."""
    _, toutes = hypotheses
    bareme = toutes["B"].bareme
    (_, taux_1, _), (_, taux_2, _), (_, taux_3, _) = bareme
    pass_annuel = 47_100.0
    assert taux_du_bareme(bareme, 0.5 * pass_annuel, pass_annuel)[0] == pytest.approx(taux_1)
    assert taux_du_bareme(bareme, 2 * pass_annuel, pass_annuel)[0] == pytest.approx((taux_1 + taux_2) / 2)
    assert taux_du_bareme(bareme, 10 * pass_annuel, pass_annuel)[0] == pytest.approx(
        (taux_1 + 7 * taux_2 + 2 * taux_3) / 10)
    assert taux_du_bareme(bareme, 0.0, pass_annuel) == (0.0, 0.0)


def test_chaque_hypothese_est_un_bareme_du_moteur(hypotheses):
    """Une hypothèse de l'étude est le barème du régime unique que le moteur
    applique (``Parametres.bareme_regime_unique``) : l'étude ne remplace plus
    aucune fonction du moteur le temps d'un calcul. A, le régime unique du
    modèle, n'en pose aucun ; le moteur tient les trois autres pour bien
    formés."""
    _, toutes = hypotheses
    assert solde_fusion.parametres_de(toutes["A"], PARAMETRES) == PARAMETRES
    for lettre in "BCD":
        parametres = solde_fusion.parametres_de(toutes[lettre], PARAMETRES)
        assert parametres == replace(PARAMETRES, bareme_regime_unique=toutes[lettre].bareme)
        assert Simulateur(parametres).constructeur.parametres.bareme_regime_unique is not None
    taux_unifie = ConstructeurCompte.taux_unifie
    with solde_fusion.RegimeUniqueVariante(toutes["C"]):
        assert ConstructeurCompte.taux_unifie is taux_unifie


def test_la_grille_se_simule_par_le_portage_au_bit_pres_du_jumeau(hypotheses, monkeypatch):
    """Sous chaque barème, la grille du coût se simule par le portage, le
    barème dans les paramètres de la demande, et rend de chaque couple, avec ce
    que le coût en lit, ce que le compte du scénario 4 prélève et sur quels
    revenus (action 161) : au bit près de ce que le jumeau Python en simule
    sous le même barème et ``pont.par_le_jumeau()`` — sans que le moteur
    Python ne calcule rien. Le prélèvement du régime unique y change après la
    bascule, et non avant."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne calcule pas ici")
    from outils_pont import empecher_les_jumeaux_du_cout
    from retraite_notionnelle.castypes import GRILLE_DU_COUT

    monkeypatch.setattr(C, "generations", lambda: (1965, 2000))
    grille = tuple(cas for cas in GRILLE_DU_COUT
                   if cas.code in ("salaire_moyen", "artisan", "fonctionnaire_sedentaire"))
    _, toutes = hypotheses
    lus = {}
    for lettre in "BC":
        simulateur = Simulateur(solde_fusion.parametres_de(toutes[lettre], PARAMETRES))
        with solde_fusion.RegimeUniqueVariante(toutes[lettre]):
            with pont.par_le_jumeau():
                lus[f"{lettre}, jumeau"] = C._pensionnes(simulateur, grille, "droit")
    empecher_les_jumeaux_du_cout(monkeypatch)
    for lettre in "BC":
        simulateur = Simulateur(solde_fusion.parametres_de(toutes[lettre], PARAMETRES))
        with solde_fusion.RegimeUniqueVariante(toutes[lettre]):
            lus[lettre] = C._pensionnes(simulateur, grille, "droit")
        assert lus[lettre] == lus[f"{lettre}, jumeau"], lettre
        assert len(lus[lettre][0]) == len(grille) * 2, lettre
    bascule = PARAMETRES.annee_bascule
    for b, c in zip(lus["B"][0], lus["C"][0], strict=True):
        assert b.cotisations[solde_fusion.REVENU] == c.cotisations[solde_fusion.REVENU]
        fusion_b, fusion_c = b.cotisations[solde_fusion.FUSION], c.cotisations[solde_fusion.FUSION]
        assert ({a: v for a, v in fusion_b.items() if a < bascule}
                == {a: v for a, v in fusion_c.items() if a < bascule})
        assert any(fusion_b[a] != fusion_c[a] for a in fusion_b if a >= bascule), b.code


def test_les_quatre_hypotheses_se_rangent_par_taux(hypotheses):
    simulateur, toutes = hypotheses
    b, c, d = (toutes[l].taux_affiche for l in "BCD")
    assert b == pytest.approx(simulateur.regime_fusionne.taux_cotisation_retraite)
    assert b > c > d > 0.0


def test_sous_a_le_taux_effectif_est_celui_du_regime_unique(resultat_a, hypotheses, reference):
    simulateur, _ = hypotheses
    assert resultat_a.taux_effectif == pytest.approx(
        simulateur.regime_fusionne.taux_cotisation_retraite, abs=1e-9)
    assert 0.0 < resultat_a.rapport_recette < 1.0
    assert resultat_a.echecs == reference.echecs


def test_les_scenarios_1_et_6_ne_bougent_pas(resultat_a, reference):
    """À la TVA à taux unique près, que les variantes tiennent hors de la
    comparaison : le scénario 6 y perd exactement ce qu'elle apportait à son
    régime."""
    for convention in solde_fusion.CONVENTIONS:
        lectures = resultat_a.lectures[convention]
        for scenario in ("actuel", "notionnel_liberal"):
            for ligne in reference.solde.projetees():
                assert lectures[scenario].soldes[ligne.annee] == pytest.approx(
                    ligne.solde(scenario) - ligne.tva_de(scenario), abs=1e-12), (
                    convention, scenario, ligne.annee)


def test_avant_la_bascule_rien_ne_change(resultat_a, reference):
    for ligne in reference.solde.annees:
        if ligne.annee >= 2026:
            continue
        variante = resultat_a.cout.solde.annee(ligne.annee)
        for scenario, _ in C.SCENARIOS:
            assert variante.solde(scenario) == pytest.approx(ligne.solde(scenario), abs=1e-12)


def test_la_recette_suit_la_regle_du_programme(resultat_a, reference):
    """Sous « assiette », la recette d'un scénario 2 à 5 est celle du scénario 6
    à son taux près : taux × assiette, plus les autres produits, moins ce que
    la CNAF et le fonds de solidarité vieillesse versent pour des droits qu'il
    ne sert plus."""
    ligne = reference.solde.annee(2030)
    attendu = (ligne.ressources * resultat_a.taux_effectif / ligne.taux_prelevement
               + ligne.ressources * (1.0 - ligne.part_contributive
                                     - ligne.part_subventions - ligne.part_impots)
               - (ligne.retrait - ligne.retrait_par_impot))
    lecture = resultat_a.lectures[C.CONVENTION_ASSIETTE]["notionnel_prospectif_employeur"]
    assert lecture.ressources[2030] == pytest.approx(attendu, abs=1e-12)
    # Sous « rapport », les impôts affectés restent : la recette est plus haute.
    rapport = resultat_a.lectures[C.CONVENTION_RAPPORT]["notionnel_prospectif_employeur"]
    assert rapport.ressources[2030] > lecture.ressources[2030]
    # Et elle ne vaut plus les ressources du système actuel, comme sur la page.
    assert lecture.ressources[2030] < ligne.ressources


def test_le_contexte_rend_ses_attributs(hypotheses):
    """Le contexte ne remplace que des fonctions du coût, et les rend."""
    _, toutes = hypotheses
    avant = (C._simulations, C.CLES_RECETTES, C._pensionnes,
             C._rapports_recettes, C.SoldeAnnuel.ressources_de,
             C.SoldeAnnuel._tva_affectee)
    with solde_fusion.RegimeUniqueVariante(toutes["C"]):
        assert C.CLES_RECETTES != avant[1]
        assert C._pensionnes is not avant[2]
        # La TVA à taux unique n'est pas un taux de cotisation : les variantes
        # la laissent hors de la comparaison.
        assert C.SoldeAnnuel._tva_affectee is not avant[5]
    assert (C._simulations, C.CLES_RECETTES, C._pensionnes,
            C._rapports_recettes, C.SoldeAnnuel.ressources_de,
            C.SoldeAnnuel._tva_affectee) == avant


# -- ce que l'accueil cite --------------------------------------------------


@pytest.fixture(scope="module")
def resultats_c_d(hypotheses):
    _, toutes = hypotheses
    return {nom: solde_fusion.calculer(toutes[nom], Parametres(),
                                       conventions=(C.CONVENTION_ASSIETTE,))
            for nom in ("C", "D")}


def test_l_accueil_cite_le_taux_du_regime_unique_et_le_cout_des_18_pour_cent(resultat_a):
    """Les points de blocage de l'accueil citent deux mesures de ce script ; elles
    doivent être celles qu'il rend, à la précision où la page les écrit. Le
    dépôt les écrivait dans le texte jusqu'au 23 septembre 2026, et le coût des
    18 % y était resté à 2,3 points quand le modèle en donnait 2,4."""
    from retraite_notionnelle.web.site import disponible, module

    if not disponible():
        pytest.skip("node absent : le site ne se lit pas sans lui")
    MESURES_BLOCAGES = module("pages").MESURES_BLOCAGES

    assert round(resultat_a.taux_effectif * 100, 1) == MESURES_BLOCAGES["taux_regime_unique"]
    lectures = resultat_a.lectures[C.CONVENTION_ASSIETTE]
    cout = (lectures["notionnel_retroactif_employeur"].solde_moyen
            - lectures["notionnel_liberal"].solde_moyen) * 100
    assert round(cout, 1) == MESURES_BLOCAGES["cout_18_pour_cent"]


def test_sous_les_deux_derniers_baremes_le_deficit_depasse_cinq_points(resultats_c_d):
    """« Sous les deux derniers barèmes le déficit dépasse cinq points de PIB
    par an de 2030 à 2040 » : celui du compte notionnel au taux du régime
    unique, part patronale comprise, stock intact — le scénario 5."""
    for nom, resultat in resultats_c_d.items():
        soldes = resultat.lectures[C.CONVENTION_ASSIETTE]["notionnel_prospectif_employeur"].soldes
        for annee in (2030, 2040):
            assert soldes[annee] < -0.05, (nom, annee, soldes[annee])


def test_l_accueil_cite_le_solde_la_dette_et_le_coefficient_du_cout_par_defaut(reference):
    """Le solde moyen de la proposition et du système actuel, leur dette en
    2070 et le coefficient d'équilibre : les mêmes sondes que le README, à la
    précision de l'accueil. Celui-ci écrivait −1,5, 103 % et 0,92 quand le
    modèle donnait −1,4, 97 % et 1,00."""
    from retraite_notionnelle.web.site import disponible, module

    if not disponible():
        pytest.skip("node absent : le site ne se lit pas sans lui")
    m = module("pages").MESURES_BLOCAGES

    solde, dette = reference.solde, reference.dette
    assert round(solde.solde_moyen("notionnel_liberal", 2026, C.HORIZON) * 100, 1) \
        == m["solde_moyen_proposition"]
    assert round(solde.solde_moyen("actuel", 2026, C.HORIZON) * 100, 1) \
        == m["solde_moyen_actuel"]
    assert round(dette.horizon("notionnel_liberal") * 100) == m["dette_2070_proposition"]
    assert round(dette.horizon("actuel") * 100) == m["dette_2070_actuel"]
    projetees = solde.projetees()
    plus_bas = min(projetees, key=lambda l: l.coefficient("notionnel_liberal"))
    assert round(plus_bas.coefficient("notionnel_liberal"), 2) == m["coefficient_minimum"]
    # La décennie, et non l'année : le creux est plat, 0,80 deux ans de suite,
    # et l'année exacte basculerait au moindre arrondi.
    assert plus_bas.annee // 10 * 10 == m["decennie_coefficient_minimum"]
    assert round(solde.annee(C.HORIZON).coefficient("notionnel_liberal"), 2) \
        == m["coefficient_2070"]

