#!/usr/bin/env python3
"""L'AVTS, l'allocation supplémentaire et leur plafond, relus au Journal officiel, décret par décret.

    python scripts/fetch/dila_index.py jorf --recuperer   # les deux index, une fois
    python scripts/fetch/dila_index.py legi --recuperer
    python scripts/fetch/cnav_avts.py                     # le barème de la caisse, d'abord
    python scripts/fetch/jorf_avts.py                     # quelques secondes

À QUOI IL SERT. ``cnav_avts.py`` lit dans les barèmes de la Cnav chaque montant
de l'allocation aux vieux travailleurs salariés (AVTS), de l'allocation
supplémentaire et de son plafond de ressources, daté et rapporté au texte qui
l'a fixé. C'est une transcription de la caisse : niveau ``haute``. Ce script
relit ces montants dans les textes eux-mêmes, par les index JORF et LEGI du
dépôt, et certifie ceux que le texte, ou sa notice, redit à la même date. Il lit
TOUS les textes dont le titre fixe ces montants — « fixant le montant de divers
avantages de vieillesse et d'invalidité », « fixant le montant de l'allocation
supplémentaire du Fonds national de solidarité », « portant revalorisation de
divers avantages de vieillesse » —, non les seuls que la caisse cite : c'est ce
qui montre qu'elle en cite parfois un autre.

CE QUE LES INDEX PORTENT, ÉPOQUE PAR ÉPOQUE.

* **avant 1970**, le titre seul, ou une notice sans montant : « FIXANT LE TAUX
  DE DIVERS AVANTAGES DE VIEILLESSE ET D'INVALIDITE ». Rien ne s'y certifie ; le
  fac-similé du Journal officiel le pourrait (action 138, étape 17) ;
* **de 1970 à 1989, la notice**, en capitales, qui redit souvent le montant de
  l'AVTS et sa date — « (2 250 FRS PAR AN A COMPTER DU 01-07-1973) » —, rarement
  le plafond. Les décrets de l'allocation supplémentaire n'y sont presque pas :
  leur titre ne nomme ni la vieillesse ni la retraite, et le filtre thématique
  de l'index (``THEMATIQUE`` dans ``dila_index.py``) les a laissés au dump. Le
  dump global les porte de 1968 à 1981, et leur titre redit le montant de
  l'allocation, jamais le plafond : aucune ligne ne s'y certifie de plus (lu le
  13 octobre 2026), et le script s'en tient aux index ;
* **de 1981 à 2003, le texte**, article par article, dans LEGI, et dans le JORF
  depuis 1990 : « Sont portés à 13 470 F par an à compter du 1er janvier 1987 et
  à 13 600 F par an à compter du 1er juillet 1987 : - le montant de l'allocation
  aux vieux travailleurs salariés […] » ;
* **de 2004 à 2006**, un arrêté qui ne fixe qu'un coefficient — « est égal à
  1,017 » — : appliquer un coefficient est un calcul, et un calcul ne se
  certifie pas.

CE QUI EST LU, ET COMMENT. Les textes d'outre-mer et les majorations
exceptionnelles, versées une fois aux allocataires, sont écartés. Chaque titre,
notice ou article est coupé en phrases et en propositions, aux points-virgules ;
dans chacune, chaque montant (« 10.100 F », « 1750FRS », « 2 849,84 Euros »)
prend la date d'effet qui le précède si elle ouvre ce qui la suit (« AU
01-01-1987: 18120FRS »), sinon la première qui le suit — « à compter du »,
« au » —, sinon la dernière qui le précède, sinon la seule que porte l'article,
sinon la seule que porte le décret, ce que la sortie dit. Il est rangé dans une
série par ce que la proposition nomme :

* ``plafond_seul`` et ``plafond_couple`` : les « montants limites annuels » ou
  « chiffres limites », par le libellé qui suit le montant — « pour une personne
  seule », « pour deux époux », « par ménage » ;
* ``as_seul``, ``as_couple`` : l'allocation supplémentaire, par le libellé qui
  la suit dans une notice (« 18120FRS POUR UNE PERSONNE SEULE »), qui la précède
  dans un article (« b) Pour les couples mariés, à 34 300 F ») ; ``as_marie``,
  le montant d'un allocataire marié (« lorsque le bénéficiaire est marié, ce
  montant est fixé à 12700 F », décret n° 82-560) ;
* ``avts`` : le montant que l'article porte pour « l'allocation aux vieux
  travailleurs salariés » ; dans une notice ou un titre d'un décret « fixant le
  montant de divers avantages de vieillesse », le seul montant qu'elle donne,
  celui de ces avantages, que l'article 1er de chacun de ces décrets applique
  d'abord à l'AVTS.

Ne sont pas des séries, et ne sont pas lus : le montant que les caisses sont
autorisées à servir « à titre provisionnel » (la somme des deux étages, bornée
au plafond), et le « minimum vieillesse » ou le « minimum global » des notices,
par an ou par jour, avec ce qui les suit — celle du décret n° 81-1166 y écrit le
plafond, 24 900 F, quand les deux étages font 24 000 F.

LE MONTANT DU MÉNAGE. La colonne ``supplementaire_menage`` porte ce que
reçoivent deux allocataires mariés. Le texte le fixe pour le couple depuis 1992
(« b) Pour les couples mariés, à 34 300 F par an ») ; en 1982, il fixe celui de
chaque allocataire marié, 12 700 F, et le ménage en reçoit deux ; de 1983 à
1991, il fixe un seul montant, sans distinguer l'allocataire marié, et chacun
des deux le reçoit. Le script ne double un montant que si l'article ne nomme ni
le mariage, ni le couple, ni les époux, ni le ménage, et le dit
(``derivation``).

LES CONTRÔLES. Chaque montant daté du barème de la caisse est certifié si un
texte redit le même montant, à la même date, dans la même série ; un texte qui
dit autre chose à cette date est un écart, déclaré, et le montant reste au
niveau de la caisse — c'est ainsi que la notice du décret n° 82-1142 (10 300 F)
cède à son article 1er (11 300 F). Une série du dépôt est une ligne par année,
au 31 décembre : une année n'est certifiée que si tous les montants de la ligne
— l'AVTS, l'allocation supplémentaire d'un et de deux allocataires, les deux
plafonds — le sont, puisque le modèle les lit ensemble et que la ligne n'a
qu'un niveau de fiabilité. Le seuil d'un trimestre de 1949 à 1971 est le quart
de l'AVTS au 1er janvier (R. 351-9) : certifié quand cette AVTS l'est ; de 1946
à 1948, 18 F, que le script relit dans les rédactions de R. 351-9 qui le
portent.

CE QUI EST ÉCRIT. ``data/brut/jorf_avts.json`` : les énoncés lus, texte par
texte ; les montants datés certifiés, avec leurs sources ; les écarts, les dates
qui diffèrent, ce que la caisse rapporte à un autre décret que celui qui le dit ;
les années certifiées et, pour elles, chaque série au 31 décembre ; le seuil
d'un trimestre certifié. ``scripts/verifier_donnees.py`` en fait le niveau
``certifiee`` de ``minimum_vieillesse_avant_2007.csv`` et de
``salaire_validant_trimestre_avant_1972.csv``, la Cnav gardant les autres années
au niveau ``haute``.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dila_index import ouvrir_lecture  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
CNAV = RACINE / "data" / "brut" / "cnav_avts.json"
SORTIE = RACINE / "data" / "brut" / "jorf_avts.json"

FRANCS_PAR_EURO = 6.55957
#: Écart toléré entre deux montants en euros : le centime, arrondi.
TOLERANCE = 0.005
#: Le minimum vieillesse à deux étages s'arrête avec l'ASPA, le 13 janvier 2007.
DERNIERE_ANNEE = 2006
#: Les colonnes de ``minimum_vieillesse_avant_2007.csv`` et la série de chacune.
COLONNES = {"avts": "avts", "supplementaire": "as_seul",
            "supplementaire_menage": "as_couple", "plafond": "plafond_seul",
            "plafond_couple": "plafond_couple"}
#: R. 351-9 rapporte le seuil d'un trimestre à l'AVTS du 1er janvier de 1949 à
#: 1971 ; de 1946 à 1948, il écrit 18 F.
PREMIERE_ANNEE_AVTS, DERNIERE_ANNEE_AVTS = 1949, 1971
ANNEES_DIX_HUIT_FRANCS = (1946, 1947, 1948)

MOIS = {"JANVIER": 1, "FEVRIER": 2, "MARS": 3, "AVRIL": 4, "MAI": 5, "JUIN": 6,
        "JUILLET": 7, "AOUT": 8, "SEPTEMBRE": 9, "OCTOBRE": 10, "NOVEMBRE": 11,
        "DECEMBRE": 12}

#: Les titres des textes qui fixent ces montants. L'outre-mer a ses textes et
#: ses montants, que le dépôt ne porte pas ; une majoration exceptionnelle (100 F
#: en 1974, 150 F en 1980) est versée une fois aux allocataires, sans changer le
#: montant de l'allocation : les uns et les autres sont écartés.
TITRE_PERTINENT = re.compile(
    r"(?:FIXANT|FIXATION|REVALORIS|MAJOR|AUGMENT|RELEVANT)\w*\b.*"
    r"(?:DIVERS AVANTAGES|ALLOCATION SUPPLEMENTAIRE|VIEUX TRAVAILLEURS SALARIES)")
TITRE_ECARTE = re.compile(r"SAINT-PIERRE|MAYOTTE|OUTRE-MER|GUADELOUPE|MARTINIQUE|"
                          r"GUYANE|REUNION|SAHARA|OASIS|ALGERIE|MAJORATION EXCEPTIONNELLE")

MONTANT = re.compile(
    r"(?<![\d.,])(\d{1,3}(?:[ .]\d{3})+|\d+)(?:,(\d{1,2}))?\s?"
    r"(FRANCS|FRS|F|EUROS?|EUR|€)(?![A-Z])")
DATE_MOT = re.compile(
    r"(?:(?:A COMPTER|A DATER|A PARTIR) DU|\bAU) (1ER|\d{1,2}) (" + "|".join(MOIS)
    + r") (\d{4})")
DATE_CHIFFRE = re.compile(r"(?:(?:A COMPTER|A DATER|A PARTIR) DU|\bAU) (\d{2})-(\d{2})-(\d{4})")
#: Une date suivie d'un deux-points ou d'une virgule ouvre ce qui la suit :
#: « AU 01-01-1987: 18120FRS », « A COMPTER DU 01-10-1970,LES TAUX SONT PORTES ».
EN_TETE = re.compile(r"\s*[:,](?!\s*ET\b)")
#: Ce qui n'est pas une série : la somme servie à titre provisionnel ; le
#: « minimum vieillesse » ou le « minimum global » des notices, par an ou par
#: jour, souvent suivi du taux de revalorisation. La lecture d'un article
#: s'arrête là jusqu'à la fin de la phrase, celle d'une notice jusqu'à sa fin :
#: ses phrases suivantes détaillent ce minimum (« LES COUPLES MARIES:
#: 33690FRS. »), ou mêlent les deux étages et les plafonds sans les séparer.
PROPOSITION_ECARTEE = re.compile(r"PROVISIONNEL|PREVISIONNEL|MINIMUM VIEILLESSE|"
                                 r"MINIMUM GLOBAL|MONTANT GLOBAL|PAR JOUR|%")
PLAFOND = re.compile(r"LIMITES? (?:ANNUEL|DE RESSOURCES)|CHIFFRES? LIMITES?|"
                     r"MONTANTS? LIMITES?|PLAFOND")
LIBELLE_PLAFOND = re.compile(r"PERSONNE SEULE|DEUX EPOUX|MENAGE|COUPLE")
LIBELLE_AS = re.compile(r"PERSONNES? SEULES?|PERSONNES? MARIEES?|COUPLES? MARIES?|"
                        r"\b(?:UN|LE|DEUX) MENAGES?|EST MARIE\b")
MENAGE_NOMME = re.compile(r"MARIE|COUPLE|EPOUX|MENAGE")
#: La note que LEGI a collée en tête des articles après la loi n° 93-936 : elle
#: nomme l'allocation supplémentaire dans des articles qui n'en parlent pas.
NOTE_93_936 = re.compile(
    r"\[?\s*Loi 93-936 du 22 juillet 1993 art\. 12 .*?allocation sp[ée]ciale "
    r"vieillesse\s*\"\s*\.\s*\]?", re.S)
#: Les abréviations dont le point n'achève pas une phrase.
ABREVIATION = re.compile(r"\b(ART|ARTS|AL|PARAG|N|NO|L|R|D|P|RECT)\.\s*")
NUMERO_DECRET = re.compile(r"\bN(?:°|O)\s*(\d{2,4})-(\d+)\b")


@dataclass(frozen=True)
class Enonce:
    """Un montant qu'un texte écrit, rangé dans sa série et daté."""

    serie: str
    date: str | None
    euros: float
    ecrit: str           # le montant tel que le texte l'écrit
    source: str          # l'identifiant JORF ou LEGI
    decret: str          # « 82-560 », ou le titre quand le texte n'a pas de numéro
    forme: str           # « article », « notice » ou « titre »
    date_de: str = ""    # d'où vient la date quand la proposition ne la porte pas
    derivation: str = ""


