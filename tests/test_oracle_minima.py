"""L'oracle au-delà des carrières simples, cinquième famille : les minima — le
minimum garanti de la pension civile et le minimum contributif du régime
général —, confrontés à OpenFisca-France-Pension (action 153, étape 2).

Le frère de ``tests/test_oracle_carriere_longue_fonction_publique.py``, dont il
reprend la méthode : la convention de traduction d'abord, écrite dans
``scripts/fetch/openfisca_minima.py`` et portée par le témoin, puis chaque
règle ; un écart connu est déclaré avec le texte qui le tranche, et chacun
des deux modèles doit rendre exactement ce que SA règle commande.

* **Le barème de L. 17** : les deux le servent de même, rapporté à sa
  référence, que chacun date à sa façon (``tests/test_oracle.py``).
* **La CNRACL** : OpenFisca y lit les services de l'État. L'écart est le sien.
* **L'ancien droit sous quinze ans** : OpenFisca sert le d à qui garde le c.
  L'écart est le sien.
* **La minoration transitoire** : OpenFisca ne la porte pas. L'écart est le
  sien.
* **La condition de taux plein** : les deux refusent le minimum à qui part
  avec une décote après 2015.
* **Le minimum contributif** : les deux le servent au centime.
* **La durée corrigée** : OpenFisca ne la lit pas. L'écart est le sien.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.droit.liquider import MINORATION_AGE_MINIMUM_GARANTI
from retraite_notionnelle.simulateur import Simulateur
from test_oracle_familles import AFFILIATIONS, PRECISION_OPENFISCA, _notre_calcul

TEMOIN = Path(__file__).resolve().parent / "temoins" / "openfisca_minima.json"

BAREME = "bareme"
MOINS_DE_QUINZE_ANS = "moins_de_quinze_ans"
CNRACL = "cnracl"
ANCIEN_DROIT = "ancien_droit"
MINORATION = "minoration"
CONDITION = "condition"
MINIMUM_CONTRIBUTIF = "minimum_contributif"
DUREE_CORRIGEE = "duree_corrigee"

REGIME_GENERAL = "regime_general"
AFFILIATION_SALARIE = "salarie_prive_non_cadre"

#: Les entrées d'OpenFisca que la convention doit dire, au témoin.
CONVENTION_ATTENDUE = {
    "date_de_naissance", "sexe", "liquidation_date", "salaire_de_base",
    "duree_de_service_cotisee_annuelle", "categorie_salarie", "taux_de_prime",
    "nombre_enfants", "reference", "non_traduit",
}

#: Marge laissée à la référence du minimum garanti : OpenFisca la prend au
#: point d'indice de l'année, quand L. 17 la gèle au 1er janvier 2004 et la
#: revalorise comme les pensions (``tests/test_oracle.py``).
TOLERANCE_REFERENCE = 0.15
#: L. 17, c, dans sa rédaction d'avant 2011 : 57,5 % de la référence à quinze
#: ans, un quinzième par année en dessous.
PART_A_QUINZE_ANS = 0.575
QUINZE_ANS = 60
#: Le profil ajourné : 124 trimestres, quatre trimestres après l'âge du taux
#: plein, 2,5 % chacun (R. 351-7), arrondis au trimestre supérieur ; la durée
#: de proratisation de la génération 1951.
DUREE_ACCOMPLIE, DUREE_CORRIGEE_ATTENDUE, PRORATISATION_1951 = 124, 137, 163


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _salarie(profil: dict) -> Carriere:
    """La carrière d'un salarié du profil."""
    lignes = [AnneeCarriere(annee=annee, revenu=profil["salaire"],
                            affiliation=AFFILIATION_SALARIE, trimestres_valides=4)
              for annee in range(profil["debut"], profil["liquidation"])]
    return Carriere(annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
                    age_liquidation=float(profil["liquidation"] - profil["naissance"]),
                    identifiant=profil["code"], jour_naissance=1)


def _le_droit(simulateur: Simulateur, profil: dict) -> dict:
    """Ce que le scénario 1 rend : la pension du régime, avant et après le
    minimum, et la référence du minimum garanti."""
    if profil["regime"] != REGIME_GENERAL:
        moi = _notre_calcul(simulateur, profil)
        reference = simulateur.scenario_actuel.minimum_garanti.reference(
            profil["liquidation"])
        return {**moi, "reference": reference[0]}
    resultat = simulateur.scenario_actuel.calculer(_salarie(profil))
    pension = next(p for p in resultat.pensions_par_regime if p.regime == REGIME_GENERAL)
    avantages = {a.code: a.montant for a in resultat.avantages_appliques}
    return {"pension": pension.montant,
            "pension_avant_minimum": pension.montant - avantages.get(
                "minimum_contributif", 0.0),
            "taux_de_liquidation": resultat.taux_liquidation}


