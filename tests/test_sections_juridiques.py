"""Ce que les règlements des sections juridiques servent, lus au texte.

La passe du 23 septembre 2026 sur les professions juridiques (action 89) a lu
les statuts et les règlements de la CAVOM et de la CPRN au Journal officiel,
et les barèmes de la CNBF. Ce fichier tient ce qu'elle a corrigé.

**La CAVOM a ses âges.** L'article 14 de ses statuts dans la rédaction de
l'arrêté du 12 décembre 2024, puis l'article 1er du règlement que l'arrêté du
10 juillet 2026 approuve, les écrivent génération par génération : ouverture à
soixante ans et taux plein à soixante-cinq avant la génération 1956, six mois
de plus par génération jusqu'à 62 et 67 ans pour celle de 1959, puis
l'ouverture portée à 64 ans de 1965 à 1968. La fiche lisait les tables du
régime général.

**Sa minoration compte des années, et seul l'âge l'annule.** « Ce coefficient
est fixé à 5 % par année manquante entre l'âge auquel est demandée la
liquidation de la retraite […] et l'âge prévu au 2°. Ce coefficient n'est pas
susceptible de fractionnement. » La fiche lui opposait la décote du régime de
base, que la durée d'assurance annule : un officier ministériel parti à
soixante-quatre ans avec sa durée ne perdait rien de sa complémentaire.

**Son plafond est monté par marches.** Le décret n° 2015-1875 appelle la
cotisation proportionnelle de 2016 dans la limite de quatre plafonds, puis
cinq, six et sept, avant les huit de 2020 ; l'assiette ne peut descendre sous
le quart du plafond, puis sous 19 % depuis 2019.

**La décote de la CPRN ne connaît que l'âge.** « 1,25 % par trimestre séparant
l'âge de l'affilié à la date de liquidation de l'âge du taux plein », écrivent
ses statuts depuis 2014 ; la fiche laissait la durée d'assurance l'annuler. Et
de 2014 à 2023, cet âge n'était pas celui du régime général : l'âge légal
« différé de vingt-quatre mois », et le taux plein cinq ans plus tard — 64 et
69 ans pour les générations nées depuis 1955. Depuis 2024, une majoration de
10 % pour trois enfants.

**La surcote des avocats a deux taux.** 0,75 % par trimestre accompli de 2004
au 30 juin 2010, 1,25 % depuis le 1er juillet 2010 (R. 723-39 puis R. 653-3) ;
la fiche servait 0,75 % à tous.

**Trois enfants majorent aussi la base des libéraux et des avocats.** La loi
du 14 avril 2023 leur étend L. 351-12 (L. 643-1-1 et L. 653-3), et le
règlement de la complémentaire des avocats l'a suivie en 2024 ; aucune des
trois fiches ne la portait.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int,
              debut: float, liquidation: float, enfants: int = 0,
              niveau: float = 1.5):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance,
        sexe="H",
        metiers=[Metier(affiliation=affiliation, age_debut=debut,
                        niveau_salaire=niveau)],
        age_liquidation=liquidation,
        macro=simulateur.macro,
        nombre_enfants=enfants,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return resultat, {p.regime: p for p in resultat.pensions_par_regime}


def _coefficient(detail: str) -> float:
    """Le coefficient d'anticipation écrit dans le détail, 1 s'il n'y en a pas."""
    marque = "coefficient d'anticipation "
    if marque not in detail:
        return 1.0
    return float(detail.split(marque)[1].split()[0])


