#!/usr/bin/env python3
"""Le chaînage : chaque durée d'échelon et chaque reclassement rattaché à la
grille, au corps et à la période qu'il régit, ou déclaré, avec sa raison.

    python scripts/fetch/dila_index.py legi --recuperer   # l'index, une fois
    python scripts/fetch/dila_legi_chainage.py            # une minute

CE QUI EST À RELIER. Les durées d'échelon (``grilles/durees/``) et les
reclassements (``grilles/reclassements/``) sont écrits dans les statuts, qui
nomment leurs grades par leur libellé (« Ingénieur hors classe »). Les grilles
du dépôt sont ailleurs : celles du LEGI (``grilles/<versant>/``) dans les
textes d'échelonnement, une par groupe d'un texte ; celles de l'État depuis le
Noyau RH du CISIRH (``grilles/etat/``), où un corps a ses grades et chaque
version de grade sa grille. Le chaînage ne lit aucune durée ni aucun indice :
il dit, pour chaque grade de chaque tableau, quelle grille il régit, de quel
corps, et pendant quelle période.

CE QUI PROUVE UN RATTACHEMENT D'UNE DURÉE. Rien ne se rattache sur le seul
libellé : la même « Ingénieur de recherche hors classe » est le grade de deux
corps, celui de 1985 et celui de l'agriculture, que le décret n° 2017-171,
commun à divers corps, vise tous deux. Il faut, à la fois :

- *Un texte qui relie le statut à la grille.* Au LEGI : le texte
  d'échelonnement vise le statut par son numéro (« Vu le décret
  n° 2016-201 […] ») ; et, soit il ne vise, parmi les décrets statutaires,
  que ce statut-là (lien ``visa`` ; le décret qui l'a modifié, « modifié par
  le décret n° … », n'en est pas un second), soit l'article qui fixe la grille
  le nomme, à chacune de ses versions en vigueur sur la période, par son
  numéro, ou par sa date quand aucun autre décret de ses visas n'a la même
  (lien ``article``). Au Noyau RH : le corps, ou l'un de ses grades, cite le
  statut parmi ses textes, par des versions qui couvrent la période (lien
  ``noyau``) ; corps et grades se lisent chacun dans son fichier.
- *Le même grade.* Le libellé du tableau et celui de la grille, ou du grade du
  noyau, sont égaux après ``normaliser`` : sans accents, ni casse, ni
  ponctuation, au singulier, sans le « (article N) » que le lecteur des
  grilles ajoute, et, au noyau, sans « de l'État ».
- *Une période commune*, l'intersection de celle du tableau (fin exclue) et
  de celle de la grille ou du grade (fin incluse).
- *Les mêmes échelons* : les rangs que le tableau écrit sont ceux que la
  grille a pendant la période, stagiaire et élève (rang zéro) mis à part.
  Au noyau, dont le rang ordonne sans numéroter (``Depot._renumeroter``),
  c'est leur nombre, élève, stagiaire et échelons provisoires mis à part.
- *Une seule grille à la fois* pour un grade d'un tableau, et un seul corps
  au noyau.

Ce qui manque à l'une de ces conditions est déclaré, avec la plus avancée des
raisons rencontrées, et les candidats qu'elle écarte. Deux versions d'un même
article que le LEGI fait valoir ensemble (colonne ``chevauche`` des tableaux)
ne se rattachent pas sur leur recouvrement : le chaînage ne choisit pas.

CE QUI PROUVE UN RATTACHEMENT D'UN RECLASSEMENT. À l'État seulement, par le
Noyau RH : la date du reclassement est celle que le lecteur a lue (``effet``),
ou celle qui ouvre la phrase (« Au 1er juillet 2011, les membres […] ») ; le
corps est l'un de ceux que le noyau rattache, la veille ou le jour, au statut
que la phrase nomme (``statuts_de_la_phrase``) : par son numéro, par sa date
quand les visas la résolvent en un seul décret identifié au LEGI ou par son
NOR, ou le texte du tableau quand il est lui-même ce statut ; jamais tous les
corps d'un décret qui en modifie plusieurs (relecture R-B3 : les géomètres de
l'IGN, nommés par « le décret du 20 janvier 1967 », rattachés aux
géomètres-cadastreurs) ; le libellé du tableau, où l'aplatissement colle
le grade d'origine et le grade d'accueil, se coupe en deux libellés de grades
de ce corps (ou des corps qu'il absorbe), en vigueur la veille et le jour du
reclassement, une seule coupe possible ; chaque échelon d'origine et d'accueil
est dans sa grille, à sa place et de sa nature (``rang_dans_la_grille`` : le
spécial ou l'exceptionnel est l'exceptionnel de la grille, à son rang, que
``rangs_grille`` écrit). Ailleurs, les grilles ne sont qu'au LEGI,
dont les libellés ne se coupent pas sans deviner : déclaré.

CE QU'IL ÉCRIT, sous ``data/reference/grilles/chainage/`` : ``durees.csv``,
``reclassements.csv``, et ``a_lire_au_jorf.csv``, les textes dont un tableau
de durées ou de reclassement est abîmé au LEGI ou y manque — ce qu'une
lecture à la main au Journal officiel viserait, sans rien en lire ici.
"""

from __future__ import annotations

import argparse
import collections
import csv
import re
import sqlite3
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
GRILLES = RACINE / "data" / "reference" / "grilles"
SORTIE = GRILLES / "chainage"
INDEX = RACINE / "data" / "brut" / "dila" / "legi.sqlite"
VERSANTS_LEGI = ("etat_legi", "territoriale", "hospitaliere", "militaires")
OUVERT = "9999-12-31"
SOURCE_ID = ("# source_id: dila_legi_chainage — les fichiers de grilles/ du dépôt et les visas "
             "et articles de l'index LEGI (scripts/fetch/dila_index.py) ; "
             "scripts/fetch/dila_legi_chainage.py")

# ---------------------------------------------------------------------------
# Les règles
# ---------------------------------------------------------------------------

MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre")
_MOIS = r"janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre"
_DATE = rf"(?P<jour>1\s*er|\d{{1,2}})\s+(?P<mois>{_MOIS})\s+(?P<annee>\d{{4}})"
DATE_EN_TETE = re.compile(
    rf"^\s*(?:[IVX]+\s*\.?\s*[-–]\s*)?(?:au|[àa]\s+compter\s+du|[àa]\s+partir\s+du)\s+{_DATE}\s*,",
    re.IGNORECASE)
NUMERO = re.compile(r"n[°o]\s*(\d{2,4}-\d{1,4})(?![\d-])")
VISA = re.compile(r"\bVu\s[^;]*")
FIN_DE_VISA = re.compile(r"\s+(?:Le Conseil d.[ÉE]tat|Fait à|D[ée]cr[èe]te|Arr[êe]te)\b")
STATUTAIRE = re.compile(r"statuts?\s+particuliers?|dispositions\s+statutaires|portant\s+statut"
                        r"|relatif\s+au\s+statut|organisation\s+des\s+carri", re.IGNORECASE)


def _sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texte)
                   if not unicodedata.combining(c))