@pytest.fixture(scope="module")
def nous(temoin, simulateur) -> dict[str, dict]:
    """Le calcul du dépôt pour chaque profil, fait une fois."""
    return {code: _le_droit(simulateur, entree["profil"])
            for code, entree in temoin["profils"].items()}


def _de_la_regle(temoin: dict, *regles: str) -> list[tuple[str, dict]]:
    return [(code, entree) for code, entree in temoin["profils"].items()
            if entree["profil"]["regle"] in regles]


def _coefficient(moi: dict) -> float:
    """Le barème du dépôt : la pension portée au minimum, sur sa référence."""
    return moi["pension"] / moi["reference"]


# -- la convention ---------------------------------------------------------------

def test_le_temoin_suit_sa_convention_de_traduction(temoin, nous):
    """Le témoin dit d'où il vient, porte sa convention, et chaque profil les
    entrées qu'OpenFisca a reçues : ni enfant, ni raison de départ. Les deux
    comptent la même durée, et la même pension avant le minimum aux
    fonctionnaires ; aux salariés, le salaire de référence s'écarte, ce que
    ``tests/test_oracle.py`` tranche, mais le minimum passe les deux."""
    assert temoin["source"] == "OpenFisca-France-Pension"
    assert temoin["version"]
    assert CONVENTION_ATTENDUE <= set(temoin["convention"])
    profils = temoin["profils"]
    assert {e["profil"]["regle"] for e in profils.values()} == {
        BAREME, MOINS_DE_QUINZE_ANS, CNRACL, ANCIEN_DROIT, MINORATION, CONDITION,
        MINIMUM_CONTRIBUTIF, DUREE_CORRIGEE}
    for code, entree in profils.items():
        profil, recu, eux, moi = (entree["profil"], entree["entrees_openfisca"],
                                  entree["openfisca"], nous[code])
        assert recu == {"sexe": False, "nombre_enfants": 0}, code
        assert eux["duree_assurance"] == 4 * (profil["liquidation"] - profil["debut"]), code
        if profil["regime"] == REGIME_GENERAL:
            assert eux["duree_cotisee"] == eux["duree_assurance"], code
            assert eux["taux_de_liquidation"] == moi["taux_de_liquidation"] == 0.5, code
            assert moi["pension_avant_minimum"] < moi["pension"], code
        else:
            assert moi["services"] == eux["services"], code
            assert moi["pension_avant_minimum"] == pytest.approx(
                eux["pension_avant_minimum"], rel=PRECISION_OPENFISCA), code


# -- le minimum garanti ----------------------------------------------------------

def test_le_bareme_du_minimum_garanti_concorde(temoin, nous):
    """L. 17 : 57,5 % de la référence à quinze ans, 2,5 points par année
    jusqu'à trente, puis 0,5 point, la totalité à quarante — les marches
    datées de 2004 à 2013 ; et, sous quinze ans depuis 2011, la référence
    rapportée à la durée de la génération (le d). Les deux portent la
    pension au minimum, et leur minimum sur leur référence est le même :
    seule la référence s'écarte, du côté qu'a dit ``tests/test_oracle.py``."""
    profils = _de_la_regle(temoin, BAREME, MOINS_DE_QUINZE_ANS)
    assert len(profils) == 4
    for code, entree in profils:
        eux, moi = entree["openfisca"], nous[code]
        assert eux["pension_brute"] == eux["minimum_garanti"] > eux["pension_avant_minimum"]
        assert moi["pension"] > moi["pension_avant_minimum"], code
        assert _coefficient(moi) == pytest.approx(
            eux["minimum_garanti"] / eux["reference_du_minimum"], rel=PRECISION_OPENFISCA), code
        assert eux["reference_du_minimum"] <= moi["reference"] == pytest.approx(
            eux["reference_du_minimum"], rel=TOLERANCE_REFERENCE), code
    quarante = nous["etat_1952_quarante_ans_en_2017"]
    assert quarante["pension"] == pytest.approx(quarante["reference"], rel=1e-12)
    treize = temoin["profils"]["etat_1955_treize_ans_en_2022"]["openfisca"]
    assert _coefficient(nous["etat_1955_treize_ans_en_2022"]) == pytest.approx(
        treize["services"] / treize["duree_requise_de_la_generation"], rel=PRECISION_OPENFISCA)


