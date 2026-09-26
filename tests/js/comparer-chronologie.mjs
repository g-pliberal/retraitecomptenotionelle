/**
 * Construit des chronologies avec le portage JavaScript et les rend.
 *
 * Reçoit en argument un fichier JSON — une liste de saisies, chacune
 * `{ parcours: {...} }` ou `{ releve: {...} }`, les options de
 * `duParcours` ou de `duReleve` — et écrit sur la sortie standard, pour
 * chacune, la chronologie complétée par les présomptions du paquet, ou
 * l'erreur levée. `tests/test_chronologie.py` compare le tout au Python.
 *
 *     node tests/js/comparer-chronologie.mjs saisies.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import * as chrono from "../../moteur/js/chronologie.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const saisies = JSON.parse(readFileSync(process.argv[2], "utf8"));

const sortie = saisies.map((saisie) => {
  try {
    if (saisie.parcours) {
      const options = { ...saisie.parcours };
      if (options.interruptions) {
        options.interruptions = new Map(
          Object.entries(options.interruptions).map(([annee, motif]) => [Number(annee), motif]));
      }
      return { chronologie: chrono.completer(chrono.duParcours(options), paquet.presomptions) };
    }
    return { chronologie: chrono.completer(chrono.duReleve(saisie.releve), paquet.presomptions) };
  } catch (erreur) {
    return { erreur: String(erreur.message ?? erreur) };
  }
});

process.stdout.write(JSON.stringify(sortie));
