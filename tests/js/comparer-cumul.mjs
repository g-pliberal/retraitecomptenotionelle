/**
 * Simule des parcours avec le portage JavaScript et rend leurs résultats.
 *
 * Reçoit en argument un fichier JSON — une liste d'options de
 * `carriereParcours`, activités cumulées comprises — et écrit sur la sortie
 * standard, pour chacune, le dictionnaire de la comparaison ou l'erreur levée.
 * `tests/test_cumul_activites.py` compare le tout au modèle Python.
 *
 *     node tests/js/comparer-cumul.mjs parcours.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte } from "../../moteur/js/pages.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const simulateur = new Contexte(paquet).simulateur();

const parcours = JSON.parse(readFileSync(process.argv[2], "utf8"));

const sortie = parcours.map((options) => {
  try {
    return { resultat: simulateur.simuler(simulateur.carriereParcours(options)).dictionnaire() };
  } catch (erreur) {
    return { erreur: String(erreur.message ?? erreur) };
  }
});

process.stdout.write(JSON.stringify(sortie));
