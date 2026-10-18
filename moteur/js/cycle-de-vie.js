/**
 * Les indicateurs de cycle de vie : ce qu'une carrière verse, ce qu'elle
 * reçoit — portage de `cycle_de_vie.py`, qui fait foi et dit le détail
 * (action 138, étape 9 ; registre des modèles, chantier « 138.9 »).
 *
 * La durée de retraite et sa part de la vie, le taux de récupération, le taux
 * d'annuité et le remplacement sur le cycle de vie, le rendement interne réel
 * et relatif au salaire moyen, le patrimoine retraite de l'OCDE, la valeur
 * actuelle nette et le remplacement au décès de PROST ; l'âge d'équilibre du
 * diviseur et l'âge de part de vie constante.
 *
 * CE QUI EST PORTÉ, ET CE QUI NE L'EST PAS ENCORE. Les deux flux de chaque
 * système — ce que la paie supporte pour la retraite, contributions
 * d'équilibre de l'Agirc-Arrco comprises (`contributions-equilibre.js`), et ce
 * qui est servi, année après année —, et, depuis le 14 octobre, les revenus
 * nets de chaque année, que l'histoire des prélèvements donne
 * (`prelevements-historiques.js`) : donc la convention de l'OCDE, la
 * convention nette et celle du COR, la pension nette chaque année au taux de
 * son année ; depuis le 16 octobre, l'impôt sur le revenu de chaque année
 * (`impot-revenu.js`, étape 5), donc la convention après impôt et le taux de
 * remplacement après impôt au départ ; depuis le 16 octobre aussi, les âges
 * de départ d'une carrière (`agesBalayes`, `depart`, `balayageDUneCarriere`),
 * qu'une fonction bâtit à chaque âge ; depuis le 18 octobre, la pension du
 * départ par étage et le revenu autour du départ (`pensionParEtage`,
 * `revenusAutourDuDepart`), les tableaux 1 et 2 de Typfallsmodellen. Les cas types du COR, que le Python
 * bâtit, passent par lui depuis le pont (action 161, étape 5) :
 * `scripts/cycle_de_vie.mjs` en calcule les indicateurs, les âges de départ
 * et les âges d'équilibre pour `scripts/cycle_de_vie.py`.
 * `node tests/js/comparer-cycle-de-vie.mjs` rejoue le tout contre le Python
 * (`tests/test_cycle_de_vie_portage.py`).
 */

import { contributionsDUneCarriere, partSalarialeAnnualisee } from "./contributions-equilibre.js";
import { AGE_TERMINAL } from "./mortalite.js";
import {
  chargerPrelevementsHistoriques, familleDeLaFiche, FAMILLES_INDEPENDANTES,
} from "./prelevements-historiques.js";
import {
  ficheDepuisBrut, indemnitesDesLignes, profilDeLaFiche, remunerationDeLaCarriere,
} from "./remuneration.js";
import {
  chargerBaremesImpotRevenu, croissanceMacro, Declarant, Foyer, impotAuxParametres, INDEXATIONS,
} from "./impot-revenu.js";
import { agesDeLEstimation } from "./pilote.js";
import { faireVivre, RevalorisationServie } from "./revalorisation.js";
import { exp, log, pow } from "./libm.js";

/** Les six systèmes, dans l'ordre de la comparaison. */
export const SCENARIOS = Object.freeze([
  "actuel",
  "notionnel_retroactif",
  "notionnel_prospectif",
  "notionnel_retroactif_employeur",
  "notionnel_prospectif_employeur",
  "notionnel_liberal",
]);

/** Le taux réel auquel l'OCDE actualise le patrimoine retraite. */
export const TAUX_ACTUALISATION_OCDE = 0.015;

/** Les bornes de la recherche d'un rendement interne. */
export const BORNES_RENDEMENT = Object.freeze([-0.5, 1.0]);

/**
 * Comment une retraite finit, et comment on la compte ; le défaut est la
 * convention de l'OCDE. Voir `Convention` dans le Python.
 */
export class Convention {
  constructor({
    age_deces = null, unisexe = false, taux_actualisation = TAUX_ACTUALISATION_OCDE,
    prelevement = 0.0, prelevements = null, impot = null,
  } = {}) {
    this.age_deces = age_deces;
    this.unisexe = unisexe;
    this.taux_actualisation = taux_actualisation;
    this.prelevement = prelevement;
    this.prelevements = prelevements;
    this.impot = impot;
    if (impot !== null) {
      if (!INDEXATIONS.includes(impot)) {
        throw new Error(`indexation du barème inconnue : '${impot}' (${INDEXATIONS.join(", ")})`);
      }
      if (!this.nette) {
        throw new Error("l'impôt se calcule sur le net imposable : une convention après "
          + "impôt porte les prélèvements");
      }
    }
    Object.freeze(this);
  }

  /** La même convention, après l'impôt d'`impot` (`replace(…, impot=…)`). */
  avecLImpot(impot) {
    return new Convention({
      age_deces: this.age_deces, unisexe: this.unisexe,
      taux_actualisation: this.taux_actualisation, prelevement: this.prelevement,
      prelevements: this.prelevements, impot,
    });
  }

  /** La pension est-elle nette des prélèvements ? */
  get nette() {
    return this.prelevement > 0.0
      || (this.prelevements !== null && this.prelevements.size > 0);
  }

  /** La part de la pension de l'année `annee` que les prélèvements laissent. */
  retenu(annee) {
    if (this.prelevements !== null && this.prelevements.has(annee)) {
      return 1.0 - this.prelevements.get(annee);
    }
    return 1.0 - this.prelevement;
  }
}

/**
 * L'impôt sur le revenu d'une année du cycle de vie, et ce qu'en supportent
 * le salaire et la pension (`impotsParAnnee`).
 */
export class ImpotDeLAnnee {
  constructor({ annee, salaire, pension, foyer, sur_la_pension, benefice = 0.0 }) {
    Object.assign(this, { annee, salaire, pension, foyer, sur_la_pension, benefice });
    Object.freeze(this);
  }

  /** Ce que le foyer paie ; négatif, ce qui lui est restitué. */
  get impot() {
    return this.foyer.impot;
  }

  get sur_le_salaire() {
    return this.foyer.impot - this.sur_la_pension;
  }
}

/** Ce qu'une carrière verse et reçoit sous un système, en euros courants. */
export class Flux {
  constructor({
    scenario, cotisations, revenus, niveaux, debut, age, sexe, dernier_revenu,
    revenus_nets = null, dernier_revenu_net = null, indexation_impot = null, impots = null,
    exoneree = new Map(), revenus_apres_impot = null, dernier_revenu_apres_impot = null,
  }) {
    Object.assign(this, {
      scenario, cotisations, revenus, niveaux, debut, age, sexe, dernier_revenu,
      revenus_nets, dernier_revenu_net, indexation_impot, impots, exoneree,
      revenus_apres_impot, dernier_revenu_apres_impot,
    });
  }

  /** Le même flux, ses champs de `champs` remplacés (`dataclasses.replace`). */
  remplace(champs) {
    return new Flux({ ...this, ...champs });
  }

  get naissance() {
    return this.debut - this.age;
  }

  /** La part de l'année `annee` où la pension est servie. */
  servi(annee) {
    return Math.min(Math.max(annee + 1 - this.debut, 0.0), 1.0);
  }

  /**
   * La part de la pension brute de l'année `annee` que l'impôt lui retire :
   * ce qu'elle en supporte sur ce qu'elle sert dans l'année ; zéro sans impôt.
   */
  impotDeLaPension(annee) {
    const impot = this.impots === null ? undefined : this.impots.get(annee);
    const servie = (this.niveaux.get(annee) ?? 0.0) * this.servi(annee);
    if (impot === undefined || servie <= 0.0) return 0.0;
    return impot.sur_la_pension / servie;
  }

  get annee_liquidation() {
    return Math.floor(this.debut + 1e-9);
  }

  /** Les années qui portent un revenu d'activité. */
  get duree_carriere() {
    let n = 0;
    for (const revenu of this.revenus.values()) if (revenu > 0) n += 1;
    return n;
  }
}

/** Les indicateurs de cycle de vie d'une carrière, sous un système. */
export class Indicateurs {
  constructor(champs) {
    Object.assign(this, champs);
  }

  get duree_relative() {
    return this.duree_carriere <= 0 ? null : this.duree_retraite / this.duree_carriere;
  }

  dictionnaire() {
    return {
      duree_retraite: this.duree_retraite,
      part_de_vie: this.part_de_vie,
      duree_carriere: this.duree_carriere,
      duree_relative: this.duree_relative,
      taux_recuperation: this.taux_recuperation,
      taux_annuite: this.taux_annuite,
      taux_remplacement_cycle: this.taux_remplacement_cycle,
      rendement_reel: this.rendement_reel,
      rendement_smpt: this.rendement_smpt,
      patrimoine: this.patrimoine,
      valeur_nette: this.valeur_nette,
      remplacement_au_deces: this.remplacement_au_deces,
    };
  }
}

// -- les flux ----------------------------------------------------------------

/** Des montants datés, sommés par année, dans l'ordre où ils viennent. */
function parAnnee(couples) {
  const sommes = new Map();
  for (const [annee, montant] of couples) {
    if (montant) sommes.set(annee, (sommes.get(annee) ?? 0.0) + montant);
  }
  return sommes;
}

function trieesParAnnee(map) {
  return [...map.entries()].sort(([a], [b]) => a - b);
}

/**
 * Ce que le droit en vigueur prélève sur `carriere` pour sa retraite, année
 * par année et sans bascule : le compte des scénarios 4 et 5, sans régime
 * fusionné, et les contributions d'équilibre de l'Agirc-Arrco.
 */
