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

Il ne fait plus tourner le moteur Python d'une carrière (action 161) : ses
carrières se datent, se bâtissent et se simulent au portage, par le pont, qui
rend pour lui les capitaux d'un compte (``pont.grille_du_cout``, sous
``capitaux``) et le niveau de salaire d'une carrière
(``conversion.niveau_relatif``, par ``pont.droit``).
"""

from __future__ import annotations

import inspect
import shutil
import sys
import textwrap
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import entrees_du_moteur  # noqa: E402
import mortalite_population as M  # noqa: E402
from outils_pont import droit_et_refait  # noqa: E402
from retraite_notionnelle import pont  # noqa: E402
from retraite_notionnelle.castypes import (GRILLE_DU_COUT, carriere_de_la_grille,  # noqa: E402
                                           primes_projetees_en_donnees)
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


def test_aux_scenarios_3_et_5_le_diviseur_ne_touche_que_le_compte_ouvert_a_la_bascule():
    """Les scénarios 3 et 5 gardent au stock d'avant la bascule le droit en
    vigueur (`ScenarioNotionnel._deja_liquide`), et les droits acquis à la
    bascule entrent au compte par le diviseur de leur vingtile et en sortent
    par lui (`_droits_acquis`) : seule la part de la pension que porte le
    compte ouvert à la bascule sent le diviseur du vingtile. Un couple dont le
    rapport des diviseurs vaut un demi, et dont ce compte porte le quart de la
    pension au scénario 3, les trois quarts au scénario 5 : sous le diviseur
    de son vingtile, sa pension en garde 0,25 × 0,5 + 0,75 = 0,875 au
    scénario 3, 0,75 × 0,5 + 0,25 = 0,625 au scénario 5, la moitié au
    scénario 2, qui n'a pas de droits acquis ; partie avant la bascule, toute.
    Le flux de 2030 n'en touche que la cohorte de 1966. Jusqu'au 23 octobre
    2026, le script appliquait le rapport à toute la pension (action 138,
    étape 7, note « la part ouverte à la bascule »)."""
    cles = ["notionnel_retroactif", "notionnel_prospectif", "notionnel_prospectif_employeur"]
    datee = Pensionne(code="x", generation=1965, annee_liquidation=2028,
                      pensions=dict(zip(cles, (2.0, 4.0, 8.0))),
                      propre=_REPORTE, bascule=2026, departs=_DEPARTS)
    rapports = (0.5,) * 5
    ouvertes = {("x", 1965): dict(zip(cles, (1.0, 0.25, 0.75)))}
    masses = M._masses([(datee, rapports)], {"x": 1.0}, _Population(), 2030, cles,
                       ouvertes=ouvertes)
    # Nées en 1963, 1964, 1965 et 1966 : 67, 66, 65 et 64 ans en 2030.
    tetes = 67 + 66 + 65 + 64
    for cle, pension, garde in zip(cles, (2.0, 4.0, 8.0), (0.5, 0.875, 0.625)):
        for survie in ("generale", "vrai"):
            assert masses[cle][f"{survie}_commun"] == pytest.approx(pension * tetes, rel=1e-12)
            assert masses[cle][f"{survie}_propre"] == pytest.approx(
                garde * pension * tetes, rel=1e-12)

    flux = M._masses([(datee, rapports)], {"x": 1.0}, _Population(), 2030, cles, depuis=2030,
                     ouvertes=ouvertes)
    assert flux["notionnel_prospectif"]["generale_propre"] == pytest.approx(
        4.0 * (67 + 66 + 65) + 4.0 * 64 * 0.875, rel=1e-12)

    partie = {("x", 1965): dict(zip(cles, (1.0, 0.0, 0.0)))}
    avant = M._masses([(datee, rapports)], {"x": 1.0}, _Population(), 2030, cles,
                      ouvertes=partie)
    for cle in cles[1:]:
        assert avant[cle]["generale_propre"] == pytest.approx(
            avant[cle]["generale_commun"], rel=1e-12)


def test_la_part_ouverte_a_la_bascule_se_lit_sur_le_compte_de_la_simulation():
    """La part de la pension que porte le compte ouvert à la bascule se lit
    sur la simulation de la carrière que la page construit : un, moins la part
    de son capital que portent les droits acquis à la bascule
    (`capital_droits_acquis`, `capital_notionnel`). Le salarié au salaire
    moyen né en 1955 part en 2017, avant la bascule de 2026 : les scénarios 3
    et 5 lui gardent le droit en vigueur, rien n'y sent le diviseur. Né en
    2005, il entre au travail l'année de la bascule, sans rien d'acquis avant
    elle : tout le sent. Né en 1965, parti en 2028, il est entre les deux, et
    plus près de un au scénario 5, dont le compte reçoit aussi la part
    patronale, sur les mêmes droits acquis. Les scénarios 2, 4 et 6 n'ont pas
    de droits acquis : tout le sent."""
    cas = tuple(un for un in GRILLE_DU_COUT if un.code == "salaire_moyen")
    parts = M._parts_ouvertes(M._simulateur(None), cas, "droit")
    prospectifs = ("notionnel_prospectif", "notionnel_prospectif_employeur")
    retroactifs = ("notionnel_retroactif", "notionnel_retroactif_employeur",
                   "notionnel_liberal")
    for cle in prospectifs:
        assert parts["salaire_moyen", 1955][cle] == 0.0
        assert parts["salaire_moyen", 2005][cle] == 1.0
    assert 0.0 < parts["salaire_moyen", 1965]["notionnel_prospectif"] < (
        parts["salaire_moyen", 1965]["notionnel_prospectif_employeur"]) < 1.0
    for generation in (1955, 1965, 2005):
        for cle in retroactifs:
            assert parts["salaire_moyen", generation][cle] == 1.0


def test_un_point_de_pib_en_vaut_le_centieme():
    """Le PIB des lignes du solde est en millions d'euros courants : 2 991
    milliards en 2025 font un point de 29,9 milliards, 30 à l'euro près du
    script. Jusqu'au 19 octobre 2026, il imprimait le PIB entier pour un
    point. Sans PIB publié, rien."""
    annees = [SimpleNamespace(annee=2025, pib=2_991_000.0),
              SimpleNamespace(annee=2026, pib=0.0)]
    assert M._point_de_pib(annees) == "Un point de PIB vaut 30 Md€ au PIB de 2025."
    assert M._point_de_pib(annees[1:]) == ""


# -- ce que le pont rend pour l'étude (action 161) ----------------------------------

sans_node = pytest.mark.skipif(shutil.which("node") is None,
                               reason="node absent : le pont ne se vérifie pas ici")


def _baties(simulateur, code: str, generations, quoi: str = "carriere") -> dict[int, object]:
    """Les carrières d'un cas type de la grille, par génération, que le
    portage date et bâtit sous les paramètres de ``simulateur``
    (``pont.carrieres_de_la_grille``) ; ou, sous ``quoi``, celles que l'âge
    légal de la proposition en dérive (``reportee``)."""
    cas = next(un for un in GRILLE_DU_COUT if un.code == code)
    lues, refus = pont.carrieres_de_la_grille(
        [{"cle": str(generation), **cas.pour_le_portage(simulateur, generation),
          "rendre": "carriere"} for generation in generations],
        simulateur.parametres, primes_projetees_en_donnees(simulateur), "droit",
        pont.paquet_des_donnees(simulateur.parametres.racine_donnees))
    assert refus == {}
    return {generation: lues[str(generation)][quoi] for generation in generations}


@sans_node
def test_les_capitaux_d_un_compte_passent_le_pont():
    """Des scénarios que la demande nomme (``capitaux``), la grille du coût
    rend de plus, de chaque case, le capital du compte à la liquidation et ce
    qu'en portent les droits acquis à la bascule — ce que le déficit en lit
    (``_parts_ouvertes``, action 161) —, au bit près du jumeau
    (``cout._simulations_en_python``). Le salarié au salaire moyen né en 1955
    part en 2017, avant la bascule de 2026 : les scénarios 3 et 5 lui gardent
    le droit en vigueur, et tout son capital y est un droit acquis. Né en
    2005, il entre au travail l'année de la bascule : rien d'acquis avant
    elle. Né en 1965, parti en 2028, il est entre les deux. Le scénario 2,
    rétroactif, n'a pas de droits acquis. Sans ``capitaux``, rien."""
    from retraite_notionnelle import cout

    simulateur = Simulateur(Parametres()).pour_la_projection()
    cas = [{"cle": str(generation), "carriere": carriere, "propositions": {}}
           for generation, carriere in _baties(simulateur, "salaire_moyen",
                                               (1955, 1965, 2005)).items()]
    scenarios = [cle for cle, _ in cout.SCENARIOS]
    capitaux = ("notionnel_retroactif", "notionnel_prospectif",
                "notionnel_prospectif_employeur")
    paquet = pont.paquet_des_donnees()
    lus, echecs = pont.grille_du_cout(cas, scenarios, simulateur.parametres, paquet,
                                      capitaux=capitaux)
    attendus, refus = cout._simulations_en_python(simulateur, cas, scenarios,
                                                  capitaux=capitaux)
    assert not echecs and not refus
    assert lus == attendus
    for lu in lus.values():
        assert set(lu["capitaux"]) == set(capitaux)
        for capital in lu["capitaux"].values():
            assert set(capital) == {"capital_droits_acquis", "capital_notionnel"}
            assert all(type(nombre) is float for nombre in capital.values())
            assert capital["capital_notionnel"] > 0.0
    for generation in ("1955", "1965", "2005"):
        assert lus[generation]["capitaux"]["notionnel_retroactif"]["capital_droits_acquis"] == 0.0
    for scenario in capitaux[1:]:
        parti = lus["1955"]["capitaux"][scenario]
        assert parti["capital_droits_acquis"] == parti["capital_notionnel"]
        assert lus["2005"]["capitaux"][scenario]["capital_droits_acquis"] == 0.0
        entre = lus["1965"]["capitaux"][scenario]
        assert 0.0 < entre["capital_droits_acquis"] < entre["capital_notionnel"]
    sans, _ = pont.grille_du_cout(cas[:1], scenarios, simulateur.parametres, paquet)
    assert sans["1955"]["capitaux"] == {}


