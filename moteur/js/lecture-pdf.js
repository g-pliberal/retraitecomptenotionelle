/**
 * Extraction de texte PDF avec mise en page, dans le navigateur.
 *
 * Portage de ``scripts/fetch/lecture_pdf.py``, qui fait foi : mêmes fonctions,
 * mêmes expressions régulières, mêmes défauts corrigés — les flux d'objets
 * compressés, les polices à encodage propre, l'échelle de la matrice de texte,
 * le numéro de flux dans la clé de regroupement. Toute correction apportée d'un
 * côté est à porter de l'autre, et `tests/js/lecture-pdf.test.js` rejoue ici
 * les documents minimaux de `tests/test_lecture_pdf.py`.
 *
 * Deux écarts, et deux seulement, imposés par le navigateur :
 *
 * 1. **La décompression est asynchrone.** `zlib.decompress` n'a pas
 *    d'équivalent synchrone en JavaScript ; `DecompressionStream("deflate")`
 *    en tient lieu, et il rend une promesse. Les flux sont donc TOUS dépliés
 *    d'abord, en une passe, et le reste de la lecture se fait ensuite sans
 *    attendre : la structure du module Python est conservée, seul son point
 *    d'entrée devient `async`.
 * 2. **Les octets sont portés par une chaîne latin-1**, un caractère par
 *    octet. C'est ce qui permet de reprendre mot pour mot les expressions
 *    régulières binaires du modèle de référence, que JavaScript ne sait pas
 *    appliquer à un `Uint8Array`.
 *
 * Le fichier n'est lu que dans la page : rien n'est envoyé nulle part, et le
 * module n'est chargé qu'au moment où quelqu'un dépose un PDF.
 */

/** Les cinq lettres échappées de la norme, hors octal. */
const LETTRES = { n: "\n", r: "\r", t: "\t", b: "\b", f: "\f" };

/**
 * Les échappements d'une chaîne littérale : octal, les cinq lettres, la barre
 * devant une parenthèse ou une barre, et la barre en fin de ligne, qui ne vaut
 * rien. Traités en une passe, de gauche à droite, comme le fait un lecteur :
 * deux passes rendaient « \\101 » en « A ».
 */
const ECHAPPEMENT = /\\(?:([0-7]{1,3})|\r\n|\r|\n|([\s\S]))/g;

/**
 * Ce que cp1252 met là où latin-1 met des caractères de contrôle. C'est la
 * seule différence entre les deux encodages, et c'est celle qui porte les
 * guillemets typographiques, le tiret cadratin et l'œ — les caractères qu'une
 * police WinAnsi pose sans les déclarer dans sa table.
 */
const CP1252 = {
  0x80: "€", 0x82: "‚", 0x83: "ƒ", 0x84: "„",
  0x85: "…", 0x86: "†", 0x87: "‡", 0x88: "ˆ",
  0x89: "‰", 0x8A: "Š", 0x8B: "‹", 0x8C: "Œ",
  0x8E: "Ž", 0x91: "‘", 0x92: "’", 0x93: "“",
  0x94: "”", 0x95: "•", 0x96: "–", 0x97: "—",
  0x98: "˜", 0x99: "™", 0x9A: "š", 0x9B: "›",
  0x9C: "œ", 0x9E: "ž", 0x9F: "Ÿ",
};

/** Les octets d'un fichier, portés par une chaîne d'un caractère par octet. */
export function enChaine(octets) {
  const morceaux = [];
  for (let i = 0; i < octets.length; i += 0x8000) {
    morceaux.push(String.fromCharCode.apply(
      null, octets.subarray(i, Math.min(i + 0x8000, octets.length)),
    ));
  }
  return morceaux.join("");
}

function enOctets(chaine) {
  const octets = new Uint8Array(chaine.length);
  for (let i = 0; i < chaine.length; i += 1) {
    octets[i] = chaine.charCodeAt(i) & 0xff;
  }
  return octets;
}

/**
 * La somme de contrôle qu'un flux zlib pose derrière ses données. Elle sert
 * ici à distinguer les deux échecs que `DecompressionStream` confond — voir
 * {@link inflater}.
 */
