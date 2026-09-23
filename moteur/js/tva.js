/**
 * Ce que rapporte une TVA à taux unique : l'assiette de la TVA, taux par taux.
 *
 * Portage de ``src/retraite_notionnelle/donnees/tva.py``.
 *
 * Le Parti libéral affecte au scénario 6, depuis le 23 septembre 2026, une TVA
 * à TAUX UNIQUE : les quatre taux d'aujourd'hui cèdent la place à un seul, et
 * ce qu'il rapporte de plus va à la retraite. Les assiettes viennent du modèle
 * de la TVA théorique de la DG Trésor (Trésor-Éco n° 371, septembre 2025), qui
 * publie ce que rapporterait en 2025 un point de plus sur chaque taux : un
 * point étant un centième, l'assiette en est le centuple. Le point NET retire
 * la TVA que les administrations paient sur leurs propres achats ; c'est lui
 * que le dépôt emploie.
 *
 * Deux nombres en découlent : le TAUX MOYEN d'aujourd'hui sur l'assiette nette,
 * qui est aussi le taux unique à recette constante (15,46 %), et la PART DE PIB
 * de cette assiette (38,4 % en 2025), tenue à ce niveau ensuite. Ce qu'un taux
 * unique `t` rapporte de plus est `(t − taux moyen) × part de PIB`. Chiffrage
 * STATIQUE : ni effet de volume, ni asymétrie de répercussion, ni effet de prix
 * sur les dépenses indexées — le module Python dit lesquels.
 */

import { Fiabilite, SerieAnnuelle } from "./serie.js";

/** L'assiette de chaque taux de TVA, et ce qu'un taux unique en tirerait. */
export class AssietteTva {
  constructor(paquet) {
    const brut = paquet.tva ?? { annee: 0, lignes: [] };
    // L'année des points publiés. Une seule : le Trésor ne publie qu'un
    // millésime, et un point ne se reconduit pas en euros courants.
    this.annee = brut.annee ?? 0;
    // Assiette de chaque taux, en millions d'euros de `annee` — le centuple du
    // point.
    this.assiettesBrutes = new Map();
    this.assiettesNettes = new Map();
    let fiabilite = Fiabilite.CERTIFIEE;
    for (const ligne of brut.lignes ?? []) {
      this.assiettesBrutes.set(ligne.taux, 100 * ligne.point_brut_meur);
      this.assiettesNettes.set(ligne.taux, 100 * ligne.point_net_meur);
      fiabilite = Math.min(fiabilite, ligne.fiabilite);
    }
    this._fiabilite = this.assiettesNettes.size ? fiabilite : Fiabilite.ESTIMEE;
    this.pib = SerieAnnuelle.depuisPaquet("pib_courant", paquet.depenses.pib_courant);
  }

  /** Les assiettes sont-elles chargées ? */
  get chargee() {
    return this.assiettesNettes.size > 0 && this.annee > 0;
  }

  /** L'assiette de chaque taux, en millions d'euros de `annee`. */
  assiettes(nette = true) {
    return nette ? this.assiettesNettes : this.assiettesBrutes;
  }

  /** L'assiette de tous les taux, en millions d'euros de `annee`. */
  montant(nette = true) {
    let somme = 0.0;
    for (const assiette of this.assiettes(nette).values()) somme += assiette;
    return somme;
  }

  /** Ce que les taux d'aujourd'hui en tirent, en millions d'euros. */
  recette(nette = true) {
    let somme = 0.0;
    for (const [taux, assiette] of this.assiettes(nette)) somme += taux * assiette;
    return somme;
  }

  /** Le taux unique qui rapporterait exactement ce que rapportent les quatre. */
  tauxMoyen(nette = true) {
    const montant = this.montant(nette);
    return montant ? this.recette(nette) / montant : 0.0;
  }

  /** L'assiette rapportée au PIB de `annee`, et tenue à ce niveau ensuite. */
  partPib(nette = true) {
    const pib = this.chargee ? this.pib.valeur(this.annee) : 0.0;
    return pib ? this.montant(nette) / pib : 0.0;
  }

  /**
   * Ce qu'un taux unique rapporte DE PLUS que les quatre, en part de PIB.
   * Négatif sous le taux moyen ; zéro quand `tauxUnique` est nul, qui veut dire
   * « la TVA n'est pas réformée » et non « une TVA à zéro ».
   */
  recetteSupplementaire(tauxUnique, nette = true) {
    if (tauxUnique <= 0 || !this.chargee) return 0.0;
    return (tauxUnique - this.tauxMoyen(nette)) * this.partPib(nette);
  }

  /** Ce que le passage au taux unique fait au prix TTC, répercussion intégrale. */
  variationPrix(tauxUnique, tauxActuel) {
    return (1 + tauxUnique) / (1 + tauxActuel) - 1;
  }

  get fiabilite() {
    return this.chargee
      ? Math.min(this._fiabilite, this.pib.fiabilite(this.annee))
      : Fiabilite.ESTIMEE;
  }
}
