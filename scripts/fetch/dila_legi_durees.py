#!/usr/bin/env python3
"""La durée de chaque échelon des grilles indiciaires, lue au LEGI.

    python scripts/fetch/dila_index.py legi --recuperer   # l'index, une fois
    python scripts/fetch/dila_legi_durees.py              # deux minutes
    python scripts/verifier_donnees.py --appliquer        # puis certifie

CE QU'UNE DURÉE D'ÉCHELON DIT. Le statut d'un corps, d'un cadre d'emplois ou
d'un emploi fixe, grade par grade, le temps à passer dans chaque échelon avant
d'accéder au suivant : « La durée du temps passé dans chacun des échelons […]
est fixée ainsi qu'il suit ». Depuis 2017 (le protocole PPCR), une durée
unique ; auparavant, à l'État, une durée moyenne et une durée minimale ; à la
territoriale, une durée maximale et une durée minimale ; chez les militaires,
l'« ancienneté exigée dans l'échelon pour accéder à l'échelon supérieur », et
des conditions d'accès aux échelons exceptionnels (« Après 13 ans de grade »).
Le plus haut échelon d'un grade n'a pas de durée. Ces tableaux sont dans les
statuts, non dans les textes d'échelonnement que lit ``dila_legi_grilles.py``.

LA SOURCE. L'index LEGI du dépôt (``scripts/fetch/dila_index.py``), dont le
filtre garde depuis le 3 novembre 2026 les articles qui fixent ces durées, par
leur seul texte (``DUREES_D_ECHELON``). Un article y est son texte sans
balises : le tableau n'est plus qu'une suite d'échelons et de durées.
``tableaux`` y cherche la phrase qui annonce un tableau de durées (elle finit
par « : ») ; ``lire_tableau`` relit ce qui la suit : l'en-tête, qui dit les
colonnes et leur ordre (« DURÉES Minimale Maximale », « MAXIMALE MINIMALE »,
« DURÉE Moyenne Minimale », « DURÉE ») ; puis les lignes, chacune un échelon
et autant de durées que de colonnes ; le libellé écrit entre deux lignes, le
grade, qui devient le groupe des lignes suivantes. Une durée se compte en
mois.

CE QUI EST REFUSÉ, plutôt que lu de travers, et consigné dans
``non_lus.csv`` : une ligne qui n'a pas autant de durées que de colonnes (hors
l'échelon le plus haut, et l'échelon spécial ou exceptionnel) ; une durée hors
de sa ligne ; des échelons en double, dans le désordre ou avec un trou ; une
durée de plus de dix ans ; une durée minimale au-dessus de la moyenne ou de la
maximale ; un en-tête d'une seule colonne quand la phrase en nomme deux ; les
durées écrites d'échelon à échelon (« du 1er au 2e échelon : 2 ans ») ou à
l'accès à l'échelon (« pour accéder au 3e échelon »), qui se liraient décalées
d'un échelon ; un tableau dessiné en caractères ; une phrase qui coupe le
tableau. Les durées écrites en phrases, et celles qu'un article renvoie à un
autre texte (« sont fixées à l'article 4 du décret du 20 septembre 1973 »), ne
sont pas lues : elles y sont consignées aussi.

CE QU'IL ÉCRIT, sous ``data/reference/grilles/durees/`` : ``textes.csv``, les
textes qui portent un tableau lu ou refusé, avec leur versant (celui des
grilles, au titre puis aux visas ; les statuts militaires reconnus en plus à
leur titre) ; ``tableaux.csv``, chaque tableau à chaque période de son
article, ses colonnes, la phrase qui l'annonce et son en-tête ;
``lignes.csv``, chaque ligne ; ``non_lus.csv``. Et
``data/brut/dila_legi_durees.json``, le rang et les durées de chaque ligne,
que ``scripts/verifier_donnees.py`` confronte aux fichiers.

CE QUE LA DONNÉE NE DIT PAS. Un tableau nomme ses grades par son libellé, non
par les clés de ``grilles/<versant>/grilles.csv`` : rattacher chaque tableau
aux grilles du dépôt, par le texte d'échelonnement qui vise le statut, reste à
faire. Les réductions et majorations d'ancienneté (l'avancement accéléré, la
bonification), écrites en phrases, ne sont pas lues.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

BRUT = RACINE / "data" / "brut" / "dila_legi_durees.json"
REFERENCE = RACINE / "data" / "reference" / "grilles" / "durees"
EN_VIGUEUR = "2999-01-01"

# ---------------------------------------------------------------------------
# Les durées
# ---------------------------------------------------------------------------

NOMBRES = {"un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6,
           "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12,
           "quinze": 15, "dix-huit": 18, "vingt": 20, "vingt-quatre": 24, "trente": 30,
           "trente-six": 36}
_NOMBRE = (r"(?:\d{1,3}(?=\s*(?:ans?|mois)\b)|(?:dix-huit|vingt-quatre|trente-six|un|une|deux|trois"
           r"|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|quinze|vingt|trente)(?=\s))")
#: « 2 ans 5 mois », « 1 an et 6 mois », « 2 ans et six mois », « 18 mois »,
#: « un an et demi ».
DUREE = (rf"\b{_NOMBRE}\s*(?:ans?|mois)\b(?:\s*,?\s*(?:et\s+)?{_NOMBRE}\s*mois\b)?"
         rf"(?:\s+et\s+demi\b)?")
_UNE_DUREE = re.compile(
    rf"(?P<n1>{_NOMBRE})\s*(?P<u1>ans?|mois)\b(?:\s*,?\s*(?:et\s+)?(?P<n2>{_NOMBRE})\s*mois\b)?"
    rf"(?P<demi>\s+et\s+demi\b)?", re.IGNORECASE)


def _nombre(mot: str) -> int:
    return int(mot) if mot.isdigit() else NOMBRES[mot.lower()]


def mois(texte: str) -> int:
    """Une durée en mois : « 3 ans 6 mois » 42, « un an et demi » 18."""
    trouve = _UNE_DUREE.fullmatch(texte.strip())
    if not trouve:
        raise ValueError(f"durée illisible : {texte!r}")
    total = _nombre(trouve.group("n1")) * (1 if trouve.group("u1").lower() == "mois" else 12)
    if trouve.group("n2"):
        if trouve.group("u1").lower() == "mois":
            raise ValueError(f"des mois après des mois : {texte!r}")
        total += _nombre(trouve.group("n2"))
    if trouve.group("demi"):
        if trouve.group("u1").lower() == "mois" or trouve.group("n2"):
            raise ValueError(f"une demie de mois : {texte!r}")
        total += 6
    return total


# ---------------------------------------------------------------------------
# Le vocabulaire des tableaux
# ---------------------------------------------------------------------------

APOS = r"['’]\s*"
_SUFFIXE = r"(?:er|re|ère|e|ème|eme)"
#: « l'échelon exceptionnel » de l'en-tête n'est pas une ligne.
_PAS_ARTICLE = r"(?<!['’])(?<!['’]\s)"
#: Un échelon : « 11e échelon », « 1 er échelon », « Echelon 7 », « échelon
#: spécial », « échelon exceptionnel », « Echelon unique », « 13e échelon
#: provisoire ».
ECHELON = (
    rf"(?<!n°)(?<!n°\s)\b(?P<numero>\d{{1,2}})\s*{_SUFFIXE}?\s*[ée]chelon\b"
    r"(?!\s+(?:sp[ée]cial|exceptionnel|unique)\b)(?:\s*\(?(?P<provisoire>provisoire)\b\)?)?"
    rf"|{_PAS_ARTICLE}\b[ée]chelon\s+(?P<numero_apres>\d{{1,2}})\b(?!\s*{_SUFFIXE}?\s*[ée]chelon)"
    rf"|{_PAS_ARTICLE}\b[ée]chelon\s+(?P<nom>sp[ée]cial|exceptionnel|unique)\b")
#: Plusieurs échelons d'une même durée : « 7e, 8e, 9e, 10e, 11e et 12e
#: échelons », « 3e et 4e échelons ».
LISTE = (rf"(?P<liste>\b\d{{1,2}}\s*{_SUFFIXE}(?:\s*,\s*\d{{1,2}}\s*{_SUFFIXE})*"
         rf"\s+et\s+\d{{1,2}}\s*{_SUFFIXE}\s+[ée]chelons?\b)")
_NUMEROS = re.compile(r"\d{1,2}")
#: Les échelons des tableaux militaires, sans le mot « échelon » : « 13e »,
#: « 1er », quand le tableau n'en a aucun qui le porte.
ORDINAL = (rf"\b(?P<ordinal>\d{{1,2}})\s?{_SUFFIXE}\b"
           r"(?!\s*(?:[ée]chelons?|classe|grade|cat[ée]gorie|groupe|niveau|[ée]chelle|alin[ée]a"
           r"|article|janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre|octobre"
           r"|novembre|d[ée]cembre|ann[ée]e|section|chambre|partie)\b)")
#: Ce qui ouvre un échelon sans être sa durée : « Après 13 ans de grade »,
#: « avant 17 ans de grade », « au moins 4 ans de services ».
CONDITION = (rf"\b(?:apr[èe]s|avant|au\s+moins|moins\s+de|plus\s+de|au[- ]del[àa]\s+de)\s+"
             rf"(?:{DUREE})(?:\s+(?:de|d{APOS})\s*(?:grade|services?|anciennet[ée]|"
             rf"commandement|serviced?)\w*(?:\s+(?:effectifs?|militaires?|dans\s+le\s+grade))?)?")
#: Une case vide : un tiret ou une barre seuls.
VIDE = r"(?<![\w-])[-–—―/](?![\w-])|\b[ée]chelon\s+terminal\b"


def _jetons(militaire: bool) -> re.Pattern:
    echelon = ORDINAL if militaire else f"{LISTE}|{ECHELON}"
    return re.compile(rf"(?P<cond>{CONDITION})|(?P<duree>{DUREE})|(?P<ech>{echelon})"
                      rf"|(?P<vide>{VIDE})", re.IGNORECASE)


JETONS = _jetons(False)
JETONS_MILITAIRES = _jetons(True)
_UN_ECHELON = re.compile(ECHELON, re.IGNORECASE)

#: Les mots de l'en-tête qui nomment la colonne des durées ; l'en-tête finit au
#: dernier, et ce qui le suit nomme le premier grade.
MOTS_D_ENTETE = re.compile(
    rf"\bdur[ée]es?\b(?:\s+(?:de\s+l{APOS}|d{APOS}|dans\s+l{APOS})[ée]chelon\b)?"
    r"|\bmoyennes?\b|\bminimales?\b|\bmaximales?\b|\bminimum\b|\bmaximum\b|\bmini\b|\bmaxi\b"
    r"|\bmin\.|\bmax\."
    rf"|anciennet[ée]\s+(?:exig[ée]e|requise)(?:[^.]{{0,80}}?sup[ée]rieur\b"
    rf"|\s+dans\s+l{APOS}[ée]chelon\b)"
    rf"|conditions\s+d{APOS}acc[èe]s\s+[àa]\s+l{APOS}[ée]chelon\s+(?:exceptionnel|sp[ée]cial)\b"
    r"|r[èe]gles\s+particuli[èe]res\b"
    rf"|temps\s+[àa]\s+passer(?:\s+dans\s+l{APOS}[ée]chelon\b)?",
    re.IGNORECASE)
#: Les noms des colonnes, dans l'ordre où l'en-tête les écrit.
COLONNES_NOMMEES = re.compile(
    r"\b(?P<moyenne>moyennes?)\b|\b(?P<minimale>minimales?|minimum|mini)\b|\b(?P<minp>min)\."
    r"|\b(?P<maximale>maximales?|maximum|maxi)\b|\b(?P<maxp>max)\.", re.IGNORECASE)
#: Ce qu'une ligne peut porter sans que ce soit une case : la ponctuation, un
#: renvoi « (1) », « (a) ».
BRUIT = re.compile(r"\(\s*\w{1,2}\s*\)|\*+|[.:;,()=]", re.IGNORECASE)
#: Une phrase, non un grade : le tableau s'arrête là.
PROSE = re.compile(
    r"\b(?:sont|est|peut|peuvent|fix[ée]e?s?|pr[ée]vue?s?|conform[ée]ment|lorsque|ainsi|qui"
    r"|dont|comporte\w*|comprend\w*|b[ée]n[ée]ficie\w*|application|d[ée]cret|article|arr[êe]t[ée]|loi|susvis[ée]e?s?)\b",
    re.IGNORECASE)
CARACTERES = re.compile(r":-{4,}|-{6,}|: \d{3} :")
#: Un grade ne porte ni durée ni numéro d'échelon : c'est une case mal lue.
LIBELLE_SUSPECT = re.compile(rf"\d\s*(?:ans?|mois)\b|\b(?:ans?|mois)\b|\b\d{{1,2}}\s*{_SUFFIXE}\s*,"
                             rf"|\b\d{{1,2}}\s*{_SUFFIXE}\s+et\s*$", re.IGNORECASE)
#: Les durées écrites d'un échelon au suivant, ou à l'accès d'un échelon :
#: lues ligne à ligne, elles seraient décalées d'un échelon.
D_ECHELON_A_ECHELON = re.compile(
    rf"\bdu\s+\d{{1,2}}\s*{_SUFFIXE}?\s+(?:[ée]chelon\s+)?au\s+\d{{1,2}}"
    rf"|\b(?:pour\s+)?(?:acc[ée]der|l{APOS}acc[èe]s|acc[èe]s)\s+(?:au|[àa]\s+l{APOS})\s*\d{{1,2}}",
    re.IGNORECASE)
ACCES_SANS_SUPERIEUR = re.compile(rf"acc[èe]s|acc[ée]der", re.IGNORECASE)
EN_TETE_REDIT = re.compile(r"^\s*(?:grades?|classes?)?\s*(?:,|et)?\s*[ée]chelons?\b", re.IGNORECASE)
ECHELLE_DE_SOLDE = re.compile(r"^[ée]chelle\s+de\s+solde\b", re.IGNORECASE)
_ECHELLE_DANS = re.compile(r"\s+[ée]chelle\s+de\s+solde\b.*$", re.IGNORECASE)

#: La phrase qui annonce un tableau de durées.
LIMITE = re.compile(r"limite\s+(?:de\s+)?(?:la\s+)?dur[ée]e", re.IGNORECASE)
NON_DUREE = re.compile(
    r"reclass|int[ée]gr|\bclass[ée]e?s\b|\bclass[ée]\b|classement|correspondance|situation"
    r"|\bpromu|reprise|nomm[ée]s?\b|d[ée]tach", re.IGNORECASE)
RECLASSEMENT_DANS_LE_CORPS = re.compile(
    r"anciennet[ée]\s+(?:d['’]\s*[ée]chelon\s+)?(?:acquise|conserv[ée]e|maintenue)"
    r"|sans\s+anciennet[ée]|situation\s+(?:ancienne|nouvelle|actuelle)", re.IGNORECASE)
TABLEAU = re.compile(r"\btableaux?\b|\bsuit\b|\bsuivante?s?\b|ci-(?:apr[èe]s|dessous)",
                     re.IGNORECASE)
NON_REPRODUIT = re.compile(r"consulter\s+le\s+tableau|non\s+reproduit|voir\s+(?:le\s+)?tableau"
                           r"\s+(?:au|dans\s+le)\s+(?:jo|journal)", re.IGNORECASE)


def _sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texte)
                   if not unicodedata.combining(c))


def _propre(texte: str) -> str:
    return re.sub(r"\s+", " ", texte).strip(" :;,.-–—― ")


def _durees_d_echelon() -> re.Pattern:
    from dila_index import DUREES_D_ECHELON  # noqa: PLC0415
    return DUREES_D_ECHELON


def annonce_des_durees(intro: str, debut_du_corps: str) -> bool:
    """La phrase annonce-t-elle un tableau de durées d'échelon ? Elle les nomme
    (« la durée du temps passé dans chacun des échelons »), ou annonce un
    tableau dont l'en-tête les nomme (« ANCIENNETÉ EXIGÉE dans l'échelon »).
    Ni un reclassement, ni un classement à la nomination, qui gardent
    l'ancienneté « dans la limite de la durée de l'échelon »."""
    if NON_DUREE.search(intro) or RECLASSEMENT_DANS_LE_CORPS.search(debut_du_corps):
        return False
    motif = _durees_d_echelon()
    for texte in (intro, intro + " " + debut_du_corps if TABLEAU.search(intro) else ""):
        for trouve in motif.finditer(texte):
            if not LIMITE.search(texte[max(0, trouve.start() - 30):trouve.start() + 12]):
                return True
    return False


# ---------------------------------------------------------------------------
# L'analyseur
# ---------------------------------------------------------------------------

#: Les colonnes, et le champ de ``Ligne`` que chacune remplit.
CHAMPS = {"unique": "duree", "moyenne": "duree_moyenne", "minimale": "duree_minimale",
          "maximale": "duree_maximale"}


@dataclass
class Ligne:
    groupe: str
    echelon: str
    duree: int | None = None
    duree_moyenne: int | None = None
    duree_minimale: int | None = None
    duree_maximale: int | None = None
    condition: str = ""
    cases: list = field(default_factory=list, repr=False)
    #: Les lignes d'une même case « 3e et 4e échelons » partagent leur bloc.
    bloc: int = 0


@dataclass
class Tableau:
    colonnes: tuple[str, ...] = ()
    entete: str = ""
    lignes: list[Ligne] = field(default_factory=list)
    refus: str = ""


@dataclass
class Extrait:
    intro: str
    corps: str


def tableaux(article: str) -> list[Extrait]:
    """Les tableaux de durées d'un article, chacun avec la phrase qui l'annonce :
    celle qui finit par « : » et nomme les durées d'échelon."""
    extraits: list[tuple[int, int, str]] = []
    for deux_points in re.finditer(r":", article):
        avant = article[:deux_points.start()]
        point = max(avant.rfind(". "), avant.rfind(" : "), avant.rfind(": "))
        intro = _propre(avant[point + 2 if point >= 0 else 0:])
        if not intro:
            continue
        suite = article[deux_points.end():deux_points.end() + 400]
        if not _UN_ECHELON.search(suite) and not re.search(ORDINAL, suite, re.IGNORECASE):
            continue
        if annonce_des_durees(intro, suite[:300]):
            extraits.append((deux_points.start(), deux_points.end(), intro))
    sortie = []
    for k, (_, fin, intro) in enumerate(extraits):
        limite = extraits[k + 1][0] if k + 1 < len(extraits) else len(article)
        # Le tableau suivant commence à sa phrase, non à ses deux points.
        if k + 1 < len(extraits):
            phrase = article.rfind(". ", fin, limite)
            limite = phrase + 1 if phrase >= 0 else limite
        sortie.append(Extrait(intro + " :", article[fin:limite]))
    return sortie