function adler32(octets) {
  let a = 1;
  let b = 0;
  for (let rang = 0; rang < octets.length;) {
    // Le modulo tous les 5 552 octets : c'est le plus grand nombre de tours
    // qui ne peut pas déborder, et le prendre à chaque tour coûterait dix fois
    // plus cher sur un flux d'un méga-octet.
    const fin = Math.min(rang + 5552, octets.length);
    for (; rang < fin; rang += 1) { a += octets.charCodeAt(rang) & 0xff; b += a; }
    a %= 65521; b %= 65521;
  }
  return ((b << 16) | a) >>> 0;
}

/**
 * Déplie un flux comprimé, en rendant `null` comme le modèle de référence
 * quand il n'y parvient pas.
 *
 * `DecompressionStream` lève dans DEUX cas que `zlib.decompress` sépare : le
 * flux tronqué, dont Python ne rend rien, et les octets qu'un producteur
 * laisse traîner derrière la fin du flux, que Python ignore en silence après
 * avoir tout rendu. Les confondre écarte le portage du modèle dans un sens ou
 * dans l'autre : rendre ce qui a été lu, c'est lire cinq lignes de plus qu'en
 * Python sur un document abîmé ; ne rien rendre, c'est en perdre tout un flux
 * sur un document sain mais bavard.
 *
 * On les sépare donc comme zlib le fait : un flux complet porte derrière ses
 * données la somme Adler-32 de ce qu'il vient de rendre. Si on la retrouve
 * dans la queue de l'entrée, le flux s'est terminé et ce qui suit n'est que du
 * bavardage ; sinon, il est tronqué, et l'on ne rend rien.
 */
const QUEUE_BAVARDE = 1024;

async function inflater(donnees) {
  const flux = new Blob([enOctets(donnees)]).stream()
    .pipeThrough(new DecompressionStream("deflate"));
  const lecteur = flux.getReader();
  const morceaux = [];
  let acheve = true;
  try {
    for (;;) {
      const { done, value } = await lecteur.read();
      if (done) break;
      morceaux.push(value);
    }
  } catch {
    acheve = false;
  }
  const taille = morceaux.reduce((somme, part) => somme + part.length, 0);
  const tout = new Uint8Array(taille);
  let rang = 0;
  for (const part of morceaux) { tout.set(part, rang); rang += part.length; }
  const texte = enChaine(tout);
  if (acheve) return texte;
  const somme = adler32(texte);
  const queue = donnees.slice(Math.max(0, donnees.length - QUEUE_BAVARDE));
  for (let i = 0; i + 4 <= queue.length; i += 1) {
    const lue = ((queue.charCodeAt(i) & 0xff) * 0x1000000)
      + ((queue.charCodeAt(i + 1) & 0xff) << 16)
      + ((queue.charCodeAt(i + 2) & 0xff) << 8)
      + (queue.charCodeAt(i + 3) & 0xff);
    if (lue >>> 0 === somme) return texte;
  }
  return null;
}

// -- objets et flux ---------------------------------------------------------

const OBJET = /(\d+)\s+0\s+obj\b([\s\S]*?)\bendobj/g;
const DONNEES_DE_FLUX = /stream\r?\n([\s\S]*?)endstream/;

/**
 * Tous les objets du fichier, ceux des flux d'objets compris, et le contenu
 * déplié de chaque flux.
 *
 * Un flux ``/ObjStm`` porte ``/N`` objets ; ses données commencent par ``N``
 * paires « numéro décalage », puis, à ``/First`` octets du début, les objets
 * eux-mêmes, sans ``obj``/``endobj``. On les range sous leur numéro, comme les
 * autres. Le flux lui-même reste dans le dictionnaire : il ne porte ni texte ni
 * police, il ne gêne pas.
 */
