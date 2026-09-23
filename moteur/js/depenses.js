/**
 * Ce que la retraite a coûté : les dépenses réellement versées, depuis 1959.
 *
 * Portage de ``src/retraite_notionnelle/donnees/depenses.py``. Le reste du
 * modèle calcule des DROITS — ce qu'une carrière ouvre ; ce module porte la
 * grandeur inverse, ce que la collectivité a effectivement payé.
 *
 * La source est unique : les Comptes de la protection sociale de la DREES,
 * risque vieillesse-survie. Le total tous régimes court de 1959 à 2024 sans
 * trou ; la ventilation par système ne commence qu'en 1990, parce que la
 * nomenclature d'avant ne se raccorde pas à celle d'après.
 */

import { SerieAnnuelle } from "./serie.js";

/**
 * Les treize postes de la ventilation, dans l'ordre d'affichage : la
 * répartition obligatoire d'abord, par masse décroissante en 2024, puis ce qui
 * n'en relève pas. `repartition` dit si le système relève de la répartition
 * OBLIGATOIRE — le risque vieillesse-survie porte aussi la capitalisation,
 * l'aide sociale aux personnes âgées et le minimum vieillesse, et l'on ne
 * compare pas des comptes notionnels à une allocation d'autonomie.
 */
/**
 * Les deux catégories de la ventilation d'une masse de pensions, du vocabulaire
 * du COR comme de celui de la DREES : ce qu'un assuré s'est ouvert par sa
 * propre carrière, et ce qu'un conjoint survivant reçoit de celle d'un autre.
 */
export const CATEGORIES_DROITS = ["direct", "derive"];

export const SYSTEMES = [
  {
    code: "regime_general",
    libelle: "Régime général (Cnav)",
    glose: "Le socle des salariés du privé. Il absorbe depuis 2020 les artisans "
      + "et les commerçants, dont le régime a été adossé à la Cnav : la marche "
      + "de cette année-là est une réorganisation, pas une dépense nouvelle.",
    repartition: true,
  },
  {
    code: "agirc_arrco",
    libelle: "Agirc-Arrco",
    glose: "Les complémentaires des salariés du privé, deux caisses jusqu'en "
      + "2018 et une seule depuis. À elles seules, un quart de la dépense.",
    repartition: true,
  },
  {
    code: "fonction_publique_etat",
    libelle: "Fonction publique d'État",
    glose: "Les pensions civiles et militaires de l'État, versées par le compte "
      + "d'affectation spéciale « Pensions ». La territoriale et l'hospitalière "
      + "n'y sont pas : la DREES les range avec les régimes spéciaux.",
    repartition: true,
  },
  {
    code: "regimes_speciaux",
    libelle: "Régimes spéciaux",
    glose: "La CNRACL — fonction publique territoriale et hospitalière —, la "
      + "SNCF, la RATP, les industries électriques et gazières et les autres, "
      + "réunies par la comptabilité nationale sous un seul poste.",
    repartition: true,
  },
  {
    code: "exploitants_agricoles",
    libelle: "Exploitants agricoles",
    glose: "Le régime des chefs d'exploitation, dont la dépense recule en euros "
      + "constants depuis trente ans : ses cotisants ont disparu avant ses "
      + "pensionnés.",
    repartition: true,
  },
  {
    code: "professions_liberales",
    libelle: "Professions libérales (CNAVPL)",
    glose: "Base et complémentaires des sections professionnelles.",
    repartition: true,
  },
  {
    code: "salaries_agricoles",
    libelle: "Salariés agricoles",
    glose: "Le régime aligné de la MSA.",
    repartition: true,
  },
  {
    code: "ircantec",
    libelle: "Ircantec",
    glose: "La complémentaire des agents non titulaires de l'État et des "
      + "collectivités.",
    repartition: true,
  },
  {
    code: "non_salaries_autres",
    libelle: "Autres régimes de non-salariés",
    glose: "Ce qui reste des régimes de non-salariés une fois les exploitants "
      + "agricoles et les professions libérales mis à part — la part la plus "
      + "réduite depuis l'adossement du RSI à la Cnav.",
    repartition: true,
  },
  {
    code: "repartition_autres",
    libelle: "Autres régimes par répartition",
    glose: "Fonds spéciaux, régimes résiduels, prestations vieillesse versées "
      + "par les branches maladie et famille.",
    repartition: true,
  },
  {
    code: "solidarite_etat",
    libelle: "Solidarité de l'État",
    glose: "Minimum vieillesse et crédits d'impôt liés à l'âge. Non "
      + "contributif : aucun compte notionnel ne le porterait, et c'est "
      + "précisément ce que les scénarios notionnels retirent.",
    repartition: false,
  },
  {
    code: "aide_sociale_locale",
    libelle: "Aide sociale des collectivités",
    glose: "Allocation personnalisée d'autonomie, hébergement des personnes "
      + "âgées dépendantes. De la dépendance plutôt que de la retraite, mais le risque vieillesse-survie les loge au même endroit.",
    repartition: false,
  },
  {
    code: "supplementaire",
    libelle: "Retraite supplémentaire",
    glose: "Capitalisation : RAFP, contrats collectifs d'assurance, de "
      + "prévoyance et de mutuelle, régimes d'entreprise. Un capital est placé : c'est ce qui la sépare de tout le reste de ce tableau.",
    repartition: false,
  },
];

export const CODES_SYSTEMES = SYSTEMES.map((systeme) => systeme.code);

