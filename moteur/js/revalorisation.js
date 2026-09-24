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

import { RevalorisationStock, SituationFoyer } from "./config.js";
import { Fiabilite } from "./serie.js";

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

  /** Coefficient nominal d'une pension de régime, de `depart` à `jusqua`. */
  coefficient(pension, anneeLiquidation, depart, jusqua, mensuel2019) {
    const code = pension.regime;
    const regime = this.catalogue.obtenir(code);
    const debutAnnee = dateIso(anneeLiquidation, 1, 1);
    if (pension.type_calcul === "points" || pension.type_calcul === "mixte") {
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnneeRegime(regime)));
      const bareme = (periode !== null ? periode.points_de : null) || code;
      const auDepart = this.actuel.valeurDuPoint(bareme, anneeLiquidation);
      const publiee = derniereValeurPubliee(this.actuel, bareme);
      if (auDepart !== null && auDepart[0] > 0 && publiee !== null) {
        const anneeFin = Number(jusqua.slice(0, 4));
        const ancre = Math.min(anneeFin, publiee);
        const aLAncre = this.actuel.valeurDuPoint(bareme, ancre);
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

/** Le système 1 servi en `annee` — l'année courante par défaut. */
export function actuelAujourdhui(simulateur, carriere, resultat, annee = null) {
  const parametres = simulateur.parametres;
  const an = annee === null ? parametres.annee_courante : annee;
  const servie = new PensionServie(simulateur);
  const liquidation = carriere.anneeLiquidation;
  const depart = dateIso(liquidation, carriere.dateLiquidation.mois, 1);
  const fin = dateIso(an, 12, 31);
  const isoler = parametres.isoler_capitalisation;
  const pensions = [...resultat.pensions_par_regime];
  const horsRepartition = (p) => isoler
    && Boolean(simulateur.catalogue.obtenir(p.regime).hors_repartition);
  let majoration = 0;
  let aspaAuDepart = 0;
  // La part de chaque régime dans la majoration pour enfants, plafond compris.
  const partsMajoration = [];
  for (const a of resultat.avantages_appliques) {
    if (a.code === "majoration_enfants") {
      majoration += a.montant;
      partsMajoration.push(...(a.par_regime ?? []));
    }
    if (a.code === "minimum_vieillesse") aspaAuDepart += a.montant;
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
    let pondere = 0;
    for (const [code, part] of partsMajoration) {
      pondere += part * (parRegime.has(code) ? parRegime.get(code) : 1.0);
    }
    return pondere / masse;
  };

  // Une pension qui prend effet en janvier 2020 n'était pas servie en
  // décembre : le montant du mois précédent était nul.
  let mensuel2019 = null;
  if (depart <= "2020-01-01" && "2020-01-01" <= fin) {
    const jusqu2019 = pensions.map((p) => (depart <= MOIS_DES_TRANCHES
      ? servie.coefficient(p, liquidation, depart, MOIS_DES_TRANCHES, null)[0]
      : 0.0));
    let somme = 0;
    pensions.forEach((p, rang) => { somme += p.montant * jusqu2019[rang]; });
    mensuel2019 = (somme + majoration * coefficientDeLaMajoration(jusqu2019)) / 12.0;
  }

  const regimes = [];
  const coefficients = [];
  let fiabilite = Fiabilite.CERTIFIEE;
  for (const pension of pensions) {
    const [coefficient, regle, fiabiliteRegime] = servie.coefficient(
      pension, liquidation, depart, fin, mensuel2019,
    );
    coefficients.push(coefficient);
    fiabilite = Math.min(fiabilite, fiabiliteRegime);
    regimes.push({
      regime: pension.regime,
      au_depart: pension.montant,
      coefficient,
      regle,
      fiabilite: fiabiliteRegime,
      hors_repartition: horsRepartition(pension),
      aujourd_hui: pension.montant * coefficient,
    });
  }
  const coefficientMajoration = coefficientDeLaMajoration(coefficients);

  let aspa = 0.0;
  if (parametres.minimum_vieillesse_dans_le_scenario_actuel
      && an >= carriere.annee_naissance + MINIMUM_VIEILLESSE_AGE) {
    const bareme = simulateur.scenarioActuel.minimumVieillesse.plafond(an);
    if (bareme !== null) {
      let ressources = 0;
      for (const r of regimes) ressources += r.aujourd_hui;
      ressources += majoration * coefficientMajoration;
      aspa = Math.max(0.0, bareme[0] - ressources);
      if (aspa > 0) fiabilite = Math.min(fiabilite, bareme[1]);
    }
  }

  return new ActuelAujourdhui({
    annee: an,
    regimes,
    majoration_enfants: majoration,
    coefficient_majoration: coefficientMajoration,
    minimum_vieillesse_au_depart: aspaAuDepart,
    minimum_vieillesse: aspa,
    mensuel_decembre_2019: mensuel2019,
    fiabilite,
  });
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

/** Les six systèmes servis l'année courante, pour qui a déjà liquidé. */
export function pensionAujourdhui(simulateur, comparaison) {
  const parametres = simulateur.parametres;
  const carriere = comparaison.carriere;
  const annee = parametres.annee_courante;
  const liquidation = carriere.anneeLiquidation;
  const bascule = parametres.annee_bascule;
  const macro = simulateur.macro;
  const revalorisation = simulateur.revalorisationServie;
  const versAujourdhui = macro.coefficientPrix(liquidation, annee);

  const actuel = actuelAujourdhui(simulateur, carriere, comparaison.actuel, annee);
  const coefficientActuel = comparaison.actuel.pension_annuelle > 0
    ? actuel.pension_annuelle / comparaison.actuel.pension_annuelle
    : 1.0;

  const notionnels = {};
  const coefficients = {};
  for (const cle of ["notionnel_retroactif", "notionnel_prospectif",
    "notionnel_retroactif_employeur", "notionnel_prospectif_employeur"]) {
    const pension = comparaison[cle].pension_annuelle;
    const prospectif = cle.startsWith("notionnel_prospectif");
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
  const complement = ouverte
    ? Math.max(0.0, plancher - contributiveAujourdhui - rente)
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
    ressources_garantie: contributiveAujourdhui + rente,
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
    let index = 1;
    this._index = new Map([[this.premiereAnnee, index]]);
    for (let annee = this.premiereAnnee + 1; annee <= this.derniereAnnee; annee += 1) {
      // Le taux d'indexation est NOMINAL, les masses sont en euros constants :
      // on le déflate année par année, et non en bloc.
      index *= (1 + indexation.taux(annee).taux) * macro.coefficientPrix(annee, annee - 1);
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
