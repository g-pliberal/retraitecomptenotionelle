/**
 * Les avantages non contributifs du scénario 1 : lesquels, depuis quand, combien.
 *
 * Portage de ``src/retraite_notionnelle/avantages.py``.
 *
 * Le scénario 1 est le droit en vigueur. Un compte notionnel ne sert que ce qui
 * a été cotisé. Tout ce qui sépare les deux est inventorié dans
 * ``data/reference/legislation/avantages_non_contributifs.yaml``, que le paquet
 * de données transporte sous la clé ``avantages``.
 *
 * CE QUE L'INVENTAIRE PORTE, ET QUE LE MODÈLE NE CALCULE PAS
 * Trente-neuf dispositifs, chacun avec sa date de création, sa date de fin
 * quand il est éteint, sa base légale et l'état du modèle à son égard. C'est
 * une DONNÉE, pas un résultat : le comptage que la page trace ne suppose aucun
 * calcul, et c'est ce qui le rend sûr là où les masses sont fragiles.
 *
 * LES DEUX SÉRIES DE COÛT, ET POURQUOI ELLES NE DISENT PAS LA MÊME CHOSE
 * 1. Ce que l'avantage ajoute au MONTANT de la pension. La cascade du
 *    scénario 1 en isole huit ; deux autres — les périodes assimilées et la
 *    catégorie active — sont servies sans être isolées, leur effet passant par
 *    un trimestre ou par un âge, et se mesurent par RECALCUL : on refait la
 *    pension sans l'avantage, à date de liquidation inchangée, et l'écart est
 *    la ligne.
 * 2. Ce qu'un avantage d'ÂGE coûte en ANNÉES DE SERVICE. C'est le second
 *    effet, et il est treize fois plus lourd. Une pension servie de
 *    cinquante-deux à soixante-quatre ans est douze annuités que personne n'a
 *    cotisées et qu'aucune décote ne rattrape : l'article L. 14 la plafonne à
 *    vingt trimestres, si bien que l'agent classé et l'agent sédentaire partis
 *    le même jour butent sur le même plafond.
 *
 * CE QUE CES SÉRIES VALENT, ET IL FAUT LE DIRE AVANT DE LES LIRE
 * La grille de cas types n'est pas une population. Un seul de ses treize cas
 * types a des enfants, un seul porte des interruptions, aucun ne connaît le
 * chômage. Les masses qui en sortent sont donc des PLANCHERS, et très bas.
 */

import { CAS_TYPES, ageLiquidationPour } from "./castypes.js";
import { DEMI_TRANCHE, generations, ponderation } from "./cout.js";

/** Les quatre états possibles du modèle à l'égard d'un avantage. */
export const ETATS = new Set(["chiffre", "integre", "declare", "absent"]);

/** Les trois façons d'en mesurer le coût. */
export const MESURES = new Set(["modele", "serie_publiee", "aucune"]);

/** La part contributive, sous une clé qui ne peut être celle d'aucun avantage. */
export const CONTRIBUTIF = "_contributif";

/**
 * Les avantages que le scénario 1 sert mais que la cascade N'ISOLE PAS, et
 * qu'on mesure donc par recalcul. Leur montant est PRIS SUR la part
 * contributive, où la cascade les avait laissés faute de savoir les séparer :
 * la somme des parts vaut donc toujours la pension entière.
 */
export const RECALCULS = [
  "periodes_assimilees",
  "categorie_active",
  "age_jouissance_militaire",
];

/**
 * Pour chaque statut CLASSÉ, le statut sédentaire de mêmes régimes.
 *
 * Le classement tient à l'emploi et non à la personne : la contrefactuelle d'un
 * agent de catégorie active est le même agent, même caisse, même traitement,
 * dont l'emploi ne serait pas classé. Les régimes sont identiques des deux
 * côtés — un test l'exige —, si bien que l'écart ne porte que sur l'âge opposé.
 *
 * Les militaires y figurent sous leur propre ligne : ce n'est pas un classement
 * d'emploi, c'est une pension qui s'ouvre à une DURÉE DE SERVICES et non à un
 * âge. Leur contrefactuelle est refusée — voir `recalculer`.
 */
