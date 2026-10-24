#!/usr/bin/env python3
"""L'âge moyen de départ à la retraite par génération, et les départs d'avant l'âge légal, du COR en juin 2026.

    python scripts/fetch/cor_age_depart_generations.py
    python scripts/fetch/cor_age_depart_generations.py --fichier Données_RA2026_P4_0.xlsx

POURQUOI CE TÉMOIN. La grille de la page Coût fait partir chacun de ses cas
types au taux plein, à la date que le droit de sa génération lui donne
(``cout.Pensionne.departs``) ; le partage de sa couverture entre les âges tient
à l'âge où elle les fait partir (action 138, étape 3, note « les 65 ans et
plus d'après 2030 »). Le COR publie l'âge moyen de départ de chaque génération,
de 1906 à 2000 (figure 4.5) : la DREES l'observe jusqu'à la génération 1954,
dans l'EIR et Ancetre ; le COR le projette au-delà, des évolutions de
TRAJECTOiRE, sous la législation de juin 2026, la suspension de la réforme de
2023 comprise. La part de chaque génération de 1942 à 1960 déjà partie, à
chaque âge d'avant son âge légal (figure 4.7) : ce qui fait partir la France
avant le taux plein de droit commun, carrières longues et catégories actives.
Et la part des résidents de chaque âge de 50 à 70 ans déjà retraités au 31
décembre 2024 (figure 4.6) : la forme des départs autour de l'âge légal.
``tests/test_facteurs_depense.py`` y confronte la grille (``facteurs_depense.
ages_moyens_de_depart``, ``facteurs_depense.parts_parties``).

LA SOURCE. Le classeur de la partie 4 du rapport, feuilles « Fig. 4.5 »,
« Fig 4.6 » et « Fig. 4.7 ». La figure 4.5 porte deux séries, l'âge observé et
l'âge projeté, qui se recouvrent à la génération 1954 ; la figure 4.6, les
retraités et les nouveaux retraités de 2024, dont le témoin garde les
premiers, par sexe ; la figure 4.7, les âges de 55 à 59 ans de chaque
génération, 60 ans depuis celle de 1953 et 61 ans depuis celle de 1955 :
ceux d'avant son âge légal, que le rapport arrondit à 60 ans jusqu'à la
génération née le 30 juin 1951, 61 ans pour celle de 1953 et 62 depuis celle
de 1955. Le chapitre 2 du
rapport écrit que l'âge « se stabiliserait autour de 64,6 ans à partir des
générations nées dans les années 1975 » (p. 215), le sommaire du classeur
64,5 : la moyenne des générations 1975 à 2000 fait 64,53. Le champ de la
figure 4.5 est, dans le classeur, celui des retraités résidant en France ; dans
le rapport, en France et à l'étranger ; dans les deux, corrigé pour compter
toutes les personnes qui ont liquidé un droit, mortes avant 66 ans comprises.

Le témoin est versionné : les tests le relisent sans réseau. ``--fichier``
lit le classeur déjà téléchargé.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
URL = ("https://www.cor-retraites.fr/sites/default/files/2026-06/"
       "Donn%C3%A9es_RA2026_P4_0.xlsx")
SORTIE = RACINE / "tests" / "temoins" / "cor_age_depart_generations_2026.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
FEUILLE_AGES = "Fig. 4.5"
FEUILLE_AVANT = "Fig. 4.7"
FEUILLE_PAR_AGE = "Fig 4.6"
#: Les trois lignes du premier bloc de la figure 4.6.
SEXES: tuple[str, ...] = ("ensemble", "femmes", "hommes")

#: Les deux séries de la figure 4.5, reconnues à leur intitulé, sans accents
#: ni casse.
SERIES: tuple[tuple[str, str], ...] = (
    ("observe", "age moyen observe"),
    ("projete", "age moyen projete"),
)


def _texte(valeur) -> str:
    texte = unicodedata.normalize("NFD", str(valeur))
    return "".join(c for c in texte if unicodedata.category(c) != "Mn").lower().strip()


def _lignes(grille: dict) -> dict[int, dict[int, object]]:
    lignes: dict[int, dict[int, object]] = {}
    for (ligne, colonne), valeur in grille.items():
        lignes.setdefault(ligne, {})[colonne] = valeur
    return lignes


def _annee(valeur) -> int | None:
    """Une génération, que la figure 4.5 écrit en texte et la figure 4.7 en
    nombre ; ``None`` pour ce qui n'en est pas une."""
    if isinstance(valeur, str):
        valeur = float(valeur) if valeur.strip().isdigit() else None
    if isinstance(valeur, float) and valeur.is_integer() and 1900 < valeur < 2100:
        return int(valeur)
    return None


