/**
 * La carrière longue se lit dans les versions de sa fiche (note de décision
 * 0009, étape 3, troisième session).
 *
 * Le portage ne lit plus de table indexée par une année décimale
 * (`paquet.carriere_longue`, `2011.5`, `2012.833`) : il lit, dans le paquet
 * (`fiches_datees`), les versions de la fiche `carriere_longue`, et la date
 * d'effet de la pension choisit la version. Un droit contrefactuel ne coupe
 * plus la table (`CarriereLongue.avant`) : sa pile de couches remplace la
 * fiche (`remplacer_une_version`).
 *
 * Les âges attendus viennent du texte, D. 351-1-1 du code de la sécurité
 * sociale, lu dans l'index LEGI le 21 novembre 2026 :
 *
 * - rédaction du 1er septembre 2023 (LEGIARTI000047634571, décret n° 2023-436,
 *   article 9) : « 1° A cinquante-huit ans pour les assurés qui ont débuté
 *   leur activité avant l'âge de seize ans » ; « 3° A soixante-deux » avant
 *   vingt ans ; au II, « 1° Pour les assurés nés entre le 1er septembre 1961
 *   et 31 août 1963 inclus, le nombre : “ soixante-deux ” est remplacé par le
 *   nombre : “ soixante ” ; 2° Pour les assurés nés entre le 1er septembre
 *   1963 et le 31 décembre 1968 inclus, les mots : “ soixante-deux ans ” sont
 *   remplacés par les mots : “ l'âge prévu à l'article L. 161-17-2 minoré de
 *   deux ans et six mois ” ; 3° Pour les assurés nés en 1969 […] “ soixante-
 *   et-un ans et neuf mois ” » ;
 * - rédaction du 1er septembre 2026 (LEGIARTI000054059621, décret
 *   n° 2026-345, article 4) : le renvoi aux nés de septembre à décembre 1963
 *   et de 1966 à 1969 ; « soixante ans et six mois » en 1964 ; « soixante ans
 *   et neuf mois » de janvier à novembre 1965 et « soixante ans et huit mois »
 *   en décembre 1965 ; « soixante-et-un ans et neuf mois » en 1970 ;
 * - rédaction du 1er novembre 2012 (LEGIARTI000026139949) : « à soixante
 *   ans » avant vingt ans, pour toute génération.
 *
 * L'âge légal que le renvoi lit est celui de la génération, dans la version
 * de L. 161-17-2 qui vaut à la date d'effet : 62 ans et 9 mois au né en
 * octobre 1963, d'où 60 ans et 3 mois. Les âges écrits en clair au I ne sont
 * pas des renvois : 58 ans au né en mars 1963 parti avant seize ans, et non
 * son âge légal moins quatre ans (58 ans et 9 mois).
 *
 *     node --test tests/js/carriere-longue-versions.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { CarriereLongue, FichesDatees } from "../../moteur/js/regimes.js";
import { DateMois } from "../../moteur/js/calendrier.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const EFFET = "liquidation.date_effet";
const FICHE = "carriere_longue";

/** Ce que `portes` lit d'une carrière : sa génération et sa date d'effet. */
function carriere([annee, mois], [anneeEffet, moisEffet]) {
  return {
    generation: Math.round((annee + (mois - 1) / 12) * 1000) / 1000,
    dateLiquidation: new DateMois(anneeEffet, moisEffet),
  };
}

/** L'âge de la porte qui s'ouvre avant `ageMax` ans sans trimestre de plus. */
function porte(longue, naissance, effet, ageMax) {
  const portes = longue.portes(carriere(naissance, effet));
  const trouvees = (portes ?? []).filter(([max, , , supplement]) => max === ageMax
    && supplement === 0);
  assert.equal(trouvees.length, 1, `une porte avant ${ageMax} ans : ${JSON.stringify(portes)}`);
  return trouvees[0][2];
}

