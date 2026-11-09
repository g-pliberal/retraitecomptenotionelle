"""La garantie vieillesse dégressive du scénario 6 (action 186, chantier 3).

Décision 100 du programme (``docs/feuille_de_route_programme.md``), le 9
novembre 2026 : « Jusqu'à la moitié du plancher (525 € seul, 400 € en couple),
la pension est retirée en entier, comme aujourd'hui ; au-delà, de moitié
seulement, et le complément s'éteint à une fois et demie le plancher (1 575 €,
1 200 €). » Décision 102 : « Le plancher d'une personne seule reste 1 050 €,
et la forme dégressive s'y applique en entier. »

Les valeurs attendues sont posées à la main, en euros par mois
(``docs/feuille_de_route/186/2026-11-09-garantie-degressive.md``, « La
consigne de la session du modèle ») ; aucune ne vient du code. Le portage, qui
fait foi pour une carrière, a les siennes dans
``tests/js/garantie-degressive.test.js`` ; ce fichier tient son jumeau Python
et le barème que le coût applique à la distribution des pensions.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

from retraite_notionnelle.config import Parametres, SituationFoyer
from retraite_notionnelle.donnees.distribution import DistributionPensions, Tranche
from retraite_notionnelle.garantie import (
    _manque_moyen,
    complement_garantie,
    cout_garantie,
    cout_garantie_par_sexe,
)
from retraite_notionnelle.simulateur import Simulateur

#: Les sondes de la prose sont un script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

#: La forme suédoise : la moitié du plancher, puis la moitié de la pension.
FORME = (0.5, 0.5)

#: Ressources et complément, en euros par mois. Seul, plancher de 1 050 €,
#: pivot de 525 € ; en couple, plancher de 800 €, pivot de 400 €.
SEUL = [
    (0.0, 1050.0),
    (400.0, 650.0),            # 1 050 − 400
    (525.0, 525.0),            # au pivot
    (600.0, 487.5),            # 525 − 0,5 × 75
    (1124.85, 225.075),        # 525 − 0,5 × 599,85 : le smicard seul
    (1575.0, 0.0),             # la sortie, 525 + 525 / 0,5
    (1600.0, 0.0),
]
COUPLE = [
    (0.0, 800.0),
    (400.0, 400.0),
    (593.19, 303.405),         # 400 − 0,5 × 193,19 : le mi-temps
    (1124.85, 37.575),         # 400 − 0,5 × 724,85
    (1200.0, 0.0),
]


def test_la_proposition_porte_la_forme_suedoise():
    parametres = Parametres()
    assert parametres.part_retrait_entier_garantie == 0.5
    assert parametres.taux_retrait_garantie == 0.5


@pytest.mark.parametrize("plancher, cas", [(1050.0, SEUL), (800.0, COUPLE)])
def test_le_bareme_retire_la_pension_en_entier_puis_de_moitie(plancher, cas):
    for ressources, attendu in cas:
        assert complement_garantie(plancher, ressources, *FORME) == pytest.approx(
            attendu, abs=1e-9), ressources


@pytest.mark.parametrize("situation, cas", [
    (SituationFoyer.SEUL, SEUL), (SituationFoyer.COUPLE, COUPLE)])
def test_le_moteur_python_sert_le_meme_bareme_que_le_portage(situation, cas):
    """Le jumeau de ``_garantieVieillesse``, à 66 ans en 2026 : le plancher est
    alors celui de la proposition, sans prix à lui appliquer."""
    simulateur = Simulateur(Parametres(situation_foyer=situation))
    carriere = simulateur.carriere_simple(
        annee_naissance=1960, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=21, age_liquidation=66, niveau_salaire=0.4)
    assert carriere.annee_liquidation == 2026
    for ressources, attendu in cas:
        garantie = simulateur.scenario_liberal._garantie_vieillesse(
            carriere, ressources * 12.0)
        assert garantie.complement / 12.0 == pytest.approx(attendu, abs=1e-9), ressources


def test_le_complement_ne_croit_jamais_et_le_total_ne_decroit_jamais():
    for plancher in (800.0, 1050.0):
        avant = None
        for pas in range(0, 137):
            ressources = 12.5 * pas
            servi = complement_garantie(plancher, ressources, *FORME)
            if avant is not None:
                assert servi <= avant[1] + 1e-9
                assert ressources + servi >= sum(avant) - 1e-9
            avant = (ressources, servi)


def test_a_un_et_un_le_bareme_redonne_la_garantie_differentielle_au_bit_pres():
    for plancher in (800.0, 1050.0, 893.5512345, 9600.0, 12600.0):
        for ressources in (0.0, 0.1, 333.33, 400.0, 525.0, 799.99, 800.0, 893.5512345,
                           1049.99, 1050.0, 1124.85, 9000.0, 13498.2, 30000.0):
            assert complement_garantie(plancher, ressources, 1.0, 1.0) == max(
                0.0, plancher - ressources)


# -- le barème sur une tranche de la distribution ----------------------------


def test_le_manque_moyen_d_une_tranche_suit_la_pente():
    """Part de la tranche que la garantie sert, et complément moyen sur toute
    la tranche, pensions uniformes dans la tranche. Seul : plancher de 1 050 €,
    pivot de 525 €, sortie à 1 575 €."""
    def manque(inferieure, superieure, plancher=1050.0):
        return _manque_moyen(inferieure, superieure, plancher, *FORME)

    # Sous le pivot, la tranche entière reçoit ce qui lui manque : 1 050 − 50.
    assert manque(0.0, 100.0) == pytest.approx((1.0, 1000.0))
    # À cheval sur le pivot : de 550 à 525 sur 25 €, moyenne 537,50 ; puis de
    # 525 à 487,50 sur 75 €, moyenne 506,25. (25 × 537,5 + 75 × 506,25) / 100.
    assert manque(500.0, 600.0) == pytest.approx((1.0, 514.0625))
    # Dans la pente : 525 − 0,5 × 475 = 287,50 à 1 000 €, 237,50 à 1 100 €.
    # La garantie différentielle n'y servait que la moitié de la tranche.
    assert manque(1000.0, 1100.0) == pytest.approx((1.0, 262.5))
    # À cheval sur la sortie : de 37,50 à zéro sur 75 €, moyenne 18,75, sur
    # les trois quarts de la tranche. 75 × 18,75 / 100.
    assert manque(1500.0, 1600.0) == pytest.approx((0.75, 14.0625))
    # Au-delà de la sortie, rien.
    assert manque(1600.0, 1700.0) == (0.0, 0.0)
    # La tranche ouverte est une masse ponctuelle à sa borne : 525 − 0,5 × 875.
    assert manque(1400.0, None) == pytest.approx((1.0, 87.5))
    assert manque(1600.0, None) == (0.0, 0.0)
    # En couple, plancher de 800 €, pivot de 400 €, sortie à 1 200 € : une
    # tranche de 200 € à cheval sur le pivot, 450 puis 375 en moyenne ; et la
    # dernière avant la sortie, de 50 € à zéro.
    assert manque(300.0, 500.0, 800.0) == pytest.approx((1.0, 412.5))
    assert manque(1100.0, 1200.0, 800.0) == pytest.approx((1.0, 25.0))


def _differentielle(borne_inferieure, borne_superieure, plancher):
    """Le manque moyen de la garantie différentielle, tel que le module
    l'écrivait avant le 9 novembre 2026 : la référence du bit près."""
    if borne_superieure is None:
        manque = max(0.0, plancher - borne_inferieure)
        return (1.0, manque) if manque > 0 else (0.0, 0.0)
    if borne_superieure <= plancher:
        return 1.0, plancher - (borne_inferieure + borne_superieure) / 2.0
    if borne_inferieure >= plancher:
        return 0.0, 0.0
    largeur = borne_superieure - borne_inferieure
    concernee = (plancher - borne_inferieure) / largeur
    return concernee, concernee * (plancher - borne_inferieure) / 2.0


