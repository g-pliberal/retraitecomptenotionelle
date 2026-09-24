"""La pension du mineur, lue au texte.

La passe du 24 septembre 2026 sur la Caisse des dépôts (action 89) a lu le
décret n° 46-2769 du 27 novembre 1946 — articles 125, 127, 131, 131-1, 131-2,
136, 139 et 181 —, le décret n° 2002-800 qui a créé le coefficient de
majoration, les arrêtés qui le fixent chaque année, les tableaux « Barèmes et
revalorisations » de la Caisse des dépôts de 2024 à 2026 et la fiche du COR.
Ce fichier tient ce qu'elle a corrigé.

**La pension est un produit de trois facteurs, et la fiche n'en portait que
deux.** Trimestres × valeur du trimestre (article 131), la durée « affectée
d'un coefficient de majoration déterminé en fonction de la date de prise
d'effet de la pension » (article 131-1) : 1,473 en 2026.

**La valeur du trimestre suit les pensions, non les prix** (article 181).
Portée par les prix depuis ses ancres, elle valait 102,49 € en 2026 pour
97,15 €. Trente ans de mine liquidés en 2026 : 17 172 € par an, quand le
modèle en servait 12 299.

**Cent vingt trimestres au plus, sauf ceux d'avant cinquante-cinq ans**
(article 136), et **l'âge est cinquante-cinq ans**, cinquante pour trente ans
de services (article 127) : la fiche ouvrait la pension à cinquante ans à
tous, et comptait tous les trimestres.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.simulateur import Simulateur

LEGISLATION = Path(RACINE_DONNEES) / "reference" / "legislation"

#: Les 382,08 F de l'article 131 au 1er juillet 1992, au taux officiel.
FRANCS_PAR_EURO = 6.55957
VALEUR_1992_FRANCS = 382.08


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def _mines(simulateur: Simulateur, naissance: int, debut: float, liquidation: float):
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, sexe="H", affiliation="mineur",
        age_debut=debut, age_liquidation=liquidation)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    pension = next(p for p in resultat.pensions_par_regime if p.regime == "mines")
    return carriere, resultat, pension


# -- la valeur du trimestre ---------------------------------------------------

def test_la_valeur_du_trimestre_est_la_chaine_des_revalorisations_des_pensions():
    """Chaque ligne est la chaîne des coefficients de la Cnav depuis 1992.

    Partie des 382,08 F de l'article 131, multipliée par chaque
    revalorisation des pensions — en 2020, celle des pensions au-delà de
    2 014 € par mois, 0,3 % —, et par les 2 % du protocole du 27 septembre
    2001 au 1er janvier 2001, puis arrondie au centime à la fin : c'est ainsi
    qu'elle retombe sur toutes les valeurs publiées. Arrondie à chaque
    marche, elle donne 89,46 € en 2023, et la caisse en publie 89,47.
    """
    revalorisations = _lire(LEGISLATION / "revalorisation_pensions.csv")
    bareme = _lire(LEGISLATION / "bareme_trimestre_mines.csv")

    def coefficient(apres: str, jusqu_a: str) -> float:
        produit = 1.0
        for ligne in revalorisations:
            if not apres < ligne["date_effet"] <= jusqu_a:
                continue
            if ligne["mensuel_superieur_a"] or ligne["mensuel_au_plus"]:
                # 2020 : la tranche des pensions de plus de 2 014 € par mois.
                if ligne["mensuel_superieur_a"] != "2014" or ligne["mensuel_au_plus"]:
                    continue
            produit *= float(ligne["coefficient"])
        return produit

    valeur = VALEUR_1992_FRANCS / FRANCS_PAR_EURO
    precedente = None
    for ligne in bareme:
        if precedente is not None:
            valeur *= coefficient(precedente, ligne["date_effet"])
            if ligne["date_effet"] == "2001-01-01":
                valeur *= 1.02
        precedente = ligne["date_effet"]
        assert float(ligne["valeur_trimestre"]) == pytest.approx(round(valeur, 2), abs=1e-9), (
            ligne["date_effet"], valeur)


def test_la_table_porte_les_valeurs_que_les_textes_et_la_caisse_publient():
    """Les ancres : décret n° 2002-800, article 131 de 2015, barèmes de la
    Caisse des dépôts de 2024 à 2026, et les coefficients des arrêtés."""
    lignes = {l["date_effet"]: l for l in _lire(LEGISLATION / "bareme_trimestre_mines.csv")}
    publiees = {
        "1992-07-01": 58.25, "2001-01-01": 67.73, "2002-01-01": 69.22,
        "2013-04-01": 82.83, "2023-01-01": 89.47, "2024-01-01": 94.21,
        "2025-01-01": 96.28, "2026-01-01": 97.15,
    }
    for date, valeur in publiees.items():
        assert float(lignes[date]["valeur_trimestre"]) == valeur, date
    coefficients = {
        "2001-01-01": 1.17, "2003-01-01": 1.194, "2004-01-01": 1.2,
        "2006-01-01": 1.21, "2007-01-01": 1.228, "2008-01-01": 1.255,
        "2009-01-01": 1.287, "2010-04-01": 1.293, "2011-04-01": 1.294,
        "2012-04-01": 1.305, "2013-04-01": 1.319, "2015-10-01": 1.34,
        "2017-10-01": 1.351, "2019-01-01": 1.374, "2020-01-01": 1.395,
        "2022-01-01": 1.446, "2025-01-01": 1.454, "2026-01-01": 1.473,
    }
    for date, coefficient in coefficients.items():
        assert float(lignes[date]["coefficient"]) == coefficient, date
    # Avant le décret n° 2002-800, aucun coefficient.
    assert all(float(l["coefficient"]) == 1.0
               for date, l in lignes.items() if date < "2001-01-01")


# -- la pension ---------------------------------------------------------------

def test_trente_ans_de_mine_liquides_en_2026(simulateur):
    """120 × 1,473 × 97,15 € = 17 172,23 € par an. La fiche servait
    120 × 102,49 €, soit 12 299 €."""
    carriere, _, pension = _mines(simulateur, 1971, 25, 55)
    assert (carriere.date_liquidation.annee, carriere.date_liquidation.mois) == (2026, 1)
    assert pension.montant == pytest.approx(120 * 1.473 * 97.15, abs=1e-6)
    assert pension.detail == ("120.00 trimestres × coefficient de majoration de la "
                              "durée 1.473 × valeur du trimestre 97.15 €")


def test_la_valeur_et_le_coefficient_se_lisent_au_mois_de_l_effet(simulateur):
    """En 2009, le coefficient change au 1er janvier (arrêté du 7 mai 2009),
    la valeur au 1er avril avec la revalorisation des pensions."""
    baremes = simulateur.scenario_actuel.baremes_trimestre
    assert baremes.valeurs("mines", DateMois(2009, 3))[:2] == (76.97, 1.287)
    assert baremes.valeurs("mines", DateMois(2009, 4))[:2] == (77.74, 1.287)
    # Avant juillet 1992, la table se tait et la fiche reprend.
    assert baremes.valeurs("mines", DateMois(1992, 6)) is None


def test_au_dela_de_la_derniere_ligne(simulateur):
    """La valeur suit les prix de l'année écoulée, le coefficient le quotient
    de l'article 131-1 — salaire moyen sur prix de l'année écoulée, jamais
    moins que un —, et la fiabilité le dit."""
    actuel = simulateur.scenario_actuel
    macro = actuel.macro
    valeur, coefficient, fiabilite = actuel.baremes_trimestre.valeurs(
        "mines", DateMois(2028, 1))
    assert valeur == pytest.approx(
        97.15 * (1 + macro.inflation(2026)) * (1 + macro.inflation(2027)))
    attendu = 1.473
    for annee in (2026, 2027):
        attendu *= max(1.0, (1 + macro.salaire_moyen(annee)) / (1 + macro.inflation(annee)))
    assert coefficient == pytest.approx(attendu)
    assert fiabilite == Fiabilite.ESTIMEE


# -- le plafond et l'âge ------------------------------------------------------

@pytest.mark.parametrize("debut, liquidation, retenus", [
    (25, 55, 120),   # trente ans, le plafond tout juste
    (18, 60, 148),   # trente-sept ans avant cinquante-cinq : tous comptent
    (20, 62, 140),   # trente-cinq ans avant cinquante-cinq, sept après
    (30, 62, 120),   # trente-deux ans, dont vingt-cinq avant cinquante-cinq
])
def test_cent_vingt_trimestres_au_plus_sauf_avant_cinquante_cinq_ans(
        simulateur, debut, liquidation, retenus):
    """« Le nombre maximum de trimestres susceptibles d'être pris en compte
    pour le calcul de la pension est de cent-vingt ; toutefois, pour les
    affiliés qui ont réalisé cette durée avant l'âge de cinquante-cinq ans,
    les trimestres accomplis postérieurement sont pris en compte jusqu'à ce
    que cet âge soit atteint » (article 136)."""
    _, _, pension = _mines(simulateur, 1964, debut, liquidation)
    assert pension.detail.startswith(f"{retenus:.2f} trimestres ×"), pension.detail


@pytest.mark.parametrize("debut, liquidation, ouverte", [
    (20, 50, True),    # trente ans à cinquante ans
    (21, 50, False),   # vingt-neuf ans : il attend cinquante-cinq ans
    (30, 50, False),
    (30, 55, True),
])
def test_cinquante_cinq_ans_et_cinquante_a_trente_ans_de_services(
        simulateur, debut, liquidation, ouverte):
    """L'article 125 ouvre la pension à cinquante-cinq ans ; l'article 127
    abaisse cet âge d'un an par tranche de quatre années au fond, jusqu'à
    cinquante ans, pour qui compte trente années d'affiliation. Le modèle ne
    sait pas où le mineur a travaillé et lui prête l'âge du fond ; la fiche
    ouvrait la pension à cinquante ans à tous."""
    _, resultat, _ = _mines(simulateur, 1964, debut, liquidation)
    assert resultat.liquidation_ouverte is ouverte, resultat.motif_ouverture
