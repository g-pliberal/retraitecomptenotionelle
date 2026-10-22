/**
 * Les indicateurs de cycle de vie : leurs définitions, sur des flux faits à la main.
 *
 * `moteur/js/cycle-de-vie.js` voit une carrière, sous chacun des six
 * systèmes, comme deux chroniques — ce qu'elle verse, ce qu'elle reçoit — et en
 * tire la durée de retraite, le taux de récupération, le rendement interne et le
 * patrimoine retraite (action 138, étape 9). Ces essais tiennent les
 * définitions : un rendement qu'on connaît d'avance se retrouve, une durée de
 * retraite est celle que la convention dit, un taux de récupération est le
 * rapport de deux sommes, et chaque système reçoit et verse ce que le modèle lui
 * prête ; après impôt, l'impôt de chaque année est celui du foyer qui la déclare
 * (action 138, étape 5) ; à chaque âge de départ, de l'âge d'ouverture à
 * l'annulation de la décote, en net, sous les trois productivités du COR ;
 * l'âge d'équilibre, où une génération retrouve le diviseur ou la part de vie de
 * la référence du compte ; la pension du départ par étage et le revenu autour du
 * départ, les tableaux 1 et 2 de Typfallsmodellen.
 * La confrontation aux chiffres publiés par le COR, TRAJECTOiRE, l'OCDE, l'ETK
 * et le simulateur du COR est dans `tests/test_cycle_de_vie_references.py`.
 *
 * Ils viennent de `tests/test_cycle_de_vie.py`, au retrait du jumeau Python
 * (action 161) : chacun de ses tests, traduit contre le portage, y garde ses
 * valeurs attendues, ses tolérances et ses assertions ; les deux qui ne portent
 * que sur le jeu de projection de `DonneesMacro`, du Python, restent en Python.
 *
 *     node --test tests/js/cycle-de-vie.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { PROFIL_AUTOMATIQUE, PROFIL_SMIC } from "../../moteur/js/carriere.js";
import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { Contexte } from "../../moteur/js/contexte.js";
import { contributionsDUneCarriere } from "../../moteur/js/contributions-equilibre.js";
// `depart` s'y importe sous le nom `departDe` : comme dans le Python, `depart`
// nomme aussi, dans les essais, l'année ou l'âge du départ.
import {
  ageDeDecesCor, ageDEquilibre, ageDePartDeVieConstante, agesBalayes, balayageDUneCarriere,
  beneficesParAnnee, Convention, conventionApresImpot, conventionNette, depart as departDe,
  derniereAnneePleine, diviseurA, Flux, fluxDesSystemes, impotsParAnnee, indicateurs,
  indicateursDesSystemes, majorationExoneree, minimumVieillesse, partDeVie,
  partsImposablesParAnnee, PensionParEtage, pensionAuDepart, pensionParEtage, pensionsEsperees,
  prelevementsParAnnee, referenceDuCompte, remplacementApresImpot, rendementInterne, revenusAutourDuDepart,
  revenusDActivite, revenusImposables, revenusNets, SCENARIOS, tauxDePrelevement,
} from "../../moteur/js/cycle-de-vie.js";
import { ageTauxPleinDroit } from "../../moteur/js/droit/ouvrir.js";
import {
  chargerBaremesImpotRevenu, croissanceMacro, Declarant, FRANC, Foyer, impotDuFoyer,
  taxeComplementaireDesRevenus,
} from "../../moteur/js/impot-revenu.js";
import { pow } from "../../moteur/js/libm.js";
import { pointFixe } from "../../moteur/js/pilote.js";
import { ficheDepuisBrut, indemnitesDeLaCarriere } from "../../moteur/js/remuneration.js";
import { faireVivre } from "../../moteur/js/revalorisation.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const contexte = new Contexte(paquet);
const simulateur = contexte.simulateur();

// -- ce que le Python écrit sans y penser --------------------------------------

/**
 * `obtenu == pytest.approx(attendu, rel=…, abs=…)` : l'écart au plus la
 * tolérance. Sans `rel` ni `abs`, la plus large de 1e-6 en relatif et de
 * 1e-12 ; `abs` seule, elle seule ; `rel` seule, la plus large d'elle et de
 * 1e-12 ; les deux, la plus large des deux. Un attendu infini ou indéfini
 * n'est proche que de lui-même. `message` dit le cas, comme le second membre
 * d'un `assert` du Python.
 */
function proche(obtenu, attendu, { rel = null, abs = null } = {}, message = "") {
  if (obtenu === attendu) return;
  const tolerance = rel === null && abs !== null ? abs
    : Math.max((rel ?? 1e-6) * Math.abs(attendu), abs ?? 1e-12);
  assert.ok(typeof obtenu === "number" && typeof attendu === "number"
    && Number.isFinite(attendu) && Math.abs(attendu - obtenu) <= tolerance,
  `${message === "" ? "" : `${message} : `}${obtenu} n'est pas ${attendu} ± ${tolerance}`);
}

/** `obtenu == pytest.approx({…})` : les mêmes clés, chaque valeur proche de la sienne. */
function procheDe(obtenu, attendu, options = {}) {
  assert.deepStrictEqual(new Set(Object.keys(obtenu)), new Set(Object.keys(attendu)));
  for (const [cle, valeurAttendue] of Object.entries(attendu)) {
    proche(obtenu[cle], valeurAttendue, options, cle);
  }
}

/** `obtenu == attendu` du Python, entre deux nombres ou deux booléens : 0 y égale -0. */
function egal(obtenu, attendu, message = "") {
  assert.ok(obtenu === attendu,
    `${message === "" ? "" : `${message} : `}${obtenu} n'est pas ${attendu}`);
}

/** Un nombre : `None < 1.0` lève en Python, quand `null < 1` est vrai en JavaScript. */
function nombre(x, message) {
  assert.equal(typeof x, "number",
    `${message === "" ? "" : `${message} : `}un nombre attendu, reçu ${x}`);
  return x;
}

/** `a < b`, `a > b`, `a <= b` et `a >= b` du Python, entre deux nombres. */
function inferieur(a, b, message = "") {
  assert.ok(nombre(a, message) < nombre(b, message),
    `${message === "" ? "" : `${message} : `}${a} < ${b}`);
}

function superieur(a, b, message = "") {
  assert.ok(nombre(a, message) > nombre(b, message),
    `${message === "" ? "" : `${message} : `}${a} > ${b}`);
}

function auPlus(a, b, message = "") {
  assert.ok(nombre(a, message) <= nombre(b, message),
    `${message === "" ? "" : `${message} : `}${a} <= ${b}`);
}

function auMoins(a, b, message = "") {
  assert.ok(nombre(a, message) >= nombre(b, message),
    `${message === "" ? "" : `${message} : `}${a} >= ${b}`);
}

/** `x is not None` du Python. */
function nonNul(x, message = "") {
  assert.ok(x !== null && x !== undefined, message === "" ? `${x}` : message);
}

/**
 * `serie[cle]` du Python, sur une `Map` ou un objet : une clé absente lève,
 * quand `get` rendrait `undefined`.
 */
function valeur(serie, cle) {
  const presente = serie instanceof Map ? serie.has(cle) : Object.hasOwn(serie, cle);
  assert.ok(presente, `clé absente : ${cle}`);
  return serie instanceof Map ? serie.get(cle) : serie[cle];
}

/** `range(debut, fin)` du Python. */
function range(debut, fin) {
  return Array.from({ length: Math.max(fin - debut, 0) }, (_, rang) => debut + rang);
}

/** `zip(valeurs, valeurs[1:])` du Python : chaque valeur et la suivante. */
function paires(valeurs) {
  return valeurs.slice(1).map((apres, rang) => [valeurs[rang], apres]);
}

/**
 * `sum` du Python, qui compense ses arrondis depuis la 3.12 (Neumaier) : les
 * valeurs attendues sont celles que le Python attendait, au bit près.
 */
function somme(valeurs) {
  let total = 0.0;
  let compensation = 0.0;
  for (const x of valeurs) {
    const t = total + x;
    compensation += Math.abs(total) >= Math.abs(x) ? (total - t) + x : (x - t) + total;
    total = t;
  }
  return compensation !== 0.0 && Number.isFinite(compensation) ? total + compensation : total;
}

/**
 * `round(x, chiffres)` du Python : la valeur binaire exacte de `x`, arrondie
 * au plus proche, une égalité exacte au chiffre pair.
 */
function arrondi(x, chiffres) {
  const [entiere, fraction] = Math.abs(x).toFixed(100).split(".");
  const reste = fraction.slice(chiffres);
  const moitie = `5${"0".repeat(reste.length - 1)}`;
  let garde = BigInt(entiere + fraction.slice(0, chiffres));
  if (reste > moitie || (reste === moitie && garde % 2n === 1n)) garde += 1n;
  const texte = garde.toString().padStart(chiffres + 1, "0");
  const resultat = Number(`${texte.slice(0, -chiffres)}.${texte.slice(-chiffres)}`);
  return x < 0 ? -resultat : resultat;
}

/** Une fixture de portée « module » : faite au premier essai qui la demande. */
function fixture(fabrique) {
  let faite = null;
  return () => (faite ??= { valeur: fabrique() }).valeur;
}

/** `dataclasses.replace` d'une `Convention`, que le portage ne fait que pour l'impôt (`avecLImpot`). */
function remplace(convention, champs) {
  return new Convention({ ...convention, ...champs });
}

// -- les cas types ------------------------------------------------------------

/**
 * Les deux cas types de `CAS_TYPES` que ces essais balaient, que le portage
 * n'a pas, recopiés de `src/retraite_notionnelle/castypes.py` : ce qui fait les
 * options de leur carrière d'un seul statut (`CasType.options`), tous deux
 * hommes, sans interruption, sans enfant, sans primes ni inaptitude, et l'âge
 * écrit d'où le pilote part (`age_liquidation`). Tous deux partent au taux
 * plein (`regle_liquidation`), sans décalage (`ecart_liquidation`), et n'ont
 * qu'un statut (`affiliation_avant_entree` vide) : leur `carriere_a` est la
 * `carriere_simple` de leurs options, sous les conventions du COR comme hors
 * d'elles, leur part des primes étant nulle.
 */
const CAS_TYPES = {
  smic_carriere_complete: {
    libelle: "Salarié au niveau du SMIC, carrière complète",
    affiliation: "salarie_prive_non_cadre", age_debut: 18, age_liquidation: 64,
    niveau_salaire: 1.0, profil_carriere: PROFIL_SMIC,
  },
  salaire_moyen: {
    libelle: "Salarié au salaire moyen",
    affiliation: "salarie_prive_non_cadre", age_debut: 21, age_liquidation: 64,
    niveau_salaire: 1.0, profil_carriere: PROFIL_AUTOMATIQUE,
  },
};

/**
 * `_cas(code)` : le cas type, sa carrière liquidée à un âge (`carriere_a`), et
 * l'âge que le pilote lui fixe (`age_liquidation_pour`, `pilote.age_de_depart`,
 * que le portage ne porte plus) : sous la règle `taux_plein`, le point fixe de
 * l'âge du taux plein, parti de l'âge écrit, par les jumeaux de `point_fixe` et
 * d'`age_taux_plein_droit`.
 */
