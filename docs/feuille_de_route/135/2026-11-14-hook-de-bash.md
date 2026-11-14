# Le hook de Bash : le `cat` d'un gros fichier refusé, la queue des sorties longues

**Le 14 novembre 2026, la demande.** La session d'orchestration confie cette
étape : fermer le trou que `CLAUDE.md` signalait à la puce « Chercher avant de
lire » — un fichier de plus de 50 000 octets ne se lit pas en entier, « ni par
`cat`, qu'il ne voit pas » — et, si une réécriture garde le code de sortie,
ajouter `| tail -n 30` aux sorties longues lancées nues.

**Ce qui est lu**, dans `https://code.claude.com/docs/en/hooks.md`, ce jour.

- *Le champ `if`* (« Common fields », « How `if` patterns match Bash
  commands ») tient une seule règle de permission ; `Bash(cat *)` lance le
  script si une sous-commande de l'appel y répond, affectations de tête
  ôtées. Il est « best-effort » : une commande que Claude Code ne sait pas
  découper lance le script quand même.
- *« PreToolUse decision control »* : `permissionDecision: "deny"` refuse, et
  sa raison va au modèle ; `updatedInput` remplace l'entrée entière, que les
  règles de permission relisent ; `additionalContext` s'ajoute au résultat.
- *« Match Monitor commands »* : un hook au `matcher` `Bash` tourne aussi sur
  les commandes de l'outil Monitor, où il peut refuser, mais où
  `updatedInput` reste sans effet.
- *Le même gestionnaire*, déclaré deux fois, ne tourne qu'une fois : les deux
  déclarations portent donc deux commandes distinctes, `bash.py cat` et
  `bash.py queue`.

**Le premier comportement : le `cat` refusé.** `.claude/hooks/bash.py`,
déclaré sous `if: "Bash(cat *)"`, lit la commande par `shlex`, la découpe en
commandes simples, et refuse quand un `cat` écrirait à la session plus de
50 000 octets de fichiers texte. La règle et le seuil sont ceux de
`lecture.py`, qui les lui prête : `SEUIL`, `poids` (les octets d'un fichier
texte, depuis le dossier de la session), `refus`, `repondre`.

- *Vu* : le `cat` où qu'il soit dans une commande composée (`&&`, `||`, `;`,
  une ligne nouvelle, des parenthèses, `then`, `do`, la fin d'un tube), avec
  ses options, une affectation devant, un motif que le shell étend
  (`cat docs/*.md`), une lecture par `< fichier`.
- *Plusieurs fichiers se pèsent ensemble* : c'est ce que `cat` écrit qui
  entre dans le contexte. Deux fichiers de 30 000 octets sont refusés, ce que
  `Read` n'a pas à dire, qui n'en lit qu'un.
- *Laissé passer, à dessein* : le `cat` dont la sortie va à un tube, à un
  fichier (`>`, `>>`, `&>`), à une substitution (`$(…)`, `<(…)`) ; le texte
  d'un document en ligne ; ce qui est entre guillemets ; une commande que
  `shlex` ne sait pas lire.

**Ce que le hook ne voit toujours pas.**

- Les autres commandes qui lisent : `head -c`, `tail`, `sed` sans fenêtre,
  `less`, `nl`, `tac`, `awk`, un script. Un champ `if` ne tient qu'une règle :
  chacune voudrait sa déclaration.
- Le `cat` que le champ `if` ne reconnaît pas — `/bin/cat`, constaté —, ou
  que le script ne sait pas résoudre : un chemin tenu par une variable, des
  accolades (`{a,b}`), `xargs cat`, `find -exec cat`, `bash -c "cat …"`.
- Ce qui suit le premier document en ligne d'une commande : la lecture s'y
  arrête.
- Deux refus à tort, connus et rares : un groupe dont la sortie va à un tube,
  `(cat gros) | head` ; un fichier nommé d'un chiffre devant une redirection.

