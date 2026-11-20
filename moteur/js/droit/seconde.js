/**
 * Les droits de l'activité exercée après le départ (docs/architecture.md,
 * § 7.4 ; fiches `droits_apres_la_premiere_pension` et `seconde_pension`).
 *
 * Après une première pension de base, l'activité n'ouvre plus aucun
 * droit, pour qui la prend depuis 2015, puis pour tous depuis 2023, sauf, en
 * cumul intégral, une nouvelle pension dans le régime de base de l'activité
 * — au taux plein, plafonnée à 5 % du plafond de la sécurité sociale avant les
 * premières pensions de 2027 —, une seconde retraite de l'Agirc-Arrco, sur
 * les points de la tranche 1, et une du RCI, sur les périodes de 2025 et après.
 *
 * Les dates et le plafond de ces règles ne s'écrivent pas ici : le module lit,
 * dans le paquet (`fiches_datees`), la version de chaque fiche qui vaut aux
 * dates qui décident (action 191, étape 2 du domaine du cumul).
 */

import { DateMois, MOIS_PAR_AN, trimestresCivils } from "../calendrier.js";
import { AnneeCarriere, forfaitMicro, revenuCotise } from "../carriere.js";
import { menerAuMois } from "../revalorisation.js";
import { assietteMinimale } from "./acquerir.js";
import * as lesDeparts from "./departs.js";
import * as liquidation from "./liquidation.js";
import { valeurDuPoint } from "./liquider.js";
import { dateDEffet } from "./commun.js";
import { FICHE_DU_VERSEMENT_RCI, salaireDeReferencePoints } from "./completer.js";
import { FONCTION_PUBLIQUE, fonctionPubliqueQuittee, jour } from "./cumul.js";

/** Ce que le droit fait d'un mois d'activité après le départ. */
export const NOUVELLE_PENSION = "nouvelle_pension";
export const ETEINTS = "eteints";
export const DERNIER_EMPLOYEUR = "dernier_employeur";
export const REGIMES_NON_LIQUIDES = "regimes_non_liquides";
export const REGIME_LIQUIDE = "regime_liquide";
export const PENSION_MILITAIRE = "pension_militaire";

/** Les deux fiches que le module lit, et que le paquet porte (`fiches_datees`). */
export const FICHE_DES_DROITS = "droits_apres_la_premiere_pension";
export const FICHE_DE_LA_SECONDE_PENSION = "seconde_pension";

/** Les versions de la fiche `droits_apres_la_premiere_pension`. */
export const SANS_REGLE_GENERALE = "sans_regle_generale";
export const LOI_2014 = "loi_2014";
export const LOI_2023 = "loi_2023";
export const LFSS_2026 = "lfss_2026";

/** Les dates qui décident des versions des deux fiches. */
const DATE_PREMIERE_PENSION = "liquidation.premiere_pension_de_base";
const DATE_DU_DROIT = "droit_acquis";
const DATE_D_EFFET = "liquidation.date_effet";

/** Ce que les versions de la fiche des droits disent des droits nouveaux. */
const SELON_LE_REGIME = "selon_le_regime";
const AUCUN = "aucun";
/** Les exceptions qui ouvrent une nouvelle pension, et celle du militaire. */
const CUMULS_QUI_OUVRENT = ["cumul_integral", "cumul_entier"];
const EXCEPTION_MILITAIRE = "pension_militaire";

