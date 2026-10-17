# Le test d'abord, étape 1 : la règle et sa garde

**Le 17 octobre 2026, la demande.** Le propriétaire : « Sur ce dépôt, je
veux utiliser le TDD : Test driven development. » Rien dans les consignes ne
disait jusque-là quand le test s'écrit, avant ou après le code ; la veille du
droit faisait entrer l'exemple publié dans `exemples_officiels.yaml`, sans
dire à quel moment.

**Ce que le TDD devient ici.** Le cycle classique — le test, vu rouge ; le
code le plus court qui le fait passer ; le remaniement, sous des tests
verts —, avec quatre précisions propres au dépôt, écrites dans `CLAUDE.md`
(« Travailler », et une ligne des listes de contrôle) et dans les consignes
des trois zones.

- *La valeur attendue vient de la source.* Une règle du scénario 1 se teste
  par l'exemple publié de la caisse, ou, à défaut, par un cas posé à la main
  depuis le texte ; jamais par ce que rend le code, qui ferait passer le test
  par construction. `docs/veille_droit.md` le dit à son étape 3 : l'exemple
  entre avant la moindre ligne du code, et se voit échouer.
- *Un témoin n'est pas le test d'abord.* Refaits par les scripts, les
  témoins disent ce qu'un changement déplace, non ce qu'il devait déplacer.
- *On commite au vert, test et code ensemble.* Le hook `Stop` publie sur
  `main` à chaque fin de tour, et GitHub y joue la suite complète : un test
  rouge commité seul mettrait toutes les sessions à le réparer. Le rouge vit
  dans le dossier de travail, le temps d'un cycle.
- *Le portage suit.* Une étape qui a son jumeau JavaScript, une fois le
  Python au vert, voit d'abord rouge le cas qui confronte les deux moteurs.

**La garde.** Une règle de `CLAUDE.md` se lit à l'ouverture de chaque
session, mais rien ne la rappelle au moment d'agir : c'est ce que font les
garde-fous mécaniques du dépôt, comme le hook de lecture (action 135).
`.claude/hooks/tdd.py`, déclaré sous `PreToolUse` pour `Edit` et `Write`,
refuse une fois par commit et par session la première retouche du code — les
`.py` de `src/`, les `.js` et `.mjs` de `moteur/`, les `.py`, `.sh` et `.mjs`
de `scripts/`, les `.py` et `.sh` de `.claude/hooks/` — tant qu'aucun test
n'a été vu échouer depuis le dernier commit. C'est pytest qui le voit :
`tests/conftest.py`, au bout d'une séance qui a échoué, note le commit dans
`.cache/tdd/rouge` si un fichier de `tests/` a changé dans le dossier de
travail, hors des fabriqués, que `.gitattributes` marque `-merge`. Trois
choix, et ce qu'ils écartent :

- *Le rouge vu, et non un test modifié.* Un fichier de tests modifié ne
  prouve pas qu'on a vu le test échouer, l'étape que le TDD perd le plus
  souvent ; une séance de pytest qui échoue pendant qu'il s'écrit, si. Un
  témoin régénéré ne compte pas.
- *Un refus, une seule fois.* Un rappel qui laisse passer arrive après la
  retouche, trop tard pour un test qui devait la précéder ; un refus à chaque
  fois pousserait à tromper la garde par un test factice. Refaite telle
  quelle, la retouche passe : un remaniement, un commentaire, un message
  n'ont pas de test neuf.
- *Par commit.* Le commit clôt le cycle ; le suivant commence par un nouveau
  rouge.

Une session qui suit le cycle ne rencontre jamais le hook ; celle qui
l'oublie le rencontre une fois par commit.

**Ce qui a été vérifié, dans l'ordre du cycle.** Les tests d'abord :
`tests/test_hook_tdd.py`, vingt-cinq cas, lancés sans le hook, rouges à
l'import (`ModuleNotFoundError`), puis contre une coquille vide : quatorze
rouges sur leur assertion, et onze verts, ceux qui gardent ce qui doit
passer — un test, la prose, une donnée, le style, un fichier hors du dépôt,
un autre outil, les entrées illisibles — et le dernier, sur le dépôt réel,
que la coquille vide satisfait trivialement. Puis le hook et la séance de
pytest qui le renseigne : vingt-cinq verts, en une demi-seconde. De bout en
bout dans le dépôt : la retouche d'un module de `src/` refusée ; une séance
de pytest qui échoue, en série puis sous xdist, note le commit ; la retouche
passe ensuite.

**Les limites.** Un rouge vu hors de pytest (`node --test`) n'est pas noté :
la retouche se refait, une fois. Les marques sont sous le `.cache/` du
dossier de travail, une par worktree ; le rappel ne garde que la dernière
session, et deux sessions dans le même dossier se le rappellent tour à tour.
`pousser.sh`, qui rattrape `main` à chaque fin de tour, change `HEAD` quand
une autre session a poussé : un cycle à cheval sur deux tours peut alors
revoir le rappel. Le fichier de tests est rangé parmi les contrôles, avec
celui du hook de lecture : la suite rapide ne le joue pas.

**Ce qui reste** : l'étape 2, la mesure, après une semaine de sessions, et
la décision du propriétaire sur la force de la garde (feuille de route).
