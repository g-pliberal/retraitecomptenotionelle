#!/usr/bin/env python3
"""Pension majorée de référence des non-salariés agricoles et son plafond, datés.

    python scripts/fetch/dila_index.py legi --recuperer        # l'index, une fois
    python scripts/fetch/dila_legi_pension_majoree.py          # écrit le fichier
    python scripts/fetch/dila_legi_pension_majoree.py --verifier

Le code rural ne porte que des ANCRES : la pension majorée de référence (PMR)
de D. 732-111 et le plafond de son écrêtement, D. 732-113, fixés à une date,
puis « revalorisés aux mêmes dates et dans les mêmes conditions que celles
prévues pour les pensions de vieillesse de base par l'article L. 161-23-1 ».
Aucune caisse ne publie la série entre deux ancres ; la loi la définit. Le
script la refait donc, date par date, de deux pièces que le dépôt certifie
déjà :

* les ancres, lues dans l'index LEGI du dépôt, chacune dans la version de
  l'article qui la fixe — le script refuse d'écrire si le texte ne redonne pas
  le montant au centime ;
* les coefficients de l'article L. 161-23-1, que la Cnav publie
  (``legislation/revalorisation_pensions.csv``), la tranche de 2020 étant celle
  des montants de moins de 2 000 € par mois, comme pour le minimum
  contributif (7 638,78 € portés à 7 715,16 €, soit 1 %).

Chaque revalorisation s'arrondit au centime INFÉRIEUR : c'est ce que font la
Cnav (le minimum majoré de 8 557,38 € porté à 8 899,67 € au 1er juillet 2022)
et la MSA (le plafond de 11 001,44 € porté à 11 441,49 € à la même date,
tableau de bord des retraites des non-salariés agricoles, août 2023). La série
se ferme sur l'ancre suivante, qui la remplace : le décret n° 2021-1919 relève
la PMR au minimum contributif majoré au 1er janvier 2022, plus haut que la
revalorisation ne l'aurait portée.

Pour les pensions prenant effet depuis le 1er septembre 2023, la PMR est
revalorisée comme le minimum contributif (L. 732-54-2 renvoie au dernier alinéa
de L. 351-10) et part du même montant, 10 170,86 € : elle VAUT le minimum
contributif majoré, que ``minimum_contributif.csv`` date. Son plafond, 12 732,96 €
au 1er septembre 2023, suit le SMIC « aux mêmes dates et dans les mêmes
proportions », comme le plafond de l'article L. 173-2 (D. 173-21-4) : le script
lui applique les rapports de celui-ci. Depuis 2026, le plafond EST celui de
l'article L. 173-2 (L. 732-54-3, 2°), que le modèle lit dans
``minimum_contributif.csv`` : ce fichier ne le répète pas.

Montants en euros PAR AN. Le fichier n'a besoin que des montants en vigueur à
une date d'effet : chaque mesure s'arrête où la version suivante de la règle
cesse de la lire.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sqlite3
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "reference" / "legislation" / "pension_majoree_reference.csv"
REVALORISATIONS = RACINE / "data" / "reference" / "legislation" / "revalorisation_pensions.csv"
MINIMUM = RACINE / "data" / "reference" / "legislation" / "minimum_contributif.csv"
INDEX = RACINE / "data" / "brut" / "dila" / "legi.sqlite"

#: Le montant mensuel qui choisit la tranche de 2020 : la PMR et son plafond
#: sont sous 2 000 € par mois.
MENSUEL_DES_MINIMA = 1_000.0

#: Les ancres : mesure, date, montant, article, version qui le fixe, et le
#: passage où le texte le dit.
ANCRES: tuple[tuple[str, str, float, str, str, str], ...] = (
    ("pmr_chef", "2009-01-01", 7596.00, "D. 732-111", "LEGIARTI000020254705",
     "PMR1 est égal à 7 596 euros au 1er janvier 2009"),
    ("pmr_chef", "2022-01-01", 8557.38, "D. 732-111", "LEGIARTI000044944271",
     "PMRmax est égal à 8 557,38 euros au 1er janvier 2022"),
    ("pmr_chef", "2023-01-01", 8970.86, "D. 732-111", "LEGIARTI000047961256",
     "PMRmax est égal à 8 970,86 euros au 1er janvier 2023"),
    ("pmr_conjoint", "2009-01-01", 6036.00, "D. 732-111", "LEGIARTI000020254705",
     "PMR2 est égal à 6 036 euros au 1er janvier 2009"),
    ("pmr_depuis_septembre_2023", "2023-09-01", 10170.86, "D. 732-111",
     "LEGIARTI000047961256", "PMRmax est égal à 10 170,86 euros au 1er septembre 2023"),
    ("plafond", "2009-01-01", 9000.00, "D. 732-113", "LEGIARTI000020254692",
     "fixé à 9 000 euros au 1er janvier 2009"),
    ("plafond", "2010-02-11", 9600.00, "D. 732-113", "LEGIARTI000021803611",
     "est fixé à 9 600 euros"),
    ("plafond", "2022-01-01", 11001.44, "D. 732-113", "LEGIARTI000044944264",
     "fixé à 11 001,44 euros au 1er janvier 2022"),
    ("plafond", "2023-01-01", 11533.02, "D. 732-113", "LEGIARTI000047961228",
     "fixé à 11 533,02 euros au 1er janvier 2023"),
    ("plafond_depuis_septembre_2023", "2023-09-01", 12732.96, "D. 732-113",
     "LEGIARTI000047961228", "fixé à 12 732,96 euros au 1er septembre 2023"),
)

#: Où chaque mesure s'arrête : la dernière date d'effet que la règle lui
#: confie (``data/reference/regles/pension_majoree_reference.yaml``).
FINS = {
    "pmr_chef": "2023-08-31",
    "pmr_conjoint": "2021-12-31",
    "plafond": "2023-08-31",
    "plafond_depuis_septembre_2023": "2025-12-31",
    "pmr_depuis_septembre_2023": "2026-12-31",
}


def _plancher(valeur: float) -> float:
    """Au centime inférieur, comme la caisse."""
    return math.floor(valeur * 100.0 + 1e-6) / 100.0


def _lignes(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def coefficients_l_161_23_1(chemin: Path = REVALORISATIONS) -> list[tuple[str, float]]:
    """Les revalorisations de l'article L. 161-23-1, date par date, la tranche
    de 2020 étant celle d'un montant de ``MENSUEL_DES_MINIMA`` par mois."""
    retenues = []
    for ligne in _lignes(chemin):
        bas = float(ligne["mensuel_superieur_a"]) if ligne["mensuel_superieur_a"] else None
        haut = float(ligne["mensuel_au_plus"]) if ligne["mensuel_au_plus"] else None
        if (bas is not None and MENSUEL_DES_MINIMA <= bas) or (
                haut is not None and MENSUEL_DES_MINIMA > haut):
            continue
        retenues.append((ligne["date_effet"], float(ligne["coefficient"])))
    return sorted(retenues)


