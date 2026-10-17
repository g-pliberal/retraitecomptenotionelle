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
    # Au-delà de 2026, la dernière version vaut.
    assert rapport_validation_micro(table, "vente", 2040) == rapport_validation_micro(
        table, "vente", 2026)


def test_de_2018_a_2022_les_clefs_que_la_cnav_applique():
    """Avant le décret n° 2022-1529, D. 613-6 ne répartit pas le forfait de
    l'Assurance retraite ; la Cnav l'affecte par des clefs — au régime de
    base, 40,31 % pour la vente, 40,36 % pour les services, 53,23 % pour le
    libéral — et valide sur ce qu'elles achètent, divisé par 17,75 %
    (circulaire Cnav n° 2025-20, annexe 1, « Clefs de répartition » de 2018 à
    2021). Les taux globaux : 12,8 % et 22 % (D. 131-5-1, puis D. 613-4)."""
    table = charger_validation_micro(DONNEES)
    assert rapport_validation_micro(table, "vente", 2018) == pytest.approx(
        0.128 * 0.4031 / 0.1775 / 0.29, rel=1e-12)
    assert rapport_validation_micro(table, "services", 2020) == pytest.approx(
        0.22 * 0.4036 / 0.1775 / 0.5, rel=1e-12)
    assert rapport_validation_micro(table, "liberal", 2021) == pytest.approx(
        0.22 * 0.5323 / 0.1775 / 0.66, rel=1e-12)
    # 2022 : neuf mois aux clefs, trois au décret n° 2022-1529.
    assert rapport_validation_micro(table, "vente", 2022) == pytest.approx(
        (9 * 0.128 * 0.4031 + 3 * 0.123 * 0.418) / 12 / 0.1775 / 0.29, rel=1e-12)
    # Avant 2018, aucune clef n'est lue : le revenu abattu valide. La Cipav
    # aussi avant octobre 2022, la règle de la CNAVPL n'étant pas lue.
    assert rapport_validation_micro(table, "vente", 2017) is None
    assert rapport_validation_micro(table, "cipav", 2022) is None


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


#: Les trimestres d'un auto-entrepreneur à jour de son forfait, de 2009 à
#: 2015, quand l'État compensait ce que le forfait ne versait pas
#: (L. 133-6-8-2, D. 131-6-4) : les tableaux des circulaires du RSI.
COMPENSATION = [
    # 2009, une année civile entière : un trimestre au moins, « quel que soit
    # le montant de son chiffre d'affaires », deux dès 12 014 € de ventes
    # (circulaire RSI n° 2009/024, point I).
    ("vente", 2009, 3000.0, 1),
    ("vente", 2009, 12014.0, 2),
    # De 2010 à 2013, rien sous 200 heures de SMIC, le seuil du trimestre :
    # 6 111 € de ventes en valident un en 2010 (circulaire RSI n° 2010/034).
    ("vente", 2010, 6111.0, 1),
    ("vente", 2010, 6000.0, 0),
    # 2014 : le trimestre vaut 150 heures, mais l'État ne compense qu'à 200,
    # et le forfait de qui relève de la maladie du RSI va tout entier à ce
    # risque : 6 573 € de ventes, 3 812 € de services, 2 888 € de recettes
    # pour le premier trimestre (circulaire RSI n° 2016/010, second tableau).
    ("vente", 2014, 6573.0, 1),
    ("vente", 2014, 6500.0, 0),
    ("services", 2014, 3812.0, 1),
    ("services", 2014, 3700.0, 0),
    ("liberal", 2014, 2888.0, 1),
    ("liberal", 2014, 2800.0, 0),
    ("vente", 2014, 9859.0, 2),
    # 2015 : la compensation à 300 heures, qui « permettra ainsi la
    # validation de deux trimestres » (circulaire RSI n° 2015/007) ; rien en
    # deçà.
    ("vente", 2015, 7000.0, 0),
    ("vente", 2015, 9942.0, 2),
]


@pytest.mark.parametrize("activite,annee,chiffre_d_affaires,trimestres", COMPENSATION)
def test_la_compensation_de_l_etat_de_2009_a_2015(macro, activite, annee,
                                                  chiffre_d_affaires, trimestres):
    ligne = _ligne(macro, "micro_entrepreneur", activite, activite,
                   chiffre_d_affaires, annee)
    assert ligne.trimestres_valides == trimestres


def test_le_trimestre_de_2009_demande_l_annee_entiere(macro):
    """« En présence d'une affiliation sur une année civile complète » ; en
    début d'activité, la table ordinaire : 3 000 € de ventes au rythme d'une
    année, de juillet à décembre 2009, ne valident rien (circulaire RSI
    n° 2009/024, point I)."""
    niveau = 3000.0 * 0.29 / salaire_moyen_annuel(macro, 2009)
    carriere = Carriere.depuis_parcours(
        1975, "H", [Metier("micro_entrepreneur", 34.5, niveau, micro="vente")], 64.0,
        macro, profil_carriere="plat")
    [ligne] = [l for l in carriere.lignes if l.annee == 2009]
    assert ligne.trimestres_valides == 0


