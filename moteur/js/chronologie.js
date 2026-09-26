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
 * tombe le premier du mois. Une période vaut [début, fin).
 */

import { DateMois, enMois } from "./calendrier.js";

/** La version du contrat C.1 que la chronologie suit. */
export const SCHEMA_VERSION = 1;

/** La personne dont on calcule les droits, quand l'appelant n'en nomme pas d'autre. */
export const ASSURE = "assure";

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
function plusAns(date, ans) {
  const annee = Number(date.slice(0, 4)) + ans;
  const mois = Number(date.slice(5, 7));
  let quantieme = Number(date.slice(8, 10));
  const bissextile = annee % 4 === 0 && (annee % 100 !== 0 || annee % 400 === 0);
  if (mois === 2 && quantieme === 29 && !bissextile) {
    quantieme = 28;
  }
  return `${quatre(annee)}-${deux(mois)}-${deux(quantieme)}`;
}

/** Un fait du contrat C.1 : déclaré, ou posé par la présomption qu'il nomme. */
export function fait(ident, personne, sorte, debut, fin = null, attributs = null,
  presomption = null) {
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
 * Ce que toute saisie déclare de l'assuré : sa naissance, son départ et ses
 * enfants. Rend la naissance, le départ (vide sans âge de départ) et les liens
 * de filiation, que {@link completer} datera.
 */
function personne(anneeNaissance, moisNaissance, sexe, ageLiquidation, nombreEnfants) {
  const naissance = new DateMois(anneeNaissance, moisNaissance);
  const faitsNaissance = [fait(`naissance_${ASSURE}`, ASSURE, "naissance", jour(naissance),
    null, { sexe, precision: "mois" })];
  const depart = ageLiquidation === null || ageLiquidation === undefined ? [] : [
    fait(`depart_${ASSURE}`, ASSURE, "acte_de_la_personne",
      jour(naissance.plusMois(enMois(ageLiquidation))), null,
      { acte: "depart", motif: "vieillesse", age: ageLiquidation })];
  const role = sexe === "F" ? "mere" : "pere";
  const liens = [];
  for (let rang = 1; rang <= nombreEnfants; rang += 1) {
    liens.push(lien(`filiation_enfant_${rang}`, ASSURE, `enfant_${rang}`, "filiation",
      { [ASSURE]: role, [`enfant_${rang}`]: "enfant" }));
  }
  return [faitsNaissance, depart, liens];
}

/**
 * La chronologie d'une carrière construite ligne à ligne : la naissance, le
 * départ et les enfants, sans ses périodes, que l'appelant a déjà traduites en
 * années.
 */
export function duResume(anneeNaissance, sexe, moisNaissance = 1, ageLiquidation = null,
  nombreEnfants = 0) {
  const [naissance, depart, liens] = personne(anneeNaissance, moisNaissance, sexe,
    ageLiquidation, nombreEnfants);
  return { schema_version: SCHEMA_VERSION, faits: [...naissance, ...depart], liens };
}

/**
 * La chronologie d'un parcours : un fait par métier, daté au mois, et un par
 * année d'interruption. Les contrôles sont ceux du parcours : les métiers se
 * suivent, le premier n'est pas cumulé, rien ne dépasse le départ.
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

  const dateNaissance = new DateMois(annee_naissance, mois_naissance);
  const bornes = principaux.map(
    (metier) => dateNaissance.plusMois(enMois(metier.age_debut)),
  );
  const debut = bornes[0];
  // La pension prend effet ce mois-là : il n'est plus travaillé, la borne est
  // donc EXCLUE.
  const fin = dateNaissance.plusMois(enMois(age_liquidation));
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
    const ouverture = dateNaissance.plusMois(enMois(metier.age_debut));
    const cloture = metier.age_fin === null || metier.age_fin === undefined
      ? fin
      : dateNaissance.plusMois(enMois(metier.age_fin));
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

  const [naissance, depart, liens] = personne(annee_naissance, mois_naissance, sexe,
    age_liquidation, nombre_enfants);
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
    age_liquidation, nombre_enfants);
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
 * Aujourd'hui, `naissance_des_enfants` date la naissance de chaque enfant dont
 * la date n'est pas déclarée aux trente ans de son parent ; la filiation
 * commence à cette naissance. Compléter deux fois ne change rien.
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

/** Le fait de naissance d'une personne, s'il est connu. */
export function naissance(chronologie, personne) {
  return faitsDe(chronologie, personne, "naissance")[0] ?? null;
}

/** L'acte de départ d'une personne, s'il est déclaré. */
export function depart(chronologie, personne) {
  return faitsDe(chronologie, personne, "acte_de_la_personne")
    .find((acte) => acte.attributs.acte === "depart") ?? null;
}

/** Les périodes d'emploi et d'interruption d'une personne, dans leur ordre. */
export function periodes(chronologie, personne) {
  return faitsDe(chronologie, personne)
    .filter((f) => f.sorte === EMPLOI || f.sorte === INTERRUPTION);
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
