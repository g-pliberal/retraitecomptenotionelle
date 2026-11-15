# Les départs à la façade : chaque départ liquidé et les pensions déjà servies

Action 161, étape 5k, après `2026-11-15-l-echeancier-restant-a-la-facade.md`,
« Ce qui reste », 2. Aucune règle, aucune donnée du dépôt, aucun témoin n'a
bougé. La suite complète de GitHub était verte sur `a08f52e` ; celles de
`04d0bec` et de `ebe8d2b` tournaient encore à l'envoi.

## Ce qui est fait

- **`departs.liquider_les_departs` servie par le portage** : une entrée de
  plus (`departs.liquider_les_departs`, `pont.mjs` et `pont.py`), qui reçoit
  le moteur, la carrière, les neutralisations du contexte, la nature et les
  départs reçus (`[année, mois, régimes, motif]`), ou les date elle-même. Un
  journal, une retraite progressive, le moteur Python sont refusés.
- **La liquidation reçoit les pensions déjà servies** : `liquidation.liquider`
  de la façade passe au portage les `departs.PensionServie` de l'état ; une
  pension provisoire, un recalcul restent refusés.
- **Ce qu'une liquidation de la façade rend, en plus** : `complements.minimum_applique`,
  sa demande (lue sous `Demande`, celle que le portage a bâtie pour chaque
  départ), `date_liquidation` (la date de la carrière liquidée) et `ouverte`.
  Le test des départs lit `liquidee.date_liquidation` et `liquidee.ouverte`,
  au lieu de la carrière et de l'ouverture, qui ne passent pas le pont.
- **`test_departs.py`** (2 → 0) quitte `RESTES` et ne tient plus la fixture
  des fichiers basculés. `test_facade.py` éprouve l'entrée et ses refus.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide`, `test_departs.py`,
`test_facade.py`, `test_fichiers_sur_le_moteur_python.py`, `test_pont.py`,
`test_liquidation.py`, `test_minima_agricoles.py`,
`test_majoration_exceptionnelle.py`, `test_reversion.py` et les
confrontations légères.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Les confrontations des deux moteurs gardent leur marque, comme le solveur
   `niveau_pour_pension` (`test_simulateur.py`) et `Saisies.simuler`
   (`test_reversion.py`).
2. Les autres tests marqués de `RESTES` qui ne sont pas des confrontations :
   d'abord les fins de charge et les étapes imbriquées
   (`test_majoration_enfants_a_charge.py`), l'étape suivante.
