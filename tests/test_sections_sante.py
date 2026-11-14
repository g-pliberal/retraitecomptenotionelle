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
    """Née en janvier 1960, taux plein à 66 ans et 8 mois, en septembre 2026,
    pour qui n'a pas la durée du régime de base ; demandée à 67 ans, en janvier
    2027, la pension prend effet « au premier jour du trimestre civil qui suit
    la demande » (règlement de 2026, article 7), le 1er avril 2027 : deux
    trimestres civils entiers d'ajournement, d'octobre 2026 à mars 2027, 2,5 %
    — un seul, 1,25 %, tant que le modèle la servait le 1er février, jusqu'au
    14 novembre 2026. Qui a la durée plus tôt est majoré dès qu'il l'atteint
    (article 12 ter)."""
    _, pensions = _calculer(simulateur, "auxiliaire_medical", 1960, 67.0, debut=30.0)
    assert _coefficient(pensions["carpimko_complementaire"].detail) == pytest.approx(1.025)


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
    4 % par année des générations 1955 et antérieures de 2015 à 2024 — sont
    déclarés dans les fiches ; la date d'effet au trimestre civil, corrigée le
    14 novembre 2026, a son paramètre et ses essais
    (`tests/test_sections_liberales.py`)."""
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
    ce que la fiche déclare (`CAVP_HORS_DU_MODELE`). L'écart que ces
    paramètres ne disent pas — la valeur de service par génération — est
    déclaré dans la fiche ; la carrière longue depuis 2024, corrigée le
    14 novembre 2026, y est un paramètre, et la date d'effet au trimestre
    civil, corrigée le même jour, a le sien et ses essais
    (`tests/test_sections_liberales.py`)."""
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
    mars 2017, le revenu de l'avant-dernière année — sont déclarés dans les
    fiches ; la date d'effet au trimestre civil de la complémentaire, corrigée
    le 14 novembre 2026, a son paramètre et ses essais
    (`tests/test_sections_liberales.py`)."""
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


# -- les écarts de la relecture R-E7, corrigés (action 130, E6-bis) ---------------


def _a_plat(texte: str) -> str:
    """Un texte sans guillemets, ses espaces ramenées à une : la forme où une
    citation de la fiche et le texte de l'index se comparent."""
    import re

    return " ".join(re.sub(r"[«»\"]", " ", texte).split())


def _chaines(valeur):
    """Toutes les chaînes d'une fiche, à plat."""
    if isinstance(valeur, str):
        yield valeur
    elif isinstance(valeur, dict):
        for sous in valeur.values():
            yield from _chaines(sous)
    elif isinstance(valeur, (list, tuple)):
        for sous in valeur:
            yield from _chaines(sous)


def _textes_cites(fiche: dict) -> dict[str, str]:
    """Pour chaque identifiant que la fiche cite (ses versions et ses textes
    sans effet), les citations et les motifs mis bout à bout, à plat."""
    cites: dict[str, str] = {}
    for version in fiche.get("versions") or []:
        for texte in version.get("textes") or []:
            cites[texte["id"]] = cites.get(texte["id"], "") + " " + _a_plat(texte.get("citation") or "")
    for texte in fiche.get("textes_sans_effet") or []:
        cites[texte["id"]] = cites.get(texte["id"], "") + " " + _a_plat(texte.get("motif") or "")
    return cites


#: Ce que l'index JORF dit, lu le 6 novembre 2026 (index à jour au 3 novembre),
#: mot pour mot : l'article 12 ter des statuts de l'ASV, que l'arrêté du 28
#: septembre 2011 nomme et que celui du 1er décembre 2016 abroge, et l'article
#: 41 de la complémentaire, son jumeau pour la réversion.
DU_JORF_SUR_L_ARTICLE_12_TER = {
    "JORFARTI000024612007": (
        "Article 12 ter Au premier alinéa de l'article 12 ter, les mots : « dès l'âge de 60 "
        "ans » sont remplacés par les mots : « dès l'âge prévu à l'article L. 161-17-2 du "
        "code de la sécurité sociale »"),
    "JORFARTI000033538061": (
        "4° L'article 12 ter est abrogé ; 5° L'article 15 est ainsi modifié : a. Au dernier "
        "alinéa, les mots : « au titre de l'article 12 ter » sont remplacés par les mots : "
        "« avant le 1er janvier 2017 »"),
    "JORFARTI000033521562": (
        "4° L'article 41 est ainsi modifié : a) Au deuxième alinéa, les mots : « demandé la "
        "liquidation de ses droits par anticipation au titre de l'article 15 » sont "
        "remplacés par les mots : « liquidé ses droits par anticipation avant le 1er "
        "janvier 2017 au titre de l'article 15 »"),
}

#: Le rectificatif du 8 août 2026 (JORFARTI000054642802), tout ce qu'il dit.
RECTIFICATIF_DU_8_AOUT_2026 = (
    "Dans l'annexe, au lieu de lire : « Article 6 « Chapitre 2 « Médecins en cumul "
    "activité/retraite « Le conseil d'administration détermine, chaque année, la valeur "
    "du point de retraite. », lire : « Article 6 « Le conseil d'administration détermine, "
    "chaque année, la valeur du point de retraite. « Chapitre 2 « Médecins en cumul "
    "activité/retraite »")


def test_la_fiche_de_la_carmf_cite_l_article_12_ter_de_l_asv():
    """R-E7, point 5 : l'ASV avait, avant 2017, un article 12 ter, que
    l'arrêté du 28 septembre 2011 récrit (« dès l'âge de 60 ans ») et que celui
    du 1er décembre 2016 abroge ; sa réversion le citait, comme celle de la
    complémentaire citait la liquidation par anticipation de l'article 15. La
    fiche cite ces trois phrases, mot pour mot, à leur place."""
    from retraite_notionnelle.noyau import carte

    cites = _textes_cites(carte.fiches()["carmf_asv_minoration_enfants"])
    for identifiant, phrase in DU_JORF_SUR_L_ARTICLE_12_TER.items():
        assert _a_plat(phrase) in cites.get(identifiant, ""), identifiant


