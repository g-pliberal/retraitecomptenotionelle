"""Ce que la CNAVPL, la CAVAMAC, la CAVEC et la Cipav servent, lu au texte.

La passe du 23 septembre 2026 sur les dernières sections libérales (action 89)
a lu les pages et le guide de la CNAVPL, les statuts de la CAVAMAC de 2011 et
de 2023 et ceux de la CAVEC depuis 2008 au Journal officiel, et le décret
n° 2026-418 dans ses articles des trois sections. Ce fichier tient ce qu'elle
a corrigé.

**Deux complémentaires minoraient comme le régime de base, et ne le font pas.**
La CAVAMAC compte les années qui séparent de son taux plein — 5 % par tranche
de douze mois jusqu'en 2023, 1,25 % par trimestre manquant jusqu'à 67 ans
depuis 2024 —, la CAVEC les trimestres qui séparent de 65 ans ; la durée
d'assurance n'y ouvre rien. Les fiches laissaient la durée annuler la
minoration : un agent général ou un expert-comptable parti à l'âge légal avec
sa durée ne perdait rien, quand ses statuts lui retirent 15 % ou davantage.

**Trois enfants majorent de 10 %** la complémentaire de la CAVAMAC depuis ses
statuts de 2011, celle de la Cipav depuis 2000 au moins, celle de la CAVEC
depuis l'arrêté du 4 juillet 2025. Aucune fiche ne la portait.

**La CNAVPL rend aux mères la majoration de durée d'assurance** depuis le
1er avril 2010 (L. 643-1-1). Le moteur ne la cherchait que dans les régimes en
annuités ; une libérale qui n'avait cotisé qu'à sa section n'en recevait rien.

**Sa valeur de service est celle qu'elle publie**, datée depuis 2004, et non
la valeur de 2021 déflatée vers le passé.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, LigneRelevee, Metier
from retraite_notionnelle.droit import compter
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int,
              liquidation: float, debut: float = 21.0, sexe: str = "H",
              enfants: int = 0, interruptions: dict[int, str] | None = None):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance,
        sexe=sexe,
        metiers=[Metier(affiliation=affiliation, age_debut=debut,
                        niveau_salaire=1.0)],
        age_liquidation=liquidation,
        macro=simulateur.macro,
        nombre_enfants=enfants,
        interruptions=interruptions,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return resultat, {p.regime: p for p in resultat.pensions_par_regime}


def _coefficient(detail: str) -> float:
    """Le coefficient écrit dans le détail d'une pension en points, 1 sans."""
    for marque in ("coefficient d'anticipation ", "coefficient de majoration "):
        if marque in detail:
            return float(detail.split(marque)[1].split()[0])
    return 1.0


def _majoration(resultat, regime: str) -> float:
    """La majoration pour enfants que le scénario 1 sert à ce régime."""
    for avantage in resultat.avantages_appliques:
        if avantage.code == "majoration_enfants":
            return dict(avantage.par_regime).get(regime, 0.0)
    return 0.0


# -- la CAVAMAC ----------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # Statuts de 2011, supposés les mêmes avant : taux plein à l'âge légal
    # augmenté de cinq ans — 65 ans pour ces générations —, 5 % par tranche de
    # douze mois d'anticipation, l'année entamée comptant entière.
    (1945, 64.0, 0.95),
    (1945, 63.25, 0.90),
    # La génération 1925 n'est pas dans la table du 1° de L. 351-8 : la fiche
    # lui donne 65 ans, et non les 67 ans d'aujourd'hui.
    (1925, 64.0, 0.95),
    # 2019 : taux plein à 67 ans pour la génération 1955, trois années.
    (1955, 64.0, 0.85),
    (1955, 64.25, 0.85),
    # Depuis 2024 : 1,25 % par trimestre manquant jusqu'à 67 ans.
    (1964, 63.0, 0.80),
    (1975, 64.0, 0.85),
    (1975, 67.0, 1.0),
])
def test_la_cavamac_minore_par_l_age_seul(simulateur, naissance, liquidation,
                                          coefficient):
    """Carrière commencée à 21 ans : la durée est réunie partout, et c'est le
    cas où la fiche ne minorait rien."""
    resultat, pensions = _calculer(simulateur, "agent_general_assurance",
                                   naissance, liquidation)
    assert resultat.liquidation_ouverte
    assert _coefficient(pensions["cavamac_complementaire"].detail) == pytest.approx(
        coefficient)


def test_la_cavamac_majore_par_annee_pleine_et_depuis_2024_par_annee_cotisee(
        simulateur):
    # Statuts de 2011 : « pour chaque année pleine différée » au-delà du taux
    # plein, 65 ans pour la génération 1950 — deux années à 67 ans.
    _, pensions = _calculer(simulateur, "agent_general_assurance", 1950, 67.0)
    assert _coefficient(pensions["cavamac_complementaire"].detail) == pytest.approx(1.10)
    # Depuis 2024, « pour chaque année pleine COTISÉE » : deux années de
    # travail au-delà de 67 ans valent 10 %…
    _, pensions = _calculer(simulateur, "agent_general_assurance", 1960, 69.0)
    assert _coefficient(pensions["cavamac_complementaire"].detail) == pytest.approx(1.10)
    # … et deux années d'attente, rien.
    _, pensions = _calculer(simulateur, "agent_general_assurance", 1960, 69.0,
                            interruptions={2027: "sans_activite",
                                           2028: "sans_activite"})
    assert _coefficient(pensions["cavamac_complementaire"].detail) == pytest.approx(1.0)


def test_la_cavamac_majore_l_annee_differee_des_le_1er_juillet_2011(simulateur):
    """Les statuts de 2011 entrent en vigueur le 1er juillet 2011 (arrêté du
    23 juin 2011, article 2), sans disposition transitoire : « une majoration
    de 5 % du nombre de points […] pour chaque année pleine différée au-delà
    de l'âge mentionné à l'article 15 » (article 16). L'agent né en février
    1945, au taux plein à 65 ans, qui liquide en novembre 2011 à 66 ans et
    9 mois, a différé une année pleine : 1,05. Le modèle ne servait les
    statuts de 2011 qu'aux pensions de 2012 (corrigé le 14 novembre 2026)."""
    def coefficient(age: float) -> tuple[tuple[int, int], float]:
        carriere = Carriere.depuis_parcours(
            annee_naissance=1945, mois_naissance=2, jour_naissance=1, sexe="H",
            metiers=[Metier(affiliation="agent_general_assurance", age_debut=21.0,
                            niveau_salaire=1.0)],
            age_liquidation=age, macro=simulateur.macro)
        resultat = simulateur.scenario_actuel.calculer(carriere)
        [pension] = [p for p in resultat.pensions_par_regime
                     if p.regime == "cavamac_complementaire"]
        effet = carriere.date_liquidation
        return (effet.annee, effet.mois), _coefficient(pension.detail)

    assert coefficient(66.75) == ((2011, 11), pytest.approx(1.05))
    # 66 ans et 5 mois, le 1er juillet 2011, premier jour des statuts.
    assert coefficient(66 + 5 / 12) == ((2011, 7), pytest.approx(1.05))
    # Le 1er juin 2011, les statuts de 1967, que nul texte lu ne dit : le
    # modèle n'y sert aucune majoration, ce que la fiche déclare.
    assert coefficient(66 + 4 / 12) == ((2011, 6), pytest.approx(1.0))


def test_la_cavamac_majore_de_dix_pour_cent_pour_trois_enfants(simulateur):
    resultat, pensions = _calculer(simulateur, "agent_general_assurance", 1960,
                                   67.0, sexe="F", enfants=3)
    assert _majoration(resultat, "cavamac_complementaire") == pytest.approx(
        0.10 * pensions["cavamac_complementaire"].montant)
    # Avant les statuts de 2011, rien n'est lu, rien n'est servi.
    resultat, _ = _calculer(simulateur, "agent_general_assurance", 1945, 65.0,
                            sexe="F", enfants=3)
    assert _majoration(resultat, "cavamac_complementaire") == 0.0


#: (naissance, âge au départ, titre déclaré) : la pension de la CAVAMAC par an
#: et son coefficient. Agent général au double du salaire moyen depuis ses
#: 22 ans, euros de 2026. Le titre ne change pas les points : chaque montant est
#: celui du taux plein (12 610,2304 €, 14 984,9734 €, 17 879,9355 €,
#: 21 070,3823 €, 21 752,7869 €, 25 169,5755 €) multiplié à la main par le
#: coefficient du texte en vigueur.
CAVAMAC_SANS_MINORATION = {
    # Statuts de 2011, article 15, en vigueur le 1er juillet 2011 : « à taux
    # plein sans application d'un coefficient de minoration au plus tôt à partir
    # de l'âge prévu à l'article L. 161-17-2 […] : a) Pour les adhérents reconnus
    # atteints d'inaptitude au travail […] ; b) Pour les anciens déportés et
    # internés ». Né le 1er janvier 1951, âge légal 60 ans, taux plein à 65 ans,
    # pension au 1er juillet 2011, à 60 ans et 6 mois, 54 mois avant : « 25 %
    # […] entre le 49e et le 60e mois » (article 16) au valide,
    # 12 610,2304 × 0,75 = 9 457,67 € ; rien à l'inapte, 12 610,23 €.
    ("1951-01-01", "60.5", ""): (9_457.67, 0.75),
    ("1951-01-01", "60.5", "inaptitude"): (12_610.23, 1.0),
    # Né le 1er janvier 1955, âge légal 62 ans, taux plein à 67 ans, pension au
    # 1er janvier 2017, à 62 ans, 60 mois avant : 25 % au valide,
    # 14 984,9734 × 0,75 = 11 238,73 € ; 14 984,97 € à l'inapte et au déporté.
    ("1955-01-01", "62", ""): (11_238.73, 0.75),
    ("1955-01-01", "62", "inaptitude"): (14_984.97, 1.0),
    ("1955-01-01", "62", "deporte"): (14_984.97, 1.0),
    # Né le 1er janvier 1958, inapte, pension au 1er janvier 2020, à 62 ans :
    # 17 879,94 €, au lieu de 17 879,9355 × 0,75 = 13 409,95 €.
    ("1958-01-01", "62", "inaptitude"): (17_879.94, 1.0),
    # Arrêté du 4 août 2023, annexe, 6°, b, en vigueur le 1er septembre 2023 :
    # « à partir de l'âge prévu au IV de l'article L. 643-3 et sans application
    # d'un coefficient de minoration les pensions […] des assurés mentionnés aux
    # 2° et 3° de l'article L. 643-4 », dont l'inapte, à 62 ans (D. 643-14,
    # D. 351-1-14). Né le 1er août 1961, âge légal 62 ans, pension au
    # 1er novembre 2023, à 62 ans et 3 mois, 57 mois avant 67 ans : 25 % au
    # valide, 21 070,3823 × 0,75 = 15 802,79 € ; 21 070,38 € à l'inapte.
    ("1961-08-01", "62.25", ""): (15_802.79, 0.75),
    ("1961-08-01", "62.25", "inaptitude"): (21_070.38, 1.0),
    # Statuts de 2024 : « 1,25 % par trimestre manquant pour atteindre » 67 ans.
    # Né le 1er janvier 1962, pension au 1er juillet 2024, à 62 ans et 6 mois,
    # dix-huit trimestres : 21 752,7869 × 0,775 = 16 858,41 € au valide ;
    # 21 752,79 € à l'inapte et au déporté (L. 643-4, 2°, a et c).
    ("1962-01-01", "62.5", ""): (16_858.41, 0.775),
    ("1962-01-01", "62.5", "inaptitude"): (21_752.79, 1.0),
    ("1962-01-01", "62.5", "deporte"): (21_752.79, 1.0),
    # Règlement de 2026, article 4, mot pour mot. Né le 1er janvier 1965,
    # pension au 1er octobre 2027, à 62 ans et 9 mois, l'âge de L. 161-17-2,
    # dix-sept trimestres : 25 169,5755 × 0,7875 = 19 821,04 € au valide ;
    # 25 169,58 € à l'inapte, au déporté, et à l'ancien combattant de soixante
    # mois (L. 643-4, 2°, d, « personnes mentionnées au 5° de l'article
    # L. 351-8 »), que D. 351-2 sert dès « l'âge prévu à l'article L. 161-17-2 » ;
    # celui de douze mois attend « l'âge prévu au 1° de l'article L. 351-8
    # minoré d'un an », 66 ans.
    ("1965-01-01", "62.75", ""): (19_821.04, 0.7875),
    ("1965-01-01", "62.75", "inaptitude"): (25_169.58, 1.0),
    ("1965-01-01", "62.75", "deporte"): (25_169.58, 1.0),
    ("1965-01-01", "62.75", "guerre=60"): (25_169.58, 1.0),
    ("1965-01-01", "62.75", "guerre=12"): (19_821.04, 0.7875),
}


