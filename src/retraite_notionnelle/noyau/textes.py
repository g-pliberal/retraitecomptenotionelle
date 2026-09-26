"""La liste de contrôle des textes : chaque rédaction d'article, et son statut.

``docs/architecture.md``, § 6.6. La carte part des textes, pas de la mémoire :
les articles qui touchent les retraites sont listés depuis l'index LEGI du
dépôt, rédaction par rédaction, dans ``data/reference/textes/redactions.csv``
(``scripts/textes.py`` la tient ; le périmètre est déclaré dans
``perimetre.yaml``). Chaque rédaction reçoit un statut, qu'on ne lui écrit
pas : il se lit dans les fiches.

``rattachee``
    une version de fiche la cite parmi ses textes ;
``sans_effet``
    une fiche la déclare sans effet sur elle, avec le mot à mot qui le montre
    (``textes_sans_effet``) ;
``a_rattacher``
    une fiche la cite sans l'avoir encore coupée en version : dans
    ``textes_a_rattacher``, ou dans une lecture de ses sources ;
``a_examiner``
    une fiche la range parmi ses textes à relire, ou le script l'a inscrite,
    datée, en l'apportant de l'index après la pose de la liste.

Une fiche cite une rédaction par son identifiant (``id``), ou le nomme dans
une référence : ``LEGIARTI`` suivi de ses douze chiffres suffit. Le CLIQUET
compte les rédactions sans aucun statut. Il ne peut que décroître, et une loi
nouvelle ne le fait jamais monter : ses rédactions entrent « à examiner ».
"""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

from ..config import RACINE_DONNEES
from ..donnees.chargement import charger_yaml
from . import carte, vocabulaire

TEXTES = RACINE_DONNEES / "reference" / "textes"
COLONNES = ("id", "texte", "article", "debut", "fin", "inscrite_le")
LEGIARTI = re.compile(r"LEGIARTI\d{12}")

#: Du plus établi au moins établi : une rédaction que deux fiches citent
#: prend le statut le plus établi.
STATUTS = ("rattachee", "sans_effet", "a_rattacher", "a_examiner")


def perimetre(dossier: Path = TEXTES) -> dict:
    return charger_yaml(dossier / "perimetre.yaml")


def redactions(dossier: Path = TEXTES) -> list[dict]:
    """Les rédactions de la liste, telles que le CSV les porte."""
    with (dossier / "redactions.csv").open(encoding="utf-8", newline="") as flux:
        return list(csv.DictReader(flux))


def titres(dossier: Path = TEXTES) -> dict[str, str]:
    """Le titre de chaque texte de la liste, sous sa clé."""
    with (dossier / "textes.csv").open(encoding="utf-8", newline="") as flux:
        return {ligne["texte"]: ligne["titre"] for ligne in csv.DictReader(flux)}


def _identifiants(textes) -> set[str]:
    trouves: set[str] = set()
    for texte in textes or []:
        if isinstance(texte, dict):
            trouves |= set(LEGIARTI.findall(" ".join(str(v) for v in texte.values())))
        else:
            trouves |= set(LEGIARTI.findall(str(texte)))
    return trouves


def citations(fiches: dict[str, dict] | None = None) -> dict[str, dict[str, str]]:
    """Pour chaque rédaction qu'une fiche cite, le statut qu'elle en reçoit,
    fiche par fiche."""
    if fiches is None:
        fiches = carte.fiches()
    sortie: dict[str, dict[str, str]] = {}

    def noter(identifiants, statut, nom):
        for ident in identifiants:
            actuel = sortie.setdefault(ident, {}).get(nom)
            if actuel is None or STATUTS.index(statut) < STATUTS.index(actuel):
                sortie[ident][nom] = statut

    for nom, fiche in fiches.items():
        for version in fiche.get("versions") or []:
            if isinstance(version, dict):
                noter(_identifiants(version.get("textes")), "rattachee", nom)
        noter(_identifiants(fiche.get("textes_sans_effet")), "sans_effet", nom)
        noter(_identifiants(fiche.get("textes_a_rattacher")), "a_rattacher", nom)
        lectures = (fiche.get("sources") or {}).get("lectures") if isinstance(
            fiche.get("sources"), dict) else None
        noter(_identifiants(lectures), "a_rattacher", nom)
        noter(_identifiants(fiche.get("textes_a_relire")), "a_examiner", nom)
    return sortie


