# Le témoin des valeurs : les confrontations du pont figées, et le levier du jumeau retiré

Action 161, étape 8d, après `2026-11-15-le-temoin-des-sorties.md`. Aucune
règle du portage, aucune donnée n'a bougé ; un témoin naît, et le moteur
Python ne simule plus la grille du coût.

## Ce qui est fait

- **Le témoin des valeurs**, `tests/temoins/valeurs.json` : pour une valeur
  Python que le portage rend à travers le pont (une grille du coût, les
  dates d'une grille, des cas servis), l'empreinte de la valeur mise en
  données, sous `<fichier>::<nom>`, chaque flottant lu à douze chiffres
  significatifs. 45 valeurs, 4 Ko. Figées sur ce que le portage rendait
  quand chaque confrontation le tenait encore égal au moteur Python : les
  confrontations passaient sur ce commit de départ, le portage n'a pas
  changé.
- **`tests/outils_valeurs.py`** : `valeur_figee(nom, valeur)` confronte la
  valeur au témoin et la rend ; une valeur absente ou déplacée arrête le
  test, `FIGER_VALEURS=1 python -m pytest <fichier>` l'écrit (sous verrou).
  `python scripts/construire_temoins.py --valeurs` (quarante-trois secondes)
  le refait à neuf, en relançant sous `FIGER_VALEURS=1`, sur un témoin à
  part, les seuls tests qui en figent une (`tests_qui_figent`, lus dans
  l'arbre syntaxique) ; la fabrique le refait avec les autres témoins.
  Tests : `tests/test_valeurs_figees.py`.
- **Vingt-quatre confrontations figées** : dix-sept de `tests/test_pont.py`
  (les cases, leurs variantes, le stock, le barème, les saisies, les âges du
  pilote, les carrières bâties, la grille des carrières types, les départs
  des facteurs de la dépense, les avantages, le scénario 1 servi, la grille
  du coût et ses comptes, la grille d'essai sous chaque variante et sur des
  données d'ailleurs), et celles de `test_cout.py`, `test_grille_large.py`
  (deux), `test_solde_fusion.py`, `test_stock_age_legal.py`,
  `test_mortalite_population.py`. Onze tests renommés, qui disaient « au
  bit près du jumeau ».
- **Le levier retiré** : `CONFRONTATIONS_DU_JUMEAU` vide, `pont.par_le_jumeau`
  et `pont.par_le_portage` partent, avec les deux tests du levier ; le coût
  simule sa grille au portage sans autre chemin (`cout._simulations`), et
  `cout._simulations_en_python` part ; `castypes.batie_au_portage` ne
  regarde plus que ses cas types. `Saisies.scenario_actuel` et
  `scenario_actuel_en_donnees` partent de `tests/outils_pont.py`.
  `test_seules_les_confrontations_ouvrent_le_jumeau` reste : il refuse qu'un
  levier revienne.

## Ce qui reste

1. **`droit_et_refait`** (`tests/outils_pont.py`), qui fait refaire au
   jumeau chaque appel du droit : 85 appels dans douze fichiers, dont cinq
   tests de `test_pont.py` (les leviers des avantages, les fonctions du
   droit, l'ulp déplacé, les lignes du relevé, la carrière bâtie de ses
   options) et `test_le_pont_prete_une_table_au_moteur_du_portage`. Même
   recette que `servi_et_fige` : figer dans l'aide, et tous passent d'un coup.
2. **Les deux tests qui refont les témoins au moteur Python**
   (`test_le_moteur_python_refait_*`) : `test_affirmations.py` exige le
   second, parce qu'une page du site affirme que le jumeau refait les
   témoins. Ils partent avec la phrase, à la session du site.
3. **L'inversion** (`test_une_saisie_par_la_pension_passe_le_pont_…`), qui
   simule au `Simulateur` Python, et les carrières de la grille que les
   tests bâtissent encore en Python (`carriere_de_la_grille`,
   `_carriere_du_cout` : soixante-dix à quatre-vingt-dix règles appelées par
   test, selon l'espion).
4. **Les autres confrontations de la note du témoin des sorties** :
   `test_reversion.py`, `test_chronologie.py`, `test_age_conjoncturel.py`,
   `test_avantages.py`, et les `moitie_python` de `test_cumul_activites.py`,
   `test_cycle_de_vie_portage.py`, `test_moteur.py`, `test_web.py`.
5. **L'écart `rattachement_pension_smic`** (3,45 € par an), toujours non
   traité, sans décision du propriétaire.

**Tests.** Les fichiers touchés, `test_valeurs_figees.py`,
`test_sorties_figees.py`, `test_outillage.py`, `test_fabrique.py`,
`test_niveaux.py` : verts, sauf `test_l_accueil_cite_le_solde_…` de
`test_solde_fusion.py` et cinq affirmations de l'accueil, rouges déjà sur le
commit de départ (l'accueil, que la fabrique refait) ; `python -m pytest -m
rapide` : 5 385 passés.
