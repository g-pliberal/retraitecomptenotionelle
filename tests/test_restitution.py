"""Ce que la proposition rend au salaire, et ce qu'elle éteint en dette.

Quatre choses s'y vérifient, et elles n'ont pas le même statut.

D'abord que le PARTAGE est un partage : les deux moitiés somment au poste
abandonné, et le réglage tient ses deux bornes — à zéro rien n'est rendu, à un
tout l'est.

Ensuite que l'ORDRE est celui que le droit impose : ce qui est assis sur une
rémunération est supprimé d'abord, et la CSG ne prend que le solde. C'est ce
qui interdit de compter deux fois la même somme.

Puis que le CHIFFRE tient : un peu plus d'un point de CSG, et une part du poste
assise sur la rémunération qui reste entre un quart et un tiers sur toute la
fenêtre publiée. Si l'un des deux sortait de ces bornes, c'est qu'une série
aurait changé de périmètre.

Enfin que la RECONDUCTION est celle d'un taux et non d'un montant : au-delà de
la dernière année publiée, la part du poste ne bouge plus, et le montant suit
le poste que le COR projette.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.restitution import (
    POSTES_REMUNERATION,
    Restitution,
    points_csg_rendus,
)

PARAMETRES = Parametres()


@pytest.fixture(scope="module")
def restitution() -> Restitution:
    return Restitution(PARAMETRES.racine_donnees, PARAMETRES.part_rendue_aux_salaires)


def test_les_deux_moities_somment_au_poste_abandonne(restitution):
    """Un partage est un partage : rien ne se perd entre les deux moitiés."""
    for annee in (2024, 2030, 2050, 2070):
        part = restitution.annuelle(annee)
        assert part.rendu + part.eteint_de_dette == pytest.approx(
            part.poste_abandonne, rel=1e-12)


def test_ce_qui_est_supprime_sort_de_la_moitie_rendue(restitution):
    """L'ordre du droit, et ce qui interdit de compter deux fois.

    La taxe sur les salaires et le forfait social sont SUPPRIMÉS, et cette
    suppression est prise sur la moitié rendue : la CSG ne rend que le solde.
    Les compter à côté ferait rendre plus que la moitié.
    """
    part = restitution.annuelle(2024)
    assert 0 < part.supprime_sur_la_remuneration < part.rendu
    reste = part.rendu - part.supprime_sur_la_remuneration
    assiette = restitution.assiette.part_pib(
        restitution.assiette.annee_de_reference(2024))
    assert part.points_csg == pytest.approx(reste / assiette, rel=1e-12)


def test_le_reglage_tient_ses_deux_bornes():
    """Zéro rend l'ancienne convention, un donne la baisse d'impôt intégrale."""
    rien = Restitution(PARAMETRES.racine_donnees, 0.0).annuelle(2024)
    assert rien.rendu == 0.0
    assert rien.supprime_sur_la_remuneration == 0.0
    assert rien.points_csg == 0.0
    assert rien.eteint_de_dette == pytest.approx(rien.poste_abandonne)

    tout = Restitution(PARAMETRES.racine_donnees, 1.0).annuelle(2024)
    assert tout.eteint_de_dette == 0.0
    assert tout.rendu == pytest.approx(tout.poste_abandonne)
    # Et la CSG rend davantage, puisque la suppression n'absorbe plus la moitié
    # mais le quart du poste.
    assert tout.points_csg > Restitution(
        PARAMETRES.racine_donnees, 0.5).annuelle(2024).points_csg


def test_un_peu_plus_d_un_point_de_csg(restitution):
    """Le chiffre de tête, et ses bornes.

    Un point, à peu près, sur toute la fenêtre. Sortir de ces bornes signalerait
    qu'une des trois séries a changé de périmètre — le poste du COR, les deux
    impôts, ou l'assiette des revenus d'activité.
    """
    for annee in range(2019, 2071):
        points = restitution.annuelle(annee).points_csg
        assert 0.005 < points < 0.02, annee


def test_la_part_assise_sur_la_remuneration_est_stable(restitution):
    """Entre un quart et un tiers du poste, de 2019 à 2025.

    C'est ce qui autorise à la reconduire au-delà : une part qui aurait doublé
    sur la fenêtre ne se prolongerait pas.
    """
    for annee in range(2019, restitution.derniere_annee + 1):
        assert 0.25 < restitution.part_du_poste(annee) < 0.33, annee


def test_au_dela_de_la_fenetre_c_est_le_taux_qui_se_reconduit(restitution):
    """Un montant en euros courants de 2025 ne se prolonge pas jusqu'en 2070.

    La part du poste, elle, se prolonge — et le montant suit le poste que le
    COR projette, qui n'est pas constant.
    """
    derniere = restitution.derniere_annee
    assert restitution.part_du_poste(2070) == pytest.approx(
        restitution.part_du_poste(derniere))
    supprime_2070 = restitution.annuelle(2070).supprime_sur_la_remuneration
    supprime_derniere = restitution.annuelle(derniere).supprime_sur_la_remuneration
    assert supprime_2070 != pytest.approx(supprime_derniere, rel=1e-6)


def test_les_deux_impots_sont_ceux_que_le_droit_designe(restitution):
    """La taxe sur les salaires et le forfait social, et rien d'autre.

    Le reste du poste est assis sur du capital, sur des pensions ou sur un
    chiffre d'affaires : le rendre au salarié n'aurait pas de sens. Voir le
    docstring du module pour les articles.
    """
    assert [code for code, _ in POSTES_REMUNERATION] == [
        "taxe_sur_les_salaires", "forfait_social"]
    assert restitution.montant_remuneration(2024) == pytest.approx(
        9694.0 + 6300.0)


def test_le_raccourci_de_la_fiche_de_paie_donne_la_meme_chose(restitution):
    """``points_csg_rendus`` n'est que ``annuelle(...).points_csg``, mémorisé."""
    assert points_csg_rendus(
        PARAMETRES.racine_donnees, 2026, PARAMETRES.part_rendue_aux_salaires
    ) == pytest.approx(restitution.annuelle(2026).points_csg)


