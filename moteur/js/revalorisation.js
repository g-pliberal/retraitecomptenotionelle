/**
 * La pension d'aujourd'hui : ce que devient une pension une fois liquidée.
 *
 * Portage de `revalorisation.py`, dont le raisonnement est écrit en entier.
 * En deux phrases : le moteur calcule une pension au jour de la liquidation, et
 * un retraité touche ce qu'elle est devenue depuis, date d'effet après date
 * d'effet ; la page lui montrait la première, ramenée en euros d'aujourd'hui
 * par les prix, comme si elle les avait suivis. Chaque régime est revalorisé
 * ici selon son texte — la valeur du point pour les régimes en points, les
 * coefficients de l'article L. 161-23-1 pour le régime général et les régimes
 * alignés, la péréquation puis les décrets puis L. 161-23-1 pour la fonction
 * publique —, et les cinq systèmes notionnels selon la règle que la page Coût
 * leur prête, `RevalorisationServie`, déplacée ici depuis `cout.js`.
 *
 * Les dates sont des chaînes ISO « AAAA-MM-JJ » : leur ordre alphabétique est
 * l'ordre du calendrier, et c'est tout ce que le module leur demande.
 */

import { DateMois } from "./calendrier.js";
import { RevalorisationStock, SituationFoyer } from "./config.js";
import * as liquider from "./droit/liquider.js";
import { pensionsALEcretement, pensionsEtrangeresServies } from "./droit/etranger.js";
import { conditionDeResidence, foyerEtNet } from "./droit/foyer.js";
import { ageDeLAspa } from "./droit/invalidite.js";
import { Fiabilite, nomFiabilite } from "./serie.js";

/** Fin de la péréquation des pensions civiles et militaires. */
export const FIN_PEREQUATION = "2004-01-01";

/** Début de l'article L. 161-23-1 pour la fonction publique et les régimes spéciaux. */
export const DEBUT_REGLE_GENERALE_PUBLIC = "2009-01-01";

/** Dernier point d'indice servi par la péréquation. */
export const DERNIERE_ANNEE_PEREQUATION = 2003;

/** Le mois dont le montant total choisit la tranche de 2020. */
export const MOIS_DES_TRANCHES = "2019-12-31";

/** Âge de l'ASPA et de la garantie vieillesse. */
export const MINIMUM_VIEILLESSE_AGE = 65;

export const REGLE_POINT = "point";
export const REGLE_GENERALE = "regime_general";
export const REGLE_FONCTION_PUBLIQUE = "fonction_publique";
export const REGLE_REGIME_SPECIAL = "regime_special";
export const REGLE_PAR_DEFAUT = "par_defaut";

export const REGIMES_FONCTION_PUBLIQUE = new Set([
  "fonction_publique_etat", "pensions_civiles_1853", "cnracl", "fspoeie",
]);

export const REGIMES_REGLE_GENERALE = new Set([
  "regime_general", "avts", "assurances_sociales", "msa_salaries",
  "msa_non_salaries", "rsi", "cancava", "organic", "cssm_mayotte",
]);

/** Une date ISO, à partir de ses trois nombres. */
export function dateIso(annee, mois, jour) {
  return `${String(annee).padStart(4, "0")}-${String(mois).padStart(2, "0")}-`
    + String(jour).padStart(2, "0");
}

const plusGrande = (a, b) => (a > b ? a : b);
const plusPetite = (a, b) => (a < b ? a : b);

function ligneDuPaquet([dateEffet, coefficient, superieurA, auPlus, fiabilite]) {
  return {
    date_effet: dateEffet,
    coefficient,
    superieur_a: superieurA,
    au_plus: auPlus,
    fiabilite,
    par_tranche: superieurA !== null || auPlus !== null,
  };
}

function couvre(ligne, mensuel) {
  return (ligne.superieur_a === null || mensuel > ligne.superieur_a)
    && (ligne.au_plus === null || mensuel <= ligne.au_plus);
}

function trier(lignes) {
  return lignes.map(ligneDuPaquet).sort((a, b) => {
    if (a.date_effet !== b.date_effet) return a.date_effet < b.date_effet ? -1 : 1;
    return (a.superieur_a ?? 0) - (b.superieur_a ?? 0);
  });
}

/** Le coefficient cumulé d'une suite de revalorisations, et sa fiabilité. */
export function produit(revalorisations) {
  let coefficient = 1.0;
  let fiabilite = Fiabilite.CERTIFIEE;
  for (const revalorisation of revalorisations) {
    coefficient *= revalorisation.coefficient;
    fiabilite = Math.min(fiabilite, revalorisation.fiabilite);
  }
  return [coefficient, fiabilite];
}

