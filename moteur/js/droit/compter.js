/**
 * Compter les durées (docs/architecture.md, § 7.2).
 *
 * Jumeau de `src/retraite_notionnelle/droit/compter.py`, fonction pour
 * fonction : les trimestres de chaque compte — l'assurance, périodes
 * assimilées comprises ; les services, qui proratisent la pension de la
 * fonction publique ; la durée cotisée —, régime par régime et année par
 * année, et les trimestres des enfants, dans le régime que la priorité entre
 * régimes désigne (R. 173-15) : `majorationPourEnfants`. Ce que l'étape écrit,
 * `Durees`, suit son schéma, `data/reference/etapes/compter_les_durees.yaml`.
 */

import { DateMois } from "../calendrier.js";
import * as chrono from "../chronologie.js";
import { fiabiliteDepuisTexte, nomFiabilite, Fiabilite } from "../serie.js";
import { derniereAnnee, ligneCotisee } from "./commun.js";
import * as coordonner from "./coordonner.js";
import { compterLesPeriodes, familleDesRegimes } from "./etranger.js";

/**
 * La version du schéma de l'étape : la deuxième compte les trimestres des
 * enfants enfant par enfant, chacun dans son régime ; la troisième, les
 * trimestres que les périodes hors de France apportent ; la quatrième, ceux
 * que les emplois classés ajoutent.
 */
export const SCHEMA_VERSION = 4;

/** Les trois comptes, dans l'ordre où l'étape les écrit. */
export const COMPTES = ["assurance", "services", "cotises"];

/**
 * Le seul dispositif pour enfants qu'un régime EN POINTS puisse porter : une
 * majoration de durée d'assurance ne touche que la durée, qu'il oppose aussi ;
 * une bonification entre aux services, qu'il n'a pas.
 */
const MAJORATION_DE_DUREE = "mda";

/** Le régime à qui R. 173-15 donne la priorité parmi les régimes alignés. */
const REGIME_GENERAL = "regime_general";

/**
 * Les conditions qu'une version de la bonification ou de la majoration de la
 * fonction publique pose à l'enfant (`contenu.parametres.condition` de la fiche
 * `enfants_fonction_publique`). Voir `CONDITIONS` du Python.
 */
export const CONDITIONS = Object.freeze([
  "tout_enfant", "ne_en_service", "ne_avant_radiation", "accouchement_apres_recrutement",
]);

/**
 * Les fiches des bonifications et des majorations que l'emploi CLASSÉ ouvre
 * dans le régime qui le pensionne, lues par `FichesDatees` à la date d'effet.
 * Voir `FICHES_DES_EMPLOIS` du Python.
 */
export const FICHES_DES_EMPLOIS = Object.freeze(["bonification_cinquieme_police_penitentiaire"]);

/**
 * Les conditions qu'une version de ces fiches pose à la carrière : la durée de
 * services classés qui ouvre l'âge anticipé ou minoré à la génération, ou la
 * radiation pour invalidité. Voir `CONDITIONS_DES_EMPLOIS` du Python.
 */
export const CONDITIONS_DES_EMPLOIS = Object.freeze(["duree_de_l_age_minore"]);

/**
 * Ce que l'emploi classé ajoute dans le régime qui le pensionne : des services
 * liquidés, sous le pourcentage maximum sauf `auDelaDuMaximum` ; de la durée
 * tous régimes, que la surcote du fonctionnaire ne lit pas (L. 14, III) ; une
 * majoration de la seule durée que ce régime oppose à sa décote. Voir
 * `TrimestresEmploi` du Python.
 */
export class TrimestresEmploi {
  constructor({ regime, fiche, version, texte, services, duree, majoration,
    auDelaDuMaximum, fiabilite }) {
    this.regime = regime;
    this.fiche = fiche;
    this.version = version;
    this.texte = texte;
    this.services = services;
    this.duree = duree;
    this.majoration = majoration;
    this.auDelaDuMaximum = auDelaDuMaximum;
    this.fiabilite = fiabilite;
  }
}

