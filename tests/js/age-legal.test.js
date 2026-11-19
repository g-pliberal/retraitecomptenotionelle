/**
 * L'âge légal se lit dans les versions de sa fiche (note de décision 0009,
 * étape 2, deuxième session).
 *
 * Le portage ne lit plus la table fusionnée (`age_ouverture_requis.csv`) : il
 * lit, dans le paquet (`fiches_datees`), les versions de la fiche
 * `age_legal_par_generation`. La date d'effet de la pension choisit la
 * version, la génération sa ligne, et ce que la loi de 2025 laisse à sa
 * rédaction antérieure se lit dans la version de 2023.
 *
 * Les âges attendus viennent des textes : soixante ans jusqu'au 30 juin 2011
 * (R. 351-2) ; soixante ans et huit mois pour les nés en 1952 sous la loi
 * n° 2010-1330, soixante ans et neuf mois sous la loi n° 2011-1906
 * (D. 161-2-1-9, rédactions du 1er juillet et du 31 décembre 2011) ;
 * soixante-trois ans pour les nés en 1964 sous la loi n° 2023-270 ;
 * soixante-deux ans et neuf mois sous la loi n° 2025-1403, pour les pensions
 * prenant effet à compter du 1er septembre 2026.
 *
 * La recherche du premier départ se confronte à deux témoins : l'essai de
 * chaque premier du mois, de l'âge le plus bas que porte une version au plus
 * haut (premier rectificatif de la note), et la table fusionnée, que la
 * fabrique tire des mêmes versions. Aucune des quatre réformes n'a relevé
 * l'âge d'un assuré qui pouvait déjà partir : les trois rendent la même date.
 *
 *     node --test tests/js/age-legal.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { DateMois, enMois } from "../../moteur/js/calendrier.js";
import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import * as categories from "../../moteur/js/droit/categories.js";
import * as compter from "../../moteur/js/droit/compter.js";
import * as lesDeparts from "../../moteur/js/droit/departs.js";
import * as invalidite from "../../moteur/js/droit/invalidite.js";
import * as ouvrir from "../../moteur/js/droit/ouvrir.js";
import { AgesOuverture, FICHE_DE_L_AGE_LEGAL } from "../../moteur/js/regimes.js";
import { Simulateur } from "../../moteur/js/simulateur.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const EFFET = "liquidation.date_effet";

/** La table fusionnée que la fabrique tire des versions : génération -> âge. */
const TABLE = readFileSync(
  join(RACINE, "data/reference/legislation/age_ouverture_requis.csv"), "utf8")
  .split("\n").filter((ligne) => /^\d/.test(ligne))
  .map((ligne) => ligne.split(",")).map(([generation, age]) => [Number(generation), Number(age)]);

/**
 * L'âge de la table fusionnée, lue en escalier, au mois exact : le fichier
 * écrit 61.17 pour soixante et un ans et deux mois.
 */
function ageDeLaTable(generation) {
  let age = null;
  for (const [debut, valeur] of TABLE) {
    if (debut <= generation) {
      age = enMois(valeur) / 12;
    }
  }
  return age;
}

/** La génération d'un mois de naissance, comme la carrière l'écrit. */
function generationDe(annee, mois) {
  return Math.round((annee + (mois - 1) / 12) * 1000) / 1000;
}

/** Le premier jour d'un mois, AAAA-MM-01. */
function jour(date) {
  return `${String(date.annee).padStart(4, "0")}-${String(date.mois).padStart(2, "0")}-01`;
}

/** Le paquet, la fiche de l'âge légal retouchée par `retouche(fiche)`. */
function paquetRetouche(retouche) {
  const copie = structuredClone(paquet);
  retouche(copie.fiches_datees[FICHE_DE_L_AGE_LEGAL]);
  return copie;
}

function version(fiche, identifiant) {
  return fiche.versions.find((v) => v.id === identifiant);
}

/** Le moteur du droit en vigueur, sur ce paquet. */
function moteurSur(donnees, parametres = {}) {
  return new Simulateur(donnees, { ...PARAMETRES_DEFAUT, ...parametres }).scenarioActuel;
}

/**
 * Le témoin de la recherche : chaque premier du mois, de l'âge le plus bas
 * que porte une version au plus haut, le premier où l'assuré a l'âge que la
 * version de ce jour-là lui oppose ; `null` quand aucun n'ouvre le droit.
 */
