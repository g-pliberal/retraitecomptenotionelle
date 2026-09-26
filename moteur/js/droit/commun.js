/**
 * Ce que les étapes du droit partagent avec la liquidation.
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
