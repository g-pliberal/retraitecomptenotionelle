#!/usr/bin/env python3
"""La frontière contributive, et la vérification qu'elle a bien été LUE.

    python scripts/frontiere_contributive.py            # la carte, par face
    python scripts/frontiere_contributive.py --verifier  # rouvre l'index LEGI
    python scripts/frontiere_contributive.py --chronologie

CE QUE CE SCRIPT TIENT. `data/reference/legislation/frontiere_contributive.yaml`
affirme, pour chaque déplacement de la frontière entre le cotisé et le gratuit,
une date, un article et une VERSION d'article — un identifiant LEGI. Une date
écrite sans version opposable serait une mémoire, et le dépôt ne fait pas
confiance aux mémoires. `--verifier` rouvre l'index LEGI construit par
`scripts/fetch/dila_index.py` et confronte chaque ligne à ce que le dump
contient : la version existe-t-elle, porte-t-elle bien ce numéro d'article,
et sa date d'entrée en vigueur est-elle celle qui est écrite ?

CE QU'IL NE VÉRIFIE PAS, et il faut le dire. Il vérifie qu'une version
existe à la date annoncée sous l'article annoncé. Il ne vérifie pas que la
PROSE de la ligne dit ce que cette version dit — cela, seul un lecteur le
fait, et c'est pourquoi chaque ligne porte `lu_le`. Un test refuse qu'une
version citée soit introuvable ; aucun test ne refusera un contresens.

LES TROIS FACES. « Contributif » désigne trois choses distinctes — ce que
l'assuré acquiert sans cotiser (`droit`), ce qu'il verse sans acquérir
(`cotisation`), et qui paie la charge (`financement`) —, et elles se
déplacent séparément. L'en-tête du fichier de données le développe.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
CHEMIN = RACINE / "data" / "reference" / "legislation" / "frontiere_contributive.yaml"
INDEX_LEGI = RACINE / "data" / "brut" / "dila" / "legi.sqlite"

#: Les sens possibles, par face. Le vocabulaire est fermé : une valeur inventée
#: au fil de l'eau rendrait la carte illisible, et le test l'interdit.
SENS_PAR_FACE = {
    "droit": {"ouvre", "ferme"},
    "cotisation": {"sterilise", "fertilise"},
    "financement": {"identifie", "fond"},
}

LIBELLE_FACE = {
    "droit": "ce que l'assuré acquiert sans avoir cotisé",
    "cotisation": "ce qu'il verse sans rien acquérir",
    "financement": "qui paie la charge, et si elle reste visible",
}

FLECHE = {
    "ouvre": "→ gratuit", "ferme": "→ cotisé",
    "sterilise": "→ sans contrepartie", "fertilise": "→ acquisitif",
    "identifie": "→ mesurable", "fond": "→ invisible",
}

PORTEES = {"applique", "non_applique", "sans_objet"}


def charger() -> dict:
    with CHEMIN.open(encoding="utf-8") as flux:
        return yaml.safe_load(flux)


def _normalise(num: str) -> str:
    """« L. 135-2 CSS » et « L135-2 » désignent la même colonne de l'index."""
    return re.sub(r"[ .]", "", num.upper())