@dataclass(frozen=True)
class DateEffet:
    debut: int
    fin: int
    jour: str
    en_tete: bool


def majuscules(texte: str) -> str:
    """Le texte en capitales, sans accents ni espaces insécables : les notices
    d'avant 1990 sont écrites ainsi, et les articles s'y ramènent."""
    texte = NOTE_93_936.sub(" ", texte)
    # « 17.48O F », « articles 1O et 16 » : LEGI a pris un O pour un zéro.
    texte = re.sub(r"(?<=\d)O(?=\d|\b)", "0", texte)
    texte = "".join(c for c in unicodedata.normalize("NFD", texte)
                    if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texte).upper()


def phrases(texte: str) -> list[list[str]]:
    """Le texte en phrases, et chaque phrase en propositions, coupées aux
    points-virgules."""
    texte = ABREVIATION.sub(lambda m: m.group(1) + " ", texte)
    return [[p.strip() for p in phrase.split(";") if p.strip()]
            for phrase in re.split(r"\.\s+", texte) if phrase.strip()]


def _euros(entier: str, decimales: str | None, unite: str) -> float:
    nombre = float(re.sub(r"[ .]", "", entier) + "." + (decimales or "0"))
    return nombre if unite.startswith("EUR") or unite == "€" else nombre / FRANCS_PAR_EURO