/** Les coefficients qui ont revalorisé les pensions servies, date par date. */
export class RevalorisationsPensions {
  constructor(paquet) {
    const contenu = paquet.revalorisation_pensions ?? {};
    this.generales = trier(contenu.generales ?? []);
    this.fonction_publique = trier(contenu.fonction_publique ?? []);
  }

  /**
   * Celles qu'a reçues une pension prenant effet à `depuis`, jusqu'à `jusqua`
   * inclus. Voir `retenues` dans `revalorisation.py`.
   */
  static retenues(lignes, depuis, jusqua, inclureDepuis, mensuel2019) {
    const choisies = [];
    for (const ligne of lignes) {
      const effet = ligne.date_effet;
      if (effet > jusqua || effet < depuis || (effet === depuis && !inclureDepuis)) {
        continue;
      }
      if (ligne.par_tranche) {
        if (mensuel2019 === null || mensuel2019 === undefined) {
          throw new Error(
            `la revalorisation du ${effet} dépend du montant total de la retraite `
            + "du mois précédent, qui n'a pas été donné",
          );
        }
        if (!couvre(ligne, mensuel2019)) continue;
      }
      choisies.push(ligne);
    }
    return choisies;
  }

  /** Le coefficient de l'article L. 161-23-1 entre deux dates. */
  generale(depuis, jusqua, inclureDepuis, mensuel2019) {
    return produit(RevalorisationsPensions.retenues(
      this.generales, depuis, jusqua, inclureDepuis, mensuel2019,
    ));
  }
}

/**
 * Ce qui porte le dernier traitement d'une pension DIFFÉRÉE jusqu'à sa mise en
 * paiement, ou `null` si la série du point ne couvre pas l'année — portage de
 * `coefficient_traitement_differe`. L. 25 du code des pensions (article 26 du
 * décret n° 2003-1306, article 22 du décret n° 2004-1056) : le traitement est
 * revalorisé comme les pensions civiles de la radiation à la mise en paiement,
 * celle-ci comprise et celle-là non ; en 2020, le coefficient de L. 161-25.
 * `radiation` et `paiement` sont des dates ISO.
 */
export function coefficientTraitementDiffere(revalorisations, ratioPointIndice,
  perception, radiation, paiement) {
  const finPoint = radiation >= FIN_PEREQUATION
    ? Number(radiation.slice(0, 4))
    : Math.min(Number(paiement.slice(0, 4)), DERNIERE_ANNEE_PEREQUATION);
  const point = ratioPointIndice(perception, finPoint);
  if (point === null || point === undefined) {
    return null;
  }
  const [decrets] = produit(RevalorisationsPensions.retenues(
    revalorisations.fonction_publique, plusGrande(radiation, FIN_PEREQUATION),
    plusPetite(paiement, DEBUT_REGLE_GENERALE_PUBLIC), radiation < FIN_PEREQUATION, null,
  ));
  const [generale] = revalorisations.generale(
    plusGrande(radiation, DEBUT_REGLE_GENERALE_PUBLIC), paiement,
    radiation < DEBUT_REGLE_GENERALE_PUBLIC, 0.0,
  );
  return point * decrets * generale;
}

function derniereValeurPubliee(actuel, code) {
  let courant = code;
  for (let garde = 0; garde < actuel.catalogue.taille + 1; garde += 1) {
    const derniere = actuel.valeursPoint.derniereAnneeServie(courant);
    if (derniere === null) return null;
    const successeur = actuel.catalogue.contient(courant)
      ? actuel.catalogue.obtenir(courant).integre_dans
      : null;
    const reprise = successeur ? actuel.conversionsPoints.fusion(courant, successeur) : null;
    if (reprise === null) return derniere;
    courant = successeur;
  }
  return null;
}

function derniereAnneeRegime(regime) {
  if (regime.periodes.length === 0) return 2100;
  const annees = regime.periodes.map((p) => (p.fin === null ? 9999 : p.fin));
  return Math.min(Math.max(...annees), 2100);
}

/** La règle de chaque régime, appliquée d'une date à une autre. */
export class PensionServie {
  constructor(simulateur) {
    this.actuel = simulateur.scenarioActuel;
    this.catalogue = simulateur.catalogue;
    this.revalorisations = simulateur.revalorisations;
  }