def mesure_du_minimum(mesure: str, chemin: Path = MINIMUM) -> list[tuple[str, float, str]]:
    """Une mesure de ``minimum_contributif.csv`` : date, montant, fiabilité."""
    return sorted((l["date"], float(l["valeur"]), l["fiabilite"])
                  for l in _lignes(chemin) if l["mesure"] == mesure)


def serie(ancres=ANCRES, revalorisations=None, minimum_majore=None,
          plafond_l_173_2=None) -> list[tuple[str, str, float, str]]:
    """Les montants datés : (mesure, date, valeur, fiabilité).

    Une ancre est ``certifiee`` ; ce que la revalorisation en fait, ``moyenne``
    — le droit le définit, mais aucune caisse ne publie la série ; ce que le
    minimum contributif majoré date, au niveau du fichier qui le porte."""
    revalorisations = coefficients_l_161_23_1() if revalorisations is None else revalorisations
    minimum_majore = (mesure_du_minimum("montant_majore") if minimum_majore is None
                      else minimum_majore)
    plafond_l_173_2 = (mesure_du_minimum("plafond_ecretement") if plafond_l_173_2 is None
                       else plafond_l_173_2)
    lignes: list[tuple[str, str, float, str]] = []
    par_mesure: dict[str, list[tuple[str, float]]] = {}
    for mesure, jour, valeur, *_ in ancres:
        par_mesure.setdefault(mesure, []).append((jour, valeur))
    for mesure, datees in par_mesure.items():
        datees.sort()
        fin = FINS[mesure]
        for rang, (jour, valeur) in enumerate(datees):
            lignes.append((mesure, jour, valeur, "certifiee"))
            suivante = datees[rang + 1][0] if rang + 1 < len(datees) else None
            if mesure == "pmr_depuis_septembre_2023":
                # Le minimum contributif majoré, que la PMR vaut depuis.
                for date_m, montant, fiabilite in minimum_majore:
                    if jour < date_m <= fin:
                        lignes.append((mesure, date_m, montant, fiabilite))
                continue
            if mesure == "plafond_depuis_septembre_2023":
                # Les rapports du plafond de l'article L. 173-2, qui suit le
                # SMIC aux mêmes dates et dans les mêmes proportions.
                base = dict((d, v) for d, v, _ in plafond_l_173_2)[jour]
                for date_p, montant, _ in plafond_l_173_2:
                    if jour < date_p <= fin:
                        lignes.append((mesure, date_p,
                                       _plancher(valeur * montant / base), "moyenne"))
                continue
            courante = valeur
            for date_r, coefficient in revalorisations:
                if date_r <= jour or date_r > fin or (suivante is not None and date_r >= suivante):
                    continue
                courante = _plancher(courante * coefficient)
                lignes.append((mesure, date_r, courante, "moyenne"))
    return sorted(lignes)


