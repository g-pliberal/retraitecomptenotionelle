/**
 * Ouvrir le droit (docs/architecture.md, § 7.3).
 *
 * Jumeau de `src/retraite_notionnelle/droit/ouvrir.py`, fonction pour
 * fonction : à quel âge le droit ouvre-t-il la liquidation demandée, et à
 * quelle durée la sert-il au taux plein ? L'âge qu'un régime spécial a en
 * propre, celui que la catégorie active ou la jouissance militaire ouvrent,
 * l'âge légal de la génération (`ageOuverture`) ; la durée requise
 * (`dureeRequise`) ; la carrière longue quand l'âge demandé précède tous les
 * autres. `ouvrir` écrit ce que l'étape dit d'une demande — son schéma est
 * `data/reference/etapes/ouvrir_le_droit.yaml` ; `ageOuvertureDroit` et
 * `ageTauxPleinDroit` sont ce que le pilote en lit, sans rien liquider.
 */

import { DateMois, enMois } from "../calendrier.js";
import {
  GENERATIONS_SUSPENSION, SUSPENSION_2026_EFFET,
  GENERATION_REFORME_2023, REFORME_2023_EFFET,
} from "../regimes.js";
import { Fiabilite, nomFiabilite } from "../serie.js";
import { dateDEffet, derniereAnnee } from "./commun.js";
import * as compter from "./compter.js";
import * as coordonner from "./coordonner.js";
import { borneCarriere, REGIMES_CODE_DES_PENSIONS } from "./coordonner.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

/**
 * L'âge avant lequel un droit ouvert fait lire la durée à l'année d'ouverture
 * plutôt qu'à la génération : « avant l'âge de soixante ans » (L. 13, III).
 */
const AGE_DUREE_A_L_OUVERTURE = 60.0;

/** Le XXIV, C, de la loi du 14 avril 2023 ne vise que ceux qui peuvent liquider depuis ce mois. */
const DUREE_XXIV_C_DEPUIS = new DateMois(2023, 9);

/**
 * Durée minimale de services qui ouvre une pension militaire, même différée :
 * « lorsqu'ils ont accompli […] moins de quinze ans de services effectifs »,
 * dit le 5° de l'article L. 25, la pension n'est due qu'à l'âge légal.
 */
const SERVICES_MINIMAUX_MILITAIRES = 15.0;

/**
 * Trimestres de services que le II de l'article L. 14 ajoute à la durée
 * d'ouverture pour borner la décote militaire, et plafond de celle-ci.
 */
export const TRIMESTRES_DECOTE_MILITAIRE = 10;

/**
 * Surcote de l'emploi classé de la fonction publique (loi n° 2023-270, article
 * 10, XXIV, D) : première génération des marches de 2023, et années ajoutées à
 * l'âge anticipé ou minoré.
 */
const SURCOTE_EMPLOIS_CLASSES = {
  active: [1966 + 8 / 12, 5.0],
  super_active: [1971 + 8 / 12, 10.0],
};

/** Âge de la surcote d'avant la réforme de 2023, laissé aux classés plus âgés. */
const AGE_SURCOTE_AVANT_2023 = 62.0;

/** Ce que l'étape « ouvrir le droit » dit d'une demande. */
export class Ouverture {
  constructor({ carriere, requis, age, motif, trimestresCotises, fiabilite }) {
    this.carriere = carriere;
    this.requis = requis;
    this.age = age;
    this.motif = motif;
    this.trimestresCotises = trimestresCotises;
    this.fiabilite = fiabilite;
  }

  /** Le droit ouvre-t-il la liquidation à cet âge ? */
  get ouverte() {
    return this.motif !== "non_ouverte";
  }

  /** L'ouverture, telle que le schéma de l'étape la décrit. */
  donnees() {
    return {
      schema_version: SCHEMA_VERSION,
      personne: this.carriere.personne,
      date_effet: dateDEffet(this.carriere),
      requis: this.requis,
      age: this.age,
      motif: this.motif,
      trimestres_cotises: this.trimestresCotises,
      fiabilite: nomFiabilite(this.fiabilite),
    };
  }
}

