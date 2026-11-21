"""L'âge du taux plein, lu dans les versions de sa fiche (note de décision
0009, étape 3, première session).

L'âge du 1° de L. 351-8 se range en quatre versions, choisies à la date d'effet
de la pension : soixante-cinq ans depuis l'ordonnance n° 82-270 (article 9 :
« entreront en vigueur le 1er avril 1983 »), puis R. 351-27 (« l'âge prévu au
1° de l'article L. 351-8 est fixé à soixante-cinq ans ») ; du 1er juillet 2011
(loi n° 2010-1330, article 118, II), « l'âge prévu à l'article L. 161-17-2
augmenté de cinq années » ; du 1er septembre 2023 (loi n° 2023-270), « l'âge
prévu au premier alinéa de l'article L. 161-17-2 augmenté de trois années ».
Les deux dernières sont des renvois : la valeur se lit dans la version de
l'âge légal à la même date. Le premier alinéa de L. 161-17-2 fixe
soixante-quatre ans, pour les nés à compter du 1er janvier 1968, puis 1969 :
la valeur que le second renvoi nomme (``age_du_premier_alinea``).

Les âges attendus sont lus dans les textes, l'index LEGI relu le 21 novembre
2026 ; ceux du moteur, carrière par carrière, dans
``tests/js/age-du-taux-plein.test.js``.
"""

from __future__ import annotations

import copy
import csv
from datetime import date

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import droits_contrefactuels, tables_de_version
from retraite_notionnelle.donnees.tables_du_droit import FichesDatees
from retraite_notionnelle.noyau import carte, renvois

FICHE = "age_annulation_decote"
AGE_LEGAL = "age_legal_par_generation"
EFFET = "liquidation.date_effet"


@pytest.fixture(scope="module")
def fiches() -> dict:
    return carte.fiches()


@pytest.fixture(scope="module")
def preparees() -> dict:
    return FichesDatees(RACINE_DONNEES).fiches()


def _versions(fiche: dict) -> dict:
    return {v["id"]: v for v in fiche["versions"]}


def test_la_fiche_porte_cinq_versions_bornees_par_leurs_textes(fiches):
    versions = _versions(fiches[FICHE])
    bornes = {i: [str(b) for b in v["bornes"][EFFET]] for i, v in versions.items()}
    assert bornes == {
        "avant_l_ordonnance_de_1982": ["None", "1983-04-01"],
        "ordonnance_de_1982": ["1983-04-01", "1985-12-21"],
        "soixante_cinq_ans": ["1985-12-21", "2011-07-01"],
        "age_legal_plus_cinq": ["2011-07-01", "2023-09-01"],
        "premier_alinea_plus_trois": ["2023-09-01", "None"],
    }
    assert fiches[FICHE]["dates_qui_decident"] == [EFFET]
    for identifiant in ("ordonnance_de_1982", "soixante_cinq_ans"):
        assert versions[identifiant]["contenu"]["parametres"] == {"age": 65}
    assert versions["ordonnance_de_1982"]["statut"] == "supposee"
    assert versions["avant_l_ordonnance_de_1982"]["contenu"]["parametres"] == {"age": None}
    for version in versions.values():
        for texte in version.get("textes") or []:
            assert texte.get("citation") and texte.get("lu_le"), (version["id"], texte)


@pytest.mark.parametrize("version, valeur, ans", [
    ("age_legal_plus_cinq", "age", 5),
    ("premier_alinea_plus_trois", "age_du_premier_alinea", 3),
])
def test_les_deux_dernieres_versions_renvoient_a_l_age_legal(fiches, version, valeur, ans):
    contenu = _versions(fiches[FICHE])[version]["contenu"]
    assert "parametres" not in contenu
    assert contenu["renvois"] == [{"fiche": AGE_LEGAL, "valeur": valeur, "de": "assure",
                                   "date": EFFET, "ajoute": {"ans": ans}}]


def test_le_premier_alinea_fixe_soixante_quatre_ans_depuis_2023(fiches):
    """« est fixé à soixante-quatre ans pour les assurés nés à compter du
    1er janvier 1968 » (LEGIARTI000047452768), puis « 1969 »
    (LEGIARTI000053280889) : la valeur reste soixante-quatre ans."""
    versions = _versions(fiches[AGE_LEGAL])
    for identifiant in ("loi_de_2023", "suspension_de_2025"):
        assert versions[identifiant]["contenu"]["parametres"] == {"age_du_premier_alinea": 64}
    for identifiant in ("soixante_ans", "loi_de_2010", "loi_de_2011"):
        assert "age_du_premier_alinea" not in (
            versions[identifiant]["contenu"].get("parametres") or {})


