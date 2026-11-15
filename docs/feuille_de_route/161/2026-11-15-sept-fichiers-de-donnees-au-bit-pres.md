# Sept fichiers de données au bit près : l'assiette, la TVA, les effectifs, les dépenses, la vie en couple, les caractéristiques et la série annuelle confrontés à leur double, `partFemmes` retiré du portage

Action 161, étape 7c, après `2026-11-15-les-jumeaux-gardes-au-bit-pres.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

- **29 fonctions de plus confrontées au bit près**, toutes identiques, par
  `tests/test_jumeaux_au_bit.py` : quatre d'`assiette.py`, trois de
  `tva.py`, trois d'`effectifs.py`, huit de `depenses.py`, deux de
  `vie_en_couple.py`, six de `caracteristiques.py`, trois de
  `chargement.py` (`brut`, `fiabilite`, `prolongee` de `SerieAnnuelle`,
  sur la dépense totale et les séries des retraités par caisse). Les années
  vont de 1945 à 2080 : avant, dans et après ce qui est publié. 57 fonctions
  ont désormais leur grille.
- **Le test sait davantage** : un genre d'objet de plus par classe de
  données (`CLASSES`), bâti sur `data/` en Python et sur le paquet au
  portage ; des arguments nommés (`Nommes`), passés par leur nom en Python
  et à leur rang au portage ; une table rendue à clés flottantes (les
  assiettes de la TVA) se compare par ses clés écrites.
- **Ce que le paquet ne porte pas reste hors des grilles**, comme à
  l'étape 7b : les caractéristiques des retraités n'y ont que les neuf
  indicateurs que le site lit, et le nom d'une série n'est qu'une étiquette
  de message d'erreur (« total » au portage, « depenses_retraite » en
  Python), que la grille de `prolongee` ne compare pas.
- **`partFemmes` retiré de `moteur/js/distribution.js`** : le site lit
  `partFemmesResidents`. L'écart déclaré tombe avec lui, et l'entrée de la
  liste aussi ; `test_jumeaux.py` l'a vu rougir avant le retrait.

## La relecture des lecteurs

Par leurs appels, et non plus par leurs noms : la liste de l'étape 7a
prenait un `ligne.part_pib` ou un `population.effectif` pour le leur.

- **19 lecteurs corrigés** : `annee_de_reference`, `part_pib`,
  `taux_prelevement` d'`assiette.py`, et `part_pib` de `tva.py`, par
  `cout.py` ; `montant` de chacun, par son propre fichier ; `assiettes`, par
  `tva.py` ; `effectif`, par `castypes.py` ; `serie`, par
  `construire_donnees.py` ; `annees`, `depense`, `fiabilite`, `part_pib`,
  `repartition` de `depenses.py`, et `part` de `vie_en_couple.py`, par
  `cout.py` ; `reversion`, par `avantages.py` ; `valeur` des
  caractéristiques, par `construire_donnees.py` ; `fiabilite` de la série,
  par `depenses.py` ; `prolongee`, par `macro.py`.
- **15 fonctions passent au moteur** : aucun fichier qui reste ne les
  appelle. `fiabilite` et `poste` de l'assiette, `fiabilite` de la TVA et
  des effectifs ; `fiabilite_minimale_sur` de la série, que seule
  `fiabilite_sur` de `macro.py`, déjà au moteur, appelle ; les quatre
  méthodes gardées d'`indemnite_csg.py` et les six de `primes.py`, que
  seuls `remuneration.py`, `droit/` et `moteur/compte.py` appellent. Leurs
  chargeurs restent : la fabrique en tire le paquet.

La liste compte 148 fonctions gardées, dont 58 confrontées (57 ici, et
`en_mois` par `test_moteur.py`), et 89 au moteur.

## Ce qui reste

1. **Les grilles des 90 autres fonctions gardées**, avec la même relecture,
   dans `calendrier.py`, `config.py`, `contexte.py`,
   `contributions_equilibre.py`, `bilan.py`, `equilibre.py`, `macro.py`,
   `prelevements_historiques.py`, `regimes.py` et `frontiere.py`. `bilan.py`
   lit un bilan figé, bâti d'un dictionnaire des deux côtés. Un argument
   `dict` part au portage en objet, et non en `Map` : une fonction qui
   attend une `Map` demandera un moyen d'en bâtir une par le pont. Puis la
   colonne `test` rendue obligatoire dans `jumeaux.ecarts_de_la_liste`.
2. Le lecteur de `taux_au` de `config.py` est `primes.py`, qui ne nomme
   que sa propre `taux_au` : à relire avec `config.py`.
3. Puis le retrait des règles du moteur Python, avec les fonctions
   `au_moteur` ; puis les périodes assimilées du relevé.

**Tests.** `tests/test_jumeaux_au_bit.py` (59, un écart attendu) et
`tests/test_jumeaux.py` (21) ; `python -m pytest -m rapide` : 5 311
passés, un écart attendu.
