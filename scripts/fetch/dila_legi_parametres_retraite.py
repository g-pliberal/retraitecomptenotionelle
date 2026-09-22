#!/usr/bin/env python3
"""Les paramètres du scénario 1, lus dans la loi elle-même.

    python scripts/fetch/dila_index.py legi --recuperer       # l'index, une fois
    python scripts/fetch/dila_index.py legi --mettre-a-jour   # les incréments parus
    python scripts/fetch/dila_legi_parametres_retraite.py     # quelques secondes

    python scripts/fetch/dila_legi_parametres_retraite.py --dump   # 1,1 Go, un quart d'heure

Quatre tables commandent le scénario « système actuel », et donc l'écart que le
modèle affiche pour les deux autres. Elles étaient saisies depuis les textes,
sans chemin de recontrôle — `docs/limites.md` les tenait pour hors de portée,
au motif que « Légifrance expose une API, mais elle demande une clé et renvoie
du texte juridique, non des paramètres ».

Les deux moitiés de cette phrase étaient vraies et la conclusion fausse. La
base **LEGI** de la DILA est en accès libre et garde chaque version datée de
chaque article codifié ; et si elle renvoie bien du texte juridique, ce texte
est une TABLE, écrite en toutes lettres, article par article :

* `L. 161-17-2` du code de la sécurité sociale — l'âge d'ouverture des droits.
  Jusqu'en 2025, l'article ne fixait que la cible (« soixante-quatre ans pour
  les assurés nés à compter du 1er janvier 1968 ») et renvoyait la montée en
  charge à un décret, `D. 161-2-1-9` : « Soixante-deux ans et trois mois pour
  les assurés nés entre le 1er septembre 1961 et le 31 décembre 1961 inclus ».
  Depuis la loi n° 2025-1403 du 30 décembre 2025 (article 105, la SUSPENSION
  de la réforme de 2023), c'est la loi elle-même qui écrit la table, génération
  par génération, pour les nés à compter du 1er septembre 1961 — et le décret,
  qu'elle n'a pas réécrit, porte encore les âges de 2023. Le script lit donc
  les DEUX articles, chaque version s'appliquant aux générations qu'elle nomme
  à compter de sa date d'effet : la loi de 2025 recouvre le décret de 2023 sur
  les générations 1961 (septembre) à 1968, et le laisse intact avant ;
* `L. 161-17-3` — la durée d'assurance requise : « 169 trimestres, pour les
  assurés nés entre le 1er septembre 1961 et le 31 décembre 1962 » ;
* `R. 351-27` II — le coefficient de minoration : « 2,375 % pour l'assuré né en
  1944 […] 1,25 % pour l'assuré né après 1952 ». Ce II est ABROGÉ depuis le
  1er janvier 2026 (décret n° 2025-1409 du 30 décembre 2025, article 2, 29°) :
  l'article en vigueur ne porte plus que « 1,25 % », sans génération. Il ne
  change rien à personne — les générations qui avaient un coefficient plus
  lourd sont toutes au-delà de l'âge du taux plein d'office —, et la table par
  génération du dépôt reste ce que ses versions successives ont dit ;
* `D. 351-1-1` — les portes du départ anticipé pour carrière longue : « A
  cinquante-huit ans pour les assurés qui ont débuté leur activité avant l'âge
  de seize ans » ; et, au II, la borne des vingt ans PAR GÉNÉRATION, écrite en
  substitutions — « les mots : “ soixante-deux ans ” sont remplacés par les
  mots : “ l'âge prévu à l'article L. 161-17-2 minoré de deux ans et six
  mois ” » —, que le script résout contre la table d'âge en vigueur à la date
  d'effet de la version ;
* `R. 351-6` II — la durée maximale d'assurance prise en compte par la
  PRORATISATION, qu'il ne faut pas confondre avec la durée requise pour le taux
  plein : « 152 trimestres pour les assurés nés en 1944 » ;
* `R. 351-9` — le nombre d'heures de SMIC qu'il faut avoir cotisé pour valider
  un trimestre : « calculé sur la base de 200 heures », puis de 150 pour la
  période postérieure au 31 décembre 2013 ;
* `R. 351-29-1` — le nombre d'années retenues au salaire annuel moyen,
  génération par génération : « Vingt et une années pour l'assuré né en 1944 ».
  Abrogé lui aussi au 1er janvier 2026 par le même décret, qui renvoie la
  règle à l'article R. 173-3-2 : la table par génération est celle de sa
  dernière version, et le dépôt porte à part les vingt-quatre et vingt-trois
  années des parents.

Il n'y avait donc rien à demander à personne : il fallait lire. La leçon est la
même que pour la valeur du point agricole et pour le minimum contributif —
*chercher par le NUMÉRO D'ARTICLE*, LEGI étant organisée par version d'article
et non par thème.

**Où lire.** Le dump global de la DILA date du 13 juillet 2025, et elle ne l'a
pas régénéré depuis : tout ce qui a paru après — la suspension de 2026 en
premier — n'est que dans ses incréments quotidiens. C'est ce qui a fait, le
17 septembre 2026, des tables certifiées sur ce dump des tables fausses pour
tout assuré né de 1964 à 1968, sans que rien le dise. Le script lit donc
désormais l'INDEX du dépôt (`scripts/fetch/dila_index.py legi`), qui est le
dump global plus tous les incréments parus, tenu à jour chaque lundi par le
workflow `index-dila.yml` ; `--mettre-a-jour` y applique les derniers en
quelques secondes. `--dump` garde l'ancienne voie, qui ne connaît que le dump
global : elle ne sert plus qu'à contrôler l'index, et elle rendra les âges
de 2023 tant que la DILA n'aura pas régénéré son dump.

**Une version s'applique à une date d'effet, pas à sa date de publication.**
La loi de 2025 est consolidée au 31 décembre 2025 et ne s'applique qu'aux
pensions prenant effet à compter du 1er septembre 2026 ; sa note le dit. Le
script lit cette date dans la note (« s'appliquent aux pensions prenant effet à
compter du ») et ordonne les versions par elle : c'est ce qui permet de
résoudre « l'âge prévu à l'article L. 161-17-2 minoré de deux ans et six
mois » contre l'âge que la version du décret avait sous les yeux — 63 ans
pour la génération 1964 au 1er septembre 2023, 62 ans et 9 mois au
1er septembre 2026.

**Un article porte plusieurs codes.** `R. 351-27` existe aussi au code du
travail, à celui de la construction et de l'habitation, à celui de l'action
sociale ; `L. 14` existe au code forestier comme au code électoral. Le script
retient donc, pour chaque article, le code attendu.

**Une génération coupée en cours d'année.** La loi coupe parfois une génération
à une date — le 1er juillet 1951, le 1er septembre 1961, le 1er avril 1965. Le
script rend UN SEGMENT PAR VALEUR, la clé portant le mois de la coupure —
`1951.5` pour le 1er juillet 1951, `1965.25` pour le 1er avril 1965 —, et le
modèle lit ces tables au mois de naissance. Les versions successives d'un
article se recouvrent au MOIS près : une version remplace ce qu'elle dit des
mois qu'elle nomme, et laisse le reste à la précédente. C'est ainsi que la loi
de 2025, muette sur les nés avant septembre 1961 (« il est celui applicable en
application du présent article dans sa rédaction antérieure »), ne touche pas
à ce que le décret de 2011 en disait.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
SORTIE = Path("data/brut/dila_legi_parametres_retraite.json")
INDEX = Path("data/brut/dila/legi.sqlite")

#: Article -> code qui le porte. Un même numéro sert dans plusieurs codes.
ARTICLES = {
    "L161-17-2": "sécurité sociale",
    "D161-2-1-9": "sécurité sociale",
    "L161-17-3": "sécurité sociale",
    "R351-27": "sécurité sociale",
    "D351-1-1": "sécurité sociale",
    "R351-6": "sécurité sociale",
    "R351-9": "sécurité sociale",
    "R351-29-1": "sécurité sociale",
    "R351-45": "sécurité sociale",
}

#: Nombres écrits en lettres, tels que le Journal officiel les emploie pour les
#: âges. Au-delà de soixante-neuf, la retraite n'a plus de barème.
MOTS = {
    # « Vingt et une années » : le féminin, que le nombre d'années impose.
    "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6,
    "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12,
    "treize": 13, "quatorze": 14, "quinze": 15, "seize": 16, "vingt": 20,
    "trente": 30, "quarante": 40, "cinquante": 50, "soixante": 60,
}

MOIS = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
    "decembre": 12,
}

#: « soixante-deux ans et trois mois », « cinquante-six ans ».
AGE = re.compile(
    r"\b((?:cinquante|soixante)"
    r"(?:[- ](?:et[- ])?(?:un|deux|trois|quatre|cinq|six|sept|huit|neuf))?)"
    r"\s*ans?"
    r"(?:\s*et\s*(un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze)\s*mois)?",
    re.I,
)

#: Un jour du mois : « 1er », « 31 », et « 1 er » — la loi de 2025 espace le
#: « er », et le décret de 2023 le colle. Suivi du mois, puis de l'année.
JOUR = r"(\d{1,2})\s*(?:er)?"

#: Les formes par lesquelles un alinéa désigne les générations qu'il vise.
#: « entre le 1er septembre 1961 et 31 août 1963 » : le « le » manque au décret
#: de 2023 ; « entre le 1er avril et le 31 décembre 1965 » : la loi de 2025
#: omet l'année de la première date quand c'est celle de la seconde.
AVANT = re.compile(rf"n[ée]s?\s+avant\s+le\s+{JOUR}\s+(\w+)\s+(\d{{4}})", re.I)
ENTRE = re.compile(
    rf"n[ée]s?\s+entre\s+le\s+{JOUR}\s+(\w+)\s+(?:(\d{{4}})\s+)?(?:inclus\s+)?et\s+(?:le\s+)?"
    rf"{JOUR}\s+(\w+)\s+(\d{{4}})", re.I)
EN_ANNEE = re.compile(r"n[ée]s?\s+en\s+(\d{4})", re.I)
A_COMPTER = re.compile(
    rf"n[ée]s?\s+(?:à\s+compter\s+du|à\s+partir\s+du)\s+{JOUR}\s+(\w+)\s+(\d{{4}})",
    re.I)
APRES_ANNEE = re.compile(r"n[ée]\s+apr[èe]s\s+(\d{4})", re.I)

#: Chaque mention de générations d'une phrase, dans l'ordre, jusqu'à la
#: suivante : « nés entre le 1er janvier 1965 et le 30 novembre 1965 inclus et
#: pour les assurés nés entre le 1er décembre et le 31 décembre 1965 inclus ».
MENTION = re.compile(
    r"n[ée]s?\s+(?:entre|en|avant|à\s+compter|à\s+partir|apr[èe]s)\b"
    r"(?:(?!n[ée]s?\s+(?:entre|en|avant|à\s+compter|à\s+partir|apr[èe]s)\b).)*",
    re.I | re.S)

#: « s'appliquent aux pensions prenant effet à compter du 1er septembre 2026 » —
#: la note qui ouvre une version consolidée avant sa date d'application.
PRISE_D_EFFET = re.compile(
    rf"pensions\s+prenant\s+effet\s+à\s+compter\s+du\s+{JOUR}\s+(\w+)\s+(\d{{4}})",
    re.I)

#: Bornes de génération que le modèle couvre. Au-delà, la table est constante.
PREMIERE_GENERATION, DERNIERE_GENERATION = 1900, 1975


def nombre_en_lettres(texte: str | None) -> int | None:
    if texte is None:
        return 0
    mots = [m for m in re.split(r"[- ]+", texte.strip().lower())
            if m and m != "et"]
    total = 0
    for mot in mots:
        if mot not in MOTS:
            return None
        total += MOTS[mot]
    return total


def age_en_lettres(texte: str) -> float | None:
    """« Soixante et un ans et deux mois » -> 61,17."""
    trouve = AGE.search(texte)
    if trouve is None:
        return None
    annees = nombre_en_lettres(trouve.group(1))
    mois = nombre_en_lettres(trouve.group(2))
    if annees is None or mois is None:
        return None
    return round(annees + mois / 12.0, 2)


def _date(jour: str, mois: str, annee: str) -> str | None:
    numero = MOIS.get(mois.lower())
    if numero is None:
        return None
    return f"{int(annee):04d}-{numero:02d}-{int(jour):02d}"


def date_effet(date_debut: str, texte: str) -> str:
    """Date à laquelle la version s'oppose aux pensions.

    La base consolide une version à la date de publication du texte qui la
    fait, quand ce texte ne s'applique qu'aux pensions prenant effet plus
    tard — la loi de 2025 est du 31 décembre, sa table vaut au 1er septembre
    2026 — et le dit dans une note en tête de la version. C'est la plus
    tardive de ces dates qui compte, et jamais moins que la date de début.
    """
    dates = [date_debut]
    for jour, mois, annee in PRISE_D_EFFET.findall(texte):
        trouvee = _date(jour, mois, annee)
        if trouvee:
            dates.append(trouvee)
    return max(dates)


def _mois_couverts(alinea: str) -> dict[int, set[int]]:
    """MOIS de chaque génération que cet alinéa vise, un par un.

    Une génération pleine compte douze mois ; une génération coupée en compte
    autant que la période en couvre — et l'on retient LESQUELS, pas seulement
    combien. Le récupérateur ne comptait que le nombre, ce qui suffisait à
    départager deux valeurs à la majorité mais perdait la date de la coupure :
    « nés à compter du 1er septembre 1961 » se réduisait à « quatre mois de la
    génération 1961 », et le modèle opposait alors la valeur majoritaire à
    toute la génération. La table peut désormais couper là où le texte coupe.
    """
    couverts: dict[int, set[int]] = {}

    def ajouter(annee: int, premier: int, dernier: int) -> None:
        if PREMIERE_GENERATION <= annee <= DERNIERE_GENERATION and dernier >= premier:
            couverts.setdefault(annee, set()).update(
                range(max(1, premier), min(12, dernier) + 1)
            )

    trouve = ENTRE.search(alinea)
    if trouve:
        j1, m1, a1, j2, m2, a2 = trouve.groups()
        a1 = a1 or a2
        debut_mois, fin_mois = MOIS.get(m1.lower()), MOIS.get(m2.lower())
        if debut_mois is None or fin_mois is None:
            return {}
        for annee in range(int(a1), int(a2) + 1):
            premier = debut_mois if annee == int(a1) else 1
            dernier = fin_mois if annee == int(a2) else 12
            ajouter(annee, premier, dernier)
        return couverts

    trouve = AVANT.search(alinea)
    if trouve:
        _, mois, annee = trouve.groups()
        borne = MOIS.get(mois.lower())
        if borne is None:
            return {}
        for a in range(PREMIERE_GENERATION, int(annee)):
            ajouter(a, 1, 12)
        ajouter(int(annee), 1, borne - 1)
        return couverts

    trouve = A_COMPTER.search(alinea)
    if trouve:
        _, mois, annee = trouve.groups()
        borne = MOIS.get(mois.lower())
        if borne is None:
            return {}
        ajouter(int(annee), borne, 12)
        for a in range(int(annee) + 1, DERNIERE_GENERATION + 1):
            ajouter(a, 1, 12)
        return couverts

    trouve = APRES_ANNEE.search(alinea)
    if trouve:
        for a in range(int(trouve.group(1)) + 1, DERNIERE_GENERATION + 1):
            ajouter(a, 1, 12)
        return couverts

    trouve = EN_ANNEE.search(alinea)
    if trouve:
        ajouter(int(trouve.group(1)), 1, 12)
    return couverts


def generation_decimale(annee: int, mois: int) -> float:
    """Génération et mois -> clé de table. Janvier donne l'année toute nue."""
    return annee if mois == 1 else round(annee + (mois - 1) / 12.0, 3)


