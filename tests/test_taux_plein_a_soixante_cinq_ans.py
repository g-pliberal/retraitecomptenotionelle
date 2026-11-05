"""Le taux plein à soixante-cinq ans du parent de trois enfants né du 1er juillet
1951 au 31 décembre 1955 (fiche ``taux_plein_a_soixante_cinq_ans``).

« Par dérogation aux dispositions de l'article L. 351-8 du code de la sécurité
sociale, l'âge mentionné au 1° dudit article est fixé à soixante-cinq ans pour
les assurés nés entre le 1er juillet 1951 et le 31 décembre 1955 inclus
lorsqu'ils remplissent les conditions suivantes : 1° Avoir eu ou élevé [...] au
moins trois enfants ; 2° Avoir interrompu ou réduit leur activité
professionnelle, dans des conditions et un délai déterminés suivant la
naissance ou l'adoption d'au moins un de ces enfants [...] ; 3° Avoir validé,
avant cette interruption ou réduction de leur activité professionnelle, un
nombre de trimestres minimum à raison de l'exercice d'une activité
professionnelle » (loi n° 2010-1330, article 20, IV, LEGIARTI000023023835).

Le décret n° 2011-620 du 31 mai 2011, article 2 (LEGIARTI000024111672), en fixe
les décomptes : « au plus huit trimestres au titre de l'année civile de la
naissance [...] et des deux années civiles suivantes ou, si l'enfant est né [...]
au cours d'un second semestre, au titre des trois années civiles suivant celle
de cette naissance », sans les trimestres de l'AVPF (L. 381-1) ni ceux de
l'invalidité et de l'accident du travail (R. 351-12, 3° et 5°) ; « au titre des
deux années précédant l'année de la naissance [...], un nombre de trimestres
égal ou supérieur à huit », les cotisations à la charge de l'assuré et les
arrêts maladie, la maternité, le chômage, la formation ; et huit trimestres
d'activité professionnelle avant l'interruption, que la caisse compte jusqu'au
« dernier jour du trimestre civil précédant la date de la naissance »
(circulaire Cnav n° 2014-64 du 23 décembre 2014, point 2.2.2).

L'âge du 1° de L. 351-8 est celui où la décote s'annule, et celui dont se
comptent la décote (R. 351-27, I, 2°, LEGIARTI000024113020 : « la durée séparant
l'âge auquel leur pension prend effet de leur soixante-cinquième anniversaire,
s'ils remplissent les conditions prévues [...] au III ou IV de l'article 20 ») et
la majoration de durée (R. 351-7, LEGIARTI000024113035) : l'âge que rend
``liquider.decote_opposable``. Hors de la dérogation, l'âge de la génération,
tel que la Cnav le publie (exposé « Taux de la retraite personnelle », version du
29 juillet 2026) : « 1953 66 ans et 2 mois », « à partir de 1955 67 ans », «  du
01/07/1951 au 31/12/1951 65 ans et 4 mois ».
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import pont
from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.droit import categories
from retraite_notionnelle.simulateur import Simulateur

#: Le IV de l'article 20 : « fixé à soixante-cinq ans ».
DEROGATION = 65.0
#: L'âge du taux plein que la Cnav publie pour chaque génération. La table du
#: modèle l'écrit à deux décimales (66,17 pour 1953) : les âges se comparent au
#: centième.
AGE_DE_1951_SECOND_SEMESTRE = 65 + 4 / 12
AGE_DE_1953 = 66 + 2 / 12
AGE_DE_1955_ET_APRES = 67.0


def _emploi(annee: int, trimestres: int = 4, revenu: float = 20_000.0) -> AnneeCarriere:
    return AnneeCarriere(annee=annee, revenu=revenu, trimestres_valides=trimestres,
                         affiliation="salarie_prive_non_cadre")


def _sans_emploi(annee: int, nature: str, avpf: float = 0.0) -> AnneeCarriere:
    """Une année que la carrière valide sans cotisation de l'assuré : quatre
    trimestres, de l'AVPF quand ``avpf`` porte son salaire forfaitaire."""
    return AnneeCarriere(annee=annee, revenu=0.0, trimestres_valides=4,
                         affiliation="salarie_prive_non_cadre", type_periode=nature,
                         cotisations_versees=False, revenu_avpf=avpf)


def _carriere(cle: str, naissance=(1953, 3), enfants: int = 3,
              naissances=("1980-04", "1984-05", "1986-06"), debut: int = 1973,
              sans=(), autres: dict | None = None, age: float = 65.0) -> Carriere:
    """Une assurée née le 15 du mois dit, au travail chaque année de ``debut`` à
    celle qui précède son départ, sauf les années ``sans`` ligne et celles que
    ``autres`` décrit."""
    annee, mois = naissance
    autres = autres or {}
    lignes = [autres[an] if an in autres else _emploi(an)
              for an in range(debut, annee + int(age)) if an not in sans]
    return Carriere(annee_naissance=annee, mois_naissance=mois, jour_naissance=15,
                    sexe="F", age_liquidation=age, nombre_enfants=enfants,
                    naissances_enfants=tuple(naissances), identifiant=cle, lignes=lignes)


def _chomage_avant_l_activite(naissance_du_premier: str) -> dict:
    """Un trimestre d'emploi en 1972, le chômage indemnisé en 1973, l'emploi en
    1974 et 1975, aucune ligne de 1976 à 1978 : les deux années qui précèdent
    une naissance de 1975 valident huit trimestres, chômage compris, mais
    l'activité ne compte que les trimestres cotisés (circulaire n° 2014-64,
    point 2.2.3 : « sont exclusivement retenues [...] les périodes de salariat
    ayant donné lieu à cotisations »)."""
    return {"naissances": (naissance_du_premier, "1980-04", "1982-04"), "debut": 1972,
            "sans": (1976, 1977, 1978),
            "autres": {1972: _emploi(1972, trimestres=1, revenu=2_000.0),
                       1973: _sans_emploi(1973, "chomage_indemnise")}}


#: Chaque carrière, et l'âge du 1° de L. 351-8 qu'elle reçoit au régime général,
#: à sa date d'effet. Les calculs, posés à la main, sont dans la note
#: docs/feuille_de_route/175/2026-11-03-taux-plein-parents-de-trois-enfants.md.
CAS = {
    # Aucune ligne de 1980 à 1982 : 0 trimestre dans la fenêtre de l'enfant né en
    # avril 1980 (1980, 1981, 1982), 8 en 1978 et 1979, 28 d'activité avant.
    "interrompue trois ans": ({"sans": (1980, 1981, 1982)}, DEROGATION),
    # Les trimestres de l'AVPF ne comptent pas dans la fenêtre (L. 381-1).
    "à l'AVPF trois ans": ({"autres": {an: _sans_emploi(an, "education_enfant", 12_000.0)
                                       for an in (1980, 1981, 1982)}}, DEROGATION),
    # Ni ceux de la pension d'invalidité (R. 351-12, 3°).
    "en invalidité trois ans": ({"autres": {an: _sans_emploi(an, "invalidite")
                                            for an in (1980, 1981, 1982)}}, DEROGATION),
    # L'arrêt maladie, période assimilée, compte : 12 trimestres, plus de huit.
    "en arrêt maladie trois ans": ({"autres": {an: _sans_emploi(an, "maladie")
                                               for an in (1980, 1981, 1982)}}, AGE_DE_1953),
    # Au travail chaque année : 12 trimestres dans chaque fenêtre.
    "sans interruption": ({}, AGE_DE_1953),
    # « au moins trois enfants ».
    "deux enfants": ({"enfants": 2, "naissances": ("1980-04", "1984-05"),
                      "sans": (1980, 1981, 1982)}, AGE_DE_1953),
    # Sans naissance dite, aucune fenêtre ne se date.
    "naissances non dites": ({"naissances": (), "sans": (1980, 1981, 1982)}, AGE_DE_1953),
    # Dite à l'année, la naissance ouvre le droit quand les deux fenêtres le
    # donnent : 1980-1982, 0 trimestre ; 1981-1983, 4.
    "à l'année, les deux fenêtres": ({"naissances": ("1980", "1984", "1986"),
                                      "sans": (1980, 1981, 1982)}, DEROGATION),
    # Seule 1983 sans ligne : née en septembre 1980, la fenêtre est 1981-1983,
    # 4 + 4 + 0 = 8 trimestres, au plus huit.
    "septembre, 1983 seule": ({"naissances": ("1980-09", "1984-05", "1986-06"),
                               "sans": (1983,)}, DEROGATION),
    # Née en mars, la fenêtre est 1980-1982 : 12 trimestres.
    "mars, 1983 seule": ({"naissances": ("1980-03", "1984-05", "1986-06"),
                          "sans": (1983,)}, AGE_DE_1953),
    # Dite à l'année, la fenêtre du premier semestre ne le donne pas.
    "à l'année, 1983 seule": ({"naissances": ("1980", "1984", "1986"),
                               "sans": (1983,)}, AGE_DE_1953),
    # Né en novembre 1975 : 1 + 0 + 4 + 3 (les trois trimestres civils
    # d'avant celui de la naissance) = 8 trimestres d'activité.
    "chômage, novembre": (_chomage_avant_l_activite("1975-11"), DEROGATION),
    # Né en septembre 1975 : 1 + 0 + 4 + 2 = 7 trimestres d'activité.
    "chômage, septembre": (_chomage_avant_l_activite("1975-09"), AGE_DE_1953),
    # Les bornes des générations : juillet 1951, décembre 1955, janvier 1956.
    "née en juillet 1951": ({"naissance": (1951, 7), "debut": 1971,
                             "naissances": ("1978-04", "1982-05", "1984-06"),
                             "sans": (1978, 1979, 1980)}, DEROGATION),
    "née en juillet 1951, sans interruption": (
        {"naissance": (1951, 7), "debut": 1971,
         "naissances": ("1978-04", "1982-05", "1984-06")}, AGE_DE_1951_SECOND_SEMESTRE),
    "née en décembre 1955": ({"naissance": (1955, 12), "debut": 1975,
                              "naissances": ("1982-04", "1986-05", "1988-06"),
                              "sans": (1982, 1983, 1984)}, DEROGATION),
    "née en janvier 1956": ({"naissance": (1956, 1), "debut": 1976,
                             "naissances": ("1983-04", "1987-05", "1989-06"),
                             "sans": (1983, 1984, 1985)}, AGE_DE_1955_ET_APRES),
}


