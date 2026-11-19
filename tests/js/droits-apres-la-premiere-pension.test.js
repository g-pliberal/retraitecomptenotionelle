/**
 * Les droits de l'activité après le départ et la seconde pension se lisent
 * dans leurs fiches (action 191, étape 2 du domaine du cumul).
 *
 * Le portage n'écrit plus les dates qui découpent ces deux règles : il lit la
 * version de `droits_apres_la_premiere_pension` qui vaut à la date de la
 * première pension et à celle du mois d'activité, et celle de
 * `seconde_pension` qui vaut à la date d'effet de la nouvelle pension et à
 * celle de la première (`fiches_datees`, `versionAuxDates`).
 *
 * Les valeurs attendues viennent des textes que les versions citent, relus
 * dans les index LEGI et KALI le 19 novembre 2026 : L. 161-22-1 A, pour les
 * premières pensions prises à compter du 1er janvier 2015 (loi n° 2014-40,
 * article 19, VIII) ; L. 161-22-1, pour « les droits […] constitués à partir
 * du 1er janvier 2023 » (loi n° 2023-270, article 26, XII) ; la rédaction de
 * la loi n° 2025-1403, pour qui entre « en jouissance de [sa] première
 * pension de vieillesse de base à compter du 1er janvier 2027 » (article 102,
 * XI) ; « 5 % du montant annuel du plafond », pour les nouvelles pensions
 * « prenant effet à compter du 1er septembre 2023 » (D. 161-2-22-1) ; la
 * deuxième pension de l'Agirc-Arrco, qui « prend effet, au plus tôt, le 1er
 * janvier 2024 » (accord du 17 novembre 2017, article 91) ; l'article 27 du
 * règlement du RCI, en vigueur le 1er janvier 2025.
 *
 * Et la preuve que les fiches pilotent : une version retouchée dans une copie
 * du paquet déplace ce que le portage rend.
 *
 *     node --test tests/js/droits-apres-la-premiere-pension.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { DateMois } from "../../moteur/js/calendrier.js";
import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import * as seconde from "../../moteur/js/droit/seconde.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const DROITS = "droits_apres_la_premiere_pension";
const SECONDE = "seconde_pension";

/** Le moteur du droit réel, sur ce paquet. */
function moteurSur(donnees) {
  return new Simulateur(donnees, { ...PARAMETRES_DEFAUT }).scenarioActuel;
}

/** Le paquet, une version d'une fiche retouchée par `retouche`. */
function paquetRetouche(fiche, version, retouche) {
  const copie = structuredClone(paquet);
  retouche(copie.fiches_datees[fiche].versions.find((v) => v.id === version));
  return copie;
}

const moteur = moteurSur(paquet);
const mois = (annee, rang) => new DateMois(annee, rang);

/** Ce que le droit fait d'un mois d'activité, sans cumul intégral ni pension militaire. */
function motif(leMoteur, leMois, premiere, { integral = null, sixMois = false,
  militaire = false, nouveaux = false } = {}) {
  return seconde.motif(leMoteur, leMois, premiere, integral, sixMois, militaire, nouveaux);
}

test("le paquet porte les deux fiches, et les dates qui décident de chacune", () => {
  const droits = paquet.fiches_datees[DROITS];
  assert.ok(droits, `${DROITS} manque à fiches_datees`);
  assert.deepEqual(droits.dates_qui_decident,
    ["liquidation.premiere_pension_de_base", "droit_acquis"]);
  assert.deepEqual(droits.versions.map((v) => v.id),
    ["sans_regle_generale", "loi_2014", "loi_2023", "lfss_2026"]);
  const laSeconde = paquet.fiches_datees[SECONDE];
  assert.ok(laSeconde, `${SECONDE} manque à fiches_datees`);
  assert.deepEqual(laSeconde.dates_qui_decident,
    ["liquidation.date_effet", "liquidation.premiere_pension_de_base"]);
  assert.deepEqual(laSeconde.versions.map((v) => v.id),
    ["sans_droit_avant_2023", "loi_2023", "lfss_2026"]);
});

test("avant 2023, la date de la première pension choisit la règle (L. 161-22-1 A)", () => {
  // Première pension de décembre 2014 : aucune règle générale, chaque régime la sienne.
  assert.deepEqual(motif(moteur, mois(2016, 1), mois(2014, 12), { nouveaux: true }),
    ["regimes_non_liquides", "sans_regle_generale"]);
  assert.deepEqual(motif(moteur, mois(2016, 1), mois(2014, 12)),
    ["regime_liquide", "sans_regle_generale"]);
  // Première pension de janvier 2015 : plus aucun droit, cumul intégral ou non.
  assert.deepEqual(motif(moteur, mois(2016, 1), mois(2015, 1), { integral: mois(2015, 1) }),
    ["eteints", "loi_2014"]);
});

