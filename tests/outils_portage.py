"""Les tests qui confrontent les deux moteurs : leur moitié Python, gardée.

Un tel test calcule les mêmes saisies en Python et en JavaScript, puis compare.
La moitié JavaScript se rejoue à chaque passage : c'est elle qu'il éprouve. La
moitié Python ne dépend que du modèle, du code du test et de ses arguments :
la mémoire des calculs la garde (``retraite_notionnelle.memoire``), sous
l'empreinte de ``src/``, ``data/`` et ``scripts/``, et sous une clé qui porte
le texte du fichier de test, que l'empreinte ne lit pas, et les arguments. Le
10 octobre 2026, elle coûtait une demi-minute à chaque passage, pour trois
tests (feuille de route, action 135).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Callable, TypeVar

from retraite_notionnelle import CHARGE_A, memoire

T = TypeVar("T")


def moitie_python(fonction: Callable[..., T], *arguments) -> T:
    """``fonction(*arguments)``, calculée une fois tant que ni le modèle, ni le
    fichier qui la définit, ni ses arguments ne bougent.

    Les arguments s'écrivent en entier dans la clé : des valeurs simples,
    jamais un objet qui s'écrit par son adresse. Un fichier de test retouché
    depuis le chargement du modèle se calcule sans mémoire : le code qui
    tourne n'est peut-être pas celui que son texte dirait.
    """
    fichier = Path(sys.modules[fonction.__module__].__file__)
    texte = fichier.read_bytes()
    if fichier.stat().st_mtime > CHARGE_A:
        return fonction(*arguments)
    cle = ("portage_python", fonction.__module__, fonction.__qualname__,
           hashlib.sha256(texte).hexdigest(), arguments)
    return memoire.memoriser(cle, lambda: fonction(*arguments))