async function lireObjets(octets) {
  const objets = new Map();
  OBJET.lastIndex = 0;
  for (let trouve = OBJET.exec(octets); trouve; trouve = OBJET.exec(octets)) {
    objets.set(Number(trouve[1]), trouve[2]);
  }
  // Tous les flux sont dépliés d'une seule traite : c'est la seule partie
  // asynchrone de la lecture, et la garder en un point unique laisse le reste
  // du portage identique, ligne pour ligne, au modèle Python.
  const flux = new Map();
  await Promise.all([...objets].map(async ([numero, objet]) => {
    const donnees = DONNEES_DE_FLUX.exec(objet);
    if (!donnees) return;
    if (!objet.includes("/FlateDecode")) {
      flux.set(numero, donnees[1]);
      return;
    }
    const deplie = await inflater(donnees[1].replace(/^[\r\n]+|[\r\n]+$/g, ""));
    if (deplie !== null) flux.set(numero, deplie);
  }));

  for (const [numero, objet] of [...objets]) {
    if (!objet.includes("/ObjStm")) continue;
    const contenu = flux.get(numero);
    const nombre = /\/N\s+(\d+)/.exec(objet);
    const premier = /\/First\s+(\d+)/.exec(objet);
    if (!contenu || !nombre || !premier) continue;
    const debut = Number(premier[1]);
    const tete = contenu.slice(0, debut).split(/\s+/).filter(Boolean).map(Number);
    const paires = [];
    for (let i = 0; i < Math.min(2 * Number(nombre[1]), tete.length - 1); i += 2) {
      paires.push([tete[i], tete[i + 1]]);
    }
    paires.forEach(([numeroObjet, decalage], rang) => {
      const fin = rang + 1 < paires.length ? paires[rang + 1][1] : contenu.length - debut;
      // `setdefault` du modèle de référence : un objet écrit en clair dans le
      // fichier prime sur celui que porte le flux, jamais l'inverse.
      if (!objets.has(numeroObjet)) {
        objets.set(numeroObjet, contenu.slice(debut + decalage, debut + fin));
      }
    });
  }
  return { objets, flux };
}

// -- tables ToUnicode -------------------------------------------------------

/**
 * Une table ToUnicode, avec la largeur en octets de ses codes.
 *
 * ``codespacerange`` la déclare : ``<00> <FF>`` pour une police simple, un
 * octet ; ``<0000> <FFFF>`` pour une police Type0, deux. Sans déclaration,
 * deux — c'est ce que le lecteur a toujours supposé pour l'hexadécimal.
 */
class Table extends Map {
  constructor() {
    super();
    this.largeur = 2;
    //: L'encodage qui traduit un code absent de la table, quand la police en
    //: déclare un (``cp1252`` pour WinAnsiEncoding) ; sinon rien.
    this.repli = null;
  }
}

/** Une destination de table ToUnicode : de l'hexadécimal en UTF-16 gros-boutiste. */
function deHexa(chiffres) {
  let texte = "";
  for (let i = 0; i < chiffres.length; i += 4) {
    texte += String.fromCharCode(parseInt(chiffres.slice(i, i + 4).padEnd(4, "0"), 16));
  }
  return texte;
}

/**
 * Les jetons d'un bloc ``bfrange`` : un hexadécimal entre chevrons, ou l'un des
 * deux crochets qui encadrent une liste de destinations.
 */
const JETON_CMAP = /<([0-9A-Fa-f]+)>|([[\]])/g;

/**
 * Les entrées d'un bloc ``bfrange``, lues jeton par jeton.
 *
 * Une entrée s'écrit de DEUX façons, et la norme les mêle dans le même bloc :
 * `<début> <fin> <destination>`, où les codes suivants se déduisent en ajoutant
 * un, et `<début> <fin> [ <dst> <dst> … ]`, où chaque code a la sienne.
 * Les deux se sont présentées dans un même document : une estimation
 * retraite d'Info Retraite ré-exportée par un éditeur de bureau. La table
 * venait de l'éditeur, non de la caisse — mais la forme tableau est de la
 * norme, et un lecteur qui ne la connaît pas se trompe sur tout le document.
 *
 * Une expression régulière qui cherchait trois hexadécimaux d'affilée ignorait
 * les crochets et lisait À CHEVAL sur les entrées : de proche en proche, TOUTE
 * la table se décalait. Le document sortait en lettres fausses — et ses
 * chiffres, tombés sur des codes de contrôle, ne sortaient pas du tout.
 */
