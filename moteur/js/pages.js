/**
 * Contenu des pages : formulaire, résultats, cas types, méthode, données.
 *
 * Portage de ``src/retraite_notionnelle/web/pages.py``. Le rendu doit être
 * identique à celui de la référence Python au caractère près : c'est ce que
 * vérifient les témoins de ``tests/temoins/pages.json``.
 */

import { MOIS_PAR_AN, enMois, formaterAge } from "./calendrier.js";
import { bornesDeformation, salaireMoyenAnnuel } from "./carriere.js";
import { CAS_TYPES, GENERATIONS, calculerCasTypes } from "./castypes.js";
import {
  AgeConversionDroitsAcquis, ModeAgeReference, ModeIndexation, PARAMETRES_DEFAUT, PartCotisation,
  TableConversion, avec, cleParametres,
} from "./config.js";
import { SCENARIOS, calculerCout } from "./cout.js";
import { SYSTEMES, DepensesRetraite } from "./depenses.js";
import { Population } from "./population.js";
import { echapper, formatFixe, formatG } from "./format.js";
import * as g from "./gabarit.js";
import { nomFiabilite } from "./serie.js";
import { Simulateur } from "./simulateur.js";

export const PROFILS = [
  ["plat", "Plat — le salaire suit le salaire moyen"],
  ["ascendant", "Ascendant — profil employé/ouvrier"],
  ["fortement_ascendant", "Fortement ascendant — profil cadre"],
];

// La règle par défaut vient EN TÊTE : c'est celle que la simulation applique, et
// donc la première ligne du tableau « D'où vient l'écart ».
export const INDEXATIONS = [
  ["masse_salariale", "Masse salariale — règle d'équilibre (défaut)"],
  ["revalorisation_portee_au_compte", "Revalorisation réellement pratiquée (arrêtés Cnav)"],
  ["triple_lock_inverse", "Triple lock inversé (règle demandée)"],
  ["triple_lock_inverse_nominal", "Triple lock inversé, tout en nominal"],
  ["mediane_trois_taux", "Médiane des trois taux"],
  ["moyenne_trois_taux", "Moyenne des trois taux"],
  ["pib_nominal", "PIB nominal (assiette la plus large)"],
  ["prix", "Prix"],
  ["salaires", "Salaire moyen"],
];

// Fenêtre de lissage maximale acceptée par le formulaire, en années. La fenêtre
// se saisit librement — 1 pour aucun lissage, 5 pour la règle italienne. La
// borne est un garde-fou de sens, pas une limite du moteur : au-delà d'une
// trentaine d'années la moyenne couvre presque toute une carrière, et ce n'est
// plus un lissage mais un taux fixe reconstitué.
export const LISSAGE_MAXIMUM = 30;

export const AGES_REFERENCE = [
  ["cliquet_legal", "Cliquet légal (défaut)"],
  ["cliquet_puis_esperance_vie", "Cliquet puis espérance de vie"],
  ["legal_sans_cliquet", "Âge légal, sans cliquet"],
];

export const TABLES = [["unisexe", "Unisexe (défaut)"], ["par_sexe", "Par sexe"]];

export const PARTS_COTISATION = [
  ["salariale", "Part salariale seule (défaut)"],
  ["totale", "Salariale et patronale"],
  ["totale_alignee", "Salariale et patronale, public aligné sur le privé"],
];

export const CONVERSIONS_ACQUIS = [
  ["reference", "À l'âge de référence (défaut)"],
  ["liquidation", "À l'âge de départ effectif"],
];

export const PROJECTIONS = [
  ["cor_reference", "COR référence — productivité 0,7 %"],
  ["cor_productivite_basse", "COR variante basse — 0,4 %"],
  ["cor_productivite_haute", "COR variante haute — 1,0 %"],
];

// Unités dans lesquelles un revenu d'activité peut être saisi. Le modèle n'en
// connaît qu'une — le multiple du salaire moyen —, parce qu'elle seule garde son
// sens sur quatre-vingts ans : 40 000 francs ne veulent pas dire la même chose
// en 1955, en 1985 et jamais après 2001. Mais personne ne connaît son salaire
// dans cette unité-là, et la question « brut ou net, et combien en euros ? »
// revenait à chaque lecture. Le formulaire accepte donc aussi le montant que
// porte le bulletin de paie, et fait la conversion lui-même.
export const UNITES_REVENU = [
  ["moyen", "En multiples du salaire moyen (défaut)"],
  ["euros_mois", "En euros bruts par mois"],
  ["euros_an", "En euros bruts par an"],
  ["francs_mois", "En francs bruts par mois"],
  ["francs_an", "En francs bruts par an"],
];

// Durée mensuelle de référence du SMIC : 35 heures par semaine ramenées au mois,
// soit 151,67 heures. Elle ne sert qu'à écrire un repère à l'échelle d'un
// salaire mensuel.
export const HEURES_SMIC_PAR_MOIS = 151.67;

// Première année où ce repère mensuel a un sens. La durée légale a été de 40
// heures jusqu'en 1982, de 39 ensuite, puis de 35 par étapes ; la garantie
// mensuelle unique sur 151,67 heures n'existe qu'au terme de l'harmonisation
// prévue par la loi du 17 janvier 2003, achevée au 1er juillet 2005. Le modèle
// ne porte pas la durée légale année par année : plutôt que de l'inventer, le
// repère des années antérieures est donné à l'heure, ce qui ne suppose rien.
export const ANNEE_SMIC_MENSUEL = 2005;

// Taux de conversion irrévocable fixé par le règlement (CE) n° 2866/98 :
// 1 euro = 6,559 57 francs.
export const FRANCS_PAR_EURO = 6.55957;

// Le « nouveau franc » du décret du 27 décembre 1958 vaut cent anciens francs et
// a cours à partir du 1er janvier 1960. Un montant en francs d'avant cette date
// est donc en anciens francs : le convertir au taux du nouveau franc le
// multiplierait par cent. Le formulaire connaît l'année du montant, il applique
// donc le bon des deux sans rien demander.
export const ANNEE_NOUVEAU_FRANC = 1960;

// Dernière année où un salaire pouvait être libellé en francs. L'euro est la
// monnaie de compte depuis le 1er janvier 1999, mais les bulletins de paie ont
// porté les deux jusqu'au basculement des espèces, le 1er janvier 2002.
export const DERNIERE_ANNEE_FRANC = 2001;

/**
 * Nombre maximal de métiers d'une carrière, le premier compris. Le formulaire
 * affiche toujours une ligne vide de plus que les métiers saisis : c'est ainsi
 * qu'on en ajoute un, sans une ligne de JavaScript. La borne n'est pas une
 * limite du moteur mais celle du formulaire : au-delà, ce n'est plus une suite
 * de métiers qu'on décrit, c'est un relevé de carrière année par année.
 */
export const METIERS_MAXIMUM = 6;

/** Rang de chaque métier, tel que le formulaire l'annonce. */
export const RANGS_METIER = ["premier", "deuxième", "troisième", "quatrième",
  "cinquième", "sixième", "septième", "huitième"];

/**
 * Mois de naissance. Le droit coupe deux générations en cours d'année — au
 * 1er juillet 1951, au 1er septembre 1961 — et l'âge à la liquidation ne se lit
 * qu'à partir de lui.
 */
export const MOIS_NAISSANCE = [
  ["1", "janvier"], ["2", "février"], ["3", "mars"], ["4", "avril"],
  ["5", "mai"], ["6", "juin"], ["7", "juillet"], ["8", "août"],
  ["9", "septembre"], ["10", "octobre"], ["11", "novembre"], ["12", "décembre"],
];

/** Mois qui s'ajoutent aux années entières d'un âge. */
export const MOIS_AGE = Array.from({ length: 12 }, (unused, m) => [
  String(m), m === 0 ? "0 mois" : `${m} mois`,
]);

/** Saisie inexploitable, à afficher telle quelle à l'utilisateur. */
export class ErreurSaisie extends Error {}

const DEFAUTS = Object.freeze({
  naissance: 1975,
  naissance_mois: 1,
  sexe: "H",
  statut: "salarie_prive_non_cadre",
  debut: 21,
  liquidation: 64,
  //: Revenu du premier métier, dans l'unité choisie ci-dessous.
  salaire: 1.0,
  //: Unité dans laquelle les revenus sont saisis, pour TOUS les métiers : un
  //: seul choix pour la carrière entière, parce qu'on décrit une même vie de
  //: travail et qu'un changement d'unité en cours de route n'est pas une
  //: information sur la carrière.
  unite_revenu: "moyen",
  //: Année dont les montants saisis sont ceux-là. Sans effet quand l'unité est
  //: le multiple du salaire moyen — celui-ci vaut pour toute la carrière —,
  //: indispensable dès qu'on saisit une somme : 2 000 € de 1990 et 2 000 € de
  //: 2026 ne décrivent pas la même carrière.
  annee_revenu: 2026,
  //: Les métiers exercés APRÈS le premier. Le premier, lui, est décrit par
  //: ``statut``, ``debut`` et ``salaire`` : une adresse d'avant les carrières
  //: multiples reste donc valide, et décrit la carrière d'un seul métier.
  metiers: Object.freeze([]),
  profil: "ascendant",
  primes: 0.0,
  enfants: 0,
  interruptions: "",
  indexation: "masse_salariale",
  lissage: 1,
  age_reference: "cliquet_legal",
  table: "unisexe",
  conversion_acquis: "reference",
  part_cotisation: "salariale",
  projection: "cor_reference",
  bascule: 2026,
  euros: 2026,
  //: Vrai si la requête portait des paramètres, donc s'il faut calculer.
  demandee: false,
});

/** Paramètres d'une simulation, tels que l'utilisateur les a saisis. */
export class Saisie {
  constructor(champs = {}) {
    Object.assign(this, DEFAUTS, champs);
  }

  static depuisRequete(parametres) {
    // Le premier métier se lit d'abord : les suivants héritent de son niveau de
    // revenu quand ils n'en portent pas.
    const statut = parametres.statut || DEFAUTS.statut;
    const salaire = reel(parametres, "salaire", DEFAUTS.salaire);
    const saisie = new Saisie({
      unite_revenu: parmi(parametres, "unite_revenu", UNITES_REVENU, DEFAUTS.unite_revenu),
      annee_revenu: entier(parametres, "annee_revenu", DEFAUTS.annee_revenu),
      naissance: entier(parametres, "naissance", DEFAUTS.naissance),
      naissance_mois: entier(parametres, "naissance_mois", DEFAUTS.naissance_mois),
      sexe: parametres.sexe === "F" ? "F" : "H",
      statut,
      debut: ageSaisi(parametres, "debut", DEFAUTS.debut),
      liquidation: ageSaisi(parametres, "liquidation", DEFAUTS.liquidation),
      salaire,
      metiers: metiersSaisis(parametres, salaire),
      profil: parmi(parametres, "profil", PROFILS, DEFAUTS.profil),
      primes: reel(parametres, "primes", DEFAUTS.primes),
      enfants: entier(parametres, "enfants", DEFAUTS.enfants),
      interruptions: (parametres.interruptions || "").trim(),
      indexation: parmi(parametres, "indexation", INDEXATIONS, DEFAUTS.indexation),
      lissage: entier(parametres, "lissage", DEFAUTS.lissage),
      age_reference: parmi(parametres, "age_reference", AGES_REFERENCE, DEFAUTS.age_reference),
      table: parmi(parametres, "table", TABLES, DEFAUTS.table),
      conversion_acquis: parmi(
        parametres, "conversion_acquis", CONVERSIONS_ACQUIS, DEFAUTS.conversion_acquis,
      ),
      part_cotisation: parmi(
        parametres, "part_cotisation", PARTS_COTISATION,
        DEFAUTS.part_cotisation,
      ),
      projection: parmi(parametres, "projection", PROJECTIONS, DEFAUTS.projection),
      bascule: entier(parametres, "bascule", DEFAUTS.bascule),
      euros: entier(parametres, "euros", DEFAUTS.euros),
      demandee: Object.keys(parametres).length > 0,
    });
    saisie.verifier();
    return saisie;
  }

  verifier() {
    if (!(this.naissance_mois >= 1 && this.naissance_mois <= 12)) {
      throw new ErreurSaisie("Mois de naissance attendu entre 1 et 12.");
    }
    if (!(this.naissance >= 1900 && this.naissance <= 2020)) {
      throw new ErreurSaisie(
        `Année de naissance hors du champ du modèle : ${this.naissance}. `
        + "Attendu entre 1900 et 2020.",
      );
    }
    if (!(this.debut >= 14 && this.debut <= 40)) {
      throw new ErreurSaisie("Âge de début d'activité attendu entre 14 et 40 ans.");
    }
    if (!(this.liquidation >= 40 && this.liquidation <= 75)) {
      throw new ErreurSaisie("Âge de liquidation attendu entre 40 et 75 ans.");
    }
    if (this.liquidation <= this.debut) {
      throw new ErreurSaisie(
        "L'âge de liquidation doit être postérieur à l'âge de début d'activité.",
      );
    }
    this.verifierUnite();
    this.verifierRevenu(this.salaire, 1);
    if (!(this.primes >= 0 && this.primes <= 0.6)) {
      throw new ErreurSaisie("Part de primes attendue entre 0 et 0,6.");
    }
    if (!(this.lissage >= 1 && this.lissage <= LISSAGE_MAXIMUM)) {
      throw new ErreurSaisie(
        `Fenêtre de lissage attendue entre 1 et ${LISSAGE_MAXIMUM} ans `
        + "(1 = aucun lissage).",
      );
    }
    // Les métiers se suivent sans se recouvrir : chacun commence après le
    // précédent et avant le départ à la retraite.
    let precedent = this.debut;
    this.metiers.forEach((metier, index) => {
      const rang = index + 2;
      if (!(metier.debut >= 14 && metier.debut <= 75)) {
        throw new ErreurSaisie(
          `Métier n° ${rang} : âge de début attendu entre 14 et 75 ans.`,
        );
      }
      if (metier.debut <= precedent) {
        throw new ErreurSaisie(
          `Métier n° ${rang} : il doit commencer après le précédent, qui débute `
          + `à ${age(precedent)}.`,
        );
      }
      if (metier.debut >= this.liquidation) {
        throw new ErreurSaisie(
          `Métier n° ${rang} : il doit commencer avant le départ à la retraite, `
          + `fixé à ${age(this.liquidation)}.`,
        );
      }
      this.verifierRevenu(metier.salaire, rang);
      precedent = metier.debut;
    });
  }

  /** Vrai si les revenus sont saisis en monnaie, faux s'ils sont un ratio. */
  get revenu_en_montant() {
    return this.unite_revenu !== "moyen";
  }

  get revenu_en_francs() {
    return this.unite_revenu.startsWith("francs");
  }

  /** Ce que l'unité choisie exige, avant même de regarder les montants. */
  verifierUnite() {
    if (!this.revenu_en_montant) {
      return;
    }
    if (!(this.annee_revenu >= 1941 && this.annee_revenu <= 2070)) {
      throw new ErreurSaisie(
        "Année des montants saisis attendue entre 1941 et 2070 "
        + `(reçu : ${this.annee_revenu}).`,
      );
    }
    if (this.revenu_en_francs && this.annee_revenu > DERNIERE_ANNEE_FRANC) {
      throw new ErreurSaisie(
        "Un salaire n'était plus libellé en francs après "
        + `${DERNIERE_ANNEE_FRANC} : choisir une année antérieure, ou saisir `
        + "les revenus en euros.",
      );
    }
  }

  /**
   * Un revenu saisi, contrôlé dans l'unité où il a été écrit. Le message parle
   * la langue du champ : refuser « 2 500 € par mois » au motif qu'il faut
   * « entre 0,1 et 10 fois le salaire moyen » ne dirait rien à qui n'a jamais
   * entendu parler de cette unité.
   */
  verifierRevenu(valeur, rang) {
    if (this.revenu_en_montant) {
      if (!(valeur > 0)) {
        throw refus(rang, "Le revenu doit être un montant strictement positif.");
      }
      return;
    }
    if (!(valeur >= 0.1 && valeur <= 10)) {
      throw refus(
        rang, "Niveau de revenu attendu entre 0,1 et 10 fois le salaire moyen.",
      );
    }
  }

  /**
   * Un revenu saisi, ramené à l'unité du modèle : un multiple du salaire moyen.
   * C'est ici, et nulle part ailleurs, que la monnaie entre dans le modèle. Le
   * moteur ne connaît que le ratio : il garde son sens sur quatre-vingts ans,
   * quand un montant n'en a que rapporté à son année et à sa monnaie.
   */
  niveau(macro, valeur) {
    if (!this.revenu_en_montant) {
      return valeur;
    }
    return eurosAnnuels(this.unite_revenu, valeur, this.annee_revenu)
      / salaireMoyenAnnuel(macro, this.annee_revenu);
  }

  /** Le niveau de chaque métier, du premier au dernier, en multiples. */
  niveaux(macro) {
    return [this.niveau(macro, this.salaire)].concat(
      this.metiers.map((metier) => this.niveau(macro, metier.salaire)),
    );
  }

  /**
   * La carrière comme suite de métiers, le premier compris. C'est sous cette
   * forme que le modèle la reçoit ; le formulaire, lui, garde le premier métier
   * dans ses champs historiques. `macro` sert à convertir les revenus saisis en
   * monnaie — il ne coûte rien quand ils sont déjà des multiples.
   */
  parcours(macro) {
    const niveaux = this.niveaux(macro);
    niveaux.forEach((niveau, index) => this.verifierNiveau(niveau, index + 1, macro));
    const statuts_ = [this.statut, ...this.metiers.map((metier) => metier.statut)];
    const debuts = [this.debut, ...this.metiers.map((metier) => metier.debut)];
    return niveaux.map((niveau, index) => ({
      affiliation: statuts_[index],
      age_debut: debuts[index],
      niveau_salaire: niveau,
    }));
  }

