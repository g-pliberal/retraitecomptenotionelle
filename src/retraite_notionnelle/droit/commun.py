"""Ce que les étapes du droit partagent avec la liquidation.

Son jumeau est ``moteur/js/droit/commun.js``.
"""

from __future__ import annotations


def derniere_annee(regime) -> int:
    """Dernière année pour laquelle le régime a des paramètres."""
    annees = [p.fin if p.fin is not None else 9999 for p in regime.periodes]
    return min(max(annees), 2100) if annees else 2100