export function cotisationsVersees(simulateur, carriere) {
  const compte = simulateur.constructeurEmployeur.construire(
    carriere, carriere.anneeLiquidation, carriere.premiereAnnee);
  return parAnnee([
    ...compte.cotisations.map((ligne) => [ligne.annee, ligne.cotisation]),
    ...trieesParAnnee(contributionsDUneCarriere(simulateur, carriere)),
  ]);
}

/**
 * Ce que versent les scénarios 2 à 5 : le compte du scénario 4, et les
 * contributions d'équilibre jusqu'à la bascule.
 */
export function cotisationsReformees(simulateur, comparaison) {
  const compte = comparaison.notionnel_retroactif_employeur.compte;
  const bascule = simulateur.parametres.annee_bascule;
  const equilibre = contributionsDUneCarriere(simulateur, comparaison.carriere);
  return parAnnee([
    ...compte.cotisations.map((ligne) => [ligne.annee, ligne.cotisation]),
    ...trieesParAnnee(equilibre).filter(([annee]) => annee < bascule),
  ]);
}

/**
 * Ce que le scénario 6 fait verser : le droit en vigueur avant la bascule,
 * son compte ensuite, et les deux parts de son pilier.
 */
export function cotisationsLiberales(simulateur, versees, liberal) {
  const bascule = simulateur.parametres.annee_bascule;
  const couples = [...versees.entries()].filter(([annee]) => annee < bascule);
  for (const ligne of liberal.compte.cotisations) {
    if (ligne.annee >= bascule) couples.push([ligne.annee, ligne.cotisation]);
  }
  const pilier = liberal.capitalisation;
  if (pilier !== null && pilier !== undefined && pilier.actif) {
    for (const annee of pilier.annees) couples.push([annee.annee, annee.versement_brut]);
  }
  return parAnnee(couples);
}

/** Les revenus d'activité des années cotisées, en euros courants. */
export function revenusDActivite(carriere) {
  return parAnnee(carriere.lignes.filter((ligne) => ligne.cotise)
    .map((ligne) => [ligne.annee, ligne.revenu]));
}

/** Les postes de la fiche que les contributions d'équilibre de l'année remplacent. */
export const POSTES_EQUILIBRE = Object.freeze(["equilibre_general", "equilibre_technique"]);

/** Les postes de la fiche d'un indépendant que l'histoire refait à l'année. */
export const POSTES_REFAITS_INDEPENDANT = Object.freeze([
  "maladie_maternite", "indemnites_journalieres", "famille", "csg_crds",
]);

function historiqueDe(simulateur) {
  const historique = chargerPrelevementsHistoriques(simulateur.paquet);
  if (historique === null) {
    throw new Error("le paquet ne porte pas l'histoire des prélèvements "
      + "(`prelevements_historiques`) : les revenus nets ne se calculent pas");
  }
  return historique;
}

/**
 * Le net du revenu annualisé d'une ligne cotisée, aux prélèvements de son
 * année, et, avec `imposable`, ce que ces prélèvements en retirent sans que
 * le revenu imposable le déduise ; `null` sans fiche de paie. Jumeau de
 * `_net_annualise`.
 */
function netAnnualise(simulateur, carriere, ligne, indemnite = 0.0, imposable = false) {
  const { macro, catalogue, affiliations } = simulateur;
  // Les régimes de la date d'entrée dans le statut : l'agent de la SNCF entré
  // avant 2020 paie le sien après la fermeture.
  const entree = carriere.dateEntree(ligne.affiliation);
  const fiche = ficheDepuisBrut(simulateur.baremePrelevements, macro, catalogue, affiliations,
    ligne.affiliation, ligne.annee, ligne.revenuAnnualise, ligne.part_primes, indemnite,
    entree);
  if (fiche === null) return null;
  const annualise = fiche.brut;
  const profil = profilDeLaFiche(affiliations, catalogue, ligne.affiliation, ligne.annee,
    entree);
  const regimes = profil === "independant"
    ? affiliations.regimes(ligne.affiliation, ligne.annee, entree)
    : [];
  const famille = familleDeLaFiche(profil, regimes);
  const historique = historiqueDe(simulateur);
  const plafond = macro.plafond_securite_sociale.valeur(ligne.annee);
  const courante = simulateur.baremePrelevements.annee;
  if (famille === null) {
    return [fiche.net, imposable
      ? historique.nonDeductiblesAnnuel(null, courante, annualise, plafond) : 0.0];
  }
  let retraite;
  if (FAMILLES_INDEPENDANTES.includes(famille)) {
    retraite = 0.0;
    for (const l of fiche.lignes) {
      if (!POSTES_REFAITS_INDEPENDANT.includes(l.code)) retraite += l.salarie;
    }
  } else {
    retraite = fiche.retraiteSalarie;
  }
  const horsRetraite = historique.horsRetraiteAnnuel(famille, courante, annualise, plafond, retraite)
    - historique.horsRetraiteAnnuel(famille, ligne.annee, annualise, plafond, retraite);
  let equilibre = 0.0;
  for (const l of fiche.lignes) if (POSTES_EQUILIBRE.includes(l.code)) equilibre += l.salarie;
  if (equilibre > 0.0) equilibre -= partSalarialeAnnualisee(simulateur, carriere, ligne);
  const nonDeductibles = imposable
    ? historique.nonDeductiblesAnnuel(famille, ligne.annee, annualise, plafond, retraite) : 0.0;
  return [fiche.net + horsRetraite + equilibre, nonDeductibles];
}

/**
 * Chaque ligne cotisée, dans l'ordre : son année, son net et, avec
 * `imposable`, sa part non déductible, ramenés aux mois travaillés ; `null`
 * quand un statut de la carrière n'a pas de fiche de paie.
 */
function paies(simulateur, carriere, imposable) {
  const resultat = [];
  const indemnites = indemnitesDesLignes(carriere, simulateur.macro, simulateur.catalogue,
    simulateur.affiliations);
  for (const [rang, ligne] of carriere.lignes.entries()) {
    if (!ligne.cotise) continue;
    const paie = netAnnualise(simulateur, carriere, ligne, indemnites[rang], imposable);
    if (paie === null) return null;
    const [net, nonDeductible] = paie;
    resultat.push([ligne.annee, net * ligne.fraction_annee, nonDeductible * ligne.fraction_annee]);
  }
  return resultat;
}

/** Les nets des années de la bascule au départ, lus sur la fiche de la proposition. */
function avecLaProposition(simulateur, carriere, nets) {
  const remuneration = remunerationDeLaCarriere(carriere, simulateur.macro,
    simulateur.catalogue, simulateur.affiliations, simulateur.parametres,
    simulateur.baremePrelevements, simulateur.paquet);
  const bruts = revenusDActivite(carriere);
  for (const annee of remuneration === null ? [] : remuneration.annees) {
    const fiche = annee.proposition;
    if (fiche.brut > 0.0 && bruts.has(annee.annee)) {
      // Le même brut que la fiche du droit en vigueur, indemnité comprise.
      const revenu = annee.droitEnVigueur.brut - annee.indemniteCsg;
      const paye = revenu > 0.0 ? annee.indemniteCsg * bruts.get(annee.annee) / revenu : 0.0;
      nets.set(annee.annee, (bruts.get(annee.annee) + paye) * fiche.net / fiche.brut);
    }
  }
  return nets;
}

/**
 * Ce que la paie laisse de chaque revenu d'activité, année par année, aux
 * prélèvements de son année ; avec `proposition`, les années de la bascule au
 * départ lues sur la fiche de la proposition. `null` quand un statut de la
 * carrière n'a pas de fiche de paie. Jumeau de `revenus_nets`.
 */
export function revenusNets(simulateur, carriere, proposition = false) {
  const lues = paies(simulateur, carriere, false);
  if (lues === null) return null;
  const nets = parAnnee(lues.map(([annee, net]) => [annee, net]));
  return proposition ? avecLaProposition(simulateur, carriere, nets) : nets;
}

/**
 * Les revenus d'activité nets imposables, année par année : le net, plus ce
 * que la paie retire sans que le revenu imposable le déduise. Jumeau de
 * `revenus_imposables`.
 */
export function revenusImposables(simulateur, carriere, proposition = false) {
  const revenus = netsEtImposables(simulateur, carriere, proposition);
  return revenus === null ? null : revenus[1];
}

/** `revenusNets` et `revenusImposables`, d'une seule fiche de paie par ligne. */
function netsEtImposables(simulateur, carriere, proposition) {
  const lues = paies(simulateur, carriere, true);
  if (lues === null) return null;
  let nets = parAnnee(lues.map(([annee, net]) => [annee, net]));
  if (proposition) nets = avecLaProposition(simulateur, carriere, nets);
  const retires = parAnnee(lues.map(([annee, , part]) => [annee, part]));
  return [nets,
    new Map([...nets].map(([annee, net]) => [annee, net + (retires.get(annee) ?? 0.0)]))];
}

/** Le dernier revenu annualisé, net : le rapport du net au brut de la dernière année cotisée. */
function dernierRevenuNet(dernierRevenu, revenus, nets) {
  if (nets === null || revenus.size === 0) return null;
  const annee = Math.max(...revenus.keys());
  return dernierRevenu * (nets.get(annee) ?? 0.0) / revenus.get(annee);
}

function debutDe(carriere) {
  return carriere.anneeLiquidation + carriere.fractionAnneeLiquidation;
}

/** La dernière année qu'une pension peut atteindre. */
function derniereAnneeDe(carriere) {
  return Math.floor(debutDe(carriere) - carriere.age_liquidation + AGE_TERMINAL) + 1;
}

function horsRepartition(simulateur, regime) {
  return Boolean(simulateur.parametres.isoler_capitalisation
    && simulateur.catalogue.obtenir(regime).hors_repartition);
}

