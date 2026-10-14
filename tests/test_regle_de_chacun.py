"""Le droit de chacun, et non celui de la génération de l'année (action 121).

« Mon site doit représenter toutes les personnes encore vivantes » : pour
toute génération de 1920 à 2005, chaque statut et chaque régime qu'il route,
le modèle trouve une règle DATÉE — une période de la fiche — à toute année où
l'assuré peut partir, de cinquante à soixante-dix ans, et cette règle est la
SIENNE : l'âge d'ouverture et la durée requise qu'elle lui oppose ne
dépendent pas de l'année où il part, une fois cet âge atteint. Une fiche qui
écrivait, pour chaque année, l'âge de la génération qui l'atteint cette
année-là donnait à chacun la règle d'une autre génération ; une table qui
commençait en 2004 rendait au fonctionnaire parti plus tard la durée de sa
génération, au lieu de celle de l'année où son droit s'était ouvert.

Le droit lui-même compte parfois à l'année d'effet de la pension : la règle
d'une génération y change avec l'année où elle part. Ces régimes se déclarent
un à un, texte en main, avec les années où la règle bascule
(``A_L_ANNEE_D_EFFET``). Ceux dont la variation n'a pas encore été confrontée
à leur texte se déclarent aussi, comme tels (``A_RELIRE``) : c'est la suite de
l'action 121. Une bascule hors des années déclarées échoue, et une déclaration
qui ne sert plus se retire.

Le balayage construit une carrière par statut et par génération, partie à
soixante-dix ans, puis la décline à chaque âge de départ : l'âge d'ouverture
et la durée requise ne dépendent pas des lignes au-delà du départ.
"""

from __future__ import annotations

import dataclasses
from collections import defaultdict

import pytest

from retraite_notionnelle.carriere import Affiliations
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.droit import ouvrir
from retraite_notionnelle.simulateur import Simulateur

#: De la plus ancienne génération vivante à la plus jeune en âge de travailler.
GENERATIONS = range(1920, 2006)
#: Les âges de départ balayés, en années pleines.
AGES_DE_DEPART = range(50, 71)

