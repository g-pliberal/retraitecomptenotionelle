/**
 * La limite d'âge des agents publics, et ses exceptions (action 151, étapes 3
 * et 4).
 *
 * Le fonctionnaire est radié des cadres à la limite d'âge de son emploi,
 * reculée de droit pour ses enfants, prolongée — présumée demandée et accordée
 * autant que le départ saisi le demande — pour carrière incomplète, pour
 * l'actif jusqu'à la limite des sédentaires, et pour le sédentaire jusqu'à
 * soixante-dix ans ; depuis le 14 juin 2023, pas au-delà de soixante-dix ans.
 * Le militaire prend la limite la plus haute de sa catégorie. Sa pension part
 * de la radiation, et ce qui suit n'est plus du service. L'agent contractuel,
 * l'ouvrier de l'État, l'agent de la SNCF et de la RATP, et, depuis l'étape 6,
 * l'agent des industries électriques et gazières, le personnel de l'Opéra
 * national de Paris et l'agent de la SEITA, et, depuis l'étape 8, l'agent
 * titulaire de la Banque de France, dont la prorogation pour enfants est celle
 * de son statut et ne se cumule pas avec la prolongation pour carrière
 * incomplète, ont chacun leur fiche, dont chaque version nomme les exceptions
 * qui jouent pour eux. Depuis l'étape 9, une version peut prêter à l'agent la
 * classe que le modèle lui présume et ne s'atteindre qu'avec des années de
 * services : l'admission d'office de l'agent des IEG avant 2008 (décret
 * n° 54-50). Depuis l'étape 10, le mineur a la sienne, l'âge d'ouverture de sa
 * pension (décret n° 54-51), et reste dans l'intérêt du service, sans borne,
 * présumé maintenu jusqu'au départ saisi ; et les exceptions se lisent au jour
 * où l'agent atteint sa limite, le premier de la version qui la crée quand il
 * l'avait déjà passée.
 *
 * Jumeau de `src/retraite_notionnelle/droit/limite_age.py`, qui fait foi et
 * dit le droit.
 */

import { DateMois } from "../calendrier.js";
import { applicable } from "../versions.js";
import { periodeDeLiquidation } from "./commun.js";
import * as ouvrirLeDroit from "./ouvrir.js";

export const FICHE_DE_LA_LIMITE = "limite_age_fonction_publique";
export const FICHE_DES_MILITAIRES = "limite_age_militaires";
export const FICHE_DES_ENFANTS = "recul_limite_age_enfants";
export const FICHE_DE_LA_CARRIERE_INCOMPLETE = "prolongation_activite_carriere_incomplete";
export const FICHE_DE_L_ACTIF = "prolongation_activite_categorie_active";
export const FICHE_DU_MAINTIEN = "maintien_en_fonctions_jusqu_a_70_ans";
export const FICHE_DU_PLAFOND = "plafond_limite_age_fonction_publique";
export const FICHE_DES_CONTRACTUELS = "limite_age_contractuels";
export const FICHE_DES_OUVRIERS = "limite_age_ouvriers_etat";
export const FICHE_SNCF_RATP = "limite_age_sncf_ratp";
export const FICHE_IEG = "limite_age_ieg";
export const FICHE_OPERA = "limite_age_opera";
export const FICHE_SEITA = "limite_age_seita";
export const FICHE_BANQUE_DE_FRANCE = "limite_age_banque_de_france";
export const FICHE_MINES = "limite_age_mines";
/** Les fiches du code des pensions, fonctionnaires et militaires. */
export const FICHES_DU_CODE_DES_PENSIONS = new Set([FICHE_DE_LA_LIMITE, FICHE_DES_MILITAIRES]);

/** Les régimes du code des pensions, dont l'agent est radié des cadres. */
export const REGIMES_RADIES = new Set(["fonction_publique_etat", "cnracl", "pensions_civiles_1853"]);