def _echelon(trouve: re.Match) -> str:
    groupes = trouve.groupdict()
    numero = groupes.get("numero") or groupes.get("numero_apres")
    if numero:
        return f"{int(numero)}-provisoire" if groupes.get("provisoire") else str(int(numero))
    if groupes.get("ordinal"):
        return str(int(groupes["ordinal"]))
    return _sans_accents(groupes["nom"]).lower()


def _colonnes(entete: str, intro: str) -> tuple[tuple[str, ...], str]:
    """Les colonnes de durées, dans l'ordre de l'en-tête ; à défaut d'un nom
    dans l'en-tête, la seule que la phrase nomme, ou la durée unique."""
    noms: list[str] = []
    for trouve in COLONNES_NOMMEES.finditer(entete):
        nom = next(n for n, v in trouve.groupdict().items() if v)
        nom = {"minp": "minimale", "maxp": "maximale"}.get(nom, nom)
        if nom not in noms:
            noms.append(nom)
    if noms:
        return tuple(noms), ""
    dans_l_intro = {n for n, v in (
        ("moyenne", r"\bmoyennes?\b"), ("minimale", r"\bminimales?\b|\bminimum\b"),
        ("maximale", r"\bmaximales?\b|\bmaximum\b")) if re.search(v, intro, re.IGNORECASE)}
    if len(dans_l_intro) > 1:
        return (), (f"l'en-tête n'a qu'une colonne quand la phrase nomme les durées "
                    f"{' et '.join(sorted(dans_l_intro))}")
    return (dans_l_intro.pop() if dans_l_intro else "unique",), ""


