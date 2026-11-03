#!/usr/bin/env python3
"""Les séries que le dépôt tire des classeurs du panorama de la DREES, édition 2026.

    python scripts/fetch/source_locale.py --recuperer   # l'archive, dans data/brut/
    python scripts/fetch/drees_panorama_classeurs.py    # ses séries, dans data/brut/

Le panorama « Les retraités et les retraites » (action 178) a un classeur par
fiche ; la release ``documents-apportes`` les sert réunis, en une archive que
le manifeste déclare (jeu ``drees_panorama_retraites_2026_classeurs``) et dont
le champ ``contenu`` donne l'empreinte de chaque membre. Ce script vérifie les
classeurs qu'il ouvre à cette empreinte, lit les feuilles dont le dépôt tire
une série et dépose ce qu'il lit dans ``data/brut/drees_panorama_2026.json``,
que ``scripts/verifier_donnees.py`` confronte aux fichiers de référence :

* ``age_conjoncturel`` — fiche 15, graphique 1 : l'âge conjoncturel moyen de
  départ à la retraite, par sexe, de 2004 à 2024 ; le jeu du portail de
  données, que ``age_conjoncturel_depart.csv`` certifie, s'arrête à 2022 ;
* ``cumul`` — fiche 22, tableau 1 : les retraités qui cumulent une activité
  et leur retraite, de 2014 à 2024, l'enquête Emploi de l'INSEE ;
* ``retraite_progressive`` — fiche 22, tableau 2 : ses bénéficiaires par
  régime en 2015, 2023 et 2024, l'EACR ;
* ``invalidite`` — fiche 25, graphique 1 et tableaux 1 à 4 : les
  bénéficiaires d'une pension d'invalidité de droit direct depuis 2015, et,
  fin 2024, par régime, leur âge, leurs nouveaux, leur pension, leur dépense.

Une feuille se lit par ses libellés : la colonne d'une grandeur est celle dont
l'en-tête la nomme, la ligne d'un régime celle qui porte son nom, et un
libellé qui manque arrête la lecture au lieu de prendre la case voisine. Une
case qui n'est pas un nombre — « nd », « - », « <1 » — n'est pas une valeur.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import lecture_xlsx  # noqa: E402

JEU = "drees_panorama_retraites_2026_classeurs"
SORTIE = RACINE / "data" / "brut" / "drees_panorama_2026.json"

#: Le nom d'un régime dans les tableaux, et sa clé dans le dépôt ; un nom se
#: reconnaît à son début, le renvoi en note (« FPE civils1 ») ôté.
REGIMES = (
    ("Régimes dans le champ", "ensemble"),
    ("Ensemble", "ensemble"),
    ("Régime général", "regime_general"),
    ("MSA salariés", "msa_salaries"),
    ("MSA non-salariés", "msa_exploitants"),
    ("CNIEG", "cnieg"),
    ("FPE civils", "fonction_publique_etat_civile"),
    ("FPE militaires", "fonction_publique_etat_militaire"),
    ("CNRACL", "cnracl"),
)

SEXES = {"Femmes": "F", "Hommes": "H", "Ensemble": "ensemble"}


class FeuilleIllisible(ValueError):
    """Un libellé attendu manque : la feuille a changé de forme."""


def nombre(valeur) -> float | None:
    """Un nombre, ou ``None`` : « 54,5 », écrit en texte, est 54,5 ; « nd »,
    « - » ou « <1 » ne sont pas des valeurs."""
    if isinstance(valeur, (int, float)):
        return float(valeur)
    texte = str(valeur).strip().replace("\xa0", "").replace(" ", "")
    if re.fullmatch(r"-?\d+(,\d+)?", texte):
        return float(texte.replace(",", "."))
    return None


def annee(valeur) -> int | None:
    """Une année d'en-tête : 2004.0, « 2018 3 » ou « 20141 » (renvoi en note,
    collé ou non), « 2024(p) »."""
    if isinstance(valeur, (int, float)):
        return int(valeur) if 1900 < valeur < 2100 and valeur == int(valeur) else None
    trouve = re.match(r"\s*((?:19|20)\d\d)(?:\d?\b)", str(valeur))
    return int(trouve.group(1)) if trouve else None


def _texte(valeur) -> str:
    return " ".join(str(valeur).replace("\xa0", " ").split())


def _colonne(grille: dict, debut: str, *, exact: bool = False) -> int:
    """La colonne dont l'en-tête commence par ``debut`` — ou n'est que lui,
    ``exact`` : « Total » n'est pas « Total des pensions de droit direct »."""
    for (_, colonne), valeur in sorted(grille.items()):
        if isinstance(valeur, str):
            texte = _texte(valeur)
            if texte == debut or (not exact and texte.startswith(debut)):
                return colonne
    raise FeuilleIllisible(f"aucun en-tête « {debut} »")


