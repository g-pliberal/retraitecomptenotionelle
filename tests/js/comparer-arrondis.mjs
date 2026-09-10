/**
 * Compare l'arrondi du portage à celui de Python, valeur par valeur.
 *
 *     node tests/js/comparer-arrondis.mjs arrondis.json
 *
 * Le lien qui bascule d'unité écrit un nombre arrondi ; il doit être le même
 * des deux côtés, sans quoi le site et la référence n'enverraient pas vers la
 * même adresse. Or Python et JavaScript ne tranchent pas les demis de la même
 * façon : ``round`` va au pair, ``Math.round`` monte. Le portage passe donc par
 * le développement décimal exact du flottant — c'est ce que ce contrôle vérifie
 * sur des valeurs choisies pour tomber pile sur un demi.
 *
 * Le fichier attendu est une liste ``[{x, attendus: [chaîne par décimale]}]``.
 */

import { readFileSync } from "node:fs";

import { formatFixe, formatG } from "../../moteur/js/format.js";

const arrondir = (valeur, decimales) => Number(formatFixe(valeur, decimales));

const [, , fichierCas] = process.argv;
if (!fichierCas) {
  console.error("usage : node tests/js/comparer-arrondis.mjs <arrondis.json>");
  process.exit(2);
}

const cas = JSON.parse(readFileSync(fichierCas, "utf8"));
const divergences = [];
for (const { x, attendus } of cas) {
  attendus.forEach((attendu, decimales) => {
    const obtenu = formatG(arrondir(x, decimales));
    if (obtenu !== attendu) {
      divergences.push(`round(${x}, ${decimales}) : python ${attendu}, js ${obtenu}`);
    }
  });
}

if (divergences.length > 0) {
  console.error(`${divergences.length} divergence(s) :\n${divergences.slice(0, 10).join("\n")}`);
  process.exit(1);
}
console.log(`${cas.length} valeurs arrondies à l'identique.`);
