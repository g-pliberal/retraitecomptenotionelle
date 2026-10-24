/**
 * La saisie du portage, ce que seul node en voit.
 *
 * Une saisie reçoit les valeurs des défauts telles quelles (`Object.assign`) :
 * un tableau des défauts qui ne serait pas gelé, une saisie qui y écrirait
 * l'écrirait pour toutes celles qui suivent. `DEFAUTS.demandes` était le seul
 * à ne pas l'être (action 161, étape 6 : la relecture de `saisie.py`). Le
 * pont, qui rend des copies, ne le voit pas : ce que la saisie lit et réécrit
 * d'une adresse s'éprouve, lui, dans `test_saisie_de_l_adresse.py`.
 *
 *     node --test tests/js/*.test.js
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { DEFAUTS, Saisie } from "../../moteur/js/saisie.js";

test("chaque tableau des défauts est gelé : une saisie n'y écrit pas pour les suivantes", () => {
  const tableaux = Object.entries(DEFAUTS).filter(([, valeur]) => Array.isArray(valeur));
  assert.ok(tableaux.length > 1, "les défauts ne portent plus de tableaux");
  for (const [cle, valeur] of tableaux) {
    assert.ok(Object.isFrozen(valeur), `DEFAUTS.${cle} n'est pas gelé`);
  }
  assert.throws(() => new Saisie().demandes.push(["regime_general", 64]), TypeError);
  assert.deepEqual(new Saisie().demandes, []);
});
