/**
 * Compléter tous régimes (docs/architecture.md, § 7.3).
 *
 * Jumeau de `src/retraite_notionnelle/droit/completer.py`, fonction pour
 * fonction : ce que le droit ajoute aux pensions de régime en les regardant
 * toutes ensemble, dans l'ordre où il l'applique — le minimum contributif et
 * son écrêtement (`complementMinimum`), le minimum garanti de la fonction
 * publique, la surcote parentale, la majoration pour enfants, plafonnée en
 * euros à la complémentaire (`plafondMajoration`) et au traitement dans les
 * régimes du code des pensions (`majorationSousLeTraitement`), les deux minima des
 * exploitants agricoles (`pensionMajoree`, `complementDifferentiel`), les
 * versements uniques enfin, qui remplacent les petites pensions par un capital
 * (`verserEnCapital`). L'ASPA n'en est pas :
 * c'est l'étape « foyer et net » (`foyer.js`). Ce que l'étape écrit,
 * `Complements`, suit son schéma, `data/reference/etapes/completer_tous_regimes.yaml`.
 */

import { DateMois } from "../calendrier.js";
import { formatFixe, formatPourcentage } from "../format.js";
import { Fiabilite, fiabiliteDepuisTexte, nomFiabilite } from "../serie.js";
import { dateDEffet, derniereAnnee, ligneCotisee } from "./commun.js";
import { pointsGratuits } from "./acquerir.js";
import { trimestresDeLaLigneEntre } from "./compter.js";
import * as etranger from "./etranger.js";
import * as liquider from "./liquider.js";
import * as ouvrir from "./ouvrir.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

/** La fiche de la carte que chaque dispositif applique. */
export const FICHES = {
  minimum_contributif: "minimum_contributif",
  minimum_garanti: "minimum_garanti",
  surcote_parentale: "surcote_parentale",
  majoration_enfants: "majoration_dix_pour_cent",
  pension_majoree_reference: "pension_majoree_reference",
  complement_differentiel_rco: "complement_differentiel_rco",
};

/** Le régime de la retraite complémentaire des non-salariés agricoles. */
export const RCO = "msa_rco";

/** Les heures de SMIC d'une année, que le complément de la RCO multiplie. */
export const HEURES_DU_COMPLEMENT = 1820;

/**
 * Les points de RCO d'une carrière complète au minimum, que la formule du
 * complément retranche de 2015 à octobre 2021 (D. 732-166-4).
 */
export const POINTS_D_UNE_CARRIERE_COMPLETE = 3750;

/**
 * La fiche du plafond de L. 18, que `FichesDatees` lit à la date d'effet
 * (`plafondDeLArticleL18`).
 */
export const FICHE_DU_PLAFOND_L18 = "majoration_enfants_plafond_fonction_publique";

/** Les plafonds qu'une version de cette fiche peut nommer : le traitement. */
export const PLAFONDS_DE_L18 = ["traitement"];

/**
 * Ce qu'elle peut dire de la surcote : comptée dans la pension qu'on compare au
 * traitement, ou laissée hors du plafond et servie au-delà (Conseil d'État,
 * 29 décembre 2020, n° 428626).
 */
export const SURCOTES_DE_L18 = ["dans_le_plafond", "hors_du_plafond"];

/**
 * Les fiches des versements uniques, que `FichesDatees` lit à la date d'effet
 * (`verserEnCapital`) : le régime général, l'Agirc-Arrco et ses deux
 * devancières, l'Ircantec.
 */
export const FICHE_DU_VERSEMENT_FORFAITAIRE = "versement_forfaitaire_unique";
export const FICHE_DU_VERSEMENT_AGIRC_ARRCO = "versement_unique_agirc_arrco";
export const FICHE_DU_VERSEMENT_IRCANTEC = "versement_unique_ircantec";

/**
 * Ce à quoi une version de l'Agirc-Arrco compare son seuil : le nombre de points
 * de l'allocation (avant 2019), ou son montant, coefficients et majorations
 * compris (accord du 17 novembre 2017, article 107).
 */
export const MESURES_DU_VERSEMENT = ["points", "montant"];

/**
 * La version du plafond de L. 18 qui vaut à la date d'effet de la pension ;
 * null quand aucun plafond ne la borne. Un plafond ou une surcote que le moteur
 * ne connaît pas l'arrête. Voir `plafond_de_l_article_l18` du Python.
 */
export function plafondDeLArticleL18(moteur, carriere) {
  const version = moteur.fichesDatees.version(
    FICHE_DU_PLAFOND_L18, dateDEffet(carriere) ?? ouvrir.SANS_DATE_D_EFFET);
  if (version === null || !version.parametres.existe) {
    return null;
  }
  const parametres = version.parametres;
  if (!PLAFONDS_DE_L18.includes(parametres.plafond)) {
    throw new Error(`${FICHE_DU_PLAFOND_L18}.${version.id} : plafond inconnu, `
      + `${JSON.stringify(parametres.plafond)}`);
  }
  if (!SURCOTES_DE_L18.includes(parametres.surcote)) {
    throw new Error(`${FICHE_DU_PLAFOND_L18}.${version.id} : surcote inconnue, `
      + `${JSON.stringify(parametres.surcote)}`);
  }
  return version;
}

/**
 * La majoration pour enfants d'une pension du code des pensions, sous le
 * plafond de L. 18, V : elle cède seule, la pension jamais ; hors du plafond,
 * la pension se compare au traitement sans sa surcote, servie au-delà. Voir
 * `majoration_sous_le_traitement` du Python.
 */
export function majorationSousLeTraitement(montant, majoration, traitement, surcote,
  horsDuPlafond) {
  const base = horsDuPlafond ? montant - surcote : montant;
  return Math.max(0.0, Math.min(majoration, traitement - base));
}

/**
 * Ce que la pension majorée de référence (PMR) ajoute à la pension de base des
 * non-salariés agricoles ; null quand elle n'y ajoute rien. La PMR de la date
 * d'effet au prorata de la durée sur DR, au taux plein, comparée avant surcote
 * et sans la majoration pour enfants, écrêtée de ce que `ressources` — toutes
 * les pensions et majorations pour enfants — dépassent du plafond. Voir
 * `pension_majoree` du Python.
 */
export function pensionMajoree(moteur, carriere, eligible, pension, ressources) {
  const regle = moteur.pensionMajoreeReference.regle(dateDEffet(carriere));
  if (!regle.existe || !eligible.tauxPlein || pension.montant <= 0.0) {
    return null;
  }
  const duree = eligible.duree + (regle.majorations_de_duree ? eligible.enfants : 0);
  if (duree < (regle.duree_minimale ?? 0)) {
    return null;
  }
  // De 2009 à 2021, PMR1 pour qui a été chef d'exploitation dix-sept ans et
  // demi, PMR2 sinon (D. 732-110, II ; D. 732-111).
  let serie = regle.montant;
  if (regle.montant_reduit && eligible.duree < (regle.seuil_chef ?? 0)) {
    serie = regle.montant_reduit;
  }
  const annee = carriere.anneeLiquidation;
  const mois = carriere.moisLiquidation;
  const lu = moteur.pensionMajoreeReference.montant(serie, annee, mois);
  if (lu === null) {
    return null;
  }
  const [entiere, fiabilite] = lu;
  const retenue = Math.min(duree, eligible.reference);
  const avant = Math.max(0.0, entiere * retenue / eligible.reference
    - pension.montant / eligible.surcote);
  if (avant <= 0.0) {
    return null;
  }
  let plafond;
  let fiabilitePlafond;
  if (regle.plafond === "minimum_contributif") {
    [, , plafond, fiabilitePlafond] = moteur.minimumContributif.valeurs(annee, mois);
  } else {
    [plafond, fiabilitePlafond] = moteur.pensionMajoreeReference.montant(
      regle.plafond, annee, mois);
  }
  return {
    entiere, duree: retenue, reference: eligible.reference, avantEcretement: avant,
    complement: Math.max(0.0, Math.min(avant, plafond - ressources)),
    plafond, fiabilite: Math.min(fiabilite, fiabilitePlafond),
  };
}