def normaliser(libelle: str) -> str:
    """Le libellé d'un grade, comparable : sans accents, ni casse, ni
    ponctuation, chaque mot au singulier (« principaux » → « principal »,
    « techniques » → « technique »), sans le « (article N) » que le lecteur
    des grilles ajoute pour distinguer deux grilles du même nom."""
    texte = re.sub(r"\s*\(article\s+\d+\)\s*$", "", libelle.strip())
    mots = re.sub(r"[^a-z0-9]+", " ", _sans_accents(texte).lower()).split()
    singulier = []
    for mot in mots:
        if len(mot) > 4 and mot.endswith("aux"):
            mot = mot[:-3] + "al"
        elif len(mot) > 3 and mot[-1] in "sx":
            mot = mot[:-1]
        singulier.append(mot)
    return " ".join(singulier)


def normaliser_noyau(libelle: str) -> str:
    """Au noyau, les grades portent souvent « de l'État », que le statut
    n'écrit pas."""
    return re.sub(r"\s+", " ", re.sub(r"\b(?:de l|d) etat\b", " ", normaliser(libelle))).strip()


def _date_en_lettres(iso: str) -> str:
    annee, mois, jour = (int(x) for x in iso.split("-"))
    premier = r"1\s*er" if jour == 1 else str(jour)
    return rf"{premier}\s+{MOIS[mois - 1]}\s+{annee}"


def nomme(texte: str, numero: str, signature: str) -> str:
    """« numero » si le texte nomme le statut par son numéro, « date » par sa
    date (« le décret du 1er août 1990 »), rien sinon."""
    if numero and re.search(rf"n[°o]\s*{re.escape(numero)}(?![\d-])", texte):
        return "numero"
    if signature and re.search(rf"\bd[ée]cret\s+(?:n[°o]\s*[\d-]+\s+)?du\s+"
                               rf"{_date_en_lettres(signature)}\b", texte, re.IGNORECASE):
        return "date"
    return ""


def _date_en_lettres_souple(iso: str) -> str:
    """La date en lettres, le premier du mois écrit « 1er » ou « 1 » (les
    titres du LEGI écrivent « Décret n°90-680 du 1 août 1990 »), les accents
    facultatifs."""
    annee, mois, jour = (int(x) for x in iso.split("-"))
    nom = _MOIS.split("|")[mois - 1]
    return rf"{r'1(?:\s*er)?' if jour == 1 else jour}\s+{nom}\s+{annee}"


def decrets_de_la_date(visas: list[str], iso: str) -> set[str]:
    """Les numéros des décrets que les visas portent à cette date : « Vu le
    décret n° 67-91 du 20 janvier 1967 […] » ; le numéro est celui qui précède
    la date, non celui du décret qui a modifié le statut (« modifié par le
    décret n° 2000-972 du 28 septembre 2000 »)."""
    motif = re.compile(rf"\bd[ée]cret\s+n[°o]\s*(\d{{2,4}}-\d{{1,4}})\s+du\s+"
                       rf"{_date_en_lettres_souple(iso)}(?!\d)", re.IGNORECASE)
    return {n for v in visas for n in motif.findall(v)}


def date_de_la_phrase(intro: str) -> str:
    """La date qui ouvre la phrase d'un reclassement (« Au 1er juillet 2011, »),
    ou rien : une date au milieu de la phrase est celle d'un texte cité."""
    trouve = DATE_EN_TETE.search(intro)
    if not trouve:
        return ""
    return _iso(trouve)


def _iso(trouve: re.Match) -> str:
    """La date ISO d'une date en lettres reconnue par ``_DATE``."""
    jour = 1 if re.match(r"1\s*er", trouve.group("jour")) else int(trouve.group("jour"))
    mois = [_sans_accents(m) for m in MOIS].index(_sans_accents(trouve.group("mois").lower())) + 1
    return date(int(trouve.group("annee")), mois, jour).isoformat()


def lendemain(iso: str) -> str:
    return OUVERT if not iso or iso >= OUVERT else (date.fromisoformat(iso) + timedelta(days=1)).isoformat()


def veille(iso: str) -> str:
    return (date.fromisoformat(iso) - timedelta(days=1)).isoformat()


def intersection(debut: str, fin_exclue: str, debut2: str, fin_incluse2: str):
    """[debut, fin_exclue) ∩ [debut2, fin_incluse2] ; vide : ouvert."""
    d, f = max(debut, debut2), min(fin_exclue or OUVERT, lendemain(fin_incluse2))
    return (d, f) if d < f else None


def en_vigueur(ligne: dict, jour: str) -> bool:
    return ligne["debut"] <= jour and (not ligne["fin"] or jour <= ligne["fin"])


# ---------------------------------------------------------------------------
# Les données
# ---------------------------------------------------------------------------

def lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.startswith("#")))


class Index:
    """Les visas et les articles, lus dans l'index LEGI."""

    def __init__(self, chemin: Path):
        if not Path(chemin).exists():
            raise FileNotFoundError(f"{chemin} : `python scripts/fetch/dila_index.py legi --recuperer`")
        self.db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
        self._textes: dict[str, str] = {}

    def texte(self, ident: str) -> str:
        if ident not in self._textes:
            ligne = self.db.execute("SELECT texte FROM doc WHERE id = ?", (ident,)).fetchone()
            self._textes[ident] = (ligne[0] or "") if ligne else ""
        return self._textes[ident]

    def visas(self, texte: str) -> list[str]:
        return [FIN_DE_VISA.split(v)[0].strip(" ,") for v in VISA.findall(self.texte(texte))]

    def versions_sur(self, article: str, debut: str, fin: str) -> list[str]:
        """Les versions de l'article (même texte, même numéro d'article, comme
        les relie le lecteur des grilles) en vigueur sur [debut, fin) : la fin
        d'une version au LEGI est le début de la suivante ; une version datée
        d'une fin antérieure ou égale à son début n'a jamais été en vigueur."""
        if not hasattr(self, "_versions"):
            self._versions: dict[tuple, list[tuple[str, str, str]]] = collections.defaultdict(list)
            self._article: dict[str, tuple] = {}
            for ident, d, f, num, titre in self.db.execute(
                    "SELECT id, date, fin, num, titre FROM doc "
                    "WHERE id >= 'LEGIARTI' AND id < 'LEGIARTJ'"):
                self._article[ident] = (titre, num)
                if d and f and d < f:
                    self._versions[(titre, num)].append((ident, d, f))
        cle = self._article.get(article)
        return sorted(i for i, d, f in self._versions.get(cle, [])
                      if d < (fin or OUVERT) and f > debut)

    def notices_du_decret(self, numero: str, iso: str) -> list[tuple[str, str]]:
        """Les notices LEGITEXT dont le titre est celui de ce décret : « Décret
        n° 67-91 du 20 janvier 1967 […] » (le LEGI en garde parfois deux, avant
        et après un changement de titre)."""
        if not hasattr(self, "_decrets"):
            self._decrets: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
            titre = re.compile(r"^\s*D[ée]cret\s+n[°o]\s*(\d{2,4}-\d{1,4})\s+du\s+", re.IGNORECASE)
            for ident, libelle in self.db.execute(
                    "SELECT id, titre FROM doc WHERE id >= 'LEGITEXT' AND id < 'LEGITEXU'"):
                trouve = titre.match(libelle or "")
                if trouve:
                    self._decrets[trouve.group(1)].append((ident, libelle))
        date_du_titre = re.compile(rf"^\s*D[ée]cret\s+n[°o]\s*{re.escape(numero)}\s+du\s+"
                                   rf"{_date_en_lettres_souple(iso)}(?!\d)", re.IGNORECASE)
        return sorted((i, t) for i, t in self._decrets.get(numero, []) if date_du_titre.match(t))

    def source(self) -> str:
        meta = dict(self.db.execute("SELECT cle, valeur FROM meta").fetchall())
        return f"{meta.get('dump', '?')}, à jour au {meta.get('dernier_increment', '?')}"


