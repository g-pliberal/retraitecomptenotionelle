# La garantie et les durées posées à la façade : cinq tests de plus quittent le moteur Python

Action 161, étape 5e, après
`2026-11-15-la-proposition-et-la-mortalite-a-la-facade.md`, « Ce qui
reste », 1. Aucune règle, aucune donnée, aucun témoin n'a bougé. La suite
complète de GitHub était verte sur `18813a2`, l'étape précédente.

## Ce qui est fait

- **Une constante lue au portage** (`pont.CONSTANTES_DE_LA_FACADE`,
  `pont.constante_du_droit`, entrée `droit.constante` de `pont.mjs`) :
  `liquider.SURCOTE_AGE_MAJORE`, que `droit/liquider.js` exporte désormais.
  La façade la sert sous le module `liquider`, où le jumeau ne la tient pas.
- **Deux marques d'argument** : `pont.SALAIRE_MOYEN`, le salaire moyen des
  séries du simulateur en fonction de l'année, que `grilles.forfait` reçoit
  (table servie de plus, `TABLES_DE_LA_FACADE`) ; `pont.DureesPosees`, des
  trimestres par régime posés par le test, que
  `liquider.duree_majoree_apres_taux_plein` (règle servie de plus) lit en
  `Map`.
- **La garantie vieillesse du scénario 6** : `simulateur.scenario_liberal.
  _garantie_vieillesse`, entrée `simulateur.garantie_vieillesse`, lue sous
  `GarantieVieillesse`.
- **La liquidation de la façade rend davantage** : `pensions.regimes` et
  `pensions.plafonds`, l'étape « liquider » avant les compléments, et
  `complements.regimes` et `complements.avantages`.
- **Leurs tests tirés de la source**, dans `test_facade.py` (le forfait de
  la treizième catégorie des marins en 2024, la circulaire Cnav 2004/20, la
  ligne à 750 € du tableau de la proposition, L. 17), vus rouges ; leurs
  confrontations au jumeau, dans `test_facade_jumeau.py`.
- **`test_simulateur.py`** : 5 tests quittent la marque (7 → 2).

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Les deux tests du solveur `niveau_pour_pension` de `test_simulateur.py`,
   qui reçoit une fonction Python : ils peuvent rester sur le Python
   jusqu'au retrait.
2. Les neuf tests marqués de `test_liquidation.py` : le journal, que l'état
   d'une liquidation ne passe pas (3), l'échéancier et `depart_de` (2),
   `pilote.age_de_depart` (3), une confrontation (1).
3. `Saisies.simuler` et `Saisies.simulateur` (`test_reversion.py`).
4. L'échéancier à la façade (`Echeancier.parcourir`).
