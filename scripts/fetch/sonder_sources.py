"""Sonde les adresses de ``data/sources_a_explorer.yaml`` — et regarde ce qu'elles SERVENT.

Le premier sondage, le 22 septembre 2026, rangeait une adresse en ``session``
dès qu'elle répondait 200. Le même jour, ``www.enim.eu`` a montré ce que ce
critère laisse passer : un 200 qui porte une page de 212 octets, le script d'un
pare-feu anti-robots, et rien du contenu. Un code de réponse ne dit pas qu'on a
lu la page.

Ce script refait la requête et juge le CORPS : texte visible, et marques des
pages de défi (Incapsula, Cloudflare, « Just a moment », « Attention
Required », pages qui n'ont qu'un script). Il n'écrit rien : il imprime, pour
chaque adresse, le code, la taille et le verdict, puis la liste de celles dont
l'``acces`` déclaré ne correspond plus à ce qu'on a mesuré.

Un appel par seconde, une adresse à la fois : ce sont des serveurs publics.

    python scripts/fetch/sonder_sources.py                 # tout l'inventaire
    python scripts/fetch/sonder_sources.py --statut a_explorer
    python scripts/fetch/sonder_sources.py --id enim_reversion
"""

from __future__ import annotations

import argparse
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[2]
INVENTAIRE = RACINE / "data" / "sources_a_explorer.yaml"

#: Marques des pages de défi. Chacune a été vue, ou est la signature publique
#: du service qui la sert ; une page qui en porte une n'est pas la page visée.
MARQUES_DEFI = (
    "_Incapsula_Resource",
    "Incapsula incident",
    "cf-chl-",
    "challenge-platform",
    "Just a moment...",
    "Attention Required! | Cloudflare",
    "cf-browser-verification",
    "Please enable JavaScript and cookies",
    "Request unsuccessful. Incapsula",
    "DDoS protection by",
)

#: Texte visible en deçà duquel une page qui porte une marque de défi n'est
#: que le défi. Les pages de défi vues en ont moins de cent caractères.
TEXTE_MINIMAL_DEFI = 2000


def _texte_visible(corps: bytes) -> bytes:
    """Le corps sans scripts, styles, balises ni blancs."""
    return re.sub(rb"<(script|style)\b.*?</\1>|<[^>]+>|\s+", b"", corps,
                  flags=re.S | re.I)


def verdict(code: int | None, corps: bytes, type_contenu: str) -> str:
    """``session`` si la page est lue, ``navigateur`` si c'est un défi,
    ``refus`` sinon — et ``erreur`` quand rien n'est revenu.

    Une marque ne suffit pas : Incapsula glisse son script dans les VRAIES
    pages qu'il protège aussi — celles de la fonction publique en portent un
    au milieu de cinquante kilo-octets de contenu. Une page de défi, elle, n'a
    presque pas de texte. C'est le texte visible qui tranche.
    """
    if code is None:
        return "erreur"
    marque = any(m.encode() in corps for m in MARQUES_DEFI)
    visible = len(_texte_visible(corps)) if "html" in type_contenu else None
    if marque and (visible is None or visible < TEXTE_MINIMAL_DEFI):
        return "navigateur"
    if code >= 400:
        return "refus"
    if visible is not None and visible < 200:
        return "navigateur"
    return "session"


def sonder(url: str) -> tuple[int | None, bytes, str]:
    # Une adresse accentuée se remet en octets avant la requête : urllib
    # refuse tout caractère hors ASCII dans le chemin.
    url = urllib.parse.quote(url, safe=":/?&=#%@+,;~")
    requete = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) retraitecomptenotionelle/sondage",
        "Accept": "text/html,application/pdf,*/*",
    })
    contexte = ssl.create_default_context()
    try:
        with urllib.request.urlopen(requete, timeout=30, context=contexte) as reponse:
            return (reponse.status, reponse.read(400_000),
                    reponse.headers.get("Content-Type", ""))
    except urllib.error.HTTPError as erreur:
        return erreur.code, erreur.read(50_000), erreur.headers.get("Content-Type", "")
    except Exception as erreur:  # noqa: BLE001 — on consigne, on ne s'arrête pas
        return None, str(erreur).encode(), ""


def main() -> int:
    arguments = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    arguments.add_argument("--statut", help="ne sonder que ce statut")
    arguments.add_argument("--id", action="append", help="ne sonder que cette ligne")
    arguments.add_argument("--pause", type=float, default=1.0)
    options = arguments.parse_args()

    sources = yaml.safe_load(INVENTAIRE.read_text(encoding="utf-8"))["sources"]
    if options.statut:
        sources = [s for s in sources if s["statut"] == options.statut]
    if options.id:
        sources = [s for s in sources if s["id"] in options.id]

    ecarts = []
    for source in sources:
        code, corps, type_contenu = sonder(source["url"])
        mesure = verdict(code, corps, type_contenu)
        print(f"{code or '---'}\t{len(corps):>7}\t{mesure:<10}\t{source['acces']:<17}\t{source['id']}",
              flush=True)
        # `chaine_incomplete`, `git` et `ferme` sont des diagnostics plus fins
        # qu'une requête ne les refait : on ne les conteste que sur un défi.
        declare = source["acces"]
        if declare == "session" and mesure != "session":
            ecarts.append((source["id"], declare, mesure, code, len(corps)))
        time.sleep(options.pause)

    if ecarts:
        print("\nAccès déclaré démenti par la mesure :")
        for ident, declare, mesure, code, taille in ecarts:
            print(f"  {ident} : déclaré {declare}, mesuré {mesure} ({code}, {taille} octets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
