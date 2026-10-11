#!/usr/bin/env python3
"""La part des nouveaux retraités au minimum contributif : le modèle, l'EACR, TRAJECTOiRE.

    python scripts/part_minimum_contributif.py                     # les deux grilles
    python scripts/part_minimum_contributif.py --grille ensemble   # une seule
    python scripts/part_minimum_contributif.py --grille population # la population
    python scripts/part_minimum_contributif.py --processus 4       # sur quatre cœurs
    python scripts/part_minimum_contributif.py --json part.json

LA QUESTION
-----------
Combien de nouveaux retraités voient leur pension portée au minimum
contributif, et de combien ? L'enquête annuelle auprès des caisses de retraite
le compte, année de liquidation par année : la part des nouveaux retraités
(``regimes/minimum_contributif_liquidants.csv``), à la Cnav, à la MSA salariés
et, depuis 2019, aux régimes alignés réunis, le champ de TRAJECTOiRE ; et le
complément moyen qu'il leur sert (``regimes/minimum_contributif_montant.csv``,
en euros courants par mois). TRAJECTOiRE, le modèle de la DREES, les projette,
et prévient qu'il surestime la part (Études et résultats n° 1297, février 2024,
note 7). L'action 137 demande ce que le modèle en sait, et de le confronter aux
deux : la part, et le minimum moyen d'un bénéficiaire, en euros de 2023.

CE QUE LE MODÈLE EN SAIT
------------------------
Le minimum d'une carrière, entier : le taux plein qu'il exige, sa
proratisation, sa majoration au-delà de cent vingt trimestres cotisés,
l'écrêtement au plafond de pension tous régimes depuis 2012, le montant suivi
du Smic depuis la réforme de 2023 (``droit/completer.py``, fiche
``minimum_contributif``). Une PART demande une population, et le dépôt n'en a
pas. Il a deux grilles : les treize cas types de la page Coût, et les 791
carrières de la grille « ensemble » de ``scripts/grille_large.py``, qui les
déclinent aux parts que l'échantillon interrégimes de 2020 donne aux femmes,
aux polypensionnés, aux carrières courtes, aux périodes assimilées et aux
salaires. Le script passe chaque carrière au scénario 1, sous les conventions
de la page (``Simulateur.pour_la_projection``), et compte, parmi celles qui
liquident une pension du régime général, celles dont le minimum contributif la
relève, chacune à son poids de personnes de 2020 (``grille_large.composition``).

Deux lectures :

``par année de liquidation``  les carrières de toutes les générations qui
                              liquident leur pension du régime général cette
                              année-là, chaque génération pesant autant : ce
                              que l'EACR compte. La grille fait naître chaque
                              génération en janvier, et une année où aucune ne
                              part à l'âge du taux plein des carrières courtes
                              — 2018 et 2021, que le relèvement de cet âge
                              enjambe — ne compterait que des carrières
                              complètes : chaque génération s'étale donc sur
                              ses douze mois de naissance (:func:`etalement`) ;
``par génération``            les carrières d'une génération, quelle que soit
                              l'année de leur départ : ce que les tableaux de
                              TRAJECTOiRE donnent.

CE QUE LA MESURE N'EST PAS
--------------------------
Une population, pas plus que la grille (``scripts/grille_large.py``, même
section). Trois de ses conventions jouent dans le sens de TRAJECTOiRE, qui en
nomme deux : chaque carrière part au premier âge du taux plein, que le minimum
exige, quand une part des liquidants part avec une décote ; personne ne renonce
à ce qu'il peut demander ; et toutes les pensions se liquident ensemble, la
condition de subsidiarité étant toujours remplie. Et les axes de la grille sont
indépendants : le salaire d'une femme y est celui d'un homme, ce qui efface une
part de ce que l'EACR mesure entre les sexes. La population de
``scripts/grille_large.py`` (``--grille population``, action 136, étape 6)
donne à chaque sexe les siens, et au salariat privé le temps partiel.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import multiprocessing
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts"))

import grille_large as G  # noqa: E402
from retraite_notionnelle import memoire  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402
from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

#: Les grilles mesurées par défaut : celle de la page, et la plus large.
GRILLES = ("reference", "ensemble")

#: Le régime dont la pension entre dans le champ, et que le minimum relève : le
#: régime général, seul régime aligné des grilles, qui sert les indépendants
#: depuis 2020 et ne se distingue pas ici des salariés agricoles.
REGIME = "regime_general"

#: Les années de liquidation que l'EACR observe, puis trois que TRAJECTOiRE
#: projette (Études et résultats n° 1297, graphique 2b).
ANNEES = tuple(range(2012, 2025)) + (2030, 2040, 2050)

#: Les âges entre lesquels la pension du régime général d'une carrière de la
#: grille peut prendre effet : les générations qu'une année de liquidation
#: réclame s'en déduisent.
AGES_DE_DEPART = (55, 70)

#: Les générations que la lecture par génération imprime : celles des
#: liquidants observés, puis, de cinq en cinq, celles que TRAJECTOiRE projette.
GENERATIONS_IMPRIMEES = (1950, 1955, 1960, 1965, 1970, 1975, 1980, 1985, 1990)

#: Ce que le détail du minimum dit quand sa majoration est servie
#: (:func:`retraite_notionnelle.droit.completer.completer`).
MAJORATION = "majoration des périodes cotisées comprise"

#: Les euros constants des tableaux de TRAJECTOiRE.
ANNEE_EUROS = 2023

#: Ce que TRAJECTOiRE publie, sur les régimes alignés, avant la loi du 30
#: décembre 2025 et aux hypothèses du COR de juin 2023 : Martin Chopard,
#: Études et résultats n° 1297, DREES, février 2024 (``drees_er_1297_minimum_contributif``
#: au registre des sources). Les parts en pour cent, les montants en euros bruts
#: par mois : le gain moyen que le minimum donne à ses bénéficiaires, en euros
#: de l'année ``euros_de``.
TRAJECTOIRE = {
    "liquidants_2024": {
        "source": "tableau 1 : les liquidants de 2024, euros courants",
        "sans_reforme_de_2023": 25.7, "avec_reforme_de_2023": 30.0,
        "montant_avant_relevement": 110, "montant_apres_relevement": 136,
        "euros_de": 2024,
    },
    "liquidants_2050": {
        "source": "graphique 2b, sa lecture : les liquidants de 2050",
        "sans_reforme_de_2023": 14.3, "avec_reforme_de_2023": 26.5,
    },
    "generation_1975": {
        "source": "tableau 3 : la génération 1975, euros de 2023",
        "F": 31.6, "H": 18.1, "majore_F": 15.0, "majore_H": 5.2,
        "montant_F": 106, "montant_H": 82,
        "euros_de": ANNEE_EUROS,
    },
}

#: Les caisses de l'EACR que la mesure imprime : le champ de TRAJECTOiRE, les
#: régimes alignés réunis, est le plus proche de la grille, dont le régime
#: général tient lieu des trois (:data:`REGIME`).
CAISSES = ("cnav", "msa_salaries", "regimes_alignes")

SEXES = ("ensemble", "F", "H")


# -- la simulation ---------------------------------------------------------------

def _mesurer(parametres: Parametres, morceau: tuple) -> list[tuple]:
    """Le minimum de chaque carrière du morceau, au scénario 1 de la page.

    Rend, pour chaque ``(indice, cas type, génération)`` qui liquide une
    pension du régime général, ``(indice, génération, (année et mois d'effet
    de cette pension, minimum annuel qui la relève, majoration servie, minimum
    avant écrêtement))``, ce dernier ``None`` avant 2012 ; ``(indice,
    génération, None)`` pour une carrière que le moteur refuse.
    """
    simulateur = Simulateur(parametres).pour_la_projection()
    sortie = []
    for indice, cas, generation in morceau:
        try:
            carriere = cas.construire(simulateur, generation)
            actuel = simulateur.echeancier(carriere).au_depart
        except (ValueError, KeyError):
            sortie.append((indice, generation, None))
            continue
        pensions = [p for p in actuel.pensions_par_regime
                    if p.regime == REGIME and p.montant > 0.0]
        if not pensions:
            continue
        annee, mois = min(
            (int(p.date_effet[:4]), int(p.date_effet[5:7])) if p.date_effet
            else (carriere.annee_liquidation, carriere.mois_liquidation)
            for p in pensions)
        minimum, majore = 0.0, False
        for avantage in actuel.avantages_appliques:
            if avantage.code == "minimum_contributif":
                minimum += somme_ordonnee(montant for regime, montant in avantage.par_regime
                                          if regime == REGIME)
                majore = majore or MAJORATION in avantage.detail
        avant = (None if actuel.minimum_ecrete is None
                 else actuel.minimum_ecrete.avant_ecretement)
        sortie.append((indice, generation, (annee, mois, minimum, majore, avant)))
    return sortie


def _mesurer_morceau(parametres: Parametres, morceau: tuple) -> list[tuple]:
    """Le morceau, gardé sous l'empreinte du modèle et le code de ce script."""
    return memoire.memoriser_pour(
        parametres, ("part_minimum_contributif", parametres, morceau),
        lambda: _mesurer(parametres, morceau))