function premierDepartMoisParMois(ages, generation, origine, [bas, haut]) {
  for (let mois = enMois(bas); mois <= enMois(haut); mois += 1) {
    const effet = origine.plusMois(mois);
    const lu = ages.aLEffet(jour(effet)).age(generation);
    if (lu !== null && origine.plusMois(enMois(lu[0])).rang <= effet.rang) {
      return effet;
    }
  }
  return null;
}

const ages = new AgesOuverture(paquet);
const moteur = moteurSur(paquet);

test("le paquet porte la fiche de l'âge légal, ses six versions choisies à la date d'effet", () => {
  const fiche = paquet.fiches_datees[FICHE_DE_L_AGE_LEGAL];
  assert.ok(fiche, "la fiche manque à fiches_datees");
  assert.deepEqual(fiche.dates_qui_decident, [EFFET]);
  assert.equal(fiche.versions.length, 6);
});

test("la date d'effet choisit la version, la génération sa ligne", () => {
  // Soixante ans jusqu'au 30 juin 2011, quelle que soit la génération.
  assert.deepEqual(ages.aLEffet("1984-01-01").age(1924), [60, 1]);
  assert.deepEqual(ages.aLEffet("2011-06-01").age(1955), [60, 2]);
  // La loi de 2010, puis celle de 2011, pour les nés en 1952.
  assert.deepEqual(ages.aLEffet("2011-08-01").age(1952), [60 + 8 / 12, 3]);
  assert.deepEqual(ages.aLEffet("2012-01-01").age(1952), [60.75, 3]);
  // La loi de 2023, puis sa suspension, pour les nés en 1964.
  assert.deepEqual(ages.aLEffet("2025-01-01").age(1964), [63, 3]);
  assert.deepEqual(ages.aLEffet("2026-09-01").age(1964), [62.75, 3]);
  // Les nés du premier trimestre de 1965 gardent 62 ans et 9 mois, ceux
  // d'avril ont 63 ans.
  assert.deepEqual(ages.aLEffet("2028-01-01").age(generationDe(1965, 3)), [62.75, 3]);
  assert.deepEqual(ages.aLEffet("2028-01-01").age(generationDe(1965, 4)), [63, 3]);
});

test("la loi de 2025 renvoie les nés avant le 1er septembre 1961 à sa rédaction antérieure", () => {
  const suspension = version(paquet.fiches_datees[FICHE_DE_L_AGE_LEGAL], "suspension_de_2025");
  assert.equal(suspension.table[0][0], 1961.667, "la loi n'écrit que les nés depuis septembre 1961");
  // Né en août 1961 : soixante-deux ans, que dit D. 161-2-1-9 sous la loi de
  // 2023 ; né en 1953 : soixante et un ans et deux mois.
  assert.deepEqual(ages.aLEffet("2027-01-01").age(generationDe(1961, 8)), [62, 3]);
  assert.deepEqual(ages.aLEffet("2027-01-01").age(generationDe(1961, 9)), [62.25, 3]);
  assert.deepEqual(ages.aLEffet("2027-01-01").age(1953), [61 + 2 / 12, 3]);
});

/** Les générations que chaque réforme a déplacées, d'après son texte. */
const REFORMES = {
  "loi n° 2010-1330 (nés du 1er juillet 1951 à 1955)": [[1951, 7], [1956, 12]],
  "loi n° 2011-1906 (nés de 1952 à 1955)": [[1952, 1], [1955, 12]],
  "loi n° 2023-270 (nés du 1er septembre 1961 à 1968)": [[1961, 9], [1968, 12]],
  "loi n° 2025-1403 (nés de 1964 à 1968)": [[1964, 1], [1969, 12]],
  "toutes les générations de 1900 à 1975": [[1900, 1], [1975, 12]],
};

for (const [reforme, [[debut, moisDebut], [fin, moisFin]]] of Object.entries(REFORMES)) {
  test(`la recherche du premier départ rend la date de la table : ${reforme}`, () => {
    const bornes = [60, 64];
    let essais = 0;
    for (let rang = debut * 12 + moisDebut - 1; rang <= fin * 12 + moisFin - 1; rang += 1) {
      const naissance = DateMois.depuisRang(rang);
      const generation = generationDe(naissance.annee, naissance.mois);
      // Né le 1er, les âges se comptent du mois de naissance ; sinon du suivant.
      for (const origine of [naissance, naissance.plusMois(1)]) {
        const cherche = ages.premierDepart(generation, origine);
        const parLaTable = origine.plusMois(enMois(ageDeLaTable(generation)));
        const moisParMois = premierDepartMoisParMois(ages, generation, origine, bornes);
        assert.equal(jour(cherche.date), jour(parLaTable),
          `né en ${jour(naissance)} : la recherche et la table`);
        assert.equal(jour(cherche.date), jour(moisParMois),
          `né en ${jour(naissance)} : la recherche et l'essai de chaque mois`);
        assert.equal(cherche.age[0], ageDeLaTable(generation));
        essais += 1;
      }
    }
    assert.ok(essais >= 96);
  });
}

