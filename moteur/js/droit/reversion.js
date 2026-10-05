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
 * l'Agirc-Arrco (`reversion_agirc_arrco`), le RAFP (`reversion_rafp`),
 * l'Ircantec (`reversion_ircantec`), la complémentaire des indépendants
 * (`reversion_rci`). Les autres régimes n'ont pas encore de fiche : leur ligne
 * le dit, sans montant. Ce qui n'est pas encore porté, et les montants — ceux
 * de l'année du décès —, sont dits dans l'en-tête du Python. Sans décès
 * déclaré, l'échéancier liquide une réversion d'essai pour un décès supposé
 * juste après le départ (présomption `deces_apres_le_depart`).
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

/**
 * Les fiches dont les réversions se chiffrent après les autres, parce que celles
 * des autres régimes de base comptent à leurs ressources : le régime général et
 * les régimes alignés, puis la complémentaire des indépendants.
 */
export const APRES_LES_BASES = Object.freeze(["reversion", "reversion_rci"]);

/** La réversion d'un régime du défunt. */
export class ReversionRegime {
  /**
   * `base` : la pension du défunt dans ce régime, à l'année des montants ;
   * `date_effet` : le premier jour du mois qui suit le décès, ou qui suit
   * l'âge requis.
   */
  constructor({ regime, base, montant, motif, fiche = null, version = null, texte = null,
    taux = 0.0, date_effet = null, fiabilite = Fiabilite.ESTIMEE, majoration = 0.0 }) {
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
    // La part du montant qui reverse la majoration pour enfants du défunt,
    // hors du taux : l'Agirc-Arrco la reverse en entier depuis 2019.
    this.majoration = majoration;
    Object.freeze(this);
  }

  donnees() {
    return {
      regime: this.regime, base: this.base, taux: this.taux, montant: this.montant,
      motif: this.motif, date_effet: this.date_effet, fiche: this.fiche,
      version: this.version, texte: this.texte, fiabilite: nomFiabilite(this.fiabilite),
      majoration: this.majoration,
    };
  }
}