def test_a_un_et_un_le_manque_moyen_est_celui_d_avant_au_bit_pres():
    """Sur les tranches de cent euros de l'enquête, déplacées des facteurs que
    le coût leur applique, et aux planchers qu'il leur oppose — ceux de 2026
    ramenés aux euros de 2020, 680,80 € et 893,55 €."""
    for facteur in (1.0, 0.62, 0.805, 0.979, 0.7312345678):
        for plancher in (680.8, 893.55, 800.0, 1050.0, 0.0, 9000.0):
            for rang in range(0, 46):
                inferieure, superieure = 100.0 * rang * facteur, 100.0 * (rang + 1) * facteur
                for borne in (superieure, None):
                    attendu = _differentielle(inferieure, borne, plancher)
                    assert _manque_moyen(inferieure, borne, plancher, 1.0, 1.0) == attendu
                    # Sans rien dire, le barème d'une tranche reste différentiel.
                    assert _manque_moyen(inferieure, borne, plancher) == attendu


# -- le barème sur une distribution ------------------------------------------


class _Distribution:
    """Quatre tranches posées à la main, un quart de la population chacune."""

    tranches = (
        Tranche(0.0, 100.0, 0.25),
        Tranche(500.0, 600.0, 0.25),
        Tranche(1000.0, 1100.0, 0.25),
        Tranche(1500.0, 1600.0, 0.25),
    )