/**
 * Les points de RCO que le complément différentiel ajoute (L. 732-63) ; null
 * quand il n'en ajoute pas. La cible, un pourcentage de 1 820 SMIC nets
 * agricoles, la formule de D. 732-166-4 — une carrière complète jusqu'en
 * octobre 2021, différentielle depuis —, le plafond des pensions agricoles
 * (D. 732-166-5) et, depuis novembre 2021, celui de toutes les pensions
 * personnelles, `personnelles` ; des points arrondis à l'entier le plus
 * proche. Voir `complement_differentiel` du Python.
 */
export function complementDifferentiel(moteur, carriere, eligible, base, rco, pointsRco,
  valeurPoint, personnelles, quand = null, smicLu = null, pmrLu = null) {
  // `quand`, `smicLu` et `pmrLu` lisent la règle, le SMIC net agricole et la PMR
  // du 1er septembre 2023, pour une pension prise avant que le taux plein ouvre
  // depuis (`releverLesExploitants`).
  const dateEffet = dateDEffet(carriere);
  const regle = moteur.complementDifferentielRco.regle(quand ?? dateEffet);
  if (!regle.existe || valeurPoint <= 0.0) {
    return null;
  }
  const duree = eligible.duree + (regle.majorations_de_duree ? eligible.enfants : 0);
  const ouvert = regle.condition === "taux_plein"
    ? eligible.tauxPlein : eligible.dureeRequiseAtteinte;
  if (duree < (regle.seuil_chef ?? 0) || !ouvert) {
    return null;
  }
  const annee = carriere.anneeLiquidation;
  const smic = smicLu ?? moteur.complementDifferentielRco.smicNet(annee);
  const pmr = pmrLu ?? moteur.pensionMajoreeReference.montant(
    moteur.pensionMajoreeReference.regle(dateEffet).montant || "pmr_chef",
    annee, regle.pmr_au_mois || 1);
  if (smic === null || pmr === null) {
    return null;
  }
  const [smicNet, fiabilite] = smic;
  const cible = regle.pourcentage * HEURES_DU_COMPLEMENT * smicNet;
  const retenue = Math.min(duree, eligible.reference);
  const prorata = retenue / eligible.reference;
  const formule = regle.formule === "carriere_complete"
    ? (cible - (pmr[0] + POINTS_D_UNE_CARRIERE_COMPLETE * valeurPoint)) * prorata
    : (cible - pmr[0]) * prorata - pointsRco * valeurPoint;
  let montant = Math.min(formule, cible * prorata - (base + rco));
  if (regle.plafond_tous_regimes) {
    montant = Math.min(montant, cible - personnelles);
  }
  montant = Math.max(0.0, montant);
  const points = Math.floor(montant / valeurPoint + 0.5 + 1e-9);
  if (points <= 0) {
    return null;
  }
  return {
    pourcentage: regle.pourcentage, smicNet, cible, duree: retenue,
    reference: eligible.reference, points, valeurPoint, montant: points * valeurPoint,
    plafonne: montant < formule - 1e-9, fiabilite: Math.min(fiabilite, pmr[1]),
  };
}

/**
 * Première date d'effet, [année, mois], où la surcote s'AJOUTE au minimum
 * contributif au lieu d'entrer dans la pension qu'on lui compare : décret
 * n° 2008-1509, dernier alinéa de D. 351-2-1.
 */
const SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS = [2009, 4];

/**
 * La majoration au titre des périodes cotisées est-elle due ? Pas avant 2004,
 * sans condition jusqu'en mars 2009, à 120 trimestres cotisés tous régimes
 * depuis — l'AVPF et l'AVA comprises depuis septembre 2023. Voir
 * `majoration_ouverte` du Python.
 */
export function majorationOuverte(regle, cotises) {
  if (regle.majoration === "aucune") {
    return false;
  }
  const seuil = regle.seuil_trimestres_cotises;
  return seuil === null || seuil === undefined || cotises >= seuil;
}

/**
 * Les trimestres d'AVPF et d'AVA que la majoration compte parmi les périodes
 * cotisées depuis le 1er septembre 2023, dans la limite de `plafond`, chaque
 * année dans la place que les trimestres cotisés laissent. Voir `avpf_retenue`
 * du Python.
 */
export function avpfRetenue(moteur, carriere, plafond) {
  if (!(plafond > 0)) {
    return 0;
  }
  const anneeLiquidation = carriere.anneeLiquidation;
  const cotises = carriere.trimestresParAnnee(carriere.lignes.filter(
    (ligne) => ligneCotisee(moteur, carriere, ligne) && ligne.annee <= anneeLiquidation));
  const avpf = carriere.trimestresParAnnee(carriere.lignes.filter(
    (ligne) => ligne.revenu_avpf > 0 && ligne.annee <= anneeLiquidation));
  let retenus = 0;
  for (const annee of [...avpf.keys()].sort((a, b) => a - b)) {
    const place = Math.max(0, carriere.plafondTrimestres(annee) - (cotises.get(annee) ?? 0));
    retenus = Math.min(plafond, retenus + Math.min(avpf.get(annee), place));
  }
  return retenus;
}

/**
 * Le minimum auquel la pension d'un régime est portée, majoration comprise :
 * au prorata de la durée du régime, ou, depuis 2004, de la durée tous régimes
 * quand elle dépasse la durée requise. Voir `plancher_du_regime` du Python.
 */
export function plancherDuRegime(eligible, montantBase, montantMajore, majoration,
  tousRegimes) {
  const dureeTotale = eligible.dureeTousRegimes ?? 0;
  if (tousRegimes && dureeTotale > eligible.requis && dureeTotale > eligible.dureeRegime) {
    const part = eligible.dureeRegime / dureeTotale;
    let plancher = montantBase * part;
    if (majoration) {
      plancher += (montantMajore - montantBase) * part
        * Math.min(1.0, eligible.cotiseeTousRegimes / eligible.proratisation);
    }
    return plancher;
  }
  let plancher = montantBase * Math.min(1.0, eligible.prorataAssurance);
  if (majoration) {
    plancher += (montantMajore - montantBase) * Math.min(1.0, eligible.prorataCotise);
  }
  return plancher;
}

/**
 * Les durées cotisées de l'éligible, telles que la majoration de cette date les
 * lit : la durée d'assurance de janvier 2004 à juin 2005, l'AVPF et l'AVA en
 * plus au régime général depuis septembre 2023. Voir `selon_la_regle` du
 * Python.
 */
export function selonLaRegle(eligible, regle, avpf) {
  if (regle.majoration === "sans_distinction") {
    return {
      ...eligible, cotiseeRegime: eligible.dureeRegime,
      prorataCotise: Math.min(1.0, eligible.prorataAssurance),
      cotiseeTousRegimes: eligible.dureeTousRegimes,
    };
  }
  if (avpf > 0 && eligible.porteAvpf) {
    const cotisee = eligible.cotiseeRegime + avpf;
    return {
      ...eligible, cotiseeRegime: cotisee,
      prorataCotise: Math.min(cotisee, eligible.proratisation) / eligible.proratisation,
      cotiseeTousRegimes: eligible.cotiseeTousRegimes + avpf,
    };
  }
  return eligible;
}

/**
 * La limitation du cumul des pensions portées au minimum, de décembre 1984 à
 * 2003 : leur total ne dépasse pas le minimum entier ; le régime de la plus
 * longue durée sert sa pension portée au minimum, les autres un complément
 * différentiel au prorata de leurs durées. Voir `limiter_le_cumul` du Python.
 */
