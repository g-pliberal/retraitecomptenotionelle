#!/usr/bin/env python3
"""La population au 1er janvier par sexe, âge et état matrimonial légal, chez l'INSEE.

    python scripts/fetch/insee_etat_matrimonial.py
    python scripts/fetch/insee_etat_matrimonial.py --fichier ~/Téléchargements/irsocsd2021_t6_fe.xlsx

L'INSEE (« La situation démographique en 2021 », pyramide des âges par état
matrimonial, tableau 6) estime au 1er janvier de chaque année la population
de la France, Mayotte comprise, par sexe, âge et état matrimonial légal :
célibataires, mariés, veufs, divorcés ; jusqu'à 89 ans âge par âge, puis à 90
ans ou plus ensemble. Les feuilles de 1991 à 2005 n'ont que les totaux ; celles
de 2006 à 2020, les quatre états.

CE QUE LE DÉPÔT EN REPREND
--------------------------
Les quatre états de chaque sexe, de 60 à 89 ans et à 90 ans ou plus, de 2006 à
2020, tels que le classeur les écrit. Rien n'est dérivé.

À QUOI ÇA SERT
--------------
À dire qui, parmi les personnes qui ne vivent pas en couple, est veuf, et
touche donc une réversion qui compte dans ses ressources : la population de
``scripts/grille_large.py`` ne porte que des droits directs, et l'ASPA
regarde toutes les ressources (``scripts/recours_aspa.py``, action 138,
étape 14).
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

URL = "https://www.insee.fr/fr/outil-interactif/2418114/xls/irsocsd2021_t6_fe.xlsx"
RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "reference" / "macro" / "etat_matrimonial.csv"
ANNEES = range(2006, 2021)
AGES = range(60, 90)
ETATS = ("celibataire", "marie", "veuf", "divorce")

ENTETE = """\
# La population au 1er janvier par sexe, âge et état matrimonial légal
# source_id: insee_etat_matrimonial
# unite: personnes, au 1er janvier
# fiabilite:
#   haute : valeur publiée, lue telle quelle dans le tableau 6 de « La
#           situation démographique en 2021 » de l'INSEE
#           (`irsocsd2021_t6_fe.xlsx`, France y compris Mayotte) par
#           scripts/fetch/insee_etat_matrimonial.py. Les quatre états
#           somment, âge par âge, à la population que le modèle lit
#           (population_par_age.csv, tests/test_recours_aspa.py).
#
# age : de 60 à 89 ans, puis 90_plus, 90 ans ou plus, que l'INSEE ne
#   détaille pas par âge ; etat : celibataire, marie, veuf, divorce ;
#   l'état légal, non la vie en couple que le recensement mesure.
#
# À QUOI CETTE SÉRIE SERT
# ------------------------
# À dire qui, parmi les personnes qui ne vivent pas en couple, est veuf, et
# touche une réversion que l'ASPA compte dans ses ressources : la population
# de scripts/grille_large.py ne porte que des droits directs
# (scripts/recours_aspa.py, action 138, étape 14).
#
# Ne pas modifier à la main : le script réécrit le fichier en entier.
"""


def _telecharger(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as reponse:
        return reponse.read()


def _entier(valeur: float | str) -> int | None:
    """Un âge écrit en nombre ou en texte (« 55 ») ; ``None`` pour un libellé."""
    if isinstance(valeur, float):
        return int(valeur)
    texte = valeur.strip()
    return int(texte) if texte.isdigit() else None


def _onze(cellules: dict[int, float | str], depuis: int) -> list[int] | None:
    """Les onze effectifs de la ligne à partir de la colonne ``depuis`` —
    l'ensemble, puis le total et les quatre états de chaque sexe —, ou
    ``None`` s'il en manque un (« . » au-delà de 89 ans)."""
    valeurs = [cellules.get(colonne) for colonne in range(depuis, depuis + 11)]
    if not all(isinstance(v, float) for v in valeurs):
        return None
    return [int(v) for v in valeurs]


def extraire(donnees: bytes) -> list[dict]:
    grilles = feuilles(donnees, tuple(str(annee) for annee in ANNEES))
    sortie = []
    for annee in ANNEES:
        grille = grilles.get(str(annee))
        if grille is None:
            raise LookupError(f"feuille « {annee} » absente du classeur")
        lignes: dict[int, dict[int, float | str]] = {}
        for (ligne, colonne), valeur in grille.items():
            lignes.setdefault(ligne, {})[colonne] = valeur
        lus: dict[str, list[int]] = {}
        for cellules in lignes.values():
            libelles = [str(cellules.get(c, "")) for c in (0, 1)]
            plus = next((c for c, texte in enumerate(libelles)
                         if texte.strip().startswith("90") and "plus" in texte), None)
            if plus is not None:
                # Les effectifs commencent à la première colonne remplie après
                # le libellé : la deuxième jusqu'en 2012, la première ensuite.
                debut = min((c for c, v in cellules.items()
                             if c > plus and isinstance(v, float)), default=None)
                onze = None if debut is None else _onze(cellules, debut)
                if onze is not None:
                    lus["90_plus"] = onze
                continue
            age = _entier(cellules.get(1, ""))
            if age is not None and age in AGES:
                onze = _onze(cellules, 2)
                if onze is not None:
                    lus[str(age)] = onze
        if len(lus) != len(AGES) + 1:
            raise ValueError(f"{annee} : {len(lus)} âges lus, {len(AGES) + 1} attendus")
        for age, (ensemble, hommes, *reste) in lus.items():
            etats_h, femmes, etats_f = reste[:4], reste[4], reste[5:]
            if sum(etats_h) != hommes or sum(etats_f) != femmes or hommes + femmes != ensemble:
                raise ValueError(f"{annee}, {age} ans : les états ne somment pas aux totaux")
            for sexe, etats in (("H", etats_h), ("F", etats_f)):
                for etat, effectif in zip(ETATS, etats):
                    sortie.append({"annee": annee, "age": age, "sexe": sexe, "etat": etat,
                                   "effectif": effectif, "fiabilite": "haute"})
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
    colonnes = ["annee", "age", "sexe", "etat", "effectif", "fiabilite"]
    with SORTIE.open("w", encoding="utf-8") as flux:
        flux.write(ENTETE)
        flux.write(f"# recupere_le: {date.today().isoformat()}\n")
        flux.write(",".join(colonnes) + "\n")
        for ligne in valeurs:
            flux.write(",".join(str(ligne[c]) for c in colonnes) + "\n")
    veuves = {(l["annee"], l["age"]): l["effectif"] for l in valeurs
              if l["sexe"] == "F" and l["etat"] == "veuf"}
    femmes = {}
    for l in valeurs:
        if l["sexe"] == "F":
            femmes[(l["annee"], l["age"])] = femmes.get((l["annee"], l["age"]), 0) + l["effectif"]
    derniere = max(ANNEES)
    print(f"\n{len(valeurs)} lignes écrites dans {SORTIE.relative_to(RACINE)}")
    print(f"Veuves en {derniere} : {veuves[(derniere, '70')] / femmes[(derniere, '70')]:.1%} "
          f"des femmes de 70 ans, {veuves[(derniere, '90_plus')] / femmes[(derniere, '90_plus')]:.1%} "
          "de celles de 90 ans ou plus")
    return 0


if __name__ == "__main__":
    sys.exit(main())
