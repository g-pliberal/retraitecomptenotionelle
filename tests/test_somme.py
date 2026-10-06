"""La somme de gauche à droite : les mêmes octets sous tous les Python.

Depuis Python 3.12, ``sum()`` additionne les flottants en somme compensée ;
sous 3.11, de gauche à droite. Les fichiers fabriqués en différaient au
dernier chiffre, et une session sous 3.13 voyait périmé ce que GitHub, sous
3.11, venait de fabriquer (action 148, étape 1). ``src/`` et ``scripts/``
additionnent par :func:`retraite_notionnelle.somme.somme_ordonnee`. Seuls les scripts
de ``scripts/fetch/``, autonomes, qui lisent les sources et ne fabriquent
rien de ce que GitHub refait, gardent ``sum()``.
"""

import io
import tokenize
from pathlib import Path

from retraite_notionnelle.somme import somme_ordonnee

RACINE = Path(__file__).resolve().parents[1]


def _appels_de_sum(chemin: Path) -> list[int]:
    jetons = list(tokenize.generate_tokens(
        io.StringIO(chemin.read_text(encoding="utf-8")).readline))
    return [j.start[0] for i, j in enumerate(jetons)
            if j.type == tokenize.NAME and j.string == "sum"
            and i + 1 < len(jetons) and jetons[i + 1].string == "("
            and not (i and jetons[i - 1].string in (".", "def"))]


def test_aucun_sum_dans_le_code_qui_fabrique():
    fautes = []
    for dossier in ("src", "scripts"):
        for chemin in sorted((RACINE / dossier).rglob("*.py")):
            relatif = chemin.relative_to(RACINE)
            if relatif.parts[:2] == ("scripts", "fetch"):
                continue
            fautes += [f"{relatif}:{ligne}" for ligne in _appels_de_sum(chemin)]
    assert not fautes, ("sum() additionne autrement sous Python 3.12 et après :"
                        " employer somme_ordonnee() — " + ", ".join(fautes))


def test_la_somme_va_de_gauche_a_droite():
    termes = [1e16, 1.0, -1e16]
    attendu = 0
    for terme in termes:
        attendu += terme
    assert somme_ordonnee(termes) == attendu == 0.0
    assert somme_ordonnee([], 5) == 5
    assert somme_ordonnee([[1], [2]], []) == [1, 2]