#: (régime, paramètre) : premières et dernières années de départ où la règle
#: d'une génération peut basculer, et le texte qui le veut.
A_L_ANNEE_D_EFFET = {
    ("cafat_nouvelle_caledonie", "age"): (2023, 2026, (
        "délibération n° 458 du 8 janvier 2009, articles 1er à 4, rédaction de la "
        "délibération n° 59/CP du 24 février 2022 : « 60 ans et six mois à compter "
        "du 1er janvier 2023 », six mois de plus chaque 1er janvier jusqu'à 62 ans "
        "en 2026 (Juridoc, lu le 13 octobre 2026)")),
    ("cafat_nouvelle_caledonie", "duree"): (2023, 2026, (
        "même délibération : la durée qui évite l'abattement, 35 ans et 6 mois en "
        "2023, six mois de plus par an jusqu'à 37 ans")),
    ("cps_polynesie", "age"): (2020, 2023, (
        "loi du pays n° 2019-6 : l'âge légal suit l'année du départ, 60 ans et "
        "6 mois en 2020 jusqu'à 62 ans en 2023 (rapport 2020 du Conseil "
        "d'orientation et de suivi des retraites, source CPS, lu le 13 octobre "
        "2026)")),
    ("cps_polynesie", "duree"): (2020, 2023, (
        "même loi : la durée d'assurance suffisante, 429 mois en 2020 jusqu'à "
        "456 mois en 2023")),
    ("cps_polynesie_tranche_b", "age"): (2020, 2023, (
        "les conditions de la tranche B « sont identiques en tranche A et B "
        "depuis la réforme » (même rapport)")),
    ("fonctionnaires_pacifique", "age"): (2025, 2028, (
        "code des pensions de retraites des fonctionnaires de Nouvelle-Calédonie, "
        "Lp. 221-1, loi du pays n° 2024-10 : la condition d'âge s'apprécie « à la "
        "date d'admission à la retraite », 60 ans et 6 mois en 2025 jusqu'à "
        "62 ans en 2028")),
    ("cssm_mayotte", "age"): (2003, 2012, (
        "décret n° 2003-589, article 2 : 55 ans pour les pensions prenant effet "
        "en 2003, 2004 et 2005, un an de plus par an jusqu'à 60 ans en 2010 ; la "
        "génération depuis le décret n° 2012-1168")),
    ("cssm_mayotte", "duree"): (2003, 2018, (
        "décret n° 2003-589, article 9 : 64 trimestres pour les pensions prenant "
        "effet en 2003, quatre de plus chaque année jusqu'en 2017 ; la génération "
        "depuis 2018 (décret n° 2016-1246)")),
    ("cps_saint_pierre_et_miquelon", "duree"): (1987, 1998, (
        "décret n° 89-110, article 9 : la durée se lit à la date d'entrée en "
        "jouissance, 108 trimestres en 1987, puis 110 et quatre de plus par année "
        "civile jusqu'à 150")),
    ("crpnpac", "duree"): (2012, 2012, (
        "R. 426-11 du code de l'aviation civile, rédaction du décret "
        "n° 2011-1500 : trente annuités pour le taux plein des pensions prenant "
        "effet à compter du 1er janvier 2012, et non plus vingt-cinq")),
    ("crpnpac_tranche_2", "duree"): (2012, 2012, "la même caisse, la même règle"),
    ("opera_de_paris", "age"): (2002, 2002, (
        "décret n° 68-382, article 6, rédaction du décret n° 2002-347 du "
        "12 mars 2002 (LEGIARTI000006765539) : quarante ans pour tout le ballet "
        "dès le 14 mars 2002, quarante-cinq avant pour les hommes, sans "
        "disposition transitoire sur l'âge d'ouverture (lu le 14 octobre 2026)")),
    ("banque_de_france", "age"): (2008, 2012, (
        "règlement annexé au décret n° 2007-262, article 26 "
        "(LEGIARTI000006778516) : soixante ans pour les pensions qu'il régit, à "
        "compter du printemps 2007, que la fiche fait commencer en 2008 ; avant, "
        "les cinquante-cinq ans de l'ancien régime, non relus. Puis la table de "
        "l'article 72, par génération (lu le 14 octobre 2026). Les nés de 1949 "
        "à 1952, qui partaient à cinquante-cinq ans, ne peuvent plus partir "
        "avant soixante : leur premier départ sous le règlement tombe de 2009 "
        "à 2012")),
    ("banque_de_france", "duree"): (2008, 2012, (
        "même règlement, article 69 : la durée lue à la date où l'agent est "
        "susceptible de liquider, 150 trimestres jusqu'en mars 2007 ; avant la "
        "fiche de 2008, celle de l'ancien régime ; de 2009 à 2012, la même "
        "bascule, au premier départ que le règlement ouvre aux nés de 1949 à "
        "1952")),
    ("msa_non_salaries", "age"): (1986, 1986, (
        "loi n° 86-19 du 6 janvier 1986, article 11 (LEGIARTI000006757038) : "
        "soixante ans pour les pensions « prenant effet postérieurement au "
        "1er janvier 1986 », soixante-cinq avant (lu le 14 octobre 2026)")),
}

#: (régime, paramètre) : les années où la règle bascule aujourd'hui, et ce que
#: le relevé du 13 octobre 2026 en montre, faute d'en avoir lu le texte.
A_RELIRE = {
    **{(code, "duree"): (1983, 1983, (
        "générations 1920 à 1922 : 160 trimestres pour un départ d'avant le "
        "1er avril 1983, 150 après ; la durée que la fiche lit avant "
        "l'ordonnance de 1982 n'est celle d'aucun texte relu"))
       for code in ("agirc", "agirc_entreprises_nouvelles", "arrco",
                    "arrco_tranche_2", "ircantec")},
    ("asv_conventionnes", "age"): (2017, 2017, (
        "générations 1947 à 1954 : leur âge de la génération avant 2017, "
        "62 ans pour un départ de 2017 et après")),
    ("asv_conventionnes", "duree"): (2017, 2017, (
        "générations 1949 à 1954 : la durée change pour un départ de 2017 et "
        "après")),
    ("carmf_complementaire", "age"): (2017, 2017, (
        "générations 1947 à 1954 : 62 ans pour un départ de 2017 et après")),
    ("carmf_complementaire", "duree"): (2000, 2000, (
        "générations 1930 à 1939 : la durée change pour un départ de 2000 et "
        "après")),
    ("carpimko_complementaire", "age"): (2016, 2016, (
        "générations 1952 et 1953 : 60 ans et 9 mois avant 2016, 60 ans après")),
    ("cavimac", "age"): (2007, 2007, (
        "générations 1937 à 1941 : 65 ans avant 2007, 60 ans après")),
    ("cese_membres", "duree"): (2005, 2014, (
        "générations 1935 à 1952 : la durée change en 2005, puis chaque année "
        "de 2011 à 2014")),
    ("cnavpl", "age"): (2004, 2004, (
        "générations 1934 à 1938 : 65 ans avant 2004, 60 ans après, même pour "
        "qui avait déjà 65 ans")),
    ("cnavpl", "duree"): (2004, 2004, (
        "générations 1934 à 1938 : la durée de la génération pour un départ de "
        "2004 et après")),
    ("cnbf", "age"): (2004, 2004, "comme la CNAVPL"),
    ("cnbf", "duree"): (2004, 2004, "comme la CNAVPL"),
    ("comedie_francaise", "age"): (1993, 1997, (
        "générations 1923 à 1937 : 55 ans avant le décret du 25 mars 1993, "
        "60 ans après, même pour qui avait déjà 55 ans")),
    ("cprn_complementaire", "age"): (2014, 2024, (
        "générations 1952 à 1959 : 64 ans pour un départ de 2014 à 2023, 62 ans "
        "avant et après")),
}


