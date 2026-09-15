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
`scripts/fetch/openfisca_regime_general.py`, `openfisca_fonction_publique.py`,
`openfisca_arrco.py`, `openfisca_agirc.py` et `openfisca_ircantec.py` ont figés,
ce qui le rend exécutable sur un dépôt fraîchement cloné, sans les quatre cents
mégaoctets de numpy, pandas et numba.

Cinq familles de régimes sont confrontées, et c'est tout ce qu'OpenFisca
expose : le régime général, la pension civile (État et CNRACL), l'Arrco d'avant
2019, l'Agirc des cadres et l'Ircantec des agents non titulaires. S'y ajoutent
les régimes ALIGNÉS — MSA des salariés agricoles, artisans, commerçants —, pour
lesquels il n'a aucun module et n'en a pas besoin : la loi les calcule comme le
régime général, et c'est à l'oracle du régime général qu'ils se confrontent.

Ce que chaque confrontation a trouvé, dans l'ordre où elles ont été écrites.

* **Régime général** — deux désaccords, un de chaque côté : la durée de
  proratisation, que nous confondions avec la durée requise (corrigé), et sa
  table de durée requise, qui ignore la réforme du 14 avril 2023.
* **Pension civile** — deux erreurs chez nous, le barème de décote lu à l'année
  de liquidation au lieu de l'année d'ouverture du droit et le traitement de
  l'année d'avant ramené au départ par les prix au lieu du point d'indice ; une
  chez lui, un 0,65 % transcrit pour 2010 là où la loi écrit 0,625 %.
* **Arrco** — rien à corriger, et c'est le résultat.
* **Agirc** — trois écarts, tous chez lui : son barème salarié ne suit pas le
  taux d'appel de 1989 ni le contractuel de 1994, sa tranche C est cotisée par
  le salarié dès 1948 faute d'un taux nul écrit là où le barème employeur en
  porte un, et son prix d'achat se lit au 1er janvier, soit un millésime de
  retard à partir de 2004.
* **Ircantec** — deux corrections chez nous, toutes deux lues dans les textes :
  l'assiette de la tranche B, que l'article 7 du décret n° 70-1277 limite à
  4,75 plafonds jusqu'en 2008, et le coefficient d'anticipation, que l'article
  16 de l'arrêté du 30 décembre 1970 écrit en escalier là où la fiche portait
  une pente moyenne. Chez lui, une assiette portée à huit plafonds seize ans
  trop tôt et une surcote dix fois trop forte.
* **Régimes alignés** — la MSA rend exactement la pension du régime général ;
  l'artisan et le commerçant, non, parce que le modèle coupe leur carrière à
  chaque changement de caisse et calcule deux salaires de référence là où la
  loi n'en veut qu'un.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.donnees.regimes import BORNES_ASSIETTE
from retraite_notionnelle.simulateur import Simulateur

TEMOINS = Path(__file__).resolve().parent / "temoins"
TEMOIN = TEMOINS / "openfisca_regime_general.json"
TEMOIN_FONCTION_PUBLIQUE = TEMOINS / "openfisca_fonction_publique.json"
TEMOIN_ARRCO = TEMOINS / "openfisca_arrco.json"
TEMOIN_AGIRC = TEMOINS / "openfisca_agirc.json"
TEMOIN_IRCANTEC = TEMOINS / "openfisca_ircantec.json"

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


# -- l'Agirc des cadres, 1947-2018 ---------------------------------------------

#: Taux EFFECTIFS que le barème d'OpenFisca sert sur la tranche B là où il
#: s'écarte du nôtre, et ils ne s'en écartent que deux fois. En 1989, le taux
#: d'appel de l'Agirc passe à 1,134 : son barème employeur suit — 6 % × 1,134 =
#: 6,804 % — et son barème salarié reste à 2,2 %, la valeur de 1987, au lieu de
#: 2,268 %. En 1994, son couple 8,43 / 3,63 donne 12,06 % quand le contractuel
#: de 10 % appelé à 1,21 en fait 12,10. Les profils sont gardés, et le test
#: vérifie que l'écart n'est que celui-là.
TAUX_AGIRC_OPENFISCA = {1989: 0.09004, 1994: 0.1206}

#: Même chose pour la part SALARIÉE, qui est celle qu'OpenFisca étend à tort à
#: la tranche C avant 1991 : 2,2 % en 1989 au lieu de 2,268 %.
TAUX_SALARIE_AGIRC_OPENFISCA = {1989: 0.022}

#: Année à partir de laquelle l'Agirc revalorise sa valeur de service au 1er
#: avril et non plus au 1er janvier — donc année à partir de laquelle le
#: paramètre lu au 1er janvier par OpenFisca porte le millésime précédent.
ANNEE_DU_1ER_AVRIL_SERVICE_AGIRC = 2001

#: Même bascule pour le prix d'achat, trois ans plus tard.
ANNEE_DU_1ER_AVRIL_ACHAT_AGIRC = 2004

#: Première année où l'Agirc appelle une cotisation sur la tranche C.
PREMIERE_ANNEE_TRANCHE_C = 1991

#: Tolérance des identités rejouées sur les relevés d'OpenFisca : il rend des
#: flottants simple précision, et le témoin les porte tels quels.
TOLERANCE_FLOTTANT_32 = 1e-4


