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

from retraite_notionnelle.carriere import AnneeCarriere, Carriere, Metier, salaire_moyen_annuel
from retraite_notionnelle.droit import acquerir, compter, coordonner, liquider
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
    2021). Les taux globaux : 12,8 % et 22 % (D. 131-5-1, puis D. 613-4).
    En 2018 et en 2019, les seuils publiés valident à leur place
    (``test_les_seuils_de_2017_a_2019``) : la clef ne fait plus que le revenu
    annuel moyen."""
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
    # Avant 2018, aucune clef n'est lue : le revenu abattu vaut, et les seuils
    # publiés valident en 2017. La Cipav aussi avant octobre 2022, la règle de
    # la CNAVPL n'étant pas lue.
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


@pytest.mark.parametrize("seuil,trimestres", [
    (2_792.0, 1), (5_584.0, 2), (8_376.0, 3), (11_168.0, 4)])
def test_les_seuils_de_la_cipav_en_2026(macro, seuil, trimestres):
    """« Pour valider des trimestres de retraite, votre chiffre d'affaires
    annuel doit atteindre, en 2026, au moins 11 168 € » : 2 792, 5 584, 8 376
    et 11 168 € de recettes valident un, deux, trois et quatre trimestres
    (service-public, F23369, vérifiée le 14 octobre 2026). La fiche arrondit
    ses seuils à l'euro — 1 803 € de revenu cotisé en demandent 2 792,002 — :
    un euro de plus passe le seuil, un euro de moins le manque."""
    for recettes, valides in ((seuil + 1.0, trimestres), (seuil - 1.0, trimestres - 1)):
        assert _ligne(macro, "profession_liberale", "cipav", "cipav", recettes,
                      2026).trimestres_valides == valides


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


#: Le chiffre d'affaires qui valide un, deux, trois et quatre trimestres, de
#: 2017 à 2019 : le barème de la Cnav « Chiffre d'affaire des
#: micro-entrepreneurs validant un trimestre », source Urssaf Caisse nationale,
#: lu le 18 octobre 2026 (ventes, prestations de service BIC et BNC).
SEUILS_PUBLIES = {
    2017: {"vente": (3510, 6305, 9120, 20195), "services": (2020, 3635, 5245, 11715),
           "liberal": (2320, 4190, 6090, 8875)},
    2018: {"vente": (4085, 7185, 10250, 20430), "services": (2375, 4185, 5975, 11850),
           "liberal": (2835, 4990, 7150, 9550)},
    2019: {"vente": (4137, 7286, 10426, 20740), "services": (2412, 4239, 6071, 12030),
           "liberal": (2880, 5062, 7266, 9675)},
}


@pytest.mark.parametrize("annee,activite", [
    (annee, activite) for annee, seuils in SEUILS_PUBLIES.items() for activite in seuils])
def test_les_seuils_de_2017_a_2019(macro, annee, activite):
    """De 2016 à 2021, le forfait va d'abord à la CSG et à la CRDS, puis à la
    maladie, puis à la vieillesse de base (L. 133-6-8-3, puis L. 613-9 ;
    D. 133-4) : les seuils ne suivent aucune clef. 4 085 € de ventes valident
    un trimestre en 2018, quand la clef de 40,31 % en demande 5 099 € ;
    9 550 € de recettes libérales en valident quatre, quand elle en demande
    8 986 €. Au seuil, ses trimestres ; un euro en deçà, un de moins."""
    for trimestres, seuil in enumerate(SEUILS_PUBLIES[annee][activite], 1):
        assert _ligne(macro, "micro_entrepreneur", activite, activite, float(seuil),
                      annee).trimestres_valides == trimestres
        assert _ligne(macro, "micro_entrepreneur", activite, activite, seuil - 1.0,
                      annee).trimestres_valides == trimestres - 1


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


def test_le_paquet_porte_les_seuils_du_python():
    from retraite_notionnelle.donnees.chargement import charger_seuils_micro

    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    attendu = {activite: {str(annee): list(seuils) for annee, seuils in par_annee.items()}
               for activite, par_annee in charger_seuils_micro(DONNEES).items()}
    assert attendu and paquet["seuils_micro"] == attendu


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


def _revenu_annuel_moyen(simulateur, code, annee_naissance, age_liquidation, lignes):
    """Le revenu annuel moyen que ``code`` liquide pour un micro-entrepreneur
    dont ``lignes`` donne, par année, l'activité, le revenu abattu, la part de
    l'année et les trimestres ; et la carrière."""
    carriere = Carriere.depuis_lignes(
        annee_naissance, "H",
        [AnneeCarriere(annee=annee, revenu=abattu, affiliation="micro_entrepreneur",
                       micro=activite, fraction_annee=part, trimestres_valides=trimestres)
         for annee, activite, abattu, part, trimestres in lignes],
        age_liquidation=age_liquidation)
    annee = carriere.annee_liquidation
    periode = simulateur.catalogue[code].periode(annee)
    return carriere, liquider.salaire_de_reference(
        simulateur.scenario_actuel, code, carriere, periode, annee, True, annee_naissance)