/** Les dépenses observées, avec leur ventilation et le PIB qui les rapporte. */
export class DepensesRetraite {
  constructor(paquet) {
    const brut = paquet.depenses;
    const serie = (cle) => SerieAnnuelle.depuisPaquet(cle, brut[cle]);
    this.total = serie("total");
    this.pib = serie("pib_courant");
    // La réversion, lue et non modélisée : le modèle décrit une carrière, pas
    // un ménage. C'est la seule dépense non contributive dont le montant vienne
    // d'une publication plutôt que d'un calcul.
    this.droitsDerives = serie("droits_derives");
    // Les prestations non contributives que les comptes isolent, poste par
    // poste, depuis 2020. Elles ne complètent pas le modèle : elles le
    // REMPLACENT là où elles existent, le producteur primant sur le calcul.
    this.prestations = new Map(
      Object.keys(brut.prestations || {}).sort().map(
        (poste) => [poste, SerieAnnuelle.depuisPaquet(poste, brut.prestations[poste])],
      ),
    );
    this.systemes = new Map(
      SYSTEMES.map((systeme) => [systeme.code, serie(systeme.code)]),
    );
    this.premiereAnnee = this.total.premiereAnnee;
    this.derniereAnnee = this.total.derniereAnnee;
    this.premiereAnneeVentilee = Math.max(
      ...SYSTEMES.map((systeme) => this.systemes.get(systeme.code).premiereAnnee),
    );
    this.partDerives = serie("part_droits_derives");
    this.pensionsDroits = new Map(
      CATEGORIES_DROITS.map((categorie) => [categorie, serie(`pensions_${categorie}`)]),
    );
  }

  annees() {
    const liste = [];
    for (let a = this.premiereAnnee; a <= this.derniereAnnee; a += 1) liste.push(a);
    return liste;
  }

  anneesVentilees() {
    const liste = [];
    for (let a = this.premiereAnneeVentilee; a <= this.derniereAnnee; a += 1) {
      liste.push(a);
    }
    return liste;
  }

  /** Dépense totale du risque vieillesse-survie, en millions d'euros courants. */
  depense(annee) {
    return this.total.valeur(annee);
  }

  depenseSysteme(code, annee) {
    return this.systemes.get(code).valeur(annee);
  }

  /**
   * Quelle fraction de la masse versée est une pension de RÉVERSION. Un
   * huitième en 2010, un dixième en 2024, un dix-huitième en 2070 : la
   * réversion recule dans la projection du COR, les carrières des femmes se
   * rapprochant de celles des hommes.
   *
   * Elle sert à une chose : le rapport de masses par lequel un scénario
   * notionnel fait réagir la dépense est celui des droits DIRECTS des cas
   * types, et sans cette part il s'appliquait aussi à la réversion, que le
   * modèle ne calcule pas.
   */
  partDroitsDerives(annee) {
    return this.partDerives.valeur(annee);
  }

  /** Pensions de droit direct ou de droit dérivé selon la DREES, 2020-2024. */
  pensionsDroit(categorie, annee) {
    return this.pensionsDroits.get(categorie).valeur(annee);
  }

  /** Part de la dépense dans le produit intérieur brut de la même année. */
  /**
   * Masse des pensions de réversion de l'année, en millions d'euros courants.
   *
   * `null` hors de la fenêtre que la DREES publie : cette grandeur ne
   * s'extrapole pas. Elle ne se calcule pas non plus — le modèle n'a ni
   * conjoint, ni date de décès, ni ressources du survivant —, et c'est
   * précisément pourquoi elle est lue.
   */
  reversion(annee) {
    if (annee < this.droitsDerives.premiereAnnee
        || annee > this.droitsDerives.derniereAnnee) {
      return null;
    }
    return this.droitsDerives.valeur(annee);
  }

  /**
   * Un poste non contributif des comptes, en millions d'euros courants.
   *
   * `null` hors de la fenêtre publiée. La DREES ne donne ce grain qu'à partir
   * de 2020, quand le total du risque remonte à 1959.
   */
  prestation(poste, annee) {
    const serie = this.prestations.get(poste);
    if (serie === undefined) return null;
    if (annee < serie.premiereAnnee || annee > serie.derniereAnnee) return null;
    return serie.valeur(annee);
  }

  partPib(annee) {
    return this.total.valeur(annee) / this.pib.valeur(annee);
  }

  /**
   * Ce que coûte la seule répartition obligatoire, ventilation à l'appui.
   * Le total publié est plus large : il porte aussi la capitalisation, l'aide
   * sociale aux personnes âgées et le minimum vieillesse.
   */
  repartition(annee) {
    let somme = 0;
    for (const systeme of SYSTEMES) {
      if (systeme.repartition) somme += this.depenseSysteme(systeme.code, annee);
    }
    return somme;
  }

  /**
   * La part du total publié qui est une pension de répartition obligatoire :
   * la seule que le rapport de masses d'un scénario décrit. Lue sur la
   * ventilation, et reconduite avant sa première année — voir le modèle Python.
   */
  partRepartition(annee) {
    const reperee = Math.min(Math.max(annee, this.premiereAnneeVentilee),
                             this.derniereAnnee);
    const total = this.depense(reperee);
    return total ? this.repartition(reperee) / total : 1.0;
  }

  fiabilite(annee) {
    return Math.min(this.total.fiabilite(annee), this.pib.fiabilite(annee));
  }
}
