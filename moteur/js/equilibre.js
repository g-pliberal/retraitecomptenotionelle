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
      + "le modèle la porte au compte du système 3, et elle est comptée "
      + "ici comme contributive pour cette raison.",
    contributive: true,
  },
  {
    code: "impots_et_taxes",
    libelle: "Impôts et taxes affectés",
    glose: "CSG, taxe sur les salaires, forfait social, contribution sociale "
      + "de solidarité des sociétés, taxes des régimes agricoles. "
      + "38 % en financent le fonds de solidarité vieillesse. Ce n'est PAS la "
      + "compensation des allègements généraux de cotisations patronales : "
      + "celle-là passe par la TVA, qui finance la branche maladie, et le "
      + "compte de la Cnav n'en porte aucune ligne.",
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
    explication: "CSG, taxe sur les salaires, forfait social. Des recettes "
      + "fiscales affectées à la retraite, qui n'ouvrent de droit à personne : "
      + "plus du tiers finance le fonds de solidarité vieillesse.",
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
    explication: "Ce que l'État comble à la SNCF, aux mines, aux marins (des régimes dont les cotisants ont disparu avant les retraités), plus les "
      + "produits financiers et les recettes diverses des caisses.",
    postes: ["subventions_equilibre", "autres_produits"],
    couleur: "var(--serie-9)",
  },
];

/**
 * Ce qu'un organisme extérieur verse à la retraite, ligne par ligne, au
 * découpage des rapports à la Commission des comptes de la Sécurité sociale —
 * du côté de celui qui paie. La fiche de la CNAF distingue l'AVPF des
 * majorations, les fiches de l'Agirc-Arrco et de l'Ircantec portent chacune ce
 * que l'Unédic leur verse.
 */
export const POSTES_TRANSFERTS = [
  {
    code: "cnaf_avpf",
    organisme: "famille",
    libelle: "Assurance vieillesse des parents au foyer",
    glose: "Les cotisations que la branche famille verse à la Cnav pour les "
      + "parents qui ont réduit ou cessé leur activité pour élever un enfant : "
      + "des trimestres et un salaire portés au compte, sans cotisation de "
      + "l'assuré.",
  },
  {
    code: "cnaf_majorations",
    organisme: "famille",
    libelle: "Majorations de pension pour enfants",
    glose: "Les 10 % de pension en plus des parents de trois enfants, que la "
      + "branche famille rembourse en totalité aux régimes depuis 2011.",
  },
  {
    code: "unedic_agirc_arrco",
    organisme: "chomage",
    libelle: "Points Agirc-Arrco des chômeurs",
    glose: "Ce que l'assurance chômage verse à l'Agirc-Arrco pour que les "
      + "périodes de chômage indemnisé ouvrent des points de retraite "
      + "complémentaire (l'Agirc et l'Arrco séparément avant 2019).",
  },
  {
    code: "unedic_ircantec",
    organisme: "chomage",
    libelle: "Points Ircantec des chômeurs",
    glose: "La même chose, pour les contractuels de la fonction publique.",
  },
  {
    code: "fsv_cotisations",
    organisme: "solidarite",
    libelle: "Cotisations prises en charge pour des périodes non travaillées",
    glose: "Ce que le fonds de solidarité vieillesse verse aux régimes pour "
      + "que le chômage indemnisé, la maladie, l'apprentissage, le service "
      + "national et les stages de formation ouvrent des trimestres : des "
      + "droits acquis sans qu'aucune cotisation ait été prélevée sur un "
      + "revenu.",
  },
  {
    code: "fsv_prestations",
    organisme: "solidarite",
    libelle: "Minimum vieillesse, et le minimum contributif jusqu'en 2015",
    glose: "Ce que le même fonds verse pour les prestations qui ne dépendent "
      + "pas de ce qui a été cotisé : le minimum vieillesse, et le minimum "
      + "contributif de 2011 à 2015. C'est ce second financement, éteint "
      + "depuis, qui fait doubler cette ligne avant 2016.",
  },
];

export const CODES_TRANSFERTS = POSTES_TRANSFERTS.map((poste) => poste.code);