  /**
   * Le montant converti tient-il dans ce que le modèle sait décrire ? Le
   * contrôle ne peut se faire qu'ici : « 0,1 à 10 fois le salaire moyen » ne
   * devient un intervalle de montants qu'une fois l'année connue et la série
   * chargée. Le refus redit donc les bornes en monnaie, faute de quoi il
   * n'indiquerait pas quoi corriger.
   */
  verifierNiveau(niveau, rang, macro) {
    if (niveau >= 0.1 && niveau <= 10) {
      return;
    }
    if (!this.revenu_en_montant) {
      throw refus(
        rang, "Niveau de revenu attendu entre 0,1 et 10 fois le salaire moyen.",
      );
    }
    const moyen = salaireMoyenAnnuel(macro, this.annee_revenu);
    const borne = (part) => g.nombre(
      depuisEurosAnnuels(this.unite_revenu, part * moyen, this.annee_revenu), 0,
    );
    throw refus(
      rang,
      `Ce revenu vaut ${g.nombre(niveau, 2)} fois le salaire moyen de `
      + `${this.annee_revenu}, et le modèle en accepte de 0,1 à 10 fois — `
      + `soit de ${borne(0.1)} à ${borne(10)} `
      + `${libelleUnite(this.unite_revenu)} de ${this.annee_revenu}.`,
    );
  }

  parametres(base) {
    return avec(base, {
      mode_indexation: ModeIndexation[cleEnum(ModeIndexation, this.indexation)],
      lissage_indexation: this.lissage,
      mode_age_reference: ModeAgeReference[cleEnum(ModeAgeReference, this.age_reference)],
      table_conversion: TableConversion[cleEnum(TableConversion, this.table)],
      age_conversion_droits_acquis:
        AgeConversionDroitsAcquis[cleEnum(AgeConversionDroitsAcquis, this.conversion_acquis)],
      part_cotisation: PartCotisation[
        cleEnum(PartCotisation, this.part_cotisation)],
      scenario_projection: this.projection,
      annee_bascule: this.bascule,
      annee_euros_constants: this.euros,
    });
  }

  /** « 1995:1999:education_enfant, 2003:2004:chomage » -> Map année → motif. */
  interruptionsAnalysees() {
    const plages = new Map();
    for (const brut of this.interruptions.replace(/\n/g, ",").split(",")) {
      const morceau = brut.trim();
      if (!morceau) {
        continue;
      }
      const parties = morceau.split(":");
      const [debut, fin, motif] = parties;
      if (parties.length !== 3 || !estEntier(debut) || !estEntier(fin)) {
        throw new ErreurSaisie(
          `Interruption mal formée : « ${morceau} ». Attendu `
          + "« année_début:année_fin:motif », par exemple "
          + "1995:1999:education_enfant.",
        );
      }
      for (let annee = Number(debut); annee <= Number(fin); annee += 1) {
        plages.set(annee, motif.trim());
      }
    }
    return plages;
  }

  /** Mois qui s'ajoutent aux années entières de l'âge de départ. */
  get liquidation_mois() {
    return enMois(this.liquidation) % 12;
  }

  get debut_mois() {
    return enMois(this.debut) % 12;
  }

  requete(remplacements = {}) {
    const champs = {
      naissance: this.naissance, naissance_mois: this.naissance_mois,
      sexe: this.sexe, statut: this.statut,
      // L'âge s'écrit en années ENTIÈRES et en mois : « 64 ans et sept mois »
      // plutôt que « 64,583333 ». L'adresse reste lisible, et une ancienne
      // adresse portant un âge décimal reste comprise.
      debut: Math.floor(enMois(this.debut) / 12), debut_mois: this.debut_mois,
      liquidation: Math.floor(enMois(this.liquidation) / 12),
      liquidation_mois: this.liquidation_mois,
      salaire: nombreBrut(this.salaire), profil: this.profil,
      primes: nombreBrut(this.primes), enfants: this.enfants,
      interruptions: this.interruptions, indexation: this.indexation,
      lissage: this.lissage,
      age_reference: this.age_reference, table: this.table,
      conversion_acquis: this.conversion_acquis,
      part_cotisation: this.part_cotisation,
      projection: this.projection, bascule: this.bascule, euros: this.euros,
    };
    // L'unité par défaut ne s'écrit pas : une adresse produite avant que le
    // formulaire n'accepte les montants reste exactement celle qu'elle était, et
    // une adresse en multiples du salaire moyen ne se met pas à traîner deux
    // paramètres qui ne disent rien.
    if (this.revenu_en_montant) {
      champs.unite_revenu = this.unite_revenu;
      champs.annee_revenu = this.annee_revenu;
    }
    // Les métiers qui suivent le premier, un groupe de trois champs chacun. Une
    // ligne vide du formulaire n'en produit aucun : l'adresse ne porte que ce
    // qui a été saisi.
    this.metiers.forEach((metier, index) => {
      const rang = index + 2;
      champs[`metier${rang}_debut`] = nombreBrut(metier.debut);
      champs[`metier${rang}_statut`] = metier.statut;
      champs[`metier${rang}_salaire`] = nombreBrut(metier.salaire);
    });
    Object.assign(champs, remplacements);
    return Object.entries(champs)
      .map(([cle, valeur]) => `${encodeURIComponent(cle).replace(/%20/g, "+")}`
        + `=${encodeURIComponent(String(valeur)).replace(/%20/g, "+")}`)
      .join("&");
  }
}

/**
 * Les métiers qui suivent le premier, lus dans « metier2_… », « metier3_… ».
 *
 * Le formulaire affiche toujours une ligne de plus qu'il n'y a de métiers : tant
 * qu'elle reste vide, elle ne décrit rien. Une ligne partiellement remplie, en
 * revanche, est une intention manquée — elle est refusée, avec ce qui lui manque.
 */
function metiersSaisis(parametres, salairePrecedent) {
  const metiers = [];
  let salaire = salairePrecedent;
  for (let rang = 2; rang <= METIERS_MAXIMUM; rang += 1) {
    const debutBrut = String(parametres[`metier${rang}_debut`] ?? "").trim();
    const statut = String(parametres[`metier${rang}_statut`] ?? "").trim();
    const salaireBrut = String(parametres[`metier${rang}_salaire`] ?? "").trim();
    if (!debutBrut && !statut && !salaireBrut) {
      continue;
    }
    if (!debutBrut) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : indiquer l'âge auquel il commence, ou laisser sa `
        + "ligne entièrement vide.",
      );
    }
    if (!statut) {
      throw new ErreurSaisie(`Métier n° ${rang} : indiquer le statut d'affiliation.`);
    }
    salaire = reel(parametres, `metier${rang}_salaire`, salaire);
    metiers.push({
      debut: reel(parametres, `metier${rang}_debut`, 0.0),
      statut,
      salaire,
    });
  }
  return metiers;
}

function cleEnum(enumeration, valeur) {
  const cle = Object.keys(enumeration).find((nom) => enumeration[nom] === valeur);
  if (cle === undefined) {
    throw new ErreurSaisie(`valeur inconnue : ${valeur}`);
  }
  return cle;
}

const NOMBRE = /^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/;

function versFlottant(texte) {
  const propre = String(texte).trim();
  if (!NOMBRE.test(propre)) {
    return null;
  }
  return Number(propre);
}

function estEntier(texte) {
  return /^\s*[+-]?\d+\s*$/.test(String(texte ?? ""));
}

function entier(parametres, nom, defaut) {
  const valeur = parametres[nom];
  if (valeur === undefined || valeur === null || valeur === "") {
    return defaut;
  }
  const flottant = versFlottant(valeur);
  if (flottant === null) {
    throw new ErreurSaisie(`« ${nom} » doit être un nombre entier (reçu : ${valeur}).`);
  }
  return Math.trunc(flottant);
}

function reel(parametres, nom, defaut) {
  const valeur = parametres[nom];
  if (valeur === undefined || valeur === null || valeur === "") {
    return defaut;
  }
  const flottant = versFlottant(String(valeur).replace(/,/g, "."));
  if (flottant === null) {
    throw new ErreurSaisie(`« ${nom} » doit être un nombre (reçu : ${valeur}).`);
  }
  return flottant;
}

function parmi(parametres, nom, options, defaut) {
  const valeur = parametres[nom];
  return options.some(([code]) => code === valeur) ? valeur : defaut;
}

/** Valeur telle qu'elle est réinjectée dans un champ de formulaire. */
function nombreBrut(valeur) {
  return formatG(valeur);
}

/**
 * Âge lu en années entières plus un nombre de mois.
 *
 * Le formulaire envoie deux champs — `liquidation` et `liquidation_mois` —, et
 * l'adresse les porte tous deux. Une adresse ancienne ne portant qu'un âge
 * décimal reste valide et vaut ce qu'elle a toujours valu.
 */
function ageSaisi(parametres, nom, defaut) {
  const annees = reel(parametres, nom, defaut);
  const cle = `${nom}_mois`;
  const brut = parametres[cle];
  if (brut === undefined || brut === null || brut === "") {
    return annees;
  }
  const mois = entier(parametres, cle, 0);
  if (!(mois >= 0 && mois <= 11)) {
    throw new ErreurSaisie(`« ${cle} » doit être compris entre 0 et 11 mois.`);
  }
  return Math.floor(annees) + mois / 12;
}

/**
 * Âge à la française, en ans et en mois : « 64 ans », « 64 ans et 9 mois ».
 *
 * Le modèle date la liquidation au mois : l'écrire « 64,75 » demanderait au
 * lecteur de multiplier par douze pour retrouver ce qu'il a saisi.
 */
function age(valeur) {
  return formaterAge(valeur);
}

// -- fabrique ----------------------------------------------------------------

/**
 * Simulateurs mémorisés par jeu de paramètres. Le chargement des données coûte
 * quelques dixièmes de seconde ; une simulation en coûte dix millisecondes.
 */
export class Contexte {
  constructor(paquet, base = PARAMETRES_DEFAUT) {
    this.paquet = paquet;
    this.base = base;
    this._instances = new Map();
    this._depenses = null;
    this._population = null;
    this._cout = null;
  }

  simulateur(parametres = null) {
    const retenus = parametres || this.base;
    const cle = cleParametres(retenus);
    if (!this._instances.has(cle)) {
      this._instances.set(cle, new Simulateur(this.paquet, retenus));
    }
    return this._instances.get(cle);
  }

  depenses() {
    if (!this._depenses) {
      this._depenses = new DepensesRetraite(this.paquet);
    }
    return this._depenses;
  }

  population() {
    if (!this._population) {
      this._population = new Population(this.paquet);
    }
    return this._population;
  }

  /** Le coût agrégé des cinq systèmes — une seconde de calcul, une fois. */
  cout() {
    if (!this._cout) {
      this._cout = calculerCout(
        this.simulateur(), this.depenses(), this.population(),
      );
    }
    return this._cout;
  }

  /**
   * Les séries macroéconomiques du jeu de paramètres d'une saisie. Le
   * formulaire en a besoin pour convertir un montant en multiple du salaire
   * moyen, et il lui faut CELLES-LÀ : au-delà de la dernière année observée, le
   * salaire moyen dépend du scénario de projection choisi.
   */
  macro(saisie) {
    return this.simulateur(saisie.parametres(this.base)).macro;
  }

  simuler(saisie) {
    const simulateur = this.simulateur(saisie.parametres(this.base));
    const parcours = saisie.parcours(simulateur.macro);
    for (const metier of parcours) {
      if (!simulateur.affiliations.contient(metier.affiliation)) {
        throw new ErreurSaisie(
          `Statut d'affiliation inconnu : « ${metier.affiliation} ».`,
        );
      }
    }
    const carriere = simulateur.carriereParcours({
      annee_naissance: saisie.naissance,
      mois_naissance: saisie.naissance_mois,
      sexe: saisie.sexe,
      metiers: parcours,
      age_liquidation: saisie.liquidation,
      profil_carriere: saisie.profil,
      interruptions: saisie.interruptionsAnalysees(),
      nombre_enfants: saisie.enfants,
      part_primes: saisie.primes,
      identifiant: "assuré",
    });
    return simulateur.simuler(carriere);
  }
}

/** Titre de chaque page, dans l'ordre de la navigation. */
export const TITRES = {
  "/": "Simuler",
  "/cas-types": "Cas types",
  "/cout": "Coût",
  "/methode": "Méthode",
  "/donnees": "Données",
};

/**
 * Contenu d'une page : ``[titre, corps HTML]``. Les erreurs de saisie sont
 * rendues dans la page, jamais levées : une adresse mal formée doit afficher un
 * message, pas une trace d'exécution.
 */
export function rendre(contexte, chemin, parametres = null) {
  if (chemin === "/cas-types") {
    return [TITRES[chemin], casTypes(contexte)];
  }
  if (chemin === "/cout") {
    return [TITRES[chemin], cout(contexte)];
  }
  if (chemin === "/methode") {
    return [TITRES[chemin], methode(contexte)];
  }
  if (chemin === "/donnees") {
    return [TITRES[chemin], donnees(contexte)];
  }

  let saisie;
  try {
    saisie = Saisie.depuisRequete(parametres || {});
  } catch (erreur) {
    if (!(erreur instanceof ErreurSaisie)) {
      throw erreur;
    }
    return [TITRES["/"], presentation() + messageErreur(erreur.message)
      + formulaire(new Saisie({ demandee: false }), contexte)];
  }

  let corps = presentation() + formulaire(saisie, contexte);
  if (saisie.demandee) {
    try {
      corps += resultats(contexte, saisie);
    } catch (erreur) {
      // Saisie refusée, données insuffisantes, régime inconnu : le message est
      // rendu dans la page. Une adresse mal formée doit afficher une phrase,
      // pas une trace d'exécution.
      corps += messageErreur(erreur.message);
    }
  }
  return [TITRES["/"], corps];
}

export function statuts(contexte) {
  const affiliations = contexte.simulateur().affiliations;
  return affiliations.codes.map((code) => ({
    code, libelle: affiliations.libelle(code),
  }));
}

// -- fragments ---------------------------------------------------------------

function messageErreur(message) {
  return `<div class="erreur"><strong>Saisie refusée.</strong> ${echapper(message)}</div>`;
}

function presentation() {
  return `
<p class="chapeau">Ce simulateur calcule, pour une même carrière, ce que verse le
système de retraite français tel qu'il est, et ce que verserait un système
en <strong>comptes notionnels</strong> — pension strictement proportionnelle aux
cotisations versées, divisée par l'espérance de vie restante à la liquidation —
appliqué de deux façons : <strong>rétroactivement</strong> depuis 1941, ou
seulement <strong>à compter de 2026</strong>.</p>

<p>Les cinq montants qu'il affiche sont ceux de la <strong>première pension</strong>,
au premier mois de retraite : celle de l'année du départ pour qui est déjà
retraité, celle de l'année du départ à venir pour qui est encore en activité.
Jamais la pension d'aujourd'hui d'un retraité parti il y a vingt ans. Chacun est
donné <strong>deux fois</strong> : en euros d'aujourd'hui, et tel qu'il serait
inscrit sur le virement le mois du départ — la conversion n'est ainsi à refaire
de tête ni dans un sens ni dans l'autre.</p>

<div class="note"><strong>À lire avant les chiffres.</strong> Le scénario
rétroactif n'est pas une proposition de réforme : c'est un contrefactuel, qui
mesure ce qu'aurait produit une règle purement contributive appliquée depuis
l'origine de la répartition. L'essentiel de l'écart qu'il affiche vient de la
<a href="${g.lien("/methode", "indexation")}">règle d'indexation</a>, pas du passage aux comptes
notionnels — le simulateur permet de séparer les deux effets.</div>
`;
}

