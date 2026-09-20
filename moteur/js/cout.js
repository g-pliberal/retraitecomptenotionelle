/**
 * Le coût des six systèmes : ce qu'il a été depuis 1959, ce qu'il serait d'ici 2070.
 *
 * Portage de ``src/retraite_notionnelle/cout.py``. Deux temps, qui n'ont pas le
 * même statut et qu'il ne faut jamais confondre.
 *
 * LE PASSÉ
 *     coût du système S en t = dépense OBSERVÉE en t × (masse S / masse actuelle)
 * La dépense vient de la DREES et n'est pas modélisée ; seul le RAPPORT l'est.
 *
 * L'AVENIR
 *     coût du système S en t = ancrage × masse S en t
 *     ancrage = dépense de répartition observée en 2024 ÷ masse actuelle en 2024
 * Les deux expressions coïncident exactement en 2024 : les courbes ne sautent
 * pas au passage. Ce qui les fait bouger ensuite est la pyramide des âges de
 * l'INSEE et les pensions que chaque génération acquiert sous chaque système.
 *
 * Le poids d'une génération une année donnée est son EFFECTIF RÉEL, lu dans les
 * projections de population. Chaque génération de la grille en représente cinq,
 * parcourues une à une, chacune liquidant sa propre année.
 *
 * CE QUE CHAQUE CAS TYPE PÈSE
 * Les douze cas types ont longtemps pesé d'un poids ÉGAL, faute de source : il y
 * a près de cent fois moins de retraités à la SNCF qu'à la Cnav, et les départs
 * très précoces, que le notionnel pénalise le plus, étaient surreprésentés.
 * Chacun porte désormais l'effectif des retraités de sa caisse, publié par la
 * DREES et lu année par année. L'ancienne convention reste disponible —
 * ``ponderation = "egale"`` — pour dire de combien elle déplaçait les résultats.
 *
 * LE SOLDE, ET NON LE COÛT
 * Un coût n'est pas un solde. Le second terme du bilan vient du COR, seul à
 * consolider dépenses ET ressources du système de retraite sur un même
 * périmètre (``equilibre.js`` dit pourquoi ce n'est pas la DREES) :
 *     solde du système S = ressources observées − dépenses du COR × rapport S
 *     coefficient d'équilibre de S = ressources ÷ (dépenses × rapport S)
 * Le coefficient est le facteur par lequel multiplier TOUTES les pensions du
 * système S pour que l'année tombe juste. Le modèle le calcule ; il ne
 * l'applique jamais.
 */

import {
  CAS_TYPES, VARIANTES_LIQUIDATION, calculerCasTypes, poidsEffectifs, poidsEgaux,
} from "./castypes.js";
import { coutGarantie, manqueMoyen } from "./garantie.js";
import { DistributionPensions } from "./distribution.js";
import { Fiabilite } from "./serie.js";
import { ORGANISMES, POSTES } from "./equilibre.js";

/** Les six systèmes, dans l'ordre du tableau de comparaison. */
export const SCENARIOS = [
  ["actuel", "1. Système actuel"],
  ["notionnel_retroactif", "2. Notionnel rétroactif, part salariale"],
  ["notionnel_prospectif", "3. Notionnel dès la bascule, part salariale"],
  ["notionnel_retroactif_employeur",
    "4. Notionnel rétroactif, avec la part patronale"],
  ["notionnel_prospectif_employeur",
    "5. Notionnel dès la bascule, avec la part patronale"],
  ["notionnel_liberal",
    "6. Notionnel rétroactif, 18 % dès la bascule, garantie vieillesse"],
];

/**
 * La part du scénario 6 que l'IMPÔT finance : la garantie vieillesse, portée à
 * part de la pension contributive. Une composante d'un système, pas un système :
 * elle a sa masse et son rapport comme les autres, mais n'entre dans aucun
 * tableau de comparaison comme une ligne à part entière.
 */
export const COMPOSANTE_GARANTIE = "garantie_vieillesse_liberal";

/**
 * Ce que la garantie REGARDE, cas type par cas type : la pension contributive
 * du scénario 6 et la rente du pilier capitalisé, comptées à partir de
 * soixante-cinq ans et revalorisées jusqu'à l'année. Ni un système ni une
 * composante : la masse par laquelle la distribution des pensions est DÉPLACÉE
 * avant qu'on lui applique le plancher — voir `GarantieDistribution`.
 */
export const RESSOURCES_GARANTIE = "ressources_garantie_liberal";

/** Tout ce que la grille sait calculer : les six systèmes, et ces ressources. */
export const CLES_CAS_TYPES = [...SCENARIOS.map(([scenario]) => scenario), RESSOURCES_GARANTIE];

/** Les deux comptes de TÊTES que la grille rend avec ses masses. */
const TETES_TOUTES = "toutes";
const TETES_GARANTIE = "garantie";

/** Tout ce dont une masse est calculée : les six systèmes, et la composante. */
export const CLES_MASSES = [...SCENARIOS.map(([scenario]) => scenario), COMPOSANTE_GARANTIE];

/**
 * Les deux BARÈMES DE PRÉLÈVEMENT dont une masse de cotisations est calculée.
 *
 * Ils ne sont que deux parce qu'un seul scénario change ce qui est PRÉLEVÉ : le
 * 6, qui remplace tous les taux par 18 % à compter de la bascule. Les scénarios
 * 2 à 5 changent ce qui est PORTÉ AU COMPTE — la part salariale seule, ou les
 * deux parts — et non ce que la paie supporte : l'employeur verse toujours sa
 * part, elle finance toujours le système, et elle n'ouvre simplement plus de
 * droit à celui qui la voit passer.
 */
export const TAUX_REELS = "taux_reels";
export const CLES_RECETTES = [TAUX_REELS, "notionnel_liberal"];

/**
 * Les deux façons d'établir la recette du scénario 6, et elles ne posent pas
 * la même question.
 *
 * `assiette` applique son taux de 18 % à l'ASSIETTE MESURÉE des revenus
 * d'activité, et ne reconduit aucune ressource non contributive. C'est la
 * convention du programme : un compte notionnel ne crédite que ce qui est
 * assis sur un revenu d'activité.
 *
 * `rapport` est l'ancienne convention, gardée pour mesurer ce qu'elle valait :
 * elle multipliait la part cotisée des ressources OBSERVÉES par le rapport de
 * deux taux LÉGAUX, et ne retirait aucun des trois postes non contributifs.
 */
export const CONVENTION_ASSIETTE = "assiette";
export const CONVENTION_RAPPORT = "rapport";
export const CONVENTIONS_RECETTE = [CONVENTION_ASSIETTE, CONVENTION_RAPPORT];

/**
 * CE QUE LES SCÉNARIOS NOTIONNELS FONT DE LA RÉVERSION, et il fallait le dire.
 *
 * Le modèle ne calcule aucune pension de réversion : elle concerne le conjoint
 * survivant et non l'assuré. Le rapport de masses par lequel un scénario fait
 * réagir la dépense ne décrit donc que les droits DIRECTS, et il s'appliquait
 * pourtant à une base qui porte les deux.
 *
 * `supprimee` est la convention du dépôt, et elle n'est pas un choix de plus :
 * elle est la RÈGLE DÉJÀ APPLIQUÉE aux trente-huit autres lignes. Les
 * scénarios 2 à 6 retirent tous les avantages non contributifs, et
 * l'inventaire du dépôt range la réversion parmi eux depuis toujours : non
 * contributive au sens strict, la cotisation de l'assuré ayant déjà été rendue
 * par sa propre pension, et de très loin la PREMIÈRE dépense non contributive
 * du système. C'est le chemin de la Suède, où un compte notionnel ne verse
 * qu'à son titulaire.
 *
 * `servie` reste calculable : c'est le chemin de l'Italie, où le capital
 * notionnel du défunt se partage.
 *
 * LE SCÉNARIO 1 SERT LA RÉVERSION DANS TOUS LES CAS : il est le droit en
 * vigueur, et le droit en vigueur la sert.
 */
export const CONVENTION_REVERSION_SERVIE = "servie";
export const CONVENTION_REVERSION_SUPPRIMEE = "supprimee";
export const CONVENTIONS_REVERSION = [
  CONVENTION_REVERSION_SERVIE, CONVENTION_REVERSION_SUPPRIMEE,
];

/**
 * LE BILAN, POSTE PAR POSTE. Le COR publie la structure des ressources en
 * sept lignes ; `SoldeAnnuel.postesRessources` rend la même chose pour CHAQUE
 * système, en part de PIB, en appliquant à chaque poste la règle que
 * `ressourcesDe` applique au total : les deux se somment exactement. Les six
 * premiers codes sont ceux d'`equilibre.POSTES` ; les « dont » ventilent le
 * poste des transferts par celui qui paie, et l'impôt par ce qu'en verse le
 * fonds de solidarité vieillesse.
 */
export const POSTES_RESSOURCES = POSTES.map((poste) => poste.code);
export const DONT_TRANSFERTS = ["transferts_famille", "transferts_chomage", "transferts_autres"];
export const DONT_IMPOTS = ["impots_solidarite", "impots_autres"];

/**
 * Ce qu'un système verse, en trois lignes que `masseDuScenario` sépare déjà
 * sans les nommer : droit direct, réversion, et la garantie vieillesse —
 * financée par l'impôt, hors du compte des cotisants, redite pour mémoire.
 */
export const POSTES_DEPENSES = ["droits_directs", "droits_derives", "garantie_vieillesse"];

/**
 * Applique un rapport de masses à une base, et au seul morceau qu'il décrit.
 *
 * LE RAPPORT NE DÉCRIT QUE LES DROITS DIRECTS : il est le quotient de deux
 * masses calculées sur les treize cas types, qui n'ont ni conjoint ni
 * survivant. La base, elle, porte les deux — un huitième de réversion en 2010,
 * un dixième en 2024, un dix-huitième en 2070. Le rapport ne multiplie donc
 * que la part directe, et la part dérivée suit la convention du scénario — que
 * le dépôt fixe à « supprimée », la réversion étant un avantage non
 * contributif de plus.
 *
 * `reformeEnVigueur` ne sert qu'aux réformes PROSPECTIVES : elles sont, par
 * construction, le système actuel jusqu'à leur bascule, et y servent donc sa
 * réversion. À compter de la bascule elles ne la servent plus, à personne. Les
 * réformes rétroactives recalculent tout le monde depuis 1941 : le drapeau ne
 * les concerne pas.
 *
 * Deux cas à part : le système actuel rend sa base sans rien y toucher, étant
 * le droit en vigueur ; et la garantie vieillesse, qui n'est pas un système
 * mais une allocation différentielle calculée elle aussi sur les seuls droits
 * directs, ne reçoit aucune réversion.
 */
