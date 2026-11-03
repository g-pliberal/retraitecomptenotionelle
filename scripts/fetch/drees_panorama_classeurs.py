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
* ``pensions_moyennes`` — fiche 5, tableau 1 complémentaire bis : la pension
  mensuelle moyenne brute et la nette des retraités résidant en France ou à
  l'étranger, de droit direct et totale, de 2004 à 2024 ; le tableau 2.1-a,
  que ``pensions_brutes_nettes.csv`` certifie, s'arrête à 2022 ;
* ``cumul`` — fiche 22, tableau 1 : les retraités qui cumulent une activité
  et leur retraite, de 2014 à 2024, l'enquête Emploi de l'INSEE ;
* ``retraite_progressive`` — fiche 22, tableau 2 : ses bénéficiaires par
  régime en 2015, 2023 et 2024, l'EACR ;
* ``invalidite`` — fiche 25, graphique 1 et tableaux 1 à 4 : les
  bénéficiaires d'une pension d'invalidité de droit direct depuis 2015, et,
  fin 2024, par régime, leur âge, leurs nouveaux, leur pension, leur dépense.

Puis les séries des graphiques et des tableaux que le PDF ne chiffre pas
(étape 6) : ``retraite_progressive_cnav`` (fiche 22, graphique 1, depuis
1989) ; ``invalidite_par_age`` (fiche 25, graphique 2 et son complément) ;
``minimum_vieillesse_regimes`` et ``minimum_vieillesse_effectifs`` (fiche 27,
tableau 1 et graphique 1) ; ``cumul_profil`` (fiche 23) ;
``rapport_emploi_retraites`` (fiche 1, graphique 1) ; ``retraites_generations``
(fiches 1, 16 et 17 : polypension, âge et taux de liquidation par génération) ;
``reversion`` (fiche 3, graphiques 2 et 4). Enfin, l'échantillon
interrégimes de cotisants de 2021 (étape 3) : ``durees_validees`` (fiche 12,
graphiques 1 à 5 : les trimestres validés à 30 ans et le début de carrière, le
rythme de validation par tranche d'âge, la nature des trimestres, le chômage
validé, les validations de l'année par âge) et ``fins_de_carriere`` (fiche 21,
graphiques 1 et 2, tableaux 1 à 3 : la situation à 59 ans et de 50 à 67 ans,
l'année qui précède la liquidation, les trajectoires et les transitions). Les
séries à plusieurs clés s'écrivent en listes, chaque élément ses clés puis sa
valeur ; une grandeur que deux figures donnent y est une fois, à la valeur
qu'elles disent toutes deux.

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


#: Fiche 5, tableau 1 complémentaire bis : les deux pensions que le dépôt suit,
#: par le début de leur en-tête, et leur nom dans ``pensions_brutes_nettes.csv``
#: ; la pension de droit direct HORS majoration n'en est pas une.
PENSIONS_MOYENNES = (
    ("Pension de droit direct, y compris majoration", "directe"),
    ("Pension totale", "totale"),
)


def lire_pensions_moyennes(grille: dict) -> dict[str, dict[str, float]]:
    """Fiche 5, tableau 1 complémentaire bis : la pension mensuelle moyenne de
    l'ensemble des retraités résidant en France ou à l'étranger, le champ de
    ``pensions_brutes_nettes.csv``, brute et nette, de droit direct majoration
    comprise et totale, une ligne par année. Sous l'en-tête de chaque pension,
    et avant celui de la suivante, la colonne de l'ensemble, brute puis nette.
    Le tableau 1 et son complément, résidents en France seulement, ont le même
    dessin : leur titre arrête la lecture."""
    _verifier_titre(grille, "Tableau 1 complémentaire bis. Montant mensuel moyen de la "
                            "pension des retraités résidant en France ou à l")
    premiere_annee = min(ligne for (ligne, colonne), v in grille.items()
                         if colonne == 1 and annee(v))
    colonnes: dict[int, str] = {}
    for debut, pension in PENSIONS_MOYENNES:
        colonne = _colonne(grille, debut)
        ligne_entete = next(l for (l, c), v in sorted(grille.items()) if c == colonne
                            and isinstance(v, str) and _texte(v).startswith(debut))
        suivante = min((c for (l, c), v in grille.items()
                        if l == ligne_entete and c > colonne and isinstance(v, str)),
                       default=max(c for _, c in grille) + 1)
        for nature in ("Brute", "Nette"):
            trouvee = next((c for c in range(colonne, suivante)
                            if {nature, "Ensemble"} <= {
                                _texte(v) for (l, col), v in grille.items()
                                if col == c and ligne_entete < l < premiere_annee}), None)
            if trouvee is None:
                raise FeuilleIllisible(f"aucune colonne « {nature} », « Ensemble » "
                                       f"sous la pension {pension}")
            colonnes[trouvee] = f"{nature.lower()}_{pension}"
    serie: dict[str, dict[str, float]] = {}
    for (ligne, colonne), v in sorted(grille.items()):
        if colonne == 1 and annee(v):
            valeurs = {nom: nombre(grille.get((ligne, col), "")) for col, nom in colonnes.items()}
            serie[str(annee(v))] = {nom: x for nom, x in valeurs.items() if x is not None}
    return serie


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


def _generation_du_titre(grille: dict, debut: str) -> str:
    """La génération que nomme le titre qui commence par ``debut`` (« … nés
    en », « … née en ») : l'année qui le suit, non l'échantillon qui clôt le
    titre (« …, en 2020 »)."""
    for valeur in grille.values():
        texte = _texte(valeur) if isinstance(valeur, str) else ""
        if texte.startswith(debut):
            trouve = re.match(r"\s*((?:19|20)\d\d)\b", texte[len(debut):])
            if trouve:
                return trouve.group(1)
    raise FeuilleIllisible(f"aucune génération après « {debut} »")


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


# ---------------------------------------------------------------------------
# Les séries que le suivi porte aux référents : fiches 1, 3, 16 et 17
# ---------------------------------------------------------------------------

SEXES_EN_TETE = tuple(SEXES.items())
AGES_PREMIERE_1953 = (
    ("Moins de 55 ans", "moins_55"), ("55 ans", "55"), ("56-59 ans", "56_59"), ("60 ans", "60"),
    ("61 ans", "61"), ("62 ans", "62"), ("63-65 ans", "63_65"), ("66 ans", "66"),
    ("67 ans ou plus", "67_plus"), ("Âge moyen", "age_moyen"),
)
AGES_PREMIERE_GENERATIONS = (
    ("Moins de 55 ans", "moins_55"), ("55 ans", "55"), ("56-59 ans", "56_59"), ("60 ans", "60"),
    ("61 ans", "61"), ("62 ans", "62"), ("63-64 ans", "63_64"), ("65 ans", "65"),
    ("66 ans ou plus", "66_plus"),
)
#: Fiche 16, tableau 2 : les en-têtes d'âge sont des textes ou des nombres.
AGES_REGIME_PRINCIPAL = (
    ("Moins de 55", "moins_55"), ("55", "55"), ("56-59", "56_59"), ("60", "60"), ("61", "61"),
    ("62", "62"), ("63-65", "63_65"), ("66", "66"), ("67 ou plus", "67_plus"),
)
REGIMES_PRINCIPAUX = (
    ("Régime général", "regime_general"), ("MSA salariés", "msa_salaries"),
    ("FPE civils", "fonction_publique_etat_civile"), ("FPE militaires", "fonction_publique_etat_militaire"),
    ("CNRACL", "cnracl"), ("Régimes spéciaux", "regimes_speciaux"),
    ("MSA non-salariés", "msa_exploitants"), ("Professions libérales", "professions_liberales"),
    ("Ensemble", "ensemble"),
)
MOTIFS_TAUX = (
    ("Départ avec décote", "decote"), ("Départ au taux plein, dont", "taux_plein"),
    ("Décote non applicable", "decote_non_applicable"),
    ("Départ au taux plein par l'âge", "taux_plein_age"), ("Ex-invalidité", "ex_invalidite"),
    ("Inaptitude au travail", "inaptitude"), ("Départ au taux plein pour autre motif", "autre_motif"),
    ("Départ au taux plein (sans surcote) par la durée", "taux_plein_duree"),
    ("Départ avec surcote", "surcote"),
)
REGIMES_DECOTE = (
    ("Régime général", "regime_general"), ("MSA salariés", "msa_salaries"),
    ("MSA non-salariés", "msa_exploitants"), ("FPE civils", "fonction_publique_etat_civile"),
    ("CNRACL", "cnracl"), ("Tous régimes", "tous_regimes"),
)


def _lignes(grille: dict, table=None) -> dict[int, str]:
    """Les lignes de données : celles dont la première case commence par un
    libellé de ``table``, ou, sans elle, porte une année ou une génération."""
    if table is None:
        return {l: str(annee(v)) for (l, c), v in grille.items() if c == 1 and annee(v)}
    return {l: cle for (l, c), v in grille.items() if c == 1 and (cle := _cle(v, table))}


def _entetes(grille: dict, table, premiere: int, *, apres: int = 1,
             avant: int = 10 ** 6) -> dict[int, str]:
    """Les colonnes, entre ``apres`` et ``avant``, dont l'en-tête, au-dessus de
    la ligne ``premiere``, commence par un libellé de ``table``."""
    return {c: cle for (l, c), v in grille.items()
            if l < premiere and apres < c < avant and (cle := _cle(v, table))}


def _generations_en_tete(grille: dict, premiere: int) -> dict[int, str]:
    return {c: str(annee(v)) for (l, c), v in grille.items() if l < premiere and c > 1 and annee(v)}


def _cases(grille: dict, lignes: dict[int, str], colonnes: dict[int, str]) -> dict[tuple, float]:
    """{(clé de ligne, clé de colonne): valeur}, une case non numérique omise."""
    if not lignes or not colonnes:
        raise FeuilleIllisible("aucune ligne ou aucune colonne reconnue")
    lu = {}
    for ligne, cle_ligne in lignes.items():
        for colonne, cle_colonne in colonnes.items():
            valeur = nombre(grille.get((ligne, colonne), ""))
            if valeur is not None:
                lu[(cle_ligne, cle_colonne)] = valeur
    return lu


def _exiger(colonnes: dict, attendues: set, feuille: str) -> dict:
    if not attendues <= set(colonnes.values()):
        raise FeuilleIllisible(f"{feuille} : il manque {sorted(attendues - set(colonnes.values()))}")
    return colonnes


def lire_rapport_emploi_retraites(grille: dict) -> dict[str, dict[str, float]]:
    """Fiche 1, graphique 1 : les retraités de droit direct, résidant en
    France ou à l'étranger puis en France seulement, et l'emploi intérieur,
    en milliers, une ligne par année ; le rapport, qu'ils donnent, ne se lit
    pas."""
    _verifier_titre(grille, "Graphique 1. Rapport entre les effectifs de personnes en emploi")
    retraites = _colonne(grille, "Effectifs de retraités de droits directs")
    emploi = _colonne(grille, "Emploi intérieur")
    lignes = _lignes(grille)
    colonnes = _entetes(grille, (("Résidant en France ou à l'étranger", "retraites_milliers"),
                                 ("Résidant en France uniquement", "retraites_france_milliers")),
                        min(lignes, default=0), apres=retraites - 1, avant=emploi)
    colonnes[emploi] = "emploi_interieur_milliers"
    _exiger(colonnes, {"retraites_milliers", "retraites_france_milliers"}, "fiche 1, graphique 1")
    lu: dict[str, dict[str, float]] = {}
    for (an, nom), valeur in _cases(grille, lignes, colonnes).items():
        lu.setdefault(an, {})[nom] = valeur
    return lu


def lire_polypensionnes(grille: dict) -> dict[tuple, float]:
    """Fiche 1, graphique 3 : la part des polypensionnés par génération et
    par sexe."""
    _verifier_titre(grille, "Graphique 3. Part des polypensionnés, par génération et par sexe")
    lignes = _lignes(grille)
    colonnes = _exiger(_entetes(grille, SEXES_EN_TETE, min(lignes, default=0)),
                       set(SEXES.values()), "fiche 1, graphique 3")
    return {(generation, "polypension", "tous_regimes", "ensemble", sexe, "part_pct"): valeur
            for (generation, sexe), valeur in _cases(grille, lignes, colonnes).items()}


def lire_age_premiere_liquidation(tableau: dict, graphique: dict) -> dict[tuple, float]:
    """Fiche 16, tableau 1 : les nés en 1953 par âge à la première
    liquidation, par sexe — la colonne « Ensemble » de chaque sexe ; les
    résidents en France et à l'étranger ne se lisent pas —, et leur âge
    moyen ; graphique 5 : les générations d'avant, que le tableau complète."""
    titre = "Tableau 1. Répartition des retraités nés en"
    _verifier_titre(tableau, titre)
    _verifier_titre(graphique, "Graphique 5. Répartition des retraités, selon la génération et "
                               "l’âge à la première liquidation")
    generation = _generation_du_titre(tableau, titre)
    lignes = _lignes(tableau, AGES_PREMIERE_1953)
    premiere = min(lignes, default=0)
    groupes = {_colonne(tableau, "Femmes", exact=True): "F",
               _colonne(tableau, "Hommes", exact=True): "H"}
    ligne_groupes = min(l for (l, c), v in tableau.items() if c in groupes and _texte(v) == "Femmes")
    colonnes = {}
    for (l, c), v in tableau.items():
        if l < premiere and isinstance(v, str) and _texte(v) == "Ensemble":
            gauche = [g for g in groupes if g <= c]
            colonnes[c] = "ensemble" if l == ligne_groupes else groupes[max(gauche)] if gauche else None
    _exiger(colonnes, set(SEXES.values()), "fiche 16, tableau 1")
    champ = ("age_premiere_liquidation", "tous_regimes")
    lu = {}
    for (modalite, sexe), valeur in _cases(tableau, lignes, colonnes).items():
        if modalite == "age_moyen":
            lu[(generation, *champ, "ensemble", sexe, "age_moyen")] = valeur
        else:
            lu[(generation, *champ, modalite, sexe, "part_pct")] = valeur
    lignes = _lignes(graphique, AGES_PREMIERE_GENERATIONS)
    colonnes = _generations_en_tete(graphique, min(lignes, default=0))
    for (modalite, autre), valeur in _cases(graphique, lignes, colonnes).items():
        if autre != generation:
            lu[(autre, *champ, modalite, "ensemble", "part_pct")] = valeur
    return lu


def lire_liquidation_regime_principal(grille: dict) -> dict[tuple, float]:
    """Fiche 16, tableau 2 : les nés en 1953 par régime principal — l'âge
    moyen de liquidation dans ce régime, avec et sans les départs avant l'âge
    d'ouverture des droits, la répartition par âge, la part parmi les
    retraités."""
    titre = "Tableau 2. Âge de départ à la retraite et répartition des retraités nés en"
    _verifier_titre(grille, titre)
    generation = _generation_du_titre(grille, titre)
    lignes = _lignes(grille, REGIMES_PRINCIPAUX)
    premiere = min(lignes, default=0)
    age = _colonne(grille, "Âge moyen à la liquidation")
    repartition = _colonne(grille, "Répartition par âge")
    part = _colonne(grille, "Part parmi les retraités")
    colonnes = {c: ("ensemble", nom) for c, nom in _entetes(
        grille, (("Ensemble", "age_moyen"),
                 ("Après neutralisation des départs avant", "age_moyen_hors_departs_avant_aod")),
        premiere, apres=age - 1, avant=repartition).items()}
    colonnes.update({c: (modalite, "part_pct") for c, modalite in _entetes(
        grille, AGES_REGIME_PRINCIPAL, premiere, apres=repartition - 1, avant=part).items()})
    colonnes[part] = ("ensemble", "part_retraites_pct")
    return {(generation, "age_liquidation_regime_principal", regime, modalite, "ensemble", nom): v
            for (regime, (modalite, nom)), v in _cases(grille, lignes, colonnes).items()}


def lire_taux_liquidation(generation_seule: dict, generations: dict) -> dict[tuple, float]:
    """Fiche 17, graphique 1 : les nés en 1953 par taux de liquidation et
    motif du taux plein, par sexe (les colonnes de résidence ne se lisent
    pas) ; graphique 3 : les générations d'avant, une par colonne."""
    titre = "Graphique 1. Répartition des retraités de la génération née en"
    _verifier_titre(generation_seule, titre)
    _verifier_titre(generations, "Graphique 3. Répartition des retraités, selon la génération et "
                                 "le taux de liquidation")
    generation = _generation_du_titre(generation_seule, titre)
    champ = ("taux_liquidation", "tous_regimes")
    lignes = _lignes(generation_seule, MOTIFS_TAUX)
    colonnes = _exiger(_entetes(generation_seule, SEXES_EN_TETE, min(lignes, default=0)),
                       set(SEXES.values()), "fiche 17, graphique 1")
    lu = {(generation, *champ, motif, sexe, "part_pct"): valeur
          for (motif, sexe), valeur in _cases(generation_seule, lignes, colonnes).items()}
    lignes = _lignes(generations, MOTIFS_TAUX)
    colonnes = _generations_en_tete(generations, min(lignes, default=0))
    lu.update({(autre, *champ, motif, "ensemble", "part_pct"): valeur
               for (motif, autre), valeur in _cases(generations, lignes, colonnes).items()})
    return lu


def lire_decote_surcote(decote: dict, surcote: dict) -> dict[tuple, float]:
    """Fiche 17, graphiques 4 et 5 : la part des retraités partis avec une
    décote, puis avec une surcote, par génération et par régime."""
    lu = {}
    for grille, nom in ((decote, "decote"), (surcote, "surcote")):
        _verifier_titre(grille, "Graphique {}. Part des retraités ayant liquidé leurs droits avec "
                                "une {}".format(4 if nom == "decote" else 5,
                                                "décote" if nom == "decote" else nom))
        lignes = _lignes(grille)
        colonnes = _exiger(_entetes(grille, REGIMES_DECOTE, min(lignes, default=0)),
                           {"regime_general", "tous_regimes"}, f"fiche 17, {nom}")
        lu.update({(generation, nom, regime, "ensemble", "ensemble", "part_pct"): valeur
                   for (generation, regime), valeur in _cases(grille, lignes, colonnes).items()})
    return lu


def _groupe(libelle) -> str | None:
    """« De 1936 à 1940 » → 1936_1940, « Avant 1935 » → avant_1935 ;
    « 50 à 54 ans » → 50_54, « Moins de 50 ans » → moins_50."""
    texte = _texte(libelle) if isinstance(libelle, str) else ""
    if trouve := re.fullmatch(r"(?:De )?(\d+) à (\d+)(?: ans)?", texte):
        return f"{trouve.group(1)}_{trouve.group(2)}"
    if trouve := re.fullmatch(r"(Avant|Moins de) (\d+)(?: ans)?", texte):
        return f"{'avant' if trouve.group(1) == 'Avant' else 'moins'}_{trouve.group(2)}"
    return None


def lire_reversion(femmes: dict, generations: dict) -> dict[tuple, float]:
    """Fiche 3, graphique 2 : la part des femmes de 60 ans ou plus résidant
    en France qui touchent une réversion, avec ou sans droit direct, par
    année ; graphique 4 : la part des personnes qui en ont touché une, par
    groupe de générations et par âge."""
    _verifier_titre(femmes, "Graphique 2. Part des retraitées d’une pension de droit dérivé parmi "
                            "les femmes âgées de 60 ans ou plus")
    _verifier_titre(generations, "Graphique 4. Part des personnes bénéficiant d’une pension de "
                                 "droit dérivé, selon l’âge et la génération")
    lignes = _lignes(femmes)
    colonnes = _exiger(_entetes(femmes, (
        ("Bénéficiaires d'une pension de droit dérivé cumulée", "reversion_et_droit_direct"),
        ("Bénéficiaires d'une pension de droit dérivé seule", "reversion_seule")),
        min(lignes, default=0)), {"reversion_et_droit_direct", "reversion_seule"},
        "fiche 3, graphique 2")
    lu = {("femmes_60_plus", an, modalite, "part_pct"): valeur
          for (an, modalite), valeur in _cases(femmes, lignes, colonnes).items()}
    lignes = {l: cle for (l, c), v in generations.items() if c == 1 and (cle := _groupe(v))}
    colonnes = {c: cle for (l, c), v in generations.items()
                if l < min(lignes, default=0) and c > 1 and (cle := _groupe(v))}
    lu.update({("generations", groupe, age, "part_pct"): valeur
               for (groupe, age), valeur in _cases(generations, lignes, colonnes).items()})
    return lu


# ---------------------------------------------------------------------------
# L'échantillon interrégimes de cotisants de 2021 : fiches 12 et 21 (étape 3)
# ---------------------------------------------------------------------------

def reunir(*series: dict) -> dict:
    """Les clés de plusieurs figures en une série : une grandeur que deux
    figures donnent doit y avoir la même valeur, sinon la lecture s'arrête."""
    reunies: dict = {}
    for serie in series:
        for cle, valeur in serie.items():
            if cle in reunies and reunies[cle] != valeur:
                raise FeuilleIllisible(f"{cle} : {reunies[cle]} et {valeur}, deux figures "
                                       "se contredisent")
            reunies[cle] = valeur
    return reunies


def _titre(grille: dict, debut: str) -> str:
    """Le titre qui commence par ``debut``, l'apostrophe courbe redressée."""
    for valeur in grille.values():
        if isinstance(valeur, str) and _simple(valeur).startswith(debut):
            return _simple(valeur)
    raise FeuilleIllisible(f"aucun titre « {debut} »")


def _generation_nommee(grille: dict, debut: str) -> str:
    """La génération que le titre nomme, après « née en » ou « nées en »."""
    trouve = re.search(r"\bnée?s? en ((?:19|20)\d\d)\b", _titre(grille, debut))
    if not trouve:
        raise FeuilleIllisible(f"le titre « {debut} » ne nomme plus de génération")
    return trouve.group(1)


def _age_ans(valeur) -> str | None:
    """« 25 ans » : "25" ; un nombre seul n'en est pas un."""
    trouve = re.fullmatch(r"(\d+) ans", _simple(valeur)) if isinstance(valeur, str) else None
    return trouve.group(1) if trouve else None


def _sexe_du_bloc(marques: dict[int, str], ligne: int) -> str:
    """Le sexe de l'étiquette la plus proche au-dessus de ``ligne``, ou sur elle."""
    au_dessus = [marque for marque in marques if marque <= ligne]
    if not au_dessus:
        raise FeuilleIllisible(f"la ligne {ligne} n'a pas de sexe au-dessus d'elle")
    return marques[max(au_dessus)]


def _marques_de_sexe(grille: dict, colonne: int = 1) -> dict[int, str]:
    """Les lignes dont la case de ``colonne`` n'est qu'un sexe."""
    return {l: SEXES[_texte(v)] for (l, c), v in grille.items()
            if c == colonne and isinstance(v, str) and _texte(v) in SEXES}


def _colonnes_par_grandeur_et_sexe(grille: dict, grandeurs: dict[int, tuple],
                                   premiere: int) -> dict[int, tuple]:
    """Des grandeurs côte à côte, chacune sur ses colonnes de sexe : une
    colonne est de la grandeur dont l'en-tête est à sa gauche, au plus près,
    et du sexe que nomme son propre en-tête. Chaque grandeur a ses trois
    sexes."""
    debuts = sorted(grandeurs)
    colonnes = {}
    for (ligne, colonne), valeur in grille.items():
        if ligne < premiere and colonne >= debuts[0] and isinstance(valeur, str):
            sexe = _cle(valeur, SEXES_EN_TETE)
            if sexe:
                colonnes[colonne] = (*grandeurs[max(d for d in debuts if d <= colonne)], sexe)
    for grandeur in grandeurs.values():
        sexes = sorted(cle[-1] for cle in colonnes.values() if cle[:-1] == grandeur)
        if sexes != sorted(SEXES.values()):
            raise FeuilleIllisible(f"{grandeur} : les sexes {sexes}")
    return colonnes


def lire_debut_de_carriere(grille: dict) -> dict[tuple, float]:
    """Fiche 12, graphique 1 : par génération et par sexe, les trimestres
    validés à 30 ans, qui vont aux cumuls, l'âge de la première année
    complète validée et la part des affiliés qui n'en ont validé aucune."""
    _verifier_titre(grille, "Graphique 1. Nombre moyen de trimestres validés à 30 ans")
    lignes = _lignes(grille)
    grandeurs = {
        _premiere_colonne(grille, "Nombre moyen de trimestres validés à 30 ans"):
            ("cumul", "30", "trimestres"),
        _premiere_colonne(grille, "Âge moyen de première validation d'une année complète"):
            ("debut_de_carriere", "ensemble", "age_premiere_annee_complete"),
        _premiere_colonne(grille, "Part d'affiliés n'ayant pas validé d'année complète"):
            ("debut_de_carriere", "ensemble", "part_sans_annee_complete_pct"),
    }
    colonnes = _colonnes_par_grandeur_et_sexe(grille, grandeurs, min(lignes, default=0))
    return {(generation, champ, groupe, "toutes", sexe, indicateur): valeur
            for (generation, (champ, groupe, indicateur, sexe)), valeur
            in _cases(grille, lignes, colonnes).items()}


#: Fiche 12, graphique 2 : « À 49 ans » est un cumul, les autres des rythmes.
TRANCHES_RYTHME = (
    ("Entre 20 et 24 ans", ("rythme", "20_24")), ("Entre 25 et 29 ans", ("rythme", "25_29")),
    ("Entre 30 et 34 ans", ("rythme", "30_34")), ("Entre 35 et 39 ans", ("rythme", "35_39")),
    ("Entre 40 et 44 ans", ("rythme", "40_44")), ("Entre 45 et 49 ans", ("rythme", "45_49")),
    ("Entre 50 et 54 ans", ("rythme", "50_54")), ("Entre 55 et 59 ans", ("rythme", "55_59")),
    ("Entre 40 et 49 ans", ("rythme", "40_49")), ("Entre 30 et 49 ans", ("rythme", "30_49")),
    ("Entre 50 et 59 ans", ("rythme", "50_59")), ("À 49 ans", ("cumul", "49")),
)


def lire_rythme_validation(grille: dict) -> dict[tuple, float]:
    """Fiche 12, graphique 2 : les trimestres validés par tranche d'âge et leur
    cumul à 49 ans, par génération, dans le bloc de chaque sexe, qui a sa
    colonne de générations ; l'étiquette du sexe peut être décalée dans son
    bloc. L'écart entre les femmes et les hommes, qui suit, ne se lit pas."""
    _verifier_titre(grille, "Graphique 2. Rythmes moyens de validation des trimestres")
    ecart = _premiere_colonne(grille, "Écart entre les femmes et les hommes")
    blocs = sorted({c for (_, c), v in grille.items() if c < ecart and annee(v)})
    lu = {}
    for rang, debut in enumerate(blocs):
        fin = blocs[rang + 1] if rang + 1 < len(blocs) else ecart
        lignes = {l: str(annee(v)) for (l, c), v in grille.items() if c == debut and annee(v)}
        premiere = min(lignes)
        sexes = {cle for (l, c), v in grille.items()
                 if l < premiere and debut <= c < fin and (cle := _cle(v, SEXES_EN_TETE))}
        if len(sexes) != 1:
            raise FeuilleIllisible(f"fiche 12, graphique 2 : le bloc de la colonne {debut} "
                                   f"a pour sexes {sorted(sexes)}")
        sexe = sexes.pop()
        colonnes = _exiger(_entetes(grille, TRANCHES_RYTHME, premiere, apres=debut, avant=fin),
                           {cle for _, cle in TRANCHES_RYTHME}, "fiche 12, graphique 2")
        for (generation, (champ, groupe)), valeur in _cases(grille, lignes, colonnes).items():
            lu[(generation, champ, groupe, "toutes", sexe, "trimestres")] = valeur
    if {cle[4] for cle in lu} != {"F", "H"}:
        raise FeuilleIllisible("fiche 12, graphique 2 : il faut un bloc par sexe")
    return lu


NATURES_COMPOSITION = (
    ("Trimestres cotisés", "cotises"), ("Trimestres d'AVPF", "avpf"),
    ("Trimestres de maladie", "maladie"), ("Trimestres de chômage", "chomage"),
    ("Trimestres de service national", "service_national"), ("Autres trimestres", "autres"),
    ("Nombre moyen de trimestres validés", "toutes"),
)


def lire_composition_trimestres(grille: dict) -> dict[tuple, float]:
    """Fiche 12, graphique 3 : pour la génération que le titre nomme, par sexe
    et par âge, la part de chaque nature dans les trimestres validés, et
    leur nombre moyen, qui va aux cumuls."""
    titre = "Graphique 3. Composition des trimestres validés"
    _verifier_titre(grille, titre)
    generation = _generation_nommee(grille, titre)
    marques = _marques_de_sexe(grille)
    lignes = {l: (age, _sexe_du_bloc(marques, l))
              for (l, c), v in grille.items() if c == 2 and (age := _age_ans(v))}
    colonnes = _exiger(_entetes(grille, NATURES_COMPOSITION, min(lignes, default=0), apres=2),
                       {cle for _, cle in NATURES_COMPOSITION}, "fiche 12, graphique 3")
    lu = {}
    for ((age, sexe), nature), valeur in _cases(grille, lignes, colonnes).items():
        if nature == "toutes":
            lu[(generation, "cumul", age, "toutes", sexe, "trimestres")] = valeur
        else:
            lu[(generation, "composition", age, nature, sexe, "part_pct")] = valeur
    return lu


def lire_chomage_cumule(grille: dict) -> dict[tuple, float]:
    """Fiche 12, graphique 4 : les trimestres validés au titre du chômage, de
    la préretraite, de la reconversion et de la formation, cumulés à chaque
    âge, par génération, les deux sexes ensemble."""
    _verifier_titre(grille, "Graphique 4. Durée moyenne validée au titre du chômage")
    lignes = _lignes(grille)
    premiere = min(lignes, default=0)
    colonnes = {c: age for (l, c), v in grille.items()
                if l < premiere and c > 1 and (age := _age_ans(v))}
    return {(generation, "cumul", age, "chomage", "ensemble", "trimestres"): valeur
            for (generation, age), valeur in _cases(grille, lignes, colonnes).items()}


NATURES_ANNEE = (
    ("Trimestres cotisés au titre de l'emploi", "cotises"), ("AVPF", "avpf"),
    ("Chômage, formation", "chomage"), ("Maladie, maternité", "maladie"),
)


def lire_validations_de_l_annee(grille: dict) -> dict[tuple, float]:
    """Fiche 12, graphique 5 : les trimestres validés de chaque nature au cours
    de l'année civile de chaque âge, par sexe, l'une des deux années que le
    titre nomme. L'échantillon ne suit que des générations paires : un âge
    est celui qu'avait, l'une de ces deux années, la génération paire."""
    titre = "Graphique 5. Nombre moyen et nature des trimestres validés selon"
    annees = [int(a) for a in re.findall(r"\b((?:19|20)\d\d)\b", _titre(grille, titre))]
    if len(annees) != 2 or annees[1] != annees[0] + 1:
        raise FeuilleIllisible(f"fiche 12, graphique 5 : le titre nomme les années {annees}")
    debuts = _marques_de_sexe_en_colonnes(grille)
    bornes = sorted(debuts)
    lu = {}
    for rang, debut in enumerate(bornes):
        fin = bornes[rang + 1] if rang + 1 < len(bornes) else 10 ** 6
        lignes = {l: str(age) for (l, c), v in grille.items()
                  if c == debut and (age := _age(v)) is not None}
        colonnes = _exiger(_entetes(grille, NATURES_ANNEE, min(lignes, default=0), apres=debut,
                                    avant=fin),
                           {cle for _, cle in NATURES_ANNEE}, "fiche 12, graphique 5")
        for (age, nature), valeur in _cases(grille, lignes, colonnes).items():
            generation = next(a - int(age) for a in annees if (a - int(age)) % 2 == 0)
            lu[(str(generation), "validations_de_l_annee", age, nature, debuts[debut],
                "trimestres")] = valeur
    return lu


def _marques_de_sexe_en_colonnes(grille: dict) -> dict[int, str]:
    """Les colonnes qu'ouvre l'étiquette « Femmes » ou « Hommes »."""
    debuts = {c: SEXES[_texte(v)] for (_, c), v in grille.items()
              if isinstance(v, str) and _texte(v) in ("Femmes", "Hommes")}
    if sorted(debuts.values()) != ["F", "H"]:
        raise FeuilleIllisible(f"il faut un bloc par sexe, non {sorted(debuts.values())}")
    return debuts


#: Fiche 21 : la situation principale sur le marché du travail.
SITUATIONS_FIN_DE_CARRIERE = (
    ("Absence", "absence"), ("AVPF", "avpf"), ("Chômage", "chomage"), ("En emploi", "emploi"),
    ("Maladie ou invalidité", "maladie_invalidite"), ("Préretraite", "preretraite"),
    ("Retraite", "retraite"), ("Cumul emploi-retraite", "cumul_emploi_retraite"),
)


def _situations_par_sexe(grille: dict, cle_de_ligne) -> dict[tuple, float]:
    """Les blocs « Femmes », « Hommes » et « Ensemble » de la fiche 21, chacun
    ouvert par son étiquette, en première colonne, puis par son en-tête de
    situations ; une ligne par génération ou par âge, que ``cle_de_ligne``
    lit dans la première colonne. {(clé de ligne, situation, sexe): part}."""
    marques = _marques_de_sexe(grille)
    entetes: dict[int, dict[int, str]] = {}
    for (l, c), v in grille.items():
        if c > 1 and (cle := _cle(v, SITUATIONS_FIN_DE_CARRIERE)):
            entetes.setdefault(l, {})[c] = cle
    attendues = {cle for _, cle in SITUATIONS_FIN_DE_CARRIERE}
    lu = {}
    for (l, c), v in sorted(grille.items()):
        if c != 1 or (cle := cle_de_ligne(v)) is None:
            continue
        au_dessus = [h for h in entetes if h < l]
        if not au_dessus:
            raise FeuilleIllisible(f"fiche 21 : la ligne {l} n'a pas d'en-tête")
        colonnes = _exiger(entetes[max(au_dessus)], attendues, "fiche 21")
        sexe = _sexe_du_bloc(marques, l)
        for (_, situation), valeur in _cases(grille, {l: cle}, colonnes).items():
            lu[(cle, situation, sexe)] = valeur
    if {sexe for *_, sexe in lu} != set(SEXES.values()):
        raise FeuilleIllisible("fiche 21 : il manque le bloc d'un sexe")
    return lu


def lire_situation_a_un_age(grille: dict) -> dict[tuple, float]:
    """Fiche 21, graphique 1 : la situation principale à l'âge que le titre
    nomme, par génération et par sexe."""
    titre = "Graphique 1. Situation principale d"
    trouve = re.search(r"\bà (\d+) ans\b", _titre(grille, titre))
    if not trouve:
        raise FeuilleIllisible("fiche 21, graphique 1 : le titre ne nomme plus d'âge")
    lu = _situations_par_sexe(grille, lambda v: str(annee(v)) if annee(v) else None)
    return {(generation, "situation_par_age", trouve.group(1), situation, sexe, "part_pct"): valeur
            for (generation, situation, sexe), valeur in lu.items()}


def lire_situations_successives(grille: dict) -> dict[tuple, float]:
    """Fiche 21, graphique 2 : la situation principale à chaque âge, de la
    génération que le titre nomme, par sexe."""
    generation = _generation_nommee(grille, "Graphique 2. Situations principales successives")
    lu = _situations_par_sexe(grille, lambda v: None if _age(v) is None else str(_age(v)))
    return {(generation, "situation_par_age", age, situation, sexe, "part_pct"): valeur
            for (age, situation, sexe), valeur in lu.items()}


GROUPES_LIQUIDATION = (
    ("Départ avant", "depart_avant_aod"), ("Départ à partir de", "depart_a_l_aad_ou_apres"),
    ("Départ à", "depart_a_l_aod"), ("Départ après", "depart_entre_aod_et_aad"),
    ("Ayant travaillé après 50 ans", "travail_apres_50_ans"),
    ("N'ayant pas travaillé après 50 ans", "sans_travail_apres_50_ans"),
)


def lire_situation_avant_liquidation(grille: dict) -> dict[tuple, float]:
    """Fiche 21, tableau 1 : la situation principale de l'année qui précède la
    liquidation, par génération et par sexe, puis, dans la dernière, selon
    l'âge de départ et le travail après 50 ans, les deux sexes ensemble. Une
    génération couvre ses lignes depuis celle de ses femmes jusqu'à celle des
    femmes de la suivante ; son étiquette est sur l'une d'elles."""
    _verifier_titre(grille, "Tableau 1. Situation principale d")
    lignes = {}
    for (l, c), v in grille.items():
        if c == 2 and isinstance(v, str):
            if _texte(v) in SEXES:
                lignes[l] = ("ensemble", SEXES[_texte(v)])
            elif groupe := _cle(v, GROUPES_LIQUIDATION):
                lignes[l] = (groupe, "ensemble")
    etiquettes = {l: trouve.group(1) for (l, c), v in grille.items()
                  if c == 1 and isinstance(v, str)
                  and (trouve := re.fullmatch(r"Génération ((?:19|20)\d\d)", _texte(v)))}
    debuts = sorted(l for l, cle in lignes.items() if cle == ("ensemble", "F"))
    if not debuts:
        raise FeuilleIllisible("fiche 21, tableau 1 : aucune ligne de femmes")
    colonnes = _exiger(_entetes(grille, SITUATIONS_FIN_DE_CARRIERE, min(lignes), apres=2),
                       {"emploi", "preretraite", "maladie_invalidite", "chomage", "absence"},
                       "fiche 21, tableau 1")
    lu = {}
    for rang, debut in enumerate(debuts):
        fin = debuts[rang + 1] if rang + 1 < len(debuts) else 10 ** 6
        generations = {g for l, g in etiquettes.items() if debut <= l < fin}
        if len(generations) != 1:
            raise FeuilleIllisible(f"fiche 21, tableau 1 : les lignes depuis la {debut} ont "
                                   f"pour générations {sorted(generations)}")
        generation = generations.pop()
        bloc = {l: cle for l, cle in lignes.items() if debut <= l < fin}
        for ((groupe, sexe), situation), valeur in _cases(grille, bloc, colonnes).items():
            lu[(generation, "situation_avant_liquidation", groupe, situation, sexe,
                "part_pct")] = valeur
    return lu


TRAJECTOIRES = (
    ("Trajectoires sans années de non-emploi", "sans_non_emploi"),
    ("Trajectoires avec années de non-emploi", "avec_non_emploi"),
    ("Trajectoires avec une seule période de non-emploi", "une_periode_non_emploi"),
    ("Emploi, puis chômage, puis retraite", "emploi_chomage_retraite"),
    ("Emploi, puis maladie ou invalidité, puis retraite", "emploi_maladie_retraite"),
    ("Emploi, puis absence, puis retraite", "emploi_absence_retraite"),
    ("Autres trajectoires", "autres_avec_non_emploi"),
    ("Trajectoires sans départ à la retraite", "sans_depart_a_67_ans"),
    ("Personnes continûment en emploi", "emploi_continu_sans_depart"),
)


def lire_trajectoires(grille: dict) -> dict[tuple, float]:
    """Fiche 21, tableau 2 : la part de chaque trajectoire à partir de 50 ans,
    par sexe, dans la génération que le titre nomme ; la ligne « Ensemble »,
    qui fait 100, ne se lit pas."""
    titre = "Tableau 2. Trajectoires les plus fréquentes"
    generation = _generation_nommee(grille, titre)
    lignes = _lignes(grille, TRAJECTOIRES)
    colonnes = _exiger(_entetes(grille, SEXES_EN_TETE, min(lignes, default=0)),
                       set(SEXES.values()), "fiche 21, tableau 2")
    return {(generation, "trajectoire", "ensemble", trajectoire, sexe, "part_pct"): valeur
            for (trajectoire, sexe), valeur in _cases(grille, lignes, colonnes).items()}


GROUPES_TRANSITIONS = (
    ("Y compris transitions entre retraite et cumul", "avec_cumul"),
    ("Hors transitions entre retraite et cumul", "hors_cumul"),
)


def lire_transitions(grille: dict) -> dict[tuple, float]:
    """Fiche 21, tableau 3 : la répartition par nombre de transitions entre 50
    et 67 ans, et leur nombre moyen, y compris ou hors celles entre retraite et
    cumul, par sexe ; la ligne « Ensemble », qui somme les parts, ne se lit
    pas."""
    generation = _generation_nommee(grille, "Tableau 3. Nombre de transitions")
    lignes = {}
    for (l, c), v in grille.items():
        if c != 1:
            continue
        plus = re.fullmatch(r"(\d+) ou plus", _simple(v))
        if isinstance(v, (int, float)) and _age(v) is not None:
            lignes[l] = (str(_age(v)), "part_pct")
        elif plus:
            lignes[l] = (f"{plus.group(1)}_plus", "part_pct")
        elif _simple(v).startswith("Nombre moyen de transitions"):
            lignes[l] = ("ensemble", "nombre_moyen")
    groupes = {_premiere_colonne(grille, libelle): (cle,) for libelle, cle in GROUPES_TRANSITIONS}
    colonnes = _colonnes_par_grandeur_et_sexe(grille, groupes, min(lignes, default=0))
    return {(generation, "transitions", groupe, modalite, sexe, indicateur): valeur
            for ((modalite, indicateur), (groupe, sexe)), valeur
            in _cases(grille, lignes, colonnes).items()}


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
        f01 = _classeur(archive, jeu, "fiche_01.xlsx")
        f03 = _classeur(archive, jeu, "fiche_03.xlsx")
        f05 = _classeur(archive, jeu, "fiche_05.xlsx")
        f12 = _classeur(archive, jeu, "fiche_12.xlsx")
        f15 = _classeur(archive, jeu, "fiche_15.xlsx")
        f16 = _classeur(archive, jeu, "fiche_16.xlsx")
        f17 = _classeur(archive, jeu, "fiche_17.xlsx")
        f21 = _classeur(archive, jeu, "fiche_21.xlsx")
        f22 = _classeur(archive, jeu, "fiche_22.xlsx")
        f23 = _classeur(archive, jeu, "fiche_23.xlsx")
        f25 = _classeur(archive, jeu, "fiche_25.xlsx")
        f27 = _classeur(archive, jeu, "fiche_27.xlsx")
    return {
        "age_conjoncturel": lire_age_conjoncturel(f15["F15_Graphique 1"]),
        "pensions_moyennes": lire_pensions_moyennes(f05["F05_Tableau 1 compl_bis"]),
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
        "rapport_emploi_retraites": lire_rapport_emploi_retraites(f01["F01_Graphique 1"]),
        "retraites_generations": [[*cle, valeur] for cle, valeur in sorted({
            **lire_polypensionnes(f01["F01_Graphique 3"]),
            **lire_age_premiere_liquidation(f16["F16_Tableau 1"], f16["F16_Graphique 5"]),
            **lire_liquidation_regime_principal(f16["F16_Tableau 2"]),
            **lire_taux_liquidation(f17["F17_Graphique 1"], f17["F17_Graphique 3"]),
            **lire_decote_surcote(f17["F17_Graphique 4"], f17["F17_Graphique 5"]),
        }.items())],
        "reversion": [[*cle, valeur] for cle, valeur in sorted(
            lire_reversion(f03["F03_Graphique 2"], f03["F03_Graphique 4"]).items())],
        "durees_validees": [[*cle, valeur] for cle, valeur in sorted(reunir(
            lire_debut_de_carriere(f12["F12_Graphique 1"]),
            lire_rythme_validation(f12["F12_Graphique 2"]),
            lire_composition_trimestres(f12["F12_Graphique 3"]),
            lire_chomage_cumule(f12["F12_Graphique 4"]),
            lire_validations_de_l_annee(f12["F12_Graphique 5"]),
        ).items())],
        "fins_de_carriere": [[*cle, valeur] for cle, valeur in sorted(reunir(
            lire_situation_a_un_age(f21["F21_Graphique 1"]),
            lire_situations_successives(f21["F21_Graphique 2"]),
            lire_situation_avant_liquidation(f21["F21_Tableau 1"]),
            lire_trajectoires(f21["F21_Tableau 2"]),
            lire_transitions(f21["F21_Tableau 3"]),
        ).items())],
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
