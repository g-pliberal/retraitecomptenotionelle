"""Qui vit en couple après 65 ans, âge par âge et par sexe.

CE QUE LE FICHIER PORTE. ``vie_en_couple.csv`` donne, pour chaque âge de 65 ans
à la fin de la table et pour chaque sexe, la part des personnes vivant en
couple et la part vivant seules, telles que l'*Insee Première* n° 2040 les
publie sur le recensement de 2021. Voir
``scripts/fetch/insee_vie_en_couple.py``.

À QUOI ÇA SERT. À une seule question, celle de la reprise sur succession : deux
bénéficiaires de la garantie qui vivent ensemble laissent DEUX avances sur UNE
succession, celle du survivant. Une avance deux fois plus grosse n'est pas deux
fois mieux couverte par un patrimoine donné — c'est même l'inverse —, et sans
cette part le modèle confrontait chaque avance au patrimoine d'un ménage
entier.

CE QUI EST FIGÉ. « Vivre en couple » est une cohabitation au sens du
recensement, pas un régime matrimonial : deux concubins ne se succèdent pas
l'un à l'autre, et leurs deux avances ne pèsent pas sur la même succession.
La part retenue est donc une borne haute du regroupement.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .chargement import Fiabilite


class VieEnCouple:
    """Les parts publiées, au millésime le plus récent du fichier."""

    def __init__(self, racine: Path) -> None:
        chemin = racine / "reference" / "macro" / "vie_en_couple.csv"
        parts: dict[int, dict[tuple[int, str, str], float]] = {}
        fiabilites: dict[int, Fiabilite] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                annee = int(ligne["annee"])
                cle = (int(ligne["age"]), ligne["sexe"], ligne["mode"])
                parts.setdefault(annee, {})[cle] = float(ligne["part_pct"]) / 100.0
                niveau = Fiabilite.depuis_texte(ligne["fiabilite"])
                courante = fiabilites.get(annee)
                fiabilites[annee] = niveau if courante is None else min(courante, niveau)
        if not parts:
            raise ValueError(f"aucune ligne exploitable dans {chemin}")
        self.annee = max(parts)
        self._parts = parts[self.annee]
        self.fiabilite = fiabilites[self.annee]
        self.age_minimal = min(age for age, _, _ in self._parts)
        self.age_maximal = max(age for age, _, _ in self._parts)

    def part(self, age: float, sexe: str, mode: str = "couple") -> float:
        """La part publiée pour cet âge, ce sexe et ce mode de résidence.

        Hors de la table, la valeur du bord est reconduite : le recensement
        s'arrête là où les effectifs deviennent trop minces pour être publiés.
        """
        rang = int(min(max(age, self.age_minimal), self.age_maximal))
        return self._parts.get((rang, sexe, mode), 0.0)

    def part_moyenne(self, sexe: str, exposition: list[float] | tuple[float, ...],
                     age_debut: int = 65, mode: str = "couple") -> float:
        """La part moyenne sur une courbe d'exposition : les survivants d'une
        table de mortalité, âge par âge à partir de ``age_debut``.

        C'est la bonne pondération pour une question posée sur les ANNÉES
        vécues — une avance se constitue tant que le bénéficiaire vit —, et
        non sur les têtes de départ.
        """
        total = sum(exposition)
        if total <= 0.0:
            return 0.0
        return sum(
            poids * self.part(age_debut + rang, sexe, mode)
            for rang, poids in enumerate(exposition)
        ) / total
