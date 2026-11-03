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
    """Une année d'en-tête : 2004.0, « 2018 3 » (renvoi en note), « 2024(p) »."""
    if isinstance(valeur, (int, float)):
        return int(valeur) if 1900 < valeur < 2100 and valeur == int(valeur) else None
    trouve = re.match(r"\s*((?:19|20)\d\d)\b", str(valeur))
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
        f25 = _classeur(archive, jeu, "fiche_25.xlsx")
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
