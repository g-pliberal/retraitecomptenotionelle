/**
 * Lire un relevé de carrière officiel, tel qu'une caisse l'imprime.
 *
 * Portage de ``src/retraite_notionnelle/web/releve_lu.py``, qui fait foi :
 * mêmes tables, mêmes règles, mêmes refus. `tests/test_releve_lu.py` fait
 * tourner les deux sur les mêmes relevés et compare la saisie qu'ils rendent,
 * caractère par caractère.
 *
 * Ce module n'est chargé que lorsqu'un relevé est déposé sur le site : il ne
 * sert pas au calcul, et le faire partir avec le reste du moteur coûterait à
 * tous ce dont un seul se sert.
 */

/** Le taux légal de conversion, fixé le 31 décembre 1998 et jamais révisé. */
export const FRANCS_PAR_EURO = 6.55957;
/** Cent anciens francs valent un franc depuis le 1er janvier 1960. */
export const ANCIENS_FRANCS_PAR_FRANC = 100.0;
/** La première année en euros sur un relevé. */
export const PREMIERE_ANNEE_EN_EUROS = 2002;
/** La première année en nouveaux francs. */
export const PREMIERE_ANNEE_EN_NOUVEAUX_FRANCS = 1960;

/**
 * Les bornes de `pages.js`, reprises ici pour ne pas lire comme une année de
 * carrière un nombre à quatre chiffres qui n'en est pas une.
 */
export const ANNEE_MINIMALE = 1914;
export const ANNEE_MAXIMALE = 2095;

/**
 * Au-delà, la ligne n'est pas un trimestre mais un montant : un relevé ne
 * valide jamais plus de quatre trimestres dans une année civile.
 */
export const TRIMESTRES_PAR_AN = 4;

/**
 * Les régimes qu'un relevé nomme, et le statut du simulateur qui leur
 * correspond. `genre` vaut « base » pour un régime qui porte une carrière en
 * euros, « points » pour un régime de base qui compte en points — professions
 * libérales, exploitants agricoles —, dont on lit les années et les trimestres
 * mais jamais un revenu qu'il ne porte pas, et « indice » pour un régime
 * complémentaire, qui ne porte aucune carrière mais dit le statut : des points
 * Agirc dans une année disent que l'emploi était un emploi de cadre.
 *
 * L'ordre ne compte pas : c'est l'alias le plus long qui gagne, sans quoi
 * « agirc » trancherait avant « agirc-arrco ».
 */
export const REGIMES = [
  ["regime_general", "base", "salarie_prive_non_cadre", [
    "regime general", "cnav", "carsat", "assurance retraite",
    "caisse nationale d assurance vieillesse", "cramif", "cgss",
    "securite sociale des independants", "ssi", "rsi", "organic", "cancava",
  ]],
  ["msa_salaries", "base", "salarie_agricole", [
    "msa salaries", "salaries agricoles", "mutualite sociale agricole salaries",
  ]],
  ["msa_exploitants", "points", "exploitant_agricole", [
    "msa non salaries", "non salaries agricoles", "exploitants agricoles",
    "amexa", "ava agricole",
  ]],
  ["pension_civile_etat", "base", "fonctionnaire_etat", [
    "service des retraites de l etat", "sre", "pensions civiles et militaires",
    "pension civile", "fonction publique d etat", "retraites de l etat",
  ]],
  ["cnracl", "base", "fonctionnaire_territorial_hospitalier", [
    "cnracl", "agents des collectivites locales",
  ]],
  ["fspoeie", "base", "ouvrier_etat", ["fspoeie", "ouvriers de l etat"]],
  ["cnieg", "base", "agent_ieg", ["cnieg", "industries electriques et gazieres"]],
  ["sncf", "base", "agent_sncf", ["cprp sncf", "cprpsncf", "sncf"]],
  ["ratp", "base", "agent_ratp", ["crp ratp", "crpratp", "ratp"]],
  ["enim", "base", "marin", ["enim", "marins", "gens de mer"]],
  ["crpcen", "base", "clerc_de_notaire", ["crpcen", "clercs et employes de notaires"]],
  ["cavimac", "base", "ministre_du_culte", ["cavimac", "cultes"]],
  ["mines", "base", "mineur", ["canssm", "regime des mines", "mines"]],
  ["banque_de_france", "base", "agent_banque_de_france", ["banque de france"]],
  ["crpnpac", "base", "personnel_navigant", [
    "crpnpac", "personnel navigant", "navigants de l aeronautique",
  ]],
  ["opera", "base", "personnel_opera", ["opera national de paris", "cropera"]],
  ["comedie_francaise", "base", "personnel_comedie_francaise", ["comedie francaise"]],
  ["cnbf", "points", "avocat", ["cnbf", "barreaux francais", "avocats"]],
  ["carmf", "points", "medecin_liberal", ["carmf", "medecins de france"]],
  ["carcdsf", "points", "chirurgien_dentiste_ou_sage_femme", [
    "carcdsf", "chirurgiens dentistes", "sages femmes",
  ]],
  ["carpimko", "points", "auxiliaire_medical", ["carpimko", "auxiliaires medicaux"]],
  ["cavp", "points", "pharmacien", ["cavp", "pharmaciens"]],
  ["cavec", "points", "expert_comptable", ["cavec", "experts comptables"]],
  ["cavamac", "points", "agent_general_assurance", [
    "cavamac", "agents generaux d assurances",
  ]],
  ["cprn", "points", "notaire", ["cprn", "crn", "notaires"]],
  ["cavom", "points", "officier_ministeriel", ["cavom", "officiers ministeriels"]],
  ["cnavpl", "points", "profession_liberale", ["cipav", "cnavpl", "professions liberales"]],
  ["ircantec", "indice", "contractuel_public", ["ircantec"]],
  ["agirc", "indice", "salarie_prive_cadre", ["agirc"]],
  ["arrco", "indice", "salarie_prive_non_cadre", [
    "agirc arrco", "arrco", "retraite complementaire",
  ]],
  ["rafp", "indice", "fonctionnaire_etat", [
    "rafp", "retraite additionnelle de la fonction publique",
  ]],
].map(([code, genre, statut, alias]) => ({ code, genre, statut, alias }));