#: Les décrets qui ont modifié le statut visé : « modifié par le décret n° 2000-972
#: du 28 septembre 2000 », « modifié par les décrets n° 96-60 du 24 janvier 1996,
#: n° 98-936 […] et n° 2003-695 […] », « modifié en dernier lieu par … ».
MODIFIE_PAR = re.compile(
    r"modifi[ée]e?s?\s+(?:en\s+dernier\s+lieu\s+)?par\s+(?:le|les)\s+d[ée]crets?\s+"
    r"((?:n[°o]\s*\d{2,4}-\d{1,4}(?![\d-])(?:\s+du\s+(?:1\s*er|\d{1,2})\s+\S+\s+\d{4})?"
    r"(?:\s*,\s*|\s+et\s+(?:par\s+)?(?:le\s+d[ée]cret\s+)?)?)+)", re.IGNORECASE)


def _visas_statutaires(visas: list[str]) -> set[str]:
    """Les numéros des décrets statutaires qu'un texte vise ; ni les lois, ni
    les décrets de rémunération, ni ceux qui ont modifié le statut visé (« Vu
    le décret n° 90-973 […], modifié par le décret n° 2000-972 […] » ne vise
    qu'un statut : relecture R-B3, point 2)."""
    numeros = set()
    for v in visas:
        if re.match(r"Vu\s+(?:le|les)\s+d[ée]crets?\b", v) and STATUTAIRE.search(v):
            modificatifs = {n for m in MODIFIE_PAR.finditer(v) for n in NUMERO.findall(m.group(1))}
            numeros |= set(NUMERO.findall(v)) - modificatifs
    return numeros


class Depot:
    def __init__(self, index: Index):
        self.index = index
        self.durees_textes = {t["texte"]: t for t in lire(GRILLES / "durees" / "textes.csv")}
        self.durees_tableaux = lire(GRILLES / "durees" / "tableaux.csv")
        self.durees_lignes = lire(GRILLES / "durees" / "lignes.csv")
        self.reclassements_textes = {t["texte"]: t for t in
                                     lire(GRILLES / "reclassements" / "textes.csv")}
        self.reclassements_tableaux = lire(GRILLES / "reclassements" / "tableaux.csv")
        self.reclassements_lignes = lire(GRILLES / "reclassements" / "lignes.csv")
        # Les grilles du LEGI, et les textes d'échelonnement qui visent chaque numéro.
        self.grilles_du_texte: dict[str, list[tuple[str, dict]]] = collections.defaultdict(list)
        self.echelons: dict[tuple, list[dict]] = collections.defaultdict(list)
        self.visant: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
        self.visas: dict[str, list[str]] = {}
        for versant in VERSANTS_LEGI:
            for grille in lire(GRILLES / versant / "grilles.csv"):
                self.grilles_du_texte[grille["texte"]].append((versant, grille))
            for echelon in lire(GRILLES / versant / "echelons.csv"):
                self.echelons[(versant, echelon["texte"], echelon["grille"])].append(echelon)
            for texte in lire(GRILLES / versant / "textes.csv"):
                visas = index.visas(texte["texte"])
                self.visas[texte["texte"]] = visas
                for visa in visas:
                    for numero in NUMERO.findall(visa):
                        self.visant[numero].append((texte["texte"], visa))
        # Le noyau : les corps qui citent chaque numéro de texte.
        self.noyau_textes = {t["texte"]: t for t in lire(GRILLES / "etat" / "textes.csv")}
        self.noyau_corps = collections.defaultdict(list)
        for corps in lire(GRILLES / "etat" / "corps.csv"):
            self.noyau_corps[corps["corps"]].append(corps)
        self.noyau_grades = collections.defaultdict(list)
        for grade in lire(GRILLES / "etat" / "grades.csv"):
            self.noyau_grades[grade["corps"]].append(grade)
        self.noyau_echelons = collections.defaultdict(list)
        for echelon in lire(GRILLES / "etat" / "echelons.csv"):
            self.noyau_echelons[echelon["grille"]].append(echelon)
        # Qui cite chaque numéro de texte, et quand : une version de corps
        # (`corps.csv`) ou une version de l'un de ses grades (`grades.csv`), avec
        # ses dates. Les deux fichiers se lisent l'un après l'autre : réunis en un
        # dictionnaire indexé par le code du corps, les grades écrasaient le corps
        # (relecture R-B3, point 1 d).
        self.citations: dict[str, dict[str, list[dict]]] = collections.defaultdict(
            lambda: collections.defaultdict(list))
        for versions, qui in ((self.noyau_corps, lambda v: f"le corps {v['corps']}"),
                              (self.noyau_grades,
                               lambda v: f"le grade {v['grade']} du corps {v['corps']}")):
            for liste in versions.values():
                for version in liste:
                    for reference in version["textes"].split():
                        ident = reference.split(":")[0]
                        numero = self.noyau_textes.get(ident, {}).get("numero", "")
                        if numero:
                            self.citations[numero][version["corps"]].append(
                                {"qui": qui(version), "texte": ident, "debut": version["debut"],
                                 "fin": version["fin"]})
        self.corps_citant: dict[str, dict[str, str]] = {
            numero: {c: liste[0]["texte"] for c, liste in sorted(par_corps.items())}
            for numero, par_corps in self.citations.items()}

    def citations_sur(self, numero: str, corps: str, debut: str, fin: str):
        """Les morceaux de [debut, fin) où une version du corps ou de l'un de ses
        grades cite le n° numero : [(début, fin exclue, citations)]."""
        bouts = sorted(((p, c) for c in self.citations.get(numero, {}).get(corps, [])
                        for p in [intersection(debut, fin, c["debut"], c["fin"])] if p),
                       key=lambda b: (b[0], b[1]["qui"], b[1]["texte"]))
        morceaux: list[list] = []
        for (d, f), c in bouts:
            if morceaux and d <= morceaux[-1][1]:
                morceaux[-1][1] = max(morceaux[-1][1], f)
                morceaux[-1][2].append(c)
            else:
                morceaux.append([d, f, [c]])
        for morceau in morceaux:
            # Le corps d'abord : ses grades ne sont cités que là où il ne cite pas.
            du_corps = [c for c in morceau[2] if c["qui"].startswith("le corps")]
            if du_corps and self._couvre(du_corps, morceau[0], morceau[1]):
                morceau[2] = du_corps
        return [tuple(m) for m in morceaux]

    @staticmethod
    def _couvre(citations: list[dict], debut: str, fin: str) -> bool:
        jour = debut
        for c in sorted(citations, key=lambda c: c["debut"]):
            if c["debut"] <= jour:
                jour = max(jour, lendemain(c["fin"]))
        return jour >= (fin or OUVERT)

    def cite_au(self, numero: str, corps: str, *jours: str) -> list[dict]:
        """Les citations du n° numero par le corps, ou l'un de ses grades, en
        vigueur l'un de ces jours."""
        return [c for c in self.citations.get(numero, {}).get(corps, [])
                if any(en_vigueur(c, j) for j in jours)]

    def preuve_du_noyau(self, citations: list[dict]) -> str:
        """« Noyau RH : le corps 00021 cite le texte 160, « … » (du … au …) »,
        ou « le grade 03762 du corps 00550 cite … » quand seul un grade cite."""
        groupes: dict[tuple, list[dict]] = collections.defaultdict(list)
        for c in citations:
            groupes[(c["qui"], c["texte"])].append(c)
        return " ; ".join(
            f"Noyau RH : {qui} cite le texte {ident}, « {self.noyau_textes[ident]['titre']} » ("
            + ", ".join(sorted({f"du {c['debut']} au {c['fin']}" if c["fin"]
                                else f"depuis le {c['debut']}" for c in liste})) + ")"
            for (qui, ident), liste in sorted(groupes.items(), key=lambda g: (
                not g[0][0].startswith("le corps"), g[0])))

    def rangs_legi(self, versant: str, texte: str, grille: str, debut: str, fin: str) -> set[int]:
        return {int(e["rang"]) for e in self.echelons[(versant, texte, grille)]
                if e["rang"] != "0" and intersection(debut, fin, e["debut"], e["fin"])}

    def articles_legi(self, versant: str, texte: str, grille: str, debut: str, fin: str) -> set[str]:
        return {e["article"] for e in self.echelons[(versant, texte, grille)]
                if e["rang"] != "0" and intersection(debut, fin, e["debut"], e["fin"])}

    def _renumeroter(self, grille: str, garder) -> set[int]:
        """Au noyau, le rang ordonne les échelons sans les numéroter : la
        grille 00422 des gardiens de la paix met au rang 1 un échelon
        provisoire, au 2 l'élève, au 3 le stagiaire, au 4 le 1er échelon. Les
        échelons d'élève, de stagiaire et provisoires mis à part, le n-ième
        rang est donc l'échelon n : ce qui se compare est leur nombre."""
        rangs = sorted({int(e["rang"]) for e in self.noyau_echelons[grille]
                        if e["nature"] not in ("stagiaire", "eleve", "provisoire")
                        and e["rang"] not in ("", "0") and garder(e)})
        return set(range(1, len(rangs) + 1))

    def rangs_noyau(self, grille: str, debut: str, fin: str) -> set[int]:
        return self._renumeroter(grille, lambda e: intersection(debut, fin, e["debut"], e["fin"]))

    def natures_noyau_au(self, grille: str, jour: str) -> list[str]:
        """La nature de chaque échelon de la grille ce jour-là, dans l'ordre du
        rang, élève, stagiaire et provisoires mis à part : la n-ième est celle
        de l'échelon n (vide : ordinaire ; « exceptionnel »)."""
        par_rang = {int(e["rang"]): e["nature"] for e in self.noyau_echelons[grille]
                    if e["nature"] not in ("stagiaire", "eleve", "provisoire")
                    and e["rang"] not in ("", "0") and en_vigueur(e, jour)}
        return [par_rang[r] for r in sorted(par_rang)]


