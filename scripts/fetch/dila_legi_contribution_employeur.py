#!/usr/bin/env python3
"""Contribution employeur des régimes spéciaux, dans les textes qui la fixent.

    python scripts/fetch/dila_legi_contribution_employeur.py

Ce qu'il referme. ``docs/limites.md`` rangeait douze régimes sous une seule
ligne : « rien / tout — aucune série de taux employeur publiée sous une forme
exploitable ». C'était vrai de la recherche menée, pas des textes : le *Journal
officiel* porte la contribution de la RATP, celle des industries électriques et
gazières, celle de la SNCF d'avant 2007, celle des mines, celle de l'Opéra et
celle de la Comédie-Française. Six régimes de moins sur cette ligne, et pour
chacun un taux LU plutôt que celui d'un salarié du privé mis à sa place.

DEUX FORMES DE TEXTE, DEUX LECTURES

**L'arrêté annuel** — RATP et IEG. Ces deux régimes ont été « adossés » au
régime général en 2005-2006 : l'employeur verse depuis lors ce que les mêmes
salariés coûteraient à la CNAV et à l'Agirc-Arrco, et le taux qui le réalise est
arrêté chaque année, une fois l'exercice connu. C'est la mécanique de la
composante T1 de la SNCF, et la convention de date est la même :

* un arrêté porte **deux taux**, le PROVISIONNEL appelé d'avance et le DÉFINITIF
  arrêté après coup. Seul le définitif est retenu — il est ce qui est dû ;
* il date son taux par l'EXERCICE, non par une date d'effet : « fixé à 19,43 %
  pour l'exercice 2024 » range 19,43 % en 2024, sans passer par la règle du
  1er janvier ;
* un arrêté **corrige** parfois le précédent. Celui du 23 juin 2020 ramène le
  taux 2019 de la RATP de 19,20 % à 19,18 %. Quand deux textes se disputent une
  année, le plus récent l'emporte, et l'écart est conservé au fichier brut.

**La version datée d'un article** — SNCF d'avant 2007, mines, Opéra,
Comédie-Française. Là, le taux est dans un article dont la base LEGI garde les
rédactions successives, et la règle du dépôt s'applique : le taux en vigueur au
1er JANVIER de l'année. Une même version peut porter plusieurs taux, chacun daté
par ce qui le suit — « 9,20 % pour l'année 2017 ; 9,25 % pour l'année 2018 » —,
et c'est la date la plus proche du taux qui le date, comme pour la CNRACL.

CE QUE CES TAUX SONT, ET CE QU'ILS NE SONT PAS

Ce fichier ne porte que ce que l'EMPLOYEUR verse. Trois de ces régimes reçoivent
aussi de l'État une contribution qui n'est pas ici, parce qu'elle n'est pas une
cotisation d'employeur :

* la **RATP** ne finance les droits spécifiques du régime que pour ses agents
  au-delà de 45 000 ; en deçà, c'est l'État (article 4 du décret n° 2005-1637) ;
* les **mines** reçoivent de l'État « une cotisation correspondant à 22 % des
  salaires » plus une contribution d'équilibre (article 52 du décret de 1946) —
  soit près de trois fois ce que verse l'exploitant ;
* l'**Opéra** perçoit un droit sur les places et une contribution de l'État
  (article 4, 3° et 5°, du décret du 5 avril 1968).

C'est la même convention que pour la SNCF, dont la somme T1 + T2 laisse dehors
la subvention d'équilibre de l'État. Un taux d'employeur, et non un taux
d'équilibre — à la différence de la ligne de l'État, qui est l'un et l'autre.

LES SIX SÉRIES, ET OÙ CHACUNE S'ARRÊTE

* **RATP, 2007-2025** — arrêtés annuels pris pour l'article 2 du décret
  n° 2005-1637 du 26 décembre 2005. Deux années ne sont que dans la base JORF,
  les arrêtés de 2018 et de 2022 n'ayant pas été versés à LEGI : les deux bases
  sont donc lues. Avant 2007, la RATP payait les pensions sans qu'aucun taux
  soit fixé, comme l'État avant son compte d'affectation spéciale ;
* **IEG, 2005-2020** — arrêtés annuels pris pour l'article 3 du décret
  n° 2005-278 du 24 mars 2005. La série s'arrête là, et pour une raison écrite :
  l'arrêté du 29 décembre 2021 remplace la fixation annuelle par une FORMULE,
  ``T = [(a) + (b) - (c)] / (d)``, que la caisse applique sans que le *Journal
  officiel* en publie le résultat. Même mur que la composante T2 de la SNCF ;
* **SNCF, 1992-2006** — « est fixé à 36,29 p. 100, soit 28,44 p. 100 à la
  charge de l'employeur », II de l'article 8 du décret n° 91-613 du 28 juin
  1991, abrogé le 29 juin 2007. 2007 n'est pas rendue : l'arrêté qui fixe T1
  « pour l'année 2007 » date l'exercice entier, et le dépôt porte déjà cette
  année-là au titre de la somme T1 + T2 ;
* **mines, 1984-2026** — « 7,75 % à la charge des employeurs », article 52 du
  décret n° 46-2769 du 27 novembre 1946 jusqu'en 1992, article 90 du même décret
  depuis 1993. Le taux n'a pas bougé en quarante ans. Seule la part PLAFONNÉE
  est portée : la fiche du régime a une assiette plafonnée, et les 1,6 % dus sur
  la totalité des rémunérations depuis 1991 n'y trouveraient pas leur place ;
* **Opéra national de Paris et Comédie-Française, 1992-2026** — II des articles
  6 et 7 du décret n° 91-613, qui fixent « le taux de la contribution
  mentionnée au 2° de l'article 4 » des décrets n° 68-382 et n° 68-960. Cette
  contribution est « égale à un pourcentage des rémunérations soumises à retenue
  pour pension » : la même assiette que la retenue de l'agent, exactement ce que
  le modèle attend.

CE QU'ON NE PEUT PAS AFFIRMER

La base garde les versions, pas la preuve qu'elle les garde toutes : la leçon de
la CNRACL, où un décret manquant faisait courir une version quinze ans sans
coupure. Deux garde-fous sont repris ici. Le premier est la CONTRADICTION — un
texte de la base qui dit remplacer un taux que la version qu'il coupe ne porte
pas dénonce la lacune. Le second est la CORROBORATION aux bornes : le décret
n° 91-159 du 12 février 1991 porte déjà 8,80 % pour l'Opéra et la
Comédie-Française, et le décret n° 91-225 du 27 février 1991 déjà 28,44 % pour
la SNCF ; l'article 8 du décret de 1991 est explicitement abrogé en 2007, et
l'article 52 du décret de 1946 explicitement remplacé par l'article 90 en 1993.
Les deux bouts de chaque chaîne sont donc tenus par un texte, et non supposés.
Il reste qu'une version de vingt ans — celle de l'Opéra, 1991 à 2011 — ne
prouve pas qu'aucun décret n'a été perdu entre-temps. Le récupérateur le dit et
ne le cache pas derrière un chiffre.

POURQUOI IL LIT L'INDEX ET NON LE DUMP

Les récupérateurs ``dila_legi_*`` plus anciens retéléchargent le dump global de
la DILA : 1,1 Go et un quart d'heure chacun. Ce dump n'a pas été régénéré depuis
juillet 2025, quand l'index publié par le dépôt lui applique les incréments
quotidiens — l'arrêté RATP du 13 mars 2026, qui porte l'année 2025, n'est QUE
dans l'index. Lire le dump serait ici à la fois plus lent et moins complet.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dila_index import chemin_index, meta, recuperer  # noqa: E402

SORTIE = Path("data/brut/dila_contribution_employeur.json")

#: « 7,75 p. 100 », « 19,43 % », « 19 % » : le Journal officiel laisse tomber
#: les décimales quand elles sont nulles.
TAUX = re.compile(r"(\d{1,2}(?:,\d+)?)\s*(?:%|p\.\s?100)")

#: Les façons dont ces textes datent un taux, de la plus explicite à la moins.
#: On retient celle qui suit le taux au plus près.
QUALIFICATIFS = (
    re.compile(r"[àa]\s+compter\s+(?:du\s+1er\s+janvier|de\s+l['’]ann[ée]e)\s+(\d{4})",
               re.I),
    re.compile(r"pour\s+l['’]ann[ée]e\s+(\d{4})", re.I),
    re.compile(r"jusqu['’]au\s+31\s+d[ée]cembre\s+(\d{4})", re.I),
)

#: Une version qui court plus longtemps que cela peut avoir avalé un texte que
#: la base n'a pas gardé. Elle n'est pas écartée — la corroboration aux bornes
#: la tient —, mais elle est signalée.
DUREE_SUSPECTE_ANS = 15

#: L'année où s'arrête le dépôt. Une version TOUJOURS EN VIGUEUR vaut jusque-là
#: et pas au-delà : le taux des mines n'a pas bougé depuis 2018 et court donc
#: encore, mais rien n'autorise à l'écrire pour 2030. La base borne ses versions
#: en cours au 1er janvier 2999, qui n'est pas une date mais une absence de
#: date ; c'est cette constante qui la remplace.
DERNIERE_ANNEE = 2026

#: La borne que la base met aux versions en cours, et qu'il ne faut pas lire
#: comme une durée.
SANS_FIN = date(2999, 1, 1)


# ---------------------------------------------------------------------------
# Les deux formes de lecture
# ---------------------------------------------------------------------------


def _nombre(brut: str) -> float:
    return float(re.sub(r"\s", "", brut).replace(",", "."))


def _date_du_taux(fenetre: str, defaut: date) -> date:
    """Date que porte le texte qui SUIT un taux, ou celle de la version.

    « 9,20 % pour l'année 2017 ; 9,25 % pour l'année 2018 » : chaque taux est
    daté par ce qui le suit immédiatement. Lire la première date de la fenêtre
    et non la plus proche décalerait toute la table d'un cran.

    « jusqu'au 31 décembre 2016 » date une FIN, non un début : le taux qu'elle
    qualifie vaut depuis l'ouverture de la version, et c'est elle qu'on rend.
    """
    trouvees = []
    for rang, motif in enumerate(QUALIFICATIFS):
        trouve = motif.search(fenetre)
        if trouve is not None:
            trouvees.append((trouve.start(), rang, trouve))
    if not trouvees:
        return defaut
    _, rang, trouve = min(trouvees)
    if rang == 2:
        return defaut
    return date(int(trouve.group(1)), 1, 1)


def taux_par_date(versions: list[tuple[str, str, str]],
                  bloc_utile,
                  plausible: tuple[float, float]) -> dict[date, float]:
    """Taux par date d'effet, lu dans les versions datées d'un article.

    Les versions sont prises dans l'ordre où elles entrent en vigueur : une
    rédaction plus récente qui redate un taux l'emporte sur l'ancienne, comme
    le fait le droit.
    """
    par_date: dict[date, float] = {}
    for debut, _, texte in sorted(versions):
        bloc = bloc_utile(texte)
        if not bloc:
            continue
        try:
            entree = date.fromisoformat(debut)
        except ValueError:
            continue
        trouves = list(TAUX.finditer(bloc))
        for rang, trouve in enumerate(trouves):
            fin = trouves[rang + 1].start() if rang + 1 < len(trouves) else len(bloc)
            valeur = _nombre(trouve.group(1)) / 100
            if not plausible[0] <= valeur <= plausible[1]:
                continue
            par_date[_date_du_taux(bloc[trouve.end():fin][:140], entree)] = valeur
    return par_date


def serie_annuelle(par_date: dict[date, float],
                   fin: date | None) -> dict[int, float]:
    """Taux en vigueur au 1er janvier de chaque année, la règle du dépôt.

    ``fin`` est la date où l'article cesse de porter le taux : l'expiration de
    sa dernière version, ou une borne plus proche quand le régime en impose une.
    Au-delà, rien n'est écrit, et rien n'est rendu.

    Une version TOUJOURS EN VIGUEUR n'a pas de fin, et le dernier taux court
    alors jusqu'à ``DERNIERE_ANNEE`` : s'arrêter à la date d'entrée de cette
    version rendrait le modèle muet sur les huit années que le droit remplit
    depuis 2018 pour les mines. Les combler par le repli serait pire que les
    lire — le texte les porte.
    """
    dates = sorted(par_date)
    if not dates:
        return {}
    derniere = (fin.year - 1) if fin else max(dates[-1].year, DERNIERE_ANNEE)
    serie: dict[int, float] = {}
    for annee in range(dates[0].year, derniere + 1):
        applicables = [d for d in dates if d <= date(annee, 1, 1)]
        if applicables:
            serie[annee] = par_date[applicables[-1]]
    return serie


def _expiration(versions: list[tuple[str, str, str]], bloc_utile) -> date | None:
    """Date où le dernier texte qui porte le taux cesse de le porter.

    ``None`` si cette version est toujours en vigueur. Sans ce calcul, une
    abrogation future prolongerait silencieusement un taux mort jusqu'à
    ``DERNIERE_ANNEE`` — c'est ce qui serait arrivé à la SNCF si le décret de
    2007 n'avait pas été borné à la main, et une borne écrite à la main ne
    protège que ce qu'on a pensé à borner.
    """
    portantes = []
    for debut, fin, texte in versions:
        if not bloc_utile(texte):
            continue
        try:
            portantes.append((date.fromisoformat(debut), date.fromisoformat(fin)))
        except ValueError:
            continue
    if not portantes:
        return None
    _, derniere = max(portantes)
    return None if derniere == SANS_FIN else derniere


# ---------------------------------------------------------------------------
# Les arrêtés annuels : RATP et IEG
# ---------------------------------------------------------------------------


#: « est fixé à 19,43 % pour l'exercice 2024 » et « est fixé à : 17,94 % pour
#: l'exercice 2007 ; 18,02 % pour l'exercice 2008 ». Le taux précède l'année.
TAUX_PUIS_ANNEE = re.compile(
    r"(\d{1,2}(?:,\d+)?)\s*%\s*(?:est fix[ée]\s*)?pour l['’](?:exercice|ann[ée]e)\s*"
    r"(\d{4})", re.I)

#: « pour l'exercice 2024 est fixé à 19,43 % » : l'arrêté de 2025 inverse
#: l'ordre, et il est le seul à porter cette année-là.
ANNEE_PUIS_TAUX = re.compile(
    r"pour l['’](?:exercice|ann[ée]e)\s*(\d{4})[^.]{0,160}?est fix[ée]\s*[àa]\s*"
    r"(\d{1,2}(?:,\d+)?)\s*%", re.I)

#: « établissant à 24,41 % le taux définitif […] pour l'exercice 2005 » : la
#: forme propre aux arrêtés de la CNIEG, qui approuvent une délibération.
DELIBERATION = re.compile(
    r"[ée]tablissant\s*[àa]\s*(\d{1,2}(?:,\d+)?)\s*%\s*le taux d[ée]finitif"
    r"(.{0,320}?)exercice\s*(\d{4})", re.I | re.S)

DEFINITIF = re.compile(r"d[ée]finitif", re.I)
PROVISIONNEL = re.compile(r"provisionnel", re.I)


def _phrases_definitives(texte: str) -> list[str]:
    """Les morceaux du texte qui parlent du taux DÉFINITIF, et eux seuls.

    Un même article porte souvent les deux taux — « Le taux provisionnel […]
    est fixé à 19,13 % pour l'exercice 2023. Le taux définitif […] est fixé à
    19,19 % pour l'exercice 2022. » —, et les confondre coûterait un point de
    taux sur une année sur deux. Le texte est coupé à chaque « le taux » ; un
    morceau est gardé si le premier des deux qualificatifs qu'il porte est
    « définitif ».
    """
    gardes = []
    for morceau in re.split(r"(?=\b[Ll]e taux\b)", texte):
        definitif, provisionnel = DEFINITIF.search(morceau), PROVISIONNEL.search(morceau)
        if definitif is None:
            continue
        if provisionnel is not None and provisionnel.start() < definitif.start():
            continue
        gardes.append(morceau)
    return gardes


def lectures_annuelles(textes: list[tuple[str, str, str]],
                       plausible: tuple[float, float],
                       deliberation: bool = False
                       ) -> tuple[dict[int, float], list[str], list[str]]:
    """Taux définitif par exercice, lu dans les arrêtés annuels.

    Rend la série, les identifiants des textes qui l'ont donnée, et les écarts :
    une année que deux textes chiffrent différemment est tranchée par le plus
    RÉCENT — un arrêté modificatif corrige celui qu'il modifie —, et le désaccord
    est rendu pour que la correction reste visible.
    """
    par_annee: dict[int, tuple[str, float]] = {}
    origines: set[str] = set()
    ecarts: list[str] = []
    for ident, publication, texte in sorted(textes, key=lambda ligne: ligne[1]):
        lus: list[tuple[int, float]] = []
        if deliberation:
            for valeur, entre, annee in DELIBERATION.findall(texte):
                if PROVISIONNEL.search(entre):
                    continue
                lus.append((int(annee), _nombre(valeur)))
        else:
            for phrase in _phrases_definitives(texte):
                for valeur, annee in TAUX_PUIS_ANNEE.findall(phrase):
                    lus.append((int(annee), _nombre(valeur)))
                for annee, valeur in ANNEE_PUIS_TAUX.findall(phrase):
                    lus.append((int(annee), _nombre(valeur)))
        for annee, valeur in lus:
            taux = valeur / 100
            if not plausible[0] <= taux <= plausible[1]:
                continue
            ancien = par_annee.get(annee)
            if ancien is not None and abs(ancien[1] - taux) > 1e-9:
                ecarts.append(
                    f"{annee} : {ancien[1]:.2%} ({ancien[0]}) corrigé en "
                    f"{taux:.2%} par {ident}, publié le {publication}")
            par_annee[annee] = (ident, taux)
            origines.add(ident)
    return ({annee: taux for annee, (_, taux) in sorted(par_annee.items())},
            sorted(origines), ecarts)


# ---------------------------------------------------------------------------
# Les blocs utiles, article par article
# ---------------------------------------------------------------------------


def _entre(debut: re.Pattern, fin: re.Pattern | None, large: int = 700):
    """Fabrique un extracteur du morceau d'article qui porte le taux cherché."""
    def extraire(texte: str) -> str:
        depart = debut.search(texte)
        if depart is None:
            return ""
        reste = texte[depart.end():]
        if fin is None:
            return reste[:large]
        arret = fin.search(reste)
        return reste[:arret.start()] if arret else reste[:large]
    return extraire


