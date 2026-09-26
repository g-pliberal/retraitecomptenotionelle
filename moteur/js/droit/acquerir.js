/**
 * Acquérir les droits (docs/architecture.md, § 7.2).
 *
 * Jumeau de `src/retraite_notionnelle/droit/acquerir.py`, fonction pour
 * fonction : ce que chaque année verse aux régimes qui la reçoivent — des
 * points, chacun avec le taux de majoration pour enfants de son année
 * d'acquisition, ou des cotisations revalorisées aux prix de l'année de
 * liquidation —, la durée qu'un régime plafonne, et les points attribués
 * sans cotisation à la liquidation. Ce que l'étape écrit, `Droits`, suit son
 * schéma, `data/reference/etapes/acquerir_les_droits.yaml`.
 */

import { DateMois, enMois } from "../calendrier.js";
import { assietteMinimale as assietteMinimaleDe, salaireMoyenAnnuel } from "../carriere.js";
import { nomFiabilite, Fiabilite } from "../serie.js";
import { derniereAnnee } from "./commun.js";
import * as compter from "./compter.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

/**
 * L'assiette minimale que la ligne oppose à l'un de ces régimes : celle du
 * régime de BASE d'un indépendant (D. 633-2, D. 642-4), nulle ailleurs.
 */
export function assietteMinimale(moteur, codes, ligne) {
  if (!(ligne.assiette_minimale_base > 0)) {
    return 0.0;
  }
  const regle = assietteMinimaleDe(moteur.macro.paquet, ligne.affiliation, ligne.annee);
  if (regle === null || !codes.some((c) => regle[1].includes(c))) {
    return 0.0;
  }
  return ligne.assiette_minimale_base;
}

/** Points de retraite proportionnelle agricole d'une année (R. 732-71).
 *
 * Escalier à quatre marches : quinze points jusqu'à 400 SMIC horaires, une
 * pente jusqu'à trente à 800 SMIC, un plateau à trente jusqu'à deux fois le
 * minimum contributif, puis une pente jusqu'au maximum M de l'année, que
 * R. 732-70 définit par (PM − AVTS) / (37,5 × valeur du point).
 */
export function pointsMsa(moteur, periode, annee, revenu) {
  const smic = moteur.macro.smic_horaire.valeur(annee);
  const passAnnuel = moteur.macro.plafond_securite_sociale.valeur(annee);
  const valeurPoint = moteur.valeurPointFiche(periode, annee);
  if (smic <= 0 || passAnnuel <= 0 || valeurPoint <= 0) {
    return 0.0;
  }
  const avts = (periode.pension_forfaitaire_annuelle ?? 0.0)
    * moteur.macro.coefficientPrix(periode.pension_forfaitaire_annee ?? annee, annee);
  const minimumContributif = moteur.minimumContributif.valeurs(annee)[0];
  const maximum = (0.5 * passAnnuel - avts) / (37.5 * valeurPoint);
  if (revenu <= 400 * smic) {
    return 15.0;
  }
  if (revenu <= 800 * smic) {
    return Math.min(30.0, 15.0 + 15.0 * (revenu - 400 * smic) / (400 * smic));
  }
  if (revenu <= 2 * minimumContributif || passAnnuel <= 2 * minimumContributif) {
    return 30.0;
  }
  return Math.min(maximum, 30.0 + (maximum - 30.0)
    * (revenu - 2 * minimumContributif)
    / (passAnnuel - 2 * minimumContributif));
}

/**
 * Points que ce régime attribue sans cotisation à la liquidation, et la
 * fiabilité de la durée requise qui les conditionne : cent points par année
 * de chef d'exploitation d'avant 2003 à la RCO agricole (D. 732-154), dans
 * la limite de 37,5 ans moins les années de RCO, à qui a dix-sept ans et
 * demi comme chef (D. 732-151) et le taux plein de son régime de base
 * (L. 732-56, II, 2°) — la durée requise jusqu'au 31 août 2023, la pension
 * liquidée au taux plein depuis. Voir `points_gratuits` dans le Python.
 */
