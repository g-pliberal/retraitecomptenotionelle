#!/usr/bin/env python3
"""Les indicateurs de cycle de vie de la grille des cas types, sous les six systèmes.

    python scripts/cycle_de_vie.py                    # conventions du dépôt (celles de l'OCDE)
    python scripts/cycle_de_vie.py --cor              # conventions du COR
    python scripts/cycle_de_vie.py --impot            # après impôt, barème projeté sur les prix
    python scripts/cycle_de_vie.py --impot salaire_moyen --cor
    python scripts/cycle_de_vie.py --indicateurs rendement_reel,patrimoine --scenarios actuel
    python scripts/cycle_de_vie.py --json grille.json # tout, case par case
    python scripts/cycle_de_vie.py --ages salaire_moyen --generations 1970,2000
    python scripts/cycle_de_vie.py --ages cadre --productivites cor_reference \
        --scenarios actuel,notionnel_liberal --cor
    python scripts/cycle_de_vie.py --equilibre        # les âges d'équilibre
    python scripts/cycle_de_vie.py --equilibre --generations 1962,1970 --json equilibre.json

Ce qu'il imprime : pour chaque indicateur et chaque système, un tableau des
treize cas types sur les sept générations de la grille
(``castypes.carriere_de_la_grille``). Les définitions, les deux conventions et
ce qu'elles laissent de côté sont dans ``retraite_notionnelle/cycle_de_vie.py`` ;
la confrontation au COR, à TRAJECTOiRE et à l'OCDE, dans
``tests/test_cycle_de_vie_references.py``.

LE PONT (action 161, étape 5). Les cas types ne se bâtissent qu'en Python
(``castypes.py``, que le coût lit) ; le reste se calcule par le portage, comme
le site le calcule d'une saisie : le script résout chaque case — les options de
sa carrière (``CasType.options``), l'âge où le pilote la fait partir —, et
``scripts/cycle_de_vie.mjs``, que node fait tourner, en rend les indicateurs,
les âges de départ et les âges d'équilibre. Sans node, le script s'arrête.

LES DEUX CONVENTIONS. Par défaut, celle de l'OCDE, sur les tables du dépôt :
la survie de génération du sexe du cas type, le patrimoine actualisé à 1,5 %
réel, la pension brute. Sous ``--cor``, celle des cas types du COR : les deux
sexes réunis, le décès à 60 ans plus l'espérance de vie à 60 ans de la
génération, la pension nette des prélèvements de chaque année (IPP).

APRÈS IMPÔT (``--impot``, action 138, étape 5) : la pension et les revenus de
chaque année, nets de leurs prélèvements, perdent aussi l'impôt sur le revenu
d'une personne seule sans enfant (``conventionApresImpot``),
sous les conventions du dépôt ou, avec ``--cor``, sous celles du COR. Le
barème se projette au-delà de la dernière loi de finances lue sur les prix
(``--impot`` ou ``--impot prix``) ou, comme l'OCDE, sur le salaire moyen
(``--impot salaire_moyen``). Avec ``--ages``, une colonne de plus : le taux de
remplacement après impôt au départ, le taux net de l'OCDE.

À CHAQUE ÂGE DE DÉPART (``--ages``, action 138, étape 9) : pour chaque cas type
nommé, chaque génération et chaque hypothèse de productivité du COR, un
tableau des âges de départ, de l'âge d'ouverture à l'âge d'annulation de la
décote, de trimestre en trimestre (``balayageDUneCarriere``), en net — la
pension nette rapportée au minimum vieillesse, le taux de remplacement net en
euros courants, constants et en salaire moyen, et les indicateurs de cycle de
vie. Le scénario 1 seul, sauf ``--scenarios``.

L'ÂGE D'ÉQUILIBRE (``--equilibre``, action 138, étape 9) : pour chaque
génération, sur la table commune, puis pour chaque cas type de la grille, sur
la mortalité de sa population, l'âge où le diviseur du compte rejoint celui de
la génération de référence à l'âge de référence — exact, et au premier mois,
comme l'ETK compte son âge cible —, et l'âge qui tient la part de la vie
passée en retraite de la référence, sous la convention du COR et sous celle du
dépôt (``ageDEquilibre``, ``ageDePartDeVieConstante``).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.calendrier import decomposer, formater_age  # noqa: E402
from retraite_notionnelle.castypes import CAS_TYPES, GENERATIONS, carriere_de_la_grille  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.donnees.chargement import charger_yaml  # noqa: E402
from retraite_notionnelle.donnees.impot_revenu import INDEXATIONS  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

#: Les indicateurs imprimés, leur titre et leur unité : ``%`` pour un taux
#: affiché en pour cent, ``x`` pour un rapport, ``ans`` pour une durée.
INDICATEURS = {
    "rendement_reel": ("Rendement interne réel (flux déflatés des prix)", "%"),
    "rendement_smpt": ("Rendement interne relatif (flux rapportés au salaire moyen)", "%"),
    "taux_recuperation": ("Taux de récupération (pensions sur cotisations, en salaire moyen)", "x"),
    "taux_annuite": ("Taux d'annuité (pensions sur revenus d'activité, en salaire moyen)", "%"),
    "taux_remplacement_cycle": ("Taux de remplacement sur le cycle de vie", "%"),
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

#: Les six systèmes, dans l'ordre du portage (``SCENARIOS``, cycle-de-vie.js).
SCENARIOS = tuple(LIBELLES)

#: Le programme qui calcule ce que le script imprime.
PROGRAMME = RACINE / "scripts" / "cycle_de_vie.mjs"

#: Le pas des âges de départ, un trimestre (``PAS_DES_AGES``, cycle-de-vie.js).
PAS_DES_AGES = 0.25


def portage(demande: dict) -> dict:
    """Ce que le portage rend d'une demande (``scripts/cycle_de_vie.mjs``).
    Sans node, rien : aucun moteur périmé ne prend le relais."""
    if shutil.which("node") is None:
        raise SystemExit("node absent : le cycle de vie se calcule par le portage "
                         "JavaScript (scripts/cycle_de_vie.mjs)")
    execution = subprocess.run(
        ["node", str(PROGRAMME)], input=json.dumps(demande), cwd=RACINE,
        capture_output=True, text=True, encoding="utf-8", check=False)
    if execution.returncode != 0:
        raise RuntimeError(f"{PROGRAMME.name} : {execution.stderr.strip()}")
    return json.loads(execution.stdout)


def _sans_echec(reponse: dict) -> None:
    """Un cas type nommé que le portage refuse arrête le script : seule la
    grille en écarte, comme le droit les écarte."""
    echecs = reponse.pop("echecs")
    if echecs:
        raise RuntimeError("; ".join(f"{cle} : {motif}" for cle, motif in echecs.items()))


def options(simulateur: Simulateur, cas, generation: int, age: float) -> dict:
    """Les options de la carrière du cas type ``cas`` né en ``generation``,
    liquidée à ``age``, celles que le portage reçoit. Sous
    ``Parametres.conventions_cor``, que le script n'allume jamais, la carrière
    d'un cas type se déforme en Python (``primes_projetees``) : rien ne passe."""
    if simulateur.parametres.conventions_cor:
        raise ValueError("les conventions de projection du COR ne passent pas au portage")
    return cas.options(generation, age)