#: Le II de l'article 6 (Opéra) et de l'article 7 (Comédie-Française) : la
#: contribution de l'établissement. Le I, qui le précède, porte la retenue de
#: l'agent — sept à onze pour cent, dans la même plage que la contribution des
#: premières années : le confondre avec elle ne se verrait pas.
CONTRIBUTION_1968 = _entre(
    re.compile(r"Le taux de la contribution (?:pr[ée]vue|mentionn[ée]e) au 2"),
    None)

#: Le II de l'article 8 : la cotisation d'assurance vieillesse de la SNCF, dont
#: le texte donne le total puis sa répartition. C'est la part employeur qu'on
#: veut, et elle suit « soit ».
#: Le « p. 100 » de ces textes interdit de borner la recherche aux points :
#: c'est la seule raison pour laquelle ces motifs se lisent au caractère près.
COTISATION_SNCF = _entre(
    re.compile(r"cotisation d'assurance vieillesse.{0,220}?"
               r"est fix[ée]\s*[àa].{0,40}?soit", re.S),
    re.compile(r"[àa] la charge de l['’]agent"))

#: L'article 52 du décret de 1946 jusqu'en 1992, puis l'article 90 : dans l'un
#: comme dans l'autre, la part de l'exploitant est nommée avant le taux.
COTISATION_MINES_52 = _entre(
    re.compile(r"cotisation de l['’]exploitant est fix[ée]e?\s*[àa]"),
    re.compile(r"des salaires"))
