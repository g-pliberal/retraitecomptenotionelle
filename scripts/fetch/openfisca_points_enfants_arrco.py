#!/usr/bin/env python3
"""L'oracle au-delà des carrières simples, sixième famille (action 153) : les
points enfants de l'Arrco et de l'Agirc — la majoration pour enfants nés ou
élevés, son plafond, la majoration pour enfants à charge — et la minoration
qui les frappe, le coefficient d'anticipation, par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_points_enfants_arrco.py

Le frère de ``openfisca_arrco.py``, dont il reprend la carrière, et de
``openfisca_minima.py``, dont il reprend la forme. ``tests/test_oracle.py``
confrontait déjà les points de l'Arrco et son coefficient d'anticipation, sans
enfant ; celle-ci éprouve ce qu'il ne voyait pas : le taux de chaque période
d'acquisition, le plafond en euros et la génération qu'il touche, la
majoration pour enfants à charge, et l'assiette de chacune sous un
coefficient d'anticipation. Sa convention suit ; le témoin la porte, et
``tests/test_oracle_points_enfants_arrco.py`` la vérifie avant de comparer.

LA CONVENTION DE TRADUCTION.

* **Les salariés** ont la carrière de ``openfisca_arrco.py`` : nés un
  1er janvier, entrés au 1er janvier de ``debut``, 1999 au plus tôt — ses
  points d'avant l'unification sont en unité UNIRS non convertie —, à
  salaire nominal constant, quatre trimestres par an, liquidant au
  1er janvier de ``liquidation``, 2018 au plus tard — son régime unifié de
  2019 lève une exception. Non-cadres, sauf le cadre du plafond par régime.
* **Les enfants.** OpenFisca en lit deux nombres, ``nombre_enfants`` et
  ``nombre_enfants_a_charge`` ; le dépôt, des naissances datées. Les enfants
  nés ou élevés naissent le 1er juin des 25e, 26e, ... années du parent ; les
  enfants à charge, le 1er juin de ``liquidation - 12``, ``- 10``, ... : ils ont
  moins de dix-huit ans à la date d'effet, et comptent dans les deux nombres.
  Tous naissent avant 2010, et le père n'a pas de majoration de durée au
  régime général : la décote, d'où l'Arrco tire son coefficient, ne bouge pas.
* **Ce qui se compare** : la majoration de chaque régime, au centime, telle
  que la pension la sert — chez OpenFisca, la majoration de points fois le
  coefficient d'anticipation, puisqu'il les minore ensemble ; au dépôt, sa part
  de la majoration pour enfants. Et la pension de l'Arrco, coefficient compris.
* **Ce qui ne se traduit pas.** Les points d'avant 1999 et leur majoration de
  10 à 30 % ; la condition d'avoir élevé l'enfant neuf ans avant ses seize ans,
  que les naissances remplissent ; la date de naissance du 2 août 1951, coupée
  à l'année au dépôt et au jour chez OpenFisca, qu'aucun profil n'approche ;
  les points de l'Agirc du cadre, que ``tests/test_oracle.py`` confronte.

Ce que la confrontation a trouvé, le 16 octobre 2026 : une erreur chez nous,
une chez OpenFisca.

* **Le plafond, chez nous.** Le dépôt servait de 1999 à 2018 le plafond du
  régime unifié — 2 367,48 € en 2025, deux fois celui d'un seul régime, et
  commun à l'Agirc et à l'Arrco. L'accord du 18 mars 2011 plafonne à
  « 1 000 € par an au titre de l'Agirc et à 1 000 € par an au titre de
  l'Arrco », « revalorisé comme le point de retraite », les allocations
  prenant effet à compter du 1er janvier 2012 (circulaire Agirc-Arrco du
  7 juillet 2011, point 3.3.1). Corrigé dans les deux moteurs : la
  majoration d'un non-cadre de 2018 qui gagnait 100 000 € passe de 1 104 € à
  1 031 €, celle de l'Agirc d'un cadre de 1 028 € à part.
* **Les droits bruts, chez OpenFisca.** Il minore la majoration pour enfants
  à charge du coefficient d'anticipation, comme l'allocation ; de 2012 à
  2018, elle est « égale à 5 % des droits bruts de l'ensemble de la
  carrière par enfant à charge » (accord du 8 décembre 1961, annexe A,
  article 17, dans sa rédaction de l'accord du 18 mars 2011).

Le fichier produit, ``tests/temoins/openfisca_points_enfants_arrco.json``,
est VERSIONNÉ : le test rejoue la confrontation sur un dépôt fraîchement
cloné, sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SORTIE = Path("tests/temoins/openfisca_points_enfants_arrco.json")

#: Voir ``openfisca_arrco.py`` et ``openfisca_agirc.py`` : sans ces réglages,
#: OpenFisca rend zéro en silence, ou remonte l'Agirc jusqu'en 1947, où son
#: prix d'achat manque.
RECURSION = 20_000
SPIRALES = 100
PREMIERE_ANNEE_SURE_AGIRC = 1948

#: La convention, telle que le témoin la porte.
CONVENTION = {
    "date_de_naissance": "le 1er janvier de `naissance`",
    "sexe": "faux (`sexe` H)",
    "liquidation_date": "le 1er janvier de `liquidation`, au régime général, à "
                        "l'Arrco et à l'Agirc",
    "salaire_de_base": "le salaire, chaque année de `debut` à `liquidation` exclue",
    "categorie_salarie": "non-cadre du privé, ou cadre (`cadre`)",
    "nombre_enfants": "les enfants nés ou élevés et les enfants à charge",
    "nombre_enfants_a_charge": "les enfants à charge, l'année de `liquidation`",
    "naissances": (
        "Au dépôt : les enfants nés ou élevés le 1er juin des 25e, 26e, ... "
        "années du parent ; les enfants à charge le 1er juin de "
        "`liquidation - 12`, `- 10`, ..."
    ),
    "comparaison": (
        "La majoration de chaque régime telle que la pension la sert : chez "
        "OpenFisca, la majoration fois le coefficient d'anticipation ; au dépôt, "
        "sa part de la majoration pour enfants."
    ),
    "non_traduit": (
        "Les points d'avant 1999 ; la condition des neuf ans avant seize ans ; "
        "le 2 août 1951, qu'aucun profil n'approche ; les points de l'Agirc du "
        "cadre, confrontés par tests/test_oracle.py."
    ),
}

#: Profils confrontés. ``regle`` dit ce que chacun éprouve ; ``objet``, en clair.
PROFILS: tuple[dict, ...] = (
    {"code": "trois_enfants_en_2012", "regle": "nes_ou_eleves",
     "naissance": 1947, "debut": 1999, "liquidation": 2012, "salaire": 22000.0,
     "enfants": 3, "a_charge": 0,
     "objet": "des points de 1999 à 2011 : 5 %"},
    {"code": "trois_enfants_en_2018", "regle": "nes_ou_eleves",
     "naissance": 1952, "debut": 1999, "liquidation": 2018, "salaire": 22000.0,
     "enfants": 3, "a_charge": 0,
     "objet": "5 % jusqu'en 2011, 10 % depuis, sous le plafond"},
    {"code": "quatre_enfants_en_2018", "regle": "nes_ou_eleves",
     "naissance": 1952, "debut": 1999, "liquidation": 2018, "salaire": 22000.0,
     "enfants": 4, "a_charge": 0,
     "objet": "un quatrième enfant n'ajoute rien depuis 1999"},
    {"code": "deux_enfants_en_2018", "regle": "sans_majoration",
     "naissance": 1952, "debut": 1999, "liquidation": 2018, "salaire": 22000.0,
     "enfants": 2, "a_charge": 0,
     "objet": "deux enfants qui ne sont plus à charge : rien"},
    {"code": "plafond_arrco_en_2018", "regle": "plafond",
     "naissance": 1952, "debut": 1999, "liquidation": 2018, "salaire": 100000.0,
     "enfants": 3, "a_charge": 0,
     "objet": "deux tranches de l'Arrco, une majoration au-delà de 1 000 € de "
              "2012 revalorisés"},
    {"code": "plafond_par_regime_en_2018", "regle": "plafond",
     "naissance": 1952, "debut": 1999, "liquidation": 2018, "salaire": 90000.0,
     "enfants": 3, "a_charge": 0, "cadre": True,
     "objet": "un cadre : l'Agirc au plafond, l'Arrco sous le sien"},
    {"code": "generation_1950_en_2015", "regle": "generation",
     "naissance": 1950, "debut": 1999, "liquidation": 2015, "salaire": 100000.0,
     "enfants": 3, "a_charge": 0,
     "objet": "né avant le 2 août 1951 : aucun plafond"},
    {"code": "deux_a_charge_en_2018", "regle": "a_charge",
     "naissance": 1952, "debut": 1999, "liquidation": 2018, "salaire": 22000.0,
     "enfants": 0, "a_charge": 2,
     "objet": "deux enfants à charge, sans décote : 5 % chacun"},
    {"code": "un_a_charge_decote_en_2011", "regle": "a_charge",
     "naissance": 1948, "debut": 1999, "liquidation": 2011, "salaire": 23000.0,
     "enfants": 0, "a_charge": 1,
     "objet": "un enfant à charge, huit trimestres de décote, avant 2012 : 5 % "
              "de l'allocation, coefficient compris"},
    {"code": "deux_a_charge_decote_en_2014", "regle": "droits_bruts",
     "naissance": 1951, "debut": 1999, "liquidation": 2014, "salaire": 22000.0,
     "enfants": 0, "a_charge": 2,
     "objet": "deux enfants à charge, huit trimestres de décote, après 2011 : "
              "5 % des droits bruts, sans le coefficient"},
    {"code": "trois_enfants_decote_en_2011", "regle": "minoration",
     "naissance": 1948, "debut": 1999, "liquidation": 2011, "salaire": 23000.0,
     "enfants": 3, "a_charge": 0,
     "objet": "huit trimestres de décote : 0,92 sur l'allocation et sa "
              "majoration"},
    {"code": "trois_enfants_a_soixante_ans_en_2004", "regle": "minoration",
     "naissance": 1944, "debut": 1999, "liquidation": 2004, "salaire": 22000.0,
     "enfants": 3, "a_charge": 0,
     "objet": "parti à soixante ans, vingt trimestres de décote par l'âge : 0,78"},
    {"code": "trois_enfants_quinze_trimestres_en_2014", "regle": "troncature",
     "naissance": 1952, "debut": 1999, "liquidation": 2014, "salaire": 22000.0,
     "enfants": 3, "a_charge": 0,
     "objet": "quinze trimestres de décote : le barème au trimestre, que "
              "OpenFisca tronque à l'année"},
)

#: Grandeurs relevées, par régime.
GRANDEURS = (
    "points", "points_enfants", "points_enfants_nes_et_eleves",
    "points_enfants_a_charge", "majoration_pension", "coefficient_de_minoration",
    "pension_brute", "pension",
)


def entrees(profil: dict) -> dict:
    """La situation qu'OpenFisca reçoit."""
    annees = [str(a) for a in range(profil["debut"], profil["liquidation"])]
    liquidation = {"ETERNITY": f"{profil['liquidation']}-01-01"}
    categorie = "prive_cadre" if profil.get("cadre") else "prive_non_cadre"
    return {
        "date_de_naissance": {"ETERNITY": f"{profil['naissance']}-01-01"},
        "sexe": {"ETERNITY": False},
        "nombre_enfants": {"ETERNITY": profil["enfants"] + profil["a_charge"]},
        "nombre_enfants_a_charge": {str(profil["liquidation"]): profil["a_charge"]},
        "regime_general_cnav_liquidation_date": liquidation,
        "arrco_liquidation_date": liquidation,
        "agirc_liquidation_date": liquidation,
        "regime_general_cnav_salaire_de_base": {a: profil["salaire"] for a in annees},
        "statut_du_cotisant": {a: "emploi" for a in annees},
        "categorie_salarie": {a: categorie for a in annees},
    }