export function pointsGratuits(moteur, periode, carriere, assurance, trimestres, ageLiquidation) {
  const regle = periode.points_gratuits;
  const base = moteur.catalogue.obtenir(regle.regime);
  const periodeBase = base.periode(
    Math.min(carriere.anneeLiquidation, derniereAnnee(base)));
  if (periodeBase === null) {
    return [0.0, null];
  }
  const valides = (code, avant = null) => {
    let total = 0;
    for (const [annee, nombre] of assurance.get(code) ?? []) {
      if (avant === null || annee < avant) {
        total += Math.min(nombre, carriere.plafondTrimestres(annee));
      }
    }
    return total;
  };
  if (valides(regle.regime) < regle.annees_minimum * 4) {
    return [0.0, null];
  }
  const [requis, fiabilite] = moteur.dureeRequise(periodeBase, carriere);
  let tauxPlein = trimestres >= requis;
  const [anneeDepuis, moisDepuis] = regle.taux_plein_depuis;
  if (!tauxPlein
      && carriere.dateLiquidation.rang >= new DateMois(anneeDepuis, moisDepuis).rang) {
    tauxPlein = ageLiquidation >= moteur.ageTauxPlein(periodeBase, carriere);
  }
  if (!tauxPlein) {
    return [0.0, fiabilite];
  }
  const retenus = Math.min(
    valides(regle.regime, regle.avant),
    Math.max(0.0, regle.annees_maximum * 4 - valides(periode.regime)),
  );
  return [regle.points_par_annee * retenus / 4, fiabilite];
}

/**
 * Ce que l'étape écrit. Son schéma :
 * `data/reference/etapes/acquerir_les_droits.yaml`. Les crédits de points et
 * de cotisations sont la source ; les comptes par régime que la liquidation
 * lit en sont les sommes, faites dans l'ordre des crédits, puis réduites par le
 * plafond de la durée, puis augmentées des points gratuits.
 */
export class Droits {
  constructor({ carriere, points, cotisations, plafonds, gratuits, derniereAnneeParRegime,
    fiabilitePoints, pointsAcquis, majorationPoints, pointsMajores, cumulCotisations }) {
    this.carriere = carriere;
    /** Les points crédités, dans l'ordre : [régime, année, points, taux]. */
    this.points = points;
    /** Les cotisations revalorisées : [régime, année, montant]. */
    this.cotisations = cotisations;
    /** La durée plafonnée : [régime, trimestres, avant l'âge, retenus]. */
    this.plafonds = plafonds;
    /** Les points gratuits : régime -> [points, année avant laquelle]. */
    this.gratuits = gratuits;
    /** La dernière année qui verse à chaque régime. */
    this.derniereAnneeParRegime = derniereAnneeParRegime;
    /** La fiabilité des points de chaque régime qui en crédite. */
    this.fiabilitePoints = fiabilitePoints;
    /** Les comptes que la liquidation lit. */
    this.pointsAcquis = pointsAcquis;
    this.majorationPoints = majorationPoints;
    this.pointsMajores = pointsMajores;
    this.cumulCotisations = cumulCotisations;
  }

  /** Les régimes où un droit est acquis, points ou cotisations. */
  get codes() {
    return [...new Set([...this.cumulCotisations.keys(), ...this.pointsAcquis.keys()])].sort();
  }

  /** Les droits, tels que leur schéma les décrit. */
  donnees() {
    return {
      schema_version: SCHEMA_VERSION,
      personne: this.carriere.personne,
      regimes: [...this.derniereAnneeParRegime].map(([regime, annee]) => ({
        regime, derniere_annee: annee,
        fiabilite: this.fiabilitePoints.has(regime)
          ? nomFiabilite(this.fiabilitePoints.get(regime)) : null,
      })),
      points: this.points.map(([regime, annee, points, taux]) => ({
        regime, annee, points, majoration: taux,
      })),
      cotisations: this.cotisations.map(([regime, annee, montant]) => ({ regime, annee, montant })),
      plafonds: this.plafonds.map(([regime, total, avantAge, retenus]) => ({
        regime, trimestres: total, avant_age: avantAge, retenus,
      })),
      gratuits: [...this.gratuits].map(([regime, [points, avant]]) => ({ regime, points, avant })),
    };
  }
}

/**
 * L'étape : les points et les cotisations de chaque année, puis la durée
 * qu'un régime plafonne, puis les points attribués sans cotisation.
 * `avecPointsGratuits` à faux retire ces derniers. Voir `acquerir` dans le
 * Python.
 */
