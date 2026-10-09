/**
 * La chronologie datée et le réseau de personnes.
 *
 * Portage de ``src/retraite_notionnelle/chronologie.py``, fonction pour
 * fonction : la même donnée, au format JSON, dans les deux moteurs
 * (docs/architecture.md, § 5 et § 7.1 ; contrat C.1). Ce que la personne
 * déclare devient des faits datés ({@link duParcours}, {@link duReleve},
 * {@link duResume}) ; les présomptions posent ce qu'elle ne dit pas, en leur
 * nom ({@link completer}) ; la carrière du moteur en est la vue
 * (`Carriere.depuisChronologie`).
 *
 * Les dates sont au jour, au format ISO ; une date connue au mois seulement
 * tombe le premier du mois. Une période vaut [début, fin). La naissance de
 * l'assuré fait exception : son jour décide du mois d'où ses âges se comptent,
 * et la présomption `jour_de_naissance` le pose dès la construction quand la
 * saisie ne le dit pas ({@link naissanceDeLAssure}).
 */

import { DateMois, enMois, origineDesAges } from "./calendrier.js";

/** La version du contrat C.1 que la chronologie suit. */
export const SCHEMA_VERSION = 1;

/** La personne dont on calcule les droits, quand l'appelant n'en nomme pas d'autre. */
export const ASSURE = "assure";
/** Le conjoint de l'assuré, que le mariage lui relie (§ 5.1). */
export const CONJOINT = "conjoint";
/**
 * Les formes d'une union (vocabulaire, `formes_d_union`) : celle où le conjoint
 * survivant vit après le décès en est une.
 */
export const FORMES_D_UNION = Object.freeze(["mariage", "pacs", "concubinage"]);

/** Les sortes de faits qui sont des périodes de la carrière. */
export const EMPLOI = "periode_d_activite";
export const INTERRUPTION = "periode_d_interruption";

/** Le niveau d'un fait que la personne déclare, et celui d'un fait présumé. */
const DECLAREE = "haute";
const PRESUMEE = "estimee";

// -- les faits et les liens -----------------------------------------------------

const deux = (n) => String(n).padStart(2, "0");
const quatre = (n) => String(n).padStart(4, "0");

/** Le premier jour du mois, au format ISO. */
function jour(date) {
  return `${quatre(date.annee)}-${deux(date.mois)}-01`;
}

/** La même date, `ans` années plus tard ; un 29 février tombe le 28. */
export function plusAns(date, ans) {
  const annee = Number(date.slice(0, 4)) + ans;
  const mois = Number(date.slice(5, 7));
  let quantieme = Number(date.slice(8, 10));
  const bissextile = annee % 4 === 0 && (annee % 100 !== 0 || annee % 400 === 0);
  if (mois === 2 && quantieme === 29 && !bissextile) {
    quantieme = 28;
  }
  return `${quatre(annee)}-${deux(mois)}-${deux(quantieme)}`;
}

/**
 * Les années révolues de `debut` à `fin` (AAAA-MM-JJ) : les anniversaires de
 * l'un atteints au plus tard à l'autre, zéro si `fin` le précède. Voir
 * `annees_revolues` du Python.
 */
export function anneesRevolues(debut, fin) {
  let ans = Number(fin.slice(0, 4)) - Number(debut.slice(0, 4));
  if (ans > 0 && plusAns(debut, ans) > fin) {
    ans -= 1;
  }
  return Math.max(ans, 0);
}

/**
 * Un fait du contrat C.1 : déclaré, ou posé par la présomption qu'il nomme.
 * `montant` — un montant et sa monnaie — ne s'écrit que s'il est donné : les
 * ressources d'une personne en portent un. `territoire` de même : un fait qui
 * ne le dit pas a lieu en métropole, le défaut du contrat, et seuls ceux d'une
 * carrière hors de France le disent.
 */
export function fait(ident, personne, sorte, debut, fin = null, attributs = null,
  presomption = null, montant = null, territoire = null) {
  const resultat = {
    schema_version: SCHEMA_VERSION,
    id: ident,
    personne,
    sorte,
    debut,
    fin,
    attributs: { ...(attributs ?? {}) },
    origine: presomption ? "presume" : "declare",
    fiabilite: presomption ? PRESUMEE : DECLAREE,
  };
  if (presomption) {
    resultat.presomption = presomption;
  }
  if (montant !== null) {
    resultat.montant = { ...montant };
  }
  if (territoire !== null) {
    resultat.territoire = territoire;
  }
  return resultat;
}

/**
 * Un lien déclaré du contrat C.1. Une filiation commence à la naissance de
 * l'enfant : tant qu'elle n'est pas connue, `debut` reste vide, et
 * {@link completer} le recopie du fait de naissance.
 */
export function lien(ident, de, vers, sorte, roles, debut = null) {
  return {
    schema_version: SCHEMA_VERSION,
    id: ident,
    de,
    vers,
    sorte,
    roles: { ...roles },
    debut,
    fin: null,
    origine: "declare",
  };
}

// -- construire : ce que la personne déclare -----------------------------------

/**
 * La naissance déclarée d'un enfant : `[date, précision]`. On déclare une
 * année (`1995`), un mois (`1995-06`) ou un jour (`1995-06-14`) ; ce qui n'est
 * pas dit tombe au premier du mois, ou au 1er janvier. Voir
 * `naissance_declaree` du Python.
 */
