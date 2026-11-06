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
(``DATES_D_UN_AUTRE_ARTICLE``), ou, quand elle le date de l'entrée en vigueur du
décret, celle que le décret fixe (``ENTREES_EN_VIGUEUR``, ``ENTREES_LUES_A_LEGIFRANCE``),
ou, s'il n'en fixe pas, le lendemain de sa publication (``LENDEMAINS_DE_PUBLICATION``,
code civil, art. 1er, depuis le 1er juin 2004), sinon l'entrée en vigueur
de l'article (``debut``) ; les versions suivantes d'un article qui redisent le même
tableau ne font pas un second reclassement. L'ancienneté conservée se garde « dans la limite de la durée de
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
    # n° 98-896, art. 8 : le n° 2002-378, art. 1er (JORFARTI000002416455), n'en ôte que
    # « en fonctions à la date du présent décret », sans clause d'effet ; le tableau ne
    # change pas (relecture R-B6, B6).
    "LEGIARTI000006508629": ("1996-08-01", "LEGIARTI000006508631",
                             "Les dispositions des articles 1er, 6, 7 et 8 du présent décret "
                             "sont applicables à compter du 1er août 1996."),
}

#: Le décret qui fixe lui-même son entrée en vigueur, ou son effet, quand la phrase d'un
#: de ses tableaux date le reclassement de cette entrée en vigueur (« A la date d'entrée
#: en vigueur du présent décret », « à la date d'effet du présent décret ») (action 158,
#: B6) : son numéro → la date, l'article qui la fixe (LEGIARTI, seule version), le texte
#: au JORF et le jour de sa publication, dont part « le premier jour du mois suivant sa
#: publication », et les mots de la clause, lus au LEGI et au JORF.
ENTREES_EN_VIGUEUR = {
    "98-809": ("1995-08-01", "LEGIARTI000006508229", "JORFTEXT000000194869", "1998-09-12",
            "Le présent décret prend effet au 1er août 1995, à l'exception des articles 3 et "
            "4."),
    "2011-964": ("2011-09-01", "LEGIARTI000024477652", "JORFTEXT000024476275", "2011-08-18",
            "Le présent décret entre en vigueur le premier jour du mois suivant sa "
            "publication."),
    # Le décret ne dit qu'une fois quand il s'applique (cette clause, art. 35) ; ses tableaux
    # disent « la date d'entrée en vigueur du présent décret » : B6-bis (relecture R-B7).
    "2011-1140": ("2011-10-01", "LEGIARTI000024581626", "JORFTEXT000024580517", "2011-09-23",
            "Le présent décret prend effet à compter du 1er jour du mois qui suit sa "
            "publication."),
    "2011-1642": ("2011-12-01", "LEGIARTI000024847365", "JORFTEXT000024846671", "2011-11-25",
            "Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa "
            "publication."),
    "2011-1987": ("2012-01-01", "LEGIARTI000025072735", "JORFTEXT000025046328", "2011-12-29",
            "Les dispositions du présent décret entrent en vigueur le 1er janvier 2012."),
    "2011-1988": ("2012-01-01", "LEGIARTI000025073321", "JORFTEXT000025046447", "2011-12-29",
            "Les dispositions du présent décret entrent en vigueur le 1er janvier 2012."),
    "2012-230": ("2012-03-01", "LEGIARTI000025378144", "JORFTEXT000025376765", "2012-02-18",
            "Les dispositions du présent décret entrent en vigueur le 1er mars 2012."),
    "2012-379": ("2012-04-01", "LEGIARTI000025546343", "JORFTEXT000025545406", "2012-03-21",
            "Le présent décret entre en vigueur le premier jour du mois suivant sa "
            "publication au Journal officiel de la République française."),
    "2012-924": ("2012-08-01", "LEGIARTI000026237262", "JORFTEXT000026236871", "2012-07-31",
            "Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa "
            "publication."),
    "2012-984": ("2012-09-01", "LEGIARTI000026311285", "JORFTEXT000026310499", "2012-08-24",
            "Le présent décret entre en vigueur le premier jour du mois suivant sa "
            "publication."),
    "2012-1099": ("2012-10-01", "LEGIARTI000026428567", "JORFTEXT000026427069", "2012-09-30",
            "Le présent décret entre en vigueur le 1er octobre 2012."),
    "2012-1161": ("2012-11-01", "LEGIARTI000026508387", "JORFTEXT000026507710", "2012-10-19",
            "Le présent décret entre en vigueur le premier jour du mois suivant celui de sa "
            "publication au Journal officiel de la République française."),
    "2012-1419": ("2013-01-01", "LEGIARTI000026797414", "JORFTEXT000026796060", "2012-12-20",
            "Le présent décret entre en vigueur à compter du premier jour du mois qui suit sa "
            "publication."),
    "2012-1420": ("2013-01-01", "LEGIARTI000026796792", "JORFTEXT000026796099", "2012-12-20",
            "Le présent décret entre en vigueur à compter du premier jour du mois qui suit sa "
            "publication."),
    "2013-830": ("2013-10-01", "LEGIARTI000027962726", "JORFTEXT000027962189", "2013-09-18",
            "Les dispositions du présent décret entrent en vigueur le premier jour du mois "
            "suivant sa publication."),
    "2014-75": ("2014-02-01", "LEGIARTI000028540391", "JORFTEXT000028539339", "2014-01-31",
            "Les dispositions du présent décret entrent en vigueur le premier jour du mois "
            "suivant sa publication."),
    "2014-76": ("2014-02-01", "LEGIARTI000028540771", "JORFTEXT000028539402", "2014-01-31",
            "Le présent décret entre en vigueur le premier jour du mois suivant sa date de "
            "publication."),
    "2014-79": ("2014-02-01", "LEGIARTI000028540862", "JORFTEXT000028539499", "2014-01-31",
            "Les dispositions du présent décret entrent en vigueur le premier jour du mois "
            "suivant sa publication."),
    "2014-81": ("2014-02-01", "LEGIARTI000028541522", "JORFTEXT000028539558", "2014-01-31",
            "Les dispositions du présent décret entrent en vigueur le premier jour du mois "
            "suivant sa date de publication."),
    "2014-922": ("2014-09-01", "LEGIARTI000029384148", "JORFTEXT000029382044", "2014-08-21",
            "Le présent décret entre en vigueur le premier jour du mois qui suit sa "
            "publication."),
    "2014-1164": ("2014-11-01", "LEGIARTI000029563614", "JORFTEXT000029562200", "2014-10-11",
            "Le présent décret entre en vigueur le premier jour du mois suivant sa "
            "publication au Journal officiel de la République française."),
    "2015-303": ("2015-04-01", "LEGIARTI000030371580", "JORFTEXT000030370469", "2015-03-19",
            "Le présent décret entre en vigueur le premier jour du mois qui suit sa "
            "publication."),
    "2015-1275": ("2015-11-01", "LEGIARTI000031317655", "JORFTEXT000031313295", "2015-10-15",
            "Le présent décret entre en vigueur le premier jour du mois suivant sa "
            "publication au Journal officiel de la République française."),
    "2016-219": ("2016-03-01", "LEGIARTI000032128540", "JORFTEXT000032114422", "2016-02-28",
            "Le présent décret entre en vigueur le premier jour du mois suivant celui de sa "
            "publication."),
    "2016-336": ("2016-04-01", "LEGIARTI000032276866", "JORFTEXT000032276187", "2016-03-22",
            "Le présent décret entre en vigueur à compter du premier jour du mois qui suit "
            "celui de sa publication."),
    "2016-2002": ("2017-01-01", "LEGIARTI000033792205", "JORFTEXT000033758808", "2016-12-31",
            "Le présent décret entre en vigueur le 1er janvier 2017."),
    "2017-180": ("2017-01-01", "LEGIARTI000034036522", "JORFTEXT000034035533", "2017-02-15",
            "Le présent décret entre en vigueur le 1er janvier 2017."),
    "2017-233": ("2017-03-01", "LEGIARTI000034082772", "JORFTEXT000034080592", "2017-02-25",
            "Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa "
            "publication."),
    "2020-1174": ("2020-10-01", "LEGIARTI000042368622", "JORFTEXT000042365978", "2020-09-27",
            "Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa "
            "publication."),
    "2020-1175": ("2020-10-01", "LEGIARTI000042368942", "JORFTEXT000042366071", "2020-09-27",
            "Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa "
            "publication."),
    # Les deux phrases de l'art. 12 (relecture R-B7, écart 1) : la seconde ôte des personnes,
    # non des articles, et les tableaux des art. 7, 8 et 9 gardent le 1er janvier 2022 pour
    # les agents qu'ils reclassent.
    "2021-1818": ("2022-01-01", "LEGIARTI000044804898", "JORFTEXT000044571714", "2021-12-28",
            "Les dispositions du présent décret entrent en vigueur le 1er janvier 2022. Elles "
            "ne s'appliquent pas aux auxiliaires de puériculture relevant, au 31 décembre "
            "2021, du cadre d'emplois régi par le décret n° 92-865 du 28 août 1992 susvisé ni "
            "aux auxiliaires de soins relevant, à la même date, de la spécialité "
            "aide-soignant du cadre d'emplois régi par le décret n° 92-866 du 28 août 1992 "
            "susvisé."),
    "2021-1826": ("2022-01-01", "LEGIARTI000044799842", "JORFTEXT000044572291", "2021-12-28",
            "Les dispositions du présent décret entrent en vigueur le 1er janvier 2022."),
    "2021-1834": ("2022-01-01", "LEGIARTI000044804034", "JORFTEXT000044572775", "2021-12-28",
            "Les dispositions du présent décret entrent en vigueur le 1er janvier 2022."),
    "2022-516": ("2022-05-01", "LEGIARTI000045540046", "JORFTEXT000045537923", "2022-04-10",
            "Les dispositions du présent décret entrent en vigueur le premier jour du mois "
            "suivant celui de sa publication."),
    "2022-1093": ("2022-08-01", "LEGIARTI000046121303", "JORFTEXT000046114822", "2022-07-31",
            "Le présent décret entre en vigueur le premier jour du mois suivant celui de sa "
            "publication."),
    "2022-1200": ("2022-09-01", "LEGIARTI000046243434", "JORFTEXT000046242148", "2022-09-01",
            "Les dispositions du présent décret entrent en vigueur le 1er septembre 2022."),
    "2022-1206": ("2022-09-01", "LEGIARTI000046243814", "JORFTEXT000046242594", "2022-09-01",
            "Les dispositions du présent décret entrent en vigueur le 1er septembre 2022."),
    "2022-1209": ("2022-09-01", "LEGIARTI000046243977", "JORFTEXT000046242908", "2022-09-01",
            "Le présent décret entre en vigueur le 1er septembre 2022."),
    "2023-527": ("2023-07-01", "LEGIARTI000047766737", "JORFTEXT000047752873", "2023-06-30",
            "Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa "
            "publication."),
    "2023-709": ("2023-09-01", "LEGIARTI000047917296", "JORFTEXT000047915341", "2023-08-02",
            "Les dispositions du présent décret entrent en vigueur le 1er septembre 2023 à "
            "l'exception de celles de l'article 11 qui s'appliquent aux procédures engagées à "
            "compter du 1er janvier 2024."),
    "2023-1092": ("2023-12-01", "LEGIARTI000048461730", "JORFTEXT000048460347", "2023-11-26",
            "Le présent décret entre en vigueur le premier jour du mois suivant celui de sa "
            "publication."),
    "2023-1336": ("2024-01-01", "LEGIARTI000048842648", "JORFTEXT000048728435", "2023-12-30",
            "Le présent décret entre en vigueur le premier jour du mois suivant celui de sa "
            "publication."),
    "2024-51": ("2024-02-01", "LEGIARTI000049063869", "JORFTEXT000049060184", "2024-01-31",
            "Le présent décret entre en vigueur le premier jour du mois suivant celui de sa "
            "publication."),
    "2024-282": ("2024-04-01", "LEGIARTI000049350387", "JORFTEXT000049343100", "2024-03-30",
            "Le présent décret entre en vigueur le premier jour du mois suivant celui de sa "
            "publication."),
    "2025-1002": ("2025-11-01", "LEGIARTI000052461403", "JORFTEXT000052456736", "2025-10-30",
            "Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa "
            "publication."),
    "2025-1003": ("2025-11-01", "LEGIARTI000052461514", "JORFTEXT000052456773", "2025-10-30",
            "Le présent décret entre en vigueur le premier jour du mois qui suit celui de sa "
            "publication."),
    "2025-1327": ("2026-01-01", "LEGIARTI000053186037", "JORFTEXT000053174358", "2025-12-27",
            "Le présent décret entre en vigueur le 1 er janvier 2026."),
    # Action 158, B7 : les textes publiés depuis le 1er juin 2004, que leur clause date
    # (docs/feuille_de_route/158/2026-11-06-b7-dates-d-apres-juin-2004.md).
    # B7 : la clause est dans l'article d'exécution, « prendra effet » (tests :
    # PRISES_D_EFFET).
    "2005-939": ("2006-01-01", "LEGIARTI000006413799", "JORFTEXT000000813276", "2005-08-06",
            "Le ministre d'Etat, ministre de l'intérieur et de l'aménagement du "
            "territoire, le ministre de l'économie, des finances et de l'industrie, le "
            "garde des sceaux, ministre de la justice, le ministre de la fonction "
            "publique et le ministre délégué au budget et à la réforme de l'Etat, "
            "porte-parole du Gouvernement, sont chargés, chacun en ce qui le concerne, "
            "de l'exécution du présent décret, qui prendra effet au 1er janvier 2006 et"
            " sera publié au Journal officiel de la République française."),
    # B7 : le tableau (art. 36) ne date qu'une condition, « à la date de publication du
    # présent décret » ; le décret « prendra effet au 1er novembre 2005 ».
    "2005-1304": ("2005-11-01", "LEGIARTI000006414058", "JORFTEXT000000241288", "2005-10-22",
            "Le ministre d'Etat, ministre de l'intérieur et de l'aménagement du "
            "territoire, le ministre de l'économie, des finances et de l'industrie, le "
            "ministre de la fonction publique et le ministre délégué au budget et à la "
            "réforme de l'Etat, porte-parole du Gouvernement, sont chargés, chacun en "
            "ce qui le concerne, de l'exécution du présent décret, qui prendra effet au"
            " 1er novembre 2005 et sera publié au Journal officiel de la République "
            "française."),
    # B7 : le tableau (art. 33) dit « à la date d'entrée en vigueur du présent titre » ; il
    # est au titre II (art. 31 à 38), que le II date.
    "2010-982": ("2010-09-01", "LEGIARTI000022751503", "JORFTEXT000022747189", "2010-08-28",
            "I. ― Les dispositions du titre Ier entrent en vigueur le 1er septembre "
            "2011. II. - Les dispositions du titre II entrent en vigueur le 1er "
            "septembre 2010."),
    "2010-1719": ("2011-01-01", "LEGIARTI000023400748", "JORFTEXT000023333539", "2010-12-31",
            "La ministre de l'économie, des finances et de l'industrie, le ministre du "
            "budget, des comptes publics, de la fonction publique et de la réforme de "
            "l'Etat, porte-parole du Gouvernement, et le secrétaire d'Etat auprès du "
            "ministre du budget, des comptes publics, de la fonction publique, et de la"
            " réforme de l'Etat, chargé de la fonction publique sont chargés, chacun en"
            " ce qui le concerne, de l'exécution du présent décret, qui entrera en "
            "vigueur au 1er janvier 2011 et sera publié au Journal officiel de la "
            "République française."),
    "2010-1720": ("2011-01-01", "LEGIARTI000023410103", "JORFTEXT000023333639", "2010-12-31",
            "La ministre de l'économie, des finances et de l'industrie, le ministre du "
            "budget, des comptes publics, de la fonction publique et de la réforme de "
            "l'Etat, porte-parole du Gouvernement, et le secrétaire d'Etat auprès du "
            "ministre du budget, des comptes publics, de la fonction publique et de la "
            "réforme de l'Etat, chargé de la fonction publique, sont chargés, chacun en"
            " ce qui le concerne, de l'exécution du présent décret, qui entrera en "
            "vigueur au 1er janvier 2011 et sera publié au Journal officiel de la "
            "République française."),
    # B7 : « prennent effet », quand le tableau dit l'entrée en vigueur, comme le n° 2011-1140.
    "2011-215": ("2011-03-01", "LEGIARTI000023632829", "JORFTEXT000023631790", "2011-02-27",
            "Les dispositions du présent décret prennent effet le premier jour du mois "
            "suivant celui de sa publication."),
    "2012-761": ("2012-06-01", "LEGIARTI000025855104", "JORFTEXT000025838289", "2012-05-10",
            "Le ministre de la défense et des anciens combattants, le garde des sceaux,"
            " ministre de la justice et des libertés, le ministre du travail, de "
            "l'emploi et de la santé, le ministre de l'éducation nationale, de la "
            "jeunesse et de la vie associative, la ministre du budget, des comptes "
            "publics et de la réforme de l'Etat, porte-parole du Gouvernement, et le "
            "ministre de la fonction publique sont chargés, chacun en ce qui le "
            "concerne, de l'exécution du présent décret, qui sera publié au Journal "
            "officiel de la République française et entrera en vigueur le premier jour "
            "du mois qui suit sa publication."),
    "2012-762": ("2012-06-01", "LEGIARTI000025855239", "JORFTEXT000025838383", "2012-05-10",
            "Le ministre de la défense et des anciens combattants, le garde des sceaux,"
            " ministre de la justice et des libertés, le ministre du travail, de "
            "l'emploi et de la santé, le ministre de l'éducation nationale, de la "
            "jeunesse et de la vie associative, la ministre du budget, des comptes "
            "publics et de la réforme de l'Etat, porte-parole du Gouvernement, et le "
            "ministre de la fonction publique sont chargés, chacun en ce qui le "
            "concerne, de l'exécution du présent décret, qui sera publié au Journal "
            "officiel de la République française et entrera en vigueur le premier jour "
            "du mois qui suit sa publication."),
    "2012-1002": ("2012-09-01", "LEGIARTI000026327475", "JORFTEXT000026326536", "2012-08-30",
            "Le ministre de l'économie et des finances, le ministre du redressement "
            "productif, la ministre de la réforme de l'Etat, de la décentralisation et "
            "de la fonction publique et le ministre délégué auprès du ministre de "
            "l'économie et des finances, chargé du budget, sont chargés, chacun en ce "
            "qui le concerne, de l'exécution du présent décret, qui sera publié au "
            "Journal officiel de la République française et entrera en vigueur le "
            "premier jour du mois suivant sa publication."),
    "2013-176": ("2013-03-01", "LEGIARTI000027115996", "JORFTEXT000027114846", "2013-02-28",
            "Les dispositions du présent décret entreront en vigueur le premier jour du"
            " mois suivant sa publication au Journal officiel de la République "
            "française."),
    "2013-875": ("2013-10-01", "LEGIARTI000027998176", "JORFTEXT000027996887", "2013-09-29",
            "Les dispositions du présent décret entreront en vigueur le premier jour du"
            " mois suivant sa publication au Journal officiel de la République "
            "française."),
    "2013-974": ("2013-11-01", "LEGIARTI000028140167", "JORFTEXT000028138788", "2013-10-31",
            "Le présent décret entrera en vigueur le premier jour du mois suivant sa "
            "publication."),
    # B7 : l'art. 12, que la clause réserve, fixe les échelons « A compter du 1er janvier
    # 2020 » ; le tableau est à l'art. 21.
    "2016-2008": ("2017-01-01", "LEGIARTI000033792417", "JORFTEXT000033759014", "2016-12-31",
            "Sous réserve des dispositions de l'article 12,le présent décret entre en "
            "vigueur le 1er janvier 2017."),
    # B7 : le tableau est à l'art. 7, que la clause n'excepte pas.
    "2018-648": ("2017-01-01", "LEGIARTI000037246485", "JORFTEXT000037245707", "2018-07-25",
            "Les dispositions du présent décret entrent en vigueur le 1er janvier 2017,"
            " à l'exception de celles des articles 1er, 5 et 6."),
}

