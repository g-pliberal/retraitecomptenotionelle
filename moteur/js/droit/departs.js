/**
 * Le départ de chaque régime (docs/architecture.md, § 7.4).
 *
 * Jumeau de `src/retraite_notionnelle/droit/departs.py`, fonction pour
 * fonction. Le droit ne connaît pas de départ « tous régimes » : chaque régime
 * sert sa pension quand l'assuré la demande et remplit SES conditions (fiche
 * `liquidation_regime_par_regime`). Cette étape dit, pour une carrière et son
 * départ déclaré, QUAND chaque régime liquide : une UNITÉ est un régime de
 * base ou intégré, ou le groupe que la loi fait liquider ensemble ; chaque
 * complémentaire suit l'unité avec laquelle ses années sont routées, et le
 * RAFP n'ouvre qu'à l'âge légal (fiche `rafp_age_d_ouverture`). La présomption
 * `depart_de_chaque_regime` date la demande : au départ déclaré ; à
 * l'ouverture, pour l'unité qui n'ouvre pas encore ; à la sortie de l'armée,
 * pour la pension militaire. La personne peut DIRE la date où elle demande une
 * pension : une date plus tardive remplace la présumée, une plus précoce ne
 * l'avance pas, et `DemandeExaminee` dit pourquoi. Le départ reste UNIQUE
 * quand toutes les unités liquident au départ déclaré, et quand aucune n'y est
 * ouverte sans que rien soit demandé plus tard.
 *
 * `liquiderLesDeparts` liquide ensuite chaque départ, dans l'ordre des dates,
 * chacun sur la carrière arrêtée à sa date et voyant les pensions déjà
 * servies. Voir le Python.
 */

import { DateMois } from "../calendrier.js";
import { menerAuMois } from "../revalorisation.js";
import { derniereAnnee } from "./commun.js";
import * as compter from "./compter.js";
import * as coordonner from "./coordonner.js";
import * as etranger from "./etranger.js";
import * as invalidite from "./invalidite.js";
import * as liquidation from "./liquidation.js";
import * as ouvrirLeDroit from "./ouvrir.js";
import * as lesProgressives from "./progressive.js";

/** L'étage des régimes qui forment une unité. */
export const ETAGES_DES_UNITES = new Set(["base", "integre"]);

/** Le RAFP, que l'article 6 du décret n° 2004-569 n'ouvre qu'à l'âge légal. */
export const RAFP = "rafp";

/** Ce qui date un départ, par rapport au départ déclaré. */
export const MOTIF_DEPART = "depart";
export const MOTIF_OUVERTURE = "ouverture";
export const MOTIF_SORTIE = "sortie";
/** Une date que la personne demande, plus tardive que la présumée. */
export const MOTIF_DEMANDE = "demande";
/** La pension de vieillesse qui remplace la pension d'invalidité. */
export const MOTIF_INVALIDITE = "invalidite";
/** La pension du fonctionnaire radié des cadres pour invalidité, à la radiation. */
export const MOTIF_RADIATION = "radiation";

/**
 * Ce qu'une demande devient quand elle ne date pas sa pension : servie avec la
 * pension que la loi lui attache, ou sans pension de ce régime.
 */
export const ENSEMBLE = "ensemble";
export const SANS_PENSION = "sans_pension";

/** Un départ : le mois où il prend effet, et les régimes qui y liquident. */
export class Depart {
  constructor(date, regimes = new Set(), motif = MOTIF_DEPART) {
    this.date = date;
    // Vide pour le départ unique, où tous liquident ensemble.
    this.regimes = regimes;
    this.motif = motif;
  }

  /** La date d'effet (AAAA-MM-JJ) : le premier jour du mois. */
  get dateEffet() {
    return `${String(this.date.annee).padStart(4, "0")}-`
      + `${String(this.date.mois).padStart(2, "0")}-01`;
  }

  /** Le départ unique, où tous les régimes liquident ensemble. */
  get unique() {
    return this.regimes.size === 0;
  }
}

