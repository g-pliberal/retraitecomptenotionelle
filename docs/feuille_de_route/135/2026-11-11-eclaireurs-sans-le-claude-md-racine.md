# Les éclaireurs sans le `CLAUDE.md` racine

**Le 11 novembre 2026.** Chantier 4 de la note « La plateforme Claude, lue
contre nos réglages » : que l'éclaireur et Explore, les deux agents qui lisent
pour la session, sur Haiku, démarrent sans le `CLAUDE.md` de la racine, comme
l'Explore d'origine de Claude Code. Sont faits le réglage, la carte du dépôt
qui le remplace, leur test et le relevé d'avant. La comparaison d'après reste
à faire, dans une session ouverte après ce commit : la fin de la note dit
comment.

**La source**, lue ce jour. `code.claude.com/docs/en/sub-agents.md` :
« Explore and Plan start without your CLAUDE.md files and the git status
snapshot to keep research fast and inexpensive. Other built-in and custom
subagents load both, unless you set `omitClaudeMd` in a custom subagent's
definition to start it without the user, project, and local CLAUDE.md
files. » Le champ demande Claude Code 2.1.271 ; les sessions du cloud
tournent sur 2.1.322. « For Explore, Plan, and subagents with
`omitClaudeMd`, a subdirectory's `CLAUDE.md` and matching path-scoped rules
still load when the subagent works with files there. » Et : « The main
conversation still has your full CLAUDE.md when it reads these subagents'
results, so most rules don't need to reach the subagent itself. If a rule
must, […] restate it in the prompt you give Claude when delegating. » Le
guide de Haiku 5.5 (`platform.claude.com`, `prompting-claude-haiku-5-5.md`)
dit de l'effort `low` : « In long agent prompts, the model is more likely to
skip a search, stop early, or skip a check at this level » ; d'une consigne
courte : « With a short system prompt, Claude Haiku 5.5 rarely stops before
the work is done » ; et de l'effort seul : « moving from `low` to `medium`
effort roughly halved early stopping ». Les deux agents sont à `medium` : le
gain de comportement attendu est modeste, et se constate.

**Ce qui est fait.**

- *Le réglage* : `omitClaudeMd: true` dans l'en-tête de
  `.claude/agents/eclaireur.md` et de `.claude/agents/Explore.md` ;
  `claude plugin validate .claude/agents` les accepte.
- *Une carte du dépôt* dans leur consigne, la même pour les deux, 169 mots
  sur vingt lignes : l'architecture et ses versions, l'état, la feuille de
  route et ses notes, les actions closes et les leurs, les trois zones et
  leurs consignes, les fiches de règles, les limites, le journal de veille,
  les tests et leurs témoins. Elle dit où restent les conventions, et que
  l'agent n'y cherche que si la demande porte sur elles : ouvert par
  précaution à chaque course, le `CLAUDE.md` reprendrait ce que le réglage
  ôte. Pour la même raison elle ne renvoie pas à `docs/carte_du_depot.md`,
  21 000 octets de schémas.
- *Le test*, dans `tests/test_reglages_claude.py`, vu rouge d'abord : les
  deux agents déclarent `omitClaudeMd: true` ; leur carte est la même, nomme
  chacun de ces lieux, ne cite que des chemins qui existent, et tient en 250
  mots, moins du dixième du `CLAUDE.md` qu'elle remplace.

