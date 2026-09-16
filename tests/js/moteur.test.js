/**
 * Le moteur JavaScript contre les cas-témoins du modèle Python.
 *
 * Le Python de ``src/`` reste la référence : il a été écrit contre les sources,
 * testé et documenté. Ce fichier vérifie que le JavaScript qui fait tourner le
 * site en retrouve les chiffres — et le HTML — sur un jeu de cas figé par
 * ``scripts/construire_temoins.py``. Toute divergence, sur n'importe quelle
 * valeur de l'un des cas, fait échouer le test.
 *
 *     node --test tests/js/
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { Contexte, Saisie, rendre } from "../../moteur/js/pages.js";
import { Affiliations } from "../../moteur/js/regimes.js";
import * as gabarit from "../../moteur/js/gabarit.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");

const lire = (chemin) => JSON.parse(readFileSync(join(RACINE, chemin), "utf8"));

const paquet = lire("moteur/donnees.json");
const temoinsSimulations = lire("tests/temoins/simulations.json");
const temoinsPages = lire("tests/temoins/pages.json");

/**
 * Tolérance relative. Python et JavaScript s'appuient sur la libm de leur
 * plateforme pour ``exp`` : deux implémentations correctes peuvent différer
 * d'un ulp, soit 1e-16 en relatif. On accepte 1e-9, six ordres de grandeur
 * au-dessus du bruit et six en dessous de ce qui se verrait à l'affichage.
 */
const TOLERANCE = 1e-9;

function comparer(obtenu, attendu, chemin, ecarts) {
  if (attendu === null) {
    // Le témoin écrit ``null`` là où Python produit NaN — écart non défini.
    if (!(obtenu === null || Number.isNaN(obtenu))) {
      ecarts.push(`${chemin} : attendu null, obtenu ${obtenu}`);
    }
    return;
  }
  if (typeof attendu === "number") {
    if (typeof obtenu !== "number") {
      ecarts.push(`${chemin} : attendu un nombre, obtenu ${typeof obtenu}`);
      return;
    }
    const ecart = Math.abs(obtenu - attendu);
    const relatif = attendu === 0 ? ecart : ecart / Math.abs(attendu);
    if (relatif > TOLERANCE) {
      ecarts.push(`${chemin} : python=${attendu} js=${obtenu} (écart ${relatif.toExponential(2)})`);
    }
    return;
  }
  if (Array.isArray(attendu)) {
    if (!Array.isArray(obtenu) || obtenu.length !== attendu.length) {
      ecarts.push(`${chemin} : tableau de ${attendu.length} attendu, obtenu ${
        Array.isArray(obtenu) ? obtenu.length : typeof obtenu}`);
      return;
    }
    attendu.forEach((valeur, i) => comparer(obtenu[i], valeur, `${chemin}[${i}]`, ecarts));
    return;
  }
  if (attendu !== null && typeof attendu === "object") {
    const clesAttendues = Object.keys(attendu).sort();
    const clesObtenues = Object.keys(obtenu ?? {}).sort();
    assert.deepEqual(clesObtenues, clesAttendues, `clés différentes en ${chemin}`);
    for (const cle of clesAttendues) {
      comparer(obtenu[cle], attendu[cle], `${chemin}.${cle}`, ecarts);
    }
    return;
  }
  if (obtenu !== attendu) {
    ecarts.push(`${chemin} : python=${JSON.stringify(attendu)} js=${JSON.stringify(obtenu)}`);
  }
}

test("les simulations retrouvent les chiffres du modèle Python", () => {
  const contexte = new Contexte(paquet);
  const ecarts = [];
  let cas = 0;
  for (const [nom, temoin] of Object.entries(temoinsSimulations)) {
    const saisie = Saisie.depuisRequete(temoin.requete);
    const obtenu = contexte.simuler(saisie).dictionnaire();
    comparer(obtenu, temoin.resultat, nom, ecarts);
    cas += 1;
  }
  assert.ok(cas > 50, `${cas} cas seulement : les témoins sont-ils à jour ?`);
  assert.deepEqual(ecarts, [], `${ecarts.length} écart(s) sur ${cas} cas`);
});

