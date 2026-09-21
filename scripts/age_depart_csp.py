#!/usr/bin/env python3
"""Lequel des treize cas types part de travers, et de combien.

    python scripts/age_depart_csp.py            # le tableau, cas type par cas type
    python scripts/age_depart_csp.py --json c.json

LA QUESTION
-----------
`scripts/age_conjoncturel.py` a montré que la grille de cas types suivait
l'âge conjoncturel TOUS RÉGIMES à moins d'une demi-année sur dix-neuf ans.
Cette concordance-là ne juge que la SOMME. Treize cas types dont l'un partirait
deux ans trop tard et l'autre deux ans trop tôt la donneraient tout aussi
bien — et c'est la réserve que `docs/limites.md` § 5 ter écrivait sans pouvoir
la lever.

La DREES publie le même indicateur ventilé par catégorie socioprofessionnelle
(`data/reference/macro/age_depart_csp.csv`, 2013-2020), et la plupart des cas
types ont une catégorie. C'est la confrontation au grain en dessous.

LE COULOIR, ET POURQUOI CE N'EST PAS UN POINT
----------------------------------------------
La nomenclature classe des PROFESSIONS ; la grille décrit des carrières par
leur régime, leur niveau de revenu et leur âge d'entrée. « Salarié au salaire
moyen » ne dit pas si l'intéressé est technicien, employé ou ouvrier. Chaque
cas type déclare donc, dans `data/reference/macro/cas_types_csp.yaml`, TOUS
les groupes où il peut tomber, et on le confronte au couloir qu'ils forment :
l'écart est nul s'il y tombe, et vaut la distance à la borne la plus proche
sinon.

Déclarer large affaiblit le constat et ne le fausse jamais. Un écart trouvé
malgré un couloir de quatre groupes est un écart que la correspondance ne peut
pas expliquer.

POURQUOI LA MOYENNE 2013-2020, ET PAS L'ANNÉE
-----------------------------------------------
Parce que la source est un SONDAGE — l'enquête Emploi de l'INSEE — et que la
DREES avertit que ses indicateurs par catégorie sont bruités et se lisent en
moyenne sur plusieurs années. La série tous régimes, elle, est un dénombrement
et se compare année par année ; c'est `age_conjoncturel.py` qui le fait.

QUATRE CAS TYPES SONT HORS CHAMP, ET LE FICHIER DIT POURQUOI
--------------------------------------------------------------
Le militaire, l'agent de conduite, l'agent des IEG et le fonctionnaire de
catégorie active. Leur départ n'est pas une sortie du marché du travail :
l'enquête compte retraité qui se déclare tel, et une radiation à quarante-quatre
ou cinquante-deux ans est le plus souvent suivie d'un second emploi. Le motif
de chacun est écrit dans `cas_types_csp.yaml`, et ce script le rappelle.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts"))

from retraite_notionnelle.castypes import CAS_TYPES, poids_effectifs  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

from age_conjoncturel import age_interpole, departs_de_la_grille  # noqa: E402

SERIE = RACINE / "data" / "reference" / "macro" / "age_depart_csp.csv"
CORRESPONDANCE = RACINE / "data" / "reference" / "macro" / "cas_types_csp.yaml"


@dataclass
class Confrontation:
    """Un cas type, son couloir de catégories, et ce qui les sépare."""

    code: str
    libelle: str
    #: Âge moyen de départ du cas type sur la fenêtre de la source.
    grille: float
    #: Groupes déclarés, et les bornes de l'âge qu'ils donnent.
    groupes: tuple[str, ...]
    borne_basse: float
    borne_haute: float
    #: Distance à la borne la plus proche, nulle si le cas type est dans le
    #: couloir. Négative s'il part plus tôt que le couloir, positive sinon.
    ecart: float
    #: Poids du cas type parmi les COMPARABLES, renormalisé : les quatre cas
    #: types hors champ pèsent environ un douzième de la grille, et les laisser
    #: au dénominateur ferait un total qui ne vaut pas un.
    poids: float


def correspondance() -> dict:
    return yaml.safe_load(CORRESPONDANCE.read_text(encoding="utf-8"))


def ages_par_groupe() -> tuple[tuple[int, ...], dict[str, dict[int, float]]]:
    """Les années publiées, et l'âge de chaque groupe année par année."""
    par_groupe: dict[str, dict[int, float]] = {}
    with SERIE.open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        for ligne in csv.DictReader(lignes):
            par_groupe.setdefault(ligne["csp"], {})[int(ligne["annee"])] = \
                float(ligne["age"])
    annees = tuple(sorted({annee for serie in par_groupe.values() for annee in serie}))
    return annees, par_groupe


def _moyenne(valeurs: list[float]) -> float:
    return sum(valeurs) / len(valeurs)


