import { DateMois } from "./calendrier.js";
import { Fiabilite } from "./serie.js";

/**
 * Durée d'assurance requise pour le taux plein, PAR GÉNÉRATION.
 *
 * Depuis la loi du 22 juillet 1993, l'exigence est indexée sur l'année de
 * NAISSANCE et non sur l'année de liquidation : deux assurés qui liquident le
 * même jour n'ont pas la même durée requise s'ils ne sont pas de la même
 * génération.
 */
export class TableParGeneration {
  constructor(table) {
    this._table = table ?? {};
    this._generations = Object.keys(this._table).map(Number).sort((a, b) => a - b);
  }

  /**
   * Lecture en escalier : la valeur d'une génération non renseignée est celle
   * de la dernière renseignée avant elle, et la dernière du fichier vaut pour
   * toutes les suivantes. En deçà de la première, `null` : le paramètre ne
   * dépendait pas encore de la génération.
   *
   * @returns {[number, number] | null} valeur et fiabilité.
   */
  valeur(generation) {
    if (this._generations.length === 0 || generation < this._generations[0]) {
      return null;
    }
    let applicable = this._generations[0];
    for (const candidate of this._generations) {
      if (candidate > generation) {
        break;
      }
      applicable = candidate;
    }
    return this._table[String(applicable)];
  }
}

/** Durée d'assurance requise pour le taux plein, par génération. */
export class DureesRequises extends TableParGeneration {
  constructor(paquet) {
    super(paquet.durees_requises);
  }

  /** @returns {[number, number] | null} trimestres et fiabilité. */
  trimestres(generation) {
    return this.valeur(generation);
  }
}

/**
 * Durée requise que la suspension de 2026 remplace, pour les pensions prenant
 * effet avant le 1er septembre 2026 : 171 trimestres pour les nés en 1964, 172
 * pour ceux de 1965 — portage de `DureesRequisesAvantSuspension`.
 */
export class DureesRequisesAvantSuspension extends TableParGeneration {
  constructor(paquet) {
    super(paquet.durees_requises_avant_suspension);
  }

  /** @returns {[number, number] | null} trimestres et fiabilité. */
  trimestres(generation) {
    return this.valeur(generation);
  }
}

/** Première date d'effet de la table de la suspension, et ses générations. */
export const SUSPENSION_2026_EFFET = [2026, 9];
export const GENERATIONS_SUSPENSION = [1964.0, 1966.0];

/**
 * Durée requise propre à un régime spécial, par génération.
 *
 * La SNCF, la RATP et les IEG écrivent chacune leur table dans leur texte, et la
 * suspension de 2026, qui a abaissé la table commune, ne les a pas touchées. La
 * table de la SNCF porte en plus ce que le II de l'article 35 du décret
 * n° 2008-639 retranche à la durée requise pour compter la décote par la durée.
 */
export class DureesRequisesRegimes {
  constructor(paquet) {
    this._tables = Object.fromEntries(
      Object.entries(paquet.durees_requises_regimes ?? {})
        .map(([table, { depuis, lignes }]) => [
          table, { depuis, lignes: new TableParGeneration(lignes) },
        ]),
    );
  }

  /**
   * Une table ne répond qu'à qui réunit les conditions à compter de sa date
   * d'effet (`ouverture`, rang du mois) — portage de `DureesRequisesRegimes`.
   * @returns {[number, number, number] | null} trimestres, retranchés pour la décote, fiabilité.
   */
  ligne(table, generation, ouverture) {
    const lue = this._tables[table];
    if (lue === undefined || ouverture < lue.depuis) {
      return null;
    }
    return lue.lignes.valeur(generation);
  }
}

/**
 * Durée requise lue au MOIS où l'assuré réunit les conditions : le calendrier
 * de la réforme de 2008 des régimes spéciaux, 150 puis 151 à 166 trimestres —
 * portage de `CalendriersDureeRequise`.
 */
export class CalendriersDureeRequise {
  constructor(paquet) {
    this._table = paquet.calendriers_duree_requise ?? {};
  }

  /** @returns {[number, number] | null} trimestres et fiabilité. */
  trimestres(calendrier, ouverture) {
    let retenue = null;
    for (const [depuis, trimestres, fiabilite] of this._table[calendrier] ?? []) {
      if (depuis > ouverture) {
        break;
      }
      retenue = [trimestres, fiabilite];
    }
    return retenue;
  }
}

/**
 * Durée de services requise dans la fonction publique, 2004-2008.
 *
 * Le II de l'article 66 de la loi du 21 août 2003 fait monter le nombre de
 * trimestres du pourcentage maximum de 150 à 160, deux par an, selon l'ANNÉE
 * OÙ LE DROIT S'OUVRE. La table ne répond que pour les années qu'elle porte :
 * avant, la fiche porte 150 ; après, la durée du régime général vaut.
 */
export class DureesRequisesFonctionPublique {
  constructor(paquet) {
    this._table = paquet.durees_requises_fonction_publique ?? {};
  }

  /** @returns {[number, number] | null} trimestres et fiabilité. */
  trimestres(anneeOuverture) {
    return this._table[String(anneeOuverture)] ?? null;
  }
}

/**
 * Durée requise d'un fonctionnaire dont le droit s'ouvre AVANT SOIXANTE ANS.
 *
 * Ce n'est pas celle de sa génération mais celle « exigée des fonctionnaires
 * atteignant [soixante ans] l'année à compter de laquelle la liquidation peut
 * intervenir » (article 5, VI, de la loi du 21 août 2003, puis L. 13, III, du
 * code des pensions). Deux règles : ``l13_iii``, par année d'ouverture ;
 * ``xxiv_c``, les militaires qui peuvent liquider à compter du 1er septembre
 * 2023. Les clés du paquet sont des rangs de mois (``DateMois.rang``).
 */
export class DureesRequisesAvantSoixanteAns {
  constructor(paquet) {
    this._table = paquet.durees_requises_avant_soixante_ans ?? {};
    this._rangs = {};
    for (const [regle, valeurs] of Object.entries(this._table)) {
      this._rangs[regle] = Object.keys(valeurs).map(Number).sort((a, b) => a - b);
    }
  }

  _marche(regle, rang) {
    const rangs = this._rangs[regle];
    if (rangs === undefined || rangs.length === 0 || rang < rangs[0]) {
      return null;
    }
    let retenu = rangs[0];
    for (const candidat of rangs) {
      if (candidat > rang) {
        break;
      }
      retenu = candidat;
    }
    return this._table[regle][String(retenu)];
  }

  /** Règle de L. 13, III : la génération qui a soixante ans cette année. */
  parAnnee(anneeOuverture) {
    return this._marche("l13_iii", anneeOuverture * 12);
  }

  /** Règle du XXIV, C, 2° : null avant le 1er septembre 2023. */
  depuis2023(ouverture) {
    return this._marche("xxiv_c", ouverture.rang);
  }
}

/**
 * Durée d'assurance MAXIMALE prise en compte par la proratisation.
 *
 * Ce n'est pas la durée requise pour le taux plein, et le moteur les
 * confondait. La loi du 22 juillet 1993 a fait monter la première de 150 à
 * 160 trimestres pour les générations 1934 à 1943, et n'a touché à la seconde
 * que pour les générations 1944 à 1948 (article R. 351-6). Un assuré né en
 * 1945 ayant validé 156 trimestres se voit opposer 160 trimestres pour le taux
 * — il est décoté — mais 154 pour la proratisation : son coefficient vaut 1.
 *
 * La lecture s'ARRÊTE à la dernière génération du fichier, au lieu de prolonger
 * sa dernière valeur : à compter de 1949 la durée de proratisation rejoint la
 * durée requise, et prolonger 160 trimestres à des générations qui en doivent
 * 172 rendrait l'erreur dans l'autre sens.
 */
export class DureesProratisation extends TableParGeneration {
  constructor(paquet) {
    super(paquet.durees_proratisation);
  }

  /** @returns {[number, number] | null} trimestres et fiabilité. */
  trimestres(generation) {
    if (this._generations.length === 0
        || generation > this._generations[this._generations.length - 1]) {
      return null;
    }
    return this.valeur(generation);
  }
}

/** Âge légal d'ouverture des droits, par génération. */
export class AgesOuverture extends TableParGeneration {
  constructor(paquet) {
    super(paquet.ages_ouverture);
  }

  /** @returns {[number, number] | null} âge et fiabilité. */
  age(generation) {
    return this.valeur(generation);
  }
}

/**
 * Âge d'où la SNCF et la RATP comptent la surcote, par génération : l'âge
 * légal décalé de cinq générations, soixante-quatre ans à compter de 1970.
 */
export class AgesSurcoteRegimesSpeciaux extends TableParGeneration {
  constructor(paquet) {
    super(paquet.ages_surcote_regimes_speciaux);
  }

  /** @returns {[number, number] | null} âge et fiabilité. */
  age(generation) {
    return this.valeur(generation);
  }
}

/** Âge d'annulation de la décote, par génération : 65 ans, puis 67. */
export class AgesAnnulationDecote extends TableParGeneration {
  constructor(paquet) {
    super(paquet.ages_annulation_decote);
  }

  /** @returns {[number, number] | null} âge et fiabilité. */
  age(generation) {
    return this.valeur(generation);
  }
}

/**
 * Âges PROPRES à un régime, par génération : ouverture et taux plein.
 *
 * Le règlement d'une section libérale écrit souvent ses âges génération par
 * génération, et ce ne sont pas ceux du régime général : celui de la CAVOM
 * ouvre la complémentaire à soixante ans aux nés avant 1956. La fiche nomme
 * sa table (`age_table`) ; la lecture est en escalier. Voir le modèle Python.
 */
export class AgesRegimes {
  constructor(paquet) {
    this._tables = new Map(
      Object.entries(paquet.ages_regimes ?? {})
        .map(([table, lignes]) => [table, new TableParGeneration(lignes)]),
    );
  }

  /**
   * @returns {[number, number, number] | null} âge d'ouverture, âge du taux
   *   plein, fiabilité ; `null` hors table.
   */
  ages(table, generation) {
    const lue = this._tables.get(table);
    const ligne = lue ? lue.valeur(generation) : null;
    return ligne ? ligne.slice(0, 3) : null;
  }