@sans_node
def test_le_pont_rend_le_niveau_de_salaire_d_une_carriere():
    """Le niveau de salaire d'une carrière est la somme de ses revenus
    cotisés rapportée à celle des salaires moyens des mêmes années
    (``conversion.niveau_relatif``) : pour une carrière d'un seul statut à
    deux fois le salaire moyen, sans profil, deux ; pour la carrière d'un cas type que le
    portage a bâtie, passée en données, ce que rend son jumeau, au bit près —
    le salarié au SMIC est sous le salaire moyen, le cadre au-dessus."""
    simulateur = Simulateur(Parametres()).pour_la_projection()
    double = pont.CarriereSimple({
        "annee_naissance": 1975, "sexe": "F", "affiliation": "salarie_prive_non_cadre",
        "age_debut": 22, "age_liquidation": 64, "niveau_salaire": 2.0,
        "profil_carriere": "plat", "jour_naissance": 15})
    appels = {"double": ("conversion.niveau_relatif", pont.SIMULATEUR, double)}
    for code in ("smic_carriere_complete", "cadre"):
        appels[code] = ("conversion.niveau_relatif", pont.SIMULATEUR,
                        _baties(simulateur, code, (1975,))[1975])
    lus, refus = droit_et_refait(appels, simulateur.parametres)
    assert refus == {}
    assert lus["double"] == pytest.approx(2.0, rel=1e-12)
    assert 0.0 < lus["smic_carriere_complete"] < 1.0 < lus["cadre"]


