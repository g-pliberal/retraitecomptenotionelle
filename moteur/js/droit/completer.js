/**
 * Compléter tous régimes (docs/architecture.md, § 7.3).
 *
 * Jumeau de `src/retraite_notionnelle/droit/completer.py`, fonction pour
 * fonction : ce que le droit ajoute aux pensions de régime en les regardant
 * toutes ensemble, dans l'ordre où il l'applique — le minimum contributif et
 * son écrêtement (`complementMinimum`), le minimum garanti de la fonction
 * publique, la surcote parentale, la majoration pour enfants enfin, plafonnée
 * en euros à la complémentaire (`plafondMajoration`). L'ASPA n'en est pas :
 * c'est l'étape « foyer et net » (`foyer.js`). Ce que l'étape écrit,
 * `Complements`, suit son schéma, `data/reference/etapes/completer_tous_regimes.yaml`.
 */

import { DateMois } from "../calendrier.js";
import { formatFixe, formatPourcentage } from "../format.js";
import { Fiabilite, nomFiabilite } from "../serie.js";
import { dateDEffet, derniereAnnee } from "./commun.js";
import { trimestresDeLaLigneEntre } from "./compter.js";
import * as etranger from "./etranger.js";
import * as liquider from "./liquider.js";
import * as ouvrir from "./ouvrir.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

/** La fiche de la carte que chaque dispositif applique. */
export const FICHES = {
  minimum_contributif: "minimum_contributif",
  minimum_garanti: "minimum_garanti",
  surcote_parentale: "surcote_parentale",
  majoration_enfants: "majoration_dix_pour_cent",
};

/**
 * Durée cotisée, tous régimes, qui ouvre la majoration du minimum contributif
 * au titre des périodes cotisées (article L. 351-10). En deçà, seul le montant
 * de base est dû.
 */
const TRIMESTRES_COTISES_MINIMUM_MAJORE = 120;

/**
 * Première date d'effet, [année, mois], où la surcote s'AJOUTE au minimum
 * contributif au lieu d'entrer dans la pension qu'on lui compare : décret
 * n° 2008-1509, dernier alinéa de D. 351-2-1.
 */
const SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS = [2009, 4];

/**
 * Le minimum d'une pension proratisée se proratise-t-il sur la durée totale non
 * limitée (fiche `minimum_contributif_international`, depuis 2004) ? Voir
 * `_minimum_international` du Python.
 */
function minimumInternational(moteur, carriere) {
  const version = moteur.carrieresHorsDeFrance.version(
    "minimum", { "liquidation.date_effet": dateDEffet(carriere) });
  return version !== null
    && version.parametres.prorata_du_minimum === "duree_totale_non_limitee";
}

/**
 * Le minimum d'une pension proratisée et sa majoration, théoriques puis
 * proratisés. Voir `plancher_international` du Python.
 */
export function plancherInternational(eligible, montantBase, montantMajore, dureeTotale,
  cotiseeTotale, majorationOuverte) {
  const maximum = eligible.proratisation;
  const dureeRegime = Math.min(eligible.dureeRegime, maximum);
  const theorique = montantBase * Math.min(1.0, dureeTotale / maximum);
  let plancher = theorique * dureeRegime / dureeTotale;
  if (majorationOuverte) {
    const majoration = montantMajore - montantBase;
    if (dureeTotale > eligible.requis) {
      plancher += majoration * Math.min(1.0, cotiseeTotale / maximum)
        * dureeRegime / dureeTotale;
    } else if (cotiseeTotale < maximum) {
      plancher += majoration * cotiseeTotale / maximum
        * dureeRegime / Math.min(dureeTotale, maximum);
    } else {
      plancher += majoration * Math.min(eligible.cotiseeRegime, maximum) / maximum;
    }
  }
  return plancher;
}

