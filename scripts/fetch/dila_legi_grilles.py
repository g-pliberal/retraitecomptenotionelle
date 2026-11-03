#!/usr/bin/env python3
"""Les grilles indiciaires de la territoriale et de l'hospitalière, lues au LEGI.

    python scripts/fetch/dila_index.py legi --recuperer   # l'index, une fois
    python scripts/fetch/dila_legi_grilles.py             # une minute
    python scripts/verifier_donnees.py --appliquer        # puis certifie

LA SOURCE. Aucune base ouverte ne date les grilles de la fonction publique
territoriale ni de l'hospitalière (action 158, étape 1) : leur source est le
texte qui fixe l'échelonnement indiciaire de chaque cadre d'emplois ou corps,
décret ou arrêté, dont la base LEGI de la DILA garde chaque version d'article
depuis sa première version consolidée. Le script lit l'index LEGI du dépôt
(``scripts/fetch/dila_index.py``), dont le filtre garde ces textes depuis sa
reconstruction du 2 novembre 2026.

CE QUE L'INDEX EN GARDE. Un article y est son texte débarrassé des balises :
le tableau n'est plus qu'une suite de mots et de nombres, où les cases vides
ont disparu. ``lire_tableau`` le relit : les échelons (« 10e échelon »,
« Echelon 7 », « Echelon spécial », ou le rang nu devant son indice), leurs
valeurs — l'indice brut, la lettre de hors-échelle, « Néant » ou la barre
oblique pour l'échelon qui n'existe pas —, les dates en tête des colonnes
(« A compter du 1er janvier 2017 »), les groupes, grade ou échelle, entre
les lignes, ou les échelles en colonnes. Une ligne plus courte que les autres
n'a pas dit où était sa case vide : s'il s'agit de la première ligne de son
groupe, l'échelon le plus haut, ses valeurs vont aux dernières colonnes —
l'échelon créé à la dernière date — et le tableau le note ; ailleurs, le
tableau est refusé. Refusés aussi, et jamais lus de travers : les tableaux de
reclassement, ceux dessinés en caractères (les textes d'avant 1995 surtout),
ceux d'indices majorés, une ligne de plus de valeurs que de colonnes, un
échelon en double, un indice qui baisse quand l'échelon monte.

CE QU'IL ÉCRIT. Sous ``data/reference/grilles/territoriale/`` et
``.../hospitaliere/`` : ``textes.csv``, les textes lus ; ``grilles.csv``, les
grilles de chaque texte, une par groupe ; ``echelons.csv``, l'indice brut de
chaque échelon, période par période, avec l'article qui le fixe ;
``non_lus.csv``, les versions d'articles que l'analyseur a refusées, et
pourquoi. Et ``data/brut/dila_legi_grilles.json`` : les indices que
``scripts/verifier_donnees.py`` confronte aux fichiers de référence.

CE QUE LA DONNÉE DIT, ET NE DIT PAS. Une période commence à la date d'effet
de sa colonne, ou de sa version si elle est plus tardive, et finit à la veille
de la suivante : une colonne annoncée qu'une version suivante a remplacée
avant son effet ne s'applique jamais. Les durées d'échelon ne sont pas dans
ces textes, mais dans les statuts particuliers ; le reclassement d'une grille
à la suivante, dans les textes qui les refont. Avant la première version
consolidée d'un texte, le LEGI ne dit rien : ce que les textes plus anciens
écrivaient reste au JORF.
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
from datetime import date, timedelta
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

BRUT = RACINE / "data" / "brut" / "dila_legi_grilles.json"
REFERENCE = RACINE / "data" / "reference" / "grilles"
VERSANTS = {"territoriale": "FPT", "hospitaliere": "FPH"}
EN_VIGUEUR = "2999-01-01"
#: L'indice brut le plus haut : 1 027 au sommet de l'échelle, avant les lettres
#: de la hors-échelle ; 2 074 depuis que la réforme de la haute fonction
#: publique numérote au-delà (décret n° 2021-1550 et ceux qui le suivent).
INDICE_MAXIMAL = 2200

MOIS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
        "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11,
        "decembre": 12}

#: Les jetons d'un tableau aplati, dans l'ordre où ils se reconnaissent.
JETONS = re.compile(r"""
    (?P<jusque>jusqu'(?:au|à)\s+(?:1\s*er|premier|\d{1,2})\s+
        (?:janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre|octobre|novembre
           |d[ée]cembre)\s+(?:19|20)\d\d\b)
  | (?P<date>(?:[àa]\s+compter\s+du|[àa]\s+partir\s+du|depuis\s+le|au)\s+
        (?P<jour>1\s*er|premier|\d{1,2})\s+
        (?P<mois>janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre
                 |octobre|novembre|d[ée]cembre)\s+(?P<an>(?:19|20)\d\d)\b)
  | (?P<duree>\b\d{1,2}\s+ans?(?:\s+(?:et\s+)?\d{1,2}\s+mois)?\b|\b\d{1,2}\s+mois\b)
  | (?P<echelon>\b(?P<rang>\d{1,2})\s*(?:er|re|ère|e|è|ème|eme)\s+[ée]chelon\b
                  (?P<provisoire>\s+provisoire)?
              | \b[ée]chelon\s+(?P<rang2>\d{1,2})\b(?P<provisoire2>\s+provisoire)?
              | \b[ée]chelon\s+(?P<special>sp[ée]cial|exceptionnel|fonctionnel)\b
              | (?<![\w'])(?P<special2>sp[ée]cial)\b
              | (?<![\w'])(?P<stage>stagiaire|[ée]l[èe]ve)\b
              | \b(?P<rang3>\d{1,2})\s*(?:er|re|ère|e|è|ème|eme)(?![\w']))
  | (?P<he>\bHE\s?(?P<lettre>[A-G])(?P<bis>\s?bis)?\b
         | \bhors[- ][ée]chelle\s+(?P<lettre2>[A-G])(?P<bis2>\s?bis)?\b)
  | (?P<valeur>(?<![\w,.-])(?:1[.\s]0\d\d|\d{3,4}(?!\.\d)))(?:\.(?!\d))?(?![\w,-])
  | (?P<vide>\bn[ée]ant\b|(?<!\S)(?:/|—|–|-)(?!\S))
  | (?P<nombre>(?<![\w,.-])\d{1,2})(?![\w,-])
  | (?P<renvoi>\(\d{1,2}\)|\(\*+\)|\*+|:)
  | (?P<mot>\S+)
""", re.IGNORECASE | re.VERBOSE)
GENRES = ("jusque", "date", "duree", "echelon", "he", "valeur", "vide", "nombre", "renvoi", "mot")

#: Les mots d'en-tête que le tableau répète et qui ne nomment aucun groupe.
ENTETE_GENERIQUE = re.compile(
    r"\b(?:GRADES|[ÉE]CHELLES|[ÉE]CHELONS|EMPLOIS)\s+ET\s+[ÉE]CHELONS\b"
    r"|\((?:indices?\s+bruts?)\)|\b(?:indices?\s+bruts?)\b"
    r"|\b(?:[ÉE]chelons|[ÉE]CHELONS|GRADES|Grades)\b|\bGRADES?\s+ET\s+[ÉE]CHELONS?\b"
    r"|^\s*(?:\d{1,2}|[IVX]+)\s*[.)]\s*|\bEn\s+ce\s+qui\s+concerne\b",
    re.IGNORECASE)
#: Une échelle nommée par son numéro : plusieurs de suite sont les colonnes.
ECHELLE = re.compile(r"[ée]chelles?\s+(?:de\s+r[ée]mun[ée]ration\s+)?(?:C\s*)?\d{1,2}(?:\s*bis)?",
                     re.IGNORECASE)
#: Deux grades côte à côte : « ÉCHELONS <grade> INDICES BRUTS » répété.
COTE_A_COTE = re.compile(r"[ÉE]CHELONS\s+(\S.*?)\s+INDICES\s+BRUTS", re.IGNORECASE)
#: Ce qui dit qu'un texte n'est pas une grille à lire comme telle.
RECLASSEMENT = re.compile(r"reclass|situation\s+(?:actuelle|nouvelle|ancienne)|"
                          r"anciennet[ée]\s+(?:conserv|acquise)", re.IGNORECASE)
CARACTERES = re.compile(r":-{4,}|-{6,}|: \d{3} :")
MAJORES = re.compile(r"indices?\s+(?:nouveaux\s+)?major[ée]s?|\bbruts\s+nouveaux\b|\bINM\b"
                     r"|\bIM\b", re.IGNORECASE)
#: Le début du tableau : la phrase qui l'introduit finit par « suit : ».
DEBUT_TABLEAU = re.compile(r"(?:\bsuit|ci-(?:dessous|apr[èe]s))(?P<quand>[^:.]{0,60}?)\s*:",
                           re.IGNORECASE)
#: Ce que le LEGI colle : « Indices brutsà compter du », « 1987portant ».
COLLES = re.compile(r"(?<=[^\W\d_])(?=[àaÀA]\s+compter\b)|(?<=\d)(?=[^\W\d_]{3,})")
#: Le groupe que la phrase introductive nomme, quand le tableau ne le nomme pas.
GROUPE_INTRODUIT = re.compile(
    r"applicables?\s+(?:à\s+la\s+|à\s+l'|aux?\s+|à\s+)(?P<groupe>.{3,160}?)"
    r"(?:\s+(?:institu|mentionn|régi|prévu|créé|défini|fix)\w*\b|\s*,|\s+est\s+fix"
    r"|\s+sont\s+fix|\s+de\s+la\s+fonction\s+publique|\s+des\s+établissements|$)",
    re.IGNORECASE)


@dataclass
class Cellule:
    groupe: str          # le libellé du groupe, tel que le tableau l'écrit
    date: str            # la date de la colonne, AAAA-MM-JJ ; vide : celle de la version
    echelon: str         # "1", "2"…, "special", "exceptionnel", "stagiaire", "1-provisoire"…
    rang: int | None
    indice: int | None
    hors_echelle: str    # « A », « B bis »… quand l'échelon est hors échelle
    #: vide : lue ; « deduite » : la case vide d'une ligne courte placée par
    #: l'ordre des indices ; « presumee » : placée à droite, rien ne tranchant.
    lecture: str = ""


@dataclass
class Tableau:
    cellules: list[Cellule] = field(default_factory=list)
    groupes: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    alertes: list[str] = field(default_factory=list)
    refus: str = ""


@dataclass
class _Jeton:
    genre: str
    texte: str
    valeur: object = None


@dataclass
class _Ligne:
    echelon: str
    rang: int | None
    cases: list[tuple[int | None, str]]   # (indice, hors-échelle) ; (None, "") : vide


@dataclass
class _Segment:
    groupe: str
    lignes: list[_Ligne] = field(default_factory=list)


@dataclass
class _Bloc:
    dates: list[str]
    colonnes: list[str] | None            # les échelles en colonnes, s'il y en a
    segments: list[_Segment] = field(default_factory=list)


def _sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texte) if not unicodedata.combining(c))


def cle_groupe(libelle: str) -> str:
    """La clé d'un groupe : sans accents ni casse, « de rémunération » et
    l'espace entre la lettre d'une échelle et son numéro ôtés."""
    texte = _sans_accents(libelle).lower()
    texte = re.sub(r"\bde\s+remuneration\b", " ", texte)
    texte = re.sub(r"\b([a-z])\s+(\d)", r"\1\2", texte)
    texte = re.sub(r"[^a-z0-9]+", "-", texte).strip("-")
    # Un mot ou deux répétés par erreur : « du corps du corps ».
    return re.sub(r"(?<![a-z0-9])((?:[a-z0-9]+-){1,2}?[a-z0-9]+)-\1(?![a-z0-9])", r"\1", texte)


def _date(trouve: re.Match) -> str:
    jour = trouve.group("jour")
    jour = 1 if re.match(r"1\s*er|premier", jour, re.I) else int(jour)
    mois = MOIS[_sans_accents(trouve.group("mois")).lower()]
    return date(int(trouve.group("an")), mois, jour).isoformat()


def _jetons(texte: str) -> list[_Jeton]:
    jetons = []
    for trouve in JETONS.finditer(texte):
        genre = next(nom for nom in GENRES if trouve.group(nom) is not None)
        brut = trouve.group(0)
        if genre == "date":
            try:
                jetons.append(_Jeton("date", brut, _date(trouve)))
            except ValueError:
                jetons.append(_Jeton("mot", brut))
        elif genre == "echelon":
            rang = trouve.group("rang") or trouve.group("rang2") or trouve.group("rang3")
            if rang:
                provisoire = trouve.group("provisoire") or trouve.group("provisoire2")
                nom = f"{int(rang)}-provisoire" if provisoire else str(int(rang))
                jetons.append(_Jeton("echelon", brut, (nom, None if provisoire else int(rang))))
            else:
                special = (trouve.group("special") or trouve.group("special2")
                           or trouve.group("stage"))
                jetons.append(_Jeton("echelon", brut, (_sans_accents(special.lower()), None)))
        elif genre == "he":
            lettre = (trouve.group("lettre") or trouve.group("lettre2")).upper()
            bis = " bis" if (trouve.group("bis") or trouve.group("bis2")) else ""
            jetons.append(_Jeton("he", brut, lettre + bis))
        elif genre == "valeur":
            valeur = int(re.sub(r"[.\s]", "", trouve.group("valeur")))
            jetons.append(_Jeton("valeur", brut, valeur) if 100 <= valeur <= INDICE_MAXIMAL
                          else _Jeton("mot", brut))
        elif genre == "nombre":
            jetons.append(_Jeton("nombre", brut, int(brut)))
        else:
            jetons.append(_Jeton("mot" if genre == "jusque" else genre, brut))
    return jetons


CASES = ("valeur", "vide", "he")


def _debut_de_ligne(jetons: list[_Jeton], i: int) -> bool:
    """Un échelon, ou un rang nu, suivi d'au moins une case."""
    if jetons[i].genre not in ("echelon", "nombre"):
        return False
    j = i + 1
    while j < len(jetons) and jetons[j].genre == "renvoi":
        j += 1
    return j < len(jetons) and jetons[j].genre in CASES


class _Refus(Exception):
    """Un tableau que l'analyseur s'abstient de lire."""


#: Ce qu'un libellé peut porter de chiffres sans qu'une valeur s'y soit perdue :
#: le numéro d'un texte, une date, un seuil de population écrit par milliers.
CHIFFRES_NEUTRES = re.compile(
    r"n°\s*\d{2,4}-\d{1,5}|\b\d{1,2}(?:er|re)?\s+(?:janvier|f[ée]vrier|mars|avril|mai|juin"
    r"|juillet|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre)\s+\d{4}\b"
    r"|\b\d{1,3}(?:\s?\.\d{3})+\b|\b\d{1,3}(?:\s000)+\b", re.IGNORECASE)


def _hors_des_lignes(libelle: str) -> bool:
    """Un nombre d'indice dans un libellé : une valeur tombée hors de sa ligne,
    signe d'une mise en page que l'analyseur ne lit pas."""
    return bool(re.search(r"(?<!\d)\d{3,4}(?!\d)", CHIFFRES_NEUTRES.sub(" ", libelle)))


def _nettoyer(mots: list[str]) -> str:
    texte = ENTETE_GENERIQUE.sub(" ", " ".join(mots))
    return re.sub(r"\s+", " ", texte).strip(" :;,.-–")


def _intro(phrase: str) -> str:
    trouve = GROUPE_INTRODUIT.search(phrase)
    return trouve.group("groupe").strip(" ,") if trouve else ""


def _blocs(jetons: list[_Jeton], groupe_courant: str) -> list[_Bloc]:
    """Premier passage : les en-têtes (mots et dates) et les lignes, en blocs.
    Un bloc s'ouvre sur des dates ou des échelles en colonnes ; un groupe
    nommé entre deux lignes ouvre un segment du bloc."""
    blocs: list[_Bloc] = []
    mots: list[str] = []
    dates: list[str] = []
    paralleles: list[_Segment] = []      # des grades côte à côte, s'il y en a
    i = 0
    while i < len(jetons):
        if not _debut_de_ligne(jetons, i):
            if jetons[i].genre == "date":
                dates.append(jetons[i].valeur)
            elif jetons[i].genre not in ("renvoi", "duree"):
                mots.append(jetons[i].texte)
            i += 1
            continue
        if mots or dates or not blocs:
            cote_a_cote = COTE_A_COTE.findall(" ".join(mots))
            libelle = _nettoyer(mots)
            if _hors_des_lignes(libelle):
                raise _Refus(f"valeurs hors des lignes, dans « {libelle[:80]} »")
            echelles = ECHELLE.findall(libelle)
            colonnes = None
            if len(cote_a_cote) >= 2:
                corps = _nettoyer(COTE_A_COTE.split(" ".join(mots), 1)[:1])
                noms = [_nettoyer([n]) for n in cote_a_cote]
                noms = [f"{corps} – {n}" if corps else n for n in noms]
            elif len(echelles) >= 2 and not ECHELLE.sub("", libelle).strip(" ,;:"):
                colonnes = [e.strip() for e in echelles]
            elif libelle:
                groupe_courant = libelle
            if dates or colonnes is not None or not blocs or cote_a_cote:
                blocs.append(_Bloc(dates=dates, colonnes=colonnes))
            if len(cote_a_cote) >= 2:
                paralleles = [_Segment(n) for n in noms]
                blocs[-1].segments.extend(paralleles)
                groupe_courant = noms[-1]
            else:
                paralleles = []
                blocs[-1].segments.append(_Segment(groupe_courant))
            mots, dates = [], []
        jeton = jetons[i]
        nom, rang = jeton.valeur if jeton.genre == "echelon" else (str(jeton.valeur), jeton.valeur)
        ligne = _Ligne(nom, rang, [])
        i += 1
        while i < len(jetons) and jetons[i].genre in CASES + ("renvoi", "duree"):
            if jetons[i].genre == "valeur":
                ligne.cases.append((jetons[i].valeur, ""))
            elif jetons[i].genre == "he":
                ligne.cases.append((None, jetons[i].valeur))
            elif jetons[i].genre == "vide":
                ligne.cases.append((None, ""))
            i += 1
        if paralleles:
            # Côte à côte, une ligne du texte porte le même échelon de chaque
            # grade, de gauche à droite : il va au premier qui ne l'a pas.
            cible = next((s for s in paralleles
                          if all(l.echelon != ligne.echelon for l in s.lignes)), paralleles[-1])
            cible.lignes.append(ligne)
        else:
            blocs[-1].segments[-1].lignes.append(ligne)
    return blocs


def _colonnes(bloc: _Bloc) -> tuple[list[tuple[str, str | None]], str]:
    """Les colonnes d'un bloc : leur date et, s'il y a lieu, leur échelle ; ou
    le motif du refus."""
    if bloc.colonnes is not None:
        if len(bloc.dates) > 1:
            return [], "échelles en colonnes sous plusieurs dates, non lu"
        return [(bloc.dates[0] if bloc.dates else "", e) for e in bloc.colonnes], ""
    comptes = collections.Counter(len(l.cases) for s in bloc.segments for l in s.lignes)
    plus_frequent = comptes.most_common()[0][1]
    largeur = max(n for n, c in comptes.items() if c == plus_frequent)
    if largeur == len(bloc.dates):
        return [(d, None) for d in bloc.dates], ""
    if largeur == len(bloc.dates) + 1 and (bloc.dates or largeur == 1):
        return [("", None)] + [(d, None) for d in bloc.dates], ""
    return [], f"{largeur} valeurs par ligne pour {len(bloc.dates)} dates : colonnes non lues"


BORNES = re.compile(r"\b\d{3}\s*-\s*\d{3,4}\b")
VIDE = (None, "")


def _hauteur_case(case: tuple[int | None, str]) -> float | None:
    indice, lettre = case
    if indice is not None:
        return indice
    if lettre:
        lettre, _, bis = lettre.partition(" ")
        return ORDRE_HORS_ECHELLE[lettre] + (5 if bis else 0)
    return None


def _aligner(ligne: _Ligne, voisine: _Ligne | None, largeur: int
             ) -> tuple[list[tuple[int | None, str]], str]:
    """Les cases d'une première ligne trop courte : à droite (l'échelon créé à
    une date plus tardive) ou à gauche (l'échelon supprimé), selon que l'ordre
    des indices, comparé à la ligne voisine, n'admet que l'une ; à droite,
    présumée, s'il admet les deux ; aucune s'il n'en admet pas."""
    manque = [VIDE] * (largeur - len(ligne.cases))
    droite, gauche = manque + ligne.cases, ligne.cases + manque
    if voisine is None or len(voisine.cases) != largeur:
        return droite, "presumee"
    plus_haute = (ligne.rang is None or voisine.rang is None
                  or ligne.rang > voisine.rang)

    def ordonnee(cases):
        for case, autre in zip(cases, voisine.cases):
            h, k = _hauteur_case(case), _hauteur_case(autre)
            if h is not None and k is not None and (h < k if plus_haute else h > k):
                return False
        return True

    a_droite, a_gauche = ordonnee(droite), ordonnee(gauche)
    if a_droite and a_gauche:
        return droite, "presumee"
    if a_droite:
        return droite, "deduite"
    if a_gauche:
        return gauche, "deduite"
    return [], ""


def lire_tableau(texte: str) -> Tableau:
    """Le tableau d'échelonnement d'un article, relu dans son texte aplati."""
    texte = re.sub(r"(\d\s*(?:er|e|ème))(?=[ée]chelon)", r"\1 ", COLLES.sub(" ", texte))
    if RECLASSEMENT.search(texte):
        return Tableau(refus="tableau de reclassement, pas une grille")
    if CARACTERES.search(texte):
        return Tableau(refus="tableau dessiné en caractères, non lu")
    debut = DEBUT_TABLEAU.search(texte)
    # La date d'effet que la phrase met avant les deux-points ouvre le tableau.
    phrase, corps = ((texte[:debut.start()], f"{debut.group('quand')} {texte[debut.end():]}")
                     if debut else ("", texte))
    if MAJORES.search(corps):
        return Tableau(refus="tableau d'indices majorés, non lu")
    try:
        blocs = _blocs(_jetons(corps), _intro(phrase))
    except _Refus as refus:
        return Tableau(refus=str(refus))
    if not blocs:
        if BORNES.search(corps):
            return Tableau(refus="indices extrêmes des grades, sans leurs échelons")
        return Tableau(refus="aucun échelon")

    tableau = Tableau()
    ordre: list[str] = []
    for bloc in blocs:
        colonnes, refus = _colonnes(bloc)
        if refus:
            return Tableau(refus=refus)
        largeur = len(colonnes)
        ordre += [e for _, e in colonnes if e is not None] or [s.groupe for s in bloc.segments]
        for segment in bloc.segments:
            for k, ligne in enumerate(segment.lignes):
                cases, lecture = ligne.cases, ""
                if len(cases) > largeur or (len(cases) < largeur and k > 0):
                    return Tableau(refus=f"échelon {ligne.echelon} de « {segment.groupe} » : "
                                         f"{len(cases)} valeurs pour {largeur} colonnes")
                if len(cases) < largeur:
                    voisine = segment.lignes[1] if len(segment.lignes) > 1 else None
                    cases, lecture = _aligner(ligne, voisine, largeur)
                    if not cases:
                        return Tableau(refus=f"échelon {ligne.echelon} de « {segment.groupe} » : "
                                             "aucune place de ses valeurs ne garde l'ordre "
                                             "des indices")
                    tableau.alertes.append(
                        f"échelon {ligne.echelon} de « {segment.groupe} » : "
                        f"{len(ligne.cases)} valeur(s) pour {largeur} colonnes, placée(s) "
                        f"{'à droite' if cases[-1] != (None, '') else 'à gauche'} ({lecture})")
                for (date_colonne, echelle), (indice, lettre) in zip(colonnes, cases):
                    if indice is None and not lettre:
                        continue
                    groupe = echelle if echelle is not None else segment.groupe
                    tableau.cellules.append(Cellule(groupe, date_colonne, ligne.echelon,
                                                    ligne.rang, indice, lettre, lecture))
        for date_colonne, _ in colonnes:
            if date_colonne not in tableau.dates:
                tableau.dates.append(date_colonne)

    if not tableau.cellules:
        return Tableau(refus="aucune valeur")
    refus = _controler(tableau.cellules)
    if refus:
        return Tableau(refus=refus)
    _ranger(tableau.cellules)
    remplis = {c.groupe for c in tableau.cellules}
    tableau.groupes = [g for g in dict.fromkeys(ordre) if g in remplis]
    return tableau


ORDRE_HORS_ECHELLE = {lettre: 2000 + 10 * n for n, lettre in enumerate("ABCDEFG")}


def _ranger(cellules: list[Cellule]) -> None:
    """Le rang des échelons que le tableau ne numérote pas : l'échelon spécial
    ou exceptionnel, écrit au-dessus du plus haut échelon de son grade, prend
    le rang suivant ; le stagiaire et l'élève, le rang zéro ; un échelon
    provisoire, son numéro."""
    plus_haut: dict[tuple[str, str], int] = collections.Counter()
    for c in cellules:
        if c.rang is not None:
            plus_haut[(c.groupe, c.date)] = max(plus_haut[(c.groupe, c.date)], c.rang)
    for c in cellules:
        if c.rang is not None:
            continue
        if c.echelon.endswith("-provisoire"):
            c.rang = int(c.echelon.split("-")[0])
        elif c.echelon in ("stagiaire", "eleve"):
            c.rang = 0
        else:
            c.rang = plus_haut[(c.groupe, c.date)] + 1


def _hauteur(cellule: Cellule) -> float:
    if cellule.indice is not None:
        return cellule.indice
    lettre, _, bis = cellule.hors_echelle.partition(" ")
    return ORDRE_HORS_ECHELLE[lettre] + (5 if bis else 0)


def _controler(cellules: list[Cellule]) -> str:
    """Un échelon une fois par groupe et par colonne ; un indice qui ne baisse
    pas quand l'échelon monte."""
    par_colonne: dict[tuple[str, str], list[Cellule]] = collections.defaultdict(list)
    for cellule in cellules:
        par_colonne[(cellule.groupe, cellule.date)].append(cellule)
    for (groupe, _), liste in par_colonne.items():
        vus = collections.Counter(c.echelon for c in liste)
        doubles = [e for e, n in vus.items() if n > 1]
        if doubles:
            return f"échelon {doubles[0]} en double dans « {groupe} »"
        rangees = sorted((c for c in liste if c.rang is not None), key=lambda c: c.rang)
        for bas, haut in zip(rangees, rangees[1:]):
            if _hauteur(haut) < _hauteur(bas):
                return (f"« {groupe} » : l'indice baisse quand l'échelon monte "
                        f"({bas.echelon} : {bas.indice or bas.hors_echelle}, "
                        f"{haut.echelon} : {haut.indice or haut.hors_echelle})")
    return ""


# ---------------------------------------------------------------------------
# Les versions d'un texte, composées en périodes
# ---------------------------------------------------------------------------

@dataclass
class Version:
    article: str
    debut: str           # LEGI : début de vigueur
    fin: str             # LEGI : fin de vigueur, exclue ; 2999-01-01 : en vigueur
    tableau: Tableau
    numero: str = ""     # le numéro de l'article dans son texte


@dataclass
class Periode:
    groupe: str          # la clé du groupe (``cle_groupe``)
    libelle: str
    echelon: str
    rang: int | None
    debut: str           # inclus
    fin: str             # inclus ; vide : en vigueur
    indice: int | None
    hors_echelle: str
    article: str
    lecture: str = ""


def _veille(jour: str) -> str:
    if jour >= EN_VIGUEUR:
        return ""
    return (date.fromisoformat(jour) - timedelta(days=1)).isoformat()


def _bornes(version: Version) -> dict[str, tuple[str, str]]:
    """De quand à quand chaque colonne d'une version vaut : de sa date, ou du
    début de la version s'il est plus tardif, à la colonne suivante ou à la
    fin de la version. Une colonne qu'une plus tardive recouvre ne vaut pas."""
    debuts = [max(d or version.debut, version.debut) for d in version.tableau.dates]
    bornes = {}
    for k, (colonne, debut) in enumerate(zip(version.tableau.dates, debuts)):
        if any(d == debut for d in debuts[k + 1:]):
            continue
        fin = min([version.fin] + [d for d in debuts[k + 1:] if d > debut])
        if debut < fin:
            bornes[colonne] = (debut, fin)
    return bornes


def composer(versions: list[Version]) -> list[Periode]:
    """Les périodes de chaque échelon d'un texte : chaque cellule vaut le temps
    de sa colonne ; une version plus tardive l'emporte sur celle qu'elle
    chevauche ; deux périodes qui se suivent au même indice n'en font qu'une."""
    intervalles: dict[tuple[str, str], list[list]] = collections.defaultdict(list)
    ordre = sorted(versions, key=lambda v: (v.debut, v.fin, v.article))
    for position, version in enumerate(ordre):
        if version.tableau.refus or version.debut >= version.fin:
            continue
        bornes = _bornes(version)
        for cellule in version.tableau.cellules:
            if cellule.date in bornes:
                debut, fin = bornes[cellule.date]
                intervalles[(cle_groupe(cellule.groupe), cellule.echelon)].append(
                    [debut, fin, cellule.indice, cellule.hors_echelle, cellule.lecture,
                     version.article, cellule.groupe, cellule.rang, position])

    periodes = []
    for (groupe, echelon), liste in sorted(intervalles.items()):
        liste.sort(key=lambda x: (x[0], x[8]))
        suite: list[list] = []
        for intervalle in liste:
            while suite and suite[-1][1] > intervalle[0]:
                suite[-1][1] = intervalle[0]
                if suite[-1][1] > suite[-1][0]:
                    break
                suite.pop()
            if suite and suite[-1][1] == intervalle[0] and suite[-1][2:5] == intervalle[2:5]:
                suite[-1][1] = intervalle[1]
            else:
                suite.append(list(intervalle))
        for debut, fin, indice, lettre, lecture, article, libelle, rang, _ in suite:
            periodes.append(Periode(groupe, libelle, echelon, rang, debut, _veille(fin),
                                    indice, lettre, article, lecture))
    return periodes


# ---------------------------------------------------------------------------
# Les textes de l'index, lus versant par versant
# ---------------------------------------------------------------------------

#: Le titre d'un texte de grille.
TITRE_GRILLE = re.compile(r"[ée]chelonnement\s+indiciaire|[ée]chelles?\s+de\s+r[ée]mun[ée]ration"
                          r"|classement\s+(?:et\s+(?:à\s+l')?[ée]chelonnement\s+)?indiciaires?"
                          r"|grilles?\s+indiciaires?", re.IGNORECASE)
TERRITORIALE = re.compile(r"fonction\s+publique\s+territoriale|territoriaux|territoriales\b",
                          re.IGNORECASE)
HOSPITALIERE = re.compile(r"hospitali|86-33|9\s+janvier\s+1986|[ée]tablissements\s+"
                          r"d'hospitalisation", re.IGNORECASE)
NUMERO = re.compile(r"^\s*(?:D[ée]cret|Arr[êe]t[ée]|Loi|Ordonnance)\s+n°\s*(\d{2,4}-\d+)",
                    re.IGNORECASE)
SIGNATURE = re.compile(r"\bdu\s+(1\s*er|\d{1,2})\s+(janvier|f[ée]vrier|mars|avril|mai|juin|"
                       r"juillet|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre)\s+(\d{4})",
                       re.IGNORECASE)
INDICES = re.compile(r"(?<![\w,.-])\d{3,4}(?![\w,-])")


def versant(titre: str) -> str:
    """Le versant d'un texte, lu à son titre : « territoriale », « hospitaliere »,
    ou vide — l'État, que le Noyau RH porte, ou plusieurs versants à la fois,
    ce que fait un décret qui en modifie d'autres."""
    territoriale = re.search(r"fonction\s+publique\s+territoriale", titre, re.I)
    hospitaliere = re.search(r"fonction\s+publique\s+hospitali", titre, re.I)
    if territoriale or hospitaliere:
        return "" if territoriale and hospitaliere else (
            "territoriale" if territoriale else "hospitaliere")
    if re.search(r"universit", titre, re.I):
        return ""                   # les corps hospitalo-universitaires sont de l'État
    if TERRITORIALE.search(titre) and not re.search(r"minist[èe]re", titre, re.I):
        return "territoriale"
    return "hospitaliere" if HOSPITALIERE.search(titre) else ""


def numero(titre: str) -> str:
    """Le numéro d'un décret, lu en tête de son titre ; vide pour un arrêté."""
    trouve = NUMERO.search(titre)
    return trouve.group(1) if trouve else ""


def desambiguer(versions: list[Version]) -> list[Version]:
    """Deux articles d'un texte qui nomment pareil un groupe, au même moment, en
    décrivent deux : le nom de chacun prend son article. Le même groupe passé
    d'un article à l'autre, l'un finissant quand l'autre commence, garde le sien."""
    etendues: dict[str, dict[str, list[tuple[str, str, set[str]]]]] = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for v in versions:
        if not v.tableau.refus:
            for groupe in v.tableau.groupes:
                echelons = {c.echelon for c in v.tableau.cellules if c.groupe == groupe}
                etendues[cle_groupe(groupe)][v.numero].append((v.debut, v.fin, echelons))
    doubles: set[tuple[str, str]] = set()     # (clé, article) en conflit
    for cle, par_article in etendues.items():
        articles = sorted(par_article)
        for a, b in ((a, b) for i, a in enumerate(articles) for b in articles[i + 1:]):
            if any(d1 < f2 and d2 < f1 and e1 & e2
                   for d1, f1, e1 in par_article[a] for d2, f2, e2 in par_article[b]):
                doubles |= {(cle, a), (cle, b)}
    for v in versions:
        if v.tableau.refus or not any((cle_groupe(g), v.numero) in doubles
                                      for g in v.tableau.groupes):
            continue
        nom = {g: (f"{g} (article {v.numero})" if (cle_groupe(g), v.numero) in doubles else g)
               for g in v.tableau.groupes}
        for cellule in v.tableau.cellules:
            cellule.groupe = nom[cellule.groupe]
        v.tableau.groupes = [nom[g] for g in v.tableau.groupes]
    return versions


def _ressemble_a_un_tableau(texte: str) -> bool:
    """Ce qu'un refus doit consigner : un article qui parle d'échelons et porte
    au moins deux nombres d'indice ; non la formule d'exécution, ni l'entrée
    en vigueur."""
    nombres = [int(n) for n in INDICES.findall(texte)]
    return (bool(re.search(r"[ée]chelon|indices?\s+bruts?", texte, re.I))
            and sum(100 <= n <= 1200 for n in nombres) >= 2)


def _signature(titre: str) -> str:
    trouve = SIGNATURE.search(titre)
    if not trouve:
        return ""
    jour = 1 if re.match(r"1\s*er", trouve.group(1)) else int(trouve.group(1))
    try:
        return date(int(trouve.group(3)), MOIS[_sans_accents(trouve.group(2)).lower()],
                    jour).isoformat()
    except ValueError:
        return ""


def _fin(jour: str) -> str:
    return "" if not jour or jour >= EN_VIGUEUR else jour


def extraire(chemin_index: Path | str | None = None) -> dict:
    """Les grilles de la territoriale et de l'hospitalière, lues dans l'index
    LEGI : par versant, les textes, les grilles, les échelons et les refus."""
    import dila_index

    db, source = dila_index.ouvrir_lecture("legi", str(chemin_index) if chemin_index else None)
    textes: dict[str, dict] = {}
    for ident, debut, fin, nature, titre in db.execute(
            "SELECT id, date, fin, nature, titre FROM doc WHERE nature NOT LIKE 'Article%'"):
        if TITRE_GRILLE.search(titre or "") and versant(titre):
            textes.setdefault(titre, {"texte": ident, "debut": debut, "fin": fin,
                                      "nature": nature})
    versions: dict[str, list[Version]] = collections.defaultdict(list)
    non_lus: dict[str, list[dict]] = collections.defaultdict(list)
    for ident, debut, fin, article, titre, contenu in db.execute(
            "SELECT id, date, fin, num, titre, texte FROM doc WHERE nature LIKE 'Article%' "
            "ORDER BY date, id"):
        if titre not in textes or debut >= EN_VIGUEUR or not _ressemble_a_un_tableau(contenu):
            continue
        tableau = lire_tableau(contenu)
        if tableau.refus:
            non_lus[titre].append({"texte": textes[titre]["texte"], "article": ident,
                                   "numero": article, "debut": debut, "fin": _fin(fin),
                                   "motif": tableau.refus})
        else:
            versions[titre].append(Version(ident, debut, fin, tableau, article))
    db.close()

    extrait: dict = {"source": source}
    for nom in VERSANTS:
        extrait[nom] = {"textes": [], "grilles": [], "echelons": [], "non_lus": []}
    for titre, texte in sorted(textes.items(), key=lambda kv: kv[1]["texte"]):
        if titre not in versions and titre not in non_lus:
            continue
        cible = extrait[versant(titre)]
        cible["textes"].append({
            "texte": texte["texte"], "numero": numero(titre),
            "nature": texte["nature"], "signature": _signature(titre),
            "debut": texte["debut"], "fin": _fin(texte["fin"]), "titre": titre,
            "articles_lus": str(len(versions.get(titre, []))),
            "articles_non_lus": str(len(non_lus.get(titre, [])))})
        cible["non_lus"].extend(non_lus.get(titre, []))
        periodes = composer(desambiguer(versions.get(titre, [])))
        par_grille: dict[str, list[Periode]] = collections.defaultdict(list)
        for p in periodes:
            par_grille[p.groupe].append(p)
        for grille, liste in sorted(par_grille.items()):
            derniere = max(liste, key=lambda p: p.debut)
            cible["grilles"].append({
                "texte": texte["texte"], "grille": grille, "libelle": derniere.libelle,
                "debut": min(p.debut for p in liste),
                "fin": "" if any(not p.fin for p in liste) else max(p.fin for p in liste),
                "echelons": str(len({p.echelon for p in liste}))})
            for p in sorted(liste, key=lambda p: (p.echelon, p.debut)):
                cible["echelons"].append({
                    "texte": texte["texte"], "grille": grille, "echelon": p.echelon,
                    "rang": str(p.rang), "debut": p.debut, "fin": p.fin,
                    "indice": "" if p.indice is None else str(p.indice),
                    "hors_echelle": p.hors_echelle, "lecture": p.lecture,
                    "article": p.article})
    for nom in VERSANTS:
        extrait[nom]["textes"].sort(key=lambda t: (t["signature"], t["texte"]))
        extrait[nom]["non_lus"].sort(key=lambda n: (n["texte"], n["numero"], n["debut"]))
    return extrait


# ---------------------------------------------------------------------------
# L'écriture
# ---------------------------------------------------------------------------

COLONNES = {
    "textes": ("texte", "numero", "nature", "signature", "debut", "fin", "titre",
               "articles_lus", "articles_non_lus"),
    "grilles": ("texte", "grille", "libelle", "debut", "fin", "echelons"),
    "echelons": ("texte", "grille", "echelon", "rang", "debut", "fin", "indice",
                 "hors_echelle", "lecture", "article"),
    "non_lus": ("texte", "article", "numero", "debut", "fin", "motif"),
}
CLES_ECHELON = ("texte", "grille", "echelon", "debut")
ENTETES = {
    "textes": "Les textes qui fixent les grilles, au LEGI : numéro, nature, date de "
              "signature, vigueur du texte ; les versions d'articles lues et non lues.",
    "grilles": "Les grilles de chaque texte, une par groupe (grade, échelle, classe) : sa "
               "clé, son dernier libellé, la période qu'elle couvre, ses échelons.",
    "echelons": "L'indice brut de chaque échelon, période par période (fin incluse ; vide : "
                "en vigueur), et l'article du LEGI qui le fixe. hors_echelle : la lettre, à "
                "défaut d'indice. rang : le numéro de l'échelon ; l'échelon spécial prend le "
                "rang qui suit le plus haut, le stagiaire et l'élève le rang zéro. lecture : "
                "vide, lue ; « deduite », la case vide d'une ligne courte placée par l'ordre "
                "des indices ; « presumee », placée à droite, l'échelon créé à la dernière "
                "date, rien ne tranchant (fiabilité estimee).",
    "non_lus": "Les versions d'articles qui portent un tableau que l'analyseur n'a pas lu, "
               "et pourquoi.",
}
SOURCE_ID = ("# source_id: dila_legi_grilles — DILA, base LEGI, par l'index du dépôt "
             "(scripts/fetch/dila_index.py) ; scripts/fetch/dila_legi_grilles.py")


def _cle_echelon(ligne: dict) -> str:
    return "|".join(ligne[c] for c in CLES_ECHELON)


def brut(extrait: dict, source: str) -> dict:
    """Le fichier brut de la certification : par versant, le rang et l'indice de
    chaque période lue, sous la clé « texte|grille|échelon|début » ; à part,
    ceux des périodes dont la colonne est présumée."""
    contenu: dict = {"source": source, "recupere_le": date.today().isoformat()}
    for nom in VERSANTS:
        series = {"rang": {}, "indice": {}, "rang_presume": {}, "indice_presume": {}}
        for ligne in extrait[nom]["echelons"]:
            suffixe = "_presume" if ligne["lecture"] == "presumee" else ""
            series["rang" + suffixe][_cle_echelon(ligne)] = int(ligne["rang"])
            if ligne["indice"]:
                series["indice" + suffixe][_cle_echelon(ligne)] = int(ligne["indice"])
        contenu[nom] = series
    return contenu


def ecrire_reference(extrait: dict, dossier: Path = REFERENCE) -> None:
    """Les quatre fichiers de chaque versant. Les échelons gardent leur colonne
    ``fiabilite`` : vide pour une ligne neuve ou changée, la valeur qu'elle
    avait sinon — seul ``verifier_donnees.py`` la fait ``certifiee`` ou
    ``estimee``. Ils sont triés comme la certification les trie, par leurs clés."""
    for nom in VERSANTS:
        cible = dossier / nom
        cible.mkdir(parents=True, exist_ok=True)
        for fichier, colonnes in COLONNES.items():
            chemin = cible / f"{fichier}.csv"
            lignes = extrait[nom][fichier]
            champs = list(colonnes)
            if fichier == "echelons":
                champs.append("fiabilite")
                anciennes = {}
                if chemin.exists():
                    with chemin.open(encoding="utf-8") as flux:
                        for ligne in csv.DictReader(l for l in flux if not l.startswith("#")):
                            anciennes[_cle_echelon(ligne)] = ligne
                sorties = []
                for ligne in lignes:
                    avant = anciennes.get(_cle_echelon(ligne), {})
                    identique = all(avant.get(c) == ligne[c] for c in colonnes)
                    sorties.append({**ligne, "fiabilite": avant.get("fiabilite", "")
                                    if identique else ""})
                lignes = sorted(sorties, key=lambda l: tuple(l[c] for c in CLES_ECHELON))
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
    BRUT.write_text(json.dumps(brut(extrait, extrait["source"]), ensure_ascii=False, indent=1,
                               sort_keys=True), encoding="utf-8")
    for nom in VERSANTS:
        partie = extrait[nom]
        lus = sum(int(t["articles_lus"]) for t in partie["textes"])
        print(f"{nom} : {len(partie['textes'])} textes, {len(partie['grilles'])} grilles, "
              f"{len(partie['echelons'])} périodes d'échelons ; {lus} versions d'articles "
              f"lues, {len(partie['non_lus'])} non lues", file=sys.stderr)
    print(f"source : {extrait['source']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
