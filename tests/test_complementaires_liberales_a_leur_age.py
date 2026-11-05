"""La complémentaire de la CAVOM, de la CARPIMKO et de la CPRN, à SON âge, sans la base
(action 130, file N de la vague 9).

Aucun de leurs statuts ne demande que la base soit liquidée ; chacun fixe son
propre âge, et la complémentaire se demande à cet âge, avant la base ou après.

- **CAVOM**, statuts approuvés par l'arrêté du 30 décembre 2015 (annexe,
  JORFARTI000031740853, publié le 31, en vigueur le 1er janvier 2016) :
  « La liquidation de la retraite, conditionnée à la cessation de toute
  activité professionnelle ressortissant de la caisse et au paiement à la
  caisse de toutes les cotisations et majorations exigibles, peut
  intervenir : 1° À partir de 62 ans » (article 14) ; « Pour les générations
  antérieures, les âges d'ouverture des droits à retraite et de bénéfice du
  taux plein évoluent selon le tableau ci-dessous : [...] 1957 61 ans 66
  ans » (article 23). Arrêté du 12 décembre 2024 (annexe, II, 4°,
  JORFARTI000050823056 ; « entrent en vigueur au 1er janvier 2025 »,
  JORFARTI000050823053) : « 1° L'âge d'ouverture des droits à pensions est
  fixé à : [...] - 62 ans pour les affiliés nés entre le 1er janvier 1959 et
  le 31 décembre 1964 inclus » (article 14).
- **CARPIMKO**, arrêté du 31 juillet 2015 (annexe, JORFARTI000031255547,
  publié le 2 octobre 2015) : « Par dérogation aux dispositions de l'article
  11, les conditions de liquidation des assurés des générations 1960 et
  antérieures sont les suivantes : GÉNÉRATION 1955 ET ANTÉRIEURE 1956 1957
  [...] Age prévu à l'article 11.2 (a) 60 ans 60 ans 4 mois 60 ans 8 mois »
  (article 12 quater) ; même table, « Âge minimal pour liquider sa retraite »,
  arrêté du 27 décembre 2023 (JORFARTI000048880643) et règlement de 2026,
  article 6 (JORFARTI000054435915), dont l'article 2 : « Pour bénéficier de
  la retraite complémentaire, les affiliés doivent avoir versé toutes les
  cotisations exigibles et avoir l'âge prévu par les dispositions des
  articles 3, 4 et 6 ».
- **CPRN**, arrêté du 16 décembre 2013 (annexe, JORFARTI000028387445 ;
  « Le présent arrêté prend effet au 1er janvier 2014 », JORFARTI000028387441),
  article 15 : « Pour les affiliés nés avant le 1er janvier 1954 : [...]
  l'âge légal d'ouverture des droits est fixé à 60 ans [...] Pour les
  affiliés nés à compter du 1er janvier 1954 : [...] l'âge légal d'ouverture
  des droits est celui visé à l'article L. 161-17-2 du code de la sécurité
  sociale différé de vingt-quatre mois » ; même phrase à l'article 18 des
  statuts de 2017 (JORFARTI000034975971).
- **CAVP**, le témoin : « L'affilié remplissant les conditions pour prétendre
  au versement de la pension de retraite du régime complémentaire peut
  demander à en bénéficier dès l'âge d'ouverture du droit à pension de
  retraite tel qu'il est fixé à l'article L. 161-17-2 du code de la sécurité
  sociale. A titre transitoire, pour les affiliés nés avant le 1er janvier
  1956, l'âge d'ouverture du droit à pension de retraite est fixé selon le
  calendrier figurant à l'article D. 161-2-1-9 » (article 15, arrêté du
  23 juin 2011, JORFARTI000024270214) : l'âge de la base.

La base : « soixante-deux ans pour les assurés nés à compter du 1er janvier
1955 » (L. 161-17-2, LEGIARTI000025014605) ; « 4° Soixante et un ans et deux
mois pour les assurés nés en 1953 » (D. 161-2-1-9, LEGIARTI000025089933) ;
« 9° Soixante-deux ans et neuf mois pour les assurés nés en 1963 »
(D. 161-2-1-9, LEGIARTI000047634502). Chaque cas part de la requête du
simulateur, servi par le portage et refait par le moteur Python
(``servi_et_refait``) ; une pension prend effet au premier jour du mois qui
suit l'anniversaire de son âge, et chaque date tombe aussi au premier jour
d'un trimestre civil, la date d'effet de la CAVOM et de la CARPIMKO. Le
calcul de chaque date est posé à la main dans
``docs/feuille_de_route/130/2026-11-05-complementaire-avant-la-base-des-liberaux.md``.
"""

