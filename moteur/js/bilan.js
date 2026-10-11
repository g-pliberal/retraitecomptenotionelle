/**
 * Le bilan des quatre systèmes, figé sous les réglages de référence.
 * Portage de `src/retraite_notionnelle/donnees/bilan.py`.
 *
 * POURQUOI CE FICHIER EXISTE. Le coefficient d'équilibre d'un système est un
 * rapport de MASSES : ce que le système encaisse une année, sur ce qu'il verse
 * cette année-là. Le calculer suppose la grille des cas types simulée sous
 * chaque système, pondérée par les effectifs, année par année jusqu'en 2070 —
 * dix-huit secondes de calcul, que le Python fait une fois, pour le paquet.
 *
 * La page des résultats du simulateur ne peut pas le payer : elle est la page
 * d'entrée du site, elle se recalcule à chaque changement de champ, et elle
 * tourne dans le navigateur du lecteur. Or elle a besoin du même coefficient —
 * c'est lui qui dit ce que les comptes financent de la pension qu'elle
 * affiche. D'où cette table, calculée une fois par
 * `scripts/construire_donnees.py` et lue ici telle quelle.
 *
 * « Pourquoi changer » et « Partager » la lisent aussi, depuis le 7 octobre
 * 2026 : elles ne prennent aucun réglage, et refaisaient le coût entier — cinq
 * secondes — pour y lire la dépense, la recette et le solde de quelques années.
 * La table porte donc la dépense et le PIB de chaque année, et les trois
 * carrières d'exemple de « Pourquoi changer » (`ExempleFige`). Carrières types
 * y lit le coefficient de chaque système depuis le 11 octobre ; la page Coût
 * lit le coût entier dans une table voisine (`agregats.js`).
 *
 * CE QUE LE FIGEAGE COÛTE. La table est calculée sous les réglages de
 * RÉFÉRENCE. Le coefficient du système actuel n'en dépend pas : il est le
 * rapport des ressources aux dépenses que le COR publie, et aucun réglage du
 * simulateur ne le déplace. Les trois autres, si — leur dépense est une masse
 * de pensions notionnelles, qui bouge avec la règle d'indexation ou la table
 * de mortalité. La page le dit en toutes lettres.
 *
 * STRUCTURELLEMENT IDENTIQUE AU `Solde` DU PYTHON : mêmes accesseurs, mêmes
 * unités — la part de PIB partout. C'est ce qui garantit que la table figée et
 * le calcul complet ne peuvent pas dire deux choses.
 */