#: Les échelons qu'un tableau de reclassement ne numérote pas : le lecteur les
#: range au-dessus du plus haut échelon écrit de leur côté du tableau.
NON_NUMEROTES = ("special", "exceptionnel")


def rang_dans_la_grille(echelon: str, rang: int, natures: list[str]) -> int | None:
    """Le rang, dans une grille du noyau (``Depot.natures_noyau_au``), de
    l'échelon qu'un tableau écrit : un échelon numéroté garde son numéro, si la
    grille l'a et qu'il n'y est pas l'exceptionnel ; le spécial ou l'exceptionnel
    est l'unique échelon exceptionnel de la grille (le noyau n'a pas de nature
    « spécial »), à son rang, non à celui que le lecteur lui donne : la colonne
    d'accueil des majors de police (n° 2004-1439, art. 23-1) n'écrit pas le
    4e échelon que la grille a (n° 2010-564, art. 5 ; relecture R-B3-bis).
    None : l'échelon n'est pas dans la grille."""
    if echelon in NON_NUMEROTES:
        places = [i for i, nature in enumerate(natures, 1) if nature == "exceptionnel"]
        return places[0] if len(places) == 1 else None
    return rang if 1 <= rang <= len(natures) and natures[rang - 1] != "exceptionnel" else None


# ---------------------------------------------------------------------------
# Les durées
# ---------------------------------------------------------------------------

#: L'ordre des raisons : la plus avancée l'emporte.
ETAPES = ("texte", "libelle", "periode", "statut", "echelons", "unicite")


def _fmt(debut: str, fin: str) -> str:
    return f"du {debut} au {fin}" if fin and fin < OUVERT else f"depuis le {debut}"


def _candidats_legi(depot: Depot, tableau: dict, groupe: str, rangs: set[int]):
    """Les rattachements prouvés par le LEGI, et les raisons des refus."""
    statut = depot.durees_textes[tableau["texte"]]
    numero, signature = statut["numero"], statut["signature"]
    prouves, raisons = [], []
    visants = {} if not numero else {e: v for e, v in depot.visant.get(numero, [])}
    if not visants:
        raisons.append(("texte", "aucun texte de grille du LEGI au dépôt ne vise "
                        + (f"le n° {numero}" if numero else "ce texte, qui n'a pas de numéro")))
        return prouves, raisons
    cle = normaliser(groupe)
    ecartees: list[tuple[str, str, str, str, str]] = []
    for e, visa in sorted(visants.items()):
        statutaires = _visas_statutaires(depot.visas[e])
        meme_date = [v for v in depot.visas[e] if signature and nomme(v, "", signature)]
        for versant, grille in depot.grilles_du_texte[e]:
            if not cle or normaliser(grille["libelle"]) != cle:
                continue
            periode = intersection(tableau["debut"], tableau["fin"], grille["debut"], grille["fin"])
            nom = f"{grille['grille']} ({versant}, {e})"
            if not periode:
                raisons.append(("periode", f"la grille {nom} porte ce libellé, mais "
                                + _fmt(grille["debut"], lendemain(grille["fin"]))))
                continue
            debut, fin = periode
            # Chaque version de l'article en vigueur sur la période, non la seule
            # que le fichier des échelons nomme (relecture R-B3, point 1 c).
            articles = {v for a in depot.articles_legi(versant, e, grille["grille"], debut, fin)
                        for v in depot.index.versions_sur(a, debut, fin)}
            par_article = {a: nomme(depot.index.texte(a), numero, signature) for a in articles}
            if articles and all(par_article.values()) and not (
                    "date" in par_article.values() and len(meme_date) > 1):
                lien = "article"
                preuve = (f"{visa} ; l'article qui fixe la grille ("
                          + ", ".join(sorted(articles)) + ") nomme ce statut par "
                          + ("son numéro" if set(par_article.values()) == {"numero"}
                             else "sa date, que nul autre décret de ses visas ne porte"))
            elif statutaires == {numero}:
                lien, preuve = "visa", f"{visa} ; seul décret statutaire que vise {e}"
            else:
                cites = sorted(statutaires)
                raisons.append(("statut", f"le texte {e} vise {len(cites)} décrets statutaires ("
                                + ", ".join(cites[:5]) + (", …" if len(cites) > 5 else "")
                                + f") et l'article de sa grille {grille['grille']} ne nomme pas "
                                f"le n° {numero}"))
                ecartees.append((e, grille["grille"], debut, fin,
                                 f"son article ne nomme pas le n° {numero}"))
                continue
            rangs_grille = depot.rangs_legi(versant, e, grille["grille"], debut, fin)
            if rangs_grille != rangs:
                raisons.append(("echelons", f"les échelons diffèrent : le tableau a les rangs "
                                f"{sorted(rangs)}, la grille {nom} {sorted(rangs_grille)}"))
                ecartees.append((e, grille["grille"], debut, fin,
                                 f"ses échelons {sorted(rangs_grille)} ne sont pas ceux du "
                                 f"tableau {sorted(rangs)}"))
                continue
            prouves.append({"source": versant, "texte_grille": e, "grille": grille["grille"],
                            "libelle_grille": grille["libelle"], "corps": "", "grade": "",
                            "debut": debut, "fin": fin, "lien": lien, "preuve": preuve})
    # Deux grilles du même nom dans un texte : la preuve dit pourquoi l'autre
    # est écartée (relecture R-B3, point 1 c).
    for p in prouves:
        autres = [f"la grille {g} {_fmt(d, f)}, écartée : {pourquoi}"
                  for e, g, d, f, pourquoi in ecartees
                  if e == p["texte_grille"] and d < (p["fin"] or OUVERT) and p["debut"] < (f or OUVERT)]
        if autres:
            p["preuve"] += (f" ; {p['texte_grille']} a aussi, du même libellé, "
                            + " ; ".join(autres))
    if not prouves and not raisons:
        raisons.append(("libelle", f"aucune grille des {len(visants)} textes du LEGI qui visent "
                        f"le n° {numero} ne porte ce libellé"))
    return prouves, raisons