def _regime(libelle) -> str | None:
    if not isinstance(libelle, str):
        return None
    texte = _texte(libelle)
    for debut, cle in REGIMES:
        if texte.startswith(debut):
            return cle
    return None


def _lignes_des_regimes(grille: dict, colonne: int) -> dict[str, int]:
    trouvees: dict[str, int] = {}
    for (ligne, col), valeur in sorted(grille.items()):
        cle = _regime(valeur) if col == colonne else None
        if cle and cle not in trouvees:
            trouvees[cle] = ligne
    if "ensemble" not in trouvees:
        raise FeuilleIllisible("aucune ligne d'ensemble")
    return trouvees


def _verifier_titre(grille: dict, debut: str) -> None:
    if not any(isinstance(v, str) and _texte(v).startswith(debut) for v in grille.values()):
        raise FeuilleIllisible(f"aucun titre « {debut} »")


def lire_age_conjoncturel(grille: dict) -> dict[str, dict[str, float]]:
    """Fiche 15, graphique 1 : la ligne des années, puis une ligne par sexe."""
    _verifier_titre(grille, "Graphique 1. Âge conjoncturel moyen de départ")
    ligne_annees = next(ligne for (ligne, colonne), v in sorted(grille.items())
                        if colonne > 1 and annee(v))
    annees = {colonne: annee(v) for (ligne, colonne), v in grille.items()
              if ligne == ligne_annees and annee(v)}
    serie: dict[str, dict[str, float]] = {}
    for (ligne, colonne), v in sorted(grille.items()):
        if colonne == 1 and _texte(v) in SEXES and ligne > ligne_annees:
            for col, an in annees.items():
                age = nombre(grille.get((ligne, col), ""))
                if age is not None:
                    serie.setdefault(str(an), {})[SEXES[_texte(v)]] = age
    if not serie or any(len(sexes) != 3 for sexes in serie.values()):
        raise FeuilleIllisible("une année sans ses trois âges")
    return dict(sorted(serie.items()))


def lire_cumul(grille: dict) -> dict[str, dict[str, float]]:
    """Fiche 22, tableau 1 : une ligne par année, trois grandeurs."""
    _verifier_titre(grille, "Tableau 1. Effectifs de retraités en situation de cumul")
    colonnes = {"cumulants_milliers": _colonne(grille, "Effectifs de cumulants"),
                "part_retraites_pct": _colonne(grille, "Part parmi les retraités"),
                "part_femmes_pct": _colonne(grille, "Proportion de femmes")}
    serie: dict[str, dict[str, float]] = {}
    for (ligne, colonne), v in sorted(grille.items()):
        if colonne == 1 and annee(v):
            valeurs = {nom: nombre(grille.get((ligne, col), "")) for nom, col in colonnes.items()}
            serie[str(annee(v))] = {nom: x for nom, x in valeurs.items() if x is not None}
    return serie


def lire_retraite_progressive(grille: dict) -> dict[str, dict[str, dict[str, float]]]:
    """Fiche 22, tableau 2 : les effectifs de trois années, puis, pour la
    dernière, les femmes, les hommes, la part des femmes, la part parmi les
    retraités de 60 à 69 ans et l'âge moyen, chacun l'ensemble de son groupe."""
    _verifier_titre(grille, "Tableau 2. Effectifs de bénéficiaires de la retraite progressive")
    debut = _colonne(grille, "Effectifs")
    details = {"femmes": _colonne(grille, "Femmes"), "hommes": _colonne(grille, "Hommes"),
               "part_femmes_pct": _colonne(grille, "Part des femmes"),
               "part_retraites_60_69_pct": _colonne(grille, "Part parmi les retraités"),
               "age_moyen": _colonne(grille, "Âge moyen")}
    ligne_annees = next(ligne for (ligne, colonne), v in sorted(grille.items())
                        if colonne == debut and annee(v))
    annees = {colonne: annee(v) for (ligne, colonne), v in grille.items()
              if ligne == ligne_annees and debut <= colonne < details["femmes"] and annee(v)}
    derniere = str(max(annees.values()))
    lu: dict[str, dict[str, dict[str, float]]] = {}
    for cle, ligne in _lignes_des_regimes(grille, debut - 1).items():
        regime: dict[str, dict[str, float]] = {}
        for colonne, an in sorted(annees.items()):
            effectif = nombre(grille.get((ligne, colonne), ""))
            if effectif is not None:
                regime[str(an)] = {"beneficiaires": effectif}
        for nom, colonne in details.items():
            valeur = nombre(grille.get((ligne, colonne), ""))
            if valeur is not None:
                regime.setdefault(derniere, {})[nom] = valeur
        lu[cle] = regime
    return lu


