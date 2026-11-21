"""Le témoin du droit : ce que le portage rend des appels du droit, figé
(action 161, étape 8e).

Les exemples d'OpenFisca et des caisses, et les tests qui appellent le droit
fonction par fonction à travers le pont (:func:`pont.droit`), faisaient
refaire chaque appel au jumeau Python, au bit près
(``outils_pont.droit_et_refait``). Le moteur Python se retirant, une
référence figée prend sa place : ``tests/temoins/droit.json`` porte, sous
l'empreinte de la demande (les appels, leurs carrières et les paramètres, mis
en données comme le pont les envoie), l'empreinte de ce que le portage en rend
et de ce qu'il en refuse, chaque flottant lu à douze chiffres significatifs
(:func:`outils_valeurs.empreinte_de_la_valeur`). Une demande neuve s'y
ajoute, et un rendu qui a bougé s'y refait, par
``FIGER_DROIT=1 python -m pytest <fichier>`` ;
``scripts/construire_temoins.py --droit`` relance ainsi chaque fichier qui
appelle le droit.
"""

from __future__ import annotations

import importlib.util
import json

import outils_pont
import pytest
from outils_pont import droit_et_fige, empreinte_de_la_demande
from outils_valeurs import empreinte_de_la_valeur

from retraite_notionnelle import pont


@pytest.fixture
def temoin_vide(tmp_path, monkeypatch):
    chemin = tmp_path / "droit.json"
    chemin.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(outils_pont, "TEMOIN_DU_DROIT", chemin)
    monkeypatch.delenv("FIGER_DROIT", raising=False)
    # Le témoin même s'éprouve ici, sous la garde des présomptions aussi.
    monkeypatch.delenv("PRESOMPTIONS_DECALEES", raising=False)
    outils_pont.droit_fige.cache_clear()
    yield chemin
    outils_pont.droit_fige.cache_clear()


@pytest.fixture
def portage(monkeypatch):
    """Un portage simulé, sans node : il rend le double du premier argument
    de chaque appel, et refuse un appel dont la fonction finit par
    ``refusee``."""
    rendus = {"facteur": 2.0}

    def droit(appels, parametres=None, paquet=None):
        lus = {cle: rendus["facteur"] * arguments[0] for cle, (fonction, *arguments)
               in appels.items() if not fonction.endswith("refusee")}
        refus = {cle: "refusé" for cle, (fonction, *_) in appels.items()
                 if fonction.endswith("refusee")}
        return lus, refus

    monkeypatch.setattr(outils_pont, "DROIT_DU_PORTAGE", droit)
    return rendus


APPELS = {"a": ("calendrier.en_mois", 1.5), "b": ("liquider.refusee", 3)}


def test_la_demande_a_l_empreinte_de_ce_que_le_pont_envoie():
    """Deux demandes qui envoient la même chose au portage ont la même
    empreinte ; une valeur, une clé ou des paramètres de plus la changent.
    Le moteur du scénario 1 s'y lit avec les tables qu'on lui prête."""
    assert empreinte_de_la_demande(dict(APPELS)) == empreinte_de_la_demande(dict(APPELS))
    assert empreinte_de_la_demande({"a": ("calendrier.en_mois", 1.5)}) != (
        empreinte_de_la_demande({"a": ("calendrier.en_mois", 2.5)}))
    assert empreinte_de_la_demande({"a": ("calendrier.en_mois", 1.5)}) != (
        empreinte_de_la_demande({"z": ("calendrier.en_mois", 1.5)}))
    moteur = {"a": ("ouvrir.duree_requise", pont.MOTEUR, 1960)}
    prete = {"a": ("ouvrir.duree_requise", pont.MOTEUR.pretant("x", "y"), 1960)}
    assert empreinte_de_la_demande(moteur) != empreinte_de_la_demande(prete)
    from retraite_notionnelle.config import Parametres

    assert empreinte_de_la_demande(moteur) != empreinte_de_la_demande(moteur, Parametres())


