/**
 * Simule des carrières de parcours avec le portage JavaScript.
 *
 * Reçoit en argument un fichier JSON — une liste d'options de
 * `Simulateur.carriereParcours` — et écrit sur la sortie standard, pour
 * chacune, la comparaison entière (`dictionnaire()`), ou l'erreur levée. Le
 * témoin des sorties en fige l'empreinte (`tests/outils_sorties.py`,
 * action 161).
 *
 *     node tests/js/simuler-parcours.mjs options.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const simulateur = new Simulateur(JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));
const options = JSON.parse(readFileSync(process.argv[2], "utf8"));

process.stdout.write(JSON.stringify(options.map((option) => {
  try {
    return simulateur.simuler(simulateur.carriereParcours(option)).dictionnaire();
  } catch (erreur) {
    return { erreur: String(erreur.message ?? erreur) };
  }
})));
