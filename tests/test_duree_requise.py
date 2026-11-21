"""La durée requise lue dans les versions de sa fiche (note de décision 0009,
étape 3, deuxième session).

Les versions de `duree_requise_par_generation` sont la source : chacune désigne
ses lignes dans `legislation/duree_requise_par_version.csv`, que le
récupérateur lit dans l'index LEGI, ou écrit une valeur pour toute génération
(`contenu.parametres.trimestres`). La table par génération,
`duree_assurance_requise.csv`, que la fabrique, le coût et la prose lisent
encore, dit la durée de chaque génération sous la version qui l'a vue partir à
l'âge légal : l'escalier de 1993 jusqu'à la génération 1942, la dernière
version au-delà. Les deux copies d'avant réforme sont parties : les droits
contrefactuels gardent la version d'avant dans une couche.
"""

from __future__ import annotations

import csv

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import droits_contrefactuels, tables_de_version
from retraite_notionnelle.donnees.chargement import charger_yaml
from retraite_notionnelle.donnees.tables_du_droit import FichesDatees

REGLES = RACINE_DONNEES / "reference" / "regles"
LEGISLATION = RACINE_DONNEES / "reference" / "legislation"
FICHE = "duree_requise_par_generation"


def _fiche() -> dict:
    return charger_yaml(REGLES / f"{FICHE}.yaml")


def _table() -> dict[str, float]:
    with (LEGISLATION / "duree_assurance_requise.csv").open(encoding="utf-8") as flux:
        return {l["generation"]: float(l["trimestres"])
                for l in csv.DictReader(l for l in flux if not l.startswith("#"))}


def test_les_versions_partagent_la_date_d_effet_dans_l_ordre_des_textes():
    versions = [(v["id"], v["bornes"]["liquidation.date_effet"]) for v in _fiche()["versions"]]
    assert [identifiant for identifiant, _ in versions] == [
        "cent_cinquante", "escalier_de_1993", "decembre_1942_au_1er_janvier_2003",
        "cent_soixante", "loi_de_2003", "loi_de_2014", "loi_de_2023", "suspension_de_2025"]
    for (_, (_, fin)), (_, (debut, _)) in zip(versions, versions[1:]):
        assert fin == debut


@pytest.mark.parametrize("version, naissance, attendu", [
    ("cent_cinquante", 1930.167, 150),   # R. 351-27 de 1985
    ("escalier_de_1993", 1933, 150),     # R. 351-45, II : né avant 1934
    ("escalier_de_1993", 1938.167, 155),  # R. 351-45, II : né en 1938
    ("escalier_de_1993", 1945, 160),     # R. 351-27 de 1993
    ("decembre_1942_au_1er_janvier_2003", 1942.917, 159),  # R. 351-45, III
    ("decembre_1942_au_1er_janvier_2003", 1942.833, 160),  # novembre : le I
    ("cent_soixante", 1938, 160),        # R. 351-45, I
    ("cent_soixante", 1950, 160),
    ("loi_de_2003", 1948, 160),          # R. 351-27 de 2009 : nés avant 1949
    ("loi_de_2003", 1950.167, 162),      # loi n° 2003-775, article 5, III
    ("loi_de_2003", 1955.167, 166),      # décret n° 2011-916
    ("loi_de_2014", 1955, 166),          # rédaction antérieure : le décret
    ("loi_de_2014", 1962.167, 168),      # L. 161-17-3 de 2014
    ("loi_de_2023", 1962.167, 169),      # L. 161-17-3 de 2023
    ("loi_de_2023", 1965.417, 172),
    ("suspension_de_2025", 1965.417, 171),  # L. 161-17-3 de 2025
    ("suspension_de_2025", 1965.083, 170),
])
def test_la_duree_de_chaque_version_est_celle_de_son_texte(version, naissance, attendu):
    valeurs = tables_de_version.par_mois(_fiche(), version, nom="trimestres")
    assert valeurs[tables_de_version.rang(naissance)] == attendu


def test_la_loi_de_2003_ne_dit_rien_des_nes_a_compter_de_1958():
    valeurs = tables_de_version.par_mois(_fiche(), "loi_de_2003", nom="trimestres")
    assert tables_de_version.rang(1958) not in valeurs
    assert valeurs[tables_de_version.rang(1957.917)] == 166


def test_la_table_par_generation_est_celle_des_versions():
    """Jusqu'à la génération 1942, l'escalier de 1993, sous lequel elles sont
    parties à soixante ans ; au-delà, la dernière version."""
    fiche = _fiche()
    escalier = tables_de_version.par_mois(fiche, "escalier_de_1993", nom="trimestres")
    en_vigueur = dict(tables_de_version.vue_de_la_duree_requise())
    for generation, trimestres in _table().items():
        mois = tables_de_version.rang(generation)
        if float(generation) < 1943:
            assert escalier[mois] == trimestres, generation
        else:
            assert en_vigueur[tables_de_version.cle(mois)] == trimestres, generation


def test_les_deux_copies_d_avant_reforme_sont_parties():
    for nom in ("duree_requise_avant_reforme_2023.csv", "duree_requise_avant_suspension.csv"):
        assert not (LEGISLATION / nom).exists(), nom


@pytest.mark.parametrize("droit, garde", [
    ("au_31_aout_2023", "loi_de_2014"),
    ("loi_2023_sans_suspension", "loi_de_2023"),
])
def test_chaque_droit_contrefactuel_garde_la_version_d_avant_sans_fin(droit, garde):
    fiches = FichesDatees(RACINE_DONNEES).fiches()
    resolues = droits_contrefactuels.fiches_resolues(
        droits_contrefactuels.DROITS[droit], fiches)
    versions = resolues[FICHE]["versions"]
    assert versions[-1]["id"] == garde
    assert versions[-1]["bornes"]["liquidation.date_effet"][1] is None
