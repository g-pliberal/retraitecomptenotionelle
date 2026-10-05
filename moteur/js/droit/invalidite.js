/**
 * L'invalidité et l'inaptitude (docs/architecture.md, § 11) : ce que les
 * étapes du droit lisent des fiches du domaine, que `Invalidites` prépare.
 *
 * Jumeau de `src/retraite_notionnelle/droit/invalidite.py`, fonction pour
 * fonction. L'assuré reconnu inapte au travail — et l'ex-invalide, dont la
 * pension de vieillesse est celle « allouée en cas d'inaptitude au travail »
 * (L. 341-15) — a le taux plein quelle que soit sa durée, dans les régimes de
 * la fiche `inaptitude_au_travail`, à l'âge que la version dit. La pension
 * d'invalidité prend fin à cet âge, et la pension de vieillesse la remplace
 * d'office au premier jour du mois qui suit (fiche
 * `pension_d_invalidite_substituee`) ; l'invalide qui travaille la garde
 * jusqu'à sa demande, au plus tard à l'âge du taux plein automatique, le
 * demandeur d'emploi indemnisé six mois de plus. L'assuré qui a cotisé en
 * situation de handicap la durée de la fiche `retraite_anticipee_handicap` part
 * dès cinquante-cinq ans, au taux plein, sa pension majorée ; le fonctionnaire
 * handicapé n'a pas de coefficient de minoration. Voir le Python.
 */

import { DateMois, enMois } from "../calendrier.js";
import { formatFixe } from "../format.js";
import { dateDEffet, ligneCotisee } from "./commun.js";

/** L'âge d'une version qui le lit à la génération : celui de L. 161-17-2. */
export const AGE_LEGAL_PAR_GENERATION = "age_legal_par_generation";

/**
 * L'âge de l'allocation de solidarité aux personnes âgées de droit commun :
 * celui de `MinimumVieillesse.AGE_OUVERTURE`, recopié pour que ce module
 * n'importe pas les tables du scénario 1.
 */
export const AGE_DE_L_ASPA = 65.0;

/** Le régime dont l'Agirc-Arrco et l'Ircantec suivent le taux plein. */
export const REGIME_DES_SALARIES = "regime_general";

/** Ce que devient la pension d'invalidité de qui travaille à l'âge. */
export const MAINTIEN_JUSQU_A_LA_DEMANDE = "maintien_jusqu_a_la_demande";
export const OPPOSITION = "opposition";

/** Pourquoi la substitution ne se fait pas à l'âge. */
export const ACTIVITE = "activite";
export const CHOMAGE = "chomage";

/** Un âge qu'une version écrit : un nombre, ou l'âge légal de la génération. */
export function ageDeLaFiche(moteur, carriere, valeur) {
  if (valeur === AGE_LEGAL_PAR_GENERATION) {
    const lu = moteur.agesOuverture.age(carriere.generation);
    return lu !== null ? lu[0] : 60.0;
  }
  return Number(valeur);
}

/**
 * L'assuré est-il inapte au sens de L. 351-8, 2° ? Reconnu inapte, ex-invalide,
 * ou, quand la `version` de la fiche `inaptitude_au_travail` le dit, dont
 * l'incapacité permanente atteint son taux à la date d'effet. Voir
 * `reconnu_inapte` du Python.
 */
export function reconnuInapte(carriere, version = null) {
  return carriere.inaptitude || carriere.pensionDInvalidite !== null
    || incapaciteReconnue(carriere, version, "incapacite_permanente");
}

/**
 * L'incapacité permanente que la carrière déclare atteint-elle le taux que
 * `version` exige sous `cle`, et la date d'effet la trouve-t-elle reconnue ?
 * Voir `incapacite_reconnue` du Python.
 */
export function incapaciteReconnue(carriere, version, cle) {
  const incapacite = carriere.incapacitePermanente;
  if (version === null || version === undefined || incapacite === null
      || carriere.age_liquidation === null || carriere.age_liquidation === undefined) {
    return false;
  }
  const exige = version.parametres[cle];
  return exige !== undefined && exige !== null && incapacite.taux >= Number(exige)
    && incapacite.debut.rang <= carriere.dateLiquidation.rang;
}

/**
 * L'âge auquel ce régime ouvre le droit à l'inapte, au taux plein, pour une
 * pension qui prend effet à la date de liquidation de `carriere` ; `null`
 * quand l'assuré n'est pas inapte, que le régime n'applique pas la fiche ou
 * que la carrière n'a pas de départ.
 */
