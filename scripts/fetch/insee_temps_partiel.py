#!/usr/bin/env python3
"""Récupération de la part du temps partiel dans l'emploi auprès de l'INSEE.

    python scripts/fetch/insee_temps_partiel.py

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
Les centiles du salaire du privé, sexe par sexe (``insee_profil_salaire_age.py``),
sont des salaires en équivalent temps plein : ils disent ce que vaut une heure,
pas combien d'heures une année en compte. La pension, elle, compte le salaire de
l'année, et c'est au bas de l'échelle que le minimum contributif se décide : la
grille élargie de la page Coût, qui n'avait pas de temps partiel, ne savait pas
y poser ses carrières (action 136, étape 6). La part du temps partiel dans
l'emploi, par sexe et par âge, est la première pièce du volume de travail que
la population de la page donnera à chacun : 17,2 % des femmes en emploi en
1975, 32,0 % en 2000, 26,7 % en 2024, quand les hommes passent de 3,3 à 8,7 %.

LE JEU
------
``DD_EEC_SERIES``, les séries longues de l'enquête Emploi, de 1975 à
aujourd'hui, en France entière : la part du temps partiel parmi les personnes
en emploi (``EMPSTA=1``, salariés et non-salariés), par sexe et par trois
tranches d'âge — 15 à 24 ans, 25 à 49 ans, 50 ans ou plus. Les résultats
annuels (``DD_EEC_ANNUEL``) détaillent l'âge par cinq ans, mais pour la seule
dernière année ; aucun jeu de Melodi ne dit combien d'heures un temps partiel
compte, par sexe.

Le fichier produit, ``data/brut/insee_temps_partiel.json``, est le document
source : il n'est pas lu par le modèle, seulement par
``scripts/verifier_donnees.py``.
"""

from __future__ import annotations

import json
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from insee_melodi import telecharger  # noqa: E402

#: Les séries longues de l'enquête Emploi.
JEU = "DD_EEC_SERIES"

#: La part de chaque temps de travail dans l'emploi, par sexe et âge, réduite au
#: temps partiel ; le temps complet en est le complément à cent. Les autres
#: dimensions ne portent que leur total pour cette mesure : les fixer garde la
#: série si l'INSEE les détaillait un jour.
FILTRES = {
    "EEC_MEASURE": "PT_WKTIME_IN_EMP_BY_SEX_AGE", "WKTIME": "PT",
    "EMPSTA": "1", "EMPFORM": "_T", "PCS": "_T", "EDUC": "_T",
}

SORTIE = Path("data/brut/insee_temps_partiel.json")


def main() -> int:
    try:
        chemin = telecharger(JEU, FILTRES, SORTIE)
    except urllib.error.HTTPError as erreur:
        print(f"Erreur HTTP {erreur.code} : {erreur.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as erreur:
        print(f"Réseau indisponible : {erreur.reason}", file=sys.stderr)
        return 1

    observations = json.loads(chemin.read_text(encoding="utf-8"))["observations"]
    annees = sorted({int(o["dimensions"]["TIME_PERIOD"]) for o in observations})
    if not annees:
        print("aucune observation : les filtres ne désignent plus rien",
              file=sys.stderr)
        return 1
    print(f"{len(observations)} observations écrites dans {chemin} "
          f"({annees[0]}-{annees[-1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
