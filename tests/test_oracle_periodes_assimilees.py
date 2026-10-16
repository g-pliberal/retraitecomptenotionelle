"""L'oracle au-delà des carrières simples, huitième et dernière famille : les
périodes assimilées du régime général, année par année, confrontées à
OpenFisca-France-Pension (action 153, étape 2).

Le frère de ``tests/test_oracle_salaire_annuel_moyen.py``, dont il reprend la
méthode : la convention de traduction d'abord, écrite dans
``scripts/fetch/openfisca_periodes_assimilees.py`` et portée par le témoin,
puis chaque règle ; un écart connu est déclaré avec le texte qui le tranche.

OpenFisca ne compte pas les trimestres d'une période assimilée : il reçoit
ceux que le dépôt compte (``droit/compter.py``, action 130, sixième domaine),
et les mène jusqu'à la pension. Ce qui se confronte est ce qu'ils deviennent.

* **La durée** : les trimestres assimilés s'ajoutent à ceux du salaire,
  quatre par année au plus, et comptent au taux et à la proratisation. Les
  deux concordent.
* **La durée cotisée** : ils n'y entrent pas — ni à la surcote, ni à la
  majoration du minimum contributif et à son seuil de 120 trimestres. Les
  deux concordent.
* **Le salaire annuel moyen** : une année dont le salaire n'achète pas un
  trimestre en reste exclue, que des trimestres assimilés la complètent ou
  non. Les deux concordent.
* **La surcote de l'année de l'âge légal** : OpenFisca n'en compte aucune
  quand le trimestre civil qui suit l'âge commence après le 1er janvier ;
  l'écart est le sien (D. 351-1-4).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from retraite_notionnelle import chronologie
from retraite_notionnelle.carriere import Carriere, LigneRelevee
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.droit import liquider, releve
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "openfisca_periodes_assimilees.json"
MINIMUM_CONTRIBUTIF = RACINE / "data" / "reference" / "legislation" / "minimum_contributif.csv"

DUREE = "duree"
PLAFOND_ANNUEL = "plafond_annuel"
SALAIRE_ANNUEL_MOYEN = "salaire_annuel_moyen"
SURCOTE = "surcote"
MINIMUM = "minimum_contributif"

#: Les entrées d'OpenFisca que la convention doit dire, au témoin.
CONVENTION_ATTENDUE = {
    "date_de_naissance", "sexe", "liquidation_date", "salaire_de_base",
    "categorie_salarie", "periodes", "trimestres_assimiles", "comparaison",
    "non_traduit",
}

#: La majoration de 1,25 % par trimestre de surcote depuis 2009
#: (D. 351-1-4) ; le taux plein.
SURCOTE_PAR_TRIMESTRE, TAUX_PLEIN = 0.0125, 0.5
#: Né le 1er janvier 1955, soixante-deux ans le 1er janvier 2017 : D. 351-1-4
#: retient pour 2017 les trois trimestres civils entiers qui suivent le
#: premier, qu'OpenFisca ne compte pas ; le stage de 2018 n'en donne aucun.
TRIMESTRES_DE_L_ANNEE_DE_L_AGE, TRIMESTRES_DU_STAGE = 3, 4
#: Le seuil de trimestres cotisés de la majoration du minimum contributif
#: (D. 351-2-1, depuis le 1er avril 2009) ; la durée de proratisation de la
#: génération 1951.
SEUIL_MAJORATION, PRORATISATION_1951 = 120, 163

#: La décote de la génération 1957, par trimestre, en points de taux
#: (D. 351-1-2).
DECOTE_PAR_TRIMESTRE_1957 = 0.00625

_REGIME = "regime_general"
_AFFILIATION = "salarie_prive_non_cadre"


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def chronologie_du_profil(profil: dict) -> dict:
    """La chronologie que la convention décrit : un relevé dont chaque année
    valide les trimestres que son salaire achète, les années d'un contrat
    d'apprentissage marquées, et les périodes assimilées déclarées."""
    construite = chronologie.du_releve(
        annee_naissance=profil["naissance"], sexe="H", jour_naissance=1,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        releve=[LigneRelevee(annee=int(annee), affiliation=_AFFILIATION, revenu=salaire)
                for annee, salaire in sorted(profil["salaires"].items(), key=lambda x: int(x[0]))
                if salaire > 0])
    apprentissage = set(profil.get("apprentissage") or ())
    for fait in construite["faits"]:
        if fait["sorte"] == chronologie.EMPLOI and int(fait["debut"][:4]) in apprentissage:
            fait["attributs"]["apprentissage"] = True
    if profil["periodes"]:
        construite = chronologie.avec_periodes_assimilees(construite, profil["periodes"])
    return chronologie.completer(construite)


