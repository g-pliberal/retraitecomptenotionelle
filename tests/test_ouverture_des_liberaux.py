"""L'âge où s'ouvrent la base des libéraux et leurs sections (action 130, file L).

La base : « La liquidation de la pension prévue à l'article L. 643-1 peut être
demandée à partir de l'âge prévu au premier alinéa de l'article L. 351-1 »
(L. 643-3, I, rédactions de 2004 à 2026), « l'âge mentionné à l'article
L. 161-17-2 » (L. 351-1 depuis le 1er juillet 2011). Cet âge, pour une pension
qui prend effet :

- jusqu'au 31 août 2023, « soixante-deux ans pour les assurés nés à compter du
  1er janvier 1955 » (L. 161-17-2, LEGIARTI000025014605) ;
- du 1er septembre 2023 au 31 août 2026, « 6° Soixante-deux ans pour les
  assurés nés entre le 1er janvier 1955 et le 31 août 1961 inclus ; 7°
  Soixante-deux ans et trois mois pour les assurés nés entre le 1er septembre
  1961 et le 31 décembre 1961 inclus » (D. 161-2-1-9, LEGIARTI000047634502) ;
- depuis le 1er septembre 2026, « 3° Soixante-deux ans et neuf mois, pour les
  assurés nés entre le 1er janvier 1963 et le 31 mars 1965 » et « 7°
  Soixante-trois ans et neuf mois, pour les assurés nés en 1968 »
  (L. 161-17-2, LEGIARTI000053280889).

Les sections, lues dans leurs statuts : la CARPV sert sa retraite
complémentaire « dès leur soixantième anniversaire », aux seuls adhérents qui
ont « versé les cotisations exigibles de l'ensemble des régimes appelés par la
CARPV » (statuts de 2021, articles 33 et 34 ; règlement de 2026, articles 1er
et 2) ; la CAVEC la liquide « entre 60 et 65 ans, avec application d'un
abattement définitif de 1,25 % par trimestre manquant » (statuts de 2008,
article 3.13 ; de 2018, partie 2, article 12 ; règlement de 2026, article
1.1.3). Ni l'une ni l'autre ne demande que la base soit liquidée, ni L. 643-3,
ni L. 644-1 : chacune se demande à son âge. Les prestations des biologistes
directeurs de laboratoire, non : « Le biologiste remplissant les conditions
pour prétendre au versement de la prestation supplémentaire de vieillesse peut
demander à en bénéficier à partir de l'âge fixé à l'article L. 161-17-2 du
code de la sécurité sociale » (statuts de la CAVP, article 14, arrêté du
23 juin 2011, publié le 29 juin) ; « Le biologiste médical peut demander à
bénéficier de la prestation du présent régime à partir de l'âge fixé à
l'article L. 161-17-2 » (règlement de 2026, article 1er).

Le modèle prenait le plus bas des âges des régimes en points, et la CARPV, la
CAVEC et ces prestations, ouvertes à soixante ans, ouvraient la base avec
elles (relecture R-E-bis, note
``docs/feuille_de_route/130/2026-11-03-relecture-corrections-r-e.md``). Chaque
cas part de la requête du simulateur, servi par le portage et refait par le
moteur Python (``servi_et_refait``) : un libéral né le 10 de son mois, qui
demande son départ à soixante ans. Une pension prend effet au premier jour du
mois qui suit l'anniversaire de son âge (``Carriere.date_de_l_age``). Les
dates, posées à la main, sont dans la note
``docs/feuille_de_route/130/2026-11-04-ouverture-de-la-base-des-liberaux.md``.
"""

from __future__ import annotations

import re

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import departs, ouvrir
from retraite_notionnelle.simulateur import Simulateur

from outils_pont import servi_et_refait

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "26", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "liquidation": "60", "primes": "0", "profil": "plat",
    "projection": "cor_reference", "salaire": "2", "sexe": "H",
    "stock": "prix", "table": "unisexe",
}