export function naissanceDeclaree(valeur) {
  const texte = String(valeur).trim();
  const morceaux = texte.split("-");
  const longueurs = [4, 2, 2];
  const valide = morceaux.length >= 1 && morceaux.length <= 3
    && morceaux.every((m, i) => /^[0-9]+$/.test(m) && m.length === longueurs[i]);
  if (!valide) {
    throw new Error(`naissance d'un enfant attendue en AAAA, AAAA-MM ou AAAA-MM-JJ, reçu '${valeur}'`);
  }
  const [annee, mois, quantieme] = [...morceaux.map(Number), 1, 1].slice(0, 3);
  const date = new Date(Date.UTC(annee, mois - 1, quantieme));
  if (date.getUTCFullYear() !== annee || date.getUTCMonth() !== mois - 1
      || date.getUTCDate() !== quantieme) {
    throw new Error(`naissance d'un enfant impossible : '${valeur}'`);
  }
  return [`${quatre(annee)}-${deux(mois)}-${deux(quantieme)}`,
    ["annee", "mois", "jour"][morceaux.length - 1]];
}

/** Le quantième d'une date de la chronologie : 15 pour « 1962-03-15 ». */
export function jourDe(date) {
  return Number(date.slice(8, 10));
}

/** Une date AAAA-MM-JJ, contrôlée ; nulle si elle n'existe pas. */
function dateControlee(annee, mois, quantieme) {
  const date = new Date(Date.UTC(annee, mois - 1, quantieme));
  if (date.getUTCFullYear() !== annee || date.getUTCMonth() !== mois - 1
      || date.getUTCDate() !== quantieme) {
    return null;
  }
  return `${quatre(annee)}-${deux(mois)}-${deux(quantieme)}`;
}

/**
 * Le fait de naissance de l'assuré, au jour qu'il déclare, ou à celui que la
 * présomption `jour_de_naissance` pose quand il ne le dit pas. Le jour se pose
 * ici, et non dans {@link completer}, parce que les dates de la carrière se
 * comptent depuis lui. `presomptions` est la table du paquet. Voir
 * `naissance_de_l_assure` du Python.
 */
export function naissanceDeLAssure(anneeNaissance, moisNaissance, sexe,
  jourNaissance = null, presomptions = null) {
  if (jourNaissance === null || jourNaissance === undefined) {
    return fait(`naissance_${ASSURE}`, ASSURE, "naissance",
      dateControlee(anneeNaissance, moisNaissance,
        valeur("jour_de_naissance", presomptions)),
      null, { sexe, precision: "mois" }, "jour_de_naissance");
  }
  const date = dateControlee(anneeNaissance, moisNaissance, jourNaissance);
  if (date === null) {
    throw new Error(`naissance impossible : le ${jourNaissance} du mois `
      + `${moisNaissance} de ${anneeNaissance}`);
  }
  return fait(`naissance_${ASSURE}`, ASSURE, "naissance", date, null,
    { sexe, precision: "jour" });
}

/** Le mois d'où comptent les âges de qui est né à ce fait de naissance. */
export function origineDe(naissance) {
  return origineDesAges(moisDe(naissance.debut), jourDe(naissance.debut));
}

/**
 * Une date déclarée — le décès de l'assuré, la naissance de son conjoint,
 * leur mariage — et sa précision, comme {@link naissanceDeclaree} lit celle
 * d'un enfant : `[date, précision]`. `quoi` nomme la date dans le message
 * d'erreur. Voir `date_declaree` du Python.
 */
export function dateDeclaree(valeur, quoi) {
  const texte = String(valeur).trim();
  const morceaux = texte.split("-");
  const longueurs = [4, 2, 2];
  const valide = morceaux.length >= 1 && morceaux.length <= 3
    && morceaux.every((m, i) => /^[0-9]+$/.test(m) && m.length === longueurs[i]);
  if (!valide) {
    throw new Error(`${quoi} attendu(e) en AAAA, AAAA-MM ou AAAA-MM-JJ, reçu '${valeur}'`);
  }
  const [annee, mois, quantieme] = [...morceaux.map(Number), 1, 1].slice(0, 3);
  const date = new Date(Date.UTC(annee, mois - 1, quantieme));
  if (date.getUTCFullYear() !== annee || date.getUTCMonth() !== mois - 1
      || date.getUTCDate() !== quantieme) {
    throw new Error(`${quoi} impossible : '${valeur}'`);
  }
  return [`${quatre(annee)}-${deux(mois)}-${deux(quantieme)}`,
    ["annee", "mois", "jour"][morceaux.length - 1]];
}

/**
 * Ce que toute saisie déclare de l'assuré : sa naissance, son départ, ses
 * enfants, et, s'il les dit, son conjoint et son décès. Rend les naissances —
 * celle de l'assuré, puis celles des enfants qu'elle déclare, puis celle du
 * conjoint —, les événements de sa vie — le départ (vide sans âge de départ),
 * le décès — et les liens : de filiation, et le mariage.
 * `naissancesEnfants` déclare la naissance des premiers enfants, dans
 * l'ordre ; {@link completer} présume celles des autres, et date leur
 * filiation. Le départ tombe à l'âge déclaré, compté depuis le mois d'où les
 * âges se comptent. `conjoint` déclare le conjoint (§ 5.1) : sa `naissance`
 * et son `sexe`, la date du `mariage` — que {@link completer} présume sinon —,
 * ses `ressources` annuelles, et ce qui en vient de son activité
 * (`revenus_d_activite`), la `nouvelle_union` où il vit après le décès et ce
 * que son nouveau conjoint y apporte (`ressources_du_nouveau_conjoint`), et
 * son `invalidite`, une décision médicale
 * datée, s'il les dit ; `deces` date le décès de l'assuré, qui clôt le
 * mariage ; `demandesDePension` dit, régime par régime,
 * l'âge auquel il demande sa pension ; `etranger`, la carrière hors de France :
 * ses périodes, ses pensions étrangères et l'État de sa résidence après le
 * départ. Voir `_personne` du Python.
 */