#: La règle d'entrée en vigueur d'un texte publié au Journal officiel depuis le 1er juin
#: 2004 : code civil, art. 1er, dans sa rédaction issue de l'ordonnance n° 2004-164 du 20
#: février 2004, art. 1er (JORF du 21 février 2004), « En vigueur depuis le 01 juin 2004 »,
#: lu à Légifrance le 6 novembre 2026 (LEGIARTI000006419280 ; aucun des deux index du dépôt
#: ne l'a). Ses trois alinéas, mis bout à bout (action 158, B7).
ARTICLE_1ER_DU_CODE_CIVIL = (
    "Les lois et, lorsqu'ils sont publiés au Journal officiel de la République française, les "
    "actes administratifs entrent en vigueur à la date qu'ils fixent ou, à défaut, le "
    "lendemain de leur publication. Toutefois, l'entrée en vigueur de celles de leurs "
    "dispositions dont l'exécution nécessite des mesures d'application est reportée à la date "
    "d'entrée en vigueur de ces mesures. En cas d'urgence, entrent en vigueur dès leur "
    "publication les lois dont le décret de promulgation le prescrit et les actes "
    "administratifs pour lesquels le Gouvernement l'ordonne par une disposition spéciale. Les "
    "dispositions du présent article ne sont pas applicables aux actes individuels.")

