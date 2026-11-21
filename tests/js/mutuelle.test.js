/**
 * La mutuelle d'entreprise que le lecteur dit (décision du propriétaire du
 * 21 novembre 2026) : facultative, en euros par mois, elle remplace le
 * forfait de 20 € de la fiche de paie (L. 911-7), et passe aux paramètres.
 *
 *     node --test tests/js/mutuelle.test.js
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { DEFAUTS, MUTUELLE_MAXIMUM, Saisie } from "../../moteur/js/saisie.js";

test("sans mutuelle dite, le forfait : aucun paramètre, rien dans l'adresse", () => {
  assert.equal(DEFAUTS.mutuelle, null);
  const saisie = Saisie.depuisRequete({});
  assert.equal(saisie.mutuelle, null);
  assert.equal(saisie.parametres(PARAMETRES_DEFAUT).mutuelle_mensuelle, null);
  assert.ok(!new URLSearchParams(saisie.requete()).has("mutuelle"));
});

test("la mutuelle dite passe aux paramètres et se relit dans l'adresse", () => {
  const saisie = Saisie.depuisRequete({ mutuelle: "35.5" });
  assert.equal(saisie.mutuelle, 35.5);
  assert.equal(saisie.parametres(PARAMETRES_DEFAUT).mutuelle_mensuelle, 35.5);
  const relue = Saisie.depuisRequete(Object.fromEntries(new URLSearchParams(saisie.requete())));
  assert.equal(relue.mutuelle, 35.5);
});

test("une mutuelle négative ou démesurée est refusée", () => {
  assert.throws(() => Saisie.depuisRequete({ mutuelle: "-1" }), /Mutuelle/);
  assert.throws(() => Saisie.depuisRequete({ mutuelle: String(MUTUELLE_MAXIMUM + 1) }),
    /Mutuelle/);
  assert.equal(Saisie.depuisRequete({ mutuelle: "0" }).mutuelle, 0);
});
