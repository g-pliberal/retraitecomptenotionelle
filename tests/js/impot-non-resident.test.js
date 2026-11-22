/**
 * L'impôt sur le revenu du retraité qui réside hors de France : la convention
 * fiscale de son État de résidence décide si la France impose sa pension.
 *
 * Les textes, lus le 21 novembre 2026 sur impots.gouv.fr (« Conventions
 * internationales ») :
 *
 * - Maroc, convention du 29 mai 1970, en vigueur le 1er décembre 1971,
 *   article 17 : « Les pensions et les rentes viagères ne sont imposables que
 *   dans l'Etat contractant où le bénéficiaire a son domicile fiscal. »
 *   L'article 18 bis, qui réserve les rémunérations publiques à l'État qui
 *   les paie, en exclut les pensions : celles des fonctionnaires aussi sont
 *   imposées au Maroc.
 * - Algérie, convention du 17 octobre 1999, en vigueur le 1er décembre 2002,
 *   article 18 : « les pensions et autres rémunérations similaires, payées à
 *   un résident d'un Etat contractant au titre d'un emploi antérieur, ne sont
 *   imposables que dans cet Etat » ; article 19, 1 : les pensions payées par
 *   un État ou ses personnes morales de droit public « ne sont imposables que
 *   dans cet Etat », sauf au résident de l'autre État qui en a la seule
 *   nationalité. Les sommes payées depuis l'entrée en vigueur relèvent de la
 *   convention : 2003 est sa première année entière.
 *
 * Les valeurs attendues viennent de là : rien d'imposé en France sur une
 * pension privée, ni au Maroc sur une pension publique ; la pension de
 * fonctionnaire d'un Français résidant en Algérie reste imposée comme avant ;
 * avant la convention lue, rien ne change.
 *
 *     node --test tests/js/impot-non-resident.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { Contexte } from "../../moteur/js/contexte.js";
import {
  fluxDesSystemes, partPubliqueDuDepart, partsImposablesParAnnee,
} from "../../moteur/js/cycle-de-vie.js";
import { Saisie } from "../../moteur/js/saisie.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const contexte = new Contexte(paquet);

const BASE = {
  age_reference: "fixe_apres_bascule", bascule: "2026", conversion_acquis: "reference",
  emploi: "cor_2026", enfants: "0", euros: "2026", indexation: "triple_lock_inverse",
  interruptions: "", primes: "0", profil: "ascendant", projection: "cor_reference",
  sexe: "H", stock: "prix", table: "unisexe", salaire: "1",
};

/** La comparaison, le simulateur et les flux après impôt d'une requête. */
function simuler(requete) {
  const saisie = Saisie.depuisRequete({ ...BASE, ...requete }, false, paquet.presomptions);
  const simulateur = contexte.simulateur(saisie.parametres(contexte.base));
  const comparaison = contexte.simuler(saisie);
  const systemes = fluxDesSystemes(simulateur, comparaison, { impot: "prix" });
  return { simulateur, comparaison, systemes };
}

/** La pension que le foyer déclare l'année `annee`, sans exonération. */
function entiere(flux, parts, annee) {
  return flux.niveaux.get(annee) * flux.servi(annee) * parts.get(annee);
}

const proche = (obtenu, attendu, quoi) => assert.ok(
  Math.abs(obtenu - attendu) <= 1e-6 * Math.max(1.0, Math.abs(attendu)),
  `${quoi} : ${obtenu}, attendu ${attendu}`);

test("au Maroc, aucune pension française n'est imposée en France", () => {
  for (const statut of ["salarie_prive_non_cadre", "fonctionnaire_etat"]) {
    const { systemes } = simuler({
      statut, naissance: "1955-03-15", debut: "1977-01", liquidation: "2020-04",
      residence: "MA",
    });
    for (const [scenario, flux] of Object.entries(systemes)) {
      for (const annee of [2020, 2021, 2026, 2040]) {
        assert.equal(flux.impots.get(annee).pension, 0.0, `${statut}, ${scenario}, ${annee}`);
      }
    }
  }
});

