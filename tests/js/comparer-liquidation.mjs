/**
 * Liquide et journalise avec le portage JavaScript, étape par étape.
 *
 * Reçoit en argument un fichier JSON — une liste de requêtes du formulaire,
 * celles des témoins — et écrit sur la sortie standard, pour chacune, ce que
 * les étapes de la liquidation écrivent (`donnees()` de l'ouverture, des
 * pensions et des compléments), le journal de l'échéancier du scénario 1 et
 * le nombre d'appels de `liquider` que la simulation a faits, ou l'erreur
 * levée. `tests/test_liquidation.py` compare le tout au Python.
 *
 *     node tests/js/comparer-liquidation.mjs requetes.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { appels } from "../../moteur/js/droit/liquidation.js";
import { Contexte, Saisie } from "../../moteur/js/pages.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const contexte = new Contexte(JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));
const requetes = JSON.parse(readFileSync(process.argv[2], "utf8"));

// La comparaison que le site simule est celle que la comparaison reçoit : on
// la saisit au passage, sans refaire le chemin du formulaire.
let saisie = null;
const simuler = Simulateur.prototype.simuler;
Simulateur.prototype.simuler = function (carriere, ...reste) {
  const comparaison = simuler.call(this, carriere, ...reste);
  if (saisie === null) {
    saisie = comparaison;
  }
  return comparaison;
};

const sortie = requetes.map((requete) => {
  saisie = null;
  const avant = appels();
  try {
    contexte.simuler(Saisie.depuisRequete(requete));
  } catch (erreur) {
    return { erreur: String(erreur.message ?? erreur) };
  }
  if (saisie === null) {
    return { erreur: "aucune carrière simulée" };
  }
  const { journal } = saisie;
  const [liquidee] = [...journal].filter((e) => e.sorte === "liquidation").map((e) => e.contenu);
  return {
    ouverture: liquidee.ouverture.donnees(),
    pensions: liquidee.pensions.donnees(),
    complements: liquidee.complements.donnees(),
    journal: journal.donnees(),
    appels: appels() - avant,
  };
});

process.stdout.write(JSON.stringify(sortie));
