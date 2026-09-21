/**
 * Le lecteur PDF du navigateur contre les documents minimaux du Python.
 *
 * `tests/test_lecture_pdf.py` tient neuf comportements du lecteur de référence,
 * chacun par un document fabriqué à la main : les polices rangées dans un flux
 * d'objets, les chaînes littérales à un octet par code, le même nom de police
 * qui change de table d'une page à l'autre, les codes sur deux octets d'une
 * police Type0, les polices d'un formulaire, les espaces posées seules et les
 * reculs d'un tableau ``TJ``, les dictionnaires en ligne du contenu balisé, les
 * échappements lus en une passe, et l'image qu'on ne lit pas comme du texte.
 *
 * Les mêmes documents sont refaits ici, octet pour octet, et le portage doit en
 * rendre les mêmes lignes. Un lecteur qui diverge du modèle sur l'un d'eux
 * lirait le relevé de carrière déposé sur le site autrement que le Python ne le
 * lit — et c'est le Python qui fait foi.
 *
 *     node --test tests/js/lecture-pdf.test.js
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { lignesPdf } from "../../moteur/js/lecture-pdf.js";

// -- fabrique de documents ---------------------------------------------------

/** Les octets d'une chaîne latin-1, un octet par caractère. */
function octets(chaine) {
  const sortie = new Uint8Array(chaine.length);
  for (let i = 0; i < chaine.length; i += 1) sortie[i] = chaine.charCodeAt(i) & 0xff;
  return sortie;
}

function enChaine(tableau) {
  return Array.from(tableau, (octet) => String.fromCharCode(octet)).join("");
}

async function comprimer(donnees) {
  const flux = new Blob([octets(donnees)]).stream()
    .pipeThrough(new CompressionStream("deflate"));
  return enChaine(new Uint8Array(await new Response(flux).arrayBuffer()));
}

function objet(numero, corps) {
  return `${numero} 0 obj\n${corps}\nendobj\n`;
}

function flux(dictionnaire, donnees) {
  return `${dictionnaire.slice(0, -2)} /Length ${donnees.length} >>\nstream\n`
    + `${donnees}\nendstream`;
}

async function fluxComprime(dictionnaire, donnees) {
  const comprime = await comprimer(donnees);
  return flux(`${dictionnaire.slice(0, -2)} /Filter /FlateDecode >>`, comprime);
}

/** Une table ToUnicode : code de glyphe -> caractère, sur une ou deux octets. */
function cmap(largeur, correspondances) {
  const plage = largeur === 1 ? "<00> <FF>" : "<0000> <FFFF>";
  const entrees = Object.entries(correspondances).map(([code, lettre]) => {
    const source = Number(code).toString(16).toUpperCase().padStart(2 * largeur, "0");
    const cible = [...lettre].map(
      (c) => c.charCodeAt(0).toString(16).toUpperCase().padStart(4, "0"),
    ).join("");
    return `<${source}> <${cible}>\n`;
  }).join("");
  return `1 begincodespacerange\n${plage}\nendcodespacerange\n`
    + `${Object.keys(correspondances).length} beginbfchar\n${entrees}endbfchar\n`;
}

function document(...corps) {
  return octets(`%PDF-1.5\n${corps.join("")}trailer\n<< >>\n%%EOF\n`);
}

/** Un ``/ObjStm`` : en tête les paires « numéro décalage », puis les objets. */
async function fluxDObjets(numero, contenus) {
  let tete = "";
  let corps = "";
  for (const [numeroObjet, contenu] of contenus) {
    tete += `${numeroObjet} ${corps.length} `;
    corps += `${contenu}\n`;
  }
  const donnees = `${tete}\n${corps}`;
  const dictionnaire = `<< /Type /ObjStm /N ${contenus.length} /First ${tete.length + 1} >>`;
  return objet(numero, await fluxComprime(dictionnaire, donnees));
}

// -- les neuf comportements --------------------------------------------------

test("les polices rangées dans un flux d'objets sont lues", async () => {
  const contenu = "BT /TT0 12 Tf 70 700 Td (\\001\\002\\002\\003) Tj ET";
  const pdf = document(
    objet(5, flux("<< >>", contenu)),
    objet(7, flux("<< >>", cmap(1, { 1: "A", 2: "n", 3: "e" }))),
    await fluxDObjets(9, [
      [4, "<< /Type /Page /Contents 5 0 R /Resources << /Font << /TT0 6 0 R >> >> >>"],
      [6, "<< /Type /Font /Subtype /TrueType /ToUnicode 7 0 R >>"],
    ]),
  );
  assert.deepEqual(await lignesPdf(pdf), ["Anne"]);
});

test("le même nom de police change de table d'une page à l'autre", async () => {
  const pdf = document(
    objet(1, "<< /Type /Page /Contents 2 0 R /Resources << /Font << /TT0 3 0 R >> >> >>"),
    objet(2, flux("<< >>", "BT /TT0 12 Tf 70 700 Td (\\001\\002) Tj ET")),
    objet(3, "<< /Type /Font /ToUnicode 4 0 R >>"),
    objet(4, flux("<< >>", cmap(1, { 1: "U", 2: "N" }))),
    objet(5, "<< /Type /Page /Contents 6 0 R /Resources << /Font << /TT0 7 0 R >> >> >>"),
    objet(6, flux("<< >>", "BT /TT0 12 Tf 70 700 Td (\\001\\002\\003\\004) Tj ET")),
    objet(7, "<< /Type /Font /ToUnicode 8 0 R >>"),
    objet(8, flux("<< >>", cmap(1, { 1: "D", 2: "E", 3: "U", 4: "X" }))),
  );
  assert.deepEqual(await lignesPdf(pdf), ["UN", "DEUX"]);
});

