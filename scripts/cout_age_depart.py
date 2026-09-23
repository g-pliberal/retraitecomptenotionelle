#!/usr/bin/env python3
"""Ce que l'erreur d'âge de la grille coûte à la trajectoire.

    python scripts/cout_age_depart.py            # le contrefactuel, et son écart
    python scripts/cout_age_depart.py --json c.json

LA QUESTION
-----------
`scripts/age_depart_csp.py` a mesuré que les cas types s'écartent de 1,17 an en
valeur absolue de l'âge de départ de leur catégorie socioprofessionnelle, et le
dépôt a écrit qu'il ne corrigeait rien. Une erreur qu'on ne corrige pas doit au
moins être CHIFFRÉE : tant qu'on ne sait pas ce que ces 1,17 an déplacent, on
ne sait pas s'il faut réécrire une fiche ou fermer le sujet.

Ce script fait le contrefactuel. Pour chaque cas type comparable, il cherche
l'âge d'entrée qui rapproche le plus son départ du couloir de sa catégorie,
rebâtit la grille avec ces âges-là, et relance `cout.calculer_cout`. L'écart
entre les deux trajectoires est la réponse.

POURQUOI L'ÂGE D'ENTRÉE, ET PAS L'ÂGE DE DÉPART
-------------------------------------------------
Parce que c'est la cause que `docs/limites.md` § 5 ter désigne : « les âges
d'entrée des cas types restent ceux de la grille — vingt-quatre ans pour
l'artisan, vingt-sept pour le libéral —, ce qui suffit à les faire partir à
soixante-sept ans une fois la durée requise opposée ». Forcer l'âge de départ
directement donnerait une carrière que le droit ne produit pas ; déplacer
l'âge d'entrée déplace la durée validée, donc l'âge du taux plein, donc le
départ — et aussi la pension, ce qui est le second terme du coût et non un
effet de bord.

CE QUE CE CONTREFACTUEL N'EST PAS
----------------------------------
Ce n'est **pas une proposition de réécriture des fiches**. Aucun âge d'entrée
trouvé ici n'entre dans `castypes.py` : ils ne servent qu'à borner ce que
l'erreur coûte. Une fiche se réécrit sur ce qu'on sait d'une carrière, pas sur
ce qui rapproche une moyenne d'une autre.

DEUX RAISONS QUI EN FONT UNE BORNE BASSE
------------------------------------------
1. **Quatre cas types restent hors champ** — militaire, agent de conduite,
   agent des IEG, catégorie active —, pour la raison écrite dans
   `cas_types_csp.yaml` : leur départ n'est pas une sortie du marché du
   travail. Ils pèsent un douzième de la grille et ne sont pas touchés.
2. **Le couloir d'une catégorie unique est un POINT**, qu'un pas d'une
   demi-année n'atteint pas exactement. Le résidu est imprimé pour chaque cas
   type : c'est ce que la correction ne referme pas.

Elles étaient TROIS jusqu'au 21 septembre 2026. La troisième disait que deux
cas types ne se corrigeaient pas par l'âge d'entrée — l'exploitant agricole et
la profession libérale, « auxquels le modèle n'oppose aucune durée requise ».
Le constat était juste et l'explication fausse : c'était un défaut du moteur,
qui ne savait rien opposer à une carrière entière en points, ni durée, ni âge
d'ouverture, ni carrière longue. Il est corrigé, et les neuf cas types
comparables répondent tous à leur âge d'entrée. Voir `docs/limites.md` § 5 ter,
« Une carrière tout en points ne se voyait rien opposer ».
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts"))

from retraite_notionnelle import cout as C  # noqa: E402
from retraite_notionnelle.castypes import CAS_TYPES, CasType  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.equilibre import ComptesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

import age_depart_csp as ACSP  # noqa: E402
from age_conjoncturel import (  # noqa: E402
    age_interpole, departs_de_la_grille, mesurer,
)

#: Générations rejouées pendant la RECHERCHE de l'âge d'entrée. La fenêtre de
#: la source va de 2013 à 2020 ; ces sept générations l'encadrent largement, et
#: en rejouer vingt-huit coûterait quatre fois plus pour le même âge moyen.
GENERATIONS_RECHERCHE: tuple[int, ...] = tuple(range(1940, 1971, 5))

#: Pas et portée de la recherche, en années d'âge d'entrée.
PAS = 0.5
PORTEE = 8.0

#: Bornes d'un âge d'entrée qu'on accepte d'écrire dans un contrefactuel. En
#: deçà la scolarité obligatoire l'interdit, au-delà la carrière ne ressemble
#: plus à celle que la fiche décrit.
ENTREE_MINIMALE, ENTREE_MAXIMALE = 14.0, 32.0

def cor_horizon(racine: Path, horizon: int = C.HORIZON) -> float:
    """Ce que le COR projette pour le système actuel à l'horizon, en part de PIB.

    C'est la valeur que la page Coût oppose à celle du modèle, et le § 5 ter
    de `limites.md` la question ouverte qu'elle pose. Elle est LUE dans le
    compte du système de retraite (`comptes_retraite.csv`, scénario de
    référence du dernier rapport annuel) : la constante qui la tenait,
    14,2 %, était celle du rapport de juin 2025, quand le dépôt porte celui de
    juin 2026, 15,3 %.
    """
    return ComptesRetraite(racine).depense(horizon)

#: Résidu en deçà duquel on considère le couloir atteint. Un couloir réduit à
#: un point ne s'atteint pas au pas d'une demi-année ; un dixième d'année est
#: le grain auquel la source elle-même est publiée.
RESIDU_ATTEINT = 0.1


@dataclass
class Decalage:
    """L'âge d'entrée cherché pour un cas type, et ce qu'il laisse."""

    code: str
    entree_fiche: float
    entree_contrefactuelle: float
    depart_fiche: float
    depart_contrefactuel: float
    borne_basse: float
    borne_haute: float
    #: Ce qui séparait le départ du couloir, et ce qui l'en sépare encore.
    ecart_fiche: float
    residu: float
    #: Vrai quand l'âge de départ ne répond pas du tout à l'âge d'entrée.
    insensible: bool


