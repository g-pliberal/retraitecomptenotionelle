// Le banc synthétique du lecteur PDF (action 161, étape 4) : un lot de PDF
// en base64, lu par le lecteur du site, ses lignes rendues (`synthetique.py`).
import { readFileSync, writeFileSync } from "node:fs";
import { lignesPdf, lignesParPage } from "../../moteur/js/lecture-pdf.js";

const [entree, sortie] = process.argv.slice(2);
const lot = JSON.parse(readFileSync(entree, "utf8"));
const rendu = [];
for (const { nom, b64 } of lot) {
  const octets = new Uint8Array(Buffer.from(b64, "base64"));
  try {
    rendu.push({ nom, lignes: await lignesPdf(octets), pages: await lignesParPage(octets) });
  } catch (e) {
    rendu.push({ nom, erreur: String(e) });
  }
}
writeFileSync(sortie, JSON.stringify(rendu));