def test_la_fiche_date_l_age_du_parent_de_trois_enfants():
    """Les pensions prenant effet à compter du 1er juillet 2011 (loi
    n° 2010-1330, article 118, II) ; abrogé pour celles qui prennent effet à
    compter du 1er janvier 2026 (loi n° 2025-199, article 87, IV et VIII, A)."""
    fiches = Simulateur().scenario_actuel.fiches_datees
    nom = categories.FICHE_DES_SOIXANTE_CINQ_ANS
    assert not fiches.regle(nom, "2011-06-01")["existe"]
    regle = fiches.regle(nom, "2011-07-01")
    # « applicable dans tous les régimes obligatoires de retraite auxquels
    # s'appliquent les dispositions de l'article L. 351-8 » : les cultes
    # (L. 382-27), et les points d'avant 1973 des artisans et des commerçants,
    # que le décret n° 73-937, article 3, II, minore jusqu'au soixante-cinquième
    # anniversaire de qui remplit « les conditions prévues [...] aux III ou IV
    # de l'article 20 ».
    assert regle["age"] == 65 and regle["regimes"] == [
        "regime_general", "msa_salaries", "rsi", "cavimac", "cancava_avant_1973",
        "organic_avant_1973"]
    assert regle["parents_de_trois_enfants"] == {
        "nes_du": [1951, 7], "nes_au": [1955, 12], "enfants": 3,
        "apres_au_plus": 8, "avant_au_moins": 8, "activite_au_moins": 8}
    # Les fonctionnaires : loi n° 2010-1330, article 28, III, et R. 26 ter, I —
    # « au moins une année » d'interruption, dans un congé ou une disponibilité
    # de R. 13, 1° ; « huit trimestres » avant, deux fois. Le congé de maternité
    # en est, mais ne dure pas une année : seule l'année « élever un enfant »,
    # qui dit le congé parental ou la disponibilité, la compte entière.
    assert regle["fonctionnaires"] == {
        "regimes": ["fonction_publique_etat", "cnracl", "fspoeie"],
        "interruptions": ["education_enfant"],
        "interruption_au_moins_annees": 1, "avant_au_moins": 8, "activite_au_moins": 8}
    assert fiches.regle(nom, "2025-12-01")["parents_de_trois_enfants"]["enfants"] == 3
    assert not fiches.regle(nom, "2026-01-01")["existe"]


def test_l_age_du_taux_plein_du_parent_de_trois_enfants():
    """L'âge d'annulation de la décote au régime général, dans les deux moteurs :
    le portage le rend, le jumeau Python le refait (``droit_et_refait``)."""
    from outils_pont import droit_et_refait

    appels, attendus = {}, {}
    for cle, (champs, age) in CAS.items():
        carriere = _carriere(cle, **champs)
        appels[cle] = ("liquider.decote_opposable", pont.MOTEUR,
                       pont.Periode("regime_general", carriere.annee_liquidation),
                       carriere, carriere.annee_liquidation)
        attendus[cle] = age
    lus, refus = droit_et_refait(appels)
    assert refus == {}, refus
    obtenus = {cle: lu[1] for cle, lu in lus.items()}
    assert obtenus == {cle: pytest.approx(age, abs=0.005) for cle, age in attendus.items()}


#: Les régimes où vaut le même âge, et le texte qui l'y porte.
ALIGNES = {
    # Les salariés agricoles, les artisans et les commerçants : la note
    # docs/feuille_de_route/175/2026-11-03-taux-plein-parents-de-trois-enfants.md.
    "msa_salaries": DEROGATION, "rsi": DEROGATION,
    # L. 382-27 (LEGIARTI000019959668) : « une pension de vieillesse dans les
    # conditions définies aux articles [...] L. 351-8 à L. 351-13 ».
    "cavimac": DEROGATION,
    # Décret n° 73-937, article 3, II (LEGIARTI000026474703, puis
    # LEGIARTI000047634732) : la minoration se compte « de leur
    # soixante-cinquième anniversaire s'ils remplissent les conditions prévues
    # [...] aux III ou IV de l'article 20 de la loi n° 2010-1330 ».
    "cancava_avant_1973": DEROGATION, "organic_avant_1973": DEROGATION,
}


def test_les_regimes_alignes_suivent():
    """Le même âge aux salariés agricoles, aux artisans et commerçants, aux
    cultes et aux points d'avant 1973 des artisans et des commerçants, à qui
    s'applique L. 351-8 (« Le présent article est applicable dans tous les
    régimes obligatoires de retraite auxquels s'appliquent les dispositions de
    l'article L. 351-8 »). Les complémentaires que le modèle ne sert pas encore :
    ``ENCORE_A_L_AGE_DE_LA_GENERATION``."""
    from outils_pont import droit_et_refait

    carriere = _carriere("interrompue trois ans", sans=(1980, 1981, 1982))
    annee = carriere.annee_liquidation
    appels = {regime: ("liquider.decote_opposable", pont.MOTEUR,
                       pont.Periode(regime, annee), carriere, annee)
              for regime in ALIGNES}
    lus, refus = droit_et_refait(appels)
    assert refus == {}, refus
    assert {regime: lu[1] for regime, lu in lus.items()} == ALIGNES


#: Une assurée née le 15 mars 1953, au travail dès dix-huit ans, sans activité
#: de 1976 à 1999 — une durée bien en deçà des 165 trimestres de sa génération —,
#: trois enfants nés en avril 1976, juin 1978 et juin 1980.
REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "18", "emploi": "cor_2026",
    "enfants": "3", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "1976:1999:sans_activite", "naissance": "1953-03-15",
    "naissances": "1976-04, 1978-06, 1980-06", "primes": "0", "profil": "plat",
    "projection": "cor_reference", "salaire": "1", "sexe": "F",
    "statut": "salarie_prive_non_cadre", "stock": "prix", "table": "unisexe",
}


