/**
 * L'indemnité compensatrice de la hausse de la CSG des agents publics, depuis
 * 2018 (`legislation/indemnite_compensatrice_csg.yaml`) : le décret
 * n° 2017-1889, son article 2, qui la fixe, et son article 5, qui la
 * réévalue. Ce module ne connaît que des rémunérations ; ce qu'en fait la
 * fiche de paie est dans `remuneration.js`.
 *
 * Jumeau de `src/retraite_notionnelle/donnees/indemnite_csg.py`, qui fait foi.
 */

/** Une réévaluation de l'article 5 : voir le Python. */
class Reevaluation {
  constructor({ annee, chaqueAnnee, sens, seulementRemuneresFin2017 = false }) {
    this.annee = annee;
    this.chaqueAnnee = chaqueAnnee;
    this.sens = sens;
    this.seulementRemuneresFin2017 = seulementRemuneresFin2017;
  }

  vaut(annee) {
    return this.chaqueAnnee ? annee >= this.annee : annee === this.annee;
  }
}

/** Les paramètres du décret, et le montant qu'ils donnent. */
export class IndemniteCompensatrice {
  constructor(paquet) {
    const brut = paquet.indemnite_compensatrice_csg ?? null;
    if (brut === null) {
      this.debut = 2018;
      this.familles = new Set();
      this.profils = new Set();
      this.anneeDeReference = 2017;
      this.tauxHausseCsg = 0.0;
      this.coefficient = 1.0;
      this.tauxCes = 0.0;
      this.plafondCesEnPss = 0.0;
      this.seuilCesAnnuel = 0.0;
      this.tauxRecrutes = 0.0;
      this.reevaluations = [];
      return;
    }
    this.debut = brut.debut;
    this.familles = new Set(brut.familles);
    this.profils = new Set(brut.profils);
    this.anneeDeReference = brut.annee_de_reference;
    this.tauxHausseCsg = brut.taux_hausse_csg;
    this.coefficient = brut.coefficient;
    this.tauxCes = brut.taux_ces;
    this.plafondCesEnPss = brut.plafond_ces_en_pss;
    this.seuilCesAnnuel = brut.seuil_ces_annuel;
    this.tauxRecrutes = brut.taux_recrutes;
    this.reevaluations = brut.reevaluations.map((r) => new Reevaluation({
      annee: r.annee, chaqueAnnee: r.chaque_annee, sens: r.sens,
      seulementRemuneresFin2017: r.seulement_remuneres_fin_2017,
    }));
  }

  /** La CES de l'année de référence : voir le Python. */
  contributionDeSolidarite(remuneration, cotisations, traitementNet, plafondAnnuel) {
    if (traitementNet < this.seuilCesAnnuel) {
      return 0.0;
    }
    const nette = Math.max(0.0, remuneration - cotisations);
    return this.tauxCes * Math.min(nette, this.plafondCesEnPss * plafondAnnuel);
  }

  /** Le montant annuel du I de l'article 2. */
  initiale(remunerationReference, deduits) {
    return Math.max(0.0, this.tauxHausseCsg * remunerationReference - deduits)
      * this.coefficient;
  }

  /**
   * L'indemnité annuelle de chaque année où l'agent est payé, depuis 2018 :
   * `remunerations`, une `Map` de l'année à la rémunération annualisée de
   * l'agent public bénéficiaire ; `deduitsReference`, ce que le I déduit de
   * celle de 2017. Voir le Python.
   */
  montants(remunerations, deduitsReference = 0.0) {
    const reference = this.anneeDeReference;
    const annees = [...remunerations.keys()]
      .filter((a) => a >= this.debut && remunerations.get(a) > 0.0)
      .sort((a, b) => a - b);
    const resultat = new Map();
    if (!annees.length) {
      return resultat;
    }
    const fin2017 = (remunerations.get(reference) ?? 0.0) > 0.0;
    let montant;
    let depuis;
    if (fin2017) {
      montant = this.initiale(remunerations.get(reference), deduitsReference);
      depuis = this.debut;
    } else {
      depuis = annees[0];
      montant = this.tauxRecrutes * remunerations.get(depuis);
    }
    for (let annee = depuis; annee <= annees[annees.length - 1]; annee += 1) {
      if (annee > depuis) {
        montant *= this.rapport(remunerations, annee, fin2017);
      }
      if ((remunerations.get(annee) ?? 0.0) > 0.0) {
        resultat.set(annee, montant);
      }
    }
    return resultat;
  }

  /** Ce par quoi la réévaluation du 1er janvier de `annee` multiplie l'indemnité. */
  rapport(remunerations, annee, fin2017) {
    const regle = this.reevaluations.find((r) => r.vaut(annee)) ?? null;
    if (regle === null || (regle.seulementRemuneresFin2017 && !fin2017)) {
      return 1.0;
    }
    const ecoulee = remunerations.get(annee - 1) ?? 0.0;
    const precedente = remunerations.get(annee - 2) ?? 0.0;
    if (ecoulee <= 0.0 || precedente <= 0.0) {
      return 1.0;
    }
    const rapport = ecoulee / precedente;
    if (regle.sens === "hausse" && rapport <= 1.0) {
      return 1.0;
    }
    return rapport;
  }
}

const INDEMNITES_PAR_PAQUET = new WeakMap();

/** La table du décret, une fois par paquet. */
export function indemniteCsg(paquet) {
  let table = INDEMNITES_PAR_PAQUET.get(paquet);
  if (table === undefined) {
    table = new IndemniteCompensatrice(paquet);
    INDEMNITES_PAR_PAQUET.set(paquet, table);
  }
  return table;
}