def test_la_cavamac_sert_sans_minoration_l_inapte_et_les_categories_de_ses_statuts():
    """Statuts de 2011, article 15, a et b (JORFARTI000024270173) ; arrêté du
    4 août 2023, annexe, 6°, b (JORFARTI000047977908), et L. 643-4, 2°
    (LEGIARTI000047453026) ; règlement de 2026, article 4
    (JORFARTI000054436046). L'inapte et l'ancien déporté ou interné sont servis
    « sans application d'un coefficient de minoration » dès l'âge de
    L. 161-17-2, l'inapte dès 62 ans depuis le 1er septembre 2023 ; l'ancien
    combattant ou prisonnier de guerre du 5° de L. 351-8, aux âges de D. 351-2,
    depuis les statuts de 2024. Le modèle leur opposait la minoration de
    l'assuré valide, 25 % à 62 ans (corrigé le 14 novembre 2026). Servi par le
    portage, refait au bit près par le moteur Python."""
    from outils_pont import servi_et_refait

    requete = {
        "age_reference": "fixe_apres_bascule", "bascule": "2026",
        "conversion_acquis": "reference", "debut": "22", "emploi": "cor_2026",
        "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
        "primes": "0", "profil": "plat", "projection": "cor_reference",
        "salaire": "2", "sexe": "H", "stock": "prix", "table": "unisexe",
        "statut": "agent_general_assurance",
    }

    def titre(declare):
        if not declare:
            return {}
        nom, _, valeur = declare.partition("=")
        return {nom: valeur or "oui"}

    cas = [{"cle": "|".join(cle),
            "requete": {**requete, "naissance": cle[0], "liquidation": cle[1],
                        **titre(cle[2])}}
           for cle in CAVAMAC_SANS_MINORATION]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    ecarts = {}
    for cle, (montant, coefficient) in CAVAMAC_SANS_MINORATION.items():
        actuel = servis["|".join(cle)]["actuel"]
        [pension] = [p for p in actuel["pensions_par_regime"]
                     if p["regime"] == "cavamac_complementaire"]
        if (_coefficient(pension["detail"]) != pytest.approx(coefficient)
                or pension["montant"] != pytest.approx(montant, abs=0.005)):
            ecarts[cle] = (_coefficient(pension["detail"]), round(pension["montant"], 2))
    assert ecarts == {}, ecarts


# -- la CAVEC -------------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # « Entre 60 et 65 ans, avec application d'un abattement définitif de
    # 1,25 % par trimestre manquant » : neuf trimestres à 62 ans et 9 mois,
    # la durée fût-elle réunie.
    (1964, 62.75, 0.8875),
    (1950, 60.0, 0.75),
    # Avant 2008 aussi : la caisse garde 65 ans depuis 1983.
    (1940, 62.0, 0.85),
    (1961, 65.0, 1.0),
])
def test_la_cavec_minore_par_l_age_seul(simulateur, naissance, liquidation,
                                        coefficient):
    resultat, pensions = _calculer(simulateur, "expert_comptable", naissance,
                                   liquidation)
    assert resultat.liquidation_ouverte
    assert _coefficient(pensions["cavec_complementaire"].detail) == pytest.approx(
        coefficient)


def test_la_cavec_majore_pour_trois_enfants_depuis_juillet_2025(simulateur):
    resultat, pensions = _calculer(simulateur, "expert_comptable", 1961, 65.0,
                                   sexe="F", enfants=3)
    assert _majoration(resultat, "cavec_complementaire") == pytest.approx(
        0.10 * pensions["cavec_complementaire"].montant)
    resultat, _ = _calculer(simulateur, "expert_comptable", 1959, 65.0,
                            sexe="F", enfants=3)
    assert _majoration(resultat, "cavec_complementaire") == 0.0


#: Les minorations à l'âge seul lues au droit le 3 novembre 2026 (action 130),
#: la CAVAMAC et la CAVOM le 5, et le régime que chacune minore.
MINORATIONS_LUES_AU_DROIT = {
    "cavec_minoration_age_seul": "cavec_complementaire",
    "carpv_minoration_age_seul": "carpv_complementaire",
    "cavamac_minoration_age_seul": "cavamac_complementaire",
    "cavom_ages_minoration": "cavom_complementaire",
}


