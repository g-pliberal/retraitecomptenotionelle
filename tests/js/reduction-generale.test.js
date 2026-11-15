/**
 * L'arrondi du coefficient de la réduction générale (et de la Lodeom) : « au
 * dix-millième le plus proche » (D. 241-7, I : le coefficient « est arrondi à
 * quatre décimales, au dix-millième le plus proche »).
 *
 * Le portage arrondissait par `Math.round(x * 1e4) / 1e4` : la multiplication
 * arrondit déjà, et une valeur juste SOUS la moitié d'un dix-millième y
 * devenait la moitié exacte, que `Math.round` montait. 0,21284999999999998
 * donnait 0,2129 au lieu de 0,2128 : 3,45 € de réduction en trop sur le
 * témoin `rattachement_pension_smic`, années 11 à 13 de la proposition, où la
 * dichotomie du coût du travail donné s'arrête au bord de ce saut.
 *
 *     node --test tests/js/reduction-generale.test.js
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { ReductionGenerale, arrondiAuDixMillieme } from "../../moteur/js/remuneration.js";

test("une valeur juste sous la moitié d'un dix-millième s'arrondit en dessous", () => {
  // 0,21284999999999998 est à 4,999…998 cent-millièmes de 0,2128, à
  // 5,000…002 de 0,2129 : le plus proche est 0,2128.
  assert.equal(arrondiAuDixMillieme(0.21284999999999998), 0.2128);
  assert.equal(arrondiAuDixMillieme(0.2128500000000002), 0.2129);
  assert.equal(arrondiAuDixMillieme(0.21284999999999984), 0.2128);
  assert.equal(arrondiAuDixMillieme(0.4021), 0.4021);
  assert.equal(arrondiAuDixMillieme(0), 0);
});

test("le coefficient du témoin au SMIC, année 11 de la proposition", () => {
  // Les entrées du cas, relevées sur le témoin : le brut où s'arrête la
  // dichotomie, le SMIC annuel de l'année, la retraite patronale de la
  // proposition. Le périmètre est celui de
  // `data/reference/legislation/prelevements_remuneration.yaml`.
  const reduction = new ReductionGenerale({
    libelle: "Réduction générale dégressive unique",
    plafond_en_smic: 3.0,
    puissance: 1.75,
    taux_minimum: 0.02,
    coefficient_maximal: 0.4021,
    composantes: {
      maladie: 0.1300, vieillesse_plafonnee: 0.0855, vieillesse_deplafonnee: 0.0211,
      famille: 0.0525, accidents_travail: 0.0049, autonomie: 0.0030,
      agirc_arrco: 0.0472, equilibre_general: 0.0129, chomage: 0.0400, logement: 0.0050,
    },
    composantes_retraite: [
      "vieillesse_plafonnee", "vieillesse_deplafonnee", "agirc_arrco", "equilibre_general",
    ],
  });
  // T − Tmin multiplié par le rapport à la puissance 1,75 y vaut
  // 0,21284999999999998 : le coefficient est 0,02 + 0,2128.
  assert.equal(
    reduction.coefficient(34520.5218592072, 28945.49937682269, 0.13046086956521738),
    0.02 + 0.2128,
  );
});
