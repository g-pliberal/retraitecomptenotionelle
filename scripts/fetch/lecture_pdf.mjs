// Le lecteur PDF du site, pour la fabrique : le document sur l'entrée standard,
// la question en argument, la réponse en JSON sur la sortie.
//
//     node scripts/fetch/lecture_pdf.mjs lignes|pages|fragments|page [argument] < document.pdf
//
// `scripts/fetch/lecture_pdf.py` l'appelle ; les questions sont ses fonctions :
// `lignes` et `pages` (`lignesPdf`, `lignesParPage`, la tolérance en argument),
// `fragments` (`fragmentsParPage`), `page` (`contenuDeLaPage`, son numéro en
// argument). Une erreur se rend comme une réponse, `{erreur, message}`, pour que
// le Python lève la sienne.
import {
  contenuDeLaPage, fragmentsParPage, lignesParPage, lignesPdf,
} from "../../moteur/js/lecture-pdf.js";

const [question, argument] = process.argv.slice(2);
const morceaux = [];
for await (const morceau of process.stdin) morceaux.push(morceau);
const octets = new Uint8Array(Buffer.concat(morceaux));

let reponse;
try {
  if (question === "lignes") reponse = { rendu: await lignesPdf(octets, Number(argument)) };
  else if (question === "pages") reponse = { rendu: await lignesParPage(octets, Number(argument)) };
  else if (question === "fragments") reponse = { rendu: await fragmentsParPage(octets) };
  else if (question === "page") reponse = { rendu: await contenuDeLaPage(octets, Number(argument)) };
  else throw new Error(`question inconnue : ${question}`);
} catch (erreur) {
  reponse = { erreur: erreur.name, message: erreur.message };
}
process.stdout.write(JSON.stringify(reponse));
