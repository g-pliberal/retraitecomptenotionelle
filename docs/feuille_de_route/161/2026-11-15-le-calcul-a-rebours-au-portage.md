# Le calcul à rebours au portage : l'inversion et les carrières de la grille de `test_pont.py` sans le moteur Python

Action 161, étape 8f, après `2026-11-15-le-temoin-du-droit.md`. Aucune
règle du portage, aucune donnée n'a bougé ; seuls des tests changent de
juge.

## Ce qui est fait

- **L'inversion** (`test_une_saisie_par_la_pension_passe_le_pont_…`) : la
  carrière que le portage trouve en remontant de la pension saisie se
  simulait au moteur Python (`Simulateur.simuler`) ; elle se simule
  désormais au portage, par `pont.droit` et `simulateur.simuler`, et sa
  pension doit être celle que le site montre (`Contexte.simuler`). Le test
  rougit si l'on y simule la carrière au revenu de la saisie (26 165 € contre
  19 814 €).
- **Les carrières du coût** : `_carriere_du_cout`, qui les bâtissait en
  Python (`castypes.carriere_de_la_grille`), devient `_carrieres_du_cout`,
  qui les fait bâtir au portage (`pont.carrieres_de_la_grille`), avec les
  deux carrières que l'âge légal de la proposition en dérive, au lieu de
  `Carriere.prolongee`. Quatre tests la lisent ; leurs valeurs figées n'ont
  pas bougé d'un bit.
- **Les cases de `test_le_pont_rend_des_cases_…`** se datent au pilote du
  portage (`_ages_au_portage`), non plus au Python.
- **`test_chaque_case_passe_au_portage_…`** confrontait les options de
  chaque case au Python ; elles sont figées au témoin des valeurs (« cases de
  la grille et leurs refus »), écrites pendant une course où la
  confrontation tenait encore, puis la confrontation est partie.

## Ce qui reste

1. **Les deux tests qui refont les témoins au moteur Python**, avec la
   phrase du site qui les exige (`test_affirmations.py`), à la session du
   site.
2. **Les carrières de la grille bâties en Python ailleurs** :
   `test_lectures_decision_29.py` (`du_moteur_python`, une confrontation
   entière), `test_cycle_de_vie_script.py`, `test_mortalite_population.py`.
3. **Les autres confrontations** : `test_reversion.py`, `test_chronologie.py`,
   `test_age_conjoncturel.py`, `test_avantages.py`, et les `moitie_python` de
   `test_cumul_activites.py`, `test_cycle_de_vie_portage.py`,
   `test_moteur.py`, `test_web.py`.
4. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** `tests/test_pont.py` et `test_valeurs_figees.py` : 75 passés ;
`python -m pytest -m rapide` : 5 393 passés.