def test_le_cout_d_une_distribution_additionne_ses_tranches():
    """Un million de personnes seules, plancher de 1 050 € : les manques moyens
    du test des tranches, un quart chacun."""
    chiffre = cout_garantie(_Distribution(), 1e6, 1050.0,
                            part_retrait_entier=0.5, taux_retrait=0.5)
    # 0,25 × (1 + 1 + 1 + 0,75).
    assert chiffre.part_beneficiaires == pytest.approx(0.9375)
    assert chiffre.beneficiaires == pytest.approx(937_500.0)
    # 0,25 × (1 000 + 514,0625 + 262,5 + 14,0625) = 447,65625 € par mois et
    # par personne, soit 5 371,875 M€ par an pour un million.
    assert chiffre.cout_annuel_meur == pytest.approx(5371.875)
    assert chiffre.complement_moyen_mensuel == pytest.approx(447.65625 / 0.9375)
    # La garantie différentielle servait moins de monde, et moins : 0,25 ×
    # (1 + 1 + 0,5) de la population, 0,25 × (1 000 + 500 + 12,5) € par mois.
    avant = cout_garantie(_Distribution(), 1e6, 1050.0)
    assert avant.part_beneficiaires == pytest.approx(0.625)
    assert avant.cout_annuel_meur == pytest.approx(0.25 * 1512.5 * 12.0)


def test_les_deux_planchers_suivent_la_meme_forme():
    """Décision 102 : l'isolement suit la même règle. Un million de personnes,
    toutes du même sexe, dont la moitié vit seule : la moitié du coût à 800 €,
    la moitié du coût à 1 050 €, chacun sous sa forme."""
    forme = dict(part_retrait_entier=0.5, taux_retrait=0.5)
    distribution = _Distribution()
    melange = cout_garantie_par_sexe(
        distribution, distribution, 1.0, 1e6, 800.0, 1.0, 1.0,
        plancher_majore=1050.0, part_seule={"F": 0.5, "H": 0.5}, **forme)
    a_deux = cout_garantie(distribution, 5e5, 800.0, **forme)
    seules = cout_garantie(distribution, 5e5, 1050.0, **forme)
    assert melange.cout_annuel_meur == pytest.approx(
        a_deux.cout_annuel_meur + seules.cout_annuel_meur)
    assert melange.beneficiaires == pytest.approx(
        a_deux.beneficiaires + seules.beneficiaires)
    # À 800 €, pivot de 400 € et sortie à 1 200 € : 0,25 × (750 + 325 + 75) €
    # par mois — 400 − 0,5 × 150 = 325 au milieu de la deuxième tranche, 400 −
    # 0,5 × 650 = 75 au milieu de la troisième, rien à la quatrième.
    assert a_deux.cout_annuel_meur == pytest.approx(0.25 * 1150.0 * 5e5 * 12.0 / 1e6)


def test_a_un_et_un_le_cout_de_l_enquete_est_celui_d_avant_au_bit_pres():
    """La distribution de la DREES, à ses deux planchers et sous les facteurs
    du modèle : dire « un et un » ne change pas un bit à ce que rendait le
    plancher différentiel."""
    racine = Parametres().racine_donnees
    distribution = DistributionPensions(racine)
    for facteur in (1.0, 0.62, 0.805, 0.979):
        for plancher in (680.8, 893.55):
            assert cout_garantie(distribution, 16e6, plancher, facteur,
                                 part_retrait_entier=1.0, taux_retrait=1.0) == cout_garantie(
                distribution, 16e6, plancher, facteur)
    # Et la forme suédoise sert plus de monde, pour plus cher.
    avant = cout_garantie(distribution, 16e6, 893.55, 0.805)
    apres = cout_garantie(distribution, 16e6, 893.55, 0.805,
                          part_retrait_entier=0.5, taux_retrait=0.5)
    assert apres.beneficiaires > avant.beneficiaires
    assert apres.cout_annuel_meur > avant.cout_annuel_meur


