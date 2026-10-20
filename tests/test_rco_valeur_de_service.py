"""La valeur de service du point de la retraite complémentaire obligatoire des
non-salariés agricoles, lue au code rural année après année.

L'article D. 732-166 du code rural et de la pêche maritime fixe chaque année la
valeur de service du point ; `scripts/fetch/dila_legi_msa.py` la lit dans la
base LEGI et `scripts/verifier_donnees.py` la certifie. Le reste de la série —
ses bornes, sa continuité, la séparation de la base et de la complémentaire —
est tenu par `test_simulateur.py`
(`test_valeur_du_point_de_la_complementaire_agricole_est_sourcee`) : ce
fichier ne tient que les années qu'une veille a ajoutées depuis.
"""

from __future__ import annotations

import csv

import pytest

from retraite_notionnelle.config import RACINE_DONNEES


def _valeurs_de_service() -> dict[int, float]:
    chemin = RACINE_DONNEES / "reference" / "regimes" / "valeurs_point.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = [ligne for ligne in csv.DictReader(
            x for x in flux if not x.lstrip().startswith("#"))
            if ligne["regime"] == "msa_rco" and ligne["mesure"] == "valeur_service"]
    assert {ligne["fiabilite"] for ligne in lignes} == {"certifiee"}
    return {int(ligne["annee"]): float(ligne["valeur"]) for ligne in lignes}


def test_la_valeur_de_service_de_2026():
    """« 0,3954 euros pour l'année 2026 » : D. 732-166 dans la rédaction du
    décret n° 2026-931 du 6 octobre 2026 (LEGIARTI000054963689, en vigueur le
    9 octobre 2026). La série du dépôt s'arrêtait à 2025."""
    valeurs = _valeurs_de_service()
    assert valeurs[2026] == pytest.approx(0.3954)
    assert valeurs[2026] > valeurs[2025]