/**
 * Les motifs d'une année sans revenu, tels que le relevé les nomme. Le premier
 * qui se trouve dans la ligne l'emporte, l'ordre va donc du plus précis au plus
 * général : « chomage non indemnise » avant « chomage ».
 */
export const MOTIFS = [
  ["chomage non indemnise", "chomage_non_indemnise"],
  ["non indemnise", "chomage_non_indemnise"],
  ["chomage", "chomage_indemnise"],
  ["pole emploi", "chomage_indemnise"],
  ["france travail", "chomage_indemnise"],
  ["accident du travail", "accident_travail"],
  ["accident de travail", "accident_travail"],
  ["maternite", "maternite"],
  ["adoption", "maternite"],
  ["invalidite", "invalidite"],
  ["maladie", "maladie"],
  ["service national", "service_militaire"],
  ["service militaire", "service_militaire"],
  ["avpf", "education_enfant"],
  ["parent au foyer", "education_enfant"],
  ["education enfant", "education_enfant"],
  ["congé parental", "education_enfant"],
  ["conge parental", "education_enfant"],
  ["sans activite", "sans_activite"],
  ["inactivite", "sans_activite"],
];

/**
 * Ce à quoi se reconnaît un relevé, et sans quoi l'on ne lit rien.
 *
 * Un document quelconque porte des années et des nombres : le rapport de
 * l'OPEF sur les frais de l'épargne retraite, cent pages sans le moindre
 * relevé, y nommait au passage la Banque de France et rendait vingt-deux
 * « années de carrière » que personne n'avait vécues. Remplir un formulaire
 * avec cela serait pire que ne rien remplir — le lecteur corrigerait des
 * chiffres au lieu de comprendre qu'il s'est trompé de fichier.
 *
 * Ce qu'on cherche est donc le TITRE du document, ou l'en-tête de la colonne
 * qui compte les trimestres. Le mot « trimestre » seul ne suffit pas : ce même
 * rapport de l'OPEF écrit « trimestre par trimestre » au détour d'une phrase
 * sur le calcul d'une performance, et cela rouvrait la porte en entier.
 */
export const MARQUEURS = ["trimestres retenus", "trimestres cotises",
  "trimestres valides", "trimestres assimiles", "nombre de trimestres",
  "total des trimestres", "trimestres acquis", "releve de carriere",
  "releve de situation individuelle", "releve individuel de situation",
  "duree d assurance"];

/**
 * Ce qui désigne un emploi, et interdit donc de lire la ligne comme une
 * interruption même quand elle ne porte aucun revenu — une année d'emploi à
 * revenu inconnu reste une année d'emploi.
 */