export const TAUX_PLEIN = 0.5;
export const HEURES_PAR_TRIMESTRE = 150;
export const REGIMES_CALCULES = new Set(["regime_general", "msa_salaries"]);
export const AGIRC_ARRCO = "agirc_arrco";
export const RCI = "rci";
/** Le groupe de l'activité des artisans, des commerçants et des micro-entrepreneurs. */
export const INDEPENDANTS = "independants";

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
    montant, revenuAnnuelMoyen = 0.0, capital = null }) {
    this.regime = regime;
    this.date_effet = dateEffet;
    this.trimestres = trimestres;
    this.salaire_mensuel = salaireMensuel;
    this.points = points;
    this.brute = brute;
    this.plafond = plafond;
    this.montant = montant;
    this.revenu_annuel_moyen = revenuAnnuelMoyen;
    /** Le versement forfaitaire unique qui la remplace, ou `null` (fiche `versement_unique_rci`). */
    this.capital = capital;
  }

  donnees() {
    return { regime: this.regime, date_effet: jour(this.date_effet),
      trimestres: this.trimestres, salaire_mensuel: this.salaire_mensuel,
      revenu_annuel_moyen: this.revenu_annuel_moyen,
      points: this.points, brute: this.brute, plafond: this.plafond,
      montant: this.montant, capital: this.capital };
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

/** Le mois d'un jour AAAA-MM-JJ, que porte une borne ou un paramètre de fiche. */
const moisDuJour = (texte) => new DateMois(Number(texte.slice(0, 4)), Number(texte.slice(5, 7)));

/**
 * La fiche `nom`, telle que le paquet la porte. Sans elle, le paquet est
 * périmé et le calcul s'arrête : un droit ne s'ouvre ni ne se refuse par
 * défaut.
 */
function fiche(moteur, nom) {
  const fiches = moteur.fichesDatees.fiches();
  if (!(nom in fiches)) {
    throw new Error(`${nom} : la fiche manque au paquet, que `
      + "scripts/construire_donnees.py refait");
  }
  return fiches[nom];
}

/**
 * La version de la fiche des droits qui vaut pour une première pension de
 * base prise à `premiere` et un mois d'activité `mois` : ses deux dates qui
 * décident. Aucune version à ces dates arrête le calcul.
 */
export function versionDesDroits(moteur, premiere, mois) {
  fiche(moteur, FICHE_DES_DROITS);
  const version = moteur.fichesDatees.versionAuxDates(FICHE_DES_DROITS,
    { [DATE_PREMIERE_PENSION]: jour(premiere), [DATE_DU_DROIT]: jour(mois) });
  if (version === null) {
    throw new Error(`${FICHE_DES_DROITS} : aucune version pour une première pension du `
      + `${jour(premiere)} et un droit du ${jour(mois)}`);
  }
  return version;
}

/**
 * Ce que le droit fait d'un mois d'activité, et la version qui le dit : celle
 * de la fiche des droits qui vaut ce mois-là pour cette première pension,
 * dont les paramètres disent si l'activité ouvre des droits, et par quelles
 * exceptions.
 *
 * Le titulaire d'une pension militaire garde ses droits sous toutes les
 * versions : la règle de ses mois est, comme pour tous, celle qui vaut pour
 * sa première pension.
 */
export function motif(moteur, mois, premiere, integral, sixMois, militaire, nouveaux) {
  const version = versionDesDroits(moteur, premiere, mois);
  if (militaire) return [PENSION_MILITAIRE, version.id];
  const { droits_nouveaux: droitsNouveaux, exceptions = [] } = version.parametres;
  if (droitsNouveaux !== SELON_LE_REGIME && droitsNouveaux !== AUCUN) {
    throw new Error(`${FICHE_DES_DROITS} : droits nouveaux « ${droitsNouveaux} » `
      + "inconnus du moteur");
  }
  // Chaque régime garde ses règles : celui qui n'a rien liquidé ouvre ses droits.
  const selonLeRegime = droitsNouveaux === SELON_LE_REGIME;
  if (selonLeRegime && nouveaux) return [REGIMES_NON_LIQUIDES, version.id];
  // Sinon, seul un cumul que la version excepte ouvre une nouvelle pension.
  const ferme = selonLeRegime ? REGIME_LIQUIDE : ETEINTS;
  if (!CUMULS_QUI_OUVRENT.some((exception) => exceptions.includes(exception))) {
    return [ferme, version.id];
  }
  if (sixMois) return [DERNIER_EMPLOYEUR, version.id];
  if (integral !== null && mois.rang >= integral.rang) return [NOUVELLE_PENSION, version.id];
  return [ferme, version.id];
}

/**
 * La règle de la nouvelle pension qui prend effet à `dateEffet`, pour une
 * première pension de base prise à `premiere` : les paramètres de la version
 * de sa fiche qui vaut à ces deux dates ; sans version, aucun droit.
 */
export function regleDeLaNouvellePension(moteur, dateEffet, premiere) {
  fiche(moteur, FICHE_DE_LA_SECONDE_PENSION);
  const version = moteur.fichesDatees.versionAuxDates(FICHE_DE_LA_SECONDE_PENSION,
    { [DATE_D_EFFET]: jour(dateEffet), [DATE_PREMIERE_PENSION]: jour(premiere) });
  return version === null ? { existe: false } : { ...version.parametres };
}

/**
 * La date d'effet de la nouvelle pension d'une activité qui cesse à `fin` :
 * cette date, ou la première qui la suit dont la version ouvre le droit — la
 * fin de la version sans droit, que la fiche borne. `null` si aucune ne
 * l'ouvre.
 */
export function effetDeLaNouvellePension(moteur, fin, premiere) {
  fiche(moteur, FICHE_DE_LA_SECONDE_PENSION);
  const dates = (effet) => (
    { [DATE_D_EFFET]: jour(effet), [DATE_PREMIERE_PENSION]: jour(premiere) });
  let effet = fin;
  for (;;) {
    const version = moteur.fichesDatees.versionAuxDates(FICHE_DE_LA_SECONDE_PENSION,
      dates(effet));
    if (version === null) return null;
    if (version.parametres.existe) return effet;
    const suivante = version.bornes[DATE_D_EFFET]?.[1] ?? null;
    if (suivante === null) return null;
    effet = moisDuJour(suivante);
  }
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
    const [leMotif, regle] = motif(moteur, mois, premiere, cumul.integral_depuis, sixMois,
      militaire, nouveaux(mois.annee));
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
  const dateEffet = ouverts.length > 0
    ? effetDeLaNouvellePension(moteur, cumul.fin, premiere) : null;
  if (dateEffet !== null) {
    const regle = regleDeLaNouvellePension(moteur, dateEffet, premiere);
    const auPlusTot = (texte) => {
      const borne = moisDuJour(texte);
      return dateEffet.rang >= borne.rang ? dateEffet : borne;
    };
    const lignes = carriere.lignes_apres_depart;
    const activite = new Map();
    for (let r = cumul.debut.rang; r < cumul.fin.rang; r += 1) {
      const annee = DateMois.depuisRang(r).annee;
      activite.set(annee, (activite.get(annee) ?? 0) + 1);
    }
    const periode = new Map();
    for (const mois of ouverts) periode.set(mois.annee, (periode.get(mois.annee) ?? 0) + 1);
    // Le salaire de chaque année, sur ses seuls mois de la période : celui que
    // `code` cotise (`revenus`).
    const annees = [...periode.keys()].sort((a, b) => a - b);
    const salaires = (code = null) => {
      const parAnnee = revenus(moteur, lignes, code);
      return new Map(annees.map((annee) => [annee,
        (parAnnee.get(annee) ?? 0.0) / activite.get(annee) * periode.get(annee)]));
    };
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
      const pension = nouvellePension(moteur, code, salaires(code), periode, dateEffet,
        resultat.trimestres_requis, regle, cumul.groupe === INDEPENDANTS);
      if (pension !== null) pensions.push(pension);
    }
    if (regimes.has(AGIRC_ARRCO)) {
      // La deuxième pension de l'Agirc-Arrco « prend effet, au plus tôt », à la
      // date que porte la version (accord du 17 novembre 2017, article 91).
      const pension = secondeRetraiteComplementaire(moteur, salaires(), periode,
        auPlusTot(regle.agirc_arrco_effet_au_plus_tot));
      if (pension !== null) pensions.push(pension);
    }
    if (regimes.has(RCI)) {
      // Le RCI n'ouvre de droits au retraité en cumul intégral que depuis la
      // date que porte la version (règlement du RCI, articles 4 et 27).
      const depuis = moisDuJour(regle.rci_droits_depuis);
      const pension = secondeRetraiteRci(moteur, lignes, activite, periode,
        auPlusTot(regle.rci_droits_depuis), depuis.annee);
      if (pension !== null) pensions.push(pension);
    }
  }
  return new DroitsApresDepart({ periodes, pensions, nonCalcules: [...nonCalcules].sort() });
}