function personne(anneeNaissance, moisNaissance, sexe, ageLiquidation, nombreEnfants,
  naissancesEnfants = [], jourNaissance = null, presomptions = null, conjoint = null,
  deces = null, retraiteProgressive = null, emploiRetraite = null,
  demandesDePension = null, invalidite = null, etranger = null) {
  const assure = naissanceDeLAssure(anneeNaissance, moisNaissance, sexe, jourNaissance,
    presomptions);
  const faitsNaissance = [assure];
  if (naissancesEnfants.length > nombreEnfants) {
    throw new Error(`${naissancesEnfants.length} naissances d'enfants déclarées pour `
      + `${nombreEnfants} enfant${nombreEnfants > 1 ? "s" : ""}`);
  }
  const declarees = naissancesEnfants.map(naissanceDeclaree);
  for (const [date] of declarees) {
    if (date <= assure.debut) {
      throw new Error(`un enfant né le ${date}, avant son parent`);
    }
  }
  declarees.forEach(([date, precision], i) => {
    faitsNaissance.push(fait(`naissance_enfant_${i + 1}`, `enfant_${i + 1}`, "naissance",
      date, null, { precision }));
  });
  const depart = ageLiquidation === null || ageLiquidation === undefined ? [] : [
    fait(`depart_${ASSURE}`, ASSURE, "acte_de_la_personne",
      jour(origineDe(assure).plusMois(enMois(ageLiquidation))), null,
      { acte: "depart", motif: "vieillesse", age: ageLiquidation })];
  if (retraiteProgressive !== null && retraiteProgressive !== undefined) {
    const { age, quotite } = retraiteProgressive;
    if (ageLiquidation === null || ageLiquidation === undefined
        || enMois(age) >= enMois(ageLiquidation)) {
      throw new Error("une retraite progressive précède le départ");
    }
    if (!(quotite > 0.0 && quotite < 1.0)) {
      throw new Error(`la quotité d'une retraite progressive : entre 0 et 1, reçu ${quotite}`);
    }
    depart.unshift(fait(`retraite_progressive_${ASSURE}`, ASSURE, "acte_de_la_personne",
      jour(origineDe(assure).plusMois(enMois(age))), null,
      { acte: "retraite_progressive", age, quotite }));
  }
  if (demandesDePension && Object.keys(demandesDePension).length > 0) {
    if (ageLiquidation === null || ageLiquidation === undefined) {
      throw new Error("une pension demandée à une date suppose un départ");
    }
    for (const code of Object.keys(demandesDePension).sort()) {
      const age = demandesDePension[code];
      if (age < 0) {
        throw new Error(`la pension de ${code} demandée avant la naissance`);
      }
      depart.push(fait(`demande_de_pension_${code}_${ASSURE}`, ASSURE, "acte_de_la_personne",
        jour(origineDe(assure).plusMois(enMois(age))), null,
        { acte: "demande_de_pension", regime: code, age }));
    }
  }
  if (emploiRetraite !== null && emploiRetraite !== undefined) {
    const { age, fin } = emploiRetraite;
    if (ageLiquidation === null || ageLiquidation === undefined
        || enMois(age) < enMois(ageLiquidation)) {
      throw new Error("une activité après le départ ne précède pas le départ");
    }
    if (enMois(fin) <= enMois(age)) {
      throw new Error("une activité après le départ finit après avoir commencé");
    }
    if (!["dernier", "autre"].includes(emploiRetraite.employeur)) {
      throw new Error("l'employeur d'une activité après le départ : le dernier ou un "
        + `autre, reçu « ${emploiRetraite.employeur} »`);
    }
    depart.push(fait(`emploi_retraite_${ASSURE}`, ASSURE, EMPLOI,
      jour(origineDe(assure).plusMois(enMois(age))),
      jour(origineDe(assure).plusMois(enMois(fin))), {
        affiliation: emploiRetraite.affiliation,
        niveau_salaire: emploiRetraite.niveau_salaire, profil: "plat",
        part_primes: 0.0, apres_depart: true, employeur: emploiRetraite.employeur,
      }));
  }
  if (invalidite !== null && invalidite !== undefined) {
    depart.push(...invaliditeDeclaree(assure, ageLiquidation, invalidite));
  }
  if (etranger !== null && etranger !== undefined) {
    depart.push(...etrangerDeclare(assure, ageLiquidation, etranger));
  }
  const role = sexe === "F" ? "mere" : "pere";
  const liens = [];
  for (let rang = 1; rang <= nombreEnfants; rang += 1) {
    liens.push(lien(`filiation_enfant_${rang}`, ASSURE, `enfant_${rang}`, "filiation",
      { [ASSURE]: role, [`enfant_${rang}`]: "enfant" },
      rang <= declarees.length ? declarees[rang - 1][0] : null));
  }
  let jourDeces = null;
  if (deces !== null && deces !== undefined) {
    let precision;
    [jourDeces, precision] = dateDeclaree(deces, "le décès de l'assuré");
    if (jourDeces <= assure.debut) {
      throw new Error(`un décès le ${jourDeces}, avant la naissance`);
    }
    depart.push(fait(`deces_${ASSURE}`, ASSURE, "deces", jourDeces, null, { precision }));
  }
  if (conjoint !== null && conjoint !== undefined) {
    const epoux = naissanceDuConjoint(conjoint);
    faitsNaissance.push(epoux);
    const union = lien(`union_${CONJOINT}`, ASSURE, CONJOINT, "union",
      { [ASSURE]: "conjoint", [CONJOINT]: "conjoint" });
    union.forme = "mariage";
    if (conjoint.mariage !== null && conjoint.mariage !== undefined) {
      [union.debut] = dateDeclaree(conjoint.mariage, "le mariage");
      if (union.debut <= (assure.debut > epoux.debut ? assure.debut : epoux.debut)) {
        throw new Error(`un mariage le ${union.debut}, avant la naissance d'un époux`);
      }
    }
    if (jourDeces !== null) {
      if (union.debut !== null && union.debut >= jourDeces) {
        throw new Error(`un mariage le ${union.debut}, après le décès`);
      }
      union.fin = { date: jourDeces, cause: "deces" };
    }
    liens.push(union);
    if (conjoint.ressources !== null && conjoint.ressources !== undefined) {
      faitsNaissance.push(fait(`ressources_${CONJOINT}`, CONJOINT, "ressources",
        jourDeces ?? epoux.debut, null,
        { periode: "annuelle" }, null,
        { annuel: Number(conjoint.ressources), monnaie: "EUR" }));
    }
    if (conjoint.revenus_d_activite !== null && conjoint.revenus_d_activite !== undefined) {
      // La part de ces ressources que lui rapporte son activité, que le plafond
      // de la réversion abat après cinquante-cinq ans (R. 353-1).
      faitsNaissance.push(fait(`revenus_d_activite_${CONJOINT}`, CONJOINT, "ressources",
        jourDeces ?? epoux.debut, null,
        { periode: "annuelle", nature: "revenus_d_activite" }, null,
        { annuel: Number(conjoint.revenus_d_activite), monnaie: "EUR" }));
    }
    if (conjoint.nouvelle_union !== null && conjoint.nouvelle_union !== undefined) {
      // Le ménage où il vit après le décès : la forme de sa nouvelle union, et ce
      // que son nouveau conjoint y apporte, s'il le dit (L. 353-1).
      const forme = conjoint.nouvelle_union;
      if (!FORMES_D_UNION.includes(forme)) {
        throw new Error(`une union « ${forme} » : mariage, pacs ou concubinage`);
      }
      const apport = conjoint.ressources_du_nouveau_conjoint;
      faitsNaissance.push(fait(`menage_${CONJOINT}`, CONJOINT, "ressources",
        jourDeces ?? epoux.debut, null,
        { periode: "annuelle", nature: "menage", forme }, null,
        apport === null || apport === undefined
          ? null : { annuel: Number(apport), monnaie: "EUR" }));
    }
    if (conjoint.invalidite !== null && conjoint.invalidite !== undefined) {
      const [jourInvalidite, precision] = dateDeclaree(conjoint.invalidite,
        "l'invalidité du conjoint");
      if (jourInvalidite <= epoux.debut) {
        throw new Error(`une invalidité du conjoint le ${jourInvalidite}, avant sa naissance`);
      }
      faitsNaissance.push(fait(`invalidite_${CONJOINT}`, CONJOINT, "decision_medicale",
        jourInvalidite, null, { decision: "invalidite", precision }));
    }
  }
  return [faitsNaissance, depart, liens];
}