/** Ce que le droit ouvre à la demande dont `releve` est le relevé. Voir le Python. */
export function ouvrir(moteur, releve) {
  const carriere = releve.carriere;
  const { durees, droits } = releve;
  const anneeLiquidation = carriere.anneeLiquidation;
  const ageLiquidation = carriere.age_liquidation || 0.0;
  const majorationEnfants = durees.enfants;
  const codes = droits.codes;
  let fiabilite = Fiabilite.CERTIFIEE;

  // Durée requise de référence : celle du régime de base. C'est elle qui
  // commande le taux plein, donc aussi l'abattement des complémentaires —
  // un assuré au taux plein liquide sa complémentaire sans abattement, quel
  // que soit son âge.
  let requisReference = 0;
  // Âge d'ouverture des droits le plus précoce parmi les régimes de base de
  // la carrière. Un polypensionné liquide en réalité chaque pension à l'âge
  // de son régime ; le modèle liquide tout à la fois, et retient donc l'âge
  // du régime le plus précoce.
  let ageOuvertureReference = null;
  // Un régime et celui qui lui succède liquident ensemble, sous les règles
  // de la caisse qui aurait le dossier : les autres membres du groupe sont
  // sautés partout où un régime liquide. À FAUX, chaque nom de caisse est
  // liquidé sur ses seules années — variante qui ne sert qu'à mesurer.
  const groupes = releve.groupes;
  // DEUX PASSES, ET LA SECONDE NE SERT QU'À QUI N'A QUE DES POINTS. Les
  // régimes en annuités commandent ; mais une carrière entière en points
  // n'en a aucun, et `ageOuvertureReference` restait nul — aucun âge ne lui
  // était opposé, et un chef d'exploitation pouvait liquider à cinquante ans
  // sans que rien ne le refuse. `requisReference` retombait de son côté sur
  // 160, une durée que plus aucune génération ne doit, et c'est elle que
  // l'abattement du régime en points opposait.
  for (const calculs of [["annuites"], ["points", "mixte"]]) {
    for (const code of codes) {
      if ((groupes.get(code) ?? [code])[0] !== code) {
        continue;
      }
      const regime = moteur.catalogue.obtenir(code);
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
      if (periode === null || !calculs.includes(periode.type_calcul)) {
        continue;
      }
      if (periode.abattement_points === "agirc_arrco"
        || periode.abattement_points === "ircantec") {
        continue;
      }
      // Une complémentaire qui a SES âges ne dit pas quand le droit s'ouvre :
      // c'est le régime de base qu'elle accompagne qui le dit. Un régime de
      // base en annuités qui a les siens — SNCF, RATP, IEG — le dit, lui.
      if (periode.age_table && periode.type_calcul !== "annuites") {
        continue;
      }
      requisReference = Math.max(requisReference, dureeRequise(moteur, periode, carriere)[0]);
      const ageRegime = ageOuverture(moteur, periode, carriere);
      ageOuvertureReference = ageOuvertureReference === null
        ? ageRegime
        : Math.min(ageOuvertureReference, ageRegime);
    }
    if (ageOuvertureReference !== null) {
      break;
    }
  }
  requisReference = requisReference || 160;

  // Trimestres réellement COTISÉS, tous régimes : ils commandent la carrière
  // longue et la majoration du minimum contributif.
  const trimestresCotises = carriere.trimestresCumules(carriere.lignes.filter(
    (ligne) => ligne.cotise && ligne.annee <= anneeLiquidation,
  ));

  // Le droit ouvre-t-il cette liquidation à cet âge ? La question n'était pas
  // posée : le modèle servait une pension décotée à qui ne pouvait pas encore
  // liquider, ce qui n'est ni le droit ni un contrefactuel utile.
  let motifOuverture = "age_legal";
  if (ageOuvertureReference !== null && ageLiquidation < ageOuvertureReference) {
    const anticipe = moteur.carriereLongue.ageDeDepart(
      carriere, anneeLiquidation,
      moteur.carriereLongue.cotisesReputes(
        carriere, trimestresCotises,
        majorationEnfants !== null ? majorationEnfants.trimestres : 0,
      ),
      requisReference,
    );
    if (anticipe !== null && ageLiquidation >= anticipe[0]) {
      motifOuverture = "carriere_longue";
      ageOuvertureReference = anticipe[0];
      fiabilite = Math.min(fiabilite, anticipe[1]);
    } else {
      motifOuverture = "non_ouverte";
    }
  }

  return new Ouverture({
    carriere,
    requis: requisReference,
    age: ageOuvertureReference,
    motif: motifOuverture,
    trimestresCotises,
    fiabilite,
  });
}