test("une police Type0 lit ses codes sur deux octets", async () => {
  const pdf = document(
    objet(1, "<< /Type /Page /Contents 2 0 R /Resources << /Font << /C2_0 3 0 R >> >> >>"),
    objet(2, flux("<< >>", "BT /C2_0 12 Tf 70 700 Td <00350044> Tj "
      + "0 -20 Td (\\000\\065\\000\\104) Tj ET")),
    objet(3, "<< /Type /Font /Subtype /Type0 /Encoding /Identity-H /ToUnicode 4 0 R >>"),
    objet(4, flux("<< >>", cmap(2, { 0x35: "R", 0x44: "a" }))),
  );
  assert.deepEqual(await lignesPdf(pdf), ["Ra", "Ra"]);
});

test("un formulaire porte ses propres polices", async () => {
  const pdf = document(
    objet(1, "<< /Type /Page /Contents 2 0 R /Resources << /XObject << /Fm0 3 0 R >> >> >>"),
    objet(2, flux("<< >>", "q /Fm0 Do Q")),
    objet(3, flux("<< /Type /XObject /Subtype /Form /BBox [0 0 100 100] "
      + "/Resources << /Font << /F5 4 0 R >> >> >>",
    "BT /F5 8 Tf 10 50 Td (\\001\\002) Tj ET")),
    objet(4, "<< /Type /Font /ToUnicode 5 0 R >>"),
    objet(5, flux("<< >>", cmap(1, { 1: "O", 2: "K" }))),
  );
  assert.deepEqual(await lignesPdf(pdf), ["OK"]);
});

test("les espaces posées seules et les reculs du tableau séparent les mots", async () => {
  const contenu = "BT /F1 10 Tf 70 700 Td (Effectif) Tj ( ) Tj (total) Tj "
    + "0 -20 Td [(Rapport) -250 (sur) -20 (les)] TJ ET";
  const pdf = document(objet(1, flux("<< >>", contenu)));
  assert.deepEqual(await lignesPdf(pdf), ["Effectif total", "Rapport surles"]);
});

test("un dictionnaire en ligne du contenu balisé ne s'imprime pas", async () => {
  const contenu = "BT /F1 10 Tf 70 700 Td /Span <</MCID 3 /Lang (en-US)>> BDC "
    + "(FPE) Tj EMC ( ) Tj /Span <</Lang (en-US)>> BDC (Civils) Tj EMC ET";
  const pdf = document(objet(1, flux("<< >>", contenu)));
  assert.deepEqual(await lignesPdf(pdf), ["FPE Civils"]);
});

test("les échappements d'une chaîne littérale se lisent en une passe", async () => {
  const contenu = "BT /F1 10 Tf 70 700 Td (a\\\\101\\(b\\)\\101) Tj ET";
  const pdf = document(objet(1, flux("<< >>", contenu)));
  assert.deepEqual(await lignesPdf(pdf), ["a\\101(b)A"]);
});

test("une image n'est pas lue comme du texte", async () => {
  const pdf = document(
    objet(1, flux("<< /Type /XObject /Subtype /Image /Width 1 /Height 1 >>",
      "\x00 BT (BRUIT) Tj ET \xff")),
    objet(2, flux("<< >>", "BT /F1 10 Tf 70 700 Td (TEXTE) Tj ET")),
  );
  assert.deepEqual(await lignesPdf(pdf), ["TEXTE"]);
});

test("une police simple lit par un octet quoi que déclare sa table", async () => {
  const pdf = document(
    objet(1, "<< /Type /Page /Contents 2 0 R /Resources << /Font << /F1 3 0 R >> >> >>"),
    objet(2, flux("<< >>", "BT /F1 10 Tf 70 700 Td (du\\351) Tj ET")),
    objet(3, "<< /Type /Font /Subtype /TrueType /Encoding /WinAnsiEncoding "
      + "/ToUnicode 4 0 R >>"),
    objet(4, flux("<< >>", cmap(2, { 0x64: "d", 0x75: "u" }))),
  );
  assert.deepEqual(await lignesPdf(pdf), ["dué"]);
});

// -- ce que le navigateur fait et que Python ne fait pas ---------------------

test("un flux tronqué ne rend rien, un flux bavard rend tout", async () => {
  // `zlib.decompress` ignore les octets qui traînent derrière la fin d'un flux
  // et refuse un flux tronqué ; `DecompressionStream` lève dans les deux cas.
  // Le lecteur les sépare par la somme Adler-32 que zlib pose en queue.
  const contenu = "BT /F1 10 Tf 70 700 Td (LISIBLE) Tj ET";
  const comprime = await comprimer(contenu);
  const bavard = document(objet(1, flux(
    "<< /Filter /FlateDecode >>", `${comprime}\x00\x00`,
  )));
  assert.deepEqual(await lignesPdf(bavard), ["LISIBLE"]);

  const tronque = document(objet(1, flux(
    "<< /Filter /FlateDecode >>", comprime.slice(0, comprime.length - 6),
  )));
  assert.deepEqual(await lignesPdf(tronque), []);
});

test("chaque objet texte repart de l'origine de la page", async () => {
  // `BT` remet la matrice de texte à l'identité. Sans cela, les ordonnées
  // s'additionnent d'un objet au suivant et le document sort à l'envers — le
  // défaut qui rendait illisible le premier relevé de carrière déposé.
  const contenu = "BT /F1 10 Tf 60 700 Td (HAUT) Tj ET "
    + "BT /F1 10 Tf 60 680 Td (MILIEU) Tj ET "
    + "BT /F1 10 Tf 60 660 Td (BAS) Tj ET";
  const pdf = document(objet(1, flux("<< >>", contenu)));
  assert.deepEqual(await lignesPdf(pdf), ["HAUT", "MILIEU", "BAS"]);
});

