"""La pension d'aujourd'hui d'un retraité, et les deux cas types qui la tiennent.

Le simulateur montrait à qui est déjà parti sa pension du premier mois, ramenée
en euros d'aujourd'hui par l'indice des prix. Il montre désormais celle qu'il
touche, revalorisée comme le droit l'a fait (``retraite_notionnelle.revalorisation``).
Ce module tient trois choses :

* la SÉRIE — les coefficients que la Cnav publie depuis 1949, et ceux des
  pensions civiles et militaires de 2004 à 2008 — lue telle qu'elle est écrite ;
* les RÈGLES de chaque régime, une à une ;
* deux CAS TYPES. Le premier se refait à la main : un salarié non cadre parti
  en janvier 2012, dont la pension de départ est prise au modèle et menée à
  2026 par les quatorze coefficients du barème, recopiés ici un à un. Le
  second est un calcul fait par d'autres : le COR publie, pour un non-cadre et
  un cadre de quatre générations, l'évolution du pouvoir d'achat de leur
  pension nette depuis leur départ (rapport annuel de juin 2026, figure 3.14).
  Le dépôt la retrouve avec ses propres séries.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from retraite_notionnelle.config import Parametres, RevalorisationStock
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.revalorisation import (
    REGLE_FONCTION_PUBLIQUE,
    REGLE_GENERALE,
    REGLE_POINT,
    REGLE_REGIME_SPECIAL,
    RevalorisationsPensions,
)
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.simulateur import Simulateur

TEMOINS = Path(__file__).resolve().parent / "temoins"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def revalorisations() -> RevalorisationsPensions:
    return RevalorisationsPensions(RACINE_DONNEES)


def _retraite(simulateur, **options):
    """Une comparaison pour une carrière paramétrique, et sa pension d'aujourd'hui."""
    carriere = simulateur.carriere_simple(**options)
    return simulateur.simuler(carriere)


# -- la série ------------------------------------------------------------------


def test_la_serie_remonte_a_1949_et_s_arrete_au_coefficient_de_2026(revalorisations):
    """Première et dernière lignes du barème de la Cnav : le 1er janvier 1949,
    et le 1er janvier 2026 à 1,009 — le chiffre de la circulaire 2025/29, que
    le registre de veille porte déjà."""
    generales = revalorisations.generales
    assert generales[0].date_effet == date(1949, 1, 1)
    assert generales[-1].date_effet == date(2026, 1, 1)
    assert generales[-1].coefficient == 1.009
    assert all(1.0 <= r.coefficient <= 1.25 for r in generales)
    assert all(r.fiabilite == Fiabilite.HAUTE for r in generales)


def test_une_annee_sans_ligne_est_une_annee_sans_revalorisation(revalorisations):
    """Le gel de 2014, le 1,000 de 2016 et le report de 2018 au 1er janvier
    2019 : trois années sans date d'effet, et c'est ce que le droit a servi."""
    annees = {r.date_effet.year for r in revalorisations.generales}
    assert not {2014, 2016, 2018} & annees
    assert {2013, 2015, 2017, 2019} <= annees


def test_2020_porte_cinq_tranches_selon_la_pension_de_decembre_2019(revalorisations):
    """Loi n° 2019-1446, art. 81 : 1 % jusqu'à 2 000 € par mois, puis 0,8, 0,6
    et 0,4 % par marches de quelques euros, et 0,3 % au-delà de 2 014 €."""
    def coefficient_2020(mensuel):
        return revalorisations.generale(
            date(2019, 12, 31), date(2020, 12, 31), False, mensuel)[0]

    assert coefficient_2020(1500.0) == 1.01
    assert coefficient_2020(2000.0) == 1.01
    assert coefficient_2020(2000.01) == 1.008
    assert coefficient_2020(2010.0) == 1.006
    assert coefficient_2020(2014.0) == 1.004
    assert coefficient_2020(2014.01) == 1.003
    assert coefficient_2020(9000.0) == 1.003
    with pytest.raises(ValueError):
        revalorisations.generale(date(2019, 12, 31), date(2020, 12, 31), False, None)


def test_la_serie_des_pensions_recoupe_celle_des_salaires_la_ou_le_droit_les_confond(
        simulateur, revalorisations):
    """Depuis 2021, la même instruction fixe le coefficient des pensions servies
    et celui des salaires portés au compte : les deux séries, lues dans deux
    publications différentes de la caisse, doivent donner le même nombre. En
    2019 et en 2020, les lois de financement n'ont limité que les PENSIONS — à
    0,3 % —, et les deux séries s'écartent, comme elles le doivent."""
    colonne = next(table for annee, mois, table
                   in simulateur.macro.revalorisation_portee_au_compte
                   if (annee, mois) == (2026, 1))
    pensions = {r.date_effet: r.coefficient for r in revalorisations.generales
                if not r.par_tranche}
    for annee in (2021, 2022, 2024, 2025, 2026):
        salaires = colonne[annee - 1] / colonne[annee] if annee < 2026 else colonne[2025]
        # La table des salaires est arrondie à trois décimales : un millième
        # et demi d'écart est l'arrondi, pas un désaccord.
        assert pensions[date(annee, 1, 1)] == pytest.approx(salaires, abs=1.5e-3), annee
    assert colonne[2018] / colonne[2019] > pensions[date(2019, 1, 1)] + 0.01