def _annee_mois(cle: float) -> tuple[int, int]:
    """Clé de table -> (année, mois) : ``1961.667`` -> (1961, 9)."""
    annee = int(cle)
    return annee, int(round((cle - annee) * 12.0)) + 1


def _segments(par_mois: dict[int, dict[int, float]],
              par_annee: bool = True) -> dict[float, float]:
    """Table en escalier depuis une valeur par mois.

    Un segment s'ouvre là où la valeur change. ``par_annee`` en ouvre aussi un
    à chaque janvier, même sans changement : c'est la forme des tables d'âge
    et de durée, une ligne par génération. Sans lui, seules les coupures
    restent — la forme des portes de carrière longue.
    """
    table: dict[float, float] = {}
    precedente = None
    for annee, mois in sorted(par_mois.items()):
        if par_annee:
            precedente = None
        for m in sorted(mois):
            valeur = mois[m]
            if valeur != precedente:
                table[generation_decimale(annee, m)] = valeur
                precedente = valeur
    return table


def _mois_des_segments(table: dict[float, float]) -> dict[int, dict[int, float]]:
    """L'inverse : une table en escalier rendue mois par mois.

    Un segment court jusqu'au suivant, ou jusqu'à la fin de son année : une
    version n'écrit une clé qu'aux générations qu'elle nomme, et c'est cette
    étendue-là qu'elle recouvre — pas ce qui vient après sa dernière ligne.
    Pour les tables par ANNÉE — la montée en charge de 1993, la proratisation,
    l'assiette du trimestre. Une table lue au mois ne repasse pas par ici :
    une clé de janvier ne dit pas si la version nomme l'année entière ou ses
    premiers mois seulement, et le mois le sait.
    """
    par_mois: dict[int, dict[int, float]] = {}
    cles = sorted(table)
    for cle, suivante in zip(cles, cles[1:] + [None]):
        annee, mois = _annee_mois(cle)
        fin = (annee, 13)
        if suivante is not None:
            a2, m2 = _annee_mois(suivante)
            if a2 == annee:
                fin = (annee, m2)
        for m in range(mois, fin[1]):
            par_mois.setdefault(annee, {})[m] = table[cle]
    return par_mois