from __future__ import annotations

import pytest

from outils_pont import servi_et_refait

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "25", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "primes": "0", "profil": "plat", "projection": "cor_reference",
    "salaire": "2", "sexe": "H", "stock": "prix", "table": "unisexe",
}

#: (statut, naissance, âge demandé) : les départs attendus.
CAS = {
    # CAVOM, né le 10 mars 1957 : 61 ans le 10 mars 2018, la complémentaire le
    # 1er avril 2018 ; la base à 62 ans, le 10 mars 2019 : 1er avril 2019.
    ("officier_ministeriel", "1957-03-10", "61"): [
        {"date_effet": "2018-04-01", "motif": "depart"},
        {"date_effet": "2019-04-01", "motif": "ouverture"}],
    # CAVOM, né le 10 mars 1963 : 62 ans le 10 mars 2025, la complémentaire le
    # 1er avril 2025 ; la base à 62 ans et 9 mois, le 10 décembre 2025 :
    # 1er janvier 2026.
    ("officier_ministeriel", "1963-03-10", "62"): [
        {"date_effet": "2025-04-01", "motif": "depart"},
        {"date_effet": "2026-01-01", "motif": "ouverture"}],
    # CARPIMKO, né le 10 mars 1957 : 60 ans et 8 mois le 10 novembre 2017,
    # ouverte au départ demandé, 61 ans, le 1er avril 2018 ; la base le
    # 1er avril 2019.
    ("auxiliaire_medical", "1957-03-10", "61"): [
        {"date_effet": "2018-04-01", "motif": "depart"},
        {"date_effet": "2019-04-01", "motif": "ouverture"}],
    # CPRN, né le 10 septembre 1953 : 60 ans le 10 septembre 2013, ouverte au
    # départ demandé, 61 ans, le 1er octobre 2014 ; la base à 61 ans et
    # 2 mois, le 10 novembre 2014 : 1er décembre 2014.
    ("notaire", "1953-09-10", "61"): [
        {"date_effet": "2014-10-01", "motif": "depart"},
        {"date_effet": "2014-12-01", "motif": "ouverture"}],
    # CPRN, né le 10 mars 1956 : la base à 62 ans, le 1er avril 2018 ; la
    # complémentaire à 62 ans « différé de vingt-quatre mois », 64 ans, le
    # 10 mars 2020 : 1er avril 2020.
    ("notaire", "1956-03-10", "62"): [
        {"date_effet": "2018-04-01", "motif": "depart"},
        {"date_effet": "2020-04-01", "motif": "ouverture"}],
    # CAVP, né le 10 mars 1953 : la complémentaire et la base à 61 ans et
    # 2 mois ; à 62 ans, un seul départ.
    ("pharmacien", "1953-03-10", "62"): [],
}


@pytest.fixture(scope="module")
def servis():
    cas = [{"cle": "|".join(cle),
            "requete": {**REQUETE, "statut": cle[0], "naissance": cle[1],
                        "liquidation": cle[2]}}
           for cle in [*CAS, ("pharmacien", "1953-03-10", "61")]]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


@pytest.mark.parametrize("cle", CAS, ids=["|".join(cle) for cle in CAS])
def test_la_complementaire_se_sert_a_son_age_et_la_base_au_sien(servis, cle):
    actuel = servis["|".join(cle)]
    assert actuel["liquidation_ouverte"], actuel["motif_ouverture"]
    assert actuel["departs"] == CAS[cle]


def test_la_cavp_n_ouvre_pas_avant_l_age_de_la_base(servis):
    """Né le 10 mars 1953, à 61 ans : ni la CAVP ni la base, qui attendent
    61 ans et 2 mois."""
    actuel = servis["pharmacien|1953-03-10|61"]
    assert not actuel["liquidation_ouverte"]
