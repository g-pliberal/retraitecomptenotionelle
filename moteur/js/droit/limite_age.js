/**
 * La limite d'âge des fonctionnaires, et ses exceptions (action 151, étape 3).
 *
 * Le fonctionnaire est radié des cadres à la limite d'âge de son emploi,
 * reculée de droit pour ses enfants, prolongée — présumée demandée et accordée
 * autant que le départ saisi le demande — pour carrière incomplète, pour
 * l'actif jusqu'à la limite des sédentaires, et pour le sédentaire jusqu'à
 * soixante-dix ans ; depuis le 14 juin 2023, pas au-delà de soixante-dix ans.
 * Le militaire prend la limite la plus haute de sa catégorie. Sa pension part
 * de la radiation, et ce qui suit n'est plus du service.
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

/** Les régimes du code des pensions, dont l'agent est radié des cadres. */
export const REGIMES_RADIES = new Set(["fonction_publique_etat", "cnracl", "pensions_civiles_1853"]);

export const SEDENTAIRE = "sedentaire";
export const ACTIVE = "active";
export const POLICE_PENITENTIAIRE = "police_penitentiaire";
export const NON_OFFICIER = "non_officier";
export const OFFICIER = "officier";
/** Les statuts de la police nationale et de la surveillance pénitentiaire. */
export const STATUTS_DE_POLICE = new Set(["policier", "fonctionnaire_etat_super_actif"]);

export const RECUL_ENFANTS = "recul_enfants_a_charge";
export const RECUL_PARENT_DE_TROIS = "recul_parent_de_trois_enfants";
export const CARRIERE_INCOMPLETE = "prolongation_carriere_incomplete";
export const PROLONGATION_ACTIVE = "prolongation_categorie_active";
export const MAINTIEN = "maintien_jusqu_a_70_ans";

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
 * La classe d'emploi d'un statut, qui choisit sa limite ; `null` pour un
 * statut sans limite d'âge au modèle.
 */
export function classeDe(moteur, affiliation, annee) {
  const categorie = moteur.affiliations.pensionMilitaire(affiliation);
  if (categorie !== null) {
    return categorie;
  }
  if (!moteur.affiliations.regimes(affiliation, annee).some((code) => REGIMES_RADIES.has(code))) {
    return null;
  }
  if (STATUTS_DE_POLICE.has(affiliation)) {
    return POLICE_PENITENTIAIRE;
  }
  return moteur.affiliations.categorieActive(affiliation) ? ACTIVE : SEDENTAIRE;
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

/** La limite d'âge de cette classe, en mois, et la version qui la donne. */
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
    for (const [debut, fin, m] of morceaux(carriere, version, classe)) {
      let jour = jourDe(carriere, m);
      if (debut !== null && jour < debut) {
        jour = debut;
      }
      if (fin === null || jour < fin) {
        return [Math.max(m, moisAu(carriere, jour)), version.id];
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

function reculsPourEnfants(moteur, carriere, limite, classe) {
  if (militaire(classe)) {
    return null;
  }
  const jour = jourDe(carriere, limite);
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

function prolongationCarriereIncomplete(moteur, carriere, depuis, affiliations, regime) {
  const version = versionAu(moteur, FICHE_DE_LA_CARRIERE_INCOMPLETE, jourDe(carriere, depuis));
  if (version === null || !version.parametres.trimestres_au_plus) {
    return null;
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
  const prolongation = Math.min(manque, version.parametres.trimestres_au_plus * 3);
  if (prolongation <= 0) {
    return null;
  }
  return recul(CARRIERE_INCOMPLETE, FICHE_DE_LA_CARRIERE_INCOMPLETE, version.id,
    depuis / MOIS_PAR_AN, (depuis + prolongation) / MOIS_PAR_AN, true);
}

function jusquALaLimite(moteur, carriere, depuis, classe) {
  const jour = jourDe(carriere, depuis);
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
    const lue = limiteDe(moteur, carriere, FICHE_DE_LA_LIMITE, SEDENTAIRE);
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
    && classeDe(moteur, ligne.affiliation, ligne.annee) !== null);
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
  const classe = classeDe(moteur, affiliation, derniere.annee);
  const declare = carriere.dateLiquidation;
  const fin = derniere.annee >= declare.annee ? declare : new DateMois(derniere.annee + 1, 1);
  const lue = limiteDe(moteur, carriere,
    militaire(classe) ? FICHE_DES_MILITAIRES : FICHE_DE_LA_LIMITE, classe);
  if (lue === null) {
    return null;
  }
  const [limite, version] = lue;
  if (carriere.dateDeLAge(limite / MOIS_PAR_AN).rang >= fin.rang) {
    return null;
  }
  const regimes = new Set();
  for (const ligne of lignes) {
    for (const code of moteur.affiliations.regimes(ligne.affiliation, ligne.annee)) {
      if (REGIMES_RADIES.has(code)) {
        regimes.add(code);
      }
    }
  }
  let candidats = [];
  if (!militaire(classe)) {
    const civiles = new Set(lignes
      .filter((ligne) => !militaire(classeDe(moteur, ligne.affiliation, ligne.annee)))
      .map((ligne) => ligne.affiliation));
    const regime = [...moteur.affiliations.regimes(affiliation, derniere.annee)]
      .sort().find((code) => REGIMES_RADIES.has(code)) ?? null;
    let atteint = limite;
    const enfants = reculsPourEnfants(moteur, carriere, atteint, classe);
    if (enfants !== null) {
      candidats.push(enfants);
      atteint = mois(enfants.jusqu_a);
    }
    const incomplete = prolongationCarriereIncomplete(moteur, carriere, atteint, civiles, regime);
    if (incomplete !== null) {
      candidats.push(incomplete);
      atteint = mois(incomplete.jusqu_a);
    }
    const prolongee = jusquALaLimite(moteur, carriere, atteint, classe);
    if (prolongee !== null) {
      candidats.push(prolongee);
      atteint = mois(prolongee.jusqu_a);
    }
    const plafond = versionAu(moteur, FICHE_DU_PLAFOND, jourDe(carriere, atteint));
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
  });
}

/**
 * La carrière dont les services de fonctionnaire ou de militaire s'arrêtent à
 * la radiation par limite d'âge, quand elle précède leur fin déclarée ; rendue
 * telle quelle sinon. Voir `radier` du Python.
 */
export function radier(moteur, carriere) {
  const radiee = radiation(moteur, carriere);
  if (radiee === null || !radiee.forcee) {
    return carriere;
  }
  const derniere = radiee.date.annee - (radiee.date.mois === 1 ? 1 : 0);
  const gardees = carriere.lignes.filter((ligne) => ligne.annee <= derniere
    || classeDe(moteur, ligne.affiliation, ligne.annee) === null);
  if (gardees.length === carriere.lignes.length) {
    return carriere;
  }
  return carriere.avecLignes(gardees);
}
