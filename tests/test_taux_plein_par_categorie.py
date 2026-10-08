"""Les taux pleins par catégorie de L. 351-8 (action 138, étape 17).

L'ancien déporté ou interné (3°), la mère de famille ouvrière (4°), le
travailleur manuel d'avant 1983 (décret n° 45-0179, article 70-2, a) et
l'ancien combattant ou prisonnier de guerre (5° ; D. 351-2) ont le taux plein
sans la durée requise — avant le 1er avril 1983, le taux de soixante-cinq ans
dès soixante ans —, et leurs complémentaires suivent (fiches ``taux_plein_*`` ;
:mod:`retraite_notionnelle.droit.categories`).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.droit import categories
from retraite_notionnelle.saisie import ErreurSaisie, Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _regle(simulateur, nom: str, date: str) -> dict:
    return simulateur.scenario_actuel.fiches_datees.regle(nom, date)


def _pensions(simulateur, naissance: int, debut: float, age: float, sexe: str = "H",
              enfants: int = 0, niveau: float = 1.0, **invalidite) -> dict:
    """Les pensions d'une carrière d'un seul métier, salariée du privé, avec les
    titres que la saisie déclarerait."""
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, sexe=sexe, affiliation="salarie_prive_non_cadre",
        age_debut=debut, age_liquidation=age, niveau_salaire=niveau,
        nombre_enfants=enfants, invalidite=invalidite or None)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return {p.regime: p for p in resultat.pensions_par_regime}


# -- les fiches ----------------------------------------------------------------

def test_les_fiches_datent_chaque_categorie(simulateur):
    """Les déportés depuis le 1er mai 1965, dès soixante ans, puis dès l'âge légal
    en 1983 ; les mères ouvrières et les travailleurs manuels depuis le 1er
    juillet 1976 ; les anciens combattants depuis 1974."""
    deportes = categories.FICHE_DES_DEPORTES
    assert not _regle(simulateur, deportes, "1965-04-01")["existe"]
    assert _regle(simulateur, deportes, "1965-05-01")["age"] == 60
    assert _regle(simulateur, deportes, "1983-04-01")["age"] == categories.AGE_LEGAL
    meres = categories.FICHE_DES_MERES_OUVRIERES
    assert not _regle(simulateur, meres, "1976-06-01")["existe"]
    for date in ("1976-07-01", "2026-03-01"):
        regle = _regle(simulateur, meres, date)
        assert (regle["enfants"], regle["trimestres"]) == (3, 120)
    manuels = categories.FICHE_DES_TRAVAILLEURS_MANUELS
    assert [_regle(simulateur, manuels, d)["trimestres"]
            for d in ("1976-07-01", "1977-07-01", "1978-04-01")] == [172, 168, 164]
    assert not _regle(simulateur, manuels, "1983-04-01")["existe"]
    combattants = categories.FICHE_DES_ANCIENS_COMBATTANTS
    assert not _regle(simulateur, combattants, "1973-12-01")["existe"]
    assert _regle(simulateur, combattants, "1974-06-01")["age_minimum"] == 63


def _age_combattant(simulateur, date: str, naissance: int, mois: int) -> float | None:
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=62)
    regle = _regle(simulateur, categories.FICHE_DES_ANCIENS_COMBATTANTS, date)
    return categories.age_des_anciens_combattants(
        simulateur.scenario_actuel, regle, carriere, mois)


@pytest.mark.parametrize("mois, age", [(5, None), (6, 64), (17, 64), (18, 63), (30, 62),
                                       (42, 61), (54, 60), (120, 60)])
def test_les_paliers_du_decret_de_1974(simulateur, mois, age):
    """« Soixante-quatre ans pour ceux dont la durée de captivité et des services
    militaires en temps de guerre a été de six à dix-sept mois » … « Soixante ans
    […] d'au moins cinquante-quatre mois » (décret n° 74-54 ; D. 351-2)."""
    assert _age_combattant(simulateur, "1990-01-01", 1925, mois) == age


@pytest.mark.parametrize("naissance, mois, age", [
    # « il était ajouté à chaque âge de départ AC/PG prévu à l'article D351-2 CSS
    # deux années de plus » (circulaire Cnav n° 2024-29) : à la génération 1955,
    # dont l'âge légal est de 62 ans ; rien à celle de 1950, de 60 ans.
    (1955, 54, 62), (1955, 6, 66), (1950, 54, 60), (1950, 6, 64),
])
def test_la_caisse_ajoutait_deux_ans_depuis_2010(simulateur, naissance, mois, age):
    assert _age_combattant(simulateur, "2020-01-01", naissance, mois) == pytest.approx(age)


@pytest.mark.parametrize("naissance, mois, age", [
    # Le tableau de la circulaire Cnav n° 2024-29 : 66, 65, 64 ans ; 63 ans à qui
    # est né avant 1965, l'âge légal sinon ; l'âge légal dès cinquante-quatre mois,
    # celui que le dépôt donne à la génération (« 64 ans à terme »).
    (1960, 6, 66), (1960, 18, 65), (1960, 30, 64), (1960, 42, 63), (1966, 42, "legal"),
    (1960, 54, "legal"), (1966, 54, "legal"),
])
def test_le_decret_de_2024_suit_le_tableau_de_la_cnav(simulateur, naissance, mois, age):
    if age == "legal":
        carriere = simulateur.carriere_simple(
            annee_naissance=naissance, sexe="H", affiliation="salarie_prive_non_cadre",
            age_debut=20, age_liquidation=62)
        age = categories.age_legal(simulateur.scenario_actuel, carriere)
    assert _age_combattant(simulateur, "2026-03-01", naissance, mois) == pytest.approx(age)


