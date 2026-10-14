"""Ce que chaque ministère verse au compte « Pensions », en part de ses crédits.

Le jaune pensions annexé au PLF 2027 décompose, à sa figure 3B, les crédits de
dix-sept ministères : la contribution employeur au CAS « Pensions », les
cotisations salariales, le reste des dépenses de personnel et le reste des
dépenses. ``credits_ministeres.csv`` les porte, lus sur les tracés de la
figure et certifiés (``scripts/fetch/sre_jaune_ministeres.py``) ; la page Coût
les montre, par le paquet (``moteur/js/credits-ministeres.js``, son jumeau).
Aucun calcul du modèle ne les lit (``memoire.HORS_DU_MODELE``).
"""

from __future__ import annotations

import csv
from pathlib import Path

from ..somme import somme_ordonnee
from .chargement import Fiabilite

#: Les parts que verse le compte « Pensions » : la contribution employeur,
#: sur les dépenses de personnel (T2 CAS) ou, pour les opérateurs de
#: l'Enseignement supérieur, sur leurs crédits de fonctionnement (T3 CAS).
CONTRIBUTION = ("t2_cas", "t3_cas")


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
        #: Les ministères, du plus au moins versé au compte « Pensions ».
        self.ministeres = tuple(sorted({m for m, _ in parts},
                                       key=lambda m: (-self.au_compte_pensions(m), m)))

    def part(self, ministere: str, part: str) -> float:
        """Une part des crédits d'un ministère ; zéro pour une part que sa
        barre ne trace pas — le T3 CAS, hors de l'Enseignement supérieur."""
        if not any(m == ministere for m, _ in self._parts):
            raise KeyError(f"ministère absent de la figure 3B : {ministere}")
        return self._parts.get((ministere, part), 0.0)

    def parts(self) -> dict[tuple[str, str], float]:
        """Toutes les parts, sous la clé (ministère, part)."""
        return dict(self._parts)

    def contribution(self, ministere: str) -> float:
        """La contribution employeur que le ministère verse au compte."""
        return somme_ordonnee(self.part(ministere, part) for part in CONTRIBUTION)

    def au_compte_pensions(self, ministere: str) -> float:
        """Ce qui va au compte « Pensions » : la contribution, et la retenue
        des fonctionnaires."""
        return self.contribution(ministere) + self.part(ministere, "cotisations_salariales")
