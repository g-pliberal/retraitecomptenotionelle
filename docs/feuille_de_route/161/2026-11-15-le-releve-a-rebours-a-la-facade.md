# Le relevé à rebours à la façade : les points d'une année et le revenu qu'ils supposent servis par le portage, deux fichiers y passent

Dix-neuvième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-minima-agricoles-a-la-facade.md`, « Ce qui reste », 1 : une
première tranche cohérente des six fichiers du relevé. Aucune règle, aucune
donnée, aucun témoin n'a bougé. La suite complète de GitHub était verte sur
`ca030fa` au début de l'étape ; ses courses sur `83971c1` et `d09e207`
tournaient encore.

## Ce qui est fait

**Les deux règles du relevé à rebours** (action 138, étape 11),
`releve.points_de_l_annee` et `releve.revenu_des_points`, sont servies par
le portage : `"releve"` entre dans `REGLES_DE_LA_FACADE` (`pont.py`) et dans
`MODULES_DU_DROIT` (`pont.mjs`), `RevenuDesPoints` dans
`CLASSES_EN_CHAMEAU` (le portage écrit `auPlafond`). `facade.releve` les
sert à côté de `construire`, par une `Regles` du module.

**`test_revenu_des_points.py` et `test_releve_lu.py` passent entiers à la
façade** : leurs `Simulateur` et leurs deux règles viennent de `facade`, sans
test marqué ; ils quittent `FICHIERS`, et n'importent pas `entrees_du_test`.
Aucun fichier n'en emprunte de fonction.

## Ce qui est mesuré

Un test neuf dans `tests/test_facade.py` (le plafond de 2015, 550 points à
cinq plafonds ; avant 2004, aucun revenu), cinq appels confrontés au jumeau
dans `tests/test_facade_jumeau.py`. `-m rapide` (5 175), `test_facade.py`,
`test_facade_jumeau.py`, `test_pont.py`, les confrontations légères, les
deux fichiers et `test_fichiers_sur_le_moteur_python.py` : verts.

## Ce qui reste

1. `test_referents.py` (`points_de_l_annee` y est servi ; restent
   `droit.foyer`, `scenarios.actuel`, `Carriere`), `test_sections_liberales.py`
   (`compter`, `acquerir`, `coordonner`, `completer._taux_majoration_enfants`,
   `noyau.carte`), `test_temps_partiel.py` (`releve`, `chronologie`),
   `test_oracle.py` (l'échéancier, `departs`, `invalidite`, des tables du
   scénario).
2. « Faire vivre » servi ouvre la voie aux fichiers qui l'appellent :
   `test_departs.py`, `test_invalidite.py`, `test_pension_maximale.py`,
   `test_majoration_*`, `test_pension_minimum_avant_1983.py`, et le test
   marqué de `test_liquidation.py`.
3. Les 37 tests marqués de `test_simulateur.py`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
