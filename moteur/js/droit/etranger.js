/**
 * Les carrières hors de France (docs/architecture.md, § 11) : ce que les étapes
 * du droit lisent des fiches du domaine et du tableau des accords, que
 * `CarrieresHorsDeFrance` prépare.
 *
 * Jumeau de `src/retraite_notionnelle/droit/etranger.py`, fonction pour
 * fonction : « coordonner les affiliations » dit à quel titre chaque période
 * passée hors de France compte, et pour quelles familles de régimes
 * (`coordonnerLesPeriodes`) ; « compter les durées » en fait des trimestres,
 * année par année, sans dépasser quatre avec ceux de la carrière française
 * (`compterLesPeriodes`).
 */

import { DateMois, MOIS_PAR_AN, moisTravailles, trimestresCivils } from "../calendrier.js";
import { dateDEffet } from "./commun.js";

/**
 * Les deux familles de régimes qui lisent les trimestres étrangers : le régime
 * général, et ceux que la fiche coordonne avec lui ; les régimes du code des
 * pensions.
 */
export const GENERALE = "regime_general";
export const FONCTIONNAIRES = "fonction_publique";
export const FAMILLES = Object.freeze([GENERALE, FONCTIONNAIRES]);

/**
 * Les titres auxquels une période étrangère compte, dans l'ordre où ses
 * trimestres entrent sous le plafond de l'année : ceux d'un accord d'abord, les
 * seuls qui comptent aussi comme cotisés.
 */
export const ACCORD = "accord";
export const ORGANISATION = "organisation_internationale";
export const EQUIVALENCE = "equivalence";
export const TITRES = Object.freeze([ACCORD, ORGANISATION, EQUIVALENCE]);

/** Les instruments d'un accord qui totalise les périodes (tableau des accords). */
const INSTRUMENTS_QUI_TOTALISENT = new Set([
  "reglements_europeens", "accord_de_commerce_et_de_cooperation", "convention",
]);
/** L'instrument propre à un État : une convention bilatérale. */
const CONVENTION = "convention";
/** Celui qui, seul, coordonne aussi les régimes des fonctionnaires. */
const REGLEMENTS_EUROPEENS = "reglements_europeens";
/** Les personnes qu'une convention ne vise qu'à moitié : les seuls salariés. */
const SALARIES = "salaries";
const SALARIEE = "salariee";
/** Le code d'une organisation internationale au tableau des accords. */
const ORGANISATION_INTERNATIONALE = "OI";
/**
 * Le calcul des règlements européens qui compare la pension nationale à la
 * pension proratisée, et ceux d'un accord bilatéral qui la comparent ou
 * laissent l'assuré choisir la plus élevée. Voir `CALCULS_COMPARES` du Python.
 */
const COMPARAISON = "comparaison";
const CALCULS_COMPARES = new Set([COMPARAISON, "option"]);

const jourDe = (mois) =>
  `${String(mois.annee).padStart(4, "0")}-${String(mois.mois).padStart(2, "0")}-01`;

/**
 * Une période passée hors de France, et ce que la coordination en fait :
 * `{periode, titre, instrument, familles, version, parametres, comparee,
 * etatsTiers}`. Voir `PeriodeCoordonnee` du Python.
 */
export function donneesDeLaPeriode(coordonnee) {
  const { periode } = coordonnee;
  return {
    pays: periode.pays, debut: jourDe(periode.debut), fin: jourDe(periode.fin),
    activite: periode.activite, titre: coordonnee.titre, instrument: coordonnee.instrument,
    familles: [...coordonnee.familles], version: coordonnee.version,
    comparee: coordonnee.comparee,
  };
}

/**
 * Chaque période hors de France, et le titre auquel elle compte pour une
 * pension qui prend effet à la date de la carrière : l'accord que le tableau
 * donne alors à son État, s'il vise l'activité de la période ; l'organisation
 * internationale depuis 2010 ; l'équivalence de l'activité d'avant le
 * 1er avril 1983 sinon. Voir `coordonner_les_periodes` du Python.
 */
