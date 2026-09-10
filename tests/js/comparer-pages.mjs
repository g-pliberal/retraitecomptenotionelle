/**
 * Compare le HTML rendu par le site à celui du modèle Python.
 *
 *     node tests/js/comparer-pages.mjs pages.json
 *
 * Le fichier attendu est une liste d'objets ``{nom, requete, corps}`` produite
 * par ``tests/test_web.py``. Les témoins figés de ``tests/temoins/`` couvrent
 * des pages choisies ; celui-ci couvre des saisies auxquelles personne n'a
 * pensé — et surtout les deux unités de revenu, que la comparaison des seuls
 * NOMBRES ne voit pas : elle ignore les libellés, les aides chiffrées et le
 * lien de bascule, où vivent tous les arrondis d'affichage.
 *
 * Le bloc JSON est retiré des deux côtés, comme dans les témoins : Python et
 * JavaScript n'écrivent pas les flottants de la même façon, et le comparer ne
 * dirait rien du rendu.
 */

import { readFileSync } from "node:fs";

import { Contexte, rendre } from "../../moteur/js/pages.js";

const [, , fichierCas, fichierPaquet = "moteur/donnees.json"] = process.argv;
if (!fichierCas) {
  console.error("usage : node tests/js/comparer-pages.mjs <pages.json> [donnees.json]");
  process.exit(2);
}

const BLOC_JSON = /(<pre class="json">)[\s\S]*?(<\/pre>)/g;
const sansBlocJson = (html) => html.replace(BLOC_JSON, "$1$2");

const cas = JSON.parse(readFileSync(fichierCas, "utf8"));
const contexte = new Contexte(JSON.parse(readFileSync(fichierPaquet, "utf8")));

const divergences = [];
for (const { nom, requete, corps } of cas) {
  const obtenu = sansBlocJson(rendre(contexte, "/", requete)[1]);
  if (obtenu === corps) {
    continue;
  }
  // Le premier caractère qui diffère, avec ce qui l'entoure : sur une page de
  // quinze mille caractères, le diff entier ne se lit pas.
  let rang = 0;
  while (rang < obtenu.length && rang < corps.length && obtenu[rang] === corps[rang]) {
    rang += 1;
  }
  const autour = (texte) => JSON.stringify(
    texte.slice(Math.max(0, rang - 100), rang + 100),
  );
  divergences.push(`${nom} (${new URLSearchParams(requete)}) au caractère ${rang}\n`
    + `  python : ${autour(corps)}\n  js     : ${autour(obtenu)}`);
}

if (divergences.length > 0) {
  console.error(`${divergences.length} page(s) divergente(s) sur ${cas.length} :\n`);
  console.error(divergences.slice(0, 3).join("\n\n"));
  process.exit(1);
}
console.log(`${cas.length} pages rendues à l'identique.`);
