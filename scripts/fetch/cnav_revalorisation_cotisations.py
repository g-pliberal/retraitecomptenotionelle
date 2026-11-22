#!/usr/bin/env python3
"""Coefficients de revalorisation des COTISATIONS de 1930 à 1944, par la Cnav.

    python scripts/fetch/cnav_revalorisation_cotisations.py

À QUOI ILS SERVENT. Avant 1945, le compte d'un assuré social portait des
cotisations, non des salaires. Pour le salaire annuel moyen d'une pension du
régime général, la caisse convertit et revalorise ces cotisations d'un même
coefficient, fixé à chaque date d'effet avec ceux des salaires : la circulaire
ministérielle n° 151 du 5 août 1946 (CR_MIN_151_05081946) dit que « pour la
période du 1er juillet 1930 au 31 décembre 1944 », « les cotisations seront
directement revalorisées avant la recherche du salaire annuel moyen ».

CE QUI EST LU. La caisse publie ces coefficients dans les mêmes tableaux que
ceux des salaires : la page d'avant 2013 (quatre-vingt-six colonnes, de
l'arrêté du 14 mai 1946 à la circulaire 2012/35 ; voir
``cnav_revalorisation_salaires_anciennes.py``), puis chaque édition du barème
depuis avril 2013, sous « Coefficients applicables aux cotisations avant
1947 ». Treize cellules : de juillet 1930 à 1935, deux catégories — la 1re à
la 4e, la 5e —, puis une par année de 1936 à 1946.

CE QUI EN EST GARDÉ. Les années 1930 à 1944, celles des assurances sociales,
que le modèle porte en salaires : 1930 à 1935 au coefficient des quatre
premières catégories, une ligne par année. La 5e catégorie ne se distingue
que par le multiplicateur qui convertit sa cotisation en salaire (22,5 au lieu
de 25 dans la colonne de 1946, 67,500 contre 75,000) : le modèle, qui
part du salaire, en lit le rapport à la colonne de 1946, qui ne dépend pas de
la catégorie (à 0,1 % près, l'arrondi des colonnes récentes). 1945 et 1946,
que le modèle porte au régime général, restent hors du fichier.

LA COLONNE D'AVRIL 1958 (arrêté du 14 avril 1958) est gardée à sa date : le
récupérateur des salaires la confond avec celle de 1957, dont il croit qu'elle
porte la date, parce que sa référence, sans point-virgule, échappe à sa
lecture ; ce récupérateur-ci ne lit pas la référence.

DEUX COQUILLES DE LA PAGE, corrigées : « 29,148,750 » (5e catégorie, janvier
1986), des milliers séparés d'une virgule, se lit 29 148,750 ; « 1.1938,375 »
(1939 et 1940, avril 1971), un chiffre doublé, 1 938,375 (``COQUILLES``).

Le script refuse d'écrire si une colonne n'a pas ses treize cellules, si un
coefficient remonte d'une année à la suivante, ou si les repères recopiés à la
main ne se retrouvent pas.

Statut de fiabilité : ``haute``. La caisse transcrit l'arrêté qu'elle cite.
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cnav_api  # noqa: E402
import cnav_revalorisation_salaires as recentes  # noqa: E402
import cnav_revalorisation_salaires_anciennes as anciennes  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
BRUT = RACINE / "data" / "brut" / "cnav_revalorisation_cotisations.json"
SORTIE = RACINE / "data" / "reference" / "legislation" / "revalorisation_cotisations_1930_1944.csv"

#: Les éditions du barème, avec la date d'effet de leur colonne.
BAREMES = dict(anciennes.BAREMES) | recentes.BAREMES

#: Recopiés à la main de la page et des barèmes : (date d'effet, année,
#: coefficient). 1930 vaut la 1re à la 4e catégorie.
REPERES = (
    ("1946-05-14", 1930, 75.0),
    ("1946-05-14", 1936, 42.857),
    ("1946-05-14", 1944, 18.75),
    ("1950-01-01", 1938, 263.75),
    ("1957-04-01", 1938, 533.125),
    ("1958-04-01", 1938, 573.125),
    ("1950-01-01", 1944, 83.75),
    ("2013-04-01", 1936, 27846.6),
    ("2026-01-01", 1930, 64805.725),
    ("2026-01-01", 1944, 6719.187),
)

ENTETE_CSV = """\
# Coefficients de revalorisation des cotisations des assurances sociales, 1930-1944
# ---------------------------------------------------------------------------------
# source_id: cnav_revalorisation_cotisations
#
# Fichier écrit par scripts/fetch/cnav_revalorisation_cotisations.py :
# ne pas modifier à la main.
#
# Le coefficient que la Cnav applique, à chaque date d'effet, aux cotisations
# d'une année de 1930 à 1944 pour en faire un salaire revalorisé du salaire
# annuel moyen : la page d'avant 2013, puis les éditions du barème. Une colonne
# vaut de sa date d'effet à la suivante. 1930 à 1935 : la 1re à la 4e
# catégorie. Le modèle porte des salaires : il lit le rapport d'une colonne à
# celle de l'arrêté du 14 mai 1946, multiplié par le coefficient de la
# circulaire n° 151 du 5 août 1946 (3, 2 ou 1). Voir le récupérateur.
#
# fiabilite : `haute`. La caisse transcrit l'arrêté ou la loi qu'elle cite.
date_effet,annee_perception,coefficient,fiabilite
"""

ANNEES = range(1930, 1945)

#: Les coquilles de la page, et ce qu'elles valent : la colonne d'avril 1971
#: (arrêté du 4 mars 1971) écrit « 1.1938,375 » pour 1939 et 1940, entre
#: 1 918,125 (1938) et 1 292,875 (1941) ; ses voisines d'avril 1970 et d'avril
#: 1972 portent 1 760,550 et 2 161,250, et le rapport de la colonne à celle
#: de 1970, 1,101 sur les autres années, donne 1 938,4 : un chiffre doublé.
COQUILLES = {"1.1938,375": "1.938,375"}


def _nombre(cellule: str) -> float:
    """Comme la page des salaires, plus une coquille de la page : « 29,148,750 »,
    des milliers et des décimales tous séparés d'une virgule, se lit 29 148,750."""
    cellule = COQUILLES.get(cellule.strip(), cellule).strip().replace(" ", "")
    if cellule.count(",") > 1:
        entier, _, decimales = cellule.rpartition(",")
        cellule = f"{entier.replace(',', '.')},{decimales}"
    return anciennes._nombre(cellule)