  /**
   * La même règle, tirée du moteur du scénario 1 seul : ce qu'une liquidation
   * lit quand elle doit voir une pension déjà servie.
   */
  static duMoteur(moteur) {
    return new PensionServie({
      scenarioActuel: moteur, catalogue: moteur.catalogue,
      revalorisations: moteur.revalorisationsPensions,
    });
  }

  /** Coefficient nominal d'une pension de régime, de `depart` à `jusqua`. */
  coefficient(pension, anneeLiquidation, depart, jusqua, mensuel2019) {
    const code = pension.regime;
    const regime = this.catalogue.obtenir(code);
    const debutAnnee = dateIso(anneeLiquidation, 1, 1);
    if (pension.type_calcul === "points" || pension.type_calcul === "mixte") {
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnneeRegime(regime)));
      const bareme = (periode !== null ? periode.points_de : null) || code;
      const auDepart = liquider.valeurDuPoint(this.actuel, bareme, anneeLiquidation);
      const publiee = derniereValeurPubliee(this.actuel, bareme);
      if (auDepart !== null && auDepart[0] > 0 && publiee !== null) {
        const anneeFin = Number(jusqua.slice(0, 4));
        const ancre = Math.min(anneeFin, publiee);
        const aLAncre = liquider.valeurDuPoint(this.actuel, bareme, ancre);
        const [echelle, fiabiliteEchelle] = this.actuel.conversionsPoints.echelle(
          bareme, anneeLiquidation, ancre,
        );
        const [suite, fiabiliteSuite] = this.revalorisations.generale(
          dateIso(ancre, 12, 31), jusqua, false, mensuel2019,
        );
        let fiabilite = Math.min(auDepart[1], aLAncre[1], fiabiliteEchelle);
        if (ancre < anneeFin) {
          fiabilite = Math.min(fiabilite, fiabiliteSuite, Fiabilite.MOYENNE);
        }
        return [echelle * aLAncre[0] / auDepart[0] * suite, REGLE_POINT, fiabilite];
      }
    }
    if (REGIMES_FONCTION_PUBLIQUE.has(code)) {
      return this._fonctionPublique(anneeLiquidation, depart, jusqua, mensuel2019);
    }
    if (regime.famille === "special") {
      const [coefficient, fiabiliteSerie] = this.revalorisations.generale(
        depart, jusqua, true, mensuel2019,
      );
      const fiabilite = depart < DEBUT_REGLE_GENERALE_PUBLIC ? Fiabilite.ESTIMEE : fiabiliteSerie;
      return [coefficient, REGLE_REGIME_SPECIAL, fiabilite];
    }
    const [coefficient, fiabilite] = this.revalorisations.generale(
      debutAnnee, jusqua, false, mensuel2019,
    );
    if (REGIMES_REGLE_GENERALE.has(code)) {
      return [coefficient, REGLE_GENERALE, fiabilite];
    }
    return [coefficient, REGLE_PAR_DEFAUT, Math.min(fiabilite, Fiabilite.MOYENNE)];
  }

  _fonctionPublique(anneeLiquidation, depart, jusqua, mensuel2019) {
    let coefficient = 1.0;
    let fiabilite = Fiabilite.CERTIFIEE;
    if (depart < FIN_PEREQUATION) {
      const fin = Math.min(Number(jusqua.slice(0, 4)), DERNIERE_ANNEE_PEREQUATION);
      const ratio = this.actuel.minimumGaranti.ratioPointIndice(anneeLiquidation, fin);
      if (ratio !== null) coefficient *= ratio;
      fiabilite = Fiabilite.MOYENNE;
    }
    const [decrets, fiabiliteDecrets] = produit(RevalorisationsPensions.retenues(
      this.revalorisations.fonction_publique, plusGrande(depart, FIN_PEREQUATION),
      plusPetite(jusqua, DEBUT_REGLE_GENERALE_PUBLIC), true, null,
    ));
    const [generale, fiabiliteGenerale] = this.revalorisations.generale(
      plusGrande(depart, DEBUT_REGLE_GENERALE_PUBLIC), jusqua, true, mensuel2019,
    );
    return [coefficient * decrets * generale, REGLE_FONCTION_PUBLIQUE,
      Math.min(fiabilite, fiabiliteDecrets, fiabiliteGenerale)];
  }
}

