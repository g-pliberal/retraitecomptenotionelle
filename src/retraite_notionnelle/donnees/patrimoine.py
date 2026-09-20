"""Le patrimoine des ménages, et ce qu'une succession couvre d'une avance.

CE QUE LE FICHIER PORTE. ``patrimoine_menages.csv`` donne, par population, des
quantiles (déciles, centiles), une médiane et une moyenne du patrimoine par
ménage : les ménages dans leur ensemble, lus chez l'INSEE pour 2021 et 2024 ;
les ménages de retraités, et le quart de ceux-ci au revenu disponible le plus
bas, recopiés du COR pour 2018. Voir ``scripts/fetch/insee_patrimoine_menages.py``.

CE QUE LE MODULE EN FAIT. Une seule question : quelle part d'une AVANCE d'un
montant donné une succession tirée de cette population couvre-t-elle, en
moyenne ? C'est l'espérance de ``min(avance, patrimoine)`` rapportée à
l'avance, et elle demande une distribution entière là où le fichier ne donne
que quelques points. Deux formes, selon ce que la population publie :

- des QUANTILES (au moins deux) : la fonction de quantile est prise linéaire
  entre les points publiés, nulle en zéro, et plate au-delà du dernier point.
  Plate, et non prolongée : au-delà du dernier quantile, on ne sait rien, et
  un patrimoine de 622 900 € couvre déjà toute avance que la garantie puisse
  constituer. L'espérance se calcule segment par segment, sans tirage ;
- une MÉDIANE et une MOYENNE seulement : une log-normale les reproduit toutes
  les deux (l'écart-type du logarithme vaut ``sqrt(2·ln(moyenne/médiane))``),
  et l'espérance a une forme fermée. La fonction de répartition normale y est
  approchée par la formule 7.1.26 d'Abramowitz et Stegun, à 1,5·10⁻⁷ près,
  la même dans le portage JavaScript, pour que les deux moteurs rendent le
  même chiffre.

CE QUI EST FIGÉ. Le patrimoine est celui d'un MÉNAGE ; une avance est celle
d'une PERSONNE, et un couple de deux bénéficiaires pèse deux avances sur une
succession : cette convention compte une avance par succession, et surestime
donc la couverture d'autant. Le patrimoine des retraités selon leur pension
n'est publié nulle part : le premier quartile de REVENU DISPONIBLE tient lieu
des plus petites pensions, l'ensemble des retraités des autres, et c'est
``cout._reprises_successions`` qui dit comment il passe de l'un à l'autre.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .chargement import Fiabilite

#: L'ordre des quantiles publiés, et le rang de chacun.
RANGS = {
    "d1": 0.1, "d2": 0.2, "d3": 0.3, "d4": 0.4, "mediane": 0.5, "d6": 0.6,
    "d7": 0.7, "d8": 0.8, "d9": 0.9, "p95": 0.95, "p99": 0.99,
}


def repartition_normale(x: float) -> float:
    """Φ(x), par la formule 7.1.26 d'Abramowitz et Stegun — la même que le
    portage JavaScript, qui n'a pas ``erf``."""
    signe = 1.0 if x >= 0.0 else -1.0
    z = abs(x) / math.sqrt(2.0)
    t = 1.0 / (1.0 + 0.3275911 * z)
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741
           + t * (-1.453152027 + t * 1.061405429))))
    erf = 1.0 - poly * math.exp(-z * z)
    return 0.5 * (1.0 + signe * erf)


