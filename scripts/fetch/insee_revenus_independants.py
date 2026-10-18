#!/usr/bin/env python3
"""Récupération des revenus des non-salariés et de la pension des anciens
non-salariés auprès de l'INSEE.

    python scripts/fetch/insee_revenus_independants.py

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
La dispersion des revenus des indépendants. La population de la page Coût
(action 136, étape 6 ; action 138, étape 14) donnait à l'artisan celle des
salaires de son sexe, en équivalent temps plein : aucun artisan n'y touchait le
minimum contributif. Le neuvième décile du revenu des hommes non salariés vaut
15,8 fois le premier en 2022 ; celui du salaire des hommes du privé à temps
complet, 3,3. Et de quoi la juger : la pension des anciens artisans et
commerçants.

LES TROIS FICHES
----------------
« Emploi et revenus des indépendants », Insee Références, édition 2025 (paru
le 21 mai 2025), trois fiches dont chacune sert son classeur :

``sexe``       la fiche 1.6, « Emploi et revenus selon le sexe » : figure 4,
               la distribution des revenus mensuels des non-salariés
               classiques par sexe en 2022 — la part des revenus nuls ou
               déficitaires, puis les déciles et quartiles des revenus
               positifs, que les rapports Q3/Q1 et D9/D1 publiés contrôlent ;
               figure 1, leur revenu moyen, revenus nuls compris ;
``secteurs``   la fiche 1.3, « Disparités de revenus des non-salariés
               classiques » : figure 1, les mêmes quantiles par secteur, et le
               99e centile, que la fiche par sexe ne donne pas ;
``pensions``   la fiche 1.11, « Pensions de retraite des non-salariés » :
               figure 1, la pension de droit direct tous régimes, fin 2020,
               des retraités résidant en France selon leur régime principal —
               les artisans et commerçants, les exploitants agricoles, les
               professions libérales —, de l'EIR de la DREES.

Le champ des revenus : la France hors Mayotte, les non-salariés en activité au
31 décembre 2022, hors micro-entrepreneurs, hors agriculture, hors taxés
d'office. Le revenu d'activité est le bénéfice net des cotisations sociales
payées dans l'année, l'assiette des cotisations personnelles ; il est
« annualisé », ramené à une année entière d'affiliation, et nul en cas de
déficit. L'ensemble de la fiche par sexe est celui de la fiche par secteur : le
récupérateur le vérifie avant de rien écrire.

Les classeurs sont gardés dans ``data/brut/``, à côté du fichier produit,
``data/brut/insee_revenus_independants.json`` : il n'est pas lu par le modèle,
seulement par ``scripts/verifier_donnees.py``.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_xlsx import feuilles  # noqa: E402

ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
BRUT = Path("data/brut")
SORTIE = BRUT / "insee_revenus_independants.json"

#: Les trois classeurs : nom local, adresse, page qui les sert.
CLASSEURS = {
    "sexe": ("insee_eri2025_revenus_sexe.xlsx",
             "https://www.insee.fr/fr/statistiques/fichier/8376549/ERI2025-F6.xlsx",
             "https://www.insee.fr/fr/statistiques/8376549"),
    "secteurs": ("insee_eri2025_disparites_revenus.xlsx",
                 "https://www.insee.fr/fr/statistiques/fichier/8376543/ERI2025-F3.xlsx",
                 "https://www.insee.fr/fr/statistiques/8376543"),
    "pensions": ("insee_eri2025_pensions_non_salaries.xlsx",
                 "https://www.insee.fr/fr/statistiques/fichier/8376559/ERI2025-F11.xlsx",
                 "https://www.insee.fr/fr/statistiques/8376559"),
}

#: L'année des revenus, et celle des pensions.
ANNEE_REVENUS = 2022
ANNEE_PENSIONS = 2020

#: Les lignes de la figure 4 de la fiche 1.6 : le sexe.
SEXES = {"Femmes": "F", "Hommes": "H", "Ensemble des non-salariés classiques": "ensemble"}

#: Les secteurs de la figure 1 de la fiche 1.3, sous le nom que le dépôt leur
#: donne.
SECTEURS = {
    "Industrie (hors artisanat commercial)": "industrie",
    "Construction": "construction",
    "Commerce et artisanat commercial": "commerce",
    "Transports et entreposage": "transports",
    "Services aux entreprises et services mixtes": "services_entreprises",
    "Services aux particuliers": "services_particuliers",
    "Santé et action sociale": "sante",
    "Ensemble": "ensemble",
}

#: Les régimes principaux de la figure 1 de la fiche 1.11 ; chacun est suivi de
#: ses femmes, puis de ses hommes.
REGIMES = {
    "Artisans et commerçants": "artisans_commercants",
    "Exploitants agricoles": "exploitants_agricoles",
    "Professions libérales": "professions_liberales",
    "Ensemble des non-salariés": "non_salaries",
    "Ensemble des retraités": "ensemble",
}

#: Les trois régimes de non-salariés, dont l'ensemble fait la somme.
NON_SALARIES = ("artisans_commercants", "exploitants_agricoles", "professions_liberales")

QUANTILES = ("d1", "q1", "mediane", "q3", "d9")

#: Un rapport publié l'est au dixième, sur des quantiles arrondis à la dizaine
#: d'euros : il peut s'écarter du rapport des quantiles d'un vingtième, plus un
#: centième de lui-même. Une colonne décalée l'écarte bien davantage.
ECART_RAPPORT = 0.05
ECART_RAPPORT_RELATIF = 0.01

#: Les effectifs sont arrondis à la dizaine de milliers : les femmes et les
#: hommes font celui de leur régime à une dizaine près, et les trois régimes de
#: non-salariés celui de leur ensemble à quinze près.
ECART_EFFECTIFS = 10.0
ECART_SOMME_REGIMES = 15.0


def _libelle(texte: str) -> str:
    """Un libellé sans espace insécable, sans renvoi de note, sans espace en trop."""
    return " ".join(texte.replace("\xa0", " ").rstrip("0123456789¹²³ ").split())


def _lignes(grille: dict[tuple[int, int], float | str]) -> list[list[float | str]]:
    rangs = sorted({ligne for ligne, _ in grille})
    return [[grille[(r, c)] for c in sorted(c for l, c in grille if l == r)] for r in rangs]


def _nombres(cellules: list, compte: int) -> list[float] | None:
    """Les ``compte`` nombres qui suivent le libellé d'une ligne, ou ``None``."""
    valeurs = cellules[1:]
    if len(valeurs) != compte or not all(isinstance(v, float) for v in valeurs):
        return None
    return valeurs


