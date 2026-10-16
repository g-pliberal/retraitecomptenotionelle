#!/usr/bin/env python3
"""L'oracle au-delà des carrières simples, septième famille (action 153) : le
salaire annuel moyen du régime général sur des salaires qui varient, par
OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_salaire_annuel_moyen.py

Le frère de ``openfisca_regime_general.py``, dont il reprend la carrière, et de
``openfisca_points_enfants_arrco.py``, dont il reprend la forme.
``tests/test_oracle.py`` confrontait déjà le salaire annuel moyen, mais sur des
salaires nominaux constants, où toutes les années se valent : ni le choix des
meilleures, ni le plafond d'une année, ni l'exclusion d'une année faible n'y
jouaient. Celle-ci les éprouve, et sépare ce qui tient à la règle de ce qui
tient aux coefficients de revalorisation. Sa convention suit ; le témoin la
porte, et ``tests/test_oracle_salaire_annuel_moyen.py`` la vérifie avant de
comparer.

LA CONVENTION DE TRADUCTION.

* **Les salariés** sont non-cadres du privé, nés un 1er janvier, au seul
  régime général, et liquident au 1er janvier de ``liquidation``, de 1994 —
  la première formule par génération d'OpenFisca — à 2021 : sa table de
  revalorisation s'arrête à 2023.
* **Les salaires** sont donnés année par année, de ``debut`` à
  ``liquidation`` exclue, et portés tels quels des deux côtés ; le témoin les
  écrit en clair. Au dépôt, chaque année valide les trimestres que son
  salaire achète (``trimestres_valides`` du dépôt) : OpenFisca les tire du
  salaire de même.
* **Ce qui se compare.** Le salaire annuel moyen et la pension de base, et,
  pour séparer la règle des coefficients, le détail qu'OpenFisca forme chaque
  année : le salaire retenu, plafonné, exclu ou non, et le coefficient de
  revalorisation qu'il lui applique. Le témoin les relève dans ses
  paramètres, à la date d'effet, avec le nombre d'années qu'il retient.
* **Ce qui ne se traduit pas.** L'assurance vieillesse des parents au foyer,
  les périodes assimilées, une année incomplète ; le salaire d'avant les
  onze ans, qu'OpenFisca ne lit pas et qu'aucun profil n'a.

Ce que la confrontation a trouvé, le 16 octobre 2026 : rien chez nous ; sa
règle, rejouée sous nos coefficients et notre plafond, rend notre salaire au
centime. Quatre écarts chez OpenFisca.

* **Les coefficients de revalorisation.** OpenFisca compose ses coefficients
  en multipliant une série annuelle (``reval_s``) ; la Cnav publie chaque
  colonne entière dans sa circulaire, que le dépôt lit
  (``legislation/revalorisation_salaires.csv``). Les deux s'écartent de −9 % à
  +2 % selon l'année : pour un départ en 2018, OpenFisca applique 21,89 aux
  salaires de 1961, la circulaire du 1er octobre 2017 20,034 ; 1,000 à ceux de
  2017, la circulaire 1,008. C'est là, et non dans la seule revalorisation de
  juillet 2022, que naissent les écarts de ``tests/test_oracle.py``.
* **Le plafond d'une année à deux plafonds.** Le plafond annuel est la somme
  des plafonds mensuels : 6 840 F en 1960, 8 100 F en 1961. OpenFisca lit
  celui du 1er janvier, 6 600 et 7 200 F.
* **Le calcul trimestriel.** Jusqu'au 30 juin 1995, la somme des salaires
  retenus se rapporte à leurs trimestres, multipliée par quatre (circulaire
  Cnav 1/73) ; OpenFisca divise par le nombre d'années dès 1994.
* **La décote au jour anniversaire**, hors de cette famille mais trouvée par
  elle : OpenFisca tire l'âge en mois d'une durée en jours au mois moyen de
  numpy, et tronque ; né le 1er janvier 1950, parti le 1er janvier 2012, il a
  743 mois, et treize trimestres de décote au lieu de douze.

Le fichier produit, ``tests/temoins/openfisca_salaire_annuel_moyen.json``, est
VERSIONNÉ : le test rejoue la confrontation sur un dépôt fraîchement cloné,
sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SORTIE = Path("tests/temoins/openfisca_salaire_annuel_moyen.json")

#: Voir ``openfisca_regime_general.py`` : sans ces réglages, OpenFisca rend
#: zéro en silence.
RECURSION = 20_000
SPIRALES = 100

#: OpenFisca ne lit pas les salaires d'avant les onze ans (``OFFSET``).
DECALAGE = 10

#: La convention, telle que le témoin la porte.
CONVENTION = {
    "date_de_naissance": "le 1er janvier de `naissance`",
    "sexe": "faux (`sexe` H)",
    "liquidation_date": "le 1er janvier de `liquidation`, au régime général",
    "salaire_de_base": "`salaires`, année par année, de `debut` à `liquidation` exclue",
    "categorie_salarie": "non-cadre du privé",
    "trimestres": (
        "Au dépôt : ceux que le salaire de l'année achète "
        "(`trimestres_valides`) ; chez OpenFisca, tirés du salaire de même."
    ),
    "comparaison": (
        "Le salaire annuel moyen et la pension de base ; et, année par année, "
        "le salaire qu'OpenFisca retient, plafonné et exclu ou non, et le "
        "coefficient qu'il lui applique, relevés dans ses paramètres."
    ),
    "non_traduit": (
        "L'AVPF, les périodes assimilées, les années incomplètes ; les salaires "
        "d'avant les onze ans, qu'aucun profil n'a."
    ),
}


def _croissants(debut: int, fin: int, premier: float, pas: float) -> dict[int, float]:
    return {a: round(premier + pas * (a - debut), 2) for a in range(debut, fin)}


def _avec(salaires: dict[int, float], autres: dict[int, float]) -> dict[int, float]:
    return {**salaires, **autres}


#: Profils confrontés. ``regle`` dit ce que chacun éprouve ; ``objet``, en clair.
PROFILS: tuple[dict, ...] = (
    {"code": "croissant_en_2017", "regle": "meilleures",
     "naissance": 1955, "debut": 1977, "liquidation": 2017,
     "salaires": _croissants(1977, 2017, 6000.0, 700.0),
     "objet": "un salaire qui croît de 700 € par an : les vingt-cinq dernières"},
    {"code": "decroissant_en_2015", "regle": "meilleures",
     "naissance": 1953, "debut": 1975, "liquidation": 2015,
     "salaires": _croissants(1975, 2015, 30000.0, -500.0),
     "objet": "un salaire qui décroît : les meilleures sont revalorisées, pas "
              "les plus fortes en euros courants"},
    {"code": "en_dents_de_scie_en_2012", "regle": "meilleures",
     "naissance": 1950, "debut": 1972, "liquidation": 2012,
     "salaires": {a: (24000.0 if a % 3 else 9000.0) for a in range(1972, 2012)},
     "objet": "une année sur trois à 9 000 € : celles-là d'abord écartées"},
    {"code": "au_plafond_en_2014", "regle": "plafond",
     "naissance": 1952, "debut": 1976, "liquidation": 2014,
     "salaires": _avec(_croissants(1976, 2014, 9000.0, 600.0),
                       {a: 80000.0 for a in range(1995, 2005)}),
     "objet": "dix ans à 80 000 €, écrêtés au plafond de chaque année"},
    {"code": "annees_sans_trimestre_en_2016", "regle": "sans_trimestre",
     "naissance": 1954, "debut": 1996, "liquidation": 2016,
     "salaires": _avec({a: 20000.0 for a in range(1996, 2016)},
                       {2001: 900.0, 2006: 1000.0, 2011: 1100.0}),
     "objet": "vingt ans, dont trois sous le salaire d'un trimestre : exclues "
              "depuis 2004"},
    {"code": "annees_faibles_en_2003", "regle": "avant_2004",
     "naissance": 1943, "debut": 1988, "liquidation": 2003,
     "salaires": _avec({a: 18000.0 for a in range(1988, 2003)},
                       {1992: 700.0, 1997: 800.0}),
     "objet": "quinze ans, dont deux sous le salaire d'un trimestre : retenues "
              "avant 2004"},
    {"code": "carriere_courte_en_2012", "regle": "moins_que_le_nombre",
     "naissance": 1950, "debut": 1996, "liquidation": 2012,
     "salaires": _croissants(1996, 2012, 15000.0, 900.0),
     "objet": "seize ans quand la génération en retient vingt-cinq : toutes"},
    {"code": "generation_1938_en_1998", "regle": "generation",
     "naissance": 1938, "debut": 1960, "liquidation": 1998,
     "salaires": _croissants(1960, 1998, 2000.0, 450.0),
     "objet": "quinze années pour la génération 1938"},
    {"code": "generation_1944_en_2004", "regle": "generation",
     "naissance": 1944, "debut": 1966, "liquidation": 2004,
     "salaires": _croissants(1966, 2004, 3500.0, 550.0),
     "objet": "vingt et une années pour la génération 1944"},
    {"code": "generation_1946_en_2009", "regle": "generation",
     "naissance": 1946, "debut": 1968, "liquidation": 2009,
     "salaires": _croissants(1968, 2009, 3000.0, 600.0),
     "objet": "vingt-trois années, parti à soixante-trois ans"},
    {"code": "trois_trimestres_en_1994", "regle": "trimestriel",
     "naissance": 1934, "debut": 1985, "liquidation": 1994,
     "salaires": _avec({a: 9000.0 for a in range(1985, 1994)}, {1993: 3500.0}),
     "objet": "neuf ans pour onze retenus, dont un de trois trimestres : avant "
              "juillet 1995, la somme rapportée aux trimestres"},
    {"code": "quatre_trimestres_en_1994", "regle": "generation",
     "naissance": 1934, "debut": 1956, "liquidation": 1994,
     "salaires": _croissants(1956, 1994, 900.0, 300.0),
     "objet": "onze années pour la génération 1934, toutes de quatre trimestres"},
)

#: Grandeurs relevées.
GRANDEURS = {
    "salaire_de_reference": "regime_general_cnav_salaire_de_reference",
    "duree_assurance": "regime_general_cnav_duree_assurance",
    "decote_trimestres": "regime_general_cnav_decote_trimestres",
    "taux_de_liquidation": "regime_general_cnav_taux_de_liquidation",
    "coefficient_de_proratisation": "regime_general_cnav_coefficient_de_proratisation",
    "pension_brute": "regime_general_cnav_pension_brute",
}


def entrees(profil: dict) -> dict:
    """La situation qu'OpenFisca reçoit."""
    salaires = {str(a): s for a, s in profil["salaires"].items()}
    return {
        "date_de_naissance": {"ETERNITY": f"{profil['naissance']}-01-01"},
        "sexe": {"ETERNITY": False},
        "nombre_enfants": {"ETERNITY": 0},
        "regime_general_cnav_liquidation_date": {
            "ETERNITY": f"{profil['liquidation']}-01-01"},
        "regime_general_cnav_salaire_de_base": salaires,
        "statut_du_cotisant": {a: "emploi" for a in salaires},
        "categorie_salarie": {a: "prive_non_cadre" for a in salaires},
    }


