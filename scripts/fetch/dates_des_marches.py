#!/usr/bin/env python3
"""La date d'effet de chaque marche de l'IPP, lue dans le document qui la dit.

    python scripts/fetch/dates_des_marches.py

Importé par ``ipp_prelevements_sociaux.py``, qui imprime ce qu'il trouve à
chaque réécriture de ``data/reference/legislation/prelevements_historiques.yaml``
(action 138, étape 9).

POURQUOI. L'ancrage relie la marche au texte que l'IPP cite, à sa date de
publication au *Journal officiel* : il ne dit pas que la date de la marche est
celle où ce texte fait valoir la règle. Une date fausse ne se voit pas plus
qu'une marche qui manque : la marche des collectivités de 1991 avançait de six
mois, et rien ne rougissait. Cette garde nomme, pour chaque marche de l'IPP, le
document des index de la DILA (``dila_index.py``) qui dit sa date — un article,
la notice ou le titre d'un texte du JORF, une version d'article de LEGI —, et
les mots qui la disent, qu'un test y relit
(``tests/test_prelevements_historiques.py``) ; ou pourquoi elle ne se lit pas.

CE QU'ELLE A VU. Là où un document de l'index la dit, la date de l'IPP est
juste, sauf deux fois : le seuil de la contribution de solidarité de mars et de
septembre 1988, que l'IPP, qui le tient du Fonds de solidarité, date du 21 et
du 23 du mois, quand la valeur du point qui le fait change le 1er
(``CORRECTIONS`` du récupérateur). Ses autres marches d'avant 1989 ont un jour
qui n'est pas une date : un compteur. Le document qui date une marche n'est
pas toujours celui qu'elle cite : la suppression du veuvage est datée par la
loi n° 2003-775, et non par le décret n° 2004-858 ; les seuils que l'IPP cite
d'un décret absent de l'index ou mal numéroté, par l'article 3 du décret
n° 85-1148, dont LEGI garde chaque valeur avec sa date.

CE QU'ELLE NE DIT PAS. Une date lue l'est par des mots relus, non par un juge :
le test vérifie qu'ils sont dans le document et qu'ils disent la date de la
marche (:func:`dates_dites`), non qu'ils visent la bonne série ; c'est la
lecture, consignée dans la note de la feuille de route, qui l'a établi. Le
modèle compte les mois au premier jour : une date du 22 décembre ou du
31 mars ne change aucun mois de celle du 1er janvier ou du 1er avril.
"""

from __future__ import annotations

import datetime as dt
import re
import sys
import unicodedata
from collections.abc import Iterable
from pathlib import Path

import yaml

DONNEE = (Path(__file__).resolve().parents[2] / "data" / "reference" / "legislation"
          / "prelevements_historiques.yaml")

# -- les dates que disent des mots ----------------------------------------------

_MOIS = ("janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout",
         "septembre", "octobre", "novembre", "decembre")
#: Un jour et un mois, en lettres (« 1er juillet 1991 », « 1 er janvier 1998 »)
#: ou en chiffres (« 01-07-1987 », « 01-08 »), l'année en option.
_DATE = re.compile(r"\b(?:(1 ?er|\d{1,2}) (" + "|".join(_MOIS) + r")(?: (\d{4}))?"
                   r"|(\d{2})[-/](\d{2})(?:[-/](\d{4}))?)\b")
_ANNEE = re.compile(r"\b(19\d\d|20\d\d)\b")
#: Une année entière : « au titre de l'année 1990 », « de l'exercice 2007 ».
_ANNEE_ENTIERE = re.compile(r"\b(?:annee|exercice) (19\d\d|20\d\d)\b")
#: Ce qui fait d'une date la veille de l'effet : « postérieures au 30-06-1980 »,
#: « jusqu'au 31-12-1979 ».
_VEILLE = re.compile(r"(?:posterieure?s? au|jusqu.au) $")


def _plat(mots: str) -> str:
    """Les mots sans accents, en minuscules, aux blancs réduits."""
    sans = "".join(c for c in unicodedata.normalize("NFD", mots)
                   if unicodedata.category(c) != "Mn")
    return " ".join(sans.lower().split())


