/**
 * La CSG et la CRDS sur la part patronale de la complémentaire santé et de la
 * prévoyance (L. 136-1-1 du code de la sécurité sociale) : au taux de chaque
 * année, et rien avant la CSG. La fiche de paie les prend au taux de l'année
 * courante, 9,2 + 0,5 = 9,7 % ; l'histoire des prélèvements
 * (`legislation/prelevements_historiques.yaml`) dit le taux de chaque date :
 * rien avant février 1991 ; 2,4 % en 1995, sans CRDS (février 1996) ; 7,5 + 0,5
 * = 8,0 % de 2012 à 2017, dont 5,1 points déductibles ; 9,2 + 0,5 depuis 2018,
 * dont 6,8 déductibles.
 *
 *     node --test tests/js/csg-part-patronale.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { Contexte } from "../../moteur/js/contexte.js";
import { revenusImposables, revenusNets } from "../../moteur/js/cycle-de-vie.js";
import { chargerPrelevementsHistoriques } from "../../moteur/js/prelevements-historiques.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const contexte = new Contexte(paquet);
const historique = chargerPrelevementsHistoriques(paquet);

const proche = (obtenu, attendu, ecart = 1e-9) =>
  assert.ok(Math.abs(obtenu - attendu) <= ecart, `${obtenu} au lieu de ${attendu}`);

test("le taux de la part patronale est celui de son année, et nul avant la CSG", () => {
  proche(historique.tauxPartPatronaleAnnuel(1985), 0.0);
  proche(historique.tauxPartPatronaleAnnuel(1995), 0.024);
  proche(historique.tauxPartPatronaleAnnuel(2016), 0.080);
  proche(historique.tauxPartPatronaleAnnuel(2017), 0.080);
  proche(historique.tauxPartPatronaleAnnuel(2026), 0.097);
});

test("la part non déductible est celle de son année", () => {
  proche(historique.nonDeductiblePartPatronaleAnnuel(1985), 0.0);
  proche(historique.nonDeductiblePartPatronaleAnnuel(2016), 0.075 - 0.051 + 0.005);
  proche(historique.nonDeductiblePartPatronaleAnnuel(2026), 0.092 - 0.068 + 0.005);
});

// Cent euros de mutuelle par mois de plus de chaque côté : le net d'une année
// perd la part salariale et la CSG-CRDS de l'année sur la part patronale ; le
// revenu imposable ne perd que la CSG déductible sur la part patronale, qui y
// entre (CGI, art. 83, 1° quater). Avant 2016, pas de complémentaire santé.
test("une mutuelle plus chère retire du net la CSG de son année", () => {
  const options = {
    annee_naissance: 1975, sexe: "H", affiliation: "salarie_prive_non_cadre",
    age_debut: 22, age_liquidation: 64, niveau_salaire: 1.0,
  };
  const sans = contexte.simulateur({ ...PARAMETRES_DEFAUT, mutuelle_mensuelle: 20 });
  const avec = contexte.simulateur({ ...PARAMETRES_DEFAUT, mutuelle_mensuelle: 120 });
  const carriere = sans.carriereSimple(options);
  const [netsSans, netsAvec] = [revenusNets(sans, carriere), revenusNets(avec, carriere)];
  const [impSans, impAvec] = [revenusImposables(sans, carriere),
    revenusImposables(avec, carriere)];
  const courante = PARAMETRES_DEFAUT.annee_courante;
  const plafond = (annee) => sans.macro.plafond_securite_sociale.valeur(annee);
  const ecart = (annee) => 1200 * plafond(annee) / plafond(courante);
  proche(netsAvec.get(2010) - netsSans.get(2010), 0.0);
  for (const [annee, csg, deductible] of [[2016, 0.080, 0.051], [2017, 0.080, 0.051],
    [2020, 0.097, 0.068], [courante, 0.097, 0.068]]) {
    proche(netsAvec.get(annee) - netsSans.get(annee), -ecart(annee) * (1 + csg), 1e-6);
    proche(impAvec.get(annee) - impSans.get(annee), -ecart(annee) * deductible, 1e-6);
  }
});
