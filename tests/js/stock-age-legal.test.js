/**
 * Le stock à l'âge légal (`stock_age_legal`, action 161) : la parade que
 * `scripts/stock_age_legal.py` chiffre au grief d'une pension déjà liquidée
 * que le compte rétroactif ferait payer de l'âge de son départ, quand cet âge
 * était celui que sa loi lui ouvrait. Le défaut, `null`, ne touche rien.
 *
 * - `droit_commun` : dans les scénarios rétroactifs, une pension liquidée
 *   avant la bascule, à l'âge légal de la génération ou après, mais avant
 *   l'âge de référence, se divise au diviseur de l'âge de référence ;
 * - `tout_droit` : de même, l'âge légal étant celui que le droit de l'assuré
 *   lui ouvrait, régime spécial et carrière longue compris
 *   (`ageOuvertureDroit`) ;
 * - `acquis` : dans les scénarios prospectifs, les droits acquis à la bascule
 *   se convertissent à l'âge légal de la génération quand il est plus bas que
 *   l'âge de référence.
 *
 * Les âges viennent des textes : soixante ans pour la génération 1950,
 * soixante-deux pour 1960, soixante-quatre pour 1970
 * (`age_ouverture_requis.csv`, D. 161-2-1-9) ; cinquante ans pour un agent de
 * conduite de la SNCF parti avant 2017 ; soixante-cinq, l'âge de référence de
 * la proposition (`age_reference_fixe`). La pension attendue est le capital du
 * compte, que la règle ne touche pas, divisé au diviseur de l'âge de
 * référence, que le convertisseur donne.
 *
 *     node --test tests/js/stock-age-legal.test.js
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

const RETROACTIFS = ["notionnel_retroactif", "notionnel_retroactif_employeur", "notionnel_liberal"];
const PROSPECTIFS = ["notionnel_prospectif", "notionnel_prospectif_employeur"];
//: L'âge de référence de la proposition, depuis le 22 septembre 2026.
const AGE_DE_REFERENCE = 65;

const simulateurs = new Map();

/** Le simulateur sous la règle `regle` du stock ; `null`, celui du modèle. */
function sous(regle) {
  if (!simulateurs.has(regle)) {
    simulateurs.set(regle, new Simulateur(paquet, { ...PARAMETRES_DEFAUT, stock_age_legal: regle }));
  }
  return simulateurs.get(regle);
}

/** La carrière d'un seul statut de `options`, au salaire moyen. */
function carriere(simulateur, options) {
  return simulateur.carriereSimple({ sexe: "H", niveau_salaire: 1.0, ...options });
}

/** Ce que le simulateur sous `regle` sert à la carrière de `options`. */
function simuler(regle, options) {
  return sous(regle).simuler(carriere(sous(regle), options));
}

/** Le diviseur de l'âge de référence, à la date où la carrière liquide. */
function diviseurDeReference(simulateur, liquidee) {
  return simulateur.convertisseur.coefficient(
    AGE_DE_REFERENCE, liquidee.anneeLiquidation, null, liquidee.moisLiquidation,
    simulateur.convertisseur.populationDe(liquidee)).diviseur;
}

test("le défaut ne convertit rien : la règle du stock est facultative", () => {
  assert.equal(PARAMETRES_DEFAUT.stock_age_legal, null);
  assert.equal(PARAMETRES_DEFAUT.age_reference_fixe, AGE_DE_REFERENCE);
});

test("droit_commun : parti à l'âge légal de sa génération avant la bascule, le retraité est divisé au diviseur de l'âge de référence", () => {
  // Né en 1950, parti à soixante ans en 2010 : l'âge légal de sa génération.
  const options = {
    annee_naissance: 1950, affiliation: "salarie_prive_non_cadre", age_debut: 20, age_liquidation: 60,
  };
  const droit = simuler(null, options);
  const simulateur = sous("droit_commun");
  const liquidee = carriere(simulateur, options);
  const converti = simulateur.simuler(liquidee);
  const diviseur = diviseurDeReference(simulateur, liquidee);
  for (const scenario of RETROACTIFS) {
    const lu = converti[scenario];
    assert.equal(lu.capital_notionnel, droit[scenario].capital_notionnel, scenario);
    assert.equal(droit[scenario].conversion.age_liquidation, 60, scenario);
    assert.equal(lu.conversion.age_liquidation, AGE_DE_REFERENCE, scenario);
    assert.equal(lu.conversion.diviseur, diviseur, scenario);
    assert.ok(lu.pension_annuelle > droit[scenario].pension_annuelle, scenario);
  }
  for (const scenario of ["notionnel_retroactif", "notionnel_retroactif_employeur"]) {
    assert.equal(converti[scenario].pension_annuelle,
      converti[scenario].capital_notionnel / diviseur, scenario);
  }
  // La proposition divise le même compte, et sa garantie ne s'y ajoute pas ici.
  const liberal = converti.notionnel_liberal;
  assert.equal(liberal.garantie_vieillesse.servie_a_la_liquidation, false);
  assert.equal(liberal.pension_annuelle, liberal.capital_notionnel / diviseur);
  // Le système actuel, et les prospectifs, qui lui gardent sa pension, ne bougent pas.
  for (const scenario of ["actuel", ...PROSPECTIFS]) {
    assert.equal(converti[scenario].pension_annuelle, droit[scenario].pension_annuelle, scenario);
  }
});