/**
 * Ce que valent, au premier jour du mois `jusqua`, des pensions liquidées au
 * premier jour du mois `depart` (deux `DateMois`) : chacune menée par la règle
 * de son régime. C'est ce qu'un départ suivant voit servi (`droit/departs.js`) :
 * le minimum contributif s'écrête sur les pensions du mois de sa date d'effet
 * (R. 173-7). Voir `mener_au_mois` dans le Python.
 */
export function menerAuMois(moteur, pensions, depart, jusqua) {
  const servie = PensionServie.duMoteur(moteur);
  const debut = dateIso(depart.annee, depart.mois, 1);
  const fin = dateIso(jusqua.annee, jusqua.mois, 1);
  if (fin <= debut) {
    return pensions.map((pension) => pension.montant);
  }
  let mensuel2019 = null;
  if (debut <= "2020-01-01" && "2020-01-01" <= fin) {
    let somme = 0;
    for (const p of pensions) {
      somme += p.montant * (debut <= MOIS_DES_TRANCHES
        ? servie.coefficient(p, depart.annee, debut, MOIS_DES_TRANCHES, null)[0] : 0.0);
    }
    mensuel2019 = somme / 12.0;
  }
  return pensions.map((p) => p.montant
    * servie.coefficient(p, depart.annee, debut, fin, mensuel2019)[0]);
}

/** Le système 1 aujourd'hui : ce que le droit sert, régime par régime. */
export class ActuelAujourdhui {
  constructor(champs) {
    Object.assign(this, champs);
  }

  get pension_annuelle() {
    let total = 0;
    for (const r of this.regimes) {
      if (!r.hors_repartition) total += r.aujourd_hui;
    }
    return total + this.majoration_enfants * this.coefficient_majoration
      + this.minimum_vieillesse;
  }

  get pension_hors_repartition() {
    let total = 0;
    for (const r of this.regimes) {
      if (r.hors_repartition) total += r.aujourd_hui;
    }
    return total;
  }
}

/**
 * Ce que l'étape « faire vivre » écrit : les pensions du système 1 menées à
 * une échéance, dont l'année donne les euros de tous les montants. Son schéma :
 * `data/reference/etapes/faire_vivre.yaml`.
 */
export class Revalorisee {
  constructor(champs) {
    Object.assign(this, champs);
  }

  /** La revalorisation, telle que le schéma de l'étape la décrit. */
  donnees() {
    return {
      schema_version: 1,
      personne: this.personne,
      date: dateIso(this.annee, 12, 31),
      regimes: this.regimes.map((r) => ({
        regime: r.regime, coefficient: r.coefficient, regle: r.regle,
        fiabilite: nomFiabilite(r.fiabilite), revision: r.revision ?? 0.0,
      })),
      majoration: this.coefficient_majoration,
      mensuel_decembre_2019: this.mensuel_decembre_2019,
      fiabilite: nomFiabilite(this.fiabilite),
    };
  }
}

/**
 * L'étape « faire vivre » (docs/architecture.md, § 7.4) : les pensions du
 * système 1 menées jusqu'en `annee` — l'année courante par défaut. Rien n'est
 * recalculé de la carrière : seuls les montants de chaque régime sont
 * revalorisés, selon la règle de leur texte. Une revalorisation ne relance
 * jamais la liquidation. Quand les régimes liquident à des dates différentes
 * (`droit/departs.js`), chaque pension part de SA date d'effet et de son
 * montant à cette date ; celle qui n'est pas encore servie à l'échéance n'y
 * est pas.
 */
