# Les jumeaux gardés au bit près : un test paramétré confronte chaque fonction gardée de la mortalité, de la courbe des taux, du patrimoine et de la distribution à son double, et la relecture de leurs lecteurs en renvoie six au moteur

Action 161, étape 7b, après `2026-11-15-la-liste-des-fonctions-gardees.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

- **Le test** : `tests/test_jumeaux_au_bit.py`,
  `test_la_fonction_gardee_rend_la_meme_valeur_des_deux_cotes`, paramétré
  par `GRILLES` : pour chaque fonction gardée, les objets qui la portent et
  ses arguments. Le Python est bâti sur `data/`, le portage sur le paquet du
  contexte du site (`web/site.py`), et chaque appel se compare au bit près
  (tolérance du moteur Python : nulle sous Linux x86_64). Un nombre vaut un
  nombre, entier ou flottant, puisque JSON écrit « 0 » pour 0.0 ; un objet
  rendu (une loi de Makeham, un placement, une distribution) se compare par
  ses champs. 29 fonctions, trois secondes, dans la suite rapide.
- **La réciproque** : `test_chaque_grille_est_declaree_dans_la_liste_et_reciproquement`
  exige la colonne `test` de la liste pour chaque fonction qui a sa grille,
  et pour elles seules. `test_l_ecart_d_un_bit_se_voit` éprouve la
  comparaison au dernier bit.
- **27 fonctions identiques au bit** sur leurs grilles : les six de
  `taux.py` (sans prime et avec 0,6 point à trente ans), seize de
  `mortalite.py` (lois de 1940 à 2130, cellules, courbes par sexe,
  unisexes, de génération ou du moment, par population), six de
  `patrimoine.py`, `part_sous` de `distribution.py` pour les trois sexes.

## Les deux écarts déclarés

Ils sont dans `ECARTS_DECLARES`, attendus rouges (`xfail` strict) : la suite
rougit le jour où les deux exemplaires se rejoignent.

- **`DonneesMortalite.populations`** : 24 en Python, 21 au portage. Le
  paquet ne porte pas les trois populations de la CNAV publiées à plusieurs
  âges, dont seul le coût lit les facteurs par tranche. Voulu ; les grilles
  de la mortalité s'en tiennent aux populations du paquet.
- **`part_femmes`** : 52,8 % en Python, sur tous les retraités, 54,0 % au
  portage, sur les résidents en France du paquet. `partFemmes` n'a aucun
  lecteur dans le portage, qui lit `partFemmesResidents` : c'est du code
  mort, à retirer du JavaScript (l'entrée de la liste tombe alors d'elle-même).

La distribution des pensions se confronte bâtie sur les résidents en France
(`residence="france"`), comme la fabrique l'écrit au paquet.

## La relecture des lecteurs

Lue par les appels, non plus par les noms, pour les quatre fichiers.

- **Six lecteurs corrigés** : `prime` est lue par `taux.py` même (la
  `prime` de `trajectoire.py` est une variable) ; `courbe` de la mortalité,
  `distribution` et `grille` du patrimoine, par `cout.py` ; `annee` du
  patrimoine, par `construire_donnees.py` ; `forme`, par `patrimoine.py`.
- **Six fonctions passent au moteur** : aucun fichier qui reste ne les
  appelle. `DonneesMortalite.fiabilite` (lue par `moteur/conversion.py`
  seul), `DonneesMortalite.survie`, `DistributionPatrimoine.couverture`, et
  ce que seule `couverture` appelait, `_esperance_min_quantiles`,
  `_esperance_min_lognormale`, `repartition_normale`. Elles partent avec le
  moteur Python ; leurs doubles restent au portage, qui les sert au site.

La liste compte désormais 164 fonctions gardées et 74 au moteur.

## Ce qui reste

1. **Les grilles des 135 autres fonctions gardées** (les 20 autres paires :
   `calendrier.py`, `config.py`, `contexte.py`, `donnees/equilibre.py`…),
   avec la même relecture de leurs lecteurs, par lots de quelques fichiers.
   Les accesseurs de données (`fiabilite`, `montant`, `serie`) se
   confrontent comme les calculs, sur leurs années. Puis la colonne `test`
   rendue obligatoire dans `jumeaux.ecarts_de_la_liste`.
2. Le retrait de `partFemmes` du portage, qui n'a pas de lecteur.
3. Puis le retrait des règles du moteur Python, avec les fonctions
   `au_moteur` ; puis les périodes assimilées du relevé.

**Tests.** `tests/test_jumeaux_au_bit.py` (31) et `tests/test_jumeaux.py`
(21) ; `python -m pytest -m rapide` : 5 282 passés, 2 écarts attendus.
