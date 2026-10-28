#!/usr/bin/env python3
"""Le recours à l'ASPA par type de ménage, sur la population (action 138, étape 14).

    python scripts/recours_aspa.py                  # la population simulée, puis 2016, 2020 et 2024
    python scripts/recours_aspa.py --processus 4
    python scripts/recours_aspa.py --json r.json

LA QUESTION
-----------
Ines (INSEE, DREES, Cnaf) cale le recours à l'ASPA type de ménage par type de
ménage : parmi les ayants droit que l'enquête Revenus fiscaux et sociaux lui
donne, il tire autant d'allocataires que les caisses en servent — personnes
seules, couples à un et à deux allocataires. Le dépôt sert l'ASPA à tout ayant
droit au scénario 1, qui simule une carrière ; la page Coût retient, pour la
garantie et pour l'ASPA de l'effet retour, un recours uniforme de 50 %, que la
DREES mesure sur les seules personnes seules (dossier n° 97, fin 2016). Le
recours qu'impliquent les effectifs servis demande les ayants droit, donc une
population : celle de ``scripts/grille_large.py``.

LA MÉTHODE
----------
Chaque cohorte de la population, l'année voulue, à sa pension de droit direct
du scénario 1, sans ASPA, en euros de l'année — celle que la distribution de
2020 confronte à l'EIR (``grille_large.cohortes_de_l_annee``) —, à 65 ans ou
plus :

- vit en couple dans la part que le recensement de 2021 donne à son âge et à
  son sexe (``vie_en_couple.csv``), la même chaque année ;
- sinon, elle est seule ; veuve dans la part que l'état matrimonial légal de
  l'INSEE donne aux veufs de son âge et de son sexe, rapportée à ceux qui ne
  vivent pas en couple (``etat_matrimonial.csv``, 2020 pour les années qui
  suivent). Une veuve touche une réversion, :data:`TAUX_REVERSION` de la
  pension de son mari, tiré des hommes de la population à l'âge qu'il aurait ;
  les divorcés n'en touchent aucune ;
- en couple, son conjoint est de l'autre sexe, tiré de même, et le couple a
  droit quand ses deux pensions restent sous le plafond du couple ; il a un ou
  deux membres en âge de l'allocation selon l'âge du conjoint.

Le mari a ``Parametres.ecart_age_couple`` ans de plus que sa femme, 2,6 : son
âge tombe entre deux âges de la population, qui se partagent son poids. Le
conjoint est tiré sans lien avec la pension de la personne. Les couples se
comptent du côté du mari. Une personne a droit quand ses ressources restent
sous le plafond de l'année (le barème du dépôt) ; aucune autre ressource ne
compte, ni revenus du patrimoine ni d'activité.

Les allocataires servis : l'enquête de la DREES sur les allocations du minimum
vieillesse, que l'INSEE reprend (``allocataires_minimum_vieillesse.csv``), à
65 ans ou plus, isolés ou en couple. Les couples servis sont les allocataires
en couple moins les couples qui en comptent deux, que l'enquête ne sépare pas :
entre aucun et autant que de femmes servies ; Ines en compte 12 164 sur
120 088 couples en 2024, sur son champ (:data:`PART_DES_COUPLES_A_DEUX`).

Le recours : les servis rapportés aux ayants droit, personnes seules et
couples. Rien de ce que la page lit ne bouge : elle ne lit pas la population
(action 157).
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

#: L'âge de l'allocation, de droit commun ; l'inapte l'a plus tôt, que la
#: population ne distingue pas.
AGE_DE_L_ASPA = 65
#: Ce que la réversion sert de la pension du conjoint mort : 54 % de la base du
#: régime général et des régimes alignés, 60 % des points de l'Agirc-Arrco,
#: 50 % de la fonction publique. Une convention, pour une pension de base et
#: une complémentaire.
TAUX_REVERSION = 0.55
#: Les couples à deux allocataires parmi tous les couples allocataires, chez
#: Ines : 12 164 sur 12 164 + 107 923 en 2024 (Ines 2024.1,
#: ``param_presta_mensuel.xlsx``, onglet Minima, lignes 8 et 9, sous ODbL), sur
#: le champ de l'enquête Revenus fiscaux et sociaux.
PART_DES_COUPLES_A_DEUX = 12_164 / (12_164 + 107_923)
ANNEES = (2016, 2020, 2024)
#: Les tranches d'âge de l'enquête, à 65 ans ou plus.
TRANCHES = (("65-69", 65, 69), ("70-74", 70, 74), ("75-79", 75, 79),
            ("80-84", 80, 84), ("85-89", 85, 89), ("90+", 90, 200))
SEXES = ("F", "H")
MACRO = Path("reference") / "macro"


def tranche_de(age: int) -> str:
    return next(nom for nom, debut, fin in TRANCHES if debut <= age <= fin)


@dataclass(frozen=True)
class Ligne:
    """Une cohorte de la population, une année : son sexe, son âge, sa pension
    mensuelle de droit direct en euros de l'année, ses têtes."""

    sexe: str
    age: int
    pension: float
    tetes: float