def test_le_revenu_annuel_moyen_porte_le_revenu_cotise(simulateur):
    """Le revenu de chaque année est « celui correspondant […] aux cotisations
    versées par l'assuré au titre de cette année » (R. 351-29, I, B, que
    D. 634-3 applique aux indépendants depuis 2026 ; R. 634-1 avant) : celui
    d'un micro-entrepreneur, la part de son forfait affectée au régime de
    base, divisée par le taux de base, le « revenu cotisé » de la caisse
    (circulaire Cnav n° 2024-23, point 4 et annexe 2), et non le revenu abattu.
    40 000 € de ventes, 11 600 € abattus, portent au compte 40 000 × 12,3 % ×
    41,80 % / 17,75 % en 2023 (D. 613-4, D. 613-6, D. 633-3), et 40 000 ×
    12,3 % × 43,45 % / 17,87 % en 2026."""
    macro = simulateur.macro
    carriere, revenu_annuel_moyen = _revenu_annuel_moyen(
        simulateur, "regime_general", 1962, 65,
        [(annee, "vente", 40_000.0 * 0.29, 1.0, 4) for annee in (2023, 2026)])
    cotises = {2023: 40_000.0 * 0.123 * 0.418 / 0.1775,
               2026: 40_000.0 * 0.123 * 0.4345 / 0.1787}
    assert revenu_annuel_moyen == pytest.approx(sum(
        revenu * macro.coefficient_revalorisation_portee_au_compte(
            annee, carriere.annee_liquidation, carriere.mois_liquidation)
        for annee, revenu in cotises.items()) / len(cotises), rel=1e-12)
    # L'exemple de la circulaire : 6 220 € de ventes en 2023, « 1 802,82 € »
    # de revenu cotisé. La caisse arrondit chaque forfait trimestriel et la
    # somme des parts de l'année à l'euro ; le modèle prend l'année entière.
    carriere, revenu_annuel_moyen = _revenu_annuel_moyen(
        simulateur, "regime_general", 1962, 65, [(2023, "vente", 6_220.0 * 0.29, 1.0, 1)])
    assert revenu_annuel_moyen == pytest.approx(
        1_802.82 * macro.coefficient_revalorisation_portee_au_compte(
            2023, carriere.annee_liquidation, carriere.mois_liquidation), rel=1e-3)


@pytest.mark.parametrize("activite,trimestres,revenu_cotise", [
    # « (224,63 € + 106,88 € + 122,96 € + 192,48 €) / 17,87 % = 3 620,31 » :
    # la fiche arrondit chaque forfait trimestriel à l'euro, le modèle prend
    # l'année, 3 618,73 €.
    ("vente", 2, 3_620.31),
    ("services", 3, 6_237.05),
    # « (499 € + 238 € + 273 € + 428 €) / 17,87 % = 8 043,01 € » : la somme
    # écrite en donne 8 047 ; le résultat est celui de l'année sans arrondi,
    # 12 100 € × 25,6 % × 46,40 % / 17,87 %.
    ("liberal", 4, 8_043.01),
])
def test_les_revenus_cotises_de_service_public_en_2026(simulateur, activite, trimestres,
                                                       revenu_cotise):
    """12 100 € de chiffre d'affaires en 2026 portent au revenu annuel moyen le
    revenu cotisé que service-public calcule pour la vente, les services et
    le libéral de l'Assurance retraite (F23369, vérifiée le 14 octobre 2026)."""
    macro = simulateur.macro
    carriere, revenu_annuel_moyen = _revenu_annuel_moyen(
        simulateur, "regime_general", 1962, 65,
        [(2026, activite, 12_100.0 * (1.0 - ABATTEMENTS_MICRO[activite]), 1.0, trimestres)])
    assert revenu_annuel_moyen == pytest.approx(
        revenu_cotise * macro.coefficient_revalorisation_portee_au_compte(
            2026, carriere.annee_liquidation, carriere.mois_liquidation), rel=1e-3)