def test_le_rectificatif_du_8_aout_2026_est_lu_et_sans_effet():
    """R-E7, point 3 : l'index porte l'article du rectificatif ; il ne déplace
    qu'un intitulé de chapitre, et la fiche ne le dit plus « pas lu »."""
    from retraite_notionnelle.noyau import carte

    fiche = carte.fiches()["carmf_asv_minoration_enfants"]
    sans_effet = {t["id"] for t in fiche["textes_sans_effet"]}
    assert "JORFARTI000054642802" in sans_effet
    assert _a_plat(RECTIFICATIF_DU_8_AOUT_2026) in _textes_cites(fiche)["JORFARTI000054642802"]
    approximations = _a_plat(" ".join(_chaines(fiche["approximations"])))
    assert "Le rectificatif du 8 août 2026 n'est pas lu" not in approximations
    assert "JORFTEXT000054642801" not in approximations
    assert not any("rectificatif" in a for a in _chaines(fiche["sources"]["a_relire"]))


def test_l_age_legal_des_nes_en_1964_est_celui_de_l_161_17_2():
    """R-E7, point 4 : pour les pensions prenant effet depuis le 1er septembre
    2026, L. 161-17-2, rédaction de la loi n° 2025-1403 (LEGIARTI000053280889),
    fixe « 3° Soixante-deux ans et neuf mois, pour les assurés nés entre le 1
    er janvier 1963 et le 31 mars 1965 » ; D. 161-2-1-9, 10°, qui disait 63
    ans, n'est plus le texte. La fiche cite le premier ; le modèle ouvre déjà
    à 62 ans et 9 mois (62,75) les nés en 1964, non à 62,5 — dans les deux
    moteurs —, si bien que les cas de la fiche, partis à 63 ans et au-delà,
    n'en changent pas."""
    from outils_pont import servi_et_refait
    from retraite_notionnelle.noyau import carte

    fiche = carte.fiches()["carmf_asv_minoration_enfants"]
    tout = _a_plat(" ".join(_chaines(fiche)))
    assert "LEGIARTI000053280889" in tout
    assert _a_plat("3° Soixante-deux ans et neuf mois, pour les assurés nés entre le 1 er "
                   "janvier 1963 et le 31 mars 1965") in tout

    requete = {
        "age_reference": "fixe_apres_bascule", "bascule": "2026",
        "conversion_acquis": "reference", "debut": "22", "emploi": "cor_2026",
        "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
        "primes": "0", "profil": "plat", "projection": "cor_reference",
        "salaire": "2", "sexe": "H", "stock": "prix", "table": "unisexe",
        "statut": "medecin_liberal", "naissance": "1964-05-10",
    }
    ages = ("62.5", "62.75", "63")
    servis, refus = servi_et_refait(
        [{"cle": age, "requete": {**requete, "liquidation": age}} for age in ages])
    assert refus == {}, refus
    assert [servis[age]["actuel"]["liquidation_ouverte"] for age in ages] == [False, True, True]
    assert servis["62.75"]["actuel"]["motif_ouverture"] == "age_legal"


def test_l_ajustement_de_l_avant_derniere_annee_se_chiffre_a_la_main():
    """R-E7, point 7. Exercice 2026, taux de 4 % (décret n° 2011-1644, article
    2, rédaction du décret n° 2025-1076), forfait total 5 751 € (3 × 1 917 €),
    valeur de service de 11,82 € (article 4, II, 3°). Revenu de 40 000 € en
    2024, que le décret prend (« la deuxième année précédant »), de 42 000 € en
    2026, que le modèle prend. Le décret : 18 × 1 600 / 5 751 = 5,0078 points,
    5,01 arrondis. Le modèle : 18 × 1 680 / 5 751 = 5,2582. L'assiette seule :
    18 × 80 / 5 751 = 0,2504 point, 0,2504 × 11,82 = 2,96 € de pension par
    exercice. Les 0,2482 point qu'on avait (5,2582 − 5,01) mêlaient à
    l'assiette l'arrondi du décret, 5,0078 → 5,01 (0,0022 point, 0,03 €), et
    faisaient 2,93 €."""
    from fractions import Fraction as F

    from retraite_notionnelle.noyau import carte

    forfait, taux, valeur = 3 * 1917, F(4, 100), F(1182, 100)
    decret = 18 * taux * 40_000 / forfait
    modele = 18 * taux * 42_000 / forfait
    assiette = modele - decret
    assert (round(float(decret), 4), round(float(modele), 4)) == (5.0078, 5.2582)
    assert round(float(assiette), 4) == 0.2504
    assert round(float(assiette * valeur), 2) == 2.96
    arrondi = F(501, 100) - decret
    assert round(float(arrondi), 4) == 0.0022 and round(float(arrondi * valeur), 2) == 0.03
    assert round(float(modele - F(501, 100)), 4) == 0.2482
    assert round(float((modele - F(501, 100)) * valeur), 2) == 2.93

    premiere = carte.fiches()["asv_medecins_ajustement"]["approximations"][0]
    assert "0,2504" in premiere["ecart"] and "0,2504 × 11,82 = 2,96 €" in premiere["effet"]
    assert "2,93" not in premiere["effet"]
    assert "0,2482" not in premiere["effet"]


def test_la_fiche_de_l_ajustement_cite_l_arrete_du_7_janvier_2025():
    """R-E7, point 8 : l'arrêté du 7 janvier 2025 (JORFARTI000050962838), IV,
    statuts de l'ASV, 3°, dit « l'avant dernière année » à l'article 8, dont
    le contenu n'est pas publié ; le décret n° 2011-1644 prime, et
    l'approximation demeure."""
    from retraite_notionnelle.noyau import carte

    fiche = carte.fiches()["asv_medecins_ajustement"]
    tout = _a_plat(" ".join(_chaines(fiche)))
    assert "JORFARTI000050962838" in tout
    assert _a_plat("3° Au premier alinéa de l'article 8, les mots : « l'année » sont "
                   "remplacés par les mots : « l'avant dernière année »") in tout


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


# -- la CARMF : la dispense des deux premières années (action 130, la file) --------

REQUETE_DE_MEDECIN = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "liquidation": "67", "primes": "0", "profil": "plat",
    "projection": "cor_reference", "salaire": "2", "sexe": "F", "stock": "prix",
    "table": "unisexe", "statut": "medecin_liberal",
}

