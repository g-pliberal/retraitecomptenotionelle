#!/usr/bin/env python3
"""Le minimum de la réversion du régime général, sa limite de cumul, ses majorations, par la Cnav.

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
  le plafond trimestriel, depuis le 1er janvier 2010 ;
* « Limite forfaitaire de cumul pour la retraite de réversion »
  (``retraite_reversion_limite_forfaitaire_cumul_bar``) : la limite au-dessous
  de laquelle D. 355-1 ne réduit pas la réversion attribuée avant le
  1er juillet 2004 quand le survivant a ses propres retraites, depuis le
  1er juillet 1974 (loi n° 75-3, article 21) — l'AVTS et l'allocation
  supplémentaire jusqu'en juin 1977, puis 60 %, 70 % et, depuis le
  1er décembre 1982, 73 % du maximum des pensions ;
* « Montant mensuel de la majoration forfaitaire pour charge d'enfant »
  (``mfe_montant_bar``) : la majoration de L. 353-5 et R. 353-11, par enfant,
  depuis le 1er janvier 1988, que le script porte à l'année (douze mois).

Le barème « Montant maximum de la retraite de réversion »
(``retraite_reversion_montant_maximum_bar``) ne sert qu'au contrôle : la
limite forfaitaire en est, à chaque date commune, le multiple que les deux
taux disent (60 % ou 70 % du maximum des pensions, quand la réversion en est
50 % ; 73 %, quand elle en est 52 %, puis 54 %).

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
LIMITE = "retraite_reversion_limite_forfaitaire_cumul_bar"
ENFANT = "mfe_montant_bar"
MAXIMUM = "retraite_reversion_montant_maximum_bar"
BAREMES = (MINIMUM, PLAFOND, LIMITE, ENFANT, MAXIMUM)
SORTIE = RACINE / "data" / "brut" / "cnav_reversion.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Le taux de conversion du franc en euro, et l'ancien franc au centième.
FRANCS_PAR_EURO = 6.55957
EN_FRANCS = {"€": 1.0, "F": 1.0 / FRANCS_PAR_EURO, "AF": 0.01 / FRANCS_PAR_EURO}

#: Ce que les articles écrivent, et que le barème doit redonner au centime à
#: leur date : D. 353-1 depuis 2026 (LEGIARTI000053356066), le minimum ;
#: D. 353-4 (LEGIARTI000020791861), le plafond trimestriel de la majoration ;
#: R. 353-11, la majoration pour enfant.
REPERES = {
    "minimum|2025-01-01": 3_983.29,
    "plafond|2010-01-01": 2_400.00,
    # R. 353-11 : 400 F par mois au 1er janvier 1988 (LEGIARTI000006749417),
    # 112,58 euros au 1er janvier 2025 (LEGIARTI000053335708), portés à l'année.
    "enfant|1988-01-01": round(12 * 400 / 6.55957, 2),
    "enfant|2025-01-01": 12 * 112.58,
}

#: Depuis cette date, le plafond et le minimum se revalorisent ensemble.
DEBUT_DU_PLAFOND = "2010-01-01"

#: Le montant annuel que le barème de la limite forfaitaire écrit de travers :
#: au 1er janvier 1982, « 27 278,00 F » pour un mensuel de 2 306,50 F, quand
#: 70 % du maximum des pensions de ce jour (2 × 19 770 F) font 27 678 F, douze
#: fois le mensuel. Le script prend 27 678 F, et refuse si la ligne change.
CORRECTIONS = {"limite|1982-01-01": (27_278.00, 27_678.00)}

#: Le rapport de la limite forfaitaire au maximum de la réversion, par
#: période (D. 355-1 ; article 90 du décret n° 45-179 ; circulaire Cnav
#: n° 120/82, § 5) : 60 % puis 70 % du maximum des pensions, la réversion en
#: étant 50 % ; 73 %, la réversion en étant 52 %, puis 54 % depuis 1995.
RAPPORTS_DE_LA_LIMITE = (
    ("1977-07-01", "1978-07-01", 0.60 / 0.50),
    ("1978-07-01", "1982-12-01", 0.70 / 0.50),
    ("1982-12-01", "1995-01-01", 0.73 / 0.52),
    ("1995-01-01", "9999-12-31", 0.73 / 0.54),
)

#: La date où c'est le barème du maximum qui se trompe : au 1er juillet 1987,
#: il répète le montant du 1er janvier 1988 (31 044 F), quand la limite
#: forfaitaire du jour (43 099,20 F) en suppose 30 701 F. Le contrôle s'y tait.
MAXIMUM_DOUTEUX = frozenset({"1987-07-01"})


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


def controler(series: dict[str, list[dict]]) -> list[str]:
    """Ce qui ferait d'une lecture de travers une série fausse sans bruit."""
    erreurs = []
    for nom, lignes in series.items():
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
    for nom, lignes in series.items():
        ordonnees = sorted(lignes, key=lambda ligne: ligne["date"])
        for avant, apres in zip(ordonnees, ordonnees[1:]):
            if apres["montant"] < avant["montant"] - 0.005:
                erreurs.append(f"{nom} {apres['date']} : {apres['montant']:.2f} €, moins "
                               f"que {avant['montant']:.2f} € au {avant['date']}")
    lus = {f"{nom}|{ligne['date']}": ligne["montant"]
           for nom, lignes in series.items() for ligne in lignes}
    for cle, attendu in REPERES.items():
        lu = lus.get(cle)
        if lu is None or abs(lu - attendu) > 0.005:
            erreurs.append(f"{cle} : attendu {attendu:.2f}, lu {lu}")
    minimum_au = en_vigueur(series["minimum"])
    rapports = [(ligne["date"], ligne["montant"] / minimum_au(ligne["date"]))
                for ligne in sorted(series["plafond"], key=lambda ligne: ligne["date"])
                if ligne["date"] >= DEBUT_DU_PLAFOND]
    if rapports:
        _, premier = rapports[0]
        for jour, rapport in rapports[1:]:
            if abs(rapport - premier) > 1e-4:
                erreurs.append(f"plafond {jour} : {rapport:.5f} fois le minimum, "
                               f"{premier:.5f} au {DEBUT_DU_PLAFOND}")
    if "maximum" in series and "limite" in series:
        maximums = {ligne["date"]: ligne["montant"] for ligne in series["maximum"]}
        for ligne in series["limite"]:
            maximum = maximums.get(ligne["date"])
            rapport = next((r for debut, fin, r in RAPPORTS_DE_LA_LIMITE
                            if debut <= ligne["date"] < fin), None)
            if maximum is None or rapport is None or ligne["date"] in MAXIMUM_DOUTEUX:
                continue
            if abs(ligne["montant"] - rapport * maximum) > 0.6 / FRANCS_PAR_EURO:
                erreurs.append(f"limite {ligne['date']} : {ligne['montant']:.2f} €, "
                               f"pas {rapport:.5f} fois le maximum {maximum:.2f} €")
    return erreurs


