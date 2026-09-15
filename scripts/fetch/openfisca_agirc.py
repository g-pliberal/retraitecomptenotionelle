#!/usr/bin/env python3
"""Oracle indépendant de l'Agirc d'avant 2019, par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_agirc.py

Le quatrième oracle du dépôt, après le régime général, la pension civile et
l'Arrco. L'Agirc est le régime des CADRES, et sa mécanique n'est pas celle de
l'Arrco : elle ne cotise que sur la part du salaire qui dépasse le plafond de
la Sécurité sociale — la tranche B, d'un à quatre plafonds —, y ajoute la
tranche C au-dessus de quatre plafonds à compter de 1991, et garantit depuis
1989 un nombre minimal de points annuels à tout cadre cotisant. Trois règles
que l'Arrco n'a pas, et que ``openfisca_arrco.py`` ne mettait donc pas à
l'épreuve.

Ce que cette confrontation contrôle : la chaîne assiette → cotisation → points,
année par année. Le témoin porte les points de CHAQUE ANNÉE, et le test les
compare un à un — c'est ce qui permet de dire non pas « les deux modèles
s'écartent de 0,06 % » mais « ils s'accordent sur dix-huit années sur vingt,
et voici les deux qui manquent et pourquoi ».

Ce qu'elle a trouvé, et les trois écarts sont chez lui.

* **Son barème salarié saute deux marches.** En 1989, le taux d'appel de
  l'Agirc passe à 1,134 : son barème employeur le suit (6 % × 1,134 = 6,804 %),
  son barème salarié reste à 2,2 %, la valeur de 1987, au lieu de 2,268 %. En
  1994, son couple employeur/salarié donne 12,06 % quand le contractuel de 10 %
  appelé à 1,21 en fait 12,10. Deux années sur vingt et une, et le test les
  isole par le rapport exact des deux taux.
* **Sa tranche C est cotisée par le salarié dès 1948.** Le fichier de barème
  employeur écrit `0` sur la tranche 4-8 plafonds avant 1991 ; le fichier
  salarié y écrit `null`. OpenFisca traite le premier comme un taux nul et le
  second comme une tranche ABSENTE : le taux de la tranche B s'étend alors
  jusqu'à huit plafonds, et un cadre payé plus de quatre plafonds en 1983 se
  voit prélever une cotisation salariale sur une tranche que l'Agirc n'ouvrira
  que huit ans plus tard. Un profil est gardé exprès pour le montrer, et le
  test vérifie que l'écart vaut exactement cette cotisation-là.
* **Son prix d'achat se lit trois mois trop tôt.** Le salaire de référence de
  l'Agirc change au 1er avril ; OpenFisca lit le paramètre au 1er janvier, et
  sert donc à partir de 2004 le prix de l'année précédente. C'est la même
  convention de millésime que la valeur de service de l'Arrco, déjà documentée,
  et elle joue cette fois sur l'ACQUISITION. Les profils s'arrêtent donc en
  2003, sauf un, gardé pour la montrer : le test l'encadre par les deux
  rapports extrêmes de prix d'achat successifs de sa carrière.

Deux bornes de mécanique, comme pour l'Arrco.

* **Le déroulage récursif doit être borné à la main.** ``points`` lit
  ``points`` de l'année précédente et remonte ainsi jusqu'à ce que
  ``max_spiral_loops`` l'arrête. Laissé à cent, il atteint 1947, où le barème
  de l'Agirc existe (formule datée du 1er janvier) mais pas son prix d'achat
  (première valeur au 1er avril 1947) : ``ParameterNotFoundError``. Le nombre
  de reprises est donc calculé pour que la remontée s'arrête en 1948, et le
  script vérifie qu'il couvre la carrière.
* **Il rend zéro sans se plaindre** si le déroulage n'a pas lieu : le script
  refuse d'écrire un profil dont les points ou la rente seraient nuls.

Le fichier produit, ``tests/temoins/openfisca_agirc.json``, est VERSIONNÉ :
``tests/test_oracle.py`` rejoue la confrontation sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SORTIE = Path("tests/temoins/openfisca_agirc.json")

#: Voir ``openfisca_regime_general.py`` : sans ces réglages, OpenFisca rend
#: zéro en silence.
RECURSION = 20_000

#: Première année où le prix d'achat de l'Agirc est défini au 1er janvier. La
#: remontée récursive de ``points`` doit s'arrêter ici ou après.
PREMIERE_ANNEE_SURE = 1948

#: Profils confrontés. Salaire nominal constant, cadre, carrière continue.
#: Le salaire reste entre un et quatre plafonds sur toute la carrière — c'est
#: la tranche B, la seule assiette de l'Agirc jusqu'en 1991 —, sauf pour
#: `tranche_c_avant_1991`, gardé pour montrer ce qu'OpenFisca y prélève.
#: Les liquidations s'arrêtent en 2003, borne au-delà de laquelle son prix
#: d'achat retarde d'un millésime, sauf pour `prix_d_achat_2012`, gardé pour
#: montrer ce retard.
PROFILS: tuple[dict, ...] = (
    {"code": "carriere_1983_2003_1940", "naissance": 1940, "debut": 1983,
     "liquidation": 2003, "salaire": 40000.0},
    {"code": "carriere_1984_2002_1941", "naissance": 1941, "debut": 1984,
     "liquidation": 2002, "salaire": 45000.0},
    {"code": "carriere_1985_2003_1943", "naissance": 1943, "debut": 1985,
     "liquidation": 2003, "salaire": 50000.0},
    {"code": "sans_anticipation_1938", "naissance": 1938, "debut": 1983,
     "liquidation": 2003, "salaire": 35000.0},
    {"code": "avant_la_gmp_1936", "naissance": 1936, "debut": 1983,
     "liquidation": 1996, "salaire": 30000.0},
    {"code": "apres_1994_1939", "naissance": 1939, "debut": 1995,
     "liquidation": 2003, "salaire": 45000.0},
    {"code": "apres_1994_1942", "naissance": 1942, "debut": 1995,
     "liquidation": 2002, "salaire": 38000.0},
    {"code": "apres_1994_1937", "naissance": 1937, "debut": 1995,
     "liquidation": 2001, "salaire": 50000.0},
    {"code": "tranche_c_avant_1991_1940", "naissance": 1940, "debut": 1983,
     "liquidation": 2003, "salaire": 150000.0},
    {"code": "prix_d_achat_2012_1948", "naissance": 1948, "debut": 1999,
     "liquidation": 2012, "salaire": 80000.0},
)


def calculer(profil: dict, tbs) -> dict:
    """Relève les grandeurs de l'Agirc pour un profil, année par année."""
    from openfisca_core.simulation_builder import SimulationBuilder

    liquidation, debut = profil["liquidation"], profil["debut"]
    annees = [str(a) for a in range(debut, liquidation)]
    situation = {
        "date_de_naissance": {"ETERNITY": f"{profil['naissance']}-01-01"},
        "sexe": {"ETERNITY": False},
        "nombre_enfants": {"ETERNITY": 0},
        # L'Agirc lit ses trimestres de décote dans le régime général : les
        # deux liquident le même jour.
        "regime_general_cnav_liquidation_date": {
            "ETERNITY": f"{liquidation}-01-01"
        },
        "agirc_liquidation_date": {"ETERNITY": f"{liquidation}-01-01"},
        "regime_general_cnav_salaire_de_base": {a: profil["salaire"] for a in annees},
        "statut_du_cotisant": {a: "emploi" for a in annees},
        "categorie_salarie": {a: "prive_cadre" for a in annees},
    }
    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": situation}}
    )
    # La remontée récursive s'arrête à `liquidation - spirales`. On la borne
    # pour qu'elle atteigne 1948 et pas 1947, tout en couvrant la carrière.
    spirales = liquidation - PREMIERE_ANNEE_SURE
    if spirales <= liquidation - debut + 1:
        raise SystemExit(
            f"{profil['code']} : la carrière remonte plus haut que le barème "
            "d'OpenFisca ; aucun nombre de reprises ne convient."
        )
    simulation.max_spiral_loops = spirales

    def valeur(variable: str, periode) -> float:
        return float(simulation.calculate(variable, periode)[0])

    points = valeur("agirc_points", liquidation)
    pension_brute = valeur("agirc_pension_brute", liquidation)
    return {
        "points": points,
        "valeur_du_point": pension_brute / points if points else 0.0,
        "coefficient_de_minoration": valeur("agirc_coefficient_de_minoration",
                                            liquidation),
        "decote_trimestres_regime_general": valeur(
            "regime_general_cnav_decote_trimestres", liquidation),
        "pension_brute": pension_brute,
        "pension": valeur("agirc_pension", liquidation),
        # Les points de chaque année : c'est sur eux que porte la
        # confrontation, et c'est ce qui permet de nommer l'année d'un écart.
        "points_annuels": {a: valeur("agirc_points_annuels", int(a)) for a in annees},
        "cotisations_annuelles": {a: valeur("agirc_cotisation", int(a)) for a in annees},
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
        print(f"{profil['code']:<28} points {mesures['points']:>10.3f}  "
              f"valeur {mesures['valeur_du_point']:.4f} €  "
              f"anticipation {mesures['coefficient_de_minoration']:.4f}  "
              f"rente {mesures['pension_brute']:>10.2f} €")

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
            "Deuxième implémentation, pas une source officielle. Son barème "
            "salarié ne suit pas le taux d'appel de 1989 ni le contractuel de "
            "1994 ; sa tranche C est cotisée par le salarié dès l'origine, "
            "faute d'un taux nul écrit là où le barème employeur en porte un ; "
            "son prix d'achat se lit au 1er janvier, soit un millésime de "
            "retard à partir de 2004."
        ),
        "perimetre": (
            "Agirc des cadres, carrières continues à salaire nominal constant "
            "comprises entre un et quatre plafonds de la Sécurité sociale et "
            "liquidées en 2003 au plus tard — deux profils sortent de ces "
            "bornes, et disent lequel dans leur code."
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