/**
 * Le revenu de chaque année de l'activité, que la ligne déclare ; celui du
 * micro-entrepreneur, que son forfait cotise. Avec `code`, celui sur lequel ce
 * régime de base a cotisé : l'assiette minimale de l'artisan et du commerçant
 * qui déclare moins (D. 633-2), dont rien ne dispense le pensionné. Voir
 * `_revenus` (seconde.py).
 */
function revenus(moteur, lignes, code = null) {
  const parAnnee = new Map();
  for (const ligne of lignes) {
    let revenu;
    if (ligne.micro) {
      revenu = revenuCotise(moteur.macro, ligne.revenu, ligne.micro, ligne.annee,
        ligne.fraction_annee);
    } else if (code === null) {
      revenu = ligne.revenu;
    } else {
      revenu = Math.max(ligne.revenu, assietteMinimale(moteur, [code], ligne));
    }
    parAnnee.set(ligne.annee, (parAnnee.get(ligne.annee) ?? 0.0) + revenu);
  }
  return parAnnee;
}

/**
 * La nouvelle pension d'un régime aligné : le salaire mensuel moyen des années
 * qui valident un trimestre (R. 351-29, III), revalorisé et écrêté au plafond,
 * au taux plein, proratisé par la durée requise, et écrêté au plafond que
 * porte `regle`, les paramètres de la version de la fiche
 * (`regleDeLaNouvellePension`). `annuel` : celle de l'indépendant, sur le
 * revenu annuel moyen de ces années, l'année de l'effet comprise (R. 634-1,
 * puis D. 634-3).
 */