def statuts(dossier: Path = TEXTES, fiches: dict[str, dict] | None = None) -> dict[str, str | None]:
    """Le statut de chaque rédaction de la liste, ou ``None`` : le plus établi
    que les fiches lui donnent, sinon « à examiner » si le script l'a
    inscrite."""
    cite = citations(fiches)
    sortie = {}
    for redaction in redactions(dossier):
        donnes = cite.get(redaction["id"], {}).values()
        if donnes:
            sortie[redaction["id"]] = min(donnes, key=STATUTS.index)
        elif redaction["inscrite_le"]:
            sortie[redaction["id"]] = "a_examiner"
        else:
            sortie[redaction["id"]] = None
    return sortie


def sans_statut(dossier: Path = TEXTES, fiches: dict[str, dict] | None = None) -> list[str]:
    return [ident for ident, statut in statuts(dossier, fiches).items() if statut is None]


def controler(dossier: Path = TEXTES, fiches: dict[str, dict] | None = None) -> list[str]:
    """Ce qui ne va pas dans la liste : rien, si elle tient et si le cliquet
    est juste. Les statuts sont ceux du vocabulaire, liste fermée."""
    erreurs = []
    if set(STATUTS) != vocabulaire.liste("statuts_de_texte"):
        erreurs.append(f"les statuts {STATUTS} ne sont plus ceux du vocabulaire")
    with (dossier / "redactions.csv").open(encoding="utf-8", newline="") as flux:
        entete = next(csv.reader(flux), [])
    if tuple(entete) != COLONNES:
        return erreurs + [f"redactions.csv : les colonnes sont {COLONNES}, pas {tuple(entete)}"]
    lignes = redactions(dossier)
    connus = titres(dossier)
    vus: set[str] = set()
    for rang, ligne in enumerate(lignes, 2):
        ou = f"redactions.csv:{rang}"
        if not LEGIARTI.fullmatch(ligne["id"]):
            erreurs.append(f"{ou} : « {ligne['id']} » n'est pas un identifiant de rédaction")
        if ligne["id"] in vus:
            erreurs.append(f"{ou} : {ligne['id']} deux fois")
        vus.add(ligne["id"])
        if ligne["texte"] not in connus:
            erreurs.append(f"{ou} : texte « {ligne['texte']} » absent de textes.csv")
        for champ in ("debut", "fin", "inscrite_le"):
            if ligne[champ] and not _est_date(ligne[champ]):
                erreurs.append(f"{ou} : {champ} « {ligne[champ]} » n'est pas une date")
        if not ligne["debut"]:
            erreurs.append(f"{ou} : une rédaction a un début")
    reel = len(sans_statut(dossier, fiches))
    inscrit = (perimetre(dossier).get("cliquet") or {}).get("redactions_sans_statut")
    if inscrit is None:
        erreurs.append(f"perimetre.yaml : le cliquet n'est pas posé (redactions_sans_statut: {reel})")
    elif reel > inscrit:
        erreurs.append(f"{reel} rédactions sans statut, le cliquet en admet {inscrit} : une "
                       "rédaction nouvelle s'inscrit « à examiner » "
                       "(python scripts/textes.py --inscrire), et une fiche ne rend pas "
                       "le statut qu'elle donnait")
    elif reel < inscrit:
        erreurs.append(f"{reel} rédactions sans statut, et le cliquet en admet encore "
                       f"{inscrit} : l'abaisser à {reel} dans perimetre.yaml")
    return erreurs


def _est_date(texte: str) -> bool:
    try:
        date.fromisoformat(texte)
    except ValueError:
        return False
    return True
