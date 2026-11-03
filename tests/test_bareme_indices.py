"""Le barème du décret n° 82-1105 : l'indice majoré de chaque indice brut, depuis 1983 (action 158).

Le barème A, annexé au décret n° 82-1105 du 23 décembre 1982 et remplacé
vingt-huit fois depuis, dit quel indice majoré — celui qui se multiplie par la
valeur du point — répond à chaque indice brut des grilles. Le LEGI ne
reproduit ses tableaux que depuis le 1er juillet 2007 ; avant, l'article 1er dit
« tableau non reproduit », et les décrets qui les annexent renvoient au Journal
officiel imprimé. Le jeu d'Épicycle, sur data.gouv.fr, les transcrit tous ; le
récupérateur (``scripts/fetch/epicycle_bareme.py``) le lit, date chaque version
par son texte, ajoute celle du 1er juillet 1999 qu'il omet et corrige huit
valeurs recopiées de la ligne voisine.

Ce qui est vérifié : la lecture et la construction, sur de petits exemples ;
puis la donnée, sous ``data/reference/grilles/bareme/``, confrontée à ce que
les textes écrivent eux-mêmes — les dates de chaque version (LEGI et JORF), les
couples « indice majoré X (indice brut Y) » que le décret n° 85-1148 et les
décrets de rémunération portent de 1985 à 2008, les tableaux du LEGI depuis
2007, les points uniformes que les titres attribuent à tous —, et au barème du
Noyau RH de l'État, qui le redonne de juillet 2009 à 2023.
"""

from __future__ import annotations

import bisect
import csv
import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
BAREME = RACINE / "data" / "reference" / "grilles" / "bareme"


def _charger(nom: str):
    chemin = RACINE / "scripts" / "fetch" / f"{nom}.py"
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules[nom] = module
    specification.loader.exec_module(module)
    return module


bareme = _charger("epicycle_bareme")


# ---------------------------------------------------------------------------
# La lecture et la construction
# ---------------------------------------------------------------------------

def test_le_csv_d_epicycle_se_lit_colonne_par_colonne():
    texte = ("indices_bruts,1979-09-01,1985-01-01\n"
             "100,150,152\n"
             "101,151,\n")
    assert bareme.lire_csv(texte) == {
        "1979-09-01": {100: 150, 101: 151},
        "1985-01-01": {100: 152},
    }


@pytest.mark.parametrize("texte", [
    "indices_bruts,1979-09-01\n100,15a\n",
    "indices_bruts,septembre 1979\n100,150\n",
])
def test_une_cellule_ou_une_colonne_illisible_est_refusee(texte):
    with pytest.raises(ValueError):
        bareme.lire_csv(texte)


def test_un_tableau_du_legi_se_lit_par_couples_malgre_ses_en_tetes_et_ses_milliers():
    """Le tableau aplati par l'index : des couples « brut majoré », coupés
    d'en-têtes datés, de tirets, d'un couple répété au saut de page (2009) et
    des milliers écrits « 1 001 » (2013)."""
    texte = ("Correspondance entre les indices bruts et majorés au 1er juillet 2007 "
             "INDICES Bruts Majorés du 1er juillet 2007 100 194 101 195 - "
             "INDICES Bruts Majorés du 1er juillet 2007 317 304 317 304 318 305 .. "
             "1 001 810 1 015 821 .")
    assert bareme.lire_tableau_legi(texte) == {100: 194, 101: 195, 317: 304, 318: 305,
                                               1001: 810, 1015: 821}
    with pytest.raises(ValueError):
        bareme.lire_tableau_legi("INDICES Bruts Majorés 317 304 317 305")


def _version(debut, colonne, points=None):
    return bareme.Version(debut=debut, texte="t", signature="", jorf="", legi="",
                          points=points, colonne=colonne)


def _periodes(lignes):
    return [(l["indice_brut"], l["debut"], l["fin"], l["indice_majore"], l["lecture"])
            for l in lignes]