export function nouvellePension(moteur, code, salaires, periode, dateEffet, requis, regle,
  annuel = false) {
  const macro = moteur.macro;
  let trimestres = 0;
  let total = 0.0;
  let mois = 0;
  let annees = 0;
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
    annees += 1;
  }
  if (trimestres === 0 || mois === 0 || requis <= 0) return null;
  const salaireMensuel = annuel ? 0.0 : total / mois;
  const revenuAnnuelMoyen = annuel ? total / annees : 0.0;
  const base = annuel ? revenuAnnuelMoyen : salaireMensuel * 12.0;
  const brute = base * TAUX_PLEIN * Math.min(1.0, trimestres / requis);
  const enPass = regle.plafond_en_pass ?? null;
  const plafond = enPass === null
    ? null : enPass * macro.plafond_securite_sociale.valeur(dateEffet.annee);
  const montant = plafond === null ? brute : Math.min(brute, plafond);
  return new NouvellePension({ regime: code, dateEffet, trimestres, salaireMensuel,
    points: 0.0, brute, plafond, montant, revenuAnnuelMoyen });
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
      .find((p) => p.bornesAssietteEnEuros(plafond, annee)[0] === 0);
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

/**
 * La seconde retraite du RCI : les points que les cotisations des mois de
 * cumul intégral achètent depuis `anneeDesDroits`, servis sans coefficient,
 * à la date de la nouvelle pension de base (règlement du RCI, article 27) ;
 * ceux de la première pension, sur le revenu déclaré, ou la part
 * complémentaire du forfait du micro-entrepreneur ; sous quarante points, un
 * versement forfaitaire unique la remplace (article 39). Voir seconde.py.
 */