function plagesDe(bloc) {
  const jetons = [];
  JETON_CMAP.lastIndex = 0;
  for (let t = JETON_CMAP.exec(bloc); t; t = JETON_CMAP.exec(bloc)) {
    jetons.push(t[1] !== undefined ? { hexa: t[1] } : { delimiteur: t[2] });
  }
  const entrees = [];
  let rang = 0;
  while (rang < jetons.length) {
    if (jetons[rang].delimiteur) {
      // Un crochet là où l'on attend un début de plage : entrée abîmée, on la
      // saute plutôt que de décaler tout ce qui suit.
      rang += 1;
      continue;
    }
    if (rang + 1 >= jetons.length || jetons[rang + 1].delimiteur) break;
    const debut = jetons[rang].hexa;
    const fin = jetons[rang + 1].hexa;
    rang += 2;
    if (rang >= jetons.length) break;
    if (jetons[rang].delimiteur === "[") {
      rang += 1;
      const destinations = [];
      while (rang < jetons.length && !jetons[rang].delimiteur) {
        destinations.push(jetons[rang].hexa);
        rang += 1;
      }
      if (rang < jetons.length && jetons[rang].delimiteur === "]") rang += 1;
      entrees.push([debut, fin, destinations]);
    } else {
      entrees.push([debut, fin, jetons[rang].hexa]);
      rang += 1;
    }
  }
  return entrees;
}

/** Lit une table ToUnicode : code de glyphe -> caractère. */
function cmap(contenu) {
  const table = new Table();
  const largeurs = [];
  for (const bloc of contenu.match(/begincodespacerange[\s\S]*?endcodespacerange/g) ?? []) {
    for (const paire of bloc.match(/<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>/g) ?? []) {
      largeurs.push(Math.floor(/<([0-9A-Fa-f]+)>/.exec(paire)[1].length / 2));
    }
  }
  if (largeurs.length) table.largeur = Math.max(...largeurs);

  for (const bloc of contenu.match(/beginbfchar[\s\S]*?endbfchar/g) ?? []) {
    const paires = /<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>/g;
    for (let t = paires.exec(bloc); t; t = paires.exec(bloc)) {
      table.set(parseInt(t[1], 16), deHexa(t[2]));
    }
  }
  for (const bloc of contenu.match(/beginbfrange[\s\S]*?endbfrange/g) ?? []) {
    for (const [debut, fin, destinations] of plagesDe(bloc)) {
      const premiere = parseInt(debut, 16);
      const derniere = parseInt(fin, 16);
      if (Array.isArray(destinations)) {
        // La forme TABLEAU : une destination par code, dans l'ordre.
        destinations.forEach((dst, i) => {
          if (premiere + i <= derniere) table.set(premiere + i, deHexa(dst));
        });
        continue;
      }
      const premier = parseInt(destinations, 16);
      let i = 0;
      for (let code = premiere; code <= derniere; code += 1, i += 1) {
        // Une destination hors du plan Unicode — les rapports à la CCSS en
        // portent, dans des plages que rien n'utilise — ne doit pas faire
        // tomber la lecture de tout le document.
        if (premier + i > 0x10FFFF) break;
        table.set(code, String.fromCodePoint(premier + i));
      }
    }
  }
  return table;
}

/**
 * Le dictionnaire que ``cle`` (``/Resources``, ``/Font``) désigne dans
 * ``objet`` : écrit sur place entre ``<<`` et ``>>``, imbrications comprises,
 * ou par référence à un autre objet. Vide si absent.
 */
function dictionnaire(objet, cle, objets) {
  const trouve = new RegExp(`${cle}\\s*(?:(\\d+)\\s+0\\s+R|<<)`).exec(objet);
  if (!trouve) return "";
  if (trouve[1]) return objets.get(Number(trouve[1])) ?? "";
  const debut = trouve.index + trouve[0].length - 2;
  let profondeur = 0;
  for (let i = debut; i < objet.length - 1; i += 1) {
    if (objet.startsWith("<<", i)) profondeur += 1;
    else if (objet.startsWith(">>", i)) {
      profondeur -= 1;
      if (profondeur === 0) return objet.slice(debut, i + 2);
    }
  }
  return objet.slice(debut);
}

function tableDe(police, objets, flux) {
  const trouve = /\/ToUnicode\s+(\d+)\s+0\s+R/.exec(police);
  const contenu = trouve ? flux.get(Number(trouve[1])) : null;
  if (!contenu) return null;
  const table = cmap(contenu);
  // Une police simple — TrueType, Type1, Type3 — code ses glyphes sur UN
  // octet, quoi que déclare le codespacerange de sa table : InDesign y écrit
  // <0000> <FFFF> avec des entrées <64>, et lire par deux rendait le rapport
  // de l'OPEF en lettres perdues. Seule une police Type0 lit par deux.
  if (!/\/Subtype\s*\/Type0\b/.test(police)) {
    table.largeur = 1;
    // Et ce que sa table ne dit pas, son encodage le dit : un code absent
    // d'une table WinAnsi est la lettre WinAnsi de ce code.
    if (police.includes("WinAnsiEncoding")) table.repli = "cp1252";
  }
  return table;
}

