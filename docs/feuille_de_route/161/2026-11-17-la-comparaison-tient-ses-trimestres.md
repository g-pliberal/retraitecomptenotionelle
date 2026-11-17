# La comparaison tient ses trimestres du portage : 137 tests dépendent encore de la carrière des règles, au lieu de 170

Action 161, morceau 1 du plan de `2026-11-17-la-facade-transmet-la-carriere-nue.md`,
mené la nuit du 16 au 17 novembre 2026, sur la consigne du propriétaire
d'avancer ce qui ne demande pas son avis.

- **Le changement.** La comparaison relue (`types_du_pont/comparaison.py`)
  porte un champ `trimestres_actuels`, que son résumé (`dictionnaire`,
  `tableau`) lit au lieu de le redemander à la carrière. Le pont l'écrit
  (`comparaisonTelleQuelle` de `pont.mjs`, depuis `trimestresActuels` de la
  carrière du portage) ; le simulateur Python, qui vit encore, le remplit de
  sa carrière. Aucun fichier de `moteur/` n'est touché.
- **Le test.** `tests/test_facade.py`,
  `test_la_comparaison_tient_ses_trimestres_du_portage` : la comparaison d'un
  salarié né en janvier 1965, de 23 à 64 ans, sa carrière recopiée sous le type
  nu, dit 164 trimestres (41 années pleines, 1988 à 2028, et janvier 2029, qui
  n'en valide aucun). Vu rouge (`AttributeError`), puis vert.
- **Les vérifications.** `construire_temoins.py` : témoins identiques à
  l'octet. `pytest -m rapide` : vert (5 695). Confrontations légères,
  `test_pont.py`, `test_facade.py`, `test_reversion.py` : vertes.
- **Mesuré de nouveau** sous la carrière nue : 137 échecs, au lieu de 170.
  Les quatre lectures de `trimestres_actuels` qui restent sont des tests qui
  la lisent sur la carrière (morceau 3).

**Ce qui reste** : les morceaux 2 à 4 de la note d'hier. Le suivant, le
simulateur Python lui-même (`simulateur.py`, ligne 416, `prolongee` ;
`donnees/affiliations.py`, ligne 167, `date_entree`).
