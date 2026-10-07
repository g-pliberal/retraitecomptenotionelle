"""Rien de perdu (docs/architecture.md, § 12) : ce qui est gelé se retrouve.

Les phases 1 à 8 ont déplacé la documentation et les registres sans changer
un résultat, et les domaines en déplacent encore. Ce test joue le filet de
``scripts/conservation.py`` : les paragraphes des récits, des notes de
décision et des archives, et les entrées des registres, que la référence
figée tient, doivent se retrouver quelque part dans le dépôt. Un récit
réécrit y apparaît comme perdu : un récit est gelé.
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


def test_un_bloc_produit_n_est_pas_gele(tmp_path):
    """Ce qu'un script écrit entre ses repères (`blocs_produits`) change avec le
    modèle, même dans un récit : le filet ne le gèle pas. Collé au repère, le
    tableau ne commence pas par une barre ; ceux de `docs/chiffrage_plf.md`
    étaient gelés, et la première correction qui déplaçait leurs chiffres les
    disait perdus. La prose autour reste gelée."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "data" / "reference" / "prose").mkdir(parents=True)
    (tmp_path / conservation.ZONES).write_text(
        "fichiers:\n  docs/avis.md:\n    defaut: recit\n    blocs_produits: [annuel]\n",
        encoding="utf-8")
    avis = tmp_path / "docs" / "avis.md"
    avis.write_text("# Avis\n\nLe coût est tenable.\n\n<!-- annuel:debut -->\n"
                    "| Année | Pensions |\n|---|---:|\n| 2026 | 8,50 |\n"
                    "<!-- annuel:fin -->\n", encoding="utf-8")
    arbre = conservation.Arbre(racine=tmp_path)
    reference = conservation.figer(arbre)
    assert reference["paragraphes"] == {"docs/avis.md": {"Avis": [
        conservation.empreinte("# Avis"), conservation.empreinte("Le coût est tenable.")]}}
    avis.write_text(avis.read_text(encoding="utf-8").replace("8,50", "8,49"),
                    encoding="utf-8")
    assert conservation.verifier(reference, arbre) == []
    avis.write_text(avis.read_text(encoding="utf-8").replace("tenable", "intenable"),
                    encoding="utf-8")
    assert conservation.verifier(reference, arbre)


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


def test_une_version_de_l_architecture_est_gelee_des_son_fichier_ecrit(tmp_path):
    """Depuis l'action 149, une version de l'architecture a son fichier : un
    récit, que le filet gèle sans que `zones.yaml` le déclare — chaque
    version l'y déclarerait, et deux sessions y écriraient de nouveau au même
    endroit. Une note de la feuille de route, elle, vit tant que son action
    est ouverte."""
    (tmp_path / "data" / "reference" / "prose").mkdir(parents=True)
    (tmp_path / conservation.ZONES).write_text("fichiers: {}\n", encoding="utf-8")
    version = tmp_path / conservation.VERSIONS / "2026-10-06-un-sujet.md"
    version.parent.mkdir(parents=True)
    version.write_text("# Version du 6 octobre 2026 : un sujet\n\nCe qui change.\n",
                       encoding="utf-8")
    note = tmp_path / "docs" / "feuille_de_route" / "149" / "2026-10-06-etape.md"
    note.parent.mkdir(parents=True)
    note.write_text("# Action 149 : une étape\n\nVivante.\n", encoding="utf-8")
    arbre = conservation.Arbre(racine=tmp_path)
    reference = conservation.figer(arbre)
    assert reference["paragraphes"] == {
        f"{conservation.VERSIONS}/2026-10-06-un-sujet.md": {
            "Version du 6 octobre 2026 : un sujet": [
                conservation.empreinte("# Version du 6 octobre 2026 : un sujet"),
                conservation.empreinte("Ce qui change.")]}}
    version.write_text(version.read_text(encoding="utf-8").replace("change", "changeait"),
                       encoding="utf-8")
    assert conservation.verifier(reference, arbre)


def test_une_regle_de_claude_md_se_retrouve_puce_par_puce(tmp_path):
    """Action 135, étape 3 du contexte : les règles de `CLAUDE.md` partent une
    à une vers les consignes des dossiers, que Claude Code ne charge qu'à la
    première lecture d'un de leurs fichiers. Une liste n'est qu'un paragraphe :
    `--depuis` la retrouve puce par puce, en puce d'une autre liste ou en
    paragraphe, et dit laquelle manque. Un dossier caché, qui est à
    l'outillage, ne compte pas."""
    avant, apres = tmp_path / "avant", tmp_path / "apres"
    for racine in (avant, apres):
        (racine / "data" / "reference" / "prose").mkdir(parents=True)
        (racine / conservation.ZONES).write_text("fichiers: {}\n", encoding="utf-8")
    (avant / "CLAUDE.md").write_text(
        "# Règles\n\n- **Une.** Pour tous.\n- **Deux.** Pour le modèle,\n"
        "  sur deux lignes.\n- **Trois.** Pour les données.\n", encoding="utf-8")
    (apres / "CLAUDE.md").write_text("# Règles\n\n- **Une.** Pour tous.\n",
                                     encoding="utf-8")
    for dossier, texte in (("src", "1. **Deux.** Pour le modèle, sur deux lignes.\n"),
                           ("data", "**Trois.** Pour les données.\n")):
        (apres / dossier).mkdir(exist_ok=True)
        (apres / dossier / "CLAUDE.md").write_text(f"# {dossier}\n\n{texte}",
                                                   encoding="utf-8")
    assert conservation.Arbre(racine=apres).documents() == [
        "CLAUDE.md", "data/CLAUDE.md", "src/CLAUDE.md"]
    assert conservation.pertes_entre(conservation.Arbre(racine=avant),
                                     conservation.Arbre(racine=apres)) == []

    (apres / ".claude").mkdir()
    (apres / ".claude" / "CLAUDE.md").write_text("**Trois.** Pour les données.\n", encoding="utf-8")
    (apres / "data" / "CLAUDE.md").write_text("# data\n\n**Trois.** Pour la donnée.\n",
                                              encoding="utf-8")
    assert conservation.pertes_entre(conservation.Arbre(racine=avant),
                                     conservation.Arbre(racine=apres)) == [
        "CLAUDE.md:6 : **Trois.** Pour les données."]