def _entete_et_groupe(libelle: str) -> tuple[str, str]:
    fins = [m.end() for m in MOTS_D_ENTETE.finditer(libelle)]
    if not fins:
        reste = re.sub(r"^\s*(?:grades?\s+(?:et\s+)?)?[ée]chelons?\b", "", libelle,
                       flags=re.IGNORECASE)
        return _propre(libelle[:len(libelle) - len(reste)]), _propre(reste)
    return _propre(libelle[:fins[-1]]), _propre(libelle[fins[-1]:])


def _bruit(texte: str) -> bool:
    return not BRUIT.sub("", texte).strip()


def _groupe(libelle: str, precedent: str) -> str:
    """Le grade d'une ligne : le libellé écrit avant elle ; une échelle de
    solde seule (« Echelle de solde n° 2 ») reste sous le grade d'avant."""
    if ECHELLE_DE_SOLDE.match(libelle) and precedent:
        grade = _ECHELLE_DANS.sub("", precedent).strip()
        if grade and not ECHELLE_DE_SOLDE.match(grade):
            return f"{grade} {libelle}"
    return libelle


def lire_tableau(extrait: Extrait) -> Tableau:
    """Les lignes d'un tableau de durées aplati : le grade, l'échelon et ses
    durées, en mois, dans l'ordre des colonnes que l'en-tête écrit."""
    tableau = Tableau()
    corps = extrait.corps
    if CARACTERES.search(corps):
        tableau.refus = "tableau dessiné en caractères"
        return tableau
    if NON_REPRODUIT.search(corps[:400]):
        tableau.refus = "tableau non reproduit au LEGI"
        return tableau
    militaire = not _UN_ECHELON.search(corps)
    elements = []
    fin = 0
    for trouve in (JETONS_MILITAIRES if militaire else JETONS).finditer(corps):
        if corps[fin:trouve.start()].strip():
            elements.append(("libre", corps[fin:trouve.start()], fin, None))
        genre = next(g for g in ("cond", "duree", "ech", "vide") if trouve.group(g) is not None)
        elements.append((genre, trouve.group(), trouve.start(), trouve))
        fin = trouve.end()
    if corps[fin:].strip():
        elements.append(("libre", corps[fin:], fin, None))

    lignes: list[Ligne] = []
    courante: Ligne | None = None
    groupe, entete, libre = "", None, ""
    coupe = None
    for genre, texte, debut, trouve in elements:
        if genre == "libre" or (genre == "vide" and (courante is None or libre)):
            if _bruit(texte):
                continue
            if courante is not None and courante.condition and not PROSE.search(texte):
                courante.condition = _propre(courante.condition + " " + texte)
                continue
            if entete is not None and PROSE.search(texte):
                coupe = debut
                break
            libre = (libre + " " + texte) if libre else texte
            continue
        if entete is None:
            if genre != "ech":
                libre = (libre + " " + texte) if libre else texte
                continue
            entete, groupe = _entete_et_groupe(libre)
            libre = ""
            if LIBELLE_SUSPECT.search(groupe):
                tableau.refus = f"un libellé porte une durée ou un échelon : « {groupe[:50]} »"
                return tableau
        if genre == "ech":
            if libre:
                libelle = _propre(libre)
                if MOTS_D_ENTETE.search(libelle) or EN_TETE_REDIT.match(libelle):
                    # L'en-tête redit avant un grade, au même ordre de colonnes.
                    redit, libelle = _entete_et_groupe(libelle)
                    if (COLONNES_NOMMEES.search(redit)
                            and _colonnes(redit, extrait.intro)[0]
                            != _colonnes(entete, extrait.intro)[0]):
                        tableau.refus = "l'en-tête change d'ordre au milieu du tableau"
                        return tableau
                    libre = libelle
                if LIBELLE_SUSPECT.search(libre):
                    tableau.refus = f"un libellé porte une durée ou un échelon : « {_propre(libre)[:50]} »"
                    return tableau
                groupe = _groupe(_propre(libre), groupe)
                libre = ""
            cases: list = []
            echelons = ([str(int(n)) for n in _NUMEROS.findall(trouve.group("liste"))]
                        if trouve.groupdict().get("liste") else [_echelon(trouve)])
            bloc = len(lignes)
            for echelon in echelons:
                courante = Ligne(groupe, echelon, cases=cases, bloc=bloc)
                lignes.append(courante)
        elif libre:
            tableau.refus = f"une durée hors de sa ligne, après « {_propre(libre)[:50]} »"
            return tableau
        elif genre == "cond":
            courante.condition = _propre(courante.condition + " " + texte)
        else:
            courante.cases.append(None if genre == "vide" else texte)
    if coupe is not None and len(_UN_ECHELON.findall(corps[coupe:])) >= 4:
        tableau.refus = "une phrase coupe le tableau"
        return tableau
    if coupe is not None:
        # « Le 8e échelon de la classe exceptionnelle est accessible… » : la
        # phrase qui suit le tableau a ouvert une ligne sans durée, sous un
        # libellé neuf. Elle n'est pas du tableau.
        while (len(lignes) >= 2 and not lignes[-1].cases and not lignes[-1].condition
               and lignes[-1].groupe != lignes[-2].groupe):
            lignes.pop()
    if entete is None:
        tableau.refus = "aucun échelon"
        return tableau
    corps_lu = corps[:coupe] if coupe is not None else corps
    if D_ECHELON_A_ECHELON.search(corps_lu):
        tableau.refus = ("durées écrites d'un échelon au suivant ou à l'accès d'un échelon : "
                         "elles se liraient décalées d'un échelon")
        return tableau
    if (ACCES_SANS_SUPERIEUR.search(entete)
            and not re.search(r"sup[ée]rieur|exceptionnel|sp[ée]cial", entete, re.IGNORECASE)):
        tableau.refus = "l'en-tête ne dit pas de quel échelon part la durée"
        return tableau
    colonnes, refus = _colonnes(entete, extrait.intro)
    if refus:
        tableau.refus = refus
        return tableau
    tableau.colonnes, tableau.entete = colonnes, entete
    tableau.refus = _remplir(lignes, colonnes)
    tableau.lignes = [] if tableau.refus else lignes
    return tableau