def verifier(donnees: dict, index: Path = INDEX_LEGI) -> list[str]:
    """Confronte chaque version citée au dump LEGI. Rend la liste des écarts.

    Trois raffinements, et chacun vient d'un écart que ce contrôle a levé sur
    une ligne qui semblait pourtant juste :

    - ``preuve: fin`` — ce qui fait foi n'est pas toujours l'ENTRÉE en vigueur
      d'une version. La cotisation d'assurance veuvage n'a jamais eu qu'une
      version, de 1985 à 2004 : ce qui date sa suppression est la FIN de
      celle-ci, pas son début.
    - ``date_preuve`` — la date d'effet d'une bascule n'est pas celle du texte
      qui la porte. L'article 24 de la LFSS 2025 est en vigueur au 1er mars
      2025 et supprime le FSV au 1er janvier 2026. Les deux dates sont vraies,
      et les confondre donnerait un calendrier faux.
    - ``article_precedent`` — une comparaison peut traverser une
      recodification. Le 2° de L. 135-2 se compare au 2° de L. 222-2-1, qui
      lui succède sous un autre numéro.
    """
    if not index.exists():
        raise FileNotFoundError(
            f"{index} absent — python scripts/fetch/dila_index.py legi --recuperer")
    db = sqlite3.connect(f"file:{index}?mode=ro", uri=True)
    pivots = {_normalise(p["article"]): p for p in donnees["pivots"]}
    ecarts: list[str] = []

    def controler(code: str, champ: str, ident: str, article: str,
                  date_attendue: str | None, preuve: str) -> None:
        pivot = pivots.get(_normalise(article))
        if pivot is None:
            ecarts.append(f"{code}.{champ} : l'article {article} n'est pas un pivot déclaré")
            return
        ligne = db.execute(
            "SELECT num, date, fin, titre FROM doc WHERE id = ?", (ident,)).fetchone()
        if ligne is None:
            ecarts.append(f"{code}.{champ} : {ident} introuvable dans l'index LEGI")
            return
        num, debut, fin, titre = ligne
        if _normalise(num or "") != _normalise(pivot["num"]):
            ecarts.append(f"{code}.{champ} : {ident} porte l'article {num}, non {pivot['num']}")
        # Un numéro d'article de loi (« 24 ») ne vaut que dans son texte : le
        # pivot dit alors ce que le titre doit contenir.
        marque = pivot.get("titre_contient")
        if marque and marque.lower() not in (titre or "").lower():
            ecarts.append(f"{code}.{champ} : {ident} a pour titre « {titre} », "
                          f"qui ne porte pas « {marque} »")
        if date_attendue is None:
            return
        lue = fin if preuve == "fin" else debut
        if lue != date_attendue:
            quoi = "s'achève" if preuve == "fin" else "entre en vigueur"
            ecarts.append(f"{code}.{champ} : {ident} {quoi} le {lue}, non le {date_attendue}")

    for bascule in donnees["bascules"]:
        code = bascule["code"]
        preuve = bascule.get("preuve", "debut")
        if preuve not in ("debut", "fin"):
            ecarts.append(f"{code} : preuve « {preuve} » inconnue")
            continue
        attendue = str(bascule.get("date_preuve") or bascule["date"])
        controler(code, "version", bascule["version"], bascule["article"], attendue, preuve)
        precedente = bascule.get("version_precedente")
        if precedente is not None:
            article = bascule.get("article_precedent") or bascule["article"]
            controler(code, "version_precedente", precedente, article, None, "debut")
            ligne = db.execute("SELECT date FROM doc WHERE id = ?", (precedente,)).fetchone()
            if ligne and ligne[0] >= attendue:
                ecarts.append(f"{code}.version_precedente : {precedente} ({ligne[0]}) "
                              f"n'est pas antérieure à {attendue}")
    db.close()
    return ecarts


def carte(donnees: dict, sortie=None) -> None:
    """Les bascules par face, dans l'ordre du temps.

    ``sortie`` se résout ICI et non dans la signature : un ``sys.stdout`` posé
    en valeur par défaut est lié à l'import, et toute redirection ultérieure
    — celle d'un test, celle d'un appelant — lui échappe.
    """
    sortie = sortie or sys.stdout
    bascules = sorted(donnees["bascules"], key=lambda b: (b["face"], str(b["date"])))
    for face in ("droit", "cotisation", "financement"):
        lignes = [b for b in bascules if b["face"] == face]
        if not lignes:
            continue
        print(f"\n{face.upper()} — {LIBELLE_FACE[face]}", file=sortie)
        for b in lignes:
            print(f"  {b['date']}  {FLECHE[b['sens']]:22} {b['libelle']}", file=sortie)
            print(f"  {'':12}  {'':22} {b['article']}  {b['version']}", file=sortie)


def chronologie(donnees: dict, sortie=None) -> None:
    """Toutes faces mêlées, dans l'ordre du temps : c'est là qu'on voit que
    les trois avancent sans se donner la main."""
    sortie = sortie or sys.stdout
    for b in sorted(donnees["bascules"], key=lambda b: str(b["date"])):
        print(f"{b['date']}  {b['face']:12} {FLECHE[b['sens']]:22} {b['libelle']}",
              file=sortie)


def bilan(donnees: dict, sortie=None) -> None:
    sortie = sortie or sys.stdout
    sens = Counter(b["sens"] for b in donnees["bascules"])
    portee = Counter(b["portee_modele"] for b in donnees["bascules"])
    dates = sorted(str(b["date"]) for b in donnees["bascules"])
    print(f"\n{len(donnees['bascules'])} bascules, de {dates[0]} à {dates[-1]}, "
          f"sur {len(donnees['pivots'])} articles pivots.", file=sortie)
    print("  sens   : " + ", ".join(f"{k} {v}" for k, v in sorted(sens.items())), file=sortie)
    print("  modèle : " + ", ".join(f"{k} {v}" for k, v in sorted(portee.items())), file=sortie)


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="rouvre l'index LEGI et confronte chaque version citée")
    analyseur.add_argument("--chronologie", action="store_true",
                           help="toutes faces mêlées, dans l'ordre du temps")
    options = analyseur.parse_args(arguments)
    donnees = charger()

    if options.verifier:
        try:
            ecarts = verifier(donnees)
        except FileNotFoundError as erreur:
            print(f"Échec : {erreur}", file=sys.stderr)
            return 2
        if ecarts:
            print(f"{len(ecarts)} écart(s) entre le fichier et l'index LEGI :")
            for ecart in ecarts:
                print(f"  - {ecart}")
            return 1
        total = sum(1 for b in donnees["bascules"] for c in ("version", "version_precedente")
                    if b.get(c))
        print(f"{total} versions d'article vérifiées dans l'index LEGI, aucun écart.")
        return 0

    if options.chronologie:
        chronologie(donnees)
    else:
        carte(donnees)
    bilan(donnees)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
