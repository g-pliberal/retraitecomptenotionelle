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
 * fonction publique et la CNRACL (`reversion_fonction_publique`), la CRPCEN
 * (`reversion_crpcen`), les IEG (`reversion_ieg`), la SNCF
 * (`reversion_sncf`), l'Agirc-Arrco
 * (`reversion_agirc_arrco`), le RAFP (`reversion_rafp`),
 * l'Ircantec (`reversion_ircantec`), la complémentaire des indépendants
 * (`reversion_rci`). Les autres régimes n'ont pas encore de fiche : leur ligne
 * le dit, sans montant. Le régime général et les régimes alignés : le taux de
 * la pension sans le minimum contributif qui la relevait (L. 351-10), avec ce
 * que le maximum des pensions en avait retiré, porté au minimum de D. 353-1,
 * réduit du dépassement du plafond — d'une personne seule, ou du ménage du
 * survivant qui vit en couple, ses revenus d'activité abattus à cinquante-cinq
 * ans —, ramené au maximum de la réversion, la
 * surcote en sus, réduit avant juillet 2004 par la limite de cumul avec les
 * retraites du survivant (D. 355-1), majoré de 10 % pour trois enfants
 * (R. 353-2), de la majoration forfaitaire pour enfant à charge (L. 353-5),
 * puis de 11,1 % sous le plafond de L. 353-6. Ce qui n'est pas encore porté, et les
 * montants — ceux de l'année du décès —, sont dits dans l'en-tête du Python.
 * Sans décès déclaré,
 * l'échéancier liquide une réversion d'essai pour un décès supposé juste après
 * le départ (présomption `deces_apres_le_depart`). Mort avant son départ,
 * l'assuré laisse la réversion de la pension qu'il « eût obtenue » à son décès,
 * sans décote (R. 353-6), que l'échéancier liquide. Chaque régime la partage
 * avec les précédents conjoints que sa fiche admet, au prorata des mariages en
 * mois (`partDuSurvivant`), et l'éteint au mois qui suit l'union nouvelle du
 * survivant quand sa fiche le dit (`jusquAuRemariage`).
 */

import * as chrono from "../chronologie.js";
import { Fiabilite, fiabiliteDepuisTexte, nomFiabilite } from "../serie.js";
import {
  REGIMES_ALIGNES, REGIMES_ALIGNES_TETE, luraApplicable, regimesDe, teteDeSuccession,
} from "./coordonner.js";
import { maximumDesPensions } from "./liquider.js";

/** La version du schéma que `Reversion.donnees` suit. */
export const SCHEMA_VERSION = 1;

/** Ce que dit une ligne dont le montant est nul, ou qui n'est pas servie en entier. */
export const MOTIFS = Object.freeze({
  servie: "servie",
  minimum: "portée au minimum de la réversion (D. 353-1 ; décret n° 2008-639, article 18)",
  maximum: "ramenée au maximum de la réversion, son taux du maximum des pensions",
  ecretee: "réduite à due concurrence du plafond de ressources",
  ressources: "ressources au-dessus du plafond",
  cumul: "réduite par la limite de cumul avec ses retraites personnelles (D. 355-1)",
  mariage: "condition d'antériorité ou de durée du mariage non remplie",
  remariage: "perdue par l'union qu'il a formée avant sa date d'effet",
  non_portee: "la réversion de ce régime n'est pas encore portée",
});

/**
 * Les fiches dont les réversions se chiffrent après les autres, parce que celles
 * des autres régimes de base comptent à leurs ressources : le régime général et
 * les régimes alignés, puis la complémentaire des indépendants.
 */
export const APRES_LES_BASES = Object.freeze(["reversion", "reversion_rci"]);

/**
 * Les fiches qui servent la moitié de la pension sans âge ni ressources, sous la
 * condition de mariage de L. 39 : voir le Python.
 */
export const MOITIE_SOUS_CONDITION_DE_MARIAGE = Object.freeze([
  "reversion_fonction_publique", "reversion_crpcen",
]);

/**
 * Les fiches des régimes de base autres que le régime général et les régimes
 * alignés, dont les réversions servies divisent les retraites du survivant et
 * la limite forfaitaire du cumul d'avant juillet 2004 : voir le Python.
 */
export const AUTRES_BASES = Object.freeze([...MOITIE_SOUS_CONDITION_DE_MARIAGE,
  "reversion_ieg", "reversion_sncf"]);

/**
 * Les fiches qui reversent la moitié de la majoration pour enfants du défunt
 * avec la moitié de sa pension, les IEG et la SNCF : voir le Python.
 */
export const MOITIE_MAJORATION_COMPRISE = Object.freeze(["reversion_ieg", "reversion_sncf"]);

/**
 * Les lignes de la cascade dont `reversion` lit la part dans chaque pension
 * (`minima`) : le minimum contributif, sans lequel le régime général reverse la
 * pension, et le minimum de pension de la SNCF, dont la pension relevée se
 * reverse au minimum de l'article 18.
 */
export const MINIMA_REVERSES = Object.freeze(["minimum_contributif", "minimum_pension_sncf"]);

/** La fiche de la majoration forfaitaire pour enfant à charge (L. 353-5). */
export const MAJORATION_FORFAITAIRE = "majoration_forfaitaire_reversion";

/**
 * Les régimes dont les durées d'assurance du défunt s'additionnent pour
 * proratiser le minimum de la réversion du régime général depuis le 1er juillet
 * 2004, chacun sous sa tête de succession (`groupesDuMinimum`) : voir le Python.
 */
export const REGIMES_DU_MINIMUM = Object.freeze([
  "regime_general", "msa_salaries", "msa_non_salaries", "organic", "cancava", "rsi",
  "cnavpl", "cavimac",
]);

/** La majoration de L. 353-6 ne prend pas effet avant cette date. */
export const DEBUT_DE_LA_MAJORATION = "2010-01-01";

/** La réversion d'un régime du défunt. */
export class ReversionRegime {
  /**
   * `base` : la pension du défunt dans ce régime, à l'année des montants ;
   * `date_effet` : le premier jour du mois qui suit le décès, ou qui suit
   * l'âge requis.
   */
  constructor({ regime, base, montant, motif, fiche = null, version = null, texte = null,
    taux = 0.0, date_effet = null, fiabilite = Fiabilite.ESTIMEE, majoration = 0.0,
    minimum = 0.0, majoration_trois_enfants = 0.0, majoration_petites_retraites = 0.0,
    majoration_petites_retraites_effet = null, minimum_contributif = 0.0,
    ecretement_du_maximum = 0.0, maximum = 0.0, plafond = 0.0,
    ressources_retenues = 0.0, part = 1.0, fin = null, limite_cumul = 0.0,
    majoration_forfaitaire_enfants = 0.0, majoration_forfaitaire_enfants_etapes = [],
    majorations_forfaitaires = [], cumul_effet = null, reduction_du_cumul = 0.0,
    revision_effet = null, reduction_de_la_revision = 0.0, derniere_revision = null }) {
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
    // Le minimum de D. 353-1, soixantièmes et prorata faits, ou de l'article 18
    // du décret n° 2008-639 à la SNCF, sa part faite ; 0 sans lui.
    this.minimum = minimum;
    // La majoration de 10 % du survivant de trois enfants, comprise dans le montant.
    this.majoration_trois_enfants = majoration_trois_enfants;
    // La majoration de 11,1 % (L. 353-6) et le jour où elle commence :
    // comprise dans le montant quand elle commence à la date d'effet, à part sinon.
    this.majoration_petites_retraites = majoration_petites_retraites;
    this.majoration_petites_retraites_effet = majoration_petites_retraites_effet;
    // La part de `base` que le minimum contributif y ajoute (L. 351-10) : la
    // réversion du régime général et des régimes alignés se calcule sans elle.
    this.minimum_contributif = minimum_contributif;
    // Ce que le maximum des pensions avait retiré de `base`, que la réversion du
    // régime général reprend, et le maximum de cette réversion ; 0 sans lui.
    this.ecretement_du_maximum = ecretement_du_maximum;
    this.maximum = maximum;
    // Le plafond de ressources auquel la réversion se mesure, d'une personne
    // seule ou du ménage, et les ressources qu'il retient à côté d'elle ; 0
    // sans plafond.
    this.plafond = plafond;
    this.ressources_retenues = ressources_retenues;
    // La part du survivant, partagée avec les précédents conjoints au prorata
    // des mariages (L. 353-3) : 1 sans eux.
    this.part = part;
    // Le jour où l'union nouvelle du survivant éteint la réversion, quand elle
    // suit la date d'effet ; null sinon.
    this.fin = fin;
    // La limite de cumul de la réversion d'avant juillet 2004 avec les
    // retraites du survivant (D. 355-1) ; 0 sans elle.
    this.limite_cumul = limite_cumul;
    // La majoration forfaitaire pour enfant à charge (L. 353-5), comprise dans
    // le montant, et ce qu'elle devient depuis chaque jour où le nombre des
    // enfants à charge change, `[jour, montant]`, la dernière étape nulle.
    this.majoration_forfaitaire_enfants = majoration_forfaitaire_enfants;
    this.majoration_forfaitaire_enfants_etapes = Object.freeze(
      [...majoration_forfaitaire_enfants_etapes]);
    // Les majorations forfaitaires qui relèvent la réversion après sa date
    // d'effet, chacune `[jour, montant]`, hors du montant.
    this.majorations_forfaitaires = Object.freeze([...majorations_forfaitaires]);
    // Le jour où la retraite personnelle du survivant, qui suit la date
    // d'effet, revoit la réversion d'avant juillet 2004 par la limite de cumul
    // de ce jour, et ce qu'elle en retire alors, hors du montant ; null et 0
    // sans elle.
    this.cumul_effet = cumul_effet;
    this.reduction_du_cumul = reduction_du_cumul;
    // Le jour où la retraite personnelle du survivant, qui suit la date
    // d'effet, revoit la réversion sous le plafond de ressources — la recalcule
    // aux règles de 2004 quand elle les précède, la révise sinon (R. 353-1-1) —,
    // et ce qu'elle en retire alors, négatif quand elle y ajoute, hors du
    // montant ; null et 0 sans elle. Puis le jour d'où elle n'est plus
    // révisable, trois mois après sa retraite ; null sans elle.
    this.revision_effet = revision_effet;
    this.reduction_de_la_revision = reduction_de_la_revision;
    this.derniere_revision = derniere_revision;
    Object.freeze(this);
  }