/**
 * Le taux d'incapacité permanente que la saisie déclare : « au moins 50 % ».
 * Voir `TAUX_D_INCAPACITE_DECLARE` du Python.
 */
export const TAUX_D_INCAPACITE_DECLARE = 50;

/**
 * Les faits de l'invalidité et de l'inaptitude que la saisie déclare : la
 * pension d'invalidité, l'inaptitude et l'incapacité permanente, trois
 * décisions médicales, la radiation pour invalidité d'un fonctionnaire. Voir
 * `_invalidite` du Python.
 */
function invaliditeDeclaree(assure, ageLiquidation, invalidite) {
  if (ageLiquidation === null || ageLiquidation === undefined) {
    throw new Error("l'invalidité ou l'inaptitude déclarée suppose un départ");
  }
  const naissance = moisDe(assure.debut);
  const depart = origineDe(assure).plusMois(enMois(ageLiquidation));
  const faits = [];
  if (invalidite.pension !== null && invalidite.pension !== undefined) {
    const age = invalidite.pension;
    const debut = naissance.plusMois(enMois(age));
    if (debut.rang <= naissance.rang || debut.rang >= depart.rang) {
      throw new Error("une pension d'invalidité commence après la naissance et avant le "
        + "départ");
    }
    faits.push(fait(`pension_d_invalidite_${ASSURE}`, ASSURE, "decision_medicale",
      jour(debut), null, { decision: "pension_d_invalidite", age }));
  }
  if (invalidite.inaptitude) {
    faits.push(fait(`inaptitude_${ASSURE}`, ASSURE, "decision_medicale", jour(depart), null,
      { decision: "inaptitude" }));
  }
  const radiation = invalidite.radiation;
  if (radiation !== null && radiation !== undefined) {
    const { age } = radiation;
    const taux = radiation.taux ?? null;
    const debut = naissance.plusMois(enMois(age));
    if (debut.rang <= naissance.rang || debut.rang > depart.rang) {
      throw new Error("une radiation pour invalidité tombe après la naissance et au plus "
        + "tard au départ");
    }
    if (taux !== null && !(taux > 0 && taux <= 100)) {
      throw new Error(`le taux d'invalidité : entre 0 et 100 %, reçu ${taux}`);
    }
    faits.push(fait(`radiation_pour_invalidite_${ASSURE}`, ASSURE, "radiation", jour(debut),
      null, { motif: "invalidite", age, imputable: Boolean(radiation.imputable), taux }));
  }
  if (invalidite.handicap !== null && invalidite.handicap !== undefined) {
    // L'incapacité permanente d'au moins 50 % : depuis le mois que la saisie
    // dit, qui peut précéder la carrière, jamais le départ.
    const age = invalidite.handicap;
    const debut = naissance.plusMois(enMois(age));
    if (debut.rang <= naissance.rang || debut.rang > depart.rang) {
      throw new Error("une incapacité permanente est reconnue après la naissance et au plus "
        + "tard au départ");
    }
    faits.push(fait(`incapacite_permanente_${ASSURE}`, ASSURE, "decision_medicale",
      jour(debut), null,
      { decision: "incapacite_permanente", age, taux: TAUX_D_INCAPACITE_DECLARE }));
  }
  // Les autres titres au taux plein de L. 351-8 (`droit/categories.js`), que la
  // caisse constate à la demande de la pension, donc au départ.
  if (invalidite.deporte) {
    faits.push(fait(`deporte_ou_interne_${ASSURE}`, ASSURE, "titre", jour(depart), null,
      { titre: "deporte_ou_interne" }));
  }
  const mois = invalidite.mois_de_guerre ?? null;
  if (mois !== null) {
    if (!(Math.trunc(mois) > 0)) {
      throw new Error(`la captivité et les services de guerre : en mois, reçu ${mois}`);
    }
    faits.push(fait(`ancien_combattant_ou_prisonnier_${ASSURE}`, ASSURE, "titre",
      jour(depart), null, { titre: "ancien_combattant_ou_prisonnier", mois: Math.trunc(mois) }));
  }
  if (invalidite.travail_manuel) {
    faits.push(fait(`travail_manuel_${ASSURE}`, ASSURE, "exposition", jour(depart), null,
      { exposition: "travail_manuel", nature: invalidite.travail_manuel }));
  }
  return faits;
}

