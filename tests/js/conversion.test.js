/**
 * La conversion du capital notionnel en rente (action 161, quatrième vague) :
 * ce que `tests/test_moteur.py` éprouvait sur `Convertisseur` et
 * `DonneesMortalite` du moteur Python, éprouvé sur ceux du site.
 *
 * Aucune valeur attendue ne vient du moteur : chaque test dit un sens de
 * variation du diviseur — avec l'âge, le mois, le taux anticipé, la table, la
 * population, l'hypothèse d'espérance de vie —, une identité de la règle, ou
 * un écart d'espérance de vie que les tables publiées imposent.
 *
 *     node --test tests/js/conversion.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { PARAMETRES_DEFAUT, TableConversion, avec } from "../../moteur/js/config.js";
import { Contexte } from "../../moteur/js/contexte.js";
import { Convertisseur } from "../../moteur/js/conversion.js";
import { DonneesMortalite } from "../../moteur/js/mortalite.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur", "donnees.json"), "utf8"));
const mortalite = new DonneesMortalite(paquet);

/** Le convertisseur sous les réglages de référence, retouchés de `modifications`. */
const convertisseur = (modifications = {}, donnees = mortalite) => new Convertisseur(
  donnees, avec(PARAMETRES_DEFAUT, modifications));

/** Comme `pytest.approx` : 10⁻⁶ relatif par défaut. */
const proche = (lu, attendu, { relatif = 1e-6, absolu = 1e-12 } = {}, message = "") => assert.ok(
  Math.abs(lu - attendu) <= Math.max(absolu, relatif * Math.abs(attendu)),
  `${message}${lu} au lieu de ${attendu}`);

const ecartsSuccessifs = (valeurs) => valeurs.slice(1).map((apres, i) => valeurs[i] - apres);

// -- l'âge, le taux anticipé -----------------------------------------------------

test("le diviseur décroît avec l'âge de liquidation", () => {
  const regle = convertisseur();
  let precedent = null;
  for (const age of [55, 60, 62, 64, 67, 70]) {
    const { diviseur } = regle.coefficient(age, 2026);
    if (precedent !== null) {
      assert.ok(diviseur < precedent, `le diviseur ne baisse pas à ${age} ans`);
    }
    precedent = diviseur;
  }
});

test("l'anticipation réduit la pension sans décote administrative", () => {
  // La sanction du départ anticipé est produite par le seul diviseur : cinq
  // ans d'anticipation coûtent de l'ordre de 15 % de pension annuelle, avant
  // même de compter les cotisations non versées.
  const rapport = convertisseur().effetAnticipation(59.0, 64.0, 2026);
  assert.ok(rapport < 1.0);
  assert.ok(rapport > 0.75 && rapport < 0.92, String(rapport));
});

test("à taux anticipé nul, le diviseur vaut l'espérance de vie résiduelle", () => {
  const coefficient = convertisseur({ taux_anticipe_conversion: 0.0 }).coefficient(64, 2026);
  proche(coefficient.diviseur, coefficient.esperance_residuelle);
});

test("un taux anticipé positif réduit le diviseur", () => {
  const sans = convertisseur().coefficient(64, 2026);
  const avecTaux = convertisseur({ taux_anticipe_conversion: 0.015 }).coefficient(64, 2026);
  assert.ok(avecTaux.diviseur < sans.diviseur);
});

// -- la table : par sexe, par population ---------------------------------------

test("la table par sexe pénalise les femmes", () => {
  // Justification du choix unisexe par défaut : l'écart est loin d'être marginal.
  const regle = convertisseur({ table_conversion: TableConversion.PAR_SEXE });
  const homme = regle.coefficient(64, 2026, "H").diviseur;
  const femme = regle.coefficient(64, 2026, "F").diviseur;
  assert.ok(femme > homme);
  assert.ok(femme / homme - 1 > 0.05);
});

test("la table par sexe exige le sexe", () => {
  const regle = convertisseur({ table_conversion: TableConversion.PAR_SEXE });
  assert.throws(() => regle.coefficient(64, 2026, null), /sexe non renseigné/);
});

test("la table d'une population allonge le diviseur", () => {
  // Ce que le diviseur commun transfère (action 14) : à 64 ans, un
  // fonctionnaire civil de l'État a entre un et deux ans de rente de plus que
  // la population générale, et une table qui le saurait lui servirait 4 à 8 %
  // de moins par an à capital égal. La table commune reste le défaut.
  const commun = convertisseur().coefficient(64, 2026);
  const corrige = convertisseur({ population_conversion: "fonctionnaires_civils_etat" })
    .coefficient(64, 2026);
  const ecart = corrige.esperance_residuelle - commun.esperance_residuelle;
  assert.ok(ecart > 1.0 && ecart < 2.0, String(ecart));
  const rapport = corrige.diviseur / commun.diviseur - 1;
  assert.ok(rapport > 0.04 && rapport < 0.08, String(rapport));
  assert.equal(commun.table, "unisexe_generation");
  assert.equal(corrige.table, "unisexe_generation_fonctionnaires_civils_etat");
});

