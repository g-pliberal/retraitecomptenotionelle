"""Ce que le moteur rend, lu par `moteur.mjs` sous node : les tables que la
pension lit, la pratique que le moteur garde au code, et les grilles de la
comparaison."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).with_name("moteur.mjs")


def extraire(racine) -> dict:
    """Les tables de la décote et de la proratisation par mois de naissance,
    et `DUREES_AVANT_LE_DECRET`."""
    sortie = subprocess.run(["node", str(SCRIPT), str(racine), "extrait"], check=True,
                            capture_output=True, text=True).stdout
    return json.loads(sortie)


def lignes(racine, quoi: str):
    """Les lignes de la grille ``durees`` ou ``fiches``, découpées en champs,
    au fil de ce que node écrit."""
    with subprocess.Popen(["node", str(SCRIPT), str(racine), quoi], stdout=subprocess.PIPE,
                          text=True) as p:
        for ligne in p.stdout:
            yield ligne.rstrip("\n").split("\t")
    if p.returncode:
        raise subprocess.CalledProcessError(p.returncode, p.args)
