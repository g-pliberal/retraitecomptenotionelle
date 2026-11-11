# Le contexte de départ : les outils que le dépôt n'emploie pas sortent de chaque requête

**Le 11 novembre 2026, la demande.** Le premier des quatre chantiers de la
note « La plateforme Claude, lue contre nos réglages » : réduire ce que
chaque session relit à chaque appel, en retirant du contexte les définitions
d'outils que le dépôt n'emploie jamais ; mesurer d'abord, proposer au
propriétaire outil par outil, ne toucher à `.claude/settings.json`, une
garde, qu'avec son accord.

**La mesure : 89 000 jetons au premier appel, dont 68 000 de définitions
d'outils.**

- *Le contexte du premier appel* se lit dans la transcription de la session
  (`python scripts/consommation.py`, colonne « départ ») et, d'une autre
  session, dans le premier événement `result` de celle qu'on regarde
  (`first_request_input_tokens`, note du 3 novembre). Le champ vaut pour le
  tour, non pour la session : un tour suivant y porte son propre premier
  appel (176 866 puis 371 780 dans une session de plusieurs tours), et un
  tour repris après une interruption ne le porte pas. Le même événement
  donne le nombre de définitions envoyées (`tool_schema_build_detail.tools`).
- *Le relevé.* Le 3 novembre, 76 184, 75 226 et 76 162 jetons (note du 3). Le
  10, 87 399, pour 58 définitions. Le 11, dans la session qui écrit cette
  note, 89 147, pour 60. Quatre sessions du 9, relevées par un agent sur
  Haiku : de 89 071 à 90 464. La plateforme a donc ajouté 13 000 jetons en
  huit jours, sans rien demander ; l'estimation de départ, 23 000 jetons
  d'outils inutiles sur 76 000, était bien en dessous.
- *La composition*, dans cette session : les définitions d'outils 68 000, le
  prompt système 6 000, la liste des skills 5 000, `CLAUDE.md` 5 000, la
  liste des agents 2 000, le reste 3 000.
- *Outil par outil.* La transcription garde un instantané du prompt
  (`prompt_snapshot`) : le prompt système, et chaque définition telle qu'elle
  part, nom, description et schéma. `consommation.py` le lit désormais et
  partage le départ au prorata des caractères ; `--limite 80` montre toutes
  les définitions. C'est une estimation : un sous-agent témoin (plus bas)
  montre que les longues descriptions en anglais pèsent une dizaine de pour
  cent de moins que leur part de caractères.

**Ce que dit la source**, lue le jour même par `curl` puis `grep`
(`code.claude.com/docs/en/`).

- `permissions.md` : « A bare tool name like `Bash` removes the tool from
  Claude's context entirely, so Claude never sees it » ; un motif sur le nom
  fait de même, « `mcp__puppeteer__*` matches every tool from the `puppeteer`
  server ». Une règle à parenthèses, `Bash(rm *)`, laisse l'outil en place.
- `settings.md`, « Settings in cloud sessions » : le `.claude/settings.json`
  du dépôt est lu « in a session with one repository outside a project's
  threads ».
- `prompt-caching.md`, « Denying an entire tool » : dans une conversation
  ouverte, l'outil refusé ne s'appelle plus, mais « the request's tool
  definitions don't change and the cached prefix survives ». Le gain ne vaut
  donc qu'aux sessions ouvertes après le réglage.
- `mcp.md` : `disableClaudeAiConnectors` n'agit que sur les connecteurs que
  Claude Code va chercher lui-même, « not to the connectors a cloud host or
  the desktop app delivers » : sans effet dans nos sessions. Et
  `deniedMcpServers` épargne les serveurs que l'application enregistre
  (« In-process `type: "sdk"` servers are exempt »). Restent les refus
  d'outils, serveur par serveur.
- `artifacts.md`, « Disable artifacts », et `workflows.md`, « Turn workflows
  off » : `enableArtifact: false` et `disableWorkflows: true` valent dans le
  fichier du dépôt.
- `skills.md` : `skillOverrides` masque un skill fourni avec Claude Code,
  non ceux d'un plugin ; les skills du compte claude.ai
  (`anthropic-skills:…`) se choisissent sur claude.ai.