def _generations(lignes: dict[int, dict[int, object]]) -> tuple[int, dict[int, int]]:
    """La ligne des générations, la première dont toutes les cellules sont des
    années, et la génération de chacune de ses colonnes."""
    for numero in sorted(lignes):
        annees = {c: _annee(v) for c, v in lignes[numero].items()}
        if annees and all(annee is not None for annee in annees.values()):
            return numero, annees
    raise ValueError("aucune ligne de générations")


def _textes(cellules: dict[int, object]) -> list[str]:
    return [_texte(v) for _c, v in sorted(cellules.items()) if isinstance(v, str)]


def lire_ages(grille: dict) -> dict[str, dict[str, float]]:
    """L'âge moyen de départ, observé et projeté, par génération."""
    lignes = _lignes(grille)
    numero, generations = _generations(lignes)
    resultat: dict[str, dict[str, float]] = {}
    for autre in sorted(lignes):
        if autre <= numero:
            continue
        cellules = lignes[autre]
        for cle, debut in SERIES:
            if any(t.startswith(debut) for t in _textes(cellules)):
                resultat[cle] = {str(generations[c]): v for c, v in cellules.items()
                                 if c in generations and isinstance(v, float)}
    if set(resultat) != {cle for cle, _ in SERIES}:
        raise ValueError(f"figure 4.5 : séries trouvées {sorted(resultat)}")
    return resultat


def lire_avant_l_age_legal(grille: dict) -> dict[str, dict[str, float]]:
    """La part de chaque génération déjà partie au 31 décembre de l'année de
    chaque âge, par âge (« 55 »… « 61 »), puis par génération."""
    lignes = _lignes(grille)
    numero, generations = _generations(lignes)
    resultat: dict[str, dict[str, float]] = {}
    for autre in sorted(lignes):
        if autre <= numero:
            continue
        cellules = lignes[autre]
        textes = _textes(cellules)
        if len(textes) != 1 or not textes[0].endswith(" ans") or not textes[0][:-4].isdigit():
            continue
        resultat[textes[0][:-4]] = {str(generations[c]): v for c, v in cellules.items()
                                    if c in generations and isinstance(v, float)}
    if sorted(resultat) != [str(age) for age in range(55, 62)]:
        raise ValueError(f"figure 4.7 : âges trouvés {sorted(resultat)}")
    return resultat


def lire_par_age(grille: dict) -> dict[str, dict[str, float]]:
    """La part des résidents de chaque âge déjà retraités au 31 décembre
    2024, par sexe puis par âge : le premier bloc de la figure 4.6, avant
    celui des nouveaux retraités."""
    lignes = _lignes(grille)
    ages: dict[int, int] = {}
    resultat: dict[str, dict[str, float]] = {}
    for numero in sorted(lignes):
        cellules = lignes[numero]
        textes = _textes(cellules)
        if any(t.startswith("taux de nouveaux retraites") for t in textes):
            break
        nombres = {c: v for c, v in cellules.items() if isinstance(v, float)}
        if (not ages and nombres and not textes
                and all(v.is_integer() and 40 <= v <= 80 for v in nombres.values())):
            ages = {c: int(v) for c, v in nombres.items()}
        elif ages and len(textes) == 1 and textes[0] in SEXES:
            resultat[textes[0]] = {str(ages[c]): v for c, v in nombres.items() if c in ages}
    if set(resultat) != set(SEXES):
        raise ValueError(f"figure 4.6 : lignes trouvées {sorted(resultat)}")
    return resultat


