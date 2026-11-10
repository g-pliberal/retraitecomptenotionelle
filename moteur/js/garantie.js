/**
 * Ce que coûte la garantie vieillesse, chiffrée sur la distribution des pensions.
 *
 * Portage de ``src/retraite_notionnelle/garantie.py``. La garantie du scénario 6
 * est une allocation sous condition de ressources, DÉGRESSIVE depuis le 9
 * novembre 2026 (`complementGarantie`, que le moteur d'une carrière applique).
 * Son coût est entièrement celui de la queue basse de la distribution, et c'est
 * précisément ce qu'une grille de douze cas types ne sait pas décrire. Les
 * fonctions de coût de ce module, que seules les pages lisent, portent la même
 * forme que le coût du modèle (`_manque_moyen` de `garantie.py`) ; sans forme
 * donnée, elles rendent le barème différentiel, celui de l'ASPA.
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
 * Le complément que la garantie sert à des ressources données : son barème.
 *
 * DÉGRESSIF, à la forme suédoise (décisions 100 et 102 du programme, 9
 * novembre 2026). Jusqu'au pivot, ``partRetraitEntier`` du plancher, chaque
 * euro de ressources retire un euro de garantie ; au-delà, il n'en retire que
 * ``tauxRetrait``, et le complément s'éteint à
 * ``pivot + (plancher - pivot) / tauxRetrait``. Le plancher est celui de la
 * personne, isolement compris : la forme s'y applique en entier. À un et un,
 * c'est la garantie différentielle, ``max(0, plancher - ressources)``, au bit
 * près. Le moteur d'une carrière le lit, au départ (`scenario-notionnel.js`)
 * et aujourd'hui (`revalorisation.js`).
 */
export function complementGarantie(plancher, ressources, partRetraitEntier, tauxRetrait) {
  const pivot = partRetraitEntier * plancher;
  if (ressources <= pivot) {
    return Math.max(0.0, plancher - ressources);
  }
  return Math.max(0.0, plancher - pivot - tauxRetrait * (ressources - pivot));
}

/**
 * Part de la tranche que la garantie sert, et complément MOYEN sur toute la
 * tranche.
 *
 * Le complément moyen est rapporté à la tranche entière et non aux seuls
 * bénéficiaires : c'est lui qu'il faut multiplier par l'effectif de la tranche
 * pour obtenir la dépense. Le barème est celui de `complementGarantie`,
 * linéaire par morceaux : sa moyenne sur une tranche uniforme est exacte,
 * morceau par morceau. Sans forme donnée — un et un —, le pivot et la sortie
 * sont au plancher : c'est le manque moyen de la garantie différentielle, au
 * bit près. Portage de ``garantie._manque_moyen``, ligne pour ligne.
 */
export function manqueMoyen(borneInferieure, borneSuperieure, plancher,
                            partRetraitEntier = 1.0, tauxRetrait = 1.0) {
  const pivot = partRetraitEntier * plancher;
  const sortie = pivot + (plancher - pivot) / tauxRetrait;
  if (borneSuperieure === null || borneSuperieure === undefined) {
    // Masse ponctuelle : ou bien tout le monde est servi, ou bien personne.
    const manque = complementGarantie(
      plancher, borneInferieure, partRetraitEntier, tauxRetrait);
    return manque > 0 ? [1, manque] : [0, 0];
  }
  if (borneSuperieure <= pivot) {
    return [1, plancher - (borneInferieure + borneSuperieure) / 2];
  }
  if (borneInferieure >= sortie) {
    return [0, 0];
  }
  const largeur = borneSuperieure - borneInferieure;
  const concernee = (Math.min(borneSuperieure, sortie) - borneInferieure) / largeur;
  let manque = 0;
  if (borneInferieure < pivot) {
    // Sous le pivot, le complément décroît d'un euro par euro, de
    // ``plancher - borneInferieure`` à ``plancher - pivot`` : sa moyenne est ce
    // dernier, plus la moitié de ce morceau.
    manque += (pivot - borneInferieure) / largeur * (
      (plancher - pivot) + (pivot - borneInferieure) / 2);
  }
  const debut = Math.max(borneInferieure, pivot);
  const fin = Math.min(borneSuperieure, sortie);
  if (fin > debut) {
    // Dans la pente, il décroît linéairement : la moyenne de ses deux bouts.
    manque += (fin - debut) / largeur * (
      complementGarantie(plancher, debut, partRetraitEntier, tauxRetrait)
      + complementGarantie(plancher, fin, partRetraitEntier, tauxRetrait)
    ) / 2;
  }
  return [concernee, manque];
}

/**
 * Applique le barème de la garantie à la distribution, et en tire la dépense.
 *
 * ``plancherMensuel`` est exprimé dans les euros de la distribution : c'est à
 * l'appelant de l'y ramener, parce que lui seul sait dans quels euros son barème
 * est écrit. `partRetraitEntier` et `tauxRetrait` sont la forme du barème
 * (`complementGarantie`), que l'appelant lit aux paramètres de la proposition ;
 * sans eux — un et un —, le plancher est différentiel.
 */
