/**
 * Les départs de « Mon estimation retraite », datés et chiffrés par le portage
 * JavaScript (`Contexte.departsDeLEstimation`).
 *
 * Reçoit en argument un fichier JSON — une liste de requêtes du formulaire — et
 * écrit sur la sortie standard, pour chacune, ses départs, ou l'erreur levée ;
 * un second argument nomme le droit contrefactuel sous lequel les dater
 * (`droit_contrefactuel`, action 138, étape 10). `tests/test_estimation_du_site.py`
 * compare le tout au Python.
 *
 *     node tests/js/comparer-estimation.mjs requetes.json [droit]
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Saisie } from "../../moteur/js/saisie.js";
import { Contexte } from "../../moteur/js/contexte.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const partage = new Contexte(JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));
const contexte = process.argv[3] === undefined ? partage
  : partage.pour({ ...partage.base, droit_contrefactuel: process.argv[3] });
const requetes = JSON.parse(readFileSync(process.argv[2], "utf8"));

const sortie = requetes.map((requete) => {
  try {
    const saisie = Saisie.depuisRequete(requete, false, contexte.paquet.presomptions);
    return contexte.departsDeLEstimation(saisie).map((depart) => ({
      quoi: depart.quoi,
      age: depart.age,
      date: depart.date,
      etages: depart.etages,
      total: depart.total,
      minimum_vieillesse: depart.minimum_vieillesse,
      trimestres: depart.trimestres,
      trimestres_requis: depart.trimestres_requis,
      motif_ouverture: depart.motif_ouverture,
      assiette_maladie: depart.assiette_maladie,
      assiette_regime_general: depart.assiette_regime_general,
    }));
  } catch (erreur) {
    return { erreur: String(erreur.message ?? erreur) };
  }
});

process.stdout.write(JSON.stringify(sortie));
