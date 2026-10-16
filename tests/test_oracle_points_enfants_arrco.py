"""L'oracle au-delà des carrières simples, sixième famille : les points enfants
de l'Arrco et de l'Agirc et la minoration qui les frappe, confrontés à
OpenFisca-France-Pension (action 153, étape 2).

Le frère de ``tests/test_oracle_minima.py``, dont il reprend la méthode : la
convention de traduction d'abord, écrite dans
``scripts/fetch/openfisca_points_enfants_arrco.py`` et portée par le témoin,
puis chaque règle ; un écart connu est déclaré avec le texte qui le tranche, et
chacun des deux modèles doit rendre exactement ce que SA règle commande.

* **Les enfants nés ou élevés** : 5 % des points de 1999 à 2011, 10 % depuis,
  quel que soit le nombre au-delà de trois. Les deux concordent au centime.
* **Le plafond** : 1 000 € au 1er janvier 2012, par régime, revalorisé comme
  le point. L'écart était le nôtre, corrigé le 16 octobre 2026.
* **La génération** : aucun plafond avant le 2 août 1951, chez l'un et l'autre.
* **Les enfants à charge** : 5 % par enfant, la plus forte des deux
  majorations. Avant 2012, sur l'allocation ; de 2012 à 2018, sur les droits
  bruts, sans le coefficient : l'écart est celui d'OpenFisca.
* **La minoration** : le coefficient d'anticipation frappe l'allocation et sa
  majoration, chez l'un et l'autre ; OpenFisca le tronque à l'année, l'écart
  que ``tests/test_oracle.py`` tranche déjà.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.simulateur import Simulateur

TEMOIN = Path(__file__).resolve().parent / "temoins" / "openfisca_points_enfants_arrco.json"

NES_OU_ELEVES = "nes_ou_eleves"
SANS_MAJORATION = "sans_majoration"
PLAFOND = "plafond"
GENERATION = "generation"
A_CHARGE = "a_charge"
DROITS_BRUTS = "droits_bruts"
MINORATION = "minoration"
TRONCATURE = "troncature"

#: Les entrées d'OpenFisca que la convention doit dire, au témoin.
CONVENTION_ATTENDUE = {
    "date_de_naissance", "sexe", "liquidation_date", "salaire_de_base",
    "categorie_salarie", "nombre_enfants", "nombre_enfants_a_charge",
    "naissances", "comparaison", "non_traduit",
}

#: Les régimes du dépôt qui servent, chacun, l'Arrco et l'Agirc d'avant 2019.
REGIMES = {"arrco": ("arrco", "arrco_tranche_2"), "agirc": ("agirc",)}

#: L'accord du 18 mars 2011 : 1 000 € par an et par régime, pour les
#: allocations prenant effet à compter du 1er janvier 2012, « revalorisé comme
#: le point de retraite ». Les taux de chaque période d'acquisition.
PLAFOND_EN_2012 = 1000.0
TAUX_1999_2011, TAUX_DEPUIS_2012, TAUX_PAR_ENFANT_A_CHARGE = 0.05, 0.10, 0.05

_COEFFICIENT = re.compile(r"coefficient d'anticipation ([\d.]+)")
_PAR_AN = 4
#: OpenFisca rend ses coefficients en simple précision.
SIMPLE_PRECISION = 1e-6


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def naissances(profil: dict) -> tuple[str, ...]:
    """Les naissances que la convention date."""
    nes = tuple(f"{profil['naissance'] + 25 + i}-06-01" for i in range(profil["enfants"]))
    charge = tuple(f"{profil['liquidation'] - 12 + 2 * i}-06-01"
                   for i in range(profil["a_charge"]))
    return nes + charge


def carriere(profil: dict) -> Carriere:
    affiliation = ("salarie_prive_cadre" if profil.get("cadre")
                   else "salarie_prive_non_cadre")
    lignes = [AnneeCarriere(annee=annee, revenu=profil["salaire"],
                            affiliation=affiliation, trimestres_valides=4)
              for annee in range(profil["debut"], profil["liquidation"])]
    enfants = naissances(profil)
    return Carriere(annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
                    age_liquidation=float(profil["liquidation"] - profil["naissance"]),
                    identifiant=profil["code"], jour_naissance=1,
                    nombre_enfants=len(enfants), naissances_enfants=enfants)


def _le_droit(simulateur: Simulateur, profil: dict) -> dict:
    """Ce que le scénario 1 rend, régime par régime : la pension, son
    coefficient d'anticipation, sa part de la majoration pour enfants."""
    resultat = simulateur.scenario_actuel.calculer(carriere(profil))
    parts: dict[str, float] = {}
    for avantage in resultat.avantages_appliques:
        if avantage.code == "majoration_enfants":
            for code, part in avantage.par_regime:
                parts[code] = parts.get(code, 0.0) + part
    sortie = {}
    for regime, codes in REGIMES.items():
        pensions = [p for p in resultat.pensions_par_regime
                    if p.regime in codes and p.montant > 0]
        if not pensions:
            continue
        lecture = _COEFFICIENT.search(pensions[0].detail)
        sortie[regime] = {
            "pension": sum(p.montant for p in pensions),
            "coefficient": float(lecture.group(1)) if lecture else 1.0,
            "majoration": sum(parts.get(code, 0.0) for code in codes),
        }
    return sortie