/**
 * Les trimestres dus au titre des enfants, enfant par enfant : chacun a son
 * régime, que la priorité entre régimes désigne pour lui. Voir
 * `MajorationEnfants` du Python.
 */
export class MajorationEnfants {
  constructor(enfants) {
    /** Les enfants qui ouvrent un droit, dans l'ordre de leurs filiations. */
    this.enfants = enfants;
  }

  /** Trimestres accordés au total, tous enfants confondus. */
  get trimestres() {
    return this.enfants.reduce((somme, enfant) => somme + enfant.trimestres, 0);
  }

  /** Ceux d'entre eux qui entrent aux services, tous enfants confondus. */
  get services() {
    return this.enfants.reduce((somme, enfant) => somme + enfant.services, 0);
  }

  /** La fiabilité la plus basse des enfants. */
  get fiabilite() {
    return Math.min(...this.enfants.map((enfant) => enfant.fiabilite));
  }

  /**
   * Les trimestres et les services que porte chaque régime, `[trimestres,
   * services]`, dans l'ordre de son premier enfant.
   */
  parRegime() {
    const sommes = new Map();
    for (const enfant of this.enfants) {
      const [trimestres, services] = sommes.get(enfant.regime) ?? [0, 0];
      sommes.set(enfant.regime, [trimestres + enfant.trimestres, services + enfant.services]);
    }
    return sommes;
  }

  /** Les régimes qui portent des trimestres d'enfants. */
  get regimes() {
    return [...this.parRegime().keys()];
  }

  /** Les dispositifs qui les accordent, dans l'ordre des enfants. */
  get dispositifs() {
    return [...new Set(this.enfants.map((enfant) => enfant.dispositif))];
  }
}

/**
 * Ce que l'étape écrit. Son schéma :
 * `data/reference/etapes/compter_les_durees.yaml`. Deux activités d'une même
 * année s'additionnent dans `parAnnee` ; le plafond de l'année, ses
 * trimestres civils, s'applique quand on les lit (`cumulPlafonne`).
 */
export class Durees {
  constructor({ carriere, parAnnee, horsAnnee, enfants, trimestres, trimestresParRegime,
    bonificationsParRegime, etranger = null, emplois = [] }) {
    this.carriere = carriere;
    /** Par compte, par régime et par année, les trimestres crédités. */
    this.parAnnee = parAnnee;
    /** Ce qui ne tient à aucune année — les trimestres des enfants. */
    this.horsAnnee = horsAnnee;
    /** Les trimestres dus au titre des enfants, et le régime qui les porte. */
    this.enfants = enfants;
    /**
     * La durée d'assurance tous régimes, enfants et bonifications des emplois
     * classés compris.
     */
    this.trimestres = trimestres;
    /** La durée d'assurance de chaque régime, plafonnée année par année. */
    this.trimestresParRegime = trimestresParRegime;
    /** Les BONIFICATIONS, à part des services (`taux_maximum_bonifie`). */
    this.bonificationsParRegime = bonificationsParRegime;
    /**
     * Les trimestres que les périodes hors de France apportent, par famille de
     * régimes : hors de `trimestres` et de la durée de chaque régime ;
     * `pourLeTaux` les y ajoute.
     */
    this.etranger = etranger;
    /**
     * Ce que les emplois classés ajoutent, régime par régime : leur durée est
     * dans `trimestres` ; leurs services et leurs majorations, la liquidation
     * du régime qui les sert les y lit.
     */
    this.emplois = emplois;
  }

  /**
   * Les trimestres que les emplois classés ajoutent aux services liquidés de
   * ces régimes, sous le pourcentage maximum.
   */
  servicesDesEmplois(membres) {
    return this.emplois.filter((e) => membres.includes(e.regime))
      .reduce((somme, e) => somme + e.services, 0);
  }

  /**
   * Les trimestres que les emplois classés ajoutent à la seule durée que ces
   * régimes opposent à leur décote (L. 14, I).
   */
  majorationsDesEmplois(membres) {
    return this.emplois.filter((e) => membres.includes(e.regime))
      .reduce((somme, e) => somme + e.majoration, 0);
  }

