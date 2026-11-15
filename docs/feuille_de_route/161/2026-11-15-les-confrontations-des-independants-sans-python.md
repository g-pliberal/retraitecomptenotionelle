# Les confrontations des indépendants sans Python : les lignes figées, les points tenus aux textes

Action 161, étape 8p, après `2026-11-15-les-independants-et-la-sante-au-temoin.md`.
Aucune règle du portage, aucune donnée n'a bougé ; deux fixtures de
`test_independants.py` ne font plus travailler le moteur Python.

## Ce qui est fait

- **`deux_moteurs`** (dispenses et assiette minimale, trois tests) : la
  carrière n'est plus bâtie ni simulée en Python. Le portage rend les lignes
  et le résultat entier, figés au témoin des valeurs sous le nom de chaque
  test ; les assertions sur les lignes lisent celles du portage. Avant de
  figer, la suite du fichier passait encore avec l'ancienne confrontation,
  au milliardième près.
- **`points_des_deux_moteurs`** (cotisations complémentaires, neuf tests) :
  le jumeau Python est retiré. Chaque test tenait déjà les deux moteurs aux
  points que les textes donnent ; il y tient le portage seul. La fixture rend
  toujours `{"javascript": [...]}`, pour ne pas toucher aux neuf boucles.
- `_proches`, devenu sans usage, retiré.

## Ce qui reste avant de retirer les règles Python

1. **Les deux tests qui refont les témoins au moteur Python**, à la session
   du site.
2. **Les quelque cent fichiers de tests** de
   `test_fichiers_sur_le_moteur_python.py`.
3. `memoire.memoriser` garde son paramètre `fichiers_lus`, que plus rien
   n'emploie hors de son test.
4. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.
