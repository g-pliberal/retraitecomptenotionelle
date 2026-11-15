/**
 * Le pilier capitalisé, sur une courbe plate et sous d'autres allocations
 * (action 161, quatrième vague) : ce que `tests/test_capitalisation.py`
 * éprouvait sur le constructeur du moteur Python, éprouvé sur celui du site.
 *
 * Aucune valeur attendue ne vient du moteur. Sur une courbe à taux unique,
 * le capital a une forme close — chaque versement net, crédité en fin
 * d'année, capitalisé à `(1 + taux)(1 − frais)` par année restante —, que
 * chaque test écrit à côté de son assertion ; sous les anticipations pures,
 * toute allocation qui pave l'horizon sans le dépasser rend le même capital,
 * parce que c'est ce que l'arbitrage impose au forward.
 *
 *     node --test tests/js/capitalisation.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import {
  ConstructeurCapitalisation, MATURITE_MAXIMALE, repartition,
} from "../../moteur/js/capitalisation.js";
import {
  PARAMETRES_DEFAUT, avec, sousRegimeTaux, tauxCapitalisationApplique,
} from "../../moteur/js/config.js";
import { Convertisseur } from "../../moteur/js/conversion.js";
import { DonneesMortalite } from "../../moteur/js/mortalite.js";
import { Fiabilite } from "../../moteur/js/serie.js";
import { Simulateur } from "../../moteur/js/simulateur.js";
import { CourbeTauxSansRisque } from "../../moteur/js/taux.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur", "donnees.json"), "utf8"));
const mortalite = new DonneesMortalite(paquet);

/** Les frais figés à leur niveau de départ : ces tests vérifient la
 * convention de date et l'ordre des prélèvements, pas la trajectoire. */
const FRAIS_FIGES = {
  frais_versement_paliers: [], frais_gestion_paliers: [],
  frais_arrerages_paliers: [], frais_encours_rente_paliers: [],
};

/** Une courbe fictive à taux unique : toutes les maturités rendent le même
 * taux, et le capital admet une forme close. */
class CourbePlate {
  constructor(taux) {
    this.taux = taux;
    this.annee = 2026;
    this.date = "2026-01-01";
  }

  placement(annee, duree) {
    return { taux: this.taux, differe: Math.max(0, annee - this.annee), duree,
      fiabilite: Fiabilite.CERTIFIEE };
  }
}

const constructeur = (courbe, parametres, repartir = null) => new ConstructeurCapitalisation(
  courbe, mortalite, new Convertisseur(mortalite, parametres), parametres, repartir);

const plate = (taux, parametres) => constructeur(new CourbePlate(taux), parametres);

const assiettesDe = (debut, fin, montant) => new Map(
  Array.from({ length: fin - debut + 1 }, (_, i) => [debut + i, montant]));

const proche = (lu, attendu, relatif = 1e-9, absolu = 1e-9) => assert.ok(
  Math.abs(lu - attendu) <= Math.max(absolu, relatif * Math.abs(attendu)),
  `${lu} au lieu de ${attendu}`);

// -- l'allocation des maturités ------------------------------------------------

test("le versement est adossé à son horizon, plafonné au bout de la courbe", () => {
  for (let horizon = 1; horizon <= MATURITE_MAXIMALE; horizon += 1) {
    assert.deepEqual(repartition(horizon), [[horizon, 1.0]]);
  }
  for (let horizon = MATURITE_MAXIMALE + 1; horizon < 60; horizon += 1) {
    assert.deepEqual(repartition(horizon), [[MATURITE_MAXIMALE, 1.0]]);
  }
  assert.deepEqual(repartition(0), []);
});

test("les maturités achetées sont des points cotés, de poids un", () => {
  const cotees = new Set(new CourbeTauxSansRisque(paquet).maturites);
  for (let horizon = 1; horizon < 60; horizon += 1) {
    const parts = repartition(horizon);
    proche(parts.reduce((somme, [, poids]) => somme + poids, 0), 1.0);
    for (const [maturite] of parts) {
      assert.ok(cotees.has(maturite) && maturite <= horizon, `${horizon} : ${maturite}`);
    }
  }
});

/** L'échelle glissante 2/10/30, telle qu'elle servait jusqu'en 2026. */
function echelleGlissante(horizon) {
  if (horizon <= 0) return [];
  const borner = (v) => Math.min(1.0, Math.max(0.0, v));
  const longue = 0.75 * borner((horizon - 10) / 20);
  const courte = 0.75 * borner((10 - horizon) / 8);
  const cumul = new Map();
  [[2, courte], [10, 1.0 - courte - longue], [30, longue]].forEach(([maturite, part]) => {
    if (part > 0) {
      const effective = Math.min(maturite, horizon);
      cumul.set(effective, (cumul.get(effective) ?? 0.0) + part);
    }
  });
  return [...cumul].sort((a, b) => a[0] - b[0]);
}