#: (naissance, âge du début d'exercice) : la retraite complémentaire que la
#: CARMF sert à 67 ans, par an, en euros de 2026.
DEBUTS_A_LA_CARMF = {
    # Née le 1er janvier 2001, installée le 1er janvier 2027, à 26 ans : 2027 et
    # 2028, ses deux premières années d'exercice, sont dispensées, sans points.
    # Posé à la main (note `130/2026-11-06-e10-decret-2026-418.md`) : le modèle
    # servait 990 651,9421 € de cotisations revalorisées, dont 20 997,0503 € de
    # 2027 (0,118 × 87 370,5656 € l'année même, × 2,0366) et 21 141,5017 € de
    # 2028 ; 990 651,9421 − 42 138,5520 = 948 513,3901 ; × 0,0448 =
    # 42 493,3999 ; × 1,21 = 51 417,01 €, 2 284,25 € de moins que 53 701,26 €.
    ("2001-01-01", "26"): 51_417.01,
    # Née le 1er janvier 1987, installée le 1er janvier 2027, le jour de ses
    # 40 ans : elle a « atteint l'âge de 40 ans », rien n'est dispensé, et la
    # pension reste celle d'avant la correction.
    ("1987-01-01", "40"): 26_389.47,
    # Née le 1er janvier 1986, installée le 1er janvier 2025, à 39 ans : ses
    # deux premières années, 2025 et 2026, précèdent les cotisations que
    # l'article 4 du 1er juillet 2026 dispense de façon prouvée ; la pension
    # reste celle d'avant la correction (limite déclarée à la fiche).
    ("1986-01-01", "39"): 26_506.51,
}


@pytest.fixture(scope="module")
def debuts_a_la_carmf():
    """Chaque cas, servi par le portage et refait au bit près par le moteur
    Python (``servi_et_refait``)."""
    from outils_pont import servi_et_refait

    cas = [{"cle": "|".join(cle),
            "requete": {**REQUETE_DE_MEDECIN, "naissance": cle[0], "debut": cle[1]}}
           for cle in DEBUTS_A_LA_CARMF]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: {p["regime"]: p for p in servi["actuel"]["pensions_par_regime"]}
            for cle, servi in servis.items()}


@pytest.mark.parametrize("cle", DEBUTS_A_LA_CARMF,
                         ids=["|".join(cle) for cle in DEBUTS_A_LA_CARMF])
def test_la_carmf_dispense_sans_points_les_deux_premieres_annees_d_exercice(
        debuts_a_la_carmf, cle):
    """Décret n° 49-579, article 4, I, dans la rédaction du décret n° 2026-418
    (article 3), en vigueur le 1er juillet 2026 (LEGIARTI000054168136) : « Tout
    médecin obligatoirement affilié à la caisse est dispensé du paiement de la
    cotisation afférente au présent régime pendant les deux premières années
    d'exercice de la profession libérale si cet exercice débute alors qu'il
    n'a pas atteint l'âge de 40 ans. » Article 4-1, II (LEGIARTI000054168116) :
    « Les cotisations ou fractions de cotisations ayant fait l'objet d'une
    dispense au titre des I à III de l'article 4 ne donnent pas lieu à
    acquisition de points. » Jusqu'au 14 novembre 2026, le modèle faisait
    cotiser et acquérir ces deux années."""
    carmf = debuts_a_la_carmf["|".join(cle)]["carmf_complementaire"]
    assert carmf["montant"] == pytest.approx(DEBUTS_A_LA_CARMF[cle], abs=0.005)


def test_la_dispense_de_la_carmf_retire_2_284_euros_a_la_medecin_de_26_ans(
        debuts_a_la_carmf):
    """Au cas posé, les cotisations revalorisées tombent de 990 652 € à
    948 513 €, et la pension de 53 701,26 € à 51 417,01 € : 2 284,25 € par an.
    La base et l'ASV, que l'article ne vise pas, ne bougent pas. L'ASV, que
    le modèle servait 44 511,19 €, est depuis le 14 novembre 2026 à la valeur
    de service de 2026 portée aux prix, et non plus à celle de 2025 (1,75 % de
    hausse en 2026) : 44 511,19 / 1,0175 = 43 745,64 €."""
    pensions = debuts_a_la_carmf["2001-01-01|26"]
    assert "cotisations revalorisées 948,513 €" in pensions["carmf_complementaire"]["detail"]
    assert 53_701.26 - pensions["carmf_complementaire"]["montant"] == pytest.approx(
        2_284.25, abs=0.005)
    assert pensions["asv_conventionnes"]["montant"] == pytest.approx(43_745.64, abs=0.005)
    assert pensions["cnavpl"]["montant"] == pytest.approx(31_726.78, abs=0.005)


def _versees_au_compte(naissance: str, debut: str, annee: int,
                       requete: dict = REQUETE_DE_MEDECIN) -> dict:
    """Les cotisations de l'année que le compte notionnel reçoit, régime par
    régime, rendues par le portage et refaites par le moteur Python
    (``droit_et_refait``)."""
    from outils_pont import Saisies, droit_et_refait
    from retraite_notionnelle import pont

    requete = {**requete, "naissance": naissance, "debut": debut}
    saisies = Saisies()
    lus, refus = droit_et_refait(
        {"versees": ("compte.cotisation_annuelle.par_regime", pont.SIMULATEUR,
                     saisies.carriere(requete), annee)},
        saisies.simulateur(requete).parametres)
    assert refus == {}, refus
    return dict(lus["versees"])


def test_le_compte_ne_porte_pas_la_cotisation_que_la_carmf_dispense():
    """« Dispensé du paiement de la cotisation afférente au présent régime » :
    la médecin installée à 26 ans le 1er janvier 2027 ne verse rien à la
    complémentaire en 2027 ni en 2028 — 0,118 × 87 370,5656 = 10 309,73 € en
    2027, que le compte portait —, et le compte porte ce qui a été versé. La
    base et l'ASV, que l'article ne vise pas, restent dues ; la troisième
    année, la complémentaire l'est."""
    for annee in (2027, 2028):
        versees = _versees_au_compte("2001-01-01", "26", annee)
        assert "carmf_complementaire" not in versees, annee
        assert versees["cnavpl"] > 0 and versees["asv_conventionnes"] > 0
    assert _versees_au_compte("2001-01-01", "26", 2029)["carmf_complementaire"] > 0
    # Installée le jour de ses 40 ans : rien n'est dispensé.
    assert _versees_au_compte("1987-01-01", "40", 2027)["carmf_complementaire"] == (
        pytest.approx(10_309.73, abs=0.005))


# -- la CARCDSF : la part proportionnelle des deux premières années (action 130) ---

REQUETE_DE_DENTISTE = {**REQUETE_DE_MEDECIN, "statut": "chirurgien_dentiste_ou_sage_femme"}

