#!/usr/bin/env python3
"""Les indicateurs de cycle de vie de la grille des cas types, sous les six systèmes.

    python scripts/cycle_de_vie.py                    # conventions du dépôt (celles de l'OCDE)
    python scripts/cycle_de_vie.py --cor              # conventions du COR
    python scripts/cycle_de_vie.py --indicateurs rendement_reel,patrimoine --scenarios actuel
    python scripts/cycle_de_vie.py --json grille.json # tout, case par case

Ce qu'il imprime : pour chaque indicateur et chaque système, un tableau des
treize cas types sur les sept générations de la grille
(``castypes.calculer_cas_types``). Les définitions, les deux conventions et ce
qu'elles laissent de côté sont dans ``retraite_notionnelle/cycle_de_vie.py`` ;
la confrontation au COR, à TRAJECTOiRE et à l'OCDE, dans
``tests/test_cycle_de_vie_references.py``.

LES DEUX CONVENTIONS. Par défaut, celle de l'OCDE, sur les tables du dépôt :
la survie de génération du sexe du cas type, le patrimoine actualisé à 1,5 %
réel, la pension brute. Sous ``--cor``, celle des cas types du COR : les deux
sexes réunis, le décès à 60 ans plus l'espérance de vie à 60 ans de la
génération, la pension nette des prélèvements de l'année courante.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle import cycle_de_vie  # noqa: E402
from retraite_notionnelle.castypes import CAS_TYPES, GENERATIONS, calculer_cas_types  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

#: Les indicateurs imprimés, leur titre et leur unité : ``%`` pour un taux
#: affiché en pour cent, ``x`` pour un rapport, ``ans`` pour une durée.
INDICATEURS = {
    "rendement_reel": ("Rendement interne réel (flux déflatés des prix)", "%"),
    "rendement_smpt": ("Rendement interne relatif (flux rapportés au salaire moyen)", "%"),
    "taux_recuperation": ("Taux de récupération (pensions sur cotisations, en salaire moyen)", "x"),
    "patrimoine": ("Patrimoine retraite (années de dernier revenu)", "x"),
    "valeur_nette": ("Valeur actuelle nette (années de dernier revenu)", "x"),
    "remplacement_au_deces": ("Taux de remplacement au décès, contre le salaire d'alors", "%"),
    "duree_retraite": ("Durée de retraite (années)", "ans"),
    "part_de_vie": ("Part de la vie passée en retraite", "%"),
}

LIBELLES = {
    "actuel": "1. Système actuel",
    "notionnel_retroactif": "2. Notionnel rétroactif, part salariale",
    "notionnel_prospectif": "3. Notionnel dès la bascule, part salariale",
    "notionnel_retroactif_employeur": "4. Notionnel rétroactif, part patronale comprise",
    "notionnel_prospectif_employeur": "5. Notionnel dès la bascule, part patronale comprise",
    "notionnel_liberal": "6. Proposition libérale",
}


def calculer(simulateur: Simulateur, cor: bool = False) -> dict:
    """Les indicateurs de chaque case de la grille, système par système."""
    grille = calculer_cas_types(simulateur)
    resultats = {}
    for cle, comparaison in sorted(grille.resultats.items()):
        convention = (cycle_de_vie.convention_cor(simulateur, comparaison) if cor
                      else cycle_de_vie.Convention())
        resultats[cle] = cycle_de_vie.indicateurs_des_systemes(
            simulateur, comparaison, convention)
    return resultats


def _cellule(valeur: float | None, unite: str) -> str:
    if valeur is None:
        return f"{'—':>6}"
    if unite == "%":
        return f"{valeur * 100:>6.1f}"
    if unite == "x":
        return f"{valeur:>6.2f}"
    return f"{valeur:>6.1f}"


def tableau(resultats: dict, indicateur: str, scenario: str) -> str:
    titre, unite = INDICATEURS[indicateur]
    lignes = [f"{titre} — {LIBELLES[scenario]}",
              f"{'':<46}" + " ".join(f"{generation:>6}" for generation in GENERATIONS)]
    for cas in CAS_TYPES:
        cellules = []
        for generation in GENERATIONS:
            case = resultats.get((cas.code, generation))
            cellules.append(_cellule(getattr(case[scenario], indicateur), unite)
                            if case else f"{'—':>6}")
        lignes.append(f"{cas.libelle[:45]:<46}" + " ".join(cellules))
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--cor", action="store_true",
                           help="les conventions des cas types du COR")
    analyseur.add_argument("--indicateurs", default=",".join(INDICATEURS),
                           help="les indicateurs à imprimer, séparés par des virgules")
    analyseur.add_argument("--scenarios", default=",".join(cycle_de_vie.SCENARIOS),
                           help="les systèmes à imprimer, séparés par des virgules")
    analyseur.add_argument("--json", help="écrit toute la grille dans ce fichier")
    arguments = analyseur.parse_args(argv)

    indicateurs = [nom for nom in arguments.indicateurs.split(",") if nom]
    scenarios = [nom for nom in arguments.scenarios.split(",") if nom]
    for nom in indicateurs:
        if nom not in INDICATEURS:
            analyseur.error(f"indicateur inconnu : {nom} ({', '.join(INDICATEURS)})")
    for nom in scenarios:
        if nom not in cycle_de_vie.SCENARIOS:
            analyseur.error(f"système inconnu : {nom} ({', '.join(cycle_de_vie.SCENARIOS)})")

    resultats = calculer(Simulateur(Parametres()), cor=arguments.cor)
    print("Conventions du COR" if arguments.cor
          else "Conventions du dépôt : survie de génération, patrimoine à 1,5 % réel, brut")
    for indicateur in indicateurs:
        for scenario in scenarios:
            print()
            print(tableau(resultats, indicateur, scenario))
    if arguments.json:
        Path(arguments.json).write_text(json.dumps(
            {f"{code}|{generation}": {scenario: valeurs.dictionnaire()
                                      for scenario, valeurs in case.items()}
             for (code, generation), case in resultats.items()},
            ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
