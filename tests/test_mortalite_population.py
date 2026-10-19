"""Ce que le diviseur commun coûte au régime : la grille du coût, lue à la date
de chaque cohorte (`scripts/mortalite_population.py --deficit`).

Le script relit les couples de la page Coût, et chacun représente cinq
cohortes. Jusqu'au 19 octobre 2026, il les faisait partir à l'âge de la
génération de la grille, l'année décalée d'autant, quand `cout.py` les date
depuis le 18 octobre au droit de leur génération (`Pensionne.liquidation`) :
la même erreur, que le coût et le coût des avantages ont quittée (action 138,
étape 3, notes « la date de chaque cohorte » et « le coût des avantages »).
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import mortalite_population as M  # noqa: E402
from retraite_notionnelle.cout import Pensionne, VoletLiberal  # noqa: E402


class _Mortalite:
    """La survie perd un dixième par an sous la table commune, un vingtième
    sous celle du vingtile : cinq ans de rente contre dix, un rapport des
    diviseurs d'un demi. Chaque courbe demandée est notée."""

    def __init__(self):
        self.appels = []

    def courbe(self, age, annee, sexe, generation=True, population=None):
        self.appels.append((age, annee, population))
        pas = 0.1 if population is None else 0.05
        return tuple(1.0 - pas * rang for rang in range(round(1 / pas) + 1))


class _Population:
    """Autant de têtes que d'années d'âge : chaque cohorte se reconnaît."""

    def effectif(self, age, annee):
        return float(age)


def test_chaque_cohorte_part_l_annee_que_lui_donne_le_droit_de_sa_generation():
    """Le salarié au salaire moyen né en janvier 1965 part en 2028 avec 170
    trimestres, sous la suspension de 2026 ; né en 1963 ou 1964, en 2026 et
    2027 ; né en 1966 ou 1967, il en doit 172 et part en 2030 et 2031
    (L. 161-17-3 ; `test_cout.py`, même couple). En 2030, la cohorte de 1967
    n'est pas partie, celle de 1966 part l'année même : la survie de chacune se
    compte depuis son départ, ses deux courbes et le rapport de ses diviseurs
    se prennent à son âge et à son année de départ, et le flux qui reçoit le
    diviseur de son vingtile depuis 2030 est la cohorte de 1966. Sans dates,
    celles de la grille."""
    reporte = VoletLiberal(annee_liquidation=2030, annee_ouverture_garantie=2030,
                           pension=1.0, ressources_garantie=1.0)
    datee = Pensionne(code="x", generation=1965, annee_liquidation=2028,
                      pensions={"actuel": 1.0, "notionnel_retroactif": 2.0},
                      propre=reporte, bascule=2026,
                      departs=(2026, 2027, 2028, 2030, 2031))
    mortalite = _Mortalite()
    cohortes = M._cohortes(datee, mortalite, "v10")
    assert set(mortalite.appels) == {
        (age, annee, population)
        for age, annee in ((63, 2026.0), (63, 2027.0), (63, 2028.0),
                           (64, 2030.0), (64, 2031.0))
        for population in (None, "v10")}
    assert [rapport for rapport, _, _ in cohortes] == pytest.approx([0.5] * 5, rel=1e-12)

    cles = ["actuel", "notionnel_retroactif"]
    poids = {"x": 0.5}
    masses = M._masses([(datee, cohortes)], poids, _Population(), 2030, cles)
    # Nées en 1963, 1964, 1965 et 1966 : 67, 66, 65 et 64 ans en 2030, parties
    # depuis 4, 3, 2 et 0 ans.
    tetes = (67, 66, 65, 64)
    survies = (0.8 / 0.6, 0.85 / 0.7, 0.9 / 0.8, 1.0)
    for cle, pension in (("actuel", 1.0), ("notionnel_retroactif", 2.0)):
        commun = 0.5 * pension * sum(tetes)
        vrai = 0.5 * pension * sum(t * s for t, s in zip(tetes, survies))
        assert masses[cle]["page_commun"] == pytest.approx(commun, rel=1e-12)
        assert masses[cle]["page_propre"] == pytest.approx(0.5 * commun, rel=1e-12)
        assert masses[cle]["vrai_commun"] == pytest.approx(vrai, rel=1e-12)
        assert masses[cle]["vrai_propre"] == pytest.approx(0.5 * vrai, rel=1e-12)

    # Le flux de 2030 : la seule cohorte de 1966.
    flux = M._masses([(datee, cohortes)], poids, _Population(), 2030, cles, depuis=2030)
    assert flux["actuel"]["page_propre"] == pytest.approx(
        0.5 * (67 + 66 + 65) + 0.5 * 64 * 0.5, rel=1e-12)

    # Sans dates, la grille : les cinq parties en 2030, la dernière l'année même.
    grille = replace(datee, departs=())
    masses = M._masses([(grille, M._cohortes(grille, _Mortalite(), "v10"))], poids,
                       _Population(), 2030, cles)
    assert masses["actuel"]["page_commun"] == pytest.approx(0.5 * (262 + 63), rel=1e-12)