  /**
   * Coefficient de minoration par trimestre que la table écrit pour cette
   * génération — la CARCDSF de 2011 à 2023 —, et sa fiabilité ; `null` si
   * la ligne n'en porte pas, et la fiche garde alors le sien.
   *
   * @returns {[number, number] | null}
   */
  decote(table, generation) {
    const lue = this._tables.get(table);
    const ligne = lue ? lue.valeur(generation) : null;
    if (!ligne || ligne[3] === null || ligne[3] === undefined) {
      return null;
    }
    return [ligne[3], ligne[2]];
  }
}

/**
 * Âges de la catégorie active et de la super-active, par génération.
 *
 * Le drapeau `categorie_active` existait dans la configuration sans qu'aucun
 * statut le porte : le policier et l'aide-soignant étaient calculés comme des
 * sédentaires, et l'âge du sédentaire leur était opposé. Cette table porte les
 * quatre paramètres que le classement déplace — l'âge d'ouverture (l'âge
 * anticipé ou minoré de L. 24, I, 1°), l'âge d'annulation de la décote (la
 * limite d'âge du grade, puis l'article L. 14 bis), la durée de services
 * classés exigée, et la durée de services et bonifications REQUISE, que le
 * XXIV, B de l'article 10 de la loi du 14 avril 2023 fixe par dérogation à
 * L. 13 — pour les deux classements, lus en escalier sur la génération.
 */
export class AgesCategorieActive {
  constructor(paquet) {
    this._table = paquet.categorie_active ?? {};
    this._generations = {};
    for (const [classement, valeurs] of Object.entries(this._table)) {
      this._generations[classement] = Object.keys(valeurs).map(Number)
        .sort((a, b) => a - b);
    }
  }

  get classements() {
    return Object.keys(this._table).sort();
  }

  /**
   * @returns {{ageOuverture: number, ageAnnulation: number,
   *            servicesRequis: number, fiabilite: number,
   *            dureeRequise: number|null} | null}
   */
  derogation(classement, generation) {
    const generations = this._generations[classement];
    if (generations === undefined || generations.length === 0
        || generation < generations[0]) {
      return null;
    }
    let applicable = generations[0];
    for (const candidate of generations) {
      if (candidate > generation) {
        break;
      }
      applicable = candidate;
    }
    const ligne = this._table[classement][String(applicable)];
    return {
      ageOuverture: ligne[0],
      ageAnnulation: ligne[1],
      servicesRequis: ligne[2],
      fiabilite: ligne[3],
      // Durée de services et bonifications propre au classement, « par
      // dérogation à l'article L. 13 ». Nulle avant les marches de 2023
      // (septembre 1966, septembre 1971) : la durée est alors celle de
      // l'année d'ouverture du droit (DureesRequisesAvantSoixanteAns).
      dureeRequise: ligne[4] ?? null,
    };
  }
}

/**
 * Durée de services qui ouvre la pension militaire, PAR ANNÉE D'ATTEINTE.
 *
 * La pension militaire ne s'ouvre pas à un âge mais à une durée : dix-sept ans
 * de services effectifs pour un non-officier, vingt-sept pour un officier
 * (L. 24, II), quinze et vingt-cinq avant la loi du 9 novembre 2010. La clé
 * n'est pas la génération : l'article 4 du décret n° 2011-2103 indexe le
 * relèvement sur l'année où l'ancienne durée est atteinte.
 */
export class DureesServicesMilitaires {
  constructor(paquet) {
    this._table = paquet.durees_services_militaires ?? {};
    this._annees = {};
    for (const [categorie, valeurs] of Object.entries(this._table)) {
      this._annees[categorie] = Object.keys(valeurs).map(Number).sort((a, b) => a - b);
    }
  }

  get categories() {
    return Object.keys(this._table).sort();
  }

  /** Durée d'avant la loi de 2010 — quinze ans, ou vingt-cinq. */
  dureeDeBase(categorie) {
    const annees = this._annees[categorie];
    if (annees === undefined || annees.length === 0) {
      return null;
    }
    return this._table[categorie][String(annees[0])][0];
  }

  /** @returns {[number, number] | null} années requises et fiabilité. */
  anneesRequises(categorie, anneeAtteinte) {
    const annees = this._annees[categorie];
    if (annees === undefined || annees.length === 0) {
      return null;
    }
    let applicable = annees[0];
    for (const candidate of annees) {
      if (candidate > anneeAtteinte) {
        break;
      }
      applicable = candidate;
    }
    return this._table[categorie][String(applicable)];
  }
}

/**
 * Âge auquel la pension militaire différée entre en jouissance.
 *
 * Les 2° à 4° de l'article L. 25 servent une pension au militaire qui part
 * avant la durée d'ouverture, à condition qu'il ait quinze ans de services,
 * mais à « l'âge défini à l'article L. 161-17-2 […] abaissé de dix années ».
 */
export class AgesJouissanceMilitaire extends TableParGeneration {
  constructor(paquet) {
    super(paquet.ages_jouissance_militaire);
  }

  /** @returns {[number, number] | null} âge et fiabilité. */
  age(generation) {
    return this.valeur(generation);
  }
}

/** Coefficient de minoration du taux plein par trimestre manquant. */
export class CoefficientsMinoration extends TableParGeneration {
  constructor(paquet) {
    super(paquet.coefficients_minoration);
  }

  /** @returns {[number, number] | null} coefficient et fiabilité. */
  coefficient(generation) {
    return this.valeur(generation);
  }
}

/** Nombre d'années retenues au salaire annuel moyen, par génération. */
export class AnneesSalaireReference extends TableParGeneration {
  constructor(paquet) {
    super(paquet.annees_salaire_reference);
  }

  /** @returns {[number, number] | null} nombre d'années et fiabilité. */
  annees(generation) {
    return this.valeur(generation);
  }
}

/**
 * Minimum contributif, minimum majoré et plafond d'écrêtement.
 *
 * Trois grandeurs : le minimum auquel est portée la pension de base, le
 * minimum MAJORÉ servi à sa place quand la durée cotisée atteint la durée
 * requise, et le plafond de l'article L. 173-2 au-delà duquel le complément
 * est rogné.
 *
 * Les trois sont des ANCRES DATÉES, lues dans le code de la sécurité sociale
 * et non dans une série annuelle : le code n'est pas modifié chaque année, les
 * montants sont revalorisés par l'effet de la loi. C'est donc au modèle de le
 * faire, et sur le bon index — le SMIC à partir de la date d'effet, les prix
 * avant elle.
 */
/**
 * Année à partir de laquelle chaque montant suit le SMIC et non plus les prix :
 * le plafond d'écrêtement depuis le décret du 14 février 2014, les deux minima
 * depuis la réforme du 14 avril 2023. Avant, ils suivaient les prix.
 */
export const INDEXATION_SUR_LE_SMIC = Object.freeze({
  montant_base: 2023,
  montant_majore: 2023,
  plafond_ecretement: 2014,
});

export class MinimumContributif {
  constructor(paquet, macro) {
    this.macro = macro;
    this._table = paquet.minimum_contributif ?? {};
  }

  /**
   * Ancre de la mesure, portée à l'année demandée.
   *
   * Un montant CONNU passe avant tout calcul : quand l'année figure au
   * fichier, on la sert telle quelle. Sinon on projette depuis la valeur en
   * vigueur à cette date — la dernière fixée avant elle, jamais une
   * postérieure, sans quoi les marches créées par une réforme glisseraient
   * dans le passé.
   *
   * L'index dépend de l'ANNÉE TRAVERSÉE et non de l'ancre : les prix jusqu'à
   * la bascule que la loi a fixée pour cette grandeur, le SMIC ensuite.
   *
   * @returns {[number, number]} valeur, et fiabilité.
   */
  _revalorise(mesure, annee) {
    const ancres = Object.keys(this._table)
      .filter((cle) => cle.startsWith(`${mesure}|`))
      .map((cle) => Number(cle.split("|")[1]))
      .sort((a, b) => a - b);
    if (ancres.length === 0) {
      return [0.0, 0];
    }
    if (ancres.includes(annee)) {
      return this._table[`${mesure}|${annee}`];
    }
    const anterieures = ancres.filter((a) => a < annee);
    const reference = anterieures.length
      ? anterieures[anterieures.length - 1]
      : ancres[0];
    const [valeur, fiabilite] = this._table[`${mesure}|${reference}`];
    const bascule = INDEXATION_SUR_LE_SMIC[mesure];
    const pivot = Math.min(Math.max(reference, bascule), annee);
    const coefficient = this.macro.coefficientPrix(reference, pivot)
      * this.macro.coefficientSmic(pivot, annee);
    return [valeur * coefficient, fiabilite];
  }

  /**
   * Montant de base, montant majoré et plafond d'écrêtement de l'année.
   *
   * Les deux montants sont rendus ensemble parce que le droit les ADDITIONNE
   * plutôt qu'il ne choisit entre eux : la pension est portée au montant de
   * base au prorata de la durée d'assurance acquise dans le régime, puis
   * l'écart entre le majoré et le base s'y ajoute au prorata de la seule durée
   * COTISÉE (D. 351-2-2).
   *
   * @returns {[number, number, number, number]} base, majoré, plafond, fiabilité.
   */
  valeurs(annee) {
    if (Object.keys(this._table).length === 0) {
      return [0.0, 0.0, 0.0, 0];
    }
    const [base, fiabiliteBase] = this._revalorise("montant_base", annee);
    const [majore, fiabiliteMajore] = this._revalorise("montant_majore", annee);
    const [plafond, fiabilitePlafond] = this._revalorise("plafond_ecretement", annee);
    return [base, majore, plafond,
      Math.min(fiabiliteBase, fiabiliteMajore, fiabilitePlafond)];
  }
}