  /**
   * Ce que `trimestres` doit aux emplois classés, et que la surcote du
   * fonctionnaire ne lit pas (L. 14, III).
   */
  get dureeHorsSurcote() {
    return this.emplois.reduce((somme, e) => somme + e.duree, 0);
  }

  /**
   * Ceux de leurs trimestres de services qui portent le pourcentage au-delà du
   * maximum, comme les bonifications de L. 12.
   */
  bonificationsDesEmplois(membres) {
    return this.emplois.filter((e) => membres.includes(e.regime) && e.auDelaDuMaximum)
      .reduce((somme, e) => somme + e.services, 0);
  }

  /**
   * La durée d'assurance tous régimes que le taux d'un régime de cette famille
   * lit : celle de la carrière, enfants compris, et les trimestres étrangers que
   * la famille retient — sans ceux qu'un accord compare, pour la pension
   * nationale. Voir `pour_le_taux` du Python.
   */
  pourLeTaux(famille, nationale = false) {
    if (this.etranger === null || famille === null) {
      return this.trimestres;
    }
    return this.trimestres + this.etranger.trimestres(famille, nationale);
  }

  /**
   * Les trimestres étrangers que retient la famille des régimes de la
   * carrière : ceux que le résultat ajoute à sa durée tous régimes.
   */
  get trimestresEtrangers() {
    return this.etranger === null ? 0 : this.etranger.trimestres(this.etranger.famille);
  }

  /**
   * Les trimestres d'un compte, pour un régime ou un groupe de régimes
   * liquidés ensemble : sommés ANNÉE PAR ANNÉE, sans dépasser les trimestres
   * civils de chaque année, plus ce qui ne tient à aucune. `annees` ne garde
   * que les années qu'il accepte, et rien de ce qui ne tient à aucune.
   */
  cumulPlafonne(table, membres, annees = null) {
    const sommes = new Map();
    let total = 0;
    for (const membre of membres) {
      for (const [annee, trimestres] of this.parAnnee[table].get(membre) ?? []) {
        if (annees === null || annees(annee)) {
          sommes.set(annee, (sommes.get(annee) ?? 0) + trimestres);
        }
      }
      if (annees === null) {
        total += this.horsAnnee[table].get(membre) ?? 0;
      }
    }
    for (const [annee, somme] of sommes) {
      total += Math.min(somme, this.carriere.plafondTrimestres(annee));
    }
    return total;
  }

  /** Les durées, telles que leur schéma les décrit. */
  donnees() {
    const comptes = [];
    for (const compte of COMPTES) {
      for (const [regime, annees] of this.parAnnee[compte]) {
        for (const [annee, trimestres] of annees) {
          comptes.push({ compte, regime, annee, trimestres });
        }
      }
    }
    const enfants = this.enfants;
    return {
      schema_version: SCHEMA_VERSION,
      personne: this.carriere.personne,
      comptes,
      enfants: enfants === null ? null : {
        trimestres: enfants.trimestres,
        services: enfants.services,
        fiabilite: nomFiabilite(enfants.fiabilite),
        par_enfant: enfants.enfants.map((e) => ({
          enfant: e.enfant, naissance: e.naissance, regime: e.regime,
          dispositif: e.dispositif, fiche: e.fiche, version: e.version,
          trimestres: e.trimestres, services: e.services,
          fiabilite: nomFiabilite(e.fiabilite),
        })),
      },
      trimestres: this.trimestres,
      etranger: this.etranger === null ? null : this.etranger.donnees(),
      emplois: this.emplois.map((e) => ({
        regime: e.regime, fiche: e.fiche, version: e.version,
        services: e.services, duree: e.duree, majoration: e.majoration,
        au_dela_du_maximum: e.auDelaDuMaximum,
        fiabilite: nomFiabilite(e.fiabilite),
      })),
    };
  }
}

/**
 * L'étape : les trimestres de chaque compte, puis ceux des enfants.
 * `avantagesNonContributifs` à faux retire ces derniers. Voir `compter` dans
 * le Python.
 */