#: « à hauteur de 15,60 %, soit 7,75 % à la charge des employeurs et 7,85 % à
#: la charge des salariés » : trois taux dans une phrase, et il faut le
#: deuxième. La lecture s'arrête donc à « à la charge des employeurs », que le
#: taux cherché PRÉCÈDE — s'arrêter à la part salariale la laisserait entrer.
COTISATION_MINES_90 = _entre(
    re.compile(r"hauteur de\s*\d{1,2},\d+\s*(?:%|p\.\s?100)\s*,?\s*soit"),
    re.compile(r"[àa] la charge des employeurs"))


# ---------------------------------------------------------------------------
# L'index
# ---------------------------------------------------------------------------


def _ouvrir(base: str) -> sqlite3.Connection:
    chemin = chemin_index(base)
    if not chemin.exists():
        print(f"Index {base} absent : récupération de l'index publié.")
        recuperer(base, chemin)
    db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    print(f"Index {base:<5} {meta(db, 'dump') or '?'}, "
          f"à jour au {meta(db, 'dernier_increment') or '?'}")
    return db


def versions(db: sqlite3.Connection, titre: str, article: str
             ) -> list[tuple[str, str, str]]:
    """Les rédactions successives d'un article, datées au jour."""
    lignes = db.execute(
        "SELECT date, fin, texte FROM doc WHERE titre LIKE ? AND num = ? "
        "AND nature LIKE '%Article%'", (f"%{titre}%", article)).fetchall()
    return [(debut or "", fin or "", texte or "") for debut, fin, texte in lignes]


