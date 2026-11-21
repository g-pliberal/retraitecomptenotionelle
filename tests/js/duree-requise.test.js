/**
 * La durée requise se lit dans les versions de sa fiche (note de décision
 * 0009, étape 3, deuxième session).
 *
 * Le portage ne lit plus de table par génération, ni ses deux copies d'avant
 * réforme posées l'une sur l'autre (`TableRecouverte`) : il lit, dans le
 * paquet (`fiches_datees`), les versions de la fiche
 * `duree_requise_par_generation`, et la date d'effet de la pension choisit la
 * version.
 *
 * Les durées attendues viennent des textes : R. 351-45, I à III (« 160
 * trimestres […] applicable aux pensions prenant effet postérieurement au 31
 * décembre 2002, quelle que soit la date de naissance » ; « 155 trimestres
 * pour l'assuré né en 1938 » avant ; « 159 trimestres pour les assurés nés en
 * décembre 1942 et dont la pension prend effet au 1er janvier 2003 ») ; la loi
 * n° 2003-775, article 5, III, « à compter de 2009 » (162 pour le né en
 * 1950) ; le décret n° 2011-916, en vigueur le 3 août 2011 (166 pour le né en
 * 1955) ; L. 161-17-3 dans ses rédactions de 2014, de 2023 et de la
 * suspension ; la circulaire Cnav 2011/25 pour la pratique de la caisse.
 *
 *     node --test tests/js/duree-requise.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import * as lesRegimes from "../../moteur/js/regimes.js";
import { DureesRequises, FICHE_DE_LA_DUREE_REQUISE, FichesDatees } from "../../moteur/js/regimes.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const EFFET = "liquidation.date_effet";

/** La génération d'un mois de naissance, comme la carrière l'écrit. */
function generationDe(annee, mois) {
  return Math.round((annee + (mois - 1) / 12) * 1000) / 1000;
}

const durees = new DureesRequises(paquet);

test("le paquet porte la fiche de la durée requise, ses huit versions choisies à la date d'effet", () => {
  const fiche = paquet.fiches_datees[FICHE_DE_LA_DUREE_REQUISE];
  assert.ok(fiche, "la fiche manque à fiches_datees");
  assert.deepEqual(fiche.dates_qui_decident, [EFFET]);
  assert.deepEqual(fiche.versions.map((v) => v.id), [
    "cent_cinquante", "escalier_de_1993", "decembre_1942_au_1er_janvier_2003", "cent_soixante",
    "loi_de_2003", "loi_de_2014", "loi_de_2023", "suspension_de_2025"]);
});

// Né le, date d'effet, durée attendue, et pourquoi (le brief de l'étape).
const CAS = [
  [[1938, 3], "2002-07-01", 155, "R. 351-45, II : 155 trimestres au né en 1938"],
  [[1938, 3], "2003-02-01", 160, "R. 351-45, I : 160 quelle que soit la génération"],
  [[1942, 12], "2003-01-01", 159, "R. 351-45, III : décembre 1942, le 1er janvier 2003"],
  [[1942, 12], "2003-02-01", 160, "R. 351-45, I, le lendemain"],
  [[1942, 11], "2003-01-01", 160, "R. 351-45, I : le III ne vise que décembre"],
  [[1950, 3], "2008-12-01", 160, "avant 2009, la durée unique"],
  [[1950, 3], "2010-04-01", 162, "loi n° 2003-775, article 5, III : né en 1950"],
  [[1955, 3], "2011-09-01", 166, "décret n° 2011-916 : né en 1955"],
  [[1962, 3], "2022-01-01", 168, "L. 161-17-3, 2014"],
  [[1962, 3], "2023-10-01", 169, "L. 161-17-3, loi de 2023"],
  [[1965, 6], "2026-08-01", 172, "L. 161-17-3, loi de 2023"],
  [[1965, 6], "2026-09-01", 171, "L. 161-17-3, suspension"],
  [[1965, 2], "2026-09-01", 170, "L. 161-17-3, suspension : premier trimestre 1965"],
  [[1930, 3], "1990-04-01", 150, "R. 351-27 de 1985 : 150 trimestres"],
];

