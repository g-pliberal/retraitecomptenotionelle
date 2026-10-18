"""Le pont : ce que la fabrique fait calculer au moteur JavaScript, par node.

La note de décision 0003 veut que le coût, la fabrique et les études fassent
tourner le moteur JavaScript au lieu du moteur Python, sous six conditions
(action 161, étape 5). La première lecture qui passe le pont est la grille des
carrières types de la table des agrégats, avec les deux départs que compare
Droits non cotisés (``scripts/construire_donnees.py``) ; ``test_agregats.py``
exige, à l'égalité exacte, que la table soit ce que le moteur Python calcule.
Ici : le pont rend au bit près ce que le moteur Python simule, chaque nombre
sous le type que le Python lui donne ; et, sans node, il s'arrête, sans repli
sur le moteur Python.
"""

from __future__ import annotations

import shutil

import pytest

from retraite_notionnelle import pont
from retraite_notionnelle.castypes import CAS_TYPES, carriere_de_la_grille, cases_de_la_grille
from retraite_notionnelle.contexte import Contexte

SCENARIOS = ("notionnel_retroactif", "notionnel_retroactif_employeur", "notionnel_liberal")

#: Des cases de la grille où passe ce que le pont fait traverser : un profil au
#: SMIC, des interruptions, des primes, la catégorie active, un non-salarié, un
#: exploitant ; plusieurs s'écartaient au dernier bit avant que le portage
#: calcule ses exponentielles comme la libm de Linux.
CASES = (("smic_carriere_complete", 1970), ("carriere_interrompue", 1970),
         ("fonctionnaire_actif", 1960), ("fonctionnaire_sedentaire", 2000),
         ("profession_liberale", 1960), ("exploitant_agricole", 2000), ("cadre", 2000))


def test_le_pont_rend_au_bit_pres_ce_que_le_moteur_python_simule():
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    simulateur = Contexte().simulateur()
    demandes, attendus = [], {}
    for code, generation in CASES:
        cas = next(cas for cas in CAS_TYPES if cas.code == code)
        carriere = carriere_de_la_grille(simulateur, cas, generation)
        comparaison = simulateur.simuler(carriere)
        cle = f"{code}|{generation}"
        demandes.append({"cle": cle, "options": cas.options(generation, carriere.age_liquidation)})
        attendus[cle] = {
            "annee_liquidation": comparaison.carriere.annee_liquidation,
            "annees_liquidation": {scenario: comparaison.carriere_de(scenario).annee_liquidation
                                   for scenario in SCENARIOS},
            "variations": {scenario: comparaison.variation_totale(scenario)
                           for scenario in SCENARIOS},
            "pension_annuelle": comparaison.actuel.pension_annuelle,
            "trimestres_requis": comparaison.actuel.trimestres_requis,
        }
    resultats, echecs = pont.carrieres(demandes, SCENARIOS)
    assert not echecs
    assert resultats == attendus
    for lu in resultats.values():
        assert type(lu["annee_liquidation"]) is int
        assert type(lu["trimestres_requis"]) is int
        assert type(lu["pension_annuelle"]) is float
        assert all(type(variation) is float for variation in lu["variations"].values())


def test_chaque_case_passe_au_portage_partant_a_l_age_que_le_pilote_fixe():
    """Le Python fixe l'âge de chaque départ et écarte ce que le droit écarte
    (``carriere_de_la_grille``) ; le portage simule. Sous les conventions du
    COR, la carrière d'un cas type se déforme en Python : rien ne passe."""
    simulateur = Contexte().simulateur()
    types = tuple(cas for cas in CAS_TYPES if cas.code in ("cadre", "carriere_interrompue"))
    options, echecs = cases_de_la_grille(simulateur, types, (1940, 2000))
    assert set(options) | set(echecs) == {(cas.code, generation)
                                         for cas in types for generation in (1940, 2000)}
    for cas in types:
        for generation in (1940, 2000):
            if (cas.code, generation) in options:
                carriere = carriere_de_la_grille(simulateur, cas, generation)
                assert options[(cas.code, generation)] == cas.options(
                    generation, carriere.age_liquidation)
    with pytest.raises(ValueError, match="COR"):
        cases_de_la_grille(simulateur.pour_la_projection(), types, (2000,))


def test_sans_node_le_pont_s_arrete_sans_repli(monkeypatch):
    monkeypatch.setattr(pont.shutil, "which", lambda nom: None)
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.carrieres([{"cle": "cadre|2000", "options": {}}], SCENARIOS)