# -- l'étude par le pont (action 161) ------------------------------------------------


@sans_node
def test_la_mesure_sert_la_proposition_sur_l_esperance_de_son_depart():
    """La mesure d'un cas type sous la table d'une population : la pension
    sous la table commune, multipliée par les années de rente que la
    population reçoit en plus. Le salarié au salaire moyen né en 1975, mesuré
    sous la mortalité des fonctionnaires civils de l'État, part avant 65 ans ;
    la proposition, dont l'âge légal est de 65 ans, reporte son départ, et sa
    rente se sert sur l'espérance de ce départ-là, à 65 ans. Le scénario 1 n'a
    pas de diviseur : sa pension ne bouge pas d'un euro sous la table des
    fonctionnaires, quand celle des comptes notionnels baisse."""
    population = "fonctionnaires_civils_etat"
    commun = M._simulateur(None)
    cas = next(un for un in GRILLE_DU_COUT if un.code == "salaire_moyen")
    resultat = M.mesurer(population, cas, 1975)
    assert resultat["age_liquidation"] < 65
    annees = resultat["esperance_population"] - resultat["esperance_commune"]
    assert annees > 0.0
    lignes = {ligne["numero"]: ligne for ligne in resultat["scenarios"]}
    assert set(lignes) == {1, 2, 3, 4, 5, 6}
    assert lignes[1]["pension_population"] == lignes[1]["pension_commune"]
    assert lignes[1]["ecart"] == 0.0
    for numero in (1, 2, 3, 4, 5):
        assert lignes[numero]["transfert_vie"] == lignes[numero]["pension_commune"] * annees
    for numero in (2, 4, 6):
        assert lignes[numero]["pension_population"] < lignes[numero]["pension_commune"]

    reportee = _baties(commun, cas.code, (1975,), "reportee")[1975]
    assert reportee.age_liquidation == 65
    date = reportee.annee_liquidation + reportee.fraction_annee_liquidation
    a_65_ans = (commun.mortalite.esperance_residuelle(65, date, population=population)
                - commun.mortalite.esperance_residuelle(65, date))
    assert a_65_ans != annees
    assert lignes[6]["transfert_vie"] == lignes[6]["pension_commune"] * a_65_ans