export const EMPLOIS = ["salarie", "emploi", "activite", "apprentissage",
  "employeur", "travailleur", "stage", "titulaire", "services"];

/**
 * L'euro le plus proche, la moitié vers le haut. Ni `Math.round`, qui arrondit
 * vers le haut aussi pour les négatifs, ni `round` de Python, qui arrondit à
 * l'entier PAIR : la règle est écrite, et la même des deux côtés du portage.
 */
export function arrondi(montant) {
  return Math.floor(montant + 0.5);
}

/**
 * Le texte en minuscules, sans accent et sans ponctuation séparatrice. C'est
 * la forme sur laquelle les alias se cherchent : « Agirc-Arrco », « AGIRC
 * ARRCO » et « agirc/arrco » sont le même nom, et une caisse ne l'écrit pas
 * deux fois de la même façon d'un document à l'autre.
 */
export function sansAccent(texte) {
  const plat = texte.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  return plat.replace(/[^a-z0-9]+/g, " ").replace(/\s+/g, " ").trim();
}

/**
 * Un montant : des chiffres, des groupes de milliers de TROIS chiffres
 * exactement — séparés par une espace ordinaire, une insécable ou une fine —,
 * puis des centimes derrière une virgule ou un point. La règle des trois
 * chiffres est ce qui sépare « 1998 14 200 4 » en une année, un montant et des
 * trimestres : « 14 200 » se recolle, « 4 » reste seul.
 */
const MONTANT = /(?<![\d,.])(\d{1,3}(?:[    ]\d{3})+|\d+)(?:[.,](\d{1,2}))?(?!\d)/g;

/**
 * Une date écrite en clair. Un relevé de fonction publique décrit ses services
 * par leurs bornes — « du 01/09/1996 au 31/08/2001 » — et ces jours et ces mois
 * sont des nombres qu'on lirait pour des trimestres : ils sont donc retirés de
 * la ligne avant tout comptage, et leur année retenue à part.
 */
const DATE = /(?<!\d)(\d{1,2})[/.-](\d{1,2})[/.-]((?:1[89]|20)\d{2})(?!\d)/g;

/**
 * Ce qui annonce la date de naissance sur un relevé. Elle y figure en tête,
 * sous le nom de l'assuré : c'est la seule donnée du formulaire, hors la
 * carrière elle-même, que le document porte — et celle dont tout le reste
 * dépend, l'âge légal comme la durée requise.
 */
export const NAISSANCE = ["date de naissance", "ne le", "nee le", "ne e le"];

/** La date de naissance qu'une ligne d'en-tête annonce, au format ISO. */
function naissanceDe(ligne, plat) {
  if (!NAISSANCE.some((marqueur) => plat.includes(marqueur))) return null;
  DATE.lastIndex = 0;
  const date = DATE.exec(ligne);
  if (date === null) return null;
  const [, jour, mois, annee] = date;
  return `${String(Number(annee)).padStart(4, "0")}-`
    + `${String(Number(mois)).padStart(2, "0")}-${String(Number(jour)).padStart(2, "0")}`;
}

function regimeDe(plat) {
  let trouve = null;
  let longueur = 0;
  for (const regime of REGIMES) {
    for (const alias of regime.alias) {
      const motif = new RegExp(`(?<![a-z0-9])${alias.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?![a-z0-9])`);
      if (alias.length > longueur && motif.test(plat)) {
        trouve = regime;
        longueur = alias.length;
      }
    }
  }
  return trouve;
}

function motifDe(plat) {
  for (const [texte, motif] of MOTIFS) {
    if (plat.includes(sansAccent(texte))) return motif;
  }
  return null;
}

/** Les nombres d'une ligne, virgule décimale et milliers recollés. */
function nombresDe(reste) {
  const valeurs = [];
  MONTANT.lastIndex = 0;
  for (let t = MONTANT.exec(reste); t; t = MONTANT.exec(reste)) {
    let nombre = Number(t[1].replace(/[    ]/g, ""));
    if (t[2]) nombre += Number(t[2]) / (10 ** t[2].length);
    valeurs.push(nombre);
  }
  return valeurs;
}

/** Le montant d'une année, ramené en euros de cette année-là. */
function enEuros(montant, annee) {
  if (annee >= PREMIERE_ANNEE_EN_EUROS) return montant;
  if (annee >= PREMIERE_ANNEE_EN_NOUVEAUX_FRANCS) return montant / FRANCS_PAR_EURO;
  return montant / (FRANCS_PAR_EURO * ANCIENS_FRANCS_PAR_FRANC);
}

