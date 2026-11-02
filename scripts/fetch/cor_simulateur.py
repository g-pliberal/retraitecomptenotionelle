#!/usr/bin/env python3
"""Les données du simulateur du COR, que ses copies gardent depuis sa fermeture.

    python scripts/fetch/cor_simulateur.py
    python scripts/fetch/source_locale.py --recuperer   # les deux fichiers dans data/brut/

POURQUOI CE TÉMOIN. Le simulateur du COR — trois leviers, l'âge, le taux de
prélèvement et la pension relative, qu'on règle à la main sur ses projections —
est fermé depuis juillet 2026 « pour révision des scénarios économiques », et
son fichier de données (``fileProjection.json``) n'est plus servi. Son code
retire G retraités par année de recul de l'âge, G l'effectif d'une génération
qui arrive aux âges de la retraite, et en compte la moitié parmi les cotisants
(``js/script.js``, l. 403) : le geste que ``releve_age``
(``src/retraite_notionnelle/leviers.py``) reconstruit d'après sa documentation
de 2016. ``tests/test_leviers.py`` les confronte sur ses propres séries, dont
le rapport annuel ne publie ni les retraités en niveau, ni G.

LA SOURCE. Deux millésimes du fichier, que des copies gardent
(``data/sources.yaml``, ``cor_simulateur_2019`` et ``cor_simulateur_2021``, au
blocage ``retire``) : celui de juin 2019, dans ``brunoscherrer/retraites``,
identique à l'octet à celui de ``nosretraites/roc-retraites``, la copie du site
entier, code compris ; celui que ``ChallengesRedac/simulateurRetraite`` nomme
``donneesCor2021.json``. Le COR n'en permet la reproduction qu'avec son
accord : les fichiers restent dans ``data/brut/``, et le témoin n'en garde que
les huit séries du levier de l'âge, aux six scénarios, chaque cinquième année
de 2030 à 2070. Le manifeste donne l'adresse, la copie et l'empreinte de
chacun ; un fichier déposé dans ``data/brut/`` sous son nom local passe avant
la copie, et doit porter la même empreinte.

Le témoin est versionné : les tests le relisent sans réseau.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_locale import jeux_bloques, lire_ou_telecharger, telecharger  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "tests" / "temoins" / "cor_simulateur.json"

#: Les jeux du manifeste, par millésime.
JEUX = {"2019": "cor_simulateur_2019", "2021": "cor_simulateur_2021"}

#: Les séries dont se sert le levier de l'âge du simulateur (``js/script.js``,
#: l. 383-411), avec ce qu'elles mesurent.
SERIES = {
    "NR": "retraités de droit direct, tous régimes confondus, en milliers",
    "NC": "personnes en emploi, ou cotisants, en milliers",
    "G": "effectif moyen d'une génération arrivant aux âges de la retraite, en milliers",
    "T": "taux de prélèvement global, en part des revenus d'activité bruts",
    "P": "pension moyenne de droit direct, en part du revenu d'activité brut moyen",
    "dP": ("autres dépenses de retraite par retraité de droit direct, en part du "
           "revenu d'activité brut moyen"),
    "PdP": "P + dP, que le code lit pour le solde à législation inchangée (l. 397)",
    "A": "âge effectif moyen de départ, en années",
}
SCENARIOS = ("1", "2", "3", "4", "5", "6")
ANNEES = tuple(range(2030, 2071, 5))


def extraire(donnees: dict) -> dict[str, dict[str, dict[str, float]]]:
    """Les huit séries, aux six scénarios et aux années du témoin."""
    return {nom: {scenario: {str(annee): float(donnees[nom][scenario][str(annee)])
                             for annee in ANNEES}
                  for scenario in SCENARIOS}
            for nom in SERIES}


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.parse_args(argv)

    manifeste = {jeu["id"]: jeu for jeu in jeux_bloques()}
    temoin = {
        "source": {
            "editeur": "Conseil d'orientation des retraites",
            "reference": ("Le fichier de données du simulateur du COR (fileProjection.json), "
                          "fermé depuis juillet 2026, lu dans ses copies ; son code, "
                          "js/script.js, l. 383-411, dans nosretraites/roc-retraites "
                          "(commit d375f10)"),
            "manifeste": "data/sources.yaml : " + ", ".join(JEUX.values()),
        },
        "unites": SERIES,
        "millesimes": {},
    }
    for millesime, ident in JEUX.items():
        jeu = manifeste[ident]
        octets = lire_ou_telecharger(jeu["url"], telecharger, nom_local=jeu["fichier_local"],
                                     miroir=jeu["miroir"], sha256=jeu["sha256"])
        temoin["millesimes"][millesime] = {
            "source": {
                "url": jeu["url"],
                "copie": jeu["miroir"],
                "sha256": jeu["sha256"],
                "lu_le": date.today().isoformat(),
            },
            "series": extraire(json.loads(octets)),
        }
    SORTIE.write_text(json.dumps(temoin, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} écrit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
