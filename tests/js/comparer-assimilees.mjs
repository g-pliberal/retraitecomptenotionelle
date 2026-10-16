/**
 * Compte les durées de chronologies avec le portage JavaScript.
 *
 * Reçoit en argument un fichier JSON — une liste de chronologies complétées,
 * celles que `tests/test_periodes_assimilees.py` construit — et écrit sur la
 * sortie standard, pour chacune, ce que l'étape « compter les durées » écrit
 * (`donnees()`), ou l'erreur levée. Le test compare le tout au Python.
 *
 *     node tests/js/comparer-assimilees.mjs chronologies.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Carriere } from "../../moteur/js/carriere.js";
import { Contexte } from "../../moteur/js/contexte.js";
import { construire } from "../../moteur/js/droit/releve.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const contexte = new Contexte(JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));
const simulateur = contexte.simulateur();
const chronologies = JSON.parse(readFileSync(process.argv[2], "utf8"));

const sortie = chronologies.map((chronologie) => {
  try {
    const carriere = Carriere.depuisChronologie(chronologie, simulateur.macro);
    return construire(simulateur.scenarioActuel, carriere).durees.donnees();
  } catch (erreur) {
    return { erreur: String(erreur.message ?? erreur) };
  }
});

process.stdout.write(JSON.stringify(sortie));