def calculer(profil: dict, tbs) -> dict:
    """Relève les grandeurs de l'Arrco, et de l'Agirc du cadre."""
    from openfisca_core.simulation_builder import SimulationBuilder

    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": entrees(profil)}})
    annee = profil["liquidation"]
    # L'Agirc remonte ses points jusqu'à la première année sûre de son barème.
    simulation.max_spiral_loops = (annee - PREMIERE_ANNEE_SURE_AGIRC
                                   if profil.get("cadre") else SPIRALES)
    mesures: dict = {"decote_trimestres_regime_general": float(
        simulation.calculate("regime_general_cnav_decote_trimestres", annee)[0])}
    for regime in ("arrco", "agirc") if profil.get("cadre") else ("arrco",):
        mesures[regime] = {
            grandeur: float(simulation.calculate(f"{regime}_{grandeur}", annee)[0])
            for grandeur in GRANDEURS
        }
    return mesures


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
        if any(r["points"] <= 0 or r["pension_brute"] <= 0
               for nom, r in mesures.items() if isinstance(r, dict)):
            print(
                f"{profil['code']} : OpenFisca rend des points ou une rente nuls "
                "— le déroulage récursif n'a pas eu lieu. Rien n'est écrit.",
                file=sys.stderr,
            )
            return 1
        releves[profil["code"]] = {"profil": profil, "openfisca": mesures}
        arrco = mesures["arrco"]
        print(f"{profil['code']:<40} majoration {arrco['majoration_pension']:>8.2f}  "
              f"coefficient {arrco['coefficient_de_minoration']:.4f}  "
              f"pension {arrco['pension']:>9.2f} €")

    from importlib.metadata import PackageNotFoundError, version

    try:
        publiee = version("OpenFisca-France-Pension")
    except PackageNotFoundError:  # pragma: no cover - paquet posé à la main
        publiee = "inconnue"

    document = {
        "source": "OpenFisca-France-Pension",
        "version": publiee,
        "recupere_le": date.today().isoformat(),
        "famille": "les points enfants de l'Arrco et de l'Agirc, et la minoration "
                   "qui les frappe",
        "avertissement": (
            "Deuxième implémentation, pas une source officielle. Il minore la "
            "majoration pour enfants à charge du coefficient d'anticipation, quand "
            "elle porte de 2012 à 2018 sur les droits bruts ; il ne lit son "
            "coefficient que par année entière."
        ),
        "perimetre": (
            "Arrco des non-cadres, et Agirc d'un cadre, carrières continues à "
            "salaire nominal constant commençant en 1999 et liquidées de 2004 à "
            "2018, de zéro à quatre enfants."
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
