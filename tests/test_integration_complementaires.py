"""Les complémentaires sous les décisions 36 à 48 : chaque caisse projetée
jusqu'à l'épuisement de ses réserves, qui est l'année de son intégration.

Action 186, chantier 6, étape 1
(``docs/feuille_de_route/186/2026-11-07-complementaires-au-modele.md``), et
étape 1 bis, la baisse des pensions avant l'intégration
(``…/2026-11-07-complementaires-baisse-avant-integration.md``) : ici, sans la
baisse (``baisses={}``) ou sous une baisse posée à la main ; celle que le
modèle calcule, dans ``test_integration_complementaires_baisse.py``. Les
valeurs attendues viennent des sources — le tableau 2.3 du rapport du COR de
juin 2026, les assiettes du Chiffr'Agirc-Arrco 2026, les fiches du COR de
juin 2024 — ou d'un calcul posé à la main, écrit dans le test.
"""
from __future__ import annotations

import csv
from collections import defaultdict

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle import integration_complementaires as ic

REGIMES = RACINE_DONNEES / "reference" / "regimes"


def _lignes(chemin):
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


# --- Les données ---------------------------------------------------------


def test_les_reserves_de_fin_2025_somment_aux_totaux_du_cor():
    """Tableau 2.3 du rapport du COR de juin 2026 (p. 100) : 5,3 Md€ aux
    régimes de base, 15,7 aux régimes spéciaux, 202,9 aux complémentaires,
    223,9 en tout — le total que ``reserves_retraite.csv`` porte déjà."""
    sommes = defaultdict(float)
    for ligne in _lignes(REGIMES / "reserves_regimes.csv"):
        if ligne["poste"] == "reserves":
            sommes[ligne["groupe"]] += float(ligne["montant_md"])
    assert sommes["base"] == pytest.approx(5.3, abs=1e-9)
    assert sommes["speciaux"] == pytest.approx(15.7, abs=1e-9)
    assert sommes["complementaires"] == pytest.approx(202.9, abs=1e-9)
    total = [float(l["montant"]) for l in _lignes(RACINE_DONNEES / "reference" / "macro"
                                                   / "reserves_retraite.csv")
             if l["annee"] == "2025" and l["poste"] == "reserves_regimes"]
    assert sum(sommes.values()) == pytest.approx(total[0], abs=1e-9) == 223.9


def test_les_assiettes_de_l_agirc_arrco_somment_a_leur_total():
    """Chiffr'Agirc-Arrco 2026, p. 46 : tranche 1 et tranche 2 font le total
    publié, au million d'euros près, chaque année de 2018 à 2024, avec et sans
    les IEG."""
    valeurs = {(l["annee"], l["perimetre"], l["poste"]): float(l["valeur"])
               for l in _lignes(REGIMES / "assiettes_agirc_arrco.csv")}
    paires = {(annee, perimetre) for annee, perimetre, poste in valeurs if poste == "total"}
    assert len(paires) == 14
    for annee, perimetre in paires:
        assert (valeurs[(annee, perimetre, "tranche_1")]
                + valeurs[(annee, perimetre, "tranche_2")]
                == pytest.approx(valeurs[(annee, perimetre, "total")], abs=1.0))
    assert valeurs[("2024", "ieg_compris", "total")] == 756_138


def test_les_comptes_des_complementaires_bouclent():
    """Le classeur du COR de juin 2024 : le solde élargi est la différence des
    ressources et des dépenses, chaque année, pour chaque caisse."""
    comptes = defaultdict(dict)
    for ligne in _lignes(REGIMES / "comptes_complementaires.csv"):
        comptes[(ligne["regime"], int(ligne["annee"]))][ligne["poste"]] = float(ligne["part_pib"])
    assert {regime for regime, _ in comptes} == set(ic.CAISSES_DU_COR)
    for (regime, annee), postes in comptes.items():
        assert postes["ressources"] - postes["depenses"] == pytest.approx(
            postes["solde_elargi"], abs=2e-8), (regime, annee)


