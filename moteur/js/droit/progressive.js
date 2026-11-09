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

/** La fiche qui porte la règle : ses dates et ses valeurs, version par version. */
export const FICHE = "retraite_progressive";
/** Ce que la fiche dit de l'âge, de la fraction, de la pension complète et des régimes liquidés. */
export const AGE_LEGAL = "age_legal";
export const AGE_LEGAL_MOINS_DEUX_ANS = "age_legal_moins_deux_ans";
export const PAR_TRANCHES = "par_tranches";
export const COMPLEMENT_DE_LA_QUOTITE = "complement_de_la_quotite";
export const RECALCULEE = "recalculee";
export const TOUS = "tous";

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

/**
 * La règle de la retraite progressive pour une pension prenant effet à cette
 * date : les paramètres de la version de sa fiche qui vaut ce jour-là, que le
 * paquet porte (`fiches_datees`). Sans version à cette date, aucun droit ;
 * sans la fiche, le paquet est périmé et le calcul s'arrête : un droit ne se
 * refuse pas par défaut.
 */
export function regle(moteur, date) {
  if (!(FICHE in moteur.fichesDatees.fiches())) {
    throw new Error(`${FICHE} : la fiche manque au paquet, que `
      + "scripts/construire_donnees.py refait");
  }
  return moteur.fichesDatees.regle(FICHE, jour(date)) ?? { existe: false };
}

/** L'âge qui ouvre la retraite progressive à cette date ; `null` sans droit. */
export function ageMinimum(moteur, carriere, date) {
  const { age = null, age_plancher: plancher = null } = regle(moteur, date);
  if (age === null) {
    return null;
  }
  let ouvre;
  if (age === AGE_LEGAL) {
    ouvre = lesDeparts.ageLegal(moteur, carriere);
  } else if (age === AGE_LEGAL_MOINS_DEUX_ANS) {
    ouvre = lesDeparts.ageLegal(moteur, carriere) - 2.0;
  } else if (typeof age === "number") {
    ouvre = age;
  } else {
    throw new Error(`${FICHE} : âge « ${age} » inconnu du moteur`);
  }
  return plancher === null ? ouvre : Math.max(plancher, ouvre);
}

/**
 * La durée d'assurance que la retraite progressive demande à cette date ;
 * `null` sans droit.
 */
export function dureeRequise(moteur, date) {
  return regle(moteur, date).duree_requise ?? null;
}

/**
 * Les régimes de base où l'on peut demander la retraite progressive à cette
 * date, en y travaillant à temps partiel.
 */
export function regimesOuverts(moteur, date) {
  return new Set(regle(moteur, date).regimes_ouverts ?? []);
}

/**
 * Les régimes de base où la demande liquide à titre provisoire à cette date ;
 * `null` : tous.
 */
export function regimesLiquides(moteur, date) {
  const liquides = regle(moteur, date).regimes_liquides ?? [];
  if (liquides === TOUS) {
    return null;
  }
  if (!Array.isArray(liquides)) {
    throw new Error(`${FICHE} : régimes liquidés « ${liquides} » inconnus du moteur`);
  }
  return new Set(liquides);
}


/**
 * La fraction servie pour cette quotité, ou `null` si la quotité ne l'ouvre
 * pas : par tranches de quotité, puis, depuis le 18 décembre 2014, ce qui
 * manque à la quotité pour faire 100 %, la quotité arrondie à l'unité, la
 * moitié comptée pour un (R. 351-41, R. 161-19-6). La fiche dit laquelle, ses
 * tranches et ses bornes, celles du fonctionnaire à part.
 */
export function fraction(moteur, date, quotite, fonctionnaire) {
  const lue = regle(moteur, date);
  if (lue.fraction === PAR_TRANCHES) {
    if (quotite > lue.quotite_maximum + 1e-9) {
      return null;
    }
    for (const [seuil, servie] of lue.tranches) {
      if (quotite >= seuil - 1e-9) {
        return servie;
      }
    }
    return null;
  }
  if (lue.fraction !== COMPLEMENT_DE_LA_QUOTITE) {
    if (lue.existe) {
      throw new Error(`${FICHE} : fraction « ${lue.fraction} » inconnue du moteur`);
    }
    return null;
  }
  const points = Math.floor(quotite * 100.0 + 0.5 + 1e-9);
  const bornes = fonctionnaire ? lue.quotite_des_fonctionnaires
    : { minimum: lue.quotite_minimum, maximum: lue.quotite_maximum };
  const [bas, haut] = [Math.round(bornes.minimum * 100.0), Math.round(bornes.maximum * 100.0)];
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
  const lue = regle(moteur, date);
  if (!lue.existe) {
    return new Progressive({ date, quotite, motif: AVANT_1988 });
  }
  const aLaDate = carriere.liquideeAu(date);
  const actifs = lesDeparts.regimesActifs(moteur, aLaDate);
  if (actifs.size === 0) {
    return new Progressive({ date, quotite, motif: SANS_ACTIVITE });
  }
  const ouverts = regimesOuverts(moteur, date);
  if (![...actifs].some((code) => ouverts.has(code))) {
    return new Progressive({ date, quotite, motif: SANS_REGIME });
  }
  const [bases, suivies] = lesDeparts.regimesDeLaCarriere(moteur, aLaDate);
  const liquides = regimesLiquides(moteur, date);
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
  const fonctionnaires = new Set(lue.quotite_des_fonctionnaires?.regimes ?? []);
  const fonctionnaire = [...actifs].some((code) => fonctionnaires.has(code));
  const servie = fraction(moteur, date, quotite, fonctionnaire);
  const age = ageMinimum(moteur, carriere, date);
  const commun = {
    date, quotite, bases: retenues, complementaires, ageMinimum: age,
    dureeRequise: dureeRequise(moteur, date),
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

/**
 * La pension complète qui prend effet à cette date se recalcule-t-elle ? Non
 * avant le décret du 8 juin 2006 : elle était la pension provisoire.
 */
export function recalculee(moteur, date) {
  return regle(moteur, date).pension_complete === RECALCULEE;
}

/**
 * La pension provisoire de chaque régime de base de la retraite progressive,
 * entière, menée jusqu'à `date` : `[[régime, montant], …]`, ce que la pension
 * complète ne peut descendre sous — hors des régimes que la fiche dit sans
 * plancher à cette date, ceux de la fonction publique. `regimes` borne ceux
 * qu'un départ liquide.
 */
export function initiales(moteur, progressive, provisoire, date, regimes = null) {
  const sansPlancher = new Set(regle(moteur, date).pension_complete_sans_plancher ?? []);
  const pensions = provisoire.regimes.filter((p) => progressive.bases.has(p.regime)
    && !sansPlancher.has(p.regime)
    && (regimes === null || regimes.has(p.regime)));
  const menees = menerAuMois(moteur, pensions, progressive.date, date);
  return pensions.map((p, i) => [p.regime, menees[i]]);
}