export function masseDuScenario(base, partDerives, rapport, scenario,
                                reversionServie = false, reformeEnVigueur = true) {
  if (scenario === "actuel") return base;
  const directe = base * (1 - partDerives) * rapport;
  if (scenario === COMPOSANTE_GARANTIE) return directe;
  if (reversionServie) return directe + base * partDerives;
  // Avant sa bascule, une réforme prospective EST le système actuel : elle en
  // sert la réversion comme le reste. Après, elle ne la sert plus, à personne.
  if (CLES_PROSPECTIVES.has(scenario) && !reformeEnVigueur) {
    return directe + base * partDerives;
  }
  return directe;
}

/**
 * Première génération dont une liquidation puisse tomber après le début de la
 * répartition (1941). En deçà, le modèle refuse — à juste titre — de calculer.
 */
export const PREMIERE_GENERATION = 1880;

/** Dernière génération retenue : née en 2015, elle liquide au plus tôt en 2067. */
export const DERNIERE_GENERATION = 2015;

/**
 * Pas de la grille de générations. Chaque génération retenue représente les
 * cinq classes d'âge qui l'entourent, dont elle porte l'effectif.
 */
export const PAS_GENERATIONS = 5;

/** Dernière année que les projections de population de l'INSEE couvrent. */
export const HORIZON = 2070;

/** Âge auquel le rapport de dépendance démographique compte les « vieux ». */
export const AGE_DEPENDANCE = 65;

export function generations() {
  const liste = [];
  for (let g = PREMIERE_GENERATION; g <= DERNIERE_GENERATION; g += PAS_GENERATIONS) {
    liste.push(g);
  }
  return liste;
}

/** Demi-largeur de la tranche d'âges qu'une génération de la grille représente. */
export const DEMI_TRANCHE = Math.floor(PAS_GENERATIONS / 2);

/**
 * Les deux pondérations possibles des cas types. `effectifs` est celle des
 * résultats affichés ; `egale` est l'ancienne convention, gardée pour mesurer ce
 * qu'elle valait.
 */
export const PONDERATIONS = ["effectifs", "egale"];

/**
 * Les deux côtés d'un bilan, et l'effectif qui pèse un cas type de chaque côté :
 * ses RETRAITÉS pour une masse de pensions, ses COTISANTS pour une masse de
 * cotisations. Un même mode de pondération se lit des deux côtés.
 */
export const COTE_RETRAITES = "retraites";
export const COTE_COTISANTS = "cotisants";
export const COTES = [COTE_RETRAITES, COTE_COTISANTS];

/**
 * Les deux façons de dater le départ des cas types, reprises de `castypes.js`.
 * `droit` est celle des résultats affichés ; `absolu` est l'ancienne, où toutes
 * les générations partaient à l'âge écrit dans la grille.
 */
export const LIQUIDATIONS = VARIANTES_LIQUIDATION;

/** Simule la grille et en tire, pour chaque couple, sa pension par système. */
function pensionnes(simulateur, casTypes, liquidation = "droit") {
  const grille = calculerCasTypes(simulateur, casTypes, generations(), liquidation);
  const liste = [];
  for (const [cle, comparaison] of grille.resultats) {
    const pensions = {};
    for (const [scenario] of SCENARIOS) {
      pensions[scenario] = comparaison.enEurosConstants(
        comparaison[scenario].pension_annuelle,
      );
    }
    // Ce que la garantie regarde : la pension contributive ET la rente du
    // pilier capitalisé, à la liquidation. La grille ne chiffre plus le
    // complément — elle n'a pas de queue basse —, elle dit seulement de combien
    // les pensions du scénario 6 déplacent la distribution observée.
    pensions[RESSOURCES_GARANTIE] = comparaison.enEurosConstants(
      comparaison.notionnel_liberal.garantie_vieillesse.ressources,
    );
    // La clé de la grille est « code|génération » : la génération en est la
    // seconde moitié, et c'est elle qui dit quel âge ce couple a chaque année.
    // Ce que cette carrière VERSE, année par année, sous les deux barèmes. Le
    // dénominateur ne peut pas être le compte du scénario 4 : celui-là fusionne
    // les régimes à la bascule et prélève ensuite le taux du statut pivot privé
    // pour tout le monde, ce qui est déjà une réforme. On redemande donc le
    // même compte SANS régime fusionné, c'est-à-dire ce que le droit en vigueur
    // prélèverait sur la même carrière jusqu'en 2070.
    const versements = { [TAUX_REELS]: {}, notionnel_liberal: {} };
    const reels = simulateur.constructeurEmployeur.construire(
      comparaison.carriere,
      comparaison.carriere.anneeLiquidation,
      comparaison.carriere.premiereAnnee,
    );
    for (const ligne of reels.cotisations) {
      versements[TAUX_REELS][ligne.annee] = ligne.cotisation;
    }
    for (const ligne of comparaison.notionnel_liberal.compte.cotisations) {
      versements.notionnel_liberal[ligne.annee] = ligne.cotisation;
    }
    // Le scénario 6 est ramené à sa part CONTRIBUTIVE : la garantie est
    // financée par l'impôt, elle ne pèse pas sur le compte des cotisants.
    pensions.notionnel_liberal = comparaison.enEurosConstants(
      comparaison.notionnel_liberal.garantie_vieillesse.pension_contributive,
    );
    liste.push({
      // Le code du cas type est la première moitié de la clé : c'est par lui
      // que le couple reçoit son poids.
      code: cle.slice(0, cle.indexOf("|")),
      generation: Number(cle.slice(cle.indexOf("|") + 1)),
      anneeLiquidation: comparaison.carriere.anneeLiquidation,
      // Avant 65 ans, on ne touche pas le minimum vieillesse : la composante
      // n'entre qu'à cette date, même pour qui est parti plus tôt.
      anneeOuvertureGarantie:
        comparaison.notionnel_liberal.garantie_vieillesse.annee_ouverture,
      pensions,
      cotisations: versements,
      pilier: fluxPilier(comparaison),
      rentePilier: rentePilier(comparaison),
    });
  }
  const motifs = new Map();
  for (const motif of grille.echecs.values()) {
    motifs.set(motif, (motifs.get(motif) || 0) + 1);
  }
  return { liste, motifs };
}

/** Les flux annuels du pilier capitalisé d'une carrière, en euros courants :
 * versement brut, frais sur versement, frais de gestion, encours. */
function fluxPilier(comparaison) {
  const pilier = comparaison.notionnel_liberal.capitalisation;
  const flux = {};
  if (!pilier || !pilier.actif) return flux;
  for (const annee of pilier.annees) {
    flux[annee.annee] = [annee.versement_brut, annee.frais_versement,
      annee.frais_gestion, annee.encours];
  }
  return flux;
}

/** La rente du pilier d'une carrière, brute puis nette de ses frais. */
function rentePilier(comparaison) {
  const pilier = comparaison.notionnel_liberal.capitalisation;
  if (!pilier || !pilier.actif) return [0.0, 0.0];
  return [pilier.capital / pilier.conversion.diviseur, pilier.rente_annuelle];
}

/**
 * Le pilier capitalisé de TOUS les cotisants, une année, PAR EURO VERSÉ.
 * Portage de `PilierAnnuel` dans `cout.py` : la grille ne donne que des
 * rapports, le niveau vient des cotisations du système 4 ancrées sur le
 * compte du COR, et `niveaux` fait le produit.
 */
export class PilierAnnuel {
  constructor(annee, rapports) {
    this.annee = annee;
    this.frais_versement = rapports.frais_versement;
    this.frais_gestion = rapports.frais_gestion;
    this.encours = rapports.encours;
    this.rentes_brutes = rapports.rentes_brutes;
    this.rentes = rapports.rentes;
  }

  get frais_accumulation() { return this.frais_versement + this.frais_gestion; }

  get frais_rentes() { return this.rentes_brutes - this.rentes; }

  /** Tout ce que l'enveloppe prélève dans l'année, par euro versé. */
  get frais() { return this.frais_accumulation + this.frais_rentes; }

  /** Les frais de gestion de l'année rapportés à l'encours. */
  get taux_frais_encours() {
    return this.encours > 0 ? this.frais_gestion / this.encours : 0.0;
  }

  /** Chaque grandeur au niveau des `versements` donnés, même unité. */
  niveaux(versements) {
    return {
      versements,
      frais_versement: this.frais_versement * versements,
      frais_gestion: this.frais_gestion * versements,
      frais_accumulation: this.frais_accumulation * versements,
      encours: this.encours * versements,
      rentes_brutes: this.rentes_brutes * versements,
      rentes: this.rentes * versements,
      frais_rentes: this.frais_rentes * versements,
      frais: this.frais * versements,
    };
  }
}

/**
 * Ce que le pilier capitalisé de TOUS les cotisants encaisse, prélève, détient
 * et sert une année donnée, en euros courants. Portage de `_masses_pilier`.
 */
function massesPilier(liste, population, annee, poidsCotisants, poidsRetraites) {
  const total = {
    versements: 0.0, frais_versement: 0.0, frais_gestion: 0.0, encours: 0.0,
    rentes_brutes: 0.0, rentes: 0.0,
  };
  for (const pensionne of liste) {
    if (!pensionne.pilier || Object.keys(pensionne.pilier).length === 0) continue;
    const partCotisants = poidsCotisants[pensionne.code] || 0;
    const partRetraites = poidsRetraites[pensionne.code] || 0;
    for (let decalage = -DEMI_TRANCHE; decalage <= DEMI_TRANCHE; decalage += 1) {
      const poids = population.effectif(annee - pensionne.generation - decalage, annee);
      if (poids <= 0) continue;
      // L'année CIVILE de la grille, non son âge : un pilier dépend de dates
      // (la bascule, les paliers), voir `_masses_pilier` dans cout.py.
      const flux = pensionne.pilier[annee];
      if (flux !== undefined && partCotisants > 0
          && annee <= pensionne.anneeLiquidation + decalage) {
        total.versements += partCotisants * poids * flux[0];
        total.frais_versement += partCotisants * poids * flux[1];
        total.frais_gestion += partCotisants * poids * flux[2];
        total.encours += partCotisants * poids * flux[3];
      }
      if (annee > pensionne.anneeLiquidation + decalage && partRetraites > 0) {
        total.rentes_brutes += partRetraites * poids * pensionne.rentePilier[0];
        total.rentes += partRetraites * poids * pensionne.rentePilier[1];
      }
    }
  }
  return total;
}

/**
 * Les masses que la revalorisation des pensions SERVIES atteint : les cinq
 * scénarios notionnels, et eux seuls. Le scénario 1 en est exclu parce que le
 * droit l'indexe sur les prix — article L. 161-23-1 du code de la sécurité
 * sociale, qui renvoie au coefficient de l'article L. 161-25 —, et la garantie
 * vieillesse parce que l'article L. 816-2 renvoie l'ASPA au même coefficient.
 * C'est cette asymétrie qui fait tout : une règle commune se simplifierait dans
 * le rapport de masses, celle-ci ne se simplifie pas.
 */