def test_les_reserves_de_la_cnbf_s_epuisent_en_2047_chez_le_cor():
    """Fiche CNBF du COR, juin 2024 : « les réserves seraient épuisées en
    2047 » ; celles de l'Ircantec « un peu après 2050 »."""
    reserves = {(l["regime"], int(l["annee"])): float(l["part_pib"])
                for l in _lignes(REGIMES / "comptes_complementaires.csv")
                if l["poste"] == "reserves"}
    assert reserves[("cnbf", 2046)] > 0 and reserves[("cnbf", 2047)] == 0
    assert reserves[("ircantec", 2050)] > 0
    assert min(a for (r, a), v in reserves.items() if r == "ircantec" and v == 0) in range(2051, 2056)


def test_le_facteur_de_la_regle_du_cor_reste_un_rendement():
    """La règle du classeur du COR : les réserves de l'année sont celles de la
    précédente, multipliées par un facteur — un à partir de 2028, 1,5 à 3 % à
    l'Ircantec —, plus le solde élargi. Près de l'épuisement, le classeur s'en
    écarte : à la main, les réserves de la CNBF font 0,688 Md€ fin 2043 et son
    solde − 0,485 Md€ en 2044, soit 0,203 Md€ fin 2044, quand le classeur en
    écrit 0,411 ; le facteur en sortirait à 1,30, puis 1,97 et 2,60, et
    multiplierait d'autant l'écart que les décisions creusent. Un facteur
    au-delà du rendement maximal n'est pas un rendement : il vaut un."""
    comptes = ic._comptes(RACINE_DONNEES)
    for caisse in ic.CAISSES:
        _, facteurs = ic._trajectoire_du_cor(comptes, caisse.cor)
        assert max(facteurs.values()) <= 1.0 + ic.RENDEMENT_MAXIMAL, caisse.cor
    _, facteurs = ic._trajectoire_du_cor(comptes, "cnbf")
    assert [facteurs[a] for a in (2043, 2044, 2045, 2046)] == [1.0, 1.0, 1.0, 1.0]


# --- Ce que la décision 36 retire à l'Agirc-Arrco -------------------------


def test_la_ceg_et_la_cet_rapportent_pres_de_18_md_en_2024():
    """À la main, sur les assiettes de 2024 (IEG compris) : CEG 2,15 % de
    636 259 M€ et 2,70 % de 119 878 M€, 13 680 + 3 237 M€ ; CET 0,35 % des
    tranches 1 et 2 des 23,7 % de salariés au-dessus du plafond — 119 878 M€
    de tranche 2 et 0,237 × (756 138 M€ ÷ 41 878 €) × 46 368 €, soit
    198 419 M€ de tranche 1 —, 1 114 M€ ; en tout 18 030 M€, sur 93 986 M€
    prélevés (75 955 M€ de cotisations, 7,87 % et 21,59 %) : 19,18 %."""
    pertes = ic.contributions_supprimees_agirc_arrco(RACINE_DONNEES)
    assert pertes.ceg_meur == pytest.approx(16_916, abs=2)
    assert pertes.cet_meur == pytest.approx(1_114, abs=2)
    assert pertes.cotisations_meur == pytest.approx(75_955, abs=2)
    assert pertes.part == pytest.approx(18_030 / 93_986, abs=1e-4)


# --- La projection --------------------------------------------------------


@pytest.fixture(scope="module")
def projections():
    """Sans la baisse des pensions avant l'intégration : les années les plus
    précoces que les décisions 36 à 48 permettent."""
    return ic.projeter_les_caisses(RACINE_DONNEES, baisses={})


def test_la_complementaire_agricole_privee_des_droits_sur_les_alcools_rejoint_en_2026(projections):
    """0,4 Md€ de réserves fin 2025 (COR 2026, tableau 2.3) ; en 2026, le COR
    lui prête 0,038 % du PIB de ressources, dont la moitié d'impôts affectés
    (48 % en 2023, 53 % en 2030) : à peu près 0,020 % du PIB, 0,6 Md€, perdus
    dès la première année (décision 12)."""
    assert projections["msa_exploitants_complementaire"].annee_integration == 2026


