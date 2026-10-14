/**
 * Calcule les indicateurs de cycle de vie avec le portage JavaScript.
 *
 * Reçoit un fichier JSON — `{cas: [{carriere, conventions}], equilibres:
 * [{generation, sexe}]}` — et écrit, pour chaque cas, les contributions
 * d'équilibre de la carrière et ses indicateurs sous chaque convention ; pour
 * chaque génération, ses âges d'équilibre. `tests/test_cycle_de_vie_portage.py`
 * compare le tout au modèle Python.
 *
 *     node tests/js/comparer-cycle-de-vie.mjs demande.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte } from "../../moteur/js/contexte.js";
import { contributionsDUneCarriere } from "../../moteur/js/contributions-equilibre.js";
import {
  ageDeDecesCor, ageDEquilibre, ageDePartDeVieConstante, Convention,
  indicateursDesSystemes, tauxDePrelevement,
} from "../../moteur/js/cycle-de-vie.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const simulateur = new Contexte(paquet).simulateur();
const demande = JSON.parse(readFileSync(process.argv[2], "utf8"));

const cas = demande.cas.map(({ carriere: options, conventions }) => {
  try {
    const carriere = simulateur.carriereSimple(options);
    const comparaison = simulateur.simuler(carriere);
    const indicateurs = {};
    for (const [nom, champs] of Object.entries(conventions)) {
      const reglages = { ...champs };
      if (reglages.age_deces === "cor") {
        reglages.age_deces = ageDeDecesCor(simulateur.mortalite, carriere.annee_naissance);
      }
      const systemes = indicateursDesSystemes(simulateur, comparaison, new Convention(reglages));
      indicateurs[nom] = Object.fromEntries(Object.entries(systemes)
        .map(([scenario, valeurs]) => [scenario, valeurs.dictionnaire()]));
    }
    return {
      contributions: Object.fromEntries(contributionsDUneCarriere(simulateur, carriere)),
      taux_de_prelevement: tauxDePrelevement(simulateur, comparaison.actuel),
      indicateurs,
    };
  } catch (erreur) {
    return { erreur: String(erreur.stack ?? erreur) };
  }
});

const equilibres = demande.equilibres.map(({ generation, sexe }) => {
  const age = ageDEquilibre(simulateur, generation, sexe);
  return {
    age: age.age, au_mois: age.au_mois, coefficient: age.coefficient,
    part_de_vie: ageDePartDeVieConstante(simulateur, generation, sexe),
    part_de_vie_cor: ageDePartDeVieConstante(simulateur, generation, sexe, true),
  };
});

process.stdout.write(JSON.stringify({ cas, equilibres }));
