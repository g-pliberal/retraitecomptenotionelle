#!/usr/bin/env python3
"""Le calendrier des textes contre les périodes des fiches de régime.

    python scripts/calendrier_regimes.py                 # tous les régimes
    python scripts/calendrier_regimes.py --regime sncf   # un seul, en détail
    python scripts/calendrier_regimes.py --regime sncf --motif 'ans|trimestres'
    python scripts/calendrier_regimes.py --carte         # tableau Markdown
    python scripts/calendrier_regimes.py --strict        # code 1 si un manque

Une fiche porte des PÉRIODES, chaque période un jeu de règles ; une fiche
à une seule période applique le droit de 2026 à 1950. Ce script lit, dans
l'index LEGI du dépôt (``data/brut/dila/legi.sqlite``, récupéré par
``scripts/fetch/dila_index.py legi --recuperer``), le calendrier des
versions des articles pivots de chaque régime (``regimes/pivots.yaml``) —
identifiant, dates de début et de fin de validité —, contrôle que la chaîne
des versions est jointive, et confronte ces dates aux périodes de la fiche.
Il confronte aussi le calendrier central des réformes
(``legislation/reformes.yaml``) : pour chaque couple (réforme, régime), la
fiche doit être coupée à la date d'effet, ou absorber la réforme par un
drapeau par génération, ou la déclarer non appliquée avec sa raison.

Ce qu'il ne fait pas : écrire dans ``data/reference/``. Il dit où lire ; les
paramètres se lisent ensuite version par version (``--motif`` imprime les
fenêtres utiles, ``scripts/fetch/dila_cherche.py legi --texte ID`` le texte
entier) et s'écrivent dans la fiche à la main, avec l'identifiant en note.

Deux réserves. L'index est filtré sur le champ social : une version dont le
texte ne touche plus au champ en sort, et la chaîne apparaît trouée — le
script le dit, sans conclure. Et la PREMIÈRE version d'un article n'est pas
une réforme : pour un code, c'est la date de codification (1985 pour le code
de la sécurité sociale) ; elle n'est donc pas comptée comme une coupure de
texte non reflétée.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))

from retraite_notionnelle.config import RACINE_DONNEES  # noqa: E402
from retraite_notionnelle.donnees.regimes import (  # noqa: E402
    CatalogueRegimes,
    DRAPEAUX_PAR_GENERATION,
    charger_pivots,
    charger_reformes,
    reformes_non_portees,
)

INDEX = RACINE / "data" / "brut" / "dila" / "legi.sqlite"
EN_VIGUEUR = "2999-01-01"
ANNEE_COURANTE = 2026

#: « Conformément à … ces dispositions s'appliquent … à compter du 1er
#: janvier 2013 » : la date d'effet d'une version, quand elle diffère de son
#: entrée en vigueur. Même motif que dila_legi_rci.py.
EFFET_DIFFERE = re.compile(
    r"(?:Conform[ée]ment|applicables?|s['’]appliquent).{0,400}?"
    r"compter du (?:1er |premier )?(?:janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|"
    r"septembre|octobre|novembre|d[ée]cembre) (\d{4})",
    re.S | re.I,
)


def _normaliser(num: str) -> str:
    return re.sub(r"[ .]", "", num.upper())


def _titres(texte: str) -> list[str]:
    """Les deux graphies du numéro : « Décret n°X » et « Décret n° X »."""
    variantes = {texte}
    if "n°" in texte:
        variantes.add(texte.replace("n° ", "n°", 1))
        variantes.add(texte.replace("n°", "n° ", 1).replace("n°  ", "n° "))
    return sorted(variantes)


def versions(db: sqlite3.Connection, texte: str, num: str) -> list[dict]:
    """Le calendrier des versions d'un article (ou d'un texte entier)."""
    clauses, valeurs = [], []
    titres = _titres(texte)
    clauses.append("(" + " OR ".join("titre LIKE ?" for _ in titres) + ")")
    valeurs.extend(t + "%" for t in titres)
    if num:
        clauses.append("replace(replace(upper(num), ' ', ''), '.', '') = ?")
        valeurs.append(_normaliser(num))
        clauses.append("nature LIKE 'Article %'")
    else:
        clauses.append("nature NOT LIKE 'Article %'")
    lignes = db.execute(
        "SELECT id, date, fin, nature, titre, texte FROM doc WHERE "
        + " AND ".join(clauses) + " ORDER BY date, id",
        valeurs,
    ).fetchall()
    resultat = []
    for ident, date, fin, nature, titre, corps in lignes:
        effet = EFFET_DIFFERE.search(corps or "")
        resultat.append({
            "id": ident, "date": date, "fin": fin, "nature": nature, "titre": titre,
            "texte": corps or "",
            "effet": int(effet.group(1)) if effet else int(date[:4]),
        })
    return resultat


def chaine_trouee(calendrier: list[dict]) -> list[tuple[str, str]]:
    """Les jointures manquantes : (fin de la version n, début de la n+1)."""
    trous = []
    for avant, apres in zip(calendrier, calendrier[1:]):
        if avant["fin"] != apres["date"]:
            trous.append((avant["fin"], apres["date"]))
    return trous


def coupures_non_refletees(regime, calendrier: list[dict], tolerance: int = 1) -> list[dict]:
    """Les versions qui commencent une année où aucune période ne commence.

    La première version d'un article est écartée : c'est sa codification ou
    sa création, pas une réforme. Une version en dehors de la couverture de la
    fiche l'est aussi.
    """
    debuts = {p.debut for p in regime.periodes}
    couverture_debut = min(p.debut for p in regime.periodes)
    couverture_fin = max((p.fin if p.fin is not None else ANNEE_COURANTE) for p in regime.periodes)
    manques = []
    for version in calendrier[1:]:
        annees = {int(version["date"][:4]), version["effet"]}
        if all(a < couverture_debut or a > couverture_fin for a in annees):
            continue
        if any(abs(d - a) <= tolerance for d in debuts for a in annees):
            continue
        manques.append(version)
    return manques


def fenetres(texte: str, motif: str, autour: int = 120, maximum: int = 6) -> list[str]:
    sorties = []
    for trouve in re.finditer(motif, texte, re.I):
        debut, fin = max(0, trouve.start() - autour), min(len(texte), trouve.end() + autour)
        sorties.append("…" + " ".join(texte[debut:fin].split()) + "…")
        if len(sorties) >= maximum:
            break
    return sorties


def jeux_de_regles(regime) -> tuple[int, int, int, int]:
    """(nombre de jeux, années du pire jeu, début, fin de couverture)."""
    debuts = sorted({p.debut for p in regime.periodes})
    fin_couverture = max((p.fin if p.fin is not None else ANNEE_COURANTE) for p in regime.periodes)
    bornes = debuts + [fin_couverture + 1]
    pire = max(b - a for a, b in zip(bornes, bornes[1:]))
    return len(debuts), pire, debuts[0], fin_couverture


def rapport_regime(db, regime, pivots, hors_legi, reformes, motif=None, tolerance=1) -> tuple[list[str], int, int]:
    """Le rapport d'un régime : lignes de texte, manques de texte, manques de réforme."""
    lignes = []
    nb_jeux, pire, debut, fin = jeux_de_regles(regime)
    lignes.append(f"## {regime.code} — {regime.nom}")
    lignes.append(f"couverture {debut}-{fin}, {nb_jeux} jeu(x) de règles, {pire} ans pour le plus long")
    lignes.append("périodes : " + ", ".join(
        f"{p.debut}-{p.fin if p.fin is not None else ''}"
        + ("[" + ",".join(d.split('_')[0] for d in DRAPEAUX_PAR_GENERATION if getattr(p, d, False)) + "]"
           if any(getattr(p, d, False) for d in DRAPEAUX_PAR_GENERATION) else "")
        for p in regime.periodes
    ))
    manques_texte = 0
    if regime.code in hors_legi:
        lignes.append(f"hors LEGI : {hors_legi[regime.code]}")
    for pivot in pivots.get(regime.code, ()):
        calendrier = versions(db, pivot.texte, pivot.num)
        etiquette = f"{pivot.texte} art. {pivot.num}" if pivot.num else pivot.texte
        if not calendrier:
            lignes.append(f"  ✗ {etiquette} : AUCUNE version dans l'index ({', '.join(pivot.parametres)})")
            continue
        trous = chaine_trouee(calendrier)
        lignes.append(
            f"  {etiquette} ({', '.join(pivot.parametres)}) : {len(calendrier)} version(s)"
            + (f", chaîne trouée {len(trous)} fois" if trous else ", chaîne jointive")
        )
        for version in calendrier:
            fin_texte = "en vigueur" if version["fin"] == EN_VIGUEUR else version["fin"]
            effet = f" (effet {version['effet']})" if version["effet"] != int(version["date"][:4]) else ""
            lignes.append(f"      {version['id']}  {version['date']} → {fin_texte}{effet}")
            if motif:
                for fenetre in fenetres(version["texte"], motif):
                    lignes.append(f"          {fenetre}")
        for version in coupures_non_refletees(regime, calendrier, tolerance):
            manques_texte += 1
            lignes.append(
                f"    ⚠ coupure de texte non reflétée : {version['id']} commence le "
                f"{version['date']} (effet {version['effet']}), aucune période ne commence à un an près"
            )
    manques_reformes = [m for m in reformes_non_portees(_Catalogue1(regime), reformes, tolerance)]
    for code_reforme, _, diagnostic in manques_reformes:
        lignes.append(f"    ⚠ réforme non portée : {code_reforme} — {diagnostic}")
    declarees = [r.code for r in reformes if regime.code in r.non_appliquee]
    if declarees:
        lignes.append("    déclarées non appliquées : " + ", ".join(declarees))
    return lignes, manques_texte, len(manques_reformes)