/**
 * Qui paie, et si le compte notionnel du dépôt supprime ce qu'il finance.
 *
 * `droitSupprime` : oui pour la branche famille — ni AVPF ni majorations dans
 * les scénarios 2 à 6. Oui aussi pour l'assurance chômage, mais pour une autre
 * raison : une année de chômage indemnisé ne verse rien au compte, alors qu'un
 * système notionnel réel pourrait créditer ce que l'Unédic paie, qui est une
 * cotisation assise sur l'allocation. Tant que le modèle ne le fait pas, la
 * recette suit le droit.
 *
 * `recetteParImpot` : vrai du seul fonds de solidarité vieillesse. Ce qu'il
 * verse aux régimes est financé par la CSG, et cette CSG est DÉJÀ dans le
 * poste « impôts et taxes affectés » des ressources. Qui retire ce poste en
 * entier doit cesser de retirer ce versement, sous peine de retirer la même
 * somme deux fois.
 */
export const ORGANISMES = [
  {
    code: "famille",
    libelle: "Branche famille",
    explication: "La CNAF paie les droits à retraite liés aux enfants. Le "
      + "compte notionnel du dépôt ne sert plus ces droits : il ne peut pas "
      + "compter cette recette comme la sienne.",
    droitSupprime: true,
  },
  {
    code: "chomage",
    libelle: "Assurance chômage",
    explication: "L'Unédic paie les points de retraite complémentaire des "
      + "chômeurs indemnisés. Le compte notionnel du dépôt ne porte rien au "
      + "compte pendant une année de chômage : cette recette non plus n'est "
      + "pas la sienne, tant qu'il ne crédite pas ce que l'Unédic verse.",
    droitSupprime: true,
  },
  {
    code: "solidarite",
    libelle: "Fonds de solidarité vieillesse",
    explication: "Le fonds finance par la CSG deux choses, et deux seulement : "
      + "des trimestres pour des périodes non travaillées, et le minimum "
      + "vieillesse. Aucun scénario notionnel ne sert l'un ni l'autre, la "
      + "garantie vieillesse qui remplace le second étant financée à part, "
      + "hors du compte des cotisants. Ce fonds échappait à la règle parce "
      + "que sa recette n'arrive pas par un transfert mais par l'impôt : elle "
      + "est dans le poste « impôts et taxes affectés », dont elle fait 38 % "
      + "en 2024. Il est supprimé au 1er janvier 2026, ses missions et son "
      + "financement passant à la CNAV ; la série s'arrête donc à 2025, et la "
      + "part constante prend le relais, ce qui est exact puisque les "
      + "missions, elles, continuent.",
    droitSupprime: true,
    recetteParImpot: true,
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
    // En MILLIONS d'euros, l'unité des rapports à la CCSS : c'est le PIB qui
    // les ramène à l'unité du reste du compte.
    this.transferts = new Map(
      POSTES_TRANSFERTS.map((poste) => [
        poste.code,
        SerieAnnuelle.depuisPaquet(`transferts_${poste.code}`,
                                   brut[`transferts_${poste.code}`]),
      ]),
    );
    // Le taux de prélèvement du système, en part des REVENUS D'ACTIVITÉ et non
    // du PIB. C'est la seule série du compte qui dise pourquoi les ressources
    // reculent en part de PIB : parce que le taux baisse, et non parce que
    // l'assiette rétrécit. `profilTaux` dit ce qu'on en prend.
    this.tauxPrelevement = SerieAnnuelle.depuisPaquet("taux_prelevement_retraite",
                                                      brut.taux_prelevement);
    this.pib = SerieAnnuelle.depuisPaquet("pib_courant", paquet.depenses.pib_courant);
    // La dette de TOUTES les administrations publiques, au sens de Maastricht,
    // en part de PIB : ce que le pays porte déjà. Elle ne sert à aucun calcul ;
    // la page Coût pose dessus le stock que chaque système accumule.
    this.dettePublique = SerieAnnuelle.depuisPaquet("dette_publique", brut.dette_publique);
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
  /**
   * Ce que le taux de prélèvement de `annee` vaut, rapporté à celui de
   * `reference`.
   *
   * LE PROFIL, ET JAMAIS LE NIVEAU. Le COR projette son taux sur les revenus
   * d'activité ; le dépôt mesure le sien sur l'assiette qu'il certifie, et les
   * deux définitions ne coïncident pas — 32,14 % contre 32,84 % en 2025.
   * Emprunter le niveau déplacerait la recette de 2 % sans le dire ; emprunter
   * le rapport d'une année à l'autre n'emprunte que la FORME de la
   * trajectoire. Vaut un sur toute année où l'assiette est publiée.
   */
  profilTaux(annee, reference) {
    const base = this.tauxPrelevement.valeur(reference);
    return base ? this.tauxPrelevement.valeur(annee) / base : 1.0;
  }

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

  // -- ce que d'autres caisses versent ---------------------------------------

  /** Ce qu'une ligne de transfert a rapporté, en millions d'euros. */
  transfert(code, annee) {
    return this.transferts.get(code).valeur(annee);
  }

  /** Ce qu'un organisme a versé, en millions d'euros. */
  transfertOrganisme(organisme, annee) {
    let somme = 0;
    for (const poste of POSTES_TRANSFERTS) {
      if (poste.organisme === organisme) somme += this.transfert(poste.code, annee);
    }
    return somme;
  }

  /** Le même versement, en part du PIB — l'unité du reste du compte. */
  transfertPartPib(organisme, annee) {
    return this.transfertOrganisme(organisme, annee) / this.pib.valeur(annee);
  }

  /**
   * Le même versement, en part des ressources de l'année : l'unité de la
   * structure des ressources, et ce qui permet de dire quelle fraction du
   * poste « transferts » un organisme explique.
   */
  transfertPartRessources(organisme, annee) {
    return this.transfertPartPib(organisme, annee) / this.ressource(annee);
  }

  /**
   * Ce que le compte notionnel ne peut pas compter, en part du PIB : la somme
   * des versements qui financent un droit que les scénarios notionnels ne
   * servent pas. C'est ce qu'il faudrait retirer des ressources avant de lire
   * leur coefficient d'équilibre.
   */
  transfertSupprimePartPib(annee, parImpot = null, organisme = null) {
    // `organisme` ne garde qu'un seul payeur : c'est ce qui permet au tableau
    // des postes de la page Coût d'écrire « dont branche famille » et « dont
    // assurance chômage » sur la ligne des transferts, comme le COR.
    let somme = 0;
    for (const payeur of ORGANISMES) {
      if (!payeur.droitSupprime) continue;
      if (parImpot !== null && Boolean(payeur.recetteParImpot) !== parImpot) continue;
      if (organisme !== null && payeur.code !== organisme) continue;
      somme += this.transfertPartPib(payeur.code, annee);
    }
    return somme;
  }

  /**
   * Ce qu'un scénario notionnel doit retirer de ses ressources, en part du
   * PIB. Dans la fenêtre où les quatre lignes sont connues, c'est ce que la
   * branche famille et l'assurance chômage ont réellement versé. En dehors —
   * avant 2013, et sur tout l'horizon projeté du COR —, c'est la même chose à
   * PART CONSTANTE des ressources, celle de l'année connue la plus proche :
   * personne ne projette ce que la CNAF versera en 2070, et une part constante
   * est l'hypothèse qui n'en ajoute aucune autre. `parImpot` passe à
   * `transfertSupprimePartPib` et y dit lesquels des quatre organismes compter.
   */
  recetteNonAcquise(annee, parImpot = null, organisme = null) {
    const premiere = this.premiereAnneeTransferts;
    const derniere = this.derniereAnneeTransferts;
    if (annee >= premiere && annee <= derniere) {
      return this.transfertSupprimePartPib(annee, parImpot, organisme);
    }
    const reference = Math.min(Math.max(annee, premiere), derniere);
    const part = this.transfertSupprimePartPib(reference, parImpot, organisme)
      / this.ressource(reference);
    return part * this.ressource(annee);
  }

  /**
   * La fenêtre où les QUATRE lignes sont connues. Elles ne commencent ni ne
   * finissent la même année : l'Ircantec n'est détaillée que depuis 2013, et le
   * rapport de printemps qui arrête la dernière année ne porte pas les fiches
   * des régimes complémentaires.
   */
  get premiereAnneeTransferts() {
    return Math.max(...[...this.transferts.values()].map((s) => s.premiereAnnee));
  }

  get derniereAnneeTransferts() {
    return Math.min(...[...this.transferts.values()].map((s) => s.derniereAnnee));
  }

  anneesTransferts() {
    const liste = [];
    for (let a = this.premiereAnneeTransferts; a <= this.derniereAnneeTransferts; a += 1) {
      liste.push(a);
    }
    return liste;
  }

  fiabilite(annee) {
    return Math.min(this.depenses.fiabilite(annee), this.ressources.fiabilite(annee));
  }
}