def textes(db: sqlite3.Connection, motif_titre: str) -> list[tuple[str, str, str]]:
    """Les articles dont le titre porte le motif, avec leur date de publication."""
    lignes = db.execute(
        "SELECT id, date, texte FROM doc WHERE titre LIKE ? "
        "AND nature LIKE '%Article%'", (f"%{motif_titre}%",)).fetchall()
    return [(ident, publication or "", texte or "") for ident, publication, texte in lignes]


# ---------------------------------------------------------------------------
# Assemblage
# ---------------------------------------------------------------------------


#: Ce que le récupérateur lit, régime par régime. Chaque série dit d'où elle
#: vient, ce qui la borne, et dans quelle plage son taux est plausible : hors
#: de cette plage, la phrase lue parle d'autre chose.
SERIES_DATEES = {
    "sncf": {
        "titre": "91-613 du 28 juin 1991",
        "article": "8",
        "bloc": COTISATION_SNCF,
        "plausible": (0.20, 0.35),
        # L'article est abrogé le 29 juin 2007, mais 2007 appartient déjà à la
        # somme T1 + T2 : l'arrêté qui fixe T1 « pour l'année 2007 » date
        # l'exercice entier, et deux sources ne peuvent pas se disputer l'année.
        "fin": date(2007, 1, 1),
        "texte": "décret n° 91-613 du 28 juin 1991, article 8 II",
    },
    "opera_de_paris": {
        "titre": "91-613 du 28 juin 1991",
        "article": "6",
        "bloc": CONTRIBUTION_1968,
        "plausible": (0.05, 0.15),
        "fin": None,
        "texte": "décret n° 91-613 du 28 juin 1991, article 6 II, renvoyant au 2° "
                 "de l'article 4 du décret n° 68-382 du 5 avril 1968",
    },
    "comedie_francaise": {
        "titre": "91-613 du 28 juin 1991",
        "article": "7",
        "bloc": CONTRIBUTION_1968,
        "plausible": (0.05, 0.15),
        "fin": None,
        "texte": "décret n° 91-613 du 28 juin 1991, article 7 II, renvoyant au 2° "
                 "de l'article 4 du décret n° 68-960 du 11 octobre 1968",
    },
    "mines_52": {
        "titre": "46-2769 du 27 novembre 1946",
        "article": "52",
        "bloc": COTISATION_MINES_52,
        "plausible": (0.05, 0.15),
        # L'article cesse de porter la cotisation le 1er janvier 1993, où
        # l'article 90 la reprend.
        "fin": date(1993, 1, 1),
        "texte": "décret n° 46-2769 du 27 novembre 1946, article 52",
    },
    "mines_90": {
        "titre": "46-2769 du 27 novembre 1946",
        "article": "90",
        "bloc": COTISATION_MINES_90,
        "plausible": (0.05, 0.15),
        "fin": None,
        "texte": "décret n° 46-2769 du 27 novembre 1946, article 90",
    },
}

