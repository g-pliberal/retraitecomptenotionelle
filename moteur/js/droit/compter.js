/**
 * Compter les durées (docs/architecture.md, § 7.2).
 *
 * Jumeau de `src/retraite_notionnelle/droit/compter.py`, fonction pour
 * fonction : les trimestres de chaque compte — l'assurance, périodes
 * assimilées comprises ; les services, qui proratisent la pension de la
 * fonction publique ; la durée cotisée —, régime par régime et année par
 * année, et les trimestres des enfants, dans le régime que la priorité entre
 * régimes désigne (R. 173-15) : `majorationPourEnfants`. Et les trimestres
 * des périodes assimilées que la chronologie porte : `trimestresAssimiles`.
 * Et les services du
 * code des pensions au jour, que le décompte final arrondit une seule fois
 * (R. 26) : `joursDeLaLigne`, `arrondirLesServices`. Ce que l'étape écrit,
 * `Durees`, suit son schéma, `data/reference/etapes/compter_les_durees.yaml`.
 */

import { DateMois, trimestresCivils } from "../calendrier.js";
import * as chrono from "../chronologie.js";
import { fiabiliteDepuisTexte, nomFiabilite, Fiabilite } from "../serie.js";
import { ligneCotisee, periodeDeLiquidation } from "./commun.js";
import * as coordonner from "./coordonner.js";
import { compterLesPeriodes, familleDesRegimes } from "./etranger.js";

/**
 * La version du schéma de l'étape : la deuxième compte les trimestres des
 * enfants enfant par enfant, chacun dans son régime ; la troisième, les
 * trimestres que les périodes hors de France apportent ; la quatrième, ceux
 * que les emplois classés ajoutent ; la cinquième, les services du code des
 * pensions au jour ; la sixième, ceux des périodes assimilées.
 */
export const SCHEMA_VERSION = 6;

/**
 * La fiche du décompte des services du code des pensions, lue à la date
 * d'effet (`decompteDesServices`). Voir `FICHE_DU_DECOMPTE` du Python.
 */
export const FICHE_DU_DECOMPTE = "decompte_des_services_fonction_publique";

/** Le mois des pensions, en jours : l'année de trois cent soixante jours. */
export const JOURS_PAR_MOIS = 30;
export const JOURS_PAR_TRIMESTRE = 90;
export const JOURS_PAR_AN = 360;

/**
 * Ce que le minimum garanti compte (`contenu.parametres.minimum_garanti`) :
 * les services effectifs arrondis, ou le décompte de la pension.
 */
export const MINIMA_DU_DECOMPTE = Object.freeze(["services_effectifs", "liquidation"]);

/** La tolérance des jours, qu'un produit par une quotité laisse flottants. */
const EPSILON_JOURS = 1e-6;

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
 * La fiche de la bonification du cinquième des militaires (L. 12, i), que
 * l'inventaire des avantages mesure à part. Voir `FICHE_DES_MILITAIRES` du Python.
 */
export const FICHE_DES_MILITAIRES = "bonification_cinquieme_militaires";

/**
 * Les fiches des bonifications et des majorations que l'emploi CLASSÉ, ou le
 * service militaire, ouvre dans le régime qui le pensionne, lues par
 * `FichesDatees` à la date d'effet, dans l'ordre du cumul que les versions de
 * septembre 2023 bornent. Voir `FICHES_DES_EMPLOIS` du Python.
 */
export const FICHES_DES_EMPLOIS = Object.freeze([
  "bonification_cinquieme_police_penitentiaire", "bonification_cinquieme_sapeurs_pompiers",
  FICHE_DES_MILITAIRES, "majoration_duree_hospitaliers_actifs",
]);

/**
 * Ce qu'une version de ces fiches accorde : une `bonification`, aux services
 * liquidés et à la durée tous régimes, ou une `majoration`, à la seule durée que
 * le régime oppose à sa décote. Voir `NATURES_DES_EMPLOIS` du Python.
 */
export const NATURES_DES_EMPLOIS = Object.freeze(["bonification", "majoration"]);

/**
 * Les conditions qu'une version de ces fiches pose à la carrière, lues sur la
 * table des emplois classés de la génération : la durée de l'âge minoré dans les
 * statuts de la fiche (ou la radiation pour invalidité), les conditions de la
 * catégorie active réunies à la radiation dans l'un de ces statuts, la seule
 * durée de services actifs, ou les années dans l'emploi et dans la fonction
 * publique civile, l'âge anticipé atteint (ou la radiation pour invalidité
 * imputable au service), ou les seules années dans l'emploi, l'agent y étant à
 * la fin de ses services s'il le faut. Voir `CONDITIONS_DES_EMPLOIS` du Python.
 */
export const CONDITIONS_DES_EMPLOIS = Object.freeze([
  "duree_de_l_age_minore", "categorie_active_en_fonction", "duree_de_la_categorie_active",
  "durees_et_age_de_l_emploi", "duree_dans_l_emploi",
]);

/**
 * L'âge au-delà duquel une version supprime la bonification, quand elle ne
 * l'écrit pas en années : l'âge légal de la génération. Voir `AGE_LEGAL` du Python.
 */
export const AGE_LEGAL = "age_legal";

