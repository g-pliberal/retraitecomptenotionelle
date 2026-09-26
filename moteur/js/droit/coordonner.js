/**
 * Coordonner les affiliations (docs/architecture.md, § 7.2).
 *
 * Jumeau de `src/retraite_notionnelle/droit/coordonner.py`, fonction pour
 * fonction : le rétablissement de l'agent parti de la fonction publique sans
 * droit à pension (`retablir`), le routage de chaque ligne vers les régimes
 * qui la reçoivent (`regimesDe`), et les groupes de régimes que le droit fait
 * liquider ensemble (`groupesDeSuccession`), que le relevé écrit une fois les
 * droits acquis. Ce que l'étape écrit, `Coordination`, suit son schéma,
 * `data/reference/etapes/coordonner_les_affiliations.yaml`.
 */

import { AnneeCarriere } from "../carriere.js";
import { nomFiabilite, Fiabilite } from "../serie.js";
import { derniereAnnee } from "./commun.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

/**
 * Les régimes que L. 13 du code des pensions et le XXIV visent : l'État, et
 * par renvoi la CNRACL et le FSPOEIE. Ce sont aussi les trois que L. 5 et
 * L. 11 interpénètrent (`regimesInterpenetres`).
 */
export const REGIMES_CODE_DES_PENSIONS = new Set(["fonction_publique_etat", "cnracl", "fspoeie"]);

/**
 * Les trois régimes que la liquidation unique des régimes alignés réunit — le
 * régime général, les salariés agricoles et la sécurité sociale des
 * indépendants sous ses trois noms. Les exploitants agricoles n'en sont pas :
 * la LURA ne vise que les SALARIÉS agricoles.
 */
export const REGIMES_ALIGNES = new Set([
  "regime_general", "msa_salaries", "cancava", "organic", "rsi",
]);
/** La clé sous laquelle ils se réunissent : ce n'est pas un régime. */
export const REGIMES_ALIGNES_TETE = "regimes_alignes";
/**
 * LES TROIS RÉGIMES DU CODE DES PENSIONS SONT INTERPÉNÉTRÉS : chacun compte et
 * liquide les services des deux autres (L. 5 et L. 11 du code des pensions,
 * articles 8 et 13 du décret n° 2003-1306, articles 4 et 10 du décret
 * n° 2004-1056), et le régime de la dernière affiliation sert une PENSION
 * UNIQUE. La clé sous laquelle ils se réunissent. Voir le Python.
 */
export const REGIMES_INTERPENETRES_TETE = "regimes_interpenetres";

/**
 * LE RÉTABLISSEMENT : l'agent qui part sans droit à pension est « rétabli [...]
 * dans la situation qu'il aurait eue s'il avait été affilié au régime général
 * [...] et à l'Ircantec » (L. 65 du code des pensions). Les régimes que
 * D. 173-15 du code de la sécurité sociale y soumet et que le catalogue porte.
 * Voir `retablir` dans le Python.
 */
export const REGIMES_RETABLIS = new Set([
  "fonction_publique_etat", "pensions_civiles_1853", "cnracl", "fspoeie", "seita",
]);
/**
 * Pour qui a quitté son régime après le 28 janvier 1950 (décret n° 50-133) ;
 * l'agent parti plus tôt garde la pension au prorata que le modèle sert.
 */
export const RETABLISSEMENT_DEPUIS = "1950-01-29";
/**
 * Où vont les années rétablies : là où le contractuel du public est routé, et
 * avant 1945, aux assurances sociales du salarié.
 */
export const STATUTS_DU_RETABLISSEMENT = ["contractuel_public", "salarie_prive_non_cadre"];
/** Assurés nés à compter de 1953 (article 51 de la LFSS pour 2016). */
export const LURA_PREMIERE_GENERATION = 1953;
/** Pensions prenant effet au 1er juillet 2017 (décret n° 2017-737, art. 4). */
export const LURA_DATE_EFFET = 2017 * 12 + 6;
/** Dernière année à compter dans les services, null si sans objet. */
export function borneCarriere(carriere) {
  return carriere.age_liquidation === null || carriere.age_liquidation === undefined
    ? null
    : carriere.anneeLiquidation;
}