/**
 * L'année de la ligne, les nombres qui restent, et si elle couvre une plage.
 *
 * Les dates en clair sont retirées d'abord : leurs jours et leurs mois sont des
 * nombres de un à trente et un, qu'on lirait pour des trimestres. Quand une
 * ligne en porte deux d'années différentes, elle décrit une PÉRIODE de
 * plusieurs années — un état de services de la fonction publique — que la
 * maille annuelle du modèle ne sait pas répartir : on ne la lit pas, on la
 * montre.
 */
function anneeEtNombres(ligne) {
  const anneesDesDates = [];
  DATE.lastIndex = 0;
  for (let t = DATE.exec(ligne); t; t = DATE.exec(ligne)) anneesDesDates.push(Number(t[3]));
  const reste = ligne.replace(DATE, " ");
  let nombres = nombresDe(reste);
  const plage = new Set(anneesDesDates).size > 1;
  let annee = null;
  for (let rang = 0; rang < nombres.length; rang += 1) {
    const nombre = nombres[rang];
    if (Number.isInteger(nombre) && nombre >= ANNEE_MINIMALE && nombre <= ANNEE_MAXIMALE) {
      annee = nombre;
      nombres = nombres.slice(0, rang).concat(nombres.slice(rang + 1));
      break;
    }
  }
  if (annee === null && anneesDesDates.length) [annee] = anneesDesDates;
  return { annee, nombres, plage };
}

/**
 * Lit un relevé, ligne à ligne, et rend la carrière qu'il décrit.
 *
 * Quatre règles, et elles suffisent à lire les relevés des deux formes — celui
 * du régime général, une seule caisse et un seul tableau, et le relevé de
 * situation individuelle, qui empile un tableau par régime :
 *
 * 1. **Une ligne qui NOMME un régime le rend courant** pour celles qui suivent.
 * 2. **Une ligne de carrière porte son année**, en général la première. Un
 *    nombre supérieur à quatre est un revenu ; un nombre de quatre au plus est
 *    un compte de trimestres, et c'est le dernier qui compte.
 * 3. **Une année revient autant de fois que le relevé la coupe** : les revenus
 *    s'additionnent, les trimestres aussi, plafonnés à quatre.
 * 4. **Ce qui n'est pas compris n'est pas deviné** : la ligne ressort telle
 *    quelle dans `ignorees`, et le site la montre.
 */
