/**
 * La surcote du régime général se lit dans les versions de sa fiche (note de
 * décision 0009, étape 3, quatrième session).
 *
 * Le portage ne lit plus les lignes `regime_general` du barème daté
 * (`legislation/surcote_baremes.csv`) : il lit, dans le paquet
 * (`fiches_datees`), les versions de la fiche `surcote_regime_general`. La date
 * d'effet de la pension choisit la version, la date de chaque trimestre sa
 * ligne (« Deux dates peuvent décider, l'une dans l'autre »).
 *
 * Les taux attendus viennent des textes : D. 351-1-4 dans sa rédaction du
 * décret n° 2004-156 (« 0,75 % par trimestre ») ; dans celle du décret
 * n° 2006-1611, articles 1er et 3 (« 1° 0,75 % du premier au quatrième
 * trimestre ; 2° 1 % au-delà du quatrième trimestre ; 3° ou, quel que soit son
 * rang, 1,25 % pour chaque trimestre accompli après le soixante-cinquième
 * anniversaire », « applicables aux pensions prenant effet à compter du
 * 1er janvier 2007 ») ; dans celle du décret n° 2008-1509, article 5 (« La
 * majoration est égale à 1,25 % pour chaque trimestre accompli à compter du
 * 1er janvier 2009 »). L'exemple de la circulaire Cnav 2004/37, point 41 :
 * « 5 x 0,75 % = 0,0375 ».
 *
 *     node --test tests/js/surcote-versions.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { DateMois } from "../../moteur/js/calendrier.js";
import { AgesOuverture, FICHE_DE_LA_SURCOTE, SurcoteBaremes } from "../../moteur/js/regimes.js";
import { ageLegalALaDateDEffet, ageOuvertureCommun } from "../../moteur/js/droit/ouvrir.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const EFFET = "liquidation.date_effet";

const baremes = new SurcoteBaremes(paquet);

test("le paquet porte la fiche de la surcote, ses quatre versions choisies à la date d'effet", () => {
  assert.equal(FICHE_DE_LA_SURCOTE, "surcote_regime_general");
  const fiche = paquet.fiches_datees[FICHE_DE_LA_SURCOTE];
  assert.ok(fiche, "la fiche manque à fiches_datees");
  assert.deepEqual(fiche.dates_qui_decident, [EFFET]);
  assert.deepEqual(fiche.versions.map((v) => [v.id, v.bornes[EFFET]]), [
    ["sans_surcote", [null, "2004-01-01"]],
    ["loi_de_2003", ["2004-01-01", "2007-01-01"]],
    ["decret_de_2006", ["2007-01-01", "2009-01-01"]],
    ["lfss_2009", ["2009-01-01", null]],
  ]);
});

test("le barème daté du paquet n'a plus de ligne du régime général", () => {
  assert.deepEqual(paquet.surcote_baremes.filter((ligne) => ligne[0] === "regime_general"), []);
  assert.ok(baremes.connait("regime_general"), "la fiche le fait connaître");
  assert.ok(baremes.connait("fonction_publique"));
});

test("les soixante-cinq ans de la surcote sont un paramètre des versions de 2006 et de 2009", () => {
  const fiche = paquet.fiches_datees[FICHE_DE_LA_SURCOTE];
  const ages = Object.fromEntries(fiche.versions.map((v) => [v.id, v.parametres.age_majore ?? null]));
  assert.deepEqual(ages, { sans_surcote: null, loi_de_2003: null, decret_de_2006: 65, lfss_2009: 65 });
  assert.equal(baremes.ageMajore("regime_general", new DateMois(2006, 1)), null);
  assert.equal(baremes.ageMajore("regime_general", new DateMois(2007, 1)), 65);
  assert.equal(baremes.ageMajore("fonction_publique", new DateMois(2007, 1)), null);
});

/** Des trimestres civils consécutifs, à partir de `annee`/`mois`. */
function trimestres(annee, mois, nombre, apres65 = false) {
  const dates = [];
  let date = new DateMois(annee, mois);
  for (let i = 0; i < nombre; i += 1) {
    dates.push([date, apres65]);
    date = date.plusMois(3);
  }
  return dates;
}