/** La nature d'une activité exercée hors de France : salariée, ou non. */
export const ACTIVITES_A_L_ETRANGER = Object.freeze(["salariee", "non_salariee"]);

/**
 * Le code d'un État étranger, tel qu'un fait le porte pour territoire ; jamais
 * la France, ni la métropole. Voir `_etat_etranger` du Python.
 */
function etatEtranger(code) {
  if (typeof code !== "string" || !code || code === "FR" || code === "metropole") {
    throw new Error(`un État étranger : son code, reçu « ${code ?? "None"} »`);
  }
  return code;
}

/**
 * Les faits de la carrière hors de France que la saisie déclare : une période à
 * l'étranger par période, son État pour territoire ; un acte de la caisse de
 * l'État par pension étrangère, la liquidation qu'elle notifie, avec son
 * montant ; la résidence, à compter du départ. Voir `_etranger` du Python.
 */
function etrangerDeclare(assure, ageLiquidation, etranger) {
  if (ageLiquidation === null || ageLiquidation === undefined) {
    throw new Error("une carrière hors de France déclarée suppose un départ");
  }
  const naissance = moisDe(assure.debut);
  const depart = origineDe(assure).plusMois(enMois(ageLiquidation));
  const faits = [];
  const bornes = [];
  (etranger.periodes ?? []).forEach((periode, i) => {
    const debut = naissance.plusMois(enMois(periode.debut));
    const fin = naissance.plusMois(enMois(periode.fin));
    if (debut.rang <= naissance.rang || fin.rang <= debut.rang || fin.rang > depart.rang) {
      throw new Error("une période à l'étranger commence après la naissance, finit "
        + "après avoir commencé, et au plus tard au départ");
    }
    if (!ACTIVITES_A_L_ETRANGER.includes(periode.activite)) {
      throw new Error("l'activité d'une période à l'étranger : salariée ou non, reçu "
        + `« ${periode.activite ?? "None"} »`);
    }
    bornes.push([debut.rang, fin.rang]);
    faits.push(fait(`etranger_${i + 1}`, ASSURE, "periode_a_l_etranger", jour(debut),
      jour(fin), { activite: periode.activite }, null, null, etatEtranger(periode.pays)));
  });
  bornes.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  for (let i = 1; i < bornes.length; i += 1) {
    if (bornes[i][0] < bornes[i - 1][1]) {
      throw new Error("deux périodes à l'étranger se chevauchent");
    }
  }
  (etranger.pensions ?? []).forEach((pension, i) => {
    const { age } = pension;
    const debut = naissance.plusMois(enMois(age));
    if (debut.rang <= naissance.rang) {
      throw new Error("une pension étrangère commence après la naissance");
    }
    if (!(pension.mensuel > 0)) {
      throw new Error(`le montant d'une pension étrangère : positif, reçu ${pension.mensuel}`);
    }
    faits.push(fait(`pension_etrangere_${i + 1}`, ASSURE, "acte_de_la_caisse", jour(debut),
      null, { acte: "liquidation", age }, null,
      { mensuel: pension.mensuel, monnaie: "EUR" }, etatEtranger(pension.pays)));
  });
  const mois = etranger.mois_en_france ?? null;
  if (mois !== null && !(mois >= 0 && mois <= 12)) {
    throw new Error(`les mois en France chaque année : de 0 à 12, reçu ${mois}`);
  }
  const ailleurs = etranger.residence !== null && etranger.residence !== undefined;
  if (ailleurs || mois !== null) {
    // Hors de France, son État ; en France, les mois qu'elle y passe.
    faits.push(fait(`residence_${ASSURE}`, ASSURE, "residence", jour(depart), null,
      mois === null ? null : { mois_en_france: mois }, null, null,
      ailleurs ? etatEtranger(etranger.residence) : null));
  }
  return faits;
}

/** Le fait de naissance du conjoint déclaré : sa date et son sexe. */
function naissanceDuConjoint(conjoint) {
  const [date, precision] = dateDeclaree(conjoint.naissance, "la naissance du conjoint");
  if (conjoint.sexe !== "H" && conjoint.sexe !== "F") {
    throw new Error(`le sexe du conjoint : H ou F, reçu '${conjoint.sexe}'`);
  }
  return fait(`naissance_${CONJOINT}`, CONJOINT, "naissance", date, null,
    { sexe: conjoint.sexe, precision });
}

/**
 * La chronologie d'une carrière construite ligne à ligne : la naissance, le
 * départ et les enfants, sans ses périodes, que l'appelant a déjà traduites en
 * années.
 */