/**
 * Les régimes que ces statuts atteignent, une année au moins.
 *
 * C'est la seconde garde du droit dérogatoire, et elle n'est pas de confort.
 * Plusieurs régimes SPÉCIAUX servent eux aussi une catégorie active — leur
 * fiche le déclare, et c'est exact : la SNCF a ses agents de conduite. Mais
 * la catégorie active de la fonction publique n'a rien à y voir : sans cette
 * garde, un assuré ayant fait vingt ans d'emploi classé après une carrière à
 * la SNCF aurait vu son régime SNCF liquidé à l'âge de la fonction publique.
 */
export function regimesRoutes(moteur, statuts) {
  const codes = new Set();
  for (const statut of statuts) {
    for (const periode of moteur.affiliations.periodes(statut)) {
      for (const code of periode.regimes ?? []) {
        codes.add(code);
      }
    }
  }
  return codes;
}

/**
 * Les régimes du code des pensions que cette carrière réunit en une pension
 * unique : les trois, sauf l'État quand l'assuré n'y a servi que sous
 * l'uniforme — le militaire garde sa pension militaire, et n'y renonce que
 * par un choix exprès (L. 77). Voir `regimes_interpenetres` du Python.
 *
 * @returns {Set<string>}
 */
export function regimesInterpenetres(moteur, carriere) {
  const militaires = moteur.affiliations.categoriesMilitaires;
  const civil = carriere.lignes.some((ligne) => {
    if (!ligne.cotise || Object.prototype.hasOwnProperty.call(militaires, ligne.affiliation)) {
      return false;
    }
    const routes = regimesRoutes(moteur, [ligne.affiliation]);
    return routes.has("fonction_publique_etat") || routes.has("pensions_civiles_1853");
  });
  const regimes = new Set(REGIMES_CODE_DES_PENSIONS);
  if (!civil) {
    regimes.delete("fonction_publique_etat");
  }
  return regimes;
}

/**
 * Ce régime peut-il pensionner cet agent ? `null` s'il n'y a pas servi. La
 * durée exigée se compte sur les années que le régime a effectivement
 * reçues — celles des trois régimes interpénétrés ensemble —, et se lit à la
 * radiation ; une carrière d'État seulement militaire se lit à la règle des
 * militaires (L. 6), et à son premier engagement : les deux ans de R. 4-1
 * ne valent que pour le militaire engagé depuis le 1er janvier 2014
 * (article 42, II, de la loi n° 2014-40). Voir `droit_a_pension` dans le
 * Python.
 */
export function droitAPension(moteur, code, carriere, anneeLiquidation) {
  // Les pensions civiles d'avant 1948 sont celles de l'État.
  const regime = code === "pensions_civiles_1853" ? "fonction_publique_etat" : code;
  const interpenetres = regimesInterpenetres(moteur, carriere);
  let regimes;
  let cle;
  if (interpenetres.has(regime)) {
    regimes = new Set(interpenetres);
    cle = regime;
  } else if (regime === "fonction_publique_etat") {
    regimes = new Set([regime]);
    cle = "militaires";
  } else {
    regimes = new Set([regime]);
    cle = regime;
  }
  if (regimes.has("fonction_publique_etat")) {
    regimes.add("pensions_civiles_1853");
  }
  const borne = borneCarriere(carriere);
  const parAnnee = new Map();
  for (const ligne of carriere.lignes) {
    if (!ligne.cotise || (borne !== null && ligne.annee > borne)) {
      continue;
    }
    if (!moteur.affiliations.regimes(
      ligne.affiliation, ligne.annee, carriere.dateEntree(ligne.affiliation),
    ).some((c) => regimes.has(c))) {
      continue;
    }
    const retenue = parAnnee.get(ligne.annee);
    if (retenue === undefined || ligne.fraction_annee > retenue.fraction_annee) {
      parAnnee.set(ligne.annee, ligne);
    }
  }
  if (parAnnee.size === 0) {
    return null;
  }
  const lignes = [...parAnnee.keys()].sort((a, b) => a - b).map((a) => parAnnee.get(a));
  const mois = carriere.age_liquidation !== null && carriere.age_liquidation !== undefined
    ? carriere.dateLiquidation.mois : 1;
  const depart = `${String(anneeLiquidation).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`;
  let radiation = `${String(lignes[lignes.length - 1].annee + 1).padStart(4, "0")}-01-01`;
  const enFonctions = radiation >= depart;
  if (enFonctions) {
    radiation = depart;
  }
  const lueLe = cle === "militaires"
    ? `${String(lignes[0].annee).padStart(4, "0")}-01-01` : radiation;
  const regle = moteur.servicesOuvrantPension.annees(cle, lueLe, enFonctions);
  const [exigees, fiabilite] = regle ?? [0, Fiabilite.ESTIMEE];
  const servies = lignes.reduce((total, ligne) => total + ligne.fraction_annee, 0);
  return {
    regimes,
    cleRegimes: [...regimes].sort().join(","),
    lignes,
    servies,
    exigees,
    fiabilite,
    radiation,
    pension: servies + 1e-9 >= exigees,
    recrutement: lignes[0].annee,
    derniere: lignes[lignes.length - 1].annee,
  };
}

