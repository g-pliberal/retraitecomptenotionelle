"""Ce que les règlements des sections de santé servent, lus au texte.

La passe du 23 septembre 2026 sur les professions de santé (action 89) a lu au
Journal officiel les statuts et les règlements de la CARMF, de la CARCDSF, de
la CAVP, de la CARPIMKO et de la CARPV, du plus ancien que l'index porte en
entier au règlement que l'arrêté du 10 juillet 2026 approuve. Ce fichier tient
ce qu'elle a corrigé.

**Trois de ces cinq complémentaires minorent par l'âge seul.** La CARCDSF, la
CAVP et la CARPV comptent les trimestres — ou les années — qui séparent de
l'âge de leur taux plein, et la durée d'assurance n'y change rien. Les fiches
leur opposaient la décote du régime de base, que la durée annule : un
dentiste, un pharmacien ou un vétérinaire parti à soixante-quatre ans avec sa
durée ne perdait rien de sa complémentaire, quand sa caisse lui en retire 15,
9 ou 5 %. Deux fiches croyaient le dire en laissant leur durée requise vide ;
le moteur lisait celle de la carrière.

**Les taux sont les leurs, et ont bougé.** La CARCDSF minore de 5 % par année
jusqu'en 2010, de 1,50 % par trimestre les nés depuis 1955 de 2011 à 2023, de
1,25 % depuis dans la limite de 15 %. La CAVP compte deux pentes depuis 2011 :
1,25 % par trimestre jusqu'à 65 ans, 0,5 % de 65 ans à l'âge du taux plein. La
CARMF, de 2000 à 2016, comptait des années d'âge.

**Les mères de la CARCDSF partent plus tôt au taux plein** — une année par
enfant, cinq au plus —, et la voie est exclusive de la minoration : l'âge
dont celle-ci se compte ne bouge pas.

**La CARPIMKO a ses âges** depuis 2015 : taux plein à 65 ans pour les
générations 1955 et antérieures, quatre mois de plus par génération jusqu'à
67 ans en 1961.

**Trois enfants majorent de 10 % les cinq complémentaires** — la CARMF depuis
1964, l'ASV depuis 1981, la CARCDSF et la CAVP depuis leurs premiers statuts
lus, la CARPV depuis 2022, la CARPIMKO depuis 2024. Aucune fiche ne la
portait.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.droit import ouvrir


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int,
              liquidation: float, debut: float = 21.0, sexe: str = "H",
              enfants: int = 0):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance,
        sexe=sexe,
        metiers=[Metier(affiliation=affiliation, age_debut=debut,
                        niveau_salaire=1.0)],
        age_liquidation=liquidation,
        macro=simulateur.macro,
        nombre_enfants=enfants,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return resultat, {p.regime: p for p in resultat.pensions_par_regime}


def _coefficient(detail: str) -> float:
    """Le coefficient écrit dans le détail d'une pension en points, 1 sans."""
    for marque in ("coefficient d'anticipation ", "coefficient de majoration "):
        if marque in detail:
            return float(detail.split(marque)[1].split()[0])
    return 1.0


# -- la CARCDSF ----------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # 2008-2010, statuts de 2007 : 5 % par année d'âge jusqu'à 65 ans, l'année
    # entamée comptant entière — 63 ans et 3 mois laissent deux années.
    (1945, 64.0, 0.95),
    (1945, 63.25, 0.90),
    # 2011-2023 : 1,50 % par trimestre pour les nés depuis 1955, jusqu'à 67 ans.
    (1955, 64.0, 0.82),
    # Entre les deux, le tableau publié en image : 1,25 % en tient lieu,
    # jusqu'à l'âge légal majoré de cinq ans (66 ans et 2 mois en 1953).
    (1953, 63.0, 0.8375),
    # Depuis 2024 : 1,25 % par trimestre, dans la limite de 15 %.
    (1975, 64.0, 0.85),
    (1965, 63.0, 0.85),
    (1975, 67.0, 1.0),
])
def test_la_carcdsf_minore_par_l_age_seul(simulateur, naissance, liquidation,
                                         coefficient):
    """Carrière commencée à 21 ans : la durée est réunie partout, et c'est
    précisément le cas où la fiche ne minorait rien."""
    resultat, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                                   naissance, liquidation)
    assert resultat.liquidation_ouverte
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(
        coefficient)


