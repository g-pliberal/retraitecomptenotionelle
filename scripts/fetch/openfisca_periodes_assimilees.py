#!/usr/bin/env python3
"""L'oracle au-delà des carrières simples, huitième et dernière famille
(action 153) : les périodes assimilées du régime général, année par année,
par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_periodes_assimilees.py

Le frère de ``openfisca_salaire_annuel_moyen.py``, dont il reprend la carrière
et la forme. Le dépôt compte, depuis le sixième domaine de l'action 130, les
périodes assimilées que la personne déclare : les stages de formation
professionnelle, les stages d'insertion, les sportifs de haut niveau, le congé
supplémentaire de naissance, et le complément de l'apprentissage
(``droit/compter.py``). OpenFisca ne les compte pas : il reçoit, année par
année et par catégorie, les trimestres qu'une période a validés
(``regime_general_cnav_duree_assurance_chomage_annuelle``, ``…_autre_annuelle``),
et les mène jusqu'à la pension. Ce qui se confronte est donc ce que ces
trimestres deviennent : la durée d'assurance, le plafond de quatre par année,
la décote, la surcote, la proratisation, le minimum contributif et le salaire
annuel moyen. Sa convention suit ; le témoin la porte, et
``tests/test_oracle_periodes_assimilees.py`` la vérifie avant de comparer.

LA CONVENTION DE TRADUCTION.

* **Les salariés** sont non-cadres du privé, nés un 1er janvier, au seul
  régime général, et liquident au 1er janvier de ``liquidation``, de 2016 à
  2021 : les stages de formation ne valident qu'à partir de 2015, et la table
  de revalorisation d'OpenFisca s'arrête à 2023.
* **Les salaires** sont donnés année par année, de ``debut`` à
  ``liquidation`` exclue, et portés tels quels des deux côtés ; au dépôt,
  chaque année valide les trimestres que son salaire achète, comme chez
  OpenFisca.
* **Les périodes** sont déclarées au dépôt telles que la chronologie les
  porte (``periodes``, et ``apprentissage`` pour les années d'un contrat) ;
  le dépôt en compte les trimestres, année par année, avant le plafond de
  l'année. Ces trimestres, écrits en clair (``trimestres_assimiles``), sont
  ce qu'OpenFisca reçoit : les stages de formation au chômage, sa catégorie
  « chômage, pré-retraite, reconversion et formation » ; les sportifs et le
  complément de l'apprentissage aux « autres périodes assimilées ».
* **Ce qui se compare.** La durée d'assurance et la durée cotisée, la décote
  et la surcote en trimestres, le taux, le coefficient de proratisation, le
  minimum contributif, et la pension rapportée au salaire annuel moyen, qui
  laisse de côté les coefficients de revalorisation (famille précédente).
* **Ce qui ne se traduit pas.** La règle qui compte les trimestres d'une
  période — cinquante jours de stage, quatre-vingt-dix jours d'inscription,
  la durée du contrat —, qu'OpenFisca n'a pas ; les stages d'insertion et le
  congé supplémentaire de naissance, qui ne valident que pour une pension
  prenant effet après le 1er septembre 2023 ou le 1er juillet 2026, hors de
  sa table ; l'année de la liquidation, aucun profil ne partant en cours
  d'année.

Ce que la confrontation a trouvé, le 16 octobre 2026 : rien chez nous. Les
trimestres assimilés comptent à la durée, au taux et à la proratisation, et ne
comptent ni à la durée cotisée, ni à la surcote, ni à la majoration du minimum
contributif et à son seuil de 120 trimestres cotisés, des deux côtés ; le
plafond de quatre par année, l'exclusion du salaire annuel moyen d'une année
dont le salaire n'achète pas un trimestre, concordent. Un écart chez OpenFisca,
hors de cette famille mais trouvé par elle :

* **La surcote de l'année de l'âge légal.** OpenFisca ne compte aucun
  trimestre de surcote l'année où le trimestre civil qui suit l'âge légal
  commence après le 1er janvier (``regime_general_cnav_surcote_trimestres``,
  formule de 2004 : ``ouverture_des_droits_date_surcote <= period.start``).
  Né le 1er janvier 1955, soixante-deux ans le 1er janvier 2017, il perd les
  trois trimestres d'avril à décembre 2017 ; D. 351-1-4 retient, l'année où
  l'âge est atteint, « un nombre de trimestres égal au nombre de trimestres
  civils entiers suivant celui au cours duquel cet âge a été atteint ».

Le fichier produit, ``tests/temoins/openfisca_periodes_assimilees.json``, est
VERSIONNÉ : le test rejoue la confrontation sur un dépôt fraîchement cloné,
sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SORTIE = Path("tests/temoins/openfisca_periodes_assimilees.json")

#: Voir ``openfisca_regime_general.py`` : sans ces réglages, OpenFisca rend
#: zéro en silence.
RECURSION = 20_000
SPIRALES = 100

#: Les motifs du dépôt, et la catégorie d'OpenFisca qui reçoit leurs
#: trimestres (``TypesStatutDuCotisant``, guide EIC 2013).
STAGE = "stage_de_formation_professionnelle"
SPORTIF = "sportif_de_haut_niveau"
APPRENTISSAGE = "apprentissage"
CATEGORIES = {STAGE: "chomage", SPORTIF: "autre", APPRENTISSAGE: "autre"}

#: La convention, telle que le témoin la porte.
CONVENTION = {
    "date_de_naissance": "le 1er janvier de `naissance`",
    "sexe": "faux (`sexe` H)",
    "liquidation_date": "le 1er janvier de `liquidation`, au régime général",
    "salaire_de_base": "`salaires`, année par année, de `debut` à `liquidation` exclue",
    "categorie_salarie": "non-cadre du privé",
    "periodes": (
        "Au dépôt : `periodes`, telles que la chronologie les porte, et les "
        "années `apprentissage` d'un contrat ; il en compte les trimestres, "
        "année par année, avant le plafond de l'année."
    ),
    "trimestres_assimiles": (
        "Chez OpenFisca : ceux que le dépôt compte, par catégorie — les stages "
        "de formation à `duree_assurance_chomage_annuelle`, les sportifs et le "
        "complément de l'apprentissage à `duree_assurance_autre_annuelle`."
    ),
    "comparaison": (
        "La durée d'assurance et la durée cotisée, la décote et la surcote, le "
        "taux, la proratisation, le minimum contributif, et la pension "
        "rapportée au salaire annuel moyen."
    ),
    "non_traduit": (
        "La règle qui compte les trimestres d'une période ; les stages "
        "d'insertion et le congé supplémentaire de naissance, qui ne valident "
        "qu'après 2023 ; l'année de la liquidation."
    ),
}


def _constants(debut: int, fin: int, salaire: float) -> dict[int, float]:
    return {a: salaire for a in range(debut, fin)}


def _avec(salaires: dict[int, float], autres: dict[int, float]) -> dict[int, float]:
    return {**salaires, **autres}


#: Profils confrontés. ``regle`` dit ce que chacun éprouve ; ``objet``, en
#: clair ; ``trimestres_assimiles``, ce que le dépôt compte de ses périodes,
#: par motif et par année, avant le plafond de l'année.
PROFILS: tuple[dict, ...] = (
    {"code": "formation_sans_salaire", "regle": "duree",
     "naissance": 1958, "liquidation": 2021,
     "salaires": _avec(_constants(1980, 2021, 25000.0), {2016: 0.0, 2017: 0.0}),
     "periodes": [{"motif": STAGE, "debut": "2016-03", "fin": "2017-06"}],
     "trimestres_assimiles": {STAGE: {2016: 6, 2017: 3}},
     "objet": "quinze mois de stage sans salaire : six trimestres en 2016, "
              "ramenés à quatre, trois en 2017"},
    {"code": "formation_en_jours", "regle": "duree",
     "naissance": 1956, "liquidation": 2019,
     "salaires": _avec(_constants(1978, 2019, 20000.0), {2015: 0.0}),
     "periodes": [{"motif": STAGE, "debut": "2015-02", "fin": "2015-12", "jours": 149}],
     "trimestres_assimiles": {STAGE: {2015: 2}},
     "objet": "cent quarante-neuf jours de stage déclarés : deux trimestres"},
    {"code": "formation_et_salaire", "regle": "plafond_annuel",
     "naissance": 1957, "liquidation": 2020,
     "salaires": _avec(_constants(1979, 2020, 22000.0), {2016: 3500.0, 2017: 5200.0}),
     "periodes": [{"motif": STAGE, "debut": "2016-05", "fin": "2016-11"},
                  {"motif": STAGE, "debut": "2017-01", "fin": "2017-12"}],
     "trimestres_assimiles": {STAGE: {2016: 3, 2017: 6}},
     "objet": "un salaire qui achète deux et trois trimestres, et des stages "
              "qui en ajoutent : quatre par année au plus"},
    {"code": "annee_faible_et_stage", "regle": "salaire_annuel_moyen",
     "naissance": 1957, "liquidation": 2020,
     "salaires": _avec(_constants(2000, 2020, 18000.0), {2016: 900.0}),
     "periodes": [{"motif": STAGE, "debut": "2016-01", "fin": "2017-01"}],
     "trimestres_assimiles": {STAGE: {2016: 7}},
     "objet": "vingt ans, dont un de 900 € et d'un an de stage : quatre "
              "trimestres, et l'année hors du salaire annuel moyen"},
    {"code": "annee_sans_salaire_et_stage", "regle": "salaire_annuel_moyen",
     "naissance": 1957, "liquidation": 2020,
     "salaires": _avec(_constants(2000, 2020, 18000.0), {2016: 0.0}),
     "periodes": [{"motif": STAGE, "debut": "2016-01", "fin": "2017-01"}],
     "trimestres_assimiles": {STAGE: {2016: 7}},
     "objet": "le jumeau du précédent, sans les 900 € : le même salaire "
              "annuel moyen"},
    {"code": "sportif", "regle": "duree",
     "naissance": 1957, "liquidation": 2019,
     "salaires": _avec(_constants(1980, 2019, 24000.0), {a: 4000.0 for a in range(2012, 2016)}),
     "periodes": [{"motif": SPORTIF, "debut": "2012-01", "fin": "2016-01"}],
     "trimestres_assimiles": {SPORTIF: {2012: 4, 2013: 4, 2014: 4, 2015: 4}},
     "objet": "quatre ans sur la liste des sportifs de haut niveau, à 4 000 € "
              "par an : quatre trimestres chaque année"},
    {"code": "apprenti", "regle": "duree",
     "naissance": 1957, "liquidation": 2019,
     "salaires": _avec(_constants(1980, 2019, 24000.0), {2014: 500.0, 2015: 1500.0, 2016: 1000.0}),
     "periodes": [], "apprentissage": [2014, 2015, 2016],
     "trimestres_assimiles": {APPRENTISSAGE: {2014: 4, 2015: 3, 2016: 4}},
     "objet": "trois ans d'apprentissage, sans limite d'âge pour un travailleur "
              "handicapé : le complément du contrat"},
    {"code": "surcote_et_stage", "regle": "surcote",
     "naissance": 1955, "liquidation": 2020,
     "salaires": _avec(_constants(1975, 2020, 30000.0), {2018: 0.0}),
     "periodes": [{"motif": STAGE, "debut": "2018-01", "fin": "2019-01"}],
     "trimestres_assimiles": {STAGE: {2018: 7}},
     "objet": "un an de stage après l'âge légal et la durée requise : aucune "
              "surcote"},
    {"code": "surcote_sans_stage", "regle": "surcote",
     "naissance": 1955, "liquidation": 2020,
     "salaires": _constants(1975, 2020, 30000.0),
     "periodes": [], "trimestres_assimiles": {},
     "objet": "le jumeau du précédent, qui travaille : la surcote de 2017 à "
              "2019"},
    {"code": "minimum_contributif_et_stage", "regle": "minimum_contributif",
     "naissance": 1951, "liquidation": 2016,
     "salaires": _avec(_constants(1980, 2016, 7000.0), {2015: 0.0}),
     "periodes": [{"motif": STAGE, "debut": "2015-01", "fin": "2016-01"}],
     "trimestres_assimiles": {STAGE: {2015: 7}},
     "objet": "un petit salaire et un an de stage, parti à soixante-cinq ans : "
              "la majoration sur les seuls trimestres cotisés"},
    {"code": "minimum_contributif_sous_120_cotises", "regle": "minimum_contributif",
     "naissance": 1951, "liquidation": 2016,
     "salaires": _avec(_constants(1985, 2016, 7000.0), {2015: 0.0}),
     "periodes": [{"motif": STAGE, "debut": "2015-01", "fin": "2016-01"}],
     "trimestres_assimiles": {STAGE: {2015: 7}},
     "objet": "cent vingt trimestres dont cent seize cotisés : pas de "
              "majoration"},
)

#: Grandeurs relevées.
GRANDEURS = {
    "salaire_de_reference": "regime_general_cnav_salaire_de_reference",
    "duree_assurance": "regime_general_cnav_duree_assurance",
    "duree_cotisee": "regime_general_cnav_duree_assurance_cotisee",
    "decote_trimestres": "regime_general_cnav_decote_trimestres",
    "surcote_trimestres": "regime_general_cnav_surcote_trimestres",
    "taux_de_liquidation": "regime_general_cnav_taux_de_liquidation",
    "coefficient_de_proratisation": "regime_general_cnav_coefficient_de_proratisation",
    "pension_minimale": "regime_general_cnav_pension_minimale",
    "pension_brute": "regime_general_cnav_pension_brute",
}


def par_categorie(profil: dict) -> dict[str, dict[int, int]]:
    """Les trimestres assimilés du profil, par catégorie d'OpenFisca."""
    categories: dict[str, dict[int, int]] = {}
    for motif, annees in profil["trimestres_assimiles"].items():
        cible = categories.setdefault(CATEGORIES[motif], {})
        for annee, trimestres in annees.items():
            cible[annee] = cible.get(annee, 0) + trimestres
    return categories


