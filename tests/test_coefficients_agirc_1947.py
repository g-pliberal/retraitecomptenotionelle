"""Les coefficients d'anticipation et d'ajournement de l'Agirc d'avant 1955.

Fiche ``coefficients_anticipation_agirc_1947``. La convention collective
nationale du 14 mars 1947 liquide la retraite « lors de la cessation
d'activité, et, au plus tôt, à l'âge de 55 ans », la « retraite normale » à
soixante-cinq ans, et affecte les points d'un coefficient par année d'âge : de
0,40 à 0,93 avant, de 1,05 à 1,25 après (annexe I, article 6). Le modèle
servait à toute date la table des accords, 0,78 à soixante ans, et aucun
ajournement. Les accords l'ont remplacée en 1955, supposément au 1er janvier
(COR, document n° 13 du 28 janvier 2009 ; IPP).
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.droit import liquider
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
FICHE = RACINE / "data" / "reference" / "regles" / "coefficients_anticipation_agirc_1947.yaml"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _parametres() -> dict:
    fiche = yaml.safe_load(FICHE.read_text(encoding="utf-8"))
    version = next(v for v in fiche["versions"] if v["id"] == "convention_du_14_mars_1947")
    return version["contenu"]["parametres"]


def _coefficient(simulateur: Simulateur, annee: int, age: float) -> float:
    """Le coefficient des points de l'Agirc d'un cadre qui liquide à ``age``
    l'année ``annee``, sous la période de l'Agirc de cette année-là."""
    carriere = simulateur.carriere_simple(
        annee_naissance=annee - int(age), sexe="H", affiliation="salarie_prive_cadre",
        age_debut=25, age_liquidation=age)
    periode = simulateur.catalogue["agirc"].periode(annee)
    return liquider.abattement_points(
        simulateur.scenario_actuel, periode, carriere, 120, 120, age, annee)


def test_la_table_du_moteur_est_celle_que_la_fiche_cite():
    """L'anticipation est la table de l'article 6, ligne pour ligne ; son
    ajournement, 5 % par année révolue au-delà de soixante-cinq ans jusqu'à
    1,25, ce que les périodes de 1947 à 1954 servent par la majoration par âge
    seul."""
    parametres = _parametres()
    assert liquider._COEFFICIENTS_CONVENTION_1947 == {
        int(age): coefficient for age, coefficient in parametres["anticipation"].items()}
    assert {int(age): coefficient for age, coefficient in parametres["ajournement"].items()} == {
        66: 1.05, 67: 1.10, 68: 1.15, 69: 1.20, 70: 1.25}
    assert (parametres["age_minimum"], parametres["age_normal"]) == (55, 65)


@pytest.mark.parametrize("age, attendu", [
    (55, 0.40), (56, 0.47), (57, 0.54), (58, 0.61), (59, 0.66), (59.9, 0.66),
    (60, 0.72), (61, 0.76), (62, 0.81), (62.75, 0.81), (63, 0.87), (64, 0.93), (64.99, 0.93),
    (65, 1.0), (65.9, 1.0), (66, 1.05), (67, 1.10), (67.5, 1.10), (68, 1.15), (69, 1.20),
    (70, 1.25), (72, 1.25),
])
def test_un_cadre_parti_en_1950_prend_la_ligne_de_son_age(simulateur, age, attendu):
    """L'âge révolu : parti à soixante-deux ans et neuf mois, 0,81, la ligne de
    soixante-deux ans, quand la table des accords lui servait 0,91 ; à
    soixante-sept ans et demi, 1,10 ; « 70 ans et au delà », 1,25."""
    assert _coefficient(simulateur, 1950, age) == pytest.approx(attendu)


@pytest.mark.parametrize("annee", [1947, 1951, 1952, 1953, 1954])
def test_la_table_vaut_de_1947_a_1954(simulateur, annee):
    assert _coefficient(simulateur, annee, 60) == pytest.approx(0.72)
    assert _coefficient(simulateur, annee, 68) == pytest.approx(1.15)


@pytest.mark.parametrize("age, attendu", [
    (60, 0.78), (62.75, 0.91), (64, 0.96), (65, 1.0), (66, 1.0), (70, 1.0),
])
def test_des_1955_la_table_des_accords_et_plus_d_ajournement(simulateur, age, attendu):
    assert _coefficient(simulateur, 1955, age) == pytest.approx(attendu)


def test_la_pension_d_un_cadre_de_1882_parti_a_67_ans_est_majoree(simulateur):
    """La formule affichée dit le coefficient : le cadre né en 1882, parti en
    1949 à soixante-sept ans, 1,10 ; celui de 1888, parti en 1948 à soixante
    ans, 0,72."""
    for naissance, age, mot in ((1882, 67, "coefficient de majoration 1.1000"),
                                (1888, 60, "coefficient d'anticipation 0.7200")):
        carriere = simulateur.carriere_simple(
            annee_naissance=naissance, sexe="H", affiliation="salarie_prive_cadre",
            age_debut=25, age_liquidation=age, niveau_salaire=2.0)
        resultat = simulateur.scenario_actuel.calculer(carriere)
        agirc = next(p for p in resultat.pensions_par_regime if p.regime == "agirc")
        assert mot in agirc.detail


def test_le_paquet_porte_la_table_aux_seules_periodes_de_1947_a_1954():
    """Le moteur JavaScript lit la table et l'ajournement dans le paquet."""
    chemin = RACINE / "scripts" / "construire_donnees.py"
    specification = importlib.util.spec_from_file_location("construire_donnees", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    agirc = next(r for r in module._regimes() if r["code"] == "agirc")
    for periode in agirc["periodes"]:
        if periode["debut"] < 1955:
            assert periode["bareme_anticipation"] == "convention_1947"
            assert (periode["surcote_points"], periode["surcote_par_trimestre"],
                    periode["surcote_pas_trimestres"], periode["surcote_age_maximum"]) == (
                "par_age_seul", 0.0125, 4, 70)
        else:
            assert "bareme_anticipation" not in periode
            assert periode["surcote_points"] == "aucune"


#: Le jumeau JavaScript, sur les mêmes âges.
_JUMEAU = """
import { coefficientConvention1947, coefficientPourAge }
  from "./moteur/js/droit/liquider.js";
const ages = JSON.parse(process.argv[1]);
const periode = { bareme_anticipation: "convention_1947" };
process.stdout.write(JSON.stringify({
  table: ages.map((age) => coefficientConvention1947(age)),
  periode: ages.map((age) => coefficientPourAge(null, periode, null, age)),
}));
"""


def test_le_portage_javascript_rend_la_meme_table():
    ages = [50 + mois / 12 for mois in range(0, 12 * 25)]
    attendu = [liquider.coefficient_convention_1947(age) for age in ages]
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU, json.dumps(ages)],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    obtenu = json.loads(execution.stdout)
    assert obtenu == {"table": attendu, "periode": attendu}
