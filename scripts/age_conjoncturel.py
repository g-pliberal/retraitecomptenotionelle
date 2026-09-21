#!/usr/bin/env python3
"""De combien la grille de cas types part plus tôt, ou plus tard, que la France réelle.

    python scripts/age_conjoncturel.py            # le tableau année par année
    python scripts/age_conjoncturel.py --json a.json

LA QUESTION
-----------
``docs/limites.md`` § 5 ter écrivait, sans pouvoir le chiffrer : « les âges
d'entrée des cas types restent ceux de la grille — vingt-quatre ans pour
l'artisan, vingt-sept pour le libéral —, ce qui suffit à les faire partir à
soixante-sept ans une fois la durée requise opposée. La grille part donc, en
moyenne, un peu plus tard que la France réelle ; l'âge conjoncturel de départ
que publie la DREES permettrait de le chiffrer, et il n'est pas dans le
dépôt. »

Il y est — ``data/reference/macro/age_conjoncturel_depart.csv``, 2004 à 2022,
par sexe — et ce script fait la mesure.

CE QU'ON COMPARE À QUOI
-----------------------
D'un côté, l'âge conjoncturel de la DREES : les taux de liquidation par âge
observés dans l'année, appliqués à une génération fictive. Il ne dépend donc
pas de la pyramide des âges, et c'est ce qui le rend comparable à une grille,
qui n'a pas de pyramide non plus.

De l'autre, l'âge de départ de la grille : pour chaque année, chaque cas type
apporte l'âge auquel il part cette année-là, et les treize sont pesés par les
effectifs de caisse de la DREES — la pondération même de la page « Coût »
(``castypes.poids_effectifs``).

Un cas type ne part pas chaque année : la grille avance de cinq ans en cinq
ans (``cout.PAS_GENERATIONS``), et un cas type y a donc un point de départ
tous les cinq ou six ans. L'âge de l'année intermédiaire est INTERPOLÉ entre
les deux points qui l'encadrent. On n'extrapole jamais au-delà du premier ou
du dernier point d'un cas type ; celui-là sort alors de la moyenne, et les
poids sont renormalisés sur les cas types qui restent.

QUATRE RÉSERVES, ET AUCUNE N'EST CACHÉE
-----------------------------------------
1. **Les poids sont des STOCKS.** ``poids_effectifs`` pèse chaque cas type par
   les retraités que ses caisses comptent, non par les liquidations de
   l'année : le dépôt n'a pas de flux par caisse. Un régime dont les départs
   ralentissent garde donc, ici, le poids de ses retraités d'hier.
2. **La grille n'est pas un échantillon.** Treize configurations du système,
   pas une population — c'est écrit dans ``castypes`` et ça ne change pas
   parce qu'on les pèse.
3. **Les deux âges ne mesurent pas la même chose.** Celui de la DREES est un
   comportement sous contrainte de règles ; celui de la grille est
   mécanique — chaque cas type part quand son droit s'ouvre, et ne choisit
   rien. L'écart est précisément ce que cette différence coûte, et c'est
   pourquoi il se mesure au lieu de se supposer.
4. **Le sexe n'est pas comparé.** La DREES publie les trois colonnes ; la
   grille ne distingue pas ses cas types par sexe. On compare à l'ensemble.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.castypes import (  # noqa: E402
    CAS_TYPES, CasType, calculer_cas_types, poids_effectifs,
)
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.cout import generations  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

SERIE = RACINE / "data" / "reference" / "macro" / "age_conjoncturel_depart.csv"

#: La colonne de la DREES à laquelle la grille se compare. Voir la réserve 4.
SEXE = "ensemble"


@dataclass
class Annee:
    """Ce que les deux côtés disent d'une même année."""

    annee: int
    drees: float
    grille: float
    ecart: float
    #: Cas types entrant dans la moyenne, sur les treize de la grille.
    cas_types: int


def age_conjoncturel_publie(sexe: str = SEXE) -> dict[int, float]:
    """La série de la DREES, aux seules années qu'elle publie.

    Lue à plat plutôt que par ``charger_serie_annuelle`` : une série annuelle
    reconduit la valeur du bord hors de sa fenêtre, et comparer la grille à une
    valeur reconduite reviendrait à prêter à la DREES un chiffre qu'elle n'a
    pas publié.
    """
    with SERIE.open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        return {
            int(ligne["annee"]): float(ligne["age"])
            for ligne in csv.DictReader(lignes)
            if ligne["sexe"] == sexe
        }