export function faireVivre(simulateur, carriere, resultat, annee = null) {
  const parametres = simulateur.parametres;
  const an = annee === null ? parametres.annee_courante : annee;
  const servie = new PensionServie(simulateur);
  const liquidation = carriere.anneeLiquidation;
  const depart = dateIso(liquidation, carriere.dateLiquidation.mois, 1);
  const fin = dateIso(an, 12, 31);
  const isoler = parametres.isoler_capitalisation;
  // Chaque pension, son année de liquidation, sa date d'effet et son montant
  // à cette date : ceux du départ, sauf pour une pension datée.
  const datee = (p) => (p.date_effet == null
    ? [p, liquidation, depart, p.montant]
    : [p, Number(p.date_effet.slice(0, 4)), p.date_effet, p.montant_a_l_effet]);
  const toutes = resultat.pensions_par_regime.map(datee);
  const aVenir = new Set(toutes.filter(([p, , debut]) => p.date_effet != null && debut > fin)
    .map(([p]) => p.regime));
  const datees = toutes.filter(([p]) => !aVenir.has(p.regime));
  const pensions = datees.map(([p]) => p);
  // Ce qui ramène le montant d'une pension datée, en euros du départ, à son
  // montant à sa date d'effet : la part de la majoration qu'elle porte se
  // ramène de même.
  const aLEffet = new Map(resultat.pensions_par_regime.map((p) => [p.regime,
    p.date_effet != null && p.montant ? p.montant_a_l_effet / p.montant : 1.0]));
  const horsRepartition = (p) => isoler
    && Boolean(simulateur.catalogue.obtenir(p.regime).hors_repartition);
  let majoration = 0;
  // La part de chaque régime dans la majoration pour enfants, plafond compris.
  const partsMajoration = [];
  for (const a of resultat.avantages_appliques) {
    if (a.code === "majoration_enfants") {
      majoration += a.montant;
      partsMajoration.push(...(a.par_regime ?? []));
    }
  }

  const coefficientMoyen = (coefficients) => {
    let masse = 0;
    let pondere = 0;
    pensions.forEach((p, rang) => {
      if (horsRepartition(p)) return;
      masse += p.montant;
    });
    if (masse <= 0) return 1.0;
    pensions.forEach((p, rang) => {
      if (horsRepartition(p)) return;
      pondere += p.montant * coefficients[rang];
    });
    return pondere / masse;
  };

  // Chaque part suit le régime qui la porte ; sans parts, la moyenne.
  const coefficientDeLaMajoration = (coefficients) => {
    let masse = 0;
    for (const [, part] of partsMajoration) masse += part;
    if (masse <= 0) return coefficientMoyen(coefficients);
    const parRegime = new Map();
    pensions.forEach((p, rang) => { parRegime.set(p.regime, coefficients[rang]); });
    for (const code of aVenir) parRegime.set(code, 0.0);
    let pondere = 0;
    for (const [code, part] of partsMajoration) {
      pondere += part * (aLEffet.get(code) ?? 1.0)
        * (parRegime.has(code) ? parRegime.get(code) : 1.0);
    }
    return pondere / masse;
  };

  // Une pension qui prend effet en janvier 2020 n'était pas servie en
  // décembre : le montant du mois précédent était nul.
  let mensuel2019 = null;
  const premier = datees.reduce((plusTot, [, , debut]) => (debut < plusTot ? debut : plusTot),
    datees.length > 0 ? datees[0][2] : depart);
  if (premier <= "2020-01-01" && "2020-01-01" <= fin) {
    const jusqu2019 = datees.map(([p, a, debut]) => (debut <= MOIS_DES_TRANCHES
      ? servie.coefficient(p, a, debut, MOIS_DES_TRANCHES, null)[0]
      : 0.0));
    let somme = 0;
    datees.forEach(([, , , montant], rang) => { somme += montant * jusqu2019[rang]; });
    mensuel2019 = (somme + majoration * coefficientDeLaMajoration(jusqu2019)) / 12.0;
  }

  const regimes = [];
  const coefficients = [];
  let fiabilite = Fiabilite.CERTIFIEE;
  for (const [pension, a, debut, montant] of datees) {
    const [coefficient, regle, fiabiliteRegime] = servie.coefficient(
      pension, a, debut, fin, mensuel2019,
    );
    coefficients.push(coefficient);
    fiabilite = Math.min(fiabilite, fiabiliteRegime);
    regimes.push({
      regime: pension.regime,
      au_depart: montant,
      coefficient,
      regle,
      fiabilite: fiabiliteRegime,
      hors_repartition: horsRepartition(pension),
      aujourd_hui: montant * coefficient,
      revision: 0.0,
    });
  }
  const coefficientMajoration = coefficientDeLaMajoration(coefficients);
  reviserLeMinimum(simulateur.scenarioActuel, carriere, resultat, regimes, an);

  return new Revalorisee({
    personne: carriere.personne,
    annee: an,
    regimes,
    majoration_enfants: majoration,
    coefficient_majoration: coefficientMajoration,
    mensuel_decembre_2019: mensuel2019,
    fiabilite,
  });
}

/**
 * La révision du minimum contributif quand une pension étrangère commence après
 * le départ (R. 173-8) : les pensions que l'écrêtement compte, commencées après
 * le mois du départ et au plus tard en décembre de `annee`, s'ajoutent à la
 * marge qui séparait les pensions du plafond, menée comme le minimum ; ce
 * qu'elles en passent retire au minimum, jamais plus que lui, chaque régime à
 * proportion du sien. Modifie `regimes` en place. Voir `reviser_le_minimum` du
 * Python.
 */