def test_une_version_absente_se_deduit_du_point_uniforme_de_la_suivante():
    """Juillet absent de la source : décembre, qui ajoute un point à tous, moins
    ce point. L'indice que juillet ne change pas reste dans la période de
    janvier."""
    versions = (_version("2000-01-01", "A"), _version("2000-07-01", None),
                _version("2000-12-01", "B", points=1))
    colonnes = {"A": {100: 10, 101: 12}, "B": {100: 12, 101: 13}}
    assert _periodes(bareme.construire(colonnes, versions, {})) == [
        (100, "2000-01-01", "2000-06-30", 10, "lue"),
        (100, "2000-07-01", "2000-11-30", 11, "deduite"),
        (100, "2000-12-01", "", 12, "lue"),
        (101, "2000-01-01", "2000-11-30", 12, "lue"),
        (101, "2000-12-01", "", 13, "lue"),
    ]


def test_une_valeur_que_les_points_uniformes_dementent_se_corrige_ou_se_refuse():
    versions = (_version("2000-01-01", "A"), _version("2001-01-01", "B", points=1),
                _version("2002-01-01", "C", points=1))
    colonnes = {"A": {100: 10}, "B": {100: 12}, "C": {100: 12}}
    with pytest.raises(ValueError, match="2001-01-01"):
        bareme.construire(colonnes, versions, {})
    corrections = {("2001-01-01", 100): (12, 11, "recopiée de la ligne voisine")}
    assert _periodes(bareme.construire(colonnes, versions, corrections)) == [
        (100, "2000-01-01", "2000-12-31", 10, "lue"),
        (100, "2001-01-01", "2001-12-31", 11, "corrigee"),
        (100, "2002-01-01", "", 12, "lue"),
    ]


def test_une_correction_que_la_source_ne_justifie_plus_est_refusee():
    """La source a changé la valeur : la correction est à revoir, pas à
    appliquer les yeux fermés."""
    versions = (_version("2000-01-01", "A"), _version("2001-01-01", "B", points=1))
    colonnes = {"A": {100: 10}, "B": {100: 11}}
    corrections = {("2001-01-01", 100): (12, 11, "recopiée de la ligne voisine")}
    with pytest.raises(ValueError, match="correction"):
        bareme.construire(colonnes, versions, corrections)


@pytest.mark.parametrize("colonnes", [
    {"A": {100: 10, 101: 11}, "B": {100: 9, 101: 11}},   # baisse d'une version à l'autre
    {"A": {100: 10, 101: 11}, "B": {100: 12, 101: 11}},  # baisse quand l'indice brut monte
])
def test_un_indice_majore_qui_baisse_est_refuse(colonnes):
    versions = (_version("2000-01-01", "A"), _version("2001-01-01", "B"))
    with pytest.raises(ValueError):
        bareme.construire(colonnes, versions, {})


# ---------------------------------------------------------------------------
# La donnée
# ---------------------------------------------------------------------------

def _lire(nom: str) -> list[dict]:
    with open(BAREME / nom, encoding="utf-8") as fichier:
        return list(csv.DictReader(l for l in fichier if not l.startswith("#")))


def _indices() -> dict[int, list[tuple]]:
    periodes: dict[int, list[tuple]] = {}
    for ligne in _lire("indices.csv"):
        periodes.setdefault(int(ligne["indice_brut"]), []).append(
            (ligne["debut"], ligne["fin"] or "2999-12-31", int(ligne["indice_majore"]),
             ligne["lecture"], ligne["fiabilite"]))
    return periodes


def _majore(periodes: dict[int, list[tuple]], indice_brut: int, jour: str) -> int | None:
    for debut, fin, majore, _, _ in periodes.get(indice_brut, ()):
        if debut <= jour <= fin:
            return majore
    return None