function formulaire(saisie, contexte) {
  const affiliations = contexte.simulateur().affiliations;
  const listeStatuts = affiliations.codes.map((code) => [code, affiliations.libelle(code)]);

  const identite = [
    g.champ("naissance", "Année de naissance", saisie.naissance, "", "number",
      { min: "1900", max: "2020", step: "1" }),
    g.liste("naissance_mois", "Mois de naissance", MOIS_NAISSANCE,
      String(saisie.naissance_mois),
      "deux générations sont coupées en cours d'année par les textes"),
    g.liste("sexe", "Sexe", [["H", "Homme"], ["F", "Femme"]], saisie.sexe,
      "table de mortalité unisexe par défaut"),
    g.champ("liquidation", "Âge de départ à la retraite",
      Math.floor(enMois(saisie.liquidation) / 12),
      "effectif si vous êtes déjà retraité, souhaité sinon : c'est la date "
      + "à laquelle tout le calcul se place", "number",
      { min: "40", max: "75", step: "1" }),
    g.liste("liquidation_mois", "…et mois", MOIS_AGE,
      String(saisie.liquidation_mois),
      "la pension prend effet le premier du mois"),
  ].join("");

  const avance = [
    g.liste("profil", "Profil de carrière", PROFILS, saisie.profil,
      "déformation du salaire relatif au fil de la carrière"),
    g.champ("primes", "Part de primes", nombreBrut(saisie.primes),
      "fonction publique : assiette du RAFP", "number",
      { min: "0", max: "0.6", step: "0.01" }),
    g.champ("enfants", "Nombre d'enfants", saisie.enfants,
      "sans effet notionnel : les majorations sont supprimées", "number",
      { min: "0", max: "12", step: "1" }),
    g.champ("interruptions", "Interruptions", saisie.interruptions,
      "« 1995:1999:education_enfant », séparées par des virgules"),
    g.liste("indexation", "Règle d'indexation", INDEXATIONS, saisie.indexation,
      "revalorisation des comptes et des pensions"),
    g.champ("lissage", "Lissage de l'indexation", saisie.lissage,
      "moyenne glissante sur la règle choisie, en années : 1 = aucun, "
      + "5 = comme l'Italie",
      "number", { min: "1", max: String(LISSAGE_MAXIMUM), step: "1" }),
    g.liste("age_reference", "Âge de référence", AGES_REFERENCE, saisie.age_reference),
    g.liste("table", "Table de conversion", TABLES, saisie.table),
    g.liste("part_cotisation", "Part de la cotisation portée au compte",
      PARTS_COTISATION, saisie.part_cotisation,
      "salariale seule, ou salariale et patronale"),
    g.liste("conversion_acquis", "Conversion des droits acquis",
      CONVERSIONS_ACQUIS, saisie.conversion_acquis,
      "âge auquel les droits figés à la bascule sont convertis"),
    g.liste("projection", "Scénario macroéconomique", PROJECTIONS, saisie.projection,
      "au-delà de la dernière observation"),
    g.champ("bascule", "Année de bascule", saisie.bascule,
      "passage au régime unique", "number", { min: "1941", max: "2070" }),
    g.champ("euros", "Euros constants de", saisie.euros, "", "number",
      { min: "1941", max: "2070" }),
  ].join("");

  return `
<form class="carte" method="get" action="${g.lien("/")}">
  <h2 style="margin-top:0">Simuler une carrière</h2>
  <div class="grille">${identite}</div>
  <h3>Les métiers exercés</h3>
  <p class="discret">On faisait autrefois le même métier toute sa vie ; c'est
  devenu l'exception. Chaque changement fait passer d'un régime à un autre, donc
  d'un taux de cotisation et d'un barème à un autre — et c'est exactement ce
  qu'un compte notionnel enregistre. Ajouter un métier, c'est remplir la
  dernière ligne ; une carrière d'un seul métier la laisse vide.</p>
  ${choixUnite(saisie)}
  ${noteBrutOuNet()}
  ${reperes(contexte, saisie)}
  ${metiersFormulaire(saisie, listeStatuts)}
  ${echoRevenus(contexte, saisie)}
  <details>
    <summary>Options de modélisation (profil, indexation, âge de référence, projection)</summary>
    <div class="grille">${avance}</div>
  </details>
  <p style="margin-top:1.4rem"><button type="submit">Calculer les cinq scénarios</button></p>
</form>
`;
}

// Comment chaque unité se dit à la suite d'un nombre.
const LIBELLES_UNITE = {
  moyen: "fois le salaire moyen",
  euros_mois: "€ bruts par mois",
  euros_an: "€ bruts par an",
  francs_mois: "F bruts par mois",
  francs_an: "F bruts par an",
};

function libelleUnite(unite) {
  return LIBELLES_UNITE[unite];
}

/**
 * Un refus, daté du métier qu'il concerne quand il y en a plusieurs. La phrase
 * est écrite une fois, avec sa majuscule ; le rang la fait passer au milieu
 * d'une autre, où la majuscule n'a plus lieu d'être. Écrire les deux versions à
 * la main les laisserait diverger.
 */
function refus(rang, phrase) {
  if (rang === 1) {
    return new ErreurSaisie(phrase);
  }
  return new ErreurSaisie(
    `Métier n° ${rang} : ${phrase.charAt(0).toLowerCase()}${phrase.slice(1)}`,
  );
}

/**
 * Combien de francs de `annee` valaient un euro. Le taux légal, 6,559 57, ne
 * vaut que pour le franc issu du décret de 1958. Avant 1960, un salaire
 * s'écrivait en anciens francs, cent fois plus petits : convertir « 60 000 F par
 * mois en 1955 » au taux du nouveau franc donnerait neuf mille euros là où il
 * faut en lire quatre-vingt-onze.
 */
function francsParEuro(annee) {
  return annee >= ANNEE_NOUVEAU_FRANC ? FRANCS_PAR_EURO : FRANCS_PAR_EURO * 100;
}

/** Un montant saisi, ramené à des euros bruts ANNUELS de son année. */
function eurosAnnuels(unite, valeur, annee) {
  let montantAnnuel = valeur;
  if (unite === "euros_mois" || unite === "francs_mois") {
    montantAnnuel *= MOIS_PAR_AN;
  }
  if (unite.startsWith("francs")) {
    montantAnnuel /= francsParEuro(annee);
  }
  return montantAnnuel;
}

/** L'opération inverse : des euros annuels réécrits dans l'unité saisie. */
function depuisEurosAnnuels(unite, euros_, annee) {
  let valeur = euros_;
  if (unite.startsWith("francs")) {
    valeur *= francsParEuro(annee);
  }
  if (unite === "euros_mois" || unite === "francs_mois") {
    valeur /= MOIS_PAR_AN;
  }
  return valeur;
}

/**
 * Une somme en euros de `annee_revenu`, écrite dans la monnaie affichée.
 * `mensuel` divise par douze : l'appelant passe des euros annuels, parce que
 * c'est l'unité de tout ce que le modèle porte au compte, et le lecteur lit des
 * salaires mensuels.
 */
function montant(saisie, euros_, mensuel = true, decimales = 0) {
  const francs = saisie.revenu_en_francs;
  let valeur = euros_ * (francs ? francsParEuro(saisie.annee_revenu) : 1.0);
  if (mensuel) {
    valeur /= MOIS_PAR_AN;
  }
  return g.nombre(valeur, decimales) + (francs ? "\u202fF" : "\u202f\u20ac");
}

/**
 * Le champ « combien gagnez-vous », dans l'unité que l'utilisateur a choisie.
 * Le libellé porte le mot « brut » dès qu'un montant est saisi : c'est la
 * question qui revenait le plus souvent devant ce formulaire, et une aide
 * dépliée sous le champ ne suffisait pas à y répondre — elle se lit après.
 */
function champRevenu(nom, saisie, valeur, bref = false) {
  if (!saisie.revenu_en_montant) {
    // Le repère chiffré du SMIC n'est pas répété ici : il est calculé juste
    // au-dessus, pour l'année choisie, et une valeur écrite en dur dans cette
    // aide finirait par ne plus lui correspondre.
    const aide = bref
      ? "en multiples du salaire moyen brut"
      : "en multiples du salaire moyen BRUT : 1 = salaire moyen, "
        + "et les repères ci-dessus donnent l'échelle";
    return g.champ(nom, "Niveau de revenu", valeur, aide, "number",
      { min: "0.1", max: "10", step: "0.05" });
  }
  const mensuel = saisie.unite_revenu.endsWith("_mois");
  const libelle = mensuel ? "Revenu brut mensuel" : "Revenu brut annuel";
  const monnaie = saisie.revenu_en_francs ? "francs" : "euros";
  let aide = `en ${monnaie} de ${saisie.annee_revenu}`;
  if (!bref) {
    aide += ", avant cotisations salariales et avant impôt";
  }
  return g.champ(nom, libelle, valeur, aide, "number", { min: "0", step: "1" });
}

/**
 * Le choix d'unité, une fois pour toute la carrière. Il précède les métiers
 * plutôt qu'il ne les accompagne : une unité par métier n'aurait décrit aucune
 * carrière réelle, et aurait multiplié par six la question à laquelle ce bloc
 * répond.
 */
function choixUnite(saisie) {
  return `<div class="grille">${
    g.liste("unite_revenu", "Revenus saisis", UNITES_REVENU, saisie.unite_revenu,
      "le modèle ne connaît que le multiple du salaire moyen ; "
      + "il convertit les montants lui-même")
  }${
    g.champ("annee_revenu", "…de l'année", saisie.annee_revenu,
      "l'année dont les montants saisis sont ceux-là, et celle des repères "
      + "ci-dessous", "number", { min: "1941", max: "2070", step: "1" })
  }</div>`;
}

/**
 * La réponse à « brut ou net ? », écrite une fois et placée là où on la pose.
 * Le simulateur raisonne de bout en bout sur des montants bruts : c'est
 * l'assiette des cotisations, donc la seule grandeur qu'un compte notionnel
 * puisse enregistrer. Rien ne le disait, et la question revenait à chaque
 * lecture — assez souvent pour valoir un encadré plutôt qu'une incise.
 */
function noteBrutOuNet() {
  return '<div class="note"><strong>Brut, jamais net.</strong> Le revenu attendu '
    + "ici est le <strong>salaire brut</strong> — la ligne « brut » du "
    + "bulletin de paie : <strong>avant</strong> cotisations salariales, "
    + "<strong>avant</strong> CSG et CRDS, <strong>avant</strong> impôt sur "
    + "le revenu. Les cotisations patronales, elles, n'en font pas partie : "
    + "elles s'ajoutent au brut, elles n'en sont pas déduites. C'est la "
    + "définition des comptes nationaux (salaires et traitements bruts, D11) "
    + "et c'est l'assiette sur laquelle les régimes appellent leurs "
    + "cotisations — donc la seule grandeur qu'un compte notionnel puisse "
    + "enregistrer. Les pensions affichées plus bas sont brutes elles aussi : "
    + "les deux se comparent directement. À titre d'ordre de grandeur, un "
    + "salaire net avant impôt vaut aujourd'hui un peu moins de 80 % du brut "
    + "dans le privé ; le simulateur ne fait pas cette conversion, qui dépend "
    + "du statut, du régime et de l'année.</div>";
}

/**
 * Les trois montants qui donnent l'échelle : salaire moyen, SMIC, plafond. Sans
 * eux, « 1 = salaire moyen » n'est une information pour personne. Ils sont
 * écrits dans l'unité choisie — en francs si c'est en francs qu'on saisit —,
 * sans quoi le repère resterait à convertir de tête, ce qui est exactement le
 * travail dont ce formulaire dispense.
 */
function reperes(contexte, saisie) {
  const macro = contexte.macro(saisie);
  const annee = saisie.annee_revenu;
  const moyen = salaireMoyenAnnuel(macro, annee);

  const lignes = [
    `salaire moyen <strong>${montant(saisie, moyen)}</strong> par mois, `
    + `soit ${montant(saisie, moyen, false)} par an`,
  ];
  // Le SMIC n'existe qu'à partir de 1970 ; avant lui le SMIG, qui n'est pas la
  // même grandeur et que le modèle ne porte pas. Mieux vaut un repère de moins
  // qu'un repère faux.
  if (annee >= ANNEE_SMIC_MENSUEL) {
    const smic = HEURES_SMIC_PAR_MOIS * MOIS_PAR_AN * macro.smic_horaire.valeur(annee);
    lignes.push(`SMIC ${montant(saisie, smic)} par mois `
      + `(×${g.nombre(smic / moyen, 2)})`);
  } else if (annee >= macro.smic_horaire.premiereAnnee) {
    lignes.push(`SMIC ${
      montant(saisie, macro.smic_horaire.valeur(annee), false, 2)
    } de l'heure`);
  }
  const plafond = macro.plafond_securite_sociale.valeur(annee);
  lignes.push(`plafond de la Sécurité sociale ${montant(saisie, plafond)} par mois `
    + `(×${g.nombre(plafond / moyen, 2)})`);

  return `<p class="discret">Repères pour ${annee}, tous bruts : `
    + `${lignes.join(" · ")}.</p>`;
}

/**
 * Ce que devient, dans l'autre unité, chaque revenu saisi. La conversion est
 * faite par la page ; la montrer est ce qui la rend vérifiable. Elle dit aussi
 * ce que le profil de carrière fera du niveau saisi : sans cela, saisir
 * « 2 500 € par mois » se lit comme la promesse de gagner 2 500 € chaque année
 * de sa vie, ce que le modèle ne fait jamais.
 */
function echoRevenus(contexte, saisie) {
  const macro = contexte.macro(saisie);
  const annee = saisie.annee_revenu;
  const moyen = salaireMoyenAnnuel(macro, annee);
  const niveaux = saisie.niveaux(macro);

  // Chaque revenu est redit dans l'AUTRE unité que celle où il a été écrit :
  // répéter un montant en francs à qui vient de saisir des francs n'apprend
  // rien, et c'est le rapport au salaire moyen qui manque. Inversement, un
  // multiple ne dit rien tant qu'il n'est pas chiffré.
  const lectures = niveaux.map((niveau, index) => {
    const rappel = niveaux.length === 1 ? "" : `${RANGS_METIER[index]} métier, `;
    if (saisie.revenu_en_montant) {
      const saisi = index === 0 ? saisie.salaire : saisie.metiers[index - 1].salaire;
      return `${rappel}${g.nombre(saisi, 0)} `
        + `${libelleUnite(saisie.unite_revenu)} de ${annee} = `
        + `<strong>${g.nombre(niveau, 2)} fois le salaire moyen</strong> `
        + "de cette année-là";
    }
    return `${rappel}${g.nombre(niveau, 2)} fois le salaire moyen de ${annee} `
      + `= <strong>${montant(saisie, niveau * moyen)} bruts par mois</strong>`;
  });

  const [debut, fin] = bornesDeformation(saisie.profil);
  const profil = debut === fin
    ? "le profil de carrière « plat » l'applique tel quel à toutes les années"
    : `le profil de carrière choisi le fait varier de ×${g.nombre(debut, 2)} au `
      + `premier emploi à ×${g.nombre(fin, 2)} au dernier`;
  return `<p class="discret">Ce qui est porté au compte : ${lectures.join(" ; ")}. `
    + "Ce niveau suit ensuite le salaire moyen d'année en année, et "
    + `${profil}.</p>`;
}

/**
 * Une ligne par métier, plus une ligne vide pour en ajouter un.
 *
 * C'est ce qui permet d'allonger la carrière sans une ligne de JavaScript : la
 * ligne vide est renvoyée avec le reste du formulaire, et devient un métier dès
 * qu'on la remplit. Une ligne de plus apparaît alors à sa suite, jusqu'à
 * ``METIERS_MAXIMUM``.
 */
function metiersFormulaire(saisie, statuts) {
  const lignes = [ligneMetier(
    1,
    g.champ("debut", "Âge de début d'activité",
      Math.floor(enMois(saisie.debut) / 12), "", "number",
      { min: "14", max: "40", step: "1" })
    + g.liste("debut_mois", "…et mois", MOIS_AGE, String(saisie.debut_mois),
      "l'année d'entrée n'est complète que si l'on entre en janvier")
    + g.liste("statut", "Statut d'affiliation", statuts, saisie.statut)
    + champRevenu("salaire", saisie, nombreBrut(saisie.salaire)),
  )];

  saisie.metiers.forEach((metier, index) => {
    const rang = index + 2;
    lignes.push(ligneMetier(rang, champsMetier(
      rang, nombreBrut(metier.debut), metier.statut,
      nombreBrut(metier.salaire), statuts, saisie,
    )));
  });

  // La ligne vide : elle n'existe que tant qu'il reste de la place, et son
  // statut n'est pas présélectionné — un statut choisi par défaut ferait naître
  // un métier que personne n'a demandé.
  const rang = saisie.metiers.length + 2;
  if (rang <= METIERS_MAXIMUM) {
    lignes.push(ligneMetier(
      rang, champsMetier(rang, "", "", "", statuts, saisie), true,
    ));
  }

  return `<div class="metiers">${lignes.join("")}</div>`;
}

/**
 * Les trois champs d'un métier qui suit le premier.
 *
 * Le mois du changement n'est pas demandé : ce qui se date au mois, c'est
 * l'entrée dans la vie active et le départ à la retraite, parce que ces deux
 * bornes tronquent une année civile. Un changement de métier, lui, ne fait que
 * déplacer des mois d'un statut à l'autre à l'intérieur de la carrière.
 */
function champsMetier(rang, debut, statut, salaire, statuts, saisie) {
  return g.champ(`metier${rang}_debut`, "Âge du changement", debut,
    "âge auquel ce métier commence", "number",
    { min: "14", max: "75", step: "1" })
    + g.liste(`metier${rang}_statut`, "Statut d'affiliation",
      [["", "— aucun —"], ...statuts], statut)
    + champRevenu(`metier${rang}_salaire`, saisie, salaire, true);
}

function ligneMetier(rang, champs, vide = false) {
  const titre = vide
    ? "Un autre métier ?"
    : `${majuscule(RANGS_METIER[rang - 1])} métier`;
  const classe = vide ? "metier facultatif" : "metier";
  return `<div class="${classe}"><p class="rang">${echapper(titre)}</p>`
    + `<div class="grille">${champs}</div></div>`;
}

function majuscule(texte) {
  return texte.charAt(0).toUpperCase() + texte.slice(1);
}

/**
 * La suite des métiers, en une phrase — et la convention qui la borne. Muet
 * pour une carrière d'un seul métier : il n'y a rien à récapituler, le
 * formulaire juste au-dessus le dit déjà.
 */
function resumeParcours(contexte, saisie) {
  const parcours = saisie.parcours(contexte.macro(saisie));
  if (parcours.length < 2) {
    return "";
  }
  const affiliations = contexte.simulateur().affiliations;
  const bornes = [...parcours.map((metier) => metier.age_debut), saisie.liquidation];
  const etapes = parcours.map((metier, rang) => (
    `${echapper(affiliations.libelle(metier.affiliation))} de ${age(bornes[rang])} `
    + `à ${age(bornes[rang + 1])}`
  ));
  return `<p class="discret">Carrière en ${parcours.length} métiers : `
    + etapes.join(", puis ")
    + ". L'année d'un changement revient au métier qui en occupe le plus de "
    + "mois — les régimes liquident à l'année, et une année n'a qu'un statut — "
    + "mais le revenu porté au compte reste la somme de ce que les deux ont "
    + "payé.</p>";
}

