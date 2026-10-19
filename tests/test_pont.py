"""Le pont : ce que la fabrique fait calculer au moteur JavaScript, par node.

La note de décision 0003 veut que le coût, la fabrique et les études fassent
tourner le moteur JavaScript au lieu du moteur Python, sous six conditions
(action 161, étape 5). La première lecture qui passe le pont est la grille des
carrières types de la table des agrégats, avec les deux départs que compare
Droits non cotisés (``scripts/construire_donnees.py``) ; ``test_agregats.py``
exige, à l'égalité exacte, que la table soit ce que le moteur Python calcule.
Puis le bilan figé : la même grille, dont il tire les écarts médians, et les
carrières d'exemple de « Pourquoi changer », simulées comme le site simule une
saisie ; ``test_cout.py`` et le contrôle de ``test_affirmations.py`` exigent
de même la table du moteur Python. Ici : le pont rend au bit près ce que le
moteur Python simule, chaque nombre sous le type que le Python lui donne ; et,
sans node, il s'arrête, sans repli sur le moteur Python.
"""

from __future__ import annotations

import shutil

import pytest

from retraite_notionnelle import pont
from retraite_notionnelle.castypes import CAS_TYPES, carriere_de_la_grille, cases_de_la_grille
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.saisie import Saisie

SCENARIOS = ("notionnel_retroactif", "notionnel_retroactif_employeur", "notionnel_liberal")

#: Des cases de la grille où passe ce que le pont fait traverser : un profil au
#: SMIC, des interruptions, des primes, la catégorie active, un non-salarié, un
#: exploitant ; plusieurs s'écartaient au dernier bit avant que le portage
#: calcule ses exponentielles comme la libm de Linux.
CASES = (("smic_carriere_complete", 1970), ("carriere_interrompue", 1970),
         ("fonctionnaire_actif", 1960), ("fonctionnaire_sedentaire", 2000),
         ("profession_liberale", 1960), ("exploitant_agricole", 2000), ("cadre", 2000))

#: Des saisies comme celles que le bilan figé simule : la carrière d'exemple de
#: « Pourquoi changer » au SMIC, et un cadre à deux fois le salaire moyen.
SAISIES = (
    {"naissance": 1990, "statut": "salarie_prive_non_cadre", "debut": 22, "liquidation": 64,
     "salaire": 0.55, "unite_revenu": "moyen", "demandee": True},
    {"naissance": 1975, "statut": "salarie_prive_cadre", "debut": 24, "liquidation": 65,
     "salaire": 2.0, "unite_revenu": "moyen", "demandee": True},
)


def _aujourd_hui(aujourd_hui) -> dict | None:
    """Ce que les écarts médians lisent de la pension d'aujourd'hui d'un
    retraité, ou rien pour qui n'est pas encore parti."""
    if aujourd_hui is None:
        return None
    return {
        "pension_annuelle": aujourd_hui.pension("actuel"),
        "pensions_totales": {scenario: aujourd_hui.pension_totale(scenario)
                             for scenario in SCENARIOS},
        "rente_capitalisee_volontaire": aujourd_hui.rente_capitalisee_volontaire,
    }


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
            # Ce que les écarts médians du bilan lisent d'une case.
            "pensions_totales": {scenario: comparaison.pension_totale(scenario)
                                 for scenario in SCENARIOS},
            "rentes_volontaires": {scenario: comparaison.rente_capitalisee_volontaire(scenario)
                                   for scenario in SCENARIOS},
            "aujourd_hui": _aujourd_hui(comparaison.aujourd_hui),
        }
    resultats, echecs = pont.carrieres(demandes, SCENARIOS)
    assert not echecs
    assert resultats == attendus
    # Les deux sortes de cases : celles qui partiront, celles déjà parties.
    assert {lu["aujourd_hui"] is None for lu in resultats.values()} == {True, False}
    for lu in resultats.values():
        assert type(lu["annee_liquidation"]) is int
        assert type(lu["trimestres_requis"]) is int
        assert type(lu["pension_annuelle"]) is float
        for lecture in ("variations", "pensions_totales", "rentes_volontaires"):
            assert all(type(nombre) is float for nombre in lu[lecture].values()), lecture
        if lu["aujourd_hui"] is not None:
            assert type(lu["aujourd_hui"]["pension_annuelle"]) is float
            assert type(lu["aujourd_hui"]["rente_capitalisee_volontaire"]) is float
            assert all(type(nombre) is float
                       for nombre in lu["aujourd_hui"]["pensions_totales"].values())


def test_le_pont_simule_une_saisie_comme_le_site_au_bit_pres_du_moteur_python():
    """Les carrières d'exemple du bilan figé sont des saisies, que le portage
    simule comme le site (``Contexte.simuler``) : de chacune, la fiche de paie
    de l'année de référence sous le droit en vigueur, le passage aux euros
    constants, et la pension de chaque système demandé."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    contexte = Contexte()
    demandes, attendus = [], {}
    for rang, saisie in enumerate(SAISIES):
        comparaison = contexte.simuler(Saisie(**saisie))
        fiche = comparaison.remuneration.reference.droit_en_vigueur
        demandes.append({"cle": str(rang), "saisie": saisie})
        attendus[str(rang)] = {
            "fiche": {"annee": fiche.annee, "brut": fiche.brut, "net": fiche.net,
                      "retraite_totale": fiche.retraite_totale,
                      "retraite_employeur": fiche.retraite_employeur},
            "coefficient_euros_constants": comparaison.coefficient_euros_constants,
            "pension_annuelle": comparaison.actuel.pension_annuelle,
            "pensions": {scenario: getattr(comparaison, scenario).pension_annuelle
                         for scenario in SCENARIOS},
        }
    resultats, echecs = pont.saisies(demandes, SCENARIOS)
    assert not echecs
    assert resultats == attendus
    for lu in resultats.values():
        assert type(lu["fiche"]["annee"]) is int
        assert all(type(lu["fiche"][champ]) is float
                   for champ in ("brut", "net", "retraite_totale", "retraite_employeur"))
        assert type(lu["coefficient_euros_constants"]) is float
        assert type(lu["pension_annuelle"]) is float
        assert all(type(pension) is float for pension in lu["pensions"].values())


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
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.saisies([{"cle": "0", "saisie": SAISIES[0]}], SCENARIOS)