function cas(code) {
  const fiche = CAS_TYPES[code];
  const options = (generation, ageLiquidation) => ({
    annee_naissance: generation, sexe: "H", affiliation: fiche.affiliation,
    age_debut: fiche.age_debut, age_liquidation: ageLiquidation,
    niveau_salaire: fiche.niveau_salaire, profil_carriere: fiche.profil_carriere,
    interruptions: new Map(), nombre_enfants: 0, part_primes: 0.0,
    identifiant: `${fiche.libelle} (génération ${generation})`,
  });
  const carriereA = (leSimulateur, generation, age) => leSimulateur.carriereSimple(
    options(generation, age));
  return {
    carriereA,
    ageLiquidationPour: (leSimulateur, generation) => pointFixe(fiche.age_liquidation,
      (age) => ageTauxPleinDroit(leSimulateur.scenarioActuel,
        carriereA(leSimulateur, generation, age))),
  };
}

// -- les carrières ------------------------------------------------------------

function comparaisonDe(leSimulateur, generation, {
  age_liquidation = 64, affiliation = "salarie_prive_non_cadre", sexe = "H",
} = {}) {
  return leSimulateur.simuler(leSimulateur.carriereSimple({
    annee_naissance: generation, sexe, affiliation, age_debut: 21, age_liquidation,
    niveau_salaire: 1.0, jour_naissance: 15,
  }));
}

/** Un salarié né en 1950, parti en 2014 : avant la bascule. */
const partiEn2014 = fixture(() => comparaisonDe(simulateur, 1950));

/** Un salarié né en 1980, parti en 2044 : après elle. */
const partiEn2044 = fixture(() => comparaisonDe(simulateur, 1980));

/**
 * Dix ans de cotisations constantes en termes réels, de 2000 à 2009, puis
 * dix ans de pension constante en termes réels, de 2010 à 2019 : la pension
 * vaut la cotisation fois `(1 + rendement)^10`, ce qui fait de
 * `rendement` le rendement interne réel, exactement.
 */
function fluxALaMain(leSimulateur, rendement) {
  const macro = leSimulateur.macro;
  const euros = (annee) => 1000.0 * macro.coefficientPrix(2000, annee);
  const facteur = pow(1.0 + rendement, 10);
  return new Flux({
    scenario: "actuel",
    cotisations: new Map(range(2000, 2010).map((annee) => [annee, euros(annee)])),
    revenus: new Map(range(2000, 2010).map((annee) => [annee, 4.0 * euros(annee)])),
    niveaux: new Map(range(2010, 2030).map((annee) => [annee, facteur * euros(annee)])),
    debut: 2010.0, age: 60.0, sexe: "H",
    dernier_revenu: 4.0 * euros(2010),
  });
}

// -- le rendement interne ------------------------------------------------------

test("le rendement d'un placement se retrouve", () => {
  proche(rendementInterne([[0.0, -100.0], [1.0, 105.0]]), 0.05, { abs: 1e-9 });
  proche(rendementInterne([[2000.5, -100.0], [2010.5, 100.0 * pow(1.03, 10)]]), 0.03,
    { abs: 1e-9 });
});

/**
 * Des cotisations sans pension n'ont pas de rendement : `null`, et non
 * un nombre qu'aucune page ne saurait écrire.
 */
test("sans taux qui égalise les flux, aucun rendement n'est rendu", () => {
  assert.equal(rendementInterne([[0.0, -100.0], [1.0, -5.0]]), null);
  assert.equal(rendementInterne([]), null);
});

/**
 * Les cotisations au milieu de leur année, les pensions au milieu de la
 * part servie : dix ans d'écart entre chaque cotisation et la pension qui
 * lui répond, et un rendement réel de 2 % exactement.
 */
test("un rendement connu d'avance se retrouve sur des flux datés", () => {
  const flux = fluxALaMain(simulateur, 0.02);
  const convention = new Convention({ age_deces: 70.0 });
  const resultat = indicateurs(flux, simulateur, convention);
  proche(resultat.rendement_reel, 0.02, { abs: 1e-9 });
  proche(resultat.duree_retraite, 10.0);
  egal(resultat.duree_carriere, 10);
});

/**
 * La définition de TRAJECTOiRE (`txRecuperation`) : la somme des
 * pensions sur la somme des cotisations, chaque montant divisé par le
 * salaire moyen par tête de son année ; le taux d'annuité, la même chose
 * sur les revenus d'activité.
 */
test("le taux de récupération est le rapport des deux sommes en salaire moyen", () => {
  const flux = fluxALaMain(simulateur, 0.02);
  const resultat = indicateurs(flux, simulateur, new Convention({ age_deces: 70.0 }));
  const macro = simulateur.macro;

  const enSalaireMoyen = (montants) => somme([...montants]
    .map(([annee, montant]) => montant / macro.coefficientSalaireMoyen(2000, annee)));

  const pensions = enSalaireMoyen(new Map([...flux.niveaux]
    .filter(([annee]) => annee < 2020)));
  proche(resultat.taux_recuperation, pensions / enSalaireMoyen(flux.cotisations), { rel: 1e-12 });
  proche(resultat.taux_annuite, pensions / enSalaireMoyen(flux.revenus), { rel: 1e-12 });
  proche(resultat.taux_remplacement_cycle,
    (pensions / 10.0) / (enSalaireMoyen(flux.revenus) / 10.0), { rel: 1e-12 });
});

/**
 * À un taux nul, la valeur au départ des pensions est leur somme en
 * euros du départ : dix années de 1,02^10 fois la cotisation, rapportées à
 * un dernier revenu de quatre cotisations.
 */
test("le patrimoine sans actualisation est la somme des pensions réelles", () => {
  const flux = fluxALaMain(simulateur, 0.02);
  const resultat = indicateurs(flux, simulateur, new Convention({
    age_deces: 70.0, taux_actualisation: 0.0 }));
  proche(resultat.patrimoine, 10.0 * pow(1.02, 10) / 4.0, { rel: 1e-12 });
});

/**
 * La valeur actuelle nette d'être couvert (PROST) : les pensions moins
 * les cotisations, ramenées au départ au même taux réel. Au rendement
 * interne réel, elles s'égalisent, par définition.
 */
test("au taux du rendement interne, la valeur nette est nulle", () => {
  const flux = fluxALaMain(simulateur, 0.02);
  const auRendement = indicateurs(flux, simulateur, new Convention({
    age_deces: 70.0, taux_actualisation: 0.02 }));
  proche(auRendement.valeur_nette, 0.0, { abs: 1e-9 });
  const plusBas = indicateurs(flux, simulateur, new Convention({
    age_deces: 70.0, taux_actualisation: 0.01 }));
  superieur(plusBas.valeur_nette, 0.0);
});

/**
 * La pension de la dernière année servie, rapportée au dernier revenu
 * mené jusqu'à elle par le salaire moyen. Une pension du scénario 1 suit les
 * prix, que les salaires dépassent : elle finit sous son taux du départ.
 */
test("le remplacement au décès est la dernière pension contre le salaire d'alors", () => {
  const flux = fluxALaMain(simulateur, 0.02);
  const resultat = indicateurs(flux, simulateur, new Convention({ age_deces: 70.0 }));
  const macro = simulateur.macro;
  const attendu = valeur(flux.niveaux, 2019) / (flux.dernier_revenu
    * macro.coefficientSalaireMoyen(2010, 2019));
  proche(resultat.remplacement_au_deces, attendu, { rel: 1e-12 });
  const actuel = fluxDesSystemes(simulateur, partiEn2044()).actuel;
  const auDeces = indicateurs(actuel, simulateur).remplacement_au_deces;
  inferieur(0.0, auDeces);
  inferieur(auDeces, partiEn2044().tauxRemplacementActuel);
});

test("une pension nette retire le prélèvement et baisse le rendement", () => {
  const flux = fluxALaMain(simulateur, 0.02);
  const brute = indicateurs(flux, simulateur, new Convention({ age_deces: 70.0 }));
  const nette = indicateurs(flux, simulateur, new Convention({
    age_deces: 70.0, prelevement: 0.1 }));
  proche(nette.taux_recuperation, 0.9 * brute.taux_recuperation);
  inferieur(nette.rendement_reel, brute.rendement_reel);
  egal(nette.duree_retraite, brute.duree_retraite);
});

// -- la fin de la retraite -------------------------------------------------------

test("sous un âge de décès fixe, la retraite dure jusqu'à lui", () => {
  const flux = fluxDesSystemes(simulateur, partiEn2044()).actuel;
  const resultat = indicateurs(flux, simulateur, new Convention({ age_deces: 87.5 }));
  proche(resultat.duree_retraite, 87.5 - flux.age, { abs: 1e-9 });
  proche(resultat.part_de_vie, resultat.duree_retraite / 87.5);
});

/**
 * L'intégrale de la survie à force constante par cellule, celle que
 * suppose `survie_annuelle` : l'espérance de vie résiduelle de la table de
 * génération, que `esperance_residuelle` calcule au trapèze, à un
 * centième d'année près.
 */
test("sous la survie, la durée est l'espérance du diviseur", () => {
  const flux = fluxDesSystemes(simulateur, partiEn2044()).actuel;
  const resultat = indicateurs(flux, simulateur);
  const attendue = simulateur.mortalite.esperanceResiduelle(flux.age, flux.debut, flux.sexe);
  proche(resultat.duree_retraite, attendue, { abs: 0.02 });
  const unisexe = indicateurs(flux, simulateur, new Convention({ unisexe: true }));
  superieur(unisexe.duree_retraite, resultat.duree_retraite);
});

/**
 * « 60 + l'espérance de vie à 60 ans de la génération », les deux sexes
 * réunis : la moyenne des deux espérances, puisque la table unisexe moyenne
 * les deux survies.
 */
test("l'âge de décès du COR est soixante ans et l'espérance de vie à soixante ans", () => {
  const mortalite = simulateur.mortalite;
  const hommes = mortalite.esperanceResiduelle(60.0, 2020.0, "H");
  const femmes = mortalite.esperanceResiduelle(60.0, 2020.0, "F");
  proche(ageDeDecesCor(mortalite, 1960), 60.0 + (hommes + femmes) / 2.0, { abs: 1e-9 });
});

test("la convention par défaut est celle de l'OCDE", () => {
  const convention = new Convention();
  assert.deepStrictEqual([convention.age_deces, convention.unisexe,
    convention.taux_actualisation, convention.prelevement], [null, false, 0.015, 0.0]);
});

// -- ce que chaque système verse et reçoit ---------------------------------------

/**
 * Ils changent ce qui est porté au compte, pas ce que la paie supporte :
 * ce que verse le scénario 1 jusqu'à la bascule, le taux du régime fusionné
 * ensuite. Pour un agent de l'État parti après elle, c'est moins que la part
 * de la contribution de l'État que le scénario 1 rattache à sa retraite.
 */