export const SEDENTAIRE = "sedentaire";
export const ACTIVE = "active";
export const POLICE_PENITENTIAIRE = "police_penitentiaire";
export const NON_OFFICIER = "non_officier";
export const OFFICIER = "officier";
/** Les statuts de la police nationale et de la surveillance pénitentiaire. */
export const STATUTS_DE_POLICE = new Set(["policier", "fonctionnaire_etat_super_actif"]);
/** Les statuts d'agent contractuel de droit public (L. 556-11 CGFP). */
export const STATUTS_CONTRACTUELS = new Set(["contractuel_public"]);
/** Les régimes dont l'emploi a sa propre limite d'âge, et la fiche qui la porte. */
export const FICHE_DU_REGIME = Object.freeze({
  fspoeie: FICHE_DES_OUVRIERS, sncf: FICHE_SNCF_RATP, ratp: FICHE_SNCF_RATP,
  ieg: FICHE_IEG, opera_de_paris: FICHE_OPERA, seita: FICHE_SEITA,
  banque_de_france: FICHE_BANQUE_DE_FRANCE, mines: FICHE_MINES,
});
/** Le régime dont la durée d'assurance décide la prolongation du contractuel. */
export const REGIME_DU_CONTRACTUEL = "regime_general";

export const RECUL_ENFANTS = "recul_enfants_a_charge";
export const RECUL_PARENT_DE_TROIS = "recul_parent_de_trois_enfants";
export const CARRIERE_INCOMPLETE = "prolongation_carriere_incomplete";
export const PROLONGATION_ACTIVE = "prolongation_categorie_active";
export const MAINTIEN = "maintien_jusqu_a_70_ans";
export const MAINTIEN_DANS_L_INTERET_DU_SERVICE = "maintien_dans_l_interet_du_service";

/** Les exceptions que nomme le paramètre `exceptions` d'une version. */
export const ENFANTS = "enfants";
export const INCOMPLETE = "carriere_incomplete";
export const ACTIF_JUSQU_AUX_SEDENTAIRES = "prolongation_active";
export const JUSQU_A_70_ANS = "maintien";
export const PLAFOND = "plafond";
const TOUTES = new Set([ENFANTS, INCOMPLETE, ACTIF_JUSQU_AUX_SEDENTAIRES, JUSQU_A_70_ANS, PLAFOND]);
/** Le maintien sans borne du mineur (décret n° 54-51, article 3). */
export const INTERET_DU_SERVICE = "interet_du_service";

const MOIS_PAR_AN = 12;
const deux = (n) => String(n).padStart(2, "0");
const militaire = (classe) => classe === NON_OFFICIER || classe === OFFICIER;

function fiche(moteur, nom) {
  return moteur.fichesDatees.fiches()[nom] ?? null;
}

function versionAu(moteur, nom, jour) {
  const lue = fiche(moteur, nom);
  return lue === null ? null : applicable(lue, { age_atteint: jour });
}

const mois = (age) => Math.round(age * MOIS_PAR_AN);

/** Le jour (AAAA-MM-JJ) où l'assuré atteint cet âge, en mois. */
function jourDe(carriere, enMois) {
  const anniversaire = carriere.dateNaissance.plusMois(enMois);
  return `${String(anniversaire.annee).padStart(4, "0")}-${deux(anniversaire.mois)}-`
    + deux(Math.min(carriere.jourDeNaissance, 28));
}

/** L'âge, en mois révolus, à ce jour (AAAA-MM-JJ). */
function moisAu(carriere, jour) {
  const [annee, leMois, quantieme] = jour.split("-").map(Number);
  const naissance = carriere.dateNaissance;
  const ecart = (annee - naissance.annee) * MOIS_PAR_AN + leMois - naissance.mois;
  return ecart - (quantieme < Math.min(carriere.jourDeNaissance, 28) ? 1 : 0);
}

/**
 * La fiche de la limite d'âge d'un statut cette année, et sa classe d'emploi ;
 * `null` pour un statut sans limite d'âge au modèle. Voir `emploi_de` du
 * Python.
 */