/**
 * Décote de la fonction publique — article L. 14 du code des pensions.
 *
 * Deux paramètres, lus à l'ANNÉE DE LIQUIDATION parce que la montée en charge
 * voulue par la loi du 21 août 2003 est calendaire et non générationnelle : le
 * coefficient de minoration par trimestre, d'un huitième de point par an de
 * 0,125 % en 2006 à 1,25 % en 2015, et le nombre de trimestres retranchés à la
 * LIMITE D'ÂGE pour obtenir l'âge d'annulation, de seize en 2006 à zéro en
 * 2020. Rien avant 2006 : la décote n'existait pas dans la fonction publique.
 * Les deux se lisent à l'année où le droit s'ouvre, non à celle du départ :
 * c'est `ScenarioActuel.anneeOuvertureDesDroits` qui la fournit.
 */
export class DecoteFonctionPublique {
  /** @param {object} paquet @param {string} cle table du paquet à lire. */
  constructor(paquet, cle = "decote_fonction_publique") {
    this._table = paquet[cle] ?? {};
    this._annees = Object.keys(this._table).map(Number).sort((a, b) => a - b);
  }

  /** @returns {[number, number, number]|null} trimestres, coefficient, fiabilité. */
  parametres(annee) {
    if (this._annees.length === 0 || annee < this._annees[0]) {
      return null;
    }
    let applicable = this._annees[0];
    for (const candidate of this._annees) {
      if (candidate > annee) {
        break;
      }
      applicable = candidate;
    }
    return this._table[String(applicable)];
  }
}

/**
 * Décote des régimes spéciaux — réforme de 2008, montée en charge.
 *
 * LES RÉGIMES SPÉCIAUX N'ONT PAS DÉCOTÉ DE 1,25 % DÈS 2009. La réforme de 2008
 * leur donne la décote de la fonction publique AVEC QUATRE ANS DE RETARD :
 * rien avant le 1er juillet 2010, puis un dixième du taux plein, un dixième de
 * plus chaque 1er juillet jusqu'à 1,25 % en 2019. Opposer 1,25 % à un cheminot
 * parti en 2011, c'est décoter dix fois trop — et, la décote étant plafonnée à
 * vingt trimestres, lui retirer 25 % de sa pension au lieu de 2,5 %.
 *
 * L'âge d'annulation suit le même retard : l'âge de référence du régime —
 * l'âge d'ouverture du droit majoré de cinq ans, non la limite d'âge du grade
 * — diminué de seize trimestres en 2010, de rien à partir de 2024.
 */
export class DecoteRegimesSpeciaux extends DecoteFonctionPublique {
  constructor(paquet) {
    super(paquet, "decote_regimes_speciaux");
  }
}

/**
 * Minimum garanti de la fonction publique — article L. 17 du code des pensions.
 *
 * Ce n'est pas un plancher proratisé mais un BARÈME EN ESCALIER sur la durée de
 * services, rapporté à un traitement de référence gelé : celui de l'indice
 * majoré 227 au 1er janvier 2004, revalorisé sur les prix depuis. Quinze ans de
 * services en ouvrent 57,5 %, trente ans 95 %, quarante ans la totalité.
 */
export class MinimumGaranti {
  constructor(paquet, macro) {
    this.macro = macro;
    const contenu = paquet.minimum_garanti ?? {};
    this._bareme = contenu.bareme ?? {};
    this._point = contenu.point_indice ?? {};
    this._montants = contenu.montants ?? {};
    this._anneesBareme = Object.keys(this._bareme).map(Number).sort((a, b) => a - b);
    this._anneesMontants = Object.keys(this._montants).map(Number).sort((a, b) => a - b);
  }

  /** Barème en vigueur l'année de liquidation, ou ``null`` avant 1976. */
  bareme(anneeLiquidation) {
    if (this._anneesBareme.length === 0 || anneeLiquidation < this._anneesBareme[0]) {
      return null;
    }
    let applicable = this._anneesBareme[0];
    for (const candidate of this._anneesBareme) {
      if (candidate > anneeLiquidation) {
        break;
      }
      applicable = candidate;
    }
    return this._bareme[String(applicable)];
  }

  _pointIndice(annee) {
    const annees = Object.keys(this._point).map(Number).filter((a) => a <= annee);
    if (annees.length === 0) {
      return null;
    }
    return this._point[String(Math.max(...annees))];
  }

  /**
   * Ce que devient un traitement indiciaire entre deux années : un
   * fonctionnaire garde son indice, son traitement suit le point. `null` quand
   * la série ne couvre pas les deux années.
   */
  ratioPointIndice(depart, arrivee) {
    const de = this._pointIndice(depart);
    const a = this._pointIndice(arrivee);
    if (de === null || a === null || !(de[0] > 0)) {
      return null;
    }
    return a[0] / de[0];
  }

  /**
   * Montant plein du minimum garanti, quarante ans de services.
   *
   * Un montant SERVI connu prime sur tout calcul ; après 2004 la référence est
   * le traitement gelé de l'indice majoré 227, projeté sur les prix depuis
   * l'ancre en vigueur ; avant 2004, le gel n'existe pas et c'est le traitement
   * de l'indice majoré de l'année, au point d'indice de cette année-là.
   */
  reference(anneeLiquidation) {
    const bareme = this.bareme(anneeLiquidation);
    if (bareme === null || bareme === undefined) {
      return null;
    }
    const indice = bareme[0];
    const fiabiliteBareme = bareme[5];

    if (anneeLiquidation <= MinimumGaranti.ANNEE_GEL
        && this._montants[String(anneeLiquidation)] === undefined) {
      const point = this._pointIndice(anneeLiquidation);
      if (point === null) {
        return null;
      }
      return [indice * point[0], Math.min(fiabiliteBareme, point[1])];
    }

    if (this._anneesMontants.length === 0) {
      return null;
    }
    let valeur;
    let fiabilite;
    if (this._montants[String(anneeLiquidation)] !== undefined) {
      [valeur, fiabilite] = this._montants[String(anneeLiquidation)];
    } else {
      const anterieures = this._anneesMontants.filter((a) => a < anneeLiquidation);
      const ancre = anterieures.length
        ? anterieures[anterieures.length - 1]
        : this._anneesMontants[0];
      [valeur, fiabilite] = this._montants[String(ancre)];
      valeur *= this.macro.coefficientPrix(ancre, anneeLiquidation);
    }
    return [valeur * indice / MinimumGaranti.INDICE_REFERENCE,
      Math.min(fiabiliteBareme, fiabilite)];
  }

  /**
   * Plancher opposable pour une durée de services donnée.
   *
   * Sous quinze ans, deux règles : le c de L. 17 — un quinzième de 57,5 % par
   * année — ne vaut plus, depuis la loi du 9 novembre 2010, que pour
   * l'invalidité ; le d rapporte le montant plein, par année de services, à la
   * durée qui ouvre le pourcentage maximum. `dureeMaximum` est ce dénominateur ;
   * `null` garde le c.
   */
  montant(anneeLiquidation, trimestresServices, dureeMaximum = null) {
    const bareme = this.bareme(anneeLiquidation);
    const reference = this.reference(anneeLiquidation);
    if (bareme === null || bareme === undefined || reference === null) {
      return null;
    }
    const [, part, pointsBas, pointsHaut, seuil] = bareme;
    const duree = Math.max(0, Math.min(trimestresServices, MinimumGaranti.SEUIL_HAUT));
    if (duree <= 0) {
      return null;
    }
    let taux;
    if (duree < MinimumGaranti.SEUIL_BAS && dureeMaximum) {
      taux = duree / dureeMaximum;
    } else if (duree < MinimumGaranti.SEUIL_BAS) {
      taux = part * duree / MinimumGaranti.SEUIL_BAS;
    } else if (duree >= MinimumGaranti.SEUIL_HAUT) {
      taux = 1.0;
    } else if (duree < seuil) {
      taux = part + (duree - MinimumGaranti.SEUIL_BAS) * pointsBas;
    } else {
      taux = part + (seuil - MinimumGaranti.SEUIL_BAS) * pointsBas
        + (duree - seuil) * pointsHaut;
    }
    return [reference[0] * taux, reference[1]];
  }
}

/** Quinze ans de services, en trimestres : première marche du barème. */
MinimumGaranti.SEUIL_BAS = 60;
/** Quarante ans : au-delà, la référence est servie en entier. */
MinimumGaranti.SEUIL_HAUT = 160;
/** Année à partir de laquelle la référence est gelée puis indexée sur les prix. */
MinimumGaranti.ANNEE_GEL = 2004;
/** Indice majoré auquel se rapportent les montants transcrits. */
MinimumGaranti.INDICE_REFERENCE = 227;

/**
 * Minimum vieillesse — allocation de solidarité aux personnes âgées (ASPA).
 *
 * Allocation DIFFÉRENTIELLE qui porte les ressources au montant du barème.
 * Ce n'est pas une pension : condition d'âge, de ressources du foyer et de
 * demande, et récupérable sur les successions.
 */
export class MinimumVieillesse {
  constructor(paquet, macro) {
    this.macro = macro;
    this._table = paquet.minimum_vieillesse ?? {};
    this._annees = Object.keys(this._table).map(Number).sort((a, b) => a - b);
    // Le barème d'un couple d'allocataires : l'accueil seul s'en sert.
    this._tableCouple = paquet.minimum_vieillesse_couple ?? {};
  }

  _enVigueur(table, annee) {
    const annees = Object.keys(table).map(Number).sort((a, b) => a - b);
    if (annees.length === 0) {
      return null;
    }
    if (table[String(annee)] !== undefined) {
      return table[String(annee)];
    }
    const anterieures = annees.filter((a) => a < annee);
    const ancre = anterieures.length
      ? anterieures[anterieures.length - 1]
      : annees[0];
    const [valeur, fiabilite] = table[String(ancre)];
    return [valeur * this.macro.coefficientPrix(ancre, annee), fiabilite];
  }

  /** Montant maximal d'une personne seule, l'année demandée. */
  plafond(annee) {
    return this._enVigueur(this._table, annee);
  }

  /** Montant maximal d'un couple d'allocataires, l'année demandée. */
  plafondCouple(annee) {
    return this._enVigueur(this._tableCouple, annee);
  }
}

/** Âge d'ouverture de droit commun de l'ASPA. */
MinimumVieillesse.AGE_OUVERTURE = 65;

