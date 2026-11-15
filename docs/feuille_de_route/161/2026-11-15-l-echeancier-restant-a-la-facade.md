# L'échéancier restant à la façade : le relèvement des exploitants et la majoration exceptionnelle

Action 161, étape 5j, après `2026-11-15-les-points-msa-a-la-facade.md`,
« Ce qui reste », 2. Aucune règle, aucune donnée du dépôt, aucun témoin n'a
bougé. La suite complète de GitHub était verte sur `19323a5` ; celles de
`a08f52e` et de `04d0bec` tournaient encore à l'envoi.

## Ce qui est fait

- **L'échéancier de la façade rend sa réversion** : `echeancierTelQuel`
  (`pont.mjs`) écrit celle qu'il liquide au décès de l'assuré,
  `echeancier_des_donnees` (`pont.py`) la lit par `reversion_des_donnees`,
  et `facade.Echeancier.reversion` la porte, sous le dataclass du Python, ou
  `None`.
- **`test_minima_agricoles.py`** (3 → 2 marqués ; il quitte `FICHIERS`, qu'il
  n'importe plus du moteur) : `test_l_echeancier_inscrit_le_relevement_a_sa_date`
  parcourt l'échéancier de la façade. « Faire vivre » ne reçoit que le
  résultat que le moteur de la façade a rendu : le test vérifie que le départ
  de l'échéancier est ce résultat (`echeancier.au_depart == calculer(carriere)`),
  puis le fait vivre.
- **`test_majoration_exceptionnelle.py`** (2 → 1) : le simulateur « sans la
  fiche » est celui d'une copie des données (`facade.donnees_retouchees`) où la
  version d'avant septembre 2023 dit `existe: false` ; `majorerLesPetitesPensions`
  passe une fiche absente et une règle qui n'existe pas de la même façon. Le
  test vérifie en plus que l'échéancier témoin n'inscrit pas la majoration.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide`, `test_pont.py`,
`test_facade.py`, `test_fichiers_sur_le_moteur_python.py`, les deux fichiers,
`test_liquidation.py`, `test_reversion.py` et les confrontations légères.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Les confrontations des deux moteurs gardent leur marque, comme le solveur
   `niveau_pour_pension` (`test_simulateur.py`) et `Saisies.simuler`
   (`test_reversion.py`).
2. Les autres tests marqués de `RESTES` qui ne sont pas des confrontations :
   `liquider_les_departs` et les pensions déjà servies (`test_departs.py`),
   les fins de charge et les étapes imbriquées
   (`test_majoration_enfants_a_charge.py`). L'étape suivante peut commencer
   par `test_departs.py`.