export function limiterLeCumul(complements, pensions, eligibles, montantBase) {
  const portes = eligibles.filter((e) => complements.has(e.indice));
  if (portes.length < 2) {
    return complements;
  }
  const total = portes.reduce(
    (somme, e) => somme + pensions[e.indice].montant + complements.get(e.indice), 0.0);
  if (total <= montantBase) {
    return complements;
  }
  let premier = portes[0];
  for (const e of portes.slice(1)) {
    if (e.dureeRegime > premier.dureeRegime
        || (e.dureeRegime === premier.dureeRegime && e.indice > premier.indice)) {
      premier = e;
    }
  }
  const autres = portes.filter((e) => e !== premier);
  const marge = Math.max(0.0, montantBase - pensions[premier.indice].montant
    - complements.get(premier.indice)
    - autres.reduce((somme, e) => somme + pensions[e.indice].montant, 0.0));
  const duree = autres.reduce((somme, e) => somme + e.dureeRegime, 0);
  const limites = new Map(complements);
  for (const e of autres) {
    limites.set(e.indice, duree > 0
      ? Math.min(complements.get(e.indice), marge * e.dureeRegime / duree) : 0.0);
  }
  return limites;
}

/**
 * Le minimum d'une pension proratisée se proratise-t-il sur la durée totale non
 * limitée (fiche `minimum_contributif_international`, depuis 2004) ? Voir
 * `_minimum_international` du Python.
 */
function minimumInternational(moteur, carriere) {
  const version = moteur.carrieresHorsDeFrance.version(
    "minimum", { "liquidation.date_effet": dateDEffet(carriere) });
  return version !== null
    && version.parametres.prorata_du_minimum === "duree_totale_non_limitee";
}

/**
 * Le minimum d'une pension proratisée et sa majoration, théoriques puis
 * proratisés. Voir `plancher_international` du Python.
 */
export function plancherInternational(eligible, montantBase, montantMajore, dureeTotale,
  cotiseeTotale, majorationOuverte) {
  const maximum = eligible.proratisation;
  const dureeRegime = Math.min(eligible.dureeRegime, maximum);
  const theorique = montantBase * Math.min(1.0, dureeTotale / maximum);
  let plancher = theorique * dureeRegime / dureeTotale;
  if (majorationOuverte) {
    const majoration = montantMajore - montantBase;
    if (dureeTotale > eligible.requis) {
      plancher += majoration * Math.min(1.0, cotiseeTotale / maximum)
        * dureeRegime / dureeTotale;
    } else if (cotiseeTotale < maximum) {
      plancher += majoration * cotiseeTotale / maximum
        * dureeRegime / Math.min(dureeTotale, maximum);
    } else {
      plancher += majoration * Math.min(eligible.cotiseeRegime, maximum) / maximum;
    }
  }
  return plancher;
}

/** Ce que l'étape « compléter tous régimes » écrit. */
export class Complements {
  constructor({ personne, regimes, avantages, total, minimumApplique, fiabilite,
    plancher = 0.0, minimumEcrete = null, petitesPensions = [], chef = null }) {
    this.personne = personne;
    this.regimes = regimes;
    this.avantages = avantages;
    this.total = total;
    this.minimumApplique = minimumApplique;
    this.fiabilite = fiabilite;
    // Ce que la pension provisoire d'une retraite progressive ajoute à la
    // pension complète qui descendrait sous elle : un droit acquis, qui entre
    // au total contributif.
    this.plancher = plancher;
    // Le minimum contributif servi, et ce que sa révision relit après le
    // départ (R. 173-8) : `{avant_ecretement, marge, par_regime}`, en euros de
    // la liquidation ; `null` sans lui. Voir `MinimumEcrete` du Python.
    this.minimumEcrete = minimumEcrete;
    // Ce que la majoration exceptionnelle de septembre 2023 relit de chaque
    // pension que le minimum contributif regarde : `{regime, taux_plein,
    // cotisee, validee, maximum, cotises_tous_regimes, surcote}`. Voir
    // `PetitePension` du Python.
    this.petitesPensions = petitesPensions;
    // Ce que le relèvement des exploitants de septembre 2023 relit : `{regime,
    // eligible, points, gratuits, complement}` ; `null` sans RCO. Voir
    // `ChefDExploitation` du Python.
    this.chef = chef;
  }

  /** Les compléments, tels que le schéma de l'étape les décrit. */
  donnees() {
    return {
      schema_version: SCHEMA_VERSION,
      personne: this.personne,
      dispositifs: this.avantages.map((a) => ({
        code: a.code, fiche: FICHES[a.code], montant: a.montant,
        parts: (a.par_regime ?? []).map(([regime, montant]) => ({ regime, montant })),
      })),
      fiabilite: nomFiabilite(this.fiabilite),
    };
  }
}

/**
 * Les pensions de `liquidees`, complétées de ce que le droit y ajoute. Le
 * contexte dit ce que le calcul neutralise : les avantages non contributifs,
 * la décote et la surcote. `servies` est ce que valent, par an, à la date
 * d'effet, les pensions que des départs précédents servent déjà
 * (`departs.js`) : l'écrêtement du minimum contributif les compte.
 * `initiales` sont, après une retraite progressive, les pensions provisoires
 * de ses régimes de base menées à la date d'effet (`progressive.js`) : la
 * pension complète ne descend pas sous elles, et les vaut quand `recalcul` est
 * faux. `nationales` sont les pensions nationales de qui a des périodes qu'un
 * accord compare : la pension proratisée de chaque régime porté au minimum
 * contributif se compare à elle, chacune à son minimum, et la plus élevée est
 * servie. Voir le Python.
 */