def test_la_fonction_publique_ne_s_ecarte_du_regime_general_qu_en_2004(revalorisations):
    """1,5 % par décret au 1er janvier 2004, là où le régime général recevait
    1,7 % ; les quatre années suivantes, les décrets et l'arrêté disent le même
    nombre, et c'est ce qui autorise à ne tenir qu'une série après 2008."""
    generales = {r.date_effet: r.coefficient for r in revalorisations.generales
                 if not r.par_tranche}
    publiques = {r.date_effet: r.coefficient for r in revalorisations.fonction_publique}
    assert publiques[date(2004, 1, 1)] == 1.015
    assert generales[date(2004, 1, 1)] == 1.017
    for effet, coefficient in publiques.items():
        if effet.year > 2004:
            assert generales[effet] == coefficient, effet
    assert all(r.fiabilite == Fiabilite.CERTIFIEE for r in revalorisations.fonction_publique)


# -- les règles ------------------------------------------------------------------


def test_qui_part_cette_annee_ou_plus_tard_n_a_pas_de_pension_d_aujourd_hui(simulateur):
    """La pension du départ est alors la seule qu'il y ait à dire."""
    for age in (64, 67):
        comparaison = _retraite(simulateur, annee_naissance=1962, sexe="H",
                                affiliation="salarie_prive_non_cadre",
                                age_debut=20, age_liquidation=age)
        assert comparaison.carriere.annee_liquidation >= 2026
        assert comparaison.aujourd_hui is None


def test_la_revalorisation_du_jour_du_depart_n_est_pas_servie_au_regime_general(
        simulateur):
    """Une pension du régime général prenant effet le 1er janvier 2019 est
    calculée sur des salaires déjà revalorisés ce jour-là : elle ne reçoit pas
    en plus les 0,3 % du 1er janvier 2019. Sa première revalorisation est celle
    de 2020."""
    comparaison = _retraite(simulateur, annee_naissance=1957, sexe="H",
                            affiliation="salarie_prive_non_cadre",
                            age_debut=20, age_liquidation=62)
    assert str(comparaison.carriere.date_liquidation) == "janvier 2019"
    base = next(r for r in comparaison.aujourd_hui.actuel.regimes
                if r.regime == "regime_general")
    attendu = 1.01 * 1.004 * 1.011 * 1.04 * 1.008 * 1.053 * 1.022 * 1.009
    assert base.regle == REGLE_GENERALE
    assert base.coefficient == pytest.approx(attendu, rel=1e-12)


def test_la_fonction_publique_suit_le_point_d_indice_jusqu_en_2003(simulateur):
    """Un fonctionnaire parti en 1998 a vu sa pension suivre le traitement de
    son indice jusqu'au 31 décembre 2003, puis 1,5 % au 1er janvier 2004, puis
    les décrets et l'article L. 161-23-1. Les tableaux d'assimilation ne sont
    pas suivis, et la fiabilité le dit."""
    comparaison = _retraite(simulateur, annee_naissance=1938, sexe="H",
                            affiliation="fonctionnaire_etat",
                            age_debut=22, age_liquidation=60)
    etat = next(r for r in comparaison.aujourd_hui.actuel.regimes
                if r.regime == "fonction_publique_etat")
    revalorisations = simulateur.revalorisations
    perequation = 52.4933 / 49.6481  # point au 1er janvier 2003 / 1998
    decrets = 1.015 * 1.02 * 1.018 * 1.018 * 1.011 * 1.008
    generale = revalorisations.generale(date(2009, 1, 1), date(2026, 12, 31), True,
                                        comparaison.aujourd_hui.actuel.mensuel_decembre_2019)[0]
    assert etat.regle == REGLE_FONCTION_PUBLIQUE
    assert etat.coefficient == pytest.approx(perequation * decrets * generale, rel=1e-12)
    assert etat.fiabilite == Fiabilite.MOYENNE


