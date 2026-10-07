/**
 * Foyer et net (docs/architecture.md, § 7.4).
 *
 * Jumeau de `src/retraite_notionnelle/droit/foyer.py` : ce que le droit sert
 * en regardant toutes les ressources du bénéficiaire, et non une pension —
 * l'ASPA. Elle vient en DERNIER : elle est différentielle, et complète tout le
 * reste, majorations comprises, jusqu'au barème du foyer — d'une personne
 * seule, ou du couple quand un conjoint est déclaré, ses ressources comptées.
 * Elle s'ouvre à 65 ans, à qui réside en France, et se revoit à chaque
 * échéance. Ce que l'étape écrit, `Foyer`, suit son schéma,
 * `data/reference/etapes/foyer_et_net.yaml`.
 */

import { DateMois } from "../calendrier.js";
import { Fiabilite, nomFiabilite } from "../serie.js";
import { pensionsEtrangeresServies } from "./etranger.js";
import { AGE_DE_L_ASPA } from "./invalidite.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

/**
 * Les trois barèmes de l'allocation : une personne seule ; un couple dont la
 * personne est seule allocataire, au plus le montant d'une personne seule
 * (D. 815-1, a) ; un couple dont les deux membres le sont, qui se partagent le
 * montant du couple par moitié (D. 815-1, b).
 */
export const PERSONNE_SEULE = "personne_seule";
export const COUPLE = "couple";
export const DEUX_ALLOCATAIRES = "deux_allocataires";

/** Ce que la cascade des avantages dit de chacun. */
const DETAILS = {
  [PERSONNE_SEULE]: "allocation différentielle, barème d'une personne seule",
  [COUPLE]: "allocation différentielle, plafond du couple, au plus le montant "
    + "d'une personne seule",
  [DEUX_ALLOCATAIRES]: "allocation différentielle, barème d'un couple "
    + "d'allocataires, servie par moitié",
};

/** Ce qu'elle en dit avant 2007, quand le minimum tient en deux étages. */
const DETAILS_DEUX_ETAGES = {
  [PERSONNE_SEULE]: "allocation aux vieux travailleurs salariés et allocation "
    + "supplémentaire, sous le plafond d'une personne seule",
  [COUPLE]: "allocation aux vieux travailleurs salariés et allocation "
    + "supplémentaire, sous le plafond du couple",
  [DEUX_ALLOCATAIRES]: "allocation aux vieux travailleurs salariés et allocation "
    + "supplémentaire du ménage, sous le plafond du couple, servie par moitié",
};

/** Ce que l'étape « foyer et net » écrit, à une date. */
export class Foyer {
  constructor({ personne, date, ressources, minimumVieillesse, plafond, fiabilite,
    etrangeres = 0.0, bareme = PERSONNE_SEULE, ressourcesConjoint = 0.0,
    deuxEtages = false }) {
    this.personne = personne;
    this.date = date;
    this.ressources = ressources;
    this.minimumVieillesse = minimumVieillesse;
    this.plafond = plafond;
    this.fiabilite = fiabilite;
    /** Celles des ressources qu'un autre État sert, à part des pensions françaises. */
    this.etrangeres = etrangeres;
    /** Le barème du foyer : `PERSONNE_SEULE`, `COUPLE` ou `DEUX_ALLOCATAIRES`. */
    this.bareme = bareme;
    /** Les ressources du conjoint, que le plafond du couple compte avec les siennes. */
    this.ressourcesConjoint = ressourcesConjoint;
    /** Avant 2007, le minimum à deux étages : il borne les ressources au plafond sans les y porter. */
    this.deuxEtages = deuxEtages;
  }

  /** L'ASPA, sous la forme où la cascade des avantages la dit. */
  avantage() {
    return {
      code: "minimum_vieillesse",
      libelle: "Minimum vieillesse (ASPA)",
      montant: this.minimumVieillesse,
      detail: (this.deuxEtages ? DETAILS_DEUX_ETAGES : DETAILS)[this.bareme],
    };
  }

