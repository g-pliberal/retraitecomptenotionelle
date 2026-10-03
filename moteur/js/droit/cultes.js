/**
 * La pension du régime des cultes, en deux fractions (fiche
 * `cultes_fractions_de_pension`) : celle des périodes postérieures au
 * 31 décembre 1997 aux règles du régime général (L. 382-27), celle des
 * périodes antérieures aux règles du 31 décembre 1997 — le maximum de l'année
 * au prorata de la durée, les années d'activité cultuelle d'avant 1979
 * validées gratuitement —, adaptées depuis le 1er novembre 2006 par le décret
 * n° 2006-1325 (art. 2) : décote à taux minoré, surcote et majorations
 * jusqu'au minimum contributif au taux plein.
 *
 * Jumeau de `src/retraite_notionnelle/droit/cultes.py`, qui documente chaque
 * règle.
 */

import { formatFixe, formatPourcentage } from "../format.js";

/** L'alignement : les périodes d'avant gardent les règles de 1997. */
export const ALIGNEMENT = 1998;

/** La création du régime : les années d'avant sont validées gratuitement. */
export const CREATION = 1979;

/** D. 721-7 du code de 1985 : le maximum à cent cinquante trimestres, rien sous huit. */
export const DUREE_DU_MAXIMUM = 150;
export const DUREE_MINIMALE = 8;

/** Le décret n° 2006-1325, puis son V bis : dates d'effet [année, mois]. */
export const DECRET_DE_2006 = [2006, 11];
export const DECRET_DE_2010 = [2010, 2];

/** Le V : la part de l'écart des générations de la montée en charge. */
export const PART_DE_L_ECART = Object.freeze({ 1939: 0.2, 1940: 0.4, 1941: 0.6, 1942: 0.8 });

/** La condition du minimum contributif majoré, que la caisse écrit. */
export const TRIMESTRES_COTISES_DU_MINIMUM_MAJORE = 120;

/** [année, mois] < [année, mois] */
function avant(date, borne) {
  return date[0] < borne[0] || (date[0] === borne[0] && date[1] < borne[1]);
}

/**
 * Les trimestres de `membres`, fraction par fraction, chaque année plafonnée à
 * ses trimestres civils. `enfants` dit si les trimestres des enfants que le
 * régime porte entrent dans la fraction d'après 1997.
 */
export function durees(releveDurees, membres, enfants) {
  const carriere = releveDurees.carriere;
  const somme = (table, depuis, jusqua) => {
    const sommes = new Map();
    for (const membre of membres) {
      for (const [annee, trimestres] of releveDurees.parAnnee[table].get(membre) ?? []) {
        if ((depuis === null || annee >= depuis) && (jusqua === null || annee < jusqua)) {
          sommes.set(annee, (sommes.get(annee) ?? 0) + trimestres);
        }
      }
    }
    let total = 0;
    for (const [annee, valeur] of sommes) {
      total += Math.min(valeur, carriere.plafondTrimestres(annee));
    }
    return total;
  };
  const horsAnnee = enfants
    ? membres.reduce((total, membre) => total
      + (releveDurees.horsAnnee.assurance.get(membre) ?? 0), 0)
    : 0;
  const avant1979 = somme("assurance", null, CREATION);
  const de1979A1997 = somme("assurance", CREATION, ALIGNEMENT);
  return {
    avant1979,
    de1979A1997,
    cotisesDe1979A1997: somme("cotises", CREATION, ALIGNEMENT),
    depuis1998: somme("assurance", ALIGNEMENT, null) + horsAnnee,
    cotisesDepuis1998: somme("cotises", ALIGNEMENT, null),
    avant1998: avant1979 + de1979A1997,
  };
}

/** La part de l'écart que le V donne à la génération née l'année `naissance`. */
export function partDeLEcart(naissance) {
  if (naissance < 1939) {
    return 0.0;
  }
  return PART_DE_L_ECART[naissance] ?? 1.0;
}

/**
 * La pension des périodes d'avant 1998 — `{ montant, detail, fiabilite }` —,
 * ou `null` s'il n'y en a pas. Voir `fraction_d_avant_1998` dans cultes.py.
 */
export function fractionDAvant1998(moteur, carriere, duree, proratisation, tauxPlein,
  decote, surcote, trimestresCotises, majorations = true) {
  const trimestres = duree.avant1998;
  if (trimestres < DUREE_MINIMALE) {
    return null;
  }
  const annee = carriere.anneeLiquidation;
  const lu = moteur.maximumDesCultes.valeur(annee);
  if (lu === null) {
    return null;
  }
  const [maximum] = lu;
  let fiabilite = lu[1];
  const dateEffet = [annee, carriere.moisLiquidation];
  if (avant(dateEffet, DECRET_DE_2006)) {
    const retenus = Math.min(trimestres, DUREE_DU_MAXIMUM);
    return {
      montant: maximum * retenus / DUREE_DU_MAXIMUM,
      detail: `avant 1998, maximum ${formatFixe(maximum, 2, true)} € `
        + `× ${retenus}/${DUREE_DU_MAXIMUM}`,
      fiabilite,
    };
  }
  const retenus = Math.min(trimestres, proratisation);
  const base = maximum * retenus / proratisation;
  let detail = `avant 1998, maximum ${formatFixe(maximum, 2, true)} € × ${retenus}/${proratisation}`;
  if (!tauxPlein) {
    if (decote < 1.0) {
      detail += ` × décote ${formatFixe(decote, 4)}`;
    }
    return { montant: base * decote, detail, fiabilite };
  }
  let montant = base * surcote;
  if (surcote > 1.0) {
    detail += ` × surcote ${formatFixe(surcote, 4)}`;
  }
  if (!majorations) {
    return { montant, detail, fiabilite };
  }
  const [minimum, majore, , fiabiliteMinimum] = moteur.minimumContributif.valeurs(annee);
  // Les deux majorations se partagent la durée maximale : les trimestres
  // cotisés de 1979 à 1997 d'abord, ceux d'avant 1979 dans ce qui reste.
  const cotises = Math.min(duree.cotisesDe1979A1997, proratisation);
  const part = partDeLEcart(carriere.annee_naissance);
  const majoreOuvert = trimestresCotises >= TRIMESTRES_COTISES_DU_MINIMUM_MAJORE;
  const niveau = majoreOuvert ? majore : minimum;
  if (part > 0 && cotises > 0 && niveau > maximum) {
    const majoration = part * (niveau - maximum) * cotises / proratisation;
    montant += majoration;
    fiabilite = Math.min(fiabilite, fiabiliteMinimum);
    let qualificatif = majoreOuvert ? " majoré" : "";
    if (part < 1.0) {
      qualificatif += `, ${formatPourcentage(part, 0)} de l'écart`;
    }
    detail += ` + ${formatFixe(majoration, 2, true)} € pour ${cotises} trimestres cotisés `
      + `de 1979 à 1997 (minimum contributif${qualificatif})`;
  }
  if (!avant(dateEffet, DECRET_DE_2010)) {
    const avant1979 = Math.min(duree.avant1979, Math.max(0, proratisation - cotises));
    if (avant1979 > 0 && minimum > maximum) {
      const majoration = (minimum - maximum) * avant1979 / proratisation;
      montant += majoration;
      fiabilite = Math.min(fiabilite, fiabiliteMinimum);
      detail += ` + ${formatFixe(majoration, 2, true)} € pour ${avant1979} trimestres `
        + "d'avant 1979 (minimum contributif)";
    }
  }
  return { montant, detail, fiabilite };
}
