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
grave), un commit signé d'une adresse nominative. En avance sur `main`, il
pousse tout ce qui est commité, même si d'autres modifications attendent :
ne commiter qu'une fois ses tests passés, puisque le hook publie à chaque fin
de tour. À la main, la recette reste
`git fetch origin`, `git merge --ff-only origin/main`,
`git push origin HEAD:main` ; si l'avance rapide est refusée, la session a
divergé, et il faut comprendre pourquoi avant d'insister.

- **Ne jamais faire `git checkout main`, ni se fier au `main` local** : il
  date du clone. Ne comptent que `origin/main` et `HEAD`.
- **Ne jamais forcer une poussée sur `main`**, même pour « réparer ».
- **Aucune adresse nominative dans un commit** : auteur et committer en
  `noreply` (Anthropic, GitHub). Sur un poste, dans chaque clone :
  `git config user.name "g-pliberal"` et
  `git config user.email "240225789+g-pliberal@users.noreply.github.com"`.
- **Un clone d'avant le 26 septembre 2026** ne suit plus `main` : l'historique
  a été réécrit le 23 septembre, pour en retirer des adresses nominatives,
  puis le 26, pour en retirer un document que sa licence interdit de
  republier. Sans rien de non publié, le remplacer par un clone neuf ; sinon,
  reporter ses commits, puis publier :
  `git fetch origin main`,
  `git rebase --onto origin/main "$(git merge-base --fork-point origin/main HEAD)"`,
  `bash scripts/pousser.sh`.
- **Les branches `claude/*` se suppriment à la main**, depuis l'onglet
  Branches de GitHub : le jeton d'une session répond 403.
- **Le compteur de commits « non poussés » est faux** : relancer le script,
  et ne rien écrire là-dessus, une ligne au plus.

**Plusieurs sessions en parallèle**, chacune dans son conteneur, se partagent
le dépôt par zones : une sur le modèle et son portage, une sur les données et
la certification, une sur le site — jamais deux sur les pages en même temps.
Commiter petit, pousser souvent. Chaque session écrit ses journaux dans des
fichiers à elle (action 148), au dernier commit, juste avant de pousser : sa
note de feuille de route, voir « La documentation, au plus court », et son
entrée du journal de veille,
`data/reference/legislation/journal_de_veille/<AAAA-MM-JJ>-<sujet>.yaml`.
Deux sessions sur deux étapes d'une même action n'écrivent ainsi dans aucun
journal commun. Une action qui se clôt passe, telle quelle, à la fin de
`docs/archives/feuille_de_route.md`, et le dossier de ses notes sous
`docs/archives/feuille_de_route/`.

**Les fichiers fabriqués et la suite complète sont à GitHub** (action 148).
À chaque envoi sur `main`, `tests.yml` repart du dernier `main`, lance
`regenerer.py` puis la suite complète, et commite sous `github-actions[bot]`
les fichiers refaits et le verdict, `.github/etat_suite.yaml`, que le hook
`SessionStart` affiche à l'ouverture : une suite rouge se répare avant tout.
Une session lance `python -m pytest -m rapide` et les fichiers de tests de sa
zone avant chaque envoi, pas la suite complète ; elle peut régénérer pour voir
ce que son changement déplace, sans y être tenue. Un conflit de rebasage qui
ne porte que sur des fichiers marqués `-merge` dans `.gitattributes`,
`pousser.sh` le règle seul, en gardant la version de `main`. Un conflit de
prose qui ne porte que sur des chiffres ancrés (`<!--chiffre:…-->`) : garder
UN côté, jamais les deux, puis `python scripts/verifier_prose.py --corriger`.
Jamais `git checkout --theirs` sur un fichier de prose : il reprend le fichier
entier d'un côté, et efface ce que l'autre session y a écrit.

## Économiser le contexte

Chaque appel d'outil relit toute la conversation : ce qu'une session a lu,
elle le repaie à chaque geste suivant, et elle coûte d'autant plus cher
qu'elle dure. D'où cinq règles.

- **Une session, une étape.** L'étape poussée sur `main`, la session s'arrête
  et le dit au propriétaire ; l'étape suivante s'ouvre dans une session neuve.
