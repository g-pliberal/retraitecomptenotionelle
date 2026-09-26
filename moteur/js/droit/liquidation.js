/**
 * Liquider : `liquider(demande, état, contexte)` (docs/architecture.md, § 7.3).
 *
 * Jumeau de `src/retraite_notionnelle/droit/liquidation.py` : une FONCTION
 * PURE, qui ne lit rien d'autre que ses trois entrées — la demande, l'état (la
 * chronologie par sa vue, la carrière, et le journal de l'échéancier), le
 * contexte (l'univers, dont le moteur du scénario 1 tient les tables, et ce
 * qu'une couche d'un seul calcul neutralise). Elle fait l'acquisition, ouvre
 * le droit, liquide chaque régime, mesure par des liquidations d'essai ce
 * qu'apportent les trimestres des enfants, l'AVPF et les points gratuits, puis
 * complète tous régimes. L'ASPA vient après, de l'étape « foyer et net ». Ce
 * qu'elle rend, `Liquidation`, suit le contrat C.6. Chaque appel est compté.
 */

import { formatFixe } from "../format.js";
import { Fiabilite } from "../serie.js";
import { dateDEffet } from "./commun.js";
import { FICHES, completer } from "./completer.js";
import { liquiderChaqueRegime } from "./liquider.js";
import { ouvrir } from "./ouvrir.js";
import { construire } from "./releve.js";

/** La version du contrat C.6. */
export const SCHEMA_VERSION = 1;

/** Ce que chaque dispositif s'appelle dans la cascade des avantages. */
const LIBELLE_MAJORATION = {
  mda: "Majoration de durée d'assurance",
  bonifications: "Bonification pour enfants",
};

/** Ce que chaque mesure de la cascade neutralise de plus que la précédente. */
export const NEUTRALISATION_MESUREE = {
  majoration_duree_assurance: "avantages_non_contributifs",
  avpf: "avpf",
  points_gratuits_rco: "points_gratuits",
};

/** La demande (contrat C.6, `demande`). */
export class Demande {
  constructor({ personne, dateEffet, evenement = "depart", dateEvenement = null,
    motif = "vieillesse", nature = "definitive", regimes = [] }) {
    this.personne = personne;
    this.dateEffet = dateEffet;
    this.evenement = evenement;
    this.dateEvenement = dateEvenement;
    this.motif = motif;
    this.nature = nature;
    this.regimes = regimes;
  }

  /** La demande, telle que le contrat C.6 la décrit. */
  donnees() {
    const donnee = {
      personne: this.personne, date_effet: this.dateEffet,
      evenement: { sorte: this.evenement, date: this.dateEvenement ?? this.dateEffet },
      motif: this.motif, nature: this.nature,
    };
    if (this.regimes.length > 0) {
      donnee.regimes = [...this.regimes];
    }
    return donnee;
  }
}

/** La demande qu'un départ en retraite appelle, à la date d'effet de la carrière. */
export function demandeDeDepart(carriere, nature = "definitive") {
  const date = dateDEffet(carriere);
  return new Demande({ personne: carriere.personne, dateEffet: date, dateEvenement: date,
    nature });
}

/** L'état que la liquidation lit : la carrière, et le journal de l'échéancier. */
export class Etat {
  constructor(carriere, journal = null) {
    this.carriere = carriere;
    this.journal = journal;
  }
}

/**
 * Le contexte d'une liquidation : l'univers, la date d'observation,
 * l'hypothèse, et ce qu'une couche d'un seul calcul neutralise — la liste
 * `neutralisations` du vocabulaire, que le paquet porte.
 */
export class Contexte {
  constructor(univers, neutralisations = [], observation = null, hypothese = null) {
    this.univers = univers;
    this.neutralisations = new Set(neutralisations);
    this.observation = observation;
    this.hypothese = hypothese;
    const connues = new Set(univers.macro.paquet.neutralisations ?? []);
    const inconnues = [...this.neutralisations].filter((nom) => !connues.has(nom));
    if (inconnues.length > 0) {
      throw new Error(`neutralisations inconnues du vocabulaire : ${inconnues.sort().join(", ")}`);
    }
  }

  neutralise(nom) {
    return this.neutralisations.has(nom);
  }

  /** Le même contexte, qui neutralise aussi `noms` : celui d'une liquidation d'essai. */
  neutralisant(...noms) {
    return new Contexte(this.univers, [...this.neutralisations, ...noms], this.observation,
      this.hypothese);
  }

  donnees() {
    return {
      univers: "droit_reel", observation: this.observation, hypothese: this.hypothese,
      neutralisations: [...this.neutralisations].sort(),
    };
  }
}

