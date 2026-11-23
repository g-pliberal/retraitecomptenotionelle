/**
 * L'âge du taux plein se lit dans les versions de sa fiche (note de décision
 * 0009, étape 3, première session).
 *
 * Le portage ne lit plus la table par génération (`age_annulation_decote.csv`) :
 * il lit, dans le paquet (`fiches_datees`), les versions de la fiche
 * `age_annulation_decote`. La date d'effet de la pension choisit la version ;
 * les deux dernières renvoient à l'âge légal, lu dans SA version à la même date
 * d'effet.
 *
 * Les âges attendus viennent des textes : soixante-cinq ans fixés par R. 351-27
 * (« l'âge prévu au 1° de l'article L. 351-8 est fixé à soixante-cinq ans ») ;
 * de 2011 à 2023, « l'âge prévu à l'article L. 161-17-2 augmenté de cinq
 * années » (L. 351-8, 1°, loi n° 2010-1330), soit 60 ans et 4 mois, 60 ans et
 * 9 mois, 61 ans et 2 mois, 61 ans et 7 mois (D. 161-2-1-9) plus cinq ;
 * depuis le 1er septembre 2023, « l'âge prévu au premier alinéa de l'article
 * L. 161-17-2 augmenté de trois années » : soixante-quatre ans plus trois,
 * pour tout assuré, et non l'âge légal de sa génération plus trois.
 *
 *     node --test tests/js/age-du-taux-plein.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { DateMois } from "../../moteur/js/calendrier.js";
import {
  AgesAnnulationDecote, FICHE_DE_L_AGE_DU_TAUX_PLEIN, FICHE_DE_L_AGE_LEGAL, FichesDatees,
} from "../../moteur/js/regimes.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const EFFET = "liquidation.date_effet";

/** La génération d'un mois de naissance, comme la carrière l'écrit. */
function generationDe(annee, mois) {
  return Math.round((annee + (mois - 1) / 12) * 1000) / 1000;
}

/** Un âge en ans et en mois, en mois. */
function mois(ans, m = 0) {
  return 12 * ans + m;
}

/** L'âge lu, en mois entiers : le texte les écrit en ans et en mois. */
function enMoisLu(lu) {
  assert.notEqual(lu, null);
  return Math.round(lu[0] * 12);
}

const ages = new AgesAnnulationDecote(paquet);

test("le paquet porte la fiche de l'âge du taux plein, ses cinq versions choisies à la date d'effet", () => {
  const fiche = paquet.fiches_datees[FICHE_DE_L_AGE_DU_TAUX_PLEIN];
  assert.ok(fiche, "la fiche manque à fiches_datees");
  assert.deepEqual(fiche.dates_qui_decident, [EFFET]);
  assert.deepEqual(fiche.versions.map((v) => v.id), [
    "avant_l_ordonnance_de_1982", "ordonnance_de_1982", "soixante_cinq_ans", "age_legal_plus_cinq",
    "premier_alinea_plus_trois"]);
});

// Né le, date d'effet, âge attendu en mois, et pourquoi (le brief de l'étape).
const CAS = [
  [[1940, 3], "2003-01-01", mois(65), "R. 351-27 : soixante-cinq ans"],
  [[1950, 3], "2015-04-01", mois(65), "âge légal de 60 ans (né avant le 1er juillet 1951) + 5"],
  [[1951, 8], "2017-01-01", mois(65, 4), "60 ans et 4 mois (D. 161-2-1-9, 2°) + 5"],
  [[1952, 3], "2018-01-01", mois(65, 9), "60 ans et 9 mois (D. 161-2-1-9, 3°) + 5"],
  [[1953, 3], "2019-06-01", mois(66, 2), "61 ans et 2 mois (D. 161-2-1-9, 4°) + 5"],
  [[1954, 3], "2021-01-01", mois(66, 7), "61 ans et 7 mois (D. 161-2-1-9, 5°) + 5"],
  [[1960, 3], "2023-08-01", mois(67), "62 ans + 5, la veille de la loi de 2023"],
  [[1960, 3], "2023-10-01", mois(67), "64 ans du premier alinéa + 3"],
  [[1961, 10], "2028-10-01", mois(67), "64 + 3, et non 62 ans et 3 mois + 3"],
];

for (const [[annee, m], effet, attendu, pourquoi] of CAS) {
  test(`né en ${m}/${annee}, pension du ${effet} : ${pourquoi}`, () => {
    assert.equal(enMoisLu(ages.aLEffet(effet).age(generationDe(annee, m))), attendu);
  });
}

test("avant l'ordonnance de 1982, la fiche ne dit rien : le régime garde son droit", () => {
  assert.equal(ages.aLEffet("1983-03-01").age(1915), null);
  assert.equal(enMoisLu(ages.aLEffet("1983-04-01").age(1915)), mois(65));
});

test("le renvoi lit l'âge légal de la version à la date d'effet, avec la fiabilité la plus faible", () => {
  const lu = ages.aLEffet("2018-01-01").age(1952);
  assert.equal(lu[1], 2, "haute : la version de l'âge du taux plein n'est pas recontrôlée");
});