def _candidats_noyau(depot: Depot, tableau: dict, groupe: str, rangs: set[int]):
    statut = depot.durees_textes[tableau["texte"]]
    numero = statut["numero"]
    prouves, raisons = [], []
    if statut["versant"] not in ("etat", "plusieurs"):
        return prouves, raisons
    corps_cites = depot.corps_citant.get(numero, {}) if numero else {}
    if not corps_cites:
        raisons.append(("texte", "le Noyau RH ne cite "
                        + (f"le n° {numero}" if numero else "ce texte") + " pour aucun corps"))
        return prouves, raisons
    cle = normaliser_noyau(groupe)
    trouves = []
    for corps, ident in sorted(corps_cites.items()):
        for grade in depot.noyau_grades[corps]:
            if not cle or normaliser_noyau(grade["libelle"]) != cle:
                continue
            periode = intersection(tableau["debut"], tableau["fin"], grade["debut"], grade["fin"])
            if not periode:
                raisons.append(("periode", f"le grade {grade['grade']} du corps {corps} porte ce "
                                "libellé, mais " + _fmt(grade["debut"], lendemain(grade["fin"]))))
                continue
            trouves.append((corps, ident, grade, periode))
    if not trouves:
        if not raisons:
            raisons.append(("libelle", "aucun grade des corps du Noyau RH qui citent le n° "
                            f"{numero} ({', '.join(sorted(corps_cites))}) ne porte ce libellé"))
        return prouves, raisons
    corps_trouves = {t[0] for t in trouves}
    if len(corps_trouves) > 1:
        raisons.append(("unicite", "plusieurs corps du Noyau RH ont ce grade aux mêmes dates : "
                        + ", ".join(sorted(corps_trouves))))
        return prouves, raisons
    for corps, ident, grade, periode in trouves:
        morceaux = depot.citations_sur(numero, corps, *periode)
        if not morceaux:
            raisons.append(("periode", f"le grade {grade['grade']} du corps {corps} porte ce "
                            f"libellé {_fmt(*periode)}, mais le Noyau RH n'y cite le n° {numero} "
                            "ni pour le corps ni pour l'un de ses grades"))
            continue
        for debut, fin, citations in morceaux:
            rangs_grille = depot.rangs_noyau(grade["grille"], debut, fin)
            if rangs_grille != rangs:
                raisons.append(("echelons", f"les échelons diffèrent : le tableau a les rangs "
                                f"{sorted(rangs)}, la grille {grade['grille']} du noyau "
                                f"{sorted(rangs_grille)} {_fmt(debut, fin)}"))
                continue
            prouves.append({"source": "etat", "texte_grille": "", "grille": grade["grille"],
                            "libelle_grille": grade["libelle"], "corps": corps,
                            "grade": grade["grade"], "debut": debut, "fin": fin, "lien": "noyau",
                            "preuve": depot.preuve_du_noyau(citations)})
    return prouves, raisons


def _fusionner(lignes: list[dict]) -> list[dict]:
    """Deux périodes qui se suivent pour la même grille n'en font qu'une."""
    lignes = sorted(lignes, key=lambda l: (l["source"], l["texte_grille"], l["grille"],
                                           l["grade"], l["debut"]))
    sortie: list[dict] = []
    for ligne in lignes:
        avant = sortie[-1] if sortie else None
        if avant and all(avant[c] == ligne[c] for c in ("source", "texte_grille", "grille",
                                                        "grade", "corps", "lien")) \
                and avant["fin"] == ligne["debut"]:
            avant["fin"] = ligne["fin"]
            if ligne["preuve"] not in avant["preuve"]:
                avant["preuve"] += " ; puis " + ligne["preuve"]
        else:
            sortie.append(dict(ligne))
    return sortie


def _se_chevauchent(lignes: list[dict]) -> bool:
    legi = sorted((l for l in lignes if l["source"] != "etat"), key=lambda l: l["debut"])
    return any(b["debut"] < a["fin"] for a, b in zip(legi, legi[1:]))


def chainer_durees(depot: Depot) -> list[dict]:
    rangs: dict[tuple, set[int]] = collections.defaultdict(set)
    ordre: list[tuple] = []
    for ligne in depot.durees_lignes:
        cle = (ligne["texte"], ligne["article"], ligne["tableau"], ligne["groupe"])
        if cle not in rangs:
            ordre.append(cle)
        if ligne["rang"] != "0":
            rangs[cle].add(int(ligne["rang"]))
    tableaux = {(t["texte"], t["article"], t["tableau"]): t for t in depot.durees_tableaux}
    par_article = {(t["article"], t["tableau"]): t for t in depot.durees_tableaux}
    sortie = []
    for cle in ordre:
        tableau = tableaux[cle[:3]]
        base = {"texte": cle[0], "article": cle[1], "tableau": cle[2], "groupe": cle[3]}
        if not cle[3].strip():
            sortie.append({**base, "debut": tableau["debut"], "fin": tableau["fin"],
                           "statut": "declare",
                           "raison": "le tableau ne nomme pas le grade de ses lignes (groupe vide)"})
            continue
        legi, raisons = _candidats_legi(depot, tableau, cle[3], rangs[cle])
        noyau, raisons_noyau = _candidats_noyau(depot, tableau, cle[3], rangs[cle])
        raisons += raisons_noyau
        legi = _fusionner(legi)
        if _se_chevauchent(legi):
            raisons.append(("unicite", "plusieurs grilles du LEGI prouvées aux mêmes dates : "
                            + ", ".join(f"{l['grille']} ({l['texte_grille']})" for l in legi)))
            legi = []
        prouves = legi + _fusionner(noyau)
        if tableau["chevauche"]:
            autre = par_article[(tableau["chevauche"], tableau["tableau"])]
            d = max(tableau["debut"], autre["debut"])
            f = min(tableau["fin"] or OUVERT, autre["fin"] or OUVERT)
            coupes = []
            for p in prouves:
                if p["debut"] < d:
                    coupes.append({**p, "fin": min(p["fin"], d)})
                if p["fin"] > f:
                    coupes.append({**p, "debut": max(p["debut"], f)})
            prouves = coupes
            sortie.append({**base, "debut": d, "fin": "" if f == OUVERT else f,
                           "statut": "declare",
                           "raison": f"deux versions de l'article ({tableau['article']} et "
                                     f"{autre['article']}) valent ensemble aux dates du LEGI, "
                                     f"{_fmt(d, f)} : le chaînage ne choisit pas"})
        for p in prouves:
            sortie.append({**base, **p, "fin": "" if p["fin"] == OUVERT else p["fin"],
                           "statut": "rattache", "raison": ""})
        if not prouves:
            etape = max(ETAPES.index(e) for e, _ in raisons)
            retenues = list(dict.fromkeys(r for e, r in raisons if ETAPES.index(e) == etape))
            raison = " ; ".join(retenues[:3]) + (f" ; et {len(retenues) - 3} autres"
                                                 if len(retenues) > 3 else "")
            sortie.append({**base, "debut": tableau["debut"], "fin": tableau["fin"],
                           "statut": "declare", "raison": raison})
    return sortie


