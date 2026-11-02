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
 * - `scenario_actuel` : `{cas: [{cle, requete, prolonger}]}` — chaque requête
 *   du simulateur, simulée comme le site la simule, un relevé avec
 *   `prolonger: false` s'en tenant à ses années : ce que les confrontations
 *   aux références extérieures lisent de son scénario 1
 *   (`scenarioActuelEnDonnees`), dont une part qu'aucun témoin n'écrit.
 * - `droit` : `{appels: [{cle, fonction, arguments}], carrieres, parametres}` —
 *   chaque appel d'une fonction du droit que le pont porte
 *   (`FONCTIONS_DU_DROIT`), sur des carrières que le Python a bâties, passées
 *   en données, sous les paramètres du simulateur : ce qu'elle rend.
 * - `ages_de_depart` : `{cas: [{cle, regle, options}], parametres, variante,
 *   primes}` — chaque cas type de la grille, ce que sa règle de départ lit et
 *   les options de sa carrière d'un seul statut sans l'âge
 *   (`CasType.pour_le_portage` de `castypes.py`), daté par le pilote du
 *   portage (`ageDeDepart`) sous les paramètres de la demande, sa part des
 *   primes projetée comme le COR la projette quand `primes` porte le
 *   traitement relatif de chaque année : l'âge de son départ.
 * - `carrieres_de_la_grille` : `{cas: [{cle, regle, options, entree, rendre}],
 *   parametres, variante, primes}` — chaque case de la grille du coût, datée
 *   comme `ages_de_depart` la date, et bâtie : d'un seul statut, ou de deux
 *   métiers quand `entree` décrit l'entrée tardive d'un fonctionnaire ; écartée
 *   sous le motif du Python quand le droit l'écarte. Selon `rendre`, l'année
 *   et le mois de son départ (`depart`), ou la carrière, en données, et les
 *   deux que l'âge légal de la proposition en dérive (`carriere`).
 *   Un cas type de la grille élargie (`CasTypeLarge` de
 *   `scripts/grille_large.py`, étape 7) y ajoute, dans ces deux lectures,
 *   son `parcours`, que le portage bâtit au lieu de la carrière d'un seul
 *   statut, et l'`attente` de son départ, qu'il pose sur l'âge que le pilote
 *   fixe (`ageDuCas`) ; un âge qu'elle fixe est marqué `attendu`.
 * - `departs_des_cas` : `{cas: [{cle, regle, options, parcours, entree,
 *   attente, lire}], parametres, primes}` — chaque cas type daté comme
 *   `ages_de_depart` le date, puis, sauf sous `lire: "age"`, ce que
 *   l'échéancier lit à son départ : les mesures de `scripts/grille_large.py`.
 * - `debuts_de_la_surcote` : `{cas: [{cle, …, plein, recherche}], parametres,
 *   primes}` — le premier âge d'où le modèle sert une surcote à la pension de
 *   fonctionnaire de chaque cas type, cherché autour de `plein`.
 * - `avantages` : `{cas: [{cle, options, carriere, scenario}], parametres}` —
 *   chaque case du coût des avantages non contributifs, bâtie de ses options
 *   (`carriere_variante` d'`avantages.py`), écartée comme le droit l'écarte,
 *   liquidée au scénario 1 : ce que la décomposition en lit ; et la pension
 *   et la durée requise de chaque contrefactuelle demandée — ses périodes non
 *   travaillées changées (`carriere`), un scénario neutralisé (`scenario`,
 *   `scenariosNeutralises`) —, sauf celle qui n'a rien à perdre. Un appel du
 *   `droit` liquide de même sous un scénario neutralisé (`neutralise`).
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

import { DateMois, enMois, origineDesAges } from "../../moteur/js/calendrier.js";
import { AnneeCarriere, Carriere } from "../../moteur/js/carriere.js";
import { valeur as valeurPresumee } from "../../moteur/js/chronologie.js";
import { ConstructeurCompte } from "../../moteur/js/compte.js";
import { PARAMETRES_DEFAUT, avec } from "../../moteur/js/config.js";
import { Contexte } from "../../moteur/js/contexte.js";
import { Echeancier } from "../../moteur/js/echeancier.js";
import {
  FICHE_DE_L_APPRENTISSAGE, FICHE_DES_MILITAIRES, FICHES_DES_EMPLOIS, contrats,
} from "../../moteur/js/droit/compter.js";
import { REGIMES_CODE_DES_PENSIONS } from "../../moteur/js/droit/coordonner.js";
import * as cumul from "../../moteur/js/droit/cumul.js";
import * as departs from "../../moteur/js/droit/departs.js";
import { foyerEtNet } from "../../moteur/js/droit/foyer.js";
import * as invalidite from "../../moteur/js/droit/invalidite.js";
import { appels } from "../../moteur/js/droit/liquidation.js";
import * as liquider from "../../moteur/js/droit/liquider.js";
import * as ouvrir from "../../moteur/js/droit/ouvrir.js";
import * as releve from "../../moteur/js/droit/releve.js";
import * as reversion from "../../moteur/js/droit/reversion.js";
import { ageDeDepart } from "../../moteur/js/pilote.js";
import { BORNES_ASSIETTE, CarriereLongue } from "../../moteur/js/regimes.js";
import { ficheDepuisBrut } from "../../moteur/js/remuneration.js";
import { faireVivre } from "../../moteur/js/revalorisation.js";
import { Saisie } from "../../moteur/js/saisie.js";
import { ScenarioActuel } from "../../moteur/js/scenario-actuel.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
/** Le contexte sur le paquet de la demande, ou sur celui du dépôt. */
let contexte;

/** Le paquet du dépôt, `moteur/donnees.json`. */
function paquetDuDepot() {
  return JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
}

/**
 * Les valeurs que la garde des présomptions fait dire au vocabulaire du
 * Python (`DECALAGES` de `tests/conftest.py` ; action 135, levier 2) : le 1er
 * du mois, les enfants trois ans plus tôt, le mariage trois ans plus tard.
 */
const DECALAGES = { jour_de_naissance: 1, naissance_des_enfants: 27, mariage_des_conjoints: 30 };

/**
 * Le paquet, ses présomptions décalées quand `PRESOMPTIONS_DECALEES` est
 * posée : le portage lit alors ce que lit le Python, et un test qui écrit une
 * valeur présumée en dur échoue d'un côté comme de l'autre.
 */
function sousLaGarde(paquet) {
  if (!process.env.PRESOMPTIONS_DECALEES) return paquet;
  const presomptions = { ...paquet.presomptions };
  for (const [nom, valeur] of Object.entries(DECALAGES)) {
    presomptions[nom] = { ...presomptions[nom], valeur };
  }
  return { ...paquet, presomptions };
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
 * Le simulateur d'une saisie par le relevé, et la carrière du relevé tel
 * quel : un relevé que l'appelant a déjà prolongé à sa façon ne se prolonge
 * pas une seconde fois jusqu'au départ (`scripts/estimation_officielle.py`).
 */
function releveTelQuel(saisie) {
  const simulateur = contexte.simulateur(saisie.parametres(contexte.base));
  return [simulateur, contexte.carriereRelevee(simulateur, saisie,
    Object.keys(contexte.paquet.periodes_non_travaillees ?? {}), false)];
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
      [, carriere] = releveTelQuel(saisie);
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
 * entières, la chronologie dont elle est la vue, telle que le Python la tient
 * — celle que le portage a bâtie (`carrieresDeLaGrille`) et que le Python a
 * relue, ou celle qu'il bâtit encore, pour la grille large, dont les cas types
 * datent et bâtissent autrement leurs carrières. Elle se lit ici telle quelle.
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
 * La carrière d'un cas type de fonctionnaire, sa part des primes portée comme
 * le COR la projette (`primes_projetees` de `castypes.py`) : à rémunération
 * égale, le traitement d'une année vaut ce qu'il valait, fois le traitement
 * relatif — `relatif`, année par année, que le Python lit
 * (`primes_projetees_en_donnees`). Une ligne sans primes, ou d'une année où le
 * traitement suit le salaire moyen, reste la même, et la carrière aussi quand
 * aucune ne change.
 */
function primesProjetees(carriere, relatif) {
  const lignes = carriere.lignes.map((ligne) => {
    if (!(ligne.part_primes > 0)) {
      return ligne;
    }
    const rapport = relatif[ligne.annee];
    if (rapport === undefined) {
      throw new RangeError(`traitement relatif absent de la demande : ${ligne.annee}`);
    }
    return rapport === 1 ? ligne
      : new AnneeCarriere({ ...ligne, part_primes: 1 - (1 - ligne.part_primes) * rapport });
  });
  return lignes.every((ligne, rang) => ligne === carriere.lignes[rang])
    ? carriere : carriere.avecLignes(lignes);
}

/**
 * La carrière d'un seul statut d'un cas type, liquidée à l'âge qu'on lui
 * demande (`CasType._carriere` de `castypes.py`) : ses options, sans l'âge,
 * et, quand `primes` porte le traitement relatif de chaque année — sous les
 * conventions du COR —, ses primes projetées. Ou, pour un cas type de la
 * grille élargie qui en décrit un (`CasTypeLarge._carriere` de
 * `scripts/grille_large.py`, action 161, étape 7), son parcours : ses
 * métiers bout à bout, son temps partiel, sans primes projetées.
 */
function carriereDuCasType(simulateur, options, primes, parcours = null) {
  if (parcours !== null) {
    const etapes = optionsDeCarriere(parcours);
    return (age) => simulateur.carriereParcours({ ...etapes, age_liquidation: age });
  }
  const lues = optionsDeCarriere(options);
  return (age) => {
    const carriere = simulateur.carriereSimple({ ...lues, age_liquidation: age });
    return primes === null ? carriere : primesProjetees(carriere, primes);
  };
}

/**
 * La carrière d'un cas type liquidée à `age` (`CasType.carriere_a` de
 * `castypes.py`) : celle que son pilote date (`batir`), ou, quand `entree`
 * décrit l'entrée tardive d'un fonctionnaire sous les conventions du COR, ses
 * deux métiers.
 */
function carriereFinale(simulateur, entree, batir, primes) {
  return (age) => (entree === null ? batir(age)
    : carriereEntreeTardive(simulateur, entree, age, primes));
}

/**
 * Le premier âge d'où le modèle sert une surcote à la pension de
 * fonctionnaire d'un cas type, au trimestre près, sur les trimestres comptés
 * de l'âge `plein` de son taux plein, sa carrière bâtie à chaque âge par
 * `construire` : celui qui précède le premier départ qu'il surcote, cherché
 * en doublant le pas, puis par dichotomie, sur `recherche` trimestres de part
 * et d'autre ; `null` quand le modèle n'en sert aucune dans ceux qui suivent.
 * Portage de `debut_de_la_surcote` de `scripts/grille_large.py` (étape 7).
 */
function debutDeLaSurcote(simulateur, construire, plein, recherche) {
  const surcote = (trimestres) => simulateur.echeancier(construire(plein + trimestres / 4.0))
    .auDepart.pensions_par_regime
    .some((pension) => REGIMES_CODE_DES_PENSIONS.has(pension.regime) && pension.surcote > 0.0);
  let bas;
  let haut;
  if (surcote(0)) {
    [bas, haut] = [-1, 0];
    while (bas > -recherche && surcote(bas)) {
      [bas, haut] = [Math.max(2 * bas, -recherche), bas];
    }
  } else {
    [bas, haut] = [0, 1];
    while (!surcote(haut)) {
      if (haut >= recherche) {
        return null;
      }
      [bas, haut] = [haut, Math.min(2 * haut, recherche)];
    }
  }
  while (haut - bas > 1) {
    const milieu = Math.floor((bas + haut) / 2);
    if (surcote(milieu)) {
      haut = milieu;
    } else {
      bas = milieu;
    }
  }
  return plein + (haut - 1) / 4.0;
}

/**
 * L'âge du départ d'un cas type, `{regle, options, parcours, entree,
 * attente}` (`CasType.pour_le_portage` de `castypes.py`) : celui que le
 * pilote fixe (`ageDeDepart`) sur la carrière que ses options ou son parcours
 * décrivent, puis, hors de la variante « absolu », l'attente d'un cas type de
 * la grille élargie (`CasTypeLarge.age_liquidation_pour` de
 * `scripts/grille_large.py`, étape 7) : le plancher que l'âge légal de sa
 * génération et l'attente lui posent, ou l'attente qui court du premier âge
 * où le modèle sert une surcote à sa carrière (`debutDeLaSurcote`). Avec
 * l'âge, `attendu`, quand l'attente le fixe — le Python le tient alors pour
 * un flottant (`castypes.age_lu`) —, et la carrière que le pilote date.
 */
function ageDuCas(simulateur, cas, primes, variante) {
  const batir = carriereDuCasType(simulateur, cas.options, primes, cas.parcours ?? null);
  const age = ageDeDepart(simulateur.scenarioActuel, batir, cas.regle, variante);
  const attente = cas.attente ?? null;
  if (attente === null || variante === "absolu") {
    return { age, attendu: false, batir };
  }
  let depart;
  if (Object.hasOwn(attente, "depuis_la_surcote")) {
    const debut = debutDeLaSurcote(simulateur,
      carriereFinale(simulateur, cas.entree ?? null, batir, primes), age, attente.recherche);
    depart = debut === null ? age : Math.max(age, debut + attente.depuis_la_surcote);
  } else {
    depart = Math.max(age, attente.plancher);
  }
  return { age: depart, attendu: depart > age, batir };
}

/**
 * Le départ de chaque cas type, `{cle, regle, options, parcours, entree,
 * attente, lire}`, sous `parametres` — ce que lisent les mesures de
 * `scripts/grille_large.py` (`Departs`, étape 7) : l'âge que son pilote fixe
 * sous la variante du droit (`ageDuCas`), `attendu` quand l'attente le fixe ;
 * et, sauf sous `lire: "age"`, ce que l'échéancier lit à ce départ
 * (`Simulateur.echeancier`) — le taux, la durée requise et la durée validée,
 * le motif de l'ouverture, chaque avantage appliqué, `[code, montant]`,
 * chaque pension de régime, `[regime, montant, surcote]` —, ou le motif qui
 * le refuse (`refus`), l'âge gardé, comme le Python lit l'âge sans le départ.
 */
function departsDesCas({ parametres, primes, cas }) {
  const simulateur = simulateurSous(parametres);
  return parCas(cas, (un) => {
    const { age, attendu, batir } = ageDuCas(simulateur, un, primes, "droit");
    const lu = attendu ? { age, attendu } : { age };
    if (un.lire === "age") {
      return lu;
    }
    let depart;
    try {
      depart = simulateur.echeancier(
        carriereFinale(simulateur, un.entree ?? null, batir, primes)(age)).auDepart;
    } catch (erreur) {
      if (erreurDuProgramme(erreur)) {
        throw erreur;
      }
      return { ...lu, refus: String(erreur.message ?? erreur) };
    }
    return {
      ...lu,
      taux_liquidation: depart.taux_liquidation,
      trimestres_requis: depart.trimestres_requis,
      trimestres_valides: depart.trimestres_valides,
      motif_ouverture: depart.motif_ouverture,
      avantages_appliques: depart.avantages_appliques.map(({ code, montant }) => [code, montant]),
      pensions_par_regime: depart.pensions_par_regime
        .map(({ regime, montant, surcote }) => [regime, montant, surcote]),
    };
  });
}

/**
 * Le premier âge d'où le modèle sert une surcote à la pension de
 * fonctionnaire de chaque cas type, `{cle, regle, options, parcours, entree,
 * plein, recherche}`, sur les trimestres comptés de l'âge `plein`
 * (`debutDeLaSurcote`), ou `null` : `debut_de_la_surcote` de
 * `scripts/grille_large.py` (étape 7).
 */
function debutsDeLaSurcote({ parametres, primes, cas }) {
  const simulateur = simulateurSous(parametres);
  return parCas(cas, (un) => debutDeLaSurcote(simulateur, carriereFinale(simulateur,
    un.entree ?? null, carriereDuCasType(simulateur, un.options, primes, un.parcours ?? null),
    primes), un.plein, un.recherche));
}

/**
 * L'âge de départ de chaque cas type, `{cle, regle, options, parcours,
 * attente}` (`ageDuCas`) : le coût fait dater ici les cas types de sa grille
 * (action 161, étape 6), dont le Python garde les définitions, et ceux de la
 * grille élargie (étape 7). Avec les âges, les clés de ceux que l'attente fixe
 * (`attendus`).
 */
function agesDeDepart({ parametres, variante, primes, cas }) {
  const simulateur = simulateurSous(parametres);
  const attendus = [];
  const { resultats, echecs } = parCas(cas, (un) => {
    const { age, attendu } = ageDuCas(simulateur, un, primes, variante);
    if (attendu) {
      attendus.push(un.cle);
    }
    return age;
  });
  return { resultats, echecs, attendus };
}

/**
 * La carrière d'un fonctionnaire entré tard dans son régime, sous les
 * conventions du COR (`CasType._carriere_entree_tardive` de `castypes.py`) :
 * ses deux métiers, l'un après l'autre, que le Python décrit (`entree`), et ses
 * primes projetées. Le départ est celui que le pilote a fixé sur la carrière
 * d'un seul statut : l'entrée tardive ne fait partir personne plus tard.
 */
function carriereEntreeTardive(simulateur, entree, age, primes) {
  const carriere = simulateur.carriereParcours({
    ...optionsDeCarriere(entree), age_liquidation: age,
  });
  return primes === null ? carriere : primesProjetees(carriere, primes);
}

/**
 * Ce qui écarte une case de la grille (`carriere_de_la_grille` de
 * `castypes.py`), sous le motif du Python : une liquidation avant l'origine de
 * la répartition, un régime de son affiliation qui n'existait pas encore.
 */
function verifierLaCase(simulateur, carriere, affiliation) {
  if (carriere.anneeLiquidation <= simulateur.parametres.annee_debut_repartition) {
    throw new Error("liquidation antérieure à la répartition");
  }
  if (!carriere.lignes.some((ligne) => simulateur.affiliations.regimes(affiliation,
    ligne.annee).length > 0)) {
    throw new Error("aucun régime actif sur la période");
  }
}

/**
 * Chaque case de la grille du coût, `{cle, regle, options, entree, rendre}`,
 * datée par le pilote du portage (`ageDeDepart`) et bâtie comme le Python la
 * bâtissait (`carriere_de_la_grille` de `castypes.py`) : l'âge de son départ
 * et, selon `rendre`, l'année et le mois de ce départ (`depart`) — ce que le
 * coût lit d'une cohorte voisine — ou la carrière, en données, et les deux que
 * l'âge légal de la proposition en dérive (`Carriere.prolongee`), poursuivie
 * jusqu'à lui ou attendue sans activité, `null` quand il ne la reporte pas
 * (`carriere`). Le coût choisit lesquelles simuler (`_propositions` de
 * `cout.py`).
 */
function carrieresDeLaGrille({ parametres, variante, primes, cas }) {
  const simulateur = simulateurSous(parametres);
  const ageLegal = simulateur.parametres.age_legal_liberal ?? null;
  return parCas(cas, (un) => {
    const { options, entree, rendre } = un;
    const { age, attendu, batir } = ageDuCas(simulateur, un, primes, variante);
    const carriere = carriereFinale(simulateur, entree ?? null, batir, primes)(age);
    verifierLaCase(simulateur, carriere, options.affiliation);
    // L'âge que l'attente d'un cas type de la grille élargie fixe (étape 7).
    const marque = attendu ? { attendu } : {};
    if (rendre === "depart") {
      return { age, annee: carriere.anneeLiquidation, mois: carriere.moisLiquidation, ...marque };
    }
    if (rendre !== "carriere") {
      throw new RangeError(`lecture d'une case inconnue : ${rendre}`);
    }
    const reportee = ageLegal === null ? carriere : carriere.prolongee(ageLegal, simulateur.macro);
    const reporte = reportee !== carriere;
    return {
      age,
      carriere: carriereEnDonnees(carriere),
      reportee: reporte ? carriereEnDonnees(reportee) : null,
      attente: reporte
        ? carriereEnDonnees(carriere.prolongee(ageLegal, simulateur.macro, false)) : null,
      ...marque,
    };
  });
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

/**
 * Le résultat du scénario 1 — celui d'une comparaison, ou celui que rend
 * `ScenarioActuel.calculer` — tel que les confrontations le lisent : la
 * pension, et à part ce qui est hors de la répartition ; chaque pension de
 * régime, son montant, son type de calcul et son détail ; chaque avantage
 * appliqué, son montant, son détail et la part de chaque régime ; la durée
 * validée et la durée requise, le taux ; l'ouverture et son motif ; chaque
 * départ que l'échéancier inscrit, sa date d'effet et son motif.
 */
function actuelEnDonnees(actuel) {
  return {
    pension_annuelle: actuel.pension_annuelle,
    pension_hors_repartition: actuel.pension_hors_repartition,
    pensions_par_regime: actuel.pensions_par_regime
      .map(({ regime, montant, type_calcul, detail }) => ({ regime, montant, type_calcul, detail })),
    avantages_appliques: actuel.avantages_appliques.map(({ code, montant, detail, par_regime }) => ({
      code, montant, detail,
      par_regime: (par_regime ?? []).map(([regime, part]) => [regime, part]),
    })),
    trimestres_valides: actuel.trimestres_valides,
    trimestres_requis: actuel.trimestres_requis,
    taux_liquidation: actuel.taux_liquidation,
    liquidation_ouverte: actuel.liquidation_ouverte,
    motif_ouverture: actuel.motif_ouverture,
    departs: actuel.departs.map(({ date_effet, motif }) => ({ date_effet, motif })),
  };
}

/**
 * Ce que les confrontations aux références extérieures lisent du scénario 1
 * d'une comparaison — l'estimation officielle (`scripts/estimation_officielle.py`),
 * Destinie 2 (`tests/test_destinie.py`) —, et que `dictionnaire()` n'écrit pas
 * entier : la date du départ et le passage aux euros constants ; la pension,
 * et à part ce qui est hors de la répartition ; chaque pension de régime, son
 * montant et son détail ; chaque avantage appliqué, son montant et la part de
 * chaque régime ; la durée validée et le taux ; l'ouverture et son motif ; la
 * réversion, son année, et ce que chaque régime en sert, de quelle date.
 */
function scenarioActuelEnDonnees(comparaison) {
  const { actuel, reversion } = comparaison;
  const date = comparaison.carriere.dateLiquidation;
  return {
    annee_liquidation: date.annee,
    mois_liquidation: date.mois,
    coefficient_euros_constants: comparaison.coefficient_euros_constants,
    actuel: actuelEnDonnees(actuel),
    reversion: reversion === null ? null : {
      annee: reversion.annee,
      regimes: reversion.regimes
        .map(({ regime, montant, date_effet }) => ({ regime, montant, date_effet })),
    },
  };
}

/**
 * Chaque requête du simulateur, lue par la saisie du portage et simulée comme
 * le site la simule (`Contexte.simuler`) — tel quel un relevé que l'appelant a
 * prolongé, avec `prolonger: false` : ce que les confrontations lisent de son
 * scénario 1 (`scenarioActuelEnDonnees`).
 */
function scenarioActuel({ cas }) {
  return parCas(cas, ({ requete, prolonger = true }) => {
    const saisie = Saisie.depuisRequete(requete, false, contexte.paquet.presomptions);
    if (saisie.releveActif && !prolonger) {
      const [simulateur, carriere] = releveTelQuel(saisie);
      return scenarioActuelEnDonnees(simulateur.simuler(carriere));
    }
    return scenarioActuelEnDonnees(contexte.simuler(saisie));
  });
}

/**
 * Les options d'une carrière que le Python a écrites (`carriere_simple`), sous
 * les types du portage : une table par année — les interruptions, le temps
 * partiel, les dispenses — en `Map`, ses années en nombres, comme
 * `carrieres` les lit.
 */
function optionsDeCarriere(options) {
  const parAnnee = (table) => (table === null || table === undefined ? table
    : new Map(Object.entries(table).map(([annee, valeur]) => [Number(annee), valeur])));
  return {
    ...options,
    interruptions: parAnnee(options.interruptions),
    temps_partiel: parAnnee(options.temps_partiel),
    dispenses: parAnnee(options.dispenses),
  };
}

/**
 * Les fonctions du droit que le pont fait appeler (`droit`), sous le nom de
 * leur jumeau Python (`module.fonction`) : les exemples d'OpenFisca et des
 * caisses (`tests/test_oracle.py`) éprouvent le droit fonction par fonction.
 * Une fonction de plus s'y déclare, et ce qu'elle rend dans
 * `LECTURES_DU_DROIT` de `pont.py`, sous le type de son jumeau.
 */
const FONCTIONS_DU_DROIT = {
  "invalidite.exigences_du_handicap": invalidite.exigencesDuHandicap,
  // La version, une fiche du paquet, reste dans le portage : aucune pension
  // sans elle.
  "invalidite.retraite_pour_invalidite.pension_du_fonctionnaire_invalide":
    (moteur, regime, carriere, pension, traitement, annee) => {
      const version = invalidite.retraitePourInvalidite(moteur, regime, carriere);
      return version === null ? null : invalidite.pensionDuFonctionnaireInvalide(
        moteur, carriere, version, pension, traitement, annee);
    },
  // Le cumul de l'activité après le départ, ses champs sous les noms du
  // Python (`cumul_des_donnees` de `pont.py`) : sous les pensions prêtées,
  // `{regime: montant}`, chaque année, sans majoration pour enfants, sur le
  // scénario 1 de la carrière liquidée, que le portage refait ; ou tel que
  // l'échéancier le calcule.
  "cumul.cumuler.pensions_pretees": (moteur, carriere, liquidee, pretees, anneeCourante) => cumul
    .cumuler(moteur, carriere, moteur.calculer(liquidee), () => [{ ...pretees }, 0.0],
      anneeCourante),
  "echeancier.parcourir.au_depart.cumul":
    (simulateur, carriere) => parcourue(simulateur, carriere).auDepart.cumul,
  // Ce que lisent les exemples de quatre étapes : le minimum vieillesse du
  // foyer ; les majorations exceptionnelles que « faire vivre » sert, sur le
  // scénario 1 que le portage refait, sans leur montant à l'échéance, que le
  // Python dérive ; les lignes de retraite de la fiche de paie d'un revenu,
  // `[code, part du salarié]` ; la cotisation de l'année de chaque régime,
  // sous les paramètres de la demande.
  "foyer.foyer_et_net.minimum_vieillesse": (...valeurs) => foyerEtNet(...valeurs)
    .minimumVieillesse,
  "revalorisation.faire_vivre.majorations": (simulateur, carriere, annee) => faireVivre(
    simulateur, carriere, simulateur.scenarioActuel.calculer(carriere), annee).majorations
    .map(({ a_l_echeance: _derive, ...majoration }) => majoration),
  "remuneration.fiche_depuis_brut.lignes_de_retraite": (simulateur, statut, annee, brut) => {
    const fiche = ficheDepuisBrut(simulateur.baremePrelevements, simulateur.macro,
      simulateur.catalogue, simulateur.affiliations, statut, annee, brut);
    return fiche === null ? null
      : fiche.lignes.filter((ligne) => ligne.retraite).map(({ code, salarie }) => [code, salarie]);
  },
  "compte.cotisation_annuelle.par_regime": (simulateur, carriere, annee) => new ConstructeurCompte(
    simulateur.macro, simulateur.catalogue, simulateur.affiliations, simulateur.indexation,
    simulateur.parametres).cotisationAnnuelle(carriere, annee).par_regime,
  "calendrier.en_mois": enMois,
  "calendrier.origine_des_ages":
    ({ annee, mois }, jour) => origineDesAges(new DateMois(annee, mois), jour),
  "carriere.date_de_l_age": (carriere, age) => carriere.dateDeLAge(age),
  "departs.age_legal": departs.ageLegal,
  "chronologie.valeur": (presomption) => valeurPresumee(presomption, contexte.paquet.presomptions),
  "ouvrir.age_ouverture_droit": ouvrir.ageOuvertureDroit,
  "ouvrir.duree_requise": ouvrir.dureeRequise,
  "periode.capital_seuil_points": (periode) => periode.capital_seuil_points ?? null,
  "liquider.duree_proratisation": liquider.dureeProratisation,
  // Le RAFP lit le rang de sa date d'effet : une vraie `DateMois`.
  "liquider.majoration_rafp":
    (age, { annee, mois }) => liquider.majorationRafp(age, new DateMois(annee, mois)),
  "liquider.mois_apres_le_depart": liquider.moisApresLeDepart,
  "liquider.nombre_d_annees_retenues": liquider.nombreDAnneesRetenues,
  "liquider.prestation_rafp": (rente, points, seuil, age, { annee, mois }, ecart) => liquider
    .prestationRafp(rente, points, seuil, age, new DateMois(annee, mois), ecart),
  "liquider.decote_opposable": liquider.decoteOpposable,
  "liquider.salaire_de_reference": liquider.salaireDeReference,
  "liquider.trimestres_de_decote": liquider.trimestresDeDecote,
  "liquider.valeur_du_point": liquider.valeurDuPoint,
  "regimes.BORNES_ASSIETTE": () => BORNES_ASSIETTE,
  // Le relevé des droits, par ce que les exemples en lisent : les points de
  // chaque régime, `[code, annee, points, taux]` ; la fiche et les services de
  // chaque emploi classé ; les services liquidables de régimes nommés.
  "releve.construire.droits.points":
    (moteur, carriere) => releve.construire(moteur, carriere).droits.points,
  "releve.construire.durees.emplois": (moteur, carriere) => releve.construire(moteur, carriere)
    .durees.emplois.map(({ fiche, services }) => [fiche, services]),
  "releve.construire.durees.services_liquidables": (moteur, carriere, membres) => releve
    .construire(moteur, carriere).durees.servicesLiquidables(membres),
  // La réversion, ses champs sous les noms du Python (`reversion_des_donnees`
  // de `pont.py`) ; les régimes servis en capital, un ensemble.
  "reversion.reversion": (moteur, pensions, carriere, annee, decesSuppose = null,
    enCapital = [], ...autres) => reversion.reversion(
    moteur, pensions, carriere, annee, decesSuppose, new Set(enCapital), ...autres),
  // Ce que l'échéancier liquide de la carrière : la réversion au décès de
  // l'assuré, et le plafond de chaque nouvelle pension de l'activité après le
  // départ, `[regime, plafond]`.
  "echeancier.parcourir.reversion": (simulateur, carriere) => parcourue(simulateur, carriere)
    .reversion,
  "echeancier.parcourir.au_depart.droits_apres_depart.pensions": (simulateur, carriere) => {
    const droits = parcourue(simulateur, carriere).auDepart.droits_apres_depart;
    return droits === null ? null
      : droits.pensions.map(({ regime, plafond }) => [regime, plafond ?? null]);
  },
  "scenario_actuel.ages_annulation_decote.age":
    (moteur, generation) => moteur.agesAnnulationDecote.age(generation),
  "scenario_actuel.ages_ouverture.age": (moteur, generation) => moteur.agesOuverture.age(generation),
  // Les drapeaux de `calculer` suivent la carrière dans l'ordre du jumeau :
  // `ignorer_penalite_age`, `avantages_non_contributifs`, `avpf`,
  // `liquider_successions`…
  "scenario_actuel.calculer": (moteur, carriere, ...drapeaux) => actuelEnDonnees(
    moteur.calculer(carriere, ...drapeaux)),
  // L'étage d'un régime : la base, le régime intégré, la complémentaire…
  "scenario_actuel.catalogue.etage": (moteur, code) => moteur.catalogue.obtenir(code).etage,
  // Ce que les confrontations lisent des périodes d'un régime pour rejouer
  // ses cotisations (`periodes_des_donnees` de `pont.py`).
  "scenario_actuel.catalogue.periodes": (moteur, code) => moteur.catalogue.obtenir(code).periodes
    .map(({ debut, fin, assiette, taux_cotisation_retraite, part_salariale }) => ({
      debut, fin, assiette, taux_cotisation_retraite, part_salariale,
    })),
  "scenario_actuel.macro.plafond_securite_sociale":
    (moteur, annee) => moteur.macro.plafond_securite_sociale.valeur(annee),
  "scenario_actuel.minimum_garanti.montant":
    (moteur, ...valeurs) => moteur.minimumGaranti.montant(...valeurs),
  "scenario_actuel.valeurs_point.achat":
    (moteur, ...valeurs) => moteur.valeursPoint.achat(...valeurs),
  "scenario_actuel.valeurs_point.service":
    (moteur, ...valeurs) => moteur.valeursPoint.service(...valeurs),
  // Ses lignes de relevé, `LigneRelevee` du Python, passent par leurs champs.
  "simulateur.carriere_releve":
    (simulateur, options) => carriereEnDonnees(simulateur.carriereReleve(options)),
  "simulateur.carriere_simple":
    (simulateur, options) => carriereEnDonnees(simulateur.carriereSimple(optionsDeCarriere(options))),
};

/** L'échéancier du simulateur, la carrière parcourue. */
function parcourue(simulateur, carriere) {
  const echeancier = new Echeancier(simulateur);
  echeancier.parcourir(carriere);
  return echeancier;
}

/** Un nom du Python en casse de chameau : celui de son jumeau. */
function enChameau(nom) {
  return nom.replace(/_([a-z0-9])/g, (_, lettre) => lettre.toUpperCase());
}

/**
 * Le moteur du scénario 1, chaque table prêtée par une autre (`Moteur.pretant`
 * de `pont.py`, sous les noms du Python), sur une copie : le moteur du
 * simulateur, que les autres appels lisent, n'en garde rien. Une table que le
 * moteur ne porte pas arrête l'appel, au lieu qu'un prêt se perde.
 */
function moteurPretant(moteur, prets) {
  if (prets.length === 0) {
    return moteur;
  }
  const copie = Object.create(moteur);
  for (const [table, preteuse] of prets.map((pret) => pret.map(enChameau))) {
    if (!(table in moteur) || !(preteuse in moteur)) {
      throw new Error(`tables que le moteur ne porte pas : ${table}, ${preteuse}`);
    }
    copie[table] = moteur[preteuse];
  }
  return copie;
}

/**
 * Les fiches que retire chacune des neutralisations des bonifications de
 * service : celles des emplois classés, puis celle des militaires. Voir
 * `FICHES_RETIREES` d'`avantages.py`.
 */
const FICHES_RETIREES = {
  bonification_cinquieme_services_actifs: FICHES_DES_EMPLOIS
    .filter((nom) => nom !== FICHE_DES_MILITAIRES),
  bonification_cinquieme_militaires: [FICHE_DES_MILITAIRES],
};

/** Les scénarios neutralisés de chaque simulateur, bâtis une fois. */
const NEUTRALISES = new WeakMap();

/**
 * Un scénario 1 par avantage retiré, que la mesure des avantages non
 * contributifs liquide (`scenarios_neutralises` d'`avantages.py`, son jumeau,
 * action 161, étape 6) : celui du simulateur, bâti sur un catalogue privé de
 * la déclaration du classement de l'emploi, que la jouissance militaire
 * partage ; la règle du salaire de référence des parents repoussée hors de
 * portée ; un barème de carrière longue lu sur un paquet qui n'en porte pas,
 * vide comme le Python le lit d'un fichier absent ; la fiche du départ
 * anticipé des assurés handicapés retirée ; celles des bonifications des
 * emplois classés, puis celle des militaires ; celle de l'apprentissage.
 */
function scenariosNeutralises(simulateur) {
  if (NEUTRALISES.has(simulateur)) {
    return NEUTRALISES.get(simulateur);
  }
  const { paquet, macro, catalogue, affiliations, parametres } = simulateur;
  const scenario = (sur = catalogue) => new ScenarioActuel(
    paquet, macro, sur, affiliations, parametres);
  const sansClassement = catalogue.sansDeclaration("categorie_active");
  const variantes = {
    categorie_active: scenario(sansClassement),
    age_jouissance_militaire: scenario(sansClassement),
  };
  const parents = scenario();
  parents.parentsMeilleuresAnneesDepuis = new DateMois(2999, 1).rang;
  variantes.salaire_de_reference_des_parents = parents;
  const longue = scenario();
  longue.carriereLongue = new CarriereLongue({});
  variantes.carriere_longue = longue;
  const handicap = scenario();
  handicap.invalidites = handicap.invalidites.sans("handicap");
  variantes.retraite_anticipee_handicap = handicap;
  for (const [code, noms] of Object.entries(FICHES_RETIREES)) {
    const emplois = scenario();
    emplois.fichesDatees = emplois.fichesDatees.sans(...noms);
    variantes[code] = emplois;
  }
  const apprentissage = scenario();
  apprentissage.fichesDatees = apprentissage.fichesDatees.sans(FICHE_DE_L_APPRENTISSAGE);
  variantes.apprentissage = apprentissage;
  NEUTRALISES.set(simulateur, variantes);
  return variantes;
}

/** Le scénario 1 du simulateur, ou celui que la mesure des avantages neutralise. */
function moteurNeutralise(simulateur, code) {
  if (code === undefined) {
    return simulateur.scenarioActuel;
  }
  const variantes = scenariosNeutralises(simulateur);
  if (!Object.hasOwn(variantes, code)) {
    throw new RangeError(`avantage que la mesure ne neutralise pas : ${code}`);
  }
  return variantes[code];
}

/**
 * Les statuts que bonifie une version des fiches que la neutralisation `code`
 * retire (`FICHES_RETIREES`) : les seules carrières que le retrait peut
 * toucher. Voir `statuts_des_emplois` d'`avantages.py`.
 */
function statutsDesEmplois(moteur, code) {
  const fiches = moteur.fichesDatees.fiches();
  return new Set(FICHES_RETIREES[code].filter((nom) => Object.hasOwn(fiches, nom))
    .flatMap((nom) => fiches[nom].versions.flatMap((version) => version.parametres.statuts ?? [])));
}

/**
 * La carrière que bâtissent ces options n'a-t-elle rien à perdre au retrait de
 * l'avantage `code` ? Qu'aucune fiche retirée ne bonifie son statut, qu'elle ne
 * déclare aucune incapacité, aucun contrat d'apprentissage : les gardes de
 * `recalculer` d'`avantages.py`, que le Python ne peut tenir sans le moteur ni
 * la carrière bâtie. Rien à perdre, la carrière n'est pas liquidée ; sinon, la
 * voici, bâtie comme le Python la rebâtit pour chaque retrait.
 */
function carriereQuiPerd(simulateur, options, code) {
  if (Object.hasOwn(FICHES_RETIREES, code)
    && !statutsDesEmplois(simulateur.scenarioActuel, code).has(options.affiliation)) {
    return null;
  }
  const carriere = simulateur.carriereSimple(optionsDeCarriere(options));
  if (code === "retraite_anticipee_handicap" && carriere.incapacitePermanente === null) {
    return null;
  }
  if (code === "apprentissage" && !(carriere.chronologie && contrats(carriere).length > 0)) {
    return null;
  }
  return carriere;
}

/**
 * Chaque case du coût des avantages non contributifs, `{cle, options,
 * carriere, scenario}` (`avantages.decomposer`, dont le Python garde le
 * jumeau) : la carrière d'un seul statut de ses options
 * (`carriere_variante`), écartée sous le motif du Python quand le droit
 * l'écarte (`verifierLaCase`), liquidée au scénario 1 — ce que la
 * décomposition en lit — ; puis la pension et la durée requise de chaque
 * contrefactuelle que le Python demande, `[pension, durée]` sous son code : la
 * carrière rebâtie, ses périodes non travaillées changées (`carriere`, sous
 * chaque code, ses interruptions), ou liquidée sous un scénario neutralisé
 * (`scenario`, des codes ; `scenariosNeutralises`), sauf celle qui n'a rien à
 * perdre (`carriereQuiPerd`). Seules la carrière et sa liquidation au scénario
 * 1 écartent une case : une contrefactuelle qui faillit arrête la demande,
 * comme elle arrête le Python.
 */
function avantages({ parametres, cas }) {
  const simulateur = simulateurSous(parametres);
  const moteur = simulateur.scenarioActuel;
  const resultats = {};
  const echecs = {};
  for (const { cle, options, carriere: deCarriere, scenario: deScenario } of cas) {
    let carriere;
    let actuel;
    try {
      carriere = simulateur.carriereSimple(optionsDeCarriere(options));
      verifierLaCase(simulateur, carriere, options.affiliation);
      actuel = moteur.calculer(carriere);
    } catch (erreur) {
      if (erreurDuProgramme(erreur)) {
        throw erreur;
      }
      echecs[cle] = String(erreur.message ?? erreur);
      continue;
    }
    const sans = {};
    for (const [code, interruptions] of Object.entries(deCarriere)) {
      const variante = moteur.calculer(simulateur.carriereSimple(
        optionsDeCarriere({ ...options, interruptions })));
      sans[code] = [variante.pension_annuelle, variante.trimestres_requis];
    }
    for (const code of deScenario) {
      const perd = carriereQuiPerd(simulateur, options, code);
      if (perd !== null) {
        const variante = moteurNeutralise(simulateur, code).calculer(perd);
        sans[code] = [variante.pension_annuelle, variante.trimestres_requis];
      }
    }
    resultats[cle] = {
      annee_liquidation: carriere.anneeLiquidation,
      age_liquidation: carriere.age_liquidation,
      pension_annuelle: actuel.pension_annuelle,
      total_contributif: actuel.total_contributif,
      trimestres_requis: actuel.trimestres_requis,
      motif_ouverture: actuel.motif_ouverture,
      avantages_appliques: actuel.avantages_appliques.map(({ code, montant }) => [code, montant]),
      sans,
    };
  }
  return { resultats, echecs };
}

/**
 * Un argument d'un appel du droit, tel que `pont.py` l'écrit : le simulateur,
 * la carrière qu'il bâtit d'options (`CarriereSimple`), sans qu'elle passe,
 * le moteur du scénario 1 (`simulateur.scenarioActuel`), ou sa variante que la
 * mesure des avantages neutralise (`neutralise`, `scenariosNeutralises`), et
 * les tables qu'on lui prête, la période d'un régime à une année, une carrière
 * de la demande, par son rang, ou une valeur.
 */
function argumentDuDroit(simulateur, carrieres, argument) {
  if (Object.hasOwn(argument, "simulateur")) {
    return simulateur;
  }
  if (Object.hasOwn(argument, "carriere_simple")) {
    return simulateur.carriereSimple(optionsDeCarriere(argument.carriere_simple));
  }
  if (Object.hasOwn(argument, "moteur")) {
    return moteurPretant(moteurNeutralise(simulateur, argument.neutralise),
      argument.prets ?? []);
  }
  if (Object.hasOwn(argument, "periode")) {
    const [code, annee] = argument.periode;
    return simulateur.catalogue.obtenir(code).periode(annee);
  }
  if (Object.hasOwn(argument, "carriere")) {
    return carrieres[argument.carriere];
  }
  return argument.valeur;
}

/**
 * Chaque appel d'une fonction du droit, `{cle, fonction, arguments}`, sous les
 * paramètres que `pont.py` a passés en données, sur les carrières de la
 * demande, que le Python a bâties : ce que la fonction rend. Une fonction que
 * le pont ne porte pas arrête la demande, au lieu de se perdre.
 */
function droit({ parametres, carrieres, appels }) {
  const inconnues = [...new Set(appels.map(({ fonction }) => fonction))]
    .filter((nom) => !Object.hasOwn(FONCTIONS_DU_DROIT, nom));
  if (inconnues.length > 0) {
    throw new Error(`fonctions du droit que le pont ne fait pas appeler : ${inconnues.join(", ")}`);
  }
  const simulateur = simulateurSous(parametres);
  const lues = carrieres.map(carriereDesDonnees);
  return parCas(appels, ({ fonction, arguments: valeurs }) => FONCTIONS_DU_DROIT[fonction](
    ...valeurs.map((argument) => argumentDuDroit(simulateur, lues, argument))));
}

const LECTURES = {
  carrieres, saisies, grille_du_cout: grilleDuCout, carrieres_des_saisies: carrieresDesSaisies,
  simulations, scenario_actuel: scenarioActuel, droit, ages_de_depart: agesDeDepart,
  carrieres_de_la_grille: carrieresDeLaGrille, avantages, departs_des_cas: departsDesCas,
  debuts_de_la_surcote: debutsDeLaSurcote,
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
  contexte = new Contexte(sousLaGarde(paquetDuDepot()));
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
  contexte = new Contexte(sousLaGarde(paquet ?? paquetDuDepot()));
  process.stdout.write(JSON.stringify(repondre(demande)));
}
