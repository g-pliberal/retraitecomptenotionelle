#!/usr/bin/env python3
"""Le budget de calcul (docs/architecture.md, § 7.8), mesuré dans le moteur du site.

Le temps se mesure par carrière, une fois les données chargées : pour le
scénario 1 seul et pour les six scénarios, dans le moteur JavaScript
(`scripts/budget_calcul.mjs`), sur les carrières que les témoins simulent ;
chaque mesure garde le meilleur de plusieurs passes. Chaque phase refait la
mesure, et une phase qui la dégrade s'arrête le temps de la ramener. Le
moteur Python, qui se retire (action 161), ne se mesure plus.

    python scripts/budget_calcul.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]


def main() -> int:
    sortie = subprocess.run(["node", str(RACINE / "scripts" / "budget_calcul.mjs")],
                            cwd=RACINE, capture_output=True, text=True, check=True)
    print(sortie.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
