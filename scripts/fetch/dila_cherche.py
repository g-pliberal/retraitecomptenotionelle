#!/usr/bin/env python3
"""Recherche plein texte dans l'index DILA construit par ``dila_index.py``.

    python scripts/fetch/dila_cherche.py jorf 'plafond NEAR("securite sociale") FRS' --jusqu 1981
    python scripts/fetch/dila_cherche.py jorf '"valeur mensuelle" plafond' --nature DECRET --compter
    python scripts/fetch/dila_cherche.py legi '"sur la base de" heures' --num R351-9
    python scripts/fetch/dila_cherche.py jorf --texte JORFTEXT000000568533 --motif 'mensuel'
    python scripts/fetch/dila_cherche.py legi --num L161-17-2                  # son histoire
    python scripts/fetch/dila_cherche.py legi --num L161-17-2 --diff           # mot à mot
    python scripts/fetch/dila_cherche.py legi --num L161-17-2 --le 2026-03-01  # ce jour-là
    python scripts/fetch/dila_cherche.py legi --num L351-1 --titre 'securite sociale' --motif âge

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

L'HISTOIRE D'UN ARTICLE (action 184). ``--num`` sans requête rend toutes les
versions d'un article, texte par texte, les plus récentes si ``--limite``
coupe ; ``--titre`` départage deux textes qui portent le même numéro.
``--diff`` imprime ce que chaque version change à la dernière qui a été en
vigueur, mot à mot — ``[-retiré-]{+ajouté+}`` et quelques mots de contexte —,
ou « (texte inchangé) », qui prouve une rédaction sans effet ; ``--motif``
suit une expression de version en version. ``--le`` rend la version en
vigueur ce jour-là, la précédente, et les phrases où le texte dit à quoi et à
partir de quand il s'applique : la version en vigueur un jour n'est pas
toujours celle qu'on applique à une pension prenant effet ce jour-là
(L. 161-17-2, en vigueur le 31 décembre 2025, s'applique aux pensions prenant
effet à compter du 1er septembre 2026). L'outil relève ces phrases, il ne les
tranche pas. L'index garde la NOTA d'un article en tête de son texte.

CHAQUE RÉPONSE DIT SA FRAÎCHEUR, sur la sortie d'erreur : le jour du dernier
incrément appliqué, et la commande qui rattrape un index de plus de sept jours.
"""

from __future__ import annotations

import argparse
import difflib
import itertools
import re
import sqlite3
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dila_index import BASES, chemin_index, meta  # noqa: E402

LARGEUR_TITRE = 110

#: Les mots gardés de part et d'autre d'un changement, dans ``--diff``.
CONTEXTE = 6

#: La fin de validité d'une version qui court encore (LEGI), ou d'un document
#: qui n'en a pas (JORF).
OUVERTE = ("", "2999-01-01")

#: Ce qui, dans une phrase, dit à quoi et à partir de quand un texte
#: s'applique ; la phrase n'est relevée que si elle porte aussi une date.
APPLICATION = re.compile(
    r"s.appliqu|applicables?\b|en vigueur|prenant effet|prend effet|date d.effet", re.I)
DATE_ECRITE = re.compile(
    r"\b\d{1,2} ?(?:er)? (?:janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|"
    r"septembre|octobre|novembre|d[ée]cembre) \d{4}\b", re.I)
#: Une fin de phrase : un point ou un point-virgule, puis une majuscule ; pas
#: l'initiale d'un article (« L. 351-1 »).
PHRASE = re.compile(r"(?<=[.;])(?<!\b[A-Z]\.)\s+(?=[A-ZÀ-ÖØ-Þ«])")
#: « 1<sup>er</sup> » que l'index lit « 1 er » : le même mot que « 1er ».
ORDINAL = re.compile(r"\b(\d+) (er|re)\b")


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
    if options.titre:
        sql.append("instr(plat(doc.titre), ?) > 0"); valeurs.append(plat(options.titre))
    return (" AND " + " AND ".join(sql)) if sql else "", valeurs


def plat(texte: str | None) -> str:
    """Sans accents ni casse : « Sécurité » et « securite » se valent."""
    decompose = unicodedata.normalize("NFKD", texte or "")
    return "".join(c for c in decompose if not unicodedata.combining(c)).lower()


def _preparer(db: sqlite3.Connection) -> None:
    db.create_function("plat", 1, plat, deterministic=True)


