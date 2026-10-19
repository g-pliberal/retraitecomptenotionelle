"""Ce que le diviseur commun coûte au régime : la grille du coût, lue à la date
de chaque cohorte (`scripts/mortalite_population.py --deficit`).

Le script relit les couples de la page Coût, et chacun représente cinq
cohortes. Jusqu'au 19 octobre 2026, il les faisait partir à l'âge de la
génération de la grille, l'année décalée d'autant, quand `cout.py` les date
depuis le 18 octobre au droit de leur génération (`Pensionne.liquidation`) :
la même erreur, que le coût et le coût des avantages ont quittée (action 138,
étape 3, notes « la date de chaque cohorte » et « le coût des avantages »).

Il les fait aussi vivre comme la page. Jusqu'au même jour, il la disait à la
mortalité générale, quand elle fait vivre chaque cas type, depuis le
17 octobre, au rythme de sa population et à nombre de décès égal
(`cout._survies`, `_survies_alignees`) ; et il n'en relisait ni la grille
entière, ni le vingtile (action 138, étape 7, note « la prémisse du déficit »).
"""

from __future__ import annotations

import inspect
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import mortalite_population as M  # noqa: E402
from retraite_notionnelle.castypes import GRILLE_DU_COUT, carriere_de_la_grille  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.cout import Pensionne, VoletLiberal, calculer_cout  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402


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


class _Courbes:
    """Une courbe de survie par population, posée à la main ; chaque courbe
    demandée est notée."""

    def __init__(self, courbes):
        self.courbes = courbes
        self.appels = []

    def courbe(self, age, annee, sexe, generation=True, population=None):
        self.appels.append((age, annee, population))
        return self.courbes[population]


class _Population:
    """Autant de têtes que d'années d'âge : chaque cohorte se reconnaît."""

    def effectif(self, age, annee):
        return float(age)


#: Le report de la proposition, que le déficit ne lit pas.
_REPORTE = VoletLiberal(annee_liquidation=2030, annee_ouverture_garantie=2030,
                        pension=1.0, ressources_garantie=1.0)

#: Les départs du salarié au salaire moyen né en janvier 1965, et de ses
#: voisins, sous la suspension de 2026 (L. 161-17-3 ; `test_cout.py`).
_DEPARTS = (2026, 2027, 2028, 2030, 2031)


def test_chaque_cohorte_part_l_annee_que_lui_donne_le_droit_de_sa_generation():
    """Le salarié au salaire moyen né en janvier 1965 part en 2028 avec 170
    trimestres, sous la suspension de 2026 ; né en 1963 ou 1964, en 2026 et
    2027 ; né en 1966 ou 1967, il en doit 172 et part en 2030 et 2031
    (L. 161-17-3 ; `test_cout.py`, même couple). En 2030, la cohorte de 1967
    n'est pas partie, celle de 1966 part l'année même : chacune compte depuis
    son départ, les deux courbes du rapport de ses diviseurs se prennent à son
    âge et à son année de départ, et le flux qui reçoit le diviseur de son
    vingtile depuis 2030 est la cohorte de 1966. Sans survie propre, il vit
    comme la pyramide. Sans dates, celles de la grille."""
    datee = Pensionne(code="x", generation=1965, annee_liquidation=2028,
                      pensions={"actuel": 1.0, "notionnel_retroactif": 2.0},
                      propre=_REPORTE, bascule=2026, departs=_DEPARTS)
    mortalite = _Mortalite()
    rapports = M._rapports(datee, mortalite, "v10")
    assert set(mortalite.appels) == {
        (age, annee, population)
        for age, annee in ((63, 2026.0), (63, 2027.0), (63, 2028.0),
                           (64, 2030.0), (64, 2031.0))
        for population in (None, "v10")}
    assert rapports == pytest.approx([0.5] * 5, rel=1e-12)

    cles = ["actuel", "notionnel_retroactif"]
    poids = {"x": 0.5}
    masses = M._masses([(datee, rapports)], poids, _Population(), 2030, cles)
    # Nées en 1963, 1964, 1965 et 1966 : 67, 66, 65 et 64 ans en 2030.
    tetes = (67, 66, 65, 64)
    for cle, pension in (("actuel", 1.0), ("notionnel_retroactif", 2.0)):
        generale = 0.5 * pension * sum(tetes)
        for survie in ("generale", "vrai"):
            assert masses[cle][f"{survie}_commun"] == pytest.approx(generale, rel=1e-12)
            assert masses[cle][f"{survie}_propre"] == pytest.approx(0.5 * generale, rel=1e-12)

    # Le flux de 2030 : la seule cohorte de 1966.
    flux = M._masses([(datee, rapports)], poids, _Population(), 2030, cles, depuis=2030)
    assert flux["actuel"]["generale_propre"] == pytest.approx(
        0.5 * (67 + 66 + 65) + 0.5 * 64 * 0.5, rel=1e-12)

    # Sans dates, la grille : les cinq parties en 2030, la dernière l'année même.
    grille = replace(datee, departs=())
    masses = M._masses([(grille, M._rapports(grille, _Mortalite(), "v10"))], poids,
                       _Population(), 2030, cles)
    assert masses["actuel"]["generale_commun"] == pytest.approx(0.5 * (262 + 63), rel=1e-12)


