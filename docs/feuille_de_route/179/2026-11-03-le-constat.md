# Le constat du 3 novembre 2026 : le traitement passé d'un fonctionnaire, rebâti sur le salaire moyen

**Ce qui a été mesuré.** Ce que le moteur rebâtit du traitement passé d'un
fonctionnaire, contre ce que vaudrait, à progression égale, un traitement qui
aurait suivi le point d'indice ; puis ce que l'écart fait aux systèmes 2 et 3
du site (les scénarios 2 et 4 du modèle). Mesuré sur `main` du 3 novembre 2026
(commit 0a64139), aux paramètres par défaut, par le portage, qui fait foi.

**Les sources.**

- Le point : `data/reference/legislation/point_indice_fonction_publique.csv`,
  valeur en vigueur au 1er janvier de chaque année, lue à l'article 3 du décret
  n° 85-1148 du 24 octobre 1985 depuis 1996 (en-tête du fichier).
- Le salaire moyen par tête (SMPT) : `salaireMoyenAnnuel` du portage
  (`moteur/js/carriere.js`), qui cumule depuis son niveau de 2024
  (`macro/salaire_moyen_niveau.csv`) les croissances de
  `macro/salaire_moyen.csv` : les salaires et traitements bruts des comptes
  nationaux de l'INSEE rapportés à l'emploi salarié, certifiés de 1950 à 2025.
- Le revenu d'une année d'une carrière sans relevé : le niveau saisi, fois le
  profil d'âge du groupe, fois le SMPT de l'année (`revenuAnnuel`,
  `moteur/js/carriere.js:2365-2372`) ; le profil d'un fonctionnaire de l'État
  est `public_etat` (`PROFIL_PAR_AFFILIATION`).
- Les carrières : `Simulateur.carriereSimple`, statut `fonctionnaire_etat`, au
  niveau 1, femme.

**La méthode.** À indice constant, le traitement d'une année t rapporté à
celui d'une année de référence R vaut point(t) / point(R) ; le modèle le
rebâtit SMPT(t) / SMPT(R), à profil égal. Le traitement réel valait donc
(SMPT(R) / SMPT(t)) / (point(R) / point(t)) fois ce que le modèle rebâtit.
Pour la pension, chaque cotisation annuelle du compte est multipliée par ce
rapport, ancré sur la dernière année d'avant la bascule (2025) — le traitement
de cette année-là est le même des deux côtés —, puis revalorisée et divisée
comme le moteur le fait : même revalorisation, même diviseur. Les cotisations
d'un fonctionnaire étant proportionnelles à son traitement, sans plafond, le
rapport passe tel quel au compte.

Ce que la méthode ne voit pas, et qui en fait un ordre de grandeur : les
refontes de grilles, qui relèvent l'indice d'un échelon et réduisent l'écart ;
la progression réelle d'une carrière, prise ici au profil de l'INSEE ; la
valeur du point au 1er janvier, quand le SMPT est une moyenne de l'année.

**Le calcul**, enregistré hors du dépôt sous `constat_179.mjs` et lancé depuis
sa racine (`node constat_179.mjs`) :

```js
import { readFileSync } from "node:fs";
const racine = `file://${process.cwd()}/`;
const { PARAMETRES_DEFAUT } = await import(new URL("moteur/js/config.js", racine));
const { Simulateur } = await import(new URL("moteur/js/simulateur.js", racine));
const { salaireMoyenAnnuel } = await import(new URL("moteur/js/carriere.js", racine));
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
// La valeur du point au 1er janvier, telle que le fichier la porte.
const point = new Map(readFileSync("data/reference/legislation/point_indice_fonction_publique.csv", "utf8")
  .split("\n").filter((l) => /^\d{4},/.test(l)).map((l) => l.split(",")).map(([a, v]) => [+a, +v]));
const sim = new Simulateur(paquet, PARAMETRES_DEFAUT);
const smpt = (a) => salaireMoyenAnnuel(sim.macro, a);

// 1. Le point et le SMPT, de 1990 à 2024.
console.log(`point 1990 -> 2024 : x${(point.get(2024) / point.get(1990)).toFixed(2)} ; SMPT : x${(smpt(2024) / smpt(1990)).toFixed(2)}`);
// 2. À indice constant, le traitement réel de l'année rapporté à ce que le SMPT reconstitue, base 2024.
console.log([1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020]
  .map((a) => `${a} : ${((smpt(2024) / smpt(a)) / (point.get(2024) / point.get(a))).toFixed(2)}`).join(" ; "));

// 3. La pension, si le traitement passé avait suivi le point : chaque cotisation
// annuelle du compte multipliée par ce rapport, ancré sur la dernière année
// avant la bascule ; même revalorisation, même diviseur.
for (const [naissance, debut, depart] of [[1962, 22, 64], [1958, 23, 62]]) {
  const carriere = sim.carriereSimple({ sexe: "F", annee_naissance: naissance, affiliation: "fonctionnaire_etat",
    age_debut: debut, age_liquidation: depart, niveau_salaire: 1.0 });
  const c = sim.simuler(carriere);
  const L = carriere.anneeLiquidation;
  const ancre = Math.min(L, PARAMETRES_DEFAUT.annee_bascule - 1);
  const ligne = [`née en ${naissance}, de ${debut} à ${depart} ans, départ en ${L} ; système 1 : ${(c.actuel.pension_annuelle / 12).toFixed(0)} €`];
  for (const [nom, cle] of [["système 2", "notionnel_retroactif"], ["système 3", "notionnel_retroactif_employeur"]]) {
    const r = c[cle];
    let capital = 0, corrige = 0;
    for (const l of r.compte.cotisations) {
      const k = sim.indexation.coefficient(l.annee, L);
      const f = l.annee <= ancre ? (smpt(ancre) / smpt(l.annee)) / (point.get(ancre) / point.get(l.annee)) : 1.0;
      capital += l.cotisation * k; corrige += l.cotisation * k * f;
    }
    ligne.push(`${nom} : ${(r.pension_annuelle / 12).toFixed(0)} € -> ${(r.pension_annuelle * corrige / capital / 12).toFixed(0)} € (x${(corrige / capital).toFixed(2)})`);
  }
  console.log(ligne.join(" ; ") + " — par mois, en euros de l'année du départ");
}
```

**Ce qu'il rend** :

```
point 1990 -> 2024 : x1.37 ; SMPT : x2.22
1975 : 1.87 ; 1980 : 1.71 ; 1985 : 1.79 ; 1990 : 1.62 ; 1995 : 1.58 ; 2000 : 1.52 ; 2005 : 1.35 ; 2010 : 1.24 ; 2015 : 1.16 ; 2020 : 1.14
née en 1962, de 22 à 64 ans, départ en 2026 ; système 1 : 3246 € ; système 2 : 588 € -> 792 € (x1.35) ; système 3 : 2624 € -> 3421 € (x1.30) — par mois, en euros de l'année du départ
née en 1958, de 23 à 62 ans, départ en 2020 ; système 1 : 2203 € ; système 2 : 381 € -> 475 € (x1.25) ; système 3 : 1638 € -> 1969 € (x1.20) — par mois, en euros de l'année du départ
```

**Ce que l'étape 3 en fait.** Le premier test de l'action le refait sans
correction a posteriori : une carrière au profil plat d'un statut payé à
l'indice doit rendre chaque année l'indice fois le point, et les pensions
ci-dessus deviennent la mesure de ce que l'étape déplace.
