# Le coût sur la façade : ses études prennent un simulateur de la façade

Action 161, étape 9g, après `2026-11-16-la-troisieme-vague-a-moitie.md`.
Aucune règle, aucune donnée de calcul, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 23 à 17, la vague 4
comprise.

## Ce qui est fait

- **Le verrou du coût n'en était pas un.** Le coût et ses études ne lisent
  du simulateur que ses données (paramètres, séries, mortalité,
  distributions) et demandent le reste au pont : un simulateur de la façade
  leur suffit. Deux lectures passaient encore par le moteur du scénario 1, et
  lisent désormais leurs données : l'effet retour bâtit le barème de l'ASPA
  (`MinimumVieillesse`) de la racine et des séries ; la revalorisation
  servie prend le catalogue du simulateur. Le recalcul des avantages lit les
  fiches par leur chargeur (`FichesDatees`). La façade sert de plus deux
  données, `revalorisations` et `distributions_par_sexe`.
- **Quittent le moteur Python** : `test_etranger.py` (les trimestres
  étrangers se lisent dans les durées que la façade sert,
  `donnees()["etranger"]`), `test_facteurs_depense.py`,
  `test_indexation_programme.py`, `test_effet_retour.py`,
  `test_cycle_de_vie_references.py` (l'espérance de vie par le chargeur de
  la mortalité, les cas types datés par `castypes.departs_au_portage`).
- **`test_avantages.py`** : ses dix tests sur la façade ; les âges des cas
  types et l'âge légal des masses anticipées viennent du portage. Il reste
  dans la liste pour `_apprenti_puis_salarie`, que `test_pont.py` (vague 4)
  appelle avec un simulateur Python.
- **`test_cout_age_depart.py`** : onze tests sur douze à la façade. L'espion
  du plafond de décote se glisse dans `liquider.trimestres_de_decote` du
  Python : à la façade, il ne verrait rien et passerait à vide. Il garde un
  simulateur Python à lui, jusqu'à ce que la décote sans plafond s'écrive en
  données.

## Ce qui reste de la vague 3

- `test_revalorisation.py` : `PensionServie.coefficient`, que la façade ne
  sert pas.
- `test_retablissement.py` : `coordonner.retablir` rend une carrière, que
  ses tests comparent par identité.
- `test_plafond_majoration_enfants.py` : la liquidation passe à la façade ;
  restent `completer.majoration_sous_le_traitement` (à servir), la fiche
  lue à sa date (`fiches_datees.version`), la fiche retirée et la fiche
  altérée par `monkeypatch`, que le portage ne voit pas.
- `test_controle_drees_panorama.py`, `test_donnees.py`,
  `test_primes_soumises_a_retenue.py`, `test_retraite_progressive.py`,
  `test_solde_fusion.py`, `test_versements_uniques.py`.

**Tests.** `python -m pytest -m rapide` : vert (5 422 tests). Les fichiers
passés, `test_facade.py`, `test_facade_jumeau.py` et
`test_fichiers_sur_le_moteur_python.py` : verts ; `test_facteurs_depense.py`
(le coût calculé sans mémoire, 3 min 40) : vert.
