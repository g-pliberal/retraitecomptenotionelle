#!/usr/bin/env python3
"""Le minimum de la réversion du régime général, et le plafond de sa majoration, par la Cnav.

    python scripts/fetch/cnav_reversion.py
    python scripts/fetch/cnav_reversion.py --fichier baremes.json

À QUOI IL SERT. La pension de réversion du régime général « ne peut être
inférieure » à un montant minimum quand l'assuré décédé avait quinze ans
d'assurance, et ce minimum se réduit en soixantièmes en deçà (D. 353-1) ; elle
est majorée de 11,1 % quand le survivant a l'âge du taux plein et que ses
retraites ne dépassent pas un plafond trimestriel (L. 353-6, D. 353-4). Le
minimum est l'ancienne allocation aux vieux travailleurs salariés, revalorisée
comme les pensions ; D. 353-1 ne l'écrit en euros que depuis le 1er janvier
2026 (3 983,29 euros au 1er janvier 2025), et D. 353-4 n'écrit du plafond que
sa valeur de 2010, 2 400 euros. Les autres années, seule la caisse les publie.

LA SOURCE. Deux barèmes de la base de législation de la Cnav, par son API
publique, comme ``cnav_minimum_vieillesse.py`` :

* « Montant minimum de la retraite de réversion »
  (``retraite_reversion_montant_minimum_bar``) : chaque montant annuel depuis
  la loi du 14 mars 1941, avec la loi, le décret, l'arrêté ou la circulaire
  qui le fixe — en anciens francs jusqu'en 1959, en francs de 1960 à 2001, en
  euros depuis ; jusqu'en 1961, celui des villes de plus de 5 000 habitants,
  la première valeur de la cellule, et en 1963 celui des moins de 75 ans ;
* « Plafond de ressources pour la majoration de la retraite de réversion »
  (``retraite_reversion_plafond_ressource_majoration_retraite_reversion_bar``) :
  le plafond trimestriel, depuis le 1er janvier 2010.

UNE ANCRE PAR ANNÉE, CELLE QUE L'ANNÉE LAISSE EN PLACE, EN EUROS. Le modèle lit
les montants d'une réversion au 31 décembre de l'année de ses euros, comme la
pension que « faire vivre » mène jusque-là : chaque année reçoit le montant en
vigueur ce jour-là — celui du 1er juillet en 2022, celui d'octobre 2015 en
2016, que rien n'a revalorisé. Les francs se convertissent au taux légal de
6,55957, les anciens francs au centième.

LES CONTRÔLES. Le script refuse d'écrire si les ancres des articles
(``REPERES``) ne se retrouvent pas au centime, à leur date ; si une date
apparaît deux fois, si un montant baisse, si un mensuel publié n'est pas
l'annuel divisé par douze à un centime près ; et si, depuis 2010, le plafond
ne garde pas avec le minimum le rapport de leurs deux premières valeurs, à un
dix-millième près : D. 353-1 et D. 353-4 les revalorisent l'un et l'autre
comme les pensions (L. 161-23-1), aux mêmes dates.

Statut de fiabilité : ``haute``, jamais ``certifiee`` : la caisse transcrit ce
que le texte ou sa propre circulaire ont fixé (``scripts/verifier_donnees.py``).
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
MINIMUM = "retraite_reversion_montant_minimum_bar"
PLAFOND = "retraite_reversion_plafond_ressource_majoration_retraite_reversion_bar"
SORTIE = RACINE / "data" / "brut" / "cnav_reversion.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Le taux de conversion du franc en euro, et l'ancien franc au centième.
FRANCS_PAR_EURO = 6.55957
EN_FRANCS = {"€": 1.0, "F": 1.0 / FRANCS_PAR_EURO, "AF": 0.01 / FRANCS_PAR_EURO}

#: Ce que les articles écrivent, et que le barème doit redonner au centime à
#: leur date : D. 353-1 depuis 2026 (LEGIARTI000053356066), le minimum ;
#: D. 353-4 (LEGIARTI000020791861), le plafond trimestriel de la majoration.
REPERES = {
    "minimum|2025-01-01": 3_983.29,
    "plafond|2010-01-01": 2_400.00,
}

#: Depuis cette date, le plafond et le minimum se revalorisent ensemble.
DEBUT_DU_PLAFOND = "2010-01-01"


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
    """Le premier montant de la cellule, en euros : « 3 983,29 € », « 14 800,00 F »,
    « 72 380 AF68 640 AF pour les villes… » (le premier, celui des grandes villes)."""
    trouve = re.match(r"\s*(\d[\d ]*(?:,\d+)?)\s*(AF|F|€)", cellule)
    if trouve is None:
        return None
    nombre = float(trouve.group(1).replace(" ", "").replace(",", "."))
    return nombre * EN_FRANCS[trouve.group(2)]


def _date(cellule: str) -> str | None:
    trouve = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", cellule)
    if trouve is None:
        return None
    jour, mois, annee = trouve.groups()
    return f"{annee}-{mois}-{jour}"


def lire(contenu: str) -> list[dict]:
    """Chaque ligne datée d'un barème : la date, le montant en euros, le mensuel
    publié s'il y en a un (depuis 2004), et la référence, dernière cellule."""
    lus = []
    for cellules in _lignes(contenu):
        effet = _date(cellules[0]) if cellules else None
        if effet is None:
            continue
        mensuel = _montant(cellules[2]) if len(cellules) > 3 else None
        lus.append({
            "date": effet,
            "montant": _montant(cellules[1]) if len(cellules) > 1 else None,
            "mensuel": mensuel,
            "reference": cellules[-1] if len(cellules) > 2 else "",
        })
    return lus