test("droit au 31 août 2023 : né en octobre 1961, 67 ans, soixante-deux ans + 5 sur la loi de 2011", () => {
  const sous = new AgesAnnulationDecote(paquet, new FichesDatees(paquet).sousLeDroit("au_31_aout_2023"));
  const version = sous.aLEffet("2028-10-01");
  assert.equal(version.version, "age_legal_plus_cinq");
  assert.equal(enMoisLu(version.age(generationDe(1961, 10))), mois(67));
});

test("loi de 2023 sans la suspension : 64 + 3, 67 ans dès la génération 1955", () => {
  const sous = new AgesAnnulationDecote(
    paquet, new FichesDatees(paquet).sousLeDroit("loi_2023_sans_suspension"));
  for (const generation of [1955, generationDe(1961, 10), 1964, 1970]) {
    assert.equal(enMoisLu(sous.aLEffet("2030-01-01").age(generation)), mois(67));
  }
});

// L'âge du taux plein d'une PERSONNE, sans pension datée : celui de la version
// sous laquelle elle l'atteint. Il est celui de la table par génération qu'il
// remplace, que les textes donnent (D. 161-2-1-9 plus cinq, puis 67 ans).
test("l'âge d'une personne est celui de la version sous laquelle elle l'atteint", () => {
  const attendu = (generation) => {
    if (generation < 1951.5) return mois(65);
    if (generation < 1952) return mois(65, 4);
    if (generation < 1953) return mois(65, 9);
    if (generation < 1954) return mois(66, 2);
    if (generation < 1955) return mois(66, 7);
    return mois(67);
  };
  for (let annee = 1918; annee <= 1975; annee += 1) {
    for (let m = 1; m <= 12; m += 1) {
      const generation = generationDe(annee, m);
      assert.equal(enMoisLu(ages.age(generation)), attendu(generation), `génération ${generation}`);
    }
  }
});

test("une réforme fictive du premier alinéa à 65 ans en 2030 donne 68 ans aux pensions de 2030", () => {
  const copie = structuredClone(paquet);
  const fiche = copie.fiches_datees[FICHE_DE_L_AGE_LEGAL];
  const derniere = fiche.versions.find((v) => v.bornes[EFFET][1] === null);
  derniere.bornes[EFFET][1] = "2030-01-01";
  fiche.versions.push({
    id: "reforme_fictive", bornes: { [EFFET]: ["2030-01-01", null] }, exception_de: null,
    texte: null, parametres: { age_du_premier_alinea: 65 }, fiabilite: 2,
    redaction_anterieure: { version: derniere.id, generations: [null, null] },
  });
  const fictif = new AgesAnnulationDecote(copie);
  assert.equal(enMoisLu(fictif.aLEffet("2029-12-01").age(1963)), mois(67));
  assert.equal(enMoisLu(fictif.aLEffet("2030-01-01").age(1963)), mois(68));
});

test("un renvoi à une valeur que la version lue ne porte pas arrête le calcul, et nomme les deux fiches", () => {
  const copie = structuredClone(paquet);
  for (const version of copie.fiches_datees[FICHE_DE_L_AGE_LEGAL].versions) {
    delete version.parametres.age_du_premier_alinea;
  }
  assert.throws(() => new AgesAnnulationDecote(copie).aLEffet("2024-01-01").age(1961),
    /age_annulation_decote\.premier_alinea_plus_trois.*age_legal_par_generation\.loi_de_2023/);
});

test("la personne née le 1er du mois compte ses âges de ce mois-là", () => {
  // Née le 1er juillet 1951 : 65 ans et 4 mois le 1er novembre 2016.
  const origine = new DateMois(1951, 7);
  assert.equal(enMoisLu(ages.age(1951.5, origine)), mois(65, 4));
});

// --- Avant le 1er avril 1983, le régime garde sa valeur ---------------------

import { Contexte } from "../../moteur/js/contexte.js";
import * as ouvrir from "../../moteur/js/droit/ouvrir.js";

/**
 * Avant l'ordonnance n° 82-270 (« entreront en vigueur le 1er avril 1983 »,
 * article 9), il n'y a pas de règle commune : la version de la fiche ne dit
 * rien, et le régime qui renvoie garde la valeur de sa période (note de
 * décision 0009, « Le fichier de régime garde son droit propre »), 67 ans à la
 * CARMF de 1980. Depuis, l'âge de l'assuré est celui de la version sous
 * laquelle il l'atteint : soixante-cinq ans pour un né en 1915, parti en 1984.
 */
test("une pension d'avant le 1er avril 1983 garde la valeur de la période du régime", () => {
  const contexte = new Contexte(paquet);
  const simulateur = contexte.simulateur();
  const scenario = simulateur.scenarioActuel;
  const carriere = (age) => simulateur.carriereSimple({
    sexe: "H", niveau_salaire: 1.0, annee_naissance: 1915, mois_naissance: 3,
    jour_naissance: 10, affiliation: "salarie_prive_non_cadre", age_debut: 25,
    age_liquidation: age,
  });
  const carmf = scenario.catalogue.obtenir("carmf_complementaire");
  const avant = carmf.aLaDate("1980-01-01");
  assert.ok(avant.age_taux_plein_par_generation);
  assert.equal(ouvrir.ageTauxPlein(scenario, avant, carriere(65)), avant.age_taux_plein);
  assert.equal(ouvrir.ageTauxPlein(scenario, carmf.aLaDate("1984-01-01"), carriere(69)), 65);
});