@pytest.mark.parametrize("age, enfants, taux", [
    # À 65 ans, le taux plein ; sans la dérogation, la décote des cinq
    # trimestres qui la séparent de 66 ans et 2 mois (14 mois, au trimestre
    # supérieur), à 1,25 % chacun pour l'assurée née après 1952 (R. 351-27, II) :
    # 50 % × (1 − 5 × 1,25 %) = 46,875 %.
    ("65", "3", "taux 50.000%"), ("65", "2", "taux 46.875%"),
    # À 64 ans, quatre trimestres jusqu'à son soixante-cinquième anniversaire,
    # au lieu de neuf jusqu'à 66 ans et 2 mois (26 mois) : 50 % × (1 − 4 ×
    # 1,25 %) = 47,5 %, au lieu de 50 % × (1 − 9 × 1,25 %) = 44,375 %.
    ("64", "3", "taux 47.500%"), ("64", "2", "taux 44.375%"),
])
def test_la_pension_du_regime_general_de_bout_en_bout(age, enfants, taux):
    """Le simulateur, de la requête à la pension, dans les deux moteurs
    (``servi_et_refait``)."""
    from outils_pont import servi_et_refait

    naissances = REQUETE["naissances"] if enfants == "3" else "1976-04, 1978-06"
    requete = {**REQUETE, "liquidation": age, "enfants": enfants, "naissances": naissances}
    servis, refus = servi_et_refait([{"cle": "assurée", "requete": requete}])
    assert refus == {}, refus
    general = [p for p in servis["assurée"]["actuel"]["pensions_par_regime"]
               if p["regime"] == "regime_general"]
    assert len(general) == 1 and taux in general[0]["detail"], general


#: La même assurée, née le 15 septembre 1954 : sans activité de 1977 à 1999,
#: l'enfant d'avril 1977 ouvre le droit ; partie à 65 ans le 1er octobre 2019.
NEE_EN_1954 = {"naissance": "1954-09-15", "interruptions": "1977:1999:sans_activite",
               "naissances": "1977-04, 1979-06, 1981-06"}
#: Née le 15 mars 1955 : sans activité de 1978 à 2002, l'enfant d'avril 1978
#: ouvre le droit ; partie à 65 ans en 2020.
NEE_EN_1955 = {"naissance": "1955-03-15", "interruptions": "1978:2002:sans_activite",
               "naissances": "1978-04, 1980-06, 1982-06"}
#: Une ministre du culte, au culte dès 1979 : 8 trimestres cotisés en 1980 et
#: 1981, aucun de 1982 à 1984, l'enfant d'avril 1982 ouvre le droit.
MINISTRE_DU_CULTE = {"statut": "ministre_du_culte", "debut": "26",
                     "interruptions": "1982:1999:sans_activite",
                     "naissances": "1982-04, 1984-06, 1986-06"}

#: LA PENSION DES CULTES. Les ministres des cultes « reçoivent une pension de
#: vieillesse dans les conditions définies aux articles [...] L. 351-8 à
#: L. 351-13 » (L. 382-27, LEGIARTI000019959668), et le IV de l'article 20 y
#: vaut. Ses deux fractions (décret n° 2006-1325, article 2, LEGIARTI000023397816,
#: pour les pensions prenant effet à compter du 1er juillet 2011) :
#:
#: * celle d'après 1997, au taux de L. 351-1 et R. 351-27, que le I, 2°, minore
#:   jusqu'au « soixante-cinquième anniversaire » de ces parents ;
#: * celle d'avant 1998, la pension de D. 721-6 du code de 1985 (« fixé à
#:   soixante-cinq ans », LEGIARTI000006738898) : le maximum de pension « réduit
#:   au prorata du rapport entre sa durée d'assurance et cette durée maximale »
#:   de R. 351-6 (III), 165 trimestres pour la génération 1953 (décret
#:   n° 2010-1734, article 9) ; avant l'âge, « le coefficient de minoration fixé
#:   au 2° du I et au II de l'article R. 351-27 » (II) ; et, à qui remplit « les
#:   conditions prévues à l'article D. 721-6 », une majoration de « 100 % de
#:   l'écart pour les assurés nés après 1942 » entre le maximum et le minimum de
#:   L. 351-10, « au prorata du nombre de trimestres cotisés par l'assuré entre le
#:   1er janvier 1979 et le 31 décembre 1997 », rapporté à la même durée (V). Le
#:   minimum, 7 615,94 € par an depuis le 1er octobre 2017 (barème de la Cnav
#:   « Montant minimum de la retraite personnelle », lu le 3 novembre 2026),
#:   majoré à 8 322,13 € pour qui totalise « au moins 120 trimestres cotisés tous
#:   régimes », comme la caisse l'écrit (fiche ``cultes_fractions_de_pension``).
#:   Le maximum se retranche de la majoration : la fraction vaut le minimum au
#:   prorata, quel que soit le maximum de l'année.
#:
#: La carrière ne laisse au droit rien à trancher sur l'activité : née le 15
#: mars 1953, salariée de 1971 à 1975, sans activité de 1976 à 1979, ministre du
#: culte de 1980 à 1987 et de 2005 à 2017 ; enfants d'avril 1976, juin 1978 et
#: juin 1980 ; partie à 65 ans, effet le 1er avril 2018. L'enfant de 1976 ouvre
#: le droit par son salariat : 8 trimestres cotisés en 1974 et 1975, aucun de
#: 1976 à 1978, 20 d'activité avant. Elle valide 20 + 32 + 52 = 104 trimestres,
#: 32 cotisés de 1979 à 1997, 104 cotisés en tout, moins de 120.
CULTES_DE_BOUT_EN_BOUT = {
    # Trois enfants : le taux plein à 65 ans, aux deux régimes ; avant 1998,
    # 7 615,94 × 32 / 165 = 1 477,03 €, sans décote.
    "trois enfants": (("1976-04", "1978-06", "1980-06"), "taux 50.000%", "1,477.03", False),
    # LE CAS TÉMOIN, deux enfants : 5 trimestres jusqu'à 66 ans et 2 mois (13
    # mois et 14 jours, au trimestre supérieur), moins que ceux qui lui manquent
    # pour la durée ; 50 % × (1 − 5 × 1,25 %) = 46,875 %. Sa fraction d'avant 1998
    # sous « décote 0.9375 », sans majoration, est la lecture du modèle, que la
    # caisse décrit (« une décote qui sera appliquée sur le taux retenu pour le
    # calcul de ces deux fractions ») et que la fiche ``cultes_fractions_de_pension``
    # déclare : D. 721-6 du code de 1985 alloue cette fraction à soixante-cinq ans.
    "deux enfants": (("1976-04", "1978-06"), "taux 46.875%", None, True),
}


def _ministre_du_culte(cle: str, naissances: tuple, cultes=(), salariat=(),
                       ) -> Carriere:
    """Née le 15 mars 1953, partie à 65 ans : salariée les années ``salariat``,
    ministre du culte les années ``cultes``, sans activité les autres."""
    lignes = [_emploi(an) if an in salariat else AnneeCarriere(
        annee=an, revenu=20_000.0, trimestres_valides=4, affiliation="ministre_du_culte")
        for an in range(1971, 2018) if an in salariat or an in cultes]
    return Carriere(annee_naissance=1953, mois_naissance=3, jour_naissance=15, sexe="F",
                    age_liquidation=65.0, nombre_enfants=len(naissances),
                    naissances_enfants=naissances, identifiant=cle, lignes=lignes)


def _avant_1998(detail: str) -> str:
    """La fraction d'avant 1998 que le détail de la pension des cultes écrit."""
    return detail[detail.index("avant 1998"):]


def test_la_pension_des_cultes_de_bout_en_bout():
    """La pension de la ministre du culte, dans les deux moteurs
    (``droit_et_refait``) : ses deux fractions au taux plein à soixante-cinq ans,
    celle d'avant 1998 majorée jusqu'au minimum ; le parent de deux enfants
    garde la décote."""
    import re

    from outils_pont import droit_et_refait

    cultes = (*range(1980, 1988), *range(2005, 2018))
    appels = {cle: ("scenario_actuel.calculer", pont.MOTEUR, _ministre_du_culte(
        cle, naissances, cultes=cultes, salariat=range(1971, 1976)))
        for cle, (naissances, _, _, _) in CULTES_DE_BOUT_EN_BOUT.items()}
    lus, refus = droit_et_refait(appels)
    assert refus == {}, refus
    for cle, (_, taux, avant_1998, decote) in CULTES_DE_BOUT_EN_BOUT.items():
        pensions = {p["regime"]: p["detail"] for p in lus[cle]["pensions_par_regime"]}
        assert taux in pensions["regime_general"] and taux in pensions["cavimac"], pensions
        fraction = _avant_1998(pensions["cavimac"])
        assert ("décote 0.9375" in fraction) is decote, fraction
        if avant_1998 is not None:
            assert re.search(r"\+ [\d,.]+ € pour 32 trimestres cotisés de 1979 à 1997 "
                             r"\(minimum contributif\) = " + re.escape(avant_1998) + " €",
                             fraction), fraction