class Repartition:
    """Les pensions d'un sexe à un âge, triées, et leurs têtes cumulées : la
    part qui reste sous un montant, et ce qui lui manque pour l'atteindre."""

    def __init__(self, atomes: Iterable[tuple[float, float]]) -> None:
        tries = sorted(atomes)
        self.montants = [montant for montant, _ in tries]
        self._tetes = [0.0]
        self._masses = [0.0]
        for montant, tetes in tries:
            self._tetes.append(self._tetes[-1] + tetes)
            self._masses.append(self._masses[-1] + montant * tetes)
        self.tetes = self._tetes[-1]
        self.moyenne = self._masses[-1] / self.tetes if self.tetes > 0.0 else 0.0

    def sous(self, seuil: float) -> tuple[float, float]:
        """La part des têtes dont la pension reste strictement sous ``seuil``,
        et ce qui leur manque pour l'atteindre, en moyenne sur toutes les
        têtes de la répartition."""
        if self.tetes <= 0.0:
            return 0.0, 0.0
        rang = bisect.bisect_left(self.montants, seuil)
        tetes, masse = self._tetes[rang], self._masses[rang]
        return tetes / self.tetes, (seuil * tetes - masse) / self.tetes


def repartitions_de(lignes: Iterable[Ligne]) -> dict[tuple[str, int], Repartition]:
    atomes: dict[tuple[str, int], list[tuple[float, float]]] = {}
    for ligne in lignes:
        if ligne.tetes > 0.0:
            atomes.setdefault((ligne.sexe, ligne.age), []).append((ligne.pension, ligne.tetes))
    return {cle: Repartition(lot) for cle, lot in atomes.items()}


def conjoints(repartitions: dict[tuple[str, int], Repartition], sexe: str,
              age: float) -> list[tuple[int, float, Repartition]]:
    """Le conjoint de sexe ``sexe`` et d'âge ``age``, qui n'est pas entier :
    les deux âges de la population qui l'encadrent, chacun pesé de sa
    proximité, ``(âge, poids, répartition)`` ; le poids d'un âge absent revient
    à l'autre, et sans aucun des deux, à l'âge présent le plus proche."""
    bas = math.floor(age)
    haut = age - bas
    presents = [(a, p, repartitions[(sexe, a)]) for a, p in ((bas, 1.0 - haut), (bas + 1, haut))
                if p > 0.0 and (sexe, a) in repartitions]
    if not presents:
        ages = [a for s, a in repartitions if s == sexe]
        if not ages:
            return []
        proche = min(ages, key=lambda a: (abs(a - age), a))
        return [(proche, 1.0, repartitions[(sexe, proche)])]
    total = somme_ordonnee(p for _, p, _ in presents)
    return [(a, p / total, r) for a, p, r in presents]