def chercher(db: sqlite3.Connection, requete: str, options) -> tuple[list[tuple], int, str]:
    """Rend (lignes, total, requête réellement soumise)."""
    _preparer(db)
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


def _entete(ident: str, debut: str, fin: str | None, nature: str, num: str, titre: str) -> str:
    """La ligne qui identifie un document : identifiant, validité, nature, titre."""
    fin = fin or ""
    validite = f" → {fin}" if fin not in OUVERTE else ""
    article = f" art. {num}" if num else ""
    mort_nee = "  (jamais en vigueur)" if fin not in OUVERTE and fin <= debut else ""
    return f"{ident}  {debut}{validite}  {nature}{article}  {(titre or '')[:LARGEUR_TITRE]}{mort_nee}"


def afficher(lignes: list[tuple], total: int, options, sortie=None) -> None:
    sortie = sortie or sys.stdout
    for ident, debut, fin, nature, num, titre, extrait in lignes:
        print(_entete(ident, debut, fin, nature, num, titre), file=sortie)
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
    zones = fenetres(corps, motif, autour)
    if not zones:
        print(f"(aucune occurrence de « {motif} » dans {len(corps):,} caractères)", file=sortie)
    for debut, fin_ in zones:
        print(f"[{debut}] …{corps[debut:fin_]}…\n", file=sortie)


def fenetres(corps: str, motif: str, autour: int) -> list[tuple[int, int]]:
    """Les plages de ``corps`` autour de chaque occurrence de ``motif``,
    fondues quand elles se touchent."""
    zones: list[tuple[int, int]] = []
    for trouve in re.finditer(motif, corps, re.I):
        debut, fin = max(0, trouve.start() - autour), min(len(corps), trouve.end() + autour)
        if zones and debut <= zones[-1][1]:
            zones[-1] = (zones[-1][0], fin)
        else:
            zones.append((debut, fin))
    return zones


# ---------------------------------------------------------------------------
# L'histoire d'un article (action 184)
# ---------------------------------------------------------------------------

def versions(db: sqlite3.Connection, options) -> list[tuple]:
    """Toutes les versions d'un article (``--num``), texte par texte, de la
    plus ancienne à la plus récente : (id, date, fin, nature, num, titre, texte)."""
    _preparer(db)
    filtres, valeurs = _clauses(options)
    return db.execute(
        f"SELECT id, date, fin, nature, num, titre, texte FROM doc WHERE 1{filtres} "
        "ORDER BY titre, date, id", valeurs).fetchall()


def _a_vecu(ligne: tuple) -> bool:
    """Une version a été en vigueur, au moins un jour : LEGI garde aussi celles
    qu'un texte a modifiées avant qu'elles prennent effet (fin ≤ début)."""
    return (ligne[2] or "") in OUVERTE or ligne[2] > ligne[1]


def _en_vigueur_le(ligne: tuple, jour: str) -> bool:
    """DATE_FIN est le premier jour de la version suivante."""
    return ligne[1] <= jour and ((ligne[2] or "") in OUVERTE or jour < ligne[2])


def difference(avant: str, apres: str, contexte: int = CONTEXTE) -> str:
    """Ce qu'``apres`` change à ``avant``, mot à mot : ``[-retiré-]{+ajouté+}``,
    ``contexte`` mots de part et d'autre, « … » pour le reste. Vide si rien
    ne change. « 1 er » et « 1er » se valent."""
    a, b = (ORDINAL.sub(r"\1\2", texte).split() for texte in (avant, apres))
    blocs = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    if all(etiquette == "equal" for etiquette, *_ in blocs):
        return ""
    morceaux = []
    for rang, (etiquette, i1, i2, j1, j2) in enumerate(blocs):
        if etiquette != "equal":
            morceaux.append((f"[-{' '.join(a[i1:i2])}-]" if i2 > i1 else "")
                            + (f"{{+{' '.join(b[j1:j2])}+}}" if j2 > j1 else ""))
            continue
        mots, premier, dernier = a[i1:i2], rang == 0, rang == len(blocs) - 1
        if premier and len(mots) > contexte:
            morceaux.append("… " + " ".join(mots[-contexte:]))
        elif dernier and len(mots) > contexte:
            morceaux.append(" ".join(mots[:contexte]) + " …")
        elif not (premier or dernier) and len(mots) > 2 * contexte:
            morceaux.append(" ".join(mots[:contexte]) + " … " + " ".join(mots[-contexte:]))
        else:
            morceaux.append(" ".join(mots))
    return " ".join(morceaux)


