#!/usr/bin/env python3
"""Taux de cotisation vieillesse du régime général et des salariés agricoles.

    python scripts/fetch/dila_legi_taux_cotisation.py

Ce qu'il referme. Le compte notionnel ne connaît que la cotisation : avec le
salaire, c'est la seule grandeur qui détermine le capital accumulé, et une
erreur de deux points sur quarante ans déplace la pension d'autant. Or cette
série était la moins tenue du dépôt au regard de ce qu'elle porte — transcrite
d'OpenFisca-France, plafonnée au niveau ``haute``, et saisie avant 1967. Le taux
n'est pourtant pas une statistique : c'est un article de code, dont la base LEGI
garde les rédactions successives, exactement comme la retenue de la CNRACL.

DEUX ARTICLES PAR RÉGIME, ET ILS SE SUIVENT DANS LE TEMPS

* **Régime général** — l'article 2 du décret n° 81-1013 du 13 novembre 1981
  jusqu'à la codification, puis l'article **D. 242-4** du code de la sécurité
  sociale depuis le 21 décembre 1985 ;
* **Salariés agricoles** — l'article 2 du décret n° 50-444 du 20 avril 1950
  jusqu'à la recodification du code rural, puis l'article **D. 741-35** du code
  rural et de la pêche maritime depuis le 22 avril 2005.

TROIS ÉCRITURES POUR UNE MÊME GRANDEUR

* **la phrase**, qui est la plus ancienne et la plus longue en vigueur :

      « Le taux de la cotisation d'assurance vieillesse est fixé à 16,45 %,
        soit 8,20 % à la charge de l'employeur et 6,55 % à la charge du salarié
        […] dans la limite du plafond […], et, sur la totalité des rémunérations
        ou gains perçus par l'intéressé, 1,60 % à la charge de l'employeur et
        0,1 % à la charge du salarié. »

  Les quatre composantes y sont nommées, et le total annoncé en tête les
  recoupe : le récupérateur refait cette addition et signale l'écart ;

* **le tableau**, depuis le décret du 2 juillet 2012, qui date ses lignes
  lui-même — « Du 1er janvier au 31 décembre 2014 », « A compter du 1er janvier
  2017 » — et porte donc plusieurs années dans une seule version ;

* **le renvoi** : depuis le 1er janvier 2014, le II de l'article D. 741-35
  dispose que le taux des salariés agricoles « est fixé selon les dispositions
  prévues à l'article D. 242-4 du code de la sécurité sociale ». Le récupérateur
  le suit au lieu de recopier, et c'est ce renvoi — non une convention du dépôt —
  qui aligne les deux régimes à partir de cette date.

LA RÈGLE DE DATE EST CELLE DU DÉPÔT : le taux retenu pour une année est celui en
vigueur au **1er janvier**. Une version qui prend effet le 30 juillet ne
commande donc que l'année suivante, et c'est ce qui sépare cette lecture de la
transcription qu'elle remplace : OpenFisca date chaque taux au jour de son
entrée en vigueur, mais la série annuelle qu'en tirait le dépôt retenait le
dernier taux de l'année civile et non le premier.

CE QUE LA BASE NE PERMET PAS DE DATER, ET COMMENT ELLE LE DIT ELLE-MÊME

Avant 1982 pour le régime général, la chaîne s'arrête, et pas faute d'article :
l'article 3 du décret n° 67-803 du 20 septembre 1967 est bien dans la base, avec
les quatre composantes en toutes lettres. Mais il n'y a qu'**une** version,
datée du 1er octobre 1967 et valable jusqu'au 14 novembre 1981 — quatorze ans
sans coupure, portant 12,9 %, c'est-à-dire l'état de 1979. Le taux valait 8,5 %
en 1967 : la base a gardé la photographie finale, pas le film. C'est la leçon de
la CNRACL, et le récupérateur ne s'y fie pas sur parole — il LIT cet article
comme les autres et le refuse par une règle écrite, ``SEUIL_VERSION_UNIQUE`` :
un article qui n'a qu'une version et qui couvre plus de dix ans n'a pas de
chronologie. Les décrets modificatifs existent pourtant au *Journal officiel* —
73-1209, 75-1273, 76-894, 78-1213 — mais la base JORF n'en garde avant 1990 que
la notice, et aucune de ces notices n'écrit de taux. Ces quinze années restent
donc transcrites d'OpenFisca, au niveau ``haute``, et `docs/limites.md` le dit.

UN TAUX QUI N'EST PAS DANS L'ARTICLE, ET LE GARDE-FOU QUI L'A TROUVÉ

L'article ne dit pas tout. Du 1er juillet 1987 au 30 juin 1988, le décret
n° 87-453 du 29 juin 1987 a relevé « à titre exceptionnel et temporaire » la
cotisation salariale de 0,2 point **sans réécrire l'article D. 242-4**, que le
décret du 22 juin 1988 n'a rattrapé qu'en pérennisant la hausse. Lire la seule
chaîne des versions donnerait donc 6,40 % au 1er janvier 1988 là où le *Journal
officiel* dit 6,60 %. Ce décret est déclaré dans ``HORS_CODE`` ; le récupérateur
relit sa notice à chaque exécution, vérifie qu'elle porte bien la période et le
taux annoncés, et exige la **corroboration** : la première version postérieure à
l'ouverture de la fenêtre — celle de la pérennisation — doit porter exactement le
taux surchargé, faute de quoi la surcharge n'est pas appliquée et les années
qu'elle couvre ne sont pas certifiées.

CE QUE LE CONTRÔLE DE SOMME A TROUVÉ, ET QUI N'EST PAS UNE ERREUR DE LECTURE

L'article D. 741-35, dans sa rédaction du 22 avril 2005, annonce 15,15 % puis
détaille 7,20 + 6,55 + 1,40 + 0,10, soit 15,25 %. La recodification a repris le
total du décret n° 50-444 d'avant 2004, quand il ne comptait pas encore la part
salariale déplafonnée, et l'a gardé en ajoutant la composante. Ce sont les
composantes qui sont écrites, et le récupérateur les retient ; l'écart est
signalé à chaque exécution plutôt que corrigé en silence.

CE QUI MONTE LA GARDE, ET POURQUOI IL FAUT UN GARDE-FOU DE PLUS

Un décret peut donc changer ces taux sans que la chaîne des versions le montre.
Le récupérateur interroge pour cela la base JORF : tout décret publié depuis
1982 dont le titre porte « taux » et « cotisation » avec le régime général ou
les assurances sociales agricoles doit être expliqué — soit il ouvre une version
de la chaîne, soit il est déclaré dans ``HORS_CODE``, soit il est nommé dans
``SANS_EFFET`` avec la raison pour laquelle il ne touche pas à ce taux. Un décret
qui n'entre dans aucune de ces trois cases **arrête la certification** : le dépôt
ne sait plus si sa série est complète, et le dire est le seul comportement
honnête.

La requête **ne demande pas le mot « vieillesse »**, et c'est une leçon prise
sur la période que ce récupérateur ne couvre pas : le décret n° 79-650 du
30 juillet 1979 a relevé « à titre exceptionnel » les taux du régime général du
1er août 1979 au 31 janvier 1981 sans nommer un seul risque, ni dans son titre
ni dans sa notice. Un garde-fou qui aurait exigé le mot l'aurait laissé passer.
Le prix est une trentaine de candidats au lieu d'une douzaine, tous nommés.

POURQUOI IL LIT L'INDEX ET NON LE DUMP

Comme ``dila_legi_contribution_employeur.py`` : le dump global de la DILA n'a
pas été régénéré depuis juillet 2025, quand l'index publié par le dépôt reçoit
les incréments quotidiens. La version de l'article D. 242-4 qui porte l'année
2026 — celle du décret n° 2025-1446 du 31 décembre 2025 — n'est que dans les
incréments.
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

SORTIE = Path("data/brut/dila_taux_cotisation.json")

#: Le *Journal officiel* écrit « 8,20 % », « 8,2 p. 100 », et la consolidation
#: LEGI glisse parfois une espace après la virgule : « 15, 45 % ».
NB = r"(\d{1,2},\s?\d{1,2}|\d{1,2})"
PC = r"\s*(?:%|p\.\s?100)"

#: Le début de la clause qui porte le taux vieillesse. Ni un point-virgule ni un
#: point ne peuvent la traverser — ils séparent les risques les uns des autres —
#: et le mot « maladie » l'interdit aussi : sans cette exclusion, la clause de
#: l'assurance maladie qui précède serait lue à la place.
ANCRE = re.compile(r"taux de la cotisation(?:(?![;.]|maladie)[\s\S]){0,200}?vieillesse", re.I)

#: Ce qui ferme la clause : le risque suivant, la dérogation des rentiers
#: d'accident du travail, ou l'alinéa suivant de l'article.
FINS = (r"\b[BC]\s*[-.]\s*Le taux", r"Pour les assur[ée]s mentionn[ée]s",
        r"\b[23]\s*[°.]\s*(?:La cotisation|Le taux)")

#: La phrase : total annoncé, puis les deux parts sous plafond.
PHRASE = re.compile(
    r"est fix[ée]{1,2}\s*(?::\s*[Aà]|[àa])\s*" + NB + PC + r"\s*,?\s*soit\s*"
    + NB + PC + r"\s*[àa] la charge de l['’]employeur et\s*" + NB + PC
    + r"\s*[àa] la charge du salari[ée]", re.I)

#: La part déplafonnée, sous ses deux rédactions : celle d'avant 2004, qui ne
#: met à la charge de l'employeur, et celle d'après, qui partage.
TOTALITE_PARTAGEE = re.compile(
    r"sur la totalit[ée] des r[ée]mun[ée]rations[^,.;]{0,60},\s*" + NB + PC
    + r"\s*[àa] la charge de l['’]employeur et\s*" + NB + PC
    + r"\s*[àa] la charge du salari[ée]", re.I)
TOTALITE_EMPLOYEUR = re.compile(
    r"et\s*" + NB + PC + r"\s*[àa] la charge de l['’]employeur sur la totalit[ée]", re.I)

#: Le renvoi d'un article à un autre, que le récupérateur suit.
RENVOI = re.compile(
    r"est fix[ée]{1,2}\s+selon les dispositions pr[ée]vues [àa] l['’]article\s+"
    r"([DRL]\.?\s?\d+-\d+)", re.I)

#: Le tableau : quatre colonnes — employeur et salarié sous plafond, puis sur la
#: totalité —, et une ligne par période, que le tableau date lui-même.
ENTETE_TABLEAU = re.compile(r"Employeur\s+Salari[ée]\s+Employeur\s+Salari[ée]", re.I)
LIGNE_TABLEAU = re.compile(
    r"(Jusqu['’]au\s+\d{1,2}\s+\w+\s+\d{4}"
    r"|Du\s+1\s?er\s+\w+\s*(?:\d{4}\s*)?au\s+\d{1,2}\s+\w+\s+\d{4}"
    r"|A\s*compter\s+du\s+1\s?er\s+\w+\s+\d{4})\s*"
    + NB + PC + r"\s*" + NB + PC + r"\s*" + NB + PC + r"\s*" + NB + PC, re.I)

MOIS = {"janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5,
        "juin": 6, "juillet": 7, "août": 8, "aout": 8, "septembre": 9,
        "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12}

TOUJOURS = date(2999, 1, 1)

#: Les deux régimes et la chaîne d'articles de chacun, dans l'ordre du temps.
#: Chaque entrée dit comment retrouver les versions d'un article : par le
#: numéro d'article et le titre du texte qui le porte.
CHAINES: dict[str, tuple[tuple[str, str, str], ...]] = {
    "regime_general": (
        ("2", "Décret n°81-1013 %", "décret n° 81-1013 du 13 novembre 1981, article 2"),
        ("D242-4", "Code de la sécurité sociale", "code de la sécurité sociale, article D. 242-4"),
    ),
    "msa_salaries": (
        ("2", "Décret n°50-444 %", "décret n° 50-444 du 20 avril 1950, article 2"),
        ("D741-35", "Code rural%", "code rural et de la pêche maritime, article D. 741-35"),
    ),
}

#: Ce que le renvoi d'un article désigne : numéro d'article -> régime dont la
#: série fait foi. Seul D. 242-4 est renvoyé aujourd'hui.
RENVOIS_CONNUS = {"D242-4": "regime_general"}

#: Un article qui n'a qu'UNE version et qui couvre plus que cela n'a pas de
#: chronologie : la base en a gardé l'état final, daté de la naissance du texte.
#: C'est le cas de l'article 3 du décret n° 67-803, lu ci-dessous pour être
#: refusé — la règle s'applique, elle n'est pas invoquée.
SEUIL_VERSION_UNIQUE = 10.0

#: Les chaînes lues POUR ÊTRE REFUSÉES, avec ce que le dépôt sait par ailleurs
#: de la période qu'elles prétendent couvrir. Les lire est ce qui fait de leur
#: refus une constatation.
CONTRE_EPREUVES: tuple[tuple[str, str, str], ...] = (
    ("3", "Décret n°67-803 %", "décret n° 67-803 du 20 septembre 1967, article 3"),
)

#: Une version qui court plus longtemps que cela peut avoir avalé un texte que
#: la base n'a pas gardé. Elle n'est pas écartée — la chaîne est dense de part
#: et d'autre —, mais elle est signalée.
VERSION_LONGUE = 8.0

#: Le taux qu'un décret a fixé SANS réécrire l'article. Chaque entrée est
#: relue dans la base à chaque exécution : la notice doit porter la période et
#: le taux annoncés, et la version qui suit la fenêtre doit porter le même taux
#: — c'est la corroboration qui autorise la surcharge.
HORS_CODE: tuple[dict, ...] = (
    {
        "id": "JORFTEXT000000516870",
        "decret": "décret n° 87-453 du 29 juin 1987",
        "regimes": ("regime_general", "msa_salaries"),
        "composante": "salarie_plafonne",
        "debut": date(1987, 7, 1),
        "fin": date(1988, 6, 30),
        "taux": 0.066,
        "motif_periode": re.compile(r"DU (\d{2}-\d{2}-\d{4}) AU (\d{2}-\d{2}-\d{4})"),
        "motif_taux": re.compile(r"(\d{1,2},\d+)\s*%[^.]{0,40}?POUR L['’]ASSURANCE VIEILLESSE", re.I),
        "note": "relèvement exceptionnel et temporaire de 0,2 point de la part "
                "salariale, pérennisé par le décret n° 88-772 du 22 juin 1988",
    },
)

#: La requête du garde-fou : tout décret publié depuis 1982 qui annonce dans son
#: titre des taux de cotisation du régime général ou des assurances sociales
#: agricoles. Elle n'exige PAS le mot « vieillesse », et c'est délibéré : le
#: décret n° 79-650 du 30 juillet 1979, qui a relevé « à titre exceptionnel »
#: les taux du régime général du 1er août 1979 au 31 janvier 1981, ne nomme
#: aucun risque — ni dans son titre, ni dans sa notice. Un garde-fou qui aurait
#: demandé le mot l'aurait laissé passer. Le prix est une trentaine de candidats
#: au lieu d'une douzaine, tous nommés dans ``SANS_EFFET`` ci-dessous.
PREMIERE_ANNEE_GARDE = 1982
REQUETE_GARDE = (
    'titre:taux AND (titre:cotisation OR titre:cotisations) AND '
    '(titre:"regime general" OR titre:"assurances sociales agricoles" '
    'OR titre:"salaries agricoles")'
)

#: Un décret qui ouvre une version est publié la veille ou le jour même de sa
#: prise d'effet ; la base date parfois l'une et l'autre à quelques jours près.
TOLERANCE_OUVERTURE = 15

#: Les décrets que la requête ramène et qui ne touchent pas à ce taux, avec la
#: raison. Un décret qui n'est ni ici, ni dans ``HORS_CODE``, ni à l'ouverture
#: d'une version arrête la certification.
SANS_EFFET: dict[str, str] = {
    "JORFTEXT000000880483":
        "décret n° 82-445 du 28 mai 1982 : taux et conditions d'exonération de "
        "la cotisation d'assurance MALADIE",
    "JORFTEXT000000883619":
        "décret n° 82-1082 du 20 décembre 1982 : pénalités et majorations de "
        "retard du recouvrement, aucun taux de cotisation",
    "JORFTEXT000000690640":
        "décret n° 83-1196 du 30 décembre 1983 : tableau de l'article 1er du "
        "décret n° 67-804, branche MALADIE des salariés partiellement rattachés",
    "JORFTEXT000000509383":
        "décret n° 88-334 du 6 avril 1988 : cotisation d'assurance maladie des "
        "assurés en situation de PRÉRETRAITE, 5,50 %",
    "JORFTEXT000000719897":
        "décret n° 91-614 du 28 juin 1991 : taux des cotisations d'assurance "
        "MALADIE du régime général",
    "JORFTEXT000000719893":
        "décret n° 91-615 du 28 juin 1991 : même objet, salariés agricoles",
    "JORFTEXT000000539214":
        "décret n° 91-1388 du 31 décembre 1991 : cotisations d'assurance maladie",
    "JORFTEXT000000540784":
        "décret n° 92-572 du 25 juin 1992 : cotisations d'assurance maladie",
    "JORFTEXT000000528933":
        "décret n° 93-275 du 26 février 1993 : assiette et taux des cotisations "
        "des JEUNES AGRICULTEURS STAGIAIRES",
    "JORFTEXT000000881424":
        "décret n° 93-275 du 26 février 1993, seconde fiche du même texte",
    "JORFTEXT000000556674":
        "décret n° 95-1401 du 30 décembre 1995 : cotisation d'assurance maladie "
        "sur les avantages de retraite des salariés agricoles",
    "JORFTEXT000028968045":
        "décret n° 2014-517 du 22 mai 2014 : taux et calcul de la cotisation "
        "MALADIE",
    "JORFTEXT000000332799":
        "décret n° 87-470 du 30 juin 1987 : relèvement temporaire de la seule "
        "cotisation MALADIE des fonctionnaires, ouvriers de l'État et assurés "
        "relevant partiellement du régime général",
    "JORFTEXT000000693584":
        "décret n° 88-795 du 22 juin 1988 : cotisation maladie des articles "
        "D. 712-38 et D. 713-15 et du décret n° 67-804 (affiliation partielle)",
    "JORFTEXT000000372944":
        "décret n° 95-1356 du 30 décembre 1995 : cotisation d'assurance maladie "
        "assise sur les avantages de retraite, articles D. 242-8 et D. 242-12",
    "JORFTEXT000031740354":
        "décret n° 2015-1852 du 29 décembre 2015 : taux des cotisations "
        "d'assurance maladie ; « vieillesse » n'y est que le nom de la Cavimac",
    "JORFTEXT000033735173":
        "décret n° 2016-1932 du 28 décembre 2016 : même objet que le précédent",
    "JORFTEXT000053228345":
        "décret n° 2025-1417 du 30 décembre 2025 : cotisation vieillesse de base "
        "des NON-SALARIÉS agricoles, alignée sur celle des indépendants",
}

#: Bornes de vraisemblance. Elles n'ont pas à juger un barème, seulement à
#: attraper une phrase lue de travers : le taux plafonné a valu 11,9 % en 1980
#: et 15,45 % aujourd'hui, la part salariale a monté de 36 % à 51 % du total, et
#: la cotisation déplafonnée n'a jamais dépassé trois points.
PLAFONNE_PLAUSIBLE = (0.08, 0.25)
PART_SALARIALE_PLAUSIBLE = (0.25, 0.60)
DEPLAFONNE_PLAUSIBLE = (0.0, 0.05)

#: Écart toléré entre le total qu'annonce la phrase et la somme de ses
#: composantes, et saut maximal d'une année sur l'autre.
ECART_TOTAL = 5e-5
SAUT_MAXIMAL = 0.025

COMPOSANTES = ("employeur_plafonne", "salarie_plafonne",
               "employeur_deplafonne", "salarie_deplafonne")


def _nombre(texte: str) -> float:
    return float(texte.replace(" ", "").replace(",", ".")) / 100


def _jour(texte: str) -> date:
    return date.fromisoformat(texte) if texte else TOUJOURS


def _clause(texte: str) -> str | None:
    """La phrase, le tableau ou le renvoi qui porte le taux vieillesse."""
    ancre = ANCRE.search(texte)
    if ancre is None:
        return None
    reste = texte[ancre.start():]
    for fin in FINS:
        coupe = re.search(fin, reste)
        if coupe and coupe.start() > 40:
            reste = reste[:coupe.start()]
    return reste


def _periode(libelle: str) -> tuple[date, date]:
    """Les bornes d'une ligne de tableau, telles que le tableau les écrit."""
    lu = libelle.lower().replace("1 er", "1er")
    trouve = re.match(r"jusqu['’]au\s+(\d{1,2})\s+(\w+)\s+(\d{4})", lu)
    if trouve:
        return (date(1900, 1, 1),
                date(int(trouve.group(3)), MOIS[trouve.group(2)], int(trouve.group(1))))
    trouve = re.match(r"du\s+1er\s+(\w+)\s*(\d{4})?\s*au\s+(\d{1,2})\s+(\w+)\s+(\d{4})", lu)
    if trouve:
        fin_annee = int(trouve.group(5))
        return (date(int(trouve.group(2) or fin_annee), MOIS[trouve.group(1)], 1),
                date(fin_annee, MOIS[trouve.group(4)], int(trouve.group(3))))
    trouve = re.match(r"a\s*compter\s+du\s+1er\s+(\w+)\s*(\d{4})", lu)
    if trouve:
        return (date(int(trouve.group(2)), MOIS[trouve.group(1)], 1), TOUJOURS)
    raise ValueError(f"période illisible : {libelle}")


