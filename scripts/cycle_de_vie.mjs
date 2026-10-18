/**
 * Le cycle de vie des cas types, calculé par le portage : ce que
 * `scripts/cycle_de_vie.py` imprime.
 *
 * Les cas types du COR ne se bâtissent qu'en Python (`castypes.py`, que le
 * coût lit) : le script en résout chaque case — les options de sa carrière,
 * l'âge où le pilote la fait partir — et ce programme fait le reste, comme le
 * site le fait d'une saisie (action 161, étape 5, le pont). Il reçoit sur son
 * entrée standard une demande JSON, une seule de ces quatre :
 *
 * - `grille` : `{cas: [{cle, options}], cor, impot}` — les indicateurs des six
 *   systèmes de chaque case, sous la convention du dépôt, du COR, ou après
 *   impôt (`indicateursDesSystemes`) ;
 * - `etages` : `{cas: [{cle, options}], impot}` — la pension du départ de
 *   chaque case, étage par étage, et ses taux de remplacement, avant ou après
 *   impôt (`pensionParEtage`) ;
 * - `ages` : `{cas: [{cle, productivite, options, age}], cor, impot, pas}` —
 *   chaque case à chacun de ses âges de départ, sous l'hypothèse de
 *   productivité qu'elle nomme (`balayageDUneCarriere`) ;
 * - `equilibre` : `{generations, cas: [{cle, options}]}` — la référence du
 *   compte, les âges d'équilibre de chaque génération sur la table commune,
 *   et ceux de chaque cas type, sur la mortalité de la population où son
 *   salaire le range, celle de son diviseur (`ageDEquilibre`,
 *   `ageDePartDeVieConstante`) ;
 *
 * et écrit sur la sortie standard ce que le script écrit sous `--json`. Une
 * case que le portage refuse en est absente, comme la grille Python écarte
 * les siennes ; son motif va dans `echecs`.
 *
 *     python scripts/cycle_de_vie.py …    # le seul lecteur
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { PARAMETRES_DEFAUT } from "../moteur/js/config.js";
import { Contexte } from "../moteur/js/contexte.js";
import {
  ageDEquilibre, ageDePartDeVieConstante, balayageDUneCarriere, Convention, conventionApresImpot,
  conventionCor, fluxDesSystemes, indicateursDesSystemes, pensionParEtage, referenceDuCompte,
  SCENARIOS,
} from "../moteur/js/cycle-de-vie.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..");
const contexte = new Contexte(JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));
const demande = JSON.parse(readFileSync(0, "utf8"));

/** La carrière d'une case : ses options, les interruptions en `Map` d'années. */
function carriere(simulateur, options, age = options.age_liquidation) {
  const interruptions = new Map(Object.entries(options.interruptions ?? {})
    .map(([annee, motif]) => [Number(annee), motif]));
  return simulateur.carriereSimple({ ...options, interruptions, age_liquidation: age });
}

const parScenario = (valeurs) => Object.fromEntries(Object.entries(valeurs)
  .map(([scenario, indicateurs]) => [scenario, indicateurs.dictionnaire()]));

/** Chaque case, ou son motif dans `echecs` quand le portage la refuse. */
function parCase(cas, calculer) {
  const resultats = {};
  const echecs = {};
  for (const une of cas) {
    try {
      resultats[une.cle] = calculer(une);
    } catch (erreur) {
      if (erreur instanceof TypeError || erreur instanceof ReferenceError
          || erreur instanceof RangeError || erreur instanceof SyntaxError) {
        throw erreur;
      }
      echecs[une.cle] = String(erreur.message ?? erreur);
    }
  }
  return { resultats, echecs };
}