export function ageDInaptitude(moteur, regime, carriere) {
  if (!moteur.invalidites.regimes("inaptitude").has(regime)) {
    return null;
  }
  const date = dateDEffet(carriere);
  const version = date === null ? null : moteur.invalidites.version("inaptitude", date);
  if (version === null || !reconnuInapte(carriere, version)) {
    return null;
  }
  return ageDeLaFiche(moteur, carriere, version.parametres.age);
}

/** Le taux plein que ce régime sert à l'inapte, quelle que soit sa durée. */
export function tauxPleinDeLInapte(moteur, regime, carriere, ageLiquidation) {
  const age = ageDInaptitude(moteur, regime, carriere);
  return age !== null && ageLiquidation + 1e-9 >= age;
}

/**
 * L'âge où l'allocation de solidarité aux personnes âgées s'ouvre à cet
 * assuré : soixante-cinq ans, abaissé pour l'inapte et l'ex-invalide à l'âge
 * de la version (R. 815-1 ; paramètre `age_aspa` de la fiche
 * `inaptitude_au_travail`, à la date de liquidation). Voir `age_de_l_aspa`
 * du Python.
 */
export function ageDeLAspa(moteur, carriere) {
  const date = dateDEffet(carriere);
  const version = date === null ? null : moteur.invalidites.version("inaptitude", date);
  if (!reconnuInapte(carriere, version)) {
    return AGE_DE_L_ASPA;
  }
  const valeur = version === null ? undefined : version.parametres.age_aspa;
  if (valeur === undefined || valeur === null) {
    return AGE_DE_L_ASPA;
  }
  return Math.min(AGE_DE_L_ASPA, ageDeLaFiche(moteur, carriere, valeur));
}

/**
 * La radiation des cadres pour invalidité qui liquide la pension de ce régime :
 * celle de la carrière, quand le régime est l'un des trois du code des
 * pensions que la fiche `retraite_pour_invalidite_fonction_publique` nomme ;
 * `null` sinon.
 */
export function radiationDuRegime(moteur, regime, carriere) {
  const radiation = carriere.radiationPourInvalidite;
  if (radiation === null || !moteur.invalidites.regimes("fonction_publique").has(regime)) {
    return null;
  }
  return radiation;
}

/**
 * La version de la fiche `retraite_pour_invalidite_fonction_publique` qui
 * s'applique à la pension de ce régime liquidée à la date de `carriere`, quand
 * elle l'est pour invalidité ; `null` sinon.
 */
export function retraitePourInvalidite(moteur, regime, carriere) {
  if (radiationDuRegime(moteur, regime, carriere) === null) {
    return null;
  }
  const date = dateDEffet(carriere);
  return date === null ? null : moteur.invalidites.version("fonction_publique", date);
}

/** L'indice majoré qui borne la part du traitement que la rente compte entière. */
export const INDICE_DE_LA_RENTE = 681;

/** La rente viagère d'invalidité de L. 28. Voir le Python. */
export function renteViagereDInvalidite(traitement, taux, seuil) {
  const compte = Math.min(traitement, seuil)
    + Math.max(0.0, Math.min(traitement, 10.0 * seuil) - seuil) / 3.0;
  return taux * compte;
}

/**
 * La pension du fonctionnaire radié pour invalidité, rente comprise, et ce que
 * le détail en dit : `[montant, detail]`. Voir `pension_du_fonctionnaire_invalide`
 * du Python.
 */
export function pensionDuFonctionnaireInvalide(moteur, carriere, version, pension, traitement,
  annee) {
  const parametres = version.parametres;
  const radiation = carriere.radiationPourInvalidite;
  const taux = (radiation.taux ?? 0.0) / 100.0;
  const details = [];
  let servie = pension;
  const plancher = Number(parametres.plancher_part_du_traitement ?? 0.0) * traitement;
  if (taux + 1e-9 >= Number(parametres.plancher_taux_invalidite ?? 1.0) && servie < plancher) {
    servie = plancher;
    details.push(`portée à ${formatFixe(plancher, 2, true)} €, la moitié du traitement (L. 30)`);
  }
  let rente = 0.0;
  if (radiation.imputable && taux > 0) {
    const valeur = moteur.minimumGaranti.valeurDUnIndice(INDICE_DE_LA_RENTE, annee);
    const seuil = valeur !== null ? valeur[0] : traitement;
    rente = renteViagereDInvalidite(traitement, taux, seuil);
  }
  const total = servie + rente;
  if (parametres.plafond_total && traitement > 0 && total > traitement) {
    const reduction = traitement / total;
    servie *= reduction;
    rente *= reduction;
    details.push("réduite au traitement (L. 30 ter)");
  }
  if (rente > 0) {
    details.push(`rente viagère d'invalidité de ${formatFixe(rente, 2, true)} € à `
      + `${formatTaux(radiation.taux)} % (L. 28)`);
  }
  return [servie + rente, details.join(" ; ")];
}