/** @returns {[number, number|null]} durée requise opposable, et fiabilité. */
export function dureeRequise(moteur, periode, carriere) {
  // UN RÉGIME SPÉCIAL QUI ÉCRIT SES TABLES PASSE AVANT LA TABLE COMMUNE : la
  // SNCF, la RATP et les IEG — tables par génération à compter de leur date
  // d'effet, puis calendrier de 2008 lu au mois où les conditions sont réunies.
  const propre = dureePropre(moteur, periode, carriere);
  if (propre !== null) {
    return [propre[0], propre[2]];
  }
  // La fonction publique a sa propre montée en charge, 2004-2008, lue à
  // l'année d'ouverture du droit ; elle passe avant la table par génération.
  if (periode.bareme_decote === "fonction_publique") {
    const transitoire = moteur.dureesRequisesFonctionPublique.trimestres(
      anneeOuvertureDesDroits(
        moteur, periode, carriere,
        (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined)
          ? carriere.anneeLiquidation : 9999,
      ),
    );
    if (transitoire !== null) {
      return transitoire;
    }
  }
  // ET UN EMPLOI CLASSÉ N'A PAS LA DURÉE DE SA GÉNÉRATION : le XXIV, B de
  // l'article 10 de la loi du 14 avril 2023 pour l'État, et le II, B de
  // l'article 13 du décret n° 2023-435 pour la CNRACL et le FSPOEIE, lui en
  // fixent une propre « par dérogation à l'article L. 13 ».
  const derogation = derogationActive(moteur, periode, carriere);
  if (derogation !== null && derogation.dureeRequise !== null) {
    return [derogation.dureeRequise, derogation.fiabilite];
  }
  // Et ceux que ces marches ne visent pas — l'emploi classé né avant elles,
  // le militaire — n'ont pas davantage la durée de leur génération.
  const avantSoixanteAns = dureeRequiseAvantSoixanteAns(moteur, periode, carriere, derogation);
  if (avantSoixanteAns !== null) {
    return avantSoixanteAns;
  }
  if (periode.duree_requise_par_generation) {
    // LA RÉFORME DE 2023 NE VAUT QU'À COMPTER DU 1er SEPTEMBRE 2023 : avant,
    // les nés à compter du 1er septembre 1961 doivent la durée de la version
    // de 2014 de L. 161-17-3. Voir le Python.
    const [anneeReforme, moisReforme] = REFORME_2023_EFFET;
    if (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined
        && carriere.generation >= GENERATION_REFORME_2023
        && (carriere.anneeLiquidation < anneeReforme
          || (carriere.anneeLiquidation === anneeReforme
            && carriere.moisLiquidation < moisReforme))) {
      const avant = moteur.dureesRequisesAvantReforme2023.trimestres(carriere.generation);
      if (avant !== null) {
        return avant;
      }
    }
    // LA SUSPENSION NE VAUT QU'À COMPTER DU 1er SEPTEMBRE 2026 : avant, les
    // nés en 1964 et 1965 doivent la durée de la loi de 2023.
    const [anneeEffet, moisEffet] = SUSPENSION_2026_EFFET;
    if (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined
        && carriere.generation >= GENERATIONS_SUSPENSION[0]
        && carriere.generation < GENERATIONS_SUSPENSION[1]
        && (carriere.anneeLiquidation < anneeEffet
          || (carriere.anneeLiquidation === anneeEffet
            && carriere.moisLiquidation < moisEffet))) {
      const avant = moteur.dureesRequisesAvantSuspension.trimestres(carriere.generation);
      if (avant !== null) {
        return avant;
      }
    }
    const parGeneration = moteur.dureesRequises.trimestres(carriere.generation);
    if (parGeneration !== null) {
      return parGeneration;
    }
  }
  return [periode.duree_requise_trimestres || 160, null];
}

/**
 * La durée d'un droit qui s'ouvre avant soixante ans, ou null.
 *
 * Le militaire qui réunit ses services, l'emploi classé qui atteint son âge
 * anticipé ou minoré ne se voient pas opposer la durée de leur génération,
 * mais « celle exigée des fonctionnaires atteignant [soixante ans] l'année à
 * compter de laquelle la liquidation peut intervenir » — article 5, VI, de
 * la loi du 21 août 2003, puis L. 13, III, du code des pensions, que le XXIV
 * de la loi du 14 avril 2023 garde en vigueur par renvoi. Le militaire qui
 * peut liquider à compter du 1er septembre 2023 relève du C, 2°, du même
 * XXIV. Avant 2004, c'est la durée que la fiche portait l'année d'ouverture.
 * ``derogation`` est celle que dureeRequise vient de lire.
 *
 * @returns {[number, number|null] | null}
 */
export function dureeRequiseAvantSoixanteAns(moteur, periode, carriere, derogation) {
  if (periode.bareme_decote !== "fonction_publique") {
    return null;
  }
  const militaire = droitMilitaire(moteur, periode, carriere);
  let age;
  let carriereLongue = false;
  if (militaire !== null) {
    age = militaire.ageOuverture;
  } else if (derogation !== null) {
    age = derogation.ageOuverture;
  } else if (REGIMES_CODE_DES_PENSIONS.has(periode.regime)) {
    // Le fonctionnaire sédentaire dont la carrière longue ouvre le droit
    // avant soixante ans relève du même C du XXIV : voir le Python.
    age = ouvertureCarriereLongue(moteur, periode, carriere);
    if (age === null) {
      return null;
    }
    carriereLongue = true;
  } else {
    return null;
  }
  if (age >= AGE_DUREE_A_L_OUVERTURE) {
    return null;
  }
  let ouverture = carriere.dateNaissance.plusMois(enMois(age));
  if (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined) {
    ouverture = DateMois.depuisRang(Math.min(
      ouverture.rang,
      carriere.dateNaissance.plusMois(enMois(carriere.age_liquidation)).rang,
    ));
  }
  if ((militaire !== null || carriereLongue) && ouverture.rang >= DUREE_XXIV_C_DEPUIS.rang) {
    return moteur.dureesRequisesAvantSoixanteAns.depuis2023(ouverture);
  }
  const transitoire = moteur.dureesRequisesFonctionPublique.trimestres(ouverture.annee);
  if (transitoire !== null) {
    return transitoire;
  }
  const parAnnee = moteur.dureesRequisesAvantSoixanteAns.parAnnee(ouverture.annee);
  if (parAnnee !== null) {
    return parAnnee;
  }
  const enVigueur = moteur.catalogue.obtenir(periode.regime).periode(ouverture.annee);
  if (enVigueur === null || enVigueur === undefined
      || enVigueur.duree_requise_trimestres === null
      || enVigueur.duree_requise_trimestres === undefined) {
    return null;
  }
  return [enVigueur.duree_requise_trimestres, null];
}