/** Ce que l'étape « compléter tous régimes » écrit. */
export class Complements {
  constructor({ personne, regimes, avantages, total, minimumApplique, fiabilite,
    plancher = 0.0, minimumEcrete = null }) {
    this.personne = personne;
    this.regimes = regimes;
    this.avantages = avantages;
    this.total = total;
    this.minimumApplique = minimumApplique;
    this.fiabilite = fiabilite;
    // Ce que la pension provisoire d'une retraite progressive ajoute à la
    // pension complète qui descendrait sous elle : un droit acquis, qui entre
    // au total contributif.
    this.plancher = plancher;
    // Le minimum contributif servi, et ce que sa révision relit après le
    // départ (R. 173-8) : `{avant_ecretement, marge, par_regime}`, en euros de
    // la liquidation ; `null` sans lui. Voir `MinimumEcrete` du Python.
    this.minimumEcrete = minimumEcrete;
  }

  /** Les compléments, tels que le schéma de l'étape les décrit. */
  donnees() {
    return {
      schema_version: SCHEMA_VERSION,
      personne: this.personne,
      dispositifs: this.avantages.map((a) => ({
        code: a.code, fiche: FICHES[a.code], montant: a.montant,
        parts: (a.par_regime ?? []).map(([regime, montant]) => ({ regime, montant })),
      })),
      fiabilite: nomFiabilite(this.fiabilite),
    };
  }
}

/**
 * Les pensions de `liquidees`, complétées de ce que le droit y ajoute. Le
 * contexte dit ce que le calcul neutralise : les avantages non contributifs,
 * la décote et la surcote. `servies` est ce que valent, par an, à la date
 * d'effet, les pensions que des départs précédents servent déjà
 * (`departs.js`) : l'écrêtement du minimum contributif les compte.
 * `initiales` sont, après une retraite progressive, les pensions provisoires
 * de ses régimes de base menées à la date d'effet (`progressive.js`) : la
 * pension complète ne descend pas sous elles, et les vaut quand `recalcul` est
 * faux. `nationales` sont les pensions nationales de qui a des périodes qu'un
 * accord compare : la pension proratisée de chaque régime porté au minimum
 * contributif se compare à elle, chacune à son minimum, et la plus élevée est
 * servie. Voir le Python.
 */