def test_le_plancher_de_2009_entre_au_revenu_annuel_moyen(simulateur):
    """En 2009, la cotisation de base retenue, payée et compensée, divisée
    par son taux, fait le revenu du revenu annuel moyen (circulaire RSI
    n° 2009/024, point III, A) ; sur une année civile entière, la
    compensation la porte au moins à la cotisation d'un trimestre, sur
    200 heures de SMIC (« 966 / 290 ») : 3 000 € de ventes, 870 € abattus,
    portent au compte 200 × 8,71 €."""
    macro = simulateur.macro
    carriere, revenu_annuel_moyen = _revenu_annuel_moyen(
        simulateur, "rsi", 1950, 60.5, [(2009, "vente", 3_000.0 * 0.29, 1.0, 1)])
    assert revenu_annuel_moyen == pytest.approx(
        200 * 8.71 * macro.coefficient_revalorisation_portee_au_compte(
            2009, carriere.annee_liquidation, carriere.mois_liquidation), rel=1e-12)


def _acquis(simulateur, affiliation, activite, chiffre_d_affaires, annee):
    """Ce que le scénario 1 inscrit, l'année ``annee``, à un micro-entrepreneur
    né en 1962 et parti à 65 ans, dont ``activite`` fait ``chiffre_d_affaires``
    cette année-là : par régime, les points de chacune des périodes de l'année,
    dans leur ordre — la première tranche, puis la seconde —, et les
    cotisations, en euros de l'année."""
    carriere = Carriere.depuis_lignes(
        1962, "H",
        [AnneeCarriere(annee=annee, affiliation=affiliation, micro=activite,
                       revenu=chiffre_d_affaires * (1.0 - ABATTEMENTS_MICRO[activite]),
                       trimestres_valides=4)],
        age_liquidation=65)
    actuel = simulateur.scenario_actuel
    coordination = coordonner.coordonner(actuel, carriere)
    droits = acquerir.acquerir(actuel, coordination, compter.compter(actuel, coordination))
    points: dict[str, list[float]] = {}
    for code, annee_du_credit, nombre, _ in droits.points:
        if annee_du_credit == annee:
            points.setdefault(code, []).append(nombre)
    prix = simulateur.macro.coefficient_prix(annee, carriere.annee_liquidation)
    cotisations: dict[str, float] = {}
    for code, annee_du_credit, montant in droits.cotisations:
        if annee_du_credit == annee:
            cotisations[code] = cotisations.get(code, 0.0) + montant / prix
    return points, cotisations


