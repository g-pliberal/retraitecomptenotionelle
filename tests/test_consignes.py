"""Les consignes que Claude Code charge : la racine, courte, et ce qui l'a quittée.

`CLAUDE.md` se relit à chaque appel de chaque session, et la documentation de
Claude Code lui donne une taille (`memory.md`, « Write effective
instructions ») : « target under 200 lines per CLAUDE.md file. Longer files
consume more context and reduce adherence. » Ce qui ne vaut que pour une
partie du dépôt l'a donc quittée pour une règle à portée de chemin,
`.claude/rules/<sujet>.md`, que son champ `paths` fait charger à la lecture ou
à l'écriture d'un fichier qui lui répond ; la relève de la session
d'orchestration, pour un skill ; ce qui ne regarde qu'un poste, pour
`docs/poste.md` (feuille de route, action 135, note du 11 novembre 2026,
« `CLAUDE.md` sous 200 lignes »).

Une règle partie ne vaut que si elle se charge encore, et au bon moment : ces
tests tiennent la limite, la portée de chaque règle, et le fil qui mène de la
racine à ce qui l'a quittée.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import reprise  # noqa: E402
import verifier_prose  # noqa: E402

#: « Target under 200 lines per CLAUDE.md file » : la racine, la consigne d'un
#: dossier, une règle.
LIGNES = 200
#: La largeur ordinaire d'une ligne, celle que `scripts/reprise.py` donne au
#: bloc « Reprise », ses ancres ôtées. Sans elle, la limite se tiendrait à la
#: lettre par des lignes démesurées, comme l'ont fait les dix lignes de ce
#: bloc (note du 11 novembre 2026 sur le bloc lisible).
LARGEUR = reprise.LARGEUR_AU_PLUS
ANCRE = re.compile(r"<!--.*?-->")

#: Ce qu'une session ouvre, et les règles qui se chargent alors : la prose
#: pour tout document et pour le zonage, la documentation pour ce qu'une étape
#: écrit en finissant, la suite pour un test. Le classement est celui que le
#: propriétaire a approuvé le 11 novembre 2026.
PORTEES = {
    "README.md": {"prose.md"},
    "CLAUDE.md": {"prose.md"},
    "src/CLAUDE.md": {"prose.md"},
    ".claude/rules/tests.md": {"prose.md"},
    "docs/methodologie.md": {"prose.md"},
    "docs/poste.md": {"prose.md"},
    "data/reference/prose/zones.yaml": {"prose.md"},
    "docs/feuille_de_route.md": {"prose.md", "documentation.md"},
    "docs/feuille_de_route/135/2026-11-11-plateforme-claude.md": {
        "prose.md", "documentation.md"},
    "docs/architecture.md": {"prose.md", "documentation.md"},
    "docs/architecture/versions/2026-10-07-consignes-par-dossier.md": {
        "prose.md", "documentation.md"},
    "docs/limites/1-certification.md": {"prose.md", "documentation.md"},
    "data/reference/legislation/journal_de_veille/2026-10-17-action-135-trois-modeles.yaml": {
        "documentation.md"},
    "tests/test_consignes.py": {"tests.md"},
    "tests/temoins/conservation.json": {"tests.md"},
    # Ni le code, ni une donnée, ni le `README.md` d'un dossier ne chargent rien.
    "src/retraite_notionnelle/fabrique.py": set(),
    "moteur/js/pages.js": set(),
    "scripts/pousser.sh": set(),
    "data/sources.yaml": set(),
    "moteur/polices/README.md": set(),
}


def _regles() -> list[Path]:
    return sorted((RACINE / verifier_prose.REGLES).rglob("*.md"))


def _entete(chemin: Path) -> dict:
    """L'en-tête d'une règle ou d'un skill. Illisible, Claude Code l'ignore, et
    la règle se charge alors à l'ouverture de chaque session (`memory.md`,
    « Rule frontmatter reference »)."""
    texte = chemin.read_text(encoding="utf-8")
    assert texte.startswith("---\n"), f"{chemin.name} : pas d'en-tête"
    entete = yaml.safe_load(texte.split("---\n", 2)[1])
    assert isinstance(entete, dict), f"{chemin.name} : en-tête illisible"
    return entete


def _portee(regle: Path) -> list[str]:
    motifs = _entete(regle).get("paths")
    assert isinstance(motifs, list) and motifs and all(
        isinstance(m, str) and m for m in motifs), (
        f"{regle.name} : sans `paths`, la règle se charge à l'ouverture de chaque session")
    return motifs


def _motif(motif: str) -> re.Pattern[str]:
    """Un motif de `paths`, lu comme la documentation de Claude Code le décrit
    (`memory.md`, « Path-specific rules ») : sans barre, il vaut à toute
    profondeur (`*.md`) ; ouvert par une barre, au seul dossier de base
    (`/*.md`) ; `**` traverse les dossiers, `*` reste dans le sien."""
    assert not set(motif) & set("{}[]?\\"), (
        f"{motif} : ce test ne lit ni accolades, ni crochets, ni « ? »")
    if motif.startswith("/"):
        motif = motif[1:]
    elif "/" not in motif:
        motif = f"**/{motif}"
    regex, i = "", 0
    while i < len(motif):
        if motif.startswith("**/", i):
            regex, i = regex + "(?:.*/)?", i + 3
        elif motif.startswith("**", i):
            regex, i = regex + ".*", i + 2
        elif motif[i] == "*":
            regex, i = regex + "[^/]*", i + 1
        else:
            regex, i = regex + re.escape(motif[i]), i + 1
    return re.compile(regex + r"\Z")


def _chargees(chemin: str) -> set[str]:
    """Les règles qu'un fichier fait charger."""
    return {regle.name for regle in _regles()
            if any(_motif(m).match(chemin) for m in _portee(regle))}