/**
 * L'âge où la carrière longue ouvre le droit de ce fonctionnaire, s'il l'ouvre
 * au plus tard à la liquidation ; `null` sinon. La condition de durée est
 * celle de la génération (D. 16-1 du code des pensions) : pendant qu'on la
 * lit, `dureeRequise` ne rend pas la durée que ce droit fait opposer ensuite.
 */
export function ouvertureCarriereLongue(moteur, periode, carriere) {
  if (moteur.ouvertureCarriereLongueEnCours
      || carriere.age_liquidation === null || carriere.age_liquidation === undefined) {
    return null;
  }
  moteur.ouvertureCarriereLongueEnCours = true;
  let age;
  try {
    age = ageCarriereLongue(moteur, carriere, [[periode.regime, periode]]);
  } finally {
    moteur.ouvertureCarriereLongueEnCours = false;
  }
  if (age === null || age === undefined || age > carriere.age_liquidation + 1e-9) {
    return null;
  }
  return age;
}

/**
 * Le classement que la carrière a exercé le plus longtemps.
 *
 * La règle est celle du code : quand plusieurs emplois classés se succèdent,
 * « la catégorie applicable pour bénéficier de l'âge de départ minoré est
 * celle associée à l'emploi que le fonctionnaire a occupé le plus longtemps »
 * (L. 24, I, 1°). À égalité, le classement le plus favorable l'emporte,
 * parce que la durée qu'il exige est la plus longue.
 */
export function statutDominant(moteur, carriere, classements) {
  const durees = new Map();
  const borne = borneCarriere(carriere);
  for (const [statut, classement] of Object.entries(classements)) {
    const duree = carriere.dureeDeService([statut], borne);
    if (duree > 0) {
      durees.set(classement, (durees.get(classement) ?? 0) + duree);
    }
  }
  if (durees.size === 0) {
    return null;
  }
  let meilleur = null;
  let reference = [-1, 0];
  for (const cle of [...durees.keys()].sort()) {
    const rang = [durees.get(cle),
      (cle === "super_active" || cle === "officier") ? 1 : 0];
    if (rang[0] > reference[0] || (rang[0] === reference[0] && rang[1] > reference[1])) {
      meilleur = cle;
      reference = rang;
    }
  }
  return meilleur;
}

/**
 * L'âge anticipé que le classement de l'emploi ouvre, ou null.
 *
 * Quatre conditions, et la fiche en porte une : le régime doit servir la
 * catégorie active — l'avoir dans ses `avantages_non_contributifs` —, le
 * statut déclaré doit être classé, le régime doit être l'un de ceux que ce
 * statut route (cf. `regimesRoutes`), et la carrière doit porter la durée de
 * services classés que l'article L. 24 exige. Sans elle, l'assuré reste au
 * droit commun : la faculté « est ouverte à la condition que le fonctionnaire
 * puisse se prévaloir, au total, d'au moins dix-sept ans de services […] dits
 * services actifs ».
 */
export function derogationActive(moteur, periode, carriere) {
  if (!periode.avantages_non_contributifs.includes("categorie_active")) {
    return null;
  }
  const classements = moteur.affiliations.classementsActifs;
  const classement = statutDominant(moteur, carriere, classements);
  if (classement === null) {
    return null;
  }
  const derogation = moteur.agesCategorieActive.derogation(
    classement, carriere.generation,
  );
  if (derogation === null) {
    return null;
  }
  const statuts = Object.keys(classements)
    .filter((code) => classements[code] === classement);
  if (!coordonner.regimesRoutes(moteur, statuts).has(periode.regime)) {
    return null;
  }
  const servies = carriere.dureeDeService(statuts, borneCarriere(carriere));
  if (servies + 1e-9 < derogation.servicesRequis) {
    return null;
  }
  return derogation;
}

/**
 * Ce que la pension militaire oppose à cet assuré, ou null.
 *
 * Elle ne s'ouvre pas à un âge mais à une DURÉE — dix-sept ans de services
 * effectifs pour un non-officier, vingt-sept pour un officier (L. 24, II).
 * Qui la réunit liquide aussitôt ; qui ne la réunit pas mais a quinze ans de
 * services attend l'âge de jouissance différée de l'article L. 25 ; qui a
 * moins de quinze ans n'a pas de pension militaire.
 */
