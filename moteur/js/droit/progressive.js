/**
 * La retraite progressive (docs/architecture.md, § 7.4 ; fiche
 * `retraite_progressive`).
 *
 * Jumeau de `src/retraite_notionnelle/droit/progressive.py`, fonction pour
 * fonction. L'assuré qui garde en fin de carrière une activité à temps partiel
 * peut demander la liquidation PROVISOIRE de ses pensions et le service d'une
 * fraction : la différence entre 100 % et sa quotité depuis le 18 décembre
 * 2014, 30, 50 ou 70 % selon la tranche de sa quotité avant. Au départ, la
 * pension complète se liquide dans les conditions de droit commun et ne peut
 * être inférieure à la pension provisoire revalorisée, sauf au fonctionnaire ;
 * avant le décret du 8 juin 2006, elle était la pension provisoire. La demande s'ouvre selon la
 * date, l'âge, la durée, la quotité et le régime où l'assuré travaille à temps
 * partiel ; elle liquide les régimes que nomme L. 351-15, puis tous : voir le
 * Python, qui dit aussi pourquoi la décote de la pension provisoire, bornée à
 * 25 % de 2014 à 2023, n'a pas de code.
 */

import { menerAuMois } from "../revalorisation.js";
import * as lesDeparts from "./departs.js";
import * as liquidation from "./liquidation.js";

/** Ce qui ouvre la demande, ou ce qui la ferme. */
export const OUVERTE = "ouverte";
export const AVANT_1988 = "avant_1988";
export const SANS_ACTIVITE = "activite";
export const SANS_REGIME = "regimes";
export const QUOTITE = "quotite";
export const AGE = "age";
export const DUREE = "duree";

/** Les dates qui découpent la règle, au jour. */
export const DEBUT = "1988-05-04";
export const AGE_ABAISSE = "2014-01-22";
export const FRACTION_COMPLEMENTAIRE = "2014-12-18";
export const TOUS_REGIMES = "2023-09-01";
export const SOIXANTE_ANS = "2025-09-01";
/** Depuis le décret du 8 juin 2006, la pension complète se recalcule. */
export const RECALCUL = "2006-06-08";

/** La durée d'assurance exigée, et depuis quand (R. 351-39). */
export const DUREES = [["1988-05-04", 150], ["1993-08-28", 160], ["2006-06-08", 150]];

/**
 * Les régimes de base où l'assuré qui y travaille à temps partiel peut la
 * demander : ceux de la loi de 1988, puis, le 1er septembre 2023, ceux des
 * décrets n° 2023-751 et 2023-753.
 */
export const REGIMES_1988 = new Set([
  "regime_general", "msa_salaries", "cancava", "organic", "rsi", "msa_non_salaries",
]);
export const FONCTION_PUBLIQUE = new Set(["fonction_publique_etat", "cnracl", "fspoeie"]);
export const REGIMES_2023 = new Set([
  ...REGIMES_1988, ...FONCTION_PUBLIQUE, "cnavpl", "cnbf", "crpcen", "opera_de_paris", "mines",
]);
/**
 * Ceux où elle liquide à titre provisoire avant 2023 : les régimes que nomme
 * L. 351-15, les professions libérales comprises. Depuis, tous les régimes de
 * base (L. 161-22-1-5).
 */
export const LIQUIDES_1988 = new Set([...REGIMES_1988, "cnavpl"]);

function jour(date) {
  return `${String(date.annee).padStart(4, "0")}-${String(date.mois).padStart(2, "0")}-01`;
}

/** Une demande de retraite progressive, et ce que le droit en fait. */
export class Progressive {
  constructor({ date, quotite, motif, fraction = 0.0, bases = new Set(),
    complementaires = new Set(), ageMinimum = null, dureeRequise = null,
    trimestres = null }) {
    this.date = date;
    this.quotite = quotite;
    this.motif = motif;
    this.fraction = fraction;
    this.bases = bases;
    this.complementaires = complementaires;
    this.ageMinimum = ageMinimum;
    this.dureeRequise = dureeRequise;
    this.trimestres = trimestres;
  }

  get ouverte() {
    return this.motif === OUVERTE;
  }

  get dateEffet() {
    return jour(this.date);
  }

  get regimes() {
    return new Set([...this.bases, ...this.complementaires]);
  }

  /** La même demande, avec d'autres champs. */
  avec(champs) {
    return new Progressive({
      date: this.date, quotite: this.quotite, motif: this.motif, fraction: this.fraction,
      bases: this.bases, complementaires: this.complementaires,
      ageMinimum: this.ageMinimum, dureeRequise: this.dureeRequise,
      trimestres: this.trimestres, ...champs,
    });
  }
}

/** L'âge qui ouvre la retraite progressive à cette date. */
export function ageMinimum(moteur, carriere, date) {
  const quand = jour(date);
  const legal = lesDeparts.ageLegal(moteur, carriere);
  if (quand < AGE_ABAISSE) {
    return legal;
  }
  if (quand < TOUS_REGIMES) {
    return Math.max(60.0, legal - 2.0);
  }
  if (quand < SOIXANTE_ANS) {
    return legal - 2.0;
  }
  return 60.0;
}

/** La durée d'assurance que la retraite progressive demande à cette date. */
export function dureeRequise(date) {
  const quand = jour(date);
  let requis = DUREES[0][1];
  for (const [depuis, trimestres] of DUREES) {
    if (quand >= depuis) {
      requis = trimestres;
    }
  }
  return requis;
}

/**
 * Les régimes de base où l'on peut demander la retraite progressive à cette
 * date, en y travaillant à temps partiel.
 */