export const SEDENTAIRE = {
  fonctionnaire_etat_actif: ["fonctionnaire_etat", "categorie_active"],
  fonctionnaire_etat_super_actif: ["fonctionnaire_etat", "categorie_active"],
  fonctionnaire_territorial_hospitalier_actif: [
    "fonctionnaire_territorial_hospitalier", "categorie_active",
  ],
  fonctionnaire_territorial_hospitalier_super_actif: [
    "fonctionnaire_territorial_hospitalier", "categorie_active",
  ],
  ouvrier_etat_actif: ["ouvrier_etat", "categorie_active"],
  militaire: ["fonctionnaire_etat", "age_jouissance_militaire"],
  militaire_officier: ["fonctionnaire_etat", "age_jouissance_militaire"],
};

/**
 * Les trois familles de départ anticipé. Elles ne se recouvrent pas : un départ
 * est ouvert par un motif et un seul.
 *
 * Les confondre est la meilleure manière de se tromper de réforme. La CARRIÈRE
 * LONGUE regarde la durée cotisée, donc est la moins éloignée d'un principe
 * contributif ; le CLASSEMENT de l'emploi ne regarde ni la durée ni la
 * pénibilité réelle, mais le corps d'appartenance ; l'âge propre d'un RÉGIME
 * SPÉCIAL ne regarde que le régime.
 */
export const MOTIFS = ["carriere_longue", "classement", "regime_special"];

/** Le libellé de chaque motif, pour la légende du graphique. */
export const LIBELLES_MOTIFS = {
  carriere_longue: "Carrière longue",
  classement: "Catégorie active",
  regime_special: "Régimes spéciaux",
};

/** L'inventaire : les trente-neuf dispositifs, et les familles qui les rangent. */
export class Inventaire {
  constructor(familles, avantages) {
    this.familles = familles;
    this.avantages = avantages;
  }

  parFamille(code) {
    return this.avantages.filter((avantage) => avantage.famille === code);
  }

  compte(etat) {
    return this.avantages.filter((avantage) => avantage.etat_modele === etat).length;
  }

  /** Ceux dont le modèle sait dire ce qu'ils coûtent. */
  get chiffres() {
    return this.avantages.filter(
      (avantage) => avantage.ligne_cascade !== null || RECALCULS.includes(avantage.code),
    );
  }

  /**
   * Le nom d'une ligne de coût, qui peut porter deux dispositifs.
   *
   * La MDA et la bonification pour enfants de la fonction publique partagent
   * une ligne de cascade : le même trimestre gratuit, sous deux textes. La
   * légende du graphique doit donc les nommer toutes les deux.
   */
  libelleDeLigne(ligne) {
    const portes = this.avantages
      .filter((avantage) => avantage.ligne_cascade === ligne || avantage.code === ligne)
      .map((avantage) => avantage.libelle);
    if (portes.length === 0) return ligne;
    portes.sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
    return portes.join(" / ");
  }
}

/** L'inventaire relu depuis le paquet de données, tel que le site le charge. */
export function chargerAvantages(paquet) {
  const lignes = paquet.avantages;
  return new Inventaire(lignes.familles, lignes.avantages);
}

/**
 * La carrière d'un cas type, avec une variante possible.
 *
 * Reprend la construction ordinaire à deux libertés près, qui sont exactement
 * les deux contrefactuelles : le statut d'affiliation, et le motif des périodes
 * non travaillées. L'âge de liquidation est PASSÉ et non recalculé — c'est ce
 * qui tient les deux pensions comparables.
 */
export function carriereVariante(simulateur, cas, generation, age,
                                 affiliation = null, interruptions = null) {
  const reelles = new Map(
    cas.interruptions_relatives.map(([decalage, motif]) => [
      Math.trunc(generation + cas.age_debut + decalage), motif,
    ]),
  );
  return simulateur.carriereSimple({
    annee_naissance: generation,
    sexe: cas.sexe,
    affiliation: affiliation || cas.affiliation,
    age_debut: cas.age_debut,
    age_liquidation: age,
    niveau_salaire: cas.niveau_salaire,
    profil_carriere: cas.profil_carriere,
    interruptions: interruptions === null ? reelles : interruptions,
    nombre_enfants: cas.nombre_enfants,
    part_primes: cas.part_primes,
    identifiant: `${cas.libelle} (génération ${generation})`,
  });
}