export const CLES_REVALORISEES = new Set(
  SCENARIOS.map(([scenario]) => scenario).filter((scenario) => scenario !== "actuel"),
);

/**
 * Les scénarios 3 et 5, dont la règle d'indexation NE COMMENCE QU'À LA BASCULE.
 * Une réforme prospective ne gèle pas l'indexation du stock : elle change la
 * règle pour toutes les pensions à compter du jour où elle s'applique, celles
 * déjà servies comprises. Ce qu'elle ne fait pas, c'est agir avant elle-même.
 * D'où `max(liquidation, bascule)` et non « liquidée après la bascule ».
 */
export const CLES_PROSPECTIVES = new Set([
  "notionnel_prospectif", "notionnel_prospectif_employeur",
]);

/**
 * Ce que devient une pension DÉJÀ LIQUIDÉE, année après année.
 *
 * Portage de `RevalorisationServie` dans `cout.py`, dont le raisonnement est
 * écrit en entier. En deux phrases : un système notionnel a DEUX règles
 * d'indexation — le compte pendant la carrière, la pension une fois servie —,
 * et le dépôt n'en portait qu'une, les masses figeant la pension en euros
 * constants pour toute la retraite. C'était une indexation sur les prix qui ne
 * disait pas son nom, correcte pour le scénario 1 où c'est la loi, fausse pour
 * les cinq autres, dont le diviseur de conversion suppose déjà que la rente
 * suit le taux qui a fait grossir le compte.
 */
export class RevalorisationServie {
  constructor(simulateur, premiereAnnee, derniereAnnee) {
    const macro = simulateur.macro;
    const indexation = simulateur.indexation;
    // L'année à partir de laquelle une réforme PROSPECTIVE revalorise ce
    // qu'elle sert : voir CLES_PROSPECTIVES.
    this.anneeBascule = simulateur.parametres.annee_bascule;
    // Le stock à la bascule garde-t-il les prix ? Voir `coefficientStock`.
    this.stockSurLesPrix = simulateur.parametres.revalorisation_stock === "prix";
    this.premiereAnnee = premiereAnnee;
    this.derniereAnnee = Math.max(derniereAnnee, premiereAnnee);
    let index = 1;
    this._index = new Map([[this.premiereAnnee, index]]);
    for (let annee = this.premiereAnnee + 1; annee <= this.derniereAnnee; annee += 1) {
      // Le taux d'indexation est NOMINAL, les masses sont en euros constants :
      // on le déflate année par année, et non en bloc.
      index *= (1 + indexation.taux(annee).taux) * macro.coefficientPrix(annee, annee - 1);
      this._index.set(annee, index);
    }
  }

  _valeur(annee) {
    const borne = Math.min(Math.max(annee, this.premiereAnnee), this.derniereAnnee);
    return this._index.get(borne);
  }

  /**
   * Ce que vaut en `annee`, en euros constants, un euro de pension liquidé en
   * `anneeLiquidation`. Vaut exactement 1 l'année de la liquidation et avant.
   */
  coefficient(anneeLiquidation, annee) {
    if (annee <= anneeLiquidation) return 1;
    const depart = this._valeur(anneeLiquidation);
    return depart ? this._valeur(annee) / depart : 1;
  }

  /**
   * Le même coefficient, avec la règle du STOCK à la bascule — portage de
   * `coefficient_stock`. Une pension liquidée à compter de la bascule suit la
   * règle du compte depuis sa liquidation. Liquidée avant : sous `prix`, elle
   * garde les prix à compter de la bascule (1 depuis toujours pour une réforme
   * prospective, coefficient gelé à la bascule pour une rétroactive) ; sous
   * `reindexe`, la prospective la prend à sa règle le jour de la bascule, la
   * rétroactive l'a toujours revalorisée sur la sienne.
   */
  coefficientStock(anneeLiquidation, annee, prospectif) {
    const bascule = this.anneeBascule;
    if (anneeLiquidation >= bascule) return this.coefficient(anneeLiquidation, annee);
    if (this.stockSurLesPrix) {
      if (prospectif) return 1;
      return this.coefficient(anneeLiquidation, Math.min(annee, bascule));
    }
    if (prospectif) return this.coefficient(bascule, annee);
    return this.coefficient(anneeLiquidation, annee);
  }
}

/**
 * Masse de pensions par système, une année donnée, et le nombre de couples.
 *
 * Les cinq cohortes que représente une génération de la grille sont parcourues
 * une à une : chacune porte l'effectif réel de sa classe d'âge et liquide sa
 * propre année. Les faire basculer le même jour ferait avancer la trajectoire
 * par marches de cinq ans au lieu de la faire monter.
 */
function masses(liste, population, annee, poidsCas, revalorisation) {
  const total = {};
  for (const cle of CLES_CAS_TYPES) total[cle] = 0;
  const tetes = { [TETES_TOUTES]: 0, [TETES_GARANTIE]: 0 };
  let vivants = 0;
  for (const pensionne of liste) {
    // Deux pondérations se composent ici : celle de la GÉNÉRATION, démographique,
    // et celle du CAS TYPE, sociologique — combien de retraités ont eu cette
    // carrière-là.
    const part = poidsCas[pensionne.code] || 0;
    if (part <= 0) continue;
    let poids = 0;
    let poidsGarantie = 0;
    let poidsGarantieRevalorise = 0;
    let poidsRevalorise = 0;
    let poidsRevaloriseProspectif = 0;
    for (let decalage = -DEMI_TRANCHE; decalage <= DEMI_TRANCHE; decalage += 1) {
      const liquidation = pensionne.anneeLiquidation + decalage;
      if (annee < liquidation) continue;
      const effectif = population.effectif(annee - pensionne.generation - decalage, annee);
      poids += effectif;
      // Le troisième poids porte la revalorisation des pensions SERVIES, et il
      // faut qu'il soit à part : le coefficient dépend de l'année de
      // liquidation, qui n'est pas la même pour les cinq cohortes de la tranche.
      poidsRevalorise += effectif * revalorisation.coefficientStock(liquidation, annee, false);
      poidsRevaloriseProspectif += effectif * revalorisation.coefficientStock(
        liquidation, annee, true,
      );
      // La garantie n'entre qu'à 65 ans, même pour qui est parti plus tôt.
      if (annee >= pensionne.anneeOuvertureGarantie + decalage) {
        poidsGarantie += effectif;
        poidsGarantieRevalorise += effectif * revalorisation.coefficient(liquidation, annee);
      }
    }
    if (poids <= 0) continue;
    vivants += 1;
    tetes[TETES_TOUTES] += part * poids;
    tetes[TETES_GARANTIE] += part * poidsGarantie;
    for (const cle of CLES_CAS_TYPES) {
      let poidsCle = poids;
      if (cle === RESSOURCES_GARANTIE) poidsCle = poidsGarantieRevalorise;
      else if (CLES_PROSPECTIVES.has(cle)) poidsCle = poidsRevaloriseProspectif;
      else if (CLES_REVALORISEES.has(cle)) poidsCle = poidsRevalorise;
      total[cle] += part * poidsCle * pensionne.pensions[cle];
    }
  }
  return { total, vivants, tetes };
}

/**
 * Ce que la garantie vieillesse coûte chaque année, lu sur la distribution.
 *
 * Portage de `GarantieDistribution` : le barème est appliqué à la distribution
 * des pensions de l'EIR, et la grille ne sert qu'à dire de combien cette
 * distribution BOUGE — un seul facteur, la pension moyenne que la garantie
 * regarde en `t` sur la pension moyenne du système actuel l'année de l'enquête,
 * l'une et l'autre par tête et en euros constants. L'effectif suit les têtes de
 * soixante-cinq ans et plus ; le plancher est celui des paramètres, dans les
 * euros de l'enquête. La forme de la distribution est tenue constante : on la
 * déplace, on ne la déforme pas.
 */
class GarantieDistribution {
  constructor(distribution, plancherMensuel, pensionReference, effectifParTete,
              versConstants, tauxRecours = 1.0) {
    if (!(tauxRecours > 0 && tauxRecours <= 1)) {
      throw new RangeError("le taux de recours est une part, entre zéro exclu et un");
    }
    this.distribution = distribution;
    // Part des ayants droit qui réclament la garantie.
    this.tauxRecours = tauxRecours;
    this.plancherMensuel = plancherMensuel;
    this.pensionReference = pensionReference;
    this.effectifParTete = effectifParTete;
    this.versConstants = versConstants;
  }

  /** La garantie d'une année, d'après les masses et les têtes de la grille. */
  chiffrer(total, tetes) {
    const tetesGarantie = tetes[TETES_GARANTIE];
    const vide = { facteur: 0, effectif: 0, beneficiaires: 0, coutConstants: 0,
                   ayantsDroit: 0, tauxRecours: 1.0, avancesLibereesConstants: 0,
                   reprisesConstants: 0, stockAvancesConstants: 0, tauxReel: 0,
                   partReprise: 0, dureeAvances: 0, populationMortalite: null,
                   partFemmes: 0 };
    if (tetesGarantie <= 0 || this.pensionReference <= 0) return vide;
    const facteur = total[RESSOURCES_GARANTIE] / tetesGarantie / this.pensionReference;
    if (facteur <= 0) return vide;
    const effectif = this.effectifParTete * tetesGarantie;
    const chiffre = coutGarantie(this.distribution, effectif, this.plancherMensuel, facteur);
    return {
      facteur,
      effectif,
      beneficiaires: chiffre.beneficiaires * this.tauxRecours,
      coutConstants: chiffre.coutAnnuelMeur * this.versConstants * this.tauxRecours,
      ayantsDroit: chiffre.beneficiaires,
      tauxRecours: this.tauxRecours,
      // Les avances, leurs reprises et leur stock : posés par
      // `reprisesSuccessions`, une fois la trajectoire connue.
      avancesLibereesConstants: 0,
      reprisesConstants: 0,
      stockAvancesConstants: 0,
      tauxReel: 0,
      partReprise: 0,
      dureeAvances: 0,
      populationMortalite: null,
      partFemmes: 0,
    };
  }
}

/** Cale la distribution sur la grille, l'année de l'enquête. */
function garantieDistribution(simulateur, liste, population, poids, revalorisation) {
  const distribution = simulateur.distribution;
  const parametres = simulateur.parametres;
  const macro = simulateur.macro;
  const millesime = distribution.millesime;
  const { total, tetes } = masses(liste, population, millesime, poids(millesime),
                                  revalorisation);
  const plancher = parametres.garantie_vieillesse_mensuelle
    + (parametres.situation_foyer === "seul" ? parametres.allocation_isolement_mensuelle : 0);
  const toutes = tetes[TETES_TOUTES];
  return new GarantieDistribution(
    distribution,
    plancher * macro.coefficientPrix(parametres.annee_euros_garantie_vieillesse, millesime),
    toutes > 0 ? total.actuel / toutes : 0,
    toutes > 0 ? simulateur.effectifs.effectif("tous_regimes", millesime) / toutes : 0,
    macro.coefficientPrix(millesime, parametres.annee_euros_constants),
    parametres.taux_recours_garantie,
  );
}

