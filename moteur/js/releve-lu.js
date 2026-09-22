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
 * Au-delà, la ligne n'est pas une ligne de tableau. Une année de relevé porte
 * son millésime, un revenu, des trimestres, parfois des points : cinq nombres
 * au plus. Quarante nombres sur une ligne, c'est une couche de doublure où
 * toute une page a été collée bout à bout.
 */
export const NOMBRES_PAR_LIGNE = 6;

/**
 * Au-delà, la ligne n'est pas une ligne de tableau non plus : c'est une
 * PHRASE. « Pour valider un trimestre, il faut avoir perçu un certain revenu.
 * En 2026, il faut avoir perçu au moins 1 803,00 € pour valider 1 trimestre »
 * porte une année, un montant en euros et des trimestres, tous correctement
 * étiquetés : rien, dans les nombres, ne la distingue d'une ligne de carrière.
 * Ce qui l'en distingue, c'est qu'elle est écrite en français.
 */
export const MOTS_PAR_LIGNE = 12;

/**
 * Ce qui annonce la date du document. Un relevé ne rapporte jamais l'avenir :
 * les années postérieures à son édition sont des projections — « En partant au
 * 01/06/2060 … vous pourriez avoir droit à 2 764,30 € » — et non des carrières.
 */
export const EDITION = ["edite le", "editee le", "situation au", "releve au",
  "arrete au", "mis a jour le"];

/** Ce qu'on lit devant une date pour savoir si elle est celle du document. */
const AVANT_LA_DATE = 24;


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

const EUROS = ["eur", "euro", "euros"];
const POINTS = ["pt", "pts", "point", "points"];

/**
 * Ce que l'unité écrite derrière un nombre dit de ce nombre.
 *
 * C'est l'information la plus sûre d'un relevé, et la seule qui ne dépende pas
 * de la mise en page : « 49 150 € » est un revenu où qu'il se trouve dans la
 * ligne, « 4 trim. » une durée, « 203,91 pts » des points. Le signe € se
 * cherche sur le texte BRUT : il ne survit pas à la mise à plat, qui ne garde
 * que des lettres et des chiffres.
 */
function uniteDe(suite) {
  if (suite.trimStart().startsWith("\u20ac")) return "revenu";
  const plat = sansAccent(suite);
  const premier = plat ? plat.split(" ")[0] : "";
  if (EUROS.includes(premier)) return "revenu";
  if (premier.startsWith("trim")) return "trimestre";
  if (POINTS.includes(premier)) return "point";
  return null;
}

/**
 * Ce qu'on regarde derrière un nombre pour y chercher son unité : de quoi
 * couvrir « trimestres » sans mordre sur la colonne suivante.
 */
const SUITE_LUE = 12;