@pytest.fixture(scope="module")
def nous(temoin, simulateur) -> dict[str, dict]:
    """Le calcul du dépôt pour chaque profil, fait une fois."""
    return {code: _le_droit(simulateur, entree["profil"])
            for code, entree in temoin["profils"].items()}


def _de_la_regle(temoin: dict, *regles: str) -> list[tuple[str, dict]]:
    return [(code, entree) for code, entree in temoin["profils"].items()
            if entree["profil"]["regle"] in regles]


def _servie(eux: dict) -> float:
    """La majoration qu'OpenFisca sert : ses points, minorés avec l'allocation."""
    return eux["majoration_pension"] * eux["coefficient_de_minoration"]


def _plafond(simulateur: Simulateur, regime: str, liquidation: int) -> float:
    """1 000 € au point du 1er janvier 2012, au point de la date d'effet."""
    scenario = simulateur.scenario_actuel
    servie = liquider.valeur_du_point(scenario, regime, DateMois(liquidation, 1))
    publiee = liquider.valeur_du_point(scenario, regime, DateMois(2012, 1))
    return PLAFOND_EN_2012 * servie[0] / publiee[0]


# -- la convention ---------------------------------------------------------------

def test_le_temoin_suit_sa_convention_de_traduction(temoin, nous):
    """Le témoin dit d'où il vient et porte sa convention ; chaque profil reste
    dans ce qu'OpenFisca sait faire — carrière depuis 1999, liquidation avant
    2019 —, les deux servent la même allocation de l'Arrco, et le même
    coefficient d'anticipation quand la décote tombe sur des années pleines."""
    assert temoin["source"] == "OpenFisca-France-Pension"
    assert temoin["version"]
    assert CONVENTION_ATTENDUE <= set(temoin["convention"])
    assert {e["profil"]["regle"] for e in temoin["profils"].values()} == {
        NES_OU_ELEVES, SANS_MAJORATION, PLAFOND, GENERATION, A_CHARGE,
        DROITS_BRUTS, MINORATION, TRONCATURE}
    for code, entree in temoin["profils"].items():
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        assert profil["debut"] >= 1999 and profil["liquidation"] <= 2018, code
        assert all(n < "2010-01-01" for n in naissances(profil)), code
        arrco = eux["arrco"]
        assert moi["arrco"]["pension"] / moi["arrco"]["coefficient"] == pytest.approx(
            arrco["pension_brute"], rel=1e-4), code
        if eux["decote_trimestres_regime_general"] % _PAR_AN == 0:
            assert moi["arrco"]["coefficient"] == pytest.approx(
                arrco["coefficient_de_minoration"], abs=SIMPLE_PRECISION), code


# -- les enfants nés ou élevés ----------------------------------------------------

def test_la_majoration_pour_enfants_nes_ou_eleves_concorde_au_centime(temoin, nous):
    """Accord du 17 novembre 2017, article 94, qui reprend les accords d'avant :
    5 % des points Arrco de 1999 à 2011, 10 % depuis, pour trois enfants et
    plus. Les deux la servent au centime ; le quatrième enfant n'y ajoute rien,
    et deux enfants qui ne sont plus à charge n'ouvrent rien."""
    profils = _de_la_regle(temoin, NES_OU_ELEVES)
    assert len(profils) == 3
    for code, entree in profils:
        eux, moi = entree["openfisca"]["arrco"], nous[code]["arrco"]
        assert eux["points_enfants"] == eux["points_enfants_nes_et_eleves"] > 0, code
        assert moi["majoration"] == pytest.approx(_servie(eux), abs=0.01), code
    avant = temoin["profils"]["trois_enfants_en_2012"]["openfisca"]["arrco"]
    assert avant["points_enfants"] == pytest.approx(TAUX_1999_2011 * avant["points"])
    trois, quatre = nous["trois_enfants_en_2018"], nous["quatre_enfants_en_2018"]
    assert quatre["arrco"]["majoration"] == trois["arrco"]["majoration"]
    (code, entree), = _de_la_regle(temoin, SANS_MAJORATION)
    assert entree["openfisca"]["arrco"]["majoration_pension"] == 0
    assert nous[code]["arrco"]["majoration"] == 0


