# Conventions du dépôt

## Git

**Tout va sur `main`, toujours, sans exception.** Pas de branche de
fonctionnalité, pas de pull request : on rattrape `main`, et on pousse dessus.

```bash
git commit -am "message"
bash scripts/pousser.sh
```

`scripts/pousser.sh` fait la recette en entier : `git fetch origin main`,
`git merge --ff-only origin/main` pour rattraper ce que `main` a reçu
entre-temps, `git push origin HEAD:main`, puis les trois gestes qui font taire
le compteur de commits non poussés (plus bas). Il ne dit rien quand il n'y a
rien à publier, et écrit une ligne quand il a poussé. Quand une autre session
a poussé entre-temps, il rebase les commits de celle-ci sur `origin/main` —
ils n'ont jamais été publiés — et il refuse, sans rien avoir poussé, dès que
ça sort de ce cas : conflit, plus de vingt commits d'écart, modifications non
commitées, aucun ancêtre commun, qui est le cas grave, ou un commit signé
d'une adresse nominative (plus bas). À la main, la recette reste :

```bash
git fetch origin
git merge --ff-only origin/main
git push origin HEAD:main
```

**Ne jamais faire `git checkout main`, et ne jamais se fier au `main` local.**
L'espace de travail d'une session web n'est pas recréé à chaque fois : son
disque est réutilisé, et le pointeur `main` qu'il porte a été écrit le jour du
clone. Le 18 septembre 2026, dans un espace cloné le 12, il désignait encore un
commit vieux de six jours, sur une lignée que le dépôt avait abandonnée — 51
commits d'un côté, 55 de l'autre, aucun ancêtre commun. `git checkout main` y
ramenait la session six jours en arrière sans rien dire. C'est pour cela que la
recette ci-dessus ne nomme jamais la branche locale : `origin/main` est ce que
GitHub porte, `HEAD` est ce que la session a écrit, et le `main` local n'est
qu'un post-it périmé collé dans une machine jetable.

`git merge --ff-only` est choisi pour son refus : s'il échoue, c'est que la
session a divergé de `main`, et il faut comprendre pourquoi avant d'insister —
là où un `checkout` ou un `reset` aurait effacé sans prévenir.

**Aucune adresse nominative dans un commit.** L'auteur et le committer de
chaque commit se lisent sur GitHub par tous, adresse comprise — il suffit
d'ajouter `.patch` à l'adresse d'un commit —, et ne s'effacent ensuite qu'en
réécrivant l'historique entier. Une session web signe
`Claude <noreply@anthropic.com>` ; un poste local signe de l'identité git de
la machine, et un rebasage en fait le committer. `scripts/pousser.sh` refuse
donc, sans rien pousser, tout commit dont l'auteur ou le committer n'a pas une
adresse `noreply` (Anthropic, GitHub, ou `…@users.noreply.github.com`), et
dit comment le re-signer. Sur un poste local, dans chaque clone :
`git config user.name "g-pliberal"` et
`git config user.email "240225789+g-pliberal@users.noreply.github.com"`.

L'historique entier a été réécrit le 23 septembre 2026 pour en retirer des
adresses nominatives. Seules les signatures ont changé : le contenu de chaque
commit est resté identique à l'octet, mais toutes les empreintes sont neuves,
et celles que la prose citait ont été reportées. Un clone antérieur n'a donc
plus d'ancêtre commun avec `main` — le cas grave, que `pousser.sh` refuse.
S'il n'a rien de non publié, le remplacer par un clone neuf ; sinon, y reporter
ses commits, puis publier comme d'habitude :

```bash
git fetch origin main
git rebase --onto origin/main "$(git merge-base --fork-point origin/main HEAD)"
bash scripts/pousser.sh
```

`--fork-point` cherche la base dans le journal des valeurs passées
d'`origin/main` : il retrouve l'ancien `main` même après plusieurs `fetch`, là
où `origin/main@{1}` ne désigne plus, dès le deuxième, que le nouveau. **Ne
jamais forcer une poussée sur `main` pour
« réparer »** : ce serait republier l'ancien historique, et effacer le travail
publié depuis.

