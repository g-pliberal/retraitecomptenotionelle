"""La majoration exceptionnelle des petites pensions de septembre 2023 (action
138, étape 17).

Les pensions de base du régime général, des régimes qu'il a intégrés, des
salariés agricoles et des cultes prises avant le 1er septembre 2023 au taux
plein sont majorées depuis cette date, quand l'assuré a cotisé cent vingt
trimestres tous régimes : 100 € par mois au prorata de la durée cotisée dans le
régime, sous un plafond du régime et sous celui de L. 173-2 (loi n° 2023-270,
article 18, V ; décret n° 2023-754, article 3). La fiche
``majoration_exceptionnelle_2023`` dit la règle ; ces tests rejouent les
exemples de la circulaire Cnav n° 2023-21, puis la servent à des carrières,
dans les deux moteurs.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.droit.commun import PensionRegime
from retraite_notionnelle.droit.completer import PetitePension
from retraite_notionnelle.echeancier import Echeancier
from retraite_notionnelle.revalorisation import (
    FICHE_DE_LA_MAJORATION, PensionServie, RegimeServi, faire_vivre,
    majorer_les_petites_pensions)
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]

#: Ce que les pensions de L. 161-23-1 ont reçu du 1er septembre 2023 au
#: 31 décembre 2026 : 5,3 % en 2024, 2,2 % en 2025, 0,9 % en 2026.
JUSQU_EN_2026 = 1.053 * 1.022 * 1.009


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


# -- la règle ------------------------------------------------------------------

def test_la_fiche_porte_les_parametres_du_decret(simulateur):
    """1 200 € par an, cent vingt trimestres, un plafond de 10 170,86 € par an,
    dus depuis le 1er septembre 2023, aux pensions qui ont pris effet avant ;
    aucune majoration pour les autres, qui ont le minimum relevé."""
    fiches = simulateur.scenario_actuel.fiches_datees
    avant = fiches.regle(FICHE_DE_LA_MAJORATION, "2023-08-01")
    assert avant == {"existe": True, "due_le": "2023-09-01", "montant": 1200.0,
                     "trimestres_cotises": 120, "plafond": 10170.86}
    assert not fiches.regle(FICHE_DE_LA_MAJORATION, "2023-09-01")["existe"]


# -- les exemples de la circulaire --------------------------------------------

def _majorations(simulateur, pensions: list[tuple[str, float, str]],
                 petites: list[PetitePension]) -> dict:
    """Ce que la majoration sert, le mois où elle est due, à des pensions de
    ``pensions`` — (régime, montant mensuel, type de calcul) —, telles que la
    circulaire les donne pour septembre 2023 : chacune prise le 1er août 2023,
    que rien ne revalorise jusque-là."""
    debut = date(2023, 8, 1)
    regimes = [PensionRegime(code, mensuel * 12.0, calcul, "", Fiabilite.CERTIFIEE)
               for code, mensuel, calcul in pensions]
    datees = [(p, 2023, debut, p.montant) for p in regimes]
    servis = [RegimeServi(p.regime, p.montant, 1.0, "regime_general", Fiabilite.CERTIFIEE)
              for p in regimes]
    resultat = SimpleNamespace(petites_pensions=tuple(petites), avantages_appliques=[])
    _, majorations = majorer_les_petites_pensions(
        simulateur.scenario_actuel, resultat, datees, servis,
        PensionServie(simulateur), {}, None, date(2023, 12, 31))
    return {m.regime: m for m in majorations}


def _petite(regime: str, validee: int, cotisee: int, maximum: int,
            tous_regimes: int | None = None) -> PetitePension:
    return PetitePension(regime=regime, taux_plein=True, cotisee=cotisee, validee=validee,
                         maximum=maximum,
                         cotises_tous_regimes=cotisee if tous_regimes is None else tous_regimes)


def test_la_majoration_theorique_et_le_plafond_suivent_les_durees(simulateur):
    """Circulaire, 3.1, exemple 1 : « 100 x 160/167 = 95,80 euros » ; 3.2.2 :
    « 847,57 x 160/167 = 812,04 euros », « 847,57 x 167/167 = 847,57 euros »
    pour 180 trimestres validés."""
    majoration = _majorations(simulateur, [("regime_general", 600.0, "annuites")],
                              [_petite("regime_general", 160, 160, 167)])["regime_general"]
    assert (majoration.theorique, majoration.plafond) == (95.80, 812.04)
    assert majoration.servie == 95.80
    plafond = _majorations(simulateur, [("regime_general", 600.0, "annuites")],
                           [_petite("regime_general", 180, 160, 167)])
    assert plafond["regime_general"].plafond == 847.57


def test_une_pension_au_dessus_du_plafond_n_est_pas_majoree(simulateur):
    """Circulaire, 3.2.5, exemple 1 : 167 trimestres dont 160 cotisés, une
    retraite de 910,94 € ; « (910,94 + 95,80) – 847,57 = 159,17 euros »,
    « 0 euro »."""
    majoration = _majorations(simulateur, [("regime_general", 910.94, "annuites")],
                              [_petite("regime_general", 167, 160, 167)])["regime_general"]
    assert (majoration.theorique, majoration.plafond, majoration.retenue) == (95.80, 847.57, 0.0)
    assert majoration.servie == 0.0


def test_la_liquidation_unique_majore_sous_le_plafond(simulateur):
    """Circulaire, 3.2.5, exemple 3 : liquidation unique, 170 trimestres dont
    146 cotisés, 710,94 € ; « 100 x (146/167) = 87,42 euros », retenue
    entière."""
    majoration = _majorations(simulateur, [("regime_general", 710.94, "annuites")],
                              [_petite("regime_general", 170, 146, 167)])["regime_general"]
    assert (majoration.theorique, majoration.plafond, majoration.retenue) == (87.42, 847.57, 87.42)
    assert majoration.servie == 87.42


def test_chaque_regime_d_avant_la_liquidation_unique_doit_sa_part(simulateur):
    """Circulaire, 3.2.5, exemple 2, et 3.3.4, exemple 1 : le régime général,
    120 trimestres dont 115 cotisés, 740 € ; l'ex-RSI, 55 dont 50, 250 € ;
    durée de 165 trimestres ; 250 € d'Agirc-Arrco et 40 € de RCI. Le régime
    général : 69,69 €, plafond de 616,41 €, rien ; l'ex-RSI : 30,30 €, plafond
    de 282,52 €, servis, sous les 1 352,23 € tous régimes."""
    majorations = _majorations(
        simulateur,
        [("regime_general", 740.0, "annuites"), ("rsi", 250.0, "annuites"),
         ("agirc_arrco", 250.0, "points"), ("rci", 40.0, "points")],
        [_petite("regime_general", 120, 115, 165, 165), _petite("rsi", 55, 50, 165, 165)])
    general, independants = majorations["regime_general"], majorations["rsi"]
    assert (general.theorique, general.plafond, general.servie) == (69.69, 616.41, 0.0)
    assert (independants.theorique, independants.plafond) == (30.30, 282.52)
    assert independants.servie == 30.30


def test_le_plafond_du_regime_rogne_ce_qui_le_depasse(simulateur):
    """Circulaire, 3.3.4, exemple 2 : liquidation unique, 150 trimestres dont
    147 cotisés, 710,94 € ; 170 € de la CIPAV et 300 € de complémentaires ;
    « 88,02 – 37,67 = 50,35 euros », que le plafond tous régimes laisse."""
    majorations = _majorations(
        simulateur,
        [("regime_general", 710.94, "annuites"), ("cnavpl", 170.0, "points"),
         ("agirc_arrco", 300.0, "points")],
        [_petite("regime_general", 150, 147, 167)])
    majoration = majorations["regime_general"]
    assert (majoration.theorique, majoration.plafond) == (88.02, 761.29)
    assert (majoration.retenue, majoration.servie) == (50.35, 50.35)


def test_le_plafond_tous_regimes_ecrete_au_prorata_des_majorations(simulateur):
    """Au-delà des 1 352,23 € de septembre 2023, le dépassement s'impute à
    chaque régime au prorata de sa majoration retenue (décret n° 2023-754,
    article 3, II) : 40 € de trop sur 60 € et 30 € retenus en laissent 33,33 €
    et 16,66 €."""
    majorations = _majorations(
        simulateur,
        [("regime_general", 500.0, "annuites"), ("rsi", 300.0, "annuites"),
         ("agirc_arrco", 502.23, "points")],
        [_petite("regime_general", 160, 96, 160, 144), _petite("rsi", 160, 48, 160, 144)])
    assert majorations["regime_general"].retenue == 60.0
    assert majorations["rsi"].retenue == 30.0
    assert majorations["regime_general"].servie == pytest.approx(33.33, abs=1e-9)
    assert majorations["rsi"].servie == pytest.approx(16.66, abs=1e-9)


# -- servie à des carrières ----------------------------------------------------

def _carriere(simulateur, naissance: int = 1953, age: float = 62, niveau: float = 0.45,
              debut: float = 20, **kwargs):
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=debut, age_liquidation=age, niveau_salaire=niveau,
        profil_carriere="plat", **kwargs)
    return carriere, simulateur.scenario_actuel.calculer(carriere)


def _generale(simulateur, annee: int) -> RegimeServi:
    carriere, resultat = _carriere(simulateur)
    vivante = faire_vivre(simulateur, carriere, resultat, annee)
    return next(r for r in vivante.regimes if r.regime == "regime_general"), vivante


def test_la_pension_au_minimum_partie_avant_septembre_2023_est_majoree(simulateur):
    """Partie en février 2015 au minimum contributif majoré, avec 168
    trimestres cotisés : 100 € par mois en septembre 2023, moins le centime
    dont sa pension sans surcote dépasse le plafond, puis revalorisés comme
    elle. Rien avant septembre 2023."""
    avant, _ = _generale(simulateur, 2022)
    assert avant.majoration == 0.0
    en_2023, vivante = _generale(simulateur, 2023)
    (majoration,) = vivante.majorations
    assert (majoration.date, majoration.theorique, majoration.plafond) == (
        "2023-09-01", 100.0, 847.57)
    assert 99.0 <= majoration.servie <= 100.0
    assert en_2023.majoration == pytest.approx(majoration.servie * 12.0, abs=1e-9)
    en_2026, _ = _generale(simulateur, 2026)
    assert en_2026.majoration == pytest.approx(majoration.servie * 12.0 * JUSQU_EN_2026,
                                               rel=1e-12)
    assert en_2026.aujourd_hui == pytest.approx(
        en_2026.au_depart * en_2026.coefficient + en_2026.majoration, rel=1e-12)


def test_ni_la_pension_d_apres_ni_la_decotee_ni_la_courte_ne_le_sont(simulateur):
    """La pension de septembre 2023 et après a le minimum relevé ; la décotée
    n'est pas au taux plein ; la carrière commencée à quarante ans, au taux
    plein à 67 ans, n'a pas ses cent vingt trimestres cotisés ; une pension
    au-dessus du plafond n'a rien sous lui."""
    cas = {
        "apres": _carriere(simulateur, naissance=1961, age=62.75),
        "decotee": _carriere(simulateur, naissance=1953, age=62, debut=25),
        "courte": _carriere(simulateur, naissance=1953, age=67, debut=40),
        "haute": _carriere(simulateur, niveau=1.5),
    }
    for nom, (carriere, resultat) in cas.items():
        vivante = faire_vivre(simulateur, carriere, resultat, 2026)
        assert all(r.majoration == 0.0 for r in vivante.regimes), nom
    assert cas["apres"][0].date_liquidation.rang >= DateMois(2023, 9).rang
    assert all(not p.taux_plein for p in cas["decotee"][1].petites_pensions)
    assert all(p.cotises_tous_regimes < 120 for p in cas["courte"][1].petites_pensions)


