"""Les contrats de la façade des tests, portés par elle-même (action 161,
étape 2 du retrait des règles Python).

Pour lier les arguments d'une entrée qu'elle sert et relire ce que le portage
calcule, la façade (``tests/facade.py``) lit une signature et un type rendu.
Elle les lisait sur le jumeau Python ; elle les lit désormais dans
``tests/contrats_de_la_facade.py``, des signatures sans corps, qui ne chargent
aucun fichier de règles. Tant que le jumeau vit, chaque contrat se confronte
au sien, dans ``test_facade_jumeau.py`` : ces confrontations partent avec lui.
"""

import ast
import subprocess
import sys
from pathlib import Path

PAQUET = "retraite_notionnelle"
TESTS = Path(__file__).resolve().parent

#: Les fichiers de règles que le retrait supprimera.
REGLES = ("droit", "moteur", "scenarios", "carriere", "revalorisation", "simulateur",
          "echeancier", "pilote", "journal")


def test_les_contrats_ne_chargent_aucun_fichier_de_regles():
    programme = (
        "import sys\n"
        f"sys.path.insert(0, {str(TESTS)!r})\n"
        "import contrats_de_la_facade\n"
        f"print('\\n'.join(n for n in sys.modules if n.startswith('{PAQUET}.')))\n")
    charges = subprocess.run([sys.executable, "-c", programme], capture_output=True,
                             text=True, check=True).stdout.split()
    regles = [nom for nom in charges
              if nom.removeprefix(f"{PAQUET}.").split(".")[0] in REGLES]
    assert regles == []


def test_la_facade_ne_lit_de_signature_que_dans_ses_contrats():
    """Chaque ``inspect.signature`` et ``typing.get_type_hints`` de la façade
    lit un contrat, que ``_contrat`` lui donne, et non le jumeau."""
    arbre = ast.parse((TESTS / "facade.py").read_text(encoding="utf-8"))
    lectures = [noeud for noeud in ast.walk(arbre) if isinstance(noeud, ast.Call)
                and isinstance(noeud.func, ast.Attribute)
                and (noeud.func.attr, getattr(noeud.func.value, "id", None))
                in (("signature", "inspect"), ("get_type_hints", "typing"))]
    assert lectures
    hors_contrat = [ast.unparse(noeud) for noeud in lectures
                    if not (isinstance(noeud.args[0], ast.Name) and noeud.args[0].id == "contrat")]
    assert hors_contrat == []
