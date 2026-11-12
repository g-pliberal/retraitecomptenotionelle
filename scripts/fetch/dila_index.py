#!/usr/bin/env python3
"""Index plein texte des bases JORF, LEGI et KALI de la DILA, en SQLite FTS5.

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
point d'indice, minima, régimes, grilles indiciaires et carrières des
fonctionnaires… — selon le motif ``THEMATIQUE`` ci-dessous,
inscrit dans la table ``meta`` de la base. L'option ``--tout`` lève ce
filtre pour qui a le disque. Un texte hors champ n'y est donc pas, et une
recherche qui n'y trouve rien ne prouve rien sur le JORF entier : c'est le
dump qui fait foi, et les scripts de certification continuent de le lire.

KALI, LES CONVENTIONS COLLECTIVES (action 184, étape 5). La base qui porte
les accords Agirc-Arrco a la forme de LEGI, en plus petit : un dump de 184 Mo,
352 000 textes et articles. Elle entre ENTIÈRE dans l'index, sans qu'on le
demande : 1 Go en SQLite, 276 Mo publiés, moins que LEGI filtré, et le filtre,
qui en gardait 99 000 documents pour 151 Mo, y retenait surtout les salaires
et la prévoyance des branches. Ne rien y trouver dit donc que KALI ne l'a pas.
Chaque document y porte quatre colonnes de plus (``PROPRES_A_KALI``) : son
état, le texte qui porte l'article, le numéro et le titre de sa convention.
Elle se construit en une minute et demie, et se reconstruit seule quand la
DILA renouvelle son dump (plus bas).

QUI PEUT PUBLIER. ``--publier`` crée la release ``index-dila`` du dépôt et y
dépose ``<base>.sqlite.gz`` (455 Mo pour LEGI, 766 Mo pour le JORF, 276 Mo
pour KALI, le 12 novembre 2026) avec le
jeton ``GH_TOKEN`` ou ``GITHUB_TOKEN`` de l'environnement. Il faut un jeton
qui ait le droit d'écrire les releases : celui d'une session Claude Code ne
l'a pas — GitHub répond « Creating, editing, or deleting releases is not
permitted for this session type » —, celui d'un workflow GitHub Actions
l'a. C'est donc ``.github/workflows/index-dila.yml`` qui publie : lancé à
la main (onglet Actions, « Run workflow »), il récupère l'index publié et
lui applique les incréments parus, ou le reconstruit depuis le dump si on
le lui demande ou si rien n'est publié ; chaque lundi, la mise à jour seule.

LE DUMP GLOBAL EST RARE. La DILA n'a pas régénéré celui du JORF ni celui de
LEGI de juillet 2025 à novembre 2026 ; ce qui paraît entre deux dumps n'est
que dans les incréments quotidiens
(``JORF_AAAAMMJJ-HHMMSS.tar.gz``, cent à deux cents Ko chacun). L'index les
applique tous à la construction, et ``--mettre-a-jour`` n'applique que les
nouveaux, en secondes. Un incrément peut remplacer un document (même
identifiant) ou en supprimer (``liste_suppression_*.dat``) : les deux sont
honorés, dans l'ordre de parution.

LA DILA A RENOUVELÉ SES DUMPS LE 8 NOVEMBRE 2026, ceux des trois bases, et a
retiré de son serveur les incréments d'avant : le 11, chaque répertoire ne
listait plus que le dump du 8 et les incréments parus depuis. Un index arrêté
avant un dump neuf ne peut donc plus rattraper ce qui a paru entre son dernier
incrément et ce dump ; appliquer les suivants y laisserait un trou sans le
dire. ``--mettre-a-jour`` reconstruit alors KALI depuis le dump neuf, en
quelques minutes. Pour le JORF et LEGI, dont la reconstruction prend une heure
et plus, elle REFUSE : elle n'applique rien, laisse l'index tel quel, dit
comment le reconstruire et sort en échec, ce qui arrête la course du workflow
avant la publication. La reconstruction reste un geste voulu : le workflow
relancé en cochant « reconstruire », ou ``dila_index.py <base>`` sur un poste
(décision du propriétaire, 12 novembre 2026 ; action 184, étape 8). Les index
publiés, à jour au-delà du dump du 8 novembre, n'ont pas ce trou.
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

#: ``entiere`` : la base entre sans filtre, et se reconstruit quand la DILA
#: renouvelle son dump (voir « KALI » dans l'en-tête) ; les autres refusent
#: alors la mise à jour.
BASES = {
    "jorf": {"global": "Freemium_jorf_global_", "increment": "JORF_"},
    "legi": {"global": "Freemium_legi_global_", "increment": "LEGI_"},
    "kali": {"global": "Freemium_kali_global_", "increment": "KALI_", "entiere": True},
}

#: Ce qui fait entrer un document dans l'index : un de ces motifs dans son
#: titre ou son texte, sans égard à la casse ni aux accents (le JORF ancien est
#: en capitales non accentuées). Large à dessein sur le champ social, fermé
#: au reste : les nominations, les avis de concours et les marchés publics
#: sont les trois quarts du Journal officiel, et n'ont rien à dire au modèle.
#: Depuis l'action 158, il garde aussi les grilles indiciaires des trois
#: fonctions publiques et des militaires, et les textes qui fixent les
#: carrières — statuts particuliers, dispositions statutaires communes,
#: organisation des carrières : les durées d'échelon et les reclassements.
#: Un article porte le titre de son texte, qui le fait entrer avec les autres ;
#: l'article qui fixe les durées d'échelon entre aussi par son seul texte
#: (``DUREES_D_ECHELON``), comme D. 732-76 et D. 732-77 du code rural de 2005 à
#: 2025, qui ne disent que « points » sous le titre du code (action 131).
#: Élargi le 3 novembre 2026 (action 158, note du jour).
#:
#: Ce qui fixe, dans le texte d'un article, la durée des échelons d'une grille :
#: « la durée du temps passé dans chacun des échelons », « le temps passé aux
#: 1er et 2e échelons », « durée passée dans », « durée de l'échelon »,
#: « ancienneté exigée dans l'échelon pour accéder à l'échelon supérieur »,
#: « du 1er au 2e échelon : 2 ans », les en-têtes « échelons durée » et les
#: tableaux qui donnent deux durées par échelon. Le titre d'un statut ne le dit
#: pas toujours (« portant statuts particuliers », « fixant les dispositions
#: statutaires applicables », « relatif aux emplois supérieurs »), ni celui
#: d'un article de code. ``\b`` après « échelon » laisse « échelonnement ».
DUREES_D_ECHELON = re.compile(
    r"temps (?:de services? effectifs? )?(?:normalement )?(?:pass[ée]|[àa] passer) "
    r"(?:dans|aux?|[àa]) (?:\S+ ){0,5}?\S*[ée]chelons?\b|"
    r"dur[ée]e pass[ée]e dans (?:\S+ ){0,5}?\S*[ée]chelons?\b|"
    r"dur[ée]es? (?:(?:moyennes?|minimales?|maximales?|et) ){0,4}(?:de l.|d.|dans l.|"
    r"dans chaque |de chaque |des |de chacun des |dans chacun des )[ée]chelons?\b|"
    r"(?:anciennet[ée]|dur[ée]e) (?:\S+ ){0,3}?(?:exig[ée]e|requise|donnant acc[èe]s|"
    r"[àa] accomplir)s? (?:\S+ ){0,5}?\S*[ée]chelons?\b|"
    r"anciennet[ée] (?:moyenne|minimale|maximale) (?:\S+ ){0,5}?\S*[ée]chelons?\b|"
    r"du \d+ ?(?:er|e|[èe]me) (?:[ée]chelon )?au \d+ ?(?:e|[èe]me) [ée]chelon\W{0,3}"
    r"(?:\d+|un|deux|trois|quatre|cinq|six) (?:ans?|mois)\b|"
    r"[ée]chelons? (?:provisoires? )?:? ?dur[ée]es?\b|"
    r"[ée]chelons?\W{1,4}\d+ ans?\W{1,4}\d+ ans?\b",
    re.I)

THEMATIQUE = re.compile(
    r"retrait|pension|cotis|s[ée]curit[ée] sociale|plafond|vieillesse|smic|"
    r"salaire minimum|point d.indice|pr[ée]voyance|"
    r"agirc|arrco|ircantec|cnracl|rafp|invalidit|trimestre|annuit|"
    r"valeur (?:du|de service du|d.achat du) point|minimum (?:contributif|garanti)|"
    r"allocation de solidarit|r[ée]gime (?:g[ée]n[ée]ral|sp[ée]cia|compl[ée]mentaire|"
    r"de base|des (?:marins|mines|clercs))|section professionnelle|"
    r"caisse (?:nationale|autonome|de retraite)|"
    r"traitement (?:indiciaire|brut)|revalorisation|"
    r"indices? (?:nouveaux? |r[ée]els? )?(?:brut|major|net)|"
    r"indices? de (?:solde|la fonction publique)|"
    r"(?:[ée]chelonnement|classement|bonification) indiciaire|"
    r"grilles? (?:indiciaires?|de r[ée]mun[ée]ration)|[ée]chelles? de r[ée]mun[ée]ration|"
    r"statut particulier|dispositions statutaires communes|organisation des carri[èe]res|"
    r"avancement d.[ée]chelon|nombre annuel moyen de points|" + DUREES_D_ECHELON.pattern,
    re.I)

BALISES = re.compile(r"<[^>]+>")
BLANCS = re.compile(r"\s+")
IDENTIFIANT = re.compile(r"(?:JORF|LEGI|KALI)(?:TEXT|ARTI)\d{12}")


@dataclass
class Document:
    id: str
    date: str      # JORF : date de publication ; LEGI : début de validité
    fin: str       # LEGI : fin de validité (2999-01-01 = en vigueur) ; JORF : vide
    nature: str    # DECRET, ARRETE, LOI… ; « Article DECRET » pour un article
    num: str       # numéro d'article, vide pour un texte
    titre: str
    texte: str
    # Ce qu'un document de KALI porte de plus (``PROPRES_A_KALI``).
    etat: str = ""        # VIGUEUR_ETEN, VIGUEUR_NON_ETEN, REMPLACE, PERIME, ABROGE…
    cid: str = ""         # le texte qui porte l'article ; pour un texte, lui-même
    idcc: str = ""        # le numéro de la convention collective, s'il y en a une
    convention: str = ""  # le titre de la convention, ou du texte indépendant


# ---------------------------------------------------------------------------
# Lecture des XML
# ---------------------------------------------------------------------------

def _champ(balise: str, xml: str) -> str:
    trouve = re.search(rf"<{balise}>(.*?)</{balise}>", xml, re.S)
    return _texte(trouve.group(1)) if trouve else ""


def _texte(xml: str) -> str:
    return BLANCS.sub(" ", html.unescape(BALISES.sub(" ", xml))).strip()


def _attribut(balise: str, nom: str, xml: str) -> str:
    trouve = re.search(rf'<{balise} [^>]*?\b{nom}="([^"]*)"', xml)
    return html.unescape(trouve.group(1)) if trouve else ""


def lire(xml: str) -> Document | None:
    """Un fichier XML du dump, ramené à une ligne d'index. ``None`` s'il n'est
    ni un texte ni un article (sommaires, structures, liens ELI…)."""
    if "<TEXTE_VERSION>" in xml:
        ident = _champ("ID", xml)
        date = _champ("DATE_PUBLI", xml) if ident.startswith("JORF") else _champ("DATE_DEBUT", xml)
        fin = "" if ident.startswith("JORF") else _champ("DATE_FIN", xml)
        titre = _champ("TITREFULL", xml) or _champ("TITRE", xml)
        corps = xml.split("</META>", 1)[-1]
        doc = Document(ident, date, fin, _champ("NATURE", xml), "", titre, _texte(corps))
        if ident.startswith("KALI"):
            doc.etat, doc.cid = _champ("ETAT", xml), _champ("CID", xml) or ident
        return doc
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
        doc = Document(ident, date, fin, nature.strip(), _champ("NUM", xml), titre, _texte(corps))
        if ident.startswith("KALI"):
            doc.etat = _champ("ETAT", xml)
            doc.cid = _attribut("TEXTE", "cid", xml)
            doc.idcc = _attribut("CONTENEUR", "num", xml)
            doc.convention = _attribut("CONTENEUR", "titre", xml)
        return doc
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


#: LEGI se lit aussi article par article, par le titre du texte et le numéro
#: (``scripts/textes.py``) : sans cet index SQL, chaque lecture parcourt la
#: table entière. Le JORF, qui ne se lit que par requête ou par identifiant,
#: s'en passe.
ARTICLES_DE_LEGI = "CREATE INDEX IF NOT EXISTS doc_titre_num ON doc(titre, num);"


#: Ce qu'un document de KALI porte de plus que ceux du JORF et de LEGI : son
#: état, où se lit qu'il est étendu ou non ; le texte qui porte l'article
#: (``cid``), parce qu'un titre y couvre souvent plusieurs textes et qu'un
#: numéro s'y répète de l'un à l'autre ; sa convention, par son numéro (IDCC)
#: et son titre. Quatre colonnes que seul l'index de KALI reçoit : ceux du JORF
#: et de LEGI gardent les sept leurs.
PROPRES_A_KALI = ("etat", "cid", "idcc", "convention")

#: L'histoire d'un article de KALI se lit dans son texte.
ARTICLES_DE_KALI = "CREATE INDEX IF NOT EXISTS doc_cid_num ON doc(cid, num);"


def colonnes(db: sqlite3.Connection) -> list[str]:
    return [ligne[1] for ligne in db.execute("PRAGMA table_info(doc)")]


def ouvrir(chemin: Path, base: str = "") -> sqlite3.Connection:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(chemin)
    db.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;" + SCHEMA
                     + (ARTICLES_DE_LEGI if base == "legi" else ""))
    if base == "kali":
        for colonne in PROPRES_A_KALI:
            if colonne not in colonnes(db):
                db.execute(f"ALTER TABLE doc ADD COLUMN {colonne} TEXT")
        db.executescript(ARTICLES_DE_KALI)
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
    champs = colonnes(db)
    verser = (f"INSERT OR IGNORE INTO doc ({', '.join(champs)}) "
              f"VALUES ({','.join('?' * len(champs))})")
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
        lot.append(tuple(getattr(doc, champ) for champ in champs))
        gardes += 1
        if len(lot) >= 2000:
            db.executemany(verser, lot)
            lot = []
    db.executemany(verser, lot)
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
    commande = ["curl", "-sSf", "-L", "--retry", "5", "--retry-delay", "5",
                "-C", "-", "--max-time", "14400", "-o", str(partiel), url]
    resultat = subprocess.run(commande, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    if resultat.returncode != 0:
        if "404" in resultat.stderr:      # rien à reprendre : la page n'existe pas
            partiel.unlink(missing_ok=True)
        raise RuntimeError(f"téléchargement en échec ({resultat.stderr.strip()}) : {url}")
    partiel.rename(cible)
    return cible


def precharger(base: str, noms: list[str], travailleurs: int = 8) -> None:
    """Télécharge des incréments en parallèle : chacun ne fait que cent à deux
    cents Ko, et c'est la latence d'une requête, non le débit, qui coûte."""
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(travailleurs) as pool:
        list(pool.map(lambda nom: telecharger(RACINE + base.upper() + "/" + nom,
                                              CACHE / "increments" / nom), noms))


def verser_archive(db: sqlite3.Connection, archive: Path, tout: bool,
                   remplacer: bool) -> tuple[int, int]:
    """Lit une archive tar.gz de la DILA et verse ses documents dans la base.

    Le dump global (plusieurs Go) passe par ``tar -xzO`` en flux, sans jamais
    être extrait sur disque. Un incrément, petit, est lu par ``tarfile`` pour
    y trouver aussi la liste de suppression.
    """
    if not remplacer:
        # Le nom NU, depuis le répertoire de l'archive : `tar` lit un argument
        # qui contient un deux-points comme `hôte:chemin`, et un chemin absolu
        # de Windows commence par `C:`. GNU tar répondait « Cannot connect to
        # C: resolve failed » et l'index se construisait vide, sans que rien ne
        # le dise. `--force-local` corrigerait aussi, mais c'est une option GNU
        # que le tar BSD de Windows n'a pas ; se placer à côté du fichier ne
        # demande rien à personne.
        detar = subprocess.Popen(["tar", "-xzO", "-f", archive.name],
                                 cwd=archive.parent,
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        bilan = inserer(db, documents(detar.stdout), tout)
        if detar.wait() != 0:
            # Un dump tronqué se lisait jusqu'à la coupure, en silence.
            raise RuntimeError(f"tar n'a pas lu {archive} jusqu'au bout "
                               f"(code {detar.returncode}) : dump tronqué ou illisible")
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
    tout = tout or bool(BASES[base].get("entiere"))
    if chemin.exists():
        chemin.unlink()
    if archive is None:
        nom = dernier_dump(base)
        print(f"Dump global : {nom}", file=sys.stderr)
        archive = telecharger(RACINE + base.upper() + "/" + nom, CACHE / nom)
    db = ouvrir(chemin, base)
    debut = time.time()
    try:
        lus, gardes = verser_archive(db, archive, tout, remplacer=False)
    except RuntimeError:
        db.close()
        chemin.unlink()
        raise
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
    """Applique les incréments parus depuis le dernier appliqué. Rend leur nombre.

    Quand la DILA a renouvelé son dump après le dernier incrément de l'index,
    rien n'est appliqué : une base ``entiere`` se reconstruit du dump neuf, les
    autres refusent (``RuntimeError``) et laissent l'index tel quel.
    """
    if not chemin.exists():
        raise LookupError(f"{chemin} absent : --recuperer, ou le construire d'abord")
    db = ouvrir(chemin, base)
    depuis = meta(db, "dernier_increment") or ""
    if tout is None:
        tout = meta(db, "filtre") == "tout"
    if depuis:
        dump = dernier_dump(base)
        if horodatage(dump) > depuis:
            # Les incréments parus entre ``depuis`` et ce dump ne sont plus
            # servis : appliquer les suivants laisserait un trou sans le dire.
            db.close()
            if not BASES[base].get("entiere"):
                raise RuntimeError(
                    f"la DILA a renouvelé son dump ({dump}), postérieur à l'index "
                    f"({depuis}) : ce qui a paru entre les deux n'est plus servi, et "
                    "appliquer les incréments suivants laisserait un trou. Rien n'est "
                    "appliqué, l'index reste tel quel. Le reconstruire du dump neuf, une "
                    "heure et plus : sur GitHub, onglet Actions, « Index DILA », « Run "
                    "workflow » en cochant « reconstruire », ce qui le publie ; sur un "
                    f"poste, python scripts/fetch/dila_index.py {base}")
            print(f"dump renouvelé ({dump}), postérieur à l'index ({depuis}) : "
                  "reconstruction", file=sys.stderr)
            construire(base, chemin, tout)
            return 0
    nouveaux = increments(base, depuis)
    print(f"{len(nouveaux)} incréments à appliquer depuis {depuis or 'l’origine'}",
          file=sys.stderr)
    precharger(base, nouveaux)
    for i, nom in enumerate(nouveaux, 1):
        archive = CACHE / "increments" / nom
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

# ---------------------------------------------------------------------------
# Lecture par les récupérateurs
# ---------------------------------------------------------------------------


def ouvrir_lecture(base: str, explicite: str | None = None
                   ) -> tuple[sqlite3.Connection, str]:
    """L'index en lecture seule, et la phrase qui dit jusqu'où il est à jour.

    C'est par ici que les récupérateurs ``dila_legi_*`` et ``jorf_*`` lisent
    désormais la base, au lieu de retélécharger le dump global — que la DILA
    n'a pas régénéré depuis juillet 2025, si bien que le dump seul ignore tout
    ce qui a paru depuis. La phrase rendue va dans le fichier de sortie du
    récupérateur, puis dans le journal de certification : une certification
    l'est à une date, et cette date est celle du dernier incrément appliqué.
    """
    chemin = chemin_index(base, explicite)
    if not chemin.exists():
        raise FileNotFoundError(
            f"{chemin} absent : lancer `python scripts/fetch/dila_index.py {base} "
            "--recuperer`, puis `--mettre-a-jour`")
    db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    source = (f"index {base.upper()} du dépôt : {meta(db, 'dump') or '?'}, "
              f"incréments appliqués jusqu'au {meta(db, 'dernier_increment') or '?'}")
    return db, source


def parcourir(db: sqlite3.Connection, titre: str | None = None,
              nature: str | None = None) -> Iterator[Document]:
    """Les documents de l'index, un par un, dans l'ordre de leur date.

    ``titre`` et ``nature`` sont des motifs SQL ``LIKE`` qui restreignent le
    parcours ; sans eux, c'est toute la base — quelques secondes. Le texte
    rendu est le corps seul : les récupérateurs qui cherchaient le numéro du
    décret dans les six cents premiers caractères du dump — où les
    métadonnées précédaient le corps — lisent ``titre`` à part, ou le
    recollent devant (``texte_comme_le_dump``).
    """
    clauses, valeurs = [], []
    if titre:
        clauses.append("titre LIKE ?")
        valeurs.append(titre)
    if nature:
        clauses.append("nature LIKE ?")
        valeurs.append(nature)
    ou = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    requete = ("SELECT id, date, fin, nature, num, titre, texte FROM doc"
               + ou + " ORDER BY date, id")
    for ligne in db.execute(requete, valeurs):
        yield Document(*(champ or "" for champ in ligne))


def texte_comme_le_dump(doc: Document) -> str:
    """Le titre devant le corps, comme le dump dépouillé en flux le donnait.

    Les filtres écrits pour le dump lisaient un XML débarrassé de ses balises,
    où le titre du texte et le numéro de l'article précédaient le corps : les
    motifs qui cherchent « décret n° 91-613 » ou « 2003-775 » en tête de texte
    continuent de porter si on leur rend cet ordre.
    """
    return " ".join(morceau for morceau in (doc.titre, doc.num, doc.texte) if morceau)


def flux_pseudo_xml(db: sqlite3.Connection) -> Iterator[bytes]:
    """L'index rejoué sous la forme que les filtres du dump attendent.

    Les récupérateurs ont chacun un FILTRE, un programme qui lit le dump en
    flux, coupe aux « <?xml », regarde ``<NUM>``, ``<DATE_DEBUT>``,
    ``<DATE_FIN>`` et le texte débarrassé de ses balises, et imprime ce qu'il
    retient. Plutôt que de réécrire chaque filtre pour l'index, on lui rend un
    flux de la même forme : un document par « <?xml », les mêmes balises, le
    titre devant le corps comme dans le dump. Le filtre ne voit pas la
    différence, et la certification non plus.
    """
    for doc in parcourir(db):
        article = doc.nature.startswith("Article")
        if article:
            # La forme d'un article dans le dump, balises ôtées : « Article 3
            # MODIFIE 1955-01-21 1962-01-01 AUTONOME Décret n°47-1846 … » —
            # certains filtres lisent cet ordre-là.
            etat = "VIGUEUR" if doc.fin in ("", "2999-01-01") else "MODIFIE"
            meta = (f"<ORIGINE>LEGI</ORIGINE><NATURE>Article</NATURE>"
                    f"<NUM>{doc.num}</NUM><ETAT>{etat}</ETAT>"
                    f"<DATE_DEBUT>{doc.date}</DATE_DEBUT><DATE_FIN>{doc.fin}</DATE_FIN>"
                    f"<TYPE>AUTONOME</TYPE><TITRE_TXT>{doc.titre}</TITRE_TXT>")
        else:
            meta = (f"<NATURE>{doc.nature}</NATURE>"
                    f"<DATE_DEBUT>{doc.date}</DATE_DEBUT><DATE_FIN>{doc.fin}</DATE_FIN>"
                    f"<DATE_PUBLI>{doc.date}</DATE_PUBLI><NUM></NUM>"
                    f"<TITRE>{doc.titre}</TITRE><TITREFULL>{doc.titre}</TITREFULL>")
        yield (
            f'<?xml version="1.0"?><DOC><ID>{doc.id}</ID>{meta}'
            f"<CONTENU>{doc.texte}</CONTENU></DOC>\n"
        ).encode("utf-8", errors="replace")


def filtrer_index(base: str, filtre: str, explicite: str | None = None
                  ) -> tuple[str, str]:
    """Fait passer l'index par un FILTRE écrit pour le dump.

    Rend ce que le filtre a imprimé — à dépouiller exactement comme la sortie
    du dump — et la phrase qui dit jusqu'où l'index est à jour, à écrire dans
    le fichier de sortie du récupérateur.
    """
    import threading

    db, source = ouvrir_lecture(base, explicite)
    sonde = subprocess.Popen([sys.executable, "-X", "utf8", "-c", filtre],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # SQLite ne se lit que du fil qui l'a ouvert : c'est donc ce fil-ci qui
    # alimente le filtre, et un second qui recueille ce qu'il imprime.
    recueilli: list[bytes] = []
    lecteur = threading.Thread(target=lambda: recueilli.append(sonde.stdout.read()),
                               daemon=True)
    lecteur.start()
    try:
        for morceau in flux_pseudo_xml(db):
            sonde.stdin.write(morceau)
        # Les filtres coupent aux « <?xml » et gardent le dernier morceau en
        # attente du suivant : sans un « <?xml » de clôture, le dernier
        # document du flux ne serait jamais lu.
        sonde.stdin.write(b'<?xml version="1.0"?>\n')
    except BrokenPipeError:
        pass
    finally:
        sonde.stdin.close()
    sonde.wait()
    lecteur.join()
    db.close()
    sortie = b"".join(recueilli).decode("utf-8", errors="replace")
    if sonde.returncode != 0:
        raise RuntimeError(f"le filtre a échoué (code {sonde.returncode})")
    return sortie, source


def url_publiee(base: str) -> str:
    return f"https://github.com/{DEPOT}/releases/download/{ETIQUETTE}/{base}.sqlite.gz"


def recuperer(base: str, chemin: Path) -> None:
    """L'index publié, décompressé sur place."""
    try:
        comprime = telecharger(url_publiee(base), CACHE / f"{base}.sqlite.gz")
    except RuntimeError as erreur:
        if "404" in str(erreur):
            raise LookupError(
                f"aucun index {base} publié sur la release {ETIQUETTE} : le construire "
                f"(dila_index.py {base}, une demi-heure de téléchargement puis une "
                "heure et demie), ou demander sa publication") from erreur
        raise
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(comprime, "rb") as source, chemin.open("wb") as cible:
        shutil.copyfileobj(source, cible, 1 << 22)
    comprime.unlink()
    db = ouvrir(chemin, base)
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
    db = ouvrir(chemin, base)
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
    # Les bases publient en même temps, chacune sa ligne du même texte : il se
    # relit après l'envoi, pour ne pas y remettre la ligne périmée d'une autre.
    release = _github("GET", f"{api}/releases/tags/{ETIQUETTE}", jeton)
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
