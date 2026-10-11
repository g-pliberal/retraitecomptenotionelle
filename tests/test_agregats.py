"""Ce que les trois pages qui agrègent lisent du modèle, figé sous la référence.

``data/derive/agregats.json`` est fabriqué par ``scripts/construire_donnees.py``
depuis le 11 octobre 2026 (action 150) : Coût, Carrières types et Droits non
cotisés ne montrent plus que la référence, et ne calculent plus chez le
lecteur. Ces tests disent que la table porte ce que le modèle calcule, que les
deux lecteurs — ``donnees/agregats.py`` et ``moteur/js/agregats.js`` — en
lisent la même chose, et qu'elle refuse ce qu'elle ne porte pas.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.castypes import CAS_TYPES, GENERATIONS, calculer_cas_types
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.donnees.agregats import charger_agregats
from retraite_notionnelle.web.site import disponible, site

AGREGATS = charger_agregats(RACINE_DONNEES)

#: Les systèmes que le site compare au système actuel, ceux que la table porte.
COMPARES = ("notionnel_retroactif", "notionnel_retroactif_employeur", "notionnel_liberal")

sans_node = pytest.mark.skipif(not disponible(), reason="node absent : le site ne se lit pas")


@pytest.fixture(scope="module")
def contexte():
    return Contexte()


@pytest.fixture(scope="module")
def grille(contexte):
    return calculer_cas_types(contexte.simulateur())


# -- les carrières types -------------------------------------------------------


def test_la_grille_figee_est_celle_que_le_modele_calcule(grille):
    figee = AGREGATS.cas_types
    assert figee.generations == GENERATIONS
    assert set(figee.resultats) == set(grille.resultats)
    assert figee.echecs == grille.echecs
    for cle, comparaison in grille.resultats.items():
        case = figee.resultats[cle]
        assert case.carriere.annee_liquidation == comparaison.carriere.annee_liquidation
        for scenario in COMPARES:
            assert case.variation_totale(scenario) == comparaison.variation_totale(scenario)
            assert (case.carriere_de(scenario).annee_liquidation
                    == comparaison.carriere_de(scenario).annee_liquidation), (cle, scenario)


def test_les_cas_figes_sont_ceux_du_modele(contexte):
    figee = AGREGATS.cas_types
    assert [cas.code for cas in figee.cas] == [cas.code for cas in CAS_TYPES]
    simulateur = contexte.simulateur()
    for cas in CAS_TYPES:
        fige = figee.cas_type(cas.code)
        assert (fige.libelle, fige.commentaire) == (cas.libelle, cas.commentaire)
        for generation in GENERATIONS:
            assert fige.age_liquidation(generation) == cas.age_liquidation_pour(
                simulateur, generation), (cas.code, generation)


def test_la_table_ne_rend_pas_ce_qu_elle_ne_porte_pas():
    """Un zéro à la place d'une lecture absente tromperait la page sans bruit."""
    case = next(iter(AGREGATS.cas_types.resultats.values()))
    with pytest.raises(KeyError, match="absent de la table figée"):
        case.variation_totale("notionnel_prospectif")
    with pytest.raises(KeyError, match="absent de la table figée"):
        AGREGATS.cas_types.cas_type("inconnu")


@sans_node
def test_les_deux_lecteurs_lisent_la_meme_grille():
    js = site().contexte.cas_types()
    figee = AGREGATS.cas_types
    assert tuple(js.generations) == figee.generations
    # Les tables du portage se lisent, d'ici, en dictionnaires.
    assert len(js.echecs) == len(figee.echecs)
    assert len(js.resultats) == len(figee.resultats)
    for (code, generation), case in figee.resultats.items():
        lue = js.resultats[f"{code}|{generation}"]
        assert lue.carriere.annee_liquidation == case.carriere.annee_liquidation
        for scenario in COMPARES:
            assert lue.variation_totale(scenario) == case.variation_totale(scenario)
            assert (lue.carriere_de(scenario).annee_liquidation
                    == case.carriere_de(scenario).annee_liquidation)
    for cas in figee.cas:
        lu = js.cas_type(cas.code)
        assert (lu.libelle, lu.commentaire) == (cas.libelle, cas.commentaire)
        assert [lu.age_liquidation(generation) for generation in figee.generations] == [
            cas.age_liquidation(generation) for generation in figee.generations]
