# Le simulateur à la façade : sept méthodes de tables et le système 1 servi une année, vingt-trois tests quittent le moteur Python

Vingt-neuvième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-l-echeancier-et-les-departs-a-la-facade.md`, « Ce qui reste », 1.
Aucune règle, aucune donnée, aucun témoin n'a bougé. La suite complète de
GitHub était verte sur `c45ab4d` ; celle de `248e31b`, l'étape précédente,
tournait au début de celle-ci.

## Ce qui est mesuré

Les 37 marques de `test_simulateur.py` retirées d'une copie, chaque test a dit
ce qui lui manquait. Vingt et un passaient déjà, mais pas tous par le
portage : trois marques étaient périmées (`carriere_longue._portes`, servie
depuis ; `regimes_interpenetres`, deux tests agricoles qui ne l'atteignent
plus) ; trois tests « `Simulateur.indexation` » bâtissaient le
`ConstructeurCompte` du Python, que la façade sert sous le même nom ; quatre
gardent leur marque (`niveau_pour_pension`, `_coefficient_anticipation`,
`SURCOTE_AGE_MAJORE`) ; les autres instanciaient une table du moteur
Python (`ValeursPoint`, `MajorationsEnfantsPoints`, `AnneesSalaireReference`,
`CoefficientsMinoration`, `AgesAnnulationDecote`) ou importaient
`salaire_moyen_annuel` du Python. Les seize qui échouaient demandaient
`valeurs_point._en_vigueur`, `derniere_annee_servie`, `rendements.rendement`,
`minimum_garanti.ratio_point_indice`, ou une règle du simulateur que la façade
ne sert pas.

## Ce qui est fait

- **Servi** (`pont.TABLES_DE_LA_FACADE`) : `valeurs_point._en_vigueur` et
  `derniere_annee_servie`, `annees_salaire_reference.annees`,
  `coefficients_minoration.coefficient`, `majorations_enfants_points.taux`,
  `rendements.rendement`, `minimum_garanti.ratio_point_indice`. Le portage
  tenait déjà chacune ; `ValeursPoint._enVigueur` y devient `enVigueur`, nom
  public que l'entrée des tables sait appeler (comme `_portes`, `portes`).
- **Servi** : l'entrée `revalorisation.actuel_aujourd_hui` (`pont.mjs`,
  `pont.py`, `tests/facade.py`), le système 1 servi une année, sur le même
  contrôle du résultat que « faire vivre ».
- **Leurs tests tirés de la source**, dans `test_facade.py` : R. 351-29 et
  R. 351-27 ; la fin des points Arrco en 2018 et le forfait de 648 € de la
  circulaire Agirc 2003-9-DRE ; l'article 94 de l'accord du 17 novembre 2017 ;
  les 22,8 % de l'Ircantec des années 1970 ; le point d'indice gelé ; le
  minimum vieillesse de 1997, 42 193 F. Vus rouges.
- **Leurs confrontations au jumeau**, dans `test_facade_jumeau.py`.
- **`test_simulateur.py`** : 22 tests quittent la marque (37 → 15), lisant la
  table du simulateur de la façade (`simulateur.scenario_actuel.valeurs_point`)
  au lieu d'en bâtir une. **`test_liquidation.py`** : le test de « faire
  vivre » aussi (10 → 9).

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Les quinze tests marqués de `test_simulateur.py` : les règles du
   simulateur (`proposition`, `carriere_proposition`, `scenario_liberal`,
   `scenario_notionnel`, `pour_la_projection`, `mortalite`), `droit.liquidation`
   et `droit.acquerir` appelés en Python, `liquider.duree_majoree_apres_taux_plein`,
   `_coefficient_anticipation`, la constante `SURCOTE_AGE_MAJORE`,
   `grilles.forfait`, et le solveur `niveau_pour_pension`, qui reçoit une
   fonction Python et ne passe pas le pont tel quel.
2. `Saisies.simuler` et `Saisies.simulateur`, qui font encore tourner le
   moteur Python (`test_reversion.py`).
3. L'échéancier à la façade (`Echeancier.parcourir`), qui lèverait les tests
   marqués des départs, de la majoration et de la liquidation.