#: La clause que ni l'index LEGI ni l'index JORF n'ont (filtre thématique), lue à
#: Légifrance le 6 novembre 2026, page de l'article au JORF (action 158, B7) : le numéro →
#: la date, l'article au JORF, le texte signé et le jour de sa publication (index JORF), les
#: mots. La notice du texte signé, à l'index, donne la même date.
ENTREES_LUES_A_LEGIFRANCE = {
    "2012-1139": ("2012-11-01", "JORFARTI000026477172", "JORFTEXT000026477051", "2012-10-11",
                  "Les dispositions du présent décret entrent en vigueur le premier jour du "
                  "mois suivant celui de sa publication au Journal officiel de la République "
                  "française."),  # art. 68
    "2015-363": ("2015-04-01", "JORFARTI000030419590", "JORFTEXT000030419563", "2015-03-31",
                 "Le présent décret entre en vigueur le premier jour du mois qui suit sa "
                 "publication."),  # art. 14
}

#: Le décret qui ne fixe pas son entrée en vigueur, lu en entier (aucun article ne dit
#: quand il s'applique), dont le tableau se date de cette entrée en vigueur : le lendemain de
#: sa publication (``ARTICLE_1ER_DU_CODE_CIVIL``) (action 158, B7). Le numéro → la date, le
#: texte signé et le jour de sa publication, lu au JORF (DATE_PUBLI).
LENDEMAINS_DE_PUBLICATION = {
    "2007-835": ("2007-05-14", "JORFTEXT000000793379", "2007-05-13"),
    "2010-647": ("2010-06-14", "JORFTEXT000022337185", "2010-06-13"),
    "2011-489": ("2011-05-06", "JORFTEXT000023947061", "2011-05-05"),
    "2011-744": ("2011-06-30", "JORFTEXT000024269791", "2011-06-29"),
    "2011-1139": ("2011-09-24", "JORFTEXT000024580227", "2011-09-23"),
    "2012-78": ("2012-01-26", "JORFTEXT000025195530", "2012-01-25"),
    "2012-229": ("2012-02-19", "JORFTEXT000025376677", "2012-02-18"),
    "2013-489": ("2013-06-13", "JORFTEXT000027534080", "2013-06-12"),
    "2013-1173": ("2013-12-20", "JORFTEXT000028339653", "2013-12-19"),
    "2014-71": ("2014-02-01", "JORFTEXT000028539091", "2014-01-31"),
    "2015-1792": ("2015-12-31", "JORFTEXT000031733312", "2015-12-30"),
    "2016-1177": ("2016-09-01", "JORFTEXT000033076677", "2016-08-31"),
    "2019-1160": ("2019-11-11", "JORFTEXT000039357806", "2019-11-10"),
}