def test_un_taux_de_retrait_nul_est_refuse():
    """Sans retrait, la garantie ne s'éteindrait jamais : ce n'est plus un
    plancher, et la sortie n'a pas de valeur."""
    with pytest.raises(ValueError, match="taux de retrait"):
        cout_garantie(_Distribution(), 1e6, 1050.0, part_retrait_entier=0.5, taux_retrait=0.0)
    with pytest.raises(ValueError, match="part du plancher"):
        cout_garantie(_Distribution(), 1e6, 1050.0, part_retrait_entier=1.5, taux_retrait=0.5)


def test_la_forme_se_regle_sans_toucher_au_plancher():
    """Les deux paramètres sont ceux de ``Parametres`` : à un et un, la
    proposition redevient celle d'avant."""
    differentielle = replace(Parametres(), part_retrait_entier_garantie=1.0,
                             taux_retrait_garantie=1.0)
    assert differentielle.garantie_vieillesse_mensuelle == 800.0
    assert differentielle.allocation_isolement_mensuelle == 250.0


# -- la garantie projetée par le coût ----------------------------------------


def test_la_garantie_projetee_applique_la_forme_qu_on_lui_donne():
    """``GarantieDistribution`` porte la forme du barème, et l'applique à la
    colonne d'ensemble comme au mélange des sexes et des deux planchers."""
    from retraite_notionnelle.cout import GarantieDistribution

    racine = Parametres().racine_donnees
    distribution = DistributionPensions(racine)
    forme = dict(part_retrait_entier=0.5, taux_retrait=0.5)
    calage = GarantieDistribution(distribution, 680.8, 1000.0, 1.0, 1.0, **forme)
    assert calage.chiffrer_distribution(16e6, 0.8) == cout_garantie(
        distribution, 16e6, 680.8, 0.8, **forme)

    sexes = {sexe: DistributionPensions(racine, sexe=sexe) for sexe in ("F", "H")}
    part_seule = {"F": 0.56, "H": 0.29}
    calage = GarantieDistribution(
        distribution, 680.8, 1000.0, 1.0, 1.0, distributions_sexe=sexes,
        part_femmes=0.528, rapport_deplacement=0.9, plancher_majore=893.55,
        part_seule=part_seule, **forme)
    assert calage.chiffrer_distribution(16e6, 0.8) == cout_garantie_par_sexe(
        sexes["F"], sexes["H"], 0.528, 16e6, 680.8, 0.8, 0.9, 893.55, part_seule, **forme)
    # Sans forme, elle reste différentielle ; et une forme absurde est refusée.
    differentielle = GarantieDistribution(distribution, 680.8, 1000.0, 1.0, 1.0)
    assert differentielle.chiffrer_distribution(16e6, 0.8) == cout_garantie(
        distribution, 16e6, 680.8, 0.8)
    with pytest.raises(ValueError, match="taux de retrait"):
        GarantieDistribution(distribution, 680.8, 1000.0, 1.0, 1.0,
                             part_retrait_entier=0.5, taux_retrait=0.0)


# -- la prose ----------------------------------------------------------------


def test_la_sonde_de_prose_du_complement_suit_le_bareme_du_moteur():
    """``garantie_complement``, que la prose ancre : ce que la garantie sert à
    une personne en couple. 300 € sont sous le pivot de 400 € : 800 − 300 =
    500 €. 900 € sont dans la pente : 400 − 0,5 × 500 = 150 €, là où la sonde,
    qui portait sa propre formule différentielle, aurait dit zéro."""
    import mesures_prose

    assert mesures_prose.garantie_complement(pension="300") == pytest.approx(500.0)
    assert mesures_prose.garantie_complement(pension="900") == pytest.approx(150.0)
    assert mesures_prose.garantie_complement(pension="1500") == 0.0


# -- le recours ----------------------------------------------------------------


def test_la_garantie_est_servie_d_office():
    """Décision 20 du programme : « La garantie vieillesse est servie
    d'office, sans demande : "D'office" ». Tous les ayants droit la reçoivent,
    et le coût les compte tous ; l'ASPA du droit actuel garde son non-recours,
    sous un taux à elle."""
    parametres = Parametres()
    assert parametres.taux_recours_garantie == 1.0
    assert parametres.taux_recours_aspa == 0.5
