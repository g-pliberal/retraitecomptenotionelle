# Faire vivre à la façade : quatre fichiers qui appellent « faire vivre » quittent le moteur Python, quatre règles et trois méthodes de table de plus servies

Vingt-sixième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-autres-oracles-a-la-facade.md`, « Ce qui reste », 1.
Aucune règle, aucune donnée, aucun témoin n'a bougé. La suite complète de
GitHub était verte sur `fc4c3be` ; celle de `795a5c1` tournait à la fin de
l'étape.

## Ce qui est mesuré

Les imports basculés, chaque fichier a dit ce qui lui manquait (le test vu
rouge) :

- la table `fiches_datees` et sa méthode `regle` (le maximum des pensions, la
  majoration pour conjoint à charge, la majoration pour enfants à charge) ;
- `minimum_contributif.pension_minimum` et `minimum_contributif.avts` (la
  pension minimum d'avant le 1er avril 1983) ;
- quatre règles : `commun.majoration_du_conjoint`, `commun.date_d_effet`,
  `liquider.pension_maximale`, `liquider.taux_acquis_l_emporte` ;
- « faire vivre » appelé sur `comparaison.actuel` d'une saisie simulée par
  `Saisies` (`tests/outils_pont.py`), dont le simulateur est celui du Python.

## Ce qui est fait

- **Servies** : `pont.py` déclare les trois méthodes de table et les quatre
  règles ; le portage les tenait déjà sous les mêmes arguments.
- **Leurs tests tirés de la source**, dans `test_facade.py` : le barème de la
  Cnav du maximum (40 % du plafond en 1962, 50 % en 2026, aucun en 1948), les
  150es du 1er mars 1975, 4 000 F puis 609,80 € pour le conjoint, les
  11 300 F de 1983, l'AVTS de 2025, la date d'effet du 1er avril 1970, le
  troisième cas de la circulaire n° 22/83. Vus rouges avant que le pont ne
  les serve. `fiches_datees`, que le test des données non servies prenait en
  exemple, y cède la place à `majorations_enfants`.
- **Leurs confrontations au jumeau**, dans `test_facade_jumeau.py`.
- **Les saisies passent à la façade** : dans les deux fichiers des
  majorations, `_simuler` lit la saisie par le portage (`Saisies.lire`) et la
  simule par un simulateur de la façade ; « faire vivre » reçoit le scénario
  1 que ce simulateur refait de la carrière (`scenario_actuel.calculer`),
  celui que le portage refait de toute façon. Les assertions passent
  inchangées.
- **Quatre fichiers quittent `FICHIERS`** pour `RESTES` :
  `test_majoration_conjoint_a_charge.py` (1 test marqué),
  `test_majoration_enfants_a_charge.py` (3), `test_pension_maximale.py` (5),
  `test_pension_minimum_avant_1983.py` (2). Les marqués : les confrontations
  des deux moteurs ; les tests qui remplacent `salaire_de_reference` par
  `monkeypatch` ; `fins_de_charge` sur une carrière de fortune ;
  `parts_de_la_majoration` et `fusionner_les_charges`, dont les étapes
  imbriquées ne passent pas le pont ; `acquerir.points_msa`, règle de
  l'acquisition que la façade ne sert pas.

## Un trou relevé, laissé

`Saisies.simuler` et `Saisies.simulateur` font tourner le moteur Python sans
que la liste des fichiers le voie (« un outil commun »). D'autres fichiers
basculés s'en servent encore (`test_reversion.py`). Les retirer à leur tour
reste à faire, fichier par fichier, comme ici.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue (note précédente).

## Ce qui reste

1. `test_invalidite.py` : le module `invalidite` du droit, que la façade ne
   sert pas (`age_de_l_aspa`, `categorie_de_la_pension`,
   `plancher_de_la_substitution`), la chronologie, et ses saisies.
2. `test_majoration_exceptionnelle.py` (l'échéancier, `PetitePension`) et
   `test_departs.py` (le module `departs`, ses départs et ses demandes).
3. Le test marqué de `test_liquidation.py` sur « faire vivre », puis les 37
   tests marqués de `test_simulateur.py`.
