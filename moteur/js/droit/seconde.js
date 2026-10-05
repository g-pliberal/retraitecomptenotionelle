/**
 * Les droits de l'activité exercée après le départ (docs/architecture.md,
 * § 7.4 ; fiches `droits_apres_la_premiere_pension` et `seconde_pension`).
 *
 * Jumeau de `src/retraite_notionnelle/droit/seconde.py`, fonction pour
 * fonction. Après une première pension de base, l'activité n'ouvre plus aucun
 * droit, pour qui la prend depuis 2015, puis pour tous depuis 2023, sauf, en
 * cumul intégral, une nouvelle pension dans le régime de base de l'activité
 * — au taux plein, plafonnée à 5 % du plafond de la sécurité sociale avant les
 * premières pensions de 2027 — et une seconde retraite de l'Agirc-Arrco, sur
 * les points de la tranche 1 : voir le Python, qui dit les textes.
 */

import { DateMois } from "../calendrier.js";
import { menerAuMois } from "../revalorisation.js";
import * as lesDeparts from "./departs.js";
import * as liquidation from "./liquidation.js";
import { valeurDuPoint } from "./liquider.js";
import { FONCTION_PUBLIQUE, fonctionPubliqueQuittee, jour } from "./cumul.js";

/** Ce que le droit fait d'un mois d'activité après le départ. */
export const NOUVELLE_PENSION = "nouvelle_pension";
export const ETEINTS = "eteints";
export const DERNIER_EMPLOYEUR = "dernier_employeur";
export const REGIMES_NON_LIQUIDES = "regimes_non_liquides";
export const REGIME_LIQUIDE = "regime_liquide";
export const PENSION_MILITAIRE = "pension_militaire";

/** Les versions de la fiche `droits_apres_la_premiere_pension`. */
export const SANS_REGLE_GENERALE = "sans_regle_generale";
export const LOI_2014 = "loi_2014";
export const LOI_2023 = "loi_2023";
export const LFSS_2026 = "lfss_2026";

/** Les dates qui découpent la règle, en rang de mois. */
const rang = (annee, mois) => new DateMois(annee, mois).rang;
export const PREMIERE_2015 = rang(2015, 1);
export const DROITS_2023 = rang(2023, 1);
export const LIQUIDATION_2023 = rang(2023, 9);
// La seconde retraite de l'Agirc-Arrco « prend effet, au plus tôt, le 1er
// janvier 2024 » (avenant n° 16 ; voir seconde.py).
export const LIQUIDATION_AGIRC_ARRCO = rang(2024, 1);
export const PREMIERE_2027 = rang(2027, 1);

export const TAUX_PLEIN = 0.5;
export const PLAFOND_EN_PASS = 0.05;
export const HEURES_PAR_TRIMESTRE = 150;
export const REGIMES_CALCULES = new Set(["regime_general", "msa_salaries"]);
export const AGIRC_ARRCO = "agirc_arrco";

/** Des mois consécutifs d'activité que le droit traite de même. */
export class PeriodeDeDroits {
  constructor(debut, fin, motif, regle) {
    this.debut = debut;
    this.fin = fin;
    this.motif = motif;
    this.regle = regle;
  }

  donnees() {
    return { debut: jour(this.debut), fin: jour(this.fin), motif: this.motif,
      regle: this.regle };
  }
}

/** La nouvelle pension d'un régime, ou la seconde retraite complémentaire. */
export class NouvellePension {
  constructor({ regime, dateEffet, trimestres, salaireMensuel, points, brute, plafond,
    montant }) {
    this.regime = regime;
    this.date_effet = dateEffet;
    this.trimestres = trimestres;
    this.salaire_mensuel = salaireMensuel;
    this.points = points;
    this.brute = brute;
    this.plafond = plafond;
    this.montant = montant;
  }

  donnees() {
    return { regime: this.regime, date_effet: jour(this.date_effet),
      trimestres: this.trimestres, salaire_mensuel: this.salaire_mensuel,
      points: this.points, brute: this.brute, plafond: this.plafond,
      montant: this.montant };
  }
}

/**
 * La pension d'un régime que l'activité après le départ ouvre, liquidée à sa
 * date : par an, en euros de cette date.
 */