const toutCourt = (horizon) => (horizon > 0 ? [[1, 1.0]] : []);

const moitieMoitie = (horizon) => {
  if (horizon <= 0) return [];
  if (horizon === 1) return [[1, 1.0]];
  return [[1, 0.5], [Math.min(horizon, MATURITE_MAXIMALE), 0.5]];
};

const pilierSous = (courbe, parametres, repartir) => constructeur(courbe, parametres, repartir)
  .construire({ assiettes: assiettesDe(2030, 2065, 30_000.0), anneeNaissance: 1996,
    ageLiquidation: 64.0, anneeLiquidation: 2060 }).capital;

test("sous les anticipations pures, l'allocation est sans effet sur le capital", () => {
  const courbe = new CourbeTauxSansRisque(paquet);
  const capitaux = [repartition, echelleGlissante, toutCourt, moitieMoitie]
    .map((regle) => pilierSous(courbe, PARAMETRES_DEFAUT, regle));
  assert.ok(capitaux[0] > 0);
  for (const capital of capitaux.slice(1)) proche(capital, capitaux[0], 0, 0.01);
});

test("avec une prime de terme, l'adossement domine l'échelle, qui domine le roulement", () => {
  const parametres = avec(PARAMETRES_DEFAUT, { prime_terme_trente_ans: 0.005 });
  const courbe = new CourbeTauxSansRisque(paquet, parametres.prime_terme_trente_ans);
  const [adosse, echelle, roule] = [repartition, echelleGlissante, toutCourt]
    .map((regle) => pilierSous(courbe, parametres, regle));
  assert.ok(adosse > echelle && echelle > roule, `${adosse}, ${echelle}, ${roule}`);
});

test("le réglage des taux ne traverse que la courbe du pilier", () => {
  // « Système 4 seulement » : la courbe du taux d'emprunt de la dette ne
  // porte jamais de prime ; celle du pilier, que le constructeur lit, la porte.
  for (const regime of ["forwards", "prime", "prime_haute"]) {
    const parametres = sousRegimeTaux(PARAMETRES_DEFAUT, regime);
    const simulateur = new Simulateur(paquet, parametres);
    assert.equal(simulateur.courbeTaux.primeTerme, 0.0);
    assert.equal(simulateur.courbeTauxPilier.primeTerme, parametres.prime_terme_trente_ans);
    assert.equal(simulateur.constructeurCapitalisation.courbe, simulateur.courbeTauxPilier);
  }
  assert.ok(sousRegimeTaux(PARAMETRES_DEFAUT, "prime").prime_terme_trente_ans > 0);
});

// -- l'accumulation, sur une courbe plate ----------------------------------------

test("le capital a la forme close quand la courbe est plate", () => {
  const parametres = avec(PARAMETRES_DEFAUT, FRAIS_FIGES);
  const pilier = plate(0.03, parametres).construire({
    assiettes: assiettesDe(2026, 2040, 30_000.0), anneeNaissance: 1990,
    ageLiquidation: 50.0, anneeLiquidation: 2040 });
  const net = 30_000.0 * tauxCapitalisationApplique(parametres)
    * (1 - parametres.frais_versement_capitalisation);
  const facteur = 1.03 * (1 - parametres.frais_gestion_capitalisation);
  let attendu = 0;
  for (let annee = 2026; annee <= 2040; annee += 1) attendu += net * facteur ** (2040 - annee);
  proche(pilier.capital, attendu);
  // Le versement de l'année de la liquidation est porté, sans intérêt.
  const [avant, derniere] = pilier.annees.slice(-2);
  proche(derniere.versement_net, net);
  proche(derniere.encours - avant.encours * facteur, net);
});

test("sans frais, le capital est celui de la courbe seule", () => {
  const parametres = avec(PARAMETRES_DEFAUT, {
    frais_versement_capitalisation: 0.0, frais_gestion_capitalisation: 0.0, ...FRAIS_FIGES });
  const pilier = plate(0.04, parametres).construire({
    assiettes: assiettesDe(2026, 2035, 40_000.0), anneeNaissance: 1990,
    ageLiquidation: 45.0, anneeLiquidation: 2035 });
  const brut = 40_000.0 * tauxCapitalisationApplique(parametres);
  let attendu = 0;
  for (let annee = 2026; annee <= 2035; annee += 1) attendu += brut * 1.04 ** (2035 - annee);
  proche(pilier.capital, attendu);
  proche(pilier.capital_hors_frais, pilier.capital);
  assert.equal(pilier.frais_preleves, 0.0);
  proche(pilier.taux_rendement_annuel, 0.04, 1e-6);
});

