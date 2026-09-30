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

import { formatFixe } from "../format.js";
import { dateDEffet } from "./commun.js";

/** L'âge d'une version qui le lit à la génération : celui de L. 161-17-2. */
export const AGE_LEGAL_PAR_GENERATION = "age_legal_par_generation";

/**
 * L'âge de l'allocation de solidarité aux personnes âgées de droit commun :
 * celui de `MinimumVieillesse.AGE_OUVERTURE`, recopié pour que ce module
 * n'importe pas les tables du scénario 1.
 */
export const AGE_DE_L_ASPA = 65.0;

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
 * L'âge où l'allocation de solidarité aux personnes âgées s'ouvre à cet
 * assuré : soixante-cinq ans, abaissé pour l'inapte et l'ex-invalide à l'âge
 * de la version (R. 815-1 ; paramètre `age_aspa` de la fiche
 * `inaptitude_au_travail`, à la date de liquidation). Voir `age_de_l_aspa`
 * du Python.
 */
export function ageDeLAspa(moteur, carriere) {
  if (!reconnuInapte(carriere)) {
    return AGE_DE_L_ASPA;
  }
  const date = dateDEffet(carriere);
  const version = date === null ? null : moteur.invalidites.version("inaptitude", date);
  const valeur = version === null ? undefined : version.parametres.age_aspa;
  if (valeur === undefined || valeur === null) {
    return AGE_DE_L_ASPA;
  }
  return Math.min(AGE_DE_L_ASPA, ageDeLaFiche(moteur, carriere, valeur));
}

/**
 * La radiation des cadres pour invalidité qui liquide la pension de ce régime :
 * celle de la carrière, quand le régime est l'un des trois du code des
 * pensions que la fiche `retraite_pour_invalidite_fonction_publique` nomme ;
 * `null` sinon.
 */
export function radiationDuRegime(moteur, regime, carriere) {
  const radiation = carriere.radiationPourInvalidite;
  if (radiation === null || !moteur.invalidites.regimes("fonction_publique").has(regime)) {
    return null;
  }
  return radiation;
}

/**
 * La version de la fiche `retraite_pour_invalidite_fonction_publique` qui
 * s'applique à la pension de ce régime liquidée à la date de `carriere`, quand
 * elle l'est pour invalidité ; `null` sinon.
 */
export function retraitePourInvalidite(moteur, regime, carriere) {
  if (radiationDuRegime(moteur, regime, carriere) === null) {
    return null;
  }
  const date = dateDEffet(carriere);
  return date === null ? null : moteur.invalidites.version("fonction_publique", date);
}

/** L'indice majoré qui borne la part du traitement que la rente compte entière. */
export const INDICE_DE_LA_RENTE = 681;

/** La rente viagère d'invalidité de L. 28. Voir le Python. */
export function renteViagereDInvalidite(traitement, taux, seuil) {
  const compte = Math.min(traitement, seuil)
    + Math.max(0.0, Math.min(traitement, 10.0 * seuil) - seuil) / 3.0;
  return taux * compte;
}

/**
 * La pension du fonctionnaire radié pour invalidité, rente comprise, et ce que
 * le détail en dit : `[montant, detail]`. Voir `pension_du_fonctionnaire_invalide`
 * du Python.
 */
export function pensionDuFonctionnaireInvalide(moteur, carriere, version, pension, traitement,
  annee) {
  const parametres = version.parametres;
  const radiation = carriere.radiationPourInvalidite;
  const taux = (radiation.taux ?? 0.0) / 100.0;
  const details = [];
  let servie = pension;
  const plancher = Number(parametres.plancher_part_du_traitement ?? 0.0) * traitement;
  if (taux + 1e-9 >= Number(parametres.plancher_taux_invalidite ?? 1.0) && servie < plancher) {
    servie = plancher;
    details.push(`portée à ${formatFixe(plancher, 2, true)} €, la moitié du traitement (L. 30)`);
  }
  let rente = 0.0;
  if (radiation.imputable && taux > 0) {
    const valeur = moteur.minimumGaranti.valeurDUnIndice(INDICE_DE_LA_RENTE, annee);
    const seuil = valeur !== null ? valeur[0] : traitement;
    rente = renteViagereDInvalidite(traitement, taux, seuil);
  }
  const total = servie + rente;
  if (parametres.plafond_total && traitement > 0 && total > traitement) {
    const reduction = traitement / total;
    servie *= reduction;
    rente *= reduction;
    details.push("réduite au traitement (L. 30 ter)");
  }
  if (rente > 0) {
    details.push(`rente viagère d'invalidité de ${formatFixe(rente, 2, true)} € à `
      + `${formatTaux(radiation.taux)} % (L. 28)`);
  }
  return [servie + rente, details.join(" ; ")];
}

/** Un taux d'invalidité comme Python l'écrit avec `:g` : 70, 62.5. */
function formatTaux(taux) {
  return String(Number(taux));
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
