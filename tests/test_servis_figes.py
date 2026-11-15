"""Le témoin des servis : ce que le portage sert aux confrontations du
scénario 1, figé (action 161, étape 8b).

Les tests qui demandent le scénario 1 au portage par :func:`outils_pont.servi_et_fige`
le faisaient refaire au moteur Python, au bit près : ce que leurs assertions
ne disaient pas, la confrontation le tenait. Le moteur Python se retirant,
une référence figée prend sa place (quatrième temps de la note de décision
0003) : ``tests/temoins/servis.json``, que ``scripts/construire_temoins.py``
refait de ses propres requêtes, comme les autres témoins, et dont le diff dit
ce qu'une règle a déplacé. Chaque cas demandé doit y être : un cas neuf s'y
ajoute par ``FIGER_SERVIS=1 python -m pytest <fichier>``.
"""

from __future__ import annotations

import json
import shutil

import pytest

import outils_pont
from outils_pont import empreinte_du_cas, servi_et_fige

CAS = {"cle": "un_cas", "requete": {"naissance": "1965-03-15", "liquidation": "64"}}


@pytest.fixture
def temoin_vide(tmp_path, monkeypatch):
    chemin = tmp_path / "servis.json"
    chemin.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(outils_pont, "TEMOIN_DES_SERVIS", chemin)
    monkeypatch.delenv("FIGER_SERVIS", raising=False)
    outils_pont.servis_figes.cache_clear()
    yield chemin
    outils_pont.servis_figes.cache_clear()


def _sans_node():
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne sert rien ici")


def test_l_empreinte_d_un_cas_ignore_sa_cle():
    """Deux fichiers nomment le même cas autrement : il n'est figé qu'une
    fois, sous l'empreinte de ce que le portage lit, sans la clé."""
    assert empreinte_du_cas(CAS) == empreinte_du_cas({**CAS, "cle": "autre"})
    assert empreinte_du_cas(CAS) != empreinte_du_cas(
        {**CAS, "requete": {**CAS["requete"], "liquidation": "65"}})
    assert empreinte_du_cas(CAS) != empreinte_du_cas({**CAS, "prolonger": False})


def test_un_cas_absent_du_temoin_arrete_le_test(temoin_vide):
    """Un cas que le témoin ne porte pas n'a pas de référence : le test qui le
    demande s'arrête, et dit comment l'y ajouter."""
    _sans_node()
    with pytest.raises(AssertionError, match="FIGER_SERVIS=1"):
        servi_et_fige([CAS])


def test_sous_figer_servis_le_cas_s_ajoute_au_temoin(temoin_vide, monkeypatch):
    """Sous ``FIGER_SERVIS=1``, le cas absent s'ajoute au témoin, sa requête et
    ce que le portage en sert ; demandé de nouveau sans la variable, il passe."""
    _sans_node()
    monkeypatch.setenv("FIGER_SERVIS", "1")
    servis, refus = servi_et_fige([CAS])
    assert refus == {}
    fige = json.loads(temoin_vide.read_text(encoding="utf-8"))
    assert list(fige) == [empreinte_du_cas(CAS)]
    entree = fige[empreinte_du_cas(CAS)]
    assert entree["cle"] == "un_cas"
    assert entree["cas"] == {"requete": CAS["requete"]}
    assert entree["servi"]["actuel"]["pension_annuelle"] == servis["un_cas"]["actuel"][
        "pension_annuelle"]
    monkeypatch.delenv("FIGER_SERVIS")
    outils_pont.servis_figes.cache_clear()
    assert servi_et_fige([{**CAS, "cle": "renomme"}])[1] == {}


def test_servi_et_fige_n_entre_pas_dans_le_moteur_python(monkeypatch):
    """La confrontation ne fait plus rien refaire au moteur Python : on
    empêche ici les saisies du moteur Python (``outils_pont.Saisies``), par
    où il refaisait chaque cas, de servir, et un cas figé passe."""
    _sans_node()

    def interdit(*_, **__):
        raise AssertionError("le moteur Python refait un cas")

    monkeypatch.setattr(outils_pont, "Saisies", interdit)
    [(empreinte, entree)] = list(outils_pont.servis_figes().items())[:1]
    servis, _ = servi_et_fige([{"cle": entree["cle"], **entree["cas"]}])
    assert empreinte == empreinte_du_cas({"cle": entree["cle"], **entree["cas"]})
    assert entree["cle"] in servis


def test_le_portage_resert_chaque_servi_fige_a_l_octet():
    """Toutes les requêtes du témoin, servies de nouveau par le portage : le
    fichier revient à l'octet sous Linux x86_64. C'est ce que la fabrique
    refait (``scripts/construire_temoins.py``) ; ailleurs, la libm du système
    déplace la dernière décimale de quelques flottants
    (:data:`outils_pont.TOLERANCE_DU_MOTEUR_PYTHON`)."""
    _sans_node()
    import importlib.util

    chemin = outils_pont.TEMOIN_DES_SERVIS.parents[2] / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    construire_temoins = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(construire_temoins)
    figes = outils_pont.servis_figes()
    assert len(figes) > 300
    refaits = construire_temoins.servis(figes)
    ecarts = [f"{empreinte}, {ecart}" for empreinte, entree in figes.items()
              for ecart in outils_pont.ecarts_d_ecriture(
                  refaits[empreinte], entree, tolerance=outils_pont.TOLERANCE_DU_MOTEUR_PYTHON)]
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"
    if not outils_pont.TOLERANCE_DU_MOTEUR_PYTHON:
        texte = json.dumps(refaits, ensure_ascii=False, sort_keys=True, indent=1) + "\n"
        assert texte == outils_pont.TEMOIN_DES_SERVIS.read_text(encoding="utf-8")
