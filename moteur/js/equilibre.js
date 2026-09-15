/**
 * Ce que la retraite encaisse, et non plus seulement ce qu'elle verse.
 *
 * Portage de ``src/retraite_notionnelle/donnees/equilibre.py``.
 *
 * ``depenses.js`` porte la dépense observée — les Comptes de la protection
 * sociale de la DREES depuis 1959. Ce module porte l'autre moitié du bilan, les
 * RESSOURCES, et avec elle le solde.
 *
 * La source est autre, et il le fallait : les Comptes de la protection sociale
 * NE VENTILENT PAS LEURS RESSOURCES PAR RISQUE. Ils publient la dépense risque
 * par risque et le financement de l'ensemble, maladie et famille comprises. Ce
 * qui existe, c'est le compte du SYSTÈME DE RETRAITE — dépenses, ressources et
 * solde du même ensemble de régimes, sous la même convention —, que le COR
 * consolide chaque année depuis les rapports à la Commission des comptes de la
 * Sécurité sociale. On lui prend les DEUX colonnes : un solde ne se fabrique
 * pas en soustrayant deux périmètres.
 *
 * Champ : régimes légalement obligatoires, FSV compris, RAFP exclu. Ni
 * dépendance, ni capitalisation — 13,86 % du PIB en 2024 contre 13,59 % pour la
 * répartition obligatoire de la DREES et 14,54 % pour le risque
 * vieillesse-survie entier.
 */

import { Fiabilite, SerieAnnuelle } from "./serie.js";

/**
 * Les six postes du financement, dans l'ordre d'affichage : ce qui est cotisé
 * d'abord, puis ce qui ne l'est pas.
 *
 * `contributive` dit si le poste est une cotisation assise sur un revenu
 * d'activité — la seule ressource qu'un compte notionnel sache porter au crédit
 * de quelqu'un. La contribution d'équilibre de l'État à ses propres
 * fonctionnaires en est une malgré son nom : elle est prélevée sur les
 * traitements, à un taux publié, et le modèle la porte déjà au compte des
 * scénarios 4 et 5. Un impôt affecté, non.
 */
export const POSTES = [
  {
    code: "cotisations",
    libelle: "Cotisations sociales",
    glose: "Salariales, patronales et de non-salariés, hors contribution "
      + "d'équilibre. Les deux tiers du financement, et la seule part qu'un "
      + "compte notionnel sache créditer telle quelle.",
    contributive: true,
  },
  {
    code: "contribution_equilibre_etat",
    libelle: "Contribution d'équilibre de l'État",
    glose: "Ce que l'État verse au régime de ses propres fonctionnaires, au "
      + "taux qui équilibre ce régime — 74,28 % des traitements en 2024. C'est "
      + "une cotisation d'employeur par son assiette, un solde par son taux : "
      + "le modèle la porte au compte des scénarios 4 et 5, et elle est comptée "
      + "ici comme contributive pour cette raison.",
    contributive: true,
  },
  {
    code: "impots_et_taxes",
    libelle: "Impôts et taxes affectés",
    glose: "CSG, forfait social, taxe sur les salaires, transferts de TVA. Pour "
      + "l'essentiel, la compensation des allègements généraux de cotisations "
      + "patronales : l'État a exonéré, puis remboursé par l'impôt.",
    contributive: false,
  },
  {
    code: "transferts",
    libelle: "Transferts d'organismes extérieurs",
    glose: "Branche famille pour les majorations de pension et l'assurance "
      + "vieillesse des parents au foyer, Unédic pour les périodes de chômage. "
      + "Des droits sont acquis sans cotisation de l'assuré, et quelqu'un paie.",
    contributive: false,
  },
  {
    code: "subventions_equilibre",
    libelle: "Subventions d'équilibre aux régimes spéciaux",
    glose: "Ce que le budget de l'État comble à la SNCF, à la RATP, aux marins, "
      + "aux mines : des régimes dont les cotisants ont disparu avant les "
      + "pensionnés.",
    contributive: false,
  },
  {
    code: "autres_produits",
    libelle: "Autres produits",
    glose: "Reprises de provisions, produits de gestion, recettes diverses des "
      + "caisses.",
    contributive: false,
  },
];

export const CODES_POSTES = POSTES.map((poste) => poste.code);

/** Le compte du système de retraite : dépenses, ressources, solde, structure. */
export class ComptesRetraite {
  constructor(paquet) {
    const brut = paquet.comptes_retraite;
    this.depenses = SerieAnnuelle.depuisPaquet("comptes_retraite_depenses",
                                               brut.depenses);
    this.ressources = SerieAnnuelle.depuisPaquet("comptes_retraite_ressources",
                                                 brut.ressources);
    this.structure = new Map(
      POSTES.map((poste) => [
        poste.code,
        SerieAnnuelle.depuisPaquet(`structure_${poste.code}`, brut[poste.code]),
      ]),
    );
    this.premiereAnnee = this.depenses.premiereAnnee;
    this.derniereAnnee = this.depenses.derniereAnnee;
    // La frontière entre observé et projeté se lit dans la FIABILITÉ et non
    // dans une constante : le rapport suivant la décalera d'un an, et le
    // fichier de référence le dira tout seul.
    let observee = this.premiereAnnee;
    for (let annee = this.premiereAnnee; annee <= this.derniereAnnee; annee += 1) {
      if (this.depenses.fiabilite(annee) > Fiabilite.ESTIMEE) observee = annee;
    }
    this.derniereAnneeObservee = observee;
  }

  annees() {
    const liste = [];
    for (let a = this.premiereAnnee; a <= this.derniereAnnee; a += 1) liste.push(a);
    return liste;
  }

  /** Dépenses du système de retraite, en part du PIB de la même année. */
  depense(annee) {
    return this.depenses.valeur(annee);
  }

  ressource(annee) {
    return this.ressources.valeur(annee);
  }

  /**
   * Ressources moins dépenses, en part de PIB. Négatif : besoin de financement.
   * Le solde n'est pas stocké : il est la différence de deux séries écrites, et
   * le vérificateur confronte ce calcul au solde que le COR publie à part.
   */
  solde(annee) {
    return this.ressources.valeur(annee) - this.depenses.valeur(annee);
  }

  /** Part d'un poste dans les ressources de l'année. */
  part(code, annee) {
    return this.structure.get(code).valeur(annee);
  }

  /** Part des ressources qui est une cotisation sur un revenu d'activité. */
  partContributive(annee) {
    let somme = 0;
    for (const poste of POSTES) {
      if (poste.contributive) somme += this.part(poste.code, annee);
    }
    return somme;
  }

  fiabilite(annee) {
    return Math.min(this.depenses.fiabilite(annee), this.ressources.fiabilite(annee));
  }
}
