# La chronologie au témoin : `test_chronologie.py` ne confronte plus le portage au moteur Python

Action 161, étape 8i, après `2026-11-15-la-reversion-au-portage.md`.
Aucune règle du portage, aucune donnée n'a bougé ; un test change de juge.

## Ce qui est fait

- **La suite GitHub** : au départ de l'étape, le verdict porté par `main`
  (`.github/etat_suite.yaml`) était encore celui de `805f559`, rouge ; la
  course sur `1fab722`, qui porte les réparations de l'étape 8h, tournait.
- **`test_le_portage_construit_la_meme_chronologie`** faisait refaire au
  moteur Python (`chronologie.du_parcours`, `du_releve`, `completer`, les
  prolongations et les périodes assimilées) chacune des saisies de `SAISIES`,
  et confrontait au JSON près ce que `comparer-chronologie.mjs` en tire. Vu
  vert d'abord, il devient `test_le_portage_construit_la_chronologie_figee` :
  la sortie du script, chronologie ou refus, passe par `sortie_figee`, et le
  témoin des sorties a reçu ses entrées (`FIGER_SORTIES=1`), figées sur des
  chronologies que le moteur Python rendait encore à l'identique. `_python`
  est retiré.
- Le nom du script reste dans la source du test : sous la garde des
  présomptions, `tests/conftest.py` le passe, comme toute sortie du portage,
  qui lit ses présomptions dans le paquet.
- Les deux autres tests qui lancent node (`les deux lecteurs`, `la naissance
  impossible`) ne confrontent pas : chaque côté répond à des valeurs écrites
  depuis le texte. Leur moitié Python partira avec le moteur.

## Ce qui reste

1. **Les autres confrontations** : `test_age_conjoncturel.py`
   (`du_moteur_python`, par `calculer_cas_types`), `test_avantages.py`, et
   les `moitie_python` de `test_cumul_activites.py`,
   `test_cycle_de_vie_portage.py`, `test_moteur.py`, `test_web.py`.
2. **Les deux tests qui refont les témoins au moteur Python**, à la session
   du site.
3. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** `test_chronologie.py` : 46 passés ; sous `PRESOMPTIONS_DECALEES=1`,
43 passés et 3 passés par la garde.
