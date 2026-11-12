/**
 * Le journal de l'échéancier, contre son contrat (action 161, les lignes du
 * portage qu'aucun test n'exécutait).
 *
 * La source est `docs/architecture.md`, § 7.4 et annexe C.8 : « L'état est un
 * journal : on y ajoute, on n'efface jamais. Chaque entrée porte deux dates :
 * son inscription [...] et sa période d'effet. Deux lectures en découlent :
 * l'état à une date est tout ce qui a été inscrit au plus tard ce jour-là ; ce
 * qui est servi pour une période se lit, pour chaque composante, sur la
 * dernière entrée de sa lignée dont l'effet la couvre. [...] Une composante
 * s'éteint à la fin de son effet, ou par une entrée qui la remplace sans
 * montant. » L'annexe C.8 nomme les champs d'une entrée, et ceux qui manquent
 * par défaut : `remplace`, `annule`.
 *
 * Le moteur du site n'écrit le journal que par l'échéancier et ne le relit
 * que par `servi` et `donnees` : ses refus, l'état à une date, l'entrée par
 * son identifiant et le champ `annule` n'étaient éprouvés que dans le jumeau
 * Python (`tests/test_liquidation.py`), ou nulle part. Chaque attendu se lit
 * dans les phrases citées.
 *
 *     node --test tests/js/journal.test.js
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { Entree, Journal, SCHEMA_VERSION } from "../../moteur/js/journal.js";

/** Une composante inscrite à `date`, d'effet [date, fin). */
const entree = (id, date, { fin = null, remplace = null, montant = 1.0, ...reste } = {}) => new Entree({
  id, evenement: "depart_assure", inscriteLe: date, debut: date, fin, sorte: "composante",
  contenu: montant === null ? { id } : { id, montant: { annuel: montant, monnaie: "EUR" } },
  remplace, ...reste,
});

const ids = (entrees) => [...entrees].map((e) => e.id).sort();

/** Une pension de base révisée deux fois, et une complémentaire bornée. */
function journalRevise() {
  const journal = new Journal();
  journal.inscrire(entree("pension_regime_general", "2020-01-01"));
  journal.inscrire(entree("pension_agirc_arrco", "2020-01-01", { fin: "2030-01-01" }));
  journal.inscrire(entree("pension_regime_general_2024", "2024-12-31",
    { remplace: "pension_regime_general" }));
  journal.inscrire(entree("pension_regime_general_2025", "2025-12-31",
    { remplace: "pension_regime_general_2024" }));
  return journal;
}

test("le journal ne s'écrit qu'en ajoutant : ni deux fois le même identifiant, ni la révision d'une inconnue", () => {
  const journal = new Journal();
  const premiere = entree("pension_regime_general", "2020-01-01");
  assert.equal(journal.inscrire(premiere), premiere);
  assert.throws(() => journal.inscrire(entree("pension_regime_general", "2021-01-01")),
    /entrée déjà inscrite : pension_regime_general/);
  assert.throws(
    () => journal.inscrire(entree("pension_agirc_arrco_2021", "2021-01-01",
      { remplace: "pension_agirc_arrco" })),
    /pension_agirc_arrco_2021 remplace une entrée inconnue : pension_agirc_arrco/);
  // Ce qui est refusé n'est pas inscrit, et ce qui était inscrit le reste.
  assert.equal(journal.length, 1);
  assert.deepEqual([...journal], [premiere]);
  assert.equal(journal.entree("pension_regime_general").inscriteLe, "2020-01-01");
});

test("une entrée inscrite ne se retouche pas", () => {
  const inscrite = entree("pension_regime_general", "2020-01-01");
  assert.throws(() => { inscrite.fin = "2021-01-01"; }, TypeError);
  assert.equal(inscrite.fin, null);
});

test("l'entrée se retrouve par son identifiant, et une inconnue est un refus", () => {
  const journal = journalRevise();
  assert.equal(journal.entree("pension_regime_general_2024").remplace, "pension_regime_general");
  assert.throws(() => journal.entree("pension_cnavpl"), /entrée inconnue : pension_cnavpl/);
});

test("l'état à une date est tout ce qui a été inscrit au plus tard ce jour-là", () => {
  const journal = journalRevise();
  assert.deepEqual(ids(journal.etatAu("2019-12-31")), []);
  assert.deepEqual(ids(journal.etatAu("2024-12-30")),
    ["pension_agirc_arrco", "pension_regime_general"]);
  assert.deepEqual(ids(journal.etatAu("2024-12-31")),
    ["pension_agirc_arrco", "pension_regime_general", "pension_regime_general_2024"]);
  assert.equal(journal.etatAu("2026-01-01").length, journal.length);
});

