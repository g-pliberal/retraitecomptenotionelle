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
- **À surveiller à GitHub** : `castypes.primes_projetees` appelle
  `avec_lignes`, une méthode des règles, sur la carrière des cas types sous
  `conventions_cor`. Sur le simulateur Python, la carrière reste celle des
  règles ; aucun test lancé ici ne lui passe une carrière du pont.

**Ce qui reste** : la suppression des fichiers de règles, qui attend l'accord
final du propriétaire.
