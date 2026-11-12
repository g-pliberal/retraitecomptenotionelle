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
Claude, lue contre nos réglages »). Le même jour : les deux agents de lecture
démarrent sans le `CLAUDE.md` de la racine, une carte du dépôt dans leur
consigne (note « Les éclaireurs sans le `CLAUDE.md` racine ») ; et les outils
que le dépôt n'emploie pas sortent de chaque requête (note « Le contexte de
départ »).
"""

import json
import re
from fnmatch import fnmatchcase
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
REGLAGES = json.loads((RACINE / ".claude" / "settings.json").read_text(encoding="utf-8"))

#: Les deux agents qui lisent pour la session, sur Haiku.
AGENTS_DE_LECTURE = ("eclaireur", "Explore")

#: Ce que leur carte du dépôt nomme, chemin par chemin : les règles à portée
#: de chemin, qui ont quitté le `CLAUDE.md` de la racine le 11 novembre 2026
#: (`tests/test_consignes.py`), l'architecture, l'état, la feuille de route et
#: ses notes, les archives, les trois zones, les fiches et les limites, le
#: journal de veille, les témoins.
LIEUX_DE_LA_CARTE = (
    ".claude/rules/",
    "docs/architecture.md",
    "docs/etat.md",
    "docs/feuille_de_route.md",
    "docs/feuille_de_route/<action>/",
    "docs/archives/feuille_de_route.md",
    "docs/archives/feuille_de_route/<action>/",
    "src/",
    "moteur/",
    "data/",
    "data/reference/regles/",
    "docs/limites/",
    "data/reference/legislation/journal_de_veille/",
    "tests/temoins/",
)

#: Ce qu'une carte « de quelques lignes » peut peser, en mots : moins du
#: dixième du `CLAUDE.md` qu'elle remplace, quelque 2 700 mots en novembre 2026.
MOTS_DE_LA_CARTE = 250


def _fichier(agent: str) -> str:
    return (RACINE / ".claude" / "agents" / f"{agent}.md").read_text(encoding="utf-8")


def _entete(agent: str) -> dict[str, str]:
    return dict(ligne.split(": ", 1) for ligne in _fichier(agent).split("---")[1].strip().splitlines())


def _carte(agent: str) -> str:
    """La section « La carte du dépôt » de la consigne d'un agent, sans son
    titre, jusqu'au titre suivant."""
    consigne = _fichier(agent).split("---", 2)[2]
    section = re.search(r"^## La carte du dépôt\n(.*?)(?=^## |\Z)", consigne, flags=re.M | re.S)
    assert section, f"{agent} : sa consigne n'a pas de section « La carte du dépôt »"
    return section.group(1).strip()


def test_l_effort_se_regle_par_modele_et_non_par_la_variable():
    assert "CLAUDE_CODE_EFFORT_LEVEL" not in REGLAGES.get("env", {})
    efforts = {modele: r["effortLevel"] for modele, r in REGLAGES.get("modelSettings", {}).items()}
    assert efforts == {
        "claude-fable-5-2": "high",
        "claude-opus-5-5": "high",
        "claude-sonnet-5-5": "high",
    }


def test_l_eclaireur_et_explore_declarent_leur_effort():
    for agent in AGENTS_DE_LECTURE:
        assert _entete(agent).get("effort") == "medium", agent


def test_l_eclaireur_et_explore_demarrent_sans_le_claude_md_de_la_racine():
    """`sub-agents.md` : « Explore and Plan start without your CLAUDE.md files
    and the git status snapshot to keep research fast and inexpensive ».
    L'Explore du dépôt, qui remplace celui de Claude Code pour tourner sur
    Haiku, l'avait repris du même coup, et l'éclaireur l'a toujours eu : des
    règles de publication et de test, pour des agents qui ne publient ni ne
    testent. `omitClaudeMd: true`, depuis Claude Code 2.1.271, le leur ôte ;
    les `CLAUDE.md` de zone se chargent toujours quand l'agent lit un fichier
    de leur dossier. Décision du propriétaire, le 11 novembre 2026."""
    for agent in AGENTS_DE_LECTURE:
        assert _entete(agent).get("omitClaudeMd") == "true", agent