def _ordre(echelon: str) -> float:
    if echelon == "unique":
        return 1
    if echelon in ("special", "exceptionnel"):
        return 100 + (echelon == "exceptionnel")
    numero, _, provisoire = echelon.partition("-")
    return int(numero) - (0.5 if provisoire else 0)


def _remplir(lignes: list[Ligne], colonnes: tuple[str, ...]) -> str:
    """Les cases de chaque ligne dans ses colonnes, et ce qui trahit une lecture
    fausse ; vide si le tableau se lit."""
    groupes: dict[str, list[Ligne]] = collections.defaultdict(list)
    for ligne in lignes:
        groupes[ligne.groupe].append(ligne)
    for nom, liste in groupes.items():
        ordres = [_ordre(l.echelon) for l in liste]
        if len(set(ordres)) != len(ordres):
            return f"échelon en double dans « {nom[:60]} »"
        blocs: dict[int, list[float]] = collections.defaultdict(list)
        for ligne, ordre in zip(liste, ordres):
            blocs[ligne.bloc].append(ordre)
        bornes_des_blocs = [(min(b), max(b)) for _, b in sorted(blocs.items())]
        if len(bornes_des_blocs) >= 2:
            sens = 1 if bornes_des_blocs[1][0] > bornes_des_blocs[0][1] else -1
            if any((b[0] - a[1]) <= 0 if sens == 1 else (a[0] - b[1]) <= 0
                   for a, b in zip(bornes_des_blocs, bornes_des_blocs[1:])):
                return f"échelons dans le désordre dans « {nom[:60]} »"
        numeros = sorted(int(o) for o in ordres if o < 100 and o == int(o))
        if numeros and numeros != list(range(numeros[0], numeros[-1] + 1)):
            return f"un échelon manque dans « {nom[:60]} »"
        if numeros and numeros[0] != 1:
            return f"le grade « {nom[:60]} » ne descend pas au 1er échelon"
        plus_haut = max((o for o in ordres if o < 100), default=None)
        for ligne, ordre in zip(liste, ordres):
            sans_duree = all(c is None for c in ligne.cases)
            sommet = ordre == plus_haut or ordre >= 100 or bool(ligne.condition)
            if sans_duree and sommet:
                continue
            if len(ligne.cases) != len(colonnes):
                return (f"le {ligne.echelon}e échelon de « {nom[:50]} » a {len(ligne.cases)} "
                        f"case(s) pour {len(colonnes)} colonne(s)")
            for colonne, case in zip(colonnes, ligne.cases):
                if case is None:
                    continue
                try:
                    valeur = mois(case)
                except ValueError as erreur:
                    return str(erreur)
                if not 1 <= valeur <= 120:
                    return f"une durée de {valeur} mois au {ligne.echelon}e échelon"
                setattr(ligne, CHAMPS[colonne], valeur)
            bornes = [v for v in (ligne.duree_minimale, ligne.duree_moyenne,
                                  ligne.duree_maximale) if v is not None]
            if bornes != sorted(bornes):
                return f"une durée minimale au-dessus d'une autre au {ligne.echelon}e échelon"
    if sum(any(getattr(l, c) is not None for c in CHAMPS.values()) for l in lignes) < 2:
        return "moins de deux durées"
    return ""


