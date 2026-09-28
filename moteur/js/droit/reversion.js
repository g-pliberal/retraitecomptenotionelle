/**
 * La réversion : la pension du survivant, dans les régimes du défunt
 * (docs/architecture.md, § 7.3).
 *
 * Jumeau de `src/retraite_notionnelle/droit/reversion.py`, fonction pour
 * fonction. « La réversion n'est pas une étape. C'est `liquider` pour le
 * survivant, de motif « réversion », dans les régimes du défunt. » Elle lit la
 * liquidation du défunt — son départ, mené jusqu'à son décès par « faire
 * vivre » — et applique à chaque régime la version de sa fiche que les dates
 * choisissent : le régime général et les régimes alignés (`reversion`), la
 * fonction publique et la CNRACL (`reversion_fonction_publique`),
 * l'Agirc-Arrco (`reversion_agirc_arrco`). Les autres régimes n'ont pas encore
 * de fiche : leur ligne le dit, sans montant. Ce qui n'est pas encore porté,
 * et les montants — ceux de l'année du décès —, sont dits dans l'en-tête du
 * Python.
 */

import * as chrono from "../chronologie.js";
import { Fiabilite, fiabiliteDepuisTexte, nomFiabilite } from "../serie.js";

/** La version du schéma que `Reversion.donnees` suit. */
export const SCHEMA_VERSION = 1;

/** Ce que dit une ligne dont le montant est nul, ou qui n'est pas servie en entier. */
export const MOTIFS = Object.freeze({
  servie: "servie",
  ecretee: "réduite à due concurrence du plafond de ressources",
  ressources: "ressources au-dessus du plafond",
  mariage: "condition d'antériorité ou de durée du mariage non remplie",
  non_portee: "la réversion de ce régime n'est pas encore portée",
});

/** La réversion d'un régime du défunt. */
export class ReversionRegime {
  /**
   * `base` : la pension du défunt dans ce régime, à l'année des montants ;
   * `date_effet` : le premier jour du mois qui suit le décès, ou qui suit
   * l'âge requis.
   */
  constructor({ regime, base, montant, motif, fiche = null, version = null, texte = null,
    taux = 0.0, date_effet = null, fiabilite = Fiabilite.ESTIMEE }) {
    this.regime = regime;
    this.base = base;
    this.montant = montant;
    this.motif = motif;
    this.fiche = fiche;
    this.version = version;
    this.texte = texte;
    this.taux = taux;
    this.date_effet = date_effet;
    this.fiabilite = fiabilite;
    Object.freeze(this);
  }

  donnees() {
    return {
      regime: this.regime, base: this.base, taux: this.taux, montant: this.montant,
      motif: this.motif, date_effet: this.date_effet, fiche: this.fiche,
      version: this.version, texte: this.texte, fiabilite: nomFiabilite(this.fiabilite),
    };
  }
}

/** Ce que la liquidation d'une réversion écrit : régime par régime. */
export class Reversion {
  constructor({ personne, defunt, deces, annee, ressources, ressources_presumees, regimes }) {
    this.personne = personne;
    this.defunt = defunt;
    this.deces = deces;
    this.annee = annee;
    this.ressources = ressources;
    this.ressources_presumees = ressources_presumees;
    this.regimes = Object.freeze([...regimes]);
    Object.freeze(this);
  }

  get total() {
    let total = 0;
    for (const r of this.regimes) {
      total += r.montant;
    }
    return total;
  }

  donnees() {
    return {
      schema_version: SCHEMA_VERSION, personne: this.personne, defunt: this.defunt,
      deces: this.deces, annee: this.annee, ressources: this.ressources,
      ressources_presumees: this.ressources_presumees, total: this.total,
      regimes: this.regimes.map((r) => r.donnees()),
    };
  }
}

/** Le premier jour du mois qui suit `jour` (AAAA-MM-JJ). */
export function moisSuivant(jour) {
  let annee = Number(jour.slice(0, 4));
  let mois = Number(jour.slice(5, 7));
  if (mois === 12) {
    annee += 1;
    mois = 1;
  } else {
    mois += 1;
  }
  return `${String(annee).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`;
}

/**
 * Le premier jour du mois qui suit celui où `age` est atteint (R. 353-7) : un
 * anniversaire le 1er du mois ouvre le mois suivant, comme les autres.
 */
function apresLAge(naissance, age) {
  return moisSuivant(chrono.plusAns(naissance, Math.trunc(age)));
}

/** La date d'effet, reportée s'il le faut au mois qui suit l'âge requis. */
function aLAge(naissance, dateEffet, age) {
  if (age === null || age === undefined) {
    return dateEffet;
  }
  const apres = apresLAge(naissance, age);
  return apres > dateEffet ? apres : dateEffet;
}

/**
 * L'âge requis à l'Agirc-Arrco : celui de l'accord de 2017, ou, pour un décès
 * d'avant 2019, celui de l'Agirc ou de l'Arrco, et du veuf ou de la veuve
 * quand la version les distingue.
 */
function ageAgircArrco(parametres, regime, sexe) {
  if (parametres.age_minimum !== null && parametres.age_minimum !== undefined) {
    return Number(parametres.age_minimum);
  }
  const agirc = regime.startsWith("agirc") && regime !== "agirc_arrco";
  const propre = parametres[agirc ? "age_minimum_agirc" : "age_minimum_arrco"];
  if (propre !== null && propre !== undefined) {
    return Number(propre);
  }
  return Number(parametres[sexe === "H" ? "age_minimum_veuf" : "age_minimum_veuve"]);
}

/**
 * La condition de durée du mariage du régime général d'avant juillet 2004 :
 * `annees` de mariage au décès, sauf enfant issu du mariage — que le modèle
 * tient pour tout enfant déclaré.
 */