def productivites(racine_donnees) -> tuple[str, ...]:
    """Les scénarios de projection du COR, de la productivité la plus basse à
    la plus haute : 0,4, 0,7 et 1,0 % par an depuis son rapport de juin 2025,
    qui a retiré le 1,3 % que TRAJECTOiRE balaie encore. Les jeux de
    référence d'une autre institution, l'OCDE, n'en sont pas."""
    scenarios = charger_yaml(Path(racine_donnees) / "reference" / "macro"
                             / "hypotheses_projection.yaml").get("scenarios", {})
    return tuple(sorted(scenarios, key=lambda nom: float(scenarios[nom]["productivite_reelle"])))


def calculer(simulateur: Simulateur, cor: bool = False, impot: str | None = None) -> dict:
    """Les indicateurs de chaque case de la grille, système par système, sous
    ``"<code>|<génération>"`` ; après impôt avec ``impot``, l'indexation du
    barème. Une case que le droit écarte (``carriere_de_la_grille``) ou que le
    portage refuse en est absente."""
    cas = []
    for code, generation in sorted((c.code, g) for c in CAS_TYPES for g in GENERATIONS):
        type_ = next(c for c in CAS_TYPES if c.code == code)
        try:
            carriere = carriere_de_la_grille(simulateur, type_, generation)
        except (ValueError, KeyError):
            continue
        cas.append({"cle": f"{code}|{generation}", "options": options(
            simulateur, type_, generation, carriere.age_liquidation)})
    return portage({"grille": {"cas": cas, "cor": cor, "impot": impot}})["resultats"]


