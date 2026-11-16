"""La sonde du retrait (``scripts/sonde_moteur_python.py``, action 161) : elle
relève les règles du moteur Python qu'un calcul exécute, et elles seules —
ni le code d'un module qu'on importe, ni les chargeurs de données du
simulateur, ni ce qui vit hors des fichiers de règles."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SCRIPT = RACINE / "scripts" / "sonde_moteur_python.py"


def _sonde():
    spec = importlib.util.spec_from_file_location("sonde_moteur_python", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _module(chemin: Path, texte: str, nom: str):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _paquet_factice(tmp_path, monkeypatch):
    """Un paquet factice que la sonde prend pour le sien : le test n'entre
    pas dans le moteur Python."""
    sonde = _sonde()
    monkeypatch.setattr(sonde, "PAQUET", tmp_path)
    return sonde


def test_une_regle_executee_est_relevee(tmp_path, monkeypatch):
    sonde = _paquet_factice(tmp_path, monkeypatch)
    regle = _module(tmp_path / "moteur" / "regle.py",
                    "def doubler(x):\n    return 2 * x\n", "regle_factice")
    cout = _module(tmp_path / "cout.py",
                   "def calculer(f):\n    return f(3)\n", "cout_factice")
    assert sonde.sonder(lambda: cout.calculer(regle.doubler)) == ["moteur.regle.doubler"]


def test_ce_qui_s_execute_a_l_import_n_est_pas_releve(tmp_path, monkeypatch):
    sonde = _paquet_factice(tmp_path, monkeypatch)
    texte = ("def bareme():\n    return (1, 2)\n\n"
             "class Table:\n    ligne = bareme()\n\n"
             "BAREME = bareme()\n")
    chemin = tmp_path / "droit" / "table.py"
    assert sonde.sonder(lambda: _module(chemin, texte, "table_factice")) == []


def test_les_donnees_du_simulateur_ne_sont_pas_des_regles():
    sonde = _sonde()
    assert sonde.est_une_regle(str(sonde.PAQUET / "simulateur.py"),
                               "Simulateur.__init__") is None
    assert sonde.est_une_regle(str(sonde.PAQUET / "donnees" / "simulateur.py"),
                               "SimulateurDeDonnees.macro") is None
    assert sonde.est_une_regle(str(sonde.PAQUET / "simulateur.py"),
                               "Simulateur.simuler") == "simulateur.Simulateur.simuler"
    assert sonde.est_une_regle(str(sonde.PAQUET / "cout.py"), "calculer_cout") is None
    assert sonde.est_une_regle(str(sonde.PAQUET / "droit" / "liquider.py"),
                               "liquider") == "droit.liquider.liquider"


def test_la_sonde_lance_un_script(tmp_path):
    script = tmp_path / "etude.py"
    script.write_text("from retraite_notionnelle.moteur import capitalisation\n"
                      "capitalisation.repartition(40)\n", encoding="utf-8")
    sortie = subprocess.run([sys.executable, str(SCRIPT), "--json", str(script)],
                            capture_output=True, text=True, check=True)
    assert sortie.stdout.strip() == '["moteur.capitalisation.repartition"]'


def test_la_sonde_tient_sans_sys_monitoring(tmp_path, monkeypatch):
    """GitHub lance la suite sous Python 3.11, qui n'a pas ``sys.monitoring``
    (3.12) : la sonde se rabat alors sur ``sys.setprofile``, et relève les
    mêmes règles, hors de l'import."""
    sonde = _paquet_factice(tmp_path, monkeypatch)
    monkeypatch.delattr(sys, "monitoring", raising=False)
    regle = _module(tmp_path / "moteur" / "regle.py",
                    "def doubler(x):\n    return 2 * x\n", "regle_factice_311")
    cout = _module(tmp_path / "cout.py",
                   "def calculer(f):\n    return f(3)\n", "cout_factice_311")
    assert sonde.sonder(lambda: cout.calculer(regle.doubler)) == ["moteur.regle.doubler"]
    texte = ("def bareme():\n    return (1, 2)\n\n"
             "class Table:\n    ligne = bareme()\n\n"
             "BAREME = bareme()\n")
    chemin = tmp_path / "droit" / "table.py"
    assert sonde.sonder(lambda: _module(chemin, texte, "table_factice_311")) == []


def test_une_regle_se_releve_a_chaque_sondage(tmp_path, monkeypatch):
    """Une règle relevée par un sondage l'est encore au suivant : ce que
    ``sys.monitoring.DISABLE`` tait le reste du sondage ne se tait pas au-delà."""
    sonde = _paquet_factice(tmp_path, monkeypatch)
    regle = _module(tmp_path / "moteur" / "regle.py",
                    "def doubler(x):\n    return 2 * x\n", "regle_factice_deux")
    premier = sonde.sonder(lambda: regle.doubler(3))
    assert sonde.sonder(lambda: regle.doubler(3)) == premier == ["moteur.regle.doubler"]
