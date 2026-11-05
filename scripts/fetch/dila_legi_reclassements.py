#!/usr/bin/env python3
"""Les reclassements d'une grille indiciaire à la suivante, lus au LEGI.

    python scripts/fetch/dila_index.py legi --recuperer   # l'index, une fois
    python scripts/fetch/dila_legi_reclassements.py       # une minute
    python scripts/verifier_donnees.py --appliquer        # puis certifie

CE QU'UN RECLASSEMENT DIT. Quand un texte refait une grille — une réforme de
carrière, la fusion de deux corps, la création d'un cadre d'emplois —, il dit
où passe l'agent de chaque échelon de l'ancienne : « Les fonctionnaires […]
sont reclassés […] conformément au tableau de correspondance suivant ». Le
tableau donne, ligne par ligne, l'échelon d'origine, parfois partagé selon
l'ancienneté qu'on y a (« - à partir de 4 ans », « - avant 4 ans »), l'échelon
nouveau, et l'ancienneté d'échelon conservée : « Ancienneté acquise », « 1/2
de l'ancienneté acquise », « Sans ancienneté », « Ancienneté acquise majorée
d'un an »…, d'ordinaire « dans la limite de la durée de l'échelon » d'accueil.
Ces tableaux sont dans les statuts particuliers et les décrets qui organisent
les carrières, non dans les textes d'échelonnement que lit
``dila_legi_grilles.py``.

LA SOURCE. L'index LEGI du dépôt (``scripts/fetch/dila_index.py``), dont le
filtre garde depuis le 2 novembre 2026 les statuts particuliers, les
dispositions statutaires communes et l'organisation des carrières. Un article
y est son texte sans balises : le tableau n'est plus qu'une suite d'échelons et
de phrases d'ancienneté. ``lire_tableau`` la relit ligne à ligne ; le libellé
écrit entre deux lignes — le grade d'origine, puis le grade d'accueil, que
l'aplatissement colle l'un à l'autre — devient le groupe des lignes qui
suivent ; ce qui précède la première ligne, l'en-tête, jusqu'à son dernier mot
d'en-tête (« SITUATION NOUVELLE », « … dans la limite de la durée de
l'échelon »).

CE QUI EST RETENU, ET CE QUI EST REFUSÉ. Seul compte le passage d'une grille à
la suivante : la phrase qui annonce le tableau dit « reclassés » ou
« intégrés ». Le même tableau sert à classer un agent promu ou recruté : ces
tableaux-là ne sont pas des reclassements, et ne sont pas lus. Sont refusés,
plutôt que lus de travers, et consignés dans ``non_lus.csv`` : une ligne sans
ancienneté (les tableaux d'assimilation pour la pension, qui n'en ont pas ;
les échelons comptés en indices), un tableau dessiné en caractères, un échelon
d'origine en double ou dans le désordre, un échelon nouveau qui baisse quand
l'ancien monte, un tableau d'une seule ligne.

CE QU'IL ÉCRIT, sous ``data/reference/grilles/reclassements/`` :
``textes.csv``, les textes qui portent un tableau, avec leur versant (lu comme
celui des grilles, au titre puis aux visas) ; ``tableaux.csv``, chaque tableau,
avec la phrase qui l'annonce, son en-tête et sa date ; ``lignes.csv``, chaque
ligne ; ``non_lus.csv``, les tableaux refusés et pourquoi. Et
``data/brut/dila_legi_reclassements.json``, le rang des échelons d'origine et
d'accueil, que ``scripts/verifier_donnees.py`` confronte aux fichiers.

CE QUE LA DONNÉE DIT, ET NE DIT PAS. Un tableau vaut à la date de son
reclassement : celle que la phrase écrit (« sont, au 1er août 1993,
intégrés »), sinon celle qu'un autre article du décret lui donne, lue à la main
(``DATES_D_UN_AUTRE_ARTICLE``), sinon l'entrée en vigueur de l'article (``debut``) ; les versions
suivantes d'un article qui redisent le même tableau ne font pas un second
reclassement. L'ancienneté conservée se garde « dans la limite de la durée de
l'échelon » : l'appliquer demande les durées d'échelon, que les statuts
fixent et que le dépôt n'a pas encore. Les grilles d'origine et d'accueil ne
sont nommées que par le libellé du tableau et la phrase qui l'annonce ;
``dila_legi_chainage.py`` les rattache aux grilles du Noyau RH quand le texte
le prouve, à l'État seulement (``grilles/chainage/reclassements.csv``).
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

BRUT = RACINE / "data" / "brut" / "dila_legi_reclassements.json"
REFERENCE = RACINE / "data" / "reference" / "grilles" / "reclassements"
EN_VIGUEUR = "2999-01-01"

MOIS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
        "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11,
        "decembre": 12}

# ---------------------------------------------------------------------------
# Le vocabulaire des tableaux
# ---------------------------------------------------------------------------

APOS = r"['’]\s*"
_NOMBRE = (r"(?:\d{1,2}|un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix-huit|dix"
           r"|onze|douze|trente)")
#: Une durée : « 4 ans », « un an », « 2 ans 6 mois », « 1 an et 6 mois », « 33 mois ».
DUREE = (rf"{_NOMBRE}\s+(?:ans?|mois)(?:\s*(?:et\s+)?{_NOMBRE}\s+mois)?(?:\s+et\s+demi)?")
#: La part de l'ancienneté conservée : « 1/2 de », « 5/6e de », « la moitié de »,
#: « deux fois », « le double de ».
FRACTION = (r"(?:\d{1,2}\s*/\s*\d{1,2}\s*(?:[eè]mes?|e)?|(?:la\s+)?moiti[ée]|(?:le\s+)?tiers"
            r"|(?:les\s+)?deux\s+tiers|(?:le\s+)?quart|(?:les\s+)?trois\s+quarts|un\s+demi"
            r"|(?:le\s+)?double|(?:deux|trois|quatre)\s+fois|une\s+fois\s+et\s+demie)")
#: La limite de l'ancienneté conservée : « la durée de l'échelon d'accueil »,
#: « l'échelon d'accueil ».
_LIMITE = (rf"(?:la\s+dur[ée]e\s+(?:(?:maximale|moyenne|minimale)\s+)?(?:de\s+l{APOS}|d{APOS})"
           rf"|l{APOS})[ée]chelon"
           rf"(?:\s+d{APOS}accueil)?")
#: Ce qui suit l'ancienneté : majorée, diminuée, au-delà de, dans la limite de…
_SUITE = (rf"\s*,?\s*(?:major[ée]e?s?|minor[ée]e?s?|diminu[ée]e?s?|r[ée]duite?s?"
          rf"|augment[ée]e?s?)\s+(?:de\s+|d{APOS})(?:{DUREE})"
          rf"|\s*,?\s*au[- ]del[àa]\s+(?:de\s+|d{APOS})(?:{DUREE})"
          rf"|\s*,?\s*(?:moins|plus)\s+(?:{DUREE})"
          rf"|\s*,?\s*dans\s+la\s+limite\s+(?:de\s+|d{APOS})(?:{DUREE}|{_LIMITE})"
          rf"|\s*,?\s*limit[ée]e\s+à\s+(?:{DUREE})")
ANCIENNETE = (
    rf"sans\s+anciennet[ée]"
    rf"|(?:{FRACTION}\s+(?:de\s+)?l{APOS})?anciennet[ée]\s+"
    rf"(?:d{APOS}[ée]chelon\s+|dans\s+l{APOS}[ée]chelon\s+|à\s+l{APOS}[ée]chelon\s+)?"
    rf"(?:acquise|conserv[ée]e|maintenue)(?:\s+(?:acquise|conserv[ée]e|maintenue))?"
    rf"(?:{_SUITE})*")
#: Ce qui partage un échelon d'origine selon l'ancienneté qu'on y a.
CONDITION = (
    rf"(?:[àa]\s+partir\s+(?:de\s+|d{APOS})|apr[èe]s|avant|jusqu{APOS}à|moins\s+de|plus\s+de"
    rf"|au\s+moins|[ée]gale?\s+ou\s+sup[ée]rieure?\s+à|sup[ée]rieure?\s+ou\s+[ée]gale?\s+à"
    rf"|inf[ée]rieure?\s+à|entre\s+{_NOMBRE}\s+(?:ans?\s+|mois\s+)?et)\s*(?:{DUREE})")
#: Un échelon : « 11e échelon », « 1 er échelon », « Echelon 7 », « échelon
#: spécial », « Echelon unique », « 2e échelon provisoire », « stagiaire ».
ECHELON = (
    r"\b(?P<numero>\d{1,2})\s*(?:er|re|ère|e|ème|eme)?\s*[ée]chelon\b"
    r"(?:\s+(?P<provisoire>provisoire)\b)?"
    r"|\b[ée]chelon\s+(?P<numero_apres>\d{1,2})\b(?!\s*(?:er|e|ème)?\s*[ée]chelon)"
    r"|\b[ée]chelon\s+(?P<nom>sp[ée]cial|exceptionnel|unique)\b"
    r"|\b(?P<stagiaire>stagiaire)s?\b")
JETONS = re.compile(rf"(?P<anc>{ANCIENNETE})|(?P<cond>{CONDITION})|(?P<ech>{ECHELON})",
                    re.IGNORECASE)
#: La fin de l'en-tête : son dernier mot d'en-tête ; ce qui le suit nomme le
#: premier groupe de lignes.
MOTS_D_ENTETE = re.compile(
    rf"situation\s+(?:nouvelle|ancienne|actuelle|d{APOS}origine)\b"
    rf"|(?:nouvelle|ancienne)\s+situation\b"
    rf"|anciennet[ée](?:\s+d{APOS}[ée]chelon)?(?:\s+(?:conserv[ée]e|acquise|maintenue))?"
    rf"(?:\s+\(?dans\s+la\s+limite\s+de\s+{_LIMITE}\)?|\s+dans\s+(?:le\s+nouveau\s+grade|le\s+grade"
    rf"\s+d{APOS}accueil|l{APOS}[ée]chelon\s+d{APOS}accueil|le\s+nouvel\s+[ée]chelon))?"
    rf"|grade\s+d{APOS}(?:origine|int[ée]gration|accueil)\b|\b[ée]chelons?\b",
    re.IGNORECASE)
#: Les titres de colonnes qu'une ligne redit (« SITUATION NOUVELLE : »), et les
#: renvois (« (B) ») : ni une condition, ni un groupe.
BRUIT = re.compile(r"\b(?:situations?|actuelles?|nouvelles?|anciennet[ée]s?|anciennes?"
                   r"|d['’]\s*origine|[ée]chelons?)\b|\(\s*\w{1,2}\s*\)|[=:;,.()\-–—―]",
                   re.IGNORECASE)
#: Le titre de la colonne d'ancienneté, quand une ligne le redit devant sa case.
TITRE_ANCIENNETE = re.compile(r"anciennet[ée]\s+(?:d['’]\s*[ée]chelon\s+)?conserv[ée]e\s*,?\s*"
                              r"dans\s+la\s+limite\s+de\s+la\s+dur[ée]e.*", re.IGNORECASE)
CARACTERES = re.compile(r":-{4,}|-{6,}|: \d{3} :")
#: Le début d'un tableau : la phrase qui l'annonce finit par « : ».
DEBUT_TABLEAU = re.compile(r"\btableaux?\b[^:]{0,300}?:", re.IGNORECASE)
RECLASSEMENT = re.compile(r"reclass|int[ée]gr", re.IGNORECASE)
#: Un promu reclassé dans son nouveau grade n'a pas changé de grille.
PROMOTION = re.compile(r"\bpromu|\bavancement\b", re.IGNORECASE)
_DATE = (r"(?P<jour>1\s*er|\d{1,2})\s+(?P<mois>janvier|f[ée]vrier|mars|avril|mai|juin|juillet"
         r"|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre)\s+(?P<annee>\d{4})")
#: La date du reclassement : « A compter du 1er janvier 2017 », « sont, au
#: 1er août 1993, intégrés », « sont reclassés, au 1er janvier 2017, conformément
#: au tableau », « reclassés avec effet au », « Avec une date d'effet au », « reclassés
#: dans le grade de dessinateur projeteur en chef au 1er août 1996 » (action 158, B5) ;
#: non la date d'un texte cité, ni celle d'une nomination ou d'une position (« nommés
#: au », « placés au »).
EFFETS = (
    re.compile(rf"(?:[àa]\s+compter\s+du|[àa]\s+partir\s+du|[àa]\s+la\s+date\s+du"
               rf"|avec\s+(?:une\s+date\s+d['’]\s*)?effet\s+au)\s+{_DATE}", re.IGNORECASE),
    re.compile(rf"\bau\s+{_DATE}\s*,?\s*(?=(?:\w+\s+)?(?:reclass|int[ée]gr))", re.IGNORECASE),
    re.compile(rf"\b(?:reclass|int[ée]gr)\w*\s*,?\s+au\s+{_DATE}", re.IGNORECASE),
    re.compile(rf"\breclass\w*\s+dans\s+le\s+grade\s+d[e'’]\s*[^,:;()]{{1,80}}?\s+au\s+{_DATE}",
               re.IGNORECASE),
)


#: Le tableau dont la phrase n'écrit pas la date, qu'un autre article du même décret
#: date (action 158, B5-bis, relecture R-B5) : l'article du tableau (LEGIARTI) → la
#: date, l'article qui la donne, à la version qui couvre celle du tableau, et ses mots.
DATES_D_UN_AUTRE_ARTICLE = {
    "LEGIARTI000006506606": ("1995-08-01", "LEGIARTI000006506628",  # n° 98-268, art. 17
                             "Les articles 17, 18, 21 et 22 du présent décret prennent effet "
                             "au 1er août 1995."),
    "LEGIARTI000006567682": ("1997-01-01", "LEGIARTI000006567685",  # n° 2001-325, art. 14
                             "Les dispositions des articles 1er, 4, 5, 6 du I de l'article 7, "
                             "des articles 8, 9, 10, 11, 14 et 15 du présent décret prennent "
                             "effet au 1er janvier 1997."),
    "LEGIARTI000035601659": ("2017-01-01", "LEGIARTI000035601611",  # n° 2017-1367, art. 23
                             "Le chapitre Ier, à l'exception du troisième alinéa de l'article 2, "
                             "et les articles 23 à 25 entrent en vigueur le 1er janvier 2017."),
    "LEGIARTI000035900888": ("2017-01-01", "LEGIARTI000035900898",  # n° 2017-1494, art. 13
                             "Les dispositions du chapitre II, à l'exception de celles des "
                             "articles 4, 5 et 7, et les dispositions du I de l'article 13 "
                             "entrent en vigueur le 1er janvier 2017."),
}


def effet_du_tableau(article: str, intro: str) -> str:
    """La date du reclassement : celle que la phrase écrit, sinon celle qu'un autre
    article du décret donne au tableau, sinon rien (l'entrée en vigueur de l'article)."""
    return date_effet(intro) or DATES_D_UN_AUTRE_ARTICLE.get(article, ("",))[0]


def _sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texte)
                   if not unicodedata.combining(c))


def _propre(texte: str) -> str:
    return re.sub(r"\s+", " ", texte).strip(" :;,.-–—― ")


def date_effet(intro: str) -> str:
    """La date du reclassement que la phrase écrit, ou rien."""
    trouves = [t for t in (motif.search(intro) for motif in EFFETS) if t]
    if not trouves:
        return ""
    trouve = min(trouves, key=lambda t: t.start())
    jour = 1 if re.match(r"1\s*er", trouve.group("jour")) else int(trouve.group("jour"))
    return date(int(trouve.group("annee")), MOIS[_sans_accents(trouve.group("mois")).lower()],
                jour).isoformat()


# ---------------------------------------------------------------------------
# L'analyseur
# ---------------------------------------------------------------------------

@dataclass
class Ligne:
    groupe: str
    origine: str
    condition: str = ""
    nouveau: str = ""
    anciennete: str = ""


@dataclass
class Tableau:
    entete: str = ""
    lignes: list[Ligne] = field(default_factory=list)
    refus: str = ""


@dataclass
class Extrait:
    intro: str
    corps: str
    reclassement: bool


def _echelon(trouve: re.Match) -> str:
    numero = trouve.group("numero") or trouve.group("numero_apres")
    if numero:
        return f"{int(numero)}-provisoire" if trouve.group("provisoire") else str(int(numero))
    if trouve.group("nom"):
        return _sans_accents(trouve.group("nom")).lower()
    return "stagiaire"


#: Le rang d'un échelon sans numéro : le stagiaire sous le premier, l'échelon
#: unique au premier ; le spécial et l'exceptionnel au-dessus du plus haut.
RANGS = {"stagiaire": 0, "unique": 1}
AU_DESSUS = {"special": 1, "exceptionnel": 2}


def _ordre(echelon: str) -> float:
    if echelon in RANGS:
        return RANGS[echelon]
    if echelon in AU_DESSUS:
        return 100 + AU_DESSUS[echelon]
    numero, _, provisoire = echelon.partition("-")
    return int(numero) - (0.5 if provisoire else 0)


def _elements(corps: str) -> list[tuple[str, str, int, int, re.Match | None]]:
    """Le tableau en éléments : les échelons, les anciennetés, les conditions,
    et le texte libre entre eux."""
    elements, fin = [], 0
    for trouve in JETONS.finditer(corps):
        if _propre(corps[fin:trouve.start()]):
            elements.append(("libre", corps[fin:trouve.start()], fin, trouve.start(), None))
        genre = next(g for g in ("anc", "cond", "ech") if trouve.group(g) is not None)
        elements.append((genre, trouve.group(), trouve.start(), trouve.end(), trouve))
        fin = trouve.end()
    if _propre(corps[fin:]):
        elements.append(("libre", corps[fin:], fin, len(corps), None))
    return elements


def _bruit(texte: str) -> bool:
    return not BRUIT.sub("", texte).strip()


def _entete_et_groupe(libelle: str) -> tuple[str, str]:
    """L'en-tête finit à son dernier mot d'en-tête ; ce qui suit nomme le groupe."""
    fins = [m.end() for m in MOTS_D_ENTETE.finditer(libelle)]
    if not fins:
        return libelle, ""
    return _propre(libelle[:fins[-1]]), _propre(libelle[fins[-1]:])


def lire_tableau(corps: str) -> Tableau:
    """Les lignes d'un tableau de reclassement aplati : échelon d'origine,
    condition, échelon nouveau, ancienneté conservée, et le groupe que nomme
    le libellé écrit avant elles."""
    tableau = Tableau()
    if CARACTERES.search(corps):
        tableau.refus = "tableau dessiné en caractères"
        return tableau
    lignes: list[Ligne] = []
    courante: Ligne | None = None
    groupe, entete, attente = "", None, None
    for genre, texte, debut, fin, trouve in _elements(corps):
        complete = courante is not None and bool(courante.nouveau and courante.anciennete)
        if genre == "ech":
            echelon = _echelon(trouve)
            if courante is None or complete:
                if complete:
                    lignes.append(courante)
                if attente:
                    libelle = _propre(corps[attente[0]:attente[1]])
                    if entete is None and not lignes:
                        entete, groupe = _entete_et_groupe(libelle)
                    elif not _bruit(libelle):
                        groupe = libelle
                    attente = None
                courante = Ligne(groupe, echelon)
            elif not courante.nouveau:
                courante.nouveau = echelon
            else:
                tableau.refus = f"ligne sans ancienneté : l'échelon « {texte} » suit l'échelon nouveau"
                return tableau
        elif (complete and genre == "anc" and attente is None
              and TITRE_ANCIENNETE.fullmatch(courante.anciennete)):
            courante.anciennete = _propre(texte)     # le titre redit, puis la case
        elif courante is None or (complete and (attente or genre != "cond")):
            attente = [debut, fin] if attente is None else [attente[0], fin]
        elif complete:
            lignes.append(courante)
            courante = Ligne(courante.groupe, courante.origine, _propre(texte))
        elif not courante.nouveau:
            if not _bruit(texte):
                courante.condition = _propre(courante.condition + " " + texte)
        elif genre == "anc":
            courante.anciennete = _propre(texte)
        else:
            tableau.refus = f"ligne sans ancienneté : « {_propre(texte)[:50]} » suit l'échelon nouveau"
            return tableau
    if courante is not None:
        if not (courante.nouveau and courante.anciennete):
            tableau.refus = "ligne sans ancienneté : la dernière"
            return tableau
        lignes.append(courante)
    tableau.entete = entete or ""
    tableau.lignes = lignes
    tableau.refus = _controler(lignes)
    if tableau.refus:
        tableau.lignes = []
    return tableau


def _controler(lignes: list[Ligne]) -> str:
    """Ce qui trahit une lecture fausse : une seule ligne, un échelon d'origine
    en double ou dans le désordre, un échelon nouveau qui baisse quand l'ancien
    monte, groupe par groupe."""
    if len(lignes) < 2:
        return "moins de deux lignes"
    groupes: dict[str, list[Ligne]] = collections.defaultdict(list)
    for ligne in lignes:
        groupes[ligne.groupe].append(ligne)
    for nom, liste in groupes.items():
        origines = [_ordre(l.origine) for l in liste]
        distincts = [o for k, o in enumerate(origines) if k == 0 or o != origines[k - 1]]
        if len(set(distincts)) != len(distincts):
            return f"échelon d'origine en double dans « {nom[:60]} »"
        if len(distincts) < 2:
            continue
        sens = 1 if distincts[1] > distincts[0] else -1
        if any((b - a) * sens <= 0 for a, b in zip(distincts, distincts[1:])):
            return f"échelons d'origine dans le désordre dans « {nom[:60]} »"
        # D'un échelon d'origine au suivant, l'échelon nouveau ne baisse pas ;
        # un échelon partagé selon l'ancienneté mène à plusieurs.
        accueils: dict[float, list[float]] = collections.defaultdict(list)
        for origine, ligne in zip(origines, liste):
            accueils[origine].append(_ordre(ligne.nouveau))
        montee = sorted(accueils)
        if any(max(accueils[a]) > min(accueils[b]) for a, b in zip(montee, montee[1:])):
            return f"échelon nouveau qui baisse dans « {nom[:60]} »"
    return ""


def tableaux(article: str) -> list[Extrait]:
    """Les tableaux d'un article, chacun avec la phrase qui l'annonce ; seul est
    un reclassement celui dont la phrase dit « reclassés » ou « intégrés »."""
    debuts = list(DEBUT_TABLEAU.finditer(article))
    extraits = []
    for k, trouve in enumerate(debuts):
        avant = debuts[k - 1].end() if k else 0
        point = article.rfind(". ", avant, trouve.start())
        intro = _propre(article[(point + 2 if point >= 0 else avant):trouve.end()]) + " :"
        fin = debuts[k + 1].start() if k + 1 < len(debuts) else len(article)
        extraits.append(Extrait(intro, article[trouve.end():fin],
                                bool(RECLASSEMENT.search(intro))
                                and not PROMOTION.search(intro)))
    return extraits


# ---------------------------------------------------------------------------
# Les articles de l'index
# ---------------------------------------------------------------------------

#: Les articles qui reclassent : les mots de l'index, sans accents.
REQUETE = " OR ".join(f"texte:{mot}" for mot in (
    "reclasses", "reclassees", "reclasse", "reclassee", "reclassement", "integres", "integrees"))
#: Le titre d'un texte de la fonction publique : un statut, un corps, un cadre
#: d'emplois, l'organisation des carrières, un échelonnement.
FONCTION_PUBLIQUE = re.compile(
    r"statuts?\b|\bcorps\b|cadres?\s+d['’]emplois|carri[èe]res|fonctionnaires|[ée]chelonnement"
    r"|classement\s+indiciaire|\bgrades?\b|\bemplois?\b|personnels?\b|indices?\s+de\s+solde",
    re.IGNORECASE)
NON_REPRODUIT = re.compile(r"consulter\s+le\s+tableau|non\s+reproduit", re.IGNORECASE)
#: Le moins d'échelons qu'un tableau de reclassement nomme.
ECHELONS_MINIMUM = 4
_UN_ECHELON = re.compile(ECHELON, re.IGNORECASE)


def _rangs(lignes: list[Ligne], cote: str) -> list[int]:
    """Le rang de chaque échelon d'un côté du tableau : son numéro ; zéro pour
    le stagiaire, un pour l'échelon unique ; le spécial au-dessus du plus haut
    de son groupe, l'exceptionnel au-dessus encore."""
    plus_haut: dict[str, int] = collections.defaultdict(int)
    speciaux: set[str] = set()
    for ligne in lignes:
        echelon = getattr(ligne, cote)
        if echelon[0].isdigit():
            plus_haut[ligne.groupe] = max(plus_haut[ligne.groupe], int(echelon.split("-")[0]))
        elif echelon == "special":
            speciaux.add(ligne.groupe)
    rangs = []
    for ligne in lignes:
        echelon = getattr(ligne, cote)
        if echelon[0].isdigit():
            rangs.append(int(echelon.split("-")[0]))
        elif echelon in RANGS:
            rangs.append(RANGS[echelon])
        else:
            rangs.append(plus_haut[ligne.groupe] + 1
                         + (echelon == "exceptionnel" and ligne.groupe in speciaux))
    return rangs