test("les scénarios 2 à 5 versent ce que prélève le compte du scénario 4", () => {
  const comparaison = comparaisonDe(simulateur, 1980, { affiliation: "fonctionnaire_etat" });
  const flux = fluxDesSystemes(simulateur, comparaison);
  const compte = new Map(comparaison.notionnel_retroactif_employeur.compte.cotisations
    .map((ligne) => [ligne.annee, ligne.cotisation]));
  const bascule = simulateur.parametres.annee_bascule;
  for (const scenario of SCENARIOS.slice(1, 5)) {
    assert.deepStrictEqual(flux[scenario].cotisations,
      new Map([...compte].filter(([, m]) => m)));
  }
  for (const [annee, montant] of flux.actuel.cotisations) {
    if (annee < bascule) {
      proche(valeur(flux.notionnel_retroactif.cotisations, annee), montant);
    } else {
      inferieur(valeur(flux.notionnel_retroactif.cotisations, annee), montant);
    }
  }
});

/**
 * Le compte ne porte pas les contributions d'équilibre de l'Agirc-Arrco ;
 * la paie les supporte. Le scénario 1 les verse toute la carrière, en plus
 * de ce que le compte prélève ; les scénarios 2 à 5 jusqu'à la bascule
 * seulement, où le régime fusionné remplace la complémentaire et ses
 * contributions.
 */
test("le salarié du privé verse aussi les contributions d'équilibre", () => {
  const flux = fluxDesSystemes(simulateur, partiEn2044());
  const carriere = partiEn2044().carriere;
  const equilibre = contributionsDUneCarriere(simulateur, carriere);
  const bascule = simulateur.parametres.annee_bascule;
  inferieur(Math.min(...equilibre.keys()), bascule);
  auPlus(bascule, Math.max(...equilibre.keys()));
  const compte = simulateur.constructeurEmployeur.construire(
    carriere, carriere.anneeLiquidation, carriere.premiereAnnee);
  const sans = new Map(compte.cotisations.map((ligne) => [ligne.annee, ligne.cotisation]));
  for (const [annee, montant] of equilibre) {
    proche(valeur(flux.actuel.cotisations, annee), valeur(sans, annee) + montant);
  }
  const reforme = new Map(partiEn2044().notionnel_retroactif_employeur.compte.cotisations
    .map((ligne) => [ligne.annee, ligne.cotisation]));
  for (const scenario of SCENARIOS.slice(1, 5)) {
    for (const [annee, montant] of flux[scenario].cotisations) {
      const avant = annee < bascule ? (equilibre.get(annee) ?? 0.0) : 0.0;
      proche(montant, valeur(reforme, annee) + avant, {}, `${scenario}, ${annee}`);
    }
  }
});

test("le scénario 6 verse son taux unique et son pilier après la bascule", () => {
  const flux = fluxDesSystemes(simulateur, partiEn2044());
  const liberal = partiEn2044().notionnel_liberal;
  const bascule = simulateur.parametres.annee_bascule;
  const versees = flux.notionnel_liberal.cotisations;
  for (const [annee, montant] of flux.actuel.cotisations) {
    if (annee < bascule) {
      egal(valeur(versees, annee), montant);
    }
  }
  const compte = new Map(liberal.compte.cotisations
    .map((ligne) => [ligne.annee, ligne.cotisation]));
  const pilier = new Map(liberal.capitalisation.annees
    .map((annee) => [annee.annee, annee.versement_brut]));
  const annee = bascule + 5;
  proche(valeur(versees, annee), valeur(compte, annee) + valeur(pilier, annee));
  superieur(valeur(pilier, annee), 0.0);
});

/**
 * Jusqu'à l'année courante, la pension du scénario 1 est celle que
 * l'étape « faire vivre » mène par les textes de chaque régime.
 */
test("le scénario 1 sert ce que le droit a servi jusqu'à aujourd'hui", () => {
  const flux = fluxDesSystemes(simulateur, partiEn2014()).actuel;
  const courante = simulateur.parametres.annee_courante;
  const vivante = faireVivre(simulateur, partiEn2014().carriere, partiEn2014().actuel, courante);
  const servie = (somme(vivante.regimes.filter((r) => !r.hors_repartition)
    .map((r) => r.aujourd_hui))
    + vivante.majoration_enfants * vivante.coefficient_majoration);
  proche(valeur(flux.niveaux, courante), servie, { rel: 1e-12 });
  inferieur(valeur(flux.niveaux, 2014), valeur(flux.niveaux, courante));
});

test("une réforme prospective garde la pension de qui est parti avant elle", () => {
  const flux = fluxDesSystemes(simulateur, partiEn2014());
  const bascule = simulateur.parametres.annee_bascule;
  for (const scenario of ["notionnel_prospectif", "notionnel_prospectif_employeur"]) {
    for (const annee of range(2014, bascule + 1)) {
      egal(valeur(flux[scenario].niveaux, annee), valeur(flux.actuel.niveaux, annee));
    }
  }
});

/**
 * De la liquidation à toute année, la pension du scénario 4 est sa
 * pension de départ revalorisée par la règle du compte : les prix fois le
 * coefficient réel de `RevalorisationServie`, sur toute la retraite,
 * et non jusqu'à l'année courante seulement.
 */
test("une pension notionnelle suit la règle de son compte", () => {
  const flux = fluxDesSystemes(simulateur, partiEn2044()).notionnel_retroactif_employeur;
  const liquidation = partiEn2044().carriere.anneeLiquidation;
  const depart = partiEn2044().notionnel_retroactif_employeur.pension_annuelle;
  proche(valeur(flux.niveaux, liquidation), depart);
  const reel = valeur(flux.niveaux, liquidation + 20) / simulateur.macro.coefficientPrix(
    liquidation, liquidation + 20) / depart;
  superieur(reel, 1.05);
});

test("la pension nette retire le taux plein et la maladie des complémentaires", () => {
  const actuel = partiEn2044().actuel;
  const complementaire = somme(actuel.pensions_par_regime
    .filter((p) => ["agirc", "arrco"].some((debut) => p.regime.startsWith(debut)))
    .map((p) => p.montant));
  const taux = tauxDePrelevement(simulateur, actuel);
  proche(taux, 0.091 + 0.01 * complementaire / actuel.pension_annuelle);
});

test("les indicateurs de chaque système se calculent", () => {
  const resultats = indicateursDesSystemes(simulateur, partiEn2044());
  assert.deepStrictEqual(Object.keys(resultats), [...SCENARIOS]);
  for (const [scenario, resultat] of Object.entries(resultats)) {
    nonNul(resultat.rendement_reel, scenario);
    inferieur(0.0, resultat.taux_recuperation, scenario);
    inferieur(resultat.taux_recuperation, 5.0, scenario);
    inferieur(0.0, resultat.patrimoine, scenario);
    inferieur(resultat.patrimoine, 30.0, scenario);
    assert.ok(Number.isFinite(resultat.duree_relative));
  }
});

// -- le jeu d'hypothèses de l'OCDE ------------------------------------------------
//
// Ses deux tests (`test_le_jeu_de_l_ocde_se_nomme_comme_un_scenario_de_projection`,
// `test_un_scenario_inconnu_reste_refuse`) ne portent que sur `DonneesMacro` du
// Python : ils restent en Python.

// -- en net ------------------------------------------------------------------------

/**
 * Sous une convention nette, ce qui rapporte la pension à un revenu
 * d'activité la rapporte au revenu net : le taux d'annuité net est le brut,
 * fois la part de la pension qui reste, divisé par la part du revenu qui
 * reste. Le patrimoine reste en années de dernier revenu brut, comme l'OCDE
 * l'exprime.
 */
test("en net, la pension nette se rapporte au revenu net", () => {
  const flux = fluxDesSystemes(simulateur, partiEn2044(), { nets: true }).actuel;
  const brute = indicateurs(flux, simulateur, new Convention({ age_deces: 87.0 }));
  const nette = indicateurs(flux, simulateur, new Convention({
    age_deces: 87.0, prelevement: 0.1 }));
  const macro = simulateur.macro;

  const enSalaireMoyen = (montants) => somme([...montants]
    .map(([annee, montant]) => montant / macro.coefficientSalaireMoyen(2000, annee)));

  const rapport = enSalaireMoyen(flux.revenus) / enSalaireMoyen(flux.revenus_nets);
  inferieur(1.2, rapport);
  inferieur(rapport, 1.3);
  proche(nette.taux_annuite, 0.9 * brute.taux_annuite * rapport, { rel: 1e-12 });
  proche(nette.taux_remplacement_cycle, 0.9 * brute.taux_remplacement_cycle * rapport,
    { rel: 1e-12 });
  proche(nette.patrimoine, 0.9 * brute.patrimoine, { rel: 1e-12 });
  const sansNet = fluxDesSystemes(simulateur, partiEn2044()).actuel;
  assert.equal(sansNet.revenus_nets, null);
  assert.equal(indicateurs(sansNet, simulateur, new Convention({
    age_deces: 87.0, prelevement: 0.1 })).taux_annuite, null);
});

/**
 * Après la bascule, le revenu net du scénario 6 est celui que la fiche de
 * paie de la proposition laisse du même brut — son rapport du net au brut,
 * comme le site l'applique à son taux de remplacement net
 * (`contexte.Montants`) ; les scénarios 1 à 5 gardent la fiche du droit en
 * vigueur, et tous la gardent avant la bascule.
 */
test("le scénario 6 lit son net sur la fiche de la proposition", () => {
  const flux = fluxDesSystemes(simulateur, partiEn2044(), { nets: true });
  const bascule = simulateur.parametres.annee_bascule;
  const annee = bascule + 5;
  const remuneration = partiEn2044().remuneration.annees.find((a) => a.annee === annee);
  const brut = valeur(flux.actuel.revenus, annee);
  proche(valeur(flux.notionnel_liberal.revenus_nets, annee),
    brut * remuneration.proposition.net / remuneration.proposition.brut, { rel: 1e-12 });
  superieur(valeur(flux.notionnel_liberal.revenus_nets, annee),
    valeur(flux.actuel.revenus_nets, annee));
  for (const scenario of SCENARIOS.slice(1, 5)) {
    assert.deepStrictEqual(flux[scenario].revenus_nets, flux.actuel.revenus_nets, scenario);
  }
  proche(valeur(flux.notionnel_liberal.revenus_nets, bascule - 1),
    valeur(flux.actuel.revenus_nets, bascule - 1));
});

/**
 * La fiche de paie d'un fonctionnaire a pour assiette son traitement. À
 * revenu égal, un quart de primes ôte un quart de la retenue pour pension,
 * que la loi n'assied pas sur elles, et paie la RAFP, 5 % des primes dans la
 * limite de 20 % du traitement ; le net de chaque année est celui de sa
 * fiche, l'indemnité compensatrice de la CSG de sa carrière comprise.
 */
