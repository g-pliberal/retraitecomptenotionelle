/**
 * La pension étrangère de qui réside en France — le frontalier revenu, l'ancien
 * salarié de Suisse, du Luxembourg, d'Allemagne ou de Belgique : ce qu'elle
 * change à sa pension française.
 *
 * Les textes, lus le 21 novembre 2026 :
 *
 * - code général des impôts, article 1417, IV, 1°, c (index LEGI du dépôt,
 *   version du 1er janvier 2026) : le revenu fiscal de référence est majoré
 *   « de ceux [des revenus] exonérés par application d'une convention
 *   internationale relative aux doubles impositions ». Qu'elle soit imposable
 *   en France ou réservée à l'État qui la sert, la pension étrangère entre
 *   donc au revenu fiscal qui fixe la tranche de CSG de la pension française
 *   (L. 136-8, III du code de la sécurité sociale) ;
 * - notice 2041 GG (revenus 2025), « revenus d'activité et de remplacement
 *   de source étrangère » : la CSG déductible d'une pension prélevée au taux
 *   de 8,3 % est de 5,90 % de la pension, que le foyer déduit de la pension
 *   étrangère imposable (exemple 1 : 15 400 € perçus, 885 € déduits) ;
 * - méthode d'élimination des doubles impositions des conventions fiscales de
 *   la France : quand la convention réserve la pension à l'autre État, la
 *   France la compte pour calculer l'impôt et accorde un crédit égal à
 *   l'impôt français qui lui correspond (règle du taux effectif). Dans les
 *   deux cas, l'impôt qui frappe la pension française est celui du foyer qui
 *   déclare les deux pensions, au prorata de la pension française.
 *
 * Les valeurs attendues viennent de là : le foyer déclare la pension française
 * et la pension étrangère moins sa CSG déductible ; la pension française
 * supporte sa part de l'impôt du foyer ; le revenu fiscal présumé compte les
 * deux pensions, abattues de 10 %.
 *
 *     node --test tests/js/pension-etrangere-residente.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { Contexte, Montants } from "../../moteur/js/contexte.js";
import {
  fluxDesSystemes, partsImposablesParAnnee, remplacementApresImpot,
} from "../../moteur/js/cycle-de-vie.js";
import { Saisie } from "../../moteur/js/saisie.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const contexte = new Contexte(paquet);

const BASE = {
  age_reference: "fixe_apres_bascule", bascule: "2026", conversion_acquis: "reference",
  emploi: "cor_2026", enfants: "0", euros: "2026", indexation: "triple_lock_inverse",
  interruptions: "", primes: "0", profil: "ascendant", projection: "cor_reference",
  sexe: "H", stock: "prix", table: "unisexe", salaire: "1",
  statut: "salarie_prive_non_cadre", naissance: "1958-03-15", liquidation: "2022-04",
};

/** Une pension suisse de 1 500 € par mois, servie depuis le départ. */
const SUISSE = {
  pension_etrangere1_pays: "CH", pension_etrangere1: "1500",
  pension_etrangere1_debut: "2022-04",
};

/** La CSG déductible d'une pension au taux plein, depuis les revenus de 2018. */
const CSG_DEDUCTIBLE = 0.059;

function simuler(requete) {
  const saisie = Saisie.depuisRequete({ ...BASE, ...requete }, false, paquet.presomptions);
  const simulateur = contexte.simulateur(saisie.parametres(contexte.base));
  const comparaison = contexte.simuler(saisie);
  return { saisie, simulateur, comparaison };
}

const proche = (obtenu, attendu, quoi) => assert.ok(
  Math.abs(obtenu - attendu) <= 1e-6 * Math.max(1.0, Math.abs(attendu)),
  `${quoi} : ${obtenu}, attendu ${attendu}`);

test("le foyer déclare la pension étrangère, moins sa CSG déductible", () => {
  const { simulateur, comparaison } = simuler({ debut: "1980-01", ...SUISSE });
  const flux = fluxDesSystemes(simulateur, comparaison, { impot: "prix" }).actuel;
  const parts = partsImposablesParAnnee(simulateur, comparaison);
  for (const annee of [2023, 2026, 2035]) {
    const impot = flux.impots.get(annee);
    const francaise = flux.niveaux.get(annee) * flux.servi(annee) * parts.get(annee);
    // 1 500 € par mois en euros de l'année courante du modèle, 2026, que la
    // saisie ramène à son premier mois et que les prix mènent ensuite.
    const etrangere = 1500 * 12 * simulateur.macro.coefficientPrix(2026, annee)
      * (1 - CSG_DEDUCTIBLE);
    proche(impot.pension, francaise, `pension française déclarée en ${annee}`);
    proche(impot.pension_etrangere, etrangere, `pension étrangère déclarée en ${annee}`);
    proche(impot.sur_la_pension, impot.foyer.impot * francaise / (francaise + etrangere),
      `impôt de la pension française en ${annee}`);
    proche(impot.sur_le_salaire, 0.0, `impôt du salaire en ${annee}`);
  }
});

