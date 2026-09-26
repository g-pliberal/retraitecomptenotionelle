/**
 * Construit le relevé des droits avec le portage JavaScript, étape par étape.
 *
 * Reçoit en argument un fichier JSON — une liste de requêtes du formulaire,
 * celles des témoins — et écrit sur la sortie standard, pour chacune, ce que
 * chaque étape de l'acquisition écrit (`donnees()` de la coordination, des
 * durées et des droits) et le relevé en lignes du contrat C.5, ou l'erreur
 * levée. `tests/test_droit.py` compare le tout au Python, étape par étape.
 *
 *     node tests/js/comparer-droit.mjs requetes.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { construire } from "../../moteur/js/droit/releve.js";
import { Contexte, Saisie } from "../../moteur/js/pages.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const contexte = new Contexte(JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));
const requetes = JSON.parse(readFileSync(process.argv[2], "utf8"));

// La carrière que le site simule est celle que la comparaison reçoit : on la
// saisit au passage, sans refaire le chemin du formulaire.
let saisie = null;
const simuler = Simulateur.prototype.simuler;
Simulateur.prototype.simuler = function (carriere, ...reste) {
  if (saisie === null) {
    saisie = [this, carriere];
  }
  return simuler.call(this, carriere, ...reste);
};

const sortie = requetes.map((requete) => {
  saisie = null;
  try {
    contexte.simuler(Saisie.depuisRequete(requete));
  } catch (erreur) {
    return { erreur: String(erreur.message ?? erreur) };
  }
  if (saisie === null) {
    return { erreur: "aucune carrière simulée" };
  }
  const [simulateur, carriere] = saisie;
  const releve = construire(simulateur.scenarioActuel, carriere);
  return {
    coordination: releve.coordination.donnees(),
    durees: releve.durees.donnees(),
    droits: releve.droits.donnees(),
    releve: releve.donnees(),
  };
});

process.stdout.write(JSON.stringify(sortie));