test("les primes d'un fonctionnaire ne paient pas la retenue", () => {
  const carriere = (part_primes) => simulateur.carriereSimple({
    annee_naissance: 1980, sexe: "H", affiliation: "fonctionnaire_etat", age_debut: 22,
    age_liquidation: 64, niveau_salaire: 1.0, part_primes,
  });

  const [sans, avec] = [carriere(0.0), carriere(0.25)];
  const annee = 2030;
  const revenu = valeur(revenusDActivite(sans), annee);
  proche(valeur(revenusDActivite(avec), annee), revenu);

  const fiche = (laCarriere, partPrimes) => {
    const indemnite = valeur(indemnitesDeLaCarriere(laCarriere, simulateur.macro,
      simulateur.catalogue, simulateur.affiliations), annee);
    return ficheDepuisBrut(simulateur.baremePrelevements, simulateur.macro,
      simulateur.catalogue, simulateur.affiliations, "fonctionnaire_etat", annee, revenu,
      partPrimes, indemnite);
  };

  const ligne = (laFiche, code) => somme(laFiche.lignes.filter((l) => l.code === code)
    .map((l) => l.salarie));

  const [ficheSans, ficheAvec] = [fiche(sans, 0.0), fiche(avec, 0.25)];
  const retenue = ligne(ficheSans, "fonction_publique_etat");
  superieur(retenue, 0.1 * revenu);
  proche(ligne(ficheAvec, "fonction_publique_etat"), 0.75 * retenue, { rel: 1e-12 });
  proche(ligne(ficheAvec, "rafp"), 0.05 * 0.20 * 0.75 * revenu, { rel: 1e-12 });
  const ecart = (valeur(revenusNets(simulateur, avec), annee)
    - valeur(revenusNets(simulateur, sans), annee));
  proche(ecart, ficheAvec.net - ficheSans.net, { rel: 1e-9 });
});

test("un statut sans fiche de paie n'a pas de revenu net", () => {
  const exploitant = simulateur.carriereSimple({
    annee_naissance: 1980, sexe: "H", affiliation: "exploitant_agricole", age_debut: 20,
    age_liquidation: 64, niveau_salaire: 0.5,
  });
  assert.equal(revenusNets(simulateur, exploitant), null);
});

// -- après impôt -------------------------------------------------------------------

/**
 * Le salarié parti en 2044, sous l'impôt de son foyer, le barème projeté
 * sur les prix au-delà de la dernière loi de finances lue.
 */
const imposeEn2044 = fixture(() => fluxDesSystemes(simulateur, partiEn2044(),
  { impot: "prix" }));

/**
 * L'impôt du foyer d'une personne seule, sans enfant, qui déclare ce que
 * dit `declarant`, calculé par le module de l'impôt.
 */
function impotDe(leSimulateur, annee, declarant, indexation = "prix") {
  return impotDuFoyer(new Foyer({ declarants: [declarant] }), annee,
    chargerBaremesImpotRevenu(paquet), {
      indexation, croissance: croissanceMacro(leSimulateur.macro, indexation),
    }).impot;
}

/**
 * Chaque année, le foyer d'une personne seule, sans enfant à charge, qui
 * a l'âge de sa génération au 31 décembre, déclare son salaire imposable et
 * la part imposable de ce que sa pension sert dans l'année ; son impôt est
 * celui du module de l'impôt, au barème de l'année, projeté sur les prix. Le
 * foyer déclare les deux l'année du départ, la pension seule ensuite.
 */
test("l'impôt de chaque année est celui du foyer qui la déclare", () => {
  const flux = imposeEn2044().actuel;
  const imposables = revenusImposables(simulateur, partiEn2044().carriere);
  const parts = partsImposablesParAnnee(simulateur, partiEn2044());
  const depart = flux.annee_liquidation;
  const baremes = chargerBaremesImpotRevenu(paquet);
  for (const annee of [2005, 2020, 2035, depart, depart + 1, depart + 30]) {
    const impot = valeur(flux.impots, annee);
    const pension = (flux.niveaux.get(annee) ?? 0.0) * flux.servi(annee)
      * (parts.get(annee) ?? 0.0);
    proche(impot.salaire, imposables.get(annee) ?? 0.0, {}, annee);
    proche(impot.pension, pension, {}, annee);
    const foyer = new Foyer({ declarants: [new Declarant({
      salaires: impot.salaire, pensions: impot.pension, age: annee - 1980 })] });
    assert.deepStrictEqual(impot.foyer, impotDuFoyer(foyer, annee, baremes, {
      indexation: "prix", croissance: croissanceMacro(simulateur.macro, "prix") }),
    String(annee));
  }
  superieur(valeur(flux.impots, depart).salaire, 0.0);
  superieur(valeur(flux.impots, depart).pension, 0.0);
  egal(valeur(flux.impots, depart + 1).salaire, 0.0);
  superieur(valeur(flux.impots, depart + 1).impot, 0.0);
});

/**
 * L'année du départ, l'impôt du foyer se partage entre le salaire et la
 * pension au prorata des deux revenus après leurs abattements de 10 % : le
 * revenu après impôt de l'année perd la part du salaire, la pension la
 * sienne, sur les mois servis. Une année de carrière, tout l'impôt est
 * celui du salaire.
 */
test("l'année du départ partage l'impôt au prorata", () => {
  const flux = imposeEn2044().actuel;
  const depart = flux.annee_liquidation;
  const impot = valeur(flux.impots, depart);
  const [salaires, pensions] = [somme(impot.foyer.salaires_nets),
    somme(impot.foyer.pensions_nettes)];
  proche(impot.sur_la_pension, impot.impot * pensions / (salaires + pensions));
  proche(valeur(flux.revenus_apres_impot, depart),
    valeur(flux.revenus_nets, depart) - impot.sur_le_salaire);
  proche(flux.impotDeLaPension(depart),
    impot.sur_la_pension / (valeur(flux.niveaux, depart) * (depart + 1 - flux.debut)));
  const annee = depart - 5;
  proche(valeur(flux.revenus_apres_impot, annee),
    valeur(flux.revenus_nets, annee) - valeur(flux.impots, annee).impot);
  egal(flux.impotDeLaPension(annee), 0.0);
});

/**
 * Sous un âge de décès fixe, la pension après impôt d'une année est sa
 * pension nette moins l'impôt qu'elle supporte, l'année du départ comprise.
 */
test("après impôt, chaque année de pension perd l'impôt qu'elle supporte", () => {
  const flux = imposeEn2044().actuel;
  const nette = remplace(conventionNette(simulateur, partiEn2044()), { age_deces: 87.0 });
  const avant = new Map(pensionsEsperees(flux, simulateur, nette)
    .map(([annee, montant]) => [annee, montant]));
  const apres = new Map(pensionsEsperees(flux, simulateur, nette.avecLImpot("prix"))
    .map(([annee, montant]) => [annee, montant]));
  for (const annee of [flux.annee_liquidation, flux.annee_liquidation + 1,
    flux.annee_liquidation + 20]) {
    proche(valeur(avant, annee) - valeur(apres, annee), valeur(flux.impots, annee).sur_la_pension,
      { rel: 1e-9 }, annee);
  }
});

/**
 * La pension paie l'impôt, les cotisations non : le rendement, la
 * récupération et le patrimoine baissent. Le salaire en paie plus que la
 * pension, qui a des abattements et des revenus moindres : le taux
 * d'annuité et le remplacement sur le cycle de vie montent. La durée ne
 * change pas.
 */
test("après impôt, le rendement baisse et le taux d'annuité monte", () => {
  const nette = indicateursDesSystemes(
    simulateur, partiEn2044(), conventionNette(simulateur, partiEn2044()));
  const sousLImpot = indicateursDesSystemes(
    simulateur, partiEn2044(), conventionApresImpot(simulateur, partiEn2044()));
  const [avant, apres] = [nette.actuel, sousLImpot.actuel];
  inferieur(apres.rendement_reel, avant.rendement_reel);
  inferieur(apres.taux_recuperation, avant.taux_recuperation);
  inferieur(apres.patrimoine, avant.patrimoine);
  superieur(apres.taux_annuite, avant.taux_annuite);
  superieur(apres.taux_remplacement_cycle, avant.taux_remplacement_cycle);
  egal(apres.duree_retraite, avant.duree_retraite);
});

/**
 * Le taux net de l'OCDE : la pension du premier mois, annualisée, nette
 * de ses prélèvements et de l'impôt d'une année entière de cette pension,
 * sur le dernier revenu annualisé, net des siens et de l'impôt d'une année
 * entière de ce revenu, déclaré par un actif, sans l'abattement des
 * personnes âgées. La pension paie moins d'impôt que le salaire : il est
 * au-dessus du taux de remplacement net.
 */
test("le remplacement après impôt impose une année entière de chacun", () => {
  const flux = imposeEn2044().actuel;
  const depart = flux.annee_liquidation;
  const imposables = revenusImposables(simulateur, partiEn2044().carriere);
  const derniere = Math.max(...flux.revenus.keys());
  const salaire = flux.dernier_revenu * valeur(imposables, derniere)
    / valeur(flux.revenus, derniere);
  proche(flux.dernier_revenu_apres_impot,
    flux.dernier_revenu_net - impotDe(simulateur, depart, new Declarant({ salaires: salaire })));
  const brute = pensionAuDepart(simulateur, partiEn2044(), "actuel");
  const part = valeur(partsImposablesParAnnee(simulateur, partiEn2044()), depart);
  const nette = brute * conventionNette(simulateur, partiEn2044()).retenu(depart);
  const impot = impotDe(simulateur, depart, new Declarant({
    pensions: brute * part, age: depart - 1980 }));
  const attendu = (nette - impot) / flux.dernier_revenu_apres_impot;
  proche(remplacementApresImpot(simulateur, partiEn2044(), "actuel", "prix", imposeEn2044()),
    attendu);
  superieur(attendu, nette / flux.dernier_revenu_net);
});

/**
 * Sous l'impôt, le départ rend aussi le numérateur du taux de
 * remplacement après impôt, ce que les pages montrent (action 138, étape
 * 5) : la pension nette du premier mois, annualisée, moins l'impôt d'une
 * année entière d'elle seule, déclarée par une personne seule de son âge au
 * barème de l'année du départ. Avant impôt, il n'en rend aucune.
 */
test("le départ rend la pension après impôt de chaque système", () => {
  const lui = departDe(simulateur, partiEn2044(), false, null, "prix");
  const annee = partiEn2044().carriere.anneeLiquidation;
  const brute = pensionAuDepart(simulateur, partiEn2044(), "actuel");
  const part = valeur(partsImposablesParAnnee(simulateur, partiEn2044()), annee);
  const impot = impotDe(simulateur, annee, new Declarant({
    pensions: brute * part, age: annee - 1980 }));
  superieur(impot, 0.0);
  proche(valeur(lui.pensions_apres_impot, "actuel"),
    valeur(lui.pensions_nettes, "actuel") - impot);
  assert.deepStrictEqual(new Set(Object.keys(lui.pensions_apres_impot)),
    new Set(Object.keys(lui.pensions_nettes)));
  for (const [scenario, pension] of Object.entries(lui.pensions_apres_impot)) {
    proche(pension, valeur(lui.remplacements_apres_impot, scenario)
      * imposeEn2044()[scenario].dernier_revenu_apres_impot);
  }
  assert.equal(balayage1970()[0].pensions_apres_impot, null);
});

