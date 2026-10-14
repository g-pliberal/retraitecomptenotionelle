/**
 * Lit des relevés avec `moteur/js/releve-lu.js`, le lecteur du site, pour les
 * tests Python.
 *
 *     node tests/js/lire-releve.mjs cas.json
 *
 * Reçoit en argument un fichier JSON — une liste de cas, chacun
 * `{lignes, anneeMaximale, convertisseur}` — et écrit sur la sortie standard,
 * pour chacun, la lecture entière : les années lues, les interruptions, les
 * lignes ignorées, les régimes, les notes, la naissance, et la saisie du
 * formulaire. `tests/test_releve_lu.py` en tient les règles, et la lecture
 * figée des relevés d'essai (`tests/temoins/releves_lus.json`).
 *
 * Le convertisseur des points d'une année sans montant est `null` ; `"modele"`,
 * le barème du scénario 1 (`droit/releve.js`), comme le site ; ou `"par_cent"`,
 * un convertisseur d'essai, pour la mécanique de la lecture seule : cent euros
 * le point, au plafond à partir de cinq cents, rien sous dix.
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte } from "../../moteur/js/contexte.js";
import { revenuDesPoints } from "../../moteur/js/droit/releve.js";
import { lireReleve, parametresDe } from "../../moteur/js/releve-lu.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");

/** Cent euros le point, l'euro le plus proche ; au plafond à partir de cinq cents. */
function parCent(statut, annee, etage, points) {
  if (points < 10) return null;
  return { revenu: Math.floor(points * 100 + 0.5), auPlafond: points >= 500 };
}

let moteur = null;
function convertisseur(nom) {
  if (nom === "par_cent") return parCent;
  if (nom !== "modele") return null;
  if (moteur === null) {
    const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
    moteur = new Contexte(paquet).simulateur().scenarioActuel;
  }
  return (...arguments_) => revenuDesPoints(moteur, ...arguments_);
}

const cas = JSON.parse(readFileSync(process.argv[2], "utf8"));
const sortie = cas.map(({ lignes, anneeMaximale = null, convertisseur: nom = null }) => {
  const lecture = lireReleve(lignes, anneeMaximale, convertisseur(nom));
  return {
    lignes: lecture.lignes.map((ligne) => [ligne.annee, ligne.statut, ligne.revenu,
      ligne.trimestres, ligne.motif, ligne.source]),
    interruptions: lecture.interruptions,
    ignorees: lecture.ignorees,
    regimes: lecture.regimes,
    notes: lecture.notes,
    naissance: lecture.naissance,
    mois_de_naissance: lecture.moisDeNaissance,
    saisie: parametresDe(lecture),
  };
});

process.stdout.write(JSON.stringify(sortie));
