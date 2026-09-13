#!/usr/bin/env python3
"""Recherche plein texte dans l'index DILA construit par ``dila_index.py``.

    python scripts/fetch/dila_cherche.py jorf 'plafond NEAR("securite sociale") FRS' --jusqu 1981
    python scripts/fetch/dila_cherche.py jorf '"valeur mensuelle" plafond' --nature DECRET --compter
    python scripts/fetch/dila_cherche.py legi '"sur la base de" heures' --num R351-9
    python scripts/fetch/dila_cherche.py jorf --texte JORFTEXT000000568533 --motif 'mensuel'

Une recherche rend une ligne d'identification par document — identifiant,
date, nature, titre — et un EXTRAIT de quelques mots autour des termes
trouvés, entre crochets. C'est ce qui économise la lecture : un texte entier
ne se lit qu'à la demande, par ``--texte``, et ``--motif`` n'en imprime que
les fenêtres qui portent l'expression cherchée.

LA REQUÊTE EST CELLE DE SQLITE FTS5. Les mots se combinent par ET implicite ;
``OR``, ``NOT``, ``"une phrase"``, ``NEAR(a b, 5)`` et ``titre:mot`` sont
compris. Les accents sont ignorés des deux côtés (« sécurité » et « SECURITE »
sont le même mot), la casse aussi. Un préfixe ``mot*`` est possible mais lent :
l'index n'a pas de table de préfixes, et la requête balaie tout. Une requête
que FTS5 refuse — apostrophe, tiret, parenthèse hors syntaxe — est reprise
telle quelle comme une phrase, et la reprise est signalée.

CE QUE L'INDEX NE CONTIENT PAS. Seuls les documents dont le titre ou le texte
touche au champ social y sont (voir ``THEMATIQUE`` dans ``dila_index.py``) :
ne rien trouver ici ne dit rien du reste du Journal officiel.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dila_index import BASES, chemin_index, meta  # noqa: E402

LARGEUR_TITRE = 110


def _connexion(chemin: Path) -> sqlite3.Connection:
    if not chemin.exists():
        raise FileNotFoundError(
            f"{chemin} absent — python scripts/fetch/dila_index.py {chemin.stem} --recuperer")
    return sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)


def _clauses(options) -> tuple[str, list]:
    """Les filtres hors texte, en SQL sur la table ``doc``."""
    sql, valeurs = [], []
    if options.depuis:
        sql.append("doc.date >= ?"); valeurs.append(f"{options.depuis}")
    if options.jusqu:
        sql.append("doc.date < ?"); valeurs.append(f"{int(options.jusqu) + 1:04d}")
    if options.nature:
        sql.append("upper(doc.nature) LIKE ?"); valeurs.append(f"%{options.nature.upper()}%")
    if options.num:
        sql.append("replace(replace(upper(doc.num), ' ', ''), '.', '') = ?")
        valeurs.append(re.sub(r"[ .]", "", options.num.upper()))
    return (" AND " + " AND ".join(sql)) if sql else "", valeurs


def chercher(db: sqlite3.Connection, requete: str, options) -> tuple[list[tuple], int, str]:
    """Rend (lignes, total, requête réellement soumise)."""
    filtres, valeurs = _clauses(options)
    base = (f"FROM fts JOIN doc ON doc.rowid = fts.rowid WHERE fts MATCH ?{filtres}")
    soumise = requete
    for tentative in (requete, '"' + requete.replace('"', '""') + '"'):
        try:
            total = db.execute(f"SELECT count(*) {base}", [tentative, *valeurs]).fetchone()[0]
            soumise = tentative
            break
        except sqlite3.OperationalError as erreur:
            if "fts5: syntax error" not in str(erreur) and "no such column" not in str(erreur):
                raise
    else:
        raise ValueError(f"requête refusée par FTS5 : {requete}")
    if options.compter:
        return [], total, soumise
    lignes = db.execute(
        f"SELECT doc.id, doc.date, doc.fin, doc.nature, doc.num, doc.titre, "
        f"snippet(fts, 1, '[', ']', '…', ?) {base} ORDER BY doc.date, doc.rowid LIMIT ?",
        [options.extrait, soumise, *valeurs, options.limite]).fetchall()
    return lignes, total, soumise


def afficher(lignes: list[tuple], total: int, options, sortie=None) -> None:
    sortie = sortie or sys.stdout
    for ident, date, fin, nature, num, titre, extrait in lignes:
        validite = f" → {fin}" if fin and fin != "2999-01-01" else ""
        article = f" art. {num}" if num else ""
        print(f"{ident}  {date}{validite}  {nature}{article}  {titre[:LARGEUR_TITRE]}", file=sortie)
        if extrait:
            print(f"    {extrait}", file=sortie)
    if options.compter or total > len(lignes):
        print(f"— {total} documents au total"
              + (f", {len(lignes)} affichés (--limite)" if lignes else ""), file=sortie)


def texte(db: sqlite3.Connection, ident: str, motif: str | None, autour: int,
          sortie=None) -> None:
    sortie = sortie or sys.stdout
    ligne = db.execute("SELECT date, fin, nature, num, titre, texte FROM doc WHERE id = ?",
                       (ident,)).fetchone()
    if ligne is None:
        raise LookupError(f"{ident} n'est pas dans l'index")
    date, fin, nature, num, titre, corps = ligne
    print(f"{ident}  {date}{' → ' + fin if fin else ''}  {nature}"
          f"{' art. ' + num if num else ''}\n{titre}\n", file=sortie)
    if not motif:
        print(corps, file=sortie)
        return
    fenetres: list[tuple[int, int]] = []
    for trouve in re.finditer(motif, corps, re.I):
        debut, fin_ = max(0, trouve.start() - autour), min(len(corps), trouve.end() + autour)
        if fenetres and debut <= fenetres[-1][1]:
            fenetres[-1] = (fenetres[-1][0], fin_)
        else:
            fenetres.append((debut, fin_))
    if not fenetres:
        print(f"(aucune occurrence de « {motif} » dans {len(corps):,} caractères)", file=sortie)
    for debut, fin_ in fenetres:
        print(f"[{debut}] …{corps[debut:fin_]}…\n", file=sortie)


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("base", choices=sorted(BASES))
    analyseur.add_argument("requete", nargs="?", help="requête FTS5")
    analyseur.add_argument("--index", help="chemin de la base")
    analyseur.add_argument("--depuis", type=int, metavar="AAAA", help="année de publication minimale")
    analyseur.add_argument("--jusqu", type=int, metavar="AAAA", help="année de publication maximale")
    analyseur.add_argument("--nature", help="DECRET, ARRETE, LOI, « Article DECRET »…")
    analyseur.add_argument("--num", help="numéro d'article (LEGI : R351-9, L161-17-2…)")
    analyseur.add_argument("--limite", type=int, default=20)
    analyseur.add_argument("--extrait", type=int, default=14, metavar="MOTS",
                           help="longueur de l'extrait (défaut 14 mots, 64 au plus)")
    analyseur.add_argument("--compter", action="store_true", help="n'imprime que le nombre")
    analyseur.add_argument("--texte", metavar="ID", help="imprime un document de l'index")
    analyseur.add_argument("--motif", help="avec --texte : n'imprime que les fenêtres autour de ce motif")
    analyseur.add_argument("--autour", type=int, default=300, help="largeur des fenêtres de --motif")
    analyseur.add_argument("--etat", action="store_true", help="ce que contient l'index")
    options = analyseur.parse_intermixed_args(arguments)
    try:
        db = _connexion(chemin_index(options.base, options.index))
        if options.etat:
            for cle in ("base", "dump", "dernier_increment", "construit_le"):
                print(f"{cle} : {meta(db, cle)}")
            print(f"documents : {db.execute('SELECT count(*) FROM doc').fetchone()[0]:,}")
            print(f"filtre : {'aucun' if meta(db, 'filtre') == 'tout' else 'thématique'}")
        elif options.texte:
            texte(db, options.texte, options.motif, options.autour)
        elif options.requete:
            lignes, total, soumise = chercher(db, options.requete, options)
            if soumise != options.requete:
                print(f"(requête reprise comme phrase : {soumise})")
            afficher(lignes, total, options)
        else:
            analyseur.error("une requête, --texte ID ou --etat")
    except (FileNotFoundError, LookupError, ValueError) as erreur:
        print(f"Échec : {erreur}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
