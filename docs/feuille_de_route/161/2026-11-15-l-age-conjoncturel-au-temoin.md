# L'âge conjoncturel au témoin : les départs de la grille et le coût par carrière ne se refont plus au moteur Python

Action 161, étape 8j, après `2026-11-15-la-chronologie-au-temoin.md`.
Aucune règle du portage, aucune donnée n'a bougé ; deux tests changent de
juge.

## Ce qui est fait

- **La suite GitHub** : verte au départ de l'étape (`cd51830`).
- **`test_les_departs_de_la_grille_se_datent_au_portage_sans_les_jumeaux`**
  (`test_age_conjoncturel.py`) faisait refaire au moteur Python, par
  `calculer_cas_types`, les départs de deux grilles (trois cas types sur
  toutes les générations du coût, et l'artisan entré deux ans plus tôt), et
  les confrontait à `departs_de_la_grille`. Vu vert d'abord, il fige
  désormais ce que le portage rend au témoin des valeurs
  (`departs::trois_cas_types`, `departs::artisan_entre_plus_tot`). Les six
  cases que le droit écarte, que le Python comptait dans `grille.echecs`, se
  lisent au nombre de points : trois fois les générations, moins six.
  `du_moteur_python` est retiré.
- **`test_le_cout_par_carriere_passe_par_le_portage_sans_le_moteur_python`**
  (`test_avantages.py`) confrontait `cout_avantages.par_carriere` à
  `_par_carriere_au_moteur_python`, qui datait, liquidait et recalculait au
  moteur Python. La table de la génération 1960 (treize lignes) est figée au
  témoin (`par_carriere::1960`) ; l'aide est retirée, les assertions sur ce
  que l'option montre restent, portées par la valeur du portage.
- **Les trois empreintes figées sont celles du moteur Python** : recalculées
  à part, par l'ancien code, elles tombent juste toutes trois.
- Les autres tests de `test_avantages.py` liquident encore au scénario 1 du
  moteur Python sans rien confronter : ils partiront avec les cent fichiers
  qui importent une règle Python.

## Ce qui reste

1. **Les `moitie_python`** de `test_cumul_activites.py`,
   `test_cycle_de_vie_portage.py`, `test_moteur.py`, `test_web.py`. Même
   recette : `valeur_figee` ou `sortie_figee`, l'empreinte vérifiée contre
   le moteur Python avant de le retirer.
2. **Les deux tests qui refont les témoins au moteur Python**, à la session
   du site.
3. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** `test_age_conjoncturel.py` : 6 passés ; `test_avantages.py` :
30 passés ; sous `PRESOMPTIONS_DECALEES=1`, 34 passés et 2 passés par la
garde ; `test_valeurs_figees.py` et `test_fichiers_sur_le_moteur_python.py` :
verts ; `pytest -m rapide` : 5 396 passés.