/**
 * Trimestres accordés au titre des enfants, dispositif par dispositif.
 *
 * Le module en servait huit par enfant, à tout assuré, à toute date et dans
 * tout régime. Le droit n'en a jamais servi autant : la majoration de durée
 * d'assurance n'existe pas avant 1972, elle vaut un an par enfant jusqu'en
 * 1974, elle est attribuée à la mère, et la fonction publique ne l'applique
 * pas — elle a sa propre bonification, qui vaut un an par enfant né avant 2004
 * et deux trimestres pour les enfants nés depuis.
 *
 * Deux horloges, et la distinction est dans les textes : la MDA se lit à
 * l'ANNÉE DE LIQUIDATION, la bonification à l'ANNÉE DE NAISSANCE DE L'ENFANT.
 */
export class MajorationsPourEnfants {
  constructor(paquet) {
    this._table = paquet.majorations_enfants ?? [];
  }

  /**
   * Trimestres accordés PAR ENFANT, dont ceux qui comptent en SERVICES.
   *
   * Les premiers jouent sur la durée d'assurance, les seconds — qui en sont un
   * sous-ensemble — sur le prorata du régime. Ils ne coïncident que là où le
   * droit accorde une bonification ; une majoration de durée d'assurance rend
   * `services` nul. Voir l'en-tête de
   * `legislation/majoration_duree_assurance.csv`.
   *
   * @returns {[number, number, number]|null} trimestres, services, fiabilité.
   */
  parEnfant(dispositif, sexe, anneeNaissance, anneeLiquidation, nombreEnfants) {
    for (const [code, reference, debut, fin, trimestres, servicesTable,
      servicesDepuis, enfantsMinimum, beneficiaire, fiabilite] of this._table) {
      if (code !== dispositif) {
        continue;
      }
      const annee = reference === "liquidation"
        ? anneeLiquidation
        : anneeNaissance + MajorationsPourEnfants.AGE_PRESUME_A_LA_NAISSANCE;
      if (annee < debut || annee > fin) {
        continue;
      }
      if (beneficiaire === "mere" && sexe !== "F") {
        return null;
      }
      if (nombreEnfants < enfantsMinimum) {
        return null;
      }
      // La part qui compte en services peut n'entrer en vigueur qu'à une
      // SECONDE date, celle de la liquidation, quand la première est celle de
      // la naissance de l'enfant : c'est le cas du b ter de L. 12.
      const services = (servicesDepuis !== null && anneeLiquidation < servicesDepuis)
        ? 0
        : servicesTable;
      return [trimestres, services, fiabilite];
    }
    return null;
  }
}

/**
 * Âge présumé de la mère à la naissance de ses enfants. Le modèle ne collecte
 * pas leur date de naissance ; il la déduit de cette convention, qui est l'âge
 * moyen des mères à l'accouchement.
 */
MajorationsPourEnfants.AGE_PRESUME_A_LA_NAISSANCE = 30;

/**
 * Surcote parentale — article L. 351-1-2-1 du code de la sécurité sociale.
 *
 * Contrepartie du recul de l'âge légal : un assuré qui avait sa durée requise un
 * an avant l'âge légal s'est vu imposer par la loi du 14 avril 2023 une année de
 * travail de plus qui ne lui rapportait rien, la surcote ordinaire ne comptant
 * qu'au-delà de l'âge légal. La loi comble ce trou pour les parents : 1,25 % par
 * trimestre cotisé dans l'année qui précède l'âge légal, quatre au plus, dès
 * que cet âge atteint 63 ans.
 */
export class SurcoteParentale {
  constructor(paquet) {
    this._table = paquet.surcote_parentale ?? [];
  }

  /**
   * @returns {[number, number, number, number]|null} âge légal minimal, taux par
   * trimestre, plafond de trimestres, fiabilité.
   */
  parametres(anneeLiquidation) {
    for (const [debut, fin, age, taux, maximum, fiabilite] of this._table) {
      if (anneeLiquidation >= debut && anneeLiquidation <= fin) {
        return [age, taux, maximum, fiabilite];
      }
    }
    return null;
  }
}

/**
 * Majoration pour enfants de l'Agirc-Arrco, par période d'ACQUISITION des
 * points — portage de `MajorationsEnfantsPoints` : 10 à 30 % pour l'Arrco
 * d'avant 1999, 5 % de 1999 à 2011, 8 à 24 % pour l'Agirc d'avant 2012, 10 %
 * depuis (accord du 17 novembre 2017, article 94).
 */
export class MajorationsEnfantsPoints {
  constructor(paquet) {
    // { régime : [[début, fin, barème, fiabilité], …] }
    this._table = paquet.majoration_enfants_points ?? {};
  }

  /** Taux des points que `regime` a inscrits en `annee`, ou `null`. */
  taux(regime, annee, nombreEnfants) {
    for (const [debut, fin, bareme] of this._table[regime] ?? []) {
      if (annee >= debut && annee <= fin) {
        return bareme[Math.min(nombreEnfants, bareme.length - 1)];
      }
    }
    return null;
  }
}

/**
 * Départ anticipé pour carrière longue — article L. 351-1-1.
 *
 * La principale porte d'entrée avant l'âge légal, et la seule qui se déduise de
 * la carrière elle-même : la pénibilité, l'invalidité et l'inaptitude demandent
 * des informations que le modèle n'a pas.
 */
export class CarriereLongue {
  constructor(paquet) {
    // { date d'effet (année décimale) : [[génération, âge de début maximum,
    //   trimestres de début, âge de départ, trimestres supplémentaires,
    //   fiabilité], …] }
    this._table = paquet.carriere_longue ?? {};
    this._dates = Object.keys(this._table).map(Number).sort((a, b) => a - b);
  }

  /**
   * Les portes opposables à cette carrière : celles du texte en vigueur à sa
   * date d'effet, et pour chaque porte — borne d'entrée ET supplément de
   * trimestres — la ligne de la plus haute génération qui ne dépasse pas la
   * sienne (D. 351-1-1, II). Une borne d'entrée peut ouvrir deux portes :
   * avant 2023, débuter avant seize ans ouvrait cinquante-six ans avec huit
   * trimestres de plus, ou cinquante-huit avec quatre.
   */
  portes(carriere) {
    if (this._dates.length === 0) {
      return null;
    }
    const date = carriere.dateLiquidation;
    const effet = date.annee + (date.mois - 1) / 12.0;
    if (effet < this._dates[0]) {
      return null;
    }
    let applicable = this._dates[0];
    for (const candidate of this._dates) {
      if (candidate > effet + 1e-9) {
        break;
      }
      applicable = candidate;
    }
    const cle = Object.keys(this._table).find((k) => Number(k) === applicable);
    const generation = carriere.generation;
    const retenues = new Map();
    for (const [gen, ageMax, trimestresDebut, ageDepart, supplement, fiabilite]
      of this._table[cle]) {
      if (gen > generation + 1e-9) {
        continue;
      }
      const clePorte = `${ageMax}|${supplement}`;
      const actuelle = retenues.get(clePorte);
      if (actuelle === undefined || gen > actuelle[0]) {
        retenues.set(clePorte, [gen, [ageMax, trimestresDebut, ageDepart, supplement, fiabilite]]);
      }
    }
    return [...retenues.values()].sort((a, b) => a[1][0] - b[1][0]).map(([, porte]) => porte);
  }

  /**
   * La durée cotisée que le dispositif oppose, périodes réputées comprises.
   *
   * Deux listes fermées s'ajoutent aux trimestres réellement cotisés :
   * l'article D. 351-1-2 — service national, incapacité temporaire, chômage
   * indemnisé, maternité, invalidité, AVPF —, chacune sous sa propre limite,
   * que {@link CarriereLongue.reputesAssimiles} tient ; et l'article
   * D. 351-1-2-1, qui répute cotisés jusqu'à deux trimestres de la majoration
   * pour enfants pour les pensions prenant effet au 1er septembre 2026 (LFSS
   * 2026 article 104 ; décret n° 2026-700 ; circulaire Cnav 2026-29, point
   * 1.2.3.8).
   */
  cotisesReputes(carriere, trimestresCotises, trimestresEnfants) {
    const cotises = trimestresCotises + CarriereLongue.reputesAssimiles(carriere);
    if (trimestresEnfants <= 0 || carriere.age_liquidation === null) {
      return cotises;
    }
    if (carriere.dateLiquidation.rang < CarriereLongue.ENFANTS_REPUTES_COTISES_DEPUIS) {
      return cotises;
    }
    return cotises
      + Math.min(CarriereLongue.ENFANTS_REPUTES_COTISES_MAXIMUM, trimestresEnfants);
  }

  /**
   * Ce que les périodes assimilées ajoutent à la durée cotisée.
   *
   * Chaque enveloppe de D. 351-1-2 a son plafond, et deux motifs qui la
   * partagent le partagent : maladie et accident du travail tiennent ensemble
   * dans quatre trimestres. Le budget se consomme dans l'ordre de la carrière,
   * et une enveloppe sans plafond — la maternité — n'en consomme aucun.
   */
  static reputesAssimiles(carriere) {
    const anneeLiquidation = carriere.anneeLiquidation;
    const budgets = new Map();
    let reputes = 0;
    for (const ligne of carriere.lignes) {
      if (ligne.cotise || !ligne.reputes_cotises_enveloppe
          || ligne.annee > anneeLiquidation) {
        continue;
      }
      const retenus = carriere.trimestresRetenus(ligne);
      if (retenus <= 0) {
        continue;
      }
      const plafond = ligne.reputes_cotises_plafond;
      if (!plafond) {
        reputes += retenus;
        continue;
      }
      const restant = budgets.get(ligne.reputes_cotises_enveloppe) ?? plafond;
      const pris = Math.min(retenus, restant);
      budgets.set(ligne.reputes_cotises_enveloppe, restant - pris);
      reputes += pris;
    }
    return reputes;
  }

