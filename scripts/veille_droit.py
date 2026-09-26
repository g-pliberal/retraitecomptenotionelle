#!/usr/bin/env python3
"""La veille du droit : les règles du scénario 1 à relire, et les sources à consulter.

    python scripts/veille_droit.py            # les fiches à relire, les sources
    python scripts/veille_droit.py --tout     # toutes les fiches, par état
    python scripts/veille_droit.py --jours 90 # seuil d'ancienneté (défaut 120)
    python scripts/veille_droit.py --strict   # code 1 si une fiche est à relire

Les règles sont les fiches de la carte, ``data/reference/regles/`` : une par
dispositif, avec les textes qui la fondent, les sources lues, la date de la
dernière lecture et de la prochaine, les exemples publiés qui la rejouent,
l'état. Ce script en est une vue, et ne décide rien : il dit quelles fiches
sont ``a_verifier`` ou ``manquante``, lesquelles n'ont pas été relues depuis
plus de ``--jours`` jours ou dont la date de relecture est passée, et quelles
sources consulter avant de toucher au scénario 1. Les sources à consulter et
le journal de chaque veille sont dans ``data/reference/legislation/veille.yaml``.

C'est le premier geste d'une session qui touche au scénario 1, et le dernier :
au début pour savoir quoi relire, à la fin pour ajouter au ``journal`` ce qui
a été consulté, trouvé, et laissé. ``tests/test_carte.py`` tient la forme des
fiches ; ``docs/veille_droit.md`` dit la procédure.
"""

from __future__ import annotations

import argparse
import collections
import sys
from datetime import date
from pathlib import Path

import yaml

from retraite_notionnelle.noyau import carte

RACINE = Path(__file__).resolve().parents[1]
REGISTRE = RACINE / "data" / "reference" / "legislation" / "veille.yaml"


def charger() -> dict:
    """Les sources à consulter et le journal de la veille."""
    return yaml.safe_load(REGISTRE.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--tout", action="store_true", help="imprime toutes les fiches")
    analyseur.add_argument("--jours", type=int, default=120, help="ancienneté maximale d'une lecture")
    analyseur.add_argument("--strict", action="store_true", help="code 1 si une fiche est à relire")
    analyseur.add_argument("--date", help="date du jour (AAAA-MM-JJ), pour rejouer")
    args = analyseur.parse_args(argv)
    aujourd_hui = date.fromisoformat(args.date) if args.date else date.today()

    registre = charger()
    etats = carte.etats()
    fiches = sorted(carte.fiches().values(), key=lambda f: (etats.index(f["etat"]), f["id"]))
    par_etat = collections.Counter(f["etat"] for f in fiches)
    journal = registre.get("journal") or []
    derniere = max((str(j["date"]) for j in journal), default="jamais")

    print(f"Carte des règles : {len(fiches)} fiches — "
          + ", ".join(f"{etat} {par_etat[etat]}" for etat in etats if par_etat[etat])
          + f". Dernière veille consignée : {derniere}.")
    print()

    revoir = carte.a_relire(aujourd_hui, args.jours)
    if revoir:
        print(f"À RELIRE ({len(revoir)}) :")
        for fiche, raisons in revoir:
            print(f"  - {fiche['id']} [{fiche['etat']}] : {', '.join(raisons)}")
            for question in (fiche.get("sources") or {}).get("a_relire") or []:
                print(f"      → {' '.join(str(question).split())}")
        print()
    else:
        print("Rien à relire au seuil demandé.\n")

    if args.tout:
        for fiche in fiches:
            sources = fiche.get("sources") or {}
            print(f"[{fiche['etat']}] {fiche['id']} — lue le {sources.get('lu_le')}, "
                  f"{len(fiche.get('exemples') or [])} exemple(s)")
            print(f"    {' '.join(str(fiche['intitule']).split())}")
        print()

    print("Sources à consulter avant de toucher au scénario 1 :")
    for source in registre.get("sources_a_consulter", []):
        print(f"  - {source['nom']} — {source.get('url', '')}")
    print("\nPuis : ajouter au `journal` de veille.yaml ce qui a été consulté, trouvé et laissé.")
    return 1 if (args.strict and revoir) else 0


if __name__ == "__main__":
    sys.exit(main())