export function compter(moteur, coordination, avantagesNonContributifs = true) {
  const carriere = coordination.carriere;
  const anneeLiquidation = carriere.anneeLiquidation;
  let trimestres = carriere.trimestresActuels;
  // Ce qui reste du budget de services que L. 9 ouvre dans une limite — trois
  // ans par enfant pour le congé parental. Il se tient sur toute la carrière,
  // et non année par année.
  const budgetServicesPlafonnes = new Map();
  // Les trois comptes, ANNÉE PAR ANNÉE. Deux activités cumulées peuvent
  // verser au même régime, ou à deux régimes liquidés ensemble : leurs
  // trimestres s'y additionnent sans dépasser les trimestres civils de
  // l'année. Une année d'une seule activité n'est pas touchée.
  const parAnnee = { assurance: new Map(), services: new Map(), cotises: new Map() };
  // Ce qui ne tient à aucune année — la majoration pour enfants — et
  // s'ajoute donc hors plafond annuel.
  const horsAnnee = { assurance: new Map(), services: new Map(), cotises: new Map() };
  const crediterTrimestres = (table, code, annee, nombre) => {
    if (!parAnnee[table].has(code)) {
      parAnnee[table].set(code, new Map());
    }
    const annees = parAnnee[table].get(code);
    annees.set(annee, (annees.get(annee) ?? 0) + nombre);
  };
  carriere.lignes.forEach((ligne, i) => {
    const retenusLigne = carriere.trimestresRetenus(ligne);
    if (retenusLigne <= 0) {
      return;
    }
    let servicesLigne = ligne.services_fonction_publique
      ? servicesATempsPartiel(retenusLigne, ligne.quotite) : 0;
    const plafond = ligne.services_plafond_trimestres_par_enfant;
    if (servicesLigne > 0 && plafond > 0) {
      const restant = budgetServicesPlafonnes.get(plafond)
        ?? plafond * carriere.nombre_enfants;
      servicesLigne = Math.min(servicesLigne, restant);
      budgetServicesPlafonnes.set(plafond, restant - servicesLigne);
    }
    // Une année que tous ses régimes valident sans cotisation — l'activité
    // cultuelle d'avant 1979 — entre dans la durée, pas parmi les trimestres
    // cotisés (`ligneCotisee`).
    const cotisee = ligneCotisee(moteur, carriere, ligne);
    for (const code of coordination.regimes[i]) {
      if (!moteur.catalogue.contient(code)) {
        continue;
      }
      crediterTrimestres("assurance", code, ligne.annee, retenusLigne);
      if (servicesLigne > 0) {
        crediterTrimestres("services", code, ligne.annee, servicesLigne);
      }
      if (cotisee) {
        crediterTrimestres("cotises", code, ligne.annee, retenusLigne);
      }
    }
  });
  const provisoire = new Durees({
    carriere, parAnnee, horsAnnee, enfants: null, trimestres,
    trimestresParRegime: new Map(), bonificationsParRegime: new Map(),
  });
  // Durée d'assurance validée dans chaque régime, PÉRIODES ASSIMILÉES
  // COMPRISES : le coefficient de proratisation porte sur la durée
  // d'assurance, pas sur les seules années cotisées.
  const trimestresParRegime = new Map();
  for (const code of parAnnee.assurance.keys()) {
    trimestresParRegime.set(code, provisoire.cumulPlafonne("assurance", [code]));
  }
  // Les trimestres accordés au titre des enfants ne flottent pas au-dessus
  // des régimes : le droit les attribue DANS un régime, et ils comptent donc
  // aussi dans sa proratisation. Pour chaque enfant, UN SEUL régime les
  // accorde, celui que désigne R. 173-15 : voir `majorationPourEnfants`.
  const majorationEnfants = avantagesNonContributifs
    ? majorationPourEnfants(moteur, carriere, trimestresParRegime, anneeLiquidation)
    : null;
  const bonificationsParRegime = new Map();
  if (majorationEnfants !== null) {
    // LA DURÉE ET LES SERVICES NE SONT PAS LA MÊME CASE, et la majoration se
    // range dans les deux : tout ce qui est accordé joue sur la durée
    // d'assurance, tous régimes et dans le régime ; la seule part `services`
    // entre aux services, qui proratisent la pension de la fonction publique.
    trimestres += majorationEnfants.trimestres;
    for (const [regime, [accordes, services]] of majorationEnfants.parRegime()) {
      bonificationsParRegime.set(regime, services);
      trimestresParRegime.set(regime, trimestresParRegime.get(regime) + accordes);
      horsAnnee.assurance.set(regime, accordes);
      horsAnnee.services.set(regime, services);
    }
  }
  // Les périodes hors de France comptent pour le taux, chacune au titre que la
  // coordination lui a donné, sans dépasser quatre trimestres par année avec
  // ceux de la carrière : jamais dans la durée d'un régime.
  const etranger = coordination.etranger.length > 0
    ? compterLesPeriodes(carriere, coordination.etranger, carriere.trimestresActuels,
      familleDesRegimes(moteur, parAnnee.assurance.keys()))
    : null;
  // Ce que les emplois classés ajoutent : leur bonification à la durée tous
  // régimes, comme les services et bonifications admissibles en liquidation
  // (L. 14, I), hors de toute année ; le reste, la liquidation du régime qui
  // les sert l'y lit.
  const emplois = avantagesNonContributifs
    ? trimestresDesEmplois(moteur, carriere, anneeLiquidation)
    : [];
  trimestres += emplois.reduce((somme, emploi) => somme + emploi.duree, 0);
  return new Durees({
    carriere, parAnnee, horsAnnee, enfants: majorationEnfants, trimestres,
    trimestresParRegime, bonificationsParRegime, etranger, emplois,
  });
}