# -- la CAVOM ------------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # Avant 1956 : taux plein à 65 ans, quelle que soit la génération.
    (1945, 64.0, 0.95),
    (1955, 62.0, 0.85),
    (1955, 65.0, 1.0),
    # 66 ans pour la génération 1957 : quatre années manquantes à 62 ans.
    (1957, 62.0, 0.80),
    # 67 ans depuis 1959, et la durée n'y change rien.
    (1962, 64.0, 0.85),
    (1968, 64.0, 0.85),
    (1968, 67.0, 1.0),
])
def test_la_cavom_minore_de_cinq_pour_cent_par_annee_jusqu_a_son_age(
        simulateur, naissance, liquidation, coefficient):
    """Carrière complète commencée à 22 ans : la durée est réunie partout.

    C'est précisément le cas où la fiche ne minorait rien — la décote du
    régime de base s'annule par la durée. Le règlement de la CAVOM ne
    connaît que l'âge.
    """
    resultat, pensions = _calculer(simulateur, "officier_ministeriel",
                                   naissance, 22.0, liquidation)
    assert resultat.liquidation_ouverte
    cavom = pensions["cavom_complementaire"]
    assert cavom.montant > 0
    assert _coefficient(cavom.detail) == pytest.approx(coefficient)


def test_l_annee_entamee_compte_entiere(simulateur):
    """Deux ans et neuf mois avant l'âge du taux plein : trois années, 15 %.

    « Ce coefficient n'est pas susceptible de fractionnement » : le texte ne
    dit pas davantage, et le modèle compte l'année entamée, comme l'IRCEC
    l'écrit en toutes lettres pour la même règle.
    """
    _, pensions = _calculer(simulateur, "officier_ministeriel",
                            1962, 22.0, 64.25)
    assert _coefficient(pensions["cavom_complementaire"].detail) == pytest.approx(0.85)


def test_la_complementaire_ne_decide_pas_de_l_ouverture_de_la_base(simulateur):
    """Un officier ministériel né le 10 mars 1957, parti à soixante et un ans.

    Sa complémentaire s'ouvre à cet âge, sans condition de la base (statuts de
    la CAVOM, article 23, depuis le 1er janvier 2016 : « 1957 61 ans 66
    ans »), son régime de base à soixante-deux (L. 161-17-2) : la CAVOM le
    1er avril 2018, la base le 1er avril 2019. Jusqu'au 5 novembre 2026, le
    modèle refusait tout départ avant l'âge de la base (note
    ``130/2026-11-05-complementaire-avant-la-base-des-liberaux.md``).
    """
    carriere = Carriere.depuis_parcours(
        annee_naissance=1957, sexe="H", jour_naissance=10, mois_naissance=3,
        metiers=[Metier(affiliation="officier_ministeriel", age_debut=22.0,
                        niveau_salaire=1.5)],
        age_liquidation=61.0, macro=simulateur.macro)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    assert resultat.liquidation_ouverte
    assert [(d.date_effet, d.regimes, d.motif) for d in resultat.departs] == [
        ("2018-04-01", ("cavom_complementaire",), "depart"),
        ("2019-04-01", ("cnavpl",), "ouverture")]


def test_le_plafond_de_la_cavom_monte_par_marches(simulateur):
    """Quatre plafonds en 2016, huit en 2020 ; un minimum d'assiette partout."""
    regime = simulateur.catalogue["cavom_complementaire"]
    attendus = {
        2016: (4.0, 0.25), 2017: (5.0, 0.25), 2018: (6.0, 0.25),
        2019: (7.0, 0.19), 2020: (8.0, 0.19), 2026: (8.0, 0.19),
    }
    for annee, (plafonds, minimum) in attendus.items():
        (periode,) = regime.periodes_actives(annee)
        assert periode.bornes_assiette_en_pass() == (0.0, plafonds), annee
        assert periode.assiette_minimale_pass == pytest.approx(minimum), annee
        assert periode.taux_cotisation_retraite == pytest.approx(0.125), annee


#: La requête du formulaire d'un officier ministériel, au salaire de deux Smic.
REQUETE_D_OFFICIER_MINISTERIEL = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "25", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "primes": "0", "profil": "plat", "projection": "cor_reference",
    "salaire": "2", "sexe": "H", "stock": "prix", "table": "unisexe",
    "statut": "officier_ministeriel",
}

