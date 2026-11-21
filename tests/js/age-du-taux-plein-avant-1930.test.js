/**
 * L'âge du taux plein des assurés nés avant 1930.
 *
 * R. 351-27, 1°, rédaction du 21 décembre 1985 (LEGIARTI000006749434), jusqu'à
 * celle du 1er janvier 2009 (LEGIARTI000020082993) : « l'âge prévu au 1° de
 * l'article L. 351-8 est fixé à soixante-cinq ans », quelle que soit la
 * génération. La table par génération ne commençait qu'en 1930 : un régime qui
 * renvoie à la règle commune (`age_taux_plein_par_generation`) répondait alors
 * par la valeur de sa période, soixante-sept ans à la Carpimko de 1987, et
 * minorait la pension d'un auxiliaire médical né en 1925 parti à 65 ans.
 *
 *     node --test tests/js/age-du-taux-plein-avant-1930.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import * as ouvrir from "../../moteur/js/droit/ouvrir.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));

test("né en mai 1925, pension de 1990 : soixante-cinq ans (R. 351-27), et non la valeur de la période", () => {
  const simulateur = new Simulateur(paquet, { ...PARAMETRES_DEFAUT });
  const moteur = simulateur.scenarioActuel;
  const carriere = simulateur.carriereSimple({
    sexe: "H", niveau_salaire: 1.0, annee_naissance: 1925, mois_naissance: 5, jour_naissance: 10,
    affiliation: "salarie_prive_non_cadre", age_debut: 25, age_liquidation: 65,
  });
  for (const regime of ["carpimko_complementaire", "regime_general"]) {
    const periode = moteur.catalogue.obtenir(regime).periode(1990);
    assert.equal(ouvrir.ageTauxPlein(moteur, periode, carriere), 65, regime);
  }
});