# ---------------------------------------------------------------------------
# Les reclassements
# ---------------------------------------------------------------------------

DECRET_PAR_NUMERO = re.compile(r"\bd[ée]crets?\s+n[°o]\s*(\d{2,4}-\d{1,4})(?![\d-])",
                               re.IGNORECASE)
DECRET_PAR_DATE = re.compile(rf"\bd[ée]cret\s+du\s+{_DATE}", re.IGNORECASE)
RENVOI_NON_RESOLU = re.compile(r"\bd[ée]crets\s+du\b|\bm[êe]me\s+d[ée]cret\b", re.IGNORECASE)
PRESENT_DECRET = re.compile(
    r"\b(?:r[ée]gie?s?|cr[ée]{2}e?s?|institu[ée]e?s?)\s+par\s+(?:les\s+dispositions\s+du\s+"
    r"|le\s+chapitre\s+[IVX\d]+\s+du\s+|le\s+)pr[ée]sent\s+d[ée]cret", re.IGNORECASE)


def est_un_statut(titre: str) -> bool:
    """Le titre d'un décret qui est lui-même un statut (« portant statut
    particulier du corps … »), non d'un décret qui en modifie un (« modifiant le
    décret n° 92-1204 … portant statut particulier … »)."""
    return bool(STATUTAIRE.search(titre)) and not re.search(
        r"\bmodifi|\bportant\s+modification", titre, re.IGNORECASE)


def statuts_de_la_phrase(depot: Depot, tableau: dict) -> tuple[dict[str, str], str]:
    """Les statuts dont relève le corps reclassé, que la phrase qui annonce le
    tableau nomme : par leur numéro (« régi par le décret n° 90-90 ») ; par leur
    date (« régi par le décret du 20 janvier 1967 susvisé »), quand les visas du
    texte la résolvent en un seul décret et que ce décret est identifié, au LEGI
    par sa notice ou au Noyau RH par son NOR ; ou par « le présent décret »,
    quand le texte est lui-même un statut. Une phrase qui ne nomme aucun statut
    vaut pour le texte s'il est un statut, sinon elle ne prouve rien : un décret
    qui modifie plusieurs statuts reclasse des corps dont les grades portent
    les mêmes noms. Rend {numéro : comment la phrase le nomme}, ou la raison de
    déclarer."""
    intro = tableau["intro"]
    texte = depot.reclassements_textes[tableau["texte"]]
    renvoi = RENVOI_NON_RESOLU.search(intro)
    if renvoi:
        return {}, (f"la phrase renvoie à « {renvoi.group(0)} … », que le chaînage ne résout "
                    "pas en un statut")
    nommes = {n: f"la phrase nomme le décret n° {n}" for n in DECRET_PAR_NUMERO.findall(intro)}
    for trouve in DECRET_PAR_DATE.finditer(intro):
        iso = _iso(trouve)
        visas = depot.index.visas(tableau["texte"])
        numeros = decrets_de_la_date(visas, iso)
        if len(numeros) != 1:
            return {}, (f"la phrase nomme le statut par sa date, « {trouve.group(0)} », que les "
                        f"visas de {tableau['texte']} ne résolvent pas en un seul décret ("
                        + (", ".join(sorted(numeros)) or "aucun") + ")")
        (numero,) = numeros
        motif = re.compile(rf"n[°o]\s*{re.escape(numero)}\s+du", re.IGNORECASE)
        (visa,) = [v for v in visas if motif.search(v)][:1]
        notices = depot.index.notices_du_decret(numero, iso)
        nor = sorted({t["nor"] for t in depot.noyau_textes.values()
                      if t["numero"] == numero and t["date"] == iso and t["nor"]})
        if not notices and not nor:
            return {}, (f"la phrase nomme le statut par sa date, « {trouve.group(0)} », que le "
                        f"visa résout en n° {numero}, décret que ni le LEGI ni le Noyau RH "
                        "n'identifient")
        identifie = (f"au LEGI {', '.join(i for i, _ in notices)}, « {notices[0][1]} »"
                     if notices else f"au Noyau RH, NOR {', '.join(nor)}")
        nommes[numero] = (f"la phrase nomme « {trouve.group(0)} » ; le visa de "
                          f"{tableau['texte']} : « {visa} » ; n° {numero}, {identifie}")
    if not nommes or PRESENT_DECRET.search(intro):
        if texte["numero"] and est_un_statut(texte["titre"]):
            nommes[texte["numero"]] = (f"le texte du tableau est le statut : « {texte['titre']} »")
        elif not nommes:
            return {}, (f"la phrase ne nomme pas le statut du corps reclassé, et le texte "
                        f"{'n° ' + texte['numero'] if texte['numero'] else tableau['texte']} n'est "
                        f"pas lui-même un statut : « {texte['titre']} »")
    return nommes, ""


def _corps_du_reclassement(depot: Depot, nommes: dict[str, str],
                           jour: str) -> dict[str, tuple[str, list[dict]]]:
    """Les corps du noyau qui citent un statut nommé la veille ou le jour du
    reclassement, par une version du corps ou de l'un de ses grades :
    {corps : (numéro du statut, citations)}."""
    corps: dict[str, tuple[str, list[dict]]] = {}
    for n in sorted(nommes):
        for c in sorted(depot.citations.get(n, {})):
            citations = depot.cite_au(n, c, veille(jour), jour)
            if citations and c not in corps:
                corps[c] = (n, citations)
    return corps