#: Le tableau que le texte ne date pas d'une seule lecture : effet reste vide (l'entrée en
#: vigueur de l'article, au LEGI) ; l'article → les deux lectures (action 158, B7).
NON_TRANCHES = {
    "LEGIARTI000006413884": "n° 2005-1132, art. 18 (« A compter de la date de publication du "
                            "présent décret ») : le jour du JO, le 10 septembre 2005, ou le "
                            "lendemain, le 11, son entrée en vigueur (il n'en fixe pas)",
    "LEGIARTI000006414364": "n° 2006-8, art. 32 (« à la date de publication du présent "
                            "décret ») : le 5 janvier 2006, jour du JO, ou le 6, son entrée en "
                            "vigueur (il n'en fixe pas)",
    "LEGIARTI000006414365": "n° 2006-8, art. 33 : comme l'art. 32",
    "LEGIARTI000022755950": "n° 2010-989, art. 26 (« A la date d'entrée en vigueur du présent "
                            "décret »), au chapitre III : le 1er septembre 2010 (chapitres Ier et "
                            "III, art. 36) ou le 1er janvier 2011 (chapitre II)",
    "LEGIARTI000022007850": "n° 2010-302, art. 9 : « la date d'entrée en vigueur du décret "
                            "portant inscription de leur corps » à son annexe, une date par "
                            "corps, qu'un autre décret fixe",
}

