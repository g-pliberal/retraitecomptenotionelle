/**
 * Les taux pleins par catégorie de L. 351-8 : l'ancien déporté ou interné
 * (3°), la mère de famille ouvrière (4°), le travailleur manuel d'avant 1983
 * (décret n° 45-0179, article 70-2, a), l'ancien combattant ou prisonnier de
 * guerre (5° ; D. 351-2), que les fiches `taux_plein_*` datent.
 *
 * Et l'âge du 1° de L. 351-8 que le IV de l'article 20 de la loi n° 2010-1330
 * fixe à soixante-cinq ans au parent de trois enfants né du 1er juillet 1951
 * au 31 décembre 1955 (fiche `taux_plein_a_soixante_cinq_ans`).
 *
 * Jumeau de `src/retraite_notionnelle/droit/categories.py`, fonction pour
 * fonction.
 */

import * as chrono from "../chronologie.js";
import { dateDEffet, ligneCotisee } from "./commun.js";

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
 * L'assuré relève-t-il, à la date d'effet, de l'une des catégories `noms`, aux
 * conditions que la fiche de chacune écrit ce jour-là, quel que soit le régime
 * qu'elle nomme ? Une section libérale y renvoie : « les conditions d'âge et de
 * durée de service prévues par la loi n° 73-1051 », « les personnes
 * mentionnées au 5° de l'article L. 351-8 ». Voir `remplit_l_une_de` du Python.
 */
export function remplitLUneDe(moteur, noms, carriere, durees, ageLiquidation) {
  const date = dateDEffet(carriere);
  if (date === null || !carriere.titresAuTauxPlein) {
    return false;
  }
  for (const nom of noms) {
    const regle = moteur.fichesDatees.regle(nom, date);
    if (regle && regle.existe && remplit(moteur, nom, regle, carriere, durees, ageLiquidation)) {
      return true;
    }
  }
  return false;
}

/** La fiche de l'âge de soixante-cinq ans du parent de trois enfants. */
export const FICHE_DES_SOIXANTE_CINQ_ANS = "taux_plein_a_soixante_cinq_ans";

/**
 * Ce que le décret n° 2011-620, article 2, 1°, écarte des années qui suivent
 * la naissance : la pension d'invalidité et l'accident du travail (R. 351-12,
 * 3° et 5°) ; l'AVPF (L. 381-1) se reconnaît au salaire que la ligne porte.
 */
const ECARTEES_APRES = new Set(["invalidite", "accident_travail"]);

/**
 * Ce qu'il compte dans les deux années qui la précèdent : « les trimestres
 * validés en contrepartie de cotisations à la charge de l'assuré ou au titre
 * de périodes d'arrêt maladie, de maternité, de chômage ». L'emploi n'y entre
 * que cotisé (`commun.ligneCotisee`) : l'activité cultuelle d'avant 1979, que
 * D. 721-11 du code de 1985 prend en compte, dont la CAVIMAC dit les trimestres
 * « validés à titre gratuit » (sa page « Demander ma retraite de base »), n'en
 * est pas.
 */
const RETENUES_AVANT = new Set([
  "emploi", "maladie", "maternite", "chomage_indemnise", "chomage_solidarite",
  "chomage_non_indemnise", "preretraite_fne",
]);

/**
 * L'assuré remplit-il, pour l'enfant né à `naissance` (un fait déclaré de la
 * chronologie), les deux conditions du décret n° 2011-620, article 2 ? Au plus
 * `apres_au_plus` trimestres l'année de la naissance et les deux suivantes, ou
 * les trois suivantes pour l'enfant né au second semestre ; au moins
 * `avant_au_moins` les deux années qui la précèdent ; et `activite_au_moins`
 * trimestres d'emploi avant elle, ceux de son année comptés jusqu'au dernier
 * jour du trimestre civil qui la précède (circulaire Cnav n° 2014-64, point
 * 2.2.2). Dite à l'année seule, la naissance n'en ouvre le droit que si les
 * conditions tiennent quel que soit son mois. Voir `_remplit_pour_l_enfant` du
 * Python.
 */