test("en Algérie, la pension privée cesse d'être imposée en France en 2003", () => {
  const { simulateur, comparaison, systemes } = simuler({
    statut: "salarie_prive_non_cadre", naissance: "1938-03-15", debut: "1960-01",
    liquidation: "1998-04", residence: "DZ",
  });
  const parts = partsImposablesParAnnee(simulateur, comparaison);
  const flux = systemes.actuel;
  for (const annee of [1999, 2002]) {
    proche(flux.impots.get(annee).pension, entiere(flux, parts, annee), `${annee}`);
  }
  for (const annee of [2003, 2010, 2026]) {
    assert.equal(flux.impots.get(annee).pension, 0.0, `${annee}`);
  }
});

test("en Algérie, la pension de fonctionnaire d'un Français reste imposée en France", () => {
  const { simulateur, comparaison, systemes } = simuler({
    statut: "fonctionnaire_etat", naissance: "1955-03-15", debut: "1977-01",
    liquidation: "2020-04", residence: "DZ",
  });
  const parts = partsImposablesParAnnee(simulateur, comparaison);
  const flux = systemes.actuel;
  for (const annee of [2020, 2026, 2040]) {
    proche(flux.impots.get(annee).pension, entiere(flux, parts, annee), `${annee}`);
  }
});

/**
 * Le RAFP est une pension publique : l'Établissement de retraite additionnelle
 * de la fonction publique, établissement public, la sert au titre de services
 * rendus à l'État (convention algérienne, article 19, 1, a : les pensions
 * payées « par une de leurs personnes morales de droit public »). Quand le
 * modèle le garde dans la répartition, sa part est publique ; isolé, il n'y
 * entre pas.
 */
test("le RAFP compte dans la part publique de la pension", () => {
  const resultat = { pensions_par_regime: [
    { regime: "fonction_publique_etat", montant: 900.0 },
    { regime: "rafp", montant: 100.0 },
    { regime: "regime_general", montant: 1000.0 },
  ] };
  const catalogue = contexte.simulateur().catalogue;
  const avec = { catalogue, parametres: { isoler_capitalisation: false } };
  const isole = { catalogue, parametres: { isoler_capitalisation: true } };
  proche(partPubliqueDuDepart(avec, resultat), 1000.0 / 2000.0, "RAFP dans la répartition");
  proche(partPubliqueDuDepart(isole, resultat), 900.0 / 1900.0, "RAFP isolé");
});

/**
 * L'article 197 A du code général des impôts, rédaction applicable aux
 * revenus perçus depuis le 1er janvier 2018 (loi n° 2018-1317, article 13, II,
 * A) : « Les règles du 1 et du 2 du I de l'article 197 sont applicables pour le
 * calcul de l'impôt sur le revenu dû par les personnes qui, n'ayant pas leur
 * domicile fiscal en France [...] perçoivent des revenus de source française »
 * — ni la réduction de 20 % du 3, des revenus de 2017 à 2019, ni la décote du
 * 4 ne le sont : l'impôt avant crédits est l'impôt brut. La pension d'un fonctionnaire résidant
 * au Portugal, que la France impose, perd la décote dès l'année qui suit son
 * départ ; la même, en France, la garde. La retenue à la source de l'article
 * 182 A « s'impute sur le montant de l'impôt sur le revenu établi dans les
 * conditions prévues à l'article 197 A » (V) : elle ne change pas l'impôt de
 * l'année.
 */
test("le non-résident que la France impose n'a pas de décote depuis les revenus de 2018", () => {
  const requete = { statut: "fonctionnaire_etat", naissance: "1955-03-15", debut: "1977-01",
    liquidation: "2016-04", salaire: "0.8" };
  const ici = simuler(requete).systemes.actuel;
  const portugal = simuler({ ...requete, residence: "PT" }).systemes.actuel;
  // 2018 est l'année blanche : le crédit de modernisation du recouvrement en
  // efface l'impôt, d'où 2019.
  for (const annee of [2019, 2026]) {
    const resident = ici.impots.get(annee).foyer;
    const nonResident = portugal.impots.get(annee).foyer;
    proche(portugal.impots.get(annee).pension, ici.impots.get(annee).pension, `${annee}`);
    assert.ok(resident.decote > 0.0, `${annee} : la décote du résident`);
    assert.equal(nonResident.decote, 0.0, `${annee}`);
    assert.ok(resident.impot_avant_credits < resident.impot_brut, `${annee} : le résident`);
    proche(nonResident.impot_brut, resident.impot_brut, `${annee}`);
    proche(nonResident.impot_avant_credits, nonResident.impot_brut, `${annee}`);
  }
  assert.deepStrictEqual(portugal.impots.get(2017).foyer, ici.impots.get(2017).foyer);
});