@pytest.mark.parametrize("activite,chiffre_d_affaires,annee,points_du_forfait", [
    # « (102,10 € + 48,58 € + 55,89 € + 87,49 €) / 21,726 € = 13,53 » : 12 100 €
    # de ventes en 2026, 19,75 % de chaque forfait trimestriel (service-public,
    # F23369, vérifié le 14 octobre 2026). Le barème du commerçant, 8,10 % du
    # revenu abattu, en donnait 13,08.
    ("vente", 12_100.0, 2026, 294.06 / 21.726),
    # « (175,85 € + 83,74 € + 96,30 € + 150,73 €) / 21,726 € = 23,31 » : les
    # mêmes 12 100 € en services (F23369) ; 22,56 au barème.
    ("services", 12_100.0, 2026, 506.62 / 21.726),
    # « 211 € / 17,691 € (valeur d'acquisition du point RCI en 2020) = 11,92 » :
    # 6 032 € de services en 2020, à la clef de 15,91 % (circulaire Cnav
    # n° 2025-20, annexe 1, exemple 1), que le barème reproduisait.
    ("services", 6_032.0, 2020, 211.12 / 17.691),
    # Le libéral de 2023 ne verse rien au RCI : la rédaction du 7 décembre 2022
    # de D. 613-6 ne lui affecte aucune part, et le Conseil d'État a tenu ses
    # effets passés pour définitifs. Aucun point, quand le barème en donnait 95.
    ("liberal", 40_000.0, 2023, 0.0),
    # 2024 : six mois sans part, six à 23,1 % × 7,85 % (D. 613-4 et D. 613-6,
    # du 1er juillet 2024), au prix de 2024, 20,734 €.
    ("liberal", 40_000.0, 2024, 40_000.0 * 0.231 * 0.0785 / 2 / 20.734),
])
def test_les_points_du_rci_sont_ceux_que_le_forfait_achete(simulateur, activite,
                                                         chiffre_d_affaires, annee,
                                                         points_du_forfait):
    """Le compte de points du RCI porte « les droits acquis, année par année,
    par les cotisations versées par l'assuré » (règlement du RCI, article 3),
    un point par « revenu de référence » cotisé (article 47) : celles du
    micro-entrepreneur sont la part complémentaire de son forfait (D. 613-6 ;
    la clef de la Cnav avant le décret n° 2022-1529), et non le barème du
    commerçant sur son revenu abattu. La caisse compte des points entiers, à
    l'entier inférieur pour service-public, au plus proche pour la circulaire
    (« 11,92 = 12 points ») ; le modèle garde les décimales."""
    points, _ = _acquis(simulateur, "micro_entrepreneur", activite, chiffre_d_affaires,
                        annee)
    assert sum(points.get("rci", [])) == pytest.approx(points_du_forfait, rel=1e-3,
                                                       abs=1e-9)


def test_les_points_de_la_cnavpl_sont_au_prorata_des_parts_du_forfait(simulateur):
    """Les points du régime de base des libéraux se comptent « au prorata des
    cotisations acquittées sur chacune des tranches de revenus » (D. 643-1) :
    celles du micro-entrepreneur de la Cipav sont les parts de son forfait que
    D. 613-6 affecte à la première et à la seconde tranche de D. 642-3, et non
    le barème sur son revenu abattu ; sa complémentaire reçoit la sienne.
    48 000 € de recettes en 2026, 11 136 € de forfait : « 2 706,05 / 7,53 =
    359,37 points » en première tranche, 579,07 € en seconde à 179,76 € le
    point, 3,22 points — la fiche en écrit 3,31, en divisant 595,07 € —, et
    3 418,75 € à la complémentaire, « 72,13 points » à 47,40 € (Cipav, fiche
    pratique « Cotiser pour acquérir des droits à retraite », auto-entrepreneurs,
    2026). Le barème en donnait 367,16 et 3,30 points, et 3 545,78 €."""
    points, cotisations = _acquis(simulateur, "profession_liberale", "cipav", 48_000.0,
                                  2026)
    assert points["cnavpl"] == [pytest.approx(2_706.05 / 7.53, rel=1e-3),
                                pytest.approx(579.07 / 179.76, rel=1e-3)]
    assert cotisations["cipav_complementaire"] == pytest.approx(3_418.75, rel=1e-6)
    # 2020 : D. 131-5-3 affecte 25 % du forfait de 22 % à la première tranche,
    # 5 % à la seconde et 20 % à la complémentaire ; 40 000 € de recettes y
    # versent 2 200, 440 et 1 760 €. 525 points pour la cotisation d'un
    # plafond, 41 136 €, à 8,23 % ; 25 pour celle de cinq plafonds, à 1,87 %
    # (D. 643-1 et D. 642-3, rédactions de 2015).
    points, cotisations = _acquis(simulateur, "profession_liberale", "cipav", 40_000.0,
                                  2020)
    assert points["cnavpl"] == [
        pytest.approx(525 * 2_200.0 / (41_136.0 * 0.0823), rel=1e-9),
        pytest.approx(25 * 440.0 / (5 * 41_136.0 * 0.0187), rel=1e-9)]
    assert cotisations["cipav_complementaire"] == pytest.approx(1_760.0, rel=1e-9)