def _titre_des_conventions(cor: bool, nettes: bool, impot: str | None) -> str:
    """Ce que les tableaux supposent."""
    if cor:
        titre = "Conventions du COR, nettes" if nettes else "Conventions du COR"
    elif nettes:
        titre = "Conventions du dépôt, nettes : survie de génération, patrimoine à 1,5 % réel"
    else:
        titre = "Conventions du dépôt : survie de génération, patrimoine à 1,5 % réel, brut"
    if impot is None:
        return titre
    indexation = "les prix" if impot == "prix" else "le salaire moyen"
    return (f"{titre} ; après impôt sur le revenu d'une personne seule, barème projeté sur "
            f"{indexation}")


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
            case = resultats.get(f"{cas.code}|{generation}")
            cellules.append(_cellule(case[scenario][indicateur], unite)
                            if case else f"{'—':>6}")
        lignes.append(f"{cas.libelle[:45]:<46}" + " ".join(cellules))
    return "\n".join(lignes)


#: Les colonnes du balayage des âges : l'en-tête, l'unité, et ce qu'elle lit
#: d'un départ pour un système.
COLONNES_AGES = (
    ("ASPA", "x", lambda depart, s: depart[s]["pension_aspa"]),
    ("Rnet €", "%", lambda depart, s: _remplacement(depart, s, "courants")),
    ("Rnet K", "%", lambda depart, s: _remplacement(depart, s, "constants")),
    ("Rnet S", "%", lambda depart, s: _remplacement(depart, s, "salaire_moyen")),
    ("Durée", "ans", lambda depart, s: depart[s]["duree_retraite"]),
    ("D/carr", "x", lambda depart, s: depart[s]["duree_relative"]),
    ("Récup", "x", lambda depart, s: depart[s]["taux_recuperation"]),
    ("Annuit", "%", lambda depart, s: depart[s]["taux_annuite"]),
    ("Rcycle", "%", lambda depart, s: depart[s]["taux_remplacement_cycle"]),
    ("TRIrée", "%2", lambda depart, s: depart[s]["rendement_reel"]),
    ("TRIsal", "%2", lambda depart, s: depart[s]["rendement_smpt"]),
    ("Patrim", "x", lambda depart, s: depart[s]["patrimoine"]),
)

LEGENDE_AGES = (
    "ASPA : pension nette sur le minimum vieillesse de l'année ; Rnet €, K, S : "
    "taux de remplacement net en euros courants, constants, en salaire moyen ; "
    "Durée : retraite (années) ; D/carr : durée de retraite sur durée de carrière ; "
    "Récup : taux de récupération ; Annuit, Rcycle : taux d'annuité et de "
    "remplacement sur le cycle de vie, nets sur nets ; TRIrée, TRIsal : rendement "
    "interne réel et relatif au salaire moyen ; Patrim : patrimoine retraite net, "
    "en années de dernier revenu brut.")

#: Après impôt, la colonne de plus : le taux de remplacement après impôt au
#: départ, le taux net de l'OCDE.
COLONNE_APRES_IMPOT = ("Rimp", "%", lambda depart, s: depart[s]["remplacement_apres_impot"])

LEGENDE_APRES_IMPOT = (
    "Après impôt : la pension et les revenus perdent aussi l'impôt sur le revenu de "
    "chaque année ; Rimp : taux de remplacement après impôt au départ, une année "
    "entière de pension sur une année entière du dernier revenu, chacune nette de "
    "ses prélèvements et de son impôt.")


def _remplacement(depart, scenario: str, unite: str) -> float | None:
    remplacement = depart[scenario]["remplacement_net"]
    return None if remplacement is None else remplacement[unite]


def tableau_des_ages(departs, scenario: str, titre: str, colonnes=COLONNES_AGES) -> str:
    """Un balayage, un système : une ligne par âge de départ."""
    lignes = [titre, f"{'âge':>6} {'année':>6} "
              + " ".join(f"{entete:>6}" for entete, _, _ in colonnes)]
    for depart in departs:
        lignes.append(f"{depart['age']:>6.2f} {depart['annee']:>6} " + " ".join(
            _cellule(lire(depart, scenario), unite) for _, unite, lire in colonnes))
    return "\n".join(lignes)


