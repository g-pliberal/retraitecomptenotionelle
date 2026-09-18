"""Frais de l'enveloppe d'épargne retraite, tels qu'ils sont pratiqués.

Le pilier capitalisé de la proposition est logé dans le PER, qui existe déjà.
Une enveloppe a un prix : trois prélèvements, que l'Observatoire des produits
d'épargne financière mesure chaque année sur les remises de l'ACPR, et que
``data/reference/macro/frais_epargne_retraite.yaml`` porte.

Les VALEURS DE CALCUL sont dans :class:`Parametres`, comme tout ce qui se fait
varier ; ce module lit le fichier de référence, qui en est la source et la
justification. Un test vérifie que les deux disent la même chose — sans quoi le
barème affiché sur la page Données ne serait plus celui du calcul.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from .chargement import Fiabilite, charger_yaml


@dataclass(frozen=True)
class Frais:
    """Un poste de frais, sa valeur et ce sur quoi il est prélevé."""

    cle: str
    valeur: float
    assiette: str
    libelle: str
    note: str


class FraisEpargneRetraite:
    """Le barème publié, poste par poste."""

    def __init__(self, racine: Path) -> None:
        self.chemin = racine / "reference" / "macro" / "frais_epargne_retraite.yaml"

    @cached_property
    def _contenu(self) -> dict:
        return charger_yaml(self.chemin)

    @property
    def annee_reference(self) -> int:
        return int(self._contenu["annee_reference"])

    @property
    def publication(self) -> str:
        return str(self._contenu["publication"])

    @property
    def fiabilite(self) -> Fiabilite:
        return Fiabilite.depuis_texte(self._contenu["fiabilite"])

    @cached_property
    def postes(self) -> dict[str, Frais]:
        return {
            cle: Frais(
                cle=cle,
                valeur=float(poste["valeur"]),
                assiette=str(poste["assiette"]),
                libelle=str(poste["libelle"]),
                note=" ".join(str(poste.get("note", "")).split()),
            )
            for cle, poste in self._contenu["frais"].items()
        }

    def __getitem__(self, cle: str) -> Frais:
        return self.postes[cle]

    def valeur(self, cle: str) -> float:
        return self.postes[cle].valeur
