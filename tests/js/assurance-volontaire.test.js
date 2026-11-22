/**
 * L'assurance volontaire vieillesse des salariés expatriés (L. 742-1, 3e
 * alinéa, 1° ; R. 742-4 à R. 742-8, R. 742-30, R. 742-34) : la saisie la dit
 * sur une période passée hors de France, avec sa catégorie, et le régime
 * général la porte au compte comme une période d'assurance obligatoire
 * (action 177, étape 10).
 *
 * Les valeurs attendues viennent de la caisse, non du moteur : le barème
 * « Assurance volontaire - Montants des cotisations par trimestre » de la
 * base de législation de la Cnav (circulaires 2014/24 à 2026/23) donne le
 * salaire forfaitaire de chaque classe, par trimestre — 100 %, 75 %, 50 % et
 * 25 % du quart du plafond annuel —, et l'exposé « Assurance volontaire » dit
 * que « l'assuré qui cotise à l'assurance volontaire au titre de l'assurance
 * vieillesse est censé avoir perçu les salaires correspondant à ses
 * cotisations », reportés au relevé, et que « les trimestres d'assurance se
 * décomptent comme les périodes d'assurance obligatoire » (R. 742-8,
 * R. 351-9). La 4e catégorie, celle des moins de vingt-deux ans, vaut
 * « jusqu'à la fin du trimestre civil qui comprend le 22e anniversaire ».
 *
 *     node --test tests/js/assurance-volontaire.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { ASSURANCE_VOLONTAIRE } from "../../moteur/js/carriere.js";
import { Contexte } from "../../moteur/js/contexte.js";
import { revenusDActivite } from "../../moteur/js/cycle-de-vie.js";
import { ErreurSaisie, Saisie } from "../../moteur/js/saisie.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const contexte = new Contexte(paquet);

const saisie = (requete) => {
  const lue = Saisie.depuisRequete(requete, false, paquet.presomptions);
  lue.verifier();
  return lue;
};
const carriere = (requete) => contexte.carriere(saisie(requete));
const volontaires = (requete) => carriere(requete).lignes
  .filter((ligne) => ligne.affiliation === ASSURANCE_VOLONTAIRE);

/**
 * Née le 15 mars 1962, salariée du privé depuis 1984, partie hors de tout
 * accord de 2015 à 2024, assurée volontaire en 3e catégorie, rentrée en
 * janvier 2025, à la retraite le 1er avril 2027.
 */
const EXPATRIEE = {
  naissance: "1962-03-15", liquidation: "2027-04-01", debut: "1984-01-01",
  statut: "salarie_prive_non_cadre", salaire: "1",
  etranger1_pays: "autre", etranger1_debut: "2015-01-01", etranger1_fin: "2025-01-01",
};
const VOLONTAIRE = { ...EXPATRIEE, etranger1_avv: "3" };

// -- le salaire porté au compte et les trimestres ------------------------------

test("chaque année d'assurance volontaire porte au compte le salaire forfaitaire de sa catégorie", () => {
  const lignes = volontaires(VOLONTAIRE);
  assert.deepEqual(lignes.map((ligne) => ligne.annee),
    [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]);
  // 3e classe, par trimestre : 4 755 € en 2015, 4 827 € en 2016, 5 796 € en
  // 2024 (barème de la Cnav, circulaires 2015/12, 2016/12 et 2024/17).
  const parAnnee = new Map(lignes.map((ligne) => [ligne.annee, ligne]));
  assert.equal(parAnnee.get(2015).revenu, 4 * 4755);
  assert.equal(parAnnee.get(2016).revenu, 4 * 4827);
  assert.equal(parAnnee.get(2024).revenu, 4 * 5796);
  for (const ligne of lignes) {
    assert.equal(ligne.trimestres_valides, 4, `${ligne.annee}`);
    assert.equal(ligne.type_periode, "emploi");
    assert.ok(ligne.cotise, `${ligne.annee} : cotisée par l'assurée`);
  }
});

test("sans assurance volontaire, les années hors de France ne valident rien", () => {
  assert.deepEqual(volontaires(EXPATRIEE), []);
  const annees = carriere(EXPATRIEE).lignes.filter((l) => l.annee >= 2015 && l.annee <= 2024);
  assert.ok(annees.every((ligne) => ligne.trimestres_valides === 0));
});

test("avant le trimestre de ses vingt-deux ans, l'assuré cotise en 4e catégorie", () => {
  // Né le 10 mai 1991 : vingt-deux ans au 2e trimestre 2013. En 2013, deux
  // trimestres de 4e classe (2 314,50 €) puis deux de 1re (9 258 €) ; en
  // 2014, quatre de 1re (9 387 €) : circulaires 2014/24 et 2015/12.
  const lignes = volontaires({
    naissance: "1991-05-10", liquidation: "2056-06-01", debut: "2009-09-01",
    statut: "salarie_prive_non_cadre", salaire: "1",
    etranger1_pays: "autre", etranger1_debut: "2012-01-01", etranger1_fin: "2016-01-01",
    etranger1_avv: "1",
  });
  const parAnnee = new Map(lignes.map((ligne) => [ligne.annee, ligne.revenu]));
  assert.equal(parAnnee.get(2013), 2 * 2314.5 + 2 * 9258);
  assert.equal(parAnnee.get(2014), 4 * 9387);
  // 2012, toute en 4e catégorie : le quart du quart du plafond, 36 372 €.
  assert.equal(parAnnee.get(2012), 36372 / 4);
});

