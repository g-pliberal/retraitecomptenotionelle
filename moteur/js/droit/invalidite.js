/**
 * L'invalidité et l'inaptitude (docs/architecture.md, § 11) : ce que les
 * étapes du droit lisent des fiches du domaine, que `Invalidites` prépare.
 *
 * Jumeau de `src/retraite_notionnelle/droit/invalidite.py`, fonction pour
 * fonction. L'assuré reconnu inapte au travail — et l'ex-invalide, dont la
 * pension de vieillesse est celle « allouée en cas d'inaptitude au travail »
 * (L. 341-15) — a le taux plein quelle que soit sa durée, dans les régimes de
 * la fiche `inaptitude_au_travail`, à l'âge que la version dit. La pension
 * d'invalidité prend fin à cet âge, et la pension de vieillesse la remplace
 * d'office au premier jour du mois qui suit (fiche
 * `pension_d_invalidite_substituee`) ; l'invalide qui travaille la garde
 * jusqu'à sa demande, au plus tard à l'âge du taux plein automatique, le
 * demandeur d'emploi indemnisé six mois de plus. Voir le Python.
 */

import { dateDEffet } from "./commun.js";

/** L'âge d'une version qui le lit à la génération : celui de L. 161-17-2. */
export const AGE_LEGAL_PAR_GENERATION = "age_legal_par_generation";

/** Le régime dont l'Agirc-Arrco et l'Ircantec suivent le taux plein. */
export const REGIME_DES_SALARIES = "regime_general";

/** Ce que devient la pension d'invalidité de qui travaille à l'âge. */
export const MAINTIEN_JUSQU_A_LA_DEMANDE = "maintien_jusqu_a_la_demande";
export const OPPOSITION = "opposition";

/** Pourquoi la substitution ne se fait pas à l'âge. */
export const ACTIVITE = "activite";
export const CHOMAGE = "chomage";

/** Un âge qu'une version écrit : un nombre, ou l'âge légal de la génération. */
export function ageDeLaFiche(moteur, carriere, valeur) {
  if (valeur === AGE_LEGAL_PAR_GENERATION) {
    const lu = moteur.agesOuverture.age(carriere.generation);
    return lu !== null ? lu[0] : 60.0;
  }
  return Number(valeur);
}

/** L'assuré est-il inapte au sens de L. 351-8, 2° ? */
export function reconnuInapte(carriere) {
  return carriere.inaptitude || carriere.pensionDInvalidite !== null;
}

/**
 * L'âge auquel ce régime ouvre le droit à l'inapte, au taux plein, pour une
 * pension qui prend effet à la date de liquidation de `carriere` ; `null`
 * quand l'assuré n'est pas inapte, que le régime n'applique pas la fiche ou
 * que la carrière n'a pas de départ.
 */
export function ageDInaptitude(moteur, regime, carriere) {
  if (!reconnuInapte(carriere) || !moteur.invalidites.regimes("inaptitude").has(regime)) {
    return null;
  }
  const date = dateDEffet(carriere);
  const version = date === null ? null : moteur.invalidites.version("inaptitude", date);
  if (version === null) {
    return null;
  }
  return ageDeLaFiche(moteur, carriere, version.parametres.age);
}

/** Le taux plein que ce régime sert à l'inapte, quelle que soit sa durée. */
export function tauxPleinDeLInapte(moteur, regime, carriere, ageLiquidation) {
  const age = ageDInaptitude(moteur, regime, carriere);
  return age !== null && ageLiquidation + 1e-9 >= age;
}

/**
 * La pension de vieillesse qui remplace la pension d'invalidité : `{date,
 * version, maintien}`, le mois où elle commence, la version qui la date, et
 * pourquoi ce n'est pas à l'âge (`activite`, `chomage`), `null` sinon.
 */
export class Substitution {
  constructor(date, version, maintien = null) {
    this.date = date;
    this.version = version;
    this.maintien = maintien;
    Object.freeze(this);
  }
}

/**
 * Le mois où la pension de vieillesse de l'ex-invalide commence, pour la
 * carrière et son départ déclaré ; `null` sans pension d'invalidité, ou quand
 * l'invalidité est née après l'âge de la substitution. Voir `substitution`
 * du Python.
 */
export function substitution(moteur, carriere) {
  const pension = carriere.pensionDInvalidite;
  if (pension === null || carriere.age_liquidation === null
      || carriere.age_liquidation === undefined) {
    return null;
  }
  const preparee = moteur.invalidites.fiches()[moteur.invalidites.constructor.FICHES.substitution];
  if (preparee === undefined) {
    return null;
  }
  let retenue = null;
  let age = null;
  let date = null;
  for (const version of preparee.versions) {
    age = ageDeLaFiche(moteur, carriere, version.parametres.age);
    date = carriere.dateDeLAge(age);
    const [debut, fin] = version.bornes["liquidation.date_effet"];
    const jour = `${String(date.annee).padStart(4, "0")}-${String(date.mois).padStart(2, "0")}-01`;
    if ((debut === null || debut <= jour) && (fin === null || jour < fin)) {
      retenue = version;
      break;
    }
  }
  if (retenue === null || pension.debut.rang >= date.rang) {
    return null;
  }
  const parametres = retenue.parametres;
  const declare = carriere.dateLiquidation;
  const annee = carriere.moisDeLAnniversaire(age).annee;
  const lignes = carriere.lignesDe(annee);
  const principale = lignes.length > 0 ? lignes[0] : null;
  const nature = principale !== null ? principale.type_periode : null;
  const plusTardif = (a, b) => (a.rang >= b.rang ? a : b);
  const plusPrecoce = (a, b) => (a.rang <= b.rang ? a : b);
  if (nature === "emploi" && principale.revenu > 0
      && [MAINTIEN_JUSQU_A_LA_DEMANDE, OPPOSITION].includes(parametres.invalide_qui_travaille)) {
    let plusTard = declare;
    if (parametres.invalide_qui_travaille === MAINTIEN_JUSQU_A_LA_DEMANDE) {
      const automatique = moteur.agesAnnulationDecote.age(carriere.generation);
      plusTard = plusPrecoce(declare, carriere.dateDeLAge(
        automatique !== null ? automatique[0] : 65.0));
    }
    return new Substitution(plusTardif(date, plusTard), retenue.id, ACTIVITE);
  }
  const mois = parametres.maintien_du_demandeur_d_emploi_mois;
  if (nature === "chomage_indemnise" && mois) {
    return new Substitution(
      plusTardif(date, plusPrecoce(declare, date.plusMois(Number(mois)))), retenue.id, CHOMAGE);
  }
  return new Substitution(date, retenue.id);
}
