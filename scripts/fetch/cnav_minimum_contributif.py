#!/usr/bin/env python3
"""Minimum contributif, minimum majoré et plafond d'écrêtement, par la Cnav.

    python scripts/fetch/cnav_minimum_contributif.py
    python scripts/fetch/cnav_minimum_contributif.py --fichier baremes.json

À QUOI IL SERT. Le code de la sécurité sociale ne porte que quelques ANCRES du
minimum contributif — 26 400 F au 1er avril 1983 (R. 351-25), puis les montants
de 2004, 2006, 2008 et septembre 2023 (D. 351-2-1) — et laisse la loi les
revaloriser : comme les pensions jusqu'en 2023 (L. 161-23-1), au 1er janvier
selon le SMIC depuis (L. 351-10, dernier alinéa). Le dépôt reliait ces ancres
par les PRIX : le majoré de 2004 sortait 7,9 % trop haut, celui de 2019 4,7 %,
et la marche de 2008 (décret n° 2007-1899) glissait jusqu'en 2007. Ce
récupérateur lit ce que la caisse a réellement appliqué, date par date.

LA SOURCE. Deux barèmes de la base de législation de la Cnav, par la même API
publique que ``cnav_revalorisation_pensions.py`` :

* « Montant minimum de la retraite personnelle »
  (``retraite_personnelle_montant_minimum_bar``) : chaque date de
  revalorisation depuis le 1er avril 1983, le minimum annuel et mensuel, le
  majoré depuis 2004, et le texte qui fixe chacun — décret, arrêté, puis
  circulaire de la caisse ;
* « Plafond de retraites personnelles pour l'attribution du minimum »
  (``retraite_personnelle_minimum_plafond_retraite_bar``) : le plafond
  mensuel de l'écrêtement de L. 173-2, depuis le 1er janvier 2012, à chaque
  relèvement du SMIC.

Le script les écrit en euros PAR AN, unité du dépôt : les francs d'avant 2002
sont convertis à 6,55957, le plafond mensuel multiplié par douze. Il refuse
d'écrire si les ancres du code (``REPERES``) ne se retrouvent pas au centime,
si une date apparaît deux fois, si un montant baisse, ou si le majoré n'excède
pas le minimum.

Statut de fiabilité : ``haute``, jamais ``certifiee`` : la caisse transcrit ce
que le décret ou sa propre circulaire ont fixé. Les ancres du code, elles,
sont certifiées par ``dila_legi_minimum_contributif.py`` ; ce barème ne fait
que combler les dates qu'elles ne couvrent pas (``scripts/verifier_donnees.py``).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
API = ("https://legislation.lassuranceretraite.fr/api/v1/baremes/"
       "baremesByFileLeafRef/{}.aspx")
MINIMUM = "retraite_personnelle_montant_minimum_bar"
PLAFOND = "retraite_personnelle_minimum_plafond_retraite_bar"
SORTIE = RACINE / "data" / "brut" / "cnav_minimum_contributif.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Le taux de conversion du franc en euro, fixé le 31 décembre 1998.
FRANCS_PAR_EURO = 6.55957

#: Les ancres du code, que le barème doit redonner au centime : R. 351-25
#: (LEGIARTI000006749365) pour 1983, D. 351-2-1 pour les suivantes
#: (LEGIARTI000006736531, 006736532, 017870194, 047961314), D. 173-21-0-0-1
#: pour le plafond de 2014 (décret n° 2014-129).
REPERES = {
    "montant_base|1983-04-01": 26_400 / FRANCS_PAR_EURO,
    "montant_base|2004-01-01": 6_511.06,
    "montant_majore|2004-01-01": 6_706.39,
    "montant_base|2006-01-01": 6_760.82,
    "montant_majore|2006-01-01": 7_172.54,
    "montant_base|2008-01-01": 6_958.21,
    "montant_majore|2008-01-01": 7_603.41,
    "montant_base|2023-09-01": 8_509.61,
    "montant_majore|2023-09-01": 10_170.86,
    "plafond_ecretement|2014-02-01": 1_120.00 * 12,
}


def _texte(fragment: str) -> str:
    """Le texte d'un morceau de HTML, sans balises ni espaces invisibles."""
    brut = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"[\s​﻿]+", " ", brut).strip()


