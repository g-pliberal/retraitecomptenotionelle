#!/usr/bin/env python3
"""Le registre de conformité du scénario 1 au droit, et ce qui y a vieilli.

    python scripts/veille_droit.py            # état du registre, lignes à revoir
    python scripts/veille_droit.py --tout     # toutes les lignes, par état
    python scripts/veille_droit.py --jours 90 # seuil d'ancienneté (défaut 120)
    python scripts/veille_droit.py --strict   # code 1 si une ligne est à revoir

Le registre est ``data/reference/legislation/veille.yaml`` : une ligne par
règle du scénario 1, avec le texte, la source officielle lue, la date de la
lecture, l'exemple publié qui la rejoue, l'état. Ce script ne décide rien : il
dit quelles lignes sont ``a_verifier`` ou ``manque``, lesquelles n'ont pas été
relues depuis plus de ``--jours`` jours ou dont la date ``prochaine_veille``
est passée, et quelles sources consulter avant de toucher au scénario 1.

C'est le premier geste d'une session qui touche au scénario 1, et le dernier :
au début pour savoir quoi relire, à la fin pour ajouter au ``journal`` ce qui
a été consulté, trouvé, et laissé. Une règle nouvelle sans ligne ici est
refusée par ``tests/test_donnees.py``.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
REGISTRE = RACINE / "data" / "reference" / "legislation" / "veille.yaml"

ETATS = ("conforme", "transcrit", "approximation", "manque", "hors_modele", "a_verifier")
ORDRE = {etat: rang for rang, etat in enumerate(ETATS)}


def charger() -> dict:
    return yaml.safe_load(REGISTRE.read_text(encoding="utf-8"))


def a_revoir(entree: dict, aujourd_hui: date, jours: int) -> list[str]:
    raisons = []
    if entree["etat"] in ("a_verifier", "manque"):
        raisons.append(entree["etat"])
    verifie = date.fromisoformat(str(entree["verifie_le"]))
    if aujourd_hui - verifie > timedelta(days=jours):
        raisons.append(f"relu il y a {(aujourd_hui - verifie).days} jours")
    prochaine = entree.get("prochaine_veille")
    if prochaine and date.fromisoformat(str(prochaine)) <= aujourd_hui:
        raisons.append(f"veille prévue le {prochaine}")
    return raisons


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--tout", action="store_true", help="imprime toutes les lignes")
    analyseur.add_argument("--jours", type=int, default=120, help="ancienneté maximale d'une lecture")
    analyseur.add_argument("--strict", action="store_true", help="code 1 si une ligne est à revoir")
    analyseur.add_argument("--date", help="date du jour (AAAA-MM-JJ), pour rejouer")
    args = analyseur.parse_args(argv)
    aujourd_hui = date.fromisoformat(args.date) if args.date else date.today()

    registre = charger()
    entrees = sorted(registre["entrees"], key=lambda e: (ORDRE[e["etat"]], e["id"]))
    par_etat: dict[str, int] = {}
    for entree in entrees:
        par_etat[entree["etat"]] = par_etat.get(entree["etat"], 0) + 1
    journal = registre.get("journal") or []
    derniere = max((str(j["date"]) for j in journal), default="jamais")

    print(f"Registre : {len(entrees)} lignes — "
          + ", ".join(f"{etat} {n}" for etat, n in sorted(par_etat.items(), key=lambda x: ORDRE[x[0]]))
          + f". Dernière veille consignée : {derniere}.")
    print()

    revoir = [(e, a_revoir(e, aujourd_hui, args.jours)) for e in entrees]
    revoir = [(e, r) for e, r in revoir if r]
    if revoir:
        print(f"À REVOIR ({len(revoir)}) :")
        for entree, raisons in revoir:
            print(f"  - {entree['id']} [{entree['etat']}] : {', '.join(raisons)}")
            if entree.get("a_faire"):
                print(f"      → {' '.join(str(entree['a_faire']).split())}")
        print()
    else:
        print("Rien à revoir au seuil demandé.\n")

    if args.tout:
        for entree in entrees:
            temoins = entree.get("temoins") or []
            print(f"[{entree['etat']}] {entree['id']} — vérifié le {entree['verifie_le']}, "
                  f"{len(temoins)} témoin(s)")
            print(f"    {' '.join(str(entree['regle']).split())}")
        print()

    print("Sources à consulter avant de toucher au scénario 1 :")
    for source in registre.get("sources_a_consulter", []):
        print(f"  - {source['nom']} — {source.get('url', '')}")
    print("\nPuis : ajouter au `journal` de veille.yaml ce qui a été consulté, trouvé et laissé.")
    return 1 if (args.strict and revoir) else 0


if __name__ == "__main__":
    sys.exit(main())
