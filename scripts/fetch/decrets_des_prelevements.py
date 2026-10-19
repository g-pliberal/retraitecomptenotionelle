#!/usr/bin/env python3
"""Les décrets qu'aucune marche de l'histoire des prélèvements ne rejoint.

    python scripts/fetch/decrets_des_prelevements.py

Importé par ``ipp_prelevements_sociaux.py``, qui imprime ce qu'il trouve à
chaque réécriture de ``data/reference/legislation/prelevements_historiques.yaml``
(action 138, étape 9).

POURQUOI. ``ipp_taux_cotisation.py`` cherche, pour la vieillesse du régime
général, les décrets du *Journal officiel* qu'aucune marche ne rejoint ; rien ne
le faisait pour l'histoire des prélèvements, dont les marches viennent de l'IPP
ou des textes qu'une session a lus. Une marche qui manque ne se voit pas : la
série tient le taux d'avant, et rien ne rougit. Cette garde interroge l'index
JORF de la DILA (``dila_index.py``) et signale chaque décret de la requête
qu'aucune marche ne cite. Chacun doit s'expliquer. Deux de ceux qu'elle a vus
disaient une marche qui manquait, et qui est désormais écrite : la maladie du
salarié ramenée à 4,5 % du 1er février au 13 novembre 1981, que le décret
n° 81-1013 refixe à 5,5 %, et le relèvement exceptionnel de la maladie des
agents publics et de leurs pensions du 1er juillet 1987 au 30 juin 1988
(décret n° 87-470).

LA REQUÊTE. Les décrets publiés depuis 1967, où commencent les barèmes de
l'IPP, dont le titre annonce des taux de cotisation et nomme la maladie, le
veuvage, les allocations familiales, les assurances sociales, les régimes
spéciaux, les assurés partiellement rattachés au régime général, les retraités,
les pensionnés ou leurs avantages de vieillesse. Elle ne demande pas le mot
« maladie », et c'est délibéré : le décret n° 87-470, qui relève celle des
pensions de la fonction publique, ne le porte pas dans son titre. Le prix est
d'y voir les retenues pour pension de bien des régimes, que l'histoire n'a pas.

CE QUI REJOINT UNE MARCHE. Un décret dont une marche cite le numéro, dans son
``texte`` ou par le texte du Journal officiel où l'ancrage la relie
(``jorf``) — un rectificatif compte avec son décret. Les autres sont dans l'une
des deux listes : :data:`DECRETS_SANS_EFFET`, qui ne touchent aucune série — une
autre population, un autre risque, la part de l'employeur, ou le taux qu'une
marche porte déjà —, et :data:`DECRETS_EN_SUSPENS`, qui touchent une série ou
une pension qu'elle prélève sans qu'elle le porte, ou que l'index ne laisse pas
lire : chacun est un reste de la feuille de route.

CE QUE L'HISTOIRE NE DISTINGUE PAS, et qui range bien des décrets parmi les
premiers. Ses salaires sont ceux du privé et des agents publics : l'agent d'un
régime spécial ou le militaire y prend les taux du salarié du privé ou du
fonctionnaire, comme sur la fiche de paie (``profil_de_la_fiche``), et non ceux
que son régime fixe. Le régime local d'Alsace-Moselle, l'assurance volontaire,
les revenus de remplacement et les non-résidents n'y sont pas.

CE QU'ELLE NE COUVRE PAS. Les arrêtés — ceux des mines de 1972 et de 1987 sont
dits dans ``maladie_des_pensions.py`` — et les lois, qui fixent la CSG, la CRDS,
la CASA et le veuvage de 1982 ; les décrets dont le titre ne dit ni taux ni
cotisation, ou que l'index n'a pas.
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dila_index import chemin_index  # noqa: E402

DONNEE = (Path(__file__).resolve().parents[2] / "data" / "reference" / "legislation"
          / "prelevements_historiques.yaml")

#: La requête : tout décret dont le titre annonce des taux de cotisation d'un
#: risque, d'une population ou d'une assiette de l'histoire.
REQUETE = (
    'titre:taux AND (titre:cotisation OR titre:cotisations) AND ('
    'titre:maladie OR titre:veuvage OR titre:"allocations familiales" '
    'OR titre:"assurances sociales" OR titre:"divers regimes speciaux" '
    'OR titre:partiellement OR titre:retraites OR titre:pensionnes '
    'OR titre:"avantages de vieillesse" OR titre:"avantages de retraite")'
)

#: La première année de la requête : celle où commencent les barèmes de l'IPP.
PREMIERE_ANNEE = 1967

#: Le numéro d'un décret dans un titre du JORF, selon l'époque : « Décret
#: n°67-851 du… », « Décret no 90-1077 du… », « Décret n° 2004-1230 du… ».
NUMERO_DU_TITRE = re.compile(r"^D[ée]cret\s+n?[°o]?\s*(\d{2,4}-\d{1,5})", re.I)

#: Un numéro de texte dans le ``texte`` d'une marche : « Décret 79-650 du… »,
#: « puis 91-912, 92-793 », « décret 67-850, art. 3 » ; ni un article de code
#: (« D. 711-3 », « Article D242-3 »), ni une date.
NUMERO_CITE = re.compile(r"(?<![\w.\-])(?<![LRD]\. )(\d{2}|\d{4})-(\d{1,5})(?![\w\-])")

#: Les populations et les parts que l'histoire n'a pas, que plusieurs raisons
#: partagent.
_PARTIELLEMENT = ("les salariés des régimes spéciaux placés sous le régime général pour une "
                  "partie des risques (tableau du décret n° 67-804), que l'histoire des salaires "
                  "ne distingue pas")
_REGIME_LOCAL = "le régime local d'Alsace-Moselle, que l'histoire n'a pas"
_VOLONTAIRE = ("l'assurance volontaire des expatriés ou des pensionnés résidant à l'étranger, "
               "que l'histoire n'a pas")
_REMPLACEMENT = ("les revenus de remplacement — préretraite, garantie de ressources, chômage —, "
                 "que l'histoire n'a pas")
_NON_RESIDENTS = ("les taux des non-résidents (L. 131-7-1, puis L. 131-9), que l'histoire ne "
                  "distingue pas")
_VIEILLESSE = "la vieillesse, que l'histoire des prélèvements n'a pas"
_EMPLOYEUR = "la seule part de l'employeur, que l'histoire n'a pas"
_MILITAIRES = ("la solde des militaires de carrière (décret n° 67-851, art. 1er et 2), que "
               "l'histoire prend aux taux des fonctionnaires de l'État, comme la fiche de paie")

#: Les décrets que la requête ramène, qu'aucune marche ne cite et qui ne touchent
#: aucune série de l'histoire, avec la raison, lue dans la notice ou les articles
#: de l'index JORF, ou dans les versions de LEGI qu'elle nomme.
DECRETS_SANS_EFFET: dict[str, str] = {
    # -- Le régime général et les assurances sociales agricoles ---------------
    "73-1209": "le 1er alinéa des articles 3 et 4 du décret n° 67-803 : la vieillesse et les "
               "allocations familiales de l'employeur",
    "79-654": "les assurances sociales agricoles majorées d'un point du 1er août 1979 au "
              "31 janvier 1981, le jumeau du n° 79-650 : l'histoire prend, pour les salariés "
              "agricoles, les taux du régime général",
    "81-1028": "la maladie des assurances sociales agricoles relevée au 19 novembre 1981, le "
               "jumeau du n° 81-1013 : les salariés agricoles prennent les taux du régime général",
    "83-1198": "au 1er janvier 1984, la part de l'employeur baisse et la vieillesse du salarié "
               "monte d'un point ; sa maladie reste à 5,50 % (décret n° 81-1013, art. 1er, "
               "LEGIARTI000006762051)",
    "86-876": "la vieillesse du salarié (D. 242-4), " + _VIEILLESSE,
    "88-772": "tient au 1er juillet 1988 le 5,90 % du salarié (D. 242-3, LEGIARTI000006736373) et "
              "les 1,4 et 2,4 % des pensions (D. 242-8, LEGIARTI000006736391), que les séries "
              "portent depuis le 1er juillet 1987 (décret n° 87-453)",
    "88-1234": "la vieillesse du salarié, " + _VIEILLESSE,
    "91-1388": "la maladie de l'employeur, relevée de 0,2 point au 1er janvier 1992 ; le salarié "
               "garde 6,80 %",
    "92-572": "la maladie de l'employeur des assurances sociales agricoles, baissée de 0,1 point",
    "2015-1852": "la maladie de l'employeur relevée de 0,04 point en 2016 (D. 242-3 : le salarié "
                 "garde 0,75 %), le FNAL, la réduction générale, les régimes spéciaux "
                 "partiellement rattachés (D. 711-8), les clercs de notaires en activité et les "
                 "praticiens conventionnés (L. 722-1)",
    "2016-1932": "la maladie de l'employeur relevée de 0,05 point en 2017 (D. 242-3 : le salarié "
                 "garde 0,75 %), le FNAL, la réduction générale, les régimes spéciaux "
                 "partiellement rattachés (D. 711-8), les clercs de notaires en activité et les "
                 "volontaires pour l'insertion",
    "2012-664": "les allocations familiales de l'employeur et la réduction générale, " + _EMPLOYEUR,
    "2014-517": "la cotisation des affiliés au régime général sur critère de résidence, que "
                "l'histoire n'a pas",
    # -- Les pensions du régime général et des régimes spéciaux ----------------
    "80-481": "la maladie des pensions des salariés agricoles, 1 %, et de leurs autres avantages "
              "de retraite, 2 % : les taux de ``maladie_regime_general`` et de "
              "``maladie_complementaires``, que l'histoire leur applique (REGIMES_DES_PENSIONS)",
    "95-1401": "la maladie des pensions des salariés agricoles, 2,6 et 3,6 % en 1996, le jumeau "
               "du n° 95-1356 ; ses taux de 1997 deviennent ceux du n° 96-1167",
    "80-599": "les complémentaires des pensionnés des régimes spéciaux (L. 3-2), 2 % : le taux de "
              "``maladie_complementaires`` (LEGIARTI000006761318)",
    "87-464": "R. 711-5, les revenus de remplacement ; R. 711-11, les complémentaires des "
              "pensionnés des régimes spéciaux, 2,4 % du 1er juillet 1987 : le taux de "
              "``maladie_complementaires``",
    "88-788": "tient au 1er juillet 1988 les taux du n° 87-464 (R. 711-5 et R. 711-11, "
              "LEGIARTI000006752903)",
    "88-322": "R. 711-5, la préretraite : " + _REMPLACEMENT,
    # -- Le régime local, l'assurance volontaire, les revenus de remplacement ---
    **{numero: _REGIME_LOCAL for numero in (
        "89-541", "90-1077", "92-1", "93-43", "93-1358", "93-1359", "94-1151", "94-1152",
        "96-10", "96-11", "96-1251", "96-1253", "97-1233", "97-1238", "98-1177", "98-1178",
        "98-1179", "99-1097", "99-1098", "99-1099")},
    **{numero: _VOLONTAIRE for numero in (
        "77-1477", "81-43", "81-44", "82-1244", "96-580", "2006-162", "2008-143", "2010-153",
        "2013-564", "2017-1864")},
    "89-638": "la Caisse des Français de l'étranger, " + _VOLONTAIRE,
    "94-1149": "la Caisse des Français de l'étranger, " + _VOLONTAIRE,
    **{numero: _REMPLACEMENT for numero in ("80-435", "82-445", "83-362", "88-334")},
    "97-296": "le travail des détenus, que l'histoire n'a pas",
    "98-613": "le travail des détenus, que l'histoire n'a pas",
    "93-275": "les jeunes agriculteurs stagiaires, que l'histoire n'a pas",
    **{numero: _NON_RESIDENTS for numero in ("2004-1230", "2017-1895", "2018-162")},
    # -- Les salariés partiellement rattachés, les militaires --------------------
    **{numero: _PARTIELLEMENT for numero in (
        "73-1210", "75-1274", "76-895", "78-1214", "79-651", "81-1014", "83-1196")},
    "69-11": "annulé par le Conseil d'État (notice)",
    "75-1272": _MILITAIRES + " : le jumeau du n° 75-1270, publié le même jour",
    "78-1216": _MILITAIRES + " : le jumeau du n° 78-1215, publié le même jour, au 1er janvier "
               "1979 et au 1er janvier 1980",
    "81-1016": _MILITAIRES + " : 4,75 % de l'assuré, le taux du n° 81-1015 (notices)",
    # -- Les régimes spéciaux : leurs agents en activité, leurs employeurs -----
    "87-469": "la maladie des mineurs en activité (décret n° 46-2769, art. 46), 5,5 % portés à "
              "5,9 % du 1er juillet 1987, comme celle du salarié du privé, qu'ils prennent dans "
              "l'histoire ; leur vieillesse (art. 52)",
    "88-796": "tient au 1er juillet 1988 les taux du n° 87-469 des mineurs en activité",
    "2018-65": "la maladie des mineurs en activité, 0,75 % supprimés en 2018 comme celle du "
               "salarié du privé ; celle des marins (décret du 14 avril 2008)",
    "92-476": "la maladie des agents des IEG en activité (5,80 %), que l'histoire des salaires "
              "ne distingue pas",
    "93-689": "le régime spécial du personnel de la CANSSM, que le dépôt ne calcule pas "
              "(inventaire : ``canssm_personnel``, sans statut)",
    "94-995": "le régime spécial du personnel de la CANSSM, que le dépôt ne calcule pas "
              "(inventaire : ``canssm_personnel``, sans statut)",
    "99-194": "la maladie à la charge de la Banque de France pour ses salariés et ses retraités "
              "(11,15 %), et celle de ses agents détachés à l'étranger (décret n° 91-613, "
              "art. 13, LEGIARTI000006775984) : rien que la pension paie",
    "2011-2087": "la maladie de l'employeur des IEG, " + _EMPLOYEUR,
    "2012-1486": "la maladie de la CCI de Paris au régime général pour ses salariés intégrés en "
                 "2013, " + _EMPLOYEUR,
    "2016-1944": "la maladie due par la RATP pour 2017, " + _EMPLOYEUR,
    "2017-997": "la maladie due par le grand port maritime de Bordeaux, " + _EMPLOYEUR,
    "2017-1890": "la maladie des employeurs territoriaux et hospitaliers (décret n° 67-850, "
                 "art. 2), " + _EMPLOYEUR,
    "2018-891": "la maladie des employeurs du régime de la SNCF, baissée au 1er octobre 2018, "
                + _EMPLOYEUR,
    "2024-49": "la maladie et la vieillesse des employeurs territoriaux et hospitaliers, et la "
               "retenue pour pension, " + _EMPLOYEUR,
    # -- La vieillesse des régimes spéciaux et des complémentaires --------------
    "68-1029": "le taux de cotisation d'un régime de retraite complémentaire (décret "
               "n° 59-1569), " + _VIEILLESSE,
    "77-171": "les cotisations des exploitants et des salariés à la caisse de retraites des "
              "chemins de fer secondaires (LEGIARTI000006766155), " + _VIEILLESSE,
    "87-462": "la cotisation des salariés à la caisse de retraites des chemins de fer "
              "secondaires, 8,10 % portés à 8,30 % (LEGIARTI000006770380), " + _VIEILLESSE,
    "91-159": "les retenues pour pension de divers régimes spéciaux, au 1er février 1991, "
              + _VIEILLESSE,
    "91-969": "la cotisation supplémentaire des sapeurs-pompiers professionnels à la CNRACL, "
              + _VIEILLESSE,
    "92-998": "la vieillesse des agents de l'ex-chambre de commerce de Roubaix, " + _VIEILLESSE,
    "92-1046": "la retenue et la contribution de la CNRACL (décret n° 91-613, art. 5), "
               + _VIEILLESSE,
    "93-1104": "la vieillesse des agents de la CCI de Paris, " + _VIEILLESSE,
    "94-1153": "la contribution des employeurs à la CNRACL, " + _VIEILLESSE,
    "95-112": "la contribution des employeurs à la CNRACL, " + _VIEILLESSE,
    "99-1065": "la contribution des employeurs à la CNRACL, " + _VIEILLESSE,
    "2003-51": "la contribution des employeurs à la CNRACL, " + _VIEILLESSE,
    "83-36": "la contribution des collectivités locales à la CNRACL, " + _VIEILLESSE,
    "2021-281": "les cotisations à la CNRACL, " + _VIEILLESSE,
    "2025-86": "la vieillesse des employeurs des agents de la CNRACL, " + _VIEILLESSE,
    "83-1192": "les cotisations à la caisse de retraites de la Comédie-Française, " + _VIEILLESSE,
    "88-790": "les cotisations aux caisses de retraites de l'Opéra de Paris et de la "
              "Comédie-Française, " + _VIEILLESSE,
    "88-1237": "les cotisations aux caisses de retraites de l'Opéra de Paris et de la "
               "Comédie-Française, " + _VIEILLESSE,
    "88-1225": "la cotisation des marins à leur caisse de retraites, " + _VIEILLESSE,
    "91-836": "les cotisations à la caisse de retraites des marins, " + _VIEILLESSE,
    "93-1069": "les cotisations à la caisse de retraites des marins, " + _VIEILLESSE,
    "2007-941": "les cotisations à la caisse de retraites des marins, " + _VIEILLESSE,
    "2008-338": "les cotisations à la caisse de retraites des marins, " + _VIEILLESSE,
    "98-758": "la vieillesse du régime spécial de la CCI de Paris, " + _VIEILLESSE,
    "2005-1636": "les conventions financières de la caisse de retraites de la RATP, "
                 + _VIEILLESSE,
    "2005-1638": "les cotisations à la caisse de retraites de la RATP, " + _VIEILLESSE,
    "2007-439": "les ressources de la caisse de retraites de la RATP, " + _VIEILLESSE,
    "2018-1358": "les cotisations à la caisse de retraites de la RATP, " + _VIEILLESSE,
    "2025-990": "les cotisations patronales au régime de retraites de la RATP, " + _VIEILLESSE,
    "2015-1876": "la vieillesse et le veuvage de Saint-Pierre-et-Miquelon, que l'histoire n'a "
                 "pas",
    # -- Les indépendants ------------------------------------------------------
    "82-1118": "abroge au 1er janvier 1983 le taux réduit de 1974 des allocations familiales "
               "(décret n° 74-314), où la série change par le n° 82-1117, du même jour",
}

#: Les décrets qu'aucune marche ne cite et qui touchent une série de l'histoire,
#: ou une pension qu'elle prélève, sans qu'elle le porte, ou que l'index ne
#: laisse pas lire : chacun est un reste de la feuille de route (action 138,
#: étape 9, note « les décrets qu'aucune marche ne rejoint »).
DECRETS_EN_SUSPENS: dict[str, str] = {
    "68-579": "une réduction du taux maladie dans l'article 5 du décret n° 67-803, hors de ses "
              "articles 1er et 2, qui font la série ; la notice ne la chiffre pas, ni ne dit à "
              "quels gains elle s'applique. À lire au fac-similé",
    "77-677": "abroge au 1er juillet 1977 le 2e alinéa de l'article 5 du décret n° 67-803, peut-"
              "être la réduction du n° 68-579 ; ``ipp_taux_cotisation.py`` y lit une exonération "
              "des gains les plus faibles. À lire au fac-similé",
    "70-717": _MILITAIRES + " ; sans jumeau pour les fonctionnaires civils, que l'IPP ne change "
              "pas en 1970, ni notice qui le chiffre. À lire au fac-similé",
    "2020-1689": "la cotisation d'équilibre des pensionnés des IEG au régime complémentaire de la "
                 "CAMIEG, 2,01 % en 2021 et 2022, 2,25 % depuis 2023, que ni l'histoire ni la "
                 "fiche de paie ne prélèvent ; avant 2021, les décrets n° 2008-416, 2014-363 et "
                 "2017-989, que la requête ne ramène pas. À décider : la pension nette la perd-"
                 "elle ?",
}


def numero(titre: str) -> str | None:
    """Le numéro d'un décret, lu dans son titre au JORF."""
    trouve = NUMERO_DU_TITRE.search(titre or "")
    return trouve.group(1) if trouve else None