def test_leur_consigne_porte_une_carte_du_depot_qui_dit_vrai():
    """Ce que le `CLAUDE.md` de la racine leur disait du dépôt, et qu'ils ne
    reçoivent plus, tient dans une carte : la même pour les deux, qui nomme
    chaque lieu de `LIEUX_DE_LA_CARTE`, et dont chaque chemin existe. Un
    dossier renommé, et ce test demande à la carte de suivre."""
    cartes = {agent: _carte(agent) for agent in AGENTS_DE_LECTURE}
    assert cartes["eclaireur"] == cartes["Explore"], "les deux agents ne portent plus la même carte"
    chemins = {incise for incise in re.findall(r"`([^`\n]+)`", cartes["eclaireur"])
               if "/" in incise or incise.endswith(".md")}
    oublies = [lieu for lieu in LIEUX_DE_LA_CARTE if lieu not in chemins]
    assert not oublies, f"la carte ne nomme pas : {oublies}"
    # Un gabarit, `docs/feuille_de_route/<action>/`, vaut pour son dossier.
    absents = sorted(c for c in chemins if not (RACINE / c.split("<", 1)[0]).exists())
    assert not absents, f"la carte cite des chemins qui n'existent pas : {absents}"


def test_leur_carte_tient_en_quelques_lignes():
    """Une carte qui grossirait referait le `CLAUDE.md` qu'elle remplace. Le
    guide de Haiku 5.5, de l'effort `low` : « In long agent prompts, the model
    is more likely to skip a search, stop early, or skip a check at this
    level » ; à `medium`, l'effort des deux agents, l'arrêt prématuré y est
    « roughly halved »."""
    for agent in AGENTS_DE_LECTURE:
        mots = len(_carte(agent).split())
        assert mots <= MOTS_DE_LA_CARTE, f"{agent} : sa carte fait {mots} mots"


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


#: Les outils dont le propriétaire a accordé le refus, le 11 novembre 2026,
#: famille par famille (action 135, note « Le contexte de départ »). Un nom nu
#: dans `permissions.deny`, ou un motif sur le nom, retire la définition de
#: l'outil de chaque requête (`permissions.md` : « A bare tool name like `Bash`
#: removes the tool from Claude's context entirely, so Claude never sees it »).
_DISTANT = "mcp__claude-code-remote__"
REFUS = {
    # La plateforme : publier une page, lancer des agents par script, le réveil
    # de `/loop`, proposer des plugins et des skills, le rendu de
    # `/code-review`, la liste des agents joignables.
    "Artifact", "Workflow", "ScheduleWakeup",
    "SearchPlugins", "SuggestPluginInstall", "SuggestSkills", "ShowOnboardingRolePicker",
    "ReportFindings", "ListAgents",
    # Le serveur des sessions du cloud : les webhooks d'un artifact, les
    # environnements, les tâches récurrentes, les dossiers du poste, le suivi
    # des pull requests, les autres dépôts.
    *(_DISTANT + nom for nom in (
        "watch_url", "unwatch_url",
        "create_environment", "update_environment", "get_environment", "switch_environment",
        "list_environments", "request_credential",
        "create_trigger", "update_trigger", "list_triggers", "fire_trigger", "get_trigger",
        "list_computer_folders", "request_computer_folder",
        "subscribe_pr_activity", "unsubscribe_pr_activity",
        "add_repo", "register_repo_root", "list_repos",
    )),
    # Les connecteurs de claude.ai, serveur par serveur.
    "mcp__Claude_Docs__*",
    "mcp__Google_Docs__*", "mcp__Google_Drive__*", "mcp__Google_Sheets__*", "mcp__Google_Slides__*",
}

#: Ce que les sessions appellent, et qu'aucun refus ne doit emporter :
#: l'orchestration et ses rappels (une trentaine de `send_later` du 3 au
#: 10 novembre 2026), la documentation, le verdict de GitHub, le courant.
APPELES = {
    *(_DISTANT + nom for nom in (
        "create_session", "send_message", "list_events", "get_session", "list_sessions",
        "archive_session", "get_event", "interrupt_session", "set_session_tags",
        "set_session_title", "send_later", "delete_trigger", "confirm_repository_trust",
        "read_documentation",
    )),
    "mcp__github__actions_list",
    "ReadNotifications", "AskUserQuestion", "SendUserFile", "ToolSearch", "Skill", "Agent",
    "Bash", "Read", "Edit", "Write", "Grep", "Glob",
}


