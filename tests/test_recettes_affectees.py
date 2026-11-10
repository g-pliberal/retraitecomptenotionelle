"""Les deux recettes hors du travail que le programme donne aux retraites.

Décisions 79 à 81 du programme (action 186, chantier 4,
``docs/feuille_de_route/186/2026-11-07-recettes-tva-lvt.md``) : la TVA reste à
20 % et la part qui va déjà aux retraites leur reste ; la taxe foncière devient
une taxe sur la valeur du terrain (LVT) à 2 %, dont un point aux retraites, dès
la bascule.

Trois choses s'y vérifient. Que les DONNÉES sont celles de leur source : le
patrimoine de l'Insee, la taxe foncière des comptes nationaux, le compte de
l'Agirc-Arrco du COR. Que le CALCUL de la LVT est celui de l'étude du
7 novembre 2026, posé ici à la main : la taxe se capitalise dans le prix du
terrain, qui contient déjà la taxe foncière. Et que le PARTAGE est celui qui a
été décidé : les deux recettes entrent au régime de la proposition, à compter
de sa bascule, et à aucun autre système.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.cout import DONT_IMPOTS, SoldeAnnuel
from retraite_notionnelle.donnees.lvt import TaxeTerrain
from retraite_notionnelle.donnees.tva import TvaGardee

LIBERAL = "notionnel_liberal"


@pytest.fixture(scope="module")
def terrain() -> TaxeTerrain:
    return TaxeTerrain(RACINE_DONNEES)


@pytest.fixture(scope="module")
def gardee() -> TvaGardee:
    return TvaGardee(RACINE_DONNEES)


# -- les données de la LVT -------------------------------------------------------


def test_les_terrains_batis_sont_ceux_que_l_insee_publie(terrain):
    """Fin 2025, 7 032,4 Md€ de terrains bâtis pour l'économie nationale
    (Insee, patrimoine national par secteur, données provisoires de juillet
    2026), dont 941,4 aux administrations, qui ne paient pas la taxe foncière :
    6 091 Md€ d'assiette."""
    assert terrain.annee == 2025
    assert terrain.valeur("terrains_batis") == pytest.approx(7_032_377.2, abs=1.0)
    assert terrain.valeur("terrains_batis", "administrations_publiques") == pytest.approx(
        941_393.3, abs=0.1)
    assert terrain.assiette() == pytest.approx(6_090_983.9, abs=1.0)


def test_l_immobilier_prive_est_la_somme_des_logements_des_batiments_et_des_terrains(terrain):
    """13 447 Md€ : ce à quoi l'étude rapporte la taxe foncière."""
    assert terrain.immobilier() == pytest.approx(13_447_218.2, abs=1.0)


def test_les_taxes_foncieres_sont_celles_des_comptes_nationaux(terrain):
    """42,9 Md€ en 2024, dont 26,1 payés par les ménages et 16,8 par les autres
    agents (Fipeco, 29 septembre 2025, en comptabilité nationale)."""
    assert terrain.annee_taxe_fonciere == 2024
    assert terrain.taxe_fonciere() == pytest.approx(42_900.0)
    assert terrain.taxe_fonciere("menages") == pytest.approx(26_100.0)


def test_la_taxe_fonciere_vaut_un_tiers_de_point_de_l_immobilier_prive(terrain):
    """0,32 % : le taux que les prix d'aujourd'hui contiennent déjà."""
    assert terrain.taux_actuel() == pytest.approx(42.9 / 13_447.2182, rel=1e-9)
    assert round(terrain.taux_actuel(), 4) == 0.0032


# -- le calcul de la LVT ---------------------------------------------------------


@pytest.mark.parametrize("rendement, taux, prix, produit", [
    # Le tableau de l'étude : rendement locatif du terrain, taux de la LVT,
    # variation du prix du terrain, produit en Md€.
    (0.025, 0.01, -0.21, 48.0), (0.03, 0.01, -0.19, 50.0), (0.04, 0.01, -0.15, 52.0),
    (0.025, 0.02, -0.40, 73.0), (0.03, 0.02, -0.36, 78.0), (0.04, 0.02, -0.30, 86.0),
])
def test_la_lvt_se_capitalise_dans_le_prix_du_terrain(terrain, rendement, taux, prix, produit):
    """P₁ = P₀ × y / (y − τ₀ + t), et le produit est t × P₁ : le tableau de
    l'étude du 7 novembre 2026, au milliard près, et à un point près pour le
    prix, qu'elle arrondit."""
    assert terrain.facteur_prix(taux, rendement) - 1.0 == pytest.approx(prix, abs=0.01)
    assert terrain.produit(taux, rendement) / 1e3 == pytest.approx(produit, abs=0.5)