#: Chaque version du barème, datée par le texte qui l'annexe : l'article 1er du
#: décret n° 82-1105, au LEGI, dit « à compter du » de chacune jusqu'en 2006,
#: et le décret au JORF. Le LEGI intervertit les dates de ses versions d'avril
#: et de juillet 1999 ; le n° 99-491 date bien la seconde du 1er juillet.
VERSIONS = [
    ("1983-01-01", "82-1105", "JORFTEXT000000703628"),
    ("1985-01-01", "86-166", "JORFTEXT000000881232"),
    ("1988-10-01", "88-1067", "JORFTEXT000000504298"),
    ("1989-02-01", "89-64", "JORFTEXT000000882942"),
    ("1990-01-01", "90-321", "JORFTEXT000000166950"),
    ("1991-08-01", "91-1191", "JORFTEXT000000538342"),
    ("1998-07-01", "98-462", "JORFTEXT000000740811"),
    ("1999-04-01", "99-208", "JORFTEXT000000393446"),
    ("1999-07-01", "99-491", "JORFTEXT000000394805"),
    ("1999-12-01", "99-943", "JORFTEXT000000397436"),
    ("2001-05-01", "2001-370", "JORFTEXT000000210853"),
    ("2001-07-01", "2001-559", "JORFTEXT000000579944"),
    ("2004-07-01", "2004-679", "JORFTEXT000000620605"),
    ("2005-07-01", "2005-726", "JORFTEXT000000810890"),
    ("2006-07-01", "2006-759", "JORFTEXT000000422923"),
    ("2006-11-01", "2006-1283", "JORFTEXT000000615828"),
    ("2007-07-01", "2007-1054", "JORFTEXT000000649573"),
    ("2008-05-01", "2008-400", "JORFTEXT000018693706"),
    ("2008-07-01", "2008-622", "JORFTEXT000019108374"),
    ("2009-07-01", "2009-824", "JORFTEXT000020815910"),
    ("2011-01-01", "2011-51", "JORFTEXT000023417934"),
    ("2012-01-01", "2012-37", "JORFTEXT000025135486"),
    ("2012-07-01", "2012-853", "JORFTEXT000026149212"),
    ("2013-01-01", "2013-33", "JORFTEXT000026924624"),
    ("2017-01-01", "2017-85", "JORFTEXT000033927793"),
    ("2018-01-01", "2017-85", "JORFTEXT000033927793"),
    ("2021-04-01", "2021-406", "JORFTEXT000043339489"),
    ("2023-07-01", "2023-519", "JORFTEXT000047749211"),
    ("2024-01-01", "2023-519", "JORFTEXT000047749211"),
]

#: Les points d'indice majoré que le titre du décret attribue « aux personnels »
#: ou « à l'ensemble des personnels », et non « à certains » : un barème qui
#: ajoute exactement ce nombre à chaque indice majoré du précédent.
POINTS_UNIFORMES = {
    "1988-10-01": 2,   # n° 88-1067, « deux points d'indice majoré aux personnels »
    "1989-02-01": 1,   # n° 89-64, « un point d'indice majoré aux personnels »
    "1990-01-01": 1,   # n° 90-321
    "1991-08-01": 2,   # n° 91-1191
    "1999-04-01": 1,   # n° 99-208, « un point d'indice majoré uniforme »
    "1999-12-01": 1,   # n° 99-943, de même
    "2006-11-01": 1,   # n° 2006-1283, « à l'ensemble des personnels »
}


def test_les_versions_sont_celles_que_les_textes_datent():
    versions = _lire("versions.csv")
    assert [(v["debut"], v["texte"], v["jorf"]) for v in versions] == VERSIONS
    assert {v["debut"]: int(v["points"]) for v in versions if v["points"]} == POINTS_UNIFORMES
    # La seule version que la source omet est déduite ; toutes les autres sont lues.
    assert {v["debut"] for v in versions if v["lecture"] == "deduite"} == {"1999-07-01"}


