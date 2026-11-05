"""L'effort des modèles, tel que le dépôt le règle pour Claude Code.

L'effort se fixe modèle par modèle (`modelSettings`, dans
`.claude/settings.json`), et non par `CLAUDE_CODE_EFFORT_LEVEL` : la variable
passe devant tout, et ferait taire l'effort que déclarent les agents
(documentation de Claude Code, `sub-agents.md`, « Choose an effort level »).
Décision du propriétaire, le 3 novembre 2026 : `xhigh` au lieu de `max`, et
l'éclaireur et Explore, sur Haiku, à `high` (action 135, note du 3 novembre).
"""

import json
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
REGLAGES = json.loads((RACINE / ".claude" / "settings.json").read_text(encoding="utf-8"))


def _entete(agent: str) -> dict[str, str]:
    texte = (RACINE / ".claude" / "agents" / f"{agent}.md").read_text(encoding="utf-8")
    return dict(ligne.split(": ", 1) for ligne in texte.split("---")[1].strip().splitlines())


def test_l_effort_se_regle_par_modele_et_non_par_la_variable():
    assert "CLAUDE_CODE_EFFORT_LEVEL" not in REGLAGES.get("env", {})
    efforts = {modele: r["effortLevel"] for modele, r in REGLAGES.get("modelSettings", {}).items()}
    assert efforts == {"claude-opus-5-5": "xhigh", "claude-sonnet-5-5": "xhigh"}


def test_l_eclaireur_et_explore_declarent_leur_effort():
    for agent in ("eclaireur", "Explore"):
        assert _entete(agent).get("effort") == "high", agent


def test_le_detecteur_d_impeccable_ne_tourne_qu_a_la_demande():
    """Décision du propriétaire, le 5 novembre 2026 (action 135) : plus de hook
    Impeccable. Il tournait après chaque `Edit`/`Write` et à chaque fin de tour,
    dans toutes les sessions, et ne relevait que des choix voulus, des
    questions de goût ou un faux contraste « noir sur noir » qu'il demandait de
    trier après chaque retouche d'`index.html`. La compétence reste, à la
    demande ; son hook est éteint dans `.impeccable/config.json`, pour qu'une
    réinstallation par `/impeccable doctor` ne le rallume pas."""
    commandes = [crochet["command"]
                 for blocs in REGLAGES["hooks"].values()
                 for bloc in blocs
                 for crochet in bloc["hooks"]]
    assert not [c for c in commandes if "impeccable" in c], commandes
    config = json.loads((RACINE / ".impeccable" / "config.json").read_text(encoding="utf-8"))
    assert config["hook"]["enabled"] is False
