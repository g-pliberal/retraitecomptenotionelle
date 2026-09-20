/**
 * Combien de retraités touchent combien : la distribution des pensions.
 *
 * Portage de ``src/retraite_notionnelle/donnees/distribution.py``. Une grille de
 * douze cas types suffit à comparer des systèmes — un rapport de masses est
 * robuste — mais pas à chiffrer un PLANCHER : une allocation différentielle ne
 * coûte que ce que coûte la queue basse de la distribution, et douze carrières
 * ne la décrivent pas.
 *
 * La source est l'échantillon interrégimes de retraités de la DREES, qui apparie
 * tous les quatre ans les fichiers de toutes les caisses sur un même échantillon
 * d'individus.
 */

/** Répartition des pensions brutes de droit direct, pour un millésime d'EIR. */
export class DistributionPensions {
  constructor(paquet, sexe = "ensemble") {
    // Femmes et hommes à part, pour peser les sexes parmi les bénéficiaires
    // de la garantie ; l'ensemble, sinon.
    const brut = sexe === "ensemble" ? paquet.distribution_pensions
      : paquet.distribution_pensions_sexes[sexe];
    this.millesime = brut.millesime;
    this.sexe = sexe;
    this.fiabilite = brut.fiabilite;
    this.tranches = brut.parts.map((part, rang) => ({
      borneInferieure: brut.bornes_inferieures[rang],
      // ``null`` pour la dernière, que l'enquête laisse ouverte.
      borneSuperieure: brut.bornes_superieures[rang],
      part,
    }));
  }

  /**
   * Doit valoir un, aux arrondis de publication près. La DREES publie ses parts
   * arrondies au centième de point : leur somme vaut 100,01 % et non 100 %.
   * L'écart est réel et ne se corrige pas — redresser les parts inventerait une
   * précision que la source ne donne pas.
   */
  /**
   * La part des retraités dont la pension est inférieure à un montant, en euros
   * du millésime : le rang d'une pension parmi les retraités. Portage de
   * `part_sous` — linéaire dans la tranche, le seuil de la dernière au-delà.
   */
  partSous(montantMensuel) {
    let cumul = 0.0;
    for (const tranche of this.tranches) {
      if (montantMensuel < tranche.borneInferieure) {
        return cumul;
      }
      const ouverte = tranche.borneSuperieure === null || tranche.borneSuperieure === undefined;
      if (ouverte || montantMensuel < tranche.borneSuperieure) {
        if (ouverte) {
          return cumul;
        }
        const largeur = tranche.borneSuperieure - tranche.borneInferieure;
        return cumul + tranche.part * (montantMensuel - tranche.borneInferieure) / largeur;
      }
      cumul += tranche.part;
    }
    return cumul;
  }

  get sommeDesParts() {
    return this.tranches.reduce((somme, tranche) => somme + tranche.part, 0);
  }
}
