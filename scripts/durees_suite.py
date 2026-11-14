"""Ce que chaque fichier de tests a duré dans une course de la suite.

La course de GitHub (`.github/workflows/tests.yml`) joue la suite en tranches,
et chaque tranche écrit ses durées, test par test (`pytest --junitxml`). Ce
script les somme par fichier de tests, sur toutes les tranches, et en écrit le
tableau : `python scripts/durees_suite.py tranche-1.xml tranche-2.xml`.
`scripts/publier_fabrique.sh` le publie avec le verdict, dans
`.github/durees_suite.tsv`, quand la course est partie sans mémoire des
calculs ; le greffon `pytest_parallele` s'y pèse pour partager les fichiers
entre les tranches de la course suivante, et une session y lit, sans API
GitHub, où passe le temps de la suite (action 135).

Les secondes sont celles des processus : la préparation, le test et son
rangement, sommés sur tous les processus de toutes les machines. Un calcul
lourd que plusieurs tests partagent pèse sur le premier qui le demande.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def fichier_de(classe: str) -> str:
    """Le fichier de tests d'un cas, depuis le nom que pytest lui donne
    (`tests.test_a.TestB` : le module, puis ses classes) : le chemin s'arrête
    au premier composant qui nomme un module de tests."""
    composants = classe.split(".")
    for rang, composant in enumerate(composants):
        if composant.startswith("test_") or composant.endswith("_test"):
            composants = composants[:rang + 1]
            break
    return "/".join(composants) + ".py"


def par_fichier(sorties: list[Path]) -> dict[str, float]:
    """Les secondes de chaque fichier de tests, sommées sur les sorties."""
    durees: dict[str, float] = {}
    for sortie in sorties:
        for cas in ET.parse(sortie).getroot().iter("testcase"):
            fichier = fichier_de(cas.get("classname", ""))
            durees[fichier] = durees.get(fichier, 0.0) + float(cas.get("time", 0))
    return durees


def tableau(durees: dict[str, float]) -> str:
    """Un fichier et ses secondes entières par ligne, dans l'ordre des noms ;
    ce qui pèse moins d'une seconde ne s'écrit pas, et ne change donc pas le
    tableau d'une course à l'autre."""
    lignes = ["# Ce que chaque fichier de tests a duré, en secondes de processus, à la",
              "# dernière course de tests.yml partie sans mémoire des calculs : écrit par",
              "# GitHub (scripts/durees_suite.py), jamais à la main. Action 135."]
    lignes += [f"{fichier}\t{round(secondes)}" for fichier, secondes in sorted(durees.items())
               if round(secondes) >= 1]
    return "\n".join(lignes) + "\n"


if __name__ == "__main__":
    sys.stdout.write(tableau(par_fichier([Path(chemin) for chemin in sys.argv[1:]])))
