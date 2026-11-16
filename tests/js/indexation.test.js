/**
 * Les règles d'indexation et leurs séries (action 161, quatrième vague) : ce
 * que `tests/test_moteur.py` éprouvait sur `Indexation` et `DonneesMacro` du
 * moteur Python, éprouvé sur ceux du site.
 *
 * Aucune valeur attendue ne vient du moteur : chaque test dit une identité de
 * la règle — le minimum, la médiane, la moyenne des trois taux, la moyenne
 * géométrique d'une fenêtre de lissage, le plancher posé après elle — ou un
 * ordre que les séries publiées imposent sur 1941-2025, et les rares niveaux
 * écrits sont ceux que l'INSEE et la caisse publient.
 *
 *     node --test tests/js/indexation.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { ModeIndexation, PARAMETRES_DEFAUT, avec } from "../../moteur/js/config.js";
import { Indexation } from "../../moteur/js/indexation.js";
import { DonneesMacro, HEURES_ANNUELLES_SMIC } from "../../moteur/js/macro.js";
import { Fiabilite } from "../../moteur/js/serie.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur", "donnees.json"), "utf8"));
const macro = new DonneesMacro(paquet);

const MODES = Object.values(ModeIndexation);

/** L'indexation sous les réglages de référence, retouchés de `modifications`. */
const indexation = (modifications = {}) => new Indexation(macro, avec(PARAMETRES_DEFAUT, modifications));

const sous = (mode, autres = {}) => indexation({ mode_indexation: mode, ...autres });

const cumul = (mode, debut = 1941, fin = 2025, autres = {}) => sous(mode, autres).coefficient(debut, fin);

/** Comme `pytest.approx` : 10⁻⁶ relatif par défaut. */
const proche = (lu, attendu, { relatif = 1e-6, absolu = 1e-12 } = {}, message = "") => assert.ok(
  Math.abs(lu - attendu) <= Math.max(absolu, relatif * Math.abs(attendu)),
  `${message}${lu} au lieu de ${attendu}`);

const annees = (debut, fin) => Array.from({ length: fin - debut + 1 }, (_, i) => debut + i);

// -- les trois taux et leur statistique ----------------------------------------

test("le triple lock inversé retient bien le minimum", () => {
  // Le mode est nommé : ce n'est plus le défaut du modèle depuis que celui-ci
  // est la règle d'équilibre.
  const regle = sous(ModeIndexation.TRIPLE_LOCK_INVERSE);
  for (const annee of [1975, 1990, 2005, 2020]) {
    const taux = regle.taux(annee);
    assert.equal(taux.taux, Math.min(taux.inflation, taux.salaire_moyen, taux.productivite));
  }
});

test("le triple lock inversé est dominé par la productivité en forte inflation", () => {
  const regle = sous(ModeIndexation.TRIPLE_LOCK_INVERSE);
  for (const annee of [1974, 1980, 1981]) {
    assert.equal(regle.taux(annee).terme_retenu, "productivite_reelle");
  }
});

test("la règle littérale détruit le pouvoir d'achat des comptes anciens", () => {
  // Constat central du modèle : la règle littérale revalorise les comptes d'un
  // facteur voisin de 5 quand les prix sont multipliés par plus de 300 ; la
  // variante nominale en conserve l'essentiel.
  const prix = macro.coefficientPrix(1941, 2025);
  const litteral = cumul(ModeIndexation.TRIPLE_LOCK_INVERSE);
  const nominal = cumul(ModeIndexation.TRIPLE_LOCK_INVERSE_NOMINAL);
  assert.ok(litteral / prix < 0.05, "la règle littérale devrait tout écraser");
  assert.ok(nominal / prix > 0.50, "la variante nominale devrait préserver l'essentiel");
  assert.ok(nominal > 10 * litteral);
});

test("la médiane retient le terme du milieu", () => {
  const regle = sous(ModeIndexation.MEDIANE_TROIS_TAUX);
  for (const annee of annees(1941, 2025)) {
    const taux = regle.taux(annee);
    const trois = [taux.inflation, taux.salaire_moyen, taux.productivite].sort((a, b) => a - b);
    assert.equal(taux.taux, trois[1]);
    assert.ok(["inflation", "salaire_moyen", "productivite_reelle"].includes(taux.terme_retenu));
  }
});

test("la moyenne est la moyenne arithmétique des trois", () => {
  const regle = sous(ModeIndexation.MOYENNE_TROIS_TAUX);
  for (const annee of annees(1941, 2025)) {
    const taux = regle.taux(annee);
    proche(taux.taux, (taux.inflation + taux.salaire_moyen + taux.productivite) / 3);
    assert.equal(taux.terme_retenu, "moyenne");
  }
});

