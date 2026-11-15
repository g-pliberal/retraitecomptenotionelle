"""Le partage des 23 points entre le salarié et l'employeur, lu sur la fiche de paie du portage.

`scripts/partage_taux_unique.py` a servi à trancher le partage le 20 septembre
2026 (le partage A, ``Parametres.part_salariale_taux_unique``). La fiche de paie
qu'il lit est celle de ``moteur/js/remuneration.js``, que le pont sert
(``pont.fiches_de_paie``) : le moteur Python n'y calcule rien (action 161,
étape 6e). Les parts se confrontent à ce que le docstring de l'étude et la
décision en disent : 11,31 points sur la fiche du salarié non cadre, 16,67 chez
son employeur, 27,98 en tout ; le partage A garde les 16,67 de l'employeur et
ramène le salarié à 6,33 ; le partage moitié-moitié porte le salarié à 11,50.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import partage_taux_unique as P  # noqa: E402


def test_le_partage_se_lit_sur_la_fiche_du_portage_sans_le_moteur_python(monkeypatch, capsys):
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne calcule pas ici")
    from retraite_notionnelle import remuneration

    def interdit(*_, **__):
        raise AssertionError("le moteur Python bâtit la fiche de paie de l'étude")

    for nom in ("fiche", "brut_a_cout_donne"):
        monkeypatch.setattr(remuneration.ConstructeurFiche, nom, interdit)
    monkeypatch.setattr(remuneration, "bloc_droit_en_vigueur", interdit)
    monkeypatch.setattr(sys, "argv", ["partage_taux_unique.py", "--niveaux", "1.5", "2"])
    P.main()
    sortie = capsys.readouterr().out
    assert ("Aujourd'hui, sous le plafond : salarié 11.31 points, employeur 16.67, "
            "total 27.98.") in sortie
    assert "LE PARTAGE RETENU — salarié 6.33 pts, employeur 16.67 pts" in sortie
    assert "(l'ancien défaut du dépôt) — salarié 11.50 pts, employeur 11.50 pts" in sortie
    # Le partage C garde la part salariale : l'employeur tombe à 11,69.
    assert "part salariale inchangée — salarié 11.31 pts, employeur 11.69 pts" in sortie
    # Le détail de « qui paie », à 2 SMIC, est imprimé pour chaque partage.
    assert sortie.count("Qui paie le net du long terme, à 2 SMIC") == 7
