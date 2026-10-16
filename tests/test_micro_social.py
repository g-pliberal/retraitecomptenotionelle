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
    charger_cotisation_micro,
    charger_validation_micro,
    charger_yaml,
    rapport_validation_micro,
)
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.simulateur import Simulateur
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


def test_le_paquet_porte_le_forfait_du_python():
    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    attendu = {activite: {"regimes": list(regimes),
                          "taux": {str(annee): list(taux) for annee, taux in par_annee.items()}}
               for activite, (regimes, par_annee) in charger_cotisation_micro(DONNEES).items()}
    assert paquet["cotisation_micro"] == attendu


#: Le forfait de retraite, en part du chiffre d'affaires : taux global
#: (D. 613-4) fois part de base et part complémentaire (D. 613-6), et les deux
#: régimes qui les reçoivent.
FORFAITS = [
    # Vente, 2026 : 12,3 % × 43,45 % et 12,3 % × 19,75 %.
    ("micro_entrepreneur", "vente", 2026, "regime_general", 0.123 * 0.4345,
     "rci", 0.123 * 0.1975),
    ("micro_entrepreneur", "services", 2023, "regime_general", 0.212 * 0.418,
     "rci", 0.212 * 0.165),
    # Le libéral de 2023 ne verse rien à la complémentaire : la rédaction de
    # 2022, que le Conseil d'État a annulée au 1er juin 2024 sans toucher aux
    # cotisations dues, n'en portait pas.
    ("micro_entrepreneur", "liberal", 2023, "regime_general", 0.211 * 0.555,
     "rci", 0.0),
    # 2024 : six mois sans, six mois à 23,1 % × 7,85 %.
    ("micro_entrepreneur", "liberal", 2024, "regime_general",
     (0.211 * 0.555 + 0.231 * 0.5075) / 2, "rci", 0.231 * 0.0785 / 2),
    # La Cipav verse ses deux tranches de base à la CNAVPL.
    ("profession_liberale", "cipav", 2025, "cnavpl", 0.232 * (0.2345 + 0.0535),
     "cipav_complementaire", 0.232 * 0.256),
]


@pytest.fixture(scope="module")
def simulateur():
    return Simulateur()


@pytest.mark.parametrize("statut,activite,annee,base,part_base,complementaire,"
                         "part_complementaire", FORFAITS)
def test_le_compte_porte_le_forfait_verse(simulateur, statut, activite, annee, base,
                                          part_base, complementaire,
                                          part_complementaire):
    """Le compte notionnel porte la part de retraite du forfait, et non le
    barème du commerçant ou du libéral sur le revenu abattu, qui s'en écartait
    de +39 % pour le libéral de 2023 et de +13 % pour la Cipav de 2025."""
    macro = simulateur.macro
    chiffre_d_affaires = 40_000.0
    abattu = chiffre_d_affaires * (1.0 - ABATTEMENTS_MICRO[activite])
    carriere = Carriere.depuis_parcours(
        1975, "H", [Metier(statut, 20.0, abattu / salaire_moyen_annuel(macro, annee),
                           micro=activite)], 64.0, macro, profil_carriere="plat")
    constructeur = ConstructeurCompte(macro, simulateur.catalogue,
                                      simulateur.affiliations, simulateur.indexation,
                                      simulateur.parametres)
    versees = constructeur.cotisation_annuelle(carriere, annee)
    par_regime = dict(versees.par_regime)
    assert par_regime[base] == pytest.approx(chiffre_d_affaires * part_base, rel=1e-9)
    assert par_regime.get(complementaire, 0.0) == pytest.approx(
        chiffre_d_affaires * part_complementaire, rel=1e-9)
    assert versees.cotisation == pytest.approx(
        chiffre_d_affaires * (part_base + part_complementaire), rel=1e-9)


def test_avant_2023_le_compte_garde_le_bareme(simulateur):
    """Avant le décret n° 2022-1529, D. 613-6 ne répartit pas le forfait de
    l'Assurance retraite : le compte garde le barème sur le revenu abattu."""
    macro = simulateur.macro
    constructeur = ConstructeurCompte(macro, simulateur.catalogue,
                                      simulateur.affiliations, simulateur.indexation,
                                      simulateur.parametres)
    niveau = 11_600.0 / salaire_moyen_annuel(macro, 2021)
    avec, sans = (constructeur.cotisation_annuelle(Carriere.depuis_parcours(
        1975, "H", [Metier("micro_entrepreneur", 20.0, niveau, micro=micro)], 64.0,
        macro, profil_carriere="plat"), 2021) for micro in ("vente", ""))
    assert avec.cotisation == sans.cotisation