#: (naissance, âge demandé, inapte) : le coefficient que le texte oppose à la
#: pension de la CAVOM, posé à la main.
INAPTES_DE_LA_CAVOM = {
    # Né le 10 mars 1959, 62 ans, le 1er avril 2021 : cinq années avant 67 ans,
    # « 0,75 si la retraite est attribuée lorsque l'affilié est âgé de 62 ans ».
    ("1959-03-10", "62", "non"): 0.75,
    # Le même, inapte : « À partir de 62 ans » « En cas d'inaptitude au
    # travail », sans coefficient.
    ("1959-03-10", "62", "oui"): 1.0,
    # À 64 ans, le 1er avril 2023 : 0,85 ; inapte, sans coefficient.
    ("1959-03-10", "64", "non"): 0.85,
    ("1959-03-10", "64", "oui"): 1.0,
    # Né le 10 mars 1957, inapte, 62 ans le 1er avril 2019 ; né le 10 mars
    # 1955, le 1er avril 2017 : 62 ans atteints, sans coefficient.
    ("1957-03-10", "62", "oui"): 1.0,
    ("1955-03-10", "62", "oui"): 1.0,
    # Né le 10 novembre 1962, inapte : 62 ans le 10 novembre 2024, la pension
    # le 1er décembre 2024, sous les statuts de 2016 : sans coefficient.
    ("1962-11-10", "62", "oui"): 1.0,
    # Né le 10 décembre 1962, inapte : la pension le 1er janvier 2025, le jour
    # où les statuts de 2025 entrent en vigueur. L'inapte y ouvre ses droits à
    # 62 ans (1°, a), sans que le 2° le serve sans coefficient : cinq années
    # manquantes, « 5 % par année manquante », 0,75.
    ("1962-12-10", "62", "oui"): 0.75,
    # Né le 10 mars 1963, inapte, 62 ans le 1er avril 2025 : de même, 0,75.
    ("1963-03-10", "62", "oui"): 0.75,
}


@pytest.fixture(scope="module")
def inaptes_de_la_cavom():
    """Chaque cas, servi par le portage et refait au bit près par le moteur
    Python (``servi_et_refait``)."""
    from outils_pont import servi_et_refait

    cas = [{"cle": "|".join(cle),
            "requete": {**REQUETE_D_OFFICIER_MINISTERIEL, "naissance": cle[0],
                        "liquidation": cle[1],
                        **({"inaptitude": "oui"} if cle[2] == "oui" else {})}}
           for cle in INAPTES_DE_LA_CAVOM]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: {p["regime"]: p for p in servi["actuel"]["pensions_par_regime"]}
            for cle, servi in servis.items()}


@pytest.mark.parametrize("cle", INAPTES_DE_LA_CAVOM,
                         ids=["|".join(cle) for cle in INAPTES_DE_LA_CAVOM])
def test_la_cavom_sert_l_inapte_sans_coefficient_des_62_ans_de_2016_a_2024(
        inaptes_de_la_cavom, cle):
    """Statuts de la CAVOM, article 14, I, 1° (arrêté du 30 décembre 2015, en
    vigueur du 1er janvier 2016 au 31 décembre 2024) : la liquidation « peut
    intervenir : 1° À partir de 62 ans — En cas d'inaptitude au travail
    reconnue dans les conditions prévues aux articles 27 à 33 des statuts de
    la CNAVPL ; Ou avec application des coefficients d'anticipation
    suivants : 0,75 si la retraite est attribuée lorsque l'affilié est âgé de
    62 ans […] ». L'inapte de 62 ans est servi sans coefficient. Depuis le
    1er janvier 2025 (arrêté du 12 décembre 2024, 4°), l'inapte ouvre ses
    droits à 62 ans, et seuls les « affiliés ayant atteint l'âge de 67 ans »
    sont servis sans coefficient. Jusqu'au 13 novembre 2026, le modèle
    opposait à l'inapte de 2016 à 2024 le coefficient de son âge."""
    cavom = inaptes_de_la_cavom["|".join(cle)]["cavom_complementaire"]
    assert cavom["montant"] > 0
    assert _coefficient(cavom["detail"]) == pytest.approx(INAPTES_DE_LA_CAVOM[cle])


