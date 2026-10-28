#!/usr/bin/env python3
"""Les allocataires du minimum vieillesse par âge, sexe et situation conjugale.

    python scripts/fetch/insee_allocataires_minimum_vieillesse.py
    python scripts/fetch/insee_allocataires_minimum_vieillesse.py --fichier ~/Téléchargements/reve-protec-alloc-mini-vieillesse.xlsx

L'INSEE (« Allocataires du minimum vieillesse », données annuelles de 2005 à
2024) reprend, au 31 décembre de chaque année, l'enquête de la DREES sur les
allocations du minimum vieillesse : les allocataires de l'allocation
supplémentaire (ASV) ou de l'Aspa, par tranche d'âge et par sexe, isolés, en
couple et ensemble, en milliers, France entière. La DREES publie la même
enquête sur son portail (``drees_minimum_vieillesse``), que la session qui
écrit ces lignes ne joignait pas.

CE QUE LE DÉPÔT EN REPREND
--------------------------
Les trois colonnes d'effectifs de chaque année, telles que le classeur les
écrit, au millier près à trois décimales ; la proportion d'allocataires dans
la population, qui s'en déduit, n'est pas reprise. Rien n'est dérivé.

À QUOI ÇA SERT
--------------
À rapporter les allocataires servis aux ayants droit que la population de
``scripts/grille_large.py`` compte, type de ménage par type de ménage, comme
Ines cale son recours (``scripts/recours_aspa.py``, action 138, étape 14).
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_xlsx import feuilles  # noqa: E402
from source_locale import lire_ou_telecharger, option_fichier  # noqa: E402

URL = "https://www.insee.fr/fr/statistiques/fichier/2407793/reve-protec-alloc-mini-vieillesse.xlsx"
RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "reference" / "macro" / "allocataires_minimum_vieillesse.csv"
FEUILLE = "Données"
#: Le libellé de chaque colonne d'effectifs, lu au début de son en-tête.
MENAGES = (("Isolés", "isoles"), ("En couple", "couple"), ("Ensemble", "ensemble"))
SEXES = {"Femmes": "F", "Hommes": "H"}

ENTETE = """\
# Les allocataires du minimum vieillesse au 31 décembre, par tranche d'âge,
# sexe et situation conjugale
# source_id: insee_allocataires_minimum_vieillesse
# unite: milliers d'allocataires de l'ASV ou de l'Aspa, au 31 décembre
# fiabilite:
#   haute : valeur publiée, lue telle quelle dans le classeur
#           `reve-protec-alloc-mini-vieillesse.xlsx` de l'INSEE, qui
#           reprend l'enquête de la DREES sur les allocations du minimum
#           vieillesse, par scripts/fetch/insee_allocataires_minimum_vieillesse.py.
#           Le total de 2024 est recoupé à celui que la DREES publie
#           (tests/test_recours_aspa.py).
#
# tranche : l'âge au 31 décembre ; 61-64, ceux qui pouvaient être
#   allocataires avant 65 ans — depuis la réforme de 2010, 61 ans au moins
#   en 2017, 62 depuis 2018 —, 90+, 90 ans ou plus.
# menage : isoles ; couple — pour l'ASV, les mariés seuls ; pour l'Aspa, les
#   mariés, pacsés et concubins — ; ensemble. Champ : France.
#
# À QUOI CETTE SÉRIE SERT
# ------------------------
# À rapporter les allocataires servis aux ayants droit que la population de
# scripts/grille_large.py compte, type de ménage par type de ménage, comme
# Ines cale son recours (scripts/recours_aspa.py, action 138, étape 14).
#
# Ne pas modifier à la main : le script réécrit le fichier en entier.
"""


def _telecharger(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as reponse:
        return reponse.read()


def tranche_de(libelle: str) -> str | None:
    """« 65-69 ans » donne 65-69, « 61-64 ans2 » (renvoi de note) 61-64,
    « 90 ans ou plus » 90+ ; la ligne d'ensemble, aucune."""
    texte = libelle.strip()
    if texte.startswith("90"):
        return "90+"
    trouve = re.match(r"(\d\d)-(\d\d) ans", texte)
    return f"{trouve.group(1)}-{trouve.group(2)}" if trouve else None


