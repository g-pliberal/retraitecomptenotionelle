# Les indépendants et la santé au témoin : plus aucune confrontation par `comparer.mjs`, et `outils_portage.py` retiré

Action 161, étape 8o, après `2026-11-15-les-carrieres-au-hasard-au-temoin.md`.
Aucune règle du portage, aucune donnée n'a bougé ; cinq tests changent de juge.

## Ce qui est fait

- **Cinq confrontations figées** au témoin des valeurs. Elles faisaient
  simuler au moteur Python (`Saisies().simuler`) des requêtes que
  `tests/js/comparer.mjs` confrontait au portage : trois dans
  `test_independants.py` (points d'avant 1973, points d'invalidité, droits
  au conjoint), une dans `test_pcv_sante.py`, et une cinquième, que la note
  d'avant ne comptait pas, dans `test_saisie_assimilees.py` (périodes
  assimilées saisies). Le portage simule désormais seul les requêtes, et ce
  qu'il rend est figé. Avant de figer, chaque résultat a été recalculé par
  l'ancien chemin : seize cas, aucun écart au milliardième près.
- **`simulations_du_portage`** (`tests/outils_pont.py`) : le script node que
  `test_web.py` portait pour ses carrières au hasard, mis en commun ; les six
  tests s'en servent. L'empreinte des carrières au hasard n'a pas bougé.
- **`tests/outils_portage.py` retiré**, avec `moitie_python`. Ses deux tests
  de `test_outillage.py` éprouvaient en fait la mémoire des calculs (le code
  d'un calcul écrit hors du modèle, les fichiers qu'il lit) : ils passent par
  `memoire.memoriser`, sous une petite aide `_garder`, et gardent leurs
  assertions.
- `comparer.mjs` ne sert plus qu'à `scripts/verifier_prose.py`.

## Ce qui reste avant de retirer les règles Python

1. **Deux confrontations de `test_independants.py`** hors de `comparer.mjs` :
   les fixtures `deux_moteurs` (dispenses de l'assiette minimale) et
   `points_des_deux_moteurs` (cotisations complémentaires), qui bâtissent la
   carrière d'un relevé en Python et en comparent lignes, résultat ou points
   à ceux du portage.
2. **Les deux tests qui refont les témoins au moteur Python**, à la session
   du site.
3. **Les quelque cent fichiers de tests** de
   `test_fichiers_sur_le_moteur_python.py`.
4. `memoire.memoriser` garde son paramètre `fichiers_lus`, que plus rien
   n'emploie hors de son test : il partira avec le reste.
5. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.
