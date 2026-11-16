"""Le journal de l'échéancier (docs/architecture.md, § 7.4 et annexe C.8).

LE JOURNAL EST L'ÉTAT. On y ajoute, on n'efface jamais, et chaque entrée
porte deux dates : son INSCRIPTION — l'événement qui l'a écrite, et sa
date — et sa période d'EFFET, [début, fin). Une entrée contient un événement
traité, une liquidation, une composante — y compris celles des étapes qui ne
liquident rien, la revalorisation de « faire vivre » et l'ASPA de « foyer et
net » —, ou une décision figée.

Une composante a un identifiant stable, et l'entrée qui la révise la
REMPLACE : une composante et ses révisions forment une lignée, où la plus
récente l'emporte. Le journal se lit de deux façons, et de deux seulement :

* :meth:`Journal.etat_au` — l'état à une date : tout ce qui a été inscrit au
  plus tard ce jour-là ;
* :meth:`Journal.servi` — ce qui est servi pour une période : pour chaque
  lignée, la dernière entrée dont l'effet couvre la période.

Chaque entrée suit le contrat C.8 (``data/reference/contrats/entree_journal.yaml``).
Son jumeau est ``moteur/js/journal.js``.
"""

from __future__ import annotations

from .types_du_pont.journal import SCHEMA_DE_L_ENTREE, Entree, Journal  # noqa: F401  (types du pont, action 161)

#: La version du contrat C.8 que :meth:`Entree.donnees` suit.
SCHEMA_VERSION = SCHEMA_DE_L_ENTREE