#: Les couples que les textes écrivent en toutes lettres, « l'indice majoré X
#: (indice brut Y) » : articles 7 à 10 bis du décret n° 85-1148 au LEGI, version
#: par version, et l'article 2 du n° 91-1191 au JORF. Le n° 85-1148, dans sa
#: rédaction d'origine (JO du 5 novembre 1985), écrit les indices du barème que
#: le n° 86-166 n'avait pas encore remplacé, rétroactivement, au 1er janvier
#: 1985 : ceux de 1983. Écartées, quatre mentions que le LEGI a laissées à leur
#: ancienne valeur quand le reste de l'article changeait (« 444 (indice brut
#: 524) » de 1991 à 1999, quand la même phrase dit ailleurs 446 ; « 164 (indice
#: brut 100) » et « 213 (indice brut 164) » en mai 2001, que le n° 2001-559 dit
#: 169 et que le n° 2001-370 rapporte à l'indice brut 173).
ANCRES = [
    ("1983-01-01", 100, 150, "LEGIARTI000006454537"),
    ("1983-01-01", 175, 194, "LEGIARTI000006454537"),
    ("1983-01-01", 308, 281, "LEGIARTI000006454578"),
    ("1983-01-01", 446, 380, "LEGIARTI000006454594"),
    ("1983-01-01", 767, 621, "LEGIARTI000006454594"),
    ("1985-01-01", 100, 152, "LEGIARTI000006454538"),
    ("1985-01-01", 175, 196, "LEGIARTI000006454538"),
    ("1985-01-01", 209, 217, "LEGIARTI000006454559"),
    ("1985-01-01", 308, 283, "LEGIARTI000006454579"),
    ("1985-01-01", 446, 382, "LEGIARTI000006454595"),
    ("1985-01-01", 767, 623, "LEGIARTI000006454595"),
    ("1988-03-01", 524, 440, "LEGIARTI000006454596"),
    ("1988-03-01", 889, 716, "LEGIARTI000006454596"),
    ("1988-10-01", 100, 154, "LEGIARTI000006454539"),
    ("1988-10-01", 175, 198, "LEGIARTI000006454539"),
    ("1988-10-01", 209, 219, "LEGIARTI000006454561"),
    ("1988-10-01", 308, 285, "LEGIARTI000006454581"),
    ("1988-10-01", 524, 442, "LEGIARTI000006454597"),
    ("1988-10-01", 887, 716, "LEGIARTI000006454597"),
    ("1989-02-01", 100, 155, "LEGIARTI000006454540"),
    ("1989-02-01", 175, 199, "LEGIARTI000006454540"),
    ("1989-02-01", 209, 220, "LEGIARTI000006454562"),
    ("1989-02-01", 308, 286, "LEGIARTI000006454582"),
    ("1989-02-01", 524, 443, "LEGIARTI000006454598"),
    ("1989-02-01", 886, 716, "LEGIARTI000006454598"),
    ("1990-01-01", 100, 156, "LEGIARTI000006454541"),
    ("1990-01-01", 175, 200, "LEGIARTI000006454541"),
    ("1990-01-01", 209, 221, "LEGIARTI000006454563"),
    ("1990-01-01", 308, 287, "LEGIARTI000006454583"),
    ("1990-01-01", 524, 444, "LEGIARTI000006454599"),
    ("1990-01-01", 884, 716, "LEGIARTI000006454599"),
    ("1991-08-01", 100, 158, "LEGIARTI000006454542"),
    ("1991-08-01", 175, 202, "LEGIARTI000006454542"),
    ("1991-08-01", 214, 226, "JORFARTI000000990966"),
    ("1991-08-01", 308, 289, "LEGIARTI000006454584"),
    ("1991-08-01", 524, 446, "LEGIARTI000006454600"),
    ("1991-08-01", 882, 716, "LEGIARTI000006454600"),
    ("1998-04-01", 524, 446, "LEGIARTI000006454601"),
    ("1998-04-01", 882, 716, "LEGIARTI000006454601"),
    ("1998-07-01", 100, 160, "LEGIARTI000006454544"),
    ("1998-07-01", 169, 202, "LEGIARTI000006454544"),
    ("1998-07-01", 244, 249, "LEGIARTI000006454567"),
    ("1998-07-01", 308, 291, "LEGIARTI000006454586"),
    ("1999-04-01", 100, 161, "LEGIARTI000006454545"),
    ("1999-04-01", 169, 203, "LEGIARTI000006454545"),
    ("1999-04-01", 244, 250, "LEGIARTI000006454568"),
    ("1999-04-01", 308, 292, "LEGIARTI000006454587"),
    ("1999-04-01", 524, 447, "LEGIARTI000006454602"),
    ("1999-04-01", 880, 716, "LEGIARTI000006454602"),
    ("1999-07-01", 100, 163, "LEGIARTI000006454546"),
    ("1999-07-01", 164, 203, "LEGIARTI000006454546"),
    ("1999-07-01", 244, 252, "LEGIARTI000006454569"),
    ("1999-07-01", 308, 294, "LEGIARTI000006454588"),
    ("1999-07-01", 524, 447, "LEGIARTI000006454604"),
    ("1999-07-01", 880, 716, "LEGIARTI000006454604"),
    ("1999-12-01", 100, 164, "LEGIARTI000006454547"),
    ("1999-12-01", 164, 204, "LEGIARTI000006454547"),
    ("1999-12-01", 244, 253, "LEGIARTI000006454570"),
    ("1999-12-01", 308, 295, "LEGIARTI000006454589"),
    ("1999-12-01", 524, 448, "LEGIARTI000006454605"),
    ("1999-12-01", 879, 716, "LEGIARTI000006454605"),
    ("2001-05-01", 100, 169, "LEGIARTI000006454571"),
    ("2001-05-01", 244, 258, "LEGIARTI000006454571"),
    ("2001-05-01", 308, 297, "LEGIARTI000006454590"),
    ("2001-07-01", 100, 172, "LEGIARTI000006454550"),
    ("2001-07-01", 173, 216, "LEGIARTI000006454550"),
    ("2001-07-01", 244, 261, "LEGIARTI000006454572"),
    ("2002-01-01", 524, 448, "LEGIARTI000006454606"),
    ("2002-01-01", 879, 716, "LEGIARTI000006454606"),
    ("2004-07-01", 100, 174, "LEGIARTI000006454552"),
    ("2004-07-01", 244, 263, "LEGIARTI000006454573"),
    ("2005-07-01", 100, 186, "LEGIARTI000006454554"),
    ("2005-07-01", 244, 275, "LEGIARTI000006454574"),
    ("2006-07-01", 100, 190, "LEGIARTI000006454555"),
    ("2006-07-01", 244, 279, "LEGIARTI000006454575"),
    ("2006-11-01", 100, 191, "LEGIARTI000006454556"),
    ("2006-11-01", 244, 280, "LEGIARTI000006454576"),
    ("2006-11-01", 308, 298, "LEGIARTI000006454591"),
    ("2006-11-01", 524, 449, "LEGIARTI000006454607"),
    ("2006-11-01", 879, 717, "LEGIARTI000006454607"),
    ("2007-07-01", 100, 194, "LEGIARTI000006454557"),
    ("2007-07-01", 244, 283, "LEGIARTI000006454577"),
    ("2008-05-01", 100, 199, "LEGIARTI000018728042"),
    ("2008-05-01", 244, 288, "LEGIARTI000018728040"),
    ("2008-07-01", 100, 201, "LEGIARTI000019111499"),
    ("2008-07-01", 244, 290, "LEGIARTI000019111499"),
]