def _a_montrer(lignes: list[tuple], limite: int | None) -> list[tuple]:
    """Les ``limite`` versions les plus récentes, dans l'ordre de ``lignes``."""
    if not limite or len(lignes) <= limite:
        return lignes
    gardees = {l[0] for l in sorted(lignes, key=lambda l: (l[1], l[0]))[-limite:]}
    return [l for l in lignes if l[0] in gardees]


def historique(lignes: list[tuple], options, sortie=None) -> None:
    """Les versions, une ligne chacune ; avec ``--diff``, ce que chacune change
    à la dernière qui a été en vigueur dans le même texte ; avec ``--motif``,
    les fenêtres où l'expression se trouve, ou « (absent) »."""
    sortie = sortie or sys.stdout
    precedente: dict[str, tuple | None] = {}
    derniere: dict[str, tuple] = {}
    for ligne in lignes:
        precedente[ligne[0]] = derniere.get(ligne[5])
        if _a_vecu(ligne):
            derniere[ligne[5]] = ligne
    montrees = _a_montrer(lignes, options.limite)
    for ligne in montrees:
        print(_entete(*ligne[:6]), file=sortie)
        if options.diff:
            avant = precedente[ligne[0]]
            if avant is not None:
                print("    " + (difference(avant[6], ligne[6]) or "(texte inchangé)"), file=sortie)
        elif options.motif:
            zones = fenetres(ligne[6], options.motif, options.autour)
            for debut, fin in zones:
                print(f"    [{debut}] …{ligne[6][debut:fin]}…", file=sortie)
            if not zones:
                print("    (absent)", file=sortie)
    if len(montrees) < len(lignes):
        print(f"— {len(lignes)} versions au total, {len(montrees)} affichées (--limite)",
              file=sortie)


def clauses_d_application(texte: str) -> list[str]:
    """Les phrases où un texte dit à quoi et à partir de quand il s'applique :
    un verbe d'application et une date. Relevées, non tranchées."""
    return [phrase for phrase in PHRASE.split(texte)
            if APPLICATION.search(phrase) and DATE_ECRITE.search(phrase)]


def en_vigueur(lignes: list[tuple], jour: str, options, sortie=None) -> None:
    """Pour chaque texte, la version en vigueur le ``jour`` : son texte (ou les
    fenêtres de ``--motif``), la version précédente, et ses clauses
    d'application."""
    sortie = sortie or sys.stdout
    vecues = [ligne for ligne in lignes if _a_vecu(ligne)]
    trouvees = 0
    for _, groupe in itertools.groupby(vecues, key=lambda ligne: ligne[5]):
        groupe = list(groupe)
        for rang, ligne in enumerate(groupe):
            if not _en_vigueur_le(ligne, jour):
                continue
            trouvees += 1
            corps = ligne[6]
            print(_entete(*ligne[:6]), file=sortie)
            if options.motif:
                for debut, fin in fenetres(corps, options.motif, options.autour):
                    print(f"[{debut}] …{corps[debut:fin]}…", file=sortie)
            else:
                print(corps, file=sortie)
            if rang:
                avant = groupe[rang - 1]
                print(f"précédente : {avant[0]}  {avant[1]}"
                      f"{' → ' + avant[2] if (avant[2] or '') not in OUVERTE else ''}",
                      file=sortie)
            clauses = clauses_d_application(corps)
            if clauses:
                print("Ce que le texte dit de son application "
                      "(l'entrée en vigueur n'en décide pas seule) :", file=sortie)
                for clause in clauses:
                    print(f"    « {clause} »", file=sortie)
    if not trouvees:
        message = f"aucune version en vigueur le {jour}"
        if vecues and jour < min(ligne[1] for ligne in vecues):
            message += f" : la première commence le {min(ligne[1] for ligne in vecues)}"
        elif vecues:
            message += f" : la dernière a pris fin le {max(ligne[2] for ligne in vecues)}"
        raise LookupError(message)


def _jour(horodatage: str) -> str:
    """« 20261102-213929 » → « 2026-11-02 »."""
    trouve = re.match(r"(\d{4})(\d{2})(\d{2})", horodatage or "")
    return "-".join(trouve.groups()) if trouve else ""


