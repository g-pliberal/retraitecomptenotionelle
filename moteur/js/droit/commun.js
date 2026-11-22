/**
 * Ce que les étapes du droit partagent avec la liquidation : la dernière
 * année d'un régime, la période qui liquide une pension à sa date d'effet,
 * la date d'effet d'une demande, ce qu'est une année
 * cotisée, les parts de la majoration pour enfants à une date, et de qui
 * est l'âge légal qu'une règle lit : l'assuré, ou le conjoint survivant.
 */

import { DateMois, MOIS_PAR_AN, origineDesAges } from "../calendrier.js";

/**
 * Les complémentaires que leurs statuts font demander à leur âge, sans la
 * base : elles forment une unité à elles. La CRPNPAC, ses deux tranches,
 * « dès lors qu'il réunit [...] 1° Avoir atteint l'âge de cinquante ans »
 * (R. 426-11 du code de l'aviation civile). La CAVOM, la CARPIMKO et la
 * CPRN, chacune à l'âge de ses statuts, avant la base ou après. Voir
 * `SANS_LEUR_BASE` (commun.py). L'Ircantec n'en est pas : elle suit la base,
 * mais la devance quand celle-ci n'ouvre pas encore
 * (`ouvrir.ageAuPlusTotSansLaBase`, `departs.departsEtDemandes`).
 */
export const SANS_LEUR_BASE = new Set(["carpv_complementaire", "cavec_complementaire",
  "cavom_complementaire", "carpimko_complementaire", "cprn_complementaire",
  "crpnpac", "crpnpac_tranche_2"]);

/** La fiche des coefficients d'anticipation de l'Ircantec (article 16). */
export const FICHE_DES_COEFFICIENTS_IRCANTEC = "coefficient_anticipation_ircantec";

/**
 * Dernière année pour laquelle le régime a des paramètres : celle où finit sa
 * dernière ligne de cotisation, 2100 au plus.
 */
export function derniereAnnee(regime) {
  if (regime.cotisation.length === 0) {
    return 2100;
  }
  const annees = regime.cotisation.map((ligne) => (ligne.au === null ? 9999 : ligne.au));
  return Math.min(Math.max(...annees), 2100);
}

/**
 * Les paramètres de `regime` qui liquident une pension prenant effet le 1er
 * du mois `date` : la ligne de liquidation en vigueur ce jour-là, au jour
 * quand un texte coupe l'année (`Regime.aLaDate`) ; après la dernière année du
 * régime, celle qui l'est au dernier mois de cette année. `null` quand aucune
 * ne la couvre.
 */
export function periodeDeLiquidation(regime, date) {
  return regime.aLaDate(jourDeLiquidation(regime, date));
}

/**
 * Le jour (AAAA-MM-JJ) dont `regime` lit les paramètres d'une pension prenant
 * effet le 1er du mois `date` : ce jour-là, et après la dernière année du
 * régime, le 1er décembre de cette année.
 */
export function jourDeLiquidation(regime, date) {
  const derniere = derniereAnnee(regime);
  const [annee, mois] = date.annee > derniere ? [derniere, 12] : [date.annee, date.mois];
  return `${String(annee).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`;
}

/**
 * L'âge légal de L'ASSURÉ (L. 161-17-2), et sa fiabilité : celui de la version
 * de la fiche `age_legal_par_generation` sous laquelle son droit s'ouvre, ses
 * âges comptés de son jour de naissance (`AgesOuverture.age`). C'est l'âge de
 * la personne, quelle que soit la date d'effet de la pension qu'on calcule ;
 * l'âge qu'une version oppose à une pension d'une date donnée se lit par
 * `moteur.agesOuverture.aLEffet`. `null` quand aucune version ne le dit.
 *
 * @returns {[number, number] | null} âge et fiabilité.
 */
export function ageLegalDeLAssure(moteur, carriere) {
  return moteur.agesOuverture.age(carriere.generation, carriere.origineDesAges ?? null);
}