test("l'âge légal de l'assuré est celui de la version sous laquelle son droit s'ouvre : la table, à chaque génération", () => {
  for (let rang = 1900 * 12; rang < 1976 * 12; rang += 1) {
    const naissance = DateMois.depuisRang(rang);
    const generation = generationDe(naissance.annee, naissance.mois);
    assert.equal(ages.age(generation)[0], ageDeLaTable(generation), `génération ${generation}`);
    assert.equal(ages.valeur(generation)[0], ageDeLaTable(generation));
  }
  // Au-delà de la dernière ligne, la dernière vaut ; l'année seule est janvier.
  assert.equal(ages.age(1990)[0], 64);
  assert.equal(ages.age(1964)[0], 62.75);
});

test("le droit ne se referme pas : passé le premier départ, chaque version l'ouvre encore", () => {
  for (let rang = 1923 * 12; rang < 1976 * 12; rang += 1) {
    const naissance = DateMois.depuisRang(rang);
    const generation = generationDe(naissance.annee, naissance.mois);
    const origine = naissance.plusMois(1);
    const premier = ages.premierDepart(generation, origine).date;
    for (let mois = 0; mois <= 60; mois += 1) {
      const effet = premier.plusMois(mois);
      const lu = ages.aLEffet(jour(effet)).age(generation);
      assert.ok(origine.plusMois(enMois(lu[0])).rang <= effet.rang,
        `né en ${jour(naissance)} : droit refermé au ${jour(effet)}`);
    }
  }
});

test("les lecteurs du moteur lisent les versions : une version retouchée les déplace tous", () => {
  // La table fusionnée ôtée du paquet, le moteur répond encore.
  const sansTable = structuredClone(paquet);
  delete sansTable.ages_ouverture;
  const nu = moteurSur(sansTable);
  const simulateur = new Simulateur(paquet, { ...PARAMETRES_DEFAUT });
  const carriere = simulateur.carriereSimple({
    sexe: "F", niveau_salaire: 1.0, annee_naissance: 1970, mois_naissance: 3, jour_naissance: 12,
    affiliation: "salarie_prive_non_cadre", age_debut: 22, age_liquidation: 64,
  });
  assert.equal(categories.ageLegal(nu, carriere), 64);
  // La version en vigueur retouchée : soixante-cinq ans dès la génération 1969.
  const retouche = moteurSur(paquetRetouche((fiche) => {
    version(fiche, "suspension_de_2025").table.at(-1)[2] = 65;
  }));
  const periode = retouche.catalogue.obtenir("regime_general").periode(2035);
  for (const [lecteur, lu] of [
    ["categories.ageLegal", (m) => categories.ageLegal(m, carriere)],
    ["departs.ageLegal", (m) => lesDeparts.ageLegal(m, carriere)],
    ["invalidite.ageDeLaFiche", (m) => invalidite.ageDeLaFiche(
      m, carriere, invalidite.AGE_LEGAL_PAR_GENERATION)],
    ["ouvrir.ageOuvertureCommun", (m) => ouvrir.ageOuvertureCommun(m, periode, carriere)],
    ["compter.ageDeSuppression", (m) => compter.ageDeSuppression(m, carriere, "fiche",
      { id: "version", parametres: { age_de_suppression: compter.AGE_LEGAL } })[0]],
    ["ouvrir.ageOuvertureDroit", (m) => ouvrir.ageOuvertureDroit(m, carriere)],
    ["agesOuverture.age", (m) => m.agesOuverture.age(carriere.generation)[0]],
  ]) {
    assert.equal(lu(moteur), 64, `${lecteur}, sur le paquet du dépôt`);
    assert.equal(lu(retouche), 65, `${lecteur}, la version retouchée`);
  }
  // Et le premier départ que le moteur date la suit : 64 ans le 1er avril
  // 2034, 65 ans le 1er avril 2035.
  const tot = simulateur.carriereSimple({
    sexe: "F", niveau_salaire: 1.0, annee_naissance: 1970, mois_naissance: 3, jour_naissance: 12,
    affiliation: "salarie_prive_non_cadre", age_debut: 22, age_liquidation: 62,
  });
  const unite = new Set(["regime_general"]);
  assert.equal(jour(lesDeparts.ouvertureDe(moteur, tot, unite)), "2034-04-01");
  assert.equal(jour(lesDeparts.ouvertureDe(retouche, tot, unite)), "2035-04-01");
});