export class PensionDeRegimeNouveau {
  constructor(regime, dateEffet, montant, detail) {
    this.regime = regime;
    this.date_effet = dateEffet;
    this.montant = montant;
    this.detail = detail;
  }

  donnees() {
    return { regime: this.regime, date_effet: jour(this.date_effet), montant: this.montant,
      detail: this.detail };
  }
}

/**
 * Ce que l'activité après le départ ouvre de droits, mois par mois, et les
 * pensions nouvelles qu'elle constitue.
 */
export class DroitsApresDepart {
  constructor({ periodes, pensions, nonCalcules, regimesNouveaux = [] }) {
    this.periodes = periodes;
    this.pensions = pensions;
    this.non_calcules = nonCalcules;
    this.regimes_nouveaux = regimesNouveaux;
  }

  get montant() {
    return this.pensions.reduce((total, p) => total + p.montant, 0.0);
  }

  donnees() {
    return { periodes: this.periodes.map((p) => p.donnees()),
      pensions: this.pensions.map((p) => p.donnees()),
      non_calcules: [...this.non_calcules], montant: this.montant,
      regimes_nouveaux: this.regimes_nouveaux.map((p) => p.donnees()) };
  }
}

/** Ce que le droit fait d'un mois d'activité, et la version qui le dit. */
function motif(mois, premiere, integral, sixMois, militaire, nouveaux) {
  if (militaire) {
    return [PENSION_MILITAIRE, mois.rang < DROITS_2023 ? LOI_2014 : LOI_2023];
  }
  if (mois.rang < DROITS_2023) {
    if (premiere.rang >= PREMIERE_2015) return [ETEINTS, LOI_2014];
    return [nouveaux ? REGIMES_NON_LIQUIDES : REGIME_LIQUIDE, SANS_REGLE_GENERALE];
  }
  const regle = premiere.rang >= PREMIERE_2027 ? LFSS_2026 : LOI_2023;
  if (sixMois) return [DERNIER_EMPLOYEUR, regle];
  if (integral !== null && mois.rang >= integral.rang) return [NOUVELLE_PENSION, regle];
  return [ETEINTS, regle];
}

/**
 * Les droits de l'activité que `carriere` exerce après son départ, ou `null`
 * sans elle. `cumul` est ce que le cumul emploi-retraite en fait
 * (`droit/cumul.js`) : son premier mois de cumul intégral ouvre la nouvelle
 * pension.
 */
