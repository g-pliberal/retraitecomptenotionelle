#!/usr/bin/env python3
"""Coefficients de revalorisation des pensions servies, par la Cnav.

    python scripts/fetch/cnav_revalorisation_pensions.py
    python scripts/fetch/cnav_revalorisation_pensions.py --fichier bareme.json

À QUOI ILS SERVENT. Le simulateur calcule une pension à la LIQUIDATION. Pour
qui est déjà parti, ce n'est pas le montant qu'il touche : sa pension a été
revalorisée depuis, date d'effet après date d'effet, et pas sur les prix. Le
gel de 2014, le 0,3 % de 2019, les cinq coefficients de 2020 selon le montant
total de la retraite, les 4 % anticipés du 1er juillet 2022 : aucun ne se lit
dans l'indice des prix, et c'est pourtant ce qui sépare la pension du départ,
ramenée en euros d'aujourd'hui, de celle que le retraité voit sur son relevé
bancaire. Ces coefficients disent la seconde.

LA SOURCE. La Cnav sert, depuis sa base de législation, le barème
« Coefficients de revalorisation des retraites » : toutes les dates d'effet
depuis le 1er janvier 1949, chacune avec son coefficient et le texte qui l'a
fixé — arrêté, loi, puis circulaire de la caisse. C'est la caisse qui les
applique qui les publie, et le barème se lit par la même API publique que
``cnav_baremes_rci.py``.

Ce que le barème ne dit pas en toutes lettres, et que le script lui fait dire :

* LES ANNÉES SANS REVALORISATION n'ont pas de ligne. 2014 (gel), 2016 (un
  coefficient de 1,000) et 2018 (la date d'effet passe du 1er octobre au
  1er janvier suivant) sont absentes, et c'est exact : un coefficient
  manquant vaut un.
* 2020 N'A PAS UN COEFFICIENT MAIS CINQ, selon le montant total brut mensuel
  des retraites de base et complémentaires du mois précédent (loi n° 2019-1446,
  art. 81). Le barème les publie dans un tableau à part, sans date : le script
  les date du 1er janvier 2020 et écrit leurs bornes en euros par mois.

Statut de fiabilité : ``haute``, jamais ``certifiee``. Comme pour les
coefficients des salaires portés au compte, la caisse transcrit ce que
l'arrêté, la loi de financement ou l'instruction interministérielle ont fixé ;
les textes de 2019, 2020 et 2026 ont été relus dans l'index DILA du dépôt, et
``tests/test_revalorisation.py`` recoupe le barème avec la colonne des salaires
portés au compte là où les deux coefficients sont, en droit, le même.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
API = ("https://legislation.lassuranceretraite.fr/api/v1/baremes/"
       "baremesByFileLeafRef/{}.aspx")
BAREME = "revalorisation_coefficient_revalorisation_retraite_bar"
SORTIE = RACINE / "data" / "reference" / "legislation" / "revalorisation_pensions.csv"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Bornes de plausibilité d'un coefficient : jamais une baisse, et rien au-delà
#: des 20 % du 1er avril 1953, le plus fort de la série.
COEFFICIENT_MINIMAL = 1.0
COEFFICIENT_MAXIMAL = 1.25

#: Trois repères que le script exige de retrouver, chacun lu ailleurs que dans
#: ce barème : la circulaire Cnav 2025/29 pour 2026 (registre de veille), la loi
#: « pouvoir d'achat » pour juillet 2022, la loi de financement pour 2019.
REPERES = {
    "2026-01-01": 1.009,
    "2022-07-01": 1.04,
    "2019-01-01": 1.003,
}

#: La date d'effet des cinq coefficients de 2020, que leur tableau ne porte pas.
EFFET_2020 = "2020-01-01"

ENTETE = """\
# Coefficients de revalorisation des pensions de vieillesse servies
# -----------------------------------------------------------------
# source_id: cnav_revalorisation_pensions
#
# Fichier écrit par scripts/fetch/cnav_revalorisation_pensions.py :
# ne pas modifier à la main.
#
# UNE LIGNE PAR DATE D'EFFET, telle que la Cnav la publie dans son barème
# « Coefficients de revalorisation des retraites » : le coefficient multiplie
# toute pension du régime général ayant pris effet AVANT cette date. C'est la
# règle de l'article L. 161-23-1 du code de la sécurité sociale, que suivent
# aussi les régimes alignés, les deux régimes agricoles et, par renvoi de
# l'article L. 16 de leur code, les pensions civiles et militaires depuis le
# 19 décembre 2008 (voir revalorisation_pensions_fonction_publique.csv pour
# les années d'avant).
#
# Une année sans ligne est une année sans revalorisation : 2014 (gel), 2016,
# 2018 (date d'effet reportée au 1er janvier 2019). Un coefficient manquant
# vaut un.
#
# 2020 porte CINQ lignes, selon le montant total brut mensuel des retraites de
# base et complémentaires du mois précédent (loi n° 2019-1446, art. 81) :
# `mensuel_superieur_a` exclu, `mensuel_au_plus` inclus, en euros par mois.
# Vides ailleurs.
#
# fiabilite : `haute`. Le barème est la publication de la caisse, non le
# Journal officiel : il transcrit l'arrêté, la loi ou l'instruction qu'il cite.
"""


def _texte(fragment: str) -> str:
    """Le texte d'un morceau de HTML, sans balises ni espaces invisibles."""
    brut = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"[\s​﻿]+", " ", brut).strip()