export function completer(moteur, releve, ouverture, liquidees, contexte = null,
  servies = 0.0, initiales = [], recalcul = true, nationales = null) {
  const carriere = releve.carriere;
  const { durees, droits } = releve;
  const anneeLiquidation = carriere.anneeLiquidation;
  const avantagesNonContributifs = contexte === null
    || !contexte.neutralise("avantages_non_contributifs");
  const ignorerPenaliteAge = contexte !== null && contexte.neutralise("decote_surcote");
  const trimestresCotises = ouverture.trimestresCotises;
  const majorationEnfants = durees.enfants;
  const pointsAcquis = droits.pointsAcquis;
  const majorationPoints = droits.majorationPoints;
  const pointsMajores = droits.pointsMajores;
  const pensions = [...liquidees.regimes];
  const eligiblesMinimum = liquidees.minimum;
  const eligiblesGaranti = liquidees.garanti;
  let total = pensions.reduce((somme, p) => somme + p.montant, 0.0);
  const avantages = [];
  let fiabiliteGlobale = Fiabilite.CERTIFIEE;
  let minimumApplique = false;
  let minimumEcrete = null;

  if (avantagesNonContributifs && eligiblesMinimum.length > 0) {
    // Le minimum contributif ne relève que les pensions liquidées AU TAUX
    // PLEIN (L. 351-10). Sa majoration au titre des périodes cotisées demande
    // en outre 120 trimestres cotisés tous régimes ; elle se proratise
    // ensuite sur la durée cotisée DANS le régime, quand le montant de base
    // se proratise sur sa durée d'assurance (D. 351-2-2).
    const [montantBase, montantMajore, plafond, fiabiliteMinimum] = moteur
      .minimumContributif.valeurs(anneeLiquidation);
    const majorationOuverte = trimestresCotises >= TRIMESTRES_COTISES_MINIMUM_MAJORE;
    const dateEffet = [anneeLiquidation, carriere.moisLiquidation];
    // Le minimum se compare à la pension AVANT surcote, et la surcote,
    // calculée sur cette pension nue, s'ajoute au minimum (D. 351-2-1) : voir
    // `complementMinimum`, qui porte aussi la règle d'avant 2009.
    const complementDu = (pension, eligible, plancher) => (!eligible.tauxPlein ? 0.0
      : complementMinimum(pension.montant / eligible.surcote, plancher, eligible.surcote,
        dateEffet));
    const plancherNational = (eligible, majoration) => {
      let plancher = montantBase * Math.min(1.0, eligible.prorataAssurance);
      if (majoration) {
        plancher += (montantMajore - montantBase)
          * Math.min(1.0, eligible.prorataCotise);
      }
      return plancher;
    };
    // LA PENSION PRORATISÉE ET LA PENSION NATIONALE : quand un accord les
    // compare, chacune est portée à SON minimum, puis la plus élevée est
    // servie — la proratisée à égalité.
    const alternatives = new Map();
    for (const eligible of nationales === null ? [] : nationales.minimum) {
      const nationale = nationales.regimes[eligible.indice];
      alternatives.set(nationale.regime, [nationale, eligible]);
    }
    const international = nationales === null ? null : minimumInternational(moteur, carriere);
    let cotisesFrancais = 0;
    let dureeTotale = 0;
    if (nationales !== null) {
      // La pension nationale ne compte que les trimestres cotisés en France
      // pour la majoration.
      cotisesFrancais = carriere.trimestresCumules(carriere.lignes.filter(
        (ligne) => ligne.cotise && ligne.annee <= anneeLiquidation));
      dureeTotale = durees.pourLeTaux(etranger.GENERALE);
    }
    const complements = new Map();
    // Le minimum servi compte-t-il la majoration des périodes cotisées ?
    let majore = false;
    for (const eligible of eligiblesMinimum) {
      const pension = pensions[eligible.indice];
      const alternative = alternatives.get(pension.regime);
      let complement;
      let avecMajoration = majorationOuverte;
      if (alternative === undefined) {
        complement = complementDu(pension, eligible,
          plancherNational(eligible, majorationOuverte));
      } else {
        const plancher = international
          ? plancherInternational(eligible, montantBase, montantMajore, dureeTotale,
            trimestresCotises, majorationOuverte)
          : plancherNational(eligible, majorationOuverte);
        complement = complementDu(pension, eligible, plancher);
        const [nationale, eligibleNational] = alternative;
        const majoreeNationale = cotisesFrancais >= TRIMESTRES_COTISES_MINIMUM_MAJORE;
        const complementNational = complementDu(nationale, eligibleNational,
          plancherNational(eligibleNational, majoreeNationale));
        const proratisee = pension.montant + complement;
        if (nationale.montant + complementNational > proratisee) {
          pensions[eligible.indice] = {
            ...nationale,
            detail: "pension nationale, plus élevée que la pension proratisée "
              + `(${formatFixe(proratisee, 2, true)} €) : ${nationale.detail}`,
          };
          complement = complementNational;
          avecMajoration = majoreeNationale;
        } else {
          pensions[eligible.indice] = {
            ...pension,
            detail: "pension proratisée, au moins égale à la pension nationale "
              + `(${formatFixe(nationale.montant + complementNational, 2, true)} €) : `
              + pension.detail,
          };
        }
      }
      if (complement > 0) {
        complements.set(eligible.indice, complement);
        majore = majore || avecMajoration;
      }
    }
    total = pensions.reduce((somme, p) => somme + p.montant, 0.0);
    let releveMinimum = [...complements.values()].reduce((a, b) => a + b, 0.0);
    if (releveMinimum > 0) {
      // Écrêtement de l'article L. 173-2 : le complément est rogné de ce qui
      // dépasse le plafond, tous régimes confondus, et jamais au-delà. La
      // comparaison porte sur les pensions PERSONNELLES, majorations pour
      // enfants exclues — raison de plus pour les calculer après —, celles que
      // d'autres départs servent déjà comprises, au montant du mois de la date
      // d'effet (R. 173-7).
      // Depuis 2012, les pensions étrangères aussi, hors celles des règlements
      // européens et de six conventions.
      const etrangeres = etranger.pensionsALEcretement(moteur, carriere);
      const marge = plafond - total - servies - etrangeres;
      const admissible = Math.max(0.0, Math.min(releveMinimum, marge));
      if (admissible < releveMinimum) {
        const facteur = admissible / releveMinimum;
        for (const [indice, complement] of complements) {
          complements.set(indice, complement * facteur);
        }
      }
      minimumEcrete = {
        avant_ecretement: releveMinimum,
        marge,
        par_regime: [...complements].map(([indice, complement]) => [
          pensions[indice].regime, complement]),
      };
      releveMinimum = admissible;
    }
    if (releveMinimum > 0) {
      for (const [indice, complement] of complements) {
        // Le complément est DIT, pas seulement annoncé : sans lui, refaire la
        // formule donnait la pension d'avant le minimum et l'écart restait
        // inexpliqué — deux mille euros par an sur une petite retraite, ce
        // qui n'est pas un détail.
        pensions[indice] = {
          ...pensions[indice],
          montant: pensions[indice].montant + complement,
          detail: `${pensions[indice].detail} = `
            + `${formatFixe(pensions[indice].montant, 2, true)} €, porté au `
            + `minimum contributif par + ${formatFixe(complement, 2, true)} €`,
        };
      }
      total += releveMinimum;
      minimumApplique = true;
      fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteMinimum);
      avantages.push({
        code: "minimum_contributif",
        libelle: "Minimum contributif",
        montant: releveMinimum,
        detail: "porté au plancher, au prorata de la durée acquise"
          + (majore ? ", majoration des périodes cotisées comprise" : ""),
      });
    }
  }

  if (avantagesNonContributifs && eligiblesGaranti.length > 0) {
    // Le minimum garanti n'est pas un minimum proratisé mais un BARÈME sur la
    // durée de services : quinze ans en ouvrent 57,5 % de la référence,
    // trente ans 95 %, quarante ans la totalité. Il ne s'ajoute pas à la
    // pension, il s'y substitue quand il lui est supérieur.
    let releveGaranti = 0.0;
    for (const eligible of eligiblesGaranti) {
      if (!eligible.ouvert) {
        continue;
      }
      const plancher = moteur.minimumGaranti.montant(
        anneeLiquidation, eligible.trimestresServices, eligible.dureeMaximum,
      );
      if (plancher === null) {
        continue;
      }
      const pension = pensions[eligible.indice];
      if (pension.montant > 0 && pension.montant < plancher[0]) {
        // Le complément était calculé en ligne et jamais nommé, alors que la
        // phrase juste dessous le cite : `complement` n'existait pas dans
        // cette portée — seulement dans la boucle du minimum contributif, au
        // -dessus — et toute carrière passant ici faisait tomber le moteur
        // JavaScript sur « complement is not defined » quand le Python, lui,
        // rendait sa pension. Le Python nomme la variable ; le portage ne le
        // faisait pas.
        const complement = plancher[0] - pension.montant;
        releveGaranti += complement;
        fiabiliteGlobale = Math.min(fiabiliteGlobale, plancher[1]);
        pensions[eligible.indice] = {
          ...pension,
          montant: plancher[0],
          // Le complément est DIT, comme pour le minimum contributif :
          // sans lui, refaire la formule donnait la pension d'avant le
          // plancher, et l'écart restait sans explication.
          detail: `${pension.detail} = `
            + `${formatFixe(pension.montant, 2, true)} €, porté au minimum `
            + `garanti par + ${formatFixe(complement, 2, true)} €`,
        };
      }
    }
    if (releveGaranti > 0) {
      total += releveGaranti;
      avantages.push({
        code: "minimum_garanti",
        libelle: "Minimum garanti de la fonction publique",
        montant: releveGaranti,
        detail: "barème de l'article L. 17, sur la durée de services",
      });
    }
  }

  // LA PENSION COMPLÈTE D'UNE RETRAITE PROGRESSIVE (droit/progressive.js) :
  // elle ne peut être inférieure à la pension provisoire, revalorisée ; avant
  // le décret du 8 juin 2006, elle l'était. Voir le Python.
  let plancherProgressive = 0.0;
  for (const [regime, initiale] of initiales) {
    pensions.forEach((pension, indice) => {
      if (pension.regime !== regime || (recalcul && pension.montant >= initiale)) {
        return;
      }
      const ecart = initiale - pension.montant;
      plancherProgressive += ecart;
      total += ecart;
      pensions[indice] = {
        ...pension,
        montant: initiale,
        detail: recalcul
          ? `${pension.detail} = ${formatFixe(pension.montant, 2, true)} €, porté à la `
            + `pension provisoire revalorisée par + ${formatFixe(ecart, 2, true)} €`
          : "la pension provisoire de la retraite progressive, revalorisée : "
            + `${formatFixe(initiale, 2, true)} €, qui ne se recalcule pas avant le `
            + "8 juin 2006",
      };
    });
  }

  // Surcote parentale (L. 351-1-2-1) : après les minima, avant la majoration
  // pour enfants qui se calcule sur la pension surcotée. Elle ne compte pas
  // les mêmes trimestres que la surcote ordinaire — celle-ci au-delà de l'âge
  // légal, celle-là dans l'année qui le précède — et les deux se cumulent.
  const parametresParentale = (avantagesNonContributifs
    && majorationEnfants !== null && !ignorerPenaliteAge)
    ? moteur.surcoteParentale.parametres(anneeLiquidation)
    : null;
  if (parametresParentale !== null) {
    const [ageLegalMinimal, tauxParental, maximum, fiabiliteParentale] = parametresParentale;
    let gainParental = 0.0;
    let trimestresParentaux = 0;
    for (let indice = 0; indice < pensions.length; indice += 1) {
      const pension = pensions[indice];
      const regime = moteur.catalogue.obtenir(pension.regime);
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
      if (periode === null
          || !periode.avantages_non_contributifs.includes("surcote_parentale")) {
        continue;
      }
      const ageLegal = ouvrir.ageOuverture(moteur, periode, carriere);
      const requis = ouvrir.dureeRequise(moteur, periode, carriere)[0];
      // LA FENÊTRE EST L'ANNÉE QUI PRÉCÈDE L'ÂGE LÉGAL, dès que cet âge
      // atteint 63 ans (L. 351-1-2-1) : voir le Python, qui cite le texte.
      if (ageLegal < ageLegalMinimal) {
        continue;
      }
      // Au MOIS près : l'âge légal tombe en cours d'année depuis 2026.
      const dateLegale = carriere.dateDeLAge(ageLegal);
      const debutFenetre = dateLegale.plusMois(-12);
      // Seuls comptent les trimestres cotisés de la fenêtre accomplis « au
      // delà de la limite » de durée, trimestres pour enfants compris.
      if (requis <= 0) {
        continue;
      }
      const avant = majorationEnfants.trimestres + trimestresEntreDates(
        carriere, new DateMois(carriere.annee_naissance, 1), debutFenetre, false,
      );
      const validesFenetre = trimestresEntreDates(
        carriere, debutFenetre, dateLegale, false,
      );
      const trimestres = Math.min(
        maximum,
        trimestresEntreDates(carriere, debutFenetre, dateLegale, true),
        Math.max(0, avant + validesFenetre - requis),
      );
      if (trimestres <= 0) {
        continue;
      }
      const supplement = pension.montant * tauxParental * trimestres;
      pensions[indice] = {
        ...pension,
        montant: pension.montant + supplement,
        detail: `${pension.detail}, surcote parentale `
          + `${formatPourcentage(tauxParental * trimestres, 2)}`,
      };
      gainParental += supplement;
      trimestresParentaux = Math.max(trimestresParentaux, trimestres);
    }
    if (gainParental > 0) {
      total += gainParental;
      fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteParentale);
      avantages.push({
        code: "surcote_parentale",
        libelle: "Surcote parentale",
        montant: gainParental,
        detail: `${formatPourcentage(tauxParental * trimestresParentaux, 2)} pour `
          + `${trimestresParentaux} trimestre`
          + `${trimestresParentaux > 1 ? "s" : ""} dans `
          + "l'année qui précède l'âge légal",
      });
    }
  }

  if (avantagesNonContributifs && carriere.nombre_enfants >= 2) {
    let majoration = 0.0;
    let tauxCite = 0.0;
    // Le plafond de l'Agirc-Arrco s'oppose à la majoration de LA
    // complémentaire, pas à celle de chacune de ses fiches : les points d'un
    // salarié du privé sont répartis entre l'Agirc, l'Arrco et le régime
    // unifié, et plafonner chacun séparément triplerait le plafond.
    let majorationPlafonnee = 0.0;
    let plafondCommun = null;
    // [régime, part, soumise au plafond], dans l'ordre des pensions.
    const parts = [];
    for (const pension of pensions) {
      if (pension.montant <= 0.0) {
        continue;
      }
      const regime = moteur.catalogue.obtenir(pension.regime);
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
      if (periode === null
          || !periode.avantages_non_contributifs.includes("majoration_enfants")) {
        continue;
      }
      let taux = tauxMajorationEnfants(regime, carriere.nombre_enfants, periode);
      const points = pointsAcquis.get(pension.regime) ?? 0.0;
      const majores = pointsMajores.get(pension.regime) ?? 0.0;
      if (majores > 0.0 && points > 0.0) {
        // CHAQUE POINT À SON TAUX, celui de son année d'acquisition.
        taux = (majorationPoints.get(pension.regime) + taux * (points - majores)) / points;
      }
      if (taux <= 0) {
        continue;
      }
      const part = pension.montant * taux;
      const plafond = plafondMajoration(
        moteur, pension.regime, periode, carriere, anneeLiquidation,
      );
      if (plafond === null) {
        majoration += part;
      } else {
        majorationPlafonnee += part;
        plafondCommun = plafondCommun === null ? plafond : Math.max(plafondCommun, plafond);
      }
      parts.push([pension.regime, part, plafond !== null]);
      tauxCite = Math.max(tauxCite, taux);
    }
    const plafonnee = plafondCommun !== null;
    let retenuePlafonnee = 1.0;
    if (plafondCommun !== null) {
      majoration += Math.min(majorationPlafonnee, plafondCommun);
      if (majorationPlafonnee > plafondCommun) {
        retenuePlafonnee = plafondCommun / majorationPlafonnee;
      }
    }
    if (majoration > 0) {
      total += majoration;
      let detail = `jusqu'à ${formatPourcentage(tauxCite, 0)} selon le régime`;
      if (plafonnee) {
        detail += ", plafonnée en euros à la complémentaire";
      }
      avantages.push({
        code: "majoration_enfants",
        libelle: carriere.nombre_enfants >= 3
          ? "Majoration pour trois enfants et plus"
          : "Bonification pour deux enfants",
        montant: majoration,
        detail,
        par_regime: parts.map(([code, part, soumise]) => [
          code, part * (soumise ? retenuePlafonnee : 1.0),
        ]),
      });
    }
  }

  return new Complements({
    personne: carriere.personne,
    regimes: pensions,
    avantages,
    total,
    minimumApplique,
    fiabilite: fiabiliteGlobale,
    plancher: plancherProgressive,
    minimumEcrete,
  });
}

