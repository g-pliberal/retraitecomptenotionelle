/**
 * Le pilier de capitalisation : accumulation, rente, transmission.
 *
 * Portage de ``src/retraite_notionnelle/moteur/capitalisation.py``, dont il
 * reproduit les conventions au centime — les témoins de `tests/temoins/` le
 * vérifient.
 *
 * Ce compartiment n'est PAS un compte notionnel. Le compte notionnel est
 * virtuel : rien n'y est placé, la revalorisation est une règle collective, et
 * ce que l'assuré n'a pas consommé à sa mort revient à la collectivité. Ici un
 * capital existe vraiment : il est placé, il rapporte un taux de marché, il
 * supporte des frais, et il SE TRANSMET si l'assuré meurt avant d'avoir
 * liquidé. Les deux sont donc tenus séparément et ne s'additionnent que sur la
 * ligne « total ».
 *
 * DEUX COTISATIONS L'ALIMENTENT, et une seule est imposée. 5 % obligatoires que
 * la proposition ajoute aux 18 % de répartition, et 5 % VOLONTAIRES : les points
 * qu'elle rend, remis au même compte pour que l'effort retombe sur les quelque
 * 28 % d'aujourd'hui et que les deux systèmes se comparent à prix égal. Le
 * pilier ne les distingue qu'en proportion — même assiette, même placement,
 * mêmes frais, même rente —, parce que tout ce qu'il produit est exactement
 * proportionnel au taux. Ce qui les sépare est sur la fiche de paie, où
 * l'obligatoire est partagée avec l'employeur et la volontaire pas.
 *
 * CONVENTION DE DATE, ET POURQUOI C'EST CELLE DU COMPTE NOTIONNEL. Le versement
 * d'une année est crédité à la FIN de cette année : il rapporte de l'année
 * suivante jusqu'à l'année de liquidation incluse, soit exactement les années
 * où le compte notionnel le revaloriserait. Sans cette symétrie, l'écart entre
 * les deux compartiments contiendrait une année de rendement offerte à l'un
 * des deux.
 */

import {
  TableConversion,
  tauxCapitalisationApplique,
  tauxCapitalisationVolontaireApplique,
} from "./config.js";
import { Fiabilite } from "./serie.js";

/** Les trois maturités de l'échelle : courte, moyenne, longue. */
export const MATURITES = Object.freeze([2, 10, 30]);

export const HORIZON_LONG = 30;
export const HORIZON_PIVOT = 10;
export const HORIZON_COURT = 2;

/**
 * Part maximale d'une seule maturité — 3/4, et non 1 : une épargne obligatoire
 * ne se concentre pas sur un seul point de la courbe. En début de carrière
 * l'allocation est PRINCIPALEMENT longue, jamais exclusivement ; à l'approche
 * du départ elle est principalement courte, et de toute façon plafonnée par la
 * date de départ, qui ramène toutes les maturités à l'horizon restant.
 */
export const PART_MAXIMALE = 0.75;

/**
 * Fiabilité du barème de frais : saisi depuis le rapport de l'Observatoire des
 * produits d'épargne financière, non confronté automatiquement au document du
 * producteur, donc plafonné à `haute` comme toute transcription.
 */
export const FIABILITE_FRAIS = Fiabilite.HAUTE;

function borner(valeur) {
  return Math.min(1.0, Math.max(0.0, valeur));
}

/**
 * Maturités et poids d'un versement placé à `horizon` années du départ.
 *
 * La part longue croît avec l'horizon, la part courte décroît, et aucune
 * maturité ne dépasse l'horizon — un titre qui arriverait à échéance après le
 * départ devrait être vendu avant terme, donc à un prix qui n'est plus sans
 * risque. Les poids sont rendus par maturité EFFECTIVE, donc fusionnés quand le
 * plafonnement fait coïncider deux maturités.
 */
export function repartition(horizon) {
  if (horizon <= 0) return [];
  const partLongue = PART_MAXIMALE * borner(
    (horizon - HORIZON_PIVOT) / (HORIZON_LONG - HORIZON_PIVOT),
  );
  const partCourte = PART_MAXIMALE * borner(
    (HORIZON_PIVOT - horizon) / (HORIZON_PIVOT - HORIZON_COURT),
  );
  const poids = [partCourte, 1.0 - partCourte - partLongue, partLongue];

  const cumul = new Map();
  MATURITES.forEach((maturite, indice) => {
    const part = poids[indice];
    if (part <= 0) return;
    const effective = Math.min(maturite, horizon);
    cumul.set(effective, (cumul.get(effective) || 0.0) + part);
  });
  return [...cumul.entries()].sort((a, b) => a[0] - b[0]);
}

