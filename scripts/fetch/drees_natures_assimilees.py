#!/usr/bin/env python3
"""La nature des périodes assimilées : la part des affiliés qui ont validé un trimestre de service national, ou de maladie, et leur cumul, génération par génération (EIC 2017).

    python scripts/fetch/drees_natures_assimilees.py

POURQUOI CETTE SOURCE
---------------------
La population de la page Coût (``scripts/grille_large.py``, action 138, étape
14) met toutes les périodes assimilées de ses carrières au chômage indemnisé.
Or la carrière longue ne répute pas cotisées les mêmes natures à toutes les
dates (D. 351-1-2) : la rédaction de 2003, qui juge les départs de 2004 à
octobre 2012, répute le service national et la maladie, quatre trimestres
chacun, et aucun chômage. Les hommes de la génération 1950 de la population,
qui partent en 2009 et 2010, n'en comptaient aucun. La nature des trimestres
validés sans être cotisés se lit dans l'échantillon interrégimes de
cotisants : le fichier « eic2017_data_drees_er » du jeu « Les droits validés
au cours de la carrière » de la DREES, celui de
``scripts/fetch/drees_premier_trimestre.py``, génération par génération —
1942, 1946, 1950, puis une sur deux de 1954 à 1994 —, sexe par sexe, âge par
âge de 16 à 71 ans.

CE QU'ON EN GARDE : deux indicateurs, « Part_aff », la part des affiliés ayant
validé, à cet âge ou avant, des trimestres du type considéré, et
« Cum_trim », le cumul de ces trimestres par affilié ; pour deux types, le
service national (« SN ») et la maladie (« Maladie », qui compte aussi la
maternité, l'invalidité et les accidents du travail), chacun en trimestres
« utiles », ceux qui portent l'année vers ses quatre trimestres validés ; dans
le champ des affiliés d'avant 23 ans (« Aff_avant_23ans »), celui de
``premier_trimestre.csv`` ; les femmes et les hommes ; à 60 ans, ou au
dernier âge que l'échantillon voit quand la génération n'avait pas 60 ans en
2017. Ce dernier âge est celui où le cumul des trimestres cotisés est encore
publié : le fichier le met à zéro au-delà, et y reporte la part de l'âge
précédent. Le reste du fichier n'est pas lu.

CE QUE LE LECTEUR VÉRIFIE. Chaque génération dit jusqu'où l'échantillon la
voit ; chaque valeur gardée est là ; chaque part est un pourcentage ; un
cumul n'existe pas sans part, et ne passe pas ce que ceux qui en ont peuvent
valider, quatre trimestres par an depuis 16 ans.
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
SORTIE = Path("data/brut/drees_natures_assimilees.json")

#: Les natures gardées, sous les noms du dépôt.
NATURES = {"SN": "service_national", "Maladie": "maladie"}

#: Les indicateurs gardés, sous les noms du dépôt.
INDICATEURS = {"Part_aff": "part", "Cum_trim": "cumul"}

#: Les sexes, sous les noms du dépôt.
SEXES = {"Femmes": "F", "Hommes": "H"}

#: Le champ lu : les affiliés d'avant 23 ans.
CHAMP = "Aff_avant_23ans"

#: L'âge lu, quand l'échantillon voit la génération jusque-là.
AGE = 60


def lire(contenu: bytes) -> dict[tuple[int, str, str, str, int], float]:
    """La part des affiliés d'avant 23 ans qui ont validé un trimestre de
    chaque nature, et le cumul de ces trimestres par affilié, à 60 ans ou au
    dernier âge que l'échantillon voit : ``{(génération, sexe, nature,
    indicateur, âge): valeur}``, la part en pour cent, le cumul en
    trimestres, vérifiés comme le dit l'en-tête du module."""
    valeurs: dict[tuple[int, str, str, str, int], float] = {}
    cotises: dict[tuple[int, str], list[int]] = {}
    lignes = csv.reader(io.StringIO(contenu.decode("latin-1")), delimiter=";")
    entete = next(lignes)
    if [colonne.strip() for colonne in entete] != [
            "Génération", "Âge", "Sexe", "Type_indic", "Type_trim", "Champ", "valeur"]:
        raise RuntimeError(f"en-tête inattendu : {entete}")
    for generation, age, sexe, indicateur, trimestre, champ, valeur in lignes:
        if champ != CHAMP or sexe not in SEXES:
            continue
        if indicateur == "Cum_trim" and trimestre == "Cotisé":
            if float(valeur.replace(",", ".")) > 0.0:
                cotises.setdefault((int(generation), SEXES[sexe]), []).append(int(age))
            continue
        if indicateur not in INDICATEURS or trimestre not in NATURES:
            continue
        valeurs[(int(generation), SEXES[sexe], NATURES[trimestre], INDICATEURS[indicateur],
                 int(age))] = float(valeur.replace(",", "."))
    lu = {}
    for generation, sexe in sorted({(g, s) for g, s, _, _, _ in valeurs}):
        if (generation, sexe) not in cotises:
            raise RuntimeError(f"{generation}, {sexe} : aucun cumul de trimestres cotisés ne "
                               f"dit jusqu'où l'échantillon voit la génération")
        age = min(AGE, max(cotises[(generation, sexe)]))
        for nature in NATURES.values():
            for indicateur in INDICATEURS.values():
                cle = (generation, sexe, nature, indicateur, age)
                if cle not in valeurs:
                    raise RuntimeError(f"{generation}, {sexe}, {nature} : il manque "
                                       f"l'indicateur {indicateur} à {age} ans")
                lu[cle] = valeurs[cle]
    _verifier(lu)
    return lu


def _verifier(lu: dict[tuple[int, str, str, str, int], float]) -> None:
    """Les contrôles de l'en-tête du module."""
    if not lu:
        raise RuntimeError("aucune nature des affiliés d'avant 23 ans")
    for (generation, sexe, nature, indicateur, age), valeur in lu.items():
        if indicateur != "part":
            continue
        if not 0.0 <= valeur <= 100.0:
            raise RuntimeError(f"part hors de cent : {generation}, {sexe}, {nature}, "
                               f"{age} ans — {valeur:g}")
        cumul = lu[(generation, sexe, nature, "cumul", age)]
        if not 0.0 <= cumul <= 4 * (age - 15) * valeur / 100.0:
            raise RuntimeError(f"{generation}, {sexe}, {nature}, {age} ans : un cumul de "
                               f"{cumul:g} trimestres pour {valeur:g} % d'affiliés qui en ont")


def main() -> int:
    try:
        demande = urllib.request.Request(FICHIER, headers=ENTETES)
        with urllib.request.urlopen(demande, timeout=600) as reponse:
            lu = lire(reponse.read())
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1
    charge = {"source": FICHIER, "lu_le": date.today().isoformat(), "champ": CHAMP,
              "valeurs": [{"generation": generation, "sexe": sexe, "nature": nature,
                           "indicateur": indicateur, "age": age, "valeur": valeur}
                          for (generation, sexe, nature, indicateur, age), valeur
                          in sorted(lu.items())]}
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8")
    generations = sorted({generation for generation, _, _, _, _ in lu})
    print(f"{len(lu)} valeurs, générations {generations[0]} à {generations[-1]}, "
          f"écrites dans {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