export function duResume(anneeNaissance, sexe, moisNaissance = 1, ageLiquidation = null,
  nombreEnfants = 0, naissancesEnfants = [], jourNaissance = null, presomptions = null,
  conjoint = null, deces = null, retraiteProgressive = null, emploiRetraite = null,
  demandesDePension = null, invalidite = null, etranger = null) {
  const [naissance, depart, liens] = personne(anneeNaissance, moisNaissance, sexe,
    ageLiquidation, nombreEnfants, naissancesEnfants, jourNaissance, presomptions,
    conjoint, deces, retraiteProgressive, emploiRetraite, demandesDePension, invalidite,
    etranger);
  return { schema_version: SCHEMA_VERSION, faits: [...naissance, ...depart], liens };
}

/**
 * La chronologie d'un parcours : un fait par métier, daté au mois, et un par
 * année d'interruption. Un début ou une fin d'activité tombe dans le mois où
 * l'âge est atteint, compté du mois de naissance ; le départ, au premier mois
 * où l'âge est révolu, compté du mois que le jour de naissance désigne. Les
 * contrôles sont ceux du parcours : les métiers se suivent, le premier n'est
 * pas cumulé, rien ne dépasse le départ.
 */
export function duParcours({
  annee_naissance,
  sexe,
  metiers,
  age_liquidation,
  mois_naissance = 1,
  profil_carriere = "auto",
  interruptions = null,
  nombre_enfants = 0,
  part_primes = 0.0,
  naissances_enfants = [],
  jour_naissance = null,
  presomptions = null,
  conjoint = null,
  deces = null,
  retraite_progressive = null,
  emploi_retraite = null,
  demandes_de_pension = null,
  invalidite = null,
  etranger = null,
}) {
  if (!metiers || metiers.length === 0) {
    throw new Error("une carrière compte au moins un métier");
  }
  if (metiers[0].cumul) {
    throw new Error(
      "une activité cumulée s'ajoute à une activité principale : la "
      + "carrière ne peut pas commencer par elle",
    );
  }
  const cumuls = metiers.filter((metier) => metier.cumul);
  const principaux = metiers.filter((metier) => !metier.cumul);

  const [naissance, depart, liens] = personne(annee_naissance, mois_naissance, sexe,
    age_liquidation, nombre_enfants, naissances_enfants, jour_naissance, presomptions,
    conjoint, deces, retraite_progressive, emploi_retraite, demandes_de_pension,
    invalidite, etranger);
  const moisDeNaissance = moisDe(naissance[0].debut);
  const bornes = principaux.map(
    (metier) => moisDeNaissance.plusMois(enMois(metier.age_debut)),
  );
  const debut = bornes[0];
  // La pension prend effet ce mois-là : il n'est plus travaillé, la borne est
  // donc EXCLUE.
  const fin = origineDe(naissance[0]).plusMois(enMois(age_liquidation));
  if (fin.rang <= debut.rang) {
    throw new Error("âge de liquidation antérieur à l'âge de début d'activité");
  }
  // Chaque métier s'arrête où commence le suivant : les périodes se touchent
  // bout à bout et couvrent la carrière exactement une fois.
  for (let i = 1; i < bornes.length; i += 1) {
    if (bornes[i].rang <= bornes[i - 1].rang) {
      throw new Error(
        "les métiers doivent se suivre : chacun commence après le précédent",
      );
    }
  }
  if (bornes[bornes.length - 1].rang >= fin.rang) {
    throw new Error("le dernier métier commence après la liquidation");
  }

  const periodes = principaux.map((metier, i) => fait(
    `emploi_${i + 1}`, ASSURE, EMPLOI, jour(bornes[i]),
    jour(i + 1 < bornes.length ? bornes[i + 1] : fin), {
      affiliation: metier.affiliation,
      niveau_salaire: metier.niveau_salaire,
      profil: profil_carriere,
      part_primes,
    },
  ));
  cumuls.forEach((metier, i) => {
    const ouverture = moisDeNaissance.plusMois(enMois(metier.age_debut));
    const cloture = metier.age_fin === null || metier.age_fin === undefined
      ? fin
      : moisDeNaissance.plusMois(enMois(metier.age_fin));
    if (ouverture.rang < debut.rang) {
      throw new Error(
        "une activité cumulée commence après le début de la carrière : elle "
        + "s'ajoute à une activité déjà là",
      );
    }
    if (cloture.rang > fin.rang) {
      throw new Error("une activité cumulée s'arrête au plus tard à la liquidation");
    }
    if (cloture.rang <= ouverture.rang) {
      throw new Error("une activité cumulée doit s'arrêter après avoir commencé");
    }
    periodes.push(fait(`cumul_${i + 1}`, ASSURE, EMPLOI, jour(ouverture), jour(cloture), {
      affiliation: metier.affiliation,
      niveau_salaire: metier.niveau_salaire,
      profil: profil_carriere,
      part_primes,
      cumul: true,
    }));
  });
  const annees = interruptions ? [...interruptions.keys()].sort((a, b) => a - b) : [];
  for (const annee of annees) {
    periodes.push(fait(`interruption_${annee}`, ASSURE, INTERRUPTION,
      `${quatre(annee)}-01-01`, `${quatre(annee + 1)}-01-01`,
      { motif: interruptions.get(annee) }));
  }

  return {
    schema_version: SCHEMA_VERSION,
    faits: [...naissance, ...periodes, ...depart],
    liens,
  };
}

/**
 * La chronologie d'un relevé : un fait par ligne, une année civile chacun,
 * dans l'ordre du relevé — la première ligne d'une année est l'activité
 * principale.
 */