def _le_droit(simulateur: Simulateur, profil: dict) -> dict:
    """Ce que le scénario 1 rend au régime général."""
    scenario = simulateur.scenario_actuel
    carriere = Carriere.depuis_chronologie(chronologie_du_profil(profil), simulateur.macro)
    durees = releve.construire(scenario, carriere).durees
    resultat = scenario.calculer(carriere)
    base = next(p for p in resultat.pensions_par_regime if p.regime == _REGIME)
    periode = simulateur.catalogue[_REGIME].periode(profil["liquidation"])
    assimiles: dict[str, dict[str, int]] = {}
    for assimilee in durees.assimilees:
        annees = assimiles.setdefault(assimilee.motif, {})
        annees[str(assimilee.annee)] = annees.get(str(assimilee.annee), 0) + assimilee.trimestres
    return {
        "trimestres_assimiles": assimiles,
        "duree_assurance": resultat.trimestres_valides,
        "duree_cotisee": durees.cumul_plafonne("cotises", (_REGIME,)),
        "taux_de_liquidation": resultat.taux_liquidation,
        "salaire_de_reference": liquider.salaire_de_reference(
            scenario, _REGIME, carriere, periode, profil["liquidation"], True,
            profil["naissance"], True),
        "pension_brute": base.montant,
        "trimestres_du_salaire": {
            str(a): simulateur.macro.trimestres_valides(s, int(a))
            for a, s in profil["salaires"].items() if s > 0},
    }


@pytest.fixture(scope="module")
def nous(temoin, simulateur) -> dict[str, dict]:
    """Le calcul du dépôt pour chaque profil, fait une fois."""
    return {code: _le_droit(simulateur, entree["profil"])
            for code, entree in temoin["profils"].items()}


def _de_la_regle(temoin: dict, *regles: str) -> list[tuple[str, dict]]:
    return [(code, entree) for code, entree in temoin["profils"].items()
            if entree["profil"]["regle"] in regles]


def _surcote(taux: float) -> float:
    """Les trimestres de surcote qu'un taux porte, au-dessus du taux plein."""
    return (taux / TAUX_PLEIN - 1) / SURCOTE_PAR_TRIMESTRE


def _minimum_contributif(date: str) -> tuple[float, float]:
    """Le minimum contributif et le minimum majoré en vigueur à cette date
    (``minimum_contributif.csv``)."""
    valeurs: dict[str, tuple[str, float]] = {}
    with MINIMUM_CONTRIBUTIF.open(encoding="utf-8") as fichier:
        lignes = (ligne for ligne in fichier if not ligne.startswith("#"))
        for ligne in csv.DictReader(lignes):
            if ligne["date"] <= date and ligne["date"] >= valeurs.get(ligne["mesure"], ("",))[0]:
                valeurs[ligne["mesure"]] = (ligne["date"], float(ligne["valeur"]))
    return valeurs["montant_base"][1], valeurs["montant_majore"][1]


# -- la convention ---------------------------------------------------------------

def test_le_temoin_suit_sa_convention_de_traduction(temoin, nous):
    """Le témoin dit d'où il vient et porte sa convention ; chaque profil reste
    dans ce qu'OpenFisca sait faire, liquidé de 2016 à 2021 ; les trimestres
    qu'il a reçus sont ceux que le dépôt compte des périodes déclarées, année
    par année, avant le plafond de l'année ; et les deux comptent alors la
    même durée d'assurance."""
    assert temoin["source"] == "OpenFisca-France-Pension"
    assert temoin["version"]
    assert CONVENTION_ATTENDUE <= set(temoin["convention"])
    assert {e["profil"]["regle"] for e in temoin["profils"].values()} == {
        DUREE, PLAFOND_ANNUEL, SALAIRE_ANNUEL_MOYEN, SURCOTE, MINIMUM}
    for code, entree in temoin["profils"].items():
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        assert 2016 <= profil["liquidation"] <= 2021, code
        assert moi["trimestres_assimiles"] == profil["trimestres_assimiles"], code
        assert moi["duree_assurance"] == eux["duree_assurance"], code


# -- la durée --------------------------------------------------------------------

