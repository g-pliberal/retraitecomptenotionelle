/**
 * Le cumul emploi-retraite (docs/architecture.md, § 7.4 ; fiches
 * `cumul_emploi_retraite_et_retraite_progressive`,
 * `cumul_emploi_retraite_fonction_publique`,
 * `cumul_emploi_retraite_complementaire_des_independants`,
 * `cumul_emploi_retraite_ircantec`, `cumul_emploi_retraite_rco_agricole` et
 * `cumul_emploi_retraite_complementaires_des_liberaux`).
 *
 * Jumeau de `src/retraite_notionnelle/droit/cumul.py`, fonction pour
 * fonction. Le retraité qui travaille garde sa pension, entière ou non, selon
 * le droit du MOIS où il travaille, la date de sa pension et celle de sa
 * première pension de base : le salarié (L. 161-22 — la rupture avec le
 * dernier employeur de 1983, le plafond du dernier salaire de 2004, le cumul
 * intégral de 2009, la réduction du dépassement des premières pensions de
 * 2015 pour les activités de 2017, les trois régimes selon l'âge de 2027),
 * l'artisan et le commerçant (L. 634-6), et leur complémentaire, qui suit
 * leur base, le libéral (L. 643-6), et la complémentaire de sa section, que
 * ses statuts règlent — suspendus le nombre de mois que le dépassement de
 * l'année épuise (D. 634-11-5, D. 643-10-2) —, le fonctionnaire (L. 84 à L. 86
 * du code des pensions), l'Agirc-Arrco, l'Ircantec, la RCO agricole. Chaque
 * régime ne réduit que ses pensions, pour l'activité qui relève de lui : voir
 * le Python, qui dit les textes.
 */

import { DateMois } from "../calendrier.js";
import { periodeDeLiquidation } from "./commun.js";
import * as lesDeparts from "./departs.js";
import { dureeRequise } from "./ouvrir.js";

/** Ce que le droit fait d'une pension, pour un mois d'activité. */
export const LIBRE = "libre";
export const INTEGRAL = "integral";
export const PLAFONNEE = "plafonnee";
export const NON_DUE = "non_due";
export const SUSPENDUE = "suspendue";
export const REDUITE = "reduite";
export const SEUIL_NON_PUBLIE = "seuil_non_publie";
export const NON_CALCULE = "non_calcule";

/**
 * Le motif d'un mois de l'année du dépassement où la pension du non-salarié
 * n'est pas suspendue : le dépassement en épuise moins que l'activité n'en compte.
 */
export const HORS_DES_MOIS_SUSPENDUS = "hors_des_mois_suspendus";

/** L'ordre où se dit le statut d'un mois : celui de la pension la plus touchée. */
export const PRIORITE = [NON_DUE, SUSPENDUE, REDUITE, SEUIL_NON_PUBLIE, NON_CALCULE,
  PLAFONNEE, INTEGRAL, LIBRE];

/** Les versions des deux fiches. */
export const AVANT_1983 = "sans_condition_avant_1983";
export const RUPTURE_1983 = "rupture_avec_l_employeur_1983";
export const PLAFOND_2004 = "plafond_du_dernier_salaire_2004";
export const LIBERALISE_2009 = "cumul_liberalise_2009";
export const PREMIERES_2015 = "premieres_pensions_de_2015";
export const REDUCTION_2015 = "reduction_du_depassement_2015";
export const AGES_2027 = "trois_regimes_selon_l_age_2027";
export const FP_1970 = "limite_d_age_1970";
export const FP_2004 = "tiers_de_la_pension_2004";
export const FP_2009 = "cumul_integral_2009";
export const FP_2015 = "tout_employeur_2015";
export const FP_2027 = "regles_communes_2027";
export const RCI_AVANT_2009 = "servie_entiere_avant_2009";
export const RCI_2009 = "suspendue_avec_la_base_2009";
export const RCI_2024 = "reduite_comme_la_base_2024";
/**
 * La version de 2027 de chaque complémentaire que L. 161-22, III, A, réduit
 * après les bases : celle du RCI, de l'Ircantec, de la RCO agricole et des
 * sections libérales porte ce même nom dans sa fiche.
 */
export const RCI_2027 = "imputee_apres_les_bases_2027";
/** Les versions des fiches de l'Ircantec, de la RCO agricole et des sections. */
export const IRCANTEC_AVANT_2004 = "servie_entiere_avant_2004";
export const IRCANTEC_2004 = "l_161_22_2004";
export const IRCANTEC_2020 = "sans_le_troisieme_alinea_2020";
export const RCO_AGRICOLE_2003 = "suit_la_base_2003";
export const SECTIONS_STATUTS = "statuts_des_sections";

/** Les dates qui découpent la règle, en rang de mois. */
const rang = (annee, mois) => new DateMois(annee, mois).rang;
export const LOI_1983 = rang(1983, 4);
export const ARTISANS_1984 = rang(1984, 7);
export const LOI_2004 = rang(2004, 1);
export const LOI_2009 = rang(2009, 1);
export const REVALORISATION_2010 = rang(2010, 1);
export const ORDRE_DES_AGES = rang(2014, 2);
export const PREMIERE_2015 = rang(2015, 1);
export const REDUCTION_SALARIES = rang(2017, 4);
export const REDUCTION_NON_SALARIES = rang(2017, 1);
/**
 * Décret n° 2011-62, pour les périodes postérieures au 16 janvier 2011 : le
 * seuil du libéral rapporté à la durée de son activité, et sa pension
 * suspendue un nombre de mois ; le premier mois entier.
 */
export const LIBERAUX_2011 = rang(2011, 2);
export const PREMIERE_2027 = rang(2027, 1);
/** Les règlements du RCO et du NRCO de 2009, que la caisse applique depuis janvier. */
export const COMPLEMENTAIRES_2009 = rang(2009, 1);
/** L'arrêté du 19 juin 2024, en vigueur le 26 : le premier mois entier. */
export const SECTION_3_RCI = rang(2024, 7);
/**
 * L'article 14 de l'arrêté du 30 décembre 1970 soumet l'allocation de
 * l'Ircantec à L. 161-22 depuis 2004 ; sans son troisième alinéa depuis
 * l'arrêté du 16 décembre 2020, en vigueur le 19 : le premier mois entier.
 */
export const IRCANTEC_L_161_22 = rang(2004, 1);
export const IRCANTEC_SANS_REDUCTION = rang(2021, 1);