/**
 * « Les majorations de retraite ou de pension pour charges de famille »
 * sont affranchies de l'impôt (CGI, art. 81, 2° ter), mais « le montant
 * exonéré [...] ne peut excéder, pour un même bénéficiaire, 10 % du montant
 * de la pension pour les trois premiers enfants et 5 % par enfant au-delà du
 * troisième » (DB 5 F 1222, n° 4) ; la loi de finances pour 2014 abroge le
 * 2° ter (art. 5) dès « l'impôt sur le revenu dû au titre de 2013 » (art. 1er,
 * II, 1°). La majoration et la pension sans elle, en euros de l'année.
 */
test("la majoration pour enfants s'exonère jusqu'aux revenus de 2012", () => {
  const exoneree = majorationExoneree;
  egal(exoneree(2012, 800.0, 10_000.0, 3), 800.0);
  proche(exoneree(2012, 1_500.0, 10_000.0, 3), 1_000.0);
  proche(exoneree(2012, 1_500.0, 10_000.0, 4), 1_500.0);
  proche(exoneree(2012, 2_500.0, 10_000.0, 5), 2_000.0);
  proche(exoneree(2012, 1_500.0, 10_000.0, 1), 1_000.0);
  egal(exoneree(1960, 800.0, 10_000.0, 3), 800.0);
  egal(exoneree(2013, 800.0, 10_000.0, 3), 0.0);
  egal(exoneree(2012, 0.0, 10_000.0, 0), 0.0);
});

/**
 * Un salarié né en 1946, père de trois enfants, parti en 2008 : sa
 * pension porte la majoration pour enfants du régime général et de l'Arrco.
 */
const parentPartiEn2008 = fixture(() => simulateur.simuler(simulateur.carriereSimple({
  annee_naissance: 1946, sexe: "H", affiliation: "salarie_prive_non_cadre", age_debut: 21,
  age_liquidation: 62, niveau_salaire: 1.0, jour_naissance: 15, nombre_enfants: 3,
  naissances_enfants: ["1972-03-01", "1975-06-01", "1978-09-01"],
})));

/**
 * Le parent de trois enfants parti en 2008 déclare chaque année la part
 * imposable de sa pension sans sa majoration pour enfants jusqu'aux revenus
 * de 2012 — la CSG qui la frappe ne se déduit pas (BOI-RSA-BASE-30-30-20120912,
 * § 90) —, toute sa pension dès 2013 : « les majorations [...] perçues à
 * compter du 1er janvier 2013 sont imposables » (BOI-RSA-PENS-20-10-20140305,
 * § 1). Un système prospectif, qui lui garde jusqu'à sa bascule la pension du
 * scénario 1, l'exonère de même ; un système rétroactif, qui ne sert pas de
 * majoration, n'a rien à exonérer. Le taux de remplacement après impôt de son
 * départ l'exonère aussi.
 */
test("jusqu'aux revenus de 2012, le foyer ne déclare pas la majoration", () => {
  const systemes = fluxDesSystemes(simulateur, parentPartiEn2008(), { impot: "prix" });
  const parts = partsImposablesParAnnee(simulateur, parentPartiEn2008());
  const [carriere, resultat] = [parentPartiEn2008().carriere, parentPartiEn2008().actuel];
  const exonerees = new Map();
  for (const annee of [2008, 2010, 2012, 2013, 2020]) {
    const vivante = faireVivre(simulateur, carriere, resultat, annee);
    const majoration = vivante.majoration_enfants * vivante.coefficient_majoration;
    superieur(majoration, 0.0, annee);
    const niveau = valeur(systemes.actuel.niveaux, annee);
    exonerees.set(annee, annee <= 2012
      ? Math.min(majoration, 0.10 * (niveau - majoration)) : 0.0);
    for (const scenario of ["actuel", "notionnel_prospectif"]) {
      const flux = systemes[scenario];
      proche(valeur(flux.niveaux, annee), niveau, {}, `${scenario}, ${annee}`);
      proche(valeur(flux.impots, annee).pension,
        (niveau - valeur(exonerees, annee)) * flux.servi(annee) * valeur(parts, annee), {},
        `${scenario}, ${annee}`);
    }
    const retroactif = systemes.notionnel_retroactif;
    proche(valeur(retroactif.impots, annee).pension,
      valeur(retroactif.niveaux, annee) * retroactif.servi(annee) * valeur(parts, annee), {},
      annee);
  }
  const flux = systemes.actuel;
  const depart = flux.annee_liquidation;
  egal(depart, 2008);
  const brute = pensionAuDepart(simulateur, parentPartiEn2008(), "actuel");
  const nette = brute * conventionNette(simulateur, parentPartiEn2008()).retenu(depart);
  const declaree = brute * (1.0 - valeur(exonerees, depart) / valeur(flux.niveaux, depart))
    * valeur(parts, depart);
  const impot = impotDe(simulateur, depart, new Declarant({
    pensions: declaree, age: depart - 1946 }));
  proche(remplacementApresImpot(simulateur, parentPartiEn2008(), "actuel", "prix", systemes),
    (nette - impot) / flux.dernier_revenu_apres_impot);
});

/**
 * Les salaires montent plus vite que les prix : au-delà de la dernière
 * loi de finances lue, le barème projeté sur le salaire moyen prend moins
 * que celui que les prix relèvent ; jusqu'à elle, c'est le même.
 */
test("sur le salaire moyen, le barème projeté prend moins", () => {
  const prix = imposeEn2044().actuel;
  const salaires = fluxDesSystemes(simulateur, partiEn2044(),
    { impot: "salaire_moyen" }).actuel;
  assert.deepStrictEqual(valeur(salaires.impots, 2020), valeur(prix.impots, 2020));
  for (const annee of [2040, prix.annee_liquidation + 10]) {
    inferieur(valeur(salaires.impots, annee).impot, valeur(prix.impots, annee).impot, annee);
  }
});

/**
 * Le bénéfice d'un artisan s'impose comme celui d'un adhérent d'un
 * organisme de gestion agréé : chaque année cotisée le déclare, sans
 * l'abattement de 10 % des salaires, avec celui des adhérents jusqu'en 2005 ;
 * ses revenus après impôt se calculent, et ce qui s'y rapporte. Le libéral
 * déclare un bénéfice non commercial. Sans fiche de paie, la pension d'un
 * exploitant s'impose seule.
 */
test("le bénéfice d'un indépendant est imposé", () => {
  const artisan = simulateur.simuler(simulateur.carriereSimple({
    annee_naissance: 1970, sexe: "H", affiliation: "artisan", age_debut: 24,
    age_liquidation: 64, niveau_salaire: 1.0,
  }));
  const benefices = beneficesParAnnee(simulateur, artisan.carriere);
  assert.deepStrictEqual(new Set(benefices.keys()),
    new Set(revenusDActivite(artisan.carriere).keys()));
  assert.deepStrictEqual(
    new Set([...benefices.values()].map((valeurs) => JSON.stringify(valeurs.slice(0, 2)))),
    new Set([JSON.stringify([1.0, "bic"])]));
  let flux = fluxDesSystemes(simulateur, artisan, { impot: "prix" }).actuel;
  nonNul(flux.revenus_apres_impot);
  nonNul(flux.dernier_revenu_apres_impot);
  const imposables = revenusImposables(simulateur, artisan.carriere);
  for (const annee of [2000, 2010, 2024]) {
    const impot = valeur(flux.impots, annee);
    egal(impot.salaire, 0.0, annee);
    proche(impot.benefice, valeur(imposables, annee), {}, annee);
    assert.deepStrictEqual(impot.foyer.salaires_nets, [0.0]);
    egal(impot.foyer.abattement_adherents > 0.0, annee <= 2005, annee);
    egal(impot.foyer.majoration_des_benefices, 0.0, annee);
    proche(valeur(flux.revenus_apres_impot, annee),
      valeur(flux.revenus_nets, annee) - impot.impot, {}, annee);
  }
  const resultat = indicateurs(flux, simulateur, conventionApresImpot(simulateur, artisan));
  const nette = indicateurs(flux, simulateur, conventionNette(simulateur, artisan));
  nonNul(resultat.taux_annuite);
  nonNul(resultat.rendement_reel);
  inferieur(resultat.rendement_reel, nette.rendement_reel);
  const liberal = simulateur.simuler(simulateur.carriereSimple({
    annee_naissance: 1970, sexe: "F", affiliation: "profession_liberale", age_debut: 26,
    age_liquidation: 64, niveau_salaire: 1.5,
  }));
  assert.deepStrictEqual(new Set([...beneficesParAnnee(simulateur, liberal.carriere).values()]
    .map(([, c]) => c)), new Set(["bnc"]));
  const exploitant = simulateur.simuler(simulateur.carriereSimple({
    annee_naissance: 1980, sexe: "H", affiliation: "exploitant_agricole", age_debut: 20,
    age_liquidation: 64, niveau_salaire: 1.0,
  }));
  flux = fluxDesSystemes(simulateur, exploitant, { impot: "prix" }).actuel;
  assert.equal(flux.revenus_apres_impot, null);
  assert.ok([...flux.impots.values()]
    .every((impot) => impot.salaire === 0.0 && impot.benefice === 0.0));
});

/**
 * La taxe complémentaire frappe le bénéfice des revenus de 1959 à ceux de
 * 1969 (loi n° 59-1472, art. 18 ; loi n° 69-1161, art. 5) : le commerçant la
 * paie chaque année, et déduit de son revenu global celle de ses revenus de
 * l'année précédente, qu'il paie dans l'année (art. 18, 4) — en 1960, celle
 * des revenus de 1959, dont l'impôt ne se calcule pas. L'artisan, que le
 * modèle tient pour l'artisan fiscal (CGI, art. 1649 quater A), a
 * l'abattement de 4 400 F, la moitié du taux pour 1964 (loi n° 64-1279, art.
 * 3), et n'en paie plus dès les revenus de 1965 (loi n° 65-997, art. 4).
 */