@dataclass(frozen=True)
class DistributionPatrimoine:
    """Une population, sa forme, et ce qu'une succession y couvre."""

    population: str
    annee: int
    patrimoine: str
    #: Les quantiles publiés, (rang, valeur) croissants ; vide pour une
    #: log-normale.
    quantiles: tuple[tuple[float, float], ...]
    mediane: float
    moyenne: float

    @property
    def forme(self) -> str:
        return "quantiles" if len(self.quantiles) >= 2 else "log-normale"

    def couverture(self, avance: float) -> float:
        """La part d'une avance qu'une succession couvre, en moyenne :
        ``E[min(avance, W)] / avance``, dans les euros de la population.

        Vaut un pour une avance nulle ou négative — rien à couvrir —, et
        décroît avec l'avance.
        """
        if avance <= 0.0:
            return 1.0
        if self.forme == "quantiles":
            esperance = self._esperance_min_quantiles(avance)
        else:
            esperance = self._esperance_min_lognormale(avance)
        return min(1.0, max(0.0, esperance / avance))

    def _esperance_min_quantiles(self, avance: float) -> float:
        points = ((0.0, 0.0),) + self.quantiles
        total = 0.0
        for (u0, q0), (u1, q1) in zip(points, points[1:]):
            largeur = u1 - u0
            if largeur <= 0.0:
                continue
            if q1 <= avance:
                total += 0.5 * (q0 + q1) * largeur
            elif q0 >= avance:
                total += avance * largeur
            else:
                # Le segment croise l'avance en u* : en dessous, la moyenne du
                # trapèze ; au-dessus, l'avance elle-même.
                u_croise = u0 + largeur * (avance - q0) / (q1 - q0)
                total += 0.5 * (q0 + avance) * (u_croise - u0) + avance * (u1 - u_croise)
        u_dernier, q_dernier = points[-1]
        total += min(avance, q_dernier) * (1.0 - u_dernier)
        return total

    def _esperance_min_lognormale(self, avance: float) -> float:
        sigma = math.sqrt(2.0 * math.log(self.moyenne / self.mediane))
        mu = math.log(self.mediane)
        z = (math.log(avance) - mu) / sigma
        return (self.moyenne * repartition_normale(z - sigma)
                + avance * (1.0 - repartition_normale(z)))


class PatrimoineMenages:
    """Le fichier, population par population, au millésime le plus récent."""

    def __init__(self, racine: Path, patrimoine: str = "brut") -> None:
        chemin = racine / "reference" / "macro" / "patrimoine_menages.csv"
        valeurs: dict[tuple[str, int], dict[str, float]] = {}
        fiabilites: dict[tuple[str, int], Fiabilite] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                if ligne["patrimoine"] != patrimoine:
                    continue
                cle = (ligne["population"], int(ligne["annee"]))
                valeurs.setdefault(cle, {})[ligne["statistique"]] = float(ligne["valeur"])
                niveau = Fiabilite.depuis_texte(ligne["fiabilite"])
                courante = fiabilites.get(cle)
                fiabilites[cle] = niveau if courante is None else min(courante, niveau)
        if not valeurs:
            raise ValueError(f"aucune ligne exploitable dans {chemin} (patrimoine={patrimoine!r})")
        self.patrimoine = patrimoine
        self._valeurs = valeurs
        self._fiabilites = fiabilites
        self._distributions: dict[str, DistributionPatrimoine] = {}

    @property
    def populations(self) -> tuple[str, ...]:
        return tuple(sorted({population for population, _ in self._valeurs}))

    def annee(self, population: str) -> int:
        annees = [annee for pop, annee in self._valeurs if pop == population]
        if not annees:
            raise KeyError(f"population inconnue : {population!r} (connues : {self.populations})")
        return max(annees)

    def fiabilite(self, population: str) -> Fiabilite:
        return self._fiabilites[(population, self.annee(population))]

    def statistiques(self, population: str) -> dict[str, float]:
        return dict(self._valeurs[(population, self.annee(population))])

    def distribution(self, population: str) -> DistributionPatrimoine:
        if population in self._distributions:
            return self._distributions[population]
        annee = self.annee(population)
        stats = self._valeurs[(population, annee)]
        quantiles = tuple(sorted(
            (RANGS[nom], valeur) for nom, valeur in stats.items() if nom in RANGS
        ))
        mediane = stats.get("mediane", 0.0)
        moyenne = stats.get("moyenne", 0.0)
        if len(quantiles) < 2 and not (mediane > 0.0 and moyenne > mediane):
            raise ValueError(
                f"{population} : il faut deux quantiles, ou une médiane et une "
                f"moyenne supérieure, pour une distribution"
            )
        if any(b <= a for (_, a), (_, b) in zip(quantiles, quantiles[1:])):
            raise ValueError(f"{population} : quantiles non croissants")
        distribution = DistributionPatrimoine(
            population=population, annee=annee, patrimoine=self.patrimoine,
            quantiles=quantiles, mediane=mediane, moyenne=moyenne,
        )
        self._distributions[population] = distribution
        return distribution