@pytest.mark.parametrize("naissance,liquidation,enfants,coefficient", [
    # « Si vous avez eu 2 enfants, vous pouvez bénéficier du taux plein pour ce
    # régime dès 65 ans » — la page de la caisse, lue le 23 septembre 2026.
    (1960, 65.0, 2, 1.0),
    # Trois mois plus tôt, la voie particulière est fermée, et la minoration se
    # compte depuis 67 ans : neuf trimestres, 11,25 %.
    (1960, 64.75, 2, 0.8875),
    # Cinq années au plus : sept enfants n'avancent pas davantage que cinq.
    (1960, 62.0, 7, 1.0),
    # Les statuts de 2007 l'écrivaient déjà : « à partir de 63 ans pour deux
    # enfants », quand le taux plein était à 65.
    (1945, 63.0, 2, 1.0),
])
def test_la_mere_part_au_taux_plein_une_annee_plus_tot_par_enfant(
        simulateur, naissance, liquidation, enfants, coefficient):
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            naissance, liquidation, sexe="F", enfants=enfants)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(
        coefficient)


def test_le_pere_n_a_pas_l_anticipation_des_meres(simulateur):
    """« Aux affiliées […] au titre de l'incidence sur leur vie professionnelle
    de la maternité » : le même dentiste, père de deux enfants, est minoré."""
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            1960, 65.0, sexe="H", enfants=2)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(0.90)


def test_la_carcdsf_majore_apres_son_age(simulateur):
    """Huit trimestres civils entiers après 67 ans, 1,25 % chacun depuis 2024.

    Avant 2011 la caisse ne majorait pas ; de 2011 à 2023, 1 % par trimestre.
    """
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            1957, 69.0)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(1.10)
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            1948, 67.0)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(1.08)
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            1943, 67.0)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(1.0)


# -- la CAVP -------------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # Deux pentes : quatre trimestres à 1,25 % jusqu'à 65 ans, huit à 0,5 %
    # de 65 à 67 ans.
    (1975, 64.0, 0.91),
    (1975, 66.0, 0.98),
    (1960, 62.0, 0.81),
    # 66 ans pour les générations 1953 à 1955 : quatre et quatre.
    (1954, 64.0, 0.93),
    # Avant 2012, 65 ans pour tous et 1,25 % par trimestre.
    (1945, 64.0, 0.95),
    (1975, 67.0, 1.0),
    # Le tableau annexé à l'article 15 par l'arrêté du 23 juin 2011
    # (JORFARTI000024270214) : nés avant le 30 juin 1951 inclus, « 62 ―
    # 15,00 % » ; nés de 1953 à 1955, « 62 ― 17,00 % », et la majoration,
    # « 68 4,00 % » ; les nés avant juillet 1951, « Pas de majoration de
    # pension pour un départ après 65 ans » — l'article 12 de 2011 leur donne
    # une majoration jusqu'à 66 ans, non tranché de 2011 à 2026, le règlement
    # de 2026 suivant le tableau ; depuis 1956, « jusqu'à cet âge augmenté de
    # 3 ans », douze trimestres à 0,5 %.
    (1950, 62.0, 0.85),
    (1955, 62.0, 0.83),
    (1954, 68.0, 1.04),
    (1950, 67.0, 1.0),
    (1960, 70.0, 1.06),
])
def test_la_cavp_minore_a_deux_pentes(simulateur, naissance, liquidation,
                                      coefficient):
    resultat, pensions = _calculer(simulateur, "pharmacien", naissance, liquidation)
    assert resultat.liquidation_ouverte
    assert _coefficient(pensions["cavp_complementaire"].detail) == pytest.approx(
        coefficient)