test("la médiane et la moyenne adoucissent la règle année par année", () => {
  // Le minimum est par construction le plus bas des trois : la médiane et la
  // moyenne lui sont supérieures ou égales, et restent sous le maximum.
  const minimum = sous(ModeIndexation.TRIPLE_LOCK_INVERSE);
  const mediane = sous(ModeIndexation.MEDIANE_TROIS_TAUX);
  const moyenne = sous(ModeIndexation.MOYENNE_TROIS_TAUX);
  for (const annee of annees(1941, 2025)) {
    const bas = minimum.taux(annee);
    const haut = Math.max(bas.inflation, bas.salaire_moyen, bas.productivite);
    for (const autre of [mediane, moyenne]) {
      const taux = autre.taux(annee).taux;
      assert.ok(bas.taux <= taux && taux <= haut, `${annee}`);
    }
  }
});

test("la médiane dépasse les prix quand la moyenne reste dessous", () => {
  // La médiane est presque toujours l'un des deux taux nominaux ; la moyenne
  // incorpore un tiers de productivité réelle, même à vingt points d'inflation.
  const prix = macro.coefficientPrix(1941, 2025);
  const mediane = cumul(ModeIndexation.MEDIANE_TROIS_TAUX);
  const moyenne = cumul(ModeIndexation.MOYENNE_TROIS_TAUX);
  const litteral = cumul(ModeIndexation.TRIPLE_LOCK_INVERSE);
  assert.ok(mediane > prix && prix > moyenne && moyenne > litteral);
});

// -- la revalorisation des arrêtés ---------------------------------------------

test("la revalorisation portée au compte sert les coefficients des arrêtés", () => {
  // Année par année, le taux est le rapport de deux années consécutives dans
  // une colonne récente publiée par la caisse ; pour une liquidation de
  // janvier 1955, le salaire de 1954 n'avait encore reçu aucune revalorisation.
  const regle = sous(ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE);
  for (const annee of [1955, 1975, 1986, 1987, 2000, 2024, 2025]) {
    const taux = regle.taux(annee);
    proche(taux.taux, macro.coefficientRevalorisationParRapport(annee - 1, annee) - 1);
    assert.equal(taux.terme_retenu, "revalorisation_legale");
  }
  assert.equal(macro.coefficientRevalorisationPorteeAuCompte(1954, 1955), 1.0);
});

test("la composition annuelle ne dérive pas des colonnes publiées", () => {
  // La caisse arrondit à trois décimales, le moteur compose année par année :
  // 0,04 % sur quatre-vingt-quatre ans.
  proche(cumul(ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE),
    macro.coefficientRevalorisationPorteeAuCompte(1941, 2025), { relatif: 0.001 });
});

test("l'indexation sur les prix n'est pas la règle du droit positif", () => {
  // Le régime général ne revalorise sur les prix que depuis 1987 : avant, les
  // arrêtés suivaient les salaires.
  const legale = cumul(ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE);
  const prix = cumul(ModeIndexation.PRIX);
  const salaires = cumul(ModeIndexation.SALAIRES);
  assert.ok(legale > 3.5 * prix, "les arrêtés ont suivi les salaires jusqu'en 1986");
  assert.ok(legale < salaires, "et les prix depuis 1987");
  // Depuis la bascule de 1987, les deux règles se rejoignent.
  proche(cumul(ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE, 1990),
    cumul(ModeIndexation.PRIX, 1990), { relatif: 0.10 });
});

// -- la masse salariale --------------------------------------------------------

test("la masse salariale est le salaire moyen plus l'emploi", () => {
  // L'emploi salarié a été multiplié par 2,14 entre 1950 et 2025 (INSEE).
  const rapport = cumul(ModeIndexation.MASSE_SALARIALE, 1950) / cumul(ModeIndexation.SALAIRES, 1950);
  proche(rapport, 2.14, { absolu: 0.05, relatif: 0 });
});

test("la masse salariale est la règle la plus généreuse", () => {
  const coefficients = new Map(MODES.map((mode) => [mode, cumul(mode)]));
  const masse = coefficients.get(ModeIndexation.MASSE_SALARIALE);
  assert.equal(masse, Math.max(...coefficients.values()));
  assert.ok(masse > coefficients.get(ModeIndexation.SALAIRES));
  assert.ok(masse > 10 * macro.coefficientPrix(1941, 2025));
});

test("le cumul du PIB lissé doit son avance à la moyenne mobile", () => {
  const masse = cumul(ModeIndexation.MASSE_SALARIALE);
  const brut = cumul(ModeIndexation.PIB_NOMINAL);
  const lisse = cumul(ModeIndexation.PIB_NOMINAL, 1941, 2025, { lissage_indexation: 5 });
  assert.ok(brut < masse && masse < lisse);
});

test("la masse salariale est certifiée depuis 1950", () => {
  assert.equal(macro.masse_salariale.fiabiliteMinimaleSur(1950, 2025), Fiabilite.CERTIFIEE);
  assert.equal(macro.masse_salariale.fiabilite(1935), Fiabilite.ESTIMEE);
});

// -- le lissage et le plancher -------------------------------------------------