def balayer(cas_types: list, generations: list[int], productivites: list[str],
            cor: bool, impot: str | None = None, pas: float = PAS_DES_AGES
            ) -> tuple[dict[str, list[dict]], dict[str, str]]:
    """Les balayages des cas types nommés, génération par génération, sous
    chaque hypothèse de productivité, sous ``"<code>|<génération>|<hypothèse>"``,
    et le libellé de chaque hypothèse ; après impôt avec ``impot``,
    l'indexation du barème. Chaque cas type part de l'âge où le pilote le fait
    partir ; le portage balaie les autres (``balayageDUneCarriere``)."""
    cas, libelles = [], {}
    for productivite in productivites:
        simulateur = Simulateur(Parametres(scenario_projection=productivite))
        libelles[productivite] = simulateur.macro.projection["libelle"]
        for type_ in cas_types:
            for generation in generations:
                age = type_.age_liquidation_pour(simulateur, generation)
                cas.append({"cle": f"{type_.code}|{generation}|{productivite}",
                            "productivite": productivite, "age": age,
                            "options": options(simulateur, type_, generation, age)})
    reponse = portage({"ages": {"cas": cas, "cor": cor, "impot": impot, "pas": pas}})
    _sans_echec(reponse)
    return reponse["resultats"], libelles


def _imprimer_les_ages(arguments, analyseur, scenarios: list[str]) -> None:
    par_code = {cas.code: cas for cas in CAS_TYPES}
    cas_types = []
    for code in (nom for nom in arguments.ages.split(",") if nom):
        if code not in par_code:
            analyseur.error(f"cas type inconnu : {code} ({', '.join(par_code)})")
        cas_types.append(par_code[code])
    generations = ([int(g) for g in arguments.generations.split(",") if g]
                   if arguments.generations else list(GENERATIONS))
    connues = productivites(Parametres().racine_donnees)
    choisies = ([nom for nom in arguments.productivites.split(",") if nom]
                if arguments.productivites else list(connues))
    for nom in choisies:
        if nom not in connues:
            analyseur.error(f"productivité inconnue : {nom} ({', '.join(connues)})")
    resultats, hypotheses = balayer(cas_types, generations, choisies, arguments.cor,
                                    arguments.impot)
    print(_titre_des_conventions(arguments.cor, True, arguments.impot))
    print(LEGENDE_AGES)
    colonnes = COLONNES_AGES
    if arguments.impot is not None:
        print(LEGENDE_APRES_IMPOT)
        colonnes = COLONNES_AGES + (COLONNE_APRES_IMPOT,)
    for cle, departs in resultats.items():
        code, generation, productivite = cle.split("|")
        for scenario in scenarios if departs else ():
            print()
            print(tableau_des_ages(departs, scenario, (
                f"{par_code[code].libelle}, génération {generation} — {LIBELLES[scenario]} — "
                f"{hypotheses[productivite]}"), colonnes))
    if arguments.json:
        Path(arguments.json).write_text(json.dumps(resultats, ensure_ascii=False, indent=1),
                                        encoding="utf-8")


#: Les générations de la table commune, sauf ``--generations``.
GENERATIONS_EQUILIBRE = tuple(range(1940, 2001, 5))

LEGENDE_EQUILIBRE = (
    "Div : diviseur à l'âge de référence ; Coef : celui de la référence sur lui, "
    "le coefficient de l'ETK ; Équil. : âge où le diviseur rejoint celui de la "
    "référence, et premier mois où il le rejoint ; P COR, P 2 sx, P H, P F : âge qui "
    "tient la part de vie de la référence, sous la convention du COR, puis sous la "
    "survie de génération des deux sexes, des hommes, des femmes.")

#: Les tableaux des cas types : le titre, et ce qu'il lit de leurs âges.
TABLEAUX_EQUILIBRE = (
    ("Vingtile de niveau de vie de la mortalité de son diviseur",
     lambda ages: (ages["population"] or "commune").replace("niveau_de_vie_", "")),
    ("Âge de départ du droit de sa génération", lambda ages: ages["age_de_depart"]),
    ("Âge d'équilibre du diviseur, sur la mortalité de sa population",
     lambda ages: ages["diviseur"]["age"]),
    ("Âge de part de vie constante, survie de génération de son sexe et de sa population",
     lambda ages: ages["part_de_vie"]),
)


def equilibres(simulateur: Simulateur, generations, generations_des_cas) -> dict:
    """La référence du compte ; les âges d'équilibre de chaque génération de
    ``generations``, sur la table commune ; ceux de chaque cas type né en une
    génération de ``generations_des_cas``, sur la mortalité de la population
    où son salaire le range, à l'âge où le pilote le fait partir."""
    cas = [{"cle": f"{type_.code}|{generation}", "options": options(
                simulateur, type_, generation, type_.age_liquidation_pour(simulateur, generation))}
           for type_ in CAS_TYPES for generation in generations_des_cas]
    reponse = portage({"equilibre": {"generations": list(generations), "cas": cas}})
    _sans_echec(reponse)
    return reponse


