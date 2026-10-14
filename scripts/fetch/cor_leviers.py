#!/usr/bin/env python3
"""Les trois leviers qui équilibreraient le système de retraite, chiffrés par le COR en juin 2026.

    python scripts/fetch/cor_leviers.py
    python scripts/fetch/cor_leviers.py --fichier Données_RA2026_P2.xlsx

POURQUOI CE TÉMOIN. Le rapport annuel du COR chiffre, chaque année jusqu'en
2070, ce que chacun des trois leviers devrait faire, seul, pour que le système
tombe juste — la pension moyenne relative, l'âge effectif moyen de départ, le
taux de prélèvement global (figure 2.24) —, et ce qu'un ajustement immédiat
de la masse des pensions (« pension gap ») ou du taux de prélèvement (« tax
gap ») devrait être pour l'équilibrer en moyenne jusqu'en 2030, 2045, 2050 ou
2070 (tableau 2.11). Le dépôt chiffre les mêmes leviers de sa trajectoire
(``src/retraite_notionnelle/leviers.py``, action 138, étape 3), et
``tests/test_leviers.py`` s'y confronte : le COR n'écrit pas comment il passe
d'un manque à un âge, et ses séries permettent de le retrouver.

LA SOURCE. Le classeur de la partie 2 du rapport, feuilles « Fig 2.24 » et
« Tab 2.11 ». La figure porte, pour chaque levier, la trajectoire spontanée
(« Sc. Ref ») et le niveau qui équilibre l'année, de 2024 à 2070, sans
arrondi ; le tableau, les quatre horizons. Le titre du tableau dans le
classeur est celui du rapport de 2025, ses notes aussi (une productivité de
1,0 %) : ses valeurs sont celles que le rapport de 2026 imprime (p. 126),
sous la référence de 2026 — une productivité de 0,7 %.

Le témoin est versionné : les tests le relisent sans réseau. ``--fichier``
lit le classeur déjà téléchargé.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
URL = ("https://www.cor-retraites.fr/sites/default/files/2026-06/"
       "Donn%C3%A9es_RA2026_P2.xlsx")
SORTIE = RACINE / "tests" / "temoins" / "cor_leviers_2026.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
FEUILLE_FIGURE = "Fig 2.24"
FEUILLE_TABLEAU = "Tab 2.11"

#: Les trois blocs de la figure, reconnus au début de leur intitulé, sans
#: accents ni casse, numéro de sous-figure retiré.
LEVIERS: tuple[tuple[str, str], ...] = (
    ("pension_relative", "evolution de la pension moyenne relative"),
    ("age", "age effectif moyen de depart"),
    ("taux_prelevement", "taux de prelevement global"),
)

#: Les deux lignes du tableau, et leurs horizons, reconnus à l'année.
LIGNES_TABLEAU: tuple[tuple[str, str], ...] = (
    ("pension_gap", "masse de pension"),
    ("tax_gap", "taux de prelevement"),
)


def _texte(valeur) -> str:
    texte = unicodedata.normalize("NFD", str(valeur))
    return "".join(c for c in texte if unicodedata.category(c) != "Mn").lower().strip()


def _lignes(grille: dict) -> dict[int, dict[int, object]]:
    lignes: dict[int, dict[int, object]] = {}
    for (ligne, colonne), valeur in grille.items():
        lignes.setdefault(ligne, {})[colonne] = valeur
    return lignes


def lire_figure(grille: dict) -> dict[str, dict[str, dict[str, float]]]:
    """Chaque levier : sa trajectoire spontanée et son niveau d'équilibre,
    par année. La ligne des années est la première qui en porte."""
    lignes = _lignes(grille)
    annees: dict[int, int] = {}
    resultat: dict[str, dict[str, dict[str, float]]] = {}
    courant = None
    for numero in sorted(lignes):
        cellules = lignes[numero]
        nombres = {c: v for c, v in cellules.items() if isinstance(v, float)}
        if not annees and nombres and all(1990 < v < 2100 for v in nombres.values()):
            annees = {c: int(v) for c, v in nombres.items()}
            continue
        textes = [_texte(v) for c, v in sorted(cellules.items()) if isinstance(v, str)]
        for cle, debut in LEVIERS:
            if any(debut in t[:80] for t in textes):
                courant = cle
        if not annees or courant is None or not textes:
            continue
        if "sc. ref" in textes or "sc ref" in textes:
            serie = "spontane"
        elif any(t.startswith("niveau pour assurer") for t in textes):
            serie = "equilibre"
        else:
            continue
        resultat.setdefault(courant, {})[serie] = {
            str(annees[c]): v for c, v in nombres.items() if c in annees}
        if serie == "equilibre":
            courant = None
    manquants = [cle for cle, _ in LEVIERS
                 if set(resultat.get(cle, {})) != {"spontane", "equilibre"}]
    if manquants:
        raise ValueError(f"figure 2.24 : leviers introuvables {manquants}")
    return resultat


def lire_tableau(grille: dict) -> dict[str, dict[str, float]]:
    """Le pension gap, en fraction des prestations, et le tax gap, en points
    du revenu d'activité, à chaque horizon."""
    lignes = _lignes(grille)
    horizons: dict[int, int] = {}
    resultat: dict[str, dict[str, float]] = {}
    for numero in sorted(lignes):
        cellules = lignes[numero]
        if not horizons:
            for colonne, valeur in cellules.items():
                trouve = (re.search(r"prochaines annees \(\D*(\d{4})\)", _texte(valeur))
                          if isinstance(valeur, str) else None)
                if trouve:
                    horizons[colonne] = int(trouve.group(1))
            continue
        libelle = " ".join(_texte(v) for v in cellules.values() if isinstance(v, str))
        for cle, debut in LIGNES_TABLEAU:
            if libelle.startswith(debut):
                resultat[cle] = {str(horizons[c]): v for c, v in cellules.items()
                                 if c in horizons and isinstance(v, float)}
    if set(resultat) != {cle for cle, _ in LIGNES_TABLEAU}:
        raise ValueError(f"tableau 2.11 : lignes trouvées {sorted(resultat)}")
    return resultat