  /**
   * Âge le plus précoce ouvert par le dispositif, ou ``null``.
   *
   * @returns {[number, number]|null} âge de départ et fiabilité.
   */
  ageDeDepart(carriere, anneeLiquidation, trimestresCotises, requis) {
    const portes = this.portes(carriere);
    if (portes === null) {
      return null;
    }

    let meilleur = null;
    for (const [ageMax, trimestresDebut, ageDepart, supplement, fiabilite] of portes) {
      if (!this.entreePrecoce(carriere, anneeLiquidation, ageMax, trimestresDebut)
          || trimestresCotises < requis + supplement) {
        continue;
      }
      // Départage identique à celui de Python, qui compare des couples
      // (âge, fiabilité) : à âge égal, la fiabilité la plus basse l'emporte.
      if (meilleur === null || ageDepart < meilleur[0]
          || (ageDepart === meilleur[0] && fiabilite < meilleur[1])) {
        meilleur = [ageDepart, fiabilite];
      }
    }
    return meilleur;
  }

  /**
   * Âge le plus précoce que le dispositif ouvrirait à qui continue de cotiser
   * jusqu'à son départ, ou `null`.
   *
   * `ageDeDepart` répond à une liquidation DATÉE ; ici la question est celle
   * qui date un cas type. La condition d'entrée précoce se lit telle quelle ;
   * la condition de durée se projette : il manque `requis + supplément −
   * cotisés` trimestres, et une année de cotisation en rend quatre, la
   * soustraction étant signée. Chaque porte ouvre au plus tardif de son âge et
   * de l'âge où la durée cotisée est réunie, et la plus précoce l'emporte.
   */
  agePropose(carriere, anneeLiquidation, trimestresCotises, requis, ageLiquidation) {
    const portes = this.portes(carriere);
    if (portes === null) {
      return null;
    }
    let meilleur = null;
    for (const [ageMax, trimestresDebut, ageDepart, supplement] of portes) {
      if (!this.entreePrecoce(carriere, anneeLiquidation, ageMax, trimestresDebut)) {
        continue;
      }
      const atteint = ageLiquidation + (requis + supplement - trimestresCotises) / 4.0;
      const candidat = Math.max(ageDepart, atteint);
      if (meilleur === null || candidat < meilleur) {
        meilleur = candidat;
      }
    }
    return meilleur;
  }

  /**
   * La condition d'entrée précoce est-elle remplie pour cette porte ?
   *
   * Cinq trimestres cotisés avant la fin de l'année civile des `ageMax` ans,
   * ou quatre à qui est né au cours du dernier trimestre de l'année civile
   * (D. 351-1-1) : le modèle lit le mois de naissance.
   */
  entreePrecoce(carriere, anneeLiquidation, ageMax, trimestresDebut) {
    const requis = carriere.mois_naissance >= CarriereLongue.MOIS_DERNIER_TRIMESTRE
      ? trimestresDebut - 1 : trimestresDebut;
    // Quatre trimestres au plus par année civile, activités cumulées comprises.
    const parAnnee = new Map();
    for (const ligne of carriere.lignes) {
      if (ligne.cotise && ligne.annee <= carriere.annee_naissance + ageMax
          && ligne.annee < anneeLiquidation) {
        parAnnee.set(ligne.annee,
          (parAnnee.get(ligne.annee) ?? 0) + ligne.trimestres_valides);
      }
    }
    let acquis = 0;
    for (const trimestres of parAnnee.values()) {
      acquis += Math.min(4, trimestres);
    }
    return acquis >= requis;
  }
}

/** Premier mois du dernier trimestre civil : un trimestre de moins est dû. */
CarriereLongue.MOIS_DERNIER_TRIMESTRE = 10;
/** Rang du mois de septembre 2026 : premières pensions où les enfants comptent. */
CarriereLongue.ENFANTS_REPUTES_COTISES_DEPUIS = 2026 * 12 + 8;
CarriereLongue.ENFANTS_REPUTES_COTISES_MAXIMUM = 2;

/**
 * Barème DATÉ de la surcote — D. 351-1-4 du code de la sécurité sociale,
 * L. 14 III du code des pensions. Chaque trimestre de surcote garde le taux en
 * vigueur à la date où il a été accompli ; voir
 * `legislation/surcote_baremes.csv`.
 */
export class SurcoteBaremes {
  constructor(paquet) {
    // [barème, début, fin, rang minimum, après 65 ans, taux, plafond, fiabilité]
    this._lignes = paquet.surcote_baremes ?? [];
  }

  connait(bareme) {
    return this._lignes.some((ligne) => ligne[0] === bareme);
  }

  /**
   * Coefficient de majoration pour ces trimestres de surcote, datés.
   *
   * @param {Array<[DateMois, boolean]>} trimestres premier mois de chaque
   *   trimestre civil de surcote, dans l'ordre, et s'il suit le
   *   soixante-cinquième anniversaire.
   * @returns {[number, number|null]} coefficient et fiabilité.
   */
  coefficient(bareme, trimestres) {
    const servis = new Map();
    let total = 0.0;
    let fiabilite = null;
    trimestres.forEach(([date, apres65], indice) => {
      const rang = indice + 1;
      const valeur = date.annee + (date.mois - 1) / 12.0;
      let meilleure = null;
      this._lignes.forEach((ligne, numero) => {
        const [code, debut, fin, rangMinimum, condition65, taux, maximum, fiab] = ligne;
        if (code !== bareme || !(debut - 1e-9 <= valeur && valeur <= fin + 1e-9)) {
          return;
        }
        if (rang < rangMinimum || (condition65 && !apres65)) {
          return;
        }
        if (maximum !== null && (servis.get(numero) ?? 0) >= maximum) {
          return;
        }
        if (meilleure === null || taux > meilleure[1]) {
          meilleure = [numero, taux, fiab];
        }
      });
      if (meilleure === null) {
        return;
      }
      servis.set(meilleure[0], (servis.get(meilleure[0]) ?? 0) + 1);
      total += meilleure[1];
      fiabilite = fiabilite === null ? meilleure[2] : Math.min(fiabilite, meilleure[2]);
    });
    return [1.0 + total, fiabilite];
  }
}

/**
 * Catalogue des régimes, profils d'affiliation et barèmes du point.
 *
 * Portage de ``src/retraite_notionnelle/donnees/regimes.py``, de la classe
 * ``Affiliations`` de ``carriere.py`` et des deux lecteurs de barèmes de
 * ``scenarios/actuel.py``. Les fiches arrivent déjà normalisées par
 * ``scripts/construire_donnees.py`` : la validation des champs et des familles
 * reste du côté Python, où elle est testée, et n'est pas dupliquée ici.
 */

/**
 * Assiettes reconnues et leur borne exprimée en plafonds de la Sécurité
 * sociale. ``null`` signifie « pas de borne supérieure ».
 */
export const BORNES_ASSIETTE = Object.freeze({
  plafonnee: [0.0, 1.0],
  deplafonnee: [0.0, null],
  tranche_1: [0.0, 1.0],
  tranche_a: [0.0, 1.0],
  tranche_2: [1.0, 8.0],
  // Tranche 2 de l'Arrco d'AVANT la fusion : elle s'arrêtait à trois plafonds,
  // là où celle de l'Agirc-Arrco va jusqu'à huit.
  tranche_2_arrco: [1.0, 3.0],
  // Tranche B de l'Ircantec, et de l'IPACTE avant elle : l'article 7 du décret
  // n° 70-1277 limite l'assiette à 4,75 plafonds, et le décret n° 2008-996 du
  // 23 septembre 2008 la porte à huit.
  tranche_2_ircantec: [1.0, 4.75],
  tranche_b: [1.0, 4.0],
  tranche_c: [4.0, 8.0],
  // Tranches propres au régime de base des professions libérales : la première
  // s'arrêtait à 0,85 plafond avant 2015, la seconde part de zéro depuis — les
  // deux se recouvrent donc, et c'est bien la règle du régime.
  plafonnee_085_pass: [0.0, 0.85],
  tranche_085_5_pass: [0.85, 5.0],
  plafonnee_5_pass: [0.0, 5.0],
  // Complémentaires des indépendants : le revenu y est plafonné à trois
  // plafonds jusqu'en 2004 (D. 635-4), à quatre pour les artisans ensuite
  // (D. 635-7), et la réforme de 2008 y découpe deux tranches — l'article
  // fixe la borne de la première à 33 276 € pour 2008, qui est le plafond
  // de cette année-là.
  plafonnee_3_pass: [0.0, 3.0],
  plafonnee_4_pass: [0.0, 4.0],
  tranche_1_4_pass: [1.0, 4.0],
  // Cipav depuis 2023 : 9 % jusqu'au plafond, 22 % du plafond au triple.
  tranche_1_3_pass: [1.0, 3.0],
  // Cipav en 2024 : la seconde tranche va jusqu'à trois plafonds et demi,
  // puis jusqu'à quatre depuis 2025 (article 2 du décret n° 79-262).
  tranche_1_3_5_pass: [1.0, 3.5],
  // CARPIMKO depuis 2026 : 8,70 % entre un demi et trois plafonds.
  tranche_05_3_pass: [0.5, 3.0],
  // CAVOM depuis 2016 : 12,5 % du revenu, jusqu'à huit plafonds. C'est la
  // borne la plus haute du catalogue libéral, et le décret la fixe en
  // plafonds — 384 480 € en 2026.
  // CAVOM de 2016 à 2019 : quatre plafonds, puis cinq, six et sept
  // (décret n° 2015-1875), huit depuis 2020.
  plafonnee_6_pass: [0.0, 6.0],
  plafonnee_7_pass: [0.0, 7.0],
  plafonnee_8_pass: [0.0, 8.0],
  tranche_1_2_pass: [1.0, 2.0],
  plafonnee_033_pass: [0.0, 0.3333333333333333],
  tranche_033_1_pass: [0.3333333333333333, 1.0],
  // CAVAMAC : le plafond des commissions, que la caisse indexe sur la
  // commission MOYENNE et non sur celui de la Sécurité sociale — 625 777 €
  // en 2026, quand treize plafonds en valent 624 780.
  plafonnee_13_pass: [0.0, 13.0],
  // Complémentaires des sections libérales : la CARMF prélève jusqu'à
  // trois plafonds et demi, le RAAP des artistes-auteurs jusqu'à trois.
  plafonnee_3_5_pass: [0.0, 3.5],
  // Complémentaire des chirurgiens-dentistes : tranche partant de 0,85
  // plafond jusqu'en 2025, de 0,65 depuis la réforme de 2026.
  tranche_065_5_pass: [0.65, 5.0],
  hors_primes: [0.0, null],
  primes_uniquement: [0.0, null],
  forfaitaire: [0.0, null],
  sans_objet: [0.0, null],
});