/**
 * Plafond en euros de la majoration pour enfants, ou ``null``.
 *
 * Les régimes de base servent 10 % sans plafond ; l'Agirc-Arrco borne la
 * majoration en euros — 2 367 € par an depuis le 1er novembre 2025 — et le
 * plafond suit la valeur de service du point. Il ne s'oppose qu'aux assurés
 * nés à compter du 2 août 1951 ; le modèle ne connaît que l'année de
 * naissance et retient les générations à partir de 1952.
 */
export function plafondMajoration(moteur, code, periode, carriere, anneeLiquidation) {
  if (periode.plafond_majoration_enfants === null
      || periode.plafond_majoration_enfants === undefined) {
    return null;
  }
  if (carriere.annee_naissance < 1952) {
    return null;
  }
  const plafond = periode.plafond_majoration_enfants;
  const anneeReference = periode.plafond_majoration_annee;
  if (anneeReference === null || anneeReference === anneeLiquidation) {
    return plafond;
  }
  const servie = liquider.valeurDuPoint(moteur, code, anneeLiquidation);
  const publiee = liquider.valeurDuPoint(moteur, code, anneeReference);
  if (servie === null || publiee === null || publiee[0] <= 0) {
    return plafond * moteur.macro.coefficientPrix(anneeReference, anneeLiquidation);
  }
  return plafond * servie[0] / publiee[0];
}