def test_l_inapte_de_la_cavom_recoit_un_tiers_de_plus_que_le_valide_de_62_ans(
        inaptes_de_la_cavom):
    """Né le 10 mars 1959, parti à 62 ans le 1er avril 2021 : le valide reçoit
    ses points × 0,75, l'inapte ses points entiers — la pension du premier
    divisée par 0,75, un tiers de plus (13 564,47 € et 18 085,96 € par an au
    cas posé, en euros de 2026 : 4 521,49 € de plus)."""
    valide = inaptes_de_la_cavom["1959-03-10|62|non"]["cavom_complementaire"]["montant"]
    inapte = inaptes_de_la_cavom["1959-03-10|62|oui"]["cavom_complementaire"]["montant"]
    assert valide == pytest.approx(13_564.47, abs=0.005)
    assert inapte == pytest.approx(valide / 0.75, abs=0.005)
    assert inapte - valide == pytest.approx(4_521.49, abs=0.005)


#: (naissance, âge demandé, inapte) : le jour où la CAVOM sert sa pension, posé
#: à la main, ou ``None`` quand les statuts de 2025 ne l'ouvrent pas à cet âge.
OUVERTURE_DE_L_INAPTE_DE_LA_CAVOM = {
    # Né le 10 mars 1965, inapte : « a) 62 ans pour les affiliés relevant du a
    # du 2° de l'article L. 643-4 », 62 ans le 10 mars 2027, la pension le
    # 1er avril 2027, premier jour du mois et du trimestre civil qui suivent.
    ("1965-03-10", "62", "oui"): "2027-04-01",
    # Le même, valide : « 62 ans et 6 mois ans pour les affiliés nés en
    # 1965 », le 10 septembre 2027. À 62 ans, rien ne s'ouvre.
    ("1965-03-10", "62", "non"): None,
    # Nés les 10 mars 1966 et 1967, inaptes : 62 ans, et non 63 ans ni 63 ans
    # et 6 mois ; les 1er avril 2028 et 2029.
    ("1966-03-10", "62", "oui"): "2028-04-01",
    ("1967-03-10", "62", "oui"): "2029-04-01",
    # Né le 10 mars 1968, inapte : 62 ans, et non « 64 ans à compter de la
    # génération 1968 » ; le 1er avril 2030. Valide, rien avant 64 ans.
    ("1968-03-10", "62", "oui"): "2030-04-01",
    ("1968-03-10", "62", "non"): None,
}


@pytest.fixture(scope="module")
def ouvertures_de_l_inapte_de_la_cavom():
    """Chaque cas, servi par le portage et refait au bit près par le moteur
    Python (``servi_et_refait``)."""
    from outils_pont import servi_et_refait

    cas = [{"cle": "|".join(cle),
            "requete": {**REQUETE_D_OFFICIER_MINISTERIEL, "naissance": cle[0],
                        "liquidation": cle[1],
                        **({"inaptitude": "oui"} if cle[2] == "oui" else {})}}
           for cle in OUVERTURE_DE_L_INAPTE_DE_LA_CAVOM]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


@pytest.mark.parametrize("cle", OUVERTURE_DE_L_INAPTE_DE_LA_CAVOM,
                         ids=["|".join(cle) for cle in OUVERTURE_DE_L_INAPTE_DE_LA_CAVOM])