/** Jeu de paramètres d'un régime sur une plage d'années. */
export class PeriodeRegime {
  constructor(fiche) {
    Object.assign(this, fiche);
  }

  couvre(annee) {
    return this.debut <= annee && (this.fin === null || annee <= this.fin);
  }

  /** Part du taux que l'assuré supporte lui-même. */
  get tauxCotisationSalarie() {
    return this.taux_cotisation_retraite * this.part_salariale;
  }

  bornesAssietteEnPass() {
    return BORNES_ASSIETTE[this.assiette] || [0.0, null];
  }

  /**
   * Bornes de l'assiette EN EUROS de l'année, quelle que soit leur forme.
   *
   * Les bornes en euros priment quand la fiche en porte : un régime qui fixe
   * ses tranches en euros et ne les indexe pas — la complémentaire des avocats,
   * 42 507 € de 2023 à 2026 quand le plafond passait de 43 992 à 48 060 € — ne
   * peut pas être décrit en multiples d'un plafond qui, lui, suit les salaires.
   */
  bornesAssietteEnEuros(pass) {
    const basse = this.borne_basse_euros;
    const haute = this.borne_haute_euros;
    if ((basse !== null && basse !== undefined)
        || (haute !== null && haute !== undefined)) {
      return [basse ?? 0.0, haute ?? null];
    }
    const [borneBasse, borneHaute] = this.bornesAssietteEnPass();
    return [borneBasse * pass, borneHaute === null ? null : borneHaute * pass];
  }

  /** Assiette qui ouvre droit à ``points_maximum`` points. */
  repereAssiette(pass, smicHoraire) {
    if (this.assiette_repere_smic !== null && this.assiette_repere_smic !== undefined) {
      return this.assiette_repere_smic * smicHoraire;
    }
    const [borneBasse, borneHaute] = this.bornesAssietteEnPass();
    return borneHaute === null ? 0.0 : (borneHaute - borneBasse) * pass;
  }

  /** Assiette en deçà de laquelle la cotisation n'est pas appelée. */
  assietteMinimale(pass) {
    if (this.assiette_minimale_pass === null || this.assiette_minimale_pass === undefined) {
      return 0.0;
    }
    return this.assiette_minimale_pass * pass;
  }

  /**
   * Part de la rémunération que ce régime prend en compte : le traitement
   * seul pour la pension civile, les primes seules pour le RAFP — et
   * celles-ci dans la limite de `plafond_primes_traitement` du traitement,
   * 20 % (décret n° 2004-569, art. 2) —, la rémunération entière ailleurs.
   * Le scénario 1 et le compte notionnel découpent tous deux par ici.
   */
  partDuRevenu(revenu, partPrimes) {
    if (this.assiette === "primes_uniquement") {
      const primes = revenu * partPrimes;
      const plafond = this.plafond_primes_traitement;
      if (plafond === null || plafond === undefined) {
        return primes;
      }
      return Math.min(primes, plafond * revenu * (1.0 - partPrimes));
    }
    if (this.assiette === "hors_primes") {
      return revenu * (1.0 - partPrimes);
    }
    return revenu;
  }
}

export class Regime {
  constructor(fiche) {
    Object.assign(this, fiche);
    // Le code du régime est ESTAMPILLÉ sur chaque période, comme le fait le
    // chargeur Python, plutôt que porté par le paquet : une période circule
    // seule dans le moteur — `ageOuverture(periode, carriere)` ne reçoit
    // qu'elle — et certaines règles ont besoin de savoir de quel régime elle
    // vient. Le répéter dans le paquet coûtait cent trente kilo-octets.
    this.periodes = fiche.periodes.map(
      (p) => new PeriodeRegime({ ...p, regime: fiche.code }),
    );
  }

  /**
   * Paramètres applicables une année donnée. Quand plusieurs périodes couvrent
   * la même année — cas des régimes à tranches — la première est retournée.
   */
  periode(annee) {
    return this.periodes.find((p) => p.couvre(annee)) || null;
  }

  periodesActives(annee) {
    return this.periodes.filter((p) => p.couvre(annee));
  }

  /** Le régime accepte-t-il de nouveaux affiliés cette année-là ? */
  ouvert(annee) {
    if (annee < this.creation) {
      return false;
    }
    return !(this.fermeture !== null && annee >= this.fermeture);
  }

  /** Le régime sert-il encore des droits cette année-là ? */
  vivant(annee) {
    if (annee < this.creation) {
      return false;
    }
    return this.extinction === null || annee < this.extinction;
  }
}

export class CatalogueRegimes {
  constructor(paquet) {
    this._regimes = new Map();
    for (const fiche of paquet.regimes) {
      this._regimes.set(fiche.code, new Regime(fiche));
    }
    if (this._regimes.size === 0) {
      throw new Error("aucun régime chargé");
    }
    this.codes = [...this._regimes.keys()].sort();
  }

  obtenir(code) {
    const regime = this._regimes.get(code);
    if (regime === undefined) {
      throw new Error(
        `régime inconnu : ${code}. Régimes disponibles : ${this.codes.join(", ")}`,
      );
    }
    return regime;
  }

  contient(code) {
    return this._regimes.has(code);
  }

  get taille() {
    return this._regimes.size;
  }

  * [Symbol.iterator]() {
    yield* this._regimes.values();
  }

  enRepartition() {
    return [...this].filter((r) => !r.hors_repartition);
  }

  ouverts(annee) {
    return [...this].filter((r) => r.ouvert(annee));
  }

  /**
   * Suit la chaîne d'absorption jusqu'au régime réellement compétent.
   * Exemple : ``organic`` en 2010 renvoie ``rsi`` ; en 2020, ``regime_general``.
   */
  resoudreSuccession(code, annee) {
    const vu = new Set([code]);
    let courant = this.obtenir(code);
    while (courant.extinction !== null && annee >= courant.extinction) {
      const suivant = courant.integre_dans;
      if (suivant === null || suivant === undefined || vu.has(suivant)) {
        break;
      }
      vu.add(suivant);
      courant = this.obtenir(suivant);
    }
    return courant.code;
  }
}

/**
 * Une borne d'entrée du routage, en rang de mois : `2020` se lit janvier 2020,
 * `"2023-09"` septembre 2023. Le YAML garde les deux écritures parce que la
 * loi ferme un régime « aux agents recrutés à compter du 1er septembre 2023 »,
 * et non à compter d'une année.
 */
export function rangBorne(borne) {
  if (typeof borne === "number") {
    return new DateMois(borne, 1).rang;
  }
  const [annee, mois] = String(borne).split("-");
  return new DateMois(Number(annee), Number(mois)).rang;
}

/** « 2020 » pour un 1er janvier, « septembre 2023 » sinon. */
export function formaterBorne(borne) {
  return borne.mois === 1 ? String(borne.annee) : String(borne);
}

/**
 * Les familles de statuts, dans l'ordre où le menu du simulateur les range.
 * Copie de `FAMILLES_STATUT` dans `carriere.py`.
 */
export const FAMILLES_STATUT = Object.freeze({
  prive: "Salariés du privé",
  public: "Fonction publique et militaires",
  independant: "Indépendants et professions libérales",
  agricole: "Agriculture",
  special: "Régimes spéciaux",
  outre_mer: "Outre-mer",
  elus: "Élus et assemblées",
  hors_emploi: "Hors emploi",
});

/** Correspondance statut -> régimes, année par année. */
export class Affiliations {
  constructor(paquet) {
    this._profils = paquet.affiliations;
    if (!this._profils || Object.keys(this._profils).length === 0) {
      throw new Error("aucun profil d'affiliation chargé");
    }
    this.codes = Object.keys(this._profils).sort();
  }

  contient(code) {
    return Object.prototype.hasOwnProperty.call(this._profils, code);
  }

  libelle(code) {
    return this._profils[code].libelle ?? code;
  }

  /** Le groupe du menu où ce statut se range — une clé de FAMILLES_STATUT. */
  famille(code) {
    return this._profils[code].famille;
  }

  /** Les tranches temporelles déclarées par ce statut, telles qu'écrites. */
  periodes(affiliation) {
    return this._profils[affiliation].periodes || [];
  }

  /** Première année que le statut route — l'année où son régime naît. */
  ouverture(affiliation) {
    return Math.min(...this.periodes(affiliation).map((periode) => periode.debut));
  }

  /**
   * Mois depuis lequel le statut est fermé aux nouveaux entrants : la plus
   * ancienne borne `entres_avant` de ses périodes, null pour un statut ouvert.
   * Un jeune d'aujourd'hui ne peut pas se déclarer mineur : le régime des
   * mines est fermé aux recrutés depuis septembre 2010, et c'est cette date
   * que le formulaire lui oppose.
   */
  fermetureEntrants(affiliation) {
    // Seul un statut qui déclare `releve_par` est fermé : celui dont le nom
    // cesse de convenir après la date. Un statut dont les régimes changent
    // pour les nouveaux entrants sans qu'il cesse d'exister — le libéral non
    // réglementé, à la Cipav avant 2019, au régime général et au RCI depuis —
    // reste ouvert.
    if (this.relevePar(affiliation) === null) {
      return null;
    }
    const bornes = this.periodes(affiliation)
      .filter((periode) => periode.entres_avant !== undefined && periode.entres_avant !== null)
      .map((periode) => rangBorne(periode.entres_avant));
    if (bornes.length === 0) {
      return null;
    }
    return DateMois.depuisRang(Math.min(...bornes));
  }

  /** Le statut de droit commun dont relève qui entre après la fermeture. */
  relevePar(affiliation) {
    return this._profils[affiliation].releve_par ?? null;
  }

  /**
   * Ce statut cotise-t-il sans employeur ?
   *
   * Vrai pour les non-salariés. Le drapeau est porté par le STATUT et non par
   * le régime : un artisan cotise au régime général, dont la fiche porte la
   * répartition d'un salarié. Le taux y est le bon ; la répartition, non.
   */
  sansEmployeur(affiliation) {
    return Boolean((this._profils[affiliation] ?? {}).sans_employeur);
  }