export function completer(moteur, releve, ouverture, liquidees, contexte = null,
  servies = 0.0, initiales = [], recalcul = true, nationales = null,
  nature = "definitive", premiereRetraite = null) {
  const carriere = releve.carriere;
  const { durees, droits } = releve;
  const anneeLiquidation = carriere.anneeLiquidation;
  const avantagesNonContributifs = contexte === null
    || !contexte.neutralise("avantages_non_contributifs");
  const ignorerPenaliteAge = contexte !== null && contexte.neutralise("decote_surcote");
  const trimestresCotises = ouverture.trimestresCotises;
  const majorationEnfants = durees.enfants;
  const pointsAcquis = droits.pointsAcquis;
  const majorationPoints = droits.majorationPoints;
  const pointsMajores = droits.pointsMajores;
  const pensions = [...liquidees.regimes];
  const eligiblesMinimum = liquidees.minimum;
  const eligiblesGaranti = liquidees.garanti;
  // Ce que la surcote ajoute à chaque pension que le plafond de L. 18 borne : le
  // minimum garanti l'efface, la surcote parentale s'y ajoute.
  const surcotesL18 = new Map(
    (liquidees.plafonds ?? []).map((eligible) => [eligible.indice, eligible.surcote]));
  let total = pensions.reduce((somme, p) => somme + p.montant, 0.0);
  const avantages = [];
  let fiabiliteGlobale = Fiabilite.CERTIFIEE;
  let minimumApplique = false;
  let minimumEcrete = null;
  // Ce que le minimum contributif ajoute à chaque pension, par son indice.
  let ajoutsDuMinimum = new Map();
  let chef = null;

  // La règle du minimum que la date d'effet fait valoir (fiche
  // `minimum_contributif`) : il n'existe que depuis le 1er avril 1983, sa
  // majoration depuis 2004, son seuil depuis avril 2009, son écrêtement depuis
  // 2012, l'AVPF dans sa majoration depuis septembre 2023.
  const regle = moteur.minimumContributif.regle(dateDEffet(carriere));
  if (avantagesNonContributifs && eligiblesMinimum.length > 0 && regle.existe) {
    // Le minimum contributif ne relève que les pensions liquidées AU TAUX
    // PLEIN (L. 351-10). Sa majoration au titre des périodes cotisées se
    // proratise sur la durée cotisée DANS le régime, quand le montant de base
    // se proratise sur sa durée d'assurance. Les montants sont ceux du mois de
    // la date d'effet.
    const [montantBase, montantMajore, plafond, fiabiliteMinimum] = moteur
      .minimumContributif.valeurs(anneeLiquidation, carriere.moisLiquidation);
    const avpf = avpfRetenue(moteur, carriere, regle.plafond_avpf);
    const majoree = majorationOuverte(regle, trimestresCotises + avpf);
    const dateEffet = [anneeLiquidation, carriere.moisLiquidation];
    // Le minimum se compare à la pension AVANT surcote, et la surcote,
    // calculée sur cette pension nue, s'ajoute au minimum (D. 351-2-1) : voir
    // `complementMinimum`, qui porte aussi la règle d'avant 2009. La fraction
    // d'avant 1998 des cultes a ses propres majorations (`cultes.js`) : le
    // minimum ne relève que l'autre.
    const complementDu = (pension, eligible, plancher) => (!eligible.tauxPlein ? 0.0
      : complementMinimum((pension.montant - (eligible.horsMinimum ?? 0.0)) / eligible.surcote,
        plancher, eligible.surcote, dateEffet));
    const plancherNational = (eligible, majoration) => plancherDuRegime(
      selonLaRegle(eligible, regle, avpf), montantBase, montantMajore, majoration,
      regle.duree_tous_regimes);
    // LA PENSION PRORATISÉE ET LA PENSION NATIONALE : quand un accord les
    // compare, chacune est portée à SON minimum, puis la plus élevée est
    // servie — la proratisée à égalité.
    const alternatives = new Map();
    for (const eligible of nationales === null ? [] : nationales.minimum) {
      const nationale = nationales.regimes[eligible.indice];
      alternatives.set(nationale.regime, [nationale, eligible]);
    }
    const international = nationales === null ? null : minimumInternational(moteur, carriere);
    let cotisesFrancais = 0;
    let dureeTotale = 0;
    if (nationales !== null) {
      // La pension nationale ne compte que les trimestres cotisés en France
      // pour la majoration.
      cotisesFrancais = carriere.trimestresCumules(carriere.lignes.filter(
        (ligne) => ligneCotisee(moteur, carriere, ligne)
          && ligne.annee <= anneeLiquidation));
      dureeTotale = durees.pourLeTaux(etranger.GENERALE);
    }
    const complements = new Map();
    // Le minimum servi compte-t-il la majoration des périodes cotisées ?
    let majore = false;
    for (const eligible of eligiblesMinimum) {
      const pension = pensions[eligible.indice];
      const alternative = alternatives.get(pension.regime);
      let complement;
      let avecMajoration = majoree;
      if (alternative === undefined) {
        complement = complementDu(pension, eligible, plancherNational(eligible, majoree));
      } else {
        const plancher = international
          ? plancherInternational(selonLaRegle(eligible, regle, avpf), montantBase,
            montantMajore, dureeTotale,
            regle.majoration === "sans_distinction" ? dureeTotale : trimestresCotises + avpf,
            majoree)
          : plancherNational(eligible, majoree);
        complement = complementDu(pension, eligible, plancher);
        const [nationale, eligibleNational] = alternative;
        const majoreeNationale = majorationOuverte(regle, cotisesFrancais + avpf);
        const complementNational = complementDu(nationale, eligibleNational,
          plancherNational(eligibleNational, majoreeNationale));
        const proratisee = pension.montant + complement;
        if (nationale.montant + complementNational > proratisee) {
          pensions[eligible.indice] = {
            ...nationale,
            detail: "pension nationale, plus élevée que la pension proratisée "
              + `(${formatFixe(proratisee, 2, true)} €) : ${nationale.detail}`,
          };
          complement = complementNational;
          avecMajoration = majoreeNationale;
        } else {
          pensions[eligible.indice] = {
            ...pension,
            detail: "pension proratisée, au moins égale à la pension nationale "
              + `(${formatFixe(nationale.montant + complementNational, 2, true)} €) : `
              + pension.detail,
          };
        }
      }
      if (complement > 0) {
        complements.set(eligible.indice, complement);
        majore = majore || avecMajoration;
      }
    }
    if (regle.cumul_des_minima) {
      const limites = limiterLeCumul(complements, pensions, eligiblesMinimum, montantBase);
      for (const [indice, complement] of limites) {
        complements.set(indice, complement);
      }
    }
    total = pensions.reduce((somme, p) => somme + p.montant, 0.0);
    let releveMinimum = [...complements.values()].reduce((a, b) => a + b, 0.0);
    if (releveMinimum > 0 && regle.ecretement) {
      // Écrêtement de l'article L. 173-2, pour les pensions qui prennent effet
      // depuis le 1er janvier 2012 : le complément est rogné de ce qui
      // dépasse le plafond, tous régimes confondus, et jamais au-delà. La
      // comparaison porte sur les pensions PERSONNELLES, majorations pour
      // enfants exclues — raison de plus pour les calculer après —, celles que
      // d'autres départs servent déjà comprises, au montant du mois de la date
      // d'effet (R. 173-7).
      // Depuis 2012, les pensions étrangères aussi, hors celles des règlements
      // européens et de six conventions.
      const etrangeres = etranger.pensionsALEcretement(moteur, carriere);
      const marge = plafond - total - servies - etrangeres;
      const admissible = Math.max(0.0, Math.min(releveMinimum, marge));
      if (admissible < releveMinimum) {
        const facteur = admissible / releveMinimum;
        for (const [indice, complement] of complements) {
          complements.set(indice, complement * facteur);
        }
      }
      minimumEcrete = {
        avant_ecretement: releveMinimum,
        marge,
        par_regime: [...complements].map(([indice, complement]) => [
          pensions[indice].regime, complement]),
      };
      releveMinimum = admissible;
    }
    if (releveMinimum > 0) {
      ajoutsDuMinimum = new Map(complements);
      for (const [indice, complement] of complements) {
        // Le complément est DIT, pas seulement annoncé : sans lui, refaire la
        // formule donnait la pension d'avant le minimum et l'écart restait
        // inexpliqué — deux mille euros par an sur une petite retraite, ce
        // qui n'est pas un détail.
        pensions[indice] = {
          ...pensions[indice],
          montant: pensions[indice].montant + complement,
          detail: `${pensions[indice].detail} = `
            + `${formatFixe(pensions[indice].montant, 2, true)} €, porté au `
            + `minimum contributif par + ${formatFixe(complement, 2, true)} €`,
        };
      }
      total += releveMinimum;
      minimumApplique = true;
      fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteMinimum);
      avantages.push({
        code: "minimum_contributif",
        libelle: "Minimum contributif",
        montant: releveMinimum,
        detail: "porté au plancher, au prorata de la durée acquise"
          + (majore ? ", majoration des périodes cotisées comprise" : ""),
        // La part de chaque pension : la réversion du régime général se
        // calcule sans elle (`droit/reversion.js`).
        par_regime: [...complements].filter(([, complement]) => complement > 0)
          .map(([indice, complement]) => [pensions[indice].regime, complement]),
      });
    }
  }

  // LA MAJORATION EXCEPTIONNELLE DE SEPTEMBRE 2023 relève les pensions que le
  // minimum contributif regarde, portées ou non à lui ; elle se calcule le mois
  // où elle est due (`majorerLesPetitesPensions`). Ce qu'elle relit de chacune
  // s'écrit ici : ses durées, son taux plein et sa surcote.
  let petitesPensions = [];
  if (avantagesNonContributifs) {
    const moisDEffet = [anneeLiquidation, carriere.moisLiquidation];
    petitesPensions = eligiblesMinimum.map((eligible) => ({
      regime: pensions[eligible.indice].regime,
      taux_plein: eligible.tauxPlein,
      cotisee: eligible.cotiseeRegime,
      validee: eligible.dureeRegime,
      maximum: eligible.proratisation,
      cotises_tous_regimes: trimestresCotises,
      surcote: surcoteHorsMinimum(pensions[eligible.indice].montant, eligible,
        ajoutsDuMinimum.get(eligible.indice) ?? 0.0, moisDEffet),
    }));
  }

  if (avantagesNonContributifs && eligiblesGaranti.length > 0) {
    // Le minimum garanti n'est pas un minimum proratisé mais un BARÈME sur la
    // durée de services : quinze ans en ouvrent 57,5 % de la référence,
    // trente ans 95 %, quarante ans la totalité. Il ne s'ajoute pas à la
    // pension, il s'y substitue quand il lui est supérieur.
    let releveGaranti = 0.0;
    for (const eligible of eligiblesGaranti) {
      if (!eligible.ouvert) {
        continue;
      }
      const plancher = moteur.minimumGaranti.montant(
        anneeLiquidation, eligible.trimestresServices, eligible.dureeMaximum,
      );
      if (plancher === null) {
        continue;
      }
      const pension = pensions[eligible.indice];
      if (pension.montant > 0 && pension.montant < plancher[0]) {
        // Le complément était calculé en ligne et jamais nommé, alors que la
        // phrase juste dessous le cite : `complement` n'existait pas dans
        // cette portée — seulement dans la boucle du minimum contributif, au
        // -dessus — et toute carrière passant ici faisait tomber le moteur
        // JavaScript sur « complement is not defined » quand le Python, lui,
        // rendait sa pension. Le Python nomme la variable ; le portage ne le
        // faisait pas.
        const complement = plancher[0] - pension.montant;
        releveGaranti += complement;
        fiabiliteGlobale = Math.min(fiabiliteGlobale, plancher[1]);
        pensions[eligible.indice] = {
          ...pension,
          montant: plancher[0],
          // Le complément est DIT, comme pour le minimum contributif :
          // sans lui, refaire la formule donnait la pension d'avant le
          // plancher, et l'écart restait sans explication.
          detail: `${pension.detail} = `
            + `${formatFixe(pension.montant, 2, true)} €, porté au minimum `
            + `garanti par + ${formatFixe(complement, 2, true)} €`,
        };
        if (surcotesL18.has(eligible.indice)) {
          surcotesL18.set(eligible.indice, 0.0);
        }
      }
    }
    if (releveGaranti > 0) {
      total += releveGaranti;
      avantages.push({
        code: "minimum_garanti",
        libelle: "Minimum garanti de la fonction publique",
        montant: releveGaranti,
        detail: "barème de l'article L. 17, sur la durée de services",
      });
    }
  }

  // LA PENSION COMPLÈTE D'UNE RETRAITE PROGRESSIVE (droit/progressive.js) :
  // elle ne peut être inférieure à la pension provisoire, revalorisée ; avant
  // le décret du 8 juin 2006, elle l'était. Voir le Python.
  let plancherProgressive = 0.0;
  for (const [regime, initiale] of initiales) {
    pensions.forEach((pension, indice) => {
      if (pension.regime !== regime || (recalcul && pension.montant >= initiale)) {
        return;
      }
      const ecart = initiale - pension.montant;
      plancherProgressive += ecart;
      total += ecart;
      pensions[indice] = {
        ...pension,
        montant: initiale,
        detail: recalcul
          ? `${pension.detail} = ${formatFixe(pension.montant, 2, true)} €, porté à la `
            + `pension provisoire revalorisée par + ${formatFixe(ecart, 2, true)} €`
          : "la pension provisoire de la retraite progressive, revalorisée : "
            + `${formatFixe(initiale, 2, true)} €, qui ne se recalcule pas avant le `
            + "8 juin 2006",
      };
    });
  }

  // Surcote parentale (L. 351-1-2-1) : après les minima, avant la majoration
  // pour enfants qui se calcule sur la pension surcotée. Elle ne compte pas
  // les mêmes trimestres que la surcote ordinaire — celle-ci au-delà de l'âge
  // légal, celle-là dans l'année qui le précède — et les deux se cumulent.
  const parametresParentale = (avantagesNonContributifs
    && majorationEnfants !== null && !ignorerPenaliteAge)
    ? moteur.surcoteParentale.parametres(anneeLiquidation)
    : null;
  if (parametresParentale !== null) {
    const [ageLegalMinimal, tauxParental, maximum, fiabiliteParentale] = parametresParentale;
    let gainParental = 0.0;
    let trimestresParentaux = 0;
    for (let indice = 0; indice < pensions.length; indice += 1) {
      const pension = pensions[indice];
      const regime = moteur.catalogue.obtenir(pension.regime);
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
      if (periode === null
          || !periode.avantages_non_contributifs.includes("surcote_parentale")) {
        continue;
      }
      const ageLegal = ouvrir.ageOuverture(moteur, periode, carriere);
      const requis = ouvrir.dureeRequise(moteur, periode, carriere)[0];
      // LA FENÊTRE EST L'ANNÉE QUI PRÉCÈDE L'ÂGE LÉGAL, dès que cet âge
      // atteint 63 ans (L. 351-1-2-1) : voir le Python, qui cite le texte.
      if (ageLegal < ageLegalMinimal) {
        continue;
      }
      // Au MOIS près : l'âge légal tombe en cours d'année depuis 2026.
      const dateLegale = carriere.dateDeLAge(ageLegal);
      const debutFenetre = dateLegale.plusMois(-12);
      // Seuls comptent les trimestres cotisés de la fenêtre accomplis « au
      // delà de la limite » de durée, trimestres pour enfants compris.
      if (requis <= 0) {
        continue;
      }
      const avant = majorationEnfants.trimestres + trimestresEntreDates(
        carriere, new DateMois(carriere.annee_naissance, 1), debutFenetre, false,
      );
      const validesFenetre = trimestresEntreDates(
        carriere, debutFenetre, dateLegale, false,
      );
      const trimestres = Math.min(
        maximum,
        trimestresEntreDates(carriere, debutFenetre, dateLegale, true),
        Math.max(0, avant + validesFenetre - requis),
      );
      if (trimestres <= 0) {
        continue;
      }
      const supplement = pension.montant * tauxParental * trimestres;
      pensions[indice] = {
        ...pension,
        montant: pension.montant + supplement,
        detail: `${pension.detail}, surcote parentale `
          + `${formatPourcentage(tauxParental * trimestres, 2)}`,
      };
      gainParental += supplement;
      trimestresParentaux = Math.max(trimestresParentaux, trimestres);
      if (surcotesL18.has(indice)) {
        // La surcote parentale du fonctionnaire majore la pension « dans les
        // mêmes conditions que celles prévues au III » (L. 14, IV).
        surcotesL18.set(indice, surcotesL18.get(indice) + supplement);
      }
    }
    if (gainParental > 0) {
      total += gainParental;
      fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteParentale);
      avantages.push({
        code: "surcote_parentale",
        libelle: "Surcote parentale",
        montant: gainParental,
        detail: `${formatPourcentage(tauxParental * trimestresParentaux, 2)} pour `
          + `${trimestresParentaux} trimestre`
          + `${trimestresParentaux > 1 ? "s" : ""} dans `
          + "l'année qui précède l'âge légal",
      });
    }
  }

  if (avantagesNonContributifs && carriere.nombre_enfants >= 2) {
    let majoration = 0.0;
    let tauxCite = 0.0;
    // Le plafond de l'Agirc-Arrco s'oppose à la majoration de LA
    // complémentaire, pas à celle de chacune de ses fiches : les points d'un
    // salarié du privé sont répartis entre l'Agirc, l'Arrco et le régime
    // unifié, et plafonner chacun séparément triplerait le plafond.
    let majorationPlafonnee = 0.0;
    let plafondCommun = null;
    // [régime, part, soumise au plafond], dans l'ordre des pensions.
    const parts = [];
    // Le plafond de L. 18, au traitement qui a liquidé la pension de chaque
    // régime du code des pensions.
    const plafondL18 = plafondDeLArticleL18(moteur, carriere);
    const traitements = new Map(
      (liquidees.plafonds ?? []).map((eligible) => [eligible.indice, eligible.traitement]));
    let borneeAuTraitement = false;
    for (const [indice, pension] of pensions.entries()) {
      if (pension.montant <= 0.0) {
        continue;
      }
      const regime = moteur.catalogue.obtenir(pension.regime);
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
      if (periode === null
          || !periode.avantages_non_contributifs.includes("majoration_enfants")) {
        continue;
      }
      let taux = tauxMajorationEnfants(regime, carriere.nombre_enfants, periode);
      const points = pointsAcquis.get(pension.regime) ?? 0.0;
      const majores = pointsMajores.get(pension.regime) ?? 0.0;
      if (majores > 0.0 && points > 0.0) {
        // CHAQUE POINT À SON TAUX, celui de son année d'acquisition.
        taux = (majorationPoints.get(pension.regime) + taux * (points - majores)) / points;
      }
      if (taux <= 0) {
        continue;
      }
      let part = pension.montant * taux;
      if (plafondL18 !== null && traitements.has(indice)
          && plafondL18.parametres.regimes.includes(pension.regime)) {
        const sous = majorationSousLeTraitement(
          pension.montant, part, traitements.get(indice), surcotesL18.get(indice),
          plafondL18.parametres.surcote === "hors_du_plafond");
        if (sous < part) {
          borneeAuTraitement = true;
          fiabiliteGlobale = Math.min(fiabiliteGlobale,
            fiabiliteDepuisTexte(plafondL18.parametres.fiabilite));
          part = sous;
          if (part <= 0.0) {
            continue;
          }
        }
      }
      const plafond = plafondMajoration(
        moteur, pension.regime, periode, carriere, anneeLiquidation,
      );
      if (plafond === null) {
        majoration += part;
      } else {
        majorationPlafonnee += part;
        plafondCommun = plafondCommun === null ? plafond : Math.max(plafondCommun, plafond);
      }
      parts.push([pension.regime, part, plafond !== null]);
      tauxCite = Math.max(tauxCite, taux);
    }
    const plafonnee = plafondCommun !== null;
    let retenuePlafonnee = 1.0;
    if (plafondCommun !== null) {
      majoration += Math.min(majorationPlafonnee, plafondCommun);
      if (majorationPlafonnee > plafondCommun) {
        retenuePlafonnee = plafondCommun / majorationPlafonnee;
      }
    }
    if (majoration > 0) {
      total += majoration;
      let detail = `jusqu'à ${formatPourcentage(tauxCite, 0)} selon le régime`;
      if (plafonnee) {
        detail += ", plafonnée en euros à la complémentaire";
      }
      if (borneeAuTraitement) {
        detail += ", bornée au traitement dans la fonction publique";
      }
      avantages.push({
        code: "majoration_enfants",
        libelle: carriere.nombre_enfants >= 3
          ? "Majoration pour trois enfants et plus"
          : "Bonification pour deux enfants",
        montant: majoration,
        detail,
        par_regime: parts.map(([code, part, soumise]) => [
          code, part * (soumise ? retenuePlafonnee : 1.0),
        ]),
      });
    }
  }

  // LES DEUX MINIMA DES EXPLOITANTS AGRICOLES, après la majoration pour
  // enfants, que leurs plafonds comptent : la pension majorée de référence
  // relève la pension de base, puis le complément différentiel ajoute des
  // points de RCO, en comptant la pension relevée. Voir le Python.
  const agricole = liquidees.agricole ?? null;
  if (avantagesNonContributifs && agricole !== null) {
    const etrangeres = etranger.pensionsEtrangeresServies(
      moteur.macro, carriere, carriere.dateLiquidation);
    const base = pensions[agricole.indice];
    const majoree = pensionMajoree(moteur, carriere, agricole, base,
      total + servies + etrangeres);
    if (majoree !== null && majoree.complement > 0.0) {
      pensions[agricole.indice] = {
        ...base,
        montant: base.montant + majoree.complement,
        detail: `${base.detail} = ${formatFixe(base.montant, 2, true)} €, porté à la pension `
          + `majorée de référence par + ${formatFixe(majoree.complement, 2, true)} €`,
      };
      total += majoree.complement;
      fiabiliteGlobale = Math.min(fiabiliteGlobale, majoree.fiabilite);
      avantages.push({
        code: "pension_majoree_reference",
        libelle: "Pension majorée de référence",
        montant: majoree.complement,
        detail: `PMR ${formatFixe(majoree.entiere, 2, true)} € × ${majoree.duree}/`
          + `${majoree.reference}, au taux plein`
          + (majoree.complement < majoree.avantEcretement - 1e-9
            ? `, écrêtée au plafond de ${formatFixe(majoree.plafond, 2, true)} € de toutes `
              + "les pensions"
            : ""),
        par_regime: [[base.regime, majoree.complement]],
      });
    }
    // Le complément ne s'ajoute qu'à la RCO dont la période le déclare.
    const indiceRco = pensions.findIndex((p) => p.regime === RCO);
    let periodeRco = null;
    if (indiceRco >= 0) {
      const regimeRco = moteur.catalogue.obtenir(RCO);
      periodeRco = regimeRco.periode(Math.min(anneeLiquidation, derniereAnnee(regimeRco)));
    }
    const valeur = periodeRco !== null
      && periodeRco.avantages_non_contributifs.includes("complement_differentiel_rco")
      ? liquider.valeurDuPoint(moteur, RCO, carriere.dateLiquidation) : null;
    let differentiel = null;
    if (indiceRco >= 0 && valeur !== null) {
      const rco = pensions[indiceRco];
      differentiel = complementDifferentiel(
        moteur, carriere, agricole, pensions[agricole.indice].montant, rco.montant,
        pointsAcquis.get(RCO) ?? 0.0, valeur[0], total + servies + etrangeres);
      if (differentiel !== null) {
        pensions[indiceRco] = {
          ...rco,
          montant: rco.montant + differentiel.montant,
          detail: `${rco.detail} = ${formatFixe(rco.montant, 2, true)} €, complément `
            + `différentiel de ${formatFixe(differentiel.points, 0, true)} points`,
        };
        total += differentiel.montant;
        fiabiliteGlobale = Math.min(fiabiliteGlobale, differentiel.fiabilite, valeur[1]);
        avantages.push({
          code: "complement_differentiel_rco",
          libelle: "Complément différentiel de la complémentaire agricole",
          montant: differentiel.montant,
          detail: `${formatFixe(differentiel.points, 0, true)} points : `
            + `${formatPourcentage(differentiel.pourcentage, 0)} de 1 820 heures au SMIC `
            + `net agricole de ${formatFixe(differentiel.smicNet, 4)} €, `
            + `${formatFixe(differentiel.cible, 2, true)} € par an, × ${differentiel.duree}/`
            + `${differentiel.reference}`
            + (differentiel.plafonne ? ", plafonné" : ""),
          par_regime: [[RCO, differentiel.montant]],
        });
      }
    }
    // LE RELÈVEMENT DE SEPTEMBRE 2023 ouvre au taux plein les points gratuits et
    // le complément de la RCO des pensions prises avant (`releverLesExploitants`) :
    // ce qu'il relira s'écrit ici.
    if (indiceRco >= 0) {
      let gratuits = 0.0;
      if (!droits.gratuits.has(RCO) && periodeRco !== null
          && periodeRco.points_gratuits !== null && periodeRco.points_gratuits !== undefined
          && !(contexte !== null && contexte.neutralise("points_gratuits"))) {
        gratuits = pointsGratuits(moteur, periodeRco, carriere, durees.parAnnee.assurance,
          durees.trimestres, carriere.age_liquidation || 0.0, true)[0];
      }
      chef = {
        regime: pensions[agricole.indice].regime, eligible: agricole,
        points: pointsAcquis.get(RCO) ?? 0.0, gratuits, complement: differentiel !== null,
      };
    }
  }

  // LES VERSEMENTS UNIQUES, en dernier : ils lisent la pension complétée,
  // minimum, majorations et compléments compris.
  const fiabiliteVersee = verserEnCapital(moteur, carriere, pensions, avantages,
    pointsAcquis, nature, premiereRetraite);
  if (fiabiliteVersee !== null) {
    fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteVersee);
  }

  return new Complements({
    personne: carriere.personne,
    regimes: pensions,
    avantages,
    total,
    minimumApplique,
    fiabilite: fiabiliteGlobale,
    plancher: plancherProgressive,
    minimumEcrete,
    petitesPensions,
    chef,
  });
}

