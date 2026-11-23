"""La surcote des trimestres accomplis de 2004 à 2006, au régime général.

Le décret n° 2006-1611 du 15 décembre 2006 (JO du 17, ``JORFTEXT000000821803``)
réécrit l'article D. 351-1-4 du code de la sécurité sociale : la majoration
« est égale, pour chaque trimestre accompli à compter du 1er janvier 2004, à :
1° 0,75 % du premier au quatrième trimestre ; 2° 1 % au-delà du quatrième
trimestre ; 3° ou, quel que soit son rang, 1,25 % pour chaque trimestre
accompli après le soixante-cinquième anniversaire de l'assuré » ; son
article 3 l'applique « aux pensions prenant effet à compter du 1er janvier
2007 ». Les trimestres de 2004 à 2006 d'une pension de 2007 ou après prennent
donc ces taux ; ceux d'une pension prenant effet avant 2007, 0,75 % chacun
(circulaire Cnav 2018-04, point 3.1.1).
"""

from __future__ import annotations

import pytest

from facade import Simulateur, liquider, ouvrir
from retraite_notionnelle.calendrier import DateMois, date_d_effet


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def test_l_exemple_3_de_la_circulaire_cnav_2007_5(simulateur):
    """Circulaire Cnav n° 2007/5 du 16 janvier 2007, point 13, exemple 3 :
    65 ans en avril 2006, pension au 1er avril 2007, trois trimestres cotisés
    en 2004, trois en 2005, trois en 2006, un en 2007 ; dix trimestres de
    surcote, dont trois après le soixante-cinquième anniversaire (deux en
    2006, un en 2007). « (4 x 0,75 %) + (3 x 1 %) + (3 x 1,25 %) = 0,0975 »."""
    trimestres = [(DateMois(annee, mois), False)
                  for annee in (2004, 2005) for mois in (1, 4, 7)]
    trimestres += [(DateMois(2006, 1), False), (DateMois(2006, 7), True),
                   (DateMois(2006, 10), True), (DateMois(2007, 1), True)]
    coefficient, _ = simulateur.scenario_actuel.surcote_baremes.coefficient(
        "regime_general", trimestres, DateMois(2007, 4))
    assert coefficient == pytest.approx(1.0975)


def test_une_pension_prenant_effet_avant_2007_garde_0_75_pour_cent(simulateur):
    """Circulaire Cnav 2018-04, point 3.1.1 : les trimestres acquis du
    1er janvier 2004 au 30 septembre 2006, pour les pensions prenant effet du
    1er avril 2004 au 31 décembre 2006, valent 0,75 % chacun, quel que soit
    leur rang et l'âge (D. 351-1-4 dans sa rédaction de 2004). Huit
    trimestres, dont deux après 65 ans, pension au 1er janvier 2006 : 6 %."""
    trimestres = [(DateMois(annee, mois), annee == 2005 and mois >= 7)
                  for annee in (2004, 2005) for mois in (1, 4, 7, 10)]
    coefficient, _ = simulateur.scenario_actuel.surcote_baremes.coefficient(
        "regime_general", trimestres, DateMois(2006, 1))
    assert coefficient == pytest.approx(1.06)


def test_la_liquidation_de_2007_date_la_surcote_de_2004_a_2006(simulateur):
    """Né le 15 avril 1941 (la date entière, que le test déclare), salarié à temps plein depuis ses dix-huit ans, le
    taux plein acquis bien avant 2004, il part le 1er avril 2007 : treize
    trimestres de surcote, du 1er janvier 2004 au 31 mars 2007. Soixante-cinq
    ans au deuxième trimestre 2006 : les trimestres de juillet et d'octobre
    2006 et de janvier 2007 prennent 1,25 % ; des dix autres, les quatre
    premiers 0,75 %, les six suivants 1 %. Calcul posé sur D. 351-1-4 dans
    sa rédaction du décret n° 2006-1611 : 3 + 6 + 3,75 = 12,75 %."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1941, mois_naissance=4, jour_naissance=15, sexe="H",
        affiliation="salarie_prive_non_cadre", age_debut=18,
        age_liquidation=65 + 11 / 12)
    assert carriere.date_liquidation == DateMois(2007, 4)
    actuel = simulateur.scenario_actuel
    periode = simulateur.catalogue["regime_general"].a_la_date(date_d_effet(carriere))
    requis, _ = ouvrir.duree_requise(actuel, periode, carriere)
    total = simulateur.scenario_actuel.calculer(carriere).trimestres_valides
    coefficient, _ = liquider.coefficient_surcote_datee(
        actuel, periode, carriere, total, requis, total - requis,
        ouvrir.age_surcote(actuel, periode, carriere))
    assert coefficient == pytest.approx(1.1275)
