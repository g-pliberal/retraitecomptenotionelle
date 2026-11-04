"""Le code se lit en Python 3.10 et 3.11, que GitHub fait tourner (action 158).

`pyproject.toml` déclare `requires-python = ">=3.10"`, et `tests.yml` lance la
suite en 3.11 ; une session peut travailler sous 3.13, qui accepte ce que 3.11
refuse. Le 3 novembre 2026, une barre oblique inverse dans l'expression d'une
f-string (PEP 701, Python 3.12) a rougi la suite de GitHub, que celle de la
session avait laissée verte. Deux gardes : l'une compile le code avec le plus
ancien Python de la machine, l'autre, qui vaut sous 3.12 et plus, cherche la
faute connue dans l'arbre.
"""

from __future__ import annotations

import ast
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
DOSSIERS = ("scripts", "src", "tests", "moteur", "docs", ".claude")


def _sources() -> list[Path]:
    return sorted(p for d in DOSSIERS if (RACINE / d).is_dir() for p in (RACINE / d).rglob("*.py"))


def _ancien_python() -> str | None:
    """Le plus ancien interprète de la machine qui n'accepte pas la syntaxe de
    3.12 : celui qui court, sous 3.11 ou moins, puis `python3.10`, `python3.11`."""
    if sys.version_info < (3, 12):
        return sys.executable
    for nom in ("python3.10", "python3.11"):
        if chemin := shutil.which(nom):
            return chemin
    return None


_COMPILE = (
    "import sys\n"
    "for p in sys.argv[1:]:\n"
    "    try:\n"
    "        compile(open(p, 'rb').read(), p, 'exec', dont_inherit=True)\n"
    "    except SyntaxError as e:\n"
    "        print(f'{p}:{e.lineno}: {e.msg}')\n"
)


def test_le_code_se_compile_avec_le_plus_ancien_python_de_la_machine():
    python = _ancien_python()
    if python is None:
        pytest.skip("ni python3.10 ni python3.11 sur cette machine")
    sources = _sources()
    assert sources
    sortie = subprocess.run(
        [python, "-I", "-c", _COMPILE, *map(str, sources)],
        capture_output=True, text=True, check=True,
    ).stdout
    assert not sortie, "Python < 3.12 refuse ces fichiers :\n" + sortie.replace(str(RACINE) + "/", "")


@pytest.mark.skipif(sys.version_info < (3, 12), reason="avant 3.12, la compilation ci-dessus suffit")
def test_aucune_f_string_ne_porte_de_barre_oblique_inverse_dans_une_expression():
    """Avant 3.12, `f"{r'\\s' if x else 1}"` est une `SyntaxError` : le motif
    brut se pose dans une variable, avant la f-string."""
    fautes = []
    for chemin in _sources():
        texte = chemin.read_text(encoding="utf-8")
        lignes = texte.splitlines()
        for noeud in ast.walk(ast.parse(texte)):
            # `get_source_segment` relit tout le texte : on ne l'appelle que
            # sur les f-strings dont une ligne porte une barre oblique inverse.
            if isinstance(noeud, ast.FormattedValue) and any(
                "\\" in ligne for ligne in lignes[noeud.lineno - 1 : noeud.end_lineno]
            ):
                expression = ast.get_source_segment(texte, noeud.value) or ""
                if "\\" in expression:
                    fautes.append(f"{chemin.relative_to(RACINE)}:{noeud.lineno}: {expression}")
    assert not fautes, "barre oblique inverse dans une f-string :\n" + "\n".join(fautes)
