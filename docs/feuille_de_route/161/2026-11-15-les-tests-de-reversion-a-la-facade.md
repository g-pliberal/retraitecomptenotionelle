# Les tests de réversion à la façade : la limite de cumul, les majorations forfaitaires et la liquidation servies par le portage

Neuvième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-le-regime-unique-a-la-facade.md`, « Ce qui reste », 1. Les quatre
fonctions de test de `tests/test_reversion.py` qui restaient marquées
`sur_le_moteur_python` la quittent : le fichier n'en a plus, et sort de
`RESTES` et de `FICHIERS` (`tests/test_fichiers_sur_le_moteur_python.py`).
Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Une règle privée du jumeau.** `regles_de_la_reversion._cumuler` est servie :
le portage exporte sa fonction `cumuler` (`droit/reversion.js`), qui
n'était pas exportée, et la façade la demande sans le tiret bas
(`droit.regle` de `pont.mjs`). C'est la seule règle privée déclarée dans
`pont.REGLES_DE_LA_FACADE`.

**Un module hors de `droit/`.** `revalorisation.majorations_forfaitaires`
est servie, `revalorisation.js` rejoignant les modules de la façade. Elle
reçoit une pension de régime : `PensionRegime` rejoint
`pont.TYPES_DE_LA_FACADE`, sous les noms du Python, que le portage écrit et
lit ; il n'entre pas dans `CLASSES_EN_CHAMEAU`.

**La liquidation.** Une onzième entrée, `liquidation.liquider`, liquide une
demande dans l'état d'une carrière seule, sous le contexte du moteur de la
façade. Elle rend ce que les tests en lisent : le taux des pensions et la
pension de chaque régime. La liquidation entière ne passe pas le pont : elle
tient son contexte, les tables du moteur. Un état qui porte un journal, des
pensions servies ou provisoires, un contexte qui neutralise ou observe, le
moteur Python sont refusés (`NonTransmissible`).

## Ce qui est mesuré

| `test_reversion.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 4 | 0 |

**Contre le jumeau.** `tests/test_facade_jumeau.py` confronte huit appels de
plus (quatre limites de cumul, dont la limite forfaitaire et une fiche sans
règle de cumul ; quatre séries de majorations) et cinq liquidations, sous la
référence et sous les conventions du COR : au bit près.

**Les tests.** Quatre tests neufs dans `tests/test_facade.py`, vus rouges
avant le code. `test_facade.py`, `test_facade_jumeau.py`,
`test_reversion.py`, `test_simulateur.py`, `test_pont.py`, `test_oracle.py`,
`test_fichiers_sur_le_moteur_python.py`, `-m rapide` : verts.

## Ce qui reste

1. Les autres fichiers de tests qui lisent le relevé (`test_droit.py`,
   `test_liquidation.py`, `test_cultes.py`, `test_bonifications_emplois.py`…),
   et les règles du simulateur ; `completer.points_rco_de_chef`. Restent
   aussi les 37 tests marqués de `test_simulateur.py`.
2. Ce que la mesure ne voit pas : 27 tests de `test_reversion.py` simulent
   par `saisies.simuler` (`tests/outils_pont.py`), dont le portage bâtit la
   carrière mais dont le simulateur est celui du Python. Ils passeront au
   portage quand `Saisies` simulera par la façade.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