def _par_version(versions: list[tuple[str, str]],
                 lire: "callable") -> dict[float, float]:
    """Applique ``lire`` version par version, la plus récente l'emportant.

    Une version d'article REMPLACE la précédente, elle ne s'y ajoute pas : les
    fusionner reviendrait à opposer à une même génération deux états du droit.
    On les parcourt donc dans l'ordre de leur DATE D'EFFET, chaque version
    écrasant, MOIS PAR MOIS, ce que la précédente disait des générations
    qu'elle nomme — et laissant intact ce dont elle ne parle pas. Au mois et
    non à l'année : la loi de 2025 réécrit l'âge des nés à compter du
    1er septembre 1961 et renvoie les autres à « la rédaction antérieure »,
    janvier-août 1961 compris. Une coupure abandonnée par un texte plus récent
    ne survit pas pour autant : le texte qui la lève nomme les mois qu'elle
    coupait, et les recouvre.
    """
    par_mois: dict[int, dict[int, float]] = {}
    ordre = sorted(versions, key=lambda v: (date_effet(v[0], v[1]), v[0]))
    for _, texte in ordre:
        lu = lire(texte)
        # ``lire`` rend soit une valeur par mois — la forme de
        # ``table_par_generation(..., mois=True)``, qui sait quels mois la
        # version nomme —, soit une table par année entière.
        couverture = (lu if any(isinstance(v, dict) for v in lu.values())
                      else _mois_des_segments(lu))
        for annee, mois in couverture.items():
            par_mois.setdefault(annee, {}).update(mois)
    return _segments(par_mois)


def table_par_generation(alineas: list[tuple[float, str]],
                         par_annee: bool = True, mois: bool = False) -> dict:
    """Valeur opposable à chaque génération, coupures comprises.

    La table était annuelle : une génération que le texte coupe en cours
    d'année — 1951 au 1er juillet, 1961 au 1er septembre — s'y voyait attribuer
    la valeur couvrant le plus de mois. L'approximation valait un trimestre
    d'âge légal, et le récupérateur la fabriquait alors qu'il avait le mois
    sous les yeux.

    Elle rend désormais un SEGMENT par valeur : la clé est l'année pour un
    segment ouvert en janvier, l'année plus la part écoulée sinon —
    ``1951.5`` pour le 1er juillet 1951. Un mois qu'aucun alinéa ne vise hérite
    du segment précédent, la lecture du modèle étant en escalier.

    À valeurs concurrentes sur un même mois — deux alinéas qui se recouvrent —
    c'est la PLUS EXIGEANTE qui l'emporte : le modèle ne prête jamais à
    personne le régime le plus favorable quand il ne sait pas trancher.

    ``mois=True`` rend la valeur mois par mois, sans la ramener en escalier :
    c'est la forme que ``_par_version`` attend pour savoir exactement quels
    mois une version recouvre.
    """
    par_mois: dict[int, dict[int, float]] = {}
    for valeur, alinea in alineas:
        for annee, couverts in _mois_couverts(alinea).items():
            cible = par_mois.setdefault(annee, {})
            for m in couverts:
                cible[m] = max(cible[m], valeur) if m in cible else valeur
    if mois:
        return par_mois
    return _segments(par_mois, par_annee)


def _alineas(texte: str) -> list[str]:
    """Découpe un article en ses alinéas numérotés, puis en phrases.

    En phrases, parce qu'un alinéa peut en porter deux qui ne parlent pas des
    mêmes générations : « Soixante-trois ans et neuf mois, pour les assurés
    nés en 1968. Pour les assurés nés avant le 1er septembre 1961, il est
    celui applicable […] dans sa rédaction antérieure » — lu d'un bloc, le
    renvoi aurait opposé 63 ans et 9 mois à tous les nés d'avant 1961.
    """
    phrases = []
    for morceau in re.split(r"\s\d{1,2}°\s*[-.]?\s*", texte):
        phrases.extend(re.split(r"(?<=[.;])\s+(?=[A-ZÀ-Ý«“])", morceau))
    return [p.strip() for p in phrases if p.strip()]


