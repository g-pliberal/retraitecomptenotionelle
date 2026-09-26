/**
 * Le budget de calcul (docs/architecture.md, § 7.8), côté JavaScript : par
 * carrière, sur celles que les témoins simulent, pour le scénario 1 seul et
 * pour les six scénarios. `scripts/budget_calcul.py` l'appelle.
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte, Saisie } from "../moteur/js/pages.js";
import { Simulateur } from "../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..");
const temoins = JSON.parse(readFileSync(join(RACINE, "tests/temoins/simulations.json"), "utf8"));
const contexte = new Contexte(JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));

const saisies = [];
const simuler = Simulateur.prototype.simuler;
Simulateur.prototype.simuler = function (carriere, ...reste) {
  saisies.push([this, carriere]);
  return simuler.call(this, carriere, ...reste);
};
for (const temoin of Object.values(temoins)) {
  try {
    contexte.simuler(Saisie.depuisRequete(temoin.requete));
  } catch {
    // une saisie refusée ne simule rien
  }
}
Simulateur.prototype.simuler = simuler;

function mesurer(calcul, passes) {
  let meilleur = Infinity;
  for (let passe = 0; passe < passes; passe += 1) {
    const debut = performance.now();
    for (const [simulateur, carriere] of saisies) {
      calcul(simulateur, carriere);
    }
    meilleur = Math.min(meilleur, performance.now() - debut);
  }
  return meilleur / saisies.length;
}

const actuel = mesurer((s, c) => s.scenarioActuel.calculer(c), 10);
const tous = mesurer((s, c) => s.simuler(c), 5);
console.log(`JavaScript, ${saisies.length} carrières : ${actuel.toFixed(2)} ms pour le `
  + `scénario 1, ${tous.toFixed(2)} ms pour les six scénarios, par carrière.`);