/**
 * Ce que les emplois classés de la carrière ajoutent, une fiche après l'autre
 * (`FICHES_DES_EMPLOIS`), chacune lue à la date d'effet de la pension. Voir
 * `trimestres_des_emplois` du Python.
 */
export function trimestresDesEmplois(moteur, carriere, anneeLiquidation) {
  const mois = carriere.age_liquidation !== null ? carriere.dateLiquidation.mois : 1;
  const dateEffet = `${String(anneeLiquidation).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`;
  const emplois = [];
  for (const nom of FICHES_DES_EMPLOIS) {
    const version = moteur.fichesDatees.version(nom, dateEffet);
    if (version === null || !version.parametres.existe) {
      continue;
    }
    const emploi = bonificationDEmploi(moteur, carriere, nom, version);
    if (emploi !== null) {
      emplois.push(emploi);
    }
  }
  return emplois;
}

/**
 * La bonification d'un emploi classé, ou null s'il n'en ouvre pas : une
 * fraction du temps servi dans les statuts qui l'ouvrent, sous son plafond,
 * diminuée des services accomplis au-delà de l'âge qui la réduit, comptés à
 * l'année, arrondie au trimestre, un demi-trimestre et plus comptant pour un.
 * La condition, que la version nomme, et qu'une radiation pour invalidité
 * dispense de remplir. Voir `bonification_d_emploi` du Python.
 */
export function bonificationDEmploi(moteur, carriere, fiche, version) {
  const parametres = version.parametres;
  const statuts = [...parametres.statuts];
  const regime = parametres.regime;
  if (!moteur.catalogue.contient(regime)
      || !coordonner.regimesRoutes(moteur, statuts).has(regime)) {
    return null;
  }
  const borne = coordonner.borneCarriere(carriere);
  const servies = carriere.dureeDeService(statuts, borne);
  if (servies <= 0) {
    return null;
  }
  const condition = parametres.condition;
  if (!CONDITIONS_DES_EMPLOIS.includes(condition)) {
    throw new Error(`${fiche}.${version.id} : condition inconnue, ${JSON.stringify(condition)}`);
  }
  let fiabilite = fiabiliteDepuisTexte(parametres.fiabilite);
  if (carriere.radiationPourInvalidite === null) {
    const derogation = moteur.agesCategorieActive.derogation(
      parametres.classement, carriere.generation);
    if (derogation === null || servies + 1e-9 < derogation.servicesRequis) {
      return null;
    }
    fiabilite = Math.min(fiabilite, derogation.fiabilite);
  }
  let auDela = 0;
  if (parametres.age_de_reduction !== null && parametres.age_de_reduction !== undefined) {
    const annee = carriere.annee_naissance + Math.trunc(parametres.age_de_reduction);
    const avant = carriere.dureeDeService(statuts, borne === null ? annee : Math.min(annee, borne));
    auDela = Math.max(0, servies - avant);
  }
  const annees = Math.min(servies * Number(parametres.fraction),
    Math.trunc(parametres.plafond_trimestres) / 4) - auDela;
  const trimestres = annees > 0 ? Math.trunc(annees * 4 + 0.5) : 0;
  if (trimestres <= 0) {
    return null;
  }
  return new TrimestresEmploi({
    regime, fiche, version: version.id, texte: version.texte,
    services: trimestres, duree: trimestres, majoration: 0,
    auDelaDuMaximum: Boolean(parametres.au_dela_du_maximum), fiabilite,
  });
}

