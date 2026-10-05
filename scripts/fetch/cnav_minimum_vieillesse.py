#!/usr/bin/env python3
"""Le barème de l'ASPA d'un couple, par la Cnav.

    python scripts/fetch/cnav_minimum_vieillesse.py
    python scripts/fetch/cnav_minimum_vieillesse.py --fichier baremes.json

À QUOI IL SERT. L'article D. 815-1 du code de la sécurité sociale fixe le
montant de l'allocation de solidarité aux personnes âgées d'un couple dont les
deux membres sont allocataires — son b), que D. 815-2 fait aussi plafond de
ressources du couple —, mais il n'est pas réécrit à chaque revalorisation : il
le date en 2006, 2009, octobre 2014 et de 2018 à 2020, et la loi le revalorise
entre-temps (L. 816-2). ``dila_legi_minimum_vieillesse.py`` certifie ces six
ancres ; ce récupérateur lit ce que la caisse a appliqué les autres années.

LA SOURCE. Deux barèmes de la base de législation de la Cnav, par son API
publique, comme ``cnav_minimum_contributif.py`` :

* « Montant de l'allocation de solidarité aux personnes âgées »
  (``aspa_montant_bar``) : à chaque date de revalorisation depuis le
  1er janvier 2006, le montant annuel et mensuel d'un allocataire et de deux,
  et le texte qui le fixe — décret, puis circulaire de la caisse ;
* « Plafond de ressources pour l'allocation de solidarité aux personnes
  âgées » (``aspa_supplementaire_plafond_ressource_bar``) : aux mêmes dates,
  le plafond d'une personne seule et celui d'un couple.

UNE ANCRE PAR ANNÉE, CELLE QUE L'ANNÉE LAISSE EN PLACE. Le fichier du dépôt
porte un montant par année, que le modèle lit à la liquidation comme à
l'échéance, datée du 31 décembre : chaque année reçoit le montant en vigueur
ce jour-là — celui du 1er septembre en 2008, du 1er octobre en 2014, du
1er juillet en 2022, et celui d'octobre 2014 en 2015, que rien n'a revalorisé.
C'est la convention des ancres de l'article, où le dernier montant d'une année
l'emporte.

LES CONTRÔLES. Le script refuse d'écrire si les ancres de l'article
(``REPERES``) ne se retrouvent pas au centime, à leur date ; si une date
apparaît deux fois, si un montant baisse, si le mensuel publié n'est pas
l'annuel divisé par douze à un centime près ; si le couple ne reçoit pas plus
qu'une personne seule et moins que deux ; si le plafond du couple diffère de
son montant, que D. 815-2 lui égale ; et si, depuis le 1er avril 2010, le
plafond d'une personne seule diffère de son montant, auquel le même article
l'égale depuis cette date — il le dépassait avant.

Statut de fiabilité : ``haute``, jamais ``certifiee`` : la caisse transcrit ce
que le décret ou sa propre circulaire ont fixé. Les ancres de l'article sont
certifiées par la base LEGI ; ce barème ne fait que combler les années
qu'elles ne couvrent pas (``scripts/verifier_donnees.py``).
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
MONTANT = "aspa_montant_bar"
PLAFOND = "aspa_supplementaire_plafond_ressource_bar"
SORTIE = RACINE / "data" / "brut" / "cnav_minimum_vieillesse.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Les montants annuels que l'article D. 815-1 fixe, et que le barème doit
#: redonner au centime à leur date : son a), une personne seule, et son b), un
#: couple d'allocataires (LEGIARTI000006739608, 020562595, 029619584,
#: 036760292).
REPERES = {
    "seule|2006-01-01": 7_323.48,
    "seule|2009-04-01": 8_125.59,
    "seule|2010-04-01": 8_507.49,
    "seule|2011-04-01": 8_907.34,
    "seule|2012-04-01": 9_325.98,
    "seule|2014-10-01": 9_600.00,
    "seule|2018-04-01": 9_998.40,
    "seule|2019-01-01": 10_418.40,
    "seule|2020-01-01": 10_838.40,
    "couple|2006-01-01": 13_137.69,
    "couple|2009-04-01": 13_765.73,
    "couple|2014-10-01": 14_904.00,
    "couple|2018-04-01": 15_522.54,
    "couple|2019-01-01": 16_174.59,
    "couple|2020-01-01": 16_826.64,
}

#: Depuis cette date, le plafond d'une personne seule est son montant maximal
#: (D. 815-2, LEGIARTI000020562591) ; il le dépassait avant.
PLAFOND_EGAL_AU_MONTANT = "2010-04-01"


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
    """« 12 523,14 € » → 12 523,14 ; « 11 001,44€ » aussi."""
    trouve = re.fullmatch(r"([\d ]+(?:,\d+)?)\s*€", cellule)
    if trouve is None:
        return None
    return float(trouve.group(1).replace(" ", "").replace(",", "."))


def _date(cellule: str) -> str | None:
    trouve = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", cellule)
    if trouve is None:
        return None
    jour, mois, annee = trouve.groups()
    return f"{annee}-{mois}-{jour}"


def lire(contenu: str) -> list[dict]:
    """Chaque ligne datée d'un des deux barèmes : la date, l'annuel et le
    mensuel d'une personne seule, puis d'un couple, et la référence — les
    colonnes des deux barèmes sont dans le même ordre."""
    lus = []
    for cellules in _lignes(contenu):
        effet = _date(cellules[0]) if cellules else None
        if effet is None:
            continue
        lus.append({
            "date": effet,
            "seule": _montant(cellules[1]) if len(cellules) > 1 else None,
            "seule_mensuel": _montant(cellules[2]) if len(cellules) > 2 else None,
            "couple": _montant(cellules[3]) if len(cellules) > 3 else None,
            "couple_mensuel": _montant(cellules[4]) if len(cellules) > 4 else None,
            "reference": cellules[5] if len(cellules) > 5 else "",
        })
    return lus


def controler(montants: list[dict], plafonds: list[dict]) -> list[str]:
    """Ce qui ferait d'une lecture de travers une série fausse sans bruit."""
    erreurs = []
    for nom, lignes in (("montant", montants), ("plafond", plafonds)):
        vues = set()
        for ligne in lignes:
            if ligne["date"] in vues:
                erreurs.append(f"{nom} {ligne['date']} : la date apparaît deux fois")
            vues.add(ligne["date"])
            for mesure in ("seule", "couple"):
                annuel, mensuel = ligne[mesure], ligne[f"{mesure}_mensuel"]
                if annuel is None or mensuel is None:
                    erreurs.append(f"{nom} {mesure} {ligne['date']} : montant illisible")
                elif abs(annuel / 12 - mensuel) > 0.01:
                    erreurs.append(f"{nom} {mesure} {ligne['date']} : {mensuel:.2f} € par "
                                   f"mois pour {annuel:.2f} € par an")
        if not lignes:
            erreurs.append(f"{nom} : aucune ligne lue")
    if erreurs:
        return erreurs
    for nom, lignes in (("montant", montants), ("plafond", plafonds)):
        ordonnees = sorted(lignes, key=lambda ligne: ligne["date"])
        for avant, apres in zip(ordonnees, ordonnees[1:]):
            for mesure in ("seule", "couple"):
                if apres[mesure] < avant[mesure] - 0.005:
                    erreurs.append(f"{nom} {mesure} {apres['date']} : {apres[mesure]:.2f} €, "
                                   f"moins que {avant[mesure]:.2f} € au {avant['date']}")
    for ligne in montants:
        if not ligne["seule"] < ligne["couple"] < 2 * ligne["seule"]:
            erreurs.append(f"{ligne['date']} : le couple à {ligne['couple']:.2f} € pour "
                           f"une personne seule à {ligne['seule']:.2f} €")
    par_date = {ligne["date"]: ligne for ligne in plafonds}
    if set(par_date) != {ligne["date"] for ligne in montants}:
        erreurs.append("les deux barèmes ne portent pas les mêmes dates")
    for ligne in montants:
        plafond = par_date.get(ligne["date"])
        if plafond is None:
            continue
        if abs(plafond["couple"] - ligne["couple"]) > 0.005:
            erreurs.append(f"{ligne['date']} : le plafond du couple, {plafond['couple']:.2f} €, "
                           f"n'est pas son montant, {ligne['couple']:.2f} €")
        if (ligne["date"] >= PLAFOND_EGAL_AU_MONTANT
                and abs(plafond["seule"] - ligne["seule"]) > 0.005):
            erreurs.append(f"{ligne['date']} : le plafond d'une personne seule, "
                           f"{plafond['seule']:.2f} €, n'est pas son montant, "
                           f"{ligne['seule']:.2f} €")
    lus = {f"{mesure}|{ligne['date']}": ligne[mesure]
           for ligne in montants for mesure in ("seule", "couple")}
    for cle, attendu in REPERES.items():
        lu = lus.get(cle)
        if lu is None or abs(lu - attendu) > 0.005:
            erreurs.append(f"{cle} : attendu {attendu:.2f}, lu {lu}")
    return erreurs


