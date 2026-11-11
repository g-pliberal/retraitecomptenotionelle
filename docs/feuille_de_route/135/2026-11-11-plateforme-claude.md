# La plateforme Claude, lue contre nos réglages

**Le 11 novembre 2026, la demande.** Le propriétaire : « J'aimerais que tu
regardes la plateforme complète de Claude : https://platform.claude.com/ Il
faut que l'on prenne la meilleure configuration de notre projet en partant de
cette source. C'est la source officielle, on peut lui faire confiance. »

**La méthode.** L'index de la plateforme (`llms.txt`) compte 901 pages en
anglais. 580 sont la référence de l'API, un point d'entrée par page : laissées
de côté, le dépôt n'appelant pas l'API. Les 321 autres ont été copiées ce jour
en Markdown, avec les 203 pages de la documentation de Claude Code
(`code.claude.com/docs`), où se trouvent les réglages que la plateforme ne
fait que recommander : 524 pages, toutes rendues.

- *Lues par la session*, par fenêtres : le choix d'un modèle, l'effort, le
  guide « Optimizing for cost and intelligence », les nouveautés de Fable 5.2,
  les guides de rédaction de Fable 5.2, d'Opus 5.5, de Sonnet 5.5 et de
  Haiku 5.5, le guide général pour ce qu'il dit des agents, les tarifs, les
  notes de version ; chez Claude Code, `model-config`, `prompt-caching`,
  `costs`, `sub-agents`, `memory`, `hooks`, `cloud-environments`, `settings`
  et sa référence de 249 clés.
- *Confiées à quatre éclaireurs*, réglés sur Haiku, pour leur seul relevé : les
  agents hébergés (41 pages), l'administration, l'API et les SDK (97), les
  outils et les skills (43), et le reste de `build-with-claude` (la réflexion,
  le contexte, la compaction, le cache). Ce que cette note en reprend, la
  session l'a relu à la ligne.
- Le conteneur fait tourner Claude Code 2.1.322 : aucun réglage cité ici ne
  demande une version plus récente.

**Ce que le dépôt faisait déjà comme la source le dit.**

- *Les modèles.* « Most workloads start with Claude Opus 5.5 » ; Fable 5.2
  « for demanding reasoning and long-horizon agentic work, or when your evals
  on Claude Opus 5.5 at higher effort still fall short » ; Haiku 5.5 pour les
  « subagent tasks ». Le guide du coût mesure, sur 463 problèmes de SWE-bench
  Pro : Fable 5.2 à `high`, 96,3 % des tâches pour 1,39 $ la tâche résolue ;
  Opus 5.5 à `medium`, 93,1 % pour 0,22 $, à `high` 95,5 % pour 0,30 $, à
  `xhigh` 96,5 % pour 0,75 $ ; et, à son tableau, Sonnet 5.5 à `high`, 87,6 %
  pour 0,11 $. Sur sa recherche de défauts, l'épreuve qui ressemble le plus à
  la relecture d'une règle, Fable 5.2 seul fait, de `low` à `high`, de 1,6 à
  5,9 points de mieux qu'Opus 5.5 à `high`, pour 1,5 à 2,4 fois le coût.
  Fable 5.2 au scénario 1 est donc un choix que la source chiffre : un peu
  mieux, pour bien plus cher. Sur la même épreuve, Opus avec des sous-agents
  sur Sonnet coûte « about a third less » qu'une session Opus par partie,
  pour le même score.
- *L'effort.* Fable 5.2 : « Start with `high`. Most of the gain in capability
  is already present at `high`. » Sonnet 5.5 perd environ 7 points à `medium`
  sur SWE-bench Pro. Opus 5.5 part de `medium`, son défaut, et la source
  demande une mesure avant d'en changer : `high`, le choix du propriétaire du
  9 novembre, y gagne 2,4 points pour 36 % de plus par tâche résolue. Haiku 5.5 :
  « Start with `medium` for most work ». Les quatre éclaireurs de cette
  session, à `medium`, ont rendu des relevés cités à la ligne en 13 à 27
  appels et en 72 à 151 secondes chacun.
- *Une session neuve par étape, l'état dans git et dans le bloc « Reprise ».*
  Le guide général : « consider starting with a brand new context window
  rather than using compaction. Claude's latest models are extremely effective
  at discovering state from the local filesystem » ; « Use git for state
  tracking ».