/**
 * Les avantages non isolés par la cascade, mesurés par recalcul.
 *
 * Rend un objet VIDE quand la carrière n'en porte aucun, plutôt qu'un zéro : la
 * plupart des cas types sont dans ce cas, et un zéro écrit laisserait croire à
 * une mesure là où il n'y a rien à mesurer.
 *
 * DEUX PRÉCAUTIONS ET UN GARDE-FOU.
 *
 * La première précaution évite un double compte. Neutraliser les périodes non
 * travaillées retire les trimestres assimilés ET l'AVPF, que la cascade chiffre
 * déjà sous sa propre ligne. On la retranche donc de l'écart brut.
 *
 * La seconde est une interaction qu'on ne mesure pas. Retirer deux avantages
 * d'âge à la fois n'est pas la somme de deux retraits — la décote est
 * plafonnée, et deux pénalités qui butent sur le même plafond ne s'additionnent
 * pas. Aucun cas type de la grille ne porte les deux, et un test l'exige.
 *
 * LE GARDE-FOU refuse plutôt que de rendre un chiffre faux. Un changement de
 * statut ne vaut comme contrefactuelle que s'il ne déplace QUE l'âge opposé.
 * Quand il déplace aussi la DURÉE REQUISE, le rapport de proratisation change
 * avec lui et l'écart ne mesure plus l'avantage : c'est le cas du militaire,
 * dont la contrefactuelle civile rend une pension PLUS FORTE et l'avantage un
 * montant négatif.
 */
export function recalculer(simulateur, cas, generation, age, reelle) {
  const parts = {};
  const refus = {};
  if (cas.interruptions_relatives.length > 0) {
    const neant = new Map(
      cas.interruptions_relatives.map(([decalage]) => [
        Math.trunc(generation + cas.age_debut + decalage), "sans_activite",
      ]),
    );
    const sans = simulateur.scenarioActuel.calculer(
      carriereVariante(simulateur, cas, generation, age, null, neant),
    );
    const avpf = reelle.avantages_appliques
      .filter((avantage) => avantage.code === "avpf")
      .reduce((total, avantage) => total + avantage.montant, 0);
    const ecart = reelle.pension_annuelle - sans.pension_annuelle - avpf;
    if (ecart > 0) parts.periodes_assimilees = ecart;
  }
  if (Object.prototype.hasOwnProperty.call(SEDENTAIRE, cas.affiliation)) {
    const [temoin, ligne] = SEDENTAIRE[cas.affiliation];
    const sans = simulateur.scenarioActuel.calculer(
      carriereVariante(simulateur, cas, generation, age, temoin),
    );
    if (sans.trimestres_requis !== reelle.trimestres_requis) {
      refus[ligne] = `${cas.code} : la contrefactuelle ${temoin} exige `
        + `${sans.trimestres_requis} trimestres contre `
        + `${reelle.trimestres_requis} — la proratisation change avec le `
        + "statut, l'écart ne mesure plus l'âge";
    } else {
      const ecart = reelle.pension_annuelle - sans.pension_annuelle;
      if (ecart > 0) parts[ligne] = ecart;
    }
  }
  return [parts, refus];
}

/**
 * Ce qui ouvre ce départ, quand il est anticipé.
 *
 * Le modèle nomme la carrière longue lui-même ; les deux autres se lisent au
 * statut, le classement étant celui des sept affiliations marquées.
 */
export function motifDeDepart(cas, actuel) {
  if (actuel.motif_ouverture === "carriere_longue") return "carriere_longue";
  if (Object.prototype.hasOwnProperty.call(SEDENTAIRE, cas.affiliation)) {
    return "classement";
  }
  return "regime_special";
}

/**
 * La pension de chaque couple (cas type, génération), part par part.
 *
 * LE SCÉNARIO 1 SEUL EST CALCULÉ, et c'est ce qui rend la page tenable. La
 * grille complète rend les six scénarios quand cette décomposition n'a besoin
 * que de l'étalon. Les deux garde-fous de la grille sont repris tels quels :
 * une liquidation antérieure à la répartition et une carrière dont aucun régime
 * n'était actif sont écartées plutôt que de faire échouer l'ensemble.
 *
 * LE REFUS EST CONTAGIEUX, et il doit l'être. La durée requise d'un statut
 * varie par génération : une contrefactuelle peut être propre pour les unes et
 * faussée pour les autres. Garder les premières donnerait une série qui ne
 * porte qu'un morceau de sa population — un agrégat biaisé, et dont le biais
 * serait invisible. Une ligne refusée quelque part est donc retirée PARTOUT, et
 * son montant rendu à la part contributive d'où il venait.
 */