def _distance(age: float, basse: float, haute: float) -> float:
    if age < basse:
        return age - basse
    if age > haute:
        return age - haute
    return 0.0


def _depart_moyen(simulateur: Simulateur, cas: CasType,
                  annees: tuple[int, ...]) -> float | None:
    """L'âge de départ moyen de ce cas type sur la fenêtre de la source."""
    points = departs_de_la_grille(
        simulateur, (cas,), GENERATIONS_RECHERCHE).get(cas.code, [])
    ages = [age_interpole(points, annee) for annee in annees]
    if any(age is None for age in ages):
        return None
    return sum(ages) / len(ages)


def chercher_decalages(simulateur: Simulateur) -> list[Decalage]:
    """Pour chaque cas type comparable, l'âge d'entrée le plus proche du couloir."""
    annees, par_groupe = ACSP.ages_par_groupe()
    fiches = {cas.code: cas for cas in CAS_TYPES}
    decalages: list[Decalage] = []

    for fiche in ACSP.correspondance()["cas_types"]:
        if "groupes" not in fiche:
            continue
        cas = fiches[fiche["code"]]
        moyennes = [sum(par_groupe[groupe][annee] for annee in annees) / len(annees)
                    for groupe in fiche["groupes"]]
        basse, haute = min(moyennes), max(moyennes)

        depart_fiche = _depart_moyen(simulateur, cas, annees)
        if depart_fiche is None:
            raise RuntimeError(f"{cas.code} : la grille ne couvre pas la fenêtre")

        candidats: list[tuple[float, float, float, float]] = []
        pas = int(PORTEE / PAS)
        for rang in range(-pas, pas + 1):
            entree = cas.age_debut + rang * PAS
            if not ENTREE_MINIMALE <= entree <= ENTREE_MAXIMALE:
                continue
            age = _depart_moyen(simulateur, replace(cas, age_debut=entree), annees)
            if age is None:
                continue
            candidats.append(
                (abs(_distance(age, basse, haute)), abs(entree - cas.age_debut),
                 entree, age))
        if not candidats:
            raise RuntimeError(f"{cas.code} : aucun âge d'entrée jouable")

        # Le plus proche du couloir ; à égalité, celui qui déplace le moins la
        # fiche — un contrefactuel qui bouge peu est un contrefactuel qu'on
        # peut lire.
        _, _, entree, age = min(candidats)
        departs = {candidat[3] for candidat in candidats}
        decalages.append(Decalage(
            code=cas.code,
            entree_fiche=cas.age_debut,
            entree_contrefactuelle=entree,
            depart_fiche=round(depart_fiche, 2),
            depart_contrefactuel=round(age, 2),
            borne_basse=round(basse, 2),
            borne_haute=round(haute, 2),
            ecart_fiche=round(_distance(depart_fiche, basse, haute), 2),
            residu=round(_distance(age, basse, haute), 2),
            insensible=len(departs) == 1,
        ))
    return decalages


def grille_contrefactuelle(decalages: list[Decalage]) -> tuple[CasType, ...]:
    """La grille avec les âges d'entrée du contrefactuel, les autres intacts."""
    nouveaux = {d.code: d.entree_contrefactuelle for d in decalages}
    return tuple(
        replace(cas, age_debut=nouveaux[cas.code]) if cas.code in nouveaux else cas
        for cas in CAS_TYPES
    )


