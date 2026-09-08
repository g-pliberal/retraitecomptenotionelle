/**
 * Le coût des cinq systèmes : ce qu'il a été depuis 1959, ce qu'il serait d'ici 2070.
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
 */

import { CAS_TYPES, calculerCasTypes } from "./castypes.js";
import { Fiabilite } from "./serie.js";

/** Les cinq systèmes, dans l'ordre du tableau de comparaison. */
export const SCENARIOS = [
  ["actuel", "1. Système actuel"],
  ["notionnel_retroactif", "2. Notionnel rétroactif, part salariale"],
  ["notionnel_prospectif", "3. Notionnel dès la bascule, part salariale"],
  ["notionnel_retroactif_employeur",
    "4. Notionnel rétroactif, avec la part patronale"],
  ["notionnel_prospectif_employeur",
    "5. Notionnel dès la bascule, avec la part patronale"],
];

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
const DEMI_TRANCHE = Math.floor(PAS_GENERATIONS / 2);

/** Simule la grille et en tire, pour chaque couple, sa pension par système. */
function pensionnes(simulateur, casTypes) {
  const grille = calculerCasTypes(simulateur, casTypes, generations());
  const liste = [];
  for (const [cle, comparaison] of grille.resultats) {
    const pensions = {};
    for (const [scenario] of SCENARIOS) {
      pensions[scenario] = comparaison.enEurosConstants(
        comparaison[scenario].pension_annuelle,
      );
    }
    // La clé de la grille est « code|génération » : la génération en est la
    // seconde moitié, et c'est elle qui dit quel âge ce couple a chaque année.
    liste.push({
      generation: Number(cle.slice(cle.indexOf("|") + 1)),
      anneeLiquidation: comparaison.carriere.anneeLiquidation,
      pensions,
    });
  }
  const motifs = new Map();
  for (const motif of grille.echecs.values()) {
    motifs.set(motif, (motifs.get(motif) || 0) + 1);
  }
  return { liste, motifs };
}

/**
 * Masse de pensions par système, une année donnée, et le nombre de couples.
 *
 * Les cinq cohortes que représente une génération de la grille sont parcourues
 * une à une : chacune porte l'effectif réel de sa classe d'âge et liquide sa
 * propre année. Les faire basculer le même jour ferait avancer la trajectoire
 * par marches de cinq ans au lieu de la faire monter.
 */
function masses(liste, population, annee) {
  const total = {};
  for (const [scenario] of SCENARIOS) total[scenario] = 0;
  let vivants = 0;
  for (const pensionne of liste) {
    let poids = 0;
    for (let decalage = -DEMI_TRANCHE; decalage <= DEMI_TRANCHE; decalage += 1) {
      if (annee < pensionne.anneeLiquidation + decalage) continue;
      poids += population.effectif(annee - pensionne.generation - decalage, annee);
    }
    if (poids <= 0) continue;
    vivants += 1;
    for (const [scenario] of SCENARIOS) {
      total[scenario] += poids * pensionne.pensions[scenario];
    }
  }
  return { total, vivants };
}

function rapports(total) {
  const resultat = {};
  for (const [scenario] of SCENARIOS) {
    resultat[scenario] = total[scenario] / total.actuel;
  }
  return resultat;
}

/** Le coût d'une année, observé puis recalculé pour chaque système. */
class CoutAnnuel {
  constructor(annee, observee, coefficientConstants, partPib, rapportsAnnee, nombre) {
    this.annee = annee;
    this.observee = observee;
    this.coefficientConstants = coefficientConstants;
    this.partPib = partPib;
    this.rapports = rapportsAnnee;
    this.pensionnes = nombre;
  }

  /** Coût du système, en millions d'euros courants de l'année. */
  cout(scenario) {
    return this.observee * this.rapports[scenario];
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
              dependance) {
    this.annee = annee;
    this.projete = projete;
    this.base = base;
    this.coefficientConstants = coefficientConstants;
    this.pib = pib;
    this.rapports = rapportsAnnee;
    this.dependance = dependance;
  }

  /** Coût du système, en millions d'euros constants de référence. */
  coutConstants(scenario) {
    return this.base * this.rapports[scenario];
  }

  /** Le même coût, ramené aux euros courants de son année. */
  cout(scenario) {
    return this.coutConstants(scenario) / this.coefficientConstants;
  }