def _controler_rapport(nom: str, rapport: str, calcule: float, publie: float) -> None:
    if abs(calcule - publie) > ECART_RAPPORT + ECART_RAPPORT_RELATIF * publie:
        raise ValueError(f"{nom} : le rapport {rapport} publié vaut {publie}, ses "
                         f"quantiles en font {calcule:.2f}")


def _controler_croissance(nom: str, quantiles: list[float]) -> None:
    if any(b <= a for a, b in zip(quantiles, quantiles[1:])):
        raise ValueError(f"{nom} : les quantiles ne croissent pas ({quantiles})")


def lire_sexe(grille: dict) -> dict[str, float]:
    """La figure 4 de la fiche 1.6 : ``{ensemble|sexe|indicateur: valeur}``,
    la part des revenus nuls ou déficitaires en pour cent, les quantiles des
    revenus positifs en euros par mois."""
    serie: dict[str, float] = {}
    for cellules in _lignes(grille):
        if not cellules or not isinstance(cellules[0], str):
            continue
        sexe = SEXES.get(_libelle(cellules[0]))
        valeurs = _nombres(cellules, 8) if sexe else None
        if valeurs is None:
            continue
        part, *quantiles, inter_quartile, inter_decile = valeurs
        nom = f"figure 4, {cellules[0]}"
        _controler_croissance(nom, quantiles)
        d1, q1, _, q3, d9 = quantiles
        _controler_rapport(nom, "Q3/Q1", q3 / q1, inter_quartile)
        _controler_rapport(nom, "D9/D1", d9 / d1, inter_decile)
        serie[f"ensemble|{sexe}|part_nuls"] = part
        for code, valeur in zip(QUANTILES, quantiles):
            serie[f"ensemble|{sexe}|{code}"] = valeur
    manquants = sorted(set(SEXES.values()) - {cle.split("|")[1] for cle in serie})
    if manquants:
        raise ValueError(f"figure 4 : lignes introuvables {manquants}")
    return serie