def lire_version(texte: str) -> dict | None:
    """Ce qu'une version d'article dit du taux vieillesse."""
    clause = _clause(texte)
    if clause is None:
        return None
    renvoi = RENVOI.search(clause)
    if renvoi:
        return {"forme": "renvoi", "article": re.sub(r"[\s.]", "", renvoi.group(1))}
    entete = ENTETE_TABLEAU.search(clause)
    if entete:
        lignes = []
        for trouve in LIGNE_TABLEAU.finditer(clause[entete.end():]):
            debut, fin = _periode(trouve.group(1))
            lignes.append({
                "libelle": " ".join(trouve.group(1).split()),
                "debut": debut.isoformat(), "fin": fin.isoformat(),
                "employeur_plafonne": _nombre(trouve.group(2)),
                "salarie_plafonne": _nombre(trouve.group(3)),
                "employeur_deplafonne": _nombre(trouve.group(4)),
                "salarie_deplafonne": _nombre(trouve.group(5)),
            })
        return {"forme": "tableau", "lignes": lignes} if lignes else None
    phrase = PHRASE.search(clause)
    if phrase is None:
        return None
    taux = {
        "forme": "phrase",
        "total_annonce": _nombre(phrase.group(1)),
        "employeur_plafonne": _nombre(phrase.group(2)),
        "salarie_plafonne": _nombre(phrase.group(3)),
        "employeur_deplafonne": 0.0,
        "salarie_deplafonne": 0.0,
    }
    suite = clause[phrase.end():]
    partagee = TOTALITE_PARTAGEE.search(suite)
    employeur = TOTALITE_EMPLOYEUR.search(suite)
    if partagee:
        taux["employeur_deplafonne"] = _nombre(partagee.group(1))
        taux["salarie_deplafonne"] = _nombre(partagee.group(2))
    elif employeur:
        taux["employeur_deplafonne"] = _nombre(employeur.group(1))
    return taux