def test_un_regime_special_parti_avant_2009_est_estime(simulateur):
    """Avant les décrets de 2008, la pension d'un cheminot suivait les
    salaires de ses collègues en activité, qu'aucune série ne donne."""
    comparaison = _retraite(simulateur, annee_naissance=1955, sexe="H",
                            affiliation="agent_sncf", age_debut=20, age_liquidation=52)
    sncf = next(r for r in comparaison.aujourd_hui.actuel.regimes if r.regime == "sncf")
    assert sncf.regle == REGLE_REGIME_SPECIAL
    assert sncf.fiabilite == Fiabilite.ESTIMEE


def test_les_points_d_avant_1999_changent_d_echelle_avec_l_arrco(simulateur):
    """Un point Arrco servi en 1990 est un point de l'ancienne unité : au
    1er janvier 1999 il en est devenu 0,387464 de la nouvelle. Sa pension de
    2026 est ce nombre de points nouveaux à la valeur de 2026."""
    comparaison = _retraite(simulateur, annee_naissance=1925, sexe="H",
                            affiliation="salarie_prive_cadre",
                            age_debut=20, age_liquidation=65, niveau_salaire=2.0)
    arrco = next(r for r in comparaison.aujourd_hui.actuel.regimes if r.regime == "arrco")
    valeur_1990 = simulateur.scenario_actuel.valeur_du_point("arrco", 1990)[0]
    assert arrco.regle == REGLE_POINT
    assert arrco.coefficient == pytest.approx(0.387464 * 1.4386 / valeur_1990, rel=1e-12)


def test_la_tranche_de_2020_suit_la_retraite_de_decembre_2019(simulateur):
    """Une petite retraite reçoit 1 % en 2020, une grosse 0,3 % : le même
    salarié non cadre, à deux niveaux de salaire, n'a pas le même coefficient."""
    petite, grosse = (
        _retraite(simulateur, annee_naissance=1950, sexe="H",
                  affiliation="salarie_prive_cadre", age_debut=22,
                  age_liquidation=62, niveau_salaire=niveau)
        for niveau in (0.6, 3.0)
    )
    assert petite.aujourd_hui.actuel.mensuel_decembre_2019 <= 2000.0
    assert grosse.aujourd_hui.actuel.mensuel_decembre_2019 > 2014.0

    def base(comparaison):
        return next(r.coefficient for r in comparaison.aujourd_hui.actuel.regimes
                    if r.regime == "regime_general")

    assert base(petite) / base(grosse) == pytest.approx(1.01 / 1.003, rel=1e-12)


def test_les_systemes_prospectifs_sont_le_systeme_1_pour_qui_etait_deja_parti(simulateur):
    """Qui a liquidé avant la bascule garde sa pension : elle a reçu les
    mêmes revalorisations que celle du système 1, au centime."""
    comparaison = _retraite(simulateur, annee_naissance=1950, sexe="H",
                            affiliation="salarie_prive_non_cadre",
                            age_debut=20, age_liquidation=62, niveau_salaire=0.8)
    aujourd_hui = comparaison.aujourd_hui
    for cle in ("notionnel_prospectif", "notionnel_prospectif_employeur"):
        assert aujourd_hui.notionnels[cle] == aujourd_hui.actuel.pension_annuelle


def test_les_systemes_retroactifs_suivent_la_regle_de_la_page_cout(simulateur):
    """La pension notionnelle servie suit la règle que la page Coût lui prête :
    le compte jusqu'à la bascule, puis la règle du stock."""
    comparaison = _retraite(simulateur, annee_naissance=1950, sexe="H",
                            affiliation="salarie_prive_non_cadre",
                            age_debut=20, age_liquidation=62, niveau_salaire=0.8)
    reel = simulateur.revalorisation_servie.coefficient_stock(2012, 2026, False)
    prix = simulateur.macro.coefficient_prix(2012, 2026)
    retro = comparaison.notionnel_retroactif.pension_annuelle
    assert comparaison.aujourd_hui.notionnels["notionnel_retroactif"] == pytest.approx(
        retro * prix * reel, rel=1e-12)
    assert comparaison.aujourd_hui.coefficients_notionnels["notionnel_retroactif"] == reel