  /** Une copie, ces champs changés. */
  avec(changes) {
    return new ReversionRegime({ ...this, ...changes });
  }

  donnees() {
    return {
      regime: this.regime, base: this.base, taux: this.taux, montant: this.montant,
      motif: this.motif, date_effet: this.date_effet, fiche: this.fiche,
      version: this.version, texte: this.texte, fiabilite: nomFiabilite(this.fiabilite),
      majoration: this.majoration, minimum: this.minimum,
      majoration_trois_enfants: this.majoration_trois_enfants,
      majoration_petites_retraites: this.majoration_petites_retraites,
      majoration_petites_retraites_effet: this.majoration_petites_retraites_effet,
      minimum_contributif: this.minimum_contributif,
      ecretement_du_maximum: this.ecretement_du_maximum,
      maximum: this.maximum, plafond: this.plafond,
      ressources_retenues: this.ressources_retenues, part: this.part, fin: this.fin,
      limite_cumul: this.limite_cumul,
      majoration_forfaitaire_enfants: this.majoration_forfaitaire_enfants,
      majoration_forfaitaire_enfants_etapes: this.majoration_forfaitaire_enfants_etapes.map(
        ([date, montant]) => ({ date, montant })),
      majorations_forfaitaires: this.majorations_forfaitaires.map(
        ([date, montant]) => ({ date, montant })),
      cumul_effet: this.cumul_effet,
      reduction_du_cumul: this.reduction_du_cumul,
      revision_effet: this.revision_effet,
      reduction_de_la_revision: this.reduction_de_la_revision,
      derniere_revision: this.derniere_revision,
    };
  }
}

