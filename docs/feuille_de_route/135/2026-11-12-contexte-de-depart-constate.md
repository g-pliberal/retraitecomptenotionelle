# Le contexte de départ, constaté, et où va la dépense sur Fable 5.2

**Le 12 novembre 2026, la demande.** Le propriétaire : « Est-ce qu'on ne
pourrait pas encore améliorer des choses ? Il me semble que c'était l'action
135 ». La session, ouverte après les réglages du 11 novembre, fait d'abord le
constat que la note « Le contexte de départ » laissait à une session neuve,
puis cherche ce qui reste.

**Le constat.** `python scripts/consommation.py --limite 80`, et la
transcription de la session pour les nombres exacts.

- *Le premier appel* : 43 539 jetons, contre 89 147 le 11 novembre. La
  fourchette attendue était de 40 000 à 45 000.
- *Vingt-huit définitions d'outils*, celles que la note annonçait, à l'outil
  près ; 24 000 jetons au lieu de 68 000.
- *Les consignes git de Bash sont parties* : sa description, 4 505
  caractères, ne porte plus ni « Commit or push only when the user asks » ni
  « branch first ». `includeGitInstructions: false` agit donc, à l'ouverture
  de la session, ce que le sous-agent témoin du 11 n'avait pas pu montrer.
- *La composition* : les définitions d'outils 24 000 jetons, le prompt
  système 7 000, la liste des skills 4 000, `CLAUDE.md` 4 000, la liste des
  agents 2 000, les consignes des serveurs MCP 1 000, les noms des outils
  différés 1 000.

**Ce que les refus n'emportent pas.** Un refus retire les outils d'un
serveur, non ses consignes : celles de Claude Docs, 1 950 caractères, et des
quatre connecteurs Google, 400, entrent toujours dans chaque session, dont
les outils sont pourtant refusés. Elles ne partent qu'avec le connecteur,
sur claude.ai.

**Ce qui reste dans le contexte de départ, et à qui.**

- *Au propriétaire, sur claude.ai* : les quatorze skills de son compte font
  10 213 des 14 988 caractères de la liste des skills, de l'ordre de 2 700
  jetons. `skills.md` le confirme, lu ce jour : « Skill synced from
  claude.ai: turn the skill off for your claude.ai account » ;
  `skillOverrides` n'y peut rien. Avec les consignes de Claude Docs et des
  connecteurs Google, 3 300 jetons.
- *Hors de portée du dépôt* : les dix-sept définitions du serveur des
  sessions, 12 000 jetons, dont une session ordinaire n'appelle presque
  rien. `mcp.md`, « Defer a server's tools », ne les renvoie derrière la
  recherche d'outils que par `"alwaysLoad": false` dans l'entrée du serveur,
  et celui-ci n'a pas d'entrée dans le dépôt : la plateforme le fournit. Le
  prompt système, 7 000 jetons, ne se règle pas.
- *Dans le dépôt, pour peu* : `skillOverrides` connaît une valeur
  `"name-only"`, qui garde le nom d'un skill sans sa description. Sur
  `impeccable`, `unslop`, `code-review` et `update-config`, 3 100 caractères,
  de l'ordre de 800 jetons. C'est une garde, pour 0,04 $ par étape de 250
  appels : laissé.

Le contexte de départ n'a donc plus rien à rendre que le propriétaire ne
tienne sur claude.ai.

**Où va la dépense maintenant : huit sessions du 11 novembre au soir.** Les
huit premières des seize sessions ouvertes après les réglages, de 22 h 06 à
23 h 52 UTC, toutes sur Fable 5.2 à l'effort `high`. Un agent sur Haiku a
relevé leurs événements `result` (`list_events`, méthode de la note du
3 novembre) ; la session a recoupé chaque ligne : la lecture du cache à
0,20 $ le million, son écriture à 16 $ et la sortie à 40 $, tarifs lus ce
jour, redonnent le coût affiché à cinq centimes près. Les titres sont ceux
des sessions, que le relevé coupe à quarante caractères.

| session | coût | appels | contexte, du premier au dernier appel | lecture | écriture | sortie |
|---|---|---|---|---|---|---|
| « Efficacité du projet, lecture des bases » | 19,38 $ | 152 | 43 830 → 388 956 | 4,96 $ | 6,22 $ | 8,17 $ |
| l'orchestration de l'action 184 | 10,75 $ | 105 | 44 952 → 258 985 | 3,08 $ | 4,14 $ | 3,47 $ |
| action 184, étape 4, la liste des textes | 5,66 $ | 69 | 44 249 → 170 730 | 1,49 $ | 2,29 $ | 1,88 $ |
| étape 5, KALI dans l'index | 9,81 $ | 92 | 44 389 → 250 802 | 2,79 $ | 3,57 $ | 3,45 $ |
| étape 6, la lecture : « le code… » | 13,61 $ | 114 | 44 901 → 336 269 | 4,71 $ | 4,93 $ | 3,96 $ |
| étape 6 : « la fonct… » | 8,32 $ | 74 | 44 668 → 241 029 | 2,19 $ | 3,41 $ | 2,72 $ |
| étape 6 : « les non-… » | 8,84 $ | 83 | 44 652 → 260 810 | 2,58 $ | 3,73 $ | 2,50 $ |
| étape 6 : « les autr… » | 11,08 $ | 99 | 44 911 → 297 451 | 3,39 $ | 4,31 $ | 3,38 $ |
| ensemble | 87,45 $ | 788 | | 25,20 $ | 32,60 $ | 29,53 $ |