#: (naissance, âge du début d'exercice) : la retraite complémentaire que la
#: CARCDSF sert à 67 ans, par an.
DEBUTS_A_LA_CARCDSF = {
    # Née le 1er janvier 2001, installée le 1er janvier 2027 : en 2027 et en
    # 2028, ses deux premières années civiles d'exercice, la part
    # proportionnelle est dispensée, sans droits ; le forfait et ses six points
    # restent. Posé à la main (note `130/2026-11-06-e10-decret-2026-418.md`) : le
    # modèle servait 876 611,8159 € de cotisations revalorisées, dont la part
    # proportionnelle de 2027, 0,1135 × (87 370,5656 − 0,65 × 49 237,47) =
    # 6 284,0648 € l'année même, × 2,0366 = 12 798,2854 €, et celle de 2028,
    # 12 886,3326 € ; 876 611,8159 − 25 684,6180 = 850 927,1979 ; × 0,0595 =
    # 50 630,17 €, 1 528,23 € de moins que 52 158,40 €.
    ("2001-01-01", "26"): 50_630.17,
    # Née le 1er janvier 1987, installée le 1er janvier 2027, à 40 ans : la
    # CARCDSF ne pose aucune condition d'âge, à l'inverse de la CARMF. Le
    # modèle servait 26 039,01 € ; les mêmes parts proportionnelles de 2027 et
    # de 2028, revalorisées jusqu'en 2054 (6 284,0648 × 1,0175^27 = 10 038,5258 ;
    # 6 438,0244 × 1,0175^26 = 10 107,5869), × 0,0595 = 1 198,69 € : 24 840,32 €.
    ("1987-01-01", "40"): 24_840.32,
    # Née le 1er janvier 1986, installée le 1er janvier 2012 : les statuts
    # approuvés par l'arrêté du 13 avril 2011, en vigueur le 1er juillet 2011,
    # écrivent la même dispense (article 11). Le modèle servait 35 644,53 € ;
    # la part proportionnelle de 2012, 5 853,1628 − 2 532,9286 (le forfait,
    # 2 690,40 € de 2020 ramenés par les prix) = 3 320,2342 €, × 1,993857
    # (les prix de 2013 à 2053, ceux de l'Insee puis 1,75 % par an), et celle
    # de 2013, 5 969,7377 − 2 555,0157 = 3 414,7220 €, × 1,976621 : 13 369,6858 ;
    # × 0,0595 = 795,50 € : 34 849,04 €.
    ("1986-01-01", "26"): 34_849.04,
    # Née le 1er janvier 1985, installée le 1er janvier 2011 : 2012, sa
    # deuxième année civile, est dispensée (3 320,2342 × 1,959565, les prix de
    # 2013 à 2052, × 0,0595 = 387,12 € de moins que 34 731,23 €) ; 2011, appelée
    # sous les statuts de 2007, qui ne dispensaient que « sur demande écrite »,
    # reste cotisée (limite déclarée à la fiche).
    ("1985-01-01", "26"): 34_344.11,
    # Née le 1er janvier 1984, installée le 1er janvier 2010 : ses deux
    # premières années précèdent les statuts de 2011, et la pension reste
    # celle d'avant la correction.
    ("1984-01-01", "26"): 33_842.09,
}


@pytest.fixture(scope="module")
def debuts_a_la_carcdsf():
    """Chaque cas, servi par le portage et refait au bit près par le moteur
    Python (``servi_et_refait``)."""
    from outils_pont import servi_et_refait

    cas = [{"cle": "|".join(cle),
            "requete": {**REQUETE_DE_DENTISTE, "naissance": cle[0], "debut": cle[1]}}
           for cle in DEBUTS_A_LA_CARCDSF]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: {p["regime"]: p for p in servi["actuel"]["pensions_par_regime"]}
            for cle, servi in servis.items()}


@pytest.mark.parametrize("cle", DEBUTS_A_LA_CARCDSF,
                         ids=["|".join(cle) for cle in DEBUTS_A_LA_CARCDSF])
def test_la_carcdsf_dispense_la_part_proportionnelle_des_deux_premieres_annees(
        debuts_a_la_carcdsf, cle):
    """Décret n° 50-28, article 3-1, dans la rédaction du décret n° 2026-418
    (article 5), en vigueur le 1er juillet 2026 (LEGIARTI000054168193) : « Les
    nouveaux affiliés sont dispensés de la cotisation proportionnelle au titre
    des deux premières années civiles de leur exercice ». Article 3-5
    (LEGIARTI000054168184) : « Les dispenses ou réductions partielles
    mentionnées aux articles 3-1 à 3-4 entraînent respectivement la suppression
    ou la réduction des droits correspondants. » Avant, les statuts approuvés
    par l'arrêté du 13 avril 2011, en vigueur le 1er juillet 2011
    (LEGIARTI000023910336), article 11 : « Les nouveaux adhérents sont
    dispensés de la cotisation proportionnelle au titre des deux premières
    années civiles de leur exercice », et article 16, la suppression des droits
    correspondants ; articles 13 et 18 depuis le 25 décembre 2017
    (LEGIARTI000036540562). Jusqu'au 14 novembre 2026, le modèle faisait
    cotiser et acquérir la part proportionnelle de ces deux années."""
    carcdsf = debuts_a_la_carcdsf["|".join(cle)]["carcdsf_complementaire"]
    assert carcdsf["montant"] == pytest.approx(DEBUTS_A_LA_CARCDSF[cle], abs=0.005)


def test_la_dispense_de_la_carcdsf_retire_1_528_euros_a_la_dentiste_de_26_ans(
        debuts_a_la_carcdsf):
    """Au cas posé, les cotisations revalorisées tombent de 876 612 € à
    850 927 €, et la pension de 52 158,40 € à 50 630,17 € : 1 528,23 € par an.
    La base et les prestations complémentaires de vieillesse, que l'article ne
    vise pas, ne bougent pas."""
    pensions = debuts_a_la_carcdsf["2001-01-01|26"]
    assert "cotisations revalorisées 850,927 €" in (
        pensions["carcdsf_complementaire"]["detail"])
    assert 52_158.40 - pensions["carcdsf_complementaire"]["montant"] == pytest.approx(
        1_528.23, abs=0.005)
    assert pensions["asv_chirurgiens_dentistes"]["montant"] == pytest.approx(
        26_394.77, abs=0.005)
    assert pensions["cnavpl"]["montant"] == pytest.approx(31_726.78, abs=0.005)


