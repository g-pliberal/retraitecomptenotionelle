# La bascule de la carrière : le pont rend la carrière nue

Action 161, morceau 4 du plan de `2026-11-17-la-facade-transmet-la-carriere-nue.md`,
mené le 17 novembre 2026, sur la consigne du propriétaire d'avancer sans
pause ce qui ne demande pas son avis. Aucune règle, aucune donnée, aucun
fichier de `moteur/` n'est touché, aucune valeur attendue ne change, aucun
code Python n'est supprimé.

- **La bascule.** `pont.carriere_des_donnees` bâtit la carrière sous le type
  nu (`types_du_pont.carriere.Carriere`) au lieu de la classe des règles
  (`carriere.Carriere`), qu'il n'importe plus.
- **Mesuré d'abord** : 8 échecs sous `-m rapide`, ceux que la note de la
  traîne comptait (le test des copies de la chronologie était passé à
  l'égalité par un autre fil).
- **Les épingles de la classe** suivent : `test_pont.py`,
  `test_le_portage_bat_les_carrieres_de_la_grille`, et quatre tests de
  `test_facade.py` vérifient le type nu. Le test qui épingle la classe des
  règles sous la marque `sur_le_moteur_python` ne bouge pas.
- **Le jumeau** (`test_facade_jumeau.py`) : le simulateur Python reçoit la
  carrière du pont recopiée champ à champ sous la classe des règles
  (`_des_regles`), car il lit `prolongee` et `date_entree` sur elle ; la mise
  à plat des résultats reconnaît la carrière par le type nu, dont la classe
  des règles hérite, pour l'écrire comme le pont.
- **Les vérifications.** `python -m pytest -m rapide` : vert (5 701) ;
  `test_facade_jumeau.py` entier, parts comprises : vert (258) ;
  `test_pont.py`, `test_facade.py`, `test_jumeaux.py`, `test_chronologie.py` :
  verts (402) ; `test_simulateur.py`, les confrontations légères et les
  tests du cycle de vie : verts (798).
- **La projection des primes des cas types** (`castypes.primes_projetees`,
  sous `conventions_cor`) appelait `avec_lignes`, une méthode des règles, et
  levait `AttributeError` sur une carrière du pont. Le test
  `test_les_primes_des_cas_types_se_projettent_sur_la_carriere_du_pont`
  (`test_facade.py`), à la formule de la docstring, vu rouge ; la projection
  passe par `dataclasses.replace`, qui recopie les mêmes champs qu'
  `avec_lignes`. Verts ensuite : `-m rapide` (5 702), le pont, la façade, le
  simulateur, le cycle de vie, les confrontations légères (1 128).

**Ce qui reste** : la suppression des fichiers de règles, qui attend l'accord
final du propriétaire.
