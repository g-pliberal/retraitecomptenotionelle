/**
 * Les taux pleins par catégorie de L. 351-8 : l'ancien déporté ou interné
 * (3°), la mère de famille ouvrière (4°), le travailleur manuel d'avant 1983
 * (décret n° 45-0179, article 70-2, a), l'ancien combattant ou prisonnier de
 * guerre (5° ; D. 351-2), que les fiches `taux_plein_*` datent.
 *
 * Jumeau de `src/retraite_notionnelle/droit/categories.py`, fonction pour
 * fonction.
 */

import { dateDEffet } from "./commun.js";

/** Les fiches des catégories, dans l'ordre où le moteur les essaie. */
export const FICHE_DES_DEPORTES = "taux_plein_anciens_deportes_internes";
export const FICHE_DES_MERES_OUVRIERES = "taux_plein_meres_de_famille_ouvrieres";
export const FICHE_DES_TRAVAILLEURS_MANUELS = "taux_plein_travailleurs_manuels";
export const FICHE_DES_ANCIENS_COMBATTANTS = "taux_plein_anciens_combattants_prisonniers";
export const FICHES_DES_CATEGORIES = Object.freeze([
  FICHE_DES_DEPORTES, FICHE_DES_MERES_OUVRIERES, FICHE_DES_TRAVAILLEURS_MANUELS,
  FICHE_DES_ANCIENS_COMBATTANTS,
]);

/** L'âge qu'une version écrit pour dire l'âge légal de la génération. */
export const AGE_LEGAL = "age_legal_par_generation";

/** L'âge de L. 161-17-2 de la génération. */
export function ageLegal(moteur, carriere) {
  const lu = moteur.agesOuverture.age(carriere.generation);
  return lu !== null ? lu[0] : 60.0;
}

/** L'âge du 1° de L. 351-8, où la décote s'annule, de la génération. */
export function ageDuTauxPlein(moteur, carriere) {
  const lu = moteur.agesAnnulationDecote.age(carriere.generation);
  return lu !== null ? lu[0] : 65.0;
}

/**
 * L'âge dès lequel l'ancien combattant ou prisonnier de guerre a le taux plein,
 * selon les mois de sa captivité et de ses services militaires en temps de
 * guerre ; `null` sous le premier palier. Voir `age_des_anciens_combattants`
 * du Python.
 */
export function ageDesAnciensCombattants(moteur, regle, carriere, mois) {
  let retenu = null;
  for (const palier of regle.paliers) {
    if (mois >= Math.trunc(Number(palier.des_mois))) {
      retenu = palier;
    }
  }
  if (retenu === null) {
    return null;
  }
  const depuis = retenu.age_legal_des_la_generation ?? null;
  let age;
  if (retenu.age === AGE_LEGAL
      || (depuis !== null && carriere.annee_naissance >= Math.trunc(Number(depuis)))) {
    age = ageLegal(moteur, carriere);
  } else if (retenu.age !== undefined && retenu.age !== null) {
    age = Number(retenu.age);
  } else {
    age = ageDuTauxPlein(moteur, carriere) - Number(retenu.avant_l_age_du_taux_plein);
  }
  const decalage = regle.decalage_age_legal ?? null;
  if (decalage !== null) {
    age += Math.max(0.0, Math.min(ageLegal(moteur, carriere) - 60.0, Number(decalage.au_plus)));
  }
  return Math.max(age, Number(regle.age_minimum ?? 0.0));
}

/**
 * La pension prend-elle effet à l'âge que la version écrit, quand elle en
 * écrit un ? Sans âge, celui où la pension s'ouvre suffit.
 */
function ageAtteint(moteur, carriere, regle, ageLiquidation) {
  const age = regle.age ?? null;
  if (age === null) {
    return true;
  }
  const seuil = age === AGE_LEGAL ? ageLegal(moteur, carriere) : Number(age);
  return ageLiquidation + 1e-9 >= seuil;
}

/**
 * L'assuré remplit-il, à la date d'effet, les conditions que la version de la
 * fiche `nom` écrit ? Voir `remplit` du Python.
 */
export function remplit(moteur, nom, regle, carriere, durees, ageLiquidation) {
  if (nom === FICHE_DES_DEPORTES) {
    return carriere.deporteOuInterne && ageAtteint(moteur, carriere, regle, ageLiquidation);
  }
  if (nom === FICHE_DES_ANCIENS_COMBATTANTS) {
    const mois = carriere.moisDeGuerre;
    if (!mois) {
      return false;
    }
    const age = ageDesAnciensCombattants(moteur, regle, carriere, mois);
    return age !== null && ageLiquidation + 1e-9 >= age;
  }
  const travail = carriere.travailManuel;
  if (travail === null || !regle.travaux.includes(travail) || durees === null) {
    return false;
  }
  if (nom === FICHE_DES_MERES_OUVRIERES
      && (carriere.sexe !== "F" || carriere.nombre_enfants < Math.trunc(Number(regle.enfants)))) {
    return false;
  }
  return durees.cumulPlafonne("assurance", regle.regimes_de_la_duree)
      >= Math.trunc(Number(regle.trimestres))
    && ageAtteint(moteur, carriere, regle, ageLiquidation);
}

/**
 * La fiche de la catégorie de L. 351-8 qui donne à l'assuré le taux plein dans
 * `regime`, à la date d'effet de sa pension, ou `null`. Voir
 * `taux_plein_par_categorie` du Python.
 */
export function tauxPleinParCategorie(moteur, regime, carriere, durees, ageLiquidation) {
  const date = dateDEffet(carriere);
  if (date === null || !carriere.titresAuTauxPlein) {
    return null;
  }
  for (const nom of FICHES_DES_CATEGORIES) {
    const regle = moteur.fichesDatees.regle(nom, date);
    if (regle && regle.existe && regle.regimes.includes(regime)
        && remplit(moteur, nom, regle, carriere, durees, ageLiquidation)) {
      return nom;
    }
  }
  return null;
}
