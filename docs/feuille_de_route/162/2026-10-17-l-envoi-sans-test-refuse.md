# Le test d'abord : l'envoi sans test refusé

**Le 17 octobre 2026, la demande.** Le propriétaire, l'étape 1 publiée, sans
attendre la mesure qu'elle prévoyait : « durcis le hook : refuser l'envoi sans
test dans pousser.sh ».

**Ce que `pousser.sh` refuse.** Un commit qui change le code — les chemins du
hook : les `.py` de `src/`, les `.js` et `.mjs` de `moteur/`, les `.py`, `.sh`
et `.mjs` de `scripts/`, les `.py` et `.sh` de `.claude/hooks/` — sans toucher
à aucun fichier de `tests/` hors des fabriqués (`-merge`), et dont le message
ne porte pas de ligne `Sans-test: <raison>`, la raison non vide. Le refus suit
celui des adresses nominatives, sur les commits à publier, déjà rebasés sur
`origin/main`. Rien n'est poussé ; le message nomme chaque commit refusé et
dit comment le reprendre : le test joint au dernier commit, par
`git commit --amend --no-edit` ; plusieurs commits réunis en un, par
`git reset --soft "$(git merge-base origin/main HEAD)"` ; ou la déclaration,
par `git commit --amend --no-edit --trailer "Sans-test: <raison>"`.

**Trois choix.**

- *Commit par commit, et non envoi par envoi.* La règle veut le test et le
  code dans le même commit ; jugé en bloc, un envoi qui porterait le code dans
  un commit et un test sans rapport dans un autre passerait.
- *Une déclaration plutôt qu'un refus sans recours.* Un remaniement, un
  commentaire, un message ne changent aucun comportement et n'ont pas de test
  neuf à porter ; les refuser sans recours pousserait au test factice. La
  ligne `Sans-test: <raison>` est un trailer git, que `git commit --trailer`
  écrit à côté de `Co-Authored-By` ; elle se reconnaît aussi ailleurs dans le
  message. La raison reste dans l'historique, où l'étape 2 la relira.
- *Un seul exemplaire de ce qui est du code.* `pousser.sh` demande les commits
  à refuser à `.claude/hooks/tdd.py` (`--envoi origin/main..HEAD`), qui tient
  la liste du code et la règle des fabriqués pour les deux gardes : un
  `git log` et un `git check-attr` pour tout l'envoi, quand un git coûte près
  d'une seconde sous Windows. Sans Python, le script ne vérifie rien, comme il
  se passe déjà de ses pilotes de fusion ; une erreur de git laisse passer.
  `tests/conftest.py` compte désormais le hook parmi ce que lit
  `test_pousser.py`, dont les réussites se gardent sous l'empreinte de ce
  qu'il lit.

**Ce qui a été vérifié, dans l'ordre du cycle.** Les tests d'abord, vus
rouges pour la raison attendue : la raison du hook, qui ne nommait ni la
déclaration ni `pousser.sh` ; `commits_sans_test`, absent ; `--envoi`,
inconnu ; `pousser.sh`, qui publiait un commit de `src/` sans test. Les deux
cas qui doivent partir, le code avec son test et le code déclaré, passaient
déjà, et passent toujours : ils gardent la garde de refuser à tort. Puis le
code : soixante-trois verts, `test_niveaux.py` compris. Sur un atelier
jetable, le refus nomme le commit, et le même commit, déclaré par
`--trailer`, part.

**Les limites.** La déclaration se croit sur parole : une session peut
déclarer sans test ce qui change un comportement, et c'est l'étape 2 qui
relit les raisons. Un envoi à la main (`git push origin HEAD:main`, la
recette de `CLAUDE.md`) passe outre, comme aux autres refus du script. Un
commit de fusion ne montre aucun fichier, et passe. Un test sans rapport avec
le code passe aussi : la garde voit les fichiers, pas leur sens.

**Ce qui reste** : l'étape 2, après une semaine de sessions (feuille de
route).
