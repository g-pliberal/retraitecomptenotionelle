#!/usr/bin/env python3
"""Oracle indépendant de l'Ircantec, par OpenFisca-France-Pension.

    pip install OpenFisca-France-Pension
    python scripts/fetch/openfisca_ircantec.py

Le cinquième oracle du dépôt, et le premier qui porte sur le secteur PUBLIC
contractuel : 2 108 941 retraités de droit direct en 2024 dans la série
certifiée du dépôt, et aucune contre-expertise jusqu'ici. L'Ircantec est un
régime en points sur deux tranches — la tranche A jusqu'au plafond de la
Sécurité sociale, la tranche B au-dessus — et son coefficient d'anticipation
est le seul du dépôt dont le barème soit écrit dans un arrêté plutôt que dans
un accord paritaire.

Ce que cette confrontation a trouvé, et les deux premiers points sont chez
nous. Ils sont la raison d'être de cet oracle : personne ne relisait ces
règles.

* **L'assiette de la tranche B était de un à huit plafonds depuis 1971.**
  L'article 7 du décret n° 70-1277 écrit l'inverse — « l'assiette de cotisation
  ainsi déterminée est toutefois limitée à 4,75 fois le plafond fixé pour les
  cotisations de retraite du régime général » — et c'est le décret n° 2008-996
  du 23 septembre 2008 qui la porte à huit. Le modèle donnait donc des points
  sur une assiette que le régime n'appelait pas, pour tout contractuel payé
  plus de 4,75 plafonds avant 2009.
* **Le coefficient d'anticipation était linéaire, 1,1 % par trimestre.**
  L'article 16 de l'arrêté du 30 décembre 1970 écrit un ESCALIER à trois
  marches — 0,01 par trimestre sur les trois années les plus proches de l'âge
  normal, 0,012 5 sur les deux suivantes, 0,017 5 au-delà, plancher 0,43 — et
  ce sont exactement les paliers de l'Agirc-Arrco. Le taux moyen de 1,1 %
  tombait juste aux deux bouts, 0,78 à cinq ans d'anticipation et 1,00 à
  zéro, et nulle part entre les deux : à douze trimestres il retirait 13,2 %
  quand l'arrêté en retire 12.

Et un écart qui est chez lui, sur la même assiette que le premier :

* **Sa tranche B passe à huit plafonds en 1992**, seize ans avant le décret qui
  l'y porte. Un profil est gardé pour le montrer, et le test vérifie que
  l'écart vaut exactement la cotisation de la tranche 4,75-8 plafonds.
* **Sa surcote est dix fois trop forte.** Le paragraphe 4 de l'article 16
  majore le total des points « de 0,75 % par trimestre entier écoulé entre le
  soixante-cinquième anniversaire de l'assuré et la date d'entrée en
  jouissance » ; son paramètre porte 0,075. Deux ans de surcote y valent
  +60 % de pension. Le profil `surcote_1945` le montre, et le test vérifie
  que son coefficient est exactement 1 + 0,075 × trimestres — le modèle, lui,
  ne sert AUCUNE surcote à l'Ircantec, ce que `limites.md` dit désormais.

Trois bornes de périmètre.

* **Les carrières commencent en 1971 au plus tôt.** Avant, le dépôt a deux
  régimes distincts — l'IPACTE au-dessus du plafond depuis 1951, l'IGRANTE en
  dessous depuis 1960 — quand OpenFisca porte tout sur la même variable
  ``ircantec``, avec le barème de cotisation de 1971 et le salaire de
  référence de l'IGRANTE. Les deux lectures ne sont pas comparables.
* **Le déroulage récursif doit être borné à la main**, comme pour l'Agirc :
  ``points`` remonte d'année en année jusqu'à ce que ``max_spiral_loops``
  l'arrête, et sa formule de cotisation lit le plafond de la Sécurité sociale,
  qu'OpenFisca ne définit pas avant 1931. Laissé à cent, il remonte à 1910 et
  lève une ``ParameterNotFoundError``.
* **Il rend zéro sans se plaindre** si le déroulage n'a pas lieu : le script
  refuse d'écrire un profil dont les points ou la rente seraient nuls.

Le fichier produit, ``tests/temoins/openfisca_ircantec.json``, est VERSIONNÉ :
``tests/test_oracle.py`` rejoue la confrontation sans installer OpenFisca.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SORTIE = Path("tests/temoins/openfisca_ircantec.json")

#: Voir ``openfisca_regime_general.py``.
RECURSION = 20_000

#: Première année où OpenFisca définit le plafond de la Sécurité sociale, que
#: la cotisation Ircantec lit pour découper ses tranches. La remontée
#: récursive de ``points`` doit s'arrêter ici ou après.
PREMIERE_ANNEE_SURE = 1931

#: Profils confrontés. Salaire nominal constant, agent non titulaire, carrière
#: continue commençant en 1971 au plus tôt. Les salaires sont choisis pour que
#: la carrière traverse les deux tranches ; `tranche_b_1992` est le seul à
#: dépasser 4,75 plafonds, et il est gardé pour montrer où l'assiette
#: d'OpenFisca s'écarte du décret.
PROFILS: tuple[dict, ...] = (
    {"code": "tranche_a_seule_1948", "naissance": 1948, "debut": 1975,
     "liquidation": 2010, "salaire": 18000.0},
    {"code": "deux_tranches_1948", "naissance": 1948, "debut": 1975,
     "liquidation": 2010, "salaire": 30000.0},
    {"code": "deux_tranches_1944", "naissance": 1944, "debut": 1972,
     "liquidation": 2004, "salaire": 28000.0},
    {"code": "carriere_1971_2006_1946", "naissance": 1946, "debut": 1971,
     "liquidation": 2006, "salaire": 35000.0},
    {"code": "carriere_courte_1950", "naissance": 1950, "debut": 1990,
     "liquidation": 2013, "salaire": 32000.0},
    {"code": "bas_salaire_1952", "naissance": 1952, "debut": 1980,
     "liquidation": 2014, "salaire": 14000.0},
    {"code": "depart_tardif_1947", "naissance": 1947, "debut": 1975,
     "liquidation": 2012, "salaire": 26000.0},
    {"code": "anticipation_1954", "naissance": 1954, "debut": 1980,
     "liquidation": 2016, "salaire": 24000.0},
    {"code": "apres_2008_1956", "naissance": 1956, "debut": 1985,
     "liquidation": 2018, "salaire": 40000.0},
    {"code": "surcote_1945", "naissance": 1945, "debut": 1971,
     "liquidation": 2012, "salaire": 26000.0},
    {"code": "tranche_b_1992_1948", "naissance": 1948, "debut": 1975,
     "liquidation": 2010, "salaire": 200000.0},
)


def calculer(profil: dict, tbs) -> dict:
    """Relève les grandeurs de l'Ircantec pour un profil, année par année."""
    from openfisca_core.simulation_builder import SimulationBuilder

    liquidation, debut = profil["liquidation"], profil["debut"]
    annees = [str(a) for a in range(debut, liquidation)]
    situation = {
        "date_de_naissance": {"ETERNITY": f"{profil['naissance']}-01-01"},
        "sexe": {"ETERNITY": False},
        "nombre_enfants": {"ETERNITY": 0},
        # L'Ircantec lit ses trimestres de décote dans le régime général : les
        # deux liquident le même jour.
        "regime_general_cnav_liquidation_date": {
            "ETERNITY": f"{liquidation}-01-01"
        },
        "ircantec_liquidation_date": {"ETERNITY": f"{liquidation}-01-01"},
        "regime_general_cnav_salaire_de_base": {a: profil["salaire"] for a in annees},
        "statut_du_cotisant": {a: "emploi" for a in annees},
        "categorie_salarie": {a: "public_non_titulaire" for a in annees},
    }
    simulation = SimulationBuilder().build_from_entities(
        tbs, {"persons": {"assure": situation}}
    )
    spirales = liquidation - PREMIERE_ANNEE_SURE
    if spirales <= liquidation - debut + 1:
        raise SystemExit(
            f"{profil['code']} : la carrière remonte plus haut que les "
            "paramètres d'OpenFisca ; aucun nombre de reprises ne convient."
        )
    simulation.max_spiral_loops = spirales

    def valeur(variable: str, periode) -> float:
        return float(simulation.calculate(variable, periode)[0])

    points = valeur("ircantec_points", liquidation)
    pension_brute = valeur("ircantec_pension_brute", liquidation)
    return {
        "points": points,
        "valeur_du_point": pension_brute / points if points else 0.0,
        "coefficient_de_minoration": valeur("ircantec_coefficient_de_minoration",
                                            liquidation),
        "decote_trimestres_regime_general": valeur(
            "regime_general_cnav_decote_trimestres", liquidation),
        "surcote_trimestres_regime_general": valeur(
            "regime_general_cnav_surcote_trimestres", liquidation),
        "pension_brute": pension_brute,
        "pension": valeur("ircantec_pension", liquidation),
        "points_annuels": {a: valeur("ircantec_points_annuels", int(a)) for a in annees},
        "cotisations_annuelles": {
            a: valeur("ircantec_cotisation", int(a)) for a in annees
        },
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
              f"valeur {mesures['valeur_du_point']:.5f} €  "
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
            "Deuxième implémentation, pas une source officielle. Son assiette "
            "de tranche B passe de 4,75 à huit plafonds en 1992, quand le "
            "décret n° 2008-996 l'y porte au 25 septembre 2008 ; ses taux de "
            "1989 et suivants sont arrondis au dix-millième près différemment "
            "de ceux que publie la Caisse des dépôts."
        ),
        "perimetre": (
            "Ircantec des agents non titulaires, carrières continues à salaire "
            "nominal constant commençant en 1971 au plus tôt — avant, le dépôt "
            "a deux régimes distincts, l'IPACTE et l'IGRANTE, quand OpenFisca "
            "n'en a qu'un."
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