def test_chaque_cas_type_vit_comme_la_page_le_fait_vivre_a_nombre_de_deces_egal():
    """La page fait vivre chaque cas type au rythme de sa population, à
    nombre de décès égal (`cout._survies_alignees`, misraa) : dans chaque
    cohorte, la survie de chacun, rapportée à la pyramide, est divisée par leur
    moyenne, pesée comme la grille les pèse. Deux cas types nés en 1965,
    partis comme le salarié au salaire moyen, pesés un quart et trois quarts :
    chaque année depuis son départ, le premier survit un dixième de plus que la
    pyramide, le second un dixième de moins. En 2030, la cohorte de 1963,
    partie depuis quatre ans, survit en moyenne à 1,4 × 0,25 + 0,6 × 0,75 =
    0,8 fois la pyramide : le premier y compte 1,4 / 0,8 fois ses têtes, le
    second 0,6 / 0,8. La pyramide garde ses survivants : à pension égale, la
    masse ne bouge pas ; à pension triple, celui qui vit longtemps la grossit,
    et le diviseur de son vingtile y pèse d'autant. Seul de sa grille, un cas
    type vit comme la pyramide. Jusqu'au 19 octobre 2026, le script faisait
    vivre chacun au rythme de son vingtile rapporté à la population générale,
    sans aligner : la grille, qui n'est pas une population, n'y gardait pas le
    nombre des décès."""
    long = (1.0, 1.1, 1.2, 1.3, 1.4, 1.5)
    court = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5)
    x = Pensionne(code="x", generation=1965, annee_liquidation=2028,
                  pensions={"actuel": 1.0, "notionnel_retroactif": 3.0},
                  propre=_REPORTE, bascule=2026, departs=_DEPARTS, survies=(long,) * 5)
    y = replace(x, code="y", pensions={"actuel": 1.0, "notionnel_retroactif": 1.0},
                survies=(court,) * 5)
    couples = [(x, (0.8,) * 5), (y, (1.25,) * 5)]
    poids = {"x": 0.25, "y": 0.75}
    cles = ["actuel", "notionnel_retroactif"]
    masses = M._masses(couples, poids, _Population(), 2030, cles)

    # En 2030, nées en 1963, 1964, 1965 et 1966 : 67, 66, 65 et 64 ans,
    # parties depuis 4, 3, 2 et 0 ans.
    tetes = (67, 66, 65, 64)
    vit_x = (1.4 / 0.8, 1.3 / 0.85, 1.2 / 0.9, 1.0)
    vit_y = (0.6 / 0.8, 0.7 / 0.85, 0.8 / 0.9, 1.0)
    tetes_x = sum(t * s for t, s in zip(tetes, vit_x))
    tetes_y = sum(t * s for t, s in zip(tetes, vit_y))
    assert masses["actuel"]["generale_commun"] == pytest.approx(sum(tetes), rel=1e-12)
    assert masses["actuel"]["vrai_commun"] == pytest.approx(sum(tetes), rel=1e-12)
    assert masses["notionnel_retroactif"]["generale_commun"] == pytest.approx(
        0.25 * 3.0 * sum(tetes) + 0.75 * sum(tetes), rel=1e-12)
    assert masses["notionnel_retroactif"]["vrai_commun"] == pytest.approx(
        0.25 * 3.0 * tetes_x + 0.75 * tetes_y, rel=1e-12)
    assert masses["notionnel_retroactif"]["vrai_propre"] == pytest.approx(
        0.25 * 3.0 * 0.8 * tetes_x + 0.75 * 1.25 * tetes_y, rel=1e-12)
    assert masses["notionnel_retroactif"]["generale_propre"] == pytest.approx(
        0.25 * 3.0 * 0.8 * sum(tetes) + 0.75 * 1.25 * sum(tetes), rel=1e-12)

    seul = M._masses(couples[:1], {"x": 1.0}, _Population(), 2030, cles)
    for cle in cles:
        assert seul[cle]["vrai_commun"] == pytest.approx(seul[cle]["generale_commun"],
                                                         rel=1e-12)


