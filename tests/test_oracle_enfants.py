"""L'oracle au-delà des carrières simples, deuxième famille : les enfants des
fonctionnaires, confrontés à OpenFisca-France-Pension (action 153, étape 2).

Le frère de ``tests/test_oracle_familles.py``, dont il reprend le calcul du
dépôt et la méthode : la convention de traduction d'abord, écrite dans
``scripts/fetch/openfisca_enfants.py`` et portée par le témoin, puis chaque
grandeur ; un écart connu est déclaré avec le texte qui le tranche, et chacun
des deux modèles doit rendre exactement ce que SA règle commande.

* **Au-delà de trois enfants** : la bonification de L. 12, b, un an par enfant
  né avant 2004, et la majoration de L. 18, dix pour cent puis cinq par enfant
  au-delà du troisième, que le traitement plafonne. Rien à corriger.
* **Les enfants nés depuis 2004** : la majoration de durée de L. 12 bis, deux
  trimestres en durée, aucun en services. Rien à corriger à l'État ; à la
  CNRACL, OpenFisca n'en accorde aucune.
* **Les enfants nés hors des services** : OpenFisca ne lit ni le recrutement
  ni la radiation. Il accorde la bonification de L. 12, b, à l'enfant né avant
  le recrutement d'une pension de 2009, que R. 13 réservait alors à
  l'interruption prise dans un congé du statut, et la majoration de L. 12 bis
  à la femme qui a accouché avant son recrutement.

Le dépôt avait raison sur chaque point ; les trois écarts sont chez
OpenFisca, au registre (``data/reference/referents.yaml``).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Simulateur
from test_oracle_familles import (
    PRECISION_OPENFISCA,
    PREFIXES,
    TAUX_PLEIN,
    TOLERANCE_EXACTE,
    _coefficient_de_proratisation,
    _notre_calcul,
)

TEMOIN = Path(__file__).resolve().parent / "temoins" / "openfisca_enfants.json"

AU_DELA = "au_dela_de_trois"
APRES_2004 = "nes_apres_2004"
HORS_SERVICES = "hors_services"

#: Les entrées d'OpenFisca que la convention doit dire, au témoin.
CONVENTION_ATTENDUE = {
    "date_de_naissance", "sexe", "liquidation_date", "salaire_de_base",
    "duree_de_service_cotisee_annuelle", "quotite_de_travail", "taux_de_prime",
    "nombre_enfants", "nombre_enfants_nes_avant_2004", "date_naissance_enfant",
    "regime_general_cnav_liquidation_date", "non_traduit",
}

NE_AVANT = "2004-01-01"
SERVICES_PAR_AN = 4
#: L. 12, b : un an de bonification par enfant né avant 2004.
BONIFICATION_PAR_ENFANT = 4
#: L. 12 bis : deux trimestres de durée par enfant né depuis.
MAJORATION_PAR_ENFANT = 2
#: L. 18 : dix pour cent au parent de trois enfants, cinq par enfant au-delà.
MAJORATION_DE_TROIS, MAJORATION_PAR_ENFANT_EN_PLUS = 0.10, 0.05
#: L. 13, I : le pourcentage maximum, porté par les bonifications jusqu'à 80 %.
POURCENTAGE_MAXIMUM_BONIFIE = 80 / 75
#: L. 14, I : vingt trimestres de décote au plus, à 1,25 % en 2020.
DECOTE_PLAFONNEE = 20
COEFFICIENT_DE_DECOTE_2020 = 0.0125

#: Ce que chaque modèle accorde aux enfants qu'il ne compare pas aux mêmes
#: dates — en trimestres, le nôtre, le sien —, et le texte qui tranche.
ECARTS = {
    # Décret n° 2003-1306, article 21, I, rédaction du 1er juillet 2011
    # (LEGIARTI000023414107) : les femmes fonctionnaires de la CNRACL ont la
    # majoration de deux trimestres. Sa variable la lui refuse : elle compare la
    # liquidation de l'ÉTAT (`fonction_publique_liquidation_date`), non
    # déclarée, à celle du régime général.
    "cnracl_mere_deux_enfants_apres_2004_2020": (4, 0),
    # R. 13, rédaction du 19 avril 2009 (LEGIARTI000020532497) : la
    # bonification est « subordonnée à une interruption d'activité [...] dans
    # le cadre d'un congé » du statut ; l'enfant né avant le recrutement n'en
    # ouvre pas, hors du b bis, qu'aucun des deux ne lit.
    "mere_enfants_avant_recrutement_2009": (0, 8),
    # L. 12 bis (LEGIARTI000006362697) : la majoration va aux femmes « ayant
    # accouché postérieurement à leur recrutement ».
    "mere_accouchement_avant_recrutement_2020": (0, 2),
}


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def nous(temoin) -> dict[str, dict]:
    """Le calcul du dépôt pour chaque profil, fait une fois."""
    simulateur = Simulateur(Parametres())
    return {code: _notre_calcul(simulateur, entree["profil"])
            for code, entree in temoin["profils"].items()}


def _de_la_regle(temoin: dict, regle: str) -> list[tuple[str, dict]]:
    return [(code, entree) for code, entree in temoin["profils"].items()
            if entree["profil"]["regle"] == regle]


def _avant_2004(profil: dict) -> int:
    return sum(n < NE_AVANT for n in profil["naissances"])


def _depuis_2004(profil: dict) -> int:
    return len(profil["naissances"]) - _avant_2004(profil)


def _taux_de_majoration(enfants: int) -> float:
    if enfants < 3:
        return 0.0
    return MAJORATION_DE_TROIS + MAJORATION_PAR_ENFANT_EN_PLUS * (enfants - 3)


# -- la convention ---------------------------------------------------------------

def test_le_temoin_suit_sa_convention_de_traduction(temoin):
    """Le témoin dit d'où il vient, porte sa convention, et chaque profil les
    entrées qu'OpenFisca a reçues : un nombre d'enfants, le compte de ceux nés
    avant 2004 — pendant les services ou non —, la troisième naissance au
    parent de trois enfants, et rien d'autre ; ni temps partiel, ni date de
    liquidation au régime général."""
    assert temoin["source"] == "OpenFisca-France-Pension"
    assert temoin["version"]
    assert CONVENTION_ATTENDUE <= set(temoin["convention"])
    profils = temoin["profils"]
    assert {e["profil"]["regle"] for e in profils.values()} == {
        AU_DELA, APRES_2004, HORS_SERVICES}
    for code, entree in profils.items():
        profil, recu, eux = entree["profil"], entree["entrees_openfisca"], entree["openfisca"]
        prefixe = PREFIXES[profil["regime"]]
        assert 2009 <= profil["liquidation"] <= 2020, code
        assert eux["duree_assurance"] > 0 and eux["pension_brute"] > 0, code
        assert "temps_partiel" not in profil and "raison" not in profil, code
        assert not any(nom.endswith(("quotite_de_travail", "liquidation_date"))
                       for nom in recu), code
        assert recu["sexe"] is (profil["sexe"] == "F"), code
        naissances = sorted(profil["naissances"])
        assert recu["nombre_enfants"] == len(naissances), code
        assert recu[f"{prefixe}_nombre_enfants_nes_avant_2004"] == _avant_2004(profil), code
        assert recu.get("date_naissance_enfant") == (
            naissances[2] if len(naissances) >= 3 else None), code
        # Le profil dit lui-même qu'un enfant naît avant le recrutement.
        avant = any(int(n[:4]) < profil["debut"] for n in naissances)
        assert avant is bool(profil.get("hors_services")), code
        assert avant is (profil["regle"] == HORS_SERVICES), code
        assert all(int(n[:4]) < profil["liquidation"] for n in naissances), code


def test_le_depart_des_parents_n_est_pas_l_objet(temoin, nous):
    """Le départ des parents de trois enfants est la première famille. Ici, il
    n'est ouvert chez nous qu'à la mère de sept enfants, et sa pension ne
    dépend pas de la durée requise : elle atteint des deux côtés le
    pourcentage maximum de 80 %, quelle que soit l'année qui la fixe."""
    for code, entree in temoin["profils"].items():
        moi, eux = nous[code], entree["openfisca"]
        assert moi["liquidation_ouverte"], code
        assert not eux["depart_anticipe"], code
        if moi["depart"] is None:
            continue
        assert code == "mere_sept_enfants_plafond_2014"
        assert eux["coefficient_de_proratisation"] == pytest.approx(
            POURCENTAGE_MAXIMUM_BONIFIE, abs=TOLERANCE_EXACTE)
        for requis in (moi["proratisation"], eux["duree_requise_de_la_generation"]):
            assert _coefficient_de_proratisation(
                moi["services"], moi["services_et_bonifications"] - moi["services"],
                requis) == pytest.approx(POURCENTAGE_MAXIMUM_BONIFIE)
        assert moi["pension"] == pytest.approx(eux["pension_brute"], rel=PRECISION_OPENFISCA)


