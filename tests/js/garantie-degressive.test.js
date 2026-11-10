/**
 * La garantie vieillesse dégressive du scénario 6 (action 186, chantier 3).
 *
 * Décision 100 du programme (`docs/feuille_de_route_programme.md`), le 9
 * novembre 2026 : « Jusqu'à la moitié du plancher (525 € seul, 400 € en
 * couple), la pension est retirée en entier, comme aujourd'hui ; au-delà, de
 * moitié seulement, et le complément s'éteint à une fois et demie le plancher
 * (1 575 €, 1 200 €). » Décision 102 : « Le plancher d'une personne seule
 * reste 1 050 €, et la forme dégressive s'y applique en entier. »
 *
 * Les valeurs attendues sont posées à la main, en euros par mois de 2026
 * (`docs/feuille_de_route/186/2026-11-09-garantie-degressive.md`, « La
 * consigne de la session du modèle ») ; aucune ne vient du moteur.
 *
 *     node --test tests/js/garantie-degressive.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { PARAMETRES_DEFAUT, SituationFoyer } from "../../moteur/js/config.js";
import { coutGarantie, coutGarantieParSexe, manqueMoyen } from "../../moteur/js/garantie.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));

/** Quatre dixièmes du salaire moyen, partie à 66 ans en 2026 : le plancher est
 *  alors celui de la proposition, sans prix à lui appliquer. */
const MODESTE = {
  annee_naissance: 1960, sexe: "F", affiliation: "salarie_prive_non_cadre",
  age_debut: 21, niveau_salaire: 0.4,
};

/** Le complément mensuel que le moteur sert à des ressources mensuelles
 *  données, à 66 ans en 2026. */
const simulateurs = new Map();
function complement(parametres, ressourcesMensuelles) {
  if (!simulateurs.has(parametres)) simulateurs.set(parametres, new Simulateur(paquet, parametres));
  const simulateur = simulateurs.get(parametres);
  const carriere = simulateur.carriereSimple({ ...MODESTE, age_liquidation: 66 });
  assert.equal(carriere.anneeLiquidation, 2026);
  const garantie = simulateur.scenarioLiberal._garantieVieillesse(
    carriere, ressourcesMensuelles * 12.0);
  assert.equal(garantie.coefficient_prix, 1.0);
  return garantie.complement / 12.0;
}

const SEUL = { ...PARAMETRES_DEFAUT, situation_foyer: SituationFoyer.SEUL };
const COUPLE = { ...PARAMETRES_DEFAUT, situation_foyer: SituationFoyer.COUPLE };

const proche = (obtenu, attendu, quoi) => assert.ok(
  Math.abs(obtenu - attendu) < 1e-9, `${quoi} : ${obtenu}, attendu ${attendu}`);

test("la proposition porte la forme suédoise : la moitié du plancher, puis la moitié de la pension", () => {
  assert.equal(PARAMETRES_DEFAUT.part_retrait_entier_garantie, 0.5);
  assert.equal(PARAMETRES_DEFAUT.taux_retrait_garantie, 0.5);
});

test("seul, la pension est retirée en entier jusqu'à 525 €, de moitié au-delà, et le complément s'éteint à 1 575 €", () => {
  // Plancher de 1 050 €, pivot de 525 €.
  for (const [ressources, attendu] of [
    [0.0, 1050.0],
    [400.0, 650.0],                    // 1 050 − 400
    [525.0, 525.0],                    // au pivot
    [600.0, 487.5],                    // 525 − 0,5 × 75
    [1124.85, 225.075],                // 525 − 0,5 × 599,85 : le smicard seul
    [1575.0, 0.0],                     // la sortie, 525 + 525 / 0,5
    [1600.0, 0.0],
  ]) {
    proche(complement(SEUL, ressources), attendu, `seul, ${ressources} €`);
  }
});