def test_la_cavom_ouvre_l_inapte_a_62_ans_depuis_2025(
        ouvertures_de_l_inapte_de_la_cavom, cle):
    """Statuts de la CAVOM, article 14, dans la rédaction de l'arrêté du
    12 décembre 2024 (annexe, II, 4°, JORFARTI000050823056, en vigueur le
    1er janvier 2025), et règlement de 2026, article 1er, I
    (JORFARTI000054435969), mot pour mot : « 1° L'âge d'ouverture des droits à
    pensions est fixé à : a) 62 ans pour les affiliés relevant du a du 2° de
    l'article L. 643-4 du code de la sécurité sociale ; b) 64 ans à compter de
    la génération 1968. Pour les affiliés nés avant le 1er janvier 1968, cet
    âge est fixé à : […] - 62 ans et 6 mois ans pour les affiliés nés en
    1965 ; - 63 ans pour les affiliés nés en 1966 ; - 63 ans et 6 mois pour
    les affiliés nés en 1967 ». L. 643-4, 2°, a (LEGIARTI000047453026) :
    « Reconnus inaptes au travail dans les conditions prévues à l'article
    L. 643-5 ». L'inapte n'est pas servi sans coefficient : « 5 % par année
    manquante » jusqu'à 67 ans, cinq années, 0,75. Jusqu'au 13 novembre 2026,
    le modèle lui opposait l'âge de sa génération."""
    actuel = ouvertures_de_l_inapte_de_la_cavom["|".join(cle)]
    attendue = OUVERTURE_DE_L_INAPTE_DE_LA_CAVOM[cle]
    if attendue is None:
        assert not actuel["liquidation_ouverte"]
        return
    assert actuel["liquidation_ouverte"], actuel["motif_ouverture"]
    # La complémentaire au départ demandé ; la base, que l'inaptitude n'ouvre
    # pas ici à 62 ans (écart déclaré ailleurs), à l'âge de sa génération.
    assert actuel["departs"][0] == {"date_effet": attendue, "motif": "depart"}
    assert [d["motif"] for d in actuel["departs"][1:]] == ["ouverture"]
    pensions = {p["regime"]: p for p in actuel["pensions_par_regime"]}
    cavom = pensions["cavom_complementaire"]
    assert cavom["montant"] > 0
    assert "servie à partir" not in cavom["detail"]
    assert "servie à partir" in pensions["cnavpl"]["detail"]
    assert _coefficient(cavom["detail"]) == pytest.approx(0.75)


def test_l_inapte_de_la_cavom_ne_en_1965_gagne_six_mois_de_pension(
        ouvertures_de_l_inapte_de_la_cavom):
    """Né le 10 mars 1965, inapte : servi le 1er avril 2027 et non le
    1er octobre, six mois de sa pension de 16 635,98 € par an, 8 317,99 €
    (euros de 2026)."""
    actuel = ouvertures_de_l_inapte_de_la_cavom["1965-03-10|62|oui"]
    assert actuel["liquidation_ouverte"]
    (cavom,) = [p for p in actuel["pensions_par_regime"]
                if p["regime"] == "cavom_complementaire"]
    assert cavom["montant"] == pytest.approx(16_635.98, abs=0.005)
    assert cavom["montant"] / 2 == pytest.approx(8_317.99, abs=0.005)


# -- la CPRN -------------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # 2014-2023 : nés avant 1954, 60 et 65 ans.
    (1952, 62.0, 0.85),
    # 2014-2023 : génération 1958, taux plein à 69 ans ; vingt trimestres au
    # plus, soit 25 %.
    (1958, 64.0, 0.75),
    # Depuis 2024 : l'âge du 1° de L. 351-8, 67 ans ; la durée n'y change rien.
    (1958, 66.0, 0.95),
    (1962, 64.0, 0.85),
])
def test_la_decote_de_la_cprn_ne_connait_que_l_age(
        simulateur, naissance, liquidation, coefficient):
    """« 1,25 % par trimestre séparant l'âge de l'affilié à la date de
    liquidation de l'âge du taux plein » : une carrière complète n'y change
    rien, et l'âge du taux plein est celui des statuts de l'année."""
    resultat, pensions = _calculer(simulateur, "notaire", naissance, 22.0,
                                   liquidation)
    assert resultat.liquidation_ouverte
    cprn = pensions["cprn_complementaire"]
    assert cprn.montant > 0
    assert _coefficient(cprn.detail) == pytest.approx(coefficient)


