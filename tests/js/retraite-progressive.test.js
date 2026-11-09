/**
 * La retraite progressive se lit dans sa fiche (action 191, étape 1).
 *
 * Le portage n'écrit plus les dates ni les valeurs de la règle : il lit, à la
 * date d'effet, les paramètres de la version de `retraite_progressive` que le
 * paquet porte (`fiches_datees`). Les valeurs attendues viennent des textes
 * que chaque version cite : cent cinquante trimestres le 4 mai 1988, cent
 * soixante du 28 août 1993 au 8 juin 2006 (R. 351-39) ; l'âge de L. 351-1,
 * puis, le 22 janvier 2014, « diminué de deux années, sans pouvoir être
 * inférieur à soixante ans » (L. 351-15), « abaissé de deux ans » le
 * 1er septembre 2023 (D. 161-2-24), soixante ans le 1er septembre 2025 (décret
 * n° 2025-681) ; les tranches de R. 351-41 jusqu'au 18 décembre 2014, puis
 * « la différence entre 100 % et la quotité », de 40 à 80 %.
 *
 * Et la preuve que la fiche pilote : une version retouchée dans une copie du
 * paquet déplace ce que le portage rend.
 *
 *     node --test tests/js/retraite-progressive.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { DateMois } from "../../moteur/js/calendrier.js";
import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import * as progressive from "../../moteur/js/droit/progressive.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const FICHE = "retraite_progressive";

/** Le moteur du droit réel, sur ce paquet. */
function moteurSur(donnees) {
  return new Simulateur(donnees, { ...PARAMETRES_DEFAUT }).scenarioActuel;
}

/** Le paquet, une version de la fiche retouchée. */
function paquetRetouche(version, parametres) {
  const copie = structuredClone(paquet);
  const visee = copie.fiches_datees[FICHE].versions.find((v) => v.id === version);
  Object.assign(visee.parametres, parametres);
  return copie;
}

const moteur = moteurSur(paquet);

test("le paquet porte la fiche de la retraite progressive, ses huit versions", () => {
  const fiche = paquet.fiches_datees[FICHE];
  assert.ok(fiche, "la fiche manque à fiches_datees");
  assert.deepEqual(fiche.dates_qui_decident, ["liquidation.date_effet"]);
  assert.equal(fiche.versions.length, 8);
});

test("la règle est celle de la version qui vaut au jour de la demande", () => {
  assert.equal(progressive.regle(moteur, new DateMois(1988, 4)).existe, false);
  assert.equal(progressive.regle(moteur, new DateMois(1988, 6)).existe, true);
});

test("sans la fiche au paquet, le calcul s'arrête : aucun droit ne se refuse par défaut", () => {
  const copie = structuredClone(paquet);
  delete copie.fiches_datees[FICHE];
  assert.throws(() => progressive.regle(moteurSur(copie), new DateMois(2024, 1)),
    /retraite_progressive/);
});

test("la durée exigée vient de la fiche : 150, 160, puis 150 (R. 351-39)", () => {
  assert.equal(progressive.dureeRequise(moteur, new DateMois(1990, 1)), 150);
  assert.equal(progressive.dureeRequise(moteur, new DateMois(2000, 1)), 160);
  assert.equal(progressive.dureeRequise(moteur, new DateMois(2010, 1)), 150);
  assert.equal(progressive.dureeRequise(moteur, new DateMois(2024, 1)), 150);
  const autre = moteurSur(paquetRetouche("cent_soixante_trimestres_1993", { duree_requise: 170 }));
  assert.equal(progressive.dureeRequise(autre, new DateMois(2000, 1)), 170);
  assert.equal(progressive.dureeRequise(autre, new DateMois(2010, 1)), 150);
});

test("la fraction vient de la fiche : les tranches, puis ce qui manque à la quotité", () => {
  const avant = new DateMois(2000, 1);
  assert.equal(progressive.fraction(moteur, avant, 0.7, false), 0.3);
  assert.equal(progressive.fraction(moteur, avant, 0.5, false), 0.5);
  assert.equal(progressive.fraction(moteur, avant, 0.3, false), 0.7);
  assert.equal(progressive.fraction(moteur, avant, 0.9, false), null);
  const depuis = new DateMois(2020, 1);
  assert.equal(progressive.fraction(moteur, depuis, 0.6, false), 0.4);
  assert.equal(progressive.fraction(moteur, depuis, 0.3, false), null);
  assert.equal(progressive.fraction(moteur, depuis, 0.805, false), null);
  // Le fonctionnaire, de 50 à 90 % : son temps partiel (L. 612-1 du CGFP).
  assert.equal(progressive.fraction(moteur, new DateMois(2024, 1), 0.9, true), 0.1);
  assert.equal(progressive.fraction(moteur, new DateMois(2024, 1), 0.45, true), null);
  const autre = moteurSur(paquetRetouche("soixante_ans_2025", { quotite_maximum: 0.7 }));
  assert.equal(progressive.fraction(autre, new DateMois(2026, 1), 0.8, false), null);
  assert.equal(progressive.fraction(moteur, new DateMois(2026, 1), 0.8, false), 0.2);
});

test("les régimes ouverts et liquidés viennent de la fiche", () => {
  assert.ok(!progressive.regimesOuverts(moteur, new DateMois(2015, 1)).has("cnavpl"));
  assert.ok(progressive.regimesLiquides(moteur, new DateMois(1990, 1)).has("cnavpl"));
  assert.ok(!progressive.regimesLiquides(moteur, new DateMois(2015, 1)).has("cnbf"));
  assert.ok(progressive.regimesOuverts(moteur, new DateMois(2023, 9)).has("cnracl"));
  assert.ok(!progressive.regimesOuverts(moteur, new DateMois(2023, 8)).has("cnracl"));
  assert.ok(!progressive.regimesOuverts(moteur, new DateMois(2023, 9)).has("sncf"));
  assert.equal(progressive.regimesLiquides(moteur, new DateMois(2023, 9)), null);
});

test("la pension complète se recalcule depuis le 8 juin 2006 (D. 351-15)", () => {
  assert.equal(progressive.recalculee(moteur, new DateMois(2006, 6)), false);
  assert.equal(progressive.recalculee(moteur, new DateMois(2006, 7)), true);
  assert.equal(progressive.recalculee(moteur, new DateMois(1980, 1)), false);
});

test("le portage n'écrit plus ni les dates ni les valeurs de la règle", () => {
  for (const nom of ["DEBUT", "AGE_ABAISSE", "FRACTION_COMPLEMENTAIRE", "TOUS_REGIMES",
    "SOIXANTE_ANS", "RECALCUL", "DUREES", "REGIMES_1988", "REGIMES_2023", "LIQUIDES_1988",
    "FONCTION_PUBLIQUE"]) {
    assert.ok(!(nom in progressive), `${nom} est encore une constante du portage`);
  }
});