/**
 * Ce que les COTISANTS versent une année donnée, sous les deux barèmes.
 *
 * Le pendant de `masses`, du côté de la recette, et bâti sur la même grille.
 * Une différence : une pension ne bouge plus après la liquidation, si bien que
 * la cohorte voisine sert le même montant ; une cotisation change chaque année
 * de la carrière, et la cohorte née deux ans plus tôt verse, l'année `t`, ce que
 * la génération de la grille verse en `t + 2`. C'est cette année-là qu'on va
 * chercher.
 *
 * Le poids des cas types est celui des COTISANTS de leur caisse, et non de ses
 * retraités : `poidsCas` vient ici de `simulateur.cotisants`, la série que le
 * COR publie et projette régime par régime.
 */
function massesCotisations(liste, population, annee, poidsCas) {
  const total = {};
  for (const cle of CLES_RECETTES) total[cle] = 0;
  for (const pensionne of liste) {
    const part = poidsCas[pensionne.code] || 0;
    if (part <= 0) continue;
    for (let decalage = -DEMI_TRANCHE; decalage <= DEMI_TRANCHE; decalage += 1) {
      const poids = population.effectif(annee - pensionne.generation - decalage, annee);
      if (poids <= 0) continue;
      for (const cle of CLES_RECETTES) {
        const versee = pensionne.cotisations[cle][annee - decalage] || 0;
        if (versee) total[cle] += part * poids * versee;
      }
    }
  }
  return total;
}

/**
 * Rapport de la recette de chaque système à celle du système actuel.
 *
 * Un pour tous, sauf pour le scénario 6. AVANT LA BASCULE, il vaut un PAR
 * CONSTRUCTION, et il est écrit plutôt que calculé : la cohorte née deux ans
 * plus tôt verse ce que la génération de la grille verse deux ans plus tard,
 * déjà à 18 %, et la recette de 2025 baissait pour une réforme qui n'a pas eu
 * lieu. Après la bascule, le même décalage joue en sens inverse et s'éteint en
 * deux ans.
 */
function rapportsRecettes(total, annee, bascule) {
  const resultat = {};
  for (const [scenario] of SCENARIOS) resultat[scenario] = 1.0;
  if (annee >= bascule && total[TAUX_REELS] > 0) {
    resultat.notionnel_liberal = total.notionnel_liberal / total[TAUX_REELS];
  }
  return resultat;
}

/**
 * Fonction qui rend le poids de chaque cas type une année donnée.
 *
 * `cote` dit quel effectif pèse : les RETRAITÉS de la caisse, pour une masse de
 * pensions, ou ses COTISANTS, pour une masse de cotisations. Les deux ne disent
 * pas la même chose, et l'écart est le plus grand là où le rapport de recettes
 * mord : la SNCF a 108 000 cotisants et 158 000 retraités en 2024, et n'a plus
 * aucun cotisant en 2070.
 *
 * Les poids d'effectifs varient d'une année à l'autre — la France de 1960
 * comptait plus d'exploitants agricoles que de fonctionnaires —, et chaque
 * série a sa fenêtre : 2004-2024 pour les retraités de la DREES, 2010-2070 pour
 * les cotisants du COR. Hors d'elle, la répartition du bord est reconduite, et
 * la série le dit en tombant au niveau `estimee`.
 */
export function ponderation(simulateur, mode, casTypes, cote = COTE_RETRAITES) {
  if (!PONDERATIONS.includes(mode)) {
    throw new Error(`pondération inconnue : ${mode}`);
  }
  if (!COTES.includes(cote)) {
    throw new Error(`côté inconnu : ${cote}`);
  }
  if (mode === "egale") {
    const fixes = poidsEgaux(casTypes);
    return () => fixes;
  }
  const effectifs = cote === COTE_COTISANTS ? simulateur.cotisants : simulateur.effectifs;
  const memoire = new Map();
  return (annee) => {
    if (!memoire.has(annee)) {
      memoire.set(annee, poidsEffectifs(effectifs, annee, casTypes));
    }
    return memoire.get(annee);
  };
}

/**
 * Le rapport de chaque masse à celle du système actuel, composante comprise.
 * Les six systèmes viennent de la grille ; la composante vient de la
 * distribution, et son rapport est celui qui redonne son coût une fois
 * appliqué aux droits directs de la base.
 */
function rapports(total, garantie, baseConstants, partDerives) {
  const resultat = {};
  const directe = baseConstants * (1.0 - partDerives);
  resultat[COMPOSANTE_GARANTIE] = directe > 0 ? garantie.coutConstants / directe : 0;
  for (const [scenario] of SCENARIOS) {
    resultat[scenario] = total[scenario] / total.actuel;
  }
  return resultat;
}

/** Le coût d'une année, observé puis recalculé pour chaque système. */
class CoutAnnuel {
  constructor(annee, observee, coefficientConstants, partPib, rapportsAnnee, nombre,
              partDerives = 0.0, reversionServie = false, reformeEnVigueur = true,
              garantie = null) {
    this.annee = annee;
    // La garantie de l'année, lue sur la distribution des pensions.
    this.garantie = garantie;
    this.observee = observee;
    this.coefficientConstants = coefficientConstants;
    this.partPib = partPib;
    this.rapports = rapportsAnnee;
    this.pensionnes = nombre;
    // Part de la masse versée qui est une pension de RÉVERSION, et que le
    // rapport ne décrit pas — voir `masseDuScenario`.
    this.partDerives = partDerives;
    this.reversionServie = reversionServie;
    // La bascule a-t-elle eu lieu ? Ne sert qu'aux réformes prospectives.
    this.reformeEnVigueur = reformeEnVigueur;
  }

  /** Coût du système, en millions d'euros courants de l'année. */
  cout(scenario) {
    return masseDuScenario(this.observee, this.partDerives,
                           this.rapports[scenario], scenario, this.reversionServie,
                           this.reformeEnVigueur);
  }

  coutConstants(scenario) {
    return this.cout(scenario) * this.coefficientConstants;
  }

  get observeeConstants() {
    return this.observee * this.coefficientConstants;
  }
}

/**
 * Une année de la trajectoire de la répartition, observée ou projetée.
 *
 * UNITÉ. Contrairement au passé, dont la dépense est publiée en euros courants,
 * cette série est tenue en euros CONSTANTS de l'année de référence : les
 * pensions dont le modèle tire ses masses le sont déjà, et mêler les deux
 * reviendrait à déflater deux fois.
 */
class AvenirAnnuel {
  constructor(annee, projete, base, coefficientConstants, pib, rapportsAnnee,
              dependance, recettes = {}, partDerives = 0.0,
              reversionServie = false, reformeEnVigueur = true, garantie = null,
              pilier = null) {
    this.annee = annee;
    // La garantie de l'année, lue sur la distribution des pensions.
    this.garantie = garantie;
    // Le pilier capitalisé de l'année, tous cotisants ; null avant la bascule.
    this.pilier = pilier;
    this.projete = projete;
    this.base = base;
    this.coefficientConstants = coefficientConstants;
    this.pib = pib;
    this.rapports = rapportsAnnee;
    this.dependance = dependance;
    // Rapport de la RECETTE de chaque système à celle du système actuel. Un
    // partout, sauf pour le scénario 6 à compter de la bascule.
    this.rapportsRecettes = recettes;
    // Part de la masse versée qui est une pension de RÉVERSION, et que le
    // rapport ne décrit pas — voir `masseDuScenario`.
    this.partDerives = partDerives;
    this.reversionServie = reversionServie;
    // La bascule a-t-elle eu lieu ? Ne sert qu'aux réformes prospectives.
    this.reformeEnVigueur = reformeEnVigueur;
  }

  /** Coût du système, en millions d'euros constants de référence. */
  coutConstants(scenario) {
    return masseDuScenario(this.base, this.partDerives,
                           this.rapports[scenario], scenario, this.reversionServie,
                           this.reformeEnVigueur);
  }

  /** Le même coût, ramené aux euros courants de son année. */
  cout(scenario) {
    return this.coutConstants(scenario) / this.coefficientConstants;
  }

  /** Part du PIB : deux grandeurs de la même année, donc deux euros courants. */
  partPib(scenario) {
    return this.pib ? this.cout(scenario) / this.pib : 0.0;
  }

  /** Ce que les successions rendent de la garantie, en euros constants. */
  reprisesConstants() {
    return this.garantie ? this.garantie.reprisesConstants : 0.0;
  }

  reprises() {
    return this.reprisesConstants() / this.coefficientConstants;
  }

  partPibReprises() {
    return this.pib ? this.reprises() / this.pib : 0.0;
  }

  /** La garantie versée moins ce que les successions en rendent. */
  garantieNetteConstants() {
    return this.coutConstants(COMPOSANTE_GARANTIE) - this.reprisesConstants();
  }
}

/** La trajectoire de la répartition, de 1990 à l'horizon des projections. */
class Avenir {
  constructor(annees, premiereAnneeProjetee, anneeBascule, anneeEuros, fiabilite) {
    this.annees = annees;
    this.premiereAnneeProjetee = premiereAnneeProjetee;
    this.anneeBascule = anneeBascule;
    this.anneeEuros = anneeEuros;
    this.fiabilite = fiabilite;
    this.premiereAnnee = annees.length ? annees[0].annee : 0;
    this.derniereAnnee = annees.length ? annees[annees.length - 1].annee : 0;
  }

  projetees() {
    return this.annees.filter((ligne) => ligne.projete);
  }

  /**
   * Cumul sur les seules années PROJETÉES, en millions d'euros constants. Le
   * passé est déjà cumulé ailleurs, et sur une autre assiette.
   */
  cumul(scenario) {
    let somme = 0;
    for (const ligne of this.projetees()) somme += ligne.coutConstants(scenario);
    return somme;
  }

  annee(millesime) {
    for (const ligne of this.annees) {
      if (ligne.annee === millesime) return ligne;
    }
    return null;
  }

  /** Ce que le système ferait économiser (négatif) ou coûter en plus. */
  ecartCumule(scenario) {
    return this.cumul(scenario) - this.cumul("actuel");
  }

  /** Ce que les successions rendent sur les années projetées, en euros constants. */
  cumulReprises() {
    let somme = 0;
    for (const ligne of this.projetees()) somme += ligne.reprisesConstants();
    return somme;
  }
}

/**
 * Une année du bilan : ce qui rentre, ce que chaque système ferait sortir.
 *
 * Tout y est en PART DE PIB — l'unité du COR, et la seule où une recette de
 * 2002 et une projection de 2070 se comparent sans convention d'actualisation.
 * `pib` porte le produit intérieur brut en millions d'euros courants quand il
 * est PUBLIÉ, et zéro sinon : au-delà, un montant en milliards ne serait
 * qu'une hypothèse de croissance déguisée en observation.
 */
