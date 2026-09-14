#!/usr/bin/env python3
"""Oracle indépendant de l'Arrco d'avant 2019, par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_arrco.py

Le troisième oracle du dépôt, après le régime général et la pension civile.
L'Arrco est un régime EN POINTS : ce que la confrontation contrôle, c'est la
chaîne cotisation → points → rente — taux effectif par tranche, prix d'achat
du point, taux d'appel, valeur de service, coefficient d'anticipation —,
c'est-à-dire tout ce que ``openfisca_points.py`` et
``openfisca_cotisations.py`` transcrivent séparément, rejoué d'un bloc par un
autre moteur.

Pourquoi « d'avant 2019 », et pourquoi « depuis 1999 ».

* **Depuis 1999** parce qu'OpenFisca ne convertit pas les points d'avant
  l'unification de l'Arrco : ses prix d'achat 1957-1998 sont ceux de l'UNIRS,
  en unité ancienne, et les points qu'il en tire sont valorisés à la valeur de
  service du point unifié — un facteur quatre sur toute cette période. Le
  dépôt, lui, LIT les coefficients de conversion (``regimes/conversions_points.csv``).
  Une carrière qui commence en 1999 évite la question, et laisse vingt ans de
  barèmes à confronter.
* **Avant 2019** parce que le régime unifié Agirc-Arrco est inutilisable dans
  la version publiée : son code demande un paramètre que ses barèmes ne
  définissent pas, et toute liquidation postérieure lève une exception.

Ce que cette confrontation a trouvé : **rien à corriger, et c'est le résultat.**
Sur sept profils, le nombre de points concorde au millième, la valeur de
service à la quatrième décimale, et la rente avant abattement au centime — y
compris pour un salaire au-dessus du plafond, dont la tranche 2 cotise à son
propre taux. Le seul écart est celui du coefficient d'anticipation, et il est
le sien : OpenFisca ne lit son barème que par ANNÉE entière d'anticipation, en
tronquant les trimestres, quand le barème de l'Arrco est écrit par trimestre.
Le test ne compare donc le coefficient que lorsque l'anticipation tombe sur des
années pleines.

Un piège de calendrier, à connaître pour choisir les profils. OpenFisca compte
l'âge à la liquidation en convertissant des jours en mois par une durée moyenne
du mois : selon le nombre d'années bissextiles traversées, un assuré liquidant
le jour de son anniversaire a tantôt l'âge exact, tantôt un mois de moins — un
né le 1er janvier 1945 parti le 1er janvier 2007 a « 61 ans et 11 mois », et
treize trimestres de décote au lieu de douze. Un écart de soixante-deux ans
traverse quinze années bissextiles quand il part d'une année impaire, seize
quand il part d'une année bissextile : les profils partent d'années
bissextiles, et le test vérifie que les deux décomptes coïncident.

Le fichier produit, ``tests/temoins/openfisca_arrco.json``, est VERSIONNÉ :
``tests/test_oracle.py`` rejoue la confrontation sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SORTIE = Path("tests/temoins/openfisca_arrco.json")

#: Voir ``openfisca_regime_general.py`` : sans ces deux réglages, OpenFisca
#: rend zéro en silence.
RECURSION = 20_000
SPIRALES = 100

#: Profils confrontés. Salaire nominal constant, non-cadre, carrière continue
#: qui ne commence pas avant 1999 et ne liquide pas après 2018. Les codes
#: disent ce que chacun met à l'épreuve.
PROFILS: tuple[dict, ...] = (
    {"code": "taux_plein_1947", "naissance": 1947, "debut": 1999,
     "liquidation": 2012, "salaire": 22000.0},
    {"code": "decote_8_trimestres_1948", "naissance": 1948, "debut": 1999,
     "liquidation": 2011, "salaire": 23000.0},
    {"code": "decote_12_trimestres_1944", "naissance": 1944, "debut": 1999,
     "liquidation": 2006, "salaire": 20000.0},
    {"code": "decote_15_trimestres_1952", "naissance": 1952, "debut": 1999,
     "liquidation": 2014, "salaire": 25000.0},
    {"code": "decote_19_trimestres_1954", "naissance": 1954, "debut": 1999,
     "liquidation": 2016, "salaire": 20000.0},
    {"code": "decote_plafonnee_1956", "naissance": 1956, "debut": 2000,
     "liquidation": 2018, "salaire": 24000.0},
    {"code": "deux_tranches_1948", "naissance": 1948, "debut": 1999,
     "liquidation": 2010, "salaire": 40000.0},
)


def calculer(profil: dict, tbs) -> dict:
    """Relève les grandeurs de l'Arrco pour un profil, année par année."""
    from openfisca_core.simulation_builder import SimulationBuilder

    annees = [str(a) for a in range(profil["debut"], profil["liquidation"])]
    situation = {
        "date_de_naissance": {"ETERNITY": f"{profil['naissance']}-01-01"},
        "sexe": {"ETERNITY": False},
        "nombre_enfants": {"ETERNITY": 0},
        # L'Arrco lit ses trimestres de décote dans le régime général : les
        # deux liquident le même jour.
        "regime_general_cnav_liquidation_date": {
            "ETERNITY": f"{profil['liquidation']}-01-01"
        },
        "arrco_liquidation_date": {"ETERNITY": f"{profil['liquidation']}-01-01"},
        "regime_general_cnav_salaire_de_base": {a: profil["salaire"] for a in annees},
        "statut_du_cotisant": {a: "emploi" for a in annees},
        "categorie_salarie": {a: "prive_non_cadre" for a in annees},
    }
    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": situation}}
    )
    simulation.max_spiral_loops = SPIRALES
    liquidation = profil["liquidation"]

    def valeur(variable: str, periode) -> float:
        return float(simulation.calculate(variable, periode)[0])

    points = valeur("arrco_points", liquidation)
    pension_brute = valeur("arrco_pension_brute", liquidation)
    return {
        "points": points,
        "valeur_du_point": pension_brute / points if points else 0.0,
        "coefficient_de_minoration": valeur("arrco_coefficient_de_minoration",
                                            liquidation),
        "decote_trimestres_regime_general": valeur(
            "regime_general_cnav_decote_trimestres", liquidation),
        "pension_brute": pension_brute,
        "pension": valeur("arrco_pension", liquidation),
        # Les points de chaque année, pour que le diagnostic d'un écart ne
        # demande pas de réinstaller le paquet.
        "points_annuels": {a: valeur("arrco_points_annuels", int(a)) for a in annees},
        "cotisations_annuelles": {a: valeur("arrco_cotisation", int(a)) for a in annees},
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
        if mesures["points"] <= 0 or mesures["pension_brute"] <= 0:
            print(
                f"{profil['code']} : OpenFisca rend des points ou une rente "
                "nuls — le déroulage récursif n'a pas eu lieu. Rien n'est écrit.",
                file=sys.stderr,
            )
            return 1
        releves[profil["code"]] = {"profil": profil, "openfisca": mesures}
        print(f"{profil['code']:<28} points {mesures['points']:>9.3f}  "
              f"valeur {mesures['valeur_du_point']:.4f} €  "
              f"anticipation {mesures['coefficient_de_minoration']:.4f}  "
              f"rente {mesures['pension_brute']:>9.2f} €")

    from importlib.metadata import PackageNotFoundError, version

    try:
        publiee = version("OpenFisca-France-Pension")
    except PackageNotFoundError:  # pragma: no cover - paquet posé à la main
        publiee = "inconnue"

    document = {
        "source": "OpenFisca-France-Pension",
        "version": publiee,
        "recupere_le": date.today().isoformat(),
        "avertissement": (
            "Deuxième implémentation, pas une source officielle. Son "
            "coefficient d'anticipation ne se lit que par année entière, en "
            "tronquant les trimestres ; ses points d'avant 1999 sont en unité "
            "UNIRS non convertie."
        ),
        "perimetre": (
            "Arrco des non-cadres, carrières continues à salaire nominal "
            "constant commençant en 1999 au plus tôt et liquidées en 2018 au "
            "plus tard."
        ),
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
