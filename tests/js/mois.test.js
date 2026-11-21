/**
 * Le mois de la liquidation, sur le portage du site : action 161, quatrième
 * vague, les tests du mois que `test_moteur.py` tenait sur le module Python
 * (la date de liquidation, l'origine des âges, l'arrondi au mois, l'année du
 * départ au prorata, ses trimestres bornés, le relevé tronqué, le taux de
 * remplacement annualisé, la circulaire de revalorisation du mois), éprouvés
 * sur `moteur/js/calendrier.js`, `moteur/js/carriere.js`, `moteur/js/macro.js`
 * et `moteur/js/simulateur.js`.
 *
 * Les attendus sont ceux du droit, posés à la main : R. 351-37 (les âges se
 * comptent du mois qui suit la naissance, sauf pour qui est né un 1er),
 * R. 351-9 (les trimestres de l'année du départ bornés aux trimestres
 * civils), la circulaire Cnav n° 2026-07, point 1.1, et la revalorisation
 * exceptionnelle de 4 % au 1er juillet 2022 (soit +3,9 % sur la colonne de
 * janvier, que la circulaire porte).
 *
 *     node --test tests/js/mois.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { DateMois, enMois, formaterAge, origineDesAges } from "../../moteur/js/calendrier.js";
import { AnneeCarriere, Carriere, PROFIL_SMIC } from "../../moteur/js/carriere.js";
import * as chrono from "../../moteur/js/chronologie.js";
import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { DonneesMacro } from "../../moteur/js/macro.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur", "donnees.json"), "utf8"));
const macro = new DonneesMacro(paquet);
const JOUR_PRESUME = chrono.valeur("jour_de_naissance", paquet.presomptions);

const proche = (valeur, attendu, ecart, message) =>
  assert.ok(Math.abs(valeur - attendu) <= ecart,
    `${message ?? ""} ${valeur} au lieu de ${attendu} ± ${ecart}`);

const enClair = (date) => [date.annee, date.mois];

/**
 * Une carrière sans ligne. Sans jour dit, la présomption du paquet le pose,
 * comme la saisie : le constructeur ne lit pas le paquet, la chronologie
 * lui est donc passée.
 */
function sansLigne(annee_naissance, mois_naissance, age_liquidation, jour = 1) {
  const chronologie = jour === null
    ? chrono.duResume(annee_naissance, "H", mois_naissance, age_liquidation, 0, [], null,
      paquet.presomptions)
    : null;
  return new Carriere({ annee_naissance, sexe: "H", mois_naissance, age_liquidation,
    lignes: [], jour_naissance: jour, chronologie });
}

const depuisProfil = (age_liquidation, options = {}) => Carriere.depuisProfil({
  annee_naissance: 1962, sexe: "H", affiliation: "salarie_prive_non_cadre", age_debut: 22,
  age_liquidation, macro, jour_naissance: 1, ...options,
});

test("la liquidation est datée au mois, et non arrondie à l'année", () => {
  // « Soixante-quatre ans et six mois » n'est pas « soixante-cinq ans » : la
  // date se lit en mois depuis la naissance, depuis le mois qui la suit pour
  // qui n'est pas né un 1er (R. 351-37).
  const date = (naissance, mois, age, jour = 1) =>
    enClair(sansLigne(naissance, mois, age, jour).dateLiquidation);
  // Né le 1er mars 1962, parti à 64 ans et 6 mois : septembre 2026.
  assert.deepEqual(date(1962, 3, 64.5), [2026, 9]);
  assert.deepEqual(date(1962, 1, 64.5), [2026, 7]);
  // La parité du millésime ne décide de rien.
  assert.equal(date(1961, 1, 64.5)[1], 7);
  assert.equal(date(1962, 1, 64.5)[1], 7);
  // Un âge entier et une naissance au 1er janvier tombent au 1er janvier.
  assert.deepEqual(date(1975, 1, 64), [2039, 1]);
  // Né en mars sans dire le jour, l'assuré part comme au jour présumé, le
  // 15 : 64 ans et 6 mois au 1er octobre.
  assert.deepEqual(date(1962, 3, 64.5, null), date(1962, 3, 64.5, JOUR_PRESUME));
  assert.deepEqual(date(1962, 3, 64.5, 15), [2026, 10]);
});