@pytest.mark.parametrize("fiche,regime", sorted(MINORATIONS_LUES_AU_DROIT.items()))
def test_chaque_pension_minoree_porte_les_ages_et_le_taux_de_sa_version(
        simulateur, fiche, regime):
    """Statuts de la CAVEC (article 3.13 en 2008, article 12 en 2018, article
    1.1.3 du règlement de 2026) et de la CARPV (article 34 en 2021, article 2
    du règlement de 2026) : taux plein à 65 ans, liquidation dès 60 ans,
    1,25 % par trimestre manquant, aucune durée n'y entrant. Statuts de la
    CAVAMAC (articles 15 et 16 en 2011) : taux plein à l'âge de L. 161-17-2
    « augmenté de cinq années », celui du 1° de L. 351-8 qui dit les mêmes
    mots, liquidation dès l'âge de L. 161-17-2, 5 % par tranche de douze mois ;
    puis « 67 ans » (arrêté du 4 août 2023, 6°) et, au 1er janvier 2024,
    « 1,25 % par trimestre manquant » (7°, c ; article 5 du règlement de
    2026). Statuts de la CAVOM (articles 14 et 23 en 2016, arrêté du
    30 décembre 2015 ; article 14 récrit au 1er janvier 2025, arrêté du
    12 décembre 2024, 4° ; article 1er, I, du règlement de 2026) : liquidation
    dès 60 ans et taux plein à 65 ans jusqu'à la génération 1955, six mois de
    plus par génération jusqu'à 62 et 67 ans, puis l'ouverture portée à 64 ans
    pour la génération 1968 ; de 0,75 à 0,95 selon l'âge, puis « 5 % par année
    manquante », « non susceptible de fractionnement ». Chaque premier du
    mois que couvre une version, de la création du régime à 2040, la période qui liquide une pension prenant effet ce jour
    porte chacun des paramètres que la version lit — l'âge d'ouverture, l'âge
    du taux plein, ou leur table par génération, le barème, le taux —, et la
    durée n'y annule pas la minoration."""
    from datetime import date

    from retraite_notionnelle.noyau import carte

    caisse = simulateur.catalogue[regime]
    versions = carte.fiches()[fiche].get("versions") or []
    assert versions
    for version in versions:
        lus = version["contenu"]["parametres"]
        debut, fin = version["bornes"]["liquidation.date_effet"]
        jour = debut or date(caisse.creation, 1, 1)
        while jour < (fin or date(2041, 1, 1)):
            periode = caisse.periode_a_l_effet(jour.isoformat())
            portes = {cle: getattr(periode, cle) for cle in lus}
            portes = {cle: list(v) if isinstance(v, tuple) else v for cle, v in portes.items()}
            assert portes == lus, (version["id"], jour)
            assert periode.decote_annulee_par_la_duree is False, (version["id"], jour)
            jour = date(jour.year + jour.month // 12, jour.month % 12 + 1, 1)


@pytest.mark.parametrize("fiche", sorted(MINORATIONS_LUES_AU_DROIT))
def test_chaque_version_lue_commence_quand_son_texte_entre_en_vigueur(fiche):
    """Une version lue naît d'un texte (`nee_de`) qu'elle cite parmi les siens,
    et commence le jour où il entre en vigueur : le 1er janvier 2022 que
    l'arrêté du 18 octobre 2021 fixe aux statuts de la CARPV (article 2), le
    lendemain de leur publication pour les arrêtés qui n'en fixent pas."""
    from retraite_notionnelle.noyau import carte

    lues = [v for v in carte.fiches()[fiche].get("versions") or []
            if v.get("statut", "lue") == "lue"]
    assert lues
    for version in lues:
        texte = next(t for t in version["textes"] if t.get("id") == version["nee_de"])
        assert version["bornes"]["liquidation.date_effet"][0] == texte["en_vigueur"], (
            version["id"])


#: Les textes dont naît chaque version des deux fiches, leur publication au
#: Journal officiel et le jour où ils entrent en vigueur, relevés le 3 novembre
#: 2026 à l'index JORF du dépôt (relecture R-E, file E-bis) : aucun de ces
#: arrêtés ne fixe sa date, sauf celui du 18 octobre 2021 (article 2, « entrent
#: en vigueur le 1er janvier 2022 ») ; les autres entrent en vigueur le
#: lendemain de leur publication. La CARPV : l'alinéa de l'inapte de 2011, la
#: renumérotation de 2014, l'alinéa récrit le 2 novembre 2015.
#: La CAVAMAC, relevée le 5 novembre 2026 : l'arrêté du 23 juin 2011 met ses
#: statuts en vigueur « le 1er juillet 2011 » (article 2) ; celui du 4 août
#: 2023, le 6° de son annexe (l'article 15) « le 1er septembre 2023 », les a, c
#: et d du 7° (l'article 16) « le 1er janvier 2024 » (article 2, 1° et 2°) ;
#: celui du 10 juillet 2026 ne fixe pas de date.
#: La CARPIMKO, relevée le 5 novembre 2026 : l'arrêté du 22 février 1984, publié
#: le 29, approuve des statuts que LEGI date du 1er janvier 1984, le jour où
#: l'article 1er du décret n° 84-143 institue le régime ; ceux du 20 mai 1987
#: (relevé le 5 novembre par la relecture R-E4) et du 20 novembre 1996 ne sont
#: au Journal officiel que par leur titre ou une mention, d'où une entrée en
#: vigueur supposée au lendemain ; ceux du
#: 31 juillet 2015, du 23 mai 2019 (pour ses âges), du 27 décembre 2023 et du
#: 10 juillet 2026 ne fixent pas de date.
#: La CARCDSF, relevée le 5 novembre 2026 : l'arrêté du 13 avril 2011 met ses
#: statuts en vigueur « à compter du 1er juillet 2011 » (article 3) ; ceux du
#: 1er octobre 2007, du 9 juillet 2012, du 22 décembre 2017, du 27 décembre
#: 2023 et du 10 juillet 2026 ne fixent pas de date.
#: La CAVOM, relevée le 5 novembre 2026 : l'arrêté du 12 décembre 2024 met
#: l'annexe en vigueur « au 1er janvier 2025 » (article 2) ; ceux du
#: 30 décembre 2015 et du 10 juillet 2026 ne fixent pas de date.
#: La CPRN, relevée le 5 novembre 2026 : l'arrêté du 28 décembre 2004, publié
#: le 4 février 2005, « prend effet le 1er janvier 2005 » et n'est au Journal
#: officiel que par sa mention ; celui du 16 décembre 2013 « prend effet au
#: 1er janvier 2014 » (article 2) ; celui du 29 novembre 2023 entre en vigueur
#: « le 1er janvier 2024 » (article 2) ; ceux du 31 mai 2017 et du 10 juillet
#: 2026 ne fixent pas de date.
NAISSANCES_AU_JOURNAL_OFFICIEL = {
    "cavec_minoration_age_seul": {
        "JORFARTI000018197778": ("2008-03-01", "2008-03-02"),
        "JORFARTI000037363871": ("2018-09-04", "2018-09-05"),
        "JORFARTI000038689131": ("2019-06-27", "2019-06-28"),
        "LEGIARTI000054437585": ("2026-07-17", "2026-07-18"),
    },
    "carpimko_ages_2015": {
        "JORFTEXT000000315359": ("1984-02-29", "1984-01-01"),
        "JORFTEXT000000844323": ("1987-06-04", "1987-06-05"),
        "JORFARTI000002184842": ("1996-11-30", "1996-12-01"),
        "JORFARTI000031255547": ("2015-10-02", "2015-10-03"),
        "JORFARTI000038529117": ("2019-05-30", "2019-05-31"),
        "JORFARTI000048880643": ("2024-01-09", "2024-01-10"),
        "JORFARTI000054435915": ("2026-07-17", "2026-07-18"),
    },
    "carcdsf_minoration_age_seul": {
        "JORFARTI000001859980": ("2007-10-10", "2007-10-11"),
        "JORFARTI000023909792": ("2011-04-27", "2011-07-01"),
        "JORFARTI000026208364": ("2012-07-21", "2012-07-22"),
        "JORFARTI000036251928": ("2017-12-24", "2017-12-25"),
        "JORFARTI000048880707": ("2024-01-09", "2024-01-10"),
        "JORFARTI000054435749": ("2026-07-17", "2026-07-18"),
    },
    "cavamac_minoration_age_seul": {
        "JORFARTI000024270173": ("2011-06-29", "2011-07-01"),
        "JORFARTI000047977908": ("2023-08-18", "2023-09-01"),
        "JORFARTI000047977903": ("2023-08-18", "2024-01-01"),
        "JORFARTI000054436046": ("2026-07-17", "2026-07-18"),
    },
    "cavom_ages_minoration": {
        "JORFARTI000031740853": ("2015-12-31", "2016-01-01"),
        "JORFARTI000050823056": ("2024-12-24", "2025-01-01"),
        "JORFARTI000054435969": ("2026-07-17", "2026-07-18"),
    },
    "carpv_minoration_age_seul": {
        "JORFARTI000023448554": ("2011-01-19", "2011-01-20"),
        "JORFARTI000028939421": ("2014-05-17", "2014-05-18"),
        "JORFARTI000031549970": ("2015-12-01", "2015-12-02"),
        "JORFARTI000044220745": ("2021-10-19", "2022-01-01"),
        "JORFARTI000054436031": ("2026-07-17", "2026-07-18"),
    },
    "cavp_minoration_deux_pentes": {
        "JORFARTI000020694605": ("2009-06-06", "2009-06-07"),
        "JORFARTI000024270214": ("2011-06-29", "2011-06-30"),
        "JORFARTI000048880592": ("2024-01-09", "2024-01-10"),
        "JORFARTI000054436087": ("2026-07-17", "2026-07-18"),
    },
    "cprn_ages_decote_enfants": {
        "JORFARTI000001075201": ("2005-02-04", "2005-01-01"),
        "JORFARTI000028387445": ("2013-12-27", "2014-01-01"),
        "JORFARTI000034975971": ("2017-06-21", "2017-06-22"),
        "JORFARTI000048679350": ("2023-12-28", "2024-01-01"),
        "JORFARTI000054435995": ("2026-07-17", "2026-07-18"),
    },
    "carmf_asv_minoration_enfants": {
        "JORFARTI000033521562": ("2016-12-04", "2017-01-01"),
        "JORFARTI000034298521": ("2017-03-29", "2017-03-30"),
        "JORFARTI000054435859": ("2026-07-17", "2026-07-18"),
    },
}


@pytest.mark.parametrize("fiche", sorted(NAISSANCES_AU_JOURNAL_OFFICIEL))
def test_chaque_version_nait_d_un_texte_a_sa_date_du_journal_officiel(fiche):
    """Chaque version née d'un texte, lue ou supposée, commence le jour où il
    entre en vigueur, à la date que donne le Journal officiel et non la fiche
    seule : les naissances de la fiche sont celles de la table, ni plus ni
    moins, et chacune y porte la publication et l'entrée en vigueur relevées."""
    from datetime import date

    from retraite_notionnelle.noyau import carte

    attendues = {texte: (date.fromisoformat(publie), date.fromisoformat(en_vigueur))
                 for texte, (publie, en_vigueur) in NAISSANCES_AU_JOURNAL_OFFICIEL[fiche].items()}
    nees = [v for v in carte.fiches()[fiche]["versions"] if v.get("nee_de")]
    assert sorted(v["nee_de"] for v in nees) == sorted(attendues)
    for version in nees:
        texte = next(t for t in version["textes"] if t.get("id") == version["nee_de"])
        publie, en_vigueur = attendues[version["nee_de"]]
        assert (texte["publie_le"], texte["en_vigueur"]) == (publie, en_vigueur), version["id"]
        assert version["bornes"]["liquidation.date_effet"][0] == en_vigueur, version["id"]


# -- la Cipav -------------------------------------------------------------------


def test_la_cipav_majore_pour_trois_enfants_depuis_2000(simulateur):
    resultat, pensions = _calculer(simulateur, "profession_liberale", 1945, 65.0,
                                   sexe="F", enfants=3)
    assert _majoration(resultat, "cipav_complementaire") == pytest.approx(
        0.10 * pensions["cipav_complementaire"].montant)
    resultat, _ = _calculer(simulateur, "profession_liberale", 1930, 65.0,
                            sexe="F", enfants=3)
    assert _majoration(resultat, "cipav_complementaire") == 0.0


#: Les trois complémentaires de ``sections_liberales_majoration_enfants`` et
#: le statut de chacune dans les versions de la fiche.
SECTIONS_QUI_MAJORENT = ("cavamac_complementaire", "cavec_complementaire",
                         "cipav_complementaire")

#: L'écart que la fiche déclarait, lue au droit le 6 novembre 2026 (action
#: 130) : les statuts de la CAVAMAC de 2011 entrent en vigueur le 1er juillet
#: 2011 (arrêté du 23 juin 2011, article 2) et majorent de 10 % les points de
#: l'adhérent qui a eu trois enfants (article 18) ; le modèle ne servait la
#: majoration qu'aux pensions qui prennent effet depuis le 1er janvier 2012.
#: Corrigé le 14 novembre 2026 : plus aucune date d'effet n'est omise.
MAJORATION_OMISE_PAR_LE_MODELE: set[tuple[str, int, int]] = set()


def test_chaque_version_de_la_majoration_pour_enfants_des_sections_est_portee():
    """Lue au droit le 6 novembre 2026 (action 130) : à chaque date d'effet,
    mois par mois, de 1990 à 2040, la majoration que chaque version de
    ``sections_liberales_majoration_enfants`` donne à trois enfants est celle
    que la période de liquidation de chaque section déclare
    (``majoration_enfants`` dans ``avantages_non_contributifs``, que
    ``_taux_majoration_enfants`` sert à 10 %), sans écart."""
    from retraite_notionnelle.carriere import DateMois
    from retraite_notionnelle.droit.commun import periode_de_liquidation
    from retraite_notionnelle.droit.completer import _taux_majoration_enfants
    from retraite_notionnelle.noyau import carte

    catalogue = Simulateur().catalogue
    fiche = carte.fiches()["sections_liberales_majoration_enfants"]
    versions = fiche.get("versions") or []
    assert [v["id"] for v in versions] == [
        "aucune_avant_2000", "cipav_depuis_2000", "cavamac_depuis_juillet_2011",
        "cavec_depuis_juillet_2025", "au_decret_et_aux_reglements_de_2026"]
    vus = omis = 0
    for annee in range(1990, 2041):
        for mois in range(1, 13):
            jour = f"{annee:04d}-{mois:02d}-01"
            [version] = [v for v in versions
                         if (v["bornes"]["liquidation.date_effet"][0] is None
                             or v["bornes"]["liquidation.date_effet"][0].isoformat() <= jour)
                         and (v["bornes"]["liquidation.date_effet"][1] is None
                              or jour < v["bornes"]["liquidation.date_effet"][1].isoformat())]
            taux = version["contenu"]["parametres"]["taux_a_trois_enfants"]
            assert set(taux) == set(SECTIONS_QUI_MAJORENT), version["id"]
            for code in SECTIONS_QUI_MAJORENT:
                regime = catalogue[code]
                periode = periode_de_liquidation(regime, DateMois(annee, mois))
                servi = (_taux_majoration_enfants(regime, 3, periode)
                         if "majoration_enfants" in periode.avantages_non_contributifs
                         else 0.0)
                if (code, annee, mois) in MAJORATION_OMISE_PAR_LE_MODELE:
                    assert (servi, taux[code]) == (0.0, 0.10), (code, jour)
                    omis += 1
                    continue
                assert servi == pytest.approx(taux[code]), (version["id"], code, jour)
                vus += 1
    assert omis == 0
    assert vus == 51 * 12 * 3


#: Né un 10 mars, l'âge se compte du 1er avril (``Carriere.origine_des_ages``) :
#: 65 ans et 3 mois, une pension au 1er juillet, de l'année des 65 ans.
#: Chaque cas porte trois choses, relues aux sources le 6 novembre 2026
#: (action 130, E9) : les lectures du texte en vigueur à la date d'effet, un
#: taux, deux quand le texte ne tranche pas, ``None`` quand il atteste la
#: majoration sans en donner le taux ; le taux que le modèle sert,
#: que le test vérifie dans les deux moteurs ; et, quand le modèle n'est pas
#: la lecture unique du texte, ou qu'il suppose, l'approximation de la fiche
#: qui le déclare,
#: ``(version, régime)``. Le test ne pose pas le montant de la pension : il
#: vérifie que la majoration servie est ce taux de la pension que le modèle
#: sert.
MAJORATIONS_AUX_DATES_QUI_COMPTENT = {
    # CAVAMAC : statuts approuvés par l'arrêté du 23 juin 2011, « en vigueur le
    # 1er juillet 2011 » (article 2), article 18 : « majoré de 10 % au profit de
    # l'adhérent ayant eu au moins trois enfants ». Le modèle ne servait rien
    # avant le 1er janvier 2012 : corrigé le 14 novembre 2026.
    ("agent_general_assurance", "1946-03-10", "65.25"):  # 1er juillet 2011
        ((0.10,), 0.10, None),
    ("agent_general_assurance", "1946-03-10", "65.75"):  # 1er janvier 2012
        ((0.10,), 0.10, None),
    # CAVEC : les statuts de 2018 sans « bonification » ; l'arrêté du 4 juillet
    # 2025, publié le 6, en vigueur le 7 (article 2, la publication seule),
    # article 20 : « majoré de 10 % ».
    ("expert_comptable", "1960-03-10", "65.25"): ((0.0,), 0.0, None),  # 1er juillet 2025
    ("expert_comptable", "1960-03-10", "65.3333"): ((0.10,), 0.10, None),  # 1er août 2025
    # Cipav : avant 2000, point non tranché, rien ou 10 % (le décret n° 99-913
    # renvoie à une bonification « prévue par les statuts », que nul ne date) ;
    # de 2000 au 30 juin 2026, la bonification attestée par le décret n° 99-913,
    # article 6, sans sa forme : 10 %, la forme supposée, déclarée ; depuis le
    # 1er juillet 2026, l'article 5-2 du décret n° 79-262 : « majoré de 10 % ».
    ("profession_liberale", "1934-03-10", "65.6667"):  # 1er décembre 1999
        ((0.0, 0.10), 0.0, ("aucune_avant_2000", "cipav_complementaire")),
    ("profession_liberale", "1934-03-10", "65.75"):  # 1er janvier 2000
        (None, 0.10, ("cipav_depuis_2000", "cipav_complementaire")),
    ("profession_liberale", "1961-03-10", "65.25"): ((0.10,), 0.10, None),  # 1er juillet 2026
}


def test_les_lectures_de_la_majoration_pour_enfants_des_sections_que_le_modele_ne_suit_pas_sont_declarees():
    """Où le modèle n'est pas la lecture unique du texte, à chaque cas de
    ``MAJORATIONS_AUX_DATES_QUI_COMPTENT``, la fiche
    ``sections_liberales_majoration_enfants`` le déclare, par une
    approximation de la version et du régime ; ailleurs, le modèle sert le
    taux du texte."""
    from retraite_notionnelle.noyau import carte

    fiche = carte.fiches()["sections_liberales_majoration_enfants"]
    declarees = {(version, a.get("regime")) for a in fiche.get("approximations") or []
                 for version in a["version"]}
    ecarts = 0
    for cle, (lectures, servi, ecart) in MAJORATIONS_AUX_DATES_QUI_COMPTENT.items():
        assert (lectures == (servi,)) == (ecart is None), cle
        if ecart is not None:
            assert ecart in declarees, cle
            ecarts += 1
    assert ecarts == 2


def test_la_majoration_pour_enfants_des_sections_aux_dates_qui_comptent_dans_les_deux_moteurs():
    """Le portage sert, et le moteur Python refait (``servi_et_refait``), à
    une mère de trois enfants de chaque section, la majoration que le modèle
    sert à la date d'effet (``MAJORATIONS_AUX_DATES_QUI_COMPTENT``, le taux
    servi) : 10 % de la pension de la complémentaire, ou rien. Au 1er juillet
    2011, la CAVAMAC reçoit les 10 % de ses statuts de 2011, en vigueur ce
    jour-là : 0,10 × 13 323,31 = 1 332,331, soit 1 332,33 € par an au cas posé
    (corrigé le 14 novembre 2026) ; au 1er décembre 1999, la Cipav rien, l'une
    des deux lectures."""
    from outils_pont import servi_et_refait

    requete = {
        "age_reference": "fixe_apres_bascule", "bascule": "2026",
        "conversion_acquis": "reference", "debut": "22", "emploi": "cor_2026",
        "enfants": "3", "euros": "2026", "indexation": "triple_lock_inverse",
        "primes": "0", "profil": "plat", "projection": "cor_reference",
        "salaire": "2", "sexe": "F", "stock": "prix", "table": "unisexe",
    }
    regimes = {"agent_general_assurance": "cavamac_complementaire",
               "expert_comptable": "cavec_complementaire",
               "profession_liberale": "cipav_complementaire"}
    cas = [{"cle": "|".join(cle), "requete": {**requete, "statut": cle[0],
                                               "naissance": cle[1], "liquidation": cle[2]}}
           for cle in MAJORATIONS_AUX_DATES_QUI_COMPTENT]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    for cle, (_, taux, _) in MAJORATIONS_AUX_DATES_QUI_COMPTENT.items():
        actuel = servis["|".join(cle)]["actuel"]
        regime = regimes[cle[0]]
        montant = {p["regime"]: p["montant"] for p in actuel["pensions_par_regime"]}[regime]
        parts = [dict(a["par_regime"]).get(regime, 0.0) for a in actuel["avantages_appliques"]
                 if a["code"] == "majoration_enfants"]
        assert montant > 0, cle
        assert sum(parts) == pytest.approx(taux * montant), cle
        if cle == ("agent_general_assurance", "1946-03-10", "65.25"):
            # Posé à la main : 65 ans et 3 mois, le taux plein à 65 ans, aucune
            # année pleine différée (article 16), donc les mêmes points ;
            # article 18, 10 % de 13 323,31 €.
            assert montant == pytest.approx(13_323.31, abs=0.005), cle
            assert sum(parts) == pytest.approx(1_332.33, abs=0.005), cle


#: Ce que le décret n° 79-262 (article 2, rédaction du décret n° 2022-1746) et
#: les décrets de chaque année font payer à la Cipav, posé à la main (action
#: 130, 6 novembre 2026) : la première tranche jusqu'au plafond de l'année, la
#: seconde « entre une et trois fois le plafond » en 2023, « trois fois et
#: demie » en 2024, « quatre fois » depuis 2025 ; 9 % et 22 % en 2023
#: (décret n° 2023-1351, article 6, 8°) et en 2024 (décret n° 2024-1214,
#: article 6, 8°), 11 % et 21 % en 2025 (décret n° 2025-1076, article 12,
#: 8°) ; le plafond, douze fois sa valeur mensuelle (3 666 € en 2023, 3 864 €
#: en 2024, 3 925 € en 2025, arrêtés des 9 décembre 2022, 19 décembre 2023
#: et 19 décembre 2024) : 43 992, 46 368 et 47 100 €.
COTISATIONS_DE_LA_CIPAV = [
    # 0,09 × 43 992 + 0,22 × (100 000 − 43 992) = 3 959,28 + 12 321,76
    (2023, 100_000.0, 16_281.04),
    # 3 959,28 + 0,22 × (3 − 1) × 43 992 = 3 959,28 + 19 356,48
    (2023, 200_000.0, 23_315.76),
    # 0,09 × 46 368 + 0,22 × (3,5 − 1) × 46 368 = 4 173,12 + 25 502,40
    (2024, 200_000.0, 29_675.52),
    # 0,11 × 47 100 + 0,21 × (150 000 − 47 100) = 5 181,00 + 21 609,00
    (2025, 150_000.0, 26_790.00),
    # 5 181,00 + 0,21 × (4 − 1) × 47 100 = 5 181,00 + 29 673,00
    (2025, 200_000.0, 34_854.00),
]


@pytest.mark.parametrize("annee,revenu,attendue", COTISATIONS_DE_LA_CIPAV)
def test_la_cipav_cotise_aux_deux_tranches_du_decret_dans_les_deux_moteurs(
        simulateur, annee, revenu, attendue):
    """La fiche de paie du libéral de la Cipav (``profession_liberale``), que
    le portage sert et que le moteur Python refait (``droit_et_refait``), et
    la cotisation que le scénario 1 inscrit l'année du revenu (``acquerir``),
    ramenée en euros de cette année : celle du texte, au centime."""
    from outils_pont import droit_et_refait

    from retraite_notionnelle import pont
    from retraite_notionnelle.carriere import AnneeCarriere
    from retraite_notionnelle.droit import acquerir, coordonner

    lus, refus = droit_et_refait({"fiche": (
        "remuneration.fiche_depuis_brut.lignes_de_retraite", pont.SIMULATEUR,
        "profession_liberale", annee, revenu)})
    assert refus == {}, refus
    assert dict(lus["fiche"])["cipav_complementaire"] == pytest.approx(attendue, abs=0.005)
    carriere = Carriere.depuis_lignes(
        1962, "H", [AnneeCarriere(annee=annee, affiliation="profession_liberale",
                                  revenu=revenu, trimestres_valides=4)],
        age_liquidation=65)
    actuel = simulateur.scenario_actuel
    coordination = coordonner.coordonner(actuel, carriere)
    droits = acquerir.acquerir(actuel, coordination, compter.compter(actuel, coordination))
    prix = simulateur.macro.coefficient_prix(annee, carriere.annee_liquidation)
    inscrite = sum(montant for code, an, montant in droits.cotisations
                   if code == "cipav_complementaire" and an == annee) / prix
    assert inscrite == pytest.approx(attendue, abs=0.005)


def test_chaque_version_de_la_seconde_tranche_de_la_cipav_est_portee_par_le_modele(
        simulateur):
    """Lue au droit le 6 novembre 2026 (action 130) : chaque année du revenu
    de 2023 à 2040 que couvre une version de ``cipav_seconde_tranche``, les
    périodes de ``cipav_complementaire`` de cette année sont, ni plus ni
    moins, ses deux tranches, chacune son assiette et son taux. La version de
    2026, que nul décret ne chiffre encore, porte la reconduction que la fiche
    déclare."""
    from retraite_notionnelle.noyau import carte

    caisse = simulateur.catalogue["cipav_complementaire"]
    versions = carte.fiches()["cipav_seconde_tranche"].get("versions") or []
    assert versions
    lues = 0
    for version in versions:
        tranches = (version.get("contenu") or {}).get("parametres") or {}
        if not tranches:
            continue
        attendues = sorted((t["assiette"], t["taux_cotisation_retraite"])
                           for t in tranches.values())
        debut, fin = version["bornes"]["revenu.annee"]
        for annee in range(max(debut.year, 2023), (fin.year if fin else 2041)):
            portees = sorted((p.assiette, p.taux_cotisation_retraite)
                             for p in caisse.periodes_actives(annee))
            assert portees == attendues, (version["id"], annee)
            lues += 1
    assert lues == 18


#: Le report de la Cipav ne majore que « les points acquis au titre des trente
#: premières années de cotisation » (statuts, article 3.15, depuis 2008 ;
#: décret n° 79-262, article 5-2, II, LEGIARTI000054168515, depuis le
#: 1er juillet 2026). Ligne 14 de la file des corrections (action 130), au
#: décompte des trente ans le plus favorable à l'affilié : de date à date
#: depuis la première cotisation, l'année où ils s'achèvent prise en entier.
#: Libéral de la Cipav au double du salaire moyen, un an entier de report ;
#: les cotisations revalorisées, année par année, sont celles des notes
#: `130/2026-11-06-e10-decret-2026-418.md` et `…-e11-surcote-par-age-seul.md`,
#: et chaque pension est posée à la main : (naissance, âge demandé, début) →
#: (les années majorées, la pension).
REPORT_DE_LA_CIPAV_AU_TEXTE = {
    # Née le 10 mars 1949, libérale depuis 1971, pension au 1er janvier 2016.
    # Le régime est institué « à compter du 1er janvier 1979 » (décret
    # n° 79-262, article 1er, LEGIARTI000006767470) : 1979 est entière, les
    # trente années vont de 1979 à 2008. 193 940,3125 × 0,062 = 12 024,2994 ;
    # 0,05 × 0,062 × 137 466,6071 = 426,1465 ; 12 450,45 €.
    ("1949-03-10", "66.75", "22"): ("de 1979 à 2008", 12450.45),
    # Née le 10 mars 1957, cotisante depuis le 10 mars 1979, pension au
    # 1er janvier 2026 : 1979 est partielle, trente ans de date à date
    # s'achèvent le 9 mars 2009, 2009 prise en entier. 354 057,8613 × 0,061 =
    # 21 597,5295 ; 0,05 × 0,061 × 177 676,4629 = 541,9132 ; 22 139,44 €.
    ("1957-03-10", "68.75", "22"): ("de 1979 à 2009", 22139.44),
    # Née le 10 mars 1959, cotisante depuis le 10 mars 1981, pension au
    # 1er juillet 2027, sous le décret : de 1981 à 2011. 374 715,4414 × 0,061
    # = 22 857,6419 ; 0,05 × 0,061 × 194 651,6538 = 593,6875 ; 23 451,33 €.
    ("1959-03-10", "68.25", "22"): ("de 1981 à 2011", 23451.33),
}


def test_la_cipav_ne_majore_que_les_trente_premieres_annees_dans_les_deux_moteurs():
    from outils_pont import servi_et_refait
    from test_complementaires_liberales_a_leur_age import REQUETE

    requete = {**REQUETE, "statut": "profession_liberale"}
    # Le contrôle : cotisante depuis le 10 mars 1985, trente et une années
    # civiles jusqu'à 2015, la première partielle : toutes sont majorées.
    controle = ("1949-03-10", "66.75", "36")
    cas = [{"cle": "|".join(cle),
            "requete": {**requete, "naissance": cle[0], "liquidation": cle[1],
                        "debut": cle[2]}}
           for cle in (*REPORT_DE_LA_CIPAV_AU_TEXTE, controle)]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus

    def pension(cle):
        return {p["regime"]: p for p in servis["|".join(cle)]["actuel"]
                ["pensions_par_regime"]}["cipav_complementaire"]

    for cle, (annees, montant) in REPORT_DE_LA_CIPAV_AU_TEXTE.items():
        servie = pension(cle)
        assert servie["montant"] == pytest.approx(montant, abs=0.01), (cle, servie["detail"])
        assert annees in servie["detail"], (cle, servie["detail"])
    assert pension(controle)["detail"].endswith("coefficient de majoration 1.0500")


def test_la_cipav_majore_le_report_depuis_2008_dans_les_deux_moteurs():
    """Ligne 15 de la file des corrections (action 130) : l'article 3.15 des
    statuts de 2006 vaut depuis le 1er janvier 2008, où tombent les deux
    articles de 1979 que l'arrêté du 3 octobre 2006 gardait
    (JORFARTI000002050100) ; les arrêtés du 16 décembre 2021, 19°
    (JORFARTI000044554134), et du 20 mars 2023, 17° (JORFARTI000047334800),
    en montrent le texte : 5 % par année entière de report après 65 ans, avec
    trente années d'affiliation, sur les points des trente premières années.
    Le modèle ne majorait rien avant 2013."""
    from outils_pont import servi_et_refait
    from test_complementaires_liberales_a_leur_age import REQUETE

    requete = {**REQUETE, "statut": "profession_liberale", "liquidation": "66.75",
               "debut": "22"}
    # Née le 10 mars 1945, libérale depuis 1967, pension au 1er janvier 2012,
    # un an entier de report (65 ans le 10 mars 2010) ; trente-trois années au
    # régime, de 1979 à 2011, les trente premières de 1979 à 2008. Cotisations
    # revalorisées de la note `130/2026-11-06-e11-surcote-par-age-seul.md` :
    # 157 922,1741 × 0,062 = 9 791,1748 ; 0,05 × 0,062 × 135 298,4577 =
    # 419,4252 ; 10 210,60 €.
    # Née le 10 mars 1942, pension au 1er janvier 2009 : trente années au
    # régime, de 1979 à 2008, toutes majorées, 1,05.
    # Née le 10 mars 1940, pension au 1er janvier 2007 : l'année 2007, que le
    # texte ne tranche pas, reste hors de la file, sans majoration.
    cas = [{"cle": naissance, "requete": {**requete, "naissance": naissance}}
           for naissance in ("1945-03-10", "1942-03-10", "1940-03-10")]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus

    def pension(cle):
        return {p["regime"]: p for p in servis[cle]["actuel"]
                ["pensions_par_regime"]}["cipav_complementaire"]

    de_2012 = pension("1945-03-10")
    assert de_2012["montant"] == pytest.approx(10210.60, abs=0.01), de_2012["detail"]
    assert "de 1979 à 2008" in de_2012["detail"]
    assert pension("1942-03-10")["detail"].endswith("coefficient de majoration 1.0500")
    assert "majoration" not in pension("1940-03-10")["detail"]


def test_la_carpimko_majore_le_report_des_le_3_octobre_2015_dans_les_deux_moteurs():
    """Ligne 16 de la file des corrections (action 130) : l'arrêté du
    31 juillet 2015, publié le 2 octobre 2015 sans date d'effet
    (JORFARTI000031255544, JORFARTI000031255547), entre en vigueur le
    3 octobre 2015 ; son article 12 ter majore de « 1,25 % par trimestre civil
    entier d'ajournement postérieur à l'âge du taux plein dans la limite de
    vingt trimestres ». Le modèle ne servait l'arrêté qu'aux pensions de
    2016."""
    from outils_pont import servi_et_refait
    from test_complementaires_liberales_a_leur_age import REQUETE

    # Né le 10 mars 1949, auxiliaire médical depuis ses 25 ans : 160 trimestres
    # à 65 ans, quand sa génération en doit 161 ; le taux plein lui vient de
    # l'âge seul, 65 ans (article 12 quater, 1°, « GÉNÉRATION 1955 ET
    # ANTÉRIEURE […] 65 ans »), le 10 mars 2014. Trimestres civils entiers
    # d'ajournement : d'avril 2014 à septembre 2015, six, pour une pension du
    # 1er novembre comme du 1er décembre 2015 ; 1 + 6 × 0,0125 = 1,075.
    # Au 1er novembre 2015, 5 298,1861 € sans majoration (note
    # `130/2026-11-06-e13-surcote-par-age-seul.md`) : × 1,075 = 5 695,55 €,
    # 397,36 € de plus. Au 1er octobre 2015, l'arrêté n'est pas en vigueur.
    requete = {**REQUETE, "statut": "auxiliaire_medical", "naissance": "1949-03-10"}
    cas = [{"cle": mois, "requete": {**requete, "liquidation": age}}
           for mois, age in (("octobre", "66.5"), ("novembre", "66.5833"),
                             ("decembre", "66.6667"))]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus

    def pension(cle):
        return {p["regime"]: p for p in servis[cle]["actuel"]
                ["pensions_par_regime"]}["carpimko_complementaire"]

    assert "majoration" not in pension("octobre")["detail"]
    de_novembre = pension("novembre")
    assert de_novembre["detail"].endswith("coefficient de majoration 1.0750")
    assert de_novembre["montant"] == pytest.approx(5695.55, abs=0.01)
    assert pension("decembre")["detail"].endswith("coefficient de majoration 1.0750")


# -- la CNAVPL ------------------------------------------------------------------


def test_la_cnavpl_donne_aux_meres_leurs_trimestres_depuis_2010(simulateur):
    """Huit trimestres par enfant, portés par un régime en points."""
    avec, pensions = _calculer(simulateur, "profession_liberale", 1964, 62.75,
                               debut=24.0, sexe="F", enfants=2)
    sans, pensions_sans = _calculer(simulateur, "profession_liberale", 1964, 62.75,
                                    debut=24.0, sexe="F")
    assert avec.trimestres_valides - sans.trimestres_valides == 16
    # Sans eux, la décote de la CNAVPL — et celle de la Cipav, qui la suit.
    assert _coefficient(pensions_sans["cnavpl"].detail) < 1.0
    assert _coefficient(pensions["cnavpl"].detail) == pytest.approx(1.0)
    assert _coefficient(pensions["cipav_complementaire"].detail) == pytest.approx(1.0)
    # Avant le 1er avril 2010, la CNAVPL n'en donnait aucun.
    avant, _ = _calculer(simulateur, "profession_liberale", 1948, 60.0,
                         debut=24.0, sexe="F", enfants=2)
    avant_sans, _ = _calculer(simulateur, "profession_liberale", 1948, 60.0,
                              debut=24.0, sexe="F")
    assert avant.trimestres_valides == avant_sans.trimestres_valides


def test_la_majoration_de_duree_n_ouvre_pas_les_bonifications_des_mines(simulateur):
    """Seule `mda` passe par un régime en points : les mines déclarent des
    bonifications, qui entrent aux services qu'elles n'ont pas."""
    periode = simulateur.catalogue["mines"].periode(2020)
    assert periode.type_calcul == "points"
    assert "bonifications" in periode.avantages_non_contributifs
    mere = Carriere.depuis_parcours(
        annee_naissance=1958, sexe="F",
        metiers=[Metier(affiliation="salarie_prive_non_cadre", age_debut=20.0)],
        age_liquidation=62.0, macro=simulateur.macro, nombre_enfants=2,
    )
    actuel = simulateur.scenario_actuel
    assert compter.majoration_pour_enfants(actuel, mere, {"mines": 160}, 2020) is None
    porteur = compter.majoration_pour_enfants(actuel, mere, {"cnavpl": 160}, 2020)
    assert porteur is not None and porteur.regimes == ["cnavpl"]
    assert porteur.trimestres == 16


@pytest.mark.parametrize("annee,valeur", [
    (2004, 0.484), (2005, 0.493), (2008, 0.522), (2014, 0.562),
    # Deux valeurs en 2022 : 0,5795 € au 1er janvier, 0,6027 € au 1er juillet,
    # et c'est celle du 31 décembre qui vaut pour l'année.
    (2022, 0.6027), (2026, 0.6599),
])
def test_la_valeur_de_service_de_la_cnavpl_est_celle_qu_elle_publie(
        simulateur, annee, valeur):
    lue = simulateur.scenario_actuel.valeurs_point.service("cnavpl", annee)
    assert lue is not None and lue[0] == pytest.approx(valeur)


@pytest.mark.parametrize("revenu,points", [(20_000, 238.6), (80_000, 565.5)])
def test_les_points_des_exemples_de_la_cnavpl(simulateur, revenu, points):
    """Page « Comprendre sa retraite » de la CNAVPL, paramètres de 2025 : « Revenu
    annuel de 20 000 € », 236,5 points en tranche 1 et 2,1 en tranche 2 ;
    « 80 000 € », les 557 points du plafond et 8,5. La caisse arrondit le total
    au dixième."""
    carriere = Carriere.depuis_releve(
        annee_naissance=1959, sexe="H",
        releve=[LigneRelevee(annee=2025, affiliation="profession_liberale",
                             revenu=float(revenu))],
        age_liquidation=67.0, macro=simulateur.macro,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    detail = {p.regime: p.detail for p in resultat.pensions_par_regime}["cnavpl"]
    assert float(detail.split(" points")[0].replace(",", "")) == pytest.approx(
        points, abs=0.05)


def test_chaque_annee_de_la_cnavpl_porte_les_points_de_sa_version(simulateur):
    """`points_au_prorata_des_cotisations`, lue au droit le 29 octobre 2026
    (action 130) : la cotisation au plafond de chaque tranche de D. 642-3 ouvre
    les points de D. 643-1 — 450 et 100 points de 2004 à 2014, sur 85 % du
    plafond puis jusqu'à cinq plafonds ; 525 et 25 de 2015 à 2024, sur un
    plafond et sur cinq ; 557 et 25 depuis 2025 — et, avant 2004, chaque
    trimestre validé cent points (loi n° 2003-775, article 96, II). Chaque
    année de revenu qu'une version couvre a, dans `regimes/cnavpl.yaml`, les
    périodes qui portent ce qu'elle lit."""
    from retraite_notionnelle.noyau import carte

    regime = simulateur.catalogue["cnavpl"]
    versions = carte.fiches()["points_au_prorata_des_cotisations"].get("versions") or []
    assert versions
    for version in versions:
        lus = version["contenu"]["parametres"]
        debut, fin = version["bornes"]["revenu.annee"]
        for annee in range(debut.year if debut else regime.creation,
                           fin.year if fin else 2041):
            periodes = regime.periodes_actives(annee)
            if "points_par_trimestre_valide" in lus:
                assert [p.points_par_trimestre_valide for p in periodes] == [
                    lus["points_par_trimestre_valide"]], (version["id"], annee)
                continue
            assert [p.points_maximum for p in periodes] == lus["points_au_plafond"], annee
            assert [list(p.bornes_assiette_en_pass()) for p in periodes] == lus[
                "tranches_en_plafonds"], annee
            assert all(p.points_au_prorata_des_cotisations for p in periodes), annee


def test_les_valeurs_que_d_643_1_ecrit_sont_celles_du_modele(simulateur):
    """`cnavpl_valeur_service`, lue au droit le 29 octobre 2026 (action 130) :
    D. 643-1 écrit la valeur de service lui-même, « 0,484 Euros » en 2004,
    « 0,493 euros pour les prestations servies au titre de l'année 2005 »,
    avant que L. 643-1 ne la fasse revaloriser comme les pensions ; la version
    qui les lit et `regimes/valeurs_point.csv` disent les mêmes."""
    from retraite_notionnelle.noyau import carte

    lues = {}
    for version in carte.fiches()["cnavpl_valeur_service"].get("versions") or []:
        parametres = version["contenu"].get("parametres")
        if isinstance(parametres, dict):
            lues.update(parametres.get("valeurs_de_service", {}))
    assert lues == {2004: 0.484, 2005: 0.493}
    for annee, valeur in lues.items():
        assert simulateur.scenario_actuel.valeurs_point.service("cnavpl", annee)[0] == (
            pytest.approx(valeur))


@pytest.mark.parametrize("annee", [2023, 2024, 2025, 2026])
def test_l_assiette_minimale_valide_trois_trimestres(simulateur, annee):
    """450 SMIC horaires font trois seuils de 150 : la virgule flottante en
    rendait deux en 2025."""
    macro = simulateur.macro
    assert macro.trimestres_valides(450 * macro.smic_horaire(annee), annee) == 3


def test_la_classe_suit_l_annee_de_revenu_et_le_debut_d_activite():
    """Action 131 : la classe de l'exercice se lit sur le revenu de l'année que
    le texte désigne, et le début d'activité impose sa classe
    (`classes_cotisation_epoques.yaml`, bloc ``regles``)."""
    from pathlib import Path
    from types import SimpleNamespace

    from retraite_notionnelle.donnees.regimes import ClassesCotisation

    racine = Path(__file__).resolve().parents[1] / "data"
    classes = ClassesCotisation(racine)
    lignes = [SimpleNamespace(annee=a, revenu=r, affiliation="expert_comptable",
                              cotise=True)
              for a, r in ((2014, 20_000.0), (2015, 30_000.0), (2016, 90_000.0),
                           (2017, 10_000.0), (2018, 60_000.0))]
    carriere = SimpleNamespace(
        lignes=lignes,
        lignes_de=lambda annee: [l for l in lignes if l.annee == annee])
    retenu = lambda annee, revenu: classes.revenu_retenu(
        "cavec_complementaire", annee, revenu, carriere, "expert_comptable")
    # Classe A d'office les deux premières années civiles (statuts de 2012).
    assert retenu(2014, 20_000.0) == (20_000.0, 0)
    assert retenu(2015, 30_000.0) == (30_000.0, 0)
    # Puis le revenu de l'avant-dernière année (statuts de 2008).
    assert retenu(2016, 90_000.0) == (20_000.0, None)
    assert retenu(2018, 60_000.0) == (90_000.0, None)
    # La classe imposée est la première de la grille.
    assert classes.cotisation("cavec_complementaire", 2014, 500_000.0,
                              rang=0)[0] == 583.0
    # Avant 2008, rien n'est lu : l'année même.
    assert classes.revenu_retenu("cavec_complementaire", 2005, 40_000.0,
                                 carriere, "expert_comptable") == (40_000.0, None)


def test_la_carpv_de_1998_a_2015_suit_le_taux_d_appel_du_decret():
    """Action 131 : de 1998 à 2015, la CARPV appelle 480, 600 et 720 actes
    médicaux vétérinaires au taux d'appel du décret annuel ; l'acte, que rien
    ne publie, est tiré de la valeur d'achat du point de 2016 au rapport des
    plafonds (`classes_cotisation_epoques.yaml`)."""
    from pathlib import Path

    from retraite_notionnelle.donnees.regimes import ClassesCotisation

    classes = ClassesCotisation(Path(__file__).resolve().parents[1] / "data")
    grille = classes.grille("carpv_complementaire", 2015)
    assert [c.cotisation for c in grille] == pytest.approx(
        [7136 * 38040 / 38616 * r for r in (1, 1.25, 1.5)], abs=0.01)
    assert grille[0].revenu_maximum / grille[1].revenu_maximum == pytest.approx(0.75, rel=1e-4)
    # De 77 % en 2001 à 104 % en 2015, à plafond constant.
    b2001 = classes.grille("carpv_complementaire", 2001)[0].cotisation
    assert b2001 / grille[0].cotisation == pytest.approx(
        0.77 / 1.04 * 27349 / 38040, rel=1e-3)


@pytest.mark.parametrize("regime,annee,francs", [
    # Décret n° 84-442 du 12 juin 1984, article 1 (LEGIARTI000006767456).
    ("cipav_complementaire", 1984, (2038, 4076, 6114, 10190, 14266, 20380)),
    # Décret n° 85-1092 du 10 octobre 1985, article 1 (LEGIARTI000006768801).
    ("cipav_complementaire", 1985, (2180, 4360, 6540, 10900, 15260, 21800)),
    # Décret n° 91-864 du 30 août 1991, article 1, que l'index JORF range sous
    # un décret de délégation de signature du même Journal officiel : la classe
    # 1 de la Cipav (JORFARTI000001376516), deux, trois, cinq, sept et dix fois
    # elle ensuite ; les classes 4 à 18 de la CAVEC (JORFARTI000001183737).
    ("cipav_complementaire", 1991, (2772, 5544, 8316, 13860, 19404, 27720)),
    ("cavec_complementaire", 1991, (8832, 11040, 15456, 22080, 26496, 33120, 39744)),
])
def test_la_classe_de_reference_est_celle_du_decret_de_l_exercice(regime, annee, francs):
    """Action 131 : les décrets annuels de 1984, de 1985 et de 1991, que le
    dépôt n'avait pas lus, fixent la classe de référence de la Cipav et de la
    CAVEC, dont chaque classe est le multiple que l'article 2 écrit
    (`classes_cotisation_epoques.yaml`)."""
    from pathlib import Path

    from retraite_notionnelle.donnees.regimes import ClassesCotisation

    classes = ClassesCotisation(Path(__file__).resolve().parents[1] / "data")
    assert [c.cotisation for c in classes.grille(regime, annee)] == pytest.approx(
        [f / 6.55957 for f in francs], abs=0.01)


def _points_de_l_annee(points, code: str, annee: int) -> float:
    """Les points qu'un régime porte au compte d'une année, depuis les crédits
    ``(régime, année, points, …)`` du relevé."""
    return round(sum(nombre for regime, annee_credit, nombre, *_ in points
                     if regime == code and annee_credit == annee), 6)


def test_les_points_d_une_annee_incomplete_suivent_sa_cotisation(simulateur):
    """« Le versement de la cotisation annuelle correspondant au plafond de
    revenu [...] ouvre droit à l'attribution de 525 points », 25 pour la
    seconde tranche, et « le nombre de points acquis est calculé au prorata des
    cotisations acquittées sur chacune des tranches » (D. 643-1,
    LEGIARTI000029825121), un plafond et cinq (D. 642-3, LEGIARTI000041966479) ;
    une affiliation de moins d'un an réduit le plafond « au prorata de la
    durée d'affiliation » (R. 613-17, LEGIARTI000038750258 ; « des trimestres
    d'affiliation » jusqu'en 2020, D. 642-3). Le libéral à 40 000 € par an, parti le 1er juillet
    2020, a cotisé en 2020 sur les 20 000 € de ses six mois : 525 × 20 000 /
    41 136 = 255,25 points en tranche 1, et 25 × 20 000 / 205 680 = 2,43 en
    tranche 2, la moitié de ce qu'une année entière lui vaudrait, et non les
    515,36 points que le rapport d'une assiette et d'un repère tous deux
    réduits à six mois rendait. L'année 2019, entière, garde les siens :
    525 × 40 000 / 40 524 et 25 × 40 000 / 202 620. La caisse arrondit au
    dixième de point ; le modèle n'arrondit pas. Dans les deux moteurs."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    from retraite_notionnelle.carriere import AnneeCarriere
    from retraite_notionnelle.droit import releve

    def lignes():
        return [dict(annee=annee, revenu=40_000.0, affiliation="profession_liberale")
                for annee in range(1985, 2021)]

    carriere = Carriere(annee_naissance=1958, mois_naissance=1, jour_naissance=15,
                        sexe="H", lignes=[AnneeCarriere(**ligne) for ligne in lignes()],
                        age_liquidation=62.0 + 5 / 12)
    assert str(carriere.date_liquidation) == "juillet 2020"
    attendu = {2019: 525 * 40_000 / 40_524 + 25 * 40_000 / 202_620,
               2020: 525 * 20_000 / 41_136 + 25 * 20_000 / 205_680}
    points = releve.construire(simulateur.scenario_actuel, carriere).droits.points
    assert {annee: _points_de_l_annee(points, "cnavpl", annee) for annee in attendu} \
        == pytest.approx(attendu, abs=1e-6)
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    script = """
import { readFileSync } from "node:fs";
import { AnneeCarriere, Carriere } from "./moteur/js/carriere.js";
import { Contexte } from "./moteur/js/contexte.js";
import { construire } from "./moteur/js/droit/releve.js";
const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
const simulateur = contexte.simulateur();
const carriere = new Carriere({
  annee_naissance: 1958, mois_naissance: 1, jour_naissance: 15, sexe: "H",
  age_liquidation: 62 + 5 / 12,
  lignes: JSON.parse(process.argv[1]).map((ligne) => new AnneeCarriere(ligne)) });
process.stdout.write(JSON.stringify(
  [...construire(simulateur.scenarioActuel, carriere).droits.points]));
"""
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", script, json.dumps(lignes())],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus = json.loads(execution.stdout)
    assert {annee: _points_de_l_annee(obtenus, "cnavpl", annee) for annee in attendu} \
        == pytest.approx(attendu, abs=1e-6)


#: Les 32 documents de l'index JORF qui portent les 31 articles du décret
#: n° 2026-418 du 29 mai 2026 (JORFTEXT000054153355) : la fin de l'article 18
#: y est un document à part, étiqueté « art. 8 » (JORFARTI000054153640).
#: Chacun avec le texte qu'il modifie, lu à son visa (le décret n° … ou, pour
#: l'article 1er, D. 641-6 du code de la sécurité sociale ; rien pour les
#: articles 29 à 31), et les fiches de règle auxquelles la fiche du décret le
#: rapporte (action 130, relu par R-E11 ; table tenue par E11).
ARTICLES_DU_DECRET_2026_418 = {
    "1": ("JORFARTI000054153395", "D. 641-6", set()),
    "2": ("JORFARTI000054153399", "49-578", {
        "cprn_ages_decote_enfants", "cotisation_par_classes_liberales",
        "rachats_et_versements"}),
    "3": ("JORFARTI000054153420", "49-579", {
        "carmf_asv_minoration_enfants", "rachats_et_versements"}),
    "4": ("JORFARTI000054153444", "49-580", {"cavp_minoration_deux_pentes"}),
    "5": ("JORFARTI000054153467", "50-28", {
        "carcdsf_minoration_age_seul", "rachats_et_versements"}),
    "6": ("JORFARTI000054153484", "50-1318", {
        "carpv_minoration_age_seul", "cotisation_par_classes_liberales",
        "rachats_et_versements", "retraite_progressive"}),
    "7": ("JORFARTI000054153492", "51-310", set()),
    "8": ("JORFARTI000054153497", "53-506", {
        "cavec_minoration_age_seul", "cotisation_par_classes_liberales",
        "rachats_et_versements"}),
    "9": ("JORFARTI000054153507", "55-1390", set()),
    "10": ("JORFARTI000054153523", "60-664", set()),
    "11": ("JORFARTI000054153529", "61-1488", set()),
    "12": ("JORFARTI000054153554", "65-1139", set()),
    "13": ("JORFARTI000054153565", "67-1169", {"cavamac_minoration_age_seul"}),
    "14": ("JORFARTI000054153583", "68-884", set()),
    "15": ("JORFARTI000054153594", "70-803", set()),
    "16": ("JORFARTI000054153605", "72-968", {
        "asv_medecins_points", "asv_medecins_ajustement"}),
    "17": ("JORFARTI000054153623", "74-526", set()),
    "18": ("JORFARTI000054153633", "75-891", {"asv_autres_professions_de_sante"}),
    "18, fin": ("JORFARTI000054153640", "75-891", {"asv_autres_professions_de_sante"}),
    "19": ("JORFARTI000054153644", "78-283", {
        "asv_autres_professions_de_sante", "rachats_et_versements"}),
    "20": ("JORFARTI000054153655", "79-262", {
        "cipav_seconde_tranche", "sections_liberales_majoration_enfants",
        "surcote_par_age_seul"}),
    "21": ("JORFARTI000054153680", "79-263", set()),
    "22": ("JORFARTI000054153714", "79-265", {
        "cavom_assiette_2016", "cavom_ages_minoration"}),
    "23": ("JORFARTI000054153729", "81-755", set()),
    "24": ("JORFARTI000054153737", "81-1046", {"asv_autres_professions_de_sante"}),
    "25": ("JORFARTI000054153756", "84-143", {
        "carpimko_assiette_2026", "carpimko_ages_2015", "rachats_et_versements"}),
    "26": ("JORFARTI000054153775", "84-254", {"asv_autres_professions_de_sante"}),
    "27": ("JORFARTI000054153787", "2003-1273", set()),
    "28": ("JORFARTI000054153800", "2016-1991", set()),
    "29": ("JORFARTI000054153809", None, set()),
    "30": ("JORFARTI000054153813", None, set()),
    "31": ("JORFARTI000054153814", None, set()),
}


def _rapport_de_l_article(lectures: list[str], identifiant: str, fiches: dict,
                          ) -> tuple[str | None, set[str]]:
    """Ce que la lecture d'un article en dit : le premier texte modifié nommé
    après son identifiant (un décret « n° AA-NNN », ou D. 641-6), et les
    fiches qu'elle nomme entre accents graves ; ``(None, set())`` sans
    lecture. Une lecture qui porte plusieurs articles n'en nomme aucune."""
    import re

    trouvees = [r for r in lectures if identifiant in r]
    if not trouvees:
        return None, set()
    lecture = trouvees[0]
    suite = lecture[lecture.index(identifiant):]
    vise = re.search(r"n° (\d+-\d+)|D\. 641-6", suite)
    texte = None if vise is None else vise.group(1) or vise.group(0)
    return texte, {nom for nom in re.findall(r"`(\w+)`", lecture) if nom in fiches}


def test_chaque_article_du_decret_2026_418_est_rapporte_a_la_fiche_de_sa_regle():
    """La fiche du décret porte un texte, non un dispositif (architecture,
    § 6.1) : elle rapporte chacun de ses articles, lu au JORF, au texte qu'il
    modifie et aux fiches de ses règles, ou le dit hors du modèle (action 130,
    E10). La table ci-dessus le tient article par article : le texte que la
    lecture de l'article nomme le premier après son identifiant, et les fiches
    qu'elle nomme, exactement (E11, après R-E11). Chaque nom écrit entre accents
    graves est une fiche, une version de fiche ou un paramètre d'un régime."""
    import re

    import yaml

    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.noyau import carte

    def cles(valeur):
        if isinstance(valeur, dict):
            return set(valeur) | {c for v in valeur.values() for c in cles(v)}
        return {c for v in valeur for c in cles(v)} if isinstance(valeur, list) else set()

    fiches = carte.fiches()
    lectures = [lecture["reference"] for lecture in
                fiches["decret_2026_418_liberaux"]["sources"]["lectures"]]
    lus = {numero: _rapport_de_l_article(lectures, identifiant, fiches)
           for numero, (identifiant, _, _) in ARTICLES_DU_DECRET_2026_418.items()}
    assert [n for n, (i, _, _) in ARTICLES_DU_DECRET_2026_418.items()
            if not any(i in r for r in lectures)] == []
    assert lus == {numero: (texte, fiches_attendues) for numero, (_, texte, fiches_attendues)
                   in ARTICLES_DU_DECRET_2026_418.items()}
    connus = set(fiches) | {v["id"] for f in fiches.values() for v in f.get("versions") or []}
    for chemin in (RACINE_DONNEES / "reference" / "regimes").glob("*.yaml"):
        connus |= cles(yaml.safe_load(chemin.read_text(encoding="utf-8")))
    nommes = {nom for r in lectures for nom in re.findall(r"`(\w+)`", r)}
    assert sorted(nommes - connus) == []


def test_la_table_du_decret_2026_418_garde_ses_32_documents():
    """La table porte les 32 documents d'articles du décret, ni plus ni moins :
    les articles 1 à 31, et la fin de l'article 18 juste après lui, chacun
    sous un identifiant à lui, qui croît d'un document au suivant comme au
    Journal officiel ; seuls les articles 29 à 31 ne modifient aucun texte.
    Une ligne ôtée de la table la rougit (R-E12, 3 ; E12)."""
    assert list(ARTICLES_DU_DECRET_2026_418) == (
        [str(n) for n in range(1, 19)] + ["18, fin"] + [str(n) for n in range(19, 32)])
    identifiants = [i for i, _, _ in ARTICLES_DU_DECRET_2026_418.values()]
    assert identifiants == sorted(set(identifiants))
    assert [n for n, (_, texte, _) in ARTICLES_DU_DECRET_2026_418.items()
            if texte is None] == ["29", "30", "31"]


def test_la_table_du_decret_2026_418_est_celle_de_l_index_jorf():
    """L'index JORF récupéré, ses documents d'articles du décret n° 2026-418
    sont ceux de la table, chacun sous son numéro ; la fin de l'article 18 y
    est étiquetée « 8 » (relevé le 6 novembre 2026, E12)."""
    import sqlite3

    from retraite_notionnelle.config import RACINE_DONNEES

    base = RACINE_DONNEES / "brut" / "dila" / "jorf.sqlite"
    if not base.is_file():
        pytest.skip("l'index JORF n'est pas récupéré (dila_index.py jorf --recuperer)")
    with sqlite3.connect(base) as connexion:
        documents = dict(connexion.execute(
            "SELECT id, num FROM doc WHERE nature = 'Article DECRET' "
            "AND titre LIKE 'Décret n° 2026-418 du 29 mai 2026 %'"))
    assert documents == {i: "8" if n == "18, fin" else n
                         for n, (i, _, _) in ARTICLES_DU_DECRET_2026_418.items()}


# -- la date d'effet au trimestre civil (action 130, la file, ligne 12) --------

#: La requête du formulaire d'un libéral, au salaire de deux Smic.
REQUETE_DE_LIBERAL = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "primes": "0", "profil": "plat", "projection": "cor_reference",
    "salaire": "2", "sexe": "H", "stock": "prix", "table": "unisexe",
}

#: Les dates présumées — le premier du mois qui suit l'âge demandé — que le
#: texte lu de chaque caisse reporte au premier jour du trimestre civil qui
#: suit, [depuis, jusqu'à) : CAVOM, statuts de 2016, article 14, II, en vigueur
#: le 1er janvier 2016, et règlement de 2026 ; CARPIMKO, statuts de 1984,
#: article 11, jusqu'à l'arrêté du 20 mai 1987, non lu, en vigueur le 5 juin,
#: puis règlement de 2026, article 7, en vigueur le 18 juillet 2026 ; CAVP,
#: statuts du 11 mai 2009, article 14, en vigueur le 7 juin 2009, et règlement
#: de 2026 ; CARMF, règlement de 2026, I, article 24.
TRIMESTRE_CIVIL = {
    "cavom_complementaire": [("2016-01-01", None)],
    "carpimko_complementaire": [("1984-01-01", "1987-06-05"), ("2026-07-18", None)],
    "cavp_complementaire": [("2009-06-07", None)],
    "carmf_complementaire": [("2026-07-18", None)],
}


def test_les_quatre_caisses_portent_la_date_d_effet_au_trimestre_civil(simulateur):
    """Chaque premier du mois de 1949 à 2040, la période qui liquide une
    pension de ce jour dit si le texte lu la reporte au trimestre civil
    (`effet_au_trimestre_civil`, [depuis, jusqu'à)) ; aucun autre régime ne
    le dit : ce que nul texte lu ne fixe reste au premier du mois."""
    for code, plages in TRIMESTRE_CIVIL.items():
        caisse = simulateur.catalogue[code]
        for annee in range(1949, 2041):
            for mois in range(1, 13):
                jour = f"{annee:04d}-{mois:02d}-01"
                periode = caisse.periode_a_l_effet(jour)
                plage = None if periode is None else periode.effet_au_trimestre_civil
                porte = plage is not None and plage[0] <= jour and (
                    plage[1] is None or jour < plage[1])
                attendu = any(depuis <= jour and (jusqu is None or jour < jusqu)
                              for depuis, jusqu in plages)
                assert porte == attendu, (code, jour)
    autres = sorted(regime.code for regime in simulateur.catalogue
                    for periode in regime.periodes
                    if periode.effet_au_trimestre_civil is not None)
    assert sorted(set(autres)) == sorted(TRIMESTRE_CIVIL)


#: (statut, naissance, âge du début, âge demandé) : la complémentaire, la date
#: d'effet que son texte lui fixe, et son coefficient, posés à la main.
EFFETS_AU_TRIMESTRE_CIVIL = {
    # CAVOM. Né le 10 mai 1959, 62 ans le 10 mai 2021 : la base le 1er juin,
    # la CAVOM « au plus tôt au premier jour du trimestre civil qui suit » la
    # demande et la cessation, le 1er juillet 2021, à 62 ans, 0,75.
    ("officier_ministeriel", "1959-05-10", "25", "62"):
        ("cavom_complementaire", "2021-07-01", 0.75),
    # Né le 1er mai 1959, que le modèle sert dès le 1er mai : le 1er juillet.
    ("officier_ministeriel", "1959-05-01", "25", "62"):
        ("cavom_complementaire", "2021-07-01", 0.75),
    # Né le 1er mars 1959, servi dès le 1er mars : le 1er avril.
    ("officier_ministeriel", "1959-03-01", "25", "62"):
        ("cavom_complementaire", "2021-04-01", 0.75),
    # CARPIMKO, règlement de 2026, article 7. Né le 10 novembre 1959, entré à
    # 26 ans, demande à 67 ans, en novembre 2026 : le 1er janvier 2027 ; son
    # taux plein à 66 ans et 4 mois, en mars 2026, trois trimestres civils
    # entiers d'ajournement, d'avril à décembre 2026 : 1,0375.
    ("auxiliaire_medical", "1959-11-10", "26", "67"):
        ("carpimko_complementaire", "2027-01-01", 1.0375),
    # Statuts de 1984, article 11. Né le 10 mai 1920, 65 ans le 10 mai 1985 :
    # le 1er juillet 1985, sans coefficient.
    ("auxiliaire_medical", "1920-05-10", "25", "65"):
        ("carpimko_complementaire", "1985-07-01", 1.0),
    # CAVP, règlement de 2026, article 14. Né le 10 mai 1960, entré à 21 ans,
    # demande à 67 ans, en mai 2027 : le 1er juillet 2027, sans majoration (un
    # mois et 21 jours au-delà de 67 ans).
    ("pharmacien", "1960-05-10", "21", "67"):
        ("cavp_complementaire", "2027-07-01", 1.0),
    # Statuts du 11 mai 2009, article 14, en vigueur le 7 juin 2009. Né le
    # 10 août 1944, 65 ans le 10 août 2009 : le 1er octobre 2009.
    ("pharmacien", "1944-08-10", "25", "65"):
        ("cavp_complementaire", "2009-10-01", 1.0),
    # CARMF, règlement de 2026, I, article 24. Né le 10 mai 1964, entré à
    # 22 ans, parti à 63 ans : le 1er juillet 2027 ; 62 ans le 10 mai 2026, quatre trimestres
    # du 1er juillet 2026 au 1er juillet 2027, 1,05.
    ("medecin_liberal", "1964-05-10", "22", "63"):
        ("carmf_complementaire", "2027-07-01", 1.05),
    # Né le 10 mars 1964, parti à 63 ans et un mois, en avril 2027 : le
    # 1er juillet 2027 ; 62 ans le 10 mars 2026, cinq trimestres du 1er avril
    # 2026 au 1er juillet 2027, 1,0625.
    ("medecin_liberal", "1964-03-10", "22", "63.0833"):
        ("carmf_complementaire", "2027-07-01", 1.0625),
    # Né le 10 juillet 1959, parti à 67 ans, que le modèle date du 1er août
    # 2026, passé le 18 juillet : le 1er octobre 2026 ; 62 ans le 10 juillet
    # 2021, 65 ans le 10 juillet 2024 : douze trimestres à 1,25 % du
    # 1er octobre 2021, huit à 0,75 % du 1er octobre 2024, 1,21.
    ("medecin_liberal", "1959-07-10", "22", "67"):
        ("carmf_complementaire", "2026-10-01", 1.21),
}

#: Les mêmes clés : la complémentaire que le texte lu ne reporte pas, servie
#: au départ déclaré, avec sa base.
EFFETS_AU_PREMIER_DU_MOIS = {
    # CAVOM. Né le 10 mars 1959 ou le 1er avril 1959 : le 1er avril 2021, qui
    # ouvre un trimestre civil.
    ("officier_ministeriel", "1959-03-10", "25", "62"): "cavom_complementaire",
    ("officier_ministeriel", "1959-04-01", "25", "62"): "cavom_complementaire",
    # Né le 10 mai 1950, parti à 65 ans le 1er juin 2015, avant les statuts
    # de 2016 : la règle d'avant n'est que présumée.
    ("officier_ministeriel", "1950-05-10", "25", "65"): "cavom_complementaire",
    # CARPIMKO. Né le 10 mai 1925, 65 ans en mai 1990, sous l'arrêté du
    # 20 mai 1987, non lu ; né le 10 mai 1959, 67 ans en mai 2026, sous des
    # statuts dont l'article qui date la pension n'est pas lu.
    ("auxiliaire_medical", "1925-05-10", "25", "65"): "carpimko_complementaire",
    ("auxiliaire_medical", "1959-05-10", "26", "67"): "carpimko_complementaire",
    # CAVP. Né le 10 février 1944, 65 ans en février 2009, avant le 7 juin.
    ("pharmacien", "1944-02-10", "25", "65"): "cavp_complementaire",
    # CARMF. Né le 10 mai 1959, parti à 67 ans le 1er juin 2026, avant le
    # règlement : les statuts d'alors ne sont pas lus sur ce point.
    ("medecin_liberal", "1959-05-10", "22", "67"): "carmf_complementaire",
}


@pytest.fixture(scope="module")
def effets_des_liberaux():
    """Chaque cas, servi par le portage et refait au bit près par le moteur
    Python (``servi_et_refait``)."""
    from outils_pont import servi_et_refait

    cas = [{"cle": "|".join(cle),
            "requete": {**REQUETE_DE_LIBERAL, "statut": cle[0], "naissance": cle[1],
                        "liquidation": cle[3], **({"debut": cle[2]} if cle[2] else {})}}
           for cle in [*EFFETS_AU_TRIMESTRE_CIVIL, *EFFETS_AU_PREMIER_DU_MOIS]]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


def _coefficient_de(detail: str) -> float:
    import re

    lu = re.search(r"coefficient d(?:'anticipation|e majoration) ([0-9.]+)", detail)
    return float(lu.group(1)) if lu else 1.0


_MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
         "septembre", "octobre", "novembre", "décembre")


