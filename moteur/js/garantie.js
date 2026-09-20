/**
 * Ce que coûte la garantie vieillesse, chiffrée sur la distribution des pensions.
 *
 * Portage de ``src/retraite_notionnelle/garantie.py``. La garantie du scénario 6
 * est une allocation DIFFÉRENTIELLE : elle ne verse que ce qui manque à une
 * pension pour atteindre son plancher. Son coût est donc entièrement celui de la
 * queue basse de la distribution, et c'est précisément ce qu'une grille de douze
 * cas types ne sait pas décrire.
 *
 * TROIS CONVENTIONS
 * 1. Les pensions d'une tranche de cent euros sont supposées réparties
 *    uniformément entre ses bornes.
 * 2. La tranche ouverte du haut est une masse ponctuelle à sa borne inférieure ;
 *    au-dessus du plancher — le cas ordinaire — elle ne coûte rien.
 * 3. La situation de foyer n'est pas connue : les deux planchers sont calculés,
 *    celui de qui vit à deux et celui de qui vit seul, et le coût réel est entre
 *    les deux.
 *
 * À ``facteur = 1``, le barème est appliqué aux pensions telles qu'elles sont, et
 * le chiffre ne doit rien au modèle. Un facteur inférieur déplace toute la
 * distribution dans le même rapport, ce que le scénario 6 ne fait pas
 * exactement : ce second chiffre est un ordre de grandeur, le premier un calcul.
 */

/**
 * Part de la tranche sous le plancher, et manque MOYEN sur toute la tranche.
 *
 * Le manque moyen est rapporté à la tranche entière et non aux seuls
 * bénéficiaires : c'est lui qu'il faut multiplier par l'effectif de la tranche
 * pour obtenir la dépense.
 */
export function manqueMoyen(borneInferieure, borneSuperieure, plancher) {
  if (borneSuperieure === null || borneSuperieure === undefined) {
    const manque = Math.max(0, plancher - borneInferieure);
    return manque > 0 ? [1, manque] : [0, 0];
  }
  if (borneSuperieure <= plancher) {
    return [1, plancher - (borneInferieure + borneSuperieure) / 2];
  }
  if (borneInferieure >= plancher) {
    return [0, 0];
  }
  const largeur = borneSuperieure - borneInferieure;
  const concernee = (plancher - borneInferieure) / largeur;
  // Sur la seule fraction concernée, le manque décroît linéairement de
  // ``plancher - borneInferieure`` à zéro : sa moyenne en est la moitié.
  return [concernee, concernee * (plancher - borneInferieure) / 2];
}

/**
 * Applique un plancher différentiel à la distribution, et en tire la dépense.
 *
 * ``plancherMensuel`` est exprimé dans les euros de la distribution : c'est à
 * l'appelant de l'y ramener, parce que lui seul sait dans quels euros son barème
 * est écrit.
 */
export function coutGarantie(distribution, effectifTotal, plancherMensuel,
                             facteur = 1.0) {
  if (facteur <= 0) {
    throw new Error("le facteur de déplacement doit être strictement positif");
  }
  let partBeneficiaires = 0;
  let manqueMensuel = 0;
  for (const tranche of distribution.tranches) {
    const superieure = tranche.borneSuperieure === null
      ? null : tranche.borneSuperieure * facteur;
    const [concernee, manque] = manqueMoyen(
      tranche.borneInferieure * facteur, superieure, plancherMensuel,
    );
    partBeneficiaires += tranche.part * concernee;
    manqueMensuel += tranche.part * manque;
  }
  return {
    plancherMensuel,
    facteur,
    partBeneficiaires,
    beneficiaires: partBeneficiaires * effectifTotal,
    complementMoyenMensuel: partBeneficiaires
      ? manqueMensuel / partBeneficiaires : 0,
    coutAnnuelMeur: manqueMensuel * effectifTotal * 12 / 1e6,
  };
}
