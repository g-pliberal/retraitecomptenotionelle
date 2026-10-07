"""L'arbre du dépôt (`scripts/arbre.py`, feuille de route, action 135) : chaque
fichier, ses lignes et ses caractères, chaque dossier la somme des siens, du
plus lourd au plus léger. Tout s'exerce sur un petit dépôt écrit pour
l'occasion."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import arbre  # noqa: E402


def _ecrire(racine: Path, fichiers: dict[str, str | bytes]) -> None:
    for chemin, contenu in fichiers.items():
        cible = racine / chemin
        cible.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(contenu, str):
            cible.write_text(contenu, encoding="utf-8", newline="\n")
        else:
            cible.write_bytes(contenu)


def _git(racine: Path, *arguments: str) -> None:
    subprocess.run(["git", *arguments], cwd=racine, check=True, capture_output=True)


def test_un_caractere_n_est_pas_un_octet_et_la_derniere_ligne_compte(tmp_path):
    _ecrire(tmp_path, {"a.md": "Été\nfin sans retour", "b.txt": "un\ndeux\n", "vide.txt": "",
                       "image.png": b"\x89PNG\r\n\x1a\n\0\0", "latin.csv": b"caf\xe9\n"})
    a = arbre.mesurer(tmp_path / "a.md", "a.md")
    assert (a.lignes, a.caracteres, a.octets) == (2, 19, None)
    assert (tmp_path / "a.md").stat().st_size == 21
    b = arbre.mesurer(tmp_path / "b.txt", "b.txt")
    assert (b.lignes, b.caracteres) == (2, 8)
    vide = arbre.mesurer(tmp_path / "vide.txt", "vide.txt")
    assert (vide.lignes, vide.caracteres, vide.octets) == (0, 0, None)
    # Ni un octet nul ni de l'UTF-8 qui ne se décode pas ne font du texte.
    for nom, octets in (("image.png", 10), ("latin.csv", 5)):
        binaire = arbre.mesurer(tmp_path / nom, nom)
        assert (binaire.lignes, binaire.caracteres, binaire.octets) == (0, 0, octets)


def test_chaque_dossier_porte_la_somme_des_siens_du_plus_lourd_au_plus_leger(tmp_path):
    _ecrire(tmp_path, {"src/petit.py": "x\n", "src/gros.py": "x" * 50 + "\n",
                       "docs/note.md": "y" * 10 + "\n", "image.png": b"\0" * 300})
    tronc = arbre.construire(["docs/note.md", "image.png", "src/gros.py", "src/petit.py"],
                             tmp_path)
    assert (tronc.lignes, tronc.caracteres) == (3, 64)
    assert (tronc.enfants["src"].lignes, tronc.enfants["src"].caracteres) == (2, 53)
    # Le binaire n'a pas de caractères : il va en dernier, et ne pèse sur
    # aucune somme.
    assert [texte for texte, _ in arbre.dessiner(tronc, ".")] == [
        ".",
        "├── src/",
        "│   ├── gros.py",
        "│   └── petit.py",
        "├── docs/",
        "│   └── note.md",
        "└── image.png",
    ]
    assert [texte for texte, _ in arbre.dessiner(tronc, ".", profondeur=1)] == [
        ".", "├── src/", "├── docs/", "└── image.png"]
    assert [chemin for chemin, _ in arbre.plus_gros(tronc, 2)] == ["src/gros.py", "docs/note.md"]


def test_un_binaire_donne_ses_octets_et_une_ligne_demesuree_se_signale(tmp_path):
    _ecrire(tmp_path, {"donnees.json": "[" + "1," * 6000 + "1]\n",
                       "court.json": "[" + "1," * 4000 + "1]\n", "logo.png": b"\0" * 1234})
    tronc = arbre.construire(["court.json", "donnees.json", "logo.png"], tmp_path)
    entete, racine, donnees, court, logo = arbre.tableau(arbre.dessiner(tronc, ".")).splitlines()
    # Les chiffres s'alignent sous l'en-tête ; les remarques vont au-delà.
    assert entete.split() == ["lignes", "caractères"]
    assert len(racine) == len(court) == len(entete)
    assert racine.split() == [".", "2", "20", "008"]
    assert court.split() == ["├──", "court.json", "1", "8", "004"]
    assert donnees[:len(entete)].split() == ["├──", "donnees.json", "1", "12", "004"]
    assert donnees[len(entete):] == "  plus longue ligne : 12 003"
    assert logo[:len(entete)].split() == ["└──", "logo.png", "—", "—"]
    assert logo[len(entete):] == "  binaire, 1 234 octets"


def test_les_fichiers_sont_ceux_que_git_ajouterait(tmp_path):
    _ecrire(tmp_path, {".gitignore": "*.log\n", "suivi.py": "a\n", "efface.py": "b\n"})
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    (tmp_path / "efface.py").unlink()
    _ecrire(tmp_path, {"nouveau.md": "c\n", "trace.log": "d\n"})
    assert arbre.fichiers(tmp_path) == [".gitignore", "nouveau.md", "suivi.py"]


def test_le_script_montre_un_dossier_ou_les_plus_gros_et_refuse_l_inconnu(tmp_path, monkeypatch,
                                                                          capsys):
    _ecrire(tmp_path, {"src/gros.py": "x" * 50 + "\n", "src/petit.py": "x\n", "README.md": "r\n"})
    _git(tmp_path, "init", "-q")
    monkeypatch.setattr(arbre, "RACINE", tmp_path)
    assert arbre.main(["./src/", "--profondeur", "0"]) == 0
    assert capsys.readouterr().out.splitlines()[1:] == ["src/       2          53"]
    assert arbre.main(["--plus-gros", "1"]) == 0
    assert capsys.readouterr().out.splitlines()[1].split() == ["src/gros.py", "1", "51"]
    assert arbre.main(["absent"]) == 2
    assert "absent : rien que git suive" in capsys.readouterr().err
