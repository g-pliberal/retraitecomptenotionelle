"""L'oracle au-delà des carrières simples, troisième famille : la catégorie
active des fonctionnaires, confrontée à OpenFisca-France-Pension (action 153,
étape 2).

Le frère de ``tests/test_oracle_familles.py``, dont il reprend le calcul du
dépôt et la méthode : la convention de traduction d'abord, écrite dans
``scripts/fetch/openfisca_categorie_active.py`` et portée par le témoin, puis
chaque grandeur ; un écart connu est déclaré avec le texte qui le tranche, et
chacun des deux modèles doit rendre exactement ce que SA règle commande.

* **L'âge anticipé, la décote et la limite d'âge** des emplois classés en
  catégorie active : rien à corriger.
* **La durée de services actifs** qui ouvre l'âge anticipé, quinze ans relevés
  à dix-sept selon l'année où les quinze sont atteints (décret n° 2011-2103,
  article 6) : le dépôt la lisait par génération, et refusait l'âge anticipé à
  qui avait achevé ses quinze ans avant 2011 sans aller jusqu'à dix-sept.
  Corrigé le 14 octobre 2026 (``duree_services_actifs.csv``) ; les deux
  concordent.
* **La proratisation** des actifs : OpenFisca prend la durée de la
  génération, quand L. 13, III, prend celle des fonctionnaires qui ont
  soixante ans l'année où le droit s'ouvre — celle qu'il oppose lui-même à la
  décote. L'écart est le sien.
* **La super-active** : OpenFisca ne compte pas ses années, ne lui ouvre pas
  l'âge minoré, et ne sert pas la bonification du cinquième. L'écart est le
  sien.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Simulateur
from test_oracle_familles import (
    PRECISION_OPENFISCA,
    PREFIXES,
    TOLERANCE_EXACTE,
    _notre_calcul,
)

TEMOIN = Path(__file__).resolve().parent / "temoins" / "openfisca_categorie_active.json"

AGE_ANTICIPE = "age_anticipe"
DUREE_ACTIVE = "duree_de_services_actifs"
SUPER_ACTIVE = "super_active"

#: Les entrées d'OpenFisca que la convention doit dire, au témoin.
CONVENTION_ATTENDUE = {
    "date_de_naissance", "sexe", "liquidation_date", "salaire_de_base",
    "duree_de_service_cotisee_annuelle", "quotite_de_travail", "taux_de_prime",
    "categorie_activite", "super_actif_a_la_liquidation", "non_traduit", "dates",
}
#: Les statuts du dépôt qui ne portent que le classement : ni prime de corps,
#: ni majoration de durée des hospitaliers.
STATUTS_NUS = {
    "fonctionnaire_territorial_hospitalier_actif": "active",
    "fonctionnaire_etat_actif": "active",
    "fonctionnaire_etat_super_actif": "super_active",
}

#: Décret n° 2011-2103, article 6 (LEGIARTI000025100424) : la durée de
#: services actifs exigée, selon l'« Année au cours de laquelle est atteinte la
#: durée de services de quinze ans » ; vingt-cinq ans de services super-actifs
#: avant le 1er juillet 2011.
DUREE_ACTIVE_SELON_L_ATTEINTE = {2010: 15.0, 2012: 15 + 9 / 12, 2013: 16 + 2 / 12}
DUREE_SUPER_ACTIVE_AVANT_2011 = 25.0
#: Ce que le dépôt exigeait de toute génération née depuis le 1er juillet 1956.
DUREE_ACTIVE_PAR_GENERATION = 17.0
#: L. 14, I : vingt trimestres de décote au plus.
DECOTE_PLAFONNEE = 20
#: Loi n° 96-452, article 24 : le cinquième des services, cinq ans au plus.
BONIFICATION_DU_CINQUIEME_PLAFOND = 20


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def nous(temoin, simulateur) -> dict[str, dict]:
    """Le calcul du dépôt pour chaque profil, fait une fois."""
    return {code: _notre_calcul(simulateur, entree["profil"])
            for code, entree in temoin["profils"].items()}


def _de_la_regle(temoin: dict, regle: str) -> list[tuple[str, dict]]:
    return [(code, entree) for code, entree in temoin["profils"].items()
            if entree["profil"]["regle"] == regle]


def _actifs_des_deux_cotes(temoin: dict, nous: dict) -> list[tuple[str, dict]]:
    """Les profils de la catégorie active à qui les deux ouvrent l'âge anticipé."""
    return [(code, entree) for code, entree in temoin["profils"].items()
            if entree["profil"]["classement"] == "active"
            and nous[code]["derogation_active"] is not None
            and entree["openfisca"]["actif_a_la_liquidation"]]