# -- au-delà de trois enfants ------------------------------------------------------

def test_la_bonification_compte_chaque_enfant_au_dela_de_trois(temoin, nous):
    """L. 12, b : un an par enfant né avant 2004, à la mère — seize trimestres
    pour quatre enfants, vingt pour cinq, vingt-huit pour sept —, en services
    et en durée ; rien au père, que la présomption laisse sans interruption
    d'activité. Les deux modèles comptent pareil."""
    for code, entree in _de_la_regle(temoin, AU_DELA):
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        assert len(profil["naissances"]) > 3 and _depuis_2004(profil) == 0, code
        attendue = BONIFICATION_PAR_ENFANT * _avant_2004(profil) \
            if profil["sexe"] == "F" else 0
        assert moi["services_et_bonifications"] - moi["services"] \
            == eux["bonification_enfants"] == eux["majoration_duree"] == attendue, code
        assert moi["services"] == eux["services"], code
        assert moi["duree_assurance"] == eux["duree_assurance"] \
            == moi["services"] + attendue, code


def test_la_majoration_de_pension_croit_de_cinq_points_par_enfant(temoin, nous):
    """L. 18 : dix pour cent au parent de trois enfants, cinq de plus par
    enfant au-delà — 15 % pour quatre, 20 % pour cinq —, au père comme à la
    mère, sur la pension de chacun. Des deux côtés."""
    for code, entree in temoin["profils"].items():
        if code == "mere_sept_enfants_plafond_2014":
            continue
        eux, moi = entree["openfisca"], nous[code]
        taux = _taux_de_majoration(len(entree["profil"]["naissances"]))
        assert moi["majoration_pension"] == pytest.approx(taux * moi["pension"], abs=1e-6), code
        assert eux["majoration_pension"] == pytest.approx(
            taux * eux["pension_brute"], rel=PRECISION_OPENFISCA, abs=1e-6), code