/**
 * À quelle date se rapportent les montants affichés, et en quels euros.
 *
 * C'est la première question que pose un lecteur devant les cinq barres :
 * « ce nombre, c'est celui de quand ? ». Deux conventions y répondent, dont
 * aucune ne va de soi. Le moteur ne calcule qu'une pension AU MOMENT DE LA
 * LIQUIDATION — il n'existe aucune phase postérieure qu'il revaloriserait —,
 * et il l'exprime en euros constants. Autrement dit : jamais la pension
 * d'aujourd'hui d'un retraité, toujours celle de son premier mois de retraite ;
 * et jamais le montant nominal que porte un relevé bancaire, toujours son
 * pouvoir d'achat ramené à une année de référence.
 *
 * Les deux conventions se disent différemment selon que le départ est passé ou
 * à venir, parce que ce qu'elles écartent n'est pas le même : pour un actif,
 * les revalorisations à venir de sa pension ; pour un retraité, celles qu'il a
 * déjà reçues. La seconde convention, elle, n'est plus une convention muette :
 * les deux unités sont affichées l'une à côté de l'autre, et ce paragraphe n'a
 * qu'à dire laquelle est laquelle.
 */
function lectureDesMontants(comparaison, saisie) {
  const carriere = comparaison.carriere;
  const annee = carriere.anneeLiquidation;
  const date = echapper(String(carriere.dateLiquidation));
  const courante = comparaison.parametres.annee_courante;

  let quand;
  if (annee > courante) {
    quand = "Vous n'êtes pas encore à la retraite : ces montants sont ceux de "
      + "votre <strong>première pension</strong>, celle du mois où vous "
      + `partiriez — ${date} —, et non d'une pension que vous toucheriez `
      + "aujourd'hui.";
  } else if (annee < courante) {
    quand = "Vous êtes déjà à la retraite : ces montants sont ceux de votre "
      + `pension <strong>au moment du départ</strong> — ${date} —, et non `
      + `de celle que vous touchez aujourd'hui. Depuis ${annee}, votre `
      + "pension a été revalorisée chaque année ; le simulateur s'arrête au "
      + "jour de la liquidation et ne suit aucune de ces revalorisations.";
  } else {
    quand = "Vous liquidez cette année : ces montants sont ceux de votre "
      + `<strong>première pension</strong>, celle de ${date}. Le simulateur `
      + "s'arrête là et ne suit pas les revalorisations des années "
      + "suivantes.";
  }

  let unites;
  if (annee > saisie.euros) {
    unites = "Chaque scénario les donne dans deux unités : la somme telle "
      + `qu'elle serait versée en ${annee}, l'inflation d'ici là comprise, `
      + `et cette même somme ramenée au pouvoir d'achat de ${saisie.euros} `
      + "— plus petite, sans rien acheter de moins. C'est ce pouvoir "
      + "d'achat, et non le nombre inscrit sur le virement, qui dit ce que "
      + "vaut la pension : il est mis en avant pour cette raison.";
  } else if (annee < saisie.euros) {
    unites = "Chaque scénario les donne dans deux unités : la somme telle "
      + `qu'elle a été versée en ${annee}, en euros de l'époque, et cette `
      + `même somme ramenée au pouvoir d'achat de ${saisie.euros} — c'est `
      + "celle-là qui est mise en avant, parce qu'elle seule se compare aux "
      + "prix que vous connaissez.";
  } else {
    unites = `Le départ tombe sur ${saisie.euros}, l'année de référence : les `
      + "deux unités de la page se confondent, et chaque scénario n'affiche "
      + "qu'un chiffre.";
  }

  return `
<div class="note"><strong>De quand sont ces chiffres ?</strong> ${quand}
${unites}
Ce que compare cette page, ce sont cinq façons de CALCULER une pension de
départ, pas cinq façons de la revaloriser ensuite : le premier mois de retraite
est le seul instant où les cinq scénarios se laissent mettre côte à côte, et
c'est donc à cet instant que tous les cinq sont calculés.</div>
<p class="discret" style="margin-top:1.5rem">Montants <strong>bruts</strong>
mensuels — avant CSG, CRDS et prélèvements sociaux, avant impôt sur le revenu —
comme le revenu d'activité saisi plus haut : le taux de remplacement rapporte
donc un brut à un brut, et il est plus bas qu'un taux calculé sur des nets, la
pension étant moins prélevée que le salaire. Le chiffre mis en avant est en
euros constants de ${saisie.euros}, c'est-à-dire au pouvoir d'achat de
${saisie.euros} : seule unité qui permette de comparer des liquidations d'années
différentes. Fiabilité du résultat :
<span class="etiquette-fiabilite">${echapper(nomFiabilite(comparaison.fiabilite))}</span></p>`;
}

/**
 * Ce que sont les deux nombres qu'affiche chaque scénario.
 *
 * Elle se lit AVANT les barres, parce qu'elle répond à ce que le lecteur voit
 * d'abord — deux montants là où il en attendait un —, quand le bloc « de quand
 * sont ces chiffres ? » qui la suit répond, lui, à la convention de date.
 * Muette quand le départ tombe sur l'année de référence : il n'y a alors qu'un
 * chiffre, et rien à distinguer.
 */
function legendeDesUnites(comparaison, saisie) {
  const annee = comparaison.carriere.anneeLiquidation;
  if (annee === saisie.euros) return "";

  const date = echapper(String(comparaison.carriere.dateLiquidation));
  const valeur = saisie.euros === comparaison.parametres.annee_courante
    ? "ce que la pension vaudrait aujourd'hui"
    : `ce que la pension vaudrait en euros de ${saisie.euros}`;
  const autre = annee > saisie.euros
    ? `la somme qui serait inscrite sur le virement de ${date}, inflation d'ici `
      + "là comprise"
    : "la somme réellement versée le mois du départ, en euros de l'époque — "
      + `${date}`;
  return '<p class="discret" style="margin:0 0 1.4rem">Deux fois le même montant, '
    + `dans deux unités : le <strong>grand chiffre</strong> est ${valeur} — le `
    + "seul qui se compare à un salaire ou à un loyer que vous connaissez ; "
    + `celui d'à côté est ${autre}.</p>`;
}

function resultats(contexte, saisie) {
  const comparaison = contexte.simuler(saisie);
  const carriere = comparaison.carriere;
  const retro = comparaison.notionnel_retroactif;
  const ecart = retro.ecart_age;
  const conversion = retro.conversion;

  // Le moteur ne calcule qu'un montant, en euros de l'année de liquidation. La
  // page en affiche deux : celui-là, tel qu'il tomberait sur le relevé bancaire
  // le mois du départ, et le même ramené au pouvoir d'achat de l'année de
  // référence. Le second est le seul qui se compare à un salaire ou à un loyer
  // que le lecteur connaît ; c'est donc lui qui est mis en avant, l'autre à
  // côté pour que la conversion n'ait pas à être refaite de tête.
  const courants = {
    actuel: comparaison.actuel.pension_annuelle,
    retroactif: retro.pension_annuelle,
    prospectif: comparaison.notionnel_prospectif.pension_annuelle,
    "retroactif-employeur":
      comparaison.notionnel_retroactif_employeur.pension_annuelle,
    "prospectif-employeur":
      comparaison.notionnel_prospectif_employeur.pension_annuelle,
  };
  const constants = {};
  for (const [cle, montant] of Object.entries(courants)) {
    constants[cle] = comparaison.enEurosConstants(montant);
  }
  const reference = Math.max(...Object.values(constants)) || 1.0;

  // Les deux unités ne se distinguent que si le départ tombe ailleurs que sur
  // l'année de référence : sinon le coefficient vaut un, et afficher deux fois
  // le même nombre n'apprendrait rien.
  const anneeDepart = carriere.anneeLiquidation;
  const deuxUnites = anneeDepart !== saisie.euros;
  const uniteReference = saisie.euros === comparaison.parametres.annee_courante
    ? "par mois, en euros d'aujourd'hui"
    : `par mois, en euros de ${saisie.euros}`;

  const bloc = (cle, titre, glose, variation, tauxRemplacement) => {
    const montant = constants[cle];
    const variationHtml = variation === null
      ? '<span class="discret">référence</span>'
      : `<strong>${g.pourcentage(variation, true)}</strong>`;
    const depart = deuxUnites ? `
      <span class="chiffre depart">
        <span class="somme">${g.euros(courants[cle] / 12)}</span>
        <span class="unite">par mois, en euros de ${anneeDepart}</span>
      </span>` : "";
    return `
<div class="scenario">
  <div class="entete">
    <span class="titre">${echapper(titre)}</span>
    <span class="montant">
      <span class="chiffre principal">
        <span class="somme">${g.euros(montant / 12)}</span>
        <span class="unite">${uniteReference}</span>
        <span class="annuel">${g.euros(montant)} par an</span>
      </span>${depart}
    </span>
  </div>
  <div class="barre ${cle}"><span style="width:${formatFixe(montant / reference * 100, 1)}%"></span></div>
  <div class="glose">${glose} · taux de remplacement
    ${g.pourcentage(tauxRemplacement)} · écart au système actuel : ${variationHtml}</div>
</div>`;
  };

  const scenarios = bloc("actuel", "1. Système actuel",
    "droit en vigueur, minima et majorations compris",
    null, comparaison.tauxRemplacementActuel)
    + bloc("retroactif", "2. Comptes notionnels, rétroactifs depuis 1941",
      "toute la carrière recalculée sur la seule part salariale",
      comparaison.variation("notionnel_retroactif"),
      comparaison.tauxRemplacementRetroactif)
    + bloc("prospectif", `3. Comptes notionnels à compter de ${saisie.bascule}`,
      "droits acquis conservés, règles notionnelles ensuite",
      comparaison.variation("notionnel_prospectif"),
      comparaison.tauxRemplacementProspectif)
    + bloc("retroactif-employeur",
      "4. Comptes notionnels rétroactifs, salariale + patronale",
      "le scénario 2, la part patronale en plus",
      comparaison.variation("notionnel_retroactif_employeur"),
      comparaison.tauxRemplacement("notionnel_retroactif_employeur"))
    + bloc("prospectif-employeur",
      `5. Comptes notionnels à compter de ${saisie.bascule}, salariale + patronale`,
      "le scénario 3, la part patronale en plus",
      comparaison.variation("notionnel_prospectif_employeur"),
      comparaison.tauxRemplacement("notionnel_prospectif_employeur"));

  const anticipation = `départ ${g.nombre(Math.abs(ecart.ecart), 2).replace(/0+$/, "").replace(/,$/, "")} ans `
    + (ecart.anticipe ? "plus tôt" : "plus tard");
  const fiches = [
    g.fiche("années cotisées", String(carriere.anneesCotisees.length)),
    // La date, et pas seulement l'année : la pension prend effet le premier du
    // mois, et c'est ce mois que l'utilisateur vient de choisir.
    g.fiche("liquidation", `${age(carriere.age_liquidation)} `
      + `<span class="discret">en ${carriere.dateLiquidation}</span>`),
    g.fiche(`âge de référence — ${anticipation}`, `${age(ecart.age_reference)}`),
    g.fiche("coefficient de conversion", g.nombre(conversion.diviseur, 1)),
    g.fiche("capital notionnel rétroactif", g.euros(retro.capital_notionnel)),
  ].join("");

  let capitalisation = "";
  if (comparaison.actuel.pension_hors_repartition > 0) {
    const montant = comparaison.enEurosConstants(
      comparaison.actuel.pension_hors_repartition,
    );
    capitalisation = '<p class="discret">Hors répartition, servi à part : '
      + `${g.euros(montant / 12)} par mois de RAFP. Ce régime est PROVISIONNÉ `
      + "— sa rente sort d'un placement, non de la cotisation des actifs —, si "
      + "bien qu'une réforme de la répartition ne l'atteint pas. Il est donc "
      + "retiré des cinq totaux et servi à l'identique dans les cinq "
      + "scénarios : c'est la seule façon de comparer ce qui est comparable.</p>";
  }

  let minimum = "";
  if (comparaison.actuel.minimum_applique) {
    minimum = '<p class="discret">Le minimum contributif s\'applique dans le '
      + "scénario 1 ; il est supprimé dans les scénarios 2 à 5.</p>";
  }

  let ouverture = "";
  if (!comparaison.actuel.liquidation_ouverte) {
    const age = comparaison.actuel.age_ouverture_opposable;
    const attente = age === null ? "" : ` — il faut attendre ${g.nombre(age, 2)} ans`;
    ouverture = '<p class="note avertissement">Le droit en vigueur <strong>n\'ouvre pas'
      + "</strong> cette liquidation à "
      + `${g.nombre(comparaison.carriere.age_liquidation, 2)} ans${attente}. `
      + "Ni l'âge légal du régime, ni le départ anticipé pour carrière longue "
      + "ne le permettent. Le montant du scénario 1 reste calculé, parce qu'il "
      + "faut bien comparer les cinq scénarios sur la même carrière, mais il "
      + "ne décrit aucune pension que le système actuel servirait.</p>";
  }

  return `
<h2>Résultats</h2>
<div class="carte">
  <div class="fiches">${fiches}</div>
  ${resumeParcours(contexte, saisie)}
</div>
<div class="carte">
  ${legendeDesUnites(comparaison, saisie)}
  ${scenarios}
  ${lectureDesMontants(comparaison, saisie)}
  ${capitalisation}
  ${minimum}
  ${ouverture}
</div>
${fourchette(contexte, saisie, comparaison)}
${decomposition(contexte, saisie, comparaison)}
${contributionEmployeur(comparaison)}
${cascade(comparaison, saisie)}
${detail(contexte, comparaison)}
`;
}

/**
 * Les cinq scénarios, dans l'ordre où la page les affiche, avec le libellé
 * court que la fourchette leur donne.
 */
const SCENARIOS_AFFICHES = [
  ["actuel", "1. Système actuel"],
  ["notionnel_retroactif", "2. Notionnel rétroactif"],
  ["notionnel_prospectif", "3. Notionnel à la bascule"],
  ["notionnel_retroactif_employeur", "4. Rétroactif, avec le patronal"],
  ["notionnel_prospectif_employeur", "5. Bascule, avec le patronal"],
];

/**
 * Ce que l'hypothèse de productivité pèse dans le résultat affiché.
 *
 * Un montant unique se lit comme une prévision. Il n'en est pas une dès qu'une
 * année de la carrière tombe après la dernière observation : il est alors la
 * conséquence d'un scénario, et le lecteur doit voir laquelle.
 *
 * Le bloc rejoue donc la même carrière sous les trois hypothèses du COR et
 * donne l'écart. Quand la liquidation précède la dernière année observée, il
 * n'y a rien à faire varier — et c'est la chose la plus utile qu'on puisse dire
 * à quelqu'un qui redoute les hypothèses : son chiffre n'en contient aucune.
 */
function fourchette(contexte, saisie, comparaison) {
  const macro = contexte.simulateur(saisie.parametres(contexte.base)).macro;
  const derniereObservee = macro.derniereAnneeObservee;
  const carriere = comparaison.carriere;
  const cotisees = carriere.anneesCotisees;
  const liquidation = carriere.anneeLiquidation;
  const debut = cotisees.length ? Math.min(...cotisees) : liquidation;
  const total = liquidation - debut + 1;
  const projetees = Math.max(0, liquidation - Math.max(debut - 1, derniereObservee));

  if (!projetees) {
    return `
<h2>Ce que l'hypothèse pèse</h2>
<p class="note">Rien, ici : la carrière s'achève en ${liquidation}, et les séries
sont observées jusqu'en ${derniereObservee}. <strong>Aucune année projetée
n'entre dans ce calcul</strong> — les montants ci-dessus sont identiques dans
les trois scénarios macroéconomiques, parce qu'aucun d'eux ne s'y applique.</p>`;
  }

  const montants = new Map();
  for (const [code] of PROJECTIONS) {
    let variante;
    try {
      variante = code === saisie.projection
        ? comparaison
        : contexte.simuler(new Saisie({ ...saisie, projection: code }));
    } catch (erreur) {
      continue;
    }
    const par_scenario = {};
    for (const [scenario] of SCENARIOS_AFFICHES) {
      par_scenario[scenario] = variante.enEurosConstants(
        variante[scenario].pension_annuelle,
      );
    }
    montants.set(code, par_scenario);
  }

  const basse = montants.get("cor_productivite_basse");
  const haute = montants.get("cor_productivite_haute");
  if (!basse || !haute) {
    return "";
  }
  const retenus = montants.get(saisie.projection);

  const lignes = SCENARIOS_AFFICHES.map(([scenario, libelle]) => {
    const bas = basse[scenario];
    const haut = haute[scenario];
    const amplitude = bas > 0 ? haut / bas - 1 : NaN;
    return [
      echapper(libelle),
      g.euros(bas / 12),
      retenus ? g.euros(retenus[scenario] / 12) : "—",
      g.euros(haut / 12),
      g.pourcentage(amplitude),
    ];
  });

  const retenu = (PROJECTIONS.find(([code]) => code === saisie.projection)
    || [null, ""])[1];
  const reference = comparaison.enEurosConstants(
    comparaison.notionnel_retroactif.pension_annuelle,
  ) / 12;
  const ecart2 = basse.notionnel_retroactif > 0
    ? haute.notionnel_retroactif / basse.notionnel_retroactif - 1
    : NaN;

  return `
<h2>Ce que l'hypothèse pèse</h2>
<p>Le compte est revalorisé chaque année de ${debut} à ${liquidation}, soit
${total} années — dont <strong>${projetees} après ${derniereObservee}</strong>,
la dernière année observée. Ces ${g.pourcentage(projetees / total)} du calcul ne
reposent sur aucune mesure : elles reposent sur l'hypothèse de croissance de la
productivité, celle que le Conseil d'orientation des retraites fixe et révise.</p>
<p>La même carrière, rejouée sous les trois hypothèses du COR. Le scénario 2
passe de ${g.euros(basse.notionnel_retroactif / 12)} à
${g.euros(haute.notionnel_retroactif / 12)} par mois, soit
<strong>${g.pourcentage(ecart2)} d'amplitude</strong> autour des
${g.euros(reference)} affichés plus haut.</p>
${g.tableau(
    ["Scénario", "Productivité 0,4 %", echapper(retenu), "Productivité 1,0 %",
      "Amplitude"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
  )}
<p class="discret">Montants mensuels bruts, en euros constants de ${saisie.euros}.
La fourchette ne fait varier que la <strong>productivité</strong> — 0,4 %, 0,7 %
et 1,0 % par an, le jeu que le COR retient depuis juin 2025. Elle laisse fixes
les autres hypothèses de la projection, et n'est donc pas un intervalle de
confiance : l'inflation y reste à 1,75 %, l'emploi salarié constant, et la
législation inchangée. C'est une mesure de sensibilité à un paramètre, pas une
borne sur l'avenir — l'avenir peut sortir de cette fourchette.</p>`;
}

