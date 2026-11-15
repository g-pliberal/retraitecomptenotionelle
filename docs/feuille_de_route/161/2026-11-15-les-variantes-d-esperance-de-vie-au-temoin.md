# Les variantes d'espérance de vie au témoin : `test_moteur.py` ne confronte plus au moteur Python

Action 161, étape 8m, après `2026-11-15-les-contributions-et-l-impot-au-temoin.md`.
Aucune règle du portage, aucune donnée n'a bougé ; un test change de juge.

## Ce qui est fait

- **La suite GitHub** : verte au départ de l'étape (`0fdc849`).
- **`test_le_portage_javascript_lit_les_memes_variantes`**, seul
  `moitie_python` de `test_moteur.py`, faisait simuler au moteur Python trois
  carrières (une salariée de 1975, un fonctionnaire de 1990, un artisan de
  1962) sous les hypothèses basse et haute d'espérance de vie, puis les
  confrontait au portage. Vu vert d'abord, il fige désormais ce que le
  portage rend au témoin des valeurs (`simulations des variantes`), et
  vérifie que les deux hypothèses donnent bien des simulations distinctes.
  Le refus d'une hypothèse inconnue reste éprouvé.
- **L'empreinte figée est celle du moteur Python** : recalculée à part, par
  l'ancien code, elle tombe juste une fois les entiers lus en flottants ;
  aucun écart, valeur par valeur, entre les deux moteurs.
- `_simulations_des_variantes` et `_ecarts_au_portage` sont retirés.
  `test_moteur.py` reste sur la liste de
  `test_fichiers_sur_le_moteur_python.py` : ses autres tests importent les
  règles Python (indexation, âge de référence, conversion, fusion…).

## Ce qui reste

1. **Le `moitie_python` de `test_web.py`**. Même recette.
2. **Les deux tests qui refont les témoins au moteur Python**, à la session
   du site.
3. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** `test_moteur.py`, `test_valeurs_figees.py` et
`test_fichiers_sur_le_moteur_python.py` : 91 passés ; `pytest -m rapide` :
5 396 passés.