test("depuis le 1er janvier 2023, le cumul intégral ouvre une nouvelle pension", () => {
  const premiere = mois(2022, 6);
  const integral = { integral: premiere };
  assert.deepEqual(motif(moteur, mois(2022, 12), premiere, integral), ["eteints", "loi_2014"]);
  assert.deepEqual(motif(moteur, mois(2023, 1), premiere, integral),
    ["nouvelle_pension", "loi_2023"]);
  // Sans le cumul intégral, ou avant lui : rien.
  assert.deepEqual(motif(moteur, mois(2023, 1), premiere), ["eteints", "loi_2023"]);
  assert.deepEqual(motif(moteur, mois(2023, 1), premiere, { integral: mois(2023, 6) }),
    ["eteints", "loi_2023"]);
  // Chez le dernier employeur dans les six mois : jamais (L. 161-22-1, 2°).
  assert.deepEqual(motif(moteur, mois(2023, 1), premiere, { ...integral, sixMois: true }),
    ["dernier_employeur", "loi_2023"]);
  // Une première pension d'avant 2015 n'y échappe plus : la règle vaut pour tous.
  assert.deepEqual(motif(moteur, mois(2023, 1), mois(2010, 1), { nouveaux: true }),
    ["eteints", "loi_2023"]);
});

test("la première pension de 2027 relève de la rédaction de la loi n° 2025-1403", () => {
  assert.deepEqual(motif(moteur, mois(2027, 6), mois(2026, 12)), ["eteints", "loi_2023"]);
  assert.deepEqual(motif(moteur, mois(2027, 6), mois(2027, 1)), ["eteints", "lfss_2026"]);
  assert.deepEqual(motif(moteur, mois(2030, 1), mois(2027, 1), { integral: mois(2029, 1) }),
    ["nouvelle_pension", "lfss_2026"]);
});

test("la pension militaire n'éteint pas les droits (L. 84 du code des pensions)", () => {
  const militaire = { militaire: true };
  assert.deepEqual(motif(moteur, mois(2021, 1), mois(2020, 1), militaire),
    ["pension_militaire", "loi_2014"]);
  assert.deepEqual(motif(moteur, mois(2023, 2), mois(2020, 1), militaire),
    ["pension_militaire", "loi_2023"]);
});

test("la règle du militaire est la version qui vaut pour sa première pension", () => {
  const militaire = { militaire: true };
  // L. 161-22-1 A n'est « applicable [qu']aux assurés dont la première pension
  // prend effet à compter du 1er janvier 2015 » (loi n° 2014-40, article 19,
  // VIII) : avant, aucune règle générale, et non celle de 2014.
  assert.deepEqual(motif(moteur, mois(2012, 6), mois(2010, 1), militaire),
    ["pension_militaire", "sans_regle_generale"]);
  assert.deepEqual(motif(moteur, mois(2022, 12), mois(2014, 12), militaire),
    ["pension_militaire", "sans_regle_generale"]);
  assert.deepEqual(motif(moteur, mois(2023, 1), mois(2014, 12), militaire),
    ["pension_militaire", "loi_2023"]);
  // La rédaction de la loi n° 2025-1403 vaut pour qui entre « en jouissance de
  // [sa] première pension de vieillesse de base à compter du 1er janvier 2027 »
  // (article 102, XI).
  assert.deepEqual(motif(moteur, mois(2026, 12), mois(2026, 12), militaire),
    ["pension_militaire", "loi_2023"]);
  assert.deepEqual(motif(moteur, mois(2028, 3), mois(2027, 1), militaire),
    ["pension_militaire", "lfss_2026"]);
});

test("la fiche des droits pilote : ses bornes retouchées déplacent la règle", () => {
  // Une réforme fictive : la règle de 2014 ne vaut qu'à compter de 2016.
  const copie = structuredClone(paquet);
  const versions = copie.fiches_datees[DROITS].versions;
  const borne = "liquidation.premiere_pension_de_base";
  versions.find((v) => v.id === "sans_regle_generale").bornes[borne][1] = "2016-01-01";
  versions.find((v) => v.id === "loi_2014").bornes[borne][0] = "2016-01-01";
  const autre = moteurSur(copie);
  assert.deepEqual(motif(autre, mois(2016, 6), mois(2015, 6), { nouveaux: true }),
    ["regimes_non_liquides", "sans_regle_generale"]);
  assert.deepEqual(motif(moteur, mois(2016, 6), mois(2015, 6), { nouveaux: true }),
    ["eteints", "loi_2014"]);
});

test("sans l'une des fiches au paquet, le calcul s'arrête", () => {
  for (const fiche of [DROITS, SECONDE]) {
    const copie = structuredClone(paquet);
    delete copie.fiches_datees[fiche];
    const sans = moteurSur(copie);
    assert.throws(() => {
      motif(sans, mois(2024, 1), mois(2022, 6));
      seconde.regleDeLaNouvellePension(sans, mois(2025, 1), mois(2022, 6));
    }, new RegExp(fiche));
  }
});

