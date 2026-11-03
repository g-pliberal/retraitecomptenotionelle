/**
 * Le barème du régime unique (`bareme_regime_unique`, action 161) : ce que le
 * régime unique prélève après la bascule, par tranches du plafond de la
 * Sécurité sociale, à la place du taux du statut pivot que la fusion retient —
 * les barèmes B, C et D que `scripts/solde_fusion.py` chiffre. Le défaut,
 * `null`, garde le taux du régime fusionné.
 *
 * Un barème est une suite de tranches `[haute, taux, tauxSalarie]` : la borne
 * haute de la tranche, en plafonds annuels (`null` : sans plafond), le taux
 * total qu'elle prélève, et ce qui en reste à la charge de l'assuré. Le revenu
 * se découpe en tranches comme la paie le découpe, au plafond de l'année ramené
 * aux mois travaillés (article R. 242-2 du code de la sécurité sociale) : le
 * taux est celui du revenu annualisé. Qui n'a pas d'employeur cotise seul, au
 * taux total ; sous la part salariale, le compte ne reçoit que la part de
 * l'assuré.
 *
 * Les attendus sont posés à la main, sur des taux qui s'écrivent juste en
 * binaire : un quart, un huitième, un seizième, un trente-deuxième.
 *
 *     node --test tests/js/bareme-regime-unique.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { tauxDuBareme } from "../../moteur/js/compte.js";
import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { Fiabilite } from "../../moteur/js/serie.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));

//: Un quart jusqu'au plafond, un huitième jusqu'à huit plafonds, un seizième
//: au-delà ; l'assuré en paie la moitié, tranche par tranche.
const TROIS_TRANCHES = [[1.0, 0.25, 0.125], [8.0, 0.125, 0.0625], [null, 0.0625, 0.03125]];
//: Un quart, sans plafond, dont un huitième à la charge de l'assuré.
const DEPLAFONNE = [[null, 0.25, 0.125]];
const ANNEE = 2030;

const simulateurs = new Map();

/** Le simulateur sous le barème `bareme` ; `null`, celui du modèle. */
function sous(bareme) {
  const cle = JSON.stringify(bareme);
  if (!simulateurs.has(cle)) {
    simulateurs.set(cle, new Simulateur(paquet, { ...PARAMETRES_DEFAUT, bareme_regime_unique: bareme }));
  }
  return simulateurs.get(cle);
}

/** Deux nombres égaux au dernier bit près : les tranches s'additionnent. */
function proche(lu, attendu, message) {
  assert.ok(Math.abs(lu - attendu) <= 1e-15, `${message} : ${lu} au lieu de ${attendu}`);
}

/** Une activité de l'année `ANNEE`, cotisée, sous le statut `affiliation`. */
function ligne(affiliation, revenu, fractionAnnee = 1.0) {
  return {
    annee: ANNEE, affiliation, revenu, fraction_annee: fractionAnnee, cotise: true,
    revenu_reference: 0.0, familles_financees: [],
  };
}

/** Ce que le régime unique prélève sur `activite`, au compte salarial (scénarios 2
 *  et 3) et au compte total (scénarios 4 et 5) : taux et part de l'employeur. */
function taux(bareme, activite) {
  const simulateur = sous(bareme);
  const lire = (constructeur) => constructeur.tauxUnifie(activite, ANNEE, simulateur.regimeFusionne);
  return { salariale: lire(simulateur.constructeur), totale: lire(simulateur.constructeurEmployeur) };
}

test("le défaut garde le taux du régime fusionné : le barème est facultatif", () => {
  assert.equal(PARAMETRES_DEFAUT.bareme_regime_unique, null);
  const fusionne = sous(null).regimeFusionne;
  const pass = sous(null).macro.plafond_securite_sociale.valeur(ANNEE);
  const lus = taux(null, ligne("salarie_prive_non_cadre", 2 * pass));
  assert.deepEqual(lus.salariale, [fusionne.taux_cotisation_salarie, 0.0, "", Fiabilite.CERTIFIEE]);
  assert.deepEqual(lus.totale, [fusionne.taux_cotisation_retraite,
    fusionne.taux_cotisation_retraite - fusionne.taux_cotisation_salarie, "", Fiabilite.CERTIFIEE]);
});