test("une réforme fictive ne change qu'une version, et le moteur la suit à sa date d'effet", () => {
  // Une loi fictive : soixante-cinq ans pour les nés à compter de 1970, pour
  // les pensions prenant effet à compter du 1er septembre 2030 ; elle laisse
  // les autres à sa rédaction antérieure.
  const fictif = paquetRetouche((fiche) => {
    version(fiche, "suspension_de_2025").bornes[EFFET][1] = "2030-09-01";
    fiche.versions.push({
      id: "reforme_fictive", bornes: { [EFFET]: ["2030-09-01", null] }, exception_de: null,
      texte: null, parametres: {}, table: [[1970, null, 65, 3]],
      redaction_anterieure: { version: "suspension_de_2025", generations: [null, 1970] },
    });
  });
  // Seule la version neuve s'ajoute, et la précédente se ferme : rien d'autre.
  const avant = paquet.fiches_datees[FICHE_DE_L_AGE_LEGAL].versions;
  const apres = fictif.fiches_datees[FICHE_DE_L_AGE_LEGAL].versions;
  assert.deepEqual(apres.slice(0, 5), avant.slice(0, 5));
  assert.deepEqual({ ...apres[5], bornes: avant[5].bornes }, avant[5]);
  assert.equal(apres.length, 7);
  const reformes = new AgesOuverture(fictif);
  // Avant sa date d'effet, chaque génération garde son âge.
  for (const effet of ["2011-08-01", "2020-01-01", "2025-01-01", "2030-08-01"]) {
    for (let generation = 1940; generation <= 1975; generation += 0.25) {
      assert.deepEqual(reformes.aLEffet(effet).age(generation), ages.aLEffet(effet).age(generation));
    }
  }
  // Après, elle ne déplace que les nés depuis 1970, qui ne pouvaient pas
  // encore partir : 65 ans, au lieu de 64.
  assert.deepEqual(reformes.aLEffet("2031-01-01").age(1969), [64, 3]);
  assert.deepEqual(reformes.aLEffet("2031-01-01").age(1970), [65, 3]);
  assert.equal(reformes.age(1969.5)[0], 64);
  assert.equal(reformes.age(1970)[0], 65);
  assert.equal(jour(reformes.premierDepart(1970, new DateMois(1970, 2)).date), "2035-02-01");
  // Le moteur entier la suit.
  const simulateur = new Simulateur(fictif, { ...PARAMETRES_DEFAUT });
  const carriere = simulateur.carriereSimple({
    sexe: "H", niveau_salaire: 1.0, annee_naissance: 1970, mois_naissance: 1, jour_naissance: 20,
    affiliation: "salarie_prive_non_cadre", age_debut: 22, age_liquidation: 63,
  });
  assert.equal(jour(lesDeparts.ouvertureDe(
    simulateur.scenarioActuel, carriere, new Set(["regime_general"]))), "2035-02-01");
});

test("une loi qui relève l'âge d'un assuré qui pouvait partir : la recherche garde le premier départ, et ne le déduit plus de l'âge", () => {
  // Fictive : soixante-six ans pour tous à compter du 1er janvier 2030. Né en
  // mars 1966, l'assuré pouvait partir à 63 ans et 3 mois, le 1er juillet
  // 2029 ; la table, elle, ne lui ouvrirait qu'à 66 ans.
  const releve = new AgesOuverture(paquetRetouche((fiche) => {
    version(fiche, "suspension_de_2025").bornes[EFFET][1] = "2030-01-01";
    fiche.versions.push({
      id: "reforme_fictive", bornes: { [EFFET]: ["2030-01-01", null] }, exception_de: null,
      texte: null, parametres: { age: 66 }, fiabilite: 0,
    });
  }));
  const premier = releve.premierDepart(generationDe(1966, 3), new DateMois(1966, 4));
  assert.equal(jour(premier.date), "2029-07-01");
  assert.equal(premier.version, "suspension_de_2025");
  assert.equal(releve.aLEffet("2030-01-01").age(generationDe(1966, 3))[0], 66);
  // Né en 1967, il n'avait pas encore l'âge : la loi neuve lui oppose le sien.
  assert.equal(jour(releve.premierDepart(1967, new DateMois(1967, 2)).date), "2033-02-01");
});