def test_la_compensation_ne_touche_pas_la_cipav(macro):
    """Les circulaires lues sont celles du RSI : la CNAVPL valide la Cipav
    sur le revenu abattu, faute de sa règle d'alors. 2 600 € de recettes
    en 2014, 1 716 € abattus, un trimestre."""
    assert _ligne(macro, "profession_liberale", "cipav", "cipav", 2600.0,
                  2014).trimestres_valides == 1


def test_le_paquet_porte_la_compensation_du_python():
    from retraite_notionnelle.donnees.chargement import charger_compensation_micro

    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    compensation = charger_compensation_micro(DONNEES)
    assert paquet["compensation_micro"] == {
        "activites": list(compensation["activites"]),
        "plancher": {str(annee): h for annee, h in compensation["plancher"].items()},
        "seuil": {str(annee): h for annee, h in compensation["seuil"].items()},
    }


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
    # De 2018 à septembre 2022, les clefs que la Cnav applique (circulaire
    # n° 2025-20, annexe 1) : la vente, 12,8 % × 40,31 % et 12,8 % × 15,94 % ;
    # le libéral, 22 % × 53,23 %, et rien à la complémentaire.
    ("micro_entrepreneur", "vente", 2019, "regime_general", 0.128 * 0.4031,
     "rci", 0.128 * 0.1594),
    ("micro_entrepreneur", "liberal", 2021, "regime_general", 0.22 * 0.5323,
     "rci", 0.0),
    # 2022 : neuf mois aux clefs, trois au décret n° 2022-1529.
    ("micro_entrepreneur", "services", 2022, "regime_general",
     (9 * 0.22 * 0.4036 + 3 * 0.212 * 0.418) / 12, "rci",
     (9 * 0.22 * 0.1591 + 3 * 0.212 * 0.165) / 12),
    # La Cipav, depuis le décret n° 2018-1120 (D. 131-5-3, puis D. 613-6) :
    # 22 % × (25 % + 5 %) à la CNAVPL, 22 % × 20 % à la complémentaire ; du
    # 1er juillet 2021, 22,2 % × (24,80 % + 5 %) et 22,2 % × 19,80 %.
    ("profession_liberale", "cipav", 2020, "cnavpl", 0.22 * (0.25 + 0.05),
     "cipav_complementaire", 0.22 * 0.20),
    ("profession_liberale", "cipav", 2021, "cnavpl",
     (0.22 * (0.25 + 0.05) + 0.222 * (0.248 + 0.05)) / 2, "cipav_complementaire",
     (0.22 * 0.20 + 0.222 * 0.198) / 2),
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


def test_l_exemple_de_la_circulaire_en_2020(macro, simulateur):
    """6 032 € de prestations de services en 2020 : 1 327 € de forfait, dont
    535,58 € au régime de base et 211,12 € au RCI ; 3 019,72 € de revenu
    cotisé, un trimestre (circulaire Cnav n° 2025-20, annexe 1, exemple 1).
    La caisse arrondit chaque forfait trimestriel à l'euro, et chaque part au
    centime ; le modèle prend l'année entière, d'où la tolérance. Le barème
    du commerçant sur le revenu abattu en donnait 535,34 € au régime de base."""
    assert _ligne(macro, "micro_entrepreneur", "services", "services", 6032.0,
                  2020).trimestres_valides == 1
    macro = simulateur.macro
    constructeur = ConstructeurCompte(macro, simulateur.catalogue,
                                      simulateur.affiliations, simulateur.indexation,
                                      simulateur.parametres)
    niveau = 6032.0 * 0.5 / salaire_moyen_annuel(macro, 2020)
    versees = constructeur.cotisation_annuelle(Carriere.depuis_parcours(
        1975, "H", [Metier("micro_entrepreneur", 20.0, niveau, micro="services")],
        64.0, macro, profil_carriere="plat"), 2020)
    par_regime = dict(versees.par_regime)
    assert par_regime["regime_general"] == pytest.approx(535.58, rel=1e-4)
    assert par_regime["rci"] == pytest.approx(211.12, rel=1e-4)


@pytest.mark.parametrize("statut,activite,annee", [
    # Aucune clef n'est lue pour l'Assurance retraite avant 2018.
    ("micro_entrepreneur", "vente", 2017),
    # La Cipav : D. 131-5-3 ne répartit son forfait que du 13 décembre 2018.
    ("profession_liberale", "cipav", 2018),
])
def test_avant_les_clefs_le_compte_garde_le_bareme(simulateur, statut, activite, annee):
    """Sans répartition lue, le compte garde le barème sur le revenu abattu."""
    macro = simulateur.macro
    constructeur = ConstructeurCompte(macro, simulateur.catalogue,
                                      simulateur.affiliations, simulateur.indexation,
                                      simulateur.parametres)
    niveau = 11_600.0 / salaire_moyen_annuel(macro, annee)
    avec, sans = (constructeur.cotisation_annuelle(Carriere.depuis_parcours(
        1975, "H", [Metier(statut, 20.0, niveau, micro=micro)], 64.0,
        macro, profil_carriere="plat"), annee) for micro in (activite, ""))
    assert avec.cotisation == sans.cotisation
