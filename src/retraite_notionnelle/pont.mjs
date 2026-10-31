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
 * - `grille_du_cout` : `{cas: [{cle, carriere, propositions}], scenarios,
 *   parametres}` — chaque case de la grille du coût, sa carrière passée en
 *   données (`carriere_en_donnees` de `pont.py`), simulée sous les paramètres
 *   de la projection : ce que le coût lit de la comparaison, et la proposition
 *   seule sur chacune des carrières nommées de `propositions`.
 * - `carrieres_des_saisies` : `{cas: [{cle, requete, prolonger}]}` — chaque
 *   requête du simulateur, lue par la saisie du portage : ses paramètres, et
 *   la carrière que le site simulerait, en données, pour que le Python la
 *   simule de son moteur (`carriere_des_donnees` de `pont.py`) — celle d'une
 *   saisie par la pension, que l'inversion trouve ; un relevé avec
 *   `prolonger: false` s'en tient à ses années.
 * - `simulations` : `{cas: [{cle, requete}]}` — chaque requête d'un témoin de
 *   simulations, simulée comme `tests/js/moteur.test.js` la simule
 *   (`Contexte.simuler`) : son résultat, `Comparaison.dictionnaire()`, et les
 *   appels de `liquider` qu'il a faits, liquidations d'essai comprises, que
 *   `pont.py` relit sous la table des types du résultat.
 *
 * Il écrit `{resultats, echecs}` : une carrière que le portage refuse en est
 * absente, et son motif est dans `echecs`. Un nombre non fini s'écrit `null`,
 * comme `_fini` de `scripts/construire_temoins.py` l'écrit, et `pont.py` le
 * relit en NaN, sauf dans le résultat d'un témoin, où il reste `null`.
 *
 * Lancé avec `--servir`, il reste ouvert, sur `moteur/donnees.json`, lu une
 * fois : une demande par ligne, `{demande}`, et une réponse par ligne,
 * `{reponse}`, ou `{erreur}` quand le programme a failli. `pont.py` le garde
 * pour les demandes sans paquet, qu'un test fait une à une (action 161,
 * étape 6).
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";

import { DateMois } from "../../moteur/js/calendrier.js";
import { AnneeCarriere, Carriere } from "../../moteur/js/carriere.js";
import { PARAMETRES_DEFAUT, avec } from "../../moteur/js/config.js";
import { Contexte } from "../../moteur/js/contexte.js";
import { appels } from "../../moteur/js/droit/liquidation.js";
import { Saisie } from "../../moteur/js/saisie.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
/** Le contexte sur le paquet de la demande, ou sur celui du dépôt. */
let contexte;

/** Le paquet du dépôt, `moteur/donnees.json`. */
function paquetDuDepot() {
  return JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
}

/** Une erreur du programme, que le pont ne range pas parmi les refus. */
function erreurDuProgramme(erreur) {
  return erreur instanceof TypeError || erreur instanceof ReferenceError
    || erreur instanceof RangeError || erreur instanceof SyntaxError;
}