/** La tolérance des années de service. Voir `EPSILON_ANNEES` du Python. */
const EPSILON_ANNEES = 1e-9;

/**
 * La fiche de l'apprentissage, que l'emploi porte en attribut, et celle de
 * chaque motif de période assimilée : le sixième domaine (action 130). Voir
 * `FICHES_DES_ASSIMILEES` du Python.
 */
export const FICHE_DE_L_APPRENTISSAGE = "apprentissage";
export const FICHES_DES_ASSIMILEES = Object.freeze({
  stage_de_formation_professionnelle: "stages_formation_professionnelle",
  stage_d_insertion: "stages_formation_professionnelle",
  sportif_de_haut_niveau: "sportifs_haut_niveau",
  conge_supplementaire_de_naissance: "conge_supplementaire_naissance",
});
/** Comment une version compte ses trimestres. */
export const DECOMPTES_DES_ASSIMILEES = Object.freeze([
  "duree_du_contrat", "jours_dans_l_annee", "periodes_continues"]);
/** Les jours des mois incomplets qui font un mois de contrat (D. 373-3, 2°). */
export const JOURS_PAR_MOIS_DE_CONTRAT = 30;

/**
 * Ce qu'une période assimilée apporte dans une année, au régime qui la valide :
 * des trimestres d'assurance, non cotisés et sans services. Voir
 * `TrimestresAssimiles` du Python.
 */
