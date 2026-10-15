"""Le lecteur du site sous l'interface de ``scripts/fetch/lecture_pdf.py`` (banc).

L'ébauche de ce que la fabrique importera au troisième temps de l'étape 4 :
ce que le JavaScript fait passe par node ; ce que la règle de la note 0003
laisse en Python — les aplats, la lecture par abscisse, les fonctions internes
dont ``cnavpl_recueils.py`` se sert — est pris au lecteur Python, la lecture
par abscisse nourrie des fragments du JavaScript.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from commun import APPELS, demander, lecteur_python  # noqa: E402,F401

py = lecteur_python()


def _fragments(page: list) -> list[tuple[int, int, float, float, str]]:
    return [(int(p), int(b), float(y), float(x), t) for p, b, y, x, t in page]


def lignes_pdf(octets: bytes, tolerance: float = 3.0) -> list[str]:
    return demander(octets, "lignes", tolerance)


def lignes_par_page(octets: bytes, tolerance: float = 3.0,
                    par_abscisse: bool = False) -> list[list[str]]:
    if not par_abscisse:
        return demander(octets, "pages", tolerance)
    return [py._assembler_par_abscisse(_fragments(page), tolerance)
            for page in demander(octets, "fragments_pages")]


def fragments_par_page(octets: bytes, tolerance: float = 3.0):
    return [[rangee for rangee, _ in py._lignes_par_abscisse(_fragments(page), tolerance)]
            for page in demander(octets, "fragments_pages")]


def texte_pdf(octets: bytes) -> str:
    return "\n".join(lignes_pdf(octets))


texte_de_ligne = py.texte_de_ligne
aplats_de_page = py.aplats_de_page
Aplat = py.Aplat
_flux, _hexa, _litteral, _objets, _polices, JETONS = (
    py._flux, py._hexa, py._litteral, py._objets, py._polices, py.JETONS)