// Trimestres, date d'effet, coefficient attendu, et le calcul posé au texte.
const CAS = [
  [trimestres(2004, 1, 5), [2005, 7], 1.0375,
    "circulaire Cnav 2004/37, point 41 : 5 x 0,75 % = 0,0375"],
  [trimestres(2004, 4, 6), [2006, 1], 1.045,
    "né le 15/01/1944, six trimestres en 2004-2005 : 6 x 0,75 % (rédaction de 2004)"],
  [trimestres(2004, 4, 6), [2007, 1], 1.05,
    "les mêmes, pension de 2007 : 4 x 0,75 % + 2 x 1 % (décret n° 2006-1611)"],
  [trimestres(2005, 4, 4, true), [2006, 7], 1.03,
    "né le 15/01/1940, quatre trimestres après 65 ans, pension de 2006 : 4 x 0,75 %"],
  [trimestres(2005, 4, 4, true), [2007, 1], 1.05,
    "les mêmes, pension de 2007 : 4 x 1,25 %, quel que soit leur rang"],
  [trimestres(2008, 1, 8), [2010, 1], 1.08,
    "né le 15/01/1948, quatre trimestres en 2008, quatre en 2009 : 4 x 0,75 % + 4 x 1,25 %"],
];

for (const [dates, [annee, mois], attendu, pourquoi] of CAS) {
  test(`surcote : ${pourquoi}`, () => {
    const [coefficient] = baremes.coefficient("regime_general", dates, new DateMois(annee, mois));
    assert.ok(Math.abs(coefficient - attendu) < 1e-9, `${coefficient} au lieu de ${attendu}`);
  });
}

test("la fonction publique garde son barème daté, vingt trimestres au plus jusqu'en 2008", () => {
  // Vingt-quatre trimestres de 2003 à 2009 : aucun avant 2004, vingt de 2004 à
  // 2008 à 0,75 %, quatre de 2009 à 1,25 % (L. 14 III).
  const [coefficient] = baremes.coefficient(
    "fonction_publique", trimestres(2003, 1, 28), new DateMois(2010, 1));
  assert.ok(Math.abs(coefficient - (1 + 20 * 0.0075 + 4 * 0.0125)) < 1e-9, String(coefficient));
});

test("sans date d'effet, la surcote du régime général ne choisit pas de version : le calcul s'arrête", () => {
  assert.throws(() => baremes.coefficient("regime_general", trimestres(2009, 1, 2), null),
    /date d'effet/);
});

/**
 * Le renvoi à l'âge légal se lit à la date d'effet (note 0009 : « Les renvois
 * de la surcote à l'âge légal et à la durée requise suivent la date d'effet »),
 * et non dans la version sous laquelle le droit de la personne s'est ouvert.
 */
test("l'âge légal de la surcote : né en 1955, pension de 2030, la version de la suspension", () => {
  const moteur = { agesOuverture: new AgesOuverture(paquet) };
  const carriere = { generation: 1955.0, age_liquidation: 75, dateLiquidation: new DateMois(2030, 1) };
  const periode = { age_ouverture_par_generation: true };
  assert.equal(ageLegalALaDateDEffet(moteur, periode, carriere), 62);
});

test("l'âge légal de la surcote suit la version de la date d'effet, même quand elle diffère", () => {
  // Une version fictive, en vigueur en 2030, qui opposerait 64 ans aux nés en
  // 1955 : la surcote la suit, l'âge de la personne non.
  const copie = structuredClone(paquet);
  const fiche = copie.fiches_datees.age_legal_par_generation;
  const version = fiche.versions.find((v) => {
    const [debut, fin] = v.bornes[EFFET];
    return (debut === null || debut <= "2030-01-01") && (fin === null || "2030-01-01" < fin);
  });
  delete version.redaction_anterieure;
  version.table = [[1955.0, 1956.0, 64, 4]];
  const moteur = { agesOuverture: new AgesOuverture(copie) };
  const carriere = { generation: 1955.0, age_liquidation: 75, dateLiquidation: new DateMois(2030, 1) };
  const periode = { age_ouverture_par_generation: true };
  assert.equal(ageLegalALaDateDEffet(moteur, periode, carriere), 64);
  assert.equal(ageOuvertureCommun(moteur, periode, carriere), 62);
});
