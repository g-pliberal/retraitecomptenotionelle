"""Le Python seul, débranché des règles Python (action 161, étape 4 de
l'inventaire du retrait, ``2026-11-16-l-inventaire-du-retrait-des-regles.md``).

Le coût, ses cas types, celui des avantages et la fiche de paie se chargent
sans un seul module du moteur Python : les cas types se datent au portage, le
code mort qui simulait la grille en Python est parti, les scénarios
neutralisés de la mesure des avantages, que seuls les tests liquidaient en
Python, sont passés aux tests (``tests/jumeau_des_avantages.py``), le métier
d'une carrière et les noms de ses profils logent parmi les types du pont, et
le salaire moyen d'une année se lit sous ``donnees/``.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SOURCES = RACINE / "src" / "retraite_notionnelle"

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


def _importe_des_regles(fichier: Path) -> list[str]:
    """Les imports, même tardifs, que ``fichier`` fait d'un module de règles."""
    arbre = ast.parse(fichier.read_text(encoding="utf-8"))
    return [f"{noeud.lineno}: {'.' * noeud.level}{noeud.module}"
            for noeud in ast.walk(arbre)
            if isinstance(noeud, ast.ImportFrom) and noeud.module
            and REGLES.match("retraite_notionnelle." + noeud.module.split(".")[0])]


def test_le_cout_ses_cas_types_et_les_avantages_se_chargent_sans_le_moteur_python():
    assert _importes("import retraite_notionnelle.castypes, retraite_notionnelle.avantages, "
                     "retraite_notionnelle.cout, retraite_notionnelle.facteurs_depense") == []


def test_ni_les_cas_types_ni_les_avantages_n_importent_une_regle():
    """Pas même un import tardif, dans le corps d'une fonction."""
    fautes = {nom: _importe_des_regles(SOURCES / nom)
              for nom in ("castypes.py", "avantages.py", "remuneration.py",
                          "contributions_equilibre.py")}
    assert {nom: f for nom, f in fautes.items() if f} == {}


def test_le_code_qui_simulait_en_python_est_parti():
    """La grille simulée en Python (``calculer_cas_types``), son niveau
    relatif lu au moteur Python (``CasType.niveau_relatif``), et la mesure des
    avantages par le scénario 1 Python (``recalculer``, ses scénarios
    neutralisés et ce qui ne servait qu'à eux) ne sont plus au modèle."""
    subprocess.run([sys.executable, "-c", "\n".join((
        "from retraite_notionnelle import avantages, castypes",
        "for nom in ('calculer_cas_types', 'carriere_de_la_grille'):",
        "    assert not hasattr(castypes, nom), nom",
        "assert not hasattr(castypes.CasType, 'niveau_relatif')",
        "for nom in ('recalculer', 'scenarios_neutralises', 'carriere_variante',",
        "            '_catalogue_sans', 'statuts_des_emplois', 'FICHES_RETIREES'):",
        "    assert not hasattr(avantages, nom), nom",
    ))], check=True, cwd=RACINE)


def test_le_salaire_moyen_se_lit_sans_le_moteur_python():
    assert _importes("\n".join((
        "from retraite_notionnelle.donnees.salaire_moyen import (",
        "    ANNEE_ANCRAGE_SALAIRE_MOYEN, ancrage_salaire_moyen, indice_salaire_moyen,",
        "    salaire_moyen_annuel)",
        "from retraite_notionnelle.donnees.simulateur import SimulateurDeDonnees",
        "macro = SimulateurDeDonnees().macro",
        "assert ancrage_salaire_moyen(macro)[0] == ANNEE_ANCRAGE_SALAIRE_MOYEN",
        "assert salaire_moyen_annuel(macro, 2000) == indice_salaire_moyen(macro, 2000, 2000)[2000]",
    ))) == []


def test_les_regles_reprennent_le_meme_salaire_moyen_et_le_meme_metier():
    subprocess.run([sys.executable, "-c", "\n".join((
        "from retraite_notionnelle.donnees import salaire_moyen as d",
        "from retraite_notionnelle.types_du_pont import carriere as t",
        "from retraite_notionnelle import carriere as c",
        "for nom in ('ANNEE_ANCRAGE_SALAIRE_MOYEN', 'ancrage_salaire_moyen',",
        "            'indice_salaire_moyen', 'salaire_moyen_annuel'):",
        "    assert getattr(c, nom) is getattr(d, nom), nom",
        "for nom in ('Metier', 'PROFIL_AUTOMATIQUE', 'PROFIL_SMIC'):",
        "    assert getattr(c, nom) is getattr(t, nom), nom",
    ))], check=True, cwd=RACINE)