def lire_moyennes(grille: dict) -> dict[str, float]:
    """La première ligne de la figure 1 de la fiche 1.6, celle des non-salariés
    classiques : leur effectif, en milliers, et le revenu moyen de chaque sexe,
    revenus nuls compris, en euros par mois."""
    for cellules in _lignes(grille):
        if cellules and isinstance(cellules[0], str) \
                and _libelle(cellules[0]) == "Non-salariés classiques":
            valeurs = _nombres(cellules, 5)
            if valeurs is None:
                break
            effectif, _, femmes, hommes, _ = valeurs
            return {"ensemble|F|moyenne": femmes, "ensemble|H|moyenne": hommes,
                    "ensemble|ensemble|effectifs": effectif}
    raise ValueError("figure 1 de la fiche 1.6 : la ligne des non-salariés classiques "
                     "est introuvable")


def lire_secteurs(grille: dict) -> dict[str, float]:
    """La figure 1 de la fiche 1.3 : ``{secteur|ensemble|indicateur: valeur}``,
    l'effectif en milliers, la part des revenus nuls en pour cent, les
    quantiles et le 99e centile en euros par mois. La somme des secteurs fait
    l'effectif de l'ensemble, à l'arrondi près."""
    serie: dict[str, float] = {}
    for cellules in _lignes(grille):
        if not cellules or not isinstance(cellules[0], str):
            continue
        secteur = SECTEURS.get(_libelle(cellules[0]))
        valeurs = _nombres(cellules, 8) if secteur else None
        if valeurs is None:
            continue
        effectif, part, *quantiles = valeurs
        _controler_croissance(f"figure 1, {cellules[0]}", quantiles)
        serie[f"{secteur}|ensemble|effectifs"] = effectif
        serie[f"{secteur}|ensemble|part_nuls"] = part
        for code, valeur in zip((*QUANTILES, "c99"), quantiles):
            serie[f"{secteur}|ensemble|{code}"] = valeur
    manquants = sorted(set(SECTEURS.values()) - {cle.split("|")[0] for cle in serie})
    if manquants:
        raise ValueError(f"figure 1 de la fiche 1.3 : secteurs introuvables {manquants}")
    somme = sum(v for cle, v in serie.items()
                if cle.endswith("|effectifs") and not cle.startswith("ensemble|"))
    if abs(somme - serie["ensemble|ensemble|effectifs"]) > len(SECTEURS):
        raise ValueError(f"figure 1 de la fiche 1.3 : les secteurs comptent {somme:.0f} "
                         f"milliers, l'ensemble {serie['ensemble|ensemble|effectifs']:.0f}")
    return serie


def fusionner(*series: dict[str, float]) -> dict[str, float]:
    """Les séries des deux fiches en une : une valeur que deux fiches donnent
    doit être la même dans chacune."""
    fusion: dict[str, float] = {}
    for serie in series:
        for cle, valeur in serie.items():
            if cle in fusion and fusion[cle] != valeur:
                raise ValueError(f"{cle} : {fusion[cle]} dans une fiche, {valeur} dans "
                                 "l'autre")
            fusion[cle] = valeur
    return fusion


