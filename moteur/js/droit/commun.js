/**
 * Ce que les étapes du droit partagent avec la liquidation : la dernière
 * année d'un régime, la date d'effet d'une demande, ce qu'est une année
 * cotisée, les parts de la majoration pour enfants à une date.
 *
 * Jumeau de `src/retraite_notionnelle/droit/commun.py`.
 */

/** Dernière année pour laquelle le régime a des paramètres. */
export function derniereAnnee(regime) {
  if (regime.periodes.length === 0) {
    return 2100;
  }
  const annees = regime.periodes.map((p) => (p.fin === null ? 9999 : p.fin));
  return Math.min(Math.max(...annees), 2100);
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
    ligne.affiliation, ligne.annee, carriere.dateEntree(ligne.affiliation));
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
 * enfants à charge qui ne le sont plus retirés (`a_charge` de l'avantage). Un
 * régime peut y revenir : la part qu'elle perd s'y écrit en négatif. Voir
 * `parts_de_la_majoration` du Python.
 */
export function partsDeLaMajoration(avantages, quand = null) {
  const parts = [];
  for (const avantage of avantages) {
    if (avantage.code !== MAJORATION_ENFANTS) {
      continue;
    }
    parts.push(...(avantage.par_regime ?? []));
    const aCharge = avantage.a_charge ?? [];
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