const NATURES_PART_EMPLOYEUR = {
  appelee: "contribution appelée par décret ou par arrêté",
  implicite: "taux implicite reconstitué par les documents budgétaires",
  repli: "aucune série publiée : effort du privé de la même année",
};

/**
 * Qui verse la cotisation : l'assuré, son employeur, dans quelle proportion.
 *
 * C'est la mesure directe de ce qui sépare les scénarios 2 et 3 des scénarios 4
 * et 5. Le bloc ne s'affiche pas pour un non-salarié, qui n'a pas d'employeur.
 */
function contributionEmployeur(comparaison) {
  const employeur = comparaison.contributionEmployeur;
  if (!(employeur.a_un_employeur || employeur.concerne_un_regime_public)) {
    return "";
  }

  const partage = employeur.a_un_employeur
    ? g.tableau(
      ["Sur toute la carrière, en euros courants cumulés", "", "Montant"],
      [
        ["Part salariale", "ce que l'assuré supporte — scénarios 2 et 3",
          g.euros(employeur.agent)],
        ["Part patronale", "ce que verse l'employeur", g.euros(employeur.employeur)],
        ["Total", "scénarios 4 et 5", g.euros(employeur.total)],
      ],
      ["", "", "nombre"],
    ) + `<p>L'employeur verse ici <strong>${g.pourcentage(employeur.part)}`
      + "</strong> du total.</p>"
    : "";

  // La part patronale d'un agent public n'est dans aucune fiche : elle vient
  // d'une série à part, qui ne couvre pas tous les régimes ni toutes les
  // années. Le dire est le prix de s'en servir.
  let public_ = "";
  if (employeur.concerne_un_regime_public) {
    const origines = Object.entries(employeur.annees_par_origine)
      .sort((a, b) => (a[0] < b[0] ? -1 : 1))
      .map(([origine, nombre]) => `<li>${
        echapper(NATURES_PART_EMPLOYEUR[origine] ?? origine)
      } — ${nombre} année${nombre > 1 ? "s" : ""}</li>`)
      .join("");
    public_ = `
<p>Les fiches de la fonction publique et des régimes spéciaux ne portent que la
<strong>retenue de l'agent</strong>. La part de l'employeur vient d'une série à
part — reconstituée par les documents budgétaires de 1995 à 2005, appelée par
décret depuis 2006 pour l'État, versée à une caisse depuis 1948 pour la fonction
publique territoriale et hospitalière. Origine, année par année :</p>
<ul class="serree">${origines}</ul>
<p class="discret">Et c'est la limite de ces deux scénarios pour un agent
public. Un taux de 82,28 % ne signifie pas qu'un fonctionnaire acquiert 82 % de
son traitement en droits nouveaux : il est fixé pour que le compte
d'affectation spéciale « Pensions » soit à l'équilibre, donc pour payer les
pensions d'aujourd'hui. Le porter au compte répond à une question précise —
« et si tout ce qui a été consacré aux pensions avait été porté au compte des
actifs ? » — et à elle seule.</p>`;
  }

  return `
<h2>Qui verse la cotisation</h2>
<p>Une cotisation retraite a deux parts : ce que l'assuré supporte, et ce que
son employeur verse. Les scénarios 2 et 3 ne portent au compte que la première ;
les scénarios 4 et 5 y ajoutent la seconde, et ne changent rien d'autre.</p>
${partage}${public_}`;
}

/** Sépare l'effet de la règle d'indexation de celui des comptes notionnels. */
function decomposition(contexte, saisie, comparaison) {
  // Le défaut est lu sur DEFAUTS, non écrit en dur : ailleurs, l'utilisateur a
  // choisi lui-même sa ligne de comparaison.
  if (saisie.indexation !== DEFAUTS.indexation) {
    return "";
  }

  const lignes = [];
  for (const [code, libelle] of INDEXATIONS) {
    let variante;
    try {
      variante = code === saisie.indexation
        ? comparaison
        : contexte.simuler(new Saisie({ ...saisie, indexation: code }));
    } catch (erreur) {
      continue;
    }
    const mensuel = variante.enEurosConstants(
      variante.notionnel_retroactif.pension_annuelle,
    ) / 12;
    lignes.push([
      echapper(libelle),
      `×${g.nombre(variante.notionnel_retroactif.compte.rendement_cumule, 2)}`,
      g.euros(mensuel),
      g.pourcentage(variante.variation("notionnel_retroactif"), true),
    ]);
  }

  return `
<h2>D'où vient l'écart</h2>
<p>La même carrière, le même calcul notionnel rétroactif, avec neuf règles de
revalorisation des comptes. La <strong>première ligne est celle que la
simulation applique</strong> : la croissance de la masse salariale, c'est-à-dire
le rendement qu'un système en répartition peut servir sans changer son taux de
cotisation. La deuxième n'est pas une hypothèse mais un relevé : le coefficient
que les arrêtés ont réellement appliqué aux salaires portés au compte, celui-là
même dont le scénario 1 se sert. Les quatre suivantes sont le triple lock
inversé et ses variantes — mêmes trois séries, inflation, salaire moyen,
productivité, seul change ce qu'on en retient. La colonne « rendement » est le
facteur par lequel les cotisations ont été multipliées entre leur versement et
la liquidation.</p>
${g.tableau(
    ["Règle d'indexation", "Rendement cumulé", "Pension mensuelle", "Écart au système actuel"],
    lignes,
    ["", "nombre", "nombre", "nombre"],
  )}
<p class="discret">La ligne de repère est la <strong>revalorisation réellement
pratiquée</strong> : c'est celle du droit positif. L'écart entre elle et le
système actuel mesure l'effet propre des comptes notionnels ; tout ce qui sépare
les autres lignes de celle-là mesure l'effet de la règle d'indexation. La ligne
« Prix » ne joue pas ce rôle, contrairement à ce que cette page a longtemps dit :
le régime général ne revalorise sur les prix que depuis 1987, et suivait les
salaires avant. Le triple lock inversé, lui, compare deux taux nominaux
(inflation, salaire moyen) à un taux réel (productivité) : dès que l'inflation
dépasse la productivité — soit presque toute la période 1945-1985 — c'est la
productivité qui l'emporte, et la valeur réelle des comptes s'effondre. Les
lignes « médiane » et « moyenne » gardent ses trois séries et n'en changent que
la statistique.</p>
<p class="discret">La première ligne, la <strong>masse salariale</strong>, est
la seule qui repose sur un argument théorique et non sur un choix : c'est
l'assiette des cotisations, donc le taux de rendement qu'un système en
répartition peut servir sans toucher à son taux de cotisation. C'est pourquoi
elle est le défaut du simulateur. Elle vaut salaire moyen + emploi salarié, et
l'emploi salarié a doublé depuis 1950 : c'est la règle la plus généreuse du
tableau, et de loin. Elle a sa propre incohérence, à
garder en tête : elle crédite le compte du rendement que le système ENTIER
dégage, alors que les scénarios 2 et 3 n'y versent que la part salariale de la
cotisation. C'est aux scénarios 4 et 5, qui portent la cotisation entière,
qu'elle se compare sans biais. La ligne « PIB nominal » est la même idée poussée
à l'assiette la plus large : elle capte le déplacement de la valeur ajoutée vers
les revenus non salariaux, que la masse salariale subit.</p>
<p class="discret">Le <strong>lissage</strong>, dans les options, est
indépendant de la règle : il applique une moyenne glissante au taux que la règle
produit, quelle qu'elle soit, et s'applique donc à toutes les lignes de ce
tableau à la fois. Ce qu'il vise n'est pas le niveau mais la loterie de cohorte :
sur le PIB nominal brut, une cotisation de 1980 vaut ×5,44 à une liquidation de
2019 et ×5,18 en 2020 — attendre un an fait perdre, parce que l'année traversée
s'est mal passée. Lissée sur cinq ans, la même cotisation vaut ×6,64 puis ×6,71,
et le recul disparaît. « PIB nominal » lissé sur cinq ans, c'est la règle
italienne ; le modèle en reprend le taux, pas le reste du système italien.</p>
`;
}

/**
 * Détaille le passage du scénario 1 au scénario 3, étape par étape.
 *
 * C'est la partie du modèle la moins intuitive : le scénario 3 n'est pas le
 * scénario 1 diminué d'un pourcentage, c'est une autre formule appliquée à la
 * même carrière. Tant qu'on ne voit pas la chaîne de calcul, l'écart affiché
 * reste un chiffre à croire.
 */
function cascade(comparaison, saisie) {
  const prospectif = comparaison.notionnel_prospectif;
  const acquis = prospectif.droits_acquis;
  if (acquis === null || prospectif.capital_notionnel <= 0) {
    // Rien n'a été cotisé : une cascade de zéros n'explique rien, et le reste
    // de la page dit déjà que le compte est vide.
    return "";
  }

  const liquidation = comparaison.carriere.anneeLiquidation;
  const ageLiquidation = comparaison.carriere.age_liquidation || 0.0;
  const diviseur = prospectif.conversion.diviseur;
  const capitalApres = prospectif.capital_notionnel - acquis.capital;
  const actuel = comparaison.actuel.pension_annuelle;

  const lignes = [
    [`a) Droits acquis à ${saisie.bascule}`,
      "carrière arrêtée à la bascule, règles actuelles, avantages non "
      + "contributifs retirés, sans décote",
      `${g.euros(acquis.pension_figee)} par an`],
    [`b) × diviseur à ${age(acquis.age_conversion)}`,
      `coefficient de conversion en ${saisie.bascule} : `
      + `${g.nombre(acquis.diviseur, 2)}`,
      g.euros(acquis.capital_a_la_bascule)],
    [`c) × revalorisation ${saisie.bascule}-${liquidation}`,
      "règle d'indexation retenue : ×"
      + `${g.nombre(acquis.coefficient_revalorisation, 3)}`,
      g.euros(acquis.capital)],
    [`d) + cotisations ${saisie.bascule}-${liquidation - 1}`,
      "versées au régime unique, revalorisées de même",
      g.euros(capitalApres)],
    ["e) = capital notionnel", "ce que la carrière a effectivement financé",
      g.euros(prospectif.capital_notionnel)],
    [`f) ÷ diviseur à ${age(ageLiquidation)}`,
      `coefficient de conversion en ${liquidation} : ${g.nombre(diviseur, 2)}`,
      `${g.euros(prospectif.pension_annuelle)} par an`],
  ];

  const partAcquis = acquis.capital / prospectif.capital_notionnel;
  let neutralite = "";
  if (saisie.conversion_acquis === "reference"
      && acquis.age_conversion > ageLiquidation) {
    neutralite = `<p>Ligne b) : les droits déjà ouverts sont convertis au diviseur de `
      + `l'âge de référence (${age(acquis.age_conversion)}), alors que la `
      + `rente sera servie depuis ${age(ageLiquidation)}. L'anticipation `
      + `est donc payée une seconde fois, sur le passé. L'option « conversion `
      + `des droits acquis à l'âge de départ effectif » supprime cet `
      + `abattement, et c'est la convention qu'une réforme réelle `
      + `retiendrait.</p>`;
  }

  return `
<h2>Du scénario 1 au scénario 3, ligne à ligne</h2>
<p>Le scénario 3 n'est pas le scénario 1 diminué d'un pourcentage : c'est une
autre formule appliquée à la même carrière. Montants en euros courants de
l'année de liquidation — la chaîne de calcul est arithmétique, la convertir en
euros constants ligne à ligne la rendrait fausse.</p>
${g.tableau(
    ["Étape", "Ce qu'elle fait", "Résultat"],
    lignes,
    ["", "", "nombre"],
  )}
<p>À comparer aux ${g.euros(actuel)} par an du système actuel. L'écart ne vient
d'aucun abattement appliqué au scénario 1 : il vient de ce que le capital
réellement constitué, ${g.euros(prospectif.capital_notionnel)}, ne finance pas
les ${g.euros(actuel * diviseur)} que le droit en vigueur promet sur
${g.nombre(diviseur, 1)} années de retraite.</p>
${neutralite}
<p class="discret">Les droits acquis avant ${saisie.bascule} pèsent
${g.pourcentage(partAcquis)} du capital final. Cette part décroît de génération
en génération : c'est elle qui étale la réforme dans le temps, et non un
dispositif transitoire.</p>
`;
}

function detail(contexte, comparaison) {
  const retro = comparaison.notionnel_retroactif;
  const catalogue = contexte.simulateur().catalogue;
  const pensions = comparaison.actuel.pensions_par_regime;

  const nomRegime = (code) => (catalogue.contient(code) ? catalogue.obtenir(code).nom : code);

  const actuel = comparaison.actuel;
  const lignesActuel = pensions.map((pension) => [
    echapper(nomRegime(pension.regime)),
    g.euros(pension.montant),
    g.franciser(echapper(pension.detail)),
  ]);
  if (lignesActuel.length > 0 && actuel.avantages_appliques.length > 0) {
    lignesActuel.push([
      "<strong>Sous-total contributif</strong>",
      `<strong>${g.euros(actuel.total_contributif)}</strong>`,
      '<span class="discret">ce que la carrière a ouvert par ses seules '
      + "cotisations</span>",
    ]);
  }
  for (const avantage of actuel.avantages_appliques) {
    lignesActuel.push([
      `+ ${echapper(avantage.libelle)}`,
      g.euros(avantage.montant),
      `<span class="discret">${echapper(avantage.detail)}</span>`,
    ]);
  }
  if (lignesActuel.length > 0) {
    lignesActuel.push([
      "<strong>Pension du système actuel</strong>",
      `<strong>${g.euros(actuel.pension_annuelle)}</strong>`,
      '<span class="discret">c\'est le montant de la ligne 1 ci-dessus</span>',
    ]);
  }

  const regimes = lignesActuel.length > 0
    ? g.tableau(
      ["Régime, puis avantage", "Pension annuelle", "Calcul"],
      lignesActuel,
      ["", "nombre", ""],
    )
    : "<p>Aucun droit liquidé dans le système actuel.</p>";

  let part = "";
  if (actuel.avantages_appliques.length > 0 && actuel.pension_annuelle > 0) {
    const gratuit = actuel.avantages_appliques
      .reduce((somme, a) => somme + a.montant, 0.0);
    part = `<p>Les avantages non contributifs pèsent ${g.euros(gratuit)} par an, `
      + `soit ${g.pourcentage(gratuit / actuel.pension_annuelle)} de la `
      + "pension. C'est exactement ce que les deux scénarios notionnels "
      + "retirent : ils ne conservent que le sous-total contributif, et le "
      + "recalculent sur les cotisations réellement versées.</p>";
  }

  const compte = g.tableau(
    ["Poste", "Montant"],
    [
      ["Cotisations effectivement versées, en euros courants",
        g.euros(retro.compte.cotisations_versees)],
      ["Rendement cumulé appliqué à ces cotisations",
        `×${g.nombre(retro.compte.rendement_cumule, 2)}`],
      ["Capital notionnel à la liquidation", g.euros(retro.capital_notionnel)],
      ["Divisé par le coefficient de conversion",
        `${g.nombre(retro.conversion.diviseur, 2)} (${echapper(retro.conversion.table)})`],
      ["Pension annuelle en euros courants", g.euros(retro.pension_annuelle)],
    ],
    ["", "nombre"],
  );

  return `
<h2>Le détail du calcul</h2>
<h3>Scénario 1 — de quoi votre pension actuelle est faite</h3>
<p>Chaque régime d'abord, puis les avantages que le droit en vigueur ajoute
par-dessus. Les lignes s'additionnent exactement : le total est la pension du
scénario 1.</p>
${regimes}
${part}
<h3>Scénario 2 — construction du compte notionnel rétroactif</h3>
${compte}
<details>
  <summary>Les résultats complets en JSON</summary>
  <pre class="json">${echapper(JSON.stringify(comparaison.dictionnaire(), null, 2))}</pre>
</details>
<p class="discret">L'adresse de cette page contient tous les paramètres :
elle peut être citée ou partagée telle quelle.</p>
`;
}

