"""Les âges légaux se comptent au mois près (action 130, relecture R-L-bis).

Les textes écrivent leurs âges en ans et en mois : « 4° Soixante et un ans et
deux mois pour les assurés nés en 1953 » (D. 161-2-1-9, LEGIARTI000025089933,
du 31 décembre 2011 au 1er septembre 2023), dont L. 351-8, 1°, fait l'âge du
taux plein, « l'âge prévu à l'article L. 161-17-2 augmenté de cinq années »
(LEGIARTI000028498855, « applicable aux pensions prenant effet à compter du
1er février 2014 ») : 66 ans et 2 mois. Les tables du dépôt les écrivent au
centième : 61,17 et 66,17, qui dépassent 61 ans 2 mois (61,1667) et 66 ans
2 mois (66,1667). L'assuré né en 1953 qui partait à 66 ans et 2 mois pile
gardait un trimestre de minoration — 49,375 % au régime général, 0,99 à
l'Agirc-Arrco, 0,9875 à la CNAVPL et à l'ASV des biologistes —, et celui qui
partait à 61 ans et 2 mois pile se voyait refuser l'ouverture du droit.

Les valeurs attendues viennent des textes, à la date d'effet de chaque cas :
- le régime général : « le taux plein, soit 50 % » à « l'âge prévu au 1° de
  l'article L. 351-8 », et sinon un coefficient de minoration fonction « du
  nombre de trimestres correspondant à la durée séparant l'âge auquel leur
  pension prend effet [...] de l'âge prévu au 1° de l'article L. 351-8 »
  (R. 351-27, LEGIARTI000024113020, du 3 juin 2011 au 1er septembre 2023) ;
- la CNAVPL : la réduction « fonction [...] du nombre de trimestres
  correspondant à la durée séparant l'âge auquel la pension de retraite prend
  effet [...] de l'âge prévu au 1° de l'article L. 351-8 » (R. 643-7,
  LEGIARTI000024113055, du 3 juin 2011 au 5 mars 2023) ;
- l'ASV des biologistes : « réduite par application d'un coefficient
  d'anticipation qui est fonction du nombre de trimestres manquants, à la date
  d'effet des droits, pour atteindre l'âge fixé à l'article L. 351-8 (1°) »
  (statuts de la CAVP, article 14, arrêté du 23 juin 2011,
  JORFARTI000024270214) ;
- l'Agirc-Arrco, depuis le 1er janvier 2019 : « Le participant peut bénéficier
  de sa pension au titre du présent régime sans abattement dès lors qu'il a
  atteint l'âge visé au 1° de l'article L. 351-8 du code de la sécurité
  sociale » (accord national interprofessionnel du 17 novembre 2017,
  article 84, 1, version « Applicable au 1 janvier 2019 »).
L'ouverture : la pension est servie « à partir de l'âge mentionné à
l'article L. 161-17-2 » (L. 351-1, LEGIARTI000023035688), l'âge de
D. 161-2-1-9 pour les générations 1951 à 1954.

Chaque cas passe par ``servi_et_refait`` : le portage le sert, le moteur
Python le refait au bit près.
"""

from __future__ import annotations

import re

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.chargement import charger_table_par_generation
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.scenarios.actuel import (
    AgesCategorieActive, AgesRegimes, CarriereLongue, DureesServicesActifs,
    DureesServicesMilitaires,
)

from outils_pont import servi_et_refait

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "26", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "primes": "0", "profil": "plat", "projection": "cor_reference", "salaire": "2",
    "sexe": "H", "stock": "prix", "table": "unisexe",
}

COEFFICIENT = re.compile(r"coefficient d'anticipation ([\d.]+)")

#: La naissance, l'âge du 1° de L. 351-8 (ans, mois), et celui de L. 161-17-2.
#: D. 161-2-1-9 : « 2° Soixante ans et quatre mois pour les assurés nés entre
#: le 1er juillet 1951 et le 31 décembre 1951 inclus ; 3° Soixante ans et neuf
#: mois pour les assurés nés en 1952 ; 4° Soixante et un ans et deux mois pour
#: les assurés nés en 1953 ; 5° Soixante et un ans et sept mois pour les
#: assurés nés en 1954 ; 6° Soixante deux ans pour les assurés nés à compter du
#: 1er janvier 1955 » ; cinq années de plus au 1° de L. 351-8. Né le 10, l'assuré
#: part au 1er du mois qui suit l'âge : à 66 ans et 2 mois, le 1er mai 2019.
GENERATIONS = {
    "1951-07-10": ((65, 4), (60, 4)),
    "1952-02-10": ((65, 9), (60, 9)),
    "1953-02-10": ((66, 2), (61, 2)),
    "1954-02-10": ((66, 7), (61, 7)),
    "1955-02-10": ((67, 0), (62, 0)),
}

#: Les complémentaires des salariés : l'accord de 2017 ne régit que les
#: pensions prenant effet depuis le 1er janvier 2019, soit, à l'âge du taux
#: plein, les générations 1953 (mai 2019), 1954 (octobre 2020) et 1955
#: (mars 2022). Celles d'avant relevaient de la convention de 1947 et de
#: l'accord Arrco, non relus ici.
SOUS_L_ACCORD_DE_2017 = ("1953-02-10", "1954-02-10", "1955-02-10")


def _cas(statut: str, naissance: str, age: tuple[int, int]) -> dict:
    annees, mois = age
    return {"cle": f"{statut}|{naissance}|{annees}|{mois}",
            "requete": {**REQUETE, "statut": statut, "naissance": naissance,
                        "liquidation": str(annees), "liquidation_mois": str(mois)}}


def _avant(age: tuple[int, int]) -> tuple[int, int]:
    annees, mois = age
    return (annees, mois - 1) if mois else (annees - 1, 11)


