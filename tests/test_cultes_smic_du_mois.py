"""La base forfaitaire des cultes, au SMIC de chaque mois.

Action 130, décision 13 du propriétaire (3 novembre 2026). R. 721-29 et
R. 721-30 du code de la sécurité sociale, rédaction du 21 juin 1998 : la base
« est égale, par mois, à 169 fois le montant du salaire minimum de
croissance » ; rédaction du 26 février 2004, puis R. 382-89 et R. 382-90
depuis le 1er novembre 2006 : « par mois, à la valeur horaire du salaire
minimum de croissance en vigueur, multipliée par le nombre légal d'heures de
travail mensuel en vigueur ». La caisse le fait : au relèvement du 1er
novembre 2024, « les assiettes forfaitaires respectives des cotisations
mensuelles d'assurance maladie – maternité – invalidité, vieillesse et
retraite complémentaire obligatoire des cultes [...] sont modifiées à compter
de l'échéance du 15 décembre 2024 » (circulaire de la CAVIMAC n° 2025/01 du
14 janvier 2025), celle du mois de novembre.

Les relèvements du SMIC en cours d'année, lus un à un dans l'index JORF du
dépôt, et les valeurs attendues, posées à la main : la note
``docs/feuille_de_route/130/2026-11-03-base-des-cultes-au-smic-du-mois.md``.
Même arithmétique que ``tests/js/cultes-smic-du-mois.test.js``, que le
portage, qui fait foi, passe.
"""

from __future__ import annotations

import csv

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.simulateur import Simulateur

FRANC = 6.55957

#: Les relèvements du SMIC horaire en métropole qui ne tombent pas un
#: 1er janvier, de 1998 à 2026 : la date d'effet, la valeur et le texte, lu.
RELEVEMENTS = [
    ("1998-07-01", 40.22 / FRANC, "JORFARTI000001034949"),  # décret n° 98-518, 40,22 F
    ("1999-07-01", 40.72 / FRANC, "JORFARTI000001046712"),  # décret n° 99-546, 40,72 F
    ("2000-07-01", 42.02 / FRANC, "JORFARTI000001965864"),  # décret n° 2000-589, 42,02 F
    ("2001-07-01", 43.72 / FRANC, "JORFARTI000001645920"),  # décret n° 2001-554, 43,72 F
    ("2002-07-01", 6.83, "JORFARTI000002416035"),   # décret n° 2002-941
    ("2003-07-01", 7.19, "JORFARTI000001274126"),   # décret n° 2003-564
    ("2004-07-01", 7.61, "JORFARTI000002259434"),   # décret n° 2004-633
    ("2005-07-01", 8.03, "JORFARTI000001485867"),   # décret n° 2005-719
    ("2006-07-01", 8.27, "JORFARTI000001278723"),   # décret n° 2006-751
    ("2007-07-01", 8.44, "JORFARTI000002080353"),   # décret n° 2007-1052
    ("2008-05-01", 8.63, "JORFARTI000018730835"),   # arrêté du 25 avril 2008
    ("2008-07-01", 8.71, "JORFARTI000019078958"),   # décret n° 2008-617
    ("2009-07-01", 8.82, "JORFARTI000020793254"),   # décret n° 2009-800
    ("2011-12-01", 9.19, "JORFARTI000024874233"),   # arrêté du 29 novembre 2011
    ("2012-07-01", 9.40, "JORFARTI000026083666"),   # décret n° 2012-828
    ("2021-10-01", 10.48, "JORFARTI000044126036"),  # arrêté du 27 septembre 2021
    ("2022-05-01", 10.85, "JORFARTI000045602327"),  # arrêté du 19 avril 2022
    ("2022-08-01", 11.07, "JORFARTI000046113526"),  # arrêté du 29 juillet 2022
    ("2023-05-01", 11.52, "JORFARTI000047495827"),  # arrêté du 26 avril 2023
    ("2024-11-01", 11.88, "JORFARTI000050392696"),  # décret n° 2024-951
    ("2026-06-01", 12.31, "JORFARTI000054126607"),  # arrêté du 22 mai 2026
]