def test_les_trimestres_assimiles_comptent_a_la_duree_quatre_par_annee(temoin, nous):
    """R. 351-12 : une période assimilée valide des trimestres d'assurance,
    quatre par année au plus, tous motifs et salaire confondus. Des deux
    côtés, la durée est la somme, année par année, de ce que le salaire achète
    et de ce que les périodes valident, ramenée à quatre : six trimestres de
    stage en 2016 n'en font que quatre, et un salaire de trois trimestres
    n'en reçoit qu'un des six d'un stage."""
    for code, entree in temoin["profils"].items():
        profil, moi = entree["profil"], nous[code]
        annees: dict[str, int] = dict(moi["trimestres_du_salaire"])
        for trimestres in profil["trimestres_assimiles"].values():
            for annee, nombre in trimestres.items():
                annees[annee] = annees.get(annee, 0) + nombre
        assert moi["duree_assurance"] == sum(min(4, n) for n in annees.values()), code
    (_, plafonne), = _de_la_regle(temoin, PLAFOND_ANNUEL)
    assert plafonne["openfisca"]["duree_assurance"] == plafonne["openfisca"]["duree_cotisee"] + 3


def test_les_trimestres_assimiles_ne_sont_pas_cotises(temoin, nous):
    """Les trimestres d'une période assimilée ne sont pas cotisés : la durée
    cotisée n'en compte aucun, des deux côtés, et l'écart à la durée
    d'assurance est ce que les périodes ont ajouté."""
    for code, entree in temoin["profils"].items():
        eux, moi = entree["openfisca"], nous[code]
        assert moi["duree_cotisee"] == eux["duree_cotisee"], code
        assert moi["duree_cotisee"] == sum(
            min(4, n) for n in moi["trimestres_du_salaire"].values()), code


