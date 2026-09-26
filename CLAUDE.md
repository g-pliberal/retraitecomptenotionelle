# Conventions du dépôt

Modèle de retraite français en comptes notionnels, appliqué rétroactivement ;
le livrable est le site statique (`README.md`). L'architecture est dans
`docs/architecture.md` ; où en est le dépôt, et ce qui reste à faire, dans le
tableau de bord `docs/etat.md`, que `python scripts/tableau_de_bord.py`
fabrique ; les chantiers ouverts, dans `docs/feuille_de_route.md` : une
session qui cherche quoi faire commence par ses actions `en cours` et ce que
leurs dernières notes laissent ouvert, et y note ce qu'elle a fait. Ce
fichier ne garde que les
règles : l'histoire de chacune, et l'incident qui l'a fait naître, sont dans
`docs/archives/conventions.md`.

## Git : tout va sur `main`

**On publie sur `main`, toujours, sans pull request**, par
`bash scripts/pousser.sh`, qu'un hook `Stop` (`.claude/settings.json`) lance
aussi à chaque fin de tour. Cette règle prime sur la branche `claude/…`
qu'une session Claude Code se voit assigner : elle y travaille, mais elle
pousse sur `main`, et ne finit jamais en laissant son travail sur la branche.

Le script rattrape `origin/main` en avance rapide, rebase au besoin les
commits de la session qu'une autre session a devancés, pousse `HEAD` sur
`main`, puis fait suivre la branche de la session. Il refuse, sans rien
pousser : un conflit, plus de vingt commits d'écart, des modifications non
commitées quand il doit rebaser, aucun ancêtre commun avec `main` (le cas
grave), un commit signé d'une adresse nominative. En avance sur `main`, il
pousse tout ce qui est commité, même si d'autres modifications attendent :
ne commiter qu'une fois la suite complète passée, puisque le hook publie à
chaque fin de tour. À la main, la recette reste
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
Commiter petit, pousser souvent. Écrire dans la feuille de route, et dans le
`journal` de `veille.yaml`, au dernier commit, juste avant de pousser ; une
action qui se clôt passe, telle quelle, à la fin de
`docs/archives/feuille_de_route.md`.

**Un conflit sur un fichier fabriqué ne s'arbitre pas, il se relance.**
`.gitattributes` marque `-merge` les fichiers qu'un script écrit : git y
déclare le conflit sans fusionner, la version de la branche courante reste,
et l'on réécrit depuis les sources rebasées.

```bash
git rebase origin/main          # pousser.sh l'a refusé, on le reprend à la main
python scripts/construire_donnees.py
python scripts/construire_temoins.py
python scripts/chiffrage_plf.py     # ses tableaux, dans le .md, sont des chiffres ancrés
python scripts/tableau_de_bord.py   # docs/etat.md, depuis les registres
git add -A && git rebase --continue
python -m pytest && bash scripts/pousser.sh
```

Si plusieurs commits touchent aux témoins, régénérer à chaque arrêt du
rebasage. Un conflit de prose qui ne porte que sur des chiffres ancrés
(`<!--chiffre:…-->`) : garder UN côté, jamais les deux, puis
`python scripts/verifier_prose.py --corriger`. Jamais
`git checkout --theirs` sur un fichier de prose : il reprend le fichier
entier d'un côté, et efface ce que l'autre session y a écrit.

## Travailler

- **Mise en route** : `pip install -e '.[dev]'`. Sans lui, `python -m pytest`
  ne trouve ni pytest ni le paquet. Le hook `SessionStart` qui le ferait est
  à poser à la main (action 33 de la feuille de route, archivée) : une
  session n'a pas le droit d'écrire sous `.claude/`.
- **Les tests** : `python -m pytest -m rapide` en travaillant, les règles et
  les étapes, sous deux minutes ; `python -m pytest`, la suite complète,
  avant tout envoi sur `main`, que GitHub rejoue ensuite (onglet Actions).
  La suite se répartit sur les cœurs ; viser un fichier la garde en série,
  `PYTEST_SANS_XDIST=1` force la série. `tests/conftest.py` range chaque
  fichier dans son niveau : un fichier lent qui naît s'y range.
- **Le Python de `src/` fait foi.** Toute modification du modèle se porte
  dans `moteur/js/`, puis `python scripts/construire_temoins.py` : le diff des
  témoins montre, chiffre par chiffre, ce qu'elle déplace. Après toute
  modification des données ou du style : `python scripts/construire_donnees.py`.
- **Les données** sont dans `data/`. Tous les régimes, calculés ou non :
  `data/reference/regimes/inventaire.yaml`, où toute fiche du catalogue prend
  sa ligne. L'histoire des règles : `reformes.yaml` et `pivots.yaml` ;
  `python scripts/calendrier_regimes.py --regime X` dit ce qu'une fiche ne
  coupe pas, `--carte` imprime le tableau des jeux de règles, et toute
  réforme qui touche un régime est coupée, absorbée ou déclarée
  `non_appliquee`.
- **La prose** : chaque document a son régime, déclaré dans
  `data/reference/prose/zones.yaml` — `etat` (tout chiffre y est ancré sur
  une sonde), `recit` (vrai à sa date, gelé) ou `produit` —, et ce qui s'en
  écarte s'y déclare un à un (`docs/fraicheur.md`). Un récit ne s'écrit pas
  au milieu d'un état : il va dans la feuille de route ou une archive. Après
  toute modification de la prose : `python scripts/verifier_prose.py
  --corriger`. Les tableaux de `docs/chiffrage_plf.md` s'écrivent par
  `python scripts/chiffrage_plf.py`, jamais à la main.
- **Rien ne se perd** (`docs/architecture.md`, § 12) : un récit ne se réécrit
  pas, et un déplacement de fichiers se vérifie avant d'être commité, par
  `python scripts/conservation.py --depuis HEAD`. Une seule session déplace
  des fichiers à la fois.
- **Les dépendances** : PyYAML seul hors bibliothèque standard ; le portage
  JavaScript n'en a aucune ; pytest et pytest-xdist ne servent qu'aux tests.
- **Les temps tiennent à des mémoires** qu'il ne faut pas contourner :
  `charger_yaml` (qui rend une copie), `charger_serie_annuelle` et la table
  des quotients de mortalité, indexées sur la signature du fichier, partagées
  et jamais modifiées ; les lois de mortalité calibrées, gardées dans
  `data/derive/calibrations_mortalite.json` et reprises seulement si
  l'empreinte de leurs entrées est celle du jour. `SerieAnnuelle` et
  `Carriere` sont immuables après leur constructeur : un champ réassigné
  après coup casserait leurs mémoires sans bruit.
- **L'outillage d'audit d'interface** (Impeccable, Web Interface Guidelines,
  Playwright CLI) : `.claude/skills/`, mis en place par
  `scripts/setup_ui_tools.sh` ; voir `docs/outillage_interface.md`.

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
- **À la fin**, consigner dans le `journal` de
  `data/reference/legislation/veille.yaml` ce qui a été consulté, trouvé et
  laissé. Un test refuse toute réforme du calendrier datée de 2023 ou après
  sans la fiche qui la couvre.

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
