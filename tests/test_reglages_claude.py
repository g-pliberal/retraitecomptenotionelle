"""L'effort des modèles, tel que le dépôt le règle pour Claude Code.

L'effort se fixe modèle par modèle (`modelSettings`, dans
`.claude/settings.json`), et non par `CLAUDE_CODE_EFFORT_LEVEL` : la variable
passe devant tout, et ferait taire l'effort que déclarent les agents
(documentation de Claude Code, `sub-agents.md`, « Choose an effort level »).
Décision du propriétaire, le 3 novembre 2026 : `xhigh` au lieu de `max`, et
l'éclaireur et Explore, sur Haiku, à `high` (action 135, note du 3 novembre).
Le 9 novembre 2026 : Fable 5.2, qui prend les règles du scénario 1, à `high`,
et non au `medium` par lequel Claude Code le fait démarrer (note du 9). Le
même jour, sur le billet « Which Claude model should you build with? » :
Opus 5.5 et Sonnet 5.5 à `high`, le cran au-delà duquel il demande une mesure,
et les deux agents de lecture au défaut de Haiku, `medium` (note « L'effort
selon le billet »). Le 11 novembre 2026, sur la documentation de la
plateforme : la chaîne de secours descend par capacité, et la publication
part aussi quand un tour meurt d'une erreur de l'API (note « La plateforme
Claude, lue contre nos réglages »).
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
    assert efforts == {
        "claude-fable-5-2": "high",
        "claude-opus-5-5": "high",
        "claude-sonnet-5-5": "high",
    }


def test_l_eclaireur_et_explore_declarent_leur_effort():
    for agent in ("eclaireur", "Explore"):
        assert _entete(agent).get("effort") == "medium", agent


def _commandes(evenement: str) -> list[str]:
    return [crochet["command"]
            for bloc in REGLAGES["hooks"].get(evenement, [])
            for crochet in bloc["hooks"]]


def test_la_publication_part_aussi_quand_un_tour_meurt_d_une_erreur_de_l_api():
    """`Stop` ne part pas quand un tour finit sur une erreur de l'API, limite
    d'usage ou surcharge : Claude Code lance `StopFailure` à sa place
    (`hooks.md`, « Stop » : « API errors fire StopFailure instead »). Sans ce
    second hook, les commits du tour restaient dans le conteneur, perdus s'il
    était repris. Décision du propriétaire, le 11 novembre 2026."""
    for evenement in ("Stop", "StopFailure"):
        assert any("scripts/pousser.sh" in c for c in _commandes(evenement)), evenement


def test_la_chaine_de_secours_descend_par_capacite():
    """Le modèle de secours tient « for the rest of the turn »
    (`settings-reference.md`, `fallbackModel`) : une étape du scénario 1, menée
    sur Fable 5.2, retombe donc sur Opus avant Sonnet. Décision du
    propriétaire, le 11 novembre 2026, à la place de Sonnet puis Opus, l'ordre
    du 17 octobre, quand Opus était le modèle le plus haut du dépôt."""
    assert REGLAGES["fallbackModel"] == ["opus", "sonnet"]


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