def cle(identifiant: str, titre: str) -> str:
    """Ce qui nomme un décret dans les listes : son numéro, ou, sans numéro, son
    identifiant au JORF. Un rectificatif a le numéro de son décret."""
    return numero(titre) or identifiant


def candidats(db: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """Les décrets que la requête ramène depuis :data:`PREMIERE_ANNEE` :
    identifiant, date, titre."""
    return db.execute(
        "SELECT doc.id, doc.date, doc.titre FROM fts JOIN doc ON doc.rowid = fts.rowid "
        "WHERE fts MATCH ? AND doc.date >= ? AND doc.num = '' "
        "AND upper(doc.nature) = 'DECRET' ORDER BY doc.date, doc.id",
        (REQUETE, str(PREMIERE_ANNEE)),
    ).fetchall()


def numeros_cites(db: sqlite3.Connection, marches) -> set[str]:
    """Les décrets que les marches citent : les numéros de leur ``texte``, et
    celui du texte du Journal officiel où l'ancrage relie chacune (``jorf``)."""
    cites: set[str] = set()
    for marche in marches:
        cites.update(f"{annee}-{rang}" for annee, rang in NUMERO_CITE.findall(marche.get("texte", "")))
        identifiant = marche.get("jorf")
        if identifiant:
            ligne = db.execute("SELECT titre FROM doc WHERE id = ?", (identifiant,)).fetchone()
            cites.add(cle(identifiant, ligne[0]) if ligne else identifiant)
    return cites


def decrets_ignores(db: sqlite3.Connection, marches) -> list[str]:
    """Les décrets de la requête qu'aucune marche ne cite, et qu'aucune des deux
    listes n'explique : une ligne par décret."""
    cites = numeros_cites(db, marches)
    expliques = DECRETS_SANS_EFFET.keys() | DECRETS_EN_SUSPENS.keys()
    vus, restants = set(), []
    for identifiant, publie, titre in candidats(db):
        nom = cle(identifiant, titre)
        if nom in cites or nom in expliques or nom in vus:
            continue
        vus.add(nom)
        restants.append(f"{publie}  {identifiant}  {titre[:120]}")
    return restants


def main() -> int:
    chemin = chemin_index("jorf")
    if not chemin.exists():
        print("Index JORF absent : python scripts/fetch/dila_index.py jorf --recuperer",
              file=sys.stderr)
        return 1
    contenu = yaml.safe_load(DONNEE.read_text(encoding="utf-8"))
    marches = [marche for partie in ("pensions", "salaires", "independants")
               for serie in contenu[partie].values() for marche in serie]
    db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    ignores = decrets_ignores(db, marches)
    print(f"{len(DECRETS_SANS_EFFET)} décrets sans effet, {len(DECRETS_EN_SUSPENS)} en suspens, "
          f"{len(ignores)} qu'aucune marche ne rejoint ni aucune liste n'explique")
    for ligne in ignores:
        print(f"        {ligne}")
    return 1 if ignores else 0


if __name__ == "__main__":
    sys.exit(main())