/**
 * Pour chaque flux de contenu, les polices que SA page déclare.
 *
 * Le même nom — ``/TT0``, ``/F1`` — désigne une police différente d'une page à
 * l'autre dès qu'un producteur sous-ensemble ses polices par page, ce que Word
 * fait : chaque page a son ``/TT0`` et sa table. Une table unique par nom, la
 * dernière rencontrée, traduisait donc chaque page avec les codes d'une autre —
 * et c'est ce qui rendait le jaune budgétaire en lettres décalées.
 */
function policesParContenu(objets, flux) {
  const parContenu = new Map();
  for (const [numeroObjet, objet] of objets) {
    // Une page rattache ses polices à son flux ``/Contents`` ; un formulaire
    // (``/Subtype /Form``, un tableau collé depuis Excel, par exemple) est son
    // propre flux et porte ses propres ressources.
    const page = objet.includes("/Contents");
    if (!page && !(objet.includes("/Form") && objet.includes("/Resources"))) continue;
    const polices = dictionnaire(
      dictionnaire(objet, "/Resources", objets), "/Font", objets,
    );
    if (!polices) continue;
    const tables = new Map();
    const references = /\/(\w+)\s+(\d+)\s+0\s+R/g;
    for (let t = references.exec(polices); t; t = references.exec(polices)) {
      const table = tableDe(objets.get(Number(t[2])) ?? "", objets, flux);
      if (table) tables.set(t[1], table);
    }
    if (!page) { parContenu.set(numeroObjet, tables); continue; }
    const contenus = /\/Contents\s*(?:(\d+)\s+0\s+R|\[([^\]]*)\])/.exec(objet);
    if (!contenus) continue;
    const numeros = contenus[1]
      ? [Number(contenus[1])]
      : [...(contenus[2].match(/(\d+)\s+0\s+R/g) ?? [])].map((r) => Number(/\d+/.exec(r)[0]));
    for (const numero of numeros) parContenu.set(numero, tables);
  }
  return parContenu;
}

/**
 * Associe chaque nom de police (/F1…) à sa table ToUnicode, pour tout le
 * document : le repli quand aucune page ne rattache le flux.
 */
function polices(objets, flux) {
  const tables = new Map();
  for (const objet of objets.values()) {
    const references = /\/(\w+)\s+(\d+)\s+0\s+R/g;
    for (let t = references.exec(objet); t; t = references.exec(objet)) {
      const police = objets.get(Number(t[2]));
      if (!police || !police.includes("/Font")) continue;
      const vers = /\/ToUnicode\s+(\d+)\s+0\s+R/.exec(police);
      if (!vers) continue;
      const contenu = flux.get(Number(vers[1]));
      if (contenu) tables.set(t[1], cmap(contenu));
    }
  }
  return tables;
}

// -- lecture du texte -------------------------------------------------------

function litteral(brut, table) {
  const texte = brut.replace(ECHAPPEMENT, (tout, octal, lettre) => {
    if (octal !== undefined) return String.fromCharCode(parseInt(octal, 8) & 0xff);
    if (lettre !== undefined) return LETTRES[lettre] ?? lettre;
    return "";
  });
  if (!table) return texte;
  // Les octets de la chaîne sont des codes de la police, pas des lettres : la
  // table les traduit, par un ou par deux selon ce qu'elle déclare. Un code
  // qu'elle ne connaît pas et qui tombe dans l'ASCII imprimable est rendu tel
  // quel — une police qui numérote ses glyphes n'en produit pas, une police à
  // encodage standard n'en produit que.
  const largeur = table.largeur ?? 1;
  let sortie = "";
  for (let i = 0; i < texte.length; i += largeur) {
    let code = 0;
    for (let j = 0; j < largeur; j += 1) {
      if (i + j >= texte.length) break;
      code = (code << 8) | (texte.charCodeAt(i + j) & 0xff);
    }
    if (table.has(code)) { sortie += table.get(code); continue; }
    if (table.repli === "cp1252" && largeur === 1) {
      sortie += CP1252[code] ?? String.fromCharCode(code);
      continue;
    }
    if (code >= 32 && code < 127) sortie += String.fromCharCode(code);
  }
  return sortie;
}