- `memory.md` : « If your CLAUDE.md sets commit or pull request rules, turn
  off the built-in ones with `includeGitInstructions` ».

**Ce qui reste dans le contexte, et pourquoi.** Vingt-huit définitions,
21 000 jetons.

- *L'orchestration* : `create_session`, `send_message`, `list_events`,
  `get_session`, `list_sessions`, `archive_session`, et leurs voisins de
  quelques centaines de jetons (`get_event`, `interrupt_session`,
  `unarchive_session`, `set_session_tags`, `set_session_title`).
- *`send_later`*, que la demande rangeait parmi les tâches planifiées à
  refuser : la liste des tâches du compte (`list_triggers`) montre une
  trentaine de rappels du 3 au 10 novembre, tous d'un seul tir, posés par
  des sessions du dépôt — le verdict de GitHub à relire cinquante minutes
  plus tard, le rappel de secours d'une orchestration. Avec lui
  `delete_trigger`, qui les annule.
- *`confirm_repository_trust`* : la question que la plateforme fait poser au
  propriétaire quand elle refuse à une session de joindre ses autres
  sessions.
- *`read_documentation`, `ReadNotifications`, `SendUserFile`,
  `report_preview_port`*, ce dernier pour montrer le site depuis un
  téléphone ; les outils de GitHub, différés, dont `actions_list` lit le
  verdict d'une course ; et le courant, d'`Agent` à `Write`.

**La liste accordée.** Le propriétaire, le 11 novembre 2026, a accordé
chaque famille proposée, et les trois réglages voisins. Les jetons sont
ceux de `consommation.py` sur cette session.

| famille | outils refusés | jetons |
|---|---|---|
| publier une page | `Artifact`, et ses webhooks `watch_url`, `unwatch_url` | 14 800 |
| les environnements | `create_environment`, `update_environment`, `get_environment`, `switch_environment`, `list_environments`, `request_credential` | 12 500 |
| les tâches récurrentes | `create_trigger`, `update_trigger`, `list_triggers`, `fire_trigger`, `get_trigger` | 5 500 |
| proposer plugins et skills | `SearchPlugins`, `SuggestPluginInstall`, `SuggestSkills`, `ShowOnboardingRolePicker` | 2 800 |
| les dossiers du poste | `list_computer_folders`, `request_computer_folder` | 2 800 |
| des agents par script | `Workflow` | 2 200 |
| les autres dépôts | `add_repo`, `register_repo_root`, `list_repos` | 2 100 |
| le réveil de `/loop` | `ScheduleWakeup` | 1 900 |
| le rendu de `/code-review`, les agents joignables | `ReportFindings`, `ListAgents` | 1 200 |
| le suivi des pull requests | `subscribe_pr_activity`, `unsubscribe_pr_activity` | 700 |
| Claude Docs | `mcp__Claude_Docs__*` : trois outils chargés, cinq différés | 500 |
| les connecteurs Google | `mcp__Google_Docs__*`, `…Drive__*`, `…Sheets__*`, `…Slides__*` : vingt-huit noms différés, après le premier appel | 350 |

Soit 47 000 jetons de définitions, trente-deux sur soixante. S'y ajoutent :

- *`enableArtifact: false` et `disableWorkflows: true`*, en plus du refus de
  l'outil : le réglage emporte aussi les deux outils différés d'un artifact,
  les commandes de workflow et le mot-clé « ultracode ».
- *`skillOverrides`*, dix skills fournis mis à `off`, un millier de jetons :
  `artifact-capabilities`, `artifact-design`, `artifact-diagramming`,
  `dataviz`, `fewer-permission-prompts`, `init`, `keybindings-help`, `loop`,
  `plugin-authoring`, `run`.
- *`includeGitInstructions: false`*, deux cents jetons, et surtout une
  contradiction de moins : l'outil Bash portait « Commit or push only when
  the user asks. If on the default branch, branch first ».

