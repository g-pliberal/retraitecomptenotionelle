# Conventions du dépôt

## Git

**Tout va sur `main`, toujours, sans exception.** Pas de branche de
fonctionnalité, pas de pull request : on rattrape `main`, et on pousse dessus.

```bash
git fetch origin
git merge --ff-only origin/main     # rattraper ce que main a reçu entre-temps
git commit -am "message"
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
voudrait en ressusciter une.

## Projet

Modèle de retraite français en comptes notionnels appliqué rétroactivement.
Le livrable est le site statique ; voir `README.md`.

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
  complète se répartit d'elle-même sur les cœurs et tient en trente-cinq
  secondes ; viser
  un fichier ou un cas (`python -m pytest tests/test_moteur.py`) la garde en
  série, ce qui est plus lisible et plus rapide pour un seul test. Pour tout
  forcer en série : `PYTEST_SANS_XDIST=1`.
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
- Les chantiers à mener, classés par ce qu'ils déplacent : `docs/feuille_de_route.md`.
  Une session qui cherche quoi faire commence là, et y note ce qu'elle a fait.
- Seule dépendance hors bibliothèque standard : PyYAML. Le portage JavaScript
  n'utilise aucune bibliothèque. pytest et pytest-xdist ne servent qu'aux tests
  (`.[dev]`) ; la suite tourne sans xdist, en série.
- Les données lues sur disque sont mémorisées, indexées sur la signature du
  fichier (mtime et taille) : `charger_yaml`, `charger_serie_annuelle`, la
  table des quotients de mortalité. Un fichier modifié est donc relu sans
  qu'on ait à vider quoi que ce soit. `charger_yaml` rend une copie, l'appelant
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
  sans sa ligne de veille.

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
`dila_index.py`) : ce qu'il ne trouve pas peut exister dans le dump, que les
scripts de certification continuent de lire.