def ancres_annuelles(montants: list[dict], mesure: str) -> dict[int, float]:
    """Le montant en vigueur au 31 décembre de chaque année, de la première
    date du barème à la dernière : celui que l'année laisse en place."""
    ordonnees = sorted(montants, key=lambda ligne: ligne["date"])
    premiere, derniere = int(ordonnees[0]["date"][:4]), int(ordonnees[-1]["date"][:4])
    ancres = {}
    for annee in range(premiere, derniere + 1):
        en_vigueur = [ligne for ligne in ordonnees if ligne["date"] <= f"{annee}-12-31"]
        ancres[annee] = en_vigueur[-1][mesure]
    return ancres


def telecharger(bareme: str) -> str:
    requete = urllib.request.Request(API.format(bareme), headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return json.loads(reponse.read().decode("utf-8-sig"))["contenu"]


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument(
        "--fichier", type=Path,
        help="réponse JSON de l'API des barèmes (liste complète) déjà "
             "téléchargée, lue au lieu du réseau")
    arguments = analyseur.parse_args(argv)
    if arguments.fichier:
        tous = {b["fileLeafRef"]: b["contenu"] for b in
                json.loads(arguments.fichier.read_text(encoding="utf-8-sig"))}
        contenus = {nom: tous[f"{nom}.aspx"] for nom in (MONTANT, PLAFOND)}
    else:
        contenus = {nom: telecharger(nom) for nom in (MONTANT, PLAFOND)}
    montants, plafonds = lire(contenus[MONTANT]), lire(contenus[PLAFOND])
    erreurs = controler(montants, plafonds)
    if erreurs:
        print("Barèmes refusés :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    couple = ancres_annuelles(montants, "couple")
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": API.format(MONTANT) + " ; " + API.format(PLAFOND),
        "recupere_le": date.today().isoformat(),
        "note": "Montants annuels de l'ASPA à chaque date de revalorisation "
                "(datee : une personne seule, un couple d'allocataires), et, "
                "pour le couple, le montant en vigueur au 31 décembre de chaque "
                "année (serie_couple), qui est aussi son plafond de ressources.",
        "datee": {f"{mesure}|{ligne['date']}": ligne[mesure]
                  for ligne in sorted(montants, key=lambda l: l["date"])
                  for mesure in ("seule", "couple")},
        "references": {ligne["date"]: ligne["reference"]
                       for ligne in sorted(montants, key=lambda l: l["date"])},
        "serie_couple": {str(annee): valeur for annee, valeur in sorted(couple.items())},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(montants)} dates lues, {len(couple)} ancres du couple écrites dans "
          f"{SORTIE.relative_to(RACINE)}")
    for annee, valeur in sorted(couple.items()):
        print(f"  {annee} : {valeur:.2f} € par an")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