def corriger(lignes: list[dict], nom: str) -> list[dict]:
    """Les lignes de ``nom``, le montant de :data:`CORRECTIONS` remplacé, en
    euros ; refuse si la ligne n'écrit plus ce qu'elle écrivait."""
    corrigees = []
    for ligne in lignes:
        cle = f"{nom}|{ligne['date']}"
        if cle in CORRECTIONS:
            ecrit, juste = CORRECTIONS[cle]
            if abs(ligne["montant"] - ecrit / FRANCS_PAR_EURO) > 0.005:
                raise ValueError(f"{cle} : le barème n'écrit plus {ecrit:.2f} F")
            ligne = ligne | {"montant": juste / FRANCS_PAR_EURO,
                             "mensuel": juste / 12 / FRANCS_PAR_EURO}
        corrigees.append(ligne)
    return corrigees


def lire_limite(contenu: str) -> list[dict]:
    """La limite forfaitaire : ses tableaux anciens n'ont pas de colonne de
    référence, et la troisième cellule y est le mensuel."""
    lus = []
    for cellules in _lignes(contenu):
        effet = _date(cellules[0]) if cellules else None
        if effet is None:
            continue
        lus.append({"date": effet, "montant": _montant(cellules[1]),
                    "mensuel": _montant(cellules[2]) if len(cellules) > 2 else None,
                    "reference": cellules[3] if len(cellules) > 3 else ""})
    return lus


def lire_enfant(contenu: str) -> list[dict]:
    """La majoration pour enfant : un montant mensuel par enfant, porté à
    l'année."""
    return [ligne | {"montant": 12 * ligne["montant"], "mensuel": ligne["montant"]}
            for ligne in lire(contenu) if ligne["montant"] is not None]


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
        contenus = {nom: tous[f"{nom}.aspx"] for nom in BAREMES}
    else:
        contenus = {nom: telecharger(nom) for nom in BAREMES}
    series = {"minimum": lire(contenus[MINIMUM]), "plafond": lire(contenus[PLAFOND]),
              "limite": corriger(lire_limite(contenus[LIMITE]), "limite"),
              "enfant": lire_enfant(contenus[ENFANT]),
              "maximum": lire(contenus[MAXIMUM])}
    erreurs = controler(series)
    if erreurs:
        print("Barèmes refusés :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    ecrites = ("minimum", "plafond", "limite", "enfant")
    ancres = {nom: ancres_annuelles(series[nom]) for nom in ecrites}
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": " ; ".join(API.format(nom) for nom in BAREMES),
        "recupere_le": date.today().isoformat(),
        "note": "Le minimum annuel de la réversion du régime général (D. 353-1), le "
                "plafond trimestriel de sa majoration de 11,1 % (D. 353-4), la limite "
                "forfaitaire annuelle de cumul d'avant juillet 2004 (D. 355-1) et la "
                "majoration forfaitaire annuelle par enfant à charge (L. 353-5, "
                "R. 353-11), en euros, à chaque date du barème (datee), et le montant "
                "en vigueur au 31 décembre de chaque année (serie_minimum, "
                "serie_plafond, serie_limite, serie_enfant).",
        "datee": {f"{nom}|{ligne['date']}": round(ligne["montant"], 6)
                  for nom in ecrites
                  for ligne in sorted(series[nom], key=lambda l: l["date"])},
        "references": {f"{nom}|{ligne['date']}": ligne["reference"]
                       for nom in ecrites
                       for ligne in sorted(series[nom], key=lambda l: l["date"])},
        **{f"serie_{nom}": {str(a): round(v, 6) for a, v in sorted(ancres[nom].items())}
           for nom in ecrites},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(", ".join(f"{len(series[nom])} {nom}" for nom in ecrites)
          + f" lus, ancres écrites dans {SORTIE.relative_to(RACINE)}")
    for annee in sorted(ancres["minimum"]):
        morceaux = [f"minimum {ancres['minimum'][annee]:.2f}"]
        for nom in ("plafond", "limite", "enfant"):
            if annee in ancres[nom]:
                morceaux.append(f"{nom} {ancres[nom][annee]:.2f}")
        print(f"  {annee} : " + ", ".join(morceaux))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