- **Au démarrage, le bloc « Reprise » seul.** Chaque action `en cours` de la
  feuille de route s'ouvre, sous son titre, sur un paragraphe
  `**Reprise, au <date>.**` de dix lignes au plus : où elle en est, ce qui
  reste, par quoi commencer, et la note à lire pour le détail ;
  `python scripts/reprise.py`, ou `reprise.py 138` pour une seule action, les
  imprime avec la liste des notes de chacune. La session qui avance l'action
  le récrit, daté du jour, au commit de sa note ; c'est le seul paragraphe
  d'une action qui se récrit. Quand les étapes d'une action se mènent en
  parallèle, son bloc le dit, et aucune session ne le récrit plus : chaque
  étape inachevée tient le sien, sous le titre de sa note, et l'ôte en
  finissant.
- **Chercher avant de lire.** `grep -n` d'abord, puis la seule fenêtre utile
  (`Read` avec `offset` et `limit`, ou `sed -n`). Ne se lisent jamais en
  entier : `moteur/js/pages.js`, `docs/feuille_de_route.md` et les archives,
  `docs/architecture.md`, `README.md`, `tests/test_simulateur.py`,
  `scripts/verifier_donnees.py`, `data/sources.yaml`, ni `moteur/donnees.json`
  et les témoins de `tests/temoins/`, qui se lisent par `resumer_temoins.py`
  ou par une requête ciblée.
- **Les sorties longues passent par `tail` ou `grep`** :
  `python -m pytest 2>&1 | tail -n 30`, de même pour `regenerer.py` et
  `resumer_temoins.py` ; jamais de `git diff` ni de `git show` entier sur un
  témoin ou sur `pages.js`.
- **L'enquête à la mesure de la question.** Une question appelle la
  vérification qui y répond, pas davantage ; une recherche en éventail,
  plusieurs agents en parallèle, ne se lance qu'à la demande du propriétaire.

## Travailler

- **Mise en route** : `pip install -e '.[dev]'`. Sans lui, `python -m pytest`
  ne trouve ni pytest ni le paquet. Une session web n'a pas à le lancer : le
  hook `SessionStart` (`.claude/hooks/session-start.sh`, action 33 de la
  feuille de route, archivée) l'installe en arrière-plan à son ouverture,
  avec un PyYAML qui embarque libyaml. Un « No module named pytest » dans les
  premières secondes veut dire qu'il n'a pas fini : relancer un peu plus tard,
  sans réinstaller. Sur un poste, la commande reste à lancer une fois.
- **Les tests** : `python -m pytest -m rapide` en travaillant, les règles et
  les étapes, sous deux minutes ; `python -m pytest -m site` après une
  retouche du site ou de la saisie, en une minute ; `python -m pytest`, la
  suite complète, c'est GitHub qui la lance après chaque envoi (voir « Les
  fichiers fabriqués et la suite complète sont à GitHub »). La suite se répartit sur les cœurs, et un fichier
  visé aussi quand il est lourd (`POIDS_REPARTI`, dans `pytest_parallele.py`) ;
  un cas précis ou un fichier léger reste en série, `PYTEST_SANS_XDIST=1`
  force la série. `tests/conftest.py` range chaque fichier dans son niveau :
  un fichier lent qui naît s'y range. Les tests du site tiennent en trois
  fichiers, `test_web.py`, `test_web_saisie.py` et `test_web_revues.py`, qui
  se partagent `tests/outils_web.py`.
- **Le Python de `src/` fait foi.** Toute modification du modèle se porte
  dans `moteur/js/`. Après elle, ou après toute modification des données,
  `python scripts/regenerer.py` refait tout ce qu'un script fabrique — le
  paquet, les témoins, le chiffrage, les tableaux, le tableau de bord, les
  chiffres ancrés —, dans l'ordre (`--verifier` dit ce qui est périmé sans
  rien écrire) ; `python scripts/resumer_temoins.py` dit ce qu'elle déplace,
  scénario par scénario, et le diff des témoins, chiffre par chiffre. Une
  étape dont rien n'a bougé ne se relance pas, et la suite ne revérifie pas
  ce qu'elle vient de fabriquer (`.cache/fabrique.json`, que
  `FABRIQUE_SANS_MEMOIRE=1` ignore) ; GitHub, sans mémoire, refait tout.
- **Le texte du site ne s'écrit qu'en JavaScript** : `moteur/js/pages.js`,
  `gabarit.js`, et `moteur/style.css`, sa propre source. Le Python le lit par
  `web/site.py`, qui le fait rendre par node ; les témoins de pages se refont
  par `construire_temoins.py`, après le paquet, et leur diff montre ce qu'une
  page a changé. Seules les pages dont le formulaire est le sujet le figent
  entier (`FORMULAIRE_ENTIER`) ; les autres n'en gardent que la balise.