export function droits(moteur, carriere, resultat, cumul) {
  if (cumul === null || resultat === null) return null;
  const premiere = carriere.dateLiquidation;
  const sixMois = cumul.employeur === "dernier" && cumul.debut.rang < premiere.plusMois(6).rang;
  const unite = (code) => lesDeparts.ETAGES_DES_UNITES.has(moteur.catalogue.obtenir(code).etage);
  const bases = resultat.pensions_par_regime.map((p) => p.regime).filter(unite);
  const militaire = fonctionPubliqueQuittee(moteur, carriere)[0] && bases.length > 0
    && bases.every((code) => FONCTION_PUBLIQUE.has(code));
  const liquides = new Set(resultat.pensions_par_regime.map((p) => p.regime));
  const nouveaux = (annee) => moteur.affiliations.regimes(cumul.affiliation, annee)
    .filter(unite).some((code) => !liquides.has(code));
  const periodes = [];
  const ouverts = [];
  for (let r = cumul.debut.rang; r < cumul.fin.rang; r += 1) {
    const mois = DateMois.depuisRang(r);
    const [leMotif, regle] = motif(mois, premiere, cumul.integral_depuis, sixMois, militaire,
      nouveaux(mois.annee));
    if (leMotif === NOUVELLE_PENSION) ouverts.push(mois);
    const derniere = periodes[periodes.length - 1];
    if (derniere !== undefined && derniere.motif === leMotif && derniere.regle === regle) {
      periodes[periodes.length - 1] = new PeriodeDeDroits(derniere.debut, mois.plusMois(1),
        leMotif, regle);
    } else {
      periodes.push(new PeriodeDeDroits(mois, mois.plusMois(1), leMotif, regle));
    }
  }
  const pensions = [];
  const nonCalcules = new Set();
  if (ouverts.length > 0) {
    const dateEffet = cumul.fin.rang >= LIQUIDATION_2023 ? cumul.fin
      : DateMois.depuisRang(LIQUIDATION_2023);
    const revenus = new Map();
    for (const ligne of carriere.lignes_apres_depart) {
      revenus.set(ligne.annee, (revenus.get(ligne.annee) ?? 0.0) + ligne.revenu);
    }
    const activite = new Map();
    for (let r = cumul.debut.rang; r < cumul.fin.rang; r += 1) {
      const annee = DateMois.depuisRang(r).annee;
      activite.set(annee, (activite.get(annee) ?? 0) + 1);
    }
    const periode = new Map();
    for (const mois of ouverts) periode.set(mois.annee, (periode.get(mois.annee) ?? 0) + 1);
    // Le salaire de chaque année, sur ses seuls mois de la période.
    const annees = [...periode.keys()].sort((a, b) => a - b);
    const salaires = new Map(annees.map((annee) => [annee,
      (revenus.get(annee) ?? 0.0) / activite.get(annee) * periode.get(annee)]));
    const regimes = new Set();
    for (const annee of periode.keys()) {
      for (const code of moteur.affiliations.regimes(cumul.affiliation, annee)) regimes.add(code);
    }
    const basesActivite = [...regimes].filter(unite).sort();
    for (const code of basesActivite) {
      if (!REGIMES_CALCULES.has(code)) {
        nonCalcules.add(code);
        continue;
      }
      const pension = nouvellePension(moteur, code, salaires, periode, dateEffet,
        resultat.trimestres_requis, premiere.rang < PREMIERE_2027);
      if (pension !== null) pensions.push(pension);
    }
    if (regimes.has(AGIRC_ARRCO)) {
      const pension = secondeRetraiteComplementaire(moteur, salaires, periode,
        dateEffet.rang >= LIQUIDATION_AGIRC_ARRCO ? dateEffet
          : DateMois.depuisRang(LIQUIDATION_AGIRC_ARRCO));
      if (pension !== null) pensions.push(pension);
    }
  }
  return new DroitsApresDepart({ periodes, pensions, nonCalcules: [...nonCalcules].sort() });
}

/**
 * La nouvelle pension d'un régime aligné : le salaire mensuel moyen des années
 * qui valident un trimestre (R. 351-29, III), revalorisé et écrêté au plafond,
 * au taux plein, proratisé par la durée requise.
 */
function nouvellePension(moteur, code, salaires, periode, dateEffet, requis, plafonnee) {
  const macro = moteur.macro;
  let trimestres = 0;
  let total = 0.0;
  let mois = 0;
  for (const [annee, salaire] of salaires) {
    const valides = Math.min(4, Math.floor(
      salaire / (HEURES_PAR_TRIMESTRE * macro.smic_horaire.valeur(annee)) + 1e-9));
    if (valides < 1) continue;
    trimestres += valides;
    const plafonne = Math.min(salaire,
      macro.plafond_securite_sociale.valeur(annee) * periode.get(annee) / 12.0);
    total += plafonne * macro.coefficientRevalorisationPorteeAuCompte(
      annee, dateEffet.annee, dateEffet.mois);
    mois += periode.get(annee);
  }
  if (trimestres === 0 || mois === 0 || requis <= 0) return null;
  const salaireMensuel = total / mois;
  const brute = salaireMensuel * 12.0 * TAUX_PLEIN * Math.min(1.0, trimestres / requis);
  const plafond = plafonnee
    ? PLAFOND_EN_PASS * macro.plafond_securite_sociale.valeur(dateEffet.annee) : null;
  const montant = plafond === null ? brute : Math.min(brute, plafond);
  return new NouvellePension({ regime: code, dateEffet, trimestres, salaireMensuel,
    points: 0.0, brute, plafond, montant });
}

/**
 * Le prix d'achat d'un point de l'Agirc-Arrco : le salaire de référence et le
 * taux d'appel de l'année ; au-delà du dernier publié, celui que le texte
 * prolonge sur le salaire moyen, comme pour la première pension. Voir
 * seconde.py.
 */
function prixDuPoint(moteur, annee) {
  const achat = moteur.valeursPoint.achatProlonge(AGIRC_ARRCO, annee, moteur.macro);
  if (achat === null) {
    return null;
  }
  const [reference, tauxAppel] = achat;
  return [reference, tauxAppel];
}