export function regimesOuverts(date) {
  return jour(date) >= TOUS_REGIMES ? REGIMES_2023 : REGIMES_1988;
}

/**
 * Les régimes de base où la demande liquide à titre provisoire à cette date ;
 * `null` : tous.
 */
export function regimesLiquides(date) {
  return jour(date) >= TOUS_REGIMES ? null : LIQUIDES_1988;
}


/**
 * La fraction servie pour cette quotité, ou `null` si la quotité ne l'ouvre
 * pas. Depuis le 18 décembre 2014, la quotité s'arrondit à l'unité, la moitié
 * comptée pour un (R. 351-41, R. 161-19-6).
 */
export function fraction(date, quotite, fonctionnaire) {
  if (jour(date) < FRACTION_COMPLEMENTAIRE) {
    if (quotite > 0.8 + 1e-9) {
      return null;
    }
    return quotite >= 0.6 - 1e-9 ? 0.3 : quotite >= 0.4 - 1e-9 ? 0.5 : 0.7;
  }
  const points = Math.floor(quotite * 100.0 + 0.5 + 1e-9);
  const [bas, haut] = fonctionnaire ? [50, 90] : [40, 80];
  if (!(bas <= points && points <= haut)) {
    return null;
  }
  return (100 - points) / 100.0;
}

/**
 * La retraite progressive que `carriere` demande, ouverte ou non ; `null` sans
 * demande. La durée d'assurance se lit sur sa liquidation (`avecLaDuree`).
 */
export function examiner(moteur, carriere) {
  const demande = carriere.retraiteProgressive;
  if (demande === null) {
    return null;
  }
  const [date, quotite] = demande;
  if (jour(date) < DEBUT) {
    return new Progressive({ date, quotite, motif: AVANT_1988 });
  }
  const aLaDate = carriere.liquideeAu(date);
  const actifs = lesDeparts.regimesActifs(moteur, aLaDate);
  if (actifs.size === 0) {
    return new Progressive({ date, quotite, motif: SANS_ACTIVITE });
  }
  const ouverts = regimesOuverts(date);
  if (![...actifs].some((code) => ouverts.has(code))) {
    return new Progressive({ date, quotite, motif: SANS_REGIME });
  }
  const [bases, suivies] = lesDeparts.regimesDeLaCarriere(moteur, aLaDate);
  const liquides = regimesLiquides(date);
  const retenues = new Set(bases.filter((code) => liquides === null || liquides.has(code)));
  if (retenues.size === 0) {
    return new Progressive({ date, quotite, motif: SANS_REGIME });
  }
  // Les complémentaires qui suivent un régime qui sert la retraite
  // progressive : pas celles des libéraux avant 2023.
  const complementaires = new Set();
  for (const [code, avec] of suivies) {
    if (code !== lesDeparts.RAFP
        && [...avec].some((base) => retenues.has(base) && ouverts.has(base))) {
      complementaires.add(code);
    }
  }
  const fonctionnaire = [...actifs].some((code) => FONCTION_PUBLIQUE.has(code));
  const servie = fraction(date, quotite, fonctionnaire);
  const age = ageMinimum(moteur, carriere, date);
  const commun = {
    date, quotite, bases: retenues, complementaires, ageMinimum: age,
    dureeRequise: dureeRequise(date),
  };
  if (servie === null) {
    return new Progressive({ ...commun, motif: QUOTITE });
  }
  if (carriere.ageAu(date) + 1e-9 < age) {
    return new Progressive({ ...commun, motif: AGE });
  }
  return new Progressive({ ...commun, motif: OUVERTE, fraction: servie });
}

/**
 * La liquidation provisoire des régimes de la retraite progressive, sur la
 * carrière arrêtée à sa date.
 */
export function liquider(moteur, carriere, contexte, progressive, journal = null) {
  const demande = new liquidation.Demande({
    personne: carriere.personne, dateEffet: progressive.dateEffet,
    evenement: "retraite_progressive", dateEvenement: progressive.dateEffet,
    nature: "provisoire", regimes: [...progressive.regimes].sort(),
  });
  return liquidation.liquider(
    demande, new liquidation.Etat(carriere.liquideeAu(progressive.date), journal),
    contexte);
}

/** La demande, sa durée d'assurance lue : fermée sous la durée requise. */
export function avecLaDuree(progressive, provisoire) {
  const trimestres = provisoire.releve.durees.trimestres;
  const motif = !progressive.ouverte || trimestres >= (progressive.dureeRequise ?? 0)
    ? progressive.motif : DUREE;
  return progressive.avec({
    trimestres, motif, fraction: motif === OUVERTE ? progressive.fraction : 0.0,
  });
}

/** La pension complète qui prend effet à cette date se recalcule-t-elle ? */
export function recalculee(date) {
  return jour(date) >= RECALCUL;
}

/**
 * La pension provisoire de chaque régime de base de la retraite progressive,
 * entière, menée jusqu'à `date` : `[[régime, montant], …]`, ce que la pension
 * complète ne peut descendre sous — hors de la fonction publique, qui n'a pas
 * ce plancher. `regimes` borne ceux qu'un départ liquide.
 */
export function initiales(moteur, progressive, provisoire, date, regimes = null) {
  const pensions = provisoire.regimes.filter((p) => progressive.bases.has(p.regime)
    && !FONCTION_PUBLIQUE.has(p.regime)
    && (regimes === null || regimes.has(p.regime)));
  const menees = menerAuMois(moteur, pensions, progressive.date, date);
  return pensions.map((p, i) => [p.regime, menees[i]]);
}