- **Les données** sont dans `data/`. Tous les régimes, calculés ou non : un
  fichier par régime dans `data/reference/regimes/`, qui porte sa ligne
  d'inventaire ; `inventaire.yaml`, qui les énumère, s'en fabrique par
  `python scripts/construire_inventaire.py`. L'histoire des règles :
  `reformes.yaml` et `pivots.yaml` ;
  `python scripts/calendrier_regimes.py --regime X` dit ce qu'une fiche ne
  coupe pas, `--carte` imprime le tableau des jeux de règles, et toute
  réforme qui touche un régime est coupée, absorbée ou déclarée
  `non_appliquee`.
- **La proposition** : ses scénarios sont des univers de droit
  (`data/reference/univers/`), piles de couches (`data/reference/couches/`)
  posées sur le droit réel ; ce qu'elles ajoutent a sa fiche dans
  `data/reference/regles/proposition/`, qui cite le README. Une variante
  s'écrit en couche, jamais dans le code, et le moteur refuse ce qu'il ne
  sait pas calculer (`scenarios/univers.py`).
- **La prose** : chaque document a son régime, déclaré dans
  `data/reference/prose/zones.yaml` — `etat` (tout chiffre y est ancré sur
  une sonde), `recit` (vrai à sa date, gelé) ou `produit` —, et ce qui s'en
  écarte s'y déclare un à un (`docs/fraicheur.md`). Un récit ne s'écrit pas
  au milieu d'un état : il va dans la feuille de route ou une archive. Après
  toute modification de la prose : `python scripts/verifier_prose.py
  --corriger`. Les tableaux de `docs/chiffrage_plf.md` s'écrivent par
  `python scripts/chiffrage_plf.py`, jamais à la main.
- **La documentation, au plus court** : une note de feuille de route par
  étape, au commit qui la clôt, et non une par sous-partie, dans un fichier à
  elle : `docs/feuille_de_route/<action>/<AAAA-MM-JJ>-<sujet>.md`
  (`148/2026-10-06-etape-2.md`), qui s'ouvre sur son titre ; les notes
  écrites avant le 6 octobre 2026 restent dans la feuille de route. Une
  session qui s'arrête en cours d'étape dit seulement où, dans le bloc
  « Reprise ». Une
  version de l'architecture par domaine, à sa clôture, ou par décision hors
  domaine. Les fiches et
  `limites.md` une fois, à la fin de l'étape, sauf ce qu'un test exige plus
  tôt. Un message de commit de cinq lignes au plus sous son titre, le détail
  allant à la feuille de route. Le journal de veille garde sa règle.
- **Rien ne se perd** (`docs/architecture.md`, § 12) : un récit ne se réécrit
  pas, et un déplacement de fichiers se vérifie avant d'être commité, par
  `python scripts/conservation.py --depuis HEAD`. Une seule session déplace
  des fichiers à la fois. À la fin de chaque domaine, la référence du test de
  conservation (`tests/temoins/conservation.json`) se refige, pour protéger
  les récits nés depuis : `python scripts/conservation.py --figer`, qui
  refuse s'il y a une perte.
- **Les dépendances** : PyYAML seul hors bibliothèque standard ; le portage
  JavaScript n'en a aucune ; pytest et pytest-xdist ne servent qu'aux tests.
  Node, qui fait tourner le portage, sert aussi au Python qui lit le site :
  les tests des pages, les témoins, la prose et le paquet.
- **Les temps tiennent à des mémoires** qu'il ne faut pas contourner :
  `charger_yaml` (qui rend une copie), `charger_serie_annuelle` et la table
  des quotients de mortalité, indexées sur la signature du fichier, partagées
  et jamais modifiées ; le temps d'un calcul, les chargeurs marqués
  `une_fois_par_instantane` ne regardent le disque qu'une fois
  (`chargement.instantane`), un `stat` coûtant cher sous Windows ; les lois
  de mortalité calibrées, gardées dans
  `data/derive/calibrations_mortalite.json` et reprises seulement si
  l'empreinte de leurs entrées est celle du jour ; le coût agrégé, ses
  variantes et le coût des avantages, que `memoire.py` garde dans le
  `.cache/calculs/` du dépôt principal, commun à tous ses worktrees, sous
  l'empreinte de `src/`, `data/` et `scripts/`, un seul processus faisant
  chaque calcul pendant que les autres l'attendent
  (`CALCULS_SANS_MEMOIRE=1` s'en passe) et ne sert que sur le modèle intact :
  qui en remplace une fonction s'ouvre sous `memoire.modele_modifie()`, et
  `monkeypatch` la fait taire. `SerieAnnuelle` et
  `Carriere` sont immuables après leur constructeur : un champ réassigné
  après coup casserait leurs mémoires sans bruit.
- **L'outillage d'audit d'interface** (Impeccable, Web Interface Guidelines,
  Playwright CLI) : `.claude/skills/`, mis en place par
  `scripts/setup_ui_tools.sh` ; voir `docs/outillage_interface.md`.

