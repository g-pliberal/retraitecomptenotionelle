/**
 * La caisse des membres du CESE liquide chaque annuité au pourcentage de son
 * mandat (article 17 de son règlement) : « 2,11 % pour les mandats jusqu'au
 * 31/8/2004 », puis « 2,02 % pour tout mandat effectué du 1/9/2004 au
 * 30/9/2010 ». Le moteur le traduit en pesant les trimestres de chaque année
 * par la durée requise de son mandat, 142 trimestres puis 149, sur la durée de
 * la liquidation. Ce poids tient à l'année où l'annuité s'acquiert : c'est un
 * champ de cotisation propre à la caisse (`duree_requise_des_annuites`, note
 * de décision 0009, amendement du 22 novembre 2026), et non la durée requise
 * de la liquidation lue à l'année.
 *
 *     node --test tests/js/annuites-au-taux-de-leur-annee.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { annuitesAuTauxDeLeurAnnee } from "../../moteur/js/droit/liquider.js";
import { CatalogueRegimes } from "../../moteur/js/regimes.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));

/** Un relevé de quatre trimestres par an, de `de` à `a` inclus. */
function relevé(de, a) {
  return {
    cumulPlafonne(_table, _membres, annees) {
      let total = 0;
      for (let annee = de; annee <= a; annee += 1) {
        if (annees(annee)) total += 4;
      }
      return total;
    },
  };
}

/** Le catalogue du paquet, chaque ligne du bloc `bloc` de la caisse retouchée. */
function catalogue(bloc = "cotisation", retouche = (l) => l) {
  const copie = structuredClone(paquet);
  const cese = copie.regimes.find((r) => r.code === "cese_membres");
  cese[bloc] = cese[bloc].map(retouche);
  return { catalogue: new CatalogueRegimes(copie) };
}

test("chaque ligne de cotisation de la caisse porte la durée de son mandat", () => {
  const regime = catalogue().catalogue.obtenir("cese_membres");
  const poids = (annee) => regime.deLAnnee(annee)[0].duree_requise_des_annuites;
  assert.equal(poids(1990), 142);
  assert.equal(poids(2004), 142);
  assert.equal(poids(2005), 149);
  assert.equal(poids(2010), 149);
  assert.equal(poids(2011), 154);
  assert.equal(poids(2012), 158);
  assert.equal(poids(2013), 162);
  assert.equal(poids(2014), 165);
  assert.equal(poids(2022), 165);
});

test("vingt ans de mandat pèsent 15 annuités sur 142 trimestres et 5 sur 149", () => {
  const moteur = catalogue();
  const trimestres = annuitesAuTauxDeLeurAnnee(
    moteur, "cese_membres", null, relevé(1990, 2009), ["cese_membres"], 165, 80);
  assert.equal(trimestres, Math.round((60 * 165 / 142 + 20 * 165 / 149) * 100) / 100);
});

test("le poids se lit sur la cotisation de l'année, non sur la liquidation", () => {
  // La durée requise de la liquidation retouchée ne change rien au poids des
  // annuités, qui tient à l'année du mandat.
  const moteur = catalogue("liquidation", (l) => ({ ...l, duree_requise_trimestres: 999 }));
  const trimestres = annuitesAuTauxDeLeurAnnee(
    moteur, "cese_membres", null, relevé(1990, 2009), ["cese_membres"], 165, 80);
  assert.equal(trimestres, Math.round((60 * 165 / 142 + 20 * 165 / 149) * 100) / 100);
});

test("une ligne de cotisation sans le poids de ses annuités est refusée", () => {
  const moteur = catalogue("cotisation", ({ duree_requise_des_annuites: _, ...l }) => l);
  assert.throws(() => annuitesAuTauxDeLeurAnnee(
    moteur, "cese_membres", null, relevé(1990, 2009), ["cese_membres"], 165, 80),
  /duree_requise_des_annuites/);
});