/**
 * Le seuil d'une date d'effet : le dernier du barème, `[[AAAA-MM-JJ, euros], ...]`,
 * dont la date ne la passe pas ; null avant le premier.
 */
function seuilALaDate(seuils, dateEffet) {
  let retenu = null;
  for (const [debut, seuil] of seuils) {
    if (String(debut) <= dateEffet) {
      retenu = Number(seuil);
    }
  }
  return retenu;
}

/**
 * Le coefficient de la table d'une version, à l'âge révolu de `age`, et cet
 * âge ; un âge hors de la table prend celui de son bout. Voir
 * `coefficient_du_versement` du Python.
 */
export function coefficientDuVersement(regle, age) {
  const revolu = Math.trunc(age + 1e-9);
  const coefficients = regle.coefficients;
  const rang = Math.min(Math.max(revolu - Math.trunc(regle.coefficients_depuis), 0),
    coefficients.length - 1);
  return [Number(coefficients[rang]), revolu];
}

/**
 * Le salaire de référence, prix d'achat du point, de `regime` en `annee` :
 * publié, ou, au-delà du dernier barème, le dernier publié mené comme la valeur
 * de service du point. Voir `salaire_de_reference_points` du Python.
 */
export function salaireDeReferencePoints(moteur, regime, annee) {
  const achat = moteur.valeursPoint.achat(regime, annee);
  if (achat !== null) {
    return [achat[0], achat[2]];
  }
  const derniere = moteur.valeursPoint.derniereAnneeAchetee(regime);
  if (derniere === null || annee < derniere) {
    return null;
  }
  const publie = moteur.valeursPoint.achat(regime, derniere);
  const valeurAlors = liquider.valeurDuPoint(moteur, regime, derniere);
  const valeur = liquider.valeurDuPoint(moteur, regime, annee);
  if (publie === null || valeurAlors === null || valeur === null || valeurAlors[0] <= 0) {
    return null;
  }
  return [publie[0] * valeur[0] / valeurAlors[0],
    Math.min(publie[2], valeur[1], Fiabilite.MOYENNE)];
}