# ---------------------------------------------------------------------------
# Les articles de l'index
# ---------------------------------------------------------------------------

REQUETE = "texte:echelon OR texte:echelons"
#: Une phrase qui fixe des durées sans tableau, ou les renvoie à un autre texte.
FIXE = re.compile(r"\b(?:est|sont)\s+(?:fix[ée]e?s?|de|[ée]gale?s?)\b|\bfix[ée]e?s?\s+[àa]\b",
                  re.IGNORECASE)
RENVOI = re.compile(r"\b(?:fix[ée]e?s?|pr[ée]vue?s?|d[ée]termin[ée]e?s?)\s+(?:[àa]|par)\s+"
                    r"(?:l['’]\s*article|les\s+articles|le\s+d[ée]cret|l['’]\s*arr[êe]t[ée]"
                    r"|le\s+tableau\s+de\s+l|l['’]\s*annexe)", re.IGNORECASE)
MILITAIRES = re.compile(
    r"\bmilitaires?\b|\bsous-officiers\b|\bofficiers\b(?!\s+(?:de\s+(?:police|port|paix"
    r"|l['’][ée]tat\s+civil)|minist[ée]riels))|\bgendarmerie\b|\barm[ée]es\b|\bmarine\s+nationale\b"
    r"|\bmarins\b|\bcorps\s+de\s+l['’]armement\b", re.IGNORECASE)


