/**
 * Qui vit en couple après 65 ans, âge par âge et par sexe.
 *
 * Copie de `donnees/vie_en_couple.py`, qui dit d'où viennent les parts et ce
 * que la convention fige.
 */

export class VieEnCouple {
  constructor(paquet) {
    const brut = paquet.vie_en_couple;
    this.annee = brut.annee;
    this.fiabilite = brut.fiabilite;
    this.ageMinimal = brut.age_minimal;
    this.ageMaximal = brut.age_maximal;
    this._parts = brut.parts;
  }

  /** La part publiée pour cet âge, ce sexe et ce mode de résidence. */
  part(age, sexe, mode = "couple") {
    const rang = Math.trunc(Math.min(Math.max(age, this.ageMinimal), this.ageMaximal));
    const valeur = this._parts[`${rang}|${sexe}|${mode}`];
    return valeur === undefined ? 0.0 : valeur;
  }

  /** La part moyenne sur une courbe d'exposition, à partir de `ageDebut`. */
  partMoyenne(sexe, exposition, ageDebut = 65, mode = "couple") {
    let total = 0.0;
    for (const poids of exposition) total += poids;
    if (total <= 0.0) return 0.0;
    let somme = 0.0;
    exposition.forEach((poids, rang) => {
      somme += poids * this.part(ageDebut + rang, sexe, mode);
    });
    return somme / total;
  }
}
