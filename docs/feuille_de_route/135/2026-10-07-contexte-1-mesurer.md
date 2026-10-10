# Le contexte, étape 1 : mesurer ce que les sessions consomment

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

**Le 7 octobre 2026, le script.** `scripts/consommation.py` lit les
transcriptions sous `~/.claude/projects/` (`CLAUDE_CONFIG_DIR` s'il est
posé), sous-agents compris (`<session>/subagents/`, une session chacun), ou
les fichiers et dossiers qu'on lui nomme ; `--jours` (30) et `--limite` (15).
Il suit la méthode ci-dessus, avec trois précisions relevées sur la
transcription de cette session-ci (Claude Code 2.1.292). Les `attachment`
portent, dans `rendered`, le texte qui va au modèle : c'est lui qui se compte,
et ceux qui n'en ont pas (`prompt_snapshot`, 225 000 caractères,
`deferred_tools_record`, `credential_org`) n'y vont pas. Le contexte de
départ se détaille entre ces ajouts, estimés à 3,5 caractères par jeton, et
le reste, « système et outils », que seule l'API mesure. Une commande Bash se
réduit à son verbe (`sed`, `git diff`, `python -m pytest`,
`python scripts/x.py`), et le fichier qu'un `cat`, `sed`, `head` ou `tail`
lit compte avec ceux de `Read`. La somme des parts égale exactement celle des
contextes de chaque appel, ce que le test vérifie.

- *Le premier relevé, cette session-ci, à mi-parcours* : 22 appels, contexte
  de 73 000 à 113 000 jetons, 2,1 millions relus. Le départ en fait 75 % :
  « système et outils », 59 000 jetons, 61 % à lui seul ; `CLAUDE.md`
  (l'attachement `instructions`), 5 000 jetons, 6 % ; la liste des skills,
  4 000, 4 %. Les sorties Bash, 13 %, et la sortie du modèle, 11 %. Une
  session courte qui lit par fenêtres paie donc surtout son départ, que
  l'étape 3 réduit pour `CLAUDE.md` et que le dépôt ne commande pas pour le
  reste. Rien n'y dit encore si les lignes géantes (étape 4) ou les gros
  fichiers (étape 5) coûtent : c'est ce que le relevé du poste tranchera.

En finissant, la session ôte le bloc « Reprise » de cette note, et ne touche
à celui de l'action que si elle est la dernière des cinq étapes.

**Le 10 octobre 2026, le relevé du poste.** `python scripts/consommation.py`
sur les seuls dossiers de ce dépôt sous `~/.claude/projects/` : ceux des
autres projets du poste ne regardent pas le dépôt, et n'y sont pas nommés.
Trente et une sessions, du 22 septembre au 10 octobre ; aucune du 7 au
9 octobre, menées dans le cloud, de sorte que l'effet des étapes 2 à 5 ne se
lit pas ici.

- *Une correction d'abord.* Une entrée `<synthetic>` — un appel interrompu,
  une erreur de l'API —, d'usage nul, comptait pour un appel de contexte nul :
  elle passait pour une compaction, et le contexte rechargé à l'appel suivant,
  jusqu'à 456 000 jetons, allait au rappel de vingt-cinq jetons qui la
  précédait. Les ajouts du harnais montaient ainsi à 11 % des jetons relus,
  et en font 3 %. Le script les écarte, et un test le tient.
- *Le total.* 9 451 appels, 3,70 milliards de jetons relus, 1 142 $ pour les
  vingt-trois sessions qui notent leur coût.
- *Ce qui est relu.* La sortie du modèle, réflexion comprise, 37,1 % ; les
  résultats de Bash, 32,9 %, dont `sed` 13,1 % et `grep` 5,7 % ; le départ
  « système et outils », que le dépôt ne commande pas, 12,1 % ; `Read`,
  5,3 % ; `CLAUDE.md`, 1,3 % ; la liste des skills, 1,0 %.
- *Les fichiers.* Toute lecture de fichier, par `Read` ou par Bash, fait
  20,5 % ; celles des 76 fichiers de plus de 50 000 octets, 10,1 % : la
  feuille de route 1,3 %, `scenarios/actuel.py` et `pages.js` 0,7 % chacun,
  `droit/liquider.py` 0,6 %, `docs/limites.md` 0,2 %, quand l'historique git
  le désignait le premier (étape 5). Le paquet, les témoins et
  `data/derive/`, les lignes géantes de l'étape 4, 0,3 %.
- *La longueur des sessions.* Un appel relit tout ce qui précède : le coût
  croît comme le carré du nombre d'appels. Les treize sessions de trois cents
  appels et plus font 72 % des lectures, et finissent entre 300 000 et
  960 000 jetons de contexte.
- *Le prix.* Aux tarifs relatifs de l'API — la lecture du cache au dixième de
  l'entrée, son écriture pour une heure au double, la sortie au quintuple —,
  la lecture du cache fait 79 % du coût, son écriture 12 %, la sortie 9 %.
  Les vingt-cinq recharges de plus de 50 000 jetons en font 5 % : vingt-trois
  suivent une pause de plus d'une heure, qui a laissé expirer le cache.

**Le verdict.** L'étape 4 ne valait pas son prix, et l'étape 5 peu : à
elles deux, elles visaient moins d'un dixième de la facture, et un découpage
n'y gagne que sur les lectures entières, que la garde de l'étape 2 empêche
déjà. Ce qui coûte, c'est la longueur des sessions : « une session, une
étape » est le levier, bien avant le rangement des fichiers. Viennent
ensuite les sorties de Bash, qu'une fenêtre plus étroite réduit, et la
sortie du modèle elle-même. Aucune étape de plus n'est ouverte : les cinq
sont closes.