@pytest.mark.parametrize("jour, indice_brut, majore, source", ANCRES)
def test_chaque_couple_que_les_textes_ecrivent_est_dans_le_bareme(jour, indice_brut,
                                                                   majore, source):
    assert _majore(_indices(), indice_brut, jour) == majore, source


#: Depuis le 1er juillet 2007, le LEGI reproduit chaque barème : quelques
#: indices bruts de chacun, lus dans son tableau (celui du 1er mai 2008 s'arrête
#: à l'indice brut 536). Le récupérateur, quand l'index est là, les confronte
#: tous : 11 484 couples, aucun écart, le 3 novembre 2026.
TABLEAUX_LEGI = {
    "2007-07-01": ("LEGIARTI000018191834", {100: 194, 244: 283, 300: 292, 400: 363, 500: 431, 800: 657, 1015: 821}),
    "2008-05-01": ("LEGIARTI000018728052", {100: 199, 244: 288, 300: 292, 400: 363, 500: 431}),
    "2008-07-01": ("LEGIARTI000023596059", {100: 201, 244: 290, 300: 292, 400: 363, 500: 431, 800: 657, 1015: 821}),
    "2009-07-01": ("LEGIARTI000020973724", {100: 203, 244: 292, 300: 294, 400: 363, 500: 431, 800: 657, 1015: 821}),
    "2011-01-01": ("LEGIARTI000023427645", {100: 203, 244: 295, 300: 297, 400: 363, 500: 431, 800: 657, 1015: 821}),
    "2012-01-01": ("LEGIARTI000025140239", {100: 203, 244: 302, 300: 304, 400: 363, 500: 431, 800: 657, 1015: 821}),
    "2012-07-01": ("LEGIARTI000026151662", {100: 203, 244: 308, 300: 310, 400: 363, 500: 431, 800: 657, 1015: 821}),
    "2013-01-01": ("LEGIARTI000026928467", {100: 203, 244: 309, 300: 311, 400: 363, 500: 431, 800: 657, 1015: 821}),
    "2017-01-01": ("LEGIARTI000034061028", {100: 203, 244: 309, 300: 311, 400: 363, 500: 431, 800: 657, 1015: 821}),
    "2018-01-01": ("LEGIARTI000034079564", {100: 203, 244: 309, 300: 311, 400: 363, 500: 431, 800: 657, 1015: 821, 1027: 830}),
    "2021-04-01": ("LEGIARTI000043341340", {100: 203, 244: 309, 300: 311, 400: 363, 500: 431, 800: 657, 1015: 821, 1027: 830}),
    "2023-07-01": ("LEGIARTI000047751782", {100: 203, 244: 309, 300: 311, 400: 371, 500: 431, 800: 657, 1015: 821, 1027: 830}),
    "2024-01-01": ("LEGIARTI000047780477", {100: 208, 244: 314, 300: 316, 400: 376, 500: 436, 800: 662, 1015: 826, 1027: 835}),
}