  /**
   * Ce statut ne paie-t-il que la part salariale, sans part patronale ?
   *
   * Vrai pour les trois statuts d'auteur : l'auteur paie la cotisation du
   * salarié, à son taux, et personne ne paie celle de l'employeur. C'est
   * l'inverse de `sansEmployeur`, où l'assuré paie les deux ; dans les deux
   * cas, le compte ne porte aucune part patronale.
   */
  partSalarialeSeule(affiliation) {
    return Boolean((this._profils[affiliation] ?? {}).part_salariale_seule);
  }

  /**
   * Classement de l'emploi : "active", "super_active" ou null.
   *
   * Le classement tient à l'EMPLOI, pas à la personne ni au régime : un
   * aide-soignant et un rédacteur territorial cotisent à la même CNRACL, et
   * l'un liquide cinq ans avant l'autre. Aucune donnée de carrière ne permet de
   * le deviner ; c'est donc le statut déclaré qui le porte.
   */
  categorieActive(affiliation) {
    const classement = (this._profils[affiliation] ?? {}).categorie_active ?? null;
    if (classement === null) {
      return null;
    }
    if (classement !== "active" && classement !== "super_active") {
      throw new Error(
        `${affiliation} : classement inconnu ${classement} `
        + "(attendu 'active' ou 'super_active')",
      );
    }
    return classement;
  }

  /**
   * Catégorie militaire : "non_officier", "officier" ou null. Les militaires
   * relèvent du même régime que les fonctionnaires civils de l'État, mais leur
   * pension ne s'ouvre pas à un âge : elle s'ouvre à une durée de services.
   */
  pensionMilitaire(affiliation) {
    const categorie = (this._profils[affiliation] ?? {}).pension_militaire ?? null;
    if (categorie === null) {
      return null;
    }
    if (categorie !== "non_officier" && categorie !== "officier") {
      throw new Error(
        `${affiliation} : catégorie militaire inconnue ${categorie} `
        + "(attendu 'non_officier' ou 'officier')",
      );
    }
    return categorie;
  }

  /** Statuts classés en catégorie active, et leur classement. */
  get classementsActifs() {
    const table = {};
    for (const code of this.codes) {
      const classement = this.categorieActive(code);
      if (classement !== null) {
        table[code] = classement;
      }
    }
    return table;
  }

  /** Statuts militaires, et leur catégorie. */
  get categoriesMilitaires() {
    const table = {};
    for (const code of this.codes) {
      const categorie = this.pensionMilitaire(code);
      if (categorie !== null) {
        table[code] = categorie;
      }
    }
    return table;
  }

  /** Régimes applicables à ce statut cette année-là.
   *
   * LA FERMETURE D'UN RÉGIME NE VAUT QUE POUR LES NOUVEAUX ENTRANTS. Le régime
   * de la SNCF est fermé aux agents recrutés depuis le 1er janvier 2020, celui
   * de la RATP et celui des IEG depuis le 1er septembre 2023 : un agent
   * recruté avant garde le sien jusqu'à sa retraite. `anneeEntree` — l'entrée
   * dans le statut, une année ou un mois (DateMois) — décide ; les bornes
   * s'écrivent au mois quand la loi le fait, et une année vaut son 1er
   * janvier. Sans entrée, on suppose une entrée en janvier de l'année
   * demandée.
   *
   * UN RÉGIME PEUT N'ÊTRE DÛ QU'AU-DELÀ D'UN SEUIL DE REVENU : l'élu local
   * n'est assujetti au régime général qu'au-dessus de la moitié du plafond
   * (L. 382-31). Une période porte alors `seuil_pass: {regime: fraction}` ;
   * avec `revenu` et `plafond`, les régimes sous le seuil sont retirés ;
   * sans eux, la liste des régimes possibles est rendue telle quelle.
   */
  regimes(affiliation, annee, anneeEntree = null, revenu = null, plafond = null) {
    const profil = this._profils[affiliation];
    if (profil === undefined) {
      throw new Error(
        `affiliation inconnue : ${affiliation}. Disponibles : ${this.codes.join(", ")}`,
      );
    }
    let entree;
    if (anneeEntree === null || anneeEntree === undefined) {
      entree = new DateMois(annee, 1).rang;
    } else if (anneeEntree instanceof DateMois) {
      entree = anneeEntree.rang;
    } else {
      entree = new DateMois(Number(anneeEntree), 1).rang;
    }
    for (const periode of profil.periodes || []) {
      const fin = periode.fin ?? null;
      if (!(periode.debut <= annee && (fin === null || annee <= fin))) {
        continue;
      }
      const avant = periode.entres_avant ?? null;
      const depuis = periode.entres_depuis ?? null;
      if (avant !== null && entree >= rangBorne(avant)) {
        continue;
      }
      if (depuis !== null && entree < rangBorne(depuis)) {
        continue;
      }
      let regimes = periode.regimes || [];
      const seuils = periode.seuil_pass || null;
      if (seuils && revenu !== null && revenu !== undefined
          && plafond !== null && plafond !== undefined) {
        regimes = regimes.filter(
          (code) => revenu >= Number(seuils[code] ?? 0.0) * plafond,
        );
      }
      return regimes;
    }
    return [];
  }
}

/**
 * Cotisations PAR CLASSES, pour les régimes qui prélèvent un montant.
 *
 * La Cipav, avant 2023, ne prélevait ni un taux ni un forfait : elle rangeait
 * l'assuré dans un des huit paliers de son barème selon son revenu, et
 * appelait le montant du palier. La classe est SUBIE, pas choisie — la fiche
 * pratique 2022 écrit du complémentaire que « son montant est DÉTERMINÉ selon
 * ce tableau », et de l'invalidité-décès, juste à côté, que l'assuré « a la
 * possibilité de CHOISIR sa classe ».
 *
 * Un seul millésime est publié : pour les autres exercices, c'est la grille la
 * plus récente qui précède, bornes ET montants ramenés par le rapport des
 * plafonds. Le plafond et non les prix, parce que la grille est écrite en
 * plafonds — voir `ClassesCotisation` côté Python.
 */
/**
 * Grilles de salaires forfaitaires par catégorie, régime par régime — voir
 * `SalairesForfaitaires` côté Python. Le régime des marins cotise et liquide
 * sur un forfait par catégorie de fonction à bord, publié chaque année par
 * arrêté ; le moteur range l'assuré dans la catégorie dont le montant est le
 * plus proche de son revenu annualisé. Hors des années publiées, la grille la
 * plus proche est ramenée par le salaire moyen, et le résultat le dit.
 */
export class SalairesForfaitaires {
  constructor(paquet) {
    this._table = new Map();
    for (const [cle, grille] of Object.entries(paquet.salaires_forfaitaires ?? {})) {
      const [regime, annee] = cle.split("|");
      if (!this._table.has(regime)) {
        this._table.set(regime, new Map());
      }
      this._table.get(regime).set(
        Number(annee), [...grille].sort((a, b) => a[1] - b[1]),
      );
    }
  }

  /** @returns {[number, number, number]|null} forfait, catégorie, fiabilité. */
  forfait(regime, annee, revenuAnnuel, indiceSalaire) {
    const grilles = this._table.get(regime);
    if (!grilles || grilles.size === 0) {
      return null;
    }
    let grille;
    let coefficient = 1.0;
    let horsGrille = false;
    if (grilles.has(annee)) {
      grille = grilles.get(annee);
    } else {
      let proche = null;
      for (const a of grilles.keys()) {
        if (proche === null || Math.abs(a - annee) < Math.abs(proche - annee)
            || (Math.abs(a - annee) === Math.abs(proche - annee) && a < proche)) {
          proche = a;
        }
      }
      grille = grilles.get(proche);
      coefficient = indiceSalaire(annee) / indiceSalaire(proche);
      horsGrille = true;
    }
    let meilleur = null;
    for (const [categorie, montant, fiabilite] of grille) {
      const ecart = Math.abs(montant * coefficient - revenuAnnuel);
      if (meilleur === null || ecart < meilleur[0]
          || (ecart === meilleur[0] && categorie < meilleur[1])) {
        meilleur = [ecart, categorie, montant, fiabilite];
      }
    }
    return [
      meilleur[2] * coefficient, meilleur[1],
      horsGrille ? Fiabilite.ESTIMEE : meilleur[3],
    ];
  }
}

export class ClassesCotisation {
  constructor(paquet) {
    this._table = new Map();
    for (const [cle, grille] of Object.entries(paquet.classes_cotisation ?? {})) {
      const [regime, annee] = cle.split('|');
      if (!this._table.has(regime)) {
        this._table.set(regime, new Map());
      }
      this._table.get(regime).set(Number(annee), grille);
    }
  }

  /** @returns {number|null} millésime de la grille applicable à cet exercice. */
  anneeGrille(regime, annee) {
    const grilles = this._table.get(regime);
    if (!grilles) {
      return null;
    }
    const anterieures = [...grilles.keys()].filter((a) => a <= annee);
    return anterieures.length
      ? Math.max(...anterieures)
      : Math.min(...grilles.keys());
  }

  /** @returns {[number, number]|null} montant dû et fiabilité. */
  cotisation(regime, annee, revenu, coefficient = 1.0) {
    const millesime = this.anneeGrille(regime, annee);
    if (millesime === null) {
      return null;
    }
    const grille = this._table.get(regime).get(millesime);
    if (!grille || !grille.length) {
      return null;
    }
    for (const [borne, montant, fiabilite] of grille) {
      if (borne === null || borne === undefined || revenu <= borne * coefficient) {
        return [montant * coefficient, fiabilite];
      }
    }
    const [, montant, fiabilite] = grille[grille.length - 1];
    return [montant * coefficient, fiabilite];
  }
}


/** Rendements instantanés des régimes en points. */
export class Rendements {
  constructor(paquet) {
    this._table = paquet.rendements_points;
  }

  /** @returns {[number, number]} rendement et fiabilité. */
  rendement(regime, annee) {
    for (const [code, debut, fin, valeur, fiabilite] of this._table) {
      if (code === regime && debut <= annee && annee <= fin) {
        return [valeur, fiabilite];
      }
    }
    return [0.0, 0];
  }
}

