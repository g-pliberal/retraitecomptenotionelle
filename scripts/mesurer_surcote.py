"""La surcote de la population, sous une version de ``grille_large.py`` et sans elle.

    python scripts/mesurer_surcote.py --processus 4 --json mesure.json
    python scripts/mesurer_surcote.py --grille reference --processus 1

POURQUOI CE SCRIPT. La note de la trente-septième version (action 138, étape
14, ``docs/feuille_de_route/138/2026-11-03-etape-14-surcote-du-salariat-selon-la-generation.md``)
tirait ses mesures d'un pilote resté hors du dépôt, qu'on ne pouvait refaire
(relecture R-I, point 4.4). Ce script les refait, telles que la note les
décrit : il construit la population, la constante ``--constante`` allumée
(« version ») puis éteinte (« éteinte »), vérifie que l'une et l'autre ont
les mêmes cas types aux mêmes poids, la simule une fois
(``grille_large.en_tetes``), et pèse chacune de ses parts des générations
(``GrilleEnTetes.parts``) :

* les départs des générations 1950 et 1955 de la grille, contre les nés en
  1950 et en 1953 de l'EIR (``grille_large.departs``) : la génération 1955,
  que l'enquête ne voit pas, se juge sur les nés en 1953
  (``GENERATIONS_DES_DEPARTS``) ;
* les fonctionnaires civils de l'État et de la CNRACL : leurs retraités de
  2024 et leurs liquidants de chaque année de 2020 à 2025 ; ceux de l'État en
  regard de la table H de l'EACR, qui compte tous ses liquidants civils, le
  champ de la mesure — non des seuls départs pour ancienneté de 2025 du jaune
  (tableau B-3, 42,7 %), que la note de la version leur opposait (relecture
  R-I, point 4.5) ;
* le régime général (le groupe ``regime_general`` de la population, celui de
  ``scripts/controle_eacr.py``) : ses liquidants et ses retraités de 2024, et
  la décote de ses liquidants ;
* les retraités de 2020, sexe par sexe, ceux de 70 à 74 ans, et la part des
  fonctionnaires civils parmi ceux qui ont surcoté ;
* l'âge des liquidants de 2024, contre la table C de l'EACR
  (``controle_eacr.mesure``), et ceux du régime général, âge par âge ;
* la distribution des pensions de 2020, contre l'EIR (``grille_large.confronter``) ;
* la décote des générations nées depuis 1960 (action 138, étape 14, décision
  17 du propriétaire) : celle des liquidants du régime général de chaque année
  de 2020 à 2024, et de son stock de 2024 âge par âge — chaque âge est une
  génération —, contre la table H de la Cnav ; les départs de chaque
  génération comptée de la grille (1955, 1960, 1965), pris à 67 ans, par
  classe de condition, tous régimes et au seul régime général, contre la
  fiche 17 du panorama de la DREES de 2026 (``retraites_generations.csv``,
  jusqu'à la génération 1957) et contre la décote que la population prête à
  chaque génération (``grille_large.decotes_des_generations``).

DEUX FAÇONS DE COMPTER UNE SURCOTE. Au drapeau : la cohorte d'une jumelle qui
surcote (``Variante.surcote``), d'une génération simulée qui atteint son âge
légal depuis que la surcote existe (``CasTypeLarge._attente_du_depart``, la
règle même de son départ) ; c'est ainsi que se comptent les stocks. À la
condition de son départ (``grille_large.condition_au_depart``) : partie après
l'âge légal et après l'âge de son taux plein ; c'est ainsi que se comptent les
liquidants, parmi ceux dont la condition se lit. Une jumelle dont l'attente
ne mène pas au-delà de son taux plein part sans surcote ; une carrière qui
n'est pas jumelle peut partir après son taux plein. Le script donne l'une et
l'autre part des liquidants, et leur croisement ; et, depuis la relecture
R-I-bis (point 3), des stocks aussi : à la condition, un départ d'avant
2004, que la loi ne surcotait pas, l'est sans qu'on la lise. La table H
compte des pensions liquidées avec une surcote : c'est la condition qui s'y
compare.

LE DÉPÔT. La sortie ``--json`` dit le commit et l'arbre où la mesure a tourné,
et si des fichiers suivis y étaient modifiés (``depot``) : de quoi la refaire.

Sur la population, la simulation dure près de deux heures sur quatre cœurs ;
la mémoire des calculs en garde les morceaux (``memoire.py``), et la refaire
sur le même modèle ne coûte que les pesées. ``--grille reference`` mesure la
grille de la page, ses 18 cas types, en quelques minutes : le cas court du
test.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts"))

import controle_eacr as E  # noqa: E402
import grille_large as G  # noqa: E402
from retraite_notionnelle import controle_eacr as M  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402
from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

#: Les affiliations des fonctionnaires civils de chaque caisse du jaune
#: (``grille_large.CAISSES_DU_JAUNE``) : l'État, la CNRACL.
CAISSES = {"etat": tuple(a for a, c in G.CAISSES_DU_JAUNE.items() if c == "fpe_civils"),
           "cnracl": tuple(a for a, c in G.CAISSES_DU_JAUNE.items() if c == "cnracl_total")}
FONCTIONNAIRES_CIVILS = CAISSES["etat"] + CAISSES["cnracl"]

#: Les années dont la mesure compte les liquidants des fonctionnaires civils :
#: celles que la note met en regard des départs de 2025 du jaune.
ANNEES_DES_LIQUIDANTS = tuple(range(2020, 2026))

#: L'année du stock que l'EIR voit (« CondLiquidation », résidents), et la
#: tranche d'âge que la note en suit.
ANNEE_DU_STOCK = 2020
TRANCHE_DU_STOCK = (70, 74)

#: Le groupe de la population que la mesure range au régime général, et la
#: caisse de l'EACR qui le juge.
REGIME_GENERAL = "regime_general"
CNAV = "0015"
ETAT = "0012"

#: Les années dont la mesure compte la décote des liquidants du régime
#: général : celles de la table H de la Cnav (action 138, étape 14, la décote
#: des générations nées depuis 1960).
ANNEES_DE_LA_DECOTE = tuple(range(2020, 2025))

#: Les âges du stock de 2024 que la mesure suit au régime général : chacun est
#: une génération, 2024 moins l'âge, de 1957 (67 ans) à 1964 (60 ans), celle
#: que la DREES lit à 67 ans (panorama de 2026, fiche 17, graphique 4) ; plus
#: jeune, la part de ses retraités déjà partis.
AGES_DU_STOCK = tuple(range(60, 68))

#: Les générations de la grille dont la mesure compte tous les départs pris à
#: :data:`AGE_DES_GENERATIONS`, par classe de condition, et l'âge où elle les
#: compte : celui où la DREES lit les générations nées depuis 1954 (fiche 17,
#: graphique 4), l'âge d'annulation de la décote.
GENERATIONS_COMPTEES = (1955, 1960, 1965)
AGE_DES_GENERATIONS = 67

#: Les sexes d'une part, et leur ensemble.
SEXES_ET_ENSEMBLE = ("ensemble", "F", "H")


def surcotee(v: G.Variante, generation: int) -> bool:
    """Vrai pour une cohorte de ``v``, de la génération simulée ``generation``,
    comptée au drapeau : une jumelle qui surcote, dont la génération atteint
    son âge légal depuis que la surcote existe — la règle de son départ
    (``CasTypeLarge._attente_du_depart``, ``ANNEE_DE_LA_SURCOTE``)."""
    attente = getattr(v.cas, "_attente_du_depart", None)
    return bool(v.surcote) and attente is not None and attente(generation) is not None


def part(lot, garder, compter) -> float | None:
    """Les têtes des cohortes de ``lot`` que ``garder`` retient et que
    ``compter`` compte, sur celles que ``garder`` retient ; ``None`` sans elles."""
    gardees = [c for c in lot if garder(c)]
    total = somme_ordonnee(c.tetes for c in gardees)
    if not total:
        return None
    return somme_ordonnee(c.tetes for c in gardees if compter(c)) / total


def parts_par_sexe(lot, garder, compter, sexe_de) -> dict:
    """:func:`part`, pour les deux sexes ensemble puis chacun (``sexe_de``)."""
    return {sexe: part(lot, lambda c, sexe=sexe: garder(c) and sexe in ("ensemble", sexe_de(c)),
                       compter) for sexe in SEXES_ET_ENSEMBLE}


def annee_de_depart(c, annee: int) -> int:
    """L'année où part la cohorte ``c`` de l'année ``annee`` : son année de
    naissance, ``annee`` moins son âge, plus son âge de liquidation."""
    return annee - c.age + c.age_liquidation


def a_la_condition(lot, annee: int, garder, conditions: dict, compter=None) -> dict:
    """Les cohortes de ``lot`` que ``garder`` retient, comptées à la condition
    de leur départ : la part qui part avec une surcote parmi celles dont la
    condition se lit (ou que ``compter`` compte parmi les surcotées), et celle
    des autres. Un départ d'avant :data:`grille_large.ANNEE_DE_LA_SURCOTE`
    se lit sans condition : la loi ne servait pas de surcote."""
    def avant(c) -> bool:
        return annee_de_depart(c, annee) < G.ANNEE_DE_LA_SURCOTE

    def connue(c) -> bool:
        return avant(c) or (c.code, c.generation) in conditions

    def surcotee_(c) -> bool:
        return not avant(c) and conditions[(c.code, c.generation)][1] == "surcote"

    membres = [c for c in lot if garder(c)]
    connues = [c for c in membres if connue(c)]
    return {"surcote": part(connues, lambda c: True, surcotee_),
            "inconnues": part(membres, lambda c: True, lambda c: not connue(c)),
            **({} if compter is None else {"compter": compter(connues, surcotee_)})}


def parts_des_liquidants(lot, garder, par_code: dict, conditions: dict) -> dict:
    """Les liquidants de l'année que ``garder`` retient : la part qui surcote au
    drapeau (:func:`surcotee`), celle qui part avec une surcote parmi ceux dont
    la condition se lit (``conditions``, clé ``(code, génération)``), et la
    part de ceux dont elle ne se lit pas."""
    membres = [c for c in lot if c.nouvelle and garder(c)]
    connus = [c for c in membres if (c.code, c.generation) in conditions]
    return {
        "drapeau": part(membres, lambda c: True,
                        lambda c: surcotee(par_code[c.code], c.generation)),
        "condition": part(connus, lambda c: True,
                          lambda c: conditions[(c.code, c.generation)][1] == "surcote"),
        "inconnues": part(membres, lambda c: True,
                          lambda c: (c.code, c.generation) not in conditions),
    }


def croisement(lot, garder, par_code: dict, conditions: dict) -> dict:
    """Les liquidants de l'année que ``garder`` retient et dont la condition se
    lit, en part de tous ceux-là : ceux qui surcotent au drapeau, puis les
    autres, chacun selon la classe de sa condition."""
    connus = [c for c in lot if c.nouvelle and garder(c) and (c.code, c.generation) in conditions]
    total = somme_ordonnee(c.tetes for c in connus)
    sortie: dict = {"drapeau": {}, "sans_drapeau": {}}
    if not total:
        return sortie
    for c in connus:
        cote = "drapeau" if surcotee(par_code[c.code], c.generation) else "sans_drapeau"
        classe = conditions[(c.code, c.generation)][1]
        sortie[cote][classe] = sortie[cote].get(classe, 0.0) + c.tetes / total
    return sortie


def parts_de_la_pesee(lots: dict, par_code: dict, conditions: dict, decotes: dict) -> dict:
    """Ce que la mesure compte d'une pesée, ses cohortes de chaque année dans
    ``lots`` (``controle_eacr.Cohorte``) : les retraités de 2024 et les
    liquidants de chaque année de l'État et de la CNRACL, et la moyenne de
    leurs parts à la condition ; les liquidants et les retraités de 2024 du
    régime général, et la décote de ses liquidants (``decotes``, celles de
    ``grille_large.proratisations``, comme ``controle_eacr.population``) ; les
    retraités de 2020, sexe par sexe."""
    def affiliation(c) -> str:
        return par_code[c.code].cas.affiliation

    def drapeau(c) -> bool:
        return surcotee(par_code[c.code], c.generation)

    def sexe_de(c) -> str:
        return par_code[c.code].cas.sexe

    def decotee(c) -> bool:
        return decotes.get((c.code, c.generation), (0, False, 0, False))[3]

    du_flux = lots.get(M.ANNEE_EACR, [])
    sortie: dict = {}
    for nom, affiliations in CAISSES.items():
        def siennes(c, affiliations=affiliations) -> bool:
            return affiliation(c) in affiliations

        liquidants = {str(annee): parts_des_liquidants(lot, siennes, par_code, conditions)
                      for annee, lot in sorted(lots.items()) if annee in ANNEES_DES_LIQUIDANTS}
        valeurs = [p["condition"] for p in liquidants.values() if p["condition"] is not None]
        sortie[nom] = {
            "retraites_2024": part(du_flux, siennes, drapeau),
            "retraites_2024_condition": a_la_condition(du_flux, M.ANNEE_EACR, siennes,
                                                       conditions),
            "liquidants": liquidants,
            "liquidants_moyenne": somme_ordonnee(valeurs) / len(valeurs) if valeurs else None,
        }

    def du_regime_general(c) -> bool:
        return par_code[c.code].groupe == REGIME_GENERAL

    sortie["regime_general"] = {
        "liquidants_2024": parts_des_liquidants(du_flux, du_regime_general, par_code,
                                                conditions),
        "croisement_2024": croisement(du_flux, du_regime_general, par_code, conditions),
        "retraites_2024": part(du_flux, du_regime_general, drapeau),
        "retraites_2024_condition": a_la_condition(du_flux, M.ANNEE_EACR, du_regime_general,
                                                   conditions),
        "decote_liquidants_2024": part(
            du_flux, lambda c: c.nouvelle and du_regime_general(c), decotee),
        "decote_liquidants": {
            str(annee): parts_par_sexe(lot, lambda c: c.nouvelle and du_regime_general(c),
                                       decotee, sexe_de)
            for annee, lot in sorted(lots.items()) if annee in ANNEES_DE_LA_DECOTE},
        "stock_2024_par_age": {
            str(age): parts_par_sexe(du_flux, lambda c, age=age: (c.age == age
                                                                   and du_regime_general(c)),
                                     decotee, sexe_de)
            for age in AGES_DU_STOCK},
        "decote_liquidants_2024_par_age": {
            str(age): parts_par_sexe(du_flux, lambda c, age=age: (c.nouvelle and c.age == age
                                                                   and du_regime_general(c)),
                                     decotee, sexe_de)
            for age in AGES_DU_STOCK},
    }
    stock = lots.get(ANNEE_DU_STOCK, [])
    debut, fin = TRANCHE_DU_STOCK
    sexes = {}
    for sexe in ("F", "H"):
        def du_sexe(c, sexe=sexe) -> bool:
            return sexe_de(c) == sexe

        def de_la_tranche(c, du_sexe=du_sexe) -> bool:
            return du_sexe(c) and debut <= c.age <= fin

        def fonctionnaires(connues, surcotee_) -> float | None:
            return part(connues, surcotee_, lambda c: affiliation(c) in FONCTIONNAIRES_CIVILS)

        condition = a_la_condition(stock, ANNEE_DU_STOCK, du_sexe, conditions, fonctionnaires)
        sexes[sexe] = {
            "surcote": part(stock, du_sexe, drapeau),
            f"{debut}_{fin}": part(stock, de_la_tranche, drapeau),
            "fonctionnaires_parmi_surcotes": part(
                stock, lambda c: du_sexe(c) and drapeau(c),
                lambda c: affiliation(c) in FONCTIONNAIRES_CIVILS),
            "condition": {
                "surcote": condition["surcote"],
                f"{debut}_{fin}": a_la_condition(stock, ANNEE_DU_STOCK, de_la_tranche,
                                                 conditions)["surcote"],
                "fonctionnaires_parmi_surcotes": condition["compter"],
                "inconnues": condition["inconnues"]},
        }
    sortie[f"retraites_{ANNEE_DU_STOCK}"] = sexes
    return sortie


def parts_par_generation(lignes) -> dict:
    """La part de chaque classe de condition parmi les départs de chaque
    génération, tous régimes (« tous ») et groupe par groupe de la population
    (le régime général toujours, vide s'il n'y part personne), les deux sexes
    ensemble puis chacun ; et le poids de chaque groupe dans la génération
    (« poids »). ``lignes`` : ``(génération, sexe, groupe, poids, classe)``."""
    masses: dict = {}
    for generation, sexe, groupe, poids, classe in lignes:
        champs = masses.setdefault(str(generation), {"tous": {}, REGIME_GENERAL: {}})
        for champ in ("tous", groupe):
            for cle in ("ensemble", sexe):
                masse = champs.setdefault(champ, {}).setdefault(cle, {})
                masse[classe] = masse.get(classe, 0.0) + poids
    for generation, champs in masses.items():
        total = somme_ordonnee(champs["tous"]["ensemble"].values())
        poids_des_groupes = {champ: somme_ordonnee(sexes["ensemble"].values()) / total
                             for champ, sexes in champs.items() if champ != "tous" and sexes}
        for sexes in champs.values():
            for cle, masse in sexes.items():
                somme = somme_ordonnee(masse.values())
                sexes[cle] = {classe: valeur / somme for classe, valeur in masse.items()}
        champs["poids"] = poids_des_groupes
    return masses


def lignes_des_generations(tetes: G.GrilleEnTetes, par_code: dict, conditions: dict,
                           generations=GENERATIONS_COMPTEES,
                           age: int = AGE_DES_GENERATIONS) -> list[tuple]:
    """Les départs de chaque génération de la grille déjà pris à ``age`` ans,
    comme ``grille_large.departs`` les compte : chaque cas type du poids que la
    page lui donne l'année de ses ``age`` ans, de sa survie propre à nombre de
    décès égal (``cout._survies_alignees``) et de ce que la génération donne à
    son poids (``GrilleEnTetes.part_de``) ; en lignes de
    :func:`parts_par_generation`."""
    from retraite_notionnelle import cout as C

    lignes = []
    for generation in generations:
        poids = tetes.poids(generation + age)
        alignees = C._survies_alignees(tetes.pensionnes, poids, generation + age)
        for pensionne in tetes.pensionnes:
            lu = conditions.get((pensionne.code, pensionne.generation))
            if pensionne.generation != generation or lu is None or lu[0] >= age + 1.0:
                continue
            masse = (poids.get(pensionne.code, 0.0)
                     * alignees.get((pensionne.code, generation, 0), 1.0)
                     * tetes.part_de(pensionne.code, generation))
            if masse > 0.0:
                variante = par_code[pensionne.code]
                lignes.append((generation, variante.cas.sexe, variante.groupe, masse, lu[1]))
    return lignes


def sources(temoin: dict) -> dict:
    """Ce que l'EACR publie en regard (``tests/temoins/drees_eacr_tables_2026.json``) :
    la part des liquidants et des retraités de la Cnav et des civils de l'État
    partis avec une surcote (table H), celle des liquidants de la Cnav de plus
    de 67 ans (table B)."""
    def de_la_table_h(caisse: str, champ: str, annee: int, condition: str = "surcote"):
        for c in M.conditions_publiees(temoin, annee):
            if (c.caisse, c.champ) == (caisse, champ):
                return getattr(c, condition)
        return None

    par_age = temoin["liquidants_par_age"]["series"][CNAV]
    apres_67 = [effectif for age, effectif in par_age.items()
                if age.startswith(">") or (age.isdigit() and int(age) > 67)]
    flux = temoin["conditions_liquidation"]["series"][CNAV]["flux"]

    def decote_de_l_annee(annee: str) -> dict:
        lignes = {sexe: flux[sexe].get(annee) for sexe in SEXES_ET_ENSEMBLE}
        complete = all(lignes.values()) and (
            lignes["F"]["ensemble"] + lignes["H"]["ensemble"] == lignes["ensemble"]["ensemble"])
        return {sexe: (ligne["decote"] / ligne["ensemble"]
                       if ligne and (sexe == "ensemble" or complete) else None)
                for sexe, ligne in lignes.items()}

    stock = temoin["conditions_par_age"]["series"]["stock"]
    flux_par_age = {sexe: annees[str(M.ANNEE_EACR)] for sexe, annees
                    in temoin["conditions_par_age"]["series"]["flux"].items()}
    return {
        "cnav": {"liquidants_2024": de_la_table_h(CNAV, "flux", M.ANNEE_EACR),
                 "retraites_2024": de_la_table_h(CNAV, "stock", M.ANNEE_EACR),
                 "decote_liquidants_2024": de_la_table_h(CNAV, "flux", M.ANNEE_EACR, "decote"),
                 "decote_liquidants": {str(annee): decote_de_l_annee(str(annee))
                                       for annee in ANNEES_DE_LA_DECOTE},
                 "decote_liquidants_2024_par_age": {
                     str(age): {sexe: (flux_par_age[sexe][str(age)].get("decote", 0.0)
                                       / flux_par_age[sexe][str(age)]["ensemble"])
                                for sexe in SEXES_ET_ENSEMBLE}
                     for age in AGES_DU_STOCK},
                 "stock_2024_par_age": {
                     str(age): {sexe: (stock[sexe][str(M.ANNEE_EACR)][str(age)].get("decote", 0.0)
                                       / stock[sexe][str(M.ANNEE_EACR)][str(age)]["ensemble"])
                                for sexe in SEXES_ET_ENSEMBLE}
                     for age in AGES_DU_STOCK},
                 "liquidants_2024_de_68_ans_et_plus":
                     somme_ordonnee(apres_67) / par_age["Ensemble"],
                 "liquidants_2024_a_67_ans": par_age["67"] / par_age["Ensemble"]},
        "etat": {"retraites_2024": de_la_table_h(ETAT, "stock", M.ANNEE_EACR),
                 "liquidants": {str(annee): de_la_table_h(ETAT, "flux", annee)
                                for annee in ANNEES_DES_LIQUIDANTS}},
    }


#: Le fichier certifié des retraités par génération (panorama de la DREES de
#: 2026, fiche 17, graphiques 4 et 5).
RETRAITES_GENERATIONS = RACINE / "data" / "reference" / "macro" / "retraites_generations.csv"


def sources_des_generations(chemin: Path = RETRAITES_GENERATIONS) -> dict:
    """La part des retraités de chaque génération partis avec une décote ou une
    surcote, par régime, que la DREES publie (``retraites_generations.csv``,
    fiche 17, graphiques 4 et 5) : ``{décote|surcote: {régime: {génération:
    part}}}``, en fraction."""
    import csv

    sortie: dict = {}
    with chemin.open(encoding="utf-8") as fichier:
        lignes = csv.DictReader(ligne for ligne in fichier if not ligne.startswith("#"))
        for ligne in lignes:
            if ligne["champ"] in ("decote", "surcote") and ligne["sexe"] == "ensemble":
                (sortie.setdefault(ligne["champ"], {}).setdefault(ligne["regime"], {})
                 [ligne["generation"]]) = float(ligne["valeur"]) / 100.0
    return sortie


@contextmanager
def constante_posee(nom: str, valeur: bool):
    """La constante ``nom`` de ``grille_large.py`` posée à ``valeur`` le temps du
    bloc, puis rendue."""
    ancienne = getattr(G, nom)
    if not isinstance(ancienne, bool):
        raise ValueError(f"{nom} n'est pas une constante vraie ou fausse de grille_large.py")
    setattr(G, nom, valeur)
    try:
        yield
    finally:
        setattr(G, nom, ancienne)


def construire(grille: str, parametres: Parametres, constante: str,
               allumee: bool) -> list[G.Variante]:
    """La grille ``grille`` — la population, comme ``grille_large.mesurer`` la
    construit, ou celle de la page —, la constante allumée ou éteinte."""
    with constante_posee(constante, allumee):
        if grille == "reference":
            return G.reference()
        racine = parametres.racine_donnees
        _, valeurs = G.centiles(racine)
        return G.grille("population", Simulateur(parametres).effectifs, G.eir(racine),
                        G.multiplicateurs(valeurs))


def les_deux_grilles(grille: str, parametres: Parametres, constante: str) -> dict:
    """La grille ``grille`` la constante allumée (« version ») et éteinte
    (« éteinte ») ; refusées si la constante change les cas types ou leurs
    poids, une même simulation ne pouvant servir les deux pesées."""
    grilles = {"version": construire(grille, parametres, constante, True),
               "eteinte": construire(grille, parametres, constante, False)}
    if ([v.cas for v in grilles["eteinte"]] != [v.cas for v in grilles["version"]]
            or [v.retraites for v in grilles["eteinte"]]
            != [v.retraites for v in grilles["version"]]):
        raise ValueError(f"{constante} change les cas types ou leurs poids : une même "
                         "simulation ne sert pas les deux pesées")
    return grilles


def etat_du_depot() -> dict:
    """Le commit et l'arbre où la mesure tourne, et si des fichiers suivis y
    sont modifiés : de quoi la refaire sur le même dépôt."""
    import subprocess

    def git(*arguments: str) -> str:
        return subprocess.run(["git", *arguments], cwd=RACINE, capture_output=True,
                              text=True, check=True).stdout.strip()

    return {"commit": git("rev-parse", "HEAD"), "arbre": git("rev-parse", "HEAD^{tree}"),
            "modifie": bool(git("status", "--porcelain", "--untracked-files=no"))}


def cohortes_brutes(tetes: G.GrilleEnTetes, annee: int) -> list[M.Cohorte]:
    """Les cohortes de la grille en ``annee`` (``controle_eacr.cohortes``), sans
    les parts des générations, que chaque pesée leur donne."""
    return M.cohortes(tetes.pensionnes, tetes.poids(annee), tetes.population,
                      tetes.revalorisation,
                      tetes.macro.coefficient_prix(tetes.annee_euros, annee), annee)


def pesees(lot: list[M.Cohorte], tetes: G.GrilleEnTetes, annee: int) -> list[M.Cohorte]:
    """Les cohortes, chacune pesée de ce que son année de naissance donne au
    poids de son cas type (``GrilleEnTetes.part_de``), comme
    ``controle_eacr.cohortes_de_la_population``."""
    return [replace(c, tetes=c.tetes * tetes.part_de(c.code, annee - c.age)) for c in lot]


def mesurer(grille: str = "population", constante: str = "SURCOTE_SELON_LA_GENERATION",
            processus: int = 1, parametres: Parametres | None = None) -> dict:
    """La mesure entière : les deux pesées d'une même simulation, et les
    sources en regard."""
    debut = time.time()
    parametres = parametres if parametres is not None else Parametres()
    racine = parametres.racine_donnees
    grilles = les_deux_grilles(grille, parametres, constante)
    version = grilles["version"]
    tetes = G.en_tetes(parametres, version, processus, alleges=True)
    par_code = {v.cas.code: v for v in version}

    def du_regime_general(c: M.Cohorte) -> bool:
        return par_code[c.code].groupe == REGIME_GENERAL

    def gardee(annee: int, c: M.Cohorte) -> bool:
        if annee in (ANNEE_DU_STOCK, M.ANNEE_EACR):
            return True
        return c.nouvelle and (par_code[c.code].cas.affiliation in FONCTIONNAIRES_CIVILS
                               or (annee in ANNEES_DE_LA_DECOTE and du_regime_general(c)))

    annees = sorted({ANNEE_DU_STOCK, M.ANNEE_EACR, *ANNEES_DES_LIQUIDANTS,
                     *ANNEES_DE_LA_DECOTE})
    brutes = {annee: [c for c in cohortes_brutes(tetes, annee) if gardee(annee, c)]
              for annee in annees}
    cas_par_code = {cas.code: cas for cas in tetes.cas_types}
    liquidants = {(cas_par_code[c.code], c.generation)
                  for annee, lot in brutes.items() for c in lot if c.nouvelle
                  and (par_code[c.code].cas.affiliation in FONCTIONNAIRES_CIVILS
                       or (annee == M.ANNEE_EACR and du_regime_general(c)))}
    # Les stocks à la condition (relecture R-I-bis, point 3) : les départs
    # depuis 2004 du stock de 2020, et de ceux de 2024 du régime général et des
    # fonctionnaires civils ; et tous les couples des générations comptées.
    stocks = {(cas_par_code[c.code], c.generation)
              for annee in (ANNEE_DU_STOCK, M.ANNEE_EACR) for c in brutes[annee]
              if annee_de_depart(c, annee) >= G.ANNEE_DE_LA_SURCOTE
              and (annee == ANNEE_DU_STOCK or du_regime_general(c)
                   or par_code[c.code].cas.affiliation in FONCTIONNAIRES_CIVILS)}
    generations = {(cas_par_code[p.code], p.generation) for p in tetes.pensionnes
                   if p.generation in GENERATIONS_COMPTEES}
    couples = liquidants | stocks | generations
    conditions = {(code, generation): (age, condition) for code, generation, age, condition
                  in G._par_morceaux(G._conditions, parametres, couples, processus)}
    decotes = G.proratisations(
        parametres, {(par_code[c.code].cas, c.generation)
                     for annee in ANNEES_DE_LA_DECOTE for c in brutes[annee]
                     if du_regime_general(c)
                     and (c.nouvelle or (annee == M.ANNEE_EACR and c.age in AGES_DU_STOCK))},
        processus)
    temoin = json.loads(E.TEMOIN.read_text(encoding="utf-8"))
    publies = G.departs_publies(racine)
    source = G.eir(racine)
    residence = G.ResidenceRetraites(racine, source.millesime)
    distributions = {sexe: G.DistributionPensions(racine, sexe, source.millesime, "france")
                     for sexe in G.SEXES}
    cible = G.decotes_des_generations(racine)
    resultat: dict = {"grille": grille, "constante": constante, "depot": etat_du_depot(),
                      "cas_types": len(version),
                      "couples": len(tetes.pensionnes), "echecs": dict(tetes.echecs),
                      "conditions": {"couples": len(couples), "lues": len(conditions),
                                     "liquidants": len(liquidants), "stocks": len(stocks),
                                     "generations": len(generations)},
                      "decotes": {"couples": len(decotes)},
                      "cible_decote": {sexe: {str(generation): G._par_generation(
                          paires, generation, None) for generation in GENERATIONS_COMPTEES}
                          for sexe, paires in cible.items()},
                      "sources": {**sources(temoin),
                                  "generations": sources_des_generations()},
                      "pesees": {}}
    for nom, variantes in grilles.items():
        pesee = replace(tetes, parts={v.cas.code: v.parts_des_generations for v in variantes
                                      if v.parts_des_generations})
        lots = {annee: pesees(lot, pesee, annee) for annee, lot in brutes.items()}
        mesure = parts_de_la_pesee(lots, par_code, conditions, decotes)
        eacr = E.mesure(lots[M.ANNEE_EACR], temoin)
        mesure["liquidants_2024"] = {
            "par_age": {cle: valeurs["grille"] for cle, valeurs in eacr["flux"].items()},
            "age_moyen": eacr["age_moyen"]["grille"]}
        du_regime_general = [c for c in lots[M.ANNEE_EACR]
                             if par_code[c.code].groupe == REGIME_GENERAL]
        mesure["regime_general"]["liquidants_2024_par_age"] = M.parts(
            M.grille_par_age(du_regime_general))
        mesure["departs"] = G.departs(parametres, pesee, publies, processus)
        mesure["generations"] = parts_par_generation(
            lignes_des_generations(pesee, par_code, conditions))
        mesure["distribution_2020"] = G.confronter(pesee.pensions(source.millesime), residence,
                                                   distributions)
        resultat["pesees"][nom] = mesure
        if nom == "version":
            resultat["sources"]["eacr_tous_regimes"] = {
                "liquidants_2024_par_age": {cle: valeurs["eacr"]
                                            for cle, valeurs in eacr["flux"].items()},
                "age_moyen": eacr["age_moyen"]["eacr"]}
    resultat["secondes"] = round(time.time() - debut, 1)
    return resultat


# -- l'impression ----------------------------------------------------------------

def _pc(valeur: float | None) -> str:
    return "—" if valeur is None else f"{100 * valeur:.2f}".replace(".", ",")


def _virgule(valeur: float, decimales: int) -> str:
    return f"{valeur:.{decimales}f}".replace(".", ",")


def _ligne(intitule: str, source: float | None, eteinte, version) -> str:
    return f"| {intitule} | {_pc(source)} | {_pc(eteinte)} | {_pc(version)} |"


def imprimer(resultat: dict) -> None:
    eteinte, version = resultat["pesees"]["eteinte"], resultat["pesees"]["version"]
    sources_ = resultat["sources"]
    depot = resultat["depot"]
    print(f"Dépôt : commit {depot['commit']}, arbre {depot['arbre']}"
          f"{', fichiers suivis modifiés' if depot['modifie'] else ''}.")
    print(f"Grille « {resultat['grille']} », {resultat['cas_types']} cas types, "
          f"{resultat['couples']} couples, échecs {resultat['echecs']} ; constante "
          f"{resultat['constante']} ; {resultat['secondes']} s.")
    print()
    print("Les départs, en part des départs déjà pris à l'âge où l'enquête voit sa "
          "génération ; la génération 1955 de la grille jugée sur les nés en 1953 de l'EIR.")
    print()
    print("| | EIR | éteinte | version |")
    print("|---|---|---|---|")
    for generation in ("1955", "1950"):
        for sexe in ("ensemble", "F", "H"):
            if sexe not in version["departs"].get(generation, {}):
                continue
            e, v = eteinte["departs"][generation][sexe], version["departs"][generation][sexe]
            print(_ligne(f"{sexe}, {generation}, surcote", v["conditions"]["surcote"][1],
                         e["conditions"]["surcote"][0], v["conditions"]["surcote"][0]))
        for sexe in ("ensemble", "F"):
            if sexe not in version["departs"].get(generation, {}):
                continue
            e, v = eteinte["departs"][generation][sexe], version["departs"][generation][sexe]
            for place in ("age_legal", "entre"):
                print(_ligne(f"{sexe}, {generation}, {place}", v["positions"][place][1],
                             e["positions"][place][0], v["positions"][place][0]))
    print()
    print("Les fonctionnaires civils, le régime général et les retraités : la source est "
          "l'EACR (tables H, B et C), « — » où le script n'en lit pas.")
    print()
    print("| | source | éteinte | version |")
    print("|---|---|---|---|")
    for nom, intitule in (("etat", "État"), ("cnracl", "CNRACL")):
        e, v = eteinte[nom], version[nom]
        for annee in map(str, ANNEES_DES_LIQUIDANTS):
            publie = sources_["etat"]["liquidants"][annee] if nom == "etat" else None
            print(_ligne(f"{intitule}, liquidants de {annee}, à la condition", publie,
                         e["liquidants"][annee]["condition"],
                         v["liquidants"][annee]["condition"]))
            print(_ligne(f"{intitule}, liquidants de {annee}, au drapeau", None,
                         e["liquidants"][annee]["drapeau"], v["liquidants"][annee]["drapeau"]))
        print(_ligne(f"{intitule}, liquidants, moyenne de 2020 à 2025", None,
                     e["liquidants_moyenne"], v["liquidants_moyenne"]))
        print(_ligne(f"{intitule}, retraités de 2024", sources_["etat"]["retraites_2024"]
                     if nom == "etat" else None, e["retraites_2024"], v["retraites_2024"]))
        print(_ligne(f"{intitule}, retraités de 2024, à la condition",
                     sources_["etat"]["retraites_2024"] if nom == "etat" else None,
                     e["retraites_2024_condition"]["surcote"],
                     v["retraites_2024_condition"]["surcote"]))
        print(_ligne(f"{intitule}, retraités de 2024, conditions inconnues", None,
                     e["retraites_2024_condition"]["inconnues"],
                     v["retraites_2024_condition"]["inconnues"]))
    e, v = eteinte["regime_general"], version["regime_general"]
    for compte in ("condition", "drapeau", "inconnues"):
        print(_ligne(f"régime général, liquidants de 2024, {compte}",
                     sources_["cnav"]["liquidants_2024"] if compte != "inconnues" else None,
                     e["liquidants_2024"][compte], v["liquidants_2024"][compte]))
    print(_ligne("régime général, retraités de 2024", sources_["cnav"]["retraites_2024"],
                 e["retraites_2024"], v["retraites_2024"]))
    print(_ligne("régime général, retraités de 2024, à la condition",
                 sources_["cnav"]["retraites_2024"], e["retraites_2024_condition"]["surcote"],
                 v["retraites_2024_condition"]["surcote"]))
    print(_ligne("régime général, retraités de 2024, conditions inconnues", None,
                 e["retraites_2024_condition"]["inconnues"],
                 v["retraites_2024_condition"]["inconnues"]))
    print(_ligne("régime général, liquidants de 2024, décote",
                 sources_["cnav"]["decote_liquidants_2024"], e["decote_liquidants_2024"],
                 v["decote_liquidants_2024"]))
    print(_ligne("régime général, liquidants de 2024 de 67 ans",
                 sources_["cnav"]["liquidants_2024_a_67_ans"],
                 e["liquidants_2024_par_age"].get("67", 0.0),
                 v["liquidants_2024_par_age"].get("67", 0.0)))
    print(_ligne("régime général, liquidants de 2024 de 68 ans et plus",
                 sources_["cnav"]["liquidants_2024_de_68_ans_et_plus"],
                 e["liquidants_2024_par_age"].get("68_plus", 0.0),
                 v["liquidants_2024_par_age"].get("68_plus", 0.0)))
    for cote in ("drapeau", "sans_drapeau"):
        for classe in sorted(set(e["croisement_2024"][cote]) | set(v["croisement_2024"][cote])):
            print(_ligne(f"régime général, liquidants de 2024, {cote}, {classe}", None,
                         e["croisement_2024"][cote].get(classe),
                         v["croisement_2024"][cote].get(classe)))
    stock = f"retraites_{ANNEE_DU_STOCK}"
    debut, fin = TRANCHE_DU_STOCK
    for sexe in ("F", "H"):
        e, v = eteinte[stock][sexe], version[stock][sexe]
        for cle, intitule in (("surcote", "surcote"),
                              (f"{debut}_{fin}", f"de {debut} à {fin} ans"),
                              ("fonctionnaires_parmi_surcotes",
                               "fonctionnaires civils parmi les surcotés")):
            print(_ligne(f"retraités de {ANNEE_DU_STOCK}, {sexe}, {intitule}", None,
                         e[cle], v[cle]))
        for cle, intitule in (("surcote", "surcote"),
                              (f"{debut}_{fin}", f"de {debut} à {fin} ans"),
                              ("fonctionnaires_parmi_surcotes",
                               "fonctionnaires civils parmi les surcotés"),
                              ("inconnues", "conditions inconnues")):
            print(_ligne(f"retraités de {ANNEE_DU_STOCK}, {sexe}, {intitule}, à la condition",
                         None, e["condition"][cle], v["condition"][cle]))
    publie = sources_["eacr_tous_regimes"]
    e, v = eteinte["liquidants_2024"], version["liquidants_2024"]
    for cle, intitule in (("62", "à 62 ans"), ("67", "à 67 ans"),
                          ("68_plus", "à 68 ans et plus")):
        print(_ligne(f"liquidants de 2024 partis {intitule}",
                     publie["liquidants_2024_par_age"][cle], e["par_age"].get(cle),
                     v["par_age"].get(cle)))
    print(f"| âge moyen des liquidants de 2024 | {_virgule(publie['age_moyen'], 2)} | "
          f"{_virgule(e['age_moyen'], 2)} | {_virgule(v['age_moyen'], 2)} |")
    imprimer_la_decote(resultat)
    for sexe in ("F", "H"):
        e = eteinte["distribution_2020"].get(sexe)
        v = version["distribution_2020"].get(sexe)
        if not (e and v):
            continue
        print(f"| pension moyenne de {ANNEE_DU_STOCK}, {sexe}, € par mois | "
              f"{v['moyenne_eir']:.0f} | {e['moyenne']:.0f} | {v['moyenne']:.0f} |")
        print(f"| écart de Kolmogorov, {sexe}, points, à la borne | — | "
              f"{_virgule(100 * e['kolmogorov'], 1)} à {e['borne_kolmogorov']:.0f} | "
              f"{_virgule(100 * v['kolmogorov'], 1)} à {v['borne_kolmogorov']:.0f} |")


def imprimer_la_decote(resultat: dict) -> None:
    """La décote des générations nées depuis 1960 : les liquidants du régime
    général de chaque année et son stock de 2024 âge par âge, contre la table H
    de la Cnav ; les départs de chaque génération comptée, contre la fiche 17
    de la DREES et la cible de la population."""
    eteinte, version = resultat["pesees"]["eteinte"], resultat["pesees"]["version"]
    cnav = resultat["sources"]["cnav"]
    print()
    print("La décote : le régime général contre la table H de la Cnav (flux de chaque année, "
          "stock de 2024 à chaque âge, la génération 2024 moins l'âge).")
    print()
    print("| | source | éteinte | version |")
    print("|---|---|---|---|")
    e, v = eteinte["regime_general"], version["regime_general"]
    for annee in map(str, ANNEES_DE_LA_DECOTE):
        for sexe in SEXES_ET_ENSEMBLE:
            if annee not in v["decote_liquidants"]:
                continue
            print(_ligne(f"régime général, liquidants de {annee}, décote, {sexe}",
                         cnav["decote_liquidants"][annee][sexe],
                         e["decote_liquidants"][annee][sexe],
                         v["decote_liquidants"][annee][sexe]))
    for age in map(str, AGES_DU_STOCK):
        for sexe in SEXES_ET_ENSEMBLE:
            print(_ligne(f"régime général, liquidants de 2024 de {age} ans, décote, {sexe}",
                         cnav["decote_liquidants_2024_par_age"][age][sexe],
                         e["decote_liquidants_2024_par_age"][age][sexe],
                         v["decote_liquidants_2024_par_age"][age][sexe]))
    for age in map(str, AGES_DU_STOCK):
        for sexe in SEXES_ET_ENSEMBLE:
            print(_ligne(f"régime général, stock de 2024 à {age} ans (née en "
                         f"{M.ANNEE_EACR - int(age)}), décote, {sexe}",
                         cnav["stock_2024_par_age"][age][sexe],
                         e["stock_2024_par_age"][age][sexe],
                         v["stock_2024_par_age"][age][sexe]))
    publiees = resultat["sources"]["generations"]
    print()
    print(f"Les départs de chaque génération de la grille pris à {AGE_DES_GENERATIONS} ans, "
          "par classe ; la source, la fiche 17 de la DREES (graphiques 4 et 5) ; la cible, "
          "la décote que la population prête à la génération (sexe par sexe).")
    print()
    print("| | source | cible | éteinte | version |")
    print("|---|---|---|---|---|")
    for generation in map(str, GENERATIONS_COMPTEES):
        for champ, regime in (("tous", "tous_regimes"), ("regime_general", "regime_general")):
            for sexe in SEXES_ET_ENSEMBLE:
                for classe in ("decote", "surcote"):
                    if sexe not in version["generations"].get(generation, {}).get(champ, {}):
                        continue
                    source = (publiees.get(classe, {}).get(regime, {}).get(generation)
                              if sexe == "ensemble" else None)
                    cible = (resultat["cible_decote"].get(sexe, {}).get(generation)
                             if classe == "decote" and champ == "tous" else None)
                    valeurs = [p["generations"][generation][champ][sexe].get(classe, 0.0)
                               for p in (eteinte, version)]
                    print(f"| {generation}, {champ}, {sexe}, {classe} | {_pc(source)} | "
                          f"{_pc(cible)} | {_pc(valeurs[0])} | {_pc(valeurs[1])} |")
    print()
    print(f"Chaque groupe de la population dans les départs de la génération pris à "
          f"{AGE_DES_GENERATIONS} ans (version) : son poids, sa décote, sa surcote.")
    print()
    print("| génération, groupe | poids | décote | surcote |")
    print("|---|---|---|---|")
    for generation in map(str, GENERATIONS_COMPTEES):
        champs = version["generations"].get(generation, {})
        for groupe, poids in sorted(champs.get("poids", {}).items(), key=lambda g: -g[1]):
            classes = champs[groupe]["ensemble"]
            print(f"| {generation}, {groupe} | {_pc(poids)} | "
                  f"{_pc(classes.get('decote', 0.0))} | {_pc(classes.get('surcote', 0.0))} |")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--grille", choices=("population", "reference"), default="population",
                           help="la population (défaut), ou la grille de la page, cas court")
    analyseur.add_argument("--constante", default="SURCOTE_SELON_LA_GENERATION",
                           help="la constante de grille_large.py qui sépare les deux pesées")
    analyseur.add_argument("--processus", type=int, default=G.processus_par_defaut(),
                           help="cœurs sur lesquels simuler la grille")
    analyseur.add_argument("--json", type=Path, help="écrit la mesure dans ce fichier")
    arguments = analyseur.parse_args(argv)

    resultat = mesurer(arguments.grille, arguments.constante, arguments.processus)
    imprimer(resultat)
    if arguments.json:
        arguments.json.write_text(json.dumps(resultat, ensure_ascii=False, indent=1),
                                  encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