/** Les nombres d'une ligne, avec leur unité quand elle est écrite. */
function nombresDe(reste) {
  const valeurs = [];
  MONTANT.lastIndex = 0;
  for (let t = MONTANT.exec(reste); t; t = MONTANT.exec(reste)) {
    let nombre = Number(t[1].replace(/[ \u00a0\u202f\u2009]/g, ""));
    if (t[2]) nombre += Number(t[2]) / (10 ** t[2].length);
    const suite = reste.slice(t.index + t[0].length,
                              t.index + t[0].length + SUITE_LUE);
    valeurs.push([nombre, uniteDe(suite)]);
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
 * L'année d'édition du document, quand il la porte en toutes lettres.
 *
 * C'est la date qui SUIT le marqueur, et non la plus tardive de la ligne : une
 * couche de doublure colle toute une page sur une seule ligne, et l'on y trouve
 * « Edité le 22/09/2026 » à côté de « En partant au 01/06/2066 ».
 */
function anneeDuDocument(lignes) {
  let derniere = null;
  for (const ligne of lignes) {
    DATE.lastIndex = 0;
    for (let t = DATE.exec(ligne); t; t = DATE.exec(ligne)) {
      const avant = sansAccent(ligne.slice(Math.max(0, t.index - AVANT_LA_DATE), t.index));
      if (!EDITION.some((marqueur) => avant.endsWith(marqueur))) continue;
      const annee = Number(t[3]);
      if (derniere === null || annee > derniere) derniere = annee;
    }
  }
  return derniere;
}

/**
 * L'année de la ligne, les nombres qui restent, si elle couvre une plage, si
 * son millésime ne vient que d'une date, et combien de dates elle porte.
 *
 * Les dates en clair sont retirées d'abord : leurs jours et leurs mois sont des
 * nombres de un à trente et un, qu'on lirait pour des trimestres. Quand une
 * ligne en porte deux d'années différentes, elle décrit une PÉRIODE de
 * plusieurs années que la maille annuelle du modèle ne sait pas répartir : on
 * ne la lit pas, on la montre.
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
    const [nombre, unite] = nombres[rang];
    // Le millésime ouvre la ligne, ou ne porte pas d'unité. La réserve est pour
    // le tableau qui écrit « 2011 Points Agirc 415,20 » : lue comme une unité,
    // la colonne suivante ferait de l'année un nombre de points.
    if (Number.isInteger(nombre) && nombre >= ANNEE_MINIMALE && nombre <= ANNEE_MAXIMALE
        && (unite === null || rang === 0)) {
      annee = nombre;
      nombres = nombres.slice(0, rang).concat(nombres.slice(rang + 1));
      break;
    }
  }
  const parLaDate = annee === null && anneesDesDates.length > 0;
  if (parLaDate) [annee] = anneesDesDates;
  return { annee, nombres, plage, parLaDate, dates: anneesDesDates.length };
}

/**
 * Lit un relevé, ligne à ligne, et rend la carrière qu'il décrit.
 *
 * Cinq règles, éprouvées sur un vrai document — l'estimation retraite que
 * délivre Info Retraite, qui empile un tableau des trimestres par année et un
 * tableau des revenus par période :
 *
 * 1. **Une ligne qui NOMME un régime ouvre une section**, et les lignes qui
 *    suivent en relèvent. Seul un régime qui porte une carrière donne son
 *    statut à l'année ; une caisse complémentaire n'en donne aucun.
 * 2. **L'unité écrite l'emporte sur la position** : « 49 150 € » est un
 *    revenu, « 4 trim. » une durée, « 203,91 pts » des points, où qu'ils
 *    tombent dans la ligne. Un tableau qui n'écrit pas ses unités se lit à la
 *    position, le revenu au-dessus de quatre et les trimestres en dessous.
 * 3. **Une année revient autant de fois que le relevé la coupe** : les revenus
 *    s'additionnent, les trimestres aussi, plafonnés à quatre.
 * 4. **Ce qui ressemble à une ligne sans en être une est écarté** : une phrase
 *    française, une ligne de quarante nombres, une date de référence sans sa
 *    seconde borne, une année postérieure à l'édition du document.
 * 5. **Ce qui n'est pas compris n'est pas deviné** : la ligne ressort telle
 *    quelle dans `ignorees`, et le site la montre.
 *
 * `anneeMaximale` borne les années lues — le site passe l'année courante. La
 * date d'édition du document, quand il la porte, la resserre encore.
 */
export function lireReleve(lignes, anneeMaximale = null) {
  let courant = null;
  let section = null;
  const annees = new Map();
  const ignorees = [];
  const regimes = [];
  const cadres = new Set();
  let francs = false;
  let points = false;
  let naissance = null;

  // Le plafond des années lues : celui que l'appelant donne, resserré par la
  // date d'édition du document quand il la porte. Ce qui est postérieur est une
  // projection, pas une carrière.
  const edition = anneeDuDocument(lignes);
  let plafond = anneeMaximale;
  if (edition !== null) plafond = plafond === null ? edition : Math.min(plafond, edition);

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
      // DEUX RÉGIMES COURANTS, ET C'EST LE RELEVÉ QUI L'IMPOSE. La SECTION est
      // le dernier régime nommé, quel qu'il soit : les lignes qui suivent
      // « Ircantec » en relèvent même si elles ne le répètent pas. La BASE est
      // le dernier régime qui porte une carrière : c'est de lui que vient le
      // statut de l'année, jamais de la caisse qui ne tient que des points.
      section = regime;
      if (regime.genre !== "indice") courant = regime;
      if (!regimes.includes(regime.code)) regimes.push(regime.code);
    }

    const { annee, nombres, plage, parLaDate, dates } = anneeEtNombres(ligne);
    if (annee === null) continue;
    if (plage) { ignorees.push(ligne); continue; }
    // UNE LIGNE DE TABLEAU PORTE QUELQUES COLONNES, PAS QUARANTE. Un PDF peut
    // porter deux fois le même texte — une couche visible, mise en page, et une
    // couche de doublure où tout est collé bout à bout.
    if (nombres.length > NOMBRES_PAR_LIGNE) { ignorees.push(ligne); continue; }
    if (plafond !== null && annee > plafond) continue;
    // UNE PÉRIODE A DEUX BORNES. Quand le millésime ne vient que d'une date,
    // une seule date ne suffit pas : « Valeur du point au 01/11/2025 : 1,4386 € »
    // et « 3 / 7 Edité le 22/09/2026 » en portent une, et toutes deux se
    // lisaient comme une année de carrière.
    if (parLaDate && dates < 2) continue;
    if (plat.split(" ").filter((mot) => mot.length > 1 && !/^\d+$/.test(mot))
      .length > MOTS_PAR_LIGNE) continue;

    const motif = motifDe(plat);
    const emploi = EMPLOIS.some((mot) => plat.includes(mot));

    // Le régime qui gouverne la ligne : celui qu'elle nomme, sinon celui de la
    // section où elle se trouve.
    const gouverne = regime !== null ? regime : section;
    const indiceSeul = gouverne !== null && gouverne.genre === "indice";
    if (indiceSeul && gouverne.code === "agirc") cadres.add(annee);
    if (courant === null) {
      if (nombres.length) ignorees.push(ligne);
      continue;
    }

    const etiquetes = nombres.filter(([, unite]) => unite).map(([, unite]) => unite);
    let revenu = 0.0;
    let trimestres = null;
    if (etiquetes.length) {
      for (const [valeur, unite] of nombres) {
        if (unite === "revenu") revenu = Math.max(revenu, valeur);
        else if (unite === "trimestre" && valeur <= TRIMESTRES_PAR_AN) {
          // Le dernier l'emporte, et jamais un cumul de carrière : « 172
          // trimestres » est un total, pas une année.
          trimestres = valeur;
        }
        // Les points sont lus, et jetés : ce n'est pas un revenu.
      }
    } else if (indiceSeul) {
      // Une ligne qui ne relève que d'un régime complémentaire et n'écrit
      // aucune unité ne dit rien qu'on sache lire : ses nombres sont des points
      // bien plus souvent que des euros.
      continue;
    } else {
      for (const [valeur] of nombres) {
        if (valeur > TRIMESTRES_PAR_AN || !Number.isInteger(valeur)) {
          revenu = Math.max(revenu, valeur);
        } else {
          // LE DERNIER l'emporte, et non le premier : les trimestres sont la
          // colonne de droite, et une année assimilée y porte « 0 4 ».
          trimestres = valeur;
        }
      }
    }
    if (courant.genre === "points") {
      // Le nombre lu est un nombre de POINTS, pas un revenu. L'année et ses
      // trimestres se gardent ; le revenu reste à compléter.
      if (revenu) points = true;
      revenu = 0.0;
    }
    if (parLaDate && !etiquetes.length) {
      // L'année ne vient que d'une date, et aucun nombre ne porte son unité :
      // la ligne ne dit pas de carrière. Si elle nomme tout de même un régime,
      // elle ressort — c'est une ligne dont une cellule manque.
      if (regime !== null && !indiceSeul) ignorees.push(ligne);
      continue;
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