def trajectoire(simulateur: Simulateur, donnees, cas_types: tuple[CasType, ...],
                ) -> dict[str, float]:
    """La part de PIB de chaque système à l'horizon, sous cette grille.

    `part_pib` et non `depense` : c'est le NIVEAU de dépense propre au modèle,
    celui que la page Coût oppose à la projection du COR (`cor_horizon`), et
    donc la grandeur sur laquelle porte la question ouverte du § 5 ter.
    """
    depenses, population, comptes, assiette = donnees
    cout = C.calculer_cout(simulateur, depenses, population, comptes,
                           cas_types=cas_types, assiette=assiette)
    avenir = cout.avenir
    horizon = avenir.annee(avenir.derniere_annee)
    return {scenario: horizon.part_pib(scenario) for scenario, _ in C.SCENARIOS}


def concordance(simulateur: Simulateur,
                cas_types: tuple[CasType, ...]) -> float:
    """L'écart moyen à l'âge conjoncturel TOUS RÉGIMES, sous cette grille.

    La correction cas par cas et la concordance d'ensemble peuvent tirer en
    sens contraire : rapprocher chaque cas type de sa catégorie n'oblige pas
    leur somme à rester où elle était. On le mesure plutôt que d'en décider.
    """
    lignes = mesurer(simulateur, cas_types)
    return sum(ligne.ecart for ligne in lignes) / len(lignes)


def imprimer(decalages: list[Decalage], reference: dict[str, float],
             contrefactuel: dict[str, float], horizon: int,
             concordances: tuple[float, float]) -> None:
    print("Âge d'entrée cherché, et ce qu'il laisse — moyenne 2013-2020\n")
    entete = (f"{'cas type':26} {'entrée':>14} {'départ':>14} "
              f"{'couloir':>15} {'écart':>7} {'résidu':>7}")
    print(entete)
    print("-" * len(entete))
    for d in decalages:
        couloir = (f"{d.borne_basse:.2f}" if d.borne_basse == d.borne_haute
                   else f"{d.borne_basse:.2f}-{d.borne_haute:.2f}")
        marque = "  (insensible)" if d.insensible else ""
        print(f"{d.code:26} {d.entree_fiche:6.2f} →{d.entree_contrefactuelle:6.2f} "
              f"{d.depart_fiche:6.2f} →{d.depart_contrefactuel:6.2f} "
              f"{couloir:>15} {d.ecart_fiche:>+7.2f} {d.residu:>+7.2f}{marque}")

    touches = [d for d in decalages if d.entree_contrefactuelle != d.entree_fiche]
    print(f"\n{len(touches)} cas types déplacés sur {len(decalages)} comparables ; "
          f"{sum(1 for d in decalages if d.insensible)} insensibles à leur âge "
          f"d'entrée.")

    print(f"\nPart du PIB en {horizon}, par système\n")
    entete = f"{'système':34} {'fiches':>9} {'contrefactuel':>15} {'écart':>9}"
    print(entete)
    print("-" * len(entete))
    for scenario, _ in C.SCENARIOS:
        avant, apres = reference[scenario], contrefactuel[scenario]
        print(f"{scenario:34} {avant * 100:>8.2f}% {apres * 100:>14.2f}% "
              f"{(apres - avant) * 100:>+8.2f}")

    cor = cor_horizon(Parametres().racine_donnees, horizon)
    ecart_avant = (reference["actuel"] - cor) * 100
    ecart_apres = (contrefactuel["actuel"] - cor) * 100
    print(f"\nÉcart au COR ({cor * 100:.1f} % en {horizon}) : "
          f"{ecart_avant:+.2f} points sous les fiches, "
          f"{ecart_apres:+.2f} sous le contrefactuel.")
    sens = "ÉLOIGNE" if abs(ecart_apres) > abs(ecart_avant) else "rapproche"
    print(f"Corriger les âges {sens} le modèle du COR.")

    avant, apres = concordances
    print(f"\nÉcart moyen à l'âge conjoncturel tous régimes : "
          f"{avant:+.2f} an sous les fiches, {apres:+.2f} sous le contrefactuel.")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--json", help="écrit le résultat dans ce fichier")
    arguments = analyseur.parse_args(argv)

    parametres = Parametres()
    racine = parametres.racine_donnees
    donnees = (DepensesRetraite(racine), Population(racine),
               ComptesRetraite(racine), AssietteActivite(racine))
    simulateur = Simulateur(parametres)

    decalages = chercher_decalages(simulateur)
    reference = trajectoire(simulateur, donnees, CAS_TYPES)
    corrigee = grille_contrefactuelle(decalages)
    contrefactuel = trajectoire(simulateur, donnees, corrigee)
    concordances = (concordance(simulateur, CAS_TYPES),
                    concordance(simulateur, corrigee))
    imprimer(decalages, reference, contrefactuel, C.HORIZON, concordances)

    if arguments.json:
        Path(arguments.json).write_text(json.dumps({
            "horizon": C.HORIZON,
            "decalages": [asdict(d) for d in decalages],
            "reference": reference,
            "contrefactuel": contrefactuel,
            "cor_horizon": cor_horizon(racine),
            "concordance_fiches": concordances[0],
            "concordance_contrefactuelle": concordances[1],
        }, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
