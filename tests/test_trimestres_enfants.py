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
    ouvre ; ``None`` s'il n'ouvre rien. ``naissances`` sont celles de tous ses
    enfants, lui compris ; par défaut, il est seul."""
    accorde = majorations.par_enfant(dispositif, "F", naissance, date_effet,
                                     naissances or [naissance])
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


# -- le régime général ------------------------------------------------------------

@pytest.mark.parametrize("date_effet, attendu", [
    ("1974-06-01", ("mda_1972", 4, 4)),
    ("1974-07-01", ("mda_1975", 8, 8)),
])
def test_la_loi_de_1975_vaut_pour_les_pensions_d_apres_le_30_juin_1974(
        majorations, date_effet, attendu):
    """Loi n° 75-3, article 21, et décret n° 75-109, article 20 : deux ans par
    enfant pour les pensions prenant effet après le 30 juin 1974. La veille,
    la loi Boulin en donne un, à la mère de deux enfants au moins. Le modèle,
    qui datait à l'année, la faisait durer jusqu'à la fin de 1974."""
    assert _accorde(majorations, "mda", "1950-03-01", date_effet,
                    ["1950-03-01", "1953-05-01"]) == attendu


@pytest.mark.parametrize("date_effet, attendu", [
    ("1974-06-01", None),
    ("1974-07-01", ("mda_1975", 8, 8)),
])
def test_la_loi_boulin_ne_donne_rien_a_la_mere_d_un_seul_enfant(
        majorations, date_effet, attendu):
    """La loi n° 71-1132 ne vise que les mères de deux enfants au moins ; la
    loi n° 75-3 compte dès le premier."""
    assert _accorde(majorations, "mda", "1950-03-01", date_effet) == attendu


@pytest.mark.parametrize("date_effet, attendu", [
    ("1999-05-01", None),
    ("1999-06-01", ("mda_1975", 8, 8)),
])
def test_l_enfant_qui_n_a_pas_neuf_ans_n_a_pas_ete_eleve_neuf_ans(
        majorations, date_effet, attendu):
    """De 1972 à 2003, la majoration va à l'enfant élevé neuf ans avant ses
    seize ans, et celui qui n'a pas neuf ans à la date d'effet ne peut pas
    l'avoir été : la veille de son neuvième anniversaire, rien ; le jour, les
    huit trimestres. Le modèle présumait la condition remplie."""
    assert _accorde(majorations, "mda", "1990-06-01", date_effet) == attendu


def test_sous_la_loi_boulin_seuls_comptent_les_enfants_eleves_neuf_ans(majorations):
    """« Au moins deux enfants » élevés neuf ans : la mère d'un aîné de treize
    ans et d'un cadet de cinq n'en a élevé qu'un, et n'a droit à rien."""
    naissances = ["1960-01-01", "1968-01-01"]
    assert _accorde(majorations, "mda", "1960-01-01", "1973-01-01", naissances) is None
    assert _accorde(majorations, "mda", "1968-01-01", "1973-01-01", naissances) is None
    assert _accorde(majorations, "mda", "1960-01-01", "1974-06-01",
                    ["1960-01-01", "1964-01-01"]) == ("mda_1972", 4, 4)
