# Ce que coûtent les sessions : la relecture du contexte, la réflexion, l'orchestration

**Le 3 novembre 2026, la demande.** Le propriétaire : « Comment pourrait-on
économiser des tokens sur notre dépôt ? J'ai l'impression que l'on consomme
énormément de tokens en ne faisant pas grand chose. » Il tenait à garder un
effort élevé, et doutait que Haiku et Sonnet aient aidé, un petit modèle
pouvant consommer plus qu'un grand sur une tâche difficile.

**La méthode.** `consommation.py` lit les transcriptions du poste, et le
conteneur d'une session du cloud n'a que la sienne. Chaque session écrit en
revanche, à la fin de chaque tour, un événement `result`, que rend l'outil
`list_events` du serveur `claude-code-remote` (`kinds: ["result"]`,
`limit: 100`, sans curseur, pour le plus récent) : `modelUsage`, cumulé depuis
l'ouverture de la session, modèle par modèle (entrée, écriture et lecture du
cache, sortie, réflexion, `costUSD` au tarif public, `costBasis: list`) ;
`model_usage_since_last_result`, le seul tour ; `num_turns`, ses appels ;
`first_request_input_tokens`, le contexte du premier appel ; et, dans
`usage.iterations`, celui du dernier (`cache_read_input_tokens`). Tarifs du
jour, en dollars par million de jetons : Opus 5.5, 4 en entrée, 8 pour
l'écriture du cache à une heure, 0,20 pour sa lecture, 20 en sortie ; Sonnet
5.5, la moitié ; Haiku 5.5, 0,10, 0,20, 0,01 et 0,50 jusqu'à 100 000 jetons
de contexte.

**Six sessions du 3 novembre**, au tarif public :

| session | coût | appels | contexte, du premier au dernier appel | sous-agents |
|---|---|---|---|---|
| l'orchestration, en cumul | 60,56 $ | — | → 866 462 | Haiku, 0,0007 $ |
| M4, le taux plein des parents de trois enfants | 21,86 $ | 246 | 76 184 → 523 140 | aucun |
| R-M4, sa relecture indépendante | 14,30 $ | 158 | 75 226 → 413 403 | aucun |
| « Vérification montants cotisés », du propriétaire | 17,93 $ | — | → 478 639 | l'éclaireur sur Haiku, 0,59 $ |
| le site, le budget de mots de `/simuler` | 9,33 $ | 133 | 76 162 → 303 855 | aucun |
| la Cnav, « rien à réparer » | 7,51 $ | — | → 252 715 | Sonnet, 1,95 $ (deux généralistes, dont un a échoué) ; Haiku, 0,28 $ |

- *Les sous-agents pèsent 2 %* : 2,82 $ sur 131,48 $, et quatre sessions sur
  six n'en ont lancé aucun. Haiku et Sonnet n'expliquent pas la dépense, et
  ne la réduiraient guère. L'éclaireur tournait à `max`, comme tout le reste :
  135 843 de ses 154 871 jetons de sortie, 88 %, étaient de la réflexion, d'où
  sa lenteur (neuf minutes et 52 outils pour une recherche, note du
  17 octobre), pour quelques centimes.
- *La relecture du contexte fait l'essentiel.* Sur M4, R-M4 et le site, tout
  Opus, la lecture du cache fait 59 % du coût (26,99 $ sur 45,48 $), son
  écriture 19 %, la sortie 22 %. Une étape fait de 130 à 250 appels, qui
  relisent chacun de 186 000 à 278 000 jetons en moyenne ; le contexte de
  départ en fait de 27 à 41 %. `consommation.py`, sur la session qui écrit
  cette note, le détaille : 61 000 jetons pour le système et les outils de la
  plateforme, 5 000 pour la liste des skills, 5 000 pour `CLAUDE.md`, 3 000
  pour les noms des outils différés, ceux d'ElevenLabs surtout, 2 000 pour les
  consignes des serveurs MCP.
- *La réflexion pèse le tiers.* Opus 5.5 garde toute sa réflexion passée dans
  le contexte (`thinking.md`, documentation de l'API : « Keep all prior
  turns: Claude Opus 4.5 and later Opus models, Claude Sonnet 4.6 and later
  Sonnet models, Claude Haiku 5.5 »). Elle forme le quart du contexte final —
  138 833 jetons sur 523 140 pour M4, 99 953 sur 413 403 pour R-M4, 79 584 sur
  303 855 pour le site — et se paie trois fois : en sortie, à l'écriture du
  cache, puis à chaque relecture. Pour M4, 2,78 $ de sortie, 1,11 $
  d'écriture et, à la supposer répartie également le long des 246 appels,
  3,4 $ de relecture : 7,3 $ sur 21,86 $.