@pytest.fixture(scope="module")
def oracle_agirc() -> dict:
    return json.loads(TEMOIN_AGIRC.read_text(encoding="utf-8"))


def _assiette_et_cotisation(simulateur: Simulateur, code: str, annee: int,
                            salaire: float) -> dict[str, float]:
    """L'assiette de chaque tranche du régime, et la cotisation qui en sort.

    Le moteur ne les publie pas séparément — il n'en publie que des points.
    Le test les recompose depuis la fiche du régime, parce que c'est là que
    porte la confrontation : ce sont les barèmes de cotisation des deux
    modèles qu'il s'agit d'opposer, avant qu'un prix d'achat ne les traduise.
    """
    plafond = simulateur.macro.plafond_securite_sociale(annee)
    tranches: dict[str, float] = {}
    parts: dict[str, float] = {}
    cotisation = 0.0
    for periode in simulateur.catalogue[code].periodes:
        if not (periode.debut <= annee <= (periode.fin or 9999)):
            continue
        bas, haut = BORNES_ASSIETTE[periode.assiette]
        assiette = max(
            0.0, min(salaire, (haut * plafond) if haut else salaire) - bas * plafond
        )
        tranches[periode.assiette] = assiette
        parts[periode.assiette] = periode.part_salariale
        cotisation += assiette * periode.taux_cotisation_retraite
    return {"tranches": tranches, "cotisation": cotisation,
            "parts_salariales": parts}


def _taux_de_la_tranche(simulateur: Simulateur, code: str, annee: int,
                        assiette: str) -> float:
    for periode in simulateur.catalogue[code].periodes:
        if (periode.debut <= annee <= (periode.fin or 9999)
                and periode.assiette == assiette):
            return periode.taux_cotisation_retraite
    return 0.0