def lire_invalidite(beneficiaires: dict, nouveaux: dict, montants: dict, depenses: dict,
                    evolution: dict) -> dict[str, dict[str, dict[str, float]]]:
    """Fiche 25 : fin 2024, par régime, les tableaux 1 à 4 ; depuis 2015,
    l'ensemble, le graphique 1, la pension en euros constants de 2024."""
    _verifier_titre(beneficiaires, "Tableau 1. Bénéficiaires d’une pension d’invalidité")
    _verifier_titre(nouveaux, "Tableau 2. Nouveaux bénéficiaires d’une pension d’invalidité")
    _verifier_titre(montants, "Tableau 3. Montant mensuel des pensions d’invalidité")
    _verifier_titre(depenses, "Tableau 4. Dépenses de pensions d’invalidité")
    _verifier_titre(evolution, "Graphique 1. Évolution du nombre de bénéficiaires d’une pension")
    lectures = (
        (beneficiaires, {"beneficiaires_milliers": "Effectifs", "age_moyen": "Âge moyen",
                         "part_femmes_pct": "Part des femmes"}),
        (nouveaux, {"nouveaux_milliers": "Effectifs"}),
        (montants, {"montant_mensuel_euros": "Pension d’invalidité de droit direct"}),
        (depenses, {"depenses_meur": "Total"}),
    )
    fin_2024: dict[str, dict[str, float]] = {}
    for grille, grandeurs in lectures:
        colonnes = {nom: _colonne(grille, entete, exact=entete == "Total")
                    for nom, entete in grandeurs.items()}
        for cle, ligne in _lignes_des_regimes(grille, 1).items():
            for nom, colonne in colonnes.items():
                valeur = nombre(grille.get((ligne, colonne), ""))
                if valeur is not None:
                    # Le tableau 3 affiche ses montants à l'euro.
                    fin_2024.setdefault(cle, {})[nom] = (
                        float(round(valeur)) if nom == "montant_mensuel_euros" else valeur)
    effectifs = _colonne(evolution, "Effectifs de bénéficiaires")
    pension = _colonne(evolution, "Pension d'invalidité de droit direct moyenne")
    if "euros constants de 2024" not in _texte(evolution[(min(l for l, c in evolution
                                                             if c == pension), pension)]):
        raise FeuilleIllisible("la pension du graphique 1 n'est plus en euros de 2024")
    lu: dict[str, dict[str, dict[str, float]]] = {}
    for (ligne, colonne), v in sorted(evolution.items()):
        if colonne == 1 and annee(v):
            lu[str(annee(v))] = {"ensemble": {
                "beneficiaires_milliers": nombre(evolution[(ligne, effectifs)]),
                "pension_moyenne_euros_2024": round(nombre(evolution[(ligne, pension)]), 2)}}
    for cle, grandeurs in fin_2024.items():
        lu.setdefault("2024", {}).setdefault(cle, {}).update(grandeurs)
    return lu


def _age(valeur) -> int | None:
    """Un âge de ligne : 20.0, ou « 20 » ; « Âge (en années) » n'en est pas un."""
    if isinstance(valeur, (int, float)):
        return int(valeur) if 0 <= valeur < 120 and valeur == int(valeur) else None
    texte = _texte(valeur)
    return int(texte) if texte.isdigit() and int(texte) < 120 else None


def _annee_du_titre(grille: dict, debut: str) -> str:
    """L'année que le titre nomme en dernier : « …, par âge, en 2024 »."""
    for valeur in grille.values():
        if isinstance(valeur, str) and _texte(valeur).startswith(debut):
            annees = re.findall(r"\b((?:19|20)\d\d)\b", _texte(valeur))
            if annees:
                return annees[-1]
    raise FeuilleIllisible(f"aucune année au titre « {debut} »")


def lire_retraite_progressive_cnav(grille: dict) -> dict[str, float]:
    """Fiche 22, graphique 1 : les assurés en retraite progressive au régime
    général, une ligne par année depuis 1989, du recueil de la Cnav."""
    _verifier_titre(grille, "Graphique 1. Évolution des effectifs d’assurés en retraite progressive")
    effectifs = _colonne(grille, "Effectifs", exact=True)
    serie = {str(annee(v)): nombre(grille.get((ligne, effectifs), ""))
             for (ligne, colonne), v in sorted(grille.items()) if colonne == 1 and annee(v)}
    serie = {an: valeur for an, valeur in serie.items() if valeur is not None}
    if not serie:
        raise FeuilleIllisible("aucune année sous « Effectifs »")
    return serie