export function coordonnerLesPeriodes(moteur, carriere) {
  const effet = dateDEffet(carriere);
  if (effet === null || carriere.periodesALEtranger.length === 0) {
    return [];
  }
  const domaine = moteur.carrieresHorsDeFrance;
  const proratisation = domaine.version("proratisation", {
    "liquidation.date_effet": effet,
    "assure.generation": `${String(carriere.annee_naissance).padStart(4, "0")}-01-01`,
  });
  const reglementsCompares = proratisation !== null
    && proratisation.parametres.reglements_europeens === COMPARAISON;
  return carriere.periodesALEtranger.map((periode) => {
    const version = domaine.version("totalisation", {
      "liquidation.date_effet": effet, "periode.debut": jourDe(periode.debut),
      "periode.fin": jourDe(periode.fin),
    });
    const parametres = version === null ? {} : version.parametres;
    const accord = domaine.accord(periode.pays, effet);
    let titre = null;
    let instrument = null;
    let familles = [];
    if (!parametres.compte_pour_le_taux) {
      // Avant le 1er avril 1983, le taux se lit sur l'âge.
    } else if (periode.pays === ORGANISATION_INTERNATIONALE) {
      if (accord !== null && parametres.organisations_internationales) {
        titre = ORGANISATION;
        instrument = accord.instrument;
        familles = [...FAMILLES];
      }
    } else if (accord !== null && INSTRUMENTS_QUI_TOTALISENT.has(accord.instrument)
        && (accord.personnes !== SALARIES || periode.activite === SALARIEE)) {
      titre = ACCORD;
      instrument = accord.instrument;
      const fonctionnaires = parametres.fonctionnaires_depuis ?? null;
      familles = instrument === REGLEMENTS_EUROPEENS && fonctionnaires !== null
        && effet >= fonctionnaires ? [GENERALE, FONCTIONNAIRES] : [GENERALE];
    } else if ((parametres.equivalentes_avant ?? null) !== null
        && jourDe(periode.debut) < parametres.equivalentes_avant) {
      titre = EQUIVALENCE;
      familles = [GENERALE];
    }
    const comparee = titre === ACCORD && (instrument === REGLEMENTS_EUROPEENS
      ? reglementsCompares : CALCULS_COMPARES.has(accord.calcul));
    return {
      periode, titre, instrument, familles,
      version: version === null ? null : version.id, parametres, comparee,
      etatsTiers: titre === ACCORD ? [...(accord.etats_tiers ?? [])] : [],
    };
  });
}

/**
 * Ce que les périodes hors de France apportent aux durées, famille par famille
 * de régimes et année par année, le plafond de l'année fait. Voir
 * `TrimestresEtrangers` du Python.
 */
export class TrimestresEtrangers {
  constructor(pourLeTaux, cotises, periodes, famille = GENERALE, nationaux = {}) {
    /** Par famille, une `Map` de l'année aux trimestres que le taux retient. */
    this.pourLeTaux = pourLeTaux;
    /** Par famille, ceux d'entre eux qui comptent comme cotisés. */
    this.cotises = cotises;
    /** Les périodes, et ce que la coordination en a fait. */
    this.periodes = periodes;
    /** La famille des régimes de la carrière. */
    this.famille = famille;
    /**
     * Par famille, ceux que la durée du taux de la pension NATIONALE retient,
     * sans les périodes qu'un accord compare.
     */
    this.nationaux = nationaux;
  }

  /**
   * Les trimestres que la durée du taux de cette famille retient — de sa
   * pension nationale, avec `nationale`.
   */
  trimestres(famille, nationale = false) {
    const table = nationale ? this.nationaux : this.pourLeTaux;
    let total = 0;
    for (const nombre of (table[famille] ?? new Map()).values()) {
      total += nombre;
    }
    return total;
  }

  /** Un accord compare-t-il, pour cette famille, une pension nationale à la proratisée ? */
  compare(famille) {
    return this.trimestres(famille) !== this.trimestres(famille, true);
  }

  /** Ceux d'entre eux qui comptent comme cotisés. */
  trimestresCotises(famille) {
    let total = 0;
    for (const nombre of (this.cotises[famille] ?? new Map()).values()) {
      total += nombre;
    }
    return total;
  }

