#!/usr/bin/env python3
"""Les salaires forfaitaires des marins, catégorie par catégorie, lus au Journal officiel.

    python scripts/fetch/jorf_salaires_forfaitaires_marins.py

Cotisations et pensions des marins ne sont pas assises sur le salaire réel mais
sur un SALAIRE FORFAITAIRE fixé par catégorie de fonction à bord — vingt
catégories, de l'apprenti (1re) au capitaine au long cours (20e) —, dont « le
montant est fixé par arrêté des ministres chargés de la mer, de la sécurité
sociale et du budget » (décret n° 2020-649, réécrivant le décret n° 48-1709).
Ces arrêtés « portant majoration des salaires forfaitaires servant de base au
calcul des contributions des armateurs, des cotisations et des pensions des
marins » paraissent chaque année depuis 2008 avec leur tableau complet ; les
textes antérieurs de l'index (décrets de 1956 à 1961, arrêtés de 1991 à 2006)
n'en portent que le visa ou le titre.

Le script lit ces arrêtés dans l'index JORF du dépôt (``dila_index.py jorf``),
en extrait la date d'effet et les vingt montants annuels, et retient pour
chaque année la grille EN VIGUEUR AU 1ER JUILLET — les arrêtés prennent effet
tantôt au 1er janvier, tantôt au 1er avril —, convention nommée ici et nulle
part ailleurs. ``verifier_donnees.py --appliquer`` en fait
``data/reference/regimes/salaires_forfaitaires.csv``.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))

from dila_index import chemin_index  # noqa: E402

SORTIE = RACINE / "data" / "brut" / "jorf_salaires_forfaitaires_marins.json"
CATEGORIES = 20

MOIS = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5,
    "juin": 6, "juillet": 7, "août": 8, "aout": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12,
}
_EFFET = re.compile(
    r"(?:pour compter du|applicable au|à compter du)\s+(1er|\d{1,2})\s+([a-zéû]+)\s+(\d{4})",
    re.I,
)
_LIGNE = re.compile(r"(?<!\d)(\d{1,2})\s+((?:\d{1,3}\s)*\d{1,3},\d{2})\s+((?:\d{1,3}\s)*\d{1,3},\d{2})")


def _nombre(texte: str) -> float:
    return float(texte.replace(" ", "").replace("\xa0", "").replace(" ", "").replace(",", "."))


def lire_tableau(texte: str) -> dict[int, float] | None:
    """Les vingt montants annuels d'un arrêté, ou ``None`` s'il n'en porte pas."""
    texte = texte.replace(" ", " ").replace("\xa0", " ")
    # « Par jour », « par jour », « PAR JOUR » : la casse de l'en-tête change
    # avec les années, pas le tableau.
    trouve = re.search(r"par jour", texte, re.I)
    if trouve is None:
        return None
    debut = trouve.start()
    montants: dict[int, float] = {}
    attendue = 1
    for trouve in _LIGNE.finditer(texte[debut:]):
        categorie = int(trouve.group(1))
        if categorie != attendue:
            continue
        montants[categorie] = _nombre(trouve.group(2))
        attendue += 1
        if attendue > CATEGORIES:
            break
    return montants if len(montants) == CATEGORIES else None


def date_effet(texte: str, publication: str) -> date:
    trouve = _EFFET.search(texte)
    if trouve is None:
        return date.fromisoformat(publication)
    jour = 1 if trouve.group(1).lower() == "1er" else int(trouve.group(1))
    return date(int(trouve.group(3)), MOIS[trouve.group(2).lower()], jour)


def lire_arretes(db: sqlite3.Connection) -> list[dict]:
    lignes = db.execute(
        "SELECT id, date, titre, texte FROM doc WHERE nature = 'Article ARRETE' "
        "AND titre LIKE '%salaires forfaitaires%' AND titre LIKE '%marins%' "
        "ORDER BY date"
    ).fetchall()
    arretes = []
    for ident, publication, titre, texte in lignes:
        montants = lire_tableau(texte or "")
        if montants is None:
            continue
        arretes.append({
            "id": ident, "publication": publication, "titre": titre,
            "date_effet": date_effet(texte, publication).isoformat(),
            "montants": {str(c): m for c, m in sorted(montants.items())},
        })
    return arretes


def serie_annuelle(arretes: list[dict]) -> dict[str, float]:
    """La grille en vigueur au 1er juillet de chaque année : ``"annee|categorie"``."""
    serie: dict[str, float] = {}
    if not arretes:
        return serie
    par_effet = sorted(arretes, key=lambda a: a["date_effet"])
    premiere = date.fromisoformat(par_effet[0]["date_effet"]).year
    derniere = date.today().year
    for annee in range(premiere, derniere + 1):
        pivot = date(annee, 7, 1).isoformat()
        en_vigueur = [a for a in par_effet if a["date_effet"] <= pivot]
        if not en_vigueur:
            continue
        for categorie, montant in en_vigueur[-1]["montants"].items():
            serie[f"marins|{annee}|{categorie}"] = montant
    return serie


def main() -> int:
    chemin = chemin_index("jorf")
    if not chemin.exists():
        print(f"{chemin} absent — python scripts/fetch/dila_index.py jorf --recuperer",
              file=sys.stderr)
        return 1
    db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    arretes = lire_arretes(db)
    serie = serie_annuelle(arretes)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": "DILA, base JORF : arrêtés portant majoration des salaires forfaitaires "
                  "servant de base au calcul des contributions des armateurs, des "
                  "cotisations et des pensions des marins",
        "convention": "grille en vigueur au 1er juillet de l'année",
        "recupere_le": date.today().isoformat(),
        "arretes": arretes,
        "serie": serie,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    annees = sorted({cle.split("|")[1] for cle in serie})
    print(f"{len(arretes)} arrêtés lus, {len(serie)} montants écrits dans {SORTIE.relative_to(RACINE)}"
          f" ({annees[0]}-{annees[-1]})" if annees else "aucun arrêté lisible")
    for a in arretes:
        print(f"  {a['id']}  effet {a['date_effet']}  1re {a['montants']['1']:>10.2f}  20e {a['montants']['20']:>10.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
