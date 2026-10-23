#!/usr/bin/env python3
"""La durée validée à chaque âge : le cumul des trimestres validés par affilié, génération par génération (EIC 2017).

    python scripts/fetch/drees_duree_validee.py
    python scripts/fetch/drees_duree_validee.py --fichier eic2017_data_drees_er.csv

POURQUOI CE TÉMOIN
------------------
``--entree`` de ``scripts/facteurs_depense.py`` fait entrer chaque génération
de la grille du coût dans l'emploi d'autant plus tard que l'âge médian de son
premier trimestre cotisé recule (``premier_trimestre.csv``,
``facteurs_depense.decalage_d_entree``) ; un emploi d'été y compte comme une
entrée. Le taux plein regarde la durée validée : son cumul à chaque âge,
génération par génération, que diffuse le fichier de
``scripts/fetch/drees_premier_trimestre.py`` (« Les droits validés au cours de
la carrière », « eic2017_data_drees_er »), dit quand il vient
(``facteurs_depense.decalage_par_la_duree``, action 138, étape 3). Le témoin
est versionné : les tests le relisent sans réseau. Il n'alimente aucune
valeur du modèle.

CE QU'ON EN GARDE : l'indicateur « Cum_trim », le cumul par affilié des
trimestres validés à la fin de l'année de chaque âge, ou avant ; des
trimestres validés (« Validé »), de quelque nature qu'ils soient (activité,
service national, chômage, maladie, AVPF) ; dans le champ des affiliés d'avant
23 ans (« Aff_avant_23ans »), celui de ``premier_trimestre.csv`` ; les femmes
et les hommes ; génération par génération — 1942, 1946, 1950, puis une sur
deux de 1954 à 1994 —, de 16 ans au dernier âge que l'échantillon voit, celui
de la génération en 2017, ou 71 ans, le dernier que le fichier publie.
Au-delà, le fichier reporte le cumul de ce dernier âge. Le reste n'est pas lu.

CE QUE LE LECTEUR VÉRIFIE. Chaque génération a tous ses âges, de 16 ans au
dernier ; un cumul ne baisse pas d'un âge au suivant, et n'y gagne pas plus
des quatre trimestres d'une année. ``--fichier`` lit le fichier déjà
téléchargé.
"""

from __future__ import annotations

import argparse
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
RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "tests" / "temoins" / "drees_duree_validee_2017.json"

#: Les sexes, sous les noms du dépôt.
SEXES = {"Femmes": "F", "Hommes": "H"}

#: Le champ lu : les affiliés d'avant 23 ans.
CHAMP = "Aff_avant_23ans"

#: L'année de l'échantillon, qui voit chaque génération jusqu'à son âge de
#: cette année-là.
ANNEE_DE_L_ECHANTILLON = 2017

#: Le premier âge et le dernier que le fichier publie.
PREMIER_AGE, DERNIER_AGE = 16, 71


def dernier_age(generation: int) -> int:
    """Le dernier âge que l'échantillon voit chez ``generation``."""
    return min(DERNIER_AGE, ANNEE_DE_L_ECHANTILLON - generation)


def lire(contenu: bytes) -> dict[tuple[str, int], dict[int, float]]:
    """Le cumul des trimestres validés par affilié d'avant 23 ans à chaque âge :
    ``{(sexe, génération): {âge: cumul}}``, vérifié comme le dit l'en-tête du
    module."""
    lu: dict[tuple[str, int], dict[int, float]] = {}
    lignes = csv.reader(io.StringIO(contenu.decode("latin-1")), delimiter=";")
    entete = next(lignes)
    if [colonne.strip() for colonne in entete] != [
            "Génération", "Âge", "Sexe", "Type_indic", "Type_trim", "Champ", "valeur"]:
        raise RuntimeError(f"en-tête inattendu : {entete}")
    for generation, age, sexe, indicateur, trimestre, champ, valeur in lignes:
        if (indicateur != "Cum_trim" or trimestre != "Validé" or champ != CHAMP
                or sexe not in SEXES or int(age) > dernier_age(int(generation))):
            continue
        lu.setdefault((SEXES[sexe], int(generation)), {})[int(age)] = float(
            valeur.replace(",", "."))
    _verifier(lu)
    return lu


def _verifier(lu: dict[tuple[str, int], dict[int, float]]) -> None:
    """Les contrôles de l'en-tête du module."""
    if not lu:
        raise RuntimeError("aucun cumul des trimestres validés")
    for (sexe, generation), cumuls in sorted(lu.items()):
        ages = list(range(PREMIER_AGE, dernier_age(generation) + 1))
        if sorted(cumuls) != ages:
            raise RuntimeError(f"{generation}, {sexe} : il manque les âges "
                               f"{sorted(set(ages) - set(cumuls))}")
        for age in ages[1:]:
            gain = cumuls[age] - cumuls[age - 1]
            if not 0.0 <= gain <= 4.0:
                raise RuntimeError(f"{generation}, {sexe} : le cumul passe de "
                                   f"{cumuls[age - 1]:g} à {cumuls[age]:g} à {age} ans")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--fichier", type=Path,
                           help="le fichier « eic2017_data_drees_er » déjà téléchargé")
    arguments = analyseur.parse_args(argv)
    try:
        if arguments.fichier is not None:
            lu = lire(arguments.fichier.read_bytes())
        else:
            demande = urllib.request.Request(FICHIER, headers=ENTETES)
            with urllib.request.urlopen(demande, timeout=600) as reponse:
                lu = lire(reponse.read())
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1
    temoin = {"source": FICHIER, "lu_le": date.today().isoformat(), "champ": CHAMP,
              "annee_de_l_echantillon": ANNEE_DE_L_ECHANTILLON,
              "unite": "trimestres validés par affilié, à la fin de l'année de l'âge",
              "cumuls": {sexe: {str(generation): {str(age): cumul
                                                  for age, cumul in sorted(lu[(sexe, generation)].items())}
                                for s, generation in sorted(lu) if s == sexe}
                         for sexe in sorted(SEXES.values())}}
    SORTIE.write_text(json.dumps(temoin, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    generations = sorted({generation for _sexe, generation in lu})
    print(f"{sum(len(c) for c in lu.values())} cumuls, générations {generations[0]} à "
          f"{generations[-1]}, écrits dans {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