def _annees_classees(profil: dict) -> int:
    debut, fin = profil["actif"]
    return fin - debut + 1


def _date(profil: dict, age: float) -> str:
    """La date où le profil, né un 1er janvier, atteint ``age``, au mois."""
    mois = round(age * 12)
    return f"{profil['naissance'] + mois // 12}-{mois % 12 + 1:02d}-01"


# -- la convention ---------------------------------------------------------------

def test_le_temoin_suit_sa_convention_de_traduction(temoin):
    """Le témoin dit d'où il vient, porte sa convention, et chaque profil les
    entrées qu'OpenFisca a reçues : la catégorie de chaque année classée, la
    super-active déclarée à la liquidation, et rien d'autre ; ni enfant, ni
    temps partiel. Les statuts du dépôt ne portent que le classement, et
    aucune plage n'achève ses quinze ou vingt-cinq ans en 2011, que le décret
    coupe au 1er juillet."""
    assert temoin["source"] == "OpenFisca-France-Pension"
    assert temoin["version"]
    assert CONVENTION_ATTENDUE <= set(temoin["convention"])
    profils = temoin["profils"]
    assert {e["profil"]["regle"] for e in profils.values()} == {
        AGE_ANTICIPE, DUREE_ACTIVE, SUPER_ACTIVE}
    for code, entree in profils.items():
        profil, recu, eux = entree["profil"], entree["entrees_openfisca"], entree["openfisca"]
        prefixe = PREFIXES[profil["regime"]]
        assert 2009 <= profil["liquidation"] <= 2020, code
        assert eux["duree_assurance"] > 0 and eux["pension_brute"] > 0, code
        assert not {"temps_partiel", "naissances", "raison"} & set(profil), code
        assert STATUTS_NUS[profil["statut_actif"]] == profil["classement"], code
        assert (profil["regle"] == SUPER_ACTIVE) is (profil["classement"] == "super_active")
        debut, fin = profil["actif"]
        assert profil["debut"] <= debut <= fin < profil["liquidation"], code
        categorie = "super_actif" if profil["classement"] == "super_active" else "actif"
        assert recu[f"{prefixe}_categorie_activite"] == {
            str(a): categorie for a in range(debut, fin + 1)}, code
        assert recu.get(f"{prefixe}_super_actif_a_la_liquidation") == (
            {str(profil["liquidation"]): True}
            if profil["classement"] == "super_active" else None), code
        base = 25 if profil["classement"] == "super_active" else 15
        assert debut + base - 1 != 2011, code
        assert recu["sexe"] is False and recu["nombre_enfants"] == 0, code


# -- l'âge anticipé ---------------------------------------------------------------

def test_l_age_anticipe_s_ouvre_des_deux_cotes(temoin, nous, simulateur):
    """L. 24, I, 1° : l'emploi classé en catégorie active ouvre la pension à
    l'âge anticipé de sa génération — 55 ans, puis 55 ans et 4 mois pour la
    génération du second semestre 1956, et ainsi jusqu'à 57 ans pour celle de
    1960 (décret n° 2011-2103, article 2). Les deux le datent au mois."""
    profils = _actifs_des_deux_cotes(temoin, nous)
    assert len(profils) == 7
    for code, entree in profils:
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        age = moi["derogation_active"].age_ouverture
        assert age == simulateur.scenario_actuel.ages_categorie_active.derogation(
            "active", profil["naissance"]).age_ouverture, code
        assert age <= profil["liquidation"] - profil["naissance"], code
        assert eux["ouverture_des_droits_le"] == _date(profil, age), code
        assert moi["liquidation_ouverte"], code


