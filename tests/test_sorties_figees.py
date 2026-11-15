"""Le témoin des sorties : ce que les scripts de comparaison du portage
écrivent, figé (action 161, étape 8c).

Les confrontations de la liquidation, du relevé, des durées et des
simulations entières faisaient refaire au moteur Python, au bit près, ce
qu'un script de ``tests/js/`` écrit du portage. Le moteur Python se retirant,
une référence figée prend sa place, comme le témoin des servis :
``tests/temoins/sorties.json`` porte, pour chaque entrée d'un script, l'entrée
elle-même et l'empreinte de ce que le script en écrit — l'empreinte seule :
les sorties du relevé pèsent vingt-deux mégaoctets. ``scripts/construire_temoins.py``
le refait en relançant chaque script. Une entrée neuve s'y ajoute par
``FIGER_SORTIES=1 python -m pytest <fichier>``.
"""

from __future__ import annotations

import json
import shutil

import outils_sorties
import pytest
from outils_sorties import empreinte_de_l_entree, empreinte_de_la_sortie, sortie_figee

SCRIPT = "comparer-liquidation.mjs"
REQUETE = {"naissance": "1960-03-15", "debut": "20", "liquidation": "64", "salaire": "1",
           "statut": "salarie_prive_non_cadre"}


@pytest.fixture
def temoin_vide(tmp_path, monkeypatch):
    chemin = tmp_path / "sorties.json"
    chemin.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(outils_sorties, "TEMOIN_DES_SORTIES", chemin)
    monkeypatch.delenv("FIGER_SORTIES", raising=False)
    outils_sorties.sorties_figees.cache_clear()
    yield chemin
    outils_sorties.sorties_figees.cache_clear()


def _sans_node():
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage n'écrit rien ici")


def test_l_empreinte_d_une_entree_tient_au_script_et_a_l_entree():
    """La même entrée, donnée à deux scripts, est deux entrées du témoin ;
    l'ordre de ses clés n'y fait rien."""
    assert empreinte_de_l_entree(SCRIPT, {"a": 1, "b": 2}) == empreinte_de_l_entree(
        SCRIPT, {"b": 2, "a": 1})
    assert empreinte_de_l_entree(SCRIPT, {"a": 1}) != empreinte_de_l_entree(
        "comparer-droit.mjs", {"a": 1})
    assert empreinte_de_l_entree(SCRIPT, {"a": 1}) != empreinte_de_l_entree(SCRIPT, {"a": 2})


def test_l_empreinte_d_une_sortie_tait_le_bruit_de_la_libm():
    """Un flottant s'y lit à douze chiffres significatifs : le dernier bit
    qu'une autre libm déplace n'y change rien, un centime si."""
    assert empreinte_de_la_sortie({"x": 0.1 + 0.2}) == empreinte_de_la_sortie({"x": 0.3})
    assert empreinte_de_la_sortie({"x": 1234.56}) != empreinte_de_la_sortie({"x": 1234.57})
    assert empreinte_de_la_sortie([1, "a"]) != empreinte_de_la_sortie(["a", 1])


def test_une_entree_absente_du_temoin_arrete_le_test(temoin_vide):
    """Une entrée que le témoin ne porte pas n'a pas de référence : le test qui
    la donne s'arrête, et dit comment l'y ajouter."""
    _sans_node()
    with pytest.raises(AssertionError, match="FIGER_SORTIES=1"):
        sortie_figee(SCRIPT, [REQUETE])


def test_sous_figer_sorties_l_entree_s_ajoute_au_temoin(temoin_vide, monkeypatch):
    """Sous ``FIGER_SORTIES=1``, l'entrée absente s'ajoute au témoin, avec
    l'empreinte de ce que le script en écrit ; donnée de nouveau sans la
    variable, elle passe, et le script en rend la sortie."""
    _sans_node()
    monkeypatch.setenv("FIGER_SORTIES", "1")
    [sortie] = sortie_figee(SCRIPT, [REQUETE])
    assert "liquidations" in sortie
    fige = json.loads(temoin_vide.read_text(encoding="utf-8"))
    empreinte = empreinte_de_l_entree(SCRIPT, REQUETE)
    assert fige == {empreinte: {"script": SCRIPT, "entree": REQUETE,
                                "sortie": empreinte_de_la_sortie(sortie)}}
    monkeypatch.delenv("FIGER_SORTIES")
    outils_sorties.sorties_figees.cache_clear()
    assert sortie_figee(SCRIPT, [REQUETE]) == [sortie]


def test_une_sortie_qui_bouge_arrete_le_test(temoin_vide):
    """Ce que le script écrit n'est plus ce que le témoin porte : le test
    s'arrête, nomme l'entrée, et dit comment refaire le témoin si le
    déplacement est voulu."""
    _sans_node()
    empreinte = empreinte_de_l_entree(SCRIPT, REQUETE)
    temoin_vide.write_text(json.dumps({empreinte: {
        "script": SCRIPT, "entree": REQUETE, "sortie": "0" * 16}}), encoding="utf-8")
    with pytest.raises(AssertionError, match="construire_temoins.py --sorties"):
        sortie_figee(SCRIPT, [REQUETE])


def test_le_temoin_refait_revient_a_l_octet():
    """Chaque script relancé sur ses entrées : le témoin revient à l'octet.
    C'est ce que la fabrique refait (``scripts/construire_temoins.py``)."""
    _sans_node()
    import importlib.util

    chemin = outils_sorties.TEMOIN_DES_SORTIES.parents[2] / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    construire_temoins = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(construire_temoins)
    figes = outils_sorties.sorties_figees()
    assert {entree["script"] for entree in figes.values()} >= {
        "comparer-liquidation.mjs", "comparer-droit.mjs", "simuler.mjs",
        "maximum-du-jour.mjs", "faire-vivre-retouchee.mjs", "simuler-parcours.mjs"}
    refaits = construire_temoins.sorties(figes)
    texte = json.dumps(refaits, ensure_ascii=False, sort_keys=True, indent=1) + "\n"
    assert texte == outils_sorties.TEMOIN_DES_SORTIES.read_text(encoding="utf-8")