function casTypes(contexte) {
  const resultat = calculerCasTypes(contexte.simulateur());

  const grille = (scenario) => {
    const lignes = CAS_TYPES.map((cas) => {
      const cellules = [
        `<span title="${echapper(cas.commentaire)}">${echapper(cas.libelle)}</span>`,
      ];
      for (const generation of GENERATIONS) {
        const comparaison = resultat.resultats.get(`${cas.code}|${generation}`);
        if (comparaison === undefined) {
          cellules.push("—");
          continue;
        }
        const variation = comparaison.variation(scenario);
        cellules.push(new g.Cellule(g.pourcentage(variation, true, 0), variation));
      }
      return cellules;
    });
    return g.tableau(
      ["Cas type", ...GENERATIONS.map(String)],
      lignes,
      ["", ...GENERATIONS.map(() => "nombre")],
    );
  };

  let echecs = "";
  if (resultat.echecs.size > 0) {
    const elements = [...resultat.echecs.entries()]
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
      .map(([cle, motif]) => {
        const [code, generation] = cle.split("|");
        return `<li>${echapper(code)} / ${generation} : ${echapper(motif)}</li>`;
      })
      .join("");
    echecs = `<h3>Combinaisons non calculées</h3><ul class='serree'>${elements}</ul>`;
  }

  return `
<h2 style="margin-top:0">Le cas général</h2>
<p class="chapeau">Douze carrières représentatives × sept générations. Chaque
cellule est l'écart de pension par rapport au système actuel, à carrière
identique : négatif = pension plus faible qu'aujourd'hui.</p>

<h3>Scénario 2 — comptes notionnels rétroactifs depuis 1941</h3>
${grille("notionnel_retroactif")}
<p class="discret">Les générations anciennes sont les plus touchées : leurs
cotisations, versées quand l'inflation dépassait la productivité, ont été
revalorisées à un taux très inférieur à la hausse des prix.</p>

<h3>Scénario 3 — comptes notionnels à compter de la bascule</h3>
${grille("notionnel_prospectif")}
<p class="discret">Les générations déjà retraitées sont inchangées : leurs droits
sont intégralement acquis avant la bascule. Les indépendants et professions
libérales progressent parce que le régime unique relève leur taux de cotisation
et déplafonne leur assiette — un effort contributif accru, pas un avantage
accordé.</p>

<h3>Scénario 4 — le scénario 2, part patronale comprise</h3>
${grille("notionnel_retroactif_employeur")}
<p class="discret">Toutes les lignes bougent, sauf celles des non-salariés —
artisan, exploitant agricole, profession libérale — qui n'ont pas d'employeur et
pour qui ce scénario est le scénario 2. Les lignes publiques bougent le plus :
la contribution de leur employeur est un taux d'équilibre, sans commune mesure
avec la part patronale d'un salarié.</p>

<h3>Scénario 5 — le scénario 3, part patronale comprise</h3>
${grille("notionnel_prospectif_employeur")}
<p class="discret">Même lecture, à compter de la bascule : les droits acquis
restent ceux du scénario 3, et seul le flux postérieur change. À compter de la
bascule il n'y a plus qu'un régime, dont la répartition salarié/employeur est
celle du statut pivot privé : les écarts entre statuts s'y referment.</p>
${echecs}
`;
}

// Bandes du graphique par système : les six plus lourdes gardent leur couleur,
// le reste de la répartition est réuni, et ce qui n'en relève pas forme la
// dernière bande. Huit bandes se lisent ; treize ne se lisent plus.
const BANDES_COUT = [
  ["regime_general", "var(--serie-1)"],
  ["agirc_arrco", "var(--serie-2)"],
  ["fonction_publique_etat", "var(--serie-3)"],
  ["regimes_speciaux", "var(--serie-4)"],
  ["exploitants_agricoles", "var(--serie-5)"],
  ["professions_liberales", "var(--serie-6)"],
];

// Couleur de chacun des cinq scénarios — les mêmes que sur la page de
// résultats, pour qu'un lecteur qui passe de l'une à l'autre les reconnaisse.
const COULEURS_SCENARIOS = {
  actuel: "var(--actuel)",
  notionnel_retroactif: "var(--retroactif)",
  notionnel_prospectif: "var(--prospectif)",
  notionnel_retroactif_employeur: "var(--retroactif-employeur)",
  notionnel_prospectif_employeur: "var(--prospectif-employeur)",
};

/** Un montant en millions d'euros, écrit en milliards. */
function milliards(millions, decimales = 0) {
  return `${g.nombre(millions / 1000, decimales)} Md €`;
}

function cout(contexte) {
  const depenses = contexte.depenses();
  const c = contexte.cout();
  const annees = depenses.annees();
  const ventilees = depenses.anneesVentilees();
  const derniere = depenses.derniereAnnee;
  const euros = c.anneeEuros;

  const total = depenses.depense(derniere);
  const repartition = depenses.repartition(derniere);
  const autres = {};
  for (const systeme of SYSTEMES) {
    if (!systeme.repartition) {
      autres[systeme.code] = depenses.depenseSysteme(systeme.code, derniere);
    }
  }

  // -- ce que la dépense a été, en euros courants et constants --------------
  const courbeConstants = new g.Serie(
    `En euros constants de ${euros}`,
    c.annees.map((ligne) => ligne.observeeConstants / 1000),
    "var(--serie-1)",
  );
  const courbeCourants = new g.Serie(
    "En euros courants de chaque année",
    c.annees.map((ligne) => ligne.observee / 1000),
    "var(--serie-2)", true,
  );
  const courbePib = new g.Serie(
    "Part du produit intérieur brut",
    c.annees.map((ligne) => ligne.partPib * 100),
    "var(--serie-3)",
  );

  // -- ce que chaque système pèse ------------------------------------------
  const reunies = BANDES_COUT.map(([code]) => code);
  const bandes = BANDES_COUT.map(([code, couleur]) => new g.Serie(
    SYSTEMES.find((s) => s.code === code).libelle,
    ventilees.map((annee) => depenses.depenseSysteme(code, annee) / 1000),
    couleur,
  ));
  bandes.push(new g.Serie(
    "Autres régimes par répartition",
    ventilees.map((annee) => {
      let somme = 0;
      for (const s of SYSTEMES) {
        if (s.repartition && !reunies.includes(s.code)) {
          somme += depenses.depenseSysteme(s.code, annee);
        }
      }
      return somme / 1000;
    }),
    "var(--serie-7)",
  ));
  bandes.push(new g.Serie(
    "Hors répartition obligatoire",
    ventilees.map((annee) => {
      let somme = 0;
      for (const s of SYSTEMES) {
        if (!s.repartition) somme += depenses.depenseSysteme(s.code, annee);
      }
      return somme / 1000;
    }),
    "var(--serie-9)", false, "capitalisation, dépendance, minimum vieillesse",
  ));

  const premiereVentilee = ventilees[0];
  const duree = derniere - premiereVentilee;
  const lignesSystemes = SYSTEMES.map((systeme) => {
    const debut = depenses.depenseSysteme(systeme.code, premiereVentilee);
    const fin = depenses.depenseSysteme(systeme.code, derniere);
    const coefficient = contexte.simulateur().macro.coefficientPrix(
      premiereVentilee, derniere,
    );
    const croissance = debut > 0
      ? (fin / (debut * coefficient)) ** (1 / duree) - 1
      : 0.0;
    let cumul = 0;
    for (const annee of ventilees) {
      cumul += depenses.depenseSysteme(systeme.code, annee)
        * contexte.simulateur().macro.coefficientPrix(annee, euros);
    }
    return [
      `<span title="${echapper(systeme.glose)}">${echapper(systeme.libelle)}</span>`,
      milliards(fin, 1),
      g.pourcentage(fin / total, false, 1),
      milliards(cumul, 0),
      g.pourcentage(croissance, true, 1),
      systeme.repartition ? "oui" : "non",
    ];
  });

  // -- ce que les cinq systèmes auraient coûté -----------------------------
  // Un scénario dont la courbe est exactement celle du système actuel serait
  // tracé PAR-DESSUS elle et la ferait disparaître : le graphique montrerait
  // alors une seule courbe en prétendant en montrer trois. On ne trace donc que
  // les scénarios qui s'en écartent, et la légende nomme les autres.
  const confondus = c.confondusAvecActuel();
  const numeros = SCENARIOS
    .filter(([scenario]) => confondus.includes(scenario))
    .map(([, libelle]) => libelle.split(".")[0]);
  const gloseActuel = numeros.length
    ? `et les scénarios ${numeros.join(" et ")}, qui lui sont confondus`
    : "";
  const courbesScenarios = SCENARIOS
    .filter(([scenario]) => !confondus.includes(scenario))
    .map(([scenario, libelle]) => new g.Serie(
      libelle,
      c.annees.map((ligne) => ligne.coutConstants(scenario) / 1000),
      COULEURS_SCENARIOS[scenario],
      scenario.startsWith("notionnel_prospectif"),
      scenario === "actuel" ? gloseActuel : "",
    ));
  const reference = c.cumul("actuel");
  const lignesScenarios = SCENARIOS.map(([scenario, libelle]) => {
    const cumul = c.cumul(scenario);
    const dernier = c.annee(derniere);
    return [
      echapper(libelle),
      milliards(cumul, 0),
      scenario !== "actuel"
        ? g.pourcentage(cumul / reference - 1, true, 1)
        : "réf.",
      milliards(dernier.cout(scenario), 1),
      g.pourcentage(dernier.partPib * dernier.rapports[scenario], false, 1),
    ];
  });

  // -- demain : la trajectoire de la répartition jusqu'à l'horizon INSEE ----
  const avenir = c.avenir;
  const anneesAvenir = avenir.annees.map((ligne) => ligne.annee);
  const bascule = contexte.base.annee_bascule;
  const courbesAvenir = SCENARIOS.map(([scenario, libelle]) => new g.Serie(
    libelle,
    avenir.annees.map((ligne) => ligne.coutConstants(scenario) / 1000),
    COULEURS_SCENARIOS[scenario],
    scenario.startsWith("notionnel_prospectif"),
  ));
  const partsAvenir = SCENARIOS.map(([scenario, libelle]) => new g.Serie(
    libelle,
    avenir.annees.map((ligne) => ligne.partPib(scenario) * 100),
    COULEURS_SCENARIOS[scenario],
    scenario.startsWith("notionnel_prospectif"),
  ));
  const horizon = avenir.annee(avenir.derniereAnnee);
  const depart = avenir.annee(derniere);
  const referenceAvenir = avenir.cumul("actuel");
  const lignesAvenir = SCENARIOS.map(([scenario, libelle]) => {
    const cumul = avenir.cumul(scenario);
    return [
      echapper(libelle),
      milliards(horizon.coutConstants(scenario), 0),
      g.pourcentage(horizon.partPib(scenario), false, 1),
      milliards(cumul, 0),
      scenario === "actuel"
        ? "réf."
        : g.pourcentage(cumul / referenceAvenir - 1, true, 1),
      scenario === "actuel" ? "—" : milliards(avenir.ecartCumule(scenario), 0),
    ];
  });

  const horizons = [];
  for (let millesime = 2030; millesime <= avenir.derniereAnnee; millesime += 10) {
    const ligne = avenir.annee(millesime);
    if (ligne === null) continue;
    horizons.push([
      String(millesime),
      g.nombre(ligne.dependance, 2),
      g.pourcentage(ligne.partPib("actuel"), false, 1),
      g.pourcentage(ligne.partPib("notionnel_prospectif"), false, 1),
      g.pourcentage(ligne.partPib("notionnel_prospectif_employeur"), false, 1),
    ]);
  }

  const decennies = [];
  for (let debut = 1960; debut <= derniere; debut += 10) {
    const fin = Math.min(debut + 9, derniere);
    const lignesDecennie = c.annees.filter(
      (l) => l.annee >= debut && l.annee <= fin,
    );
    if (!lignesDecennie.length) continue;
    const moyenne = (extraire) => lignesDecennie.reduce(
      (somme, l) => somme + extraire(l), 0,
    ) / lignesDecennie.length;
    decennies.push([
      `${debut}-${fin}`,
      milliards(lignesDecennie.reduce((s, l) => s + l.observeeConstants, 0), 0),
      g.pourcentage(moyenne((l) => l.partPib), false, 1),
      g.pourcentage(moyenne((l) => l.rapports.notionnel_retroactif), false, 1),
      g.pourcentage(
        moyenne((l) => l.rapports.notionnel_retroactif_employeur), false, 1,
      ),
    ]);
  }

  return `
<h2 style="margin-top:0">Ce que la retraite a coûté</h2>
<p class="chapeau">Le reste du site calcule des droits : ce qu'une carrière
ouvre. Cette page porte la grandeur inverse — ce qui a été payé, année par année
depuis ${c.premiereAnnee}, système par système. Puis elle pose les deux
questions qui suivent : ce que les quatre autres systèmes auraient coûté sur la
même période, et ce qu'ils coûteraient d'ici ${avenir.derniereAnnee}. On ne
change pas le passé ; c'est la seconde question qui décide de quelque chose.</p>

<div class="fiches">
${g.fiche(`Dépense ${derniere}, risque vieillesse-survie`, milliards(total, 1))}
${g.fiche("Dont répartition obligatoire", milliards(repartition, 1))}
${g.fiche(`Part du PIB en ${derniere}`,
    g.pourcentage(depenses.partPib(derniere), false, 1))}
${g.fiche(`Cumul ${c.premiereAnnee}-${derniere}, euros de ${euros}`,
    milliards(c.cumulObserve(), 0))}
</div>

<p>Les ${milliards(total, 1)} de ${derniere} sont le risque
<strong>vieillesse-survie tout entier</strong> : les pensions, mais aussi le
minimum vieillesse, l'aide sociale aux personnes âgées et la retraite
supplémentaire par capitalisation. La <strong>répartition obligatoire</strong>
seule en fait ${milliards(repartition, 1)} — c'est cette grandeur-là, et non le
total, qu'il faut rapprocher des quelque 420 milliards que l'on cite d'ordinaire
pour l'année en cours. Le reste est
${milliards(autres.aide_sociale_locale, 1)} de dépendance,
${milliards(autres.supplementaire, 1)} de capitalisation et
${milliards(autres.solidarite_etat, 1)} de solidarité de l'État.</p>

<h3>Soixante-six ans de dépense</h3>
${g.graphique(
    `Dépenses du risque vieillesse-survie de ${c.premiereAnnee} à ${derniere}, `
    + "en milliards d'euros",
    annees, [courbeConstants, courbeCourants], "Md €")}
<p class="discret">Deux lectures de la même série. En euros courants, la
dépense est multipliée par cent quatre-vingt-treize depuis
${c.premiereAnnee} — mais les prix aussi ont été multipliés par treize.
En euros constants, la multiplication est par quinze : c'est celle-là qui est
réelle, et elle reste considérable.</p>

${g.graphique(
    "Part des dépenses de vieillesse-survie dans le produit intérieur brut, "
    + `${c.premiereAnnee}-${derniere}`,
    annees, [courbePib], "% du PIB", false, 1)}
<p class="discret">Rapportée à la richesse produite, la dépense passe de
${g.pourcentage(depenses.partPib(c.premiereAnnee), false, 1)} à
${g.pourcentage(depenses.partPib(derniere), false, 1)}. La courbe monte par
paliers — chaque crise fait un décrochage du dénominateur avant que le
numérateur ne rattrape — et le palier des années 2020 n'a pas encore été
refermé.</p>

<h3>Système par système</h3>
${g.graphique(
    `Dépenses de vieillesse-survie par système, ${premiereVentilee}-${derniere}, `
    + "en milliards d'euros courants",
    ventilees, bandes, "Md €", true)}
<p class="discret">La ventilation ne commence qu'en ${premiereVentilee} : de 1981
à 1989 la DREES publie une autre nomenclature, dont les périmètres ne se
raccordent pas à ceux-ci, et personne n'a publié le raccord. Le total, lui,
remonte à ${c.premiereAnnee}.</p>

${g.tableau(
    ["Système", `${derniere}`, "Part", `Cumul ${premiereVentilee}-${derniere}`,
      "Croissance réelle", "Répartition"],
    lignesSystemes,
    ["", "nombre", "nombre", "nombre", "nombre", ""],
)}
<p class="discret">Le cumul est en euros constants de ${euros} : additionner des
euros de 1990 et de ${derniere} n'aurait aucun sens. La croissance réelle est
celle de la dépense annuelle, déflatée, de ${premiereVentilee} à ${derniere}.
Deux chiffres se lisent en connaissant le découpage : le régime général absorbe
en 2020 les artisans et les commerçants, dont le régime a été adossé à la Cnav,
et les « régimes spéciaux » de la comptabilité nationale contiennent la CNRACL,
c'est-à-dire la fonction publique territoriale et hospitalière.</p>

<h3>Ce que les cinq systèmes auraient coûté</h3>
<p>La dépense observée n'est pas modélisée : elle est ce qu'elle est. Ce qui est
modélisé, c'est le <strong>rapport</strong> entre ce qui a été versé et ce que
chaque système aurait versé aux mêmes retraités — la moyenne des écarts de
pension, pondérée par le poids de chaque génération dans la masse de l'année.
Les poids sont les effectifs réels de chaque génération, lus dans la pyramide
des âges de l'INSEE ; les écarts viennent des douze cas types croisés avec
${c.generations.length} générations, de ${c.generations[0]} à
${c.generations[c.generations.length - 1]}.</p>

${g.graphique(
    `Coût annuel des cinq systèmes, ${c.premiereAnnee}-${derniere}, `
    + `en milliards d'euros constants de ${euros}`,
    annees, courbesScenarios, `Md € ${euros}`)}

${g.tableau(
    ["Système", `Cumul ${c.premiereAnnee}-${derniere}`, "Écart",
      `Coût ${derniere}`, `Part du PIB ${derniere}`],
    lignesScenarios,
    ["", "nombre", "nombre", "nombre", "nombre"],
)}