SERIES_ARRETEES = {
    "ratp": {
        # Le titre de ces arrêtés a changé quatre fois en vingt ans : au
        # singulier puis au pluriel, « contribution patronale » puis
        # « cotisation à la charge de », puis « cotisation due par ». Un seul
        # motif perdait cinq années, dont les cinq premières.
        "motifs": ("patronale de la R", "patronales de la R",
                   "cotisation à la charge de la Régie autonome",
                   "cotisation due par la Régie autonome"),
        "plausible": (0.10, 0.30),
        "deliberation": False,
        "texte": "arrêtés annuels pris pour l'article 2 du décret n° 2005-1637 "
                 "du 26 décembre 2005",
    },
    "ieg": {
        "motifs": ("cotisation à la charge des employeurs à la Caisse nationale",
                   "cotisation des employeurs à la Caisse nationale des industries"),
        "plausible": (0.15, 0.40),
        "deliberation": True,
        "texte": "arrêtés annuels pris pour l'article 3 du décret n° 2005-278 "
                 "du 24 mars 2005",
    },
}

#: Ce qu'on attend de chaque série : sans ce minimum, la mise en page d'un texte
#: a changé ou une recherche a manqué sa cible, et il vaut mieux le savoir.
MINIMUM = {"sncf": 14, "opera_de_paris": 34, "comedie_francaise": 34,
           "mines": 42, "ratp": 18, "ieg": 15}