/**
 * Taux constant qui mène des versements au capital, par dichotomie.
 *
 * La fonction est strictement croissante en le taux dès qu'un versement est
 * positif : la dichotomie converge, et sans dérivée. Les bornes sont larges —
 * un pilier ouvert un an avant le départ peut afficher un rendement négatif du
 * seul fait des frais.
 */
export function tauxInterne(versements, anneeFinale, capital, tolerance = 1e-10) {
  if (versements.length === 0 || capital <= 0) return 0.0;
  const valeur = (taux) => versements.reduce(
    (somme, [annee, montant]) => somme + montant * (1.0 + taux) ** (anneeFinale - annee),
    0.0,
  ) - capital;

  let bas = -0.99;
  let haut = 1.0;
  // Un seul cas produit une équation sans solution : tous les versements
  // tombent l'année de la liquidation, où ils ne rapportent rien et où les
  // frais les amputent. Zéro est rendu plutôt qu'un NaN, qui ne s'écrit pas en
  // JSON et qui n'est égal à rien, pas même à lui-même.
  if (valeur(bas) > 0 || valeur(haut) < 0) return 0.0;
  for (let i = 0; i < 200; i += 1) {
    const milieu = 0.5 * (bas + haut);
    if (valeur(milieu) < 0) bas = milieu; else haut = milieu;
    if (haut - bas < tolerance) break;
  }
  return 0.5 * (bas + haut);
}

/** Construit le pilier capitalisé d'une carrière. */
export class ConstructeurCapitalisation {
  constructor(courbe, mortalite, convertisseur, parametres) {
    this.courbe = courbe;
    this.mortalite = mortalite;
    // Le convertisseur reçu est celui du TAUX TECHNIQUE de la rente, dérivé
    // par le simulateur ; au réglage par défaut — taux technique nul — il
    // coïncide avec celui de la pension notionnelle, et c'est voulu.
    this.convertisseur = convertisseur;
    this.parametres = parametres;
  }

  /**
   * Place `montant`, disponible à la fin de `annee`, sur l'échelle. Rend la
   * répartition en euros, par maturité. Un montant disponible l'année même de
   * la liquidation ne se place plus : il n'a plus d'années devant lui, et le
   * compte notionnel ne revalorise pas davantage sa dernière cotisation.
   */
  placer(montant, annee, anneeLiquidation, lignes) {
    const horizon = anneeLiquidation - annee;
    if (montant <= 0) return [];
    if (horizon <= 0) {
      lignes.push({ montant, anneeFin: annee, taux: 0.0 });
      return [];
    }
    const detail = [];
    for (const [maturite, poids] of repartition(horizon)) {
      const part = montant * poids;
      if (part <= 0) continue;
      const taux = this.courbe.placement(annee, maturite);
      lignes.push({ montant: part, anneeFin: annee + maturite, taux: taux.taux });
      detail.push([maturite, part]);
    }
    return detail;
  }

  _fiabilitePlacements(anneeOuverture, anneeLiquidation) {
    let niveau = Fiabilite.CERTIFIEE;
    for (let annee = anneeOuverture; annee < anneeLiquidation; annee += 1) {
      for (const [maturite] of repartition(anneeLiquidation - annee)) {
        niveau = Math.min(niveau, this.courbe.placement(annee, maturite).fiabilite);
      }
    }
    return niveau;
  }

