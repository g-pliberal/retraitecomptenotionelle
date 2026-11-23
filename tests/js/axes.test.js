/**
 * Les axes du régime (note de décision 0009, amendement du 22 novembre 2026) :
 * le paquet porte les quatre blocs de chaque régime, et non plus des périodes
 * (étape 4), et le moteur les lit tels quels, sans plus en refaire de vue
 * (étape 5).
 *
 *     node --test tests/js/axes.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { CatalogueRegimes } from "../../moteur/js/regimes.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const BLOCS = ["structure", "liquidation", "cotisation", "servi"];

test("le paquet porte les quatre blocs, que le moteur lit tels quels", () => {
  const catalogue = new CatalogueRegimes(paquet);
  for (const fiche of paquet.regimes) {
    assert.equal(fiche.periodes, undefined, `${fiche.code} porte encore des périodes`);
    assert.equal(fiche.dates_d_effet, undefined, `${fiche.code} porte encore des dates d'effet`);
    const regime = catalogue.obtenir(fiche.code);
    assert.equal(regime.periodes, undefined, `${fiche.code} : le moteur refait des périodes`);
    for (const bloc of BLOCS) {
      assert.ok(Array.isArray(fiche[bloc]), `${fiche.code} sans bloc ${bloc}`);
      assert.deepEqual(regime[bloc], fiche[bloc], `${fiche.code}, ${bloc} lu tel quel`);
    }
  }
});