#: Le tableau que le lecteur a mal découpé, laissé sans date (action 158, B7) : la ligne du
#: n° 2004-1439, art. 23 (version du 2023-08-01), joint la phrase du I (« A la date de
#: l'entrée en vigueur du décret n° 2023-676 ») et le tableau du II (« Au 1er janvier 2024,
#: les brigadiers-chefs de classe normale, les brigadiers-chefs de classe supérieure et les
#: majors sont reclassés ») ; le tableau du I n'est pas lu. La date du I serait le 1er août
#: 2023 (n° 2023-676, art. 21, LEGIARTI000047905418, JO du 29 juillet 2023), celle du II le
#: 1er janvier 2024 : ni l'une ni l'autre ne s'écrit avant que le lecteur sépare les deux.
A_RELIRE = {
    "LEGIARTI000047908641": "n° 2004-1439, art. 23 : la phrase du I, le tableau du II",
}

#: L'article du tableau → le numéro de son décret dans ``ENTREES_EN_VIGUEUR``,
#: ``ENTREES_LUES_A_LEGIFRANCE`` ou ``LENDEMAINS_DE_PUBLICATION``.
DATES_DU_DECRET = {
    "LEGIARTI000006508227": "98-809",  # art. 10
    "LEGIARTI000024477660": "2011-964",  # art. 21
    "LEGIARTI000024477662": "2011-964",  # art. 22
    "LEGIARTI000024581630": "2011-1140",  # art. 21
    "LEGIARTI000024581632": "2011-1140",  # art. 22
    "LEGIARTI000024847333": "2011-1642",  # art. 18
    "LEGIARTI000024847335": "2011-1642",  # art. 19
    "LEGIARTI000025072785": "2011-1987",  # art. 24
    "LEGIARTI000025073303": "2011-1988",  # art. 22
    "LEGIARTI000025378134": "2012-230",  # art. 19
    "LEGIARTI000025546325": "2012-379",  # art. 16
    "LEGIARTI000026237250": "2012-924",  # art. 19
    "LEGIARTI000026311271": "2012-984",  # art. 21
    "LEGIARTI000026428541": "2012-1099",  # art. 16
    "LEGIARTI000026508372": "2012-1161",  # art. 35
    "LEGIARTI000026797412": "2012-1419",  # art. 6
    "LEGIARTI000026796776": "2012-1420",  # art. 26
    "LEGIARTI000027962708": "2013-830",  # art. 16
    "LEGIARTI000028540405": "2014-75",  # art. 6
    "LEGIARTI000028540761": "2014-76",  # art. 8
    "LEGIARTI000028540763": "2014-76",  # art. 9
    "LEGIARTI000028540765": "2014-76",  # art. 10
    "LEGIARTI000028540767": "2014-76",  # art. 11
    "LEGIARTI000028540858": "2014-79",  # art. 6
    "LEGIARTI000028541518": "2014-81",  # art. 6
    "LEGIARTI000029384142": "2014-922",  # art. 16
    "LEGIARTI000029563606": "2014-1164",  # art. 10
    "LEGIARTI000030371569": "2015-303",  # art. 24
    "LEGIARTI000031317649": "2015-1275",  # art. 35
    "LEGIARTI000032128528": "2016-219",  # art. 6
    "LEGIARTI000032128530": "2016-219",  # art. 7
    "LEGIARTI000032276852": "2016-336",  # art. 27
    "LEGIARTI000033792187": "2016-2002",  # art. 23
    "LEGIARTI000034036512": "2017-180",  # art. 20
    "LEGIARTI000034082758": "2017-233",  # art. 17
    "LEGIARTI000042368604": "2020-1174",  # art. 25
    "LEGIARTI000042368924": "2020-1175",  # art. 25
    "LEGIARTI000044804888": "2021-1818",  # art. 7
    "LEGIARTI000044804890": "2021-1818",  # art. 8
    "LEGIARTI000044804892": "2021-1818",  # art. 9
    "LEGIARTI000044799836": "2021-1826",  # art. 6
    "LEGIARTI000044804028": "2021-1834",  # art. 3
    "LEGIARTI000045540040": "2022-516",  # art. 4
    "LEGIARTI000046121299": "2022-1093",  # art. 9
    "LEGIARTI000046243448": "2022-1200",  # art. 6
    "LEGIARTI000046243452": "2022-1200",  # art. 8
    "LEGIARTI000046243454": "2022-1200",  # art. 9
    "LEGIARTI000046243822": "2022-1206",  # art. 4
    "LEGIARTI000046243824": "2022-1206",  # art. 5
    "LEGIARTI000046243826": "2022-1206",  # art. 6
    "LEGIARTI000046243983": "2022-1209",  # art. 2
    "LEGIARTI000047766733": "2023-527",  # art. 10
    "LEGIARTI000047917292": "2023-709",  # art. 28
    "LEGIARTI000048461728": "2023-1092",  # art. 3
    "LEGIARTI000048842644": "2023-1336",  # art. 9
    "LEGIARTI000049063861": "2024-51",  # art. 27
    "LEGIARTI000049063907": "2024-51",  # art. 18
    "LEGIARTI000049350385": "2024-282",  # art. 9
    "LEGIARTI000052461401": "2025-1002",  # art. 11
    "LEGIARTI000052461512": "2025-1003",  # art. 7
    "LEGIARTI000053185999": "2025-1327",  # art. 31
    "LEGIARTI000053186007": "2025-1327",  # art. 35
    # Action 158, B7.
    "LEGIARTI000006413791": "2005-939",  # art. 20
    "LEGIARTI000006414050": "2005-1304",  # art. 36
    "LEGIARTI000022751573": "2010-982",  # art. 33
    "LEGIARTI000023400750": "2010-1719",  # art. 14
    "LEGIARTI000023410135": "2010-1720",  # art. 14
    "LEGIARTI000023632819": "2011-215",  # art. 13
    "LEGIARTI000025855090": "2012-761",  # art. 10
    "LEGIARTI000025855187": "2012-762",  # art. 22
    "LEGIARTI000026327465": "2012-1002",  # art. 8
    "LEGIARTI000027115984": "2013-176",  # art. 27
    "LEGIARTI000027998167": "2013-875",  # art. 10
    "LEGIARTI000028140216": "2013-974",  # art. 23
    "LEGIARTI000033792401": "2016-2008",  # art. 21
    "LEGIARTI000037246483": "2018-648",  # art. 7
    "LEGIARTI000026477976": "2012-1139",  # art. 50
    "LEGIARTI000030420449": "2015-363",  # art. 12
    "LEGIARTI000006264680": "2007-835",  # art. 4
    "LEGIARTI000022338220": "2010-647",  # art. 12
    "LEGIARTI000023947863": "2011-489",  # art. 24
    "LEGIARTI000024272771": "2011-744",  # art. 11
    "LEGIARTI000024581275": "2011-1139",  # art. 18
    "LEGIARTI000024581277": "2011-1139",  # art. 19
    "LEGIARTI000025196191": "2012-78",  # art. 11
    "LEGIARTI000025377504": "2012-229",  # art. 18
    "LEGIARTI000027535136": "2013-489",  # art. 23
    "LEGIARTI000028342387": "2013-1173",  # art. 17
    "LEGIARTI000028540018": "2014-71",  # art. 12
    "LEGIARTI000028540020": "2014-71",  # art. 13
    "LEGIARTI000031826959": "2015-1792",  # art. 11
    "LEGIARTI000033078337": "2016-1177",  # art. 22
    "LEGIARTI000039363229": "2019-1160",  # art. 5
}