def dates_d_effet(texte: str) -> list[DateEffet]:
    """Les dates d'effet d'un texte en capitales, dans l'ordre."""
    trouvees = []
    for m in DATE_MOT.finditer(texte):
        jour = 1 if m.group(1) == "1ER" else int(m.group(1))
        trouvees.append((m, f"{m.group(3)}-{MOIS[m.group(2)]:02d}-{jour:02d}"))
    for m in DATE_CHIFFRE.finditer(texte):
        trouvees.append((m, f"{m.group(3)}-{m.group(2)}-{m.group(1)}"))
    return sorted((DateEffet(m.start(), m.end(), jour, bool(EN_TETE.match(texte, m.end())))
                   for m, jour in trouvees), key=lambda d: d.debut)


def date_du_montant(dates: list[DateEffet], debut: int, fin: int) -> str | None:
    """La date d'un montant : celle qui le précède si elle ouvre ce qui la suit
    (« au 01-01-1987: 18120FRS »), sinon la première qui le suit (« à 13 470 F
    par an à compter du 1er janvier 1987 et à 13 600 F par an à compter du
    1er juillet 1987 »), sinon la dernière qui le précède (« à compter du
    1er janvier 1984 à 28.950 F »)."""
    avant = [d for d in dates if d.fin <= debut]
    if avant and avant[-1].en_tete:
        return avant[-1].jour
    apres = [d for d in dates if d.debut >= fin]
    if apres:
        return apres[0].jour
    return avant[-1].jour if avant else None


