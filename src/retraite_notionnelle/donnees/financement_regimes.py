"""Qui finance chaque régime : ses cotisants, l'État, ou personne.

CE QUE CETTE SÉRIE AJOUTE
--------------------------
``equilibre.py`` sait dire de quoi les ressources du SYSTÈME sont faites — deux
tiers de cotisations, une contribution d'équilibre de l'État, des impôts
affectés, des subventions. Il ne sait pas dire à QUI. La question que la page
« Coût » ne pouvait donc pas poser est pourtant celle qui décide du coût réel
d'une réforme : un scénario qui remplace tous les taux par 18 % rend-il de
l'argent à l'État, ou en demande-t-il aux caisses ?

La réponse n'est pas la même d'un régime à l'autre, et l'écart est énorme.
En 2023, l'État finance 86 % de la fonction publique d'État par sa contribution
d'équilibre et 61 % de la SNCF par une subvention, quand la CNRACL ne reçoit
rien de lui — mais porte un besoin de financement que personne ne couvre, 7 %
cette année-là et 49 % en 2070.

TROIS LIMITES, QUI SONT DANS L'EN-TÊTE DU FICHIER ET QU'ON RÉPÈTE ICI
---------------------------------------------------------------------
1. **Les années sont ÉPARSES** : 2010, 2015, 2023, 2030, 2040, 2050 et 2070
   selon les régimes, parce que le classeur du COR ne publie cette ventilation
   qu'à ces dates. Cette classe ne sait donc lire qu'une année PUBLIÉE et
   refuse les autres, là où ``SerieAnnuelle`` interpolerait. Interpoler une
   structure de financement entre 2030 et 2040 reviendrait à inventer une
   trajectoire que personne n'a calculée.
2. **Les parts ne somment pas toujours à un.** Cent couples sur 134 y sont à un
   millième près ; les autres s'en écartent jusqu'à onze pour cent. On les rend
   telles que publiées, et :meth:`somme` permet de le vérifier avant de s'en
   servir.
3. **La fonction publique d'État est d'un seul tenant**, civils et militaires
   confondus, là où le reste du dépôt les sépare.
"""

from __future__ import annotations

import csv
from pathlib import Path

#: Les deux postes par lesquels l'ÉTAT verse directement au régime. Les impôts
#: et taxes affectés n'en sont pas : ils compensent des exonérations de
#: cotisations, ce qui est une aide à l'activité et non un financement de la
#: retraite — ``cout.py`` tient déjà cette distinction pour l'agrégat, et la
#: mélanger ici ferait dire deux choses différentes au même mot.
POSTES_ETAT: tuple[str, ...] = ("contribution_equilibre_etat", "subventions_equilibre")

#: Le poste qui n'est financé par personne : ce que le régime devrait emprunter.
POSTE_DECOUVERT = "besoin_de_financement"


class StructureFinancement:
    """Part de chaque poste dans le financement de chaque régime, par année."""

    def __init__(self, racine: Path) -> None:
        chemin = racine / "reference" / "regimes" / "structure_financement.csv"
        parts: dict[tuple[str, int], dict[str, float]] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                cle = (ligne["regime"], int(ligne["annee"]))
                parts.setdefault(cle, {})[ligne["poste"]] = float(ligne["part"])
        self._parts = parts

    @property
    def regimes(self) -> list[str]:
        return sorted({regime for regime, _ in self._parts})

    def annees(self, regime: str) -> list[int]:
        """Les années PUBLIÉES pour ce régime, et il n'y en a pas d'autres."""
        return sorted(annee for r, annee in self._parts if r == regime)

    def ventilation(self, regime: str, annee: int) -> dict[str, float]:
        """Tous les postes d'un régime pour une année publiée.

        Lève ``KeyError`` sur une année non publiée, au lieu d'interpoler : le
        classeur ne donne que six ou sept dates, et rien ne dit comment la
        structure évolue entre elles.
        """
        try:
            return dict(self._parts[(regime, annee)])
        except KeyError:
            publiees = self.annees(regime)
            raise KeyError(
                f"{regime} n'a pas de ventilation publiée pour {annee} ; "
                f"années disponibles : {publiees}"
            ) from None

    def part(self, regime: str, poste: str, annee: int) -> float:
        """La part d'un poste, ou zéro si le classeur ne porte pas cette ligne."""
        return self.ventilation(regime, annee).get(poste, 0.0)

    def part_etat(self, regime: str, annee: int) -> float:
        """Ce que l'État verse directement : contribution et subvention d'équilibre."""
        ventilation = self.ventilation(regime, annee)
        return sum(ventilation.get(poste, 0.0) for poste in POSTES_ETAT)

    def part_decouvert(self, regime: str, annee: int) -> float:
        """Ce que personne ne finance, et qu'il faudrait donc emprunter."""
        return self.part(regime, POSTE_DECOUVERT, annee)

    def somme(self, regime: str, annee: int) -> float:
        """La somme des parts publiées, qui ne vaut pas toujours un.

        À consulter avant de tirer une conclusion d'une ventilation : le
        classeur du COR ne boucle pas partout, et on ne l'a pas corrigé.
        """
        return sum(self.ventilation(regime, annee).values())