def effet_du_tableau(article: str, intro: str) -> str:
    """La date du reclassement : celle que la phrase écrit, sinon celle qu'un autre
    article du décret donne au tableau, ou l'entrée en vigueur que le décret fixe, ou le
    lendemain de sa publication s'il n'en fixe pas, sinon rien (l'entrée en vigueur de
    l'article)."""
    numero = DATES_DU_DECRET.get(article, "")
    return (date_effet(intro) or DATES_D_UN_AUTRE_ARTICLE.get(article, ("",))[0]
            or (ENTREES_EN_VIGUEUR.get(numero) or ENTREES_LUES_A_LEGIFRANCE.get(numero)
                or LENDEMAINS_DE_PUBLICATION.get(numero) or ("",))[0])


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
                "qu'un autre article du décret donne, ou, quand la phrase dit l'entrée en "
                "vigueur du décret, celle que le décret fixe, ou, s'il n'en fixe pas et qu'il "
                "est publié depuis le 1er juin 2004, le lendemain de sa publication ; vide : "
                "l'entrée en vigueur de l'article, debut), la phrase qui l'annonce et "
                "son en-tête. La règle, code civil, art. 1er, dans sa rédaction issue de "
                "l'ordonnance n° 2004-164 du 20 février 2004, en vigueur depuis le 1er juin "
                "2004 (LEGIARTI000006419280, lu à Légifrance) : « " + ARTICLE_1ER_DU_CODE_CIVIL
                + " » Quatre effets précèdent la publication de leur décret, et le texte "
                "les date ainsi : n° 98-809 (1er août 1995, JO du 12 septembre 1998), n° 98-896 "
                "(1er août 1996, JO du 9 octobre 1998), n° 2017-180 (1er janvier 2017, JO du 15 "
                "février 2017), n° 2018-648 (1er janvier 2017, JO du 25 juillet 2018) ; la "
                "donnée date ce que le texte date, sans examiner la validité "
                "d'un effet antérieur à la publication. Pour le n° 98-896, art. 8, la donnée ne "
                "porte que la date du tableau : l'élargissement du n° 2002-378 (JO du 21 mars "
                "2002), qui ôte « en fonctions à la date du présent décret », n'est pas dans la "
                "donnée ; pour l'agent que cette condition excluait, deux lectures, le 1er août "
                "1996 ou l'entrée en vigueur du n° 2002-378, et le texte n'en écrit aucune. "
                "Sept tableaux, que le texte ne date pas d'une seule lecture, gardent effet "
                "vide : n° 2005-1132, art. 18, et n° 2006-8, art. 32 et 33 (« à la date de "
                "publication du présent décret » : le jour du JO, ou le lendemain, l'entrée en "
                "vigueur de ces décrets, qui n'en fixent pas) ; n° 2010-989, art. 26 (« la date "
                "d'entrée en vigueur du présent décret », dont les chapitres Ier et III entrent "
                "en vigueur le 1er septembre 2010, le chapitre II le 1er janvier 2011) ; n° "
                "2010-302, art. 9 (une date par corps, que fixe le décret qui l'inscrit à son "
                "annexe). Le tableau du n° 2004-1439, art. 23 (version du 2023-08-01), joint "
                "la phrase du I et le tableau du II (« Au 1er janvier 2024 ») : effet vide, à "
                "relire.",
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