test("en couple, la même forme sur 800 € : pivot à 400 €, sortie à 1 200 €", () => {
  for (const [ressources, attendu] of [
    [0.0, 800.0],
    [400.0, 400.0],
    [593.19, 303.405],                 // 400 − 0,5 × 193,19 : le mi-temps
    [1124.85, 37.575],                 // 400 − 0,5 × 724,85
    [1200.0, 0.0],
  ]) {
    proche(complement(COUPLE, ressources), attendu, `en couple, ${ressources} €`);
  }
});

test("le complément ne croît jamais avec les ressources, et le total ne décroît jamais", () => {
  for (const parametres of [SEUL, COUPLE]) {
    let avant = null;
    for (let ressources = 0.0; ressources <= 1700.0; ressources += 12.5) {
      const servi = complement(parametres, ressources);
      if (avant !== null) {
        assert.ok(servi <= avant.servi + 1e-9, `${ressources} € : le complément monte`);
        assert.ok(ressources + servi >= avant.ressources + avant.servi - 1e-9,
          `${ressources} € : le total baisse`);
      }
      avant = { ressources, servi };
    }
  }
});

test("à un et un, la règle redonne la garantie différentielle, au bit près", () => {
  for (const situation of [SEUL, COUPLE]) {
    const differentielle = {
      ...situation, part_retrait_entier_garantie: 1.0, taux_retrait_garantie: 1.0,
    };
    const plancher = situation === SEUL ? 1050.0 : 800.0;
    for (const ressources of [0.0, 0.1, 333.33, 400.0, 525.0, 600.0, 799.99, 800.0,
      1049.99, 1050.0, 1124.85, 1575.0, 3000.0]) {
      assert.equal(complement(differentielle, ressources) * 12.0,
        Math.max(0.0, plancher * 12.0 - ressources * 12.0), `${ressources} €`);
    }
  }
});

test("aujourd'hui, la garantie d'une retraitée partie avant 65 ans suit le même barème", () => {
  // Partie à 62 ans en 2022, elle a 66 ans en 2026 : sa garantie est ouverte,
  // et ses ressources d'aujourd'hui sont entre le pivot et la sortie.
  const simulateur = new Simulateur(paquet, SEUL);
  const aujourdhui = simulateur.simuler(
    simulateur.carriereSimple({ ...MODESTE, age_liquidation: 62 })).aujourd_hui;
  assert.ok(aujourdhui.garantie_ouverte && aujourdhui.garantie_residence);
  const plancher = aujourdhui.plancher_garantie;
  const ressources = aujourdhui.ressources_garantie;
  proche(plancher, 1050.0 * 12.0, "le plancher de 2026");
  assert.ok(ressources > 0.5 * plancher && ressources < 1.5 * plancher,
    `des ressources de ${ressources / 12} € par mois sortent de la pente`);
  proche(aujourdhui.garantie_vieillesse,
    0.5 * plancher - 0.5 * (ressources - 0.5 * plancher), "le complément d'aujourd'hui");
});

// -- le barème sur la distribution, que les pages appliquent ------------------
//
// Les mêmes tranches, posées à la main, que `tests/test_garantie_degressive.py`
// oppose au coût du modèle : le module du portage, que seules les pages lisent,
// doit rendre ce que le Python rend.

const FORME = [0.5, 0.5];

test("le manque moyen d'une tranche suit la pente, comme au modèle", () => {
  const manque = (inferieure, superieure, plancher = 1050.0) => manqueMoyen(
    inferieure, superieure, plancher, ...FORME);
  const egal = ([concernee, moyen], [attendue, attendu], quoi) => {
    proche(concernee, attendue, `${quoi}, part servie`);
    proche(moyen, attendu, `${quoi}, complément moyen`);
  };
  egal(manque(0.0, 100.0), [1.0, 1000.0], "sous le pivot");
  // (25 × 537,5 + 75 × 506,25) / 100.
  egal(manque(500.0, 600.0), [1.0, 514.0625], "à cheval sur le pivot");
  // 525 − 0,5 × 475 = 287,50 à 1 000 €, 237,50 à 1 100 €.
  egal(manque(1000.0, 1100.0), [1.0, 262.5], "dans la pente");
  // De 37,50 à zéro sur 75 € : 75 × 18,75 / 100, sur les trois quarts.
  egal(manque(1500.0, 1600.0), [0.75, 14.0625], "à cheval sur la sortie");
  assert.deepEqual(manque(1600.0, 1700.0), [0, 0]);
  egal(manque(1400.0, null), [1.0, 87.5], "la tranche ouverte");
  assert.deepEqual(manque(1600.0, null), [0, 0]);
  egal(manque(300.0, 500.0, 800.0), [1.0, 412.5], "en couple, sur le pivot");
  egal(manque(1100.0, 1200.0, 800.0), [1.0, 25.0], "en couple, avant la sortie");
});