def age_ouverture(versions: list[tuple[str, str]]) -> dict[float, float]:
    """Âge d'ouverture des droits, par génération — L. 161-17-2 et D. 161-2-1-9.

    Les versions des deux articles sont lues ensemble, dans l'ordre de leur
    date d'effet : la loi ne portait que la cible et le décret la montée en
    charge jusqu'en 2025 ; depuis, la loi porte la table et le décret n'est
    plus lu que pour les générations qu'elle ne nomme pas.
    """
    def lire(texte: str) -> dict[float, float]:
        alineas = [(age_en_lettres(a), a) for a in _alineas(texte)]
        return table_par_generation(
            [(v, a) for v, a in alineas if v is not None and 55.0 <= v <= 70.0],
            mois=True)
    return _par_version(versions, lire)


def duree_requise(versions: list[tuple[str, str]]) -> dict[float, float]:
    """Durée d'assurance requise, par génération — L. 161-17-3."""
    def lire(texte: str) -> dict[float, float]:
        alineas = []
        for alinea in _alineas(texte):
            trouve = re.search(r"\b(1[5-7]\d)\s*trimestres", alinea)
            if trouve:
                alineas.append((float(trouve.group(1)), alinea))
        return table_par_generation(alineas, mois=True)
    return _par_version(versions, lire)


#: « 151 trimestres pour l'assuré né en 1934 ; 152 trimestres pour l'assuré né
#: en 1935 » — la montée en charge de la loi du 22 juillet 1993, au II de
#: l'article R. 351-45. L'article est abrogé depuis 2009 ; la base le garde.
DUREE_1993 = re.compile(
    r"(\d{3})\s*trimestres\s*pour\s*l['’]assur[ée]\s*n[ée]\s*en\s*(19[34]\d)",
    re.I)

#: Générations que ce II couvre. Il s'ouvre sur « l'assuré né AVANT le
#: 1er janvier 1934 », que le motif ci-dessus n'attrape pas — et c'est voulu :
#: le dépôt tient la table à partir de 1934.
GENERATIONS_1993 = (1934, 1942)


def duree_requise_1993(versions: list[tuple[str, str]]) -> dict[float, float]:
    """Durée requise des générations 1934-1942 — R. 351-45 II.

    `docs/limites.md` tenait ces générations pour hors de portée : « leur montée
    en charge vient de la loi du 22 juillet 1993 et de la loi du 21 août 2003,
    dont les tableaux ne sont pas des textes consolidés séparés ». La seconde
    moitié est vraie et la conclusion fausse : le tableau de 1993 n'est pas un
    texte séparé, il est CODIFIÉ — à l'article R. 351-45, une disposition
    transitoire que la base garde bien qu'elle soit abrogée depuis 2009.

    **CE QUE L'ARTICLE DIT DE PLUS QUE LE DÉPÔT.** Son II ne s'applique qu'aux
    « pensions prenant effet avant le 1er janvier 2003 » ; son I porte 160
    trimestres au-delà de cette date, « quelle que soit la date de naissance ».
    Le dépôt, lui, indexe la durée sur la seule génération. Les deux lectures ne
    se séparent que pour un assuré de ces générations qui aurait liquidé après
    2002 — donc à plus de soixante ans, à une époque où l'âge légal en était
    soixante. C'est écrit ici parce que l'écart existe, non parce qu'il pèse.
    """
    def lire(texte: str) -> dict[float, float]:
        table: dict[float, float] = {}
        for trimestres, generation in DUREE_1993.findall(texte):
            annee = int(generation)
            if GENERATIONS_1993[0] <= annee <= GENERATIONS_1993[1]:
                table[annee] = float(trimestres)
        return table
    return _par_version(versions, lire)


def coefficient_minoration(versions: list[tuple[str, str]]) -> dict[float, float]:
    """Coefficient de minoration, par génération — R. 351-27 II.

    L'article n'écrit pas ses alinéas en numéros mais en phrases séparées par
    des points-virgules, et il ne parle pas des « assurés nés » mais de
    « l'assuré né » : le découpage lui est propre.

    Les versions en vigueur depuis le 1er janvier 2026 n'ont plus de II — le
    décret n° 2025-1409 l'a abrogé, et l'article ne dit plus que « 1,25 % ».
    Elles ne nomment donc aucune génération et ne recouvrent rien : la table
    reste celle de la dernière version qui les nommait, ce qui est exactement
    ce que ces générations-là — toutes au-delà de l'âge du taux plein
    d'office — se sont vu opposer.
    """
    def lire(texte: str) -> dict[float, float]:
        partie = texte.split("II.-", 1)
        if len(partie) < 2:
            return {}
        alineas = []
        for alinea in partie[1].split(";"):
            trouve = re.search(r"(\d[,.]\d+|\d)\s*%", alinea)
            if trouve is None:
                continue
            valeur = float(trouve.group(1).replace(",", "."))
            if 1.0 <= valeur <= 3.0:
                alineas.append((valeur / 100.0, alinea))
        return table_par_generation(alineas, mois=True)
    return _par_version(versions, lire)


#: « A soixante-deux pour les assurés qui ont débuté leur activité avant l'âge
#: de vingt ans » — le décret de 2023 a perdu le mot « ans » à son 3°. On
#: tolère l'omission plutôt que de manquer une porte.
PORTE = re.compile(
    r"\b[Aaà]\s+((?:cinquante|soixante)(?:[- ](?:et[- ])?"
    r"(?:un|deux|trois|quatre|cinq|six|sept|huit|neuf))?)"
    r"(?:\s*ans?)?(?:\s*et\s*(un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze)"
    r"\s*mois)?[^;]*?"
    r"avant\s+l['’]?\s*âge\s+de\s+((?:seize|dix-sept|dix-huit|dix-neuf|vingt|"
    r"vingt[- ]et[- ]un))\s*ans",
    re.I)

#: Ce que le II de D. 351-1-1 cite entre guillemets : le texte remplacé, puis
#: le ou les textes de remplacement.
CITATION = re.compile(r"[“«\"]\s*([^”»\"]+?)\s*[”»\"]")

#: « l'âge prévu à l'article L. 161-17-2 minoré de deux ans et six mois ».
MINORE = re.compile(
    r"minor[ée]e?\s+de\s+(\w+)\s+ans?(?:\s+et\s+(\w+)\s+mois)?", re.I)

#: « Les dispositions du 3° du I s'appliquent aux assurés nés … » — laquelle
#: des portes le II adapte.
PORTE_ADAPTEE = re.compile(r"du\s+(\d)°\s+du\s+I\b", re.I)

#: Une version dont la base ne porte pas la note d'application, et dont le
#: décret la fixe pourtant : le décret n° 2003-1036 du 30 octobre 2003, qui
#: crée l'article, « est applicable aux pensions prenant effet postérieurement
#: au 31 décembre 2003 » (article 7, JORFARTI000001667141). La clé est la date
#: de début de la version dans la base.
EFFET_CONNU = {"2003-10-31": "2004-01-01"}

