"""Les tests qui confrontent les deux moteurs : leur moitié Python, gardée.

Un tel test calcule les mêmes saisies en Python et en JavaScript, puis compare.
La moitié JavaScript se rejoue à chaque passage : c'est elle qu'il éprouve. La
moitié Python ne dépend que du modèle, du code du test et de ses arguments :
la mémoire des calculs la garde (``retraite_notionnelle.memoire``), sous
l'empreinte du modèle, et sous une clé qui porte les arguments et, le calcul
étant écrit dans un test, son code. Le 10 octobre 2026, elle coûtait une
demi-minute à chaque passage, pour trois tests (feuille de route, action 135).
"""

from __future__ import annotations

import functools
from typing import Callable, TypeVar

from retraite_notionnelle import memoire

T = TypeVar("T")


def moitie_python(fonction: Callable[..., T], *arguments) -> T:
    """``fonction(*arguments)``, calculée une fois tant que ni le modèle, ni le
    code du test qui l'écrit, ni ses arguments ne bougent. Les arguments
    s'écrivent en entier dans la clé : des valeurs simples, jamais un objet qui
    s'écrit par son adresse."""
    return memoire.memoriser(
        ("portage_python", fonction.__module__, fonction.__qualname__, arguments),
        functools.partial(fonction, *arguments))