/** Les règles des statuts des sections libérales pour leur complémentaire. */
export const A_LA_REPRISE = "suspendue_a_la_reprise";
export const AVEC_LA_BASE = "suspendue_avec_la_base";
export const COMME_LA_BASE = "reduite_comme_la_base";
export const APRES_LA_BASE = "reduite_apres_la_base";
export const DEPASSEMENT_ENTIER = "reduite_du_depassement";
export const SANS_SUSPENSION = "sans_suspension";
export const NOTAIRE_LIBERAL = "incompatible_avec_le_notariat_liberal";
/**
 * Chaque section dont les statuts sont lus, la règle de chacune de leurs
 * rédactions et le premier mois entier où elle vaut (fiche
 * `cumul_emploi_retraite_complementaires_des_liberaux`).
 */
export const REGLES_DES_SECTIONS = {
  carcdsf_complementaire: [[rang(2007, 11), A_LA_REPRISE], [rang(2011, 2), AVEC_LA_BASE]],
  carmf_complementaire: [[rang(2011, 10), APRES_LA_BASE]],
  carpv_complementaire: [[rang(2011, 2), DEPASSEMENT_ENTIER], [rang(2022, 1), SANS_SUSPENSION]],
  cavamac_complementaire: [[rang(2011, 7), AVEC_LA_BASE], [rang(2026, 8), COMME_LA_BASE]],
  cavom_complementaire: [[rang(2020, 10), APRES_LA_BASE], [rang(2026, 8), DEPASSEMENT_ENTIER]],
  cprn_complementaire: [[rang(2017, 7), NOTAIRE_LIBERAL]],
};
/** Les professions que visent les statuts de 2007 de la CARCDSF et ceux de la CPRN. */
export const PROFESSIONS_DES_STATUTS = {
  [A_LA_REPRISE]: "chirurgien_dentiste_ou_sage_femme", [NOTAIRE_LIBERAL]: "notaire",
};

export const SIX_MOIS = 6;
export const HEURES_SMIC = 1820;
export const PART_SMIC_2004 = 1.0;
export const PART_SMIC_2009 = 1.6;
export const ASSIETTES_CSG = [[1991, 0.95], [2005, 0.97], [2012, 0.9825]];
export const SEUILS_NON_SALARIES = { independants: 0.5, liberaux: 1.0 };
export const PART_DE_LA_PENSION = 1.0 / 3.0;
export const ABATTEMENT_MINIMUM_GARANTI = 0.5;
export const FRANCHISE_1970 = 0.25;

export const FONCTION_PUBLIQUE = new Set(["fonction_publique_etat", "cnracl", "fspoeie",
  "pensions_civiles_1853"]);
export const OUTRE_MER = new Set(["cafat_nouvelle_caledonie", "cps_polynesie",
  "cps_polynesie_tranche_b", "cps_saint_pierre_et_miquelon", "cssm_mayotte",
  "wallis_et_futuna", "fonctionnaires_pacifique", "crfm_mayotte", "elus_pacifique"]);
export const AGIRC_ARRCO = new Set(["agirc", "agirc_arrco", "agirc_entreprises_nouvelles",
  "arrco", "arrco_cultes", "arrco_tranche_2", "arrco_tranche_2_entreprises_nouvelles",
  "igrante", "ipacte", "regimes_professionnels_integres", "unirs"]);
export const INDEPENDANTS = new Set(["artisan", "commercant", "micro_entrepreneur",
  "liberal_non_reglemente", "gerant_debit_tabac"]);
/** Le RCI et les complémentaires qu'il a reprises en 2013, dont il sert les points. */
export const COMPLEMENTAIRES_DES_INDEPENDANTS = new Set(["rci", "rco_artisans", "nric"]);
export const COMPLEMENTAIRES_DES_LIBERAUX = new Set(["carcdsf_complementaire",
  "carmf_complementaire", "carpimko_complementaire", "carpv_complementaire",
  "cavamac_complementaire", "cavec_complementaire", "cavom_complementaire",
  "cavp_complementaire", "cipav_complementaire", "cprn_complementaire"]);
export const GROUPES_COMPLEMENTAIRES_2027 = new Set(["rci", "ircantec", "rco_agricole",
  "liberales"]);
export const ALIGNES = new Set(["regime_general"]);
/** La limite d'âge de l'emploi quitté, avant 2004, selon son classement. */
export const LIMITES_D_AGE_1970 = { aucune: 65.0, active: 60.0, super_active: 55.0 };
export const GROUPES_DE_BASE = new Set(["salaries", "independants", "liberaux", "avocats",
  "exploitants", "fonction_publique"]);

/** La part du salaire brut que la CSG retient, cette année-là. */
export function assietteCsg(annee) {
  let part = 1.0;
  for (const [debut, valeur] of ASSIETTES_CSG) {
    if (annee >= debut) part = valeur;
  }
  return part;
}

/**
 * Le groupe de régimes dont relève l'activité : `salaries`, `independants`,
 * `liberaux`, `avocats`, `exploitants`, `fonctionnaires` ; `null` pour une
 * activité dont le modèle n'a pas lu la règle (outre-mer, élus).
 */
export function groupeDeLActivite(moteur, affiliation, annee) {
  if (INDEPENDANTS.has(affiliation)) return "independants";
  const regimes = moteur.affiliations.regimes(affiliation, annee);
  if (regimes.includes("cnavpl")) return "liberaux";
  if (regimes.includes("cnbf")) return "avocats";
  if (regimes.includes("msa_non_salaries")) return "exploitants";
  const famille = moteur.affiliations.famille(affiliation);
  if (["prive", "special", "agricole"].includes(famille)
      || affiliation === "contractuel_public") {
    return "salaries";
  }
  if (famille === "public") return "fonctionnaires";
  return null;
}

/** Le groupe d'une pension : celui de l'activité qui la réduit. */
export function groupeDeLaPension(moteur, regime) {
  if (FONCTION_PUBLIQUE.has(regime)) return "fonction_publique";
  if (OUTRE_MER.has(regime)) return "outre_mer";
  if (AGIRC_ARRCO.has(regime)) return "agirc_arrco";
  if (COMPLEMENTAIRES_DES_INDEPENDANTS.has(regime)) return "rci";
  if (regime === "ircantec") return "ircantec";
  if (regime === "msa_rco") return "rco_agricole";
  if (COMPLEMENTAIRES_DES_LIBERAUX.has(regime)) return "liberales";
  const fiche = moteur.catalogue.obtenir(regime);
  if (!lesDeparts.ETAGES_DES_UNITES.has(fiche.etage)) return "complementaires";
  if (regime === "cnavpl") return "liberaux";
  if (regime === "cnbf") return "avocats";
  if (regime === "msa_non_salaries") return "exploitants";
  if (fiche.famille === "non_salarie") return "independants";
  if (["base_prive", "agricole", "special"].includes(fiche.famille)) return "salaries";
  return "autres";
}

