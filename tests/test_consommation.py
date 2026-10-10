"""Ce que les sessions consomment (`scripts/consommation.py`, feuille de route,
action 135, étape 1 du contexte) : chaque part du contexte, multipliée par le
nombre d'appels qui l'ont relue. Tout s'exerce sur des transcriptions écrites
pour l'occasion, à la forme de celles de Claude Code 2.1."""

from __future__ import annotations

import base64
import json
import struct
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import consommation  # noqa: E402

DOSSIER = "/depot"


def _appel(requete: str, contexte: int, sortie: int, blocs: list[dict]) -> list[dict]:
    """Un appel de l'API, réparti comme Claude Code le fait : une entrée par bloc."""
    usage = {
        "input_tokens": 2,
        "cache_creation_input_tokens": 100,
        "cache_read_input_tokens": contexte - 102,
        "output_tokens": sortie,
    }
    return [
        {
            "type": "assistant",
            "requestId": requete,
            "cwd": DOSSIER,
            "message": {"id": "m" + requete, "content": [bloc], "usage": usage},
        }
        for bloc in blocs
    ]


def _outil(identifiant: str, nom: str, **entree) -> dict:
    return {"type": "tool_use", "id": identifiant, "name": nom, "input": entree}


def _resultat(identifiant: str, contenu) -> dict:
    return {
        "type": "user",
        "message": {"content": [{"type": "tool_result", "tool_use_id": identifiant, "content": contenu}]},
    }


def _piece(sorte: str, texte: str | None, **autres) -> dict:
    entree = {"type": "attachment", "attachment": {"type": sorte, **autres}}
    if texte is not None:
        entree["rendered"] = [{"content": texte}]
    return entree


def _ecrire(chemin: Path, entrees: list[dict]) -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("".join(json.dumps(e) + "\n" for e in entrees), encoding="utf-8")
    return chemin


def _session(tmp_path: Path) -> Path:
    return _ecrire(
        tmp_path / "projects" / "-depot" / "s1.jsonl",
        [
            _piece("hook_success", "x" * 700, hookName="SessionStart:startup"),
            _piece("prompt_snapshot", None, content="y" * 100_000),
            {"type": "user", "message": {"content": "Bonjour"}},
            *_appel("r1", 1000, 50, [{"type": "thinking"}, _outil("t1", "Read", file_path="/depot/a.py")]),
            _resultat("t1", "z" * 3500),
            _piece("total_tokens_reminder", "w" * 35),
            *_appel("r2", 2060, 40, [_outil("t2", "Bash", command="cd /depot && sed -n 1,9p b.md | tail")]),
            _resultat("t2", "v" * 700),
            *_appel("r3", 2300, 10, [{"type": "text", "text": "fini"}]),
            {"type": "cost-state", "totalCostUSD": 0.42},
        ],
    )


def test_un_appel_reparti_sur_plusieurs_entrees_se_compte_une_fois(tmp_path):
    session = consommation.lire(_session(tmp_path))
    assert [a.contexte for a in session.appels] == [1000, 2060, 2300]
    assert session.cout == 0.42


def test_les_jetons_relus_font_exactement_la_somme_des_contextes(tmp_path):
    session = consommation.lire(_session(tmp_path))
    assert sum(p.relu for p in session.parts) == pytest.approx(session.relu)
    assert session.relu == 1000 + 2060 + 2300


def test_la_croissance_va_a_la_sortie_puis_au_prorata_des_blocs(tmp_path):
    session = consommation.lire(_session(tmp_path))
    lecture = next(p for p in session.parts if p.fichier == "a.py")
    rappel = next(p for p in session.parts if p.etiquette == "total_tokens_reminder")
    # De 1000 à 2060 : 50 de sortie, puis 1010 répartis à 1000 contre 10.
    assert lecture.jetons == pytest.approx(1000)
    assert rappel.jetons == pytest.approx(10)
    assert lecture.relu == pytest.approx(2000)  # relue par les appels 2 et 3