/** Une année du bilan figé, dans l'unité du COR : la part de PIB. */
class AnneeBilan {
  constructor(annee, projete, partContributive, coefficients, soldes, ressources,
              depenses = {}, pib = 0.0) {
    this.annee = annee;
    this.projete = projete;
    this.partContributive = partContributive;
    this._coefficients = coefficients;
    this._soldes = soldes;
    this._ressources = ressources;
    this._depenses = depenses;
    // Le PIB de l'année, en millions d'euros courants, s'il est publié ; zéro
    // sinon, comme dans le solde du coût.
    this.pib = pib;
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

  /** Ce que le système actuel encaisse : la recette que le COR publie. */
  get ressources() {
    return this.ressourcesDe("actuel");
  }

  depense(scenario) {
    const valeur = this._depenses[scenario];
    return valeur === undefined ? 0.0 : valeur;
  }

  soldeMeur(scenario) {
    return this.solde(scenario) * this.pib;
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

/**
 * Les écarts médians de la grille des cas types, tels que la table les porte.
 *
 * L'accueil dit de combien la proposition baisse les retraites, et il ne
 * simule rien : il lit ces trois médianes, que `castypes.ecarts_medians` tire
 * de la grille entière côté Python — des secondes de calcul que la première
 * page ouverte ne peut pas faire attendre. Les champs sont ceux de
 * `castypes.EcartsMedians`.
 */
export class EcartsFiges {
  constructor(brut) {
    this.aVenir = brut.a_venir;
    this.aVenirVolontaire = brut.a_venir_volontaire;
    this.dejaLiquidees = brut.deja_liquidees;
    this.casesAVenir = brut.cases_a_venir;
    this.casesDejaLiquidees = brut.cases_deja_liquidees;
  }
}

/**
 * Une carrière d'exemple de « Pourquoi changer », simulée une fois.
 *
 * `saisie` est la saisie simulée, champ par champ : la page ne lit l'exemple
 * que si elle demande exactement celle-là. Elle simulait sinon, jusqu'au
 * 11 octobre 2026 ; un paquet qui ne la porte pas est désormais à refaire, et
 * la page le dit en levant une erreur. `pensionFinancee`
 * est la pension du système 3 — le scénario `notionnel_retroactif_employeur` —,
 * ce que les cotisations de l'assuré financeraient au rendement d'équilibre.
 * Les champs sont ceux d'`ExempleFige` côté Python.
 */
export class ExempleFige {
  constructor(saisie, fiche, coefficientEurosConstants, pensionActuel, pensionFinancee) {
    this.saisie = saisie;
    // La fiche de paie, réduite à ce que la page en lit.
    this.fiche = fiche;
    this.coefficientEurosConstants = coefficientEurosConstants;
    this.pensionActuel = pensionActuel;
    this.pensionFinancee = pensionFinancee;
  }
}

/**
 * Ce que les comptes financent d'une pension promise, sur la durée du service.
 * Portage de `cout.PensionFinancee`, venu ici de `cout.js` quand le portage du
 * coût est parti (11 octobre 2026) : le simulateur la lit sur ce bilan.
 *
 * Le site affiche quatre pensions calculées sur une même carrière, et la
 * première — le droit en vigueur — se lit comme une promesse tenue. Elle ne
 * l'est pas : le système qui la sert est en déficit, et le COR projette ce
 * déficit jusqu'en 2070. Le coefficient d'équilibre dit de combien ; celui de
 * la seule année du départ flatte qui part tôt, puisqu'il ignore les années où
 * le déficit se creuse, et le coefficient retenu est donc la moyenne des
 * coefficients annuels PONDÉRÉE PAR LA SURVIE.
 *
 * Ce n'est pas une prévision : rogner toutes les pensions d'un même facteur est
 * UNE façon d'équilibrer une année, et les deux autres — lever davantage de
 * cotisations, emprunter — sont chiffrées à côté.
 */
export class PensionFinancee {
  constructor(donnees) {
    Object.assign(this, donnees);
  }

  /** De combien il faudrait rogner, en part de la pension. Négatif : une marge. */
  get manque() {
    return 1.0 - this.coefficient;
  }

  /** Les comptes couvrent-ils l'année du départ elle-même ? */
  get departCouvert() {
    return this.premiereAnnee === this.anneeLiquidation;
  }

  /** La fenêtre couvre-t-elle toute la durée de service de la pension ? */
  get entiere() {
    return this.partCouverte >= 0.999;
  }

  /**
   * Le montant que les comptes financent, la capitalisation mise à part : une
   * rente capitalisée sort d'un placement déjà constitué, qu'aucun déficit de
   * la répartition n'atteint.
   */
  servie(montant, horsRepartition = 0.0) {
    return (montant - horsRepartition) * this.coefficient + horsRepartition;
  }
}

/**
 * Ce que les comptes financent de la pension du scénario, à cette date.
 * Portage de `cout.financer`.
 *
 * `poids` porte, rang par rang à compter de l'année de liquidation, la part des
 * partants encore en vie pendant l'année. `solde` est le bilan figé du paquet,
 * ou tout objet qui en porte les accesseurs — le `Solde` du Python les porte.
 *
 * Rend `null` quand aucune année du service n'est couverte par les comptes du
 * COR : un départ de 1980 n'a rien à lire dans un bilan qui commence en 2002.
 */
export function financer(solde, assiette, scenario, anneeLiquidation, poids) {
  if (!solde || !solde.annees.length) return null;
  const debut = Math.max(anneeLiquidation, solde.premiereAnnee);
  let numerateur = 0.0;
  let couvert = 0.0;
  let total = 0.0;
  for (let rang = 0; rang < poids.length; rang += 1) {
    const part = poids[rang];
    if (part <= 0) continue;
    const annee = anneeLiquidation + rang;
    total += part;
    const ligne = solde.annee(annee);
    if (annee < debut || ligne === null) continue;
    numerateur += part * ligne.coefficient(scenario);
    couvert += part;
  }
  if (couvert <= 0 || total <= 0) return null;
  const ligneDepart = solde.annee(debut);
  if (ligneDepart === null) return null;
  const manque = -ligneDepart.solde(scenario);
  const anneeAssiette = assiette ? assiette.derniereAnnee : 0;
  const partAssiette = assiette ? assiette.partPib(anneeAssiette) : 0.0;
  const cotisees = ligneDepart.ressourcesDe(scenario) * ligneDepart.partContributive;
  return new PensionFinancee({
    scenario,
    anneeLiquidation,
    premiereAnnee: debut,
    derniereAnnee: Math.min(anneeLiquidation + poids.length - 1, solde.derniereAnnee),
    coefficientDepart: ligneDepart.coefficient(scenario),
    coefficient: numerateur / couvert,
    partCouverte: couvert / total,
    manquePib: manque,
    pointsAssiette: partAssiette > 0 ? manque / partAssiette : 0.0,
    hausseCotisations: cotisees > 0 ? manque / cotisees : 0.0,
    anneeAssiette,
  });
}

/** Deux saisies écrites comme des objets : les mêmes champs, les mêmes valeurs. */
function memesChamps(une, autre) {
  const cles = Object.keys(une);
  return cles.length === Object.keys(autre).length
    && cles.every((cle) => une[cle] === autre[cle]);
}

/** Le bilan des quatre systèmes comparés, tel que la table le porte. */
export class BilanFige {
  constructor(annees, premiereAnneeProjetee, assiette, pib = 0.0, anneePib = 0,
              engagements = null, ecarts = null, exemples = []) {
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
    // Les écarts médians de la proposition au système actuel, sur la grille.
    this.ecarts = ecarts;
    // Les carrières d'exemple de « Pourquoi changer ».
    this.exemples = exemples;
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

  /** L'exemple de cette saisie exactement, ou rien. */
  exemple(saisie) {
    return this.exemples.find((exemple) => memesChamps(exemple.saisie, saisie)) ?? null;
  }
}

/** Reconstruit le bilan depuis la clé `bilan_equilibre` du paquet. */
export function chargerBilan(donnees) {
  return new BilanFige(
    donnees.annees.map((ligne) => new AnneeBilan(
      ligne.annee, ligne.projete, ligne.part_contributive,
      ligne.coefficients, ligne.soldes, ligne.ressources, ligne.depenses, ligne.pib,
    )),
    donnees.premiere_annee_projetee,
    new AssietteFigee(donnees.annee_assiette, donnees.part_pib_assiette),
    donnees.pib, donnees.annee_pib,
    donnees.engagements ? new EngagementFige(donnees.engagements) : null,
    donnees.ecarts_medians ? new EcartsFiges(donnees.ecarts_medians) : null,
    donnees.exemples_risque.map((brut) => new ExempleFige(
      brut.saisie,
      {
        annee: brut.fiche.annee, brut: brut.fiche.brut, net: brut.fiche.net,
        retraiteTotale: brut.fiche.retraite_totale,
        retraiteEmployeur: brut.fiche.retraite_employeur,
      },
      brut.coefficient_euros_constants, brut.pension_actuel, brut.pension_financee,
    )),
  );
}
