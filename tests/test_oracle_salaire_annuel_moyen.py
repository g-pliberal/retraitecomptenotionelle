"""L'oracle au-delà des carrières simples, septième famille : le salaire annuel
moyen du régime général sur des salaires qui varient, confronté à
OpenFisca-France-Pension (action 153, étape 2).

Le frère de ``tests/test_oracle_points_enfants_arrco.py``, dont il reprend la
méthode : la convention de traduction d'abord, écrite dans
``scripts/fetch/openfisca_salaire_annuel_moyen.py`` et portée par le témoin,
puis chaque règle ; un écart connu est déclaré avec le texte qui le tranche, et
chacun des deux modèles doit rendre exactement ce que SA règle commande.

Le témoin porte, année par année, ce qu'OpenFisca forme : le salaire, le
plafond, l'exclusion, le coefficient de revalorisation. Rejouer sa règle sur ce
détail rend son salaire annuel moyen au centime ; la rejouer avec les
coefficients et le plafond du dépôt rend le nôtre. Ce qui tient à la règle se
sépare ainsi de ce qui tient aux paramètres.

* **La règle** : les meilleures années revalorisées, plafonnées, au nombre que
  fixe la génération, sans celles qui n'achètent pas un trimestre depuis 2004.
  Les deux concordent au centime.
* **Les coefficients** : la colonne de la circulaire Cnav au dépôt, une série
  composée chez OpenFisca ; l'écart est le sien.
* **Le plafond d'une année à deux plafonds** : la somme des plafonds mensuels
  au dépôt, celui de janvier chez OpenFisca ; l'écart est le sien.
* **Le calcul trimestriel** jusqu'au 30 juin 1995 : l'écart est le sien.
* **La décote à l'âge exact** : OpenFisca compte un trimestre de trop quand le
  départ tombe le jour anniversaire ; l'écart est le sien.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.simulateur import Simulateur

TEMOIN = Path(__file__).resolve().parent / "temoins" / "openfisca_salaire_annuel_moyen.json"

MEILLEURES = "meilleures"
PLAFOND = "plafond"
SANS_TRIMESTRE = "sans_trimestre"
AVANT_2004 = "avant_2004"
MOINS_QUE_LE_NOMBRE = "moins_que_le_nombre"
GENERATION = "generation"
TRIMESTRIEL = "trimestriel"

#: Les entrées d'OpenFisca que la convention doit dire, au témoin.
CONVENTION_ATTENDUE = {
    "date_de_naissance", "sexe", "liquidation_date", "salaire_de_base",
    "categorie_salarie", "trimestres", "comparaison", "non_traduit",
}

#: Le franc, et les deux plafonds de 1960 : 6 600 F au 1er janvier, 7 080 F au
#: 1er juillet (décrets n° 58-1436 du 31 décembre 1958 et n° 60-620 du 29 juin
#: 1960, tels qu'OpenFisca les date).
FRANC = 6.55957
PLAFONDS_DE_1960 = (6600.0, 7080.0)

#: OpenFisca tire l'âge en mois d'une durée en jours, convertie au mois moyen
#: du calendrier grégorien de numpy (``timedelta64[M]``), et tronque.
MOIS_MOYEN = 365.2425 / 12

_REGIME = "regime_general"
_AFFILIATION = "salarie_prive_non_cadre"


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def carriere(simulateur: Simulateur, profil: dict) -> Carriere:
    """La carrière que la convention décrit : chaque année valide les
    trimestres que son salaire achète."""
    macro = simulateur.scenario_actuel.macro
    lignes = [AnneeCarriere(annee=int(annee), revenu=salaire, affiliation=_AFFILIATION,
                            trimestres_valides=macro.trimestres_valides(salaire, int(annee)))
              for annee, salaire in profil["salaires"].items()]
    return Carriere(annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
                    age_liquidation=float(profil["liquidation"] - profil["naissance"]),
                    identifiant=profil["code"], jour_naissance=1)


def _le_droit(simulateur: Simulateur, profil: dict) -> dict:
    """Ce que le scénario 1 rend au régime général."""
    scenario = simulateur.scenario_actuel
    histoire = carriere(simulateur, profil)
    periode = simulateur.catalogue[_REGIME].periode(profil["liquidation"])
    resultat = scenario.calculer(histoire)
    base = next(p for p in resultat.pensions_par_regime if p.regime == _REGIME)
    return {
        "salaire_de_reference": liquider.salaire_de_reference(
            scenario, _REGIME, histoire, periode, profil["liquidation"], True,
            profil["naissance"], True),
        "nombre_d_annees": liquider.nombre_d_annees_retenues(
            scenario, periode, histoire, profil["naissance"]),
        "duree_assurance": resultat.trimestres_valides,
        "taux_de_liquidation": resultat.taux_liquidation,
        "pension_brute": base.montant,
        "trimestres": {annee: ligne.trimestres_valides for annee, ligne in
                       ((str(ligne.annee), ligne) for ligne in histoire.lignes)},
    }


@pytest.fixture(scope="module")
def nous(temoin, simulateur) -> dict[str, dict]:
    """Le calcul du dépôt pour chaque profil, fait une fois."""
    return {code: _le_droit(simulateur, entree["profil"])
            for code, entree in temoin["profils"].items()}


def _de_la_regle(temoin: dict, *regles: str) -> list[tuple[str, dict]]:
    return [(code, entree) for code, entree in temoin["profils"].items()
            if entree["profil"]["regle"] in regles]


def _retenues(eux: dict, plafond, coefficient) -> list[float]:
    """Les années que la règle d'OpenFisca retient, sous un plafond et des
    coefficients donnés, de la plus forte à la plus faible."""
    valeurs = sorted((min(d["salaire"], plafond(int(a), d)) * coefficient(int(a), d)
                      for a, d in eux["annees"].items() if not d["exclue"]), reverse=True)
    return valeurs[:eux["nombre_d_annees"]]


def _moyenne(valeurs: list[float]) -> float:
    return sum(valeurs) / len(valeurs)


def _ses_parametres(eux: dict) -> list[float]:
    return _retenues(eux, lambda a, d: d["plafond"], lambda a, d: d["coefficient"])


def _nos_parametres(simulateur: Simulateur, liquidation: int):
    macro = simulateur.scenario_actuel.macro
    return (lambda a, d: macro.plafond_securite_sociale(a),
            lambda a, d: macro.coefficient_revalorisation_portee_au_compte(a, liquidation, 1))


# -- la convention ---------------------------------------------------------------

def test_le_temoin_suit_sa_convention_de_traduction(temoin, nous):
    """Le témoin dit d'où il vient et porte sa convention ; chaque profil reste
    dans ce qu'OpenFisca sait faire — une formule par génération depuis 1994,
    une table de revalorisation jusqu'en 2023 —, les deux comptent la même
    durée d'assurance et retiennent le même nombre d'années, et la règle
    d'OpenFisca, rejouée sur le détail que le témoin relève, rend son salaire
    annuel moyen au centime : le détail est fidèle."""
    assert temoin["source"] == "OpenFisca-France-Pension"
    assert temoin["version"]
    assert CONVENTION_ATTENDUE <= set(temoin["convention"])
    assert {e["profil"]["regle"] for e in temoin["profils"].values()} == {
        MEILLEURES, PLAFOND, SANS_TRIMESTRE, AVANT_2004, MOINS_QUE_LE_NOMBRE,
        GENERATION, TRIMESTRIEL}
    for code, entree in temoin["profils"].items():
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        assert 1994 <= profil["liquidation"] <= 2021, code
        assert min(map(int, profil["salaires"])) > profil["naissance"] + 10, code
        assert moi["duree_assurance"] == eux["duree_assurance"], code
        assert moi["nombre_d_annees"] == eux["nombre_d_annees"], code
        assert _moyenne(_ses_parametres(eux)) == pytest.approx(
            eux["salaire_de_reference"], abs=0.01), code


# -- la règle --------------------------------------------------------------------

def test_la_regle_concorde_au_centime_sous_les_memes_parametres(temoin, nous, simulateur):
    """R. 351-29 : la moyenne des meilleures années, salaires revalorisés et
    plafonnés, au nombre que fixe la génération (R. 351-29-1) — toutes s'il y
    en a moins —, sans celles qui ne valident aucun trimestre depuis 2004. La
    règle d'OpenFisca, rejouée avec le plafond et les coefficients du dépôt,
    rend le salaire annuel moyen du dépôt au centime : les années retenues,
    l'écrêtement, l'exclusion et le nombre sont les mêmes. Seul le calcul
    trimestriel d'avant juillet 1995 s'en écarte, plus bas."""
    profils = _de_la_regle(temoin, MEILLEURES, PLAFOND, SANS_TRIMESTRE, AVANT_2004,
                           MOINS_QUE_LE_NOMBRE, GENERATION)
    assert len(profils) == 11
    for code, entree in profils:
        eux = entree["openfisca"]
        plafond, coefficient = _nos_parametres(simulateur, entree["profil"]["liquidation"])
        assert nous[code]["salaire_de_reference"] == pytest.approx(
            _moyenne(_retenues(eux, plafond, coefficient)), abs=0.01), code


def test_les_annees_sans_trimestre_sont_exclues_depuis_2004(temoin, nous):
    """Depuis le 1er janvier 2004, une année dont le salaire ne valide aucun
    trimestre n'entre plus dans la moyenne (R. 351-29, décret n° 2004-144).
    Les trois années à moins de 1 200 € d'une carrière de vingt ans sont
    écartées des deux côtés ; les deux de la carrière liquidée en 2003 restent,
    et y abaissent la moyenne."""
    (code, entree), = _de_la_regle(temoin, SANS_TRIMESTRE)
    eux, moi = entree["openfisca"], nous[code]
    exclues = {a for a, d in eux["annees"].items() if d["exclue"]}
    assert exclues == {a for a, t in moi["trimestres"].items() if t == 0} == {
        "2001", "2006", "2011"}
    assert eux["nombre_d_annees"] > len(eux["annees"]) - len(exclues)
    (code, entree), = _de_la_regle(temoin, AVANT_2004)
    eux, moi = entree["openfisca"], nous[code]
    assert not any(d["exclue"] for d in eux["annees"].values())
    faibles = {a for a, t in moi["trimestres"].items() if t == 0}
    assert faibles == {"1992", "1997"}
    assert len(_ses_parametres(eux)) == len(eux["annees"]) < eux["nombre_d_annees"]


def test_le_plafond_ecrete_chaque_annee(temoin, nous):
    """Le salaire de chaque année n'entre que dans la limite du plafond de la
    même année : les dix années à 80 000 € n'y valent, des deux côtés, que leur
    plafond."""
    (code, entree), = _de_la_regle(temoin, PLAFOND)
    eux = entree["openfisca"]
    ecretees = {a for a, d in eux["annees"].items() if d["salaire"] > d["plafond"]}
    assert {str(a) for a in range(1995, 2005)} <= ecretees


# -- les écarts d'OpenFisca --------------------------------------------------------

def test_les_coefficients_sont_l_ecart_d_openfisca(temoin, nous, simulateur):
    """La Cnav publie chaque colonne de coefficients entière dans sa circulaire,
    que le dépôt lit (``legislation/revalorisation_salaires.csv``) ; OpenFisca
    compose les siens en multipliant une série annuelle (``reval_s``). Au
    départ de 2018, il applique 21,89 aux salaires de 1961 au lieu de 20,034,
    1,000 à ceux de 2017 au lieu de 1,008. Sous ses coefficients, le salaire
    annuel moyen du dépôt deviendrait le sien : l'écart des deux salaires
    annuels moyens est tout entier celui des coefficients, et du plafond qui
    suit."""
    macro = simulateur.scenario_actuel.macro
    ecarts = []
    for code, entree in _de_la_regle(temoin, MEILLEURES, PLAFOND, SANS_TRIMESTRE,
                                     MOINS_QUE_LE_NOMBRE):
        eux, liquidation = entree["openfisca"], entree["profil"]["liquidation"]
        for annee, d in eux["annees"].items():
            ecarts.append(macro.coefficient_revalorisation_portee_au_compte(
                int(annee), liquidation, 1) / d["coefficient"] - 1)
        assert nous[code]["salaire_de_reference"] != pytest.approx(
            eux["salaire_de_reference"], abs=1.0), code
    assert min(ecarts) < -0.05 and max(ecarts) > 0.005


def test_le_plafond_d_une_annee_a_deux_plafonds_est_l_ecart_d_openfisca(
        temoin, nous, simulateur):
    """Le plafond annuel est la somme des plafonds mensuels : en 1960, 6 600 F
    jusqu'en juin, 7 080 F ensuite, soit 6 840 F, que le dépôt porte
    (``macro/plafond_securite_sociale.csv``). OpenFisca lit le plafond au
    1er janvier, 6 600 F. Le profil de la génération 1938, dont les années
    1960 à 1962 sont parmi les meilleures, en garde chez lui un salaire annuel
    moyen trop bas de près de 102 €, à coefficients égaux ; 1961, relevé au
    1er avril, de même."""
    macro = simulateur.scenario_actuel.macro
    janvier, juillet = PLAFONDS_DE_1960
    assert macro.plafond_securite_sociale(1960) == round((janvier + juillet) / 2 / FRANC)
    entree = temoin["profils"]["generation_1938_en_1998"]
    eux = entree["openfisca"]
    assert eux["annees"]["1960"]["plafond"] == pytest.approx(janvier / FRANC, abs=0.01)
    plafond, coefficient = _nos_parametres(simulateur, entree["profil"]["liquidation"])
    sous_le_sien = _moyenne(_retenues(eux, lambda a, d: d["plafond"], coefficient))
    assert nous["generation_1938_en_1998"]["salaire_de_reference"] - sous_le_sien == (
        pytest.approx(101.73, abs=0.05))


def test_le_calcul_trimestriel_avant_juillet_1995_est_l_ecart_d_openfisca(
        temoin, nous, simulateur):
    """Jusqu'au 30 juin 1995, la somme des salaires retenus se rapporte à leurs
    trimestres, multipliée par quatre (circulaire Cnav 1/73), et non au nombre
    d'années (circulaire Cnav 95/94, ensuite) : fiche ``salaire_annuel_moyen``.
    Neuf années retenues, dont une de trois trimestres : le dépôt divise par
    35 trimestres, OpenFisca par neuf années, soit 36 trimestres."""
    (code, entree), = _de_la_regle(temoin, TRIMESTRIEL)
    eux, moi = entree["openfisca"], nous[code]
    assert sorted(moi["trimestres"].values()) == [3] + [4] * 8
    plafond, coefficient = _nos_parametres(simulateur, entree["profil"]["liquidation"])
    retenues = _retenues(eux, plafond, coefficient)
    assert moi["salaire_de_reference"] == pytest.approx(sum(retenues) * 4 / 35, abs=0.01)
    assert eux["salaire_de_reference"] == pytest.approx(_moyenne(_ses_parametres(eux)))


def test_la_decote_a_l_age_exact_est_l_ecart_d_openfisca(temoin, nous):
    """Né le 1er janvier 1950, parti le 1er janvier 2012 : soixante-deux ans
    tout juste, trois ans avant l'âge d'annulation de la décote, douze
    trimestres (R. 351-27, arrondi au trimestre supérieur). OpenFisca tire
    l'âge en mois d'une durée en jours, au mois moyen de numpy, et tronque :
    22 645 jours font 743 mois, et treize trimestres. Le taux s'en ressent,
    0,394 au lieu de 0,4025 ; le salaire annuel moyen, lui, concorde à
    coefficients égaux."""
    entree = temoin["profils"]["carriere_courte_en_2012"]
    eux, moi = entree["openfisca"], nous["carriere_courte_en_2012"]
    jours = (2012 - 1950) * 365 + sum(1 for a in range(1950, 2012) if a % 4 == 0)
    assert jours == 22645 and int(jours / MOIS_MOYEN) == 62 * 12 - 1
    assert eux["decote_trimestres"] == 13
    assert moi["taux_de_liquidation"] == pytest.approx(0.5 * (1 - 12 * 0.01625))
    assert eux["taux_de_liquidation"] == pytest.approx(0.5 * (1 - 13 * 0.01625), abs=1e-6)


def test_la_pension_suit_le_salaire_annuel_moyen(temoin, nous):
    """La pension de base est le salaire annuel moyen fois le taux et la
    proratisation, chez l'un et l'autre : à décote égale, le rapport des deux
    pensions est celui des deux salaires annuels moyens."""
    for code, entree in temoin["profils"].items():
        eux, moi = entree["openfisca"], nous[code]
        if code == "carriere_courte_en_2012":
            continue
        assert moi["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=1e-6), code
        assert moi["pension_brute"] / eux["pension_brute"] == pytest.approx(
            moi["salaire_de_reference"] / eux["salaire_de_reference"], rel=1e-5), code


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
  const lignes = Object.entries(p.salaires).map(([annee, revenu]) => new AnneeCarriere({
    annee: Number(annee), revenu, trimestres_valides: p.trimestres[annee],
    affiliation: "salarie_prive_non_cadre" }));
  const resultat = simulateur.scenarioActuel.calculer(new Carriere({
    annee_naissance: p.naissance, sexe: "H", lignes, jour_naissance: 1,
    age_liquidation: p.liquidation - p.naissance, identifiant: p.code }));
  sortie[p.code] = resultat.pensions_par_regime
    .filter((x) => x.regime === "regime_general")
    .reduce((s, x) => s + x.montant, 0);
}
process.stdout.write(JSON.stringify(sortie));
"""


def test_le_portage_javascript_sert_les_memes_pensions(temoin, nous):
    """Le jumeau JavaScript sert, sur les douze profils, la même pension de
    base, au milliardième."""
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    profils = [{**entree["profil"], "trimestres": nous[code]["trimestres"]}
               for code, entree in temoin["profils"].items()]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _PORTAGE_JS, json.dumps(profils)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    portage = json.loads(execution.stdout)
    for code, moi in nous.items():
        assert portage[code] == pytest.approx(moi["pension_brute"], rel=1e-9), code
