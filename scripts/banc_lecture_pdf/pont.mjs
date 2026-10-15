// Le lecteur du site interrogé par le banc du lecteur PDF (action 161, étape 4).
//
//     node pont.mjs <pdf> <question> <tolérance> <réponse.json>
//
// `commun.py` copie ce fichier, avec le lecteur du site dont il exporte les
// fonctions internes, dans le dossier de travail du banc : il ne tourne pas
// depuis le dépôt. Les questions : `lignes` et `pages`, ce que rendent
// `lignesPdf` et `lignesParPage` ; `fragments_pages`, les fragments triés,
// page par page, que la lecture par abscisse du Python reprend ; `tout`, chaque
// niveau de la lecture, les objets et les flux en empreintes.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import * as l from "./lecture-pdf-banc.mjs";

const [chemin, quoi, tolerance, sortie] = process.argv.slice(2);
const octets = new Uint8Array(readFileSync(chemin));
const t = Number(tolerance);
const empreinte = (chaine) => createHash("sha1").update(Buffer.from(chaine, "latin1")).digest("hex");
const table = (tab) => ({
  largeur: tab.largeur, repli: tab.repli, codes: [...tab.entries()].sort((a, b) => a[0] - b[0]),
});

function parPage(tries) {
  const pages = new Map();
  for (const f of tries) {
    if (!pages.has(f[0])) pages.set(f[0], []);
    pages.get(f[0]).push(f);
  }
  return [...pages.keys()].sort((a, b) => a - b).map((p) => pages.get(p));
}

const debut = performance.now();
let rendu;
if (quoi === "lignes") {
  rendu = await l.lignesPdf(octets, t);
} else if (quoi === "pages") {
  rendu = await l.lignesParPage(octets, t);
} else if (quoi === "fragments_pages") {
  rendu = parPage(l.trier(await l.fragments(l.enChaine(octets))));
} else if (quoi === "tout") {
  const { objets, flux } = await l.lireObjets(l.enChaine(octets));
  const parContenu = l.policesParContenu(objets, flux);
  const communes = l.polices(objets, flux);
  const bruts = await l.fragments(l.enChaine(octets));
  const tries = l.trier(bruts);
  rendu = {
    objets: Object.fromEntries([...objets].map(([n, o]) => [n, empreinte(o)])),
    flux: Object.fromEntries([...flux].map(([n, f]) => [n, empreinte(f)])),
    par_contenu: Object.fromEntries([...parContenu].map(([n, tables]) => [
      n, Object.fromEntries([...tables].map(([nom, tab]) => [nom, table(tab)]))])),
    communes: Object.fromEntries([...communes].map(([nom, tab]) => [nom, table(tab)])),
    fragments: bruts,
    lignes: l.assembler(tries, t),
    pages: parPage(tries).map((page) => l.assembler(page, t)),
  };
} else {
  throw new Error(`question inconnue : ${quoi}`);
}
writeFileSync(sortie, JSON.stringify({ duree: (performance.now() - debut) / 1000, rendu }));