def versions(db: sqlite3.Connection, chaine, signalements: list[str]) -> list[dict]:
    """Les versions lisibles d'une chaîne d'articles, triées par date d'effet."""
    lues: list[dict] = []
    for num, titre, libelle in chaine:
        trouvees = []
        for ident, debut, fin, texte in db.execute(
            "SELECT id, date, fin, texte FROM doc WHERE num = ? AND titre LIKE ? "
            "ORDER BY date", (num, titre),
        ):
            taux = lire_version(texte)
            if taux is None:
                continue
            trouvees.append({"id": ident, "debut": debut, "fin": fin or TOUJOURS.isoformat(),
                             "article": libelle, **taux})
        # Une version dont la base fait finir la validité avant qu'elle ne
        # commence est une incohérence de consolidation : elle ne date rien.
        gardees = [v for v in trouvees if _jour(v["fin"]) > _jour(v["debut"])]
        for rejetee in trouvees:
            if rejetee not in gardees:
                signalements.append(
                    f"version incohérente ignorée : {rejetee['id']} "
                    f"({rejetee['debut']} → {rejetee['fin']}), {libelle}")
        if len(gardees) == 1:
            portee = (_jour(gardees[0]["fin"]) - _jour(gardees[0]["debut"])).days / 365.25
            if portee > SEUIL_VERSION_UNIQUE:
                signalements.append(
                    f"REFUSÉ  {libelle} : une seule version, {portee:.0f} ans "
                    f"({gardees[0]['debut']} → {gardees[0]['fin']}) — la base en a "
                    "gardé l'état final, pas la chronologie")
                continue
        lues.extend(gardees)
    return sorted(lues, key=lambda v: (v["debut"], v["id"]))