/** Un taux d'invalidité comme Python l'écrit avec `:g` : 70, 62.5. */
function formatTaux(taux) {
  return String(Number(taux));
}

/**
 * La pension de vieillesse qui remplace la pension d'invalidité : `{date,
 * version, maintien}`, le mois où elle commence, la version qui la date, et
 * pourquoi ce n'est pas à l'âge (`activite`, `chomage`), `null` sinon.
 */
export class Substitution {
  constructor(date, version, maintien = null) {
    this.date = date;
    this.version = version;
    this.maintien = maintien;
    Object.freeze(this);
  }
}

/**
 * Le mois où la pension de vieillesse de l'ex-invalide commence, pour la
 * carrière et son départ déclaré ; `null` sans pension d'invalidité, ou quand
 * l'invalidité est née après l'âge de la substitution. Voir `substitution`
 * du Python.
 */
export function substitution(moteur, carriere) {
  const pension = carriere.pensionDInvalidite;
  if (pension === null || carriere.age_liquidation === null
      || carriere.age_liquidation === undefined) {
    return null;
  }
  const preparee = moteur.invalidites.fiches()[moteur.invalidites.constructor.FICHES.substitution];
  if (preparee === undefined) {
    return null;
  }
  let retenue = null;
  let age = null;
  let date = null;
  for (const version of preparee.versions) {
    age = ageDeLaFiche(moteur, carriere, version.parametres.age);
    date = carriere.dateDeLAge(age);
    const [debut, fin] = version.bornes["liquidation.date_effet"];
    const jour = `${String(date.annee).padStart(4, "0")}-${String(date.mois).padStart(2, "0")}-01`;
    if ((debut === null || debut <= jour) && (fin === null || jour < fin)) {
      retenue = version;
      break;
    }
  }
  if (retenue === null || pension.debut.rang >= date.rang) {
    return null;
  }
  const parametres = retenue.parametres;
  const declare = carriere.dateLiquidation;
  const annee = carriere.moisDeLAnniversaire(age).annee;
  const lignes = carriere.lignesDe(annee);
  const principale = lignes.length > 0 ? lignes[0] : null;
  const nature = principale !== null ? principale.type_periode : null;
  const plusTardif = (a, b) => (a.rang >= b.rang ? a : b);
  const plusPrecoce = (a, b) => (a.rang <= b.rang ? a : b);
  if (nature === "emploi" && principale.revenu > 0
      && [MAINTIEN_JUSQU_A_LA_DEMANDE, OPPOSITION].includes(parametres.invalide_qui_travaille)) {
    let plusTard = declare;
    if (parametres.invalide_qui_travaille === MAINTIEN_JUSQU_A_LA_DEMANDE) {
      const automatique = moteur.agesAnnulationDecote.age(carriere.generation);
      plusTard = plusPrecoce(declare, carriere.dateDeLAge(
        automatique !== null ? automatique[0] : 65.0));
    }
    return new Substitution(plusTardif(date, plusTard), retenue.id, ACTIVITE);
  }
  const mois = parametres.maintien_du_demandeur_d_emploi_mois;
  if (nature === "chomage_indemnise" && mois) {
    return new Substitution(
      plusTardif(date, plusPrecoce(declare, date.plusMois(Number(mois)))), retenue.id, CHOMAGE);
  }
  return new Substitution(date, retenue.id);
}

// LE DÉPART ANTICIPÉ DES ASSURÉS HANDICAPÉS (fiche `retraite_anticipee_handicap`)

/** La famille des régimes du code des pensions. */
export const FONCTION_PUBLIQUE = "fonction_publique";

/**
 * La version de la fiche `retraite_anticipee_handicap` pour une pension qui
 * prend effet à la date de liquidation de `carriere`, ou `null`.
 */
export function versionDuHandicap(moteur, carriere) {
  const date = dateDEffet(carriere);
  return date === null ? null : moteur.invalidites.version("handicap", date);
}