def _valeur(valeur) -> str:
    return f"{valeur:>6}" if isinstance(valeur, str) else f"{valeur:>6.2f}"


def _mois(age: float) -> str:
    annees, mois = decomposer(age)
    return f"{annees}a{mois:02d}m"


def _imprimer_l_equilibre(arguments) -> None:
    choisies = ([int(g) for g in arguments.generations.split(",") if g]
                if arguments.generations else None)
    resultats = equilibres(Simulateur(Parametres()), choisies or GENERATIONS_EQUILIBRE,
                           choisies or GENERATIONS)
    reference, communs = resultats["reference"], resultats["table_commune"]
    cas_types = resultats["cas_types"]
    print(f"Référence du compte : la génération {reference['naissance']:.0f}, "
          f"{formater_age(reference['age'])} au 1er janvier {reference['annee']}.")
    print(LEGENDE_EQUILIBRE)
    print()
    print("Table commune")
    print(f"{'génér.':>6} {'Div':>6} {'Coef':>7} {'Équil.':>6} {'au mois':>8} "
          + " ".join(f"{entete:>6}" for entete in ("P COR", "P 2 sx", "P H", "P F")))
    for generation, ages in communs.items():
        diviseur = ages["diviseur"]
        print(f"{generation:>6} {diviseur['diviseur_a_l_age_de_reference']:>6.2f} "
              f"{diviseur['coefficient']:>7.4f} {diviseur['age']:>6.2f} "
              f"{_mois(diviseur['au_mois']):>8} "
              + " ".join(f"{ages[cle]:>6.2f}" for cle in (
                  "part_de_vie_cor", "part_de_vie_unisexe", "part_de_vie_hommes",
                  "part_de_vie_femmes")))
    colonnes = sorted({int(cle.split("|")[1]) for cle in cas_types})
    for titre, lire in TABLEAUX_EQUILIBRE:
        print()
        print(titre)
        print(f"{'':<46}" + " ".join(f"{generation:>6}" for generation in colonnes))
        for cas in CAS_TYPES:
            print(f"{cas.libelle[:45]:<46}" + " ".join(
                _valeur(lire(cas_types[f"{cas.code}|{generation}"])) for generation in colonnes))
    if arguments.json:
        Path(arguments.json).write_text(json.dumps(resultats, ensure_ascii=False, indent=1),
                                        encoding="utf-8")


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
    analyseur.add_argument("--generations", help="avec --ages ou --equilibre : les "
                                                 "générations, séparées par des virgules")
    analyseur.add_argument("--productivites", help="avec --ages : les hypothèses de "
                                                   "productivité, séparées par des virgules")
    analyseur.add_argument("--equilibre", action="store_true",
                           help="les âges d'équilibre de chaque génération et des cas types")
    analyseur.add_argument("--impot", nargs="?", const="prix", choices=INDEXATIONS,
                           help="après impôt sur le revenu, le barème projeté sur les prix "
                                "(par défaut) ou sur le salaire moyen")
    arguments = analyseur.parse_args(argv)
    if arguments.equilibre:
        _imprimer_l_equilibre(arguments)
        return 0

    indicateurs = [nom for nom in arguments.indicateurs.split(",") if nom]
    defaut = "actuel" if arguments.ages else ",".join(SCENARIOS)
    scenarios = [nom for nom in (arguments.scenarios or defaut).split(",") if nom]
    for nom in indicateurs:
        if nom not in INDICATEURS:
            analyseur.error(f"indicateur inconnu : {nom} ({', '.join(INDICATEURS)})")
    for nom in scenarios:
        if nom not in SCENARIOS:
            analyseur.error(f"système inconnu : {nom} ({', '.join(SCENARIOS)})")
    if arguments.ages:
        _imprimer_les_ages(arguments, analyseur, scenarios)
        return 0

    resultats = calculer(Simulateur(Parametres()), cor=arguments.cor, impot=arguments.impot)
    print(_titre_des_conventions(arguments.cor, arguments.impot is not None, arguments.impot))
    for indicateur in indicateurs:
        for scenario in scenarios:
            print()
            print(tableau(resultats, indicateur, scenario))
    if arguments.json:
        Path(arguments.json).write_text(json.dumps(resultats, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
