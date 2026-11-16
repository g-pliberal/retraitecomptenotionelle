# La troisième vague à moitié : neuf fichiers quittent le moteur Python

Action 161, étape 9f, après `2026-11-15-les-univers-hors-du-moteur-python.md`.
Aucune règle, aucune donnée de calcul, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 36 à 23, la vague 4,
menée en parallèle, comprise.

## Ce qui est fait

- **La façade sert de plus** : `Carriere.depuis_chronologie` (entrée
  `carriere.depuis_chronologie`, la chronologie complétée telle quelle) ;
  les tables `surcote_baremes` (`coefficient`, `connait`) et
  `services_ouvrant_pension` (`annees`) ; les règles
  `compter.bonification_ouverte` et `compter.droit_regime_special`. Chaque
  méthode et chaque règle a son appel confronté au jumeau
  (`test_facade_jumeau.py`).
- **Quittent le moteur Python** : `test_outre_mer.py`,
  `test_sections_juridiques.py`, `test_cnracl.py`, `test_chronologie.py`,
  `test_salaire_annuel_moyen.py`, `test_mayotte.py`,
  `test_sections_sante.py`, `test_estimation_officielle.py`,
  `test_priorite_enfants.py`. Ce qui n'était qu'une confrontation au jumeau
  JavaScript (l'outre-mer, la retenue d'avant 1946) devient la vérification
  des valeurs de la source sur le portage ; le coefficient du traitement
  différé et la moyenne selon la règle du salaire annuel moyen se lisent au
  portage par node, leurs arguments (`Map`, `Set`, une fonction du point)
  ne passant pas la façade. La garde de l'estimation officielle vise le
  moteur Python par son chemin, sans l'importer.
- **`test_avantages.py`** : cinq tests sur dix passent à la façade, et la
  cascade se lit dans les sources du portage. Les cinq autres font tourner le
  coût, qui demande un simulateur Python ; `_apprenti_puis_salarie` reste
  bâti en Python, `test_pont.py` le lui demandant.
- `test_mayotte.py` garde ses fixtures « deux moteurs » : elles confrontent
  désormais le portage à lui-même, et les valeurs qu'elles tiennent viennent
  de la source ; elles pourront se simplifier.

## Ce qui reste de la vague 3

- **Le coût et les études**, qui veulent un simulateur Python :
  `test_avantages.py` (5), `test_cout_age_depart.py`,
  `test_cycle_de_vie_references.py`, `test_facteurs_depense.py`,
  `test_indexation_programme.py` (la revalorisation servie lit
  `scenario_actuel.catalogue`). Ils attendent, comme l'effet retour, que le
  coût ne lise plus le moteur Python.
- **`test_revalorisation.py`** : `PensionServie.coefficient` et
  `RevalorisationServie` lisent le simulateur Python ; la façade ne sert
  pas `PensionServie.coefficient`.
- **`test_retablissement.py`** : `coordonner.retablir` rend une carrière,
  et ses tests vérifient l'identité (`is carriere`).
- Puis `test_controle_drees_panorama.py`, `test_donnees.py`,
  `test_etranger.py`, `test_plafond_majoration_enfants.py`,
  `test_primes_soumises_a_retenue.py`, `test_retraite_progressive.py`,
  `test_solde_fusion.py`, `test_versements_uniques.py`.

**Tests.** `python -m pytest -m rapide` : vert (5 417 tests, avant
`test_priorite_enfants.py`) ; les fichiers passés, `test_facade_jumeau.py`,
`test_facade.py` (ses entrées) et `test_fichiers_sur_le_moteur_python.py` :
verts.