/**
 * L'année civile compte-t-elle en situation de handicap ? Toute l'année de la
 * reconnaissance et les suivantes ; celle du départ, si l'incapacité précède
 * l'arrêt du compte. Voir `annee_en_situation_de_handicap` du Python.
 */
export function anneeEnSituationDeHandicap(carriere, annee) {
  const incapacite = carriere.incapacitePermanente;
  if (incapacite === null || carriere.age_liquidation === null
      || carriere.age_liquidation === undefined) {
    return false;
  }
  const depart = carriere.dateLiquidation;
  if (annee < incapacite.debut.annee || annee > depart.annee) {
    return false;
  }
  if (annee < depart.annee) {
    return true;
  }
  const arret = new DateMois(depart.annee, 3 * Math.floor((depart.mois - 1) / 3) + 1);
  return incapacite.debut.rang < arret.rang;
}

/**
 * Les trimestres que la carrière a accomplis en situation de handicap, tous
 * régimes : les seuls cotisés, ou tous ; `etrangers`, ceux des périodes hors
 * de France, année par année. Voir `trimestres_en_situation_de_handicap` du
 * Python.
 */
export function trimestresEnSituationDeHandicap(moteur, carriere, cotises = true,
  etrangers = null) {
  if (carriere.incapacitePermanente === null || carriere.age_liquidation === null
      || carriere.age_liquidation === undefined) {
    return 0;
  }
  const lignes = carriere.lignes.filter((ligne) => anneeEnSituationDeHandicap(carriere, ligne.annee)
    && (!cotises || ligneCotisee(moteur, carriere, ligne)));
  let total = carriere.trimestresCumules(lignes);
  if (etrangers) {
    const entrees = etrangers instanceof Map ? [...etrangers.entries()]
      : Object.entries(etrangers);
    for (const [annee, nombre] of entrees) {
      if (anneeEnSituationDeHandicap(carriere, Number(annee))) {
        total += nombre;
      }
    }
  }
  return total;
}

/**
 * La durée dont la version retranche les trimestres : la durée requise, ou
 * celle d'avant la loi du 14 avril 2023 pour les générations que la version
 * dit, moins ce qu'elle retranche en plus. Voir `_duree_limite` du Python.
 */
function dureeLimite(moteur, carriere, parametres, requis) {
  let limite = requis;
  const jusquA = parametres.duree_d_avant_2023_jusqu_a;
  if (jusquA !== undefined && jusquA !== null && carriere.generation < Number(jusquA)) {
    const avant = moteur.dureesRequisesAvantReforme2023.trimestres(carriere.generation)
      ?? moteur.dureesRequises.trimestres(carriere.generation);
    if (avant !== null && avant !== undefined) {
      limite = avant[0];
    }
  }
  for (const [debut, fin, plus] of parametres.retranches_en_plus ?? []) {
    if ((debut === null || carriere.generation >= Number(debut))
        && (fin === null || carriere.generation < Number(fin))) {
      limite -= Math.trunc(Number(plus));
    }
  }
  return limite;
}

/**
 * Ce que la version exige pour partir à `age` au titre du handicap : `[âge
 * abaissé, durée cotisée, durée validée ou null]`, ou `null`. Voir
 * `exigences_du_handicap` du Python.
 */
export function exigencesDuHandicap(moteur, carriere, requis, age = null) {
  const version = versionDuHandicap(moteur, carriere);
  if (version === null || !version.parametres.ages || version.parametres.ages.length === 0) {
    return null;
  }
  const parametres = version.parametres;
  const depart = age === null ? carriere.age_liquidation : age;
  const ages = parametres.ages.map(Number);
  let rang = null;
  ages.forEach((seuil, i) => {
    if (enMois(depart) >= enMois(seuil)) {
      rang = i;
    }
  });
  if (rang === null) {
    return null;
  }
  const limite = dureeLimite(moteur, carriere, parametres, requis);
  const validees = parametres.validees_retranchees ?? null;
  return [ages[rang], limite - Math.trunc(Number(parametres.cotisees_retranchees[rang])),
    validees === null ? null : limite - Math.trunc(Number(validees[rang]))];
}

/** La demande vise-t-elle un régime de base que la fiche nomme ? */
function regimesDuHandicap(moteur, regimes) {
  const nommes = moteur.invalidites.regimes("handicap");
  return [...regimes].some((code) => nommes.has(code));
}

/**
 * L'âge le plus précoce auquel le départ anticipé des assurés handicapés
 * ouvre CETTE liquidation, ou `null`. `etrangers` : `[cotisés, validés]` hors
 * de France, année par année. Voir `age_du_handicap` du Python.
 */
