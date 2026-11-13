# Conventions du dépôt

Modèle de retraite français en comptes notionnels, appliqué rétroactivement ;
le livrable est le site statique (`README.md`). L'architecture est dans
`docs/architecture.md` ; où en est le dépôt, et ce qui reste à faire, dans le
tableau de bord `docs/etat.md`, que `python scripts/tableau_de_bord.py`
fabrique ; les chantiers ouverts, dans `docs/feuille_de_route.md` : une
session qui cherche quoi faire n'y lit que le bloc « Reprise » qui ouvre
chacune de ses actions `en cours` (`python scripts/reprise.py`), et note ce
qu'elle a fait dans un fichier à elle, sous `docs/feuille_de_route/`. Ce
fichier ne garde que les règles : l'histoire de chacune, et l'incident qui
l'a fait naître, sont dans `docs/archives/conventions.md`.

## Git : tout va sur `main`

**On publie sur `main`, toujours, sans pull request**, par
`bash scripts/pousser.sh`, qu'un hook `Stop` (`.claude/settings.json`) lance
aussi à chaque fin de tour. Cette règle prime sur la branche `claude/…`
qu'une session Claude Code se voit assigner : elle y travaille, mais elle
pousse sur `main`, et ne finit jamais en laissant son travail sur la branche.

Le script rattrape `origin/main` en avance rapide, rebase au besoin les
commits de la session qu'une autre session a devancés, pousse `HEAD` sur
`main`, puis fait suivre la branche de la session. Il refuse, sans rien
pousser : un conflit sur une source, plus de vingt commits d'écart, des modifications non
commitées quand il doit rebaser, aucun ancêtre commun avec `main` (le cas
grave), un commit signé d'une adresse nominative, un commit qui change le
code sans toucher aux tests, s'il ne le déclare pas (« Le test d'abord »),
une feuille de route dont le bloc « Reprise » ou les notes enfreignent leurs
règles, quand un commit à publier la touche, un commit qui touche une garde —
les workflows de GitHub, les hooks et leurs réglages, `pousser.sh`,
`publier_fabrique.sh`, `publier_inscription.sh` — sans ligne
`Garde-modifiée: <raison>`, qu'une session n'écrit qu'avec l'accord du
propriétaire, demandé avant (action 163). En avance sur `main`, il pousse
tout ce qui est commité, même si d'autres modifications attendent :
ne commiter qu'une fois ses tests passés, puisque le hook publie à chaque fin
de tour. À la main, la recette reste
`git fetch origin`, `git merge --ff-only origin/main`,
`git push origin HEAD:main` ; si l'avance rapide est refusée, la session a
divergé, et il faut comprendre pourquoi avant d'insister.

- **Ne jamais faire `git checkout main`, ni se fier au `main` local** : il
  date du clone. Ne comptent que `origin/main` et `HEAD`.
- **Ne jamais forcer une poussée sur `main`**, même pour « réparer ».
- **Aucune adresse nominative dans un commit** : auteur et committer en
  `noreply` (Anthropic, GitHub).
- **Un message de commit de cinq lignes au plus sous son titre**, le détail
  allant à la feuille de route.
- **Sur un poste**, et non dans une session web, qui part d'un clone neuf :
  lire d'abord `docs/poste.md` — l'identité git du clone, le clone d'avant le
  26 septembre 2026, qui est le cas grave de `pousser.sh`, les branches
  `claude/*` à supprimer.
- **Le compteur de commits « non poussés » est faux** : relancer le script,
  et ne rien écrire là-dessus, une ligne au plus.

**Plusieurs sessions en parallèle**, chacune dans son conteneur, se partagent
le dépôt par zones : une sur le modèle et son portage, une sur les données et
la certification, une sur le site — jamais deux sur les pages en même temps.
Commiter petit, pousser souvent. Chaque session écrit ses journaux dans des
fichiers à elle (action 148), au dernier commit, juste avant de pousser : sa
note de feuille de route,
`docs/feuille_de_route/<action>/<AAAA-MM-JJ>-<sujet>.md`, et son
entrée du journal de veille,
`data/reference/legislation/journal_de_veille/<AAAA-MM-JJ>-<sujet>.yaml`.
Deux sessions sur deux étapes d'une même action n'écrivent ainsi dans aucun
journal commun.