/**
 * L'âge légal du CONJOINT SURVIVANT, né ce jour-là (AAAA-MM-JJ), et sa
 * fiabilité : le sien, celui de la version sous laquelle son propre droit
 * s'ouvre, et non celui de l'assuré décédé ni celui de la date d'effet de la
 * réversion. `null` quand aucune version ne le dit.
 *
 * @returns {[number, number] | null} âge et fiabilité.
 */
export function ageLegalDuConjointSurvivant(moteur, naissance) {
  const annee = Number(naissance.slice(0, 4));
  const mois = Number(naissance.slice(5, 7));
  const generation = Math.round((annee + (mois - 1) / MOIS_PAR_AN) * 1000) / 1000;
  return moteur.agesOuverture.age(
    generation, origineDesAges(new DateMois(annee, mois), Number(naissance.slice(8, 10))));
}

/**
 * L'âge du taux plein (L. 351-8, 1°) de L'ASSURÉ, et sa fiabilité : celui de la
 * version de la fiche `age_annulation_decote` sous laquelle il l'atteint, ses
 * âges comptés de son jour de naissance (`AgesAnnulationDecote.age`). C'est
 * l'âge de la personne : il date ce qui se passe quand elle l'atteint — la
 * retraite qui suit l'invalidité, le terme de l'activité après la pension.
 * `null` quand aucune version ne le dit.
 *
 * @returns {[number, number] | null} âge et fiabilité.
 */
export function ageDuTauxPleinDeLAssure(moteur, carriere) {
  return moteur.agesAnnulationDecote.age(carriere.generation, carriere.origineDesAges ?? null);
}

/**
 * L'âge du taux plein que le droit oppose à la PENSION de cette carrière. Sa
 * date d'effet choisit la version de la fiche (`AgesAnnulationDecote.aLEffet`) :
 * avant le 1er avril 1983, il n'y a pas de règle commune, et `null` laisse au
 * régime la valeur de sa période. Depuis, c'est l'âge de l'assuré, celui de la
 * version sous laquelle il l'atteint ({@link ageDuTauxPleinDeLAssure}) : pour
 * toute pension dont la décote en dépend, c'est celui de la version à la date
 * d'effet. Les deux ne divergent que pour l'assuré né avant 1955 dont la
 * pension prend effet après le 1er septembre 2023, à 68 ans passés : il garde
 * l'âge qu'il a atteint, que les statuts de 2017 de la CARCDSF écrivent aussi
 * génération par génération, quand la rédaction de 2023 dirait 67 ans (question
 * au propriétaire, note de l'étape 3 du 21 novembre 2026).
 *
 * @returns {[number, number] | null} âge et fiabilité.
 */
export function ageDuTauxPleinDeLaPension(moteur, carriere) {
  const date = dateDEffet(carriere);
  if (date !== null && !moteur.agesAnnulationDecote.aLEffet(date).regleCommune()) {
    return null;
  }
  return ageDuTauxPleinDeLAssure(moteur, carriere);
}

/**
 * La date d'effet d'une demande (AAAA-MM-JJ) : le premier jour du mois de la
 * liquidation, ou `null` pour une carrière sans départ.
 */
export function dateDEffet(carriere) {
  if (carriere.age_liquidation === null || carriere.age_liquidation === undefined) {
    return null;
  }
  const date = carriere.dateLiquidation;
  return `${String(date.annee).padStart(4, "0")}-${String(date.mois).padStart(2, "0")}-01`;
}

/**
 * La ligne compte-t-elle parmi les trimestres COTISÉS ? Une année d'emploi,
 * sauf celle que tous ses régimes valident sans cotisation : l'activité
 * cultuelle d'avant 1979, que la CAVIMAC valide gratuitement. La carrière
 * longue et le minimum contributif majoré lisent ce compte. Voir commun.py.
 */
