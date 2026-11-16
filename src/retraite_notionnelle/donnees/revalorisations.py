"""Les revalorisations des pensions servies, date par date : celles de
l'article L. 161-23-1, que la Cnav publie depuis 1949, et celles des pensions
civiles et militaires de 2004 à 2008.

Un chargeur, que la fabrique du paquet lit sans importer le moteur Python
(action 161) ; la revalorisation servie et le scénario 1 le reprennent d'ici.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .chargement import Fiabilite


@dataclass(frozen=True)
class Revalorisation:
    """Une date d'effet de revalorisation, et son coefficient."""

    date_effet: date
    coefficient: float
    #: Les tranches de 2020 : bornes du montant total brut MENSUEL des
    #: retraites du mois précédent, la basse exclue, la haute incluse. ``None``
    #: pour toutes les autres lignes.
    superieur_a: float | None
    au_plus: float | None
    reference: str
    fiabilite: Fiabilite

    @property
    def par_tranche(self) -> bool:
        return self.superieur_a is not None or self.au_plus is not None

    def couvre(self, mensuel: float) -> bool:
        """La tranche s'applique-t-elle à ce montant total mensuel ?"""
        return ((self.superieur_a is None or mensuel > self.superieur_a)
                and (self.au_plus is None or mensuel <= self.au_plus))


def _reel_ou_rien(texte: str | None) -> float | None:
    return float(texte) if texte else None


def _charger(chemin: Path) -> tuple[Revalorisation, ...]:
    """Les lignes d'un fichier de revalorisations, de la plus ancienne à la plus récente."""
    if not chemin.exists():
        return ()
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in flux if not l.lstrip().startswith("#")]
    revalorisations = [
        Revalorisation(
            date_effet=date.fromisoformat(ligne["date_effet"]),
            coefficient=float(ligne["coefficient"]),
            superieur_a=_reel_ou_rien(ligne.get("mensuel_superieur_a")),
            au_plus=_reel_ou_rien(ligne.get("mensuel_au_plus")),
            reference=ligne["reference"],
            fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
        )
        for ligne in csv.DictReader(lignes)
    ]
    return tuple(sorted(revalorisations,
                        key=lambda r: (r.date_effet, r.superieur_a or 0.0)))


def produit(revalorisations) -> tuple[float, Fiabilite]:
    """Le coefficient cumulé d'une suite de revalorisations, et sa fiabilité."""
    coefficient = 1.0
    fiabilite = Fiabilite.CERTIFIEE
    for revalorisation in revalorisations:
        coefficient *= revalorisation.coefficient
        fiabilite = min(fiabilite, revalorisation.fiabilite)
    return coefficient, fiabilite


class RevalorisationsPensions:
    """Les coefficients qui ont revalorisé les pensions servies, date par date.

    Deux fichiers : celui de l'article L. 161-23-1, que la Cnav publie depuis
    1949, et celui des pensions civiles et militaires de 2004 à 2008, quand
    elles avaient leurs propres décrets.
    """

    def __init__(self, racine: Path) -> None:
        dossier = racine / "reference" / "legislation"
        self.generales = _charger(dossier / "revalorisation_pensions.csv")
        self.fonction_publique = _charger(
            dossier / "revalorisation_pensions_fonction_publique.csv")

    @staticmethod
    def retenues(lignes, depuis: date, jusqu_a: date, inclure_depuis: bool,
                 mensuel_2019: float | None) -> list[Revalorisation]:
        """Celles qu'a reçues une pension prenant effet à ``depuis``, jusqu'à
        ``jusqu_a`` inclus.

        ``inclure_depuis`` dit si une revalorisation tombant le jour même du
        départ s'applique — oui dans la fonction publique et les régimes
        spéciaux, non au régime général, dont les salaires portés au compte
        l'ont déjà reçue. Une tranche de 2020 n'est retenue que si le montant
        mensuel de décembre 2019 y tombe : c'est à l'appelant de le donner, et
        ne pas le faire quand la fenêtre couvre 2020 est une erreur.
        """
        choisies = []
        for ligne in lignes:
            effet = ligne.date_effet
            if effet > jusqu_a or effet < depuis or (effet == depuis and not inclure_depuis):
                continue
            if ligne.par_tranche:
                if mensuel_2019 is None:
                    raise ValueError(
                        f"la revalorisation du {effet} dépend du montant total "
                        "de la retraite du mois précédent, qui n'a pas été donné"
                    )
                if not ligne.couvre(mensuel_2019):
                    continue
            choisies.append(ligne)
        return choisies

    def generale(self, depuis: date, jusqu_a: date, inclure_depuis: bool,
                 mensuel_2019: float | None) -> tuple[float, Fiabilite]:
        """Le coefficient de l'article L. 161-23-1 entre deux dates."""
        return produit(self.retenues(self.generales, depuis, jusqu_a,
                                     inclure_depuis, mensuel_2019))