## Listes de contrôle

- **Au début d'une étape** : lire le bloc « Reprise » de son action, et celui
  de son étape s'il en a un (`python scripts/reprise.py <action>`), puis
  relever, par `grep -n` de son numéro ou de son domaine, ce que la feuille de
  route, ses notes et les fiches lui renvoient, avant d'écrire la moindre
  ligne.
- **Une retouche de `moteur/js/pages.js`** : le budget de mots du formulaire
  vierge (`test_le_simulateur_tient_en_peu_de_mots`) ; toute phrase en gras
  d'une page figée au catalogue `data/reference/site/affirmations.yaml`, avec
  son contrôle ; `python scripts/construire_temoins.py`, puis
  `python scripts/resumer_temoins.py` ; `python -m pytest -m site`.
- **Un champ de saisie de plus** : les deux saisies, `saisie.py` et
  `saisie.js` — la lecture, la vérification, la réécriture de l'adresse — ;
  toute borne `min` ou `max` du formulaire opposée aussi par la saisie ; les
  deux contextes ; la chronologie s'il porte un fait ; un témoin de
  simulation, et de page si la page change ; `python -m pytest -m site`.
- **Un changement du modèle** : le Python d'abord, puis son jumeau ;
  `python scripts/regenerer.py`, puis `python scripts/resumer_temoins.py`, pour
  voir ce qu'il déplace ; `-m rapide` et les tests de sa zone, puis le commit.

## Le scénario 1 est le droit applicable, et rien d'autre

Le scénario 1 est l'étalon : le droit EN VIGUEUR à la date d'effet de la
pension, tel que la caisse l'applique. D'où trois obligations, décrites dans
`docs/veille_droit.md` :

- **Au début de toute session qui touche au scénario 1**, lancer
  `python scripts/veille_droit.py` et consulter les sources qu'il liste pour
  tout texte paru depuis la dernière date du journal (LFSS de l'année et ses
  décrets, circulaires Cnav, fiches service-public, JORF par l'index DILA).
- **Toute règle écrite ou modifiée** a été lue sur Légifrance (version en
  vigueur, identifiant) ET dans la circulaire ou la fiche qui l'applique, a
  son exemple chiffré publié dans `tests/temoins/exemples_officiels.yaml`
  quand il en existe un — en écart connu si le modèle ne le reproduit pas —,
  et sa fiche dans `data/reference/regles/`, avec la date de lecture et
  l'état. Une déduction n'est pas une lecture ; une mémoire n'est pas une
  source ; une table certifiée l'est à une date.
- **À la fin**, consigner ce qui a été consulté, trouvé et laissé dans une
  entrée du journal de veille : un fichier neuf de
  `data/reference/legislation/journal_de_veille/`, nommé de la date et du
  sujet de la session (`2026-10-06-action-148-etape-2.yaml`). Un test refuse
  toute réforme du calendrier datée de 2023 ou après sans la fiche qui la
  couvre.

## Chercher dans le JORF ou LEGI

Ne pas retélécharger les dumps de la DILA : l'index plein texte du champ
social se récupère en une minute depuis la release `index-dila` du dépôt, que
le workflow `index-dila.yml` tient à jour chaque lundi. Si `--recuperer`
répond qu'aucun index n'est publié, lancer ce workflow (onglet Actions, « Run
workflow ») : une session ne peut pas publier elle-même.

```bash
python scripts/fetch/dila_index.py jorf --recuperer      # une fois par session
python scripts/fetch/dila_index.py jorf --mettre-a-jour  # les incréments parus depuis
python scripts/fetch/dila_cherche.py jorf 'plafond NEAR("securite sociale")' --jusqu 1981
python scripts/fetch/dila_cherche.py jorf --texte JORFTEXT000000568533 --motif mensuel
python scripts/fetch/dila_cherche.py legi '"sur la base de" heures' --num R351-9
```

Lire les extraits, pas les textes : `--compter` d'abord si la requête est
large, `--limite` ensuite, `--texte ID --motif` pour ne lire que les fenêtres
utiles. L'index ne contient que le champ social (`THEMATIQUE` dans
`dila_index.py`) : ce qu'il ne trouve pas peut exister dans le dump, que les
scripts de certification lisent encore par leur option `--dump`.