/**
 * La carrière que le scénario 1 liquide, RÉTABLISSEMENT fait : les années
 * d'un fonctionnaire parti sans droit à pension passent au régime général et
 * à l'Ircantec. Le régime général y porte le dernier traitement, dans la
 * limite du plafond de chaque année (D. 173-16) ; l'Ircantec le traitement de
 * chaque année ; les primes restent au RAFP. Voir `retablir` dans le Python.
 */
export function retablir(moteur, carriere) {
  return retablirEnDetail(moteur, carriere).carriere;
}

/**
 * `retablir`, et les rétablissements faits : pour chacun, le droit que
 * l'agent n'a pas, et le dernier traitement que le régime général porte au
 * compte de ses années. Voir `_retablir` dans le Python.
 */
function retablirEnDetail(moteur, carriere) {
  if (carriere.age_liquidation === null || carriere.age_liquidation === undefined) {
    return { carriere, retablissements: [] };
  }
  const anneeLiquidation = carriere.anneeLiquidation;
  const vus = new Set();
  const retablies = new Map();
  const faits = [];
  for (const code of [...REGIMES_RETABLIS].sort()) {
    const droit = droitAPension(moteur, code, carriere, anneeLiquidation);
    if (droit === null || vus.has(droit.cleRegimes)) {
      continue;
    }
    vus.add(droit.cleRegimes);
    if (droit.pension || droit.radiation < RETABLISSEMENT_DEPUIS) {
      continue;
    }
    const derniere = droit.lignes[droit.lignes.length - 1];
    const traitement = derniere.revenuAnnualise * (1.0 - derniere.part_primes);
    faits.push([droit, traitement]);
    for (const ligne of carriere.lignes) {
      if (ligne.cotise && ligne.annee <= anneeLiquidation && moteur.affiliations.regimes(
        ligne.affiliation, ligne.annee, carriere.dateEntree(ligne.affiliation),
      ).some((c) => droit.regimes.has(c))) {
        retablies.set(ligne, traitement * ligne.fraction_annee);
      }
    }
  }
  if (retablies.size === 0) {
    return { carriere, retablissements: [] };
  }
  return {
    carriere: carriere.avecLignes(carriere.lignes.map((ligne) => (
      retablies.has(ligne)
        ? new AnneeCarriere({ ...ligne, revenu_retabli: retablies.get(ligne) })
        : ligne
    ))),
    retablissements: faits,
  };
}

/**
 * Les régimes auxquels cette ligne cotise cette année-là : ceux de son
 * statut, sauf pour une année RÉTABLIE, qui quitte son régime spécial pour le
 * régime général et l'Ircantec et garde le RAFP. Voir `regimes_de` dans le Python.
 */
export function regimesDe(moteur, ligne, annee, anneeEntree = null, revenu = null, plafond = null) {
  const regimes = moteur.affiliations.regimes(
    ligne.affiliation, annee, anneeEntree, revenu, plafond,
  );
  if (!(ligne.revenu_retabli > 0)) {
    return regimes;
  }
  let cibles = [];
  for (const statut of STATUTS_DU_RETABLISSEMENT) {
    cibles = [...moteur.affiliations.regimes(statut, annee)];
    if (cibles.length > 0) {
      break;
    }
  }
  return [...cibles, ...regimes.filter((code) => !REGIMES_RETABLIS.has(code))];
}