/** Le premier jour d'un mois (AAAA-MM-01). */
export function jour(dateMois) {
  return `${String(dateMois.annee).padStart(4, "0")}-${String(dateMois.mois).padStart(2, "0")}-01`;
}

function moisDe(texte) {
  return new DateMois(Number(texte.slice(0, 4)), Number(texte.slice(5, 7)));
}

const indexDuStatut = (statut) => PRIORITE.indexOf(statut);

/**
 * La durée que L. 351-1 exige pour le taux plein, condition du cumul intégral
 * à l'âge légal : celle du régime général, pour la génération et le départ.
 */
export function dureeDuTauxPlein(moteur, carriere) {
  const periode = periodeDeLiquidation(moteur.catalogue.obtenir("regime_general"),
    carriere.dateLiquidation);
  return dureeRequise(moteur, periode, carriere)[0];
}

/**
 * La pension de l'État est-elle militaire, et la limite d'âge de l'emploi
 * quitté, avant 2004 : celles de la dernière ligne de fonctionnaire avant le
 * départ.
 */
export function fonctionPubliqueQuittee(moteur, carriere) {
  const affiliations = moteur.affiliations;
  for (const ligne of [...carriere.lignes].reverse()) {
    if (ligne.annee > carriere.anneeLiquidation) continue;
    const regimes = affiliations.regimes(ligne.affiliation, ligne.annee);
    if (!regimes.some((code) => FONCTION_PUBLIQUE.has(code))) continue;
    const categorie = affiliations.categorieActive(ligne.affiliation);
    const limite = LIMITES_D_AGE_1970[categorie ?? "aucune"] ?? LIMITES_D_AGE_1970.aucune;
    return [affiliations.pensionMilitaire(ligne.affiliation) !== null, limite];
  }
  return [false, LIMITES_D_AGE_1970.aucune];
}

/** La pension la plus touchée : la première de la priorité la plus haute. */
function laPlusTouchee(pensions) {
  let principale = null;
  for (const pension of pensions) {
    if (principale === null || indexDuStatut(pension.statut) < indexDuStatut(principale.statut)) {
      principale = pension;
    }
  }
  return principale;
}

/** Ce que le droit fait d'une pension, des mois d'une tranche. */
export class PensionEnCumul {
  constructor(regime, statut, regle, motif, montant, reduction, plafond = null) {
    this.regime = regime;
    this.statut = statut;
    this.regle = regle;
    this.motif = motif;
    this.montant = montant;
    this.reduction = reduction;
    this.plafond = plafond;
  }

  donnees() {
    return { regime: this.regime, statut: this.statut, regle: this.regle,
      motif: this.motif, montant: this.montant, reduction: this.reduction,
      plafond: this.plafond };
  }
}

/**
 * Des mois consécutifs d'une même année, où le droit traite chaque pension de
 * la même façon. Les montants sont mensuels, en euros de l'année.
 */
export class TrancheDeCumul {
  constructor({ debut, fin, revenu, pensions, plafond, parRegime }) {
    this.debut = debut;
    this.fin = fin;
    this.revenu = revenu;
    this.pensions = pensions;
    this.plafond = plafond;
    this.par_regime = parRegime;
  }

  get mois() {
    return this.fin.rang - this.debut.rang;
  }

  get reduction() {
    return this.par_regime.reduce((total, p) => total + p.reduction, 0.0);
  }

  get principale() {
    return laPlusTouchee(this.par_regime);
  }

  get statut() {
    const principale = this.principale;
    return principale !== null ? principale.statut : LIBRE;
  }

  donnees() {
    const principale = this.principale;
    return {
      debut: jour(this.debut), fin: jour(this.fin), mois: this.mois, statut: this.statut,
      regle: principale !== null ? principale.regle : null,
      motif: principale !== null ? principale.motif : null,
      revenu: this.revenu, pensions: this.pensions, plafond: this.plafond,
      reduction: this.reduction, par_regime: this.par_regime.map((p) => p.donnees()),
    };
  }
}

/** L'activité exercée après le départ, et ce que chaque pension en garde. */
export class Cumul {
  constructor({ debut, fin, affiliation, employeur, groupe, integralDepuis, tranches }) {
    this.debut = debut;
    this.fin = fin;
    this.affiliation = affiliation;
    this.employeur = employeur;
    this.groupe = groupe;
    this.integral_depuis = integralDepuis;
    this.tranches = tranches;
  }

  /** Ce que l'activité fait perdre de pension, en tout, en euros de chaque année. */
  get non_servi() {
    return this.tranches.reduce((total, t) => total + t.reduction * t.mois, 0.0);
  }

  donnees() {
    return {
      debut: jour(this.debut), fin: jour(this.fin), affiliation: this.affiliation,
      employeur: this.employeur, groupe: this.groupe,
      integral_depuis: this.integral_depuis !== null ? jour(this.integral_depuis) : null,
      non_servi: this.non_servi, tranches: this.tranches.map((t) => t.donnees()),
    };
  }
}

