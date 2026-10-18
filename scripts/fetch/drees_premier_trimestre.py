#!/usr/bin/env python3
"""L'âge du premier trimestre : la part des affiliés qui ont validé, et cotisé, un trimestre à chaque âge, génération par génération (EIC 2017).

    python scripts/fetch/drees_premier_trimestre.py

POURQUOI CETTE SOURCE
---------------------
La population de la page Coût (``scripts/grille_large.py``, action 138, étape
14) faisait commencer toutes les carrières pleines du salariat privé d'une
génération au même âge, assez tôt pour leur donner la durée des carrières
pleines : à 16 ans pour la génération 1950, à 17 pour 1955. Toutes avaient donc
droit à la carrière longue, dont la condition d'entrée se lit sur les
trimestres cotisés à la fin de l'année des 16, 17 ou 20 ans (D. 351-1-1), et
les hommes partaient en carrière longue deux fois plus que dans l'EIR. L'âge
du premier trimestre se lit dans l'échantillon interrégimes de cotisants : la
DREES en publie les données détaillées de 2017 (« Les droits validés au cours
de la carrière », fichier « eic2017_data_drees_er »), génération par
génération — 1942, 1946, 1950, puis une sur deux de 1954 à 1994 —, sexe par
sexe, âge par âge de 16 à 71 ans.

CE QU'ON EN GARDE : l'indicateur « Part_aff », la part des affiliés ayant
validé, à cet âge ou avant, des trimestres du type considéré, pour deux types,
les trimestres validés (« Validé ») et les trimestres cotisés au titre de
l'activité (« Cotisé ») ; dans le champ des affiliés d'avant 23 ans
(« Aff_avant_23ans »), qui laisse de côté ceux arrivés plus tard, de
l'étranger surtout, et que l'enquête suit de 16 ans à leur âge de 2017 ; de
16 à 23 ans ; les femmes et les hommes. L'âge est celui de l'année : la part
de 19 ans compte les trimestres validés jusqu'à la fin de l'année des 19 ans.
Le reste du fichier — le nombre et le cumul des trimestres, les trimestres de
chômage, de maladie, d'AVPF, de service national, les autres champs, les deux
sexes réunis — n'est pas lu.

CE QUE LE LECTEUR VÉRIFIE. Chaque série a ses huit âges ; une part ne baisse
pas d'un âge au suivant, puisqu'elle cumule ; celle des trimestres cotisés ne
passe pas celle des trimestres validés, un trimestre cotisé étant validé ;
chaque part est un pourcentage.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

BASE = (
    "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog"
    "/datasets/2596_les-droits-valides-au-cours-de-la-carriere"
)
FICHIER = f"{BASE}/attachments/eic2017_data_drees_er_csv"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/drees_premier_trimestre.json")

#: Les types de trimestre gardés, sous les noms du dépôt.
TRIMESTRES = {"Cotisé": "cotise", "Validé": "valide"}

#: Les sexes, sous les noms du dépôt.
SEXES = {"Femmes": "F", "Hommes": "H"}

#: Le champ lu : les affiliés d'avant 23 ans.
CHAMP = "Aff_avant_23ans"

#: Les âges gardés, de la fin de l'année des 16 ans à celle des 23 ans.
AGES = tuple(range(16, 24))


def lire(contenu: bytes) -> dict[tuple[int, str, str, int], float]:
    """La part des affiliés d'avant 23 ans qui ont validé un trimestre de
    chaque type à chaque âge : ``{(génération, sexe, trimestre, âge): part}``,
    en pour cent, vérifiée comme le dit l'en-tête du module."""
    lu: dict[tuple[int, str, str, int], float] = {}
    lignes = csv.reader(io.StringIO(contenu.decode("latin-1")), delimiter=";")
    entete = next(lignes)
    if [colonne.strip() for colonne in entete] != [
            "Génération", "Âge", "Sexe", "Type_indic", "Type_trim", "Champ", "valeur"]:
        raise RuntimeError(f"en-tête inattendu : {entete}")
    for generation, age, sexe, indicateur, trimestre, champ, valeur in lignes:
        if (indicateur != "Part_aff" or champ != CHAMP or sexe not in SEXES
                or trimestre not in TRIMESTRES or int(age) not in AGES):
            continue
        part = float(valeur.replace(",", "."))
        if not 0.0 <= part <= 100.0:
            raise RuntimeError(f"part hors de cent : {generation}, {sexe}, {trimestre}, "
                               f"{age} ans — {valeur}")
        lu[(int(generation), SEXES[sexe], TRIMESTRES[trimestre], int(age))] = part
    _verifier(lu)
    return lu


def _verifier(lu: dict[tuple[int, str, str, int], float]) -> None:
    """Les contrôles de l'en-tête du module."""
    if not lu:
        raise RuntimeError("aucune part des affiliés d'avant 23 ans")
    for generation in sorted({g for g, _, _, _ in lu}):
        for sexe in SEXES.values():
            for trimestre in TRIMESTRES.values():
                manquants = [age for age in AGES if (generation, sexe, trimestre, age) not in lu]
                if manquants:
                    raise RuntimeError(f"{generation}, {sexe}, {trimestre} : il manque "
                                       f"les âges {manquants}")
                parts = [lu[(generation, sexe, trimestre, age)] for age in AGES]
                for age, avant, apres in zip(AGES[1:], parts, parts[1:]):
                    if apres < avant:
                        raise RuntimeError(f"{generation}, {sexe}, {trimestre} : la part "
                                           f"baisse à {age} ans ({avant:g} puis {apres:g})")
            for age in AGES:
                cotise = lu[(generation, sexe, "cotise", age)]
                valide = lu[(generation, sexe, "valide", age)]
                if cotise > valide:
                    raise RuntimeError(f"{generation}, {sexe}, {age} ans : {cotise:g} % ont "
                                       f"cotisé un trimestre, {valide:g} % en ont validé un")


def main() -> int:
    try:
        demande = urllib.request.Request(FICHIER, headers=ENTETES)
        with urllib.request.urlopen(demande, timeout=600) as reponse:
            lu = lire(reponse.read())
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1
    charge = {"source": FICHIER, "lu_le": date.today().isoformat(), "champ": CHAMP,
              "parts": [{"generation": generation, "sexe": sexe, "trimestre": trimestre,
                         "age": age, "part": part}
                        for (generation, sexe, trimestre, age), part in sorted(lu.items())]}
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8")
    generations = sorted({generation for generation, _, _, _ in lu})
    print(f"{len(lu)} parts, générations {generations[0]} à {generations[-1]}, "
          f"écrites dans {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