def dates_dites(mots: str) -> set[str]:
    """Les dates que disent des mots, au format ISO : chaque date écrite ; le
    lendemain de celle que précède « postérieures au » ou « jusqu'au » ; pour un
    jour et un mois sans année, l'année écrite la plus proche avant eux, sinon
    après ; le 1er janvier d'une année ou d'un exercice nommés."""
    texte = _plat(mots)
    annees = [(trouve.start(), int(trouve.group(1))) for trouve in _ANNEE.finditer(texte)]
    dites = {f"{annee}-01-01" for annee in _ANNEE_ENTIERE.findall(texte)}
    for trouve in _DATE.finditer(texte):
        jour_l, mois_l, annee_l, jour_c, mois_c, annee_c = trouve.groups()
        if jour_l:
            jour = 1 if "er" in jour_l else int(jour_l)
            mois, annee = _MOIS.index(mois_l) + 1, annee_l
        else:
            jour, mois, annee = int(jour_c), int(mois_c), annee_c
        if annee is None:
            avant = [a for position, a in annees if position < trouve.start()]
            apres = [a for position, a in annees if position > trouve.end()]
            if not avant and not apres:
                continue
            annee = avant[-1] if avant else apres[0]
        try:
            date = dt.date(int(annee), mois, jour)
        except ValueError:
            continue
        dites.add(date.isoformat())
        if _VEILLE.search(texte[:trouve.start()]):
            dites.add((date + dt.timedelta(days=1)).isoformat())
    return dites


# -- les dates lues --------------------------------------------------------------

_CSG = ("csg_taux_plein", "csg")
_CSG_ET_TAUX_REDUIT = ("csg_taux_plein", "csg_taux_reduit", "csg")
_RETRAITES = ("maladie_regime_general", "maladie_complementaires")
_AGENTS = ("maladie_etat", "maladie_collectivites")
_INDEPENDANTS = ("maladie_artisans_commercants", "maladie_professions_liberales")
_INDEPENDANTS_ET_RETRAITES = ("maladie_independants", *_INDEPENDANTS)