test("la pension étrangère alourdit l'impôt de la pension française", () => {
  const seule = simuler({ debut: "1980-01" });
  const avec = simuler({ debut: "1980-01", ...SUISSE });
  const sans = fluxDesSystemes(seule.simulateur, seule.comparaison, { impot: "prix" }).actuel;
  const plus = fluxDesSystemes(avec.simulateur, avec.comparaison, { impot: "prix" }).actuel;
  const annee = 2026;
  assert.ok(plus.impots.get(annee).sur_la_pension > sans.impots.get(annee).sur_la_pension,
    `${plus.impots.get(annee).sur_la_pension} contre ${sans.impots.get(annee).sur_la_pension}`);
});

test("la pension du départ après impôt perd sa part de l'impôt des deux pensions", () => {
  // Le taux de remplacement après impôt de l'OCDE déclare la pension du
  // départ seule ; la pension étrangère servie au même mois s'y ajoute, et la
  // pension française n'en supporte que sa part.
  const seule = simuler({ debut: "1980-01" });
  const avec = simuler({ debut: "1980-01", ...SUISSE });
  const sans = remplacementApresImpot(seule.simulateur, seule.comparaison);
  const plus = remplacementApresImpot(avec.simulateur, avec.comparaison);
  assert.ok(plus < sans, `${plus} contre ${sans}`);
});

test("qui réside hors de France ne déclare pas sa pension étrangère en France", () => {
  const { simulateur, comparaison } = simuler({ debut: "1980-01", ...SUISSE, residence: "CH" });
  const flux = fluxDesSystemes(simulateur, comparaison, { impot: "prix" }).actuel;
  assert.equal(flux.impots.get(2026).pension_etrangere, 0.0);
});

test("la pension étrangère entre au revenu fiscal qui fixe la tranche de CSG", () => {
  // Une courte carrière française : sa pension seule, abattue de 10 %, reste
  // sous le seuil d'exonération ; avec 2 500 € par mois de pension suisse,
  // le revenu fiscal passe le seuil du taux médian (26 004 € pour une part
  // en 2025, notice 2041 GG, tableau 3).
  const courte = { debut: "1998-01", salaire: "0.4" };
  const seule = simuler(courte);
  const avec = simuler({ ...courte, ...SUISSE, pension_etrangere1: "2500" });
  const sans = Montants.depuis(seule.saisie, seule.simulateur, seule.comparaison);
  const plus = Montants.depuis(avec.saisie, avec.simulateur, avec.comparaison);
  assert.equal(sans.tauxCsg, 0, `sans pension étrangère : ${sans.tranche}, ${sans.revenuFiscal}`);
  // La pension française du second cas, seule : l'écrêtement du minimum
  // contributif, qui compte la pension étrangère, a pu la baisser.
  const francaise = Montants.duFoyer(avec.saisie, avec.simulateur.baremePrelevements.pensions,
    avec.comparaison.actuel, avec.comparaison.aujourd_hui.actuel,
    avec.comparaison.coefficient_euros_aujourd_hui);
  const etrangere = 2500 * 12;
  proche(plus.revenuFiscal, francaise.revenuFiscal + 0.9 * etrangere, "revenu fiscal présumé");
  assert.equal(plus.tauxCsg, 0.083, `avec : ${plus.tranche}, ${plus.revenuFiscal}`);
});

test("la pension étrangère paie la CSG, la CRDS et la CASA de la tranche du foyer", () => {
  // CSS, art. L. 136-1 et L. 137-41 ; ordonnance n° 96-50, art. 14 : toute
  // pension de qui est domicilié en France et à la charge d'un régime
  // français d'assurance maladie, quelle que soit sa source (BOI-RES-RSA-000219,
  // 11 août 2025). Au taux plein : 8,3 % de CSG, 0,5 % de CRDS, 0,3 % de
  // CASA (notice 2041 GG, tableau 4) ; aucune cotisation maladie.
  const avec = simuler({ debut: "1980-01", ...SUISSE });
  const montants = Montants.depuis(avec.saisie, avec.simulateur, avec.comparaison);
  assert.equal(montants.tranche, "taux plein");
  proche(montants.tauxPensionEtrangere, 0.083 + 0.005 + 0.003, "prélèvements");
  proche(montants.etrangeres, 1500 * 12, "pension étrangère annuelle");
  // Qui réside hors de France n'est pas domicilié en France : rien.
  const dehors = simuler({ debut: "1980-01", ...SUISSE, residence: "CH" });
  assert.equal(Montants.depuis(dehors.saisie, dehors.simulateur, dehors.comparaison)
    .tauxPensionEtrangere, 0);
});