export function duReleve({
  annee_naissance,
  sexe,
  releve,
  age_liquidation,
  mois_naissance = 1,
  nombre_enfants = 0,
  part_primes = 0.0,
  naissances_enfants = [],
  jour_naissance = null,
  presomptions = null,
  conjoint = null,
  deces = null,
  retraite_progressive = null,
  emploi_retraite = null,
  demandes_de_pension = null,
  invalidite = null,
  etranger = null,
}) {
  if (!releve || releve.length === 0) {
    throw new Error("un relevé compte au moins une ligne");
  }
  const periodes = releve.map((ligne, i) => {
    const typePeriode = ligne.type_periode ?? "emploi";
    const attributs = {
      affiliation: ligne.affiliation,
      revenu: ligne.revenu,
      trimestres: ligne.trimestres ?? null,
      part_primes,
    };
    const emploi = typePeriode === "emploi";
    if (!emploi) {
      attributs.motif = typePeriode;
    }
    return fait(`releve_${i + 1}`, ASSURE, emploi ? EMPLOI : INTERRUPTION,
      `${quatre(ligne.annee)}-01-01`, `${quatre(ligne.annee + 1)}-01-01`, attributs);
  });
  const [naissance, depart, liens] = personne(annee_naissance, mois_naissance, sexe,
    age_liquidation, nombre_enfants, naissances_enfants, jour_naissance, presomptions,
    conjoint, deces, retraite_progressive, emploi_retraite, demandes_de_pension,
    invalidite, etranger);
  return {
    schema_version: SCHEMA_VERSION,
    faits: [...naissance, ...periodes, ...depart],
    liens,
  };
}

// -- compléter : les présomptions ------------------------------------------------

/**
 * La valeur d'une présomption (§ 5.6), dans la table que le paquet de données
 * porte (`paquet.presomptions`) : le vocabulaire, fabriqué pour le site.
 */
export function valeur(presomption, presomptions) {
  if (!presomptions || !(presomption in presomptions)) {
    throw new Error(`présomption inconnue : ${presomption}`);
  }
  return presomptions[presomption].valeur;
}

/**
 * La chronologie complétée par les présomptions : une copie, où chaque fait
 * qui manque et qu'une présomption sait poser est posé, en son nom.
 * `presomptions` est la table où lire leurs valeurs, celle du paquet.
 * Deux présomptions posent un fait ou un lien : `naissance_des_enfants` date
 * la naissance de chaque enfant dont la date n'est pas déclarée aux trente ans
 * de son parent, et la filiation commence à cette naissance ;
 * `mariage_des_conjoints` date le mariage que la saisie ne date pas aux
 * vingt-sept ans de l'assuré. `jour_de_naissance` pose le sien à la
 * construction ({@link naissanceDeLAssure}). Compléter deux fois ne change
 * rien.
 */
export function completer(chronologie, presomptions = null) {
  const faits = (chronologie.faits ?? []).map((f) => ({ ...f }));
  const liens = (chronologie.liens ?? []).map((l) => ({ ...l }));
  const naissances = new Map();
  for (const f of faits) {
    if (f.sorte === "naissance" && !naissances.has(f.personne)) {
      naissances.set(f.personne, f);
    }
  }
  for (const filiation of liens) {
    if (filiation.sorte !== "filiation") {
      continue;
    }
    const enfant = filiation.vers;
    if (!naissances.has(enfant)) {
      const parent = naissances.get(filiation.de);
      if (!parent) {
        continue;
      }
      const presume = fait(`naissance_${enfant}`, enfant, "naissance",
        plusAns(parent.debut, valeur("naissance_des_enfants", presomptions)), null, null,
        "naissance_des_enfants");
      faits.push(presume);
      naissances.set(enfant, presume);
    }
    if (filiation.debut === null || filiation.debut === undefined) {
      filiation.debut = naissances.get(enfant).debut;
    }
  }
  for (const union of liens) {
    if (union.sorte !== "union" || (union.debut !== null && union.debut !== undefined)) {
      continue;
    }
    const epoux = naissances.get(union.de);
    if (!epoux) {
      continue;
    }
    union.debut = plusAns(epoux.debut, valeur("mariage_des_conjoints", presomptions));
    union.origine = "presume";
    union.presomption = "mariage_des_conjoints";
  }
  return { schema_version: chronologie.schema_version ?? SCHEMA_VERSION, faits, liens };
}

/** Les présomptions qui ont posé un fait ou un lien de la chronologie. */
export function presomptionsEmployees(chronologie) {
  const noms = new Set();
  for (const element of [...(chronologie.faits ?? []), ...(chronologie.liens ?? [])]) {
    if (element.origine === "presume") {
      noms.add(element.presomption);
    }
  }
  return [...noms].sort();
}

// -- lire ------------------------------------------------------------------------

/** Les faits d'une personne, d'une sorte s'il le faut, dans leur ordre. */
export function faitsDe(chronologie, personne, sorte = null) {
  return (chronologie.faits ?? []).filter(
    (f) => f.personne === personne && (sorte === null || f.sorte === sorte),
  );
}

/**
 * Le conjoint d'une personne : celui que son mariage lui relie, ou `null`. Le
 * modèle n'en connaît qu'un, qui lui survit.
 */
export function conjoint(chronologie, personne) {
  const trouvee = union(chronologie, personne);
  if (trouvee === null) {
    return null;
  }
  return trouvee.de === personne ? trouvee.vers : trouvee.de;
}

/** Le mariage d'une personne, s'il est dit. */
export function union(chronologie, personne) {
  return (chronologie.liens ?? []).find(
    (l) => l.sorte === "union" && (l.de === personne || l.vers === personne),
  ) ?? null;
}

/** Le décès d'une personne, s'il est dit. */
export function deces(chronologie, personne) {
  return faitsDe(chronologie, personne, "deces")[0] ?? null;
}

/**
 * Le fait de ressources d'une personne qui a cette nature : toutes ses
 * ressources sans nature dite, une part d'elles, ou celles de son ménage.
 */
function ressourcesDeNature(chronologie, personne, nature) {
  return faitsDe(chronologie, personne, "ressources").find(
    (f) => (f.attributs.nature ?? null) === nature) ?? null;
}

