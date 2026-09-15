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
- Tests : `tests/` — `python -m pytest` (lance aussi `node --test`)
- Les chantiers à mener, classés par ce qu'ils déplacent : `docs/feuille_de_route.md`.
  Une session qui cherche quoi faire commence là, et y note ce qu'elle a fait.
- Seule dépendance hors bibliothèque standard : PyYAML. Le portage JavaScript
  n'utilise aucune bibliothèque.

Le Python de `src/` fait foi. Toute modification du modèle doit être portée dans
`moteur/js/`, puis les témoins régénérés par
`python scripts/construire_temoins.py` : leur diff montre, chiffre par chiffre,
ce que le changement déplace.

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
