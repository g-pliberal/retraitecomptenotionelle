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
import { nomFiabilite, Fiabilite } from "../serie.js";
import { derniereAnnee } from "./commun.js";
import * as coordonner from "./coordonner.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

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
 * Quand le droit à la bonification d'un régime spécial est OUVERT, dans les
 * trois versions de R. 13 du code des pensions : pour chacun des enfants
 * jusqu'en 2003 ; pour l'enfant né en service de 2004 à 2010, R. 13 n'admettant
 * que les congés du statut ; pour l'enfant né avant la radiation depuis 2011,
 * le congé de maternité du code de la sécurité sociale suffisant. Les deux
 * bornes se lisent à l'année de liquidation. Voir le Python.
 */
const BONIFICATION_NE_EN_SERVICE_DEPUIS = 2004;
const BONIFICATION_NE_AVANT_RADIATION_DEPUIS = 2011;

/**
 * Pour les enfants nés depuis 2004, la majoration de L. 12 bis ne va qu'aux
 * femmes « ayant accouché postérieurement à leur recrutement ».
 */
const MAJORATION_APRES_RECRUTEMENT_DEPUIS = 2004;

/**
 * Ce que l'étape écrit. Son schéma :
 * `data/reference/etapes/compter_les_durees.yaml`. Deux activités d'une même
 * année s'additionnent dans `parAnnee` ; le plafond de l'année, ses
 * trimestres civils, s'applique quand on les lit (`cumulPlafonne`).
 */
export class Durees {
  constructor({ carriere, parAnnee, horsAnnee, enfants, trimestres, trimestresParRegime,
    bonificationsParRegime }) {
    this.carriere = carriere;
    /** Par compte, par régime et par année, les trimestres crédités. */
    this.parAnnee = parAnnee;
    /** Ce qui ne tient à aucune année — les trimestres des enfants. */
    this.horsAnnee = horsAnnee;
    /** Les trimestres dus au titre des enfants, et le régime qui les porte. */
    this.enfants = enfants;
    /** La durée d'assurance tous régimes, enfants compris. */
    this.trimestres = trimestres;
    /** La durée d'assurance de chaque régime, plafonnée année par année. */
    this.trimestresParRegime = trimestresParRegime;
    /** Les BONIFICATIONS, à part des services (`taux_maximum_bonifie`). */
    this.bonificationsParRegime = bonificationsParRegime;
  }

