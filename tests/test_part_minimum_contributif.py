"""La part des nouveaux retraités au minimum contributif : ce que l'EACR observe, et ce que la mesure lit.

`scripts/part_minimum_contributif.py` confronte les grilles de la page Coût à
l'enquête annuelle auprès des caisses de retraite et à TRAJECTOiRE (action
137). La mesure entière prend trois minutes et ne se rejoue pas ici ; ce qui se
tient ici la rend lisible : le fichier certifié redonne ce que la DREES en
publie, une génération s'étale sur ses mois de naissance, et le minimum se lit
dans le scénario 1 tel que le moteur le sert.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle.castypes import CAS_TYPES
from retraite_notionnelle.config import Parametres

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import part_minimum_contributif as P  # noqa: E402


def test_le_fichier_de_l_eacr_redonne_l_etude_de_la_drees():
    """Études et résultats n° 1297, graphique 1 et son texte (p. 3) : 17,5 % des
    nouveaux retraités du régime général et 25,1 % de ceux de la MSA salariés en
    2021. Pour 2012, l'étude lit 27,6 %, et le fichier, qui retient le
    millésime le plus récent, un demi-point de moins."""
    parts = P.observees(Parametres().racine_donnees)
    assert round(parts[(2021, "cnav", "ensemble")], 1) == 17.5
    assert round(parts[(2021, "msa_salaries", "ensemble")], 1) == 25.1
    assert 27.0 < parts[(2012, "cnav", "ensemble")] < 27.6
    # Le sexe n'est ventilé que depuis 2022, et les deux sexes encadrent l'ensemble.
    assert (2021, "cnav", "F") not in parts
    for annee in (2022, 2023, 2024):
        femmes, hommes, ensemble = (parts[(annee, "cnav", s)] for s in ("F", "H", "ensemble"))
        assert hommes < ensemble < femmes


def test_une_generation_s_etale_sur_ses_mois_de_naissance():
    """La grille fait naître une génération en janvier ; ses autres mois de
    naissance partent au même âge, autant de mois plus tard."""
    # Un effet en janvier : chaque mois de naissance part la même année.
    assert P.etalement(1955, 2017, 1) == pytest.approx({2017: 1.0})
    # Un effet en février : le mois de décembre part l'année suivante.
    assert P.etalement(1955, 2017, 2) == pytest.approx({2017: 11 / 12, 2018: 1 / 12})
    # À 66 ans et 8 mois d'écart, quatre mois de naissance partent cette année-là.
    assert P.etalement(1954, 2020, 9) == pytest.approx({2020: 4 / 12, 2021: 8 / 12})


def test_le_minimum_se_lit_dans_le_scenario_1():
    """Le cas type au Smic de la génération 1955 a sa pension du régime général
    relevée au minimum, majoration comprise ; le cadre l'a au-dessus ; aucun
    n'est refusé, et le plafond de l'écrêtement s'applique aux deux départs,
    postérieurs à 2012."""
    cas = {c.code: c for c in CAS_TYPES}
    lignes = P._mesurer(Parametres(), ((0, cas["smic_carriere_complete"], 1955),
                                       (1, cas["cadre"], 1955)))
    mesures = {indice: mesure for indice, _, mesure in lignes}
    annee, _, minimum, majore, avant = mesures[0]
    assert 2015 <= annee <= 2017
    assert minimum > 0.0 and majore
    assert avant is not None and minimum <= avant
    assert mesures[1][2] == 0.0