def departs_de_la_grille(
    simulateur: Simulateur,
    cas_types: tuple[CasType, ...] = CAS_TYPES,
    generations_retenues: tuple[int, ...] | None = None,
) -> dict[str, list[tuple[int, float]]]:
    """Pour chaque cas type, ses couples (année de liquidation, âge), triés.

    ``cas_types`` et ``generations_retenues`` ne servent pas ici : ils servent
    à ``age_depart_csp.py`` et à ``cout_age_depart.py``, qui rejouent la même
    lecture sur une grille MODIFIÉE ou sur un petit nombre de générations.
    Restreindre les générations ne change aucun point — la grille en donne un
    par génération —, cela n'en calcule que moins.
    """
    grille = calculer_cas_types(
        simulateur, cas_types,
        generations_retenues if generations_retenues is not None else generations(),
        "droit")
    departs: dict[str, list[tuple[int, float]]] = {}
    for (code, _), comparaison in grille.resultats.items():
        carriere = comparaison.carriere
        if carriere.age_liquidation is None:
            continue
        departs.setdefault(code, []).append(
            (carriere.annee_liquidation, float(carriere.age_liquidation))
        )
    for points in departs.values():
        points.sort()
    return departs


def age_interpole(points: list[tuple[int, float]], annee: int) -> float | None:
    """L'âge de départ de ce cas type cette année-là, ou ``None`` hors fenêtre."""
    if not points or annee < points[0][0] or annee > points[-1][0]:
        return None
    for (debut, age_debut), (fin, age_fin) in zip(points, points[1:]):
        if debut <= annee <= fin:
            if fin == debut:
                return age_debut
            return age_debut + (age_fin - age_debut) * (annee - debut) / (fin - debut)
    return points[-1][1]


def mesurer(simulateur: Simulateur,
            cas_types: tuple[CasType, ...] = CAS_TYPES) -> list[Annee]:
    """Le tableau, année par année, sur la fenêtre que la DREES publie.

    ``cas_types`` sert à ``cout_age_depart.py``, qui rejoue la mesure sur une
    grille dont les âges d'entrée ont été déplacés : la concordance d'ensemble
    survit-elle à la correction cas par cas ?
    """
    publie = age_conjoncturel_publie()
    departs = departs_de_la_grille(simulateur, cas_types)
    mesures: list[Annee] = []
    for annee in sorted(publie):
        poids = poids_effectifs(simulateur.effectifs, annee)
        ages = {code: age_interpole(points, annee)
                for code, points in departs.items()}
        retenus = {code: poids.get(code, 0.0) for code, age in ages.items()
                   if age is not None and poids.get(code, 0.0) > 0}
        total = sum(retenus.values())
        if total <= 0:
            continue
        grille = sum(part * ages[code] for code, part in retenus.items()) / total
        mesures.append(Annee(
            annee=annee,
            drees=publie[annee],
            grille=round(grille, 3),
            ecart=round(grille - publie[annee], 3),
            cas_types=len(retenus),
        ))
    return mesures


def imprimer(mesures: list[Annee]) -> None:
    print(f"{'année':>6} {'DREES':>7} {'grille':>7} {'écart':>7}  cas types")
    for ligne in mesures:
        print(f"{ligne.annee:>6} {ligne.drees:>7.2f} {ligne.grille:>7.2f} "
              f"{ligne.ecart:>+7.2f}  {ligne.cas_types}/{len(CAS_TYPES)}")
    ecarts = [ligne.ecart for ligne in mesures]
    moyen = sum(ecarts) / len(ecarts)
    pire = max(ecarts, key=abs)
    print(f"\nÉcart moyen {moyen:+.2f} an, le plus fort {pire:+.2f} an "
          f"({next(l.annee for l in mesures if l.ecart == pire)}).")
    print("La grille part plus tôt que la France réelle quand l'écart est négatif.")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--json", help="écrit le tableau dans ce fichier")
    arguments = analyseur.parse_args(argv)

    mesures = mesurer(Simulateur(Parametres()))
    if not mesures:
        print("aucune année comparable", file=sys.stderr)
        return 1
    imprimer(mesures)
    if arguments.json:
        Path(arguments.json).write_text(
            json.dumps([asdict(ligne) for ligne in mesures],
                       ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
