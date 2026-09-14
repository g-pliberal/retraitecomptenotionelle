"""Confrontation du scénario 1 à une SECONDE IMPLÉMENTATION, écrite par d'autres.

Le scénario « système actuel » est l'étalon du modèle : tous les écarts affichés
se mesurent par rapport à lui. Le vérifier en le relisant ne prouve rien — une
réimplémentation écrite par la même main hérite des mêmes hypothèses. Et aucun
simulateur officiel n'est automatisable : M@rel exige FranceConnect et le relevé
de carrière réel, sans mode anonyme ni API.

Reste OpenFisca-France-Pension, le module « retraites » de l'écosystème
OpenFisca. Ce n'est pas une source officielle, c'est un autre modèle — mais il
est écrit par d'autres, à partir des mêmes textes, et c'est exactement ce qui
manquait. La première confrontation a produit deux désaccords, un de chaque
côté : la durée de proratisation, que nous confondions avec la durée requise
(corrigé), et sa table de durée requise, qui ignore la réforme du 14 avril 2023.

**Ce test n'installe pas OpenFisca.** Il rejoue les témoins versionnés que
`scripts/fetch/openfisca_regime_general.py`, `openfisca_fonction_publique.py`
et `openfisca_arrco.py` ont figés, ce qui le rend exécutable sur un dépôt
fraîchement cloné, sans les quatre cents mégaoctets de numpy, pandas et numba.

Trois régimes sont confrontés : le régime général, la pension civile (État et
CNRACL) et l'Arrco d'avant 2019. La seconde confrontation a trouvé, comme la
première, un désaccord de chaque côté — chez nous, le barème de décote de la
fonction publique lu à l'année de liquidation au lieu de l'année d'ouverture du
droit, et le traitement de l'année d'avant ramené au départ par les prix au lieu
du point d'indice ; chez lui, un 0,65 % transcrit pour l'année 2010 là où la loi
écrit 0,625 %. La troisième n'a rien trouvé à corriger.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Simulateur

TEMOINS = Path(__file__).resolve().parent / "temoins"
TEMOIN = TEMOINS / "openfisca_regime_general.json"
TEMOIN_FONCTION_PUBLIQUE = TEMOINS / "openfisca_fonction_publique.json"
TEMOIN_ARRCO = TEMOINS / "openfisca_arrco.json"

#: Tolérance sur la durée, la décote, le taux et la proratisation : ce sont des
#: comptages et des tables, ils doivent tomber juste à l'unité près.
TOLERANCE_EXACTE = 1e-4

#: Tolérance sur le salaire annuel moyen et sur la pension, qui en découle.
#:
#: Elle valait 8 % : le modèle approchait les coefficients de revalorisation des
#: salaires portés au compte par « les salaires jusqu'en 1986, les prix depuis »,
#: une approximation qui sur-revalorise les salaires anciens de 12 à 14 % sur
#: quarante ans.
#:
#: Le modèle lit désormais les coefficients dans la circulaire annuelle de la
#: Cnav, et **c'est OpenFisca qui s'en écarte** : sa table cumulée est de 3 à
#: 5,5 % en dessous de ce que la caisse publie pour toutes les perceptions
#: postérieures à 1990 — il lui manque la revalorisation exceptionnelle de 4 %
#: du 1er juillet 2022 — et jusqu'à 17 % à côté sur les années 1950. La
#: confrontation vaut toujours, mais elle ne peut plus être une égalité sur ce
#: poste : le désaccord résiduel, de 0,16 % à 2,22 %, est celui d'OpenFisca avec
#: la source. `tests/test_simulateur.py` vérifie, lui, que le modèle reproduit
#: la colonne que la caisse a publiée.
TOLERANCE_SALAIRE = 0.03


@pytest.fixture(scope="module")
def oracle() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _notre_calcul(simulateur: Simulateur, profil: dict) -> dict[str, float]:
    """Le régime général du scénario 1, sur la carrière exacte du témoin."""
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["salaire"],
            affiliation="salarie_prive_non_cadre", trimestres_valides=4,
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    carriere = Carriere(
        annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"],
    )
    scenario = simulateur.scenario_actuel
    resultat = scenario.calculer(carriere)
    periode = simulateur.catalogue["regime_general"].periode(profil["liquidation"])
    requis, _ = scenario._duree_requise(periode, carriere)
    proratisation, _ = scenario._duree_proratisation(periode, carriere, requis)
    _, age_annulation, _ = scenario._decote(
        periode, carriere, profil["liquidation"]
    )
    base = next(
        p for p in resultat.pensions_par_regime if p.regime == "regime_general"
    )
    return {
        "duree_assurance": float(resultat.trimestres_valides),
        "salaire_de_reference": scenario.salaire_de_reference(
            "regime_general", carriere, periode, profil["liquidation"],
            True, profil["naissance"], True,
        ),
        "coefficient_de_proratisation": (
            min(resultat.trimestres_valides, proratisation) / proratisation
        ),
        "decote_trimestres": float(scenario._trimestres_de_decote(
            periode, resultat.trimestres_valides, requis,
            profil["liquidation"] - profil["naissance"], age_annulation,
        )),
        "taux_de_liquidation": resultat.taux_liquidation,
        "pension_brute": base.montant,
    }


def test_le_temoin_couvre_le_perimetre_annonce(oracle):
    """Le témoin doit dire d'où il vient, et rester dans ce qu'OpenFisca sait faire.

    Ses barèmes s'arrêtent en 2024 — valeur du point Agirc-Arrco en novembre
    2024, revalorisations CNAV en 2023 — et son Arrco est cassé dans la version
    publiée. Un profil qui déborderait ces bornes produirait une comparaison
    sans valeur, ou pas de comparaison du tout.
    """
    assert oracle["source"] == "OpenFisca-France-Pension"
    assert oracle["version"]
    assert len(oracle["profils"]) >= 8
    for code, entree in oracle["profils"].items():
        assert entree["profil"]["liquidation"] < 2025, code
        # Le garde-fou du récupérateur : un oracle silencieusement nul
        # validerait n'importe quoi.
        assert entree["openfisca"]["duree_assurance"] > 0, code
        assert entree["openfisca"]["pension_brute"] > 0, code


def test_la_duree_dassurance_concorde(oracle, simulateur):
    """Trimestres validés : les deux modèles doivent compter pareil."""
    for code, entree in oracle["profils"].items():
        nous = _notre_calcul(simulateur, entree["profil"])
        assert nous["duree_assurance"] == entree["openfisca"]["duree_assurance"], code


def test_la_decote_concorde_trimestre_par_trimestre(oracle, simulateur):
    """Le décompte des trimestres de décote, et le taux qui en découle.

    C'est le contrôle le plus exigeant du lot : il met en jeu la durée requise
    par génération, l'âge d'annulation de la décote par génération, la règle du
    minimum entre les deux décomptes, le plafond de vingt trimestres et
    l'arrondi à l'entier supérieur. Cinq tables et trois règles doivent tomber
    juste ensemble.
    """
    for code, entree in oracle["profils"].items():
        nous, eux = _notre_calcul(simulateur, entree["profil"]), entree["openfisca"]
        assert nous["decote_trimestres"] == eux["decote_trimestres"], code
        assert nous["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=TOLERANCE_EXACTE
        ), code


def test_la_proratisation_concorde(oracle, simulateur):
    """Le coefficient de proratisation, et son dénominateur.

    C'est ce contrôle qui a révélé que le modèle confondait la durée requise
    pour le taux plein et la durée maximale prise en compte par la
    proratisation, que l'article R. 351-6 fixe plus bas pour les générations
    d'avant 1949. Un assuré né en 1945 avec 156 trimestres y perdait 2,5 % de
    pension de base que le droit ne lui retire pas.
    """
    for code, entree in oracle["profils"].items():
        nous, eux = _notre_calcul(simulateur, entree["profil"]), entree["openfisca"]
        assert nous["coefficient_de_proratisation"] == pytest.approx(
            eux["coefficient_de_proratisation"], abs=TOLERANCE_EXACTE
        ), code


def test_le_salaire_de_reference_reste_proche(oracle, simulateur):
    """Le salaire annuel moyen : le seul poste où les deux modèles diffèrent.

    Il divergeait de 0,30 % à 7,55 % quand le modèle APPROCHAIT les coefficients
    de revalorisation. Il les lit maintenant dans la circulaire de la Cnav, et
    ce qui reste — de 0,16 % à 2,22 % — n'est plus notre écart mais celui
    d'OpenFisca avec la source : il manque à sa table la revalorisation
    exceptionnelle de 4 % du 1er juillet 2022.

    Le test garde donc une borne large, et ce n'est pas un relâchement : le
    contrôle serré de cette grandeur est ailleurs, dans
    `test_les_coefficients_de_revalorisation_reproduisent_la_circulaire`, qui
    oppose au modèle la colonne que la caisse a publiée.
    """
    for code, entree in oracle["profils"].items():
        nous, eux = _notre_calcul(simulateur, entree["profil"]), entree["openfisca"]
        assert nous["salaire_de_reference"] == pytest.approx(
            eux["salaire_de_reference"], rel=TOLERANCE_SALAIRE
        ), code
        # Et toujours en dessous : l'écart a un sens, il n'est pas du bruit.
        assert nous["salaire_de_reference"] <= eux["salaire_de_reference"], code


def test_la_pension_de_base_concorde(oracle, simulateur):
    """Le bout de la chaîne : deux implémentations, une pension.

    C'est le contrôle qui donne son prix à la confrontation. Salaire de
    référence, taux, coefficient de proratisation : chacun a été vérifié
    séparément, et leur produit doit tomber juste — un écart qui n'apparaîtrait
    qu'ici signalerait une règle appliquée dans le mauvais ordre.
    """
    for code, entree in oracle["profils"].items():
        nous, eux = _notre_calcul(simulateur, entree["profil"]), entree["openfisca"]
        assert nous["pension_brute"] == pytest.approx(
            eux["pension_brute"], rel=TOLERANCE_SALAIRE
        ), code


# -- la pension civile : État et CNRACL ---------------------------------------

#: Ce que le témoin appelle chaque régime, et le statut d'affiliation qui y
#: conduit dans le modèle.
AFFILIATIONS_PUBLIQUES = {
    "fonction_publique_etat": "fonctionnaire_etat",
    "cnracl": "fonctionnaire_territorial_hospitalier",
}

#: Coefficient de décote que la loi du 21 août 2003 fixe pour un droit ouvert
#: en 2010 — le cinquième huitième de point —, et celui qu'OpenFisca a
#: transcrit. Le profil est gardé exprès : la confrontation vaut en
#: connaissance de cause, et le test dit de quel côté est l'écart.
COEFFICIENT_2010_LOI = 0.00625
COEFFICIENT_2010_OPENFISCA = 0.0065
TAUX_PLEIN_PENSION_CIVILE = 0.75

#: Marge laissée au minimum garanti : OpenFisca le calcule au point d'indice de
#: l'année de liquidation, quand l'article L. 17 fige la référence au 1er
#: janvier 2004 et la revalorise comme les pensions. L'écart est le sien, et
#: il va toujours dans le même sens — le point a fait moins que les prix
#: depuis 2004, gel de 2010-2016 compris : de 4,7 % en 2010 à 8,5 % en 2012.
TOLERANCE_MINIMUM_GARANTI = 0.10


@pytest.fixture(scope="module")
def oracle_fonction_publique() -> dict:
    return json.loads(TEMOIN_FONCTION_PUBLIQUE.read_text(encoding="utf-8"))


def _annee_ouverture_du_droit(profil: dict) -> int:
    """Année où un sédentaire de ce profil atteint l'âge d'ouverture."""
    return profil["naissance"] + (60 if profil["naissance"] < 1951 else 62)


def _notre_calcul_fonction_publique(simulateur: Simulateur, profil: dict
                                    ) -> dict[str, float]:
    """La pension civile du scénario 1, sur la carrière exacte du témoin."""
    code = profil["regime"]
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["traitement"],
            affiliation=AFFILIATIONS_PUBLIQUES[code], trimestres_valides=4,
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    carriere = Carriere(
        annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"],
    )
    scenario = simulateur.scenario_actuel
    resultat = scenario.calculer(carriere)
    periode = simulateur.catalogue[code].periode(profil["liquidation"])
    requis, _ = scenario._duree_requise(periode, carriere)
    proratisation, _ = scenario._duree_proratisation(periode, carriere, requis)
    _, age_annulation, _ = scenario._decote(periode, carriere, profil["liquidation"])
    pension = next(p for p in resultat.pensions_par_regime if p.regime == code)
    # Le minimum garanti se SUBSTITUE à la pension quand il lui est supérieur,
    # et le complément est dit : la pension d'avant le plancher se retrouve en
    # le retirant.
    complement = sum(
        a.montant for a in resultat.avantages_appliques
        if a.code == "minimum_garanti"
    )
    plancher = scenario.minimum_garanti.montant(
        profil["liquidation"], resultat.trimestres_valides
    )
    return {
        "duree_assurance": float(resultat.trimestres_valides),
        "coefficient_de_proratisation": (
            min(resultat.trimestres_valides, proratisation) / proratisation
        ),
        "decote_trimestres": float(scenario._trimestres_de_decote(
            periode, resultat.trimestres_valides, requis,
            profil["liquidation"] - profil["naissance"], age_annulation,
        )),
        "taux_de_liquidation": resultat.taux_liquidation,
        "traitement_de_reference": scenario.salaire_de_reference(
            code, carriere, periode, profil["liquidation"], False,
            profil["naissance"], True,
        ),
        "pension_avant_minimum": pension.montant - complement,
        "minimum_garanti": plancher[0] if plancher else 0.0,
        "pension_brute": pension.montant,
    }


def test_le_temoin_de_la_fonction_publique_couvre_le_perimetre_annonce(
        oracle_fonction_publique):
    """Deux régimes, liquidations de 2009 à 2020, aucun relevé nul."""
    assert oracle_fonction_publique["source"] == "OpenFisca-France-Pension"
    assert oracle_fonction_publique["version"]
    profils = oracle_fonction_publique["profils"]
    assert len(profils) >= 8
    assert {e["profil"]["regime"] for e in profils.values()} == set(AFFILIATIONS_PUBLIQUES)
    for code, entree in profils.items():
        assert 2009 <= entree["profil"]["liquidation"] <= 2020, code
        # Les générations d'avant 1949 liquidant après 2013 tombent sur une
        # table de durée de service qu'OpenFisca a mal transcrite.
        assert not (entree["profil"]["naissance"] < 1949
                    and entree["profil"]["liquidation"] > 2013), code
        assert entree["openfisca"]["duree_assurance"] > 0, code
        assert entree["openfisca"]["pension_brute"] > 0, code


def test_la_duree_de_service_de_la_pension_civile_concorde(
        oracle_fonction_publique, simulateur):
    for code, entree in oracle_fonction_publique["profils"].items():
        nous = _notre_calcul_fonction_publique(simulateur, entree["profil"])
        assert nous["duree_assurance"] == entree["openfisca"]["duree_assurance"], code


def test_la_decote_de_la_pension_civile_se_lit_a_l_annee_d_ouverture_du_droit(
        oracle_fonction_publique, simulateur):
    """Le décompte des trimestres de décote, barème de l'article L. 14.

    C'est ce contrôle qui a révélé que le modèle lisait le barème à l'année de
    LIQUIDATION. Le III de l'article 66 de la loi du 21 août 2003 titre sa
    colonne « Année au cours de laquelle sont réunies les conditions
    mentionnées au I et au II de l'article L. 24 » : un sédentaire né en 1948
    réunit ces conditions en 2008, et garde 0,375 % et « limite d'âge moins
    douze trimestres » quelle que soit l'année de son départ. Parti en 2010 à
    soixante-deux ans, il n'a aucun trimestre de décote — le modèle lui en
    opposait deux, avec le barème de 2010.
    """
    for code, entree in oracle_fonction_publique["profils"].items():
        nous, eux = (_notre_calcul_fonction_publique(simulateur, entree["profil"]),
                     entree["openfisca"])
        assert nous["decote_trimestres"] == eux["decote_trimestres"], code


def test_le_taux_de_la_pension_civile_concorde_sauf_la_transcription_de_2010(
        oracle_fonction_publique, simulateur):
    """Décote et surcote ensemble : le taux de liquidation.

    Un seul écart, et il est chez OpenFisca : pour un droit ouvert en 2010, sa
    table porte 0,65 % par trimestre là où la loi écrit 0,625 %. Le profil est
    gardé, et le test vérifie que chacun des deux modèles rend exactement le
    taux que SON coefficient commande — c'est ainsi qu'on sait de quel côté
    est l'écart, et qu'il n'est que celui-là.
    """
    for code, entree in oracle_fonction_publique["profils"].items():
        profil, eux = entree["profil"], entree["openfisca"]
        nous = _notre_calcul_fonction_publique(simulateur, profil)
        if _annee_ouverture_du_droit(profil) == 2010 and eux["decote_trimestres"]:
            manquants = eux["decote_trimestres"]
            assert nous["taux_de_liquidation"] == pytest.approx(
                TAUX_PLEIN_PENSION_CIVILE * (1 - COEFFICIENT_2010_LOI * manquants),
                abs=TOLERANCE_EXACTE), code
            assert eux["taux_de_liquidation"] == pytest.approx(
                TAUX_PLEIN_PENSION_CIVILE * (1 - COEFFICIENT_2010_OPENFISCA * manquants),
                abs=TOLERANCE_EXACTE), code
            continue
        assert nous["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=TOLERANCE_EXACTE), code


def test_la_surcote_de_la_pension_civile_concorde(oracle_fonction_publique, simulateur):
    """Le témoin porte au moins un profil surcoté, et les deux la servent."""
    surcotes = [
        (code, entree) for code, entree in oracle_fonction_publique["profils"].items()
        if entree["openfisca"]["surcote_trimestres"] > 0
    ]
    assert surcotes
    for code, entree in surcotes:
        eux = entree["openfisca"]
        nous = _notre_calcul_fonction_publique(simulateur, entree["profil"])
        attendu = TAUX_PLEIN_PENSION_CIVILE * (1 + 0.0125 * eux["surcote_trimestres"])
        assert eux["decote_trimestres"] == 0, code
        assert nous["taux_de_liquidation"] == pytest.approx(attendu, abs=TOLERANCE_EXACTE), code
        assert eux["taux_de_liquidation"] == pytest.approx(attendu, abs=TOLERANCE_EXACTE), code


def test_la_proratisation_de_la_pension_civile_concorde(
        oracle_fonction_publique, simulateur):
    for code, entree in oracle_fonction_publique["profils"].items():
        nous, eux = (_notre_calcul_fonction_publique(simulateur, entree["profil"]),
                     entree["openfisca"])
        assert nous["coefficient_de_proratisation"] == pytest.approx(
            eux["coefficient_de_proratisation"], abs=TOLERANCE_EXACTE), code


def test_le_traitement_de_reference_suit_le_point_d_indice(
        oracle_fonction_publique, simulateur):
    """Le traitement de l'année d'avant, ramené à l'année du départ.

    Un fonctionnaire garde son indice : son traitement suit le point. Le
    modèle le ramenait au départ par les prix, et s'écartait d'OpenFisca de
    0,5 à 0,8 % — de tout ce que le point avait fait de moins que les prix,
    gel de 2010-2016 compris. Il suit maintenant le point, et les deux
    traitements tombent au centime.
    """
    for code, entree in oracle_fonction_publique["profils"].items():
        nous, eux = (_notre_calcul_fonction_publique(simulateur, entree["profil"]),
                     entree["openfisca"])
        assert nous["traitement_de_reference"] == pytest.approx(
            eux["traitement_de_reference"], rel=1e-6), code


def test_la_pension_civile_concorde_au_centime(oracle_fonction_publique, simulateur):
    """Traitement × taux × proratisation : le bout de la chaîne.

    Au centime près, sauf pour le droit ouvert en 2010, où l'écart est celui
    de la transcription d'OpenFisca — et il se retrouve exactement en
    substituant son coefficient au nôtre.
    """
    for code, entree in oracle_fonction_publique["profils"].items():
        profil, eux = entree["profil"], entree["openfisca"]
        nous = _notre_calcul_fonction_publique(simulateur, profil)
        notre_pension = nous["pension_avant_minimum"]
        if _annee_ouverture_du_droit(profil) == 2010 and eux["decote_trimestres"]:
            manquants = eux["decote_trimestres"]
            notre_pension *= ((1 - COEFFICIENT_2010_OPENFISCA * manquants)
                              / (1 - COEFFICIENT_2010_LOI * manquants))
        assert notre_pension == pytest.approx(eux["pension_avant_minimum"], rel=1e-6), code


def test_le_minimum_garanti_reste_proche(oracle_fonction_publique, simulateur):
    """Le plancher de l'article L. 17, sur un profil où il joue.

    OpenFisca le calcule au point d'indice de l'année de liquidation ; le
    modèle fige la référence au 1er janvier 2004 et la revalorise comme les
    pensions, ce que l'article écrit. L'écart est donc le sien, il va toujours
    dans le même sens — le point a fait moins que les prix — et il reste de
    quelques pour cent : le test le borne sans l'effacer.
    """
    joues = [
        (code, entree) for code, entree in oracle_fonction_publique["profils"].items()
        if entree["openfisca"]["minimum_garanti"] > entree["openfisca"]["pension_avant_minimum"]
    ]
    assert joues, "aucun profil où le minimum garanti se substitue à la pension"
    for code, entree in oracle_fonction_publique["profils"].items():
        eux = entree["openfisca"]
        if eux["minimum_garanti"] <= 0:
            continue
        nous = _notre_calcul_fonction_publique(simulateur, entree["profil"])
        assert nous["minimum_garanti"] == pytest.approx(
            eux["minimum_garanti"], rel=TOLERANCE_MINIMUM_GARANTI), code
        assert nous["minimum_garanti"] >= eux["minimum_garanti"], code
    for code, entree in joues:
        nous = _notre_calcul_fonction_publique(simulateur, entree["profil"])
        assert nous["pension_brute"] == pytest.approx(nous["minimum_garanti"], rel=1e-6), code
        assert entree["openfisca"]["pension_brute"] == pytest.approx(
            entree["openfisca"]["minimum_garanti"], rel=1e-6), code


# -- l'Arrco d'avant 2019 ------------------------------------------------------

@pytest.fixture(scope="module")
def oracle_arrco() -> dict:
    return json.loads(TEMOIN_ARRCO.read_text(encoding="utf-8"))


_POINTS = re.compile(r"^([\d,]+\.\d+) points ×")


def _nos_points_arrco(simulateur: Simulateur, profil: dict) -> dict[str, float]:
    """L'Arrco du scénario 1 : points acquis, valeur servie, abattement.

    Les points se lisent dans la formule que le modèle écrit pour chaque
    pension — « 1,543.91 points × valeur de service 1.2513 € » —, celle qu'on
    doit pouvoir refaire à la main. La tranche 2 des non-cadres a sa propre
    ligne, et OpenFisca additionne les deux.
    """
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["salaire"],
            affiliation="salarie_prive_non_cadre", trimestres_valides=4,
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    carriere = Carriere(
        annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"],
    )
    scenario = simulateur.scenario_actuel
    resultat = scenario.calculer(carriere)
    points, coefficient = 0.0, 1.0
    for pension in resultat.pensions_par_regime:
        if not pension.regime.startswith("arrco") or pension.montant <= 0:
            continue
        lecture = _POINTS.match(pension.detail)
        assert lecture, pension.detail
        points += float(lecture.group(1).replace(",", ""))
        if "coefficient d'anticipation" in pension.detail:
            coefficient = float(pension.detail.rsplit(" ", 1)[1])
    service = scenario.valeurs_point.service("arrco", profil["liquidation"] - 1)
    return {
        "points": points,
        "coefficient_de_minoration": coefficient,
        "valeur_du_point_au_1er_janvier": service[0] if service else 0.0,
    }


def test_le_temoin_de_l_arrco_couvre_le_perimetre_annonce(oracle_arrco):
    """Carrières d'après l'unification de 1999, liquidées avant la fusion."""
    assert oracle_arrco["source"] == "OpenFisca-France-Pension"
    assert oracle_arrco["version"]
    assert len(oracle_arrco["profils"]) >= 6
    for code, entree in oracle_arrco["profils"].items():
        assert entree["profil"]["debut"] >= 1999, code
        assert entree["profil"]["liquidation"] <= 2018, code
        assert entree["openfisca"]["points"] > 0, code
        assert entree["openfisca"]["pension_brute"] > 0, code
        assert len(entree["openfisca"]["points_annuels"]) == (
            entree["profil"]["liquidation"] - entree["profil"]["debut"]), code


def test_les_points_arrco_concordent(oracle_arrco, simulateur):
    """Cotisation → points, vingt ans de barèmes rejoués par un autre moteur.

    Taux effectif par tranche, prix d'achat du point, taux d'appel : trois
    transcriptions séparées d'OpenFisca-France, que le modèle lit, contre le
    calcul complet d'OpenFisca-France-Pension. Au millième, tranche 2 comprise.
    """
    for code, entree in oracle_arrco["profils"].items():
        nous = _nos_points_arrco(simulateur, entree["profil"])
        assert nous["points"] == pytest.approx(entree["openfisca"]["points"], rel=1e-4), code
    assert any(e["profil"]["salaire"] > 30000 for e in oracle_arrco["profils"].values()), (
        "aucun profil au-dessus du plafond : la tranche 2 n'est pas mise à l'épreuve"
    )


def test_la_valeur_de_service_arrco_concorde_a_une_convention_pres(
        oracle_arrco, simulateur):
    """La même valeur du point, lue à deux dates.

    Le dépôt retient pour chaque année la valeur EN VIGUEUR AU 31 DÉCEMBRE ;
    OpenFisca lit celle du 1er janvier de la liquidation, qui est la valeur de
    l'année précédente. Une liquidation au 1er janvier 2012 se voit servir
    1,2135 € chez lui — la valeur d'avril 2011 — et c'est exactement notre
    valeur de 2011. La chaîne des valeurs est donc la même ; seule la
    convention de millésime diffère, et elle est documentée des deux côtés.
    """
    for code, entree in oracle_arrco["profils"].items():
        nous = _nos_points_arrco(simulateur, entree["profil"])
        assert nous["valeur_du_point_au_1er_janvier"] == pytest.approx(
            entree["openfisca"]["valeur_du_point"], abs=1e-4), code


def test_la_decote_du_regime_general_qui_commande_l_arrco_concorde(
        oracle_arrco, simulateur):
    """L'abattement Arrco se lit sur les trimestres de décote du régime général."""
    for code, entree in oracle_arrco["profils"].items():
        nous = _notre_calcul(simulateur, entree["profil"])
        assert nous["decote_trimestres"] == (
            entree["openfisca"]["decote_trimestres_regime_general"]), code


def test_le_coefficient_d_anticipation_arrco_concorde_sur_les_annees_pleines(
        oracle_arrco, simulateur):
    """Le barème d'anticipation, là où les deux lectures se recouvrent.

    OpenFisca ne lit son barème que par année ENTIÈRE d'anticipation, en
    tronquant les trimestres ; l'Arrco l'écrit par trimestre, et le modèle le
    lit ainsi. Les deux coïncident quand l'anticipation tombe sur des années
    pleines, et le modèle ne peut jamais servir plus qu'OpenFisca ailleurs.
    """
    pleines = 0
    for code, entree in oracle_arrco["profils"].items():
        eux = entree["openfisca"]
        nous = _nos_points_arrco(simulateur, entree["profil"])
        if eux["decote_trimestres_regime_general"] % 4 == 0:
            pleines += 1
            assert nous["coefficient_de_minoration"] == pytest.approx(
                eux["coefficient_de_minoration"], abs=TOLERANCE_EXACTE), code
        else:
            assert nous["coefficient_de_minoration"] <= (
                eux["coefficient_de_minoration"] + TOLERANCE_EXACTE), code
    assert pleines >= 3
