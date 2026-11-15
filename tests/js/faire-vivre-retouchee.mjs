/**
 * « Faire vivre » une liquidation dont la pension du régime général est
 * retouchée, avec le portage JavaScript.
 *
 * Reçoit en argument un fichier JSON — une liste de cas
 * `[options, montant, ecretement, annee]` : la carrière simple des options,
 * liquidée, sa pension du régime général portée à `montant`, son écrêtement
 * au maximum à `ecretement` — et écrit sur la sortie standard, pour chacun,
 * la pension vivante de l'année (`donnees()`) et ce que chaque régime sert
 * aujourd'hui. `tests/test_pension_maximale.py` en fige l'empreinte
 * (action 161).
 *
 *     node tests/js/faire-vivre-retouchee.mjs cas.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte } from "../../moteur/js/contexte.js";
import { faireVivre } from "../../moteur/js/revalorisation.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const simulateur = new Contexte(paquet).simulateur();
const cas = JSON.parse(readFileSync(process.argv[2], "utf8"));

process.stdout.write(JSON.stringify(cas.map(([options, montant, ecretement, annee]) => {
  const carriere = simulateur.carriereSimple(options);
  const resultat = simulateur.scenarioActuel.calculer(carriere);
  for (const pension of resultat.pensions_par_regime) {
    if (pension.regime === "regime_general") {
      pension.montant = montant;
      pension.ecretement_du_maximum = ecretement;
    }
  }
  const vivante = faireVivre(simulateur, carriere, resultat, annee);
  return [vivante.donnees(), vivante.regimes.map((r) => r.aujourd_hui)];
})));
