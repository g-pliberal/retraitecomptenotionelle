# Le solveur de l'inversion retiré du Python, et ce qui retient encore les règles du moteur Python

Action 161, étape 8a, après `2026-11-15-les-dernieres-fonctions-gardees-au-bit-pres.md`.
Aucune règle du portage, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

- **Le solveur `niveau_pour_pension` est parti du Python**, avec
  `NiveauInverse`, `COUPES_INVERSION` et `TOLERANCE_INVERSION`
  (`simulateur.py`, 137 lignes). Aucun Python de production ne l'appelait :
  le site inverse la pension par `niveauPourPension` (`contexte.js`), et le
  coût n'inverse rien. Ses deux tests, les derniers de `test_simulateur.py`
  sous la marque `sur_le_moteur_python`, passent à
  `tests/js/inversion.test.js`, sur l'exemplaire du portage et la pension du
  scénario 1 qu'il calcule : la même carrière, les mêmes niveaux, le même
  saut des 150 heures de SMIC à 6 000 €. `test_web.py` lance ce fichier avec
  les autres `tests/js/*.test.js`.
- **`test_simulateur.py` n'entre plus dans le moteur Python** : il quitte
  `FICHIERS` et `RESTES` (`tests/test_fichiers_sur_le_moteur_python.py`) et
  n'importe plus la fixture `entrees_du_test`. Les niveaux du balayage de la
  croissance (`NIVEAUX_BALAYAGE`), que seul son test lisait, y passent.
- **Le champ `niveau_inverse` de `Comparaison` reste**, typé `dict | None` :
  le pont lit chaque champ que le portage écrit, et refuse un type qui n'en
  porte pas un ; il ne transmet pas le niveau trouvé (`Saisies.simuler`,
  `tests/outils_pont.py`), le champ vaut donc `None` côté Python.

## Ce qui retient encore les règles du moteur Python

La reprise disait qu'il ne restait que le retrait des règles, paire par
paire. La mesure dit autre chose : aucune paire du moteur ne peut partir
seule aujourd'hui.

- **Les règles s'importent les unes les autres.** `python scripts/jumeaux.py
  <nom>` sur vingt-deux paires du moteur : chacune est importée par d'autres
  fichiers du moteur (`droit/commun.py` par vingt, `droit/etranger.py` par
  dix), et toutes remontent à `simulateur.py`, `scenarios/actuel.py`,
  `carriere.py` — dont le constructeur de `Carriere`, type du pont, appelle
  `droit/preparer.py` — et `echeancier.py`. Le retrait se fera donc par le
  haut : on cesse d'exécuter le moteur Python, puis ses fichiers partent,
  chaque type du pont gardé sans ses règles.
- **Ce qui l'exécute encore** :
  1. les confrontations du jumeau : 17 tests marqués `sur_le_moteur_python`
     dans 12 fichiers (`RESTES`), presque tous « le jumeau refait … du
     portage » ; `servi_et_refait` (`tests/outils_pont.py`), qui fait refaire
     au Python chaque cas de l'estimation officielle et de Destinie 2 ; les
     onze de `CONFRONTATIONS_DU_JUMEAU` et les deux de `TESTS_DU_LEVIER`
     (`tests/test_pont.py`), sous `pont.par_le_jumeau()`, et la branche
     `_simulations_en_python` du coût qu'ils ouvrent ;
  2. 100 fichiers de tests qui importent encore une règle ou une entrée du
     moteur Python (`FICHIERS`), à porter à la façade ou au pont.
- **La relecture** reste due, avant leur retrait, pour `droit/releve.js`,
  `journal.js`, `droit/categories.js` et `fusion.js` (note de décision 0007).

## Ce qui reste

1. **Les confrontations du jumeau partent** (étape 8b) : les 17 tests
   marqués, `servi_et_refait`, `CONFRONTATIONS_DU_JUMEAU`, le levier
   `pont.par_le_jumeau` et `_simulations_en_python`. Chacune ne compare que
   les deux moteurs ; ce qu'elle seule exécutait se fige d'abord par un
   témoin (quatrième temps de la note 0003).
2. Les 100 fichiers de `FICHIERS` passent à la façade ou au pont, par lots.
3. Puis les fichiers du moteur Python partent, par le haut, leurs chargeurs
   sous `donnees/` et leurs types gardés (note 0006).
4. L'écart d'`ecart_pour` et les deux points de l'audit carrière longue
   attendent la décision du propriétaire.

**Tests.** `node --test tests/js/inversion.test.js` : 2 passés ;
`tests/test_simulateur.py` : 335 passés ; `python -m pytest -m rapide` :
5 366 passés, deux écarts attendus.
