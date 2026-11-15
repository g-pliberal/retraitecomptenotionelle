# Les carrières des tests au portage : plus aucune carrière de la grille bâtie en Python par un test

Action 161, étape 8g, après `2026-11-15-le-calcul-a-rebours-au-portage.md`.
Aucune règle du portage, aucune donnée n'a bougé ; seuls trois tests changent
de juge.

## Ce qui est fait

- **`test_lectures_decision_29.py`** : `du_moteur_python`, qui refaisait au
  moteur Python les pensions des cas types de `--cas-types`
  (`carriere_de_la_grille`, `Simulateur.simuler`), est parti. Ce que le
  portage rend sous le taux du programme et sous 11,23 % est figé au témoin
  des valeurs (« cas types sous le taux … »), écrit pendant une course où la
  confrontation tenait encore ; les deux assertions du taux crédité (il
  baisse la pension du scénario 6, il laisse l'étalon) se lisent désormais
  sur ce que rend le portage.
- **`test_cycle_de_vie_script.py`** : les demandes à `cycle_de_vie.mjs`
  ne se rebâtissent plus au pilote Python (`carriere_de_la_grille`,
  `age_liquidation_pour`) ; elles sont figées, écrites en JSON à l'octet,
  au témoin (« demandes de l'étude, écrites »), après avoir été confrontées
  une dernière fois. Restent vérifiés : 91, 27 et 26 cases, les étages sur
  la grille même, des âges entiers et des âges fractionnaires.
- **`test_mortalite_population.py`** : le vingtile du salarié au salaire
  moyen né en 1965 n'est plus refait par `Convertisseur.population_de` sur
  une carrière Python ; il vaut le quatorzième, que la page lui donne
  (action 138, étape 7, et le docstring du test).

## Ce qui reste

1. **Les deux tests qui refont les témoins au moteur Python**, avec la
   phrase du site qui les exige (`test_affirmations.py`), à la session du
   site.
2. **Les autres confrontations** : `test_reversion.py`, `test_chronologie.py`,
   `test_age_conjoncturel.py`, `test_avantages.py`, et les `moitie_python` de
   `test_cumul_activites.py`, `test_cycle_de_vie_portage.py`,
   `test_moteur.py`, `test_web.py`.
3. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** Les trois fichiers et `test_valeurs_figees.py` : 47 passés ;
`python -m pytest -m rapide` : 5 393 passés (un rouge au premier passage,
`test_fichiers_sur_le_moteur_python.py`, qui demandait de retirer
`test_lectures_decision_29.py` de sa liste : c'est fait).