def simuler(parametres: Parametres, variantes: list, generations: tuple[int, ...],
            processus: int) -> list[tuple]:
    """Chaque carrière de la grille, à chaque génération : un morceau par
    génération, sur ``processus`` cœurs."""
    morceaux = [tuple((indice, v.cas, generation) for indice, v in enumerate(variantes))
                for generation in generations]
    if processus <= 1:
        resultats = [_mesurer_morceau(parametres, morceau) for morceau in morceaux]
    else:
        with ProcessPoolExecutor(max_workers=processus,
                                 mp_context=multiprocessing.get_context("spawn")) as pool:
            resultats = list(pool.map(_mesurer_morceau, [parametres] * len(morceaux),
                                      morceaux))
    return [ligne for resultat in resultats for ligne in resultat]


# -- les parts -------------------------------------------------------------------

def _part(lot: list[tuple[float, tuple]], coefficients: dict[int, float]) -> dict:
    """Ce qu'un lot de carrières pesées dit du minimum : la part des
    bénéficiaires, celle de la majoration, le minimum mensuel moyen d'un
    bénéficiaire en euros de :data:`ANNEE_EUROS`, la part des éligibles que
    l'écrêtement prive de tout."""
    total = somme_ordonnee(p for p, _ in lot)
    if total <= 0.0:
        return {}
    servis = [(p, m) for p, m in lot if m[2] > 0.0]
    poids_servis = somme_ordonnee(p for p, _ in servis)
    eligibles = somme_ordonnee(p for p, m in lot if m[4] is not None and m[4] > 0.0)
    prives = somme_ordonnee(p for p, m in lot
                            if m[4] is not None and m[4] > 0.0 and m[2] <= 0.0)
    return {
        "poids": total,
        "part": 100.0 * poids_servis / total,
        "part_majoree": 100.0 * somme_ordonnee(p for p, m in servis if m[3]) / total,
        "montant": (somme_ordonnee(p * m[2] / 12.0 * coefficients[m[0]] for p, m in servis)
                    / poids_servis) if poids_servis else 0.0,
        "prives_par_l_ecretement": 100.0 * prives / eligibles if eligibles else 0.0,
    }