export function decomposer(simulateur, liquidation = "droit") {
  const macro = simulateur.macro;
  const anneeEuros = simulateur.parametres.annee_euros_constants;
  const debut = simulateur.parametres.annee_debut_repartition;
  const pensionnes = [];
  const refus = {};
  for (const cas of CAS_TYPES) {
    for (const generation of generations()) {
      let age;
      let carriere;
      let actuel;
      try {
        age = ageLiquidationPour(cas, simulateur, generation, liquidation);
        carriere = carriereVariante(simulateur, cas, generation, age);
        if (carriere.anneeLiquidation <= debut) continue;
        const connus = carriere.lignes.some(
          (ligne) => simulateur.affiliations.regimes(cas.affiliation, ligne.annee).length > 0,
        );
        if (!connus) continue;
        actuel = simulateur.scenarioActuel.calculer(carriere);
      } catch (erreur) {
        continue;
      }
      const parts = { [CONTRIBUTIF]: actuel.total_contributif };
      for (const avantage of actuel.avantages_appliques) {
        parts[avantage.code] = (parts[avantage.code] || 0) + avantage.montant;
      }
      const [mesures, refuses] = recalculer(simulateur, cas, generation, age, actuel);
      Object.assign(refus, refuses);
      for (const [ligne, montant] of Object.entries(mesures)) {
        parts[ligne] = (parts[ligne] || 0) + montant;
        parts[CONTRIBUTIF] -= montant;
      }
      const coefficient = macro.coefficientPrix(carriere.anneeLiquidation, anneeEuros);
      const constants = {};
      for (const [cle, valeur] of Object.entries(parts)) {
        constants[cle] = valeur * coefficient;
      }
      pensionnes.push({
        code: cas.code,
        generation,
        anneeLiquidation: carriere.anneeLiquidation,
        ageLiquidation: age,
        parts: constants,
        motif: motifDeDepart(cas, actuel),
      });
    }
  }
  for (const pensionne of pensionnes) {
    for (const ligne of Object.keys(refus)) {
      const montant = pensionne.parts[ligne] || 0;
      delete pensionne.parts[ligne];
      pensionne.parts[CONTRIBUTIF] += montant;
    }
  }
  return [pensionnes, refus];
}

/**
 * La masse de chaque part une année donnée.
 *
 * Copie fidèle de la pondération de `cout.js` pour le scénario 1 : chaque
 * génération de la grille en représente cinq, parcourues une à une, chacune
 * liquidant sa propre année. Le scénario 1 n'est pas revalorisé — le droit
 * l'indexe sur les prix et les masses sont déjà en euros constants —, si bien
 * qu'un seul poids suffit, celui des têtes.
 */
export function masses(pensionnes, population, annee, poidsCas) {
  const total = {};
  for (const pensionne of pensionnes) {
    const partCas = poidsCas[pensionne.code] || 0;
    if (partCas <= 0) continue;
    let poids = 0;
    for (let decalage = -DEMI_TRANCHE; decalage <= DEMI_TRANCHE; decalage += 1) {
      if (annee < pensionne.anneeLiquidation + decalage) continue;
      poids += population.effectif(annee - pensionne.generation - decalage, annee);
    }
    if (poids <= 0) continue;
    for (const [cle, montant] of Object.entries(pensionne.parts)) {
      total[cle] = (total[cle] || 0) + partCas * poids * montant;
    }
  }
  return total;
}

/**
 * La masse servie AVANT l'âge légal de droit commun, ventilée par motif.
 *
 * La comparaison se fait à l'âge légal de la GÉNÉRATION, et non à un âge fixe :
 * opposer soixante-quatre ans à une génération qui relevait de soixante
 * compterait comme anticipé un départ que le droit de l'époque disait à
 * l'heure.
 *
 * La ventilation par motif est l'essentiel du résultat. Le coût des départs
 * anticipés n'a pas la même origine selon l'époque : il vient des statuts
 * classés et des régimes spéciaux tant que ceux-ci pèsent, puis de la carrière
 * longue à mesure que l'âge légal monte au-dessus de l'âge auquel les carrières
 * commencées tôt réunissent leur durée.
 */