def test_l_inapte_vit_comme_les_inaptes_de_la_cnav_sous_le_diviseur_de_son_vingtile():
    """La page fait vivre l'inapte comme les inaptes de la Cnav
    (`CasType.mortalite`), quand son diviseur reste celui du vingtile où son
    salaire le range (`cout._survies`) ; le script fait de même, chaque
    cohorte à son âge et à son année de départ. Sur des courbes de trois ans
    — la pyramide 1, 0,8, 0,4 ; le vingtile 1, 0,9, 0,6 ; les inaptes 1, 0,6,
    0,2 —, l'inapte survit à 0,75 puis 0,5 fois la pyramide, et le rapport de
    ses diviseurs est celui du vingtile, 1,5 an de rente contre 1,7. Sans
    mortalité propre, la survie est celle du vingtile."""
    mortalite = _Courbes({None: (1.0, 0.8, 0.4), "v10": (1.0, 0.9, 0.6),
                          "cnav_inaptitude": (1.0, 0.6, 0.2)})
    simulateur = SimpleNamespace(mortalite=mortalite)
    inapte = Pensionne(code="x~inapte", generation=1965, annee_liquidation=2027,
                       pensions={"actuel": 1.0}, propre=_REPORTE,
                       departs=(2025, 2026, 2027, 2029, 2030))
    survivant, rapports = M._couple(inapte, simulateur, "v10", "cnav_inaptitude")
    assert len(survivant.survies) == 5
    for courbe in survivant.survies:
        assert courbe == pytest.approx((1.0, 0.75, 0.5), rel=1e-12)
    assert rapports == pytest.approx([1.5 / 1.7] * 5, rel=1e-12)
    # Nées de 1963 à 1967 : 62 ans de 2025 à 2027, 63 en 2029 et 2030.
    assert {(age, annee) for age, annee, _ in mortalite.appels} == {
        (62, 2025.0), (62, 2026.0), (62, 2027.0), (63, 2029.0), (63, 2030.0)}
    assert {population for _, _, population in mortalite.appels} == {
        None, "v10", "cnav_inaptitude"}

    survivant, _ = M._couple(replace(inapte, code="x"), simulateur, "v10")
    for courbe in survivant.survies:
        assert courbe == pytest.approx((1.0, 0.9 / 0.8, 0.6 / 0.4), rel=1e-12)


def test_chaque_couple_a_le_vingtile_que_la_page_donne_a_sa_carriere():
    """Le diviseur de la page range chaque carrière au vingtile où son salaire
    la place : la somme de ses revenus cotisés, rapportée à celle des salaires
    moyens des mêmes années (`Convertisseur.population_de`, sous le défaut du
    site) ; sa survie suit ce vingtile. Le script prend le même, sur la carrière
    que la page construit. Au 19 octobre 2026, le salarié au salaire moyen né
    en 1965, d'un salaire moyen écrit, que le treizième vingtile range, a une
    carrière que la page range au quatorzième : jusqu'à ce jour, le script
    rangeait le niveau écrit (`CasType.niveau_relatif`)."""
    commun = M._simulateur(None)
    cas = tuple(un for un in GRILLE_DU_COUT if un.code == "salaire_moyen")
    vingtiles = M._vingtiles(commun, cas, "droit")
    defaut = Simulateur(Parametres()).pour_la_projection()
    attendu = defaut.convertisseur.population_de(
        carriere_de_la_grille(defaut, cas[0], 1965, "droit"))
    assert attendu is not None
    assert vingtiles["salaire_moyen", 1965] == attendu


def test_la_grille_est_celle_que_la_page_pese():
    """Le script relit la grille que la page Coût pèse : les cas types de la
    page Cas types et leurs variantes — l'agent sédentaire de la CNRACL, les
    actifs et les super-actifs de l'État, l'inapte et l'ex-invalide de la
    Cnav. Jusqu'au 19 octobre 2026, il n'en relisait que les cas types, et en
    perdait cinq, dont les poids de la page pesaient pourtant leur caisse."""
    assert M.GRILLE is inspect.signature(calculer_cout).parameters["cas_types"].default


def test_un_point_de_pib_en_vaut_le_centieme():
    """Le PIB des lignes du solde est en millions d'euros courants : 2 991
    milliards en 2025 font un point de 29,9 milliards, 30 à l'euro près du
    script. Jusqu'au 19 octobre 2026, il imprimait le PIB entier pour un
    point. Sans PIB publié, rien."""
    annees = [SimpleNamespace(annee=2025, pib=2_991_000.0),
              SimpleNamespace(annee=2026, pib=0.0)]
    assert M._point_de_pib(annees) == "Un point de PIB vaut 30 Md€ au PIB de 2025."
    assert M._point_de_pib(annees[1:]) == ""