@dataclass
class AyantsDroit:
    """Les ayants droit d'une année, par type de ménage."""

    #: Les personnes seules qui ont droit, par sexe et tranche d'âge.
    seules: dict[tuple[str, str], float] = field(default_factory=dict)
    #: Celles d'entre elles qui sont veuves.
    seules_veuves: dict[tuple[str, str], float] = field(default_factory=dict)
    #: Les personnes en couple, en âge de l'allocation, dont le couple a droit,
    #: par sexe et tranche d'âge, chacune comptée de son côté.
    en_couple: dict[tuple[str, str], float] = field(default_factory=dict)
    #: Les couples qui ont droit, comptés du côté du mari : un seul membre en
    #: âge de l'allocation, puis les deux.
    couples_un: float = 0.0
    couples_deux: float = 0.0
    #: L'ASPA que les ayants droit recevraient tous, en euros par mois :
    #: ``seules`` et ``couples``.
    montants: dict[str, float] = field(default_factory=lambda: {"seules": 0.0, "couples": 0.0})
    #: Les personnes en âge de l'allocation, seules et en couple, par sexe et
    #: tranche, qu'elles aient droit ou non.
    personnes: dict[tuple[str, str, str], float] = field(default_factory=dict)
    #: Les réversions que les veufs touchent, en euros par mois : un contrôle
    #: de la convention, contre la masse des droits dérivés.
    reversions: float = 0.0


def _ajouter(table: dict, cle, valeur: float) -> None:
    table[cle] = table.get(cle, 0.0) + valeur


def ayants_droit(lignes: list[Ligne], plafond_seul: float, plafond_couple: float,
                 en_couple: Callable[[int, str], float], veuves: Callable[[int, str], float],
                 taux_reversion: float = TAUX_REVERSION, ecart: float = 2.6,
                 age_minimal: int = AGE_DE_L_ASPA) -> AyantsDroit:
    """Les ayants droit de ``lignes`` aux plafonds mensuels d'une personne seule
    et d'un couple. ``en_couple(âge, sexe)`` dit la part de qui vit en couple ;
    ``veuves(âge, sexe)``, la part des veufs parmi les autres ; le mari a
    ``ecart`` ans de plus que sa femme."""
    if ecart < 0.0:
        raise ValueError("le mari est le plus âgé : les couples se comptent de son côté")
    repartitions = repartitions_de(lignes)
    droits = AyantsDroit()
    for ligne in lignes:
        if ligne.age < age_minimal or ligne.tetes <= 0.0:
            continue
        cle = (ligne.sexe, tranche_de(ligne.age))
        autre = "H" if ligne.sexe == "F" else "F"
        lot = conjoints(repartitions, autre,
                        ligne.age + (ecart if ligne.sexe == "F" else -ecart))
        part_couple = en_couple(ligne.age, ligne.sexe)
        seules = ligne.tetes * (1.0 - part_couple)
        part_veuves = veuves(ligne.age, ligne.sexe) if lot else 0.0
        _ajouter(droits.personnes, ("seules", *cle), seules)
        _ajouter(droits.personnes, ("en_couple", *cle), ligne.tetes * part_couple)
        manque = plafond_seul - ligne.pension
        if manque > 0.0:
            non_veuves = seules * (1.0 - part_veuves)
            _ajouter(droits.seules, cle, non_veuves)
            droits.montants["seules"] += non_veuves * manque
        for age_conjoint, poids, repartition in lot:
            veufs = seules * part_veuves * poids
            droits.reversions += veufs * taux_reversion * repartition.moyenne
            if manque > 0.0 and veufs > 0.0:
                part, manque_moyen = repartition.sous(manque / taux_reversion)
                _ajouter(droits.seules, cle, veufs * part)
                _ajouter(droits.seules_veuves, cle, veufs * part)
                droits.montants["seules"] += veufs * taux_reversion * manque_moyen
            couples = ligne.tetes * part_couple * poids
            if couples <= 0.0:
                continue
            reste = plafond_couple - ligne.pension
            part, manque_moyen = repartition.sous(reste)
            _ajouter(droits.en_couple, cle, couples * part)
            if ligne.sexe != "H":
                continue
            if age_conjoint >= age_minimal:
                droits.couples_deux += couples * part
                droits.montants["couples"] += couples * manque_moyen
            else:
                # Un seul allocataire : ce qui manque au couple, au plus le
                # montant d'une personne seule (D. 815-1, a).
                droits.couples_un += couples * part
                droits.montants["couples"] += couples * (
                    manque_moyen - repartition.sous(reste - plafond_seul)[1])
    return droits