#: « I. ― Pour les assurés nés avant le 1er juillet 1951 : », « B.-Pour les
#: assurés nés en 1953 : » — les rédactions de 2011 et de 2012 groupent les
#: portes par génération sous de tels en-têtes.
EN_TETE = re.compile(r"Pour les assur[ée]s n[ée]s[^:]{0,120}?:", re.I)


def _age_cite(texte: str) -> float | None:
    """« soixante », « soixante ans et six mois », « soixante-et-un ans et neuf
    mois » -> années décimales. ``None`` si ce n'est pas un âge en lettres."""
    trouve = re.match(
        r"^([a-zéè\- ]+?)\s*(?:ans?)?(?:\s*et\s+(\w+)\s+mois)?\s*$",
        texte.strip().lower())
    if trouve is None:
        return None
    annees = nombre_en_lettres(trouve.group(1))
    mois = nombre_en_lettres(trouve.group(2))
    if annees is None or mois is None or not 50 <= annees <= 70:
        return None
    return round(annees + mois / 12.0, 2)


def _adaptations(partie: str, age_general: float, age_debut: int,
                 ages: dict[int, dict[int, float]]) -> dict[float, float]:
    """La borne des vingt ans par génération, résolue depuis le II.

    Chaque alinéa nomme une ou deux périodes de naissance et ce qui remplace
    « soixante-deux ans » pour elles : un âge en lettres, ou l'âge légal
    « minoré de deux ans et six mois », que l'on résout mois par mois contre
    la table d'âge en vigueur à la date d'effet de la version. Après la
    dernière génération que le II adapte, la règle générale reprend, et la
    table le dit d'une ligne.
    """
    del age_debut  # la porte adaptée est identifiée par l'appelant
    par_mois: dict[int, dict[int, float]] = {}
    # Le chapeau cite « le 3° du I » : on ne coupe qu'aux numéros qui ouvrent
    # une adaptation, « 1° Pour les assurés nés … ».
    morceaux = re.split(r"\s\d°\s(?=Pour\b)", partie)
    chapeau, alineas = morceaux[0], morceaux[1:]
    for alinea in alineas:
        remplacements = CITATION.findall(alinea)[1:]
        periodes = [_mois_couverts(m.group(0)) for m in MENTION.finditer(alinea)]
        periodes = [p for p in periodes if p]
        if not remplacements or not periodes:
            continue
        if len(remplacements) == 1:
            remplacements = remplacements * len(periodes)
        if len(remplacements) != len(periodes):
            continue
        for periode, remplacement in zip(periodes, remplacements):
            fixe = _age_cite(remplacement)
            minore = MINORE.search(remplacement)
            for annee, mois in periode.items():
                for m in mois:
                    if fixe is not None:
                        valeur = fixe
                    elif minore and annee in ages and m in ages[annee]:
                        offset = (nombre_en_lettres(minore.group(1)) or 0) \
                            + (nombre_en_lettres(minore.group(2)) or 0) / 12.0
                        valeur = round(ages[annee][m] - offset, 2)
                    else:
                        continue
                    par_mois.setdefault(annee, {})[m] = valeur
    # La règle générale reprend le mois qui suit la dernière génération adaptée.
    couverture = _mois_couverts(chapeau)
    if couverture and par_mois:
        annee = max(couverture)
        mois = max(couverture[annee])
        annee, mois = (annee + 1, 1) if mois == 12 else (annee, mois + 1)
        if annee <= DERNIERE_GENERATION:
            par_mois.setdefault(annee, {})[mois] = age_general
    return _segments(par_mois, par_annee=False)


def _supplement(item: str, chapeau: int) -> int:
    """Trimestres cotisés exigés au-delà de la durée requise, pour une porte.

    Le chapeau de l'article majore la durée requise (« majorée de huit
    trimestres ») ; chaque porte y renvoie (« la durée minimale mentionnée au
    premier alinéa »), la minore (« minorée de quatre trimestres »), porte sa
    propre majoration (2012 : « majorée de huit trimestres » dans la porte),
    ou demande la durée requise nue (« la limite fixée en application du
    deuxième alinéa », « celle prévue au deuxième alinéa »).
    """
    minoree = re.search(r"minor[ée]e?\s+de\s+(\w+)\s+trimestres", item, re.I)
    if minoree:
        return max(0, chapeau - (nombre_en_lettres(minoree.group(1)) or 0))
    majoree = re.search(r"major[ée]e?\s+de\s+(\w+)\s+trimestres", item, re.I)
    if majoree:
        return nombre_en_lettres(majoree.group(1)) or 0
    if re.search(r"limite fixée en application|prévue au deuxième alinéa", item, re.I):
        return 0
    return chapeau


def _portes(texte: str, effet: str) -> list[dict]:
    """Les portes qu'une version écrit en toutes lettres, avec leur génération.

    Le texte est coupé en blocs par génération là où il en a — « Pour les
    assurés nés en 1953 : » — et ce qui précède le premier bloc, ou le II,
    est la règle générale (génération ``1900``). Dans chaque bloc, chaque
    point-virgule sépare une porte : un âge de départ, un âge de début
    d'activité, un supplément de trimestres. Les blocs qui n'écrivent pas de
    porte — les substitutions de 2023 — ne rendent rien ici.
    """
    general = re.split(r"\sII\s*\.?\s*[-―]", texte, maxsplit=1)[0]
    chapeau = re.split(r"\s1°\s", general, maxsplit=1)[0]
    chapeau = EN_TETE.split(chapeau, maxsplit=1)[0]
    trouve = re.search(r"major[ée]e?\s+de\s+(\w+)\s+trimestres", chapeau, re.I)
    supplement_chapeau = (nombre_en_lettres(trouve.group(1)) or 0) if trouve else 0

    blocs: list[tuple[float, str]] = []
    en_tetes = list(EN_TETE.finditer(texte))
    premier = en_tetes[0].start() if en_tetes else len(texte)
    blocs.append((PREMIERE_GENERATION, general[:min(len(general), premier)]))
    for rang, en_tete in enumerate(en_tetes):
        fin = en_tetes[rang + 1].start() if rang + 1 < len(en_tetes) else len(texte)
        couverture = _mois_couverts(en_tete.group(0))
        if not couverture:
            continue
        annee = min(couverture)
        blocs.append((generation_decimale(annee, min(couverture[annee])),
                      texte[en_tete.end():fin]))

    portes: list[dict] = []
    for generation, bloc in blocs:
        # Un point-virgule sépare les portes — sauf dans le décret de 2010,
        # dont le 3° finit sur un point avant le 4°.
        for item in re.split(r";|\.\s+(?=\d°\s)", bloc):
            trouve = PORTE.search(item)
            if trouve is None:
                continue
            annees = nombre_en_lettres(trouve.group(1))
            mois = nombre_en_lettres(trouve.group(2))
            age_debut = nombre_en_lettres(trouve.group(3))
            if annees is None or mois is None or age_debut is None:
                continue
            portes.append({
                "entree_en_vigueur": effet,
                "generation": generation,
                "age_debut_maximum": age_debut,
                "age_depart": round(annees + mois / 12.0, 2),
                "trimestres_supplementaires": _supplement(item, supplement_chapeau),
            })
    return portes