export function droitMilitaire(moteur, periode, carriere) {
  if (!periode.avantages_non_contributifs.includes("categorie_active")) {
    return null;
  }
  const categories = moteur.affiliations.categoriesMilitaires;
  const categorie = statutDominant(moteur, carriere, categories);
  if (categorie === null) {
    return null;
  }
  const statuts = Object.keys(categories)
    .filter((code) => categories[code] === categorie);
  if (!coordonner.regimesRoutes(moteur, statuts).has(periode.regime)) {
    return null;
  }
  const base = moteur.dureesServicesMilitaires.dureeDeBase(categorie);
  if (base === null) {
    return null;
  }
  const dateBase = carriere.dateDeService(statuts, base);
  const anneeBase = dateBase === null
    ? 9999.0
    : dateBase.annee + (dateBase.mois - 1) / 12;
  const requises = moteur.dureesServicesMilitaires.anneesRequises(categorie, anneeBase);
  if (requises === null || requises === undefined) {
    return null;
  }
  const [anneesRequises] = requises;
  let fiabilite = requises[1];
  const servies = carriere.dureeDeService(statuts, borneCarriere(carriere));
  const ageRequis = carriere.ageDeService(statuts, anneesRequises);
  let ageOuverture;
  let differee;
  if (servies + 1e-9 >= anneesRequises && ageRequis !== null) {
    ageOuverture = ageRequis;
    differee = false;
  } else if (servies + 1e-9 >= SERVICES_MINIMAUX_MILITAIRES) {
    const parGeneration = moteur.agesJouissanceMilitaire.age(carriere.generation);
    if (parGeneration === null) {
      return null;
    }
    ageOuverture = parGeneration[0];
    differee = true;
    fiabilite = Math.min(fiabilite, parGeneration[1]);
  } else {
    return null;
  }
  return {
    ageOuverture,
    trimestresServis: Math.round(servies * 4),
    trimestresCible: Math.round(anneesRequises * 4) + TRIMESTRES_DECOTE_MILITAIRE,
    jouissanceDifferee: differee,
    fiabilite,
  };
}

/**
 * Âge légal opposable à cet assuré dans ce régime.
 *
 * Trois droits se superposent, du plus particulier au plus général : la
 * pension militaire, qui s'ouvre à une durée de services ; la catégorie
 * active, qui avance l'âge de cinq ou de dix années ; le droit commun.
 */
export function ageOuverture(moteur, periode, carriere) {
  const militaire = droitMilitaire(moteur, periode, carriere);
  if (militaire !== null) {
    return militaire.ageOuverture;
  }
  const derogation = derogationActive(moteur, periode, carriere);
  if (derogation !== null) {
    return derogation.ageOuverture;
  }
  const commun = ageOuvertureCommun(moteur, periode, carriere);
  const speciale = ouverturePensionSpeciale(moteur, periode, carriere);
  if (speciale !== null) {
    return speciale;
  }
  const parServices = ouvertureParServices(moteur, periode, carriere);
  if (parServices !== null && parServices < commun) {
    return parServices;
  }
  return commun;
}

/** Les statuts que le régime route, et les années servies dans ceux-ci. */
export function servicesDansLeRegime(moteur, periode, carriere) {
  const statuts = moteur.affiliations.codes
    .filter((code) => coordonner.regimesRoutes(moteur, [code]).has(periode.regime));
  return { statuts, servies: carriere.dureeDeService(statuts, borneCarriere(carriere)) };
}

/**
 * L'âge de la pension SPÉCIALE des marins, ou null si l'assuré a les quinze
 * ans de services qui ouvrent une autre pension. Elle entre en jouissance
 * avec la pension de base d'un autre régime, jamais avant cinquante-cinq ans,
 * et à défaut à soixante ans (L. 5552-12 du code des transports, R. 5 du code
 * des pensions de retraite des marins). Le modèle liquidant tout à la même
 * date, elle suit le plus précoce des AUTRES régimes de base traversés.
 */
export function ouverturePensionSpeciale(moteur, periode, carriere) {
  const seuil = periode.pension_speciale_services_annees;
  const isole = periode.pension_speciale_age_sans_autre_pension;
  if (seuil == null || isole == null) {
    return null;
  }
  const { servies } = servicesDansLeRegime(moteur, periode, carriere);
  if (servies + 1e-9 >= seuil) {
    return null;
  }
  const { annuites, autres } = periodesParcourues(moteur, carriere);
  const bases = [...annuites, ...periodesOpposantUneDuree(autres)]
    .filter(([code]) => code !== periode.regime)
    .map(([, p]) => p);
  if (bases.length === 0) {
    return isole;
  }
  return Math.max(periode.age_ouverture,
    Math.min(...bases.map((p) => ageOuverture(moteur, p, carriere))));
}