def _serie_datee(db: sqlite3.Connection, nom: str) -> tuple[dict[int, float], list[str]]:
    reglage = SERIES_DATEES[nom]
    lues = versions(db, reglage["titre"], reglage["article"])
    if not lues:
        raise LookupError(f"{nom} : aucune version de l'article "
                          f"{reglage['article']} de {reglage['titre']}")
    par_date = taux_par_date(lues, reglage["bloc"], reglage["plausible"])
    # La borne écrite l'emporte quand elle est plus proche — 2007 pour la SNCF,
    # dont l'article court jusqu'au 29 juin mais dont l'exercice entier
    # appartient déjà à la somme T1 + T2.
    naturelle = _expiration(lues, reglage["bloc"])
    bornes = [b for b in (naturelle, reglage["fin"]) if b is not None]
    fin = min(bornes) if bornes else None
    dits = []
    for debut, cloture, texte in sorted(lues):
        if not reglage["bloc"](texte):
            continue
        try:
            ouverture, fermeture = date.fromisoformat(debut), date.fromisoformat(cloture)
        except ValueError:
            continue
        if fermeture == SANS_FIN:
            continue
        if (fermeture - ouverture).days > DUREE_SUSPECTE_ANS * 366:
            dits.append(
                f"{nom} : la version du {ouverture} court {(fermeture - ouverture).days // 365} "
                "ans sans modification — la base pourrait avoir perdu un décret")
    return serie_annuelle(par_date, fin), dits