/** Le calcul, mois par mois, d'une activité après le départ. */
class Calcul {
  constructor(moteur, carriere, resultat, pensionsDe, anneeCourante) {
    const emploi = carriere.emploiRetraite;
    this.moteur = moteur;
    this.carriere = carriere;
    this.pensionsDe = pensionsDe;
    this.debut = emploi.debut;
    this.fin = emploi.fin;
    this.affiliation = emploi.affiliation;
    this.employeur = emploi.employeur;
    this.groupe = groupeDeLActivite(moteur, this.affiliation, this.debut.annee);
    this.public = moteur.affiliations.famille(this.affiliation) === "public";
    this.declare = carriere.dateLiquidation;
    this.ancre = Math.max(anneeCourante, this.declare.annee);
    this.premiere = this.declare.rang;
    this.pensions = resultat.pensions_par_regime.map((p) => [
      p.regime, (p.date_effet ? moisDe(p.date_effet) : this.declare).rang,
      groupeDeLaPension(moteur, p.regime),
    ]);
    this.ageLegal = lesDeparts.ageLegal(moteur, carriere);
    const automatique = moteur.agesAnnulationDecote.age(carriere.generation);
    this.ageAutomatique = automatique !== null ? automatique[0] : 65.0;
    // La durée du cumul intégral : celle des régimes en annuités, ou, à une
    // carrière tout en points, celle de L. 351-1.
    const requis = resultat.trimestres_requis || dureeDuTauxPlein(moteur, carriere);
    this.duree = resultat.trimestres_valides >= requis;
    [this.militaire, this.limiteDAge] = fonctionPubliqueQuittee(moteur, carriere);
    this.independant = carriere.lignes.some((ligne) => ligne.annee <= this.declare.annee
      && INDEPENDANTS.has(ligne.affiliation));
    this.dernier = this.dernierSalaire();
    this.moyen = this.salaireMoyen();
    this.lignes = new Map();
    for (const ligne of carriere.lignes_apres_depart) {
      this.lignes.set(ligne.annee, (this.lignes.get(ligne.annee) ?? 0.0) + ligne.revenu);
    }
    this.annees = new Map();
    this.revalorisations = new Map();
    this.deductions = new Map();
    this.suspensions = new Map();
  }

  // -- la carrière d'avant le départ --------------------------------------------------

  emplois() {
    return this.carriere.lignes.filter((l) => l.type_periode === "emploi" && l.revenu > 0
      && l.annee <= this.declare.annee);
  }

  dernierSalaire() {
    const emplois = this.emplois();
    if (emplois.length === 0) return null;
    const annee = Math.max(...emplois.map((l) => l.annee));
    const derniere = emplois.filter((l) => l.annee === annee);
    const mois = Math.max(1, Math.round(Math.max(...derniere.map((l) => l.fraction_annee)) * 12));
    const brut = derniere.reduce((total, l) => total
      + l.revenu / (l.quotite > 0 && l.quotite < 1 ? l.quotite : 1.0), 0.0);
    return [brut / mois, annee];
  }

  salaireMoyen() {
    const emplois = this.emplois();
    const annees = [...new Set(emplois.map((l) => l.annee))].sort((a, b) => a - b).slice(-10);
    if (annees.length === 0) return null;
    const macro = this.moteur.macro;
    let total = 0.0;
    let mois = 0.0;
    for (const annee of annees) {
      const lignes = emplois.filter((l) => l.annee === annee);
      total += lignes.reduce((somme, l) => somme + l.revenu, 0.0)
        * macro.coefficientPrix(annee, this.declare.annee);
      mois += Math.max(...lignes.map((l) => l.fraction_annee)) * 12;
    }
    return [mois ? total / mois : 0.0, this.declare.annee];
  }

  // -- l'année et le mois -------------------------------------------------------------

  annee(annee) {
    if (!this.annees.has(annee)) {
      let [pensions, majoration] = this.pensionsDe(Math.min(annee, this.ancre));
      if (annee > this.ancre) {
        const prix = this.moteur.macro.coefficientPrix(this.ancre, annee);
        const menees = {};
        for (const [regime, montant] of Object.entries(pensions)) menees[regime] = montant * prix;
        pensions = menees;
        majoration *= prix;
      }
      let mois = 0;
      for (let r = this.debut.rang; r < this.fin.rang; r += 1) {
        if (DateMois.depuisRang(r).annee === annee) mois += 1;
      }
      const macro = this.moteur.macro;
      const reference = this.moteur.minimumGaranti.reference(annee);
      this.annees.set(annee, {
        pensions, majoration, mois,
        revenu: mois ? (this.lignes.get(annee) ?? 0.0) / mois : 0.0,
        smic: macro.smic_horaire.valeur(annee) * HEURES_SMIC / 12.0,
        plafondSecuriteSociale: macro.plafond_securite_sociale.valeur(annee),
        minimumGaranti: reference !== null ? reference[0] : 0.0,
      });
    }
    return this.annees.get(annee);
  }

  age(mois) {
    return this.carriere.ageAu(mois);
  }

  integral(mois) {
    if (mois.rang < LOI_2009) return false;
    for (const [, dateEffet] of this.pensions) {
      if (dateEffet <= mois.rang) continue;
      if (mois.rang >= ORDRE_DES_AGES
          && this.carriere.ageAu(DateMois.depuisRang(dateEffet)) > this.ageLegal + 1e-9) {
        continue;
      }
      return false;
    }
    const age = this.age(mois);
    // La première pension de 2027 ne se cumule entièrement qu'à l'âge du taux
    // plein automatique (L. 161-22, III, A, 3°).
    if (this.premiere >= PREMIERE_2027) return age >= this.ageAutomatique - 1e-9;
    return age >= this.ageAutomatique - 1e-9 || (age >= this.ageLegal - 1e-9 && this.duree);
  }

  revalorisation(mois) {
    if (mois.rang < REVALORISATION_2010) return 1.0;
    if (!this.revalorisations.has(mois.rang)) {
      const depuis = jour(this.declare);
      const jusqua = mois.annee <= this.ancre ? jour(mois)
        : `${String(this.ancre).padStart(4, "0")}-12-31`;
      let coefficient = jusqua > depuis
        ? this.moteur.revalorisationsPensions.generale(depuis, jusqua, false, null)[0]
        : 1.0;
      if (mois.annee > this.ancre) {
        coefficient *= this.moteur.macro.coefficientPrix(this.ancre, mois.annee);
      }
      this.revalorisations.set(mois.rang, coefficient);
    }
    return this.revalorisations.get(mois.rang);
  }

  plafondSalarie(mois, annee) {
    let dernier = 0.0;
    if (this.dernier !== null) {
      const [mensuel, sonAnnee] = this.dernier;
      dernier = mensuel * assietteCsg(sonAnnee) * this.revalorisation(mois);
    }
    const part = mois.rang >= LOI_2009 ? PART_SMIC_2009 : PART_SMIC_2004;
    return Math.max(dernier, part * annee.smic);
  }

  plafondAgircArrco(mois, annee) {
    let plafond = this.plafondSalarie(mois, annee);
    if (this.moyen !== null && mois.rang >= LOI_2009) {
      const [mensuel, sonAnnee] = this.moyen;
      plafond = Math.max(plafond, mensuel * assietteCsg(sonAnnee) * this.revalorisation(mois));
    }
    return plafond;
  }