  _accumuler(assiettes, anneeOuverture, anneeLiquidation, anneeNaissance, avecFrais) {
    const fraisVersement = avecFrais
      ? this.parametres.frais_versement_capitalisation : 0.0;
    const fraisGestion = avecFrais
      ? this.parametres.frais_gestion_capitalisation : 0.0;
    const tauxCotisation = tauxCapitalisationApplique(this.parametres);

    let lignes = [];
    const annees = [];

    for (let annee = anneeOuverture; annee <= anneeLiquidation; annee += 1) {
      const ouverture = lignes.reduce((somme, l) => somme + l.montant, 0.0);

      // 1. Intérêts de l'année, ligne par ligne, au taux bloqué le jour du
      //    placement : le taux d'une ligne portée jusqu'à l'échéance ne change
      //    plus.
      const interets = lignes.reduce((somme, l) => somme + l.montant * l.taux, 0.0);
      for (const ligne of lignes) ligne.montant *= 1.0 + ligne.taux;

      // 2. Frais de gestion sur l'encours de fin d'année, au prorata de chaque
      //    ligne. Le versement de l'année n'y est pas encore : il n'a pas passé
      //    l'année dans l'enveloppe.
      const prelevement = (ouverture + interets) * fraisGestion;
      if (prelevement) {
        for (const ligne of lignes) ligne.montant *= 1.0 - fraisGestion;
      }

      // 3. Échéances : ce qui arrive à terme est replacé pour ce qu'il reste
      //    d'horizon.
      const echues = lignes
        .filter((l) => l.anneeFin === annee)
        .reduce((somme, l) => somme + l.montant, 0.0);
      lignes = lignes.filter((l) => l.anneeFin !== annee);
      if (echues) this.placer(echues, annee, anneeLiquidation, lignes);

      // 4. Versement de l'année, crédité en fin d'année.
      const assiette = assiettes.get(annee) || 0.0;
      const brut = assiette * tauxCotisation;
      const frais = brut * fraisVersement;
      const net = brut - frais;
      const placements = this.placer(net, annee, anneeLiquidation, lignes);

      const encours = lignes.reduce((somme, l) => somme + l.montant, 0.0);
      annees.push({
        annee,
        age: annee - anneeNaissance,
        horizon: anneeLiquidation - annee,
        assiette,
        versement_brut: brut,
        frais_versement: frais,
        versement_net: net,
        encours_ouverture: ouverture,
        interets,
        frais_gestion: prelevement,
        encours,
        capital_transmissible: encours,
        taux_moyen: ouverture > 0 ? interets / ouverture : 0.0,
        placements,
      });
    }
    return annees;
  }

  /**
   * Probabilité de mourir avant le départ, et espérance du capital transmis.
   *
   * Vues de l'OUVERTURE du pilier : ce qui est en jeu est le capital de ce
   * compte-là, qui n'existe pas avant. Chaque année de décès possible pèse
   * l'encours MOYEN de l'année, parce qu'un décès ne choisit pas son mois.
   * L'année de la liquidation n'est pas comptée : le modèle calcule une pension
   * pour un assuré qui atteint son départ, et la compter ferait servir la rente
   * et transmettre le capital à la fois.
   */
  _transmission(annees, ageOuverture, anneeOuverture, sexe, population = null) {
    const courbe = this.mortalite.courbe(
      ageOuverture, anneeOuverture, sexe, this.parametres.table_generation,
      population,
    );
    let esperance = 0.0;
    let deces = 0.0;
    for (let indice = 0; indice < annees.length - 1; indice += 1) {
      if (indice + 1 >= courbe.length) break;
      const probabilite = courbe[indice] - courbe[indice + 1];
      const moyen = 0.5 * (annees[indice].encours_ouverture + annees[indice].encours);
      esperance += probabilite * moyen;
      deces += probabilite;
    }
    return [deces, esperance];
  }

