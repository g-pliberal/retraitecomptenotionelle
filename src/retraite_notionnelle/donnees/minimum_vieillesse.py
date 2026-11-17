"""Le barème du minimum vieillesse : l'ASPA, et avant elle les deux étages
(l'allocation aux vieux travailleurs salariés et l'allocation supplémentaire).

Un chargeur, que le coût, l'effet retour et la fabrique du paquet lisent sans
importer le moteur Python (action 161) ; le scénario 1 le reprend d'ici.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .chargement import Fiabilite
from .macro import DonneesMacro


@dataclass(frozen=True)
class DeuxEtages:
    """Le minimum vieillesse d'avant l'ASPA, une année, en euros par an.

    Le premier étage porte l'avantage de vieillesse au montant de l'allocation
    aux vieux travailleurs salariés (L. 814-2) ; le second, l'allocation
    supplémentaire, depuis 1956, n'est due que si son total et celui des
    ressources n'excède pas un plafond, et se réduit « à due concurrence »
    sinon (L. 815-8). ``supplementaire_menage`` est le montant servi à deux
    allocataires, que le barème distingue depuis le 1er juillet 1982 ;
    ``None`` avant, chacun ayant le sien. Avant 1956, le seul premier étage.
    """

    avts: float
    supplementaire: float
    supplementaire_menage: float | None
    plafond: float | None
    plafond_couple: float | None
    fiabilite: Fiabilite


class MinimumVieillesse:
    """Allocation de solidarité aux personnes âgées (ASPA).

    Le dernier plancher du système actuel, et le seul qui ne suppose aucune
    cotisation : une allocation DIFFÉRENTIELLE qui porte les ressources au
    montant du barème. Ce n'est pas une pension — elle est soumise à condition
    d'âge, de ressources du foyer et de demande, et récupérable sur les
    successions —, d'où la ligne séparée dans la cascade et le paramètre qui
    permet de la retirer.
    """

    #: Âge d'ouverture de droit commun. L'inapte l'a plus tôt : voir
    #: ``ageDeLAspa`` de ``moteur/js/droit/invalidite.js``.
    AGE_OUVERTURE = 65

    def __init__(self, racine: Path, macro: DonneesMacro) -> None:
        self.macro = macro
        self._table = self._lire(racine / "reference" / "legislation"
                                 / "minimum_vieillesse.csv")
        self._annees = sorted(self._table)
        #: Le barème d'un couple dont les deux membres sont allocataires, qui
        #: est aussi le plafond de ressources de tout couple (D. 815-2) : le
        #: foyer d'un assuré qui déclare un conjoint, et l'accueil.
        self._table_couple = self._lire(racine / "reference" / "legislation"
                                        / "minimum_vieillesse_couple.csv")
        #: Jusqu'en 2006, le minimum vieillesse à deux étages, une ligne par
        #: année depuis la loi du 14 mars 1941 (action 138, étape 6).
        self._deux_etages = self._lire_deux_etages(
            racine / "reference" / "legislation" / "minimum_vieillesse_avant_2007.csv")

    #: L'ASPA remplace l'allocation aux vieux travailleurs salariés et
    #: l'allocation supplémentaire le 13 janvier 2007 (ordonnance n° 2004-605,
    #: décret n° 2007-57) : jusqu'en 2006, le minimum tient en deux étages.
    DERNIERE_ANNEE_A_DEUX_ETAGES = 2006

    @staticmethod
    def _lire_deux_etages(chemin: Path) -> dict[int, DeuxEtages]:
        table: dict[int, DeuxEtages] = {}
        if not chemin.exists():
            return table

        def montant(texte: str) -> float | None:
            return float(texte) if texte else None

        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                table[int(ligne["annee"])] = DeuxEtages(
                    avts=float(ligne["avts"]),
                    supplementaire=montant(ligne["supplementaire"]) or 0.0,
                    supplementaire_menage=montant(ligne["supplementaire_menage"]),
                    plafond=montant(ligne["plafond"]),
                    plafond_couple=montant(ligne["plafond_couple"]),
                    fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
                )
        return table

    def deux_etages(self, annee: int) -> DeuxEtages | None:
        """Le minimum vieillesse à deux étages de l'année, s'il a cours : de
        1941 à 2006 ; ``None`` avant la loi du 14 mars 1941, et depuis l'ASPA."""
        if annee > self.DERNIERE_ANNEE_A_DEUX_ETAGES:
            return None
        return self._deux_etages.get(annee)

    @staticmethod
    def _lire(chemin: Path) -> dict[int, tuple[float, Fiabilite]]:
        table: dict[int, tuple[float, Fiabilite]] = {}
        if not chemin.exists():
            return table
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                table[int(ligne["annee"])] = (
                    float(ligne["valeur"]),
                    Fiabilite.depuis_texte(ligne["fiabilite"]),
                )
        return table

    def _en_vigueur(self, table: dict[int, tuple[float, Fiabilite]],
                    annee: int) -> tuple[float, Fiabilite] | None:
        if not table:
            return None
        if annee in table:
            return table[annee]
        annees = sorted(table)
        anterieures = [a for a in annees if a < annee]
        ancre = max(anterieures) if anterieures else annees[0]
        valeur, fiabilite = table[ancre]
        return valeur * self.macro.coefficient_prix(ancre, annee), fiabilite

    def plafond(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Montant maximal d'une personne seule, l'année demandée."""
        return self._en_vigueur(self._table, annee)

    def plafond_couple(self, annee: int) -> tuple[float, Fiabilite] | None:
        """Montant maximal d'un couple d'allocataires, et plafond de ressources
        de tout couple, l'année demandée."""
        return self._en_vigueur(self._table_couple, annee)