# .. la part de TVA gardée ......................................................
#
# La proposition garde la part de TVA qui va déjà aux retraites (décision 79
# du programme, ``donnees/tva.py``) : le coût la lui rend sur la ligne
# ``impots_tva_gardee``. Elle n'est donc pas abandonnée, et le partage qui la
# compterait la distribuerait une seconde fois — 64 Md€ partagés en 2026 quand
# la retraite n'en perd que 53. Le propriétaire a tranché le 21 novembre 2026 :
# moitié, moitié, sur ce qui est vraiment abandonné.

#: La compensation de l'Agirc-Arrco en 2026, en millions d'euros, calculée à la
#: main sur la source : la réduction générale efface 18 910 M€ hors des
#: régimes de base (rapport CCSS d'octobre 2026, fiche 1.6, tableau 2), dont
#: l'Agirc-Arrco porte 6,01 points sur 10,2.
COMPENSATION_2026_MEUR = 11142.06862745098


def test_la_part_de_tva_gardee_n_est_pas_partagee(restitution):
    """Rendu et dette somment au poste du COR MOINS la part de TVA gardée."""
    part = restitution.annuelle(2026)
    pib_2026 = restitution.pib_de_la_trajectoire(2026)
    assert part.tva_gardee * pib_2026 == pytest.approx(COMPENSATION_2026_MEUR, rel=1e-12)
    assert part.poste_abandonne == pytest.approx(
        restitution.poste_affecte(2026) - part.tva_gardee - part.cta_supprimee,
        rel=1e-12)
    assert part.rendu + part.eteint_de_dette == pytest.approx(
        part.poste_abandonne, rel=1e-12)


def test_le_pib_de_2026_est_celui_que_le_cout_projette(restitution):
    """Le PIB publié de 2025, que fait croître la variation nominale de 2026 :
    la convention du coût (``cout.py``, ``pib_projete``), sans quoi la part
    gardée n'y serait pas la même."""
    attendu = restitution.assiette.pib(2025) * (1 + restitution.macro.pib_nominal(2026))
    assert restitution.pib_de_la_trajectoire(2026) == pytest.approx(attendu, rel=1e-12)
    assert restitution.pib_de_la_trajectoire(2025) == restitution.assiette.pib(2025)


def test_avant_la_bascule_rien_n_est_garde(restitution):
    """Le coût ne garde la part de TVA qu'à compter de la bascule."""
    part = restitution.annuelle(2025)
    assert part.tva_gardee == 0.0
    assert part.poste_abandonne == restitution.poste_affecte(2025)


def test_sans_la_part_gardee_tout_le_poste_est_partage():
    """Le réglage ``tva_des_retraites_gardee`` à faux rend tout le poste."""
    sans = Restitution(PARAMETRES.racine_donnees, 0.5, tva_gardee=False).annuelle(2026)
    assert sans.tva_gardee == 0.0
    assert sans.poste_abandonne == pytest.approx(
        Restitution(PARAMETRES.racine_donnees, 0.5).poste_affecte(2026)
        - sans.cta_supprimee)


def test_le_raccourci_suit_la_bascule_et_le_reglage():
    """La fiche de paie reçoit la même chose que la page."""
    racine = PARAMETRES.racine_donnees
    assert points_csg_rendus(racine, 2026, 0.5, 2026, True) == pytest.approx(
        Restitution(racine, 0.5, 2026, True).annuelle(2026).points_csg)
    assert points_csg_rendus(racine, 2026, 0.5, 2030, True) == pytest.approx(
        Restitution(racine, 0.5, 2030, True).annuelle(2026).points_csg)
    assert points_csg_rendus(racine, 2026, 0.5, 2026, False) == pytest.approx(
        Restitution(racine, 0.5, tva_gardee=False).annuelle(2026).points_csg)


