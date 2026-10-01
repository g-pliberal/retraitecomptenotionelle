/**
 * Foyer et net (docs/architecture.md, § 7.4).
 *
 * Jumeau de `src/retraite_notionnelle/droit/foyer.py` : ce que le droit sert
 * en regardant toutes les ressources du bénéficiaire, et non une pension —
 * l'ASPA. Elle vient en DERNIER : elle est différentielle, et complète tout le
 * reste, majorations comprises, jusqu'au barème d'une personne seule. Elle
 * s'ouvre à 65 ans, à qui réside en France, et se revoit à chaque échéance.
 * Ce que l'étape écrit, `Foyer`, suit son schéma,
 * `data/reference/etapes/foyer_et_net.yaml`.
 */

import { DateMois } from "../calendrier.js";
import { Fiabilite, nomFiabilite } from "../serie.js";
import { pensionsEtrangeresServies } from "./etranger.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

/** Ce que l'étape « foyer et net » écrit, à une date. */
export class Foyer {
  constructor({ personne, date, ressources, minimumVieillesse, plafond, fiabilite,
    etrangeres = 0.0 }) {
    this.personne = personne;
    this.date = date;
    this.ressources = ressources;
    this.minimumVieillesse = minimumVieillesse;
    this.plafond = plafond;
    this.fiabilite = fiabilite;
    /** Celles des ressources qu'un autre État sert, à part des pensions françaises. */
    this.etrangeres = etrangeres;
  }

  /** L'ASPA, sous la forme où la cascade des avantages la dit. */
  avantage() {
    return {
      code: "minimum_vieillesse",
      libelle: "Minimum vieillesse (ASPA)",
      montant: this.minimumVieillesse,
      detail: "allocation différentielle, barème d'une personne seule",
    };
  }

  /** Le foyer, tel que le schéma de l'étape le décrit. */
  donnees() {
    return {
      schema_version: SCHEMA_VERSION, personne: this.personne, date: this.date,
      ressources: this.ressources, etrangeres: this.etrangeres,
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
 * L'ASPA qu'appellent `ressources`, les pensions françaises, en `annee`.
 * `ageAtteint` dit si l'âge de l'allocation l'est : à la date d'effet pour une
 * liquidation, dans l'année pour une échéance ; la `carriere`, les pensions
 * qu'un autre État sert à cette date, qui s'ajoutent aux ressources, et l'État
 * où le bénéficiaire réside hors de France, s'il le déclare : elle n'y est pas
 * servie. Voir le Python.
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
  let montant = 0.0;
  let plafond = null;
  let fiabilite = Fiabilite.CERTIFIEE;
  if (ageAtteint && moteur.parametres.minimum_vieillesse_dans_le_scenario_actuel
      && conditionDeResidence(moteur, residence, jour, moisEnFrance)
      && !(contexte !== null && contexte.neutralise("avantages_non_contributifs"))) {
    const bareme = moteur.minimumVieillesse.plafond(annee);
    if (bareme !== null) {
      plafond = bareme[0];
      montant = Math.max(0.0, bareme[0] - total);
      if (montant > 0) {
        fiabilite = bareme[1];
      }
    }
  }
  return new Foyer({
    personne, date, ressources: total, minimumVieillesse: montant, plafond, fiabilite,
    etrangeres,
  });
}