def au_premier_janvier(lues: list[dict], annee: int, series: dict,
                       profondeur: int = 0) -> dict | None:
    """Le taux en vigueur au 1er janvier d'une année, renvois suivis."""
    jour = date(annee, 1, 1)
    candidates = [v for v in lues if _jour(v["debut"]) <= jour < _jour(v["fin"])]
    if not candidates:
        return None
    version = max(candidates, key=lambda v: (v["debut"], v["id"]))
    if version["forme"] == "renvoi":
        regime = RENVOIS_CONNUS.get(version["article"])
        if regime is None or profondeur >= 3:
            return None
        vise = series.get(regime, {}).get(str(annee))
        if vise is None:
            return None
        return {**{c: vise[c] for c in COMPOSANTES},
                "source": f"{version['id']} → {vise['source']}",
                "article": f"{version['article']} (renvoi)"}
    if version["forme"] == "tableau":
        for ligne in version["lignes"]:
            if _jour(ligne["debut"]) <= jour <= _jour(ligne["fin"]):
                return {**{c: ligne[c] for c in COMPOSANTES},
                        "source": version["id"], "article": version["article"],
                        "ligne": ligne["libelle"]}
        return None
    return {**{c: version[c] for c in COMPOSANTES},
            "source": version["id"], "article": version["article"]}