def etalement(generation: int, annee: int, mois: int) -> dict[int, float]:
    """Les années civiles où partent les douze mois de naissance d'une
    génération que la grille fait naître en janvier, et la part de chacune.

    Une carrière née en janvier dont la pension prend effet en ``mois`` de
    ``annee`` part au même âge, né un autre mois, autant de mois plus tard : à
    62 ans, toute la génération part la même année ; à 66 ans et 7 mois, cinq
    mois de naissance partent cette année-là et sept l'année suivante. Les
    naissances sont tenues pour égales d'un mois à l'autre.
    """
    age = (annee - generation) * 12 + (mois - 1)
    annees: dict[int, float] = {}
    for naissance in range(12):
        depart = generation + (naissance + age) // 12
        annees[depart] = annees.get(depart, 0.0) + 1.0 / 12.0
    return annees


def parts(variantes: list, poids: list[float], lignes: list[tuple],
          coefficients: dict[int, float], groupes_de) -> dict:
    """Les parts de chaque groupe, sexe par sexe. ``groupes_de(génération,
    mesure)`` dit à quels groupes une ligne appartient, et pour quelle part de
    son poids : la génération, entière, ou les années de liquidation."""
    groupes: dict = {}
    for indice, generation, mesure in lignes:
        if mesure is None:
            continue
        sexe = variantes[indice].cas.sexe
        for groupe, part in groupes_de(generation, mesure):
            for s in ("ensemble", sexe):
                groupes.setdefault(groupe, {}).setdefault(s, []).append(
                    (poids[indice] * part, mesure))
    return {groupe: {s: _part(lot, coefficients) for s, lot in sorted(par_sexe.items())}
            for groupe, par_sexe in sorted(groupes.items())}


