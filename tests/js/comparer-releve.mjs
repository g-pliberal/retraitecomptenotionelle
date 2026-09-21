/**
 * Lit des relevés avec le portage JavaScript et rend ce qu'il en tire.
 *
 * Reçoit en argument un fichier JSON — une liste de relevés, chacun étant une
 * liste de lignes — et écrit sur la sortie standard, pour chacun, la saisie du
 * formulaire, les lignes ignorées, les régimes reconnus et les notes.
 * `tests/test_releve_lu.py` compare le tout à ce que rend le modèle Python.
 *
 *     node tests/js/comparer-releve.mjs relevés.json
 */

import { readFileSync } from "node:fs";

import { lireReleve, parametresDe } from "../../moteur/js/releve-lu.js";

const releves = JSON.parse(readFileSync(process.argv[2], "utf8"));

const sortie = releves.map((lignes) => {
  const lecture = lireReleve(lignes);
  return {
    ...parametresDe(lecture),
    ignorees: lecture.ignorees,
    regimes: lecture.regimes,
    notes: lecture.notes,
    naissance: lecture.naissance,
  };
});

process.stdout.write(JSON.stringify(sortie));