test("le frais sur la réserve de rente vaut une actualisation négative", () => {
  // 0,52 % par an sur la réserve d'une rente nivelée : diviser le capital par
  // Σ p_t (1 − f)^(−t), sur la courbe de survie à la liquidation.
  const avecFrais = avec(PARAMETRES_DEFAUT, FRAIS_FIGES);
  const sansFrais = avec(PARAMETRES_DEFAUT, {
    frais_encours_rente_capitalisation: 0.0, ...FRAIS_FIGES });
  const demande = { assiettes: assiettesDe(2026, 2065, 30_000.0), anneeNaissance: 2001,
    ageLiquidation: 64.0, anneeLiquidation: 2065 };
  const pilierAvec = plate(0.03, avecFrais).construire(demande);
  const pilierSans = plate(0.03, sansFrais).construire(demande);
  assert.equal(pilierSans.facteur_encours_rente, 1.0);
  proche(pilierAvec.capital, pilierSans.capital);
  const courbe = mortalite.courbe(64.0, 2065.0, null, avecFrais.table_generation, null);
  const attendu = courbe.reduce((s, p) => s + p, 0)
    / courbe.reduce((s, p, t) => s + p / (1 - 0.0052) ** t, 0);
  proche(pilierAvec.facteur_encours_rente, attendu);
  assert.ok(attendu > 0.90 && attendu < 0.94);
  proche(pilierAvec.rente_annuelle, pilierSans.rente_annuelle * attendu);
});

/** Un tarif de gestion de 1 %, qui tombe à zéro en 2030. */
const sousConvergence = (convergence) => avec(PARAMETRES_DEFAUT, {
  frais_versement_capitalisation: 0.0, frais_versement_paliers: [],
  frais_gestion_capitalisation: 0.01, frais_gestion_paliers: [[2030, 0.0]],
  frais_arrerages_paliers: [], frais_encours_rente_paliers: [],
  convergence_frais_stock: convergence });

const versementUnique = (parametres, annee) => plate(0.0, parametres).construire({
  assiettes: new Map([[annee, 20_000.0]]), anneeNaissance: 1990,
  ageLiquidation: 50.0, anneeLiquidation: 2040 });

test("la baisse porte sur les nouveaux dépôts, et le stock garde son tarif", () => {
  const parametres = sousConvergence(0.0);
  const brut = 20_000.0 * tauxCapitalisationApplique(parametres);
  // Versé en 2027 : 1 % par an, de 2028 à 2040, malgré le palier de 2030.
  const ancien = versementUnique(parametres, 2027);
  proche(ancien.capital, brut * 0.99 ** 13);
  proche(ancien.annees.at(-1).taux_frais_gestion, 0.01);
  // Versé en 2031 : il entre à zéro et n'est jamais prélevé.
  const nouveau = versementUnique(parametres, 2031);
  proche(nouveau.capital, brut);
  assert.equal(nouveau.frais_gestion, 0.0);
});

test("la convergence rapproche le stock du tarif des nouveaux dépôts", () => {
  const brut = 20_000.0 * tauxCapitalisationApplique(PARAMETRES_DEFAUT);
  const total = versementUnique(sousConvergence(1.0), 2027);
  // 1 % en 2028 et 2029, puis zéro dès 2030.
  proche(total.capital, brut * 0.99 ** 2);
  const partiel = versementUnique(sousConvergence(0.5), 2027);
  const taux = partiel.annees.filter((a) => a.annee >= 2030).map((a) => a.taux_frais_gestion);
  proche(taux[0], 0.005);
  proche(taux[1], 0.0025);
  assert.ok(total.capital > partiel.capital
    && partiel.capital > versementUnique(sousConvergence(0.0), 2027).capital);
});

test("l'espérance transmise se recalcule à la main, sur la même table", () => {
  // La somme, année par année, de la probabilité de mourir cette année-là
  // par l'encours moyen de l'année.
  const parametres = avec(PARAMETRES_DEFAUT, FRAIS_FIGES);
  const pilier = plate(0.03, parametres).construire({
    assiettes: assiettesDe(2026, 2040, 30_000.0), anneeNaissance: 1990,
    ageLiquidation: 50.0, anneeLiquidation: 2040, sexe: "H" });
  const survie = mortalite.courbe(36.0, 2026.0, null, parametres.table_generation);
  const attendu = pilier.annees.slice(0, -1).reduce((somme, a, i) => somme
    + (survie[i] - survie[i + 1]) * 0.5 * (a.encours_ouverture + a.encours), 0);
  proche(pilier.esperance_capital_transmis, attendu);
  proche(pilier.probabilite_deces_avant_liquidation,
    survie[0] - survie[pilier.annees.length - 1]);
});
