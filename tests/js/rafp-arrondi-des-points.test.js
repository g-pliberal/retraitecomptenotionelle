/**
 * Les points du RAFP, arrondis chaque année au point supérieur.
 *
 * Le décret n° 2004-569, article 5, dit seulement que le nombre de points de
 * l'année « est égal au rapport entre les cotisations versées […] et la
 * valeur d'acquisition du point » ; il ne dit pas d'arrondi. La caisse, elle,
 * arrondit les points de chaque année au point supérieur : sa page des
 * cotisations l'écrit (350 € en 2026, 239,79 points, 240), et sa calculette
 * de points le fait. Le scénario 1 étant le droit tel que la caisse
 * l'applique, le moteur arrondit comme elle. Les trois cas sont ceux que la
 * calculette de rafp.fr a rendus le 21 novembre 2026, part agent saisie, la
 * calculette doublant pour l'employeur : 14,99 € par mois en 2005, 360
 * points ; 15 € par mois en 2015, 315 ; 15 € par mois en 2026, 247.
 *
 *     node --test tests/js/rafp-arrondi-des-points.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { Contexte } from "../../moteur/js/contexte.js";
import { AnneeCarriere, Carriere } from "../../moteur/js/carriere.js";
import { acquerir, arrondirLesPointsDeLAnnee } from "../../moteur/js/droit/acquerir.js";
import { compter } from "../../moteur/js/droit/compter.js";
import { coordonner } from "../../moteur/js/droit/coordonner.js";

// Les salaires de référence du RAFP, ceux du dépôt (valeurs_point.csv).
const REFERENCE = { 2005: 1.0, 2015: 1.1452, 2026: 1.4596 };
const points = (annee, partAgentMensuelle) =>
  (2 * 12 * partAgentMensuelle) / REFERENCE[annee];

test("chaque année du RAFP s'arrondit au point supérieur, comme la calculette", () => {
  const credits = [
    ["rafp", 2005, points(2005, 14.99), null],
    ["rafp", 2015, points(2015, 15), null],
    ["rafp", 2026, points(2026, 15), null],
  ];
  const arrondis = arrondirLesPointsDeLAnnee(credits);
  assert.deepEqual(arrondis.map(([, annee, p]) => [annee, p]),
    [[2005, 360], [2015, 315], [2026, 247]]);
});

test("l'arrondi porte sur le total de l'année, non sur chaque période", () => {
  // Deux périodes de 2026 qui font ensemble 246,64 points : 247, non 248.
  const total = points(2026, 15);
  const arrondis = arrondirLesPointsDeLAnnee([
    ["rafp", 2026, total / 2, null], ["rafp", 2026, total / 2, null]]);
  const somme = arrondis.filter(([code]) => code === "rafp")
    .reduce((s, [, , p]) => s + p, 0);
  assert.equal(somme, 247);
});

test("un nombre entier de points ne monte pas, et les autres régimes ne bougent pas", () => {
  const arrondis = arrondirLesPointsDeLAnnee([
    ["rafp", 2010, 300.0000000001, null], ["agirc_arrco", 2026, 12.34, null]]);
  assert.deepEqual(arrondis.map(([code, annee, p]) => [code, annee, p]),
    [["rafp", 2010, 300], ["agirc_arrco", 2026, 12.34]]);
});

/**
 * Le relevé des points, année par année, porte les points arrondis : c'est
 * lui que la pension, le relevé et la conversion inverse lisent, et 246,64
 * points de 2026 y valent 247 comme dans le total (relecture du patch).
 */
test("le relevé des points du RAFP porte, chaque année, des points entiers", () => {
  const racine = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
  const paquet = JSON.parse(readFileSync(join(racine, "moteur/donnees.json"), "utf8"));
  const actuel = new Contexte(paquet).simulateur().scenarioActuel;
  const carriere = new Carriere({
    annee_naissance: 1975, sexe: "F", age_liquidation: 64, jour_naissance: 1,
    lignes: [2024, 2025, 2026].map((annee) => new AnneeCarriere({
      annee, affiliation: "fonctionnaire_etat", trimestres_valides: 4,
      revenu: 37_123.45, part_primes: 0.17,
    })),
  });
  const coordination = coordonner(actuel, carriere);
  const droits = acquerir(actuel, coordination, compter(actuel, coordination));
  const rafp = droits.points.filter(([code]) => code === "rafp");
  assert.ok(rafp.length > 0, "aucun point RAFP");
  for (const [, annee, points] of rafp) {
    assert.ok(Number.isInteger(points), `${annee} : ${points} points`);
  }
});
