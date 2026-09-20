#!/usr/bin/env python3
"""Le patrimoine des ménages, par décile et par âge, lu chez l'INSEE — et celui
des retraités par quartile de revenu, recopié du COR.

    python scripts/fetch/insee_patrimoine_menages.py
    python scripts/fetch/insee_patrimoine_menages.py --fichier ~/Téléchargements/if287.xlsx

L'INSEE publie, avec l'*Insee Focus* n° 287 (« Début 2021, 92 % des avoirs
patrimoniaux sont détenus par la moitié des ménages ») et sa page « Distribution
du patrimoine des ménages », deux classeurs de quelques kilo-octets : les
déciles de patrimoine brut et net de tous les ménages début 2021 et début
2024, et, pour 2021, les montants moyens et médians par âge de la personne de
référence. Source : enquête Histoire de vie et Patrimoine.

CE QUE LE DÉPÔT EN REPREND
--------------------------
Les déciles, les centiles 95 et 99, la moyenne et la médiane, brut et net, tels
que les classeurs les écrivent ; par âge pour 2021. Rien n'est dérivé.

ET CE QU'IL RECOPIE D'AILLEURS
------------------------------
L'INSEE ne publie pas le patrimoine des RETRAITÉS selon leur revenu. Le
secrétariat général du COR l'a fait, sur la vague 2018 de la même enquête,
dans le document n° 3 de la séance du 16 décembre 2021 (« Le patrimoine des
retraités ») : patrimoine brut hors reste des ménages dont la personne de
référence est retraitée — médiane, moyenne, deuxième et neuvième déciles —,
et, pour le quart de ces ménages au revenu disponible le plus bas, la médiane
et le rapport de la moyenne à la médiane, lu sur son graphique 7. Ces valeurs
sont SAISIES dans ce script, avec leur source, et écrites dans le même fichier
sous le `source_id` du COR : le document est un PDF que le site du COR sert,
et que `lecture_pdf.py` lit, mais ses graphiques ne se lisent pas.

À QUOI ÇA SERT
--------------
À la reprise sur succession de la garantie vieillesse (action 47) : ce qu'une
succession couvre de l'avance d'un bénéficiaire dépend du patrimoine des
retraités modestes, et ``donnees/patrimoine.py`` en tire une couverture au lieu
d'un réglage.
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

URL_FOCUS = "https://www.insee.fr/fr/statistiques/fichier/6689022/if287.xlsx"
URL_DECILES = "https://www.insee.fr/fr/statistiques/fichier/2388851/reve-patrim-decile.xlsx"
RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "reference" / "macro" / "patrimoine_menages.csv"

#: Libellé de ligne dans les classeurs -> statistique.
STATISTIQUES = {
    "1er décile": "d1", "2e décile": "d2", "3e décile": "d3", "4e décile": "d4",
    "Médiane": "mediane", "6e décile": "d6", "7e décile": "d7", "8e décile": "d8",
    "9e décile": "d9", "95e centile": "p95", "99e centile": "p99",
}
#: Libellé d'âge dans les figures 4 et 5 -> population.
AGES = {
    "Moins de 30 ans": "age_moins_30", "De 30 à 39 ans": "age_30_39",
    "De 40 à 49 ans": "age_40_49", "De 50 à 59 ans": "age_50_59",
    "De 60 à 69 ans": "age_60_69", "70 ans ou plus": "age_70_plus",
    "Ensemble": "ensemble",
}

#: Ce que le COR a publié sur la vague 2018, recopié : (population, statistique,
#: valeur en euros de 2018, patrimoine BRUT HORS RESTE).
SAISIES_COR = [
    ("retraites", "mediane", 190_200),
    ("retraites", "moyenne", 296_600),
    ("retraites", "d2", 23_000),
    ("retraites", "d9", 622_900),
    ("retraites_q1", "mediane", 36_800),
    # Le graphique 7 du document écrit « Moy/Méd = 3 » pour les retraités du
    # premier quartile de revenu disponible : la moyenne est portée à trois
    # fois la médiane, et c'est le seul chiffre dérivé de ce fichier.
    ("retraites_q1", "moyenne", 3 * 36_800),
]

ENTETE = """\
# Patrimoine des ménages : déciles, moyennes et médianes — et celui des retraités
# source_id: insee_patrimoine_menages (INSEE, lignes 2021 et 2024)
#            cor_patrimoine_retraites (COR, lignes 2018, populations retraites*)
# unite: euros courants de l'année, par MÉNAGE
# population: ensemble | age_<tranche> (âge de la personne de référence) |
#             retraites (personne de référence retraitée) | retraites_q1 (le
#             quart de ces ménages au revenu disponible le plus bas)
# statistique: d1 … d9, p95, p99, mediane, moyenne
# patrimoine: brut | net (l'INSEE) ; brut hors reste (le COR, écrit `brut`)
# fiabilite:
#   haute : valeur publiée, lue telle quelle dans le classeur de l'INSEE par
#           scripts/fetch/insee_patrimoine_menages.py, ou recopiée du document
#           du COR (16 décembre 2021) par le même script, qui la porte en dur.
#           Aucune certification ne les recontrôle par un second chemin.
#
# À QUOI CETTE SÉRIE SERT
# ------------------------
# À la reprise sur succession de la garantie vieillesse (action 47) : la
# succession d'un bénéficiaire couvre ce que son patrimoine vaut, et
# `donnees/patrimoine.py` ajuste une distribution par population pour dire
# quelle part d'une avance donnée est couverte. Les retraités du premier
# quartile servent aux plus petites pensions, l'ensemble des retraités aux
# autres ; les déciles INSEE de tous les ménages ne servent qu'au recoupement.
#
# Ne pas modifier à la main : le script réécrit le fichier en entier.
"""


def _telecharger(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as reponse:
        return reponse.read()


def _cellules(grille: dict) -> dict[int, dict[int, float | str]]:
    lignes: dict[int, dict[int, float | str]] = {}
    for (ligne, colonne), valeur in grille.items():
        lignes.setdefault(ligne, {})[colonne] = valeur
    return lignes


def _texte(valeur: float | str | None) -> str:
    return valeur.strip() if isinstance(valeur, str) else ""


def _quantiles(grille: dict, annee: int) -> list[dict]:
    """Une feuille « Distribution | brut | net » : les déciles et centiles."""
    sortie = []
    for cellules in _cellules(grille).values():
        libelle = _texte(cellules.get(0)).rstrip()
        # « 1er décile (D1) » chez l'un, « 1er décile  » chez l'autre.
        libelle = libelle.split(" (")[0].strip()
        statistique = STATISTIQUES.get(libelle)
        if statistique is None:
            continue
        for colonne, patrimoine in ((1, "brut"), (2, "net")):
            valeur = cellules.get(colonne)
            if isinstance(valeur, (int, float)):
                sortie.append({"annee": annee, "population": "ensemble",
                               "statistique": statistique, "patrimoine": patrimoine,
                               "valeur": int(round(valeur)), "source_id": "insee_patrimoine_menages"})
    if len(sortie) < 20:
        raise ValueError(f"déciles {annee} : {len(sortie)} valeurs lues, 22 attendues")
    return sortie


def _par_age(grille: dict, annee: int, statistique: str, colonnes: dict[int, str]) -> list[dict]:
    """Les figures 4 (moyennes) et 5 (médianes) : une ligne par âge."""
    sortie = []
    for cellules in _cellules(grille).values():
        population = AGES.get(_texte(cellules.get(0)))
        if population is None:
            continue
        for colonne, patrimoine in colonnes.items():
            valeur = cellules.get(colonne)
            if isinstance(valeur, (int, float)):
                sortie.append({"annee": annee, "population": population,
                               "statistique": statistique, "patrimoine": patrimoine,
                               "valeur": int(round(valeur)), "source_id": "insee_patrimoine_menages"})
    if len(sortie) < 14:
        raise ValueError(f"{statistique} par âge : {len(sortie)} valeurs lues, 14 attendues")
    return sortie


def _feuille(classeur: dict, debut_titre: str) -> dict:
    for nom, grille in classeur.items():
        titre = _texte(grille.get((0, 0)))
        if titre.startswith(debut_titre):
            return grille
    raise LookupError(f"aucune feuille dont le titre commence par « {debut_titre} »")


def extraire(focus: bytes, deciles: bytes) -> list[dict]:
    classeur = feuilles(focus)
    lignes = _quantiles(_feuille(classeur, "Figure 2"), 2021)
    lignes += _par_age(_feuille(classeur, "Figure 4"), 2021, "moyenne", {1: "net", 2: "brut"})
    lignes += _par_age(_feuille(classeur, "Figure 5"), 2021, "mediane", {1: "brut", 2: "net"})
    lignes += _quantiles(next(iter(feuilles(deciles).values())), 2024)
    lignes += [{"annee": 2018, "population": population, "statistique": statistique,
                "patrimoine": "brut", "valeur": valeur, "source_id": "cor_patrimoine_retraites"}
               for population, statistique, valeur in SAISIES_COR]
    return lignes


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    option_fichier(analyseur)
    analyseur.add_argument("--fichier-deciles", help="le classeur des déciles 2024, déjà téléchargé")
    options = analyseur.parse_args(argv)
    print(f"Sources   {URL_FOCUS}\n          {URL_DECILES}")
    try:
        focus = lire_ou_telecharger(URL_FOCUS, _telecharger, options.fichier)
        deciles = lire_ou_telecharger(URL_DECILES, _telecharger, options.fichier_deciles)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as erreur:
        print(f"ÉCHEC   téléchargement : {erreur}", file=sys.stderr)
        return 1
    try:
        lignes = extraire(focus, deciles)
    except (LookupError, ValueError) as erreur:
        print(f"ÉCHEC   lecture des classeurs : {erreur}", file=sys.stderr)
        return 1
    # Deux contrôles de vraisemblance : les quantiles croissent, et le net ne
    # dépasse pas le brut.
    par_cle = {(l["annee"], l["population"], l["statistique"], l["patrimoine"]): l["valeur"]
               for l in lignes}
    ordre = ["d1", "d2", "d3", "d4", "mediane", "d6", "d7", "d8", "d9", "p95", "p99"]
    for annee in (2021, 2024):
        for patrimoine in ("brut", "net"):
            suite = [par_cle[(annee, "ensemble", s, patrimoine)] for s in ordre]
            if any(b <= a for a, b in zip(suite, suite[1:])):
                print(f"ÉCHEC   quantiles non croissants ({annee}, {patrimoine})", file=sys.stderr)
                return 1
    for (annee, population, statistique, patrimoine), valeur in par_cle.items():
        if patrimoine == "net" and valeur > par_cle[(annee, population, statistique, "brut")]:
            print(f"ÉCHEC   net au-dessus du brut ({annee}, {population}, {statistique})",
                  file=sys.stderr)
            return 1
    colonnes = ["annee", "population", "statistique", "patrimoine", "valeur", "source_id", "fiabilite"]
    for ligne in lignes:
        ligne["fiabilite"] = "haute"
    lignes.sort(key=lambda l: (l["annee"], l["population"], l["patrimoine"], ordre.index(l["statistique"]) if l["statistique"] in ordre else 99))
    with SORTIE.open("w", encoding="utf-8") as flux:
        flux.write(ENTETE)
        flux.write(f"# recupere_le: {date.today().isoformat()}\n")
        flux.write(",".join(colonnes) + "\n")
        for ligne in lignes:
            flux.write(",".join(str(ligne[c]) for c in colonnes) + "\n")
    print(f"\n{len(lignes)} lignes écrites dans {SORTIE.relative_to(RACINE)}")
    print(f"Médiane brute de tous les ménages : {par_cle[(2021, 'ensemble', 'mediane', 'brut')]:,} € "
          f"en 2021, {par_cle[(2024, 'ensemble', 'mediane', 'brut')]:,} € en 2024 ; "
          f"retraités du premier quartile : {par_cle[(2018, 'retraites_q1', 'mediane', 'brut')]:,} € en 2018")
    return 0


if __name__ == "__main__":
    sys.exit(main())