def ayants_droit_comme_la_page(lignes: list[Ligne], plafond_seul: float, plafond_couple: float,
                               en_couple: Callable[[int, str], float],
                               age_minimal: int = AGE_DE_L_ASPA) -> float:
    """Les ayants droit comme la page Coût les compte
    (``effet_retour.EffetRetour._aspa``, que la garantie mêle de même) : la
    seule pension de droit direct, chacun à part, sans réversion ; qui vit
    seul sous le plafond d'une personne seule, qui vit en couple sous la
    moitié de celui du couple."""
    return somme_ordonnee(
        ligne.tetes * ((1.0 - part) * (ligne.pension < plafond_seul)
                       + part * (ligne.pension < plafond_couple / 2.0))
        for ligne in lignes if ligne.age >= age_minimal
        for part in (en_couple(ligne.age, ligne.sexe),))


def couples_servis(hommes: float, femmes: float, part_a_deux: float) -> float:
    """Les couples que comptent ``hommes`` et ``femmes`` allocataires en couple,
    quand ``part_a_deux`` d'entre eux en ont deux : chaque couple compte un
    allocataire, et ceux-là un second."""
    return (hommes + femmes) / (1.0 + part_a_deux)


def recours(servis: float, ayants: float) -> float:
    return servis / ayants if ayants > 0.0 else math.nan


def _lire(racine: Path, nom: str) -> list[dict[str, str]]:
    with (racine / MACRO / nom).open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def servis(racine: Path, annee: int) -> dict[tuple[str, str, str], float]:
    """Les allocataires du 31 décembre ``annee``, ``(isoles | couple | ensemble,
    sexe, tranche)``, en personnes."""
    return {(l["menage"], l["sexe"], l["tranche"]): float(l["milliers"]) * 1000.0
            for l in _lire(racine, "allocataires_minimum_vieillesse.csv")
            if int(l["annee"]) == annee}


def veuves_parmi_les_seules(racine: Path, annee: int) -> Callable[[int, str], float]:
    """La part des veufs parmi ceux qui ne vivent pas en couple, à chaque âge et
    pour chaque sexe : les veufs de l'état matrimonial légal de l'année — la
    dernière publiée, après elle —, rapportés à la population de leur âge,
    puis à la part qui ne vit pas en couple (recensement de 2021) ; une au
    plus. Avant 60 ans, celle de 60 ; à 90 ans ou plus, celle de tous."""
    from retraite_notionnelle.donnees.vie_en_couple import VieEnCouple

    lignes = _lire(racine, "etat_matrimonial.csv")
    publiees = sorted({int(l["annee"]) for l in lignes})
    lue = max((a for a in publiees if a <= annee), default=publiees[0])
    veufs: dict[tuple[str, str], float] = {}
    tous: dict[tuple[str, str], float] = {}
    for l in lignes:
        if int(l["annee"]) != lue:
            continue
        cle = (l["age"], l["sexe"])
        _ajouter(tous, cle, float(l["effectif"]))
        if l["etat"] == "veuf":
            _ajouter(veufs, cle, float(l["effectif"]))
    couple = VieEnCouple(racine)

    def part(age: int, sexe: str) -> float:
        rang = "90_plus" if age >= 90 else str(max(age, 60))
        seuls = 1.0 - couple.part(age, sexe)
        if seuls <= 0.0:
            return 0.0
        return min(1.0, veufs.get((rang, sexe), 0.0) / tous[(rang, sexe)] / seuls)

    return part