test("la taxe complémentaire des indépendants d'avant 1970", () => {
  const commercant = simulateur.simuler(simulateur.carriereSimple({
    annee_naissance: 1932, sexe: "H", affiliation: "commercant", age_debut: 24,
    age_liquidation: 65, niveau_salaire: 3.0,
  }));
  let impots = fluxDesSystemes(simulateur, commercant, { impot: "prix" }).actuel.impots;
  for (const [annee, taux, abattement] of [[1960, 0.08, 3000], [1966, 0.06, 3000],
    [1968, 0.06, 4000], [1969, 0.06, 30000]]) {
    const francs = valeur(impots, annee).benefice * FRANC;
    proche(valeur(impots, annee).foyer.taxe_complementaire * FRANC,
      taux * (francs - abattement), { abs: taux * 100 }, annee);
  }
  egal(valeur(impots, 1970).foyer.taxe_complementaire, 0.0);
  const imposables = revenusImposables(simulateur, commercant.carriere);
  const de1959 = taxeComplementaireDesRevenus(new Foyer({ declarants: [new Declarant({
    benefices: valeur(imposables, 1959) })] }), 1959, chargerBaremesImpotRevenu(paquet));
  proche(de1959 * FRANC, 0.09 * (valeur(imposables, 1959) * FRANC - 3000), { abs: 9 });
  proche(valeur(impots, 1960).foyer.taxe_complementaire_deduite, de1959);
  for (const annee of range(1961, 1971)) {
    proche(valeur(impots, annee).foyer.taxe_complementaire_deduite,
      valeur(impots, annee - 1).foyer.taxe_complementaire, {}, annee);
  }
  superieur(valeur(impots, 1970).foyer.taxe_complementaire_deduite, 0.0);
  egal(valeur(impots, 1971).foyer.taxe_complementaire_deduite, 0.0);
  const artisan = simulateur.simuler(simulateur.carriereSimple({
    annee_naissance: 1936, sexe: "H", affiliation: "artisan", age_debut: 21,
    age_liquidation: 64, niveau_salaire: 1.0,
  }));
  impots = fluxDesSystemes(simulateur, artisan, { impot: "prix" }).actuel.impots;
  for (const [annee, taux] of [[1960, 0.08], [1963, 0.06], [1964, 0.03], [1965, 0.0],
    [1968, 0.0]]) {
    const francs = valeur(impots, annee).benefice * FRANC;
    proche(valeur(impots, annee).foyer.taxe_complementaire * FRANC,
      taux * (francs - 4400), { abs: taux * 11 + 1e-9 }, annee);
  }
});

/**
 * `_part_de_la_pension` du Python, dont le jumeau, `partDeLaPension`, reste
 * privé dans `cycle-de-vie.js` : la part de l'impôt d'un foyer que supporte
 * sa pension, au prorata des revenus après leurs abattements de 10 %, le
 * bénéfice tel que l'impôt le retient, un déficit ne comptant pour rien ;
 * chaque somme de gauche à droite (`somme_ordonnee`).
 */
function partDeLaPension(impot) {
  const ordonnee = (termes) => termes.reduce((total, terme) => total + terme, 0);
  const activite = Math.max(ordonnee(impot.salaires_nets) + ordonnee(impot.benefices_retenus),
    0.0);
  const pensions = ordonnee(impot.pensions_nettes);
  if (activite + pensions <= 0.0) return 0.0;
  return pensions / (activite + pensions);
}

/**
 * La part de l'impôt que supporte une pension se prend sur l'impôt sur le
 * revenu seul : la taxe complémentaire ne frappe que le bénéfice (loi n°
 * 59-1472, art. 18, 1). Un foyer de 1966 qui déclare un bénéfice et une
 * pension, comme l'année d'un départ.
 */
test("la taxe complémentaire ne pèse pas sur la pension", () => {
  const flux = { niveaux: new Map([[1966, 1000.0]]), servi: () => 1.0, exoneree: new Map() };
  const impots = impotsParAnnee(simulateur, flux, { annee_naissance: 1901 },
    new Map([[1966, 1.0]]), new Map(), "prix", null,
    new Map([[1966, [2000.0, "bic", false]]]));
  const impot = valeur(impots, 1966);
  const taxe = impot.foyer.taxe_complementaire;
  superieur(taxe, 0.0);
  superieur(impot.pension, 0.0);
  superieur(impot.foyer.pensions_nettes[0], 0.0);
  const part = partDeLaPension(impot.foyer);
  proche(impot.sur_la_pension, (impot.impot - taxe) * part);
  superieur(impot.sur_le_salaire, taxe);
});

test("une convention après impôt est nette et demande un flux imposé", () => {
  assert.throws(() => new Convention({ impot: "prix" }), /net imposable/);
  assert.throws(() => new Convention({ prelevement: 0.1, impot: "loyers" }), /inconnue/);
  const flux = fluxDesSystemes(simulateur, partiEn2044(), { nets: true }).actuel;
  // Le Python demande « impot='prix' », l'argument nommé de
  // `flux_des_systemes(…, impot='prix')` que son message cite ; le portage
  // cite son jumeau, `fluxDesSystemes(…, {impot: 'prix'})`.
  assert.throws(() => indicateurs(flux, simulateur,
    conventionApresImpot(simulateur, partiEn2044())), /\{impot: 'prix'\}/);
});

// -- la pension par étage et le revenu autour du départ ------------------------------

/**
 * Le tableau 1 de Typfallsmodellen, de Pensionsmyndigheten, pour l'exemple de
 * son manuel (PID289138, version 2.2 du 27 janvier 2025, § 2.1), l'aide-soignante
 * née en 1960 qui part à 67 ans : chaque étage en couronnes de 2024 par an
 * (colonne B), et en pour cent du salaire de fin de carrière (colonne D).
 */
const TABLEAU_1_TYPFALLSMODELLEN = {
  inkomstpension: [172_296.0, 51.6],
  tillaggspension: [0.0, 0.0],
  premiepension: [34_596.0, 10.4],
  garantipension: [13_572.0, 4.1],
  inkomstpensionstillagg: [7_200.0, 2.2],
  tjanstepension: [67_068.0, 20.1],
  privat_pensionssparande: [0.0, 0.0],
};

/**
 * Typfallsmodellen rend la pension de son cas type étage par étage, chacun
 * en part du salaire de fin de carrière, et la pension après impôt en part du
 * salaire après impôt (registre, `typfallsmodellen`, chantier « 138.9 ») :
 * de son exemple — 334 098 couronnes de salaire, 259 206 après impôt, 209 562
 * de pension après impôt —, la pension par étage refait sa colonne D au
 * dixième de point, 88,2 % au total, 80,8 % après impôt.
 */
test("chaque étage se rapporte au dernier salaire, comme dans Typfallsmodellen", () => {
  const pension = new PensionParEtage({
    etages: Object.fromEntries(Object.entries(TABLEAU_1_TYPFALLSMODELLEN)
      .map(([etage, [montant]]) => [etage, montant])),
    dernier_revenu: 334_098.0, apres_impot: 209_562.0, dernier_revenu_apres_impot: 259_206.0,
  });
  assert.deepStrictEqual(Object.fromEntries(Object.entries(pension.parts)
    .map(([etage, part]) => [etage, arrondi(100.0 * part, 1)])),
  Object.fromEntries(Object.entries(TABLEAU_1_TYPFALLSMODELLEN)
    .map(([etage, [, publie]]) => [etage, publie])));
  egal(pension.brute, 294_732.0);
  egal(arrondi(100.0 * pension.remplacement_brut, 1), 88.2);
  egal(arrondi(100.0 * pension.remplacement_apres_impot, 1), 80.8);
  assert.equal(pension.remplacement_net, null);
});

/**
 * Au départ, la pension du scénario 1 se range par étage, chaque régime
 * au sien : le régime général à la base, l'Arrco puis l'Agirc-Arrco à la
 * complémentaire. La fonctionnaire de l'État a un régime intégré, qui sert
 * aussi sa majoration pour trois enfants ; le RAFP, servi à part, n'y est
 * pas. Un système notionnel n'a qu'un étage, son compte, auquel le
 * scénario 6 ajoute son pilier capitalisé ; une réforme prospective garde
 * à qui part avant elle les étages du scénario 1. Leur somme est la
 * pension du départ.
 */
test("chaque régime sert à son étage, et la proposition aux siens", () => {
  const regimes = Object.fromEntries(partiEn2044().actuel.pensions_par_regime
    .map((p) => [p.regime, p.montant]));
  procheDe(pensionParEtage(simulateur, partiEn2044()).etages, {
    base: valeur(regimes, "regime_general"),
    complementaire: valeur(regimes, "arrco") + valeur(regimes, "agirc_arrco"),
  });
  const fonctionnaire = simulateur.simuler(simulateur.carriereSimple({
    annee_naissance: 1966, sexe: "F", affiliation: "fonctionnaire_etat", age_debut: 22,
    age_liquidation: 63.0, niveau_salaire: 1.0, part_primes: 0.2, nombre_enfants: 3,
    jour_naissance: 15,
  }));
  const majoration = fonctionnaire.actuel.avantages_appliques
    .find((a) => a.code === "majoration_enfants");
  const integre = fonctionnaire.actuel.pensions_par_regime
    .find((p) => p.regime === "fonction_publique_etat").montant;
  superieur(fonctionnaire.actuel.pension_hors_repartition, 0.0);
  procheDe(pensionParEtage(simulateur, fonctionnaire).etages,
    { integre: integre + majoration.montant });
  const liberal = partiEn2044().notionnel_liberal;
  procheDe(pensionParEtage(simulateur, partiEn2044(), "notionnel_liberal").etages, {
    notionnel: liberal.garantie_vieillesse.pension_contributive,
    capitalise: liberal.rente_capitalisation_obligatoire,
  });
  procheDe(pensionParEtage(simulateur, partiEn2044(), "notionnel_retroactif").etages,
    { notionnel: partiEn2044().notionnel_retroactif.pension_annuelle });
  assert.deepStrictEqual(pensionParEtage(simulateur, partiEn2014(), "notionnel_prospectif").etages,
    pensionParEtage(simulateur, partiEn2014()).etages);
  for (const comparaison of [partiEn2014(), partiEn2044(), fonctionnaire]) {
    for (const scenario of SCENARIOS) {
      proche(pensionParEtage(simulateur, comparaison, scenario).brute,
        pensionAuDepart(simulateur, comparaison, scenario), {}, scenario);
    }
  }
});

/**
 * En part du dernier revenu, la pension par étage rend ce que le
 * simulateur et le module rendent déjà : brute, le taux de remplacement du
 * simulateur ; nette des prélèvements de l'année du départ, sur le dernier
 * revenu net ; après l'impôt d'une année entière de cette pension, sur le
 * dernier revenu après impôt, le taux net de l'OCDE. Avant impôt, elle n'a
 * pas de pension après impôt.
 */
test("la pension par étage rend les trois taux de remplacement au départ", () => {
  proche(pensionParEtage(simulateur, partiEn2044(), "actuel", imposeEn2044()).remplacement_brut,
    partiEn2044().tauxRemplacementActuel);
  const nette = conventionNette(simulateur, partiEn2044());
  const retenu = (annee) => nette.retenu(annee);
  for (const scenario of ["actuel", "notionnel_liberal"]) {
    const pension = pensionParEtage(simulateur, partiEn2044(), scenario, imposeEn2044());
    const flux = imposeEn2044()[scenario];
    proche(pension.remplacement_net,
      pension.brute * retenu(flux.annee_liquidation) / flux.dernier_revenu_net, {}, scenario);
    proche(pension.remplacement_apres_impot, remplacementApresImpot(simulateur, partiEn2044(),
      scenario, "prix", imposeEn2044()), {}, scenario);
  }
  const avant = pensionParEtage(simulateur, partiEn2044());
  nonNul(avant.nette);
  assert.equal(avant.apres_impot, null);
  assert.equal(avant.remplacement_apres_impot, null);
});