test("droit_commun : parti avant l'âge légal de sa génération, il garde le diviseur de son âge ; tout_droit lui compte l'âge que son régime lui ouvrait", () => {
  // Un agent de conduite de la SNCF né en 1960, parti à cinquante-deux ans en
  // 2012 : son régime lui ouvrait la retraite à cinquante ans, le régime
  // général à soixante-deux.
  const options = { annee_naissance: 1960, affiliation: "agent_sncf", age_debut: 20, age_liquidation: 52 };
  const droit = simuler(null, options);
  const commun = simuler("droit_commun", options);
  const simulateur = sous("tout_droit");
  const liquidee = carriere(simulateur, options);
  const tout = simulateur.simuler(liquidee);
  const diviseur = diviseurDeReference(simulateur, liquidee);
  for (const scenario of RETROACTIFS) {
    assert.equal(commun[scenario].pension_annuelle, droit[scenario].pension_annuelle, scenario);
    assert.equal(commun[scenario].conversion.age_liquidation, 52, scenario);
    assert.equal(tout[scenario].conversion.age_liquidation, AGE_DE_REFERENCE, scenario);
    assert.ok(tout[scenario].pension_annuelle > droit[scenario].pension_annuelle, scenario);
  }
  for (const scenario of ["notionnel_retroactif", "notionnel_retroactif_employeur"]) {
    assert.equal(tout[scenario].pension_annuelle, tout[scenario].capital_notionnel / diviseur, scenario);
  }
});

test("après la bascule, ou à l'âge de référence et au-delà, la règle du stock ne touche rien", () => {
  for (const options of [
    // Parti à soixante-quatre ans en 2034 : la règle est connue avant le choix.
    { annee_naissance: 1970, affiliation: "salarie_prive_non_cadre", age_debut: 22, age_liquidation: 64 },
    // Parti à soixante-six ans en 2011 : son âge passe déjà celui de référence.
    { annee_naissance: 1945, affiliation: "salarie_prive_non_cadre", age_debut: 20, age_liquidation: 66 },
  ]) {
    const droit = simuler(null, options);
    for (const regle of ["droit_commun", "tout_droit"]) {
      const lu = simuler(regle, options);
      for (const scenario of [...RETROACTIFS, ...PROSPECTIFS]) {
        assert.equal(lu[scenario].pension_annuelle, droit[scenario].pension_annuelle,
          `${options.annee_naissance} ${regle} ${scenario}`);
      }
    }
  }
});

test("acquis : les droits acquis d'un actif se convertissent à l'âge légal de sa génération, plus bas que l'âge de référence", () => {
  // Né en 1970, parti à soixante-quatre ans en 2034 : l'âge légal de sa génération.
  const options = {
    annee_naissance: 1970, affiliation: "salarie_prive_non_cadre", age_debut: 22, age_liquidation: 64,
  };
  const droit = simuler(null, options);
  const simulateur = sous("acquis");
  const liquidee = carriere(simulateur, options);
  const lu = simulateur.simuler(liquidee);
  const bascule = PARAMETRES_DEFAUT.annee_bascule;
  for (const scenario of PROSPECTIFS) {
    const avant = droit[scenario].droits_acquis;
    const apres = lu[scenario].droits_acquis;
    assert.equal(avant.age_conversion, AGE_DE_REFERENCE, scenario);
    assert.equal(apres.age_conversion, 64, scenario);
    assert.equal(apres.pension_figee, avant.pension_figee, scenario);
    const conversion = simulateur.convertisseur.coefficient(64, bascule, null, 1,
      simulateur.convertisseur.populationPourPension(apres.pension_figee, bascule, liquidee));
    assert.equal(apres.diviseur, conversion.diviseur, scenario);
    assert.equal(apres.capital_a_la_bascule, apres.pension_figee * conversion.diviseur, scenario);
    assert.equal(apres.capital, apres.capital_a_la_bascule * apres.coefficient_revalorisation,
      scenario);
    assert.ok(lu[scenario].pension_annuelle > droit[scenario].pension_annuelle, scenario);
  }
  // Les rétroactifs ne lisent pas de droits acquis : ils ne bougent pas.
  for (const scenario of ["actuel", ...RETROACTIFS]) {
    assert.equal(lu[scenario].pension_annuelle, droit[scenario].pension_annuelle, scenario);
  }
});

test("une règle du stock que le moteur ne connaît pas arrête le simulateur qui la reçoit", () => {
  assert.throws(
    () => new Simulateur(paquet, { ...PARAMETRES_DEFAUT, stock_age_legal: "au_plus_tot" }),
    /stock_age_legal inconnu : 'au_plus_tot'/);
});
