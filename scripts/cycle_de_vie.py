#!/usr/bin/env python3
"""Les indicateurs de cycle de vie de la grille des cas types, sous les six systèmes.

    python scripts/cycle_de_vie.py                    # conventions du dépôt (celles de l'OCDE)
    python scripts/cycle_de_vie.py --cor              # conventions du COR
    python scripts/cycle_de_vie.py --indicateurs rendement_reel,patrimoine --scenarios actuel
    python scripts/cycle_de_vie.py --json grille.json # tout, case par case
    python scripts/cycle_de_vie.py --ages salaire_moyen --generations 1970,2000
    python scripts/cycle_de_vie.py --ages cadre --productivites cor_reference \
        --scenarios actuel,notionnel_liberal --cor

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

À CHAQUE ÂGE DE DÉPART (``--ages``, action 138, étape 9) : pour chaque cas type
nommé, chaque génération et chaque hypothèse de productivité du COR, un
tableau des âges de départ, de l'âge d'ouverture à l'âge d'annulation de la
décote, de trimestre en trimestre (``cycle_de_vie.balayage``), en net — la
pension nette rapportée au minimum vieillesse, le taux de remplacement net en
euros courants, constants et en salaire moyen, et les indicateurs de cycle de
vie. Le scénario 1 seul, sauf ``--scenarios``.
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
    if unite == "%2":
        return f"{valeur * 100:>6.2f}"
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


#: Les colonnes du balayage des âges : l'en-tête, l'unité, et ce qu'elle lit
#: d'un départ pour un système.
COLONNES_AGES = (
    ("ASPA", "x", lambda depart, s: depart.pensions_aspa[s]),
    ("Rnet €", "%", lambda depart, s: _remplacement(depart, s, "courants")),
    ("Rnet K", "%", lambda depart, s: _remplacement(depart, s, "constants")),
    ("Rnet S", "%", lambda depart, s: _remplacement(depart, s, "salaire_moyen")),
    ("Durée", "ans", lambda depart, s: depart.indicateurs[s].duree_retraite),
    ("D/carr", "x", lambda depart, s: depart.indicateurs[s].duree_relative),
    ("Récup", "x", lambda depart, s: depart.indicateurs[s].taux_recuperation),
    ("Annuit", "%", lambda depart, s: depart.indicateurs[s].taux_annuite),
    ("Rcycle", "%", lambda depart, s: depart.indicateurs[s].taux_remplacement_cycle),
    ("TRIrée", "%2", lambda depart, s: depart.indicateurs[s].rendement_reel),
    ("TRIsal", "%2", lambda depart, s: depart.indicateurs[s].rendement_smpt),
    ("Patrim", "x", lambda depart, s: depart.indicateurs[s].patrimoine),
)

LEGENDE_AGES = (
    "ASPA : pension nette sur le minimum vieillesse de l'année ; Rnet €, K, S : "
    "taux de remplacement net en euros courants, constants, en salaire moyen ; "
    "Durée : retraite (années) ; D/carr : durée de retraite sur durée de carrière ; "
    "Récup : taux de récupération ; Annuit, Rcycle : taux d'annuité et de "
    "remplacement sur le cycle de vie, nets sur nets ; TRIrée, TRIsal : rendement "
    "interne réel et relatif au salaire moyen ; Patrim : patrimoine retraite net, "
    "en années de dernier revenu brut.")


def _remplacement(depart, scenario: str, unite: str) -> float | None:
    remplacement = depart.remplacements[scenario]
    return None if remplacement is None else getattr(remplacement, unite)


def tableau_des_ages(departs, scenario: str, titre: str) -> str:
    """Un balayage, un système : une ligne par âge de départ."""
    lignes = [titre, f"{'âge':>6} {'année':>6} "
              + " ".join(f"{entete:>6}" for entete, _, _ in COLONNES_AGES)]
    for depart in departs:
        lignes.append(f"{depart.age:>6.2f} {depart.annee:>6} " + " ".join(
            _cellule(lire(depart, scenario), unite) for _, unite, lire in COLONNES_AGES))
    return "\n".join(lignes)


def balayer(cas_types: list, generations: list[int], productivites: list[str],
            cor: bool) -> tuple[dict[tuple[str, int, str], tuple], dict[str, str]]:
    """Les balayages des cas types nommés, génération par génération, sous
    chaque hypothèse de productivité, et le libellé de chaque hypothèse."""
    resultats, libelles = {}, {}
    for productivite in productivites:
        simulateur = Simulateur(Parametres(scenario_projection=productivite))
        libelles[productivite] = simulateur.macro.projection["libelle"]
        for cas in cas_types:
            for generation in generations:
                resultats[(cas.code, generation, productivite)] = cycle_de_vie.balayage(
                    simulateur, cas, generation, cor)
    return resultats, libelles


def _imprimer_les_ages(arguments, analyseur, scenarios: list[str]) -> None:
    par_code = {cas.code: cas for cas in CAS_TYPES}
    cas_types = []
    for code in (nom for nom in arguments.ages.split(",") if nom):
        if code not in par_code:
            analyseur.error(f"cas type inconnu : {code} ({', '.join(par_code)})")
        cas_types.append(par_code[code])
    generations = ([int(g) for g in arguments.generations.split(",") if g]
                   if arguments.generations else list(GENERATIONS))
    connues = cycle_de_vie.hypotheses_de_productivite(Parametres().racine_donnees)
    productivites = ([nom for nom in arguments.productivites.split(",") if nom]
                     if arguments.productivites else list(connues))
    for nom in productivites:
        if nom not in connues:
            analyseur.error(f"productivité inconnue : {nom} ({', '.join(connues)})")
    resultats, hypotheses = balayer(cas_types, generations, productivites, arguments.cor)
    print("Conventions du COR, nettes" if arguments.cor
          else "Conventions du dépôt, nettes : survie de génération, patrimoine à 1,5 % réel")
    print(LEGENDE_AGES)
    for (code, generation, productivite), departs in resultats.items():
        for scenario in scenarios if departs else ():
            print()
            print(tableau_des_ages(departs, scenario, (
                f"{par_code[code].libelle}, génération {generation} — {LIBELLES[scenario]} — "
                f"{hypotheses[productivite]}")))
    if arguments.json:
        Path(arguments.json).write_text(json.dumps(
            {f"{code}|{generation}|{productivite}": [
                {"age": depart.age, "annee": depart.annee, **{
                    scenario: {**depart.indicateurs[scenario].dictionnaire(),
                               "pension_nette": depart.pensions_nettes[scenario],
                               "pension_aspa": depart.pensions_aspa[scenario],
                               "remplacement_net": (None if depart.remplacements[scenario] is None
                                                    else vars(depart.remplacements[scenario]))}
                    for scenario in cycle_de_vie.SCENARIOS}}
                for depart in departs]
             for (code, generation, productivite), departs in resultats.items()},
            ensure_ascii=False, indent=1), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--cor", action="store_true",
                           help="les conventions des cas types du COR")
    analyseur.add_argument("--indicateurs", default=",".join(INDICATEURS),
                           help="les indicateurs à imprimer, séparés par des virgules")
    analyseur.add_argument("--scenarios", default=None,
                           help="les systèmes à imprimer, séparés par des virgules "
                                "(tous pour la grille, le scénario 1 pour --ages)")
    analyseur.add_argument("--json", help="écrit toute la grille dans ce fichier")
    analyseur.add_argument("--ages", help="les cas types à balayer âge par âge, "
                                          "séparés par des virgules")
    analyseur.add_argument("--generations", help="avec --ages : les générations, "
                                                 "séparées par des virgules")
    analyseur.add_argument("--productivites", help="avec --ages : les hypothèses de "
                                                   "productivité, séparées par des virgules")
    arguments = analyseur.parse_args(argv)

    indicateurs = [nom for nom in arguments.indicateurs.split(",") if nom]
    defaut = "actuel" if arguments.ages else ",".join(cycle_de_vie.SCENARIOS)
    scenarios = [nom for nom in (arguments.scenarios or defaut).split(",") if nom]
    for nom in indicateurs:
        if nom not in INDICATEURS:
            analyseur.error(f"indicateur inconnu : {nom} ({', '.join(INDICATEURS)})")
    for nom in scenarios:
        if nom not in cycle_de_vie.SCENARIOS:
            analyseur.error(f"système inconnu : {nom} ({', '.join(cycle_de_vie.SCENARIOS)})")
    if arguments.ages:
        _imprimer_les_ages(arguments, analyseur, scenarios)
        return 0

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
