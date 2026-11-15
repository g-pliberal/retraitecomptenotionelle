/**
 * Le maximum du jour de la dernière majoration, avec le portage JavaScript.
 *
 * Reçoit en argument un fichier JSON — une liste de cas
 * `[pension, annee, depart, menee, ecretement, jusqua]` — et écrit sur la
 * sortie standard, pour chacun, ce que `maximumDuJour` rend.
 * `tests/test_pension_maximale.py` en fige l'empreinte (action 161).
 *
 *     node tests/js/maximum-du-jour.mjs cas.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte } from "../../moteur/js/contexte.js";
import { PensionServie, maximumDuJour } from "../../moteur/js/revalorisation.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const servie = new PensionServie(new Contexte(paquet).simulateur());
const cas = JSON.parse(readFileSync(process.argv[2], "utf8"));

process.stdout.write(JSON.stringify(cas.map(
  ([pension, annee, depart, menee, ecretement, jusqua]) =>
    maximumDuJour(servie, pension, annee, depart, menee, ecretement, jusqua))));
