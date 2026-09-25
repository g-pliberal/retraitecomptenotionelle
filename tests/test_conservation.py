"""Rien de perdu (docs/architecture.md, § 12) : ce qui est gelé se retrouve.

Les phases 1 à 8 déplacent la documentation et les registres sans changer un
résultat. Ce test joue le filet de ``scripts/conservation.py`` : les
paragraphes des récits, des notes de décision et des archives, et les entrées
des registres, que la référence figée tient, doivent se retrouver quelque part
dans le dépôt. Un récit réécrit y apparaît comme perdu : un récit est gelé.
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import conservation  # noqa: E402


def test_rien_de_ce_qui_est_gele_ne_se_perd():
    pertes = conservation.verifier()
    assert not pertes, "\n".join(pertes)


def test_un_paragraphe_deplace_se_reconnait():
    """Aux blancs, aux dièses d'un titre et aux valeurs des chiffres ancrés près,
    que `verifier_prose.py --corriger` récrit ; au mot près, pas davantage."""
    empreinte = conservation.empreinte
    assert empreinte("### 26. Confronter   le scénario 1") == empreinte(
        "## 26. Confronter le\nscénario 1")
    assert empreinte("les <!--chiffre:tests()-->2513<!--/--> tests") == empreinte(
        "les <!--chiffre:tests()-->2514<!--/--> tests")
    assert empreinte("un mot") != empreinte("un autre mot")


def test_un_bloc_de_code_est_un_seul_paragraphe():
    texte = "# Titre\nAvant.\n\n```bash\nune ligne\n\n# pas un titre\n```\n\nAprès.\n"
    blocs = [bloc for _, _, bloc in conservation.paragraphes(texte)]
    assert blocs == ["# Titre", "Avant.", "```bash\nune ligne\n\n# pas un titre\n```",
                     "Après."]


def test_une_action_en_cours_n_est_pas_gelee():
    """Une action `en cours` de la feuille de route s'écrit encore ; une action
    close ne se réécrit plus."""
    texte = ("## Journal\n\n### 1. Une action faite — `fait`\n\nFigée.\n\n"
             "### 2. Une action ouverte — `en cours`\n\nVivante.\n\n"
             "```\n# un commentaire, pas un titre\n```\n\n"
             "### Une note sous l'action\n\nVivante aussi.\n\n"
             "### 3. Une action abandonnée — `abandonnée`\n\nFigée aussi.\n")
    lignes = texte.split("\n")
    vivantes = [lignes[n - 1] for n in sorted(conservation._vivantes(texte))]
    assert "Vivante." in vivantes and "Vivante aussi." in vivantes
    assert "Figée." not in vivantes and "Figée aussi." not in vivantes


def test_le_filet_voit_un_recit_perdu_et_le_retrouve_archive(tmp_path):
    """Sur un dépôt miniature : un paragraphe de récit supprimé est perdu ;
    déplacé dans une archive, il est retrouvé ; un paragraphe d'état peut
    changer sans rien perdre."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "data" / "reference" / "prose").mkdir(parents=True)
    (tmp_path / conservation.ZONES).write_text(
        "fichiers:\n  docs/journal.md:\n    defaut: recit\n"
        "    sections:\n      Aujourd'hui: etat\n", encoding="utf-8")
    journal = tmp_path / "docs" / "journal.md"
    journal.write_text("# Journal\n\nLe 3 mars, on a trouvé une erreur.\n\n"
                       "## Aujourd'hui\n\nTout va bien.\n", encoding="utf-8")
    arbre = conservation.Arbre(racine=tmp_path)
    reference = conservation.figer(arbre)
    assert conservation.verifier(reference, arbre) == []

    journal.write_text("# Journal\n\n## Aujourd'hui\n\nTout va mieux.\n", encoding="utf-8")
    (pertes,) = conservation.verifier(reference, arbre)
    assert "docs/journal.md" in pertes and "Journal" in pertes

    (tmp_path / "docs" / "archives").mkdir()
    (tmp_path / "docs" / "archives" / "journal.md").write_text(
        "# Journal, archivé\n\nLe 3 mars, on a trouvé une erreur.\n", encoding="utf-8")
    assert conservation.verifier(reference, arbre) == []