def lignes_de_la_population(tetes, annee: int) -> list[Ligne]:
    """Les cohortes de la population en ``annee`` (``GrilleEnTetes``), chacune
    à son âge : ``grille_large.cohortes_de_l_annee``, dont chaque cohorte dit
    aussi l'année où elle est née."""
    import grille_large as G
    from retraite_notionnelle import cout as C

    sexes = {cas.code: cas.sexe for cas in tetes.cas_types}
    poids = tetes.poids(annee)
    vers_l_annee = tetes.macro.coefficient_prix(tetes.annee_euros, annee) / 12.0
    alignees = C._survies_alignees(tetes.pensionnes, poids, annee)
    sortie = []
    for pensionne in tetes.pensionnes:
        part = poids.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        siennes = tetes.parts.get(pensionne.code, ())
        for decalage in range(-C._DEMI_TRANCHE, C._DEMI_TRANCHE + 1):
            liquidation = pensionne.liquidation(decalage)
            if annee < liquidation:
                continue
            age = annee - pensionne.generation - decalage
            effectif = (tetes.population.effectif(age, annee)
                        * alignees.get((pensionne.code, pensionne.generation, decalage), 1.0)
                        * G._par_generation(siennes, pensionne.generation + decalage, 1.0))
            if effectif <= 0.0:
                continue
            montant = pensionne.pensions["actuel"] * vers_l_annee * C.coefficient_servi(
                pensionne.parts_regimes, tetes.revalorisation, liquidation, annee)
            sortie.append(Ligne(sexes[pensionne.code], age, montant, part * effectif))
    return sortie


def mesurer_annee(lignes: list[Ligne], racine: Path, annee: int, bareme: tuple[float, float],
                  ecart: float) -> dict:
    """Les ayants droit de l'année, les servis et le recours de chaque type de
    ménage ; ``bareme``, les plafonds mensuels d'une personne seule et d'un
    couple."""
    from retraite_notionnelle.donnees.vie_en_couple import VieEnCouple

    couple = VieEnCouple(racine)
    droits = ayants_droit(lignes, bareme[0], bareme[1], couple.part,
                          veuves_parmi_les_seules(racine, annee), ecart=ecart)
    publies = servis(racine, annee)
    tranches = [nom for nom, _, _ in TRANCHES]
    seules_servies = somme_ordonnee(publies[("isoles", s, t)] for s in SEXES for t in tranches)
    hommes = somme_ordonnee(publies[("couple", "H", t)] for t in tranches)
    femmes = somme_ordonnee(publies[("couple", "F", t)] for t in tranches)
    seules = somme_ordonnee(droits.seules.values())
    couples = droits.couples_un + droits.couples_deux
    comme_la_page = ayants_droit_comme_la_page(lignes, bareme[0], bareme[1], couple.part)
    servis_couples = {"sans_couple_a_deux": couples_servis(hommes, femmes, 0.0),
                      "ines": couples_servis(hommes, femmes, PART_DES_COUPLES_A_DEUX),
                      "tous_a_deux": couples_servis(hommes, femmes, min(hommes, femmes)
                                                    / max(hommes, femmes))}
    return {
        "bareme": {"seul": bareme[0], "couple": bareme[1]},
        "seules": {
            "servies": seules_servies, "ayants_droit": seules,
            "dont_veuves": somme_ordonnee(droits.seules_veuves.values()),
            "recours": recours(seules_servies, seules),
            "par_sexe": {s: {"servies": somme_ordonnee(publies[("isoles", s, t)]
                                                     for t in tranches),
                             "ayants_droit": somme_ordonnee(droits.seules.get((s, t), 0.0)
                                                            for t in tranches)}
                         for s in SEXES},
            "par_tranche": {f"{s} {t}": {"servies": publies[("isoles", s, t)],
                                         "ayants_droit": droits.seules.get((s, t), 0.0),
                                         "personnes": droits.personnes.get(("seules", s, t), 0.0)}
                            for s in SEXES for t in tranches},
        },
        "couples": {
            "servis": servis_couples, "allocataires": {"H": hommes, "F": femmes},
            "ayants_droit": couples, "un": droits.couples_un, "deux": droits.couples_deux,
            "recours": {cle: recours(valeur, couples) for cle, valeur in servis_couples.items()},
            "personnes_ayants_droit": {s: somme_ordonnee(droits.en_couple.get((s, t), 0.0)
                                                         for t in tranches) for s in SEXES},
        },
        # La convention de la page compte des personnes : les servis aussi,
        # seuls et en couple.
        "comme_la_page": {"servis": seules_servies + hommes + femmes,
                          "ayants_droit": comme_la_page,
                          "recours": recours(seules_servies + hommes + femmes, comme_la_page)},
        "montants": droits.montants,
        "personnes": {cle: somme_ordonnee(v for (m, s, _), v in droits.personnes.items()
                                          if (m, s) == cle_)
                      for cle, cle_ in ((f"{m} {s}", (m, s)) for m in ("seules", "en_couple")
                                        for s in SEXES)},
        "reversions_annuelles": droits.reversions * 12.0,
    }