/**
 * Trimestres dus au titre des enfants, enfant par enfant, et régime qui porte
 * ceux de chacun. Voir `majoration_pour_enfants` du Python.
 *
 * Chaque enfant compte à sa date : la version de la fiche se lit sur sa
 * naissance et sur la date d'effet de la pension, et la condition qu'elle lui
 * pose sur sa naissance. Un enfant né à la date d'effet ou après n'ouvre rien.
 * Pour chaque enfant, un seul régime les accorde, et R. 173-15 dit lequel :
 *
 * 1. un RÉGIME SPÉCIAL, qui déclare `bonifications`, passe le premier s'il
 *    peut servir une pension à l'assurée — la durée de services qu'il exige,
 *    `ServicesOuvrantPension` — et si l'enfant y ouvre le droit
 *    (`bonificationOuverte`), même quand il accorde moins (TA Amiens, 2 juin
 *    2017). Entre deux régimes spéciaux, le dernier servi ;
 * 2. sinon le RÉGIME GÉNÉRAL, prioritaire parmi les régimes alignés, et
 *    compétent pour l'enfant qui n'ouvre pas droit dans le régime spécial
 *    (circulaire Cnav 2017-01, fiches n° 6.2a et 6.2b) ;
 * 3. sans lui, le régime de la dernière affiliation, puis celui qui compte le
 *    plus de trimestres.
 *
 * @returns {MajorationEnfants|null}
 */
/**
 * Les trimestres de services d'une année travaillée à `quotite` : sa durée
 * réelle, arrondie au trimestre, un demi-trimestre et plus comptant pour un
 * (L. 13), année par année. Voir `services_a_temps_partiel` du Python.
 */
export function servicesATempsPartiel(trimestres, quotite) {
  if (quotite >= 1.0) {
    return trimestres;
  }
  return Math.floor(trimestres * quotite + 0.5);
}