def test_les_annees_cultuelles_d_avant_1979_ne_sont_pas_cotisees():
    """Les deux années qui précèdent la naissance ne comptent que « les trimestres
    validés en contrepartie de cotisations à la charge de l'assuré » ou de la
    maladie, de la maternité, du chômage, de la formation (décret n° 2011-620,
    article 2, 1°). L'activité cultuelle d'avant 1979, D. 721-11 du code de 1985
    la prend en compte (LEGIARTI000006739120 : « sont prises en compte pour
    l'ouverture du droit et le calcul de la pension, les périodes d'exercice
    d'activités [...] accomplies antérieurement au 1er janvier 1979 »), et la
    CAVIMAC en dit les trimestres « validés à titre gratuit » (sa page
    « Demander ma retraite de base », lue le 5 novembre 2026) ; le Gouvernement, des « années
    antérieures à 1979, qui n'ont donné lieu à aucune cotisation et ont été
    validées gratuitement » (JO Sénat du 16 janvier 2008, p. 207, question
    orale n° 122) ; les cotisations de 1979 et après sont, pour leur part, « à
    la charge des assurés » (L. 382-25, I, 1°, LEGIARTI000006742803).
    Ministre du culte de 1973, sans activité ensuite jusqu'en 1999 ; enfants
    d'avril 1980, juin 1984 et juin 1986 : pour
    celui de 1980, 1978 ne compte pas, 1979 donne 4 trimestres, moins de 8 ; pour
    les deux autres, aucun trimestre les deux années d'avant : l'âge de la
    génération, 66 ans et 2 mois. Le témoin, au culte jusqu'en 1980, enfants
    d'avril 1981, juin 1984 et juin 1986 : 1979 et 1980, 8 trimestres cotisés ;
    1981 à 1983, aucun ; 8 cotisés d'activité avant, l'activité cultuelle
    comptée comme l'emploi (``NON_TRANCHE_CULTES``) : 65 ans, aux deux régimes."""
    from outils_pont import droit_et_refait

    cas = {
        "enfant de 1980": (_ministre_du_culte(
            "enfant de 1980", ("1980-04", "1984-06", "1986-06"),
            cultes=(*range(1973, 1980), *range(2000, 2018))), AGE_DE_1953),
        "enfant de 1981": (_ministre_du_culte(
            "enfant de 1981", ("1981-04", "1984-06", "1986-06"),
            cultes=(*range(1973, 1981), *range(2000, 2018))), DEROGATION),
    }
    appels = {f"{cle}|{regime}": ("liquider.decote_opposable", pont.MOTEUR,
                                  pont.Periode(regime, carriere.annee_liquidation),
                                  carriere, carriere.annee_liquidation)
              for cle, (carriere, _) in cas.items() for regime in ("cavimac", "regime_general")}
    lus, refus = droit_et_refait(appels)
    assert refus == {}, refus
    assert {cle: lu[1] for cle, lu in lus.items()} == {
        f"{cle}|{regime}": pytest.approx(age, abs=0.005)
        for cle, (_, age) in cas.items() for regime in ("cavimac", "regime_general")}


#: LES POINTS D'AVANT 1973 DES ARTISANS ET DES COMMERÇANTS (décret n° 73-937,
#: article 3, II, LEGIARTI000026474703, du 7 octobre 2012 au 1er septembre
#: 2023) : un coefficient de minoration « fonction soit du nombre de trimestres
#: manquant à la date d'effet de leur pension par rapport à la limite prévue au
#: I, soit de leur soixante-cinquième anniversaire s'ils remplissent les
#: conditions prévues [...] aux III ou IV de l'article 20 [...] ou, dans le cas
#: contraire, de l'âge prévu au 1° de l'article L. 351-8 », « Le plus petit de
#: ces deux nombres », « 1,25 % pour l'assuré né après 1952 ». L'assurée de
#: ``REQUETE``, artisane ou commerçante dès dix-huit ans, partie à 65 ans le 1er
#: avril 2018 : 0 trimestre jusqu'à son soixante-cinquième anniversaire, aucun
#: coefficient ; le cas témoin, deux enfants, 5 trimestres jusqu'à 66 ans et 2
#: mois, moins que ceux qui lui manquent pour la durée : 1 − 5 × 1,25 % = 0,9375.
AVANT_1973 = {
    "artisane": ({"statut": "artisan"}, {"cancava_avant_1973": None}),
    "commerçante": ({"statut": "commercant"}, {"organic_avant_1973": None}),
    "artisane, deux enfants": ({"statut": "artisan", "enfants": "2",
                                "naissances": "1976-04, 1978-06"},
                               {"cancava_avant_1973": 0.9375}),
}


def test_les_points_d_avant_1973_sans_minoration():
    """Les points d'avant 1973, de la requête à la pension, dans les deux
    moteurs (``servi_et_refait``)."""
    assert _coefficients_servis(AVANT_1973) == {
        cle: attendus for cle, (_, attendus) in AVANT_1973.items()}


#: CE QUE LES TEXTES NE TRANCHENT PAS : l'activité cultuelle est-elle l'«
#: activité professionnelle » du 2° et du 3° du IV (« Avoir validé [...] un
#: nombre de trimestres minimum à raison de l'exercice d'une activité
#: professionnelle ») ? Le code n'en dit que des « activités mentionnées à
#: l'article L. 382-15 » (L. 382-27), le décret n° 2011-620 et la circulaire
#: Cnav n° 2014-64 ne nomment pas les cultes, la CAVIMAC ne publie rien de la
#: mesure. Le modèle la compte comme l'emploi, déclaré à la fiche : la ministre
#: du culte de 1979 de la saisie (``MINISTRE_DU_CULTE``), ses 11 trimestres
#: cultuels de 1979 à 1981 pour activité, a le taux plein à 65 ans ; avant 1998,
#: 7 615,94 × 11 / 165 = 507,73 € (le maximum, 4 635,65 € × 11/165 = 309,04 €,
#: et 198,69 € de majoration).
NON_TRANCHE_CULTES = {"taux": "taux 50.000%", "avant 1998": "= 507.73 €"}


def test_l_activite_cultuelle_compte_comme_l_emploi():
    """Le point que les textes ne tranchent pas, dans les deux moteurs
    (``servi_et_refait``), déclaré à la fiche."""
    from outils_pont import servi_et_refait

    servis, refus = servi_et_refait([{"cle": "ministre", "requete": {
        **REQUETE, "liquidation": "65", **MINISTRE_DU_CULTE}}])
    assert refus == {}, refus
    detail = next(p["detail"] for p in servis["ministre"]["actuel"]["pensions_par_regime"]
                  if p["regime"] == "cavimac")
    assert NON_TRANCHE_CULTES["taux"] in detail, detail
    fraction = _avant_1998(detail)
    assert NON_TRANCHE_CULTES["avant 1998"] in fraction and "décote" not in fraction, detail

#: Les régimes où le moteur lit encore l'âge de la génération, celui d'où se
#: comptent leur décote ou leur coefficient : pour l'assurée « interrompue
#: trois ans » de 2018, 66 ans et 2 mois au lieu de 65 ans — chaque fois un écart
#: déclaré, sauf à l'Arrco, qui sert ces parents sans abattement dès soixante-cinq
#: ans (``test_l_agirc_arrco_sert_ces_parents_sans_abattement``) : l'âge d'où elle
#: compte leur coefficient avant soixante-cinq ans, et celui des points de la
#: tranche C d'avant 2016, les textes lus ne le tranchent pas, et le modèle garde
#: celui de la génération (``NON_TRANCHE``). Le RCI (règlement, article 12 :
#: 0,95 au lieu de 1) s'y tient, par l'âge, à l'abri du paquet : sa pension de
#: bout en bout passe par le RCO des artisans, que le paquet de main peut servir
#: en retard sur le jumeau. La CAVIMAC et les points d'avant 1973, écarts
#: déclarés jusqu'au 3 novembre 2026, sont servis : ``ALIGNES``.
ENCORE_A_L_AGE_DE_LA_GENERATION = ("arrco", "rci")