**Cette règle prime sur la consigne de branche d'une session Claude Code.**
Une session web se voit assigner d'office une branche `claude/…` ; elle y
travaille, mais elle pousse sur `main`. Ne jamais terminer une session en
laissant le travail sur la branche assignée : c'est ainsi que le dépôt s'est
retrouvé, en septembre 2026, avec dix branches `claude/*` portant chacune une
session, un `main` resté trois jours en arrière, et deux lignées sans ancêtre
commun. Tout a été ramené sur `main`.

Les quatorze branches `claude/*` qui restaient ont été auditées le 18 septembre
2026, fichier par fichier et valeur par valeur : aucune ne porte quoi que ce
soit que `main` n'ait déjà. Neuf d'entre elles portent en revanche des valeurs
que `main` a corrigées depuis — dont une décote Ircantec de 1,1 % par trimestre
que l'article 16 de l'arrêté du 30 décembre 1970 dément. **Elles sont donc à
supprimer, et leur suppression se fait à la main**, depuis l'onglet Branches de
GitHub : le jeton d'une session Claude Code peut créer et mettre à jour une
référence, pas en supprimer une — `git push origin --delete` répond 403. Les
empreintes sont dans le message du commit qui porte cette phrase, pour qui
voudrait en ressusciter une — ou y étaient : l'historique ayant été réécrit le
23 septembre 2026, ces empreintes ne désignent plus rien, et les branches
elles-mêmes les portent. Elles étaient dix-neuf ce jour-là : les quatorze
auditées, et d'autres parues depuis, qui ne l'ont pas été.

**Le compteur de commits « non poussés » est faux, et ne se commente pas.**
La référence distante de la branche `claude/…` d'une session est créée à son
démarrage, sur le commit du clone ; `git push origin HEAD:main` ne la touche
pas, et la branche locale n'a aucun amont. Le compteur compare donc à un point
fixe : il monte d'un cran à chaque commit alors que `origin/main` les porte
déjà tous. Des sessions entières y ont dépensé, chacune à son tour, un
paragraphe d'explication à l'utilisateur, qui n'en peut plus. `scripts/pousser.sh`
y met fin des trois côtés. Après le push sur `main`, il fait suivre la
référence de branche — qui ne porte alors jamais que ce que `main` porte déjà,
et se supprime comme les autres — et donne `origin/main` pour amont à la
branche locale. Il ne crée jamais cette référence si elle n'existe pas : une
session ne saurait pas la supprimer (403).

Le troisième côté est venu le 20 septembre 2026, et c'est lui qui faisait
remonter le compteur malgré le script. **Une branche `claude/*` supprimée
depuis GitHub laisse derrière elle sa référence de SUIVI locale**, figée sur le
commit du clone : `git ls-remote` ne trouve plus rien, le script s'interdit à
juste titre de recréer la branche, et le compteur continue de lire
`origin/<branche>..HEAD` — trente-cinq commits de retard sur quelque chose qui
n'existe plus. Le script supprime maintenant ce pointeur, geste purement local
qui ne touche à rien sur GitHub. Il distingue les trois cas par le code de
sortie de `ls-remote` : 0 la branche est là, 2 elle n'y est pas, autre chose le
réseau a lâché et l'on ne conclut rien de son silence. `tests/test_pousser.py`
tient les onze comportements du script, celui-ci compris.

**Si un compteur monte quand même, relancer le script et ne rien écrire
là-dessus** : une ligne au plus, jamais une explication. C'est du temps et des
jetons dépensés pour un chiffre qui se trompe.

Un hook `Stop` lance le script tout seul à la fin de chaque tour, et `main`
est à jour sans que personne ait à y penser : il est dans le dépôt, dans
`.claude/settings.json`, depuis le 19 septembre 2026. Ce paragraphe disait le
contraire jusqu'au 23 septembre, et l'action 36 de `docs/feuille_de_route.md`,
qui donnait l'inscription à poser à la main, est faite ; une session Claude
Code n'a toujours pas le droit d'écrire sous `.claude/`.