  /**
   * Les pensions françaises de la personne et l'allocation, ensemble : le
   * barème d'une personne seule, moins ce que les pensions étrangères en
   * remplissent ; dans un couple, ses pensions et sa part de l'allocation ;
   * avant 2007, ses pensions et les deux étages, que le plafond borne.
   */
  servieAvec(pensions) {
    if (this.bareme === PERSONNE_SEULE && !this.deuxEtages) {
      return this.plafond - this.etrangeres;
    }
    return pensions + this.minimumVieillesse;
  }

  /** Le foyer, tel que le schéma de l'étape le décrit. */
  donnees() {
    return {
      schema_version: SCHEMA_VERSION, personne: this.personne, date: this.date,
      ressources: this.ressources, etrangeres: this.etrangeres, bareme: this.bareme,
      ressources_conjoint: this.ressourcesConjoint,
      minimum_vieillesse: this.minimumVieillesse,
      fiabilite: nomFiabilite(this.fiabilite),
    };
  }
}

/**
 * La condition de résidence de l'allocation à cette date (fiche
 * `residence_et_minimum_vieillesse`) : elle n'est servie qu'en France, à qui y
 * séjourne plus de six mois de l'année civile, plus de neuf depuis le
 * 1er septembre 2023. `residence` est l'État où le bénéficiaire réside hors de
 * France, `null` pour qui n'en déclare pas (présomption `residence_en_france`) ;
 * `moisEnFrance`, les mois qu'il y passe chaque année, `null` pour toute
 * l'année. Voir `condition_de_residence` du Python.
 */
export function conditionDeResidence(moteur, residence, date, moisEnFrance = null) {
  const ailleurs = residence !== null && residence !== undefined;
  if (!ailleurs && (moisEnFrance === null || moisEnFrance === undefined)) {
    return true;
  }
  const version = moteur.carrieresHorsDeFrance.version(
    "residence", { "liquidation.date_effet": date });
  if (version === null || !version.parametres.residence_requise) {
    return true;
  }
  if (ailleurs) {
    return false;
  }
  const seuil = version.parametres.mois_de_residence_plus_de ?? null;
  return seuil === null || moisEnFrance > seuil;
}

/**
 * Le conjoint avec qui la personne vit à cette date, dont les ressources
 * comptent au plafond du couple : celui que la saisie déclare, une fois le
 * mariage célébré ; `null` sinon. Voir `conjoint_au_foyer` du Python.
 */
export function conjointAuFoyer(carriere, jour) {
  const conjoint = carriere === null ? null : carriere.conjoint;
  if (conjoint === null || conjoint.mariage > jour) {
    return null;
  }
  return conjoint;
}

/**
 * Si le conjoint peut lui aussi prétendre à l'allocation à cette date : il en
 * a l'âge, soixante-cinq ans. Voir `conjoint_allocataire` du Python.
 */
export function conjointAllocataire(conjoint, jour) {
  const naissance = conjoint.naissance;
  const anniversaire = `${String(Number(naissance.slice(0, 4)) + Math.trunc(AGE_DE_L_ASPA))
    .padStart(4, "0")}${naissance.slice(4)}`;
  return anniversaire <= jour;
}

/**
 * Le minimum vieillesse d'avant 2007, et le plafond qui le borne : le premier
 * étage porte la pension au montant de l'allocation aux vieux travailleurs
 * salariés (L. 814-2) ; le second, l'allocation supplémentaire, se réduit de ce
 * que son total et les ressources du foyer, premier étage compris, dépassent le
 * plafond (L. 815-8). Deux allocataires se partagent par moitié le montant du
 * ménage, le double de celui d'un seul avant juillet 1982 ; le premier étage
 * n'est servi que sous le plafond, que les ressources du conjoint peuvent
 * atteindre ; avant 1956, le premier étage seul. Voir `avant_l_aspa` du Python.
 */