/**
 * L'âge que la durée de services dans le régime ouvre, ou null.
 *
 * Les marins acquièrent la pension d'ancienneté « lorsque se trouve remplie
 * la double condition de cinquante ans d'âge et de vingt-cinq années de
 * services » (R. 2 de leur code) ; les cinquante-cinq ans que le même article
 * fixe ensuite ne bornent que l'entrée en jouissance de celui qui continue à
 * naviguer (L. 5552-5 du code des transports). L'âge est le plus tardif de
 * l'âge écrit et de celui où la durée est atteinte.
 */
export function ouvertureParServices(moteur, periode, carriere) {
  if (periode.age_ouverture_services == null
      || periode.services_ouverture_annees == null) {
    return null;
  }
  const { statuts, servies } = servicesDansLeRegime(moteur, periode, carriere);
  const requis = periode.services_ouverture_annees;
  if (servies + 1e-9 < requis) {
    return null;
  }
  const atteint = carriere.ageDeService(statuts, requis);
  if (atteint === null) {
    return null;
  }
  return Math.max(periode.age_ouverture_services, atteint);
}

/**
 * Âge au-delà duquel les trimestres cotisés ouvrent la surcote : l'âge légal
 * de droit commun, sauf la SNCF et la RATP, qui ont leur calendrier, et
 * l'emploi classé de la fonction publique. Pour lui, le D du XXIV de
 * l'article 10 de la loi du 14 avril 2023 (et le II, D, de l'article 13 du
 * décret n° 2023-435) donne l'âge anticipé majoré de cinq années aux actifs
 * nés à compter du 1er septembre 1966, l'âge minoré majoré de dix aux
 * super-actifs nés à compter du 1er septembre 1971, et soixante-deux ans
 * avant — et non l'âge légal de leur génération.
 */
export function ageSurcote(moteur, periode, carriere) {
  if (periode.age_surcote_regimes_speciaux) {
    const propre = moteur.agesSurcoteRegimesSpeciaux.age(carriere.generation);
    if (propre !== null) {
      return propre[0];
    }
  }
  const commun = ageOuvertureCommun(moteur, periode, carriere);
  if (moteur.catalogue.obtenir(periode.regime).famille !== "fonction_publique") {
    return commun;
  }
  const derogation = derogationActive(moteur, periode, carriere);
  if (derogation === null) {
    return commun;
  }
  const classement = statutDominant(moteur, carriere, moteur.affiliations.classementsActifs);
  const marche = SURCOTE_EMPLOIS_CLASSES[classement ?? ""];
  if (marche === undefined) {
    return commun;
  }
  const [premiereGeneration, majoration] = marche;
  if (carriere.generation + 1e-9 >= premiereGeneration) {
    return derogation.ageOuverture + majoration;
  }
  return Math.min(commun, AGE_SURCOTE_AVANT_2023);
}

export function ageOuvertureCommun(moteur, periode, carriere) {
  if (periode.age_table) {
    const propres = moteur.agesRegimes.ages(periode.age_table, carriere.generation);
    // Un âge vide renvoie au droit commun, que les tables communes portent.
    if (propres !== null && propres[0] !== null) {
      return propres[0];
    }
  }
  if (periode.age_ouverture_par_generation) {
    const parGeneration = moteur.agesOuverture.age(carriere.generation);
    if (parGeneration !== null) {
      return parGeneration[0];
    }
  }
  return periode.age_ouverture;
}

/**
 * Les régimes que cette carrière traverse, séparés en deux paquets.
 *
 * Le premier est celui des régimes en ANNUITÉS, qui commandent le taux plein
 * et l'ouverture du droit ; le second recueille les autres. C'est la même
 * énumération que celle de `calculer`, mais tirée de la seule carrière : elle
 * répond donc AVANT que la pension ne soit calculée, ce qu'il faut pour dater
 * un départ.
 *
 * @returns {{annuites: Array, autres: Array}}
 */
export function periodesParcourues(moteur, carriere) {
  const anneeLiquidation = carriere.anneeLiquidation;
  const codes = new Set();
  for (const ligne of carriere.lignes) {
    if (ligne.annee > anneeLiquidation) {
      continue;
    }
    for (const code of coordonner.regimesDe(moteur, 
      ligne, ligne.annee, carriere.dateEntree(ligne.affiliation),
      ligne.cotise ? ligne.revenu : ligne.revenu_reference,
      moteur.macro.plafond_securite_sociale.valeur(ligne.annee),
    )) {
      codes.add(code);
    }
  }
  const annuites = [];
  const autres = [];
  for (const code of [...codes].sort()) {
    if (!moteur.catalogue.contient(code)) {
      continue;
    }
    const regime = moteur.catalogue.obtenir(code);
    const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
    if (periode === null) {
      continue;
    }
    (periode.type_calcul === "annuites" ? annuites : autres).push([code, periode]);
  }
  return { annuites, autres };
}