**Ce qu'un agent de lecture reçoit au départ**, lu dans les transcriptions
des sous-agents de la session
(`~/.claude/projects/<dossier>/<session>/subagents/agent-*.jsonl`). Le
`CLAUDE.md` de la racine y entre par une pièce `instructions` de 16 995
caractères, de l'ordre de 5 000 jetons à 3,5 caractères le jeton,
l'estimation de `consommation.py`, sur un contexte de départ de 14 163 à
14 216 jetons pour l'éclaireur et de 14 373 à 14 398 pour Explore, selon la
longueur de la question. Chaque requête de l'agent relit ce départ, et une
course en fait de deux à cinq : les trois quarts des jetons relus par les
douze courses d'avant sont ce départ, relu. À requêtes égales, ôter le
`CLAUDE.md` retirerait donc le quart environ des jetons relus par des
questions de cette taille, moins la carte, quatorze fois plus légère que lui.
En dollars, presque rien : les sous-agents pèsent 2 % de la dépense. Le
`CLAUDE.md` de `data/` est arrivé de lui-même, par une pièce
`nested_memory`, aux deux courses qui ont lu une entrée du journal de veille.
Ce que le réglage ne touche pas : les consignes des serveurs MCP, 4 228
caractères, que reçoivent des agents qui n'ont aucun de leurs outils. Au
chantier du contexte de départ.

**Le relevé d'avant.** Six questions dont la session avait d'abord établi la
réponse par `grep`, posées telles quelles avant tout changement, deux fois
chacune pour connaître l'écart d'une course à l'autre. Une requête est un
appel au modèle, tel que `consommation.lire` le compte ; un outil, un appel
de recherche, sans le `SubagentHandback` par lequel l'agent rend son
rapport, que le compteur `tool_uses` de l'outil Agent compte, lui ; le
départ, le contexte de la première requête, cache compris ; les jetons
relus, la somme des contextes de toutes les requêtes ; les mots rendus, ceux
du rapport, chemins et balises compris. Une course dure de quatre à seize
secondes.

| Question | Requêtes | Outils | Départ | Jetons relus | Jetons de sortie | Mots rendus |
|---|---|---|---|---|---|---|
| A1, le seuil de lecture | 4, 4 et 3 | 5, 5 et 4 | 14 216 | 65 382, 65 870 et 48 562 | 1 670, 1 673 et 1 854 | 172, 147 et 178 |
| A2, l'action 148 | 4 et 3 | 5 et 4 | 14 179 | 78 985 et 53 762 | 1 976 et 1 544 | 85 et 131 |
| A3, le journal de veille | 3 et 3 | 3 et 3 | 14 163 | 63 084 et 57 001 | 1 159 et 1 130 | 105 et 92 |
| B1, l'effort | 5 et 5 | 9 et 5 | 14 398 | 128 868 et 112 440 | 3 533 et 2 983 | 295 et 285 |
| B2, les consignes de zone | 4 et 4 | 8 et 6 | 14 382 | 67 319 et 65 578 | 2 179 et 1 883 | 218 et 206 |
| B3, les témoins | 3 et 2 | 4 et 1 | 14 373 | 49 385 et 32 422 | 1 594 et 842 | 150 et 108 |
| Les six, par série | 23 et 21 | 34 et 24 | | 453 023 et 387 073 | 12 111 et 10 055 | |

D'une série à l'autre, sans que rien ait changé, les outils passent de 34 à
24 et les jetons relus baissent de 15 % ; sur la seule B3, de quatre outils à
un. Un écart d'après plus petit que celui-là ne dira rien. La troisième
course d'A1 est une sonde lancée après la retouche des agents, qui a tourné
sur leur ancienne définition (voir plus bas) : elle compte avec l'avant.

**Les questions, ce qui était attendu, ce qui a été rendu.** Les lignes et
les tailles sont celles de l'arbre que les agents ont lu. La session d'après
les relève de nouveau : la règle du bloc « Reprise », récrite le même jour, a
déjà descendu de six lignes celle des 50 000 octets dans le `CLAUDE.md`, qui
doit encore maigrir (chantier 2).

