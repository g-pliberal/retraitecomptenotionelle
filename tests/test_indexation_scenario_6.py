"""Le coût du scénario 6 sous les voies de l'indexation (action 186, chantier 5).

Le coût agrégé, recalculé sous une voie (``calculer_cout(indexation_liberale=…)``) :
la règle d'avant redonne le modèle, α = 1 retire au scénario 6 ce que le
nombre de retraités par cotisant lui demande, et la crise de l'emploi passe
par la variante d'emploi que la page Coût sait déjà faire. Puis l'étude de
``scripts/indexation_scenario_6.py``, sur ce qu'elle établit par
construction.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle import indexation_programme as I
from retraite_notionnelle import memoire

LIBERAL = "notionnel_liberal"
RACINE = Path(__file__).resolve().parents[1]


def _sous(voie: str, trajectoire: str):
    voies, trajectoires = I.charger()
    return memoire.cout(indexation_liberale=I.IndexationLiberale(
        voies[voie], trajectoires[trajectoire]))


def _par_annee(cout):
    return {ligne.annee: ligne for ligne in cout.solde.annees}


def test_sous_la_regle_d_avant_le_scenario_6_coute_ce_que_le_modele_calcule():
    modele, avant = _par_annee(memoire.cout()), _par_annee(_sous("avant", "cor"))
    assert set(modele) == set(avant)
    for annee, ligne in modele.items():
        assert avant[annee].depense(LIBERAL) == pytest.approx(ligne.depense(LIBERAL),
                                                              rel=1e-9), annee
        assert avant[annee].solde(LIBERAL) == pytest.approx(ligne.solde(LIBERAL),
                                                            rel=1e-9, abs=1e-15), annee


def test_sous_alpha_un_le_scenario_6_sert_moins_a_compter_de_la_bascule():
    modele, regle = _par_annee(memoire.cout()), _par_annee(_sous("regle", "cor"))
    # La bascule elle-même ne change rien : la règle joue à compter de 2027.
    assert regle[2026].depense(LIBERAL) == pytest.approx(modele[2026].depense(LIBERAL),
                                                         rel=1e-9)
    for annee in (2030, 2050, 2070):
        assert regle[annee].depense(LIBERAL) < modele[annee].depense(LIBERAL)
    # Les autres systèmes ne bougent pas.
    assert regle[2050].depense("actuel") == modele[2050].depense("actuel")


def test_la_crise_de_l_emploi_retire_au_pib_ce_qu_elle_retire_a_l_emploi():
    modele = {ligne.annee: ligne for ligne in memoire.cout().avenir.annees}
    crise = {ligne.annee: ligne for ligne in _sous("avant", "emploi_ia").avenir.annees}
    assert crise[2029].pib == pytest.approx(modele[2029].pib, rel=1e-12)
    assert crise[2045].pib == pytest.approx(modele[2045].pib * 0.99 ** 10, rel=1e-12)
    # Le système actuel sert les mêmes euros : sa part du PIB monte d'autant.
    assert crise[2045].cout_constants("actuel") == pytest.approx(
        modele[2045].cout_constants("actuel"), rel=1e-9)


def test_la_masse_du_stock_est_celle_des_prix_fois_le_chemin_d_un_euro():
    """Toutes les pensions du stock suivent le même chemin depuis la bascule :
    sa masse sous une voie est sa masse sous les prix, fois ce que devient un
    euro de la bascule. L'étude sépare ainsi le stock des nouvelles sans
    recalculer le stock seul sous chaque voie."""
    sys.path.insert(0, str(RACINE / "scripts"))
    import indexation_scenario_6 as script

    voies, trajectoires = I.charger()
    basse = trajectoires["inflation_basse"]
    aux_prix = script._droits_directs(script._cout(voies["avant"], basse, "stock"))
    sous_la_voie = script._droits_directs(script._cout(voies["decidee"], basse, "stock"))
    euro = script._pensions(voies["decidee"], basse).detail_stock()
    for annee in (2026, 2033, 2040, 2055, 2070):
        assert sous_la_voie[annee] == pytest.approx(aux_prix[annee] * euro.servi[annee],
                                                    rel=1e-9)


def test_sous_la_voie_1_decidee_le_cout_suit_la_prime_que_la_reserve_fixe():
    """La voie 1 décidée revalorise le stock sur sa prime, sa réserve et sa
    dette, que la masse du stock mesure : la masse du stock sous elle est sa
    masse sous les prix, fois le chemin d'un euro que le module calcule."""
    sys.path.insert(0, str(RACINE / "scripts"))
    import indexation_scenario_6 as script

    voies, trajectoires = I.charger()
    crise = trajectoires["emploi_ia"]
    aux_prix = script._droits_directs(script._cout(voies["avant"], crise, "stock"))
    masses = tuple(sorted(aux_prix.items()))
    voie = voies["voie_1_crise_a_ses_dates"]
    sous_la_voie = script._droits_directs(script._cout(voie, crise, "stock", masses))
    euro = script._pensions(voie, crise, masses).detail_stock()
    assert euro.prime[2026] == 0.0215
    for annee in (2026, 2033, 2040, 2055, 2070):
        assert sous_la_voie[annee] == pytest.approx(aux_prix[annee] * euro.servi[annee],
                                                    rel=1e-9)


