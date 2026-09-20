"""Combien de retraités dans chaque caisse, et donc ce que chaque cas type pèse.

C'est la pièce que `docs/limites.md` §5 bis déclarait manquante. Sans elle,
passer de douze carrières de référence à une masse de pensions obligeait à les
peser À ÉGALITÉ : l'agent de conduite comptait autant que le salarié au salaire
moyen, alors qu'il y a près de cent fois moins de retraités à la SNCF qu'à la
Cnav. La page « Coût » disait ce que valait cette convention — elle faisait du
rapport affiché un PLANCHER, les départs très précoces étant ceux que le
notionnel pénalise le plus et étant surreprésentés. Elle disait aussi qu'aucune
source ne fixerait la pondération. C'était faux : l'enquête annuelle auprès des
caisses de retraite la fixe, caisse par caisse et année par année.

CE QU'UN EFFECTIF DE CAISSE EST, ET CE QU'IL N'EST PAS
------------------------------------------------------
C'est un nombre de BÉNÉFICIAIRES d'un droit direct dans cette caisse, non un
nombre de personnes : un polypensionné compte dans chacune des siennes, et la
somme des caisses dépasse d'un tiers la ligne « tous régimes », qui compte les
personnes. Les poids qu'on en tire sont donc RELATIFS — seul leur rapport entre
cas types est utilisé, et la masse de pensions les normalise de toute façon en
divisant par celle du scénario actuel.

Le biais qui reste est connu et il est écrit dans `limites.md` : une caisse dont
les affiliés ont typiquement aussi une carrière au régime général — l'Ircantec,
la MSA salariés — est comptée deux fois, une fois chez elle et une fois à la
Cnav, ce qui gonfle le poids du salariat privé. Le sens du biais est l'inverse
de celui de l'ancienne convention, et il est beaucoup plus petit.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .chargement import Fiabilite, SerieAnnuelle, ValeurAnnuelle


class EffectifsRetraites:
    """Effectifs de retraités de droit direct, par caisse et par année.

    Chaque caisse est une :class:`SerieAnnuelle` : hors de la fenêtre publiée,
    la valeur du bord est reconduite et tombe au niveau ``estimee``. C'est le
    comportement qu'il faut ici — la répartition par régime de 1970 n'est pas
    celle de 2004, et la page ne doit pas prétendre le contraire.
    """

    #: Caisse dont l'effectif compte des PERSONNES et non des droits : la seule
    #: du fichier qui ne soit pas une caisse.
    TOUS_REGIMES = "tous_regimes"

    def __init__(self, racine: Path) -> None:
        chemin = racine / "reference" / "regimes" / "effectifs_retraites.csv"
        valeurs: dict[str, dict[int, ValeurAnnuelle]] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                annee = int(ligne["annee"])
                valeurs.setdefault(ligne["caisse"], {})[annee] = ValeurAnnuelle(
                    annee=annee,
                    valeur=float(ligne["effectifs"]),
                    fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
                )
        if not valeurs:
            raise ValueError(f"aucune ligne exploitable dans {chemin}")
        # PONCTUELLE, et non escalier : c'est une ENQUÊTE annuelle, où une
        # année absente est une année non mesurée et non une année sans
        # changement. La DREES ne publie pas la coordination RATP en 2022 —
        # 2020, 2021, 2023 et 2024, et rien entre les deux — et reconduire 2021
        # au niveau `certifiee` lui prêterait un chiffre qu'elle n'a pas
        # publié. La valeur reconduite reste la même ; ce qui change est
        # qu'elle se dit estimée.
        self._series = {
            caisse: SerieAnnuelle(points, nom=f"effectifs_{caisse}",
                                  interpolation="ponctuelle")
            for caisse, points in sorted(valeurs.items())
        }

    # -- accès ---------------------------------------------------------------

    def caisses(self) -> tuple[str, ...]:
        return tuple(self._series)

    def serie(self, caisse: str) -> SerieAnnuelle:
        if caisse not in self._series:
            raise KeyError(f"caisse inconnue : {caisse!r}")
        return self._series[caisse]

    def effectif(self, caisse: str, annee: int) -> float:
        return self.serie(caisse)(annee)

    def fiabilite(self, caisse: str, annee: int) -> Fiabilite:
        return self.serie(caisse).fiabilite(annee)

    @property
    def premiere_annee(self) -> int:
        return min(serie.premiere_annee for serie in self._series.values())

    @property
    def derniere_annee(self) -> int:
        return max(serie.derniere_annee for serie in self._series.values())