/**
 * Une pension dont la personne dit la date de demande, et la date où le modèle
 * la sert : la demandée quand elle vient après la présumée, la présumée sinon,
 * avec sa raison. Voir `DemandeExaminee` du Python.
 */
export class DemandeExaminee {
  constructor(regime, demandee, retenue, motif) {
    this.regime = regime;
    this.demandee = demandee;
    // Le mois où la pension commence ; `null` sans pension de ce régime.
    this.retenue = retenue;
    // `demande`, `depart`, `ouverture`, `sortie`, `ensemble` ou `sans_pension`.
    this.motif = motif;
  }

  donnees() {
    return {
      regime: this.regime, demandee: new Depart(this.demandee).dateEffet,
      retenue: this.retenue === null ? null : new Depart(this.retenue).dateEffet,
      motif: this.motif,
    };
  }
}

function periodeDe(moteur, code, annee) {
  if (!moteur.catalogue.contient(code)) {
    return null;
  }
  const regime = moteur.catalogue.obtenir(code);
  return regime.periode(Math.min(annee, derniereAnnee(regime)));
}

/**
 * Chaque ligne jusqu'au départ déclaré, et les régimes qui la reçoivent : le
 * routage que toute l'acquisition lit.
 */
function routage(moteur, carriere) {
  const anneeLiquidation = carriere.anneeLiquidation;
  return carriere.lignes
    .filter((ligne) => ligne.annee <= anneeLiquidation)
    .map((ligne) => [ligne, [...coordonner.regimesDe(
      moteur, ligne, ligne.annee, carriere.dateEntree(ligne.affiliation),
      ligne.cotise ? ligne.revenu : ligne.revenu_reference,
      moteur.macro.plafond_securite_sociale.valeur(ligne.annee),
    )]]);
}

/**
 * Une ligne au moins ouvre-t-elle un droit dans ce régime ? Une période
 * validée sans cotisation en ouvre ; une année cotisée, si l'assiette du
 * régime n'y est pas nulle. Voir `_acquiert` dans le Python.
 */
function acquiert(moteur, code, routes) {
  for (const [ligne, regimes] of routes) {
    if (!regimes.includes(code)) {
      continue;
    }
    if (!ligne.cotise) {
      // Une période qui ne valide rien — celle « sans activité » qui suit une
      // radiation — n'ouvre pas de droit.
      if (ligne.trimestres_valides > 0) {
        return true;
      }
      continue;
    }
    const periode = periodeDe(moteur, code, ligne.annee);
    if (periode === null || periode.partDuRevenu(ligne.revenu, ligne.part_primes) > 0) {
      return true;
    }
  }
  return false;
}

/**
 * Les unités : chaque régime de base ou intégré, ceux que le droit fait
 * liquider ensemble réunis, dans l'ordre de leur premier membre.
 */
function unitesDe(moteur, carriere, bases, routes) {
  const derniere = new Map();
  for (const [ligne, regimes] of routes) {
    for (const code of regimes) {
      derniere.set(code, Math.max(derniere.get(code) ?? ligne.annee, ligne.annee));
    }
  }
  const groupes = coordonner.groupesDeSuccession(
    moteur, bases, carriere.anneeLiquidation, derniere, carriere);
  const unites = [];
  const vus = new Set();
  for (const code of bases) {
    if (vus.has(code)) {
      continue;
    }
    const unite = new Set(groupes.get(code) ?? [code]);
    for (const membre of unite) {
      vus.add(membre);
    }
    unites.push(unite);
  }
  return unites;
}

/**
 * Le premier mois où l'unité peut servir sa pension à cet assuré : l'âge que
 * l'étape « ouvrir le droit » oppose à chacun de ses régimes, ou celui de la
 * carrière longue acquise au départ déclaré. Voir `_ouverture` dans le Python.
 */
