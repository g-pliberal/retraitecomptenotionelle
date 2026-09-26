/**
 * Ce que les étapes du droit partagent avec la liquidation : la dernière
 * année d'un régime, la date d'effet d'une demande.
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