test("seuls comptent les trimestres civils que la période couvre en entier", () => {
  // De février à octobre 2015 : les 2e et 3e trimestres, 2 × 4 755 €, que
  // R. 351-9 compte à 150 heures de SMIC à 9,61 €, soit 1 441,50 € le
  // trimestre — quatre trimestres, comme pour tout salaire de l'année.
  const lignes = volontaires({ ...EXPATRIEE, etranger1_debut: "2015-02-01",
    etranger1_fin: "2015-11-01", etranger1_avv: "3" });
  assert.equal(lignes.length, 1);
  assert.equal(lignes[0].revenu, 2 * 4755);
  assert.equal(lignes[0].fraction_annee, 0.5);
  assert.equal(lignes[0].trimestres_valides, 4);
});

// -- ce que les régimes en font ---------------------------------------------------

const pensions = (requete) => Object.fromEntries(contexte.simuler(saisie(requete))
  .actuel.pensions_par_regime.map((pension) => [pension.regime, pension.montant]));

test("le régime général seul sert l'assurance volontaire : l'Agirc-Arrco n'en sait rien", () => {
  // À 67 ans, le taux plein est acquis avec ou sans l'assurance volontaire :
  // avant, ses trimestres effaceraient aussi la minoration de l'Agirc-Arrco,
  // qui suit celle du régime général, sans rien changer à ses points.
  const aSoixanteSeptAns = { liquidation: "2029-04-01" };
  const avec = pensions({ ...VOLONTAIRE, ...aSoixanteSeptAns });
  const sans = pensions({ ...EXPATRIEE, ...aSoixanteSeptAns });
  assert.ok(avec.regime_general > sans.regime_general,
    `${avec.regime_general} ≤ ${sans.regime_general}`);
  for (const regime of ["agirc_arrco", "arrco", "arrco_tranche_2"]) {
    assert.equal(avec[regime], sans[regime], regime);
  }
});

test("le salaire forfaitaire n'est pas un revenu d'activité : il ne se nette ni ne s'impose", () => {
  const avec = revenusDActivite(carriere(VOLONTAIRE));
  const sans = revenusDActivite(carriere(EXPATRIEE));
  assert.deepEqual([...avec.entries()], [...sans.entries()]);
});

// -- la saisie --------------------------------------------------------------------

test("l'adresse garde la catégorie de l'assurance volontaire", () => {
  const relue = saisie(VOLONTAIRE);
  assert.equal(relue.etranger[0].avv, "3");
  assert.equal(new URLSearchParams(relue.requete()).get("etranger1_avv"), "3");
  assert.equal(new URLSearchParams(saisie(EXPATRIEE).requete()).get("etranger1_avv"), null);
});

const REFUS = [
  [{ etranger1_avv: "4" }, "Période à l'étranger n° 1 : « 4 » n'est pas une catégorie "
    + "d'assurance volontaire — 1, 2 ou 3 ; la 4e, celle des moins de vingt-deux ans, "
    + "s'applique d'elle-même."],
  [{ etranger1_avv: "2", etranger1_activite: "non_salariee" }, "Période à l'étranger "
    + "n° 1 : l'assurance volontaire que ce champ décrit est celle des salariés "
    + "(L. 742-1) ; celle des non-salariés (L. 742-6) n'est pas modélisée."],
  [{ etranger1_avv: "2", etranger1_debut: "2015-02-01", etranger1_fin: "2015-05-01" },
    "Période à l'étranger n° 1 : l'assurance volontaire se paie par trimestre civil "
    + "entier, et la période n'en couvre aucun."],
  [{ etranger1_avv: "2", debut: "1960-01-01", naissance: "1942-03-15",
    liquidation: "2004-04-01", etranger1_debut: "1965-01-01", etranger1_fin: "1970-01-01" },
  "Période à l'étranger n° 1 : l'assurance volontaire des salariés expatriés ne court "
    + "qu'à partir de juillet 1966 (loi n° 65-555 du 10 juillet 1965, décret "
    + "n° 66-303 du 13 mai 1966)."],
  [{ etranger1_avv: "2", releve: "2014:salarie_prive_non_cadre:30000" },
    "Période à l'étranger n° 1 : un relevé porte déjà les salaires de l'assurance "
    + "volontaire ; écrivez-les à ses années, sous le statut "
    + "« assure_volontaire_expatrie »."],
];

for (const [champs, message] of REFUS) {
  test(`refusé : ${message.slice(0, 70)}…`, () => {
    assert.throws(() => carriere({ ...EXPATRIEE, ...champs }),
      (erreur) => erreur instanceof ErreurSaisie && erreur.message === message);
  });
}

test("le statut de l'assurance volontaire ne se choisit pas pour un métier", () => {
  assert.throws(() => carriere({ ...EXPATRIEE, statut: ASSURANCE_VOLONTAIRE }),
    (erreur) => erreur instanceof ErreurSaisie
      && erreur.message.includes("se déclare sur une période à l'étranger"));
});

test("un relevé dit l'assurance volontaire par son statut, au régime général seul", () => {
  const lignes = carriere({
    naissance: "1962-03-15", liquidation: "2027-04-01",
    releve: "2014:salarie_prive_non_cadre:30000\n2015:assure_volontaire_expatrie:19020",
  }).lignes.filter((ligne) => ligne.annee === 2015);
  assert.equal(lignes.length, 1);
  assert.equal(lignes[0].affiliation, ASSURANCE_VOLONTAIRE);
  assert.equal(lignes[0].revenu, 19020);
  assert.equal(lignes[0].trimestres_valides, 4);
});