#: Les marches de l'IPP dont un document de l'index dit la date : (date, séries,
#: document, mots). Le document est un article, la notice ou le titre d'un texte
#: du JORF, ou une version d'article de LEGI ; ses mots, tels que l'index les
#: écrit, blancs réduits. Une série nomme ses marches des pensions et des
#: salaires ensemble : la CRDS a les mêmes.
DATES_LUES: tuple[tuple[str, tuple[str, ...], str, str], ...] = (
    ("1967-10-01", ("maladie_prive",), "LEGIARTI000006761087",
     "est applicable aux rémunérations ou gains versés aux travailleurs salariés ou assimilés"
     " à compter du 1er octobre 1967"),
    ("1974-10-01", _INDEPENDANTS_ET_RETRAITES, "LEGIARTI000006762464",
     "Les dispositions du présent décret sont applicables à compter du 1er octobre 1974"),
    ("1976-10-01", _INDEPENDANTS_ET_RETRAITES, "JORFTEXT000000507288",
     "MODIFICATION DES ART. 3 ET 7 DU DECRET 74810 DU 28-09-1974, A COMPTER DU 01-10-1976"),
    ("1977-10-01", _INDEPENDANTS_ET_RETRAITES, "JORFTEXT000000864145",
     "MODIFICATION, A COMPTER DU 01-10-1977 DES ART. 3, 4 ET 7 DU DECRET 74810"),
    ("1979-01-01", _AGENTS, "JORFTEXT000000697278",
     "MODIFICATION DE L'ART. 2 DU DECRET 67850 DU 30-09-1967 A COMPTER DU 01-01-1979 ET "
     "JUSQU'AU 31-12-1979"),
    ("1979-04-01", _INDEPENDANTS, "JORFTEXT000000874409",
     "LES DISPOSITIONS DU PRESENT DECRET ENTRENT EN VIGUEUR LE 01-04-1979"),
    ("1979-08-01", ("maladie_prive",), "JORFTEXT000000518706",
     "DU 01-08 AU 31-12-1979"),
    ("1980-01-01", ("maladie_prive",), "JORFTEXT000000518706",
     "ET DU 01-01-1980 AU 31-01-1981"),
    ("1980-01-01", _AGENTS, "JORFTEXT000000697278",
     "ET NOUVELLE MODIFICATION A COMPTER DU 01-01-1980"),
    ("1980-07-01", _RETRAITES, "JORFTEXT000000328902",
     "LES DISPOSITIONS DU PRESENT DECRET S'APPLIQUENT AUX AVANTAGES DE RETRAITE VERSES AU "
     "TITRE DES PERIODES POSTERIEURES AU 30-06-1980"),
    ("1981-01-01", ("veuvage_prive",), "JORFTEXT000000861526",
     "FIXE A COMPTER DU 01-01-1981"),
    ("1981-04-01", ("maladie_independants",), "JORFTEXT000000503013",
     "TAUX DE LA COTISATION DUE SUR LES PENSIONS OU ALLOCATIONS:10%. LES DISPOSITIONS DU "
     "PRESENT DECRET SONT APPLICABLES AU 01-04-1981"),
    ("1981-10-01", _INDEPENDANTS_ET_RETRAITES, "JORFTEXT000000519483",
     "TRAVAILLEURS NON SALARIES NON AGRICOLES A COMPTER DU 01-10-1981"),
    ("1982-04-01", ("famille",), "JORFTEXT000000701319",
     "APPLICABLE AUX COTISATIONS VENANT A ECHEANCE A COMPTER DU 01-04-1982"),
    ("1982-11-06", ("chomage_prive",), "JORFTEXT000000331503",
     "SUR LES REMUNERATIONS VERSEES A PARTIR DU 06-11-1982"),
    ("1982-12-01", ("solidarite_public",), "JORFTEXT000000883611",
     "barème B relatif aux traitements bruts annuels soumis aux retenues pour pensions à "
     "compter du 1er décembre 1982"),
    ("1983-01-01", ("famille",), "JORFTEXT000000703768",
     "VENANT A ECHEANCE A COMPTER DU 01-01-1983"),
    ("1984-10-01", ("maladie_artisans_commercants",), "JORFTEXT000000873004",
     "APPLICATION A COMPTER DU 01-10-1984"),
    ("1985-07-01", ("chomage_prive",), "JORFTEXT000000497155",
     "COTISATION SALARIALE: 0,2 POINT AU 01-07-1985"),
    ("1987-07-01", (*_RETRAITES, "maladie_prive"), "JORFTEXT000000516870",
     "TAUX DES COTISATIONS DES ASSURES DU 01-07-1987 AU 30-06-1988"),
    ("1987-07-01", _INDEPENDANTS_ET_RETRAITES, "JORFTEXT000000700929",
     "SUR LEURS REVENUS SALARIES DU 01-07-1987 AU 30-06-1988. LA COTISATION AU REGIME "
     "D'ASSURANCE MALADIE DUE SUR LES RETRAITES DE NON SALARIES EST PORTEE DE 3% A 3,4%"),
    ("1988-07-01", _AGENTS, "JORFTEXT000000693584",
     "TRAITEMENTS OU SOLDES ET PENSIONS DE VIEILLESSE VERSES A COMPTER DU 01-07-1988"),
    ("1989-01-01", ("famille",), "JORFTEXT000000332517",
     "DES TAUX DES COTISATIONS DUES AU TITRE DE L'ANNEE 1989 PAR LES EMPLOYEURS ET "
     "TRAVAILLEURS INDEPENDANTS"),
    ("1989-04-01", _INDEPENDANTS, "JORFTEXT000000881840",
     "PRENANT EFFET POUR LE CALCUL DE LA COTISATION DUE AU TITRE DE L'ECHEANCE SEMESTRIELLE "
     "DU 01-04-1989. ENTREE EN VIGUEUR: 01-04-1989"),
    ("1989-09-01", ("solidarite_public",), "LEGIARTI000006454430",
     "est fixée à 28 129 F à compter du 1er septembre 1989"),
    ("1990-01-01", ("famille",), "JORFARTI000001928720",
     "les taux de cotisations d'allocations familiales dues au titre de l'année 1990 par les "
     "employeurs et travailleurs indépendants"),
    ("1990-01-01", ("solidarite_public",), "JORFARTI000001124372",
     "est fixée à 28270 F à compter du 1er janvier 1990"),
    ("1990-04-01", ("solidarite_public",), "LEGIARTI000006454432",
     "est fixée à 28 607 F à compter du 1er avril 1990"),
    ("1990-12-01", ("solidarite_public",), "JORFARTI000001563880",
     "est fixée à 28973 F à compter du 1er décembre 1990"),
    ("1991-02-01", ("famille",), "JORFARTI000000986494",
     "s'appliquent pour les cotisations dues au titre de la période postérieure au 1er "
     "février 1991. Les dispositions du décret no 90-288 du 30 mars 1990 continuent à "
     "s'appliquer jusqu'à cette date"),
    ("1991-07-01", ("maladie_prive",), "JORFARTI000001760118",
     "décret est applicable aux rémunérations et gains versés à compter du 1er juillet 1991"),
    ("1991-07-01", ("maladie_etat",), "JORFARTI000001566429",
     "Le présent décret est applicable aux gains, rémunérations, traitements ou soldes versés"
     " à compter du 1er juillet 1991"),
    ("1991-08-01", ("solidarite_public",), "JORFARTI000001568120",
     "est fixée à 29118 F à compter du 1er août 1991"),
    ("1991-11-01", ("solidarite_public",), "JORFARTI000001568120",
     "puis à 29408 F à compter du 1er novembre 1991"),
    ("1992-02-01", ("solidarite_public",), "JORFARTI000001546530",
     "est fixée à 29784F à compter du 1er février 1992"),
    ("1992-04-01", _INDEPENDANTS, "JORFARTI000001372694",
     "pour les cotisations dues à l'échéance du 1er avril 1992"),
    ("1992-10-01", ("solidarite_public",), "JORFARTI000001769165",
     "est fixée à 30 190 F à compter du 1er octobre 1992"),
    ("1993-02-01", ("solidarite_public",), "JORFARTI000001514294",
     "est fixée à 30 711 F à compter du 1er février 1993"),
    ("1993-07-01", _CSG, "JORFARTI000001772936",
     "est porté à 2,4 p. 100 à compter du 1er juillet 1993"),
    ("1994-01-01", ("solidarite_public",), "LEGIARTI000006454438",
     "est fixée à 30 926 F à compter du 1er janvier 1994"),
    ("1994-08-01", ("solidarite_public",), "JORFARTI000001165190",
     "est fixée à 31 080 F à compter du 1er août 1994"),
    ("1994-12-01", ("solidarite_public",), "LEGIARTI000006454440",
     "est fixée à 31 422 F à compter du 1er décembre 1994"),
    ("1995-03-01", ("solidarite_public",), "JORFARTI000001589737",
     "est fixée à 31 799 F à compter du 1er mars 1995"),
    ("1995-07-01", ("maladie_artisans_commercants",), "JORFARTI000001398418",
     "Les dispositions du présent décret sont applicables à compter du 1er juillet 1995"),
    ("1995-11-01", ("solidarite_public",), "JORFARTI000001593104",
     "est fixée à 32 244 F à compter du 1er novembre 1995"),
    ("1996-01-01", _RETRAITES, "JORFARTI000001982702",
     "pour les pensions dues à compter du 1er janvier 1996"),
    ("1996-02-01", ("crds",), "JORFARTI000002177845",
     "perçus du 1er février 1996 au 31 janvier 2009 par les personnes physiques désignées à "
     "l'article L. 136-1 du même code"),
    ("1997-01-01", _CSG_ET_TAUX_REDUIT, "JORFARTI000002387477",
     "en tant qu'elles concernent la contribution visée à l'article L. 136-1 du code de la "
     "sécurité sociale, sont applicables aux revenus versés à compter du 1er janvier 1997"),
    ("1997-01-01", (*_RETRAITES, "maladie_independants", "maladie_prive"), "JORFARTI000002386284",
     "s'appliquent aux rémunérations, gains, pensions et allocations versés à compter du 1er "
     "janvier 1997"),
    ("1997-01-01", _INDEPENDANTS, "JORFARTI000002386284",
     "en ce qui concerne les revenus professionnels, s'appliquent aux revenus perçus à "
     "compter du 1er janvier 1997"),
    ("1997-01-01", ("chomage_prive",), "JORFARTI000001797659",
     "entrent en application à compter du 1er janvier 1997"),
    ("1997-01-01", _AGENTS, "JORFARTI000001991998",
     "les dispositions du présent décret s'appliquent aux rémunérations, gains, pensions et "
     "allocations versés à compter du 1er janvier 1997"),
    ("1997-03-01", ("solidarite_public",), "JORFARTI000001412767",
     "est fixée à 32 405 F à compter du 1er mars 1997"),
    ("1997-10-01", ("solidarite_public",), "JORFARTI000001414499",
     "est fixée à 32 567 F à compter du 1er octobre 1997"),
    ("1998-01-01", _CSG_ET_TAUX_REDUIT, "JORFARTI000002306091",
     "En ce qu'elles concernent la contribution mentionnée à l'article L. 136-1 du code de la"
     " sécurité sociale, aux revenus perçus à compter du 1 er janvier 1998"),
    ("1998-01-01", (*_RETRAITES, "maladie_independants"), "JORFARTI000001346386",
     "s'appliquent aux rémunérations, gains, pensions et allocations versés à compter du 1er "
     "janvier 1998"),
    ("1998-01-01", _INDEPENDANTS, "JORFARTI000001346386",
     "en ce qui concerne les revenus professionnels s'appliquent aux revenus perçus à compter"
     " du 1er janvier 1998"),
    ("1998-01-01", ("maladie_prive", *_AGENTS), "JORFARTI000001032378",
     "les dispositions du présent décret s'appliquent aux rémunérations, gains, pensions et "
     "allocations versés à compter du 1er janvier 1998"),
    ("1998-01-01", ("solidarite_public",), "JORFARTI000001416432",
     "A compter du 1 er janvier 1998, sont exonérés du versement de la contribution de "
     "solidarité"),
    ("1998-04-01", ("solidarite_public",), "JORFARTI000001557414",
     "est fixée à 32 828 F à compter du 1er avril 1998"),
    ("1998-07-01", ("solidarite_public",), "JORFARTI000001168959",
     "Le décret du 23 décembre 1982 susvisé est modifié ainsi qu'il suit à compter du 1er "
     "juillet 1998"),
    ("1998-11-01", ("solidarite_public",), "JORFARTI000002089260",
     "est fixée à 32 990 F à compter du 1er novembre 1998"),
    ("1999-04-01", ("solidarite_public",), "JORFARTI000001818188",
     "est fixée à 33 155 F à compter du 1er avril 1999"),
    ("1999-07-01", ("solidarite_public",), "JORFARTI000002209233",
     "Le décret du 23 décembre 1982 susvisé est modifié ainsi qu'il suit à compter du 1er "
     "juillet 1999"),
    ("1999-12-01", ("solidarite_public",), "JORFARTI000001130980",
     "est fixée à 33 419 F à compter du 1er décembre 1999"),
    ("2000-12-01", ("solidarite_public",), "JORFARTI000001711931",
     "est fixée à 33 586 F à compter du 1er décembre 2000"),
    ("2001-01-01", ("chomage_prive",), "JORFARTI000002028258",
     "Le taux des contributions est fixé : - à 5,80 % à compter du 1er janvier 2001"),
    ("2001-01-01", _INDEPENDANTS, "JORFARTI000001256724",
     "maladie et maternité dues au titre des périodes d'activité postérieures au 31 décembre "
     "2000"),
    ("2001-05-01", ("solidarite_public",), "JORFARTI000002487322",
     "est fixée à 33 754 F à compter du 1er mai 2001"),
    ("2001-11-01", ("solidarite_public",), "JORFARTI000002434687",
     "est fixée à 33 990 F à compter du 1er novembre 2001"),
    ("2002-01-01", ("chomage_prive",), "JORFARTI000002028258",
     "- 5,60 % à compter du 1er janvier 2002"),
    ("2002-01-01", ("solidarite_public",), "JORFARTI000002434687",
     "est fixée à 5 181,75 Euro à compter du 1er janvier 2002"),
    ("2002-03-01", ("solidarite_public",), "JORFARTI000002443410",
     "est fixée à 5 212,84 EUR à compter du 1er mars 2002"),
    ("2002-12-01", ("solidarite_public",), "JORFARTI000001058105",
     "est fixée à 5 249,33 EUR à compter du 1er décembre 2002"),
    ("2004-01-01", ("solidarite_public",), "JORFARTI000001915530",
     "est fixée à 5 275,58 EUR à compter du 1er janvier 2004"),
    ("2004-07-01", ("veuvage_prive",), "JORFARTI000001072419",
     "Les dispositions des I à IV sont applicables à compter du 1er juillet 2004"),
    ("2005-01-01", _CSG, "JORFARTI000002058251",
     "En ce qui concerne la contribution mentionnée à l'article L. 136-1 du code de la "
     "sécurité sociale, aux revenus perçus à compter du 1er janvier 2005"),
    ("2005-02-01", ("solidarite_public",), "JORFARTI000001871570",
     "est fixée à 5 301,96 EUR à compter du 1er février 2005"),
    ("2005-07-01", ("solidarite_public",), "JORFARTI000002064055",
     "est fixée à 5 328,47 EUR à compter du 1er juillet 2005"),
    ("2005-11-01", ("solidarite_public",), "JORFARTI000001467510",
     "est fixée à 5 371,10 EUR à compter du 1er novembre 2005"),
    ("2006-07-01", ("solidarite_public",), "JORFARTI000002439927",
     "est fixée à 5 397,95 EUR à compter du 1er juillet 2006"),
    ("2006-11-01", ("solidarite_public",), "JORFARTI000001476703",
     "Le décret du 23 décembre 1982 susvisé est modifié ainsi qu'il suit à compter du 1er "
     "novembre 2006"),
    ("2007-01-01", ("maladie_artisans_commercants",), "JORFARTI000001086443",
     "Les dispositions du présent décret sont applicables aux cotisations exigibles à partir "
     "de l'exercice 2007"),
    ("2007-01-01", ("chomage_prive",), "JORFARTI000002277875",
     "Cette majoration cessera de s'appliquer à compter du 1er janvier 2007"),
    ("2007-02-01", ("solidarite_public",), "JORFARTI000001111230",
     "est fixée à 5 441,13 EUR à compter du 1er février 2007"),
    ("2008-03-01", ("solidarite_public",), "JORFARTI000018194403",
     "est fixée à 5 468,34 € à compter du 1er mars 2008"),
    ("2008-07-01", ("solidarite_public",), "JORFARTI000019108390",
     "Le décret du 23 décembre 1982 susvisé est modifié ainsi qu'il suit à compter du 1er "
     "juillet 2008"),
    ("2008-10-01", ("solidarite_public",), "JORFARTI000019564080",
     "est fixée à 5 484, 75 € à compter du 1er octobre 2008"),
    ("2009-07-01", ("solidarite_public",), "JORFARTI000020815923",
     "est fixée à 5 512, 17 € à compter du 1er juillet 2009"),
    ("2009-10-01", ("solidarite_public",), "JORFARTI000021089944",
     "est fixée à 5 528, 71 € à compter du 1er octobre 2009"),
    ("2010-07-01", ("solidarite_public",), "JORFARTI000022447564",
     "est fixée à 5 556, 35 € à compter du 1er juillet 2010"),
    ("2011-01-01", ("solidarite_public",), "JORFARTI000023417947",
     "Le décret du 23 décembre 1982 susvisé est modifié ainsi qu'il suit à compter du 1er "
     "janvier 2011"),
    ("2012-01-01", ("solidarite_public",), "JORFARTI000025135499",
     "Le décret du 23 décembre 1982 susvisé est modifié ainsi qu'il suit à compter du 1er "
     "janvier 2012"),
    ("2012-07-01", ("solidarite_public",), "JORFARTI000026149224",
     "Le décret du 23 décembre 1982 susvisé est modifié ainsi qu'il suit à compter du 1er "
     "juillet 2012"),
    ("2013-01-01", ("solidarite_public",), "JORFARTI000026924636",
     "Le décret du 23 décembre 1982 susvisé est modifié ainsi qu'il suit à compter du 1er "
     "janvier 2013"),
    ("2013-01-01", ("maladie_professions_liberales",), "JORFTEXT000026864962",
     "le présent décret est applicable à compter du 1er janvier 2013"),
    ("2013-04-01", ("casa",), "JORFARTI000026785476",
     "Le I s'applique aux pensions et allocations servies à compter du 1er avril 2013"),
    ("2014-01-01", ("famille",), "JORFARTI000028408321",
     "décret s'applique aux cotisations de sécurité sociale dues au titre des périodes "
     "courant à compter du 1er janvier 2014"),
    ("2015-01-01", ("famille",), "JORFARTI000029920905",
     "s'appliquent aux cotisations de sécurité sociale dues au titre des périodes courant à "
     "compter du 1er janvier 2015"),
    ("2016-07-01", ("solidarite_public",), "JORFARTI000032584299",
     "est fixée à 5 589,69 € à compter du 1er juillet 2016"),
    ("2017-02-01", ("solidarite_public",), "JORFARTI000032584306",
     "est fixée à 5 623,23 € à compter du 1er février 2017"),
    ("2018-01-01", _CSG, "JORFARTI000036339150",
     "pour les revenus d'activité, les revenus de remplacement et les sommes engagées ou "
     "produits réalisés à l'occasion des jeux, aux cotisations et contributions dues au titre"
     " des périodes intervenant à compter du 1er janvier 2018"),
    ("2018-01-01", ("chomage_prive",), "JORFARTI000036339150",
     "Pour l'année 2018, les contributions salariales prévues à l'article L. 5422-9 du code "
     "du travail sont prises en charge par l'Agence centrale des organismes de sécurité "
     "sociale, dans la limite des contributions salariales dues, à hauteur de : 1° 1,45 point"
     " au titre des contributions dues au titre des périodes courant entre le 1er janvier et "
     "le 30 septembre"),
    ("2018-01-01", ("maladie_prive",), "JORFARTI000036342365",
     "dues au titre des périodes courant à compter du 1er janvier 2018"),
    ("2018-01-01", ("solidarite_public",), "JORFARTI000036339320",
     "Le présent article s'applique aux revenus perçus à compter du 1er janvier 2018"),
    ("2018-01-01", ("famille",), "JORFARTI000036342574",
     "aux cotisations et aux contributions de sécurité sociale dues au titre des périodes "
     "courant à compter du 1er janvier 2018"),
    ("2018-10-01", ("chomage_prive",), "JORFARTI000036339150",
     "Pour l'année 2018, les contributions salariales prévues à l'article L. 5422-9 du code "
     "du travail sont prises en charge par l'Agence centrale des organismes de sécurité "
     "sociale, dans la limite des contributions salariales dues, à hauteur de : 1° 1,45 point"
     " au titre des contributions dues au titre des périodes courant entre le 1er janvier et "
     "le 30 septembre ; 2° 2,40 points au titre des contributions dues au titre des périodes "
     "courant à compter du 1er octobre"),
    ("2019-01-01", ("csg_taux_median",), "JORFARTI000037851902",
     "s'applique à compter du versement des revenus intervenant en mai 2019 et donne lieu à "
     "la même date à une régularisation pour la période courant depuis le 1er janvier 2019"),
)