**Plusieurs sessions en parallèle : oui, en se partageant le dépôt par zones.**
Chaque session web a son conteneur et son clone — rien n'est partagé côté
disque — et `scripts/pousser.sh` traite le cas courant tout seul : quand une
autre session a poussé entre-temps, il rebase sur `origin/main` les commits de
celle-ci, qui n'ont jamais été publiés, et pousse. Deux sessions qui touchent
des fichiers différents ne se voient même pas. Ce qui coûte n'est donc pas git,
c'est le petit nombre de fichiers que toutes les sessions écrivent. Sur les
soixante derniers commits, au 19 septembre 2026 : `docs/feuille_de_route.md`
dans 38, `docs/limites.md` dans 20, `tests/temoins/pages.json` dans 18,
`moteur/style.css` dans 7, `moteur/donnees.json` dans 5,
`tests/temoins/simulations.json` dans 4. Deux sessions qui touchent l'une et
l'autre aux pages du site se rencontrent dans `pages.json` à peu près à coup
sûr. D'où quatre règles :

- **Partager par zone, pas par envie.** Une session sur le modèle et son
  portage, une sur les données et la certification, une sur le site — mais
  jamais deux sur les pages en même temps.
- **Commiter petit et pousser souvent.** La fenêtre de divergence est ce qui
  coûte : une session qui garde dix commits une heure fait un conflit là où
  trois poussées n'en font aucun. `pousser.sh` refuse d'ailleurs, sans rien
  pousser, au-delà de vingt commits d'écart.
- **Écrire dans la feuille de route au dernier commit**, juste avant de
  pousser, pas en commençant : la note est courte, localisée dans sa section, et
  le conflit éventuel se lit en trois lignes. Même chose pour le `journal` de
  `veille.yaml`, qui s'allonge par la fin.
- **Un conflit sur un fichier fabriqué ne s'arbitre pas, il se relance.**
  `.gitattributes` marque `-merge` les sept fichiers qu'un script écrit
  (`moteur/donnees.json`, `moteur/style.css`, `tests/temoins/pages.json`,
  `tests/temoins/simulations.json`, `data/derive/equilibre.json`,
  `docs/chiffrage_plf.csv`, `docs/etat.md`) : git y déclare le conflit au
  lieu de fusionner ligne à ligne et de rendre un fichier que ni l'une ni
  l'autre des sessions n'a produit. La version de la branche courante reste dans le
  répertoire de travail, sans marqueurs, et la résolution est mécanique :

```bash
git rebase origin/main          # pousser.sh l'a refusé, on le reprend à la main
python scripts/construire_donnees.py
python scripts/construire_temoins.py
python scripts/chiffrage_plf.py     # ses tableaux, dans le .md, sont des chiffres ancrés
python scripts/tableau_de_bord.py   # docs/etat.md, depuis les registres
git add -A && git rebase --continue
python -m pytest && bash scripts/pousser.sh
```

  Le côté qu'on garde n'a pas d'importance, puisqu'on réécrit ces fichiers
  depuis les sources rebasées. Même geste pour un conflit de prose
  qui ne porte que sur des chiffres ancrés (`<!--chiffre:…-->`) : garder UN
  côté, jamais les deux, puis `python scripts/verifier_prose.py --corriger`.
  Garder les deux a doublé deux fois un paragraphe de la feuille de route ;
  `tests/test_prose.py` refuse désormais deux paragraphes identiques à la
  suite. Et `git checkout --theirs` sur un fichier de prose en conflit est à
  proscrire : il reprend le fichier ENTIER d'un côté, et efface ce que
  l'autre session y a écrit ailleurs. Si plusieurs commits de la session
  touchent aux témoins, le rebasage s'arrête autant de fois : régénérer à
  chaque arrêt, chaque commit retrouvant alors les témoins de son propre état.

## Projet

Modèle de retraite français en comptes notionnels appliqué rétroactivement.
Le livrable est le site statique ; voir `README.md`.

**L'architecture du dépôt** est dans `docs/architecture.md` ; où en est le
dépôt, ce qui ne va pas encore et ce qui reste à faire, dans le tableau de
bord, `docs/etat.md`, que `python scripts/tableau_de_bord.py` fabrique.

- Modèle de référence, en Python : `src/`
- Données (barèmes, régimes, séries) : `data/`
- Tous les régimes, calculés ou non : `data/reference/regimes/inventaire.yaml`.
  Toute fiche ajoutée au catalogue y prend sa ligne, un test l'exige.
