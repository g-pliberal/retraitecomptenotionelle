# La retraite progressive à la façade : un fichier de plus quitte le moteur Python

Action 161, étape 9j, après `2026-11-16-le-retablissement-et-le-plafond-de-l-18.md`.
Aucune règle, aucune donnée de calcul, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 12 à 11, la vague 4
comprise.

## Ce qui est fait

- **`test_retraite_progressive.py`** quitte le moteur Python. La façade sert
  les règles de `droit/progressive` (`regle`, `age_minimum`, `duree_requise`,
  `regimes_ouverts`, `regimes_liquides`, `fraction`, `recalculee`,
  `examiner`, qui rend le type `Progressive`, lu en chameau) et
  `compter.services_a_temps_partiel`, chacune confrontée au jumeau
  (`test_facade_jumeau.py`). Deux entrées neuves du pont :
  `progressive.liquider`, la liquidation provisoire, et
  `progressive.initiales`, que le portage refait de la demande dont la
  façade a rendu la liquidation provisoire.
- **La liquidation reçoit les pensions provisoires** (`Etat.initiales`) et
  rend le relèvement qu'elles imposent (`complements.plancher`).
- **La fiche retouchée** se lit sur une copie des données
  (`facade.donnees_retouchees`) ; une retouche qui rend `None` y retire le
  fichier : sans la fiche, le portage s'arrête, et le pont rend la
  `LookupError` du Python (`ERREURS_DU_PORTAGE`). Le paquet se compare à la
  fiche préparée par la fabrique (`noyau.versions`).
- **La confrontation des deux moteurs sur le plancher**
  (`test_les_deux_moteurs_comparent_le_plancher_…`) part : le test de la
  surcote parentale tourne désormais sur le portage lui-même, contre les
  mêmes valeurs, et le jumeau est confronté par
  `test_le_jumeau_rend_la_retraite_progressive_que_la_facade_lit`.
- La confrontation des règles compare un dictionnaire sans son ordre et un
  ensemble trié, que le hachage ordonnait au hasard.

## Ce qui reste de la vague 3

- `test_solde_fusion.py` : la grille sous une variante du coût (voir
  `2026-11-16-la-revalorisation-et-le-versement-unique.md`).
- `test_controle_drees_panorama.py`, `test_donnees.py` : non regardés.

**Tests.** `python -m pytest -m rapide` : vert, hors deux confrontations
corrigées ensuite (ordre d'un ensemble), revérifiées sous trois graines de
hachage. `test_retraite_progressive.py`, `test_facade.py`,
`test_facade_jumeau.py` et `test_fichiers_sur_le_moteur_python.py` : verts.