- *L'orchestration.* Son contexte, 866 462 jetons au dernier appel, ne paraît
  pas avoir été compacté (la compaction vient vers 967 000) : ses écritures de
  cache, 1 705 855 jetons, font ce contexte plus une réécriture entière.
  Près de la moitié est sa propre sortie, 407 637 jetons, réflexion comprise.
  Chaque appel y relit pour 0,17 $ ; un compte rendu reçu lui coûte de 0,64 $
  (10 h 36 UTC, quatre appels) à 1,52 $ (11 h 14, huit appels). Une heure
  sans appel vide son cache : à 10 h 29, 61 minutes après la fin de son tour
  précédent, elle a récrit 845 511 jetons, 6,76 $, dans un tour de six appels
  et 7,69 $ qui relayait la fin de M4.
- *La relecture indépendante* a coûté 65 % de l'étape relue (14,30 $ pour
  21,86 $), et y a trouvé l'erreur grave de l'Agirc-Arrco.

**L'effort** (`model-config.md`, `sub-agents.md`, `settings-reference.md`,
lus le 3 novembre). Opus 5.5, Sonnet 5.5 et Haiku 5.5 offrent cinq crans,
`low`, `medium`, `high`, `xhigh` et `max`, et commencent à `medium`.
`CLAUDE_CODE_EFFORT_LEVEL=max` passait devant tout : une session ne pouvait
le baisser par `/effort`, et l'effort que déclare un agent était ignoré
(« Overrides the session effort level, but not the CLAUDE_CODE_EFFORT_LEVEL
environment variable »). `modelSettings` fixe l'effort d'un modèle, jusqu'à
`xhigh` : `max` ne s'impose que par la variable.

**Ce qui est fait**, à la demande du propriétaire : « A. Passe à xhigh pour
opus. Pour éclaireur et explore, j'ai peur que ce soit trop faible en low.
B. Oui C. Oui ».

- *L'effort à `xhigh`* pour Opus 5.5 par `modelSettings`, dans
  `.claude/settings.json`, la variable ôtée ; Sonnet 5.5 de même, pour que les
  agents généralistes et une session ouverte sur Sonnet ne retombent pas à
  `medium`, leur défaut.
- *L'éclaireur et Explore à `high`*, le cran sous `xhigh`, puisque `low`
  paraissait trop faible au propriétaire ; Haiku, à son défaut, serait à
  `medium`. Les agents d'impeccable tournent désormais à l'effort qu'ils
  déclarent : `medium` pour les trois sur Sonnet, `high` pour le relecteur,
  sur le modèle de la session.
- *`tests/test_reglages_claude.py`* tient ces réglages : l'effort par modèle
  et non par la variable, et celui des deux agents.
- *La relève de l'orchestration*, nouvelle règle d'« Économiser le contexte »
  (`CLAUDE.md`) : une vague close, la session d'orchestration ne lance pas la
  suivante ; elle ouvre la session qui lui succède, avec son état pour
  consigne, et s'arrête. Une session neuve repart vers 80 000 jetons.
- *Le skill `claude-api`* dit le nouveau réglage.

**Ce qui reste.**

- Relever, sur les sessions des jours qui viennent, la réflexion de chacune
  (`thinkingTokens`) à `xhigh`, contre les chiffres de cette note.
- La session d'orchestration ouverte ne lit pas la nouvelle règle :
  `CLAUDE.md` ne se charge qu'à l'ouverture. Il faut la lui dire.
- Au propriétaire : essayer Sonnet 5.5 pour des sessions entières où les
  tests tiennent serré — le site, l'outillage, l'archivage —, et comparer
  leurs appels et leur coût à ceux d'une session Opus comparable : au-delà du
  double des appels, Sonnet coûte plus ; réserver la relecture indépendante
  aux règles du scénario 1 ; couper le connecteur ElevenLabs, dont les
  outils, inutiles ici, entrent dans le contexte de chaque session (il s'est
  déconnecté de la session qui écrit cette note, en cours de route).