def _lire_eacr(racine: Path, nom: str, colonne: str) -> dict[tuple[int, str, str], float]:
    chemin = racine / "reference" / "regimes" / nom
    with chemin.open(encoding="utf-8") as flux:
        lignes = csv.DictReader(l for l in flux if not l.lstrip().startswith("#"))
        return {(int(l["annee"]), l["caisse"], l["sexe"]): float(l[colonne]) for l in lignes}


def observees(racine: Path) -> dict[tuple[int, str, str], float]:
    """La part que l'EACR observe : ``(année, caisse, sexe) -> part``."""
    return _lire_eacr(racine, "minimum_contributif_liquidants.csv", "part")


def montants_observes(racine: Path) -> dict[tuple[int, str, str], float]:
    """Le minimum moyen que l'EACR observe, en euros courants par mois :
    ``(année, caisse, sexe) -> montant``."""
    return _lire_eacr(racine, "minimum_contributif_montant.csv", "montant")


def en_euros_de_reference(montants: dict[tuple, float], coefficient_prix) -> dict[tuple, float]:
    """Des montants en euros courants de l'année qui ouvre leur clé, passés en
    euros de :data:`ANNEE_EUROS` par ``coefficient_prix(année, ANNEE_EUROS)``."""
    return {cle: montant * coefficient_prix(cle[0], ANNEE_EUROS)
            for cle, montant in sorted(montants.items())}


def generations_requises(annees: tuple[int, ...]) -> tuple[int, ...]:
    """Les générations dont une carrière peut liquider l'une de ces années, et
    celles que la lecture par génération imprime."""
    requises = {g for annee in annees
                for g in range(annee - AGES_DE_DEPART[1], annee - AGES_DE_DEPART[0] + 1)}
    return tuple(sorted(requises | set(GENERATIONS_IMPRIMEES)))


