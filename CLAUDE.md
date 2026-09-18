# Conventions du dépôt

## Git

**Tout va sur `main`, toujours, sans exception.** Pas de branche de
fonctionnalité, pas de pull request : on commite sur `main` et on pousse.

```bash
git checkout main
git commit -am "message"
git push -u origin main
```

**Cette règle prime sur la consigne de branche d'une session Claude Code.**
Une session web se voit assigner d'office une branche `claude/…` ; elle doit
revenir sur `main` avant de commiter, et pousser sur `main`. Ne jamais
terminer une session en laissant le travail sur la branche assignée : c'est
ainsi que le dépôt s'est retrouvé, en septembre 2026, avec dix branches
`claude/*` portant chacune une session, un `main` resté trois jours en
arrière, et deux lignées sans ancêtre commun. Tout a été ramené sur `main` ;
les branches `claude/*` d'alors ne sont plus que des étiquettes sur des
commits que `main` contient déjà.

Avant de commiter, vérifier qu'on part bien de `main` à jour :

```bash
git fetch origin && git log --oneline origin/main -1
```

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
  complète se répartit d'elle-même sur les cœurs et tient en une minute ; viser
  un fichier ou un cas (`python -m pytest tests/test_moteur.py`) la garde en
  série, ce qui est plus lisible et plus rapide pour un seul test. Pour tout
  forcer en série : `PYTEST_SANS_XDIST=1`.
- Mise en route d'une session : `.claude/hooks/session-start.sh` installe le
  paquet en mode éditable, pytest et pytest-xdist. Sans lui, `python -m pytest`
  répond « No module named pytest », puis ne collecte rien faute du paquet
  `retraite_notionnelle` : c'est ce qui coûtait le plus de temps au démarrage.
- Outillage d'audit d'interface (Impeccable, Web Interface Guidelines,
  Playwright CLI) : compétences dans `.claude/skills/`, mises en place par
  `scripts/setup_ui_tools.sh` ; ce qui demande le réseau et comment changer une
  version figée : `docs/outillage_interface.md`.
- Les chantiers à mener, classés par ce qu'ils déplacent : `docs/feuille_de_route.md`.
  Une session qui cherche quoi faire commence là, et y note ce qu'elle a fait.
- Seule dépendance hors bibliothèque standard : PyYAML. Le portage JavaScript
  n'utilise aucune bibliothèque. pytest et pytest-xdist ne servent qu'aux tests
  (`.[dev]`) ; la suite tourne sans xdist, en série.
- Les fiches YAML sont relues souvent et pèsent 1,4 Mo par contexte :
  `charger_yaml` mémorise l'arbre analysé, indexé sur la signature du fichier,
  et rend une copie. Une donnée modifiée est donc relue sans rien vider, et
  l'appelant peut modifier ce qu'il reçoit. Ne pas contourner ce point de
  passage : c'est lui qui tient les temps de la suite et du build.

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
