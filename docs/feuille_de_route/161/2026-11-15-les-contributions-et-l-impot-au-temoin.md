# Les contributions et l'impôt au témoin : le cycle de vie ne confronte plus au moteur Python

Action 161, étape 8l, après `2026-11-15-les-cumuls-tires-au-temoin.md`.
Aucune règle du portage, aucune donnée n'a bougé ; deux tests changent de juge.

## Ce qui est fait

- **La suite GitHub** : verte au départ de l'étape (`cd51830`).
- **`test_cycle_de_vie_portage.py`** faisait refaire au moteur Python
  (`moitie_python`) les contributions d'équilibre de onze carrières et
  l'impôt de 2 516 foyers de la grille, puis les confrontait au portage
  (`tests/js/comparer-cycle-de-vie.mjs`). Vus verts d'abord, ils figent
  désormais ce que le portage rend au témoin des valeurs : une entrée par
  carrière (`contributions <statut>-<génération>`) et une pour la grille
  (`impots de la grille`). « La grille a un objet » lit le portage.
- **L'empreinte figée est celle du moteur Python** : recalculée à part, par
  l'ancien code, elle tombe juste sur les onze carrières ; pour l'impôt, une
  fois les nombres lus en flottants (le portage écrit `0` où le Python écrit
  `0.0`), les 2 516 résultats sont identiques, aucun refus.
- **L'histoire des prélèvements** reste confrontée : son Python est un jumeau
  que le coût et la fabrique gardent, non le moteur d'une carrière.
- Le fichier n'entre plus dans le moteur Python : il quitte la liste de
  `test_fichiers_sur_le_moteur_python.py`.

## Ce qui reste

1. **Les `moitie_python`** de `test_moteur.py`, puis `test_web.py`. Même
   recette.
2. **Les deux tests qui refont les témoins au moteur Python**, à la session
   du site.
3. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** `test_cycle_de_vie_portage.py` : 15 passés (sous
`PRESOMPTIONS_DECALEES=1`, 15 sautés, comme avant) ;
`test_valeurs_figees.py` et `test_fichiers_sur_le_moteur_python.py` :
verts ; `pytest -m rapide` : 5 396 passés.
