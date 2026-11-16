/**
 * L'âge de référence et l'écart d'anticipation (action 161, quatrième vague) :
 * ce que `tests/test_moteur.py` éprouvait sur `AgeReference` du moteur
 * Python, éprouvé sur celle du site (`moteur/js/age-reference.js`).
 *
 * Aucune valeur attendue ne vient du moteur : le cliquet qui ne redescend
 * jamais est un sens de variation ; 65 ans en 1990, 60 ans sans cliquet, 67
 * ans l'année d'avant la bascule sont l'âge du taux plein que le droit fixait,
 * avant et après 1982, et après 2010 ; 65 ans après la bascule est l'âge légal
 * de départ de la proposition.
 *
 *     node --test tests/js/age-reference.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { AgeReference } from "../../moteur/js/age-reference.js";
import { ModeAgeReference, PARAMETRES_DEFAUT, avec } from "../../moteur/js/config.js";
import { DonneesMortalite } from "../../moteur/js/mortalite.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur", "donnees.json"), "utf8"));
const mortalite = new DonneesMortalite(paquet);

/** L'âge de référence sous les réglages de référence, retouchés de `modifications`. */
const reference = (modifications = {}) => new AgeReference(
  paquet, avec(PARAMETRES_DEFAUT, modifications), mortalite);

/** Comme `pytest.approx` : 10⁻⁶ relatif, 10⁻¹² absolu. */
const proche = (lu, attendu) => assert.ok(
  Math.abs(lu - attendu) <= Math.max(1e-12, 1e-6 * Math.abs(attendu)),
  `${lu} au lieu de ${attendu}`);

test("le cliquet ne redescend jamais", () => {
  // Le mode est nommé : le défaut, lui, abaisse la référence à la bascule.
  const regle = reference({ mode_age_reference: ModeAgeReference.CLIQUET_LEGAL });
  let precedent = 0;
  for (let annee = 1945; annee <= 2030; annee += 1) {
    const courant = regle.age(annee);
    assert.ok(courant >= precedent, `l'âge de référence recule en ${annee}`);
    precedent = courant;
  }
});

test("le défaut tient le cliquet, puis fixe l'âge légal de la proposition", () => {
  // Deux paramètres, `age_reference_fixe` et `age_legal_liberal`, aux défauts
  // égaux : régler l'un ne règle pas l'autre. La bascule est du second côté.
  const parametres = PARAMETRES_DEFAUT;
  assert.equal(parametres.mode_age_reference, ModeAgeReference.FIXE_APRES_BASCULE);
  assert.equal(parametres.age_reference_fixe, 65);
  assert.equal(parametres.age_legal_liberal, 65);
  const regle = reference();
  assert.equal(regle.age(1990), 65);
  assert.equal(regle.age(parametres.annee_bascule - 1), 67);
  assert.equal(regle.age(parametres.annee_bascule), 65);
  assert.equal(regle.age(2070), 65);
});

test("l'abaissement de 1982 ne baisse pas la référence", () => {
  // Cœur du cahier des charges : partir à 60 ans en 1990, c'est anticiper de
  // cinq ans.
  const regle = reference();
  assert.equal(regle.age(1990), 65);
  const ecart = regle.ecart(60, 1990);
  proche(ecart.ecart, 5);
  assert.equal(ecart.anticipe, true);
});

test("sans cliquet, la référence suit le droit positif", () => {
  const regle = reference({ mode_age_reference: ModeAgeReference.LEGAL_SANS_CLIQUET });
  assert.equal(regle.age(1990), 60);
  proche(regle.ecart(60, 1990).ecart, 0);
});

test("un départ de régime spécial à 50 ans en 1990 anticipe de quinze ans", () => {
  proche(reference().ecart(50, 1990).ecart, 15);
});

test("le report se compte négativement", () => {
  const ecart = reference().ecart(69, 2026);
  assert.ok(ecart.ecart < 0, String(ecart.ecart));
  assert.equal(ecart.anticipe, false);
});