# -- le plafond --------------------------------------------------------------------

def test_le_plafond_est_de_mille_euros_par_regime(temoin, nous, simulateur):
    """Accord du 18 mars 2011 : la majoration pour enfants nés ou élevés est
    « plafonnée à 1 000 € par an au titre de l'Agirc et à 1 000 € par an au
    titre de l'Arrco », pour les allocations prenant effet à compter du
    1er janvier 2012, et « revalorisé[e] comme le point de retraite »
    (circulaire Agirc-Arrco du 7 juillet 2011, point 3.3.1). Le non-cadre aux
    deux tranches de l'Arrco y est porté ; le cadre l'est à l'Agirc, et garde
    son Arrco entier, sous le sien. Le dépôt servait le plafond unifié de
    2025, commun aux deux régimes : 1 104 € au premier, au lieu de 1 031."""
    profils = _de_la_regle(temoin, PLAFOND)
    assert len(profils) == 2
    for code, entree in profils:
        eux, moi = entree["openfisca"], nous[code]
        for regime, sien in eux.items():
            if not isinstance(sien, dict):
                continue
            assert moi[regime]["majoration"] == pytest.approx(_servie(sien), abs=0.01), (
                code, regime)
    liquidation = 2018
    arrco = nous["plafond_arrco_en_2018"]["arrco"]["majoration"]
    assert arrco == pytest.approx(_plafond(simulateur, "arrco", liquidation), abs=0.01)
    cadre = nous["plafond_par_regime_en_2018"]
    assert cadre["agirc"]["majoration"] == pytest.approx(
        _plafond(simulateur, "agirc", liquidation), abs=0.01)
    assert cadre["arrco"]["majoration"] < _plafond(simulateur, "arrco", liquidation)
    points = temoin["profils"]["plafond_par_regime_en_2018"]["openfisca"]["agirc"]
    assert points["points_enfants"] * points["pension_brute"] / points["points"] > (
        cadre["agirc"]["majoration"])


def test_aucun_plafond_avant_le_2_aout_1951(temoin, nous):
    """Le plafond ne touche que les participants nés à compter du 2 août 1951 :
    le dépôt coupe à 1952, OpenFisca au jour. Le non-cadre né en 1950, parti en
    2015, garde chez l'un et l'autre une majoration au-delà du plafond."""
    (code, entree), = _de_la_regle(temoin, GENERATION)
    eux, moi = entree["openfisca"]["arrco"], nous[code]["arrco"]
    assert moi["majoration"] == pytest.approx(_servie(eux), abs=0.01)
    assert moi["majoration"] > PLAFOND_EN_2012 * 0.9


# -- les enfants à charge --------------------------------------------------------

def test_la_majoration_pour_enfants_a_charge_concorde(temoin, nous):
    """5 % par enfant à charge à la date d'effet, la plus forte des deux
    majorations. Avant 2012, sur l'allocation : « une majoration de leur
    allocation égale à 5 % » (accord du 25 avril 1996, article 12), le
    coefficient compris ; sans décote, la question ne se pose pas. Les deux
    concordent au centime."""
    profils = _de_la_regle(temoin, A_CHARGE)
    assert len(profils) == 2
    for code, entree in profils:
        profil, eux, moi = entree["profil"], entree["openfisca"]["arrco"], nous[code]["arrco"]
        assert eux["points_enfants"] == eux["points_enfants_a_charge"] == pytest.approx(
            TAUX_PAR_ENFANT_A_CHARGE * profil["a_charge"] * eux["points"]), code
        assert moi["majoration"] == pytest.approx(_servie(eux), abs=0.01), code


def test_les_droits_bruts_sont_l_ecart_d_openfisca(temoin, nous):
    """De 2012 à 2018, la majoration pour enfants à charge est « égale à 5 %
    des droits bruts de l'ensemble de la carrière par enfant à charge »
    (accord du 8 décembre 1961, annexe A, article 17, dans sa rédaction de
    l'accord du 18 mars 2011) : sans le coefficient d'anticipation, que la
    circulaire n° 2020-02-DRJ écarte en mots depuis 2019. Le dépôt la sert
    entière au non-cadre né en 1951, parti en 2014 avec deux enfants à charge
    et huit trimestres de décote ; OpenFisca la minore de 0,92."""
    (code, entree), = _de_la_regle(temoin, DROITS_BRUTS)
    eux, moi = entree["openfisca"]["arrco"], nous[code]["arrco"]
    assert moi["coefficient"] == pytest.approx(
        eux["coefficient_de_minoration"], abs=SIMPLE_PRECISION) and moi["coefficient"] < 1
    assert moi["majoration"] == pytest.approx(eux["majoration_pension"], abs=0.01)
    assert _servie(eux) < moi["majoration"]


