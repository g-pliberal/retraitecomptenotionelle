#!/usr/bin/env python3
"""Les taux de remplacement et le patrimoine retraite que l'OCDE publie pour la France.

    python scripts/fetch/ocde_pensions.py
    python scripts/fetch/ocde_pensions.py --fichier pag_fra.csv

POURQUOI CE TÉMOIN. *Pensions at a Glance* projette, pays par pays, la
retraite d'un salarié entré à 22 ans en 2024 — né en 2002 — qui cotise toute
sa carrière à un multiple constant du salaire moyen et part à l'âge normal de
son pays, 65 ans pour la France. Elle en publie le taux de remplacement brut
et net, à la moitié, à une fois et à deux fois le salaire moyen, et le
patrimoine retraite : la valeur, au départ, des pensions qu'il touchera,
actualisées à 1,5 % réel sur une mortalité de cohorte de l'ONU, en années de
son salaire. C'est un calcul fait par d'autres, sous des hypothèses publiées
— prix à +2 %, salaires réels à +1,25 % —, que le dépôt refait sous les mêmes
(``hypotheses_projection.yaml``, jeu ``ocde_2025``) :
``tests/test_cycle_de_vie_references.py`` s'y confronte.

LA SOURCE. L'API SDMX de l'OCDE, flux ``DSD_PAG@DF_PAG`` (*Pensions at a
Glance 2025*), France, toutes dimensions : le registre des modèles l'a lu le
4 octobre 2026 (``modeles_ocde``), et ses tableaux 4.1, 4.4, 4.6 et 5.4 en
sont tirés. Le site de l'OCDE refuse les robots ; l'API, non.

Le témoin est versionné : les tests le relisent sans réseau.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
URL = ("https://sdmx.oecd.org/public/rest/data/OECD.ELS.SPD,DSD_PAG@DF_PAG,"
       "/FRA......?dimensionAtObservation=AllDimensions")
SORTIE = RACINE / "tests" / "temoins" / "ocde_pensions.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)",
           "Accept": "application/vnd.sdmx.data+csv; charset=utf-8"}

#: Les mesures retenues, et ce que chacune désigne dans le témoin. Les taux
#: sont en pour cent, comme l'OCDE les publie ; le patrimoine en années de
#: salaire individuel.
MESURES = {
    "GPRR50": ("taux_remplacement_brut", "0.5"),
    "GPRR100": ("taux_remplacement_brut", "1"),
    "GPRR200": ("taux_remplacement_brut", "2"),
    "NPRR50": ("taux_remplacement_net", "0.5"),
    "NPRR100": ("taux_remplacement_net", "1"),
    "NPRR200": ("taux_remplacement_net", "2"),
    "GPW50": ("patrimoine_brut", "0.5"),
    "GPW100": ("patrimoine_brut", "1"),
    "GPW200": ("patrimoine_brut", "2"),
    "NPW50": ("patrimoine_net", "0.5"),
    "NPW100": ("patrimoine_net", "1"),
    "NPW200": ("patrimoine_net", "2"),
}
SEXES = {"M": "hommes", "F": "femmes"}
#: L'année de la publication : celle de l'entrée dans la carrière simulée.
ANNEE = "2024"


def extraire(texte: str) -> dict:
    """Le CSV de l'API, réduit à ce que le témoin garde."""
    temoin: dict = {"salaire_moyen": None, "age_de_depart": {}}
    for ligne in csv.DictReader(io.StringIO(texte)):
        mesure, sexe, periode = ligne["MEASURE"], ligne["SEX"], ligne["TIME_PERIOD"]
        valeur = float(ligne["OBS_VALUE"])
        if periode != ANNEE:
            continue
        if mesure in MESURES:
            # L'OCDE publie les taux deux fois, pour les régimes obligatoires
            # et pour les régimes obligatoires et volontaires : en France,
            # c'est le même nombre.
            nom, multiple = MESURES[mesure]
            temoin.setdefault(nom, {}).setdefault(SEXES[sexe], {})[multiple] = valeur
        elif mesure == "AWGW" and ligne["UNIT_MEASURE"] == "XDC":
            temoin["salaire_moyen"] = valeur
        elif mesure in ("CRPLF22", "FRPLF22") and sexe in SEXES:
            cle = "actuel" if mesure == "CRPLF22" else "futur"
            temoin["age_de_depart"].setdefault(cle, {})[SEXES[sexe]] = valeur
    return temoin


def controler(temoin: dict) -> list[str]:
    erreurs = []
    for nom in ("taux_remplacement_brut", "patrimoine_brut"):
        for sexe in SEXES.values():
            if sorted(temoin.get(nom, {}).get(sexe, {})) != ["0.5", "1", "2"]:
                erreurs.append(f"{nom}, {sexe} : incomplet")
    if not temoin.get("salaire_moyen"):
        erreurs.append("salaire moyen absent")
    if temoin.get("age_de_depart", {}).get("futur", {}).get("hommes") is None:
        erreurs.append("âge de départ d'une carrière entrée en 2024 absent")
    return erreurs


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--fichier", type=Path,
                           help="CSV de l'API déjà téléchargé, lu au lieu du réseau")
    arguments = analyseur.parse_args(argv)
    if arguments.fichier:
        texte = arguments.fichier.read_text(encoding="utf-8")
    else:
        try:
            requete = urllib.request.Request(URL, headers=ENTETES)
            with urllib.request.urlopen(requete, timeout=300) as reponse:
                texte = reponse.read().decode("utf-8")
        except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
            print(f"OCDE indisponible : {erreur}", file=sys.stderr)
            return 1
    temoin = extraire(texte)
    erreurs = controler(temoin)
    if erreurs:
        print("Réponse refusée :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    temoin = {
        "source": {
            "editeur": "OCDE",
            "reference": "Pensions at a Glance 2025, tableaux 4.1, 4.4, 4.6 et 5.4 ; "
                         "hypothèses p. 160-161",
            "url": URL,
            "lu_le": "2026-10-07",
        },
        "conventions": {
            "carriere": ("entrée à 22 ans en 2024 (génération 2002), carrière complète "
                         "au même multiple du salaire moyen, départ à l'âge normal"),
            "multiples": "0.5, 1 et 2 fois le salaire moyen (AWGW, en euros de 2024)",
            "taux": "en pour cent du salaire individuel brut (net) d'avant le départ",
            "patrimoine": ("valeur au départ des pensions des régimes obligatoires, "
                           "actualisées à 1,5 % réel sur la mortalité de cohorte de "
                           "l'ONU, en années de salaire individuel brut (net)"),
            "hypotheses": "prix +2 % par an, salaires réels +1,25 % par an",
        },
        **temoin,
    }
    # Les clés rangées : l'API ne rend pas ses lignes dans un ordre fixe.
    SORTIE.write_text(json.dumps(temoin, ensure_ascii=False, indent=1, sort_keys=True)
                      + "\n", encoding="utf-8")
    print(f"Témoin écrit dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