class SoldeAnnuel {
  constructor(annee, projete, ressources, depenses, rapportsAnnee, pib, retrait = 0.0,
              recettes = {}, partContributive = 0.0, partSubventions = 0.0,
              partImpots = 0.0, retraitParImpot = 0.0,
              tauxPrelevement = 0.0,
              tauxLiberal = 0.0, anneeBascule = 0,
              convention = CONVENTION_RAPPORT,
              partDerives = 0.0, reversionServie = false,
              reformeEnVigueur = true, parts = {}, retraits = {}) {
    this.annee = annee;
    this.projete = projete;
    this.ressources = ressources;
    this.depenses = depenses;
    this.rapports = rapportsAnnee;
    this.pib = pib;
    // Ce que la branche famille et l'assurance chômage versent pour des droits
    // que les scénarios notionnels ne servent pas, en part de PIB : une
    // recette du système actuel, jamais la leur.
    this.retrait = retrait;
    // Rapport de la recette de chaque système à celle du système actuel, et
    // part des ressources qui est une cotisation — la seule sur laquelle un
    // changement de taux ait prise.
    this.rapportsRecettes = recettes;
    this.partContributive = partContributive;
    // Part des ressources qui est une subvention d'équilibre : ce que le
    // budget comble aux régimes dont les cotisants ont disparu avant les
    // retraités. Le scénario 6 ne la reconduit pas — voir `ressourcesDe`.
    this.partSubventions = partSubventions;
    // Part des ressources qui est un impôt ou une taxe affectés : le
    // scénario 6 ne la reconduit pas non plus. `retraitParImpot` est la part
    // de `retrait` dont la recette est DANS ce poste — la CSG du fonds de
    // solidarité vieillesse —, et qui sortirait deux fois sans lui.
    this.partImpots = partImpots;
    this.retraitParImpot = retraitParImpot;
    // Ce que le système prélève, rapporté à l'ASSIETTE et non au PIB ; le taux
    // unique de la proposition ; l'année où il commence ; et laquelle des deux
    // conventions de recette s'applique.
    this.tauxPrelevement = tauxPrelevement;
    this.tauxLiberal = tauxLiberal;
    this.anneeBascule = anneeBascule;
    this.conventionRecette = convention;
    // Part de la masse versée qui est une pension de RÉVERSION, et que le
    // rapport ne décrit pas — voir `masseDuScenario`.
    this.partDerives = partDerives;
    this.reversionServie = reversionServie;
    // La bascule a-t-elle eu lieu ? Ne sert qu'aux réformes prospectives.
    this.reformeEnVigueur = reformeEnVigueur;
    // Part de chaque poste dans les ressources, au découpage du COR, et le
    // retrait payeur par payeur : ne servent qu'au tableau poste par poste.
    this.parts = parts;
    this.retraits = retraits;
  }

  /**
   * La convention du programme s'applique-t-elle à cette année ? Trois
   * conditions, et la moindre manquante fait retomber sur l'ancienne plutôt
   * que sur une division par zéro.
   */
  get recetteParAssiette() {
    return this.conventionRecette === CONVENTION_ASSIETTE
      && this.tauxPrelevement > 0
      && this.tauxLiberal > 0
      && this.anneeBascule > 0 && this.anneeBascule <= this.annee;
  }

  /**
   * Ce que le système coûterait cette année-là, en part de PIB. Le rapport ne
   * multiplie que la part des droits DIRECTS de la base : il ne décrit qu'eux,
   * et `masseDuScenario` dit pourquoi.
   */
  depense(scenario) {
    return masseDuScenario(this.depenses, this.partDerives,
                           this.rapports[scenario], scenario, this.reversionServie,
                           this.reformeEnVigueur);
  }

  /**
   * Ce qu'un système peut compter comme ressources, en part de PIB. Le système
   * actuel encaisse tout ; un scénario notionnel ne sert ni l'AVPF, ni les
   * majorations pour enfants, ni rien pendant une année de chômage, et ne peut
   * pas compter ce que la CNAF et l'Unédic versent pour ces droits-là. LA
   * RECETTE SUIT LE DROIT.
   */
  ressourcesDe(scenario) {
    if (scenario === "actuel") return this.ressources;
    if (scenario === "notionnel_liberal" && this.recetteParAssiette) {
      // Le taux plein sur l'assiette mesurée. Trois postes ne sont pas
      // reconduits. LA CONTRIBUTION D'ÉQUILIBRE DE L'ÉTAT est remplacée par
      // les 18 % appliqués aux traitements, et la reconduire en plus la
      // compterait deux fois. LES SUBVENTIONS D'ÉQUILIBRE comblent le compte
      // d'un régime dont les cotisants ont disparu avant les retraités — la
      // SNCF, les mines, les marins ; le scénario 6 fusionne tous les régimes,
      // et cette catégorie cesse d'exister. LES IMPÔTS ET TAXES AFFECTÉS
      // n'acquièrent de droits à personne : un compte notionnel ne crédite que
      // ce qui est assis sur un revenu d'activité.
      const pleine = this.ressources * this.tauxLiberal / this.tauxPrelevement;
      const autres = this.ressources
        * (1 - this.partContributive - this.partSubventions - this.partImpots);
      // La CSG du fonds de solidarité vieillesse vient de sortir avec le
      // poste : la retirer encore ici la retirerait deux fois.
      return pleine + autres - (this.retrait - this.retraitParImpot);
    }
    // LA RECETTE SUIT LE TAUX, ancienne convention : la part COTISÉE des
    // ressources observées est multipliée par un rapport de taux légaux.
    const rapport = this.rapportsRecettes[scenario] ?? 1.0;
    const cotisees = this.ressources * this.partContributive;
    return cotisees * rapport + (this.ressources - cotisees) - this.retrait;
  }

  /** Ressources moins dépenses. Négatif : besoin de financement. */
  solde(scenario) {
    return this.ressourcesDe(scenario) - this.depense(scenario);
  }

  /**
   * Facteur par lequel multiplier toutes les pensions pour tomber juste. Un
   * quand le système s'équilibre, moins de un quand il faut rogner.
   */
  coefficient(scenario) {
    const depense = this.depense(scenario);
    return depense > 0 ? this.ressourcesDe(scenario) / depense : 0.0;
  }

  /** Le même solde en millions d'euros courants, et zéro si le PIB manque. */
  soldeMeur(scenario) {
    return this.solde(scenario) * this.pib;
  }

  /**
   * Ce qui rentre, en millions d'euros courants, et zéro si le PIB manque.
   *
   * Une part de PIB ne parle qu'à qui sait ce qu'est le PIB. Les euros, si — et
   * c'est en euros que la page Coût ouvre, avant de passer aux parts, qui sont
   * la seule unité où 1959 et 2070 se comparent.
   */
  ressourcesMeur() {
    return this.ressources * this.pib;
  }

  /** Ce qui sort, en millions d'euros courants, et zéro si le PIB manque. */
  depenseMeur(scenario) {
    return this.depense(scenario) * this.pib;
  }

  /**
   * Les ressources d'un système, poste par poste, en part de PIB : c'est
   * `ressourcesDe` écrit ligne à ligne, au découpage du COR, et les lignes
   * somment au total. Le système actuel encaisse chaque poste tel quel, et
   * ses « dont » sont ce que chaque payeur verse réellement. La proposition,
   * dès la bascule, remplace les cotisations par 18 % de l'assiette et met à
   * zéro la contribution d'équilibre, les subventions et les impôts affectés ;
   * des transferts, elle ne garde que ce qui ne paie pas un droit supprimé.
   * Les autres scénarios notionnels gardent chaque poste, la part cotisée
   * multipliée par le rapport de recette, et retranchent chez le payeur ce
   * qu'ils ne peuvent pas compter.
   */
  postesRessources(scenario) {
    const total = this.ressources;
    const parts = this.parts;
    const part = (code) => parts[code] ?? 0.0;
    const famille = this.retraits.famille ?? 0.0;
    const chomage = this.retraits.chomage ?? 0.0;
    const solidarite = this.retraits.solidarite ?? 0.0;
    let postes;
    if (scenario === "actuel") {
      postes = {};
      for (const code of POSTES_RESSOURCES) postes[code] = total * part(code);
      postes.transferts_famille = famille;
      postes.transferts_chomage = chomage;
      postes.impots_solidarite = solidarite;
    } else if (scenario === "notionnel_liberal" && this.recetteParAssiette) {
      postes = {
        cotisations: total * this.tauxLiberal / this.tauxPrelevement,
        contribution_equilibre_etat: 0.0,
        subventions_equilibre: 0.0,
        impots_et_taxes: 0.0,
        transferts: total * part("transferts") - famille - chomage,
        autres_produits: total * part("autres_produits"),
        transferts_famille: 0.0,
        transferts_chomage: 0.0,
        impots_solidarite: 0.0,
      };
    } else {
      const rapport = this.rapportsRecettes[scenario] ?? 1.0;
      postes = {
        cotisations: total * part("cotisations") * rapport,
        contribution_equilibre_etat: total * part("contribution_equilibre_etat") * rapport,
        subventions_equilibre: total * part("subventions_equilibre"),
        impots_et_taxes: total * part("impots_et_taxes") - solidarite,
        transferts: total * part("transferts") - famille - chomage,
        autres_produits: total * part("autres_produits"),
        transferts_famille: 0.0,
        transferts_chomage: 0.0,
        impots_solidarite: 0.0,
      };
    }
    postes.transferts_autres = postes.transferts - postes.transferts_famille
      - postes.transferts_chomage;
    postes.impots_autres = postes.impots_et_taxes - postes.impots_solidarite;
    return postes;
  }

  /**
   * Ce qu'un système verse, en trois lignes et en part de PIB. Droit direct
   * et réversion somment exactement à `depense` ; la garantie vieillesse est
   * la composante que l'impôt finance, redite pour la proposition et nulle
   * pour les autres, et `depense` ne la contient pas.
   */
  postesDepenses(scenario) {
    const base = this.depenses;
    const directeBase = base * (1.0 - this.partDerives);
    if (scenario === "actuel") {
      return {
        droits_directs: directeBase,
        droits_derives: base * this.partDerives,
        garantie_vieillesse: 0.0,
      };
    }
    const directs = directeBase * this.rapports[scenario];
    const garantie = scenario === "notionnel_liberal"
      ? directeBase * (this.rapports[COMPOSANTE_GARANTIE] ?? 0.0) : 0.0;
    return {
      droits_directs: directs,
      droits_derives: this.depense(scenario) - directs,
      garantie_vieillesse: garantie,
    };
  }
}