def test_le_compte_ne_porte_que_le_forfait_des_deux_premieres_annees_de_la_dentiste():
    """« Dispensés de la cotisation proportionnelle » : la dentiste installée
    le 1er janvier 2027 ne verse à la complémentaire, en 2027, que la
    cotisation forfaitaire — 3 210,60 € de 2026, que le modèle porte à
    3 210,60 × 1,0175 = 3 266,79 € en 2027 —, et non les 0,1135 × (87 370,5656
    − 0,65 × 49 237,47) = 6 284,06 € de plus que le compte portait (9 550,85 €) ;
    de même en 2028 (3 210,60 × 1,0175² = 3 323,95 €). La base et les
    prestations complémentaires de vieillesse restent dues ; la troisième
    année, la part proportionnelle l'est."""
    for annee, forfait in ((2027, 3_266.79), (2028, 3_323.95)):
        versees = _versees_au_compte("2001-01-01", "26", annee,
                                     requete=REQUETE_DE_DENTISTE)
        assert versees["carcdsf_complementaire"] == pytest.approx(forfait, abs=0.005)
        assert versees["cnavpl"] > 0 and versees["asv_chirurgiens_dentistes"] > 0
    assert _versees_au_compte("2001-01-01", "26", 2029, requete=REQUETE_DE_DENTISTE)[
        "carcdsf_complementaire"] == pytest.approx(9_977.88, abs=0.005)


# -- la CARMF : l'exemption passé 75 ans (action 130, la file, ligne 7) ------------

#: (naissance, âge du départ) : la retraite complémentaire que la CARMF sert à
#: la médecin libérale au double du salaire moyen, installée à 30 ans, par an,
#: en euros de 2026.
DEPARTS_PASSE_75_ANS = {
    # Née le 1er janvier 1951, partie à 76 ans et 6 mois, le 1er juillet 2027 :
    # 75 ans le 1er janvier 2026, exemptée du 1er juillet 2026. Le semestre de
    # 2027 n'est pas dû sous toute lecture. Posé à la main (note
    # `130/2026-11-06-e10-decret-2026-418.md`) : le modèle servait
    # 324 443,6335 € de cotisations revalorisées, dont 5 154,8634 € du semestre
    # de 2027 (0,118 × 87 370,5656 € / 2) ; 324 443,6335 − 5 154,8634 =
    # 319 288,7701 ; × 0,0448 = 14 304,1369 ; × 1,30 = 18 595,38 €, 300,22 € de
    # moins que 18 895,60 €. L'année 2026 reste cotisée en entier (limite
    # déclarée à la fiche : le partage de la cotisation au semestre).
    ("1951-01-01", "76.5"): 18_595.38,
    # Née le 1er juillet 1951, partie à 76 ans, le 1er juillet 2027 : 75 ans le
    # 1er juillet 2026, exemptée du 1er janvier 2027, le semestre civil qui
    # suit. Les mêmes cotisations, le même semestre de 2027 : 18 595,38 €.
    ("1951-07-01", "76"): 18_595.38,
    # Née le 1er janvier 1952, partie à 75 ans et 6 mois, le 1er juillet 2027 :
    # 75 ans le 1er janvier 2027, exemptée du 1er juillet 2027, le jour de son
    # départ. Rien n'est exempté, et la pension reste celle d'avant la
    # correction.
    ("1952-01-01", "75.5"): 18_665.63,
}


@pytest.fixture(scope="module")
def departs_passe_75_ans():
    """Chaque cas, servi par le portage et refait au bit près par le moteur
    Python (``servi_et_refait``)."""
    from outils_pont import servi_et_refait

    cas = [{"cle": "|".join(cle),
            "requete": {**REQUETE_DE_MEDECIN, "naissance": cle[0], "debut": "30",
                        "liquidation": cle[1]}}
           for cle in DEPARTS_PASSE_75_ANS]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: {p["regime"]: p for p in servi["actuel"]["pensions_par_regime"]}
            for cle, servi in servis.items()}


@pytest.mark.parametrize("cle", DEPARTS_PASSE_75_ANS,
                         ids=["|".join(cle) for cle in DEPARTS_PASSE_75_ANS])
def test_la_carmf_exempte_sans_points_passe_le_semestre_des_75_ans(
        departs_passe_75_ans, cle):
    """Décret n° 49-579, article 4, II, dans la rédaction du décret
    n° 2026-418 (article 3), en vigueur le 1er juillet 2026
    (LEGIARTI000054168136) : « Tout médecin qui continue d'exercer en qualité
    de non salarié est exempté du versement de la cotisation à partir du
    premier jour du semestre civil qui suit son soixante-quinzième
    anniversaire. » Article 4-1, II (LEGIARTI000054168116) : « Les cotisations
    ou fractions de cotisations ayant fait l'objet d'une dispense au titre des
    I à III de l'article 4 ne donnent pas lieu à acquisition de points. »
    Jusqu'au 14 novembre 2026, le modèle faisait cotiser et acquérir jusqu'au
    départ."""
    carmf = departs_passe_75_ans["|".join(cle)]["carmf_complementaire"]
    assert carmf["montant"] == pytest.approx(DEPARTS_PASSE_75_ANS[cle], abs=0.005)


def test_l_exemption_de_la_carmf_retire_300_euros_a_la_medecin_de_76_ans(
        departs_passe_75_ans):
    """Au cas posé, les cotisations revalorisées tombent de 324 444 € à
    319 289 €, et la pension de 18 895,60 € à 18 595,38 € : 300,22 € par an.
    La base et l'ASV, que l'article ne vise pas, ne bougent pas. L'ASV, que
    le modèle servait 22 383,12 €, est depuis le 14 novembre 2026 à la valeur
    de service de 2026 portée aux prix, et non plus à celle de 2025 (1,75 % de
    hausse en 2026) : 22 383,12 / 1,0175 = 21 998,15 €."""
    pensions = departs_passe_75_ans["1951-01-01|76.5"]
    assert "cotisations revalorisées 319,289 €" in pensions["carmf_complementaire"]["detail"]
    assert 18_895.60 - pensions["carmf_complementaire"]["montant"] == pytest.approx(
        300.22, abs=0.005)
    assert pensions["asv_conventionnes"]["montant"] == pytest.approx(21_998.15, abs=0.005)
    assert pensions["cnavpl"]["montant"] == pytest.approx(18_281.12, abs=0.005)