@pytest.mark.parametrize("chemin", ["CLAUDE.md", *verifier_prose.consignes()])
def test_une_consigne_tient_sous_deux_cents_lignes(chemin):
    """La limite que vise la documentation de Claude Code, pour la racine
    comme pour la consigne d'un dossier ou une règle : au-delà, ce qui ne vaut
    que pour une partie du dépôt part dans une règle à portée de chemin, une
    procédure dans un skill. Et des lignes d'une largeur de prose, pour que la
    limite ne se tienne pas en les allongeant."""
    lignes = (RACINE / chemin).read_text(encoding="utf-8").splitlines()
    assert len(lignes) < LIGNES, (
        f"{chemin} fait {len(lignes)} lignes : déplacer ce qui ne vaut que pour "
        f"une partie du dépôt vers une règle de {verifier_prose.REGLES}/")
    larges = [numero for numero, ligne in enumerate(lignes, 1)
              if len(ANCRE.sub("", ligne)) > LARGEUR]
    assert not larges, f"{chemin} : lignes de plus de {LARGEUR} caractères, {larges}"


def test_chaque_regle_se_charge_pour_des_fichiers_du_depot():
    """Une règle dont un motif ne répond plus à aucun fichier — un dossier
    renommé, une faute de frappe — ne se chargerait plus, et rien ne le
    dirait : la règle serait perdue sans avoir été effacée."""
    regles = _regles()
    assert regles, f"aucune règle sous {verifier_prose.REGLES}/"
    try:
        fichiers = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=RACINE, capture_output=True, text=True, check=True).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("hors d'un dépôt git")
    muets = [(regle.name, motif) for regle in regles for motif in _portee(regle)
             if not any(_motif(motif).match(fichier) for fichier in fichiers)]
    assert not muets, f"des motifs ne répondent à aucun fichier du dépôt : {muets}"


@pytest.mark.parametrize("chemin", sorted(PORTEES))
def test_une_regle_se_charge_au_bon_moment(chemin):
    """Ce qu'une session ouvre décide de ce qu'elle reçoit : sa note de
    feuille de route charge la prose et la documentation, un test charge la
    suite, et le code ne charge rien que sa zone ne lui donne déjà."""
    assert _chargees(chemin) == PORTEES[chemin]


def test_la_racine_mene_a_tout_ce_qui_l_a_quittee():
    """Un Grep, une commande composée ou un script ne chargent pas une règle :
    la racine, que toute session lit, nomme donc chacune, la page du poste et
    le skill de l'orchestration, pour qui ne travaille que par eux."""
    racine = " ".join((RACINE / "CLAUDE.md").read_text(encoding="utf-8").split())
    assert f"`{verifier_prose.REGLES}/`" in racine
    for regle in _regles():
        assert f"`{regle.name}`" in racine, f"la racine ne nomme pas {regle.name}"
    assert "`docs/poste.md`" in racine and (RACINE / "docs" / "poste.md").is_file()
    assert "skill `orchestration`" in racine
    skill = _entete(RACINE / ".claude" / "skills" / "orchestration" / "SKILL.md")
    assert skill["name"] == "orchestration" and skill["description"]