def famille(titre: str) -> str | None:
    """Ce qu'un titre fixe, pour ranger le montant qu'une notice donne sans le
    nommer : l'AVTS dans un décret « de divers avantages de vieillesse »,
    l'allocation supplémentaire dans le sien ; rien si le titre porte les deux."""
    avantages = "DIVERS AVANTAGES" in titre
    supplementaire = "ALLOCATION SUPPLEMENTAIRE" in titre
    if avantages and not supplementaire:
        return "avts"
    if supplementaire and not avantages:
        return "as_seul"
    return None


def _serie_as(libelle: str | None) -> str:
    if libelle is None or "SEULE" in libelle:
        return "as_seul"
    if libelle.startswith("COUPLE") or "MENAGE" in libelle:
        return "as_couple"
    return "as_marie"


def _serie(proposition: str, tete: str, debut: int, fin: int, suivant: int,
           forme: str, defaut: str | None) -> str | None:
    """La série du montant lu de ``debut`` à ``fin`` dans la proposition, le
    montant suivant commençant à ``suivant``. Le libellé d'un plafond suit le
    montant (« à 24.900 F pour une personne seule ») ; celui de l'allocation
    supplémentaire le suit dans une notice (« 18120FRS POUR UNE PERSONNE
    SEULE »), le précède dans un article (« a) Pour les personnes seules, à
    20 900 F »)."""
    contexte = tete + " " + proposition
    if PLAFOND.search(contexte):
        libelle = LIBELLE_PLAFOND.search(proposition, fin, suivant)
        if libelle is None:
            return None
        return "plafond_seul" if libelle.group() == "PERSONNE SEULE" else "plafond_couple"
    if "ALLOCATION SUPPLEMENTAIRE" in contexte or (
            defaut == "as_seul" and "VIEUX TRAVAILLEURS SALARIES" not in contexte):
        libelle = LIBELLE_AS.search(proposition, fin, suivant)
        if libelle is None:
            precedents = list(LIBELLE_AS.finditer(proposition, 0, debut))
            libelle = precedents[-1] if precedents else None
        return _serie_as(None if libelle is None else libelle.group())
    if "VIEUX TRAVAILLEURS SALARIES" in contexte:
        return "avts"
    if forme in ("notice", "titre") and defaut == "avts":
        return "avts"
    return None


