"""La surcote de la Banque de France est celle de l'article 33 de son
règlement, trimestre par trimestre (action 191).

Règlement annexé au décret n° 2007-262 du 27 février 2007, article 33,
rédaction d'origine (LEGIARTI000006778516) : « un coefficient de majoration
calculé sur la base de 0,75 % par trimestre supplémentaire s'applique au
montant de la pension […] dans la limite de vingt trimestres. Le nombre de
trimestres supplémentaires pris en compte pour ce calcul est égal, à la date
de liquidation de la pension, au nombre de trimestres de services effectués
après le 1er avril 2007, au-delà de l'âge de soixante ans et en sus du nombre
de trimestres nécessaires pour obtenir le pourcentage maximum ». Le décret
n° 2008-1514 du 30 décembre 2008 (article 1er, JORFARTI000020018201) porte le
taux à 1,25 %, pour les seuls « trimestres d'assurance cotisés et effectués à
compter du 1er janvier 2009 » (II, 2°). Le décret n° 2012-701 du 7 mai 2012
(article 26, 2°) retire la limite de vingt trimestres, pour les « pensions
prenant effet à compter du 1er janvier 2016 » (article 41, I).

Le dépôt servait un taux plat, celui de l'année du départ, à tous les
trimestres accomplis depuis soixante ans : douze trimestres à 0,75 % à
l'agent parti à 63 ans en février 2008, quand le texte en compte trois.

Les valeurs attendues sont posées à la main depuis le texte : le taux est de
75 %, majoré du taux de chaque trimestre entier compris entre le 1er avril
2007, ou le mois qui suit les soixante ans s'il vient après, et la date
d'effet. Les carrières commencent à vingt ans, sauf mention : la durée est
acquise à soixante ans.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import RACINE_PROJET

from facade import Simulateur

REGLES = Path(RACINE_PROJET) / "data" / "reference" / "regles"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _majoration(simulateur: Simulateur, naissance: int, depart: float,
                debut: int = 20, mois: int = 1) -> float:
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, mois_naissance=mois, sexe="H",
        affiliation="agent_banque_de_france", age_debut=debut, age_liquidation=depart)
    return simulateur.scenario_actuel.calculer(carriere).taux_liquidation / 0.75 - 1.0


@pytest.mark.parametrize("naissance, mois, depart, a_0_75, a_1_25", [
    # Né en janvier 1945, soixante ans en 2005. Pension d'août 2007 : avril à
    # juillet 2007, quatre mois, un trimestre entier.
    (1945, 1, 62.5, 1, 0),
    # Pension de novembre 2007 : avril à octobre, sept mois, deux trimestres.
    (1945, 1, 62.75, 2, 0),
    # Pension de février 2008 : avril 2007 à janvier 2008, dix mois, trois
    # trimestres — et non les douze accomplis depuis soixante ans.
    (1945, 1, 63, 3, 0),
    # Né en janvier 1947, pension de février 2010 : avril 2007 à décembre
    # 2008, sept trimestres à 0,75 % ; janvier 2009 à janvier 2010, treize
    # mois, quatre trimestres « effectués à compter du 1er janvier 2009 ».
    (1947, 1, 63, 7, 4),
    # Né en décembre 1947, soixante ans révolus au 1er janvier 2008, pension
    # de janvier 2010 : quatre trimestres en 2008, quatre en 2009.
    (1947, 12, 62, 4, 4),
    # Né en décembre 1949, soixante ans révolus au 1er janvier 2010, pension
    # de janvier 2012 : huit trimestres, tous d'après 2009.
    (1949, 12, 62, 0, 8),
    # Né en janvier 1950, soixante ans révolus en février 2010, pension de
    # février 2012 : vingt-quatre mois, huit trimestres — le mois de janvier
    # 2012, qui ne valide aucun trimestre à lui seul, compte dans le huitième.
    (1950, 1, 62, 0, 8),
    # Né en janvier 1948, soixante ans révolus en février 2008, pension de
    # février 2010 : huit trimestres. De janvier 2009 à janvier 2010, treize
    # mois, quatre trimestres entiers « effectués à compter du 1er janvier
    # 2009 » ; les quatre autres à 0,75 %, dont celui qui court de novembre
    # 2008 à janvier 2009 — PRÉSOMPTION que la fiche déclare.
    (1948, 1, 62, 4, 4),
])
def test_chaque_trimestre_d_apres_le_1er_avril_2007_a_le_taux_de_sa_date(
        simulateur, naissance, mois, depart, a_0_75, a_1_25):
    assert _majoration(simulateur, naissance, depart, mois=mois) == pytest.approx(
        a_0_75 * 0.0075 + a_1_25 * 0.0125)


def test_les_trimestres_comptes_sont_ceux_en_sus_de_la_duree(simulateur):
    """Né en janvier 1947, entré à vingt-cinq ans : 152 trimestres en février
    2010, pour 150 requis (article 69, soixante ans avant le 1er avril 2007).
    Deux trimestres « en sus », les derniers, accomplis en 2009 : 1,25 %
    chacun, et non les onze effectués depuis le 1er avril 2007."""
    assert _majoration(simulateur, 1947, 63, debut=25) == pytest.approx(2 * 0.0125)


def test_vingt_trimestres_au_plus_avant_2016(simulateur):
    """« Dans la limite de vingt trimestres », jusqu'aux pensions de 2015. Né
    en janvier 1947, pension d'août 2012 : avril 2007 à juillet 2012,
    soixante-quatre mois, vingt et un trimestres, dont quatorze depuis 2009.
    Vingt sont servis ; le texte ne dit pas lequel tombe, et la fiche PRÉSUME
    que c'est le plus ancien : quatorze à 1,25 %, six à 0,75 %."""
    assert _majoration(simulateur, 1947, 65.5) == pytest.approx(14 * 0.0125 + 6 * 0.0075)


def _version(fiche: dict, identifiant: str) -> dict:
    return next(v for v in fiche["versions"] if v["id"] == identifiant)


def test_la_fiche_porte_les_taux_les_dates_et_la_limite_du_texte():
    fiche = yaml.safe_load((REGLES / "surcote_banque_de_france.yaml").read_text("utf-8"))
    assert _version(fiche, "avant_le_reglement_de_2007")["contenu"]["parametres"]["taux"] == []
    de_2007 = _version(fiche, "vingt_trimestres_au_plus")
    assert [str(borne) for borne in de_2007["bornes"]["liquidation.date_effet"]] == [
        "2007-04-01", "2016-01-01"]
    assert de_2007["contenu"]["parametres"] == {
        "taux": [{"depuis": "2007-04-01", "taux": 0.0075},
                 {"depuis": "2009-01-01", "taux": 0.0125}],
        "trimestres_maximum": 20,
    }
    de_2016 = _version(fiche, "sans_limite_de_trimestres")
    assert [str(borne) for borne in de_2016["bornes"]["liquidation.date_effet"]] == [
        "2016-01-01", "None"]
    assert de_2016["contenu"]["parametres"] == {
        "taux": de_2007["contenu"]["parametres"]["taux"],
        "trimestres_maximum": None,
    }


def test_toutes_les_periodes_du_reglement_renvoient_a_la_fiche():
    regime = yaml.safe_load((REGLES.parent / "regimes" / "banque_de_france.yaml")
                            .read_text("utf-8"))
    periodes = [p for p in regime["periodes"] if p["debut"] >= 2007]
    assert len(periodes) >= 16
    assert {p.get("surcote_bareme") for p in periodes} == {"surcote_banque_de_france"}