@pytest.mark.parametrize("jour", sorted(TABLEAUX_LEGI))
def test_depuis_2007_le_bareme_est_celui_que_le_legi_reproduit(jour):
    article, couples = TABLEAUX_LEGI[jour]
    periodes = _indices()
    assert {brut: _majore(periodes, brut, jour) for brut in couples} == couples, article


def _par_version() -> dict[str, dict[int, int]]:
    periodes = _indices()
    return {debut: {brut: _majore(periodes, brut, debut) for brut in periodes
                    if _majore(periodes, brut, debut) is not None}
            for debut, _, _ in VERSIONS}


def test_chaque_version_porte_tous_les_indices_bruts_de_son_tableau():
    """916 indices bruts, de 100 à 1015, jusqu'en 2013 ; 1022 depuis 2017, et
    1027 depuis 2018, que le protocole PPCR ajoute au sommet."""
    for debut, indices in _par_version().items():
        sommet = 1027 if debut >= "2018-01-01" else 1022 if debut >= "2017-01-01" else 1015
        assert sorted(indices) == list(range(100, sommet + 1)), debut


def test_les_points_uniformes_s_ajoutent_a_tous_les_indices_majores():
    versions = _par_version()
    dates = [debut for debut, _, _ in VERSIONS]
    for debut, points in POINTS_UNIFORMES.items():
        avant = versions[dates[dates.index(debut) - 1]]
        apres = versions[debut]
        ecarts = {brut for brut in avant if apres[brut] - avant[brut] != points}
        assert not ecarts, (debut, sorted(ecarts)[:5])


def test_l_indice_majore_ne_baisse_ni_d_une_version_a_l_autre_ni_quand_le_brut_monte():
    versions = _par_version()
    dates = [debut for debut, _, _ in VERSIONS]
    for avant, apres in zip(dates, dates[1:]):
        assert all(versions[apres][b] >= versions[avant][b] for b in versions[avant]), apres
    for debut, indices in versions.items():
        bruts = sorted(indices)
        assert all(indices[b] <= indices[s] for b, s in zip(bruts, bruts[1:])), debut