def _refus_qui_touchent(outil: str, refus: list[str]) -> list[str]:
    return [regle for regle in refus if fnmatchcase(outil, regle)]


def test_les_outils_que_le_depot_n_emploie_pas_sortent_du_contexte():
    refus = REGLAGES.get("permissions", {}).get("deny", [])
    assert sorted(refus) == sorted(REFUS)
    # Seul un refus au nom nu retire la définition : une règle à parenthèses,
    # `Bash(rm *)`, laisse l'outil dans le contexte.
    assert not [regle for regle in refus if "(" in regle]


def test_aucun_refus_n_emporte_ce_que_les_sessions_appellent():
    refus = REGLAGES["permissions"]["deny"]
    # Le piège : un motif sur tout le serveur emporterait l'orchestration.
    assert _refus_qui_touchent(_DISTANT + "send_later", [_DISTANT + "*"])
    for outil in sorted(APPELES):
        assert not _refus_qui_touchent(outil, refus), outil


def test_artifact_et_les_workflows_sont_coupes_par_leur_reglage_aussi():
    """Le réglage de chacun emporte ce que le refus de l'outil laisse : les
    skills d'artifact, les commandes de workflow et le mot-clé « ultracode »
    (`artifacts.md`, « Disable artifacts » ; `workflows.md`, « Turn workflows
    off »)."""
    assert REGLAGES.get("enableArtifact") is False
    assert REGLAGES.get("disableWorkflows") is True


def test_les_consignes_git_de_claude_code_cedent_a_celles_du_depot():
    """L'outil Bash portait « Commit or push only when the user asks. If on the
    default branch, branch first », contre « on publie sur `main`, toujours ».
    `memory.md` : « If your CLAUDE.md sets commit or pull request rules, turn
    off the built-in ones with `includeGitInstructions` »."""
    assert REGLAGES.get("includeGitInstructions") is False


#: Les skills du compte claude.ai du propriétaire, que la plateforme livre à
#: chaque session du cloud (`anthropic-skills:…`), et que ce dépôt n'appelle
#: pas : décision du 12 novembre 2026 (action 135, note « Les skills du compte
#: masqués pour ce dépôt »). Éteints, ceux qui n'ont pas d'objet ici : les
#: navigateurs et le poste, les connecteurs refusés, l'artifact coupé, le
#: brief du matin, l'import de mémoire.
SKILLS_DU_COMPTE_ETEINTS = (
    "artifact-emulator", "built-in-browser", "chrome-browser", "computer-use",
    "docs", "google-workspace", "import-memory", "morning",
)

#: Ceux que le propriétaire peut encore appeler par leur nom, `/pdf`, sans
#: que leur description entre dans chaque requête.
SKILLS_DU_COMPTE_A_LA_DEMANDE = ("deep-research", "docx", "pdf", "skill-creator", "xlsx")

#: Celui qui reste annoncé : les présentations aux adhérents en sortent.
SKILL_DU_COMPTE_GARDE = "pptx"


def test_les_skills_fournis_hors_sujet_ne_s_annoncent_plus():
    """`skillOverrides` masque un skill fourni avec Claude Code, et aussi,
    sous son nom entier, un skill du compte claude.ai : constaté le
    12 novembre 2026 sur un sous-agent témoin, contre la lecture du 11."""
    fournis = (
        "artifact-capabilities", "artifact-design", "artifact-diagramming", "dataviz",
        "fewer-permission-prompts", "init", "keybindings-help", "loop", "plugin-authoring", "run",
    )
    assert REGLAGES.get("skillOverrides") == {
        **{nom: "off" for nom in fournis},
        **{f"anthropic-skills:{nom}": "off" for nom in SKILLS_DU_COMPTE_ETEINTS},
        **{f"anthropic-skills:{nom}": "user-invocable-only"
           for nom in SKILLS_DU_COMPTE_A_LA_DEMANDE},
    }


def test_le_skill_des_presentations_reste_annonce():
    """`docs/presentation_adherents_*.pptx` : le dépôt s'en sert."""
    assert list((RACINE / "docs").glob("presentation_adherents_*.pptx"))
    assert f"anthropic-skills:{SKILL_DU_COMPTE_GARDE}" not in REGLAGES.get("skillOverrides", {})
