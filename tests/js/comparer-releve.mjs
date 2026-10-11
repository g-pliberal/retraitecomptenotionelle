/**
 * Lit des relevés avec le portage JavaScript et rend ce qu'il en tire.
 *
 * Reçoit en argument un fichier JSON — une liste de relevés, chacun étant une
 * liste de lignes — et écrit sur la sortie standard, pour chacun, la saisie du
 * formulaire, les lignes ignorées, les régimes reconnus et les notes.
 * `tests/test_releve_lu.py` compare le tout à ce que rend le modèle Python.
 * Avec `points`, la lecture convertit les points des années sans montant au
 * barème du modèle, comme le site.
 *
 *     node tests/js/comparer-releve.mjs relevés.json [points]
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte } from "../../moteur/js/contexte.js";
import { revenuDesPoints } from "../../moteur/js/droit/releve.js";
import { lireReleve, parametresDe } from "../../moteur/js/releve-lu.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const releves = JSON.parse(readFileSync(process.argv[2], "utf8"));
let convertir = null;
if (process.argv[3] === "points") {
  const contexte = new Contexte(JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));
  const moteur = contexte.simulateur().scenarioActuel;
  convertir = (...arguments_) => revenuDesPoints(moteur, ...arguments_);
}

const sortie = releves.map((lignes) => {
  const lecture = lireReleve(lignes, null, convertir);
  return {
    ...parametresDe(lecture),
    ignorees: lecture.ignorees,
    regimes: lecture.regimes,
    notes: lecture.notes,
    naissance: lecture.naissance,
    mois_de_naissance: lecture.moisDeNaissance,
  };
});

process.stdout.write(JSON.stringify(sortie));