def _lignes(contenu: str) -> list[list[str]]:
    return [
        [_texte(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", ligne, flags=re.S)]
        for ligne in re.findall(r"<tr[^>]*>(.*?)</tr>", contenu, flags=re.S)
    ]


def _montant(cellule: str) -> float | None:
    """« 26 400,00 F » → 4 024,65 € ; « 9 075,50 € » → 9 075,50 €."""
    trouve = re.fullmatch(r"([\d ]+(?:,\d+)?)\s*(€|F)", cellule)
    if trouve is None:
        return None
    valeur = float(trouve.group(1).replace(" ", "").replace(",", "."))
    return valeur / FRANCS_PAR_EURO if trouve.group(2) == "F" else valeur


def _date(cellule: str) -> str | None:
    trouve = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", cellule)
    if trouve is None:
        return None
    jour, mois, annee = trouve.groups()
    return f"{annee}-{mois}-{jour}"


def lire_minimum(contenu: str) -> list[tuple[str, str, float, str]]:
    """(mesure, date, euros par an, référence) du barème des minima : le
    minimum annuel en deuxième colonne, le majoré annuel en quatrième quand
    la ligne en porte un (depuis 2004), la référence en dernière."""
    lus = []
    for cellules in _lignes(contenu):
        effet = _date(cellules[0]) if cellules else None
        if effet is None:
            continue
        reference = cellules[-1]
        lus.append(("montant_base", effet, _montant(cellules[1]), reference))
        if len(cellules) >= 6:
            lus.append(("montant_majore", effet, _montant(cellules[3]), reference))
    return lus


def lire_plafond(contenu: str) -> list[tuple[str, str, float, str]]:
    """(mesure, date, euros par an, référence) du barème du plafond, publié au mois."""
    lus = []
    for cellules in _lignes(contenu):
        effet = _date(cellules[0]) if cellules else None
        if effet is None or len(cellules) < 2:
            continue
        mensuel = _montant(cellules[1])
        lus.append(("plafond_ecretement", effet,
                    None if mensuel is None else mensuel * 12, cellules[-1]))
    return lus


def controler(lus: list[tuple[str, str, float, str]]) -> list[str]:
    """Ce qui ferait d'une lecture de travers une série fausse sans bruit."""
    erreurs = []
    vus: dict[str, float] = {}
    for mesure, effet, valeur, _ in lus:
        cle = f"{mesure}|{effet}"
        if valeur is None:
            erreurs.append(f"{cle} : montant illisible")
        elif cle in vus:
            erreurs.append(f"{cle} : la date apparaît deux fois")
        else:
            vus[cle] = valeur
    for mesure in ("montant_base", "montant_majore", "plafond_ecretement"):
        serie = sorted((cle, v) for cle, v in vus.items() if cle.startswith(mesure + "|"))
        if not serie:
            erreurs.append(f"{mesure} : aucune ligne lue")
        for (avant, a), (apres, b) in zip(serie, serie[1:]):
            if b < a - 0.005:
                erreurs.append(f"{apres} : {b:.2f} €, moins que {a:.2f} € au {avant}")
    for cle, valeur in vus.items():
        if cle.startswith("montant_majore|"):
            base = vus.get(cle.replace("montant_majore", "montant_base"))
            if base is None or valeur <= base:
                erreurs.append(f"{cle} : le majoré n'excède pas le minimum")
    for cle, attendu in REPERES.items():
        lu = vus.get(cle)
        if lu is None or abs(lu - attendu) > 0.005:
            erreurs.append(f"{cle} : attendu {attendu:.2f}, lu {lu}")
    return erreurs


def telecharger(bareme: str) -> str:
    requete = urllib.request.Request(API.format(bareme), headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return json.loads(reponse.read().decode("utf-8"))["contenu"]


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument(
        "--fichier", type=Path,
        help="réponse JSON de l'API des barèmes (liste complète) déjà "
             "téléchargée, lue au lieu du réseau")
    arguments = analyseur.parse_args(argv)
    if arguments.fichier:
        tous = {b["fileLeafRef"]: b["contenu"] for b in
                json.loads(arguments.fichier.read_text(encoding="utf-8"))}
        contenus = {nom: tous[f"{nom}.aspx"] for nom in (MINIMUM, PLAFOND)}
    else:
        contenus = {nom: telecharger(nom) for nom in (MINIMUM, PLAFOND)}
    lus = lire_minimum(contenus[MINIMUM]) + lire_plafond(contenus[PLAFOND])
    erreurs = controler(lus)
    if erreurs:
        print("Barèmes refusés :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": API.format(MINIMUM) + " ; " + API.format(PLAFOND),
        "recupere_le": date.today().isoformat(),
        "note": "Montants en euros par an, à chaque date de revalorisation : "
                "les francs convertis à 6,55957, le plafond mensuel multiplié "
                "par douze.",
        "serie": {f"{m}|{d}": v for m, d, v, _ in sorted(lus)},
        "references": {f"{m}|{d}": r for m, d, _, r in sorted(lus)},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(lus)} montants écrits dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