def lire_enonces(texte: str, *, source: str, decret: str, forme: str,
                 titre: str) -> tuple[list[Enonce], list[tuple[str, float, str]]]:
    """Les montants d'un titre, d'une notice ou d'un article, et ceux qui n'ont
    pas de date à eux (série, euros, écrit), que l'appelant date par l'article
    ou le décret."""
    capitales = majuscules(texte)
    defaut = famille(majuscules(titre))
    tete = capitales.split(":", 1)[0] if ":" in capitales[:400] else ""
    enonces, sans_date = [], []
    ecartee = False
    for phrase in phrases(capitales):
        if ecartee and forme != "article":
            break
        for proposition in phrase:
            if PROPOSITION_ECARTEE.search(proposition):
                ecartee = True
                break
            dates = dates_d_effet(proposition)
            montants = list(MONTANT.finditer(proposition))
            for rang, m in enumerate(montants):
                suivant = montants[rang + 1].start() if rang + 1 < len(montants) else len(proposition)
                serie = _serie(proposition, tete, m.start(), m.end(), suivant, forme, defaut)
                if serie is None:
                    continue
                euros = _euros(m.group(1), m.group(2), m.group(3))
                effet = date_du_montant(dates, m.start(), m.end())
                if effet is None:
                    sans_date.append((serie, euros, m.group()))
                    continue
                enonces.append(Enonce(serie, effet, round(euros, 6), m.group(), source,
                                      decret, forme))
    return enonces, sans_date


def _menage(enonces: list[Enonce], texte: str) -> list[Enonce]:
    """Le montant de deux allocataires mariés, quand l'article ne fixe que celui
    de chacun. Seul un article le permet : une notice qui tait le ménage ne dit
    pas que le texte le taise."""
    derives = []
    nomme = bool(MENAGE_NOMME.search(majuscules(texte)))
    for e in enonces:
        if e.forme != "article":
            continue
        if e.serie == "as_marie":
            derives.append(Enonce("as_couple", e.date, round(2 * e.euros, 6), e.ecrit,
                                  e.source, e.decret, e.forme, e.date_de,
                                  "deux fois le montant de l'allocataire marié"))
        elif e.serie == "as_seul" and not nomme:
            derives.append(Enonce("as_couple", e.date, round(2 * e.euros, 6), e.ecrit,
                                  e.source, e.decret, e.forme, e.date_de,
                                  "deux fois le montant que l'article fixe pour tout "
                                  "allocataire, sans nommer ni le mariage ni le couple"))
    return derives


def decret_de(titre: str) -> str:
    numero = NUMERO_DECRET.search(majuscules(titre))
    return f"{numero.group(1)}-{numero.group(2)}" if numero else titre[:80]


def textes_pertinents(db: sqlite3.Connection) -> list[tuple[str, str, str, str, str]]:
    """Les titres, notices et articles des textes qui fixent ces montants, de
    1941 à 2006 : (identifiant, date, nature, titre, texte)."""
    lignes = db.execute(
        "SELECT id, date, nature, titre, texte FROM doc WHERE date >= '1941' "
        "AND date < '2008' AND (titre LIKE '%avantages%vieillesse%' OR titre LIKE "
        "'%allocation suppl%' OR titre LIKE '%vieux travailleurs%') ORDER BY date, id"
    ).fetchall()
    retenus = []
    for ident, jour, nature, titre, texte in lignes:
        capitales = majuscules(titre or "")
        if TITRE_PERTINENT.search(capitales) and not TITRE_ECARTE.search(capitales):
            retenus.append((ident, jour, nature or "", titre or "", texte or ""))
    return retenus


