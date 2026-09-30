"""Le greffon qui répartit la suite sur les cœurs
(``retraite_notionnelle/pytest_parallele.py``) : des fichiers entiers et
lourds, visés seuls, se répartissent comme la suite ; un cas précis ou un
fichier léger reste en série."""

from __future__ import annotations

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