export function emploiDe(moteur, affiliation, annee, entree = null) {
  const categorie = moteur.affiliations.pensionMilitaire(affiliation);
  if (categorie !== null) {
    return [FICHE_DES_MILITAIRES, categorie];
  }
  if (STATUTS_CONTRACTUELS.has(affiliation)) {
    return [FICHE_DES_CONTRACTUELS, SEDENTAIRE];
  }
  const regimes = moteur.affiliations.regimes(affiliation, annee, entree);
  const active = moteur.affiliations.categorieActive(affiliation);
  const propre = [...regimes].sort().find((code) => code in FICHE_DU_REGIME);
  if (propre !== undefined) {
    return [FICHE_DU_REGIME[propre], active ? ACTIVE : SEDENTAIRE];
  }
  if (!regimes.some((code) => REGIMES_RADIES.has(code))) {
    return null;
  }
  if (STATUTS_DE_POLICE.has(affiliation)) {
    return [FICHE_DE_LA_LIMITE, POLICE_PENITENTIAIRE];
  }
  return [FICHE_DE_LA_LIMITE, active ? ACTIVE : SEDENTAIRE];
}

/**
 * La classe d'emploi d'un statut, qui choisit sa limite ; `null` pour un
 * statut sans limite d'âge au modèle.
 */
export function classeDe(moteur, affiliation, annee, entree = null) {
  const emploi = emploiDe(moteur, affiliation, annee, entree);
  return emploi === null ? null : emploi[1];
}

/** L'emploi d'une ligne de la carrière, à sa date d'entrée dans le statut. */
function emploiDeLaLigne(moteur, carriere, ligne) {
  return emploiDe(moteur, ligne.affiliation, ligne.annee, carriere.dateEntree(ligne.affiliation));
}

/** Les régimes d'une ligne de la carrière, à sa date d'entrée dans le statut. */
function regimesDeLaLigne(moteur, carriere, ligne) {
  return moteur.affiliations.regimes(ligne.affiliation, ligne.annee,
    carriere.dateEntree(ligne.affiliation));
}

/** Les exceptions que la fiche de la limite ouvre ce jour-là. */
function exceptions(moteur, nom, jour) {
  if (nom === FICHE_DE_LA_LIMITE) {
    return TOUTES;
  }
  const version = versionAu(moteur, nom, jour);
  if (version === null) {
    return new Set();
  }
  const nommees = version.parametres.exceptions;
  return nommees === undefined || nommees === null ? TOUTES : new Set(nommees);
}

/** Les fiches dont la radiation arrête les services. */
function memesEmplois(nom) {
  return FICHES_DU_CODE_DES_PENSIONS.has(nom) ? FICHES_DU_CODE_DES_PENSIONS : new Set([nom]);
}

function ageDeLaVersion(carriere, parametres, classe) {
  const limites = parametres.limites ?? {};
  if (classe in limites) {
    return mois(limites[classe]);
  }
  const avant = parametres.limites_avant ?? {};
  if (!(classe in avant)) {
    return null;
  }
  const ancienne = mois(avant[classe]);
  const repere = jourDe(carriere, ancienne - mois(parametres.ecart_de_reference ?? 0));
  let plus = 0;
  for (const marche of parametres.marche ?? []) {
    if (repere >= marche.depuis) {
      plus = marche.mois;
    }
  }
  return ancienne + plus;
}

function morceaux(carriere, version, classe) {
  const [debut, fin] = version.bornes.age_atteint ?? [null, null];
  const parametres = version.parametres;
  const liste = [[debut, fin, ageDeLaVersion(carriere, parametres, classe)]];
  for (const palier of parametres.paliers ?? []) {
    if (!(classe in palier)) {
      continue;
    }
    const precedent = liste.pop();
    liste.push([precedent[0], palier.depuis, precedent[2]]);
    liste.push([palier.depuis, fin, mois(palier[classe])]);
  }
  return liste.filter(([, , m]) => m !== null);
}

/**
 * La limite, en mois, d'une version qui demande des années de services dans
 * l'emploi (`services_requis`), celle du décret n° 54-50. Voir
 * `_au_terme_des_services` du Python.
 */
function auTermeDesServices(moteur, carriere, nom, enMois, parametres) {
  const statuts = new Set();
  for (const ligne of carriere.lignes) {
    const emploi = emploiDeLaLigne(moteur, carriere, ligne);
    if (emploi !== null && emploi[0] === nom) {
      statuts.add(ligne.affiliation);
    }
  }
  const plafond = mois(parametres.a_defaut_des_services);
  const reunis = carriere.dateDeService(statuts, parametres.services_requis);
  if (reunis === null) {
    return plafond;
  }
  return Math.min(Math.max(enMois, mois(carriere.ageAu(reunis.plusMois(1)))), plafond);
}