/** Le bilan du système de retraite, de la première année du COR à son horizon. */
class Solde {
  constructor(annees, premiereAnneeProjetee, fiabiliteObservee, fiabilite) {
    this.annees = annees;
    this.premiereAnneeProjetee = premiereAnneeProjetee;
    // Niveau du COMPTE observé — ce qui rentre et ce qui sort, sans modèle —
    // puis celui de tout ce qui passe par un rapport de masses, c'est-à-dire de
    // toutes les colonnes des cinq contrefactuels. Le second n'est jamais mieux
    // qu'estimé : aucune institution ne publie le solde d'un système qui n'a
    // pas existé.
    this.fiabiliteObservee = fiabiliteObservee;
    this.fiabilite = fiabilite;
    this.premiereAnnee = annees.length ? annees[0].annee : 0;
    this.derniereAnnee = annees.length ? annees[annees.length - 1].annee : 0;
    this.derniereAnneeObservee = premiereAnneeProjetee - 1;
  }

  observees() {
    return this.annees.filter((ligne) => !ligne.projete);
  }

  projetees() {
    return this.annees.filter((ligne) => ligne.projete);
  }

  annee(millesime) {
    for (const ligne of this.annees) {
      if (ligne.annee === millesime) return ligne;
    }
    return null;
  }

  /**
   * Solde moyen sur une fenêtre, en part de PIB — l'indicateur par lequel le
   * COR juge la pérennité financière. Un solde négatif une année donnée ne dit
   * rien ; une moyenne négative sur quarante ans dit tout.
   */
  soldeMoyen(scenario, debut, fin) {
    const lignes = this.annees.filter((l) => l.annee >= debut && l.annee <= fin);
    if (!lignes.length) return 0.0;
    let somme = 0;
    for (const ligne of lignes) somme += ligne.solde(scenario);
    return somme / lignes.length;
  }

  /**
   * Première année PROJETÉE où le système cesse d'être en déficit, `null`
   * quand il ne l'est jamais. La question ne se pose que sur l'avenir : le
   * passé est ce qu'il a été.
   */
  premiereAnneeEquilibree(scenario) {
    for (const ligne of this.projetees()) {
      if (ligne.solde(scenario) >= 0) return ligne.annee;
    }
    return null;
  }
}

/**
 * Une année du stock : ce que les soldes cumulés depuis le départ pèsent, en
 * part de PIB. Un stock POSITIF est une dette, un stock NÉGATIF une réserve :
 * le même calcul rend les deux. Portage de `DetteAnnuelle`.
 */
class DetteAnnuelle {
  constructor(annee, croissance, taux, stocks, interets, soldes) {
    this.annee = annee;
    // Croissance NOMINALE du PIB sur l'année, et taux nominal auquel le stock
    // de fin d'année précédente se refinance — ou se place — sur l'année.
    this.croissance = croissance;
    this.taux = taux;
    this.stocks = stocks;
    this.interets = interets;
    this.soldes = soldes;
  }

  stock(scenario) { return this.stocks[scenario]; }

  interet(scenario) { return this.interets[scenario]; }

  solde(scenario) { return this.soldes[scenario]; }
}

/**
 * Le stock que les soldes à venir accumulent, de l'année de départ à
 * l'horizon. Portage de `Dette` : la récurrence est celle de toute dette
 * publique rapportée au PIB,
 *
 *     stock(t) = stock(t−1) ÷ (1 + croissance(t)) + intérêts(t) − solde(t)
 *     intérêts(t) = stock(t−1) × taux(t) ÷ (1 + croissance(t))
 *
 * Le stock part de zéro à la dernière année observée ; le taux est le forward
 * à un an de la courbe sans risque, celui-là même auquel le pilier capitalisé
 * place ses versements ; la croissance est celle du PIB de `Avenir`.
 *
 * La dette publique est posée dessous, pas mélangée : `dettePubliqueObservee`
 * porte ce que le pays doit déjà, au sens de Maastricht, année par année
 * jusqu'au départ ; `dettePublique()` tient ce niveau à plat, en part de PIB,
 * et y ajoute le stock d'un système. Ce n'est pas une prévision de la dette du
 * pays, c'est l'échelle à laquelle le stock d'un système se lit.
 */
class Dette {
  constructor(annees = [], anneeDepart = 0, ecartTaux = 0.0, dateCourbe = "",
              derniereAnneeCotee = 0, fiabiliteTaux = Fiabilite.ESTIMEE,
              fiabilite = Fiabilite.ESTIMEE, dettePubliqueObservee = {},
              anneeDettePublique = 0) {
    this.annees = annees;
    this.anneeDepart = anneeDepart;
    this.ecartTaux = ecartTaux;
    this.dateCourbe = dateCourbe;
    this.derniereAnneeCotee = derniereAnneeCotee;
    this.fiabiliteTaux = fiabiliteTaux;
    this.fiabilite = fiabilite;
    // La dette des administrations publiques observée, en part de PIB, par
    // année jusqu'à l'année de départ incluse ; et l'année dont la valeur
    // sert de point de départ — le départ lui-même, ou la dernière publiée.
    this.dettePubliqueObservee = dettePubliqueObservee;
    this.anneeDettePublique = anneeDettePublique;
    this.premiereAnnee = annees.length ? annees[0].annee : 0;
    this.derniereAnnee = annees.length ? annees[annees.length - 1].annee : 0;
  }

  /** Ce que le pays doit au départ, en part de PIB ; zéro sans série. */
  get dettePubliqueDepart() {
    const valeur = this.dettePubliqueObservee[this.anneeDettePublique];
    return valeur === undefined ? 0.0 : valeur;
  }

  /**
   * La dette publique de départ, plus ce que le système y a ajouté : le reste
   * des administrations publiques est supposé tenir sa dette à plat.
   */
  dettePublique(scenario, millesime) {
    return this.dettePubliqueDepart + this.stock(scenario, millesime);
  }

  annee(millesime) {
    for (const ligne of this.annees) {
      if (ligne.annee === millesime) return ligne;
    }
    return null;
  }

  /** Le stock en fin d'année, et zéro à l'année de départ ou avant. */
  stock(scenario, millesime) {
    const ligne = this.annee(millesime);
    return ligne ? ligne.stock(scenario) : 0.0;
  }

  /** Le stock à la dernière année, en part de PIB. */
  horizon(scenario) {
    return this.annees.length ? this.annees[this.annees.length - 1].stock(scenario) : 0.0;
  }

  /** Ce que les soldes seuls accumulent, SANS intérêts, en points de PIB. */
  cumulSoldes(scenario) {
    let somme = 0.0;
    for (const ligne of this.annees) somme += ligne.solde(scenario);
    return -somme;
  }

  /** Les intérêts cumulés sur la période, en points de PIB. */
  cumulInterets(scenario) {
    let somme = 0.0;
    for (const ligne of this.annees) somme += ligne.interet(scenario);
    return somme;
  }

  /** L'année où le stock est le plus haut, `null` s'il n'est jamais positif. */
  pic(scenario) {
    let haut = null;
    for (const ligne of this.annees) {
      if (ligne.stock(scenario) > 0.0
          && (haut === null || ligne.stock(scenario) > haut.stock(scenario))) {
        haut = ligne;
      }
    }
    return haut;
  }

  /** Première année où une dette positive cesse de croître, `null` sinon. */
  premiereAnneeDecroissance(scenario) {
    let precedent = 0.0;
    for (const ligne of this.annees) {
      const courant = ligne.stock(scenario);
      if (precedent > 0.0 && courant < precedent) return ligne.annee;
      precedent = courant;
    }
    return null;
  }
}

/**
 * Le stock que les soldes projetés accumulent, système par système. Rien
 * n'est resimulé : les soldes sont ceux de `Solde`, le PIB celui de `Avenir`,
 * le taux celui de la courbe. Borné aux années PROJETÉES : le passé a été
 * financé, et son stock est ailleurs. `dettePublique`, la série observée de
 * la dette des administrations publiques, n'entre dans aucun cumul : elle est
 * recopiée jusqu'à l'année de départ, et sa dernière valeur publiée avant ou
 * à cette année devient le point de départ de `Dette.dettePublique()`.
 */
export function calculerDette(solde, avenir, courbe, ecartTaux = 0.0,
                              dettePublique = null) {
  const projetees = solde.projetees();
  if (!projetees.length) return new Dette();
  const scenarios = SCENARIOS.map(([scenario]) => scenario);
  const stocks = {};
  for (const scenario of scenarios) stocks[scenario] = 0.0;
  let fiabiliteTaux = courbe.fiabilitePubliee;
  const lignes = [];
  for (const ligne of projetees) {
    const precedente = avenir.annee(ligne.annee - 1);
    const courante = avenir.annee(ligne.annee);
    if (!precedente || !courante || precedente.pib <= 0.0) break;
    const croissance = courante.pib / precedente.pib - 1.0;
    const placement = courbe.placement(ligne.annee - 1, 1);
    const taux = placement.taux + ecartTaux;
    fiabiliteTaux = Math.min(fiabiliteTaux, placement.fiabilite);
    const interets = {};
    const soldes = {};
    for (const scenario of scenarios) {
      interets[scenario] = stocks[scenario] * taux / (1.0 + croissance);
      soldes[scenario] = ligne.solde(scenario);
      stocks[scenario] = stocks[scenario] / (1.0 + croissance)
        + interets[scenario] - soldes[scenario];
    }
    lignes.push(new DetteAnnuelle(
      ligne.annee, croissance, taux, { ...stocks }, interets, soldes,
    ));
  }
  if (!lignes.length) return new Dette();
  const depart = lignes[0].annee - 1;
  const observee = {};
  let anneeDettePublique = 0;
  if (dettePublique) {
    for (const annee of dettePublique.annees) {
      if (annee <= depart) {
        observee[annee] = dettePublique.valeur(annee);
        anneeDettePublique = annee;
      }
    }
  }
  return new Dette(
    lignes,
    depart,
    ecartTaux,
    courbe.date,
    courbe.annee + courbe.maturiteMaximale,
    fiabiliteTaux,
    Fiabilite.ESTIMEE,
    observee,
    anneeDettePublique,
  );
}

/** La série complète, et les cumuls qu'on en tire. */
class Cout {
  constructor(annees, avenir, solde, anneeEuros, generationsRetenues, echecs,
              fiabilite, ponderationRetenue = "effectifs", poids = {},
              liquidationRetenue = "droit", dette = new Dette(), poidsCotisants = {}) {
    this.annees = annees;
    this.avenir = avenir;
    this.solde = solde;
    // Le stock que les soldes projetés accumulent, avec intérêts.
    this.dette = dette;
    this.anneeEuros = anneeEuros;
    this.generations = generationsRetenues;
    this.echecs = echecs;
    this.fiabilite = fiabilite;
    // Pondération appliquée aux cas types, et poids de chacun la DERNIÈRE année
    // observée : ce que la page affiche pour dire sur quoi ses agrégats reposent.
    this.ponderation = ponderationRetenue;
    this.poids = poids;
    // Les mêmes poids du côté de la RECETTE — les cotisants de chaque caisse et
    // non ses retraités —, la même année. Égaux aux premiers sous `egale`.
    this.poidsCotisants = poidsCotisants;
    // Datation du départ des cas types : `droit` ou `absolu`.
    this.liquidation = liquidationRetenue;
    this.premiereAnnee = annees[0].annee;
    this.derniereAnnee = annees[annees.length - 1].annee;
  }