- *Le cache.* Sur abonnement, dans l'usage inclus, la conversation principale
  garde son cache une heure et les sous-agents cinq minutes
  (`prompt-caching.md`, « Which TTL each request gets »). C'est le bon côté
  pour nos contextes. Sur l'étape M4 de la note du 3 novembre, au tarif
  d'Opus 5.5 (246 appels, un contexte porté de 76 184 à 523 140 jetons),
  écrire le cache à cinq minutes plutôt qu'à une heure économiserait 1,57 $,
  et une seule pause de plus de cinq minutes, sur un préfixe de 300 000
  jetons, en reprendrait 1,44 $. Ce que le dépôt ne notait pas : changer
  d'effort en cours de session ne vide plus le cache (« changing effort keeps
  the cache on Fable 5.1 and later, Opus 5.5, Sonnet 5.5, and Haiku 5.5 ») ;
  changer de modèle, toujours.
- *Les hooks plutôt que la prose*, pour ce qui doit se faire à un moment
  fixe (`memory.md` : « write it as a hook instead ») ; le hook de démarrage
  pour les dépendances (`cloud-environments.md` : « Use a SessionStart hook
  for project setup that should run everywhere ») ; `Explore` redéfini sur
  Haiku (`sub-agents.md` : « define one with `model: haiku` ») ; l'effort par
  `modelSettings`, et non par la variable, qui passerait devant celui des
  agents.

**Ce qui est fait**, avec l'accord du propriétaire, demandé avant : ce sont
deux gardes.

- *`StopFailure` publie comme `Stop`.* `hooks.md`, « Stop » : « Does not run
  if the stoppage occurred due to a user interrupt. API errors fire
  StopFailure instead. » Un tour qui mourait d'une limite d'usage ou d'une
  surcharge laissait donc ses commits dans le conteneur, que la plateforme
  reprend après une période d'inactivité : à la réouverture, seul l'historique
  de la conversation est rendu (`claude-code-on-the-web.md`, « Environment
  expired »). Le même `pousser.sh` part désormais sur `StopFailure`. Sa sortie
  et son code y sont ignorés : un refus s'y tait, et reparaît à la fin du tour
  suivant. Une interruption par le propriétaire ne lance toujours aucun hook.
- *La chaîne de secours : Opus, puis Sonnet.* `["sonnet", "opus"]` datait du
  17 octobre, quand Opus était le modèle le plus haut du dépôt. Or le modèle
  de secours tient « for the rest of the turn » (`settings-reference.md`), une
  étape est souvent un seul tour, et « Moving from Claude Fable 5.2 […] to any
  other model loses their reasoning for the turns that run there ». Un Fable
  saturé au vingtième appel d'une étape du scénario 1 la finissait sur Sonnet.
  Contrepartie : un éclaireur dont Haiku sature retombe sur Opus, plus cher
  que Sonnet.
- `tests/test_reglages_claude.py` tient les deux ; le skill `claude-api` dit
  la chaîne, et où lire la plateforme.

**Les quatre chantiers inscrits**, tous retenus par le propriétaire, chacun
pour une session neuve.

1. *Le contexte de départ.* `permissions.md` : « A bare tool name like `Bash`
   removes the tool from Claude's context entirely ». Une règle `deny` au nom
   nu retire donc de chaque requête la définition d'un outil que le dépôt
   n'emploie pas : `Artifact`, `Workflow`, les outils d'environnement, de
   tâches planifiées, de dossiers d'ordinateur et de suivi de pull requests du
   serveur `claude-code-remote`, les suggestions de plugins. Estimation de la
   session, non mesurée : 23 000 des 76 000 jetons de départ, de l'ordre de
   6 % d'une étape comme M4. À mesurer par `first_request_input_tokens`,
   avant et après ; la session d'orchestration garde `create_session`,
   `send_message` et `list_events`. S'y rattachent `skillOverrides` pour les
   skills fournis hors sujet, `disableClaudeAiConnectors`, et
   `includeGitInstructions: false`, que `memory.md` conseille quand
   `CLAUDE.md` fixe ses propres règles de commit. C'est une garde : l'accord
   du propriétaire, outil par outil.
2. *`CLAUDE.md` sous 200 lignes.* `memory.md` : « target under 200 lines per
   CLAUDE.md file. Longer files consume more context and reduce adherence » ;
   la racine en fait 259. La source propose les règles à portée de chemin
   (`.claude/rules/`, champ `paths`), chargées à la première lecture d'un
   fichier qui leur répond, pour ce qui ne vaut que pour une partie du dépôt,
   et un skill pour une procédure. Candidats : la prose et la documentation,
   le clone d'avant le 26 septembre et les branches `claude/*`, qui ne
   regardent qu'un poste, la relève de l'orchestration. La règle du scénario 1
   reste à la racine : elle doit se lire avant la bascule de modèle.
