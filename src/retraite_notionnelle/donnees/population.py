"""La pyramide des âges : combien de gens, à quel âge, quelle année.

C'est la pièce que `docs/limites.md` déclarait manquante. Sans elle, passer d'un
droit individuel à un coût collectif obligeait à supposer toutes les générations
de même taille — ce que le baby-boom dément d'un tiers, et ce qui interdisait
purement et simplement de projeter.

Une seule source, et une seule méthodologie de part et d'autre de la frontière :
le scénario central des **projections de population 2026** de l'INSEE, dont
l'onglet ``population`` porte l'effectif au 1er janvier par âge détaillé et par
année, de 1962 à 2070. L'INSEE date lui-même la frontière — estimations jusqu'en
2023, projections ensuite — et le dépôt la reprend telle quelle : ce qui est
projeté entre au niveau ``estimee``, et cette fiabilité se propage jusqu'au
résultat affiché.

Deux séries en sont tirées, qui ne servent pas à la même chose :

* ``effectif(age, annee)`` compte des **retraités** — d'où le plancher à 50 ans,
  en deçà duquel aucune pension de droit direct n'est servie ;
* ``actifs(annee)`` compte les **20-64 ans**, et ne sert qu'à projeter le
  dénominateur d'une part de PIB.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .chargement import Fiabilite, SerieAnnuelle, charger_serie_annuelle

#: Âge plancher de la série, et donc âge en deçà duquel ``effectif`` rend zéro.
#: Le cas type qui liquide le plus tôt part à 52 ans.
AGE_MINIMAL = 50


class Population:
    """Effectifs par âge et par année, observés puis projetés."""

    def __init__(self, racine: Path) -> None:
        macro = racine / "reference" / "macro"
        self._effectifs: dict[int, dict[int, float]] = {}
        self._fiabilites: dict[int, Fiabilite] = {}
        chemin = macro / "population_par_age.csv"
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                annee, age = int(ligne["annee"]), int(ligne["age"])
                self._effectifs.setdefault(annee, {})[age] = float(ligne["effectif"])
                niveau = Fiabilite.depuis_texte(ligne["fiabilite"])
                courante = self._fiabilites.get(annee)
                self._fiabilites[annee] = (
                    niveau if courante is None else min(courante, niveau)
                )
        if not self._effectifs:
            raise ValueError(f"aucune ligne exploitable dans {chemin}")

        self.actifs: SerieAnnuelle = charger_serie_annuelle(
            macro / "population_active.csv", "effectif", nom="population_active"
        )
        self._annees = sorted(self._effectifs)
        self.premiere_annee = self._annees[0]
        self.derniere_annee = self._annees[-1]
        self.age_maximal = max(
            age for effectifs in self._effectifs.values() for age in effectifs
        )

    # -- accès ---------------------------------------------------------------

    def _annee_bornee(self, annee: int) -> int:
        """Année ramenée dans la plage publiée.

        La série commence en 1962, la dépense observée en 1959 : les trois
        premières années empruntent la pyramide de 1962. C'est une approximation
        assumée, et elle porte sur trois années dont la dépense pèse un demi
        pour cent de celle d'aujourd'hui.
        """
        return min(max(annee, self.premiere_annee), self.derniere_annee)

    def effectif(self, age: int, annee: int) -> float:
        """Effectif d'un âge une année donnée ; zéro hors de la plage d'âges."""
        return self._effectifs[self._annee_bornee(annee)].get(age, 0.0)

    def effectif_tranche(self, age_debut: int, age_fin: int, annee: int) -> float:
        """Effectif cumulé d'une tranche d'âges, bornes comprises."""
        effectifs = self._effectifs[self._annee_bornee(annee)]
        return sum(
            effectifs.get(age, 0.0) for age in range(age_debut, age_fin + 1)
        )

    def fiabilite(self, annee: int) -> Fiabilite:
        """Fiabilité de la pyramide d'une année.

        Hors de la plage publiée, la valeur est empruntée : elle ne peut donc
        pas valoir mieux qu'``estimee``.
        """
        if annee < self.premiere_annee or annee > self.derniere_annee:
            return Fiabilite.ESTIMEE
        return self._fiabilites[annee]

    def annees(self) -> list[int]:
        return list(self._annees)