#: La naissance, le mois où l'assuré a soixante ans, et celui où il a l'âge
#: de L. 161-17-2 (le premier jour du mois qui suit chaque anniversaire).
GENERATIONS = {
    # 62 ans (L. 161-17-2 de 2011) : le 10 février 2017.
    "1955": ("1955-02-10", "2015-03-01", "2017-03-01"),
    # 62 ans, une pension du 1er mars 2023 (L. 161-17-2 de 2011).
    "1961_fevrier": ("1961-02-10", "2021-03-01", "2023-03-01"),
    # 62 ans et 3 mois (D. 161-2-1-9, 7°) : le 10 janvier 2024.
    "1961_octobre": ("1961-10-10", "2021-11-01", "2024-02-01"),
    # 62 ans et 9 mois (L. 161-17-2 de 2026, 3°) : le 10 novembre 2026,
    # après le 1er septembre 2026 ; 63 ans avant (D. 161-2-1-9, 10°).
    "1964": ("1964-02-10", "2024-03-01", "2026-12-01"),
    # 63 ans et 9 mois (L. 161-17-2 de 2026, 7°) : le 10 novembre 2031.
    "1968": ("1968-02-10", "2028-03-01", "2031-12-01"),
}

#: Le statut, et la section qui se demande à soixante ans sans la base.
SECTIONS = {"veterinaire": "carpv_complementaire",
            "expert_comptable": "cavec_complementaire"}

COEFFICIENT = re.compile(r"coefficient d'anticipation ([\d.]+)")


def _cle(statut: str, generation: str) -> str:
    return f"{statut}|{generation}"


@pytest.fixture(scope="module")
def servis():
    cas = [{"cle": _cle(statut, generation),
            "requete": {**REQUETE, "statut": statut, "naissance": naissance}}
           for statut in (*SECTIONS, "biologiste_liberal")
           for generation, (naissance, _, _) in GENERATIONS.items()]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


@pytest.mark.parametrize("generation", GENERATIONS)
@pytest.mark.parametrize("statut", SECTIONS)
def test_la_section_se_sert_a_soixante_ans_et_la_base_a_l_age_legal(servis, statut,
                                                                    generation):
    """Parti à soixante ans, le vétérinaire touche la CARPV, l'expert-comptable
    la CAVEC, au départ ; la base de la CNAVPL attend l'âge de L. 161-17-2."""
    _naissance, soixante, legal = GENERATIONS[generation]
    actuel = servis[_cle(statut, generation)]
    assert actuel["liquidation_ouverte"], actuel["motif_ouverture"]
    assert actuel["departs"] == [{"date_effet": soixante, "motif": "depart"},
                                 {"date_effet": legal, "motif": "ouverture"}]


@pytest.mark.parametrize("statut", SECTIONS)
def test_la_section_partie_a_soixante_ans_est_minoree_de_vingt_trimestres(servis, statut):
    """« 1,25 % par trimestre manquant avant l'âge de soixante-cinq ans » (CARPV,
    2021, article 34) ; « entre 60 et 65 ans, [...] 1,25 % par trimestre
    manquant » (CAVEC, 2018, article 12) : à soixante ans, 20 × 1,25 % = 25 %,
    le coefficient 0,75."""
    actuel = servis[_cle(statut, "1964")]
    pension = next(p for p in actuel["pensions_par_regime"]
                   if p["regime"] == SECTIONS[statut])
    assert float(COEFFICIENT.search(pension["detail"]).group(1)) == 0.75, pension


@pytest.mark.parametrize("generation", GENERATIONS)
def test_le_biologiste_n_a_rien_a_soixante_ans(servis, generation):
    """Le biologiste libéral : la CNAVPL, la CAVP et les prestations des
    directeurs de laboratoire s'ouvrent à l'âge de L. 161-17-2 ; à soixante
    ans, rien ne lui est ouvert."""
    actuel = servis[_cle("biologiste_liberal", generation)]
    assert not actuel["liquidation_ouverte"]
    assert actuel["motif_ouverture"] == "non_ouverte"


# -- le jumeau Python : les régimes de chaque départ, et l'âge des cas types --

@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur, statut: str, naissance: int, liquidation: float) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe="H", metiers=[Metier(statut, 40.0)],
        age_liquidation=liquidation, macro=simulateur.macro, jour_naissance=10,
        mois_naissance=2)


@pytest.mark.parametrize("statut", SECTIONS)
def test_chaque_depart_ne_liquide_que_son_regime(simulateur, statut):
    """Né le 10 février 1964, parti à soixante ans : la section en mars 2024,
    la CNAVPL en décembre 2026, à 62 ans et 9 mois."""
    moteur = simulateur.scenario_actuel
    carriere = _carriere(simulateur, statut, 1964, 60)
    assert [(depart.date, sorted(depart.regimes), depart.motif)
            for depart in departs.departs(moteur, carriere)] == [
        (DateMois(2024, 3), [SECTIONS[statut]], departs.MOTIF_DEPART),
        (DateMois(2026, 12), ["cnavpl"], departs.MOTIF_OUVERTURE),
    ]