/**
 * Ce que l'étape écrit : la carrière, rétablissement fait, et les régimes qui
 * reçoivent chacune de ses lignes. Son schéma :
 * `data/reference/etapes/coordonner_les_affiliations.yaml`.
 */
export class Coordination {
  constructor(carriere, regimes, retablissements = []) {
    /** La vue de la chronologie que les étapes suivantes lisent. */
    this.carriere = carriere;
    /** Pour chaque ligne de `carriere`, dans son ordre, ses régimes. */
    this.regimes = regimes;
    /** Les rétablissements faits : [droit, traitement]. */
    this.retablissements = retablissements;
  }

  /** La coordination, telle que son schéma la décrit. */
  donnees() {
    return {
      schema_version: SCHEMA_VERSION,
      personne: this.carriere.personne,
      retablissements: this.retablissements.map(([droit, traitement]) => ({
        regimes: [...droit.regimes].sort(), radiation: droit.radiation, traitement,
      })),
      lignes: this.carriere.lignes.map((ligne, i) => ({
        annee: ligne.annee, affiliation: ligne.affiliation,
        regimes: [...this.regimes[i]], revenu_retabli: ligne.revenu_retabli,
      })),
    };
  }
}

/**
 * L'étape : rétablir, puis router chaque ligne vers ses régimes, pour le
 * revenu de l'année — le salaire de référence d'une année indemnisée. Voir
 * `coordonner` dans le Python.
 */
export function coordonner(moteur, carriereSaisie) {
  const { carriere, retablissements } = retablirEnDetail(moteur, carriereSaisie);
  const regimes = carriere.lignes.map((ligne) => regimesDe(
    moteur, ligne, ligne.annee, carriere.dateEntree(ligne.affiliation),
    ligne.cotise ? ligne.revenu : ligne.revenu_reference,
    moteur.macro.plafond_securite_sociale.valeur(ligne.annee),
  ));
  return new Coordination(carriere, regimes, retablissements);
}

/**
 * La liquidation unique vaut-elle pour cette carrière ? La génération, et la
 * date d'effet au mois près. Voir `lura_applicable` dans le Python.
 */
export function luraApplicable(carriere) {
  return carriere.generation >= LURA_PREMIERE_GENERATION
    && carriere.dateLiquidation.rang >= LURA_DATE_EFFET;
}

/**
 * Le régime au bout de la chaîne d'absorption de `code`, tant que la chaîne
 * reste en annuités : `cancava` et `rsi` rendent `regime_general`,
 * `pensions_civiles_1853` rend `fonction_publique_etat`. Un régime en points
 * au bout de la chaîne l'arrête, et un régime en points n'y entre jamais :
 * ses points se convertissent et s'additionnent déjà (voir `valeurDuPoint`).
 *
 * L'absorption ne se suit qu'à partir de l'année où le régime FERME à ses
 * affiliés — celle où l'absorbant commence à recevoir leurs années. Avant,
 * ce sont deux régimes distincts, et un polypensionné en a deux.
 */
export function teteDeSuccession(moteur, code, anneeLiquidation) {
  const vu = new Set([code]);
  let courant = code;
  for (;;) {
    const regime = moteur.catalogue.obtenir(courant);
    const suivant = regime.integre_dans;
    const borne = regime.fermeture !== null && regime.fermeture !== undefined
      ? regime.fermeture
      : regime.extinction;
    if (suivant === null || suivant === undefined
        || borne === null || borne === undefined || anneeLiquidation < borne
        || !moteur.catalogue.contient(suivant) || vu.has(suivant)) {
      return courant;
    }
    const absorbant = moteur.catalogue.obtenir(suivant);
    const periode = absorbant.periode(
      Math.min(anneeLiquidation, derniereAnnee(absorbant)),
    );
    if (periode === null || periode.type_calcul !== "annuites") {
      return courant;
    }
    vu.add(suivant);
    courant = suivant;
  }
}

/** Les membres dans l'ordre de la chaîne, du plus ancien à l'absorbant. */
export function chaineDepuis(moteur, membres) {
  const restants = new Set(membres);
  let ordre = [];
  for (const depart of [...membres].sort()) {
    let courant = depart;
    const chaine = [];
    while (restants.has(courant) && !ordre.includes(courant)) {
      chaine.push(courant);
      courant = moteur.catalogue.obtenir(courant).integre_dans;
    }
    if (chaine.length > ordre.length) {
      ordre = chaine;
    }
  }
  return [...ordre, ...[...restants].filter((c) => !ordre.includes(c)).sort()];
}