- L'histoire des règles : `data/reference/legislation/reformes.yaml` (le calendrier
  des réformes, régime par régime) et `data/reference/regimes/pivots.yaml` (les
  articles dont les versions datent chaque fiche). `python scripts/calendrier_regimes.py
  --regime X` lit leurs versions dans l'index LEGI et dit ce que la fiche ne coupe
  pas ; `--carte` imprime le tableau des jeux de règles. Un test impose que toute
  réforme touchant un régime soit coupée, absorbée ou déclarée `non_appliquee`.
- Ce que le site charge : `moteur/` — portage JavaScript du modèle (`moteur/js/`),
  paquet de données et feuille de style, tous deux produits par
  `python scripts/construire_donnees.py`. À reconstruire après toute modification
  des données ou du style.
- Tests : `tests/` — `python -m pytest` (lance aussi `node --test`). La suite
  complète se répartit d'elle-même sur les cœurs et tient en huit minutes
  environ sur quatre (mesuré le 23 septembre 2026 ; « trente-cinq
  secondes », qu'on lisait ici, datait d'une suite bien plus légère) ;
  viser
  un fichier ou un cas (`python -m pytest tests/test_moteur.py`) la garde en
  série, ce qui est plus lisible et plus rapide pour un seul test. Pour tout
  forcer en série : `PYTEST_SANS_XDIST=1`.
  La suite rapide, `python -m pytest -m rapide`, ne joue que les règles et
  les étapes, sous deux minutes, même en série : c'est elle qu'on relance en
  travaillant. `python -m pytest` n'a pas changé : il lance toujours la suite
  complète, qui passe avant tout envoi sur `main`, et que GitHub rejoue après
  chaque envoi (onglet Actions). `tests/conftest.py` range chaque fichier dans
  son niveau — rapide, complet ou contrôle — et un fichier lent qui naît s'y
  range, sans quoi il alourdirait la suite rapide.
- Mise en route d'une session : `pip install -e '.[dev]'`. Sans ça,
  `python -m pytest` répond « No module named pytest », puis ne collecte rien
  faute du paquet `retraite_notionnelle` — c'est ce qui coûtait le plus de
  temps au démarrage. Un hook `SessionStart` le ferait tout seul ; son script
  est sous l'action 33 de `docs/feuille_de_route.md`, à poser à la main, une
  session Claude Code n'ayant pas le droit d'écrire sous `.claude/`.
- Outillage d'audit d'interface (Impeccable, Web Interface Guidelines,
  Playwright CLI) : compétences dans `.claude/skills/`, mises en place par
  `scripts/setup_ui_tools.sh` ; ce qui demande le réseau et comment changer une
  version figée : `docs/outillage_interface.md`.
- Ce que la prose affirme, et ce qu'un test en exige : `docs/fraicheur.md`. Une
  section est `etat` (vraie aujourd'hui : tout chiffre y est ancré sur une sonde
  qui le recalcule, un chiffre nu est refusé), `recit` (vraie à sa date, gelée),
  `produit` (écrite par un script) ou `a_declarer`. Le partage est dans
  `data/reference/prose/zones.yaml`, et ses deux cliquets ne peuvent que
  décroître. Après toute modification de la prose :
  `python scripts/verifier_prose.py --corriger`.
- Ce que la proposition coûte et rapporte, année par année, pour un projet de
  loi de finances : `docs/chiffrage_plf.md`, dont tous les tableaux sont écrits
  par `python scripts/chiffrage_plf.py` et tenus par un test de péremption. Sa
  prose est datée ; ses chiffres ne le sont pas. Ne jamais y corriger un tableau
  à la main.
- Les chantiers à mener, classés par ce qu'ils déplacent : `docs/feuille_de_route.md`.
  Une session qui cherche quoi faire commence là — par les actions `en cours`
  et ce que leurs dernières notes laissent ouvert, aucune n'étant plus « à
  faire » —, et y note ce qu'elle a fait.
- Seule dépendance hors bibliothèque standard : PyYAML. Le portage JavaScript
  n'utilise aucune bibliothèque. pytest et pytest-xdist ne servent qu'aux tests
  (`.[dev]`) ; la suite tourne sans xdist, en série.
