/**
 * Ce que la proposition rend au salaire, et ce qu'elle éteint en dette.
 *
 * Portage de `src/retraite_notionnelle/restitution.py`, dont le docstring
 * porte l'argument en entier. En deux phrases :
 *
 * La proposition ne reconduit pas les impôts et taxes affectés à la retraite —
 * 63,9 Md€ en 2025. Ne rien dire de cette recette, c'est la laisser au budget
 * de l'État, c'est-à-dire la consacrer tout entière au déficit ; la décision du
 * 20 septembre 2026 tranche autrement, et en deux moitiés : LA MOITIÉ EST
 * RENDUE AUX SALAIRES, LA MOITIÉ ÉTEINT DE LA DETTE.
 *
 * Ce qui est rendu l'est dans cet ordre, et le droit fixe l'ordre : on
 * SUPPRIME d'abord les deux impôts du poste qui sont assis sur une
 * rémunération — la taxe sur les salaires, dont l'article L. 131-8, 1° du code
 * de la sécurité sociale verse 58,35 % à la branche vieillesse, et le forfait
 * social, dont l'article L. 241-3, 1° lui donne le produit entier, ensemble
 * 28 % du poste —, puis le solde revient par une baisse de la CSG sur les
 * revenus d'activité, un peu plus d'un point.
 *
 * ET CETTE CSG-LÀ NE FINANCE AUCUNE RETRAITE. Ses 9,20 points vont à la CNAF
 * (0,95), à l'assurance maladie (4,25), à la CADES (0,45), à l'Unédic (1,47) et
 * à la CNSA (2,08) — 9,20 exactement, et rien pour la branche vieillesse
 * (L. 131-8, 3°). La baisse n'est donc pas la restitution d'un prélèvement
 * retraite : c'est une baisse d'impôt financée par une recette que la retraite
 * abandonne, et le site l'écrit comme telle.
 */

import { AssietteActivite } from "./assiette.js";
import { ComptesRetraite } from "./equilibre.js";
import { Fiabilite, SerieAnnuelle } from "./serie.js";

/** Les deux impôts du poste qui sont assis sur une rémunération. */
export const POSTES_REMUNERATION = [
  { code: "taxe_sur_les_salaires", libelle: "Taxe sur les salaires" },
  { code: "forfait_social", libelle: "Forfait social" },
];

/** Le partage, année par année, des impôts que la proposition abandonne. */
export class Restitution {
  constructor(paquet, partRendue = 0.5) {
    const brut = paquet.comptes_retraite;
    this.partRendue = partRendue;
    this.postes = new Map(
      POSTES_REMUNERATION.map(({ code }) => [
        code,
        SerieAnnuelle.depuisPaquet(`impots_remuneration_${code}`,
                                   brut[`impots_remuneration_${code}`]),
      ]),
    );
    this.assiette = new AssietteActivite(paquet);
    this.comptes = new ComptesRetraite(paquet);
    this.derniereAnnee = Math.min(
      ...[...this.postes.values()].map((s) => s.derniereAnnee),
    );
  }

  /** Taxe sur les salaires et forfait social, en millions d'euros courants. */
  montantRemuneration(annee) {
    let somme = 0;
    for (const serie of this.postes.values()) somme += serie.valeur(annee);
    return somme;
  }

  /** Les impôts et taxes que la proposition n'encaisse plus, en part de PIB. */
  posteAbandonne(annee) {
    return this.comptes.ressource(annee) * this.comptes.part("impots_et_taxes", annee);
  }

  /**
   * La part du poste qui est assise sur une rémunération — mesurée sur l'année
   * demandée tant que les deux impôts sont publiés, sur la dernière publiée
   * ensuite. C'est un TAUX qui se reconduit, jamais un montant en euros
   * courants.
   */
  partDuPoste(annee) {
    const reference = Math.min(annee, this.derniereAnnee);
    const poste = this.posteAbandonne(reference) * this.assiette.pib.valeur(reference);
    if (poste <= 0) {
      return 0;
    }
    return this.montantRemuneration(reference) / poste;
  }

  /** Le partage d'une année. */
  annuelle(annee) {
    const poste = this.posteAbandonne(annee);
    const rendu = this.partRendue * poste;
    const supprime = Math.min(this.partDuPoste(annee) * poste, rendu);
    const reference = this.assiette.anneeDeReference(annee);
    const partAssiette = this.assiette.partPib(reference);
    const reste = Math.max(0, rendu - supprime);
    const niveaux = [...this.postes.values()].map(
      (s) => s.fiabilite(Math.min(annee, this.derniereAnnee)),
    );
    return {
      annee,
      posteAbandonne: poste,
      rendu,
      supprimeSurLaRemuneration: supprime,
      pointsCsg: partAssiette ? reste / partAssiette : 0,
      eteintDeDette: (1 - this.partRendue) * poste,
      // Celle des deux séries d'impôts qui vaut le moins, l'année où la part
      // est mesurée. Les parts de PIB valent ce que vaut le compte du COR.
      fiabilite: niveaux.length ? Math.min(...niveaux) : Fiabilite.ESTIMEE,
    };
  }
}

/**
 * Les points de CSG d'activité que la proposition rend cette année-là — le
 * raccourci de la fiche de paie, qui n'a besoin que de ce nombre. La lecture
 * des trois séries est mémorisée : la fiche de paie d'une carrière la demande
 * une fois par année cotisée.
 */
const MEMOIRE = new Map();

export function pointsCsgRendus(paquet, annee, partRendue = 0.5) {
  let restitution = MEMOIRE.get(paquet);
  if (!restitution || restitution.partRendue !== partRendue) {
    restitution = new Restitution(paquet, partRendue);
    MEMOIRE.set(paquet, restitution);
  }
  return restitution.annuelle(annee).pointsCsg;
}