def _nombre(texte: str) -> float:
    return float(re.search(r"\d+(?:,\d+)?", texte).group(0).replace(",", "."))


def _euros(texte: str) -> float:
    """« 2 014 € » → 2014.0 : l'espace sépare les milliers."""
    return float(re.sub(r"\s", "", texte))


def _lignes(contenu: str) -> list[list[str]]:
    return [
        [_texte(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", ligne, flags=re.S)]
        for ligne in re.findall(r"<tr[^>]*>(.*?)</tr>", contenu, flags=re.S)
    ]


def lire(contenu: str) -> list[dict]:
    """Les lignes du barème : dates d'effet, puis les cinq tranches de 2020."""
    lignes: list[dict] = []
    for cellules in _lignes(contenu):
        if len(cellules) < 2:
            continue
        date_effet = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", cellules[0])
        if date_effet:
            jour, mois, annee = date_effet.groups()
            lignes.append({
                "date_effet": f"{annee}-{mois}-{jour}",
                "coefficient": _nombre(cellules[1]),
                "mensuel_superieur_a": None,
                "mensuel_au_plus": None,
                "reference": cellules[2] if len(cellules) > 2 else "",
            })
            continue
        # Les tranches de 2020 : « Inférieur ou égal à 2 000 € », « Supérieur à
        # 2 000 € et inférieur ou égal à 2 008 € », « Supérieur à 2 014 € ».
        libelle = cellules[0]
        superieur = re.search(r"Sup[ée]rieur à ([\d\s]+)€", libelle)
        au_plus = re.search(r"[Ii]nf[ée]rieur ou égal à ([\d\s]+)€", libelle)
        if (superieur or au_plus) and re.fullmatch(r"\d+,\d+", cellules[1]):
            lignes.append({
                "date_effet": EFFET_2020,
                "coefficient": _nombre(cellules[1]),
                "mensuel_superieur_a": _euros(superieur.group(1)) if superieur else None,
                "mensuel_au_plus": _euros(au_plus.group(1)) if au_plus else None,
                "reference": "Loi n° 2019-1446 du 24/12/2019, art. 81 ; "
                             "circulaire Cnav 2020/9 du 04/02/2020",
            })
    return lignes


def controler(lignes: list[dict]) -> list[str]:
    """Ce qui ferait d'une lecture de travers une série fausse sans bruit."""
    erreurs = []
    datees = [l for l in lignes if l["mensuel_superieur_a"] is None
              and l["mensuel_au_plus"] is None]
    tranches = [l for l in lignes if l not in datees]
    dates = [l["date_effet"] for l in datees]
    if len(dates) != len(set(dates)):
        erreurs.append("une date d'effet apparaît deux fois")
    if EFFET_2020 in dates:
        erreurs.append("2020 porte à la fois une ligne datée et des tranches")
    if min(dates, default="9999") > "1949-01-01":
        erreurs.append("la série ne remonte pas au 1er janvier 1949")
    for ligne in lignes:
        if not COEFFICIENT_MINIMAL <= ligne["coefficient"] <= COEFFICIENT_MAXIMAL:
            erreurs.append(f"{ligne['date_effet']} : coefficient {ligne['coefficient']} "
                           "hors des bornes plausibles")
    for effet, attendu in REPERES.items():
        lu = next((l["coefficient"] for l in datees if l["date_effet"] == effet), None)
        if lu is None or abs(lu - attendu) > 1e-9:
            erreurs.append(f"{effet} : attendu {attendu}, lu {lu}")
    # Les cinq tranches de 2020 se suivent sans trou ni recouvrement, de la
    # première, ouverte en bas, à la dernière, ouverte en haut ; et le
    # coefficient ne peut que baisser quand la pension monte.
    tranches.sort(key=lambda l: (l["mensuel_superieur_a"] or 0.0))
    if len(tranches) != 5:
        erreurs.append(f"2020 : {len(tranches)} tranches lues, cinq attendues")
    elif (tranches[0]["mensuel_superieur_a"] is not None
          or tranches[-1]["mensuel_au_plus"] is not None
          or any(a["mensuel_au_plus"] != b["mensuel_superieur_a"]
                 for a, b in zip(tranches, tranches[1:]))
          or any(a["coefficient"] <= b["coefficient"]
                 for a, b in zip(tranches, tranches[1:]))):
        erreurs.append("2020 : les tranches ne se suivent pas, ou le coefficient "
                       "ne décroît pas avec la pension")
    return erreurs


def ecrire(lignes: list[dict]) -> str:
    """Le fichier de référence, de la date d'effet la plus ancienne à la plus récente."""
    flux = io.StringIO()
    flux.write(ENTETE)
    ecrivain = csv.writer(flux, lineterminator="\n")
    ecrivain.writerow(["date_effet", "coefficient", "mensuel_superieur_a",
                       "mensuel_au_plus", "reference", "fiabilite"])
    for ligne in sorted(lignes, key=lambda l: (l["date_effet"],
                                               l["mensuel_superieur_a"] or 0.0)):
        ecrivain.writerow([
            ligne["date_effet"], f"{ligne['coefficient']:g}",
            "" if ligne["mensuel_superieur_a"] is None else f"{ligne['mensuel_superieur_a']:g}",
            "" if ligne["mensuel_au_plus"] is None else f"{ligne['mensuel_au_plus']:g}",
            ligne["reference"], "haute",
        ])
    return flux.getvalue()


def telecharger() -> str:
    requete = urllib.request.Request(API.format(BAREME), headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return json.loads(reponse.read().decode("utf-8"))["contenu"]


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument(
        "--fichier", type=Path,
        help="réponse JSON de l'API déjà téléchargée, lue au lieu du réseau",
    )
    arguments = analyseur.parse_args(argv)
    contenu = (json.loads(arguments.fichier.read_text(encoding="utf-8"))["contenu"]
               if arguments.fichier else telecharger())
    lignes = lire(contenu)
    erreurs = controler(lignes)
    if erreurs:
        print("Barème refusé :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    SORTIE.write_text(ecrire(lignes), encoding="utf-8")
    print(f"{len(lignes)} lignes écrites dans {SORTIE.relative_to(RACINE)}, "
          f"lues le {date.today().isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