/** La répartition d'une pension menée à une échéance, sans le RAFP. */
function servie(vivante) {
  let total = 0.0;
  for (const r of vivante.regimes) if (!r.hors_repartition) total += r.aujourd_hui;
  return total + vivante.majoration_enfants * vivante.coefficient_majoration;
}

/** La répartition du scénario 1 au départ, sans l'ASPA. */
function auDepart(simulateur, resultat) {
  let regimes = 0.0;
  for (const p of resultat.pensions_par_regime) {
    if (!horsRepartition(simulateur, p.regime)) regimes += p.montant;
  }
  let majoration = 0.0;
  for (const a of resultat.avantages_appliques) {
    if (a.code === "majoration_enfants") majoration += a.montant;
  }
  return regimes + majoration;
}

function partsConvenues(simulateur, resultat, revalorisation) {
  const total = auDepart(simulateur, resultat);
  const parts = new Map();
  if (total <= 0.0) return parts;
  for (const pension of resultat.pensions_par_regime) {
    const convenu = revalorisation.regimeConvenu(pension.regime);
    if (convenu !== null && pension.montant > 0.0) {
      parts.set(convenu, (parts.get(convenu) ?? 0.0) + pension.montant / total);
    }
  }
  return parts;
}

/** `cout.coefficient_actuel` : les prix, et la valeur de service convenue. */
function coefficientActuel(parts, revalorisation, anneeLiquidation, annee) {
  let coefficient = 1.0;
  if (annee <= anneeLiquidation) return coefficient;
  for (const [regime, part] of parts) {
    coefficient += part * (revalorisation.coefficientPoints(regime, anneeLiquidation, annee) - 1.0);
  }
  return coefficient;
}

/**
 * Le niveau annuel de la pension du scénario 1, de l'année du départ à
 * `derniere`, en euros courants : le droit jusqu'à l'année courante, puis
 * la convention de projection de la page Coût.
 */
export function niveauxActuels(simulateur, comparaison, revalorisation, derniere) {
  const carriere = comparaison.carriere;
  const resultat = comparaison.actuel;
  const macro = simulateur.macro;
  const liquidation = carriere.anneeLiquidation;
  const courante = simulateur.parametres.annee_courante;
  const niveaux = new Map();
  let ancre;
  if (liquidation <= courante) {
    for (let annee = liquidation; annee <= courante; annee += 1) {
      niveaux.set(annee, servie(faireVivre(simulateur, carriere, resultat, annee)));
    }
    ancre = courante;
  } else {
    niveaux.set(liquidation, auDepart(simulateur, resultat));
    ancre = liquidation;
  }
  const depart = niveaux.get(ancre);
  const parts = partsConvenues(simulateur, resultat, revalorisation);
  for (let annee = ancre + 1; annee <= derniere; annee += 1) {
    niveaux.set(annee, depart * macro.coefficientPrix(ancre, annee)
      * coefficientActuel(parts, revalorisation, ancre, annee));
  }
  return niveaux;
}

function pensionContributive(calcul, resultat) {
  const garantie = resultat.garantie_vieillesse;
  if (calcul.garantie && garantie !== null && garantie !== undefined) {
    return garantie.pension_contributive;
  }
  return resultat.pension_annuelle;
}

/** Le niveau annuel de la pension d'un système notionnel, en euros courants. */
export function niveauxNotionnels(simulateur, comparaison, scenario, revalorisation,
  actuels, derniere) {
  const parametres = simulateur.parametres;
  const calcul = simulateur.calculs[scenario];
  const macro = simulateur.macro;
  const resultat = comparaison[scenario];
  const liquidation = comparaison.carriereDe(scenario).anneeLiquidation;
  const bascule = parametres.annee_bascule;
  if (calcul.prospectif && liquidation <= bascule) {
    const niveaux = new Map([...actuels].filter(([annee]) => annee <= bascule));
    const base = actuels.get(bascule);
    const reindexe = parametres.revalorisation_stock === "reindexe";
    for (let annee = bascule + 1; annee <= derniere; annee += 1) {
      const reel = reindexe ? revalorisation.coefficient(bascule, annee) : 1.0;
      niveaux.set(annee, base * macro.coefficientPrix(bascule, annee) * reel);
    }
    return niveaux;
  }
  const pension = pensionContributive(calcul, resultat);
  const rente = resultat.rente_capitalisation_obligatoire ?? 0.0;
  const niveaux = new Map();
  for (let annee = liquidation; annee <= derniere; annee += 1) {
    niveaux.set(annee, pension * macro.coefficientPrix(liquidation, annee)
      * revalorisation.coefficientStock(liquidation, annee, calcul.prospectif) + rente);
  }
  return niveaux;
}

/**
 * Les deux flux d'une carrière sous chacun des six systèmes ; avec `nets`,
 * leurs revenus nets aussi (`revenusNets`), sur la fiche du droit en vigueur,
 * ou sur celle de la proposition pour le scénario 6 ; avec `impot`,
 * l'indexation du barème de l'impôt sur le revenu, l'impôt de chaque année
 * aussi, et les revenus nets qu'il laisse (`avecLImpot`).
 */
export function fluxDesSystemes(simulateur, comparaison, { nets = false, impot = null } = {}) {
  const carriere = comparaison.carriere;
  let derniere = -Infinity;
  for (const scenario of SCENARIOS) {
    derniere = Math.max(derniere, derniereAnneeDe(comparaison.carriereDe(scenario)));
  }
  const revalorisation = new RevalorisationServie(
    simulateur, simulateur.parametres.annee_debut_repartition, derniere);
  const versees = cotisationsVersees(simulateur, carriere);
  const actuels = niveauxActuels(simulateur, comparaison, revalorisation, derniere);
  const parts = impot === null ? null : partsImposablesParAnnee(simulateur, comparaison);
  const exonerees = impot === null ? {} : partsExonerees(simulateur, comparaison);
  // Les revenus de chaque carrière, leur net et, sous l'impôt, leur net
  // imposable : une fiche de paie par année, une fois par carrière et par
  // fiche (`_cle_des_revenus`).
  const revenus = new Map();
  const revenusDe = (scenario) => {
    const duScenario = comparaison.carriereDe(scenario);
    const proposition = scenario in simulateur.calculs
      ? Boolean(simulateur.calculs[scenario].garantie) : false;
    if (!revenus.has(duScenario)) revenus.set(duScenario, new Map());
    const parFiche = revenus.get(duScenario);
    if (!parFiche.has(proposition)) {
      const bruts = revenusDActivite(duScenario);
      let lus;
      if (impot === null) {
        lus = [bruts, nets ? revenusNets(simulateur, duScenario, proposition) : null, null];
      } else {
        const deux = netsEtImposables(simulateur, duScenario, proposition);
        lus = deux === null ? [bruts, null, null] : [bruts, ...deux];
      }
      parFiche.set(proposition, lus);
    }
    return parFiche.get(proposition);
  };

  const flux = (scenario, cotisations, niveaux) => {
    const duScenario = comparaison.carriereDe(scenario);
    const [bruts, netsDuScenario, imposables] = revenusDe(scenario);
    const dernier = duScenario !== carriere
      ? comparaison.dernier_revenu_annualise_liberal
      : comparaison.dernier_revenu_annualise;
    const avantImpot = new Flux({
      scenario,
      cotisations,
      revenus: bruts,
      niveaux,
      debut: debutDe(duScenario),
      age: duScenario.age_liquidation,
      sexe: duScenario.sexe,
      dernier_revenu: dernier,
      revenus_nets: netsDuScenario,
      dernier_revenu_net: dernierRevenuNet(dernier, bruts, netsDuScenario),
      exoneree: exonerees[scenario] ?? new Map(),
    });
    if (impot === null) return avantImpot;
    return avecLImpot(simulateur, avantImpot, duScenario, parts, imposables, impot, derniere);
  };

  const systemes = { actuel: flux("actuel", versees, actuels) };
  const reformees = cotisationsReformees(simulateur, comparaison);
  for (const scenario of SCENARIOS.slice(1)) {
    const cotisations = simulateur.calculs[scenario].garantie
      ? cotisationsLiberales(simulateur, versees, comparaison[scenario])
      : reformees;
    systemes[scenario] = flux(scenario, cotisations, niveauxNotionnels(
      simulateur, comparaison, scenario, revalorisation, actuels, derniere));
  }
  return systemes;
}

// -- la fin de la retraite ---------------------------------------------------

/**
 * ∫ S(x) dx de `debut` à `fin` années après le départ, la force de mortalité
 * constante entre deux anniversaires du départ.
 */
export function integraleSurvie(courbe, debut, fin) {
  let total = 0.0;
  let x = debut;
  while (x < fin - 1e-12) {
    const rang = Math.floor(x + 1e-12);
    const borne = Math.min(fin, rang + 1);
    if (rang + 1 >= courbe.length) break;
    const haut = courbe[rang];
    const bas = courbe[rang + 1];
    if (haut <= 0.0) break;
    const u0 = x - rang;
    const u1 = borne - rang;
    if (bas <= 0.0) {
      total += haut * ((u1 - u0) - (u1 * u1 - u0 * u0) / 2.0);
    } else if (Math.abs(bas - haut) <= 1e-15 * haut) {
      total += haut * (u1 - u0);
    } else {
      const logarithme = log(bas / haut);
      total += haut * (exp(logarithme * u1) - exp(logarithme * u0)) / logarithme;
    }
    x = borne;
  }
  return total;
}

function trieesNiveaux(flux) {
  return trieesParAnnee(flux.niveaux);
}

/**
 * Chaque année servie : [année, pension espérée en euros courants, instant
 * moyen, années de vie espérées dans l'année].
 */
