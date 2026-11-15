# La pension maximale et l'invalidité à la façade : ce que les tests remplaçaient en Python, une copie des données le dit au portage

Action 161, étape 5g, après
`2026-11-15-l-echeancier-le-journal-et-le-pilote-a-la-facade.md`, « Ce qui
reste », 4. Aucune règle, aucune donnée du dépôt, aucun témoin n'a bougé. La
suite complète de GitHub était verte sur `03f9ea9` ; celle de `65cc935`
tournait encore au début de l'étape.

## Ce qui est fait

- **Des données retouchées en copie** (`facade.donnees_retouchees`) : une
  copie de `data/` dont les fichiers sont liés à ceux du dépôt, sauf ceux
  qu'un test récrit, une fonction du texte au texte ; le simulateur de la
  façade la reçoit par `Parametres(racine_donnees=…)`, et le pont bâtit son
  paquet (`pont.paquet_des_donnees`). Ce qu'un test remplaçait en Python par
  `monkeypatch` ou par une copie retouchée d'un résultat, le portage le voit
  ainsi, par ses données. Une copie par jeu de retouches et par processus.
- **`test_pension_maximale.py`** (5 → 3 marqués) : les deux tests qui
  remplaçaient `liquider.salaire_de_reference` relèvent les plafonds de la
  Sécurité sociale d'avant la liquidation (× 2 avant 2005 ; × 1,5 et × 3,4
  avant 1971), et le salaire annuel moyen du cadre au plafond avec eux, le
  plafond de l'année, qui fixe le maximum, intact. Le test des majorations
  de 1972 à 1982 lit la pension calculée du portage,
  `montant + ecretement_du_maximum`, au lieu de la refaire d'un facteur.
- **`test_invalidite.py`** (4 → 3) : le test des majorations de 1972 à 1977
  ne retouche plus le résultat (`sur_la_duree_maximum`) ; la copie fait
  retenir au plus 96 trimestres à la période 1951-1971 du régime général, et
  le test vérifie que la liquidation le dit.
- `RESTES` de `tests/test_fichiers_sur_le_moteur_python.py` suit.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide`,
`test_pension_maximale.py`, `test_invalidite.py`, les fichiers de la façade,
`test_fichiers_sur_le_moteur_python.py`.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Les confrontations des deux moteurs gardent leur marque (trois dans
   chacun des deux fichiers), comme le solveur `niveau_pour_pension` et
   `Saisies.simuler` (`test_reversion.py`).
2. Les autres fichiers de `RESTES`, chacun avec ce qui lui manque ; la copie
   retouchée sert ceux dont un test remplace une fonction du droit par
   `monkeypatch` quand une donnée peut dire la même chose.