function grille({ cas, cor, impot }) {
  const simulateur = contexte.simulateur();
  return parCase(cas, ({ options }) => {
    const comparaison = simulateur.simuler(carriere(simulateur, options));
    let convention;
    if (impot !== null) {
      convention = conventionApresImpot(simulateur, comparaison, cor, impot);
    } else if (cor) {
      convention = conventionCor(simulateur, comparaison);
    } else {
      convention = new Convention();
    }
    return parScenario(indicateursDesSystemes(simulateur, comparaison, convention));
  });
}

function etages({ cas, impot }) {
  const simulateur = contexte.simulateur();
  return parCase(cas, ({ options }) => {
    const comparaison = simulateur.simuler(carriere(simulateur, options));
    const systemes = fluxDesSystemes(simulateur, comparaison, { nets: true, impot });
    return Object.fromEntries(SCENARIOS.map((scenario) => [scenario,
      pensionParEtage(simulateur, comparaison, scenario, systemes).dictionnaire()]));
  });
}

function ages({ cas, cor, impot, pas }) {
  return parCase(cas, ({ productivite, options, age }) => {
    const simulateur = contexte.simulateur({ ...PARAMETRES_DEFAUT,
                                             scenario_projection: productivite });
    const batir = (a) => carriere(simulateur, options, a);
    return balayageDUneCarriere(simulateur, batir, age, cor, pas, impot).map((depart) => ({
      age: depart.age,
      annee: depart.annee,
      ...Object.fromEntries(SCENARIOS.map((scenario) => [scenario, {
        ...depart.indicateurs[scenario].dictionnaire(),
        pension_nette: depart.pensions_nettes[scenario],
        pension_aspa: depart.pensions_aspa[scenario],
        remplacement_net: depart.remplacements[scenario] === null
          ? null : { ...depart.remplacements[scenario] },
        remplacement_apres_impot: depart.remplacements_apres_impot === null
          ? null : depart.remplacements_apres_impot[scenario],
      }])),
    }));
  });
}

function equilibre({ generations, cas }) {
  const simulateur = contexte.simulateur();
  const tableCommune = Object.fromEntries(generations.map((generation) => [String(generation), {
    part_de_vie_cor: ageDePartDeVieConstante(simulateur, generation, null, true),
    part_de_vie_unisexe: ageDePartDeVieConstante(simulateur, generation, null),
    part_de_vie_hommes: ageDePartDeVieConstante(simulateur, generation, "H"),
    part_de_vie_femmes: ageDePartDeVieConstante(simulateur, generation, "F"),
    diviseur: ageDEquilibre(simulateur, generation),
  }]));
  // Le cas type n'entre dans ses âges que par la mortalité de son diviseur, la
  // population où son salaire le range (`Convertisseur.populationDe`) — sous
  // le rattachement par la pension, une variante, qui la lit sur une pension
  // que l'âge d'équilibre ne connaît pas, celle du salaire reste —, et par son
  // sexe, pour la part de vie. Ni l'une ni l'autre n'entrent dans la part de
  // vie des indicateurs, ni dans l'âge de part de vie constante sous la
  // convention du COR, qui ne dépend que de la génération.
  const { resultats, echecs } = parCase(cas, ({ options }) => {
    const une = carriere(simulateur, options);
    const generation = options.annee_naissance;
    const population = simulateur.convertisseur.populationDe(une);
    return {
      generation,
      age_de_depart: une.age_liquidation,
      population,
      part_de_vie: ageDePartDeVieConstante(simulateur, generation, une.sexe, false, population),
      diviseur: ageDEquilibre(simulateur, generation, une.sexe, population),
    };
  });
  return { reference: referenceDuCompte(simulateur), table_commune: tableCommune,
           cas_types: resultats, echecs };
}

const MODES = { grille, etages, ages, equilibre };
const [mode] = Object.keys(demande);
if (Object.keys(demande).length !== 1 || !(mode in MODES)) {
  throw new Error(`demande attendue : une seule de ${Object.keys(MODES).join(", ")}`);
}
process.stdout.write(JSON.stringify(MODES[mode](demande[mode])));