export function ligneCotisee(moteur, carriere, ligne) {
  return ligne.cotise && !moteur.affiliations.valideeSansCotisation(
    ligne.affiliation, ligne.annee,
    moteur.affiliations.dateEntree(carriere, ligne.affiliation, ligne.annee));
}

/**
 * Le code de la majoration pour enfants, que la revalorisation mène à chaque
 * échéance.
 */
export const MAJORATION_ENFANTS = "majoration_enfants";

/**
 * Les parts de la dernière étape commencée à `quand` (AAAA-MM-JJ), celles de
 * la première avant elle.
 */
function etapeAu(etapes, quand) {
  let retenues = etapes[0][1];
  for (const [depuis, parts] of etapes) {
    if (depuis <= quand) {
      retenues = parts;
    }
  }
  return retenues;
}

/**
 * Les parts de la majoration pour enfants, régime par régime : celles de la
 * date d'effet, ou, à `quand` (AAAA-MM-JJ), celles qu'elle sert alors, les
 * enfants à charge qui ne le sont plus retirés (`a_charge` de l'avantage) ;
 * sans `avecACharge`, celles des seuls enfants nés ou élevés, que la réversion
 * lit. Un régime peut y revenir : la part qu'elle perd s'y écrit en négatif.
 * Voir `parts_de_la_majoration` du Python.
 */
export function partsDeLaMajoration(avantages, quand = null, avecACharge = true) {
  const parts = [];
  for (const avantage of avantages) {
    if (avantage.code !== MAJORATION_ENFANTS) {
      continue;
    }
    parts.push(...(avantage.par_regime ?? []));
    const aCharge = avantage.a_charge ?? [];
    if (aCharge.length > 0 && !avecACharge) {
      parts.push(...aCharge[0][1].map(([code, part]) => [code, -part]));
      continue;
    }
    if (quand === null || aCharge.length === 0) {
      continue;
    }
    const servies = etapeAu(aCharge, quand);
    if (servies !== aCharge[0][1]) {
      parts.push(...aCharge[0][1].map(([code, part]) => [code, -part]));
      parts.push(...servies);
    }
  }
  return parts;
}

/**
 * Les parts de la majoration pour enfants nés ou élevés, régime par régime,
 * sans le coefficient d'anticipation qui a pu réduire celle de la date
 * d'effet, sous le même plafond (`par_regime_sans_anticipation` de
 * l'avantage) : celle que la réversion de l'Agirc-Arrco reprend depuis 2019
 * (circulaire 2020-02-DRJ, fiche 6, I.1.2.2). Voir
 * `parts_sans_anticipation` du Python.
 */
export function partsSansAnticipation(avantages) {
  return avantages.filter((avantage) => avantage.code === MAJORATION_ENFANTS)
    .flatMap((avantage) => avantage.par_regime_sans_anticipation ?? []);
}

/**
 * Les étapes de deux majorations pour enfants à charge réunies, celles de deux
 * départs que le scénario additionne : à chaque date de l'une ou de l'autre,
 * la somme de leurs parts. Voir `fusionner_les_charges` du Python.
 */
export function fusionnerLesCharges(une, autre) {
  if (une.length === 0) {
    return autre;
  }
  if (autre.length === 0) {
    return une;
  }
  const dates = [...new Set([...une.map(([depuis]) => depuis),
    ...autre.map(([depuis]) => depuis)])].sort();
  return dates.map((depuis) => [depuis, [...etapeAu(une, depuis), ...etapeAu(autre, depuis)]]);
}

/**
 * La majoration pour conjoint à charge que les étapes d'une pension servent à
 * `quand` (AAAA-MM-JJ) : celle de la dernière commencée, rien avant la
 * première (`conjoint` de la pension). Voir `majoration_du_conjoint` du Python.
 */
export function majorationDuConjoint(etapes, quand) {
  let servie = 0.0;
  for (const [depuis, montant] of etapes ?? []) {
    if (depuis <= quand) {
      servie = montant;
    }
  }
  return servie;
}
