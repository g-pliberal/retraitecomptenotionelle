#!/usr/bin/env python3
"""Le budget de calcul (docs/architecture.md, § 7.8), mesuré dans les deux moteurs.

Le temps se mesure par carrière, une fois les données chargées : pour le
scénario 1 seul et pour les six scénarios, dans chacun des deux moteurs. Les
carrières sont celles que les témoins simulent (`scripts/construire_temoins.py`),
saisies au passage de la simulation ; chaque mesure garde le meilleur de
plusieurs passes. Chaque phase refait la mesure, et une phase qui la dégrade
s'arrête le temps de la ramener.

    python scripts/budget_calcul.py            # les deux moteurs
    python scripts/budget_calcul.py --python   # le Python seul
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts"))


def carrieres() -> list:
    """Les (simulateur, carrière) que les témoins simulent."""
    from construire_temoins import _cas
    from retraite_notionnelle.simulateur import Simulateur
    from retraite_notionnelle.web.pages import Contexte, Saisie

    saisies: list = []
    original = Simulateur.simuler

    def capter(self, carriere, *args, **kwargs):
        saisies.append((self, carriere))
        return original(self, carriere, *args, **kwargs)

    Simulateur.simuler = capter
    try:
        contexte = Contexte()
        for cas in _cas():
            try:
                contexte.simuler(Saisie.depuis_requete(cas["requete"]))
            except Exception:  # noqa: BLE001 — une saisie refusée ne simule rien
                pass
    finally:
        Simulateur.simuler = original
    return saisies


def mesurer(saisies: list, calcul, passes: int) -> float:
    """Millisecondes par carrière, au mieux de ``passes`` passes."""
    meilleur = float("inf")
    for _ in range(passes):
        debut = time.perf_counter()
        for simulateur, carriere in saisies:
            calcul(simulateur, carriere)
        meilleur = min(meilleur, time.perf_counter() - debut)
    return meilleur / len(saisies) * 1000


def main() -> int:
    arguments = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    arguments.add_argument("--python", action="store_true", help="le moteur Python seul")
    options = arguments.parse_args()
    saisies = carrieres()
    print(f"Python, {len(saisies)} carrières : "
          f"{mesurer(saisies, lambda s, c: s.scenario_actuel.calculer(c), 5):.2f} ms pour "
          f"le scénario 1, {mesurer(saisies, lambda s, c: s.simuler(c), 3):.2f} ms pour les "
          "six scénarios, par carrière.")
    if not options.python:
        sortie = subprocess.run(["node", str(RACINE / "scripts" / "budget_calcul.mjs")],
                                cwd=RACINE, capture_output=True, text=True, check=True)
        print(sortie.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
