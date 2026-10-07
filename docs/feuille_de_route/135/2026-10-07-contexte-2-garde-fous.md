# Le contexte, étape 2 : les garde-fous mécaniques

**Reprise, au 7 octobre 2026.** À faire, quatre gestes sûrs, sans attendre la
mesure : un hook `PreToolUse` qui refuse de lire d'un bloc un fichier texte de
plus de 50 000 caractères, et dit de chercher puis de lire par fenêtre ; un
`.ignore` qui retire des recherches larges les gros fichiers fabriqués ; dans
`CLAUDE.md`, l'outil Grep conseillé plutôt que `grep -n` par Bash ; le mode
discret du hook d'Impeccable. Commencer par le hook, avec son test. La liste
des fichiers à ne jamais lire en entier reste dans `CLAUDE.md` jusqu'à
l'étape 3, qui la remplace par la règle du hook. Détail : ce fichier.

**Le 7 octobre 2026, ce qui est établi.**

- *Les gros fichiers.* 83 fichiers texte dépassent 50 000 caractères
  (`python scripts/arbre.py --plus-gros 90`). La liste « ne se lisent jamais
  en entier » de `CLAUDE.md` en nomme 17 ; trois sont l'outillage
  d'Impeccable ; les 63 autres n'y sont pas, dont
  `data/reference/referents.yaml`, `docs/limites.md`,
  `src/retraite_notionnelle/cout.py` et `tests/test_cout.py`.
- *Ce qu'un hook peut faire* (documentation de Claude Code, page des hooks).
  Un hook `PreToolUse` reçoit l'appel en JSON sur son entrée standard
  (`tool_name`, `tool_input`) ; il peut le refuser, avec une raison que le
  modèle lit (`hookSpecificOutput.permissionDecision` à `"deny"`, et
  `permissionDecisionReason`), ou en modifier l'entrée (`updatedInput`).
- *La recherche, essayée le 7 octobre.* L'outil Grep omet une ligne trop
  longue (« [Omitted long matching line] ») et respecte un `.ignore` : un
  fichier qui y est nommé disparaît d'une recherche dans son dossier, et se
  trouve encore quand on le cherche en le nommant. Le `grep` lancé par Bash,
  que `CLAUDE.md` conseille (« `grep -n` d'abord »), rend la ligne entière :
  `moteur/donnees.json` tient sur une ligne de 4 millions de caractères, et
  `tests/temoins/pages.json` a 63 lignes de plus de 10 000. Aucun script du
  dépôt n'appelle ripgrep : un `.ignore` ne touche que les outils de recherche.
- *Le hook d'Impeccable* (`.claude/settings.json`) passe après chaque `Edit`
  ou `Write` d'un fichier d'interface et pousse un rappel dans le contexte : un
  accusé court même quand le fichier est propre (CSS, HTML), jusqu'à cinq
  constats et 8 000 caractères sinon ; puis une passe complète au `Stop`.
  `.impeccable/config.json` ne règle que des valeurs ignorées : le hook tourne
  à ses valeurs par défaut. Le mode discret (`hook.quiet`) retire les accusés ;
  `.claude/skills/impeccable/reference/hooks.md` en donne les clés.

**Le plan.**

1. Le hook : `.claude/hooks/lecture.py`, déclaré dans `.claude/settings.json`
   sous `PreToolUse`, pour `Read`. Il refuse quand l'appel n'a pas de `limit`,
   que le fichier est du texte (`Read` lit autrement une image ou un PDF) et
   qu'il dépasse le seuil ; sa raison donne la taille et le geste : chercher,
   puis lire par `offset` et `limit`. Le seuil se compte en octets, par un seul
   `stat` (une lecture entière à chaque appel coûterait sous Windows), presque
   égaux aux caractères ici. Il tourne sous Windows comme dans le cloud, et ne
   bloque jamais sur une erreur : un fichier absent ou illisible laisse
   passer. Un test l'appelle avec des entrées JSON factices.
2. Un `.ignore` à la racine : les témoins JSON de `tests/temoins/`,
   `moteur/donnees.json`, `data/derive/*.json`, les données et scripts
   minifiés d'Impeccable (`.claude/skills/impeccable/scripts/data/`,
   `live-browser*.js`, `modern-screenshot.umd.js`). Rien de ce qu'une session
   lit en travaillant.
3. `CLAUDE.md`, « Chercher avant de lire » : l'outil Grep d'abord, `grep -n`
   par Bash sur un fichier qu'on sait sans ligne démesurée.
4. Impeccable en mode discret, dans `.impeccable/config.json`, après lecture de
   `reference/hooks.md`.

*Les pièges.* Un `cat` ou un `sed` lancé par Bash échappe au hook : la règle
de `CLAUDE.md` les couvre encore, et le hook pourra s'étendre à Bash si la
mesure (étape 1) montre qu'ils coûtent. `CLAUDE.md` est un document d'état
(`zones.yaml`) : `python scripts/verifier_prose.py --corriger` après l'avoir
touché. Un changement de `CLAUDE.md` ne vaut, pour une session, qu'à son
prochain démarrage.

En finissant, la session ôte le bloc « Reprise » de cette note, et ne touche
à celui de l'action que si elle est la dernière des cinq étapes.