def entrees(profil: dict) -> dict:
    """La situation qu'OpenFisca reçoit."""
    categories = par_categorie(profil)
    annees = sorted(set(profil["salaires"]).union(*(c.keys() for c in categories.values())))
    situation = {
        "date_de_naissance": {"ETERNITY": f"{profil['naissance']}-01-01"},
        "sexe": {"ETERNITY": False},
        "nombre_enfants": {"ETERNITY": 0},
        "regime_general_cnav_liquidation_date": {
            "ETERNITY": f"{profil['liquidation']}-01-01"},
        "regime_general_cnav_salaire_de_base": {
            str(a): profil["salaires"].get(a, 0.0) for a in annees},
        "statut_du_cotisant": {str(a): "emploi" for a in annees},
        "categorie_salarie": {str(a): "prive_non_cadre" for a in annees},
    }
    for categorie, trimestres in categories.items():
        situation[f"regime_general_cnav_duree_assurance_{categorie}_annuelle"] = {
            str(a): t for a, t in trimestres.items()}
    return situation


def calculer(profil: dict, tbs) -> dict:
    from openfisca_core.simulation_builder import SimulationBuilder

    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": entrees(profil)}})
    simulation.max_spiral_loops = SPIRALES
    return {nom: float(simulation.calculate(variable, profil["liquidation"])[0])
            for nom, variable in GRANDEURS.items()}