def test_la_cprn_majore_de_dix_pour_cent_pour_trois_enfants_depuis_2024(simulateur):
    """Article 23 des statuts depuis l'arrêté du 29 novembre 2023."""
    avec, pensions = _calculer(simulateur, "notaire", 1962, 22.0, 67.0,
                               enfants=3)
    majoration = sum(a.montant for a in avec.avantages_appliques
                     if a.code == "majoration_enfants")
    assert majoration > 0
    assert majoration >= 0.10 * pensions["cprn_complementaire"].montant - 0.01
    sans, _ = _calculer(simulateur, "notaire", 1962, 22.0, 67.0, enfants=2)
    assert not [a for a in sans.avantages_appliques
                if a.code == "majoration_enfants"]


def test_chaque_version_de_la_cprn_est_portee_par_le_modele(simulateur):
    """Lue au droit le 5 novembre 2026 (action 130) : statuts récrits par
    l'arrêté du 16 décembre 2013 (articles 14 à 16), statuts de l'arrêté du
    31 mai 2017 (articles 18, 19, 21 et 23), récrits par celui du 29 novembre
    2023 (articles 18, 21 et 23), règlement de 2026 (articles 4, 5, 7 et 9) ;
    avant 2014, des statuts que le Journal officiel ne publie pas. Chaque
    premier du mois de 1949 à 2040, la période qui liquide une pension prenant
    effet ce jour porte les paramètres que chaque version lit. Les écarts que
    ces paramètres ne disent pas — l'âge d'avant 2014, le passage de 2024, le
    trimestre entamé, les 30 % par enfant à charge — sont déclarés dans la
    fiche."""
    from test_sections_sante import _chaque_version_est_portee

    _chaque_version_est_portee(simulateur, "cprn_complementaire",
                               "cprn_ages_decote_enfants", "liquidation.date_effet",
                               set(), 1949)


#: Ce que les statuts de la CPRN servent, lu au texte, joué dans les deux
#: moteurs sur la requête du formulaire (notaire, entré à 22 ans, deux salaires
#: moyens) : (naissance, âge demandé) → (date d'effet de la CPRN, servie à part
#: de la base, ou None, et le coefficient que dit le détail).
CPRN_AU_TEXTE = {
    # Statuts de 2017, articles 18 et 21 : né le 10 mars 1954, l'âge de
    # L. 161-17-2, 61 ans et 7 mois (D. 161-2-1-9, 5°), « différé de
    # vingt-quatre mois » : 63 ans et 7 mois le 10 octobre 2017, la pension le
    # 1er novembre 2017 ; le taux plein à 68 ans et 7 mois, le 10 octobre 2022 ;
    # 20 trimestres × 1,25 % = 25 %.
    ("1954-03-10", "62"): ("2017-11-01", "coefficient d'anticipation 0.7500"),
    # Statuts de 2014, article 16 : né le 10 mars 1950, le taux plein à 65 ans ;
    # parti à 67 ans le 1er avril 2017, 8 trimestres × 0,5 % = 4 %.
    ("1950-03-10", "67"): (None, "coefficient de majoration 1.0400"),
    # Statuts de 2024, article 23 : né le 10 mars 1957, le taux plein à 67 ans
    # (1° de L. 351-8) ; parti à 68 ans le 1er avril 2025, 4 trimestres × 1 % =
    # 4 %.
    ("1957-03-10", "68"): (None, "coefficient de majoration 1.0400"),
}