Ce que le propriétaire y perd, dans ce dépôt seulement : publier un artifact
depuis une session (son compte en a dix-huit, que rien ne rattache à un
dépôt), « ultracode », `/loop`, `/init`, `/run`, et la proposition, par une
session, de modifier son environnement — le sien a le réseau sans
restriction, et aucune clé.

**Ce qui est fait.**

- `.claude/settings.json` : trente-quatre règles `permissions.deny`, au nom
  nu ou au motif, et les quatre réglages ci-dessus.
- `tests/test_reglages_claude.py` tient la liste accordée, à l'outil près,
  refuse qu'une règle à parenthèses s'y glisse, et vérifie qu'aucun refus,
  motif compris, n'emporte ce que les sessions appellent : un
  `mcp__claude-code-remote__*` tuerait l'orchestration.
- `scripts/consommation.py` détaille le départ outil par outil
  (`tests/test_consommation.py`).

**Constaté dans la session même**, avant de publier.

- Trois outils refusés, appelés pour voir — un du serveur des sessions, un
  de la plateforme, un par motif —, répondent « Permission to use … has been
  denied ». Claude Docs et les quatre connecteurs Google se déconnectent ;
  les deux outils différés d'un artifact disparaissent.
- *Un sous-agent généraliste d'un seul appel, sur Haiku*, comparé à ceux que
  la session avait lancés avant le réglage : 32 661 jetons au premier appel
  au lieu de 67 737, vingt-huit définitions au lieu de cinquante, vingt-quatre
  skills au lieu de trente-cinq (les dix masqués, et `workflow-authoring`,
  que `disableWorkflows` emporte). Net de trois outils que l'application de
  bureau a ajoutés entre-temps, 160 000 caractères de moins y font 35 076
  jetons de moins : 4,6 caractères le jeton, quand le contexte entier en
  comptait 4,1.
- *Non constaté* : `includeGitInstructions`. La description de Bash n'a pas
  changé dans ce sous-agent ; elle se fabrique peut-être à l'ouverture de la
  session.

**Comment constater le gain.** Les réglages ne valent qu'aux sessions
ouvertes après eux. Dans une telle session,
`python scripts/consommation.py --limite 80` donne son contexte de départ,
à comparer aux 89 147 jetons du 11 novembre : de 40 000 à 45 000 sont
attendus, selon que l'on compte au prorata des caractères ou au poids du
sous-agent témoin. La même sortie liste les définitions — vingt-huit
attendues, plus les deux que l'application de bureau ajoute quand elle suit
la session (`mcp__ccd_session__spawn_task`, `dismiss_task`) — et le poids de
Bash, qui dira si ses consignes git sont parties. D'une autre session, le
premier événement `result` de la session neuve donne les deux nombres. La
plateforme change d'une semaine à l'autre : c'est la liste qui se compare,
plus que le total.

Au tarif de Fable 5.2 (16 $ le million à l'écriture du cache d'une heure,
0,20 $ à sa lecture), 44 000 jetons de moins font 0,70 $ à l'ouverture et
0,0088 $ par appel : 2,87 $ sur une étape de 246 appels. Un sous-agent
généraliste en profite aussi ; l'éclaireur et Explore, qui déclarent leurs
quatre outils, n'en portaient rien.

**Ce qui reste.**

- Le constat sur la première session ouverte après ce commit, et ce que
  devient Bash ; à écrire à la suite de cette note.
- Au propriétaire, sur claude.ai : les quatorze skills de son compte
  (`anthropic-skills:…`, 2 400 jetons) entrent dans chaque session, dont
  `google-workspace`, `computer-use`, `chrome-browser`, `built-in-browser`,
  `morning` et `import-memory`, que ce dépôt n'appelle pas ; et les
  connecteurs Google, s'il ne s'en sert pas ailleurs.
- Vu, et laissé : la liste des agents, 1 400 jetons, dont `web-fetch` et
  `claude-code-guide` que fournit la plateforme ; un refus `Agent(nom)`
  désactive un agent, sans que la source dise qu'il l'ôte de la liste.
- Ce qui pèse désormais au départ : `CLAUDE.md` (le chantier 2), les
  définitions de l'orchestration, 5 600 jetons que seule la session
  d'orchestration appelle, et le prompt système, que rien ne règle.