for (const [[annee, m], effet, attendu, pourquoi] of CAS) {
  test(`né en ${m}/${annee}, pension du ${effet} : ${pourquoi}`, () => {
    assert.equal(durees.aLEffet(effet).trimestres(generationDe(annee, m))[0], attendu);
  });
}

test("sans date d'effet, la durée est celle de la dernière version, le droit en vigueur", () => {
  assert.equal(durees.trimestres(generationDe(1965, 6))[0], 171);
  assert.equal(durees.trimestres(generationDe(1964, 6))[0], 170);
  assert.equal(durees.trimestres(1975)[0], 172);
});

// Les deux droits contrefactuels gardent la version d'avant la réforme qu'ils
// écartent, sans fin (couches `sans_la_reforme_de_2023`, `sans_la_suspension_de_2026`).
test("au 31 août 2023, le né en juin 1965 parti en septembre 2027 doit 169 trimestres", () => {
  const sous = new DureesRequises(paquet, new FichesDatees(paquet).sousLeDroit("au_31_aout_2023"));
  assert.equal(sous.aLEffet("2027-09-01").trimestres(generationDe(1965, 6))[0], 169);
});

test("sous la loi de 2023 sans la suspension, le même en doit 172", () => {
  const sous = new DureesRequises(
    paquet, new FichesDatees(paquet).sousLeDroit("loi_2023_sans_suspension"));
  assert.equal(sous.aLEffet("2027-09-01").trimestres(generationDe(1965, 6))[0], 172);
});

test("la version de la loi lit le décret n° 2010-1734 : 165 au né en 1953 parti en mai 2011", () => {
  // La caisse lui en opposait 164 (circulaire Cnav 2011/25) : une pratique de
  // caisse, que le moteur garde au code (`DUREES_AVANT_LE_DECRET`) et que
  // tests/test_cnav_exposes.py juge sur le simulateur.
  assert.equal(durees.aLEffet("2011-05-01").trimestres(generationDe(1953, 3))[0], 165);
  assert.ok(Array.isArray(lesRegimes.DUREES_AVANT_LE_DECRET));
});

// La loi de 2003 ne fixe la durée que génération par génération, par décret,
// jusqu'à 1957 : pour une pension datée d'avant le 22 janvier 2014 d'un né
// après 1957 (la liquidation fictive des droits acquis à une bascule), aucune
// version ne dit rien. La pension prend la durée du premier texte qui fixe
// celle de sa génération, comme la copie d'avant 2023 la lui donnait : 171
// trimestres au né en 1971 (L. 161-17-3 de 2014), et non 172 (2023).
test("une version muette pour la génération laisse à la pension la durée du premier texte qui la fixe", () => {
  assert.equal(durees.aLEffet("2013-06-01").trimestres(generationDe(1971, 2)), null);
  assert.equal(durees.deLaPension("2013-06-01", generationDe(1971, 2))[0], 171);
  assert.equal(durees.deLaPension("2010-04-01", generationDe(1950, 3))[0], 162);
});

test("le portage n'a plus de table recouverte ni de copie d'avant réforme", () => {
  for (const nom of ["TableRecouverte", "DureesRequisesAvantSuspension",
    "DureesRequisesAvantReforme2023", "REFORME_2023_EFFET", "GENERATION_REFORME_2023",
    "SUSPENSION_2026_EFFET", "GENERATIONS_SUSPENSION", "DUREE_UNIQUE_2003",
    "DUREE_UNIQUE_2003_EFFET", "GENERATION_DECEMBRE_1942", "DUREE_PAR_GENERATION_EFFET"]) {
    assert.equal(lesRegimes[nom], undefined, nom);
  }
  assert.equal(paquet.durees_requises_avant_suspension, undefined);
  assert.equal(paquet.durees_requises_avant_reforme_2023, undefined);
});