/**
 * La limite d'âge de cette classe, en mois, la version qui la donne, et le jour
 * où l'agent l'atteint, son anniversaire ou le premier jour de la version qui
 * la crée ; une version peut prêter à l'agent la classe que le modèle lui
 * présume (`classe_presumee`), et ne s'atteindre qu'avec des années de services.
 */
function limiteDe(moteur, carriere, nom, classe) {
  const lue = fiche(moteur, nom);
  if (lue === null) {
    return null;
  }
  const debutDe = (v) => (v.bornes.age_atteint ?? [null])[0] ?? "";
  const ordre = [...lue.versions].sort((a, b) => {
    const [x, y] = [debutDe(a), debutDe(b)];
    return x < y ? -1 : x > y ? 1 : 0;
  });
  for (const version of ordre) {
    const parametres = version.parametres;
    for (let [debut, fin, m] of morceaux(carriere, version, parametres.classe_presumee ?? classe)) {
      if (parametres.services_requis !== undefined) {
        m = auTermeDesServices(moteur, carriere, nom, m, parametres);
      }
      let jour = jourDe(carriere, m);
      if (debut !== null && jour < debut) {
        jour = debut;
      }
      if (fin === null || jour < fin) {
        return [Math.max(m, moisAu(carriere, jour)), version.id, jour];
      }
    }
  }
  return null;
}

function enfantsACharge(carriere, jour, ageACharge) {
  const seuil = `${String(Number(jour.slice(0, 4)) - Math.trunc(ageACharge)).padStart(4, "0")}`
    + jour.slice(4);
  return carriere.naissancesDesEnfants
    .filter(([, naissance]) => seuil < naissance && naissance <= jour).length;
}

function recul(nom, ficheDuRecul, version, depuis, jusquA, presumee) {
  return Object.freeze({ nom, fiche: ficheDuRecul, version, depuis, jusqu_a: jusquA, presumee });
}

/**
 * La prorogation pour enfants qu'un statut écrit lui-même (paramètre `enfants`
 * de la version de la limite), celle de la Banque de France. Voir
 * `_prorogation_du_statut` du Python.
 */
function prorogationDuStatut(carriere, limite, nom, version, p, jour) {
  const aCharge = enfantsACharge(carriere, jour, p.age_a_charge);
  const annees = Math.trunc(Math.max(p.age_a_charge, p.eleves_jusqu_a));
  const seuil = `${String(Number(jour.slice(0, 4)) - annees).padStart(4, "0")}${jour.slice(4)}`;
  const eleves = carriere.naissancesDesEnfants.filter(([, naissance]) => naissance <= seuil).length;
  const ans = Math.max(0, ...p.prorogations
    .filter((q) => aCharge >= q.a_charge && eleves >= (q.eleves ?? 0)).map((q) => q.ans));
  const valeur = mois(Math.min(ans, p.au_plus));
  if (valeur <= 0) {
    return null;
  }
  return recul(RECUL_ENFANTS, nom, version.id, limite / MOIS_PAR_AN,
    (limite + valeur) / MOIS_PAR_AN, false);
}