/**
 * Les petites pensions que leur régime ne sert pas : un versement unique les
 * remplace, que `pensions` porte désormais (`capital`), chacune avec la formule
 * qui le dit ; son montant annuel reste celui de la pension remplacée. Rend la
 * fiabilité des barèmes lus quand un versement remplace une pension, null
 * sinon. Le versement forfaitaire unique du régime général, celui de
 * l'Agirc-Arrco (ou de l'Arrco et de l'Agirc), celui de l'Ircantec ; jamais la
 * retraite progressive. Voir `verser_en_capital` du Python.
 */
export function verserEnCapital(moteur, carriere, pensions, avantages, pointsAcquis,
  nature = "definitive", premiereRetraite = null) {
  const dateEffet = dateDEffet(carriere);
  if (dateEffet === null || nature === "provisoire") {
    return null;
  }
  const enfants = new Map();
  for (const avantage of avantages) {
    if (avantage.code === "majoration_enfants") {
      for (const [code, part] of avantage.par_regime) {
        enfants.set(code, (enfants.get(code) ?? 0.0) + part);
      }
    }
  }
  const fiabilites = [];
  const sansCapital = (pension) => pension.capital === undefined || pension.capital === null;
  const annuelle = (pension) => pension.montant + (enfants.get(pension.regime) ?? 0.0);
  const remplacer = (indice, capital, formule) => {
    pensions[indice] = { ...pensions[indice], capital,
      detail: pensions[indice].detail + formule };
  };

  // LE RÉGIME GÉNÉRAL : quinze annuités, sous le seuil de la date d'effet.
  let regle = moteur.fichesDatees.regle(FICHE_DU_VERSEMENT_FORFAITAIRE, dateEffet);
  const avant = (regle === null || !regle.existe) ? null
    : (regle.premiere_retraite_avant ?? null);
  if (regle !== null && regle.existe
      && (avant === null || (premiereRetraite !== null && premiereRetraite < String(avant)))) {
    const seuil = seuilALaDate(regle.seuils, dateEffet);
    const multiple = Math.trunc(regle.multiple);
    pensions.forEach((pension, indice) => {
      if (seuil === null || !regle.regimes.includes(pension.regime)
          || pension.montant <= 0.0 || !sansCapital(pension)) {
        return;
      }
      const montant = annuelle(pension);
      if (montant >= seuil) {
        return;
      }
      remplacer(indice, multiple * montant,
        ` ; ${formatFixe(montant, 2, true)} € par an`
        + (enfants.has(pension.regime) ? ", majoration pour enfants comprise" : "")
        + `, sous le seuil de ${formatFixe(seuil, 2, true)} € : remplacée par un versement `
        + `forfaitaire unique de ${formatFixe(multiple * montant, 2, true)} €, ${multiple} fois `
        + "la pension annuelle");
      fiabilites.push(fiabiliteDepuisTexte(regle.fiabilite));
    });
  }

  // L'AGIRC-ARRCO, ou l'Arrco et l'Agirc : chaque allocation, un groupe de
  // régimes, sa valeur viagère au coefficient de l'âge révolu.
  regle = moteur.fichesDatees.regle(FICHE_DU_VERSEMENT_AGIRC_ARRCO, dateEffet);
  if (regle !== null && regle.existe) {
    if (!MESURES_DU_VERSEMENT.includes(regle.mesure)) {
      throw new Error(`${FICHE_DU_VERSEMENT_AGIRC_ARRCO} : la mesure ${regle.mesure} n'est `
        + `pas de celles que le moteur connaît, ${MESURES_DU_VERSEMENT}`);
    }
    const [coefficient, age] = coefficientDuVersement(regle, carriere.age_liquidation || 0.0);
    for (const allocation of regle.allocations) {
      const membres = [];
      pensions.forEach((pension, indice) => {
        if (allocation.regimes.includes(pension.regime) && pension.montant > 0.0
            && sansCapital(pension)) {
          membres.push(indice);
        }
      });
      if (membres.length === 0) {
        continue;
      }
      const seuilPoints = Number(allocation.seuil_points);
      let mesure;
      let seuil;
      let unite;
      let dit;
      if (regle.mesure === "points") {
        mesure = membres.reduce(
          (somme, i) => somme + (pointsAcquis.get(pensions[i].regime) ?? 0.0), 0.0);
        seuil = seuilPoints;
        unite = "points";
        dit = `${formatFixe(mesure, 2, true)} points`;
      } else {
        const valeur = liquider.valeurDuPoint(moteur, allocation.point,
          carriere.dateLiquidation);
        if (valeur === null) {
          continue;
        }
        mesure = membres.reduce((somme, i) => somme + annuelle(pensions[i]), 0.0);
        seuil = seuilPoints * valeur[0];
        unite = "€";
        dit = `${formatFixe(mesure, 2, true)} € par an`;
        fiabilites.push(valeur[1]);
      }
      const sous = allocation.seuil_compris ? mesure <= seuil : mesure < seuil;
      if (mesure <= 0.0 || !sous) {
        continue;
      }
      let borne = allocation.seuil_compris
        ? `au plus ${formatFixe(seuilPoints, 0, true)} points`
        : `moins de ${formatFixe(seuilPoints, 0, true)} points`;
      if (unite === "€") {
        borne += `, ${formatFixe(seuil, 2, true)} €`;
      }
      for (const indice of membres) {
        const montant = annuelle(pensions[indice]);
        remplacer(indice, montant * coefficient,
          ` ; allocation de ${dit}, ${borne} : versée en capital, `
          + `${formatFixe(montant * coefficient, 2, true)} € (${formatFixe(montant, 2, true)} € `
          + `× ${formatFixe(coefficient, 1)} à ${age} ans)`);
      }
      fiabilites.push(fiabiliteDepuisTexte(regle.fiabilite));
    }
  }

  // L'IRCANTEC : les points, par le salaire de référence de l'année d'avant.
  regle = moteur.fichesDatees.regle(FICHE_DU_VERSEMENT_IRCANTEC, dateEffet);
  if (regle !== null && regle.existe) {
    const annee = carriere.anneeLiquidation - 1;
    pensions.forEach((pension, indice) => {
      if (!regle.regimes.includes(pension.regime) || pension.montant <= 0.0
          || !sansCapital(pension)) {
        return;
      }
      const points = pointsAcquis.get(pension.regime) ?? 0.0;
      if (!(points > 0.0 && points < Number(regle.seuil_points))) {
        return;
      }
      const reference = salaireDeReferencePoints(moteur, pension.regime, annee);
      if (reference === null) {
        return;
      }
      remplacer(indice, points * reference[0],
        ` ; ${formatFixe(points, 2, true)} points, moins de `
        + `${formatFixe(Number(regle.seuil_points), 0, true)} : versée en capital, `
        + `${formatFixe(points * reference[0], 2, true)} € (${formatFixe(points, 2, true)} points `
        + `× salaire de référence de ${annee}, ${formatFixe(reference[0], 4)} €)`);
      fiabilites.push(reference[1], fiabiliteDepuisTexte(regle.fiabilite));
    });
  }
  return fiabilites.length > 0 ? Math.min(...fiabilites) : null;
}

