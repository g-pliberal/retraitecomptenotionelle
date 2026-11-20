"""Le solde sous quatre régimes uniques : ce que le script déplace, et rien d'autre. Le
barème est au moteur, sous ``Parametres.bareme_regime_unique`` (action 161) :
``tests/js/bareme-regime-unique.test.js`` le tient ligne par ligne, ``tests/test_pont.py``
son jumeau ; ici, ce que l'étude en lit, calculé par le portage."""

from __future__ import annotations

import shutil
import re
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle import memoire, pont
from retraite_notionnelle.config import Parametres

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import solde_fusion  # noqa: E402
from facade import Simulateur, compte  # noqa: E402

PARAMETRES = Parametres()


@pytest.fixture(scope="module")
def reference():
    """La page Coût telle qu'elle est : le point de comparaison."""
    return memoire.cout(Parametres())


@pytest.fixture(scope="module")
def hypotheses():
    """Les barèmes du simulateur de la page Coût, sous ses conventions."""
    simulateur = Simulateur(Parametres()).pour_la_projection()
    return simulateur, solde_fusion.hypotheses(simulateur, 2026)


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
    assert compte.taux_du_bareme(bareme, 0.5 * pass_annuel, pass_annuel)[0] == pytest.approx(taux_1)
    assert compte.taux_du_bareme(bareme, 2 * pass_annuel, pass_annuel)[0] == pytest.approx((taux_1 + taux_2) / 2)
    assert compte.taux_du_bareme(bareme, 10 * pass_annuel, pass_annuel)[0] == pytest.approx(
        (taux_1 + 7 * taux_2 + 2 * taux_3) / 10)
    assert compte.taux_du_bareme(bareme, 0.0, pass_annuel) == (0.0, 0.0)


def test_chaque_hypothese_est_un_bareme_du_moteur(hypotheses):
    """Une hypothèse de l'étude est le barème du régime unique que le moteur
    applique (``Parametres.bareme_regime_unique``) : l'étude ne remplace plus
    aucune fonction du moteur le temps d'un calcul. A, le régime unique du
    modèle, n'en pose aucun ; le portage tient les trois autres pour bien
    formés : il bâtit leur simulateur, quand un barème mal formé l'arrête."""
    _, toutes = hypotheses
    assert solde_fusion.parametres_de(toutes["A"], PARAMETRES) == PARAMETRES
    for lettre in "BCD":
        parametres = solde_fusion.parametres_de(toutes[lettre], PARAMETRES)
        assert parametres == replace(PARAMETRES, bareme_regime_unique=toutes[lettre].bareme)
        assert Simulateur(parametres).regime_fusionne is not None
    (haute, taux, _), *suite = toutes["B"].bareme
    mal_forme = replace(PARAMETRES, bareme_regime_unique=((haute, taux, 2 * taux), *suite))
    with pytest.raises(Exception, match="mal formé"):
        Simulateur(mal_forme).regime_fusionne