- *A1, à l'éclaireur.* « Où le dépôt fixe-t-il le seuil au-delà duquel un
  fichier texte ne se lit pas en entier ? Rends le fichier:ligne de la
  constante du hook qui le tient, avec sa valeur telle qu'elle est écrite, et
  le fichier:ligne de la règle écrite que ce hook fait respecter, citée mot
  pour mot. Cent cinquante mots au plus. » Attendu :
  `.claude/hooks/lecture.py:19`, `SEUIL = 50_000` ; `CLAUDE.md:126-129`, « Un
  fichier texte de plus de 50 000 octets ne se lit jamais en entier, ni par
  `Read`, que le hook `.claude/hooks/lecture.py` refuse alors sans `limit`,
  ni par `cat`, qu'il ne voit pas ». Rendu : la valeur et la règle, justes,
  aux trois courses ; la ligne 19 à la première, la 18 aux deux autres ; la
  citation entière aux deux premières, coupée à « que le hook », et dite
  coupée, à la troisième. Chacune a cherché puis lu dans le `CLAUDE.md`
  qu'elle avait déjà dans son contexte, pour en tenir les lignes. Deux
  expliquent une recherche vaine par une espace insécable que le fichier n'a
  pas : la phrase y passe à la ligne entre « 50 000 » et « octets ».
- *A2, à l'éclaireur.* « L'action 148 de la feuille de route : dans quel
  fichier et à quelle ligne se trouve son titre, quel est ce titre mot pour
  mot, quel est son état, et où sont ses notes (le dossier, et le nom de
  chaque fichier) ? Cent cinquante mots au plus. » Attendu :
  `docs/archives/feuille_de_route.md:16563`, « 148. Plusieurs sessions sans
  se marcher dessus : la fabrique à GitHub, les journaux séparés », `fait` ;
  `docs/archives/feuille_de_route/148/`, `2026-10-06-etape-2.md` et
  `2026-10-06-etape-3.md`. Rendu : tout, juste, aux deux courses ; la seconde
  s'en est assurée par `python scripts/reprise.py 148`.
- *A3, à l'éclaireur.* « Quelle entrée du journal de veille porte sur les
  trois modèles de l'action 135 ? Rends son chemin, sa date, et, mot pour
  mot, ce qu'elle dit avoir consulté. Cent cinquante mots au plus. »
  Attendu : `2026-10-17-action-135-trois-modeles.yaml`, dans
  `data/reference/legislation/journal_de_veille/`, du 17 octobre 2026, et
  son champ `consulte`, qui s'ouvre sur « Aucune source de droit : la session
  ne touche à aucune règle du scénario 1 ». Rendu : tout, juste, le champ
  entier mot pour mot, aux deux courses.
- *B1, à Explore.* « Recense tous les endroits où le dépôt règle l'effort des
  modèles et des agents de Claude Code — les réglages, les fichiers d'agents
  — et le test qui les tient. Pour chacun, fichier:ligne et la valeur telle
  qu'elle est écrite. Ampleur moyenne ; trois cents mots au plus. » Attendu :
  `.claude/settings.json:6-8`, les trois modèles à `"effortLevel": "high"` ;
  la ligne 6 des six fichiers d'agents, `effort: medium` partout, sauf
  `effort: high` pour `impeccable-finish-reviewer.md` ;
  `tests/test_reglages_claude.py`, ses deux tests de l'effort. Rendu : tout,
  juste, aux deux courses, avec ce qu'aucun test ne tient, les quatre agents
  d'Impeccable, et la phrase du `CLAUDE.md` sur Fable 5.2.
- *B2, à Explore.* « Où sont les consignes propres à chaque zone du dépôt —
  le modèle, son portage et le site, les données — et, pour chacune, à quelle
  ligne s'ouvre sa liste de contrôle, sous quel titre ? Ampleur rapide ; deux
  cents mots au plus. » Attendu : `src/CLAUDE.md:85`, « ## Liste de
  contrôle » ; `moteur/CLAUDE.md:114`, « ## Listes de contrôle » ;
  `data/CLAUDE.md`, qui n'en a pas. Rendu : tout, juste, aux deux courses,
  l'absence dite comme telle.
- *B3, à Explore.* « Les témoins des tests : dans quel dossier sont-ils,
  combien de fichiers y a-t-il, quels sont les cinq plus gros avec leur
  taille en octets, et quel script les résume ? Ampleur rapide ; deux cents
  mots au plus. » Attendu : `tests/temoins/`, 42 fichiers ; `pages.json`,
  12 197 954 octets, `simulations.json`, 12 187 592, `trajectoire.json`,
  763 723, `drees_eacr_tables_2026.json`, 728 608, et
  `exemples_officiels.yaml`, 264 163 ; `scripts/resumer_temoins.py`. Rendu :
  tout, juste, aux deux courses. La première a écrit un fichier de tri,
  `/tmp/x`, hors du dépôt, et l'a dit : sa consigne lui interdit d'en écrire
  aucun.

