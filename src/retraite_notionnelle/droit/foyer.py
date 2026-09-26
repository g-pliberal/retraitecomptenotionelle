"""Foyer et net (docs/architecture.md, § 7.4).

Ce que le droit sert en regardant toutes les ressources du bénéficiaire, et
non une pension : l'ASPA. Elle vient en DERNIER, et pour cause : elle est
différentielle. Elle complète tout le reste, majorations comprises, jusqu'au
montant du barème d'une personne seule — c'est la seule prestation du système
actuel qui ne suppose aucune cotisation, et donc celle qui creuse le plus
l'écart avec un compte notionnel. Elle s'ouvre à 65 ans, et se revoit à
chaque échéance : l'échéancier l'applique après les liquidations du jour, et
après « faire vivre ».

Les prélèvements selon le revenu du foyer n'y sont pas encore : le modèle
compare des pensions brutes.

Ce que l'étape écrit, :class:`Foyer`, suit son schéma,
``data/reference/etapes/foyer_et_net.yaml``. Son jumeau est
``moteur/js/droit/foyer.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..donnees.chargement import Fiabilite
from .commun import AvantageApplique

if TYPE_CHECKING:
    from ..scenarios.actuel import ScenarioActuel
    from .liquidation import Contexte

#: La version du schéma de l'étape que :meth:`Foyer.donnees` suit.
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Foyer:
    """Ce que l'étape « foyer et net » écrit, à une date."""

    personne: str
    #: La date à laquelle les ressources sont lues : l'effet de la
    #: liquidation, ou l'échéance (AAAA-MM-JJ).
    date: str | None
    #: Toutes les pensions que le bénéficiaire reçoit, régimes provisionnés
    #: et majorations compris.
    ressources: float
    #: L'ASPA : le complément jusqu'au barème, nul quand les ressources
    #: l'atteignent.
    minimum_vieillesse: float
    #: Le barème lu, quand l'allocation est ouverte.
    plafond: float | None
    fiabilite: Fiabilite

    def avantage(self) -> AvantageApplique:
        """L'ASPA, sous la forme où la cascade des avantages la dit."""
        return AvantageApplique(
            code="minimum_vieillesse",
            libelle="Minimum vieillesse (ASPA)",
            montant=self.minimum_vieillesse,
            detail="allocation différentielle, barème d'une personne seule",
        )

    def donnees(self) -> dict:
        """Le foyer, tel que le schéma de l'étape le décrit."""
        return {"schema_version": SCHEMA_VERSION, "personne": self.personne,
                "date": self.date, "ressources": self.ressources,
                "minimum_vieillesse": self.minimum_vieillesse,
                "fiabilite": self.fiabilite.name.lower()}


def foyer_et_net(moteur: ScenarioActuel, personne: str, date: str | None, annee: int,
                 ressources: float, age_atteint: bool,
                 contexte: Contexte | None = None) -> Foyer:
    """L'ASPA qu'appellent ``ressources`` en ``annee``.

    ``age_atteint`` dit si l'âge de l'allocation l'est : à la date d'effet
    pour une liquidation, dans l'année pour une échéance. Le contexte peut
    neutraliser les avantages non contributifs, et l'allocation avec eux ; le
    paramètre ``minimum_vieillesse_dans_le_scenario_actuel`` la retire aussi.
    """
    montant, plafond, fiabilite = 0.0, None, Fiabilite.CERTIFIEE
    if (age_atteint and moteur.parametres.minimum_vieillesse_dans_le_scenario_actuel
            and not (contexte is not None
                     and contexte.neutralise("avantages_non_contributifs"))):
        bareme = moteur.minimum_vieillesse.plafond(annee)
        if bareme is not None:
            plafond = bareme[0]
            montant = max(0.0, bareme[0] - ressources)
            if montant > 0:
                fiabilite = bareme[1]
    return Foyer(personne=personne, date=date, ressources=ressources,
                 minimum_vieillesse=montant, plafond=plafond, fiabilite=fiabilite)