def lire_invalidite_par_age(graphique: dict, complement: dict
                            ) -> dict[str, dict[str, dict[str, float]]]:
    """Fiche 25, graphique 2 : les bénéficiaires de l'année du titre, par âge,
    l'ensemble ; son complément : par sexe, une colonne par année sous
    l'en-tête de son sexe. Les cases sont des personnes, arrondies à la
    dizaine, quoi qu'en dise l'en-tête du graphique (« en milliers ») : ses
    âges font les 843 400 bénéficiaires du tableau 1."""
    titre = "Graphique 2. Nombre et part des bénéficiaires d’une pension d’invalidité"
    _verifier_titre(graphique, titre)
    _verifier_titre(complement, "Graphique 2 complémentaire. Évolution du nombre de "
                                "bénéficiaires de pensions d'invalidité par âge et par sexe")
    lu: dict[str, dict[str, dict[str, float]]] = {}
    beneficiaires = _colonne(graphique, "Nombre de bénéficiaires")
    ensemble = lu.setdefault(_annee_du_titre(graphique, titre), {}).setdefault("ensemble", {})
    for (ligne, colonne), v in sorted(graphique.items()):
        if colonne == 1 and _age(v) is not None:
            valeur = nombre(graphique.get((ligne, beneficiaires), ""))
            if valeur is not None:
                ensemble[str(_age(v))] = valeur
    sexes = {_colonne(complement, "Femmes", exact=True): "F",
             _colonne(complement, "Hommes", exact=True): "H"}
    ligne_annees = min(ligne for (ligne, colonne), v in complement.items()
                       if colonne > 1 and annee(v))
    colonnes = {}
    for (ligne, colonne), v in complement.items():
        if ligne == ligne_annees and annee(v):
            gauche = [c for c in sexes if c <= colonne]
            if not gauche:
                raise FeuilleIllisible(f"la colonne {colonne} n'a pas de sexe")
            colonnes[colonne] = (str(annee(v)), sexes[max(gauche)])
    for (ligne, colonne), v in sorted(complement.items()):
        if colonne == 1 and ligne > ligne_annees and _age(v) is not None:
            for col, (an, sexe) in colonnes.items():
                valeur = nombre(complement.get((ligne, col), ""))
                if valeur is not None:
                    lu.setdefault(an, {}).setdefault(sexe, {})[str(_age(v))] = valeur
    return lu


#: Fiche 27, tableau 1 : les régimes de versement du minimum vieillesse, dans
#: l'ordre où une ligne se reconnaît — « Total champ enquête Drees » avant
#: « Total » ; la SNCF, la CANSSM, l'Enim, le FSPOEIE, la CNRACL, la FPE et
#: les autres sont les lignes des régimes spéciaux.
REGIMES_MINIMUM_VIEILLESSE = (
    ("Régime général", "regime_general"), ("Saspa", "saspa"),
    ("MSA non-salariés", "msa_exploitants"), ("MSA salariés", "msa_salaries"),
    ("Cavimac", "cavimac"), ("Professions libérales", "professions_liberales"),
    ("Régimes spéciaux", "regimes_speciaux"), ("SNCF", "sncf"), ("CANSSM", "canssm"),
    ("Enim", "enim"), ("FSPOEIE", "fspoeie"), ("CNRACL", "cnracl"),
    ("FPE", "fonction_publique_etat"), ("Autres", "autres"),
    ("Total champ enquête Drees", "champ_enquete_drees"), ("Total", "ensemble"),
)

TERRITOIRES = (("Métropole", "metropole"), ("DROM", "drom"))


def _simple(valeur) -> str:
    """Le texte d'une case, l'apostrophe courbe redressée : les en-têtes d'une
    même feuille emploient l'une et l'autre."""
    return _texte(valeur).replace("’", "'")


def _cle(libelle, table):
    """La clé du premier libellé de ``table`` par lequel la case commence ;
    une case numérique se lit comme le classeur l'écrit (« 0.8 »)."""
    texte = _simple(libelle) if libelle is not None else ""
    return next((cle for debut, cle in table if texte.startswith(debut.replace("’", "'"))), None)


def lire_minimum_vieillesse_regimes(grille: dict) -> dict[str, dict[str, dict[str, float]]]:
    """Fiche 27, tableau 1 : les allocataires de fin d'année par régime de
    versement, et, sous un régime, ses lignes « Métropole » et « DROM ». Les
    évolutions depuis l'année d'avant et les parts par caisse ne se lisent
    pas : les effectifs donnent les unes, une autre année porte les autres."""
    _verifier_titre(grille, "Tableau 1. Nombre d’allocataires du minimum vieillesse")
    colonnes = {"premier_etage": _colonne(grille, "Toutes allocations dites de premier étage"),
                "asv": _colonne(grille, "ASV (ancien"), "aspa": _colonne(grille, "Aspa (L. 815-1)"),
                "asv_aspa": _colonne(grille, "ASV et Aspa", exact=True),
                "asi": _colonne(grille, "Allocation supplémentaire d'invalidité")}
    lu: dict[str, dict[str, dict[str, float]]] = {}
    regime = None
    for (ligne, colonne), libelle in sorted(grille.items()):
        if colonne != 1:
            continue
        territoire = _cle(libelle, TERRITOIRES)
        cle = None if territoire else _cle(libelle, REGIMES_MINIMUM_VIEILLESSE)
        if cle:
            regime, territoire = cle, "ensemble"
        elif not (territoire and regime):
            continue
        valeurs = {nom: nombre(grille.get((ligne, col), "")) for nom, col in colonnes.items()}
        lu.setdefault(regime, {})[territoire] = {nom: v for nom, v in valeurs.items()
                                                 if v is not None}
    if not {"regime_general", "ensemble"} <= set(lu):
        raise FeuilleIllisible("le tableau 1 n'a plus son régime général ou son total")
    return lu


