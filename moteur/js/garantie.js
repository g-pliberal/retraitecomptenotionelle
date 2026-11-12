/**
 * Ce que coûte la garantie vieillesse, chiffrée sur la distribution des pensions.
 *
 * UN SEUL EXEMPLAIRE (note de décision 0007, action 161). Seul le barème
 * d'une personne, `complementGarantie`, reste le
 * jumeau de ``src/retraite_notionnelle/garantie.py``, qui ne garde plus que
 * lui, tant que le moteur Python d'une carrière reste. Les fonctions de coût,
 * elles, ne s'écrivent qu'ici : les pages les lisent, et le coût du modèle
 * les demande au pont, par lot (`pont.garantie`, `GarantieDistribution` de
 * ``cout.py``). Sans forme donnée, elles rendent le barème différentiel, celui
 * de l'ASPA.
 *
 * La garantie du scénario 6 est une allocation SOUS CONDITION DE RESSOURCES :
 * elle porte la pension à un plancher — 800 € par mois, plus 250 €
 * d'allocation d'isolement pour qui vit seul —, et, depuis le 9 novembre 2026
 * (décisions 100 à 102 du programme), elle est DÉGRESSIVE (`complementGarantie`,
 * que le moteur d'une carrière applique). Son coût est entièrement celui de la
 * queue basse de la distribution des pensions, et c'est précisément ce qu'une
 * grille de treize cas types ne sait pas décrire. Ce module applique le barème
 * à la distribution publiée par la DREES. Il ne simule rien : il additionne,
 * tranche par tranche, ce qui manque à chacune.
 *
 * TROIS CONVENTIONS, ET CE QU'ELLES VALENT
 * 1. **Uniformité dans la tranche.** Les pensions d'une tranche de cent euros
 *    sont supposées réparties uniformément entre ses bornes. L'erreur est
 *    bornée par la largeur de la tranche et joue dans les deux sens d'une
 *    tranche à l'autre.
 * 2. **La tranche ouverte est une masse ponctuelle** à sa borne inférieure.
 *    Au-dessus du plancher — le cas ordinaire — elle ne coûte rien de toute
 *    façon.
 * 3. **La situation de foyer n'est pas connue.** L'enquête dit la pension, pas
 *    avec qui l'on vit. On ne choisit donc pas : les deux planchers sont
 *    calculés et affichés, celui de qui vit à deux et celui de qui vit seul.
 *    Le coût réel est entre les deux, et la source qui dirait où ne serait
 *    pas celle-ci.
 *
 * CE QUE LE FACTEUR FAIT, ET CE QU'IL NE FAIT PAS
 * À ``facteur = 1``, le barème est appliqué aux pensions TELLES QU'ELLES SONT :
 * c'est ce que la garantie coûterait aujourd'hui, en remplacement de l'ASPA, et
 * ce chiffre ne doit rien au modèle. Un facteur inférieur à un déplace toute la
 * distribution dans le même rapport, pour dire ce que la garantie coûterait une
 * fois les pensions devenues celles du scénario 6. Cette translation est
 * proportionnelle et uniforme, alors que le scénario 6 ne déplace pas toutes les
 * carrières du même rapport : le second chiffre est un ORDRE DE GRANDEUR là où
 * le premier est un calcul.
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
 * pour obtenir la dépense. Celui d'un bénéficiaire s'en déduit en divisant par
 * la part concernée, et `coutGarantie` le fait une fois pour toutes. Le barème
 * est celui de `complementGarantie`, linéaire par morceaux : il rend ce qui
 * manque jusqu'au pivot, puis décroît de ``tauxRetrait`` jusqu'à la sortie, où
 * il s'éteint ; sa moyenne sur une tranche uniforme est donc exacte, morceau
 * par morceau. Sans forme donnée — un et un —, le pivot et la sortie sont au
 * plancher : c'est le manque moyen de la garantie différentielle, au bit près
 * de ce que le module rendait avant le 9 novembre 2026.
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
    // Sans borne supérieure, `null` ou absente, la tranche est ouverte, comme
    // pour `manqueMoyen` et `pensionMoyenne`.
    const ouverte = tranche.borneSuperieure === null
      || tranche.borneSuperieure === undefined;
    const superieure = ouverte ? null : tranche.borneSuperieure * facteur;
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
 * Les deux facteurs de déplacement, sous contrainte de masse.
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
 *
 * La contrainte est ce qui fait de l'exercice une RÉPARTITION et non une
 * hypothèse de plus : la grille garde le dernier mot sur l'agrégat, et il ne
 * reste à décider que le partage entre les deux sexes. À `rapport = 1`, les
 * deux facteurs valent `facteur` et l'on retrouve la convention uniforme.
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
 * Pension moyenne de la distribution, dans ses propres euros.
 *
 * Même convention que `coutGarantie` : le milieu de chaque tranche, et la
 * tranche ouverte à sa borne inférieure. Les deux moyennes en sont
 * sous-estimées, celle des hommes un peu plus — ils sont plus nombreux dans
 * la tranche ouverte —, mais seul leur RAPPORT entre dans la contrainte de
 * `facteursParSexe`, et repousser la tranche ouverte de 4 500 à 6 500 € le
 * déplace de 0,641 à 0,624.
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
 * Le barème appliqué aux deux sexes à part, chacun de son facteur.
 *
 * `rapport` vaut un pour la convention uniforme, et le résultat redonne alors
 * celui de `coutGarantie` sur la colonne « ensemble » — à l'arrondi de
 * publication près, la source arrondissant ses parts au centième de point. En
 * deçà de un, les pensions des femmes tombent davantage, ce qui fait passer
 * plus de monde sous le plancher : le coût de la convention uniforme est une
 * borne basse, et c'est ce que cette fonction chiffre.
 *
 * DEUX PLANCHERS, ET C'EST UNE POPULATION QU'ON CHIFFRE. La garantie vaut
 * 800 € par personne, plus 250 € à qui vit seul : le plancher d'un individu
 * dépend d'un fait, sa situation de foyer, et celui d'une POPULATION dépend
 * donc de la répartition de ce fait. `plancherMajore` et `partSeule` portent
 * cette répartition, sexe par sexe — les femmes vivent hors couple bien plus
 * souvent, et elles sont aussi bien plus souvent sous le plancher, si bien que
 * les deux se composent et qu'un partage global les manquerait. Sans eux, le
 * plancher unique s'applique à tout le monde : c'est la convention d'avant le
 * 21 septembre 2026, qui servait le plancher majoré à la population entière
 * et surestimait le coût de près d'un quart.
 *
 * LA FORME EST LA MÊME AUX DEUX PLANCHERS (décision 102 du programme) :
 * `partRetraitEntier` et `tauxRetrait` s'appliquent à chacun en entier,
 * isolement compris, comme dans `coutGarantie`.
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
    // Sans `partSeule`, le plancher unique vaut pour tout le monde.
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
    // Le facteur rendu est celui de la contrainte, commun aux deux sexes par
    // construction : c'est lui qui a été tenu, pas ceux qu'il répartit.
    facteur,
    partBeneficiaires: part,
    beneficiaires,
    complementMoyenMensuel: part ? manqueMensuel / part : 0,
    coutAnnuelMeur: manqueMensuel * effectifTotal * 12 / 1e6,
  };
}