/**
 * Ce que la surcote ajoute à `montant`, la pension d'un régime que le minimum
 * contributif a peut-être relevée de `ajout` : celle de la pension nue, que le
 * minimum laisse en sus depuis avril 2009 ; avant, rien quand il l'a relevée.
 * Voir `surcote_hors_minimum` du Python.
 */
export function surcoteHorsMinimum(montant, eligible, ajout, dateEffet) {
  const [annee, mois] = dateEffet;
  const [anneeRegle, moisRegle] = SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS;
  const avant2009 = annee < anneeRegle || (annee === anneeRegle && mois < moisRegle);
  if (eligible.surcote <= 1.0 || (ajout > 0 && avant2009)) {
    return 0.0;
  }
  const nue = (montant - ajout - (eligible.horsMinimum ?? 0.0)) / eligible.surcote;
  return Math.max(0.0, nue * (eligible.surcote - 1.0));
}

/**
 * Plafond en euros de la majoration pour enfants, ou ``null``.
 *
 * Les régimes de base servent 10 % sans plafond ; l'Agirc-Arrco borne la
 * majoration en euros — 2 367,48 € par an depuis le 1er novembre 2024 — et le
 * plafond suit la valeur de service du point. Il ne s'oppose qu'aux assurés
 * nés à compter du 2 août 1951 ; le modèle ne connaît que l'année de
 * naissance et retient les générations à partir de 1952.
 */