function ouvertureDe(moteur, carriere, unite) {
  const annee = carriere.anneeLiquidation;
  const periodes = [];
  for (const code of [...unite].sort()) {
    const periode = periodeDe(moteur, code, annee);
    if (periode !== null) {
      periodes.push([code, periode]);
    }
  }
  const annuites = periodes.filter(([, p]) => p.type_calcul === "annuites");
  const autres = periodes.filter(([, p]) => p.type_calcul !== "annuites");
  const retenues = annuites.length > 0 ? annuites : ouvrirLeDroit.sansAgesPropres(autres);
  if (retenues.length === 0) {
    return carriere.dateLiquidation;
  }
  let age = Math.min(...retenues.map(
    ([, periode]) => ouvrirLeDroit.ageOuverture(moteur, periode, carriere)));
  const opposent = annuites.length > 0
    ? annuites : ouvrirLeDroit.periodesOpposantUneDuree(autres);
  const longue = carriereLongueAcquise(moteur, carriere, opposent);
  if (longue !== null && longue < age) {
    age = longue;
  }
  return carriere.dateDeLAge(age);
}

/**
 * L'âge que la carrière longue ouvre aux régimes de `periodes` sur la durée
 * cotisée au départ déclaré, ou `null`. Voir `_carriere_longue_acquise`.
 */
function carriereLongueAcquise(moteur, carriere, periodes) {
  if (periodes.length === 0) {
    return null;
  }
  const requis = Math.max(...periodes.map(
    ([, periode]) => ouvrirLeDroit.dureeRequise(moteur, periode, carriere)[0])) || 160;
  const anneeLiquidation = carriere.anneeLiquidation;
  let cotises = carriere.trimestresCumules(carriere.lignes.filter(
    (ligne) => ligne.cotise && ligne.annee <= anneeLiquidation));
  const famille = etranger.familleDesRegimes(moteur, periodes.map(([code]) => code));
  const etrangers = etranger.trimestresEtrangers(moteur, carriere);
  const majoration = compter.majorationPourEnfants(
    moteur, carriere, new Map(periodes.map(([code]) => [code, cotises])), anneeLiquidation);
  cotises = moteur.carriereLongue.cotisesReputes(
    carriere, cotises + etrangers.trimestresCotises(famille),
    majoration !== null ? majoration.trimestres : 0);
  const anticipe = moteur.carriereLongue.ageDeDepart(
    carriere, anneeLiquidation, cotises, requis, etrangers.cotises[famille]);
  return anticipe === null ? null : anticipe[0];
}

/**
 * Le mois où l'assuré quitte l'unité : le 1er janvier qui suit sa dernière
 * année d'activité dans ses régimes, ou le départ déclaré s'il y travaille
 * encore cette année-là.
 */
function sortieDe(carriere, unite, routes) {
  const declare = carriere.dateLiquidation;
  const annees = routes
    .filter(([ligne, regimes]) => ligne.cotise && regimes.some((code) => unite.has(code)))
    .map(([ligne]) => ligne.annee);
  if (annees.length === 0 || Math.max(...annees) >= declare.annee) {
    return declare;
  }
  return new DateMois(Math.max(...annees) + 1, 1);
}

/**
 * L'unité sert-elle une pension militaire ? Celle de l'État, quand l'assuré
 * n'y a servi que sous l'uniforme. Voir `_pension_militaire` dans le Python.
 */
function pensionMilitaire(moteur, carriere, unite) {
  return unite.has("fonction_publique_etat")
    && !coordonner.regimesInterpenetres(moteur, carriere).has("fonction_publique_etat");
}

/**
 * Les régimes de base et intégrés où `carriere` acquiert un droit jusqu'à sa
 * liquidation, dans l'ordre de leurs codes, et, pour chaque complémentaire,
 * ceux de ces régimes avec lesquels ses années sont routées : ce qu'une
 * retraite progressive liquide à sa date (`progressive.js`).
 *
 * @returns {[string[], Map<string, Set<string>>]}
 */