  donnees() {
    const trimestres = [];
    for (const famille of FAMILLES) {
      const annees = [...(this.pourLeTaux[famille] ?? new Map()).entries()]
        .sort((a, b) => a[0] - b[0]);
      for (const [annee, nombre] of annees) {
        trimestres.push({
          famille, annee, trimestres: nombre,
          cotises: (this.cotises[famille] ?? new Map()).get(annee) ?? 0,
          nationaux: (this.nationaux[famille] ?? new Map()).get(annee) ?? 0,
        });
      }
    }
    return {
      famille: this.famille,
      periodes: this.periodes.map(donneesDeLaPeriode),
      trimestres,
    };
  }
}

/**
 * La famille dont un régime lit les trimestres étrangers : celle des
 * fonctionnaires pour un régime de la fonction publique que la fiche coordonne,
 * la générale pour les autres qu'elle coordonne et pour les régimes en points ;
 * aucune pour un autre régime en annuités. Voir `famille_du_regime` du Python.
 */
export function familleDuRegime(moteur, code) {
  const regime = moteur.catalogue.contient(code) ? moteur.catalogue.obtenir(code) : null;
  if (moteur.carrieresHorsDeFrance.regimes("totalisation").has(code)) {
    return regime !== null && regime.famille === "fonction_publique"
      ? FONCTIONNAIRES : GENERALE;
  }
  if (regime !== null && regime.periodes.some(
    (periode) => periode.type_calcul === "points" || periode.type_calcul === "mixte")) {
    return GENERALE;
  }
  return null;
}

/**
 * La famille dont une condition commune à plusieurs régimes lit les trimestres
 * étrangers : celle des fonctionnaires quand tous les régimes de la carrière
 * que la fiche coordonne en sont, la générale sinon. Voir
 * `famille_des_regimes` du Python.
 */
export function familleDesRegimes(moteur, codes) {
  const coordonnes = moteur.carrieresHorsDeFrance.regimes("totalisation");
  const familles = new Set();
  for (const code of codes) {
    if (coordonnes.has(code)) {
      familles.add(familleDuRegime(moteur, code));
    }
  }
  return familles.size === 1 && familles.has(FONCTIONNAIRES) ? FONCTIONNAIRES : GENERALE;
}

/**
 * Les trimestres que chaque période coordonnée apporte, année par année, puis
 * ceux que chaque famille retient sous le plafond de l'année — quatre, avec
 * ceux de la carrière française ; l'année du départ, les trimestres civils
 * écoulés avant lui —, ceux d'un accord d'abord ; et, de même, ceux que la
 * pension nationale retient, sans les périodes qu'un accord compare. Un seul
 * accord à la fois : chaque famille retient celui qui lui apporte le plus de
 * trimestres, avec les États tiers que sa convention fait compter. Voir
 * `compter_les_periodes` du Python.
 */
export function compterLesPeriodes(carriere, periodes, trimestresFrancais,
  famille = GENERALE) {
  const francais = carriere.trimestresParAnnee(carriere.lignes);
  const depart = carriere.dateLiquidation;
  const candidats = [];
  for (const coordonnee of periodes) {
    if (coordonnee.titre === null) {
      continue;
    }
    const { parametres } = coordonnee;
    const seuil = parametres.equivalentes_trimestres_francais_au_moins ?? null;
    if (coordonnee.titre === EQUIVALENCE && seuil !== null && trimestresFrancais < seuil) {
      continue;
    }
    for (const [annee, trimestres] of trimestresDe(coordonnee, parametres, depart)) {
      candidats.push([coordonnee, annee, trimestres]);
    }
  }
  const calculs = groupes(candidats).map(([groupe, compare]) => {
    const [pourLeTaux, cotises] = retenir(groupe, francais, depart);
    const [nationaux] = retenir(groupe.filter(
      ([coordonnee]) => !compare || accordDe(coordonnee) === null), francais, depart);
    return [pourLeTaux, cotises, nationaux];
  });
  const retenus = [{}, {}, {}];
  for (const retenante of FAMILLES) {
    // Le premier des accords qui en apportent le plus, dans l'ordre des
    // périodes.
    const somme = (calcul) => [...calcul[0][retenante].values()].reduce((a, b) => a + b, 0);
    let meilleur = calculs[0];
    for (const calcul of calculs.slice(1)) {
      if (somme(calcul) > somme(meilleur)) {
        meilleur = calcul;
      }
    }
    retenus.forEach((table, rang) => {
      table[retenante] = meilleur[rang][retenante];
    });
  }
  return new TrimestresEtrangers(retenus[0], retenus[1], periodes, famille, retenus[2]);
}