def test_le_depart_detaille_ce_que_le_harnais_y_a_mis(tmp_path):
    session = consommation.lire(_session(tmp_path))
    depart = {p.etiquette: p for p in session.parts if p.categorie == "depart"}
    assert depart["hook SessionStart:startup"].jetons == pytest.approx(200)
    # Le prompt instantané ne va pas au modèle ; le reste est système et outils.
    assert "prompt_snapshot" not in depart
    assert depart["système et outils"].jetons == pytest.approx(1000 - 200 - 2)
    assert depart["système et outils"].relu == pytest.approx(798 * 3)


def test_une_commande_se_reduit_a_son_verbe_et_au_fichier_qu_elle_lit():
    decrire = consommation.decrire_commande
    assert decrire("cd /depot && sed -n 1,9p b.md | tail") == ("sed", "b.md")
    assert decrire("python -m pytest -m rapide 2>&1 | tail -n 30") == ("python -m pytest", None)
    assert decrire("FOO=1 python scripts/regenerer.py --verifier") == ("python scripts/regenerer.py", None)
    assert decrire("git diff --stat") == ("git diff", None)
    assert decrire("cat docs/etat.md") == ("cat", "docs/etat.md")
    assert decrire("grep -n motif fichier.py") == ("grep", None)
    assert decrire("cat a.md 2>/dev/null; ls") == ("cat", "a.md")
    assert decrire("sed -i 's/x  #/; s/y/z/' f.py") == ("sed", "f.py")
    assert decrire("python - <<'EOF'") == ("python", None)


def test_une_compaction_ouvre_un_segment_neuf(tmp_path):
    chemin = _ecrire(
        tmp_path / "s.jsonl",
        [
            *_appel("r1", 1000, 0, [{"type": "text"}]),
            _resultat("x", "a" * 3500),
            *_appel("r2", 5000, 0, [{"type": "text"}]),
            *_appel("r3", 1500, 0, [{"type": "text"}]),
            *_appel("r4", 1500, 0, [{"type": "text"}]),
        ],
    )
    session = consommation.lire(chemin)
    assert session.compactions == 1
    assert sum(p.relu for p in session.parts) == pytest.approx(9000)
    resume = next(p for p in session.parts if p.etiquette == "résumé de compaction")
    assert resume.relu == pytest.approx(3000)


def test_une_interruption_n_est_ni_un_appel_ni_une_compaction(tmp_path):
    # Claude Code écrit une entrée `<synthetic>`, d'usage nul, quand un appel
    # est interrompu ou échoue : comptée, elle passait pour une compaction, et
    # le contexte rechargé ensuite allait au rappel qui la suivait.
    synthetique = {
        "type": "assistant",
        "message": {"id": "s", "model": "<synthetic>", "content": [{"type": "text"}],
                    "usage": {"input_tokens": 0, "output_tokens": 0}},
    }
    chemin = _ecrire(
        tmp_path / "s.jsonl",
        [
            *_appel("r1", 1000, 0, [{"type": "text"}]),
            synthetique,
            _piece("total_tokens_reminder", "w" * 35),
            *_appel("r2", 1010, 0, [{"type": "text"}]),
        ],
    )
    session = consommation.lire(chemin)
    assert [a.contexte for a in session.appels] == [1000, 1010]
    assert session.compactions == 0
    rappel = next(p for p in session.parts if p.etiquette == "total_tokens_reminder")
    assert rappel.jetons == pytest.approx(10)


def test_une_image_se_compte_a_ses_dimensions_et_non_a_son_base64():
    entete = b"\x89PNG\r\n\x1a\n" + b"\0\0\0\rIHDR" + struct.pack(">II", 750, 100)
    image = {"type": "image", "source": {"data": base64.b64encode(entete + b"\0" * 300_000).decode()}}
    assert consommation.estimer([image]) == pytest.approx(100)


def test_le_rapport_classe_fichiers_commandes_et_hooks(tmp_path, capsys):
    _session(tmp_path)
    _ecrire(
        tmp_path / "projects" / "-depot" / "s1" / "subagents" / "agent-a.jsonl",
        _appel("r9", 500, 5, [{"type": "text"}]),
    )
    assert consommation.main([str(tmp_path / "projects")]) == 0
    sortie = capsys.readouterr().out
    assert "total, 2 sessions" in sortie
    assert "a.py" in sortie and "b.md" in sortie
    assert "sed" in sortie and "hook SessionStart:startup" in sortie
    assert "s1/agent-a" in sortie