def test_la_cnracl_est_l_ecart_d_openfisca(temoin, nous):
    """Décret n° 2003-1306, article 22 (LEGIARTI000023412553) : la pension
    de la CNRACL « ne peut être inférieure » au même barème qu'à l'État. Le
    dépôt sert aux trois profils de la CNRACL le minimum de leur jumeau de
    l'État, au centime. OpenFisca y compte les services de la fonction
    publique de l'État (``fonction_publique_duree_de_service_effective``,
    écrit en dur dans ``cnracl_minimum_garanti``) : zéro, et aucun minimum."""
    profils = _de_la_regle(temoin, CNRACL)
    assert len(profils) == 3
    for code, entree in profils:
        eux, moi = entree["openfisca"], nous[code]
        jumeau = code.replace("cnracl", "etat")
        assert eux["services"] > 0 and eux["services_fonction_publique"] == 0, code
        assert eux["minimum_garanti"] == 0, code
        assert eux["pension_brute"] == eux["pension_avant_minimum"], code
        assert temoin["profils"][jumeau]["openfisca"]["minimum_garanti"] > eux["pension_brute"]
        assert moi["pension"] == nous[jumeau]["pension"] > moi["pension_avant_minimum"], code


def test_l_ancien_droit_sous_quinze_ans_est_l_ecart_d_openfisca(temoin, nous):
    """Loi n° 2010-1330, article 45, V (JORFARTI000023022174) : qui avait
    atteint l'âge d'ouverture avant 2011 conserve « le bénéfice des
    dispositions de l'article L. 17 [...] dans leur rédaction antérieure à
    la présente loi » — le c, un quinzième de 57,5 % par année de services,
    que l'article 53, V, a réservé ensuite à l'invalidité. Le dépôt le sert
    au fonctionnaire né en 1950, treize ans de services, parti en 2013 ;
    OpenFisca lui sert le d, 52 trimestres sur 162."""
    (code, entree), = _de_la_regle(temoin, ANCIEN_DROIT)
    eux, moi = entree["openfisca"], nous[code]
    assert eux["ouverture_des_droits_le"] < "2011-01-01"
    assert moi["services"] < QUINZE_ANS
    assert _coefficient(moi) == pytest.approx(
        PART_A_QUINZE_ANS * moi["services"] / QUINZE_ANS, rel=1e-9)
    assert eux["minimum_garanti"] / eux["reference_du_minimum"] == pytest.approx(
        eux["services"] / eux["duree_requise_de_la_generation"], rel=PRECISION_OPENFISCA)
    assert _coefficient(moi) > eux["minimum_garanti"] / eux["reference_du_minimum"]


def test_la_minoration_transitoire_est_l_ecart_d_openfisca(temoin, nous, simulateur):
    """Loi n° 2010-1330, article 45, IV, et décret n° 2010-1744, article 3
    (JORFARTI000023334941) : l'âge d'annulation de la décote qui ouvre le
    minimum sans la durée est minoré de neuf trimestres pour qui atteint
    l'âge d'ouverture en 2011. Le fonctionnaire né en 1951, parti à 61 ans
    en 2012 avec sept trimestres de décote, est dans la marge : le dépôt le
    porte au minimum. OpenFisca, qui n'ouvre le minimum qu'à la durée ou sans
    décote, le lui refuse."""
    (code, entree), = _de_la_regle(temoin, MINORATION)
    profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
    assert eux["ouverture_des_droits_le"].startswith("2011")
    assert eux["decote_trimestres"] == moi["decote_trimestres"] > 0
    assert eux["minimum_garanti"] == 0 and eux["pension_brute"] == eux["pension_avant_minimum"]
    assert moi["pension"] > moi["pension_avant_minimum"]
    assert MINORATION_AGE_MINIMUM_GARANTI[2011] == 9
    periode = simulateur.catalogue[profil["regime"]].periode(profil["liquidation"])
    lignes = [AnneeCarriere(annee=annee, revenu=profil["traitement"],
                            affiliation=AFFILIATIONS[profil["regime"]], trimestres_valides=4)
              for annee in range(profil["debut"], profil["liquidation"])]
    carriere = Carriere(annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
                        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
                        jour_naissance=1)
    _, annulation, _ = liquider.decote_opposable(
        simulateur.scenario_actuel, periode, carriere, profil["liquidation"])
    age = profil["liquidation"] - profil["naissance"]
    assert annulation - MINORATION_AGE_MINIMUM_GARANTI[2011] / 4 <= age < annulation


def test_sans_le_taux_plein_aucun_minimum_apres_2015(temoin, nous):
    """L. 17, premier alinéa, depuis 2011 : le minimum n'est dû qu'à la
    durée, sans décote, ou à l'âge d'annulation minoré jusqu'en 2015. Le
    fonctionnaire né en 1955, parti à soixante-deux ans avec dix-sept
    trimestres de décote, n'a de minimum ni chez l'un ni chez l'autre."""
    (code, entree), = _de_la_regle(temoin, CONDITION)
    eux, moi = entree["openfisca"], nous[code]
    assert eux["decote_trimestres"] == moi["decote_trimestres"] > 0
    assert eux["minimum_garanti"] == 0
    assert moi["pension"] == moi["pension_avant_minimum"] == pytest.approx(
        eux["pension_brute"], rel=PRECISION_OPENFISCA)