def controler(minimums: list[dict], plafonds: list[dict]) -> list[str]:
    """Ce qui ferait d'une lecture de travers une série fausse sans bruit."""
    erreurs = []
    for nom, lignes in (("minimum", minimums), ("plafond", plafonds)):
        vues = set()
        for ligne in lignes:
            if ligne["date"] in vues:
                erreurs.append(f"{nom} {ligne['date']} : la date apparaît deux fois")
            vues.add(ligne["date"])
            if ligne["montant"] is None:
                erreurs.append(f"{nom} {ligne['date']} : montant illisible")
            elif (ligne["mensuel"] is not None
                  and abs(ligne["montant"] / 12 - ligne["mensuel"]) > 0.01):
                erreurs.append(f"{nom} {ligne['date']} : {ligne['mensuel']:.2f} € par mois "
                               f"pour {ligne['montant']:.2f} € par an")
        if not lignes:
            erreurs.append(f"{nom} : aucune ligne lue")
    if erreurs:
        return erreurs
    for nom, lignes in (("minimum", minimums), ("plafond", plafonds)):
        ordonnees = sorted(lignes, key=lambda ligne: ligne["date"])
        for avant, apres in zip(ordonnees, ordonnees[1:]):
            if apres["montant"] < avant["montant"] - 0.005:
                erreurs.append(f"{nom} {apres['date']} : {apres['montant']:.2f} €, moins "
                               f"que {avant['montant']:.2f} € au {avant['date']}")
    lus = {f"{nom}|{ligne['date']}": ligne["montant"]
           for nom, lignes in (("minimum", minimums), ("plafond", plafonds))
           for ligne in lignes}
    for cle, attendu in REPERES.items():
        lu = lus.get(cle)
        if lu is None or abs(lu - attendu) > 0.005:
            erreurs.append(f"{cle} : attendu {attendu:.2f}, lu {lu}")
    minimum_au = en_vigueur(minimums)
    rapports = [(ligne["date"], ligne["montant"] / minimum_au(ligne["date"]))
                for ligne in sorted(plafonds, key=lambda ligne: ligne["date"])
                if ligne["date"] >= DEBUT_DU_PLAFOND]
    if rapports:
        _, premier = rapports[0]
        for jour, rapport in rapports[1:]:
            if abs(rapport - premier) > 1e-4:
                erreurs.append(f"plafond {jour} : {rapport:.5f} fois le minimum, "
                               f"{premier:.5f} au {DEBUT_DU_PLAFOND}")
    return erreurs


def en_vigueur(lignes: list[dict]):
    """Le montant en vigueur à une date (AAAA-MM-JJ) : la dernière ligne datée
    au plus tard ce jour-là."""
    ordonnees = sorted(lignes, key=lambda ligne: ligne["date"])

    def au(jour: str) -> float:
        valables = [ligne for ligne in ordonnees if ligne["date"] <= jour]
        return valables[-1]["montant"]
    return au


def ancres_annuelles(lignes: list[dict]) -> dict[int, float]:
    """Le montant en vigueur au 31 décembre de chaque année, de la première
    date du barème à la dernière : celui que l'année laisse en place."""
    ordonnees = sorted(lignes, key=lambda ligne: ligne["date"])
    au = en_vigueur(ordonnees)
    premiere, derniere = int(ordonnees[0]["date"][:4]), int(ordonnees[-1]["date"][:4])
    return {annee: au(f"{annee}-12-31") for annee in range(premiere, derniere + 1)}


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
        contenus = {nom: tous[f"{nom}.aspx"] for nom in (MINIMUM, PLAFOND)}
    else:
        contenus = {nom: telecharger(nom) for nom in (MINIMUM, PLAFOND)}
    minimums, plafonds = lire(contenus[MINIMUM]), lire(contenus[PLAFOND])
    erreurs = controler(minimums, plafonds)
    if erreurs:
        print("Barèmes refusés :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    serie_minimum, serie_plafond = ancres_annuelles(minimums), ancres_annuelles(plafonds)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": API.format(MINIMUM) + " ; " + API.format(PLAFOND),
        "recupere_le": date.today().isoformat(),
        "note": "Le minimum annuel de la réversion du régime général (D. 353-1) et "
                "le plafond trimestriel de sa majoration de 11,1 % (D. 353-4), en "
                "euros, à chaque date du barème (datee), et le montant en vigueur au "
                "31 décembre de chaque année (serie_minimum, serie_plafond).",
        "datee": {f"{nom}|{ligne['date']}": round(ligne["montant"], 6)
                  for nom, lignes in (("minimum", minimums), ("plafond", plafonds))
                  for ligne in sorted(lignes, key=lambda l: l["date"])},
        "references": {f"{nom}|{ligne['date']}": ligne["reference"]
                       for nom, lignes in (("minimum", minimums), ("plafond", plafonds))
                       for ligne in sorted(lignes, key=lambda l: l["date"])},
        "serie_minimum": {str(a): round(v, 6) for a, v in sorted(serie_minimum.items())},
        "serie_plafond": {str(a): round(v, 6) for a, v in sorted(serie_plafond.items())},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(minimums)} minimums et {len(plafonds)} plafonds lus, "
          f"{len(serie_minimum)} et {len(serie_plafond)} ancres écrites dans "
          f"{SORTIE.relative_to(RACINE)}")
    for annee in sorted(serie_minimum):
        plafond = serie_plafond.get(annee)
        print(f"  {annee} : minimum {serie_minimum[annee]:.2f} € par an"
              + (f", plafond {plafond:.2f} € par trimestre" if plafond else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