def test_le_traitement_plafonne_la_pension_majoree(temoin, nous):
    """L. 18 : « En aucun cas, le montant de la pension majorée ne peut
    excéder le montant du traitement ». La mère de sept enfants a 80 % de son
    traitement (L. 13, I) ; trente pour cent de majoration l'en porteraient à
    104 %. Le dépôt réduit la majoration, OpenFisca plafonne la somme : les
    deux servent le traitement."""
    code = "mere_sept_enfants_plafond_2014"
    eux, moi = temoin["profils"][code]["openfisca"], nous[code]
    assert _taux_de_majoration(7) == pytest.approx(0.30)
    assert moi["pension"] == pytest.approx(eux["pension_brute"], rel=PRECISION_OPENFISCA)
    assert moi["pension"] * (1 + _taux_de_majoration(7)) > moi["traitement_de_reference"]
    assert moi["pension"] + moi["majoration_pension"] == pytest.approx(
        moi["traitement_de_reference"], abs=1e-6)
    assert eux["pension"] == pytest.approx(eux["traitement_de_reference"],
                                           rel=PRECISION_OPENFISCA)
    assert eux["majoration_pension"] == pytest.approx(
        _taux_de_majoration(7) * eux["pension_brute"], rel=PRECISION_OPENFISCA)


# -- les enfants nés depuis 2004 --------------------------------------------------