def test_l_agirc_arrco_sans_ceg_ni_cet_rejoint_en_2032(projections):
    """À la main, en part de PIB : 113,6 Md€ fin 2025 sur 2 991 Md€ de PIB,
    3,80 % ; la CEG et la CET coûtent 19,18 % de ses cotisations, de sa
    compensation et des transferts de l'Unédic et du FSV, 0,63 % du PIB par an ;
    le COR lui donne un solde de − 0,02 % en 2026, + 0,07 % en 2030, et un
    rendement de 3 % sur ses réserves. Fin 2026, 3,22 % ; 2027, 2,62 % ;
    2028, 2,00 % ; 2029, 1,39 % ; 2030, 0,78 % ; 2031, 0,15 % ; 2032,
    sous zéro."""
    agirc_arrco = projections["agirc_arrco"]
    assert agirc_arrco.annee_integration == 2032
    assert agirc_arrco.reserves[2026] == pytest.approx(0.0322, abs=0.0005)
    assert agirc_arrco.reserves[2030] == pytest.approx(0.0078, abs=0.0010)


def test_ses_seules_reserves_techniques_l_integreraient_plus_tot(projections):
    """92,1 Md€ de réserves techniques, le fonds de roulement mis à part (COR
    2026, note du tableau 2.3) : 21,5 Md€ de moins, plus d'un an de pertes."""
    techniques = ic.projeter_les_caisses(RACINE_DONNEES, reserves_techniques=True,
                                         baisses={})
    assert (techniques["agirc_arrco"].annee_integration
            < projections["agirc_arrco"].annee_integration)


def test_l_ircantec_rejoint_peu_apres_2050_comme_chez_le_cor(projections):
    """Rien ne lui est retiré : elle suit le COR, qui épuise ses réserves
    « un peu après 2050 » ; ses 19,2 Md€ de fin 2025 dépassent un peu ce que
    le COR lui prêtait (0,61 % du PIB, quand 19,2 Md€ en font 0,64 %)."""
    assert projections["ircantec"].annee_integration in range(2051, 2056)


def test_les_independants_les_liberaux_et_les_navigants_tiennent_jusqu_en_2070(projections):
    """Fiches du COR de juin 2024 : réserves du RCI qui s'éteignent « au-delà
    de 2070 », libéraux excédentaires après 2040, navigants à 0,5 % du PIB en
    2070 ; rien ne leur est retiré."""
    for caisse in ("rci_complementaire", "cnavpl_complementaire", "crpnpac"):
        assert projections[caisse].annee_integration is None, caisse


def test_l_ordre_d_integration(projections):
    """La complémentaire agricole, puis l'Agirc-Arrco, que les décisions
    privent de leurs recettes ; puis, comme chez le COR, la CNBF (réserves
    « épuisées en 2047 ») avant l'Ircantec (« un peu après 2050 »)."""
    ordre = ic.ordre_d_integration(projections)
    assert [caisse for caisse, _ in ordre[:4]] == [
        "msa_exploitants_complementaire", "agirc_arrco", "cnbf_complementaire", "ircantec"]
    annees = [annee for _, annee in ordre if annee is not None]
    assert annees == sorted(annees)


def test_garder_les_droits_sur_les_alcools_sauverait_la_complementaire_agricole():
    """L'autre lecture de la décision 48 (« une complémentaire ne perd que la
    CEG et la CET ») : la caisse garde son impôt, et le COR la projette
    excédentaire jusqu'en 2070 (0,49 % du PIB de réserves)."""
    projections = ic.projeter_les_caisses(RACINE_DONNEES, impots_affectes_gardes=True,
                                          baisses={})
    assert projections["msa_exploitants_complementaire"].annee_integration is None


# --- La baisse des pensions avant l'intégration (étape 1 bis) ---------------