export function ageDuHandicap(moteur, carriere, requis, regimes, etrangers = null) {
  if (!regimesDuHandicap(moteur, regimes)) {
    return null;
  }
  const version = versionDuHandicap(moteur, carriere);
  if (version === null || !incapaciteReconnue(carriere, version, "taux_incapacite")) {
    return null;
  }
  const parametres = version.parametres;
  const age = carriere.age_liquidation;
  const limite = dureeLimite(moteur, carriere, parametres, requis);
  const cotises = trimestresEnSituationDeHandicap(
    moteur, carriere, true, etrangers === null ? null : etrangers[0]);
  const validees = parametres.validees_retranchees ?? null;
  const valides = validees === null ? null : trimestresEnSituationDeHandicap(
    moteur, carriere, false, etrangers === null ? null : etrangers[1]);
  const ages = parametres.ages.map(Number);
  for (let i = 0; i < ages.length; i += 1) {
    if (enMois(ages[i]) > enMois(age)) {
      break;
    }
    if (cotises < limite - Math.trunc(Number(parametres.cotisees_retranchees[i]))) {
      continue;
    }
    if (validees !== null && valides < limite - Math.trunc(Number(validees[i]))) {
      continue;
    }
    return ages[i];
  }
  return null;
}

/**
 * L'âge le plus précoce que le départ anticipé des assurés handicapés
 * ouvrirait à qui continue de cotiser, ou `null`. Voir
 * `age_propose_du_handicap` du Python.
 */
export function ageProposeDuHandicap(moteur, carriere, requis, regimes, etrangers = null) {
  if (!regimesDuHandicap(moteur, regimes)) {
    return null;
  }
  const version = versionDuHandicap(moteur, carriere);
  const incapacite = carriere.incapacitePermanente;
  const exige = version === null ? null : (version.parametres.taux_incapacite ?? null);
  if (exige === null || incapacite === null || carriere.age_liquidation === null
      || carriere.age_liquidation === undefined || incapacite.taux < Number(exige)) {
    return null;
  }
  const parametres = version.parametres;
  const age = carriere.age_liquidation;
  const depuis = Math.max(age, carriere.ageAu(incapacite.debut));
  const limite = dureeLimite(moteur, carriere, parametres, requis);
  const cotises = trimestresEnSituationDeHandicap(
    moteur, carriere, true, etrangers === null ? null : etrangers[0]);
  const validees = parametres.validees_retranchees ?? null;
  const valides = validees === null ? 0 : trimestresEnSituationDeHandicap(
    moteur, carriere, false, etrangers === null ? null : etrangers[1]);
  const candidats = [];
  parametres.ages.map(Number).forEach((seuil, i) => {
    let atteint = depuis
      + (limite - Math.trunc(Number(parametres.cotisees_retranchees[i])) - cotises) / 4.0;
    if (validees !== null) {
      atteint = Math.max(atteint,
        depuis + (limite - Math.trunc(Number(validees[i])) - valides) / 4.0);
    }
    candidats.push(Math.max(seuil, atteint));
  });
  return candidats.length > 0 ? Math.min(...candidats) : null;
}

/**
 * Le fonctionnaire handicapé, que le coefficient de minoration n'atteint pas
 * (L. 14, I, du code des pensions). Voir `sans_decote_du_fonctionnaire` du
 * Python.
 */
export function sansDecoteDuFonctionnaire(moteur, regime, carriere) {
  if (!moteur.invalidites.regimes("handicap").has(regime)
      || !moteur.catalogue.contient(regime)
      || moteur.catalogue.obtenir(regime).famille !== FONCTION_PUBLIQUE) {
    return false;
  }
  const version = versionDuHandicap(moteur, carriere);
  return version !== null && Boolean(version.parametres.fonctionnaire_sans_decote)
    && incapaciteReconnue(carriere, version, "taux_incapacite");
}

/**
 * Le coefficient de la majoration de pension, arrondi au centième le plus
 * proche. Voir `coefficient_de_majoration` du Python.
 */
export function coefficientDeMajoration(version, enSituation, duree) {
  const majoration = version.parametres.majoration ?? null;
  if (!majoration || duree <= 0 || enSituation <= 0) {
    return 0.0;
  }
  const brut = Number(majoration.fraction) * enSituation / duree;
  const pas = Math.round(1.0 / Number(majoration.arrondi));
  return Math.floor(brut * pas + 0.5 + 1e-9) / pas;
}