/** Les ressources annuelles qu'une personne déclare, ou `null`. */
export function ressources(chronologie, personne) {
  const trouve = ressourcesDeNature(chronologie, personne, null);
  return trouve === null ? null : Number(trouve.montant.annuel);
}

/**
 * La part de ses ressources que son activité rapporte à une personne, si elle
 * la déclare, ou `null`.
 */
export function revenusDActivite(chronologie, personne) {
  const trouve = ressourcesDeNature(chronologie, personne, "revenus_d_activite");
  return trouve === null ? null : Number(trouve.montant.annuel);
}

/**
 * Le ménage où une personne dit vivre : `[forme de son union, ressources
 * annuelles que l'autre y apporte, ou null quand il ne les dit pas]` ; `null`
 * pour qui vit seul. Voir `menage` du Python.
 */
export function menage(chronologie, personne) {
  const trouve = ressourcesDeNature(chronologie, personne, "menage");
  if (trouve === null) {
    return null;
  }
  return [trouve.attributs.forme, trouve.montant ? Number(trouve.montant.annuel) : null];
}

/** Le fait de naissance d'une personne, s'il est connu. */
export function naissance(chronologie, personne) {
  return faitsDe(chronologie, personne, "naissance")[0] ?? null;
}

/** L'acte de départ d'une personne, s'il est déclaré. */
export function depart(chronologie, personne) {
  return faitsDe(chronologie, personne, "acte_de_la_personne")
    .find((acte) => acte.attributs.acte === "depart") ?? null;
}

/** La demande de retraite progressive d'une personne, si elle la déclare. */
export function retraiteProgressive(chronologie, personne) {
  return faitsDe(chronologie, personne, "acte_de_la_personne")
    .find((acte) => acte.attributs.acte === "retraite_progressive") ?? null;
}

/**
 * Les pensions dont une personne déclare la date de demande : un acte par
 * régime, dans l'ordre de leurs codes.
 */
/**
 * La décision médicale d'une personne, de cette nature — `pension_d_invalidite`,
 * `inaptitude` ou `incapacite_permanente` de l'assuré, `invalidite` de son
 * conjoint —, si elle est dite.
 */
export function decisionMedicale(chronologie, personne, decision) {
  return faitsDe(chronologie, personne, "decision_medicale")
    .find((f) => f.attributs.decision === decision) ?? null;
}

/**
 * Le titre d'une personne, de ce nom — `deporte_ou_interne`,
 * `ancien_combattant_ou_prisonnier` —, s'il est dit.
 */
export function titre(chronologie, personne, nom) {
  return faitsDe(chronologie, personne, "titre")
    .find((f) => f.attributs.titre === nom) ?? null;
}

/** L'exposition d'une personne, de ce nom — `travail_manuel` —, si elle est dite. */
export function exposition(chronologie, personne, nom) {
  return faitsDe(chronologie, personne, "exposition")
    .find((f) => f.attributs.exposition === nom) ?? null;
}

/** La radiation des cadres pour invalidité d'une personne, si elle est dite. */
export function radiationPourInvalidite(chronologie, personne) {
  return faitsDe(chronologie, personne, "radiation")
    .find((f) => f.attributs.motif === "invalidite") ?? null;
}

/**
 * Les périodes qu'une personne a passées hors de France, dans leur ordre : leur
 * État est leur territoire.
 */
export function periodesALEtranger(chronologie, personne) {
  return faitsDe(chronologie, personne, "periode_a_l_etranger");
}

/**
 * Les pensions étrangères d'une personne, dans leur ordre : les liquidations que
 * la caisse d'un autre État lui notifie, celui-ci pour territoire.
 */
export function pensionsEtrangeres(chronologie, personne) {
  return faitsDe(chronologie, personne, "acte_de_la_caisse").filter(
    (acte) => acte.attributs.acte === "liquidation"
      && (acte.territoire ?? "metropole") !== "metropole");
}

/**
 * La résidence qu'une personne déclare après son départ, si elle la dit : hors
 * de France, son État pour territoire ; en France, la métropole, et les
 * `mois_en_france` qu'elle y passe chaque année.
 */
export function residence(chronologie, personne) {
  const faits = faitsDe(chronologie, personne, "residence");
  return faits.length > 0 ? faits[0] : null;
}

export function demandesDePension(chronologie, personne) {
  return faitsDe(chronologie, personne, "acte_de_la_personne")
    .filter((acte) => acte.attributs.acte === "demande_de_pension");
}

/**
 * Les périodes d'emploi et d'interruption d'une personne, dans leur ordre,
 * jusqu'à son départ : l'activité d'après le départ n'en est pas.
 */
export function periodes(chronologie, personne) {
  return faitsDe(chronologie, personne)
    .filter((f) => (f.sorte === EMPLOI || f.sorte === INTERRUPTION)
      && !f.attributs.apres_depart);
}

/**
 * L'activité qu'une personne exerce après son départ, si elle la déclare : le
 * cumul emploi-retraite.
 */
export function emploiRetraite(chronologie, personne) {
  return faitsDe(chronologie, personne, EMPLOI)
    .find((f) => f.attributs.apres_depart) ?? null;
}

/** Les enfants d'une personne, dans l'ordre de leurs filiations. */
export function enfants(chronologie, personne) {
  return (chronologie.liens ?? [])
    .filter((l) => l.sorte === "filiation" && l.de === personne)
    .map((l) => l.vers);
}

/** L'année d'une date de la chronologie. */
export function anneeDe(date) {
  return Number(date.slice(0, 4));
}

/** Le mois d'une date de la chronologie, pour le moteur qui compte au mois. */
export function moisDe(date) {
  return new DateMois(Number(date.slice(0, 4)), Number(date.slice(5, 7)));
}
