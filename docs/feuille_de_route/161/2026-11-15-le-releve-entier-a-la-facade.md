# Le relevé entier à la façade : ses lignes, ses étapes et ses drapeaux servis par le portage, et `test_droit.py` y passe

Dixième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-tests-de-reversion-a-la-facade.md`, « Ce qui reste », 1.
`tests/test_droit.py` passe à la façade : il quitte `FICHIERS` et entre dans
`RESTES` avec un seul test marqué, la confrontation des deux moteurs
(`tests/test_fichiers_sur_le_moteur_python.py`). Aucune règle, aucune donnée,
aucun témoin n'a bougé. `test_liquidation.py` n'est pas commencé.

## Ce qui est fait

**Le relevé entier.** `releve.construire` rend, en plus de ses durées et de
ses droits, l'enveloppe du contrat C.5 (`donnees()`, `lignes()`), les
groupes de la liquidation unique, sa coordination (régimes de chaque ligne,
carrière rétablie), ce qui ne tient à aucune année, les trimestres des
enfants, les points acquis, la majoration, les plafonds de durée et les points
gratuits, et ce que chaque étape écrit sous son schéma. Ses trois drapeaux
passent au portage, qui les refusait jusqu'ici.

**Les étapes seules.** Quatre entrées de plus, quinze en tout :
`coordonner.coordonner`, `compter.compter`, `acquerir.acquerir` et
`compter.cumul_plafonne`. Chaque objet de la façade garde la carrière et les
drapeaux dont il vient (`_Source`, `tests/facade.py`) ; le portage refait
l'étape de cette carrière (`etapes`, `pont.mjs`). Une coordination qui garde
la carrière reçue la rend elle-même, comme le Python.

**Ce qui est refusé.** Des durées comptées sous un drapeau, passées à une
règle : le portage refait celles du relevé par défaut. Des durées d'une autre
coordination passées à `acquerir`. Le filtre d'années de `cumul_plafonne`,
une fonction.

**Une retouche de test.** Le relevé de carrière déposé se bâtit par
`simulateur.carriere_releve`, servi, au lieu de `Carriere.depuis_releve`, que
la façade ne sert pas : la carrière est la même.

## Ce qui est mesuré

| `test_droit.py` | avant | après |
|---|---:|---:|
| tests sur le moteur Python | 19 | 1 (la confrontation) |

**Contre le jumeau.** `tests/test_facade_jumeau.py` confronte le relevé de
trois carrières sous chacun de ses drapeaux, et chaque étape seule, sous la
référence et sous les conventions du COR : au bit près.

**Les tests.** Quatre tests neufs dans `tests/test_facade.py`, vus rouges ;
un test retouché, le drapeau n'étant plus refusé. `-m rapide` (5 133),
`test_facade.py`, `test_facade_jumeau.py`, `test_droit.py`,
`test_reversion.py`, `test_simulateur.py`, `test_pont.py`, `test_oracle.py`,
`test_fichiers_sur_le_moteur_python.py` : verts.

## Ce qui reste

1. `test_liquidation.py` : 22 tests y entrent dans le moteur Python, par
   `liquidation` (le contexte, ses neutralisations, la cascade), `journal`,
   `echeancier`, `pilote`, `foyer`. La façade ne sert de `liquidation.liquider`
   que le taux et les pensions d'une carrière seule : la tranche commence par
   relever ce que chaque test en lit, et ce que le pont devrait rendre de plus.
2. Puis `test_cultes.py`, `test_bonifications_emplois.py` et les autres
   fichiers qui lisent le relevé ; `completer.points_rco_de_chef` ; les 37
   tests marqués de `test_simulateur.py`.
3. La confrontation marquée de `test_droit.py` part avec le moteur Python.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
