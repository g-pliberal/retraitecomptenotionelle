"""La fraction de TVA que l'Agirc-Arrco reçoit, lue à sa source (action 186, chantier 4).

La décision 79 du programme garde aux retraites « la part existante » de TVA :
celle que l'Urssaf verse à l'Agirc-Arrco pour les cotisations que la réduction
générale efface. Aucune source lue n'en publie le montant. Le rapport à la
Commission des comptes de la sécurité sociale d'octobre 2026 publie ce que la
réduction générale efface HORS des régimes de base — assurance chômage,
retraite complémentaire, FNAL — (fiche 1.6, tableau 2, p. 67), et dit que la
compensation de l'Agirc-Arrco se fait « à l'euro près » (synthèse, p. 15). La
part de l'Agirc-Arrco s'en déduit par les taux : 6,01 points sur 10,2.

Les valeurs attendues sont celles du rapport, lues sur le document le
9 novembre 2026, et le calcul que la note ``2026-11-09-qui-finance-quoi.md``
pose en « 5. » : 0,589 × 12,587 = 7,4 ; 0,589 × 18,910 = 11,1.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.compensation_agirc_arrco import (
    POINTS_AGIRC_ARRCO, POINTS_HORS_REGIMES_DE_BASE, CompensationAgircArrco,
)

RACINE = Path(__file__).resolve().parents[1]
FICHIER = RACINE_DONNEES / "reference" / "macro" / "allegements_hors_regimes_de_base.csv"
RAPPORT = ("https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/"
           "2026/CCSS-octobre-2026_assemble_VDEF.pdf")

#: Fiche 1.6, tableau 2, p. 67, en millions d'euros : la réduction générale,
#: « dont cotisations des régimes de base », « dont cotisations hors régime de
#: base », et l'ensemble. La réduction générale de 2024 et 2025 ; la réduction
#: générale dégressive unique de 2026 et 2027, en prévision.
PUBLIE = {
    2024: (26_681.0, 12_671.0, 39_352.0),
    2025: (26_529.0, 12_587.0, 39_115.0),
    2026: (54_301.0, 18_910.0, 73_211.0),
    2027: (51_722.0, 18_011.0, 69_733.0),
}


@pytest.fixture(scope="module")
def compensation() -> CompensationAgircArrco:
    return CompensationAgircArrco(RACINE_DONNEES)


def test_la_serie_porte_les_montants_publies(compensation: CompensationAgircArrco):
    """Les quatre années du tableau, telles qu'il les publie."""
    assert (compensation.premiere_annee, compensation.derniere_annee) == (2024, 2027)
    for annee, (base, hors_base, ensemble) in PUBLIE.items():
        assert compensation.allegements(annee, "regimes_de_base") == base, annee
        assert compensation.allegements(annee, "hors_regimes_de_base") == hors_base, annee
        assert compensation.allegements(annee, "ensemble") == ensemble, annee


def test_les_deux_parts_somment_a_l_ensemble_publie(compensation: CompensationAgircArrco):
    """Le tableau se recoupe lui-même : régimes de base et hors régimes de base
    font l'ensemble, au million d'arrondi près. Une faute de saisie le romprait."""
    for annee in PUBLIE:
        somme = (compensation.allegements(annee, "regimes_de_base")
                 + compensation.allegements(annee, "hors_regimes_de_base"))
        assert somme == pytest.approx(compensation.allegements(annee, "ensemble"), abs=1.0), annee


def test_la_part_de_l_agirc_arrco_est_celle_de_ses_taux():
    """4,72 points de cotisation et 1,29 de contribution d'équilibre général
    à la charge de l'employeur, sur les 10,2 points que la réduction générale
    efface hors des régimes de base."""
    assert POINTS_AGIRC_ARRCO == pytest.approx(4.72 + 1.29)
    assert POINTS_HORS_REGIMES_DE_BASE == 10.2


def test_la_tva_de_l_agirc_arrco_vaut_7_4_puis_11_1_milliards(
        compensation: CompensationAgircArrco):
    """Le calcul de la note, refait sur la source : 7,4 Md€ en 2025, 11,1 en
    2026, 10,6 en 2027. Et non « de l'ordre de 7 Md€ », 0,23 point de PIB,
    que comptait ``scripts/lectures_decision_29.py`` avant la lecture du
    rapport."""
    assert compensation.montant(2025) / 1000.0 == pytest.approx(7.4, abs=0.05)
    assert compensation.montant(2026) / 1000.0 == pytest.approx(11.1, abs=0.05)
    assert compensation.montant(2027) / 1000.0 == pytest.approx(10.6, abs=0.05)


def test_le_saut_de_2026_recoupe_l_effet_publie_de_la_reduction_unique(
        compensation: CompensationAgircArrco):
    """Le même rapport publie, à part, ce que le passage à la réduction
    générale dégressive unique retire de cotisations à l'Agirc-Arrco en 2026 :
    3,8 Md€ (fiche 1.6, tableau 3, p. 67). Le saut de la série, 3,7 Md€, le
    recoupe à 0,15 près — l'arrondi du tableau, et la baisse spontanée des
    allègements, que le saut porte aussi."""
    saut = (compensation.montant(2026) - compensation.montant(2025)) / 1000.0
    assert saut == pytest.approx(3.8, abs=0.15)


def test_hors_de_sa_fenetre_la_serie_se_tait(compensation: CompensationAgircArrco):
    """Une année que le rapport ne publie pas n'a pas de montant : qui projette
    la série dit sa convention, la série ne la devine pas."""
    for annee in (2023, 2028):
        with pytest.raises(KeyError):
            compensation.montant(annee)


def test_le_fichier_nomme_sa_source_au_manifeste():
    """« D'où vient ce chiffre » a sa réponse dans le dépôt : le fichier nomme
    son jeu, et le manifeste porte l'adresse du rapport."""
    entete = [ligne for ligne in FICHIER.read_text(encoding="utf-8").splitlines()
              if ligne.startswith("#")]
    assert any("source_id: dss_ccss_allegements_hors_base" in ligne for ligne in entete)
    manifeste = yaml.safe_load((RACINE / "data" / "sources.yaml").read_text(encoding="utf-8"))
    jeux = {jeu["id"]: jeu for institution in manifeste["institutions"].values()
            for jeu in institution.get("jeux") or []}
    jeu = jeux["dss_ccss_allegements_hors_base"]
    assert jeu["url"] == RAPPORT
    assert jeu["cible"] == "data/reference/macro/allegements_hors_regimes_de_base.csv"