def carriere_longue(versions: list[tuple[str, str]],
                    versions_age: list[tuple[str, str]] | None = None) -> list[dict]:
    """Portes du départ anticipé — D. 351-1-1, version par version.

    Chaque porte associe un âge de départ à un âge de début d'activité : « A
    cinquante-huit ans pour les assurés […] ayant débuté leur activité avant
    l'âge de seize ans ». La condition de durée cotisée se lit dans le chapeau,
    en trimestres ajoutés à la durée requise, ou dans la porte elle-même.

    Quatre rédactions se succèdent, et le script les lit toutes. 2003 : trois
    portes, sans génération. 2011 (loi du 9 novembre 2010) et 2012 (décret du
    2 juillet 2012) : les portes sont groupées par génération sous des
    en-têtes « Pour les assurés nés en 1953 : », et la règle générale de 2012
    — soixante ans pour qui a débuté avant vingt ans — précède le II. Depuis
    2023 : un I de règle générale, un II qui adapte la borne des vingt ans
    génération par génération PAR SUBSTITUTION (voir ``_adaptations``),
    résolue contre la table d'âge en vigueur à la date d'effet de la version
    — c'est pour cela qu'il faut ``versions_age``, celles de L. 161-17-2 et
    D. 161-2-1-9. Une version qui ne change aucune porte — le décret
    n° 2025-1410, qui réécrit le I sans en changer une valeur — n'ouvre pas
    de date d'effet : la table est indexée sur les dates où quelque chose
    change.
    """
    portes: list[dict] = []
    precedentes: list[tuple] | None = None
    ordre = sorted(versions, key=lambda v: (date_effet(v[0], v[1]), v[0]))
    for date_debut, texte in ordre:
        effet = EFFET_CONNU.get(date_debut) or date_effet(date_debut, texte)
        lignes = _portes(texte, effet)
        morceaux = re.split(r"\sII\s*\.?\s*[-―]", texte, maxsplit=1)
        if len(morceaux) > 1 and versions_age:
            adaptee = PORTE_ADAPTEE.search(morceaux[1])
            rang = int(adaptee.group(1)) - 1 if adaptee else -1
            generales = [l for l in lignes if l["generation"] == PREMIERE_GENERATION]
            if 0 <= rang < len(generales):
                porte = generales[rang]
                ages = _mois_des_segments(age_ouverture(
                    [v for v in versions_age if date_effet(v[0], v[1]) <= effet]))
                for generation, age in _adaptations(
                        morceaux[1], porte["age_depart"],
                        porte["age_debut_maximum"], ages).items():
                    lignes.append({
                        "entree_en_vigueur": effet,
                        "generation": generation,
                        "age_debut_maximum": porte["age_debut_maximum"],
                        "age_depart": age,
                        "trimestres_supplementaires": porte["trimestres_supplementaires"],
                    })
        empreinte = [tuple(sorted((k, v) for k, v in l.items()
                                  if k != "entree_en_vigueur")) for l in lignes]
        if not lignes or empreinte == precedentes:
            continue
        precedentes = empreinte
        portes.extend(lignes)
    return portes


#: « 152 trimestres pour les assurés nés en 1944 », « 150 trimestres pour les
#: assurés nés avant 1944 » — la table de proratisation de l'article R. 351-6.
PRORATISATION = re.compile(
    r"(\d{3})\s+trimestres\s+pour\s+les\s+assur[ée]s\s+n[ée]s\s+"
    r"(avant|en)\s+(\d{4})",
    re.I)

#: « sur la base de 200 heures » — l'assiette d'un trimestre, à l'article
#: R. 351-9. L'alinéa qui la porte dit sur quelle période elle vaut, de deux
#: façons : « comprise entre le 1er janvier 1972 et le 31 décembre 2013 » ou
#: « postérieure au 31 décembre 2013 ».
ASSIETTE = re.compile(r"sur\s+la\s+base\s+de\s+(\d{2,3})\s+heures", re.I)
PERIODE_ENTRE = re.compile(r"comprise\s+entre\s+le\s+1er\s+janvier\s+(\d{4})", re.I)
PERIODE_APRES = re.compile(r"post[ée]rieure\s+au\s+31\s+d[ée]cembre\s+(\d{4})", re.I)


def duree_proratisation(versions: list[tuple[str, str]]) -> dict[int, float]:
    """Durée maximale d'assurance prise en compte par la proratisation.

    C'est le DÉNOMINATEUR du rapport qui réduit la pension d'une carrière
    incomplète, et la loi du 22 juillet 1993 l'a fait monter de 150 à 160
    trimestres pour les seules générations 1944 à 1948 — deux trimestres par
    génération, quand la durée REQUISE, elle, montait de dix trimestres sur
    dix générations. Confondre les deux retire 2,5 % de pension à un assuré né
    en 1945 qui a validé 156 trimestres.

    L'article s'arrête à la génération 1947 et renvoie, au-delà, à la durée du
    troisième alinéa de l'article L. 351-1 : la table du dépôt porte donc une
    dernière ligne, pour 1948, que cet article-ci ne fixe pas et que la
    certification ne touche pas.

    Les rédactions antérieures à 2004 ne portaient pas de table par génération
    mais une durée unique, et ne nomment donc aucune génération. Celle du
    1er janvier 2026 (décret n° 2025-1409, article 2, 21°) SUPPRIME le II :
    ces générations ont toutes plus de soixante-dix-huit ans, et le texte était
    mort. La base le consolide en tronquant la table plutôt qu'en l'effaçant ;
    lue version par version, chacune ne recouvrant que les générations qu'elle
    nomme, la table reste ce que ces générations se sont vu opposer.
    """
    def lire(texte: str) -> dict[float, float]:
        table: dict[float, float] = {}
        for trimestres, portee, generation in PRORATISATION.findall(texte):
            debut = PREMIERE_GENERATION if portee.lower() == "avant" else int(generation)
            table[debut] = float(trimestres)
        return table
    return _par_version(versions, lire)


def heures_par_trimestre(versions: list[tuple[str, str]]) -> dict[int, float]:
    """Heures de SMIC qu'il faut avoir cotisé pour valider un trimestre.

    Un trimestre d'assurance ne s'acquiert pas par le temps passé mais par un
    montant cotisé, que l'article exprime en multiples du SMIC horaire de
    l'année : 200 heures depuis 1972, 150 depuis 2014 — l'abaissement destiné
    aux temps très partiels et aux carrières hachées.

    Chaque alinéa porte sa période, et la clé est l'année où elle s'ouvre : une
    période « postérieure au 31 décembre 2013 » commence en 2014. Lu version
    par version, chacune ne recouvrant que les périodes qu'elle nomme : le
    décret n° 2025-1409 (article 2, 24°) supprime au 1er janvier 2026 les
    alinéas des périodes closes, que la base ne consolide pas tous.
    """
    def lire(texte: str) -> dict[float, float]:
        table: dict[float, float] = {}
        for alinea in re.split(r"(?=Pour la période)", texte):
            heures = ASSIETTE.search(alinea)
            if heures is None:
                continue
            entre = PERIODE_ENTRE.search(alinea)
            apres = PERIODE_APRES.search(alinea)
            if entre is not None:
                table[int(entre.group(1))] = float(heures.group(1))
            elif apres is not None:
                table[int(apres.group(1)) + 1] = float(heures.group(1))
        return table
    return _par_version(versions, lire)


