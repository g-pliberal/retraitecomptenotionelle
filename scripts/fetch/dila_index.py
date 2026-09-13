#!/usr/bin/env python3
"""Index plein texte des bases JORF et LEGI de la DILA, en SQLite FTS5.

    python scripts/fetch/dila_index.py jorf --recuperer      # l'index publié, en une minute
    python scripts/fetch/dila_index.py jorf --mettre-a-jour  # les incréments parus depuis
    python scripts/fetch/dila_cherche.py jorf 'plafond NEAR("securite sociale") FRS'

    python scripts/fetch/dila_index.py jorf                  # le construire soi-même (30 min)
    python scripts/fetch/dila_index.py jorf --publier        # l'envoyer sur la release GitHub

CE QUE CELA REMPLACE. Chaque script ``dila_legi_*`` et ``jorf_*`` de ce
répertoire retélécharge le dump global de la DILA — 1,67 Go pour le JORF,
1,1 Go pour LEGI — et le dépouille en flux. Mesuré depuis une session
Claude Code : 21 minutes de téléchargement à 1,3 Mo/s, puis 7 minutes de
décompression et de filtre, pour un dump global qui n'a pas changé depuis
le 13 juillet 2025. Toute recherche exploratoire coûtait donc une
demi-heure, et imprimait jusqu'à 12 000 caractères par texte retenu.

CE QUE CELA FAIT. Le dump est lu UNE fois, gardé en cache sur disque, et
versé dans une base SQLite FTS5 : une ligne par texte et par article, avec
son identifiant, ses dates, sa nature, son titre et son texte débarrassé
des balises. Une recherche y prend quelques millisecondes et rend des
EXTRAITS, pas des textes entiers. La base construite est publiée comme
fichier de release GitHub, d'où n'importe quelle session la récupère en
une minute ; les incréments quotidiens de la DILA la tiennent à jour sans
retélécharger le dump.

CE QU'ELLE CONTIENT, ET CE QU'ELLE NE CONTIENT PAS. Tout le JORF fait
4 millions de documents et 6,5 Go en SQLite : trop pour être publié. La
base ne garde que les documents dont le titre ou le texte touche au champ
du dépôt — retraite, pension, cotisation, Sécurité sociale, plafond, SMIC,
point d'indice, minima, régimes… — selon le motif ``THEMATIQUE`` ci-dessous,
inscrit dans la table ``meta`` de la base. L'option ``--tout`` lève ce
filtre pour qui a le disque. Un texte hors champ n'y est donc pas, et une
recherche qui n'y trouve rien ne prouve rien sur le JORF entier : c'est le
dump qui fait foi, et les scripts de certification continuent de le lire.

LE DUMP GLOBAL A QUATORZE MOIS. La DILA ne l'a pas régénéré depuis juillet
2025 ; ce qui a paru depuis n'est que dans les incréments quotidiens
(``JORF_AAAAMMJJ-HHMMSS.tar.gz``, cent à deux cents Ko chacun). L'index les
applique tous à la construction, et ``--mettre-a-jour`` n'applique que les
nouveaux, en secondes. Un incrément peut remplacer un document (même
identifiant) ou en supprimer (``liste_suppression_*.dat``) : les deux sont
honorés, dans l'ordre de parution.
"""

from __future__ import annotations

import argparse
import gzip
import html
import io
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Iterator

RACINE = "https://echanges.dila.gouv.fr/OPENDATA/"
CACHE = Path(__file__).resolve().parents[2] / "data" / "brut" / "dila"
DEPOT = "g-pliberal/retraitecomptenotionelle"
ETIQUETTE = "index-dila"

BASES = {
    "jorf": {"global": "Freemium_jorf_global_", "increment": "JORF_"},
    "legi": {"global": "Freemium_legi_global_", "increment": "LEGI_"},
}

#: Ce qui fait entrer un document dans l'index : un de ces motifs dans son
#: titre ou son texte, sans égard à la casse ni aux accents (le JORF ancien est
#: en capitales non accentuées). Large à dessein sur le champ social, fermé
#: au reste : les nominations, les avis de concours et les marchés publics
#: sont les trois quarts du Journal officiel, et n'ont rien à dire au modèle.
THEMATIQUE = re.compile(
    r"retrait|pension|cotis|s[ée]curit[ée] sociale|plafond|vieillesse|smic|"
    r"salaire minimum|point d.indice|indice (?:brut|major)|pr[ée]voyance|"
    r"agirc|arrco|ircantec|cnracl|rafp|invalidit|trimestre|annuit|"
    r"valeur (?:du|de service du|d.achat du) point|minimum (?:contributif|garanti)|"
    r"allocation de solidarit|r[ée]gime (?:g[ée]n[ée]ral|sp[ée]cia|compl[ée]mentaire|"
    r"de base|des (?:marins|mines|clercs))|section professionnelle|"
    r"caisse (?:nationale|autonome|de retraite)|"
    r"traitement (?:indiciaire|brut)|revalorisation",
    re.I)