/** Ce que la liquidation d'une réversion écrit : régime par régime. */
export class Reversion {
  constructor({ personne, defunt, deces, annee, ressources, ressources_presumees, regimes,
    deces_suppose = false, avant_le_depart = false }) {
    this.personne = personne;
    this.defunt = defunt;
    this.deces = deces;
    // Le décès est-il supposé (présomption `deces_apres_le_depart`) ?
    this.deces_suppose = deces_suppose;
    // Le défunt est-il mort avant son départ ? La réversion porte alors sur la
    // pension qu'il « eût obtenue » à son décès (R. 353-6).
    this.avant_le_depart = avant_le_depart;
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
      deces: this.deces, deces_suppose: this.deces_suppose,
      avant_le_depart: this.avant_le_depart, annee: this.annee,
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
/**
 * La durée d'un mariage, en mois : « déterminée de date à date et arrondie au
 * nombre de mois inférieur » (R. 353-4).
 */
export function moisDeMariage(debut, fin) {
  let mois = (Number(fin.slice(0, 4)) - Number(debut.slice(0, 4))) * 12
    + Number(fin.slice(5, 7)) - Number(debut.slice(5, 7));
  if (Number(fin.slice(8, 10)) < Number(debut.slice(8, 10))) {
    mois -= 1;
  }
  return Math.max(0, mois);
}

/**
 * La part du conjoint survivant dans la réversion d'un régime : la durée de son
 * mariage, jusqu'au décès, rapportée à celle de tous les mariages dont les
 * conjoints y ont droit — les précédents que `admis` retient. Voir
 * `_part_du_survivant` du Python.
 */
function partDuSurvivant(carriere, conjoint, deces, admis) {
  let autres = 0;
  for (const ex of carriere.exConjoints) {
    if (admis(ex)) {
      autres += moisDeMariage(ex.mariage, ex.divorce);
    }
  }
  if (!autres) {
    return 1.0;
  }
  const propre = moisDeMariage(conjoint.mariage, deces);
  return propre / (propre + autres);
}

/** Le précédent conjoint s'est-il remarié avant le décès de l'assuré ? */
function remarieAvant(ex, deces) {
  return ex.remariage !== null && ex.remariage !== undefined && ex.remariage <= deces;
}

/**
 * Les précédents conjoints qui partagent la réversion du régime général : tous
 * depuis juillet 2004 ; avant, les seuls non remariés dont le mariage a duré
 * deux ans, sauf enfant. Voir `_admis_au_regime_general` du Python.
 */
function admisAuRegimeGeneral(parametres, deces, enfants) {
  if (parametres.ex_conjoints === "tous") {
    return () => true;
  }
  const annees = parametres.mariage_minimum_annees;
  return (ex) => !remarieAvant(ex, deces)
    && (!annees || enfants > 0 || chrono.anneesRevolues(ex.mariage, ex.divorce) >= annees);
}

/**
 * Les précédents conjoints qui partagent la réversion d'un autre régime, selon
 * ce que la version dit (`ex_conjoints`) : aucun, ceux qui ne se sont pas
 * remariés avant le décès, ou tous. Voir `_admis_ailleurs` du Python.
 */
function admisAilleurs(parametres, deces) {
  const regle = parametres.ex_conjoints ?? "aucun";
  if (regle === "tous") {
    return () => true;
  }
  if (regle === "non_remaries") {
    return (ex) => !remarieAvant(ex, deces);
  }
  return () => false;
}

/**
 * La réversion entière au conjoint survivant, malgré les précédents conjoints,
 * quand la version le dit (`entiere_au_conjoint`) : à l'Agirc-Arrco, le
 * conjoint marié avant le 13 janvier 1998, quand le mariage précédent du
 * défunt a été dissous avant le 1er juillet 1980. Voir `_entiere_au_conjoint`
 * du Python.
 */
function entiereAuConjoint(parametres, carriere, conjoint) {
  const regle = parametres.entiere_au_conjoint;
  if (!regle || carriere.exConjoints.length === 0
      || conjoint.mariage === null || conjoint.mariage === undefined) {
    return false;
  }
  const dernierDivorce = carriere.exConjoints.reduce(
    (dernier, ex) => (ex.divorce > dernier ? ex.divorce : dernier), "");
  return conjoint.mariage < regle.marie_avant
    && dernierDivorce < regle.precedent_dissous_avant;
}

/**
 * Le jour où l'union nouvelle du survivant éteint la réversion d'un régime qui
 * la retire à cette forme d'union : le premier jour du mois qui suit l'union ;
 * `null` sinon. Voir `_fin_au_remariage` du Python.
 */
function finAuRemariage(parametres, conjoint) {
  if (conjoint.nouvelle_union === null || conjoint.nouvelle_union === undefined
      || conjoint.nouvelle_union_depuis === null || conjoint.nouvelle_union_depuis === undefined
      || !(parametres.perte_au_remariage ?? []).includes(conjoint.nouvelle_union)) {
    return null;
  }
  return moisSuivant(conjoint.nouvelle_union_depuis);
}

/**
 * La ligne, arrêtée par l'union nouvelle du survivant : sans montant quand
 * l'union précède sa date d'effet, jusqu'à elle sinon.
 */
function jusquAuRemariage(ligne, parametres, conjoint) {
  const fin = finAuRemariage(parametres, conjoint);
  if (fin === null || ligne.date_effet === null || ligne.montant <= 0) {
    return ligne;
  }
  if (fin <= ligne.date_effet) {
    return ligne.avec({ montant: 0.0, motif: "remariage", majoration: 0.0 });
  }
  return ligne.avec({ fin });
}

/**
 * La ligne sans montant quand le survivant vit, au décès, dans une union que la
 * version dit sans jouissance : voir `_sans_jouissance_au_deces` du Python.
 */
function sansJouissanceAuDeces(ligne, parametres, conjoint, deces) {
  const depuis = conjoint.nouvelle_union_depuis ?? null;
  if (ligne.montant > 0
      && (parametres.sans_jouissance_au_deces ?? []).includes(conjoint.nouvelle_union)
      && depuis !== null && depuis <= deces) {
    return ligne.avec({ montant: 0.0, motif: "remariage", majoration: 0.0 });
  }
  return ligne;
}

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
 * La condition de l'article 24 de l'annexe 3 au statut national des IEG : voir
 * `_mariage_ieg` du Python.
 */
function mariageIeg(parametres, conjoint, deces, depart, enfants) {
  const minimum = parametres.mariage_minimum_annees ?? null;
  if (minimum === null || enfants > 0 || conjoint.mariage <= depart) {
    return true;
  }
  return chrono.anneesRevolues(conjoint.mariage, deces) >= minimum;
}

/**
 * La condition de l'article 19, I, du décret n° 2008-639 : voir `_mariage_sncf`
 * du Python.
 */
function mariageSncf(parametres, conjoint, deces, depart, naissances) {
  if (naissances.some((naissance) => naissance < depart)) {
    return true;
  }
  if (chrono.anneesRevolues(conjoint.mariage, depart)
      >= parametres.mariage_cessation_minimum_annees) {
    return true;
  }
  const minimum = naissances.length > 0 ? parametres.mariage_minimum_annees_avec_enfant
    : parametres.mariage_minimum_annees;
  return chrono.anneesRevolues(conjoint.mariage, deces) >= minimum;
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
 * Le jour où la majoration de L. 353-6 peut commencer : le premier jour du mois
 * qui suit l'âge du taux plein, ou l'anniversaire même du survivant né le
 * premier jour d'un mois. L'âge se compte en mois. Voir le Python.
 */
function auTauxPlein(naissance, age) {
  const atteint = atteintA(naissance, age);
  return naissance.slice(8, 10) === "01" ? atteint : moisSuivant(atteint);
}

/** Le jour où le survivant né le jour `naissance` atteint `age`, compté en mois. */
function atteintA(naissance, age) {
  const mois = Math.round(age * 12);
  const depuis = Number(naissance.slice(5, 7)) - 1 + mois;
  const annee = Number(naissance.slice(0, 4)) + Math.floor(depuis / 12);
  const numero = (depuis % 12) + 1;
  return `${String(annee).padStart(4, "0")}-${String(numero).padStart(2, "0")}-`
    + naissance.slice(8, 10);
}

/**
 * La date d'effet que l'âge de la version reporte : l'âge requis, ou, avant
 * 1973, soixante ans pour le survivant inapte, que le modèle tient pour celui
 * qui déclare son invalidité, au plus tôt le mois qui la suit. Voir le Python.
 */
function dateDEffetDuRegimeGeneral(parametres, conjoint, lendemain) {
  let dateEffet = aLAge(conjoint.naissance, lendemain, Number(parametres.age_minimum));
  const inaptitude = parametres.age_inaptitude ?? null;
  if (inaptitude !== null && conjoint.invalidite !== null
      && conjoint.invalidite !== undefined) {
    const inapte = aLAge(conjoint.naissance, lendemain, Number(inaptitude));
    const apres = moisSuivant(conjoint.invalidite);
    const possible = inapte > apres ? inapte : apres;
    dateEffet = possible < dateEffet ? possible : dateEffet;
  }
  return dateEffet;
}

/**
 * La première date d'effet de la réversion du régime général : la plus proche
 * des dates que chaque version permet, au plus tôt à son début et à l'âge
 * qu'elle requiert, avant sa fin. Voir le Python.
 */
function premiereDateDEffet(table, fiche, conjoint, lendemain, deces) {
  let premiere = null;
  for (const version of fiche.versions) {
    const [debut, fin] = version.bornes["liquidation.date_effet"] ?? [null, null];
    let jour = debut !== null && debut > lendemain ? debut : lendemain;
    jour = dateDEffetDuRegimeGeneral(version.parametres, conjoint, jour);
    if (fin !== null && jour >= fin) {
      continue;
    }
    const retenue = table.version(fiche, jour, deces);
    if (retenue !== null && retenue.id === version.id && (premiere === null || jour < premiere)) {
      premiere = jour;
    }
  }
  return premiere ?? lendemain;
}

/**
 * La réversion d'avant juillet 2004 qu'il reste quand le survivant a ses
 * propres retraites, et la limite de cumul : `[montant, limite]` (D. 355-1).
 * Voir `_cumuler` du Python.
 */
function cumuler(parametres, montant, retraites, principale, forfaitaire, reversions) {
  const regle = parametres.cumul ?? null;
  if (regle === null || montant <= 0 || retraites <= 0) {
    return [montant, 0.0];
  }
  const retenues = retraites / Math.max(1, reversions);
  if (regle === "aucun") {
    return [Math.max(0.0, montant - retenues), 0.0];
  }
  const limite = Math.max(montant, Number(parametres.cumul_taux) * (retenues + principale),
    (forfaitaire ?? 0.0) / Math.max(1, reversions));
  return [Math.max(0.0, montant - Math.max(0.0, montant + retenues - limite)), limite];
}

/**
 * Les retraites personnelles du survivant servies le jour `jour` : toutes, sauf
 * quand sa propre retraite, qu'il date, ne prend effet qu'après. Voir
 * `_retraites_au` du Python.
 */
function retraitesAu(conjoint, retraites, jour) {
  return conjoint.retraite !== null && conjoint.retraite !== undefined && conjoint.retraite > jour
    ? 0.0 : retraites;
}

/**
 * Avant cette date, la limite revue à l'attribution des droits personnels du
 * survivant tenait la pension du défunt pour la réversion servie rapportée au
 * taux de la limite ; depuis, pour celle qui a servi de base à la réversion
 * (circulaire Cnav n° 105/90, § 12 et 13). Voir le Python.
 */
export const PRINCIPALE_REVALORISEE_DEPUIS = "1990-11-15";

/**
 * La réversion d'avant juillet 2004 revue à l'attribution de la retraite
 * personnelle du survivant, quand elle suit sa date d'effet : `[jour, servie,
 * ce qu'il en reste, limite, fiabilité]`, ou `null` sans elle. Voir
 * `_cumul_a_la_retraite` du Python.
 */
function cumulALaRetraite(moteur, fiche, conjoint, deces, annee, dateEffet, servie,
  ulterieures, retraites, principale, reversions, personnelles = []) {
  const jour = conjoint.retraite ?? null;
  if (jour === null || jour <= dateEffet || servie <= 0 || retraites <= 0) {
    return null;
  }
  const alors = moteur.reversions.version(fiche, jour, deces);
  const parametres = alors === null ? {} : alors.parametres;
  if ((parametres.cumul ?? null) === null) {
    return null;
  }
  let enPaiement = servie;
  for (const [quand, montant] of ulterieures) {
    if (quand <= jour) {
      enPaiement += montant;
    }
  }
  let pensionDuDefunt = principale;
  for (const [quand, taux] of personnelles) {
    if (dateEffet < quand && quand <= jour) {
      pensionDuDefunt *= 1 + taux;
    }
  }
  if (jour < PRINCIPALE_REVALORISEE_DEPUIS && parametres.cumul_taux) {
    pensionDuDefunt = enPaiement / Number(parametres.cumul_taux);
  }
  let fiabilite = fiabiliteDepuisTexte(parametres.fiabilite);
  const anneeDuJour = Number(jour.slice(0, 4));
  const forfaitaire = moteur.reversions.limiteCumul(anneeDuJour);
  let enEuros = null;
  if (forfaitaire !== null) {
    const [coefficient, fiabiliteCoefficient] = moteur.revalorisationsPensions.generale(
      `${String(annee).padStart(4, "0")}-12-31`,
      `${String(anneeDuJour).padStart(4, "0")}-12-31`, false, null);
    enEuros = forfaitaire[0] / coefficient;
    fiabilite = Math.min(fiabilite, forfaitaire[1], fiabiliteCoefficient);
  }
  const [reste, limite] = cumuler(parametres, enPaiement, retraites, pensionDuDefunt, enEuros,
    reversions);
  return [jour, enPaiement, reste, limite, fiabilite];
}

/**
 * L'année dont le SMIC fait le plafond d'une révision du jour `jour` : la
 * sienne, ou, quand le barème ne la publie pas encore, la dernière qu'il
 * publie, jamais avant l'année des montants. Voir `_annee_du_plafond` du
 * Python.
 */
function anneeDuPlafond(moteur, annee, jour) {
  let alors = Number(jour.slice(0, 4));
  while (alors > annee && moteur.macro.smic_horaire.fiabilite(alors) <= Fiabilite.ESTIMEE) {
    alors -= 1;
  }
  return alors;
}

/**
 * La réversion revue sous le plafond de ressources quand la retraite
 * personnelle du survivant, qu'il date, suit sa date d'effet : `[jour, servie,
 * revue, fiabilité]`, ou `null` sans elle. Attribuée avant juillet 2004, une
 * retraite prise depuis la recalcule aux règles de ressources, à sa date
 * d'effet ; attribuée depuis, la retraite la révise le mois qui suit
 * (R. 353-1-1). Voir `_revision_a_la_retraite` du Python.
 */
function revisionALaRetraite(moteur, fiche, parametres, conjoint, deces, annee, dateEffet,
  servie, entiere, ulterieures, ressources, retraites, bases) {
  const jour = conjoint.retraite ?? null;
  if (jour === null || jour <= dateEffet || retraites <= 0) {
    return null;
  }
  let revision;
  if ((parametres.cumul ?? null) !== null) {
    if (servie <= 0) {
      return null;
    }
    revision = jour;
  } else if (parametres.ressources === "ecretement") {
    revision = moisSuivant(jour);
  } else {
    return null;
  }
  const alors = moteur.reversions.version(fiche, revision, deces);
  const regles = alors === null ? {} : alors.parametres;
  if (regles.ressources !== "ecretement") {
    return null;
  }
  let venues = 0;
  for (const [quand, montant] of ulterieures) {
    if (quand <= revision) {
      venues += montant;
    }
  }
  const [retenues, facteur] = ressourcesDuPlafond(regles, conjoint, ressources, revision);
  const an = anneeDuPlafond(moteur, annee, revision);
  const [coefficient, fiabiliteCoefficient] = moteur.revalorisationsPensions.generale(
    `${String(annee).padStart(4, "0")}-12-31`, `${String(an).padStart(4, "0")}-12-31`,
    false, 0.0);
  const plafond = facteur * Number(regles.plafond_smic_heures)
    * moteur.macro.smic_horaire.valeur(an) / coefficient;
  const revue = Math.max(0.0, Math.min(entiere + venues, plafond - retenues - bases));
  const fiabilite = Math.min(fiabiliteDepuisTexte(regles.fiabilite), fiabiliteCoefficient);
  return [revision, servie + venues, revue, fiabilite];
}

/** Le premier jour du troisième mois qui suit celui de `jour`. */
function troisMoisApres(jour) {
  return moisSuivant(moisSuivant(moisSuivant(jour)));
}

/**
 * Le jour d'où la réversion soumise aux règles de ressources n'est plus
 * révisable : trois mois après la retraite que le survivant date, ou sa date
 * d'effet quand il en jouit depuis plus longtemps (R. 353-1-1) ; `null` sans
 * retraite datée, ou pour la réversion d'avant juillet 2004 qu'aucune retraite
 * n'a recalculée. Voir `_derniere_revision` du Python.
 */
function derniereRevision(parametres, conjoint, dateEffet, recalculee) {
  const retraite = conjoint.retraite ?? null;
  if (retraite === null || (parametres.ressources !== "ecretement" && !recalculee)) {
    return null;
  }
  const trois = troisMoisApres(retraite);
  return trois > dateEffet ? trois : dateEffet;
}

/**
 * Les versions de la majoration forfaitaire pour enfant, dans l'ordre de leurs
 * dates : `[début, fin, paramètres]`, la fin exclue. Voir
 * `_versions_de_la_charge` du Python.
 */
function versionsDeLaCharge(fiche) {
  const bornees = fiche.versions.map((version) => [
    ...(version.bornes["liquidation.date_effet"] ?? [null, null]), version.parametres]);
  bornees.sort(([a], [b]) => ((a ?? "") < (b ?? "") ? -1 : ((a ?? "") > (b ?? "") ? 1 : 0)));
  return bornees;
}

/**
 * Des périodes `[début, fin)`, réunies quand elles se chevauchent ou se
 * touchent, dans l'ordre. Voir `_reunir` du Python.
 */
function reunir(periodes) {
  const triees = [...periodes].sort(([a, b], [c, d]) => (a < c ? -1 : a > c ? 1
    : b < d ? -1 : b > d ? 1 : 0));
  const reunies = [];
  for (const [debut, fin] of triees) {
    const derniere = reunies[reunies.length - 1];
    if (derniere !== undefined && debut <= derniere[1]) {
      derniere[1] = derniere[1] > fin ? derniere[1] : fin;
    } else {
      reunies.push([debut, fin]);
    }
  }
  return reunies;
}

/**
 * Les jours, depuis `depuis`, où l'enfant né le `naissance` est à la charge du
 * survivant, en périodes `[début, fin)` : sous l'âge de la version en vigueur
 * chaque jour (R. 353-9, R. 313-12, R. 161-4), et pendant ses `prolongations`
 * sous vingt ans. Voir `_jours_a_charge` du Python.
 */
function joursACharge(fiche, naissance, depuis, prolongations) {
  const periodes = [];
  for (const [debut, fin, parametres] of versionsDeLaCharge(fiche)) {
    const ans = parametres.enfant_moins_de_ans ?? null;
    if (ans === null) {
      continue;
    }
    const de = [debut ?? depuis, depuis, naissance].reduce((a, b) => (a > b ? a : b));
    if (fin !== null && de >= fin) {
      continue;
    }
    const limites = [[de, chrono.plusAns(naissance, Math.trunc(Number(ans)))]];
    const prolonge = parametres.enfant_prolonge_moins_de_ans ?? null;
    if (prolonge !== null) {
      const vingtAns = chrono.plusAns(naissance, Math.trunc(Number(prolonge)));
      for (const [depuisLe, jusquAu] of prolongations) {
        limites.push([de > depuisLe ? de : depuisLe,
          jusquAu === null || vingtAns < jusquAu ? vingtAns : jusquAu]);
      }
    }
    for (const [de_, limite] of limites) {
      const jusquA = fin !== null && fin < limite ? fin : limite;
      if (de_ < jusquA) {
        periodes.push([de_, jusquA]);
      }
    }
  }
  return reunir(periodes);
}

/**
 * Les périodes `[début, fin)` où la part d'un enfant est servie : dès la date
 * d'effet, dès le 1er janvier 1988 quand la majoration naît après elle, sinon
 * le premier jour du mois qui suit (R. 353-10) ; jusqu'au premier jour du mois
 * qui suit la fin de la charge. Voir `_parts_de_l_enfant` du Python.
 */
function partsDeLEnfant(jours, dateEffet, creation) {
  const parts = [];
  for (const [de, jusquA] of jours) {
    const debut = de === dateEffet || de === creation ? de : moisSuivant(de);
    const fin = moisSuivant(jusquA);
    if (debut < fin) {
      parts.push([debut, fin]);
    }
  }
  return parts;
}

/**
 * La majoration forfaitaire ENTIÈRE pour enfant à charge (L. 353-5) : `[montant
 * annuel par enfant aux euros de annee, fiabilité, les périodes [début, fin) où
 * la part de chaque enfant est servie, dans l'ordre]` ; `null` quand elle n'est
 * jamais due. Elle s'attribue le jour où la première part commence ; toute
 * entière, elle cesse le mois qui suit la retraite du survivant, ou, avant
 * juillet 2004, l'union où il entre. Voir `_majoration_forfaitaire_enfants` du
 * Python.
 */
function majorationForfaitaireEnfants(moteur, carriere, conjoint, retraitesPersonnelles,
  dateEffet, annee) {
  const table = moteur.reversions;
  const fiche = table.fiche(MAJORATION_FORFAITAIRE);
  if (fiche === null) {
    return null;
  }
  const deces = carriere.deces ?? dateEffet;
  const debuts = versionsDeLaCharge(fiche)
    .filter(([debut, , parametres]) => parametres.servie && debut !== null)
    .map(([debut]) => debut);
  const creation = debuts.length === 0 ? null
    : debuts.reduce((a, b) => (a < b ? a : b));
  const parts = carriere.naissancesDesEnfants.flatMap(([enfant, naissance]) => partsDeLEnfant(
    joursACharge(fiche, naissance, dateEffet,
      chrono.prolongationsDeLaCharge(carriere.chronologie, enfant)), dateEffet, creation));
  if (parts.length === 0) {
    return null;
  }
  const attribution = parts.map(([debut]) => debut).reduce((a, b) => (a < b ? a : b));
  if (retraitesAu(conjoint, retraitesPersonnelles, attribution) > 0) {
    return null;
  }
  const version = table.version(fiche, attribution, deces);
  const parametres = version === null ? {} : version.parametres;
  if (!parametres.servie) {
    return null;
  }
  if (parametres.age_maximum !== null && parametres.age_maximum !== undefined
      && chrono.anneesRevolues(conjoint.naissance, attribution)
        >= Number(parametres.age_maximum)) {
    return null;
  }
  if (parametres.age_du_taux_plein) {
    const generation = Math.round((Number(conjoint.naissance.slice(0, 4))
      + (Number(conjoint.naissance.slice(5, 7)) - 1) / 12) * 1000) / 1000;
    const age = moteur.agesAnnulationDecote.age(generation);
    if (age === null || atteintA(conjoint.naissance, age[0]) <= attribution) {
      return null;
    }
  }
  if (parametres.refusee_en_couple && conjoint.nouvelle_union !== null
      && conjoint.nouvelle_union !== undefined
      && (conjoint.nouvelle_union_depuis ?? dateEffet) <= attribution) {
    return null;
  }
  let parEnfant = table.majorationEnfant(annee);
  if (parEnfant === null) {
    const anneeDeLAttribution = Number(attribution.slice(0, 4));
    const premiere = table.majorationEnfant(anneeDeLAttribution);
    if (premiere === null) {
      return null;
    }
    const [coefficient, fiabiliteCoefficient] = moteur.revalorisationsPensions.generale(
      `${String(annee).padStart(4, "0")}-12-31`,
      `${String(anneeDeLAttribution).padStart(4, "0")}-12-31`, false, null);
    parEnfant = [premiere[0] / coefficient, Math.min(premiere[1], fiabiliteCoefficient)];
  }
  // Ce qui l'arrête toute entière : sa propre retraite, puis, avant juillet
  // 2004, l'union où il entre après l'attribution.
  const arrets = [];
  if (conjoint.retraite !== null && conjoint.retraite !== undefined
      && conjoint.retraite > attribution) {
    arrets.push(moisSuivant(conjoint.retraite));
  }
  const union = conjoint.nouvelle_union_depuis ?? null;
  if (conjoint.nouvelle_union !== null && conjoint.nouvelle_union !== undefined
      && union !== null && union > attribution) {
    const alors = table.version(fiche, union, deces);
    if (alors !== null && alors.parametres.refusee_en_couple) {
      arrets.push(moisSuivant(union));
    }
  }
  const arret = arrets.length === 0 ? null : arrets.reduce((a, b) => (a < b ? a : b));
  const servies = parts.filter(([debut]) => arret === null || debut < arret)
    .map(([debut, fin]) => [debut, arret === null || fin < arret ? fin : arret]);
  servies.sort(([a, b], [c, d]) => (a < c ? -1 : a > c ? 1 : b < d ? -1 : b > d ? 1 : 0));
  return [parEnfant[0], Math.min(parEnfant[1], fiabiliteDepuisTexte(parametres.fiabilite)),
    servies];
}

/**
 * La dernière année cotisée de l'assuré dans chaque régime, jusqu'à l'année
 * `jusquA` : celle de sa dernière affiliation. Voir `_dernieres_affiliations`
 * du Python.
 */
function dernieresAffiliations(moteur, carriere, jusquA) {
  const dernieres = new Map();
  for (const ligne of carriere.lignes) {
    if (!ligne.cotise || ligne.annee > jusquA) {
      continue;
    }
    for (const code of regimesDe(moteur, ligne, ligne.annee,
      carriere.dateEntree(ligne.affiliation), ligne.revenu,
      moteur.macro.plafond_securite_sociale.valeur(ligne.annee))) {
      dernieres.set(code, Math.max(dernieres.get(code) ?? 0, ligne.annee));
    }
  }
  return dernieres;
}

/**
 * Le régime qui sert la majoration pour enfant, parmi les `candidats` : celui
 * de la dernière affiliation, puis la plus longue durée d'assurance, puis la
 * réversion la plus élevée, le régime général enfin (D. 173-21-1, D. 173-21-7,
 * R. 173-17-3 ; circulaire Cnav n° 76/88, fiche n° 7). Voir
 * `_regime_de_la_majoration` du Python.
 */
function regimeDeLaMajoration(moteur, carriere, candidats, jusquA, durees, reduites) {
  if (candidats.length < 2) {
    return candidats[0] ?? null;
  }
  const dernieres = dernieresAffiliations(moteur, carriere, jusquA);
  const cle = (regime) => [dernieres.get(regime) ?? 0, (durees ?? {})[regime] ?? 0,
    reduites.get(regime)[0], regime === "regime_general" ? 1 : 0];
  let choisi = candidats[0];
  for (const regime of candidats.slice(1)) {
    const [a, b] = [cle(regime), cle(choisi)];
    const premier = a.findIndex((valeur, i) => valeur !== b[i]);
    if (premier >= 0 && a[premier] > b[premier]) {
      choisi = regime;
    }
  }
  return choisi;
}

/**
 * Les majorations forfaitaires qui relèvent la réversion attribuée avant leur
 * date — 4 % au 1er décembre 1982, 3,846 % au 1er janvier 1995 —, chacune ce
 * qu'elle ajoute à la réversion portée au minimum et ramenée au maximum,
 * `[jour, montant]`. Voir `_majorations_ulterieures` du Python.
 */
function majorationsUlterieures(parametres, dateEffet, calcule, minimum, maximum,
  personnelles = [], autres = 0.0) {
  // `autres` : les réversions que le minimum compte avec elle (D. 634-14), que
  // les majorations de la réversion relèvent aussi : voir le Python.
  const servie = (facteur, propre) => {
    const montant = Math.max(minimum - autres * propre, calcule * facteur);
    return maximum > 0 ? Math.min(montant, maximum) : montant;
  };
  // Celles de la pension du défunt passent, le même jour, avant celle de la
  // réversion : voir le Python.
  const datees = [
    ...personnelles.filter(([jour]) => jour > dateEffet).map(([jour, taux]) => [jour, 0, taux]),
    ...(parametres.majorations_forfaitaires ?? [])
      .filter((majoration) => String(majoration.date) > dateEffet)
      .map((majoration) => [String(majoration.date), 1, Number(majoration.taux)]),
  ];
  datees.sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1
    : a[1] !== b[1] ? a[1] - b[1] : a[2] - b[2]));
  const ecrites = [];
  let facteur = 1.0;
  let propre = 1.0;
  for (const jour of [...new Set(datees.map(([quand]) => quand))]) {
    let nouveau = facteur;
    let nouveauPropre = propre;
    for (const [, sorte, taux] of datees.filter(([quand]) => quand === jour)) {
      nouveau *= 1 + taux;
      if (sorte === 1) {
        nouveauPropre *= 1 + taux;
      }
    }
    ecrites.push([jour, servie(nouveau, nouveauPropre) - servie(facteur, propre)]);
    facteur = nouveau;
    propre = nouveauPropre;
  }
  return ecrites;
}

/**
 * Le régime de chacun des régimes du minimum pour la liquidation de l'année
 * `annee` : sa tête de succession, ou celle des régimes alignés sous la
 * liquidation unique ; les droits d'avant 1973 de chaque caisse avec le régime
 * qui leur succède, quand la version compte leur réversion avec la sienne pour
 * le minimum (D. 634-14). Une `Map`, dans l'ordre de `REGIMES_DU_MINIMUM` :
 * voir le Python.
 */
function groupesDuMinimum(moteur, parametres, lura, annee) {
  const groupes = new Map();
  for (const code of REGIMES_DU_MINIMUM) {
    if (lura && REGIMES_ALIGNES.has(code)) {
      groupes.set(code, REGIMES_ALIGNES_TETE);
    } else {
      groupes.set(code, moteur.catalogue.contient(code)
        ? teteDeSuccession(moteur, code, annee) : code);
    }
  }
  if (parametres.minimum_avec_les_droits_d_avant_1973) {
    for (const [code, successeur] of Object.entries(parametres.droits_d_avant_1973 ?? {})) {
      groupes.set(code, groupes.get(successeur) ?? successeur);
    }
  }
  return groupes;
}

/**
 * La part du minimum de D. 353-1 que sert la réversion de `regime` : entière
 * avant le 1er décembre 1982 ; ensuite, autant de soixantièmes que le défunt a
 * de trimestres dans le régime, soixante au plus ; depuis le 1er juillet 2004,
 * sa durée dans le régime rapportée à celle de tous les régimes alignés quand
 * elles dépassent ensemble soixante trimestres dans plusieurs. Le régime est
 * celui de `groupes` (`groupesDuMinimum`). Sans durées dites, la part entière.
 * Voir le Python.
 */
function partDuMinimum(parametres, regime, durees, groupes) {
  if (!parametres.minimum_proratise || durees === null) {
    return 1.0;
  }
  const seuil = Number(parametres.minimum_trimestres);
  const dureesDesGroupes = new Map();
  for (const [code, groupe] of groupes) {
    dureesDesGroupes.set(groupe, (dureesDesGroupes.get(groupe) ?? 0) + (durees[code] ?? 0));
  }
  const propre = Number(groupes.has(regime) ? dureesDesGroupes.get(groupes.get(regime))
    : (durees[regime] ?? 0));
  const alignes = [...dureesDesGroupes.values()].filter((d) => d > 0);
  let total = 0;
  for (const duree of alignes) {
    total += duree;
  }
  if (parametres.minimum_tous_regimes && alignes.length > 1 && total > seuil) {
    return propre / total;
  }
  return Math.min(1.0, propre / seuil);
}

/**
 * Les ressources du survivant que retient le plafond de la version, et le
 * facteur qui multiplie ce plafond : `[ressources, facteur]`. Ses revenus
 * d'activité abattus de 30 % quand il a cinquante-cinq ans à la date d'effet ;
 * celles de son nouveau conjoint en plus, sous le plafond du ménage, quand il
 * vit en couple et que la version dit ce facteur. Voir `_ressources_du_plafond`
 * du Python.
 */
function ressourcesDuPlafond(parametres, conjoint, ressources, dateEffet) {
  let retenues = ressources;
  const taux = parametres.abattement_activite;
  if (taux && conjoint.revenus_d_activite
      && chrono.anneesRevolues(conjoint.naissance, dateEffet)
        >= Math.trunc(Number(parametres.abattement_activite_age))) {
    retenues -= Number(taux) * Math.min(retenues, Number(conjoint.revenus_d_activite));
  }
  const facteur = parametres.facteur_menage;
  // Le ménage ne compte que formé à la date d'effet, ou à la révision
  // qu'ouvre la retraite du survivant : voir le Python.
  if (facteur === null || facteur === undefined
      || conjoint.nouvelle_union === null || conjoint.nouvelle_union === undefined
      || (conjoint.nouvelle_union_depuis ?? dateEffet) > dateEffet) {
    return [retenues, 1.0];
  }
  return [retenues + Number(conjoint.ressources_du_nouveau_conjoint ?? 0.0), Number(facteur)];
}

/**
 * La majoration de 11,1 % des réversions des régimes alignés (L. 353-6),
 * écrite dans `lignes`, une fois toutes les réversions chiffrées :
 * `retraitesPersonnelles`, les ressources du survivant hors de ses revenus
 * d'activité. Voir `_majorer_les_petites_retraites` du Python.
 */
function majorerLesPetitesRetraites(moteur, lignes, reduites, conjoint, retraitesPersonnelles,
  annee) {
  const eligibles = [...reduites].filter(([, [montant, parametres]]) => montant > 0
    && parametres.majoration_taux !== null && parametres.majoration_taux !== undefined);
  const plafond = moteur.reversions.plafondMajoration(annee);
  const generation = Math.round((Number(conjoint.naissance.slice(0, 4))
    + (Number(conjoint.naissance.slice(5, 7)) - 1) / 12) * 1000) / 1000;
  const age = moteur.agesAnnulationDecote.age(generation);
  if (eligibles.length === 0 || plafond === null || age === null) {
    return;
  }
  const debut = auTauxPlein(conjoint.naissance, age[0]);
  // Ses réversions, revues par la limite de cumul ou sous le plafond de
  // ressources quand sa retraite les suit.
  let servies = 0;
  for (const ligne of lignes.values()) {
    servies += ligne.montant - ligne.reduction_du_cumul - ligne.reduction_de_la_revision;
  }
  const retraites = retraitesPersonnelles + servies;
  const theoriques = new Map(eligibles.map(([regime, [montant, parametres]]) => [
    regime, Number(parametres.majoration_taux) * montant]));
  const marge = 4 * plafond[0] - retraites;
  let total = 0;
  for (const majoration of theoriques.values()) {
    total += majoration;
  }
  if (marge <= 0 || total <= 0) {
    return;
  }
  const servie = Math.min(total, marge);
  let reversions = 0;
  for (const [, [montant]] of eligibles) {
    reversions += montant;
  }
  for (const [regime, [montant]] of eligibles) {
    const majoration = servie === total ? theoriques.get(regime) : servie * montant / reversions;
    const ligne = lignes.get(regime);
    const effet = [debut, DEBUT_DE_LA_MAJORATION, ligne.date_effet].reduce(
      (a, b) => (a > b ? a : b));
    const comprise = effet <= ligne.date_effet;
    lignes.set(regime, ligne.avec({
      montant: ligne.montant + (comprise ? majoration : 0.0),
      majoration_petites_retraites: majoration,
      majoration_petites_retraites_effet: effet,
      fiabilite: Math.min(ligne.fiabilite, plafond[1], age[1]),
    }));
  }
}

/**
 * Ce que garde au moins la réversion entière de la SNCF, aux euros de
 * `annee`, et sa fiabilité, `[montant, fiabilité]` : la part
 * `part_du_minimum_de_pension` du minimum de pension de l'article 15, IV,
 * quand la pension de l'agent, `base`, a été portée au minimum à sa
 * liquidation — `portee` —, ou lui est supérieure ; `null` sans lui. Voir
 * `_minimum_de_pension` du Python.
 */
function minimumDePension(moteur, parametres, base, annee, portee = false) {
  const part = parametres.part_du_minimum_de_pension;
  const ancre = moteur.reversions.minimumPensionSncf(annee);
  if (part === null || part === undefined || ancre === null) {
    return null;
  }
  const [depuis, montant, fiabilite] = ancre;
  const [coefficient, fiabiliteDuCoefficient] = moteur.revalorisationsPensions.generale(
    `${String(depuis).padStart(4, "0")}-12-31`, `${String(annee).padStart(4, "0")}-12-31`,
    false, montant / 12);
  if (!portee && base < montant * coefficient) {
    return null;
  }
  return [Number(part) * montant * coefficient, Math.min(fiabilite, fiabiliteDuCoefficient)];
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
 * suppose, quand la chronologie n'en dit pas. `durees` donne la durée
 * d'assurance du défunt dans chaque régime, que le minimum du régime général
 * proratise ; sans elle, il est servi entier. `minima` donne, régime par
 * régime, la part de la pension que le minimum contributif y ajoute : le
 * régime général et les régimes alignés reversent la pension sans elle.
 * `maxima` donne, régime par régime, `[ce que le maximum des pensions a retiré
 * de la pension, ce que la surcote y ajoute, le coefficient qui multiplie son
 * maximum]` : le régime général reverse la pension d'avant son maximum, sous
 * le maximum de la réversion. `avantLeDepart` dit que le défunt est mort avant
 * son départ, et que `pensions` sont celles qu'il eût obtenues à son décès.
 * Voir `reversion` du Python.
 */
export function reversion(moteur, pensions, carriere, annee, decesSuppose = null,
  enCapital = new Set(), majorations = null, durees = null, minima = null,
  maxima = null, avantLeDepart = false, majorationsDesPensions = null) {
  const conjoint = carriere.conjoint;
  const deces = decesSuppose === null ? carriere.deces : decesSuppose;
  if (deces === null || conjoint === null) {
    return null;
  }
  const lendemain = moisSuivant(deces);
  // La cessation d'activité que lisent les conditions de mariage : le départ,
  // ou le décès qui le précède.
  const liquidation = carriere.dateLiquidation;
  const declare = `${String(liquidation.annee).padStart(4, "0")}-`
    + `${String(liquidation.mois).padStart(2, "0")}-01`;
  const depart = deces < declare ? deces : declare;
  const enfants = carriere.nombre_enfants;
  const presumees = conjoint.ressources === null;
  const ressources = presumees ? 0.0 : Number(conjoint.ressources);
  // Ses retraites personnelles : ses ressources, moins ce que son activité lui
  // rapporte ; la limite de cumul d'avant 2004, la majoration pour enfant à
  // charge et celle de 11,1 % les lisent.
  const retraitesPersonnelles = ressources
    - Math.min(ressources, Number(conjoint.revenus_d_activite ?? 0.0));
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
    // La part du survivant, partagée avec les précédents conjoints au prorata
    // des mariages, et la ligne arrêtée par son union nouvelle.
    const part = entiereAuConjoint(parametres, carriere, conjoint) ? 1.0
      : partDuSurvivant(carriere, conjoint, deces, admisAilleurs(parametres, deces));
    if (MOITIE_SOUS_CONDITION_DE_MARIAGE.includes(fiche.id)) {
      const servie = mariageSuffit(parametres, conjoint, deces, depart, enfants);
      const montant = servie ? taux * base * part : 0.0;
      lignes.set(regime, jusquAuRemariage(ligne(regime, base, montant,
        servie ? "servie" : "mariage", fiche, version, taux, lendemain, fiabilite)
        .avec({ part }), parametres, conjoint));
      autresBases += lignes.get(regime).montant;
      continue;
    }
    if (MOITIE_MAJORATION_COMPRISE.includes(fiche.id)) {
      // La moitié de la pension, majoration pour enfants comprise aux IEG,
      // majorée comme la pension à la SNCF : voir le Python.
      const servie = fiche.id === "reversion_sncf"
        ? mariageSncf(parametres, conjoint, deces, depart,
          carriere.naissancesDesEnfants.map(([, naissance]) => naissance))
        : mariageIeg(parametres, conjoint, deces, depart, enfants);
      // La réversion entière, portée au minimum de la SNCF, que le survivant
      // partage comme elle ; sa majoration au même taux de son montant.
      let entiere = taux * base;
      let minimum = 0.0;
      let motif = "servie";
      let releve = 1.0;
      let fiabiliteLigne = fiabilite;
      const garanti = servie
        ? minimumDePension(moteur, parametres, base, annee, Boolean((minima ?? {})[regime]))
        : null;
      if (garanti !== null) {
        minimum = garanti[0];
        if (minimum > entiere) {
          releve = minimum / entiere;
          entiere = minimum;
          motif = "minimum";
          fiabiliteLigne = Math.min(fiabilite, garanti[1]);
        }
      }
      const majoration = servie
        ? Number(parametres.majoration_reversible ?? 0.0) * ((majorations ?? {})[regime] ?? 0.0)
          * part * releve
        : 0.0;
      const montant = servie ? entiere * part + majoration : 0.0;
      lignes.set(regime, sansJouissanceAuDeces(jusquAuRemariage(ligne(regime, base, montant,
        servie ? motif : "mariage", fiche, version, taux, lendemain, fiabiliteLigne, majoration)
        .avec({ part, minimum: minimum * part }), parametres, conjoint), parametres, conjoint,
      deces));
      autresBases += lignes.get(regime).montant;
      continue;
    }
    if (fiche.id === "reversion_rafp") {
      lignes.set(regime, jusquAuRemariage(ligne(regime, base, taux * base * part, "servie",
        fiche, version, taux, lendemain, fiabilite).avec({ part }), parametres, conjoint));
      if (parametres.compte_aux_ressources) {
        autresBases += lignes.get(regime).montant;
      }
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
      lignes.set(regime, jusquAuRemariage(ligne(regime, base, servie ? taux * base * part : 0.0,
        servie ? "servie" : "mariage", fiche, version, taux, dateEffet, fiabilite)
        .avec({ part }), parametres, conjoint));
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
      * ((majorations ?? {})[regime] ?? 0.0) * part;
    lignes.set(regime, jusquAuRemariage(ligne(regime, base, taux * base * part + majoration,
      "servie", fiche, version, taux, dateEffet, fiabilite, majoration).avec({ part }),
    parametres, conjoint));
  }

  // Le plafond de ressources est un : les réversions des régimes alignés se
  // l'imputent l'une après l'autre, dans l'ordre de la liquidation.
  const minimumDeLAnnee = table.minimum(annee);
  const lura = luraApplicable(carriere);
  // L'année de la liquidation dont viennent les pensions, qui dit quelle caisse
  // succède aux autres : celle du décès pour l'assuré mort avant son départ.
  const anneeDeLiquidation = avantLeDepart ? Number(deces.slice(0, 4))
    : carriere.anneeLiquidation;
  // Les droits d'avant 1973 que nomment les versions : leur réversion ne porte
  // pas les majorations pour enfants (décret n° 73-937, article 9).
  const dAvant1973 = new Set();
  // La « pension principale » (L. 353-1), que la caisse prend « avant
  // comparaison au minimum et au maximum » : sans la majoration qui la portait
  // au minimum contributif (L. 351-10), avec ce que le maximum des pensions en
  // avait retiré (exposé de la Cnav, « Retraite de l'assuré décédé » ;
  // circulaire n° 105/90, § 22) ; relevée par les majorations forfaitaires de
  // sa pension venues entre l'année des montants et la date d'effet.
  const principaleDe = (regime, base, dateEffet) => {
    let principale = base - Math.min(base, (minima ?? {})[regime] ?? 0.0)
      + ((maxima ?? {})[regime] ?? [0.0, 0.0, 1.0])[0];
    for (const [jour, tauxMajoration] of (majorationsDesPensions ?? {})[regime] ?? []) {
      if (jour <= dateEffet) {
        principale *= 1 + tauxMajoration;
      }
    }
    return principale;
  };
  // La réversion de chaque régime aligné, réduite, avant ses majorations : ce
  // que la majoration de 11,1 % multiplie.
  const reduites = new Map();
  // Leur réversion entière, portée au minimum et ramenée au maximum, avant les
  // ressources et le cumul : la majoration pour enfant se réduit dans la
  // proportion de la réduite à l'entière.
  const entieres = new Map();
  // Leur réversion réduite, revue par la limite de cumul quand la retraite du
  // survivant la suit : celle que la majoration de 11,1 % multiplie.
  const revues = new Map();
  // Les réversions de base du survivant, qui divisent ses retraites et la
  // limite forfaitaire du cumul d'avant 2004.
  let reversionsDeBase = servies.filter(
    ([regime]) => table.ficheDuRegime(regime)?.id === "reversion").length;
  for (const ligneDejaFaite of lignes.values()) {
    if (ligneDejaFaite.montant > 0 && AUTRES_BASES.includes(ligneDejaFaite.fiche)) {
      reversionsDeBase += 1;
    }
  }
  // Les réversions des autres régimes de base que la révision à sa retraite
  // retient, celles des régimes alignés revues l'une après l'autre.
  let basesRevues = autresBases;
  for (const [regime, base, fiabiliteDuRegime] of servies) {
    const fiche = table.ficheDuRegime(regime);
    if (fiche === null || fiche.id !== "reversion") {
      continue;
    }
    const dateEffet = premiereDateDEffet(table, fiche, conjoint, lendemain, deces);
    const version = table.version(fiche, dateEffet, deces);
    const parametres = version.parametres;
    const taux = Number(parametres.taux);
    // Ses retraites personnelles, servies dès la date d'effet, ou seulement
    // quand sa propre retraite, qu'il date après elle, commence.
    const retraites = retraitesAu(conjoint, retraitesPersonnelles, dateEffet);
    const contributif = Math.min(base, (minima ?? {})[regime] ?? 0.0);
    const [ecretement, surcote, coefficient] = (maxima ?? {})[regime] ?? [0.0, 0.0, 1.0];
    const duDefunt = (majorationsDesPensions ?? {})[regime] ?? [];
    const principale = principaleDe(regime, base, dateEffet);
    // Partagée avec les précédents conjoints au prorata des mariages, la
    // réversion l'est avec son minimum et son maximum (circulaire Cnav
    // n° 105/90, § 3).
    const part = partDuSurvivant(carriere, conjoint, deces,
      admisAuRegimeGeneral(parametres, deces, enfants));
    let montant = taux * principale * part;
    let motif = "servie";
    let fiabilite = fiabiliteDuRegime;
    // Le minimum de D. 353-1, avant les ressources : la caisse porte la
    // réversion au minimum, puis la réduit du dépassement du plafond. Les
    // réversions d'un même régime n'en ont qu'un, que la première de leurs
    // lignes qui n'est pas d'avant 1973 sert en complément des autres
    // (D. 634-14 ; décret n° 73-937, article 7-2) : voir le Python.
    const avant1973 = parametres.droits_d_avant_1973 ?? {};
    for (const code of Object.keys(avant1973)) {
      dAvant1973.add(code);
    }
    const groupes = groupesDuMinimum(moteur, parametres, lura, anneeDeLiquidation);
    const membres = servies.filter(([autre]) => groupes.has(regime)
      && groupes.get(autre) === groupes.get(regime)
      && table.ficheDuRegime(autre)?.id === "reversion");
    const tete = membres.find(([autre]) => !(autre in avant1973))?.[0]
      ?? (membres.length > 0 ? membres[0][0] : regime);
    let autres = 0.0;
    let minimum = 0.0;
    if (minimumDeLAnnee !== null && parametres.minimum_trimestres && tete === regime
        && (!(regime in avant1973) || groupes.has(regime))) {
      for (const [autre, baseAutre] of membres) {
        if (autre !== regime) {
          autres += taux * principaleDe(autre, baseAutre, dateEffet) * part;
        }
      }
      minimum = minimumDeLAnnee[0] * partDuMinimum(parametres, regime, durees, groupes) * part;
      if (minimum - autres > montant) {
        montant = minimum - autres;
        motif = "minimum";
        fiabilite = Math.min(fiabilite, minimumDeLAnnee[1]);
      }
    }
    // Le plafond, d'une personne seule ou du ménage, et ce qu'il retient à côté
    // de la réversion : les ressources du survivant, ou du ménage, et les
    // réversions des autres régimes de base — avant juillet 2004, ses
    // ressources personnelles « sans tenir compte des avantages de réversion »
    // (R. 353-1, rédactions de 1985 et de 1990).
    const [personnelles, facteur] = ressourcesDuPlafond(parametres, conjoint,
      ressources - (retraitesPersonnelles - retraites), dateEffet);
    const plafondAnnuel = facteur * Number(parametres.plafond_smic_heures)
      * moteur.macro.smic_horaire.valeur(annee);
    const reversions = parametres.ressources === "ecretement" ? autresBases : 0.0;
    // Avant juillet 2004, ses retraites personnelles « n'étaient pas retenues
    // dans les ressources » : elles se cumulaient dans une limite.
    const sansRetraites = (parametres.cumul ?? null) !== null
      ? personnelles - Math.min(personnelles, retraites) : personnelles;
    const disponible = plafondAnnuel - sansRetraites - reversions;
    const retenues = sansRetraites + reversions;
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
    // Le maximum, ensuite : la réversion réduite est comparée à son taux du
    // maximum des pensions « opposable à l'assuré décédé », celui de sa date
    // d'effet, au plafond de l'année des montants, l'ajournement d'avant 1983
    // le majorant, auquel s'ajoute son taux de la surcote (circulaires Cnav
    // n° 120/82, § 4, et n° 2018-4, § 5).
    let maximum = 0.0;
    const desPensions = maximumDesPensions(moteur, regime, dateEffet, annee);
    if (desPensions !== null) {
      maximum = taux * (desPensions[0] * coefficient + surcote) * part;
      if (montant > maximum) {
        montant = maximum;
        motif = "maximum";
        fiabilite = Math.min(fiabilite, desPensions[1]);
      }
    }
    const calcule = taux * principale * part;
    entieres.set(regime, maximum > 0 ? Math.min(Math.max(calcule, minimum - autres), maximum)
      : Math.max(calcule, minimum - autres));
    // Le cumul d'avant juillet 2004 avec ses retraites personnelles, après le
    // maximum (D. 355-1).
    const forfaitaire = table.limiteCumul(annee);
    const [cumulee, limiteALEffet] = cumuler(parametres, montant, retraites, principale,
      forfaitaire === null ? null : forfaitaire[0], reversionsDeBase);
    let limiteCumul = limiteALEffet;
    if (cumulee < montant) {
      montant = cumulee;
      motif = "cumul";
      if (forfaitaire !== null && parametres.cumul === "limite") {
        fiabilite = Math.min(fiabilite, forfaitaire[1]);
      }
    }
    autresBases += montant;
    // La majoration de 10 % du survivant de trois enfants, sur la réversion
    // réduite et hors du plafond, au moins le dixième du minimum (R. 353-2) ;
    // pas sur les points d'avant 1973 (décret n° 73-937, article 9).
    const desTroisEnfants = (reversion_) => (reversion_ <= 0 || enfants < 3
      || regime in avant1973 ? 0.0
      : Math.max(Number(parametres.majoration_enfants_taux) * reversion_,
        Number(parametres.majoration_enfants_minimum ?? 0.0) * minimum));
    const troisEnfants = desTroisEnfants(montant);
    const ulterieures = montant > 0
      ? majorationsUlterieures(parametres, dateEffet, calcule, minimum, maximum, duDefunt,
        autres)
      : [];
    // La limite revue quand sa propre retraite suit la date d'effet : ce
    // qu'elle retire alors, la majoration de 10 % suivant la réversion.
    let cumulEffet = null;
    let reductionDuCumul = 0.0;
    let revueA = montant;
    const revue = cumulALaRetraite(moteur, fiche, conjoint, deces, annee, dateEffet, montant,
      ulterieures, retraitesPersonnelles, principale, reversionsDeBase, duDefunt);
    if (revue !== null) {
      let servieAlors;
      let fiabiliteRevue;
      [cumulEffet, servieAlors, revueA, limiteCumul, fiabiliteRevue] = revue;
      reductionDuCumul = servieAlors + desTroisEnfants(servieAlors)
        - revueA - desTroisEnfants(revueA);
      fiabilite = Math.min(fiabilite, fiabiliteRevue);
    }
    // Ou revue sous le plafond de ressources, quand sa retraite la suit depuis
    // juillet 2004 : de même.
    let revisionEffet = null;
    let reductionDeLaRevision = 0.0;
    const revisee = revisionALaRetraite(moteur, fiche, parametres, conjoint, deces, annee,
      dateEffet, montant, entieres.get(regime), ulterieures, ressources,
      retraitesPersonnelles, basesRevues);
    if (revisee !== null) {
      let servieAlors;
      let fiabiliteRevisee;
      [revisionEffet, servieAlors, revueA, fiabiliteRevisee] = revisee;
      reductionDeLaRevision = servieAlors + desTroisEnfants(servieAlors)
        - revueA - desTroisEnfants(revueA);
      fiabilite = Math.min(fiabilite, fiabiliteRevisee);
    }
    basesRevues += revueA;
    reduites.set(regime, [montant, parametres]);
    revues.set(regime, [revueA, parametres]);
    lignes.set(regime, ligne(regime, base, montant + troisEnfants, motif, fiche, version,
      taux, dateEffet, fiabilite).avec({
      minimum, majoration_trois_enfants: troisEnfants, minimum_contributif: contributif,
      ecretement_du_maximum: ecretement, maximum, plafond: plafondAnnuel,
      ressources_retenues: retenues, part, limite_cumul: limiteCumul,
      majorations_forfaitaires: ulterieures, cumul_effet: cumulEffet,
      reduction_du_cumul: reductionDuCumul, revision_effet: revisionEffet,
      reduction_de_la_revision: reductionDeLaRevision,
      derniere_revision: derniereRevision(parametres, conjoint, dateEffet, revisee !== null),
    }));
  }

  // La complémentaire des indépendants en dernier : ses ressources sont celles
  // de R. 353-1, « personnelles ou du ménage », que les réversions de tous les
  // régimes de base grossissent (articles 17 et 35 de son règlement). Un
  // dépassement de son plafond, le même pour un ménage, réduit ses réversions à
  // due concurrence, chacune au prorata de son montant.
  const independantes = [];
  for (const [regime, base, fiabilite] of servies) {
    const fiche = table.ficheDuRegime(regime);
    if (fiche === null || fiche.id !== "reversion_rci") {
      continue;
    }
    const version = table.version(fiche, lendemain, deces);
    // Le versement forfaitaire unique de l'assuré « fait obstacle à
    // l'attribution d'une pension de réversion » (article 41, II).
    if (version.parametres.rien_apres_un_capital && enCapital.has(regime)) {
      continue;
    }
    if ((version.parametres.portee ?? true) === false) {
      lignes.set(regime, new ReversionRegime({
        regime, base, montant: 0.0, motif: "non_portee",
      }));
      continue;
    }
    const part = partDuSurvivant(carriere, conjoint, deces,
      admisAilleurs(version.parametres, deces));
    independantes.push([regime, base, fiabilite, fiche, version, part]);
  }
  if (independantes.length > 0) {
    const premiers = independantes[0][4].parametres;
    const [personnelles, facteur] = ressourcesDuPlafond(premiers, conjoint, ressources,
      aLAge(conjoint.naissance, lendemain, Number(premiers.age_minimum)));
    const plafondAnnuel = facteur * Number(premiers.plafond_pass)
      * moteur.macro.plafond_securite_sociale.valeur(annee);
    const retenues = personnelles + autresBases;
    let brut = 0.0;
    for (const [, base, , , version, part] of independantes) {
      brut += Number(version.parametres.taux) * base * part;
    }
    const depassement = Math.max(0.0, retenues + brut - plafondAnnuel);
    for (const [regime, base, fiabilite, fiche, version, part] of independantes) {
      const parametres = version.parametres;
      const taux = Number(parametres.taux);
      let montant = taux * base * part;
      let motif = "servie";
      if (depassement > 0 && brut > 0) {
        montant = Math.max(0.0, montant - depassement * montant / brut);
        motif = "ecretee";
      }
      const dateEffet = aLAge(conjoint.naissance, lendemain, Number(parametres.age_minimum));
      lignes.set(regime, ligne(regime, base, montant, motif, fiche, version, taux,
        dateEffet, fiabilite).avec({ plafond: plafondAnnuel, ressources_retenues: retenues,
        part }));
    }
  }

  // La majoration forfaitaire pour enfant à charge, servie par un seul
  // régime, celui de la dernière affiliation parmi ceux qui servent une
  // réversion (`regimeDeLaMajoration`) ; réduite dans la proportion de la
  // réversion réduite à l'entière (D. 353-2). Jamais celle des points d'avant
  // 1973 (décret n° 73-937, article 9).
  const avecReversion = [...reduites]
    .filter(([regime, [montant]]) => montant > 0 && !dAvant1973.has(regime))
    .map(([regime]) => regime);
  const servant = regimeDeLaMajoration(moteur, carriere, avecReversion,
    Math.min(anneeDeLiquidation, Number(deces.slice(0, 4))), durees, reduites);
  if (servant !== null) {
    const ligneDuRegime = lignes.get(servant);
    const entiere = majorationForfaitaireEnfants(moteur, carriere, conjoint,
      retraitesPersonnelles, ligneDuRegime.date_effet, annee);
    if (entiere !== null) {
      const [parEnfant, fiabiliteEnfant, parts] = entiere;
      const reduite = reduites.get(servant)[0];
      const facteur = entieres.get(servant) > 0
        ? Math.min(1.0, reduite / entieres.get(servant)) : 0.0;
      // Chaque enfant compte pendant que sa part est servie.
      const servieAu = (jour) => parts.filter(([debut, fin]) => debut <= jour && jour < fin)
        .length * parEnfant * facteur;
      const majoration = servieAu(ligneDuRegime.date_effet);
      const jours = [...new Set(parts.flat())]
        .filter((jour) => jour > ligneDuRegime.date_effet).sort();
      const etapes = [];
      for (const jour of jours) {
        const montant = servieAu(jour);
        if (montant !== (etapes.length > 0 ? etapes[etapes.length - 1][1] : majoration)) {
          etapes.push([jour, montant]);
        }
      }
      lignes.set(servant, ligneDuRegime.avec({
        montant: ligneDuRegime.montant + majoration,
        majoration_forfaitaire_enfants: majoration,
        majoration_forfaitaire_enfants_etapes: etapes,
        fiabilite: Math.min(ligneDuRegime.fiabilite, fiabiliteEnfant),
      }));
    }
  }

  // Ses retraites personnelles, que la majoration de 11,1 % compte.
  majorerLesPetitesRetraites(moteur, lignes, revues, conjoint, retraitesPersonnelles,
    annee);

  return new Reversion({
    personne: conjoint.personne, defunt: carriere.personne, deces, annee,
    ressources, ressources_presumees: presumees,
    regimes: servies.filter(([regime]) => lignes.has(regime))
      .map(([regime]) => lignes.get(regime)),
    deces_suppose: decesSuppose !== null, avant_le_depart: avantLeDepart,
  });
}