/** Ce que `liquider` rend (contrat C.6). */
export class Liquidation {
  constructor({ demande, contexte, releve, ouverture, pensions, complements, mesures,
    avantages, total, horsRepartition, totalContributif, fiabilite }) {
    this.demande = demande;
    this.contexte = contexte;
    this.releve = releve;
    this.ouverture = ouverture;
    this.pensions = pensions;
    this.complements = complements;
    this.mesures = mesures;
    this.avantages = avantages;
    this.total = total;
    this.horsRepartition = horsRepartition;
    this.totalContributif = totalContributif;
    this.fiabilite = fiabilite;
  }

  get carriere() {
    return this.releve.carriere;
  }

  /** Les pensions de régime, complétées. */
  get regimes() {
    return this.complements.regimes;
  }

  /** Ses composantes : la pension de chaque régime, puis la majoration pour enfants. */
  composantes() {
    const moteur = this.contexte.univers;
    const isoler = moteur.parametres.isoler_capitalisation;
    const debut = this.demande.dateEffet;
    const composantes = this.regimes.map((p) => ({
      id: `pension_${p.regime}`, beneficiaire: this.demande.personne,
      montant: { annuel: p.montant, monnaie: "EUR" }, debut, regime: p.regime,
      detail: p.detail,
      hors_repartition: Boolean(isoler && moteur.catalogue.obtenir(p.regime).hors_repartition),
    }));
    for (const avantage of this.complements.avantages) {
      if (avantage.code === "majoration_enfants") {
        composantes.push({
          id: "majoration_enfants", fiche: FICHES[avantage.code],
          beneficiaire: this.demande.personne,
          montant: { annuel: avantage.montant, monnaie: "EUR" }, debut,
          detail: avantage.detail,
        });
      }
    }
    return composantes;
  }

  /** La liquidation, telle que le contrat C.6 la décrit. */
  donnees() {
    return {
      schema_version: SCHEMA_VERSION,
      demande: this.demande.donnees(),
      contexte: this.contexte.donnees(),
      composantes: this.composantes(),
      lignes_consommees: this.releve.lignes().map((ligne) => ligne.id),
      origine: "calculee",
      mesures: this.mesures.map((m) => ({
        code: m.code, neutralisation: m.neutralisation, montant: m.montant,
      })),
    };
  }
}

let nombreDAppels = 0;

/** Combien de liquidations ont été calculées : le budget de calcul les compte. */
export function appels() {
  return nombreDAppels;
}