function hexa(brut, table) {
  let chiffres = brut.replace(/[^0-9A-Fa-f]/g, "");
  const pas = 2 * (table ? table.largeur ?? 2 : 2);
  if (chiffres.length % pas) chiffres = chiffres.padEnd(chiffres.length + pas - (chiffres.length % pas), "0");
  let sortie = "";
  for (let i = 0; i < chiffres.length; i += pas) {
    const code = parseInt(chiffres.slice(i, i + pas), 16);
    if (table) sortie += table.get(code) ?? "";
    else if (code >= 32 && code < 0x3000) sortie += String.fromCharCode(code);
  }
  return sortie;
}

/**
 * Les opérateurs de texte utiles. ``TL`` fixe l'interligne, que ``T*``, ``'``
 * et ``"`` appliquent pour passer à la ligne suivante : sans eux, tout un
 * paragraphe reste à la même ordonnée et se retrouve collé sur une seule ligne.
 */
const JETONS = new RegExp([
  // ``BT`` ouvre un objet texte, et la norme y remet la matrice de texte à
  // l'identité : les ``Td`` qui suivent partent de l'origine de la page, et non
  // du curseur laissé par l'objet précédent. Sans ce jeton, un producteur qui
  // ouvre un ``BT`` par ligne — et c'est le cas des relevés de carrière que le
  // site reçoit — voyait ses ordonnées s'ADDITIONNER d'un bloc au suivant : la
  // page partait vers le haut à chaque ligne, et le document sortait à
  // l'envers, une ligne par fragment.
  "(?<bt>\\bBT\\b)",
  "(?<tm>[-\\d.]+\\s+[-\\d.]+\\s+[-\\d.]+\\s+[-\\d.]+\\s+[-\\d.]+\\s+[-\\d.]+\\s+Tm)",
  "(?<td>[-\\d.]+\\s+[-\\d.]+\\s+T[dD])",
  "(?<tl>[-\\d.]+\\s+TL)",
  "(?<etoile>T\\*)",
  "(?<retour>[)\\]]\\s*['\"])",
  "(?<tf>/(?<nomPolice>\\w+)\\s+[-\\d.]+\\s+Tf)",
  // Un dictionnaire en ligne — les propriétés d'un contenu balisé, « /Span
  // <</Lang (en-US)>> BDC » — porte des chaînes qui ne sont pas du texte : on
  // le saute d'un bloc, sinon « en-US » s'imprime entre chaque cellule.
  "(?<dict><<[\\s\\S]*?>>)",
  "(?<hex><[0-9A-Fa-f\\s]+>)",
  "(?<txt>\\((?:[^()\\\\]|\\\\[\\s\\S])*\\))",
  // Les crochets d'un tableau ``TJ`` et les nombres qu'il intercale entre ses
  // chaînes : un recul de plus d'un cinquième de cadratin est une espace que le
  // producteur n'a pas écrite — Word pose « Rapport » et « sur » dans le même
  // tableau, séparés par -250, et les coller rend « Rapportsur ».
  "(?<ouvre>\\[)",
  "(?<ferme>\\])",
  "(?<nombre>-?\\d+(?:\\.\\d+)?)",
].join("|"), "g");

const ESPACE_DE_TABLEAU = -180.0;

/**
 * La tête numérique d'un opérateur de position.
 *
 * On s'arrête au premier jeton qui n'est pas un nombre, ce qui laisse de côté
 * le nom de l'opérateur et, surtout, l'opérande réduit à « - » que certains
 * producteurs émettent. On ne devine jamais la valeur manquante — la mettre à
 * zéro déplacerait le texte sans prévenir : c'est à l'appelant de vérifier
 * qu'il en a assez, et de SAUTER l'opérateur sinon.
 */
function reels(operandes) {
  const valeurs = [];
  for (const jeton of operandes.trim().split(/\s+/)) {
    if (!/^[-+]?(\d+\.?\d*|\.\d+)$/.test(jeton)) break;
    valeurs.push(Number(jeton));
  }
  return valeurs;
}

