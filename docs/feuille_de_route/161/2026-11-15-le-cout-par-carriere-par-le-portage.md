# Le coût par carrière par le portage : `cout_avantages.py --par-carriere` ne demande plus rien au moteur Python

Action 161, étape 6b, après `2026-11-15-la-grille-des-meres-par-le-portage.md`,
« Ce qui reste », 1 : la deuxième étude de la table de
`2026-11-13-les-decisions-du-proprietaire.md`. Aucune règle, aucune donnée,
aucun témoin, ni le pont ni le portage n'ont bougé. Les suites complètes de
GitHub sur `14f43e8` et `0cf0d2d` tournaient encore au début de l'étape ; la
dernière connue, sur `3c5007c`, était verte.

## Ce qui est fait

- **Le test, écrit d'abord et vu rouge** pour la raison attendue
  (`test_le_cout_par_carriere_passe_par_le_portage_sans_le_moteur_python`,
  dans `tests/test_avantages.py`, qui entre déjà dans le moteur Python) :
  l'option telle qu'elle s'écrivait, recopiée dans le test, calcule la
  génération 1960 au moteur Python ; puis les jumeaux du coût,
  `avantages.recalculer` et le scénario 1 du simulateur sont empêchés, et
  `par_carriere` doit rendre les mêmes lignes. Elle les rend au bit près :
  âges, pensions, écarts et refus. Le test dit aussi ce que l'option montre :
  plus de dix cas types datés, et la dose qui fait paraître au moins un
  avantage. Il tourne en 8 s.
- **`scripts/cout_avantages.py`, `par_carriere`** : l'âge de chaque cas type
  par `pont.ages_de_depart` (relu sous le type du pilote Python, `age_lu`),
  puis une seule demande à `pont.avantages`, deux cases par cas type, la
  carrière réelle et la même sous la dose, chacune avec les contrefactuelles
  qu'elle demande (`_variantes_demandees`). Les écarts et les refus se
  mesurent ici, par `_ecarts`, comme pour la décomposition au portage
  (`_decomposees_au_portage`). Un cas type que le portage ne date ou ne
  liquide pas est omis, comme l'omettait l'exception attrapée. Le chemin
  principal et `--duree` n'ont pas changé.

## Les chiffres, inchangés

Avant et après, au même commit de `main` : `--par-carriere`, génération 1960
par défaut et génération 1975, sorties identiques à l'octet.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide` (5 248 tests),
le nouveau test, `test_fichiers_sur_le_moteur_python.py`. Les autres tests
de `test_avantages.py` relèvent du coût et restent à GitHub.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. **L'étape suivante** : les deux études que la table des décisions laisse
   « non instruites » (note de la question 3). La première à instruire et
   porter, une par session, selon la section « Hors de l'inventaire » de
   cette note : `cycle_de_vie.py`, qui date encore ses cases au pilote Python
   quand `castypes.cases_de_la_grille` le fait au portage.
2. Puis la liste des fonctions gardées des deux côtés, le retrait, et les
   périodes assimilées du relevé.