- Les données lues sur disque sont mémorisées, indexées sur la signature du
  fichier (mtime et taille) : `charger_yaml`, `charger_serie_annuelle`, la
  table des quotients de mortalité. Un fichier modifié est donc relu sans
  qu'on ait à vider quoi que ce soit. Les lois de mortalité calibrées, elles,
  sont gardées sur disque (`data/derive/calibrations_mortalite.json`), et une
  loi n'y est reprise que si l'empreinte de ses entrées est celle des données
  du jour : ce n'était pas le cas avant le 23 septembre 2026, et 112 lois
  étaient restées calées sur d'anciennes cibles. `charger_yaml` rend une copie, l'appelant
  peut la modifier ; les séries et la table des quotients sont partagées, parce
  qu'elles ne sont jamais modifiées — le rester est une contrainte. Ne pas
  contourner ces points de passage : ce sont eux qui tiennent les temps.
- `SerieAnnuelle` et `Carriere` sont immuables après leur constructeur, et s'en
  servent : mémoire d'interpolation pour la première, `cached_property` pour la
  seconde (`date_liquidation` était recalculée 1,3 million de fois). Ajouter un
  champ qu'on réassigne après coup casserait silencieusement ces mémoires.

Le Python de `src/` fait foi. Toute modification du modèle doit être portée dans
`moteur/js/`, puis les témoins régénérés par
`python scripts/construire_temoins.py` : leur diff montre, chiffre par chiffre,
ce que le changement déplace.

## Le scénario 1 est le droit applicable, et rien d'autre

Le scénario 1 est l'étalon : il doit être le droit EN VIGUEUR à la date
d'effet de la pension, tel que la caisse l'applique. Le 17 septembre 2026,
ses âges légaux certifiés dataient d'un dump LEGI antérieur à la loi qui les
avait changés, et rien ne le disait. D'où trois obligations, décrites dans
`docs/veille_droit.md` :

- **Au début de toute session qui touche au scénario 1**, lancer
  `python scripts/veille_droit.py` et consulter les sources qu'il liste pour
  tout texte paru depuis la dernière date du journal (LFSS de l'année et ses
  décrets, circulaires Cnav, fiches service-public, JORF par l'index DILA).
- **Toute règle écrite ou modifiée** a été lue sur Légifrance (version en
  vigueur, identifiant) ET dans la circulaire ou la fiche qui l'applique, a
  son exemple chiffré publié dans `tests/temoins/exemples_officiels.yaml`
  quand il en existe un, et sa ligne dans
  `data/reference/legislation/veille.yaml` avec la date de lecture et l'état.
  Une déduction n'est pas une lecture ; une mémoire n'est pas une source ; une
  table certifiée l'est à une date.
- **À la fin**, consigner dans le `journal` de `veille.yaml` ce qui a été
  consulté, trouvé et laissé. Un test refuse toute réforme du calendrier
  datée de 2023 ou après sans sa ligne de veille ; les plus anciennes n'en
  exigent pas.

## Chercher dans le JORF ou LEGI

Ne pas retélécharger les dumps de la DILA pour une recherche : l'index plein
texte du champ social se récupère en une minute depuis la release `index-dila`
du dépôt, que le workflow GitHub Actions `index-dila.yml` tient à jour chaque
lundi. Si `--recuperer` répond qu'aucun index n'est publié, lancer ce workflow
(onglet Actions, « Run workflow ») plutôt que d'écrire un nouveau filtre en
flux ; une session ne peut pas publier elle-même, GitHub le lui interdit.

```bash
python scripts/fetch/dila_index.py jorf --recuperer      # une fois par session
python scripts/fetch/dila_index.py jorf --mettre-a-jour  # les incréments parus depuis
python scripts/fetch/dila_cherche.py jorf 'plafond NEAR("securite sociale")' --jusqu 1981
python scripts/fetch/dila_cherche.py jorf --texte JORFTEXT000000568533 --motif mensuel
python scripts/fetch/dila_cherche.py legi '"sur la base de" heures' --num R351-9
```

Lire les extraits, pas les textes : `--compter` d'abord si la requête est
large, `--limite` ensuite, `--texte ID --motif` pour ne lire que les fenêtres
utiles. L'index ne contient que le champ social (voir `THEMATIQUE` dans
`dila_index.py`) : ce qu'il ne trouve pas peut exister dans le dump. Les
scripts de certification lisent eux aussi l'index depuis le 17 septembre
2026 ; leur option `--dump` garde la lecture du dump.
