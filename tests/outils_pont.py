"""Les saisies des tests, lues par le portage : la saisie n'aura qu'un
exemplaire, le JavaScript (action 161, étape 6).

Un test qui éprouve une règle du moteur par une saisie en demande la carrière
au pont (:func:`retraite_notionnelle.pont.carrieres_des_saisies`) : le portage
lit la requête comme le site, en bâtit la carrière et les paramètres, et le
moteur Python la simule, qui garde son jumeau. C'est le chemin des témoins
(``scripts/construire_temoins.py``), sur le même paquet, celui du dépôt : une
donnée retouchée n'y entre qu'à la fabrique suivante
(``python scripts/regenerer.py``). Un test qui éprouve la saisie elle-même —
un refus, une date, l'adresse qu'elle écrit — la lit dans le portage, par
``site()`` (:func:`saisie_du_portage`).

    saisies = Saisies()
    comparaison = saisies.simuler({"naissance": "1965-03-15", "liquidation": "2029-04"})
    carriere = saisies.carriere(requete)
    simulateur = saisies.simulateur(requete)

Ce module n'est pas un fichier de tests, et pytest ne le collecte pas.
"""

from __future__ import annotations

import functools

from retraite_notionnelle import pont
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Comparaison, Simulateur
from retraite_notionnelle.web.site import module, site


class RefusDuPortage(Exception):
    """Le portage refuse la requête : sa saisie, ou le modèle quand il en
    bâtit la carrière. Le message est son motif, tel que le site l'écrit."""


def _chaines(requete: dict) -> dict[str, str]:
    """Une requête d'adresse ne porte que des chaînes, comme
    ``URLSearchParams`` ; une valeur absente n'y est pas."""
    return {str(cle): str(valeur) for cle, valeur in requete.items() if valeur is not None}


class Saisies:
    """Ce que le contexte du site fait d'une requête, la carrière bâtie par le
    portage, et un simulateur Python par jeu de paramètres, comme lui."""

    def __init__(self) -> None:
        self._simulateurs: dict[Parametres, Simulateur] = {}

    def lire(self, requete: dict, prolonger: bool = True):
        """Les paramètres de la saisie, et la carrière que le site simulerait ;
        ``prolonger=False`` s'en tient aux années d'un relevé."""
        cas = {"cle": "saisie", "requete": _chaines(requete)}
        if not prolonger:
            cas["prolonger"] = False
        lus, refus = pont.carrieres_des_saisies([cas])
        if refus:
            raise RefusDuPortage(refus["saisie"])
        return lus["saisie"]

    def parametres(self, requete: dict) -> Parametres:
        return self.lire(requete)[0]

    def carriere(self, requete: dict, prolonger: bool = True):
        return self.lire(requete, prolonger)[1]

    def simulateur(self, de: dict | Parametres | None = None) -> Simulateur:
        """Le simulateur des paramètres d'une requête, de ``de`` lui-même, ou
        des réglages de référence."""
        parametres = (Parametres() if de is None
                      else self.parametres(de) if isinstance(de, dict) else de)
        if parametres not in self._simulateurs:
            self._simulateurs[parametres] = Simulateur(parametres)
        return self._simulateurs[parametres]

    def simuler(self, requete: dict) -> Comparaison:
        """Les quatre systèmes sur la carrière de la saisie : pour une saisie
        par la pension, celle que le portage trouve en l'inversant, sans le
        niveau trouvé (``niveau_inverse``)."""
        parametres, carriere = self.lire(requete)
        return self.simulateur(parametres).simuler(carriere)


@functools.cache
def _presomptions():
    """Les présomptions du paquet que le site a lu, lues une fois : le paquet
    entier passe le fil pour qu'on les y prenne."""
    return site().contexte.paquet.presomptions


def saisie_du_portage(requete: dict):
    """La saisie du portage, lue d'une requête comme le site la lit, sur les
    présomptions du paquet : un objet du portage, dont les champs se lisent
    et les méthodes s'appellent depuis le Python (``site.py``) ; un refus
    lève ``ErreurSite``, avec son motif."""
    return module("saisie").Saisie.depuis_requete(_chaines(requete), False, _presomptions())