const AU_MOIS = (ans, mois = 0) => (ans * 12 + mois) / 12;

test("le paquet porte la fiche de la carrière longue, ses six versions choisies à la date d'effet", () => {
  const fiche = paquet.fiches_datees[FICHE];
  assert.ok(fiche, "la fiche manque à fiches_datees");
  assert.deepEqual(fiche.dates_qui_decident, [EFFET]);
  assert.deepEqual(fiche.versions.map((v) => [v.id, v.bornes[EFFET]]), [
    ["avant_la_loi_de_2003", [null, "2004-01-01"]],
    ["loi_de_2003", ["2004-01-01", "2011-07-01"]],
    ["loi_de_2010", ["2011-07-01", "2012-11-01"]],
    ["decret_de_2012", ["2012-11-01", "2023-09-01"]],
    ["decret_de_2023", ["2023-09-01", "2026-09-01"]],
    ["decret_de_2026", ["2026-09-01", null]],
  ]);
  assert.equal(paquet.carriere_longue, undefined,
    "la table indexée par année décimale a quitté le paquet");
});

test("le renvoi de 2023 et ceux de 2026 lisent l'âge légal de la génération, moins deux ans et six mois", () => {
  const versions = Object.fromEntries(paquet.fiches_datees[FICHE].versions.map((v) => [v.id, v]));
  const lus = (id) => (versions[id].renvois ?? []).map((r) => [r.fiche, r.valeur, r.de, r.date,
    r.mois, r.generations, r.ligne]);
  assert.deepEqual(lus("decret_de_2023"), [
    ["age_legal_par_generation", "age", "assure", EFFET, -30, [1963.667, 1969], { age_debut_maximum: 20 }]]);
  assert.deepEqual(lus("decret_de_2026"), [
    ["age_legal_par_generation", "age", "assure", EFFET, -30, [1963.667, 1964], { age_debut_maximum: 20 }],
    ["age_legal_par_generation", "age", "assure", EFFET, -30, [1966, 1970], { age_debut_maximum: 20 }]]);
  for (const id of ["avant_la_loi_de_2003", "loi_de_2003", "loi_de_2010", "decret_de_2012"]) {
    assert.deepEqual(lus(id), [], id);
  }
});

// Né le, date d'effet, borne de début, âge attendu, et pourquoi (le brief).
const CAS = [
  [[1963, 3], [2023, 10], 16, AU_MOIS(58), "I, 1° de 2023 : 58 ans, pas l'âge légal moins quatre"],
  [[1963, 3], [2023, 10], 20, AU_MOIS(60), "II, 1° de 2023 : nés de septembre 1961 à août 1963"],
  [[1963, 10], [2023, 10], 20, AU_MOIS(60, 3), "II, 2° de 2023 : 62 ans 9 mois moins 2 ans 6 mois"],
  [[1964, 6], [2024, 12], 20, AU_MOIS(60, 6), "II, 2° de 2023 : 63 ans moins 2 ans 6 mois"],
  [[1968, 6], [2026, 3], 20, AU_MOIS(61, 6), "II, 2° de 2023 : 64 ans moins 2 ans 6 mois"],
  [[1969, 6], [2026, 3], 20, AU_MOIS(61, 9), "II, 3° de 2023 : écrit en clair"],
  [[1970, 6], [2026, 3], 20, AU_MOIS(62), "I, 3° de 2023 : la règle générale reprend"],
  [[1965, 12], [2026, 9], 20, AU_MOIS(60, 8), "II, 4° de 2026 : décembre 1965"],
  [[1965, 12], [2026, 8], 20, AU_MOIS(60, 9), "II, 2° de 2023, la veille du décret de 2026"],
  [[1965, 6], [2026, 10], 20, AU_MOIS(60, 9), "II, 4° de 2026 : janvier à novembre 1965"],
  [[1964, 6], [2026, 10], 20, AU_MOIS(60, 6), "II, 3° de 2026 : écrit en clair"],
  [[1963, 10], [2026, 10], 20, AU_MOIS(60, 3), "II, 2° de 2026 : 62 ans 9 mois de la suspension"],
  [[1967, 6], [2028, 10], 20, AU_MOIS(61), "II, 2° de 2026 : 63 ans 6 mois de la suspension"],
  [[1969, 6], [2030, 10], 20, AU_MOIS(61, 6), "II, 2° de 2026 : 64 ans moins 2 ans 6 mois"],
  [[1970, 6], [2031, 10], 20, AU_MOIS(61, 9), "II, 5° de 2026 : écrit en clair"],
  [[1971, 6], [2032, 10], 20, AU_MOIS(62), "I, 3° de 2026"],
  [[1962, 3], [2023, 8], 20, AU_MOIS(60), "I de 2012 : soixante ans avant vingt ans"],
  [[1953, 6], [2012, 10], 18, AU_MOIS(60), "loi de 2010 : 60 ans avant dix-huit ans"],
  [[1950, 6], [2010, 6], 17, AU_MOIS(59), "loi de 2003 : 59 ans avant dix-sept ans"],
];

