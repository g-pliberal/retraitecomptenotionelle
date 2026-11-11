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
consigne (note « Les éclaireurs sans le `CLAUDE.md` racine »).
"""

import json
import re
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
