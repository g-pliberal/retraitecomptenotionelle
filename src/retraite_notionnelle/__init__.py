"""Modélisation d'un système de retraite français en comptes notionnels.

Le paquet fournit :

* un socle de données historiques traçables (``data/``) : séries macro-
  économiques, mortalité, catalogue des régimes de 1930 à aujourd'hui ;
* un moteur de comptes notionnels (``moteur/``) : accumulation, indexation
  « triple lock inversé », coefficients de conversion actuariels, écart à
  l'âge de référence à cliquet, neutralisation des droits non contributifs ;
* six scénarios comparables (``scenarios/``) : système actuel, comptes
  notionnels rétroactifs et prospectifs, les deux mêmes en y portant la
  contribution que l'employeur public verse réellement, puis la proposition
  libérale — le compte rétroactif à 18 % pour tous, avec une garantie
  vieillesse individualisée financée par l'impôt ;
* un simulateur individuel et des cas types (``simulateur``, ``castypes``).

Toute grandeur produite par le paquet est accompagnée du niveau de fiabilité
des données qui l'ont produite : voir :class:`~retraite_notionnelle.donnees.chargement.Fiabilite`.
"""

from .config import Parametres, ModeIndexation, SourceCotisations

__all__ = ["Parametres", "ModeIndexation", "SourceCotisations", "__version__"]

__version__ = "0.1.0"
