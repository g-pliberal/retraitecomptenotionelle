"""Les transferts reçus par la retraite, lus dans les rapports à la CCSS
(``scripts/fetch/ccss_transferts_retraite.py``).

Les lignes sont fabriquées à la main, telles que le lecteur PDF les rend.
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import ccss_transferts_retraite as transferts  # noqa: E402


def test_un_double_signe_tient_la_place_d_un_taux():
    """L'édition d'automne du rapport de 2026 écrit la ligne du fonds dans le
    compte de la CNAV avec des prévisions nulles, le fonds disparaissant en
    2026, et des taux sans objet, « -- » : la ligne se lit, ses deux années
    closes avec ; un tiret seul reste une cellule vide."""
    colonnes = transferts._colonnes("2024 2025 % % 2026 (p) 2027 (p) %")
    ligne = "Prises en charge de cotisations par le FSV 15 064 15 691 4,2 0 -- 0 -- - 0 -"
    assert transferts._valeurs(ligne, transferts._libelle(ligne), colonnes) == {
        2024: 15064.0, 2025: 15691.0, 2026: 0.0, 2027: 0.0}
