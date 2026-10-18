"""Les coefficients d'anticipation de l'Agirc et de l'Arrco, et ce qui en
exonère avant 1983 : le protocole du 14 juin 1976 et la structure financière.

Fiche ``coefficients_anticipation_agirc_arrco``, ses versions. Jusqu'au 31 mars
1983, l'Agirc et l'Arrco abattent à l'âge seul toute liquidation avant
soixante-cinq ans. Le protocole d'accord du 14 juin 1976 en excepte, « auprès
des régimes adhérents à l'Arrco », les travailleurs manuels et les mères de
famille ouvrières que l'article 70-2 du décret du 29 décembre 1945 met au taux
de soixante-cinq ans dès soixante ans, pour les droits qui prennent effet « à
partir du 1er juillet 1976 ». La structure financière (ASF), « créée par les
partenaires sociaux avec l'agrément de l'Etat à partir du 1er avril 1983 »
(accord du 23 décembre 1996, article 3), lève l'abattement de qui a la durée
du taux plein ; avant, les « modalités en vigueur avant le 1er avril 1983 »
(article 2). Le modèle la servait dès le 1er janvier 1983, et à toute date sur
les points de l'UNIRS, fiche fermée en 1961 ; il ne servait pas le protocole.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.droit import categories
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
FICHE = "coefficients_anticipation_agirc_arrco"
COMPLEMENTAIRES = ("agirc", "arrco", "arrco_tranche_2", "unirs")


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _coefficients(simulateur: Simulateur, naissance: int, debut: float, age: float,
                  affiliation: str = "salarie_prive_non_cadre", niveau: float = 1.0,
                  sexe: str = "H", enfants: int = 0, **titres) -> dict:
    """Le coefficient d'anticipation que la formule de chaque complémentaire
    affiche, ``None`` quand elle n'en affiche aucun ; et la date d'effet. Né le
    15 janvier : ses âges se comptent de février (R. 351-37), quelle que soit
    la présomption du jour de naissance."""
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, mois_naissance=1, jour_naissance=15, sexe=sexe,
        affiliation=affiliation, age_debut=debut, age_liquidation=age,
        niveau_salaire=niveau, nombre_enfants=enfants, invalidite=titres or None)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    lus = {}
    for pension in resultat.pensions_par_regime:
        if pension.regime in COMPLEMENTAIRES:
            trouve = re.search(r"coefficient d'anticipation ([0-9.]+)", pension.detail)
            lus[pension.regime] = float(trouve.group(1)) if trouve else None
    return {"date": str(carriere.date_liquidation), **lus}


# -- la fiche --------------------------------------------------------------------

def test_les_versions_datent_le_protocole_et_la_structure_financiere(simulateur):
    """Rien avant le 1er juillet 1976 ; le protocole, pour les seuls régimes de
    l'Arrco, jusqu'au 31 mars 1983 ; la structure financière ensuite."""
    regle = simulateur.scenario_actuel.fiches_datees.regle
    assert regle(FICHE, "1976-06-01") == {"exoneration_au_taux_plein": False,
                                          "exonerations": []}
    protocole = regle(FICHE, "1976-07-01")
    assert protocole == {
        "exoneration_au_taux_plein": False,
        "exonerations": [{
            "motifs": [categories.FICHE_DES_TRAVAILLEURS_MANUELS,
                       categories.FICHE_DES_MERES_OUVRIERES],
            "regimes": ["arrco", "arrco_tranche_2", "unirs"]}]}
    assert regle(FICHE, "1983-03-01") == protocole
    asf = regle(FICHE, "1983-04-01")
    assert asf["exoneration_au_taux_plein"] is True
    assert asf["exonerations"] == [{"motifs": ["inaptitude", *categories.FICHES_DES_CATEGORIES],
                                    "regimes": None}]
    assert regle(FICHE, "2026-10-01") == asf


# -- la structure financière, au 1er avril 1983 ------------------------------------

@pytest.mark.parametrize("age, date, attendu", [
    (61, "février 1983", 0.83),
    (61 + 1 / 12, "mars 1983", 0.83),
    (61 + 2 / 12, "avril 1983", None),
])
def test_la_structure_financiere_ne_vaut_qu_au_1er_avril_1983(simulateur, age, date, attendu):
    """Né en janvier 1922, au travail dès dix-huit ans : cent soixante-douze
    trimestres. Parti à soixante et un ans en février ou en mars 1983, ses points
    de l'Arrco, de sa tranche 2 et de l'UNIRS prennent encore le coefficient de
    son âge, 0,83 ; parti en avril, aucun (« application à compter du
    01-04-1983 », arrêté du 21 mars 1983)."""
    assert _coefficients(simulateur, 1922, 18, age) == {
        "date": date, "arrco": attendu, "arrco_tranche_2": attendu, "unirs": attendu}


def test_l_agirc_aussi(simulateur):
    """Le cadre parti en février 1983 : 0,83 à l'Agirc comme à l'Arrco."""
    assert _coefficients(simulateur, 1922, 18, 61, affiliation="salarie_prive_cadre",
                         niveau=2.0) == {"date": "février 1983", "agirc": 0.83, "arrco": 0.83}


# -- le protocole du 14 juin 1976 -----------------------------------------------

def test_l_arrco_sert_sans_coefficient_le_travailleur_manuel_de_1978(simulateur):
    """Né en 1918, au travail dès quinze ans, un travail pénible : le taux de
    soixante-cinq ans au régime général à soixante ans, en février 1978, et ses
    points de l'Arrco, de sa tranche 2 et de l'UNIRS « sans application de
    coefficients d'abattement » ; sans le travail pénible, 0,78 sur les trois."""
    assert _coefficients(simulateur, 1918, 15, 60, travail_manuel="penible") == {
        "date": "février 1978", "arrco": None, "arrco_tranche_2": None, "unirs": None}
    assert _coefficients(simulateur, 1918, 15, 60) == {
        "date": "février 1978", "arrco": 0.78, "arrco_tranche_2": 0.78, "unirs": 0.78}