BALISES = re.compile(r"<[^>]+>")
BLANCS = re.compile(r"\s+")
IDENTIFIANT = re.compile(r"(?:JORF|LEGI)(?:TEXT|ARTI)\d{12}")


@dataclass
class Document:
    id: str
    date: str      # JORF : date de publication ; LEGI : début de validité
    fin: str       # LEGI : fin de validité (2999-01-01 = en vigueur) ; JORF : vide
    nature: str    # DECRET, ARRETE, LOI… ; « Article DECRET » pour un article
    num: str       # numéro d'article, vide pour un texte
    titre: str
    texte: str


# ---------------------------------------------------------------------------
# Lecture des XML
# ---------------------------------------------------------------------------

def _champ(balise: str, xml: str) -> str:
    trouve = re.search(rf"<{balise}>(.*?)</{balise}>", xml, re.S)
    return _texte(trouve.group(1)) if trouve else ""


def _texte(xml: str) -> str:
    return BLANCS.sub(" ", html.unescape(BALISES.sub(" ", xml))).strip()


def lire(xml: str) -> Document | None:
    """Un fichier XML du dump, ramené à une ligne d'index. ``None`` s'il n'est
    ni un texte ni un article (sommaires, structures, liens ELI…)."""
    if "<TEXTE_VERSION>" in xml:
        ident = _champ("ID", xml)
        date = _champ("DATE_PUBLI", xml) if ident.startswith("JORF") else _champ("DATE_DEBUT", xml)
        fin = "" if ident.startswith("JORF") else _champ("DATE_FIN", xml)
        titre = _champ("TITREFULL", xml) or _champ("TITRE", xml)
        corps = xml.split("</META>", 1)[-1]
        return Document(ident, date, fin, _champ("NATURE", xml), "", titre, _texte(corps))
    if "<ARTICLE>" in xml:
        ident = _champ("ID", xml)
        contexte = re.search(r'<TEXTE [^>]*?\sdate_publi="([^"]*)"[^>]*?\snature="([^"]*)"', xml)
        titres = re.findall(r"<TITRE_TXT[^>]*>(.*?)</TITRE_TXT>", xml, re.S)
        titre = _texte(titres[-1]) if titres else ""
        if ident.startswith("JORF"):
            date, fin = (contexte.group(1) if contexte else ""), ""
        else:
            date, fin = _champ("DATE_DEBUT", xml), _champ("DATE_FIN", xml)
        nature = "Article " + (contexte.group(2) if contexte else "")
        corps = " ".join(re.findall(r"<CONTENU>(.*?)</CONTENU>", xml, re.S))
        return Document(ident, date, fin, nature.strip(), _champ("NUM", xml), titre, _texte(corps))
    return None


def documents(flux: BinaryIO) -> Iterator[str]:
    """Les fichiers XML d'un flux où ils sont concaténés (``tar -xzO``).

    Le découpage se fait sur les octets, et chaque document est décodé entier :
    décoder bloc par bloc abîmerait un caractère accentué tombé à cheval sur
    une frontière de lecture.
    """
    tampon = b""
    for bloc in iter(lambda: flux.read(1 << 22), b""):
        tampon += bloc
        morceaux = tampon.split(b"<?xml")
        tampon = morceaux.pop()
        yield from (m.decode("utf-8", errors="replace") for m in morceaux if m.strip())
    if tampon.strip():
        yield tampon.decode("utf-8", errors="replace")


def pertinent(doc: Document, tout: bool = False) -> bool:
    return tout or bool(THEMATIQUE.search(doc.titre) or THEMATIQUE.search(doc.texte))