export function acquerir(moteur, coordination, durees, avecPointsGratuits = true) {
  const carriere = coordination.carriere;
  const anneeLiquidation = carriere.anneeLiquidation;
  const ageLiquidation = carriere.age_liquidation || 0.0;
  // Cotisations des régimes en points dont on n'a pas le prix d'achat du
  // point : [régime, année, montant revalorisé].
  const cotisations = [];
  // La majoration pour enfants des points de l'Agirc-Arrco dépend de leur
  // année d'ACQUISITION : chaque point y entre avec son taux.
  const credits = [];
  const crediter = (code, annee, points) => {
    credits.push([code, annee, points,
      moteur.majorationsEnfantsPoints.taux(code, annee, carriere.nombre_enfants)]);
  };
  const fiabilitePoints = new Map();
  // Trimestres qu'un régime à la durée crédite, et ceux d'entre eux
  // accomplis avant l'âge qui lève son plafond : voir le Python.
  const trimestresPlafonnables = new Map();
  // Dernière année cotisée dans chaque régime : elle désigne, dans une
  // chaîne de succession, la caisse qui liquide.
  const derniereAnneeParRegime = new Map();
  carriere.lignes.forEach((ligne, i) => {
    // Une ligne postérieure à la liquidation décrit une activité exercée
    // APRÈS le départ : elle n'ouvre pas de droits dans la pension qu'on
    // liquide. L'année du départ, elle, ouvre ceux de ses mois qui l'ont
    // précédé — ni zéro ni douze, mais le compte juste.
    const part = carriere.partRetenueLigne(ligne);
    if (part <= 0) {
      return;
    }
    if (!ligne.cotise && ligne.familles_cotisantes.length === 0) {
      return;
    }
    // Pendant une période indemnisée, seuls les régimes complémentaires
    // encaissent, et sur le salaire d'avant l'interruption.
    let baseLigne = ligne.cotise ? ligne.revenu : ligne.revenu_reference;
    if (part < ligne.fraction_annee) {
      baseLigne *= part / ligne.fraction_annee;
    }
    const famillesAdmises = ligne.cotise ? null : new Set(ligne.familles_cotisantes);
    for (const code of coordination.regimes[i]) {
      if (!moteur.catalogue.contient(code)) {
        continue;
      }
      const regime = moteur.catalogue.obtenir(code);
      if (famillesAdmises !== null && !famillesAdmises.has(regime.famille)) {
        continue;
      }
      derniereAnneeParRegime.set(
        code, Math.max(derniereAnneeParRegime.get(code) ?? 0, ligne.annee),
      );
      for (const periode of regime.periodesActives(ligne.annee)) {
        // BARÈME D'UN AUTRE RÉGIME : une tranche que tous les affiliés ne
        // cotisent pas forme une fiche à part, dont les points restent ceux
        // du régime d'origine. Voir `points_de`.
        const bareme = periode.points_de ?? code;
        // Les bornes d'assiette et le repère en points sont ANNUELS : une
        // année incomplète ne les atteint qu'à proportion de ses mois, comme
        // le plafond lui-même.
        const passPlein = moteur.macro.plafond_securite_sociale.valeur(ligne.annee);
        const pass = passPlein * part;
        let [borneBasse, borneHaute] = periode.bornesAssietteEnEuros(passPlein);
        if (part < 1.0) {
          borneBasse *= part;
          borneHaute = borneHaute === null ? null : borneHaute * part;
        }
        // Traitement seul, primes seules — celles du RAFP dans la limite de
        // 20 % du traitement : voir `partDuRevenu`.
        let base = periode.partDuRevenu(baseLigne, ligne.part_primes);
        if (ligne.revenu_retabli > 0 && periode.assiette !== "primes_uniquement") {
          // Une année RÉTABLIE : l'Ircantec valide le traitement de l'année,
          // les primes restent au RAFP.
          base = baseLigne * (1.0 - ligne.part_primes);
        }
        // Commissions de la CAVAMAC, produits de l'office de la CPRN : le
        // facteur reconstitue l'assiette depuis le revenu, avant les bornes.
        if (periode.assiette_facteur_revenu !== null
            && periode.assiette_facteur_revenu !== undefined) {
          base *= periode.assiette_facteur_revenu;
        }
        // Le marin cotise sur le salaire forfaitaire de sa catégorie : voir
        // `ConstructeurCompte.cotisationAnnuelle`.
        if (periode.assiette_grille) {
          const forfaitGrille = moteur.grilles.forfait(
            periode.assiette_grille, ligne.annee, ligne.revenuAnnualise,
            (a) => salaireMoyenAnnuel(moteur.macro, a),
          );
          if (forfaitGrille !== null) {
            base = forfaitGrille[0] * part;
          }
        }
        // L'assiette minimale du régime de base d'un libéral : 450 SMIC
        // horaires depuis 2023 (D. 642-4), qui ouvrent leurs points.
        base = Math.max(base, assietteMinimale(moteur, [code], ligne));
        const plafond = borneHaute === null ? base : borneHaute;
        let assiette = Math.max(0.0, Math.min(base, plafond) - borneBasse);
        const repere = periode.repereAssiette(
          pass, moteur.macro.smic_horaire.valeur(ligne.annee),
        ) * (periode.assiette_repere_smic !== null
          && periode.assiette_repere_smic !== undefined ? part : 1.0);
        if (periode.assiette_forfaitaire) {
          // Assiette FORFAITAIRE : le régime des cultes cotise sur un
          // forfait égal au SMIC mensuel, quel que soit le revenu —
          // inconditionnel, là où assiette_plancher ne relève que les
          // assiettes trop basses.
          assiette = repere;
        } else if (periode.assiette_plancher && assiette < repere) {
          // Assiette minimale : la complémentaire agricole cotise sur
          // 1 820 SMIC même quand le revenu est en dessous.
          assiette = repere;
        }
        if (!periode.assiette_forfaitaire) {
          // Assiette minimale en plafonds : la CARPIMKO appelle depuis 2026
          // sa cotisation sur un demi-plafond au moins, et les points suivent
          // ce qui est appelé. Le plafond est déjà proratisé sur les mois.
          assiette = Math.max(assiette, periode.assietteMinimale(pass));
        }
        // La cotisation forfaitaire s'ajoute à la proportionnelle, et elle est
        // due quel que soit le revenu — même convention que dans compte.js.
        let forfait = 0.0;
        if (periode.cotisation_forfaitaire_euros !== null
            && periode.cotisation_forfaitaire_euros !== undefined) {
          const reference = periode.cotisation_forfaitaire_annee || ligne.annee;
          forfait = periode.cotisation_forfaitaire_euros
            * moteur.macro.coefficientPrix(reference, ligne.annee);
        }
        let cotisation = assiette * periode.taux_cotisation_retraite + forfait;
        // COTISATION PAR CLASSES : la Cipav, avant 2023, appelait le montant
        // du palier où tombait le revenu, et non une fraction d'une assiette.
        // Ce montant achète des points comme n'importe quelle cotisation —
        // « 3 600 € / 47,40 € = 75,9 points », écrit la caisse —, et c'est
        // donc ici, avant la conversion, qu'il se substitue.
        if (periode.cotisation_par_classes) {
          const millesime = moteur.classes.anneeGrille(code, ligne.annee);
          const reference = millesime === null
            ? 0.0
            : moteur.macro.plafond_securite_sociale.valeur(millesime);
          const parClasse = reference <= 0 ? null : moteur.classes.cotisation(
            code, ligne.annee, base,
            moteur.macro.plafond_securite_sociale.valeur(ligne.annee) / reference,
          );
          if (parClasse !== null) {
            cotisation = parClasse[0] * part;
          }
        }
        if (periode.bareme_points === "msa_proportionnelle") {
          // BARÈME NOMMÉ : R. 732-71 écrit l'escalier, `pointsMsa` le sert.
          // C'est l'ASSIETTE qui y entre : la cotisation est due sur six
          // cents SMIC horaires au moins et sur un plafond au plus.
          const [echelleMsa, fiabiliteEchelleMsa] = moteur.conversionsPoints
            .echelle(bareme, ligne.annee, anneeLiquidation);
          crediter(code, ligne.annee,
            pointsMsa(moteur, periode, ligne.annee, assiette) * part * echelleMsa);
          fiabilitePoints.set(code, Math.min(
            fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE, regime.fiabilite,
            fiabiliteEchelleMsa,
          ));
          continue;
        }
        if (periode.points_par_trimestre_valide !== null
            && periode.points_par_trimestre_valide !== undefined) {
          // POINTS PAR TRIMESTRE VALIDÉ, sans égard au montant. Le régime de
          // base des libéraux d'avant 2004 ne servait pas une pension
          // proportionnelle au revenu mais une ALLOCATION : un quinzième de
          // l'AVTS par année cotisée, la même pour tous. La réforme de 2003
          // l'a convertie en points « à raison de cent points par trimestre »
          // (D. 643-1), et c'est cette conversion qui porte le droit
          // d'avant 2004.
          const [echelleTrim, fiabiliteEchelleTrim] = moteur.conversionsPoints
            .echelle(bareme, ligne.annee, anneeLiquidation);
          let points = periode.points_par_trimestre_valide
            * carriere.trimestresRetenus(ligne);
          if (periode.trimestres_maximum !== null
              && periode.trimestres_maximum !== undefined) {
            // Le plafond se lit sur toute la durée : on note ici les
            // trimestres de la ligne, et ceux d'entre eux qui précèdent l'âge
            // qui le lève.
            if (!trimestresPlafonnables.has(code)) {
              trimestresPlafonnables.set(code, [0.0, 0.0]);
            }
            const suivi = trimestresPlafonnables.get(code);
            suivi[0] += carriere.trimestresRetenus(ligne);
            if (periode.trimestres_maximum_leve_avant_age !== null
                && periode.trimestres_maximum_leve_avant_age !== undefined) {
              suivi[1] += compter.trimestresDeLaLigneEntre(
                carriere, ligne, new DateMois(carriere.annee_naissance, 1),
                carriere.dateNaissance.plusMois(
                  enMois(periode.trimestres_maximum_leve_avant_age)),
              );
            }
          }
          if (periode.points_ajustement_par_forfait !== null
              && periode.points_ajustement_par_forfait !== undefined
              && forfait > 0) {
            // Les points d'AJUSTEMENT de l'ASV des médecins : 18 fois la
            // cotisation proportionnelle sur le forfait, neuf au plus
            // (décret n° 2011-1644, art. 3). Ils suivent le revenu, là où
            // les 27 points du forfait ne suivent que la durée.
            let ajustement = periode.points_ajustement_par_forfait * assiette
              * periode.taux_cotisation_retraite / forfait;
            if (periode.points_ajustement_maximum !== null
                && periode.points_ajustement_maximum !== undefined) {
              ajustement = Math.min(ajustement,
                periode.points_ajustement_maximum * part);
            }
            points += ajustement;
          }
          crediter(code, ligne.annee, points * echelleTrim);
          fiabilitePoints.set(code, Math.min(
            fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE, regime.fiabilite,
            fiabiliteEchelleTrim,
          ));
          continue;
        }
        if (periode.points_maximum !== null && periode.points_maximum !== undefined
            && repere > 0) {
          // Barème écrit en POINTS et non en prix d'achat : le régime annonce
          // combien de points ouvre une assiette donnée. Le nombre de points
          // ne dépend alors pas du taux de cotisation, et c'est heureux : ce
          // sont les barèmes qui sont publiés, pas les prix d'achat.
          const [echelleBareme, fiabiliteEchelleBareme] = moteur.conversionsPoints
            .echelle(bareme, ligne.annee, anneeLiquidation);
          crediter(code, ligne.annee,
            periode.points_maximum * assiette / repere * echelleBareme);
          fiabilitePoints.set(code, Math.min(
            fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE, regime.fiabilite,
            fiabiliteEchelleBareme,
          ));
          continue;
        }
        const achat = (periode.type_calcul === "points" || periode.type_calcul === "mixte")
          ? moteur.valeursPoint.achat(bareme, ligne.annee)
          : null;
        if (achat !== null) {
          const [reference, tauxAppel, fiabiliteAchat] = achat;
          let pointsAnnee = cotisation / (tauxAppel * reference);
          if (periode.points_minimum_annuels !== null
              && periode.points_minimum_annuels !== undefined) {
            // Garantie minimale de points de l'Agirc : tout cadre cotisant en
            // acquiert au moins 120 par an de 1989 à 2018, même quand sa
            // tranche B est nulle.
            pointsAnnee = Math.max(pointsAnnee, periode.points_minimum_annuels);
          }
          // Changement d'unité entre l'achat et le service : les points
          // Arrco d'avant 1999 sont ceux de l'UNIRS, et valent 0,387464 point
          // du régime unifié. Sans cette conversion, cent euros cotisés en
          // 1998 produisaient 30,31 € de pension quand les mêmes cent euros
          // de 1999 n'en produisaient que 11,15.
          const [echelle, fiabiliteEchelle] = moteur.conversionsPoints
            .echelle(bareme, ligne.annee, anneeLiquidation);
          crediter(code, ligne.annee, pointsAnnee * echelle);
          fiabilitePoints.set(code, Math.min(
            fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE, fiabiliteAchat,
            fiabiliteEchelle,
          ));
        } else {
          cotisations.push([code, ligne.annee,
            cotisation * moteur.macro.coefficientPrix(ligne.annee, anneeLiquidation)]);
        }
      }
    }
  });

  const pointsAcquis = new Map();
  const majorationPoints = new Map();
  const pointsMajores = new Map();
  for (const [code, , points, taux] of credits) {
    pointsAcquis.set(code, (pointsAcquis.get(code) ?? 0.0) + points);
    if (taux !== null) {
      majorationPoints.set(code, (majorationPoints.get(code) ?? 0.0) + points * taux);
      pointsMajores.set(code, (pointsMajores.get(code) ?? 0.0) + points);
    }
  }
  const cumulCotisations = new Map();
  for (const [code, , montant] of cotisations) {
    cumulCotisations.set(code, (cumulCotisations.get(code) ?? 0.0) + montant);
  }

  const plafonds = [];
  // LE PLAFOND DE LA DURÉE, LEVÉ AVANT UN ÂGE : cent vingt trimestres au plus
  // aux mines, sauf ceux accomplis avant cinquante-cinq ans (article 136 du
  // décret n° 46-2769). Voir le Python.
  for (const [code, [total, avantAge]] of trimestresPlafonnables) {
    const regime = moteur.catalogue.obtenir(code);
    const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
    if (periode === null || periode.trimestres_maximum === null
        || periode.trimestres_maximum === undefined || total <= 0) {
      continue;
    }
    const retenus = Math.min(total, Math.max(periode.trimestres_maximum, avantAge));
    plafonds.push([code, total, avantAge, retenus]);
    if (retenus < total && pointsAcquis.has(code)) {
      const rapport = retenus / total;
      pointsAcquis.set(code, pointsAcquis.get(code) * rapport);
      if (majorationPoints.has(code)) {
        majorationPoints.set(code, majorationPoints.get(code) * rapport);
        pointsMajores.set(code, pointsMajores.get(code) * rapport);
      }
    }
  }

  // POINTS GRATUITS : la RCO agricole attribue à la liquidation des points
  // pour les années de chef d'exploitation d'avant sa création. Ils entrent au
  // compte de points du régime comme des points acquis, et la cascade les
  // isole plus bas. Voir `pointsGratuits`.
  // Points attribués, et année avant laquelle comptent les années.
  const gratuitsAttribues = new Map();
  if (avecPointsGratuits) {
    for (const [base, attribuants] of moteur.pointsGratuitsParBase) {
      if (!durees.parAnnee.assurance.has(base)) {
        continue;
      }
      for (const code of attribuants) {
        const regime = moteur.catalogue.obtenir(code);
        const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
        if (periode === null || periode.points_gratuits === null
            || periode.points_gratuits === undefined) {
          continue;
        }
        const [gratuits, fiabiliteDuree] = pointsGratuits(
          moteur, periode, carriere, durees.parAnnee.assurance, durees.trimestres,
          ageLiquidation,
        );
        if (gratuits <= 0) {
          continue;
        }
        gratuitsAttribues.set(code, [gratuits, periode.points_gratuits.avant]);
        pointsAcquis.set(code, (pointsAcquis.get(code) ?? 0.0) + gratuits);
        fiabilitePoints.set(code, Math.min(
          fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE,
          regime.fiabilite,
          fiabiliteDuree === null ? Fiabilite.CERTIFIEE : fiabiliteDuree,
        ));
      }
    }
  }
  return new Droits({
    carriere, points: credits, cotisations, plafonds, gratuits: gratuitsAttribues,
    derniereAnneeParRegime, fiabilitePoints, pointsAcquis, majorationPoints, pointsMajores,
    cumulCotisations,
  });
}
