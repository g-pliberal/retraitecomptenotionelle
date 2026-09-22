"""Les services de la fonction publique, et ce qui n'en est pas.

La pension de la fonction publique ne se proratise pas sur la durée
d'assurance mais sur les SERVICES ET BONIFICATIONS — article L. 13 du code des
pensions civiles et militaires de retraite. Et l'article L. 9 est catégorique
sur ce que les services ne retiennent pas : « Le temps passé dans une position
statutaire ne comportant pas l'accomplissement de services effectifs au sens de
l'article L. 5 ne peut entrer en compte dans la constitution du droit à
pension », hors une liste fermée qu'il énumère — congés de maladie, de
maternité, congé parental dans la limite de trois ans par enfant, détachement.

Le moteur créditait ce prorata de TOUTE période validée. Une carrière de
fonctionnaire coupée de cinq ans de chômage servait donc exactement la même
pension qu'une carrière pleine, ce qu'aucun texte n'autorise : un fonctionnaire
au chômage n'est d'ailleurs plus fonctionnaire, le chômage n'étant pas une
position statutaire.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _pension(simulateur: Simulateur, affiliation: str, motif: str | None,
             nombre_enfants: int = 0, annees: int = 5) -> tuple[float, str]:
    """Pension d'une carrière pleine, coupée ou non par cinq ans d'un motif."""
    carriere = Carriere.depuis_parcours(
        annee_naissance=1975,
        sexe="F",
        metiers=[Metier(affiliation=affiliation, age_debut=22.0,
                        niveau_salaire=1.0)],
        age_liquidation=64.0,
        macro=simulateur.macro,
        interruptions={annee: motif
                       for annee in range(2000, 2000 + annees)} if motif else {},
        nombre_enfants=nombre_enfants,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    # Le prorata ne se lit que sur le régime en ANNUITÉS : c'est lui qui
    # compare une durée acquise à une durée requise.
    annuites = next(p for p in resultat.pensions_par_regime
                    if p.type_calcul == "annuites")
    return resultat.pension_annuelle, annuites.detail


def test_le_chomage_n_ouvre_aucun_service_a_l_etat(simulateur):
    """L. 9 : pas de position statutaire, donc pas de services.

    C'est le cas qui a révélé la confusion : avant correction, les deux
    montants étaient égaux au centime, et cinq ans de chômage ne coûtaient
    rien à un fonctionnaire.
    """
    pleine, _ = _pension(simulateur, "fonctionnaire_etat", None)
    coupee, detail = _pension(simulateur, "fonctionnaire_etat",
                              "chomage_indemnise")
    assert coupee < pleine, (
        "cinq ans de chômage retirent vingt trimestres de services : "
        f"{detail}"
    )
    assert "148/172" in detail, "168 trimestres de services moins vingt"


def test_le_chomage_reste_une_periode_assimilee_au_regime_general(simulateur):
    """La correction ne déborde pas sur le privé.

    Le coefficient de proratisation du régime général porte sur la durée
    d'ASSURANCE (R. 351-1), périodes assimilées comprises : les mêmes cinq ans
    de chômage y valident vingt trimestres. Confondre les deux corrections
    aurait retiré aux chômeurs du privé ce que le droit leur accorde.
    """
    _, detail_plein = _pension(simulateur, "salarie_prive_non_cadre", None)
    _, detail_coupe = _pension(simulateur, "salarie_prive_non_cadre",
                               "chomage_indemnise")
    assert "168/172" in detail_plein
    assert "168/172" in detail_coupe, (
        "les mêmes cinq ans coûtent vingt trimestres de services à l'État et "
        "aucun trimestre de durée d'assurance à la CNAV"
    )


def test_la_maladie_compte_en_services_parce_que_L_9_l_excepte(simulateur):
    """Le 2° de L. 9 excepte les congés de maladie du fonctionnaire en activité.

    Contrôle qui empêche de « corriger » trop loin : tout ce qui n'est pas du
    travail n'est pas hors des services.
    """
    pleine, _ = _pension(simulateur, "fonctionnaire_etat", None)
    malade, detail = _pension(simulateur, "fonctionnaire_etat", "maladie")
    assert malade == pytest.approx(pleine), detail


def test_le_conge_parental_est_excepte_dans_la_limite_de_trois_ans(simulateur):
    """« Dans la limite de trois ans par enfant né ou adopté » (1° de L. 9).

    Cinq ans d'éducation d'un enfant n'ouvrent que douze trimestres de
    services ; le même congé pour deux enfants les ouvre tous. La limite se
    tient sur toute la carrière, et non année par année.
    """
    sans, _ = _pension(simulateur, "fonctionnaire_etat", "education_enfant",
                       nombre_enfants=0)
    un, detail_un = _pension(simulateur, "fonctionnaire_etat",
                             "education_enfant", nombre_enfants=1)
    deux, detail_deux = _pension(simulateur, "fonctionnaire_etat",
                                 "education_enfant", nombre_enfants=2)
    assert sans < un < deux
    # Cent soixante-huit trimestres de services pour une carrière pleine.
    # Sans enfant, aucun des vingt trimestres du congé n'est excepté : 148.
    # Avec un enfant, douze le sont, et la bonification de L. 12 en ajoute un :
    # 161. Avec deux enfants, les vingt le sont, plus deux bonifications : 170.
    assert "161/172" in detail_un
    assert "170/172" in detail_deux


def test_la_table_dit_ce_que_chaque_motif_ouvre_aux_services():
    """La règle est en données, pas en code, et elle est close.

    Trois valeurs seulement, et une seule porte un plafond.
    """
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.chargement import (
        charger_periodes_non_travaillees,
    )

    table = charger_periodes_non_travaillees(RACINE_DONNEES)
    assert not table["chomage_indemnise"].services_fonction_publique
    assert not table["chomage_non_indemnise"].services_fonction_publique
    assert table["maladie"].services_fonction_publique
    assert table["service_militaire"].services_fonction_publique
    assert table["education_enfant"].services_fonction_publique
    assert table["education_enfant"].services_plafond_trimestres_par_enfant == 12
    for motif, regle in table.items():
        assert regle.services_plafond_trimestres_par_enfant >= 0, motif
        if regle.services_plafond_trimestres_par_enfant:
            assert regle.services_fonction_publique, motif


def test_le_portage_du_paquet_porte_les_deux_colonnes():
    """Ce que le site charge doit dire la même chose que le Python.

    Le paquet range chaque motif dans un tableau positionnel : ajouter une
    colonne sans la porter laissait le site sur l'ancienne règle, sans que
    rien ne le dise.
    """
    import json
    from pathlib import Path

    paquet = json.loads(
        (Path(__file__).resolve().parents[1] / "moteur" / "donnees.json")
        .read_text(encoding="utf-8")
    )["periodes_non_travaillees"]
    assert paquet["chomage_indemnise"][4] is False
    assert paquet["maladie"][4] is True
    assert paquet["education_enfant"][5] == 12