test("les âges se comptent du mois qui suit la naissance", () => {
  // Né le 16 mai 1964, l'assuré a 62 ans et 9 mois le 16 février 2027 et part
  // au 1er mars au plus tôt (circulaire Cnav n° 2026-07, point 1.1) ; né le
  // 1er mai, au 1er février.
  assert.deepEqual(enClair(origineDesAges(new DateMois(1964, 5), 1)), [1964, 5]);
  assert.deepEqual(enClair(origineDesAges(new DateMois(1964, 5), 16)), [1964, 6]);
  assert.deepEqual(enClair(origineDesAges(new DateMois(1964, 12), 31)), [1965, 1]);

  const neLe = (jour) => sansLigne(1964, 5, 62.75, jour);
  const [seize, premier, presume] = [neLe(16), neLe(1), neLe(null)];
  assert.deepEqual(enClair(seize.dateLiquidation), [2027, 3]);
  assert.deepEqual(enClair(premier.dateLiquidation), [2027, 2]);
  assert.deepEqual(enClair(seize.moisDeLAnniversaire(62.75)), [2027, 2]);
  proche(seize.ageAu(new DateMois(2027, 3)), 62.75, 1e-12);
  proche(premier.ageAu(new DateMois(2027, 3)), 62 + 10 / 12, 1e-12);
  // La génération reste au vrai mois.
  assert.equal(seize.generation, premier.generation);
  assert.equal(presume.generation, premier.generation);
  assert.equal(presume.jourDeNaissance, JOUR_PRESUME);
  assert.deepEqual(enClair(presume.dateLiquidation), enClair(neLe(JOUR_PRESUME).dateLiquidation));
});

test("un demi-mois compte le mois qui suit", () => {
  // Atteint à la moitié d'un mois, l'âge compte le mois qui suit (fiche
  // `date_effet_mois_suivant`) : 64 + 1/8 an = 769,5 mois → 770.
  assert.deepEqual([1, 3, 5, 7].map((k) => enMois(64 + k / 8)), [770, 773, 776, 779]);
  assert.equal(formaterAge(64.375), "64 ans et 5 mois");
  // Né le 1er janvier 1962, il a 64 ans et 5 mois au 1er juin 2026.
  assert.deepEqual(enClair(sansLigne(1962, 1, 64.375).dateLiquidation), [2026, 6]);
  // Aucun demi-mois ne se perd selon la parité du mois.
  for (let mois = 0; mois < 960; mois += 1) {
    assert.equal(enMois((mois + 0.5) / 12), mois + 1, `${mois} mois et demi`);
  }
});

test("l'année de liquidation est portée au compte au prorata", () => {
  // Partir en décembre, ce n'est pas travailler onze mois pour rien.
  const capitaux = [];
  for (let mois = 0; mois < 12; mois += 1) {
    const carriere = depuisProfil(64 + mois / 12);
    const ligne = carriere.ligne(carriere.anneeLiquidation);
    if (mois === 0) {
      // Départ au 1er janvier : aucun mois de l'année n'est travaillé.
      assert.ok(ligne === null || carriere.partRetenue(2026) === 0);
    } else {
      proche(ligne.fraction_annee, mois / 12, 1e-12, `${mois} mois`);
      assert.ok(ligne.revenu > 0);
    }
    capitaux.push(carriere.lignes.reduce((somme, l) => somme + l.revenu, 0));
  }
  assert.deepEqual(capitaux, [...capitaux].sort((a, b) => a - b));
  assert.ok(capitaux[11] > capitaux[0]);
});

test("les trimestres de l'année du départ sont bornés aux trimestres civils", () => {
  // On ne valide pas quatre trimestres en sept mois : R. 351-1 arrête les
  // cotisations au dernier jour du trimestre civil précédant la date d'effet.
  const attendus = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3];
  attendus.forEach((attendu, mois) => {
    const carriere = depuisProfil(64 + mois / 12, { niveau_salaire: 3.0 });
    const ligne = carriere.ligne(carriere.anneeLiquidation);
    assert.equal(ligne === null ? 0 : carriere.trimestresRetenus(ligne), attendu, `${mois} mois`);
  });
});