/** Le recul de droit pour enfants, au jour `jour` où la limite est atteinte. */
function reculsPourEnfants(moteur, carriere, limite, classe, nomDeLaLimite, jour) {
  if (militaire(classe)) {
    return null;
  }
  const propre = FICHES_DU_CODE_DES_PENSIONS.has(nomDeLaLimite)
    ? null : versionAu(moteur, nomDeLaLimite, jour);
  if (propre !== null && propre.parametres.enfants) {
    return prorogationDuStatut(carriere, limite, nomDeLaLimite, propre, propre.parametres.enfants,
      jour);
  }
  const version = versionAu(moteur, FICHE_DES_ENFANTS, jour);
  if (version === null || Object.keys(version.parametres).length === 0) {
    return null;
  }
  const p = version.parametres;
  const groupe = classe === SEDENTAIRE ? SEDENTAIRE : ACTIVE;
  const plafonne = (valeur, plafonds) => {
    const plafond = (plafonds ?? {})[groupe];
    return plafond === undefined || plafond === null
      ? valeur : Math.min(valeur, Math.max(0, mois(plafond) - limite));
  };
  const aCharge = enfantsACharge(carriere, jour, p.age_a_charge);
  const parEnfant = plafonne(mois(Math.min(aCharge, p.enfants_au_plus) * p.par_enfant),
    p.plafond_par_enfant);
  const cinquante = jourDe(carriere, mois(p.age_du_parent));
  const nes = carriere.naissancesDesEnfants.filter(([, naissance]) => naissance <= cinquante).length;
  const parent = nes >= p.enfants_du_parent
    ? plafonne(mois(p.parent_de_trois), p.plafond_du_parent) : 0;
  const [valeur, nom] = parent > parEnfant
    ? [parent, RECUL_PARENT_DE_TROIS] : [parEnfant, RECUL_ENFANTS];
  if (valeur <= 0) {
    return null;
  }
  return recul(nom, FICHE_DES_ENFANTS, version.id, limite / MOIS_PAR_AN,
    (limite + valeur) / MOIS_PAR_AN, false);
}

function prolongationCarriereIncomplete(moteur, carriere, depuis, affiliations, regime, nom, jour) {
  // Lue au jour `jour` où l'agent atteint l'âge `depuis`. La version de la
  // limite qui porte `incomplete_au_dela_de`, celle des industries électriques
  // et gazières, borne la prolongation à la durée du taux maximum moins ce
  // nombre de trimestres.
  const propre = FICHES_DU_CODE_DES_PENSIONS.has(nom) ? null : versionAu(moteur, nom, jour);
  const auDelaDe = propre?.parametres?.incomplete_au_dela_de ?? null;
  let fiche = nom;
  let version = propre;
  if (auDelaDe === null) {
    fiche = FICHE_DE_LA_CARRIERE_INCOMPLETE;
    version = versionAu(moteur, FICHE_DE_LA_CARRIERE_INCOMPLETE, jour);
    if (version === null || !version.parametres.trimestres_au_plus) {
      return null;
    }
  }
  if (regime === null || !moteur.catalogue.contient(regime)) {
    return null;
  }
  const date = carriere.dateDeLAge(depuis / MOIS_PAR_AN);
  const periode = periodeDeLiquidation(moteur.catalogue.obtenir(regime), date);
  if (periode === null || periode === undefined) {
    return null;
  }
  const requis = ouvrirLeDroit.dureeRequise(moteur, periode, carriere.liquideeAu(date))[0];
  const services = carriere.dureeDeServiceAvant(affiliations, date);
  const manque = Math.ceil((requis / 4 - services) * MOIS_PAR_AN - 1e-9);
  const auPlus = auDelaDe !== null ? requis - auDelaDe : version.parametres.trimestres_au_plus;
  const prolongation = Math.min(manque, auPlus * 3);
  if (prolongation <= 0) {
    return null;
  }
  return recul(CARRIERE_INCOMPLETE, fiche, version.id,
    depuis / MOIS_PAR_AN, (depuis + prolongation) / MOIS_PAR_AN, true);
}

/** La prolongation de l'actif ou le maintien du sédentaire, lus au jour `jour`. */
function jusquALaLimite(moteur, carriere, depuis, classe, nomDeLaLimite, jour) {
  let version;
  let cible = null;
  let nom;
  let ficheDuRecul;
  if (classe === SEDENTAIRE) {
    version = versionAu(moteur, FICHE_DU_MAINTIEN, jour);
    const age = version === null ? null : (version.parametres.jusqu_a ?? null);
    cible = age === null ? null : mois(age);
    [nom, ficheDuRecul] = [MAINTIEN, FICHE_DU_MAINTIEN];
  } else {
    version = versionAu(moteur, FICHE_DE_L_ACTIF, jour);
    if (version === null || version.parametres.jusqu_a !== SEDENTAIRE) {
      return null;
    }
    const lue = limiteDe(moteur, carriere, nomDeLaLimite, SEDENTAIRE);
    cible = lue === null ? null : lue[0];
    [nom, ficheDuRecul] = [PROLONGATION_ACTIVE, FICHE_DE_L_ACTIF];
  }
  if (cible === null || cible <= depuis) {
    return null;
  }
  return recul(nom, ficheDuRecul, version.id, depuis / MOIS_PAR_AN, cible / MOIS_PAR_AN, true);
}