def detail(profil: dict, tbs) -> tuple[int, dict[str, dict]]:
    """Ce qu'OpenFisca forme chaque année, lu dans ses paramètres comme le fait
    ``regime_general_cnav_salaire_de_reference`` (formule de 1994) : le salaire
    plafonné, exclu depuis 2004 s'il n'achète pas un trimestre, et le
    coefficient cumulé de la date d'effet."""
    from openfisca_france_pension.variables.regime_general_cnav import (
        conversion_parametre_en_euros)

    liquidation = profil["liquidation"]
    regime = tbs.parameters(f"{liquidation}-01-01").retraites.secteur_prive.regime_general_cnav
    sam = regime.sam.nombre_annees_carriere_entrant_en_jeu_dans_determination_salaire_annuel_moyen
    import numpy as np

    nombre = int(sam[np.array([str(profil["naissance"])], dtype="datetime64[Y]")][0])
    cumulees = regime.revalorisation_salaire_cummulee
    annees = {}
    for annee in range(liquidation - 1, profil["naissance"] + DECALAGE, -1):
        salaire = profil["salaires"].get(annee, 0.0)
        if salaire <= 0:
            continue
        loi = tbs.parameters(f"{annee}-01-01")
        plafond = loi.prelevements_sociaux.pss.plafond_securite_sociale_annuel * (
            conversion_parametre_en_euros(annee))
        seuil = (loi.retraites.secteur_prive.regime_general_cnav.salval
                 .salaire_validant_trimestre.metropole * conversion_parametre_en_euros(annee))
        annees[str(annee)] = {
            "salaire": salaire,
            "plafond": float(plafond),
            "seuil_d_un_trimestre": float(seuil),
            "exclue": bool(liquidation >= 2004 and salaire < seuil),
            "coefficient": float(cumulees[str(annee)]),
        }
    return nombre, annees