#: Ce que la fiche doit dire de chaque écart, dans une approximation de la
#: version de 2011 : le régime, ses textes, mot pour mot, et la valeur que le
#: modèle sert encore.
DECLARATIONS = {
    "Agirc-Arrco": ("accord du 18 mars 2011, article 1er", "article 2 ter", "article 84",
                    "avant soixante-cinq ans", "tranche C", "0,91"),
    "fonctionnaires": ("article 28, III", "R. 26 ter", "article 65-3", "article 50-3",
                       "R. 13, 2°", "temps partiel", "70,3125 %",
                       # Le congé de maternité, qui ne dure pas une année ;
                       # l'AVPF d'un relevé ; l'année d'une période saisie au
                       # mois ; les neuf ans de L. 18, III.
                       "L. 331-3", "L. 381-1", "plus de la moitié", "L. 18, III"),
    # Ce que les textes ne tranchent pas aux cultes.
    "CAVIMAC": ("L. 382-27", "L. 382-15", "activité professionnelle", "D. 721-11"),
    "RCI": ("article 12", "sans aucun abattement", "0,95"),
}


def test_ailleurs_le_moteur_lit_encore_l_age_de_la_generation():
    """L'âge d'où se comptent la décote ou le coefficient, dans les deux moteurs
    (``droit_et_refait``) : celui de la génération, là où le droit dit
    soixante-cinq ans — un écart déclaré, en attendant le calcul."""
    from outils_pont import droit_et_refait

    carriere = _carriere("interrompue trois ans", sans=(1980, 1981, 1982))
    annee = carriere.annee_liquidation
    appels = {regime: ("liquider.decote_opposable", pont.MOTEUR,
                       pont.Periode(regime, annee), carriere, annee)
              for regime in ENCORE_A_L_AGE_DE_LA_GENERATION}
    lus, refus = droit_et_refait(appels)
    assert refus == {}, refus
    assert {regime: lu[1] for regime, lu in lus.items()} == {
        regime: pytest.approx(AGE_DE_1953, abs=0.005)
        for regime in ENCORE_A_L_AGE_DE_LA_GENERATION}


def test_la_fiche_declare_chaque_ecart():
    """Chaque écart a son approximation dans la version de 2011 : le régime, ses
    textes cités, la valeur que le modèle sert encore, ou ce que les textes ne
    tranchent pas. L'Agirc-Arrco n'y est plus donnée pour garder l'âge de la
    génération : ses deux accords servent ces parents sans abattement."""
    from retraite_notionnelle.noyau import carte

    fiche = carte.fiches()[categories.FICHE_DES_SOIXANTE_CINQ_ANS]
    approximations = [" ".join(str(a.get(champ) or "") for champ in ("textes", "ecart", "effet"))
                      for a in fiche.get("approximations") or []
                      if "loi_du_9_novembre_2010" in (a.get("version") or [])]
    manquent = {regime: [mot for mot in mots
                         if not any(regime in a and mot in a for a in approximations)]
                for regime, mots in DECLARATIONS.items()}
    assert manquent == {regime: [] for regime in DECLARATIONS}
    assert not any("garde l'âge de sa génération" in a for a in approximations)


#: L'AGIRC-ARRCO SERT CES PARENTS SANS ABATTEMENT dès qu'ils ont, à soixante-cinq
#: ans, le taux plein du régime général. De 2011 à 2018 : « Les participants aux
#: régimes AGIRC et ARRCO qui justifient avoir, avant l'âge fixé au 1° de
#: l'article L. 351-8 [...], fait liquider, leur pension d'assurance vieillesse, à
#: taux plein, auprès du régime général [...] en application des III et IV de
#: l'article 20 de la loi n° 2010-1330 [...] (aidants familiaux, assurés
#: handicapés, parents d'enfant handicapé et parents de 3 enfants sous certaines
#: conditions) ; pourront faire liquider leurs allocations AGIRC et/ou ARRCO, sans
#: abattement, sur les tranches A et B des rémunérations » (accord du 18 mars
#: 2011, article 1er), « à l'âge de 65 ans » (convention du 14 mars 1947, annexe
#: V, et accord du 8 décembre 1961, annexe E, article 2 ter). Depuis 2019 : « sans
#: application des coefficients viagers [...] à l'âge auquel il a obtenu la
#: pension d'assurance vieillesse du régime général [...] à taux plein » (accord
#: du 17 novembre 2017, article 84, 3), que l'article 98 leur reconnaît dès
#: soixante-cinq ans (sa note 1 : « d'assurés nés entre le 1er juillet 1951 et le
#: 31 décembre 1955 parents d'au moins trois enfants »). Chaque cas est une
#: requête de ``REQUETE``, partie à 65 ans, sauf ce qu'il change ; la valeur
#: attendue est le coefficient que la formule de chaque régime affiche, ``None``
#: quand elle n'en affiche aucun. Les calculs, posés à la main, sont dans la note
#: docs/feuille_de_route/175/2026-11-03-agirc-arrco-des-parents-de-trois-enfants.md.
SANS_ABATTEMENT = {
    # Née le 15 mars 1953, effet le 1er avril 2018 : sans abattement, au lieu de
    # 0,95 (5 trimestres jusqu'à 66 ans et 2 mois, « moins 1 an 1 trimestre »).
    "Arrco, 2018": ({}, {"arrco": None, "arrco_tranche_2": None}),
    # Née le 15 septembre 1954, effet le 1er octobre 2019 : au lieu de 0,93.
    "Agirc-Arrco, 2019": (NEE_EN_1954, {"agirc_arrco": None, "arrco": None,
                                        "arrco_tranche_2": None}),
    # Née le 15 mars 1955, effet le 1er avril 2020 : au lieu de 0,92.
    "Agirc-Arrco, 2020": (NEE_EN_1955, {"agirc_arrco": None, "arrco": None,
                                        "arrco_tranche_2": None}),
    # LE CAS TÉMOIN : deux enfants, ni le taux plein du régime général à
    # soixante-cinq ans (« taux 46.875% »), ni l'exonération : 5 trimestres
    # jusqu'à 66 ans et 2 mois, 0,95, comme avant.
    "deux enfants, 2018": ({"enfants": "2", "naissances": "1976-04, 1978-06"},
                           {"arrco": 0.95, "arrco_tranche_2": 0.95}),
}

#: CE QUE LES TEXTES NE TRANCHENT PAS : partie avant soixante-cinq ans, sans le
#: taux plein du régime général, de quel âge l'Agirc-Arrco compte le coefficient
#: de ces parents. L'accord du 18 mars 2011 fige l'âge de la retraite « dans les
#: rédactions respectives des articles L. 351-8, 1°, et L. 161-17-2 [...] en
#: vigueur à la date du présent accord », et ne les sert sans abattement qu'« à
#: l'âge de 65 ans » (article 2 ter des annexes V et E) ; l'accord de 2017
#: compte le coefficient de « cet âge », celui du 1° de L. 351-8 (article 84, 2),
#: que le IV de l'article 20 fixe pour eux à soixante-cinq ans, quand la
#: circulaire 2020-02-DRJ dit soixante-sept ans « pour les participants nés à
#: compter du 1er janvier 1955 », sans nommer la dérogation. Le modèle garde
#: l'âge de la génération, déclaré : partie à 64 ans le 1er avril 2017, 25 mois
#: et demi jusqu'à 66 ans et 2 mois, 9 trimestres, « moins 2 ans 1 trimestre »,
#: 0,91 ; compté de 65 ans, 11 mois et demi, 4 trimestres, « moins 1 an », 0,96.
NON_TRANCHE = {
    "à 64 ans, 2017": ({"liquidation": "64"}, {"arrco": 0.91, "arrco_tranche_2": 0.91}),
}