def controler(temoin: dict) -> list[str]:
    """Ce que le rapport imprime, à l'arrondi près : les leviers de 2070
    (p. 124) et les quatre horizons (tableau 2.11)."""
    leviers, gaps = temoin["leviers"], temoin["ecarts_sur_horizon"]
    attendus = (
        (leviers["age"]["equilibre"]["2070"], 67.6, 0.05),
        (leviers["age"]["spontane"]["2070"], 64.6, 0.05),
        (leviers["pension_relative"]["spontane"]["2070"], 0.453, 0.0005),
        (leviers["pension_relative"]["equilibre"]["2070"], 0.379, 0.0005),
        (leviers["taux_prelevement"]["equilibre"]["2070"], 0.356, 0.0005),
        (gaps["pension_gap"]["2070"], -0.086, 0.0005),
        (gaps["tax_gap"]["2030"], 0.4, 0.05),
        (gaps["tax_gap"]["2070"], 2.8, 0.05),
    )
    return [f"{lu} au lieu de {imprime}" for lu, imprime, tolerance in attendus
            if abs(lu - imprime) > tolerance]


def _classeur(fichier: Path | None) -> bytes:
    if fichier is not None:
        return fichier.read_bytes()
    requete = urllib.request.Request(URL, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=120) as reponse:
        return reponse.read()


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--fichier", type=Path, help="le classeur déjà téléchargé")
    arguments = analyseur.parse_args(argv)

    grilles = feuilles(_classeur(arguments.fichier), (FEUILLE_FIGURE, FEUILLE_TABLEAU))
    temoin = {
        "source": {
            "editeur": "Conseil d'orientation des retraites",
            "reference": ("Rapport annuel de juin 2026, figure 2.24 et tableau 2.11 "
                          "(Données_RA2026_P2.xlsx, feuilles « Fig 2.24 » et « Tab 2.11 »)"),
            "url": URL,
            "lu_le": date.today().isoformat(),
        },
        "unites": {
            "pension_relative": "fraction du revenu d'activité moyen brut",
            "age": "années",
            "taux_prelevement": "fraction des revenus d'activité",
            "pension_gap": "fraction de la masse des pensions",
            "tax_gap": "points de pour cent du revenu d'activité",
        },
        "leviers": lire_figure(grilles[FEUILLE_FIGURE]),
        "ecarts_sur_horizon": lire_tableau(grilles[FEUILLE_TABLEAU]),
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