export function regimesDeLaCarriere(moteur, carriereSaisie) {
  const carriere = coordonner.retablir(moteur, carriereSaisie);
  const routes = routage(moteur, carriere);
  const routesVers = new Set(routes.flatMap(([, regimes]) => regimes));
  const codes = [...routesVers].sort().filter((code) =>
    periodeDe(moteur, code, carriere.anneeLiquidation) !== null
    && acquiert(moteur, code, routes));
  const bases = codes.filter(
    (code) => ETAGES_DES_UNITES.has(moteur.catalogue.obtenir(code).etage));
  const deBase = new Set(bases);
  const retenus = new Set(codes);
  const suivies = new Map();
  for (const [, regimes] of routes) {
    const routees = regimes.filter((code) => deBase.has(code));
    for (const code of regimes) {
      if (retenus.has(code) && !deBase.has(code)) {
        if (!suivies.has(code)) {
          suivies.set(code, new Set());
        }
        for (const base of routees) {
          suivies.get(code).add(base);
        }
      }
    }
  }
  return [bases, suivies];
}

/**
 * Les régimes de base et intégrés où `carriere` exerce une activité l'année de
 * sa liquidation : ceux du temps partiel qu'une retraite progressive garde
 * (`droit/progressive.js`). Aucun quand elle ne travaille pas cette année-là.
 */
export function regimesActifs(moteur, carriereSaisie) {
  const carriere = coordonner.retablir(moteur, carriereSaisie);
  const actifs = new Set();
  for (const [ligne, regimes] of routage(moteur, carriere)) {
    if (ligne.annee !== carriere.anneeLiquidation || ligne.type_periode !== "emploi"
        || !(ligne.revenu > 0)) {
      continue;
    }
    for (const code of regimes) {
      if (ETAGES_DES_UNITES.has(moteur.catalogue.obtenir(code).etage)) {
        actifs.add(code);
      }
    }
  }
  return actifs;
}

/** L'âge de L. 161-17-2 pour la génération de l'assuré : celui du RAFP. */
export function ageLegal(moteur, carriere) {
  const lu = moteur.agesOuverture.age(carriere.generation);
  return lu !== null ? lu[0] : 60.0;
}

/**
 * Les départs de `carriere`, dans l'ordre des dates : un seul, le départ
 * déclaré, quand tous les régimes y liquident ou qu'aucune unité n'y est
 * ouverte ; sinon, un par date. Aucun pour une carrière sans départ.
 *
 * @returns {Depart[]}
 */
export function departs(moteur, carriereSaisie) {
  return departsEtDemandes(moteur, carriereSaisie)[0];
}

/** Les pensions dont `carriere` dit la date de demande, examinées. */
export function demandes(moteur, carriereSaisie) {
  return departsEtDemandes(moteur, carriereSaisie)[1];
}

/**
 * Les départs de `carriere`, et ce que devient chaque date de demande qu'elle
 * dit, en un calcul. Voir `departs_et_demandes` du Python.
 *
 * @returns {[Depart[], DemandeExaminee[]]}
 */