<div class="note"><strong>Les scénarios 3 et 5 coûtent exactement ce que coûte
le système actuel, et ce n'est pas un défaut du calcul.</strong> Leur bascule est
fixée à ${contexte.base.annee_bascule} : aucune pension servie avant cette date
n'en est modifiée, puisque les droits déjà acquis sont conservés. Une réforme
prospective ne fait rien économiser sur le passé — elle ne commence à compter
qu'au premier assuré qui liquide après elle. C'est le principal résultat de
cette page, et il est vrai de toute réforme des retraites qui respecte les
droits acquis.</div>

<p>Le scénario 2, lui, aurait coûté ${milliards(c.cumul("notionnel_retroactif"), 0)}
au lieu de ${milliards(reference, 0)} : la retraite française aurait servi
${g.pourcentage(1 - c.cumul("notionnel_retroactif") / reference, false, 0)}
de moins sur soixante-six ans. Cet écart ne mesure PAS l'effet des comptes
notionnels. Il mesure deux choses qui n'ont rien à voir avec eux : ce scénario
ne porte au compte que la <strong>part salariale</strong> de la cotisation — le
scénario 4, qui y ajoute la part patronale, coûte
${milliards(c.cumul("notionnel_retroactif_employeur"), 0)}, soit
${g.pourcentage(
    c.cumul("notionnel_retroactif_employeur")
    / c.cumul("notionnel_retroactif") - 1, true, 0)}
de plus —, et il applique une <a href="${g.lien("/methode", "indexation")}">règle
d'indexation</a> dont la page Méthode montre qu'elle domine tout le reste.</p>

<h2>Demain : ce que chaque système coûterait d'ici ${avenir.derniereAnnee}</h2>
<p class="chapeau">On ne change pas le passé. La question qui décide de quelque
chose est celle-ci : à partir d'aujourd'hui, que coûte chaque système ? La
réponse tient à deux choses, et à deux seulement — combien de retraités, et
combien chacun perçoit.</p>

<div class="fiches">
${g.fiche(`Système actuel en ${avenir.derniereAnnee}`,
    g.pourcentage(horizon.partPib("actuel"), false, 1))}
${g.fiche(`Notionnel dès ${bascule} en ${avenir.derniereAnnee}`,
    g.pourcentage(horizon.partPib("notionnel_prospectif"), false, 1))}
${g.fiche(`Écart cumulé ${avenir.premiereAnneeProjetee}-${avenir.derniereAnnee}`,
    milliards(avenir.ecartCumule("notionnel_prospectif"), 0))}
${g.fiche(`65 ans et plus par 20-64 ans, en ${avenir.derniereAnnee}`,
    g.nombre(horizon.dependance, 2))}
</div>

<p>La méthode ne change pas d'un mot : le coût d'un système reste la dépense du
système actuel multipliée par le rapport des masses de pension. Ce qui change,
c'est d'où vient cette dépense. Jusqu'en ${derniere} elle est <strong>observée</strong> ;
au-delà, c'est le modèle qui la produit, <strong>ancré</strong> sur cette
dernière année publiée — les deux expressions coïncident exactement à la
jonction, si bien qu'aucune courbe ne saute. Ce qui les fait bouger ensuite est
ce qui doit les faire bouger : la <strong>pyramide des âges</strong> de l'INSEE,
et les pensions que chaque génération acquiert sous chaque système.</p>

<div class="note">L'assiette de cette section n'est pas celle de la précédente.
Le modèle décrit des <strong>pensions de répartition obligatoire</strong> —
${milliards(repartition, 1)} en ${derniere} — et non le risque vieillesse-survie
entier, qui porte en plus la dépendance et la capitalisation. C'est donc de la
répartition seule qu'il s'agit ici, de ${avenir.premiereAnnee} à
${avenir.derniereAnnee}.</div>

${g.graphique(
    `Coût annuel des cinq systèmes de ${avenir.premiereAnnee} à `
    + `${avenir.derniereAnnee}, en milliards d'euros constants de ${euros}`,
    anneesAvenir, courbesAvenir, `Md € ${euros}`, false, 0, true,
    derniere, "projection")}
<p class="discret">À gauche du trait, la dépense est publiée par la DREES ; à
droite, elle est projetée. Les cinq courbes se suivent jusqu'à la bascule de
${bascule} — les droits déjà acquis sont conservés — puis les deux scénarios
prospectifs s'en détachent, d'abord imperceptiblement, ensuite pour de bon. Une
réforme des retraites met une génération entière à produire son effet, et c'est
là le vrai enseignement de ce graphique : décider en ${bascule} n'économise rien
en ${bascule}, et beaucoup en ${avenir.derniereAnnee}.</p>

${g.graphique(
    `Part du produit intérieur brut, ${avenir.premiereAnnee}-`
    + `${avenir.derniereAnnee}, par système`,
    anneesAvenir, partsAvenir, "% du PIB", false, 1, true,
    derniere, "projection")}
<p class="discret">C'est la lecture qui compte, parce qu'elle rapporte la
dépense à ce qui la finance. Le système actuel passe de
${g.pourcentage(depart.partPib("actuel"), false, 1)} en ${derniere} à
${g.pourcentage(horizon.partPib("actuel"), false, 1)} en
${avenir.derniereAnnee} : il ne dérape pas, il ne s'allège pas non plus. Le
Conseil d'orientation des retraites, qui projette la même grandeur avec un
modèle de population complet, trouve 13,9 % en 2024 et
<strong>14,2 % en 2070</strong> (rapport annuel de juin 2025) — trois dixièmes
de point sous notre point de départ, six dixièmes sous notre point d'arrivée.
Deux modèles qui n'ont rien en commun, et qui tombent à un demi-point l'un de
l'autre : c'est le meilleur contrôle externe dont cette page dispose.</p>

${g.tableau(
    ["Système", `Coût ${avenir.derniereAnnee}`, `Part du PIB ${avenir.derniereAnnee}`,
      `Cumul ${avenir.premiereAnneeProjetee}-${avenir.derniereAnnee}`, "Écart",
      "Dont économie"],
    lignesAvenir,
    ["", "nombre", "nombre", "nombre", "nombre", "nombre"],
)}
<p class="discret">Le cumul porte sur les seules années projetées, en euros
constants de ${euros}. Les scénarios 2 et 4 restent des contrefactuels et non des
réformes : ils supposent recalculées les pensions de gens qui les perçoivent
depuis trente ans, ce qu'aucun droit ne permettrait. Les scénarios 3 et 5, eux,
décrivent une réforme applicable — droits acquis conservés, règles nouvelles
pour la suite.</p>

<h3>Ce qui pousse la dépense, et ce qui la retient</h3>
${g.tableau(
    ["Horizon", "65 ans et plus par 20-64 ans", "Système actuel",
      `Notionnel dès ${bascule}`, `Notionnel dès ${bascule}, avec l'employeur`],
    horizons,
    ["", "nombre", "nombre", "nombre", "nombre"],
)}
<p class="discret">La première colonne est le rapport de dépendance
démographique de l'INSEE : ${g.nombre(depart.dependance, 2)} personne de 65 ans
ou plus par personne de 20 à 64 ans en ${derniere},
${g.nombre(horizon.dependance, 2)} en ${avenir.derniereAnnee}. C'est lui qui
pousse la dépense, et il n'est l'objet d'aucun choix. Ce qui la retient, dans le
système actuel, est l'indexation sur les prix : elle fait décrocher les pensions
des salaires, génération après génération, et c'est ainsi que la dépense reste à
peu près stable dans le PIB pendant que le nombre de retraités augmente de
moitié. Les comptes notionnels font la même chose autrement — par le diviseur
d'espérance de vie —, mais ils le font <em>explicitement</em>, et à
l'acquisition plutôt qu'au versement.</p>

<h3>Ce que cette projection suppose</h3>
<ul class="serree">
  <li><strong>La démographie n'est pas de nous.</strong> Effectifs par âge du
  scénario central des projections de population 2026 de l'INSEE, jusqu'en
  ${avenir.derniereAnnee} — c'est cet horizon-là, et non une décision du dépôt,
  qui borne la page. Seize autres scénarios existent ; leur écart mesurerait
  l'incertitude démographique, que cette page ne montre pas.</li>
  <li><strong>Le PIB projeté corrige l'emploi.</strong> Il croît au rythme
  nominal des hypothèses du COR — ${g.pourcentage(
      contexte.simulateur().macro.projection.pib_nominal, false, 2)} par an —,
  corrigé de l'évolution de la population d'âge actif, qui recule de
  ${g.pourcentage(
      1 - contexte.population().actifs.valeur(avenir.derniereAnnee)
      / contexte.population().actifs.valeur(derniere), false, 0)} d'ici
  ${avenir.derniereAnnee}. Sans cette correction, la France de
  ${avenir.derniereAnnee} produirait avec des actifs qu'aucune projection ne lui
  donne, et toutes les parts de PIB de cette page seraient flatteuses d'un point.</li>
  <li><strong>La grille échantillonne une génération sur cinq.</strong> Chacune
  en représente cinq, décalées d'un an à deux ans, et chacune de ces cinq
  liquide sa propre année. Une cohorte qui part juste avant la bascule est donc
  représentée par une génération qui part juste après, et hérite de son
  traitement : les courbes prospectives s'écartent de la courbe actuelle d'un
  ou deux dixièmes de pour cent avant même la bascule. C'est le prix du pas de
  la grille, il est mesuré, et un test le borne à un demi-point.</li>
  <li><strong>Le taux de couverture est supposé constant.</strong> Le modèle
  compte des générations, non des cotisants : il suppose que la même proportion
  de chaque génération perçoit une pension, et que la carrière type ne change
  pas. Un recul de l'âge de départ, une carrière plus longue ou plus hachée
  déplaceraient la trajectoire, et la page ne les simule pas.</li>
  <li><strong>Aucune règle de pilotage.</strong> Un système notionnel réel porte
  un coefficient d'équilibre qui ajusterait toutes ses pensions par un même
  facteur, année après année, pour tomber juste. Ce facteur étant commun, il
  déplacerait les niveaux sans toucher aux écarts entre carrières — mais il
  déplacerait bel et bien les courbes de cette page.</li>
  <li><strong>Rien de tout cela n'est certifié, et ne peut l'être.</strong> Une
  projection est une hypothèse : celle de l'INSEE pour la démographie, celle du
  COR pour la macroéconomie, celle du modèle pour les pensions. La page les
  affiche parce qu'un ordre de grandeur documenté vaut mieux qu'un silence — pas
  parce qu'elle saurait de quoi 2070 sera fait.</li>
</ul>

<h3>Décennie par décennie</h3>
${g.tableau(
    ["Décennie", `Dépense cumulée, euros de ${euros}`, "Part du PIB",
      "Coût du scénario 2", "Coût du scénario 4"],
    decennies,
    ["", "nombre", "nombre", "nombre", "nombre"],
)}
<p class="discret">Les deux dernières colonnes sont en pourcentage de la dépense
réellement engagée la même décennie. Elles remontent : plus on approche du
présent, plus les carrières prises en compte ont été cotisées sous des règles
proches des règles actuelles, et moins le compte notionnel s'en écarte.</p>

<h3>Ce que cette page ne dit pas</h3>
<ul class="serree">
  <li><strong>Elle ne projette rien.</strong> La série s'arrête à ${derniere},
  dernière année publiée par la DREES. Prolonger demanderait une pyramide des
  âges et un taux d'emploi, c'est-à-dire un modèle de population — que ce dépôt
  n'a pas et ne prétend pas avoir.</li>
  <li><strong>Les effectifs de génération sont ceux de l'INSEE</strong>, non
  une hypothèse. Cette page a d'abord supposé toutes les générations de même
  taille, faute de pyramide des âges ; elle porte désormais celle des
  projections de population 2026, observée jusqu'en 2023. L'hypothèse levée
  valait ce qu'on disait qu'elle valait : elle déplaçait l'écart du scénario 2
  de six dixièmes de point sur soixante-six ans.</li>
  <li><strong>Les douze cas types pèsent d'un poids égal.</strong> Il y a moins
  d'agents de conduite que de salariés au salaire moyen. C'est la convention de
  la grille des <a href="${g.lien("/cas-types")}">cas types</a>, reconduite ici
  faute d'une pondération que quelque source fixerait.</li>
  <li><strong>Avant 1975, la reconstitution est mince.</strong> La répartition
  ne commence qu'en ${contexte.base.annee_debut_repartition} : les générations
  antérieures à ${c.generations[0]} n'ont, dans ce modèle, aucune pension, et
  plusieurs régimes n'existaient pas encore. Les premières années reposent donc
  sur deux ou trois générations et la moitié des cas types.</li>
  <li><strong>Le coût n'est pas le solde.</strong> Cette page dit ce qui a été
  versé, jamais ce qui a été encaissé. Un système notionnel qui coûterait quatre
  fois moins ne serait pas quatre fois plus « soutenable » : il servirait
  quatre fois moins, ce qui est une autre affaire.</li>
</ul>
<p class="discret">Fiabilité de l'ensemble : la dépense observée est
<strong>certifiée</strong> — recontrôlée contre l'API de la DREES à chaque
exécution —, le rapport qui en tire les quatre contrefactuels est
<strong>estimé</strong>, et ne peut pas être autre chose : aucune institution ne
publie ce qu'aurait coûté un système qui n'a pas existé.</p>
`;
}

function methode(contexte) {
  const fusionne = contexte.simulateur().regimeFusionne;
  const nombreRegimes = contexte.simulateur().catalogue.taille;
  return `
<h2 style="margin-top:0">Ce que le modèle calcule</h2>

<h3>Le compte notionnel</h3>
<p>Un compte notionnel est un compte <em>virtuel</em> : aucun capital n'est
placé, les cotisations de l'année financent les pensions de l'année, comme dans
toute répartition. Ce qui change, c'est le calcul du droit.</p>
<ol>
  <li><strong>Accumulation</strong> — la cotisation retraite effectivement
  versée chaque année est inscrite au compte ;</li>
  <li><strong>Revalorisation</strong> — le solde est revalorisé chaque année au
  taux fixé par la règle collective ;</li>
  <li><strong>Liquidation</strong> — pension annuelle = capital notionnel ÷
  espérance de vie résiduelle à l'âge de départ, lue sur une table de
  génération.</li>
</ol>
<p>Trois conséquences : la pension est strictement proportionnelle aux
cotisations ; partir tôt coûte deux fois (moins de cotisations, rente servie
plus longtemps) ; aucun droit non financé par une cotisation n'existe.</p>

<h3 id="indexation">La règle d'indexation, et pourquoi elle domine tout</h3>
<p>La règle retenue par défaut est la croissance de la <strong>masse
salariale</strong> : l'assiette des cotisations, c'est-à-dire le rendement qu'un
système en répartition peut servir sans toucher à son taux de cotisation. C'est
la règle que la théorie désigne, et non celle qui a donné son cahier des charges
au modèle.</p>
<p>Celle-là, le <strong>triple lock inversé</strong> —
<code>min(inflation, croissance du salaire moyen, productivité réelle)</code> —
reste à un clic dans les options, et c'est elle qui a motivé ce simulateur.
Prise à la lettre, elle compare deux taux nominaux à un taux réel, et voici ce
qu'elle produit.</p>
${g.tableau(
    ["Règle appliquée 1941-2025", "Comptes", "Prix", "Pouvoir d'achat conservé"],
    [
      ["Triple lock inversé, littéral", "×4,9", "×322,2", "<strong>1,5 %</strong>"],
      ["Moyenne des trois taux", "×175,7", "×322,2", "54,5 %"],
      ["Triple lock inversé, tout en nominal", "×223,3", "×322,2", "69,3 %"],
      ["Indexation sur les prix", "×322,2", "×322,2", "100 %"],
      ["Médiane des trois taux", "×397,6", "×322,2", "123,4 %"],
      ["Revalorisation réellement pratiquée", "×1 538,2", "×322,2", "477,4 %"],
      ["Masse salariale (règle d'équilibre)", "×3 685,1", "×322,2", "1 143,7 %"],
      ["PIB nominal", "×3 442,3", "×322,2", "1 068,6 %"],
      ["PIB nominal lissé sur 5 ans (Italie)", "×4 152,7", "×322,2", "1 288,8 %"],
    ],
    ["", "nombre", "nombre", "nombre"],
  )}