def calculer(profil: dict, tbs) -> dict:
    from openfisca_core.simulation_builder import SimulationBuilder

    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": entrees(profil)}})
    simulation.max_spiral_loops = SPIRALES
    mesures = {nom: float(simulation.calculate(variable, profil["liquidation"])[0])
               for nom, variable in GRANDEURS.items()}
    mesures["nombre_d_annees"], mesures["annees"] = detail(profil, tbs)
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
        if mesures["duree_assurance"] <= 0 or mesures["salaire_de_reference"] <= 0:
            print(
                f"{profil['code']} : OpenFisca rend une durée ou un salaire nul "
                "— le déroulage récursif n'a pas eu lieu. Rien n'est écrit.",
                file=sys.stderr,
            )
            return 1
        ecrit = {**profil, "salaires": {str(a): s for a, s in profil["salaires"].items()}}
        releves[profil["code"]] = {"profil": ecrit, "openfisca": mesures}
        print(f"{profil['code']:<34} {mesures['nombre_d_annees']:>2} ans  "
              f"salaire annuel moyen {mesures['salaire_de_reference']:>10.2f}  "
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
        "famille": "le salaire annuel moyen du régime général sur des salaires "
                   "qui varient",
        "avertissement": (
            "Deuxième implémentation, pas une source officielle. Ses "
            "coefficients de revalorisation composent une série annuelle et "
            "s'écartent des colonnes de la circulaire Cnav ; il divise par le "
            "nombre d'années dès 1994, quand la somme se rapporte aux trimestres "
            "jusqu'au 30 juin 1995."
        ),
        "perimetre": (
            "Régime général des non-cadres, carrières à salaires variables "
            "liquidées de 1994 à 2017, générations 1934 à 1955."
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