def enonces_des_textes(textes: list[tuple[str, str, str, str, str]]) -> list[Enonce]:
    """Tous les énoncés, datés : ceux d'une proposition sans date prennent la
    seule date de leur article, sinon la seule de leur décret."""
    enonces: list[Enonce] = []
    en_attente: list[tuple[str, str, str, str, list]] = []   # source, décret, forme, texte, sans date
    dates_par_source: dict[str, set[str]] = {}
    dates_par_decret: dict[str, set[str]] = {}
    for ident, _, nature, titre, texte in textes:
        decret = decret_de(titre)
        morceaux = []
        if ident[4:8] == "TEXT":
            morceaux.append(("titre", titre))
            # Le corps d'un texte du JORF d'avant 1990 est sa notice ; depuis,
            # c'est le visa et les signatures, que les articles suivent.
            morceaux.append(("notice", texte))
        else:
            morceaux.append(("article", texte))
        for forme, morceau in morceaux:
            if not morceau:
                continue
            lus, sans_date = lire_enonces(morceau, source=ident, decret=decret,
                                          forme=forme, titre=titre)
            lus += _menage(lus, morceau) if forme == "article" else []
            enonces += lus
            dates = {d.jour for d in dates_d_effet(majuscules(morceau))}
            dates_par_source.setdefault(ident, set()).update(dates)
            dates_par_decret.setdefault(decret, set()).update(dates)
            if sans_date:
                en_attente.append((ident, decret, forme, morceau, sans_date))
    for ident, decret, forme, morceau, sans_date in en_attente:
        propres, du_decret = dates_par_source.get(ident, set()), dates_par_decret.get(decret, set())
        if len(propres) == 1:
            effet, origine = next(iter(propres)), "la seule date de l'article"
        elif not propres and len(du_decret) == 1:
            effet, origine = next(iter(du_decret)), "la seule date du décret"
        else:
            continue
        lus = [Enonce(serie, effet, round(euros, 6), ecrit, ident, decret, forme, origine)
               for serie, euros, ecrit in sans_date]
        enonces += lus + (_menage(lus, morceau) if forme == "article" else [])
    return enonces


def seuil_de_r351_9(db: sqlite3.Connection) -> tuple[float | None, list[str]]:
    """Les 18 F de 1946 à 1948, lus dans les rédactions de R. 351-9 qui les
    portent : le montant, et les rédactions lues. ``None`` si elles se
    contredisent ou si aucune ne le porte."""
    motif = re.compile(r"1ER JANVIER 1946 ET LE 31 DECEMBRE 1948.{0,200}?DE FOIS "
                       r"(\d+(?:,\d+)?) F\b")
    montants, lues = set(), []
    for ident, texte in db.execute(
            "SELECT id, texte FROM doc WHERE replace(num, ' ', '') = 'R351-9' "
            "AND titre LIKE 'Code de la s%curit% sociale%' ORDER BY date"):
        trouve = motif.search(majuscules(texte or ""))
        if trouve:
            montants.add(float(trouve.group(1).replace(",", ".")))
            lues.append(ident)
    if len(montants) != 1:
        return None, lues
    return montants.pop() / FRANCS_PAR_EURO, lues


def _en_vigueur(datees: dict[str, float], serie: str, jour: str) -> str | None:
    """La date du montant de la caisse en vigueur ce jour-là, pour une série."""
    dates = sorted(cle.split("|")[1] for cle in datees if cle.split("|")[0] == serie)
    valables = [d for d in dates if d <= jour]
    return valables[-1] if valables else None


