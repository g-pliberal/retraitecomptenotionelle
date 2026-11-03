"""Les tests qui confrontent les deux moteurs : leur moitié Python, gardée.

Un tel test calcule les mêmes saisies en Python et en JavaScript, puis compare.
La moitié JavaScript se rejoue à chaque passage : c'est elle qu'il éprouve. La
moitié Python ne dépend que du modèle, du code du test, de ses arguments et du
paquet du dépôt, sur lequel le pont gardé ouvert lui bâtit souvent ses
carrières : la mémoire des calculs la garde (``retraite_notionnelle.memoire``),
sous l'empreinte du modèle, et sous une clé qui porte les arguments,
l'empreinte du paquet et, le calcul étant écrit dans un test, son code. Le 10
octobre 2026, elle coûtait une demi-minute à chaque passage, pour trois tests ;
le paquet est entré dans sa clé le 3 novembre (feuille de route, action 135).
"""

from __future__ import annotations

import functools
from typing import Callable, TypeVar

from retraite_notionnelle import memoire
from retraite_notionnelle.config import RACINE_PROJET

T = TypeVar("T")

#: Le paquet du dépôt, sur lequel le pont gardé ouvert calcule
#: (``pont._ouvert``) : la fabrique le récrit, et l'empreinte de la mémoire ne
#: le lit pas.
PAQUET = RACINE_PROJET / "moteur" / "donnees.json"


def moitie_python(fonction: Callable[..., T], *arguments) -> T:
    """``fonction(*arguments)``, calculée une fois tant que ni le modèle, ni le
    paquet du dépôt, ni le code du test qui l'écrit, ni ses arguments ne
    bougent. Les arguments s'écrivent en entier dans la clé : des valeurs
    simples, jamais un objet qui s'écrit par son adresse."""
    return memoire.memoriser(
        ("portage_python", fonction.__module__, fonction.__qualname__, arguments),
        functools.partial(fonction, *arguments), fichiers_lus=(PAQUET,))