test("le revenu se découpe aux bornes des tranches, en plafonds de l'année", () => {
  const pass = 40_000;
  // Un demi-plafond : la première tranche seule.
  assert.deepEqual(tauxDuBareme(TROIS_TRANCHES, 20_000, pass), [0.25, 0.125]);
  // Deux plafonds : un plafond au quart, un au huitième — 15 000 € sur 80 000.
  assert.deepEqual(tauxDuBareme(TROIS_TRANCHES, 80_000, pass), [0.1875, 0.09375]);
  // Dix plafonds : 10 000 + 35 000 + 5 000 € sur 400 000.
  assert.deepEqual(tauxDuBareme(TROIS_TRANCHES, 400_000, pass), [0.125, 0.0625]);
  // Sans revenu, rien.
  assert.deepEqual(tauxDuBareme(TROIS_TRANCHES, 0.0, pass), [0.0, 0.0]);
});

test("sous un barème, le salarié cotise au taux de son revenu, l'employeur payant le reste", () => {
  const pass = sous(TROIS_TRANCHES).macro.plafond_securite_sociale.valeur(ANNEE);
  const lus = taux(TROIS_TRANCHES, ligne("salarie_prive_non_cadre", 2 * pass));
  proche(lus.totale[0], 0.1875, "taux total, deux plafonds");
  proche(lus.totale[1], 0.09375, "part de l'employeur, deux plafonds");
  assert.deepEqual(lus.totale.slice(2), ["", Fiabilite.CERTIFIEE]);
  proche(lus.salariale[0], 0.09375, "part salariale seule, deux plafonds");
  assert.equal(lus.salariale[1], 0.0);
});

test("une année incomplète se découpe au plafond ramené aux mois travaillés", () => {
  const pass = sous(TROIS_TRANCHES).macro.plafond_securite_sociale.valeur(ANNEE);
  // Un plafond gagné en six mois : deux plafonds sur l'année.
  const lus = taux(TROIS_TRANCHES, ligne("salarie_prive_non_cadre", pass, 0.5));
  proche(lus.totale[0], 0.1875, "taux total, six mois à deux plafonds");
  proche(lus.salariale[0], 0.09375, "part salariale, six mois à deux plafonds");
});

test("qui n'a pas d'employeur n'en gagne pas : l'artisan cotise seul, au taux total", () => {
  const pass = sous(TROIS_TRANCHES).macro.plafond_securite_sociale.valeur(ANNEE);
  const lus = taux(TROIS_TRANCHES, ligne("artisan", 2 * pass));
  proche(lus.totale[0], 0.1875, "taux total de l'artisan");
  assert.equal(lus.totale[1], 0.0);
  proche(lus.salariale[0], 0.1875, "l'artisan sous la part salariale");
  assert.equal(lus.salariale[1], 0.0);
});

test("le barème ne touche que le régime unique : ni les années d'avant la bascule, ni le taux uniforme du scénario 6", () => {
  const options = {
    sexe: "F", annee_naissance: 1975, affiliation: "salarie_prive_non_cadre",
    age_debut: 22, age_liquidation: 64, niveau_salaire: 1.0,
  };
  const lire = (bareme) => {
    const simulateur = sous(bareme);
    return simulateur.simuler(simulateur.carriereSimple(options));
  };
  const avec = lire(DEPLAFONNE);
  const sans = lire(null);
  const bascule = PARAMETRES_DEFAUT.annee_bascule;
  for (const [scenario, part] of [["notionnel_retroactif_employeur", 0.25], ["notionnel_retroactif", 0.125]]) {
    const lignes = avec[scenario].compte.cotisations;
    const reference = sans[scenario].compte.cotisations;
    assert.deepEqual(lignes.filter((l) => l.annee < bascule), reference.filter((l) => l.annee < bascule));
    const apres = lignes.filter((l) => l.annee >= bascule && l.assiette_retenue > 0);
    assert.ok(apres.length > 0, scenario);
    for (const l of apres) {
      assert.equal(l.taux_effectif, part, `${scenario}, ${l.annee}`);
      assert.equal(l.cotisation, l.assiette_retenue * part, `${scenario}, ${l.annee}`);
    }
  }
  assert.deepEqual(avec.notionnel_liberal.compte.cotisations, sans.notionnel_liberal.compte.cotisations);
});

test("un barème mal formé arrête le simulateur", () => {
  for (const bareme of [
    [],
    [[2.0, 0.25, 0.125], [1.0, 0.125, 0.0625]],
    [[null, 0.25, 0.125], [8.0, 0.125, 0.0625]],
    [[1.0, 0.25]],
    [[null, 0.125, 0.25]],
  ]) {
    assert.throws(() => sous(bareme), RangeError, JSON.stringify(bareme));
  }
});