/**
 * Les régimes d'annuités que la carrière a traversés, groupés par chaîne de
 * succession : pour chaque code d'un groupe d'au moins deux, les membres du
 * groupe, LE PREMIER ÉTANT CELUI QUI LIQUIDE.
 *
 * Un régime et celui qui lui succède ne sont pas deux régimes. La CANCAVA,
 * le RSI et le régime général sont trois NOMS du même droit pour un
 * artisan : sa caisse calcule un seul salaire annuel moyen sur toute la
 * carrière et un seul coefficient de proratisation. Liquider chaque nom sur
 * ses seules années calculait deux salaires de référence là où la caisse
 * n'en calcule qu'un : « 30 077 € × 120/165 » plus « 36 778 € × 40/165 » au
 * lieu de « 34 152 € × 160/165 », de −7,2 % à +0,3 % contre l'oracle du
 * régime général.
 *
 * Le groupe est liquidé par le membre de la DERNIÈRE période active de la
 * carrière — à égalité, par l'absorbant —, dont la fiche donne les règles,
 * et c'est aussi ce que la LURA prescrit.
 *
 * ET LES RÉGIMES ALIGNÉS DISTINCTS SE RÉUNISSENT AUSSI, DEPUIS 2017. La
 * liquidation unique des régimes alignés (L. 173-1-2 CSS) donne une seule
 * retraite à qui a cotisé à deux des trois régimes alignés : un revenu
 * annuel moyen formé de la somme des salaires et revenus d'une même année,
 * sur les vingt-cinq meilleures, et une proratisation qui tient compte de
 * tous leurs trimestres (R. 173-4-4-1, 1° et 4°). Le modèle y arrivait pour
 * le couple régime général / indépendants par la chaîne d'absorption, qui
 * ne ferme le RSI qu'en 2018, et pas du tout pour les salariés agricoles.
 *
 * ET LES TROIS RÉGIMES DU CODE DES PENSIONS SONT INTERPÉNÉTRÉS : l'État, la
 * CNRACL et le FSPOEIE liquident chacun les services des deux autres, et le
 * régime de la dernière affiliation sert une pension unique, sur le
 * traitement des six derniers mois de la carrière publique entière. Voir
 * `regimesInterpenetres`.
 *
 * @returns {Map<string, string[]>}
 */
export function groupesDeSuccession(moteur, codes, anneeLiquidation, derniereAnneeParRegime, carriere = null) {
  const parTete = new Map();
  const lura = carriere !== null && luraApplicable(carriere);
  const interpenetres = carriere !== null ? regimesInterpenetres(moteur, carriere) : new Set();
  for (const code of codes) {
    const regime = moteur.catalogue.obtenir(code);
    const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
    if (periode === null || periode.type_calcul !== "annuites") {
      continue;
    }
    let tete = lura && REGIMES_ALIGNES.has(code)
      ? REGIMES_ALIGNES_TETE
      : teteDeSuccession(moteur, code, anneeLiquidation);
    if (interpenetres.has(tete)) {
      tete = REGIMES_INTERPENETRES_TETE;
    }
    if (!parTete.has(tete)) {
      parTete.set(tete, []);
    }
    parTete.get(tete).push(code);
  }
  const groupes = new Map();
  for (const membres of parTete.values()) {
    if (membres.length < 2) {
      continue;
    }
    const rang = new Map(chaineDepuis(moteur, membres).map((code, i) => [code, i]));
    let liquidateur = membres[0];
    for (const code of membres) {
      const derniere = derniereAnneeParRegime.get(code) ?? 0;
      const reference = derniereAnneeParRegime.get(liquidateur) ?? 0;
      if (derniere > reference
          || (derniere === reference && rang.get(code) > rang.get(liquidateur))) {
        liquidateur = code;
      }
    }
    const ordonnes = [
      liquidateur,
      ...[...membres].sort((a, b) => rang.get(a) - rang.get(b))
        .filter((code) => code !== liquidateur),
    ];
    for (const code of membres) {
      groupes.set(code, ordonnes);
    }
  }
  return groupes;
}