def chainer_reclassements(depot: Depot) -> list[dict]:
    groupes: dict[tuple, list[dict]] = collections.defaultdict(list)
    for ligne in depot.reclassements_lignes:
        groupes[(ligne["texte"], ligne["article"], ligne["tableau"], ligne["groupe"])].append(ligne)
    tableaux = {(t["texte"], t["article"], t["tableau"]): t for t in depot.reclassements_tableaux}
    sortie = []
    for cle, lignes in groupes.items():
        tableau = tableaux[cle[:3]]
        versant = depot.reclassements_textes[cle[0]]["versant"]
        jour, lue = tableau["effet"], "effet" if tableau["effet"] else ""
        if not jour and date_de_la_phrase(tableau["intro"]):
            jour, lue = date_de_la_phrase(tableau["intro"]), "phrase"
        base = {"texte": cle[0], "article": cle[1], "tableau": cle[2], "groupe": cle[3],
                "date": jour, "date_lue": lue}

        def declarer(raison: str) -> None:
            sortie.append({**base, "statut": "declare", "raison": raison})

        if versant not in ("etat", "plusieurs"):
            declarer(f"versant {versant} : ses grilles ne sont qu'au LEGI, dont les libellés ne "
                     "se coupent pas en grade d'origine et grade d'accueil sans deviner")
            continue
        if not cle[3].strip():
            declarer("le tableau ne nomme pas les grades de ses lignes (groupe vide)")
            continue
        if not jour:
            declarer("la phrase qui annonce le tableau n'écrit pas la date du reclassement, et "
                     "l'entrée en vigueur de l'article ne la prouve pas (le décret n° 2017-786 "
                     "reclasse « Au 1er septembre 2017 » par un article en vigueur le 8 mai)")
            continue
        nommes, raison = statuts_de_la_phrase(depot, tableau)
        if raison:
            declarer(raison)
            continue
        statuts = ", ".join(f"n° {n}" for n in sorted(nommes))
        corps = _corps_du_reclassement(depot, nommes, jour)
        if not corps:
            declarer(f"le Noyau RH ne cite, la veille ni le jour du {jour}, pour aucun corps ni "
                     f"aucun grade, le statut que nomme la phrase ({statuts})")
            continue
        absorbes = {a for c in corps for v in depot.noyau_corps.get(c, [])
                    for a in v["anterieurs"].split()}
        origines = [g for c in set(corps) | absorbes for g in depot.noyau_grades[c]
                    if en_vigueur(g, veille(jour))]
        accueils = [g for c in corps for g in depot.noyau_grades[c] if en_vigueur(g, jour)]
        mots = cle[3].split()
        coupes = set()
        for i in range(1, len(mots) + 1):
            a = normaliser_noyau(" ".join(mots[:i]))
            b = normaliser_noyau(" ".join(mots[i:])) if i < len(mots) else a
            for o in origines:
                if normaliser_noyau(o["libelle"]) != a:
                    continue
                for n in accueils:
                    if normaliser_noyau(n["libelle"]) == b:
                        coupes.add((o["grade"], o["grille"], o["corps"],
                                    n["grade"], n["grille"], n["corps"]))
        if not coupes:
            declarer("le libellé ne se coupe pas en deux grades des corps "
                     f"{', '.join(sorted(corps))} du Noyau RH ({statuts}), en vigueur la veille "
                     f"et le jour du {jour}")
            continue
        if len(coupes) > 1:
            declarer("plusieurs coupes du libellé en grades du Noyau RH : "
                     + " ; ".join(f"{c[0]} → {c[3]}" for c in sorted(coupes)))
            continue
        ((go, grille_o, corps_o, ga, grille_a, corps_a),) = coupes
        # Chaque échelon du tableau, à sa place dans sa grille, par sa nature et
        # non le seul nombre des rangs (relecture R-B3-bis, partie 1).
        cotes = (("origine", "origine", "rang_origine", grille_o,
                  depot.natures_noyau_au(grille_o, veille(jour))),
                 ("accueil", "nouveau", "rang_nouveau", grille_a,
                  depot.natures_noyau_au(grille_a, jour)))
        absents, places = [], {}
        for l in sorted(lignes, key=lambda l: int(l["ligne"])):
            for cote, colonne, colonne_rang, grille, natures in cotes:
                if l[colonne_rang] == "0":
                    continue
                place = rang_dans_la_grille(l[colonne], int(l[colonne_rang]), natures)
                if place is None:
                    n = natures.count("exceptionnel")
                    absents.append(f"{cote} « {l[colonne]} » (rang {l[colonne_rang]}) : la grille "
                                   f"{grille} a {len(natures)} échelons hors élève, stagiaire et "
                                   "provisoires, " + (f"dont {n} exceptionnel" + "s" * (n > 1)
                                                      if n else "aucun exceptionnel"))
                elif l[colonne] in NON_NUMEROTES:
                    places[(cote, l[colonne])] = place
        if absents:
            declarer("les échelons ne sont pas ceux des grilles : "
                     + " ; ".join(dict.fromkeys(absents)))
            continue
        citations = []
        for c in dict.fromkeys((corps_o, corps_a)):
            if c in corps:
                numero, liste = corps[c]
                # Le corps s'il cite ; sinon les grades du reclassement, s'ils citent.
                liste = ([x for x in liste if x["qui"].startswith("le corps")]
                         or [x for x in liste if x["qui"].split()[2] in (go, ga)] or liste)
                citations.append(f"{nommes[numero]} ; {depot.preuve_du_noyau(liste)}")
        sortie.append({**base, "statut": "rattache", "corps": corps_a,
                       "grade_origine": go, "grille_origine": grille_o,
                       "grade_accueil": ga, "grille_accueil": grille_a,
                       "rangs_grille": " ; ".join(f"{cote} {nom} {place}" for (cote, nom), place
                                                  in sorted(places.items(),
                                                            key=lambda p: p[0][0] != "origine")),
                       "preuve": " ; ".join(citations) + f" ; grade {go} ({grille_o}) le "
                                 f"{veille(jour)}, {ga} ({grille_a}) le {jour}", "raison": ""})
    return sortie


# ---------------------------------------------------------------------------
# Ce qu'une lecture au Journal officiel viserait
# ---------------------------------------------------------------------------

#: Un tableau que le LEGI ne rend pas lisible : dessiné en caractères, en
#: fiches, non reproduit, ou dont la consolidation perd une ligne prouvée au JORF.
#: L'écart, en jours, entre l'entrée en vigueur d'un texte au LEGI et son
#: premier tableau de durées, au-delà duquel le tableau d'origine manque peut-être.
ECART_RETENU = 92
ABIME = re.compile(r"dessiné en caractères|écrit en fiches|non reproduit|consolidation du LEGI")


