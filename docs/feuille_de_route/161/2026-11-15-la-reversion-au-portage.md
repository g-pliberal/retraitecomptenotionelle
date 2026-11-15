# La réversion au portage : `test_reversion.py` ne fait plus rien calculer au moteur Python

Action 161, étape 8h, après `2026-11-15-les-carrieres-des-tests-au-portage.md`.
Aucune règle du portage, aucune donnée n'a bougé ; seuls des tests changent
de juge, et la garde des présomptions est réparée.

## Ce qui est fait

- **La garde des présomptions, rouge depuis l'étape 8d** : elle rejoue les
  tests rapides sous d'autres présomptions (le 1er du mois pour le jour de
  naissance), et `capitaux du compte` (`test_mortalite_population.py`)
  tombait sur le témoin des valeurs, figé sous les présomptions du
  vocabulaire. La confrontation au moteur Python que ce témoin remplace
  tenait sous la garde, les deux côtés lisant les mêmes valeurs décalées ;
  le témoin ne le peut pas. Sous `PRESOMPTIONS_DECALEES`, `valeur_figee` ne
  lit ni n'écrit plus le témoin, et les autres assertions du test restent
  juges (`test_sous_la_garde_des_presomptions_le_temoin_se_tait`).
- **Les saisies de `test_reversion.py`** : `Saisies` (`tests/outils_pont.py`)
  prend le simulateur qui simule ; le fichier lui passe celui de la façade,
  que le portage sert. Les trente-sept appels qui simulaient en Python
  simulent au portage, sans autre retouche.
- **Les huit confrontations `les_deux_moteurs_*` par `comparer.mjs`** : le
  résultat entier vient de `simuler.mjs` et du témoin des sorties
  (`_simules`), figé sur des sorties que le moteur Python confirmait encore ;
  les assertions de chaque cas restent. Les noms ne changent pas, que
  `tests/conftest.py` range.
- **La liquidation fictive de l'assuré mort avant son départ** (cinq tests) :
  son contenu ne passe pas le pont. Elle se lit sur `comparer-liquidation.mjs`
  au témoin des sorties (`_fictive`) : la demande, l'ouverture (« non
  ouverte », les trimestres cotisés), le taux et les montants. Le test « sans
  décote » liquide à la façade la carrière arrêtée au décès, puis la même
  d'un assuré vivant, et confronte la première à ce que le journal porte.
- Un espion (`sys.setprofile`) n'a plus vu, dans tout le fichier, que les
  accesseurs des résultats (`dictionnaire`, `donnees`, `total`) : aucune
  règle du moteur Python ne tourne.

## Ce qui reste

1. **Les autres confrontations** : `test_chronologie.py`,
   `test_age_conjoncturel.py`, `test_avantages.py`, et les `moitie_python` de
   `test_cumul_activites.py`, `test_cycle_de_vie_portage.py`,
   `test_moteur.py`, `test_web.py`. Même recette : un script de `tests/js/`
   et `sortie_figee`, ou `Saisies(facade.Simulateur)`.
2. **Les deux tests qui refont les témoins au moteur Python**, avec la
   phrase du site qui les exige (`test_affirmations.py`), à la session du
   site.
3. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** `test_reversion.py` : 382 passés ; `test_valeurs_figees.py`,
`test_sorties_figees.py`, `test_fichiers_sur_le_moteur_python.py` : verts ;
le test des capitaux sous `PRESOMPTIONS_DECALEES=1` : vert.