def surcharges(db: sqlite3.Connection, series: dict, lues: dict,
               signalements: list[str]) -> list[dict]:
    """Les taux fixés hors du code, relus et corroborés avant d'être appliqués."""
    appliquees = []
    for declaration in HORS_CODE:
        ligne = db.execute("SELECT titre, texte FROM doc WHERE id = ?",
                           (declaration["id"],)).fetchone()
        if ligne is None:
            signalements.append(f"surcharge écartée : {declaration['id']} absent de l'index")
            continue
        notice = f"{ligne[0]} {ligne[1]}"
        periode = declaration["motif_periode"].search(notice)
        taux = declaration["motif_taux"].search(notice)
        if not (periode and taux):
            signalements.append(
                f"surcharge écartée : la notice de {declaration['decret']} "
                "ne porte plus la période ou le taux annoncés")
            continue
        jours = [date(int(t[6:]), int(t[3:5]), int(t[:2])) for t in periode.groups()]
        if jours != [declaration["debut"], declaration["fin"]] \
                or abs(_nombre(taux.group(1)) - declaration["taux"]) > ECART_TOTAL:
            signalements.append(
                f"surcharge écartée : la notice de {declaration['decret']} dit "
                f"{jours[0]} → {jours[1]} à {_nombre(taux.group(1)):.4f}, la "
                f"déclaration {declaration['debut']} → {declaration['fin']} à "
                f"{declaration['taux']:.4f}")
            continue
        for regime in declaration["regimes"]:
            # Corroboration : la version qui suit la fenêtre doit porter le taux
            # surchargé — c'est la pérennisation qui prouve que la hausse a eu lieu.
            suivantes = [v for v in lues[regime]
                         if _jour(v["debut"]) > declaration["debut"]
                         and v["forme"] == "phrase"]
            if not suivantes or abs(min(suivantes, key=lambda v: v["debut"])[
                    declaration["composante"]] - declaration["taux"]) > ECART_TOTAL:
                signalements.append(
                    f"surcharge écartée pour {regime} : la version qui suit "
                    f"{declaration['debut']} ne porte pas {declaration['taux']:.4f}")
                continue
            touchees = []
            for annee in sorted(series[regime]):
                if declaration["debut"] <= date(int(annee), 1, 1) <= declaration["fin"]:
                    series[regime][annee][declaration["composante"]] = declaration["taux"]
                    series[regime][annee]["source"] += f" + {declaration['id']}"
                    touchees.append(annee)
            appliquees.append({"decret": declaration["decret"], "regime": regime,
                               "composante": declaration["composante"],
                               "annees": touchees, "taux": declaration["taux"],
                               "note": declaration["note"]})
    return appliquees


