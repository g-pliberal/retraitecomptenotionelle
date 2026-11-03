# Le constat du 3 novembre 2026 : ce que le relevé plafonné retire au compte d'un cadre

**Ce qui a été mesuré.** Ce que le compte du système 2 du site (le scénario 2
du modèle, la part salariale seule) reçoit en 2020 d'un cadre du privé payé
deux plafonds de la Sécurité sociale, selon que la ligne de 2020 porte son
salaire entier ou le salaire plafonné que garde le relevé du régime général.
La simulation lit en effet ce que le relevé porte (`moteur/js/releve-lu.js`,
lignes 955 à 963). Mesuré sur `main` du 3 novembre 2026 (commit 0a64139), aux
paramètres par défaut, par le portage.

**Les taux**, ceux que le moteur lit au paquet :

- au régime général (`data/reference/regimes/taux_cotisation_annuels.csv`,
  2020) : 15,45 % sous le plafond, dont 44,6602 % au salarié, soit 6,90 % ; et
  2,30 % sur la totalité, dont 17,3913 %, soit 0,40 % ;
- à l'Agirc-Arrco (`data/reference/regimes/agirc_arrco.yaml`, périodes de
  2019) : 7,87 % sur la tranche 1 et 21,59 % sur la tranche 2, répartis 40/60
  par l'article 38 de l'accord du 17 novembre 2017, soit 3,148 % et 8,636 % au
  salarié.

**À la main**, en plafonds : 6,90 + 2 × 0,40 + 3,148 + 8,636 = 19,484 % d'un
plafond sur le salaire entier ; 6,90 + 0,40 + 3,148 = 10,448 % sur le salaire
plafonné. Au plafond de 2020, 41 136 €, cela fait 8 014,94 € et 4 297,89 € :
le compte reçoit 53,6 % des cotisations salariales de l'année.

**Le calcul**, enregistré hors du dépôt sous `constat_180.mjs` et lancé depuis
sa racine (`node constat_180.mjs`) :

```js
import { readFileSync } from "node:fs";
const racine = `file://${process.cwd()}/`;
const { PARAMETRES_DEFAUT } = await import(new URL("moteur/js/config.js", racine));
const { Simulateur } = await import(new URL("moteur/js/simulateur.js", racine));
const { AnneeCarriere, Carriere } = await import(new URL("moteur/js/carriere.js", racine));
const sim = new Simulateur(JSON.parse(readFileSync("moteur/donnees.json", "utf8")), PARAMETRES_DEFAUT);
const pass = sim.macro.plafond_securite_sociale.valeur(2020);
// Ce que le compte du système 2 (part salariale) reçoit de la ligne de 2020.
const recu = (revenu) => sim.constructeur.cotisationAnnuelle(new Carriere({
  annee_naissance: 1970, sexe: "H", age_liquidation: 64, jour_naissance: 1,
  lignes: [new AnneeCarriere({ annee: 2020, revenu, affiliation: "salarie_prive_cadre" })],
}), 2020).cotisation;
const entier = recu(2 * pass), plafonne = recu(pass);
console.log(`plafond 2020 : ${pass} € ; salaire entier : ${2 * pass} €`);
console.log(`salaire entier : ${entier.toFixed(2)} € (${(100 * entier / pass).toFixed(3)} % d'un plafond)`);
console.log(`relevé plafonné : ${plafonne.toFixed(2)} € (${(100 * plafonne / pass).toFixed(3)} % d'un plafond)`);
console.log(`part reçue : ${(100 * plafonne / entier).toFixed(1)} %`);
```

**Ce qu'il rend** :

```
plafond 2020 : 41136 € ; salaire entier : 82272 €
salaire entier : 8014.94 € (19.484 % d'un plafond)
relevé plafonné : 4297.89 € (10.448 % d'un plafond)
part reçue : 53.6 %
```

Le moteur et le calcul à la main tombent sur les mêmes montants, au centime.