def test_le_taux_et_la_proratisation_concordent(temoin, nous):
    """La décote se compte sur la durée périodes assimilées comprises, et la
    proratisation aussi : sur les profils décotés par la durée, les deux rendent
    le même taux, et la même pension rapportée au salaire annuel moyen, que
    les coefficients de revalorisation laissent de côté."""
    profils = _de_la_regle(temoin, DUREE, PLAFOND_ANNUEL)
    assert len(profils) == 5
    for code, entree in profils:
        eux, moi = entree["openfisca"], nous[code]
        assert eux["decote_trimestres"] > 0, code
        assert moi["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=1e-6), code
        assert moi["pension_brute"] / moi["salaire_de_reference"] == pytest.approx(
            eux["pension_brute"] / eux["salaire_de_reference"], rel=1e-5), code


# -- le salaire annuel moyen -------------------------------------------------------

def test_une_annee_que_le_salaire_ne_valide_pas_reste_hors_du_salaire_moyen(temoin, nous):
    """R. 351-29, depuis 2004 : une année dont le salaire n'achète pas un
    trimestre n'entre pas dans la moyenne, même quand un stage lui en donne
    quatre. Les deux jumeaux, l'un à 900 € en 2016, l'autre sans salaire, ont
    le même salaire annuel moyen, des deux côtés, sur une carrière plus courte
    que les vingt-cinq années retenues. Leur décote se règle à l'âge, qu'ils
    atteignent le jour de leur départ : OpenFisca en compte un trimestre de
    trop, l'écart de la famille précédente (R. 351-27) ; le taux à part, la
    pension rapportée au salaire annuel moyen concorde."""
    (faible, a), (sans, b) = _de_la_regle(temoin, SALAIRE_ANNUEL_MOYEN)
    assert a["profil"]["salaires"]["2016"] == 900.0 and "2016" not in nous[sans]["trimestres_du_salaire"]
    assert nous[faible]["trimestres_du_salaire"]["2016"] == 0
    assert a["openfisca"]["salaire_de_reference"] == b["openfisca"]["salaire_de_reference"]
    assert nous[faible]["salaire_de_reference"] == pytest.approx(
        nous[sans]["salaire_de_reference"], abs=0.005)
    for code, entree in ((faible, a), (sans, b)):
        eux, moi = entree["openfisca"], nous[code]
        assert moi["taux_de_liquidation"] - eux["taux_de_liquidation"] == pytest.approx(
            DECOTE_PAR_TRIMESTRE_1957, abs=1e-6), code
        assert moi["pension_brute"] / moi["salaire_de_reference"] / moi["taux_de_liquidation"] == (
            pytest.approx(eux["pension_brute"] / eux["salaire_de_reference"]
                          / eux["taux_de_liquidation"], rel=1e-5)), code


# -- la surcote -------------------------------------------------------------------

def test_la_surcote_ne_compte_pas_les_trimestres_assimiles(temoin, nous):
    """L. 351-1-2 : la surcote ne compte que la durée « ayant donné lieu à
    cotisations à la charge de l'assuré ». Un an de stage après l'âge légal et
    la durée requise ôte quatre trimestres de surcote au jumeau qui travaille,
    des deux côtés."""
    profils = dict(_de_la_regle(temoin, SURCOTE))
    stage, travail = profils["surcote_et_stage"], profils["surcote_sans_stage"]
    assert (travail["openfisca"]["surcote_trimestres"] - stage["openfisca"]["surcote_trimestres"]
            == TRIMESTRES_DU_STAGE)
    assert _surcote(nous["surcote_sans_stage"]["taux_de_liquidation"]) - _surcote(
        nous["surcote_et_stage"]["taux_de_liquidation"]) == pytest.approx(TRIMESTRES_DU_STAGE)


def test_openfisca_perd_la_surcote_de_l_annee_de_l_age_legal(temoin, nous):
    """D. 351-1-4 : « il est retenu au titre de l'année au cours de laquelle
    l'assuré a atteint l'âge [légal] […] un nombre de trimestres égal au nombre
    de trimestres civils entiers suivant celui au cours duquel cet âge a été
    atteint ». Né le 1er janvier 1955, soixante-deux ans le 1er janvier 2017 :
    trois trimestres en 2017. OpenFisca n'en compte aucun l'année où le
    trimestre qui suit l'âge commence après le 1er janvier ; l'écart est le
    sien."""
    for code, entree in _de_la_regle(temoin, SURCOTE):
        eux, moi = entree["openfisca"], nous[code]
        assert eux["decote_trimestres"] == 0, code
        assert _surcote(moi["taux_de_liquidation"]) == pytest.approx(
            eux["surcote_trimestres"] + TRIMESTRES_DE_L_ANNEE_DE_L_AGE), code
        assert eux["taux_de_liquidation"] == pytest.approx(
            TAUX_PLEIN * (1 + SURCOTE_PAR_TRIMESTRE * eux["surcote_trimestres"]), abs=1e-6), code


# -- le minimum contributif ---------------------------------------------------------

def test_le_minimum_contributif_majore_les_seuls_trimestres_cotises(temoin, nous):
    """D. 351-2-1 : le minimum au prorata de la durée, la majoration au
    prorata des seuls trimestres cotisés, à qui en a 120. Les deux portent les
    deux pensions au même minimum, au centime : la base compte le stage, la
    majoration ne le compte pas — l'y compter ajouterait quatre cent
    soixante-troisièmes de la majoration —, et cent seize trimestres cotisés
    n'y ouvrent pas droit, même quand le stage porte la durée à cent vingt."""
    base, majore = _minimum_contributif("2016-01-01")
    for code, entree in _de_la_regle(temoin, MINIMUM):
        eux, moi = entree["openfisca"], nous[code]
        assert eux["pension_brute"] == eux["pension_minimale"], code
        assert moi["pension_brute"] == pytest.approx(eux["pension_minimale"], abs=0.005), code
        majoration = ((majore - base) * eux["duree_cotisee"] / PRORATISATION_1951
                      if eux["duree_cotisee"] >= SEUIL_MAJORATION else 0.0)
        attendu = base * eux["duree_assurance"] / PRORATISATION_1951 + majoration
        assert moi["pension_brute"] == pytest.approx(attendu, abs=0.5), code
        if majoration:
            avec_le_stage = (majore - base) * eux["duree_assurance"] / PRORATISATION_1951
            assert avec_le_stage - majoration > 10, code
    assert {code for code, e in _de_la_regle(temoin, MINIMUM)
            if e["openfisca"]["duree_assurance"] >= SEUIL_MAJORATION
            > e["openfisca"]["duree_cotisee"]} == {"minimum_contributif_sous_120_cotises"}


# -- le portage -------------------------------------------------------------------

_PORTAGE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { Carriere } from "./moteur/js/carriere.js";
const chronologies = JSON.parse(readFileSync(process.argv[1], "utf8"));
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
const simulateur = new Contexte(paquet).simulateur();
const sortie = {};
for (const [code, chronologie] of Object.entries(chronologies)) {
  const resultat = simulateur.scenarioActuel.calculer(
    Carriere.depuisChronologie(chronologie, simulateur.macro));
  sortie[code] = resultat.pensions_par_regime
    .filter((x) => x.regime === "regime_general")
    .reduce((s, x) => s + x.montant, 0);
}
process.stdout.write(JSON.stringify(sortie));
"""


def test_le_portage_javascript_sert_les_memes_pensions(temoin, nous, tmp_path):
    """Le jumeau JavaScript sert, sur les onze profils, la même pension de
    base, au milliardième."""
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    chemin = tmp_path / "chronologies.json"
    chemin.write_text(json.dumps({code: chronologie_du_profil(entree["profil"])
                                  for code, entree in temoin["profils"].items()}),
                      encoding="utf-8")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _PORTAGE_JS, str(chemin)],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    portage = json.loads(execution.stdout)
    for code, moi in nous.items():
        assert portage[code] == pytest.approx(moi["pension_brute"], rel=1e-9), code