def _texte_de(titre: str, info: dict) -> dict:
    from dila_legi_grilles import numero, versant, _signature  # noqa: PLC0415
    return {"texte": info["texte"], "versant": versant(titre, info["visas"]) or "plusieurs",
            "numero": numero(titre), "nature": info["nature"], "signature": _signature(titre),
            "debut": info["debut"], "fin": _fin(info["fin"]), "titre": titre}


def _fin(jour: str) -> str:
    return "" if not jour or jour >= EN_VIGUEUR else jour


def extraire(chemin_index: Path | str | None = None) -> dict:
    """Les reclassements que l'index LEGI garde : les textes, les tableaux,
    leurs lignes et les refus."""
    import dila_index  # noqa: PLC0415

    db, source = dila_index.ouvrir_lecture("legi", str(chemin_index) if chemin_index else None)
    articles = db.execute(
        "SELECT d.id, d.date, d.fin, d.num, d.titre, d.texte FROM fts JOIN doc d "
        "ON d.rowid = fts.rowid WHERE fts MATCH ? AND d.nature LIKE 'Article%' "
        "ORDER BY d.date, d.id", (REQUETE,)).fetchall()
    titres = {a[4] for a in articles if FONCTION_PUBLIQUE.search(a[4] or "")}
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
        for rang, extrait in enumerate((e for e in tableaux(contenu) if e.reclassement), 1):
            if NON_REPRODUIT.search(extrait.corps[:400]):
                motif = "tableau non reproduit au LEGI"
            elif len(_UN_ECHELON.findall(extrait.corps)) < ECHELONS_MINIMUM:
                continue
            else:
                tableau = lire_tableau(extrait.corps)
                motif = tableau.refus
            if motif:
                non_lus.append({"texte": texte, "article": ident, "numero": numero,
                                "tableau": str(rang), "debut": debut, "fin": _fin(fin),
                                "motif": motif})
                continue
            cle = (texte, numero, rang)
            contenu_lu = [tuple(vars(l).values()) for l in tableau.lignes]
            avant = lus.get(cle)
            if avant and avant["contenu"] == contenu_lu and avant["fin"] == debut:
                avant["fin"] = fin            # la version suivante redit le même tableau
                continue
            if avant:
                cle = (texte, numero, rang, debut)
            lus[cle] = {"texte": texte, "article": ident, "numero": numero, "tableau": str(rang),
                        "debut": debut, "fin": fin, "effet": effet_du_tableau(ident, extrait.intro),
                        "intro": extrait.intro, "entete": tableau.entete,
                        "lignes": tableau.lignes, "contenu": contenu_lu}

    extrait_final: dict = {"source": source, "textes": [], "tableaux": [], "lignes": [],
                           "non_lus": sorted(non_lus, key=lambda n: (n["texte"], n["numero"],
                                                                     n["debut"], n["tableau"]))}
    comptes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for lu in sorted(lus.values(), key=lambda l: (l["texte"], l["debut"], l["article"],
                                                  int(l["tableau"]))):
        comptes[lu["texte"]]["lus"] += 1
        extrait_final["tableaux"].append({
            "texte": lu["texte"], "article": lu["article"], "numero": lu["numero"],
            "tableau": lu["tableau"], "debut": lu["debut"], "fin": _fin(lu["fin"]),
            "effet": lu["effet"], "lignes": str(len(lu["lignes"])), "intro": lu["intro"],
            "entete": lu["entete"]})
        for (n, ligne), origine, nouveau in zip(
                enumerate(lu["lignes"], 1), _rangs(lu["lignes"], "origine"),
                _rangs(lu["lignes"], "nouveau")):
            extrait_final["lignes"].append({
                "texte": lu["texte"], "article": lu["article"], "tableau": lu["tableau"],
                "ligne": str(n), "groupe": ligne.groupe, "origine": ligne.origine,
                "condition": ligne.condition, "nouveau": ligne.nouveau,
                "anciennete": ligne.anciennete, "rang_origine": str(origine),
                "rang_nouveau": str(nouveau)})
    for refus in non_lus:
        comptes[refus["texte"]]["non_lus"] += 1
    par_texte = {info["texte"]: titre for titre, info in infos.items()}
    for texte in sorted(comptes):
        titre = par_texte[texte]
        extrait_final["textes"].append({**_texte_de(titre, infos[titre]),
                                        "tableaux_lus": str(comptes[texte]["lus"]),
                                        "tableaux_non_lus": str(comptes[texte]["non_lus"])})
    extrait_final["textes"].sort(key=lambda t: (t["versant"], t["signature"], t["texte"]))
    return extrait_final