def test_la_bascule_par_defaut_est_celle_des_reglages():
    """Le raccourci sans bascule prend celle des réglages de référence."""
    from retraite_notionnelle.restitution import ANNEE_BASCULE
    assert ANNEE_BASCULE == PARAMETRES.annee_bascule


def _node(script: str) -> object:
    """Ce que le portage rend, lu par ``node`` depuis la racine du dépôt."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    sortie = subprocess.run(["node", "--input-type=module", "-e", script], cwd=racine,
                            capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(sortie.stdout)


def test_le_portage_retranche_la_meme_part_de_tva():
    """Le site et la fiche de paie partagent ce que le Python partage, au bit
    près : la part gardée vient du paquet, que la fabrique a calculée."""
    lu = _node("""
        import { readFileSync } from "node:fs";
        import { Restitution, pointsCsgRendus } from "./moteur/js/restitution.js";
        const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf-8"));
        const r = new Restitution(paquet, 0.5, 2026, true);
        const sortie = {};
        for (const a of [2025, 2026, 2027, 2050]) {
          const l = r.annuelle(a);
          sortie[a] = [l.posteAbandonne, l.tvaGardee, l.ctaSupprimee, l.pointsCsg,
                       l.eteintDeDette];
        }
        sortie.sans = pointsCsgRendus(paquet, 2026, 0.5, 2026, false);
        sortie.tard = pointsCsgRendus(paquet, 2026, 0.5, 2030, true);
        console.log(JSON.stringify(sortie));
    """)
    python = Restitution(PARAMETRES.racine_donnees, 0.5, 2026, True)
    for annee in (2025, 2026, 2027, 2050):
        l = python.annuelle(annee)
        assert lu[str(annee)] == [l.poste_abandonne, l.tva_gardee, l.cta_supprimee,
                                  l.points_csg, l.eteint_de_dette], annee
    sans = Restitution(PARAMETRES.racine_donnees, 0.5, tva_gardee=False).annuelle(2026)
    assert lu["sans"] == sans.points_csg
    assert lu["tard"] == Restitution(PARAMETRES.racine_donnees, 0.5, 2030).annuelle(
        2026).points_csg


# .. la CTA, supprimée ..........................................................
#
# Le poste du COR compte aussi la contribution tarifaire d'acheminement, que
# la CNIEG enregistre en « impôts et taxes affectés ». La proposition la
# SUPPRIME (décision 88) : elle revient aux ménages par leurs factures
# d'énergie, et la partager encore la promettrait deux fois. Le propriétaire
# l'a tranché le 21 novembre 2026.

#: La CTA recouvrée en 2025, exercice courant, en millions d'euros : comptes
#: de l'exercice 2025 de la CNIEG, section comptable « Contribution
#: tarifaire », p. 46 (2 161 807 459,00 €).
CTA_2025_MEUR = 2161.80745900

#: Le compte du COR tient le poste à sa part de PIB de 2025 en 2026 : il y
#: compte donc la CTA d'avant la baisse de taux de la CRE du 1er février 2026
#: (délibération 2026-14, 555 M€ par an). Le partage retranche la CTA que le
#: poste compte, baisse comprise, sans quoi ces 555 M€, qui n'existent plus,
#: seraient partagés : la part de PIB de 2025, reconduite.


def test_la_cta_supprimee_n_est_pas_partagee(restitution):
    """Rendu et dette somment au poste moins la TVA gardée et la CTA."""
    part = restitution.annuelle(2026)
    pib_2026 = restitution.pib_de_la_trajectoire(2026)
    assert part.cta_supprimee == pytest.approx(
        CTA_2025_MEUR / restitution.pib_de_la_trajectoire(2025), rel=1e-12)
    assert part.poste_abandonne == pytest.approx(
        restitution.poste_affecte(2026) - part.tva_gardee - part.cta_supprimee,
        rel=1e-12)
    assert part.rendu + part.eteint_de_dette == pytest.approx(
        part.poste_abandonne, rel=1e-12)


def test_la_cta_de_2025_est_celle_des_comptes_de_la_cnieg(restitution):
    """Avant la bascule rien n'est retranché ; la série porte l'observé."""
    assert restitution.cta.montant(2025) == pytest.approx(CTA_2025_MEUR, rel=1e-12)
    assert restitution.annuelle(2025).cta_supprimee == 0.0


def test_la_baisse_de_csg_de_2026_hors_tva_et_cta(restitution):
    """Un calcul posé à la main : la moitié de ce qui reste, moins les deux
    impôts supprimés, sur l'assiette."""
    poste = restitution.poste_affecte(2026)
    pib = restitution.pib_de_la_trajectoire(2026)
    reste = (poste - COMPENSATION_2026_MEUR / pib
             - CTA_2025_MEUR / restitution.assiette.pib(2025))
    supprime = restitution.part_du_poste(2026) * poste
    assiette = restitution.assiette.part_pib(restitution.assiette.annee_de_reference(2026))
    attendu = (0.5 * reste - supprime) / assiette
    assert restitution.annuelle(2026).points_csg == pytest.approx(attendu, rel=1e-12)
    assert 0.0058 < attendu < 0.0062