/** Ce que la liquidation d'une réversion écrit : régime par régime. */
export class Reversion {
  constructor({ personne, defunt, deces, annee, ressources, ressources_presumees, regimes,
    deces_suppose = false }) {
    this.personne = personne;
    this.defunt = defunt;
    this.deces = deces;
    // Le décès est-il supposé (présomption `deces_apres_le_depart`) ?
    this.deces_suppose = deces_suppose;
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
      deces: this.deces, deces_suppose: this.deces_suppose, annee: this.annee,
      ressources: this.ressources,
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
 * L'âge requis à l'Ircantec : celui du conjoint depuis 2004 ; avant, celui de
 * la veuve ou du veuf. Le veuf d'avant 1976, que l'arrêté ne servait pas,
 * attend l'âge de la veuve : une approximation que la fiche déclare.
 */
function ageIrcantec(parametres, sexe) {
  if (parametres.age_minimum !== null && parametres.age_minimum !== undefined) {
    return Number(parametres.age_minimum);
  }
  const veuf = parametres.age_minimum_veuf;
  if (sexe === "H" && veuf !== null && veuf !== undefined) {
    return Number(veuf);
  }
  return Number(parametres.age_minimum_veuve);
}

/**
 * La condition de l'article 20 de l'arrêté du 30 décembre 1970 : quatre ans de
 * mariage au décès, ou un mariage contracté deux ans au moins avant les
 * cinquante-cinq ans de l'agent né le jour `naissance`, ou avant la cessation
 * de ses fonctions — que le modèle tient pour son départ ; depuis 1994, aucune
 * durée quand un enfant est issu du mariage, que le modèle tient pour tout
 * enfant déclaré.
 */
function mariageIrcantec(parametres, conjoint, naissance, deces, depart, enfants) {
  if (parametres.mariage_leve_par_enfant && enfants > 0) {
    return true;
  }
  const avant = parametres.mariage_avant_annees;
  const limite = chrono.plusAns(naissance, Math.trunc(Number(parametres.mariage_avant_age)));
  return chrono.anneesRevolues(conjoint.mariage, deces) >= parametres.mariage_minimum_annees
    || chrono.anneesRevolues(conjoint.mariage, limite) >= avant
    || chrono.anneesRevolues(conjoint.mariage, depart) >= avant;
}

/**
 * Les enfants nés au décès qui n'ont pas encore `ans` ans : ceux que la
 * chronologie porte, déclarés ou présumés, et que le modèle tient pour à la
 * charge du survivant.
 */
function enfantsDeMoinsDe(carriere, deces, ans) {
  return carriere.naissancesDesEnfants.filter(
    ([, naissance]) => naissance <= deces && deces < chrono.plusAns(naissance, ans)).length;
}

/**
 * La réversion que le décès de la personne de `carriere` ouvre à son
 * conjoint, régime par régime ; `null` sans décès ou sans conjoint.
 * `pensions` sont les pensions du défunt à l'année `annee`, où les montants se
 * chiffrent : `[régime, montant, fiabilité]`, dans l'ordre de sa liquidation.
 * Un régime qui ne lui sert rien n'a rien à reverser, ni celui qui lui a versé
 * son droit en capital, quand la fiche le dit : `enCapital` nomme ces régimes.
 * `decesSuppose` date le décès que la présomption `deces_apres_le_depart`
 * suppose, quand la chronologie n'en dit pas. Voir `reversion` du Python.
 */
export function reversion(moteur, pensions, carriere, annee, decesSuppose = null,
  enCapital = new Set(), majorations = null) {
  const conjoint = carriere.conjoint;
  const deces = decesSuppose === null ? carriere.deces : decesSuppose;
  if (deces === null || conjoint === null) {
    return null;
  }
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
    fiabilite, majoration = 0.0) => new ReversionRegime({
    regime, base, montant, motif, fiche: fiche.id, version: version.id,
    texte: version.texte, taux, date_effet: dateEffet,
    fiabilite: Math.min(fiabilite, fiabiliteDepuisTexte(version.parametres.fiabilite)),
    majoration,
  });

  const lignes = new Map();
  // La fonction publique, le RAFP, l'Ircantec et l'Agirc-Arrco d'abord : la
  // réversion d'un autre régime de base compte aux ressources du régime
  // général ; celle des complémentaires du régime général et des
  // indépendants, non (R. 353-1, 2°), et le RAFP, complémentaire de la
  // fonction publique, le dit dans sa fiche (`compte_aux_ressources`).
  let autresBases = 0.0;
  for (const [regime, base, fiabilite] of servies) {
    const fiche = table.ficheDuRegime(regime);
    if (fiche === null) {
      lignes.set(regime, new ReversionRegime({
        regime, base, montant: 0.0, motif: "non_portee",
      }));
      continue;
    }
    if (APRES_LES_BASES.includes(fiche.id)) {
      continue;
    }
    const version = table.version(fiche, lendemain, deces);
    const parametres = version.parametres;
    if (parametres.rien_apres_un_capital && enCapital.has(regime)) {
      // Un droit direct versé en capital ne laisse rien à reverser : la ligne
      // ne s'écrit pas, comme celle d'un régime qui ne sert rien.
      continue;
    }
    const taux = Number(parametres.taux);
    if (fiche.id === "reversion_fonction_publique") {
      const servie = mariageSuffit(parametres, conjoint, deces, depart, enfants);
      const montant = servie ? taux * base : 0.0;
      autresBases += montant;
      lignes.set(regime, ligne(regime, base, montant, servie ? "servie" : "mariage",
        fiche, version, taux, lendemain, fiabilite));
      continue;
    }
    if (fiche.id === "reversion_rafp") {
      const montant = taux * base;
      if (parametres.compte_aux_ressources) {
        autresBases += montant;
      }
      lignes.set(regime, ligne(regime, base, montant, "servie", fiche, version, taux,
        lendemain, fiabilite));
      continue;
    }
    if (fiche.id === "reversion_ircantec") {
      const naissance = chrono.naissance(carriere.chronologie, carriere.personne).debut;
      const servie = mariageIrcantec(parametres, conjoint, naissance, deces, depart, enfants);
      let dateEffet = aLAge(conjoint.naissance, lendemain,
        ageIrcantec(parametres, conjoint.sexe));
      if ((parametres.deux_enfants_sans_age ?? []).includes(conjoint.sexe)
          && enfantsDeMoinsDe(carriere, deces,
            Math.trunc(Number(parametres.deux_enfants_moins_de_ans))) >= 2) {
        // Deux enfants de moins de vingt et un ans à sa charge au décès lèvent
        // l'âge (article 21) : la réversion part au mois qui suit le décès.
        dateEffet = lendemain;
      }
      lignes.set(regime, ligne(regime, base, servie ? taux * base : 0.0,
        servie ? "servie" : "mariage", fiche, version, taux, dateEffet, fiabilite));
      continue;
    }
    let dateEffet = aLAge(conjoint.naissance, lendemain,
      ageAgircArrco(parametres, regime, conjoint.sexe));
    if (conjoint.invalidite !== null && conjoint.invalidite !== undefined
        && parametres.invalidite_sans_age) {
      // L'invalidité du survivant, au décès ou plus tard, lève l'âge : la
      // réversion part au premier jour du mois qui la suit.
      const levee = moisSuivant(conjoint.invalidite);
      const plusTot = levee > lendemain ? levee : lendemain;
      if (plusTot < dateEffet) {
        dateEffet = plusTot;
      }
    }
    const enfantsACharge = parametres.deux_enfants_a_charge_moins_de_ans;
    if (enfantsACharge !== null && enfantsACharge !== undefined
        && enfantsDeMoinsDe(carriere, deces, Math.trunc(Number(enfantsACharge))) >= 2) {
      // Deux enfants à charge du survivant au décès lèvent l'âge (article
      // 110), et la réversion reste servie quand ils cessent de l'être
      // (article 111) : elle part au mois qui suit le décès.
      dateEffet = lendemain;
    }
    // La majoration pour enfants du défunt « réversible au taux de 100 % »
    // (article 109) : en plus des 60 %, qui ne la comptent pas.
    const majoration = Number(parametres.majoration_reversible ?? 0.0)
      * ((majorations ?? {})[regime] ?? 0.0);
    lignes.set(regime, ligne(regime, base, taux * base + majoration, "servie", fiche,
      version, taux, dateEffet, fiabilite, majoration));
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

  // La complémentaire des indépendants en dernier : ses ressources sont celles
  // de R. 353-1, que les réversions de tous les régimes de base grossissent
  // (articles 17 et 35 de son règlement). Un dépassement de son plafond réduit
  // ses réversions à due concurrence, chacune au prorata de son montant.
  const independantes = [];
  for (const [regime, base, fiabilite] of servies) {
    const fiche = table.ficheDuRegime(regime);
    if (fiche === null || fiche.id !== "reversion_rci") {
      continue;
    }
    const version = table.version(fiche, lendemain, deces);
    if ((version.parametres.portee ?? true) === false) {
      lignes.set(regime, new ReversionRegime({
        regime, base, montant: 0.0, motif: "non_portee",
      }));
      continue;
    }
    independantes.push([regime, base, fiabilite, fiche, version]);
  }
  if (independantes.length > 0) {
    const premiers = independantes[0][4].parametres;
    const plafondAnnuel = Number(premiers.plafond_pass)
      * moteur.macro.plafond_securite_sociale.valeur(annee);
    let brut = 0.0;
    for (const [, base, , , version] of independantes) {
      brut += Number(version.parametres.taux) * base;
    }
    const depassement = Math.max(0.0, ressources + autresBases + brut - plafondAnnuel);
    for (const [regime, base, fiabilite, fiche, version] of independantes) {
      const parametres = version.parametres;
      const taux = Number(parametres.taux);
      let montant = taux * base;
      let motif = "servie";
      if (depassement > 0) {
        montant = Math.max(0.0, montant - depassement * montant / brut);
        motif = "ecretee";
      }
      const dateEffet = aLAge(conjoint.naissance, lendemain, Number(parametres.age_minimum));
      lignes.set(regime, ligne(regime, base, montant, motif, fiche, version, taux,
        dateEffet, fiabilite));
    }
  }

  return new Reversion({
    personne: conjoint.personne, defunt: carriere.personne, deces, annee,
    ressources, ressources_presumees: presumees,
    regimes: servies.filter(([regime]) => lignes.has(regime))
      .map(([regime]) => lignes.get(regime)),
    deces_suppose: decesSuppose !== null,
  });
}