/**
 * L'accord qui fait compter la période : son instrument, ou l'État de sa
 * convention ; `null` pour une période que le droit français fait compter. Voir
 * `_accord_de` du Python.
 */
function accordDe(coordonnee) {
  if (coordonnee.titre !== ACCORD) {
    return null;
  }
  return coordonnee.instrument === CONVENTION ? coordonnee.periode.pays : coordonnee.instrument;
}

/**
 * Les trimestres que chaque accord ferait totaliser, dans l'ordre des périodes,
 * et s'il compare la pension nationale à la pension proratisée. Voir `_groupes`
 * du Python.
 */
function groupes(candidats) {
  const accords = new Map();
  for (const [coordonnee] of candidats) {
    const cle = accordDe(coordonnee);
    if (cle !== null) {
      const [tiers, compare] = accords.get(cle) ?? [new Set(), false];
      for (const etat of coordonnee.etatsTiers) {
        tiers.add(etat);
      }
      accords.set(cle, [tiers, compare || coordonnee.comparee]);
    }
  }
  if (accords.size === 0) {
    return [[candidats, false]];
  }
  return [...accords].map(([cle, [tiers, compare]]) => [
    candidats.filter(([coordonnee]) => {
      const accord = accordDe(coordonnee);
      return accord === null || accord === cle || tiers.has(coordonnee.periode.pays);
    }),
    compare,
  ]);
}

/**
 * Ce que chaque famille retient de ces trimestres, année par année, sous le
 * plafond de l'année : ceux d'un accord d'abord, les seuls cotisés. Voir
 * `_retenir` du Python.
 */
function retenir(candidats, francais, depart) {
  const offres = Object.fromEntries(FAMILLES.map((f) => [f, new Map()]));
  for (const [coordonnee, annee, trimestres] of candidats) {
    for (const retenante of coordonnee.familles) {
      if (!offres[retenante].has(annee)) {
        offres[retenante].set(annee, []);
      }
      offres[retenante].get(annee).push([TITRES.indexOf(coordonnee.titre), trimestres]);
    }
  }
  const pourLeTaux = Object.fromEntries(FAMILLES.map((f) => [f, new Map()]));
  const cotises = Object.fromEntries(FAMILLES.map((f) => [f, new Map()]));
  for (const retenante of FAMILLES) {
    const annees = [...offres[retenante].keys()].sort((a, b) => a - b);
    for (const annee of annees) {
      const plafond = annee < depart.annee ? 4 : trimestresCivils(depart.mois - 1);
      const libres = Math.max(0, plafond - (francais.get(annee) ?? 0));
      let retenus = 0;
      let cotisesAnnee = 0;
      const offresAnnee = [...offres[retenante].get(annee)]
        .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
      for (const [rang, trimestres] of offresAnnee) {
        const pris = Math.min(trimestres, libres - retenus);
        retenus += pris;
        if (TITRES[rang] === ACCORD) {
          cotisesAnnee += pris;
        }
      }
      if (retenus) {
        pourLeTaux[retenante].set(annee, retenus);
      }
      if (cotisesAnnee) {
        cotises[retenante].set(annee, cotisesAnnee);
      }
    }
  }
  return [pourLeTaux, cotises];
}

/**
 * Les trimestres qu'une période apporte, année par année, avant le plafond de
 * l'année : jusqu'au départ, quand elle le dépasse. Voir `_trimestres_de` du
 * Python.
 */