def fraicheur(db: sqlite3.Connection, aujourd_hui: date | None = None) -> str:
    """Jusqu'où va l'index, et comment le rattraper s'il a plus de sept jours."""
    base = meta(db, "base") or "?"
    jour = _jour(meta(db, "dernier_increment"))
    ligne = (f"(index {base.upper()} à jour au {jour or 'jour inconnu'}, "
             f"{'sans filtre' if meta(db, 'filtre') == 'tout' else 'filtre thématique'}")
    if jour and (aujourd_hui or date.today()) - date.fromisoformat(jour) > timedelta(days=7):
        ligne += f" ; plus de sept jours : python scripts/fetch/dila_index.py {base} --mettre-a-jour"
    return ligne + ")"


def _date(valeur: str) -> str:
    try:
        return date.fromisoformat(valeur).isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(f"« {valeur} » : une date AAAA-MM-JJ") from None


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("base", choices=sorted(BASES))
    analyseur.add_argument("requete", nargs="?", help="requête FTS5")
    analyseur.add_argument("--index", help="chemin de la base")
    analyseur.add_argument("--depuis", type=int, metavar="AAAA", help="année de publication minimale")
    analyseur.add_argument("--jusqu", type=int, metavar="AAAA", help="année de publication maximale")
    analyseur.add_argument("--nature", help="DECRET, ARRETE, LOI, « Article DECRET »…")
    analyseur.add_argument("--num", help="numéro d'article (LEGI : R351-9, L161-17-2…) ; "
                                         "sans requête, toutes ses versions")
    analyseur.add_argument("--titre", help="filtre sur le titre du texte, sans accents ni "
                                           "casse (« securite sociale »)")
    analyseur.add_argument("--diff", action="store_true",
                           help="avec --num : ce que chaque version change, mot à mot")
    analyseur.add_argument("--le", type=_date, metavar="AAAA-MM-JJ",
                           help="avec --num : la version en vigueur ce jour-là")
    analyseur.add_argument("--limite", type=int, default=20)
    analyseur.add_argument("--extrait", type=int, default=14, metavar="MOTS",
                           help="longueur de l'extrait (défaut 14 mots, 64 au plus)")
    analyseur.add_argument("--compter", action="store_true", help="n'imprime que le nombre")
    analyseur.add_argument("--texte", metavar="ID", help="imprime un document de l'index")
    analyseur.add_argument("--motif", help="avec --texte, --num ou --le : n'imprime que les "
                                           "fenêtres autour de ce motif")
    analyseur.add_argument("--autour", type=int, default=300, help="largeur des fenêtres de --motif")
    analyseur.add_argument("--etat", action="store_true", help="ce que contient l'index")
    options = analyseur.parse_intermixed_args(arguments)
    if (options.diff or options.le) and (not options.num or options.requete):
        analyseur.error("--diff et --le suivent un article : --num, sans requête")
    try:
        db = _connexion(chemin_index(options.base, options.index))
        if options.etat:
            for cle in ("base", "dump", "dernier_increment", "construit_le"):
                print(f"{cle} : {meta(db, cle)}")
            print(f"documents : {db.execute('SELECT count(*) FROM doc').fetchone()[0]:,}")
            print(f"filtre : {'aucun' if meta(db, 'filtre') == 'tout' else 'thématique'}")
        elif options.texte:
            texte(db, options.texte, options.motif, options.autour)
        elif options.num and not options.requete:
            lignes = versions(db, options)
            if not lignes:
                raise LookupError(f"{options.num} n'est pas dans l'index"
                                  + (f" sous « {options.titre} »" if options.titre else ""))
            if options.le:
                en_vigueur(lignes, options.le, options)
                borne = _jour(meta(db, "dernier_increment"))
                if borne and options.le > borne:
                    print(f"(l'index s'arrête au {borne} : un texte paru depuis n'y est pas)",
                          file=sys.stderr)
            else:
                historique(lignes, options)
            print(fraicheur(db), file=sys.stderr)
        elif options.requete:
            lignes, total, soumise = chercher(db, options.requete, options)
            if soumise != options.requete:
                print(f"(requête reprise comme phrase : {soumise})")
            afficher(lignes, total, options)
            print(fraicheur(db), file=sys.stderr)
        else:
            analyseur.error("une requête, --texte ID ou --etat")
    except (FileNotFoundError, LookupError, ValueError) as erreur:
        print(f"Échec : {erreur}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