export function avantLAspa(etages, bareme, ressources, duConjoint) {
  const seule = bareme === PERSONNE_SEULE;
  const plafond = seule ? etages.plafond : etages.plafondCouple;
  let total = seule ? ressources : ressources + duConjoint;
  let premier = Math.max(0.0, etages.avts - ressources);
  if (plafond === null || plafond === undefined) {
    return [premier, null];
  }
  premier = Math.max(0.0, Math.min(premier, plafond - total));
  total += premier;
  let maximum = etages.supplementaire;
  let part = 1.0;
  if (bareme === DEUX_ALLOCATAIRES) {
    total += Math.max(0.0, Math.min(etages.avts - duConjoint, plafond - total));
    maximum = etages.supplementaireMenage === null || etages.supplementaireMenage === undefined
      ? 2 * etages.supplementaire : etages.supplementaireMenage;
    part = 0.5;
  }
  return [premier + part * Math.max(0.0, Math.min(maximum, plafond - total)), plafond];
}

/**
 * L'ASPA qu'appellent `ressources`, les pensions françaises, en `annee`.
 * `ageAtteint` dit si l'âge de l'allocation l'est : à la date d'effet pour une
 * liquidation, dans l'année pour une échéance ; la `carriere`, les pensions
 * qu'un autre État sert à cette date, qui s'ajoutent aux ressources, l'État
 * où le bénéficiaire réside hors de France, s'il le déclare : elle n'y est pas
 * servie, et le conjoint, qui donne au foyer le barème du couple. Voir le
 * Python.
 */
export function foyerEtNet(moteur, personne, date, annee, ressources, ageAtteint,
  contexte = null, carriere = null) {
  const jour = date ?? `${annee}-12-31`;
  const residence = carriere === null ? null : carriere.residence;
  const moisEnFrance = carriere === null ? null : carriere.moisEnFrance;
  const etrangeres = carriere === null ? 0.0 : pensionsEtrangeresServies(
    moteur.macro, carriere, new DateMois(Number(jour.slice(0, 4)), Number(jour.slice(5, 7))),
    annee);
  const total = ressources + etrangeres;
  const conjoint = conjointAuFoyer(carriere, jour);
  const duConjoint = conjoint === null || conjoint.ressources === null
    || conjoint.ressources === undefined ? 0.0 : Number(conjoint.ressources);
  let bareme = PERSONNE_SEULE;
  if (conjoint !== null) {
    bareme = conjointAllocataire(conjoint, jour) ? DEUX_ALLOCATAIRES : COUPLE;
  }
  let montant = 0.0;
  let plafond = null;
  let fiabilite = Fiabilite.CERTIFIEE;
  const servie = ageAtteint && moteur.parametres.minimum_vieillesse_dans_le_scenario_actuel
    && conditionDeResidence(moteur, residence, jour, moisEnFrance)
    && !(contexte !== null && contexte.neutralise("avantages_non_contributifs"));
  const etages = servie ? moteur.minimumVieillesse.deuxEtages(annee) : null;
  if (etages !== null) {
    // Avant l'ASPA, deux étages (action 138, étape 6).
    [montant, plafond] = avantLAspa(etages, bareme, total, duConjoint);
    if (montant > 0) {
      fiabilite = etages.fiabilite;
    }
  } else if (servie) {
    const seule = moteur.minimumVieillesse.plafond(annee);
    const couple = bareme === PERSONNE_SEULE
      ? null : moteur.minimumVieillesse.plafondCouple(annee);
    if (bareme === PERSONNE_SEULE && seule !== null) {
      plafond = seule[0];
      montant = Math.max(0.0, seule[0] - total);
      if (montant > 0) {
        fiabilite = seule[1];
      }
    } else if (seule !== null && couple !== null) {
      // Ce qui manque au couple pour atteindre son plafond : partagé entre deux
      // allocataires, borné au montant d'une personne seule pour un seul.
      plafond = couple[0];
      const manque = Math.max(0.0, couple[0] - total - duConjoint);
      montant = bareme === DEUX_ALLOCATAIRES ? manque / 2.0 : Math.min(seule[0], manque);
      if (montant > 0) {
        fiabilite = bareme === DEUX_ALLOCATAIRES ? couple[1] : Math.min(couple[1], seule[1]);
      }
    }
  }
  return new Foyer({
    personne, date, ressources: total, minimumVieillesse: montant, plafond, fiabilite,
    etrangeres, bareme, ressourcesConjoint: duConjoint, deuxEtages: etages !== null,
  });
}