#: Les raisons que plusieurs marches partagent.
_UNEDIC = "un accord de l'Unédic, que l'index n'a pas"
_NOTICE = "l'index n'en a que le titre ou la notice, qui ne disent pas de date"
_FDS = ("le seuil du Fonds de solidarité, sans texte : les décrets de rémunération "
        "d'avant 1985 ne sont pas dans les index")
_FDS_JOUR = (_FDS + " ; et le jour n'est pas une date, mais un compteur (4, 6, 7, 8, 10, 13…), "
             "quand les marches de 1988, que LEGI date, tombent le 1er du mois")

#: Les marches de l'IPP dont aucun document de l'index ne dit la date, et
#: pourquoi : (date, séries, raison).
DATES_NON_LUES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("1959-01-01", ("chomage_prive",), "la convention du 31 décembre 1958, " + _UNEDIC),
    ("1962-01-01", ("chomage_prive",), "une décision du conseil d'administration de l'Unédic"),
    ("1967-10-01", _AGENTS, "décret n° 67-850 : " + _NOTICE + " ; LEGI n'a pas ses versions "
                            "d'avant 1976"),
    ("1968-01-01", ("chomage_prive",), "sans référence chez l'IPP"),
    ("1969-01-01", ("chomage_prive",), "sans référence chez l'IPP"),
    ("1970-04-01", _INDEPENDANTS_ET_RETRAITES, "l'arrêté du 26 mars 1971, que l'index n'a pas"),
    ("1973-01-01", ("chomage_prive",), "une décision du bureau de l'Unédic"),
    ("1973-04-01", _INDEPENDANTS_ET_RETRAITES, "l'arrêté du 29 décembre 1972, que l'index n'a "
                                               "pas"),
    ("1974-01-01", ("chomage_prive",), "une décision du conseil d'administration de l'Unédic"),
    ("1974-04-01", ("famille",), "le décret n° 74-313, que l'index n'a pas"),
    ("1975-01-01", ("chomage_prive",), "une décision du conseil d'administration de l'Unédic"),
    ("1975-04-01", _INDEPENDANTS_ET_RETRAITES, "décret n° 75-85 : " + _NOTICE),
    ("1975-07-01", ("chomage_prive",), "une circulaire de l'Unédic"),
    ("1975-10-01", _INDEPENDANTS_ET_RETRAITES, "décret n° 75-710 : " + _NOTICE),
    ("1976-01-01", ("maladie_prive",), "décret n° 75-1273 : " + _NOTICE),
    ("1976-01-01", _AGENTS, "décret n° 75-1270 : " + _NOTICE),
    ("1976-10-01", ("maladie_prive",), "décret n° 76-894 : " + _NOTICE + " ; LEGI date du "
                                       "1er octobre 1976 la version de l'article 1er du décret "
                                       "n° 67-803 qu'il écrit (LEGIARTI000006761082)"),
    ("1976-10-01", _AGENTS, "décret n° 76-896 : " + _NOTICE),
    ("1977-01-01", ("chomage_prive",), "une circulaire de l'Unédic"),
    ("1978-01-01", ("chomage_prive",), "une circulaire de l'Unédic"),
    ("1978-05-01", ("chomage_prive",), "une circulaire de l'Unédic"),
    ("1979-01-01", ("maladie_prive",), "décret n° 78-1213 : " + _NOTICE),
    ("1979-04-01", ("chomage_prive",), "une circulaire de l'Unédic"),
    ("1981-11-01", _AGENTS, "décret n° 81-1015 : " + _NOTICE + " ; LEGI date du 14 novembre "
                            "1981, jour de sa publication, ses versions des articles 1er et 2 "
                            "du décret n° 67-850 (LEGIARTI000006770614), comme le décret "
                            "n° 81-1013 du même jour, « à compter de la date de sa "
                            "publication », pour le salarié du privé : à lire au fac-similé"),
    ("1982-01-01", ("veuvage_prive",), "loi n° 82-1 : l'index n'en a que la notice et des "
                                       "articles vides"),
    ("1982-11-01", ("solidarite_public",), _FDS),
    ("1983-01-01", ("solidarite_public",), _FDS),
    ("1983-04-04", ("solidarite_public",), _FDS_JOUR),
    ("1983-07-01", ("chomage_prive",), "le décret n° 83-553, que l'index n'a pas"),
    ("1983-07-06", ("solidarite_public",), _FDS_JOUR),
    ("1983-11-07", ("solidarite_public",), _FDS_JOUR),
    ("1984-01-08", ("solidarite_public",), _FDS_JOUR),
    ("1984-04-01", ("chomage_prive",), "l'ordonnance n° 84-198 et la convention du 24 février "
                                       "1984, que l'index n'a pas"),
    ("1984-04-10", ("solidarite_public",), _FDS_JOUR),
    ("1984-11-13", ("solidarite_public",), _FDS_JOUR),
    ("1985-02-14", ("solidarite_public",), _FDS_JOUR),
    ("1985-07-16", ("solidarite_public",), _FDS_JOUR),
    ("1985-09-01", ("maladie_independants",), "décret n° 85-852 : la notice fait débuter le "
                                              "prélèvement « sur les arrérages servis au "
                                              "30-09-1985 », sans dire de quels mois ; le "
                                              "1er septembre de l'IPP en fait ceux de septembre"),
    ("1985-11-01", ("chomage_prive",), "le protocole du 18 juillet 1985 et l'avenant du "
                                       "29 octobre 1985, " + _UNEDIC),
    ("1985-11-17", ("solidarite_public",), _FDS_JOUR),
    ("1986-02-18", ("solidarite_public",), _FDS_JOUR),
    ("1987-03-22", ("solidarite_public",), _FDS_JOUR),
    ("1987-05-23", ("solidarite_public",), _FDS_JOUR),
    ("1987-08-24", ("solidarite_public",), _FDS_JOUR),
    ("1988-01-01", ("chomage_prive",), "la convention du 19 novembre 1985 et l'accord du "
                                       "30 décembre 1987, " + _UNEDIC),
    ("1990-10-01", ("chomage_prive",), "le compromis du 25 juin 1990, " + _UNEDIC),
    ("1991-01-01", ("chomage_prive",), "la convention du 1er janvier 1990, agréée le 14 mai "
                                       "1990, que l'index n'a pas"),
    ("1991-02-01", _CSG, "loi n° 90-1168, articles 127 à 135 : les index n'en ont que les "
                         "articles 128 à 134, dont aucun ne date la contribution"),
    ("1991-02-01", ("solidarite_public",), "sans référence chez l'IPP : l'indice majoré de "
                                           "référence passe de 254 à 259, ce qu'aucun texte "
                                           "de l'index ne date"),
    ("1992-01-01", ("chomage_prive",), "le protocole du 5 décembre 1991 et ses avenants, "
                                       + _UNEDIC),
    ("1992-08-01", ("chomage_prive",), "le protocole du 18 juillet 1992 et ses avenants, "
                                       + _UNEDIC),
    ("1993-08-01", ("chomage_prive",), "la convention du 1er janvier 1993 et son avenant, "
                                       + _UNEDIC + " ; l'arrêté que l'ancrage trouve à la date "
                                       "de l'IPP (JORFTEXT000000359380) classe les pharmaciens "
                                       "inspecteurs de santé publique"),
    ("1995-04-01", _INDEPENDANTS, "décret n° 95-337 : il vaut « dès la date d'entrée en "
                                  "vigueur du présent décret » (article 6), publié le 31 mars "
                                  "1995 ; LEGI date de ce jour la version de D. 612-4 qu'il "
                                  "écrit"),
    ("1998-01-01", ("famille",), "loi n° 97-1164 : le rapport annexé annonce le déplafonnement "
                                 "des 0,5 point, et l'index n'a pas l'article qui le date"),
    ("2002-07-01", ("chomage_prive",), "l'avenant du 19 juin 2002 à la convention du "
                                       "1er janvier 2001, " + _UNEDIC),
    ("2003-01-01", ("chomage_prive",), "l'avenant du 27 décembre 2002 à la convention du "
                                       "1er janvier 2001, " + _UNEDIC),
    ("2006-01-01", ("chomage_prive",), "la convention du 18 janvier 2006 porte le taux à 6,48 % "
                                       "« à compter de l'entrée en vigueur de la présente "
                                       "convention » (article 2, JORFARTI000002277875), date "
                                       "que l'index, qui en tronque le texte, ne garde pas ; "
                                       "l'arrêté que l'ancrage trouve agrée l'accord des "
                                       "apprentis du secteur public"),
    ("2011-01-01", ("csg",), "loi n° 2010-1594, article 20 : il borne l'abattement à quatre "
                             "plafonds sans dire de date ; LEGI date la version de L. 136-2 du "
                             "22 décembre 2010, lendemain de la publication"),
    ("2012-01-01", ("csg",), "loi n° 2011-1906, article 17 : il porte l'abattement à 1,75 % "
                             "sans dire de date ; LEGI date la version de L. 136-2 du "
                             "23 décembre 2011, lendemain de la publication"),
)


def cles(table) -> set[tuple[str, str]]:
    """Les marches qu'une table nomme : (série, date)."""
    return {(serie, entree[0]) for entree in table for serie in entree[1]}


def marches_sans_date(marches: Iterable[tuple[str, str]]) -> list[str]:
    """Les marches de l'IPP, (série, date), dont la date n'est ni lue ni
    expliquée, en « série date »."""
    nommees = cles(DATES_LUES) | cles(DATES_NON_LUES)
    return sorted(f"{serie} {depuis}" for serie, depuis in set(marches)
                  if (serie, depuis) not in nommees)


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ipp_prelevements_sociaux import marches_de_l_ipp

    marches = set(marches_de_l_ipp(yaml.safe_load(DONNEE.read_text(encoding="utf-8"))))
    sans_date = marches_sans_date(marches)
    print(f"{len(cles(DATES_LUES) & marches)} des {len(marches)} marches de l'IPP ont leur "
          f"date lue, {len(cles(DATES_NON_LUES) & marches)} disent pourquoi elle ne l'est pas, "
          f"{len(sans_date)} ni l'un ni l'autre")
    for ligne in sans_date:
        print(f"        {ligne}")
    return 1 if sans_date else 0


if __name__ == "__main__":
    sys.exit(main())
