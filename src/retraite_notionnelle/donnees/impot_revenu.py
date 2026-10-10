"""Les paramètres de l'impôt sur le revenu, d'une année de revenus à l'autre.

Le dépôt ne calculait aucun impôt sur le revenu (action 138, étape 5). Ce module
lit ses barèmes, marche par marche, dans
``data/reference/legislation/impot_revenu.yaml``, qu'écrit
``scripts/fetch/ipp_impot_revenu.py`` depuis les barèmes de l'IPP et l'index
LEGI, et rend ceux d'une année de REVENUS : le barème « de 2023 » est celui de
la loi de finances pour 2024, qui impose les revenus de 2023.

Chaque montant est dans la monnaie de son année, francs jusqu'aux revenus de
2000, euros ensuite : le calcul d'une année en francs se fait en francs
(:mod:`~retraite_notionnelle.impot_revenu`).

AU-DELÀ DE LA DERNIÈRE ANNÉE LUE, le barème se projette. Par défaut sur les
PRIX, comme le font les lois de finances, qui relèvent chaque année les seuils
du barème, et ceux que le code relève « dans la même proportion que la limite
supérieure de la première tranche », de l'évolution des prix de l'année des
revenus ; en variante sur le SALAIRE MOYEN, comme l'OCDE, qui tient le système
constant d'une génération à l'autre. Chaque montant d'une année projetée est
celui de l'année d'avant relevé de la croissance de l'année et arrondi à
l'euro, comme une loi de finances l'écrirait. Les taux ne bougent pas ; le
seuil de mise en recouvrement non plus, que le code fixe en euros sans le
relever (61 € depuis 2001). Une année projetée porte la fiabilité ``estimee``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable

from .chargement import Fiabilite, charger_yaml

CHEMIN = Path("reference") / "legislation" / "impot_revenu.yaml"

#: Un franc vaut 1/6,55957 euro (règlement (CE) n° 2866/98 du Conseil).
FRANC = 6.55957

#: Les revenus de 2000 sont les derniers imposés en francs.
DERNIERE_ANNEE_EN_FRANCS = 2000

#: Les deux façons de projeter le barème au-delà de la dernière loi de finances.
INDEXATIONS = ("prix", "salaire_moyen")

#: Les clés des séries qui sont des montants, que la projection relève : tout
#: ce qui n'est ni un taux, ni un nombre de parts, ni le seuil de recouvrement.
MONTANTS = {
    "plafonds_quotient_familial": ("general", "parent_isole_premier_enfant",
                                   "vivant_seul_ayant_eu_un_enfant",
                                   "reduction_complementaire_invalide",
                                   "reduction_complementaire_veuf"),
    "decote": ("seuil_celibataire", "seuil_couple"),
    "deductions": ("frais_professionnels_minimum", "frais_professionnels_maximum",
                   "pensions_minimum", "pensions_maximum"),
    "abattement_age_invalidite": ("abattement_plein", "seuil_plein", "abattement_reduit",
                                  "seuil_reduit"),
}

#: Les séries qu'une année porte, dans l'ordre du fichier.
SERIES = ("bareme", "quotient_familial", "parts_par_rang_d_enfant",
          "plafonds_quotient_familial", "decote", "reduction_sous_condition_de_revenus",
          "recouvrement", "deductions", "abattement_age_invalidite",
          "abattement_exceptionnel_ages_invalides", "abattement_exceptionnel_personnes_seules",
          "majorations_exceptionnelles", "minorations_exceptionnelles",
          "reduction_exceptionnelle", "prime_pour_l_emploi")

#: Les clés qui ne sont pas des valeurs : elles disent d'où vient la marche.
CLES_DE_SOURCE = ("annee", "texte", "note", "origine")


def arrondi_a_l_euro(valeur: float) -> float:
    """L'euro le plus proche, la moitié comptée pour un, comme le code arrondit
    (CGI, art. 193 et 1657, 1) — et non au pair, comme ``round``."""
    return float(math.floor(round(valeur, 6) + 0.5))


def monnaie_de(annee: int) -> str:
    """La monnaie dans laquelle les revenus d'``annee`` sont imposés."""
    return "FRF" if annee <= DERNIERE_ANNEE_EN_FRANCS else "EUR"


@dataclass(frozen=True)
class ParametresImpot:
    """Les paramètres en vigueur pour les revenus d'une année, dans sa monnaie.

    Chaque série est le dictionnaire de la marche en vigueur, sans ses clés de
    source ; une série qui n'est pas en vigueur est un dictionnaire vide. Les
    sources de chaque marche sont dans :attr:`sources`."""

    annee: int
    monnaie: str
    #: Les seuils des tranches, par part, et leurs taux.
    seuils: tuple[float, ...]
    taux: tuple[float, ...]
    series: dict[str, dict]
    sources: dict[str, str]
    #: L'année de la dernière loi de finances lue, d'où vient une projection.
    derniere_annee_lue: int
    indexation: str | None = None
    fiabilite: Fiabilite = Fiabilite.HAUTE

    @property
    def projete(self) -> bool:
        return self.annee > self.derniere_annee_lue

    def __getitem__(self, serie: str) -> dict:
        return self.series[serie]

    def parts_d_enfant(self, rang: int) -> float:
        """La part du ``rang``-ième enfant à charge (le premier a le rang 1)."""
        parts = self.series["parts_par_rang_d_enfant"]["parts"]
        return float(parts[min(rang, len(parts)) - 1])


def _marche(marches: tuple[dict, ...], annee: int) -> dict:
    retenue: dict = {}
    for marche in marches:
        if marche["annee"] > annee:
            break
        retenue = marche
    return retenue


