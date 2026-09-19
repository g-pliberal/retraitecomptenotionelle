#!/usr/bin/env python3
"""Récupération du revenu mixte des ménages auprès de l'INSEE.

    python scripts/fetch/insee_revenu_mixte.py

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
L'assiette des cotisations retraite n'est pas la seule masse salariale : les
non-salariés cotisent sur leur revenu professionnel. Aux comptes nationaux,
cette grandeur est le REVENU MIXTE des ménages (B3G du secteur S14) — mixte
parce qu'elle rémunère indissociablement le travail de l'entrepreneur
individuel et le capital qu'il engage. Additionnée aux salaires et traitements
bruts (D11, ``insee_bdm.py``), elle donne l'assiette des revenus d'activité,
que la page « Coût » confronte aux ressources encaissées pour dire ce qu'un
taux de cotisation prélève RÉELLEMENT.

POURQUOI MELODI ET NON LA BANQUE DE DONNÉES MACROÉCONOMIQUES
--------------------------------------------------------------
Parce que la BDM ne l'expose pas, et ce n'est pas faute de l'avoir cherché.
Ses comptes de branche (``CNA-2020-CPEB``) ne publient qu'un agrégat
« Excédent d'exploitation / Revenu mixte », qui mêle le profit des sociétés au
revenu des entrepreneurs individuels et ne peut donc pas servir d'assiette ;
son jeu de comptes des secteurs institutionnels (``CNA-2020-CSI``) ne sert que
cinq ratios. Le tableau économique d'ensemble de Melodi, lui, porte le compte
complet, secteur par secteur et opération par opération, de 1949 à aujourd'hui.

C'est ce qui permet de rester chez le PRODUCTEUR. Eurostat rediffuse la même
grandeur, à un millésime près, sous ``nasa_10_nf_tr`` ; le critère 1 du
manifeste des sources fait préférer celui qui produit à celui qui reprend, et
la différence n'est pas théorique : sur 2023, les deux s'écartent de 0,8 %.

Le fichier produit, ``data/brut/insee_revenu_mixte.json``, est le document
source : il n'est pas lu par le modèle, seulement par
``scripts/verifier_donnees.py``, qui en écrit la part « revenu_mixte » de
``data/reference/macro/assiette_activite.csv``.
"""

from __future__ import annotations

import json
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from insee_melodi import telecharger  # noqa: E402

#: Tableau économique d'ensemble : le compte de chaque secteur institutionnel.
JEU = "DD_CNA_TEE"

#: Les trois dimensions qui isolent la série. ``STO`` est l'opération au sens
#: du SEC 2010, ``REF_SECTOR`` le secteur qui la reçoit, ``TRANSFORMATION`` la
#: forme rendue : ``N`` pour le niveau, ``GY`` pour le glissement annuel, que
#: l'on ne prend pas — une variation ne s'additionne pas à une masse salariale.
FILTRES = {"STO": "B3G", "REF_SECTOR": "S14", "TRANSFORMATION": "N"}

SORTIE = Path("data/brut/insee_revenu_mixte.json")


def main() -> int:
    try:
        chemin = telecharger(JEU, FILTRES, SORTIE)
    except urllib.error.HTTPError as erreur:
        print(f"Erreur HTTP {erreur.code} : {erreur.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as erreur:
        print(f"Réseau indisponible : {erreur.reason}", file=sys.stderr)
        return 1

    charge = json.loads(chemin.read_text(encoding="utf-8"))
    observations = charge["observations"]
    annees = sorted(int(o["dimensions"]["TIME_PERIOD"]) for o in observations)
    if not annees:
        print("aucune observation : les filtres ne désignent plus rien",
              file=sys.stderr)
        return 1
    print(f"{len(observations)} observations écrites dans {chemin} "
          f"({annees[0]}-{annees[-1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