@pytest.fixture(scope="module")
def servis():
    cas = []
    for naissance, (taux_plein, ouverture) in GENERATIONS.items():
        for statut in ("salarie_prive_cadre", "biologiste_liberal"):
            cas.append(_cas(statut, naissance, taux_plein))
            cas.append(_cas(statut, naissance, ouverture))
            cas.append(_cas(statut, naissance, _avant(ouverture)))
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


def _pensions(actuel: dict) -> dict[str, str]:
    return {p["regime"]: p["detail"] for p in actuel["pensions_par_regime"]}


@pytest.mark.parametrize("naissance", GENERATIONS)
def test_le_salarie_a_le_taux_plein_a_l_age_du_1_de_l_351_8(servis, naissance):
    """Débutant à 26 ans, il n'a pas la durée (160 trimestres pour 165 en
    1953) : seul l'âge lui donne le taux plein, 50 %, et à l'Agirc-Arrco la
    pension sans abattement."""
    annees, mois = GENERATIONS[naissance][0]
    actuel = servis[f"salarie_prive_cadre|{naissance}|{annees}|{mois}"]
    assert actuel["liquidation_ouverte"], actuel["motif_ouverture"]
    pensions = _pensions(actuel)
    assert "taux 50.000%" in pensions["regime_general"], pensions["regime_general"]
    if naissance in SOUS_L_ACCORD_DE_2017:
        abattues = {regime: detail for regime, detail in pensions.items()
                    if regime != "regime_general" and COEFFICIENT.search(detail)}
        assert abattues == {}


@pytest.mark.parametrize("naissance", GENERATIONS)
def test_le_biologiste_n_est_pas_minore_a_l_age_du_1_de_l_351_8(servis, naissance):
    """La CNAVPL (R. 643-7) et l'ASV des biologistes (statuts, article 14)
    comptent les trimestres manquants jusqu'à l'âge du 1° de L. 351-8 : à cet
    âge, il n'en manque aucun."""
    annees, mois = GENERATIONS[naissance][0]
    actuel = servis[f"biologiste_liberal|{naissance}|{annees}|{mois}"]
    assert actuel["liquidation_ouverte"], actuel["motif_ouverture"]
    pensions = _pensions(actuel)
    for regime in ("cnavpl", "asv_directeurs_laboratoire"):
        assert COEFFICIENT.search(pensions[regime]) is None, pensions[regime]


@pytest.mark.parametrize("statut", ("salarie_prive_cadre", "biologiste_liberal"))
@pytest.mark.parametrize("naissance", GENERATIONS)
def test_le_droit_s_ouvre_a_l_age_de_l_161_17_2_et_pas_un_mois_avant(servis, naissance,
                                                                     statut):
    ouverture = GENERATIONS[naissance][1]
    annees, mois = ouverture
    a_l_age = servis[f"{statut}|{naissance}|{annees}|{mois}"]
    assert a_l_age["liquidation_ouverte"], a_l_age["motif_ouverture"]
    annees, mois = _avant(ouverture)
    avant = servis[f"{statut}|{naissance}|{annees}|{mois}"]
    assert not avant["liquidation_ouverte"]


# -- chaque âge des tables et des fiches tombe sur un mois entier ---------------

def _hors_du_mois(valeurs) -> list:
    return [valeur for valeur in valeurs
            if valeur is not None and abs(valeur * 12 - round(valeur * 12)) > 1e-9]


def test_les_tables_d_ages_par_generation_tombent_sur_un_mois_entier():
    """Toute table ``generation,age,fiabilite`` de la législation : âges
    d'ouverture, d'annulation de la décote, de la surcote des régimes spéciaux,
    de jouissance du militaire."""
    dossier = RACINE_DONNEES / "reference" / "legislation"
    lues = 0
    for chemin in sorted(dossier.glob("*.csv")):
        entete = next(ligne for ligne in chemin.read_text(encoding="utf-8").splitlines()
                      if not ligne.lstrip().startswith("#"))
        if entete.strip() != "generation,age,fiabilite":
            continue
        table, _ = charger_table_par_generation(chemin, "age")
        lues += 1
        assert _hors_du_mois(age for age, _ in table.values()) == [], chemin.name
    assert lues >= 5


def test_les_autres_ages_de_la_legislation_tombent_sur_un_mois_entier():
    regimes = AgesRegimes(RACINE_DONNEES)
    ages = [age for lignes in regimes._table.values()
            for ouverture, taux_plein, _ in lignes.values() for age in (ouverture, taux_plein)]
    ages += [age for lignes in regimes._surcotes.values() for age in lignes.values()]
    actifs = AgesCategorieActive(RACINE_DONNEES)
    ages += [age for lignes in actifs._table.values() for derogation in lignes.values()
             for age in (derogation.age_ouverture, derogation.age_annulation,
                         derogation.services_requis)]
    for classe in (DureesServicesActifs, DureesServicesMilitaires):
        ages += [annees for lignes in classe(RACINE_DONNEES)._table.values()
                 for annees, _ in lignes.values()]
    longue = CarriereLongue(RACINE_DONNEES)
    ages += [ligne[4] for lignes in longue._table.values() for ligne in lignes]
    assert _hors_du_mois(ages) == []


AGE = re.compile(r"(^|_)age(_|$)")


def test_les_ages_des_fiches_de_regime_tombent_sur_un_mois_entier():
    hors = {}
    for regime in CatalogueRegimes(RACINE_DONNEES):
        for periode in regime.periodes:
            for champ, valeur in vars(periode).items():
                if AGE.search(champ) and isinstance(valeur, float) and _hors_du_mois([valeur]):
                    hors[f"{regime.code}:{periode.debut}:{champ}"] = valeur
    assert hors == {}