def test_le_compte_ne_porte_pas_la_cotisation_que_la_carmf_exempte_passe_75_ans():
    """« Exempté du versement de la cotisation » : la médecin née le 1er janvier
    1951 ne verse rien à la complémentaire au premier semestre de 2027 —
    0,118 × 87 370,5656 / 2 = 5 154,86 €, que le compte portait —, et le compte
    porte ce qui a été versé. La base et l'ASV, que l'article ne vise pas,
    restent dues ; l'année 2026, celle du semestre où l'exemption commence,
    reste cotisée. Née un an plus tard, elle doit encore ce semestre de 2027."""
    requete = {**REQUETE_DE_MEDECIN, "liquidation": "76.5"}
    versees = _versees_au_compte("1951-01-01", "30", 2027, requete=requete)
    assert "carmf_complementaire" not in versees
    assert versees["cnavpl"] > 0 and versees["asv_conventionnes"] > 0
    assert _versees_au_compte("1951-01-01", "30", 2026, requete=requete)[
        "carmf_complementaire"] > 0
    assert _versees_au_compte(
        "1952-01-01", "30", 2027, requete={**REQUETE_DE_MEDECIN, "liquidation": "75.5"})[
        "carmf_complementaire"] == pytest.approx(5_154.86, abs=0.005)


# -- l'ASV des médecins : la cotisation d'avant 2012 (action 130) ----------------

#: Année : (la cotisation du médecin, la fraction que les caisses y ajoutent),
#: en euros de l'année, là où la fiche ancre le tarif de la consultation ; un
#: franc vaut 1 / 6,55957 €. Les caisses versent « le double de la cotisation
#: des bénéficiaires » (D. 645-3, LEGIARTI000006738166, 168 et 169), ou, du
#: 30 mars 1993 au 8 juillet 1994, une cotisation « égale à la cotisation
#: exigible des bénéficiaires » (LEGIARTI000006738167).
COTISATIONS_DE_L_ASV_AU_TEXTE = {
    # D. 645-2 (LEGIARTI000006738371) : « pour les médecins, à trente fois la
    # valeur au 1er janvier de l'année en cause du tarif de la consultation »,
    # « appelée à concurrence de 75 p. 100 » (décret n° 72-968, article 6,
    # LEGIARTI000006765951). 30 × 75 F × 0,75 = 1 687,50 F.
    1985: (257.26, 2.0),
    # Article 6, rédaction du 8 juillet 1994 (LEGIARTI000006765957) : « Pour
    # l'exercice 1993 […] la cotisation est fixée à 43,333 2 fois la valeur au
    # 1er janvier 1993 du tarif ». 43,3332 × 100 F = 4 333,32 F.
    1993: (660.61, 1.0),
    # Décret n° 94-564, article 1er, II (JORFARTI000001585515) : « A compter du
    # 1er janvier 1994 […] cinquante-deux fois ». 52 × 100 F = 5 200 F.
    1994: (792.73, 2.0),
    1995: (792.73, 2.0),
    # D. 645-2 (LEGIARTI000006738376) : « soixante fois ». 60 × 110 F = 6 600 F.
    1999: (1_006.16, 2.0),
    # D. 645-2 (LEGIARTI000006738380) : « au titre de l'exercice 2004, à
    # soixante fois ». 60 × 20 € = 1 200 € : le cas posé de la note
    # `130/2026-11-13-relecture-asv-medecins-points.md`, 2 400 € des caisses.
    2004: (1_200.0, 2.0),
}

#: Année : le nombre de consultations que le médecin verse, l'appel compris,
#: sous l'article 6 du décret n° 72-968 (LEGIARTI000006765951 à 955) : 75 %
#: de trente fois ; « pour l'année 1988 […] trente et une fois », « pour
#: l'année 1990 […] 33 fois », et pour l'année 1992 trente fois « majorée de
#: dix fois », chacune « appelée à concurrence de 100 p. 100 ».
CONSULTATIONS_DE_L_ASV_AU_TEXTE = {
    1982: 22.5, 1987: 22.5, 1988: 31.0, 1989: 22.5, 1990: 33.0, 1991: 22.5, 1992: 40.0}


@pytest.fixture(scope="module")
def versees_a_l_asv():
    """Ce que le compte reçoit de l'ASV, année par année, de la médecin née le
    1er janvier 1945 et installée à 27 ans, en 1972 : sa part seule
    (``salariale``), puis celle des caisses avec (``totale``)."""
    annees = sorted({*COTISATIONS_DE_L_ASV_AU_TEXTE, *CONSULTATIONS_DE_L_ASV_AU_TEXTE})
    return {
        part: {annee: _versees_au_compte(
            "1945-01-01", "27", annee,
            requete={**REQUETE_DE_MEDECIN, "liquidation": "68",
                     "part_cotisation": part})["asv_conventionnes"]
               for annee in annees}
        for part in ("salariale", "totale")}


@pytest.mark.parametrize("annee", COTISATIONS_DE_L_ASV_AU_TEXTE)
def test_le_medecin_verse_a_l_asv_les_consultations_du_texte_et_les_caisses_le_double(
        versees_a_l_asv, annee):
    """D. 645-2 fixe « la cotisation annuelle des bénéficiaires », D. 645-3
    celle des caisses, au double : le médecin paie N consultations, les caisses
    2 N. Jusqu'au 14 novembre 2026, la fiche prenait N consultations pour le
    total et n'en donnait que le tiers au médecin : 400 € en 2004 au lieu de
    1 200 €, et 1 200 € au compte au lieu de 3 600 €."""
    medecin, des_caisses = COTISATIONS_DE_L_ASV_AU_TEXTE[annee]
    assert versees_a_l_asv["salariale"][annee] == pytest.approx(medecin, abs=0.005)
    assert versees_a_l_asv["totale"][annee] == pytest.approx(
        medecin * (1 + des_caisses), abs=0.02)


