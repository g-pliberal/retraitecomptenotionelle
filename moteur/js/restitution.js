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
 *
 * LA PART DE TVA GARDÉE N'EST PAS ABANDONNÉE : le poste du COR la compte, et
 * le coût la rend à la proposition à compter de sa bascule. Le partage la
 * retranche avant de couper le poste en deux — moitié, moitié, sur ce qui est
 * vraiment abandonné (21 novembre 2026). Sa part de PIB vient du paquet, que
 * la fabrique rapporte au PIB que le coût projette.
 *
 * LA CTA NON PLUS : la proposition la supprime (décision 88), elle revient aux
 * factures d'énergie, et le partage la retranche de même (21 novembre 2026).
 */

import { AssietteActivite } from "./assiette.js";
import { PARAMETRES_DEFAUT } from "./config.js";
import { ComptesRetraite } from "./equilibre.js";
import { Fiabilite, SerieAnnuelle } from "./serie.js";

/** Les deux impôts du poste qui sont assis sur une rémunération. */
export const POSTES_REMUNERATION = [
  { code: "taxe_sur_les_salaires", libelle: "Taxe sur les salaires" },
  { code: "forfait_social", libelle: "Forfait social" },
];

/** Le partage, année par année, des impôts que la proposition abandonne. */
export class Restitution {
  constructor(paquet, partRendue = 0.5, anneeBascule = PARAMETRES_DEFAUT.annee_bascule, tvaGardee = true) {
    const brut = paquet.comptes_retraite;
    this.partRendue = partRendue;
    this.anneeBascule = anneeBascule;
    this.tvaGardeeActive = tvaGardee;
    this.gardee = brut.tva_gardee || {};
    const anneesGardees = Object.keys(this.gardee).map(Number);
    this.premiereGardee = Math.min(...anneesGardees);
    this.derniereGardee = Math.max(...anneesGardees);
    this.cta = brut.cta_supprimee || {};
    const anneesCta = Object.keys(this.cta).map(Number);
    this.premiereCta = Math.min(...anneesCta);
    this.derniereCta = Math.max(...anneesCta);
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

  /**
   * Les impôts et taxes affectés à la retraite, en part de PIB : le poste du
   * COR, part de TVA de l'Agirc-Arrco comprise.
   */
  posteAffecte(annee) {
    return this.comptes.ressource(annee) * this.comptes.part("impots_et_taxes", annee);
  }

  /**
   * La part de TVA que la proposition garde, en part de PIB, à compter de sa
   * bascule : l'année publiée la plus proche, comme `donnees/tva.py`.
   */
  tvaGardee(annee) {
    if (!this.tvaGardeeActive || annee < this.anneeBascule
        || !Number.isFinite(this.premiereGardee)) {
      return 0;
    }
    const publiee = Math.min(Math.max(annee, this.premiereGardee), this.derniereGardee);
    return Math.max(this.gardee[String(publiee)] ?? 0, 0);
  }

  /**
   * La CTA que la proposition supprime, en part de PIB, à compter de sa
   * bascule : l'année de la série la plus proche.
   */
  ctaSupprimee(annee) {
    if (annee < this.anneeBascule || !Number.isFinite(this.premiereCta)) {
      return 0;
    }
    const publiee = Math.min(Math.max(annee, this.premiereCta), this.derniereCta);
    return Math.max(this.cta[String(publiee)] ?? 0, 0);
  }

  /**
   * Les impôts et taxes que la proposition partage, en part de PIB : le
   * poste, moins la part de TVA qu'elle garde et la CTA qu'elle supprime.
   */
  posteAbandonne(annee) {
    return this.posteAffecte(annee) - this.tvaGardee(annee) - this.ctaSupprimee(annee);
  }

  /**
   * La part du poste qui est assise sur une rémunération — mesurée sur l'année
   * demandée tant que les deux impôts sont publiés, sur la dernière publiée
   * ensuite. C'est un TAUX qui se reconduit, jamais un montant en euros
   * courants.
   */
  partDuPoste(annee) {
    const reference = Math.min(annee, this.derniereAnnee);
    const poste = this.posteAffecte(reference) * this.assiette.pib.valeur(reference);
    if (poste <= 0) {
      return 0;
    }
    return this.montantRemuneration(reference) / poste;
  }

  /** Le partage d'une année. */
  annuelle(annee) {
    const gardee = this.tvaGardee(annee);
    const cta = this.ctaSupprimee(annee);
    const poste = this.posteAffecte(annee) - gardee - cta;
    const rendu = this.partRendue * poste;
    // Les deux impôts supprimés sont une part du poste du COR, non de ce qui
    // reste une fois la TVA gardée.
    const supprime = Math.min(this.partDuPoste(annee) * this.posteAffecte(annee), rendu);
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
      tvaGardee: gardee,
      ctaSupprimee: cta,
    };
  }
}

const MEMOIRE = new Map();

/**
 * Les points de CSG d'activité que la proposition rend cette année-là — le
 * raccourci de la fiche de paie, qui n'a besoin que de ce nombre. La lecture
 * des trois séries est mémorisée : la fiche de paie d'une carrière la demande
 * une fois par année cotisée.
 */
export function pointsCsgRendus(paquet, annee, partRendue = 0.5,
                                anneeBascule = PARAMETRES_DEFAUT.annee_bascule, tvaGardee = true) {
  let restitution = MEMOIRE.get(paquet);
  if (!restitution || restitution.partRendue !== partRendue
      || restitution.anneeBascule !== anneeBascule
      || restitution.tvaGardeeActive !== tvaGardee) {
    restitution = new Restitution(paquet, partRendue, anneeBascule, tvaGardee);
    MEMOIRE.set(paquet, restitution);
  }
  return restitution.annuelle(annee).pointsCsg;
}