test("le lissage est la moyenne géométrique de la fenêtre", () => {
  for (const mode of [ModeIndexation.PIB_NOMINAL, ModeIndexation.MASSE_SALARIALE,
    ModeIndexation.TRIPLE_LOCK_INVERSE]) {
    const brut = sous(mode);
    const lisse = sous(mode, { lissage_indexation: 5 });
    for (const annee of [1975, 2000, 2020, 2025]) {
      let produit = 1.0;
      for (const a of annees(annee - 4, annee)) {
        produit *= 1 + brut.taux(a).taux;
      }
      proche(lisse.taux(annee).taux, produit ** (1 / 5) - 1, {}, `${mode} en ${annee} : `);
    }
  }
});

test("le lissage absorbe le trou de 2020", () => {
  const brut = macro.pib_nominal.valeur(2020);
  const lisse = sous(ModeIndexation.PIB_NOMINAL, { lissage_indexation: 5 }).taux(2020).taux;
  assert.ok(brut < 0 && lisse > 0);
});

test("le lissage ne change rien à une fenêtre d'un an", () => {
  for (const mode of MODES) {
    assert.equal(cumul(mode), cumul(mode, 1941, 2025, { lissage_indexation: 1 }), mode);
  }
});

test("la fenêtre de lissage est tronquée au début des séries", () => {
  const regle = sous(ModeIndexation.PIB_NOMINAL, { lissage_indexation: 5 });
  const premiere = macro.inflation.premiereAnnee;
  proche(regle.taux(premiere).taux, macro.pib_nominal.valeur(premiere));
  // et une carrière ancienne se calcule sans lever
  assert.ok(regle.coefficient(premiere, 2025) > 1.0);
});

test("le plancher s'applique après le lissage", () => {
  const regle = sous(ModeIndexation.TRIPLE_LOCK_INVERSE,
    { lissage_indexation: 5, plancher_indexation: 0.0 });
  for (const annee of annees(1941, 2025)) {
    assert.ok(regle.taux(annee).taux >= 0.0, `${annee}`);
  }
});

test("le lissage supprime les années où attendre fait perdre", () => {
  // Une cotisation de 1950 vaut son coefficient cumulé : sur le PIB nominal
  // brut, il recule certaines années ; le lissage retire ce pouvoir au
  // calendrier.
  const reculs = (lissage) => {
    const regle = sous(ModeIndexation.PIB_NOMINAL, { lissage_indexation: lissage });
    return annees(1951, 2025).filter(
      (liquidation) => regle.coefficient(1950, liquidation) > regle.coefficient(1950, liquidation + 1),
    ).length;
  };
  assert.ok(reculs(1) > 0);
  assert.equal(reculs(3), 0);
  assert.equal(reculs(5), 0);
});

test("le lissage gonfle les cumuls longs sans toucher à l'assiette", () => {
  const brut = cumul(ModeIndexation.PIB_NOMINAL);
  const lisse = cumul(ModeIndexation.PIB_NOMINAL, 1941, 2025, { lissage_indexation: 5 });
  assert.ok(lisse / brut > 1.15 && lisse / brut < 1.30);
});

test("l'indexation sur les prix reproduit l'inflation", () => {
  proche(cumul(ModeIndexation.PRIX, 1980, 2020), macro.coefficientPrix(1980, 2020));
});

test("le plancher d'indexation est respecté", () => {
  const regle = indexation({ plancher_indexation: 0.0 });
  for (const annee of annees(1941, 2025)) {
    assert.ok(regle.taux(annee).taux >= 0.0, `${annee}`);
  }
});

test("le coefficient ne revalorise pas l'année du versement", () => {
  const regle = indexation();
  assert.equal(regle.coefficient(2000, 2000), 1.0);
  proche(regle.coefficient(2000, 2001), 1 + regle.taux(2001).taux);
});

// -- le SMIC annuel ------------------------------------------------------------

test("le SMIC annuel suit la durée légale", () => {
  // Le salaire horaire moyen de l'année fois la durée légale : 173,33 heures
  // par mois jusqu'en 1981, 169 jusqu'en 1999, 151,67 depuis 2000 (INSEE).
  proche(macro.smicAnnuel(1951), 282.48);
  proche(macro.smicAnnuel(1999), 12_511.97);
  proche(macro.smicAnnuel(2000), 11_478.40);
  // 2024 : 11,65 € de janvier à octobre, 11,88 € en novembre et décembre.
  proche(macro.smicAnnuel(2024), 1820 * (10 * 11.65 + 2 * 11.88) / 12, { absolu: 0.005, relatif: 0 });
  // Au-delà de la dernière année publiée, 1 820 heures du barème.
  const derniere = macro._smicAnnuelPublie.derniereAnnee;
  proche(macro.smicAnnuel(derniere + 2),
    HEURES_ANNUELLES_SMIC * macro.smic_horaire.valeur(derniere + 2));
  // Avant le SMIG, le rapport de 1951 au salaire moyen.
  proche(macro.smicAnnuel(1945) / macro.smicAnnuel(1951),
    1 / macro.coefficientSalaireMoyen(1945, 1951));
});