export function massesAnticipees(pensionnes, simulateur, population, annee, poidsCas) {
  const ages = simulateur.scenarioActuel.agesOuverture;
  let totale = 0;
  const parMotif = {};
  for (const motif of MOTIFS) parMotif[motif] = 0;
  for (const pensionne of pensionnes) {
    const partCas = poidsCas[pensionne.code] || 0;
    if (partCas <= 0) continue;
    const pension = Object.values(pensionne.parts).reduce((a, b) => a + b, 0);
    // L'ÂGE LÉGAL EST CELUI DE LA GÉNÉRATION DE LA GRILLE, et il est lu une
    // seule fois — non celui de chacune des cinq cohortes de la tranche.
    // L'âge de DÉPART a été calculé une fois, pour la génération de la grille,
    // et les cinq cohortes le portent tel quel. Opposer cet âge-là à l'âge
    // légal d'une cohorte plus jeune revenait à déclarer anticipé un départ que
    // rien n'avançait, et la réforme de 2023 faisait tripler la série sur ses
    // deux dernières années par ce seul effet de bord.
    const legal = ages.age(pensionne.generation);
    const seuil = legal === null ? null : legal[0];
    for (let decalage = -DEMI_TRANCHE; decalage <= DEMI_TRANCHE; decalage += 1) {
      const cohorte = pensionne.generation + decalage;
      if (annee < pensionne.anneeLiquidation + decalage) continue;
      const ageAtteint = annee - cohorte;
      const effectif = population.effectif(ageAtteint, annee);
      if (effectif <= 0) continue;
      const masse = partCas * effectif * pension;
      totale += masse;
      // Et seules les ANNÉES précoces comptent, non toute la retraite de qui
      // est parti tôt : l'annuité servie avant l'âge légal s'éteint le jour où
      // l'assuré l'atteint.
      if (seuil !== null && ageAtteint < seuil) {
        parMotif[pensionne.motif] += masse;
      }
    }
  }
  return [totale, parMotif];
}

/**
 * Les deux séries, année par année, sur la fenêtre des dépenses publiées.
 *
 * Les années où le modèle ne sert AUCUNE pension — celles d'avant la première
 * liquidation possible — sont écartées : une part y serait une division par
 * zéro, et non un résultat.
 */
export function calculerAvantages(simulateur, depenses, population,
                                  ponderationChoisie = "effectifs",
                                  liquidation = "droit") {
  const [pensionnes, refus] = decomposer(simulateur, liquidation);
  const poids = ponderation(simulateur, ponderationChoisie, CAS_TYPES);
  const annees = [];
  for (const annee of depenses.annees()) {
    const poidsAnnee = poids(annee);
    const parts = masses(pensionnes, population, annee, poidsAnnee);
    const totale = Object.values(parts).reduce((a, b) => a + b, 0);
    if (totale <= 0) continue;
    const observee = depenses.depense(annee);
    const [masse, parMotif] = massesAnticipees(
      pensionnes, simulateur, population, annee, poidsAnnee,
    );
    const lignes = {};
    for (const [cle, valeur] of Object.entries(parts)) {
      if (cle !== CONTRIBUTIF) lignes[cle] = (observee * valeur) / totale;
    }
    const anticipees = {};
    for (const [motif, valeur] of Object.entries(parMotif)) {
      anticipees[motif] = masse > 0 ? (observee * valeur) / masse : 0;
    }
    annees.push({
      annee,
      observee,
      lignes,
      anticipees,
      get gratuit() {
        return Object.values(this.lignes).reduce((a, b) => a + b, 0);
      },
      get anticipee() {
        return Object.values(this.anticipees).reduce((a, b) => a + b, 0);
      },
    });
  }
  const derniere = annees.length > 0 ? annees[annees.length - 1].lignes : {};
  const connues = new Set();
  for (const annee of annees) {
    for (const cle of Object.keys(annee.lignes)) connues.add(cle);
  }
  // Le code départage les ex aequo, comme du côté Python : sans lui, l'ordre
  // de la légende dépendrait de l'ordre d'insertion et les deux rendus
  // divergeraient.
  const lignes = [...connues].sort((a, b) => {
    const ecart = (derniere[b] || 0) - (derniere[a] || 0);
    if (ecart !== 0) return ecart;
    return a < b ? -1 : a > b ? 1 : 0;
  });
  return {
    annees,
    lignes,
    refus,
    ponderation: ponderationChoisie,
    get derniere() {
      return this.annees.length > 0 ? this.annees[this.annees.length - 1] : null;
    },
  };
}