def confronter(cnav: dict, enonces: list[Enonce]) -> dict:
    """Les montants datés de la caisse que les textes redisent, et le reste."""
    datees, references = cnav["datee"], cnav["references"]
    par_cle: dict[tuple[str, str], list[Enonce]] = {}
    for e in enonces:
        par_cle.setdefault((e.serie, e.date), []).append(e)
    certifiees, ecarts, citations = {}, [], []
    for cle, euros in sorted(datees.items()):
        serie, jour = cle.split("|")
        if jour > f"{DERNIERE_ANNEE}-12-31":
            continue
        lus = par_cle.get((serie, jour), [])
        accord = [e for e in lus if abs(e.euros - euros) <= TOLERANCE]
        desaccord = [e for e in lus if abs(e.euros - euros) > TOLERANCE]
        for e in desaccord:
            ecarts.append(f"{cle} : {e.forme} {e.source} (décret {e.decret}) écrit "
                          f"{e.ecrit}, soit {e.euros:.2f} € ; la caisse {euros:.2f} €"
                          + (" — et un autre texte le redit" if accord else ""))
        if not accord:
            continue
        certifiees[cle] = {
            "euros": round(euros, 6),
            "sources": sorted({f"{e.source} ({e.forme}, décret {e.decret})"
                               + (f", date de {e.date_de}" if e.date_de else "")
                               + (f", {e.derivation}" if e.derivation else "")
                               for e in accord}),
        }
        cites = re.search(r"(?:Décret|Loi|Ordonnance) (\d{2,4})/(\d+)", references.get(cle, ""))
        if cites and f"{cites.group(1)}-{cites.group(2)}" not in {e.decret for e in accord}:
            citations.append(f"{cle} : la caisse le rapporte au décret n° "
                             f"{cites.group(1)}-{cites.group(2)}, le Journal officiel "
                             f"le lit dans le décret n° "
                             + ", ".join(sorted({e.decret for e in accord})))
    # Ce que les textes datent autrement que la caisse, ou qu'elle n'a pas.
    connus = {tuple(cle.split("|")) for cle in datees}
    autrement = []
    for (serie, jour), lus in sorted(par_cle.items()):
        if (serie, jour) in connus or serie == "as_marie":
            continue
        for e in lus:
            if e.derivation:
                continue
            meme = [cle for cle, euros in datees.items()
                    if cle.startswith(serie + "|") and abs(euros - e.euros) <= TOLERANCE]
            autrement.append(f"{serie} {jour} : {e.forme} {e.source} (décret {e.decret}) "
                             f"écrit {e.ecrit}"
                             + (f" ; la caisse date ce montant du {meme[0].split('|')[1]}"
                                if meme else " ; la caisse n'a pas ce montant"))
    # Le montant d'une personne mariée qu'une notice écrit quand l'article ne
    # le fixe pas : celui que le plafond du couple laisse à chacun, une fois
    # les deux AVTS servies (L. 815-8), ce que le modèle calcule de lui-même.
    for e in enonces:
        if e.serie != "as_marie" or e.forme == "article":
            continue
        plafond = _montant_en_vigueur(datees, "plafond_couple", e.date)
        avts = _montant_en_vigueur(datees, "avts", e.date)
        reste = None if plafond is None or avts is None else (plafond - 2 * avts) / 2
        autrement.append(
            f"as_marie {e.date} : {e.forme} {e.source} (décret {e.decret}) écrit {e.ecrit} "
            "pour une personne mariée, que l'article ne fixe pas"
            + (" : la moitié du plafond du couple diminué de deux AVTS, ce que "
               "le plafond laisse à chacun" if reste is not None
               and abs(reste - e.euros) <= TOLERANCE else ""))
    return {"certifiees": certifiees, "ecarts": ecarts, "citations": citations,
            "autrement": autrement}


def _montant_en_vigueur(datees: dict[str, float], serie: str, jour: str) -> float | None:
    effet = _en_vigueur(datees, serie, jour)
    return None if effet is None else datees[f"{serie}|{effet}"]


def annees_certifiees(cnav: dict, certifiees: dict) -> tuple[list[int], dict[str, dict[str, float]]]:
    """Les années dont toute la ligne est certifiée, et chaque série pour elles."""
    datees = cnav["datee"]
    premiere = min(int(cle.split("|")[1][:4]) for cle in datees)
    annees, series = [], {colonne: {} for colonne in COLONNES}
    for annee in range(premiere, DERNIERE_ANNEE + 1):
        jour = f"{annee}-12-31"
        valeurs, complete = {}, True
        for colonne, serie in COLONNES.items():
            effet = _en_vigueur(datees, serie, jour)
            if effet is None:
                continue
            cle = f"{serie}|{effet}"
            if cle not in certifiees:
                complete = False
                break
            valeurs[colonne] = certifiees[cle]["euros"]
        if complete and valeurs:
            annees.append(annee)
            for colonne, valeur in valeurs.items():
                series[colonne][str(annee)] = valeur
    return annees, series