/**
 * Les points de la tranche 1 acquis en cumul intégral depuis 2023, et la
 * seconde retraite qu'ils servent, sans coefficient.
 */
function secondeRetraiteComplementaire(moteur, salaires, periode, dateEffet) {
  const macro = moteur.macro;
  let points = 0.0;
  for (const [annee, salaire] of salaires) {
    const plafond = macro.plafond_securite_sociale.valeur(annee);
    const tranche1 = moteur.catalogue.obtenir(AGIRC_ARRCO).periodesActives(annee)
      .find((p) => p.bornesAssietteEnEuros(plafond)[0] === 0);
    const prix = prixDuPoint(moteur, annee);
    if (tranche1 === undefined || prix === null) continue;
    const [reference, tauxAppel] = prix;
    const assiette = Math.min(salaire, plafond * periode.get(annee) / 12.0);
    // Au taux de calcul des points, comme la première pension : voir seconde.py.
    const tauxCalcul = tranche1.taux_calcul_points ?? null;
    points += tauxCalcul !== null ? assiette * tauxCalcul / reference
      : assiette * tranche1.taux_cotisation_retraite / (tauxAppel * reference);
  }
  const valeur = valeurDuPoint(moteur, AGIRC_ARRCO, dateEffet);
  if (points <= 0 || valeur === null) return null;
  const montant = points * valeur[0];
  return new NouvellePension({ regime: AGIRC_ARRCO, dateEffet, trimestres: 0,
    salaireMensuel: 0.0, points, brute: montant, plafond: null, montant });
}

/** Ce qui ouvre des droits dans les régimes qui ne servent pas de pension. */
export const OUVRANTS = new Set([REGIMES_NON_LIQUIDES, PENSION_MILITAIRE]);

/**
 * Les pensions que les années d'activité ouvrent dans les régimes qui n'en
 * servent pas encore, liquidées à leur date : `[date, liquidation]` pour
 * chaque départ. Voir le Python.
 */
export function liquiderLesRegimesNouveaux(moteur, carriere, resultat, droits, cumul,
  contexte, journal = null) {
  if (droits === null || droits === undefined || cumul === null) return [];
  const annees = new Set();
  for (const periode of droits.periodes) {
    if (!OUVRANTS.has(periode.motif)) continue;
    for (let r = periode.debut.rang; r < periode.fin.rang; r += 1) {
      annees.add(DateMois.depuisRang(r).annee);
    }
  }
  const lignes = carriere.lignes_apres_depart.filter((ligne) => annees.has(ligne.annee));
  if (lignes.length === 0) return [];
  const etendue = carriere.avecLignes(
    [...carriere.lignes, ...lignes].sort((a, b) => a.annee - b.annee),
  ).liquideeAu(cumul.fin);
  const liquides = new Set(resultat.pensions_par_regime.map((p) => p.regime));
  const [bases, suivies] = lesDeparts.regimesDeLaCarriere(moteur, etendue);
  const nouveaux = new Set([...bases, ...suivies.keys()].filter((code) => !liquides.has(code)));
  if (nouveaux.size === 0) return [];
  const parDate = new Map();
  for (const depart of lesDeparts.departs(moteur, etendue)) {
    const ici = depart.unique ? [...nouveaux]
      : [...depart.regimes].filter((code) => nouveaux.has(code));
    if (ici.length === 0) continue;
    if (!parDate.has(depart.date.rang)) parDate.set(depart.date.rang, new Set());
    for (const code of ici) parDate.get(depart.date.rang).add(code);
  }
  const liquidations = [];
  for (const rangDate of [...parDate.keys()].sort((a, b) => a - b)) {
    const date = DateMois.depuisRang(rangDate);
    const menes = menerAuMois(moteur, resultat.pensions_par_regime,
      carriere.dateLiquidation, date);
    const servies = resultat.pensions_par_regime.map((pension, i) => ({
      regime: pension.regime, montant: menes[i] }));
    const demande = new liquidation.Demande({
      personne: carriere.personne, dateEffet: jour(date), dateEvenement: jour(date),
      regimes: [...parDate.get(rangDate)].sort(),
    });
    const etat = new liquidation.Etat(etendue.liquideeAu(date), journal, servies);
    liquidations.push([date, liquidation.liquider(demande, etat, contexte)]);
  }
  return liquidations;
}
