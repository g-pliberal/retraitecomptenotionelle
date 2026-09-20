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

/**
 * L'engagement acquis à date, tel que la table le porte. Les accesseurs sont
 * ceux de `cout.EngagementAcquis` côté Python : la page ne sait pas lequel des
 * deux elle lit, et c'est ce qui garantit qu'ils ne disent pas deux choses.
 */
export class EngagementFige {
  constructor(brut) {
    this.annee = brut.annee;
    this.horizon = brut.horizon;
    this.retraites = brut.retraites;
    this.actifs = brut.actifs;
    this.horsProjection = brut.hors_projection;
    // Ce qu'Eurostat publie pour la même année : le seul point de comparaison
    // extérieur de cette grandeur.
    this.publie = brut.publie;
    this._parScenario = brut.scenarios;
    this._sensibilite = brut.sensibilite.map((p) => [p.ecart, p.part_pib]);
  }

  partPib(scenario = "actuel") {
    return this._parScenario[scenario] ?? 0.0;
  }

  sensibilite() {
    return this._sensibilite;
  }

  /** L'écart de taux qui ramènerait l'engagement à `cible`. */
  ecartPour(cible) {
    const points = this._sensibilite;
    for (let i = 0; i + 1 < points.length; i += 1) {
      const [ecartBas, valeurBas] = points[i];
      const [ecartHaut, valeurHaut] = points[i + 1];
      if (valeurHaut <= cible && cible <= valeurBas) {
        const largeur = valeurBas - valeurHaut;
        if (largeur <= 0) return ecartBas;
        return ecartBas + (ecartHaut - ecartBas) * ((valeurBas - cible) / largeur);
      }
    }
    return null;
  }
}

/** Le bilan des quatre systèmes comparés, tel que la table le porte. */
export class BilanFige {
  constructor(annees, premiereAnneeProjetee, assiette, pib = 0.0, anneePib = 0,
              engagements = null) {
    this.annees = annees;
    this.premiereAnneeProjetee = premiereAnneeProjetee;
    this.assiette = assiette;
    // Le PIB de la dernière année PUBLIÉE, en millions d'euros courants : un
    // manque de 2070 vaut une part de PIB, et le dire en euros suppose un
    // PIB. Le seul qu'on ait sans inventer une croissance est celui
    // d'aujourd'hui, et les pages qui s'en servent l'écrivent.
    this.pib = pib;
    this.anneePib = anneePib;
    this.engagements = engagements;
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
    donnees.pib, donnees.annee_pib,
    donnees.engagements ? new EngagementFige(donnees.engagements) : null,
  );
}