def _coefficients_servis(cas: dict) -> dict[str, dict[str, float | None]]:
    """Le coefficient d'anticipation que la formule de chaque régime de ``cas``
    affiche, dans les deux moteurs (``servi_et_refait``)."""
    import re

    from outils_pont import servi_et_refait

    servis, refus = servi_et_refait(
        [{"cle": cle, "requete": {**REQUETE, "liquidation": "65", **champs}}
         for cle, (champs, _) in cas.items()])
    assert refus == {}, refus
    lus = {}
    for cle, (_, attendus) in cas.items():
        lus[cle] = {}
        for pension in servis[cle]["actuel"]["pensions_par_regime"]:
            if pension["regime"] in attendus:
                trouve = re.search(r"coefficient d'anticipation ([0-9.]+)", pension["detail"])
                lus[cle][pension["regime"]] = float(trouve.group(1)) if trouve else None
    return lus


def test_l_agirc_arrco_sert_ces_parents_sans_abattement():
    """À soixante-cinq ans, l'Arrco de 2018 et l'Agirc-Arrco de 2019 et de 2020
    sans coefficient ; le parent de deux enfants garde le sien."""
    assert _coefficients_servis(SANS_ABATTEMENT) == {
        cle: attendus for cle, (_, attendus) in SANS_ABATTEMENT.items()}


def test_avant_soixante_cinq_ans_l_age_de_la_generation_reste():
    """Le point que les textes ne tranchent pas : le modèle compte encore le
    coefficient de l'âge de la génération, déclaré à la fiche."""
    assert _coefficients_servis(NON_TRANCHE) == {
        cle: attendus for cle, (_, attendus) in NON_TRANCHE.items()}


def test_la_tranche_c_d_avant_2016_garde_son_coefficient():
    """La cadre de ``REQUETE``, à huit fois le salaire moyen : ses points de
    l'Arrco sans abattement, ceux de l'Agirc aussi, sauf ceux de la tranche C
    acquis jusqu'en 2015, que l'accord n'exonère pas (« sans abattement, sur
    les tranches A et B des rémunérations » ; annexe V de 1947 : « Cette annexe
    n'est pas applicable aux droits constitués jusqu'au 31 décembre 2015 sur la
    tranche C des rémunérations ») : ils gardent le coefficient de l'âge, 0,95
    (5 trimestres jusqu'à 66 ans et 2 mois, « moins 1 an 1 trimestre »). Le
    coefficient affiché de l'Agirc est la moyenne des deux, pondérée par les
    points : 1 − 0,05 × points de la tranche C / points."""
    import re

    from outils_pont import servi_et_refait

    requete = {**REQUETE, "liquidation": "65", "statut": "salarie_prive_cadre", "salaire": "8"}
    servis, refus = servi_et_refait([{"cle": "cadre", "requete": requete}])
    assert refus == {}, refus
    details = {p["regime"]: p["detail"] for p in servis["cadre"]["actuel"]["pensions_par_regime"]}
    assert "coefficient d'anticipation" not in details["arrco"], details["arrco"]
    trouve = re.search(
        r"([0-9,.]+) points × valeur de service [0-9.]+ € × coefficient d'anticipation "
        r"([0-9.]+), dont ([0-9,.]+) points de la tranche C d'avant 2016 au coefficient "
        r"pour âge 0\.9500", details["agirc"])
    assert trouve is not None, details["agirc"]
    points, coefficient, tranche_c = (float(trouve.group(rang).replace(",", ""))
                                      for rang in (1, 2, 3))
    assert 0 < tranche_c < points
    assert coefficient == pytest.approx(1 - 0.05 * tranche_c / points, abs=1e-4)


#: LES FONCTIONNAIRES SÉDENTAIRES. « Pour les fonctionnaires nés entre le 1er
#: juillet 1951 et le 31 décembre 1955 dont la limite d'âge était fixée à
#: soixante-cinq ans avant l'entrée en vigueur de la présente loi et qui
#: remplissent les conditions prévues aux 1° à 3° du IV de l'article 20, l'âge
#: auquel s'annule le coefficient de minoration prévu à l'article L. 14 du code
#: des pensions civiles et militaires de retraite ne peut être supérieur à
#: soixante-cinq ans, par dérogation au III de l'article 66 de la loi n° 2003-775
#: du 21 août 2003 » (loi n° 2010-1330, article 28, III, LEGIARTI000025014566,
#: pour les pensions prenant effet à compter du 1er juillet 2011, article 118,
#: II) ; la même règle à la CNRACL (décret n° 2003-1306, article 65-3,
#: LEGIARTI000024113270) et aux ouvriers de l'État (décret n° 2004-1056, article
#: 50-3, LEGIARTI000024113274), « Les modalités d'application du présent article
#: sont celles prévues pour les fonctionnaires de l'Etat à l'article R. 26 ter ».
#: R. 26 ter, I (LEGIARTI000024111781) : une interruption « pendant une durée
#: d'au moins une année » dans l'année de la naissance et les deux suivantes, ou
#: les trois suivantes pour l'enfant né au second semestre, « dans le cadre des
#: congés ou de la disponibilité mentionnés au 1° de l'article R. 13 » — le congé
#: de maternité, d'adoption, parental, de présence parentale, la disponibilité
#: pour élever un enfant de moins de huit ans (LEGIARTI000023449727) : les années
#: que la saisie dit « élever un enfant » ; une année « congé de maternité » n'en
#: prouve pas une d'interruption, le congé durant seize semaines, vingt-six à
#: partir du troisième enfant, trente-quatre ou quarante-six pour des naissances
#: multiples (code de la sécurité sociale, L. 331-3, LEGIARTI000006742545, et
#: L. 331-4, LEGIARTI000006742550, auxquels renvoient les statuts des trois
#: régimes, « d'une durée égale à celle prévue par la législation sur la
#: sécurité sociale » ; pour la salariée, au code du travail, L. 122-26,
#: quatorze semaines jusqu'au 30 septembre 1978, LEGIARTI000006646773, seize dès
#: le 1er octobre, LEGIARTI000006646774) — ; « au
#: titre des deux années précédant l'année de la naissance [...], d'une durée
#: d'assurance, telle que définie à l'article L. 14, égale ou supérieure à huit
#: trimestres » ; et huit trimestres de durée d'assurance « à raison de
#: l'exercice d'une activité professionnelle, préalablement à l'interruption ».
#:
#: Hors de la dérogation, l'âge du tableau de l'article 66, III, de la loi
#: n° 2003-775 (LEGIARTI000006758610), lu à l'« Année au cours de laquelle sont
#: réunies les conditions mentionnées au I et au II de l'article L. 24 » — l'âge
#: d'ouverture de L. 161-17-2 (décret n° 2011-2103, article 1er : « 1954 61 ans
#: et 7 mois », « A compter de 1955 62 ans ») — : « Limite d'âge moins 3
#: trimestres » en 2017, « moins 4 » en 2016, « moins 2 » en 2018, « moins 6 » en
#: 2014 ; la limite d'âge, soixante-sept ans dès 1955 (article 28, I), soixante-six
#: ans et sept mois en 1954, et deux mois en 1953 (article 28, II ; décret
#: n° 2011-2103, article 8 : « cinq mois par génération »). Les calculs, posés à
#: la main, sont dans la note
#: docs/feuille_de_route/175/2026-11-03-taux-plein-parents-de-trois-enfants-fonctionnaires.md.

#: Née en 1955 : soixante-deux ans en 2017, 67 ans moins 3 trimestres.
AGE_FP_DE_1955 = 67 - 3 / 4
#: Née en septembre 1954 : 61 ans et 7 mois en avril 2016, 66 ans et 7 mois
#: moins 4 trimestres.
AGE_FP_DE_1954 = 66 + 7 / 12 - 1
#: Née en mars 1953 : 61 ans et 2 mois en mai 2014, 66 ans et 2 mois moins 6
#: trimestres : sous soixante-cinq ans, la dérogation n'y change rien.
AGE_FP_DE_1953 = 66 + 2 / 12 - 6 / 4
#: Née en janvier 1956 : soixante-deux ans en 2018, 67 ans moins 2 trimestres.
AGE_FP_DE_1956 = 67 - 2 / 4