for (const [naissance, effet, ageMax, attendu, pourquoi] of CAS) {
  test(`né en ${naissance.join("-")}, effet ${effet.join("-")}, avant ${ageMax} ans : ${pourquoi}`, () => {
    const longue = new CarriereLongue(paquet);
    assert.equal(porte(longue, naissance, effet, ageMax), attendu);
  });
}

test("avant le 1er janvier 2004, la carrière longue n'existe pas", () => {
  assert.equal(new CarriereLongue(paquet).portes(carriere([1945, 6], [2003, 12])), null);
});

test("le droit contrefactuel ne coupe plus la table : sa pile remplace la fiche", () => {
  assert.equal(CarriereLongue.prototype.avant, undefined);
  const fiches = new FichesDatees(paquet);
  // Au droit du 31 août 2023 : la rédaction de 2012 vaut sans fin.
  const au2023 = new CarriereLongue(paquet, fiches.sousLeDroit("au_31_aout_2023"));
  assert.equal(porte(au2023, [1965, 6], [2027, 10], 20), AU_MOIS(60));
  // La loi de 2023 sans la suspension : la rédaction de 2023 vaut sans fin, et
  // son renvoi lit l'âge légal de 2023, que la couche garde aussi.
  const sans = new CarriereLongue(paquet, fiches.sousLeDroit("loi_2023_sans_suspension"));
  assert.equal(porte(sans, [1965, 12], [2027, 1], 20), AU_MOIS(60, 9));
  assert.equal(porte(sans, [1967, 6], [2028, 10], 20), AU_MOIS(61, 3));
  assert.equal(porte(sans, [1964, 6], [2026, 10], 20), AU_MOIS(60, 6));
});

test("la version d'une date se nomme", () => {
  const longue = new CarriereLongue(paquet);
  assert.equal(longue.version("2023-08-01").id, "decret_de_2012");
  assert.equal(longue.version("2023-09-01").id, "decret_de_2023");
  assert.equal(longue.version("2003-12-01").id, "avant_la_loi_de_2003");
});

test("la clause de sauvegarde de 2023 lit la rédaction qu'elle nomme", () => {
  const regle = new FichesDatees(paquet).regle("carriere_longue_sauvegarde_de_2023", "2023-10-01");
  assert.deepEqual(regle.redactions_anterieures, { carriere_longue: "decret_de_2012" });
  const [annee, mois] = regle.duree_acquise_avant;
  const avant = new DateMois(annee, mois).plusMois(-1);
  const longue = new CarriereLongue(paquet);
  assert.equal(longue.version(`${avant.annee}-${String(avant.mois).padStart(2, "0")}-01`).id,
    regle.redactions_anterieures.carriere_longue);
});