def _fin(jour: str) -> str:
    return "" if not jour or jour >= EN_VIGUEUR else jour


def _versant(titre: str, visas: str) -> str:
    from dila_legi_grilles import versant  # noqa: PLC0415
    lu = versant(titre, visas)
    if lu == "etat" and MILITAIRES.search(titre) and not re.search(r"\bcivil", titre, re.I):
        return "militaires"
    return lu or "plusieurs"


def _texte_de(titre: str, info: dict) -> dict:
    from dila_legi_grilles import numero, _signature  # noqa: PLC0415
    return {"texte": info["texte"], "versant": _versant(titre, info["visas"]),
            "numero": numero(titre), "nature": info["nature"], "signature": _signature(titre),
            "debut": info["debut"], "fin": _fin(info["fin"]), "titre": titre}


def _en_prose(contenu: str) -> str:
    """Le motif d'un article qui fixe des durées sans tableau lisible, ou rien."""
    motif = _durees_d_echelon()
    for trouve in motif.finditer(contenu):
        if LIMITE.search(contenu[max(0, trouve.start() - 30):trouve.start() + 12]):
            continue
        debut = contenu.rfind(". ", 0, trouve.start()) + 1
        fin = contenu.find(". ", trouve.end())
        phrase = contenu[debut:fin if fin >= 0 else len(contenu)]
        if NON_DUREE.search(phrase) or not FIXE.search(phrase):
            continue
        if RENVOI.search(phrase) and not re.search(DUREE, phrase, re.IGNORECASE):
            return "durées renvoyées à un autre texte"
        if re.search(DUREE, phrase, re.IGNORECASE):
            return "durées écrites en phrases"
    return ""