class _Catalogue1:
    """Un catalogue d'un seul régime, pour réutiliser ``reformes_non_portees``."""

    def __init__(self, regime):
        self._regime = regime

    def __contains__(self, code):
        return code == self._regime.code

    def __getitem__(self, code):
        return self._regime


def carte(db, catalogue, pivots, hors_legi, reformes, tolerance=1) -> str:
    lignes = ["| Régime | Couverture | Jeux de règles | Années par jeu | Coupures de texte non reflétées | Réformes non portées |",
              "|---|---|---|---|---|---|"]
    rangs = []
    for regime in catalogue:
        nb_jeux, pire, debut, fin = jeux_de_regles(regime)
        manques_texte = 0
        for pivot in pivots.get(regime.code, ()):
            manques_texte += len(coupures_non_refletees(regime, versions(db, pivot.texte, pivot.num), tolerance))
        manques_reformes = len(reformes_non_portees(_Catalogue1(regime), reformes, tolerance))
        rangs.append((pire, regime.code, f"{debut}-{fin}", nb_jeux, manques_texte, manques_reformes))
    for pire, code, couverture, nb_jeux, mt, mr in sorted(rangs, reverse=True):
        lignes.append(f"| `{code}` | {couverture} | {nb_jeux} | {pire} | {mt} | {mr} |")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--regime", action="append", help="code(s) de régime ; tous par défaut")
    analyseur.add_argument("--motif", help="motif dont on imprime les fenêtres dans chaque version")
    analyseur.add_argument("--carte", action="store_true", help="le tableau Markdown des jeux de règles")
    analyseur.add_argument("--strict", action="store_true", help="code de retour 1 s'il reste un manque")
    analyseur.add_argument("--tolerance", type=int, default=1, help="années de tolérance entre texte et fiche")
    analyseur.add_argument("--index", default=str(INDEX), help="chemin de legi.sqlite")
    arguments = analyseur.parse_args(argv)

    chemin = Path(arguments.index)
    if not chemin.exists():
        print(f"{chemin} absent — python scripts/fetch/dila_index.py legi --recuperer", file=sys.stderr)
        return 2
    db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    pivots, hors_legi = charger_pivots(RACINE_DONNEES)
    reformes = charger_reformes(RACINE_DONNEES)

    if arguments.carte:
        print(carte(db, catalogue, pivots, hors_legi, reformes, arguments.tolerance))
        return 0

    codes = arguments.regime or [r.code for r in catalogue]
    total_texte = total_reformes = 0
    for code in codes:
        if code not in catalogue:
            print(f"régime inconnu : {code}", file=sys.stderr)
            return 2
        lignes, mt, mr = rapport_regime(db, catalogue[code], pivots, hors_legi, reformes,
                                        arguments.motif, arguments.tolerance)
        total_texte += mt
        total_reformes += mr
        print("\n".join(lignes))
        print()
    print(f"— {total_texte} coupure(s) de texte non reflétée(s), {total_reformes} réforme(s) non portée(s)")
    return 1 if arguments.strict and (total_texte or total_reformes) else 0


if __name__ == "__main__":
    sys.exit(main())