test("une loi qui abaisse l'âge ouvre le droit à sa date d'effet, pas avant", () => {
  // Fictive : soixante ans pour tous à compter du 1er janvier 2030. Né en
  // janvier 1968, soixante ans le 1er février 2028 : le droit s'ouvre le
  // 1er janvier 2030, premier jour où un texte le lui donne.
  const abaisse = new AgesOuverture(paquetRetouche((fiche) => {
    version(fiche, "suspension_de_2025").bornes[EFFET][1] = "2030-01-01";
    fiche.versions.push({
      id: "reforme_fictive", bornes: { [EFFET]: ["2030-01-01", null] }, exception_de: null,
      texte: null, parametres: { age: 60 }, fiabilite: 0,
    });
  }));
  const premier = abaisse.premierDepart(1968, new DateMois(1968, 2));
  assert.equal(jour(premier.date), "2030-01-01");
  assert.equal(jour(premierDepartMoisParMois(abaisse, 1968, new DateMois(1968, 2), [60, 64])),
    "2030-01-01");
});

test("la recherche dit quand aucune date n'ouvre le droit", () => {
  // La dernière version fermée, plus aucun texte ne répond au-delà.
  const ferme = new AgesOuverture(paquetRetouche((fiche) => {
    version(fiche, "suspension_de_2025").bornes[EFFET][1] = "2030-01-01";
  }));
  assert.equal(ferme.premierDepart(1975, new DateMois(1975, 2)), null);
  assert.equal(ferme.age(1975), null);
  assert.equal(jour(ferme.premierDepart(1964, new DateMois(1964, 2)).date), "2026-11-01");
  assert.throws(() => ferme.aLEffet("2031-01-01"),
    /age_legal_par_generation : aucune version.*2031-01-01/);
});

test("un renvoi sans cible ou qui boucle arrête le calcul, et nomme ses fiches", () => {
  const sansCible = new AgesOuverture(paquetRetouche((fiche) => {
    version(fiche, "suspension_de_2025").redaction_anterieure.version = "loi_absente";
  }));
  assert.throws(() => sansCible.aLEffet("2027-01-01").age(1960),
    /age_legal_par_generation\.suspension_de_2025 : .*« loi_absente »/);
  // Ce qu'elle écrit elle-même se lit encore.
  assert.deepEqual(sansCible.aLEffet("2027-01-01").age(1964), [62.75, 3]);
  const boucle = new AgesOuverture(paquetRetouche((fiche) => {
    const loi = version(fiche, "loi_de_2023");
    loi.table = loi.table.filter(([debut]) => debut >= 1961.667);
    loi.redaction_anterieure = { version: "suspension_de_2025", generations: [null, 1961.667] };
  }));
  assert.throws(() => boucle.aLEffet("2027-01-01").age(1960),
    /age_legal_par_generation\.suspension_de_2025.*age_legal_par_generation\.loi_de_2023.*bouclent/);
  // La fiche ôtée du paquet, le moteur le dit plutôt que de répondre soixante ans.
  const sansFiche = structuredClone(paquet);
  delete sansFiche.fiches_datees[FICHE_DE_L_AGE_LEGAL];
  assert.throws(() => new AgesOuverture(sansFiche).age(1960), /age_legal_par_generation/);
});

test("sous un droit contrefactuel, la copie d'avant réforme recouvre encore les versions", () => {
  const au31Aout = moteurSur(paquet, { droit_contrefactuel: "au_31_aout_2023" });
  const sansSuspension = moteurSur(paquet, { droit_contrefactuel: "loi_2023_sans_suspension" });
  // 62 ans dès 1955 sous le droit du 31 août 2023 ; 63 ans pour 1964 sous la
  // loi de 2023 ; en deçà de la copie, les versions répondent.
  assert.equal(au31Aout.agesOuverture.age(1968)[0], 62);
  assert.equal(sansSuspension.agesOuverture.age(1964)[0], 63);
  assert.equal(sansSuspension.agesOuverture.age(1953)[0], 61 + 2 / 12);
  assert.equal(au31Aout.agesOuverture.age(1953)[0], 61 + 2 / 12);
});