def lire_minimum_vieillesse_effectifs(grille: dict) -> dict[str, dict[str, float]]:
    """Fiche 27, graphique 1 : les allocataires de l'ASV ou de l'Aspa depuis
    1960, en milliers, et leur part parmi les 60 ans ou plus et parmi les
    65 ans ou plus, une ligne par année."""
    _verifier_titre(grille, "Graphique 1. Évolution du nombre d’allocataires de l’ASV ou de l’Aspa")
    colonnes = {"allocataires_milliers": _colonne(grille, "Nombre d'allocataires"),
                "part_60_plus_pct": _colonne(grille, "Part d'allocataires dans la population "
                                                     "âgée de 60 ans ou plus"),
                "part_65_plus_pct": _colonne(grille, "Part d'allocataires dans la population "
                                                     "âgée de 65 ans ou plus")}
    serie: dict[str, dict[str, float]] = {}
    for (ligne, colonne), v in sorted(grille.items()):
        if colonne == 1 and annee(v):
            valeurs = {nom: nombre(grille.get((ligne, col), "")) for nom, col in colonnes.items()}
            serie[str(annee(v))] = {nom: x for nom, x in valeurs.items() if x is not None}
    if not serie:
        raise FeuilleIllisible("aucune année au graphique 1")
    return serie


#: Fiche 23 : les tranches d'âge des cumulants (tableau 1 et son complément),
#: leurs catégories (tableau 2), leur temps de travail (tableau 3) — « 80 % »
#: et « 50 % », que le classeur écrit en nombres —, leurs grandeurs.
TRANCHES_CUMUL = (
    ("De 55 à 59 ans", "55_59"), ("De 60 à 64 ans", "60_64"), ("de 60 à 61 ans", "60_61"),
    ("de 62 à 64 ans", "62_64"), ("De 65 à 69 ans", "65_69"), ("70 ans ou plus", "70_plus"),
    ("55 ans ou plus", "55_plus"),
)
GRANDEURS_CUMUL_AGE = (
    ("cumulants", "Effectifs de cumulants"), ("part_population_pct", "Part parmi la population"),
    ("part_retraites_pct", "Part parmi les retraités"),
    ("part_emploi_pct", "Part parmi les personnes en emploi"),
    ("repartition_pct", "Répartition par âge"), ("part_femmes_pct", "Proportion de femmes"),
)
CATEGORIES_CUMUL = (
    ("Agriculteurs exploitants", "agriculteurs_exploitants"),
    ("Artisans, commerçants et chefs d'entreprise", "artisans_commercants_chefs_entreprise"),
    ("Cadres et professions intellectuelles supérieures", "cadres"),
    ("Professions intermédiaires", "professions_intermediaires"), ("Employés", "employes"),
    ("Ouvriers", "ouvriers"), ("Total", "total"),
)
TEMPS_CUMUL = (
    ("Temps complet", "temps_complet"), ("Temps partiel", "temps_partiel"),
    ("plus de 80 %", "plus_80_pct"), ("0.8", "80_pct"), ("entre 50 % et moins de 80 %", "50_80_pct"),
    ("0.5", "50_pct"), ("moins d'un mi-temps", "moins_mi_temps"), ("Total", "total"),
)
REPARTITIONS_CUMUL = {
    "Tableau 2. Répartition par catégorie socioprofessionnelle": ("csp", CATEGORIES_CUMUL),
    "Tableau 3. Répartition des personnes ayant cumulé un emploi et une retraite, selon la "
    "durée du temps de travail": ("temps_travail", TEMPS_CUMUL),
}
#: Fiche 23, tableau 4 et graphique 1 : les caisses, « CNAVPL » avant « CNAV ».
CAISSES_CUMUL = (("Régime général", "regime_general"), ("CNAVPL", "cnavpl"),
                 ("CNAV", "regime_general"), ("MSA salariés", "msa_salaries"),
                 ("MSA non-salariés", "msa_exploitants"))
#: Fiche 23, tableaux 5 et 6 : les régimes de retraite (en colonnes) et
#: d'emploi (en lignes) de la génération 1950, puis ceux de la fonction publique.
RETRAITE_1950 = (("Régime général", "regime_general"), ("Fonction publique", "fonction_publique"),
                 ("Professions libérales", "professions_liberales"), ("MSA", "msa"),
                 ("Ensemble des retraités", "ensemble"))
