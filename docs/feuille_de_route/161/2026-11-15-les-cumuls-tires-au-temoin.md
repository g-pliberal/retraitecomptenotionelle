# Les cumuls tirés au témoin : les parcours au hasard ne se refont plus au moteur Python

Action 161, étape 8k, après `2026-11-15-l-age-conjoncturel-au-temoin.md`.
Aucune règle du portage, aucune donnée n'a bougé ; un test change de juge.

## Ce qui est fait

- **La suite GitHub** : verte au départ de l'étape (`cd51830`).
- **`test_le_portage_javascript_concorde_sur_des_cumuls_tires_au_hasard`**
  (`test_cumul_activites.py`) tirait quarante parcours, graine fixe, avec une
  à deux activités cumulées, les faisait simuler au moteur Python
  (`moitie_python`) et au portage (`tests/js/comparer-cumul.mjs`), puis
  confrontait chaque valeur, refus compris. Vu vert d'abord, il fige
  désormais ce que le portage rend au témoin des valeurs
  (`cumuls_tires_au_hasard`). Les statuts se tirent dans le paquet
  (`moteur/donnees.json`), dans le même ordre que le Python : les parcours
  sont les mêmes, vérifié.
- **L'empreinte figée est celle du moteur Python** : recalculée à part, par
  l'ancien code, elle tombe juste sur les 39 résultats, une fois les nombres
  lus en flottants (le JSON du portage écrit `3` où le Python écrit `3.0`),
  et le même parcours est refusé des deux côtés, au même message.
- `_cumuls_tires_au_hasard`, `_sans_nan` et `_ecarts` sont retirés ; les
  autres tests du fichier simulent encore au moteur Python sans rien
  confronter : ils partiront avec les cent fichiers qui importent une règle
  Python.

## Ce qui reste

1. **Les `moitie_python`** de `test_cycle_de_vie_portage.py`,
   `test_moteur.py`, `test_web.py`. Même recette.
2. **Les deux tests qui refont les témoins au moteur Python**, à la session
   du site.
3. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** `test_cumul_activites.py` : 32 passés ; sous
`PRESOMPTIONS_DECALEES=1`, 31 passés et 1 sauté par la garde ;
`test_valeurs_figees.py` et `test_fichiers_sur_le_moteur_python.py` :
verts ; `pytest -m rapide` : 5 396 passés.
