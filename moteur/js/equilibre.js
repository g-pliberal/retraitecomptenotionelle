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

/**
 * Les quatre groupes de postes, dits dans les mots de tout le monde.
 *
 * Les six postes du COR sont ceux d'un comptable. « Contribution d'équilibre de
 * l'État », « impôts et taxes affectés », « transferts d'organismes extérieurs »
 * ne disent rien à qui n'a pas fait d'économie, et un graphique à six bandes est
 * de toute façon illisible. Quatre groupes suffisent à porter la seule chose que
 * cette ventilation a à dire : les trois quarts de l'argent viennent des
 * salaires, le reste vient d'ailleurs. L'ordre est celui des bandes du
 * graphique, de bas en haut : le socle des salaires d'abord.
 */
export const GROUPES = [
  {
    code: "salaires",
    libelle: "Cotisations sur les salaires",
    explication: "Prélevées sur chaque fiche de paie, une part par le salarié, "
      + "une part par l'employeur. C'est la seule ressource qu'un compte "
      + "notionnel sache porter au crédit de quelqu'un.",
    postes: ["cotisations", "contribution_equilibre_etat"],
    couleur: "var(--serie-5)",
  },
  {
    code: "impots",
    libelle: "Impôts",
    explication: "CSG, TVA, taxe sur les salaires. L'État a allégé les "
      + "cotisations des employeurs pour baisser le coût du travail, puis "
      + "remboursé la retraite par l'impôt.",
    postes: ["impots_et_taxes"],
    couleur: "var(--serie-6)",
  },
  {
    code: "transferts",
    libelle: "Versements d'autres caisses",
    explication: "La branche famille paie les droits liés aux enfants, "
      + "l'assurance chômage ceux des périodes sans emploi : des droits acquis "
      + "sans cotisation de l'assuré, que quelqu'un paie quand même.",
    postes: ["transferts"],
    couleur: "var(--serie-7)",
  },
  {
    code: "reste",
    libelle: "Le reste",
    explication: "Ce que l'État comble à la SNCF, aux mines, aux marins — des "
      + "régimes dont les cotisants ont disparu avant les retraités —, plus les "
      + "produits financiers et les recettes diverses des caisses.",
    postes: ["subventions_equilibre", "autres_produits"],
    couleur: "var(--serie-9)",
  },
];

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

  /** Part d'un groupe de postes dans les ressources de l'année. */
  partGroupe(code, annee) {
    const groupe = GROUPES.find((entree) => entree.code === code);
    let somme = 0;
    for (const poste of groupe.postes) somme += this.part(poste, annee);
    return somme;
  }

  /**
   * Ce qu'un groupe rapporte, en part du PIB.
   *
   * C'est la grandeur que le graphique empile : les parts d'un même total ne se
   * lisent qu'en pourcentages les unes des autres, alors que les parts de PIB se
   * lisent aussi dans le temps — et c'est le temps qui dit que l'impôt a doublé
   * pendant que les cotisations ne bougeaient pas.
   */
  ressourceGroupe(code, annee) {
    return this.partGroupe(code, annee) * this.ressource(annee);
  }

  /**
   * Les années où la VENTILATION est publiée. Le total des ressources remonte
   * plus haut et va plus loin ; les deux bornes se lisent donc dans les séries,
   * jamais dans une constante écrite ici.
   */
  anneesVentilees() {
    let premiere = -Infinity;
    let derniere = Infinity;
    for (const serie of this.structure.values()) {
      if (serie.premiereAnnee > premiere) premiere = serie.premiereAnnee;
      if (serie.derniereAnnee < derniere) derniere = serie.derniereAnnee;
    }
    const liste = [];
    for (let a = premiere; a <= derniere; a += 1) liste.push(a);
    return liste;
  }

  fiabilite(annee) {
    return Math.min(this.depenses.fiabilite(annee), this.ressources.fiabilite(annee));
  }
}