@pytest.mark.parametrize("statut", (*SECTIONS, "biologiste_liberal"))
@pytest.mark.parametrize("naissance, age", ((1955, 62.0), (1964, 62.75), (1968, 63.75)))
def test_le_cas_type_du_liberal_part_a_l_age_legal(simulateur, statut, naissance, age):
    """La grille date chaque cas type à l'âge où le droit s'ouvre : pour le
    libéral, celui de sa base."""
    carriere = _carriere(simulateur, statut, naissance, 70)
    assert ouvrir.age_ouverture_droit(simulateur.scenario_actuel, carriere) == age


# -- la base d'avant 2004 : l'allocation dès soixante ans, minorée --------------

#: « Les assurés peuvent recevoir à partir de l'âge de soixante ans et dans les
#: conditions fixées à l'article L. 643-5 une allocation de vieillesse [...]
#: affectée des coefficients d'anticipation déterminés comme suit : 1°) 0,75 si
#: l'allocation est attribuée lorsque l'assuré est âgé de soixante ans ; 2°)
#: 0,80 [...] soixante et un ans ; 3°) 0,85 [...] soixante-deux ans ; 4°) 0,90
#: [...] soixante-trois ans ; 5°) 0,95 [...] soixante-quatre ans » (R. 643-7,
#: LEGIARTI000006751830, du 21 décembre 1985 au 31 décembre 2003) ; sans
#: coefficient au « soixante-cinquième anniversaire » (R. 643-6,
#: LEGIARTI000006751828). Le libéral né le 10 février 1930 a chaque âge
#: entier au 1er mars, de 1990 à 1995.
AVANT_2004 = {"59": None, "60": 0.75, "61": 0.80, "62": 0.85, "63": 0.90,
              "64": 0.95, "65": 1.0}


@pytest.fixture(scope="module")
def avant_2004():
    cas = [{"cle": age, "requete": {**REQUETE, "statut": "profession_liberale",
                                    "naissance": "1930-02-10", "liquidation": age}}
           for age in AVANT_2004]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


@pytest.mark.parametrize("age", AVANT_2004)
def test_l_allocation_d_avant_2004_s_ouvre_a_soixante_ans_minoree(avant_2004, age):
    actuel = avant_2004[age]
    attendu = AVANT_2004[age]
    if attendu is None:
        assert not actuel["liquidation_ouverte"]
        return
    assert actuel["liquidation_ouverte"], actuel["motif_ouverture"]
    pension = next(p for p in actuel["pensions_par_regime"] if p["regime"] == "cnavpl")
    lu = COEFFICIENT.search(pension["detail"])
    assert (float(lu.group(1)) if lu else 1.0) == pytest.approx(attendu, abs=1e-9), pension


# -- le coefficient des biologistes, jusqu'à l'âge de L. 351-8, 1° ----------------

#: « La prestation supplémentaire de vieillesse est alors réduite par
#: application d'un coefficient d'anticipation qui est fonction du nombre de
#: trimestres manquants, à la date d'effet des droits, pour atteindre l'âge
#: fixé à l'article L. 351-8 (1°) du code de la sécurité sociale. Ce
#: coefficient est égal à 1,25% par trimestre manquant dans la limite de vingt
#: trimestres » (statuts de la CAVP, article 14, arrêté du 23 juin 2011,
#: JORFARTI000024270214 ; même phrase au règlement de 2026, III, article 1er,
#: JORFARTI000054436087). L. 351-8, 1° : « l'âge prévu à l'article L. 161-17-2
#: augmenté de cinq années » (LEGIARTI000023030950, pensions du 1er juillet 2011
#: au 31 janvier 2014 ; LEGIARTI000028498855, jusqu'au 31 août 2023) ; cet âge,
#: « 1° Soixante ans pour les assurés nés avant le 1er juillet 1951 ; [...]
#: 3° Soixante ans et neuf mois pour les assurés nés en 1952 ; 4° Soixante et
#: un ans et deux mois pour les assurés nés en 1953 » (D. 161-2-1-9,
#: LEGIARTI000025089933). Le biologiste né le 10 février part au 1er mars :
#: - en 1950, à 62 ans (2012) : 65 − 62 = 3 ans, 12 trimestres, 0,85 ;
#: - en 1952, à 63 ans (2015) : 65 ans 9 mois − 63 = 2 ans 9 mois, 11, 0,8625 ;
#: - en 1953, à 63 ans (2016) : 66 ans 2 mois − 63 = 3 ans 2 mois, 12,67,
#:   13 au trimestre supérieur, 0,8375.
#: Le modèle comptait jusqu'à 67 ans : 20, 16 et 16 trimestres (relecture R-L,
#: note ``docs/feuille_de_route/130/2026-11-04-relecture-ouverture-de-la-base-des-liberaux.md``).
BIOLOGISTES = {"1950-02-10": ("62", 0.85), "1952-02-10": ("63", 0.8625),
               "1953-02-10": ("63", 0.8375)}