def controler(temoin: dict) -> list[str]:
    """Ce que le chapitre 2 de la partie 4 imprime, à l'arrondi près : 64,2
    ans pour la génération 1906, 60,9 pour celle de 1932, autour de 64,6 depuis
    les générations des années 1975 (p. 215) ; 15 % de la génération 1949
    partie à 57 ans, 22 % à 59 ans, son pic, et 30 % environ de celle de 1953
    avant 61 ans (p. 219-220) ; 48,1 % des résidents de 62 ans retraités au
    31 décembre 2024 (p. 218)."""
    ages, partis = temoin["age_moyen_de_depart"], temoin["retraites_avant_l_age_legal"]
    attendus = [
        (ages["observe"]["1906"], 64.2, 0.05),
        (ages["observe"]["1932"], 60.9, 0.05),
        (partis["57"]["1949"], 0.15, 0.005),
        (partis["59"]["1949"], 0.22, 0.005),
        (partis["60"]["1953"], 0.30, 0.01),
        (temoin["retraites_par_age_en_2024"]["ensemble"]["62"], 0.481, 0.0005),
    ]
    attendus += [(ages["projete"][str(generation)], 64.6, 0.2)
                 for generation in range(1975, 2001)]
    return [f"{lu} au lieu de {imprime}" for lu, imprime, tolerance in attendus
            if abs(lu - imprime) > tolerance]


def _classeur(fichier: Path | None) -> bytes:
    if fichier is not None:
        return fichier.read_bytes()
    requete = urllib.request.Request(URL, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=120) as reponse:
        return reponse.read()


def _note(grille: dict, debut: str) -> str:
    """La note de la figure qui commence par ``debut`` (« Champ », « Source »)."""
    for (_ligne, _colonne), valeur in sorted(grille.items()):
        if isinstance(valeur, str) and _texte(valeur).startswith(debut):
            return " ".join(valeur.replace("\xa0", " ").split())
    raise ValueError(f"note introuvable : {debut}")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--fichier", type=Path, help="le classeur déjà téléchargé")
    arguments = analyseur.parse_args(argv)

    grilles = feuilles(_classeur(arguments.fichier),
                       (FEUILLE_AGES, FEUILLE_AVANT, FEUILLE_PAR_AGE))
    temoin = {
        "source": {
            "editeur": "Conseil d'orientation des retraites",
            "reference": ("Rapport annuel de juin 2026, figures 4.5, 4.6 et 4.7 "
                          "(Données_RA2026_P4_0.xlsx, feuilles « Fig. 4.5 », « Fig 4.6 » "
                          "et « Fig. 4.7 »)"),
            "url": URL,
            "lu_le": date.today().isoformat(),
        },
        "champs": {
            "age_moyen_de_depart": _note(grilles[FEUILLE_AGES], "champ"),
            "retraites_avant_l_age_legal": _note(grilles[FEUILLE_AVANT], "champ"),
            "retraites_par_age_en_2024": _note(grilles[FEUILLE_PAR_AGE], "champ"),
        },
        "producteurs": {
            "age_moyen_de_depart": _note(grilles[FEUILLE_AGES], "source"),
            "retraites_avant_l_age_legal": _note(grilles[FEUILLE_AVANT], "source"),
            "retraites_par_age_en_2024": _note(grilles[FEUILLE_PAR_AGE], "source"),
        },
        "unites": {
            "age_moyen_de_depart": "années, par génération",
            "retraites_avant_l_age_legal": ("part de la génération ayant liquidé un premier droit "
                                            "direct au 31 décembre de l'année de chaque âge"),
            "retraites_par_age_en_2024": ("part des résidents de chaque âge au 31 décembre "
                                          "2024 ayant liquidé un droit direct, par sexe"),
        },
        "age_moyen_de_depart": lire_ages(grilles[FEUILLE_AGES]),
        "retraites_avant_l_age_legal": lire_avant_l_age_legal(grilles[FEUILLE_AVANT]),
        "retraites_par_age_en_2024": lire_par_age(grilles[FEUILLE_PAR_AGE]),
    }
    ecarts = controler(temoin)
    if ecarts:
        print("Le classeur ne redonne pas le rapport : " + " ; ".join(ecarts), file=sys.stderr)
        return 1
    SORTIE.write_text(json.dumps(temoin, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} écrit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
