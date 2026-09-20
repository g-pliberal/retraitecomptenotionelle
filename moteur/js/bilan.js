/**
 * Le bilan des quatre systèmes, figé sous les réglages de référence.
 * Portage de `src/retraite_notionnelle/donnees/bilan.py`.
 *
 * POURQUOI CE FICHIER EXISTE. Le coefficient d'équilibre d'un système est un
 * rapport de MASSES : ce que le système encaisse une année, sur ce qu'il verse
 * cette année-là. Le calculer suppose la grille des cas types simulée sous
 * chaque système, pondérée par les effectifs, année par année jusqu'en 2070 —
 * dix-huit secondes de calcul. C'est le prix de la page Coût, et elle le paie
 * une fois.
 *
 * La page des résultats du simulateur ne peut pas le payer : elle est la page
 * d'entrée du site, elle se recalcule à chaque changement de champ, et elle
 * tourne dans le navigateur du lecteur. Or elle a besoin du même coefficient —
 * c'est lui qui dit ce que les comptes financent de la pension qu'elle
 * affiche. D'où cette table, calculée une fois par
 * `scripts/construire_donnees.py` et lue ici telle quelle.
 *
 * CE QUE LE FIGEAGE COÛTE. La table est calculée sous les réglages de
 * RÉFÉRENCE. Le coefficient du système actuel n'en dépend pas : il est le
 * rapport des ressources aux dépenses que le COR publie, et aucun réglage du
 * simulateur ne le déplace. Les trois autres, si — leur dépense est une masse
 * de pensions notionnelles, qui bouge avec la règle d'indexation ou la table
 * de mortalité. La page le dit en toutes lettres.
 *
 * STRUCTURELLEMENT IDENTIQUE À `Solde` : mêmes accesseurs, mêmes unités — la
 * part de PIB partout. C'est ce qui garantit que la table figée et le calcul
 * complet ne peuvent pas dire deux choses.
 */

/** Une année du bilan figé, dans l'unité du COR : la part de PIB. */
class AnneeBilan {
  constructor(annee, projete, partContributive, coefficients, soldes, ressources) {
    this.annee = annee;
    this.projete = projete;
    this.partContributive = partContributive;
    this._coefficients = coefficients;
    this._soldes = soldes;
    this._ressources = ressources;
  }

  coefficient(scenario) {
    const valeur = this._coefficients[scenario];
    return valeur === undefined ? 0.0 : valeur;
  }

  solde(scenario) {
    const valeur = this._soldes[scenario];
    return valeur === undefined ? 0.0 : valeur;
  }

  ressourcesDe(scenario) {
    const valeur = this._ressources[scenario];
    return valeur === undefined ? 0.0 : valeur;
  }
}

/** L'assiette des revenus d'activité, réduite à ce que `financer` en lit. */
class AssietteFigee {
  constructor(derniereAnnee, partPibAssiette) {
    this.derniereAnnee = derniereAnnee;
    this._partPib = partPibAssiette;
  }

  partPib() {
    return this._partPib;
  }
}

/** Le bilan des quatre systèmes comparés, tel que la table le porte. */
export class BilanFige {
  constructor(annees, premiereAnneeProjetee, assiette) {
    this.annees = annees;
    this.premiereAnneeProjetee = premiereAnneeProjetee;
    this.assiette = assiette;
    this.premiereAnnee = annees.length ? annees[0].annee : 0;
    this.derniereAnnee = annees.length ? annees[annees.length - 1].annee : 0;
    this.derniereAnneeObservee = premiereAnneeProjetee - 1;
  }

  annee(millesime) {
    for (const ligne of this.annees) {
      if (ligne.annee === millesime) return ligne;
    }
    return null;
  }
}

/** Reconstruit le bilan depuis la clé `bilan_equilibre` du paquet. */
export function chargerBilan(donnees) {
  return new BilanFige(
    donnees.annees.map((ligne) => new AnneeBilan(
      ligne.annee, ligne.projete, ligne.part_contributive,
      ligne.coefficients, ligne.soldes, ligne.ressources,
    )),
    donnees.premiere_annee_projetee,
    new AssietteFigee(donnees.annee_assiette, donnees.part_pib_assiette),
  );
}
