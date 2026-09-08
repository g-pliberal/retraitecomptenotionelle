/**
 * La pyramide des âges : combien de gens, à quel âge, quelle année.
 *
 * Portage de ``src/retraite_notionnelle/donnees/population.py``. C'est la pièce
 * qui manquait au dépôt pour passer d'un droit individuel à un coût collectif :
 * sans elle, il fallait supposer toutes les générations de même taille — ce que
 * le baby-boom dément d'un tiers, et ce qui interdisait toute projection.
 *
 * Une seule source de part et d'autre de la frontière : le scénario central des
 * projections de population 2026 de l'INSEE, observé jusqu'en 2023 et projeté
 * ensuite. Ce qui est projeté porte la fiabilité `estimee`, qui se propage
 * jusqu'au résultat affiché.
 */

import { Fiabilite, SerieAnnuelle } from "./serie.js";

/** Âge plancher de la série : aucune pension de droit direct avant. */
export const AGE_MINIMAL = 50;

/** Effectifs par âge et par année, observés puis projetés. */
export class Population {
  constructor(paquet) {
    const brut = paquet.population;
    this.annees = brut.annees;
    this.ages = brut.ages;
    this._effectifs = brut.effectifs;
    this._fiabilites = brut.fiabilites;
    this.actifs = SerieAnnuelle.depuisPaquet("population_active", brut.actifs);
    this.premiereAnnee = this.annees[0];
    this.derniereAnnee = this.annees[this.annees.length - 1];
    this.ageMinimal = this.ages[0];
    this.ageMaximal = this.ages[this.ages.length - 1];
    this._rangs = new Map(this.annees.map((annee, rang) => [annee, rang]));
  }

  /**
   * Année ramenée dans la plage publiée. La série commence en 1962, la dépense
   * observée en 1959 : les trois premières années empruntent la pyramide de
   * 1962 — trois années dont la dépense pèse un demi pour cent de celle
   * d'aujourd'hui.
   */
  _anneeBornee(annee) {
    return Math.min(Math.max(annee, this.premiereAnnee), this.derniereAnnee);
  }

  /** Effectif d'un âge une année donnée ; zéro hors de la plage d'âges. */
  effectif(age, annee) {
    if (age < this.ageMinimal || age > this.ageMaximal) {
      return 0.0;
    }
    const rang = this._rangs.get(this._anneeBornee(annee));
    return this._effectifs[rang][age - this.ageMinimal];
  }

  /** Effectif cumulé d'une tranche d'âges, bornes comprises. */
  effectifTranche(ageDebut, ageFin, annee) {
    let somme = 0.0;
    for (let age = ageDebut; age <= ageFin; age += 1) {
      somme += this.effectif(age, annee);
    }
    return somme;
  }

  /**
   * Fiabilité de la pyramide d'une année. Hors de la plage publiée, la valeur
   * est empruntée : elle ne peut donc pas valoir mieux qu'`estimee`.
   */
  fiabilite(annee) {
    if (annee < this.premiereAnnee || annee > this.derniereAnnee) {
      return Fiabilite.ESTIMEE;
    }
    return this._fiabilites[this._rangs.get(annee)];
  }
}