@pytest.fixture(scope="module")
def releve():
    """Pour chaque (régime, paramètre), les générations dont la règle change
    avec l'année du départ, et ces années ; et les départs sans période dans
    un régime ouvert."""
    simulateur = Simulateur()
    scenario = simulateur.scenario_actuel
    affiliations = Affiliations(RACINE_DONNEES)
    # (régime, statut, génération) -> [(âge de départ, année, âge, durée)]
    lu = defaultdict(list)
    lacunes = []
    for statut in affiliations.codes:
        periodes_du_statut = affiliations.periodes(statut)
        for generation in GENERATIONS:
            partie_a_70 = simulateur.carriere_simple(
                annee_naissance=generation, sexe="H", affiliation=statut,
                age_debut=22, age_liquidation=70,
            )
            for age_depart in AGES_DE_DEPART:
                carriere = dataclasses.replace(partie_a_70,
                                               age_liquidation=age_depart)
                annee = carriere.annee_liquidation
                codes = {code for p in periodes_du_statut
                         if p["debut"] <= annee <= (p.get("fin") or 9999)
                         for code in p["regimes"]}
                for code in sorted(codes):
                    if code not in simulateur.catalogue:
                        continue
                    regime = simulateur.catalogue[code]
                    periode = regime.periode(annee)
                    if periode is None:
                        if regime.creation <= annee <= (regime.extinction or 9999):
                            lacunes.append((statut, code, generation, age_depart))
                        continue
                    lu[(code, statut, generation)].append((
                        age_depart, annee,
                        round(ouvrir.age_ouverture(scenario, periode, carriere), 4),
                        ouvrir.duree_requise(scenario, periode, carriere)[0],
                    ))
    variations = defaultdict(lambda: defaultdict(set))
    for (code, statut, generation), departs in lu.items():
        # Les départs à l'âge d'ouverture ou après, dans l'ordre.
        apres = sorted(d for d in departs if d[0] + 1e-9 >= d[2])
        for rang, parametre in ((2, "age"), (3, "duree")):
            for avant, depart in zip(apres, apres[1:]):
                if depart[rang] != avant[rang]:
                    variations[(code, parametre)][(statut, generation)].add(depart[1])
    return variations, lacunes


def test_toute_generation_trouve_une_periode_dans_un_regime_ouvert(releve):
    """Une génération qui part l'année où son régime existe trouve une période
    de la fiche ; seule l'année d'avant la création, ou d'après l'extinction,
    n'en a pas."""
    _, lacunes = releve
    assert not lacunes, lacunes[:10]


def test_une_generation_garde_sa_regle_quelle_que_soit_l_annee_de_son_depart(releve):
    variations, _ = releve
    declares = {**A_L_ANNEE_D_EFFET, **A_RELIRE}
    hors = {}
    for cle, par_assure in variations.items():
        if cle not in declares:
            hors[cle] = sorted(par_assure.items())[:3]
            continue
        premiere, derniere, _ = declares[cle]
        annees = sorted({a for bascules in par_assure.values() for a in bascules})
        if annees[0] < premiere or annees[-1] > derniere:
            hors[cle] = (premiere, derniere, annees)
    assert not hors, (
        "L'âge d'ouverture ou la durée requise d'une génération change avec "
        "l'année de son départ, sans que le texte du régime soit déclaré le "
        f"vouloir : {hors}"
    )


def test_une_declaration_qui_ne_sert_plus_se_retire(releve):
    variations, _ = releve
    for nom, declaration in (("A_L_ANNEE_D_EFFET", A_L_ANNEE_D_EFFET),
                             ("A_RELIRE", A_RELIRE)):
        inutiles = sorted(set(declaration) - set(variations))
        assert not inutiles, f"{nom} : {inutiles}"


def test_les_deux_registres_ne_se_recouvrent_pas():
    assert not set(A_L_ANNEE_D_EFFET) & set(A_RELIRE)
