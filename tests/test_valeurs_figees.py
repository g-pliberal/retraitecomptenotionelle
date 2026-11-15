"""Le témoin des valeurs : ce que le portage rend à une fonction Python, figé
(action 161, étape 8d).

Les confrontations de ``tests/test_pont.py`` faisaient refaire au moteur
Python, au bit près, ce que le portage rend à travers le pont — une grille du
coût, les dates d'une grille, des cas servis : une valeur Python, non la
sortie d'un script de ``tests/js/``. Le moteur Python se retirant, une
référence figée prend sa place : ``tests/temoins/valeurs.json`` porte, sous
le nom que le test lui donne, l'empreinte de la valeur, mise en données
(:func:`outils_valeurs.en_donnees`) et chaque flottant lu à douze chiffres
significatifs. Une valeur neuve s'y ajoute, et une valeur qui a bougé s'y
refait, par ``FIGER_VALEURS=1 python -m pytest <fichier>`` ;
``scripts/construire_temoins.py --valeurs`` relance ainsi chaque fichier qui
en fige une.
"""

from __future__ import annotations

import enum
import json
from dataclasses import dataclass

import outils_valeurs
import pytest
from outils_valeurs import empreinte_de_la_valeur, en_donnees, valeur_figee


@pytest.fixture
def temoin_vide(tmp_path, monkeypatch):
    chemin = tmp_path / "valeurs.json"
    chemin.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(outils_valeurs, "TEMOIN_DES_VALEURS", chemin)
    monkeypatch.delenv("FIGER_VALEURS", raising=False)
    # Le témoin même s'éprouve ici, sous la garde des présomptions aussi.
    monkeypatch.delenv("PRESOMPTIONS_DECALEES", raising=False)
    outils_valeurs.valeurs_figees.cache_clear()
    yield chemin
    outils_valeurs.valeurs_figees.cache_clear()


class Motif(enum.Enum):
    LEGAL = "legal"


@dataclass(frozen=True)
class Depart:
    code: str
    age: float
    motif: Motif
    annees: tuple


def test_une_valeur_python_se_met_en_donnees_sous_ses_types():
    """Une classe de données devient le dictionnaire de ses champs, sous le
    nom de sa classe ; une énumération, sa valeur ; un tuple, une liste ; un
    ensemble, la liste triée de ses éléments ; un dictionnaire aux clés qui ne
    sont pas des chaînes, la liste de ses couples triés. Un entier et un
    flottant restent distincts."""
    depart = Depart("smic", 62.5, Motif.LEGAL, (2020, 2021))
    assert en_donnees(depart) == {"__classe__": "Depart", "code": "smic", "age": 62.5,
                                  "motif": "legal", "annees": [2020, 2021]}
    assert en_donnees({("a", 1): {3, 1, 2}}) == [[["a", 1], [1, 2, 3]]]
    assert en_donnees({"b": 1, "a": (1.0,)}) == {"a": [1.0], "b": 1}
    assert empreinte_de_la_valeur(1) != empreinte_de_la_valeur(1.0)


def test_l_empreinte_d_une_valeur_tait_le_bruit_de_la_libm():
    """Un flottant s'y lit à douze chiffres significatifs : le dernier bit
    qu'une autre libm déplace n'y change rien, un centime si."""
    assert empreinte_de_la_valeur({"x": 0.1 + 0.2}) == empreinte_de_la_valeur({"x": 0.3})
    assert empreinte_de_la_valeur({"x": 1234.56}) != empreinte_de_la_valeur({"x": 1234.57})


def test_une_valeur_absente_du_temoin_arrete_le_test(temoin_vide):
    """Une valeur que le témoin ne porte pas n'a pas de référence : le test
    qui la donne s'arrête, et dit comment l'y ajouter."""
    with pytest.raises(AssertionError, match="FIGER_VALEURS=1"):
        valeur_figee("essai", {"x": 1.5})


def test_sous_figer_valeurs_la_valeur_s_ajoute_au_temoin(temoin_vide, monkeypatch):
    """Sous ``FIGER_VALEURS=1``, la valeur absente s'ajoute au témoin, sous
    son nom et le fichier du test qui la fige ; donnée de nouveau sans la
    variable, elle passe, et la fonction la rend telle quelle."""
    monkeypatch.setenv("FIGER_VALEURS", "1")
    valeur = {"x": 1.5}
    assert valeur_figee("essai", valeur) is valeur
    fige = json.loads(temoin_vide.read_text(encoding="utf-8"))
    assert fige == {"test_valeurs_figees.py::essai": {
        "valeur": empreinte_de_la_valeur(valeur)}}
    monkeypatch.delenv("FIGER_VALEURS")
    outils_valeurs.valeurs_figees.cache_clear()
    assert valeur_figee("essai", {"x": 1.5}) == {"x": 1.5}


def test_une_valeur_qui_bouge_arrete_le_test_et_se_refait_sous_figer(temoin_vide,
                                                                      monkeypatch):
    """Ce que le portage rend n'est plus ce que le témoin porte : le test
    s'arrête, nomme la valeur, et dit comment refaire le témoin si le
    déplacement est voulu ; sous ``FIGER_VALEURS=1``, la valeur s'y refait."""
    temoin_vide.write_text(json.dumps({"test_valeurs_figees.py::essai": {
        "valeur": "0" * 16}}), encoding="utf-8")
    with pytest.raises(AssertionError, match="essai.*construire_temoins.py --valeurs"):
        valeur_figee("essai", {"x": 1.5})
    monkeypatch.setenv("FIGER_VALEURS", "1")
    valeur_figee("essai", {"x": 1.5})
    fige = json.loads(temoin_vide.read_text(encoding="utf-8"))
    assert fige["test_valeurs_figees.py::essai"]["valeur"] == empreinte_de_la_valeur(
        {"x": 1.5})


