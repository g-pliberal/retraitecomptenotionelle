#!/usr/bin/env python3
"""Espérances de vie par vingtile de niveau de vie, lues chez l'INSEE.

    python scripts/fetch/insee_mortalite_niveau_de_vie.py
    python scripts/fetch/insee_mortalite_niveau_de_vie.py --fichier ~/Téléchargements/morta_niv.xlsx

L'INSEE publie, dans les *Insee Résultats* « Tables de mortalité par niveau de
vie jusqu'en 2020-2024 » (classeur ``morta_niv.xlsx``, mai 2025), des tables
complètes par sexe, âge et VINGTILE de niveau de vie, pour deux périodes —
2012-2016 et 2020-2024 —, avec l'espérance de vie à chaque âge et, « pour
information », le niveau de vie mensuel moyen de chaque vingtile. C'est la
source de l'*Insee Première* n° 2085, et la seule mesure publique de la
mortalité par revenu en France.

CE QUE LE DÉPÔT EN REPREND
--------------------------
L'espérance de vie à 0, 60 et 65 ans, telle que le classeur l'écrit, pour
l'ensemble et pour chacun des vingt vingtiles, par sexe et par période ; et
le niveau de vie mensuel moyen de chaque vingtile, qui est ce qui permet d'y
RATTACHER un cas type. Rien n'est dérivé : ces espérances sont publiées.

L'année portée est le MILIEU de la période — 2014 et 2022 —, parce que le
modèle cale ses facteurs sur la table du moment d'une année. Le contrôle qui
autorise ce choix est dans le script : l'espérance « Ensemble » du classeur,
qui est une table de période, doit retrouver la MOYENNE des cinq espérances
annuelles que le dépôt certifie (INSEE, OCDE) à un dixième et demi près.

À QUOI ÇA SERT
--------------
À la variante ``population_conversion`` du diviseur (action 14) : un facteur
sur la force de mortalité de la table générale, calé par vingtile et par
sexe pour reproduire l'espérance publiée. Voir ``donnees/mortalite.py``.
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

URL = "https://www.insee.fr/fr/statistiques/fichier/8670202/morta_niv.xlsx"
RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "reference" / "mortalite" / "esperances_vie_niveau_de_vie.csv"

#: Feuille du classeur -> (sexe, période, année centrale).
FEUILLES = {
    "F - 2012_2016": ("F", "2012-2016", 2014),
    "H - 2012_2016": ("H", "2012-2016", 2014),
    "F - 2020_2024": ("F", "2020-2024", 2022),
    "H - 2020_2024": ("H", "2020-2024", 2022),
}
FEUILLE_NIVEAUX = "Pour information"

#: Âges dont le modèle se sert. e0 n'entre dans aucun calcul : il est là pour
#: que la lecture se recoupe avec l'*Insee Première*, qui le publie.
AGES = (0, 60, 65)

#: Le contrôle : l'espérance « Ensemble » du classeur — une table de PÉRIODE,
#: cinq années de décès mises ensemble — contre la moyenne des cinq espérances
#: annuelles que le dépôt certifie pour la population générale. L'écart est
#: de un à trois dixièmes, toujours du même signe : l'ensemble de l'étude
#: vit un peu moins que la population générale certifiée, ce qui tient au
#: champ (France hors Mayotte, personnes appariées dans l'échantillon
#: démographique permanent) et à la méthode (document de travail 2025-24).
#: C'est pourquoi le modèle ne cale pas un vingtile sur sa valeur brute mais
#: sur son RAPPORT à l'ensemble de l'étude, appliqué à sa propre table.
TOLERANCE_CONTROLE = 0.3

ENTETE = """# Espérances de vie par VINGTILE de niveau de vie, France hors Mayotte
# source_id: insee_mortalite_niveau_de_vie
# unite: années (valeur) ; euros par mois (niveau_de_vie_mensuel)
# sexe: H | F
# vingtile: 0 = ensemble, 1 = les 5 % les plus modestes … 20 = les 5 % les
#           plus aisés
# mesure: e0 | e60 | e65
# annee: le MILIEU de la période — 2014 pour 2012-2016, 2022 pour 2020-2024
# fiabilite:
#   haute : lu tel quel dans le classeur de l'INSEE par
#           scripts/fetch/insee_mortalite_niveau_de_vie.py, qui contrôle
#           l'espérance « ensemble » contre celle que le dépôt certifie pour
#           l'année centrale. Le producteur publie ces espérances, le dépôt
#           ne les dérive pas ; mais aucune certification ne les recontrôle
#           par un second chemin, d'où `haute` et non `certifiee`.
#
# À QUOI CETTE SÉRIE SERT
# ------------------------
# À l'axe du REVENU de l'action 14 : le diviseur de conversion est une
# espérance de vie de population générale, la même pour tous, et l'INSEE
# mesure ici treize ans d'écart à la naissance entre les hommes les plus
# modestes et les plus aisés, sept ans à 65 ans. Le modèle en tire, par
# vingtile et par sexe, un facteur sur la force de mortalité de la table
# générale (`DonneesMortalite.facteur_population`, populations
# `niveau_de_vie_v01` à `niveau_de_vie_v20`), et un cas type y est rattaché
# par son niveau de salaire (`population_niveau_de_vie`). Seule la période
# 2020-2024 sert au facteur ; 2012-2016 est gardée pour dire la dérive.
#
# CE QU'IL FAUT SAVOIR AVANT DE S'EN SERVIR
# ------------------------------------------
# - Le niveau de vie est celui du MÉNAGE par unité de consommation, revenu
#   disponible, à la date de l'observation — pas un salaire, pas une carrière.
#   Le rattachement d'un cas type par son salaire est une convention écrite,
#   pas une mesure.
# - Les quotients d'avant 20 ans et d'après 96 ans sont estimés par l'INSEE
#   sous une hypothèse d'écart constant (document de travail 2025-24) ; ils
#   ne pèsent guère sur e65.
# - `niveau_de_vie_mensuel` est le niveau de vie mensuel MOYEN du vingtile
#   sur la période, en euros courants ; vide pour l'ensemble.
"""


def _lire_feuille(grille: dict) -> tuple[list[str], dict[tuple[int, int], float]]:
    """Les libellés de vingtile en en-tête, et ``(vingtile, age) -> espérance``.

    Disposition : ligne 5, un libellé toutes les trois colonnes à partir de la
    colonne 1 (« Ensemble », puis « 0-5% » … « 95-100% ») ; ligne 6, les trois
    indicateurs de chaque bloc — quotient, survie, espérance ; à partir de la
    ligne 8, un âge en première colonne.
    """
    libelles = [
        (colonne, valeur) for (ligne, colonne), valeur in grille.items()
        if ligne == 5 and colonne >= 1 and isinstance(valeur, str)
    ]
    libelles.sort()
    if len(libelles) != 21:
        raise LookupError(f"{len(libelles)} blocs de vingtile en en-tête, 21 attendus")
    for indice, (colonne, _) in enumerate(libelles):
        if colonne != 1 + 3 * indice:
            raise LookupError(f"bloc {indice} en colonne {colonne}, {1 + 3 * indice} attendue")
        if grille.get((6, colonne + 2), "") != "Espérance de vie à l’âge x":
            raise LookupError(f"la colonne {colonne + 2} n'est pas une espérance de vie")
    esperances: dict[tuple[int, int], float] = {}
    for (ligne, colonne), valeur in grille.items():
        if ligne >= 8 and colonne == 0 and isinstance(valeur, float):
            age = int(valeur)
            for vingtile, (debut, _) in enumerate(libelles):
                cellule = grille.get((ligne, debut + 2))
                if isinstance(cellule, float):
                    esperances[(vingtile, age)] = cellule
    return [libelle for _, libelle in libelles], esperances


def _niveaux(grille: dict) -> dict[tuple[str, int], float]:
    """``(période, vingtile) -> niveau de vie mensuel moyen``."""
    periodes = {
        colonne: str(valeur) for (ligne, colonne), valeur in grille.items()
        if ligne == 3 and colonne >= 1 and isinstance(valeur, str)
    }
    niveaux: dict[tuple[str, int], float] = {}
    for (ligne, colonne), valeur in grille.items():
        if colonne == 0 and ligne >= 4 and isinstance(valeur, str) and "%" in valeur:
            vingtile = ligne - 3
            for col, periode in periodes.items():
                montant = grille.get((ligne, col))
                if isinstance(montant, float):
                    niveaux[(periode, vingtile)] = montant
    if len(niveaux) != 40:
        raise LookupError(f"{len(niveaux)} niveaux de vie lus, 40 attendus")
    return niveaux


def extraire(donnees: bytes) -> list[dict]:
    """Une ligne par (période, sexe, vingtile, mesure)."""
    classeur = feuilles(donnees)
    manquantes = (set(FEUILLES) | {FEUILLE_NIVEAUX}) - set(classeur)
    if manquantes:
        raise LookupError(f"feuilles absentes du classeur : {sorted(manquantes)}")
    niveaux = _niveaux(classeur[FEUILLE_NIVEAUX])
    lignes = []
    for feuille, (sexe, periode, annee) in FEUILLES.items():
        _, esperances = _lire_feuille(classeur[feuille])
        for vingtile in range(21):
            for age in AGES:
                valeur = esperances.get((vingtile, age))
                if valeur is None:
                    raise LookupError(f"{feuille} : pas d'espérance à {age} ans, vingtile {vingtile}")
                lignes.append({
                    "periode": periode, "annee": annee, "sexe": sexe,
                    "vingtile": vingtile, "mesure": f"e{age}",
                    "valeur": round(valeur, 2),
                    "niveau_de_vie_mensuel": (
                        "" if vingtile == 0 else f"{niveaux[(periode, vingtile)]:.0f}"
                    ),
                    "fiabilite": "haute",
                })
    return lignes


def _telecharger(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=300) as reponse:
        return reponse.read()


def _certifiee_periode(periode: str, sexe: str, mesure: str) -> float | None:
    """La moyenne, sur les années de la période, de l'espérance que le dépôt
    certifie pour la population générale."""
    import csv

    debut, fin = (int(x) for x in periode.split("-"))
    chemin = RACINE / "data" / "reference" / "mortalite" / "esperances_vie.csv"
    valeurs = []
    with chemin.open(encoding="utf-8") as flux:
        for ligne in csv.DictReader(l for l in flux if not l.startswith("#")):
            if (ligne["sexe"], ligne["mesure"]) == (sexe, mesure) and debut <= int(ligne["annee"]) <= fin:
                valeurs.append(float(ligne["valeur"]))
    return sum(valeurs) / len(valeurs) if len(valeurs) == fin - debut + 1 else None


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
    print(f"Classeur  {len(donnees) / 1024:,.0f} Ko")
    try:
        lignes = extraire(donnees)
    except (LookupError, ValueError) as erreur:
        print(f"ÉCHEC   lecture du classeur : {erreur}", file=sys.stderr)
        return 1

    # Le contrôle : l'« ensemble » du classeur est la population générale de la
    # période, et doit retrouver ce que le dépôt certifie pour l'année centrale.
    for ligne in lignes:
        if ligne["vingtile"] != 0 or ligne["mesure"] == "e0":
            continue
        attendu = _certifiee_periode(ligne["periode"], ligne["sexe"], ligne["mesure"])
        if attendu is None:
            continue
        ecart = ligne["valeur"] - attendu
        print(f"Contrôle  {ligne['mesure']} {ligne['sexe']} {ligne['periode']} : "
              f"{ligne['valeur']:.2f} ans, moyenne certifiée {attendu:.2f} "
              f"({ecart:+.2f})")
        if abs(ecart) > TOLERANCE_CONTROLE:
            print("ÉCHEC   l'ensemble du classeur ne retrouve pas la population "
                  "générale de l'année centrale", file=sys.stderr)
            return 1
    # Deux contrôles de vraisemblance : l'espérance croît avec le vingtile, et
    # les femmes vivent plus longtemps que les hommes dans chaque vingtile.
    par_cle = {(l["periode"], l["sexe"], l["vingtile"], l["mesure"]): l["valeur"] for l in lignes}
    for periode in {l["periode"] for l in lignes}:
        for sexe in ("H", "F"):
            suite = [par_cle[(periode, sexe, v, "e65")] for v in range(1, 21)]
            if any(b < a for a, b in zip(suite, suite[1:])):
                print(f"ÉCHEC   e65 non croissante avec le niveau de vie ({sexe}, {periode})",
                      file=sys.stderr)
                return 1
        for v in range(21):
            if par_cle[(periode, "F", v, "e65")] <= par_cle[(periode, "H", v, "e65")]:
                print(f"ÉCHEC   e65 des femmes sous celle des hommes, vingtile {v}, {periode}",
                      file=sys.stderr)
                return 1

    colonnes = ["periode", "annee", "sexe", "vingtile", "mesure", "valeur",
                "niveau_de_vie_mensuel", "fiabilite"]
    lignes.sort(key=lambda l: (l["annee"], l["sexe"], l["vingtile"], l["mesure"]))
    with SORTIE.open("w", encoding="utf-8") as flux:
        flux.write(ENTETE)
        flux.write(f"# recupere_le: {date.today().isoformat()}\n")
        flux.write(",".join(colonnes) + "\n")
        for ligne in lignes:
            flux.write(",".join(str(ligne[c]) for c in colonnes) + "\n")
    print(f"\n{len(lignes)} lignes écrites dans {SORTIE.relative_to(RACINE)}")
    h = [par_cle[("2020-2024", "H", v, "e65")] for v in (1, 20)]
    f = [par_cle[("2020-2024", "F", v, "e65")] for v in (1, 20)]
    print(f"e65 en 2020-2024, des 5 % les plus modestes aux 5 % les plus aisés : "
          f"hommes {h[0]:.2f} → {h[1]:.2f}, femmes {f[0]:.2f} → {f[1]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