def _valeurs(marche: dict) -> dict:
    if marche.get("supprimee"):
        return {}
    return {cle: valeur for cle, valeur in marche.items() if cle not in CLES_DE_SOURCE}


@dataclass(frozen=True)
class BaremesImpotRevenu:
    """Toutes les marches de l'impôt sur le revenu, de 1960 à la dernière loi
    de finances lue."""

    series: dict[str, tuple[dict, ...]]
    lu_le: str
    premiere_annee: int

    @property
    def derniere_annee(self) -> int:
        """La dernière année de revenus dont la loi de finances est lue."""
        return max(m["annee"] for m in self.series["bareme"])

    def lus(self, annee: int) -> ParametresImpot:
        """Les paramètres d'une année lue : ``premiere_annee`` à
        :attr:`derniere_annee`."""
        if not self.premiere_annee <= annee <= self.derniere_annee:
            raise ValueError(f"aucun barème lu pour les revenus de {annee} "
                             f"({self.premiere_annee}–{self.derniere_annee})")
        series, sources = {}, {}
        for nom in SERIES:
            marche = _marche(self.series[nom], annee)
            series[nom] = _valeurs(marche)
            sources[nom] = str(marche.get("texte", ""))
        bareme = series.pop("bareme")
        monnaie = monnaie_de(annee)
        for nom, valeurs in series.items():
            if valeurs.get("monnaie", monnaie) != monnaie:
                raise ValueError(f"{nom} des revenus de {annee} en {valeurs['monnaie']}, "
                                 f"quand l'année est en {monnaie}")
        if bareme.get("monnaie") != monnaie:
            raise ValueError(f"le barème des revenus de {annee} n'est pas en {monnaie}")
        return ParametresImpot(
            annee=annee, monnaie=monnaie, seuils=tuple(float(s) for s in bareme["seuils"]),
            taux=tuple(float(t) for t in bareme["taux"]), series=series, sources=sources,
            derniere_annee_lue=self.derniere_annee)

    def parametres(self, annee: int, indexation: str = "prix",
                   croissance: Callable[[int], float] | None = None) -> ParametresImpot:
        """Les paramètres des revenus d'``annee``, lus ou projetés.

        Au-delà de :attr:`derniere_annee`, ``croissance(t)`` donne la
        croissance de l'année ``t`` — celle des prix pour l'indexation
        ``prix``, du salaire moyen nominal pour ``salaire_moyen`` — que
        :func:`croissance_macro` tire du scénario de projection du dépôt."""
        if annee <= self.derniere_annee:
            return self.lus(annee)
        if indexation not in INDEXATIONS:
            raise ValueError(f"indexation inconnue : {indexation!r} ({', '.join(INDEXATIONS)})")
        if croissance is None:
            raise ValueError(f"les revenus de {annee} se projettent : il faut la croissance "
                             f"des {'prix' if indexation == 'prix' else 'salaires'}")
        parametres = self.lus(self.derniere_annee)
        for suivante in range(self.derniere_annee + 1, annee + 1):
            parametres = _projeter(parametres, suivante, indexation,
                                   1.0 + float(croissance(suivante)))
        return parametres


def _projeter(precedents: ParametresImpot, annee: int, indexation: str,
              facteur: float) -> ParametresImpot:
    """L'année ``annee`` à partir de la précédente : chaque montant relevé de
    ``facteur`` et arrondi à l'euro, les taux inchangés."""
    def relever(valeur: float) -> float:
        return arrondi_a_l_euro(valeur * facteur)

    series = {nom: dict(valeurs) for nom, valeurs in precedents.series.items()}
    for nom, cles in MONTANTS.items():
        for cle in cles:
            if cle in series[nom]:
                series[nom][cle] = relever(series[nom][cle])
    sources = {nom: f"projeté sur {'les prix' if indexation == 'prix' else 'le salaire moyen'} "
                    f"depuis les revenus de {precedents.derniere_annee_lue}"
               for nom in precedents.sources}
    return ParametresImpot(
        annee=annee, monnaie="EUR",
        seuils=tuple(relever(s) for s in precedents.seuils), taux=precedents.taux,
        series=series, sources=sources, derniere_annee_lue=precedents.derniere_annee_lue,
        indexation=indexation, fiabilite=Fiabilite.ESTIMEE)


def croissance_macro(macro, indexation: str = "prix") -> Callable[[int], float]:
    """La croissance qui projette le barème : l'inflation du scénario de
    projection du dépôt, ou la croissance nominale de son salaire moyen
    (:class:`~retraite_notionnelle.donnees.macro.DonneesMacro`)."""
    if indexation == "prix":
        return macro.inflation
    if indexation == "salaire_moyen":
        return macro.salaire_moyen
    raise ValueError(f"indexation inconnue : {indexation!r} ({', '.join(INDEXATIONS)})")


@lru_cache(maxsize=4)
def _charger(chemin: str, signature: tuple) -> BaremesImpotRevenu:
    contenu = charger_yaml(Path(chemin))
    return BaremesImpotRevenu(
        series={nom: tuple(sorted(contenu["series"][nom], key=lambda m: m["annee"]))
                for nom in SERIES},
        lu_le=str(contenu.get("lu_le", "")),
        premiere_annee=int(contenu["premiere_annee"]),
    )


def charger_baremes_impot_revenu(racine_donnees: Path) -> BaremesImpotRevenu:
    """Les barèmes de l'impôt sur le revenu, gardés tant que le fichier ne change pas."""
    chemin = Path(racine_donnees) / CHEMIN
    etat = chemin.stat()
    return _charger(str(chemin), (etat.st_mtime_ns, etat.st_size))