  /** Cumul depuis la première année, en millions d'euros CONSTANTS. */
  cumul(scenario) {
    let somme = 0;
    for (const ligne of this.annees) somme += ligne.coutConstants(scenario);
    return somme;
  }

  cumulObserve() {
    let somme = 0;
    for (const ligne of this.annees) somme += ligne.observeeConstants;
    return somme;
  }

  /**
   * Scénarios dont le coût ne s'écarte JAMAIS de celui du système actuel sur la
   * période observée. L'égalité est stricte — le scénario prospectif RECOPIE la
   * pension du scénario actuel pour qui a liquidé avant la bascule. Le calcul
   * est fait, et non écrit en dur.
   */
  confondusAvecActuel() {
    return SCENARIOS
      .map(([scenario]) => scenario)
      .filter((scenario) => scenario !== "actuel"
        && this.annees.every((ligne) => ligne.rapports[scenario] === 1.0));
  }

  annee(millesime) {
    for (const ligne of this.annees) {
      if (ligne.annee === millesime) return ligne;
    }
    return null;
  }
}

/**
 * La trajectoire de la répartition, de la première année ventilée à l'horizon.
 *
 * Deux régimes, une seule formule. Jusqu'à la dernière année publiée, la base
 * est la dépense de répartition OBSERVÉE. Au-delà, elle est celle que le modèle
 * produit, mise à l'échelle par un ancrage calculé sur cette même dernière
 * année : les deux expressions coïncident exactement à la jonction.
 */
/**
 * Les avances de la garantie, leur intérêt, et ce que les successions rendent.
 * Copie de `_reprises_successions` dans `cout.py`, qui dit la méthode et ce
 * qu'elle fige.
 */
function reprisesSuccessions(lignes, simulateur, calage) {
  const parametres = simulateur.parametres;
  const bascule = parametres.annee_bascule;
  const anneeEuros = parametres.annee_euros_constants;
  const macro = simulateur.macro;
  const mortalite = simulateur.mortalite;
  const projetees = lignes.filter((ligne) => ligne.annee >= bascule && ligne.garantie);
  if (!projetees.length) return;

  // 1. Le taux réel de chaque année : le forward à un an, déflaté.
  const tauxReels = new Map();
  for (const ligne of projetees) {
    const annee = ligne.annee;
    const nominal = simulateur.courbeTaux.placement(annee - 1, 1).taux;
    const inflation = macro.coefficientPrix(annee - 1, anneeEuros)
      / macro.coefficientPrix(annee, anneeEuros) - 1.0;
    tauxReels.set(annee, (1.0 + nominal) / (1.0 + inflation) - 1.0);
  }
  let tauxMoyen = 0.0;
  for (const t of tauxReels.values()) tauxMoyen += t;
  tauxMoyen /= tauxReels.size;

  // 2. Les bénéficiaires, tranche par tranche, à l'année de l'enquête.
  const distribution = calage.distribution;
  const millesime = distribution.millesime;
  const ligneEnquete = lignes.find((ligne) => ligne.annee === millesime) || null;
  const deplacement = ligneEnquete && ligneEnquete.garantie && ligneEnquete.garantie.facteur > 0
    ? ligneEnquete.garantie.facteur : 1.0;
  const tranches = [];
  for (const tranche of distribution.tranches) {
    const ouverte = tranche.borneSuperieure === null || tranche.borneSuperieure === undefined;
    const superieure = ouverte ? null : tranche.borneSuperieure * deplacement;
    const [concernee, manque] = manqueMoyen(
      tranche.borneInferieure * deplacement, superieure, calage.plancherMensuel,
    );
    if (concernee <= 0) continue;
    const milieu = ouverte ? tranche.borneInferieure
      : 0.5 * (tranche.borneInferieure + tranche.borneSuperieure);
    tranches.push([
      tranche.part * concernee,
      manque / concernee * 12.0 * calage.versConstants,
      milieu * deplacement,
      distribution.partSous(milieu),
    ]);
  }
  let poidsTotal = 0.0;
  for (const [poids] of tranches) poidsTotal += poids;

  // 3. La mortalité des bénéficiaires : le vingtile de niveau de vie le plus
  // proche de leur pension moyenne, dans les euros de l'étude de l'INSEE.
  let population = null;
  if (poidsTotal > 0 && mortalite.anneeNiveauxDeVie !== null
      && mortalite.anneeNiveauxDeVie !== undefined) {
    let pensionMoyenne = 0.0;
    for (const [poids, , pension] of tranches) pensionMoyenne += poids * pension;
    pensionMoyenne /= poidsTotal;
    population = mortalite.populationNiveauDeVieEuros(
      pensionMoyenne * macro.coefficientPrix(millesime, mortalite.anneeNiveauxDeVie),
    );
  }
  // Et les deux sexes, pesés comme ils le sont sous le plancher.
  const courbeH = mortalite.courbeSurvie(65, bascule, "H", true, population);
  const courbeF = mortalite.courbeSurvie(65, bascule, "F", true, population);
  let partFemmes = 0.5;
  if (poidsTotal > 0) {
    let femmes65 = 0.0;
    for (const s of courbeF) femmes65 += s;
    let hommes65 = 0.0;
    for (const s of courbeH) hommes65 += s;
    const sousPlancher = {};
    for (const sexe of ["F", "H"]) {
      const parSexe = new DistributionPensions(simulateur.paquet, sexe);
      sousPlancher[sexe] = coutGarantie(
        parSexe, 1.0, calage.plancherMensuel, deplacement,
      ).partBeneficiaires;
    }
    const beneficiairesF = femmes65 * sousPlancher.F;
    const beneficiairesH = hommes65 * sousPlancher.H;
    if (beneficiairesF + beneficiairesH > 0) {
      partFemmes = beneficiairesF / (beneficiairesF + beneficiairesH);
    }
  }
  const longueur = Math.max(courbeH.length, courbeF.length);
  const survie = [];
  for (let t = 0; t < longueur; t += 1) {
    const s = (1.0 - partFemmes) * (t < courbeH.length ? courbeH[t] : 0.0)
      + partFemmes * (t < courbeF.length ? courbeF[t] : 0.0);
    if (s > 1e-9) survie.push(s);
  }
  if (!survie.length) return;
  let totalSurvie = 0;
  for (const s of survie) totalSurvie += s;
  const deces = survie.map((s, k) => s - (k + 1 < survie.length ? survie[k + 1] : 0.0));

  // 4. La couverture : calculée sur le patrimoine des retraités, sauf réglage.
  let part = parametres.part_reprise_garantie;
  if (part === null || part === undefined) {
    const patrimoine = simulateur.patrimoine;
    const bas = patrimoine.distribution("retraites_q1");
    const haut = patrimoine.distribution("retraites");
    const versBas = macro.coefficientPrix(anneeEuros, bas.annee);
    const versHaut = macro.coefficientPrix(anneeEuros, haut.annee);
    let numerateur = 0.0;
    let denominateur = 0.0;
    for (const [poids, complement, , rang] of tranches) {
      const avance = Math.abs(tauxMoyen) > 1e-12
        ? complement * ((1.0 + tauxMoyen) ** totalSurvie - 1.0) / tauxMoyen
        : complement * totalSurvie;
      const couvertureBas = bas.couverture(avance * versBas);
      const couvertureHaut = haut.couverture(avance * versHaut);
      let couverture;
      if (rang <= 0.25) couverture = couvertureBas;
      else if (rang >= 0.5) couverture = couvertureHaut;
      else couverture = couvertureBas + (couvertureHaut - couvertureBas) * (rang - 0.25) / 0.25;
      numerateur += poids * avance * couverture;
      denominateur += poids * avance;
    }
    part = denominateur > 0 ? numerateur / denominateur : 0.0;
  }

  // 5. Les avances, année par année.
  const complements = new Map();
  const croissance = new Map();
  let facteur = 1.0;
  let stock = 0.0;
  for (const ligne of projetees) {
    const annee = ligne.annee;
    const tauxReel = tauxReels.get(annee);
    facteur *= 1.0 + tauxReel;
    croissance.set(annee, facteur);
    const garantie = ligne.garantie;
    const verse = garantie.coutConstants;
    complements.set(annee, garantie.beneficiaires > 0 ? verse / garantie.beneficiaires : 0.0);
    let liberees = 0.0;
    deces.forEach((partDeces, k) => {
      let avance = 0.0;
      for (let j = 0; j <= Math.min(k, annee - bascule); j += 1) {
        const c = complements.has(annee - j) ? complements.get(annee - j) : 0.0;
        const g = croissance.has(annee - j) ? croissance.get(annee - j) : facteur;
        avance += c * facteur / g;
      }
      liberees += partDeces / totalSurvie * avance;
    });
    liberees *= garantie.beneficiaires;
    stock = stock * (1.0 + tauxReel) + verse - liberees;
    garantie.avancesLibereesConstants = liberees;
    garantie.reprisesConstants = part * liberees;
    garantie.stockAvancesConstants = stock;
    garantie.tauxReel = tauxReel;
    garantie.partReprise = part;
    garantie.dureeAvances = totalSurvie;
    garantie.populationMortalite = population;
    garantie.partFemmes = partFemmes;
  }
}

