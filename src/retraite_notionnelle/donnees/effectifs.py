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

AU-DELÀ DE LA DERNIÈRE ENQUÊTE
------------------------------
La répartition du bord est reconduite, sauf pour les caisses de la fonction
publique (:attr:`EffectifsRetraites.CAISSES_PROJETEES`) : le COR tient les
retraités de l'État stables jusqu'en 2070, ceux de ses civils en recul, et fait
croître de moitié ceux de la CNRACL, quand la population des retraités croît
d'un quart. Reconduire leur part de 2024 faisait croître les têtes de l'État de
22 % dans la grille (action 147, étape 9).
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

    #: Les caisses que la grille prolonge au-delà de la dernière enquête par
    #: les retraités que le COR leur projette (``retraites_projetes.csv``),
    #: et non par leur effectif de bord. Ce sont celles de la fonction
    #: publique, où le compte du COR suit les recrutements de fonctionnaires :
    #: le recul des civils de l'État, la croissance de la CNRACL. Ailleurs, les
    #: retraités qu'il compte croissent bien plus vite que les personnes, à
    #: mesure que les polypensionnés se multiplient — ceux de la Cnav de 40 %
    #: jusqu'en 2070, ceux de l'Ircantec de 160 %, les personnes de 28 % — :
    #: les prolonger ainsi pèserait plus de carrières qu'il n'y a de retraités
    #: (la dérive de 2070 passait de 1,097 à 1,111), et les autres caisses
    #: gardent leur répartition de 2024.
    CAISSES_PROJETEES = ("fonction_publique_etat_civile",
                         "fonction_publique_etat_militaire", "cnracl")

    def __init__(self, racine: Path,
                 projetees: tuple[str, ...] = CAISSES_PROJETEES) -> None:
        """``projetees`` : les caisses prolongées par le COR ; vide, toutes
        gardent leur effectif de bord, la convention d'avant l'étape 9."""
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
        _prolonger(valeurs, racine, projetees)
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


def _prolonger(valeurs: dict[str, dict[int, ValeurAnnuelle]], racine: Path,
               caisses: tuple[str, ...]) -> None:
    """Prolonge chaque caisse de ``caisses`` au-delà de sa dernière enquête,
    par la croissance que le COR donne à ses retraités, RAPPORTÉE à celle de
    tous les retraités.

    Les poids des cas types sont relatifs : ce qu'une caisse doit garder est
    sa PART des retraités, non son effectif, que la grille ne lit pas — le
    nombre de ses têtes vient de la population de chaque âge. La croissance de
    la caisse vient du classeur par régime du COR de juin 2024
    (``retraites_projetes.csv``) ; celle des personnes, des taux que le
    rapport de juin 2026 publie par sous-période (tableau 2.1,
    ``croissance_depense_retraite.csv``) : deux millésimes, que rien d'autre
    ne permet d'apparier. La valeur prolongée est ``estimee``, comme celle que
    la reconduction donnait ; au-delà du classeur, la dernière est reconduite.
    """
    projetes = _lire_projetes(racine / "reference" / "regimes" / "retraites_projetes.csv")
    personnes = _taux_personnes(racine / "reference" / "macro"
                                / "croissance_depense_retraite.csv")
    if not projetes or not personnes:
        return
    for caisse in caisses:
        points, cor = valeurs.get(caisse), projetes.get(caisse)
        if not points or not cor:
            continue
        bord = max(points)
        if bord not in cor:
            continue
        indice = 1.0
        for annee in range(bord + 1, max(cor) + 1):
            taux = next((t for (debut, fin), t in personnes.items()
                         if debut < annee <= fin), None)
            if taux is None or annee not in cor:
                break
            indice *= 1.0 + taux
            points[annee] = ValeurAnnuelle(
                annee=annee,
                valeur=points[bord].valeur * cor[annee] / cor[bord] / indice,
                fiabilite=Fiabilite.ESTIMEE,
            )


def _lire_projetes(chemin: Path) -> dict[str, dict[int, float]]:
    """Les retraités de droit direct que le COR projette, caisse par caisse."""
    if not chemin.exists():
        return {}
    projetes: dict[str, dict[int, float]] = {}
    with chemin.open(encoding="utf-8") as flux:
        for ligne in csv.DictReader(l for l in flux if not l.lstrip().startswith("#")):
            projetes.setdefault(ligne["caisse"], {})[int(ligne["annee"])] = float(
                ligne["retraites"])
    return projetes


def _taux_personnes(chemin: Path) -> dict[tuple[int, int], float]:
    """Le rythme annuel des retraités de tous les régimes, sous-période par
    sous-période du COR : ``{(début, fin): taux}``, qui vaut pour les années
    de début exclu à fin incluse."""
    if not chemin.exists():
        return {}
    taux: dict[tuple[int, int], float] = {}
    with chemin.open(encoding="utf-8") as flux:
        for ligne in csv.DictReader(l for l in flux if not l.lstrip().startswith("#")):
            if ligne["grandeur"] == "retraites":
                debut, fin = (int(a) for a in ligne["periode"].split("-"))
                taux[(debut, fin)] = float(ligne["taux"])
    return taux