#: « Vingt et une années pour l'assuré né en 1944 », « Dix années pour l'assuré
#: né avant le 1er janvier 1934 » — la table du salaire de référence.
ANNEES_RETENUES = re.compile(
    r"([\w-]+(?:\s+et\s+[\w-]+)?)\s+ann[ée]es?\s+pour\s+l['’]assur[ée]\s+n[ée]\s+"
    r"(?:en\s+(\d{4})|avant\s+le\s+\d{1,2}e?r?\s+\w+\s+(\d{4}))",
    re.I)

#: « Les durées de vingt-cinq années fixées aux premier et troisième alinéas de
#: l'article R. 351-29 sont applicables aux assurés nés après 1947 » — la cible,
#: et la génération à partir de laquelle elle vaut. Le point qui sépare les deux
#: moitiés de la phrase n'en est pas un : « R. 351-29 » en porte un.
ANNEES_CIBLE = re.compile(
    r"dur[ée]es?\s+de\s+([\w-]+(?:\s+et\s+[\w-]+)?)\s+ann[ée]es?"
    r".{0,200}?assur[ée]s\s+n[ée]s\s+apr[èe]s\s+(\d{4})",
    re.I)


def annees_salaire_reference(versions: list[tuple[str, str]]) -> dict[int, float]:
    """Nombre d'années retenues au salaire annuel moyen, par génération.

    La loi du 22 juillet 1993 fait passer le salaire de référence des dix aux
    vingt-cinq meilleures années, à raison d'une année par génération de 1934 à
    1948, et l'article l'écrit en toutes lettres. Le paramètre se lit à l'ANNÉE
    DE NAISSANCE : le lire à l'année de liquidation opposait vingt-cinq années à
    des générations auxquelles la loi n'en a jamais opposé plus de dix, et
    minorait leur pension d'autant — étendre une moyenne aux années les plus
    faibles ne peut que l'abaisser.

    Le II donne les générations 1934 à 1947 et le plancher d'avant 1934 ; le I
    donne la cible et la première génération qu'elle vise, « nés après 1947 ».

    L'article est abrogé depuis le 1er janvier 2026 (décret n° 2025-1409), la
    règle étant passée à l'article R. 173-3-2 avec les vingt-quatre et
    vingt-trois années des parents : sa dernière version reste la table.
    """
    table: dict[int, float] = {}
    for _, texte in sorted(versions)[-1:]:
        for lettres, en_annee, avant_annee in ANNEES_RETENUES.findall(texte):
            annees = nombre_en_lettres(lettres)
            if annees is None:
                continue
            generation = int(en_annee) if en_annee else PREMIERE_GENERATION
            table[generation] = float(annees)
        cible = ANNEES_CIBLE.search(texte)
        if cible is not None:
            annees = nombre_en_lettres(cible.group(1))
            if annees is not None:
                table[int(cible.group(2)) + 1] = float(annees)
    return table


# ---------------------------------------------------------------------------
# Lecture de l'index
# ---------------------------------------------------------------------------


def depouiller_index(chemin: Path) -> tuple[dict[str, list[tuple[str, str]]], str]:
    """Versions datées de chaque article, lues dans l'index du dépôt.

    L'index (`dila_index.py legi`) est le dump global plus tous les incréments
    quotidiens parus depuis : c'est la seule voie qui connaisse un texte
    postérieur à juillet 2025 tant que la DILA ne régénère pas son dump. Sa
    table ``meta`` dit jusqu'où il est à jour, et la source écrite dans le
    fichier de sortie le répète : une certification l'est à une date.
    """
    if not chemin.exists():
        raise FileNotFoundError(
            f"{chemin} absent : lancer `python scripts/fetch/dila_index.py legi "
            "--recuperer`, puis `--mettre-a-jour`")
    db = sqlite3.connect(chemin)
    meta = dict(db.execute("SELECT cle, valeur FROM meta"))
    trouvees: dict[str, list[tuple[str, str]]] = {}
    for article, code in ARTICLES.items():
        trouvees[article] = [
            (debut, texte) for debut, texte in db.execute(
                "SELECT date, texte FROM doc WHERE num = ? AND titre LIKE ? "
                "ORDER BY date", (article, f"%{code}%"))
        ]
    db.close()
    source = (f"index LEGI du dépôt : {meta.get('dump', '?')}, incréments "
              f"appliqués jusqu'au {meta.get('dernier_increment', '?')}")
    return trouvees, source


# ---------------------------------------------------------------------------
# Lecture du dump
# ---------------------------------------------------------------------------

FILTRE = r"""
import re, sys
CIBLE = re.compile(r"<NUM>\s*(%s)\s*</NUM>")
BALISES = re.compile(r"<[^>]+>")
tampon = ""
for bloc in iter(lambda: sys.stdin.buffer.read(1 << 20), b""):
    tampon += bloc.decode("utf-8", errors="replace")
    morceaux = tampon.split("<?xml")
    tampon = morceaux.pop()
    for morceau in morceaux:
        trouve = CIBLE.search(morceau)
        if not trouve:
            continue
        debut = re.search(r"<DATE_DEBUT>(.*?)</DATE_DEBUT>", morceau)
        texte = re.sub(r"\s+", " ", BALISES.sub(" ", morceau)).strip()
        print("@@@ %%s %%s" %% (trouve.group(1), debut.group(1) if debut else "?"))
        print(texte[:12000])
        sys.stdout.flush()
"""


class TransfertIncomplet(RuntimeError):
    """Le dump n'a pas été téléchargé en entier."""


def dernier_dump() -> str:
    with urllib.request.urlopen(RACINE, timeout=120) as reponse:
        page = reponse.read().decode("utf-8", errors="replace")
    noms = sorted(set(re.findall(r'href="(Freemium_legi_global_[^"]+\.tar\.gz)"', page)))
    if not noms:
        raise LookupError("aucun dump global dans le répertoire LEGI de la DILA")
    return RACINE + noms[-1]


