/**
 * Ce que chaque ministère verse au compte « Pensions », en part de ses crédits.
 *
 * Le jaune pensions annexé au PLF 2027 décompose, à sa figure 3B, les crédits
 * de dix-sept ministères, sans en imprimer une valeur : le dépôt les lit sur
 * les tracés de ses barres, et les certifie (``credits_ministeres.csv``). Sans
 * jumeau depuis l'action 161 (note de décision 0005) : le chargeur
 * ``src/retraite_notionnelle/donnees/credits_ministeres.py`` n'en écrit que
 * les parts au paquet, et la contribution employeur, ce qui va au compte
 * « Pensions » et l'ordre des ministères ne se calculent qu'ici.
 */

/** Les parts que la contribution employeur réunit : sur les dépenses de
 * personnel (T2 CAS) et, pour les opérateurs de l'Enseignement supérieur, sur
 * leurs crédits de fonctionnement (T3 CAS). */
const CONTRIBUTION = ["t2_cas", "t3_cas"];

/** Les parts des crédits de chaque ministère, en fraction, pour une année. */
export class CreditsMinisteres {
  constructor(paquet) {
    const brut = paquet.credits_ministeres;
    this.annee = brut.annee;
    this.fiabilite = brut.fiabilite;
    this._parts = brut.parts;
    const codes = [...new Set(Object.keys(brut.parts).map((cle) => cle.split("|")[0]))];
    /** Les ministères, du plus au moins versé au compte « Pensions ». */
    this.ministeres = codes.sort((a, b) => this.auComptePensions(b)
      - this.auComptePensions(a) || (a < b ? -1 : 1));
  }

  /**
   * Une part des crédits d'un ministère ; zéro pour une part que sa barre ne
   * trace pas — le T3 CAS, hors de l'Enseignement supérieur.
   */
  part(ministere, part) {
    if (!Object.keys(this._parts).some((cle) => cle.startsWith(`${ministere}|`))) {
      throw new Error(`ministère absent de la figure 3B : ${ministere}`);
    }
    return this._parts[`${ministere}|${part}`] ?? 0;
  }

  /** La contribution employeur que le ministère verse au compte. */
  contribution(ministere) {
    return CONTRIBUTION.reduce((somme, part) => somme + this.part(ministere, part), 0);
  }

  /** Ce qui va au compte « Pensions » : la contribution, et la retenue des
   * fonctionnaires. */
  auComptePensions(ministere) {
    return this.contribution(ministere) + this.part(ministere, "cotisations_salariales");
  }
}
