"""Ce que les étapes du droit partagent avec la liquidation.

La dernière année d'un régime, que l'acquisition et la liquidation lisent ;
la date d'effet d'une demande ;
la pension d'un régime, que « liquider chaque régime » écrit et que
« compléter tous régimes » relève ; l'avantage non contributif, que la
cascade des avantages mesure et que les deux étapes qui complètent
appliquent.

Son jumeau est ``moteur/js/droit/commun.js``.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..donnees.chargement import Fiabilite


def derniere_annee(regime) -> int:
    """Dernière année pour laquelle le régime a des paramètres."""
    annees = [p.fin if p.fin is not None else 9999 for p in regime.periodes]
    return min(max(annees), 2100) if annees else 2100


def date_d_effet(carriere) -> str | None:
    """La date d'effet d'une demande (AAAA-MM-JJ) : le premier jour du mois de
    la liquidation, ou ``None`` pour une carrière sans départ."""
    if carriere.age_liquidation is None:
        return None
    date = carriere.date_liquidation
    return f"{date.annee:04d}-{date.mois:02d}-01"


@dataclass(frozen=True)
class PensionRegime:
    """Pension annuelle brute servie par un régime."""

    regime: str
    montant: float
    type_calcul: str
    detail: str
    fiabilite: Fiabilite


@dataclass(frozen=True)
class AvantageApplique:
    """Effet en euros d'un avantage non contributif du droit positif.

    Les trois avantages s'appliquent dans cet ordre, et l'ordre compte : la
    MDA ajoute des trimestres, donc modifie la décote et la proratisation AVANT
    que la majoration ne multiplie, et le minimum ne comble qu'ensuite. Leurs
    effets s'additionnent exactement au total : c'est ce qui rend la cascade
    vérifiable ligne à ligne.
    """

    code: str
    libelle: str
    montant: float
    detail: str = ""
    #: Part de chaque régime, dans l'ordre des pensions, quand l'avantage se
    #: répartit entre eux — la majoration pour enfants, plafond compris.
    par_regime: tuple[tuple[str, float], ...] = ()