def a_lire_au_jorf(depot: Depot) -> list[dict]:
    lignes = []
    refus: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for dossier, textes in (("durees", depot.durees_textes),
                            ("reclassements", depot.reclassements_textes)):
        for n in lire(GRILLES / dossier / "non_lus.csv"):
            if ABIME.search(n["motif"]):
                motif = re.split(r"\s*[;:(«]", n["motif"])[0].strip()
                refus[n["texte"]].append((n["article"], f"{dossier} : {motif}"))
    titres = {**depot.reclassements_textes, **depot.durees_textes}
    for texte, liste in refus.items():
        t = titres[texte]
        motifs = collections.Counter(m for _, m in liste)
        lignes.append({"versant": t["versant"], "texte": texte, "numero": t["numero"],
                       "titre": t["titre"], "cas": "abime",
                       "articles": " ".join(sorted({a for a, _ in liste})),
                       "detail": " ; ".join(f"{m} ({k})" for m, k in sorted(motifs.items()))})
    premier: dict[str, str] = {}
    articles: dict[str, set] = collections.defaultdict(set)
    for t in depot.durees_tableaux:
        if t["texte"] not in premier or t["debut"] < premier[t["texte"]]:
            premier[t["texte"]] = t["debut"]
        articles[t["texte"]].add(t["article"])
    non_lus: dict[str, list[dict]] = collections.defaultdict(list)
    for n in lire(GRILLES / "durees" / "non_lus.csv"):
        non_lus[n["texte"]].append(n)
    for texte, debut in premier.items():
        t = depot.durees_textes[texte]
        # Moins de trois mois d'écart est d'ordinaire l'entrée en vigueur
        # différée du texte (« le premier jour du mois qui suit sa
        # publication », décret n° 2016-203, art. 4) : non retenu.
        if (date.fromisoformat(debut) - date.fromisoformat(t["debut"])).days <= ECART_RETENU:
            continue
        ecart = (f"le texte vaut au LEGI depuis le {t['debut']} ; son premier tableau de durées "
                 f"lu (durees/tableaux.csv) vaut depuis le {debut}")
        # Un article de durées d'avant, que le lecteur n'a pas lu, est au LEGI :
        # le tableau n'y manque pas (relecture R-B3, point 6).
        avant = sorted((n for n in non_lus[texte] if n["debut"] < debut),
                       key=lambda n: (n["debut"], n["article"]))
        if avant:
            vus = list(dict.fromkeys(
                f"art. {n['numero']}, {n['article']}, {_fmt(n['debut'], n['fin'] or OUVERT)}, "
                f"« {n['motif']} »" for n in avant))
            lignes.append({"versant": t["versant"], "texte": texte, "numero": t["numero"],
                           "titre": t["titre"], "cas": "non_lu",
                           "articles": " ".join(sorted({n["article"] for n in avant})),
                           "detail": f"{ecart} ; avant, le LEGI porte {len(vus)} article(s) de "
                                     "durées que le lecteur n'a pas lus (durees/non_lus.csv) : "
                                     + " ; ".join(vus[:3])
                                     + (f" ; et {len(vus) - 3} autres" if len(vus) > 3 else "")})
        else:
            lignes.append({"versant": t["versant"], "texte": texte, "numero": t["numero"],
                           "titre": t["titre"], "cas": "manque",
                           "articles": " ".join(sorted(articles[texte])),
                           "detail": f"{ecart} ; durees/non_lus.csv ne relève, avant, aucun "
                                     "article de durées non lu"})
    return sorted(lignes, key=lambda l: (l["versant"], l["cas"], l["numero"], l["texte"]))


# ---------------------------------------------------------------------------
# L'écriture
# ---------------------------------------------------------------------------

COLONNES = {
    "durees": ("texte", "article", "tableau", "groupe", "debut", "fin", "statut", "source",
               "texte_grille", "grille", "libelle_grille", "corps", "grade", "lien", "preuve",
               "raison"),
    "reclassements": ("texte", "article", "tableau", "groupe", "date", "date_lue", "statut",
                      "corps", "grade_origine", "grille_origine", "grade_accueil",
                      "grille_accueil", "rangs_grille", "preuve", "raison"),
    "a_lire_au_jorf": ("versant", "texte", "numero", "titre", "cas", "articles", "detail"),
}
ENTETES = {
    "durees": "Chaque grade de chaque tableau de durées (texte, article, tableau, groupe, de "
              "durees/), rattaché à une grille du dépôt (statut rattache) ou déclaré, avec sa "
              "raison (declare). debut, fin : la période commune au tableau et à la grille (fin "
              "exclue ; vide : en vigueur). source : etat (le Noyau RH : corps, grade, grille), "
              "ou le dossier des grilles du LEGI (texte_grille, grille). lien : visa (le texte "
              "d'échelonnement ne vise que ce statut), article (chaque version de l'article de "
              "la grille en vigueur sur la période nomme ce statut), noyau (le corps, ou l'un de "
              "ses grades, cite ce statut sur toute la période) ; preuve : la citation. Pour une "
              "grille du LEGI, le corps est le statut, texte. Une seule grille à la fois par "
              "source : un grade peut avoir, aux mêmes dates, une grille du LEGI et une du noyau.",
    "reclassements": "Chaque groupe de chaque tableau de reclassement (de reclassements/), "
                     "rattaché aux grilles d'origine et d'accueil du Noyau RH, ou déclaré. "
                     "date : celle du reclassement ; date_lue : effet (lue par le lecteur), "
                     "phrase (la date qui ouvre la phrase) ; corps, grades et grilles du noyau. "
                     "rangs_grille : le rang, dans sa grille (élève, stagiaire et provisoires "
                     "mis à part), de chaque échelon du groupe que le tableau ne numérote pas "
                     "(« accueil exceptionnel 5 ») ; il l'emporte sur le rang de "
                     "reclassements/lignes.csv, que le lecteur donne au-dessus du plus haut "
                     "échelon écrit de son côté du tableau.",
    "a_lire_au_jorf": "Les textes dont un tableau de durées ou de reclassement est abîmé au "
                      "LEGI (cas abime : dessiné en caractères, en fiches, non reproduit, ou "
                      "perdu par la consolidation), ou dont le premier tableau de durées lu vaut "
                      "plus de trois mois après le texte : cas non_lu, le LEGI porte avant un "
                      "article de durées que le lecteur n'a pas lu (durees/non_lus.csv ; "
                      "articles : ceux-là) ; cas manque, non_lus.csv n'en relève aucun, et le "
                      "tableau d'origine manque peut-être (articles : ceux des tableaux lus) ; "
                      "non lus ici.",
}


def ecrire(nom: str, lignes: list[dict], dossier: Path = SORTIE) -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    with (dossier / f"{nom}.csv").open("w", encoding="utf-8", newline="") as flux:
        flux.write(f"# {ENTETES[nom]}\n{SOURCE_ID}\n")
        redacteur = csv.DictWriter(flux, fieldnames=COLONNES[nom], lineterminator="\n",
                                   extrasaction="ignore", restval="")
        redacteur.writeheader()
        redacteur.writerows(lignes)


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--index", default=str(INDEX), help="chemin de l'index LEGI")
    options = analyseur.parse_args(arguments)
    try:
        index = Index(Path(options.index))
    except FileNotFoundError as erreur:
        print(f"Échec : {erreur}", file=sys.stderr)
        return 1
    depot = Depot(index)
    durees = chainer_durees(depot)
    reclassements = chainer_reclassements(depot)
    lire_au_jorf = a_lire_au_jorf(depot)
    ecrire("durees", durees)
    ecrire("reclassements", reclassements)
    ecrire("a_lire_au_jorf", lire_au_jorf)
    for nom, lignes in (("durées", durees), ("reclassements", reclassements)):
        cles = collections.defaultdict(set)
        for ligne in lignes:
            cles[ligne["statut"]].add((ligne["texte"], ligne["article"], ligne["tableau"],
                                       ligne["groupe"]))
        print(f"{nom} : {len(cles['rattache'])} grades de tableaux rattachés, "
              f"{len(cles['declare'] - cles['rattache'])} seulement déclarés ; "
              f"{collections.Counter(l['statut'] for l in lignes)}", file=sys.stderr)
    print(f"à lire au JORF : {collections.Counter(l['cas'] for l in lire_au_jorf)}",
          file=sys.stderr)
    print(f"source : {index.source()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