@pytest.mark.parametrize("cle", EFFETS_AU_TRIMESTRE_CIVIL,
                         ids=["|".join(cle) for cle in EFFETS_AU_TRIMESTRE_CIVIL])
def test_la_complementaire_prend_effet_au_trimestre_civil_qui_suit(
        effets_des_liberaux, cle):
    """« La retraite prend effet au plus tôt au premier jour du trimestre civil
    qui suit le dernier des faits ci-après : - la demande [...] ; - la
    justification de la cessation d'activité » (CAVOM, statuts de 2016,
    article 14, II ; règlement de 2026, article 1er, II) ; « La date d'entrée
    en jouissance de la retraite est fixée au premier jour du trimestre civil
    qui suit la demande » (CARPIMKO, statuts de 1984, article 11 ; règlement de
    2026, article 7) ; « L'entrée en jouissance de la retraite de droits
    propres est fixée au premier jour du trimestre civil qui suit cette
    demande » (CAVP, statuts de 2009 et règlement de 2026, article 14) ; « La
    date d'effet de l'allocation est fixée au premier jour du trimestre civil
    qui suit la réalisation de toutes les conditions d'ouverture des droits »
    (CARMF, règlement de 2026, I, article 24). Jusqu'au 14 novembre 2026, le
    modèle servait ces pensions le premier du mois qui suit l'âge, avec la
    base : un ou deux mois trop tôt. La base, et l'ASV, que son règlement ne
    date pas, restent au départ déclaré : seule la complémentaire dit sa
    date."""
    regime, date, coefficient = EFFETS_AU_TRIMESTRE_CIVIL[cle]
    servi = effets_des_liberaux["|".join(cle)]
    pensions = {p["regime"]: p for p in servi["pensions_par_regime"]}
    [declare, reporte] = servi["departs"]
    assert declare["motif"] == "depart" and declare["date_effet"] < date
    assert reporte == {"date_effet": date, "motif": "trimestre_civil"}
    le_premier = f"servie à partir du 1er {_MOIS[int(date[5:7]) - 1]} {date[:4]}"
    assert [code for code, p in pensions.items() if "servie" in p["detail"]] == [regime]
    assert le_premier in pensions[regime]["detail"]
    assert _coefficient_de(pensions[regime]["detail"]) == pytest.approx(coefficient)


