# L'échéancier et les départs à la façade : la majoration des petites pensions et le module des départs servis par le portage, deux fichiers y passent

Vingt-huitième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-l-invalidite-a-la-facade.md`, « Ce qui reste », 1. Aucune règle,
aucune donnée, aucun témoin n'a bougé. La suite complète de GitHub était
verte sur `c45ab4d`, l'étape précédente.

## Ce qui est mesuré

Les imports basculés, chaque fichier a dit ce qui lui manquait (le test vu
rouge) :

- `test_majoration_exceptionnelle.py` : `revalorisation.majorer_les_petites_pensions`
  et la règle de chaque régime qu'elle reçoit (`PensionServie`), que la
  façade ne servait pas, et l'échéancier ;
- `test_departs.py` : le module `departs` du droit (`age_legal`, `departs`,
  `demandes`, `departs_et_demandes`), ses types de données (`Depart`,
  `DemandeExaminee`), et
  `Simulateur.echeancier` ;
- le pont ne savait lire ni écrire un ensemble (`frozenset`, les régimes
  d'un départ).

## Ce qui est fait

- **Servi** : l'entrée `revalorisation.majorer_les_petites_pensions`
  (`pont.mjs`, `pont.py`), qui rend les régimes servis et le calcul de la
  caisse ; la façade (`tests/facade.py`) la sert sous le nom du Python, avec
  `PensionServie`, une marque du simulateur, et refuse un moteur et une règle
  de deux simulateurs, ou des avantages appliqués, qu'elle ne transmet pas.
  Le module `departs` : quatre règles déclarées dans `REGLES_DE_LA_FACADE`,
  et ses deux types de données, portés par la façade comme ceux de la
  liquidation ; les autres types d'un module restent refusés.
  `lu_strictement` lit un `frozenset`, et `_en_donnees` écrit un ensemble en
  liste triée. La façade expose `Echeancier`, qui refuse, pour qu'un test
  marqué en reçoive le jumeau.
- **Leurs tests tirés de la source**, dans `test_facade.py` : l'exemple 3 du
  3.2.5 de la circulaire Cnav n° 2023-21 (87,42 € sous 847,57 €) ; l'âge
  légal de soixante-quatre ans de qui est né en 1970 (L. 161-17-2) et la
  retraite additionnelle du policier qui l'attend (décret n° 2004-569,
  article 6) ; la demande dans un régime sans pension. Vus rouges.
- **Leurs confrontations au jumeau**, dans `test_facade_jumeau.py` : trois
  exemples de la circulaire, et six appels des départs.
- **Les deux fichiers quittent `FICHIERS`** pour `RESTES` : deux tests
  marqués chacun. Pour la majoration, l'échéancier sous un simulateur sans la
  fiche, et la confrontation « les deux moteurs » ; pour les départs,
  `liquider_les_departs` et une liquidation qui voit des pensions déjà
  servies. Deux tests des départs lisent le journal de la simulation
  (`simulateur.simuler(carriere).journal`) au lieu de celui de l'échéancier :
  le même, que la comparaison porte.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Le test marqué de `test_liquidation.py` sur « faire vivre », puis les 37
   tests marqués de `test_simulateur.py`.
2. `Saisies.simuler` et `Saisies.simulateur`, qui font encore tourner le
   moteur Python sans que la liste des fichiers le voie : `test_reversion.py`
   s'en sert encore.
3. L'échéancier à la façade (`Echeancier.parcourir`), puis
   `departs.liquider_les_departs` et l'état d'une liquidation qui voit des
   pensions servies : ils lèveraient les quatre tests marqués de cette étape.