test("l'année d'entrée valide ce que son salaire vaut, au plus quatre (R. 351-9)", () => {
  // R. 351-9 (LEGIARTI000028751530, du 21 mars 2014) : « autant de
  // trimestres que le salaire annuel [...] représente de fois le montant du
  // salaire minimum de croissance en vigueur au 1er janvier de l'année
  // considérée calculé sur la base de 150 heures, avec un maximum de quatre
  // trimestres par année civile » — aucun plafond par mois d'activité. Entré
  // au SMIC à temps plein le 1er octobre 2015 : 3 × 151,67 h × 9,61 € =
  // 4 372,6 €, sous un seuil de 150 × 9,61 = 1 441,50 € : trois trimestres,
  // et non le seul trimestre civil de ses trois mois.
  const carriere = Carriere.depuisParcours({
    annee_naissance: 1995, sexe: "H", jour_naissance: 1, macro,
    metiers: [{ affiliation: "salarie_prive_non_cadre", age_debut: 20.75, niveau_salaire: 1.0 }],
    profil_carriere: PROFIL_SMIC, age_liquidation: 64,
  });
  const ligne = carriere.ligne(2015);
  proche(ligne.fraction_annee, 3 / 12, 1e-12, "trois mois");
  proche(ligne.revenu, 4372.6, 1, "le salaire de 2015");
  assert.equal(ligne.trimestres_valides, 3);
  assert.equal(carriere.trimestresRetenus(ligne), 3);
  assert.equal(carriere.plafondTrimestres(2015), 4);
});

test("un relevé déclarant douze mois est tronqué au point de départ", () => {
  // Né le 1er janvier 1962, l'assuré a 64 ans et 6 mois le 1er juillet 2026 :
  // de son année de départ, six mois comptent.
  const lignes = () => Array.from({ length: 2027 - 1985 }, (_, i) => new AnneeCarriere({
    annee: 1985 + i, revenu: 40_000.0, affiliation: "salarie_prive_non_cadre" }));
  const carriere = new Carriere({ annee_naissance: 1962, sexe: "H", lignes: lignes(),
    age_liquidation: 64.5, jour_naissance: 1 });
  assert.equal(carriere.anneeLiquidation, 2026);
  proche(carriere.partRetenue(2026), 0.5, 1e-12);
  assert.equal(carriere.trimestresRetenus(carriere.ligne(2026)), 2);
  assert.equal(carriere.partRetenue(2027), 0.0);
  // Départ au 1er janvier : l'année du départ ne compte pour rien.
  const janvier = new Carriere({ annee_naissance: 1962, sexe: "H", lignes: lignes(),
    age_liquidation: 64.0, jour_naissance: 1 });
  assert.equal(janvier.partRetenue(2026), 0.0);
});

test("le taux de remplacement rapporte un revenu annualisé", () => {
  // Six mois de salaire ne répondent pas d'une pension annuelle : aucun mois
  // ne fait bondir le taux.
  const simulateur = new Simulateur(paquet, PARAMETRES_DEFAUT);
  const taux = [];
  for (let mois = 0; mois < 12; mois += 1) {
    const carriere = simulateur.carriereSimple({
      annee_naissance: 1962, sexe: "H", affiliation: "salarie_prive_non_cadre", age_debut: 22,
      age_liquidation: 64 + mois / 12, profil_carriere: "plat" });
    taux.push(simulateur.simuler(carriere).tauxRemplacementActuel);
  }
  for (let i = 1; i < taux.length; i += 1) {
    assert.ok(Math.abs(taux[i] / taux[i - 1] - 1) < 0.03, taux.join(", "));
  }
  assert.ok(taux.every((t) => t > 0.2 && t < 1.2), taux.join(", "));
});

test("le mois de liquidation désigne la circulaire de revalorisation", () => {
  // Deux circulaires portent l'année 2022 ; celle du 1er juillet ajoute 3,9 %.
  const lu = (depart, arrivee, mois) =>
    macro.coefficientRevalorisationPorteeAuCompte(depart, arrivee, mois);
  const janvier = lu(2015, 2022, 1);
  const juillet = lu(2015, 2022, 7);
  assert.ok(juillet > janvier);
  proche(juillet / janvier, 1.039, 0.002);
  // La colonne ne s'applique qu'à compter de sa date d'effet.
  proche(lu(2015, 2022, 6), janvier, 1e-9 * janvier);
  proche(lu(2015, 2022, 12), juillet, 1e-9 * juillet);
});