def test_la_garantie_vieillesse_se_calcule_aujourd_hui(simulateur):
    """Une retraitée partie à 62 ans en 2020 a 68 ans : la garantie lui est
    ouverte, et elle regarde sa pension d'aujourd'hui, pas celle de ses 65 ans."""
    comparaison = _retraite(simulateur, annee_naissance=1958, sexe="F",
                            affiliation="salarie_prive_non_cadre", age_debut=20,
                            age_liquidation=62, niveau_salaire=0.3, nombre_enfants=3)
    aujourd_hui = comparaison.aujourd_hui
    plancher = (800.0 + 250.0) * 12.0
    assert aujourd_hui.garantie_vieillesse > 0
    assert aujourd_hui.notionnels["notionnel_liberal"] + aujourd_hui.rente_capitalisee == (
        pytest.approx(plancher, rel=1e-12))


def test_le_stock_reindexe_suit_la_regle_du_compte_au_dela_de_la_bascule():
    """Sous la variante ``reindexe``, une bascule passée — 2020 — fait suivre
    au stock la règle du compte de 2021 à aujourd'hui, prospectif compris."""
    simulateur = Simulateur(Parametres(annee_bascule=2020,
                                       revalorisation_stock=RevalorisationStock.REINDEXE))
    comparaison = _retraite(simulateur, annee_naissance=1950, sexe="H",
                            affiliation="salarie_prive_non_cadre",
                            age_debut=20, age_liquidation=62, niveau_salaire=0.8)
    reel = simulateur.revalorisation_servie.coefficient(2020, 2026)
    assert reel != 1.0
    jusqu_bascule = comparaison.aujourd_hui.notionnels["notionnel_prospectif"] / (
        simulateur.macro.coefficient_prix(2020, 2026) * reel)
    assert jusqu_bascule < comparaison.aujourd_hui.actuel.pension_annuelle


# -- le cas type refait à la main ----------------------------------------------

#: Les revalorisations du régime général reçues par une pension prenant effet
#: le 1er janvier 2012, recopiées du barème « Coefficients de revalorisation
#: des retraites » de la Cnav. Celle de 2020 est celle des retraites qui ne
#: dépassaient pas 2 000 € par mois en décembre 2019.
REVALORISATIONS_DEPUIS_2012 = (
    ("2012-04-01", 1.021), ("2013-04-01", 1.013), ("2015-10-01", 1.001),
    ("2017-10-01", 1.008), ("2019-01-01", 1.003), ("2020-01-01", 1.010),
    ("2021-01-01", 1.004), ("2022-01-01", 1.011), ("2022-07-01", 1.040),
    ("2023-01-01", 1.008), ("2024-01-01", 1.053), ("2025-01-01", 1.022),
    ("2026-01-01", 1.009),
)

#: Valeur de service du point Arrco au 31 décembre 2012 — celle qui a servi la
#: pension de départ dans le modèle —, et du point Agirc-Arrco en 2026, gelé
#: depuis le 1er novembre 2024.
POINT_ARRCO_2012 = 1.2414
POINT_AGIRC_ARRCO_2026 = 1.4386


