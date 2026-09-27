"""Les trimestres des enfants, version par version : ce que chaque enfant vaut à sa date.

Le domaine « les dates des enfants » (docs/architecture.md, § 11). Les versions
des fiches ``majoration_duree_assurance_enfants`` et
``enfants_fonction_publique`` se lisent sur la naissance de l'enfant et sur la
date d'effet de la pension (``MajorationsPourEnfants.par_enfant``). Ce fichier
tient les bornes que les corrections du domaine ont posées au jour près : la
veille et le jour de chacune, où une erreur de date se voit (§ 6.7).
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.scenarios.actuel import MajorationsPourEnfants


@pytest.fixture(scope="module")
def majorations() -> MajorationsPourEnfants:
    return MajorationsPourEnfants(RACINE_DONNEES)


def _accorde(majorations: MajorationsPourEnfants, dispositif: str, naissance: str,
             date_effet: str, naissances: list[str] | None = None):
    """La version, les trimestres et les services qu'un enfant de la mère
    ouvre ; ``None`` s'il n'ouvre rien."""
    accorde = majorations.par_enfant(dispositif, "F", naissance, date_effet,
                                     len(naissances or [naissance]))
    return None if accorde is None else (accorde.version, accorde.trimestres, accorde.services)


# -- la fonction publique ---------------------------------------------------------

@pytest.mark.parametrize("date_effet, attendu", [
    ("2026-08-01", ("l12bis", 2, 0)),
    ("2026-09-01", ("l12bter", 2, 1)),
])
def test_le_b_ter_vaut_a_compter_du_1er_septembre_2026(majorations, date_effet, attendu):
    """L. 12 b ter, pour les pensions prenant effet à compter du 1er septembre
    2026 (loi n° 2025-1403, article 104) : la veille, les deux trimestres de
    L. 12 bis ne comptent qu'en durée ; le jour, l'un d'eux entre aux
    services. Le modèle, qui datait à l'année, l'appliquait dès janvier."""
    assert _accorde(majorations, "bonifications", "2005-03-01", date_effet) == attendu