def test_le_produit_central_pose_a_la_main(terrain):
    """À 2 % et 3 % de rendement : 0,03 ÷ (0,03 − 0,00319025 + 0,02) = 0,640892,
    et 2 % × 6 090,98 Md€ × 0,640892 = 78,07 Md€."""
    assert terrain.facteur_prix(0.02, 0.03) == pytest.approx(0.640892, abs=1e-6)
    assert terrain.produit(0.02, 0.03) == pytest.approx(78_073.0, abs=1.0)


def test_sans_lvt_rien_ne_change(terrain):
    """Zéro veut dire « la taxe foncière reste » : ni produit, ni prix déplacé."""
    assert terrain.produit(0.0, 0.03) == 0.0
    assert terrain.facteur_prix(0.0, 0.03) == 1.0
    assert terrain.part_pib(0.01, 0.0, 0.03) == 0.0


def test_le_point_des_retraites_vaut_un_point_trois_de_pib(terrain):
    """Un point sur les deux : 39,04 Md€, soit 1,305 % des 2 991 Md€ du PIB de
    2025, l'année des terrains — la part que le coût tient constante."""
    assert terrain.part_pib(0.01, 0.02, 0.03) == pytest.approx(39_036.5 / 2_991_056, rel=1e-5)
    assert round(100 * terrain.part_pib(0.01, 0.02, 0.03), 2) == 1.31
    # La fourchette de la décision 80 : 1,2 à 1,4 point de PIB.
    assert round(100 * terrain.part_pib(0.01, 0.02, 0.025), 1) == 1.2
    assert round(100 * terrain.part_pib(0.01, 0.02, 0.04), 1) == 1.4


def test_les_communes_gardent_a_peu_pres_leur_taxe_fonciere(terrain):
    """L'autre point leur revient : 39 Md€, contre 42,9 aujourd'hui."""
    communes = terrain.produit(0.02, 0.03) - terrain.part_pib(0.01, 0.02, 0.03) * 2_991_056
    assert communes == pytest.approx(39_036.5, abs=1.0)
    assert communes < terrain.taxe_fonciere()


# -- la part de TVA gardée -------------------------------------------------------


def _pib(annee: int) -> float:
    """Un PIB posé à la main, en millions d'euros : 3 065 Md€ en 2026, celui
    que le coût projette, 3 140 ensuite."""
    return {2025: 2_991_056.0, 2026: 3_065_000.0}.get(annee, 3_140_000.0)


def test_la_tva_des_retraites_est_la_compensation_de_l_agirc_arrco(gardee):
    """L'article L. 131-8 du code de la sécurité sociale n'affecte aucune TVA
    à la branche vieillesse : la part des retraites est la compensation de la
    réduction générale à l'Agirc-Arrco, que le dépôt tient du rapport à la
    Commission des comptes de la sécurité sociale d'octobre 2026
    (``donnees/compensation_agirc_arrco.py``) : 6,01 points sur les 10,2 que
    la réduction efface hors des régimes de base, 12,587 Md€ en 2025 et
    18,910 en 2026."""
    assert gardee.montant(2025) == pytest.approx(12_587.0 * 6.01 / 10.2)
    assert gardee.montant(2026) == pytest.approx(18_910.0 * 6.01 / 10.2)
    assert round(gardee.montant(2025) / 1e3, 1) == 7.4
    assert round(gardee.montant(2026) / 1e3, 1) == 11.1


def test_la_part_gardee_se_rapporte_au_pib_de_son_annee(gardee):
    """11,1 Md€ sur 3 065 Md€ de PIB en 2026 : 0,36 point."""
    assert gardee.part_pib(2026, _pib) == pytest.approx(18_910.0 * 6.01 / 10.2 / 3_065_000.0)
    assert round(100 * gardee.part_pib(2026, _pib), 2) == 0.36


def test_au_dela_des_annees_publiees_la_part_de_pib_est_tenue(gardee):
    """Le rapport prévoit jusqu'en 2027 : 18,011 Md€ hors des régimes de base,
    10,6 à l'Agirc-Arrco. Ensuite la part garde sa part de PIB de 2027, la
    convention du dépôt pour ce qu'il ne sait pas projeter."""
    en_2027 = 18_011.0 * 6.01 / 10.2 / 3_140_000.0
    assert gardee.part_pib(2027, _pib) == pytest.approx(en_2027)
    for annee in (2028, 2040, 2070):
        assert gardee.part_pib(annee, _pib) == pytest.approx(en_2027), annee
    # Sans PIB pour l'année publiée, rien : pas de division par zéro.
    assert gardee.part_pib(2030, lambda annee: 0.0) == 0.0


def test_sans_ses_donnees_la_part_gardee_est_nulle(tmp_path):
    """Une racine de données réduite ne garde rien, sans lever d'erreur."""
    vide = TvaGardee(tmp_path)
    assert not vide
    assert vide.part_pib(2030, _pib) == 0.0