def ecrit(profil: dict) -> dict:
    """Le profil tel que le témoin l'écrit : ses années en clair."""
    return {
        **profil,
        "salaires": {str(a): s for a, s in profil["salaires"].items()},
        "trimestres_assimiles": {
            motif: {str(a): t for a, t in annees.items()}
            for motif, annees in profil["trimestres_assimiles"].items()},
    }


def main(argv: list[str] | None = None) -> int:
    sys.setrecursionlimit(RECURSION)
    try:
        from openfisca_france_pension import CountryTaxBenefitSystem
    except ImportError:
        print(
            "OpenFisca-France-Pension n'est pas installé.\n"
            "    pip install OpenFisca-France-Pension\n"
            "Il n'est PAS une dépendance du dépôt : le témoin qu'il produit est "
            "versionné, et les tests s'en contentent.",
            file=sys.stderr,
        )
        return 1

    tbs = CountryTaxBenefitSystem()
    releves = {}
    for profil in PROFILS:
        mesures = calculer(profil, tbs)
        if mesures["duree_assurance"] <= 0 or mesures["salaire_de_reference"] <= 0:
            print(
                f"{profil['code']} : OpenFisca rend une durée ou un salaire nul "
                "— le déroulage récursif n'a pas eu lieu. Rien n'est écrit.",
                file=sys.stderr,
            )
            return 1
        releves[profil["code"]] = {"profil": ecrit(profil), "openfisca": mesures}
        print(f"{profil['code']:<38} durée {mesures['duree_assurance']:>5.0f}  "
              f"cotisée {mesures['duree_cotisee']:>5.0f}  "
              f"taux {mesures['taux_de_liquidation']:.5f}  "
              f"pension {mesures['pension_brute']:>9.2f} €")

    from importlib.metadata import PackageNotFoundError, version

    try:
        publiee = version("OpenFisca-France-Pension")
    except PackageNotFoundError:  # pragma: no cover - paquet posé à la main
        publiee = "inconnue"

    document = {
        "source": "OpenFisca-France-Pension",
        "version": publiee,
        "recupere_le": date.today().isoformat(),
        "famille": "les périodes assimilées du régime général, année par année",
        "avertissement": (
            "Deuxième implémentation, pas une source officielle. Il ne compte "
            "pas les trimestres d'une période assimilée : il reçoit ceux que le "
            "dépôt compte. Il ne compte aucune surcote l'année de l'âge légal "
            "quand le trimestre qui le suit commence après le 1er janvier."
        ),
        "perimetre": (
            "Régime général des non-cadres, stages de formation, sportifs de "
            "haut niveau et apprentissage, liquidés de 2016 à 2021, générations "
            "1951 à 1958."
        ),
        "convention": CONVENTION,
        "profils": releves,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"{SORTIE} : {len(releves)} profils")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