<p>Une cotisation de 1950 ne conserve donc que 1,5 % de sa valeur réelle. C'est
la règle telle qu'énoncée, appliquée sans correctif — et c'est de là que vient
l'essentiel de la baisse affichée par le scénario rétroactif, non du passage aux
comptes notionnels. Le tableau « D'où vient l'écart » de chaque simulation
sépare les deux effets.</p>
<p>La ligne « Revalorisation réellement pratiquée » est la seule qui ne soit pas
une hypothèse : c'est le coefficient que les arrêtés annuels ont réellement
appliqué aux salaires portés au compte, celui dont le scénario 1 se sert pour
calculer le salaire de référence. Il vaut <strong>×1 538</strong> sur la période, soit près de cinq
fois les prix, parce que le régime général a revalorisé sur les SALAIRES
jusqu'en 1986 et sur les prix seulement depuis 1987. C'est donc cette ligne, et
non « Indexation sur les prix », qui neutralise la question de l'indexation
quand on veut isoler l'effet propre des comptes notionnels — cette page a
longtemps désigné la mauvaise. Sur une carrière, la correction reste modeste :
+6,2 points pour la génération 1920, +0,1 pour 1945, et -0,5 pour 1958, dont la
carrière est presque entièrement postérieure à 1987. Les cotisations se
concentrent sur les dernières années, là où les deux règles coïncident.</p>
<p>La dernière ligne est d'une autre nature : elle ne décrit ni une règle
demandée, ni une règle appliquée, mais la règle que la <strong>théorie</strong>
désigne. En répartition, le rendement qu'un système peut servir sans changer son
taux de cotisation est la croissance de son assiette — la masse salariale, soit
le salaire moyen multiplié par l'emploi salarié (Samuelson 1958, Aaron 1966).
C'est le taux d'indexation des comptes notionnels suédois, italiens, polonais et
lettons, à des variantes près. Sur 1941-2025 il vaut ×3 685, onze fois les
prix : l'emploi salarié a doublé depuis 1950, et cette croissance-là s'ajoute
chaque année à celle des salaires. Une réserve : ce rendement est celui du
système ENTIER, alors que les scénarios 2 et 3 ne portent au compte que la part
salariale de la cotisation. C'est aux scénarios 4 et 5 qu'il faut le comparer.</p>
<p>Les deux dernières lignes sont la même idée poussée à l'assiette la plus
large : le <strong>PIB nominal</strong>, qui gagne ce que la masse salariale
perd quand la valeur ajoutée se déplace vers les revenus non salariaux. La
seconde y ajoute un <strong>lissage sur cinq ans</strong>, comme le fait
l'Italie pour ses propres comptes notionnels.</p>
<p>Le lissage n'est pas une règle : c'est un réglage à part, qui applique une
moyenne glissante au taux que la règle produit — n'importe laquelle. Ce qu'il
vise n'est pas le niveau mais la <strong>loterie de cohorte</strong> : sur le PIB
nominal brut, une cotisation de 1980 vaut ×5,44 à une liquidation de 2019 et
×5,18 en 2020 — attendre un an fait <em>perdre</em>, parce que l'année traversée
s'est mal passée. Lissée sur cinq ans, elle vaut ×6,64 puis ×6,71 : le trou de
2020 est absorbé par les quatre années qui l'entourent au lieu d'être porté en
entier par qui a eu le tort de liquider cette année-là. Sur 1950-2025, le PIB
nominal brut compte deux années où liquider plus tard rapporte moins ; lissé sur
trois ou cinq ans, aucune.</p>
<p>Une réserve pour lire le tableau : sur quatre-vingts ans, une moyenne
glissante n'est pas neutre. Elle revient à mesurer la croissance depuis une base
reculée d'environ la moitié de la fenêtre, ce qui gonfle le cumul d'une
vingtaine de pour cent à cinq ans — sans qu'aucune série ait changé. Sur une
carrière, l'écart entre lissé et non lissé reste d'un à deux points. Et la règle
italienne n'est reprise ici que par son taux, pas par le reste du système
italien (décalage de publication de deux ans, coefficients de transformation,
planchers).</p>
<p>Le minimum n'est pas la seule statistique possible sur ces trois séries. Deux
variantes gardent les <em>mêmes</em> termes et ne changent que ce qu'on en
retient : la <strong>médiane</strong> — le taux du milieu — et la
<strong>moyenne</strong>. Le résultat n'est pas celui qu'on attend. La médiane
est l'inflation ou le salaire moyen trois années sur quatre, donc un taux
nominal : elle suit les prix et les dépasse même un peu, et cesse d'être une
règle d'austérité. La moyenne, elle, est plus sévère que les prix, non par
sévérité assumée mais parce qu'elle incorpore un tiers de productivité réelle
<em>chaque</em> année, y compris à vingt points d'inflation — là où le minimum
et la médiane ne retiennent le terme réel que les années où il gagne. Les deux
sont sélectionnables dans les options de modélisation.</p>

<h3>Ce que le scénario 1 applique du droit positif</h3>
<p>L'étalon ne vaut que par ce qu'il reproduit. Il applique la décote et la
surcote, la proratisation par la durée, le salaire de référence de chaque
régime — sur ses seules années, jamais sur toute la carrière —, et cinq
paramètres lus à la GÉNÉRATION et non à l'année de liquidation : durée requise,
âge légal, âge d'annulation de la décote, coefficient de minoration, nombre
d'années retenues au salaire de référence.</p>
<p>Il applique aussi, dans l'ordre où le droit les applique, les avantages non
contributifs que la carrière suffit à déterminer :</p>
<ul>
  <li><strong>l'assurance vieillesse des parents au foyer</strong>, qui porte au
  compte un salaire forfaitaire égal au SMIC — c'est ce qui la distingue d'une
  période assimilée, laquelle valide des trimestres sans jamais ajouter de
  salaire ;</li>
  <li><strong>les trimestres accordés au titre des enfants</strong>, datés : la
  majoration de durée d'assurance du régime général et des régimes alignés naît
  en 1972 à un an par enfant, passe à deux ans en 1975 et va à la mère ; la
  fonction publique et les régimes spéciaux servent leur bonification, un an par
  enfant né avant 2004 et deux trimestres pour les enfants nés depuis. Ils sont
  attribués DANS un régime et non au-dessus d'eux : ils comptent donc aussi dans
  sa proratisation ;</li>
  <li><strong>le minimum contributif</strong>, réservé aux pensions liquidées au
  taux plein, proratisé par la durée d'assurance acquise dans le régime, et sa
  majoration au titre des périodes cotisées proratisée par la seule durée
  cotisée, puis écrêté quand le total des pensions personnelles dépasse le
  plafond de l'article L. 173-2 ;</li>
  <li><strong>le minimum garanti</strong> de la fonction publique, barème en
  escalier sur la durée de services — 57,5 % de la référence à quinze ans, 95 %
  à trente, la totalité à quarante ;</li>
  <li><strong>la surcote parentale</strong>, créée par la loi du 14 avril 2023 :
  1,25 % par trimestre acquis entre 63 ans et l'âge légal, quatre au plus, à qui
  justifie de la durée requise à 63 ans et détient un trimestre de majoration
  pour enfants. C'est la contrepartie du recul de l'âge légal, et elle se cumule
  avec la surcote ordinaire, qui ne compte qu'au-delà de cet âge ;</li>
  <li><strong>la majoration pour trois enfants</strong>, calculée sur le montant
  déjà relevé par les minima, et plafonnée en euros à la complémentaire ;</li>
  <li><strong>le minimum vieillesse</strong>, allocation différentielle servie à
  partir de 65 ans sous le barème d'une personne seule. Ce n'est pas une
  pension : elle apparaît toujours comme une ligne séparée de la cascade.</li>
</ul>
<p>Deux barèmes propres complètent l'ensemble : la décote de la fonction
publique, dont le coefficient et l'âge d'annulation montent en charge de 2006 à
2020 et dont l'âge d'annulation est la limite d'âge du grade et non 67 ans ; et
la garantie minimale de points de l'Agirc, 120 points par an de 1989 à 2018
même quand la tranche B est nulle.</p>
<p>Enfin, le scénario dit si le droit <strong>ouvre</strong> la liquidation
demandée — âge légal du régime, ou départ anticipé pour carrière longue. Quand
il ne l'ouvre pas, le montant reste calculé, parce qu'il faut comparer les cinq
scénarios sur la même carrière, mais la page le signale : il ne décrit alors
aucune pension que le système actuel servirait.</p>

<h3>Ce qui est supprimé dans les scénarios notionnels</h3>
<p>Le principe « seules les cotisations comptent » est appliqué sans exception :
ni minimum contributif, ni minimum garanti, ni ASPA, ni majoration pour enfants,
ni majoration de durée d'assurance, ni AVPF, ni bonifications, ni catégorie
active, ni périodes assimilées, ni réversion, ni décote ni surcote. Le scénario
1 les conserve tous, puisqu'il décrit le droit en vigueur.</p>

<h3>La fusion des régimes</h3>
<p>À compter de l'année de bascule, les ${nombreRegimes} régimes du catalogue sont remplacés
par un régime unique dont chaque paramètre est le plus défavorable de
l'ensemble : ouverture à ${age(fusionne.age_ouverture)}, taux plein à
${age(fusionne.age_taux_plein)}, ${fusionne.duree_requise_trimestres} trimestres
requis, cotisation de ${g.pourcentage(fusionne.taux_cotisation_retraite, false, 2)}
sur assiette déplafonnée.</p>

<h3>Une carrière, plusieurs métiers</h3>
<p>Une carrière se décrit comme une <strong>suite de métiers</strong> : chacun
porte un statut d'affiliation, un âge de début et un niveau de revenu, et court
jusqu'au début du suivant. On faisait autrefois le même métier toute sa vie ;
c'est devenu l'exception, et chaque changement fait passer d'un régime à un
autre — donc d'un taux de cotisation, d'une assiette et d'un barème à un autre.
C'est précisément ce que les cinq scénarios mesurent.</p>
<p>Deux conventions le bornent, imposées l'une et l'autre par la maille des
données. Le <strong>profil de carrière</strong> vaut pour la vie active entière,
changements compris : c'est une progression de carrière et non d'emploi, et le
niveau propre à chaque métier s'y superpose au lieu de la remettre à zéro. Et
une <strong>année civile n'a qu'un statut</strong> — un salaire est déclaré à
l'année, les régimes liquident à l'année : l'année d'un changement revient au
métier qui en occupe le plus de mois, et à égalité à celui qui l'ouvre, tandis
que le revenu porté au compte reste la somme de ce que les deux ont
réellement payé.</p>

<h3 id="unites">Brut, net, euros et francs</h3>
<p>Tout ce que le modèle manipule est <strong>brut</strong> : le revenu
d'activité saisi, les cotisations versées, le capital notionnel, les cinq
pensions. « Brut » a ici le sens des comptes nationaux — <em>salaires et
traitements bruts</em> (D11) rapportés à l'emploi salarié intérieur, ce qui est
la définition même du salaire moyen par tête qui sert d'unité. C'est-à-dire
<strong>avant</strong> cotisations salariales, <strong>avant</strong> CSG et
CRDS, <strong>avant</strong> impôt sur le revenu, et <strong>hors</strong>
cotisations patronales, qui s'ajoutent au brut sans en faire partie. Ce n'est
pas une commodité : c'est l'assiette sur laquelle les régimes appellent leurs
cotisations, donc la seule grandeur qu'un compte notionnel puisse enregistrer.
Le taux de remplacement affiché rapporte donc un brut à un brut, et il est
mécaniquement plus bas qu'un taux calculé sur des nets — les pensions sont moins
prélevées que les salaires.</p>
<p>L'unité de saisie est le <strong>multiple du salaire moyen</strong> de
l'année considérée, parce qu'elle seule garde son sens sur quatre-vingts ans :
une somme n'en a que rapportée à son année et à sa monnaie. Le formulaire
accepte néanmoins des montants — euros ou francs, mensuels ou annuels — et fait
la conversion, qu'il affiche : <code>niveau = montant annuel ÷ salaire moyen de
l'année indiquée</code>. Les francs sont convertis au taux irrévocable du
règlement (CE) n° 2866/98, <strong>1 € = 6,559 57 F</strong>, et par cent de
plus avant 1960, le nouveau franc du décret du 27 décembre 1958 valant cent
anciens francs.</p>
<p>Reste que les comptes nationaux ne publient que des <em>taux de croissance</em>
du salaire moyen. Les niveaux en sont reconstitués à partir d'un point
d'ancrage — <strong>40 000 € bruts annuels en 2024</strong> —, paramètre
documenté et non donnée certifiée. Il déplace proportionnellement tous les
revenus reconstitués, donc toutes les pensions, mais il est sans effet sur les
<strong>rapports</strong> entre scénarios, qui sont l'objet du modèle. Il
commande en revanche la traduction d'un montant en multiple : saisir un salaire
en euros, c'est le lire à cette échelle-là.</p>

<h3>Périmètre</h3>
<p>Origine 1941 (allocation aux vieux travailleurs salariés), premier dispositif
où les cotisations des actifs financent les prestations des retraités. Les
assurances sociales de 1930, en capitalisation individuelle, et le RAFP sont
isolés dans un compartiment séparé, jamais converti.</p>

<p><a href="${g.DEPOT}/blob/main/docs/methodologie.md">Méthodologie complète</a> ·
<a href="${g.DEPOT}/blob/main/docs/limites.md">Limites connues</a></p>
`;
}

function donnees(contexte) {
  const simulateur = contexte.simulateur();
  const macro = simulateur.macro;

  const periodes = [];
  for (let debut = 1940; debut < 2030; debut += 10) {
    const fin = debut + 9;
    periodes.push([
      `${debut}-${fin}`,
      echapper(nomFiabilite(macro.inflation.fiabiliteMinimaleSur(debut, fin))),
      echapper(nomFiabilite(macro.salaire_moyen.fiabiliteMinimaleSur(debut, fin))),
      echapper(nomFiabilite(macro.productivite.fiabiliteMinimaleSur(debut, fin))),
      `<strong>${echapper(nomFiabilite(macro.fiabiliteSur(debut, fin)))}</strong>`,
    ]);
  }

  const parNiveau = new Map();
  for (const regime of simulateur.catalogue) {
    const niveau = nomFiabilite(regime.fiabilite);
    if (!parNiveau.has(niveau)) {
      parNiveau.set(niveau, []);
    }
    parNiveau.get(niveau).push(regime.code);
  }
  const regimes = ["certifiee", "haute", "moyenne", "estimee"]
    .filter((niveau) => parNiveau.has(niveau))
    .map((niveau) => [
      niveau,
      String(parNiveau.get(niveau).length),
      echapper([...parNiveau.get(niveau)].sort().join(", ")),
    ]);

  const journal = contexte.paquet.certification || {};
  const certifications = Object.entries(journal.series || {})
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([nom, trace]) => [
      echapper(nom), String(trace.valeurs),
      echapper(trace.niveau ?? "certifiee"), echapper(trace.source),
    ]);

  const bandeau = certifications.length > 0
    ? `<div class="note"><strong>Les séries macroéconomiques sont
certifiées de 1950 à 2025</strong>, les tables de mortalité sont celles
réellement observées depuis 1986, et le plafond de la Sécurité sociale remonte à
1931 daté décret par décret — le tout recontrôlé automatiquement contre les
sources, le ${echapper(journal.certifie_le)}. Ce qui précède 1950 et les
paramètres propres à chaque régime restent saisis à la main : les
<em>niveaux</em> de pension des carrières les plus anciennes gardent une marge,
les <em>écarts entre scénarios</em>, qui sont l'objet du modèle, sont plus
robustes encore.</div>`
    : `<div class="note avertissement"><strong>Aucune série n'a
encore été recontrôlée contre sa source.</strong> Lancer <code>scripts/fetch/</code>
puis <code>scripts/verifier_donnees.py --appliquer</code>.</div>`;

  return `
<h2 style="margin-top:0">Ce que valent les chiffres</h2>
${bandeau}

<h3>Ce qui a été recontrôlé contre la source</h3>
${g.tableau(["Série", "Valeurs", "Niveau", "Source"], certifications,
    ["", "nombre", "", ""])}
<p class="discret">Une valeur n'est « certifiée » que si elle a été confrontée au
fichier téléchargé depuis le <em>producteur</em> de la donnée. Une transcription
tierce, même sourcée et reprise automatiquement, plafonne à « haute ». Hors de
cette liste : les séries d'avant 1950, les taux de cotisation d'avant 1967, le
plafond d'avant 2002 et le point d'indice de la fonction publique, repris
d'OpenFisca, les montants servis du minimum contributif, du minimum garanti et
du minimum vieillesse — transcrits de leur publication, et préférés à toute
projection parce qu'ils disent ce qui a été payé —, et les âges, durées et
coefficients propres à chaque régime, repris des textes.</p>

<h3>Fiabilité des séries macroéconomiques, par décennie</h3>
${g.tableau(
    ["Période", "Inflation", "Salaire moyen", "Productivité", "Ensemble"],
    periodes,
    ["", "", "", "", ""],
  )}
<p class="discret">Une projection ne se fait jamais passer pour une observation :
au-delà de la dernière année observée, la fiabilité retombe à « estimée ».</p>

<h3>Fiabilité des ${simulateur.catalogue.taille} régimes</h3>
${g.tableau(["Niveau", "Nombre", "Régimes"], regimes, ["", "nombre", ""])}

<h3>Sources</h3>
<p>Vingt-six institutions sont recensées dans
<a href="${g.DEPOT}/blob/main/data/sources.yaml">data/sources.yaml</a> : INSEE,
COR, Comité de suivi des retraites, DREES, CNAV, Service des retraites de l'État,
Caisse des dépôts, Direction de la Sécurité sociale, Cour des comptes,
Agirc-Arrco, Assemblée nationale, Union Retraite, CCMSA, CNAVPL, CNBF, DGAFP,
Direction du Budget, ERAFP, Ircantec, caisses des régimes spéciaux, Urssaf,
Légifrance, INED, Eurostat, OCDE, OpenFisca-France.</p>
<p>Chaque valeur porte son niveau de fiabilité — <code>certifiee</code>,
<code>haute</code>, <code>moyenne</code>, <code>estimee</code> — et la fiabilité
d'un résultat est celle de son maillon le plus faible.</p>
<p>Quand deux institutions publient le même chiffre, quatre critères disent
laquelle aller chercher : le <strong>producteur</strong> prime sur le repreneur,
l'<strong>observé</strong> sur le projeté, le <strong>montant servi</strong> sur
le montant calculé, le <strong>recontrôlable</strong> sur le saisi. Ce n'est pas
un classement d'institutions mais de natures de données : l'INSEE pour ce qu'il
mesure, le COR pour ce qu'il décide.</p>
<p><a href="${g.DEPOT}/blob/main/docs/limites.md">Limites détaillées</a></p>
`;
}