def lire_pensions(grille: dict) -> dict[str, float]:
    """La figure 1 de la fiche 1.11 : ``{régime|sexe|indicateur: valeur}``,
    l'effectif en milliers, la moyenne et les quartiles de la pension de droit
    direct en euros bruts par mois. Chaque régime précède ses femmes et ses
    hommes, qui font son effectif ; les trois régimes de non-salariés font celui
    de leur ensemble."""
    serie: dict[str, float] = {}
    regime = None
    for cellules in _lignes(grille):
        if not cellules or not isinstance(cellules[0], str):
            continue
        libelle = _libelle(cellules[0])
        valeurs = _nombres(cellules, 6)
        if valeurs is None:
            continue
        if libelle in REGIMES:
            regime, sexe = REGIMES[libelle], "ensemble"
        elif libelle in ("Femmes", "Hommes") and regime is not None:
            sexe = libelle[0]
        else:
            continue
        effectif, moyenne, q1, mediane, q3, inter_quartile = valeurs
        nom = f"{regime}, {sexe}"
        _controler_croissance(nom, [q1, mediane, q3])
        _controler_rapport(nom, "Q3/Q1", q3 / q1, inter_quartile)
        for code, valeur in (("effectifs", effectif), ("moyenne", moyenne), ("q1", q1),
                             ("mediane", mediane), ("q3", q3)):
            serie[f"{regime}|{sexe}|{code}"] = valeur
    for regime in REGIMES.values():
        try:
            total, femmes, hommes = (serie[f"{regime}|{s}|effectifs"]
                                     for s in ("ensemble", "F", "H"))
        except KeyError:
            raise ValueError(f"figure 1 de la fiche 1.11 : {regime} incomplet") from None
        if abs(femmes + hommes - total) > ECART_EFFECTIFS:
            raise ValueError(f"{regime} : {femmes:.0f} femmes et {hommes:.0f} hommes ne "
                             f"font pas ses {total:.0f} milliers")
    somme = sum(serie[f"{r}|ensemble|effectifs"] for r in NON_SALARIES)
    if abs(somme - serie["non_salaries|ensemble|effectifs"]) > ECART_SOMME_REGIMES:
        raise ValueError(f"non_salaries : les trois régimes comptent {somme:.0f} milliers")
    return serie


def main() -> int:
    BRUT.mkdir(parents=True, exist_ok=True)
    classeurs = {}
    for nom, (local, adresse, _) in CLASSEURS.items():
        try:
            requete = urllib.request.Request(adresse, headers=ENTETES)
            with urllib.request.urlopen(requete, timeout=120) as reponse:
                classeurs[nom] = reponse.read()
        except urllib.error.URLError as erreur:
            print(f"{adresse} : {erreur}", file=sys.stderr)
            return 1
        (BRUT / local).write_bytes(classeurs[nom])
    try:
        sexe = feuilles(classeurs["sexe"], ("Figure 1", "Figure 4"))
        revenus = fusionner(lire_sexe(sexe["Figure 4"]), lire_moyennes(sexe["Figure 1"]),
                            lire_secteurs(feuilles(classeurs["secteurs"],
                                                   ("Figure 1",))["Figure 1"]))
        pensions = lire_pensions(feuilles(classeurs["pensions"], ("Figure 1",))["Figure 1"])
    except (KeyError, ValueError) as erreur:
        print(f"classeurs de l'INSEE : {erreur} — rien n'est écrit", file=sys.stderr)
        return 1
    SORTIE.write_text(json.dumps({
        "classeurs": {nom: {"fichier": local, "adresse": adresse, "page": page}
                      for nom, (local, adresse, page) in CLASSEURS.items()},
        "recupere_le": date.today().isoformat(),
        "revenus": {"annee": ANNEE_REVENUS, "serie": dict(sorted(revenus.items()))},
        "pensions": {"annee": ANNEE_PENSIONS, "serie": dict(sorted(pensions.items()))},
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"revenus de {ANNEE_REVENUS}, médiane : femmes {revenus['ensemble|F|mediane']:.0f}, "
          f"hommes {revenus['ensemble|H|mediane']:.0f} € par mois")
    print(f"pensions de {ANNEE_PENSIONS}, anciens artisans et commerçants : médiane "
          f"{pensions['artisans_commercants|ensemble|mediane']:.0f} € par mois")
    print(f"{SORTIE} : {len(revenus)} valeurs de revenus, {len(pensions)} de pensions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