export function pensionsEsperees(flux, simulateur, convention) {
  verifierLImpot(flux, convention);
  const esperees = [];
  if (convention.age_deces !== null) {
    const deces = flux.naissance + convention.age_deces;
    for (const [annee, niveau] of trieesNiveaux(flux)) {
      const debut = Math.max(annee, flux.debut);
      const fin = Math.min(annee + 1, deces);
      if (fin > debut) {
        esperees.push([annee, niveau * (fin - debut) * retenu(flux, convention, annee),
          (debut + fin) / 2.0, fin - debut]);
      }
    }
    return esperees;
  }
  const courbe = simulateur.mortalite.courbe(flux.age, flux.debut,
    convention.unisexe ? null : flux.sexe);
  for (const [annee, niveau] of trieesNiveaux(flux)) {
    const debut = Math.max(annee, flux.debut);
    const fin = annee + 1;
    if (fin <= debut) continue;
    const vie = integraleSurvie(courbe, debut - flux.debut, fin - flux.debut);
    if (vie > 0.0) {
      esperees.push([annee, niveau * vie * retenu(flux, convention, annee),
        (debut + fin) / 2.0, vie]);
    }
  }
  return esperees;
}

/**
 * La part de la pension brute de l'année `annee` qui reste : ce que les
 * prélèvements de la convention laissent, moins, après impôt, ce que
 * l'impôt prend.
 */
function retenu(flux, convention, annee) {
  if (convention.impot === null) return convention.retenu(annee);
  return convention.retenu(annee) - flux.impotDeLaPension(annee);
}

/** Une convention après impôt demande un flux qui porte l'impôt de son indexation. */
function verifierLImpot(flux, convention) {
  if (convention.impot !== null && flux.indexation_impot !== convention.impot) {
    throw new Error(`la convention est après impôt ('${convention.impot}') : il faut les flux `
      + `de fluxDesSystemes(…, {impot: '${convention.impot}'})`);
  }
}

/**
 * L'âge de décès des cas types du COR : 60 ans plus l'espérance de vie à 60
 * ans de la génération, les deux sexes réunis.
 */
export function ageDeDecesCor(mortalite, generation) {
  return 60.0 + mortalite.esperanceResiduelle(60.0, generation + 60.0, null);
}

/**
 * Ce que les prélèvements de l'année courante retirent à la pension du
 * scénario 1 de `resultat`, en part du brut.
 */
export function tauxDePrelevement(simulateur, resultat, anneeLiquidation = null) {
  const prelevements = simulateur.baremePrelevements.pensions;
  const total = auDepart(simulateur, resultat);
  if (total <= 0.0) return prelevements.tauxTotal;
  let complementaire = 0.0;
  for (const p of resultat.pensions_par_regime) {
    if (prelevements.regimes_maladie.has(p.regime)) complementaire += p.montant;
  }
  // La SNCF et les mines, sur leur part, sous le plafond de la SNCF.
  const parts = prelevements.regimes_speciaux.length > 0
    ? partsAssujetties(simulateur, resultat, anneeLiquidation) : new Map();
  let speciaux = 0.0;
  for (const special of prelevements.regimes_speciaux) {
    speciaux += special.taux * (parts.get(special.serie) ?? 0.0);
  }
  return prelevements.tauxTotal + prelevements.maladie_complementaire * complementaire / total
    + speciaux;
}

/**
 * Les conventions du rendement interne des cas types du COR : les deux sexes
 * réunis, le décès à 60 ans plus l'espérance de vie à 60 ans de la
 * génération, la pension nette au taux plein de CSG, chaque année au taux de
 * son année (`prelevementsParAnnee`). Jumeau de `convention_cor`.
 */
export function conventionCor(simulateur, comparaison) {
  return new Convention({
    age_deces: ageDeDecesCor(simulateur.mortalite, comparaison.carriere.annee_naissance),
    unisexe: true,
    prelevement: tauxDePrelevement(simulateur, comparaison.actuel,
      comparaison.carriere.anneeLiquidation),
    prelevements: prelevementsParAnnee(simulateur, comparaison),
  });
}

/**
 * La convention nette : celle du COR avec `cor`, sinon celle de l'OCDE, la
 * pension nette des prélèvements de chaque année. Jumeau de `convention_nette`.
 */
export function conventionNette(simulateur, comparaison, cor = false) {
  if (cor) return conventionCor(simulateur, comparaison);
  return new Convention({
    prelevement: tauxDePrelevement(simulateur, comparaison.actuel,
      comparaison.carriere.anneeLiquidation),
    prelevements: prelevementsParAnnee(simulateur, comparaison),
  });
}

/**
 * Les parts de la pension du scénario 1 au départ qui ont payé une cotisation
 * maladie, par cotisation : une `Map` de la série à sa part. Jumeau de
 * `_parts_assujetties`.
 */
export function partsAssujetties(simulateur, resultat, anneeLiquidation = null) {
  const total = auDepart(simulateur, resultat);
  if (total <= 0.0) return new Map([["maladie_complementaires", 1.0]]);
  const prelevements = simulateur.baremePrelevements.pensions;
  const groupes = new Map(historiqueDe(simulateur).regimes_des_pensions);
  groupes.set("maladie_complementaires", prelevements.regimes_maladie);
  const parts = new Map();
  for (const [serie, regimes] of groupes) {
    let montant = 0.0;
    for (const p of resultat.pensions_par_regime) if (regimes.has(p.regime)) montant += p.montant;
    parts.set(serie, montant / total);
  }
  // La SNCF depuis 2010 : sa part sous son plafond, la pension du départ menée
  // par les prix en euros de l'année du plafond.
  for (const special of prelevements.regimes_speciaux) {
    const part = parts.get(special.serie) ?? 0.0;
    if (special.plafond_annuel !== null && anneeLiquidation !== null && part > 0.0) {
      const montant = part * total * simulateur.macro.coefficientPrix(
        anneeLiquidation, special.annee);
      parts.set(special.serie, part * Math.min(1.0, special.plafond_annuel / montant));
    }
  }
  return parts;
}

/** Du premier départ des systèmes à la dernière année qu'une pension peut atteindre. */
function anneesDesPensions(comparaison) {
  const carrieres = SCENARIOS.map((scenario) => comparaison.carriereDe(scenario));
  const premiere = Math.min(...carrieres.map((c) => c.anneeLiquidation));
  const derniere = Math.max(...carrieres.map(derniereAnneeDe));
  return Array.from({ length: derniere - premiere + 1 }, (_, rang) => premiere + rang);
}

/**
 * Ce que les prélèvements de chaque année retirent aux pensions de
 * `comparaison`, au taux plein de CSG, du premier départ à la dernière année
 * qu'une pension peut atteindre. Jumeau de `prelevements_par_annee`.
 */
export function prelevementsParAnnee(simulateur, comparaison) {
  const historique = historiqueDe(simulateur);
  const parts = partsAssujetties(simulateur, comparaison.actuel,
    comparaison.carriere.anneeLiquidation);
  return new Map(anneesDesPensions(comparaison)
    .map((annee) => [annee, historique.tauxPensionAnnuel(annee, parts)]));
}

/**
 * La part des pensions que le revenu imposable de chaque année retient.
 * Jumeau de `parts_imposables_par_annee`.
 */
export function partsImposablesParAnnee(simulateur, comparaison) {
  const historique = historiqueDe(simulateur);
  const parts = partsAssujetties(simulateur, comparaison.actuel,
    comparaison.carriere.anneeLiquidation);
  return new Map(anneesDesPensions(comparaison)
    .map((annee) => [annee, 1.0 - historique.tauxDeductiblePensionAnnuel(annee, parts)]));
}

/**
 * La première année de revenus dont l'impôt prend les majorations pour
 * charges de famille (loi de finances pour 2014, art. 5 et art. 1er, II, 1°),
 * et la limite de leur exonération jusque-là : 10 % de la pension pour les
 * trois premiers enfants, 5 % par enfant au-delà (DB 5 F 1222, n° 4).
 */
export const PREMIERE_ANNEE_MAJORATION_IMPOSABLE = 2013;
export const TAUX_EXONERE_TROIS_ENFANTS = 0.10;
export const TAUX_EXONERE_PAR_ENFANT_AU_DELA = 0.05;

/**
 * La part de `majoration`, que sert l'année `annee` une pension de `pension`
 * sans elle, que l'impôt de l'année exonère. Jumeau de `majoration_exoneree`.
 */
export function majorationExoneree(annee, majoration, pension, enfants) {
  if (annee >= PREMIERE_ANNEE_MAJORATION_IMPOSABLE || majoration <= 0.0) return 0.0;
  const taux = TAUX_EXONERE_TROIS_ENFANTS
    + TAUX_EXONERE_PAR_ENFANT_AU_DELA * Math.max(enfants - 3, 0);
  return Math.min(majoration, taux * pension);
}

/**
 * Pour chaque système, la part du niveau de sa pension que l'impôt de chaque
 * année exonère : celle du scénario 1, que les systèmes prospectifs gardent
 * à qui est parti avant la bascule. Jumeau de `parts_exonerees`.
 */
export function partsExonerees(simulateur, comparaison) {
  const carriere = comparaison.carriere;
  const resultat = comparaison.actuel;
  const actuelle = new Map();
  if (resultat.avantages_appliques.some((a) => a.code === "majoration_enfants")) {
    const derniere = Math.min(PREMIERE_ANNEE_MAJORATION_IMPOSABLE - 1,
      simulateur.parametres.annee_courante);
    for (let annee = carriere.anneeLiquidation; annee <= derniere; annee += 1) {
      const vivante = faireVivre(simulateur, carriere, resultat, annee);
      const majoration = vivante.majoration_enfants * vivante.coefficient_majoration;
      const niveau = servie(vivante);
      const exoneree = majorationExoneree(annee, majoration, niveau - majoration,
        carriere.nombre_enfants);
      if (exoneree > 0.0) actuelle.set(annee, exoneree / niveau);
    }
  }
  const bascule = simulateur.parametres.annee_bascule;
  const parts = { actuel: actuelle };
  for (const scenario of SCENARIOS.slice(1)) {
    parts[scenario] = new Map();
    if (!(simulateur.calculs[scenario].prospectif
      && comparaison.carriereDe(scenario).anneeLiquidation <= bascule)) continue;
    for (const [annee, part] of actuelle) {
      if (annee <= bascule) parts[scenario].set(annee, part);
    }
    if (actuelle.has(bascule)) {
      for (let annee = bascule + 1; annee < PREMIERE_ANNEE_MAJORATION_IMPOSABLE; annee += 1) {
        parts[scenario].set(annee, actuelle.get(bascule));
      }
    }
  }
  return parts;
}