def _fonctionnaire(cle: str, naissance=(1955, 3), affiliation: str = "fonctionnaire_etat",
                   enfants: int = 3, naissances=("1978-04", "1980-06", "1982-06"),
                   conges: dict | None = None, debut: int = 1973, reprise: int = 2003,
                   autres: dict | None = None) -> Carriere:
    """Une fonctionnaire née le 15 du mois dit, en service de ``debut`` à 1977 et
    de ``reprise`` à l'année qui précède ses soixante-cinq ans ; de 1978 à
    ``reprise`` − 1, aucune ligne, sauf les années de ``conges`` — un motif
    d'interruption de la saisie par année — et celles qu'``autres`` décrit."""
    annee, mois = naissance
    conges = conges or {}
    autres = autres or {}
    lignes = []
    for an in range(debut, annee + 65):
        if an in autres:
            lignes.append(autres[an])
        elif an in conges:
            lignes.append(AnneeCarriere(annee=an, revenu=0.0, trimestres_valides=4,
                                        affiliation=affiliation, type_periode=conges[an],
                                        cotisations_versees=False))
        elif an < 1978 or an >= reprise:
            lignes.append(AnneeCarriere(annee=an, revenu=20_000.0, trimestres_valides=4,
                                        affiliation=affiliation))
    return Carriere(annee_naissance=annee, mois_naissance=mois, jour_naissance=15,
                    sexe="F", age_liquidation=65.0, nombre_enfants=enfants,
                    naissances_enfants=tuple(naissances), identifiant=cle, lignes=lignes)


def _trois_ans(motif: str = "education_enfant", depuis: int = 1978) -> dict:
    return {an: motif for an in range(depuis, depuis + 3)}


#: Chaque carrière de fonctionnaire de l'État, et l'âge d'annulation de sa décote
#: à soixante-cinq ans. Sauf mention : née le 15 mars 1955, en service de 1973 à
#: 1977 et de 2003 à 2019, enfants d'avril 1978, juin 1980 et juin 1982, effet le
#: 1er avril 2020.
CAS_FONCTIONNAIRES = {
    # Fenêtre de l'enfant d'avril 1978 : 1978-1980, trois années de congé, au
    # moins une ; 1976 et 1977 : 8 trimestres ; 1973-1977 : 20 d'activité avant.
    "trois ans à élever un enfant": ({"conges": _trois_ans()}, DEROGATION),
    # Une année suffit : 1980, dans la fenêtre 1978-1980.
    "un an, 1980": ({"conges": {1980: "education_enfant"}}, DEROGATION),
    # Le congé de maternité est un congé de R. 13, 1°, a, mais R. 26 ter veut
    # « une durée d'au moins une année » : en avril 1978, quatorze semaines
    # pour la salariée (L. 122-26, rédaction de 1973), seize dès le 1er octobre
    # 1978 ; au code de la sécurité sociale, de seize à quarante-six depuis
    # (L. 331-3 et L. 331-4) ; l'année que la saisie
    # dit « congé de maternité » n'en prouve pas une.
    "un an de maternité, 1978": ({"conges": {1978: "maternite"}}, AGE_FP_DE_1955),
    # Le congé de maternité suivi d'un congé parental ou d'une disponibilité :
    # 1979, « élever un enfant », dans la fenêtre 1978-1980 ; 8 trimestres en
    # 1976 et 1977 ; 20 d'activité avant 1979.
    "maternité en 1978, puis un an à élever un enfant": (
        {"conges": {1978: "maternite", 1979: "education_enfant"}}, DEROGATION),
    # Aucune année de congé ni de disponibilité : la saisie ne dit pas pourquoi
    # elle a cessé, et R. 26 ter le demande.
    "sans activité": ({}, AGE_FP_DE_1955),
    # Née en mars 1978 : fenêtre 1978-1980, sans congé ; l'enfant de juin 1980
    # (fenêtre 1980-1982, 1981) n'a aucun trimestre en 1978 et 1979 ; celui de
    # juin 1982, aucun congé de 1982 à 1984.
    "mars 1978, congé en 1981": ({"naissances": ("1978-03", "1980-06", "1982-06"),
                                  "conges": {1981: "education_enfant"}}, AGE_FP_DE_1955),
    # Née en septembre 1978 : fenêtre 1979-1981, 1981 y est ; 8 trimestres en
    # 1976 et 1977 ; 20 d'activité avant 1981.
    "septembre 1978, congé en 1981": ({"naissances": ("1978-09", "1980-06", "1982-06"),
                                       "conges": {1981: "education_enfant"}}, DEROGATION),
    # Dite à l'année, la naissance de 1978 ouvre le droit si les deux fenêtres
    # le donnent : 1978-1980 et 1979-1981 contiennent 1979.
    "à l'année, congé en 1979": ({"naissances": ("1978", "1980", "1982"),
                                  "conges": {1979: "education_enfant"}}, DEROGATION),
    # 1981 n'est pas dans 1978-1980 ; « 1980 » : aucun trimestre en 1978 et
    # 1979 ; « 1982 » : aucun congé de 1982 à 1985.
    "à l'année, congé en 1981": ({"naissances": ("1978", "1980", "1982"),
                                  "conges": {1981: "education_enfant"}}, AGE_FP_DE_1955),
    # Au service en 1976 et 1977 seulement : 8 trimestres d'activité avant 1978,
    # « fixé à huit trimestres ».
    "huit trimestres d'activité": ({"debut": 1976, "conges": _trois_ans()}, DEROGATION),
    # Au chômage indemnisé en 1976 : les deux années d'avant valident 8
    # trimestres de durée d'assurance, mais l'activité n'en compte que 4 ;
    # l'enfant de juin 1980 (congé en 1980) n'en a que 4 d'activité avant 1980.
    "quatre trimestres d'activité": (
        {"debut": 1976, "conges": _trois_ans(),
         "autres": {1976: AnneeCarriere(annee=1976, revenu=0.0, trimestres_valides=4,
                                        affiliation="salarie_prive_non_cadre",
                                        type_periode="chomage_indemnise",
                                        cotisations_versees=False)}}, AGE_FP_DE_1955),
    # « au moins trois enfants ».
    "deux enfants": ({"enfants": 2, "naissances": ("1978-04", "1980-06"),
                      "conges": _trois_ans()}, AGE_FP_DE_1955),
    # Sans naissance dite, aucune fenêtre ne se date.
    "naissances non dites": ({"naissances": (), "conges": _trois_ans()}, AGE_FP_DE_1955),
    # Née en septembre 1954, effet le 1er octobre 2019.
    "née en septembre 1954": ({"naissance": (1954, 9), "conges": _trois_ans()}, DEROGATION),
    "née en septembre 1954, sans activité": ({"naissance": (1954, 9)}, AGE_FP_DE_1954),
    # Née en mars 1953 : l'âge du tableau est déjà sous soixante-cinq ans.
    "née en mars 1953": ({"naissance": (1953, 3), "conges": _trois_ans()}, AGE_FP_DE_1953),
    # Née en décembre 1955 : soixante-deux ans en décembre 2017.
    "née en décembre 1955": ({"naissance": (1955, 12), "debut": 1974,
                              "conges": _trois_ans()}, DEROGATION),
    # Née en janvier 1956 : hors des générations.
    "née en janvier 1956": ({"naissance": (1956, 1), "debut": 1974,
                             "naissances": ("1979-04", "1981-06", "1983-06"),
                             "conges": _trois_ans(depuis=1979), "reprise": 2004},
                            AGE_FP_DE_1956),
}


def test_l_age_d_annulation_du_fonctionnaire_parent_de_trois_enfants():
    """L'âge d'annulation de la décote de la fonctionnaire de l'État, dans les
    deux moteurs (``droit_et_refait``)."""
    from outils_pont import droit_et_refait

    appels, attendus = {}, {}
    for cle, (champs, age) in CAS_FONCTIONNAIRES.items():
        carriere = _fonctionnaire(cle, **champs)
        appels[cle] = ("liquider.decote_opposable", pont.MOTEUR,
                       pont.Periode("fonction_publique_etat", carriere.annee_liquidation),
                       carriere, carriere.annee_liquidation)
        attendus[cle] = age
    lus, refus = droit_et_refait(appels)
    assert refus == {}, refus
    obtenus = {cle: lu[1] for cle, lu in lus.items()}
    assert obtenus == {cle: pytest.approx(age, abs=0.005) for cle, age in attendus.items()}