def verifier_les_ancres(index: Path = INDEX) -> list[str]:
    """Les écarts entre les ancres et le texte des versions qui les fixent ;
    vide si chacune s'y lit."""
    if not index.exists():
        return [f"index LEGI absent : {index} (python scripts/fetch/dila_index.py legi --recuperer)"]
    ecarts = []
    with sqlite3.connect(index) as base:
        for mesure, jour, valeur, article, identifiant, passage in ANCRES:
            ligne = base.execute("SELECT texte FROM doc WHERE id = ?", (identifiant,)).fetchone()
            if ligne is None:
                ecarts.append(f"{mesure} {jour} : {identifiant} absent de l'index")
                continue
            texte = re.sub(r"[\s  ]+", " ", ligne[0])
            if passage not in texte:
                ecarts.append(f"{mesure} {jour} : « {passage} » introuvable dans "
                              f"{article} ({identifiant})")
    return ecarts


ENTETE = """\
# Pension majorée de référence des non-salariés agricoles et plafond de son écrêtement
# -------------------------------------------------------------------------------------
# source_id: dila_legi_pension_majoree (ancres de D. 732-111 et D. 732-113),
#            cnav_revalorisation_pensions
#
# Écrit par scripts/fetch/dila_legi_pension_majoree.py, qui relit chaque ancre
# dans l'index LEGI du dépôt et la revalorise par les coefficients de
# l'article L. 161-23-1 (revalorisation_pensions.csv), au centime inférieur :
# ne pas modifier à la main. Montants en euros PAR AN ; une ligne par date de
# revalorisation, le modèle lisant le montant en vigueur le premier jour du
# mois de la date d'effet.
#
#   pmr_chef     PMR1 (D. 732-111, 2009) : la part des chefs d'exploitation de
#                dix-sept ans et demi, puis, depuis 2022, la PMR unique
#                (PMRmax), relevée au minimum contributif majoré ; pour les
#                pensions prenant effet avant le 1er septembre 2023 ;
#   pmr_conjoint PMR2 : les autres périodes, jusqu'en 2021 ;
#   pmr_depuis_septembre_2023
#                PMRmax des pensions prenant effet depuis le 1er septembre
#                2023 : 10 170,86 €, revalorisée comme le minimum contributif,
#                qu'elle vaut ;
#   plafond      le plafond de l'écrêtement (D. 732-113), pour les pensions
#                prenant effet avant le 1er septembre 2023 ;
#   plafond_depuis_septembre_2023
#                celui des pensions prenant effet de septembre 2023 à 2025, qui
#                suit le SMIC comme le plafond de l'article L. 173-2. Depuis
#                2026, le plafond est celui-ci (L. 732-54-3, 2°) :
#                minimum_contributif.csv.
#
# Fiabilité : certifiee pour une ancre relue dans LEGI ; moyenne pour un
# montant que la loi définit et que le script calcule, aucune caisse n'en
# publiant la série ; celle de minimum_contributif.csv pour la PMR depuis
# septembre 2023.
"""


def ecrire(lignes, chemin: Path = SORTIE) -> None:
    with chemin.open("w", encoding="utf-8", newline="") as flux:
        flux.write(ENTETE)
        flux.write("mesure,date,valeur,fiabilite\n")
        for mesure, jour, valeur, fiabilite in lignes:
            flux.write(f"{mesure},{jour},{valeur:.2f},{fiabilite}\n")


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="dire si le fichier est à jour, sans l'écrire")
    analyseur.add_argument("--index", type=Path, default=INDEX, help="index LEGI du dépôt")
    options = analyseur.parse_args(arguments)
    ecarts = verifier_les_ancres(options.index)
    if ecarts:
        for ecart in ecarts:
            print(f"ÉCHEC   {ecart}", file=sys.stderr)
        return 1
    lignes = serie()
    if options.verifier:
        lues = [(l["mesure"], l["date"], float(l["valeur"]), l["fiabilite"])
                for l in _lignes(SORTIE)] if SORTIE.exists() else []
        if lues != lignes:
            print(f"PÉRIMÉ  {SORTIE.relative_to(RACINE)}", file=sys.stderr)
            return 1
        print(f"À JOUR  {SORTIE.relative_to(RACINE)} : {len(lignes)} montants")
        return 0
    ecrire(lignes)
    print(f"Écrit   {SORTIE.relative_to(RACINE)} : {len(lignes)} montants, "
          f"{len(ANCRES)} ancres relues dans LEGI")
    return 0


if __name__ == "__main__":
    sys.exit(main())
