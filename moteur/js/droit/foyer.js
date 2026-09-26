/**
 * Foyer et net (docs/architecture.md, § 7.4).
 *
 * Jumeau de `src/retraite_notionnelle/droit/foyer.py` : ce que le droit sert
 * en regardant toutes les ressources du bénéficiaire, et non une pension —
 * l'ASPA. Elle vient en DERNIER : elle est différentielle, et complète tout le
 * reste, majorations comprises, jusqu'au barème d'une personne seule. Elle
 * s'ouvre à 65 ans et se revoit à chaque échéance. Ce que l'étape écrit,
 * `Foyer`, suit son schéma, `data/reference/etapes/foyer_et_net.yaml`.
 */

import { Fiabilite, nomFiabilite } from "../serie.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

/** Ce que l'étape « foyer et net » écrit, à une date. */
export class Foyer {
  constructor({ personne, date, ressources, minimumVieillesse, plafond, fiabilite }) {
    this.personne = personne;
    this.date = date;
    this.ressources = ressources;
    this.minimumVieillesse = minimumVieillesse;
    this.plafond = plafond;
    this.fiabilite = fiabilite;
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
      ressources: this.ressources, minimum_vieillesse: this.minimumVieillesse,
      fiabilite: nomFiabilite(this.fiabilite),
    };
  }
}

/**
 * L'ASPA qu'appellent `ressources` en `annee`. `ageAtteint` dit si l'âge de
 * l'allocation l'est : à la date d'effet pour une liquidation, dans l'année
 * pour une échéance. Voir le Python.
 */
export function foyerEtNet(moteur, personne, date, annee, ressources, ageAtteint,
  contexte = null) {
  let montant = 0.0;
  let plafond = null;
  let fiabilite = Fiabilite.CERTIFIEE;
  if (ageAtteint && moteur.parametres.minimum_vieillesse_dans_le_scenario_actuel
      && !(contexte !== null && contexte.neutralise("avantages_non_contributifs"))) {
    const bareme = moteur.minimumVieillesse.plafond(annee);
    if (bareme !== null) {
      plafond = bareme[0];
      montant = Math.max(0.0, bareme[0] - ressources);
      if (montant > 0) {
        fiabilite = bareme[1];
      }
    }
  }
  return new Foyer({ personne, date, ressources, minimumVieillesse: montant, plafond, fiabilite });
}
