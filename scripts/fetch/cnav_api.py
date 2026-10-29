#!/usr/bin/env python3
"""L'API de la base de législation de la Cnav : son adresse, l'en-tête des
requêtes, la lecture d'une réponse déjà téléchargée.

    import cnav_api                      # depuis scripts/fetch/, comme source_locale
    cnav_api.contenus(["aspa_montant_bar"])                   # par le réseau
    cnav_api.contenus(["aspa_montant_bar"], fichier=chemin)   # d'une réponse téléchargée

POURQUOI IL EXISTE (action 175, étape 1). Onze récupérateurs lisent la base,
et chacun redéfinissait l'adresse de l'API, l'en-tête de ses requêtes et la
lecture d'une réponse téléchargée — en trois variantes : avec ou sans la marque
d'ordre des octets que le site sert parfois, la liste entière des barèmes ou un
seul. Ils passent par ce module, comme le récupérateur de la base entière,
``cnav_legislation.py``, qui tient le registre de ce que la base sert.

LA BASE. ``legislation.lassuranceretraite.fr`` est une application Angular,
servie par une API publique et sans clé, sous ``/api/v1``. Trois routes y
rendent chacune une collection entière d'un appel — ``/baremes``, ``/expose``,
``/liste`` — ; ``/baremes/baremesByFileLeafRef/<nom>.aspx`` rend un barème,
``/reference/referencesByFileLeafRef/<nom>`` une référence, circulaire, lettre
ou texte, et les PDF sont sous ``/Pdf/``.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

SITE = "https://legislation.lassuranceretraite.fr"
API = SITE + "/api/v1"
#: Les circulaires et les lettres que la base sert en PDF.
PDF = SITE + "/Pdf/"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
#: L'aide de l'option ``--fichier`` des récupérateurs qui l'offrent.
AIDE_FICHIER = ("réponse JSON de l'API des barèmes déjà téléchargée — la liste "
                "entière de /baremes, ou un seul barème —, lue au lieu du réseau")


def _aspx(nom: str) -> str:
    return nom if nom.endswith(".aspx") else f"{nom}.aspx"


def adresse_bareme(nom: str) -> str:
    """L'adresse d'un barème, nommé avec ou sans ``.aspx``."""
    return f"{API}/baremes/baremesByFileLeafRef/{_aspx(nom)}"


def telecharger(adresse: str, delai: int = 60) -> bytes:
    requete = urllib.request.Request(adresse, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=delai) as reponse:
        return reponse.read()


def lire_json(octets: bytes):
    """Une réponse de l'API : du JSON en UTF-8, que précède parfois une
    marque d'ordre des octets."""
    return json.loads(octets.decode("utf-8-sig"))


def obtenir(route: str, delai: int = 60):
    """La réponse JSON d'une route de l'API : ``/baremes``, ``/menu/menuBareme``."""
    return lire_json(telecharger(API + route, delai))


def bareme(nom: str) -> dict:
    """La fiche d'un barème, demandée à l'API : son contenu, son titre, sa
    date de modification."""
    reponse = lire_json(telecharger(adresse_bareme(nom)))
    return reponse[0] if isinstance(reponse, list) else reponse


def lire_reponse(fichier: Path) -> dict[str, dict]:
    """Les fiches d'une réponse déjà téléchargée, par leur nom avec ``.aspx`` :
    la liste entière de ``/baremes``, ou la réponse d'un seul barème."""
    reponse = lire_json(Path(fichier).read_bytes())
    return {fiche["fileLeafRef"]: fiche
            for fiche in (reponse if isinstance(reponse, list) else [reponse])}


def baremes(noms, fichier: Path | None = None) -> dict[str, dict]:
    """La fiche de chaque barème nommé, sous le nom donné : lue dans
    ``fichier`` s'il y en a un, sinon demandée à l'API."""
    if fichier is None:
        return {nom: bareme(nom) for nom in noms}
    lues = lire_reponse(fichier)
    manquants = [nom for nom in noms if _aspx(nom) not in lues]
    if manquants:
        raise KeyError(f"{fichier} ne porte pas {', '.join(manquants)}")
    return {nom: lues[_aspx(nom)] for nom in noms}


def contenus(noms, fichier: Path | None = None) -> dict[str, str]:
    """Le contenu HTML de chaque barème nommé, comme :func:`baremes`."""
    return {nom: fiche["contenu"] for nom, fiche in baremes(noms, fichier).items()}