export function departsEtDemandes(moteur, carriereSaisie) {
  if (carriereSaisie.age_liquidation === null) {
    return [[], []];
  }
  const declare = carriereSaisie.dateLiquidation;
  const unique = [new Depart(declare)];
  const demandees = carriereSaisie.demandesDePension;
  const carriere = coordonner.retablir(moteur, carriereSaisie);
  const routes = routage(moteur, carriere);
  const routesVers = new Set(routes.flatMap(([, regimes]) => regimes));
  const codes = [...routesVers].sort().filter((code) =>
    periodeDe(moteur, code, carriere.anneeLiquidation) !== null
    && acquiert(moteur, code, routes));
  const bases = codes.filter(
    (code) => ETAGES_DES_UNITES.has(moteur.catalogue.obtenir(code).etage));
  if (bases.length === 0) {
    return [unique, examiner(demandees, new Map(), new Set(), null)];
  }
  const unites = unitesDe(moteur, carriere, bases, routes);
  const uniteDe = new Map();
  unites.forEach((unite, i) => {
    for (const code of unite) {
      uniteDe.set(code, i);
    }
  });

  // Chaque complémentaire suit les unités dont elle partage les années.
  const retenus = new Set(codes);
  const suivies = new Map();
  for (const [, regimes] of routes) {
    const indices = regimes.filter((code) => uniteDe.has(code)).map((code) => uniteDe.get(code));
    for (const code of regimes) {
      if (retenus.has(code) && !uniteDe.has(code)) {
        if (!suivies.has(code)) {
          suivies.set(code, new Set());
        }
        for (const i of indices) {
          suivies.get(code).add(i);
        }
      }
    }
  }

  // La date présumée de chaque unité, et ce qui la date ; puis la demande,
  // quand elle vient après : la plus tardive des régimes de l'unité.
  const ouvertures = unites.map((unite) => ouvertureDe(moteur, carriere, unite));
  // La pension de vieillesse de l'ex-invalide, quand elle commence au plus tard
  // au départ déclaré : d'office, elle ne s'avance ni ne se reporte ;
  // l'invalide qui travaille la demande, et sa demande la date.
  let substituee = invalidite.substitution(moteur, carriere);
  if (substituee !== null && substituee.date.rang > declare.rang) {
    substituee = null;
  }
  const substitues = moteur.invalidites.regimes("substitution");
  const dates = unites.map((unite, i) => {
    const voulueDe = () => {
      let voulue = null;
      for (const code of unite) {
        const demandee = demandees.get(code);
        if (demandee !== undefined && (voulue === null || demandee.rang > voulue.rang)) {
          voulue = demandee;
        }
      }
      return voulue;
    };
    // Le fonctionnaire radié des cadres pour invalidité liquide sa pension à la
    // radiation, à tout âge (L. 24, I, 2°).
    if ([...unite].some((code) => invalidite.radiationDuRegime(moteur, code, carriere) !== null)) {
      return [carriere.radiationPourInvalidite.date, MOTIF_RADIATION];
    }
    if (substituee !== null && [...unite].some((code) => substitues.has(code))) {
      const presumee = [substituee.date, MOTIF_INVALIDITE];
      const voulue = voulueDe();
      return substituee.maintien === invalidite.ACTIVITE
        && voulue !== null && voulue.rang > presumee[0].rang
        ? [voulue, MOTIF_DEMANDE] : presumee;
    }
    let presumee;
    if (ouvertures[i].rang > declare.rang) {
      presumee = [ouvertures[i], MOTIF_OUVERTURE];
    } else {
      const sortie = sortieDe(carriere, unite, routes);
      const plusTot = sortie.rang > ouvertures[i].rang ? sortie : ouvertures[i];
      presumee = plusTot.rang < declare.rang && pensionMilitaire(moteur, carriere, unite)
        ? [plusTot, MOTIF_SORTIE] : [declare, MOTIF_DEPART];
    }
    const voulue = voulueDe();
    return voulue !== null && voulue.rang > presumee[0].rang
      ? [voulue, MOTIF_DEMANDE] : presumee;
  });
  if (ouvertures.every((ouverture) => ouverture.rang > declare.rang)
      && dates.every(([, motif]) => motif !== MOTIF_DEMANDE)) {
    return [unique, []];
  }

  const parRegime = new Map();
  for (const [code, i] of uniteDe) {
    parRegime.set(code, dates[i]);
  }
  for (const [code, indices] of suivies) {
    let quand = null;
    for (const i of [...indices].sort((a, b) => a - b)) {
      if (quand === null || dates[i][0].rang > quand[0].rang) {
        quand = dates[i];
      }
    }
    parRegime.set(code, quand ?? [declare, MOTIF_DEPART]);
  }
  let legal = null;
  if (parRegime.has(RAFP)) {
    legal = carriere.dateDeLAge(ageLegal(moteur, carriere));
    if (legal.rang > parRegime.get(RAFP)[0].rang) {
      parRegime.set(RAFP, [legal, MOTIF_OUVERTURE]);
    }
  }
  for (const [code, [quand]] of [...parRegime]) {
    const demandee = demandees.get(code);
    if (!uniteDe.has(code) && demandee !== undefined && demandee.rang > quand.rang) {
      parRegime.set(code, [demandee, MOTIF_DEMANDE]);
    }
  }

  const examens = examiner(demandees, parRegime, new Set(uniteDe.keys()), legal);
  const parDate = new Map();
  for (const [code, [quand]] of parRegime) {
    if (!parDate.has(quand.rang)) {
      parDate.set(quand.rang, [quand, new Set()]);
    }
    parDate.get(quand.rang)[1].add(code);
  }
  if (parDate.size === 1 && parDate.has(declare.rang)) {
    return [unique, examens];
  }
  // Ce qui date un départ : l'acte de la personne d'abord, puis la sortie de
  // l'armée ; l'ouverture d'un régime sinon, le RAFP à l'âge légal compris.
  const motifDe = (rang, regimes) => {
    if (rang === declare.rang) {
      return MOTIF_DEPART;
    }
    const motifs = new Set([...regimes].map((code) => parRegime.get(code)[1]));
    for (const retenu of [MOTIF_DEMANDE, MOTIF_SORTIE, MOTIF_RADIATION, MOTIF_INVALIDITE]) {
      if (motifs.has(retenu)) {
        return retenu;
      }
    }
    return MOTIF_OUVERTURE;
  };
  const liste = [...parDate.keys()].sort((a, b) => a - b).map((rang) => {
    const [quand, regimes] = parDate.get(rang);
    return new Depart(quand, regimes, motifDe(rang, regimes));
  });
  return [liste, examens];
}