# -- le minimum contributif ------------------------------------------------------

def test_le_minimum_contributif_concorde_au_centime(temoin, nous):
    """L. 351-10 et D. 351-2-1 : le minimum au prorata de la durée dans le
    régime, la majoration au prorata des périodes cotisées, dès 120
    trimestres cotisés depuis le 1er avril 2009. Les deux portent les cinq
    pensions au même minimum, au centime ; la majoration n'est servie qu'aux
    trois carrières de 120 trimestres et plus."""
    profils = _de_la_regle(temoin, MINIMUM_CONTRIBUTIF)
    assert len(profils) == 5
    for code, entree in profils:
        eux, moi = entree["openfisca"], nous[code]
        assert eux["pension_brute"] == eux["minimum_contributif"] > eux["pension_avant_minimum"]
        assert moi["pension"] == pytest.approx(eux["minimum_contributif"], abs=0.005), code
    majores = {code for code, entree in profils
               if entree["openfisca"]["duree_cotisee"] >= 120}
    assert majores == {"salarie_1944_trente_ans_en_2009", "salarie_1946_en_2011",
                       "salarie_1948_en_2013"}


def test_la_duree_corrigee_est_l_ecart_d_openfisca(temoin, nous, simulateur):
    """Circulaire Cnav n° 8/89, point 3 : le minimum contributif se
    proratise sur « la durée d'assurance retenue par le régime général pour
    le calcul de la pension c'est-à-dire y compris, la durée d'assurance
    corrigée » — 2,5 % par trimestre après l'âge du taux plein (R. 351-7).
    Le salarié né en 1951, parti à 66 ans avec 124 trimestres, a 137
    trimestres corrigés : le dépôt y proratise le minimum, la majoration
    restant au prorata des 124 cotisés. OpenFisca le proratise sur les 124
    accomplis : le minimum majoré entier, fois 124/163."""
    (code, entree), = _de_la_regle(temoin, DUREE_CORRIGEE)
    profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
    assert eux["duree_assurance"] == eux["duree_cotisee"] == DUREE_ACCOMPLIE
    base, majore, _, _ = simulateur.scenario_actuel.minimum_contributif.valeurs(
        profil["liquidation"])
    assert eux["minimum_contributif"] == pytest.approx(
        majore * DUREE_ACCOMPLIE / PRORATISATION_1951, abs=0.01)
    assert moi["pension"] - eux["minimum_contributif"] == pytest.approx(
        base * (DUREE_CORRIGEE_ATTENDUE - DUREE_ACCOMPLIE) / PRORATISATION_1951, abs=0.01)


# -- le portage -------------------------------------------------------------------

_PORTAGE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { PARAMETRES_DEFAUT } from "./moteur/js/config.js";
import { AnneeCarriere, Carriere } from "./moteur/js/carriere.js";
const [profils, affiliations] = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
const simulateur = new Contexte(paquet).simulateur(PARAMETRES_DEFAUT);
const sortie = {};
for (const p of profils) {
  const lignes = [];
  for (let annee = p.debut; annee < p.liquidation; annee++) {
    lignes.push(new AnneeCarriere({
      annee, revenu: p.traitement ?? p.salaire, trimestres_valides: 4,
      affiliation: affiliations[p.regime] }));
  }
  const resultat = simulateur.scenarioActuel.calculer(new Carriere({
    annee_naissance: p.naissance, sexe: "H", lignes, jour_naissance: 1,
    age_liquidation: p.liquidation - p.naissance, identifiant: p.code }));
  const pension = resultat.pensions_par_regime.find((r) => r.regime === p.regime);
  sortie[p.code] = pension ? pension.montant : null;
}
process.stdout.write(JSON.stringify(sortie));
"""


def test_le_portage_javascript_sert_les_memes_minima(temoin, nous):
    """Le jumeau JavaScript sert, sur les seize profils, la même pension, au
    milliardième : minimum garanti, ancien droit, minoration et minimum
    contributif sur la durée corrigée sont portés des deux côtés."""
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    profils = [entree["profil"] for entree in temoin["profils"].values()]
    affiliations = {**AFFILIATIONS, REGIME_GENERAL: AFFILIATION_SALARIE}
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _PORTAGE_JS,
         json.dumps([profils, affiliations])],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    portage = json.loads(execution.stdout)
    for code, moi in nous.items():
        assert portage[code] == pytest.approx(moi["pension"], rel=1e-9), code