export function majorationPourEnfants(moteur, carriere, trimestresParRegime, anneeLiquidation) {
  // La date d'effet de la pension, au mois de la liquidation : l'année est
  // celle que l'appelant demande, comme pour le droit à pension.
  const mois = carriere.age_liquidation !== null ? carriere.dateLiquidation.mois : 1;
  const dateEffet = `${String(anneeLiquidation).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`;
  const nes = carriere.naissancesDesEnfants.filter(([, naissance]) => naissance < dateEffet);
  if (nes.length === 0) {
    return null;
  }
  // Les régimes qui peuvent porter les trimestres, et le dispositif de
  // chacun, lus une fois pour tous les enfants.
  const candidats = [];
  for (const [code, valides] of trimestresParRegime) {
    if (!moteur.catalogue.contient(code)) {
      continue;
    }
    const regime = moteur.catalogue.obtenir(code);
    const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
    if (periode === null) {
      continue;
    }
    for (const dispositif of periode.avantages_non_contributifs) {
      if (!(dispositif in moteur.majorationsEnfants.constructor.FICHES)) {
        continue;
      }
      // Un régime EN POINTS ne porte que la majoration de DURÉE, qui ne joue
      // que sur la durée d'assurance : la CNAVPL depuis 2010 (L. 643-1-1).
      // Une bonification entre aux services, qu'il n'a pas.
      if (periode.type_calcul !== "annuites" && dispositif !== MAJORATION_DE_DUREE) {
        continue;
      }
      candidats.push([code, valides, dispositif, periode]);
    }
  }
  // Le droit à pension de chaque régime spécial, et la dernière année de
  // chaque régime : lus une fois, et seulement s'il le faut.
  const droits = new Map();
  let dernieres = null;
  const droitDe = (periode) => {
    if (!droits.has(periode.regime)) {
      droits.set(periode.regime,
        coordonner.droitAPension(moteur, periode.regime, carriere, anneeLiquidation));
    }
    return droits.get(periode.regime);
  };
  const retenir = (parmi) => {
    if (parmi.size > 1 && dernieres === null) {
      dernieres = dernieresAnnees(moteur, carriere, anneeLiquidation);
    }
    return choisir(parmi, dernieres ?? new Map());
  };

  const enfants = [];
  for (const [enfant, naissance] of nes) {
    // Les régimes spéciaux qui peuvent pensionner, ceux qui ne le peuvent pas,
    // et les régimes alignés : code -> [trimestres validés, ce que l'enfant y
    // ouvre].
    const speciaux = new Map();
    const sansPension = new Map();
    const alignes = new Map();
    // Ce qu'a coûté d'écarter un régime spécial : la fiabilité de la règle qui
    // l'a écarté, que la majoration servie ailleurs hérite.
    let fiabiliteEcartes = Fiabilite.CERTIFIEE;
    for (const [code, valides, dispositif, periode] of candidats) {
      const accorde = moteur.majorationsEnfants.parEnfant(
        dispositif, carriere.sexe, naissance, dateEffet, nes.map(([, jour]) => jour),
      );
      if (accorde === null) {
        continue;
      }
      let ouvre = {
        enfant, naissance, regime: code, dispositif,
        fiche: accorde.fiche, version: accorde.version, texte: accorde.texte,
        trimestres: accorde.trimestres, services: accorde.services,
        fiabilite: accorde.fiabilite,
      };
      if (dispositif === MAJORATION_DE_DUREE) {
        alignes.set(code, [valides, ouvre]);
        continue;
      }
      const droit = droitDe(periode);
      if (droit === null) {
        continue;
      }
      if (!bonificationOuverte(accorde.condition, chrono.anneeDe(naissance),
        droit.recrutement, droit.derniere)) {
        // Le droit fermé se lit sur la date de naissance de l'enfant, présumée
        // ou déclarée : la version le dit déjà.
        fiabiliteEcartes = Math.min(fiabiliteEcartes, accorde.fiabilite);
        continue;
      }
      ouvre = { ...ouvre, fiabilite: Math.min(accorde.fiabilite, droit.fiabilite) };
      if (droit.pension) {
        speciaux.set(code, [valides, ouvre]);
      } else {
        fiabiliteEcartes = Math.min(fiabiliteEcartes, droit.fiabilite);
        sansPension.set(code, [valides, ouvre]);
      }
    }
    if (speciaux.size > 0) {
      enfants.push(retenir(speciaux));
      continue;
    }
    let retenue;
    if (alignes.has(REGIME_GENERAL)) {
      retenue = alignes.get(REGIME_GENERAL)[1];
    } else if (alignes.size > 0) {
      retenue = retenir(alignes);
    } else if (sansPension.size > 0) {
      enfants.push(retenir(sansPension));
      continue;
    } else {
      continue;
    }
    if (fiabiliteEcartes < retenue.fiabilite) {
      retenue = { ...retenue, fiabilite: fiabiliteEcartes };
    }
    enfants.push(retenue);
  }
  return enfants.length > 0 ? new MajorationEnfants(enfants) : null;
}

/**
 * Ce que ce régime spécial peut pour un enfant de cette assurée, né cette
 * année-là, sous la condition que la version de la fiche lui pose :
 * `[pension, ouvert, fiabilite]`, null si elle n'y a jamais servi. Voir
 * `droit_regime_special` du Python.
 */
