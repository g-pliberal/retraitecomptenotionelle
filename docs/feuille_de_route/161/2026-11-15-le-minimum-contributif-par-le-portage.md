# Le minimum contributif par le portage : `part_minimum_contributif.py` ne demande plus rien au moteur Python

Action 161, étape 6d, après `2026-11-15-le-cycle-de-vie-deja-au-portage.md`,
« Ce qui reste », 1 : la première des deux études que la table des
décisions laisse « non instruites ». Portée à sorties identiques, sans rien
trancher de son contenu. Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

- **Le test, écrit d'abord et vu rouge** pour la raison attendue
  (`test_le_minimum_se_mesure_au_portage_sans_le_moteur_python`, dans
  `tests/test_part_minimum_contributif.py`) : les jumeaux du coût et
  `Simulateur.echeancier` empêchés, `_mesurer` doit mesurer deux cas types
  de la table, une variante sur sept de la grille `reference` (générations
  1950 et 1962) et l'artisan au RSI (1946, 1950), avec ce que les tests
  voisins en disent : le Smic de 1955 relevé et majoré sous l'écrêtement, le
  cadre au-dessus, le RSI sans écrêtement avant 2012 et sous lui après.
  L'égalité au bit près avec le moteur Python se vérifie sur la mesure
  entière (section suivante) : un test qui l'appellerait remettrait le
  fichier dans la liste de `test_fichiers_sur_le_moteur_python.py`.
- **Le pont** : `departs_des_cas` reçoit un mode de lecture de plus,
  `"lire": "minimum"` (`minimumAuDepart` de `pont.mjs`,
  `_minimum_des_donnees` de `pont.py`). Le départ porte alors l'année et le
  mois de la liquidation, chaque pension avec sa date d'effet, la part de
  chaque régime et le détail de chaque minimum contributif appliqué, et le
  minimum avant écrêtement. Les autres modes n'ont pas changé.
- **`scripts/part_minimum_contributif.py`, `_mesurer`** : une seule demande
  par morceau, sous les paramètres de `Simulateur.pour_la_projection`, les
  primes projetées (`primes_projetees_en_donnees`) et le paquet des données
  du jour, puisque la mesure est gardée en mémoire. Le Python ne garde que
  ce qui est propre à l'étude : le choix du régime, la date d'effet la plus
  tôt, la somme ordonnée des parts du minimum, la majoration. Une carrière
  que le portage ne date pas, ou ne liquide pas, rend `None`, comme
  l'exception attrapée le faisait.

## Les chiffres, inchangés

Avant (au même commit de `main`, en arbre de travail à part) et après : la
mesure par défaut (grilles `reference` et `ensemble`, 1 033 carrières, aucune
refusée) et `--artisans` (525 carrières), sorties imprimées et JSON identiques
à l'octet, hors des durées. La grille `ensemble` passe de 598 s à 314 s sur
deux cœurs ; `reference`, de 30 s à 43 s, le pont s'ouvrant par morceau.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide`, le fichier
`tests/test_part_minimum_contributif.py` entier,
`tests/test_fichiers_sur_le_moteur_python.py` et `tests/test_prose.py`.

## Un point pour le propriétaire, sans rien trancher

Le portage attrape toute erreur qui n'est pas du programme ; le Python
n'attrapait que `ValueError` et `KeyError`. Une autre erreur, qui arrêtait la
mesure, compterait désormais la carrière comme refusée. Aucune ne s'est
produite sur la mesure entière.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. **L'étape suivante** : `scripts/partage_taux_unique.py`. Il n'appelle
   pas le moteur d'une carrière, mais les règles de la fiche de paie
   (`remuneration.py`, dont `remuneration.js` est le jumeau, que la carte
   des jumeaux dit bloqué par le coût). Le porter demande d'abord de servir
   au pont `ConstructeurFiche` et les blocs de la retraite, ou de décider
   que l'étude reste au Python avec le coût : à instruire d'abord.
2. Puis la liste des fonctions gardées des deux côtés, le retrait, et les
   périodes assimilées du relevé.