def mesurer(processus: int, annees: tuple[int, ...] = ANNEES) -> dict:
    """La population de ``grille_large.py``, simulée une fois, puis chaque
    année."""
    import grille_large as G
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.simulateur import Simulateur

    parametres = Parametres()
    racine = parametres.racine_donnees
    _, valeurs = G.centiles(racine)
    simulateur = Simulateur(parametres)
    variantes = G.grille("population", simulateur.effectifs, G.eir(racine),
                         G.multiplicateurs(valeurs))
    tetes = G.en_tetes(parametres, variantes, processus, alleges=True)
    minimum = simulateur.scenario_actuel.minimum_vieillesse
    resultat = {"echecs": somme_ordonnee(tetes.echecs.values()), "annees": {}}
    for annee in annees:
        bareme = (minimum.plafond(annee)[0] / 12.0, minimum.plafond_couple(annee)[0] / 12.0)
        resultat["annees"][str(annee)] = mesurer_annee(
            lignes_de_la_population(tetes, annee), racine, annee, bareme,
            parametres.ecart_age_couple)
    return resultat


def _milliers(valeur: float) -> str:
    return f"{valeur / 1000.0:,.1f}".replace(",", " ").replace(".", ",")


def _millions(valeur: float) -> str:
    return f"{valeur / 1e6:,.0f}".replace(",", " ")


def _pc(valeur: float) -> str:
    return "—" if math.isnan(valeur) else f"{100.0 * valeur:.1f}".replace(".", ",")


def imprimer(resultat: dict) -> None:
    print("Le recours à l'ASPA par type de ménage, sur la population (milliers, "
          "65 ans ou plus ; recours en %)")
    print()
    print("| Année | seules servies | seules ayants droit | dont veuves | recours "
          "| couples servis | couples ayants droit | dont à deux | recours |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for annee, r in resultat["annees"].items():
        s, c = r["seules"], r["couples"]
        print(f"| {annee} | {_milliers(s['servies'])} | {_milliers(s['ayants_droit'])} "
              f"| {_milliers(s['dont_veuves'])} | {_pc(s['recours'])} "
              f"| {_milliers(c['servis']['ines'])} ({_milliers(c['servis']['tous_a_deux'])} "
              f"à {_milliers(c['servis']['sans_couple_a_deux'])}) "
              f"| {_milliers(c['ayants_droit'])} | {_milliers(c['deux'])} "
              f"| {_pc(c['recours']['ines'])} ({_pc(c['recours']['tous_a_deux'])} "
              f"à {_pc(c['recours']['sans_couple_a_deux'])}) |")
    for annee, r in resultat["annees"].items():
        print()
        print(f"{annee} — personnes seules par tranche : servies / ayants droit / "
              "personnes seules de la population (milliers)")
        for cle, v in r["seules"]["par_tranche"].items():
            print(f"  {cle} : {_milliers(v['servies'])} / {_milliers(v['ayants_droit'])} / "
                  f"{_milliers(v['personnes'])}")
        page = r["comme_la_page"]
        print(f"  Comme la page les compte : {_milliers(page['servis'])} servis pour "
              f"{_milliers(page['ayants_droit'])} ayants droit, un recours de "
              f"{_pc(page['recours'])} %")
        print(f"  ASPA de tous les ayants droit, millions d'euros par an : seules "
              f"{_millions(r['montants']['seules'] * 12)}, couples "
              f"{_millions(r['montants']['couples'] * 12)} ; réversions des veufs "
              f"{_millions(r['reversions_annuelles'])}")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--processus", type=int, default=1)
    analyseur.add_argument("--json", type=Path, default=None)
    options = analyseur.parse_args(argv)
    resultat = mesurer(options.processus)
    imprimer(resultat)
    if options.json is not None:
        options.json.write_text(json.dumps(resultat, ensure_ascii=False, indent=1),
                                encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
