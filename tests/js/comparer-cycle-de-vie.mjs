/**
 * Les jumeaux que lit le cycle de vie, calculés par le portage JavaScript :
 * les contributions d'équilibre d'une carrière, l'impôt d'un foyer. Le cycle
 * de vie lui-même n'a plus qu'un exemplaire, le portage (action 161), que
 * `tests/js/cycle-de-vie.test.js` tient.
 *
 * Reçoit un fichier JSON — `{carrieres: [options], impots: [{annee, foyer,
 * unite, indexation}]}` — et écrit, pour chaque carrière aux options de
 * `carriereSimple`, ses contributions d'équilibre de chaque année ; pour
 * chaque foyer, son impôt, étape par étape.
 * `tests/test_cycle_de_vie_portage.py` compare le tout au modèle Python.
 *
 *     node tests/js/comparer-cycle-de-vie.mjs demande.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte } from "../../moteur/js/contexte.js";
import { contributionsDUneCarriere } from "../../moteur/js/contributions-equilibre.js";
import {
  chargerBaremesImpotRevenu, croissanceMacro, Declarant, Foyer, impotDuFoyer,
} from "../../moteur/js/impot-revenu.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const simulateur = new Contexte(paquet).simulateur();
const demande = JSON.parse(readFileSync(process.argv[2], "utf8"));

const contributions = demande.carrieres.map((options) => {
  try {
    return Object.fromEntries(
      contributionsDUneCarriere(simulateur, simulateur.carriereSimple(options)));
  } catch (erreur) {
    return { erreur: String(erreur.stack ?? erreur) };
  }
});

const baremes = chargerBaremesImpotRevenu(paquet);
const impots = demande.impots.map(({ annee, foyer, unite, indexation }) => {
  const resultat = impotDuFoyer(new Foyer({
    ...foyer, declarants: foyer.declarants.map((d) => new Declarant(d)),
  }), annee, baremes, {
    unite, indexation, croissance: croissanceMacro(simulateur.macro, indexation),
  });
  return { ...resultat, remarques: [...resultat.remarques] };
});

process.stdout.write(JSON.stringify({ contributions, impots }));