def mesurer(noms: tuple[str, ...] = GRILLES, processus: int = 1,
            annees: tuple[int, ...] = ANNEES, parametres: Parametres | None = None) -> dict:
    """Chaque grille, ses parts par année de liquidation et par génération, à côté
    de ce que l'EACR observe et de ce que TRAJECTOiRE publie, les montants en
    euros de :data:`ANNEE_EUROS`."""
    parametres = parametres if parametres is not None else Parametres()
    racine = parametres.racine_donnees
    source = G.eir(racine)
    _, valeurs = G.centiles(racine)
    points = G.multiplicateurs(valeurs)
    simulateur = Simulateur(parametres)
    effectifs = simulateur.effectifs
    generations = generations_requises(annees)
    coefficient_prix = simulateur.macro.coefficient_prix
    publies = TRAJECTOIRE["liquidants_2024"]
    resultat = {"millesime_des_poids": source.millesime, "generations": list(generations),
                "eacr": {f"{a}/{c}/{s}": v for (a, c, s), v in sorted(observees(racine).items())},
                "eacr_montants": {
                    f"{a}/{c}/{s}": v for (a, c, s), v
                    in en_euros_de_reference(montants_observes(racine), coefficient_prix).items()},
                "trajectoire": TRAJECTOIRE,
                "trajectoire_montants_2024": {
                    cle: publies[cle] * coefficient_prix(publies["euros_de"], ANNEE_EUROS)
                    for cle in ("montant_avant_relevement", "montant_apres_relevement")},
                "grilles": {}}
    for nom in noms:
        debut = time.time()
        variantes = G.grille(nom, effectifs, source, points)
        poids = G.poids_retraites(variantes, effectifs, source.millesime)
        lignes = simuler(parametres, variantes, generations, processus)
        coefficients = {a: simulateur.macro.coefficient_prix(a, ANNEE_EUROS)
                        for a in {m[0] for _, _, m in lignes if m is not None}}
        voulues = set(annees)
        par_annee = parts(
            variantes, poids, lignes, coefficients,
            lambda generation, mesure: [
                (annee, part) for annee, part
                in etalement(generation, mesure[0], mesure[1]).items() if annee in voulues])
        par_generation = parts(variantes, poids, lignes, coefficients,
                               lambda generation, mesure: [(generation, 1.0)])
        resultat["grilles"][nom] = {
            "carrieres": len(variantes),
            "refusees": len([m for _, _, m in lignes if m is None]),
            "par_annee": {str(a): v for a, v in par_annee.items()},
            "par_generation": {str(g): v for g, v in par_generation.items()},
            "secondes": round(time.time() - debut, 1),
        }
    return resultat


# -- l'impression ----------------------------------------------------------------

def _pc(valeur: float | None) -> str:
    return "     —" if valeur is None or (isinstance(valeur, float) and math.isnan(valeur)) \
        else f"{valeur:5.1f} %"


def _points(modele: float | None, observe: float | None) -> str:
    return "     —" if modele is None or observe is None else f"{modele - observe:+6.1f}"


def _euros(valeur: float | None) -> str:
    return "    —" if valeur is None else f"{valeur:3.0f} €"