def main() -> int:
    try:
        legi, jorf = _ouvrir("legi"), _ouvrir("jorf")
    except (LookupError, RuntimeError) as erreur:
        print(f"ÉCHEC   index DILA : {erreur}", file=sys.stderr)
        return 1
    print()

    series: dict[str, dict[str, float]] = {}
    origines: dict[str, list[str]] = {}
    ecarts: dict[str, list[str]] = {}
    griefs: list[str] = []

    # Les articles datés : SNCF, Opéra, Comédie-Française, mines.
    try:
        for nom in SERIES_DATEES:
            serie, dits = _serie_datee(legi, nom)
            griefs += dits
            series[nom] = {str(annee): round(taux, 6)
                           for annee, taux in sorted(serie.items())}
    except LookupError as erreur:
        print(f"ÉCHEC   {erreur}", file=sys.stderr)
        return 1

    # Les deux articles des mines sont une seule série, en deux morceaux
    # contigus : l'article 90 reprend le 1er janvier 1993 où l'article 52
    # s'arrête. Un recouvrement dirait que l'un des deux est mal borné.
    avant, apres = series.pop("mines_52"), series.pop("mines_90")
    if set(avant) & set(apres):
        print(f"ÉCHEC   mines : les articles 52 et 90 se recouvrent sur "
              f"{sorted(set(avant) & set(apres))}", file=sys.stderr)
        return 1
    series["mines"] = dict(sorted({**avant, **apres}.items()))

    # Les arrêtés annuels : RATP et IEG. Les deux bases sont lues, JORF portant
    # deux arrêtés RATP que LEGI n'a pas.
    for nom, reglage in SERIES_ARRETEES.items():
        trouves: dict[str, tuple[str, str, str]] = {}
        for base in (legi, jorf):
            for motif in reglage["motifs"]:
                for ident, publication, texte in textes(base, motif):
                    # Un même arrêté figure dans les deux bases sous deux
                    # identifiants ; sa date de publication et son texte, eux,
                    # sont les mêmes, et c'est par là qu'on l'y reconnaît.
                    trouves[f"{publication}|{texte[:400]}"] = (ident, publication, texte)
        serie, lus, desaccords = lectures_annuelles(
            list(trouves.values()), reglage["plausible"], reglage["deliberation"])
        series[nom] = {str(annee): round(taux, 6)
                       for annee, taux in sorted(serie.items())}
        origines[nom], ecarts[nom] = lus, desaccords

    for nom, minimum in MINIMUM.items():
        if len(series.get(nom, {})) < minimum:
            print(f"ÉCHEC   {nom} : {len(series.get(nom, {}))} années lues, "
                  f"{minimum} attendues — un texte a dû changer de rédaction",
                  file=sys.stderr)
            return 1

    # Une série trouée ne se voit pas dans son décompte : elle se voit ici.
    for nom, serie in series.items():
        annees = sorted(int(a) for a in serie)
        manquantes = [a for a in range(annees[0], annees[-1] + 1)
                      if str(a) not in serie]
        if manquantes:
            griefs.append(f"{nom} : rien pour {manquantes}")

    for grief in griefs:
        print(f"SIGNALÉ {grief}")
    for nom, desaccords in ecarts.items():
        for desaccord in desaccords:
            print(f"CORRIGÉ {nom} {desaccord}")
    if griefs or any(ecarts.values()):
        print()

    for nom, serie in sorted(series.items()):
        annees = sorted(serie)
        print(f"{nom:<20} {len(serie):>3} années {annees[0]}-{annees[-1]}, "
              f"de {min(serie.values()):.2%} à {max(serie.values()):.2%}")

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": "DILA, index plein texte des bases LEGI et JORF "
                  "(scripts/fetch/dila_index.py)",
        "index_legi": meta(legi, "dump"),
        "index_jorf": meta(jorf, "dump"),
        "recupere_le": date.today().isoformat(),
        "note": "contribution de l'EMPLOYEUR seule, la retenue de l'agent restant "
                "dans la fiche du régime. Les séries d'arrêté annuel (RATP, IEG) "
                "portent le taux DÉFINITIF de l'exercice, non le provisionnel "
                "appelé d'avance ; les séries d'article daté (SNCF, mines, Opéra, "
                "Comédie-Française) portent le taux en vigueur au 1er janvier. "
                "Les contributions de l'État qui financent ces régimes — droits "
                "spécifiques de la RATP, 22 % des salaires pour les mines, "
                "subvention de l'Opéra — n'y sont pas : ce ne sont pas des "
                "cotisations d'employeur.",
        "textes": {**{nom: reglage["texte"] for nom, reglage in SERIES_DATEES.items()},
                   **{nom: reglage["texte"] for nom, reglage in SERIES_ARRETEES.items()}},
        "series": series,
        "arretes_lus": origines,
        "corrections": ecarts,
        "signalements": griefs,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nÉcrit dans {SORTIE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