def test_la_mere_de_famille_ouvriere_de_1978_de_meme(simulateur):
    """Née en 1918, trois enfants, un travail ouvrier : le taux plein du régime
    général à soixante ans, et l'Arrco sans coefficient ; avec deux enfants, ni
    l'un ni l'autre."""
    trois = _coefficients(simulateur, 1918, 20, 60, sexe="F", enfants=3,
                          travail_manuel="ouvrier")
    deux = _coefficients(simulateur, 1918, 20, 60, sexe="F", enfants=2,
                         travail_manuel="ouvrier")
    assert trois == {"date": "février 1978", "arrco": None, "arrco_tranche_2": None,
                     "unirs": None}
    assert deux == {"date": "février 1978", "arrco": 0.78, "arrco_tranche_2": 0.78,
                    "unirs": 0.78}


def test_l_agirc_ne_suit_pas_le_protocole(simulateur):
    """Le protocole ne vise que « les régimes adhérents à l'Arrco » : le cadre
    travailleur manuel de 1978 garde 0,78 à l'Agirc, et sa part de l'Arrco n'en
    a aucun."""
    assert _coefficients(simulateur, 1918, 15, 60, affiliation="salarie_prive_cadre",
                         niveau=2.0, travail_manuel="penible") == {
        "date": "février 1978", "agirc": 0.78, "arrco": None}


# -- les deux moteurs -----------------------------------------------------------

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "18", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "61", "naissance": "1922-01-15", "primes": "0",
    "profil": "plat", "projection": "cor_reference", "salaire": "1", "sexe": "H",
    "statut": "salarie_prive_non_cadre", "stock": "prix", "table": "unisexe",
}
CAS = [
    {},
    {"liquidation": "61", "liquidation_mois": "2"},
    {"statut": "salarie_prive_cadre", "salaire": "2"},
    {"naissance": "1918-01-15", "debut": "15", "liquidation": "60",
     "travail_manuel": "penible"},
    {"naissance": "1918-01-15", "debut": "15", "liquidation": "60"},
    {"naissance": "1918-01-15", "debut": "20", "liquidation": "60", "sexe": "F",
     "enfants": "3", "travail_manuel": "ouvrier"},
    {"naissance": "1918-01-15", "debut": "15", "liquidation": "60",
     "travail_manuel": "penible", "statut": "salarie_prive_cadre", "salaire": "2"},
]


def test_les_deux_moteurs_servent_les_memes_coefficients():
    """Le journal de l'échéancier — les composantes et leur formule — est le même
    en Python et en JavaScript, et la formule de l'Arrco dit le coefficient de
    février 1983."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from test_liquidation import _ecarts, _python

    requetes = [{**REQUETE, **cas} for cas in CAS]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-liquidation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus, attendus = json.loads(execution.stdout), _python(requetes)
    assert "coefficient d'anticipation 0.8300" in json.dumps(attendus[0], ensure_ascii=False)
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