def test_l_echeancier_l_inscrit_a_sa_date_et_la_reversion_ne_la_lit_pas(simulateur):
    """Un début de composante, que la loi induit, le 1er septembre 2023 ; la
    pension de l'échéance la compte. La réversion du conjoint, elle, se
    calcule sans elle (circulaire, 5.1.3.1) : la même avec ou sans la fiche."""
    carriere, _ = _carriere(simulateur, conjoint={
        "naissance": "1955-06", "sexe": "H", "mariage": "1980-06", "ressources": None,
        "invalidite": None}, deces="2025-03")
    echeancier = Echeancier(simulateur)
    journal = echeancier.parcourir(carriere, 2026)
    entrees = {e.id: e for e in journal}
    evenement = entrees["majoration_exceptionnelle_" + carriere.personne]
    assert (evenement.debut, evenement.contenu.sorte, evenement.contenu.origine) == (
        "2023-09-01", "debut_de_composante", "induit")
    composante = entrees["majoration_exceptionnelle_regime_general"].contenu
    assert 99.0 * 12 <= composante["montant"]["annuel"] <= 100.0 * 12
    sans = Simulateur()
    sans.scenario_actuel.fiches_datees = sans.scenario_actuel.fiches_datees.sans(
        FICHE_DE_LA_MAJORATION)
    temoin = Echeancier(sans)
    temoin.parcourir(carriere, 2026)
    assert temoin.reversion.donnees() == echeancier.reversion.donnees()
    assert echeancier.aujourd_hui.pension_annuelle > temoin.aujourd_hui.pension_annuelle


# -- les deux moteurs -----------------------------------------------------------

#: Des salariés au minimum, partis avant septembre 2023 ou après, au taux plein
#: ou non, avec ou sans complémentaire au-dessus du plafond tous régimes.
REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "20", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "62", "naissance": "1953", "primes": "0",
    "profil": "plat", "projection": "cor_reference", "salaire": "0.45", "sexe": "F",
    "statut": "salarie_prive_non_cadre", "stock": "prix", "table": "unisexe",
}
CAS = [
    {},
    {"salaire": "0.6"},
    {"enfants": "3"},
    {"naissance": "1948", "liquidation": "65", "salaire": "0.3"},
    {"naissance": "1961", "liquidation": "63"},
    {"debut": "25"},
    {"statut": "salarie_agricole"},
]


def test_les_deux_moteurs_servent_la_meme_majoration():
    """Le journal de l'échéancier — l'événement du 1er septembre 2023, sa
    composante, la pension de l'échéance — est le même en Python et en
    JavaScript."""
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
    majorees = [a for a in attendus
                if any(e["id"].startswith("majoration_exceptionnelle_")
                       for e in a.get("journal", []))]
    assert majorees, "aucune requête n'est majorée"
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
