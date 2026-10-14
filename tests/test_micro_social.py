"""Les trimestres du micro-entrepreneur, validés sur le revenu que sa
cotisation achète (action 138, étape 12 ; fiche ``micro_social_abattement``).

La caisse ne valide pas sur le revenu abattu de L. 613-7, II : elle prend le
chiffre d'affaires fois le taux global (D. 613-4), fois la part de base
(D. 613-6), divisé par le taux de base (D. 633-3), et compare ce « revenu
cotisé » à 150 SMIC horaires (circulaire Cnav n° 2024-23, point 4). Les
exemples sont ceux de service-public (F23369, vérifié le 1er avril 2026) et
de la circulaire.
"""

import json
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier, salaire_moyen_annuel
from retraite_notionnelle.donnees.chargement import (
    charger_validation_micro,
    charger_yaml,
    rapport_validation_micro,
)
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.saisie import ABATTEMENTS_MICRO

RACINE = Path(__file__).resolve().parents[1]
DONNEES = RACINE / "data"


@pytest.fixture(scope="module")
def macro():
    return DonneesMacro(DONNEES)


def _ligne(macro, statut, micro, activite, chiffre_d_affaires, annee):
    """La ligne ``annee`` d'un micro-entrepreneur né en 1975 dont le chiffre
    d'affaires annuel vaut ``chiffre_d_affaires`` cette année-là."""
    abattu = chiffre_d_affaires * (1.0 - ABATTEMENTS_MICRO[activite])
    niveau = abattu / salaire_moyen_annuel(macro, annee)
    carriere = Carriere.depuis_parcours(
        1975, "H", [Metier(statut, 20.0, niveau, micro=micro)], 64.0, macro,
        profil_carriere="plat")
    [ligne] = [l for l in carriere.lignes if l.annee == annee]
    return ligne


def test_les_abattements_de_la_table_sont_ceux_de_la_saisie():
    table = charger_yaml(DONNEES / "reference" / "legislation" / "micro_social.yaml")
    assert table["abattements"] == ABATTEMENTS_MICRO


def test_le_rapport_refait_le_calcul_de_service_public():
    """12,3 % × 43,45 % / 17,87 % du chiffre d'affaires en 2026, pour la vente,
    rapportés au revenu abattu (29 %)."""
    table = charger_validation_micro(DONNEES)
    assert rapport_validation_micro(table, "vente", 2026) == pytest.approx(
        0.123 * 0.4345 / 0.1787 / 0.29, rel=1e-12)
    assert rapport_validation_micro(table, "cipav", 2026) == pytest.approx(
        0.232 * 0.243 / 0.0873 / 0.66, rel=1e-12)
    # 2024 change de taux au 1er juillet pour le libéral : la moyenne des mois.
    assert rapport_validation_micro(table, "liberal", 2024) == pytest.approx(
        (0.211 * 0.555 + 0.231 * 0.5075) / 2 / 0.1775 / 0.66, rel=1e-12)
    # Avant 2023, la règle n'est pas lue : le revenu abattu valide. Au-delà de
    # 2026, la dernière version vaut.
    assert rapport_validation_micro(table, "vente", 2022) is None
    assert rapport_validation_micro(table, "vente", 2040) == rapport_validation_micro(
        table, "vente", 2026)


@pytest.mark.parametrize("statut,activite,chiffre_d_affaires,trimestres,avant", [
    # 12 100 € de ventes : 3 619 € de revenu cotisé, deux trimestres, quand le
    # revenu abattu, 3 509 €, n'en validait qu'un.
    ("micro_entrepreneur", "vente", 12100.0, 2, 1),
    ("micro_entrepreneur", "services", 12100.0, 3, 3),
    ("micro_entrepreneur", "liberal", 12100.0, 4, 4),
    # La Cipav : « 2 792 € » de recettes valident un trimestre (F23369), un
    # seuil arrondi — 1 803 € de revenu cotisé en demandent 2 792,002 — ; le
    # revenu abattu en validait trois, par l'assiette minimale du libéral,
    # que le micro-entrepreneur ne subit pas.
    ("profession_liberale", "cipav", 2793.0, 1, 3),
])
def test_les_exemples_de_service_public_en_2026(macro, statut, activite,
                                                 chiffre_d_affaires, trimestres, avant):
    ligne = _ligne(macro, statut, activite, activite, chiffre_d_affaires, 2026)
    assert ligne.trimestres_valides == trimestres
    assert ligne.assiette_minimale_base == 0.0
    sans = _ligne(macro, statut, "", activite, chiffre_d_affaires, 2026)
    assert sans.trimestres_valides == avant


def test_l_exemple_de_la_circulaire_en_2023(macro):
    """6 220 € de ventes en 2023 : 1 802,82 € de revenu cotisé, un trimestre
    (circulaire Cnav n° 2024-23, point 4)."""
    assert _ligne(macro, "micro_entrepreneur", "vente", "vente", 6220.0,
                  2023).trimestres_valides == 1


def test_le_paquet_porte_la_table_du_python():
    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    attendu = {activite: {str(annee): rapport for annee, rapport in par_annee.items()}
               for activite, par_annee in charger_validation_micro(DONNEES).items()}
    assert paquet["validation_micro"] == attendu