3. *Le bloc « Reprise » lisible.* Sa limite de dix lignes se tient à la lettre
   par des lignes de 300 à 400 caractères, semées de sigles de session : celui
   de l'action 130. Le guide de Fable 5.2 prévient que le modèle suit de près
   les règles de style, au point qu'une limite dure rend sa prose hachée, et
   donne pour un passage de relais : « Write for an intelligent but
   low-context reader. […] Do not use a term or abbreviation that you made up
   during the work. » Une limite en mots, et cette consigne. Le test est
   `test_chaque_action_en_cours_s_ouvre_sur_son_bloc_reprise`.
4. *Les éclaireurs sans le `CLAUDE.md` racine.* L'Explore d'origine démarre
   sans lui, « to keep research fast and inexpensive » ; le nôtre, qui le
   remplace pour tourner sur Haiku, l'a repris du même coup.
   `omitClaudeMd: true` le rend, les `CLAUDE.md` de zone se chargeant toujours
   à la lecture. Le guide de Haiku 5.5 relève qu'une longue consigne lui fait
   plus souvent sauter une recherche ou s'arrêter tôt, surtout à l'effort
   `low` : à `medium`, le gain attendu est modeste. Une carte du dépôt de
   quelques lignes passe dans leur fichier. Les agents se chargent à
   l'ouverture : l'effet se compare d'une session à l'autre, sur une même
   question.

**Lu, et laissé.**

- *Le conseiller* (`advisorModel`) : sur le banc de code de la plateforme,
  1,7 point de mieux, « at the edge of run-to-run noise », pour 2,1 fois le
  coût ; « the advisor bought about what more effort does ».
- *Le mode rapide*, au double du tarif ; *les budgets de tâche*, « not
  supported on Claude Code ».
- *`promptCacheTtl`* : le défaut convient. Hors de l'usage inclus, Claude Code
  retombe à cinq minutes ; `"1h"` le tiendrait à une heure, au propriétaire
  s'il dépasse son forfait.
- *La fenêtre de compaction* (`autoCompactWindow`), et la compaction d'une
  session laissée à l'arrêt (`idleCompaction`), qui ne vaut qu'au terminal,
  dans VS Code ou sur son poste : la relève par une session neuve fait mieux.
- *Le script de préparation de l'environnement*, mis en cache sept jours : le
  hook de démarrage suffit, et tient en un seul endroit.
- *La langue* (`language`) : les sessions répondent déjà en français, que la
  plateforme mesure à 99,6 % de l'anglais pour Fable 5.2, 99,3 % pour Opus
  5.5, 98,7 % pour Sonnet 5.5 et 97,7 % pour Haiku 5.5
  (`multilingual-support.md`).
- *Les plafonds de sous-agents* (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, 20
  par défaut, et `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, 3) : les sous-agents
  pèsent 2 % de la dépense.
- *La phrase de propriété du code* du guide de Fable 5.2 : de 70 à 80 % de
  jetons de sortie en plus, et des changements que personne n'a demandés.
- *L'administration* (l'API d'analyse, les plafonds de dépense) : « The Admin
  API isn't available to […] individual Claude Console accounts ». Reste
  `consommation.py`, et l'export OpenTelemetry, « Works on any plan ».
- *Les agents hébergés*, les outils de l'API, les SDK : rien qui s'applique à
  un dépôt qui n'appelle pas l'API.

**À savoir.**

- *Un fil de projet claude.ai, ou une session à plusieurs dépôts, n'applique
  pas `.claude/settings.json`* (`settings.md`, « Settings in cloud sessions » :
  « none of a repository's `.claude/settings.json` permission rules, hooks, or
  `env` apply ») : ni publication, ni garde du test d'abord, ni garde de
  lecture. Le dépôt se mène en session d'un seul dépôt, hors projet.
- *Haiku 5.5 coûte cinq fois plus* au-delà de 100 000 jetons de requête,
  cache compris dans le compte : 0,50 $ en entrée et 2,50 $ en sortie le
  million, contre 0,10 $ et 0,50 $.
- *Les tarifs du jour*, en dollars par million de jetons (entrée, écriture du
  cache à cinq minutes puis à une heure, lecture du cache, sortie) : Fable
  5.2, 8, 10, 16, 0,20 et 40 ; Opus 5.5, 4, 5, 8, 0,20 et 20 ; Sonnet 5.5, 2,
  2,50, 4, 0,10 et 10.
- *Le mot `ultrathink`*, dans une demande, pousse la réflexion de ce seul
  tour, sans toucher au réglage (`model-config.md`).
- *`/doctor prompt-audit`*, l'audit des consignes que fournit Claude Code,
  « runs through the bundled `/claude-api` skill », que le nôtre remplace : au
  propriétaire de l'essayer ; s'il ne répond pas, c'est le dossier de notre
  skill qui le masque.