**Les fichiers fabriqués et la suite complète sont à GitHub** (action 148).
À chaque envoi sur `main`, `tests.yml` repart du dernier `main`, lance
`regenerer.py` puis la suite complète, et commite sous `github-actions[bot]`
les fichiers refaits, chiffres ancrés et blocs produits de la prose compris,
et le verdict, `.github/etat_suite.yaml`, que le hook `SessionStart` affiche
à l'ouverture : une suite rouge se répare avant tout. Une session lance
`python -m pytest -m rapide` et les fichiers de tests de sa zone avant chaque
envoi, pas la suite complète ; elle peut régénérer pour voir ce que son
changement déplace, sans y être tenue, pas plus qu'à récrire les chiffres
ancrés qu'il déplace. `pousser.sh` règle seul, au rebasage, ce que les scripts
écrivent ; un conflit sur ce qui s'écrit à la main reste à résoudre. Jamais
`git checkout --theirs` sur un fichier de prose : il reprend le fichier
entier d'un côté, et efface ce que l'autre session y a écrit.

## Économiser le contexte

Chaque appel d'outil relit toute la conversation : ce qu'une session a lu,
elle le repaie à chaque geste suivant, et elle coûte d'autant plus cher
qu'elle dure. D'où sept règles.

- **Une session, une étape.** L'étape poussée sur `main`, la session s'arrête
  et le dit au propriétaire ; l'étape suivante s'ouvre dans une session neuve.
- **La session d'orchestration passe la main à chaque vague** : celle qui
  lance et suit les autres sessions charge le skill `orchestration` avant d'en
  lancer une.
- **Au démarrage, le bloc « Reprise » seul.** Chaque action `en cours` de la
  feuille de route s'ouvre, sous son titre, sur un paragraphe
  `**Reprise, au <date>.**` de 150 mots au plus, en lignes de largeur
  ordinaire : où elle en est, ce qui reste, par quoi commencer, et la note à
  lire pour le détail ; `python scripts/reprise.py` les imprime tous, sans les
  notes, et `reprise.py 138` ceux d'une action, avec la liste de ses notes. La
  session qui avance l'action le récrit, daté du jour, au commit de sa note.
- **Chercher avant de lire.** L'outil Grep d'abord, qui omet les lignes
  géantes et passe ce que `.ignore` nomme (`grep -n` par Bash, seulement sur
  un fichier sans ligne démesurée), puis la seule fenêtre utile (`Read` avec
  `offset` et `limit`, ou `sed -n`). Un fichier texte de plus de 50 000
  octets ne se lit jamais en entier, ni par `Read`, que le hook
  `.claude/hooks/lecture.py` refuse alors sans `limit`, ni par `cat`, qu'il
  ne voit pas ; les témoins de `tests/temoins/`, par `resumer_temoins.py` ou
  une requête ciblée.
- **Ce dont seule la conclusion compte, l'éclaireur le lit.** Une recherche
  de plusieurs lectures dont la session ne veut que la réponse — où une
  règle, un chiffre ou un test se trouve, ce que la feuille de route, ses
  notes et les fiches renvoient à une action — se confie, une à la fois, à
  l'agent `eclaireur` (`.claude/agents/eclaireur.md`). Il tourne sur Haiku,
  dont le jeton coûte bien moins que celui d'Opus, dans un contexte à lui :
  ce qu'il lit n'entre pas dans celui de la session, que chaque appel relit.
  Il rend des `fichier:ligne` et des citations exactes ; ce que la session
  modifie ou cite, elle le relit elle-même, à la fenêtre qu'il désigne.
- **Les sorties longues passent par `tail` ou `grep`** :
  `python -m pytest 2>&1 | tail -n 30`, de même pour `regenerer.py` et
  `resumer_temoins.py` ; jamais de `git diff` ni de `git show` entier sur un
  témoin ou sur `pages.js`.
- **L'enquête à la mesure de la question.** Une question appelle la
  vérification qui y répond, pas davantage ; une recherche en éventail,
  plusieurs agents en parallèle, ne se lance qu'à la demande du propriétaire.

## Travailler

- **Les consignes d'une zone sont dans son dossier** : `src/CLAUDE.md`, le
  modèle ; `moteur/CLAUDE.md`, son portage et le site ; `data/CLAUDE.md`, les
  données et la proposition. Celles qui tiennent à des fichiers épars sont des
  règles de `.claude/rules/` : `prose.md`, les documents, leurs chiffres et
  leur conservation ; `documentation.md`, la feuille de route, ses notes,
  l'architecture et les limites ; `tests.md`, la suite. Claude Code charge
  chacune à la première lecture ou écriture d'un fichier de sa zone, avec ses
  listes de contrôle. Un Grep, une commande composée, un script ne la chargent
  pas : qui ne travaille que par eux la lit d'abord.