Les appels de trois d'entre elles peuvent être sous-comptés : l'agent s'est
arrêté à trois pages d'événements. Les sous-agents, sur Haiku, font 0,05 $.

- *La relecture n'est plus le premier poste.* Le 3 novembre, sur Opus, la
  lecture du cache faisait 59 % du coût, son écriture 19 %, la sortie 22 %.
  Sur Fable 5.2 : 29 %, 37 % et 34 %. Fable écrit et sort au double du prix
  d'Opus, et relit au même. Ce qui coûte, c'est chaque jeton qui entre dans
  le contexte, 16 $ le million une fois, et chaque jeton que le modèle écrit,
  40 $ puis 16 $ ; la relecture ne les rattrape qu'au bout de quatre-vingts
  appels.
- *Le cache ne s'est récrit nulle part* : l'écriture de chaque session égale
  son contexte final, à 27 906 jetons près pour six d'entre elles, qui ont
  trouvé le début de leur contexte, définitions d'outils et prompt système,
  dans le cache d'une session ouverte dans l'heure. L'orchestration finit à
  258 985 jetons, contre 866 462 le 3 novembre : la relève tient.
- *La réflexion* fait 46 % de la sortie, 13,48 $ : 15 % du coût, avant ce
  qu'elle coûte à écrire dans le cache et à relire.
- *Ce que les réglages du 11 ont rendu sur ces huit sessions* : 45 608 jetons
  de moins à chacun des 788 appels, 7,19 $ de lecture, et leur écriture à
  l'ouverture des deux sessions qui n'ont pas trouvé le début en cache,
  1,46 $. Un dixième de ce qu'elles auraient coûté.
- *Les huit sont sur Fable 5.2*, l'orchestration et les deux étapes d'outillage
  comprises. `CLAUDE.md` réserve Fable à l'étape qui écrit ou change une règle
  du scénario 1, sans dire sur quel modèle vont les autres ; `create_session`
  donne à la session lancée le modèle de celle qui la lance (« Defaults to
  the calling session's model »), et le skill `orchestration` ne dit rien du
  modèle. Une orchestration ouverte sur Fable y met donc toute sa vague. Aux
  mêmes jetons, le tarif d'Opus 5.5 ferait 56,27 $ au lieu de 87,45 $, 36 %
  de moins. La session n'a pas lu ce que chaque étape a fait : la lecture des
  textes, à l'étape 6, relève peut-être du choix du propriétaire.

**Ce qui reste, par ordre de poids.**

1. *Au propriétaire : le modèle des sessions qui n'écrivent aucune règle du
   scénario 1* — l'orchestration, l'outillage, le site, l'archivage. Les
   ouvrir sur Opus 5.5, et faire dire au skill `orchestration` de passer
   `model` à `create_session`, Fable pour la seule étape que `CLAUDE.md`
   désigne. C'est le seul levier de plus de 10 % qui reste.
2. *Au propriétaire : la mémoire des calculs sur GitHub* (`actions/cache`).
   La course du 11 novembre à 21 h 48 UTC a duré 25 minutes : 5 min 31 de
   fabrication, 18 min 07 de suite complète, 1 min 20 de garde des
   présomptions. C'est du temps, non des jetons : le verdict arrive une
   demi-heure après l'envoi, et vingt-cinq commits l'attendaient à l'ouverture
   de cette session. `tests.yml` est une garde.
3. *Au propriétaire, sur claude.ai* : les quatorze skills du compte et les
   connecteurs Claude Docs et Google, 3 300 jetons, moins de 1 % d'une étape.
4. *Une session neuve* : la comparaison des éclaireurs, note
   `2026-11-11-eclaireurs-sans-le-claude-md-racine.md`.
5. *Non mesuré* : ce qui entre dans le contexte d'une étape, lecture par
   lecture. `consommation.py` le donne dans le conteneur de la session, non
   d'une autre ; une session qui finit une étape peut y lire ses trois plus
   grosses lectures et les noter. Sessions entières sur Sonnet, changement
   transversal seul : les deux décisions anciennes, inchangées.
