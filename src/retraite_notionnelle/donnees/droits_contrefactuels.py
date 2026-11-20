"""Les droits contrefactuels du scénario 1, en piles de couches.

Note de décision 0009, « Un scénario qui garde une loi passée est une
couche », et son second rectificatif : « une couche garde une réforme, non
une fiche ». Chaque couche (``data/reference/couches/``) écarte une réforme
(``ecarte``) depuis sa date d'effet (``depuis``) : dans chaque fiche que la
réforme a réécrite, elle garde la version d'avant — « remplacer une version »
(``docs/architecture.md``, § 4.8, annexe C.4). Une fiche qui déclare la
réforme (champ ``reformes``) sans que la couche en garde la version d'avant
s'y déclare hors de la couche (``garder``), avec sa raison.

La pile se résout ici, à la fabrication : le paquet porte, sous chaque droit,
les fiches résolues, que le portage lit à la place de celles du droit en
vigueur (``FichesDatees.sousLeDroit``, ``moteur/js/regimes.js``). À cette
étape, seule la fiche de l'âge légal est gardée dans sa version d'avant ; la
durée requise et la carrière longue gardent leur mécanisme jusqu'à l'étape 3
(``ScenarioActuel._sousLeDroit``, ``moteur/js/scenario-actuel.js``).
"""

from __future__ import annotations

import copy
from datetime import date
from pathlib import Path

from ..config import RACINE_DONNEES
from ..noyau import carte, univers

#: Chaque droit contrefactuel, et sa pile, de bas en haut, sur le droit réel.
#: Le droit au 31 août 2023 écarte la suspension, puis la loi de 2023.
DROITS = {
    "loi_2023_sans_suspension": ("sans_la_suspension_de_2026",),
    "au_31_aout_2023": ("sans_la_suspension_de_2026", "sans_la_reforme_de_2023"),
}

GARDER_LA_VERSION = "remplacer_une_version"
HORS_DE_LA_COUCHE = "garder"


def fiches_sans_decision(couche: dict, racine: Path = RACINE_DONNEES) -> list[str]:
    """Les fiches de la carte qui déclarent une réforme que la couche écarte,
    et qu'elle ne garde pas dans leur version d'avant ni ne déclare hors
    d'elle."""
    fiches = carte.fiches(racine / "reference" / "regles")
    ecartees = set(couche.get("ecarte") or ())
    decidees = {o.get("vise") for o in couche.get("operations") or ()
                if o.get("operation") in (GARDER_LA_VERSION, HORS_DE_LA_COUCHE)}
    return sorted(nom for nom, fiche in fiches.items()
                  if ecartees & set(fiche.get("reformes") or ()) and nom not in decidees)


def garder_la_version_d_avant(fiche: dict, depuis: date) -> dict:
    """La fiche préparée pour le moteur, la réforme du ``depuis`` écartée : la
    version qui valait la veille vaut sans fin, celles qui commencent ce
    jour-là ou après sont ôtées. La fiche reçue n'est pas touchée. Sans
    version qui commence ce jour-là, la réforme n'a pas réécrit la fiche, et
    le calcul s'arrête : la couche se trompe de fiche ou de date."""
    jour = depuis.isoformat()
    dates = fiche.get("dates_qui_decident") or ()
    if len(dates) != 1:
        raise ValueError(f"{fiche['id']} : une couche ne garde la version d'avant que d'une "
                         "fiche qu'une seule date décide")
    cle = dates[0]
    versions = copy.deepcopy(fiche["versions"])
    if any(v.get("exception_de") for v in versions):
        raise ValueError(f"{fiche['id']} : une couche ne garde pas encore la version d'avant "
                         "d'une fiche qui porte des exceptions")
    if not any(v["bornes"][cle][0] == jour for v in versions):
        raise ValueError(f"{fiche['id']} : aucune version ne commence le {jour}, "
                         "la réforme écartée ne l'a pas réécrite")
    gardees = [v for v in versions if v["bornes"][cle][0] is None or v["bornes"][cle][0] < jour]
    for version in gardees:
        if version["bornes"][cle][1] == jour:
            version["bornes"][cle][1] = None
    return {**copy.deepcopy({k: v for k, v in fiche.items() if k != "versions"}),
            "versions": gardees}


def fiches_resolues(pile: tuple[str, ...], fiches: dict[str, dict],
                    racine: Path = RACINE_DONNEES) -> dict[str, dict]:
    """Les fiches préparées que la pile change, résolues couche après couche,
    de bas en haut : chacune agit sur le résultat de celles d'en dessous. Les
    couches et la carte se lisent sous ``racine``, comme les fiches."""
    couches = univers.couches(racine / "reference" / "couches")
    resolues: dict[str, dict] = {}
    for nom in pile:
        couche = couches[nom]
        manquent = fiches_sans_decision(couche, racine)
        if manquent:
            raise ValueError(f"couche {nom} : fiches qui déclarent une réforme écartée, ni "
                             f"gardées ni déclarées hors de la couche : {', '.join(manquent)}")
        depuis = couche["depuis"]["valeur"]
        for operation in couche["operations"]:
            if operation["operation"] != GARDER_LA_VERSION:
                continue
            vise = operation["vise"]
            if vise not in fiches:
                raise ValueError(f"couche {nom} : le moteur ne lit pas {vise} par ses versions "
                                 "(FichesDatees.NOMS)")
            resolues[vise] = garder_la_version_d_avant(resolues.get(vise, fiches[vise]), depuis)
    return resolues


def pour_le_paquet(fiches: dict[str, dict], racine: Path = RACINE_DONNEES) -> dict[str, dict]:
    """Ce que le paquet porte de chaque droit contrefactuel
    (``droits_contrefactuels``) : sa pile, et les fiches résolues que le
    portage lit sous lui."""
    return {droit: {"couches": list(pile), "fiches": fiches_resolues(pile, fiches, racine)}
            for droit, pile in DROITS.items()}
