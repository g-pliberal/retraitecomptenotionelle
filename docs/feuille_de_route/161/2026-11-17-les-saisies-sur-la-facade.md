# Les saisies sur la façade : 125 tests dépendent encore de la carrière des règles, au lieu de 137

Action 161, morceau 2 du plan de `2026-11-17-la-facade-transmet-la-carriere-nue.md`
(le simulateur Python lui-même), mené la nuit du 16 au 17 novembre 2026, sur
la consigne du propriétaire d'avancer ce qui ne demande pas son avis. Aucun
fichier de `src/` ni de `moteur/` n'est touché : aucun résultat, aucune
donnée, aucun témoin ne peut bouger.

- **D'où venaient les 16 échecs.** Sous la carrière nue, le simulateur Python
  tombait sur `prolongee` (`simulateur.py`, ligne 416) et sur `date_entree`
  (`donnees/affiliations.py`, ligne 167), appelé par des tests qui simulaient
  une saisie par `Saisies()`, dont le simulateur par défaut est encore celui du
  moteur Python (`tests/outils_pont.py`), ou par le moteur Python directement.
- **Le changement.** Ces tests simulent désormais sur le simulateur de la
  façade, que le portage sert, comme `test_reversion.py` le faisait déjà :
  `Saisies(facade.Simulateur)` dans `test_minimum_pension_sncf.py`,
  `test_saisie_assimilees.py`, `test_saisie_de_la_lodeom.py`,
  `test_saisie_de_la_reversion_agricole.py`, `test_net_pensions.py`,
  `test_releve_prolonge.py` et `test_versements_uniques.py` ;
  `test_droits_contrefactuels.py`, `test_un_depart_d_avant_septembre_2026…`,
  passe sur la fixture `du_portage` du même fichier. Les valeurs attendues ne
  changent pas : chaque test passe tel quel sur la façade.
- **Ce qui reste sur le Python, et pourquoi.**
  `test_un_droit_que_le_moteur_ne_connait_pas_est_refuse` garde la fixture du
  moteur Python : le portage refuse aussi un état du droit inconnu, mais au
  calcul et non à la construction du scénario, sous `RuntimeError` et non
  `ValueError`. Le passer à la façade changerait ce que le test affirme ; il
  ne dépend pas de la classe de la carrière.
- **Ce qui part avec les règles.** Les trois tests de `test_facade_jumeau.py`
  qui échouent encore sous la carrière nue (`…le_scenario_1…un_temoin_sur_vingt`,
  `…la_comparaison…un_temoin_sur_quarante`, `…rend_la_proposition_que_la_facade_lit`)
  confrontent la façade au moteur Python, à qui ils passent la carrière que
  le portage rend. Ils n'ont pas d'équivalent sur la façade : ils partent avec
  les règles. Rien n'est supprimé ici ; la bascule (morceau 4) les retire ou
  leur fait recopier la carrière sous la classe des règles.
- **Les vérifications.** `python -m pytest -m rapide` : vert (5 695). Les
  huit fichiers touchés : verts (134).
- **Mesuré de nouveau** sous la carrière nue, par la recette de la note
  d'hier : 125 échecs, au lieu de 137. Trois passent encore par le simulateur
  Python, les trois du jumeau ci-dessus. Le déplacement en a fait apparaître
  quelques-uns du morceau 3 qu'un échec plus tôt masquait : des lectures de
  `date_de_service`, `duree_de_service`, `reversion_agricole`,
  `retraite_progressive` et `radiation_pour_invalidite` sur la carrière, dans
  `test_minimum_pension_sncf.py`, `test_saisie_de_la_reversion_agricole.py`
  et `test_releve_prolonge.py`.

**Ce qui reste** : le morceau 3, les tests qui lisent une propriété de règle
sur la carrière, en commençant par `test_simulateur.py`
(`trimestres_retenus`, 27) et `test_priorite_enfants.py` (`date_entree`, 22) ;
puis la bascule.
