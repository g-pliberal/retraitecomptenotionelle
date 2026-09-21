"""Ce que la grille de cas types déplace en âge, face à l'âge conjoncturel de la DREES.

`docs/limites.md` § 5 ter supposait que la grille partait « un peu plus tard
que la France réelle » et disait ne pas pouvoir le chiffrer. La série est
maintenant dans le dépôt, et la mesure dit autre chose : sur les dix-neuf
années que la DREES publie, la grille suit l'âge réel à moins d'une demi-année
près, et elle part en moyenne un peu plus TÔT. Ce qu'elle ne fait pas, c'est
suivre la montée des années récentes.

Ces bornes tiennent la mesure sans la figer au centième : ce qu'on refuse est
qu'elle change d'ordre de grandeur ou de sens sans que personne le voie.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import age_conjoncturel  # noqa: E402

SERIE = age_conjoncturel.SERIE


@pytest.fixture(scope="module")
def mesures():
    return age_conjoncturel.mesurer(Simulateur(Parametres()))


@pytest.fixture(scope="module")
def lignes_publiees():
    with SERIE.open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        return list(csv.DictReader(lignes))


def test_la_serie_de_la_drees_est_certifiee_par_sexe(lignes_publiees):
    """Trois colonnes par année, toutes certifiées, et l'ensemble entre les deux sexes."""
    par_annee: dict[int, dict[str, float]] = {}
    for ligne in lignes_publiees:
        assert ligne["fiabilite"] == "certifiee", ligne
        par_annee.setdefault(int(ligne["annee"]), {})[ligne["sexe"]] = float(ligne["age"])

    assert min(par_annee) == 2004
    for annee, serie in par_annee.items():
        assert set(serie) == {"F", "H", "ensemble"}, annee
        # Les femmes partent plus tard que les hommes sur toute la période, et
        # l'ensemble tient entre les deux : une colonne lue de travers le dirait.
        assert serie["H"] < serie["ensemble"] < serie["F"], annee
        assert 55.0 < serie["ensemble"] < 70.0, annee


def test_l_age_conjoncturel_monte_de_deux_ans_sur_la_periode(lignes_publiees):
    """2004 à 2022 : 60,59 ans puis 62,68 — c'est la marche des réformes."""
    ensemble = {int(l["annee"]): float(l["age"])
                for l in lignes_publiees if l["sexe"] == "ensemble"}
    assert ensemble[2004] == pytest.approx(60.59, abs=0.01)
    assert max(ensemble) >= 2022
    assert ensemble[max(ensemble)] - ensemble[2004] > 2.0


def test_la_grille_suit_l_age_reel_a_moins_d_une_demi_annee(mesures):
    """La réponse à la question que `limites.md` § 5 ter posait.

    Chaque année de la fenêtre est comparée, et aucune ne s'écarte d'une
    demi-année. C'est le contrôle le plus fort que le dépôt ait sur la date de
    départ de sa grille — et il porte sur dix-neuf années, pas sur une.
    """
    assert len(mesures) >= 19
    for ligne in mesures:
        assert ligne.cas_types == 13, ligne.annee
        assert abs(ligne.ecart) < 0.5, ligne


def test_la_grille_ne_part_pas_plus_tard_que_la_france_reelle(mesures):
    """L'hypothèse de `limites.md` § 5 ter n'est pas confirmée.

    Elle attendait une grille partant « un peu plus tard » ; en moyenne elle
    part un peu plus tôt. Le seuil est lâche des deux côtés : ce qui est tenu
    ici est que l'écart moyen reste une fraction d'année, pas sa décimale.
    """
    moyen = sum(ligne.ecart for ligne in mesures) / len(mesures)
    assert -0.2 < moyen <= 0.0


def test_la_grille_ne_suit_pas_la_montee_des_annees_recentes(mesures):
    """Le défaut que la mesure trouve, et qui n'était pas celui qu'on cherchait.

    Jusqu'au début des années 2010 la grille partait plutôt plus tard ; depuis,
    l'âge réel monte plus vite qu'elle. La grille ne connaît que ce que le
    droit ouvre, et la montée récente doit une part au comportement.
    """
    par_annee = {ligne.annee: ligne.ecart for ligne in mesures}
    assert par_annee[2010] > 0
    assert par_annee[max(par_annee)] < par_annee[2010]
    assert par_annee[max(par_annee)] < 0