@pytest.mark.parametrize("annee", CONSULTATIONS_DE_L_ASV_AU_TEXTE)
def test_l_appel_de_l_asv_suit_l_article_6_du_decret_de_1972(
        simulateur, versees_a_l_asv, annee):
    """L'article 6 du décret n° 72-968 appelle la cotisation à 75 % de 1981 à
    1992, sauf en 1988, en 1990 et en 1992, que le texte fixe une à une. Le
    tarif de la consultation n'est pas une série du dépôt : la fiche porte par
    les prix celui de 1985, 75 F, et le test ne tient que le nombre de
    consultations, que le modèle prenait à dix (le tiers de trente) chaque
    année."""
    consultation = 75 / 6.55957 * simulateur.macro.coefficient_prix(1985, annee)
    assert versees_a_l_asv["salariale"][annee] / consultation == pytest.approx(
        CONSULTATIONS_DE_L_ASV_AU_TEXTE[annee], abs=0.002)
    assert versees_a_l_asv["totale"][annee] == pytest.approx(
        3 * versees_a_l_asv["salariale"][annee], rel=1e-5)


#: (année de naissance) : la valeur de service du point de l'ASV des médecins à
#: la date d'effet de la pension, prise à 65 ans par un médecin né un 1er
#: janvier, telle que le texte la fixe, en euros courants.
VALEURS_DE_SERVICE_DE_L_ASV = {
    # Décret n° 72-968, article 2, du 28 mars 1999 au 1er janvier 2012
    # (LEGIARTI000006765945, 946 et 947) : « La valeur du point de retraite est
    # fixée à 102 F », que le décret n° 2011-1644 (article 4,
    # LEGIARTI000024853556) écrit « 15,55 euros pour le premier semestre de
    # l'exercice 2012 ».
    "1937": 15.55,   # pension de 2002
    "1940": 15.55,   # pension de 2005
    # Décret n° 2011-1644, article 4, II, 2° (LEGIARTI000052567955) : les
    # points liquidés à compter du 1er janvier 2011, « 13 euros à compter du
    # second semestre de l'exercice 2012 et jusqu'à l'exercice 2020 ».
    "1950": 13.0,    # pension de 2015
    # Même article, II, 3° : les points liquidés à compter du 1er janvier 2017,
    # « 11,31 euros jusqu'à l'exercice 2020, 11,36 euros pour l'exercice 2021,
    # 11,48 euros pour l'exercice 2022, 11,71 euros pour les exercices 2023 et
    # 2024 et 11,82 euros à compter de l'exercice 2025 ».
    "1953": 11.31,   # pension de 2018
    "1955": 11.31,   # pension de 2020
    "1956": 11.36,   # pension de 2021
    "1959": 11.71,   # pension de 2024
    "1960": 11.82,   # pension de 2025
    "1961": 11.82,   # pension de 2026
}


@pytest.fixture(scope="module")
def asv_a_65_ans():
    """La prestation de l'ASV de chaque cas, servie par le portage et refaite
    au bit près par le moteur Python (``servi_et_refait``) : médecin libéral
    au salaire moyen depuis ses 30 ans, parti à 65 ans, euros courants."""
    from outils_pont import servi_et_refait

    cas = [{"cle": naissance,
            "requete": {"statut": "medecin_liberal", "salaire": "1", "debut": "30",
                        "liquidation": "65", "naissance": f"{naissance}-01-01"}}
           for naissance in (*VALEURS_DE_SERVICE_DE_L_ASV, "1962")]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: next(p for p in servi["actuel"]["pensions_par_regime"]
                      if p["regime"] == "asv_conventionnes")
            for cle, servi in servis.items()}


def _points_valeur_et_majoration(detail: str) -> tuple[float, float, float]:
    """« 1,014.45 points × valeur de service 11.71 € × coefficient de
    majoration 1.1500 » : les points, la valeur, le coefficient (1 sans lui)."""
    import re

    lu = re.match(r"([\d,.]+) points × valeur de service ([\d.]+) €"
                  r"(?: × coefficient de majoration ([\d.]+))?", detail)
    assert lu, detail
    return (float(lu[1].replace(",", "")), float(lu[2]), float(lu[3] or 1.0))


@pytest.mark.parametrize("naissance", VALEURS_DE_SERVICE_DE_L_ASV)
def test_la_valeur_de_service_de_l_asv_des_medecins_est_celle_du_texte(
        asv_a_65_ans, naissance):
    """Les textes fixent la valeur de service du point en francs puis en euros
    courants, exercice par exercice, sans l'indexer : l'article 2 du décret
    n° 72-968 de 1999 à 2011, l'article 4 du décret n° 2011-1644 depuis.
    Jusqu'au 14 novembre 2026, le modèle portait aux prix de l'année d'effet
    une valeur ancrée à une autre année : 13,31 € en 2002 au lieu de 15,55 €,
    11,94 € en 2024 au lieu de 11,71 €, 12,03 € en 2026 au lieu de 11,82 €."""
    pension = asv_a_65_ans[naissance]
    points, valeur, majoration = _points_valeur_et_majoration(pension["detail"])
    assert valeur == VALEURS_DE_SERVICE_DE_L_ASV[naissance]
    # Les points du détail sont arrondis au centième : 0,005 point à 15,55 €.
    assert pension["montant"] == pytest.approx(
        points * VALEURS_DE_SERVICE_DE_L_ASV[naissance] * majoration, abs=0.1)


def test_l_asv_de_2002_et_de_2005_se_pose_a_la_main(asv_a_65_ans):
    """Né le 1er janvier 1937, médecin de 1967 à 2001 : le régime court depuis
    1972, vingt-deux années à 30,16 points (1972 à 1993) et huit à 27 points
    (1994 à 2001), 663,52 + 216 = 879,52 points ; × 15,55 € = 13 676,54 € par
    an, quand le modèle servait 11 709,34 € : 1 967,20 € de moins. Né en 1940,
    trois années à 27 points de plus, 960,52 points ; × 15,55 € = 14 936,09 €,
    au lieu de 13 575,33 €."""
    assert asv_a_65_ans["1937"]["montant"] == pytest.approx(13_676.54, abs=0.005)
    assert asv_a_65_ans["1940"]["montant"] == pytest.approx(14_936.09, abs=0.005)


def test_passe_le_dernier_exercice_fixe_la_valeur_de_l_asv_suit_les_prix(
        simulateur, asv_a_65_ans):
    """Le texte lu le 14 novembre 2026 fixe 11,82 € « à compter de l'exercice
    2025 » : 2026 est le dernier exercice échu sous cette valeur. Au-delà, le
    modèle projette, et la porte aux prix depuis 2026, non depuis 2025 : une
    seule année de hausse en 2027."""
    valeur = _points_valeur_et_majoration(asv_a_65_ans["1962"]["detail"])[1]
    assert valeur == pytest.approx(
        11.82 * simulateur.macro.coefficient_prix(2026, 2027), abs=5e-7)