test("sans forme, le barème d'une tranche reste différentiel, au bit près", () => {
  const differentielle = (inferieure, superieure, plancher) => {
    if (superieure === null) {
      const manque = Math.max(0, plancher - inferieure);
      return manque > 0 ? [1, manque] : [0, 0];
    }
    if (superieure <= plancher) return [1, plancher - (inferieure + superieure) / 2];
    if (inferieure >= plancher) return [0, 0];
    const concernee = (plancher - inferieure) / (superieure - inferieure);
    return [concernee, concernee * (plancher - inferieure) / 2];
  };
  for (const facteur of [1.0, 0.62, 0.805, 0.979, 0.7312345678]) {
    for (const plancher of [680.8, 893.55, 800.0, 1050.0, 0.0, 9000.0]) {
      for (let rang = 0; rang < 46; rang += 1) {
        const inferieure = 100.0 * rang * facteur;
        for (const superieure of [100.0 * (rang + 1) * facteur, null]) {
          const attendu = differentielle(inferieure, superieure, plancher);
          assert.deepEqual(manqueMoyen(inferieure, superieure, plancher, 1.0, 1.0), attendu);
          assert.deepEqual(manqueMoyen(inferieure, superieure, plancher), attendu);
        }
      }
    }
  }
});

test("le coût d'une distribution additionne ses tranches, sous la forme donnée", () => {
  // Quatre tranches, un quart de la population chacune ; un million de
  // personnes seules, plancher de 1 050 €.
  const distribution = { tranches: [
    { borneInferieure: 0.0, borneSuperieure: 100.0, part: 0.25 },
    { borneInferieure: 500.0, borneSuperieure: 600.0, part: 0.25 },
    { borneInferieure: 1000.0, borneSuperieure: 1100.0, part: 0.25 },
    { borneInferieure: 1500.0, borneSuperieure: 1600.0, part: 0.25 },
  ] };
  const chiffre = coutGarantie(distribution, 1e6, 1050.0, 1.0, ...FORME);
  proche(chiffre.partBeneficiaires, 0.9375, "la part servie");
  // 0,25 × (1 000 + 514,0625 + 262,5 + 14,0625) € par mois et par personne.
  proche(chiffre.coutAnnuelMeur, 5371.875, "le coût");
  const avant = coutGarantie(distribution, 1e6, 1050.0);
  proche(avant.partBeneficiaires, 0.625, "la part servie, différentielle");
  proche(avant.coutAnnuelMeur, 0.25 * 1512.5 * 12.0, "le coût, différentiel");
  // Les deux planchers, chacun sous sa forme (décision 102) : la moitié à
  // 800 €, la moitié à 1 050 €.
  const melange = coutGarantieParSexe(distribution, distribution, 1.0, 1e6, 800.0, 1.0, 1.0,
    1050.0, { F: 0.5, H: 0.5 }, ...FORME);
  const aDeux = coutGarantie(distribution, 5e5, 800.0, 1.0, ...FORME);
  const seules = coutGarantie(distribution, 5e5, 1050.0, 1.0, ...FORME);
  proche(melange.coutAnnuelMeur, aDeux.coutAnnuelMeur + seules.coutAnnuelMeur, "le mélange");
  proche(aDeux.coutAnnuelMeur, 0.25 * 1150.0 * 5e5 * 12.0 / 1e6, "à deux");
});
