# Les points MSA à la façade : l'escalier de R. 732-71 servi par le portage

Action 161, étape 5i, après `2026-11-15-le-bareme-de-l-aspa-a-la-facade.md`,
« Ce qui reste », 2. Aucune règle, aucune donnée du dépôt, aucun témoin n'a
bougé. La suite complète de GitHub était verte sur `19323a5` ; celle de
`a08f52e` tournait encore à l'envoi.

## Ce qui est fait

- **`acquerir.points_msa`** rejoint `pont.REGLES_DE_LA_FACADE`, à côté de
  `points_msa_retenus` : `pointsMsa` de `moteur/js/droit/acquerir.js` le sert,
  sur le moteur d'un simulateur de la façade et une période de son catalogue.
- **`test_facade_jumeau.py`** : sept appels confrontés au jumeau, sous les
  deux jeux de paramètres — les quatre marches de l'escalier en 2025 (5 000,
  7 500, 12 000, 20 000 et 40 000 €), le plafond (47 100 €), où le maximum lit l'AVTS,
  et une année d'avant la série de l'AVTS (2002).
- **`test_pension_minimum_avant_1983.py`** (2 → 1 marqué) : le test du
  maximum de R. 732-70 lit la période et le plafond sur le simulateur de la
  façade, et non plus sur son moteur ; il garde ses valeurs (113 points,
  l'AVTS de 2025 et de 2015). Reste marquée la confrontation des deux moteurs.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide`,
`test_pension_minimum_avant_1983.py`, `test_fichiers_sur_le_moteur_python.py`,
`test_facade.py`, les tests des règles de `test_facade_jumeau.py`.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Les confrontations des deux moteurs gardent leur marque, comme le solveur
   `niveau_pour_pension` (`test_simulateur.py`) et `Saisies.simuler`
   (`test_reversion.py`).
2. Les autres tests marqués de `RESTES` qui ne sont pas des confrontations :
   l'échéancier posé à la main (`test_minima_agricoles.py`,
   `test_l_echeancier_inscrit_le_relevement_a_sa_date` ;
   `test_majoration_exceptionnelle.py`, qui veut aussi un simulateur sans la
   fiche, une copie des données retouchée), `liquider_les_departs` et les
   pensions déjà servies (`test_departs.py`), les fins de charge et les étapes
   imbriquées (`test_majoration_enfants_a_charge.py`). L'étape suivante peut
   commencer par les deux tests de l'échéancier.