# -- la CARPV et la CARMF --------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    (1975, 64.0, 0.95),
    (1945, 64.0, 0.95),
    (1925, 64.0, 0.95),
    (1975, 65.0, 1.0),
])
def test_le_veterinaire_est_minore_jusqu_a_soixante_cinq_ans(
        simulateur, naissance, liquidation, coefficient):
    """« 1,25 % par trimestre manquant avant l'âge de soixante-cinq ans », que
    la durée d'assurance n'annule pas."""
    _, pensions = _calculer(simulateur, "veterinaire", naissance, liquidation)
    assert _coefficient(pensions["carpv_complementaire"].detail) == pytest.approx(
        coefficient)


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    (1945, 64.0, 0.95),
    # 2012 : deux ans et demi avant 65 ans, trois années, 0,85.
    (1950, 62.5, 0.85),
])
def test_la_carmf_de_2000_a_2016_compte_des_annees_d_age(
        simulateur, naissance, liquidation, coefficient):
    """« 0,75 à 60 ans, 0,80 à 61 ans, 0,85 à 62 ans, 0,90 à 63 ans, 0,95 à
    64 ans » : la durée n'y joue aucun rôle, et la fiche le disait sans que le
    moteur le lise."""
    _, pensions = _calculer(simulateur, "medecin_liberal", naissance, liquidation)
    assert _coefficient(pensions["carmf_complementaire"].detail) == pytest.approx(
        coefficient)


@pytest.mark.parametrize("naissance,liquidation", [(1945, 68.0), (1946, 70.0)])
def test_la_carmf_avant_2017_ne_majore_pas_apres_65_ans(
        simulateur, naissance, liquidation):
    """« Avant réforme », 100 % de 65 à 70 ans (CARMF, réunions de formation
    2018, diapositive 18) : le « différé » de l'article 32 suppose la
    cessation, et le modèle part en cessant."""
    _, pensions = _calculer(simulateur, "medecin_liberal", naissance, liquidation)
    assert _coefficient(pensions["carmf_complementaire"].detail) == pytest.approx(1.0)


# -- la CARPIMKO -----------------------------------------------------------------


def test_la_carpimko_arrete_sa_minoration_a_son_propre_age(simulateur):
    """Né en 1958, taux plein à 66 ans : la décote d'une carrière commencée à
    30 ans s'arrête à seize trimestres, là où l'âge du régime général en
    comptait vingt."""
    _, pensions = _calculer(simulateur, "auxiliaire_medical", 1958, 62.0, debut=30.0)
    assert _coefficient(pensions["carpimko_complementaire"].detail) == pytest.approx(0.80)


def test_la_carpimko_majore_depuis_son_age(simulateur):
    """Née en 1960, taux plein à 66 ans et 8 mois pour qui n'a pas la durée du
    régime de base : un trimestre civil entier avant 67 ans, 1,25 %. Qui l'a
    plus tôt est majoré dès qu'il l'atteint (article 12 ter)."""
    _, pensions = _calculer(simulateur, "auxiliaire_medical", 1960, 67.0, debut=30.0)
    assert _coefficient(pensions["carpimko_complementaire"].detail) == pytest.approx(1.0125)


#: Ce que le modèle ne porte pas d'une version lue de la CARPIMKO, et que sa
#: fiche déclare : les statuts du 31 juillet 2015 entrent en vigueur le
#: 3 octobre 2015, la table `carpimko_2016` le 1er janvier 2016
#: (`liquidation_regime_par_regime`, l'âge de la complémentaire sans la base).
CARPIMKO_HORS_DU_MODELE = {("statuts_de_2015", "2015-10-03", "2016-01-01")}