  version(mois, dateEffet) {
    if (dateEffet < LOI_1983) return AVANT_1983;
    if (this.premiere >= PREMIERE_2027) return AGES_2027;
    if (mois.rang < LOI_2009) return dateEffet < LOI_2004 ? RUPTURE_1983 : PLAFOND_2004;
    if (this.premiere < PREMIERE_2015) return LIBERALISE_2009;
    return mois.rang < REDUCTION_SALARIES ? PREMIERES_2015 : REDUCTION_2015;
  }

  dansLesSixMois(mois, dateEffet) {
    const limite = dateEffet + SIX_MOIS;
    return this.employeur === "dernier" && this.debut.rang < limite && mois.rang < limite;
  }

  // -- la règle de chaque pension -----------------------------------------------------

  mois(mois) {
    const annee = this.annee(mois.annee);
    const servies = this.pensions.filter(([regime, dateEffet]) => dateEffet <= mois.rang
      && (annee.pensions[regime] ?? 0.0) > 0);
    const montants = {};
    for (const [regime] of servies) montants[regime] = (annee.pensions[regime] ?? 0.0) / 12.0;
    const total = Object.values(montants).reduce((somme, m) => somme + m, 0.0)
      + (servies.length ? annee.majoration / 12.0 : 0.0);
    const integral = this.integral(mois);
    const resultats = [];
    const base2027 = servies.filter(([, , groupe]) => GROUPES_DE_BASE.has(groupe))
      .reduce((somme, [regime]) => somme + montants[regime], 0.0);
    // Les points du RCI, du RCO et du NRCO font une seule pension.
    const complementaire = servies.filter(([, , groupe]) => groupe === "rci")
      .reduce((somme, [regime]) => somme + montants[regime], 0.0);
    // Les complémentaires que la règle de 2027 réduit après les bases.
    const complementaires2027 = servies
      .filter(([, , groupe]) => GROUPES_COMPLEMENTAIRES_2027.has(groupe))
      .reduce((somme, [regime]) => somme + montants[regime], 0.0);
    for (const [regime, dateEffet, groupe] of servies) {
      const montant = montants[regime];
      let decision;
      if (this.premiere >= PREMIERE_2027 && GROUPES_DE_BASE.has(groupe)) {
        decision = this.regle2027(mois, dateEffet, groupe, montant, annee, base2027);
      } else if (this.premiere >= PREMIERE_2027 && GROUPES_COMPLEMENTAIRES_2027.has(groupe)) {
        decision = this.complementaire2027(mois, dateEffet, montant,
          montant / complementaires2027, annee, base2027);
      } else if (groupe === "fonction_publique") {
        decision = this.fonctionnaire(mois, regime, dateEffet, montant, annee, integral);
      } else if (groupe === "agirc_arrco") {
        decision = this.agircArrco(mois, dateEffet, montant, annee, total, integral);
      } else if (groupe === "rci") {
        decision = this.complementaireDesIndependants(mois, dateEffet, montant,
          montant / complementaire, annee, integral, servies, montants);
      } else if (groupe === "ircantec") {
        decision = this.ircantec(mois, dateEffet, montant, annee, total, integral);
      } else if (groupe === "rco_agricole") {
        decision = this.rcoAgricole();
      } else if (groupe === "liberales") {
        decision = this.complementaireDesLiberaux(mois, regime, dateEffet, montant, annee,
          integral, servies, montants);
      } else if (groupe === "complementaires" || groupe === "autres") {
        decision = [LIBRE, "", "non_lue", 0.0, null];
      } else if (!this.concerne(regime, groupe)) {
        decision = [LIBRE, "", "autre_regime", 0.0, null];
      } else if (this.groupe === "salaries") {
        decision = this.salarie(mois, dateEffet, montant, annee, total, integral);
      } else if (SEUILS_NON_SALARIES[this.groupe] !== undefined) {
        decision = this.nonSalarie(mois, dateEffet, this.groupe, montant, annee, integral,
          servies, montants);
      } else {
        decision = [NON_CALCULE, "", "regle_non_lue", 0.0, null];
      }
      const [statut, regle, motif, reduction, plafond] = decision;
      resultats.push(new PensionEnCumul(regime, statut, regle, motif, montant,
        Math.min(montant, Math.max(0.0, reduction)), plafond));
    }
    const principale = laPlusTouchee(resultats);
    return [resultats, principale !== null ? principale.plafond : null];
  }

  concerne(regime, groupe) {
    if (groupe === this.groupe) return true;
    return this.groupe === "independants" && this.independant && ALIGNES.has(regime);
  }

  salarie(mois, dateEffet, montant, annee, total, integral) {
    const regle = this.version(mois, dateEffet);
    if (regle === AVANT_1983) return [LIBRE, regle, "avant_1983", 0.0, null];
    if (regle === RUPTURE_1983) {
      if (this.employeur === "dernier") return [NON_DUE, regle, "dernier_employeur", montant, null];
      return [LIBRE, regle, "autre_employeur", 0.0, null];
    }
    if (integral) return [INTEGRAL, regle, "taux_plein", 0.0, null];
    if (this.dansLesSixMois(mois, dateEffet)) return [NON_DUE, regle, "six_mois", montant, null];
    const plafond = this.plafondSalarie(mois, annee);
    const depassement = total + annee.revenu * assietteCsg(mois.annee) - plafond;
    if (depassement <= 0) return [PLAFONNEE, regle, "sous_le_plafond", 0.0, plafond];
    if (regle === REDUCTION_2015) return [REDUITE, regle, "depassement", depassement, plafond];
    return [SUSPENDUE, regle, "depassement", montant, plafond];
  }

  agircArrco(mois, dateEffet, montant, annee, total, integral) {
    const regimes = this.moteur.affiliations.regimes(this.affiliation, mois.annee);
    if (!regimes.some((code) => AGIRC_ARRCO.has(code))) {
      return [LIBRE, "", "autre_regime", 0.0, null];
    }
    const regle = this.version(mois, dateEffet);
    if (regle === AVANT_1983) return [LIBRE, regle, "avant_1983", 0.0, null];
    if (regle === RUPTURE_1983) {
      if (this.employeur === "dernier") return [NON_DUE, regle, "dernier_employeur", montant, null];
      return [LIBRE, regle, "autre_employeur", 0.0, null];
    }
    if (integral) return [INTEGRAL, regle, "taux_plein", 0.0, null];
    if (this.dansLesSixMois(mois, dateEffet)) return [NON_DUE, regle, "six_mois", montant, null];
    const plafond = this.plafondAgircArrco(mois, annee);
    if (total + annee.revenu * assietteCsg(mois.annee) <= plafond) {
      return [PLAFONNEE, regle, "sous_le_plafond", 0.0, plafond];
    }
    return [SUSPENDUE, regle, "depassement", montant, plafond];
  }