def garde(db_jorf: sqlite3.Connection, lues: dict) -> list[str]:
    """Les décrets du JORF que la chaîne des versions n'explique pas."""
    ouvertures = [_jour(v["debut"]) for chaine in lues.values() for v in chaine]
    declares = {d["id"] for d in HORS_CODE}
    inexpliques = []
    for ident, publie, titre in db_jorf.execute(
        "SELECT doc.id, doc.date, doc.titre FROM fts JOIN doc ON doc.rowid = fts.rowid "
        "WHERE fts MATCH ? AND doc.date >= ? AND doc.num = '' "
        "AND upper(doc.nature) = 'DECRET' ORDER BY doc.date",
        (REQUETE_GARDE, str(PREMIERE_ANNEE_GARDE)),
    ):
        if ident in declares or ident in SANS_EFFET:
            continue
        jour = _jour(publie)
        if any(0 <= (ouverture - jour).days <= TOLERANCE_OUVERTURE for ouverture in ouvertures):
            continue
        inexpliques.append(f"{publie}  {ident}  {titre[:110]}")
    return inexpliques


def _ouvrir(base: str) -> sqlite3.Connection:
    chemin = chemin_index(base)
    if not chemin.exists():
        print(f"Index {base} absent : récupération de l'index publié.")
        recuperer(base, chemin)
    db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    print(f"Index {base:<5} {meta(db, 'dump') or '?'}, "
          f"à jour au {meta(db, 'dernier_increment') or '?'}")
    return db