/**
 * Le tableau 2 de Typfallsmodellen : chaque année, de dix ans avant celle
 * du départ à dix ans après, en euros de l'année du départ, le revenu
 * d'activité, la pension des mois servis, leur net et l'impôt du foyer.
 * Né le 15 janvier 1980, parti à 64 ans en février 2044, le salarié
 * travaille encore en janvier, le douzième de son dernier revenu annualisé ;
 * sa pension sert onze mois ; ensuite, menée sur les prix, elle vaut chaque
 * année, en euros de 2044, la pension du départ.
 */
test("le revenu autour du départ va de dix ans avant à dix ans après", () => {
  const lignes = revenusAutourDuDepart(simulateur, partiEn2044(), "actuel", imposeEn2044());
  assert.deepStrictEqual(lignes.map((ligne) => ligne.annee), range(2034, 2055));
  const flux = imposeEn2044().actuel;
  const macro = simulateur.macro;
  const nette = conventionNette(simulateur, partiEn2044());
  const retenu = (annee) => nette.retenu(annee);
  const parAnnee = new Map(lignes.map((ligne) => [ligne.annee, ligne]));
  const avant = valeur(parAnnee, 2043);
  const euros = macro.coefficientPrix(2043, 2044);
  egal(avant.pension, 0.0);
  proche(avant.revenu, valeur(flux.revenus, 2043) * euros);
  proche(avant.net, valeur(flux.revenus_nets, 2043) * euros);
  proche(avant.impot, valeur(flux.impots, 2043).impot * euros);
  const depart = valeur(parAnnee, 2044);
  proche(depart.revenu, flux.dernier_revenu / 12.0);
  proche(depart.pension, valeur(flux.niveaux, 2044) * 11.0 / 12.0);
  const auDepart = pensionAuDepart(simulateur, partiEn2044(), "actuel");
  for (const annee of [2045, 2054]) {
    const ligne = valeur(parAnnee, annee);
    egal(ligne.revenu, 0.0, annee);
    proche(ligne.pension, auDepart, {}, annee);
    proche(ligne.net, auDepart * retenu(annee), {}, annee);
    proche(ligne.impot, valeur(flux.impots, annee).impot * macro.coefficientPrix(annee, 2044),
      {}, annee);
  }
  for (const ligne of lignes) {
    proche(ligne.brut, ligne.revenu + ligne.pension, {}, ligne.annee);
    proche(ligne.apres_impot, ligne.net - ligne.impot, {}, ligne.annee);
  }
  const sansImpot = revenusAutourDuDepart(simulateur, partiEn2044(), "actuel", null, 2);
  assert.deepStrictEqual(sansImpot.map((ligne) => ligne.annee), [2042, 2043, 2044, 2045, 2046]);
  assert.ok(sansImpot.every((ligne) => ligne.impot === null && ligne.apres_impot === null));
  proche(sansImpot[1].net, avant.net);
});

// -- à chaque âge de départ ---------------------------------------------------------

/** Le salarié au salaire moyen né en 1970, à chacun de ses âges de départ. */
const balayage1970 = fixture(() => {
  const leCas = cas("salaire_moyen");
  return balayageDUneCarriere(
    simulateur, (age) => leCas.carriereA(simulateur, 1970, age),
    leCas.ageLiquidationPour(simulateur, 1970));
});

/**
 * De trimestre en trimestre, comme TRAJECTOiRE, de l'âge d'ouverture à
 * l'âge d'annulation de la décote : 64 et 67 ans pour la génération 1970,
 * sous la loi du 14 avril 2023. La carrière longue ouvre le droit plus tôt,
 * et le balayage avec elle.
 */
test("les âges vont de l'ouverture à l'annulation de la décote, par trimestre", () => {
  assert.deepStrictEqual(balayage1970().map((depart) => depart.age),
    range(0, 13).map((rang) => 64.0 + 0.25 * rang));
  assert.ok(balayage1970().every((depart) => depart.annee === 1970 + Math.trunc(depart.age)));
  const smic = cas("smic_carriere_complete");
  const longue = agesBalayes(
    simulateur, (age) => smic.carriereA(simulateur, 1970, age),
    smic.ageLiquidationPour(simulateur, 1970));
  inferieur(longue[0], 64.0);
  egal(longue[longue.length - 1], 67.0);
});

/**
 * Chaque trimestre de plus : une retraite plus courte, une pension nette
 * plus forte, plus haut sur le minimum vieillesse, un taux de remplacement
 * net plus fort.
 */
test("partir plus tard raccourcit la retraite et relève la pension", () => {
  for (const [avant, apres] of paires(balayage1970())) {
    inferieur(apres.indicateurs.actuel.duree_retraite, avant.indicateurs.actuel.duree_retraite);
    superieur(valeur(apres.pensions_nettes, "actuel"), valeur(avant.pensions_nettes, "actuel"));
    superieur(valeur(apres.pensions_aspa, "actuel"), valeur(avant.pensions_aspa, "actuel"));
    auMoins(apres.remplacements.actuel.salaire_moyen, avant.remplacements.actuel.salaire_moyen);
  }
});

/**
 * La pension brute du premier mois servi, moins le taux plein de l'année
 * courante et la maladie de sa part complémentaire, sur le minimum
 * vieillesse d'une personne seule de l'année du départ. Le scénario 6, que
 * son âge légal fait partir à 65 ans, se rapporte à celui de son année.
 */
test("la pension nette se rapporte au minimum vieillesse de son année", () => {
  const leCas = cas("salaire_moyen");
  const depart = balayage1970()[0];
  const comparaison = simulateur.simuler(leCas.carriereA(simulateur, 1970, depart.age));
  const taux = tauxDePrelevement(simulateur, comparaison.actuel);
  for (const scenario of SCENARIOS) {
    const brute = pensionAuDepart(simulateur, comparaison, scenario);
    const annee = comparaison.carriereDe(scenario).anneeLiquidation;
    proche(valeur(depart.pensions_nettes, scenario), brute * (1.0 - taux), {}, scenario);
    proche(valeur(depart.pensions_aspa, scenario),
      valeur(depart.pensions_nettes, scenario) / minimumVieillesse(simulateur, annee), {},
      scenario);
  }
  assert.ok(comparaison.departReporte);
  egal(comparaison.carriereDe("notionnel_liberal").anneeLiquidation, 2035);
});

test("le minimum vieillesse est l'ASPA ou ses deux étages", () => {
  const bareme = simulateur.scenarioActuel.minimumVieillesse;
  egal(minimumVieillesse(simulateur, 2026), bareme.plafond(2026)[0]);
  const etages = bareme.deuxEtages(2005);
  proche(minimumVieillesse(simulateur, 2005), etages.avts + etages.supplementaire);
  assert.equal(minimumVieillesse(simulateur, 1930), null);
});

/**
 * La pension nette du départ sur le revenu net de la dernière année
 * travaillée en entier : en euros courants, constants, en salaire moyen.
 */
test("les trois remplacements nets ne diffèrent que par le déflateur", () => {
  const macro = simulateur.macro;
  const leCas = cas("salaire_moyen");
  for (const depart of balayage1970().filter((_, rang) => rang % 4 === 0)) {
    const carriere = leCas.carriereA(simulateur, 1970, depart.age);
    const annee = derniereAnneePleine(carriere);
    egal(annee, depart.annee - 1);
    const remplacement = depart.remplacements.actuel;
    const nets = revenusNets(simulateur, carriere);
    proche(remplacement.courants,
      valeur(depart.pensions_nettes, "actuel") / valeur(nets, annee), { rel: 1e-12 });
    proche(remplacement.constants,
      remplacement.courants / macro.coefficientPrix(annee, depart.annee), { rel: 1e-12 });
    proche(remplacement.salaire_moyen,
      remplacement.courants / macro.coefficientSalaireMoyen(annee, depart.annee),
      { rel: 1e-12 });
  }
});

/**
 * La génération 2000, partie à 64 ans en 2064. Plus la productivité est
 * forte, plus les salaires dépassent les prix : sa pension, qui suit les
 * salaires jusqu'au départ, monte sur le minimum vieillesse, qui suit les
 * prix ; ses pensions, qui suivent les prix ensuite, rendent moins en
 * salaire moyen.
 */
test("sous une productivité plus forte, la pension monte sur l'ASPA", () => {
  const leCas = cas("salaire_moyen");
  const departs = [];
  for (const nom of ["cor_productivite_basse", "cor_reference", "cor_productivite_haute"]) {
    const simulateur = contexte.simulateur({ ...PARAMETRES_DEFAUT, scenario_projection: nom });
    const comparaison = simulateur.simuler(leCas.carriereA(simulateur, 2000, 64.0));
    departs.push(departDe(simulateur, comparaison));
  }
  const aspa = departs.map((depart) => valeur(depart.pensions_aspa, "actuel"));
  const recuperation = departs.map((depart) => depart.indicateurs.actuel.taux_recuperation);
  inferieur(aspa[0], aspa[1]);
  inferieur(aspa[1], aspa[2]);
  superieur(recuperation[0], recuperation[1]);
  superieur(recuperation[1], recuperation[2]);
});

// ---------------------------------------------------------------------------
// L'âge d'équilibre
// ---------------------------------------------------------------------------

/**
 * Le diviseur de référence est celui que le compte prend pour convertir
 * les droits acquis : l'âge de référence, 65 ans, au 1er janvier de l'année
 * de la bascule, 2026 ; la génération 1961 y retrouve le sien à 65 ans
 * exactement.
 */
test("la référence est la génération qui a l'âge de référence à la bascule", () => {
  const reference = referenceDuCompte(simulateur);
  assert.deepStrictEqual([reference.naissance, reference.age, reference.annee],
    [1961.0, 65.0, 2026]);
  const equilibre = ageDEquilibre(simulateur, 1961);
  egal(equilibre.diviseur_reference, simulateur.convertisseur.coefficient(
    65.0, 2026).diviseur);
  assert.deepStrictEqual([equilibre.age, equilibre.au_mois, equilibre.coefficient],
    [65.0, 65.0, 1.0]);
});

/**
 * Au premier mois de l'âge d'équilibre, le diviseur ne dépasse plus celui
 * de la référence : à capital égal, la pension l'atteint ; le mois d'avant,
 * non. Les générations nées avant la référence y sont plus tôt qu'elle, les
 * suivantes plus tard, d'autant plus qu'elles vivront plus longtemps.
 */
test("à l'âge d'équilibre, le capital rend la pension de la référence", () => {
  const ages = [];
  for (const generation of [1940, 1950, 1970, 1980, 2000]) {
    const equilibre = ageDEquilibre(simulateur, generation);
    const auMois = equilibre.au_mois;
    auPlus(diviseurA(simulateur, generation, auMois), equilibre.diviseur_reference, generation);
    inferieur(equilibre.diviseur_reference, diviseurA(simulateur, generation, auMois - 1 / 12),
      generation);
    inferieur(auMois - 1 / 12, equilibre.age, generation);
    auPlus(equilibre.age, auMois, generation);
    egal(equilibre.coefficient > 1.0, generation < 1961, generation);
    ages.push(equilibre.age);
  }
  assert.deepStrictEqual(ages, [...ages].sort((a, b) => a - b));
  inferieur(ages[0], 65.0);
  inferieur(65.0, ages[2]);
});

