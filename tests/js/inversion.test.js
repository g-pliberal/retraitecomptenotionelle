/**
 * Le solveur de l'inversion, `niveauPourPension`, sur la pension que le
 * scénario 1 calcule (action 161, étape 8a : le solveur Python est parti, ses
 * deux tests de `tests/test_simulateur.py` passent ici, sur l'exemplaire que le
 * site exécute).
 *
 * La source est le contrat du solveur, `moteur/js/simulateur.js` : il cherche
 * le plus petit niveau dont la pension ATTEINT la cible, et dit, plutôt que de
 * rendre un chiffre approché, les trois cas où la pension n'est pas
 * inversible — le plancher du droit (minimum contributif, ASPA), le plafond du
 * statut, et le saut des 150 heures de SMIC qui valident quatre trimestres,
 * entre les bords duquel aucune carrière de cette forme ne sert rien.
 *
 *     node --test tests/js/inversion.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { Simulateur, niveauPourPension } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const simulateur = new Simulateur(paquet, PARAMETRES_DEFAUT);

/** La pension annuelle du scénario 1 d'un non-cadre du privé né en 1955,
 * de vingt à soixante-deux ans, au niveau `niveau` du salaire moyen. */
function pensionDeNiveau(niveau) {
  return simulateur.scenarioActuel.calculer(simulateur.carriereSimple({
    annee_naissance: 1955, sexe: "H", affiliation: "salarie_prive_non_cadre",
    age_debut: 20, age_liquidation: 62, niveau_salaire: niveau,
  })).pension_annuelle;
}

test("l'inversion retrouve le niveau dont on est parti", () => {
  for (const attendu of [0.6, 1.0, 1.7, 2.4]) {
    const trouve = niveauPourPension(pensionDeNiveau, pensionDeNiveau(attendu), 0.1, 10.0);
    assert.ok(trouve.atteinte, `niveau ${attendu} : cible manquée`);
    assert.ok(Math.abs(trouve.niveau - attendu) < 1e-3,
      `niveau ${attendu} : l'inversion rend ${trouve.niveau}`);
  }
});

test("l'inversion avoue ce qu'aucune carrière ne sert", () => {
  const plancher = pensionDeNiveau(0.1);
  const plafond = pensionDeNiveau(10.0);

  const tropBas = niveauPourPension(pensionDeNiveau, plancher / 2, 0.1, 10.0);
  assert.ok(!tropBas.atteinte && tropBas.sousLePlancher);
  assert.equal(tropBas.niveau, 0.1);

  const tropHaut = niveauPourPension(pensionDeNiveau, plafond * 2, 0.1, 10.0);
  assert.ok(!tropHaut.atteinte && tropHaut.auDessusDuPlafond);
  assert.equal(tropHaut.niveau, 10.0);

  // Le saut : une pension prise dans l'intervalle que le seuil des trimestres
  // laisse vide. L'inversion la manque, et l'encadre au lieu de l'ignorer.
  const saut = niveauPourPension(pensionDeNiveau, 6000.0, 0.1, 10.0);
  assert.ok(!saut.atteinte);
  assert.ok(!saut.sousLePlancher && !saut.auDessusDuPlafond);
  assert.ok(saut.pension_dessous < saut.cible && saut.cible < saut.pension);
});
