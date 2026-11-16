# La revalorisation et le versement unique à la façade : trois fichiers quittent le moteur Python

Action 161, étape 9h, après `2026-11-16-le-cout-sur-la-facade.md`. Aucune
règle, aucune donnée de calcul, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 17 à 14, la vague 4
comprise.

## Ce qui est fait

- **`test_revalorisation.py`** quitte le moteur Python. La façade sert
  `PensionServie.coefficient` par le portage (entrée
  `pension_servie.coefficient` : la pension n'y passe que par son régime et
  son type de calcul, ce que la règle en lit), et son simulateur a une
  `revalorisation_servie`, la classe Python qui ne fait que lire les séries
  que le portage calcule (note de décision 0007).
- **`test_versements_uniques.py`** quitte le moteur Python. La façade sert
  `completer._seuil_a_la_date` et `completer.coefficient_du_versement`
  (des règles, `seuilALaDate` désormais exporté par `completer.js`), et
  `completer.verser_en_capital`, une entrée à elle : comme son jumeau, elle
  remplace dans la liste reçue les pensions versées en une fois, et rend sa
  fiabilité. Les deux règles ont leurs appels confrontés au jumeau
  (`APPELS_DES_REGLES`, `test_facade_jumeau.py`).
- **`test_primes_soumises_a_retenue.py`** quitte le moteur Python : le
  catalogue et les affiliations se lisent sur le simulateur de la façade, la
  carrière s'y bâtit.
- **`test_solde_fusion.py`** : douze tests sur treize à la façade, qui sert
  `compte.taux_du_bareme` (module `compte`, à la racine du portage, confronté
  au jumeau). Un barème mal formé arrête le simulateur du portage, ce que le
  test vérifie désormais, au lieu de lire le constructeur Python. Le contrôle
  que la variante ne remplaçait pas `ConstructeurCompte.taux_unifie` du
  Python est parti avec : le coût ne passe plus par lui.
  `test_la_grille_se_simule_par_le_portage` garde un simulateur Python : la
  variante (`RegimeUniqueVariante`) remplace des fonctions du coût, et la
  façade, qui refuse tout service sous un modèle modifié
  (`memoire.modele_intact`), ne lui servirait pas `mortalite.courbe`, que
  `cout._survies` lit. Le fichier reste donc dans la liste. Le lever demande
  soit que la façade distingue un remplacement du coût d'un remplacement du
  moteur, soit que le coût lise ses survies sans passer par elle.

## Ce qui reste de la vague 3

- `test_solde_fusion.py` : la grille, ci-dessus.
- `test_retablissement.py` : `coordonner.retablir` rend une carrière, que
  ses tests comparent par identité.
- `test_plafond_majoration_enfants.py` : `completer.majoration_sous_le_traitement`
  (à servir), la fiche lue à sa date (`fiches_datees.version`), la fiche
  retirée et la fiche altérée par `monkeypatch`, que le portage ne voit pas.
- `test_retraite_progressive.py`, `test_controle_drees_panorama.py`,
  `test_donnees.py` : non regardés.

**Tests.** `python -m pytest -m rapide` : vert (5 387 tests). Les fichiers
passés, `test_facade.py`, `test_facade_jumeau.py` et
`test_fichiers_sur_le_moteur_python.py` : verts.
