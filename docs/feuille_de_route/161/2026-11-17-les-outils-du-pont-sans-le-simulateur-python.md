# Les outils du pont sans le simulateur Python : le deuxième lot de la suppression

Action 161, deuxième des quatre lots que décrit
`2026-11-17-l-essai-a-blanc-de-la-suppression.md`, mené le 17 novembre 2026.
Aucune règle, aucune donnée, aucune valeur attendue ne change ; aucun
fichier de règles n'est encore supprimé.

## Fait

`tests/outils_pont.py` n'importe plus rien d'un fichier de règles, et quitte
`IMPORTEURS_DES_REGLES` (`tests/test_fichiers_sur_le_moteur_python.py`) :

- **`Saisies`** bâtit par défaut le simulateur de la façade des tests
  (`facade.Simulateur`, importé à l'appel), et rend la carrière nue du pont.
  La copie sous la classe des règles (`des_regles`) est partie : la façade
  reçoit la carrière nue depuis l'étape où elle la transmet. Les quinze
  fichiers qui appelaient `Saisies()` sans fabrique passent ainsi par la
  façade sans changer d'une ligne ; ceux qui lui passaient
  `facade.Simulateur` la gardent.
- **Les gardes des jumeaux du coût** (`JUMEAUX_DU_COUT`,
  `empecher_les_jumeaux_du_cout`, `jumeaux_qui_datent_et_batissent`) sont
  retirées, et leurs appels dans douze tests : elles empêchaient de calculer
  des fonctions que la suppression emporte. `interdire` reste, outil
  générique : `test_grille_large.py` s'en sert encore pour empêcher les
  constructeurs Python de la grille élargie de bâtir une carrière.
- **`actuel_en_donnees`**, que seul `test_facade_jumeau.py` appelait, y est
  déplacé ; il partira avec lui au quatrième lot.

Les docstrings des tests qui disent encore « qu'on empêche ici de
calculer » relèvent des mentions que le quatrième lot reprend.

**Tests.** Un test neuf,
`test_les_saisies_des_tests_simulent_par_la_facade_sur_la_carriere_nue`, et
la liste des importeurs raccourcie, vus rouges avant le changement, verts
après ; `test_droits_contrefactuels.py` attend le refus d'un droit
inconnu du portage, au calcul, et non plus du moteur Python, à sa
construction. `python -m pytest -m rapide` : 5 709 réussis ; toute la suite
se charge (9 290 tests) ; les fichiers touchés et ceux qui bâtissent des
`Saisies` passent, le témoin des valeurs refait à l'identique.

## Ce qui reste

Quatre fichiers importent encore des règles : `tests/facade.py`,
`tests/jumeau_des_avantages.py` (qui tient désormais la copie sous la
classe des règles), `tests/test_facade.py` et `tests/test_facade_jumeau.py`.
Les lots 3 (la façade des tests sans les modules de règles) et 4 (la
suppression), tels que les décrit la note de l'essai à blanc.
