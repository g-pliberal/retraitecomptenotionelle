# Trois fichiers de la carrière à la façade : le relevé prolongé, la LODEOM et le micro-social

Vingt-troisième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-le-temps-partiel-a-la-facade.md`, « Ce qui reste », 1. Aucune
règle, aucune donnée, aucun témoin, aucune ligne de la façade ni du pont n'a
bougé : seuls les imports et les fixtures de trois fichiers de tests. La
suite complète de GitHub était verte sur `dc1ede0` et `e4919b8` ; celle de
`413398f` a été annulée par la suivante, celle de `81eb574` tournait au début
de l'étape.

## Ce qui est fait

**`test_oracle.py` attend.** Ses 3 065 lignes empruntent l'échéancier,
`departs`, `invalidite`, `ScenarioActuel` et trois tables du scénario
(`AgesAnnulationDecote`, `MinimumGaranti`, `ValeursPoint`) : plus d'une
étape. Celle-ci a pris les trois fichiers que `prolonger_releve` et
`salaire_moyen_annuel`, servis depuis la précédente, laissaient passer.

- **`test_releve_prolonge.py`** (8 tests) : `salaire_moyen_annuel` de la
  façade ; les séries qu'il reçoit sont celles d'un simulateur de la façade
  sous les paramètres de la saisie, et non plus du simulateur Python que
  `Saisies` tient.
- **`test_lodeom.py`** (11 tests) : `Simulateur` et `prolonger_releve` de la
  façade ; le bloc du droit en vigueur se lit du catalogue et des
  affiliations du simulateur, au lieu de `Affiliations` importé de
  `carriere.py`. Le test de jumelage confronte toujours `ConstructeurFiche`
  (Python, `remuneration.py`, hors de la liste) au portage ; sa moitié
  « carrières » confronte désormais le portage, par le pont, au portage
  appelé en direct : elle éprouve le pont, plus le jumeau Python.
- **`test_micro_social.py`** (75 tests) : `Carriere`, `ConstructeurCompte`,
  `Simulateur`, `acquerir`, `compter`, `coordonner`, `liquider` et
  `salaire_moyen_annuel` de la façade ; la fixture `macro`, qui lisait
  `DonneesMacro`, rend celles du simulateur de la façade.

Les trois quittent `FICHIERS` de `test_fichiers_sur_le_moteur_python.py`,
sans test marqué.

## Ce qui est mesuré

Les trois fichiers et `test_fichiers_sur_le_moteur_python.py` : verts ;
`python -m pytest -m rapide` : vert.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.

## Ce qui reste

1. `test_oracle.py` : l'échéancier, `departs`, `invalidite`, `ScenarioActuel`
   et trois tables du scénario, à servir d'abord ; une étape pour mesurer ce
   qui manque et servir l'échéancier, une autre pour le reste.
2. « Faire vivre » servi ouvre la voie aux fichiers qui l'appellent :
   `test_departs.py`, `test_invalidite.py`, `test_pension_maximale.py`,
   `test_majoration_*`, `test_pension_minimum_avant_1983.py`, et le test
   marqué de `test_liquidation.py`.
3. Les 37 tests marqués de `test_simulateur.py`.