def _baisse_posee(taux):
    """Une baisse posée à la main : ``taux`` des pensions servies à la bascule,
    qui font toute la dépense de la caisse jusqu'en 2070."""
    return ic.BaisseDuStock(taux=taux, part_du_stock={a: 1.0 for a in range(2026, ic.FIN + 1)})


def test_la_baisse_se_fait_par_cinquiemes_et_n_aide_la_complementaire_agricole_qu_un_peu():
    """À la main, en 2026, sur le compte du COR de juin 2024 et ses 0,4 Md€ de
    réserves de fin 2025 (2 991 Md€ de PIB) : 0,03760 % du PIB de ressources,
    1,125 Md€, dont 50,1 % d'impôts affectés (48 % en 2023, 53 % en 2030,
    interpolés), 0,564 Md€, perdus (décision 67) ; 0,03629 % de dépenses,
    1,085 Md€. Sans baisse : 0,4 + 1,125 − 0,564 − 1,085 = − 0,124 Md€.
    Ses pensions baissées de 40 % par cinquièmes (décisions 2 et 3), 2026 n'en
    voit qu'un cinquième, 0,2 × 0,4 × 1,085 = 0,087 Md€ : − 0,037 Md€ fin
    2026, et elle rejoint le régime général dès 2026."""
    caisse = "msa_exploitants_complementaire"
    projections = ic.projeter_les_caisses(RACINE_DONNEES, baisses={caisse: _baisse_posee(0.40)})
    rco = projections[caisse]
    assert rco.annee_integration == 2026
    assert rco.reserves[2026] * 2_991 == pytest.approx(-0.037, abs=0.005)
    assert rco.depenses[2026] * 2_991 == pytest.approx(1.085 - 0.087, abs=0.002)
    assert rco.economies[2026] * 2_991 == pytest.approx(0.087, abs=0.002)


def test_la_meme_baisse_d_un_coup_sauverait_2026():
    """La même baisse de 40 %, d'un coup à la bascule (``annees_de_baisse=1``),
    comme la page Coût la fait : 0,4 × 1,085 = 0,434 Md€ économisés en 2026,
    − 0,124 + 0,434 = + 0,310 Md€ fin 2026 : la caisse tient l'année. Le
    propriétaire a choisi les cinquièmes le 7 novembre 2026."""
    caisse = "msa_exploitants_complementaire"
    projections = ic.projeter_les_caisses(RACINE_DONNEES, baisses={caisse: _baisse_posee(0.40)},
                                          annees_de_baisse=1)
    rco = projections[caisse]
    assert rco.annee_integration != 2026
    assert rco.reserves[2026] * 2_991 == pytest.approx(0.310, abs=0.005)


def test_la_baisse_ne_touche_que_les_pensions_servies_a_la_bascule():
    """Le propriétaire, le 7 novembre 2026 : la baisse ne porte que sur les
    pensions déjà servies, non sur celles que la caisse liquide ensuite à ses
    règles. À la main, en 2030, cinquième année, la baisse entière : 30 % de
    la part de la dépense que le stock fait encore, posée à 0,5, soit 15 % de
    la dépense de l'Ircantec cette année-là."""
    sans = ic.projeter_les_caisses(RACINE_DONNEES, baisses={})["ircantec"]
    baisse = ic.BaisseDuStock(taux=0.30, part_du_stock={a: 0.5 for a in range(2026, ic.FIN + 1)})
    avec = ic.projeter_les_caisses(RACINE_DONNEES, baisses={"ircantec": baisse})["ircantec"]
    assert avec.depenses[2030] == pytest.approx(0.85 * sans.depenses[2030], rel=1e-12)
    assert avec.depenses[2026] == pytest.approx((1.0 - 0.2 * 0.15) * sans.depenses[2026], rel=1e-12)
    assert avec.recettes[2026] == pytest.approx(sans.recettes[2026], rel=1e-12)
    assert avec.reserves[2026] - sans.reserves[2026] == pytest.approx(
        0.2 * 0.15 * sans.depenses[2026], rel=1e-9)
