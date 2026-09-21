/**
 * Ce que les carrières des femmes et des hommes doivent aux droits non cotisés.
 *
 * Portage de ``src/retraite_notionnelle/donnees/caracteristiques.py``. Le même
 * échantillon interrégimes qui porte la distribution porte aussi, dans un autre
 * classeur du même millésime, les caractéristiques des retraités par sexe :
 * effectifs, pension moyenne avec et sans les majorations pour enfants, part de
 * la durée validée qui n'a pas été cotisée.
 */

/** Les indicateurs de l'EIR par sexe, pour un millésime. */
export class CaracteristiquesRetraites {
  constructor(paquet) {
    const brut = paquet.caracteristiques_retraites;
    this.millesime = brut.millesime;
    this.fiabilite = brut.fiabilite;
    this._valeurs = brut.valeurs;
  }

  /** Un indicateur pour un sexe — `F`, `H` ou `ensemble`. */
  valeur(indicateur, sexe) {
    const valeur = this._valeurs[`${indicateur}|${sexe}`];
    if (valeur === undefined) {
      throw new Error(
        `indicateur inconnu pour ${this.millesime} : ${indicateur} / ${sexe}`,
      );
    }
    return valeur;
  }

  /**
   * La part des femmes parmi les retraités, LUE et non plus ajustée. Le dépôt
   * la cherchait en recomposant la colonne « ensemble » de la distribution à
   * partir de ses deux colonnes de sexe ; l'enquête publie les effectifs, et
   * les deux se répondent au dix-millième.
   */
  get partFemmes() {
    const ensemble = this.valeur("effectifs", "ensemble");
    return ensemble ? this.valeur("effectifs", "F") / ensemble : 0;
  }

  /** La part de la durée validée qui n'a pas été cotisée, en fraction. */
  partNonCotisee(sexe) {
    return this.valeur("duree_validee_non_cotisee", sexe) / 100;
  }

  /**
   * Ce que la majoration pour enfants pèse dans la pension, en fraction. Elle
   * est proportionnelle à la pension, donc pèse un peu MOINS chez les femmes,
   * dont les pensions sont plus basses : ce terme joue à l'envers de
   * l'intuition.
   */
  partMajorations(sexe) {
    const avec = this.valeur("pension_droit_direct_majorations", sexe);
    const sans = this.valeur("pension_droit_direct", sexe);
    return avec ? (avec - sans) / avec : 0;
  }

  /**
   * La part des retraités qui touchent un minimum de pension. Elle ne sert à
   * aucun calcul : l'enquête publie la part des bénéficiaires et non ce que le
   * minimum leur apporte. Elle dit dans quel sens le rapport ci-dessous se
   * trompe, et c'est à ce titre que la page la cite.
   */
  partMinimumPension(sexe) {
    return this.valeur("part_minimum_pension", sexe) / 100;
  }

  /**
   * `r = fF / fH` : de combien les femmes tombent plus que les hommes.
   *
   * Un compte notionnel ne crédite que ce qui a été cotisé : une année validée
   * sans cotisation n'y porte rien. Le capital est donc proportionnel à la part
   * cotisée de la carrière — 74,0 % chez les femmes, 89,1 % chez les hommes en
   * 2020. La majoration pour enfants corrige de moins d'un demi-point dans
   * l'autre sens.
   */
  rapportDeplacement() {
    const cotisee = {
      F: 1 - this.partNonCotisee("F"),
      H: 1 - this.partNonCotisee("H"),
    };
    const majorees = {
      F: 1 - this.partMajorations("F"),
      H: 1 - this.partMajorations("H"),
    };
    if (cotisee.H <= 0 || majorees.H <= 0) {
      throw new Error("les parts des hommes doivent être strictement positives");
    }
    return (cotisee.F / cotisee.H) * (majorees.F / majorees.H);
  }
}
