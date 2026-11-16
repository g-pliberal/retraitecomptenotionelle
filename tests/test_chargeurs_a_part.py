"""Les chargeurs que le coût et la fabrique lisent, à part des règles (action
161, point 4 du tri des scripts et des modules) : le barème de l'ASPA
(``MinimumVieillesse``, ``DeuxEtages``) et les revalorisations des pensions
(``RevalorisationsPensions``) se lisent sous ``donnees/``, et le nombre
déclaré d'appels de ``liquider`` (``APPELS_DECLARES``) au noyau, sans importer
un seul module du moteur Python. Les modules de règles les reprennent de là,
les mêmes objets, tant qu'ils restent.

Le simulateur de données seules (``donnees/simulateur.py``) se bâtit et se lit
de même, variantes d'une étude comprises : le ``Simulateur`` du moteur Python
en hérite, la façade des tests et le coût de la mémoire le prennent seul."""

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


def test_le_simulateur_de_donnees_se_lit_sans_le_moteur_python():
    """Bâti, lu, refait sous les conventions de projection, et ses variantes
    d'une étude passées en demande : rien du moteur Python ne s'importe."""
    assert _importes("\n".join((
        "from retraite_notionnelle.donnees.simulateur import SimulateurDeDonnees",
        "from retraite_notionnelle.noyau import univers",
        "s = SimulateurDeDonnees()",
        "for nom in ('macro', 'mortalite', 'courbe_taux', 'courbe_taux_pilier', 'catalogue',",
        "            'effectifs', 'cotisants', 'distribution', 'distributions_par_sexe',",
        "            'caracteristiques', 'patrimoine', 'vie_en_couple',",
        "            'financement_regimes', 'revalorisations', 'univers'):",
        "    getattr(s, nom)",
        "assert s.univers_de_la_demande == {}",
        "p = s.pour_la_projection()",
        "assert type(p) is SimulateurDeDonnees and p.parametres.conventions_cor",
        "assert p.pour_la_projection() is p and s.pour_la_projection() is p",
        "lus = s.univers",
        "cle = next(c for c, u in lus.items() if not u.est_le_droit_reel)",
        "v = SimulateurDeDonnees(variantes={cle: lus[cle]})",
        "assert list(v.univers_de_la_demande) == [cle]",
        "assert v.pour_la_projection().variantes == v.variantes",
    ))) == []


def test_le_simulateur_python_herite_du_simulateur_de_donnees():
    """Les mêmes chargeurs, une seule fois écrits : le simulateur Python ne
    les redéfinit pas, et sa projection reste un simulateur Python."""
    subprocess.run([sys.executable, "-c", "\n".join((
        "from retraite_notionnelle.donnees.simulateur import SimulateurDeDonnees, DONNEES",
        "from retraite_notionnelle.simulateur import Simulateur",
        "assert issubclass(Simulateur, SimulateurDeDonnees)",
        "assert not set(vars(Simulateur)) & (DONNEES | {'univers', 'univers_de_la_demande',",
        "                                              'pour_la_projection'})",
        "assert type(Simulateur().pour_la_projection()) is Simulateur",
    ))], check=True, cwd=RACINE)


def test_la_facade_et_le_cout_de_la_memoire_prennent_le_simulateur_de_donnees():
    """La façade des tests lit ses données sur un simulateur de données seules,
    et la mémoire en bâtit un pour le coût et sa grille : ni l'une ni l'autre
    ne bâtit plus le simulateur Python."""
    batit = re.compile(r"_simulateur\.Simulateur\(|from \.simulateur import Simulateur")
    fautes = {}
    for f, debut, fin in (("tests/facade.py", "class Simulateur(", "def __getattr__"),
                          ("src/retraite_notionnelle/memoire.py", "def grille_du_cout(",
                           "def avantages(")):
        texte = (RACINE / f).read_text(encoding="utf-8")
        texte = texte[texte.index(debut):texte.index(debut) + texte[texte.index(debut):]
                      .index(fin)]
        fautes.update({f: m.group(0) for m in [batit.search(texte)] if m})
    assert fautes == {}
    assert "from .simulateur import" not in (
        RACINE / "src/retraite_notionnelle/cout.py").read_text(encoding="utf-8")


#: Les scripts que la sonde dit ne lire du simulateur que ses données (groupes
#: 1 et 2 de ``2026-11-16-le-tri-des-scripts-et-des-modules.md``), hors de
#: ``mesures_prose`` et de ``lectures_du_modele``, qui simulent encore.
SCRIPTS_SUR_LES_DONNEES = (
    "age_conjoncturel", "age_depart_csp", "controle_eacr", "cout_age_depart",
    "cout_avantages", "cycle_de_vie", "estimation_officielle", "facteurs_depense",
    "flux_fonction_publique", "garantie_par_sexe", "indexation_scenario_6",
    "mesures_accueil", "mortalite_population", "part_minimum_contributif",
    "proposition_prospective", "sensibilite_comptes", "solde_fusion",
    "stock_age_legal", "tableau_de_bord")

#: Les modules de ``src/`` que ces scripts appellent, et qui bâtissaient le
#: simulateur Python pour n'en lire que les données.
MODULES_SUR_LES_DONNEES = ("avantages", "controle_ancetre", "controle_eacr",
                           "facteurs_depense", "leviers")


def test_les_scripts_de_donnees_batissent_le_simulateur_de_donnees():
    """Ni ces scripts ni les modules qu'ils appellent n'importent plus le
    simulateur Python ; la mémoire bâtit le simulateur de données pour le
    coût des avantages aussi."""
    python = re.compile(r"retraite_notionnelle\.simulateur import|from \.simulateur import")
    fichiers = ([f"scripts/{s}.py" for s in SCRIPTS_SUR_LES_DONNEES]
                + [f"src/retraite_notionnelle/{m}.py" for m in MODULES_SUR_LES_DONNEES])
    fautes = {f: m.group(0) for f in fichiers
              for m in [python.search((RACINE / f).read_text(encoding="utf-8"))] if m}
    assert fautes == {}
    memoire = (RACINE / "src/retraite_notionnelle/memoire.py").read_text(encoding="utf-8")
    assert "from .simulateur import" not in memoire


#: Les scripts qui gardaient le simulateur Python pour n'en lire que des
#: données — la macro, la mortalité, les effectifs, les paramètres — et
#: demandent leurs calculs au pont (``2026-11-16-les-derniers-lecteurs-du-
#: simulateur-python.md``). ``scenarios_meres`` garde le type ``Comparaison``
#: que la façade du pont rend ; ``grille_large`` demande au portage l'âge de
#: ses cas types et le premier âge surcoté, ses jumeaux Python retirés.
SCRIPTS_QUI_NE_LISENT_QUE_DES_DONNEES = (
    "fetch/trajectoire", "grille_large", "lectures_decision_29", "mesurer_surcote",
    "mesures_prose", "recours_aspa", "scenarios_meres")


def test_les_derniers_lecteurs_ne_batissent_plus_le_simulateur_python():
    """Aucun de ces scripts n'importe ni ne bâtit le ``Simulateur`` du moteur
    Python ; ils bâtissent le simulateur de données seules."""
    python = re.compile(r"\bimport\b[^\n]*\bSimulateur\b|\bSimulateur\(")
    fautes = {s: m.group(0) for s in SCRIPTS_QUI_NE_LISENT_QUE_DES_DONNEES
              for m in [python.search((RACINE / f"scripts/{s}.py").read_text(
                  encoding="utf-8"))] if m}
    assert fautes == {}