  /** Part du PIB : deux grandeurs de la même année, donc deux euros courants. */
  partPib(scenario) {
    return this.pib ? this.cout(scenario) / this.pib : 0.0;
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
}

/** La série complète, et les cumuls qu'on en tire. */
class Cout {
  constructor(annees, avenir, anneeEuros, generationsRetenues, echecs, fiabilite) {
    this.annees = annees;
    this.avenir = avenir;
    this.anneeEuros = anneeEuros;
    this.generations = generationsRetenues;
    this.echecs = echecs;
    this.fiabilite = fiabilite;
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
function construireAvenir(liste, depenses, population, simulateur) {
  const macro = simulateur.macro;
  const anneeEuros = simulateur.parametres.annee_euros_constants;
  const dernierePubliee = depenses.derniereAnnee;

  const ancrageMasses = masses(liste, population, dernierePubliee).total;
  if (ancrageMasses.actuel <= 0) {
    return new Avenir([], 0, 0, anneeEuros, Fiabilite.ESTIMEE);
  }
  // Les deux termes sont mis dans la MÊME unité avant d'être divisés : la
  // dépense publiée, en euros de son année, est ramenée aux euros constants où
  // les pensions du modèle sont déjà exprimées.
  const ancrage = depenses.repartition(dernierePubliee)
    * macro.coefficientPrix(dernierePubliee, anneeEuros) / ancrageMasses.actuel;

  // Le PIB est publié jusqu'en 2025 ; au-delà il croît au rythme nominal des
  // hypothèses de projection, CORRIGÉ de l'évolution de la population d'âge
  // actif. Sans cette correction, la France de 2070 produirait avec douze pour
  // cent d'actifs qu'aucune projection ne lui donne.
  const dernierePib = depenses.pib.derniereAnnee;
  const pibProjete = new Map();
  let courant = depenses.pib.valeur(dernierePib);
  for (let annee = dernierePib + 1; annee <= HORIZON; annee += 1) {
    courant *= (1.0 + macro.pib_nominal.valeur(annee))
      * (population.actifs.valeur(annee) / population.actifs.valeur(annee - 1));
    pibProjete.set(annee, courant);
  }

  const lignes = [];
  for (let annee = depenses.premiereAnneeVentilee; annee <= HORIZON; annee += 1) {
    const total = masses(liste, population, annee).total;
    if (total.actuel <= 0) continue;
    const projete = annee > dernierePubliee;
    const coefficient = macro.coefficientPrix(annee, anneeEuros);
    const base = projete
      ? ancrage * total.actuel
      : depenses.repartition(annee) * coefficient;
    const actifs = population.actifs.valeur(annee);
    lignes.push(new AvenirAnnuel(
      annee,
      projete,
      base,
      coefficient,
      pibProjete.has(annee)
        ? pibProjete.get(annee)
        : depenses.pib.valeur(Math.min(annee, dernierePib)),
      rapports(total),
      actifs
        ? population.effectifTranche(AGE_DEPENDANCE, population.ageMaximal, annee)
          / actifs
        : 0.0,
    ));
  }

  // Une trajectoire ne peut pas valoir mieux qu'estimée : sa démographie est
  // projetée, sa macroéconomie est une hypothèse, et son contrefactuel n'a
  // jamais existé.
  return new Avenir(
    lignes, dernierePubliee + 1, simulateur.parametres.annee_bascule,
    anneeEuros, Fiabilite.ESTIMEE,
  );
}

/**
 * Le coût observé, les quatre contrefactuels, et la trajectoire jusqu'en 2070.
 * Les années où le modèle ne sert aucune pension sont écartées : un rapport y
 * serait une division par zéro, et non un résultat.
 */
export function calculerCout(simulateur, depenses, population,
                             casTypes = CAS_TYPES) {
  const { liste, motifs } = pensionnes(simulateur, casTypes);
  const macro = simulateur.macro;
  const anneeEuros = simulateur.parametres.annee_euros_constants;

  const lignes = [];
  for (const annee of depenses.annees()) {
    const { total, vivants } = masses(liste, population, annee);
    if (total.actuel <= 0) continue;
    lignes.push(new CoutAnnuel(
      annee,
      depenses.depense(annee),
      macro.coefficientPrix(annee, anneeEuros),
      depenses.partPib(annee),
      rapports(total),
      vivants,
    ));
  }

  let fiabilite = Fiabilite.ESTIMEE;
  for (const ligne of lignes) {
    fiabilite = Math.min(fiabilite, depenses.fiabilite(ligne.annee));
  }
  // Le contrefactuel ne peut jamais valoir mieux qu'« estimé » : la dépense
  // observée est certifiée, le rapport qui la corrige ne l'est pas et ne peut
  // pas l'être.
  return new Cout(
    lignes,
    construireAvenir(liste, depenses, population, simulateur),
    anneeEuros,
    generations(),
    motifs,
    Math.min(fiabilite, Fiabilite.ESTIMEE),
  );
}