# -- le taux --------------------------------------------------------------------

def test_l_ancien_deporte_a_le_taux_plein_sans_la_duree(simulateur):
    """Parti à soixante ans en 2010 avec trente ans d'assurance : 33,75 % sans la
    carte, 50 % avec ; l'Arrco le suit, sans coefficient d'anticipation."""
    sans = _pensions(simulateur, 1950, 30, 60)
    avec = _pensions(simulateur, 1950, 30, 60, deporte=True)
    assert "taux 33.750%" in sans["regime_general"].detail
    assert "taux 50.000%" in avec["regime_general"].detail
    assert "anticipation" in sans["arrco"].detail
    assert "anticipation" not in avec["arrco"].detail


def test_l_ancien_combattant_a_le_taux_plein_a_l_age_de_ses_mois(simulateur):
    """Trente mois de services en Algérie : le taux plein à soixante-deux ans en
    2002, sans les 160 trimestres ; à soixante et un ans, la décote."""
    a_62 = _pensions(simulateur, 1940, 24, 62, mois_de_guerre=30)["regime_general"]
    a_61 = _pensions(simulateur, 1940, 24, 61, mois_de_guerre=30)["regime_general"]
    assert "taux 50.000%" in a_62.detail
    assert "taux 50.000%" not in a_61.detail


def test_la_mere_ouvriere_de_trois_enfants_a_le_taux_plein(simulateur):
    """Trente ans d'assurance, majoration pour enfants comprise, trois enfants, un
    travail ouvrier : le taux plein à l'âge légal ; sans le travail ouvrier, ou
    avec deux enfants, la décote."""
    ouvriere = _pensions(simulateur, 1960, 30, 62, sexe="F", enfants=3,
                         travail_manuel="ouvrier")
    employee = _pensions(simulateur, 1960, 30, 62, sexe="F", enfants=3)
    deux = _pensions(simulateur, 1960, 30, 62, sexe="F", enfants=2,
                     travail_manuel="ouvrier")
    assert "taux 50.000%" in ouvriere["regime_general"].detail
    assert "taux 50.000%" not in employee["regime_general"].detail
    assert "taux 50.000%" not in deux["regime_general"].detail
    assert "anticipation" not in ouvriere["arrco"].detail


def test_le_travailleur_manuel_de_1978(simulateur):
    """Né en 1918, au travail dès quinze ans, assurances sociales d'avant 1945
    comprises : quarante-cinq ans d'assurance et un travail pénible lui donnent en
    1978 le taux de soixante-cinq ans dès soixante ans, 50 % au lieu de 25 %."""
    sans = _pensions(simulateur, 1918, 15, 60)["regime_general"]
    avec = _pensions(simulateur, 1918, 15, 60, travail_manuel="penible")["regime_general"]
    ouvrier = _pensions(simulateur, 1918, 15, 60, travail_manuel="ouvrier")["regime_general"]
    assert "taux 25.000%" in sans.detail
    assert "taux 50.000%" in avec.detail
    assert "taux 25.000%" in ouvrier.detail


# -- la saisie ------------------------------------------------------------------

def test_la_saisie_porte_les_trois_titres_et_les_reecrit():
    saisie = Saisie.depuis_requete({"naissance": "1940", "liquidation": "62",
                                    "deporte": "oui", "guerre": "30",
                                    "travail_manuel": "ouvrier"})
    assert (saisie.deporte, saisie.mois_de_guerre, saisie.travail_manuel) == (
        True, 30, "ouvrier")
    requete = saisie.requete()
    for champ in ("deporte=oui", "guerre=30", "travail_manuel=ouvrier"):
        assert champ in requete.split("&"), champ
    relue = Saisie.depuis_requete(dict(c.split("=", 1) for c in requete.split("&")))
    assert (relue.deporte, relue.mois_de_guerre, relue.travail_manuel) == (
        True, 30, "ouvrier")
    assert saisie.invalidite_declaree()["mois_de_guerre"] == 30
    with pytest.raises(ErreurSaisie):
        Saisie.depuis_requete({"naissance": "1940", "liquidation": "62", "guerre": "0"})


# -- les deux moteurs -----------------------------------------------------------

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "24", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "62", "naissance": "1940", "primes": "0",
    "profil": "plat", "projection": "cor_reference", "salaire": "1", "sexe": "H",
    "statut": "salarie_prive_non_cadre", "stock": "prix", "table": "unisexe",
}
CAS = [
    {"guerre": "30"},
    {"naissance": "1950", "debut": "30", "liquidation": "60", "deporte": "oui"},
    {"naissance": "1960", "debut": "30", "sexe": "F", "enfants": "3",
     "travail_manuel": "ouvrier"},
    {"naissance": "1918", "debut": "15", "liquidation": "60", "travail_manuel": "penible"},
    {"naissance": "1962", "liquidation": "65", "guerre": "8"},
]


def test_les_deux_moteurs_servent_les_memes_taux_pleins():
    """Le journal de l'échéancier — les composantes et leur formule — est le même
    en Python et en JavaScript."""
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
    assert "taux 50.000%" in json.dumps(attendus, ensure_ascii=False)
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