/**
 * Prix d'achat et valeur de service du point, régime par régime et année.
 *
 * Trois grandeurs suffisent à reconstituer exactement une pension en points :
 * le salaire de référence (prix d'achat du point l'année de la cotisation), le
 * taux d'appel (quelle part de la cotisation ouvre des droits) et la valeur de
 * service (conversion des points en rente à la liquidation).
 */
/**
 * Coefficients de conversion des points, lus et non devinés.
 *
 * Portage de ``ConversionsPoints`` de ``scenarios/actuel.py``. Deux sortes de
 * lignes : celles qui portent un `successeur` décrivent la reprise des points à
 * une fusion ; celles qui n'en portent pas décrivent un changement d'UNITÉ
 * interne au régime — l'unification de l'Arrco au 1er janvier 1999, dont les
 * valeurs d'avant sont celles de l'UNIRS.
 */
//: Niveau de fiabilité maximal, tel que le paquet le code. Ce module n'importe
//: rien : toutes ses valeurs viennent du paquet de données, où les fiabilités
//: sont déjà des entiers.
const FIABILITE_CERTIFIEE = 3;


export class ConversionsPoints {
  constructor(paquet) {
    this._fusions = new Map();
    this._echelles = new Map();
    for (const ligne of paquet.conversions_points ?? []) {
      const [regime, anneeEffet, successeur, coefficient, fiabilite] = ligne;
      const conversion = { anneeEffet, successeur, coefficient, fiabilite };
      if (successeur) {
        this._fusions.set(`${regime}|${successeur}`, conversion);
      } else {
        if (!this._echelles.has(regime)) {
          this._echelles.set(regime, []);
        }
        this._echelles.get(regime).push(conversion);
      }
    }
    for (const conversions of this._echelles.values()) {
      conversions.sort((a, b) => a.anneeEffet - b.anneeEffet);
    }
  }

  /** Coefficient de reprise des points de ``regime`` par ``successeur``. */
  fusion(regime, successeur) {
    return this._fusions.get(`${regime}|${successeur}`) ?? null;
  }

  /** Facteur d'unité entre l'année d'acquisition et celle de liquidation. */
  echelle(regime, anneeAcquisition, anneeLiquidation) {
    let facteur = 1.0;
    let fiabilite = FIABILITE_CERTIFIEE;
    for (const conversion of this._echelles.get(regime) ?? []) {
      if (anneeAcquisition < conversion.anneeEffet
          && conversion.anneeEffet <= anneeLiquidation) {
        facteur *= conversion.coefficient;
        fiabilite = Math.min(fiabilite, conversion.fiabilite);
      }
    }
    return [facteur, fiabilite];
  }
}


export class ValeursPoint {
  constructor(paquet) {
    this._table = new Map();
    for (const [cle, valeurs] of Object.entries(paquet.valeurs_point)) {
      const annees = Object.keys(valeurs).map(Number).sort((a, b) => a - b);
      this._table.set(cle, {
        annees,
        valeurs: annees.map((a) => valeurs[String(a)]),
      });
    }
  }

  /**
   * Dernière valeur publiée à l'année demandée, ou avant elle. Une valeur reste
   * en vigueur jusqu'à sa modification : c'est la règle de lecture d'un barème.
   * Rien n'est renvoyé pour les années antérieures à la première publication.
   */
  _enVigueur(regime, mesure, annee) {
    const table = this._table.get(`${regime}|${mesure}`);
    if (table === undefined) {
      return null;
    }
    let retenu = null;
    for (let i = 0; i < table.annees.length; i += 1) {
      if (table.annees[i] <= annee) {
        retenu = table.valeurs[i];
      } else {
        break;
      }
    }
    return retenu;
  }

  /**
   * Prix d'achat effectif d'un point : [salaire de référence, taux d'appel,
   * fiabilité]. Rien n'est renvoyé au-delà de la dernière année publiée :
   * prolonger le dernier prix connu reviendrait à supposer un barème gelé, les
   * points seraient achetés trop bon marché et la pension surestimée.
   */
  achat(regime, annee) {
    const table = this._table.get(`${regime}|salaire_reference`);
    if (table === undefined || annee > table.annees[table.annees.length - 1]) {
      return null;
    }
    const reference = this._enVigueur(regime, "salaire_reference", annee);
    if (reference === null || reference[0] <= 0) {
      return null;
    }
    const appel = this._enVigueur(regime, "taux_appel", annee);
    const [taux, fiabiliteAppel] = appel !== null ? appel : [1.0, 1];
    return [reference[0], taux, Math.min(reference[1], fiabiliteAppel)];
  }

  derniereAnneeServie(regime) {
    const table = this._table.get(`${regime}|valeur_service`);
    return table === undefined ? null : table.annees[table.annees.length - 1];
  }

  premiereAnneeServie(regime) {
    const table = this._table.get(`${regime}|valeur_service`);
    return table === undefined ? null : table.annees[0];
  }

  service(regime, annee) {
    return this._enVigueur(regime, "valeur_service", annee);
  }
}

/**
 * Contribution employeur des régimes publics, année par année.
 *
 * Portage de ``ContributionsEmployeurPubliques`` du module Python. Les fiches
 * de régime ne portent, pour la fonction publique et les régimes spéciaux, que
 * la retenue de l'agent ; cette table porte l'autre moitié, pour les trois
 * régimes dont elle est publiée — l'État (reconstituée de 1995 à 2005, appelée
 * depuis 2006), la CNRACL (appelée depuis 1948) et la SNCF (2007-2018).
 *
 * Avant la première année d'un régime, la table ne rend rien : il n'y a rien à
 * extrapoler, et l'appelant estime alors la part patronale. Après la
 * dernière, le dernier taux est prolongé, avec la fiabilité d'une projection.
 *
 * L'État a deux taux, un pour ses civils et un pour ses militaires : le second
 * est servi à part, à partir de sa première année, et sa ligne porte un
 * quatrième élément, ``true``. Voir le Python.
 */
export class ContributionsEmployeurPubliques {
  constructor(paquet) {
    this._table = new Map();
    for (const [cle, valeur] of Object.entries(
      paquet.contribution_employeur_public ?? {},
    )) {
      const [regime, annee] = cle.split("|");
      if (!this._table.has(regime)) {
        this._table.set(regime, new Map());
      }
      this._table.get(regime).set(Number(annee), valeur);
    }
    this._bornes = new Map();
    for (const [regime, annees] of this._table) {
      this._bornes.set(regime, ContributionsEmployeurPubliques._bornesDe(annees));
    }
    this._militaires = new Map();
    for (const [annee, [taux, nature, fiabilite]] of Object.entries(
      paquet.contribution_employeur_militaires ?? {},
    )) {
      this._militaires.set(Number(annee), [taux, nature, fiabilite, true]);
    }
    this._bornesMilitaires = this._militaires.size
      ? ContributionsEmployeurPubliques._bornesDe(this._militaires) : null;
  }

  static _bornesDe(annees) {
    const liste = [...annees.keys()].sort((a, b) => a - b);
    return [liste[0], liste[liste.length - 1], liste];
  }

  /** Première et dernière année publiées, ou ``null`` si le régime est absent. */
  couverture(regime) {
    const bornes = this._bornes.get(regime);
    return bornes === undefined ? null : [bornes[0], bornes[1]];
  }

  /** Première et dernière année du taux propre aux militaires. */
  couvertureMilitaires() {
    const bornes = this._bornesMilitaires;
    return bornes === null ? null : [bornes[0], bornes[1]];
  }

  /**
   * Contribution employeur du régime cette année-là. ``militaire`` : pour
   * l'État, et à partir de sa première année, le taux propre aux militaires.
   *
   * @returns {Array|null} taux, nature, fiabilité — et ``true`` en quatrième
   *   position pour une ligne du taux militaire.
   */
  taux(regime, annee, militaire = false) {
    if (militaire && regime === REGIME_DES_MILITAIRES
        && this._bornesMilitaires !== null && annee >= this._bornesMilitaires[0]) {
      return ContributionsEmployeurPubliques._enVigueur(
        this._militaires, this._bornesMilitaires, annee);
    }
    const annees = this._table.get(regime);
    if (annees === undefined) {
      return null;
    }
    return ContributionsEmployeurPubliques._enVigueur(
      annees, this._bornes.get(regime), annee);
  }

  static _enVigueur(annees, [premiere, derniere, liste], annee) {
    if (annees.has(annee)) {
      return annees.get(annee);
    }
    if (annee < premiere) {
      return null;
    }
    if (annee > derniere) {
      const [taux, nature, , militaire] = annees.get(derniere);
      return militaire ? [taux, nature, 0, true] : [taux, nature, 0];
    }
    let applicable = premiere;
    for (const candidate of liste) {
      if (candidate > annee) {
        break;
      }
      applicable = candidate;
    }
    return annees.get(applicable);
  }
}

/** Le régime dont les militaires ont leur propre taux. */
const REGIME_DES_MILITAIRES = "fonction_publique_etat";

/**
 * Ce que paie la contribution de l'État employeur, poste par poste.
 *
 * Portage de ``PartRetraiteSeuleEtat``. La Cour des comptes a décomposé le
 * taux que l'État verse au compte d'affectation spéciale « Pensions » pour
 * 2025, et n'en rattache à la retraite de l'agent lui-même que 44,1 % du
 * traitement pour un civil et 51,2 % pour un militaire. Une seule année est
 * mesurée : ``annee``.
 */
export class PartRetraiteSeuleEtat {
  constructor(paquet) {
    const table = paquet.contribution_etat_retraite_seule ?? null;
    this.annee = table === null ? null : table.annee;
    this.postes = table === null ? [] : table.postes.map(
      ([population, poste, montant, taux]) => ({ population, poste, montant, taux }),
    );
  }

  /** Taux « retraite seule » de l'année mesurée : ``civils`` ou ``militaires``. */
  taux(population) {
    for (const poste of this.postes) {
      if (poste.population === population && poste.poste === "retraite_stricto_sensu") {
        return poste.taux;
      }
    }
    throw new Error(`population inconnue : ${population}`);
  }
}