export class TrimestresAssimiles {
  constructor({ motif, regime, annee, fiche, version, texte, trimestres, fiabilite }) {
    this.motif = motif;
    this.regime = regime;
    this.annee = annee;
    this.fiche = fiche;
    this.version = version;
    this.texte = texte;
    this.trimestres = trimestres;
    this.fiabilite = fiabilite;
  }
}

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
    bonificationsParRegime, etranger = null, emplois = [], decompte = null,
    jours = { assurance: new Map(), services: new Map() }, ecartAuJour = 0.0,
    assimilees = [], plafondsAssimilees = new Map() }) {
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
    /**
     * La version de la fiche du décompte qui vaut à la date d'effet — son
     * identifiant et ses paramètres —, `null` quand elle ne compte pas au jour.
     */
    this.decompte = decompte;
    /**
     * Les services du code des pensions AU JOUR, par compte — `assurance` et
     * `services` —, par régime et par année.
     */
    this.jours = jours;
    /**
     * Ce que les fractions de trimestre de ces services changent à
     * `trimestres`, quand la durée de leur décote se compte au jour.
     */
    this.ecartAuJour = ecartAuJour;
    /**
     * Les trimestres des périodes assimilées, période par période et année par
     * année, avant le plafond de l'année : ils sont dans `parAnnee`, au compte
     * `assurance` seul.
     */
    this.assimilees = assimilees;
    /**
     * Le plafond des années où une période assimilée compte : leurs trimestres
     * civils jusqu'à la date d'effet, même quand la carrière n'en couvre
     * qu'une partie.
     */
    this.plafondsAssimilees = plafondsAssimilees;
  }

  /** Ces régimes comptent-ils leurs services au jour, à la date d'effet ? */
  auJour(membres) {
    return this.decompte !== null
      && membres.some((m) => this.decompte.parametres.regimes.includes(m));
  }

  /**
   * La décote de ces régimes lit-elle une durée d'assurance au jour, sans
   * arrondi (L. 14, I ; Conseil d'État, 2 février 2010, n° 311495) ?
   */
  dureeAuJour(membres) {
    return this.auJour(membres) && Boolean(this.decompte.parametres.duree_au_jour);
  }

  /**
   * Les jours de services de ces régimes, sommés année par année, trois cent
   * soixante au plus par année.
   */
  joursDeServices(membres) {
    const sommes = new Map();
    for (const membre of membres) {
      for (const [annee, jours] of this.jours.services.get(membre) ?? []) {
        sommes.set(annee, (sommes.get(annee) ?? 0.0) + jours);
      }
    }
    let total = 0;
    for (const jours of sommes.values()) {
      total += Math.min(JOURS_PAR_AN, jours);
    }
    return total;
  }

  /** Les services effectifs de ces régimes, en trimestres, arrondis. */
  servicesEffectifs(membres) {
    return arrondirLesServices(this.joursDeServices(membres), this.decompte.parametres);
  }

  /**
   * Le décompte final des trimestres liquidables : les services au jour,
   * arrondis, et les bonifications qui ne tiennent à aucune année.
   */
  servicesLiquidables(membres) {
    let bonifications = 0;
    for (const membre of membres) {
      bonifications += this.horsAnnee.services.get(membre) ?? 0;
    }
    return this.servicesEffectifs(membres) + bonifications;
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
    const plafonds = table === "assurance" ? this.plafondsAssimilees : new Map();
    for (const [annee, somme] of sommes) {
      total += Math.min(somme, Math.max(this.carriere.plafondTrimestres(annee),
        plafonds.get(annee) ?? 0));
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
      au_jour: this.decompte === null ? null : {
        version: this.decompte.id,
        jours: ["assurance", "services"].flatMap((compte) => [...this.jours[compte]]
          .flatMap(([regime, annees]) => [...annees]
            .map(([annee, jours]) => ({ compte, regime, annee, jours })))),
        ecart: this.ecartAuJour,
      },
      assimilees: this.assimilees.map((a) => ({
        motif: a.motif, regime: a.regime, annee: a.annee, fiche: a.fiche,
        version: a.version, trimestres: a.trimestres, fiabilite: nomFiabilite(a.fiabilite),
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
  // LES SERVICES DU CODE DES PENSIONS AU JOUR, à côté des trimestres : le
  // décompte final les arrondit une seule fois (R. 26), et la durée que la
  // décote lit ne les arrondit pas (L. 14, I). Voir `compter` du Python.
  // Les jours se comptent dans toute la famille de la fonction publique : les
  // trois régimes liquident aussi les services de ceux qu'ils réunissent.
  const decompte = decompteDesServices(moteur, carriere, anneeLiquidation);
  const jours = { assurance: new Map(), services: new Map() };
  const budgetJours = new Map();
  const joursParAnnee = new Map();
  const autresParAnnee = new Map();
  const crediterJours = (compte, code, annee, nombre) => {
    if (!jours[compte].has(code)) {
      jours[compte].set(code, new Map());
    }
    const annees = jours[compte].get(code);
    annees.set(annee, (annees.get(annee) ?? 0.0) + nombre);
  };
  carriere.lignes.forEach((ligne, i) => {
    const retenusLigne = carriere.trimestresRetenus(ligne);
    const comptesAuJour = decompte === null ? [] : coordination.regimes[i]
      .filter((code) => moteur.catalogue.contient(code)
        && moteur.catalogue.obtenir(code).famille === "fonction_publique");
    if (comptesAuJour.length > 0 && ligne.services_fonction_publique) {
      // Une ligne de services se compte au jour même quand elle ne valide
      // aucun trimestre entier : deux mois d'entrée en novembre.
      const dureeJours = joursDeLaLigne(carriere, ligne);
      if (dureeJours > 0) {
        let servicesJours = ligne.quotite >= 1.0 ? dureeJours : dureeJours * ligne.quotite;
        const plafondEnfants = ligne.services_plafond_trimestres_par_enfant;
        if (plafondEnfants) {
          const restant = budgetJours.get(plafondEnfants)
            ?? plafondEnfants * carriere.nombre_enfants * JOURS_PAR_TRIMESTRE;
          servicesJours = Math.min(servicesJours, restant);
          budgetJours.set(plafondEnfants, restant - servicesJours);
        }
        for (const code of comptesAuJour) {
          crediterJours("assurance", code, ligne.annee, dureeJours);
          if (servicesJours > 0) {
            crediterJours("services", code, ligne.annee, servicesJours);
          }
        }
        joursParAnnee.set(ligne.annee, (joursParAnnee.get(ligne.annee) ?? 0.0) + dureeJours);
      }
    } else if (retenusLigne > 0) {
      autresParAnnee.set(ligne.annee, (autresParAnnee.get(ligne.annee) ?? 0) + retenusLigne);
    }
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
  // Ce que la durée au jour change à la durée tous régimes, année par année.
  let ecartAuJour = 0.0;
  if (decompte !== null && decompte.parametres.duree_au_jour) {
    for (const annee of [...joursParAnnee.keys()].sort((a, b) => a - b)) {
      const entiers = carriere.trimestresParAnnee(carriere.lignesDe(annee)).get(annee) ?? 0;
      const auJourAnnee = Math.min(4.0, (autresParAnnee.get(annee) ?? 0)
        + joursParAnnee.get(annee) / JOURS_PAR_TRIMESTRE);
      ecartAuJour += auJourAnnee - entiers;
    }
  }
  // Les périodes assimilées : à l'assurance de leur régime, année par année,
  // et à la durée tous régimes, dans les trimestres civils que leur année
  // laisse libres.
  const assimilees = avantagesNonContributifs
    ? trimestresAssimiles(moteur, carriere, parAnnee.assurance) : [];
  const plafondsAssimilees = new Map();
  if (assimilees.length > 0) {
    const parAnneeAssimilees = new Map();
    for (const assimilee of assimilees) {
      crediterTrimestres("assurance", assimilee.regime, assimilee.annee, assimilee.trimestres);
      parAnneeAssimilees.set(assimilee.annee,
        (parAnneeAssimilees.get(assimilee.annee) ?? 0) + assimilee.trimestres);
    }
    for (const annee of [...parAnneeAssimilees.keys()].sort((a, b) => a - b)) {
      const plafond = plafondDeLAnnee(carriere, annee);
      plafondsAssimilees.set(annee, plafond);
      const deja = carriere.trimestresParAnnee(carriere.lignesDe(annee)).get(annee) ?? 0;
      trimestres += Math.max(0, Math.min(parAnneeAssimilees.get(annee), plafond - deja));
    }
  }
  const provisoire = new Durees({
    carriere, parAnnee, horsAnnee, enfants: null, trimestres,
    trimestresParRegime: new Map(), bonificationsParRegime: new Map(), plafondsAssimilees,
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
    decompte, jours: decompte !== null ? jours : { assurance: new Map(), services: new Map() },
    ecartAuJour, assimilees, plafondsAssimilees,
  });
}

// -- les périodes assimilées (action 130, sixième domaine) ---------------------

/** Un jour, compté depuis le 1er janvier 1970. */
const JOUR_MS = 86400000;
const versJour = (annee, mois, quantieme) => Date.UTC(annee, mois - 1, quantieme) / JOUR_MS;
const jourDe = (texte) => versJour(Number(texte.slice(0, 4)), Number(texte.slice(5, 7)),
  Number(texte.slice(8, 10)));
const anneeDuJour = (jour) => new Date(jour * JOUR_MS).getUTCFullYear();
const moisDuJour = (jour) => new Date(jour * JOUR_MS).getUTCMonth() + 1;
const quantiemeDuJour = (jour) => new Date(jour * JOUR_MS).getUTCDate();
const premierJanvier = (annee) => versJour(annee, 1, 1);
const moisSuivant = (jour) => versJour(anneeDuJour(jour), moisDuJour(jour) + 1, 1);
const trimestreSuivant = (jour) => versJour(anneeDuJour(jour),
  3 * Math.floor((moisDuJour(jour) - 1) / 3) + 4, 1);
const isoDuJour = (jour) => {
  const date = new Date(jour * JOUR_MS);
  return `${String(date.getUTCFullYear()).padStart(4, "0")}-`
    + `${String(date.getUTCMonth() + 1).padStart(2, "0")}-`
    + `${String(date.getUTCDate()).padStart(2, "0")}`;
};

/** La date d'effet de la pension (AAAA-MM-JJ). Voir `date_d_effet` du Python. */
export function dateDEffet(carriere) {
  const mois = carriere.age_liquidation !== null ? carriere.dateLiquidation.mois : 1;
  return `${String(carriere.anneeLiquidation).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`;
}

/**
 * Les trimestres civils d'une année que la durée d'assurance peut compter.
 * Voir `plafond_de_l_annee` du Python.
 */
export function plafondDeLAnnee(carriere, annee) {
  if (annee < carriere.anneeLiquidation) {
    return 4;
  }
  const mois = carriere.age_liquidation !== null ? carriere.dateLiquidation.mois : 1;
  return trimestresCivils(mois - 1);
}

/**
 * Les trimestres des périodes assimilées de la carrière, année par année,
 * avant le plafond de l'année ; aucun dans une année dont un relevé déposé
 * porte les trimestres. Voir `trimestres_assimiles` du Python.
 */
export function trimestresAssimiles(moteur, carriere, assurance) {
  if (!carriere.chronologie) {
    return [];
  }
  const effet = dateDEffet(carriere);
  return [...trimestresDeLApprentissage(moteur, carriere, assurance, effet),
    ...trimestresDesPeriodes(moteur, carriere, effet)]
    .filter((a) => a.trimestres > 0 && !carriere.anneesDeclarees.has(a.annee));
}

/**
 * Le premier jour d'une période où la fiche ouvre un droit, et la version qui
 * l'ouvre ; `null` quand rien ne l'ouvre avant `fin`. Voir `version_ouverte`
 * du Python.
 */
export function versionOuverte(moteur, fiche, motif, debut, fin, effet) {
  let jour = debut;
  while (jour < fin) {
    const version = moteur.fichesDatees.versionAuxDates(fiche,
      { "periode.debut": isoDuJour(jour), "liquidation.date_effet": effet });
    if (version !== null && version.parametres.existe) {
      const parametres = version.parametres;
      if (!DECOMPTES_DES_ASSIMILEES.includes(parametres.decompte)) {
        throw new Error(`${fiche}.${version.id} : décompte inconnu, `
          + `'${parametres.decompte}'`);
      }
      if (motif === null || (parametres.motifs ?? []).includes(motif)) {
        return [jour, version];
      }
    }
    jour = premierJanvier(anneeDuJour(jour) + 1);
  }
  return null;
}

/** Le régime qui valide une période assimilée. Voir `_regime_de` du Python. */
function regimeDe(moteur, parametres, annee, assurance) {
  const connus = (parametres.regimes ?? []).filter((code) => moteur.catalogue.contient(code));
  return connus.find((code) => (assurance.get(code)?.get(annee) ?? 0) > 0)
    ?? (connus.length > 0 ? connus[0] : null);
}

/**
 * Les trimestres d'un contrat d'apprentissage, année par année (D. 373-3), en
 * jours depuis 1970, `fin` exclue. Voir `trimestres_du_contrat` du Python.
 */
export function trimestresDuContrat(debut, fin) {
  let moisEntiers = 0;
  let jours = 0;
  let jour = debut;
  while (jour < fin) {
    const suivant = moisSuivant(jour);
    if (quantiemeDuJour(jour) === 1 && suivant <= fin) {
      moisEntiers += 1;
    } else {
      jours += Math.min(suivant, fin) - jour;
    }
    jour = suivant;
  }
  const total = Math.floor((moisEntiers + Math.floor(jours / JOURS_PAR_MOIS_DE_CONTRAT)) / 3);
  const parAnnee = new Map();
  let trimestre = quantiemeDuJour(debut) === 1 && moisDuJour(debut) % 3 === 1
    ? debut : trimestreSuivant(debut);
  let entiers = 0;
  while (trimestreSuivant(trimestre) <= fin) {
    const annee = anneeDuJour(trimestre);
    parAnnee.set(annee, (parAnnee.get(annee) ?? 0) + 1);
    entiers += 1;
    trimestre = trimestreSuivant(trimestre);
  }
  const reste = total - entiers;
  if (reste > 0) {
    const derniere = anneeDuJour(fin - 1);
    parAnnee.set(derniere, (parAnnee.get(derniere) ?? 0) + reste);
  }
  return parAnnee;
}

/** Les contrats d'apprentissage de la carrière. Voir `_contrats` du Python. */
function contrats(carriere) {
  const liste = [];
  for (const periode of chrono.periodes(carriere.chronologie, carriere.personne)) {
    if (periode.sorte !== chrono.EMPLOI || !periode.attributs.apprentissage) {
      continue;
    }
    const debut = jourDe(periode.debut);
    const fin = jourDe(periode.fin);
    if (liste.length > 0 && liste[liste.length - 1][1] === debut) {
      liste[liste.length - 1][1] = fin;
    } else {
      liste.push([debut, fin]);
    }
  }
  return liste.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
}

/**
 * Le complément de l'apprentissage, année par année : les trimestres du contrat
 * moins ceux que l'année a déjà validés dans son régime (D. 373-4). Voir
 * `trimestres_de_l_apprentissage` du Python.
 */
export function trimestresDeLApprentissage(moteur, carriere, assurance, effet) {
  const resultat = [];
  const finDeCarriere = jourDe(effet);
  for (const [debut, finDuContrat] of contrats(carriere)) {
    const fin = Math.min(finDuContrat, finDeCarriere);
    const ouverte = versionOuverte(moteur, FICHE_DE_L_APPRENTISSAGE, null, debut, fin, effet);
    if (ouverte === null) {
      continue;
    }
    const [ouverture, version] = ouverte;
    const parametres = version.parametres;
    const parAnnee = [...trimestresDuContrat(ouverture, fin)].sort((a, b) => a[0] - b[0]);
    for (const [annee, duContrat] of parAnnee) {
      const regime = regimeDe(moteur, parametres, annee, assurance);
      if (regime === null) {
        continue;
      }
      const valides = assurance.get(regime)?.get(annee) ?? 0;
      resultat.push(new TrimestresAssimiles({
        motif: FICHE_DE_L_APPRENTISSAGE, regime, annee, fiche: FICHE_DE_L_APPRENTISSAGE,
        version: version.id, texte: version.texte, trimestres: Math.max(0, duContrat - valides),
        fiabilite: fiabiliteDepuisTexte(parametres.fiabilite),
      }));
    }
  }
  return resultat;
}

/**
 * Les jours d'une période, année civile par année civile, `fin` exclue ; ou
 * `jours`, répartis au prorata, sans fraction. Voir `jours_par_annee` du
 * Python.
 */
export function joursParAnnee(debut, fin, jours = null) {
  const calendrier = new Map();
  let jour = debut;
  while (jour < fin) {
    const suivant = Math.min(premierJanvier(anneeDuJour(jour) + 1), fin);
    calendrier.set(anneeDuJour(jour), suivant - jour);
    jour = suivant;
  }
  if (jours === null || jours === undefined) {
    return calendrier;
  }
  const total = [...calendrier.values()].reduce((somme, n) => somme + n, 0);
  const reparti = new Map();
  let cumul = 0;
  let donnes = 0;
  for (const [annee, nombre] of calendrier) {
    cumul += nombre;
    const part = Math.floor((jours * cumul) / total) - donnes;
    reparti.set(annee, part);
    donnes += part;
  }
  return reparti;
}

/** Le jour anniversaire de cet âge. Voir `_anniversaire` du Python. */
function anniversaire(carriere, age) {
  const texte = chrono.naissance(carriere.chronologie, carriere.personne).debut;
  const annee = Number(texte.slice(0, 4)) + age;
  const mois = Number(texte.slice(5, 7));
  const quantieme = Number(texte.slice(8, 10));
  if (mois === 2 && quantieme === 29 && !(annee % 4 === 0 && (annee % 100 !== 0
    || annee % 400 === 0))) {
    return versJour(annee, 3, 1);
  }
  return versJour(annee, mois, quantieme);
}

/**
 * Les trimestres des périodes assimilées que la personne déclare : les jours
 * dans l'année, par fiche et par année ; les périodes continues des sportifs,
 * tranche par tranche. Voir `trimestres_des_periodes` du Python.
 */
export function trimestresDesPeriodes(moteur, carriere, effet) {
  const finDeCarriere = jourDe(effet);
  const joursCumules = new Map();
  const continues = new Map();
  const sportifs = new Map();
  const cumuler = (table, fiche, annee, motif, version, nombre) => {
    const cle = `${fiche}|${annee}`;
    if (!table.has(cle)) {
      table.set(cle, [fiche, annee, motif, version, 0]);
    }
    table.get(cle)[4] += nombre;
  };
  for (const periode of chrono.periodesAssimilees(carriere.chronologie, carriere.personne)) {
    const attributs = periode.attributs;
    const motif = attributs.motif;
    const fiche = FICHES_DES_ASSIMILEES[motif];
    const debut = jourDe(periode.debut);
    const finDeclaree = jourDe(periode.fin);
    const fin = Math.min(finDeclaree, finDeCarriere);
    const ouverte = versionOuverte(moteur, fiche, motif, debut, fin, effet);
    if (ouverte === null) {
      continue;
    }
    let [ouverture, version] = ouverte;
    const parametres = version.parametres;
    const parTranche = Math.trunc(parametres.jours_par_trimestre);
    if (parametres.decompte === "jours_dans_l_annee") {
      let jours = attributs.jours ?? null;
      if (jours !== null) {
        jours = Math.floor((jours * (fin - ouverture)) / (finDeclaree - debut));
      }
      for (const [annee, nombre] of joursParAnnee(ouverture, fin, jours)) {
        cumuler(joursCumules, fiche, annee, motif, version, nombre);
      }
      continue;
    }
    if (parametres.decompte === "periodes_continues") {
      ouverture = Math.max(ouverture, anniversaire(carriere, Math.trunc(parametres.age_minimum)));
      const plafond = Math.trunc(parametres.plafond_trimestres);
      let tranche = ouverture;
      while (tranche + parTranche <= fin && (sportifs.get(fiche) ?? 0) < plafond) {
        const finTranche = tranche + parTranche;
        let annee = null;
        for (const [candidate, nombre] of joursParAnnee(tranche, finTranche)) {
          if (annee === null || nombre > annee[1]) {
            annee = [candidate, nombre];
          }
        }
        tranche = finTranche;
        const revenus = carriere.lignesDe(annee[0])
          .reduce((somme, ligne) => somme + ligne.revenu, 0);
        if (revenus > parametres.ressources_maximum_en_plafonds
          * moteur.macro.plafond_securite_sociale.valeur(annee[0])) {
          continue;
        }
        sportifs.set(fiche, (sportifs.get(fiche) ?? 0) + 1);
        cumuler(continues, fiche, annee[0], motif, version, 1);
      }
      continue;
    }
    throw new Error(`${fiche}.${version.id} : la fiche d'une période assimilée `
      + "ne compte pas la durée d'un contrat");
  }
  const resultat = [];
  for (const [table, enJours] of [[joursCumules, true], [continues, false]]) {
    for (const [fiche, annee, motif, version, nombre] of table.values()) {
      const parametres = version.parametres;
      const regime = regimeDe(moteur, parametres, annee, new Map());
      if (regime === null) {
        continue;
      }
      resultat.push(new TrimestresAssimiles({
        motif, regime, annee, fiche, version: version.id, texte: version.texte,
        trimestres: enJours ? Math.floor(nombre / Math.trunc(parametres.jours_par_trimestre))
          : nombre,
        fiabilite: fiabiliteDepuisTexte(parametres.fiabilite),
      }));
    }
  }
  return resultat;
}

/**
 * La version de la fiche du décompte qui vaut à la date d'effet — son
 * identifiant et ses paramètres —, `null` quand elle ne compte pas au jour.
 * Un paramètre que le moteur ne connaît pas l'arrête. Voir
 * `decompte_des_services` du Python.
 */
export function decompteDesServices(moteur, carriere, anneeLiquidation) {
  const mois = carriere.age_liquidation !== null ? carriere.dateLiquidation.mois : 1;
  const version = moteur.fichesDatees.version(FICHE_DU_DECOMPTE,
    `${String(anneeLiquidation).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`);
  if (version === null || !version.parametres.existe) {
    return null;
  }
  const parametres = version.parametres;
  const unite = parametres.unite_jours;
  const seuil = parametres.seuil_jours;
  if (!(Number.isInteger(unite) && unite > 0 && seuil > 0 && seuil <= unite)) {
    throw new Error(`${FICHE_DU_DECOMPTE}.${version.id} : unité ${unite}, seuil ${seuil}`);
  }
  if (!MINIMA_DU_DECOMPTE.includes(parametres.minimum_garanti)) {
    throw new Error(`${FICHE_DU_DECOMPTE}.${version.id} : minimum garanti inconnu, `
      + `${parametres.minimum_garanti}`);
  }
  return { id: version.id, parametres };
}

/**
 * Les jours de services qu'une ligne compte, l'année de trois cent soixante
 * jours : ses mois, coupés au départ, de trente jours chacun ; sur un relevé,
 * les trimestres qu'il porte, à quatre-vingt-dix jours, sans dépasser ces mois.
 * Voir `jours_de_la_ligne` du Python.
 */
export function joursDeLaLigne(carriere, ligne) {
  const part = carriere.partRetenueLigne(ligne);
  if (part <= 0) {
    return 0;
  }
  let jours = Math.round(part * 12) * JOURS_PAR_MOIS;
  if (ligne.jours_de_services !== null && ligne.jours_de_services !== undefined) {
    jours = Math.min(jours, ligne.jours_de_services);
  }
  return jours;
}

/**
 * Le décompte final des trimestres liquidables, en trimestres : les jours de
 * services par unités entières, la fraction d'au moins `seuil_jours` comptée
 * pour une unité, la fraction plus courte négligée (R. 26). Voir
 * `arrondir_les_services` du Python.
 */
export function arrondirLesServices(jours, parametres) {
  const unite = parametres.unite_jours;
  const seuil = parametres.seuil_jours;
  let entieres = Math.floor((jours + EPSILON_JOURS) / unite);
  if (jours - entieres * unite + EPSILON_JOURS >= seuil) {
    entieres += 1;
  }
  return Math.floor(entieres * unite / JOURS_PAR_TRIMESTRE);
}

/**
 * Ce que les emplois classés de la carrière ajoutent, une fiche après l'autre
 * (`FICHES_DES_EMPLOIS`), chacune lue à la date d'effet de la pension ; une
 * version qui borne le cumul ne garde de son effet en durée que ce que les fiches
 * qui la précèdent lui laissent. Voir `trimestres_des_emplois` du Python.
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
    let emploi = trimestresDUnEmploi(moteur, carriere, nom, version);
    if (emploi === null) {
      continue;
    }
    const cumul = version.parametres.cumul_maximum_trimestres;
    if (cumul !== null && cumul !== undefined) {
      // Une bonification y porte ses services et sa durée, une majoration sa
      // seule majoration : l'un ou l'autre se borne.
      const reste = Math.max(0, Math.trunc(cumul)
        - emplois.reduce((somme, e) => somme + e.duree + e.majoration, 0));
      emploi = new TrimestresEmploi({
        ...emploi,
        services: Math.min(emploi.services, reste),
        duree: Math.min(emploi.duree, reste),
        majoration: Math.min(emploi.majoration, reste),
      });
      if (!(emploi.services || emploi.majoration)) {
        continue;
      }
    }
    emplois.push(emploi);
  }
  return emplois;
}

/**
 * Ce qu'un emploi classé ouvre, ou null s'il n'ouvre rien : une BONIFICATION,
 * fraction du temps servi dans les statuts qui l'ouvrent, sous son plafond,
 * diminuée des services accomplis au-delà de l'âge qui la réduit, comptés au
 * mois — d'une annuité par année entière pour le militaire —, nulle au-delà de
 * l'âge qui la supprime, aux services et à la durée ; ou une MAJORATION,
 * fraction des services effectifs de la fonction publique civile, à la seule
 * durée de la décote. En trimestres, un demi-trimestre et plus comptant pour
 * un. Voir `trimestres_d_un_emploi` du Python.
 */
export function trimestresDUnEmploi(moteur, carriere, fiche, version) {
  const parametres = version.parametres;
  const nature = parametres.nature;
  if (!NATURES_DES_EMPLOIS.includes(nature)) {
    throw new Error(`${fiche}.${version.id} : nature inconnue, ${JSON.stringify(nature)}`);
  }
  const condition = parametres.condition;
  if (!CONDITIONS_DES_EMPLOIS.includes(condition)) {
    throw new Error(`${fiche}.${version.id} : condition inconnue, ${JSON.stringify(condition)}`);
  }
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
  const ouverte = conditionDUnEmploi(moteur, carriere, condition, parametres, servies);
  if (ouverte === null) {
    return null;
  }
  const fiabilite = Math.min(fiabiliteDepuisTexte(parametres.fiabilite), ouverte);
  const bonification = nature === "bonification";
  const base = bonification
    ? servies : carriere.dureeDeService([...parametres.services_comptes], borne);
  let annees = base * Number(parametres.fraction);
  if (parametres.plafond_trimestres !== null && parametres.plafond_trimestres !== undefined) {
    annees = Math.min(annees, Math.trunc(parametres.plafond_trimestres) / 4);
  }
  let fiabiliteLue = fiabilite;
  if (parametres.age_de_suppression !== null && parametres.age_de_suppression !== undefined) {
    const [age, lue] = ageDeSuppression(moteur, carriere, fiche, version);
    if (servicesAuDela(carriere, statuts, age, borne, servies) > EPSILON_ANNEES) {
      return null;
    }
    fiabiliteLue = Math.min(fiabiliteLue, lue);
  }
  if (parametres.age_de_reduction !== null && parametres.age_de_reduction !== undefined) {
    const auDela = servicesAuDela(carriere, statuts, Number(parametres.age_de_reduction),
      borne, servies);
    annees -= parametres.reduction_par_annee_entiere
      ? Math.floor(auDela + EPSILON_ANNEES) : auDela;
  }
  const trimestres = annees > 0 ? Math.trunc(annees * 4 + 0.5) : 0;
  if (trimestres <= 0) {
    return null;
  }
  return new TrimestresEmploi({
    regime, fiche, version: version.id, texte: version.texte,
    services: bonification ? trimestres : 0,
    duree: bonification ? trimestres : 0,
    majoration: bonification ? 0 : trimestres,
    auDelaDuMaximum: Boolean(parametres.au_dela_du_maximum), fiabilite: fiabiliteLue,
  });
}

/**
 * Les années servies dans ces statuts au-delà de cet âge, `servies` étant celles
 * de toute la carrière : depuis le premier mois vécu entier à cet âge, au mois
 * près. Voir `services_au_dela` du Python.
 */
export function servicesAuDela(carriere, statuts, age, borne, servies) {
  const avant = carriere.dureeDeServiceAvant(statuts, carriere.dateDeLAge(age), borne);
  return Math.max(0, servies - avant);
}

/**
 * L'âge au-delà duquel la version supprime la bonification, et la fiabilité de
 * sa lecture : écrit en années, ou l'âge légal de la génération (`AGE_LEGAL`).
 * Voir `age_de_suppression` du Python.
 */
export function ageDeSuppression(moteur, carriere, fiche, version) {
  const parametres = version.parametres;
  const age = parametres.age_de_suppression;
  if (age === AGE_LEGAL) {
    const legal = moteur.agesOuverture.age(carriere.generation);
    if (legal === null) {
      throw new Error(`${fiche}.${version.id} : pas d'âge légal pour la génération `
        + `${carriere.generation}`);
    }
    return legal;
  }
  if (typeof age !== "number") {
    throw new Error(`${fiche}.${version.id} : âge de suppression inconnu, ${JSON.stringify(age)}`);
  }
  return [age, fiabiliteDepuisTexte(parametres.fiabilite)];
}

/**
 * Les années de services classés qu'exige l'âge anticipé ou minoré : `base`,
 * la durée d'avant la loi du 9 novembre 2010, relevée selon l'année où
 * `statuts` l'ont atteinte (décret n° 2011-2103, article 6).
 */
export function servicesActifsRequis(moteur, carriere, classement, statuts, base) {
  const atteinte = carriere.dateDeService(statuts, base);
  const annee = atteinte === null ? 9999.0 : atteinte.annee + (atteinte.mois - 1) / 12;
  const requises = moteur.dureesServicesActifs.anneesRequises(classement, annee);
  return requises === null || requises === undefined ? base : requises[0];
}

/**
 * La condition remplie, et la fiabilité de ce qu'elle a lu ; null sinon. Les
 * services actifs sont ceux de tous les statuts classés, super-actifs compris.
 * Voir `condition_d_un_emploi` du Python.
 */
export function conditionDUnEmploi(moteur, carriere, condition, parametres, servies) {
  if (condition === "duree_dans_l_emploi") {
    // La durée dans l'emploi du militaire ne lit aucun classement ; jusqu'en
    // août 2023, la dernière année des services comptés doit être dans l'emploi.
    if (servies + EPSILON_ANNEES < Number(parametres.annees_dans_l_emploi)) {
      return null;
    }
    if (parametres.en_fonction) {
      const borne = coordonner.borneCarriere(carriere);
      const comptes = carriere.bornesDeService([...parametres.services_comptes], borne);
      const dansLEmploi = carriere.bornesDeService([...parametres.statuts], borne);
      if (comptes === null || dansLEmploi === null || dansLEmploi[1] < comptes[1]) {
        return null;
      }
    }
    return fiabiliteDepuisTexte(parametres.fiabilite);
  }
  const derogation = moteur.agesCategorieActive.derogation(
    parametres.classement, carriere.generation);
  if (condition === "durees_et_age_de_l_emploi") {
    const radiation = carriere.radiationPourInvalidite;
    if (radiation !== null && radiation.imputable) {
      return fiabiliteDepuisTexte(parametres.fiabilite);
    }
    const borne = coordonner.borneCarriere(carriere);
    const publiques = carriere.dureeDeService([...parametres.services_comptes], borne);
    if (servies + 1e-9 < Number(parametres.annees_dans_l_emploi)
        || publiques + 1e-9 < Number(parametres.annees_de_services)) {
      return null;
    }
    if (!parametres.age_anticipe) {
      return fiabiliteDepuisTexte(parametres.fiabilite);
    }
    if (derogation === null || carriere.age_liquidation === null
        || carriere.age_liquidation === undefined
        || carriere.age_liquidation + 1e-9 < derogation.ageOuverture) {
      return null;
    }
    return derogation.fiabilite;
  }
  if (condition === "duree_de_l_age_minore") {
    if (carriere.radiationPourInvalidite !== null) {
      return fiabiliteDepuisTexte(parametres.fiabilite);
    }
    if (derogation === null || servies + 1e-9 < servicesActifsRequis(
      moteur, carriere, parametres.classement, [...parametres.statuts],
      derogation.servicesRequis)) {
      return null;
    }
    return derogation.fiabilite;
  }
  const borne = coordonner.borneCarriere(carriere);
  const classes = Object.keys(moteur.affiliations.classementsActifs);
  const actifs = carriere.dureeDeService(classes, borne);
  if (derogation === null || actifs + 1e-9 < servicesActifsRequis(
    moteur, carriere, parametres.classement, classes, derogation.servicesRequis)) {
    return null;
  }
  if (condition === "duree_de_la_categorie_active") {
    return derogation.fiabilite;
  }
  // `categorie_active_en_fonction` : l'âge anticipé atteint à la radiation, et
  // la dernière année de la fonction publique civile servie dans l'un des
  // statuts de la fiche.
  if (carriere.age_liquidation === null || carriere.age_liquidation === undefined
      || carriere.age_liquidation + 1e-9 < derogation.ageOuverture) {
    return null;
  }
  const publiques = carriere.bornesDeService([...parametres.services_comptes], borne);
  const dansLEmploi = carriere.bornesDeService([...parametres.statuts], borne);
  if (publiques === null || dansLEmploi === null || dansLEmploi[1] < publiques[1]) {
    return null;
  }
  return derogation.fiabilite;
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
    const periode = periodeDeLiquidation(regime, new DateMois(anneeLiquidation, mois));
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
