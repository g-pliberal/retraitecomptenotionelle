/**
 * Calcule le coût agrégé avec le portage JavaScript, sous d'autres paramètres
 * que ceux du site, et rend ce que le modèle Python en compare.
 *
 * Reçoit en argument un fichier JSON — ``{parametres, annees}`` : les
 * paramètres qui s'écartent du défaut, et les années à lire — et écrit sur la
 * sortie standard, pour chaque année, le solde de chaque système et le facteur
 * d'assiette de la proposition, puis les soldes moyens de la projection, la
 * reconstitution du passé par la mécanique de la projection, et sa
 * décomposition en retraités et en pension moyenne relative.
 * `tests/test_cout.py` compare le tout au modèle Python.
 *
 * Il existe pour les paramètres que le site n'expose pas, et qu'aucune page
 * témoin ne couvre donc : la part des reportés en emploi, d'abord.
 *
 *     node tests/js/comparer-cout.mjs cout.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { SCENARIOS } from "../../moteur/js/cout.js";
import { Contexte } from "../../moteur/js/contexte.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const { parametres, annees } = JSON.parse(readFileSync(process.argv[2], "utf8"));

const contexte = new Contexte(paquet, { ...PARAMETRES_DEFAUT, ...parametres });
const cout = contexte.cout();
const solde = cout.solde;
const scenarios = SCENARIOS.map(([scenario]) => scenario);

const sortie = {
  annees: Object.fromEntries(annees.map((millesime) => {
    const ligne = solde.annee(millesime);
    return [millesime, {
      soldes: Object.fromEntries(scenarios.map((s) => [s, ligne.solde(s)])),
      facteur_assiette: ligne.facteurAssiette,
    }];
  })),
  soldes_moyens: Object.fromEntries(scenarios.map((s) => [
    s, solde.soldeMoyen(s, solde.premiereAnneeProjetee, solde.annees.at(-1).annee),
  ])),
  reconstitution: Object.fromEntries(cout.avenir.reconstitution()),
  decomposition: Object.fromEntries(cout.avenir.decomposition(cout.avenir.premiereAnneeProjetee)),
  // La borne haute de la fourchette : la dérive de chaque année, les soldes
  // moyens et la dette à l'horizon si l'écart au COR tenait au système actuel.
  derive: Object.fromEntries(cout.avenir.annees.map((ligne) => [ligne.annee, ligne.derive])),
  soldes_moyens_derive: Object.fromEntries(scenarios.map((s) => [
    s, cout.soldeDerive.soldeMoyen(s, solde.premiereAnneeProjetee, solde.annees.at(-1).annee),
  ])),
  dette_derive: Object.fromEntries(scenarios.map((s) => [s, cout.detteDerive.horizon(s)])),
};

process.stdout.write(JSON.stringify(sortie));
