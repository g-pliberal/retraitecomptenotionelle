#!/usr/bin/env python3
"""L'allocation aux vieux travailleurs salariés, l'allocation supplémentaire et le trimestre d'avant 1972, par la Cnav.

    python scripts/fetch/cnav_avts.py
    python scripts/fetch/cnav_avts.py --fichier baremes.json

À QUOI IL SERT. Avant 1972, un trimestre ne se validait pas au SMIC : de 1949 à
1971, « autant de trimestres d'assurance que le salaire annuel […] représente
de fois le montant trimestriel de l'allocation aux vieux travailleurs salariés
au 1er janvier de l'année considérée, avec un maximum de quatre trimestres par
année civile ; jusqu'au 31 décembre 1962, ce montant est celui des villes de
plus de 5 000 habitants » ; de 1946 à 1948, autant de fois 18 F, 1 800 anciens
francs (R. 351-9). Et le minimum vieillesse d'avant l'ASPA tenait en deux
étages : l'allocation aux vieux travailleurs salariés (AVTS), ou ce qui en
tenait lieu, et l'allocation supplémentaire du Fonds national de solidarité,
servie depuis 1956 sous un plafond de ressources. Aucun article en vigueur
n'en écrit les montants : des lois, puis des décrets, les ont fixés un à un.

LA SOURCE. Quatre barèmes de la base de législation de la Cnav, par son API
publique, comme ``cnav_reversion.py`` :

* « Allocation aux vieux travailleurs salariés […] - Montant »
  (``ancienne_prestation_autre_prestation_montant_bar``) : chaque montant
  annuel depuis la loi du 14 mars 1941, avec le texte qui le fixe — jusqu'en
  1961, celui des villes de plus de 5 000 habitants, la première valeur de la
  cellule, et en 1963 celui des allocataires de moins de 75 ans ;
* « Allocation supplémentaire - Montant »
  (``ancienne_prestation_allocation_supplementaire_montant_bar``) : depuis le
  1er avril 1956, pour un allocataire, et pour deux depuis le 1er juillet 1982 ;
* « Allocation supplémentaire - Plafond de ressources »
  (``ancienne_prestation_allocation_supplementaire_plafond_ressource_bar``) :
  celui d'une personne seule et celui d'un couple marié ;
* « Salaire validant un trimestre » (``salaire_validant_un_trimestre_montant_bar``) :
  le seuil de chaque année depuis 1930, en métropole, aux Antilles et en
  Guyane, et à La Réunion.

CE QUI EST ÉCRIT. ``data/brut/cnav_avts.json`` : chaque montant daté, en euros,
avec sa référence ; le seuil d'un trimestre de 1946 à 1971 tel que R. 351-9 le
définit (``seuil_trimestre``), que ``salaire_validant_trimestre_avant_1972.csv``
reprend ; le barème des seuils tel que la caisse le publie, outre-mer compris
(``bareme_seuil``) ; et le montant en vigueur au 31 décembre de chaque année
(``serie_*``), la convention des séries du minimum vieillesse. Les francs se
convertissent au taux légal de 6,55957, les anciens francs au centième, le
franc CFA de La Réunion de 1948 à deux anciens francs.

LES CONTRÔLES. Le script refuse d'écrire si une date apparaît deux fois, si un
montant baisse ; si les montants que des textes écrivent (``REPERES`` : le
Journal officiel, l'article D. 815-1 et R. 351-9) ne s'y retrouvent pas à
leur date ; si le seuil de 1949 à 1971 n'est pas, au centime, le quart de
l'AVTS en vigueur au 1er janvier, ce que R. 351-9 définit ; et si le seuil de
1972 à aujourd'hui n'est pas, au centime, 200 SMIC horaires, 150 depuis 2014,
au SMIC du dépôt (``macro/smic_horaire.csv``), ce qui recontrôle le seuil que
le modèle calcule.

UN ÉCART, DÉCLARÉ. Le barème porte 216 anciens francs pour 1946 ; R. 351-9, de
sa rédaction de 1985 (LEGIARTI000006749353) à celle de 2014
(LEGIARTI000028751530), et l'article 71 du décret n° 45-0179 avant lui
(LEGIARTI000006760608), écrivent 18 F, 1 800 anciens francs, « pour la période
comprise entre le 1er janvier 1946 et le 31 décembre 1948 ». Le texte l'emporte :
le seuil de 1946 est celui de 1947.

Statut de fiabilité : ``haute``, jamais ``certifiee`` : la caisse transcrit ce
que les textes ont fixé (``scripts/verifier_donnees.py``).
"""

from __future__ import annotations