def test_le_cas_type_d_un_retraite_se_refait_a_la_main(simulateur):
    """Un salarié non cadre né en janvier 1950, au travail de 20 à 62 ans,
    parti en janvier 2012 — et sa pension de 2026, refaite sans le moteur.

    La pension de DÉPART est celle du modèle, que d'autres tests confrontent
    à OpenFisca et aux exemples des caisses. Tout ce qui suit se refait ici :
    la base multipliée par les treize revalorisations du barème, la
    complémentaire convertie en points et servie à la valeur de 2026. Et la
    différence avec ce que la page affichait avant — la pension de départ
    ramenée en euros de 2026 par l'indice des prix — est ce que le retraité
    a perdu.
    """
    comparaison = _retraite(simulateur, annee_naissance=1950, sexe="H",
                            affiliation="salarie_prive_non_cadre", age_debut=20,
                            age_liquidation=62, niveau_salaire=0.8)
    depart = {p.regime: p.montant for p in comparaison.actuel.pensions_par_regime}
    assert str(comparaison.carriere.date_liquidation) == "janvier 2012"
    assert set(depart) == {"regime_general", "arrco", "arrco_tranche_2"}
    assert depart["arrco_tranche_2"] == 0.0

    # Décembre 2019 choisit la tranche de 2020 : la base menée à fin 2019, la
    # complémentaire à la valeur du point de fin 2019.
    base_2019 = depart["regime_general"]
    for effet, coefficient in REVALORISATIONS_DEPUIS_2012:
        if effet < "2020":
            base_2019 *= coefficient
    arrco_2019 = depart["arrco"] / POINT_ARRCO_2012 * 1.2714
    assert (base_2019 + arrco_2019) / 12 <= 2000.0

    base = depart["regime_general"]
    for _, coefficient in REVALORISATIONS_DEPUIS_2012:
        base *= coefficient
    points = depart["arrco"] / POINT_ARRCO_2012
    complementaire = points * POINT_AGIRC_ARRCO_2026
    aujourd_hui = comparaison.aujourd_hui.actuel
    assert aujourd_hui.pension_annuelle == pytest.approx(base + complementaire, rel=1e-12)
    assert aujourd_hui.mensuel_decembre_2019 == pytest.approx(
        (base_2019 + arrco_2019) / 12, rel=1e-12)

    # Ce que la page affichait : la pension de départ ramenée en euros de 2026.
    # La vraie est plus petite, parce que ni la base ni la complémentaire n'ont
    # suivi les prix.
    affichee_avant = comparaison.en_euros_constants(comparaison.actuel.pension_annuelle)
    assert aujourd_hui.pension_annuelle < affichee_avant
    assert base < depart["regime_general"] * simulateur.macro.coefficient_prix(2012, 2026)
    assert complementaire < depart["arrco"] * simulateur.macro.coefficient_prix(2012, 2026)


def test_le_site_sert_le_cas_type_refait_a_la_main(simulateur):
    """Le même retraité, saisi sur le site : le témoin ``retraite_cas_type_2012``
    en porte la pension d'aujourd'hui, et le portage JavaScript y est tenu au
    milliardième (``tests/js/comparer.mjs``). Ce que la page affiche à ce
    retraité est donc le chiffre refait à la main ci-dessus."""
    temoin = json.loads((TEMOINS / "simulations.json").read_text(encoding="utf-8"))[
        "retraite_cas_type_2012"]["resultat"]["aujourd_hui"]["actuel"]
    comparaison = _retraite(simulateur, annee_naissance=1950, sexe="H",
                            affiliation="salarie_prive_non_cadre", age_debut=20,
                            age_liquidation=62, niveau_salaire=0.8)
    assert temoin["pension_annuelle"] == pytest.approx(
        comparaison.aujourd_hui.actuel.pension_annuelle, rel=1e-12)
    assert {r["regime"]: r["coefficient"] for r in temoin["par_regime"]} == pytest.approx(
        {r.regime: r.coefficient for r in comparaison.aujourd_hui.actuel.regimes}, rel=1e-12)


# -- le cas type du COR ---------------------------------------------------------


@pytest.fixture(scope="module")
def cor() -> dict:
    return json.loads((TEMOINS / "cor_pouvoir_achat_retraite.json").read_text(encoding="utf-8"))


#: Le mois où les complémentaires revalorisent leur point : le 1er avril
#: jusqu'en 2015, le 1er novembre depuis 2016. La série du dépôt porte la
#: valeur du 31 décembre ; le COR raisonne sur la pension de l'année.
def _mois_du_point(annee: int) -> int:
    return 4 if annee <= 2015 else 11


def _prelevements(cas_type: str, annee: int, part: str) -> float:
    """Les prélèvements sur la pension, sous les conventions du COR (annexe
    méthodologique, § 3.3) : CSG à 6,2 % puis 6,6 % depuis 2005 ; 8,3 %
    depuis 2018 pour le cadre, en 2018 seulement pour le non-cadre, qui
    retrouve le taux médian en 2019 ; CRDS ; Casa depuis 2013 ; cotisation
    maladie de 1 % sur les complémentaires."""
    if cas_type == "cadre":
        csg = 0.083 if annee >= 2018 else 0.066 if annee >= 2005 else 0.062
    else:
        csg = 0.083 if annee == 2018 else 0.066 if annee >= 2005 else 0.062
    casa = 0.003 if annee >= 2013 else 0.0
    maladie = 0.0 if part == "cnav" else 0.01
    return csg + 0.005 + casa + maladie