def _nos_points(simulateur: Simulateur, profil: dict, regime: str,
                affiliation: str) -> dict[str, float]:
    """Points acquis et coefficient d'anticipation, lus dans la formule servie.

    Comme pour l'Arrco : la formule que le modèle écrit sous chaque pension est
    celle qu'on doit pouvoir refaire à la main, et c'est donc elle qu'on
    oppose à l'oracle.
    """
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["salaire"], affiliation=affiliation,
            trimestres_valides=4,
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    carriere = Carriere(
        annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"],
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    points, coefficient = 0.0, 1.0
    for pension in resultat.pensions_par_regime:
        if pension.regime != regime or pension.montant <= 0:
            continue
        lecture = _POINTS.match(pension.detail)
        assert lecture, pension.detail
        points += float(lecture.group(1).replace(",", ""))
        if "coefficient d'anticipation" in pension.detail:
            coefficient = float(pension.detail.rsplit(" ", 1)[1])
    return {"points": points, "coefficient_de_minoration": coefficient}


def test_le_temoin_de_l_agirc_couvre_le_perimetre_annonce(oracle_agirc):
    """Dix profils de cadres, aucun relevé nul, aucune liquidation hors barème."""
    assert oracle_agirc["source"] == "OpenFisca-France-Pension"
    assert oracle_agirc["version"]
    profils = oracle_agirc["profils"]
    assert len(profils) >= 10
    for code, entree in profils.items():
        profil, mesures = entree["profil"], entree["openfisca"]
        assert profil["liquidation"] < 2025, code
        assert profil["debut"] >= 1948, code
        assert mesures["points"] > 0, code
        assert mesures["pension_brute"] > 0, code
        assert len(mesures["points_annuels"]) == (
            profil["liquidation"] - profil["debut"]), code


def test_le_prix_d_achat_agirc_concorde_a_une_date_pres(oracle_agirc, simulateur):
    """Prix d'achat et taux d'appel, année par année, sur les dix profils.

    OpenFisca achète ses points comme nous — cotisation ÷ (taux d'appel × prix
    d'achat) —, et rejouer cette division sur ses propres relevés dit si les
    deux séries sont la même. Elles le sont, à une date près : l'Agirc a
    déplacé la revalorisation de son salaire de référence du 1er janvier au
    1er avril en 2004, le dépôt retient le prix en vigueur au 31 décembre —
    celui qui vaut pour les salaires de l'année — et OpenFisca lit le
    paramètre au 1er janvier, donc le millésime précédent. Le test vérifie
    que l'écart n'est QUE ce décalage, et qu'il ne commence pas avant 2004.
    """
    decales = 0
    for code, entree in oracle_agirc["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        for annee in range(profil["debut"], profil["liquidation"]):
            cotisation = mesures["cotisations_annuelles"][str(annee)]
            leurs = mesures["points_annuels"][str(annee)]
            millesime = (annee - 1 if annee >= ANNEE_DU_1ER_AVRIL_ACHAT_AGIRC
                         else annee)
            # Le prix d'achat est lu au millésime qu'OpenFisca sert, le taux
            # d'appel à l'année courante : c'est lui qui ne bouge pas.
            prix = simulateur.scenario_actuel.valeurs_point.achat(
                "agirc", millesime)[0]
            appel = simulateur.scenario_actuel.valeurs_point.achat("agirc", annee)[1]
            assert cotisation / (appel * prix) == pytest.approx(
                leurs, rel=TOLERANCE_FLOTTANT_32), (code, annee)
            decales += millesime != annee
    assert decales, "aucun profil ne franchit 2004 : le décalage n'est pas mis à l'épreuve"


def test_la_cotisation_agirc_concorde_sauf_deux_taux(oracle_agirc, simulateur):
    """Le barème de cotisation, opposé au sien année par année.

    Il tombe juste partout, sauf deux fois, et les deux sont chez lui : son
    barème salarié ne suit pas le taux d'appel de 1989 et son couple de 1994
    perd quatre centièmes de point. Le profil qui traverse la tranche C est
    traité à part, dans le test suivant.
    """
    vus = set()
    for code, entree in oracle_agirc["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        if code.startswith("tranche_c"):
            continue
        for annee in range(profil["debut"], profil["liquidation"]):
            nous = _assiette_et_cotisation(simulateur, "agirc", annee,
                                           profil["salaire"])
            assert not nous["tranches"].get("tranche_c"), (code, annee)
            attendu = nous["cotisation"]
            if annee in TAUX_AGIRC_OPENFISCA:
                attendu = (nous["tranches"]["tranche_b"]
                           * TAUX_AGIRC_OPENFISCA[annee])
                vus.add(annee)
            assert mesures["cotisations_annuelles"][str(annee)] == pytest.approx(
                attendu, rel=TOLERANCE_FLOTTANT_32), (code, annee)
    assert vus == set(TAUX_AGIRC_OPENFISCA), (
        "les deux années où son barème retarde ne sont pas traversées"
    )


def test_la_tranche_c_de_l_agirc_est_cotisee_chez_lui_des_1948(
        oracle_agirc, simulateur):
    """Ce qu'un cadre payé plus de quatre plafonds paie, chez lui et chez nous.

    L'Agirc n'appelle de cotisation sur la tranche C qu'à compter de 1991.
    Le barème EMPLOYEUR d'OpenFisca l'écrit — taux nul de 1948 à 1990 — mais
    son barème SALARIÉ laisse la case vide, et OpenFisca lit une case vide
    comme une tranche absente : le taux de la tranche B s'étend alors jusqu'à
    huit plafonds. Le test reconstitue exactement cette cotisation
    fantôme — part salariale de la tranche B appliquée à la tranche C — et
    vérifie qu'elle explique tout l'écart, année par année.
    """
    entrees = [(c, e) for c, e in oracle_agirc["profils"].items()
               if c.startswith("tranche_c")]
    assert entrees, "aucun profil au-dessus de quatre plafonds"
    for code, entree in entrees:
        profil, mesures = entree["profil"], entree["openfisca"]
        avant_1991 = 0
        for annee in range(profil["debut"], profil["liquidation"]):
            nous = _assiette_et_cotisation(simulateur, "agirc", annee,
                                           profil["salaire"])
            tranche_b = nous["tranches"]["tranche_b"]
            tranche_c = nous["tranches"].get("tranche_c", 0.0)
            taux_b = TAUX_AGIRC_OPENFISCA.get(
                annee, _taux_de_la_tranche(simulateur, "agirc", annee, "tranche_b")
            )
            if annee >= PREMIERE_ANNEE_TRANCHE_C:
                attendu = tranche_b * taux_b + tranche_c * _taux_de_la_tranche(
                    simulateur, "agirc", annee, "tranche_c"
                )
            else:
                # Sa tranche B s'étend à huit plafonds : au-delà de quatre, il
                # ne prélève que la part salariale, l'employeur ayant un taux
                # nul écrit.
                plafond = simulateur.macro.plafond_securite_sociale(annee)
                fantome = max(0.0, min(profil["salaire"], 8 * plafond) - 4 * plafond)
                taux_salarie = TAUX_SALARIE_AGIRC_OPENFISCA.get(
                    annee, taux_b * nous["parts_salariales"]["tranche_b"]
                )
                attendu = tranche_b * taux_b + fantome * taux_salarie
                avant_1991 += fantome > 0
            assert mesures["cotisations_annuelles"][str(annee)] == pytest.approx(
                attendu, rel=TOLERANCE_FLOTTANT_32), (code, annee)
        assert avant_1991 >= 5, code


def test_les_points_agirc_concordent(oracle_agirc, simulateur):
    """Le bout de la chaîne, sur les profils que rien ne sépare.

    Trois profils ne traversent ni 1989, ni 1994, ni la tranche C, ni le
    changement de date de 2004 : sur eux, les deux moteurs doivent rendre le
    même nombre de points, au millième. Les sept autres portent chacun un des
    trois écarts, et le test vérifie que le SENS de chacun est le bon — les
    deux taux en retard font servir MOINS de points à OpenFisca, et de peu ;
    la tranche C fantôme et le prix d'achat d'un millésime en arrière lui en
    font servir davantage.
    """
    exacts = 0
    for code, entree in oracle_agirc["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        nous = _nos_points(simulateur, profil, "agirc", "salarie_prive_cadre")
        annees = set(range(profil["debut"], profil["liquidation"]))
        sert_plus = (code.startswith("tranche_c")
                     or profil["liquidation"] > ANNEE_DU_1ER_AVRIL_ACHAT_AGIRC)
        if not sert_plus and not annees & set(TAUX_AGIRC_OPENFISCA):
            exacts += 1
            assert nous["points"] == pytest.approx(
                mesures["points"], rel=1e-4), code
        elif sert_plus:
            assert mesures["points"] > nous["points"] > 0, code
        else:
            assert 0 < mesures["points"] < nous["points"], code
            assert nous["points"] / mesures["points"] - 1 < 1e-3, code
    assert exacts >= 3


def test_la_valeur_de_service_agirc_suit_la_date_de_revalorisation(
        oracle_agirc, simulateur):
    """La même chaîne de valeurs, lue à deux dates.

    Le dépôt retient la valeur en vigueur au 31 décembre, OpenFisca celle du
    1er janvier de la liquidation. Tant que l'Agirc revalorise au 1er janvier
    — jusqu'en 2000 —, les deux lectures donnent le même millésime ; à partir
    de 2001, où elle passe au 1er avril, la sienne est celle de l'année
    précédente. Un seul paramètre sépare donc les deux séries : la date, et
    le témoin la met à l'épreuve des deux côtés.
    """
    des_deux_cotes = set()
    for code, entree in oracle_agirc["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        liquidation = profil["liquidation"]
        millesime = (liquidation - 1
                     if liquidation >= ANNEE_DU_1ER_AVRIL_SERVICE_AGIRC
                     else liquidation)
        service = simulateur.scenario_actuel.valeurs_point.service("agirc", millesime)
        assert service is not None, code
        assert service[0] == pytest.approx(
            mesures["valeur_du_point"], abs=1e-4), code
        des_deux_cotes.add(millesime == liquidation)
    assert des_deux_cotes == {True, False}, (
        "les profils ne couvrent pas les deux conventions de date"
    )


def test_la_decote_du_regime_general_qui_commande_l_agirc_concorde(
        oracle_agirc, simulateur):
    """L'abattement Agirc se lit sur les trimestres de décote du régime général."""
    for code, entree in oracle_agirc["profils"].items():
        nous = _notre_calcul(simulateur, entree["profil"])
        assert nous["decote_trimestres"] == (
            entree["openfisca"]["decote_trimestres_regime_general"]), code


def test_le_coefficient_d_anticipation_agirc_concorde(oracle_agirc, simulateur):
    """Le barème d'anticipation de l'Agirc, celui de l'Arrco à l'identique.

    Il se lit par année entière chez lui, par trimestre chez nous : les dix
    profils tombent sur des années pleines, et les deux coefficients doivent
    alors coïncider exactement.
    """
    for code, entree in oracle_agirc["profils"].items():
        eux = entree["openfisca"]
        assert eux["decote_trimestres_regime_general"] % 4 == 0, code
        nous = _nos_points(simulateur, entree["profil"], "agirc",
                           "salarie_prive_cadre")
        assert nous["coefficient_de_minoration"] == pytest.approx(
            eux["coefficient_de_minoration"], abs=TOLERANCE_EXACTE), code


# -- l'Ircantec des agents non titulaires --------------------------------------

#: Seule année où le barème d'OpenFisca RETARDE : il prolonge en 1991 les taux
#: de 1989, quand la Caisse des dépôts — qui gère le régime — donne 5,28 % sur
#: la tranche A et 16,42 % sur la tranche B. C'est aussi l'année de son seul
#: désaccord de taux d'appel, 1,09 contre 1,173, que
#: `scripts/fetch/cdc_ircantec.py` avait déjà relevé.
ANNEE_DU_BAREME_EN_RETARD = 1991
TAUX_IRCANTEC_1989 = (0.04905, 0.1526)

#: Ailleurs, les deux barèmes ne diffèrent que par un ARRONDI, et il est du
#: côté du producteur : la Caisse des dépôts publie le taux appelé arrondi au
#: dix-millième — 5,63 % de 1992 à 2010 —, OpenFisca sert le produit exact du
#: contractuel par le taux d'appel, 4,5 % × 1,25 = 5,625 %. L'écart vaut cinq
#: cent-millièmes de taux, soit un millième et demi de la cotisation au pire —
#: la tranche A de 1989, dont le taux est le plus bas des trois concernés.
ECART_D_ARRONDI_IRCANTEC = 1.5e-3

#: Année du seul désaccord de taux d'appel entre la Caisse des dépôts (1,173)
#: et OpenFisca (1,09), déjà relevé par `scripts/fetch/cdc_ircantec.py`.
ANNEE_DU_TAUX_D_APPEL_CONTESTE = 1991

#: Année à partir de laquelle l'Ircantec revalorise sa valeur de service au 1er
#: avril et non plus au 1er janvier : le paramètre lu au 1er janvier porte
#: alors le millésime précédent.
ANNEE_DU_1ER_AVRIL_IRCANTEC = 2009

#: Année où OpenFisca porte l'assiette de la tranche B de 4,75 à huit plafonds.
#: Le décret n° 2008-996 du 23 septembre 2008 l'y porte seize ans plus tard.
ANNEE_DES_HUIT_PLAFONDS_OPENFISCA = 1992

#: Première année où le décret applique les huit plafonds, au 1er janvier
#: suivant la publication.
ANNEE_DES_HUIT_PLAFONDS_DECRET = 2009

#: Majoration par trimestre de surcote que sert OpenFisca, et celle que
#: l'arrêté écrit : « le nombre total de points est majoré de 0,75 % par
#: trimestre entier » (article 16, paragraphe 4). Son paramètre porte dix fois
#: cela. Le modèle, lui, n'en sert aucune — voir `limites.md` §3.
SURCOTE_IRCANTEC_OPENFISCA = 0.075
SURCOTE_IRCANTEC_ARRETE = 0.0075


def _cotisation_ircantec(simulateur: Simulateur, salaire: float, annee: int,
                         plafonds: float) -> float:
    """La cotisation Ircantec d'une année, l'assiette bornée à ``plafonds``.

    La borne est le paramètre du test : le décret en écrit 4,75 jusqu'en 2008,
    OpenFisca huit à partir de 1992. Tout le reste — les deux taux, le
    découpage des tranches — est lu dans la fiche du régime, si bien que le
    seul écart que la comparaison peut faire apparaître est celui-là.
    """
    plafond = simulateur.macro.plafond_securite_sociale(annee)
    cotisation = 0.0
    for periode in simulateur.catalogue["ircantec"].periodes:
        if not (periode.debut <= annee <= (periode.fin or 9999)):
            continue
        bas, _ = BORNES_ASSIETTE[periode.assiette]
        haut = 1.0 if periode.assiette == "tranche_1" else plafonds
        taux = periode.taux_cotisation_retraite
        if annee == ANNEE_DU_BAREME_EN_RETARD:
            taux = TAUX_IRCANTEC_1989[0 if periode.assiette == "tranche_1" else 1]
        cotisation += max(
            0.0, min(salaire, haut * plafond) - bas * plafond
        ) * taux
    return cotisation


@pytest.fixture(scope="module")
def oracle_ircantec() -> dict:
    return json.loads(TEMOIN_IRCANTEC.read_text(encoding="utf-8"))


def test_le_temoin_de_l_ircantec_couvre_le_perimetre_annonce(oracle_ircantec):
    """Onze profils d'agents non titulaires, tous postérieurs à 1971.

    Avant 1971, le dépôt a deux régimes — l'IPACTE au-dessus du plafond,
    l'IGRANTE en dessous — quand OpenFisca n'en a qu'un : la comparaison n'y
    porterait sur rien de commun.
    """
    assert oracle_ircantec["source"] == "OpenFisca-France-Pension"
    assert oracle_ircantec["version"]
    profils = oracle_ircantec["profils"]
    assert len(profils) >= 10
    for code, entree in profils.items():
        profil, mesures = entree["profil"], entree["openfisca"]
        assert profil["debut"] >= 1971, code
        assert profil["liquidation"] < 2025, code
        assert mesures["points"] > 0, code
        assert mesures["pension_brute"] > 0, code
        assert len(mesures["points_annuels"]) == (
            profil["liquidation"] - profil["debut"]), code


def test_le_prix_du_point_ircantec_concorde_sauf_le_taux_d_appel_de_1991(
        oracle_ircantec, simulateur):
    """Salaire de référence et taux d'appel, année par année, sur onze profils.

    L'Ircantec achète ses points comme nous — cotisation ÷ (taux d'appel ×
    salaire de référence) —, et rejouer cette division sur ses propres relevés
    dit si les deux séries sont la même. Elles le sont sur toute la période,
    sauf une année : 1991, où la Caisse des dépôts publie un taux d'appel de
    1,173 et OpenFisca 1,09. Le dépôt suit le producteur ; ce test constate
    que c'est bien là, et seulement là, que les deux séries divergent.
    """
    contestees = 0
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        for annee in range(profil["debut"], profil["liquidation"]):
            reference, appel, _ = simulateur.scenario_actuel.valeurs_point.achat(
                "ircantec", annee
            )
            cotisation = mesures["cotisations_annuelles"][str(annee)]
            leurs = mesures["points_annuels"][str(annee)]
            if annee == ANNEE_DU_TAUX_D_APPEL_CONTESTE:
                contestees += 1
                assert leurs > cotisation / (appel * reference), (code, annee)
                continue
            assert cotisation / (appel * reference) == pytest.approx(
                leurs, rel=TOLERANCE_FLOTTANT_32), (code, annee)
    assert contestees, "aucun profil ne traverse 1991"


def test_la_cotisation_ircantec_concorde_sauf_un_arrondi(
        oracle_ircantec, simulateur):
    """Le barème des deux tranches, opposé au sien année par année.

    Les deux barèmes tombent d'accord à l'arrondi du producteur près — un
    millième de la cotisation — sur toute la période, sauf une année : 1991,
    où sa table prolonge les taux de 1989. Là, l'accord redevient exact dès
    qu'on lui substitue ce barème-là. Le profil qui dépasse 4,75 plafonds est
    traité à part, dans le test suivant.
    """
    retards = 0
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        if code.startswith("tranche_b_1992"):
            continue
        for annee in range(profil["debut"], profil["liquidation"]):
            plafonds = BORNES_ASSIETTE[
                "tranche_2_ircantec" if annee < ANNEE_DES_HUIT_PLAFONDS_DECRET
                else "tranche_2"][1]
            attendu = _cotisation_ircantec(simulateur, profil["salaire"], annee,
                                           plafonds)
            tolerance = (TOLERANCE_FLOTTANT_32 if annee == ANNEE_DU_BAREME_EN_RETARD
                         else ECART_D_ARRONDI_IRCANTEC)
            retards += annee == ANNEE_DU_BAREME_EN_RETARD
            assert mesures["cotisations_annuelles"][str(annee)] == pytest.approx(
                attendu, rel=tolerance), (code, annee)
    assert retards, "aucun profil ne traverse 1991"


def test_le_taux_appele_ircantec_est_celui_du_producteur_arrondi(
        oracle_ircantec, simulateur):
    """Là où l'assiette tient dans la tranche A, le taux se lit directement.

    Un salaire sous le plafond ne cotise que sur la tranche A : la cotisation
    divisée par le salaire EST le taux appelé, et on peut donc opposer les
    deux chiffres sans passer par une somme de tranches. Le sien, arrondi au
    dix-millième, est exactement celui que publie la Caisse des dépôts — ce
    qui établit que l'écart du test précédent est bien un arrondi, et non deux
    séries différentes.
    """
    lus = 0
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        for annee in range(profil["debut"], profil["liquidation"]):
            if annee == ANNEE_DU_BAREME_EN_RETARD:
                continue
            plafond = simulateur.macro.plafond_securite_sociale(annee)
            if profil["salaire"] > plafond:
                continue
            implique = mesures["cotisations_annuelles"][str(annee)] / profil["salaire"]
            publie = _taux_de_la_tranche(simulateur, "ircantec", annee, "tranche_1")
            # « Arrondi au dix-millième » : la moitié d'un dix-millième sépare
            # au plus les deux lectures. On l'écrit ainsi plutôt qu'avec
            # `round`, qui tranche les demis à sa façon.
            assert abs(implique - publie) <= 5e-5 + TOLERANCE_EXACTE * 1e-3, (
                code, annee, implique, publie)
            lus += 1
    assert lus >= 20


def test_l_assiette_ircantec_s_arrete_a_4_75_plafonds_jusqu_en_2008(
        oracle_ircantec, simulateur):
    """Ce qu'un contractuel payé plus de 4,75 plafonds cotise, chez lui et chez nous.

    L'article 7 du décret n° 70-1277 limite l'assiette à « 4,75 fois le
    plafond fixé pour les cotisations de retraite du régime général » ; le
    décret n° 2008-996 du 23 septembre 2008 la porte à huit. OpenFisca l'y
    porte en 1992, seize ans trop tôt. Le test reconstitue exactement la
    tranche qu'il cotise en trop — de 4,75 à huit plafonds, au taux de la
    tranche B — et vérifie qu'avant 1992 et depuis 2009 les deux barèmes
    tombent d'accord au centime.
    """
    entrees = [(c, e) for c, e in oracle_ircantec["profils"].items()
               if c.startswith("tranche_b_1992")]
    assert entrees, "aucun profil au-dessus de 4,75 plafonds"
    for code, entree in entrees:
        profil, mesures = entree["profil"], entree["openfisca"]
        accords, ecarts = 0, 0
        for annee in range(profil["debut"], profil["liquidation"]):
            leur_borne = (8.0 if annee >= ANNEE_DES_HUIT_PLAFONDS_OPENFISCA
                          else BORNES_ASSIETTE["tranche_2_ircantec"][1])
            notre_borne = BORNES_ASSIETTE[
                "tranche_2_ircantec" if annee < ANNEE_DES_HUIT_PLAFONDS_DECRET
                else "tranche_2"][1]
            tolerance = (TOLERANCE_FLOTTANT_32 if annee == ANNEE_DU_BAREME_EN_RETARD
                         else ECART_D_ARRONDI_IRCANTEC)
            assert mesures["cotisations_annuelles"][str(annee)] == pytest.approx(
                _cotisation_ircantec(simulateur, profil["salaire"], annee,
                                     leur_borne),
                rel=tolerance), (code, annee)
            if leur_borne == notre_borne:
                accords += 1
            else:
                # Le salaire dépasse les deux bornes : l'écart est tout entier
                # la tranche que le décret n'ouvre pas encore.
                assert mesures["cotisations_annuelles"][str(annee)] > (
                    _cotisation_ircantec(simulateur, profil["salaire"], annee,
                                         notre_borne) * 1.3), (code, annee)
                ecarts += 1
        assert accords >= 10, code
        assert ecarts >= 10, code


def test_les_points_ircantec_concordent(oracle_ircantec, simulateur):
    """Le bout de la chaîne : dix profils, deux tranches, quarante ans de barèmes.

    Une seule chose sépare les deux totaux sur les profils qui restent sous
    4,75 plafonds : le taux d'appel contesté de 1991 et l'arrondi de la
    tranche A en 1989-1990, qui pèsent ensemble moins d'un pour mille. Le
    profil qui dépasse l'assiette du décret est exclu — le test précédent dit
    ce qu'il vaut, et de combien.
    """
    compares = 0
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        nous = _nos_points(simulateur, profil, "ircantec", "contractuel_public")
        if code.startswith("tranche_b_1992"):
            assert mesures["points"] > nous["points"] * 1.3, code
            continue
        compares += 1
        assert nous["points"] == pytest.approx(mesures["points"], rel=1e-3), code
    assert compares >= 9


def test_le_coefficient_d_anticipation_ircantec_suit_l_arrete_de_1970(
        oracle_ircantec, simulateur):
    """Le barème de l'article 16, et c'est ce test qui a corrigé le modèle.

    Le modèle abattait 1,1 % par trimestre d'anticipation. L'arrêté du
    30 décembre 1970 écrit un escalier : 0,01 par trimestre sur les trois
    années les plus proches de l'âge normal, 0,012 5 sur les deux suivantes,
    0,017 5 au-delà — les paliers mêmes de l'Agirc-Arrco. Le taux moyen
    tombait juste à zéro et à cinq ans d'anticipation, et nulle part entre les
    deux : à treize trimestres il retirait 14,3 % là où l'arrêté en retire
    13,25.
    """
    intermediaires = 0
    for code, entree in oracle_ircantec["profils"].items():
        eux = entree["openfisca"]
        if eux["surcote_trimestres_regime_general"] > 0:
            continue
        nous = _nos_points(simulateur, entree["profil"], "ircantec",
                           "contractuel_public")
        assert nous["coefficient_de_minoration"] == pytest.approx(
            eux["coefficient_de_minoration"], abs=TOLERANCE_EXACTE), code
        if 0 < eux["decote_trimestres_regime_general"] % 4:
            intermediaires += 1
    assert intermediaires >= 2, (
        "aucun profil ne tombe entre deux marches : l'escalier n'est pas "
        "distingué de la pente moyenne"
    )


def test_la_surcote_ircantec_est_dix_fois_trop_forte_chez_lui(
        oracle_ircantec, simulateur):
    """Le seul poste où OpenFisca sert plus que le droit, et de loin.

    Le paragraphe 4 de l'article 16 majore le total des points « de 0,75 %
    par trimestre entier écoulé entre le soixante-cinquième anniversaire de
    l'assuré et la date d'entrée en jouissance » ; son paramètre porte 0,075.
    Une année de surcote y vaut +30 % de pension.

    Le modèle, lui, n'en sert AUCUNE : la fiche de l'Ircantec ne porte pas de
    surcote, et `limites.md` §3 dit ce que cela coûte. Le test fige les deux
    lectures pour que la première correction se voie.
    """
    surcotes = [
        (code, entree) for code, entree in oracle_ircantec["profils"].items()
        if entree["openfisca"]["surcote_trimestres_regime_general"] > 0
    ]
    assert surcotes, "aucun profil surcoté"
    for code, entree in surcotes:
        eux = entree["openfisca"]
        trimestres = eux["surcote_trimestres_regime_general"]
        assert eux["decote_trimestres_regime_general"] == 0, code
        assert eux["coefficient_de_minoration"] == pytest.approx(
            1 + SURCOTE_IRCANTEC_OPENFISCA * trimestres, abs=TOLERANCE_EXACTE), code
        nous = _nos_points(simulateur, entree["profil"], "ircantec",
                           "contractuel_public")
        assert nous["coefficient_de_minoration"] == 1.0, code
        # Ce que l'arrêté donnerait, et que ni l'un ni l'autre ne sert.
        assert 1 + SURCOTE_IRCANTEC_ARRETE * trimestres < (
            eux["coefficient_de_minoration"]), code


def test_la_valeur_de_service_ircantec_suit_la_date_de_revalorisation(
        oracle_ircantec, simulateur):
    """La même chaîne de valeurs, lue à deux dates.

    Le dépôt retient la valeur en vigueur au 31 décembre, OpenFisca celle du
    1er janvier de la liquidation. Tant que l'Ircantec revalorise au 1er
    janvier — jusqu'en 2008 —, les deux lectures donnent le même millésime ;
    depuis 2009, où elle passe au 1er avril, la sienne est celle de l'année
    précédente.
    """
    des_deux_cotes = set()
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        liquidation = profil["liquidation"]
        millesime = (liquidation - 1 if liquidation >= ANNEE_DU_1ER_AVRIL_IRCANTEC
                     else liquidation)
        service = simulateur.scenario_actuel.valeurs_point.service(
            "ircantec", millesime
        )
        assert service is not None, code
        assert service[0] == pytest.approx(
            mesures["valeur_du_point"], abs=1e-5), code
        des_deux_cotes.add(millesime == liquidation)
    assert des_deux_cotes == {True, False}


def test_la_decote_du_regime_general_qui_commande_l_ircantec_concorde(
        oracle_ircantec, simulateur):
    """L'abattement Ircantec se lit sur les trimestres de décote du régime général."""
    for code, entree in oracle_ircantec["profils"].items():
        profil = dict(entree["profil"])
        nous = _notre_calcul(simulateur, profil)
        assert nous["decote_trimestres"] == (
            entree["openfisca"]["decote_trimestres_regime_general"]), code


# -- les régimes alignés : MSA des salariés, artisans, commerçants --------------

#: Statuts dont le régime de base est ALIGNÉ sur le régime général par la loi,
#: et les régimes que le modèle leur donne. « Aligné » n'est pas une image,
#: c'est un renvoi d'article à article : L. 742-3 du code rural rend au régime
#: des assurances sociales agricoles le titre V du livre III du code de la
#: sécurité sociale, qui est l'assurance vieillesse du régime général, et
#: L. 634-2 du code de la sécurité sociale calcule les pensions des artisans et
#: des commerçants « dans les conditions définies […] du premier au quatrième
#: alinéas de l'article L. 351-1 ». Leur pension se confronte donc à l'oracle
#: du régime général, sur la même carrière, sans qu'aucun module supplémentaire
#: d'OpenFisca soit nécessaire — il n'en a d'ailleurs aucun.
AFFILIATIONS_ALIGNEES = {
    "salarie_agricole": ("msa_salaries",),
    "artisan": ("cancava", "rsi", "regime_general"),
    "commercant": ("organic", "rsi", "regime_general"),
}


def _notre_pension_alignee(simulateur: Simulateur, profil: dict,
                           affiliation: str) -> dict[str, float]:
    """La pension de base d'un statut aligné, tous régimes de base confondus."""
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["salaire"], affiliation=affiliation,
            trimestres_valides=4,
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    carriere = Carriere(
        annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"],
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    codes = set(AFFILIATIONS_ALIGNEES[affiliation])
    parts = [p for p in resultat.pensions_par_regime
             if p.regime in codes and p.montant > 0]
    return {
        "montant": sum(p.montant for p in parts),
        "morceaux": len(parts),
        "trimestres": float(resultat.trimestres_valides),
        "taux_de_liquidation": resultat.taux_liquidation,
    }


def test_la_msa_des_salaries_agricoles_reproduit_le_regime_general(
        oracle, simulateur):
    """Le régime des salariés agricoles, opposé à l'oracle du régime général.

    « Les prestations sont calculées comme au régime général » : l'alignement
    est dans la loi, mais rien ne vérifiait qu'il était dans le modèle. Il
    aurait pu ne pas l'être — l'action 3 de la feuille de route a montré que
    les TAUX DE COTISATION agricoles, eux, n'ont été alignés qu'en 2014, alors
    que le dépôt les croyait alignés depuis toujours.

    Sur les dix profils de l'oracle, la MSA rend exactement la pension du
    régime général : même salaire de référence, même taux, même coefficient de
    proratisation. Sa confrontation à OpenFisca est donc celle du régime
    général, à la virgule près — 1 678 770 retraités de droit direct (série
    certifiée du dépôt, 2024) entrent ainsi dans le périmètre contrôlé, sans
    qu'OpenFisca ait de module pour eux.
    """
    for code, entree in oracle["profils"].items():
        profil = entree["profil"]
        nous = _notre_pension_alignee(simulateur, profil, "salarie_agricole")
        reference = _notre_calcul(simulateur, profil)
        assert nous["morceaux"] == 1, code
        assert nous["montant"] == pytest.approx(
            reference["pension_brute"], rel=1e-9), code
        assert nous["trimestres"] == reference["duree_assurance"], code
        assert nous["taux_de_liquidation"] == pytest.approx(
            entree["openfisca"]["taux_de_liquidation"], abs=TOLERANCE_EXACTE), code
        assert nous["montant"] == pytest.approx(
            entree["openfisca"]["pension_brute"], rel=TOLERANCE_SALAIRE), code
        assert nous["montant"] <= entree["openfisca"]["pension_brute"], code


def test_les_regimes_alignes_des_independants_sont_coupes_a_la_succession(
        oracle, simulateur):
    """Ce que la confrontation trouve chez l'artisan, et qui n'est pas aligné.

    L'artisan et le commerçant relèvent d'un régime aligné, eux aussi : leur
    pension devrait donc, à carrière identique, être celle du régime général.
    Elle ne l'est pas, et la cause n'est pas le barème — le taux de
    liquidation et le décompte des trimestres tombent juste — mais la
    SUCCESSION des caisses. La CANCAVA devient le RSI en 2006, le RSI est
    absorbé par le régime général en 2018 : le modèle liquide ces trois
    régimes séparément, chacun sur ses seules années, et calcule donc DEUX
    salaires de référence là où la caisse n'en calculerait qu'un.

    Le test mesure ce que cela coûte plutôt que de le taire : la césure joue
    dans les deux sens — les vingt-cinq meilleures années de chaque morceau
    peuvent être meilleures que celles de la carrière entière — et l'écart va
    de −7,2 % à +0,3 %. C'est la limite « coordination interrégimes » de
    `limites.md` §3, et elle est plus large qu'un polypensionnat : un régime
    et celui qui lui succède ne sont pas deux régimes.
    """
    coupes, ecarts = 0, []
    for code, entree in oracle["profils"].items():
        profil = entree["profil"]
        reference = _notre_calcul(simulateur, profil)
        for affiliation in ("artisan", "commercant"):
            nous = _notre_pension_alignee(simulateur, profil, affiliation)
            # Ce qui n'est pas perdu : la durée et le taux.
            assert nous["trimestres"] == reference["duree_assurance"], (code, affiliation)
            assert nous["taux_de_liquidation"] == pytest.approx(
                entree["openfisca"]["taux_de_liquidation"],
                abs=TOLERANCE_EXACTE), (code, affiliation)
            if nous["morceaux"] > 1:
                coupes += 1
                ecarts.append(nous["montant"] / entree["openfisca"]["pension_brute"])
            else:
                assert nous["montant"] == pytest.approx(
                    reference["pension_brute"], rel=1e-9), (code, affiliation)
    assert coupes >= 10, "aucune carrière ne traverse une succession de caisses"
    assert min(ecarts) > 0.90, min(ecarts)
    assert max(ecarts) < 1.02, max(ecarts)