@pytest.mark.parametrize("fiche,date_qui_decide", [
    ("carpimko_ages_2015", "liquidation.date_effet"),
    ("carpimko_assiette_2026", "revenu.annee"),
])
def test_chaque_version_de_la_carpimko_est_portee_par_le_modele(
        simulateur, fiche, date_qui_decide):
    """Lues au droit le 5 novembre 2026 (action 130) : statuts de 1984
    (articles 10 à 12, LEGI), de 2015, de 2019 et de 2024, règlement de 2026,
    pour les âges ; décret n° 84-143, article 2, rédaction du décret
    n° 2025-1076, pour l'assiette. Chaque premier du mois de 1984 à 2040 que
    couvre une version, la période qui liquide une pension prenant effet ce
    jour — ou, pour l'assiette, la période de l'année du revenu — porte chacun
    des paramètres que la version lit, hors de ce que la fiche déclare
    (`CARPIMKO_HORS_DU_MODELE`). Les écarts au texte que ces paramètres ne
    disent pas — la durée qui annule l'abattement, l'âge seul de 1984, les
    4 % par année des générations 1955 et antérieures de 2015 à 2024, le
    trimestre civil de la date d'effet — sont déclarés dans les fiches."""
    _chaque_version_est_portee(simulateur, "carpimko_complementaire", fiche,
                               date_qui_decide, CARPIMKO_HORS_DU_MODELE, 1984)


#: Ce que le modèle ne porte pas d'une version de la CAVP, et que sa fiche
#: déclare : la période de 2009 sert la règle des statuts du 11 mai 2009 dès
#: le 1er janvier 2009, quand ils n'entrent en vigueur que le 7 juin ; celle
#: de 2012, les deux pentes et la majoration de l'arrêté du 23 juin 2011, en
#: vigueur le 30 juin 2011 — sans effet sur aucune pension de 2011 dans la
#: lecture du tableau annexé, nul né après le 30 juin 1951 n'ayant alors
#: soixante-cinq ans, ni né après 1952 l'âge d'ouverture ; l'article 12 majore
#: aussi les nés jusqu'au 30 juin 1951, ce que la fiche déclare non tranché.
CAVP_HORS_DU_MODELE = {("statuts_d_avant_2009", "2009-01-01", "2009-06-07"),
                       ("statuts_de_2011", "2011-06-30", "2012-01-01")}


def test_chaque_version_de_la_cavp_est_portee_par_le_modele(simulateur):
    """Lue au droit le 5 novembre 2026 (action 130) : statuts du 11 mai 2009,
    articles 12, 14, 15 et 17 ; leurs articles 12 et 15 récrits par l'arrêté du
    23 juin 2011, son annexe à l'article 15 comprise ; l'article 15 récrit par
    l'arrêté du 19 décembre 2023 ; règlement de 2026, articles 8, 12, 14 et 15.
    Chaque premier du mois de 1949 à 2040, la période qui liquide une pension
    prenant effet ce jour porte les paramètres que chaque version lit, hors de
    ce que la fiche déclare (`CAVP_HORS_DU_MODELE`). Les écarts que ces
    paramètres ne disent pas — la carrière longue depuis 2024, la date d'effet
    au trimestre civil, la valeur de service par génération — sont déclarés
    dans la fiche."""
    _chaque_version_est_portee(simulateur, "cavp_complementaire",
                               "cavp_minoration_deux_pentes", "liquidation.date_effet",
                               CAVP_HORS_DU_MODELE, 1949)


