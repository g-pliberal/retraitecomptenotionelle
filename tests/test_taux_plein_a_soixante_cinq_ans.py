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
    assert regle["age"] == 65 and regle["regimes"] == ["regime_general", "msa_salaries", "rsi"]
    assert regle["parents_de_trois_enfants"] == {
        "nes_du": [1951, 7], "nes_au": [1955, 12], "enfants": 3,
        "apres_au_plus": 8, "avant_au_moins": 8, "activite_au_moins": 8}
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


def test_les_regimes_alignes_suivent_les_complementaires_non():
    """Le même âge aux salariés agricoles et aux artisans et commerçants, à qui
    s'applique L. 351-8 (« Le présent article est applicable dans tous les
    régimes obligatoires de retraite auxquels s'appliquent les dispositions de
    l'article L. 351-8 ») ; l'Arrco, en 2018, garde l'âge de la génération, celui
    que la caisse a servi selon la fiche coefficients_anticipation_agirc_arrco
    (« l'âge de la retraite est celui du 1° de L. 351-8 [...] ; la caisse a servi
    celui de la loi du 21 décembre 2011 »)."""
    from outils_pont import droit_et_refait

    carriere = _carriere("interrompue trois ans", sans=(1980, 1981, 1982))
    annee = carriere.annee_liquidation
    appels = {regime: ("liquider.decote_opposable", pont.MOTEUR,
                       pont.Periode(regime, annee), carriere, annee)
              for regime in ("msa_salaries", "rsi", "arrco")}
    lus, refus = droit_et_refait(appels)
    assert refus == {}, refus
    assert {regime: lu[1] for regime, lu in lus.items()} == {
        "msa_salaries": DEROGATION, "rsi": DEROGATION,
        "arrco": pytest.approx(AGE_DE_1953, abs=0.005)}


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
