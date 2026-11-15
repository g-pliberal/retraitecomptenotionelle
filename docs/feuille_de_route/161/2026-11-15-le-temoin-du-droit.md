# Le témoin du droit : plus aucun appel du droit refait par le moteur Python

Action 161, étape 8e, après `2026-11-15-le-temoin-des-valeurs.md`. Aucune
règle du portage, aucune donnée n'a bougé ; un témoin naît, et les jumeaux
Python du droit partent.

## Ce qui est fait

- **Le témoin du droit**, `tests/temoins/droit.json` : pour chaque demande
  qu'un test fait au droit à travers le pont (`pont.droit`), sous
  l'empreinte de ce que le pont envoie (les appels sous leurs clés, leurs
  arguments mis en données, les carrières qu'ils nomment, les paramètres,
  `None` pour les réglages de référence), les fonctions appelées et
  l'empreinte de ce que le portage rend et refuse, chaque flottant lu à douze
  chiffres significatifs (`outils_valeurs.empreinte_de_la_valeur`). 957
  demandes, 114 Ko, mesurées sur 1 255 demandes et 64 000 appels.
- **Figé sous la dernière confrontation** : le témoin s'est écrit pendant
  une course où le jumeau Python refaisait encore chaque appel au bit près ;
  les onze fichiers passaient. Puis, sans lui ni la variable de figeage, ils
  repassent tous sur le témoin : l'empreinte d'une demande ne dépend ni du
  processus ni de l'ordre des tests.
- **`outils_pont.droit_et_fige`** remplace `droit_et_refait` dans onze
  fichiers (`test_oracle.py`, `test_pont.py`, `test_taux_plein_…`,
  `test_sondes_par_le_pont.py`, `test_sections_sante.py`, et six autres) ;
  une demande absente ou déplacée arrête le test, `FIGER_DROIT=1 python -m
  pytest <fichier>` l'écrit (sous verrou). `python scripts/construire_temoins.py
  --droit` le refait à neuf en relançant les fichiers qui l'appellent
  (`fichiers_qui_appellent_le_droit`), en une minute et demie ; la fabrique
  le refait avec les autres témoins. Tests : `tests/test_droit_fige.py`.
- **Retirés** : `JUMEAUX_DU_DROIT` et les tables des sondes, de la mortalité
  et de l'histoire du droit qui s'y ajoutaient, leurs vingt aides,
  `droit_et_refait`, et `test_le_controle_du_droit_voit_un_ulp_deplace_…`
  de `test_pont.py`, que `test_un_rendu_qui_bouge_arrete_le_test…` remplace.
  Les docstrings qui disaient « le jumeau Python le refait au bit près » ou
  « dans les deux moteurs » disent le témoin.

## Ce qui reste

1. **Les deux tests qui refont les témoins au moteur Python**
   (`test_le_moteur_python_refait_*`), que `test_affirmations.py` exige tant
   qu'une page du site affirme que le jumeau refait les témoins : ils
   partent avec la phrase, à la session du site.
2. **L'inversion** (`test_une_saisie_par_la_pension_passe_le_pont_…`) et
   les carrières de la grille que les tests bâtissent encore en Python
   (`carriere_de_la_grille`, `_carriere_du_cout`).
3. **Les autres confrontations** : `test_reversion.py`, `test_chronologie.py`,
   `test_age_conjoncturel.py`, `test_avantages.py`, et les `moitie_python` de
   `test_cumul_activites.py`, `test_cycle_de_vie_portage.py`,
   `test_moteur.py`, `test_web.py`.
4. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** Les onze fichiers et `test_droit_fige.py` : 1 080 passés ;
`python -m pytest -m rapide` : 5 393 passés. Les six tests rouges sur le
commit de départ (`test_solde_fusion.py`, cinq affirmations de l'accueil)
le restent dans ce conteneur, qui ne refait pas la fabrique ; GitHub, qui la
refait, les a vus verts sur la suite du 15 novembre à 17 h 03.
