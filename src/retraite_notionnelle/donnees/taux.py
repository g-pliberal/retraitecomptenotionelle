"""Courbe des taux sans risque, et taux forward qui s'en déduisent.

Le pilier de capitalisation obligatoire place ses versements sur des titres
sans risque à plusieurs maturités. Il lui faut donc deux choses, et ce module
les donne toutes les deux à partir d'une seule donnée observée :

1. **le taux d'aujourd'hui pour chaque maturité** — la courbe zéro-coupon des
   souverains AAA de la zone euro, publiée par la BCE
   (``data/reference/macro/courbe_taux_sans_risque.csv``) ;
2. **le taux auquel se placeront les versements des années suivantes** — les
   taux FORWARD implicites de cette même courbe.

Le second point est ce qui dispense le modèle d'une prévision maison. Un
versement fait dans dix ans pour vingt ans ne se place pas au taux à vingt ans
d'aujourd'hui : il se place au taux que le marché cote déjà pour cette période,
et ce taux est entièrement déterminé par la courbe. Si l'on pouvait emprunter à
trente ans et prêter à dix, le forward serait arbitré ; c'est pourquoi il n'est
pas une opinion :

.. math::  f(T_1, T_2) = \\frac{z(T_2) \\, T_2 - z(T_1) \\, T_1}{T_2 - T_1}

où :math:`z(T)` est le taux zéro-coupon continu à l'horizon :math:`T`.

**Ce que cela suppose, et qui n'est pas rien.** Prendre le forward pour le taux
FUTUR, c'est l'hypothèse des anticipations pures : elle ignore la prime de
terme, qui rend le forward un peu supérieur au taux futur moyen quand la courbe
est ascendante. Le pilier s'en trouve légèrement flatté. L'alternative — une
prévision de taux — supposerait davantage, et personne ne la vérifierait. Voir
``docs/methodologie.md`` et ``docs/limites.md``.

**Unités.** La BCE publie des taux à composition CONTINUE, et le fichier de
référence les garde tels quels. Toute sortie de ce module est en revanche un
taux ANNUEL (:math:`e^{r} - 1`), parce que c'est ce qu'une accumulation année
par année consomme. La conversion est faite ici, une fois, et pas à la saisie.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from .chargement import Fiabilite


@dataclass(frozen=True)
class TauxPlacement:
    """Un taux de placement, et ce qu'il faut savoir pour le juger."""

    #: Taux ANNUEL équivalent, en fraction.
    taux: float
    #: Différé en années entre la date de la courbe et le placement.
    differe: int
    #: Durée du placement, en années.
    duree: int
    fiabilite: Fiabilite

    @property
    def horizon(self) -> int:
        """Point de la courbe où le placement s'achève."""
        return self.differe + self.duree


class CourbeTauxSansRisque:
    """La dernière courbe publiée, et les forwards qui s'en déduisent.

    Le fichier de référence garde les courbes successives, une ligne par date
    et par maturité ; c'est la plus récente qui sert. Une courbe est un
    instantané : mélanger deux dates donnerait une pente qui n'a jamais été
    cotée.
    """

    #: Au-delà de la dernière maturité publiée, le taux zéro-coupon est
    #: prolongé à plat. Ce n'est pas neutre — cela revient à supposer que le
    #: taux forward au-delà de trente ans égale le taux zéro-coupon à trente
    #: ans — mais c'est la seule extrapolation qui n'ajoute aucun paramètre, et
    #: les valeurs qu'elle produit sont déclarées ``estimee``.
    def __init__(self, racine: Path) -> None:
        self.chemin = racine / "reference" / "macro" / "courbe_taux_sans_risque.csv"

    @cached_property
    def _courbe(self) -> tuple[str, dict[int, float], Fiabilite]:
        lignes: dict[str, dict[int, float]] = {}
        fiabilites: dict[str, Fiabilite] = {}
        with self.chemin.open(encoding="utf-8") as flux:
            utiles = (l for l in flux if not l.lstrip().startswith("#"))
            for enregistrement in csv.DictReader(utiles):
                jour = enregistrement["date"]
                lignes.setdefault(jour, {})[int(enregistrement["maturite"])] = float(
                    enregistrement["taux_continu"]
                )
                niveau = Fiabilite.depuis_texte(enregistrement["fiabilite"])
                fiabilites[jour] = min(fiabilites.get(jour, Fiabilite.CERTIFIEE), niveau)
        if not lignes:
            raise ValueError(f"aucune courbe exploitable dans {self.chemin}")
        jour = max(lignes)
        return jour, dict(sorted(lignes[jour].items())), fiabilites[jour]

    @property
    def date(self) -> str:
        """Date d'observation de la courbe retenue, ``AAAA-MM-JJ``."""
        return self._courbe[0]

    @property
    def annee(self) -> int:
        """Année d'observation : l'origine des différés."""
        return int(self.date[:4])

    @property
    def maturites(self) -> tuple[int, ...]:
        return tuple(self._courbe[1])

    @property
    def maturite_maximale(self) -> int:
        return max(self._courbe[1])

    @property
    def fiabilite_publiee(self) -> Fiabilite:
        return self._courbe[2]

    def zero_continu(self, horizon: float) -> float:
        """Taux zéro-coupon continu à ``horizon`` années, interpolé linéairement.

        En deçà de la première maturité publiée et au-delà de la dernière, le
        taux est prolongé à plat : la courbe ne dit rien de ces horizons, et
        une extrapolation de pente en dirait davantage qu'elle ne sait.
        """
        courbe = self._courbe[1]
        maturites = self.maturites
        if horizon <= maturites[0]:
            return courbe[maturites[0]]
        if horizon >= maturites[-1]:
            return courbe[maturites[-1]]
        precedente = max(m for m in maturites if m <= horizon)
        suivante = min(m for m in maturites if m >= horizon)
        if precedente == suivante:
            return courbe[precedente]
        poids = (horizon - precedente) / (suivante - precedente)
        return courbe[precedente] * (1 - poids) + courbe[suivante] * poids

    def forward_continu(self, differe: float, duree: float) -> float:
        """Taux forward continu d'un placement différé de ``differe`` années.

        ``differe = 0`` rend le taux zéro-coupon comptant, sans cas particulier :
        la formule s'y réduit d'elle-même.
        """
        if duree <= 0:
            raise ValueError("la durée d'un placement doit être strictement positive")
        depart, arrivee = differe, differe + duree
        return (
            self.zero_continu(arrivee) * arrivee - self.zero_continu(depart) * depart
        ) / duree

    def placement(self, annee_placement: int, duree: int) -> TauxPlacement:
        """Taux annuel d'un placement fait en ``annee_placement`` pour ``duree`` ans.

        Le différé se compte en années pleines depuis l'année de la courbe. Un
        placement antérieur à la courbe — il n'y en a pas, le pilier s'ouvre
        l'année de la bascule — serait traité comme un placement comptant.
        """
        differe = max(0, annee_placement - self.annee)
        taux_continu = self.forward_continu(differe, duree)
        fiabilite = (
            self.fiabilite_publiee
            if differe + duree <= self.maturite_maximale
            else Fiabilite.ESTIMEE
        )
        return TauxPlacement(
            taux=math.exp(taux_continu) - 1.0,
            differe=differe,
            duree=duree,
            fiabilite=fiabilite,
        )