def test_la_cprn_sert_ses_ages_et_ses_coefficients_dans_les_deux_moteurs():
    from outils_pont import servi_et_refait

    requete = {
        "age_reference": "fixe_apres_bascule", "bascule": "2026",
        "conversion_acquis": "reference", "debut": "22", "emploi": "cor_2026",
        "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
        "primes": "0", "profil": "plat", "projection": "cor_reference",
        "salaire": "2", "sexe": "H", "stock": "prix", "table": "unisexe",
        "statut": "notaire",
    }
    cas = [{"cle": "|".join(cle),
            "requete": {**requete, "naissance": cle[0], "liquidation": cle[1]}}
           for cle in CPRN_AU_TEXTE]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    for cle, (date_effet, coefficient) in CPRN_AU_TEXTE.items():
        actuel = servis["|".join(cle)]["actuel"]
        (cprn,) = [p for p in actuel["pensions_par_regime"]
                   if p["regime"] == "cprn_complementaire"]
        assert coefficient in cprn["detail"], (cle, cprn["detail"])
        ouvertures = [d["date_effet"] for d in actuel["departs"] if d["motif"] == "ouverture"]
        assert ouvertures == ([date_effet] if date_effet else []), (cle, actuel["departs"])


# -- la CNBF -------------------------------------------------------------------


def test_la_surcote_des_avocats_passe_a_un_quart_le_1er_juillet_2010(simulateur):
    """R. 653-3 : « 0,75 % par trimestre accompli à compter du 1er janvier
    2004 et avant le 1er juillet 2010 et [...] 1,25 % par trimestre accompli à
    compter du 1er juillet 2010 ». La fiche servait 0,75 % à tous."""
    from retraite_notionnelle.calendrier import DateMois

    baremes = simulateur.scenario_actuel.surcote_baremes
    assert baremes.connait("cnbf")
    avril, juillet = DateMois(2010, 4), DateMois(2010, 7)
    coefficient, _ = baremes.coefficient("cnbf", [(avril, False), (juillet, False)])
    assert coefficient == pytest.approx(1.0 + 0.0075 + 0.0125)
    (periode,) = simulateur.catalogue["cnbf"].periodes_actives(2026)
    assert periode.surcote_bareme == "cnbf"


def test_un_avocat_qui_prolonge_au_dela_de_2010_surcote_aux_deux_taux(simulateur):
    """Né en 1945, entré à vingt ans, parti à soixante-huit ans en 2013 : la
    surcote court depuis 2005, vingt et un trimestres à 0,75 % puis dix à
    1,25 %, soit 28,25 % — là où la fiche en servait 24 %."""
    _, pensions = _calculer(simulateur, "avocat", 1945, 20.0, 68.0)
    assert "taux 128.250%" in pensions["cnbf"].detail


@pytest.mark.parametrize("statut,majorees", [
    # L. 653-3 pour la base, article 16-1 du règlement pour la complémentaire.
    ("avocat", ("cnbf", "cnbf_complementaire")),
    # L. 643-1-1 pour la base ; le règlement de la CAVOM n'en porte aucune.
    ("officier_ministeriel", ("cnavpl",)),
    # La CPRN depuis 2024, et la base avec elle.
    ("notaire", ("cnavpl", "cprn_complementaire")),
])
def test_trois_enfants_majorent_la_base_des_liberaux_et_des_avocats(
        simulateur, statut, majorees):
    """La loi du 14 avril 2023 étend L. 351-12 aux professions libérales et
    aux avocats, pour les pensions prenant effet depuis le 1er septembre 2023.
    Aucune des trois fiches ne la portait."""
    resultat, pensions = _calculer(simulateur, statut, 1962, 22.0, 67.0,
                                   enfants=3)
    majoration = sum(a.montant for a in resultat.avantages_appliques
                     if a.code == "majoration_enfants")
    attendue = 0.10 * sum(pensions[code].montant for code in majorees)
    assert majoration == pytest.approx(attendue, rel=1e-6)
