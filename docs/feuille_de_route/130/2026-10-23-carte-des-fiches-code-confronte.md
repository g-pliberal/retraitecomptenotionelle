# La carte des fiches : le code de chaque fiche confronté au dépôt, premiers lots

**La demande.** Vague du 22 octobre 2026, seconde salve : la session de suivi
« Qu'est-ce qu'il reste à faire ? » lance, sur la demande du propriétaire
(« Lance une session par action qui n'a pas besoin de moi »), la session de
l'action 130, seule, après les cinq de la première salve. Son point, celui que
le bloc « Reprise » plaçait après la vague : le test du code étendu à toutes
les fiches (`130/2026-10-19-carte-des-fiches-presque-mures.md`, « Ce que
l'étape laisse »), dont la plupart écrivaient le leur en prose. Le test ne
part jamais rouge sur `main` : il s'étend par lots, sous un cliquet. Aucun
chiffre du modèle ne bouge : seuls changent le champ `code` de 79 fiches et
les tests de la carte.

## Ce qui est fait

- **Le cliquet**, `test_le_code_de_chaque_fiche_tient`
  (`tests/test_carte.py`) : `outils_carte.ecarts` passe sur toute fiche qui a
  un code, hors de `EN_PROSE`, la liste de celles qui l'écrivent encore en
  prose, 148 au départ (la note du 19 en comptait 146). La liste ne fait que
  maigrir : une fiche qui tient doit en sortir, et le test l'a vu rouge quand
  dix fiches récrites y restaient.
- **Ce que l'outil lit de neuf** (`tests/outils_carte.py`), que
  `test_le_code_d_une_fiche_se_confronte_au_depot` a vu rouge forme par
  forme. Un nom de moteur peut être une constante de module ou un accesseur
  `get` du JavaScript, et non plus seulement une fonction, une classe ou une
  méthode. Les paramètres s'écrivent en clauses que sépare « ; » : celle des
  versions, entière, que toute fiche dont les versions en portent doit avoir ;
  des champs de fiches de régime ; des fichiers des données de référence
  (`legislation/`, `macro/`, les séries CSV de `regimes/`) et, s'il le faut,
  leurs clés pointées, leurs colonnes ou ce qu'une ligne mesure, valeur de sa
  première colonne ou de sa colonne `mesure` ; ou « aucun », seul. Des
  versions dont les paramètres sont une phrase, et non une table — le contrat
  laisse `contenu` libre —, n'en exigent aucun.
- **Une convention pour la prose**, que les sept lots ont suivie. Les quatre
  champs que l'outil lit ne gardent que des noms. Ce qui disait comment le
  moteur s'en sert, ou d'où vient une donnée, passe au champ `moteur`, en
  phrases, avec les champs de classe que l'outil ne lit pas
  (`PensionRegime.ecretement_du_maximum`, `Durees.assimilees`). Une glose qui
  ne faisait que redire l'en-tête d'un fichier nommé tombe ; « le paquet du
  site porte ses versions » ne se dit que des fiches que `moteur/donnees.json`
  porte (`fiches_datees`, `versions_des_fiches`), vérifiées. Un fichier
  JavaScript nommé sans fonction reçoit les jumeaux des noms Python de son
  pair, par la convention de nommage, chacun vérifié ; une phrase qui
  désignait des appelants (« où l'ASPA s'ouvre », « ses appels ») cède la
  place aux fonctions qui appellent, relevées dans chaque moteur.
- **Sept lots**, de 148 à 69 fiches en prose, chacun commité au vert et
  publié : 11, 15, 11, 12, 12, 10 et 8 fiches. La récriture a corrigé ce que
  la prose disait de faux : `ScenarioActuel.simuler`, qui n'existe pas
  (`calculer`, et `_sousLeDroit` dans le portage, appellent le foyer) ;
  `Compte._bornes_proratisees`, qui est à `ConstructeurCompte` ;
  `PensionRegime`, dans `droit/commun.py` et non `droit/liquider.py` ;
  `_fonction_publique_quittee`, sans tiret bas ; la classe `PensionServie`
  des départs, que le portage n'a pas, la pension servie y étant l'objet que
  `liquiderLesDeparts` bâtit.

La récriture s'est faite par un outil de session, hors du dépôt : il remplace
les sous-champs du bloc `code:` dans le texte même de la fiche, en `>-` à
88 colonnes, puis vérifie au chargement que rien d'autre n'a bougé.
`conservation.py --depuis HEAD` n'a rien vu de perdu à aucun lot. L'index
LEGI n'a pas été remis à jour : l'étape n'écrit aucune règle du scénario 1,
et le journal de veille n'a pas d'entrée.

## Ce que l'étape laisse

- Les 69 fiches de `EN_PROSE`. 46 n'ont pour code que leur phrase `moteur`,
  avec leurs interrupteurs pour 42 d'entre elles et leurs tests pour deux :
  leurs fonctions et leurs paramètres sont à écrire, le plus long. 17 l'écrivent encore en prose dans les trois
  champs, dont la retraite progressive et le cumul, le minimum contributif,
  les carrières hors de France et la seconde pension. 6 nomment des tests
  sans fichier : les trois du chômage des complémentaires, les fractions des
  cultes, la majoration pour enfants de l'Ircantec, les services passés
  outre-mer. `outils_carte.ecarts` dit ce qui manque à chacune.
- Les limites de l'outil : `Classe.méthode` se vérifie nom par nom, non que
  la méthode est de la classe ; un champ de classe ne se nomme pas.
- `code` n'est toujours pas parmi les champs documentaires de `memoire.py`.
- Les 107 fiches à lire au droit, et les points ouverts des phases 2 à 8.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition du sixième domaine, et celle sur
la retraite progressive, le cumul et la seconde pension, README muet.
