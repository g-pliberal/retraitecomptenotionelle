"""Ce que chaque ministère verse au compte « Pensions », en part de ses crédits.

Le jaune pensions annexé au PLF 2027 décompose, à sa figure 3B, les crédits de
dix-sept ministères : la contribution employeur au CAS « Pensions », les
cotisations salariales, le reste des dépenses de personnel et le reste des
dépenses. ``credits_ministeres.csv`` les porte, lus sur les tracés de la
figure et certifiés (``scripts/fetch/sre_jaune_ministeres.py``). Ce module
n'en est que le chargeur, dont ``scripts/construire_donnees.py`` écrit les
parts au paquet : la contribution employeur, ce qui va au compte « Pensions »
et l'ordre des ministères, que la page Coût montre, ne se calculent que dans
``moteur/js/credits-ministeres.js`` (note de décision 0005). Aucun calcul du
modèle ne les lit (``memoire.HORS_DU_MODELE``).
"""

from __future__ import annotations

import csv
from pathlib import Path

from .chargement import Fiabilite


class CreditsMinisteres:
    """Les parts des crédits de chaque ministère, en fraction, pour l'année
    que porte le fichier : celle du projet de loi de finances."""

    def __init__(self, racine: Path) -> None:
        chemin = racine / "reference" / "macro" / "credits_ministeres.csv"
        parts: dict[tuple[str, str], float] = {}
        annees: set[int] = set()
        niveaux: list[Fiabilite] = []
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                annees.add(int(ligne["annee"]))
                parts[(ligne["ministere"], ligne["part"])] = float(ligne["valeur"])
                niveaux.append(Fiabilite.depuis_texte(ligne["fiabilite"]))
        if len(annees) != 1:
            raise ValueError(f"{chemin.name} doit porter une seule année, il en porte "
                             f"{sorted(annees)}")
        self.annee = annees.pop()
        self.fiabilite = min(niveaux)
        self._parts = parts

    def parts(self) -> dict[tuple[str, str], float]:
        """Toutes les parts, sous la clé (ministère, part)."""
        return dict(self._parts)