// -- l'impôt sur le revenu ---------------------------------------------------

const chroniques = new WeakMap();

/**
 * Les paramètres de l'impôt de chaque année de revenus, du premier barème lu
 * à `derniere`, projetés au-delà de la dernière loi de finances lue sur
 * `indexation` par le scénario de projection du simulateur : une `Map`.
 */
function baremesDeLImpot(simulateur, indexation, derniere) {
  if (!chroniques.has(simulateur)) chroniques.set(simulateur, new Map());
  const memoire = chroniques.get(simulateur);
  const cle = `${indexation}:${derniere}`;
  if (!memoire.has(cle)) {
    const baremes = chargerBaremesImpotRevenu(simulateur.paquet);
    if (baremes === null) {
      throw new Error("le paquet ne porte pas les barèmes de l'impôt sur le revenu "
        + "(`impot_revenu`) : l'impôt ne se calcule pas");
    }
    memoire.set(cle, baremes.chronique(derniere, indexation,
      croissanceMacro(simulateur.macro, indexation)));
  }
  return memoire.get(cle);
}

/**
 * Le foyer fiscal de `carriere` l'année `annee` : une personne seule, sans
 * enfant à charge, qui a au 31 décembre l'âge de sa génération et déclare
 * `salaire`, `benefice` (de `categorie`, au réel, adhérent) et `pension`,
 * imposables. Jumeau de `foyer_de_l_annee`.
 */
export function foyerDeLAnnee(carriere, annee, salaire = 0.0, pension = 0.0, benefice = 0.0,
  categorie = "bic") {
  return new Foyer({
    declarants: [new Declarant({
      salaires: salaire, pensions: pension, benefices: benefice, categorie,
      age: annee - carriere.annee_naissance,
    })],
  });
}

/** Les familles d'indépendant dont le bénéfice est non commercial. */
export const FAMILLES_BNC = Object.freeze(["liberal", "avocat"]);

/**
 * Les années où `carriere` a un revenu d'indépendant : une `Map` de l'année
 * à [la part de son revenu imposable qui est un bénéfice, sa catégorie].
 * Jumeau de `benefices_par_annee`.
 */
export function beneficesParAnnee(simulateur, carriere) {
  const revenus = new Map();
  const independants = new Map();
  for (const ligne of carriere.lignes) {
    if (!ligne.cotise) continue;
    revenus.set(ligne.annee, (revenus.get(ligne.annee) ?? 0.0) + ligne.revenu);
    const entree = carriere.dateEntree(ligne.affiliation);
    const profil = profilDeLaFiche(simulateur.affiliations, simulateur.catalogue,
      ligne.affiliation, ligne.annee, entree);
    if (profil !== "independant") continue;
    const regimes = simulateur.affiliations.regimes(ligne.affiliation, ligne.annee, entree);
    const famille = familleDeLaFiche(profil, regimes);
    if (!independants.has(ligne.annee)) independants.set(ligne.annee, []);
    independants.get(ligne.annee).push(
      [ligne.revenu, FAMILLES_BNC.includes(famille) ? "bnc" : "bic"]);
  }
  const benefices = new Map();
  for (const [annee, lignes] of independants) {
    let total = 0.0;
    for (const [revenu] of lignes) total += revenu;
    const part = revenus.get(annee) > 0.0 ? total / revenus.get(annee) : 1.0;
    let plusFort = lignes[0];
    for (const l of lignes) if (l[0] > plusFort[0]) plusFort = l;
    benefices.set(annee, [Math.min(part, 1.0), plusFort[1]]);
  }
  return benefices;
}

/** Les revenus imposables partagés entre salaires et bénéfices. Jumeau de `_partage_des_imposables`. */
function partageDesImposables(simulateur, carriere, imposables) {
  const parts = beneficesParAnnee(simulateur, carriere);
  const salaires = new Map();
  const benefices = new Map();
  for (const [annee, montant] of imposables) {
    const [part, categorie] = parts.get(annee) ?? [0.0, "bic"];
    if (part < 1.0) salaires.set(annee, montant * (1.0 - part));
    if (part > 0.0) benefices.set(annee, [montant * part, categorie]);
  }
  return [salaires, benefices];
}

/** La part de l'impôt d'un foyer que supporte sa pension, au prorata des revenus nets. */
function partDeLaPension(impot) {
  let activite = 0.0;
  for (const s of impot.salaires_nets) activite += s;
  for (const b of impot.benefices_retenus) activite += b;
  activite = Math.max(activite, 0.0);
  let pensions = 0.0;
  for (const p of impot.pensions_nettes) pensions += p;
  if (activite + pensions <= 0.0) return 0.0;
  return pensions / (activite + pensions);
}

/**
 * L'impôt sur le revenu de chaque année d'un flux : celui du foyer de
 * l'année, qui déclare son salaire imposable (`salaires`) et la part
 * imposable (`parts`) de ce que la pension sert dans l'année, au barème de
 * l'année. Une `Map` de l'année à son `ImpotDeLAnnee`. Jumeau de
 * `impots_par_annee`.
 */
export function impotsParAnnee(simulateur, flux, carriere, parts, salaires,
  indexation = "prix", derniere = null, benefices = new Map()) {
  const pensions = new Map();
  for (const [annee, niveau] of flux.niveaux) {
    const servieDansLAnnee = niveau * flux.servi(annee);
    if (servieDansLAnnee > 0.0) {
      pensions.set(annee, servieDansLAnnee * (1.0 - (flux.exoneree.get(annee) ?? 0.0))
        * parts.get(annee));
    }
  }
  const annees = [...new Set([...salaires.keys(), ...benefices.keys(), ...pensions.keys()])]
    .sort((a, b) => a - b);
  const impots = new Map();
  if (annees.length === 0) return impots;
  const baremes = baremesDeLImpot(simulateur, indexation,
    Math.max(annees[annees.length - 1], derniere ?? 0));
  for (const annee of annees) {
    const parametres = baremes.get(annee);
    if (parametres === undefined) continue;
    const salaire = salaires.get(annee) ?? 0.0;
    const pension = pensions.get(annee) ?? 0.0;
    const [benefice, categorie] = benefices.get(annee) ?? [0.0, "bic"];
    const foyer = impotAuxParametres(
      foyerDeLAnnee(carriere, annee, salaire, pension, benefice, categorie), parametres);
    impots.set(annee, new ImpotDeLAnnee({
      annee, salaire, pension, foyer, sur_la_pension: foyer.impot * partDeLaPension(foyer),
      benefice,
    }));
  }
  return impots;
}

/**
 * `flux` sous l'impôt sur le revenu : l'impôt de chaque année, les revenus
 * nets qu'il laisse et le dernier revenu net d'une année entière d'impôt.
 * Jumeau de `avec_l_impot`.
 */
export function avecLImpot(simulateur, flux, carriere, parts, imposables,
  indexation = "prix", derniere = null) {
  const [salaires, benefices] = imposables === null ? [new Map(), new Map()]
    : partageDesImposables(simulateur, carriere, imposables);
  const impots = impotsParAnnee(simulateur, flux, carriere, parts, salaires, indexation,
    derniere, benefices);
  let apres = null;
  let dernier = null;
  if (flux.revenus_nets !== null && imposables !== null) {
    apres = new Map([...flux.revenus_nets].map(([annee, net]) => [annee,
      net - (impots.has(annee) ? impots.get(annee).sur_le_salaire : 0.0)]));
    dernier = dernierRevenuApresImpot(simulateur, flux, imposables, indexation, derniere,
      benefices);
  }
  return flux.remplace({
    indexation_impot: indexation, impots, revenus_apres_impot: apres,
    dernier_revenu_apres_impot: dernier,
  });
}

/**
 * Le dernier revenu annualisé, net de ses prélèvements et de l'impôt d'une
 * année entière de ce revenu, déclaré seul au barème de l'année du départ ;
 * `null` sans dernier revenu net. Jumeau de `dernier_revenu_apres_impot`.
 */
export function dernierRevenuApresImpot(simulateur, flux, imposables, indexation = "prix",
  derniere = null, benefices = new Map()) {
  if (flux.dernier_revenu_net === null || flux.revenus.size === 0) return null;
  const annee = Math.max(...flux.revenus.keys());
  const imposable = flux.dernier_revenu * (imposables.get(annee) ?? 0.0)
    / flux.revenus.get(annee);
  const depart = flux.annee_liquidation;
  const parametres = baremesDeLImpot(simulateur, indexation,
    Math.max(depart, derniere ?? 0)).get(depart);
  if (parametres === undefined) return flux.dernier_revenu_net;
  const [benefice, categorie] = benefices.get(annee) ?? [0.0, "bic"];
  const part = benefice && imposables.get(annee) ? benefice / imposables.get(annee) : 0.0;
  const declarant = new Declarant({
    salaires: imposable * (1.0 - part), benefices: imposable * part, categorie,
  });
  const impot = impotAuxParametres(new Foyer({ declarants: [declarant] }), parametres);
  return flux.dernier_revenu_net - impot.impot;
}

/**
 * La convention nette, après impôt sur le revenu, son barème projeté sur
 * `indexation`. Jumeau de `convention_apres_impot`.
 */