def test_les_renvois_de_la_carte_tiennent(fiches):
    assert [e for e in renvois.controler(fiches) if FICHE in e] == []


def test_le_paquet_porte_les_versions_et_leurs_renvois(preparees):
    versions = _versions(preparees[FICHE])
    assert list(versions) == ["avant_l_ordonnance_de_1982", "ordonnance_de_1982", "soixante_cinq_ans",
                              "age_legal_plus_cinq", "premier_alinea_plus_trois"]
    assert versions["soixante_cinq_ans"]["parametres"] == {"age": 65}
    assert versions["soixante_cinq_ans"]["fiabilite"] == 2
    assert versions["ordonnance_de_1982"]["fiabilite"] == 1
    assert versions["age_legal_plus_cinq"]["renvois"] == [
        {"fiche": AGE_LEGAL, "valeur": "age", "de": "assure", "date": EFFET, "mois": 60}]
    assert versions["premier_alinea_plus_trois"]["renvois"] == [
        {"fiche": AGE_LEGAL, "valeur": "age_du_premier_alinea", "de": "assure",
         "date": EFFET, "mois": 36}]
    assert _versions(preparees[AGE_LEGAL])["loi_de_2023"]["parametres"] == {
        "age_du_premier_alinea": 64}


def test_le_droit_au_31_aout_2023_garde_les_deux_fiches_dans_leur_version_d_avant(preparees):
    """La couche ``sans_la_reforme_de_2023`` garde l'âge du taux plein dans
    sa version de la veille, comme l'âge légal : soixante-deux ans plus cinq."""
    resolues = droits_contrefactuels.pour_le_paquet(preparees)["au_31_aout_2023"]["fiches"]
    taux_plein = resolues[FICHE]["versions"]
    assert [v["id"] for v in taux_plein][-1] == "age_legal_plus_cinq"
    assert taux_plein[-1]["bornes"][EFFET] == ["2011-07-01", None]
    sans_suspension = droits_contrefactuels.pour_le_paquet(preparees)[
        "loi_2023_sans_suspension"]["fiches"]
    assert FICHE not in sans_suspension


def test_une_couche_qui_garde_l_age_legal_sans_l_age_du_taux_plein_est_refusee(preparees):
    """La ceinture du second piège : sous la seule version de 2011 de l'âge
    légal, la version de 2023 de l'âge du taux plein chercherait le premier
    alinéa dans une version qui ne le porte pas. La fabrique le refuse, et
    nomme les deux fiches."""
    seule = {**preparees, AGE_LEGAL: droits_contrefactuels.garder_la_version_d_avant(
        copy.deepcopy(preparees[AGE_LEGAL]), date(2023, 9, 1))}
    erreurs = droits_contrefactuels.controler_les_renvois(seule)
    assert any(f"{FICHE}.premier_alinea_plus_trois" in e and f"{AGE_LEGAL}.loi_de_2011" in e
               for e in erreurs), erreurs
    assert droits_contrefactuels.controler_les_renvois(preparees) == []


def _lignes_du_fichier() -> list[tuple[str, str]]:
    chemin = RACINE_DONNEES / "reference" / "legislation" / "age_annulation_decote.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in flux if not l.startswith("#")]
    return [(r["generation"], r["age"]) for r in csv.DictReader(lignes)]


def test_la_table_par_generation_est_la_vue_des_versions():
    """La table n'est plus une source : elle se fabrique depuis les versions,
    l'âge de chaque génération étant celui de la version sous laquelle elle
    l'atteint (``AgesAnnulationDecote.age`` du portage)."""
    vue = tables_de_version.vue_de_l_age_du_taux_plein()
    assert [(cle, f"{age:.2f}") for cle, age in vue] == _lignes_du_fichier()


@pytest.mark.parametrize("generation, age", [
    ("1900", "65.00"), ("1929", "65.00"), ("1930", "65.00"), ("1951", "65.00"), ("1951.5", "65.33"), ("1952", "65.75"),
    ("1953", "66.17"), ("1954", "66.58"), ("1955", "67.00"),
])
def test_la_vue_donne_l_age_des_textes(generation, age):
    """D. 161-2-1-9 (LEGIARTI000025089933) plus cinq, puis 64 + 3."""
    vue = dict(tables_de_version.vue_de_l_age_du_taux_plein())
    assert f"{vue[generation]:.2f}" == age