def test_une_variante_demographique_ne_se_croise_pas_avec_une_crise_de_l_emploi():
    voies, trajectoires = I.charger()
    with pytest.raises(ValueError, match="emploi"):
        memoire.cout(demographie="fecondite_basse", indexation_liberale=I.IndexationLiberale(
            voies["avant"], trajectoires["emploi_ia"]))


# -- l'étude ------------------------------------------------------------------


@pytest.fixture(scope="module")
def etude():
    sys.path.insert(0, str(RACINE / "scripts"))
    import indexation_scenario_6 as script

    return script.etudier()


def test_la_baisse_d_avance_de_la_voie_2_rend_au_cor_la_regle_alpha_un(etude):
    """Calculée au jour de la bascule sous le COR, la baisse de la voie 2
    retire au stock, en valeur actuelle, ce que α = 1 lui retire : sous le
    COR, la voie 2 ne laisse rien aux cotisants sur le stock."""
    assert 0.0 < etude.baisse_voie_2 < 0.15
    stock = etude.resultat("voie_2", "cor").stock
    assert stock.valeur_actuelle_ecart == pytest.approx(0.0, abs=1e-9)


def test_sous_le_cor_le_plancher_ne_joue_pas(etude):
    """Sous 1,75 % d'inflation, aucune règle ne baisse en euros : α = 1 avec
    plancher et dette est α = 1, et le plancher n'avance rien."""
    decidee, regle = etude.resultat("decidee", "cor"), etude.resultat("regle", "cor")
    assert decidee.depense == regle.depense
    for voie in ("decidee", "voie_3"):
        resultat = etude.resultat(voie, "cor")
        echelle = max(resultat.stock.servi.values())
        for groupe in (resultat.stock, resultat.nouvelles):
            assert max(abs(d) for d in groupe.dette.values()) < 1e-9 * echelle


def test_la_prime_calibree_sur_un_choc_vide_la_reserve_a_l_horizon_sous_ce_choc(etude):
    for choc in ("inflation_basse", "emploi_ia"):
        resultat = etude.resultat(f"voie_1_{choc}", choc)
        assert etude.primes[choc] > 0.0
        assert resultat.reserve_actuelle == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("lecture", ["v1_dates", "v1_recommencee"])
def test_sous_le_cor_la_reserve_de_la_voie_1_decidee_revient_au_stock(etude, lecture):
    """Décision 75 : la réserve qui ne servira pas est rendue au stock en
    route. Sous le COR, le plancher ne joue jamais : sur sa vie, le stock
    touche ce que α = 1 lui sert, en valeur actuelle, à ce que la réserve
    garde encore en 2070 près."""
    resultat = etude.resultat(lecture, "cor")
    assert resultat.stock.valeur_actuelle_ecart == pytest.approx(0.0, abs=1e-4)
    assert max(resultat.reserve.values()) > 0.0
    assert all(dette == 0.0 for dette in resultat.stock.dette.values())


def test_sous_le_cor_la_reserve_rendue_ne_revient_toute_au_stock_que_mise_en_commun(etude):
    """La réserve personnelle, non transmise : rendue de son vivant et ce que
    laissent les morts aux survivants, le stock retrouve sur sa vie ce que
    α = 1 lui sert ; ce que les morts laissent sortant du stock, il perd, et
    les cotisants gagnent. Jamais rendue, le stock perd sa contribution."""
    commun = etude.resultat("rp_dates_commun", "cor").stock.valeur_actuelle_ecart
    a_soi = etude.resultat("rp_dates_a_soi", "cor").stock.valeur_actuelle_ecart
    jamais = etude.resultat("rp_jamais_a_soi", "cor").stock.valeur_actuelle_ecart
    assert commun == pytest.approx(0.0, abs=1e-3)
    assert jamais < a_soi < commun - 1e-3