/**
 * Reconstitue les fragments du document, avec leur page et leur position.
 *
 * LE NUMÉRO DE FLUX FAIT PARTIE DE LA CLÉ, et c'est tout sauf un détail.
 * Chaque page d'un PDF a son propre repère : l'ordonnée 700 y désigne le même
 * endroit de la feuille, page 1 comme page 60. Regrouper les fragments sur la
 * seule ordonnée collait bout à bout la ligne du haut de CHAQUE page.
 */
async function fragments(octets) {
  const { objets, flux } = await lireObjets(octets);
  const communes = polices(objets, flux);
  const parContenu = policesParContenu(objets, flux);
  const tous = [];
  let page = -1;
  for (const [numero, objet] of objets) {
    page += 1;
    // Une image JPEG contient « Tj » une fois sur dix, par hasard : on ne la
    // lit pas comme du texte.
    const debutFlux = objet.indexOf("stream");
    if (objet.slice(0, Math.max(debutFlux, 0)).includes("/Image")) continue;
    const contenu = flux.get(numero);
    if (!contenu || (!contenu.includes("Tj") && !contenu.includes("TJ"))) continue;
    const tables = parContenu.get(numero) ?? communes;
    let x = 0.0;
    let y = 0.0;
    // ÉCHELLE DE LA MATRICE DE TEXTE. `Tm` ne pose pas seulement une position,
    // il pose un repère : « 9 0 0 9 82.97 723.62 Tm » place le curseur ET
    // multiplie par neuf tout ce qui suit. Les décalages `Td` qui viennent
    // ensuite sont exprimés dans CE repère, pas en points de la page. Les
    // additionner tels quels écrasait les interlignes d'un facteur neuf, et
    // fondait en une seule des lignes distantes de quatorze points.
    let echelleX = 1.0;
    let echelleY = 1.0;
    let interligne = 0.0;
    let police = null;
    let dansTableau = false;
    // LE TEXTE TOURNÉ NE SE LIT PAS SUR LES MÊMES LIGNES QUE LE RESTE.
    // « 0 -1 -1 0 » est un quart de tour : c'est ainsi qu'un producteur pose un
    // tampon dans la marge, un filigrane, une étiquette d'axe. Ses glyphes
    // tombent aux ordonnées des lignes du corps de page, et les regrouper avec
    // elles y insérait des lettres et des chiffres étrangers — sur l'estimation
    // retraite d'Info Retraite, vingt-deux caractères par page venaient se
    // coller dans les montants du relevé, qui devenaient des revenus de deux
    // millions d'euros. La bande — 0 pour le texte droit, 1 pour le texte
    // tourné — entre donc dans la clé de regroupement.
    let bande = 0;
    JETONS.lastIndex = 0;
    for (let jeton = JETONS.exec(contenu); jeton; jeton = JETONS.exec(contenu)) {
      const g = jeton.groups;
      if (g.dict) continue;
      if (g.ouvre || g.ferme) { dansTableau = Boolean(g.ouvre); continue; }
      if (g.nombre) {
        if (dansTableau && Number(g.nombre) < ESPACE_DE_TABLEAU) {
          tous.push([page, bande, ...(bande ? [x, -y] : [y, x]), " "]);
        }
        continue;
      }
      if (g.bt) {
        x = 0.0;
        y = 0.0;
        echelleX = 1.0;
        echelleY = 1.0;
      } else if (g.tm) {
        const nombres = reels(g.tm);
        if (nombres.length < 6) continue;
        [echelleX, echelleY] = [nombres[0], nombres[3]];
        [x, y] = [nombres[4], nombres[5]];
        bande = nombres[1] || nombres[2] ? 1 : 0;
      } else if (g.td) {
        const nombres = reels(g.td);
        if (nombres.length < 2) continue;
        x += nombres[0] * echelleX;
        y += nombres[1] * echelleY;
        if (g.td.trimEnd().endsWith("TD")) interligne = -nombres[1] * echelleY;
      } else if (g.tl) {
        const nombres = reels(g.tl);
        if (!nombres.length) continue;
        interligne = nombres[0] * echelleY;
      } else if (g.etoile || g.retour) {
        y -= interligne;
      } else if (g.tf) {
        police = g.nomPolice;
      } else {
        const morceau = g.hex
          ? hexa(g.hex, tables.get(police))
          : litteral(g.txt.slice(1, -1), tables.get(police));
        const [ligne, colonne] = bande ? [x, -y] : [y, x];
        if (morceau.trim()) tous.push([page, bande, ligne, colonne, morceau]);
        else if (morceau) {
          // Une chaîne qui n'est qu'une espace est l'espace entre deux mots que
          // le producteur a posés séparément — « (Effectif) ( ) (total) » — :
          // la jeter les colle. Une insécable — la fine des milliers — reste
          // insécable, et c'est elle qui empêche « 2 132 milliards » de se lire
          // comme deux nombres.
          const insecable = morceau.replace(/[ \t\r\n\f\v]/g, "");
          tous.push([page, bande, ligne, colonne, insecable ? " " : " "]);
        }
      }
    }
  }
  return tous;
}