function secondeRetraiteRci(moteur, lignes, activite, periode, dateEffet, anneeDesDroits) {
  const macro = moteur.macro;
  let points = 0.0;
  for (const ligne of lignes) {
    const annee = ligne.annee;
    if (annee < anneeDesDroits || !periode.has(annee)) continue;
    const achat = moteur.valeursPoint.achatProlonge(RCI, annee, macro);
    if (achat === null) continue;
    const [reference, tauxAppel] = achat;
    // La part de l'année que la période garde, et le revenu de ses mois.
    const part = periode.get(annee) / activite.get(annee);
    const forfait = ligne.micro ? forfaitMicro(macro, ligne.micro, annee) : null;
    let cotisation = 0.0;
    if (forfait !== null) {
      const [[, complementaire], [, tauxComplementaire]] = forfait;
      cotisation = complementaire === RCI ? ligne.revenu * tauxComplementaire * part : 0.0;
    } else {
      const plafond = macro.plafond_securite_sociale.valeur(annee);
      const fraction = periode.get(annee) / 12.0;
      const revenu = ligne.revenu * part;
      for (const tranche of moteur.catalogue.obtenir(RCI).periodesActives(annee)) {
        const [basse, haute] = tranche.bornesAssietteEnEuros(plafond, annee);
        const plafonne = haute === null ? revenu : Math.min(revenu, haute * fraction);
        cotisation += Math.max(0.0, plafonne - basse * fraction)
          * tranche.taux_cotisation_retraite;
      }
    }
    points += cotisation / (tauxAppel * reference);
  }
  const valeur = valeurDuPoint(moteur, RCI, dateEffet);
  if (points <= 0 || valeur === null) return null;
  const montant = points * valeur[0];
  let capital = null;
  const regle = moteur.fichesDatees.regle(FICHE_DU_VERSEMENT_RCI, jour(dateEffet));
  if (regle !== null && regle.existe && points < Number(regle.seuil_points)) {
    const reference = salaireDeReferencePoints(moteur, regle.point, dateEffet.annee);
    if (reference !== null) capital = points * reference[0];
  }
  return new NouvellePension({ regime: RCI, dateEffet, trimestres: 0,
    salaireMensuel: 0.0, points, brute: montant, plafond: null, montant, capital });
}

/** Ce qui ouvre des droits dans les régimes qui ne servent pas de pension. */
export const OUVRANTS = new Set([REGIMES_NON_LIQUIDES, PENSION_MILITAIRE]);

/**
 * Les lignes de l'activité que comptent les régimes qui s'ouvrent : celles des
 * années dont des mois ouvrent des droits, chacune sur ces seuls mois. L'année
 * que la règle coupe — 2023, pour une première pension d'avant 2015 — garde
 * son revenu au prorata de ces mois et, comme l'année d'un départ, leurs seuls
 * trimestres civils entiers.
 */
export function lignesQuiOuvrent(lignes, periodes) {
  const ouvrants = new Map();
  for (const periode of periodes) {
    if (!OUVRANTS.has(periode.motif)) continue;
    for (let r = periode.debut.rang; r < periode.fin.rang; r += 1) {
      const { annee } = DateMois.depuisRang(r);
      ouvrants.set(annee, (ouvrants.get(annee) ?? 0) + 1);
    }
  }
  return lignes.filter((ligne) => ouvrants.has(ligne.annee)).map((ligne) => {
    const mois = ouvrants.get(ligne.annee);
    const travailles = Math.round(ligne.fraction_annee * MOIS_PAR_AN);
    if (mois >= travailles) return ligne;
    const part = mois / travailles;
    return new AnneeCarriere({
      ...ligne, fraction_annee: mois / MOIS_PAR_AN, revenu: ligne.revenu * part,
      revenu_reference: ligne.revenu_reference * part,
      revenu_avpf: ligne.revenu_avpf * part, revenu_retabli: ligne.revenu_retabli * part,
      trimestres_valides: Math.min(ligne.trimestres_valides, trimestresCivils(mois)),
    });
  });
}

/**
 * Les pensions que les années d'activité ouvrent dans les régimes qui n'en
 * servent pas encore, liquidées à leur date : `[date, liquidation]` pour
 * chaque départ. Voir le Python.
 */
export function liquiderLesRegimesNouveaux(moteur, carriere, resultat, droits, cumul,
  contexte, journal = null) {
  if (droits === null || droits === undefined || cumul === null) return [];
  const lignes = lignesQuiOuvrent(carriere.lignes_apres_depart, droits.periodes);
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
      regime: pension.regime, montant: menes[i],
      date_effet: pension.date_effet ?? dateDEffet(carriere) }));
    const demande = new liquidation.Demande({
      personne: carriere.personne, dateEffet: jour(date), dateEvenement: jour(date),
      regimes: [...parDate.get(rangDate)].sort(),
    });
    const etat = new liquidation.Etat(etendue.liquideeAu(date), journal, servies);
    liquidations.push([date, liquidation.liquider(demande, etat, contexte)]);
  }
  return liquidations;
}
