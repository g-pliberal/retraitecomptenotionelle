# L'invalidité à la façade : `test_invalidite.py` quitte le moteur Python, cinq règles de plus servies

Vingt-septième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-faire-vivre-a-la-facade.md`, « Ce qui reste », 1. Aucune règle,
aucune donnée, aucun témoin n'a bougé. La suite complète de GitHub était
verte sur `d66bbc2` ; celle de `a4578a0` tournait au début de l'étape.

## Ce qui est mesuré

Les imports basculés, le fichier a dit ce qui lui manquait (le test vu
rouge) :

- le module `invalidite` du droit, que la façade ne servait pas :
  `age_de_l_aspa`, `categorie_de_la_pension`, `plancher_de_la_substitution`,
  `rente_viagere_d_invalidite` ;
- `ouvrir.age_taux_plein_droit` (le départ des handicapés) ;
- `Simulateur.revalorisations`, qu'un test marqué lisait sur le simulateur de
  la façade : le fixture `simulateur` du fichier passe à
  `facade.simulateur_du_test`, qui rend le jumeau aux tests marqués ;
- un `float("inf")` passé à `revalorisations_pensions.generale` : le pont
  l'écrit `Infinity`, que le JSON de node refuse. Le test passe `None`, sans
  changer la valeur : aucune de ses fenêtres ne traverse janvier 2020, seule
  revalorisation par tranche.

## Ce qui est fait

- **Servies** : `pont.py` déclare le module `invalidite` (quatre règles) et
  `ouvrir.age_taux_plein_droit` ; `pont.mjs` ajoute `invalidite` à ses
  modules du droit ; `tests/facade.py` expose `invalidite` et son jumeau.
- **Leurs tests tirés de la source**, dans `test_facade.py` : l'âge de l'ASPA
  de l'inapte né en 1965 (R. 815-1), la catégorie dite ou présumée
  (L. 341-4), le plancher de l'AVTS de 2022 (L. 341-15, 3 566,43 €), la rente
  viagère au tiers au-delà du seuil (L. 28), le taux plein du handicapé à
  cinquante-cinq ans. Vus rouges avant que le pont ne les serve.
- **Leurs confrontations au jumeau**, dans `test_facade_jumeau.py`, dont le
  plancher de 1982 de deuxième catégorie présumée et celui de première.
- **Les saisies passent à la façade** dans ce fichier : `_simuler` et
  `_simulateur` lisent la saisie par le portage (`Saisies.lire`) et la
  simulent par un simulateur de la façade, au lieu de `Saisies.simuler`.
- **`test_invalidite.py` quitte `FICHIERS`** pour `RESTES` (4 tests
  marqués) : les trois confrontations « les deux moteurs », et les
  majorations de 1972 à 1977, qui font vivre un résultat retouché
  (`sur_la_duree_maximum`) que le portage ne refait pas.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. `test_majoration_exceptionnelle.py` (l'échéancier, `PetitePension`) et
   `test_departs.py` (le module `departs`, ses départs et ses demandes).
2. Le test marqué de `test_liquidation.py` sur « faire vivre », puis les 37
   tests marqués de `test_simulateur.py`.
3. `Saisies.simuler` et `Saisies.simulateur`, qui font encore tourner le
   moteur Python sans que la liste des fichiers le voie : `test_reversion.py`
   s'en sert encore.