def extraire(chemin_index: Path | str | None = None) -> dict:
    """Les durées d'échelon que l'index LEGI garde : les textes, les tableaux,
    leurs lignes, et ce qui n'est pas lu."""
    import dila_index  # noqa: PLC0415

    db, source = dila_index.ouvrir_lecture("legi", str(chemin_index) if chemin_index else None)
    motif = _durees_d_echelon()
    articles = [a for a in db.execute(
        "SELECT d.id, d.date, d.fin, d.num, d.titre, d.texte FROM fts JOIN doc d "
        "ON d.rowid = fts.rowid WHERE fts MATCH ? AND d.nature LIKE 'Article%' "
        "ORDER BY d.date, d.id", (REQUETE,)) if a[5] and motif.search(a[5])]
    titres = {a[4] for a in articles}
    infos: dict[str, dict] = {}
    for ident, debut, fin, nature, titre, visas in db.execute(
            "SELECT id, date, fin, nature, titre, texte FROM doc WHERE nature NOT LIKE 'Article%'"):
        if titre in titres and titre not in infos:
            infos[titre] = {"texte": ident, "debut": debut, "fin": fin, "nature": nature,
                            "visas": visas or ""}
    db.close()

    lus: dict[tuple, dict] = {}
    non_lus: list[dict] = []
    for ident, debut, fin, numero, titre, contenu in articles:
        if titre not in infos or debut >= EN_VIGUEUR:
            continue
        texte = infos[titre]["texte"]
        extraits = tableaux(contenu)
        if not extraits:
            motif_prose = _en_prose(contenu)
            if motif_prose:
                non_lus.append({"texte": texte, "article": ident, "numero": numero,
                                "tableau": "", "debut": debut, "fin": _fin(fin),
                                "motif": motif_prose})
            continue
        for rang, extrait in enumerate(extraits, 1):
            tableau = lire_tableau(extrait)
            if tableau.refus:
                non_lus.append({"texte": texte, "article": ident, "numero": numero,
                                "tableau": str(rang), "debut": debut, "fin": _fin(fin),
                                "motif": tableau.refus})
                continue
            cle = (texte, numero, rang)
            contenu_lu = (tableau.colonnes, [
                (l.groupe, l.echelon, l.duree, l.duree_moyenne, l.duree_minimale,
                 l.duree_maximale, l.condition) for l in tableau.lignes])
            avant = lus.get(cle)
            if avant and avant["contenu"] == contenu_lu and avant["fin"] == debut:
                avant["fin"] = fin            # la version suivante redit le même tableau
                avant["versions"].append(ident)
                continue
            if avant:
                lus[(texte, numero, rang, avant["debut"])] = lus.pop(cle)
            lus[cle] = {"texte": texte, "article": ident, "numero": numero, "tableau": str(rang),
                        "debut": debut, "fin": fin, "intro": extrait.intro, "tableau_lu": tableau,
                        "contenu": contenu_lu, "versions": [ident]}

    sortie: dict = {"source": source, "textes": [], "tableaux": [], "lignes": [],
                    "non_lus": sorted(non_lus, key=lambda n: (n["texte"], n["numero"],
                                                              n["debut"], n["tableau"]))}
    comptes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for lu in sorted(lus.values(), key=lambda l: (l["texte"], l["debut"], l["article"],
                                                  int(l["tableau"]))):
        tableau = lu["tableau_lu"]
        comptes[lu["texte"]]["lus"] += 1
        sortie["tableaux"].append({
            "texte": lu["texte"], "article": lu["article"], "numero": lu["numero"],
            "tableau": lu["tableau"], "debut": lu["debut"], "fin": _fin(lu["fin"]),
            "versions": " ".join(lu["versions"]), "colonnes": " ".join(tableau.colonnes), "lignes": str(len(tableau.lignes)),
            "intro": lu["intro"], "entete": tableau.entete})
        for n, (ligne, rang) in enumerate(zip(tableau.lignes, _rangs(tableau.lignes)), 1):
            sortie["lignes"].append({
                "texte": lu["texte"], "article": lu["article"], "tableau": lu["tableau"],
                "ligne": str(n), "groupe": ligne.groupe, "echelon": ligne.echelon,
                "rang": str(rang), **{c: "" if getattr(ligne, c) is None else str(getattr(ligne, c))
                                      for c in CHAMPS.values()},
                "condition": ligne.condition})
    for refus in non_lus:
        comptes[refus["texte"]]["non_lus"] += 1
    par_texte = {info["texte"]: titre for titre, info in infos.items()}
    for texte in sorted(comptes):
        titre = par_texte[texte]
        sortie["textes"].append({**_texte_de(titre, infos[titre]),
                                 "tableaux_lus": str(comptes[texte]["lus"]),
                                 "non_lus": str(comptes[texte]["non_lus"])})
    sortie["textes"].sort(key=lambda t: (t["versant"], t["signature"], t["texte"]))
    return sortie


def _rangs(lignes: list[Ligne]) -> list[int]:
    """Le rang de chaque échelon : son numéro ; un pour l'échelon unique ; le
    spécial au-dessus du plus haut de son grade, l'exceptionnel au-dessus
    encore."""
    plus_haut: dict[str, int] = collections.defaultdict(int)
    speciaux: set[str] = set()
    for ligne in lignes:
        if ligne.echelon[0].isdigit():
            plus_haut[ligne.groupe] = max(plus_haut[ligne.groupe],
                                          int(ligne.echelon.split("-")[0]))
        elif ligne.echelon == "special":
            speciaux.add(ligne.groupe)
    rangs = []
    for ligne in lignes:
        if ligne.echelon[0].isdigit():
            rangs.append(int(ligne.echelon.split("-")[0]))
        elif ligne.echelon == "unique":
            rangs.append(1)
        else:
            rangs.append(plus_haut[ligne.groupe] + 1
                         + (ligne.echelon == "exceptionnel" and ligne.groupe in speciaux))
    return rangs


# ---------------------------------------------------------------------------
# L'écriture
# ---------------------------------------------------------------------------