import argparse
import csv
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
AVTS = "ancienne_prestation_autre_prestation_montant_bar"
SUPPLEMENTAIRE = "ancienne_prestation_allocation_supplementaire_montant_bar"
PLAFOND = "ancienne_prestation_allocation_supplementaire_plafond_ressource_bar"
SEUIL = "salaire_validant_un_trimestre_montant_bar"
BAREMES = (AVTS, SUPPLEMENTAIRE, PLAFOND, SEUIL)
SORTIE = RACINE / "data" / "brut" / "cnav_avts.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Le taux de conversion du franc en euro ; l'ancien franc au centième ; le
#: franc CFA de La Réunion, que la caisse écrit pour 1948, à deux anciens francs.
FRANCS_PAR_EURO = 6.55957
EN_FRANCS = {"€": 1.0, "F": 1.0 / FRANCS_PAR_EURO, "AF": 0.01 / FRANCS_PAR_EURO,
             "CFA": 0.02 / FRANCS_PAR_EURO}

#: Ce que les textes écrivent, et que les barèmes doivent redonner au centime à
#: leur date, en francs :
#: - le décret n° 70-879, notice du Journal officiel (JORFTEXT000000518679) :
#:   « A COMPTER DU 01-10-1970, LES TAUX SONT PORTES A 1750FRS PAR AN » ;
#: - le décret n° 80-1159 (JORFTEXT000000517402) : « FIXANT A 8500FRS PAR AN A
#:   COMPTER DU 01-01-1981 », et « MINIMUM VIEILLESSE: 17000FRS PAR AN » ;
#: - le décret n° 90-265, article 1er (JORFARTI000002138946) : « Sont portés à
#:   14800 F par an à compter du 1er janvier 1990 et à 14990 F par an à compter
#:   du 1er juillet 1990 : Le montant de l'allocation aux vieux travailleurs
#:   salariés » ;
#: - le décret n° 90-266, article 1er (JORFARTI000001947321) : l'allocation
#:   supplémentaire « est fixé[e] à 19920 F à compter du 1er janvier 1990 et à
#:   20180 F à compter du 1er juillet 1990 ».
REPERES_EN_FRANCS = {
    "avts|1970-10-01": 1_750.0,
    "avts|1981-01-01": 8_500.0,
    "as_seul|1981-01-01": 8_500.0,
    "avts|1990-01-01": 14_800.0,
    "avts|1990-07-01": 14_990.0,
    "as_seul|1990-01-01": 19_920.0,
    "as_seul|1990-07-01": 20_180.0,
}

#: L'ancre certifiée de 2006 du minimum vieillesse d'une personne seule, lue
#: dans D. 815-1 (``dila_legi_minimum_vieillesse.py``) : la somme des deux
#: étages au 1er janvier 2006 doit la redonner au centime.
MINIMUM_2006 = ("2006-01-01", 7_323.48)

#: Le seuil d'un trimestre de 1946 à 1948, 18 F (R. 351-9).
SEUIL_1946_1948 = 18.0 / FRANCS_PAR_EURO
#: Les années que R. 351-9 rapporte à l'AVTS du 1er janvier.
PREMIERE_ANNEE_AVTS, DERNIERE_ANNEE_AVTS = 1949, 1971