/**
 * L'âge auquel le droit OUVRE la liquidation de cette carrière.
 *
 * C'est la même question que celle posée dans `calculer` — le plus précoce
 * des régimes de base parcourus, chacun lisant l'âge que sa génération lui
 * oppose —, mais posée AVANT la pension et sans la calculer. Elle a un usage
 * propre : dater le départ d'un cas type. Une grille qui fait partir toutes
 * les générations au même âge fait partir celle de 1940 à un âge que la loi
 * de 2023 lui opposera soixante ans plus tard.
 *
 * Ce sont les régimes en ANNUITÉS qui commandent. Quand la carrière n'en a
 * aucun — le libéral, dont le régime de base est en points —, les autres
 * répondent. `null` quand aucun régime connu n'est parcouru.
 */
export function ageOuvertureDroit(moteur, carriereSaisie) {
  const carriere = coordonner.retablir(moteur, carriereSaisie);
  const { annuites, autres: enPoints } = periodesParcourues(moteur, carriere);
  const autres = sansAgesPropres(enPoints);
  const retenues = annuites.length > 0 ? annuites : autres;
  if (retenues.length === 0) {
    return null;
  }
  const ouverture = Math.min(
    ...retenues.map(([, periode]) => ageOuverture(moteur, periode, carriere)),
  );
  // Les deux régimes de base en POINTS ouvrent la carrière longue :
  // L. 732-18-1 du code rural pour les non-salariés agricoles, le II de
  // L. 643-3 du code de la sécurité sociale pour les professions libérales,
  // par renvoi à L. 351-1-1. Les deux règles d'âge la lisent sur la même
  // liste, sans quoi elles se contrediraient.
  const anticipe = ageCarriereLongue(
    moteur, carriere,
    annuites.length > 0 ? annuites : periodesOpposantUneDuree(autres),
  );
  if (anticipe !== null && anticipe < ouverture) {
    return anticipe;
  }
  return ouverture;
}

/**
 * L'âge que le départ anticipé pour carrière longue proposerait à cette
 * carrière, ou `null` s'il ne lui ouvre rien.
 *
 * `calculer` la connaissait déjà, mais comme une dérogation qu'on lui
 * demande à un âge donné, pas comme un âge qu'il propose : un salarié entré à
 * dix-huit ans et né en 1965 partait, en cas type, à l'âge légal quand le
 * droit lui ouvre soixante-deux ans au taux plein. La durée requise et les
 * trimestres cotisés sont ceux que `calculer` oppose au même départ.
 */
export function ageCarriereLongue(moteur, carriere, annuites) {
  if (annuites.length === 0) {
    return null;
  }
  const requis = Math.max(
    ...annuites.map(([, periode]) => dureeRequise(moteur, periode, carriere)[0]),
  ) || 160;
  const anneeLiquidation = carriere.anneeLiquidation;
  let cotises = carriere.trimestresCumules(carriere.lignes.filter(
    (ligne) => ligne.cotise && ligne.annee <= anneeLiquidation,
  ));
  const majoration = compter.majorationPourEnfants(moteur, 
    carriere, new Map(annuites.map(([code]) => [code, cotises])), anneeLiquidation,
  );
  cotises = moteur.carriereLongue.cotisesReputes(
    carriere, cotises, majoration !== null ? majoration.trimestres : 0,
  );
  return moteur.carriereLongue.agePropose(
    carriere, anneeLiquidation, cotises, requis, carriere.age_liquidation,
  );
}

/**
 * Parmi des périodes NON annuitaires, celles qui opposent une durée.
 *
 * L'Agirc-Arrco et l'Ircantec sont écartées : elles ont leurs propres
 * coefficients d'anticipation, et ne sont jamais seules sur une carrière.
 */
export function periodesOpposantUneDuree(periodes) {
  return periodes.filter(([, periode]) =>
    periode.abattement_points !== "agirc_arrco"
    && periode.abattement_points !== "ircantec");
}

/**
 * Les périodes en points, moins les complémentaires qui ont leurs âges : une
 * complémentaire qui a SES âges ne dit pas quand le droit s'ouvre ni quand il
 * est entier, c'est le régime de base qu'elle accompagne qui le dit, et
 * `calculer` l'écarte déjà. Si rien d'autre ne reste, on la garde. Voir le
 * modèle Python.
 */
export function sansAgesPropres(periodes) {
  const communes = periodes.filter(([, periode]) => !periode.age_table);
  return communes.length > 0 ? communes : periodes;
}