test("une faute de programme n'est pas présentée comme une faute de saisie", () => {
  // Le portage attrapait toute exception et affichait « Saisie refusée » : un
  // bug du moteur JavaScript accusait donc le lecteur. Ce test l'a vérifié
  // après coup sur un vrai bug — « serie.valeurs is not iterable » s'affichait
  // ainsi. Une saisie réellement invalide doit toujours donner sa phrase ; une
  // faute de programme doit remonter jusqu'à la page, qui dit « Le calcul a
  // échoué » sans mettre la faute sur personne.
  const contexte = new Contexte(paquet);
  const [, refus] = rendre(contexte, "/simuler", { liquidation: "12" });
  assert.match(refus, /Saisie refusée/, "une saisie invalide garde sa phrase");

  const prototype = Object.getPrototypeOf(contexte);
  const vrai = prototype.simuler;
  prototype.simuler = () => { throw new TypeError("bug interne simulé"); };
  try {
    assert.throws(
      () => rendre(contexte, "/simuler", { naissance: "1975", liquidation: "64" }),
      TypeError,
      "une faute de programme doit remonter, non être déguisée en refus",
    );
  } finally {
    prototype.simuler = vrai;
  }
});

test("les pages rendent le même HTML que le modèle Python", () => {
  const contexte = new Contexte(paquet);
  for (const [nom, temoin] of Object.entries(temoinsPages)) {
    const [titre, corps] = rendre(contexte, temoin.chemin, temoin.parametres);
    assert.equal(titre, temoin.titre, `titre de la page « ${nom} »`);
    assert.equal(sansBlocJson(corps), temoin.corps, `corps de la page « ${nom} »`);
  }
});

/**
 * Le bloc JSON de la page reprend les chiffres déjà comparés un à un ; ne
 * subsisterait que l'écriture des flottants, que Python et JavaScript ne
 * formatent pas de la même façon. On le retire des deux côtés, comme le fait le
 * générateur de témoins.
 */
function sansBlocJson(html) {
  return html.replace(/(<pre class="json">)[\s\S]*?(<\/pre>)/g, "$1$2");
}

test("le seuil d'affiliation de l'élu local est lu comme en Python", () => {
  // L. 382-31 : le régime général n'est dû qu'au-dessus de la moitié du
  // plafond ; en deçà, l'élu n'a que l'Ircantec. Sans revenu, la liste des
  // régimes possibles est rendue telle quelle.
  const affiliations = new Affiliations(paquet);
  assert.deepEqual(affiliations.regimes("elu_local", 2020), ["regime_general", "ircantec"]);
  assert.deepEqual(affiliations.regimes("elu_local", 2020, null, 16000, 41136), ["ircantec"]);
  assert.deepEqual(
    affiliations.regimes("elu_local", 2020, null, 24000, 41136),
    ["regime_general", "ircantec"],
  );
  assert.deepEqual(affiliations.regimes("elu_local", 2010, null, 100000, 34620), ["ircantec"]);
  assert.deepEqual(
    affiliations.regimes("salarie_prive_non_cadre", 2020, null, 1, 41136),
    ["regime_general", "agirc_arrco"],
  );
});

/**
 * Le ruban d'écart sur un trou de série.
 *
 * Les témoins de pages couvrent déjà tout ce que le ruban fait quand les deux
 * séries sont pleines — la page Coût en trace deux, dont les courbes se
 * croisent quatre fois, et le HTML est comparé caractère par caractère. Le
 * chemin qu'ils n'atteignent pas est celui d'une année manquante : là, le
 * ruban ne doit RIEN peindre, un écart interpolé par-dessus un trou affirmant
 * quelque chose que personne n'a mesuré.
 */
test("le ruban d'écart se tait sur une année manquante", () => {
  const pleine = new gabarit.Serie("A", [12.0, 11.0, 10.0], "var(--serie-5)");
  const trouee = new gabarit.Serie("B", [10.0, null, 12.0], "var(--serie-2)");
  const avec = gabarit.graphique("Essai", [2000, 2001, 2002], [pleine, trouee],
    "", false, 0, true, null, "", [], "Année", [0, 1]);
  assert.equal(avec.includes('class="ecart'), false);

  // Et, série pleine, il peint bien des deux côtés du croisement.
  const seconde = new gabarit.Serie("B", [10.0, 11.0, 12.0], "var(--serie-2)");
  const peint = gabarit.graphique("Essai", [2000, 2001, 2002], [pleine, seconde],
    "", false, 0, true, null, "", [], "Année", [0, 1]);
  assert.equal((peint.match(/class="ecart plus"/g) || []).length, 1);
  assert.equal((peint.match(/class="ecart moins"/g) || []).length, 1);
});