  nonSalarie(mois, dateEffet, groupe, montant, annee, integral, servies, montants) {
    if (groupe === "independants" && dateEffet < LOI_2004) {
      if (dateEffet < ARTISANS_1984) return [LIBRE, AVANT_1983, "avant_1984", 0.0, null];
      if (mois.rang < LOI_2009) {
        if (this.employeur === "dernier") {
          return [NON_DUE, RUPTURE_1983, "meme_entreprise", montant, null];
        }
        return [LIBRE, RUPTURE_1983, "autre_entreprise", 0.0, null];
      }
    }
    if (dateEffet < LOI_2004 && mois.rang < LOI_2009) {
      return [NON_CALCULE, "", "regle_non_lue", 0.0, null];
    }
    let regle;
    if (mois.rang < LOI_2009) regle = PLAFOND_2004;
    else if (this.premiere < PREMIERE_2015) regle = LIBERALISE_2009;
    else if (mois.rang < REDUCTION_NON_SALARIES) regle = PREMIERES_2015;
    else regle = REDUCTION_2015;
    if (integral) return [INTEGRAL, regle, "taux_plein", 0.0, null];
    const seuil = this.seuilNonSalarie(mois, groupe, annee);
    const depassement = annee.revenu - seuil;
    if (depassement <= 0) return [PLAFONNEE, regle, "sous_le_plafond", 0.0, seuil];
    if (regle !== REDUCTION_2015) {
      const suspension = this.suspension(mois, groupe);
      if (suspension !== null && !suspension[0].has(mois.rang)) {
        return [PLAFONNEE, regle, HORS_DES_MOIS_SUSPENDUS, 0.0, seuil];
      }
      return [SUSPENDUE, regle, "depassement", montant, seuil];
    }
    const duGroupe = servies.filter(([code, , g]) => this.concerne(code, g))
      .reduce((somme, [code]) => somme + montants[code], 0.0);
    const part = duGroupe > 0 ? montant / duGroupe : 0.0;
    return [REDUITE, regle, "depassement", depassement * part, seuil];
  }

  /**
   * Le seuil par mois d'activité : la moitié du plafond pour l'artisan et le
   * commerçant ; le plafond pour le libéral, et avant le 17 janvier 2011 celui
   * de l'année, sur ses seuls mois d'activité.
   */
  seuilNonSalarie(mois, groupe, annee) {
    if (groupe === "liberaux" && mois.rang < LIBERAUX_2011) {
      return annee.plafondSecuriteSociale / annee.mois;
    }
    return SEUILS_NON_SALARIES[groupe] * annee.plafondSecuriteSociale / 12.0;
  }

  /**
   * Les mois de l'année de `mois` que le dépassement suspend (un `Set` de
   * rangs), et le nombre de ceux de l'activité hors du cumul intégral ; `null`
   * quand la pension l'est chaque mois au-delà du seuil — le libéral avant le
   * 17 janvier 2011, ou faute de pension de base. Voir le Python.
   */
  suspension(mois, groupe) {
    if (groupe === "liberaux" && mois.rang < LIBERAUX_2011) return null;
    const cle = `${groupe}:${mois.annee}`;
    if (!this.suspensions.has(cle)) this.suspensions.set(cle, this.suspendre(groupe, mois.annee));
    return this.suspensions.get(cle);
  }

  suspendre(groupe, anneeCivile) {
    const annee = this.annee(anneeCivile);
    const couverts = [];
    for (let r = this.debut.rang; r < this.fin.rang; r += 1) {
      const mois = DateMois.depuisRang(r);
      if (mois.annee === anneeCivile && !this.integral(mois)
          && (groupe !== "liberaux" || r >= LIBERAUX_2011)) {
        couverts.push(mois);
      }
    }
    const dernier = couverts[couverts.length - 1];
    const pensions = new Map();
    for (const [regime, dateEffet, g] of this.pensions) {
      const annuelle = annee.pensions[regime] ?? 0.0;
      if (this.concerne(regime, g) && dateEffet <= dernier.rang && annuelle > 0) {
        pensions.set(regime, annuelle / 12.0);
      }
    }
    let brute = 0.0;
    for (const montant of pensions.values()) brute += montant;
    if (brute <= 0) return null;
    const seuil = this.seuilNonSalarie(dernier, groupe, annee);
    const depassement = (annee.revenu - seuil) * couverts.length;
    let nombre = Math.floor(depassement / (brute * this.partNette(anneeCivile, pensions))
      + 1e-9);
    if (groupe === "independants") nombre = Math.max(1, nombre);
    nombre = Math.min(nombre, couverts.length);
    return [new Set(couverts.slice(couverts.length - nombre).map((m) => m.rang)),
      couverts.length];
  }

  /**
   * Ce que les prélèvements de l'année laissent de ces pensions (une `Map`),
   * en part de leur brut : la CSG au taux plein, la CRDS, la CASA, et la
   * cotisation maladie de leur régime.
   */
  partNette(anneeCivile, pensions) {
    const historiques = this.moteur.prelevementsHistoriques;
    let brute = 0.0;
    for (const montant of pensions.values()) brute += montant;
    const parts = new Map();
    for (const serie of [...historiques.regimes_des_pensions.keys()].sort()) {
      const regimes = historiques.regimes_des_pensions.get(serie);
      let part = 0.0;
      for (const [regime, montant] of pensions) if (regimes.has(regime)) part += montant;
      if (part > 0) parts.set(serie, part / brute);
    }
    return 1.0 - historiques.tauxPensionAnnuel(anneeCivile, parts);
  }

