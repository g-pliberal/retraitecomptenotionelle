/**
 * Ce que les étapes du droit partagent avec la liquidation : la dernière
 * année d'un régime, la date d'effet d'une demande, ce qu'est une année
 * cotisée.
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
