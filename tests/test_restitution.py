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