test("pour une période, chaque lignée sert sa dernière entrée dont l'effet la couvre", () => {
  const journal = journalRevise();
  assert.deepEqual(ids(journal.servi("2021-01-01", "2021-02-01")),
    ["pension_agirc_arrco", "pension_regime_general"]);
  // Entre les deux révisions, la première.
  assert.deepEqual(ids(journal.servi("2025-01-01", "2025-02-01")),
    ["pension_agirc_arrco", "pension_regime_general_2024"]);
  assert.deepEqual(ids(journal.servi("2026-01-01", "2026-02-01")),
    ["pension_agirc_arrco", "pension_regime_general_2025"]);
  // Une composante s'éteint à la fin de son effet : ni la période qui la
  // passe, ni celle qui n'a pas de fin, ne sont couvertes par elle.
  assert.deepEqual(ids(journal.servi("2029-12-01", "2030-01-01")),
    ["pension_agirc_arrco", "pension_regime_general_2025"]);
  assert.deepEqual(ids(journal.servi("2029-01-01", "2031-01-01")), ["pension_regime_general_2025"]);
  assert.deepEqual(ids(journal.servi("2026-01-01")), ["pension_regime_general_2025"]);
  // Avant le premier effet, rien n'est servi.
  assert.deepEqual(ids(journal.servi("2019-12-01", "2020-01-01")), []);
});

test("une entrée sans montant éteint sa composante : c'est elle que le journal sert", () => {
  const journal = journalRevise();
  journal.inscrire(entree("pension_regime_general_suspendue", "2027-06-01",
    { remplace: "pension_regime_general_2025", montant: null }));
  const servies = journal.servi("2027-07-01", "2027-08-01");
  assert.deepEqual(ids(servies), ["pension_agirc_arrco", "pension_regime_general_suspendue"]);
  assert.ok(!("montant" in servies.find((e) => e.remplace !== null).contenu));
  // La suspension ne vaut que de son effet : le mois d'avant garde la pension.
  assert.deepEqual(ids(journal.servi("2027-05-01", "2027-06-01")),
    ["pension_agirc_arrco", "pension_regime_general_2025"]);
});

test("ce qui est servi se lit sorte par sorte", () => {
  const journal = journalRevise();
  journal.inscrire(new Entree({
    id: "depart", evenement: "depart_assure", inscriteLe: "2020-01-01", debut: "2020-01-01",
    sorte: "evenement", contenu: { sorte: "depart" },
  }));
  assert.deepEqual(ids(journal.servi("2021-01-01", "2021-02-01", "evenement")), ["depart"]);
  assert.deepEqual(ids(journal.servi("2021-01-01", "2021-02-01", "composante")),
    ["pension_agirc_arrco", "pension_regime_general"]);
});

test("une entrée s'écrit comme l'annexe C.8 la décrit, sans les champs qui manquent par défaut", () => {
  const simple = entree("pension_regime_general", "2020-01-01", { fin: "2030-01-01" });
  assert.deepEqual(simple.donnees(), {
    schema_version: SCHEMA_VERSION,
    id: "pension_regime_general",
    inscrite: { evenement: "depart_assure", date: "2020-01-01" },
    effet: ["2020-01-01", "2030-01-01"],
    contenu: {
      sorte: "composante",
      donnee: { id: "pension_regime_general", montant: { annuel: 1.0, monnaie: "EUR" } },
    },
  });
  assert.equal(SCHEMA_VERSION, 1);
  const revisee = entree("pension_regime_general_2024", "2024-12-31",
    { remplace: "pension_regime_general" });
  assert.equal(revisee.donnees().remplace, "pension_regime_general");
  assert.ok(!("annule" in revisee.donnees()));
  // L'entrée qui annule un événement en attente le nomme.
  const annulation = new Entree({
    id: "annulation_inaptitude", evenement: "reprise_d_activite", inscriteLe: "2031-03-01",
    debut: "2031-03-01", sorte: "decision", contenu: { motif: "reprise" },
    annule: "substitution_inaptitude",
  });
  assert.equal(annulation.donnees().annule, "substitution_inaptitude");
  assert.ok(!("remplace" in annulation.donnees()));
  assert.deepEqual(annulation.donnees().effet, ["2031-03-01", null]);
});

test("le contenu qui a son propre contrat s'écrit par lui, et le journal dans l'ordre des inscriptions", () => {
  const journal = new Journal();
  journal.inscrire(new Entree({
    id: "liquidation", evenement: "depart_assure", inscriteLe: "2020-01-01", debut: "2020-01-01",
    sorte: "liquidation", contenu: { donnees: () => ({ schema_version: 7, pensions: [] }) },
  }));
  journal.inscrire(entree("pension_regime_general", "2020-01-01"));
  const ecrit = journal.donnees();
  assert.deepEqual(ecrit.map((e) => e.id), ["liquidation", "pension_regime_general"]);
  assert.deepEqual(ecrit[0].contenu, {
    sorte: "liquidation", donnee: { schema_version: 7, pensions: [] },
  });
});