def test_la_decote_des_actifs_concorde(temoin, nous):
    """L. 14 : la décote des actifs court jusqu'à la limite d'âge de l'emploi,
    moins les trimestres que le barème retranche selon l'année de l'âge
    anticipé, et sur la durée exigée des fonctionnaires qui ont soixante ans
    l'année où le droit s'ouvre (L. 13, III) — 161 trimestres pour l'actif né
    en 1954, la durée de la génération 1949. OpenFisca l'oppose à la décote
    comme le dépôt : trimestres, taux et limite d'âge concordent."""
    for code, entree in _actifs_des_deux_cotes(temoin, nous):
        eux, moi = entree["openfisca"], nous[code]
        assert moi["proratisation"] == eux["duree_requise_des_actifs"], code
        assert moi["proratisation"] < eux["duree_requise_de_la_generation"], code
        assert moi["decote_trimestres"] == eux["decote_trimestres"] <= DECOTE_PLAFONNEE, code
        assert moi["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=TOLERANCE_EXACTE), code
        assert moi["derogation_active"].age_annulation == pytest.approx(
            eux["limite_d_age"], abs=0.01), code
        assert moi["traitement_de_reference"] == pytest.approx(
            eux["traitement_de_reference"], rel=PRECISION_OPENFISCA), code
        assert moi["duree_assurance"] == eux["duree_assurance"] == moi["services"], code


# -- la durée de services actifs --------------------------------------------------

def test_la_duree_de_services_actifs_se_lit_a_l_annee_ou_les_quinze_ans_sont_atteints(
        temoin, nous):
    """Loi n° 2010-1330, article 35 (LEGIARTI000025014546), et décret
    n° 2011-2103, article 6 (LEGIARTI000025100424) : les quinze ans de
    services actifs deviennent dix-sept, par marches, selon l'« Année au cours
    de laquelle est atteinte la durée de services de quinze ans ». Seize ans
    suffisent à qui a achevé ses quinze avant juillet 2011, ou en 2012 ; non à
    qui les achève en 2013. Le dépôt exigeait dix-sept ans de toute
    génération née depuis juillet 1956 : il refusait l'âge anticipé aux deux
    premiers profils. Corrigé, il les lit comme OpenFisca, qui date l'atteinte
    du 1er janvier de son année."""
    profils = _de_la_regle(temoin, DUREE_ACTIVE)
    assert len(profils) == 3
    for code, entree in profils:
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        annees = _annees_classees(profil)
        atteinte = profil["actif"][0] + 14
        assert eux["quinze_ans_actifs_le"] == f"{atteinte}-01-01", code
        assert eux["annees_actives"] == annees < DUREE_ACTIVE_PAR_GENERATION, code
        exigee = DUREE_ACTIVE_SELON_L_ATTEINTE[min(max(atteinte, 2010), 2013)]
        ouvert = annees >= exigee
        assert bool(eux["actif_a_la_liquidation"]) is ouvert, code
        assert (moi["derogation_active"] is not None) is ouvert, code
        assert moi["liquidation_ouverte"] is ouvert, code
        assert moi["decote_trimestres"] == eux["decote_trimestres"], code
        assert moi["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=TOLERANCE_EXACTE), code
    assert [code for code, entree in profils
            if entree["openfisca"]["actif_a_la_liquidation"]] == [
        "cnracl_actif_seize_ans_avant_2011", "etat_actif_seize_ans_en_2012"]


def test_sans_l_age_anticipe_les_deux_concordent_au_centime(temoin, nous):
    """Qui n'a pas la durée de services actifs reste au droit commun, des deux
    côtés : la limite d'âge du sédentaire, vingt trimestres de décote, la
    durée de sa génération, et la même pension."""
    code = "etat_actif_seize_ans_en_2013"
    eux, moi = temoin["profils"][code]["openfisca"], nous[code]
    assert moi["derogation_active"] is None and not eux["actif_a_la_liquidation"]
    assert moi["decote_trimestres"] == eux["decote_trimestres"] == DECOTE_PLAFONNEE
    assert moi["proratisation"] == eux["duree_requise_de_la_generation"]
    assert moi["pension_avant_minimum"] == pytest.approx(
        eux["pension_avant_minimum"], rel=PRECISION_OPENFISCA)


# -- la proratisation -------------------------------------------------------------

def test_la_proratisation_des_actifs_est_l_ecart_d_openfisca(temoin, nous):
    """L. 13, III, version du 22 janvier 2014 (LEGIARTI000028498258) : « la
    durée des services et bonifications exigée des fonctionnaires [...] qui
    remplissent les conditions de liquidation d'une pension avant l'âge de
    soixante ans est celle exigée des fonctionnaires atteignant cet âge
    l'année à compter de laquelle la liquidation peut intervenir » ; avant
    2014, l'article 5, VI, de la loi n° 2003-775. C'est la durée qui
    proratise. OpenFisca l'oppose à la décote, mais proratise sur la durée de
    la génération : la pension de chaque actif lui est plus faible de ce seul
    rapport, de un à trois trimestres sur 161 à 166."""
    for code, entree in _actifs_des_deux_cotes(temoin, nous):
        eux, moi = entree["openfisca"], nous[code]
        generation, la_notre = eux["duree_requise_de_la_generation"], moi["proratisation"]
        assert moi["services"] < la_notre < generation, code
        assert eux["coefficient_de_proratisation"] == pytest.approx(
            moi["services"] / generation, abs=TOLERANCE_EXACTE), code
        assert eux["pension_avant_minimum"] == pytest.approx(
            moi["pension_avant_minimum"] * la_notre / generation,
            rel=PRECISION_OPENFISCA), code
        assert eux["minimum_garanti"] == 0 and moi["pension"] == moi["pension_avant_minimum"]


# -- la super-active --------------------------------------------------------------

def test_la_super_active_ne_s_ouvre_pas_chez_openfisca(temoin, nous, simulateur):
    """L. 24, I, 1° : l'emploi super-actif ouvre l'âge minoré, 50 ans et neuf
    mois pour la génération 1962, à qui a vingt-sept ans de services
    super-actifs — vingt-cinq s'il les avait atteints avant juillet 2011
    (décret n° 2011-2103, article 6). Le dépôt l'ouvre aux deux profils, et
    leur sert la bonification du cinquième des personnels de surveillance de
    l'administration pénitentiaire (loi n° 96-452, article 24), cinq ans au
    plus. OpenFisca ne compte pas les années super-actives : il leur oppose
    l'âge du sédentaire, n'écrit la bonification que pour la neutraliser
    (``super_actif = False``), et les décote comme des sédentaires partis à
    52 et 54 ans."""
    for code, entree in _de_la_regle(temoin, SUPER_ACTIVE):
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        derogation = moi["derogation_active"]
        assert derogation is not None, code
        assert derogation.age_ouverture == simulateur.scenario_actuel \
            .ages_categorie_active.derogation("super_active", 1962).age_ouverture
        assert _annees_classees(profil) >= DUREE_SUPER_ACTIVE_AVANT_2011, code
        assert moi["liquidation_ouverte"], code
        assert moi["duree_assurance"] - moi["services"] == BONIFICATION_DU_CINQUIEME_PLAFOND
        assert not eux["actif_a_la_liquidation"] and eux["annees_actives"] == 0, code
        assert eux["ouverture_des_droits_le"] > f"{profil['liquidation']}-01-01", code
        assert eux["bonification"] == 0 and eux["duree_assurance"] == eux["services"], code
        assert eux["services"] == moi["services"], code
        assert eux["pension_avant_minimum"] < moi["pension_avant_minimum"], code
    # Vingt-six ans, achevant les vingt-cinq en 2008 : sous la lecture par
    # génération, l'âge minoré lui était fermé.
    vingt_six = temoin["profils"]["etat_super_actif_vingt_six_ans_avant_2011"]["profil"]
    assert _annees_classees(vingt_six) < 27


# -- le portage -------------------------------------------------------------------

_PORTAGE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { PARAMETRES_DEFAUT } from "./moteur/js/config.js";
import { AnneeCarriere, Carriere } from "./moteur/js/carriere.js";
const [profils, sedentaires] = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
const simulateur = new Contexte(paquet).simulateur(PARAMETRES_DEFAUT);
const sortie = {};
for (const p of profils) {
  const lignes = [];
  for (let annee = p.debut; annee < p.liquidation; annee++) {
    const classee = annee >= p.actif[0] && annee <= p.actif[1];
    lignes.push(new AnneeCarriere({
      annee, revenu: p.traitement, trimestres_valides: 4,
      affiliation: classee ? p.statut_actif : sedentaires[p.regime] }));
  }
  const resultat = simulateur.scenarioActuel.calculer(new Carriere({
    annee_naissance: p.naissance, sexe: "H", lignes, jour_naissance: 1,
    age_liquidation: p.liquidation - p.naissance, identifiant: p.code }));
  const pension = resultat.pensions_par_regime.find((r) => r.regime === p.regime);
  sortie[p.code] = [resultat.liquidation_ouverte, pension ? pension.montant : null];
}
process.stdout.write(JSON.stringify(sortie));
"""


def test_le_portage_javascript_lit_la_duree_a_l_annee_d_atteinte(temoin, nous):
    """Le jumeau JavaScript ouvre l'âge anticipé ou minoré aux mêmes profils,
    et sert la même pension, au milliardième : la durée de services classés
    relevée selon l'année d'atteinte est portée des deux côtés."""
    import shutil
    import subprocess

    from test_oracle_familles import AFFILIATIONS

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    profils = [entree["profil"] for entree in temoin["profils"].values()]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _PORTAGE_JS,
         json.dumps([profils, AFFILIATIONS])],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    portage = json.loads(execution.stdout)
    for code, moi in nous.items():
        ouverte, pension = portage[code]
        assert ouverte is moi["liquidation_ouverte"], code
        assert pension == pytest.approx(moi["pension"], rel=1e-9), code