# -- la minoration ---------------------------------------------------------------

def test_la_minoration_frappe_l_allocation_et_sa_majoration(temoin, nous):
    """Le coefficient d'anticipation frappe la majoration pour enfants nés ou
    élevés avec l'allocation, chez l'un et l'autre : 0,92 pour deux années
    d'anticipation, 0,78 pour cinq, que le départ à soixante ans en 2004 tire
    de l'âge. Les deux concordent au centime."""
    profils = _de_la_regle(temoin, MINORATION)
    assert len(profils) == 2
    coefficients = set()
    for code, entree in profils:
        eux, moi = entree["openfisca"]["arrco"], nous[code]["arrco"]
        assert moi["coefficient"] == pytest.approx(
            eux["coefficient_de_minoration"], abs=SIMPLE_PRECISION) and moi["coefficient"] < 1, code
        assert moi["majoration"] == pytest.approx(_servie(eux), abs=0.01), code
        assert moi["pension"] == pytest.approx(
            eux["pension_brute"] * eux["coefficient_de_minoration"], rel=1e-4), code
        coefficients.add(moi["coefficient"])
    assert coefficients == {0.92, 0.78}


def test_la_troncature_est_l_ecart_d_openfisca(temoin, nous):
    """Le barème d'anticipation s'écrit par trimestre ; OpenFisca le lit par
    année entière, en tronquant (``tests/test_oracle.py``). Quinze trimestres :
    0,8425 au dépôt, 0,88 chez lui, sur l'allocation comme sur sa majoration,
    que les deux minorent de même."""
    (code, entree), = _de_la_regle(temoin, TRONCATURE)
    eux, moi = entree["openfisca"], nous[code]["arrco"]
    assert eux["decote_trimestres_regime_general"] == 15
    arrco = eux["arrco"]
    assert moi["coefficient"] == pytest.approx(0.8425)
    assert moi["coefficient"] < arrco["coefficient_de_minoration"]
    assert moi["majoration"] == pytest.approx(
        arrco["majoration_pension"] * moi["coefficient"], abs=0.01)


# -- le portage -------------------------------------------------------------------

_PORTAGE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { PARAMETRES_DEFAUT } from "./moteur/js/config.js";
import { AnneeCarriere, Carriere } from "./moteur/js/carriere.js";
const profils = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
const simulateur = new Contexte(paquet).simulateur(PARAMETRES_DEFAUT);
const sortie = {};
for (const p of profils) {
  const lignes = [];
  for (let annee = p.debut; annee < p.liquidation; annee++) {
    lignes.push(new AnneeCarriere({
      annee, revenu: p.salaire, trimestres_valides: 4,
      affiliation: p.cadre ? "salarie_prive_cadre" : "salarie_prive_non_cadre" }));
  }
  const resultat = simulateur.scenarioActuel.calculer(new Carriere({
    annee_naissance: p.naissance, sexe: "H", lignes, jour_naissance: 1,
    age_liquidation: p.liquidation - p.naissance, identifiant: p.code,
    nombre_enfants: p.naissances.length, naissances_enfants: p.naissances }));
  const parts = {};
  for (const a of resultat.avantages_appliques) {
    if (a.code !== "majoration_enfants") continue;
    for (const [code, part] of a.par_regime) parts[code] = (parts[code] ?? 0) + part;
  }
  sortie[p.code] = parts;
}
process.stdout.write(JSON.stringify(sortie));
"""


def test_le_portage_javascript_sert_les_memes_majorations(temoin, nous):
    """Le jumeau JavaScript sert, sur les treize profils, la même majoration à
    chaque régime, au milliardième : le plafond par régime, de 2012 à 2018,
    est porté des deux côtés."""
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    profils = [{**entree["profil"], "naissances": list(naissances(entree["profil"]))}
               for entree in temoin["profils"].values()]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _PORTAGE_JS, json.dumps(profils)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    portage = json.loads(execution.stdout)
    for code, moi in nous.items():
        for regime, codes in REGIMES.items():
            if regime in moi:
                assert sum(portage[code].get(c, 0.0) for c in codes) == pytest.approx(
                    moi[regime]["majoration"], rel=1e-9), (code, regime)