def test_une_demande_absente_du_temoin_arrete_le_test(temoin_vide, portage):
    """Une demande que le témoin ne porte pas n'a pas de référence : le test
    qui la fait s'arrête, et dit comment l'y ajouter."""
    with pytest.raises(AssertionError, match="FIGER_DROIT=1"):
        droit_et_fige(dict(APPELS))


def test_sous_figer_droit_la_demande_s_ajoute_au_temoin(temoin_vide, portage, monkeypatch):
    """Sous ``FIGER_DROIT=1``, la demande absente s'ajoute au témoin, sous
    son empreinte, avec les fonctions qu'elle appelle et l'empreinte de ce que
    le portage en rend et en refuse ; faite de nouveau sans la variable, elle
    passe, et la fonction rend ce que le portage rend."""
    monkeypatch.setenv("FIGER_DROIT", "1")
    assert droit_et_fige(dict(APPELS)) == ({"a": 3.0}, {"b": "refusé"})
    fige = json.loads(temoin_vide.read_text(encoding="utf-8"))
    assert fige == {empreinte_de_la_demande(dict(APPELS)): {
        "fonctions": ["calendrier.en_mois", "liquider.refusee"],
        "rendu": empreinte_de_la_valeur({"lus": {"a": 3.0}, "refus": {"b": "refusé"}})}}
    monkeypatch.delenv("FIGER_DROIT")
    outils_pont.droit_fige.cache_clear()
    assert droit_et_fige(dict(APPELS)) == ({"a": 3.0}, {"b": "refusé"})


def test_un_rendu_qui_bouge_arrete_le_test_et_se_refait_sous_figer(temoin_vide, portage,
                                                                   monkeypatch):
    """Le portage ne rend plus ce que le témoin porte, d'un ulp au-delà du
    bruit de la libm : le test s'arrête, nomme les fonctions appelées, et dit
    comment refaire le témoin si le déplacement est voulu ; sous
    ``FIGER_DROIT=1``, le rendu s'y refait. Le dernier bit qu'une autre libm
    déplace, lui, n'arrête rien."""
    monkeypatch.setenv("FIGER_DROIT", "1")
    droit_et_fige(dict(APPELS))
    monkeypatch.delenv("FIGER_DROIT")
    outils_pont.droit_fige.cache_clear()
    portage["facteur"] = 2.0 * (1 + 1e-15)
    droit_et_fige(dict(APPELS))
    portage["facteur"] = 2.0 * (1 + 1e-9)
    with pytest.raises(AssertionError, match="calendrier.en_mois.*construire_temoins.py --droit"):
        droit_et_fige(dict(APPELS))
    monkeypatch.setenv("FIGER_DROIT", "1")
    droit_et_fige(dict(APPELS))
    monkeypatch.delenv("FIGER_DROIT")
    outils_pont.droit_fige.cache_clear()
    droit_et_fige(dict(APPELS))


def test_sur_un_autre_paquet_il_n_y_a_rien_a_confronter(temoin_vide, portage):
    """Sur un paquet qui n'est pas celui du dépôt, le portage rend ce qu'il
    rend : le témoin ne porte que le paquet du dépôt."""
    assert droit_et_fige(dict(APPELS), paquet=b"{}") == ({"a": 3.0}, {"b": "refusé"})


def test_le_jumeau_python_du_droit_est_retire():
    """Plus aucun appel du droit ne se refait au moteur Python : les jumeaux
    du droit et l'aide qui les confrontait sont partis (action 161, étape
    8e)."""
    for nom in ("JUMEAUX_DU_DROIT", "droit_et_refait", "_simulateur_du_droit"):
        assert not hasattr(outils_pont, nom), nom


