/**
 * L'inventaire des avantages non contributifs : les dispositifs recensés, et les
 * familles qui les rangent. Une DONNÉE, que le paquet porte (`avantages`) et
 * que les pages Coût et Droits non cotisés lisent ; le Python la lit par
 * `avantages.Inventaire`.
 *
 * Elle vivait dans `avantages.js`, avec le calcul de ce que ces avantages
 * coûtent. Le calcul est parti le 11 octobre 2026, avec le reste du portage du
 * coût (action 150) : la table figée en porte le résultat (`agregats.js`), et
 * l'inventaire est venu ici, réduit à ce que les pages en lisent.
 */

/** L'inventaire : les dispositifs recensés, et les familles qui les rangent. */
export class Inventaire {
  constructor(familles, avantages) {
    this.familles = familles;
    this.avantages = avantages;
  }

  parFamille(code) {
    return this.avantages.filter((avantage) => avantage.famille === code);
  }

  compte(etat) {
    return this.avantages.filter((avantage) => avantage.etat_modele === etat).length;
  }

  /**
   * La famille d'une ligne de coût, pour la couleur du graphique.
   *
   * Une ligne peut porter deux dispositifs — la MDA et la bonification pour
   * enfants de la fonction publique en sont le cas — mais jamais deux
   * familles : le même trimestre gratuit reste un droit familial sous l'un et
   * l'autre texte. La première trouvée fait donc foi.
   */
  familleDeLigne(ligne) {
    const porte = this.avantages.find(
      (avantage) => avantage.ligne_cascade === ligne || avantage.code === ligne);
    return porte ? porte.famille : null;
  }
}

/** Reconstruit l'inventaire depuis la clé `avantages` du paquet. */
export function chargerAvantages(paquet) {
  const lignes = paquet.avantages;
  return new Inventaire(lignes.familles, lignes.avantages);
}
