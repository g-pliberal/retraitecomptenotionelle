#!/usr/bin/env python3
"""Oracle indépendant de la pension civile, par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_fonction_publique.py

Le frère de ``openfisca_regime_general.py``, pour la fonction publique de
l'État et la CNRACL. Même principe : le scénario « système actuel » est
l'ÉTALON du modèle, et une seconde implémentation écrite par d'autres à partir
des mêmes textes est la seule contre-expertise qui ne partage pas nos
hypothèses. Même statut : OpenFisca-France-Pension n'est PAS une source
officielle, c'est un modèle, avec ses transcriptions et ses retards, et un
désaccord ne désigne pas d'office le coupable.

Ce que cette confrontation a fait trouver — un désaccord de chaque côté, comme
la première.

* **Chez nous, deux choses.** Le barème de décote de l'article L. 14 était lu
  à l'année de LIQUIDATION. Le III de l'article 66 de la loi du 21 août 2003
  titre pourtant sa colonne « Année au cours de laquelle sont réunies les
  conditions mentionnées au I et au II de l'article L. 24 » — l'année où le
  droit s'ouvre. Un sédentaire né en 1948, dont le droit s'ouvre en 2008,
  garde 0,375 % et « limite d'âge moins douze trimestres » quelle que soit
  l'année de son départ ; le modèle lui opposait, s'il partait en 2010, le
  barème de 2010 et deux trimestres de décote que le droit ne lui retire pas.
  Corrigé, dans les deux moteurs. Et le traitement de l'année d'avant le
  départ était ramené à l'année du départ par les prix : un fonctionnaire
  garde son indice, son traitement suit le POINT, et c'est ce que fait
  OpenFisca. Corrigé aussi, et les deux pensions tombent maintenant au
  centime.
* **Chez lui, une transcription.** Son barème de décote porte 0,65 % pour
  l'année 2010, là où la loi écrit 0,625 % — huit huitièmes de point, de
  0,125 % à 1,25 %, et 2010 est le cinquième. Le profil ``ouverture_2010``
  est gardé exprès : le test le compare en connaissance de cause.

Ce que ce contrôle couvre, et ce qu'il ne couvre pas.

* **Sédentaires, sans enfant, sans prime, carrière continue** : ce qui se
  décrit à l'identique des deux côtés. Les catégories actives, les
  bonifications et le RAFP demandent des conventions de traduction qui
  deviendraient l'objet du test.
* **Liquidations de 2009 à 2020.** Avant, le barème de décote n'existe pas ;
  au-delà, les barèmes d'OpenFisca s'arrêtent.
* **Le minimum garanti est relevé, pas exigé.** OpenFisca le calcule au point
  d'indice de l'année de liquidation, quand l'article L. 17 fige la référence
  au 1er janvier 2004 et la revalorise comme les pensions : l'écart est le
  sien, de quelques pour cent, et le test lui laisse cette marge.
* **Les générations d'avant 1949 liquidant après 2013 sont évitées.** La table
  de durée de service d'OpenFisca leur oppose, à compter de 2014, 151 à 155
  trimestres — une transcription qui contredit sa propre colonne de 2003.

UN PIÈGE, ET IL EST SILENCIEUX. Sans ``simulation.max_spiral_loops``, la durée
de service d'OpenFisca vaut zéro et la pension aussi, sans exception. Le script
refuse d'écrire un profil dont la durée ou la pension serait nulle.

Le fichier produit, ``tests/temoins/openfisca_fonction_publique.json``, est
VERSIONNÉ : ``tests/test_oracle.py`` rejoue la confrontation sur un dépôt
fraîchement cloné, sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SORTIE = Path("tests/temoins/openfisca_fonction_publique.json")

#: Profondeur de récursion et nombre de reprises : voir
#: ``openfisca_regime_general.py``, les raisons sont les mêmes.
RECURSION = 20_000
SPIRALES = 100

#: Ce que le témoin appelle chaque régime, et ce qu'OpenFisca en fait :
#: préfixe de ses variables, catégorie de salarié qu'il attend.
REGIMES = {
    "fonction_publique_etat": ("fonction_publique", "public_titulaire_etat"),
    "cnracl": ("cnracl", "public_titulaire_territoriale"),
}

#: Profils confrontés. Traitement nominal constant, aucune prime, carrière
#: continue à temps plein, liquidation au 1er janvier de l'année écrite.
PROFILS: tuple[dict, ...] = (
    {"code": "taux_plein_1948", "regime": "fonction_publique_etat",
     "naissance": 1948, "debut": 1972, "liquidation": 2010, "traitement": 30000.0},
    {"code": "decote_7_trimestres_1952", "regime": "fonction_publique_etat",
     "naissance": 1952, "debut": 1975, "liquidation": 2014, "traitement": 35000.0},
    {"code": "decote_17_trimestres_1955", "regime": "fonction_publique_etat",
     "naissance": 1955, "debut": 1985, "liquidation": 2017, "traitement": 28000.0},
    {"code": "decote_plafonnee_1958", "regime": "fonction_publique_etat",
     "naissance": 1958, "debut": 1985, "liquidation": 2020, "traitement": 32000.0},
    {"code": "surcote_1948", "regime": "fonction_publique_etat",
     "naissance": 1948, "debut": 1968, "liquidation": 2011, "traitement": 30000.0},
    {"code": "carriere_courte_1947", "regime": "fonction_publique_etat",
     "naissance": 1947, "debut": 1975, "liquidation": 2009, "traitement": 25000.0},
    {"code": "minimum_garanti_1946", "regime": "fonction_publique_etat",
     "naissance": 1946, "debut": 1980, "liquidation": 2010, "traitement": 12000.0},
    {"code": "ouverture_2010_1950", "regime": "fonction_publique_etat",
     "naissance": 1950, "debut": 1972, "liquidation": 2012, "traitement": 30000.0},
    {"code": "cnracl_decote_2_trimestres_1950", "regime": "cnracl",
     "naissance": 1950, "debut": 1972, "liquidation": 2012, "traitement": 30000.0},
    {"code": "cnracl_decote_14_trimestres_1956", "regime": "cnracl",
     "naissance": 1956, "debut": 1980, "liquidation": 2018, "traitement": 30000.0},
)

#: Grandeurs relevées, et la variable OpenFisca qui les porte (sans préfixe).
GRANDEURS = {
    "duree_assurance": "duree_assurance",
    "coefficient_de_proratisation": "coefficient_de_proratisation",
    "decote_trimestres": "decote_trimestres",
    "surcote_trimestres": "surcote_trimestres",
    "taux_de_liquidation": "taux_de_liquidation",
    "traitement_de_reference": "salaire_de_reference",
    "pension_avant_minimum": "pension_avant_minimum_et_plafonnement",
    "minimum_garanti": "minimum_garanti",
    "pension_brute": "pension_brute",
}


def calculer(profil: dict, tbs) -> dict[str, float]:
    """Relève les grandeurs de la pension civile pour un profil."""
    from openfisca_core.simulation_builder import SimulationBuilder

    prefixe, categorie = REGIMES[profil["regime"]]
    annees = [str(a) for a in range(profil["debut"], profil["liquidation"])]
    situation = {
        "date_de_naissance": {"ETERNITY": f"{profil['naissance']}-01-01"},
        "sexe": {"ETERNITY": False},
        "nombre_enfants": {"ETERNITY": 0},
        f"{prefixe}_liquidation_date": {
            "ETERNITY": f"{profil['liquidation']}-01-01"
        },
        f"{prefixe}_salaire_de_base": {a: profil["traitement"] for a in annees},
        # Quatre trimestres de service cotisés par année pleine : OpenFisca ne
        # les déduit pas du traitement, il faut les lui donner.
        f"{prefixe}_duree_de_service_cotisee_annuelle": {a: 4 for a in annees},
        "taux_de_prime": {a: 0.0 for a in annees},
        "statut_du_cotisant": {a: "emploi" for a in annees},
        "categorie_salarie": {a: categorie for a in annees},
    }
    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": situation}}
    )
    simulation.max_spiral_loops = SPIRALES
    return {
        nom: float(simulation.calculate(f"{prefixe}_{variable}",
                                        profil["liquidation"])[0])
        for nom, variable in GRANDEURS.items()
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
        if mesures["duree_assurance"] <= 0 or mesures["pension_brute"] <= 0:
            print(
                f"{profil['code']} : OpenFisca rend une durée ou une pension "
                "nulle — le déroulage récursif n'a pas eu lieu. Rien n'est écrit.",
                file=sys.stderr,
            )
            return 1
        releves[profil["code"]] = {"profil": profil, "openfisca": mesures}
        print(f"{profil['code']:<36} durée {mesures['duree_assurance']:>5.0f}  "
              f"décote {mesures['decote_trimestres']:>2.0f}  "
              f"taux {mesures['taux_de_liquidation']:.4%}  "
              f"pension {mesures['pension_brute']:>10.2f} €")

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
            "Deuxième implémentation, pas une source officielle. Son barème de "
            "décote porte 0,65 % pour l'année d'ouverture 2010 là où la loi "
            "écrit 0,625 %, et son minimum garanti suit le point d'indice de "
            "l'année de liquidation là où l'article L. 17 fige la référence "
            "au 1er janvier 2004."
        ),
        "perimetre": (
            "Fonction publique de l'État et CNRACL, sédentaires sans enfant ni "
            "prime, carrières continues à traitement nominal constant, "
            "liquidations de 2009 à 2020."
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