#: Les trois régimes du code des pensions et de ses décrets, et le statut qui y
#: affilie : la règle est la même (articles 65-3 et 50-3).
REGIMES_DES_FONCTIONNAIRES = {"fonction_publique_etat": "fonctionnaire_etat",
                              "cnracl": "fonctionnaire_territorial_hospitalier",
                              "fspoeie": "ouvrier_etat"}


def test_la_cnracl_et_les_ouvriers_de_l_etat_suivent():
    """Le même âge à la CNRACL et aux ouvriers de l'État ; l'emploi classé en
    catégorie active, dont la limite d'âge n'était pas de soixante-cinq ans,
    garde le sien, celui du parent de deux enfants."""
    from outils_pont import droit_et_refait

    appels = {}
    for regime, statut in REGIMES_DES_FONCTIONNAIRES.items():
        for enfants, naissances in ((3, ("1978-04", "1980-06", "1982-06")),
                                    (2, ("1978-04", "1980-06"))):
            carriere = _fonctionnaire(f"{regime} {enfants}", affiliation=statut,
                                      enfants=enfants, naissances=naissances,
                                      conges=_trois_ans())
            appels[f"{regime}, {enfants}"] = (
                "liquider.decote_opposable", pont.MOTEUR,
                pont.Periode(regime, carriere.annee_liquidation), carriere,
                carriere.annee_liquidation)
    for enfants, naissances in ((3, ("1978-04", "1980-06", "1982-06")),
                                (2, ("1978-04", "1980-06"))):
        carriere = _fonctionnaire(f"active {enfants}",
                                  affiliation="fonctionnaire_territorial_hospitalier_actif",
                                  enfants=enfants, naissances=naissances,
                                  conges=_trois_ans())
        appels[f"active, {enfants}"] = (
            "liquider.decote_opposable", pont.MOTEUR,
            pont.Periode("cnracl", carriere.annee_liquidation), carriere,
            carriere.annee_liquidation)
    lus, refus = droit_et_refait(appels)
    assert refus == {}, refus
    ages = {cle: lu[1] for cle, lu in lus.items()}
    assert {cle: age for cle, age in ages.items() if not cle.startswith("active")} == {
        f"{regime}, {enfants}": pytest.approx(
            DEROGATION if enfants == 3 else AGE_FP_DE_1955, abs=0.005)
        for regime in REGIMES_DES_FONCTIONNAIRES for enfants in (3, 2)}
    assert ages["active, 3"] == ages["active, 2"] < DEROGATION


#: De bout en bout : la fonctionnaire de ``NEE_EN_1955``, ses trois premières
#: années sans activité dites « élever un enfant » ; partie à soixante-cinq ans,
#: le 1er avril 2020, au taux plein de L. 13, 75 %, au lieu de 75 % × (1 − 5 ×
#: 1,25 %) = 70,3125 % ; partie à soixante-quatre ans, le 1er avril 2019, 4
#: trimestres jusqu'à soixante-cinq ans, 75 % × (1 − 4 × 1,25 %) = 71,25 %, au
#: lieu de 9 jusqu'à 66 ans et 3 mois (vingt-sept mois), 75 % × (1 − 9 × 1,25 %)
#: = 66,5625 %.
CONGES_DE_1978_A_1980 = {**NEE_EN_1955,
                         "interruptions": "1978:1980:education_enfant, 1981:2002:sans_activite"}
BOUT_EN_BOUT = {
    "État, 65 ans": ({**CONGES_DE_1978_A_1980, "statut": "fonctionnaire_etat"},
                     "fonction_publique_etat", 75.0),
    "CNRACL, 65 ans": ({**CONGES_DE_1978_A_1980,
                        "statut": "fonctionnaire_territorial_hospitalier"}, "cnracl", 75.0),
    "ouvrière de l'État, 65 ans": ({**CONGES_DE_1978_A_1980, "statut": "ouvrier_etat"},
                                   "fspoeie", 75.0),
    "État, 64 ans": ({**CONGES_DE_1978_A_1980, "statut": "fonctionnaire_etat",
                      "liquidation": "64"}, "fonction_publique_etat", 71.25),
    # LES CAS TÉMOINS : deux enfants ; ou trois, sans dire pourquoi elle a cessé.
    "État, deux enfants, 65 ans": ({**CONGES_DE_1978_A_1980, "statut": "fonctionnaire_etat",
                                    "enfants": "2", "naissances": "1978-04, 1980-06"},
                                   "fonction_publique_etat", 70.3125),
    "État, deux enfants, 64 ans": ({**CONGES_DE_1978_A_1980, "statut": "fonctionnaire_etat",
                                    "enfants": "2", "naissances": "1978-04, 1980-06",
                                    "liquidation": "64"}, "fonction_publique_etat", 66.5625),
    "État, sans activité, 65 ans": ({**NEE_EN_1955, "statut": "fonctionnaire_etat"},
                                    "fonction_publique_etat", 70.3125),
    # Une seule année dite « congé de maternité » : elle ne prouve pas l'année
    # d'interruption de R. 26 ter ; 66 ans et 3 mois, 5 trimestres.
    "État, un an de maternité, 65 ans": (
        {**NEE_EN_1955, "statut": "fonctionnaire_etat",
         "interruptions": "1978:1978:maternite, 1979:2002:sans_activite"},
        "fonction_publique_etat", 70.3125),
}


def test_la_pension_du_fonctionnaire_de_bout_en_bout():
    """Le simulateur, de la requête au taux de la pension, dans les deux moteurs
    (``servi_et_refait``) : le taux que la formule affiche, au millième."""
    import re

    from outils_pont import servi_et_refait

    servis, refus = servi_et_refait(
        [{"cle": cle, "requete": {**REQUETE, "liquidation": "65", **champs}}
         for cle, (champs, _, _) in BOUT_EN_BOUT.items()])
    assert refus == {}, refus
    taux = {}
    for cle, (_, regime, _) in BOUT_EN_BOUT.items():
        details = [p["detail"] for p in servis[cle]["actuel"]["pensions_par_regime"]
                   if p["regime"] == regime]
        trouve = re.search(r"taux ([0-9.]+)%", details[0]) if len(details) == 1 else None
        taux[cle] = float(trouve.group(1)) if trouve else details
    assert taux == {cle: pytest.approx(attendu, abs=0.0006)
                    for cle, (_, _, attendu) in BOUT_EN_BOUT.items()}


def test_le_minimum_garanti_s_ouvre_a_soixante_cinq_ans():
    """Le minimum garanti est dû « si l'intéressé a atteint l'âge [...] auquel
    s'annule le coefficient de minoration prévu aux I et II de l'article L. 14 »
    (L. 17, LEGIARTI000023033916) : l'âge que l'article 28, III, borne à
    soixante-cinq ans. La fonctionnaire de ``CONGES_DE_1978_A_1980`` au tiers du
    salaire moyen, partie à soixante-cinq ans : avec trois enfants, sa pension est
    portée au minimum ; avec deux, ni sa durée (108 trimestres sur 166) ni l'âge
    d'annulation de sa génération (66 ans et 3 mois) ne l'ouvrent, et le décret
    n° 2010-1744, article 3, ne minore cet âge que pour qui atteint l'âge
    d'ouverture de 2011 à 2015, elle en 2017. Dans les deux moteurs
    (``servi_et_refait``)."""
    from outils_pont import servi_et_refait

    cas = {"trois enfants": ("3", "1978-04, 1980-06, 1982-06"),
           "deux enfants": ("2", "1978-04, 1980-06")}
    servis, refus = servi_et_refait(
        [{"cle": cle, "requete": {**REQUETE, **CONGES_DE_1978_A_1980, "liquidation": "65",
                                  "statut": "fonctionnaire_etat", "salaire": "0.3",
                                  "enfants": enfants, "naissances": naissances}}
         for cle, (enfants, naissances) in cas.items()])
    assert refus == {}, refus
    details = {cle: [p["detail"] for p in servis[cle]["actuel"]["pensions_par_regime"]
                     if p["regime"] == "fonction_publique_etat"]
               for cle in cas}
    assert {cle: "porté au minimum garanti" in detail[0] for cle, detail in details.items()} \
        == {"trois enfants": True, "deux enfants": False}, details