def _a_gauche(ligne: dict[int, float | str], colonne: int):
    """La dernière valeur de la ligne d'en-tête à gauche de la colonne, elle
    comprise : une cellule fusionnée n'écrit que sa première case."""
    return next((ligne[c] for c in range(colonne, -1, -1) if c in ligne), None)


def extraire(donnees: bytes) -> list[dict]:
    grille = feuilles(donnees, (FEUILLE,)).get(FEUILLE)
    if grille is None:
        raise LookupError(f"feuille « {FEUILLE} » absente du classeur")
    lignes: dict[int, dict[int, float | str]] = {}
    for (ligne, colonne), valeur in grille.items():
        lignes.setdefault(ligne, {})[colonne] = valeur
    rang_annees = next((rang for rang, cellules in sorted(lignes.items())
                        if str(cellules.get(0, "")).startswith("Tranche")), None)
    if rang_annees is None:
        raise LookupError("ligne des années introuvable")
    annees, menages, sexes = (lignes[rang_annees], lignes[rang_annees + 1],
                              lignes[rang_annees + 2])
    sortie = []
    for rang in sorted(lignes):
        if rang <= rang_annees + 2:
            continue
        cellules = lignes[rang]
        tranche = tranche_de(str(cellules.get(0, "")))
        if tranche is None:
            continue
        for colonne, valeur in cellules.items():
            if colonne == 0 or not isinstance(valeur, float):
                continue
            libelle = str(_a_gauche(menages, colonne) or "")
            menage = next((code for debut, code in MENAGES if libelle.startswith(debut)), None)
            sexe = SEXES.get(str(sexes.get(colonne, "")).strip())
            annee = _a_gauche(annees, colonne)
            if menage is None or sexe is None or not isinstance(annee, float):
                continue
            sortie.append({"annee": int(annee), "tranche": tranche, "sexe": sexe,
                           "menage": menage, "milliers": round(valeur, 3),
                           "fiabilite": "haute"})
    if len(sortie) < 800:
        raise ValueError(f"{len(sortie)} valeurs lues, plus de huit cents attendues")
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
    # Un contrôle : isolés et en couple somment à l'ensemble, à l'arrondi et à
    # la répartition près — trois cents allocataires au plus, de 2009 à 2017,
    # que l'enquête répartit et arrondit séparément ; dix depuis 2018.
    par_cle = {(l["annee"], l["tranche"], l["sexe"], l["menage"]): l["milliers"]
               for l in valeurs}
    ecart = 0.0
    for (annee, tranche, sexe, menage), ensemble in par_cle.items():
        if menage != "ensemble":
            continue
        somme = par_cle[(annee, tranche, sexe, "isoles")] + par_cle[(annee, tranche, sexe, "couple")]
        ecart = max(ecart, abs(somme - ensemble))
    if ecart > 0.31:
        print(f"ÉCHEC   isolés et en couple s'écartent de l'ensemble de {ecart} millier",
              file=sys.stderr)
        return 1
    colonnes = ["annee", "tranche", "sexe", "menage", "milliers", "fiabilite"]
    valeurs.sort(key=lambda l: (l["annee"], l["tranche"], l["sexe"], l["menage"]))
    with SORTIE.open("w", encoding="utf-8") as flux:
        flux.write(ENTETE)
        flux.write(f"# recupere_le: {date.today().isoformat()}\n")
        flux.write(",".join(colonnes) + "\n")
        for ligne in valeurs:
            flux.write(",".join(str(ligne[c]) for c in colonnes) + "\n")
    derniere = max(l["annee"] for l in valeurs)
    total = sum(v for (a, _, _, m), v in par_cle.items() if a == derniere and m == "ensemble")
    print(f"\n{len(valeurs)} lignes écrites dans {SORTIE.relative_to(RACINE)}")
    print(f"{derniere} : {total:.3f} milliers d'allocataires ; écart des sommes au plus "
          f"{ecart:.3f} millier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