def depouiller(url: str) -> dict[str, list[tuple[str, str]]]:
    """Versions datées de chaque article, filtrées sur le code qui le porte."""
    motif = "|".join(re.escape(a) for a in ARTICLES)
    lecture = subprocess.Popen(
        ["curl", "-sS", "--max-time", "7200", url], stdout=subprocess.PIPE
    )
    detar = subprocess.Popen(["tar", "-xzO"], stdin=lecture.stdout,
                             stdout=subprocess.PIPE)
    lecture.stdout.close()
    filtre = subprocess.Popen([sys.executable, "-X", "utf8", "-c", FILTRE % motif],
                              stdin=detar.stdout, stdout=subprocess.PIPE)
    detar.stdout.close()

    trouvees: dict[str, list[tuple[str, str]]] = {a: [] for a in ARTICLES}
    article = debut = None
    for brut in filtre.stdout:
        ligne = brut.decode("utf-8", errors="replace").rstrip("\n")
        if ligne.startswith("@@@ "):
            _, article, debut = ligne.split(" ", 2)
            continue
        if article is None:
            continue
        code = re.search(r"AUTONOME (Code [^A-Z]*?) (Partie|Livre|Titre)", ligne)
        if code and ARTICLES[article] in code.group(1):
            trouvees[article].append((debut, ligne))
        article = None
    filtre.wait()
    # Un transfert coupé ne se voit pas dans ce qui a été lu : le dépouillement
    # rend moins de versions, et les garde-fous les trouvent bonnes — un dump à
    # moitié lu n'a pas de trou, il a une fin prématurée.
    if lecture.wait() != 0:
        raise TransfertIncomplet(
            f"curl s'est interrompu (code {lecture.returncode}) : le dump n'a "
            "pas été lu en entier")
    return trouvees


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--dump", action="store_true",
                           help="lire le dump global de la DILA (1,1 Go) au lieu de l'index")
    analyseur.add_argument("--index", type=Path, default=INDEX,
                           help=f"chemin de l'index LEGI (défaut : {INDEX})")
    options = analyseur.parse_args(arguments)

    if options.dump:
        try:
            url = dernier_dump()
        except (urllib.error.HTTPError, urllib.error.URLError, LookupError) as erreur:
            print(f"Base LEGI indisponible : {erreur}", file=sys.stderr)
            return 1
        print(f"Dump    {url}")
        print("Lecture en flux d'environ 9 Go décompressés : comptez un quart d'heure.\n")
        try:
            versions = depouiller(url)
        except TransfertIncomplet as erreur:
            print(f"\nÉCHEC   {erreur}", file=sys.stderr)
            return 1
        source = url
    else:
        try:
            versions, source = depouiller_index(options.index)
        except FileNotFoundError as erreur:
            print(f"ÉCHEC   {erreur}", file=sys.stderr)
            return 1
        print(f"Source  {source}\n")
    for article, trouvees in versions.items():
        vigueur = max((debut for debut, _ in trouvees), default="-")
        print(f"  {article:12} {len(trouvees):3} version(s) au {ARTICLES[article]},"
              f" la dernière du {vigueur}")
    if not all(versions.values()):
        print("\nÉCHEC   un article n'a pas été trouvé", file=sys.stderr)
        return 1

    versions_age = versions["L161-17-2"] + versions["D161-2-1-9"]
    tables = {
        "age_ouverture": age_ouverture(versions_age),
        "duree_requise": duree_requise(versions["L161-17-3"]),
        "duree_requise_1993": duree_requise_1993(versions["R351-45"]),
        "coefficient_minoration": coefficient_minoration(versions["R351-27"]),
        "carriere_longue": carriere_longue(versions["D351-1-1"], versions_age),
        "duree_proratisation": duree_proratisation(versions["R351-6"]),
        "heures_par_trimestre": heures_par_trimestre(versions["R351-9"]),
        "annees_salaire_reference": annees_salaire_reference(versions["R351-29-1"]),
    }

    # Garde-fous : une table lue de travers ne doit pas s'écrire en silence.
    ages = tables["age_ouverture"]
    if not (ages and min(ages.values()) >= 60.0 and max(ages.values()) == 64.0):
        print(f"\nÉCHEC   âges d'ouverture invraisemblables : "
              f"{sorted(set(ages.values()))}", file=sys.stderr)
        return 1
    durees = tables["duree_requise"]
    if not (durees and max(durees.values()) == 172.0):
        print(f"\nÉCHEC   durées requises invraisemblables : "
              f"{sorted(set(durees.values()))}", file=sys.stderr)
        return 1
    coefficients = tables["coefficient_minoration"]
    if not (coefficients and max(coefficients.values()) == 0.025
            and min(coefficients.values()) == 0.0125):
        print(f"\nÉCHEC   coefficients invraisemblables : "
              f"{sorted(set(coefficients.values()))}", file=sys.stderr)
        return 1
    portes = tables["carriere_longue"]
    generales = {p["age_debut_maximum"] for p in portes if p["generation"] == PREMIERE_GENERATION}
    if not {16, 18, 20, 21} <= generales:
        print(f"\nÉCHEC   portes de carrière longue invraisemblables : "
              f"{sorted(generales)}", file=sys.stderr)
        return 1

    # La montée en charge de 1993 : un trimestre par génération, de 151 à 159.
    # Une table qui ne serait pas cette suite-là est lue de travers.
    montee = tables["duree_requise_1993"]
    attendue = {annee: 151.0 + annee - 1934
                for annee in range(GENERATIONS_1993[0], GENERATIONS_1993[1] + 1)}
    if montee != attendue:
        print(f"\nÉCHEC   montée en charge de 1993 invraisemblable : "
              f"{sorted(montee.items())}", file=sys.stderr)
        return 1

    proratisation = tables["duree_proratisation"]
    if not (proratisation and min(proratisation.values()) == 150.0
            and max(proratisation.values()) == 158.0):
        print(f"\nÉCHEC   durées de proratisation invraisemblables : "
              f"{sorted(set(proratisation.values()))}", file=sys.stderr)
        return 1
    annees_salaire = tables["annees_salaire_reference"]
    if not (annees_salaire and min(annees_salaire.values()) == 10.0
            and max(annees_salaire.values()) == 25.0):
        print(f"\nÉCHEC   années du salaire de référence invraisemblables : "
              f"{sorted(set(annees_salaire.values()))}", file=sys.stderr)
        return 1
    heures = tables["heures_par_trimestre"]
    if sorted(heures.items()) != [(1972, 200.0), (2014, 150.0)]:
        print(f"\nÉCHEC   assiette du trimestre invraisemblable : "
              f"{sorted(heures.items())}", file=sys.stderr)
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": source,
            "articles": ARTICLES,
            "recupere_le": date.today().isoformat(),
            "note": "tables par génération lues dans le texte des articles, "
                    "chaque version s'appliquant à sa date d'effet aux mois de "
                    "naissance qu'elle nomme ; une génération coupée en cours "
                    "d'année est rendue en deux segments — la clé porte alors "
                    "le mois de la coupure, 1951.5 pour le 1er juillet 1951 — "
                    "et deux alinéas qui se recouvrent sont départagés par la "
                    "valeur la plus exigeante ; les portes de carrière longue "
                    "portent la génération (1900 : règle générale) et la date "
                    "d'effet de la version qui les fixe",
            "serie": {
                f"{nom}|{cle}": valeur
                for nom in ("age_ouverture", "duree_requise",
                            "duree_requise_1993",
                            "coefficient_minoration", "duree_proratisation",
                            "heures_par_trimestre", "annees_salaire_reference")
                for cle, valeur in tables[nom].items()
            },
            "carriere_longue": portes,
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    dates_portes = sorted({p["entree_en_vigueur"] for p in portes})
    print(f"\nÂge d'ouverture        {len(ages)} segments, "
          f"{min(ages.values()):g} -> {max(ages.values()):g} ans")
    print(f"Durée requise          {len(durees)} segments, "
          f"{min(durees.values()):g} -> {max(durees.values()):g} trimestres")
    print(f"Coefficient minoration {len(coefficients)} segments, "
          f"{max(coefficients.values()):.3%} -> {min(coefficients.values()):.3%}")
    print(f"Carrière longue        {len(portes)} portes, "
          f"aux dates d'effet {', '.join(dates_portes)}")
    print(f"Montée en charge 1993  {len(montee)} générations, "
          f"{min(montee.values()):g} -> {max(montee.values()):g} trimestres")
    print(f"Durée proratisation    {len(proratisation)} segments, "
          f"{min(proratisation.values()):g} -> {max(proratisation.values()):g} "
          f"trimestres")
    print(f"Années salaire réf.    {len(annees_salaire)} générations, "
          f"{min(annees_salaire.values()):g} -> {max(annees_salaire.values()):g} années")
    print(f"Assiette du trimestre  "
          + ", ".join(f"{heure:g} heures depuis {annee}"
                      for annee, heure in sorted(heures.items())))
    print(f"Écrit dans {SORTIE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