EMPLOI_1950 = (("Régime général", "emploi_regime_general"),
               ("Fonction publique", "emploi_fonction_publique"),
               ("Professions libérales", "emploi_professions_liberales"), ("MSA", "emploi_msa"),
               ("Tous régimes d'emploi confondus", "emploi_tous_regimes"))
FONCTION_PUBLIQUE_1950 = (
    ("FPE civils", ("fpe_civils", "ensemble")), ("FPE militaires", ("fpe_militaires", "ensemble")),
    ("CNRACL", ("cnracl", "ensemble")),
    ("Fonctionnaires civils partis avant 60 ans", ("fonctionnaires_civils", "partis_avant_60")),
    ("Fonctionnaires civils partis à 60 ans ou après",
     ("fonctionnaires_civils", "partis_60_ou_apres")),
)


def _premiere_colonne(grille: dict, debut: str, apres: int = 0) -> int:
    trouvees = [c for (_, c), v in grille.items()
                if c > apres and isinstance(v, str) and _simple(v).startswith(debut)]
    if not trouvees:
        raise FeuilleIllisible(f"aucun en-tête « {debut} »")
    return min(trouvees)


def _colonnes_sous_les_sexes(grille: dict, grandeurs: dict[str, str]) -> dict[tuple, int]:
    """Les colonnes groupées sous « Femmes », « Hommes » et « Ensemble » :
    chaque sexe couvre la sienne jusqu'à celle du suivant, et, sous lui,
    chaque grandeur se reconnaît au début de son en-tête."""
    debuts = {SEXES[nom]: _colonne(grille, nom, exact=True) for nom in SEXES}
    colonnes = {}
    for sexe, debut in debuts.items():
        fin = min((c for c in debuts.values() if c > debut), default=debut + 100)
        for nom, libelle in grandeurs.items():
            trouvees = [c for (_, c), v in grille.items() if debut <= c < fin
                        and isinstance(v, str) and _simple(v).startswith(libelle)]
            if not trouvees:
                raise FeuilleIllisible(f"aucun en-tête « {libelle} » sous « {sexe} »")
            colonnes[(sexe, nom)] = min(trouvees)
    return colonnes


def _annee_des_vivants(grille: dict) -> str:
    """L'année du champ « vivants au 31 décembre 2020 » : celle où
    l'échantillon voit la génération."""
    for valeur in grille.values():
        trouve = re.search(r"vivants au 31 décembre ((?:19|20)\d\d)", _texte(valeur))
        if trouve:
            return trouve.group(1)
    raise FeuilleIllisible("le champ ne dit plus l'année où la génération est vue")


def lire_cumul_par_age(grille: dict) -> dict[tuple, float]:
    """Fiche 23, tableau 1 ou son complément : un bloc par année, les tranches
    d'âge en lignes ; le complément porte la France métropolitaine à gauche
    et la France hors Mayotte à droite, celle du tableau 1, seule lue."""
    if not any(isinstance(v, str) and _texte(v).startswith(debut) for v in grille.values()
               for debut in ("Tableau 1. Effectifs de personnes cumulant emploi et retraite",
                             "Tableau 1 complémentaire. Effectifs des personnes en cumul")):
        raise FeuilleIllisible("aucun titre du tableau 1")
    libelles = min((c for (_, c), v in grille.items()
                    if isinstance(v, str) and _texte(v).startswith("France (hors Mayotte)")),
                   default=1)
    colonnes = {nom: _premiere_colonne(grille, debut, libelles)
                for nom, debut in GRANDEURS_CUMUL_AGE}
    annees = {ligne: annee(v) for (ligne, c), v in grille.items()
              if c == libelles + 1 and annee(v)}
    lu = {}
    for (ligne, colonne), libelle in sorted(grille.items()):
        tranche = _cle(libelle, TRANCHES_CUMUL) if colonne == libelles else None
        au_dessus = [l for l in annees if l < ligne]
        if tranche and au_dessus:
            an = str(annees[max(au_dessus)])
            for nom, col in colonnes.items():
                valeur = nombre(grille.get((ligne, col), ""))
                if valeur is not None:
                    lu[(an, "age", "tous_regimes", tranche, "ensemble", nom)] = valeur
    if not lu:
        raise FeuilleIllisible("aucune tranche d'âge sous une année")
    return lu


