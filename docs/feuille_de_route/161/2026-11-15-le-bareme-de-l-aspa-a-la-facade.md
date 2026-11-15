# Le barème de l'ASPA à la façade : les deux tests des référents qui posaient un barème à la main le lisent sur une copie des données

Action 161, étape 5h, après `2026-11-15-la-pension-maximale-a-la-facade.md`,
« Ce qui reste », 2. Aucune règle, aucune donnée du dépôt, aucun témoin n'a
bougé. La suite complète de GitHub était verte sur `65cc935` ; celle de
`19323a5` tournait encore à l'envoi.

## Ce qui est fait

- **`test_referents.py`** (2 → 0 marqués, 14 cas) : les deux tests de l'ASPA
  de Saphir et d'EUROMOD prêtaient au moteur Python un barème posé à la main
  (`_BaremeDeSaphir`, `_Bareme`, sous un `SimpleNamespace`). Une aide,
  `_sur_un_bareme`, récrit dans une copie des données
  (`facade.donnees_retouchees`) la ligne de l'année de
  `minimum_vieillesse.csv` et de `minimum_vieillesse_couple.csv`, celles
  seules qui diffèrent du dépôt ; le simulateur de la façade, sous
  `Parametres(racine_donnees=…)`, sert l'étape « foyer et net » au portage.
  Sans la copie, huit des quatorze cas rougissent : le barème retouché est
  bien celui qui est lu.
- Le fichier n'a plus de test marqué : il quitte `RESTES` de
  `tests/test_fichiers_sur_le_moteur_python.py`, et la fixture
  `entrees_du_test` ses imports.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide`,
`test_referents.py`, `test_fichiers_sur_le_moteur_python.py`.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Les confrontations des deux moteurs gardent leur marque, comme le solveur
   `niveau_pour_pension` (`test_simulateur.py`) et `Saisies.simuler`
   (`test_reversion.py`).
2. Les autres tests marqués de `RESTES` qui ne sont pas des confrontations,
   chacun avec ce qui lui manque : `points_msa`
   (`test_pension_minimum_avant_1983.py`), l'échéancier
   (`test_minima_agricoles.py`, `test_majoration_exceptionnelle.py`),
   `liquider_les_departs` et les pensions déjà servies (`test_departs.py`),
   les fins de charge et les étapes imbriquées
   (`test_majoration_enfants_a_charge.py`). L'étape suivante peut commencer
   par `points_msa`, une règle de plus à servir par `Regles`.