#: La moyenne des douze mois, posée à la main pour chaque année.
MOYENNES = {
    1999: (6 * 6.131499 + 6 * 6.207724) / 12,
    2007: (6 * 8.27 + 6 * 8.44) / 12,
    2008: (4 * 8.44 + 2 * 8.63 + 6 * 8.71) / 12,
    2016: 9.67,
    2022: (4 * 10.57 + 3 * 10.85 + 5 * 11.07) / 12,
    2024: (10 * 11.65 + 2 * 11.88) / 12,
}

#: La base d'une année entière, en euros, posée à la main.
BASES = {
    1999: 169 * (6 * 40.22 + 6 * 40.72) / FRANC,       # 82 073,16 F
    2007: 1820 / 12 * (6 * 8.27 + 6 * 8.44),           # 15 206,10 €
    2008: 1820 / 12 * (4 * 8.44 + 2 * 8.63 + 6 * 8.71),  # 15 664,13 €
    2016: 1820 * 9.67,                                 # 17 599,40 €
    2022: 1820 / 12 * (4 * 10.57 + 3 * 10.85 + 5 * 11.07),  # 19 743,97 €
    2024: 1820 / 12 * (10 * 11.65 + 2 * 11.88),        # 21 272,77 €
}


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _releves_du_fichier() -> list[tuple[str, float]]:
    chemin = RACINE_DONNEES / "reference" / "macro" / "smic_horaire_releves.csv"
    with chemin.open(encoding="utf-8", newline="") as flux:
        lignes = csv.DictReader(l for l in flux if not l.lstrip().startswith("#"))
        return [(ligne["date_effet"], float(ligne["smic_horaire"])) for ligne in lignes]


def test_le_fichier_porte_chaque_relevement_en_cours_d_annee_depuis_1998():
    """Chaque relèvement que les textes lus fixent hors d'un 1er janvier, de
    1998 à 2026, à six décimales pour ceux en francs, comme
    ``smic_horaire.csv``."""
    lus = _releves_du_fichier()
    assert [d for d, _ in lus] == [d for d, _, _ in RELEVEMENTS]
    for (date_effet, valeur), (_, attendue, texte) in zip(lus, RELEVEMENTS):
        assert valeur == pytest.approx(attendue, abs=5e-7), (date_effet, texte)


def test_le_smic_horaire_des_mois_est_la_moyenne_des_smic_en_vigueur(simulateur):
    macro = simulateur.macro
    for annee, moyenne in MOYENNES.items():
        assert macro.smic_horaire_des_mois(annee) == pytest.approx(moyenne, abs=1e-12), annee
    # Une année sans relèvement en cours d'année, même projetée : son SMIC de
    # janvier, au bit près.
    for annee in (2016, 2017, 2040):
        assert macro.smic_horaire_des_mois(annee) == macro.smic_horaire(annee), annee


def test_la_base_forfaitaire_des_cultes_suit_le_smic_de_chaque_mois(simulateur):
    """Né le 1er janvier 1958, ministre du culte de 25 à 67 ans : 1983 à 2024
    entières ; chaque année porte au compte la somme des bases de ses mois."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1958, sexe="H", affiliation="ministre_du_culte", age_debut=25,
        age_liquidation=67, niveau_salaire=1.0, jour_naissance=1)
    for annee, base in BASES.items():
        ligne = next(l for l in carriere.lignes if l.annee == annee)
        assert ligne.fraction_annee == 1.0, annee
        periode = simulateur.catalogue["cavimac"].periode(annee)
        assert periode.smic_du_mois, annee
        assert liquider.assiette_de_reference(
            simulateur.scenario_actuel, periode, ligne) == pytest.approx(base, abs=0.01), annee


def test_seules_les_bases_forfaitaires_des_cultes_suivent_le_smic_du_mois(simulateur):
    """Avant 1998, la cotisation des cultes est fixée par arrêté, sans SMIC ;
    l'assiette plancher de la complémentaire agricole n'est pas lue ici.
    L'Arrco des cultes prélève sur la même assiette forfaitaire que la
    vieillesse (circulaire n° 2025/01) : elle suit le SMIC de chaque mois."""
    catalogue = simulateur.catalogue
    assert not catalogue["cavimac"].periode(1997).smic_du_mois
    assert all(catalogue["cavimac"].periode(a).smic_du_mois for a in (1998, 2005, 2026))
    assert not catalogue["msa_rco"].periode(2007).smic_du_mois
    assert all(catalogue["arrco_cultes"].periode(a).smic_du_mois for a in (2006, 2019, 2026))