def cellules_en_annees(cellules: list[float]) -> dict[int, float]:
    """Treize cellules — 1930-1935 1re à 4e catégorie, 5e catégorie, 1936 à
    1946 — en une table 1930 à 1944."""
    if len(cellules) != 13:
        raise ValueError(f"{len(cellules)} cellules au lieu de treize")
    table = {annee: cellules[0] for annee in range(1930, 1936)}
    table.update({1936 + rang: valeur for rang, valeur in enumerate(cellules[2:11])})
    return table


def lire_page(script: str) -> dict[str, dict[int, float]]:
    """Les colonnes de la page d'avant 2013, par date d'effet."""
    blocs = re.findall(
        r't_p\[i\]\s*=\s*"([^"]+)";.*?m_v\[1\]\s*=\s*new Array\(([^)]*)\)',
        script, flags=re.S)
    colonnes: dict[str, dict[int, float]] = {}
    for periode, valeurs in blocs:
        cellules = re.findall(r'"([^"]*)"', valeurs)
        if periode.strip().lower().startswith("avant"):
            effet = anciennes.DATES_CORRIGEES["avant_1949"]
        else:
            jour, mois, annee = re.search(r"(\d\d)/(\d\d)/(\d{4})", periode).groups()
            # Pas la correction de date du récupérateur des salaires : la
            # colonne d'avril 1958 porte bien l'arrêté du 14 avril 1958, dont la
            # référence seule, sans point-virgule, trompait sa lecture.
            effet = f"{annee}-{mois}-{jour}"
        colonnes[effet] = cellules_en_annees([_nombre(c) for c in cellules[:13]])
    return colonnes


def lire_bareme(contenu: str) -> dict[int, float]:
    """Le tableau des cotisations d'une édition du barème."""
    texte = html.unescape(re.sub(r"<[^>]+>", "|", contenu)).replace("​", "")
    texte = re.sub(r"(\|\s*)+", "|", texte.replace("\xa0", " "))
    cotisations = re.split(r"cotisations avant 1947", texte, flags=re.I)[1]
    par_annee = {int(a): anciennes._nombre(v) for a, v in re.findall(
        r"\|\s*(19[34]\d)\s*\|\s*([\d .]+,\s*\d+)\s*(?=\|)", cotisations)}
    premieres = re.search(r"1re à 4e catégorie\s*\|\s*([\d .]+,\s*\d+)", cotisations, re.I)
    cinquieme = re.search(r"5e catégorie\s*\|\s*([\d .]+,\s*\d+)", cotisations, re.I)
    if premieres is None or cinquieme is None:
        raise ValueError("les catégories de 1930 à 1935 manquent")
    return cellules_en_annees(
        [anciennes._nombre(premieres.group(1)), anciennes._nombre(cinquieme.group(1))]
        + [par_annee[annee] for annee in range(1936, 1947)])


def controler(colonnes: dict[str, dict[int, float]]) -> list[str]:
    griefs = []
    for effet, table in sorted(colonnes.items()):
        if sorted(table) != list(ANNEES):
            griefs.append(f"{effet} : les années ne vont pas de 1930 à 1944")
            continue
        for avant, apres in zip(ANNEES, ANNEES[1:]):
            if table[apres] > table[avant] + 1e-9:
                griefs.append(f"{effet} : le coefficient remonte de {avant} à {apres}")
    for effet, annee, attendu in REPERES:
        lu = colonnes.get(effet, {}).get(annee)
        if lu is None or abs(lu - attendu) > 5e-4:
            griefs.append(f"repère {effet}, {annee} : attendu {attendu}, lu {lu}")
    return griefs


def main() -> int:
    colonnes = lire_page(cnav_api.telecharger(anciennes.PAGE, delai=120).decode("latin-1"))
    for effet, nom in sorted(BAREMES.items()):
        colonnes[effet] = lire_bareme(cnav_api.bareme(nom)["contenu"])
    griefs = controler(colonnes)
    if griefs:
        print("Colonnes refusées :", *griefs, sep="\n  ", file=sys.stderr)
        return 1
    BRUT.parent.mkdir(parents=True, exist_ok=True)
    BRUT.write_text(json.dumps({
        "sources": [anciennes.PAGE] + [cnav_api.adresse_bareme(b) for b in BAREMES.values()],
        "recupere_le": date.today().isoformat(),
        "colonnes": {effet: {str(a): v for a, v in sorted(table.items())}
                     for effet, table in sorted(colonnes.items())},
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    lignes = [f"{effet},{annee},{coefficient:.10g},haute\n"
              for effet, table in sorted(colonnes.items())
              for annee, coefficient in sorted(table.items())]
    SORTIE.write_bytes((ENTETE_CSV + "".join(lignes)).encode("utf-8"))
    print(f"{SORTIE.relative_to(RACINE)} : {len(colonnes)} colonnes, "
          f"{len(lignes)} coefficients, du {min(colonnes)} au {max(colonnes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