  /**
   * Les trimestres d'un compte, pour un régime ou un groupe de régimes
   * liquidés ensemble : sommés ANNÉE PAR ANNÉE, sans dépasser les trimestres
   * civils de chaque année, plus ce qui ne tient à aucune.
   */
  cumulPlafonne(table, membres) {
    const sommes = new Map();
    let total = 0;
    for (const membre of membres) {
      for (const [annee, trimestres] of this.parAnnee[table].get(membre) ?? []) {
        sommes.set(annee, (sommes.get(annee) ?? 0) + trimestres);
      }
      total += this.horsAnnee[table].get(membre) ?? 0;
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
        regime: enfants.regime, dispositif: enfants.dispositif,
        trimestres: enfants.trimestres, services: enfants.services,
        fiabilite: nomFiabilite(enfants.fiabilite),
      },
      trimestres: this.trimestres,
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
    let servicesLigne = ligne.services_fonction_publique ? retenusLigne : 0;
    const plafond = ligne.services_plafond_trimestres_par_enfant;
    if (servicesLigne > 0 && plafond > 0) {
      const restant = budgetServicesPlafonnes.get(plafond)
        ?? plafond * carriere.nombre_enfants;
      servicesLigne = Math.min(servicesLigne, restant);
      budgetServicesPlafonnes.set(plafond, restant - servicesLigne);
    }
    for (const code of coordination.regimes[i]) {
      if (!moteur.catalogue.contient(code)) {
        continue;
      }
      crediterTrimestres("assurance", code, ligne.annee, retenusLigne);
      if (servicesLigne > 0) {
        crediterTrimestres("services", code, ligne.annee, servicesLigne);
      }
      if (ligne.cotise) {
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
  // aussi dans sa proratisation. UN SEUL régime les accorde, celui que
  // désigne R. 173-15 : voir `majorationPourEnfants`.
  const majorationEnfants = avantagesNonContributifs
    ? majorationPourEnfants(moteur, carriere, trimestresParRegime, anneeLiquidation)
    : null;
  const bonificationsParRegime = new Map();
  if (majorationEnfants !== null) {
    bonificationsParRegime.set(majorationEnfants.regime, majorationEnfants.services);
    // LA DURÉE ET LES SERVICES NE SONT PAS LA MÊME CASE, et la majoration se
    // range dans les deux : tout ce qui est accordé joue sur la durée
    // d'assurance, tous régimes et dans le régime ; la seule part `services`
    // entre aux services, qui proratisent la pension de la fonction publique.
    trimestres += majorationEnfants.trimestres;
    trimestresParRegime.set(
      majorationEnfants.regime,
      trimestresParRegime.get(majorationEnfants.regime) + majorationEnfants.trimestres,
    );
    horsAnnee.assurance.set(majorationEnfants.regime, majorationEnfants.trimestres);
    horsAnnee.services.set(majorationEnfants.regime, majorationEnfants.services);
  }
  return new Durees({
    carriere, parAnnee, horsAnnee, enfants: majorationEnfants, trimestres,
    trimestresParRegime, bonificationsParRegime,
  });
}

/**
 * Trimestres dus au titre des enfants, et régime qui les porte.
 *
 * Le droit n'attribue pas ces trimestres au-dessus des régimes : il les donne
 * DANS un régime, et ils comptent donc aussi dans sa proratisation. UN SEUL
 * régime les accorde, et l'article R. 173-15 du code de la sécurité sociale
 * dit lequel — le modèle retenait celui qui accordait le plus :
 *
 * 1. un RÉGIME SPÉCIAL, qui déclare `bonifications`, passe le premier s'il
 *    peut servir une pension à l'assurée — la durée de services qu'il exige,
 *    `ServicesOuvrantPension` — et si le droit y est ouvert pour ses enfants
 *    (`bonificationOuverte`), même quand il accorde moins (TA Amiens, 2 juin
 *    2017). Entre deux régimes spéciaux, le dernier servi ;
 * 2. sinon le RÉGIME GÉNÉRAL, prioritaire parmi les régimes alignés ;
 * 3. sans lui, le régime de la dernière affiliation, puis celui qui compte le
 *    plus de trimestres.
 *
 * Le modèle ne rétablit pas au régime général l'agent qui n'a pas la durée :
 * sans régime aligné, c'est le régime spécial qui porte la majoration.
 *
 * @returns {{regime: string, dispositif: string, trimestres: number,
 *            services: number, fiabilite: number}|null}
 */
export function majorationPourEnfants(moteur, carriere, trimestresParRegime, anneeLiquidation) {
  if (carriere.nombre_enfants <= 0) {
    return null;
  }
  // Les régimes spéciaux qui peuvent pensionner, ceux qui ne le peuvent pas,
  // et les régimes alignés : code -> [trimestres validés, majoration].
  const speciaux = new Map();
  const sansPension = new Map();
  const alignes = new Map();
  // Ce qu'a coûté d'écarter un régime spécial : la fiabilité de la règle qui
  // l'a écarté, que la majoration servie ailleurs hérite.
  let fiabiliteEcartes = Fiabilite.CERTIFIEE;
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
      // Un régime EN POINTS ne porte que la majoration de DURÉE, qui ne joue
      // que sur la durée d'assurance : la CNAVPL depuis 2010 (L. 643-1-1).
      // Une bonification entre aux services, qu'il n'a pas.
      if (periode.type_calcul !== "annuites" && dispositif !== MAJORATION_DE_DUREE) {
        continue;
      }
      const accorde = moteur.majorationsEnfants.parEnfant(
        dispositif, carriere.sexe, carriere.anneeNaissanceDesEnfants, anneeLiquidation,
        carriere.nombre_enfants,
      );
      if (accorde === null) {
        continue;
      }
      const [trimestres, services, fiabilite] = accorde;
      const majoration = {
        regime: code, dispositif,
        trimestres: trimestres * carriere.nombre_enfants,
        services: services * carriere.nombre_enfants,
        fiabilite,
      };
      if (dispositif === MAJORATION_DE_DUREE) {
        alignes.set(code, [valides, majoration]);
        continue;
      }
      const droit = droitRegimeSpecial(moteur, periode, carriere, anneeLiquidation);
      if (droit === null) {
        continue;
      }
      const [pension, ouvert, fiabiliteRegle] = droit;
      if (!ouvert) {
        // Le droit fermé se lit sur la date de naissance que le modèle prête
        // aux enfants : la ligne le dit déjà.
        fiabiliteEcartes = Math.min(fiabiliteEcartes, fiabilite);
        continue;
      }
      majoration.fiabilite = Math.min(fiabilite, fiabiliteRegle);
      if (pension) {
        speciaux.set(code, [valides, majoration]);
      } else {
        fiabiliteEcartes = Math.min(fiabiliteEcartes, fiabiliteRegle);
        sansPension.set(code, [valides, majoration]);
      }
    }
  }
  if (speciaux.size > 0) {
    return derniereAffiliation(moteur, carriere, speciaux, anneeLiquidation);
  }
  let retenue;
  if (alignes.has(REGIME_GENERAL)) {
    retenue = alignes.get(REGIME_GENERAL)[1];
  } else if (alignes.size > 0) {
    retenue = derniereAffiliation(moteur, carriere, alignes, anneeLiquidation);
  } else if (sansPension.size > 0) {
    return derniereAffiliation(moteur, carriere, sansPension, anneeLiquidation);
  } else {
    return null;
  }
  if (fiabiliteEcartes < retenue.fiabilite) {
    retenue = { ...retenue, fiabilite: fiabiliteEcartes };
  }
  return retenue;
}

/**
 * Ce que ce régime spécial peut pour les enfants de cette assurée :
 * `[pension, ouvert, fiabilite]` — peut-il lui servir une pension, le droit
 * y est-il ouvert, et la fiabilité de la durée exigée —, null si elle n'y a
 * jamais servi. La radiation est datée comme pour la pension différée ; un
 * régime que la table ne porte pas est présumé pouvoir pensionner, au niveau
 * « estimée ».
 */
export function droitRegimeSpecial(moteur, periode, carriere, anneeLiquidation) {
  // Les trois régimes interpénétrés se lisent ensemble : voir `droitAPension`.
  const droit = coordonner.droitAPension(moteur, periode.regime, carriere, anneeLiquidation);
  if (droit === null) {
    return null;
  }
  return [
    droit.pension,
    bonificationOuverte(carriere, droit.recrutement, droit.derniere, anneeLiquidation),
    droit.fiabilite,
  ];
}

/**
 * Le droit aux trimestres d'enfants d'un régime spécial est-il ouvert ? Sur
 * la naissance des enfants que la chronologie porte — présumée aux trente ans
 * de leur mère tant que rien n'est déclaré : né depuis
 * 2004, après le recrutement (L. 12 bis) ; né avant, tout enfant jusqu'en 2003,
 * l'enfant né en service de 2004 à 2010, l'enfant né avant la radiation depuis
 * 2011 (R. 13). Voir `bonification_ouverte` du Python.
 */
export function bonificationOuverte(carriere, recrutement, derniere, anneeLiquidation) {
  const naissance = carriere.anneeNaissanceDesEnfants;
  if (naissance >= MAJORATION_APRES_RECRUTEMENT_DEPUIS) {
    return naissance >= recrutement;
  }
  if (anneeLiquidation >= BONIFICATION_NE_AVANT_RADIATION_DEPUIS) {
    return naissance <= derniere;
  }
  if (anneeLiquidation >= BONIFICATION_NE_EN_SERVICE_DEPUIS) {
    return recrutement <= naissance && naissance <= derniere;
  }
  return true;
}

/**
 * Le candidat du régime où l'assurée a été affiliée en dernier lieu ; à
 * égalité, celui qui compte le plus de trimestres, puis le dernier code par
 * ordre alphabétique. La dernière année se lit sur les lignes que chaque
 * régime reçoit, et on ne la cherche que s'il faut départager.
 */
export function derniereAffiliation(moteur, carriere, candidats, anneeLiquidation) {
  if (candidats.size === 1) {
    return [...candidats.values()][0][1];
  }
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
      if (candidats.has(code)) {
        dernieres.set(code, Math.max(dernieres.get(code) ?? 0, ligne.annee));
      }
    }
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