/**
 * Le taux de préfinancement étant nul, le diviseur est l'espérance de vie
 * résiduelle : à l'âge d'équilibre, chaque génération espère la retraite de
 * la référence, en années, à l'interpolation entre deux mois près.
 */
test("sans préfinancement, l'âge d'équilibre tient la durée de retraite", () => {
  const mortalite = simulateur.mortalite;
  const attendue = mortalite.esperanceResiduelle(65.0, 2026.0, null);
  for (const generation of [1940, 1970, 2000]) {
    const age = ageDEquilibre(simulateur, generation).age;
    proche(mortalite.esperanceResiduelle(age, generation + age, null), attendue,
      { abs: 0.001 }, generation);
  }
});

/**
 * La part de vie de `partDeVie` est celle que le balayage calcule
 * à chaque âge de départ, au millionième ; l'âge où elle rejoint celle de la
 * référence, un homme de la génération 1961 parti à 65 ans, est celui où la
 * courbe du balayage la croise, à l'interpolation entre deux trimestres
 * près.
 */
test("l'âge de part de vie constante est celui que croise le balayage", () => {
  const leCas = cas("salaire_moyen");
  const cible = partDeVie(simulateur, 65.0, 2026.0, "H");
  const points = [];
  for (const depart of balayage1970()) {
    const carriere = leCas.carriereA(simulateur, 1970, depart.age);
    const debut = carriere.anneeLiquidation + carriere.fractionAnneeLiquidation;
    const part = depart.indicateurs.actuel.part_de_vie;
    proche(partDeVie(simulateur, depart.age, debut, "H"), part, { abs: 1e-6 }, depart.age);
    points.push([depart.age, part, debut - depart.age]);
  }
  const [[ageAvant, avant, naissance], [ageApres, apres]] = paires(points)
    .find(([un, deux]) => un[1] > cible && cible >= deux[1]);
  const croisement = ageAvant + (avant - cible) / (avant - apres) * (ageApres - ageAvant);
  proche(ageDePartDeVieConstante(simulateur, naissance, "H"), croisement, { abs: 0.002 });
});

/**
 * Sous la convention du COR, la part de vie est (D − âge) / D : l'âge qui
 * la tient est celui de référence fois le rapport des âges de décès.
 */
test("sous la convention du COR, l'âge suit l'âge de décès", () => {
  const mortalite = simulateur.mortalite;
  for (const generation of [1940, 2000]) {
    const age = ageDePartDeVieConstante(simulateur, generation, null, true);
    proche(age, 65.0 * ageDeDecesCor(mortalite, generation)
      / ageDeDecesCor(mortalite, 1961), { abs: 1e-12 }, generation);
    proche(partDeVie(simulateur, age, generation + age, null, true),
      partDeVie(simulateur, 65.0, 2026.0, null, true), { abs: 1e-12 }, generation);
  }
});

// -- ce que la concordance tenait aussi --------------------------------------------

// `tests/test_cycle_de_vie_portage.py` confrontait le portage au jumeau Python
// sur des carrières de statuts et de générations variés, et vérifiait que ses
// contrôles avaient un objet : ce qu'il exigeait du cycle de vie passe ici, sur
// les mêmes carrières, au retrait du jumeau (action 161).

/** Les carrières de la concordance : un statut, une génération, un sexe, un âge de départ, des enfants. */
function carriereDeLaConcordance(affiliation, generation, sexe, age, enfants = 0) {
  return simulateur.carriereSimple({
    annee_naissance: generation, sexe, affiliation, age_debut: 21, age_liquidation: age,
    niveau_salaire: 1.3, nombre_enfants: enfants,
  });
}

const CARRIERES_DE_LA_CONCORDANCE = [
  ["salarie_prive_non_cadre", 1948, "H", 62.0, 3],
  ["salarie_prive_cadre", 1958, "F", 62.0],
  ["salarie_prive_non_cadre", 1962, "H", 64.0],
  ["salarie_prive_cadre", 1975, "H", 66.0],
  ["fonctionnaire_etat", 1966, "F", 63.0],
  ["artisan", 1970, "H", 64.0],
  ["salarie_prive_non_cadre", 1990, "F", 65.0],
  ["agent_sncf", 1975, "H", 57.0],
  ["commercant", 1936, "H", 65.0],
  ["artisan", 1936, "F", 64.0],
  ["agent_chemins_fer_secondaires", 1930, "H", 55.0],
];

/**
 * Chaque carrière a une fiche de paie, et l'histoire déplace le net — la CSG
 * n'existait pas en 1970. L'agent des chemins de fer secondaires, qui a 60 ans
 * au 1er février 1990, paie sur sa part du régime 2,9 % en 1989, et 1,9 % dès
 * février 1990.
 */
test("les revenus nets ont un objet", () => {
  const prelevements = CARRIERES_DE_LA_CONCORDANCE.map((carriere) => {
    const lui = carriereDeLaConcordance(...carriere);
    const comparaison = simulateur.simuler(lui);
    const nets = revenusNets(simulateur, lui);
    assert.ok(nets !== null && nets.size > 0, carriere.join(" "));
    const taux = prelevementsParAnnee(simulateur, comparaison);
    superieur(taux.size, 20, carriere.join(" "));
    const cor = conventionNette(simulateur, comparaison, true);
    nonNul(indicateursDesSystemes(simulateur, comparaison, cor).actuel.taux_annuite,
      carriere.join(" "));
    return taux;
  });
  superieur(valeur(prelevements[10], 1989), valeur(prelevements[10], 1990));
});

/**
 * Le salarié paie l'impôt de son salaire, puis de sa pension, et l'impôt
 * déplace les indicateurs ; l'artisan déclare son bénéfice, et a ses revenus
 * après impôt ; le parent de trois enfants déclare sa majoration dès les
 * revenus de 2013, et sa pension déclarée y fait un saut que la
 * revalorisation ne fait pas.
 */
test("l'impôt a un objet", () => {
  const sousLImpot = (carriere) => {
    const comparaison = simulateur.simuler(carriereDeLaConcordance(...carriere));
    return { comparaison, systemes: fluxDesSystemes(simulateur, comparaison, { impot: "prix" }) };
  };
  const parent = sousLImpot(CARRIERES_DE_LA_CONCORDANCE[0]).systemes.actuel.impots;
  superieur(valeur(parent, 2013).pension, 1.05 * valeur(parent, 2012).pension);
  const cadre = sousLImpot(CARRIERES_DE_LA_CONCORDANCE[3]);
  const impots = [...cadre.systemes.actuel.impots.values()];
  superieur(impots.filter((impot) => impot.impot > 0).length, 40);
  superieur(impots.filter((impot) => impot.sur_la_pension > 0).length, 10);
  const nette = indicateursDesSystemes(simulateur, cadre.comparaison,
    conventionNette(simulateur, cadre.comparaison));
  const apres = indicateursDesSystemes(simulateur, cadre.comparaison,
    conventionApresImpot(simulateur, cadre.comparaison, false, "prix"));
  for (const scenario of ["actuel", "notionnel_prospectif"]) {
    inferieur(apres[scenario].rendement_reel, nette[scenario].rendement_reel, scenario);
  }
  for (const scenario of ["actuel", "notionnel_retroactif", "notionnel_liberal"]) {
    assert.ok(remplacementApresImpot(simulateur, cadre.comparaison, scenario, "prix",
      cadre.systemes), scenario);
  }
  const artisan = sousLImpot(CARRIERES_DE_LA_CONCORDANCE[5]);
  superieur([...artisan.systemes.actuel.impots.values()]
    .filter((impot) => impot.benefice > 0).length, 30);
  nonNul(artisan.systemes.actuel.revenus_apres_impot);
  nonNul(indicateursDesSystemes(simulateur, artisan.comparaison, conventionApresImpot(
    simulateur, artisan.comparaison, false, "prix")).actuel.taux_annuite);
});

/**
 * Les âges balayés : une carrière longue après impôt, de trimestre en
 * trimestre ; une fonctionnaire partie avant 2007 sous le COR ; un artisan. La
 * carrière longue part avant l'âge légal, le balayage finit à l'âge
 * d'annulation de la décote, que le pas n'atteint pas toujours, chaque âge a
 * son taux de remplacement net, l'impôt y joue, et le minimum vieillesse à
 * deux étages d'un départ d'avant 2007 aussi.
 */
test("le balayage des âges de départ a un objet", () => {
  const balayages = [
    [{ annee_naissance: 1966, sexe: "H", affiliation: "salarie_prive_non_cadre",
      age_debut: 18, niveau_salaire: 1.0 }, 64.0, false, 0.25, "prix"],
    [{ annee_naissance: 1944, sexe: "F", affiliation: "fonctionnaire_etat",
      age_debut: 22, niveau_salaire: 1.3 }, 62.0, true, 0.5, null],
    [{ annee_naissance: 1975, sexe: "H", affiliation: "artisan",
      age_debut: 21, niveau_salaire: 1.3 }, 64.0, false, 0.5, null],
  ].map(([options, age, cor, pas, impot]) => {
    const batir = (a) => simulateur.carriereSimple({ ...options, age_liquidation: a });
    return {
      ages: agesBalayes(simulateur, batir, age, pas),
      departs: balayageDUneCarriere(simulateur, batir, age, cor, pas, impot),
    };
  });
  const [longue, fonctionnaire, artisan] = balayages;
  assert.ok(longue.ages[0] < 62.0 && longue.ages.at(-1) === 67.0, `${longue.ages}`);
  egal(longue.departs.length, longue.ages.length);
  superieur(longue.departs.length, 20);
  for (const lui of longue.departs) {
    assert.ok(lui.remplacements.actuel, `${lui.age}`);
    assert.ok(lui.remplacements_apres_impot.actuel, `${lui.age}`);
    inferieur(lui.pensions_apres_impot.actuel, lui.pensions_nettes.actuel, `${lui.age}`);
  }
  assert.equal(fonctionnaire.departs[0].pensions_apres_impot, null);
  inferieur(fonctionnaire.departs[0].annee, 2007);
  for (const { departs } of balayages) {
    for (const lui of departs) assert.ok(lui.pensions_aspa.actuel, `${lui.age}`);
  }
  assert.ok(artisan.departs.length > 0 && fonctionnaire.departs.length > 0);
});

/** Des flux sans l'impôt de l'indexation de la convention sont refusés, plutôt que de rendre un chiffre faux. */
test("une convention après impôt refuse les flux d'une autre indexation", () => {
  const comparaison = comparaisonDe(simulateur, 1962);
  assert.throws(() => indicateurs(
    fluxDesSystemes(simulateur, comparaison, { impot: "salaire_moyen" }).actuel, simulateur,
    conventionApresImpot(simulateur, comparaison)));
});
