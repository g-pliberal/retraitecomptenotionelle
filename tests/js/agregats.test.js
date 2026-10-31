/**
 * La table des agrégats lue par son seul lecteur, `moteur/js/agregats.js`.
 *
 * Le lecteur Python de la table s'en va (note de décision 0005) : le portage
 * la lit seul. La relecture du 23 octobre 2026
 * (`docs/feuille_de_route/161/2026-10-23-etape-6-premiere-partie-la-saisie-par-le-pont.md`)
 * avait relevé où les deux lecteurs différaient, de refus et de forme : chaque
 * écart se tranche ici, par la promesse que l'en-tête du lecteur fait aux
 * pages — il rend ce que la table porte, et lève une erreur sur ce qu'elle ne
 * porte pas, une page qui lirait un zéro ou `undefined` à la place se trompant
 * sans bruit. La table est celle que la fabrique écrit
 * (`data/derive/agregats.json`) ; un cas qu'elle ne porte pas s'y fabrique
 * sur une copie.
 *
 *     node --test tests/js/*.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { CoutFige, chargerAgregats } from "../../moteur/js/agregats.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const BRUT = JSON.parse(readFileSync(join(RACINE, "data/derive/agregats.json"), "utf8"));
const TABLE = chargerAgregats(BRUT);
const ABSENT = /absent de la table figée/;

test("une année de la dette refuse un système qu'elle ne porte pas", () => {
  const dette = TABLE.cout.dette;
  const ligne = dette.annee(dette.derniereAnnee);
  assert.equal(typeof ligne.stock("actuel"), "number");
  for (const lecture of [
    () => ligne.stock("notionnel_bascule"),
    () => ligne.interet("notionnel_bascule"),
    () => ligne.solde("notionnel_bascule"),
    () => dette.dettePublique("notionnel_bascule", dette.derniereAnnee),
  ]) {
    assert.throws(lecture, ABSENT);
  }
});

test("une ligne refuse le champ qu'elle ne porte pas", () => {
  // Le solde dérivé ne porte que son coefficient et son solde.
  const derive = TABLE.cout.soldeDerive.annee(2030);
  assert.throws(() => derive.ressourcesMeur(), ABSENT);
  assert.equal(TABLE.cout.solde.annee(2030).ressourcesMeur(),
    BRUT.cout.solde.annees.find((ligne) => ligne.annee === 2030).ressources_meur);
  // La même lecture, de chaque accesseur qui rend un champ de sa ligne.
  const brut = structuredClone(BRUT.cout);
  delete brut.cumul_observe;
  delete brut.avenir.cumul_reprises;
  for (const champ of ["reprises_constants", "reprises", "part_pib_reprises",
    "garantie_nette_constants"]) {
    delete brut.avenir.annees[0][champ];
  }
  const cout = new CoutFige(brut);
  const premiere = cout.avenir.annees[0];
  for (const lecture of [
    () => cout.cumulObserve(),
    () => cout.avenir.cumulReprises(),
    () => premiere.reprisesConstants(),
    () => premiere.reprises(),
    () => premiere.partPibReprises(),
    () => premiere.garantieNetteConstants(),
  ]) {
    assert.throws(lecture, ABSENT);
  }
});

test("une table vide n'a ni première ni dernière année", () => {
  const brut = structuredClone(BRUT.cout);
  for (const partie of [brut, brut.solde, brut.avenir, brut.dette]) partie.annees = [];
  const cout = new CoutFige(brut);
  for (const partie of [cout, cout.solde, cout.avenir, cout.dette]) {
    assert.throws(() => partie.premiereAnnee, /vide/);
    assert.throws(() => partie.derniereAnnee, /vide/);
  }
  assert.equal(TABLE.cout.solde.premiereAnnee, BRUT.cout.solde.annees[0].annee);
  assert.equal(TABLE.cout.dette.derniereAnnee, BRUT.cout.dette.annees.at(-1).annee);
});

test("la dette au taux décalé se lit sous la clé que la fabrique écrit", () => {
  // `figer_cout` écrit chaque écart sous `repr(float(ecart))` : le Python
  // donne ces clés-ci.
  const cles = {
    "1.0": 1, "-2.0": -2, "1e-05": 1e-5, "1.5e-05": 1.5e-5, "2.5e-07": 2.5e-7,
    "0.0001": 0.0001, "0.01": 0.01, "-0.01": -0.01, "123.5": 123.5,
    "1000000000000000.0": 1e15, "1e+16": 1e16, "1e+100": 1e100,
  };
  const brut = structuredClone(BRUT.cout);
  brut.dettes_decalees = Object.fromEntries(Object.keys(cles).map(
    (cle, rang) => [cle, { actuel: rang }]));
  const cout = new CoutFige(brut);
  for (const [cle, ecart] of Object.entries(cles)) {
    assert.equal(cout.detteDecalee(ecart).horizon("actuel"),
      brut.dettes_decalees[cle].actuel, cle);
  }
  assert.throws(() => cout.detteDecalee(0.02), ABSENT);
});

test("une génération ou une année se demande en nombre, comme la table la porte", () => {
  const cas = TABLE.casTypes.cas[0];
  assert.equal(cas.ageLiquidation(1960), BRUT.cas_types.cas[0].ages[2]);
  const leviers = TABLE.leviers;
  const annee = leviers.annees[0];
  const fin = leviers.horizons[0];
  const variantes = TABLE.esperanceVie;
  const depuis = TABLE.cout.avenir.premiereAnneeProjetee;
  for (const lecture of [
    () => cas.ageLiquidation("1960"),
    () => TABLE.classement.departs("1960"),
    () => leviers.annee("actuel", String(annee)),
    () => leviers.vise("actuel", leviers.soldesVises[0], String(leviers.anneesVisees[0])),
    () => leviers.horizon("actuel", String(fin)),
    () => variantes.partPib("centrale", "actuel", String(variantes.annees[0])),
    () => TABLE.cout.avenir.decomposition(String(depuis)),
  ]) {
    assert.throws(lecture, ABSENT);
  }
  assert.equal(TABLE.classement.departs(1960).length, 2);
});

test("la table ne rend de zéro que celui qu'elle porte", () => {
  const dette = TABLE.cout.dette;
  // Le stock est nul jusqu'à l'année de départ : la table le porte par elle.
  assert.equal(dette.stock("actuel", dette.anneeDepart), 0);
  assert.equal(dette.stock("actuel", dette.anneeDepart - 10), 0);
  assert.equal(dette.dettePublique("actuel", dette.anneeDepart), dette.dettePubliqueDepart);
  // Au-delà de sa dernière année, elle ne porte rien.
  assert.throws(() => dette.stock("actuel", dette.derniereAnnee + 1), ABSENT);
  assert.throws(() => dette.dettePublique("actuel", dette.derniereAnnee + 1), ABSENT);
  // Ni la moyenne d'une fenêtre où elle n'a aucune année.
  const solde = TABLE.cout.solde;
  assert.throws(() => solde.soldeMoyen("actuel", solde.derniereAnnee + 1,
    solde.derniereAnnee + 10), ABSENT);
  // Ni la dette publique de départ, sans la série de son année.
  const brut = structuredClone(BRUT.cout);
  delete brut.dette.dette_publique_observee[String(brut.dette.annee_dette_publique)];
  assert.throws(() => new CoutFige(brut).dette.dettePubliqueDepart, ABSENT);
});