@sans_node
def test_l_etude_n_entre_plus_dans_le_moteur_python(tmp_path):
    """Ce que l'étude fait calculer d'une carrière se demande au portage : la
    mesure d'un cas type sous deux tables, par la sonde de la prose qui la
    lit, le niveau de salaire du salarié au SMIC, qui le range dans son
    vingtile, et, pour le déficit, le vingtile et la part ouverte à la bascule
    de chaque couple de la grille. Le relevé de ce qui entre dans le moteur
    Python (``entrees_du_moteur.relever``) est vide ; jusqu'au 12 novembre
    2026, l'étude y simulait, et les cas types y bâtissaient leur carrière
    pour elle (``tests/test_entrees_du_moteur.py``)."""
    script = tmp_path / "etude.py"
    script.write_text(textwrap.dedent(f'''\
        import sys
        sys.path.insert(0, {str(Path(M.__file__).parent)!r})
        import mesures_prose
        import mortalite_population as M
        from retraite_notionnelle.castypes import GRILLE_DU_COUT

        sonde = "mortalite_population?population={{}}&cas={{}}&generation=1975&quoi={{}}"
        mesures_prose.mesurer(sonde.format(
            "fonctionnaires_civils_etat", "fonctionnaire_sedentaire", "transfert"))
        mesures_prose.mesurer(sonde.format("vingtile", "smic_carriere_complete", "ecart"))
        grille = tuple(cas for cas in GRILLE_DU_COUT if cas.code == "salaire_moyen")
        M._vingtiles(M._simulateur(None), grille, "droit")
        M._parts_ouvertes(M._simulateur(None), grille, "droit")
        '''), encoding="utf-8")
    assert entrees_du_moteur.relever(script) == {}