def imprimer(resultat: dict) -> None:
    eacr = {tuple(cle.split("/")): v for cle, v in resultat["eacr"].items()}
    montants = {tuple(cle.split("/")): v for cle, v in resultat["eacr_montants"].items()}
    trajectoire = resultat["trajectoire"]
    for nom, grille in resultat["grilles"].items():
        print(f"\nGrille « {nom} » : {grille['carrieres']} carrières, poids de personnes "
              f"de {resultat['millesime_des_poids']}, {grille['refusees']} couples refusés "
              f"par le moteur, {grille['secondes']} s")
        print("\nPar année de liquidation de la pension du régime général : la part")
        print("  année    modèle  dont maj.   EACR Cnav    MSA sal.     alignés   écart"
              "    femmes (alignés)   hommes (alignés)")
        for annee, par_sexe in grille["par_annee"].items():
            e = par_sexe.get("ensemble", {})
            f, h = par_sexe.get("F", {}), par_sexe.get("H", {})
            cnav, msa, alignes = (eacr.get((annee, caisse, "ensemble")) for caisse in CAISSES)
            ef, eh = (eacr.get((annee, "regimes_alignes", sexe)) for sexe in ("F", "H"))
            marque = "*" if annee == "2024" else " "
            print(f"  {annee}   {_pc(e.get('part'))}   {_pc(e.get('part_majoree'))}   "
                  f"{_pc(cnav)}{marque}   {_pc(msa)}{marque}   {_pc(alignes)}{marque}  "
                  f"{_points(e.get('part'), alignes)}    "
                  f"{_pc(f.get('part'))} ({_pc(ef).strip()})   "
                  f"{_pc(h.get('part'))} ({_pc(eh).strip()})")
        print("  * l'estimation de la DREES ; les régimes alignés réunis depuis 2019, "
              "première année où ils comptent des personnes ;")
        print("    TRAJECTOiRE, liquidants des régimes alignés : "
              f"{trajectoire['liquidants_2024']['avec_reforme_de_2023']} % en 2024 "
              f"({trajectoire['liquidants_2024']['sans_reforme_de_2023']} % sans la réforme "
              f"de 2023), {trajectoire['liquidants_2050']['avec_reforme_de_2023']} % en 2050")
        print(f"\nPar année de liquidation : le minimum moyen d'un bénéficiaire, "
              f"en euros de {ANNEE_EUROS} par mois")
        print("  année   modèle   femmes   hommes   EACR Cnav   MSA sal.   alignés")
        for annee, par_sexe in grille["par_annee"].items():
            e = par_sexe.get("ensemble", {})
            f, h = par_sexe.get("F", {}), par_sexe.get("H", {})
            cnav, msa, alignes = (montants.get((annee, caisse, "ensemble")) for caisse in CAISSES)
            print(f"  {annee}    {_euros(e.get('montant'))}    {_euros(f.get('montant'))}    "
                  f"{_euros(h.get('montant'))}      {_euros(cnav)}      {_euros(msa)}     "
                  f"{_euros(alignes)}")
        publies, courants = resultat["trajectoire_montants_2024"], trajectoire["liquidants_2024"]
        print(f"  TRAJECTOiRE, liquidants de 2024 : {publies['montant_avant_relevement']:.0f} € "
              f"avant le relèvement de 2023, {publies['montant_apres_relevement']:.0f} € après "
              f"({courants['montant_avant_relevement']} et {courants['montant_apres_relevement']} "
              f"€ de {courants['euros_de']})")
        print("\nPar génération")
        print("  génér.   ensemble    femmes    hommes   majorée F   majorée H   "
              f"Mico moyen F / H (€ {ANNEE_EUROS})   éligibles privés")
        for generation, par_sexe in grille["par_generation"].items():
            if int(generation) not in GENERATIONS_IMPRIMEES:
                continue
            e = par_sexe.get("ensemble", {})
            f, h = par_sexe.get("F", {}), par_sexe.get("H", {})
            print(f"  {generation}    {_pc(e.get('part'))}   {_pc(f.get('part'))}   "
                  f"{_pc(h.get('part'))}   {_pc(f.get('part_majoree'))}     "
                  f"{_pc(h.get('part_majoree'))}     {f.get('montant', 0):5.0f} / "
                  f"{h.get('montant', 0):3.0f} €                     "
                  f"{_pc(e.get('prives_par_l_ecretement'))}")
        g = trajectoire["generation_1975"]
        print(f"  TRAJECTOiRE, génération 1975 : femmes {g['F']} %, hommes {g['H']} %, "
              f"majorée {g['majore_F']} et {g['majore_H']} %, "
              f"{g['montant_F']} et {g['montant_H']} € de {ANNEE_EUROS}")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--grille", action="append", choices=G.GRILLES,
                           help="une grille de scripts/grille_large.py (plusieurs possibles)")
    analyseur.add_argument("--processus", type=int, default=G.processus_par_defaut(),
                           help="cœurs de la simulation (défaut : tous)")
    analyseur.add_argument("--json", type=Path, help="écrit le résultat dans ce fichier")
    arguments = analyseur.parse_args(argv)
    resultat = mesurer(tuple(arguments.grille or GRILLES), arguments.processus)
    imprimer(resultat)
    if arguments.json:
        arguments.json.write_bytes(
            json.dumps(resultat, ensure_ascii=False, indent=1).encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
