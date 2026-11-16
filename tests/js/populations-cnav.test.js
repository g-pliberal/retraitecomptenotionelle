/**
 * Les populations de la Cnav par type de pension — normale, pour inaptitude,
 * d'ex-invalide —, publiées à plusieurs âges (action 161, étape 9l) : leurs
 * facteurs de mortalité sont par tranche d'âge, comme `facteurs_par_age` du
 * Python les cale, et le portage les lit au paquet, ou les recalibre à défaut.
 *
 * Les valeurs attendues viennent de la source : les espérances de vie que la
 * Cnav publie de 62 à 85 ans pour l'année observée
 * (`data/reference/mortalite/esperances_vie_pensions_cnav.csv`), que la table
 * corrigée, du moment, doit rendre à chaque âge publié.
 *
 *     node --test tests/js/populations-cnav.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { DonneesMortalite } from "../../moteur/js/mortalite.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur", "donnees.json"), "utf8"));

/** Les espérances publiées : `{population|sexe: [annee, {âge: espérance}]}`. */
function publiees() {
  const texte = readFileSync(
    join(RACINE, "data", "reference", "mortalite", "esperances_vie_pensions_cnav.csv"), "utf8");
  const lignes = texte.split("\n").filter((l) => l.trim() && !l.trimStart().startsWith("#"));
  const entete = lignes[0].split(",");
  const table = {};
  for (const ligne of lignes.slice(1)) {
    const champs = Object.fromEntries(ligne.split(",").map((v, i) => [entete[i], v]));
    const cle = `${champs.population}|${champs.sexe}`;
    table[cle] ??= [Number(champs.annee), {}];
    table[cle][1][Number(champs.mesure.replace("e", ""))] = Number(champs.valeur);
  }
  return table;
}

const PUBLIEES = publiees();

test("la Cnav publie trois types de pension, pour les deux sexes, à six âges", () => {
  assert.deepEqual(Object.keys(PUBLIEES).sort(), [
    "cnav_ex_invalide|F", "cnav_ex_invalide|H", "cnav_inaptitude|F", "cnav_inaptitude|H",
    "cnav_pension_normale|F", "cnav_pension_normale|H"]);
  for (const [, esperances] of Object.values(PUBLIEES)) {
    assert.deepEqual(Object.keys(esperances).map(Number), [62, 65, 70, 75, 80, 85]);
  }
});

for (const [nom, donnees] of [
  ["lus au paquet", () => new DonneesMortalite(paquet)],
  ["recalibrés à défaut", () => {
    const sans = { ...paquet, populations: { ...paquet.populations, facteurs_par_age: {} } };
    return new DonneesMortalite(sans);
  }],
]) {
  test(`les facteurs par tranche, ${nom}, rendent chaque espérance publiée`, () => {
    const mortalite = donnees();
    for (const [cle, [annee, esperances]] of Object.entries(PUBLIEES)) {
      const [population, sexe] = cle.split("|");
      for (const [age, publiee] of Object.entries(esperances)) {
        const rendue = mortalite.esperanceResiduelle(Number(age), annee, sexe, false, population);
        assert.ok(Math.abs(rendue - publiee) < 1e-6, `${cle} à ${age} ans : ${rendue} pour ${publiee}`);
      }
    }
  });
}

test("une tranche par âge publié, la première dès la naissance", () => {
  const facteurs = new DonneesMortalite(paquet).facteursParAge("cnav_inaptitude", "H");
  assert.deepEqual(facteurs.map(([age]) => age), [0, 65, 70, 75, 80, 85]);
  // La surmortalité des inaptes s'éteint avec l'âge : la Cnav les voit
  // rejoindre la population générale au-delà de 80 ans.
  assert.ok(facteurs[0][1] > 1 && facteurs[0][1] > facteurs[5][1]);
});

test("une population publiée à 65 ans seul n'a qu'une tranche, son facteur", () => {
  const mortalite = new DonneesMortalite(paquet);
  assert.deepEqual(mortalite.facteursParAge("fonctionnaires_civils_etat", "F"),
    [[0, mortalite.facteurPopulation("fonctionnaires_civils_etat", "F")]]);
});

test("le facteur unique d'une population publiée à plusieurs âges est refusé", () => {
  assert.throws(() => new DonneesMortalite(paquet).facteurPopulation("cnav_inaptitude", "H"),
    /plusieurs âges/);
});