export function reviserLeMinimum(moteur, carriere, resultat, regimes, annee) {
  const ecrete = resultat.minimum_ecrete ?? null;
  if (ecrete === null || carriere.pensionsEtrangeres.length === 0) {
    return;
  }
  const nouvelles = pensionsALEcretement(moteur, carriere, carriere.dateLiquidation,
    new DateMois(annee, 12), annee);
  const coefficients = new Map(regimes.map((r) => [r.regime, r.coefficient]));
  const parts = ecrete.par_regime.filter(([code]) => coefficients.has(code))
    .map(([code, part]) => [code, part, coefficients.get(code)]);
  let servi = 0;
  let somme = 0;
  for (const [, part, coefficient] of parts) {
    servi += part * coefficient;
    somme += part;
  }
  if (nouvelles <= 0 || servi <= 0) {
    return;
  }
  // Le coefficient du minimum, celui de ses régimes à proportion de leur part :
  // le plafond et la marge le suivent.
  const mene = servi / somme;
  const revise = Math.max(0.0, Math.min(ecrete.avant_ecretement * mene,
    ecrete.marge * mene - nouvelles));
  const baisse = Math.max(0.0, servi - revise);
  if (baisse <= 0) {
    return;
  }
  const retraits = new Map(parts.map(([code, part, coefficient]) => [
    code, part * coefficient / servi * baisse]));
  for (const r of regimes) {
    r.revision = retraits.get(r.regime) ?? 0.0;
    r.aujourd_hui = r.au_depart * r.coefficient - r.revision;
  }
}

/**
 * L'étape « foyer et net » à l'échéance de `vivante` : l'ASPA d'aujourd'hui,
 * comme à la liquidation, différentielle, sur TOUTES les pensions — le RAFP
 * compris —, et à 65 ans révolus dans l'année, à l'âge de l'inapte pour lui
 * (`ageDeLAspa`). Qui est parti à 62 ans l'a peut-être gagnée depuis.
 */
export function foyerALEcheance(simulateur, carriere, vivante) {
  let ressources = 0;
  for (const r of vivante.regimes) ressources += r.aujourd_hui;
  ressources += vivante.majoration_enfants * vivante.coefficient_majoration;
  return foyerEtNet(
    simulateur.scenarioActuel, carriere.personne, dateIso(vivante.annee, 12, 31),
    vivante.annee, ressources,
    vivante.annee >= carriere.annee_naissance + ageDeLAspa(simulateur.scenarioActuel, carriere),
    null, carriere,
  );
}

/**
 * Le système 1 à l'échéance : les pensions que « faire vivre » a menées
 * jusque-là, et l'ASPA que « foyer et net » y ajoute.
 */
export function aujourdHui(vivante, foyer, resultat) {
  let aspaAuDepart = 0;
  for (const a of resultat.avantages_appliques) {
    if (a.code === "minimum_vieillesse") aspaAuDepart += a.montant;
  }
  return new ActuelAujourdhui({
    annee: vivante.annee,
    regimes: vivante.regimes,
    majoration_enfants: vivante.majoration_enfants,
    coefficient_majoration: vivante.coefficient_majoration,
    minimum_vieillesse_au_depart: aspaAuDepart,
    minimum_vieillesse: foyer.minimumVieillesse,
    mensuel_decembre_2019: vivante.mensuel_decembre_2019,
    fiabilite: Math.min(vivante.fiabilite, foyer.fiabilite),
  });
}

/**
 * Le système 1 servi en `annee` — l'année courante par défaut : faire vivre,
 * puis foyer et net, comme l'échéancier les applique.
 */
export function actuelAujourdhui(simulateur, carriere, resultat, annee = null) {
  const vivante = faireVivre(simulateur, carriere, resultat, annee);
  return aujourdHui(vivante, foyerALEcheance(simulateur, carriere, vivante), resultat);
}

/** Ce qu'un retraité touche aujourd'hui, dans chacun des six systèmes. */
export class PensionAujourdhui {
  constructor(champs) {
    Object.assign(this, champs);
  }

  pension(scenario) {
    return scenario === "actuel" ? this.actuel.pension_annuelle : this.notionnels[scenario];
  }

  pensionTotale(scenario) {
    if (scenario === "notionnel_liberal") {
      return this.notionnels[scenario] + this.rente_capitalisee;
    }
    return this.pension(scenario);
  }
}