- **Mise en route** : `pip install -e '.[dev]'`. Sans lui, `python -m pytest`
  ne trouve ni pytest ni le paquet. Une session web n'a pas à le lancer : le
  hook `SessionStart` (`.claude/hooks/session-start.sh`, action 33 de la
  feuille de route, archivée) l'installe en arrière-plan à son ouverture,
  avec un PyYAML qui embarque libyaml. Un « No module named pytest » dans les
  premières secondes veut dire qu'il n'a pas fini : relancer un peu plus tard,
  sans réinstaller. Sur un poste, la commande reste à lancer une fois.
- **Le test d'abord** (TDD, action 162) : tout changement de comportement —
  une règle du modèle, son portage, le site, la saisie, un script, un hook —
  commence par le test qui le dit, lancé seul et vu échouer pour la raison
  attendue ; puis vient le code le plus court qui le fait passer, puis le
  remaniement, sous des tests verts. Un défaut se corrige de même, par le
  test qui le reproduit. La valeur attendue vient de la source — l'exemple
  publié, le texte, un calcul posé à la main —, jamais de ce que rend le
  code ; un témoin refait par un script n'en tient pas lieu : il dit ce qui a
  bougé, non ce qui devait bouger. Test et code se commitent ensemble, au
  vert : un test rouge sur `main` mettrait toutes les sessions à le réparer.
  Un remaniement garde verts les tests qui sont là, sans en ajouter.
- **Les tests** : `python -m pytest -m rapide` en travaillant, les règles et
  les étapes, sous deux minutes ; `python -m pytest -m site` après une
  retouche du site ou de la saisie, en une minute ; `python -m pytest`, la
  suite complète, c'est GitHub qui la lance après chaque envoi (voir « Les
  fichiers fabriqués et la suite complète sont à GitHub »).
- **Les dépendances** : PyYAML seul hors bibliothèque standard ; le portage
  JavaScript n'en a aucune ; pytest et pytest-xdist ne servent qu'aux tests,
  et xlrd qu'aux récupérateurs qui lisent un classeur `.xls` (action 176),
  tous trois dans `.[dev]`.
  Node, qui fait tourner le portage, sert aussi au Python qui lit le site :
  les tests des pages, les témoins, la prose et le paquet.

## Listes de contrôle

- **Au début d'une étape** : lire le bloc « Reprise » de son action, et celui
  de son étape s'il en a un (`python scripts/reprise.py <action>`), puis
  relever, par l'éclaireur ou par `grep -n` de son numéro ou de son domaine,
  ce que la feuille de route, ses notes et les fiches lui renvoient, avant
  d'écrire la moindre ligne.
- **Pour chaque comportement** : le test, vu rouge ; le code, jusqu'au vert ;
  le remaniement ; `python -m pytest -m rapide` et les tests de sa zone ; le
  commit, test et code ensemble.
- **Les autres listes** sont aux consignes des dossiers : une retouche de
  `moteur/js/pages.js` et un champ de saisie de plus, dans
  `moteur/CLAUDE.md` ; un changement du modèle, dans `src/CLAUDE.md`.

## Le scénario 1 est le droit applicable, et rien d'autre

Le scénario 1 est l'étalon : le droit EN VIGUEUR à la date d'effet de la
pension, tel que la caisse l'applique. Une session qui y touche commence par
`python scripts/veille_droit.py` et suit `docs/veille_droit.md` : ce qu'elle
lit avant d'écrire une règle, ce qu'elle en écrit, ce qu'elle consigne au
journal de veille en finissant. On y cherche dans le JORF et LEGI par l'index
de la DILA, sans jamais retélécharger les dumps.

Une étape qui écrit ou change une règle du scénario 1 se mène sur Fable 5.2,
que le dépôt règle à l'effort `high`. Ouverte sur un autre modèle, la session
le dit au propriétaire dès son début, qui bascule par `/model fable` tant que
le contexte est court : chaque modèle a son cache, et une bascule le réécrit
en entier. Si elle confie l'écriture d'une telle règle à un agent, elle lui
passe `model: fable` : l'agent généraliste tourne sur Sonnet.
