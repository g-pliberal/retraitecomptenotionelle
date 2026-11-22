/**
 * Les axes du régime et la vue des périodes pendant le gel (note de décision
 * 0009, amendement du 22 novembre 2026, étapes 3 et 4) : le paquet porte les
 * quatre blocs, le moteur en refait la vue des périodes que lisent encore le
 * pont et les tests, et ce qu'il lit par axe est ce que ces périodes donnent.
 *
 * À toute date d'effet, `aLaDate` rend la liquidation, la structure et le
 * servi de la première période qui liquide ce jour-là, et ce que la
 * liquidation lit de la cotisation ; à toute année, `deLAnnee` rend, tranche
 * par tranche et dans leur ordre, les périodes qui la couvrent, sauf la
 * liquidation des treize années où son 1er janvier n'est pas celui de la
 * période. Ce test part avec la vue des périodes, à l'étape 5.
 *
 *     node --test tests/js/axes.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { axesDesPeriodes, famille } from "../../moteur/js/axes.js";
import { CatalogueRegimes } from "../../moteur/js/regimes.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const BORNES = new Set(["debut", "fin", "date_effet", "notes", "regime"]);
const jan = (annee) => `${String(annee).padStart(4, "0")}-01-01`;

function effet(periode) {
  return periode.date_effet ?? [jan(periode.debut), periode.fin === null ? null : jan(periode.fin + 1)];
}

/** Les champs d'une famille, et ceux de la cotisation que la liquidation lit, nuls compris. */
function champs(objet, familles, aussi = new Set()) {
  if (objet === null || objet === undefined) return null;
  return Object.fromEntries(Object.keys(objet)
    .filter((c) => !BORNES.has(c) && (familles.has(famille(c)) || aussi.has(c)))
    .sort().map((c) => [c, objet[c]]));
}

const AU_JOUR = new Set(["liquidation", "structure", "servi"]);
const TOUTES = new Set(["liquidation", "structure", "servi", "cotisation"]);
const HORS_LIQUIDATION = new Set(["structure", "servi", "cotisation"]);

/**
 * Ce que la liquidation lit de la cotisation, à la date d'effet (liquider.js) :
 * l'assiette du salaire de référence, ses bornes, et le barème des points.
 */
const COTISATION_LUE_A_LA_LIQUIDATION = new Set([
  "assiette", "assiette_grille", "assiette_forfaitaire", "assiette_repere_smic",
  "bareme_points", "borne_basse_euros", "borne_haute_euros",
  "borne_basse_par_annee", "borne_haute_par_annee",
]);

/**
 * Les années où la liquidation du 1er janvier n'est pas celle de la période
 * de l'année, que la vue datait d'un autre jour (amendement du 22 novembre
 * 2026 : « le 1er janvier diffère d'elle sur 13 couples »).
 */
const PREMIER_JANVIER_AUTRE = new Set([
  "regime_general@1983", "msa_salaries@1983", "banque_de_france@2007",
  "carcdsf_complementaire@2011", "carcdsf_complementaire@2024",
  "carpimko_complementaire@1987", "cavamac_complementaire@2023",
  "cavp_complementaire@2024", "cps_saint_pierre_et_miquelon@2016",
  "cps_saint_pierre_et_miquelon@2023", "cps_saint_pierre_et_miquelon@2026",
  "cssm_mayotte@2023", "ircec_racl@2025",
]);

for (const tauxMoyens of [false, true]) {
  test(`les axes rendent ce que rendaient les périodes${tauxMoyens ? ", au taux moyen" : ""}`, () => {
    const catalogue = new CatalogueRegimes(paquet, { tauxMoyens });
    const autres = new Set();
    for (const regime of catalogue) {
      const periodes = regime.periodes;
      for (let annee = 1900; annee <= 2070; annee += 1) {
        for (let mois = 1; mois <= 12; mois += 1) {
          const jour = `${annee}-${String(mois).padStart(2, "0")}-01`;
          const vue = periodes.find((p) => {
            const [debut, fin] = effet(p);
            return debut <= jour && (fin === null || jour < fin);
          }) ?? null;
          assert.deepEqual(champs(regime.aLaDate(jour), AU_JOUR, COTISATION_LUE_A_LA_LIQUIDATION),
            champs(vue, AU_JOUR, COTISATION_LUE_A_LA_LIQUIDATION), `${regime.code} au ${jour}`);
        }
        const actives = periodes.filter((p) => p.debut <= annee && (p.fin === null || annee <= p.fin));
        const couple = `${regime.code}@${annee}`;
        const familles = PREMIER_JANVIER_AUTRE.has(couple) ? HORS_LIQUIDATION : TOUTES;
        const lues = regime.deLAnnee(annee).map((p) => champs(p, familles));
        assert.deepEqual(lues, actives.map((p) => champs(p, familles)), `${regime.code} en ${annee}`);
        if (familles === HORS_LIQUIDATION
            && JSON.stringify(regime.deLAnnee(annee).map((p) => champs(p, TOUTES)))
              !== JSON.stringify(actives.map((p) => champs(p, TOUTES)))) {
          autres.add(couple);
        }
      }
    }
    assert.deepEqual([...autres].sort(), [...PREMIER_JANVIER_AUTRE].sort());
  });
}

/**
 * Le paquet porte les quatre blocs, et non plus les périodes (étape 4) ; la vue
 * des périodes que le moteur en refait pour le pont et les tests, jusqu'à son
 * retrait (étape 5), redonne les mêmes blocs.
 */
test("le paquet porte les quatre blocs, et la vue des périodes les redonne", () => {
  const catalogue = new CatalogueRegimes(paquet);
  for (const fiche of paquet.regimes) {
    assert.equal(fiche.periodes, undefined, `${fiche.code} porte encore des périodes`);
    for (const bloc of ["structure", "liquidation", "cotisation", "servi"]) {
      assert.ok(Array.isArray(fiche[bloc]), `${fiche.code} sans bloc ${bloc}`);
    }
    const regime = catalogue.obtenir(fiche.code);
    const refaits = axesDesPeriodes(regime.periodes);
    for (const bloc of ["structure", "liquidation", "cotisation", "servi"]) {
      assert.deepEqual(refaits[bloc], regime[bloc], `${fiche.code}, ${bloc}`);
      assert.deepEqual(regime[bloc], fiche[bloc], `${fiche.code}, ${bloc} lu tel quel`);
    }
  }
});