export function ageTauxPleinDroit(moteur, carriereSaisie) {
  const carriere = coordonner.retablir(moteur, carriereSaisie);
  const { annuites, autres: enPoints } = periodesParcourues(moteur, carriere);
  const autres = sansAgesPropres(enPoints);
  const retenues = annuites.length > 0 ? annuites : autres;
  if (retenues.length === 0) {
    return null;
  }
  const ouverture = Math.min(
    ...retenues.map(([, periode]) => ageOuverture(moteur, periode, carriere)),
  );
  // Une carrière entière en points n'a aucune période en annuités, et la
  // règle rendait alors l'âge d'OUVERTURE — elle faisait donc liquider au
  // taux plein des carrières que `abattementPoints` servait minorées. Le
  // droit oppose bien la durée aux régimes en points : L. 643-3 du code de
  // la sécurité sociale pour les professions libérales, L. 732-24 II du code
  // rural pour les non-salariés agricoles. L'Agirc-Arrco et l'Ircantec sont
  // écartées : elles ont leurs propres coefficients d'anticipation, et ne
  // sont jamais seules sur une carrière.
  const opposent = annuites.length > 0
    ? annuites
    : periodesOpposantUneDuree(autres);
  if (opposent.length === 0) {
    return ouverture;
  }
  const annulation = Math.min(
    ...retenues.map(([, periode]) => ageTauxPlein(moteur, periode, carriere)),
  );
  const requis = Math.max(
    ...opposent.map(([, periode]) => dureeRequise(moteur, periode, carriere)[0]),
  );
  if (!requis) {
    return ouverture;
  }
  const anneeLiquidation = carriere.anneeLiquidation;
  let acquis = carriere.trimestresCumules(carriere.lignes.filter(
    (ligne) => ligne.annee <= anneeLiquidation,
  ));
  // Les trimestres accordés au titre des enfants comptent dans la durée,
  // lus au régime qui les porte comme `calculer` le fait : sans eux, une
  // mère de deux enfants était datée trois ans après l'âge où sa pension
  // est entière.
  const majoration = compter.majorationPourEnfants(moteur, 
    carriere, new Map(opposent.map(([code]) => [code, acquis])), anneeLiquidation,
  );
  if (majoration !== null) {
    acquis += majoration.trimestres;
  }
  const duree = carriere.age_liquidation + (requis - acquis) / 4.0;
  const tauxPlein = Math.min(annulation, Math.max(ouverture, duree));
  // Le départ anticipé pour carrière longue passe avant les trois termes :
  // il n'ouvre qu'à qui a sa durée COTISÉE, donc au taux plein.
  const anticipe = ageCarriereLongue(moteur, carriere, opposent);
  if (anticipe !== null && anticipe < tauxPlein) {
    return anticipe;
  }
  return tauxPlein;
}

/**
 * Âge d'annulation de la décote opposable à cet assuré.
 *
 * Pour un emploi classé, ce n'est pas soixante-sept ans mais la limite d'âge
 * du grade — soixante-deux ans en catégorie active, cinquante-sept en
 * super-active —, puis l'âge que l'article L. 14 bis attache au classement.
 */
export function ageTauxPlein(moteur, periode, carriere) {
  const derogation = derogationActive(moteur, periode, carriere);
  if (derogation !== null) {
    return derogation.ageAnnulation;
  }
  if (periode.age_table) {
    const propres = moteur.agesRegimes.ages(periode.age_table, carriere.generation);
    if (propres !== null && propres[1] !== null) {
      return propres[1];
    }
  }
  if (periode.age_taux_plein_par_generation) {
    const parGeneration = moteur.agesAnnulationDecote.age(carriere.generation);
    if (parGeneration !== null) {
      return parGeneration[0];
    }
  }
  return periode.age_taux_plein;
}

/**
 * Année où les conditions d'ouverture du droit sont réunies.
 *
 * C'est le millésime auquel se lisent les barèmes de décote en table. L'assuré
 * les réunit quand il atteint l'âge d'ouverture de son régime, au mois près ;
 * s'il liquide avant — carrière longue, catégorie active —, il les réunit au
 * plus tôt à la liquidation, et c'est cette année-là qui vaut.
 */
export function anneeOuvertureDesDroits(moteur, periode, carriere, anneeLiquidation) {
  const ouverture = carriere.dateNaissance
    .plusMois(enMois(ageOuverture(moteur, periode, carriere))).annee;
  return Math.min(anneeLiquidation, ouverture);
}

export function moisOuvertureDesDroits(moteur, periode, carriere) {
  let rang = carriere.dateNaissance.plusMois(
    enMois(ageOuverture(moteur, periode, carriere)),
  ).rang;
  if (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined) {
    rang = Math.min(rang, carriere.dateLiquidation.rang);
  }
  return rang;
}

/** Durée requise propre au régime : [trimestres, retranchés, fiabilité] ou null. */
export function dureePropre(moteur, periode, carriere) {
  const tables = periode.duree_requise_table ?? [];
  if (tables.length === 0 && !periode.duree_requise_calendrier) {
    return null;
  }
  const ouverture = moisOuvertureDesDroits(moteur, periode, carriere);
  for (const table of tables) {
    const ligne = moteur.dureesRequisesRegimes.ligne(table, carriere.generation, ouverture);
    if (ligne !== null) {
      return ligne;
    }
  }
  if (periode.duree_requise_calendrier) {
    const lu = moteur.calendriersDureeRequise.trimestres(
      periode.duree_requise_calendrier, ouverture,
    );
    if (lu !== null) {
      return [lu[0], 0, lu[1]];
    }
  }
  return null;
}
