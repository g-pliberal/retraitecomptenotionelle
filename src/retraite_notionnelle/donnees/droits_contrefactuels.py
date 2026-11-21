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
vigueur (``FichesDatees.sousLeDroit``, ``moteur/js/regimes.js``). Les fiches
de l'âge légal et de l'âge du taux plein sont gardées dans leur version
d'avant, et les renvois de l'une à l'autre se contrôlent sur les fiches que la
pile laisse (:func:`controler_les_renvois`) ; la durée requise et la carrière
longue gardent leur mécanisme jusqu'aux sessions suivantes de l'étape 3
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
    erreurs = controler_les_renvois({**fiches, **resolues})
    if erreurs:
        raise ValueError(f"pile {' + '.join(pile)} : " + " ; ".join(erreurs))
    return resolues


def _porte(fiche: dict, version: dict, valeur: str, vues: frozenset = frozenset()) -> bool:
    """La version préparée porte-t-elle la valeur qu'un renvoi nomme : un de
    ses paramètres, l'âge de sa table, ou ce que porte sa rédaction
    antérieure ? Voir ``renvois.porte``, sur les fiches de la carte."""
    if valeur in (version.get("parametres") or {}):
        return True
    if valeur == "age" and version.get("table"):
        return True
    anterieure = version.get("redaction_anterieure")
    if anterieure and version["id"] not in vues:
        cible = next((v for v in fiche["versions"] if v["id"] == anterieure["version"]), None)
        return cible is not None and _porte(fiche, cible, valeur, vues | {version["id"]})
    return False


def _se_croisent(une: list, autre: list) -> bool:
    (a, b), (c, d) = une, autre
    return (b is None or c is None or c < b) and (d is None or a is None or a < d)


def controler_les_renvois(fiches: dict[str, dict]) -> list[str]:
    """Ce qui ne tient pas dans les renvois datés des fiches préparées, telles
    qu'une pile de couches les laisse : chaque version de la fiche lue qui vaut
    pendant la version qui lit doit porter la valeur nommée. C'est le second
    piège de l'étape 3 de la note 0009 : une couche qui garde la version de
    2011 de l'âge légal, mais non celle de l'âge du taux plein, laisserait la
    version de 2023 chercher l'âge du premier alinéa là où il n'est pas.
    ``noyau/renvois.py`` contrôle de même les fiches de la carte."""
    erreurs = []
    for nom, fiche in fiches.items():
        for version in fiche.get("versions") or []:
            for renvoi in version.get("renvois") or []:
                lue = fiches.get(renvoi["fiche"])
                ici = f"{nom}.{version['id']}"
                if lue is None:
                    erreurs.append(f"{ici} : renvoie à « {renvoi['fiche']} », que le paquet "
                                   "ne porte pas")
                    continue
                etendue = version["bornes"].get(renvoi["date"]) or [None, None]
                for autre in lue["versions"]:
                    if (_se_croisent(etendue, autre["bornes"].get(renvoi["date"]) or [None, None])
                            and not _porte(lue, autre, renvoi["valeur"])):
                        erreurs.append(f"{ici} : lit « {renvoi['valeur']} », que "
                                       f"{renvoi['fiche']}.{autre['id']} ne porte pas")
    return erreurs


def pour_le_paquet(fiches: dict[str, dict], racine: Path = RACINE_DONNEES) -> dict[str, dict]:
    """Ce que le paquet porte de chaque droit contrefactuel
    (``droits_contrefactuels``) : sa pile, et les fiches résolues que le
    portage lit sous lui."""
    return {droit: {"couches": list(pile), "fiches": fiches_resolues(pile, fiches, racine)}
            for droit, pile in DROITS.items()}