export function lireReleve(lignes) {
  let courant = null;
  const annees = new Map();
  const ignorees = [];
  const regimes = [];
  const cadres = new Set();
  let francs = false;
  let points = false;
  let naissance = null;

  const platEntier = sansAccent(lignes.join(" "));
  if (!MARQUEURS.some((marqueur) => platEntier.includes(marqueur))) {
    return {
      lignes: [], interruptions: [], ignorees: [], regimes: [], naissance: null,
      notes: [
        "Ce document ne ressemble pas à un relevé de carrière : ni son titre, "
        + "ni la colonne des trimestres qu'une caisse imprime toujours ne s'y "
        + "trouvent. Rien n'en a été lu, plutôt que d'en tirer des années qui "
        + "n'existent pas.",
      ],
    };
  }

  for (const brute of lignes) {
    const ligne = brute.trim();
    if (!ligne) continue;
    const plat = sansAccent(ligne);
    const entete = naissanceDe(ligne, plat);
    if (entete !== null) {
      // La ligne qui porte la date de naissance n'est pas une ligne de
      // carrière : lue comme telle sous un titre de régime, elle ouvrirait une
      // année de travail à l'âge de zéro an.
      if (naissance === null) naissance = entete;
      continue;
    }
    const regime = regimeDe(plat);
    if (regime !== null) {
      courant = regime;
      if (!regimes.includes(regime.code)) regimes.push(regime.code);
    }

    const { annee, nombres, plage } = anneeEtNombres(ligne);
    if (annee === null) continue;
    if (plage) { ignorees.push(ligne); continue; }

    const motif = motifDe(plat);
    const emploi = EMPLOIS.some((mot) => plat.includes(mot));

    if (courant !== null && courant.genre === "indice") {
      if (courant.code === "agirc") cadres.add(annee);
      continue;
    }
    if (courant === null) {
      if (nombres.length) ignorees.push(ligne);
      continue;
    }

    let trimestres = null;
    let revenu = 0.0;
    for (const nombre of nombres) {
      if (nombre > TRIMESTRES_PAR_AN || !Number.isInteger(nombre)) {
        revenu = Math.max(revenu, nombre);
      } else {
        // LE DERNIER l'emporte : les trimestres sont la colonne de droite, et
        // une année assimilée y porte « 0 4 » — zéro euro, quatre trimestres.
        trimestres = nombre;
      }
    }
    if (courant.genre === "points") {
      if (revenu) points = true;
      revenu = 0.0;
    }
    if (revenu === 0.0 && trimestres === null && !motif && !emploi) {
      ignorees.push(ligne);
      continue;
    }

    const montant = enEuros(revenu, annee);
    if (!annees.has(annee)) {
      annees.set(annee, {
        revenu: 0.0, trimestres: null, statut: "", revenuDuStatut: -1.0,
        motif: null, source: "",
      });
    }
    const cumul = annees.get(annee);
    cumul.revenu += montant;
    if (trimestres !== null) {
      cumul.trimestres = Math.min(TRIMESTRES_PAR_AN, (cumul.trimestres ?? 0) + trimestres);
    }
    if (montant >= cumul.revenuDuStatut || !cumul.statut) {
      cumul.statut = courant.statut;
      cumul.revenuDuStatut = montant;
    }
    if (motif && !cumul.motif) cumul.motif = motif;
    if (!cumul.source) cumul.source = ligne;
    if (annee < PREMIERE_ANNEE_EN_EUROS && revenu) francs = true;
  }

  const lues = [];
  const interruptions = [];
  for (const annee of [...annees.keys()].sort((a, b) => a - b)) {
    const cumul = annees.get(annee);
    let statut = cumul.statut;
    if (cadres.has(annee) && statut === "salarie_prive_non_cadre") {
      statut = "salarie_prive_cadre";
    }
    if (cumul.revenu <= 0 && cumul.motif) interruptions.push([annee, annee, cumul.motif]);
    lues.push({
      annee, statut, revenu: cumul.revenu, trimestres: cumul.trimestres,
      motif: cumul.motif, source: cumul.source,
    });
  }

  const notes = [];
  if (francs) {
    notes.push(
      "Les revenus antérieurs à 2002 ont été convertis en euros : divisés par "
      + "6,55957 pour les francs, par 655,957 pour les années antérieures à "
      + "1960, qu'un relevé porte en anciens francs.",
    );
  }
  if (cadres.size) {
    notes.push(
      "Des points Agirc figurent au relevé : les années qu'ils couvrent sont "
      + "lues comme des années de cadre.",
    );
  }
  if (points) {
    notes.push(
      "Un régime qui compte en points — professions libérales, exploitants "
      + "agricoles — ne porte pas de revenu au relevé : ses années sont lues "
      + "sans montant, à compléter à la main.",
    );
  }
  if (regimes.some((code) => code === "regime_general" || code === "msa_salaries")) {
    notes.push(
      "Le revenu porté au relevé est plafonné : au-delà du plafond de la "
      + "Sécurité sociale, le salaire n'y figure pas en entier, et la "
      + "simulation lit ce que le relevé porte.",
    );
  }
  return {
    lignes: lues, interruptions: fusionner(interruptions), ignorees, regimes,
    notes, naissance,
  };
}

/**
 * Recolle les années voisines de même motif en une seule plage : le champ
 * « Interruptions » du formulaire s'écrit par plages, et huit années de chômage
 * consécutives y tiennent en une ligne plutôt qu'en huit.
 */
function fusionner(interruptions) {
  const fusionnees = [];
  const triees = [...interruptions].sort((a, b) => a[0] - b[0]
    || String(a[2]).localeCompare(String(b[2])));
  for (const [debut, fin, motif] of triees) {
    const dernier = fusionnees[fusionnees.length - 1];
    if (dernier && dernier[2] === motif && dernier[1] === debut - 1) {
      dernier[1] = fin;
    } else {
      fusionnees.push([debut, fin, motif]);
    }
  }
  return fusionnees;
}

/** La saisie du formulaire : le relevé, et les interruptions. */
export function parametresDe(lecture) {
  const releve = lecture.lignes.map((ligne) => (
    `${ligne.annee}:${ligne.statut}:${arrondi(ligne.revenu)}`
    + (ligne.trimestres === null ? "" : `:${ligne.trimestres}`)
  )).join("\n");
  const interruptions = lecture.interruptions
    .map(([debut, fin, motif]) => `${debut}:${fin}:${motif}`).join(",");
  return { releve, interruptions };
}