def confronter(simulateur: Simulateur) -> tuple[list[Confrontation], dict[str, str]]:
    """Le tableau des cas types comparables, et les motifs des autres."""
    table = correspondance()
    annees, par_groupe = ages_par_groupe()
    departs = departs_de_la_grille(simulateur)
    libelles = {cas.code: cas.libelle for cas in CAS_TYPES}

    declares = {fiche["code"] for fiche in table["cas_types"]}
    manquants = set(libelles) - declares
    if manquants:
        raise RuntimeError(
            "cas types sans ligne dans cas_types_csp.yaml : "
            f"{', '.join(sorted(manquants))}")

    confrontations: list[Confrontation] = []
    hors_champ: dict[str, str] = {}
    for fiche in table["cas_types"]:
        code = fiche["code"]
        if "hors_champ" in fiche:
            hors_champ[code] = fiche["hors_champ"]
            continue
        groupes = tuple(fiche["groupes"])
        inconnus = [groupe for groupe in groupes if groupe not in par_groupe]
        if inconnus:
            raise RuntimeError(
                f"{code} : groupes absents de la série — {', '.join(inconnus)}")

        ages = [age_interpole(departs[code], annee) for annee in annees]
        connus = [age for age in ages if age is not None]
        if len(connus) < len(annees):
            raise RuntimeError(
                f"{code} : la grille ne couvre pas {annees[0]}-{annees[-1]}")
        grille = _moyenne(connus)

        moyennes = [_moyenne([par_groupe[groupe][annee] for annee in annees])
                    for groupe in groupes]
        basse, haute = min(moyennes), max(moyennes)
        if grille < basse:
            ecart = grille - basse
        elif grille > haute:
            ecart = grille - haute
        else:
            ecart = 0.0

        confrontations.append(Confrontation(
            code=code,
            libelle=libelles[code],
            grille=round(grille, 2),
            groupes=groupes,
            borne_basse=round(basse, 2),
            borne_haute=round(haute, 2),
            ecart=round(ecart, 2),
            poids=0.0,
        ))

    # Le poids de chaque cas type, moyenné sur la fenêtre et renormalisé sur
    # les seuls comparables. C'est la pondération de la page « Coût », et c'est
    # elle qui dit si les écarts se compensent ou s'additionnent.
    bruts = {ligne.code: _moyenne([poids_effectifs(simulateur.effectifs, annee)
                                   .get(ligne.code, 0.0) for annee in annees])
             for ligne in confrontations}
    total = sum(bruts.values())
    for ligne in confrontations:
        ligne.poids = round(bruts[ligne.code] / total, 4) if total > 0 else 0.0

    confrontations.sort(key=lambda ligne: -abs(ligne.ecart))
    return confrontations, hors_champ


def imprimer(confrontations: list[Confrontation], hors_champ: dict[str, str],
             annees: tuple[int, ...]) -> None:
    print(f"Âge moyen de départ, {annees[0]}-{annees[-1]}, "
          f"par ordre d'écart décroissant.\n")
    print(f"{'cas type':30} {'grille':>7}  {'couloir CSP':>15}  {'écart':>7}  groupes")
    for ligne in confrontations:
        couloir = (f"{ligne.borne_basse:.2f}"
                   if ligne.borne_basse == ligne.borne_haute
                   else f"{ligne.borne_basse:.2f}-{ligne.borne_haute:.2f}")
        print(f"{ligne.code:30} {ligne.grille:>7.2f}  {couloir:>15}  "
              f"{ligne.ecart:>+7.2f}  {', '.join(ligne.groupes)}")

    dedans = [ligne for ligne in confrontations if ligne.ecart == 0]
    dehors = [ligne for ligne in confrontations if ligne.ecart != 0]
    print(f"\n{len(dedans)} cas type{'s' if len(dedans) > 1 else ''} dans son "
          f"couloir, {len(dehors)} dehors.")
    if dehors:
        pire = dehors[0]
        print(f"Le plus loin : {pire.code}, {pire.ecart:+.2f} an.")

    # Ce que la concordance d'ensemble cachait : les écarts se COMPENSENT.
    signe = sum(ligne.poids * ligne.ecart for ligne in confrontations)
    absolu = sum(ligne.poids * abs(ligne.ecart) for ligne in confrontations)
    print(f"Pesés comme sur la page « Coût » : écart moyen {signe:+.2f} an, "
          f"écart moyen EN VALEUR ABSOLUE {absolu:.2f} an.")
    print("Le second est ce que le tous régimes ne voyait pas.")
    print("\nHors champ, et pourquoi — voir cas_types_csp.yaml :")
    for code, motif in hors_champ.items():
        premiere = " ".join(motif.split())
        print(f"  {code:26} {premiere[:96]}…")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--json", help="écrit le tableau dans ce fichier")
    arguments = analyseur.parse_args(argv)

    annees, _ = ages_par_groupe()
    confrontations, hors_champ = confronter(Simulateur(Parametres()))
    imprimer(confrontations, hors_champ, annees)
    if arguments.json:
        Path(arguments.json).write_text(
            json.dumps({
                "annees": list(annees),
                "confrontations": [asdict(ligne) for ligne in confrontations],
                "hors_champ": hors_champ,
            }, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