def _pouvoir_d_achat(simulateur, cas_type: str, composition: dict, generation: int,
                     annee: int, inflation_2026: float) -> float:
    """L'indicateur du COR, refait avec les séries du dépôt."""
    depart = generation + 60
    revalorisations = simulateur.revalorisations
    actuel = simulateur.scenario_actuel
    # Le non-cadre ne dépasse pas 2 000 € par mois en 2019, le cadre si : le
    # COR le dit (1 % et 0,3 % en 2020).
    mensuel_2019 = 1500.0 if cas_type == "non_cadre" else 5000.0

    def mensuel(part: str, an: int, mois: int) -> float:
        if part == "cnav":
            return revalorisations.generale(date(depart, 1, 1), date(an, mois, 1),
                                            False, mensuel_2019)[0]
        valeur = actuel.valeur_du_point(part, an if mois >= _mois_du_point(an) else an - 1)[0]
        echelle = actuel.conversions_points.echelle(part, depart, an)[0]
        return echelle * valeur / actuel.valeur_du_point(part, depart - 1)[0]

    def net(an: int) -> float:
        return sum(
            poids * sum(mensuel(part, an, mois) for mois in range(1, 13)) / 12
            * (1 - _prelevements(cas_type, an, part))
            for part, poids in composition.items()
        )

    prix = simulateur.macro.coefficient_prix(depart, annee)
    if annee == 2026:
        prix *= (1 + inflation_2026) / (1 + simulateur.macro.inflation(2026))
    return net(annee) / net(depart) / prix - 1


def test_le_pouvoir_d_achat_du_non_cadre_du_cor_est_retrouve(simulateur, cor):
    """Figure 3.14 du rapport de juin 2026 : entre son départ et 2026, le
    non-cadre a perdu 6,2 % de pouvoir d'achat s'il est né en 1937 (parti en
    1997) et 5,0 % s'il est né en 1952 (parti en 2012). Le dépôt retrouve les
    quatre générations à un dixième de point, 2026 compris — l'inflation de
    cette année-là est celle que le COR prévoit, 1,9 %.

    C'est le chemin exact de la pension d'un retraité : les coefficients du
    régime général, date d'effet par date d'effet, la valeur du point Arrco,
    ses changements d'échelle et sa fusion dans l'Agirc-Arrco. Une ligne
    manquante ou lue de travers dans le barème se verrait ici.
    """
    composition = cor["conventions"]["composition"]["non_cadre"]
    for generation, serie in cor["series"]["non_cadre"].items():
        publie = serie[-1]
        refait = _pouvoir_d_achat(simulateur, "non_cadre", composition, int(generation),
                                  2026, 0.019)
        assert refait == pytest.approx(publie, abs=1e-3), generation


def test_le_non_cadre_de_1952_se_suit_annee_apres_annee(simulateur, cor):
    """Les quinze années de la génération 1952, à trois dixièmes de point.

    Trois écarts restent, et ils ont leur cause : la Casa n'est due que
    depuis avril 2013, quand la convention ci-dessus la compte toute l'année ;
    la prime de 40 € versée en 2015 aux retraites de moins de 1 200 € n'est
    pas une revalorisation, et le dépôt ne la sert pas ; 2019 et 2020 gardent
    un quart de point, que les conventions publiées n'expliquent pas.
    """
    composition = cor["conventions"]["composition"]["non_cadre"]
    for rang, publie in enumerate(cor["series"]["non_cadre"]["1952"]):
        annee = 2012 + rang
        refait = _pouvoir_d_achat(simulateur, "non_cadre", composition, 1952, annee, 0.019)
        assert refait == pytest.approx(publie, abs=3e-3), annee


def test_le_cadre_du_cor_est_retrouve_a_un_tiers_de_point(simulateur, cor):
    """Le cadre perd davantage — 10,8 % né en 1937, 7,8 % né en 1952 —, parce
    que 64 % de sa pension est complémentaire et que sa CSG est au taux
    normal. Le dépôt le retrouve à 0,4 point en 2026 et à 0,2 point en 2025 :
    l'écart de 2026 est propre au cadre et à l'année prévisionnelle, aucune
    hypothèse d'inflation ou de revalorisation de novembre ne le résorbe sans
    ouvrir celui du non-cadre, et il est déclaré comme tel dans limites.md."""
    composition = cor["conventions"]["composition"]["cadre"]
    for generation, serie in cor["series"]["cadre"].items():
        depart = int(generation) + 60
        for annee, tolerance in ((2025, 2e-3), (2026, 4e-3)):
            publie = serie[annee - depart]
            refait = _pouvoir_d_achat(simulateur, "cadre", composition, int(generation),
                                      annee, 0.019)
            assert refait == pytest.approx(publie, abs=tolerance), (generation, annee)
