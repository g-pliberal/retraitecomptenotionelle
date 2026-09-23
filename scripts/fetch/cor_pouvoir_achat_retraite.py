#!/usr/bin/env python3
"""Le pouvoir d'achat des cas types du COR au cours de la retraite.

    python scripts/fetch/cor_pouvoir_achat_retraite.py
    python scripts/fetch/cor_pouvoir_achat_retraite.py --fichier Donnees_RA2026_P3_2.xlsx

POURQUOI CE TÉMOIN. Le simulateur montre à un retraité la pension qu'il touche
AUJOURD'HUI, et non plus celle de son départ : il revalorise chaque régime
comme son texte l'a fait (``src/retraite_notionnelle/revalorisation.py``).
Relire ce calcul avec la main qui l'a écrit ne prouverait rien. Le Conseil
d'orientation des retraites, lui, publie chaque année l'évolution du pouvoir
d'achat de la pension nette de deux cas types — un non-cadre et un cadre du
secteur privé — année après année depuis leur départ, pour quatre générations
parties en janvier 1997, 2002, 2007 et 2012. C'est un calcul fait par
d'autres, sur les mêmes barèmes, et publié avec ses conventions : la
composition de la pension (70 % Cnav et 30 % Arrco pour le non-cadre ; 36 %
Cnav, 15 % Arrco et 49 % Agirc pour le cadre), le taux de CSG de chacun,
l'indice des prix y compris tabac. ``tests/test_revalorisation.py`` le refait.

LA SOURCE. Le classeur de données de la partie 3 du rapport annuel de juin
2026, feuille « Fig 3.14 » : « Évolutions nettes du pouvoir d'achat au cours
de la retraite », en écart relatif à l'année du départ. Les conventions sont
écrites au § 3.3 de l'annexe méthodologique en ligne du même rapport ; 2026
y est une année prévisionnelle.

Le témoin est versionné : les tests le relisent sans réseau.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
URL = ("https://www.cor-retraites.fr/sites/default/files/2026-06/"
       "Donn%C3%A9es_RA2026_P3_2.xlsx")
FEUILLE = "Fig 3.14"
SORTIE = RACINE / "tests" / "temoins" / "cor_pouvoir_achat_retraite.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Le titre de ligne de chaque cas type dans la feuille, et le code du témoin.
CAS_TYPES = {"Cadre": "cadre", "Non-cadre": "non_cadre"}


def lire(classeur: bytes) -> dict[str, dict[str, list[float]]]:
    """Les séries de la figure : cas type → génération → écarts, an 1 d'abord."""
    cellules = feuilles(classeur)[FEUILLE]
    lignes = sorted({ligne for ligne, _ in cellules})
    colonnes = sorted({colonne for _, colonne in cellules})
    series: dict[str, dict[str, list[float]]] = {}
    courant = None
    for ligne in lignes:
        valeurs = [cellules.get((ligne, colonne)) for colonne in colonnes]
        tete = valeurs[0]
        if isinstance(tete, str) and tete.strip() in CAS_TYPES:
            courant = CAS_TYPES[tete.strip()]
            series[courant] = {}
            continue
        if courant is None or not isinstance(tete, str) or not tete.startswith("Génération"):
            continue
        generation = tete.split()[-1]
        series[courant][generation] = [v for v in valeurs[1:] if isinstance(v, float)]
    return series


def controler(series: dict[str, dict[str, list[float]]]) -> list[str]:
    """La forme que le test suppose : deux cas types, quatre générations, un
    an 1 à zéro, et une dernière année qui tombe en 2026."""
    erreurs = []
    for cas_type in CAS_TYPES.values():
        generations = series.get(cas_type, {})
        if sorted(generations) != ["1937", "1942", "1947", "1952"]:
            erreurs.append(f"{cas_type} : générations {sorted(generations)}")
            continue
        for generation, valeurs in generations.items():
            if not valeurs or valeurs[0] != 0.0:
                erreurs.append(f"{cas_type} {generation} : l'an 1 n'est pas la référence")
            if int(generation) + 60 + len(valeurs) - 1 != 2026:
                erreurs.append(f"{cas_type} {generation} : {len(valeurs)} années, "
                               "la dernière ne tombe pas en 2026")
    return erreurs


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--fichier", type=Path,
                           help="classeur déjà téléchargé, lu au lieu du réseau")
    arguments = analyseur.parse_args(argv)
    if arguments.fichier:
        classeur = arguments.fichier.read_bytes()
    else:
        requete = urllib.request.Request(URL, headers=ENTETES)
        with urllib.request.urlopen(requete, timeout=120) as reponse:
            classeur = reponse.read()
    series = lire(classeur)
    erreurs = controler(series)
    if erreurs:
        print("Figure refusée :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    SORTIE.write_text(json.dumps({
        "source": {
            "editeur": "Conseil d'orientation des retraites",
            "reference": "Rapport annuel de juin 2026, figure 3.14, « Évolutions "
                         "nettes du pouvoir d'achat au cours de la retraite » ; "
                         "conventions : annexe méthodologique en ligne, § 3.3",
            "url": URL,
            "lu_le": "2026-09-23",
        },
        "conventions": {
            "an_1": "départ en retraite en janvier, à 60 ans",
            "mesure": "pension nette annuelle déflatée de l'indice des prix y "
                      "compris tabac, en écart relatif à l'an 1",
            "derniere_annee": "2026, prévisionnelle",
            "composition": {
                "non_cadre": {"cnav": 0.70, "arrco": 0.30},
                "cadre": {"cnav": 0.36, "arrco": 0.15, "agirc": 0.49},
            },
            "csg": {"non_cadre": "taux médian, taux plein en 2018",
                    "cadre": "taux normal"},
        },
        "series": series,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{sum(len(g) for g in series.values())} séries écrites dans "
          f"{SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
