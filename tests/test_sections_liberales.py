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


def test_la_cavamac_majore_de_dix_pour_cent_pour_trois_enfants(simulateur):
    resultat, pensions = _calculer(simulateur, "agent_general_assurance", 1960,
                                   67.0, sexe="F", enfants=3)
    assert _majoration(resultat, "cavamac_complementaire") == pytest.approx(
        0.10 * pensions["cavamac_complementaire"].montant)
    # Avant les statuts de 2011, rien n'est lu, rien n'est servi.
    resultat, _ = _calculer(simulateur, "agent_general_assurance", 1945, 65.0,
                            sexe="F", enfants=3)
    assert _majoration(resultat, "cavamac_complementaire") == 0.0


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
            assert {cle: getattr(periode, cle) for cle in lus} == lus, (version["id"], jour)
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

#: L'écart que la fiche déclare, lue au droit le 6 novembre 2026 (action 130,
#: E8) : les statuts de la CAVAMAC de 2011 entrent en vigueur le 1er juillet
#: 2011 (arrêté du 23 juin 2011, article 2) et majorent de 10 % les points de
#: l'adhérent qui a eu trois enfants (article 18) ; le modèle ne sert la
#: majoration qu'aux pensions qui prennent effet depuis le 1er janvier 2012.
#: Erreur prouvée, déclarée et non corrigée : les dates d'effet de juillet à
#: décembre 2011, où le modèle ne sert rien.
MAJORATION_OMISE_PAR_LE_MODELE = {
    ("cavamac_complementaire", 2011, mois) for mois in range(7, 13)}


def test_chaque_version_de_la_majoration_pour_enfants_des_sections_est_portee():
    """Lue au droit le 6 novembre 2026 (action 130) : à chaque date d'effet,
    mois par mois, de 1990 à 2040, la majoration que chaque version de
    ``sections_liberales_majoration_enfants`` donne à trois enfants est celle
    que la période de liquidation de chaque section déclare
    (``majoration_enfants`` dans ``avantages_non_contributifs``, que
    ``_taux_majoration_enfants`` sert à 10 %), hors l'écart déclaré."""
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
    assert omis == 6
    assert vus == 51 * 12 * 3 - 6


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
    # l'adhérent ayant eu au moins trois enfants ». Le modèle ne sert rien avant
    # le 1er janvier 2012 : erreur prouvée, déclarée, non corrigée (candidat 47).
    ("agent_general_assurance", "1946-03-10", "65.25"):  # 1er juillet 2011
        ((0.10,), 0.0, ("cavamac_depuis_juillet_2011", "cavamac_complementaire")),
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
    assert ecarts == 3


def test_la_majoration_pour_enfants_des_sections_aux_dates_qui_comptent_dans_les_deux_moteurs():
    """Le portage sert, et le moteur Python refait (``servi_et_refait``), à
    une mère de trois enfants de chaque section, la majoration que le modèle
    sert à la date d'effet (``MAJORATIONS_AUX_DATES_QUI_COMPTENT``, le taux
    servi) : 10 % de la pension de la complémentaire, ou rien. Au 1er juillet
    2011, la CAVAMAC ne reçoit rien où le texte donne 10 %, l'écart déclaré ;
    au 1er décembre 1999, la Cipav rien, l'une des deux lectures."""
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