  /**
   * Le pilier d'une carrière, de son ouverture à sa rente. `assiettes` porte,
   * année par année, l'assiette sur laquelle la cotisation notionnelle a été
   * prélevée : le pilier s'appuie sur elle et n'en construit pas une autre.
   */
  construire({
    assiettes, anneeNaissance, ageLiquidation, anneeLiquidation,
    moisLiquidation = 1, sexe = null, population = null,
  }) {
    const debutPossible = assiettes.size > 0
      ? Math.min(...assiettes.keys()) : this.parametres.annee_debut_capitalisation;
    const ouverture = Math.max(
      this.parametres.annee_debut_capitalisation, debutPossible,
    );
    const sexeTable = this.parametres.table_conversion === TableConversion.UNISEXE
      ? null : sexe;
    const conversion = this.convertisseur.coefficient(
      ageLiquidation, anneeLiquidation, sexeTable, moisLiquidation, population,
    );
    const fraisArrerages = this.parametres.frais_arrerages_capitalisation;

    // Le pilier s'éteint quand il n'a plus rien à encaisser : ni les cinq
    // points obligatoires, ni les cinq points volontaires. Retirer l'un laisse
    // l'autre debout.
    if (anneeLiquidation < ouverture
        || tauxCapitalisationApplique(this.parametres) <= 0) {
      return resultatCapitalisation({
        annee_ouverture: ouverture,
        annee_liquidation: anneeLiquidation,
        taux_cotisation: tauxCapitalisationApplique(this.parametres),
        taux_cotisation_volontaire:
          tauxCapitalisationVolontaireApplique(this.parametres),
        annees: [],
        capital: 0.0,
        capital_hors_frais: 0.0,
        conversion,
        frais_arrerages: fraisArrerages,
        rente_annuelle: 0.0,
        probabilite_deces_avant_liquidation: 0.0,
        esperance_capital_transmis: 0.0,
        date_courbe: this.courbe.date,
        fiabilite: conversion.fiabilite,
      });
    }

    const annees = this._accumuler(
      assiettes, ouverture, anneeLiquidation, anneeNaissance, true,
    );
    const sansFrais = this._accumuler(
      assiettes, ouverture, anneeLiquidation, anneeNaissance, false,
    );
    const capital = annees.length ? annees[annees.length - 1].encours : 0.0;

    // La rente du PER : capital divisé par le diviseur actuariel, puis amputé
    // des frais sur arrérages, prélevés sur chaque versement de rente et non
    // sur le capital qui la constitue.
    const rente = (capital / conversion.diviseur) * (1.0 - fraisArrerages);

    const [deces, transmis] = this._transmission(
      annees, ouverture - anneeNaissance, ouverture, sexeTable, population,
    );

    return resultatCapitalisation({
      annee_ouverture: ouverture,
      annee_liquidation: anneeLiquidation,
      taux_cotisation: tauxCapitalisationApplique(this.parametres),
      taux_cotisation_volontaire:
        tauxCapitalisationVolontaireApplique(this.parametres),
      annees,
      capital,
      capital_hors_frais: sansFrais.length
        ? sansFrais[sansFrais.length - 1].encours : 0.0,
      conversion,
      frais_arrerages: fraisArrerages,
      rente_annuelle: rente,
      probabilite_deces_avant_liquidation: deces,
      esperance_capital_transmis: transmis,
      //: Date de la courbe employée : la page qui affiche un capital doit
      //: pouvoir dire de quel jour sont les taux qui l'ont produit.
      date_courbe: this.courbe.date,
      fiabilite: Math.min(
        conversion.fiabilite,
        this._fiabilitePlacements(ouverture, anneeLiquidation),
        FIABILITE_FRAIS,
      ),
    });
  }
}

/** Le pilier capitalisé d'une carrière : ce qu'il accumule, sert et transmet. */
function resultatCapitalisation(champs) {
  const somme = (cle) => champs.annees.reduce((total, a) => total + a[cle], 0.0);
  const versements = somme("versement_brut");
  const fraisVersement = somme("frais_versement");
  const fraisGestion = somme("frais_gestion");
  // Le pilier est exactement proportionnel à son taux : aucun seuil, aucun
  // frais forfaitaire. Cette seule fraction partage donc le capital, la rente
  // et le capital transmis entre les deux cotisations, sans les recalculer.
  const tauxVolontaire = champs.taux_cotisation_volontaire || 0.0;
  const partVolontaire = champs.taux_cotisation > 0
    ? tauxVolontaire / champs.taux_cotisation : 0.0;
  return {
    ...champs,
    taux_cotisation_volontaire: tauxVolontaire,
    taux_cotisation_obligatoire: champs.taux_cotisation - tauxVolontaire,
    part_volontaire: partVolontaire,
    capital_volontaire: champs.capital * partVolontaire,
    capital_obligatoire: champs.capital - champs.capital * partVolontaire,
    rente_volontaire: champs.rente_annuelle * partVolontaire,
    rente_volontaire_mensuelle: (champs.rente_annuelle * partVolontaire) / 12.0,
    rente_obligatoire:
      champs.rente_annuelle - champs.rente_annuelle * partVolontaire,
    actif: champs.capital > 0,
    rente_mensuelle: champs.rente_annuelle / 12.0,
    versements,
    frais_versement: fraisVersement,
    frais_gestion: fraisGestion,
    interets: somme("interets"),
    //: Frais effectivement prélevés : ceux sur arrérages n'y sont pas, ils
    //: seront prélevés sur la rente, année après année.
    frais_preleves: fraisVersement + fraisGestion,
    //: Ce que les frais retirent au capital, intérêts perdus compris.
    cout_des_frais: champs.capital_hors_frais - champs.capital,
    annees_cotisees: champs.annees.filter((a) => a.versement_brut > 0).length,
    rendement_cumule: versements ? champs.capital / versements : 0.0,
    //: Taux constant qui, appliqué aux versements bruts aux mêmes dates,
    //: donnerait le même capital. Il se lit contre les taux de la courbe :
    //: l'écart est le prix de l'enveloppe.
    taux_rendement_annuel: tauxInterne(
      champs.annees.filter((a) => a.versement_brut > 0)
        .map((a) => [a.annee, a.versement_brut]),
      champs.annee_liquidation, champs.capital,
    ),
  };
}