#: Les séries datées, et le barème dont chacune vient.
SERIES = ("avts", "as_seul", "as_couple", "plafond_seul", "plafond_couple")


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
    « 72 380 AF / 68 640 AF pour les villes… » (le premier, celui des grandes
    villes), « 900 CFA » ; ``None`` pour « - » ou « 60 cotisations »."""
    trouve = re.match(r"\s*(\d[\d ]*(?:,\d+)?)\s*(AF|CFA|F|€)(?!\w)", cellule)
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


def lire_datees(contenus: dict[str, str]) -> dict[str, list[dict]]:
    """Les cinq séries datées : la date, le montant en euros, la référence.

    L'allocation supplémentaire a trois formes de tableau — une colonne avant
    le 1er juillet 1982, deux allocataires ensuite, et les mensuels depuis
    2004 — ; son plafond, deux, le mensuel en plus depuis 2000. Le montant
    pour deux allocataires et celui du couple se lisent dans l'avant-dernière
    colonne annuelle.
    """
    series: dict[str, list[dict]] = {nom: [] for nom in SERIES}
    for nom_bareme, colonnes in ((AVTS, {"avts": 1}),
                                 (SUPPLEMENTAIRE, {"as_seul": 1, "as_couple": None}),
                                 (PLAFOND, {"plafond_seul": 1, "plafond_couple": None})):
        for cellules in _lignes(contenus[nom_bareme]):
            effet = _date(cellules[0]) if cellules else None
            if effet is None:
                continue
            for nom, rang in colonnes.items():
                if rang is None:
                    # Le second montant annuel : la quatrième cellule quand le
                    # tableau porte les mensuels, la troisième sinon ; aucun
                    # quand la ligne n'a qu'un montant.
                    rang = 3 if len(cellules) >= 6 else 2 if len(cellules) == 4 else None
                    if rang is None:
                        continue
                montant = _montant(cellules[rang])
                series[nom].append({"date": effet, "montant": montant,
                                    "reference": cellules[-1]})
    return series


def lire_seuils(contenu: str) -> dict[int, dict[str, float | None]]:
    """Le barème des seuils d'un trimestre, année par année, en euros : la
    métropole, et, de 1948 à 1995, les Antilles et la Guyane, et La Réunion.
    Les lignes « 1936 à 1945 » et « 1930 à 1935 », qui ne sont pas des
    salaires, ne sont pas lues."""
    seuils: dict[int, dict[str, float | None]] = {}
    for cellules in _lignes(contenu):
        if not cellules or not re.fullmatch(r"\d{4}", cellules[0]):
            continue
        annee = int(cellules[0])
        if len(cellules) >= 4:
            seuils[annee] = {"metropole": _montant(cellules[1]),
                             "antilles_guyane": _montant(cellules[2]),
                             "reunion": _montant(cellules[3])}
        else:
            seuils[annee] = {"metropole": _montant(cellules[1]),
                             "antilles_guyane": None, "reunion": None}
    return seuils


def en_vigueur(lignes: list[dict]):
    """Le montant en vigueur à une date (AAAA-MM-JJ) : la dernière ligne datée
    au plus tard ce jour-là ; ``None`` avant la première."""
    ordonnees = sorted(lignes, key=lambda ligne: ligne["date"])

    def au(jour: str) -> float | None:
        valables = [ligne for ligne in ordonnees if ligne["date"] <= jour]
        return valables[-1]["montant"] if valables else None
    return au


def ancres_annuelles(lignes: list[dict]) -> dict[int, float]:
    """Le montant en vigueur au 31 décembre de chaque année, de la première
    date de la série à la dernière : celui que l'année laisse en place."""
    ordonnees = sorted(lignes, key=lambda ligne: ligne["date"])
    au = en_vigueur(ordonnees)
    premiere, derniere = int(ordonnees[0]["date"][:4]), int(ordonnees[-1]["date"][:4])
    return {annee: au(f"{annee}-12-31") for annee in range(premiere, derniere + 1)}


def seuil_trimestre(avts: list[dict]) -> dict[int, float]:
    """Le seuil d'un trimestre que R. 351-9 définit, de 1946 à 1971 : 18 F
    jusqu'en 1948, puis le quart de l'AVTS en vigueur au 1er janvier."""
    au = en_vigueur(avts)
    seuils = {annee: SEUIL_1946_1948 for annee in range(1946, PREMIERE_ANNEE_AVTS)}
    for annee in range(PREMIERE_ANNEE_AVTS, DERNIERE_ANNEE_AVTS + 1):
        seuils[annee] = au(f"{annee}-01-01") / 4
    return seuils


def _serie_du_depot(nom: str, colonne: str) -> dict[int, float]:
    """Une série annuelle du dépôt, par son nom de fichier sous ``data/reference``."""
    chemin = RACINE / "data" / "reference" / nom
    if not chemin.exists():
        return {}
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        return {int(ligne["annee"]): float(ligne[colonne]) for ligne in csv.DictReader(lignes)}