/**
 * Les six systèmes servis l'année courante, pour qui a déjà liquidé.
 * `actuelServi` est le système 1 à l'échéance, quand l'échéancier l'a déjà mené
 * jusque-là : il n'est pas refait.
 */
export function pensionAujourdhui(simulateur, comparaison, actuelServi = null) {
  const parametres = simulateur.parametres;
  const carriere = comparaison.carriere;
  const annee = parametres.annee_courante;
  const liquidation = carriere.anneeLiquidation;
  const bascule = parametres.annee_bascule;
  const macro = simulateur.macro;
  const revalorisation = simulateur.revalorisationServie;
  const versAujourdhui = macro.coefficientPrix(liquidation, annee);

  const actuel = actuelServi !== null
    ? actuelServi : actuelAujourdhui(simulateur, carriere, comparaison.actuel, annee);
  const coefficientActuel = comparaison.actuel.pension_annuelle > 0
    ? actuel.pension_annuelle / comparaison.actuel.pension_annuelle
    : 1.0;

  const notionnels = {};
  const coefficients = {};
  for (const [cle, calcul] of Object.entries(simulateur.calculs)) {
    if (calcul.garantie) {
      continue; // la garantie se calcule aujourd'hui : plus bas
    }
    const pension = comparaison[cle].pension_annuelle;
    // Un univers qui porte une transition ne change rien avant elle.
    const prospectif = calcul.prospectif;
    if (prospectif && liquidation <= bascule) {
      if (annee <= bascule) {
        notionnels[cle] = actuel.pension_annuelle;
        coefficients[cle] = coefficientActuel / versAujourdhui;
        continue;
      }
      const jusquBascule = actuelAujourdhui(
        simulateur, carriere, comparaison.actuel, bascule,
      ).pension_annuelle;
      const reel = parametres.revalorisation_stock === RevalorisationStock.REINDEXE
        ? revalorisation.coefficient(bascule, annee)
        : 1.0;
      notionnels[cle] = jusquBascule * macro.coefficientPrix(bascule, annee) * reel;
      coefficients[cle] = pension > 0 ? notionnels[cle] / pension / versAujourdhui : 1.0;
      continue;
    }
    const reel = revalorisation.coefficientStock(liquidation, annee, prospectif);
    notionnels[cle] = pension * versAujourdhui * reel;
    coefficients[cle] = reel;
  }

  const liberal = comparaison.notionnel_liberal;
  const garantie = liberal.garantie_vieillesse;
  const contributive = garantie !== null && garantie !== undefined
    ? garantie.pension_contributive
    : liberal.pension_annuelle;
  const reel = revalorisation.coefficientStock(liquidation, annee, false);
  const contributiveAujourdhui = contributive * versAujourdhui * reel;
  // La rente du pilier est nominale et constante : elle vaut aujourd'hui, en
  // euros d'aujourd'hui, ce qu'elle valait à la liquidation. Voir le Python.
  const rente = liberal.rente_capitalisation_obligatoire;
  const volontaire = liberal.rente_capitalisation_volontaire;
  let plancher = parametres.garantie_vieillesse_mensuelle;
  if (parametres.situation_foyer === SituationFoyer.SEUL) {
    plancher += parametres.allocation_isolement_mensuelle;
  }
  plancher *= 12.0 * macro.coefficientPrix(parametres.annee_euros_garantie_vieillesse, annee);
  const ouverte = annee >= carriere.annee_naissance + MINIMUM_VIEILLESSE_AGE;
  // Comme l'ASPA qu'elle remplace, elle ne se sert qu'à qui réside en France,
  // et compte ce qu'un autre État sert.
  const etrangeres = pensionsEtrangeresServies(macro, carriere, new DateMois(annee, 12));
  const resident = conditionDeResidence(simulateur.scenarioActuel, carriere.residence,
    dateIso(annee, 12, 31), carriere.moisEnFrance);
  const complement = ouverte && resident
    ? Math.max(0.0, plancher - contributiveAujourdhui - rente - etrangeres)
    : 0.0;
  notionnels.notionnel_liberal = contributiveAujourdhui + complement;
  coefficients.notionnel_liberal = reel;

  return new PensionAujourdhui({
    annee,
    actuel,
    notionnels,
    coefficients_notionnels: coefficients,
    garantie_vieillesse: complement,
    rente_capitalisee: rente,
    rente_capitalisee_volontaire: volontaire,
    garantie_ouverte: ouverte,
    plancher_garantie: plancher,
    ressources_garantie: contributiveAujourdhui + rente + etrangeres,
    garantie_residence: resident,
  });
}