# ---------------------------------------------------------------------------
# La base
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS doc (
    id TEXT NOT NULL UNIQUE, date TEXT, fin TEXT, nature TEXT, num TEXT,
    titre TEXT, texte TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(
    titre, texte, content='doc', content_rowid='rowid',
    tokenize="unicode61 remove_diacritics 2");
CREATE TRIGGER IF NOT EXISTS doc_ai AFTER INSERT ON doc BEGIN
    INSERT INTO fts(rowid, titre, texte) VALUES (new.rowid, new.titre, new.texte); END;
CREATE TRIGGER IF NOT EXISTS doc_ad AFTER DELETE ON doc BEGIN
    INSERT INTO fts(fts, rowid, titre, texte) VALUES ('delete', old.rowid, old.titre, old.texte); END;
CREATE TABLE IF NOT EXISTS meta (cle TEXT PRIMARY KEY, valeur TEXT);
"""


def ouvrir(chemin: Path) -> sqlite3.Connection:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(chemin)
    db.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;" + SCHEMA)
    return db


def meta(db: sqlite3.Connection, cle: str) -> str | None:
    ligne = db.execute("SELECT valeur FROM meta WHERE cle = ?", (cle,)).fetchone()
    return ligne[0] if ligne else None


def _ecrire_meta(db: sqlite3.Connection, cle: str, valeur: str) -> None:
    db.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)", (cle, valeur))


def inserer(db: sqlite3.Connection, xmls: Iterable[str], tout: bool = False,
            remplacer: bool = False) -> tuple[int, int]:
    """Verse des XML dans la base. Rend (documents lus, documents gardés).

    ``remplacer`` : la ligne portant le même identifiant est d'abord effacée —
    c'est ce que fait un incrément, qui republie un document modifié.
    """
    lus = gardes = 0
    lot: list[tuple] = []
    for xml in xmls:
        doc = lire(xml)
        if doc is None or not doc.id:
            continue
        lus += 1
        if lus % 500000 == 0:
            print(f"  {lus:,} documents lus, {gardes:,} gardés", file=sys.stderr)
        if remplacer:
            db.execute("DELETE FROM doc WHERE id = ?", (doc.id,))
        if not pertinent(doc, tout):
            continue
        lot.append((doc.id, doc.date, doc.fin, doc.nature, doc.num, doc.titre, doc.texte))
        gardes += 1
        if len(lot) >= 2000:
            db.executemany("INSERT OR IGNORE INTO doc VALUES (?,?,?,?,?,?,?)", lot)
            lot = []
    db.executemany("INSERT OR IGNORE INTO doc VALUES (?,?,?,?,?,?,?)", lot)
    return lus, gardes


# ---------------------------------------------------------------------------
# Les dumps de la DILA
# ---------------------------------------------------------------------------

def _listing(base: str) -> list[str]:
    with urllib.request.urlopen(RACINE + base.upper() + "/", timeout=120) as reponse:
        page = reponse.read().decode("utf-8", errors="replace")
    return sorted(set(re.findall(r'href="([^"]+\.tar\.gz)"', page)))


def dernier_dump(base: str) -> str:
    noms = [n for n in _listing(base) if n.startswith(BASES[base]["global"])]
    if not noms:
        raise LookupError(f"aucun dump global dans le répertoire {base.upper()} de la DILA")
    return noms[-1]


def horodatage(nom: str) -> str:
    """« Freemium_jorf_global_20250713-140000.tar.gz » -> « 20250713-140000»."""
    trouve = re.search(r"(\d{8}-\d{6})", nom)
    return trouve.group(1) if trouve else ""


def increments(base: str, depuis: str) -> list[str]:
    """Les incréments parus après l'horodatage ``depuis``, dans l'ordre."""
    prefixe = BASES[base]["increment"]
    return [n for n in _listing(base)
            if n.startswith(prefixe) and horodatage(n) > depuis]


def telecharger(url: str, cible: Path) -> Path:
    """Télécharge en cache, reprend un transfert coupé, ne refait rien si le
    fichier est déjà là."""
    if cible.exists():
        return cible
    cible.parent.mkdir(parents=True, exist_ok=True)
    partiel = cible.with_suffix(cible.suffix + ".partiel")
    commande = ["curl", "-sS", "-L", "--retry", "5", "--retry-delay", "5",
                "-C", "-", "--max-time", "14400", "-o", str(partiel), url]
    if subprocess.run(commande).returncode != 0:
        raise RuntimeError(f"téléchargement interrompu : {url}")
    partiel.rename(cible)
    return cible


def verser_archive(db: sqlite3.Connection, archive: Path, tout: bool,
                   remplacer: bool) -> tuple[int, int]:
    """Lit une archive tar.gz de la DILA et verse ses documents dans la base.

    Le dump global (plusieurs Go) passe par ``tar -xzO`` en flux, sans jamais
    être extrait sur disque. Un incrément, petit, est lu par ``tarfile`` pour
    y trouver aussi la liste de suppression.
    """
    if not remplacer:
        detar = subprocess.Popen(["tar", "-xzO", "-f", str(archive)],
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        bilan = inserer(db, documents(detar.stdout), tout)
        detar.wait()
        return bilan
    supprimes: list[str] = []
    xmls: list[str] = []
    with tarfile.open(archive, "r:gz") as flux:
        for membre in flux:
            if not membre.isfile():
                continue
            contenu = flux.extractfile(membre).read().decode("utf-8", errors="replace")
            if "liste_suppression" in membre.name:
                supprimes += IDENTIFIANT.findall(contenu)
            elif membre.name.endswith(".xml"):
                xmls.append(contenu)
    for ident in supprimes:
        db.execute("DELETE FROM doc WHERE id = ?", (ident,))
    return inserer(db, xmls, tout, remplacer=True)


def construire(base: str, chemin: Path, tout: bool = False,
               archive: Path | None = None) -> None:
    """Construit l'index depuis le dump global, puis applique les incréments."""
    if chemin.exists():
        chemin.unlink()
    if archive is None:
        nom = dernier_dump(base)
        print(f"Dump global : {nom}", file=sys.stderr)
        archive = telecharger(RACINE + base.upper() + "/" + nom, CACHE / nom)
    db = ouvrir(chemin)
    debut = time.time()
    lus, gardes = verser_archive(db, archive, tout, remplacer=False)
    _ecrire_meta(db, "base", base)
    _ecrire_meta(db, "dump", archive.name)
    _ecrire_meta(db, "filtre", "tout" if tout else THEMATIQUE.pattern)
    _ecrire_meta(db, "dernier_increment", horodatage(archive.name))
    _ecrire_meta(db, "construit_le", time.strftime("%Y-%m-%d"))
    db.commit()
    db.close()
    print(f"{lus:,} documents lus, {gardes:,} gardés en {time.time() - debut:.0f} s",
          file=sys.stderr)
    if horodatage(archive.name):
        mettre_a_jour(base, chemin, tout)


def mettre_a_jour(base: str, chemin: Path, tout: bool | None = None) -> int:
    """Applique les incréments parus depuis le dernier appliqué. Rend leur nombre."""
    if not chemin.exists():
        raise LookupError(f"{chemin} absent : --recuperer, ou le construire d'abord")
    db = ouvrir(chemin)
    depuis = meta(db, "dernier_increment") or ""
    if tout is None:
        tout = meta(db, "filtre") == "tout"
    nouveaux = increments(base, depuis)
    print(f"{len(nouveaux)} incréments à appliquer depuis {depuis or 'l’origine'}",
          file=sys.stderr)
    for i, nom in enumerate(nouveaux, 1):
        archive = telecharger(RACINE + base.upper() + "/" + nom,
                              CACHE / "increments" / nom)
        lus, gardes = verser_archive(db, archive, tout, remplacer=True)
        _ecrire_meta(db, "dernier_increment", horodatage(nom))
        db.commit()
        if i % 50 == 0 or i == len(nouveaux):
            print(f"  {i}/{len(nouveaux)} — {nom} : {lus} lus, {gardes} gardés",
                  file=sys.stderr)
    db.close()
    return len(nouveaux)


# ---------------------------------------------------------------------------
# La release GitHub
# ---------------------------------------------------------------------------

def url_publiee(base: str) -> str:
    return f"https://github.com/{DEPOT}/releases/download/{ETIQUETTE}/{base}.sqlite.gz"


def recuperer(base: str, chemin: Path) -> None:
    """L'index publié, décompressé sur place."""
    comprime = telecharger(url_publiee(base), CACHE / f"{base}.sqlite.gz")
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(comprime, "rb") as source, chemin.open("wb") as cible:
        shutil.copyfileobj(source, cible, 1 << 22)
    comprime.unlink()
    db = ouvrir(chemin)
    print(f"{chemin} : dump {meta(db, 'dump')}, à jour au {meta(db, 'dernier_increment')}, "
          f"{db.execute('SELECT count(*) FROM doc').fetchone()[0]:,} documents",
          file=sys.stderr)


def _github(methode: str, url: str, jeton: str, donnees=None,
            type_contenu: str = "application/json", longueur: int | None = None):
    entetes = {"Authorization": f"Bearer {jeton}", "Accept": "application/vnd.github+json",
               "Content-Type": type_contenu}
    if longueur is not None:
        entetes["Content-Length"] = str(longueur)
    requete = urllib.request.Request(url, data=donnees, headers=entetes, method=methode)
    with urllib.request.urlopen(requete, timeout=3600) as reponse:
        corps = reponse.read()
    return json.loads(corps) if corps else {}


def publier(base: str, chemin: Path) -> None:
    """Comprime l'index et le dépose sur la release ``index-dila`` du dépôt."""
    jeton = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not jeton:
        raise RuntimeError("GH_TOKEN ou GITHUB_TOKEN absent : impossible de publier")
    db = ouvrir(chemin)
    db.execute("VACUUM")
    etat = {cle: meta(db, cle) for cle in ("dump", "dernier_increment", "filtre")}
    total = db.execute("SELECT count(*) FROM doc").fetchone()[0]
    db.close()
    comprime = CACHE / f"{base}.sqlite.gz"
    print(f"Compression de {chemin} …", file=sys.stderr)
    with chemin.open("rb") as source, gzip.open(comprime, "wb", compresslevel=6) as cible:
        shutil.copyfileobj(source, cible, 1 << 22)
    api = f"https://api.github.com/repos/{DEPOT}"
    try:
        release = _github("GET", f"{api}/releases/tags/{ETIQUETTE}", jeton)
    except urllib.error.HTTPError as erreur:
        if erreur.code != 404:
            raise
        release = _github("POST", f"{api}/releases", jeton, json.dumps({
            "tag_name": ETIQUETTE, "name": "Index plein texte des bases DILA",
            "body": "Bases SQLite FTS5 construites par `scripts/fetch/dila_index.py`. "
                    "Récupération : `python scripts/fetch/dila_index.py jorf --recuperer`.",
        }).encode())
    for actif in release.get("assets", []):
        if actif["name"] == comprime.name:
            _github("DELETE", actif["url"], jeton)
    envoi = release["upload_url"].split("{")[0] + f"?name={comprime.name}"
    taille = comprime.stat().st_size
    print(f"Envoi de {comprime.name} ({taille / 1e6:.0f} Mo) …", file=sys.stderr)
    with comprime.open("rb") as flux:
        actif = _github("POST", envoi, jeton, flux, "application/gzip", taille)
    note = (f"- `{base}.sqlite.gz` : {total:,} documents, dump {etat['dump']}, "
            f"à jour au {etat['dernier_increment']}, filtre "
            f"{'aucun' if etat['filtre'] == 'tout' else 'thématique'}, "
            f"publié le {time.strftime('%Y-%m-%d')}.")
    corps = re.sub(rf"\n- `{base}\.sqlite\.gz`[^\n]*", "", release.get("body") or "")
    _github("PATCH", release["url"], jeton, json.dumps({"body": corps.rstrip() + "\n" + note}).encode())
    print(f"Publié : {actif.get('browser_download_url')}", file=sys.stderr)


# ---------------------------------------------------------------------------

def chemin_index(base: str, explicite: str | None = None) -> Path:
    return Path(explicite) if explicite else CACHE / f"{base}.sqlite"


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("base", choices=sorted(BASES))
    analyseur.add_argument("--index", help=f"chemin de la base (défaut : {CACHE}/<base>.sqlite)")
    action = analyseur.add_mutually_exclusive_group()
    action.add_argument("--recuperer", action="store_true", help="télécharge l'index publié")
    action.add_argument("--mettre-a-jour", action="store_true", help="applique les incréments parus depuis")
    action.add_argument("--publier", action="store_true", help="dépose l'index sur la release GitHub")
    analyseur.add_argument("--tout", action="store_true", help="indexe tout, sans filtre thématique")
    analyseur.add_argument("--archive", help="dump global déjà téléchargé, à lire au lieu de le chercher")
    options = analyseur.parse_args(arguments)
    chemin = chemin_index(options.base, options.index)
    try:
        if options.recuperer:
            recuperer(options.base, chemin)
        elif options.mettre_a_jour:
            mettre_a_jour(options.base, chemin)
        elif options.publier:
            publier(options.base, chemin)
        else:
            construire(options.base, chemin, options.tout,
                       Path(options.archive) if options.archive else None)
    except (urllib.error.URLError, LookupError, RuntimeError) as erreur:
        print(f"Échec : {erreur}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