  /**
   * La complémentaire de l'artisan et du commerçant, qui suit leur base :
   * suspendue avec elle depuis 2009, réduite comme elle du dépassement entier
   * depuis juillet 2024, et, pour la première pension de 2027, de ce que la
   * base n'absorbe pas ; `part` est celle de ses points dans la pension que le
   * RCI, le RCO et le NRCO font ensemble.
   */
  complementaireDesIndependants(mois, dateEffet, montant, part, annee, integral, servies,
    montants) {
    if (mois.rang < COMPLEMENTAIRES_2009) return [LIBRE, RCI_AVANT_2009, "non_lue", 0.0, null];
    if (this.groupe !== "independants") return [LIBRE, "", "autre_regime", 0.0, null];
    const [statut, , motif, , seuil] = this.nonSalarie(mois, dateEffet, "independants",
      montant, annee, integral, servies, montants);
    const regle = mois.rang < SECTION_3_RCI ? RCI_2009 : RCI_2024;
    if (statut === SUSPENDUE) return [SUSPENDUE, regle, motif, montant, seuil];
    if (statut !== REDUITE) return [statut, regle, motif, 0.0, seuil];
    if (regle === RCI_2009) return [PLAFONNEE, regle, "base_reduite", 0.0, seuil];
    return [REDUITE, regle, motif, (annee.revenu - seuil) * part, seuil];
  }

  /**
   * L. 161-22, III, A, de 2027, qui vise toute pension « de base ou
   * complémentaire » : la complémentaire — le RCI, l'Ircantec, la RCO
   * agricole, les sections libérales — perd ce que les pensions de base
   * n'absorbent pas, au prorata (`part`) de celles que la règle réduit.
   */
  complementaire2027(mois, dateEffet, montant, part, annee, base2027) {
    const [statut, , motif, reduction, plafond] = this.regle2027(mois, dateEffet,
      "complementaires", montant, annee, base2027);
    if (statut !== REDUITE) return [statut, RCI_2027, motif, reduction, plafond];
    const reste = annee.revenu * assietteCsg(mois.annee) - base2027;
    if (reste <= 0) return [PLAFONNEE, RCI_2027, "imputee_sur_la_base", 0.0, null];
    return [REDUITE, RCI_2027, motif, reste * part, null];
  }

  /**
   * L'allocation de l'Ircantec : entière avant 2004 ; depuis, la règle de
   * L. 161-22 pour l'activité qui y cotise, celle de la base du salarié ;
   * depuis 2021, sans le troisième alinéa qui réduit chaque pension.
   */
  ircantec(mois, dateEffet, montant, annee, total, integral) {
    if (mois.rang < IRCANTEC_L_161_22) return [LIBRE, IRCANTEC_AVANT_2004, "non_lue", 0.0, null];
    if (!this.moteur.affiliations.regimes(this.affiliation, mois.annee).includes("ircantec")) {
      return [LIBRE, "", "autre_regime", 0.0, null];
    }
    const [statut, , motif, reduction, plafond] = this.salarie(mois, dateEffet, montant, annee,
      total, integral);
    if (mois.rang < IRCANTEC_SANS_REDUCTION) {
      return [statut, IRCANTEC_2004, motif, reduction, plafond];
    }
    if (motif === "depassement") {
      return [PLAFONNEE, IRCANTEC_2020, "sans_le_troisieme_alinea", 0.0, plafond];
    }
    return [statut, IRCANTEC_2020, motif, reduction, plafond];
  }

  /**
   * La RCO agricole, que D. 732-157 soumet à L. 732-39 et L. 732-40 : la règle
   * de la base de l'exploitant, que le modèle n'a pas lue.
   */
  rcoAgricole() {
    if (this.groupe !== "exploitants") return [LIBRE, "", "autre_regime", 0.0, null];
    return [NON_CALCULE, RCO_AGRICOLE_2003, "regle_non_lue", 0.0, null];
  }

  /**
   * La complémentaire d'une section libérale, selon la règle que ses statuts
   * écrivent ce mois-là (`REGLES_DES_SECTIONS`).
   */
  complementaireDesLiberaux(mois, regime, dateEffet, montant, annee, integral, servies,
    montants) {
    let regleDesStatuts = null;
    for (const [debut, regle] of REGLES_DES_SECTIONS[regime] ?? []) {
      if (mois.rang >= debut) regleDesStatuts = regle;
    }
    if (regleDesStatuts === null) return [LIBRE, SECTIONS_STATUTS, "non_lue", 0.0, null];
    if (regleDesStatuts === SANS_SUSPENSION) {
      return [LIBRE, SECTIONS_STATUTS, "sans_suspension", 0.0, null];
    }
    if (Object.hasOwn(PROFESSIONS_DES_STATUTS, regleDesStatuts)) {
      if (this.affiliation !== PROFESSIONS_DES_STATUTS[regleDesStatuts]) {
        return [LIBRE, "", "autre_regime", 0.0, null];
      }
      if (regleDesStatuts === A_LA_REPRISE) {
        return [SUSPENDUE, SECTIONS_STATUTS, "reprise", montant, null];
      }
      return [NON_DUE, SECTIONS_STATUTS, "notaire_liberal", montant, null];
    }
    if (this.groupe !== "liberaux") return [LIBRE, "", "autre_regime", 0.0, null];
    const [statut, , motif, , seuil] = this.nonSalarie(mois, dateEffet, "liberaux", montant,
      annee, integral, servies, montants);
    const hors = motif === HORS_DES_MOIS_SUSPENDUS;
    if (statut !== SUSPENDUE && statut !== REDUITE && !hors) {
      return [statut, SECTIONS_STATUTS, motif, 0.0, seuil];
    }
    const depassement = annee.revenu - seuil;
    if (regleDesStatuts === DEPASSEMENT_ENTIER) {
      return [REDUITE, SECTIONS_STATUTS, "depassement", depassement, seuil];
    }
    if (regleDesStatuts === APRES_LA_BASE) {
      let base = servies.filter(([, , groupe]) => groupe === "liberaux")
        .reduce((somme, [code]) => somme + montants[code], 0.0);
      // La base suspendue quelques mois n'absorbe du dépassement que ces mois-là.
      const suspension = statut === REDUITE ? null : this.suspension(mois, "liberaux");
      if (suspension !== null) base *= suspension[0].size / suspension[1];
      if (depassement <= base) {
        return [PLAFONNEE, SECTIONS_STATUTS, "imputee_sur_la_base", 0.0, seuil];
      }
      return [REDUITE, SECTIONS_STATUTS, "depassement", depassement - base, seuil];
    }
    if (hors) return [PLAFONNEE, SECTIONS_STATUTS, motif, 0.0, seuil];
    if (statut === SUSPENDUE) return [SUSPENDUE, SECTIONS_STATUTS, motif, montant, seuil];
    if (regleDesStatuts === AVEC_LA_BASE) {
      return [PLAFONNEE, SECTIONS_STATUTS, "base_reduite", 0.0, seuil];
    }
    return [REDUITE, SECTIONS_STATUTS, motif, depassement, seuil];
  }

