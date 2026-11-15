/**
 * Simule des requêtes du formulaire avec le portage JavaScript, comme le site.
 *
 * Reçoit en argument un fichier JSON — une liste de requêtes du formulaire —
 * et écrit sur la sortie standard, pour chacune, la comparaison entière que
 * le site en tire (`dictionnaire()`), ou l'erreur levée. Le témoin des
 * sorties en fige l'empreinte (`tests/outils_sorties.py`, action 161).
 *
 *     node tests/js/simuler.mjs requetes.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Saisie } from "../../moteur/js/saisie.js";
import { Contexte } from "../../moteur/js/contexte.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const contexte = new Contexte(JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));
const requetes = JSON.parse(readFileSync(process.argv[2], "utf8"));

const sortie = requetes.map((requete) => {
  try {
    return contexte.simuler(
      Saisie.depuisRequete(requete, false, contexte.paquet.presomptions)).dictionnaire();
  } catch (erreur) {
    return { erreur: String(erreur.message ?? erreur) };
  }
});

process.stdout.write(JSON.stringify(sortie));