function remplitPourLEnfant(moteur, carriere, parents, naissance) {
  const annee = chrono.anneeDe(naissance.debut);
  const auMois = (naissance.attributs?.precision || "jour") !== "annee";
  const mois = auMois ? chrono.moisDe(naissance.debut).mois : 1;
  const parAnnee = (garder) => carriere.trimestresParAnnee(carriere.lignes.filter(garder));
  const somme = (table, debut, nombre) => {
    let total = 0;
    for (let rang = 0; rang < nombre; rang += 1) {
      total += table.get(debut + rang) ?? 0;
    }
    return total;
  };
  const avant = parAnnee((ligne) => RETENUES_AVANT.has(ligne.type_periode)
    && !(ligne.revenu_avpf > 0)
    && (ligne.type_periode !== "emploi" || ligneCotisee(moteur, carriere, ligne)));
  if (somme(avant, annee - 2, 2) < Number(parents.avant_au_moins)) {
    return false;
  }
  const apres = parAnnee((ligne) => !ECARTEES_APRES.has(ligne.type_periode)
    && !(ligne.revenu_avpf > 0));
  const debuts = auMois ? [mois <= 6 ? annee : annee + 1] : [annee, annee + 1];
  if (debuts.some((debut) => somme(apres, debut, 3) > Number(parents.apres_au_plus))) {
    return false;
  }
  const activite = parAnnee((ligne) => ligne.type_periode === "emploi");
  let anterieure = Math.min(activite.get(annee) ?? 0, Math.floor((mois - 1) / 3));
  for (const [an, trimestres] of activite) {
    if (an < annee) {
      anterieure += trimestres;
    }
  }
  return anterieure >= Number(parents.activite_au_moins);
}

/**
 * L'âge du 1° de L. 351-8 que la fiche `taux_plein_a_soixante_cinq_ans` fixe
 * à l'assuré dans `regime`, à la date d'effet de sa pension, quand il remplit
 * les conditions du parent de trois enfants — né dans les générations de la
 * version, ayant eu ou élevé ses enfants, et, pour l'un d'eux dont la
 * naissance est déclarée, {@link remplitPourLEnfant} — ; `null` sinon. Voir
 * `age_du_parent_de_trois_enfants` du Python.
 */
export function ageDuParentDeTroisEnfants(moteur, regime, carriere) {
  const regle = regleDuParent(moteur, carriere);
  if (regle === null || !regle.regimes.includes(regime)) {
    return null;
  }
  return pourUnEnfantDeclare(carriere, (naissance) => remplitPourLEnfant(
    moteur, carriere, regle.parents_de_trois_enfants, naissance)) ? Number(regle.age) : null;
}

/**
 * La version de la fiche `taux_plein_a_soixante_cinq_ans` à la date d'effet de
 * la pension, quand l'assuré est né dans ses générations et a ses enfants ;
 * `null` sinon. Voir `_regle_du_parent` du Python.
 */
function regleDuParent(moteur, carriere) {
  const date = dateDEffet(carriere);
  if (date === null) {
    return null;
  }
  const regle = moteur.fichesDatees.regle(FICHE_DES_SOIXANTE_CINQ_ANS, date);
  const parents = regle?.parents_de_trois_enfants ?? null;
  if (!regle || !regle.existe || parents === null) {
    return null;
  }
  const rang = carriere.annee_naissance * 12 + carriere.mois_naissance;
  const [anneeDu, moisDu] = parents.nes_du;
  const [anneeAu, moisAu] = parents.nes_au;
  if (rang < anneeDu * 12 + moisDu || rang > anneeAu * 12 + moisAu
      || carriere.nombre_enfants < Math.trunc(Number(parents.enfants))) {
    return null;
  }
  return regle;
}

/** L'un des enfants dont la saisie déclare la naissance la fait-il remplir ? */
function pourUnEnfantDeclare(carriere, remplit) {
  for (const enfant of chrono.enfants(carriere.chronologie, carriere.personne)) {
    const naissance = chrono.naissance(carriere.chronologie, enfant);
    if (naissance !== null && naissance.origine === "declare" && remplit(naissance)) {
      return true;
    }
  }
  return false;
}