function lignesRadiees(moteur, carriere) {
  return carriere.lignes.filter((ligne) => ligne.annee <= carriere.anneeLiquidation
    && emploiDeLaLigne(moteur, carriere, ligne) !== null);
}

/**
 * La radiation des cadres par limite d'âge de `carriere`, ou `null` quand ses
 * services de fonctionnaire ou de militaire finissent avant sa limite, ou
 * qu'elle n'en a pas. Voir `radiation` du Python.
 */
export function radiation(moteur, carriere) {
  if (carriere.age_liquidation === null || carriere.age_liquidation === undefined) {
    return null;
  }
  const lignes = lignesRadiees(moteur, carriere).filter((ligne) => ligne.cotise);
  if (lignes.length === 0) {
    return null;
  }
  let derniere = lignes[0];
  for (const ligne of lignes) {
    if (ligne.annee > derniere.annee) {
      derniere = ligne;
    }
  }
  const affiliation = derniere.affiliation;
  const [nom, classe] = emploiDeLaLigne(moteur, carriere, derniere);
  const declare = carriere.dateLiquidation;
  const fin = derniere.annee >= declare.annee ? declare : new DateMois(derniere.annee + 1, 1);
  const lue = limiteDe(moteur, carriere, nom, classe);
  if (lue === null) {
    return null;
  }
  const [limite, version, jourLimite] = lue;
  if (carriere.dateDeLAge(limite / MOIS_PAR_AN).rang >= fin.rang) {
    return null;
  }
  // Le jour où l'agent atteint cet âge, jamais avant celui où il atteint sa
  // limite, qu'une version a pu créer après son anniversaire.
  const au = (enMois) => {
    const jour = jourDe(carriere, enMois);
    return jour > jourLimite ? jour : jourLimite;
  };
  // Les services de l'emploi : ceux du code des pensions ensemble, ceux de la
  // même fiche pour les autres, dont la radiation ouvre tous les régimes.
  const codeDesPensions = FICHES_DU_CODE_DES_PENSIONS.has(nom);
  const memes = memesEmplois(nom);
  const services = lignes.filter((ligne) => memes.has(emploiDeLaLigne(moteur, carriere, ligne)[0]));
  const regimes = new Set();
  for (const ligne of services) {
    for (const code of regimesDeLaLigne(moteur, carriere, ligne)) {
      if (REGIMES_RADIES.has(code) || !codeDesPensions) {
        regimes.add(code);
      }
    }
  }
  let candidats = [];
  if (!militaire(classe)) {
    let civiles;
    let regime;
    if (nom === FICHE_DES_CONTRACTUELS) {
      civiles = new Set(carriere.lignes.filter((ligne) => ligne.cotise)
        .map((ligne) => ligne.affiliation));
      regime = REGIME_DU_CONTRACTUEL;
    } else {
      civiles = new Set(services
        .filter((ligne) => !militaire(emploiDeLaLigne(moteur, carriere, ligne)[1]))
        .map((ligne) => ligne.affiliation));
      const propre = (code) => (codeDesPensions ? REGIMES_RADIES.has(code) : code in FICHE_DU_REGIME);
      regime = [...regimesDeLaLigne(moteur, carriere, derniere)].sort().find(propre) ?? null;
    }
    let atteint = limite;
    const enfants = exceptions(moteur, nom, au(atteint)).has(ENFANTS)
      ? reculsPourEnfants(moteur, carriere, atteint, classe, nom, au(atteint)) : null;
    if (enfants !== null) {
      candidats.push(enfants);
      atteint = mois(enfants.jusqu_a);
    }
    // Sans cumul (Banque de France, article 242-1), la prolongation part de
    // la limite, et seule la plus longue des deux exceptions reste.
    const deLaLimite = codeDesPensions ? null : versionAu(moteur, nom, jourLimite);
    const sansCumul = Boolean(deLaLimite && deLaLimite.parametres.sans_cumul);
    const depuis = sansCumul ? limite : atteint;
    let incomplete = exceptions(moteur, nom, au(depuis)).has(INCOMPLETE)
      ? prolongationCarriereIncomplete(moteur, carriere, depuis, civiles, regime, nom, au(depuis))
      : null;
    if (incomplete !== null && sansCumul && enfants !== null) {
      if (incomplete.jusqu_a > enfants.jusqu_a) {
        candidats = candidats.filter((r) => r !== enfants);
      } else {
        incomplete = null;
      }
    }
    if (incomplete !== null) {
      candidats.push(incomplete);
      atteint = mois(incomplete.jusqu_a);
    }
    const ouvertes = exceptions(moteur, nom, au(atteint));
    const prolongee = ouvertes.has(classe === SEDENTAIRE ? JUSQU_A_70_ANS : ACTIF_JUSQU_AUX_SEDENTAIRES)
      ? jusquALaLimite(moteur, carriere, atteint, classe, nom, au(atteint)) : null;
    if (prolongee !== null) {
      candidats.push(prolongee);
      atteint = mois(prolongee.jusqu_a);
    }
    // Le maintien dans l'intérêt du service du mineur (décret n° 54-51,
    // article 3), sans borne : présumé accordé jusqu'au départ saisi, il ne
    // laisse jamais la limite radier.
    if (exceptions(moteur, nom, au(atteint)).has(INTERET_DU_SERVICE)) {
      const jusquAuDepart = mois(carriere.ageAu(declare));
      if (jusquAuDepart > atteint) {
        candidats.push(recul(MAINTIEN_DANS_L_INTERET_DU_SERVICE, nom,
          versionAu(moteur, nom, au(atteint)).id, atteint / MOIS_PAR_AN,
          jusquAuDepart / MOIS_PAR_AN, true));
        atteint = jusquAuDepart;
      }
    }
    const plafond = exceptions(moteur, nom, au(atteint)).has(PLAFOND)
      ? versionAu(moteur, FICHE_DU_PLAFOND, au(atteint)) : null;
    const maximum = plafond === null ? null : (plafond.parametres.age_maximal ?? null);
    if (maximum !== null) {
      const plafonne = Math.max(mois(maximum), limite);
      candidats = candidats
        .filter((r) => mois(r.depuis) < plafonne)
        .map((r) => recul(r.nom, r.fiche, r.version, r.depuis,
          Math.min(r.jusqu_a, plafonne / MOIS_PAR_AN), r.presumee));
    }
  }
  const ouverte = Math.max(limite, ...candidats.map((r) => mois(r.jusqu_a)));
  const auPlusTard = carriere.dateDeLAge(ouverte / MOIS_PAR_AN);
  const date = fin.rang < auPlusTard.rang ? fin : auPlusTard;
  const age = carriere.ageAu(date);
  const reculs = candidats
    .filter((r) => carriere.dateDeLAge(r.depuis).rang < date.rang)
    .map((r) => recul(r.nom, r.fiche, r.version, r.depuis, Math.min(r.jusqu_a, age), r.presumee));
  return Object.freeze({
    date,
    age,
    limite: limite / MOIS_PAR_AN,
    classe,
    affiliation,
    version,
    regimes,
    reculs,
    presumees: reculs.filter((r) => r.presumee),
    forcee: auPlusTard.rang <= fin.rang && auPlusTard.rang < declare.rang,
    fiche: nom,
  });
}

/**
 * La carrière dont les services de l'emploi radié s'arrêtent à la radiation
 * par limite d'âge, quand elle précède leur fin déclarée ; rendue
 * telle quelle sinon. Voir `radier` du Python.
 */
export function radier(moteur, carriere) {
  const radiee = radiation(moteur, carriere);
  if (radiee === null || !radiee.forcee) {
    return carriere;
  }
  const derniere = radiee.date.annee - (radiee.date.mois === 1 ? 1 : 0);
  const memes = memesEmplois(radiee.fiche);
  const deLEmploi = (ligne) => {
    const emploi = emploiDeLaLigne(moteur, carriere, ligne);
    return emploi !== null && memes.has(emploi[0]);
  };
  const gardees = carriere.lignes.filter((ligne) => ligne.annee <= derniere || !deLEmploi(ligne));
  if (gardees.length === carriere.lignes.length) {
    return carriere;
  }
  return carriere.avecLignes(gardees);
}
