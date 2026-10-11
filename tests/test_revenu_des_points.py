"""Le relevé des droits à rebours (action 138, étape 11) : le revenu que des
points supposent, retrouvé par le barème que la pension du scénario 1 applique.

Un relevé chiffre en points, et non en euros, les années d'un régime qui compte
en points et celles que seule la complémentaire chiffre. Le revenu rendu est le
plus bas qui ouvre ces points : il les ouvre, et un euro de moins ne les ouvre
pas. Son jumeau JavaScript est éprouvé contre lui par la lecture des relevés
(`test_releve_lu.py`), qui le prend pour convertisseur des deux côtés.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.droit.releve import points_de_l_annee, revenu_des_points
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def moteur():
    return Simulateur().scenario_actuel


@pytest.mark.parametrize("statut, annee, etage, points", [
    # Le régime de base des libéraux, deux tranches : 525 points au plafond,
    # 25 sur cinq plafonds.
    ("medecin_liberal", 2015, "base", 412),
    # Au-dessus de l'assiette minimale de 450 SMIC horaires.
    ("profession_liberale", 2024, "base", 300),
    # Les exploitants : la marche haute de R. 732-71, arrondie au point ; et le
    # palier de trente points, dont le revenu rendu est le bas.
    ("exploitant_agricole", 2018, "base", 80),
    ("exploitant_agricole", 2018, "base", 30),
    ("exploitant_agricole", 2018, "complementaire", 221.89),
    # L'Arrco, l'Agirc-Arrco, l'Ircantec, la complémentaire de la CNBF.
    ("salarie_prive_non_cadre", 2018, "complementaire", 2.90),
    ("salarie_prive_non_cadre", 2022, "complementaire", 187.62),
    ("contractuel_public", 2019, "complementaire", 7),
    ("avocat", 2020, "complementaire", 79.59),
])
def test_le_revenu_rendu_est_le_plus_bas_qui_ouvre_les_points(moteur, statut, annee,
                                                              etage, points):
    """La pension recalculée du revenu rendu retrouve les points du relevé, et
    celle d'un euro de moins ne les retrouve pas."""
    trouve = revenu_des_points(moteur, statut, annee, etage, points, 4)
    assert trouve is not None and not trouve.au_plafond
    assert points_de_l_annee(moteur, statut, annee, etage, trouve.revenu, 4) >= points - 1e-6
    assert points_de_l_annee(moteur, statut, annee, etage, trouve.revenu - 1, 4) < points - 1e-6


def test_au_plafond_du_bareme_le_revenu_est_le_plafond(moteur):
    """Les 550 points de 2015, le maximum des deux tranches : tout revenu de
    cinq plafonds et plus les ouvre. Le revenu rendu est cinq plafonds, et il
    dit qu'il a pu être plus haut."""
    trouve = revenu_des_points(moteur, "medecin_liberal", 2015, "base", 550, 4)
    assert trouve is not None and trouve.au_plafond
    assert trouve.revenu == round(5 * moteur.macro.plafond_securite_sociale(2015))


@pytest.mark.parametrize("statut, annee, etage, points, raison", [
    ("medecin_liberal", 2003, "base", 400,
     "cent points par trimestre avant 2004, quel que soit le revenu"),
    ("exploitant_agricole", 2018, "base", 23,
     "le plancher de six cents SMIC horaires, que tout revenu ouvre"),
    ("exploitant_agricole", 2018, "complementaire", 133,
     "l'assiette plancher de la RCO, que tout revenu ouvre"),
    ("medecin_liberal", 2016, "base", 560,
     "plus que le barème n'en ouvre : 550 au plus"),
    ("fonctionnaire_etat", 2015, "complementaire", 300,
     "un an de services rétablit à l'Ircantec, qui n'est pas le régime du statut"),
    ("fonctionnaire_etat", 2015, "additionnel", 30,
     "le RAFP compte les primes, non la rémunération"),
    ("salarie_prive_non_cadre", 1950, "complementaire", 10,
     "l'Arrco n'existe pas encore"),
])
def test_des_points_qui_ne_disent_aucun_revenu(moteur, statut, annee, etage, points,
                                               raison):
    assert revenu_des_points(moteur, statut, annee, etage, points, 4) is None, raison