export function conventionApresImpot(simulateur, comparaison, cor = false, indexation = "prix") {
  return conventionNette(simulateur, comparaison, cor).avecLImpot(indexation);
}

/**
 * La pension brute du premier mois servi, annualisée, en euros de l'année du
 * départ du système. Jumeau de `pension_au_depart`.
 */
export function pensionAuDepart(simulateur, comparaison, scenario) {
  if (scenario === "actuel") return auDepart(simulateur, comparaison.actuel);
  const calcul = simulateur.calculs[scenario];
  const liquidation = comparaison.carriereDe(scenario).anneeLiquidation;
  if (calcul.prospectif && liquidation <= simulateur.parametres.annee_bascule) {
    return auDepart(simulateur, comparaison.actuel);
  }
  const resultat = comparaison[scenario];
  return pensionContributive(calcul, resultat) + (resultat.rente_capitalisation_obligatoire ?? 0.0);
}

/**
 * Le taux de remplacement après impôt au départ du système `scenario` : le
 * taux net de l'OCDE ; `null` sans dernier revenu après impôt. `systemes`,
 * les flux sous l'impôt d'`indexation`, s'ils sont déjà calculés. Jumeau de
 * `remplacement_apres_impot`.
 */
export function remplacementApresImpot(simulateur, comparaison, scenario = "actuel",
  indexation = "prix", systemes = null) {
  const lesSystemes = systemes
    ?? fluxDesSystemes(simulateur, comparaison, { impot: indexation });
  const flux = lesSystemes[scenario];
  const convention = conventionNette(simulateur, comparaison);
  verifierLImpot(flux, convention.avecLImpot(indexation));
  return remplacementApresImpotDe(simulateur, comparaison, scenario, flux, convention,
    partsImposablesParAnnee(simulateur, comparaison));
}

/**
 * `remplacementApresImpot`, de la convention nette et des parts imposables de
 * la comparaison. Jumeau de `_remplacement_apres_impot`.
 */
function remplacementApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts) {
  const dernier = flux.dernier_revenu_apres_impot;
  if (dernier === null || dernier <= 0.0) return null;
  return pensionApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts) / dernier;
}

/**
 * La pension du premier mois servi, annualisée, nette des prélèvements de son
 * année et de l'impôt d'une année entière de cette pension, déclarée seule au
 * barème de l'année du départ. Jumeau de `_pension_apres_impot`.
 */
function pensionApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts) {
  const annee = flux.annee_liquidation;
  const brute = pensionAuDepart(simulateur, comparaison, scenario);
  const parametres = baremesDeLImpot(simulateur, flux.indexation_impot,
    Math.max(...flux.niveaux.keys())).get(annee);
  const imposable = brute * (1.0 - (flux.exoneree.get(annee) ?? 0.0)) * parts.get(annee);
  const impot = parametres === undefined ? 0.0 : impotAuxParametres(
    foyerDeLAnnee(comparaison.carriereDe(scenario), annee, 0.0, imposable),
    parametres).impot;
  return brute * convention.retenu(annee) - impot;
}

// -- les indicateurs ---------------------------------------------------------

function indices(macro, premiere, derniere) {
  const prix = new Map([[premiere, 1.0]]);
  const salaires = new Map([[premiere, 1.0]]);
  for (let annee = premiere + 1; annee <= derniere; annee += 1) {
    prix.set(annee, prix.get(annee - 1) * (1.0 + macro.inflation.valeur(annee)));
    salaires.set(annee, salaires.get(annee - 1) * (1.0 + macro.salaire_moyen.valeur(annee)));
  }
  return [prix, salaires];
}

/**
 * Le taux `r` qui annule Σ montant × (1 + r)^-(t − t₀), par dichotomie ;
 * `null` quand aucun taux des bornes ne l'annule.
 */
export function rendementInterne(flux) {
  if (flux.length === 0) return null;
  let origine = Infinity;
  for (const [instant] of flux) origine = Math.min(origine, instant);
  const valeur = (taux) => {
    let somme = 0.0;
    for (const [instant, montant] of flux) somme += montant * pow(1.0 + taux, -(instant - origine));
    return somme;
  };
  let [bas, haut] = BORNES_RENDEMENT;
  if (valeur(bas) <= 0.0 || valeur(haut) >= 0.0) return null;
  for (let i = 0; i < 200; i += 1) {
    const milieu = 0.5 * (bas + haut);
    if (valeur(milieu) > 0.0) bas = milieu;
    else haut = milieu;
    if (haut - bas < 1e-12) break;
  }
  return 0.5 * (bas + haut);
}

function instantCotisation(flux, annee) {
  if (annee === flux.annee_liquidation) return annee + Math.max(flux.debut - annee, 0.0) / 2.0;
  return annee + 0.5;
}

/** Les indicateurs de cycle de vie d'un système, sous `convention`. */
export function indicateurs(flux, simulateur, convention = new Convention()) {
  const esperees = pensionsEsperees(flux, simulateur, convention);
  let duree = 0.0;
  for (const [, , , vie] of esperees) duree += vie;
  const annees = [...esperees.map(([annee]) => annee), ...flux.cotisations.keys(),
    ...flux.revenus.keys()];
  const [prix, salaires] = indices(simulateur.macro, Math.min(...annees), Math.max(...annees));
  let revenus;
  let dernier;
  if (convention.impot !== null) {
    revenus = flux.revenus_apres_impot;
    dernier = flux.dernier_revenu_apres_impot;
  } else if (convention.nette) {
    revenus = flux.revenus_nets;
    dernier = flux.dernier_revenu_net;
  } else {
    revenus = flux.revenus;
    dernier = flux.dernier_revenu;
  }

  let pensionsSmpt = 0.0;
  for (const [annee, montant] of esperees) pensionsSmpt += montant / salaires.get(annee);
  let cotisationsSmpt = 0.0;
  for (const [annee, montant] of flux.cotisations) cotisationsSmpt += montant / salaires.get(annee);
  let revenusSmpt = null;
  if (revenus !== null) {
    revenusSmpt = 0.0;
    for (const [annee, montant] of revenus) revenusSmpt += montant / salaires.get(annee);
  }
  const carriere = flux.duree_carriere;

  const chronique = (indice) => [
    ...[...flux.cotisations].map(([annee, montant]) => [
      instantCotisation(flux, annee), -montant / indice.get(annee)]),
    ...esperees.map(([annee, montant, instant]) => [instant, montant / indice.get(annee)]),
  ];

  let patrimoine = null;
  let valeurNette = null;
  let remplacementAuDeces = null;
  if (flux.dernier_revenu > 0.0) {
    const liquidation = flux.annee_liquidation;
    const actualisation = 1.0 + convention.taux_actualisation;
    const aLaDate = (annee, montant, instant) => montant * prix.get(liquidation) / prix.get(annee)
      * pow(actualisation, -(instant - flux.debut));
    patrimoine = 0.0;
    for (const [annee, montant, instant] of esperees) patrimoine += aLaDate(annee, montant, instant);
    let capitalisees = 0.0;
    for (const [annee, montant] of flux.cotisations) {
      capitalisees += aLaDate(annee, montant, instantCotisation(flux, annee));
    }
    valeurNette = patrimoine - capitalisees;
    patrimoine /= flux.dernier_revenu;
    valeurNette /= flux.dernier_revenu;
    const derniereServie = Math.floor(flux.debut + duree - 1e-9);
    if (duree > 0.0 && flux.niveaux.has(derniereServie) && dernier) {
      remplacementAuDeces = flux.niveaux.get(derniereServie)
        * retenu(flux, convention, derniereServie)
        / (dernier * salaires.get(derniereServie) / salaires.get(liquidation));
    }
  }

  const avecCotisations = flux.cotisations.size > 0;
  return new Indicateurs({
    scenario: flux.scenario,
    duree_retraite: duree,
    part_de_vie: flux.age + duree > 0 ? duree / (flux.age + duree) : 0.0,
    duree_carriere: carriere,
    taux_recuperation: cotisationsSmpt > 0 ? pensionsSmpt / cotisationsSmpt : null,
    taux_annuite: revenusSmpt ? pensionsSmpt / revenusSmpt : null,
    taux_remplacement_cycle: duree > 0 && carriere > 0 && revenusSmpt
      ? (pensionsSmpt / duree) / (revenusSmpt / carriere) : null,
    rendement_reel: avecCotisations ? rendementInterne(chronique(prix)) : null,
    rendement_smpt: avecCotisations ? rendementInterne(chronique(salaires)) : null,
    patrimoine,
    valeur_nette: valeurNette,
    remplacement_au_deces: remplacementAuDeces,
  });
}

/** Les indicateurs d'une carrière sous chacun des six systèmes. */
export function indicateursDesSystemes(simulateur, comparaison, convention = new Convention()) {
  const systemes = fluxDesSystemes(simulateur, comparaison,
    { nets: convention.nette, impot: convention.impot });
  return Object.fromEntries(Object.entries(systemes)
    .map(([scenario, flux]) => [scenario, indicateurs(flux, simulateur, convention)]));
}

// -- les âges de départ ------------------------------------------------------

/** Le pas du balayage des âges de départ, en années : un trimestre. */
export const PAS_DES_AGES = 0.25;

/**
 * Le minimum vieillesse d'une personne seule l'année `annee`, en euros par
 * an : l'ASPA depuis 2007, menée sur les prix au-delà de son barème ; avant,
 * ses deux étages. `null` avant la loi du 14 mars 1941. Jumeau de
 * `minimum_vieillesse`.
 */
export function minimumVieillesse(simulateur, annee) {
  const bareme = simulateur.scenarioActuel.minimumVieillesse;
  if (annee <= bareme.constructor.DERNIERE_ANNEE_A_DEUX_ETAGES) {
    const etages = bareme.deuxEtages(annee);
    return etages === null ? null : etages.avts + etages.supplementaire;
  }
  const plafond = bareme.plafond(annee);
  return plafond === null ? null : plafond[0];
}