#: Les huit valeurs que la source a recopiées de l'indice brut suivant (un
#: saut de deux points que le barème ne fait nulle part ailleurs au-dessus de
#: l'indice brut 400) : chacune est la valeur que la version d'avant et celle
#: d'après donnent ensemble, par les points uniformes qui les séparent.
CORRIGEES = {
    (621, "1983-01-01"): 510,   # la source : 509 ; 1985 lui donne 512, deux points de plus
    (467, "1989-02-01"): 401,   # 402 ; 400 en octobre 1988, 402 en 1990
    (792, "1989-02-01"): 645,   # 646 ; 644, puis 646
    (554, "1990-01-01"): 465,   # 466 ; 464 en 1989, 467 en 1991
    (567, "1990-01-01"): 475,   # 476 ; 474, puis 477
    (607, "1990-01-01"): 505,   # 506 ; 504, puis 507
    (633, "1990-01-01"): 525,   # 526 ; 524, puis 527
    (457, "2004-07-01"): 399,   # 398 ; 399 en 2001 et en 2005
}


def test_les_valeurs_recopiees_de_la_ligne_voisine_sont_corrigees():
    periodes = _indices()
    for (brut, jour), majore in CORRIGEES.items():
        assert _majore(periodes, brut, jour) == majore, (brut, jour)
    corrigees = {(brut, debut) for brut, liste in periodes.items()
                 for debut, _, _, lecture, fiabilite in liste if lecture == "corrigee"}
    # L'indice brut 457 garde en 2004 la valeur de 2001 : sa période ne se coupe pas.
    assert corrigees == set(CORRIGEES) - {(457, "2004-07-01")}
    assert {fiabilite for liste in periodes.values() for _, _, _, lecture, fiabilite in liste
            if lecture == "corrigee"} == {"estimee"}
    assert {fiabilite for liste in periodes.values() for _, _, _, lecture, fiabilite in liste
            if lecture != "corrigee"} == {"haute"}


def _noyau() -> dict[int, list[tuple]]:
    periodes: dict[int, list[tuple]] = {}
    chemin = RACINE / "data" / "reference" / "grilles" / "etat" / "indices.csv"
    with open(chemin, encoding="utf-8") as fichier:
        for ligne in csv.DictReader(l for l in fichier if not l.startswith("#")):
            periodes.setdefault(int(ligne["indice_brut"]), []).append(
                (ligne["debut"], ligne["fin"] or "2999-12-31", int(ligne["indice_majore"]),
                 "", ""))
    return periodes


def test_le_noyau_rh_redonne_le_bareme_de_juillet_2009_a_2023_et_s_en_ecarte_avant():
    """Le Noyau RH de l'État (``grilles/etat/indices.csv``) recoupe le barème
    de juillet 2009 à 2023, indice pour indice. Avant, il prolonge jusqu'en 1900
    les valeurs de mai 2008 des indices bruts 100 à 302, et donne 466 à l'indice
    brut 500 avant novembre 2006, quand le barème de juillet 2006 dit 430 ; sa
    ligne d'avant novembre 2006 est, pour le reste, ce barème de juillet 2006.
    Depuis 2024, il paie l'indice majoré 366, le minimum de traitement, aux
    indices bruts dont le barème donne moins."""
    noyau, barem = _noyau(), _indices()
    for debut, _, _ in VERSIONS:
        if debut < "2006-07-01":
            continue
        ecarts = {b for b in barem if _majore(barem, b, debut) is not None
                  and _majore(noyau, b, debut) != _majore(barem, b, debut)}
        if "2009-07-01" <= debut <= "2023-07-01":
            assert not ecarts, (debut, sorted(ecarts)[:5])
        elif debut == "2024-01-01":
            assert {_majore(noyau, b, debut) for b in ecarts} == {366}
            assert all(_majore(barem, b, debut) < 366 for b in ecarts)
        else:
            assert ecarts <= set(range(100, 303)) | {500}, debut
            if debut == "2006-07-01":
                assert {100, 244, 302, 500} <= ecarts
                assert (_majore(noyau, 500, debut), _majore(barem, 500, debut)) == (466, 430)
            if debut == "2008-05-01":
                assert not ecarts


def test_le_fichier_dit_sa_source_sa_licence_et_ce_qu_il_corrige():
    with open(BAREME / "indices.csv", encoding="utf-8") as fichier:
        entete = "".join(l for l in fichier if l.startswith("#"))
    for mention in ("source_id: epicycle_bareme_indices", "CC BY-SA",
                    "scripts/fetch/epicycle_bareme.py", "1er juillet 1999", "corrigee"):
        assert mention in entete, mention