function trimestresDe(coordonnee, parametres, depart) {
  const { periode } = coordonnee;
  const auPlus = parametres.trimestres_par_annee_au_plus;
  let fin = depart.rang < periode.fin.rang ? depart : periode.fin;
  const resultat = new Map();
  if (coordonnee.titre === ORGANISATION) {
    const jours = parametres.jours_par_trimestre_organisations_internationales;
    const jour = 24 * 3600 * 1000;
    for (let annee = periode.debut.annee; annee <= fin.annee; annee += 1) {
      const ouverture = Math.max(Date.UTC(periode.debut.annee, periode.debut.mois - 1, 1),
        Date.UTC(annee, 0, 1));
      const cloture = Math.min(Date.UTC(fin.annee, fin.mois - 1, 1), Date.UTC(annee + 1, 0, 1));
      const duree = Math.round((cloture - ouverture) / jour);
      if (cloture > ouverture && duree >= jours) {
        resultat.set(annee, Math.min(auPlus, Math.floor(duree / jours)));
      }
    }
    return resultat;
  }
  if (coordonnee.titre === EQUIVALENCE) {
    const avant = parametres.equivalentes_avant;
    const limite = new DateMois(Number(avant.slice(0, 4)), Number(avant.slice(5, 7)));
    fin = limite.rang < fin.rang ? limite : fin;
  }
  const parTrimestre = parametres.mois_par_trimestre;
  for (let annee = periode.debut.annee; annee <= fin.annee; annee += 1) {
    const mois = moisTravailles(annee, periode.debut, fin);
    if (mois > 0) {
      resultat.set(annee, Math.min(auPlus, Math.ceil(mois / parTrimestre)));
    }
  }
  return resultat;
}

/** Ce que des périodes hors de France n'apportent pas, faute d'en avoir. */
export const RIEN = new TrimestresEtrangers(
  Object.fromEntries(FAMILLES.map((f) => [f, new Map()])),
  Object.fromEntries(FAMILLES.map((f) => [f, new Map()])), [], GENERALE,
  Object.fromEntries(FAMILLES.map((f) => [f, new Map()])));

/**
 * Les deux temps à la suite, pour qui lit les trimestres étrangers hors du
 * relevé — la carrière longue d'un autre départ. Voir `trimestres_etrangers`
 * du Python.
 */
export function trimestresEtrangers(moteur, carriere) {
  if (carriere.periodesALEtranger.length === 0) {
    return RIEN;
  }
  return compterLesPeriodes(carriere, coordonnerLesPeriodes(moteur, carriere),
    carriere.trimestresActuels);
}

/**
 * Ce que les pensions étrangères ajoutent, par an, aux pensions que
 * l'écrêtement du minimum contributif compte depuis 2012 : celles qui ont
 * commencé au plus tard le mois de la date d'effet, au montant de ce mois, hors
 * celles que calculent les règlements européens, l'accord avec le Royaume-Uni et
 * six conventions. Voir `pensions_a_l_ecretement` du Python.
 */
export function pensionsALEcretement(moteur, carriere) {
  const effet = dateDEffet(carriere);
  if (effet === null || carriere.pensionsEtrangeres.length === 0) {
    return 0.0;
  }
  const domaine = moteur.carrieresHorsDeFrance;
  const version = domaine.version("minimum", { "liquidation.date_effet": effet });
  if (version === null || !version.parametres.ecretement_pensions_etrangeres) {
    return 0.0;
  }
  const exclues = new Set(version.parametres.pensions_hors_ecretement ?? []);
  let total = 0.0;
  for (const pension of carriere.pensionsEtrangeres) {
    if (pension.debut.rang > carriere.dateLiquidation.rang || exclues.has(pension.pays)) {
      continue;
    }
    const accord = domaine.accord(pension.pays, jourDe(pension.debut));
    if (accord !== null && exclues.has(accord.instrument)) {
      continue;
    }
    total += pension.mensuel * MOIS_PAR_AN * moteur.macro.coefficientPrix(
      pension.debut.annee, carriere.anneeLiquidation);
  }
  return total;
}