def main() -> int:
    try:
        legi, jorf = _ouvrir("legi"), _ouvrir("jorf")
    except (LookupError, RuntimeError, OSError) as erreur:
        print(f"ÉCHEC   index DILA : {erreur}", file=sys.stderr)
        return 1

    signalements: list[str] = []
    lues = {regime: versions(legi, chaine, signalements)
            for regime, chaine in CHAINES.items()}
    for contre in CONTRE_EPREUVES:
        versions(legi, (contre,), signalements)

    for regime, chaine in lues.items():
        for version in chaine:
            portee = (_jour(version["fin"]) - _jour(version["debut"])).days / 365.25
            if _jour(version["fin"]) != TOUJOURS and portee > VERSION_LONGUE:
                signalements.append(
                    f"version longue : {regime} {version['id']} court {portee:.0f} ans "
                    f"({version['debut']} → {version['fin']})")
            if version["forme"] != "phrase":
                continue
            somme = sum(version[c] for c in COMPOSANTES)
            if abs(somme - version["total_annonce"]) > ECART_TOTAL:
                signalements.append(
                    f"total en désaccord : {regime} {version['id']} annonce "
                    f"{version['total_annonce']:.4f}, ses composantes font {somme:.4f}")

    # Les années, régime par régime. Le régime général d'abord : les salariés
    # agricoles lui renvoient depuis 2014.
    series: dict[str, dict[str, dict]] = {regime: {} for regime in CHAINES}
    premiere = min(int(v["debut"][:4]) for chaine in lues.values() for v in chaine)
    derniere = date.today().year
    for regime in ("regime_general", "msa_salaries"):
        for annee in range(premiere, derniere + 1):
            trouve = au_premier_janvier(lues[regime], annee, series)
            if trouve is not None:
                series[regime][str(annee)] = trouve

    appliquees = surcharges(jorf, series, lues, signalements)
    inexpliques = garde(jorf, lues)

    for regime, annees in series.items():
        precedent = None
        for annee in sorted(annees):
            taux = annees[annee]
            plafonne = taux["employeur_plafonne"] + taux["salarie_plafonne"]
            deplafonne = taux["employeur_deplafonne"] + taux["salarie_deplafonne"]
            part = taux["salarie_plafonne"] / plafonne if plafonne else 0.0
            if not PLAFONNE_PLAUSIBLE[0] <= plafonne <= PLAFONNE_PLAUSIBLE[1] \
                    or not PART_SALARIALE_PLAUSIBLE[0] <= part <= PART_SALARIALE_PLAUSIBLE[1] \
                    or not DEPLAFONNE_PLAUSIBLE[0] <= deplafonne <= DEPLAFONNE_PLAUSIBLE[1]:
                signalements.append(
                    f"hors bornes : {regime} {annee} plafonné {plafonne:.4f}, "
                    f"part salariale {part:.4f}, déplafonné {deplafonne:.4f}")
            if precedent and abs(plafonne - precedent) > SAUT_MAXIMAL:
                signalements.append(
                    f"saut : {regime} {annee} passe de {precedent:.4f} à {plafonne:.4f}")
            precedent = plafonne
        manquantes = [a for a in range(min(int(x) for x in annees),
                                       max(int(x) for x in annees) + 1)
                      if str(a) not in annees]
        if manquantes:
            signalements.append(f"années sans version : {regime} {manquantes}")

    charge = {
        "source": "DILA, bases LEGI et JORF, via l'index du dépôt",
        "index": {base: {"dump": meta(db, "dump"),
                         "dernier_increment": meta(db, "dernier_increment")}
                  for base, db in (("legi", legi), ("jorf", jorf))},
        "recupere_le": date.today().isoformat(),
        "note": "taux en vigueur au 1er janvier de l'année ; quatre composantes, "
                "employeur et salarié, sous plafond et sur la totalité",
        "articles": {regime: [libelle for _, _, libelle in chaine]
                     for regime, chaine in CHAINES.items()},
        "versions": lues,
        "series": series,
        "surcharges": appliquees,
        "decrets_inexpliques": inexpliques,
        "signalements": signalements,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(charge, ensure_ascii=False, indent=1, default=str),
                      encoding="utf-8")

    for regime, annees in series.items():
        if not annees:
            print(f"ÉCHEC   {regime} : aucune année lue", file=sys.stderr)
            return 1
        bornes = f"{min(annees)}-{max(annees)}"
        print(f"OK      {regime:<16} {len(annees)} années ({bornes}), "
              f"{len(lues[regime])} versions")
    for ligne in appliquees:
        print(f"HORS CODE {ligne['regime']} {ligne['annees']} "
              f"{ligne['composante']} {ligne['taux']:.4f} — {ligne['decret']}")
    for ligne in signalements:
        print(f"        {ligne}")
    if inexpliques:
        print("\nDÉCRETS INEXPLIQUÉS — la certification s'arrête :", file=sys.stderr)
        for ligne in inexpliques:
            print(f"        {ligne}", file=sys.stderr)
        return 1
    print(f"\n{sum(len(a) for a in series.values())} années écrites dans {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
