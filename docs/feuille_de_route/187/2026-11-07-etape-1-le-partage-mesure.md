# Étape 1 : le partage entre le moteur et le site, mesuré

**La demande.** Le 7 novembre 2026, le propriétaire ouvre le chantier 9 du
programme, le site et le simulateur, et tranche (décisions 34 et 35 de
`docs/feuille_de_route_programme.md`) : le simulateur ira aux adhérents, il
reste sur le site d'ici là, et le moteur s'en sépare « au fur et à mesure des
commits de notre site frontend », pour que d'autres puissent « exploiter le
moteur de leur côté ». Cette étape mesure ce qui sépare déjà le calcul du
site, et écrit le plan ; elle ne touche pas au code.

**Ce que « backend » veut dire ici.** Le mot se lit de deux façons : une
bibliothèque — le code du calcul et ses données, qui servent sans le site,
qu'un autre importe ou lance chez lui — ou un service en ligne, que le site
et les autres appellent. La session retient la bibliothèque d'abord, pour
trois raisons. Le site est statique et calcule chez son lecteur : la
carrière qu'il saisit, ses salaires, ses enfants, son invalidité, ne quitte
jamais son navigateur ; un service la recevrait, et ce sont des données
personnelles, qu'il faudrait protéger et déclarer. Un service se paie,
s'héberge et se surveille ; une bibliothèque, non. Un service s'écrit en
quelques lignes autour d'une bibliothèque, l'inverse ne se fait pas. Le choix
de la diffusion reste au propriétaire, à l'étape 6.

**Ce que la mesure a trouvé**, le 7 novembre, sur les 79 modules de
`moteur/js/` et leurs imports :

- **Le site** : `pages.js` (902 Ko), `gabarit.js` (128 Ko), `routeur.js`
  (147 Ko), `adresses.js`. Ils montrent ; ils importent le calcul.
- **Le calcul** : `simulateur.js` et tout ce qu'il importe, les 22 modules de
  `droit/`, `contexte.js`, qui bâtit la carrière, `saisie.js`, qui la lit et
  la vérifie, `agregats.js`, et `releve-lu.js` et `lecture-pdf.js`, qui
  lisent un relevé de carrière.
- **Aucun module du calcul n'importe `pages.js`, `routeur.js` ni
  `adresses.js`.** Trois liens seulement passent la ligne : `contexte.js`
  emprunte une fois `g.euros` à `gabarit.js` ; `saisie.js` lui emprunte
  `g.nombre` douze fois et `g.euros` deux fois ; `saisie.js` lit les
  constantes de `cles.js`, que le démarrage du site lit aussi
  (`moteur/CLAUDE.md`, « Le démarrage »), et qu'il faudra ranger d'un côté
  ou mettre en commun.
- **`format.js` est un terrain commun** : `formatFixe`, `formatPourcentage`,
  `arrondi`, sans aucun import. Six modules de `droit/`, `scenario-actuel.js`,
  `echeancier.js` et `fusion.js` s'en servent : le moteur écrit avec lui, en
  français, les explications de ses résultats.
- **Le moteur tourne déjà hors du navigateur.** `src/retraite_notionnelle/pont.mjs`
  le fait calculer par node pour la fabrique — la grille du coût, les cas
  types —, et `pont.mjs --servir` le garde lancé sur un paquet lu (note de
  décision 0003, action 161). C'est un premier client qui n'est pas le site ;
  mais il importe `contexte.js` et `saisie.js`, donc `gabarit.js`, par les
  trois liens.
- **Les données** : le moteur ne lit qu'un paquet, `moteur/donnees.json`
  (6 102 290 octets ce jour-là), en version 41 (`VERSION_PAQUET`, dans
  `contexte.js`), que le Python fabrique ; il ne lit pas le YAML.
- **Les tests** : sur les 23 fichiers de `tests/js/`, deux importent un
  module du site, `bascules.test.js` et `moteur.test.js`.

**Pas de déplacement de fichiers d'abord.** Ranger le calcul dans un dossier
à lui toucherait chaque import, le pont, les tests et la conservation, pour
rien que le partage exige : une liste des modules du site, gardée par un
test, sépare autant, et un `package.json` dont les `exports` ne nomment que
l'entrée publique ferait le reste, si la diffusion le demande. Le plan est
celui de l'action 187, dans `docs/feuille_de_route.md`.