function mariageDure(conjoint, deces, enfants, annees) {
  return !annees || enfants > 0 || chrono.anneesRevolues(conjoint.mariage, deces) >= annees;
}

/**
 * La condition de L. 39 : un enfant issu du mariage, quatre ans de mariage,
 * ou deux ans de services entre le mariage et la cessation d'activité — lue
 * au départ, que le modèle tient pour la cessation.
 */
function mariageSuffit(parametres, conjoint, deces, depart, enfants) {
  if (enfants > 0) {
    return true;
  }
  return chrono.anneesRevolues(conjoint.mariage, deces) >= parametres.mariage_minimum_annees
    || chrono.anneesRevolues(conjoint.mariage, depart)
      >= parametres.mariage_services_minimum_annees;
}

/**
 * La réversion que le décès de la personne de `carriere` ouvre à son
 * conjoint, régime par régime ; `null` sans décès ou sans conjoint.
 * `pensions` sont les pensions du défunt à l'année `annee`, où les montants se
 * chiffrent : `[régime, montant, fiabilité]`, dans l'ordre de sa liquidation.
 * Un régime qui ne lui sert rien n'a rien à reverser. Voir `reversion` du
 * Python.
 */
export function reversion(moteur, pensions, carriere, annee) {
  const conjoint = carriere.conjoint;
  if (carriere.deces === null || conjoint === null) {
    return null;
  }
  const deces = carriere.deces;
  const lendemain = moisSuivant(deces);
  const liquidation = carriere.dateLiquidation;
  const depart = `${String(liquidation.annee).padStart(4, "0")}-`
    + `${String(liquidation.mois).padStart(2, "0")}-01`;
  const enfants = carriere.nombre_enfants;
  const presumees = conjoint.ressources === null;
  const ressources = presumees ? 0.0 : Number(conjoint.ressources);
  const table = moteur.reversions;
  const servies = pensions.filter(([, base]) => base > 0);

  const ligne = (regime, base, montant, motif, fiche, version, taux, dateEffet,
    fiabilite) => new ReversionRegime({
    regime, base, montant, motif, fiche: fiche.id, version: version.id,
    texte: version.texte, taux, date_effet: dateEffet,
    fiabilite: Math.min(fiabilite, fiabiliteDepuisTexte(version.parametres.fiabilite)),
  });

  const lignes = new Map();
  // La fonction publique et l'Agirc-Arrco d'abord : la réversion d'un autre
  // régime de base compte aux ressources du régime général ; celle des
  // complémentaires, non (R. 353-1, 2°).
  let autresBases = 0.0;
  for (const [regime, base, fiabilite] of servies) {
    const fiche = table.ficheDuRegime(regime);
    if (fiche === null) {
      lignes.set(regime, new ReversionRegime({
        regime, base, montant: 0.0, motif: "non_portee",
      }));
      continue;
    }
    if (fiche.id === "reversion") {
      continue;
    }
    const version = table.version(fiche, lendemain, deces);
    const parametres = version.parametres;
    const taux = Number(parametres.taux);
    if (fiche.id === "reversion_fonction_publique") {
      const servie = mariageSuffit(parametres, conjoint, deces, depart, enfants);
      const montant = servie ? taux * base : 0.0;
      autresBases += montant;
      lignes.set(regime, ligne(regime, base, montant, servie ? "servie" : "mariage",
        fiche, version, taux, lendemain, fiabilite));
      continue;
    }
    const dateEffet = aLAge(conjoint.naissance, lendemain,
      ageAgircArrco(parametres, regime, conjoint.sexe));
    lignes.set(regime, ligne(regime, base, taux * base, "servie", fiche, version, taux,
      dateEffet, fiabilite));
  }

  // Le plafond de ressources est un : les réversions des régimes alignés se
  // l'imputent l'une après l'autre, dans l'ordre de la liquidation.
  for (const [regime, base, fiabilite] of servies) {
    const fiche = table.ficheDuRegime(regime);
    if (fiche === null || fiche.id !== "reversion") {
      continue;
    }
    // L'âge requis reporte la date d'effet, et la date d'effet choisit la
    // version, dont l'âge peut changer : deux tours suffisent au plus.
    let dateEffet = lendemain;
    let version;
    for (let tour = 0; tour < 3; tour += 1) {
      version = table.version(fiche, dateEffet, deces);
      const reportee = aLAge(conjoint.naissance, lendemain,
        Number(version.parametres.age_minimum));
      if (reportee === dateEffet) {
        break;
      }
      dateEffet = reportee;
    }
    const parametres = version.parametres;
    const taux = Number(parametres.taux);
    let montant = taux * base;
    const plafondAnnuel = Number(parametres.plafond_smic_heures)
      * moteur.macro.smic_horaire.valeur(annee);
    const disponible = plafondAnnuel - ressources - autresBases;
    let motif = "servie";
    if (!mariageDure(conjoint, deces, enfants, parametres.mariage_minimum_annees)) {
      montant = 0.0;
      motif = "mariage";
    } else if (parametres.ressources === "ecretement") {
      if (montant > disponible) {
        montant = Math.max(0.0, disponible);
        motif = "ecretee";
      }
    } else if (disponible < 0) {
      montant = 0.0;
      motif = "ressources";
    }
    autresBases += montant;
    lignes.set(regime, ligne(regime, base, montant, motif, fiche, version, taux,
      dateEffet, fiabilite));
  }

  return new Reversion({
    personne: conjoint.personne, defunt: carriere.personne, deces, annee,
    ressources, ressources_presumees: presumees,
    regimes: servies.map(([regime]) => lignes.get(regime)),
  });
}