export function droitRegimeSpecial(moteur, periode, carriere, anneeLiquidation, condition,
  naissance) {
  // Les trois régimes interpénétrés se lisent ensemble : voir `droitAPension`.
  const droit = coordonner.droitAPension(moteur, periode.regime, carriere, anneeLiquidation);
  if (droit === null) {
    return null;
  }
  return [
    droit.pension,
    bonificationOuverte(condition, naissance, droit.recrutement, droit.derniere),
    droit.fiabilite,
  ];
}

/**
 * L'enfant né cette année-là ouvre-t-il le droit dans le régime spécial ? La
 * condition est celle que la version de la fiche lui pose (`CONDITIONS`), et la
 * naissance se compare, à l'année près, au recrutement et à la dernière année
 * de services. Une condition inconnue arrête le calcul. Voir
 * `bonification_ouverte` du Python.
 */
export function bonificationOuverte(condition, naissance, recrutement, derniere) {
  if (condition === "tout_enfant") {
    return true;
  }
  if (condition === "ne_en_service") {
    return recrutement <= naissance && naissance <= derniere;
  }
  if (condition === "ne_avant_radiation") {
    return naissance <= derniere;
  }
  if (condition === "accouchement_apres_recrutement") {
    return naissance >= recrutement;
  }
  throw new Error(`condition inconnue pour les trimestres d'un enfant : '${condition}'`);
}

/**
 * La dernière année où chaque régime reçoit une ligne de la carrière, jusqu'à
 * la liquidation : l'affiliation « en dernier lieu » de R. 173-15.
 */
export function dernieresAnnees(moteur, carriere, anneeLiquidation) {
  const dernieres = new Map();
  for (const ligne of carriere.lignes) {
    if (ligne.annee > anneeLiquidation || carriere.trimestresRetenus(ligne) <= 0) {
      continue;
    }
    for (const code of coordonner.regimesDe(moteur,
      ligne, ligne.annee, carriere.dateEntree(ligne.affiliation),
      ligne.cotise ? ligne.revenu : ligne.revenu_reference,
      moteur.macro.plafond_securite_sociale.valeur(ligne.annee),
    )) {
      dernieres.set(code, Math.max(dernieres.get(code) ?? 0, ligne.annee));
    }
  }
  return dernieres;
}

/**
 * Le candidat du régime où l'assurée a été affiliée en dernier lieu ; à
 * égalité, celui qui compte le plus de trimestres, puis le dernier code par
 * ordre alphabétique.
 */
export function choisir(candidats, dernieres) {
  if (candidats.size === 1) {
    return [...candidats.values()][0][1];
  }
  let retenu = null;
  for (const [code, [valides]] of candidats) {
    const cle = [dernieres.get(code) ?? 0, valides, code];
    if (retenu === null || cle[0] > retenu[0]
        || (cle[0] === retenu[0] && (cle[1] > retenu[1]
          || (cle[1] === retenu[1] && cle[2] > retenu[2])))) {
      retenu = cle;
    }
  }
  return candidats.get(retenu[2])[1];
}

/**
 * Part des trimestres d'UNE ligne acquise entre deux dates, `fin` exclue : ses
 * trimestres sont répartis sur ses mois, comme le fait `trimestresEntreDates`,
 * qui en fait la somme.
 */
export function trimestresDeLaLigneEntre(carriere, ligne, debut, fin) {
  const retenus = carriere.trimestresRetenus(ligne);
  const moisLigne = Math.round(carriere.partRetenue(ligne.annee) * 12);
  if (retenus <= 0 || moisLigne <= 0) {
    return 0.0;
  }
  const premier = (moisLigne === 12 || ligne.annee === carriere.anneeLiquidation)
    ? new DateMois(ligne.annee, 1)
    : new DateMois(ligne.annee, 13 - moisLigne);
  const dernier = premier.plusMois(moisLigne);
  const recouvrement = Math.min(fin.rang, dernier.rang) - Math.max(debut.rang, premier.rang);
  return recouvrement > 0 ? retenus * recouvrement / moisLigne : 0.0;
}