COLONNES = {
    "textes": ("texte", "versant", "numero", "nature", "signature", "debut", "fin", "titre",
               "tableaux_lus", "non_lus"),
    "tableaux": ("texte", "article", "numero", "tableau", "debut", "fin", "versions", "colonnes",
                 "lignes", "intro", "entete"),
    "lignes": ("texte", "article", "tableau", "ligne", "groupe", "echelon", "rang", "duree",
               "duree_moyenne", "duree_minimale", "duree_maximale", "condition"),
    "non_lus": ("texte", "article", "numero", "tableau", "debut", "fin", "motif"),
}
CLES_LIGNE = ("texte", "article", "tableau", "ligne")
SERIES = ("rang", "duree", "duree_moyenne", "duree_minimale", "duree_maximale")
ENTETES = {
    "textes": "Les textes qui fixent la durée des échelons, au LEGI : versant (« plusieurs » : "
              "un texte de plusieurs versants), numéro, nature, date de signature, vigueur ; "
              "les tableaux lus, et les tableaux ou articles non lus.",
    "tableaux": "Chaque tableau de durées d'échelon : l'article et la période où il le porte "
                "(fin exclue : le jour où la version suivante entre en vigueur ; vide : en "
                "vigueur), son rang dans l'article, les versions de l'article qui le redisent "
                "pendant cette période (article : la première), ses colonnes dans l'ordre de l'en-tête "
                "(unique, moyenne, minimale, maximale), la phrase qui l'annonce et son en-tête.",
    "lignes": "Chaque ligne d'un tableau : groupe (le grade, le libellé écrit avant elle), "
              "l'échelon, son rang (le numéro ; le spécial au-dessus du plus haut de son grade, "
              "l'exceptionnel au-dessus encore), les durées en mois que le tableau écrit (duree : "
              "la durée unique ; vide : le tableau n'a pas cette colonne, ou l'échelon le plus "
              "haut, qui n'en a pas), la condition d'accès que le tableau écrit à la place d'une "
              "durée.",
    "non_lus": "Les tableaux de durées que l'analyseur n'a pas lus, et les articles qui fixent "
               "des durées en phrases ou les renvoient à un autre texte (tableau vide), et "
               "pourquoi.",
}
SOURCE_ID = ("# source_id: dila_legi_durees — DILA, base LEGI, par l'index du dépôt "
             "(scripts/fetch/dila_index.py) ; scripts/fetch/dila_legi_durees.py")


def _cle_ligne(ligne: dict) -> str:
    return "|".join(ligne[c] for c in CLES_LIGNE)


def brut(extrait: dict) -> dict:
    """Le fichier brut de la certification : le rang et les durées de chaque
    ligne, sous la clé « texte|article|tableau|ligne »."""
    contenu: dict = {"source": extrait["source"], "recupere_le": date.today().isoformat(),
                     **{serie: {} for serie in SERIES}}
    for ligne in extrait["lignes"]:
        for serie in SERIES:
            if ligne[serie] != "":
                contenu[serie][_cle_ligne(ligne)] = int(ligne[serie])
    return contenu


def ecrire_reference(extrait: dict, dossier: Path = REFERENCE) -> None:
    """Les quatre fichiers. Les lignes gardent leur colonne ``fiabilite`` : vide
    pour une ligne neuve ou changée, la valeur qu'elle avait sinon — seul
    ``verifier_donnees.py`` la fait ``certifiee``."""
    dossier.mkdir(parents=True, exist_ok=True)
    for fichier, colonnes in COLONNES.items():
        chemin = dossier / f"{fichier}.csv"
        lignes = extrait[fichier]
        champs = list(colonnes)
        if fichier == "lignes":
            champs.append("fiabilite")
            anciennes = {}
            if chemin.exists():
                with chemin.open(encoding="utf-8") as flux:
                    for ligne in csv.DictReader(l for l in flux if not l.startswith("#")):
                        anciennes[_cle_ligne(ligne)] = ligne
            sorties = []
            for ligne in lignes:
                avant = anciennes.get(_cle_ligne(ligne), {})
                identique = all(avant.get(c) == ligne[c] for c in colonnes)
                sorties.append({**ligne, "fiabilite": avant.get("fiabilite", "")
                                if identique else ""})
            lignes = sorted(sorties, key=lambda l: (l["texte"], l["article"], int(l["tableau"]),
                                                    int(l["ligne"])))
        with chemin.open("w", encoding="utf-8", newline="") as flux:
            flux.write(f"# {ENTETES[fichier]}\n{SOURCE_ID}\n")
            redacteur = csv.DictWriter(flux, fieldnames=champs, lineterminator="\n")
            redacteur.writeheader()
            redacteur.writerows(lignes)


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--index", help="chemin de l'index LEGI (défaut : data/brut/dila/legi.sqlite)")
    options = analyseur.parse_args(arguments)
    try:
        extrait = extraire(options.index)
    except FileNotFoundError as erreur:
        print(f"Échec : {erreur}", file=sys.stderr)
        return 1
    ecrire_reference(extrait)
    BRUT.parent.mkdir(parents=True, exist_ok=True)
    BRUT.write_text(json.dumps(brut(extrait), ensure_ascii=False, indent=1, sort_keys=True),
                    encoding="utf-8")
    par_versant = collections.Counter(t["versant"] for t in extrait["textes"]
                                      if t["tableaux_lus"] != "0")
    motifs = collections.Counter(n["motif"].split(" « ")[0].split(" dans ")[0]
                                 for n in extrait["non_lus"])
    print(f"{len(extrait['textes'])} textes, dont {sum(par_versant.values())} avec un tableau "
          f"lu ({dict(sorted(par_versant.items()))}), {len(extrait['tableaux'])} tableaux, "
          f"{len(extrait['lignes'])} lignes ; {len(extrait['non_lus'])} non lus",
          file=sys.stderr)
    for motif, nombre in motifs.most_common(12):
        print(f"  {nombre:5d}  {motif}", file=sys.stderr)
    print(f"source : {extrait['source']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