export function plafondMajoration(moteur, code, periode, carriere, anneeLiquidation) {
  if (periode.plafond_majoration_enfants === null
      || periode.plafond_majoration_enfants === undefined) {
    return null;
  }
  if (carriere.annee_naissance < 1952) {
    return null;
  }
  const plafond = periode.plafond_majoration_enfants;
  const anneeReference = periode.plafond_majoration_annee;
  if (anneeReference === null || anneeReference === undefined) {
    return plafond;
  }
  // Le plafond de la date d'effet, comme la valeur du point qu'il suit.
  const servie = liquider.valeurDuPoint(moteur, code, carriere.dateLiquidation);
  const publiee = liquider.valeurDuPoint(moteur, code, anneeReference);
  if (servie === null || publiee === null || publiee[0] <= 0) {
    return plafond * moteur.macro.coefficientPrix(anneeReference, anneeLiquidation);
  }
  return plafond * servie[0] / publiee[0];
}

/**
 * Ce que le minimum contributif ajoute à une pension, surcote comprise —
 * portage de `complement_minimum` : depuis avril 2009, `plancher − nue` (la
 * surcote, calculée sur la pension nue, s'ajoute au minimum) ; avant,
 * `max(0, plancher − nue × coefficient)`. Circulaire Cnav 2018-04, 3.4.
 */
export function complementMinimum(nue, plancher, coefficientSurcote, dateEffet) {
  if (nue <= 0) {
    return 0.0;
  }
  const [annee, mois] = dateEffet;
  const [anneeRegle, moisRegle] = SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS;
  if (annee > anneeRegle || (annee === anneeRegle && mois >= moisRegle)) {
    return Math.max(0.0, plancher - nue);
  }
  return Math.max(0.0, plancher - nue * coefficientSurcote);
}

/**
 * Taux de majoration pour enfants, régime par régime. Le régime général et les
 * régimes spéciaux servent 10 % à partir de trois enfants ; la fonction
 * publique y ajoute 5 % par enfant au-delà du troisième. Les complémentaires
 * servent 10 % aussi, mais plafonnés en euros : le taux est le même, c'est
 * `plafondMajoration` qui borne. Une fiche qui porte son propre barème — les
 * marins, qui bonifient dès deux enfants — l'emporte.
 */
function tauxMajorationEnfants(regime, nombreEnfants, periode = null) {
  const bareme = periode?.taux_majoration_enfants;
  if (bareme && bareme.length > 0) {
    return bareme[Math.min(nombreEnfants, bareme.length - 1)];
  }
  if (nombreEnfants < 3) {
    return 0.0;
  }
  if (regime.famille === "fonction_publique") {
    return 0.1 + 0.05 * (nombreEnfants - 3);
  }
  return 0.1;
}

/**
 * Trimestres acquis entre deux DATES, au mois près — `fin` exclue. Portage de
 * `_trimestres_entre_dates` : chaque ligne répartit ses trimestres sur ses
 * mois (les premiers de l'année du départ, les derniers de celle de
 * l'entrée), seuls comptent ceux de la plage, arrondi au trimestre inférieur.
 */
function trimestresEntreDates(carriere, debut, fin, cotisesSeulement) {
  let total = 0.0;
  for (const ligne of carriere.lignes) {
    if (cotisesSeulement && !ligne.cotise) {
      continue;
    }
    total += trimestresDeLaLigneEntre(carriere, ligne, debut, fin);
  }
  return Math.floor(total + 1e-9);
}