@pytest.mark.parametrize("regime,fiche,date_qui_decide", [
    ("carmf_complementaire", "carmf_asv_minoration_enfants", "liquidation.date_effet"),
    ("asv_conventionnes", "carmf_asv_minoration_enfants", "liquidation.date_effet"),
    ("asv_conventionnes", "asv_medecins_ajustement", "revenu.annee"),
])
def test_chaque_version_de_la_carmf_est_portee_par_le_modele(
        simulateur, regime, fiche, date_qui_decide):
    """Lue au droit le 6 novembre 2026 (action 130) : l'article 15 des statuts
    du régime complémentaire et l'article 12 de ceux de l'ASV, récrits par les
    arrêtés des 30 novembre et 1er décembre 2016, puis par celui du 22 mars
    2017 ; le règlement de 2026, I, articles 2, 23 et 24, et III, articles 2
    et 8 ; le décret n° 2011-1644, articles 1er à 3 et 9. Avant 2017, des
    statuts que le Journal officiel ne publie pas. Chaque premier du mois de
    1949 à 2040, la période qui liquide une pension prenant effet ce jour — ou
    celle de l'année du revenu — porte les paramètres que chaque version lit.
    Les écarts que ces paramètres ne disent pas — l'âge légal de janvier à
    mars 2017, la date d'effet au trimestre civil, le revenu de l'avant-dernière
    année — sont déclarés dans les fiches."""
    _chaque_version_est_portee(simulateur, regime, fiche, date_qui_decide, set(), 1949)


#: Ce que l'article 15 des statuts du régime complémentaire de la CARMF et
#: l'article 12 de ceux de l'ASV servent depuis le 30 mars 2017, lu au texte,
#: joué dans les deux moteurs sur la requête du formulaire (médecin libéral,
#: entré à 22 ans, deux salaires moyens) : (naissance, âge demandé) → le
#: coefficient que dit le détail des deux régimes. « 1,25 % par trimestre
#: séparant le premier jour du trimestre civil suivant celui où le médecin
#: atteint [62 ans] de la date d'effet », « réduit à 0,75 % » du premier jour
#: du trimestre civil qui suit ses 65 ans, rien au-delà de celui qui suit ses
#: 70 ans.
CARMF_AU_TEXTE = {
    # Né le 10 mars 1955 : 62 ans le 10 mars 2017, le 1er avril 2017 ; parti à
    # 64 ans, la pension le 1er avril 2019 : 8 trimestres × 1,25 % = 10 %.
    ("1955-03-10", "64"): "coefficient de majoration 1.1000",
    # Né le 10 mars 1952 : du 1er avril 2014 au 1er avril 2017 (65 ans le 10
    # mars 2017), 12 × 1,25 % = 15 % ; parti à 65 ans et un mois, la pension le
    # 1er mai 2017 : aucun trimestre entier à 0,75 %.
    ("1952-03-10", "65.0833"): "coefficient de majoration 1.1500",
    # Né le 10 mars 1950 : du 1er avril 2012 au 1er avril 2015, 12 × 1,25 % ;
    # du 1er avril 2015 au 1er avril 2020 (70 ans), 20 × 0,75 % ; 30 %, quel
    # que soit le départ au-delà, ici le 1er avril 2021.
    ("1950-03-10", "71"): "coefficient de majoration 1.3000",
}


def test_la_carmf_sert_ses_coefficients_dans_les_deux_moteurs():
    from outils_pont import servi_et_refait

    requete = {
        "age_reference": "fixe_apres_bascule", "bascule": "2026",
        "conversion_acquis": "reference", "debut": "22", "emploi": "cor_2026",
        "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
        "primes": "0", "profil": "plat", "projection": "cor_reference",
        "salaire": "2", "sexe": "H", "stock": "prix", "table": "unisexe",
        "statut": "medecin_liberal",
    }
    cas = [{"cle": "|".join(cle),
            "requete": {**requete, "naissance": cle[0], "liquidation": cle[1]}}
           for cle in CARMF_AU_TEXTE]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    for cle, coefficient in CARMF_AU_TEXTE.items():
        pensions = {p["regime"]: p for p in servis["|".join(cle)]["actuel"]["pensions_par_regime"]}
        for regime in ("carmf_complementaire", "asv_conventionnes"):
            assert coefficient in pensions[regime]["detail"], (cle, regime)