def seuils_certifies(cnav: dict, certifiees: dict,
                     dix_huit_francs: float | None) -> dict[str, float]:
    """Le seuil d'un trimestre que R. 351-9 définit, aux années où il se
    certifie : 18 F lus de 1946 à 1948, le quart de l'AVTS certifiée au
    1er janvier de 1949 à 1971. La valeur écrite est celle que
    ``cnav_avts.py`` a calculée, à neuf décimales, quand elle s'accorde au
    centime avec celle-ci : un salaire qui tombe pile sur le seuil doit
    continuer de le valider."""
    calcules = {}
    if dix_huit_francs is not None:
        calcules.update({str(a): dix_huit_francs for a in ANNEES_DIX_HUIT_FRANCS})
    for annee in range(PREMIERE_ANNEE_AVTS, DERNIERE_ANNEE_AVTS + 1):
        effet = _en_vigueur(cnav["datee"], "avts", f"{annee}-01-01")
        cle = f"avts|{effet}"
        if effet is not None and cle in certifiees:
            calcules[str(annee)] = certifiees[cle]["euros"] / 4
    publies = cnav.get("seuil_trimestre", {})
    return {annee: round(publies[annee] if annee in publies
                         and abs(publies[annee] - valeur) <= TOLERANCE else valeur, 9)
            for annee, valeur in sorted(calcules.items())}


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--index-jorf", help="chemin de l'index JORF")
    analyseur.add_argument("--index-legi", help="chemin de l'index LEGI")
    analyseur.add_argument("--cnav", type=Path, default=CNAV,
                           help="la sortie de cnav_avts.py")
    options = analyseur.parse_args(argv)
    if not options.cnav.exists():
        print(f"ÉCHEC   {options.cnav} absent : lancer d'abord "
              "python scripts/fetch/cnav_avts.py", file=sys.stderr)
        return 1
    cnav = json.loads(options.cnav.read_text(encoding="utf-8"))
    try:
        jorf, source_jorf = ouvrir_lecture("jorf", options.index_jorf)
        legi, source_legi = ouvrir_lecture("legi", options.index_legi)
    except FileNotFoundError as erreur:
        print(f"ÉCHEC   {erreur}", file=sys.stderr)
        return 1
    textes = textes_pertinents(jorf) + textes_pertinents(legi)
    enonces = enonces_des_textes(textes)
    dix_huit_francs, redactions = seuil_de_r351_9(legi)
    resultat = confronter(cnav, enonces)
    certifiees = resultat["certifiees"]
    if not certifiees:
        print("ÉCHEC   aucun montant de la caisse n'est redit par un texte : l'index "
              "est-il le bon ?", file=sys.stderr)
        return 1
    annees, series = annees_certifiees(cnav, certifiees)
    seuils = seuils_certifies(cnav, certifiees, dix_huit_francs)
    sans_texte = sorted(cle for cle in cnav["datee"]
                        if cle.split("|")[1] <= f"{DERNIERE_ANNEE}-12-31"
                        and cle not in certifiees)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": f"{source_jorf} ; {source_legi}",
        "recupere_le": date.today().isoformat(),
        "bareme_relu": f"{options.cnav.name}, récupéré le {cnav.get('recupere_le', '?')}",
        "note": "Les montants de l'AVTS, de l'allocation supplémentaire et de son "
                "plafond que la Cnav date (cnav_avts.py), relus dans les textes du "
                "Journal officiel et de LEGI : les montants datés certifiés et leurs "
                "sources (certifiees), les années dont toute la ligne l'est "
                "(annees_certifiees) et chaque série pour elles (serie_*), le seuil "
                "d'un trimestre certifié (seuil_trimestre), et ce que les textes "
                "disent autrement que la caisse.",
        "textes_lus": len({t[0] for t in textes}),
        "enonces": [asdict(e) for e in sorted(
            enonces, key=lambda e: (e.date or "", e.serie, e.source))],
        "certifiees": certifiees,
        "sans_texte": sans_texte,
        "ecarts": resultat["ecarts"],
        "autrement": resultat["autrement"],
        "citations": resultat["citations"],
        "annees_certifiees": annees,
        **{f"serie_{colonne}": valeurs for colonne, valeurs in series.items()},
        "seuil_trimestre": seuils,
        "r351_9": redactions,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len({t[0] for t in textes})} textes lus, {len(enonces)} énoncés ; "
          f"{len(certifiees)} montants datés de la caisse redits par un texte, "
          f"{len(sans_texte)} sans texte qui les redise")
    print(f"Années dont toute la ligne est certifiée : {annees}")
    print(f"Seuil d'un trimestre certifié : {sorted(int(a) for a in seuils)}")
    for titre, lignes in (("écart", resultat["ecarts"]),
                          ("autrement", resultat["autrement"]),
                          ("citation", resultat["citations"])):
        for ligne in lignes:
            print(f"  {titre} : {ligne}")
    print(f"Écrit dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