/**
 * Une espace pour toute suite d'espaces ordinaires ; UNE ESPACE INSÉCABLE pour
 * toute suite d'insécables (U+00A0, U+202F), et elle reste insécable. Un
 * document qui sépare ses milliers d'une fine insécable et ses cellules d'une
 * espace de position ne se découpe en nombres que si les deux restent
 * différentes.
 */
function normaliser(texte) {
  return texte.replace(/[  ]+/g, " ")
    .replace(/[ \t\r\n\f\v]+/g, " ").trim();
}

/** Regroupe des fragments déjà triés en lignes visuelles. */
function assembler(tous, tolerance) {
  const lignes = [];
  let courante = [];
  let ordonnee = null;
  let feuille = null;
  let abscisse = null;
  for (const [page, bande, y, x, morceau] of tous) {
    const memeLigne = ordonnee !== null && feuille !== null
      && page === feuille[0] && bande === feuille[1]
      && Math.abs(y - ordonnee) <= tolerance;
    if (memeLigne || ordonnee === null) {
      // DEUX FRAGMENTS POSÉS À DES ABSCISSES DIFFÉRENTES SONT SÉPARÉS PAR UNE
      // ESPACE. Word n'écrit pas les espaces d'un tableau : il pose chaque
      // cellule, et souvent chaque mot, par son propre ``Tm``. Les coller
      // rendait « 4 929 5 002 » comme « 49295002 » — un nombre qui n'existe
      // pas. Les glyphes d'un même tableau ``TJ``, eux, gardent la même
      // abscisse et restent collés : « 2023 » ne devient pas « 2 0 2 3 ».
      if (memeLigne && abscisse !== null && Math.abs(x - abscisse) > 0.01) {
        courante.push(" ");
      }
      courante.push(morceau);
    } else {
      lignes.push(normaliser(courante.join("")));
      courante = [morceau];
    }
    ordonnee = y; feuille = [page, bande]; abscisse = x;
  }
  if (courante.length) {
    lignes.push(courante.join("").replace(/\s+/g, " ").trim());
  }
  return lignes.filter((ligne) => ligne);
}

function trier(tous) {
  return tous
    .map((fragment, rang) => [fragment, rang])
    .sort(([a, rangA], [b, rangB]) => (
      a[0] - b[0] || a[1] - b[1] || b[2] - a[2] || a[3] - b[3] || rangA - rangB
    ))
    .map(([fragment]) => fragment);
}

/** Reconstitue les lignes visuelles du document, de haut en bas. */
export async function lignesPdf(octets, tolerance = 3.0) {
  return assembler(trier(await fragments(enChaine(octets))), tolerance);
}

/**
 * Les mêmes lignes, mais groupées par page. Savoir où une page commence et
 * finit est ce qui permet de rattacher un tableau à sa tête — et un relevé de
 * carrière recommence souvent son tableau, et son régime, à chaque feuille.
 */
export async function lignesParPage(octets, tolerance = 3.0) {
  const tous = trier(await fragments(enChaine(octets)));
  const pages = new Map();
  for (const fragment of tous) {
    if (!pages.has(fragment[0])) pages.set(fragment[0], []);
    pages.get(fragment[0]).push(fragment);
  }
  return [...pages.keys()].sort((a, b) => a - b)
    .map((page) => assembler(pages.get(page), tolerance));
}

export async function textePdf(octets) {
  return (await lignesPdf(octets)).join("\n");
}
