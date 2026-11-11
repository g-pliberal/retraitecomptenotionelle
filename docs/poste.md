# Sur un poste

Ce qu'un clone demande sur un poste, et qu'une session web, qui part d'un
clone neuf, n'a pas à faire. Les règles de git qui valent partout sont dans
`CLAUDE.md`, qui renvoie ici.

- **L'identité git du clone** : aucune adresse nominative dans un commit
  (`CLAUDE.md`). Sur un poste, dans chaque clone :
  `git config user.name "g-pliberal"` et
  `git config user.email "240225789+g-pliberal@users.noreply.github.com"`.
- **Un clone d'avant le 26 septembre 2026** ne suit plus `main` : l'historique
  a été réécrit le 23 septembre, pour en retirer des adresses nominatives,
  puis le 26, pour en retirer un document que sa licence interdit de
  republier. Sans rien de non publié, le remplacer par un clone neuf ; sinon,
  reporter ses commits, puis publier : `git fetch origin main`,
  `git rebase --onto origin/main "$(git merge-base --fork-point origin/main HEAD)"`,
  `bash scripts/pousser.sh`.
- **Les branches `claude/*` se suppriment à la main**, depuis l'onglet
  Branches de GitHub : le jeton d'une session répond 403.