/** Chaque cas, ou son motif dans `echecs` quand le portage le refuse. */
function parCas(cas, calculer) {
  const resultats = {};
  const echecs = {};
  for (const un of cas) {
    try {
      resultats[un.cle] = calculer(un);
    } catch (erreur) {
      if (erreurDuProgramme(erreur)) {
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

/**
 * La carrière telle que `pont.py` la relit (`carriere_des_donnees`), le chemin
 * inverse de `carriereDesDonnees` : chacun de ses champs, chacune de ses
 * lignes entière, et la chronologie dont elle est la vue. Les mémoires du
 * portage, ses champs privés, ne passent pas.
 */
function carriereEnDonnees(carriere) {
  const publics = (objet) => Object.fromEntries(Object.entries(objet)
    .filter(([nom]) => !nom.startsWith("_")));
  return {
    ...publics(carriere),
    lignes: carriere.lignes.map(publics),
    lignes_apres_depart: carriere.lignes_apres_depart.map(publics),
    dates_entree: Object.fromEntries(Object.entries(carriere.dates_entree)
      .map(([statut, date]) => [statut, [date.annee, date.mois]])),
  };
}

/**
 * Chaque requête du simulateur, lue par la saisie du portage, la seule, comme
 * `tests/js/moteur.test.js` lit celle d'un témoin — ou chaque saisie aux champs
 * de `Saisie`, comme `saisies` les lit : les paramètres de la saisie, et la
 * carrière que le site simulerait (`Contexte.carriere`), que `pont.py` relit
 * sous les types du Python pour les simuler de son moteur.
 */
function carrieresDesSaisies({ cas }) {
  return parCas(cas, ({ requete, saisie: champs, prolonger = true }) => {
    const saisie = champs === undefined
      ? Saisie.depuisRequete(requete, false, contexte.paquet.presomptions)
      : new Saisie(champs);
    const parametres = saisie.parametres(contexte.base);
    let carriere;
    if (saisie.releveActif && !prolonger) {
      // Un relevé que l'appelant a déjà prolongé à sa façon ne se prolonge
      // pas une seconde fois (`scripts/estimation_officielle.py`).
      carriere = contexte.carriereRelevee(contexte.simulateur(parametres), saisie,
        Object.keys(contexte.paquet.periodes_non_travaillees ?? {}), false);
    } else if (saisie.parPension && !saisie.releveActif) {
      // La carrière d'une saisie par la pension est celle que le contexte
      // trouve en inversant la pension, en la simulant.
      carriere = contexte.simuler(saisie).carriere;
    } else {
      carriere = contexte.carriere(saisie);
    }
    return { parametres, carriere: carriereEnDonnees(carriere) };
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

/**
 * La carrière que `pont.py` a passée en données : ses champs, ses lignes
 * entières, la chronologie dont elle est la vue, telle que le Python l'a
 * complétée. Ce que le Python a fait de la carrière — l'entrée tardive d'un
 * fonctionnaire, la part des primes que les conventions du COR portent — se lit
 * ici tel quel : le portage n'en garde pas de copie.
 */
function carriereDesDonnees({ lignes, lignes_apres_depart, dates_entree, ...champs }) {
  const ligne = (donnees) => new AnneeCarriere(donnees);
  return new Carriere({
    ...champs,
    lignes: lignes.map(ligne),
    lignes_apres_depart: lignes_apres_depart.map(ligne),
    dates_entree: Object.fromEntries(Object.entries(dates_entree)
      .map(([statut, [annee, mois]]) => [statut, new DateMois(annee, mois)])),
  });
}

/**
 * Le simulateur sous les paramètres que `pont.py` a passés en données : ceux
 * du Python, que le portage connaît tous. Un paramètre qu'il ne connaîtrait pas
 * arrête le pont, au lieu de se perdre.
 */
function simulateurSous(parametres) {
  const inconnus = Object.keys(parametres)
    .filter((nom) => !Object.hasOwn(PARAMETRES_DEFAUT, nom));
  if (inconnus.length > 0) {
    throw new Error(`paramètres que le portage ne connaît pas : ${inconnus.join(", ")}`);
  }
  return contexte.simulateur(avec(PARAMETRES_DEFAUT, parametres));
}

/** Ce que le coût lit de la proposition calculée sur `carriere` (`_volet_brut` de `cout.py`). */
function voletDuCout(resultat, carriere) {
  const garantie = resultat.garantie_vieillesse;
  const pilier = resultat.capitalisation;
  return {
    annee_liquidation: carriere.anneeLiquidation,
    revenus: carriere.lignes.filter((ligne) => ligne.cotise)
      .map((ligne) => [ligne.annee, ligne.revenu]),
    garantie: {
      annee_ouverture: garantie.annee_ouverture,
      pension_contributive: garantie.pension_contributive,
      ressources: garantie.ressources,
      rente_capitalisee: garantie.rente_capitalisee,
    },
    cotisations: resultat.compte.cotisations.map((ligne) => [ligne.annee, ligne.cotisation]),
    pilier: pilier === null || !pilier.actif ? null : {
      annees: pilier.annees.map((annee) => [annee.annee, annee.versement_brut,
        annee.frais_versement, annee.frais_gestion, annee.encours]),
      capital: pilier.capital,
      diviseur: pilier.conversion.diviseur,
      rente_annuelle: pilier.rente_annuelle,
    },
  };
}

/**
 * Chaque case de la grille du coût : ce que `cout.py` lit de la comparaison
 * (`_simulations_en_python`, son jumeau Python), et la proposition seule sur
 * chaque carrière nommée de `propositions`. Seule la comparaison peut refuser
 * une case, comme `calculer_cas_types` ne range parmi les échecs que ce que
 * la simulation refuse.
 */
function grilleDuCout({ cas, scenarios, parametres }) {
  const simulateur = simulateurSous(parametres);
  const resultats = {};
  const echecs = {};
  for (const { cle, carriere: donnees, propositions } of cas) {
    const carriere = carriereDesDonnees(donnees);
    let comparaison;
    try {
      comparaison = simulateur.simuler(carriere);
    } catch (erreur) {
      if (erreurDuProgramme(erreur)) {
        throw erreur;
      }
      echecs[cle] = String(erreur.message ?? erreur);
      continue;
    }
    const actuel = comparaison.actuel;
    resultats[cle] = {
      pensions: parScenario(scenarios, (scenario) => comparaison.enEurosConstants(
        comparaison[scenario].pension_annuelle, scenario)),
      depart_reporte: comparaison.departReporte,
      liberal: voletDuCout(comparaison.notionnel_liberal,
        comparaison.carriereDe("notionnel_liberal")),
      coefficient_liberal: comparaison.coefficientDe("notionnel_liberal"),
      prelevement: simulateur.constructeurPrelevement.construire(
        carriere, carriere.anneeLiquidation, carriere.premiereAnnee,
      ).cotisations.map((ligne) => [ligne.annee, ligne.cotisation]),
      pension_actuelle: actuel.pension_annuelle,
      pensions_par_regime: actuel.pensions_par_regime
        .map((pension) => [pension.regime, pension.montant]),
      population: simulateur.convertisseur.populationPourPension(
        actuel.pension_annuelle, carriere.anneeLiquidation, carriere),
      propositions: Object.fromEntries(Object.entries(propositions).map(([nom, lue]) => {
        const autre = carriereDesDonnees(lue);
        return [nom, voletDuCout(simulateur.proposition(autre), autre)];
      })),
    };
  }
  return { resultats, echecs };
}

/**
 * Chaque requête d'un témoin de simulations, lue et simulée comme
 * `tests/js/moteur.test.js` la lit et la simule : le résultat entier, et les
 * appels de `liquider` que sa simulation a faits, liquidations d'essai
 * comprises (docs/architecture.md, § 7.8).
 */
function simulations({ cas }) {
  return parCas(cas, ({ requete }) => {
    const saisie = Saisie.depuisRequete(requete, false, contexte.paquet.presomptions);
    const avant = appels();
    const resultat = contexte.simuler(saisie).dictionnaire();
    return { resultat, appels_liquider: appels() - avant };
  });
}

const LECTURES = {
  carrieres, saisies, grille_du_cout: grilleDuCout, carrieres_des_saisies: carrieresDesSaisies,
  simulations,
};

/** La réponse à une demande, qui porte une seule des `LECTURES`. */
function repondre(demande) {
  const [lecture] = Object.keys(demande);
  if (Object.keys(demande).length !== 1 || !(lecture in LECTURES)) {
    throw new Error(`demande attendue : une seule de ${Object.keys(LECTURES).join(", ")}`);
  }
  return LECTURES[lecture](demande[lecture]);
}

if (process.argv.includes("--servir")) {
  contexte = new Contexte(paquetDuDepot());
  for await (const ligne of createInterface({ input: process.stdin, crlfDelay: Infinity })) {
    let sortie;
    try {
      sortie = { reponse: repondre(JSON.parse(ligne).demande) };
    } catch (erreur) {
      sortie = { erreur: String(erreur?.stack ?? erreur) };
    }
    process.stdout.write(`${JSON.stringify(sortie)}\n`);
  }
} else {
  const { paquet, demande } = JSON.parse(readFileSync(0, "utf8"));
  contexte = new Contexte(paquet ?? paquetDuDepot());
  process.stdout.write(JSON.stringify(repondre(demande)));
}