def controler(series: dict[str, list[dict]],
              bareme: dict[int, dict[str, float | None]]) -> tuple[list[str], list[str]]:
    """Les erreurs, qui font refuser l'écriture, et les écarts, déclarés."""
    erreurs, ecarts = [], []
    for nom, lignes in series.items():
        if not lignes:
            erreurs.append(f"{nom} : aucune ligne lue")
        vues = set()
        for ligne in lignes:
            if ligne["date"] in vues:
                erreurs.append(f"{nom} {ligne['date']} : la date apparaît deux fois")
            vues.add(ligne["date"])
            if ligne["montant"] is None:
                erreurs.append(f"{nom} {ligne['date']} : montant illisible")
    if erreurs:
        return erreurs, ecarts
    # Le montant pour deux allocataires baisse en 1992 : il était jusque-là le
    # double du montant d'un seul, puis devient celui du ménage. Les autres ne
    # baissent jamais.
    for nom in ("avts", "as_seul", "plafond_seul", "plafond_couple"):
        ordonnees = sorted(series[nom], key=lambda ligne: ligne["date"])
        for avant, apres in zip(ordonnees, ordonnees[1:]):
            if apres["montant"] < avant["montant"] - 0.005:
                erreurs.append(f"{nom} {apres['date']} : {apres['montant']:.2f} €, moins "
                               f"que {avant['montant']:.2f} € au {avant['date']}")
    lus = {f"{nom}|{ligne['date']}": ligne["montant"]
           for nom, lignes in series.items() for ligne in lignes}
    for cle, francs in REPERES_EN_FRANCS.items():
        lu, attendu = lus.get(cle), francs / FRANCS_PAR_EURO
        if lu is None or abs(lu - attendu) > 0.005:
            erreurs.append(f"{cle} : attendu {attendu:.2f} €, lu {lu}")
    jour, attendu = MINIMUM_2006
    somme = en_vigueur(series["avts"])(jour) + en_vigueur(series["as_seul"])(jour)
    if abs(somme - attendu) > 0.005:
        erreurs.append(f"minimum vieillesse au {jour} : {somme:.2f} €, D. 815-1 écrit "
                       f"{attendu:.2f} €")
    for annee, seuil in seuil_trimestre(series["avts"]).items():
        publie = (bareme.get(annee) or {}).get("metropole")
        if publie is None:
            erreurs.append(f"seuil {annee} : absent du barème")
        elif abs(publie - seuil) > 0.005:
            if annee < PREMIERE_ANNEE_AVTS:
                ecarts.append(f"seuil {annee} : le barème porte {publie * FRANCS_PAR_EURO * 100:.0f} "
                              f"anciens francs, R. 351-9 en écrit 1 800 ; le texte l'emporte")
            else:
                erreurs.append(f"seuil {annee} : le barème porte {publie:.4f} €, le quart "
                               f"de l'AVTS au 1er janvier vaut {seuil:.4f} €")
    smic = _serie_du_depot("macro/smic_horaire.csv", "smic_horaire")
    heures = _serie_du_depot("legislation/validation_trimestres.csv", "heures")
    for annee, publie in sorted(bareme.items()):
        if annee < 1972 or annee not in smic or publie["metropole"] is None:
            continue
        nombre = heures[max(a for a in heures if a <= annee)]
        if abs(publie["metropole"] - nombre * smic[annee]) > 0.01:
            erreurs.append(f"seuil {annee} : le barème porte {publie['metropole']:.2f} €, "
                           f"{nombre:.0f} SMIC horaires du dépôt font "
                           f"{nombre * smic[annee]:.2f} €")
    return erreurs, ecarts


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
    series = lire_datees(contenus)
    bareme = lire_seuils(contenus[SEUIL])
    erreurs, ecarts = controler(series, bareme)
    if erreurs:
        print("Barèmes refusés :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    seuils = seuil_trimestre(series["avts"])
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": " ; ".join(API.format(nom) for nom in BAREMES),
        "recupere_le": date.today().isoformat(),
        "note": "L'allocation aux vieux travailleurs salariés, l'allocation "
                "supplémentaire (un et deux allocataires) et son plafond de "
                "ressources (personne seule, couple), en euros, à chaque date des "
                "barèmes (datee) et au 31 décembre de chaque année (serie_*) ; le "
                "seuil d'un trimestre de 1946 à 1971 que R. 351-9 définit "
                "(seuil_trimestre) ; le barème des seuils tel que la caisse le "
                "publie, outre-mer compris (bareme_seuil).",
        "datee": {f"{nom}|{ligne['date']}": round(ligne["montant"], 6)
                  for nom, lignes in series.items()
                  for ligne in sorted(lignes, key=lambda l: l["date"])},
        "references": {f"{nom}|{ligne['date']}": ligne["reference"]
                       for nom, lignes in series.items()
                       for ligne in sorted(lignes, key=lambda l: l["date"])},
        **{f"serie_{nom}": {str(a): round(v, 6)
                            for a, v in sorted(ancres_annuelles(lignes).items())}
           for nom, lignes in series.items()},
        # Neuf décimales : un salaire qui tombe pile sur le seuil, 180,95 F en
        # 1962, doit le valider, et six décimales d'euro arrondies au-dessus
        # l'en empêchaient.
        "seuil_trimestre": {str(a): round(v, 9) for a, v in sorted(seuils.items())},
        "bareme_seuil": {str(a): {zone: None if v is None else round(v, 6)
                                  for zone, v in valeurs.items()}
                         for a, valeurs in sorted(bareme.items())},
        "ecarts": ecarts,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{sum(len(l) for l in series.values())} montants datés lus, "
          f"{len(seuils)} seuils de R. 351-9 écrits dans {SORTIE.relative_to(RACINE)}")
    for ecart in ecarts:
        print(f"  écart : {ecart}")
    for annee, seuil in sorted(seuils.items()):
        print(f"  {annee} : {seuil * FRANCS_PAR_EURO:9.2f} F le trimestre, {seuil:.4f} €")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