**Le second comportement : la queue d'un pytest nu.** Sous
`if: "Bash(python *)"`, le script récrit un `python -m pytest…` lancé nu en
`set -o pipefail; <commande> 2>&1 | tail -n 30`. Le motif est celui de
`https://code.claude.com/docs/en/costs.md` (« Offload processing to hooks and
skills ») : ni tube, ni redirection, ni `;`, `&`, `$`, accent grave, `#`. Une
session qui écrit son tube garde donc sa fenêtre.

- *Le code de sortie*, point à trancher : `pipefail` rend au tube le code de
  la commande, que `tail` aurait masqué. Un test le dit, par un pytest rouge
  de cent lignes, qui sort en 1 et n'en rend que trente ; et un pytest rouge,
  lancé nu dans cette session, a rendu « Exit code 1 ».
- *La session ne voit pas sa commande changée* : le hook le lui dit par
  `additionalContext`, une phrase à chaque réécriture.
- *Sans `permissionDecision`* : le hook récrit sans approuver, comme
  l'exemple de la page ; la commande récrite garde son contrôle de
  permission.
- *Ce qu'il ne récrit pas* : `python3` et `pytest` seul, que
  `Bash(python *)` ne lance pas, constaté pour `python3` ; une commande
  composée (`cd moteur; python -m pytest`) ; `node --test`.
- *`regenerer.py` et `resumer_temoins.py` restent à la consigne.* La session
  d'orchestration les demandait aussi ; la proposition que le propriétaire a
  approuvée dit « ajouter `| tail -n 30` à un `pytest` nu ». Les y joindre
  tient en une alternative du motif `LONGUE`, et se décide avec lui.

**L'accord pour les gardes**, relu à sa source. Ce commit touche
`.claude/settings.json` et deux hooks, `bash.py`, qui naît, et `lecture.py`,
remanié sans changer ce qu'il fait, pour prêter sa règle. Dans la session
d'orchestration, la proposition, le 14 novembre 2026 à 18 h 41 UTC : « Un
hook `PreToolUse` sur Bash. Le champ `if` (`"Bash(cat *)"`) ne lance le hook
que sur les commandes visées : il fermerait le trou que `CLAUDE.md` signale,
le `cat` que `lecture.py` ne voit pas. Le même hook peut récrire la commande
(`updatedInput`) pour ajouter `| tail -n 30` à un `pytest` nu », suivie de
« Les pistes 1, 2 et 5 touchent des gardes (hooks et réglages), donc il leur
faut ton accord et la ligne `Garde-modifiée` ». Le propriétaire, à 18 h 46 :
« Faisons 1 et 2 dans un session pour chaque ».

**Ce qui a agi en vrai, dans cette session.** `.claude/settings.json` se
recharge en cours de session : les deux déclarations ont agi dès l'écriture
du fichier, sans redémarrage. Constaté : `false && cat
docs/feuille_de_route.md` refusé, avec la raison (558 723 octets) ;
`cat docs/feuille_de_route.md | wc -c` et le `cat` d'un petit fichier
passés ; `python -m pytest tests/test_hook_bash.py -v` rendu en trente
lignes, avec la phrase du hook ; le code de sortie 1 d'un pytest rouge ; la
réécriture d'une commande précédée d'une affectation. Le script répond en
24 ms.

**Ce qui reste à constater**, par la session suivante : que le hook est là
dès l'ouverture d'une session neuve ; qu'il tourne dans un agent
(l'éclaireur) ; sur un poste, en mode de permission par défaut, si la
commande récrite, qui commence par `set -o pipefail`, fait naître une
demande de permission que `python -m pytest` seul n'appelait pas ; ce que
rend un refus sur une commande de Monitor.

**Les tests** : `tests/test_hook_bash.py`, au niveau rapide, à côté de
`tests/test_hook_lecture.py`, qui reste vert sur `lecture.py` remanié.