def test_chaque_fichier_qui_appelle_le_droit_se_relance_pour_refaire_le_temoin():
    """``scripts/construire_temoins.py --droit`` refait le témoin du droit en
    relançant chaque fichier de tests qui appelle :func:`droit_et_fige` sous
    ``FIGER_DROIT=1``, sur un témoin vide, à part : une demande qu'aucun test
    ne fait plus en sort, et le témoin du dépôt n'est pas touché tant que le
    script ne l'écrit pas."""
    racine = outils_pont.TEMOIN_DU_DROIT.parents[2]
    chemin = racine / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    construire_temoins = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(construire_temoins)
    lancees = []

    def lancer(commande, cwd, env, **_):
        lancees.append(commande)
        assert env["FIGER_DROIT"] == "1" and cwd == racine
        temoin = outils_pont.Path(env["TEMOIN_DU_DROIT"])
        assert json.loads(temoin.read_text(encoding="utf-8")) == {}
        temoin.write_text(json.dumps({"0" * 16: {"fonctions": [], "rendu": "1" * 16}}),
                          encoding="utf-8")

    assert construire_temoins.droit(lancer) == {"0" * 16: {"fonctions": [], "rendu": "1" * 16}}
    [commande] = lancees
    assert commande[1:3] == ["-m", "pytest"]
    assert "tests/test_oracle.py" in commande and "tests/test_droit_fige.py" not in commande
    assert commande[-len(outils_pont.fichiers_qui_appellent_le_droit()):] == [
        f"tests/{fichier}" for fichier in outils_pont.fichiers_qui_appellent_le_droit()]


def test_le_temoin_du_depot_est_ecrit_et_trie():
    """Le témoin du dépôt existe, chaque entrée porte ses fonctions et son
    rendu, et ses fonctions sont toutes celles que le pont relit."""
    figes = json.loads(outils_pont.TEMOIN_DU_DROIT.read_text(encoding="utf-8"))
    assert figes
    for entree in figes.values():
        assert set(entree) == {"fonctions", "rendu"}
        assert set(entree["fonctions"]) <= set(pont.LECTURES_DU_DROIT)


def test_sous_la_garde_des_presomptions_le_temoin_du_droit_se_tait(temoin_vide, portage,
                                                                    monkeypatch):
    """La garde des présomptions (``PRESOMPTIONS_DECALEES``,
    ``tests/conftest.py``) décale ce que le portage lit, et ce que les tests
    lui demandent : le témoin, figé sous les présomptions du vocabulaire, ne
    peut que s'en écarter. Sous elle, il n'est ni lu ni écrit, comme le témoin
    des valeurs ; le portage rend ce qu'il rend."""
    from conftest import PRESOMPTIONS_DECALEES

    monkeypatch.setenv(PRESOMPTIONS_DECALEES, "1")
    monkeypatch.setenv("FIGER_DROIT", "1")
    assert droit_et_fige(dict(APPELS)) == ({"a": 3.0}, {"b": "refusé"})
    assert json.loads(temoin_vide.read_text(encoding="utf-8")) == {}


def test_le_temoin_se_refait_aussi_des_tests_qui_passent_par_l_oracle():
    """``scripts/simulateurs.py`` interroge le droit par les fonctions de
    ``tests/test_oracle.py``, qui confrontent au témoin : ``test_simulateurs.py``
    lui fait des demandes sans nommer ``droit_et_fige``. Le témoin refait à
    neuf (``construire_temoins.py --droit``) relance aussi ce fichier, sans
    quoi ses demandes en sortent et la suite tombe."""
    fichiers = outils_pont.fichiers_qui_appellent_le_droit()
    assert {"test_oracle.py", "test_simulateurs.py"} <= set(fichiers)
    assert "test_droit_fige.py" not in fichiers


def test_le_temoin_se_refait_aussi_des_preuves_de_la_carte_de_justesse():
    """``tests/test_justesse.py`` rejoue les cas des preuves par
    ``_confronter`` de ``tests/test_oracle.py``, sans nommer ``droit_et_fige`` :
    le témoin refait à neuf le relance aussi, sans quoi les demandes des
    grilles de l'âge légal en sortent et la suite tombe (21 novembre 2026)."""
    assert "test_justesse.py" in outils_pont.fichiers_qui_appellent_le_droit()
