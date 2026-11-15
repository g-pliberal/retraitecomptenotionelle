# Les autres oracles à la façade : deux règles et deux méthodes de table de plus servies, quatre fichiers quittent le moteur Python

Vingt-cinquième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-l-oracle-a-la-facade.md`, « Ce qui reste », 1 : les quatre autres
fichiers d'oracle. Aucune règle, aucune donnée, aucun témoin n'a bougé. La
suite complète de GitHub était verte sur `8d38a63` ; celle de `fc4c3be`
tournait à la fin de l'étape.

## Ce qui est mesuré

La note précédente lisait dans leurs imports que les quatre fichiers
n'empruntaient que `Simulateur`, `Carriere`, `ouvrir` et `liquider`, que la
façade sert. Les imports basculés, les fichiers ont dit ce qui manquait
(le test vu rouge) :

- `ouvrir.ouverture_carriere_longue` (carrière longue de la fonction
  publique) et `liquider.nombre_d_annees_retenues` (salaire annuel moyen),
  deux règles que `pont.REGLES_DE_LA_FACADE` ne déclarait pas ;
- la table `ages_categorie_active` et sa méthode `derogation` (catégorie
  active, que le fichier lisait encore sur un simulateur Python) ;
- dans le fichier de la carrière longue, `carriere_longue._portes`, méthode
  privée au Python, publique au portage (`portes`), et deux constantes de
  classe, `PORTES_FONCTION_PUBLIQUE_DEPUIS` et `DUREE_FIXE_FONCTION_PUBLIQUE`.

`test_oracle_points_enfants_arrco.py` passait tel quel.

## Ce qui est fait

- **Deux règles et deux méthodes de table servies** : `pont.py` les déclare ;
  `pont.mjs` sert une méthode de table privée au Python sous son nom sans le
  tiret bas, comme il le faisait déjà des règles (`_cumuler`).
- **Leurs tests tirés de la source**, dans `test_facade.py` : les 57 ans de
  la catégorie active de 1960 (loi n° 2010-1330), les dix-sept années de la
  génération 1940 (décret n° 93-1022), la seule porte de 59 ans ouverte aux
  fonctionnaires en 2005 (L. 25 bis), l'ouverture à 15 + 174/4 ans du
  fonctionnaire de 1955 entré à quinze ans (D. 16-1, II). Vus rouges avant
  que le pont ne les serve.
- **Leurs confrontations au jumeau**, dans `test_facade_jumeau.py`
  (`APPELS_DES_TABLES`, `APPELS_DES_REGLES`).
- **Les deux constantes se lisent au portage**, qui fait foi : une fixture du
  fichier d'oracle les demande à `CarriereLongue` de `moteur/js/regimes.js`,
  par node, et les confronte au texte, comme le Python l'était.
- **Les quatre fichiers quittent `FICHIERS`** : aucun test n'y entre plus
  dans le moteur Python.

## Un écart relevé, laissé

`_portes` ne range pas ses portes de même des deux côtés : le Python les
trie par génération de la ligne puis par porte, le portage par âge maximal
d'entrée. Les appelants n'en font qu'un ensemble ou les parcourent toutes ;
le fichier d'oracle compare des ensembles. Les confrontations au jumeau
s'en tiennent donc aux appels d'une porte ou d'aucune. Ranger le portage
comme le Python toucherait une règle du scénario 1 : la session ne l'a pas
fait, et le signale.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`
(note précédente) : ils restent, marqués.

## Ce qui reste

1. « Faire vivre » servi ouvre la voie aux fichiers qui l'appellent :
   `test_departs.py`, `test_invalidite.py`, `test_pension_maximale.py`,
   `test_majoration_*`, `test_pension_minimum_avant_1983.py`, et le test
   marqué de `test_liquidation.py`. Mesurer d'abord, en basculant les
   imports et en lançant le fichier, ce qui manque vraiment : un import ne
   dit pas un calcul, et la liste lue dans les imports ne dit pas tout ce
   qu'un fichier lit d'une table.
2. Les 37 tests marqués de `test_simulateur.py`.
