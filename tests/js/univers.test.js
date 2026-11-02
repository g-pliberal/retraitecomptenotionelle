/**
 * Les univers de la proposition sur le portage : ce que le moteur calcule d'un
 * univers que la fabrication a résolu (`calculNotionnel`, `calculerUnivers`).
 *
 * La proposition PROSPECTIVE (`scripts/proposition_prospective.py`, action
 * 161) est le scénario 5 à 18 %, le pilier capitalisé et la garantie
 * vieillesse par-dessus : « une retraite déjà liquidée à la bascule ne bouge
 * pas ; un actif voit ses droits d'avant la bascule figés […] ; son compte est
 * alimenté à 18 % ensuite ; le pilier capitalisé et la garantie vieillesse
 * s'ajoutent comme dans le scénario 6, la garantie valant aussi pour le
 * stock ». Son univers n'entre pas au paquet
 * (`data/reference/variantes/`) : le pont le passe dans la demande, son calcul
 * à la place de celui du scénario 6. On le résout ici comme la fabrication le
 * résout, du scénario 6 et de la transition du scénario 5 :
 * `tests/test_univers.py` tient que c'est bien ce que la fabrication en tire.
 *
 *     node --test tests/js/*.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));

const calculDe = (id) => paquet.univers.find((u) => u.id === id).calcul;

/** Le calcul de la proposition prospective : le compte, ses paramètres, le
 *  pilier, la garantie et l'âge légal du scénario 6, sur la transition du
 *  scénario 5 et ce que sa liquidation fictive neutralise. */
const PROSPECTIVE = {
  ...calculDe("notionnel_liberal"),
  univers: "notionnel_liberal_prospectif",
  libelle: "Comptes notionnels à compter de la bascule, 18 % et garantie vieillesse",
  prospectif: true,
  neutralisations: calculDe("notionnel_prospectif_employeur").neutralisations,
};

/** Le simulateur sur le paquet où la proposition prospective tient la place
 *  du scénario 6, comme le pont la lui passe. */
const simulateur = new Simulateur({
  ...paquet,
  univers: paquet.univers.map((u) => (u.id === "notionnel_liberal"
    ? { ...u, calcul: PROSPECTIVE } : u)),
});

test("un compte ouvert à la bascule reçoit le pilier capitalisé, puis la garantie vieillesse", () => {
  const actif = simulateur.carriereSimple({
    annee_naissance: 1985, sexe: "H", affiliation: "salarie_prive_non_cadre",
    age_debut: 22, age_liquidation: 65, niveau_salaire: 1.0,
  });
  const calcul = simulateur.calculs.notionnel_liberal;
  // Le compte ouvert à la bascule, seul, tel que le scénario 5 le calcule,
  // alimenté ici à 18 %.
  const compte = simulateur.scenarioDe(calcul).prospectif(
    actif, simulateur.regimeFusionne, calcul.libelle, calcul.neutralisations);
  const servi = simulateur.calculerUnivers("notionnel_liberal", actif);

  // Les droits d'avant la bascule, figés et convertis en capital ; puis le
  // compte, alimenté à 18 % à compter de la bascule.
  assert.ok(servi.droits_acquis !== null && servi.capital_droits_acquis > 0);
  assert.equal(servi.capital_notionnel, compte.capital_notionnel);
  const apres = servi.compte.cotisations
    .filter((c) => c.annee >= PARAMETRES_DEFAUT.annee_bascule && c.cotisation > 0);
  assert.ok(apres.length > 0);
  for (const cotisation of apres) {
    assert.ok(Math.abs(cotisation.taux_effectif - PARAMETRES_DEFAUT.taux_cotisation_liberal)
      < 1e-12, `${cotisation.annee} : ${cotisation.taux_effectif}`);
  }

  // Le pilier, sur les assiettes du même compte : rien avant la bascule.
  assert.ok(servi.capitalisation !== null && servi.capitalisation.actif);
  assert.equal(Math.min(...servi.capitalisation.annees.map((a) => a.annee)),
    PARAMETRES_DEFAUT.annee_bascule);
  assert.equal(servi.rente_capitalisation_obligatoire, servi.capitalisation.rente_annuelle);
  assert.ok(servi.rente_capitalisation_obligatoire > 0);

  // La garantie regarde les deux étages : la répartition du compte, et la
  // rente du pilier.
  const garantie = servi.garantie_vieillesse;
  assert.ok(garantie !== null);
  assert.equal(garantie.pension_contributive, compte.pension_annuelle);
  assert.equal(garantie.rente_capitalisee, servi.rente_capitalisation_obligatoire);
  assert.equal(servi.pension_annuelle,
    compte.pension_annuelle + (garantie.servie_a_la_liquidation ? garantie.complement : 0.0));
  assert.equal(servi.pension_totale,
    servi.pension_annuelle + servi.rente_capitalisation_obligatoire);
});

test("une pension liquidée avant la bascule ne bouge pas, et la garantie la porte au plancher", () => {
  // Une courte carrière, partie à 65 ans en 2010 : sa pension, le minimum
  // vieillesse compris, est sous le plancher, que la garantie complète dès le
  // départ.
  const retraite = simulateur.carriereSimple({
    annee_naissance: 1945, sexe: "F", affiliation: "salarie_prive_non_cadre",
    age_debut: 50, age_liquidation: 65, niveau_salaire: 0.5,
  });
  const actuel = simulateur.scenarioActuel.calculer(retraite);
  const servi = simulateur.calculerUnivers("notionnel_liberal", retraite);

  // Le plancher d'une personne seule, posé à la main : la garantie de base et
  // l'allocation d'isolement, mensuelles, en euros de 2026, ramenées aux prix
  // de l'année du départ.
  const p = PARAMETRES_DEFAUT;
  const plancher = (p.garantie_vieillesse_mensuelle + p.allocation_isolement_mensuelle) * 12.0
    * simulateur.macro.coefficientPrix(p.annee_euros_garantie_vieillesse, 2010);
  assert.ok(actuel.pension_annuelle < plancher, `${actuel.pension_annuelle} ≥ ${plancher}`);

  const garantie = servi.garantie_vieillesse;
  assert.ok(garantie !== null && garantie.servie_a_la_liquidation);
  assert.equal(garantie.pension_contributive, actuel.pension_annuelle);
  assert.ok(Math.abs(garantie.complement - (plancher - actuel.pension_annuelle)) < 1e-9);
  assert.equal(servi.pension_annuelle, actuel.pension_annuelle + garantie.complement);
  // Aucun versement au pilier : tout a été cotisé avant la bascule.
  assert.equal(servi.rente_capitalisation_obligatoire, 0.0);
});