function construireAvenir(liste, depenses, population, simulateur, poids, revalorisation,
                          reversionServie = false, poidsCotisants = null, garantie = null) {
  // `poids` pèse les cas types dans les masses de PENSIONS, `poidsCotisants`
  // dans les masses de COTISATIONS ; sans le second, le premier sert aux deux,
  // ce qui est l'ancienne convention.
  if (poidsCotisants === null) poidsCotisants = poids;
  const macro = simulateur.macro;
  const anneeEuros = simulateur.parametres.annee_euros_constants;
  const dernierePubliee = depenses.derniereAnnee;

  const ancrageMasses = masses(liste, population, dernierePubliee,
                              poids(dernierePubliee), revalorisation).total;
  if (ancrageMasses.actuel <= 0) {
    return new Avenir([], 0, 0, anneeEuros, Fiabilite.ESTIMEE);
  }
  if (garantie === null) {
    garantie = garantieDistribution(simulateur, liste, population, poids, revalorisation);
  }
  // Les deux termes sont mis dans la MÊME unité avant d'être divisés : la
  // dépense publiée, en euros de son année, est ramenée aux euros constants où
  // les pensions du modèle sont déjà exprimées.
  const ancrage = depenses.repartition(dernierePubliee)
    * macro.coefficientPrix(dernierePubliee, anneeEuros) / ancrageMasses.actuel;

  // Le PIB est publié jusqu'en 2025 ; au-delà il croît au rythme nominal des
  // hypothèses de projection, CORRIGÉ de l'évolution de la population d'âge
  // actif. Sans cette correction, la France de 2070 produirait avec douze pour
  // cent d'actifs qu'aucune projection ne lui donne. Le rythme est pris HORS
  // trajectoire d'emploi : la population d'âge actif en tient lieu ici.
  const dernierePib = depenses.pib.derniereAnnee;
  const pibProjete = new Map();
  let courant = depenses.pib.valeur(dernierePib);
  for (let annee = dernierePib + 1; annee <= HORIZON; annee += 1) {
    courant *= (1.0 + macro.pib_nominal_hors_emploi.valeur(annee))
      * (population.actifs.valeur(annee) / population.actifs.valeur(annee - 1));
    pibProjete.set(annee, courant);
  }

  const lignes = [];
  for (let annee = depenses.premiereAnneeVentilee; annee <= HORIZON; annee += 1) {
    const poidsAnnee = poids(annee);
    const { total, tetes } = masses(liste, population, annee, poidsAnnee, revalorisation);
    if (total.actuel <= 0) continue;
    const cotisations = massesCotisations(liste, population, annee,
                                          poidsCotisants(annee));
    const projete = annee > dernierePubliee;
    const coefficient = macro.coefficientPrix(annee, anneeEuros);
    let pilier = null;
    if (annee >= simulateur.parametres.annee_debut_capitalisation) {
      const flux = massesPilier(liste, population, annee, poidsCotisants(annee), poidsAnnee);
      if (flux.versements > 0) {
        const rapportsPilier = {};
        for (const cle of ["frais_versement", "frais_gestion", "encours",
          "rentes_brutes", "rentes"]) {
          rapportsPilier[cle] = flux[cle] / flux.versements;
        }
        pilier = new PilierAnnuel(annee, rapportsPilier);
      }
    }
    const base = projete
      ? ancrage * total.actuel
      : depenses.repartition(annee) * coefficient;
    const actifs = population.actifs.valeur(annee);
    const partDerives = depenses.partDroitsDerives(annee);
    const projetee = garantie.chiffrer(total, tetes);
    lignes.push(new AvenirAnnuel(
      annee,
      projete,
      base,
      coefficient,
      pibProjete.has(annee)
        ? pibProjete.get(annee)
        : depenses.pib.valeur(Math.min(annee, dernierePib)),
      rapports(total, projetee, base, partDerives),
      actifs
        ? population.effectifTranche(AGE_DEPENDANCE, population.ageMaximal, annee)
          / actifs
        : 0.0,
      rapportsRecettes(cotisations, annee, simulateur.parametres.annee_bascule),
      partDerives,
      reversionServie,
      annee >= simulateur.parametres.annee_bascule,
      projetee,
      pilier,
    ));
  }

  // Une trajectoire ne peut pas valoir mieux qu'estimée : sa démographie est
  // projetée, sa macroéconomie est une hypothèse, et son contrefactuel n'a
  // jamais existé.
  reprisesSuccessions(lignes, simulateur, garantie);
  return new Avenir(
    lignes, dernierePubliee + 1, simulateur.parametres.annee_bascule,
    anneeEuros, Fiabilite.ESTIMEE,
  );
}

/**
 * Le bilan, obtenu en croisant le compte du COR et les rapports du modèle.
 *
 * Aucune pension n'est resimulée ici : les rapports de masses sont ceux que
 * `construireAvenir` a déjà calculés, année par année, et cette fonction ne
 * fait que les appliquer à une autre série de dépenses. Le RAPPORT est la
 * seule chose empruntée au modèle ; il est sans dimension, et c'est pourquoi
 * on peut l'appliquer à une dépense dont le périmètre n'est pas celui sur
 * lequel il a été calculé. La dépense du système actuel, elle, reste celle du
 * COR de bout en bout : c'est ce qui fait que le solde du scénario 1 est
 * exactement le solde publié, et non une reconstitution.
 */
function construireSolde(avenir, comptes, derniereAnneePib, assiette,
                        tauxLiberal, anneeBascule, convention, depenses,
                        reversionServie = false) {
  const parAnnee = new Map(avenir.annees.map((ligne) => [ligne.annee, ligne]));
  // Le taux de prélèvement de l'année, ou celui de la dernière connue : il
  // faut le calculer sur une année où l'assiette est PUBLIÉE, reconduire un
  // montant en euros courants n'ayant pas de sens.
  const tauxPrelevement = (annee) => {
    if (!assiette) return 0.0;
    const reference = assiette.anneeDeReference(annee);
    return assiette.tauxPrelevement(comptes.ressource(reference), reference);
  };
  const lignes = [];
  for (const annee of comptes.annees()) {
    const ligne = parAnnee.get(annee);
    if (!ligne) continue;
    lignes.push(new SoldeAnnuel(
      annee,
      annee > comptes.derniereAnneeObservee,
      comptes.ressource(annee),
      comptes.depense(annee),
      ligne.rapports,
      annee <= derniereAnneePib ? ligne.pib : 0.0,
      comptes.recetteNonAcquise(annee),
      ligne.rapportsRecettes,
      comptes.partContributive(annee),
      comptes.part("subventions_equilibre", annee),
      comptes.part("impots_et_taxes", annee),
      comptes.recetteNonAcquise(annee, true),
      tauxPrelevement(annee),
      tauxLiberal,
      anneeBascule,
      convention,
      depenses.partDroitsDerives(annee),
      reversionServie,
      annee >= anneeBascule,
      Object.fromEntries(POSTES.map((poste) => [poste.code, comptes.part(poste.code, annee)])),
      Object.fromEntries(
        ORGANISMES.filter((organisme) => organisme.droitSupprime)
          .map((organisme) => [organisme.code,
            comptes.recetteNonAcquise(annee, null, organisme.code)]),
      ),
    ));
  }
  if (!lignes.length) return new Solde([], 0, Fiabilite.ESTIMEE, Fiabilite.ESTIMEE);
  let observee = Fiabilite.CERTIFIEE;
  let vues = 0;
  for (const ligne of lignes) {
    if (ligne.projete) continue;
    observee = Math.min(observee, comptes.fiabilite(ligne.annee));
    vues += 1;
  }
  return new Solde(
    lignes,
    comptes.derniereAnneeObservee + 1,
    vues ? observee : Fiabilite.ESTIMEE,
    Fiabilite.ESTIMEE,
  );
}

/**
 * Le coût observé, les cinq contrefactuels, et la trajectoire jusqu'en 2070.
 * Les années où le modèle ne sert aucune pension sont écartées : un rapport y
 * serait une division par zéro, et non un résultat.
 *
 * `comptes` porte le second terme du bilan — les ressources. Il est
 * facultatif : sans lui, tout ce qui précède est calculé à l'identique et le
 * solde reste vide.
 */
export function calculerCout(simulateur, depenses, population, comptes = null,
                             casTypes = CAS_TYPES, mode = "effectifs",
                             liquidation = "droit", assiette = null,
                             conventionRecette = CONVENTION_ASSIETTE,
                             conventionReversion = CONVENTION_REVERSION_SUPPRIMEE) {
  if (!CONVENTIONS_RECETTE.includes(conventionRecette)) {
    throw new Error(`convention de recette inconnue : ${conventionRecette}`);
  }
  if (!CONVENTIONS_REVERSION.includes(conventionReversion)) {
    throw new Error(`convention de réversion inconnue : ${conventionReversion}`);
  }
  const reversionServie = conventionReversion === CONVENTION_REVERSION_SERVIE;
  const { liste, motifs } = pensionnes(simulateur, casTypes, liquidation);
  const poids = ponderation(simulateur, mode, casTypes);
  const poidsCotisants = ponderation(simulateur, mode, casTypes, COTE_COTISANTS);
  const macro = simulateur.macro;
  const anneeEuros = simulateur.parametres.annee_euros_constants;
  // La seconde règle d'indexation, construite une fois pour les deux régimes de
  // la page. Elle part de la plus ancienne liquidation de la grille : un
  // coefficient ne se rattrape pas, il se cumule depuis le départ en retraite.
  const premiereLiquidation = liste.length
    ? Math.min(...liste.map((p) => p.anneeLiquidation)) - DEMI_TRANCHE
    : HORIZON;
  const revalorisation = new RevalorisationServie(simulateur, premiereLiquidation, HORIZON);

  // La garantie vieillesse ne se lit pas sur la grille mais sur la
  // distribution des pensions ; la grille dit seulement de combien cette
  // distribution bouge. Calée une fois, l'année de l'enquête.
  const garantie = garantieDistribution(simulateur, liste, population, poids,
                                        revalorisation);

  const lignes = [];
  for (const annee of depenses.annees()) {
    const { total, vivants, tetes } = masses(liste, population, annee, poids(annee),
                                             revalorisation);
    if (total.actuel <= 0) continue;
    const observee = depenses.depense(annee);
    const coefficient = macro.coefficientPrix(annee, anneeEuros);
    const partDerives = depenses.partDroitsDerives(annee);
    const projetee = garantie.chiffrer(total, tetes);
    lignes.push(new CoutAnnuel(
      annee,
      observee,
      coefficient,
      depenses.partPib(annee),
      rapports(total, projetee, observee * coefficient, partDerives),
      vivants,
      partDerives,
      reversionServie,
      annee >= simulateur.parametres.annee_bascule,
      projetee,
    ));
  }

  let fiabilite = Fiabilite.ESTIMEE;
  for (const ligne of lignes) {
    fiabilite = Math.min(fiabilite, depenses.fiabilite(ligne.annee));
  }
  // Le contrefactuel ne peut jamais valoir mieux qu'« estimé » : la dépense
  // observée est certifiée, le rapport qui la corrige ne l'est pas et ne peut
  // pas l'être.
  const avenir = construireAvenir(liste, depenses, population, simulateur, poids,
                                  revalorisation, reversionServie, poidsCotisants,
                                  garantie);
  const solde = comptes && avenir.annees.length
    ? construireSolde(
      avenir, comptes, depenses.pib.derniereAnnee, assiette,
      simulateur.parametres.taux_cotisation_liberal,
      simulateur.parametres.annee_bascule, conventionRecette, depenses,
      reversionServie,
    )
    : new Solde([], 0, Fiabilite.ESTIMEE, Fiabilite.ESTIMEE);
  return new Cout(
    lignes,
    avenir,
    solde,
    anneeEuros,
    generations(),
    motifs,
    Math.min(fiabilite, Fiabilite.ESTIMEE),
    mode,
    poids(depenses.derniereAnnee),
    liquidation,
    calculerDette(solde, avenir, simulateur.courbeTaux, 0.0,
                  comptes ? comptes.dettePublique : null),
    poidsCotisants(depenses.derniereAnnee),
  );
}
