#!/usr/bin/env python3
"""Récupération du profil de salaire par âge auprès de l'INSEE.

    python scripts/fetch/insee_profil_salaire_age.py

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
Le modèle ne connaît pas la carrière de celui qui se simule : il en construit
une à partir d'un niveau de revenu et d'un PROFIL, qui dit comment ce revenu
se déforme avec l'âge. Ce profil valait trois nombres écrits à la main — 60 %
du niveau saisi au premier emploi, 130 % au dernier —, sans source, alors
qu'il pèse sept points sur l'écart que le site affiche entre les systèmes : le
système actuel ne retient que les vingt-cinq meilleures années, donc un profil
montant le sert mieux, là où un compte notionnel compte toutes les années.

DEUX JEUX, PARCE QU'AUCUN NE SUFFIT SEUL
-----------------------------------------
``DS_DERA_PRIVE_SERIES_LONGUES`` porte le salaire net mensuel en équivalent
temps plein, en euros constants, par tranche d'âge, **de 1962 à 2024** pour les
quatre tranches de 26 à 60 ans. C'est la seule source qui dise comment la
prime à l'âge a évolué : elle valait 1,19 entre les 51-60 ans et les 26-30 ans
en 1962, 1,47 en 2000, 1,35 en 2024. C'est elle qui porte l'effet de
génération — celui qui est né en 1940 est entré dans la vie active au salaire
moyen de son époque, celui qui est né en 1960 à 86 % de celui de la sienne.

Mais elle est AGRÉGÉE, et un profil agrégé n'est pas un profil de carrière :
il mélange l'effet d'âge et un effet de COMPOSITION, les jeunes étant plus
souvent dans les catégories les moins payées. Son écart entre les bords vaut
0,46 en 2024 quand celui des ouvriers vaut 0,24 : le lire comme une carrière
individuelle surestimerait la progression du double.

``DS_DERA_PRIVE_ANNUEL`` croise, lui, l'âge et la catégorie
socioprofessionnelle — et c'est le seul à le faire, vérifié : ni la série
longue du privé ni celle du public ne croisent ces deux dimensions. Il donne
donc le profil INTRA-CATÉGORIE, qui est celui d'une carrière ; mais sur la
seule année 2024.

D'où le partage : la forme vient du second, l'évolution dans le temps du
premier. ``docs/limites.md`` dit ce que cette composition suppose.

Les fichiers produits, ``data/brut/insee_profil_salaire_age.json`` et
``data/brut/insee_profil_salaire_categorie.json``, sont les documents sources :
ils ne sont pas lus par le modèle, seulement par ``scripts/verifier_donnees.py``.
"""

from __future__ import annotations

import json
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from insee_melodi import telecharger  # noqa: E402

#: Séries longues du privé : la dimension TEMPS du profil.
JEU_SERIES = "DS_DERA_PRIVE_SERIES_LONGUES"

#: Salaire net mensuel moyen en équivalent temps plein, en euros CONSTANTS, à
#: temps complet, tous sexes, toutes catégories, tous secteurs. Les euros
#: constants ne servent qu'à la cohérence interne du jeu : le modèle n'en prend
#: qu'un RAPPORT, qui est sans dimension.
FILTRES_SERIES = {
    "DERA_MEASURE": "SALAIRE_NET_EQTP_MENSUEL_MOYEN_EUROS_CONSTANTS",
    "SEX": "_T", "PCS_ESE": "_T", "ACTIVITY": "_T", "QUANTILE": "_T",
    "WKTIME": "FT",
}

#: Le jeu annuel détaillé : la dimension CATÉGORIE du profil.
JEU_CATEGORIES = "DS_DERA_PRIVE_ANNUEL"

FILTRES_CATEGORIES = {
    "DERA_MEASURE": "SALAIRE_NET_EQTP_MENSUEL_MOYENNE",
    "SEX": "_T", "ACTIVITY": "_T", "NUMBER_EMPL": "_T", "QUANTILE": "_T",
    "WKTIME": "FT",
}

SORTIE_SERIES = Path("data/brut/insee_profil_salaire_age.json")
SORTIE_CATEGORIES = Path("data/brut/insee_profil_salaire_categorie.json")


def main() -> int:
    for jeu, filtres, sortie in (
        (JEU_SERIES, FILTRES_SERIES, SORTIE_SERIES),
        (JEU_CATEGORIES, FILTRES_CATEGORIES, SORTIE_CATEGORIES),
    ):
        try:
            chemin = telecharger(jeu, filtres, sortie)
        except urllib.error.HTTPError as erreur:
            print(f"Erreur HTTP {erreur.code} : {erreur.reason}", file=sys.stderr)
            return 1
        except urllib.error.URLError as erreur:
            print(f"Réseau indisponible : {erreur.reason}", file=sys.stderr)
            return 1

        observations = json.loads(chemin.read_text(encoding="utf-8"))["observations"]
        if not observations:
            print(f"aucune observation pour {jeu} : les filtres ne désignent "
                  "plus rien", file=sys.stderr)
            return 1
        annees = sorted({int(o["dimensions"]["TIME_PERIOD"]) for o in observations})
        ages = sorted({o["dimensions"]["AGE"] for o in observations})
        print(f"{len(observations)} observations écrites dans {chemin} "
              f"({annees[0]}-{annees[-1]}, {len(ages)} tranches d'âge)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
