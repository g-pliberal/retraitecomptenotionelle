"""Lequel des treize cas types part de travers : la confrontation par catégorie.

La concordance d'ensemble trouvée par `test_age_conjoncturel.py` ne juge que la
SOMME des cas types. Celle-ci descend d'un grain : chaque cas type contre le
couloir des catégories socioprofessionnelles où il peut tomber. Ce qu'elle
trouve, et que ces tests tiennent, c'est que les écarts individuels valent plus
d'une année en moyenne et qu'ils se COMPENSENT — la concordance d'ensemble
n'était donc pas un accord cas par cas.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.castypes import CAS_TYPES
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import age_conjoncturel  # noqa: E402
import age_depart_csp  # noqa: E402


@pytest.fixture(scope="module")
def simulateur():
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def confrontations(simulateur):
    return age_depart_csp.confronter(simulateur)


@pytest.fixture(scope="module")
def lignes_publiees():
    with age_depart_csp.SERIE.open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        return list(csv.DictReader(lignes))


def test_la_serie_par_csp_est_haute_et_non_certifiee(lignes_publiees):
    """Un SONDAGE ne se certifie pas comme un dénombrement.

    La DREES produit bien ce chiffre, mais depuis l'enquête Emploi, et elle
    avertit que ses indicateurs par catégorie sont bruités. Le niveau `haute`
    dit exactement cela, et c'est pourquoi la comparaison se fait en moyenne
    pluriannuelle.
    """
    assert lignes_publiees
    for ligne in lignes_publiees:
        assert ligne["fiabilite"] == "haute", ligne

    annees = {int(ligne["annee"]) for ligne in lignes_publiees}
    groupes = {ligne["csp"] for ligne in lignes_publiees}
    assert annees == set(range(2013, 2021))
    assert groupes == {"1", "2", "3", "4", "5", "6", "9"}


def test_la_ligne_toutes_csp_recoupe_le_tous_regimes(lignes_publiees):
    """Deux sources indépendantes, et elles se rejoignent à deux dixièmes près.

    Le tous régimes vient des fichiers des caisses, celui-ci de l'enquête
    Emploi. Rien ne les oblige à concorder ; qu'elles le fassent est ce qui
    autorise à lire la ventilation. L'écart va de −0,04 à +0,14 an sur les
    huit années communes, et l'enquête arrondit au dixième : la borne est donc
    posée à 0,2 an, et la moyenne des écarts à un dixième.
    """
    enquete = {int(ligne["annee"]): float(ligne["age"])
               for ligne in lignes_publiees if ligne["csp"] == "9"}
    denombrement = age_conjoncturel.age_conjoncturel_publie()
    communes = sorted(set(enquete) & set(denombrement))
    assert len(communes) >= 8
    for annee in communes:
        assert enquete[annee] == pytest.approx(denombrement[annee], abs=0.2), annee
    moyen = sum(enquete[annee] - denombrement[annee] for annee in communes)
    assert abs(moyen / len(communes)) < 0.1


def test_chaque_cas_type_a_sa_ligne_et_son_motif():
    """Un cas type déclare un couloir OU une mise hors champ, jamais les deux.

    Et jamais rien : c'est le seul endroit du dépôt où l'on décide qu'un cas
    type ressemble à une catégorie, et une décision non écrite serait une
    décision prise dans le code de la comparaison.
    """
    table = age_depart_csp.correspondance()
    groupes_connus = set(table["nomenclature"]["groupes"])
    fiches = {fiche["code"]: fiche for fiche in table["cas_types"]}
    assert set(fiches) == {cas.code for cas in CAS_TYPES}

    for code, fiche in fiches.items():
        couloir, hors = "groupes" in fiche, "hors_champ" in fiche
        assert couloir != hors, f"{code} : couloir et hors champ s'excluent"
        if couloir:
            assert fiche["groupes"], code
            assert set(fiche["groupes"]) <= groupes_connus, code
            assert len(fiche.get("motif", "").split()) >= 10, code
        else:
            assert len(fiche["hors_champ"].split()) >= 10, code


def test_les_professions_liberales_sont_avec_les_cadres():
    """Le classement qu'on suivrait mal de mémoire, et qui change la réponse.

    La nomenclature les met dans le groupe 3 avec les cadres, non dans le
    groupe 2 avec les artisans et les commerçants. Le groupe 2 part en moyenne
    plus tard : les confondre déplacerait l'écart du libéral.
    """
    fiches = {fiche["code"]: fiche
              for fiche in age_depart_csp.correspondance()["cas_types"]}
    assert fiches["profession_liberale"]["groupes"] == ["3"]
    assert fiches["cadre"]["groupes"] == ["3"]
    assert fiches["artisan"]["groupes"] == ["2"]


def test_quatre_cas_types_sortent_du_champ_et_ce_sont_les_departs_precoces(
        confrontations):
    """Le militaire, l'agent de conduite, l'agent des IEG, la catégorie active.

    Leur départ n'est pas une sortie du marché du travail, et l'enquête Emploi
    compte retraité qui se déclare tel. Les comparer reviendrait à dater deux
    événements différents.
    """
    _, hors_champ = confrontations
    assert set(hors_champ) == {
        "militaire", "agent_sncf_conduite", "agent_ieg", "fonctionnaire_actif"}


def test_les_ecarts_individuels_valent_plus_d_une_annee(confrontations):
    """Ce que la concordance d'ensemble ne disait pas.

    Neuf cas types comparables, pesés comme sur la page « Coût » : plus d'une
    année d'écart en valeur absolue, là où le tous régimes donnait moins d'un
    dixième. Le seuil est lâche — ce qu'on refuse est que ce constat s'efface
    sans que personne le voie.
    """
    lignes, _ = confrontations
    assert len(lignes) == 9
    absolu = sum(ligne.poids * abs(ligne.ecart) for ligne in lignes)
    assert absolu > 0.8
    assert max(abs(ligne.ecart) for ligne in lignes) > 2.0
    assert sum(ligne.poids for ligne in lignes) == pytest.approx(1.0, abs=1e-3)


def test_les_ecarts_se_compensent(confrontations):
    """Et c'est la raison pour laquelle le tous régimes ne les voyait pas.

    L'écart signé est plus de deux fois plus petit que l'écart en valeur
    absolue : les cas types qui partent trop tard sont rattrapés par ceux qui
    partent trop tôt.
    """
    lignes, _ = confrontations
    signe = sum(ligne.poids * ligne.ecart for ligne in lignes)
    absolu = sum(ligne.poids * abs(ligne.ecart) for ligne in lignes)
    assert abs(signe) < absolu / 2

    trop_tard = [ligne.code for ligne in lignes if ligne.ecart > 0]
    trop_tot = [ligne.code for ligne in lignes if ligne.ecart < 0]
    assert trop_tard and trop_tot, "la compensation suppose les deux sens"