/**
 * Ce que le minimum contributif ajoute à une pension, surcote comprise —
 * portage de `complement_minimum` : depuis avril 2009, `plancher − nue` (la
 * surcote, calculée sur la pension nue, s'ajoute au minimum) ; avant,
 * `max(0, plancher − nue × coefficient)`. Circulaire Cnav 2018-04, 3.4.
 */
export function complementMinimum(nue, plancher, coefficientSurcote, dateEffet) {
  if (nue <= 0) {
    return 0.0;
  }
  const [annee, mois] = dateEffet;
  const [anneeRegle, moisRegle] = SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS;
  if (annee > anneeRegle || (annee === anneeRegle && mois >= moisRegle)) {
    return Math.max(0.0, plancher - nue);
  }
  return Math.max(0.0, plancher - nue * coefficientSurcote);
}

/**
 * Taux de majoration pour enfants, régime par régime. Le régime général et les
 * régimes spéciaux servent 10 % à partir de trois enfants ; la fonction
 * publique y ajoute 5 % par enfant au-delà du troisième. Les complémentaires
 * servent 10 % aussi, mais plafonnés en euros : le taux est le même, c'est
 * `plafondMajoration` qui borne. Une fiche qui porte son propre barème — les
 * marins, qui bonifient dès deux enfants — l'emporte.
 */
function tauxMajorationEnfants(regime, nombreEnfants, periode = null) {
  const bareme = periode?.taux_majoration_enfants;
  if (bareme && bareme.length > 0) {
    return bareme[Math.min(nombreEnfants, bareme.length - 1)];
  }
  if (nombreEnfants < 3) {
    return 0.0;
  }
  if (regime.famille === "fonction_publique") {
    return 0.1 + 0.05 * (nombreEnfants - 3);
  }
  return 0.1;
}

/**
 * Trimestres acquis entre deux DATES, au mois près — `fin` exclue. Portage de
 * `_trimestres_entre_dates` : chaque ligne répartit ses trimestres sur ses
 * mois (les premiers de l'année du départ, les derniers de celle de
 * l'entrée), seuls comptent ceux de la plage, arrondi au trimestre inférieur.
 */
function trimestresEntreDates(carriere, debut, fin, cotisesSeulement) {
  let total = 0.0;
  for (const ligne of carriere.lignes) {
    if (cotisesSeulement && !ligne.cotise) {
      continue;
    }
    total += trimestresDeLaLigneEntre(carriere, ligne, debut, fin);
  }
  return Math.floor(total + 1e-9);
}