# -- la CAVP : la carrière longue depuis le 10 janvier 2024 (action 130, la file) --

REQUETE_DE_PHARMACIEN = {**REQUETE_DE_MEDECIN, "sexe": "H", "statut": "pharmacien"}

#: (naissance, âge du début d'exercice, âge demandé) : le coefficient que le
#: texte oppose à la retraite complémentaire de la CAVP, posé à la main.
CARRIERES_LONGUES_A_LA_CAVP = {
    # Né le 10 mars 1965, entré à 19 ans, parti en carrière longue à 62 ans,
    # le 1er avril 2027, sous le règlement de 2026 : douze trimestres jusqu'à
    # 65 ans, 12 × 1,25 % = 15 %, et rien de 65 à 67 ans.
    ("1965-03-10", "19", "62"): 0.85,
    # Né le 10 mars 1966, entré à 20 ans, à 63 ans le 1er avril 2029 : huit
    # trimestres, 8 × 1,25 % = 10 %.
    ("1966-03-10", "20", "63"): 0.90,
    # Né le 10 mars 1966, entré à 15 ans, à 58 ans le 1er avril 2024, sous les
    # statuts de 2024 : vingt-huit trimestres « jusqu'à l'âge de 65 ans », sans
    # la limite de vingt que l'article 15 de 2009 posait : 28 × 1,25 % = 35 %.
    ("1966-03-10", "15", "58"): 0.65,
    # Né le 10 mars 1964, entré à 17 ans, à 60 ans le 1er avril 2024 : vingt
    # trimestres, 25 %.
    ("1964-03-10", "17", "60"): 0.75,
    # Né le 10 janvier 1962, entré à 18 ans, à 62 ans le 1er février 2024, la
    # première date d'effet qui suit le 10 janvier 2024 : 15 %.
    ("1962-01-10", "18", "62"): 0.85,
    # Né le 10 décembre 1961, entré à 18 ans, à 62 ans le 1er janvier 2024 :
    # les statuts de 2011, que l'arrêté publié le 9 janvier ne touche pas
    # encore, n'écrivent pas la dérogation. Le modèle y garde les deux pentes,
    # 12 × 1,25 % + 8 × 0,5 % = 19 % (la carrière longue d'avant 2024 est
    # renvoyée à la fiche `liquidation_regime_par_regime`).
    ("1961-12-10", "18", "62"): 0.81,
    # Né le 10 mars 1962, entré à 21 ans, parti à 63 ans le 1er avril 2025,
    # passé son âge légal, sans carrière longue : la règle générale, les deux
    # pentes, 8 × 1,25 % + 8 × 0,5 % = 14 %.
    ("1962-03-10", "21", "63"): 0.86,
    # Né le 10 mars 1965, entré à 19 ans, parti à 64 ans le 1er avril 2029,
    # passé son âge légal : la liquidation n'est plus anticipée, les deux
    # pentes, 4 × 1,25 % + 8 × 0,5 % = 9 %.
    ("1965-03-10", "19", "64"): 0.91,
}


@pytest.fixture(scope="module")
def carrieres_longues_a_la_cavp():
    """Chaque cas, servi par le portage et refait au bit près par le moteur
    Python (``servi_et_refait``)."""
    from outils_pont import servi_et_refait

    cas = [{"cle": "|".join(cle),
            "requete": {**REQUETE_DE_PHARMACIEN, "naissance": cle[0],
                        "debut": cle[1], "liquidation": cle[2]}}
           for cle in CARRIERES_LONGUES_A_LA_CAVP]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: {p["regime"]: p for p in servi["actuel"]["pensions_par_regime"]}
            for cle, servi in servis.items()}


@pytest.mark.parametrize("cle", CARRIERES_LONGUES_A_LA_CAVP,
                         ids=["|".join(cle) for cle in CARRIERES_LONGUES_A_LA_CAVP])
def test_la_cavp_minore_la_carriere_longue_jusqu_a_65_ans_seulement_depuis_2024(
        carrieres_longues_a_la_cavp, cle):
    """Statuts de la CAVP, article 15 (arrêté du 19 décembre 2023, annexe, II,
    6°, publié le 9 janvier 2024, en vigueur le 10) : « Par dérogation, en cas
    de liquidation anticipée dans les conditions prévues au II de l'article
    L. 643-3, sa pension de retraite complémentaire est affectée d'un
    coefficient de minoration égal à - 1,25 % par trimestre manquant jusqu'à
    l'âge de 65 ans. » ; le règlement de 2026 (arrêté du 10 juillet 2026,
    annexe I, article 12) le reprend, « par trimestre d'anticipation jusqu'à
    l'âge de 65 ans ». Jusqu'au 14 novembre 2026, le modèle opposait à la
    carrière longue les deux pentes de la règle générale, dans la limite de
    vingt trimestres."""
    cavp = carrieres_longues_a_la_cavp["|".join(cle)]["cavp_complementaire"]
    assert cavp["montant"] > 0
    assert _coefficient(cavp["detail"]) == pytest.approx(
        CARRIERES_LONGUES_A_LA_CAVP[cle])


def test_la_carriere_longue_de_la_cavp_se_pose_a_la_main(carrieres_longues_a_la_cavp):
    """Né le 10 mars 1965, parti à 62 ans le 1er avril 2027 : le modèle servait
    ses points × 0,81, 11 035,07 € par an ; le texte, × 0,85 : 11 035,07 / 0,81
    × 0,85 = 11 580,01 €, 544,94 € de plus. Né le 10 mars 1966, parti à 58 ans
    le 1er avril 2024 : 10 580,06 € sous 0,75 ; × 0,65 / 0,75 = 9 169,39 €,
    1 410,68 € de moins (euros de 2026)."""
    a_62_ans = carrieres_longues_a_la_cavp["1965-03-10|19|62"]["cavp_complementaire"]
    a_58_ans = carrieres_longues_a_la_cavp["1966-03-10|15|58"]["cavp_complementaire"]
    assert a_62_ans["montant"] == pytest.approx(11_035.07 / 0.81 * 0.85, abs=0.01)
    assert a_62_ans["montant"] == pytest.approx(11_580.01, abs=0.01)
    assert a_58_ans["montant"] == pytest.approx(10_580.06 / 0.75 * 0.65, abs=0.01)
    assert a_58_ans["montant"] == pytest.approx(9_169.39, abs=0.01)