/**
 * Ce que devient une pension DÉJÀ LIQUIDÉE dans un système notionnel, année
 * après année.
 *
 * Portage de `RevalorisationServie` dans `revalorisation.py`, dont le
 * raisonnement est écrit en entier. En deux phrases : un système notionnel a
 * DEUX règles d'indexation — le compte pendant la carrière, la pension une
 * fois servie —, et le dépôt n'en portait qu'une, les masses figeant la
 * pension en euros constants pour toute la retraite. C'était une indexation
 * sur les prix qui ne disait pas son nom, correcte pour le scénario 1 où c'est
 * la loi, fausse pour les cinq autres, dont le diviseur de conversion suppose
 * déjà que la rente suit le taux qui a fait grossir le compte.
 */
export class RevalorisationServie {
  constructor(simulateur, premiereAnnee, derniereAnnee) {
    const macro = simulateur.macro;
    const indexation = simulateur.indexation;
    // Les prix, pour ce qui n'est revalorisé sur RIEN : `coefficientNominal`.
    this._macro = macro;
    // L'année à partir de laquelle une réforme PROSPECTIVE revalorise ce
    // qu'elle sert : voir CLES_PROSPECTIVES dans `cout.js`.
    this.anneeBascule = simulateur.parametres.annee_bascule;
    // Le stock à la bascule garde-t-il les prix ? Voir `coefficientStock`.
    this.stockSurLesPrix = simulateur.parametres.revalorisation_stock === "prix";
    this.premiereAnnee = premiereAnnee;
    this.derniereAnnee = Math.max(derniereAnnee, premiereAnnee);
    // Le rendement que le diviseur a servi d'avance : la pension servie se
    // revalorise au taux du compte divisé par 1 + ν, comme en Suède. Voir le
    // Python ; au défaut, ν = 0, rien ne change.
    const prefinancement = 1 + simulateur.parametres.taux_anticipe_conversion;
    let index = 1;
    this._index = new Map([[this.premiereAnnee, index]]);
    for (let annee = this.premiereAnnee + 1; annee <= this.derniereAnnee; annee += 1) {
      // Le taux d'indexation est NOMINAL, les masses sont en euros constants :
      // on le déflate année par année, et non en bloc.
      index *= (1 + indexation.taux(annee).taux) / prefinancement
        * macro.coefficientPrix(annee, annee - 1);
      this._index.set(annee, index);
    }
  }

  _valeur(annee) {
    const borne = Math.min(Math.max(annee, this.premiereAnnee), this.derniereAnnee);
    return this._index.get(borne);
  }

  /**
   * Ce que vaut en `annee`, en euros constants, un euro de pension liquidé en
   * `anneeLiquidation`. Vaut exactement 1 l'année de la liquidation et avant.
   */
  coefficient(anneeLiquidation, annee) {
    if (annee <= anneeLiquidation) return 1;
    const depart = this._valeur(anneeLiquidation);
    return depart ? this._valeur(annee) / depart : 1;
  }

  /**
   * Ce que vaut en `annee`, en euros constants, un euro de rente NOMINALE et
   * constante liquidé en `anneeLiquidation` : la rente du pilier capitalisé,
   * que rien ne revalorise et que les prix seuls déprécient. Voir le Python.
   */
  coefficientNominal(anneeLiquidation, annee) {
    if (annee <= anneeLiquidation) return 1;
    return this._macro.coefficientPrix(annee, anneeLiquidation);
  }

  /**
   * Le même coefficient, avec la règle du STOCK à la bascule — portage de
   * `coefficient_stock`. Une pension liquidée à compter de la bascule suit la
   * règle du compte depuis sa liquidation. Liquidée avant : sous `prix`, elle
   * garde les prix à compter de la bascule (1 depuis toujours pour une réforme
   * prospective, coefficient gelé à la bascule pour une rétroactive) ; sous
   * `reindexe`, la prospective la prend à sa règle le jour de la bascule, la
   * rétroactive l'a toujours revalorisée sur la sienne.
   */
  coefficientStock(anneeLiquidation, annee, prospectif) {
    const bascule = this.anneeBascule;
    if (anneeLiquidation >= bascule) return this.coefficient(anneeLiquidation, annee);
    if (this.stockSurLesPrix) {
      if (prospectif) return 1;
      return this.coefficient(anneeLiquidation, Math.min(annee, bascule));
    }
    if (prospectif) return this.coefficient(bascule, annee);
    return this.coefficient(anneeLiquidation, annee);
  }
}
