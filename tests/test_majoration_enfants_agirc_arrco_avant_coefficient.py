"""La majoration pour enfants nés ou élevés de l'Agirc-Arrco, avant le
coefficient d'anticipation (action 130, décision du propriétaire du 3 novembre
2026).

Depuis le 1er janvier 2019, la majoration « est calculée sur les droits de base
du participant sans tenir compte des coefficients d'anticipation éventuellement
appliqués » (circulaire Agirc-Arrco n° 2020-02-DRJ du 20 janvier 2020, fiche 4,
II.2.1). De 2012 à 2018, « Lorsque la retraite est minorée : le régime Arrco ne
tient pas compte du coefficient de minoration pour le calcul des majorations
pour enfants ; le régime Agirc en tient compte » (guide des salariés n° 9,
« Majorations pour enfants », mars 2017). Avant 2012, aucun texte lu ne le
tranche : le modèle garde le coefficient, et la fiche le déclare. Le plafond
borne la majoration ainsi calculée.

La majoration se pose comme le guide la pose : « Nombre de points de retraite
(de la période) × valeur du point × Taux de majoration », sur les points et la
valeur que la pension de chaque régime affiche ; le coefficient, lu dans la
table de l'âge (annexe A de l'accord de 1961, article 18 ; accord du 17 novembre
2017, article 84, 2 ; accord du 25 avril 1996, article 10). Chaque cas part de
la requête du simulateur, servi par le portage et refait par le moteur Python
(``servi_et_refait``). Les calculs, posés à la main, sont dans la note
docs/feuille_de_route/130/2026-11-03-majoration-enfants-agirc-arrco-avant-le-coefficient.md.
"""

from __future__ import annotations

import re

import pytest

from outils_pont import servi_et_refait

#: La carrière commune : une salariée de trois enfants au salaire moyen.
REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "22", "emploi": "cor_2026",
    "enfants": "3", "euros": "2026", "indexation": "triple_lock_inverse",
    "primes": "0", "profil": "plat", "projection": "cor_reference", "salaire": "1",
    "sexe": "F", "statut": "salarie_prive_non_cadre", "stock": "prix",
    "table": "unisexe",
}
#: Née le 15 mars 1955, au travail de 1999 à 2011 seulement, partie à 62 ans
#: le 1er avril 2017 : cinq ans avant les 67 ans du taux plein, le
#: coefficient de 0,78 (annexe A, article 18, « moins 5 ans 0,78 »).
EN_2017 = {"naissance": "1955-03-15", "liquidation": "62",
           "interruptions": "1977:1998:sans_activite, 2012:2017:sans_activite",
           "naissances": "1980-04, 1982-06, 1984-06"}
#: Née le 15 mars 1960, au travail depuis 2012, partie à 62 ans le 1er avril
#: 2022 : le coefficient de 0,78 (accord de 2017, article 84, 2) ; à 67 ans,
#: le 1er avril 2027, le taux plein, sans coefficient.
DEPUIS_2012 = {"naissance": "1960-03-15", "interruptions": "1982:2011:sans_activite",
               "naissances": "1985-04, 1987-06, 1989-06"}
#: Née le 15 mars 1948, au travail de 1999 à 2007, partie à 62 ans le 1er
#: avril 2010 : le coefficient de 0,88, celui de 60 ans « majoré de 0,0125 par
#: trimestre » (accord Arrco du 25 avril 1996, article 10 : 0,78 + 8 × 0,0125).
EN_2010 = {"naissance": "1948-03-15", "liquidation": "62",
           "interruptions": "1970:1998:sans_activite, 2008:2010:sans_activite",
           "naissances": "1973-04, 1975-06, 1977-06"}
#: Une cadre née le 15 mars 1962, au travail depuis 2012 à 4,25 salaires moyens,
#: partie à 64 ans le 1er avril 2026 : trois ans avant 67 ans, le coefficient
#: de 0,88 (article 84, 2, « moins 3 ans 0,88 »).
PLAFONNEE = {"naissance": "1962-03-15", "liquidation": "64", "statut": "salarie_prive_cadre",
             "salaire": "4.25", "interruptions": "1984:2011:sans_activite",
             "naissances": "1986-04, 1988-06, 1990-06"}

CAS = {
    "arrco_2017": EN_2017,
    "cadre_2017": {**EN_2017, "statut": "salarie_prive_cadre", "salaire": "2"},
    "unifie_2022": {**DEPUIS_2012, "liquidation": "62"},
    "unifie_2027": {**DEPUIS_2012, "liquidation": "67"},
    "arrco_2010": EN_2010,
    "plafonnee_2026": PLAFONNEE,
}

