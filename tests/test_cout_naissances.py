"""Les naissances de l'année (``scripts/cout_naissances.py``) : ce que des
cohortes nées toute l'année déplacent à la page Coût, mesuré avant d'en
décider (action 138, étape 3, note « les naissances de l'année »)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import cout_naissances as N  # noqa: E402
from retraite_notionnelle import Parametres, memoire  # noqa: E402


def test_le_tableau_dit_ce_que_les_cohortes_nees_toute_l_annee_deplacent():
    """Posé à la main : seize millions de têtes sous la grille, 0,36 million de
    moins nées toute l'année ; une masse du système actuel qui perd 4,9 %, un
    ancrage qui gagne 5,1 % ; une dérive de 1,060 qui passe à 1,077 ; un
    système de 8,870 % du PIB qui passe à 9,100."""
    def mesures(tetes, masse, ancrage, derive, page):
        return {
            "ancrage": ancrage,
            "tetes": dict.fromkeys(N.ANNEES_TETES, tetes),
            "masses": dict.fromkeys(N.ANNEES_TETES, masse),
            "derive": dict.fromkeys(N.ANNEES_DERIVE, derive),
            "page": {cle: dict.fromkeys(N.ANNEES_PAGE, page) for cle, _ in N.SYSTEMES},
            "borne_haute": {cle: dict.fromkeys(N.ANNEES_DERIVE, page) for cle, _ in N.SYSTEMES},
            "reconstitution": dict.fromkeys(N.ANNEES_PASSE, -0.1104),
            "tetes_du_passe": dict.fromkeys(N.ANNEES_PASSE, -0.0553),
        }

    tableau = N.tableau({N.VARIANTES[0]: mesures(16.86e6, 100.0, 1.0, 1.0604, 8.870),
                         N.VARIANTES[1]: mesures(16.50e6, 95.1, 1.0512, 1.0772, 9.100)})
    lignes = tableau.splitlines()
    assert lignes[0].split() == ["grille", "nées", "toute", "l'année", "écart"]
    assert "têtes 2024, millions 16.860 16.500 -0.360" in [" ".join(l.split()) for l in lignes]
    assert "masse du système 1 en 2024 -4.9%" in [" ".join(l.split()) for l in lignes]
    assert "ancrage +5.1%" in [" ".join(l.split()) for l in lignes]
    assert "dérive 2070 1.0604 1.0772 +0.0168" in [" ".join(l.split()) for l in lignes]
    assert "système 6 2026, % du PIB 8.870 9.100 +0.230" in [" ".join(l.split()) for l in lignes]
    assert "passé refait 2009, % -11.04 -11.04 +0.00" in [" ".join(l.split()) for l in lignes]


def test_nees_toute_l_annee_la_page_compte_moins_de_tetes_et_de_masses():
    """Nées toute l'année, les cohortes de la grille ne comptent plus toute
    l'année de leur départ : la page compte moins de têtes et moins de masse
    chaque année, et l'ancrage monte de ce que la masse de 2024 baisse, la
    dépense de 2024 étant la même. Le système actuel, qui part de la dépense
    du COR, ne bouge pas ; la dérive de 2070, comptée de 2025, monte, la masse
    de 2025 étant plus grossie par la grille que celle de 2070 — mesurée le 24
    octobre 2026 de 1,060 à 1,077."""
    parametres = Parametres()
    grille, nees = (N.mesurer(naissances, parametres) for naissances in N.VARIANTES)
    for annee in N.ANNEES_TETES:
        assert nees["tetes"][annee] < grille["tetes"][annee], annee
        assert nees["masses"][annee] < grille["masses"][annee], annee
    assert nees["ancrage"] / grille["ancrage"] == pytest.approx(
        grille["masses"][2024] / nees["masses"][2024], rel=1e-12)
    assert nees["derive"][2070] > grille["derive"][2070] + 0.01
    avant, apres = (memoire.cout(parametres, naissances=naissances).avenir
                    for naissances in N.VARIANTES)
    assert [ligne.part_pib("actuel") for ligne in apres.annees] == [
        ligne.part_pib("actuel") for ligne in avant.annees]
