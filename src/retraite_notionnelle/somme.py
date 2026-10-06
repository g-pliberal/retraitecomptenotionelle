"""La somme de gauche à droite, la même sous tous les Python.

Depuis Python 3.12, ``sum()`` additionne les flottants en somme compensée
(Neumaier) : le résultat diffère, au dernier chiffre, de celui de Python 3.11,
qui additionnait de gauche à droite. Les fichiers fabriqués (le paquet, les
témoins) en changeaient d'un Python à l'autre, et une session sous 3.13
voyait périmé ce que GitHub, sous 3.11, venait de fabriquer (action 148,
étape 1). :func:`somme_ordonnee` additionne toujours de gauche à droite, comme le
portage JavaScript ; ``tests/test_somme.py`` interdit ``sum()`` dans ``src/``
et ``scripts/``.
"""

from __future__ import annotations

from functools import reduce
from operator import add


def somme_ordonnee(termes, debut=0):
    """``sum(termes, debut)``, additionné de gauche à droite."""
    return reduce(add, termes, debut)
