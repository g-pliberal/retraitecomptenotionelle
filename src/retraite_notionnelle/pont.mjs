/**
 * Le pont : ce que la fabrique fait calculer au moteur JavaScript, par node
 * (action 161, étape 5 ; note de décision 0003). `pont.py` le lance.
 *
 * Il lit sur son entrée standard `{paquet, demande}`. `paquet` est celui sur
 * lequel calculer : celui que la fabrique s'apprête à écrire, sans ses
 * agrégats, pour que le portage calcule sur les données du jour, et non sur
 * le paquet qu'elle va remplacer ; `null` lit `moteur/donnees.json`. `demande`
 * en porte une seule de ces lectures :
 *
 * - `carrieres` : `{cas: [{cle, options}], scenarios}` — chaque carrière d'un
 *   seul statut, aux options de `carriereSimple`, simulée sous les réglages de
 *   référence : l'année de son départ et celle de chaque scénario, l'écart de
 *   chacun au système actuel, pilier capitalisé compris (`variationTotale`),
 *   la pension du système actuel et la durée qu'il requiert ; la pension de
 *   chaque scénario, pilier capitalisé compris, et la rente des points
 *   volontaires ; et, pour qui est déjà parti, ce que le système actuel et
 *   chaque scénario lui servent aujourd'hui (`aujourd_hui`), sinon `null`.
 * - `saisies` : `{cas: [{cle, saisie}], scenarios}` — chaque saisie, simulée
 *   comme le site la simule (`Contexte.simuler`) : la fiche de paie de l'année
 *   de référence sous le droit en vigueur, ou `null` sans fiche, le passage
 *   aux euros constants, la pension du système actuel et celle de chaque
 *   scénario.
 *
 * Il écrit `{resultats, echecs}` : une carrière que le portage refuse en est
 * absente, et son motif est dans `echecs`. Un nombre non fini s'écrit `null`,
 * que `pont.py` relit en NaN.
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte } from "../../moteur/js/contexte.js";
import { Saisie } from "../../moteur/js/saisie.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const { paquet, demande } = JSON.parse(readFileSync(0, "utf8"));
const contexte = new Contexte(
  paquet ?? JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8")));

/** Chaque cas, ou son motif dans `echecs` quand le portage le refuse. */
function parCas(cas, calculer) {
  const resultats = {};
  const echecs = {};
  for (const un of cas) {
    try {
      resultats[un.cle] = calculer(un);
    } catch (erreur) {
      if (erreur instanceof TypeError || erreur instanceof ReferenceError
          || erreur instanceof RangeError || erreur instanceof SyntaxError) {
        throw erreur;
      }
      echecs[un.cle] = String(erreur.message ?? erreur);
    }
  }
  return { resultats, echecs };
}

/** Ce que `lire` rend de chaque scénario, sous sa clé. */
function parScenario(scenarios, lire) {
  return Object.fromEntries(scenarios.map((scenario) => [scenario, lire(scenario)]));
}

function carrieres({ cas, scenarios }) {
  const simulateur = contexte.simulateur();
  return parCas(cas, ({ options }) => {
    const interruptions = new Map(Object.entries(options.interruptions ?? {})
      .map(([annee, motif]) => [Number(annee), motif]));
    const comparaison = simulateur.simuler(simulateur.carriereSimple({ ...options, interruptions }));
    const aujourdHui = comparaison.aujourd_hui;
    return {
      annee_liquidation: comparaison.carriere.anneeLiquidation,
      annees_liquidation: parScenario(scenarios,
        (scenario) => comparaison.carriereDe(scenario).anneeLiquidation),
      variations: parScenario(scenarios, (scenario) => comparaison.variationTotale(scenario)),
      pension_annuelle: comparaison.actuel.pension_annuelle,
      trimestres_requis: comparaison.actuel.trimestres_requis,
      pensions_totales: parScenario(scenarios, (scenario) => comparaison.pensionTotale(scenario)),
      rentes_volontaires: parScenario(scenarios,
        (scenario) => comparaison.renteCapitaliseeVolontaire(scenario)),
      aujourd_hui: aujourdHui === null ? null : {
        pension_annuelle: aujourdHui.pension("actuel"),
        pensions_totales: parScenario(scenarios, (scenario) => aujourdHui.pensionTotale(scenario)),
        rente_capitalisee_volontaire: aujourdHui.rente_capitalisee_volontaire,
      },
    };
  });
}

function saisies({ cas, scenarios }) {
  return parCas(cas, ({ saisie }) => {
    const comparaison = contexte.simuler(new Saisie(saisie));
    const fiche = comparaison.remuneration?.reference.droitEnVigueur ?? null;
    return {
      fiche: fiche === null ? null : {
        annee: fiche.annee,
        brut: fiche.brut,
        net: fiche.net,
        retraite_totale: fiche.retraiteTotale,
        retraite_employeur: fiche.retraiteEmployeur,
      },
      coefficient_euros_constants: comparaison.coefficient_euros_constants,
      pension_annuelle: comparaison.actuel.pension_annuelle,
      pensions: parScenario(scenarios, (scenario) => comparaison[scenario].pension_annuelle),
    };
  });
}

const LECTURES = { carrieres, saisies };
const [lecture] = Object.keys(demande);
if (Object.keys(demande).length !== 1 || !(lecture in LECTURES)) {
  throw new Error(`demande attendue : une seule de ${Object.keys(LECTURES).join(", ")}`);
}
process.stdout.write(JSON.stringify(LECTURES[lecture](demande[lecture])));