# ---------------------------------------------------------------------------
# L'écriture
# ---------------------------------------------------------------------------

COLONNES = {
    "textes": ("texte", "versant", "numero", "nature", "signature", "debut", "fin", "titre",
               "tableaux_lus", "tableaux_non_lus"),
    "tableaux": ("texte", "article", "numero", "tableau", "debut", "fin", "effet", "lignes",
                 "intro", "entete"),
    "lignes": ("texte", "article", "tableau", "ligne", "groupe", "origine", "condition",
               "nouveau", "anciennete", "rang_origine", "rang_nouveau"),
    "non_lus": ("texte", "article", "numero", "tableau", "debut", "fin", "motif"),
}
CLES_LIGNE = ("texte", "article", "tableau", "ligne")
ENTETES = {
    "textes": "Les textes qui reclassent les agents d'une grille à la suivante, au LEGI : "
              "versant (« plusieurs » : un texte des deux versants), numéro, nature, date de "
              "signature, vigueur ; les tableaux lus et non lus.",
    "tableaux": "Chaque tableau de reclassement : l'article et sa version (fin incluse ; vide : "
                "en vigueur), son rang dans l'article, effet (la date que la phrase écrit, ou "
                "qu'un autre article du décret donne ; vide : l'entrée en vigueur de "
                "l'article, debut), la phrase qui l'annonce et "
                "son en-tête.",
    "lignes": "Chaque ligne d'un tableau : groupe (le libellé écrit avant elle : grade "
              "d'origine puis grade d'accueil, que le texte aplati colle), l'échelon d'origine, "
              "la condition d'ancienneté qui le partage, l'échelon nouveau, l'ancienneté "
              "conservée telle que le texte l'écrit. rang : le numéro de l'échelon ; zéro le "
              "stagiaire, un l'échelon unique, le spécial et l'exceptionnel au-dessus du plus "
              "haut de leur groupe.",
    "non_lus": "Les tableaux de reclassement que l'analyseur n'a pas lus, et pourquoi.",
}
SOURCE_ID = ("# source_id: dila_legi_reclassements — DILA, base LEGI, par l'index du dépôt "
             "(scripts/fetch/dila_index.py) ; scripts/fetch/dila_legi_reclassements.py")


def _cle_ligne(ligne: dict) -> str:
    return "|".join(ligne[c] for c in CLES_LIGNE)


def brut(extrait: dict) -> dict:
    """Le fichier brut de la certification : le rang des échelons d'origine et
    d'accueil de chaque ligne, sous la clé « texte|article|tableau|ligne »."""
    contenu: dict = {"source": extrait["source"], "recupere_le": date.today().isoformat(),
                     "rang_origine": {}, "rang_nouveau": {}}
    for ligne in extrait["lignes"]:
        for serie in ("rang_origine", "rang_nouveau"):
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
    par_versant = collections.Counter(t["versant"] for t in extrait["textes"])
    print(f"{len(extrait['textes'])} textes ({dict(sorted(par_versant.items()))}), "
          f"{len(extrait['tableaux'])} tableaux, {len(extrait['lignes'])} lignes ; "
          f"{len(extrait['non_lus'])} tableaux non lus", file=sys.stderr)
    print(f"source : {extrait['source']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
