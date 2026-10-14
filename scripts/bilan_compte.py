#!/usr/bin/env python3
"""Le bilan du compte notionnel de chaque système, à la manière suédoise.

    python scripts/bilan_compte.py              # fin 2025, les six systèmes
    python scripts/bilan_compte.py --annee 2024

La durée de rotation, l'actif de cotisation, les réserves et leur rendement,
la dette des droits acquis, le ratio d'équilibre, et les taux de cotisation
d'équilibre (``retraite_notionnelle.bilan_compte`` ; action 138, étape 19),
sous les réglages de référence, ceux de la page Coût. Les grandeurs sont en
part du PIB de l'année, les âges et la durée en années ; le tableau s'écrit
en Markdown.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.bilan_compte import Reserves, calculer_bilans  # noqa: E402
from retraite_notionnelle.contexte import Contexte  # noqa: E402
from retraite_notionnelle.cout import SCENARIOS  # noqa: E402


def _nombre(valeur: float, decimales: int = 1, pourcent: bool = False) -> str:
    texte = f"{valeur * 100 if pourcent else valeur:.{decimales}f}"
    return texte.replace("-", "−").replace(".", ",") + (" %" if pourcent else "")


def main(argv: list[str] | None = None) -> int:
    lecteur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    lecteur.add_argument("--annee", type=int, default=2025)
    arguments = lecteur.parse_args(argv)
    contexte = Contexte()
    bilans = calculer_bilans(contexte, arguments.annee, [cle for cle, _ in SCENARIOS])
    noms = dict(SCENARIOS)
    print(f"# Bilan du compte, {arguments.annee}, en part du PIB\n")
    print("| Système | Âge des cotisations | Âge des pensions | Durée de rotation "
          "| Cotisations | Actif de cotisation | Réserves | Dette | Ratio d'équilibre "
          "| Taux de cotisation | Taux d'équilibre, tout | Taux d'équilibre, cotisations |")
    print("|---|" + "---:|" * 12)
    for cle, bilan in bilans.items():
        print(f"| {noms[cle]} | {_nombre(bilan.age_cotisations)} "
              f"| {_nombre(bilan.age_pensions)} | {_nombre(bilan.duree_rotation)} "
              f"| {_nombre(bilan.cotisations, 1, True)} "
              f"| {_nombre(bilan.actif_cotisation, 0, True)} "
              f"| {_nombre(bilan.reserves, 1, True)} | {_nombre(bilan.dette, 0, True)} "
              f"| {_nombre(bilan.ratio_equilibre, 3)} "
              f"| {_nombre(bilan.taux_cotisation, 1, True)} "
              f"| {_nombre(bilan.taux_equilibre, 1, True)} "
              f"| {_nombre(bilan.taux_cotisation_equilibre, 1, True)} |")
    reserves = Reserves.charger(contexte.simulateur().parametres.racine_donnees)
    rendement = reserves.rendement(arguments.annee)
    if rendement is not None:
        print(f"\nRendement comptable des réserves en {arguments.annee} : "
              f"{_nombre(rendement, 2, True)} (produits financiers nets sur les "
              f"réserves de la fin de {arguments.annee - 1}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
