/**
 * Le versant inverse de l'inventaire : ce qu'on cotise sans rien acquérir.
 *
 * PORT DE `src/retraite_notionnelle/frontiere.py`, et le plus léger du dépôt :
 * il n'y a RIEN à recalculer. La masse est le produit d'un taux par une
 * assiette, fait une fois par `scripts/construire_donnees.py` et déposé dans
 * le paquet ; ce module ne fait que le relire et rendre les deux proportions
 * que le fichier ne porte pas.
 *
 * POURQUOI LE CALCUL N'EST PAS PORTÉ. Le dépôt exige qu'un chiffre ne dépende
 * pas de la porte par laquelle on entre. Deux façons de le garantir : porter
 * le calcul et vérifier que les deux tombent juste, ou ne le faire qu'une fois
 * et le transporter. La seconde est ici la bonne — le produit ne dépend
 * d'aucune saisie, d'aucun réglage, d'aucune carrière : il serait identique
 * dans tous les navigateurs et pour tous les visiteurs.
 */

/** Ce qu'une année a prélevé sans ouvrir de droit, en milliards d'euros. */
class AnneeCotisationSterile {
  constructor(ligne) {
    this.annee = ligne.annee;
    this.assiette_md = ligne.assiette_md;
    this.taux = ligne.taux;
    this.total_md = ligne.total_md;
    this.salariale_md = ligne.salariale_md;
  }

  get patronale_md() {
    return this.total_md - this.salariale_md;
  }
}

/** Ce qu'une tranche Agirc-Arrco prélève, et ce qu'elle en fait acquérir. */
class TrancheComplementaire {
  constructor(ligne) {
    this.nom = ligne.nom;
    this.acquisitif = ligne.acquisitif;
    this.verse_sous_plafond = ligne.verse_sous_plafond;
    this.verse_au_dessus = ligne.verse_au_dessus;
  }

  get part_sous_plafond() {
    return 1 - this.acquisitif / this.verse_sous_plafond;
  }

  get part_au_dessus() {
    return 1 - this.acquisitif / this.verse_au_dessus;
  }
}

/** Le versant `cotisation` de la frontière, chiffré et en proportion. */
class Frontiere {
  constructor(paquet) {
    this.annees = paquet.annees.map((a) => new AnneeCotisationSterile(a));
    this.tranches = paquet.tranches.map((t) => new TrancheComplementaire(t));
    this.pourcentage_appel = paquet.pourcentage_appel;
    this.source_complementaire = paquet.source_complementaire;
    this.lu_le = paquet.lu_le;
  }

  get derniere() {
    return this.annees.length > 0 ? this.annees[this.annees.length - 1] : null;
  }
}

/** Relit le paquet — le pendant de `chargerAvantages`. */
export function chargerFrontiere(paquet) {
  return new Frontiere(paquet.frontiere);
}