/**
 * Ce que devient chaque date demandée : celle de sa pension, ou la date
 * retenue et sa raison. Voir `_examiner` du Python.
 */
function examiner(demandees, parRegime, unites, legal) {
  return [...demandees.keys()].sort().map((code) => {
    const demandee = demandees.get(code);
    if (!parRegime.has(code)) {
      return new DemandeExaminee(code, demandee, null, SANS_PENSION);
    }
    const [retenue, presume] = parRegime.get(code);
    let motif = presume;
    if (retenue.rang === demandee.rang) {
      motif = MOTIF_DEMANDE;
    } else if (code === RAFP && legal !== null && retenue.rang === legal.rang) {
      motif = MOTIF_OUVERTURE;
    } else if (presume === MOTIF_DEMANDE || !unites.has(code)) {
      motif = ENSEMBLE;
    }
    return new DemandeExaminee(code, demandee, retenue, motif);
  });
}

/**
 * Chaque départ liquidé, dans l'ordre des dates : sur la carrière arrêtée à
 * sa date, pour ses seuls régimes, en voyant servies les pensions des départs
 * qui le précèdent, menées jusqu'à lui (R. 173-7 : le minimum contributif
 * s'écrête sur les pensions du mois de sa date d'effet).
 */
export function liquiderLesDeparts(moteur, carriere, contexte, nature = "definitive",
  liste = null, journal = null, progressive = null) {
  const lesDeparts = liste ?? departs(moteur, carriere);
  const liquidations = [];
  for (const depart of lesDeparts) {
    const demande = new liquidation.Demande({
      personne: carriere.personne, dateEffet: depart.dateEffet,
      dateEvenement: depart.dateEffet, nature,
      regimes: depart.unique ? [] : [...depart.regimes].sort(),
    });
    const servies = [];
    for (const anterieure of liquidations) {
      const menes = menerAuMois(moteur, anterieure.regimes,
        anterieure.carriere.dateLiquidation, depart.date);
      anterieure.regimes.forEach((pension, i) => {
        servies.push({ regime: pension.regime, montant: menes[i] });
      });
    }
    let initiales = [];
    let recalcul = true;
    if (progressive !== null) {
      const [ouverte, provisoire] = progressive;
      initiales = lesProgressives.initiales(moteur, ouverte, provisoire, depart.date,
        depart.unique ? null : depart.regimes);
      recalcul = lesProgressives.recalculee(depart.date);
    }
    const etat = new liquidation.Etat(carriere.liquideeAu(depart.date), journal, servies,
      initiales, recalcul);
    liquidations.push(liquidation.liquider(demande, etat, contexte));
  }
  return liquidations;
}