def test_sous_la_garde_des_presomptions_le_temoin_se_tait(temoin_vide, monkeypatch):
    """Le témoin fige ce que le portage rend sous les présomptions du
    vocabulaire ; la garde des présomptions (``PRESOMPTIONS_DECALEES``,
    ``tests/conftest.py``) les décale, du Python comme du portage. La
    confrontation au moteur Python que le témoin remplace tenait sous elle,
    les deux côtés lisant les mêmes valeurs décalées ; le témoin, lui, ne
    peut que s'en écarter : sous la garde, il n'est ni lu ni écrit, et les
    autres assertions du test restent seules juges."""
    from conftest import PRESOMPTIONS_DECALEES

    temoin_vide.write_text(json.dumps({"test_valeurs_figees.py::essai": {
        "valeur": "0" * 16}}), encoding="utf-8")
    monkeypatch.setenv(PRESOMPTIONS_DECALEES, "1")
    monkeypatch.setenv("FIGER_VALEURS", "1")
    assert valeur_figee("essai", {"x": 1.5}) == {"x": 1.5}
    assert valeur_figee("absente", 2.0) == 2.0
    assert json.loads(temoin_vide.read_text(encoding="utf-8")) == {
        "test_valeurs_figees.py::essai": {"valeur": "0" * 16}}


def test_chaque_valeur_figee_l_est_par_un_test_qui_la_nomme():
    """Chaque nom du témoin désigne un fichier de tests qui fige une valeur :
    une valeur qu'aucun test ne fige plus en sort, quand le témoin se refait
    (``scripts/construire_temoins.py --valeurs``)."""
    racine = outils_valeurs.TEMOIN_DES_VALEURS.parents[1]
    fichiers = outils_valeurs.fichiers_qui_figent()
    assert fichiers and all((racine / fichier).is_file() for fichier in fichiers)
    assert {nom.partition("::")[0] for nom in outils_valeurs.valeurs_figees()} <= set(fichiers)


def test_un_test_fige_aussi_par_une_fixture_ou_une_aide_qui_fige():
    """Un test fige une valeur par son corps, mais aussi par une fixture ou une
    aide de son fichier qui appelle :func:`valeur_figee` : refait à neuf, le
    témoin le relance aussi, sans quoi ses valeurs en sortiraient (les
    dispenses de ``test_independants.py``, étape 8p)."""
    source = (
        "import pytest\n"
        "@pytest.fixture\n"
        "def figeur(request):\n"
        "    return lambda v: valeur_figee(request.node.name, v)\n"
        "def _aide(v): return valeur_figee('aide', v)\n"
        "def _par_l_aide(v): return _aide(v)\n"
        "def test_par_son_corps(): valeur_figee('x', 1)\n"
        "def test_par_la_fixture(figeur): figeur(1)\n"
        "def test_par_une_aide(): _par_l_aide(1)\n"
        "def test_sans(): assert True\n")
    assert outils_valeurs.tests_qui_figent_dans(source) == [
        "test_par_son_corps", "test_par_la_fixture", "test_par_une_aide"]
    figent = set(outils_valeurs.tests_qui_figent())
    for nom in outils_valeurs.valeurs_figees():
        fichier, _, valeur = nom.partition("::")
        if valeur.startswith("test_"):
            assert f"{fichier}::{valeur.partition('[')[0]}" in figent, nom


def test_le_temoin_se_refait_a_neuf_en_relancant_les_tests_qui_figent():
    """``scripts/construire_temoins.py`` refait le témoin des valeurs en
    relançant chaque fichier qui fige une valeur sous ``FIGER_VALEURS=1``, sur
    un témoin vide, à part : une valeur qu'aucun test ne fige plus en sort, et
    le témoin du dépôt n'est pas touché tant que le script ne l'écrit pas."""
    import importlib.util

    racine = outils_valeurs.TEMOIN_DES_VALEURS.parents[2]
    chemin = racine / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    construire_temoins = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(construire_temoins)
    lancees = []

    def lancer(commande, cwd, env, **_):
        lancees.append(commande)
        assert env["FIGER_VALEURS"] == "1" and cwd == racine
        temoin = outils_valeurs.Path(env["TEMOIN_DES_VALEURS"])
        assert json.loads(temoin.read_text(encoding="utf-8")) == {}
        temoin.write_text(json.dumps({"test_pont.py::essai": {"valeur": "1" * 16}}),
                          encoding="utf-8")

    assert construire_temoins.valeurs(lancer) == {"test_pont.py::essai": {"valeur": "1" * 16}}
    [commande] = lancees
    assert commande[1:3] == ["-m", "pytest"]
    assert "tests/test_pont.py::test_le_pont_rend_des_cases_ce_que_le_temoin_des_valeurs_porte" in (
        commande)
    assert not any(morceau.endswith(".py") for morceau in commande[3:]), (
        "seuls les tests qui figent se relancent, non leurs fichiers entiers")