/**
 * Le fonctionnaire remplit-il, pour l'enfant né à `naissance`, les conditions
 * de R. 26 ter, I, du code des pensions (loi n° 2010-1330, article 28, III) ?
 * Une interruption « pendant une durée d'au moins une année » l'année de la
 * naissance et les deux suivantes, ou les trois suivantes pour l'enfant né au
 * second semestre, « dans le cadre des congés ou de la disponibilité mentionnés
 * au 1° de l'article R. 13 » : les années dont la ligne porte l'un des motifs
 * `interruptions` ; « au titre des deux années précédant l'année de la
 * naissance [...], une durée d'assurance, telle que définie à l'article L. 14,
 * égale ou supérieure à huit trimestres », tous régimes ; et huit trimestres
 * « à raison de l'exercice d'une activité professionnelle, préalablement à
 * l'interruption » : l'emploi des années qui précèdent la première année de
 * l'interruption dans la fenêtre. Dite à l'année seule, la naissance n'en ouvre
 * le droit que si les deux fenêtres le donnent. La réduction d'activité (2°)
 * n'est pas lue : le temps partiel saisi ne dit pas son motif. Voir
 * `_remplit_pour_l_enfant_fonctionnaire` du Python.
 */
function remplitPourLEnfantFonctionnaire(carriere, conditions, naissance) {
  const annee = chrono.anneeDe(naissance.debut);
  const auMois = (naissance.attributs?.precision || "jour") !== "annee";
  const mois = auMois ? chrono.moisDe(naissance.debut).mois : 1;
  const assurance = carriere.trimestresParAnnee(carriere.lignes);
  const avant = (assurance.get(annee - 2) ?? 0) + (assurance.get(annee - 1) ?? 0);
  if (avant < Number(conditions.avant_au_moins)) {
    return false;
  }
  const motifs = new Set(conditions.interruptions);
  const conges = new Map();
  for (const ligne of carriere.lignes) {
    if (motifs.has(ligne.type_periode)) {
      conges.set(ligne.annee, Math.min(1.0, (conges.get(ligne.annee) ?? 0.0) + ligne.fraction_annee));
    }
  }
  const activite = carriere.trimestresParAnnee(
    carriere.lignes.filter((ligne) => ligne.type_periode === "emploi"),
  );
  const debuts = auMois ? [mois <= 6 ? annee : annee + 1] : [annee, annee + 1];
  return debuts.every((debut) => {
    let duree = 0.0;
    let premiere = null;
    for (let an = debut; an < debut + 3; an += 1) {
      const part = conges.get(an) ?? 0.0;
      if (part > 0) {
        duree += part;
        premiere = premiere ?? an;
      }
    }
    if (premiere === null
        || duree + 1e-9 < Number(conditions.interruption_au_moins_annees)) {
      return false;
    }
    let anterieure = 0;
    for (const [an, trimestres] of activite) {
      if (an < premiere) {
        anterieure += trimestres;
      }
    }
    return anterieure >= Number(conditions.activite_au_moins);
  });
}

/**
 * L'âge que la loi n° 2010-1330, article 28, III, donne pour borne à l'âge
 * d'annulation de la décote du fonctionnaire de `regime` — « ne peut être
 * supérieur à soixante-cinq ans » — quand il est né du 1er juillet 1951 au
 * 31 décembre 1955, a ses trois enfants et, pour l'un d'eux dont la naissance
 * est déclarée, {@link remplitPourLEnfantFonctionnaire} ; la CNRACL et les
 * ouvriers de l'État de même (décret n° 2003-1306, article 65-3 ; décret
 * n° 2004-1056, article 50-3). `null` sinon. Que sa limite d'âge ait été de
 * soixante-cinq ans, l'appelant le dit (`liquider.decoteOpposable`). Voir
 * `age_du_fonctionnaire_parent_de_trois_enfants` du Python.
 */
export function ageDuFonctionnaireParentDeTroisEnfants(moteur, regime, carriere) {
  const regle = regleDuParent(moteur, carriere);
  const conditions = regle?.fonctionnaires ?? null;
  if (conditions === null || !conditions.regimes.includes(regime)) {
    return null;
  }
  return pourUnEnfantDeclare(carriere, (naissance) => remplitPourLEnfantFonctionnaire(
    carriere, conditions, naissance)) ? Number(regle.age) : null;
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
