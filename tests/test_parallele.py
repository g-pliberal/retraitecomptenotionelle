"""Le greffon qui répartit la suite sur les cœurs
(``retraite_notionnelle/pytest_parallele.py``) : des fichiers entiers et
lourds, visés seuls, se répartissent comme la suite ; un cas précis ou un
fichier léger reste en série. Et la suite se découpe en tranches, une par
travail de la course de GitHub (``--tranche 2/4``, action 135)."""

from __future__ import annotations

import pytest

from retraite_notionnelle import pytest_parallele as greffon


def test_seuls_les_fichiers_entiers_et_lourds_se_repartissent(tmp_path):
    lourd = tmp_path / "test_lourd.py"
    lourd.write_text("#" * (greffon.POIDS_REPARTI + 1), encoding="utf-8")
    leger = tmp_path / "test_leger.py"
    leger.write_text("# une règle", encoding="utf-8")
    assert greffon._lourdes([str(lourd)])
    assert greffon._lourdes([str(tmp_path)])
    assert not greffon._lourdes([str(leger)])
    assert not greffon._lourdes([f"{lourd}::test_quelconque"])


# -- la suite en tranches (action 135) ----------------------------------------


def test_les_tranches_se_partagent_les_fichiers_selon_leur_duree():
    """Le fichier le plus long d'abord, chacun dans la tranche la moins
    chargée, la première à égalité. Posé à la main sur cinq fichiers de 10, 7,
    5, 4 et 3 secondes, en deux tranches : a (10) ; b (7) ; c avec b (12) ;
    d avec a (14) ; e avec b et c (15). Soit 14 et 15 secondes."""
    durees = {"tests/a.py": 10, "tests/b.py": 7, "tests/c.py": 5, "tests/d.py": 4,
              "tests/e.py": 3}
    assert greffon.repartir(sorted(durees), durees, 2) == {
        "tests/a.py": 1, "tests/d.py": 1,
        "tests/b.py": 2, "tests/c.py": 2, "tests/e.py": 2}


def test_un_fichier_sans_duree_connue_pese_une_seconde():
    """Un fichier né depuis la dernière mesure, ou une suite jamais mesurée :
    une seconde chacun, et les fichiers se suivent alors d'une tranche à
    l'autre, dans l'ordre de leurs noms."""
    fichiers = [f"tests/{nom}.py" for nom in "abcde"]
    assert greffon.repartir(fichiers, {}, 2) == {
        "tests/a.py": 1, "tests/b.py": 2, "tests/c.py": 1, "tests/d.py": 2, "tests/e.py": 1}
    # Deux secondes pèsent plus qu'un fichier inconnu, qui pèse plus qu'une demie.
    assert greffon.repartir(["tests/n.py", "tests/a.py", "tests/z.py"],
                            {"tests/z.py": 2, "tests/a.py": 0.5}, 3) == {
        "tests/z.py": 1, "tests/n.py": 2, "tests/a.py": 3}


def test_les_durees_se_lisent_d_un_tableau_a_deux_colonnes():
    texte = "# fichier\tsecondes\ntests/a.py\t12\n\ntests/b.py\t3\n"
    assert greffon.lire_durees(texte) == {"tests/a.py": 12.0, "tests/b.py": 3.0}


@pytest.mark.parametrize("choix", ["0/2", "3/2", "1", "a/b", "1/0"])
def test_une_tranche_mal_dite_arrete_la_suite(choix):
    """Une tranche hors de ses bornes ne jouerait aucun test, et dirait vert."""
    with pytest.raises(pytest.UsageError):
        greffon.lire_tranche(choix)


class _Config:
    def __init__(self, racine, tranche):
        self.rootpath, self._tranche, self.ecartes = racine, tranche, []
        self.hook = self

    def getoption(self, nom, defaut=None):
        return self._tranche if nom == "tranche" else defaut

    def pytest_deselected(self, items):
        self.ecartes += items


class _Test:
    def __init__(self, nodeid):
        self.nodeid = nodeid


def test_chaque_test_se_joue_dans_une_tranche_et_une_seule(tmp_path):
    """Les tranches d'une course jouent ensemble toute la suite, chaque test
    une fois, et tous les tests d'un fichier dans la même, pour que les
    calculs qu'ils partagent ne se fassent qu'une fois. Les durées se lisent
    dans ``.github/durees_suite.tsv``, que la course écrit."""
    (tmp_path / ".github").mkdir()
    (tmp_path / greffon.DUREES).write_text(
        "tests/test_a.py\t10\ntests/test_b.py\t7\ntests/test_c.py\t5\n", encoding="utf-8")
    noms = ["tests/test_a.py::test_1", "tests/test_b.py::test_1", "tests/test_b.py::T::test_2",
            "tests/test_c.py::test_1[x]", "tests/test_d.py::test_1"]
    joues = {}
    for rang in (1, 2):
        tests = [_Test(nom) for nom in noms]
        config = _Config(tmp_path, f"{rang}/2")
        greffon.pytest_collection_modifyitems(config, tests)
        joues[rang] = [t.nodeid for t in tests]
        assert sorted(joues[rang] + [t.nodeid for t in config.ecartes]) == sorted(noms)
    # a (10), puis b (7), c avec b (12), et d, inconnu (1), avec a (11).
    assert joues == {1: [noms[0], noms[4]], 2: noms[1:4]}
    # Sans tranche, rien ne s'écarte.
    tests = [_Test(nom) for nom in noms]
    config = _Config(tmp_path, None)
    greffon.pytest_collection_modifyitems(config, tests)
    assert len(tests) == len(noms) and not config.ecartes