/**
 * La dernière année civile travaillée en entier avant celle du départ ;
 * `null` sans année pleine. Jumeau de `derniere_annee_pleine`.
 */
export function derniereAnneePleine(carriere) {
  const couverture = new Map();
  for (const ligne of carriere.lignes) {
    if (ligne.cotise && ligne.annee < carriere.anneeLiquidation) {
      couverture.set(ligne.annee, (couverture.get(ligne.annee) ?? 0.0) + ligne.fraction_annee);
    }
  }
  const pleines = [...couverture].filter(([, part]) => part >= 1.0 - 1e-9)
    .map(([annee]) => annee);
  return pleines.length ? Math.max(...pleines) : null;
}

/**
 * La pension nette du départ sur le revenu net de la dernière année pleine,
 * chacun en euros de son année (`courants`), en euros constants
 * (`constants`), en salaire moyen par tête de son année (`salaire_moyen`).
 * Jumeau de `RemplacementNet`.
 */
export class RemplacementNet {
  constructor({ courants, constants, salaire_moyen }) {
    Object.assign(this, { courants, constants, salaire_moyen });
  }
}

/**
 * Le taux de remplacement net au départ de `carriere`, en trois unités ;
 * `null` sans année pleine ou sans revenu net. Jumeau de `remplacement_net`.
 */
export function remplacementNet(simulateur, carriere, nets, pensionNette) {
  const annee = derniereAnneePleine(carriere);
  if (annee === null || !nets || nets.size === 0 || (nets.get(annee) ?? 0.0) <= 0.0) {
    return null;
  }
  const courants = pensionNette / nets.get(annee);
  const liquidation = carriere.anneeLiquidation;
  const { macro } = simulateur;
  return new RemplacementNet({
    courants,
    constants: courants / macro.coefficientPrix(annee, liquidation),
    salaire_moyen: courants / macro.coefficientSalaireMoyen(annee, liquidation),
  });
}

/**
 * Un âge du balayage, et ce qu'y donne chacun des six systèmes, en net :
 * `age`, `annee` (du départ du scénario 1), `indicateurs`, `pensions_nettes`,
 * `pensions_aspa`, `remplacements`, `remplacements_apres_impot` et
 * `pensions_apres_impot` (`null` avant impôt), chacun un objet par système.
 * Jumeau de `Depart`.
 */
export class Depart {
  constructor({
    age, annee, indicateurs: lesIndicateurs, pensions_nettes, pensions_aspa, remplacements,
    remplacements_apres_impot = null, pensions_apres_impot = null,
  }) {
    Object.assign(this, {
      age, annee, indicateurs: lesIndicateurs, pensions_nettes, pensions_aspa, remplacements,
      remplacements_apres_impot, pensions_apres_impot,
    });
  }
}

/**
 * Ce que donne, en net, le départ de `comparaison` sous les six systèmes ;
 * avec `impot`, l'indexation du barème de l'impôt sur le revenu, les
 * indicateurs après impôt, la pension et le taux de remplacement après
 * impôt. Jumeau de `depart`.
 */
export function depart(simulateur, comparaison, cor = false, age = null, impot = null) {
  const convention = impot === null ? conventionNette(simulateur, comparaison, cor)
    : conventionApresImpot(simulateur, comparaison, cor, impot);
  const systemes = fluxDesSystemes(simulateur, comparaison, { nets: true, impot });
  let apres = null;
  let pensionsApres = null;
  if (impot !== null) {
    const parts = partsImposablesParAnnee(simulateur, comparaison);
    apres = Object.fromEntries(Object.entries(systemes).map(([scenario, flux]) => [scenario,
      remplacementApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts)]));
    pensionsApres = Object.fromEntries(Object.entries(systemes).map(([scenario, flux]) => [
      scenario, pensionApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts)]));
  }
  const pensions = {};
  const aspa = {};
  const remplacements = {};
  for (const [scenario, flux] of Object.entries(systemes)) {
    const carriere = comparaison.carriereDe(scenario);
    const nette = pensionAuDepart(simulateur, comparaison, scenario)
      * convention.retenu(carriere.anneeLiquidation);
    const minimum = minimumVieillesse(simulateur, carriere.anneeLiquidation);
    pensions[scenario] = nette;
    aspa[scenario] = minimum ? nette / minimum : null;
    remplacements[scenario] = remplacementNet(simulateur, carriere, flux.revenus_nets, nette);
  }
  return new Depart({
    age: age === null ? comparaison.carriere.age_liquidation : age,
    annee: comparaison.carriere.anneeLiquidation,
    indicateurs: Object.fromEntries(Object.entries(systemes)
      .map(([scenario, flux]) => [scenario, indicateurs(flux, simulateur, convention)])),
    pensions_nettes: pensions,
    pensions_aspa: aspa,
    remplacements,
    remplacements_apres_impot: apres,
    pensions_apres_impot: pensionsApres,
  });
}

/**
 * Les âges de départ de la carrière que `batir(age)` rend liquidée à `age`,
 * de `pas` en `pas` : de l'âge d'ouverture, carrière longue comprise, à
 * l'âge d'annulation de la décote (`agesDeLEstimation`, partis de
 * `ageDemande`) ; le dernier est toujours l'âge d'annulation. Vide quand le
 * droit n'oppose aucun âge à la carrière. Jumeau de `ages_balayes`.
 */
export function agesBalayes(simulateur, batir, ageDemande, pas = PAS_DES_AGES) {
  const ages = agesDeLEstimation(simulateur.scenarioActuel, batir, ageDemande);
  if (ages === null) return [];
  const debut = Number(ages.legal);
  const fin = Number(ages.automatique);
  const nombre = Math.floor((fin - debut) / pas + 1e-9);
  const balayes = [];
  for (let rang = 0; rang <= nombre; rang += 1) {
    balayes.push(Number((debut + rang * pas).toFixed(9)));
  }
  if (fin - balayes[balayes.length - 1] > 1e-9) balayes.push(fin);
  return balayes;
}

/**
 * Les indicateurs nets de la carrière que `batir(age)` rend liquidée à
 * `age`, à chacun de ses âges de départ (`agesBalayes`) ; avec `impot`,
 * après impôt (`depart`). Jumeau de `balayage_d_une_carriere`.
 */
export function balayageDUneCarriere(simulateur, batir, ageDemande, cor = false,
  pas = PAS_DES_AGES, impot = null) {
  return agesBalayes(simulateur, batir, ageDemande, pas)
    .map((age) => depart(simulateur, simulateur.simuler(batir(age)), cor, age, impot));
}

// -- la pension par étage, et le revenu autour du départ ----------------------

/** L'étage d'un système notionnel, son compte ; celui du pilier du scénario 6. */
export const ETAGE_NOTIONNEL = "notionnel";
export const ETAGE_CAPITALISE = "capitalise";

/** Les années montrées de part et d'autre de celle du départ. */
export const ANNEES_AUTOUR_DU_DEPART = 10;

function rapport(montant, revenu) {
  if (montant === null || revenu === null || revenu <= 0.0) return null;
  return montant / revenu;
}

/**
 * La pension du départ, étage par étage, et ce qu'elle remplace du dernier
 * revenu : `etages`, `dernier_revenu`, `nette`, `dernier_revenu_net`,
 * `apres_impot`, `dernier_revenu_apres_impot`. Jumeau de `PensionParEtage`.
 */
export class PensionParEtage {
  constructor({
    etages, dernier_revenu, nette = null, dernier_revenu_net = null, apres_impot = null,
    dernier_revenu_apres_impot = null,
  }) {
    Object.assign(this, {
      etages, dernier_revenu, nette, dernier_revenu_net, apres_impot,
      dernier_revenu_apres_impot,
    });
    Object.freeze(this);
  }

  get brute() {
    let total = 0.0;
    for (const montant of Object.values(this.etages)) total += montant;
    return total;
  }

  /** Chaque étage en part du dernier revenu ; vide sans dernier revenu. */
  get parts() {
    if (this.dernier_revenu <= 0.0) return {};
    return Object.fromEntries(Object.entries(this.etages)
      .map(([etage, montant]) => [etage, montant / this.dernier_revenu]));
  }

  get remplacement_brut() {
    return rapport(this.brute, this.dernier_revenu);
  }

  get remplacement_net() {
    return rapport(this.nette, this.dernier_revenu_net);
  }

  get remplacement_apres_impot() {
    return rapport(this.apres_impot, this.dernier_revenu_apres_impot);
  }

  dictionnaire() {
    return {
      etages: { ...this.etages }, parts: this.parts, brute: this.brute,
      dernier_revenu: this.dernier_revenu, nette: this.nette,
      dernier_revenu_net: this.dernier_revenu_net, apres_impot: this.apres_impot,
      dernier_revenu_apres_impot: this.dernier_revenu_apres_impot,
      remplacement_brut: this.remplacement_brut,
      remplacement_net: this.remplacement_net,
      remplacement_apres_impot: this.remplacement_apres_impot,
    };
  }
}

/**
 * La pension brute du premier mois servi, annualisée, étage par étage, en
 * euros de l'année du départ du système : au scénario 1, chaque régime à son
 * étage du catalogue, sa part de la majoration pour enfants comprise ; un
 * système notionnel, son compte, et le scénario 6 son pilier. Jumeau de
 * `etages_au_depart`.
 */
