# Le contexte, étape 1 : mesurer ce que les sessions consomment

**Reprise, au 7 octobre 2026.** À faire : `scripts/consommation.py`, qui lit
les transcriptions des sessions Claude Code et classe ce qui a coûté, par
fichier lu, par commande, par hook et par session : chaque ajout au contexte,
en jetons, multiplié par le nombre d'appels qui l'ont relu. La méthode est
éprouvée sur une session (plus bas) ; reste à l'écrire, avec ses tests sur des
transcriptions factices, puis à la lancer sur celles du poste, où vivent les
sessions locales. Indépendante des autres étapes ; la 4 et la 5 attendent son
verdict. Fini quand cette note dit, chiffres à l'appui, ce qui coûte, et
laquelle des étapes 4 et 5 vaut son prix. Détail : ce fichier.

**Le 7 octobre 2026, la demande.** Le propriétaire, l'arbre du dépôt en main
(`2026-10-07-arbre-du-depot.md`) : « Maintenant que nous avons une vision
objective, qu'est-il possible de faire ? » L'arbre dit ce qui existe ; la
facture dépend de ce qui entre dans le contexte, relu à chaque appel qui suit.
D'où cinq étapes : cette mesure, les garde-fous (2), `CLAUDE.md` par zone (3),
les lignes géantes (4), le découpage des gros fichiers (5) ; les étapes 1 et 2
se mènent ensemble, la 3 après la 2, la 4 et la 5 sur le verdict de la 1.

- *Où sont les transcriptions.* Un fichier JSONL par session, sous
  `~/.claude/projects/<dossier de travail, en tirets>/` : sur le poste du
  propriétaire, un dossier par worktree, les trente derniers jours par défaut ;
  dans un conteneur du cloud, la seule session en cours. Les sessions passées
  du cloud se lisent par l'API des sessions (`list_events`), sous une autre
  forme.
- *Leur forme, relevée le 7 octobre* (Claude Code 2.1). Une entrée par ligne,
  de `type` `user`, `assistant`, `attachment`, `system`, `cost-state`… Une
  réponse de l'API se répartit sur plusieurs entrées `assistant`, une par bloc
  (`thinking`, `text`, `tool_use`), qui partagent leur `requestId` : un appel
  se compte une fois par `requestId`. Son `message.usage` porte
  `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` et
  `output_tokens` ; le contexte de l'appel est la somme des trois premiers. Les
  résultats d'outils sont des blocs `tool_result` (`tool_use_id`, `content`)
  des entrées `user` ; les `attachment` sont ce que le harnais ajoute
  (rappels, sorties de hooks, outils devenus disponibles) ; `cost-state` porte
  `totalCostUSD`.
- *La méthode, éprouvée sur la session qui a écrit l'arbre* (cloud, 90
  appels) : la croissance du contexte d'un appel au suivant, multipliée par le
  nombre d'appels qui restent, attribuée à ce qui est entré entre les deux. Le
  contexte y est passé de 55 919 à 360 659 jetons ; 18,7 millions de jetons
  relus en tout, pour 9,55 $ ; le contexte de départ, relu 90 fois, en fait
  27 %. Compter en caractères trompe : deux captures d'écran lues par `Read`
  pesaient 500 000 caractères de base64, pour quelques milliers de jetons.
- *Ce que la croissance mêle.* La sortie du modèle à l'appel précédent,
  réflexion comprise (`output_tokens`), les résultats d'outils, et ce que le
  harnais ajoute : la plus forte hausse de cette session, 26 743 jetons,
  suivait le premier appel, quand la liste des outils MCP devenus disponibles
  est arrivée avec lui. Le script sépare les trois : la sortie par
  `output_tokens`, le reste au prorata de la taille des blocs, une image
  comptée pour largeur × hauteur / 750 jetons.
- *Ce qu'il imprime.* Par session : les appels, le contexte de départ et
  d'arrivée, les jetons relus, le coût, et la part du contexte de départ, des
  sorties du modèle, des résultats d'outils et des ajouts du harnais. Puis,
  toutes sessions confondues, les fichiers lus (`Read`, `cat`, `sed -n`), les
  commandes (`pytest`, `git diff`, `grep`…) et les hooks qui ont le plus
  coûté. Un contexte qui retombe d'un appel au suivant est une compaction :
  ce qui la précède cesse d'être relu.

En finissant, la session ôte le bloc « Reprise » de cette note, et ne touche
à celui de l'action que si elle est la dernière des cinq étapes.
