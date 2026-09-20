#!/usr/bin/env python3
"""Le mode de résidence des 65 ans et plus, âge par âge et par sexe, chez l'INSEE.

    python scripts/fetch/insee_vie_en_couple.py
    python scripts/fetch/insee_vie_en_couple.py --fichier ~/Téléchargements/ip2040.xlsx

L'*Insee Première* n° 2040 (« En 2021, une personne de 65 ans ou plus sur trois
vit seule dans son logement », recensement de la population 2021) publie, dans
sa figure 2, la part des personnes de chaque âge vivant EN COUPLE, SEULES, avec
des proches ou hors logement ordinaire, par sexe, en 1990 et en 2021.

CE QUE LE DÉPÔT EN REPREND
--------------------------
Les parts de 2021, en couple et seul(e)s, âge par âge et par sexe, telles que
le classeur les écrit. Rien n'est dérivé.

À QUOI ÇA SERT
--------------
À la reprise sur succession de la garantie vieillesse (action 47) : un couple
de deux bénéficiaires pèse DEUX avances sur UNE succession, et c'est la
succession du survivant — presque toujours la femme — qui les porte toutes les
deux. Sans cette part, le modèle confrontait chaque avance au patrimoine d'un
ménage entier, et surestimait ce que les successions couvrent.
"""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_xlsx import feuilles  # noqa: E402
from source_locale import lire_ou_telecharger, option_fichier  # noqa: E402

URL = "https://www.insee.fr/fr/statistiques/fichier/8349408/ip2040.xlsx"
RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "reference" / "macro" / "vie_en_couple.csv"
FEUILLE = "Figure 2"
#: Colonne de la figure 2 -> (mode, sexe). Les colonnes 3, 4, 7 et 8 portent
#: 1990, que le dépôt ne reprend pas.
COLONNES = {1: ("couple", "F"), 2: ("couple", "H"), 5: ("seul", "F"), 6: ("seul", "H")}
ANNEE = 2021

ENTETE = """\
# Mode de résidence des personnes de 65 ans et plus, par âge et par sexe
# source_id: insee_vie_en_couple
# unite: pour cent des personnes de cet âge et de ce sexe
# mode: couple | seul
# annee: 2021 (recensement de la population)
# fiabilite:
#   haute : valeur publiée, lue telle quelle dans le classeur `ip2040.xlsx` de
#           l'*Insee Première* n° 2040 par scripts/fetch/insee_vie_en_couple.py.
#           Aucune certification ne la recontrôle par un second chemin.
#
# À QUOI CETTE SÉRIE SERT
# ------------------------
# À la reprise sur succession de la garantie vieillesse (action 47) : deux
# bénéficiaires en couple laissent DEUX avances sur UNE succession, celle du
# survivant, et une avance deux fois plus grosse est bien moins couverte par
# un patrimoine donné. `cout._reprises_successions` en tire le nombre moyen
# d'avances par succession.
#
# Ne pas modifier à la main : le script réécrit le fichier en entier.
"""


def _telecharger(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as reponse:
        return reponse.read()


def extraire(donnees: bytes) -> list[dict]:
    grille = feuilles(donnees).get(FEUILLE)
    if grille is None:
        raise LookupError(f"feuille « {FEUILLE} » absente du classeur")
    lignes: dict[int, dict[int, float | str]] = {}
    for (ligne, colonne), valeur in grille.items():
        lignes.setdefault(ligne, {})[colonne] = valeur
    sortie = []
    for cellules in lignes.values():
        age = cellules.get(0)
        if not isinstance(age, (int, float)) or not 60 <= age <= 120:
            continue
        for colonne, (mode, sexe) in COLONNES.items():
            part = cellules.get(colonne)
            if isinstance(part, (int, float)):
                sortie.append({"annee": ANNEE, "age": int(age), "sexe": sexe,
                               "mode": mode, "part_pct": round(float(part), 1),
                               "fiabilite": "haute"})
    if len(sortie) < 100:
        raise ValueError(f"{len(sortie)} valeurs lues, plusieurs centaines attendues")
    return sortie


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    option_fichier(analyseur)
    options = analyseur.parse_args(argv)
    print(f"Source    {URL}")
    try:
        donnees = lire_ou_telecharger(URL, _telecharger, options.fichier)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as erreur:
        print(f"ÉCHEC   téléchargement : {erreur}", file=sys.stderr)
        return 1
    try:
        valeurs = extraire(donnees)
    except (LookupError, ValueError) as erreur:
        print(f"ÉCHEC   lecture du classeur : {erreur}", file=sys.stderr)
        return 1
    # Trois contrôles : les parts sont des pourcentages, couple et seul ne se
    # recouvrent pas, et les hommes vivent plus souvent en couple que les
    # femmes à tout âge — c'est l'écart d'espérance de vie, et l'écart d'âge.
    par_cle = {(l["age"], l["sexe"], l["mode"]): l["part_pct"] for l in valeurs}
    for (age, sexe, mode), part in par_cle.items():
        if not 0.0 <= part <= 100.0:
            print(f"ÉCHEC   part hors bornes : {part} ({age} ans, {sexe}, {mode})",
                  file=sys.stderr)
            return 1
    for age, sexe in {(a, s) for a, s, _ in par_cle}:
        total = par_cle.get((age, sexe, "couple"), 0.0) + par_cle.get((age, sexe, "seul"), 0.0)
        if total > 100.0:
            print(f"ÉCHEC   couple et seul somment à {total} % ({age} ans, {sexe})",
                  file=sys.stderr)
            return 1
    for age in {a for a, _, _ in par_cle}:
        if par_cle.get((age, "H", "couple"), 0.0) <= par_cle.get((age, "F", "couple"), 0.0):
            print(f"ÉCHEC   les femmes vivraient plus souvent en couple à {age} ans",
                  file=sys.stderr)
            return 1
    colonnes = ["annee", "age", "sexe", "mode", "part_pct", "fiabilite"]
    valeurs.sort(key=lambda l: (l["age"], l["sexe"], l["mode"]))
    with SORTIE.open("w", encoding="utf-8") as flux:
        flux.write(ENTETE)
        flux.write(f"# recupere_le: {date.today().isoformat()}\n")
        flux.write(",".join(colonnes) + "\n")
        for ligne in valeurs:
            flux.write(",".join(str(ligne[c]) for c in colonnes) + "\n")
    ages = sorted({a for a, _, _ in par_cle})
    print(f"\n{len(valeurs)} lignes écrites dans {SORTIE.relative_to(RACINE)}")
    print(f"En couple à 65 ans : femmes {par_cle[(65, 'F', 'couple')]} %, "
          f"hommes {par_cle[(65, 'H', 'couple')]} % ; à {ages[-1]} ans : "
          f"femmes {par_cle[(ages[-1], 'F', 'couple')]} %, "
          f"hommes {par_cle[(ages[-1], 'H', 'couple')]} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