def _chaque_version_est_portee(simulateur, regime, fiche, date_qui_decide, hors_du_modele,
                               depuis):
    """Chaque premier du mois depuis ``depuis`` jusqu'en 2040 que couvre une
    version de la fiche, la période du régime qui liquide une pension prenant
    effet ce jour — ou, sur l'année du revenu, la période de cette année —
    porte chacun des paramètres que la version lit, hors de ``hors_du_modele``
    (version, premier jour, jour de fin exclu)."""
    from datetime import date

    from retraite_notionnelle.noyau import carte

    caisse = simulateur.catalogue[regime]
    versions = carte.fiches()[fiche].get("versions") or []
    assert versions
    for version in versions:
        lus = (version.get("contenu") or {}).get("parametres") or {}
        debut, fin = version["bornes"][date_qui_decide]
        jour = max(debut or date(depuis, 1, 1), date(depuis, 1, 1))
        while jour < (fin or date(2041, 1, 1)):
            hors = any(v == version["id"] and date.fromisoformat(d) <= jour < date.fromisoformat(f)
                       for v, d, f in hors_du_modele)
            if lus and not hors:
                periode = (caisse.periode_a_l_effet(jour.isoformat())
                           if date_qui_decide == "liquidation.date_effet"
                           else caisse.periode(jour.year))
                assert {cle: getattr(periode, cle) for cle in lus} == lus, (version["id"], jour)
            jour = date(jour.year + jour.month // 12, jour.month % 12 + 1, 1)


# -- trois enfants ---------------------------------------------------------------


@pytest.mark.parametrize("statut", [
    "medecin_liberal", "chirurgien_dentiste_ou_sage_femme", "pharmacien",
    "auxiliaire_medical", "veterinaire",
])
def test_trois_enfants_majorent_toute_la_pension_en_2027(simulateur, statut):
    """En 2027, la base (L. 643-1-1) et chaque complémentaire majorent de 10 %.

    Les prestations complémentaires de vieillesse des auxiliaires médicaux
    n'ont aucune majoration que le guide de la CNAVPL nomme (2025, p. 95-96) :
    elles restent hors du compte.
    """
    resultat, pensions = _calculer(simulateur, statut, 1960, 67.0, sexe="F",
                                   enfants=3)
    majoration = sum(a.montant for a in resultat.avantages_appliques
                     if a.code == "majoration_enfants")
    majorees = [p.montant for code, p in pensions.items()
                if code != "asv_auxiliaires_medicaux"]
    assert majoration == pytest.approx(0.10 * sum(majorees))


def test_trois_enfants_majoraient_deja_les_complementaires_du_medecin(simulateur):
    """En 2010, la base ne majorait pas encore ; la CARMF (1964) et l'ASV
    (1981) le faisaient."""
    resultat, pensions = _calculer(simulateur, "medecin_liberal", 1945, 65.0,
                                   sexe="F", enfants=3)
    majoration = sum(a.montant for a in resultat.avantages_appliques
                     if a.code == "majoration_enfants")
    assert majoration == pytest.approx(0.10 * (pensions["carmf_complementaire"].montant
                                               + pensions["asv_conventionnes"].montant))


# -- l'âge du droit ---------------------------------------------------------------


@pytest.mark.parametrize("statut,naissance,age", [
    ("officier_ministeriel", 1955, 62.0),
    ("auxiliaire_medical", 1955, 62.0),
    ("pharmacien", 1950, 60.0),
])
def test_une_complementaire_qui_a_ses_ages_n_ouvre_pas_le_droit(
        simulateur, statut, naissance, age):
    """La CAVOM et la CARPIMKO s'ouvrent à 60 ans aux générations d'avant
    1956 ; le droit, lui, s'ouvre à l'âge du régime de base. Les règles d'âge
    des cas types proposaient soixante ans que le calcul refusait."""
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, sexe="H", affiliation=statut,
        age_debut=22.0, age_liquidation=64.0)
    actuel = simulateur.scenario_actuel
    assert ouvrir.age_ouverture_droit(actuel, carriere) == pytest.approx(age)
    # Et le taux plein de la carrière est celui de la base, non les 65 ans de
    # la complémentaire.
    assert ouvrir.age_taux_plein_droit(actuel, carriere) >= age