  fonctionnaire(mois, regime, dateEffet, montant, annee, integral) {
    if (dateEffet < LOI_2004) {
      if (!this.public) return [LIBRE, FP_1970, "employeur_prive", 0.0, null];
      if (this.militaire) return [NON_CALCULE, FP_1970, "militaire", 0.0, null];
      if (this.age(mois) >= this.limiteDAge - 1e-9) {
        return [LIBRE, FP_1970, "limite_d_age", 0.0, null];
      }
      if (annee.revenu <= FRANCHISE_1970 * montant) {
        return [PLAFONNEE, FP_1970, "quart_de_la_pension", 0.0, FRANCHISE_1970 * montant];
      }
      return [REDUITE, FP_1970, "remuneration", annee.revenu, null];
    }
    let regle;
    if (mois.rang < LOI_2009) regle = FP_2004;
    else if (this.premiere < PREMIERE_2015) regle = FP_2009;
    else regle = FP_2015;
    if (mois.rang >= LOI_2009 && integral) return [INTEGRAL, regle, "taux_plein", 0.0, null];
    const toutEmployeur = this.premiere >= PREMIERE_2015 && !this.militaire;
    if (!(this.public || toutEmployeur)) return [LIBRE, regle, "employeur_prive", 0.0, null];
    const [deduction, plafond] = this.deductionFonctionPublique(regime, dateEffet, mois.annee);
    if (deduction <= 0) return [PLAFONNEE, regle, "sous_le_plafond", 0.0, plafond];
    return [REDUITE, regle, "depassement", deduction, plafond];
  }

  deductionFonctionPublique(regime, dateEffet, anneeCivile) {
    const annee = this.annee(anneeCivile);
    const mois = [];
    for (let r = this.debut.rang; r < this.fin.rang; r += 1) {
      const m = DateMois.depuisRang(r);
      if (m.annee === anneeCivile) mois.push(m);
    }
    const couverts = mois.filter((m) => !(m.rang >= LOI_2009 && this.integral(m)));
    const annuelle = annee.pensions[regime] ?? 0.0;
    let servis = 0;
    for (let m = 1; m <= 12; m += 1) {
      if (new DateMois(anneeCivile, m).rang >= dateEffet) servis += 1;
    }
    const pensionDeLAnnee = annuelle * servis / 12.0;
    const plafond = PART_DE_LA_PENSION * pensionDeLAnnee
      + ABATTEMENT_MINIMUM_GARANTI * annee.minimumGaranti;
    const cle = `${regime}/${anneeCivile}`;
    if (!this.deductions.has(cle)) {
      const revenus = annee.revenu * couverts.length;
      const excedent = Math.max(0.0, revenus - plafond);
      this.deductions.set(cle, couverts.length ? excedent / couverts.length : 0.0);
    }
    return [this.deductions.get(cle), plafond / 12.0];
  }

  regle2027(mois, dateEffet, groupe, montant, annee, base) {
    const regle = groupe === "fonction_publique" ? FP_2027 : AGES_2027;
    const age = this.age(mois);
    if (age >= this.ageAutomatique - 1e-9) return [INTEGRAL, regle, "age_du_taux_plein", 0.0, null];
    if (this.dansLesSixMois(mois, dateEffet)) return [NON_DUE, regle, "six_mois", montant, null];
    if (age >= this.ageLegal - 1e-9) {
      return [SEUIL_NON_PUBLIE, regle, "seuil_non_publie", 0.0, null];
    }
    const revenu = annee.revenu * assietteCsg(mois.annee);
    const part = base > 0 ? montant / base : 0.0;
    if (revenu <= 0) return [PLAFONNEE, regle, "sans_revenu", 0.0, null];
    return [REDUITE, regle, "avant_l_age_legal", revenu * part, null];
  }
}

function memeCle(a, b) {
  if (a.annee !== b.annee || a.pensions.length !== b.pensions.length) return false;
  return a.pensions.every((p, i) => {
    const q = b.pensions[i];
    return p.regime === q.regime && p.statut === q.statut && p.regle === q.regle
      && p.motif === q.motif && p.reduction === q.reduction && p.plafond === q.plafond;
  });
}

/**
 * Le cumul de l'activité que `carriere` exerce après son départ, ou `null`
 * sans elle. `resultat` est le scénario 1 au départ ; `pensionsDe(annee)` rend
 * `[pensions, majoration]`, la pension annuelle de chaque régime menée à cette
 * année — l'étape « faire vivre » —, et la majoration pour enfants ; au-delà
 * de `anneeCourante`, le module les mène par les prix.
 */
export function cumuler(moteur, carriere, resultat, pensionsDe, anneeCourante) {
  if (carriere.emploiRetraite === null || resultat === null) return null;
  const calcul = new Calcul(moteur, carriere, resultat, pensionsDe, anneeCourante);
  const tranches = [];
  let integralDepuis = null;
  let courante = null;
  const fermer = () => {
    tranches.push(new TrancheDeCumul({
      debut: DateMois.depuisRang(courante.debut), fin: DateMois.depuisRang(courante.fin),
      revenu: courante.revenu, pensions: courante.pensions, plafond: courante.plafond,
      parRegime: courante.parRegime,
    }));
  };
  for (let r = calcul.debut.rang; r < calcul.fin.rang; r += 1) {
    const mois = DateMois.depuisRang(r);
    if (integralDepuis === null && calcul.integral(mois)) integralDepuis = mois;
    const [parRegime, plafond] = calcul.mois(mois);
    const annee = calcul.annee(mois.annee);
    const pensions = parRegime.reduce((somme, p) => somme + p.montant, 0.0)
      + (parRegime.length ? annee.majoration / 12.0 : 0.0);
    const cle = { annee: mois.annee, pensions: parRegime };
    if (courante !== null && memeCle(courante.cle, cle)) {
      courante.fin = r + 1;
      continue;
    }
    if (courante !== null) fermer();
    courante = { cle, debut: r, fin: r + 1, revenu: annee.revenu, pensions, plafond,
      parRegime };
  }
  if (courante !== null) fermer();
  return new Cumul({
    debut: calcul.debut, fin: calcul.fin, affiliation: calcul.affiliation,
    employeur: calcul.employeur, groupe: calcul.groupe, integralDepuis, tranches,
  });
}