def lire_cumul_repartition(grille: dict) -> dict[tuple, float]:
    """Fiche 23, tableau 2 (les catégories) ou 3 (le temps de travail) : sous
    chaque sexe, la part parmi les cumulants et parmi les personnes en emploi
    non retraitées, en lignes les modalités."""
    titre = next((debut for debut in REPARTITIONS_CUMUL for v in grille.values()
                  if isinstance(v, str) and _texte(v).startswith(debut)), None)
    if titre is None:
        raise FeuilleIllisible("ni le tableau 2 ni le tableau 3")
    champ, modalites = REPARTITIONS_CUMUL[titre]
    an = _annee_du_titre(grille, titre)
    colonnes = _colonnes_sous_les_sexes(grille, {
        "part_cumulants_pct": "Part parmi l'ensemble des cumulants",
        "part_emploi_non_retraites_pct": "Part parmi l'ensemble des personnes"})
    lu = {}
    for (ligne, colonne), libelle in sorted(grille.items()):
        modalite = _cle(libelle, modalites) if colonne == 1 else None
        for (sexe, nom), col in (colonnes.items() if modalite else ()):
            valeur = nombre(grille.get((ligne, col), ""))
            if valeur is not None:
                lu[(an, champ, "tous_regimes", modalite, sexe, nom)] = valeur
    return lu


def lire_cumul_meme_regime(tableau: dict, graphique: dict) -> dict[tuple, float]:
    """Fiche 23, tableau 4 : les cumulants dans un même régime, caisse par
    caisse — leurs effectifs, en milliers, des années de l'en-tête, la part
    des femmes et la part des cumulants par sexe de la dernière ; graphique
    1 : cette part par âge, l'année de chaque caisse étant celle de la note."""
    _verifier_titre(tableau, "Tableau 4. Retraités de droit direct cumulant un emploi et une "
                             "retraite dans un même régime")
    _verifier_titre(graphique, "Graphique 1. Part des retraités de droit direct cumulant un "
                               "emploi et une retraite au sein du même régime")
    effectifs = _colonne(tableau, "Effectifs (en milliers)")
    evolution = _colonne(tableau, "Évolution")
    femmes = _colonne(tableau, "Part des femmes parmi les cumulants")
    parts = _colonne(tableau, "Part des cumulants au sein des retraités du régime")
    annees = {c: str(annee(v)) for (_, c), v in tableau.items()
              if effectifs <= c < evolution and annee(v)}
    annee_femmes = next(str(annee(v)) for (_, c), v in sorted(tableau.items())
                        if c == femmes and annee(v))
    annee_parts = next(str(annee(v)) for (_, c), v in sorted(tableau.items())
                       if c == parts and annee(v))
    sexes = {c: SEXES[_texte(v)] for (_, c), v in tableau.items()
             if c >= parts and isinstance(v, str) and _texte(v) in SEXES}
    lu = {}
    for (ligne, colonne), libelle in sorted(tableau.items()):
        caisse = _cle(libelle, CAISSES_CUMUL) if colonne == 1 else None
        if not caisse:
            continue
        cases = [(an, "ensemble", "cumulants_milliers", c) for c, an in annees.items()]
        cases.append((annee_femmes, "ensemble", "part_femmes_pct", femmes))
        cases += [(annee_parts, sexe, "part_retraites_pct", c) for c, sexe in sexes.items()]
        for an, sexe, nom, col in cases:
            valeur = nombre(tableau.get((ligne, col), ""))
            if valeur is not None:
                lu[(an, "meme_regime", caisse, "ensemble", sexe, nom)] = valeur
    note = re.search(r"Les données concernent ((?:19|20)\d\d), sauf celles de la CNAV, qui "
                     r"portent sur ((?:19|20)\d\d)", " ".join(_texte(v) for v in graphique.values()))
    if not note:
        raise FeuilleIllisible("la note du graphique 1 ne dit plus l'année de chaque caisse")
    colonnes = {}
    for (_, c), v in graphique.items():
        caisse = _cle(v, CAISSES_CUMUL) if c > 1 and isinstance(v, str) else None
        if caisse:
            cnav = _texte(v).startswith("CNAV") and not _texte(v).startswith("CNAVPL")
            colonnes[c] = (caisse, note.group(2) if cnav else note.group(1))
    for (ligne, colonne), v in sorted(graphique.items()):
        if colonne == 1 and _age(v) is not None:
            for col, (caisse, an) in colonnes.items():
                valeur = nombre(graphique.get((ligne, col), ""))
                if valeur is not None:
                    lu[(an, "meme_regime", caisse, str(_age(v)), "ensemble",
                        "part_retraites_pct")] = valeur
    return lu