def test_la_grille_se_simule_par_le_portage(hypotheses):
    """Sous chaque barème, la grille du coût se simule par le portage, le
    barème dans les paramètres de la demande, et rend de chaque couple, avec ce
    que le coût en lit, ce que le compte du scénario 4 prélève et sur quels
    revenus (action 161) : ce que le témoin des valeurs porte (``outils_valeurs``,
    étape 8d). Le simulateur est celui de la façade : la lecture de la grille
    (``RegimeUniqueVariante._pensionnes``) se demande hors du contexte de la
    variante, qui remplace des fonctions du coût, et que la façade, qui ne sert
    que le modèle intact, refuserait. Le prélèvement du régime unique y change
    après la bascule, et non avant."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne calcule pas ici")
    from outils_valeurs import valeur_figee
    from retraite_notionnelle.castypes import GRILLE_DU_COUT

    grille = tuple(cas for cas in GRILLE_DU_COUT
                   if cas.code in ("salaire_moyen", "artisan", "fonctionnaire_sedentaire"))
    _, toutes = hypotheses
    lire = solde_fusion.RegimeUniqueVariante._pensionnes(C._pensionnes)
    lus = {}
    for lettre in "BC":
        simulateur = Simulateur(solde_fusion.parametres_de(toutes[lettre], PARAMETRES))
        lus[lettre] = valeur_figee(f"grille sous l'hypothèse {lettre}",
                                   lire(simulateur, grille, "droit"))
        assert {pensionne.code for pensionne in lus[lettre][0]} == {
            cas.code for cas in grille}, lettre
    bascule = PARAMETRES.annee_bascule
    for b, c in zip(lus["B"][0], lus["C"][0], strict=True):
        assert b.cotisations[solde_fusion.REVENU] == c.cotisations[solde_fusion.REVENU]
        fusion_b, fusion_c = b.cotisations[solde_fusion.FUSION], c.cotisations[solde_fusion.FUSION]
        assert ({a: v for a, v in fusion_b.items() if a < bascule}
                == {a: v for a, v in fusion_c.items() if a < bascule})
        apres = [a for a in fusion_b if a >= bascule and fusion_b[a] > 0.0]
        # Les générations nées de 1965 à 2000 cotisent après la bascule.
        assert apres or not 1965 <= b.generation <= 2000, (b.code, b.generation)
        assert all(fusion_b[a] != fusion_c[a] for a in apres), (b.code, b.generation)


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
    comparaison, et aux deux recettes hors du travail de la proposition près —
    la part de TVA gardée et le point de taxe sur la valeur du terrain : le
    scénario 6 y perd exactement ce qu'elles apportaient à son régime."""
    for convention in solde_fusion.CONVENTIONS:
        lectures = resultat_a.lectures[convention]
        for scenario in ("actuel", "notionnel_liberal"):
            for ligne in reference.solde.projetees():
                assert lectures[scenario].soldes[ligne.annee] == pytest.approx(
                    ligne.solde(scenario) - ligne.tva_de(scenario)
                    - ligne.recettes_affectees_de(scenario), abs=1e-12), (
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
             C.SoldeAnnuel._tva_affectee, C.SoldeAnnuel.recettes_affectees_de)
    with solde_fusion.RegimeUniqueVariante(toutes["C"]):
        assert C.CLES_RECETTES != avant[1]
        assert C._pensionnes is not avant[2]
        # La TVA à taux unique n'est pas un taux de cotisation : les variantes
        # la laissent hors de la comparaison, comme la part de TVA gardée et
        # le point de taxe sur la valeur du terrain.
        assert C.SoldeAnnuel._tva_affectee is not avant[5]
        assert C.SoldeAnnuel.recettes_affectees_de is not avant[6]
    assert (C._simulations, C.CLES_RECETTES, C._pensionnes,
            C._rapports_recettes, C.SoldeAnnuel.ressources_de,
            C.SoldeAnnuel._tva_affectee, C.SoldeAnnuel.recettes_affectees_de) == avant


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


def test_l_accueil_cite_les_deux_recettes_hors_du_travail(reference):
    """La part de TVA gardée et le point de taxe sur la valeur du terrain
    (décisions 79 à 81 du programme), en moyenne sur 2026-2070 : 0,34 et 1,31
    point de PIB, 1,6 ensemble. L'accueil les nomme, et dit le solde et les
    réserves qu'elles laissent, non plus un besoin et une dette."""
    from retraite_notionnelle.web.site import disponible, module, rendre

    if not disponible():
        pytest.skip("node absent : le site ne se lit pas sans lui")
    m = module("pages").MESURES_BLOCAGES
    annees = [ligne for ligne in reference.solde.annees if 2026 <= ligne.annee <= C.HORIZON]
    moyenne = sum(ligne.recettes_affectees_de("notionnel_liberal")
                  for ligne in annees) / len(annees)
    assert round(moyenne * 100, 1) == m["recettes_hors_travail"] == 1.6
    corps = rendre("/", {})[1]
    assert "un point de taxe sur la valeur du terrain" in corps
    assert "la part de TVA qui va déjà aux retraites" in corps
    assert "1,6 point de PIB par an" in corps
    # Un excédent et des réserves, quand la mesure les donne.
    assert m["solde_moyen_proposition"] > 0 and m["dette_2070_proposition"] < 0
    # L'excédent est celui que la mesure donne : 0,2 point jusqu'au 20 novembre
    # 2026, 0,3 depuis que le libéral type du coût est à 1,5 fois le salaire
    # moyen (action 191), que la fabrique récrit dans la mesure.
    excedent = str(m["solde_moyen_proposition"]).replace(".", ",")
    assert f"un excédent de {excedent} point par an" in corps
    # L'espace avant « % » est insécable sur la page. Les réserves sont celles
    # que la mesure donne : 6 % du PIB jusqu'au 15 novembre 2026, 7 % depuis
    # que l'exploitant agricole a la porte des vingt ans de la carrière longue
    # (action 192, étape 2), que la fabrique récrit dans la mesure.
    assert re.search(rf"des réserves de {-m['dette_2070_proposition']}\s% du PIB", corps)
    assert "la dette qu'elle accumule" not in corps