@pytest.mark.parametrize("cle", EFFETS_AU_PREMIER_DU_MOIS,
                         ids=["|".join(cle) for cle in EFFETS_AU_PREMIER_DU_MOIS])
def test_la_complementaire_reste_au_depart_quand_nul_texte_lu_ne_la_reporte(
        effets_des_liberaux, cle):
    """Une date qui ouvre déjà un trimestre civil, ou une pension que le texte
    lu ne date pas : un seul départ, le déclaré."""
    servi = effets_des_liberaux["|".join(cle)]
    pensions = {p["regime"]: p for p in servi["pensions_par_regime"]}
    assert pensions[EFFETS_AU_PREMIER_DU_MOIS[cle]]["montant"] > 0
    assert servi["departs"] == []


def test_la_date_d_effet_au_trimestre_civil_se_pose_a_la_main(effets_des_liberaux):
    """Les cas posés des fiches. La pension ne change que de date quand son
    coefficient ne bouge pas : l'officier ministériel, 13 580,64 € par an, un
    mois de trop, 1 131,72 € ; le pharmacien, 14 548,91 €, un mois, 1 212,41 € ;
    le médecin né le 10 mai 1964, 14 056,14 €, un mois, 1 171,35 €. Elle
    gagne les trimestres du report : le médecin né le 10 mars 1964, deux mois
    de trop, 2 337,68 €, puis 14 026,06 / 1,05 × 1,0625 = 14 193,04 € ; l'auxiliaire
    médical, un mois de trop, 475,50 €, puis 5 706,01 / 1,025 × 1,0375 =
    5 775,59 €, aux euros de 2026, l'année du départ déclaré."""
    def montant(cle, regime):
        pensions = effets_des_liberaux[cle]["pensions_par_regime"]
        return {p["regime"]: p for p in pensions}[regime]["montant"]

    assert montant("officier_ministeriel|1959-05-10|25|62",
                   "cavom_complementaire") == pytest.approx(13_580.64, abs=0.01)
    assert montant("pharmacien|1960-05-10|21|67",
                   "cavp_complementaire") == pytest.approx(14_548.91, abs=0.01)
    assert montant("medecin_liberal|1964-05-10|22|63",
                   "carmf_complementaire") == pytest.approx(14_056.14, abs=0.01)
    assert montant("medecin_liberal|1964-03-10|22|63.0833",
                   "carmf_complementaire") == pytest.approx(
                       14_026.06 / 1.05 * 1.0625, abs=0.01)
    assert montant("auxiliaire_medical|1959-11-10|26|67",
                   "carpimko_complementaire") == pytest.approx(
                       5_706.01 / 1.025 * 1.0375, abs=0.01)


def test_la_page_dit_la_complementaire_servie_au_trimestre_civil():
    """Le pharmacien né le 10 mai 1960, parti à 67 ans : la page dit que sa
    complémentaire ne commence que le 1er juillet 2027, et pourquoi."""
    from retraite_notionnelle.web.site import rendre

    page = rendre("/simuler", {**REQUETE_DE_LIBERAL, "statut": "pharmacien",
                               "naissance": "1960-05-10", "debut": "21",
                               "liquidation": "67"})[1]
    assert "Vos pensions ne commencent pas toutes à la\nmême date." in page
    assert "le 1<sup>er</sup> juillet 2027" in page
    assert "au premier jour du trimestre civil qui suit, comme ses statuts le fixent" in page
