"""Les chargeurs que le coût et la fabrique lisent, à part des règles (action
161, point 4 du tri des scripts et des modules) : le barème de l'ASPA
(``MinimumVieillesse``, ``DeuxEtages``) et les revalorisations des pensions
(``RevalorisationsPensions``) se lisent sous ``donnees/``, et le nombre
déclaré d'appels de ``liquider`` (``APPELS_DECLARES``) au noyau, sans importer
un seul module du moteur Python. Les modules de règles les reprennent de là,
les mêmes objets, tant qu'ils restent."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]

#: Les modules du moteur Python, ceux que la sonde appelle des fichiers de
#: règles (``scripts/sonde_moteur_python.py``).
REGLES = re.compile(r"^retraite_notionnelle\.(droit|moteur|scenarios|echeancier|journal"
                    r"|pilote|carriere|revalorisation|simulateur)(\.|$)")


def _importes(code: str) -> list[str]:
    """Les modules du moteur Python que ``code`` importe, dans un interpréteur neuf."""
    sortie = subprocess.run(
        [sys.executable, "-c", code + "\nimport sys, json\n"
         "print(json.dumps(sorted(sys.modules)))"],
        capture_output=True, text=True, check=True, cwd=RACINE)
    return [m for m in json.loads(sortie.stdout.splitlines()[-1]) if REGLES.match(m)]


def test_le_bareme_de_l_aspa_se_lit_sans_le_moteur_python():
    assert _importes("from retraite_notionnelle.donnees.minimum_vieillesse import "
                     "MinimumVieillesse, DeuxEtages") == []


def test_les_revalorisations_se_lisent_sans_le_moteur_python():
    assert _importes("from retraite_notionnelle.donnees.revalorisations import "
                     "RevalorisationsPensions, Revalorisation, produit") == []


def test_le_nombre_declare_se_lit_sans_le_moteur_python():
    assert _importes("from retraite_notionnelle.noyau.budget import APPELS_DECLARES") == []


def test_les_regles_reprennent_les_memes_objets():
    """Dans un interpréteur à part : ce fichier n'entre pas dans le moteur
    Python (``test_fichiers_sur_le_moteur_python.py``)."""
    subprocess.run([sys.executable, "-c", "\n".join((
        "import importlib",
        "m = lambda nom: importlib.import_module('retraite_notionnelle.' + nom)",
        "aspa, reval = m('donnees.minimum_vieillesse'), m('donnees.revalorisations')",
        "assert m('scenarios.actuel').MinimumVieillesse is aspa.MinimumVieillesse",
        "assert m('scenarios.actuel').DeuxEtages is aspa.DeuxEtages",
        "assert m('revalorisation').RevalorisationsPensions is reval.RevalorisationsPensions",
        "assert m('droit.liquidation').APPELS_DECLARES == m('noyau.budget').APPELS_DECLARES == 6",
    ))], check=True, cwd=RACINE)


def test_le_cout_et_la_fabrique_ne_les_prennent_plus_aux_regles():
    """Ce qui lit ces chargeurs hors des règles les prend à leur nouvelle place."""
    anciens = re.compile(r"from (retraite_notionnelle|\.)\.?(scenarios\.actuel import"
                         r" (MinimumVieillesse|DeuxEtages)|revalorisation import"
                         r" RevalorisationsPensions)|droit import liquidation\b")
    lecteurs = ["src/retraite_notionnelle/cout.py", "src/retraite_notionnelle/effet_retour.py",
                "scripts/construire_donnees.py", "scripts/tableau_de_bord.py"]
    fautes = {f: m.group(0) for f in lecteurs
              for m in [anciens.search((RACINE / f).read_text(encoding="utf-8"))] if m}
    assert fautes == {}