# -- le partage ------------------------------------------------------------------


def _ligne(**champs) -> SoldeAnnuel:
    """Une année du bilan réduite à ce que les recettes affectées regardent."""
    valeurs = dict(
        annee=2030, projete=True, ressources=0.14, depenses=0.14,
        rapports={"actuel": 1.0, LIBERAL: 0.7, "notionnel_pur": 0.8},
        pib=0.0, part_contributive=0.77, part_impots=0.15, part_subventions=0.02,
        taux_prelevement=0.30, taux_liberal=0.18, annee_bascule=2026,
        convention_recette="assiette",
        parts={"cotisations": 0.65, "contribution_equilibre_etat": 0.12,
               "subventions_equilibre": 0.02, "impots_et_taxes": 0.15,
               "transferts": 0.04, "autres_produits": 0.02},
        tva_gardee=0.0024, lvt_retraites=0.013, garantie_liberal=0.005,
    )
    valeurs.update(champs)
    return SoldeAnnuel(**valeurs)


def test_les_deux_recettes_entrent_au_regime_de_la_proposition():
    """Les ressources de la proposition montent de leur somme, au centième de
    point près, et la garantie vieillesse reste à la charge du budget."""
    avec, sans = _ligne(), _ligne(tva_gardee=0.0, lvt_retraites=0.0)
    assert avec.ressources_de(LIBERAL) - sans.ressources_de(LIBERAL) == pytest.approx(0.0154)
    assert avec.solde(LIBERAL) - sans.solde(LIBERAL) == pytest.approx(0.0154)
    assert avec.tva_garantie(LIBERAL) == 0.0


def test_elles_ont_chacune_leur_ligne_au_poste_des_impots_affectes():
    """Le poste ne porte plus qu'elles, et les lignes somment au total."""
    assert {"impots_tva_gardee", "impots_lvt"} <= set(DONT_IMPOTS)
    ligne = _ligne()
    postes = ligne.postes_ressources(LIBERAL)
    assert postes["impots_tva_gardee"] == pytest.approx(0.0024)
    assert postes["impots_lvt"] == pytest.approx(0.013)
    assert postes["impots_et_taxes"] == pytest.approx(0.0154)
    assert postes["impots_autres"] == pytest.approx(0.0, abs=1e-15)
    total = sum(postes[code] for code in (
        "cotisations", "contribution_equilibre_etat", "subventions_equilibre",
        "impots_et_taxes", "transferts", "autres_produits"))
    assert total == pytest.approx(ligne.ressources_de(LIBERAL))


def test_aucun_autre_systeme_ne_les_recoit():
    ligne = _ligne()
    sans = _ligne(tva_gardee=0.0, lvt_retraites=0.0)
    for scenario in ("actuel", "notionnel_pur"):
        assert ligne.ressources_de(scenario) == sans.ressources_de(scenario)
        postes = ligne.postes_ressources(scenario)
        assert postes["impots_tva_gardee"] == 0.0 and postes["impots_lvt"] == 0.0


def test_avant_la_bascule_la_proposition_ne_les_recoit_pas():
    avant = _ligne(annee=2025)
    sans = _ligne(annee=2025, tva_gardee=0.0, lvt_retraites=0.0)
    assert avant.ressources_de(LIBERAL) == sans.ressources_de(LIBERAL)
    assert avant.postes_ressources(LIBERAL)["impots_lvt"] == 0.0


def test_sous_l_ancienne_convention_la_tva_gardee_ne_se_compte_pas_deux_fois():
    """La convention du rapport ne retire pas les impôts affectés : la part de
    TVA y est encore, et seule la LVT s'ajoute."""
    avec = _ligne(convention_recette="rapport", rapports_recettes={LIBERAL: 0.6})
    sans = _ligne(convention_recette="rapport", rapports_recettes={LIBERAL: 0.6},
                  tva_gardee=0.0, lvt_retraites=0.0)
    assert avec.ressources_de(LIBERAL) - sans.ressources_de(LIBERAL) == pytest.approx(0.013)
    postes = avec.postes_ressources(LIBERAL)
    assert postes["impots_tva_gardee"] == 0.0
    assert postes["impots_lvt"] == pytest.approx(0.013)


# -- le défaut -------------------------------------------------------------------


def test_le_defaut_est_celui_des_decisions_79_et_80():
    """La part de TVA gardée ; une LVT à 2 %, dont un point aux retraites ; un
    rendement locatif du terrain de 3 %, le centre de l'étude."""
    parametres = Parametres()
    assert parametres.tva_des_retraites_gardee is True
    assert parametres.taux_lvt == 0.02
    assert parametres.taux_lvt_retraites == 0.01
    assert parametres.rendement_locatif_terrain == 0.03
    # La TVA ne monte pas : le taux unique reste une variante éteinte.
    assert parametres.taux_tva_liberal == 0.0