def test_les_enfants_nes_depuis_2004_comptent_en_duree_seulement(temoin, nous):
    """L. 12 bis : deux trimestres par enfant né depuis 2004, en durée
    d'assurance, aucun en services — la pension n'est pas avant septembre
    2026, où le b ter en fait entrer un. L'enfant né avant 2004 garde sa
    bonification d'un an, en services. Le dépôt compte ainsi, à l'État comme à
    la CNRACL ; OpenFisca à l'État seul (``ECARTS``)."""
    for code, entree in _de_la_regle(temoin, APRES_2004):
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        bonification = BONIFICATION_PAR_ENFANT * _avant_2004(profil)
        majoration = MAJORATION_PAR_ENFANT * _depuis_2004(profil)
        assert majoration > 0, code
        assert moi["services_et_bonifications"] - moi["services"] \
            == eux["bonification_enfants"] == bonification, code
        assert moi["duree_assurance"] == moi["services"] + bonification + majoration, code
        assert moi["services"] == eux["services"], code
        le_sien = ECARTS.get(code, (majoration, majoration))[1]
        assert eux["majoration_duree_enfants"] == le_sien, code
        assert eux["duree_assurance"] == eux["services"] + bonification + le_sien, code


def test_la_majoration_de_duree_ne_joue_que_sur_la_decote(temoin, nous):
    """La majoration n'entre pas aux services : elle ne joue que sur la décote
    (L. 14, I), un trimestre de moins par trimestre de durée, à 1,25 % en
    2020, sous le plafond de vingt. Le traitement et la proratisation
    concordent ; la pension de chacun se déduit de l'autre par le seul taux."""
    for code, entree in _de_la_regle(temoin, APRES_2004):
        eux, moi = entree["openfisca"], nous[code]
        assert entree["profil"]["liquidation"] == 2020, code
        requis = eux["duree_requise_de_la_generation"]
        assert moi["proratisation"] == requis, code
        for duree, decote, taux in (
                (moi["duree_assurance"], moi["decote_trimestres"], moi["taux_de_liquidation"]),
                (eux["duree_assurance"], eux["decote_trimestres"], eux["taux_de_liquidation"])):
            assert decote == min(DECOTE_PLAFONNEE, requis - duree), code
            assert taux == pytest.approx(
                TAUX_PLEIN * (1 - COEFFICIENT_DE_DECOTE_2020 * decote), abs=TOLERANCE_EXACTE), code
        assert _coefficient_de_proratisation(
            moi["services"], moi["services_et_bonifications"] - moi["services"],
            moi["proratisation"]) == pytest.approx(
                eux["coefficient_de_proratisation"], abs=TOLERANCE_EXACTE), code
        assert moi["traitement_de_reference"] == pytest.approx(
            eux["traitement_de_reference"], rel=PRECISION_OPENFISCA), code
        assert moi["pension_avant_minimum"] * eux["taux_de_liquidation"] \
            / moi["taux_de_liquidation"] == pytest.approx(
                eux["pension_avant_minimum"], rel=PRECISION_OPENFISCA), code


def test_la_cnracl_n_a_pas_de_majoration_de_duree_chez_lui(temoin, nous):
    """Décret n° 2003-1306, article 21, I (LEGIARTI000023414107) : « Pour
    chacun de leurs enfants nés à compter du 1er janvier 2004, les femmes
    fonctionnaires ayant accouché postérieurement à leur recrutement
    bénéficient d'une majoration de la durée d'assurance [...] fixée à deux
    trimestres ». Chez OpenFisca, la variable de la CNRACL compare la date de
    liquidation de l'État, qu'on ne lui donne pas, à celle du régime général :
    l'agente de la CNRACL n'a jamais sa majoration, et l'agente de l'État, de
    même carrière, l'a. L'écart est le sien."""
    etat = temoin["profils"]["mere_deux_enfants_apres_2004_2020"]["openfisca"]
    code = "cnracl_mere_deux_enfants_apres_2004_2020"
    eux, moi = temoin["profils"][code]["openfisca"], nous[code]
    le_notre, le_sien = ECARTS[code]
    assert etat["majoration_duree_enfants"] == le_notre == MAJORATION_PAR_ENFANT * 2
    assert eux["majoration_duree_enfants"] == eux["majoration_duree"] == le_sien == 0
    assert moi["duree_assurance"] - eux["duree_assurance"] == le_notre - le_sien
    assert eux["decote_trimestres"] - moi["decote_trimestres"] == 1


# -- les enfants nés hors des services --------------------------------------------