export function etagesAuDepart(simulateur, comparaison, scenario) {
  if (scenario !== "actuel") {
    const calcul = simulateur.calculs[scenario];
    const liquidation = comparaison.carriereDe(scenario).anneeLiquidation;
    if (!(calcul.prospectif && liquidation <= simulateur.parametres.annee_bascule)) {
      const resultat = comparaison[scenario];
      const etages = { [ETAGE_NOTIONNEL]: pensionContributive(calcul, resultat) };
      const rente = resultat.rente_capitalisation_obligatoire ?? 0.0;
      if (rente) etages[ETAGE_CAPITALISE] = rente;
      return etages;
    }
  }
  const resultat = comparaison.actuel;
  const etages = {};
  const porter = (regime, montant) => {
    if (!montant) return;
    const { etage } = simulateur.catalogue.obtenir(regime);
    etages[etage] = (etages[etage] ?? 0.0) + montant;
  };
  for (const pension of resultat.pensions_par_regime) {
    if (!horsRepartition(simulateur, pension.regime)) porter(pension.regime, pension.montant);
  }
  for (const avantage of resultat.avantages_appliques) {
    if (avantage.code === "majoration_enfants") {
      for (const [regime, part] of avantage.par_regime ?? []) porter(regime, part);
    }
  }
  return etages;
}

/**
 * La pension du départ du système `scenario`, étage par étage, en part du
 * dernier revenu annualisé : le tableau 1 de Typfallsmodellen. `systemes`,
 * les flux nets ou sous un impôt, s'ils sont déjà calculés ; sans eux, les
 * flux nets, avant impôt. Jumeau de `pension_par_etage`.
 */
export function pensionParEtage(simulateur, comparaison, scenario = "actuel", systemes = null) {
  const lesSystemes = systemes ?? fluxDesSystemes(simulateur, comparaison, { nets: true });
  const flux = lesSystemes[scenario];
  const convention = conventionNette(simulateur, comparaison);
  const etages = etagesAuDepart(simulateur, comparaison, scenario);
  const brute = new PensionParEtage({ etages, dernier_revenu: flux.dernier_revenu }).brute;
  const apres = flux.impots === null ? null : pensionApresImpotDe(
    simulateur, comparaison, scenario, flux, convention,
    partsImposablesParAnnee(simulateur, comparaison));
  return new PensionParEtage({
    etages, dernier_revenu: flux.dernier_revenu,
    nette: brute * convention.retenu(flux.annee_liquidation),
    dernier_revenu_net: flux.dernier_revenu_net, apres_impot: apres,
    dernier_revenu_apres_impot: flux.dernier_revenu_apres_impot,
  });
}

/**
 * Une année autour du départ, en euros de l'année du départ : `annee`,
 * `revenu`, `pension`, `net` (`null` sans fiche de paie), `impot` (`null`
 * avant impôt). Jumeau de `AnneeAutourDuDepart`.
 */
export class AnneeAutourDuDepart {
  constructor({ annee, revenu, pension, net, impot }) {
    Object.assign(this, { annee, revenu, pension, net, impot });
    Object.freeze(this);
  }

  get brut() {
    return this.revenu + this.pension;
  }

  get apres_impot() {
    if (this.net === null || this.impot === null) return null;
    return this.net - this.impot;
  }

  dictionnaire() {
    return {
      annee: this.annee, revenu: this.revenu, pension: this.pension, brut: this.brut,
      net: this.net, impot: this.impot, apres_impot: this.apres_impot,
    };
  }
}

/**
 * Le revenu de chaque année, de `annees` avant celle du départ du système
 * `scenario` à `annees` après, en euros de l'année du départ : le tableau 2
 * de Typfallsmodellen. Jumeau de `revenus_autour_du_depart`.
 */
export function revenusAutourDuDepart(simulateur, comparaison, scenario = "actuel",
  systemes = null, annees = ANNEES_AUTOUR_DU_DEPART) {
  const lesSystemes = systemes ?? fluxDesSystemes(simulateur, comparaison, { nets: true });
  const flux = lesSystemes[scenario];
  const convention = conventionNette(simulateur, comparaison);
  const depart = flux.annee_liquidation;
  const lignes = [];
  for (let annee = depart - annees; annee <= depart + annees; annee += 1) {
    const euros = simulateur.macro.coefficientPrix(annee, depart);
    const pension = (flux.niveaux.get(annee) ?? 0.0) * flux.servi(annee);
    const net = flux.revenus_nets === null ? null
      : ((flux.revenus_nets.get(annee) ?? 0.0) + pension * convention.retenu(annee)) * euros;
    let impot = null;
    if (flux.impots !== null) {
      impot = flux.impots.has(annee) ? flux.impots.get(annee).impot * euros : 0.0;
    }
    lignes.push(new AnneeAutourDuDepart({
      annee, revenu: (flux.revenus.get(annee) ?? 0.0) * euros, pension: pension * euros,
      net, impot,
    }));
  }
  return lignes;
}

// -- l'âge d'équilibre -------------------------------------------------------

/**
 * La génération à laquelle le compte rapporte les autres : celle qui a l'âge
 * de référence au 1er janvier de l'année de la bascule.
 */
export function referenceDuCompte(simulateur) {
  const annee = simulateur.parametres.annee_bascule;
  const age = simulateur.ageReference.age(annee);
  return { naissance: annee - age, age, annee };
}

/** Python `int(round(x))` : l'arrondi au pair. */
function arrondi(x) {
  const r = Math.round(x);
  return Math.abs(x - Math.trunc(x)) === 0.5 && r % 2 !== 0 ? r - 1 : r;
}

/** Le diviseur du compte de qui est né à `naissance` et part à `age`, en mois entiers. */
export function diviseurA(simulateur, naissance, age, sexe = null, population = null) {
  const mois = arrondi((naissance + age) * 12.0);
  const annee = Math.floor(mois / 12);
  return simulateur.convertisseur.coefficient(age, annee, sexe, mois - 12 * annee + 1,
    population).diviseur;
}

/** Le report le plus long que `ageCible` cherche, en mois. */
export const REPORT_MAXIMAL = 600;

/**
 * Le critère de l'âge cible de l'ETK : le premier mois entier où
 * `coefficient × majoration(mois)` atteint un.
 */
export function ageCible(coefficient, majoration, ageMinimal, moisMinimum = 0) {
  const compense = (mois) => coefficient * majoration(mois) >= 1.0;
  let mois = 0;
  if (compense(mois)) {
    while (mois > moisMinimum && compense(mois - 1)) mois -= 1;
  } else {
    while (!compense(mois)) {
      mois += 1;
      if (mois > REPORT_MAXIMAL) {
        throw new Error(`aucun report de ${REPORT_MAXIMAL} mois au plus ne `
          + `compense le coefficient ${coefficient}`);
      }
    }
  }
  return ageMinimal + mois / 12.0;
}

/** L'âge le plus bas où l'on cherche un âge d'équilibre, en années. */
export const AGE_EQUILIBRE_MINIMAL = 40.0;

/**
 * L'âge d'équilibre du diviseur de la génération `generation`, née un 1er
 * janvier, sous la mortalité de `population`.
 */
export function ageDEquilibre(simulateur, generation, sexe = null, population = null) {
  const reference = referenceDuCompte(simulateur);
  const cible = diviseurA(simulateur, reference.naissance, reference.age, sexe, population);
  const diviseur = (mois) => diviseurA(simulateur, generation, reference.age + mois / 12.0,
    sexe, population);
  const aLaReference = diviseur(0);
  const minimum = arrondi((AGE_EQUILIBRE_MINIMAL - reference.age) * 12.0);
  const auMois = ageCible(cible / aLaReference, (mois) => aLaReference / diviseur(mois),
    reference.age, minimum);
  const mois = arrondi((auMois - reference.age) * 12.0);
  if (mois <= minimum) {
    throw new Error(`génération ${generation} : pas d'âge d'équilibre `
      + `au-dessus de ${AGE_EQUILIBRE_MINIMAL} ans`);
  }
  const avant = diviseur(mois - 1);
  const apres = diviseur(mois);
  return {
    generation,
    age: auMois - (cible - apres) / (avant - apres) / 12.0,
    au_mois: auMois,
    diviseur_reference: cible,
    diviseur_a_l_age_de_reference: aLaReference,
    coefficient: cible / aLaReference,
  };
}

/** Les années de retraite qu'espère qui part à `age` à la date `debut`. */
export function dureeEsperee(simulateur, age, debut, sexe = null, population = null) {
  const courbe = simulateur.mortalite.courbe(age, debut, sexe, true, population);
  return integraleSurvie(courbe, 0.0, courbe.length - 1);
}

/** La part de la vie passée en retraite de qui part à `age` à la date `debut`. */
export function partDeVie(simulateur, age, debut, sexe = null, cor = false, population = null) {
  if (cor) {
    const deces = ageDeDecesCor(simulateur.mortalite, Math.floor(debut - age + 1e-9));
    return (deces - age) / deces;
  }
  const duree = dureeEsperee(simulateur, age, debut, sexe, population);
  return duree / (age + duree);
}

/**
 * L'âge auquel qui est né à `naissance` passe en retraite la même part de sa
 * vie que la référence partie à l'âge de référence.
 */
export function ageDePartDeVieConstante(simulateur, naissance, sexe = null, cor = false,
  population = null) {
  const reference = referenceDuCompte(simulateur);
  if (cor) {
    const mortalite = simulateur.mortalite;
    return reference.age * (ageDeDecesCor(mortalite, Math.floor(naissance + 1e-9))
      / ageDeDecesCor(mortalite, Math.floor(reference.naissance + 1e-9)));
  }
  const cible = partDeVie(simulateur, reference.age, reference.annee, sexe, false, population);
  let bas = AGE_EQUILIBRE_MINIMAL;
  let haut = AGE_EQUILIBRE_MINIMAL + 50.0;
  while (haut - bas > 1e-9) {
    const milieu = 0.5 * (bas + haut);
    if (partDeVie(simulateur, milieu, naissance + milieu, sexe, false, population) > cible) {
      bas = milieu;
    } else {
      haut = milieu;
    }
  }
  return 0.5 * (bas + haut);
}