test("la nouvelle pension prend effet au plus tôt le 1er septembre 2023", () => {
  const premiere = mois(2022, 6);
  assert.deepEqual(seconde.effetDeLaNouvellePension(moteur, mois(2023, 7), premiere),
    mois(2023, 9));
  assert.deepEqual(seconde.effetDeLaNouvellePension(moteur, mois(2023, 9), premiere),
    mois(2023, 9));
  assert.deepEqual(seconde.effetDeLaNouvellePension(moteur, mois(2025, 2), premiere),
    mois(2025, 2));
  // La fiche pilote : sa borne retouchée déplace la date.
  const copie = structuredClone(paquet);
  const versions = copie.fiches_datees[SECONDE].versions;
  versions.find((v) => v.id === "sans_droit_avant_2023")
    .bornes["liquidation.date_effet"][1] = "2023-11-01";
  for (const id of ["loi_2023", "lfss_2026"]) {
    versions.find((v) => v.id === id).bornes["liquidation.date_effet"][0] = "2023-11-01";
  }
  assert.deepEqual(seconde.effetDeLaNouvellePension(moteurSur(copie), mois(2023, 7), premiere),
    mois(2023, 11));
});

test("le plafond de 5 % vient de la fiche, et tombe pour les premières pensions de 2027", () => {
  assert.equal(seconde.regleDeLaNouvellePension(moteur, mois(2025, 2), mois(2022, 6))
    .plafond_en_pass, 0.05);
  assert.equal(seconde.regleDeLaNouvellePension(moteur, mois(2030, 1), mois(2026, 12))
    .plafond_en_pass, 0.05);
  assert.equal(seconde.regleDeLaNouvellePension(moteur, mois(2030, 1), mois(2027, 1))
    .plafond_en_pass, null);
  assert.equal(seconde.regleDeLaNouvellePension(moteur, mois(2023, 8), mois(2022, 6))
    .existe, false);
});

test("la nouvelle pension est écrêtée au plafond que porte sa version", () => {
  // Trois plafonds de salaire sur douze mois de 2024, effet en janvier 2025, et une
  // durée requise posée à huit trimestres : la moitié du taux plein, un quart du
  // plafond, loin au-dessus de 5 %.
  const pass = (annee) => moteur.macro.plafond_securite_sociale.valeur(annee);
  const salaires = new Map([[2024, 3 * pass(2024)]]);
  const periode = new Map([[2024, 12]]);
  const effet = mois(2025, 1);
  const pension = (leMoteur) => seconde.nouvellePension(leMoteur, "regime_general", salaires,
    periode, effet, 8, seconde.regleDeLaNouvellePension(leMoteur, effet, mois(2022, 6)));
  const reelle = pension(moteur);
  assert.ok(reelle.brute > reelle.plafond);
  assert.equal(reelle.plafond, 0.05 * pass(2025));
  assert.equal(reelle.montant, 0.05 * pass(2025));
  const autre = moteurSur(paquetRetouche(SECONDE, "loi_2023",
    (version) => { version.parametres.plafond_en_pass = 0.02; }));
  assert.equal(pension(autre).montant, 0.02 * pass(2025));
  // Première pension de 2027 : plus de plafond.
  const sansPlafond = seconde.nouvellePension(moteur, "regime_general", salaires, periode,
    mois(2030, 1), 8, seconde.regleDeLaNouvellePension(moteur, mois(2030, 1), mois(2027, 1)));
  assert.equal(sansPlafond.plafond, null);
  assert.equal(sansPlafond.montant, sansPlafond.brute);
});

test("les dates des secondes retraites complémentaires viennent de la fiche", () => {
  const regle = seconde.regleDeLaNouvellePension(moteur, mois(2025, 2), mois(2022, 6));
  assert.equal(regle.agirc_arrco_effet_au_plus_tot, "2024-01-01");
  assert.equal(regle.rci_droits_depuis, "2025-01-01");
  const de2027 = seconde.regleDeLaNouvellePension(moteur, mois(2030, 1), mois(2027, 1));
  assert.equal(de2027.agirc_arrco_effet_au_plus_tot, "2024-01-01");
  assert.equal(de2027.rci_droits_depuis, "2025-01-01");
});

test("le portage n'écrit plus les dates ni le plafond des deux règles", () => {
  for (const nom of ["PREMIERE_2015", "DROITS_2023", "LIQUIDATION_2023",
    "LIQUIDATION_AGIRC_ARRCO", "DROITS_RCI", "PREMIERE_2027", "PLAFOND_EN_PASS"]) {
    assert.ok(!(nom in seconde), `${nom} est encore une constante du portage`);
  }
});