export function coutGarantie(distribution, effectifTotal, plancherMensuel,
                             facteur = 1.0, partRetraitEntier = 1.0,
                             tauxRetrait = 1.0) {
  if (facteur <= 0) {
    throw new Error("le facteur de déplacement doit être strictement positif");
  }
  if (!(partRetraitEntier >= 0 && partRetraitEntier <= 1)) {
    throw new Error("la part du plancher jusqu'où la pension est retirée en "
      + "entier est entre zéro et un");
  }
  if (!(tauxRetrait > 0 && tauxRetrait <= 1)) {
    throw new Error("le taux de retrait est une part, entre zéro exclu et un");
  }
  let partBeneficiaires = 0;
  let manqueMensuel = 0;
  for (const tranche of distribution.tranches) {
    const superieure = tranche.borneSuperieure === null
      ? null : tranche.borneSuperieure * facteur;
    const [concernee, manque] = manqueMoyen(
      tranche.borneInferieure * facteur, superieure, plancherMensuel,
      partRetraitEntier, tauxRetrait,
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

/**
 * Les deux facteurs de déplacement, sous contrainte de masse. Portage de
 * ``garantie.facteurs_par_sexe``.
 *
 * Le modèle déplace toute la distribution d'un facteur unique, lu sur la
 * grille. Le scénario 6 ne déplace pourtant pas toutes les carrières du même
 * rapport : il retire les droits non contributifs, et les femmes en
 * détiennent plus souvent. De combien, personne ne le publie, et la grille ne
 * le dira pas — un seul de ses treize cas types est une femme. L'écart n'est
 * donc pas supposé, il est PARAMÉTRÉ par le rapport `r = fF / fH`, la moyenne
 * d'ensemble restant déplacée du même facteur :
 *
 *     w·μF·fF + (1−w)·μH·fH = f·(w·μF + (1−w)·μH)
 */
export function facteursParSexe(moyenneFemmes, moyenneHommes, partFemmes,
                                facteur, rapport) {
  if (rapport <= 0) {
    throw new Error("le rapport des deux facteurs doit être strictement positif");
  }
  const ensemble = partFemmes * moyenneFemmes + (1 - partFemmes) * moyenneHommes;
  const denominateur = partFemmes * moyenneFemmes * rapport
    + (1 - partFemmes) * moyenneHommes;
  if (ensemble <= 0 || denominateur <= 0) {
    throw new Error("les pensions moyennes doivent être strictement positives");
  }
  const facteurHommes = facteur * ensemble / denominateur;
  return [rapport * facteurHommes, facteurHommes];
}

/**
 * Pension moyenne de la distribution, dans ses propres euros. Portage de
 * ``garantie.pension_moyenne`` : le milieu de chaque tranche, et la tranche
 * ouverte à sa borne inférieure, comme `coutGarantie`.
 */
export function pensionMoyenne(distribution) {
  let total = 0;
  for (const tranche of distribution.tranches) {
    const ouverte = tranche.borneSuperieure === null
      || tranche.borneSuperieure === undefined;
    total += tranche.part * (ouverte ? tranche.borneInferieure
      : 0.5 * (tranche.borneInferieure + tranche.borneSuperieure));
  }
  return total;
}

/**
 * Le barème appliqué aux deux sexes à part, chacun de son facteur. Portage de
 * ``garantie.cout_garantie_par_sexe``. À `rapport = 1`, redonne le résultat de
 * `coutGarantie` sur la colonne « ensemble », à l'arrondi de publication près.
 */
export function coutGarantieParSexe(femmes, hommes, partFemmes, effectifTotal,
                                    plancherMensuel, facteur, rapport,
                                    plancherMajore = null, partSeule = null,
                                    partRetraitEntier = 1.0, tauxRetrait = 1.0) {
  const [facteurFemmes, facteurHommes] = facteursParSexe(
    pensionMoyenne(femmes), pensionMoyenne(hommes), partFemmes, facteur, rapport,
  );
  let part = 0;
  let manqueMensuel = 0;
  let beneficiaires = 0;
  for (const [sexe, distribution, poids, facteurSexe] of [
    ["F", femmes, partFemmes, facteurFemmes],
    ["H", hommes, 1 - partFemmes, facteurHommes],
  ]) {
    // DEUX PLANCHERS : la garantie vaut 800 € par personne, plus 250 € à qui
    // vit seul. Le plancher d'un individu dépend d'un fait ; celui d'une
    // POPULATION dépend de la répartition de ce fait, que le recensement
    // mesure. Sans `partSeule`, le plancher unique vaut pour tout le monde.
    const seule = (partSeule === null || plancherMajore === null)
      ? 0 : partSeule[sexe];
    for (const [plancher, poidsPlancher] of [
      [plancherMensuel, 1 - seule],
      [plancherMajore === null ? plancherMensuel : plancherMajore, seule],
    ]) {
      if (poidsPlancher <= 0) continue;
      const chiffre = coutGarantie(distribution,
                                   effectifTotal * poids * poidsPlancher,
                                   plancher, facteurSexe,
                                   partRetraitEntier, tauxRetrait);
      part += poids * poidsPlancher * chiffre.partBeneficiaires;
      beneficiaires += chiffre.beneficiaires;
      manqueMensuel += poids * poidsPlancher * chiffre.complementMoyenMensuel
        * chiffre.partBeneficiaires;
    }
  }
  return {
    plancherMensuel,
    facteur,
    partBeneficiaires: part,
    beneficiaires,
    complementMoyenMensuel: part ? manqueMensuel / part : 0,
    coutAnnuelMeur: manqueMensuel * effectifTotal * 12 / 1e6,
  };
}
