# Conventions du dépôt

## Git

Tous les travaux vont directement sur `main`. Pas de branche de
fonctionnalité, pas de pull request : on commite sur `main` et on pousse.

```bash
git checkout main
git commit -am "message"
git push -u origin main
```

Cette règle s'applique aussi aux sessions Claude Code : si une branche de
travail dédiée a été créée automatiquement, revenir sur `main` avant de
commiter.

## Projet

Modèle de retraite français en comptes notionnels appliqué rétroactivement.
Le livrable est le site statique ; voir `README.md`.

- Modèle de référence, en Python : `src/`
- Données (barèmes, régimes, séries) : `data/`
- Ce que le site charge : `moteur/` — portage JavaScript du modèle (`moteur/js/`),
  paquet de données et feuille de style, tous deux produits par
  `python scripts/construire_donnees.py`. À reconstruire après toute modification
  des données ou du style.
- Tests : `tests/` — `python -m pytest` (lance aussi `node --test`)
- Seule dépendance hors bibliothèque standard : PyYAML. Le portage JavaScript
  n'utilise aucune bibliothèque.

Le Python de `src/` fait foi. Toute modification du modèle doit être portée dans
`moteur/js/`, puis les témoins régénérés par
`python scripts/construire_temoins.py` : leur diff montre, chiffre par chiffre,
ce que le changement déplace.

## Chercher dans le JORF ou LEGI

Ne pas retélécharger les dumps de la DILA pour une recherche : l'index plein
texte du champ social se récupère en une minute depuis la release `index-dila`
du dépôt. Si `--recuperer` répond qu'aucun index n'est publié, le construire
(`dila_index.py jorf`, deux heures) plutôt que d'écrire un nouveau filtre en
flux, et signaler que la publication reste à faire depuis un poste de travail.

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