/** La liquidation de `demande`, dans `etat`, sous `contexte`. Voir le Python. */
export function liquider(demande, etat, contexte) {
  nombreDAppels += 1;
  const moteur = contexte.univers;
  const avantagesNonContributifs = !contexte.neutralise("avantages_non_contributifs");
  const avpf = !contexte.neutralise("avpf");
  const avecPointsGratuits = !contexte.neutralise("points_gratuits");
  const releve = construire(moteur, etat.carriere, {
    avantagesNonContributifs, pointsGratuits: avecPointsGratuits,
    liquiderSuccessions: !contexte.neutralise("successions"),
  });
  const carriere = releve.carriere;
  const majorationEnfants = releve.durees.enfants;
  const gratuitsAttribues = releve.droits.gratuits;
  let fiabilite = Fiabilite.CERTIFIEE;
  if (majorationEnfants !== null) {
    fiabilite = Math.min(fiabilite, majorationEnfants.fiabilite);
  }

  const ouverture = ouvrir(moteur, releve);
  const liquidees = liquiderChaqueRegime(moteur, releve, ouverture, contexte);
  const pensions = liquidees.regimes;

  const total = pensions.reduce((somme, p) => somme + p.montant, 0.0);

  // CE QUI N'EST PAS DE LA RÉPARTITION EST SERVI À PART. Le RAFP et les
  // anciennes assurances sociales sont des régimes PROVISIONNÉS : leur rente
  // sort d'un placement, pas de la cotisation des actifs. Une réforme qui
  // remplace la répartition par des comptes notionnels ne les atteint pas, et
  // les scénarios notionnels les isolent déjà. Les laisser dans le total du
  // scénario 1 revenait à comparer un total qui les contient à quatre totaux
  // qui ne les contiennent pas.
  //
  // Le calcul lui-même n'est pas touché : l'écrêtement du minimum contributif
  // et l'ASPA continuent de regarder TOUTES les pensions, comme le fait le
  // droit. Seul le total rendu est celui de la répartition.
  const horsRepartition = moteur.parametres.isoler_capitalisation
    ? pensions.reduce(
      (somme, p) => somme + (moteur.catalogue.obtenir(p.regime).hors_repartition
        ? p.montant : 0.0), 0.0)
    : 0.0;

  let totalContributif = total - horsRepartition;
  const avantages = [];

  // Avantages non contributifs du droit positif, DANS L'ORDRE OÙ LE DROIT
  // LES APPLIQUE, et l'ordre commande le résultat : les points gratuits de la
  // RCO et l'AVPF d'abord, qui déplacent le compte de points et le salaire
  // annuel moyen ; la majoration de durée d'assurance ensuite, qui change la
  // décote et la proratisation ; puis le minimum
  // contributif, qui porte la pension de base à son plancher ; puis seulement
  // la majoration pour enfants, qui se calcule SUR CE plancher ; l'ASPA
  // enfin, qui est différentielle et complète tout le reste.

  if (avantagesNonContributifs && majorationEnfants !== null) {
    // Effet des trimestres accordés au titre des enfants : la même carrière
    // sans eux, tout le reste égal.
    const sansMda = liquider(demande, new Etat(carriere),
      contexte.neutralisant("avantages_non_contributifs"));
    // Les deux termes doivent porter sur le même périmètre : celui d'en
    // face est déjà net de la capitalisation.
    const effet = (total - horsRepartition) - sansMda.totalContributif;
    // Ces trimestres sont déjà incorporés aux pensions de régime : la base
    // contributive de la cascade est celle d'AVANT.
    totalContributif = sansMda.totalContributif;
    if (Math.abs(effet) > 1e-9) {
      avantages.push({
        code: "majoration_duree_assurance",
        libelle: LIBELLE_MAJORATION[majorationEnfants.dispositif],
        montant: effet,
        detail: `${majorationEnfants.trimestres} trimestres pour `
          + `${carriere.nombre_enfants} enfant`
          + `${carriere.nombre_enfants > 1 ? "s" : ""}, `
          + `au titre du régime « ${majorationEnfants.regime} »`,
      });
    }
  }

  if (avantagesNonContributifs && avpf
      && carriere.lignes.some((ligne) => ligne.revenu_avpf > 0)) {
    // Effet de l'AVPF, mesuré comme celui de la MDA : la même carrière sans
    // le salaire forfaitaire porté au compte. Il joue en amont de tout le
    // reste, et peut jouer dans les deux sens — il relève une carrière longue
    // à bas salaire, il abaisse la moyenne d'une carrière courte et bien
    // payée, où les années au SMIC s'ajoutent aux années retenues.
    const sansAvpf = liquider(demande, new Etat(carriere),
      contexte.neutralisant("avantages_non_contributifs", "avpf"));
    const effetAvpf = totalContributif - sansAvpf.totalContributif;
    totalContributif = sansAvpf.totalContributif;
    if (Math.abs(effetAvpf) > 1e-9) {
      avantages.unshift({
        code: "avpf",
        libelle: "Assurance vieillesse des parents au foyer",
        montant: effetAvpf,
        detail: "salaire forfaitaire au SMIC porté au compte",
      });
    }
  }

  if (avantagesNonContributifs && avecPointsGratuits && gratuitsAttribues.size > 0) {
    // Effet des POINTS GRATUITS de la RCO agricole, mesuré comme celui de
    // l'AVPF : la même carrière sans eux, la MDA et l'AVPF déjà retirées. Si
    // retirer la MDA les a fait tomber, leur effet est dans celui de la MDA,
    // qui les a ouverts, et ce recalcul n'en trouve plus rien.
    const sansGratuits = liquider(demande, new Etat(carriere), contexte.neutralisant(
      "avantages_non_contributifs", "avpf", "points_gratuits"));
    const effetGratuits = totalContributif - sansGratuits.totalContributif;
    totalContributif = sansGratuits.totalContributif;
    if (Math.abs(effetGratuits) > 1e-9) {
      let pointsCites = 0.0;
      let avant = Infinity;
      for (const [points, annee] of gratuitsAttribues.values()) {
        pointsCites += points;
        avant = Math.min(avant, annee);
      }
      avantages.unshift({
        code: "points_gratuits_rco",
        libelle: "Points gratuits de la complémentaire agricole",
        montant: effetGratuits,
        detail: `${formatFixe(pointsCites, 2, true)} points pour les années de chef `
          + `d'exploitation d'avant ${avant}`,
      });
    }
  }

  const complements = completer(moteur, releve, ouverture, liquidees, contexte);
  const mesures = [];
  for (const code of Object.keys(NEUTRALISATION_MESUREE)) {
    for (const avantage of avantages) {
      if (avantage.code === code) {
        mesures.push({ code, neutralisation: NEUTRALISATION_MESUREE[code],
          montant: avantage.montant });
      }
    }
  }
  return new Liquidation({
    demande, contexte, releve, ouverture, pensions: liquidees, complements, mesures,
    avantages: [...avantages, ...complements.avantages],
    total: complements.total,
    horsRepartition,
    totalContributif,
    fiabilite: Math.min(fiabilite, ouverture.fiabilite, liquidees.fiabilite,
      complements.fiabilite),
  });
}
