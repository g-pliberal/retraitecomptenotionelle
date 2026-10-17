# Le site en ligne au vert

**Le 17 octobre 2026, la demande.** Le propriétaire soumet à une session
l'article d'Anthropic sur la revue de code (« How the Claude Code team does
code review », blog claude.dev, 15 octobre 2026) : « Est-ce que c'est utile
pour notre projet ? ». La session en tire six pratiques, et propose de
commencer par deux, la mise en ligne au vert, puis le classement des rouges.
Le propriétaire : « vas-y ».

**Ce qui se passait.** GitHub Pages publiait `main` à chaque poussée. Les
déploiements de l'environnement `github-pages`, lus le 17 octobre, alternent
ceux des envois de session (`g-pliberal`) et ceux des commits du robot
(`github-pages[bot]`), tous réussis : un envoi partait en ligne avant que la
suite l'ait passé, et un verdict rouge y restait, sans les fichiers
fabriqués, que le robot ne commite que sur une suite verte. Du 6 au
17 octobre, la recherche des commits de `main` compte 25 verdicts rouges du
robot (« Suite ROUGE sur ») pour 143 verts (« suite verte sur »).

**Ce qui change.** `scripts/publier_fabrique.sh` écrit `en_ligne=oui` dans
`GITHUB_OUTPUT` quand il a poussé le verdict d'une suite verte sur `main` ;
ni une suite rouge, ni une course lancée à la main sur une autre branche, ni
une course que `main` a dépassée ne l'écrivent. `tests.yml` demande alors à
l'API de Pages sa source : `workflow`, il archive l'arbre du commit publié
(`git archive HEAD`, non le répertoire de la course et ses caches), le
téléverse (`actions/upload-pages-artifact@v5`), et le job `en_ligne` le
déploie (`actions/deploy-pages@v5`) ; une autre réponse, ou aucune, et rien
ne part, sans que la course rougisse. Le job passe `!cancelled()` : une garde
des présomptions rouge rend la course rouge, mais la suite est verte.

**Pourquoi un job, et non une branche.** La documentation de GitHub dit
qu'une poussée du jeton du workflow ne déclenche pas de construction de
Pages ; les déploiements lus le 17 octobre montrent le contraire. Une branche
que le robot avancerait reposerait sur ce comportement contredit ; le job
déploie lui-même, par la voie que GitHub documente.

**Ce qui n'est pas fait.** Le retour arrière en un geste : il faudrait forcer
une branche, ou garder les archives au-delà du jour que leur donne
`upload-pages-artifact`, et la course verte suivante remettrait en ligne
l'état fautif tant que `main` le porte. Revenir en arrière reste rétablir
`main`.

**Ce que le propriétaire fait.** Settings → Pages → Build and deployment →
Source : « GitHub Actions ». Avant, Pages continue de publier chaque envoi ;
après, seul le job `en_ligne` publie, à la première course verte. Le
déploiement lui-même ne se joue que sur GitHub : à vérifier sur cette course,
dans l'onglet Actions et l'environnement `github-pages`.

**Vérifié.** `tests/test_outillage.py` : le script et ses quatre cas, joués
dans un dépôt jetable ; l'enchaînement de `tests.yml` ; l'étape qui lit la
source de Pages, jouée sous le shell de GitHub, `gh` remplacé par sa réponse.
Puis `python -m pytest -m rapide`.