Treize courses, treize réponses justes sur le fond ; deux numéros de ligne
faux d'une unité, une explication fausse deux fois donnée, un fichier écrit
hors du dépôt, et quatre rapports au-delà du nombre de mots demandé, de 19 %
au plus (A1 deux fois, B2 deux fois).

**Les agents se chargent-ils à l'ouverture ?** La source dit que non :
« Claude Code watches `~/.claude/agents/` and `.claude/agents/`. When you add
or edit a subagent file on disk, […] Claude Code detects the change within a
few seconds and the next delegation uses the updated definition, with no
restart needed. » Ce n'est pas ce que la session a vu. Trois délégations à
l'éclaireur, 17 secondes, 48 secondes puis 6 minutes après la retouche de son
fichier, dans le même tour, ont tourné sur l'ancienne définition : même
empreinte du prompt système (`systemHash`, dans `agent-*.prefix.json`), le
`CLAUDE.md` toujours dans la pièce `instructions`, et l'agent, interrogé, ne
se connaît que ses deux anciennes sections. La note du 17 octobre avait vu
un agent neuf se charger « au tour suivant ». Qu'un tour de plus suffise ou
qu'il faille une session neuve, cette session, qui tient en un tour, ne peut
pas le dire : la comparaison se fait dans une session ouverte après ce
commit, qui s'assure d'abord de la définition qu'elle fait tourner.

**La comparaison d'après**, pour cette session-là.

1. S'assurer de la définition : poser A1 à l'éclaireur, puis lancer la
   commande ci-dessous. La pièce `instructions` doit avoir disparu, et le
   départ être tombé de 14 216 vers 9 700 jetons, si l'estimation tient.
   Sinon le réglage n'a pas pris : le dire au propriétaire, et s'arrêter là.
2. Relever de nouveau par `grep` ce qui est attendu, puis poser les six
   questions, telles quelles, deux fois chacune, à l'agent qui a eu chacune.
3. Comparer au tableau : les réponses sont-elles toujours justes ; les
   requêtes, les outils et les jetons relus sortent-ils de l'écart d'une
   série d'avant à l'autre ? Et deux choses que le tableau ne montre pas :
   l'agent ouvre-t-il le `CLAUDE.md` de la racine quand la question ne porte
   pas sur lui (seule A1 y mène) ; le `CLAUDE.md` de `data/` arrive-t-il
   toujours à A3, par `nested_memory` ?
4. Conclure, dans une note et dans le bloc « Reprise » : garder le réglage,
   retoucher la carte, ou revenir en arrière si les réponses se dégradent.

```bash
python - <<'EOF'
import json, pathlib, sys
sys.path.insert(0, "scripts")
import consommation
transcriptions = pathlib.Path.home().glob(".claude/projects/*/*/subagents/agent-*.jsonl")
for f in sorted(transcriptions, key=lambda f: f.stat().st_mtime):
    s = consommation.lire(f)
    titre = json.loads(f.with_suffix("").with_suffix(".meta.json").read_text())["description"]
    print(titre, len(s.appels), sum(p.categorie == "outil" for p in s.parts),
          s.appels[0].contexte, sum(a.contexte for a in s.appels), sum(a.sortie for a in s.appels),
          {p.etiquette: round(p.estimation) for p in s.parts if p.etiquette in ("instructions", "nested_memory")})
EOF
```

Chaque ligne donne la description passée à l'appel, les requêtes, les
outils, le départ, les jetons relus, les jetons de sortie, puis les consignes
reçues, en jetons estimés : `instructions` au départ, 4 856 avant ce commit,
`nested_memory` à la lecture d'un fichier d'une zone.