test("le diviseur commun transfère des modestes vers les aisés", () => {
  // À 64 ans en 2026, la table des 5 % les plus modestes donne trois ans de
  // rente de MOINS que la table commune, celle des 5 % les plus aisés trois
  // ans de PLUS.
  const commun = convertisseur().coefficient(64, 2026);
  const modeste = convertisseur({ population_conversion: "niveau_de_vie_v01" }).coefficient(64, 2026);
  const aise = convertisseur({ population_conversion: "niveau_de_vie_v20" }).coefficient(64, 2026);
  const moins = modeste.esperance_residuelle - commun.esperance_residuelle;
  const plus = aise.esperance_residuelle - commun.esperance_residuelle;
  assert.ok(moins > -4.5 && moins < -2.0, String(moins));
  assert.ok(plus > 2.0 && plus < 4.5, String(plus));
  assert.ok(modeste.diviseur < commun.diviseur && commun.diviseur < aise.diviseur);
});

// -- le mois de départ ---------------------------------------------------------

test("le diviseur ne fait plus de marche à l'anniversaire", () => {
  // La force de mortalité étant supposée constante entre deux âges entiers, la
  // décroissance est lisse : en 2005, où les quotients observés couvrent la
  // première moitié de la courbe, aucun pas ne pèse plus du double du plus
  // petit, et le douzième mois retombe sur l'âge entier suivant.
  const regle = convertisseur();
  const diviseurs = Array.from({ length: 13 },
    (_, m) => regle.coefficient(60 + m / 12, 2005, "H").diviseur);
  const ecarts = ecartsSuccessifs(diviseurs);
  assert.deepEqual(diviseurs, [...diviseurs].sort((a, b) => b - a));
  assert.ok(Math.max(...ecarts) < 2 * Math.min(...ecarts), String(ecarts));
  proche(diviseurs[12], regle.coefficient(61.0, 2005, "H").diviseur);
});

test("le diviseur décroît aussi au passage du 1er janvier", () => {
  // Le millésime de la table ne saute pas quand l'âge, lui, glisse : sur
  // vingt-quatre mois à cheval sur deux 1er janvier, chaque mois de plus
  // baisse le diviseur, le pas de janvier comme les autres.
  const regle = convertisseur();
  const diviseurs = Array.from({ length: 25 },
    (_, k) => regle.coefficient(62 + k / 12, 2037 + Math.trunc(k / 12), "H", (k % 12) + 1).diviseur);
  const ecarts = ecartsSuccessifs(diviseurs);
  assert.ok(ecarts.every((ecart) => ecart > 0), String(diviseurs));
  assert.ok(Math.max(...ecarts) < 2 * Math.min(...ecarts), String(ecarts));
  proche(diviseurs[12], regle.coefficient(63.0, 2038, "H", 1).diviseur);
});

// -- l'hypothèse d'espérance de vie --------------------------------------------

const HYPOTHESES = ["basse", "centrale", "haute"];

test("le diviseur absorbe l'hypothèse d'espérance de vie", () => {
  // Sous les hypothèses basse et haute de l'INSEE, le diviseur de qui part
  // après 2026 encadre celui de la centrale, d'autant plus largement que la
  // génération est jeune ; une génération partie en 1950 a le même sous les
  // trois, l'observé ne dépendant d'aucune hypothèse (action 138, étape 7).
  const regles = HYPOTHESES.map((hypothese) => convertisseur(
    { population_conversion: null }, new DonneesMortalite(paquet, undefined, hypothese)));
  const diviseurs = (age, annee) => regles.map((regle) => regle.coefficient(age, annee).diviseur);

  assert.equal(new Set(diviseurs(65, 1950)).size, 1);
  const largeurs = [];
  for (const generation of [1960, 1975, 2000]) {
    const [basse, centrale, haute] = diviseurs(64, generation + 64);
    assert.ok(basse < centrale && centrale < haute, String(generation));
    largeurs.push((haute - basse) / centrale);
  }
  assert.deepEqual(largeurs, [...largeurs].sort((a, b) => a - b));
});

test("l'hypothèse d'espérance de vie ne touche pas au capital rétroactif", () => {
  // Le scénario 1, où nulle espérance de vie n'entre, sert la même pension ;
  // le compte rétroactif garde le même capital, et sa pension en est le
  // quotient par le diviseur de chaque hypothèse.
  const contexte = new Contexte(paquet);
  const resultats = {};
  for (const hypothese of HYPOTHESES) {
    const simulateur = contexte.simulateur(
      avec(PARAMETRES_DEFAUT, { hypothese_esperance_vie: hypothese }));
    const carriere = simulateur.carriereSimple({
      annee_naissance: 1975, sexe: "F", affiliation: "salarie_prive_non_cadre",
      age_debut: 22, age_liquidation: 64,
    });
    resultats[hypothese] = simulateur.simuler(carriere).dictionnaire();
  }
  const valeurs = Object.values(resultats);
  assert.equal(new Set(valeurs.map((r) => r.scenarios.actuel.pension_annuelle)).size, 1);
  assert.equal(new Set(valeurs.map(
    (r) => r.scenarios.notionnel_retroactif.capital_notionnel)).size, 1);
  for (const [hypothese, resultat] of Object.entries(resultats)) {
    const retroactif = resultat.scenarios.notionnel_retroactif;
    assert.equal(resultat.unite.hypothese_esperance_vie, hypothese);
    proche(retroactif.pension_annuelle, retroactif.capital_notionnel / resultat.conversion.diviseur);
  }
  const pensions = HYPOTHESES.map((h) => resultats[h].scenarios.notionnel_retroactif.pension_annuelle);
  assert.deepEqual(pensions, [...pensions].sort((a, b) => b - a));
  assert.equal(new Set(pensions).size, 3);
});