def lire_cumul_generation_1950(regimes: dict, fonction_publique: dict) -> dict[tuple, float]:
    """Fiche 23, tableau 5 : la part des retraités nés en 1950 qui ont cumulé
    avant 67 ans, par régime de retraite principal (en colonnes) et d'emploi
    principal (en lignes) ; tableau 6 : dans la fonction publique, par sexe."""
    _verifier_titre(regimes, "Tableau 5. Part des retraités nés en 1950 ayant cumulé")
    _verifier_titre(fonction_publique, "Tableau 6. Part des retraités des régimes de la FPE et "
                                       "de la CNRACL nés en 1950")
    nom = "part_ayant_cumule_pct"
    lu = {}
    an = _annee_des_vivants(regimes)
    retraite = {c: cle for (_, c), v in regimes.items()
                if c > 1 and isinstance(v, str) and (cle := _cle(v, RETRAITE_1950))}
    if "ensemble" not in retraite.values():
        raise FeuilleIllisible("le tableau 5 n'a plus sa colonne d'ensemble")
    for (ligne, colonne), libelle in sorted(regimes.items()):
        emploi = _cle(libelle, EMPLOI_1950) if colonne == 1 else None
        for col, regime in (retraite.items() if emploi else ()):
            valeur = nombre(regimes.get((ligne, col), ""))
            if valeur is not None:
                lu[(an, "generation_1950", regime, emploi, "ensemble", nom)] = valeur
    an = _annee_des_vivants(fonction_publique)
    sexes = {_colonne(fonction_publique, libelle, exact=True): sexe
             for libelle, sexe in SEXES.items()}
    for (ligne, colonne), libelle in sorted(fonction_publique.items()):
        cle = _cle(libelle, FONCTION_PUBLIQUE_1950) if colonne == 1 else None
        for col, sexe in (sexes.items() if cle else ()):
            valeur = nombre(fonction_publique.get((ligne, col), ""))
            if valeur is not None:
                lu[(an, "generation_1950", *cle, sexe, nom)] = valeur
    return lu


def _jeu() -> dict:
    import yaml

    manifeste = yaml.safe_load((RACINE / "data" / "sources.yaml").read_text(encoding="utf-8"))
    for institution in manifeste["institutions"].values():
        for jeu in institution.get("jeux", []):
            if jeu["id"] == JEU:
                return jeu
    raise KeyError(JEU)


def _classeur(archive: zipfile.ZipFile, jeu: dict, nom: str) -> dict:
    octets = archive.read(nom)
    attendue = jeu["contenu"][nom]["sha256"]
    if hashlib.sha256(octets).hexdigest() != attendue:
        raise ValueError(f"{nom} : l'empreinte n'est pas celle du manifeste")
    return lecture_xlsx.feuilles(octets)


def lire(chemin: Path, jeu: dict) -> dict:
    """Les séries de l'archive, chaque classeur vérifié à son empreinte."""
    with zipfile.ZipFile(chemin) as archive:
        f15 = _classeur(archive, jeu, "fiche_15.xlsx")
        f22 = _classeur(archive, jeu, "fiche_22.xlsx")
        f23 = _classeur(archive, jeu, "fiche_23.xlsx")
        f25 = _classeur(archive, jeu, "fiche_25.xlsx")
        f27 = _classeur(archive, jeu, "fiche_27.xlsx")
    return {
        "age_conjoncturel": lire_age_conjoncturel(f15["F15_Graphique 1"]),
        "cumul": lire_cumul(f22["F22_Tableau1"]),
        "retraite_progressive": lire_retraite_progressive(f22["F22_Tableau2"]),
        "retraite_progressive_cnav": lire_retraite_progressive_cnav(f22["F22_Graphique1"]),
        "invalidite": lire_invalidite(f25["F25_Tableau 1"], f25["F25_Tableau 2"],
                                      f25["F25_Tableau 3"], f25["F25_Tableau 4"],
                                      f25["F25_Graphique 1"]),
        "invalidite_par_age": lire_invalidite_par_age(f25["F25_Graphique 2"],
                                                      f25["F25_Graphique 2 compl"]),
        "minimum_vieillesse_regimes": {
            _annee_du_titre(f27["F27_Tableau 1"], "Tableau 1. Nombre d’allocataires du minimum"):
            lire_minimum_vieillesse_regimes(f27["F27_Tableau 1"])},
        "minimum_vieillesse_effectifs": lire_minimum_vieillesse_effectifs(f27["F27_Graphique 1"]),
        "cumul_profil": [[*cle, valeur] for cle, valeur in sorted({
            **lire_cumul_par_age(f23["F23_Tableau 1 compl."]),
            **lire_cumul_repartition(f23["F23_Tableau 2"]),
            **lire_cumul_repartition(f23["F23_Tableau 3"]),
            **lire_cumul_meme_regime(f23["F23_Tableau 4"], f23["F23_Graphique 1"]),
            **lire_cumul_generation_1950(f23["F23_Tableau 5"], f23["F23_Tableau 6"]),
        }.items())],
    }


def main(argv: list[str] | None = None) -> int:
    jeu = _jeu()
    chemin = RACINE / "data" / "brut" / jeu["fichier_local"]
    if not chemin.is_file():
        print(f"{chemin.relative_to(RACINE)} absent : lancer "
              "python scripts/fetch/source_locale.py --recuperer", file=sys.stderr)
        return 1
    charge = {"source": {"jeu": JEU, "sha256": jeu["sha256"], "millesime": jeu["millesime"],
                         "lu_le": date.today().isoformat()},
              **lire(chemin, jeu)}
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} : " + ", ".join(
        f"{nom} ({len(serie)})" for nom, serie in charge.items() if nom != "source"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
