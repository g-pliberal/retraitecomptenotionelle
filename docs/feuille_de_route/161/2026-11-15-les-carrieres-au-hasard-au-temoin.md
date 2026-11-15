# Les carrières au hasard au témoin : plus aucun `moitie_python` dans les tests

Action 161, étape 8n, après `2026-11-15-les-variantes-d-esperance-de-vie-au-temoin.md`.
Aucune règle du portage, aucune donnée n'a bougé ; un test change de juge.

## Ce qui est fait

- **`test_le_portage_javascript_concorde_sur_des_carrieres_tirees_au_hasard`**
  (`test_web.py`), dernier `moitie_python` des tests, faisait simuler au
  moteur Python soixante carrières tirées au hasard (graine fixe), puis
  `tests/js/comparer.mjs` les confrontait au portage. Vu vert d'abord, il
  tire désormais les seules requêtes (`_requetes_au_hasard`, même tirage),
  le portage les simule ou les refuse, et ce qu'il rend est figé au témoin
  des valeurs (`carrières tirées au hasard`). Le test vérifie aussi qu'une
  part des carrières est calculée, et une part refusée.
- **L'empreinte figée est celle du moteur Python** : recalculée à part par
  l'ancien chemin, elle tombe juste une fois les entiers lus en flottants,
  et les sept refus (cas 22, 26, 28, 44, 46, 47, 53) sont les mêmes des deux
  côtés.
- `moitie_python` n'a plus d'appelant hors de ses propres tests
  (`test_outillage.py`) : `outils_portage.py` pourra partir avec eux.

## Ce qui reste avant de retirer les règles Python

1. **Quatre confrontations sans `moitie_python`**, qui font simuler au
   moteur Python par `Saisies().simuler` puis passent par `comparer.mjs` :
   les trois de `test_independants.py` (points d'avant 1973, points
   d'invalidité, droits au conjoint) et celle de `test_pcv_sante.py`. Même
   recette, une étape.
2. **Les deux tests qui refont les témoins au moteur Python**, à la session
   du site.
3. **`outils_portage.py` et ses tests** dans `test_outillage.py`, devenus
   sans objet.
4. **Les quelque cent fichiers de tests** de la liste de
   `test_fichiers_sur_le_moteur_python.py`, qui importent une règle Python
   (souvent par `Saisies()`, dont le simulateur par défaut est Python) :
   chacun passe à la façade ou au témoin, puis seulement les règles se
   retirent, par le haut.
5. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