def test_l_enfant_ne_avant_le_recrutement_selon_la_date_de_la_pension(temoin, nous):
    """R. 13 subordonne la bonification à l'interruption d'activité. De 2004 à
    2010, elle se prend « dans le cadre d'un congé » du statut
    (LEGIARTI000020532497) : l'enfant né avant le recrutement n'en ouvre pas,
    sauf au b bis — l'accouchement pendant les études, le recrutement dans les
    deux ans du diplôme —, que ni l'un ni l'autre ne lit. Depuis 2011, le congé
    de maternité du code de la sécurité sociale suffit (LEGIARTI000023449727),
    et l'enfant né avant la radiation en ouvre une. OpenFisca, qui ne lit pas
    le recrutement, l'accorde aux deux dates. En 2015, les deux concordent au
    centime ; en 2009, sa pension ne s'écarte de la nôtre que des huit
    trimestres de bonification, au prorata."""
    concorde = "mere_enfants_avant_recrutement_2015"
    eux, moi = temoin["profils"][concorde]["openfisca"], nous[concorde]
    assert moi["services_et_bonifications"] - moi["services"] \
        == eux["bonification_enfants"] == 8
    assert moi["duree_assurance"] == eux["duree_assurance"]
    assert moi["pension_avant_minimum"] == pytest.approx(
        eux["pension_avant_minimum"], rel=PRECISION_OPENFISCA)

    code = "mere_enfants_avant_recrutement_2009"
    entree = temoin["profils"][code]
    eux, moi = entree["openfisca"], nous[code]
    le_notre, le_sien = ECARTS[code]
    assert entree["profil"]["liquidation"] < 2011
    assert moi["services_et_bonifications"] - moi["services"] == le_notre
    assert eux["bonification_enfants"] == le_sien
    assert eux["duree_assurance"] - moi["duree_assurance"] == le_sien - le_notre
    assert moi["services"] == eux["services"]
    assert moi["taux_de_liquidation"] == pytest.approx(
        eux["taux_de_liquidation"], abs=TOLERANCE_EXACTE)
    assert moi["pension_avant_minimum"] * (moi["services"] + le_sien) / moi["services"] \
        == pytest.approx(eux["pension_avant_minimum"], rel=PRECISION_OPENFISCA)


def test_l_accouchement_avant_le_recrutement_n_ouvre_pas_la_majoration(temoin, nous):
    """L. 12 bis (LEGIARTI000006362697) : la majoration va aux femmes « ayant
    accouché postérieurement à leur recrutement ». Recrutée en 2006, la mère
    d'un enfant né en 2005 n'en a pas chez nous ; OpenFisca, qui ne lit pas le
    recrutement, lui en donne deux trimestres. Ils ne changent rien à sa
    pension : la décote est au plafond des deux côtés."""
    code = "mere_accouchement_avant_recrutement_2020"
    eux, moi = temoin["profils"][code]["openfisca"], nous[code]
    le_notre, le_sien = ECARTS[code]
    assert moi["duree_assurance"] == moi["services"] + le_notre
    assert eux["majoration_duree_enfants"] == le_sien
    assert eux["duree_assurance"] == eux["services"] + le_sien
    assert moi["decote_trimestres"] == eux["decote_trimestres"] == DECOTE_PLAFONNEE
    assert moi["pension_avant_minimum"] == pytest.approx(
        eux["pension_avant_minimum"], rel=PRECISION_OPENFISCA)


def test_la_pension_concorde_au_centime_hors_des_ecarts(temoin, nous):
    """Le bout de la chaîne, partout où aucun écart n'est déclaré ni le départ
    des parents ouvert : décote, taux, proratisation, traitement et pension."""
    for code, entree in temoin["profils"].items():
        moi, eux = nous[code], entree["openfisca"]
        if code in ECARTS or moi["depart"] is not None:
            continue
        assert moi["decote_trimestres"] == eux["decote_trimestres"], code
        assert moi["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=TOLERANCE_EXACTE), code
        assert _coefficient_de_proratisation(
            moi["services"], moi["services_et_bonifications"] - moi["services"],
            moi["proratisation"]) == pytest.approx(
                eux["coefficient_de_proratisation"], abs=TOLERANCE_EXACTE), code
        assert moi["traitement_de_reference"] == pytest.approx(
            eux["traitement_de_reference"], rel=PRECISION_OPENFISCA), code
        assert moi["pension_avant_minimum"] == pytest.approx(
            eux["pension_avant_minimum"], rel=PRECISION_OPENFISCA), code
