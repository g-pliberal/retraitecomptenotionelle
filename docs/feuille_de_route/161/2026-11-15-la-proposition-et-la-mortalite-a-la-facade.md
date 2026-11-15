# La proposition et la mortalité à la façade : huit tests de plus quittent le moteur Python

Trentième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-le-simulateur-a-la-facade.md`, « Ce qui reste », 1. Aucune
règle, aucune donnée, aucun témoin n'a bougé. La suite complète de GitHub
était verte sur `d7878fb`, l'étape précédente.

## Ce qui est mesuré

Les quinze marques de `test_simulateur.py` retirées d'une copie : onze tests
échouaient, sur ce que la façade ne sert pas (`scenario_liberal`,
`pour_la_projection`, `mortalite`, `grilles`, `scenario_notionnel`,
`proposition`, `carriere_proposition`, `duree_majoree_apres_taux_plein`, une
règle du Python qui lit `affiliations`) ; quatre passaient, mais sur le
Python (`_coefficient_anticipation` importé du jumeau, la constante
`SURCOTE_AGE_MAJORE`, et le solveur `niveau_pour_pension`, qui reçoit une
fonction Python).

## Ce qui est fait

- **Deux règles servies** (`pont.REGLES_DE_LA_FACADE`) :
  `liquider._coefficient_anticipation`, que `droit/liquider.js` exporte
  désormais pour la façade, et `acquerir.points_msa_retenus`, un module de
  plus (`MODULES_DU_DROIT`). Le module `acquerir` de la façade sert ses
  règles déclarées comme un module de règles.
- **Trois entrées** (`pont.mjs`, `pont.py`, `tests/facade.py`) :
  `simulateur.proposition`, `simulateur.carriere_proposition` et
  `carriere.prolongee` (`facade.prolongee`, la carrière étant un type du
  pont, sans méthode servie). Une carrière que le portage rend inchangée
  revient `null`, et la façade rend celle qu'elle a reçue, la même.
- **La mortalité du simulateur** (`simulateur.mortalite`) : ses quotients
  observés lus par leur chargeur Python, des données ;
  `survie_annuelle` servie par le portage (`pont.MORTALITE_DE_LA_FACADE`,
  entrée `simulateur.mortalite`).
- **`pour_la_projection`**, sur le simulateur de la façade : un autre
  simulateur de la façade, sous les conventions du COR et sans le minimum
  vieillesse au scénario 1 ; ce ne sont que des paramètres.
- **Leurs tests tirés de la source**, dans `test_facade.py` : l'exemple de
  l'Agirc-Arrco (0,88 et 0,83) ; les seize points de R. 732-73 ; le quotient
  de 1950 de Vallin et Meslé, 0,051121 ; le départ reporté à 65 ans, en
  2035 ; la carrière prolongée. Vus rouges.
- **Leurs confrontations au jumeau**, dans `test_facade_jumeau.py`.
- **`test_simulateur.py`** : 8 tests quittent la marque (15 → 7). Deux sont
  récrits : la marche du milieu de l'année lit le scénario 3 par
  `simuler`, et le report compare la carrière des autres scénarios par
  égalité, la façade la rendant relue.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Les sept tests marqués de `test_simulateur.py` :
   `scenario_liberal._garantie_vieillesse` ; la liquidation du minimum
   garanti, qui lit les pensions avant compléments, leurs plafonds et leurs
   compléments, que `liquidation.liquider` de la façade ne rend pas ;
   `grilles.forfait`, qui reçoit une fonction Python du salaire moyen ;
   `duree_majoree_apres_taux_plein`, qui reçoit des durées
   (`trimestres_par_regime`) que le pont ne passe pas ; la constante
   `SURCOTE_AGE_MAJORE`, que le portage n'exporte pas ; les deux tests du
   solveur `niveau_pour_pension`.
2. Les neuf tests marqués de `test_liquidation.py`.
3. `Saisies.simuler` et `Saisies.simulateur`, qui font encore tourner le
   moteur Python (`test_reversion.py`).
4. L'échéancier à la façade (`Echeancier.parcourir`).