#: Chaque majoration attendue : le cas, le régime, le coefficient que sa
#: pension porte (``None`` au taux plein), le taux de ses points, et si la
#: majoration se calcule avant le coefficient.
MAJORATIONS = [
    # L'Arrco de 2012 à 2018 : ses points de 1999 à 2011, à 5 % (annexe A,
    # article 17, 2), sans le coefficient (guide n° 9).
    ("arrco_2017", "arrco", 0.78, 0.05, True),
    ("cadre_2017", "arrco", 0.78, 0.05, True),
    # L'Agirc de 2012 à 2018 « en tient compte » : ses points d'avant 2012, à
    # 8 % pour trois enfants (annexe I, article 6 bis, 2), coefficient compris.
    ("cadre_2017", "agirc", 0.78, 0.08, False),
    # Le régime unifié : les points de 2012 à 2018 de l'Arrco et ceux du
    # régime unifié depuis 2019, à 10 % (accord de 2017, article 94, 4), sans
    # le coefficient (circulaire 2020-02-DRJ).
    ("unifie_2022", "arrco", 0.78, 0.10, True),
    ("unifie_2022", "agirc_arrco", 0.78, 0.10, True),
    # Au taux plein, rien ne bouge : 10 % de l'allocation.
    ("unifie_2027", "arrco", None, 0.10, True),
    ("unifie_2027", "agirc_arrco", None, 0.10, True),
    # Avant 2012, aucun texte lu ne tranche : le modèle garde le coefficient
    # (accord du 25 avril 1996, article 11 : 5 % « de leur allocation »).
    ("arrco_2010", "arrco", 0.88, 0.05, False),
]

#: « Le montant du plafond des majorations pour enfants nés ou élevés reste
#: fixé à 2 367,48 € » (circulaire Agirc-Arrco 2025-15-DT, paramètres du
#: régime 2025-2026).
PLAFOND_2026 = 2367.48

#: « 1,639.06 points × valeur de service 1.2513 € » : les points et la valeur
#: que le détail de la pension affiche.
POINTS_ET_VALEUR = re.compile(r"([\d,]+\.\d+) points × valeur de service ([\d.]+) €")


@pytest.fixture(scope="module")
def servis():
    cas = [{"cle": cle, "requete": {**REQUETE, **champs}} for cle, champs in CAS.items()]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


def _pension(actuel: dict, regime: str) -> dict:
    return next(p for p in actuel["pensions_par_regime"] if p["regime"] == regime)


def _majoration(actuel: dict) -> dict:
    return next(a for a in actuel["avantages_appliques"] if a["code"] == "majoration_enfants")


def _droits(pension: dict) -> float:
    """Les points du régime × la valeur de service : l'allocation avant le
    coefficient, telle que le détail de la pension l'affiche."""
    trouve = POINTS_ET_VALEUR.search(pension["detail"])
    assert trouve, pension["detail"]
    return float(trouve.group(1).replace(",", "")) * float(trouve.group(2))


@pytest.mark.parametrize("cle, regime, coefficient, taux, avant", MAJORATIONS)
def test_la_majoration_se_calcule_avant_le_coefficient_quand_la_caisse_le_dit(
        servis, cle, regime, coefficient, taux, avant):
    """Points × valeur × taux, sans le coefficient là où la caisse le dit ; le
    coefficient que porte la pension est celui de la table de l'âge."""
    pension = _pension(servis[cle], regime)
    if coefficient is None:
        assert "coefficient d'anticipation" not in pension["detail"], pension["detail"]
    else:
        assert f"coefficient d'anticipation {coefficient:.4f}" in pension["detail"], (
            pension["detail"])
    part = dict(_majoration(servis[cle])["par_regime"])[regime]
    attendue = _droits(pension) * taux * (1.0 if avant or coefficient is None else coefficient)
    assert part == pytest.approx(attendue, abs=0.01), (cle, regime, part, attendue)


def test_le_plafond_borne_la_majoration_calculee_sans_le_coefficient(servis):
    """« La majoration pour enfants nés ou élevés est plafonnée » (accord de
    2017, article 94) : le plafond borne la majoration que la circulaire
    calcule « sans tenir compte des coefficients d'anticipation ». La cadre
    partie en 2026 passe le plafond sans le coefficient, et non avec lui : sa
    majoration est le plafond, 2 367,48 €."""
    actuel = servis["plafonnee_2026"]
    regimes = [p for p in actuel["pensions_par_regime"]
               if p["regime"] in {"agirc", "arrco", "agirc_arrco"} and p["montant"] > 0]
    assert {p["regime"] for p in regimes} == {"agirc", "arrco", "agirc_arrco"}
    assert all("coefficient d'anticipation 0.8800" in p["detail"] for p in regimes)
    sans_coefficient = sum(_droits(p) for p in regimes) * 0.10
    avec_coefficient = sum(p["montant"] for p in regimes) * 0.10
    assert avec_coefficient < PLAFOND_2026 < sans_coefficient
    majoration = _majoration(actuel)
    complementaire = sum(part for code, part in majoration["par_regime"]
                         if code in {"agirc", "arrco", "agirc_arrco"})
    assert complementaire == pytest.approx(PLAFOND_2026, abs=0.01)