def test_le_biologiste_est_minore_jusqu_a_l_age_de_l_351_8():
    cas = [{"cle": naissance, "requete": {**REQUETE, "statut": "biologiste_liberal",
                                          "naissance": naissance, "liquidation": age}}
           for naissance, (age, _) in BIOLOGISTES.items()]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    lus = {}
    for naissance, servi in servis.items():
        pension = next(p for p in servi["actuel"]["pensions_par_regime"]
                       if p["regime"] == "asv_directeurs_laboratoire")
        lus[naissance] = float(COEFFICIENT.search(pension["detail"]).group(1))
    assert lus == {naissance: attendu for naissance, (_, attendu) in BIOLOGISTES.items()}


#: Avant les statuts de 2011, l'âge du 1° de L. 351-8 : « l'âge prévu au 1° de
#: l'article L. 351-8 est fixé à soixante-cinq ans » (R. 351-27, toutes ses
#: rédactions du 21 décembre 1985 au 3 juin 2011 : LEGIARTI000006749434,
#: LEGIARTI000006749435, LEGIARTI000006749436, LEGIARTI000020082993) ; L. 351-8
#: visait alors « un âge déterminé » (LEGIARTI000006742633, du 22 août 2003 au
#: 1er juillet 2011). Les statuts d'avant 2011 ne sont pas publiés au Journal
#: officiel : la fiche présume qu'ils renvoyaient au même âge que ceux de 2011,
#: et le coefficient de 1,25 % par trimestre. Né le 10 février, parti au
#: 1er mars :
#: - en 1943, à 62 ans (2005) : 65 − 62 = 3 ans, 12 trimestres, 0,85 ;
#: - en 1941, à 64 ans (2005) : 1 an, 4 trimestres, 0,95 ;
#: - en 1940, à 65 ans (2005) : aucun trimestre, 1 ;
#: - en 1946, à 62 ans (2008) : 12 trimestres, 0,85.
#: Le modèle comptait jusqu'à 67 ans, l'âge du guide de 2025, et prenait la
#: durée quand elle lui manquait de moins : 17, 9, 5 et 17 trimestres, 0,7875,
#: 0,8875, 0,9375 et 0,7875 (relecture R-L-bis, écart 2). À 65 ans, l'âge en
#: oppose moins que la durée dans les quatre cas : elle ne les décide plus.
BIOLOGISTES_AVANT_2009 = {"1943-02-10": ("62", 0.85), "1941-02-10": ("64", 0.95),
                          "1940-02-10": ("65", 1.0), "1946-02-10": ("62", 0.85)}


def test_avant_2009_le_biologiste_est_minore_jusqu_a_soixante_cinq_ans():
    cas = [{"cle": naissance, "requete": {**REQUETE, "statut": "biologiste_liberal",
                                          "naissance": naissance, "liquidation": age}}
           for naissance, (age, _) in BIOLOGISTES_AVANT_2009.items()]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    lus = {}
    for naissance, servi in servis.items():
        pension = next(p for p in servi["actuel"]["pensions_par_regime"]
                       if p["regime"] == "asv_directeurs_laboratoire")
        lu = COEFFICIENT.search(pension["detail"])
        lus[naissance] = float(lu.group(1)) if lu else 1.0
    assert lus == {naissance: attendu
                   for naissance, (_, attendu) in BIOLOGISTES_AVANT_2009.items()}
