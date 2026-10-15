/**
 * Extraction de texte PDF avec mise en page, dans le navigateur et pour la
 * fabrique.
 *
 * LE SEUL LECTEUR PDF DU DÉPÔT (action 161, étape 4 ; note de décision 0003 :
 * ce qui tourne aux deux endroits s'écrit une fois, en JavaScript). Le site le
 * charge pour lire le relevé qu'un lecteur dépose ; la fabrique le fait tourner
 * par node, à travers ``scripts/fetch/lecture_pdf.py``, qui garde en Python ce
 * qu'elle seule utilise : la lecture par abscisse et les rectangles peints
 * d'une page. Il a été le portage de ce module Python, qui faisait foi, jusqu'à
 * ce que les deux, alignés cas par cas, lisent pareil les 36 documents que la
 * fabrique télécharge, et qu'il reste seul. Ses défauts corrigés
 * sont donc ceux du Python et les siens — les flux d'objets compressés, les
 * polices à encodage propre, l'échelle de la matrice de texte, le numéro de
 * flux dans la clé de regroupement, le repère de la page, les pages coupées en
 * plusieurs flux, le flux comprimé qui finit par un retour à la ligne, les
 * espaces de `str.strip` —, et `tests/test_lecture_pdf.py` les tient, par
 * node, sur des documents fabriqués à la main. « Le modèle de référence »,
 * dans ce qui suit, est ce lecteur Python, dont celui-ci garde la conduite.
 *
 * Le lecteur est né en Python, pour les barèmes de la CNBF, seule source des
 * valeurs du point des avocats, sans rien d'autre que la bibliothèque standard.
 * Deux difficultés, toutes deux rencontrées sur ces barèmes :
 *
 * 1. **Les colonnes.** L'étiquette et sa valeur ne se suivent pas dans l'ordre
 *    du flux : elles partagent une ligne à l'écran. On reconstitue donc la mise
 *    en page à partir des opérateurs de position (`Td`, `TD`, `Tm`).
 * 2. **Les polices à encodage propre.** Les nombres qui comptent — valeur de
 *    service, coût d'acquisition du point — sont écrits avec une police Type0
 *    « Identity-H », où chaque caractère est un numéro de glyphe et non une
 *    lettre. Sans la table `/ToUnicode` de la police, ils sortent en charabia,
 *    ou pas du tout. C'est exactement ce qui masquait les valeurs cherchées.
 *
 * Deux autres, rencontrées sur le jaune budgétaire des pensions (PLF 2026), qui
 * rendaient tout le document en lettres décalées — « 5DSSRUW » pour
 * « Rapport » :
 *
 * 3. **Les flux d'objets.** Un PDF 1.5 et plus range ses dictionnaires — pages,
 *    polices, ressources — dans des flux `/ObjStm` compressés, où `N 0 obj`
 *    n'apparaît plus. Un lecteur qui ne les déplie pas ne voit aucune police,
 *    donc aucune table, et lit tout en latin-1.
 * 4. **Les chaînes littérales à encodage propre.** Une police TrueType
 *    sous-ensemble numérote ses glyphes dans l'ordre d'apparition — `\001`
 *    pour le premier caractère écrit, `\002` pour le deuxième — et les pose en
 *    chaînes `(…)` à un octet par code, non en hexadécimal. La table
 *    `/ToUnicode` vaut pour elles aussi, avec la largeur de code que son
 *    `codespacerange` déclare : un octet ici, deux pour une police Type0.
 *
 * Deux dernières, rencontrées sur le relevé de carrière qu'info-retraite
 * délivre en 2026, dont chaque page sortait du bas vers le haut :
 *
 * 5. **Le repère de la page.** `cm` compose la matrice courante, que `q` sauve
 *    et `Q` rend : elle place tout ce que la page écrit. Ce relevé ouvre chaque
 *    page par « 0.05 0 0 -0.05 0 841.9 cm » — des vingtièmes de point,
 *    l'origine en haut de la feuille et l'axe vertical RETOURNÉ —, si bien que
 *    ses ordonnées croissent vers le bas. On range donc les fragments par leur
 *    position sur la feuille, la matrice de texte composée avec ce repère.
 * 6. **Une page en plusieurs flux.** Une page peut poser `/Contents` en
 *    tableau ; ses flux se lisent alors bout à bout, comme un seul, et un
 *    opérateur commencé dans l'un s'achève dans le suivant. Le même relevé coupe
 *    ainsi ses deux premières pages : le repère dans un flux, une `Tm` à la fin
 *    du deuxième, la chaîne qu'elle place au début du troisième.
 *
 * Et les tracés, que le jaune pensions du PLF 2027 a demandés : sa figure 3B
 * décompose les crédits de dix-sept ministères sans imprimer une valeur, mais
 * ses barres sont des rectangles peints, dont les longueurs sont les parts.
 * `aplats_de_page` les lit, en Python, dans le contenu de page que
 * `contenuDeLaPage` lui rend.
 *
 * Deux choix, et deux seulement, tiennent au navigateur :
 *
 * 1. **La décompression est asynchrone.** `zlib.decompress` n'a pas
 *    d'équivalent synchrone en JavaScript ; `DecompressionStream("deflate")`
 *    en tient lieu, et il rend une promesse. Les flux sont donc TOUS dépliés
 *    d'abord, en une passe, et le reste de la lecture se fait ensuite sans
 *    attendre : la structure du lecteur Python d'origine est conservée, seul
 *    son point d'entrée devient `async`.
 * 2. **Les octets sont portés par une chaîne latin-1**, un caractère par
 *    octet. C'est ce qui permet de reprendre mot pour mot les expressions
 *    régulières binaires du lecteur Python d'origine, que JavaScript ne sait pas
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
 * police WinAnsi pose sans les déclarer dans sa table, ou sans table du tout.
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

/**
 * Les cinq octets que cp1252 ne définit pas : le décodeur du modèle de
 * référence, `errors="replace"`, les rend « \ufffd ».
 */
const INDEFINIS_CP1252 = new Set([0x81, 0x8D, 0x8F, 0x90, 0x9D]);

/** La lettre que cp1252 donne à un octet : celle de latin-1, hors de 0x80 à 0x9F. */
function versCp1252(code) {
  return CP1252[code] ?? (INDEFINIS_CP1252.has(code) ? "\ufffd" : String.fromCharCode(code));
}

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
 * dans l'entrée, le flux s'est terminé et ce qui suit n'est que du bavardage ;
 * sinon, il est tronqué, et l'on ne rend rien. On la cherche dans TOUTE
 * l'entrée, depuis sa fin : zlib ignore autant d'octets qu'il en traîne, et la
 * chercher dans le dernier kilo-octet perdait le flux d'un producteur plus
 * bavard, que le Python lit. Un flux tronqué ne la porte que par hasard : une
 * chance sur quatre milliards par position.
 */

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
  for (let i = donnees.length - 4; i >= 0; i -= 1) {
    const lue = ((donnees.charCodeAt(i) & 0xff) * 0x1000000)
      + ((donnees.charCodeAt(i + 1) & 0xff) << 16)
      + ((donnees.charCodeAt(i + 2) & 0xff) << 8)
      + (donnees.charCodeAt(i + 3) & 0xff);
    if (lue >>> 0 === somme) return texte;
  }
  return null;
}

// -- objets et flux ---------------------------------------------------------
//
// Les espaces de la syntaxe PDF sont ceux de `\s` sur des octets en Python :
// l'espace, les tabulations, les fins de ligne et le saut de page. `\s` en
// JavaScript y ajoute l'insécable, l'octet \xa0, que la norme ne compte pas
// (ISO 32000-1, § 7.2.3) : les expressions régulières de la syntaxe disent
// donc leur classe, `[ \t\n\r\f\v]`, plutôt que `\s`.

const OBJET = /(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+obj\b([\s\S]*?)\bendobj/g;
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
    // LES DONNÉES COMPRIMÉES PEUVENT FINIR PAR UN RETOUR À LA LIGNE, et l'ôter
    // avec la fin de ligne qui précède « endstream » tronquait le flux : il ne
    // se dépliait plus, et sa page disparaissait sans bruit — ou sa police,
    // quand c'était sa table ToUnicode. Le dernier octet est celui de la somme
    // Adler-32, si bien qu'un flux sur cent trente environ finit ainsi ; le
    // lecteur de la fabrique perdait de la sorte cinq pages du jaune pensions
    // du PLF 2027. Le flux se relit donc tel quel quand le premier essai
    // échoue, ce qui suit sa fin écarté par `inflater` — pourvu qu'il finisse :
    // un flux tronqué ne rend pas une demi-page.
    const deplie = await inflater(donnees[1].replace(/^[\r\n]+|[\r\n]+$/g, ""))
      ?? await inflater(donnees[1].replace(/^[\r\n]+/, ""));
    if (deplie !== null) flux.set(numero, deplie);
  }));

  for (const [numero, objet] of [...objets]) {
    if (!objet.includes("/ObjStm")) continue;
    const contenu = flux.get(numero);
    const nombre = /\/N[ \t\n\r\f\v]+(\d+)/.exec(objet);
    const premier = /\/First[ \t\n\r\f\v]+(\d+)/.exec(objet);
    if (!contenu || !nombre || !premier) continue;
    const debut = Number(premier[1]);
    const tete = contenu.slice(0, debut).split(/[ \t\n\r\f\v]+/).filter(Boolean).map(Number);
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

/**
 * Une destination de table ToUnicode : de l'hexadécimal en UTF-16 gros-boutiste,
 * lu comme le décodeur `utf-16-be` du modèle de référence, `errors="replace"`.
 * Un chiffre impair se complète d'un zéro, comme toute chaîne hexadécimale de la
 * norme (ISO 32000-1, § 7.3.4.3) ; ce qui n'est pas de l'UTF-16 — l'octet de
 * reste, un surrogat sans sa moitié — rend « \ufffd ». Chaque unité se
 * complétait d'abord de zéros à droite : « <41> » donnait « 䄀 ».
 */
function deHexa(hexa) {
  const chiffres = hexa.length % 2 ? `${hexa}0` : hexa;
  const reste = chiffres.length % 4 !== 0;
  const unites = [];
  for (let i = 0; i + 4 <= chiffres.length; i += 4) unites.push(parseInt(chiffres.slice(i, i + 4), 16));
  let texte = "";
  for (let k = 0; k < unites.length; k += 1) {
    const unite = unites[k];
    const suivante = unites[k + 1];
    if (unite >= 0xD800 && unite <= 0xDBFF && suivante >= 0xDC00 && suivante <= 0xDFFF) {
      texte += String.fromCharCode(unite, suivante);
      k += 1;
    } else if (unite >= 0xD800 && unite <= 0xDBFF && k === unites.length - 1 && reste) {
      // Un surrogat haut que l'octet de reste ne complète pas : une seule
      // marque pour les deux, comme le décodeur du Python.
    } else if (unite >= 0xD800 && unite <= 0xDFFF) {
      texte += "\ufffd";
    } else {
      texte += String.fromCharCode(unite);
    }
  }
  return reste ? `${texte}\ufffd` : texte;
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
 * les crochets et lisait À CHEVAL sur les entrées : la première destination du
 * tableau devenait la destination de toute la plage, les deux suivantes se
 * recollaient à l'entrée d'après, et de proche en proche TOUTE la table se
 * décalait. Le document sortait en lettres fausses — et ses
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
    for (const paire of bloc.match(/<([0-9A-Fa-f]+)>[ \t\n\r\f\v]*<([0-9A-Fa-f]+)>/g) ?? []) {
      largeurs.push(Math.floor(/<([0-9A-Fa-f]+)>/.exec(paire)[1].length / 2));
    }
  }
  if (largeurs.length) table.largeur = Math.max(...largeurs);

  for (const bloc of contenu.match(/beginbfchar[\s\S]*?endbfchar/g) ?? []) {
    const paires = /<([0-9A-Fa-f]+)>[ \t\n\r\f\v]*<([0-9A-Fa-f]+)>/g;
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
  const trouve = new RegExp(`${cle}[ \\t\\n\\r\\f\\v]*(?:(\\d+)[ \\t\\n\\r\\f\\v]+0[ \\t\\n\\r\\f\\v]+R|<<)`).exec(objet);
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
  const trouve = /\/ToUnicode[ \t\n\r\f\v]+(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R/.exec(police);
  const contenu = trouve ? flux.get(Number(trouve[1])) : null;
  const simple = !/\/Subtype[ \t\n\r\f\v]*\/Type0\b/.test(police);
  // SANS TABLE, UNE POLICE SIMPLE WINANSI SE LIT EN CP1252, qui est son
  // encodage : elle reçoit une table sans entrée, qui ne garde que ce repli.
  // Lue en latin-1, comme toute chaîne sans table, elle rendait « ’ » par le
  // caractère de contrôle 0x92, « … » par 0x85, que le modèle de référence
  // tient pour une espace, et « € » par 0x80 : sur les 36 documents que la
  // fabrique télécharge, 443 polices WinAnsi n'ont pas de table, et leurs
  // chaînes portaient 9 719 de ces octets, dont 6 888 apostrophes et 2 131
  // euros.
  if (!contenu) {
    if (!simple || !police.includes("WinAnsiEncoding")) return null;
    const table = new Table();
    table.largeur = 1;
    table.repli = "cp1252";
    return table;
  }
  const table = cmap(contenu);
  // Une police simple — TrueType, Type1, Type3 — code ses glyphes sur UN
  // octet, quoi que déclare le codespacerange de sa table : InDesign y écrit
  // <0000> <FFFF> avec des entrées <64>, et lire par deux rendait le rapport
  // de l'OPEF en lettres perdues. Seule une police Type0 lit par deux.
  if (simple) {
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
 * et c'est ce qui rendait le jaune budgétaire en lettres décalées. On lit donc,
 * page par page, ``/Resources`` puis ``/Font``, et l'on rattache la table au
 * numéro du flux ``/Contents``.
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
    const references = /\/(\w+)[ \t\n\r\f\v]+(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R/g;
    for (let t = references.exec(polices); t; t = references.exec(polices)) {
      const table = tableDe(objets.get(Number(t[2])) ?? "", objets, flux);
      // Une table vide n'en est pas une : le Python, pour qui elle est fausse,
      // ne la rangeait pas, et la police se lit alors comme sans table — par
      // son encodage, s'il est WinAnsi (`tableDe`).
      if (table && (table.size || table.repli)) tables.set(t[1], table);
    }
    if (!page) { parContenu.set(numeroObjet, tables); continue; }
    const contenus = fluxDesContenus(objet, objets);
    if (!contenus) continue;
    for (const numero of contenus.numeros) parContenu.set(numero, tables);
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
    const references = /\/(\w+)[ \t\n\r\f\v]+(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R/g;
    for (let t = references.exec(objet); t; t = references.exec(objet)) {
      const police = objets.get(Number(t[2]));
      if (!police || !police.includes("/Font")) continue;
      const vers = /\/ToUnicode[ \t\n\r\f\v]+(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R/.exec(police);
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
  if (!table || (!table.size && !table.repli)) return texte;
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
      sortie += versCp1252(code);
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
    if (table && table.size) sortie += table.get(code) ?? "";
    // Une police WinAnsi sans table lit aussi son hexadécimal par un octet, en
    // cp1252 : lu par deux, « <E9> » devenait le code 0xE900, hors de portée,
    // et l'« é » se perdait. Les codes de contrôle restent écartés, si bien
    // qu'un numéro de glyphe écrit sur deux octets, « <0048> », rend la même
    // lettre qu'avant.
    else if (code >= 32 && code < 0x3000) {
      sortie += table && table.repli === "cp1252" ? versCp1252(code) : String.fromCharCode(code);
    }
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
  // ouvre un ``BT`` par ligne — ReportLab, et les relevés de carrière que le
  // site reçoit — voyait ses ordonnées s'ADDITIONNER d'un bloc au suivant : la
  // page partait vers le haut à chaque ligne, et le document sortait à
  // l'envers, une ligne par fragment.
  "(?<bt>\\bBT\\b)",
  "(?<tm>[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+Tm)",
  // Le repère de la page : ``cm`` le compose, ``q`` le sauve, ``Q`` le rend.
  "(?<cm>[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+cm)",
  "(?<sauve>\\bq\\b)",
  "(?<rend>\\bQ\\b)",
  "(?<td>[-\\d.]+[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+T[dD])",
  "(?<tl>[-\\d.]+[ \\t\\n\\r\\f\\v]+TL)",
  "(?<etoile>T\\*)",
  "(?<retour>[)\\]][ \\t\\n\\r\\f\\v]*['\"])",
  // Le nom de la police est un groupe NOMMÉ. Le Python le prenait d'abord par un
  // rang écrit en dur — 9 —, qui désignait un autre groupe : le nom restait
  // vide, aucune table ToUnicode ne s'appliquait aux chaînes, et le charabia
  // « 5DSSRUW » venait de là autant que du reste.
  "(?<tf>/(?<nomPolice>\\w+)[ \\t\\n\\r\\f\\v]+[-\\d.]+[ \\t\\n\\r\\f\\v]+Tf)",
  // Un dictionnaire en ligne — les propriétés d'un contenu balisé, « /Span
  // <</Lang (en-US)>> BDC » — porte des chaînes qui ne sont pas du texte : on
  // le saute d'un bloc, sinon « en-US » s'imprime entre chaque cellule.
  "(?<dict><<[\\s\\S]*?>>)",
  "(?<hex><[0-9A-Fa-f \\t\\n\\r\\f\\v]+>)",
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
 * producteurs émettent : un nombre qu'on lisait sans le vérifier levait, et
 * TOUT le rapport devenait illisible — c'est ce qui fermait celui de 1995 à la
 * CCSS, vingt méga-octets pourtant lisibles par ailleurs. On ne devine jamais la valeur manquante — la mettre à
 * zéro déplacerait le texte sans prévenir : c'est à l'appelant de vérifier
 * qu'il en a assez, et de SAUTER l'opérateur sinon.
 */
function reels(operandes) {
  const valeurs = [];
  for (const jeton of operandes.split(/[ \t\n\r\f\v]+/).filter(Boolean)) {
    if (!/^[-+]?(\d+\.?\d*|\.\d+)$/.test(jeton)) break;
    valeurs.push(Number(jeton));
  }
  return valeurs;
}

/**
 * Une matrice de la norme, « a b c d e f » : le point (x, y) qu'elle transforme
 * devient (a x + c y + e, b x + d y + f).
 */
const IDENTITE = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0];

/** La matrice qui applique ``m``, puis ``n`` : la norme écrit m × n. */
function composer(m, n) {
  const [a, b, c, d, e, f] = m;
  const [a2, b2, c2, d2, e2, f2] = n;
  return [a * a2 + b * c2, a * b2 + b * d2,
    c * a2 + d * c2, c * b2 + d * d2,
    e * a2 + f * c2 + e2, e * b2 + f * d2 + f2];
}

/**
 * ``tx ty Td`` : l'origine avance de (tx, ty) dans le repère du texte. C'est ce
 * repère qui porte l'échelle — « 9 0 0 9 82.97 723.62 Tm » place le curseur ET
 * multiplie par neuf tout ce qui suit — et, pour un texte tourné, la direction :
 * un `Td` y avance le long des glyphes, non le long des axes de la page.
 */
function decaler(matrice, tx, ty) {
  const [a, b, c, d, e, f] = matrice;
  return [a, b, c, d, tx * a + ty * c + e, tx * b + ty * d + f];
}

/**
 * La bande, la ligne et la colonne d'un fragment, en points de la feuille. Un
 * texte droit se range par ordonnée, puis par abscisse ; un texte tourné se lit
 * le long de son propre axe. Les normes se calculent par une racine, et non par
 * `Math.hypot`, que Python et JavaScript n'arrondissent pas toujours de même.
 */
function position(matrice, repere) {
  const [a, b, c, d, e, f] = composer(matrice, repere);
  if (!(b || c)) return [0, f, e];
  const longueur = Math.sqrt(a * a + b * b) || 1.0;
  const hauteur = Math.sqrt(c * c + d * d) || 1.0;
  return [1, (e * c + f * d) / hauteur, (e * a + f * b) / longueur];
}

/**
 * Pour chaque flux d'une page qui en pose plusieurs, tous ceux de la page :
 * ``/Contents [15 0 R 21 0 R]`` se lit bout à bout, comme un seul flux, et la
 * norme permet de couper un opérateur entre deux. Lus chacun pour soi, le repère
 * posé dans le premier ne valait plus pour les suivants, et la première chaîne
 * de chaque flux tombait à l'origine de la page, sa `Tm` restée dans le flux
 * d'avant.
 */
function contenusDesPages(objets) {
  const pages = new Map();
  for (const objet of objets.values()) {
    const contenus = fluxDesContenus(objet, objets);
    if (!contenus || !contenus.tableau) continue;
    for (const numero of contenus.numeros) if (!pages.has(numero)) pages.set(numero, contenus.numeros);
  }
  return pages;
}

/**
 * Les flux qui portent du texte selon la norme : ceux que les pages désignent
 * par `/Contents`, et les formulaires (`/Subtype /Form`), qu'une page pose par
 * `Do`. `null` quand rien ne désigne de flux — un PDF fabriqué à la main, ou
 * dont les pages ne se lisent pas : le document se lit alors comme avant.
 *
 * LE LECTEUR LISAIT TOUT FLUX OÙ PARAISSAIT « Tj », les images seules
 * écartées. Le programme d'une police embarquée en contient par hasard : sur
 * les 36 documents que la fabrique télécharge, 167 de ces programmes, dans 30
 * documents, se lisaient chacun en une ligne de charabia, comme quatre
 * métadonnées XMP, deux tables des références, deux flux d'indications de la
 * linéarisation, un profil de couleur et une palette. Deux pieds de page
 * qu'aucune page ne pose, enfin, rendaient avec les polices d'autres pages un
 * double mutilé de la liste des membres d'un rapport à la CCSS, en 81 lignes.
 */
function fluxDeTexte(objets, flux) {
  const porteurs = new Set();
  for (const objet of objets.values()) {
    const contenus = fluxDesContenus(objet, objets);
    if (contenus) for (const numero of contenus.numeros) if (flux.has(numero)) porteurs.add(numero);
  }
  if (!porteurs.size) return null;
  for (const [numero, objet] of objets) {
    if (/\/Subtype[ \t\n\r\f\v]*\/Form\b/.test(dictionnaireDuFlux(objet))) porteurs.add(numero);
  }
  return porteurs;
}

/** Le dictionnaire d'un flux, sans ses données ; rien pour un objet sans flux. */
function dictionnaireDuFlux(objet) {
  return objet.slice(0, Math.max(objet.indexOf("stream"), 0));
}

/**
 * Une image se reconnaît à son `/Subtype /Image`.
 *
 * L'ÉCART DES IMAGES CHERCHAIT LA CHAÎNE « /Image » DANS LE DICTIONNAIRE DU
 * FLUX, et l'y trouvait aussi dans les ressources d'un formulaire qui nomme
 * une image, « /Image869 » ou « /ImageC » : sur les 36 documents que la
 * fabrique télécharge, 382 formulaires qui portent du texte — des graphiques,
 * des tableaux collés depuis Excel — ne se lisaient pas, et les rapports à la
 * CCSS y perdaient des tableaux entiers.
 */
function estUneImage(objet) {
  return /\/Subtype[ \t\n\r\f\v]*\/Image\b/.test(dictionnaireDuFlux(objet));
}

/**
 * Les flux de contenu qu'un objet désigne par `/Contents`, et s'ils forment un
 * tableau, qui se lit bout à bout ; `null` s'il n'en désigne aucun. La norme
 * permet trois formes : un flux, un tableau de flux, ou un objet qui n'est
 * qu'un tableau de flux. Le jaune pensions du PLF 2027 range ainsi le tableau
 * de chacune de ses 250 pages : lu comme un flux, ce tableau ne rattachait les
 * polices de la page à aucun de ses flux, qui prenaient celles du document,
 * la dernière de chaque nom, et ses flux se lisaient chacun pour soi.
 */
function fluxDesContenus(objet, objets) {
  const contenus = /\/Contents[ \t\n\r\f\v]*(?:(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R|\[([^\]]*)\])/.exec(objet);
  if (!contenus) return null;
  let tableau = contenus[2];
  if (tableau === undefined) {
    const cible = /^[ \t\n\r\f\v]*\[([^\]]*)\]/.exec(objets.get(Number(contenus[1])) ?? "");
    if (!cible) return { numeros: [Number(contenus[1])], tableau: false };
    tableau = cible[1];
  }
  return { numeros: [...tableau.matchAll(/(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R/g)].map((r) => Number(r[1])), tableau: true };
}

/**
 * Reconstitue les fragments du document, avec leur page et leur position.
 *
 * LE NUMÉRO DE FLUX FAIT PARTIE DE LA CLÉ, et c'est tout sauf un détail.
 * Chaque page d'un PDF a son propre repère : l'ordonnée 700 y désigne le même
 * endroit de la feuille, page 1 comme page 60. Regrouper les fragments sur la
 * seule ordonnée collait bout à bout la ligne du haut de CHAQUE page — un titre
 * de la page 1 suivi d'un chiffre de la page 40 et d'une note de la page 97,
 * dans une même chaîne. Sur un document d'une page le défaut ne se voit pas.
 * Sur la chronologie de la CARMF, cent pages de tableaux, il rendait huit
 * lignes pour cent quatre-vingt mille caractères, et l'on en concluait que la
 * mise en page « ne se reconstituait pas ». Elle se reconstitue très bien :
 * c'est le lecteur qui empilait les pages.
 */
async function fragments(octets) {
  return fragmentsDesObjets(await lireObjets(octets));
}

/** Les fragments d'un document dont les objets sont lus (`fragments`). */
function fragmentsDesObjets({ objets, flux }) {
  const communes = polices(objets, flux);
  const parContenu = policesParContenu(objets, flux);
  const pages = contenusDesPages(objets);
  const porteurs = fluxDeTexte(objets, flux);
  const lus = new Set();
  const tous = [];
  let page = -1;
  for (const [numero, objet] of objets) {
    page += 1;
    // Seuls les flux qui portent du texte se lisent (`fluxDeTexte`) : le
    // programme d'une police contient « Tj » par hasard, une image JPEG une
    // fois sur dix. Un document qui ne désigne aucun contenu se lit comme
    // avant, ses images seules écartées.
    if (lus.has(numero)) continue;
    if (porteurs ? !porteurs.has(numero) : estUneImage(objet)) continue;
    // Les flux d'une même page se lisent ensemble, à la place du premier qu'on
    // rencontre, et dans l'ordre de la page.
    const fluxDePage = pages.get(numero) ?? [numero];
    for (const n of fluxDePage) lus.add(n);
    const contenu = fluxDePage.map((n) => flux.get(n)).filter(Boolean).join("\n");
    if (!contenu || (!contenu.includes("Tj") && !contenu.includes("TJ"))) continue;
    const tables = parContenu.get(numero) ?? communes;
    // ÉCHELLE DE LA MATRICE DE TEXTE. `Tm` ne pose pas seulement une position,
    // il pose un repère : « 9 0 0 9 82.97 723.62 Tm » place le curseur ET
    // multiplie par neuf tout ce qui suit. Les décalages `Td` qui viennent
    // ensuite sont exprimés dans CE repère, pas en points de la page. Les
    // additionner tels quels écrasait les interlignes d'un facteur neuf, et
    // fondait en une seule des lignes distantes de quatorze points : c'est ce qui
    // rendait illisibles les tableaux de la chronologie de la CARMF, trente-six
    // lignes ramenées à quatre. La matrice de ligne se garde donc entière, et
    // chaque `Td` s'y applique.
    let matrice = IDENTITE;
    // LE REPÈRE DE LA PAGE, que `cm` compose et que `q` et `Q` sauvent et
    // rendent. Le relevé de carrière d'info-retraite retourne l'axe vertical et
    // redresse ses glyphes par « 1 0 0 -1 x y Tm » : sans ce repère, chaque page
    // se rangeait du pied de page au titre, et une ligne de carrière héritait
    // du régime du bloc du dessous au lieu du sien.
    let repere = IDENTITE;
    const sauves = [];
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
    // tourné — entre donc dans la clé de regroupement (`position`).
    JETONS.lastIndex = 0;
    for (let jeton = JETONS.exec(contenu); jeton; jeton = JETONS.exec(contenu)) {
      const g = jeton.groups;
      if (g.dict) continue;
      if (g.ouvre || g.ferme) { dansTableau = Boolean(g.ouvre); continue; }
      if (g.nombre) {
        if (dansTableau && Number(g.nombre) < ESPACE_DE_TABLEAU) {
          tous.push([page, ...position(matrice, repere), " "]);
        }
        continue;
      }
      if (g.bt) {
        matrice = IDENTITE;
      } else if (g.tm) {
        const nombres = reels(g.tm);
        if (nombres.length < 6) continue;
        matrice = nombres.slice(0, 6);
      } else if (g.cm) {
        const nombres = reels(g.cm);
        if (nombres.length < 6) continue;
        repere = composer(nombres.slice(0, 6), repere);
      } else if (g.sauve) {
        // LA POLICE ET L'INTERLIGNE SONT DE L'ÉTAT GRAPHIQUE, comme le repère :
        // `q` les sauve, `Q` les rend. Excel pose chaque cellule d'un tableau
        // entre `q` et `Q`, et la police d'une seule — une Type0 — avant des
        // cellules qui n'en reposent aucune : garder la dernière posée
        // traduisait leurs octets par la table de celle-là. Les rapports à la
        // CCSS de 2022 à 2025 y perdaient la ligne de la CNAV, « Prises en
        // charge de cotisations par le FSV » devenue « POises en cMaOge… », et
        // avec elle 14,6 des 15,0 Md€ de cotisations que le fonds prenait en
        // charge en 2021.
        sauves.push([repere, police, interligne]);
      } else if (g.rend) {
        // Un `Q` sans `q` ne rend rien : on garde l'état courant.
        if (sauves.length) [repere, police, interligne] = sauves.pop();
      } else if (g.td) {
        const nombres = reels(g.td);
        if (nombres.length < 2) continue;
        matrice = decaler(matrice, nombres[0], nombres[1]);
        if (g.td.trimEnd().endsWith("TD")) interligne = -nombres[1];
      } else if (g.tl) {
        const nombres = reels(g.tl);
        if (!nombres.length) continue;
        interligne = nombres[0];
      } else if (g.etoile || g.retour) {
        matrice = decaler(matrice, 0.0, -interligne);
      } else if (g.tf) {
        police = g.nomPolice;
      } else {
        const morceau = g.hex
          ? hexa(g.hex, tables.get(police))
          : litteral(g.txt.slice(1, -1), tables.get(police));
        const [bande, ligne, colonne] = position(matrice, repere);
        if (ebarber(morceau)) tous.push([page, bande, ligne, colonne, morceau]);
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
 * Les espaces du modèle de référence : ce que `str.strip` ôte et ce que `\s`
 * reconnaît dans une chaîne Python. Ce sont ceux de JavaScript, moins U+FEFF,
 * plus les séparateurs \x1c à \x1f et \x85, que `trim` et `\s` ignorent — et
 * les documents en étaient pleins : une police WinAnsi sans table ToUnicode
 * écrivait « … » par l'octet \x85, et le programme d'une police lu comme du
 * texte semait les séparateurs, jusqu'à ce que l'une se lise en cp1252 et que
 * l'autre ne se lise plus. Avec `trim`, le portage gardait ces caractères là
 * où le Python les tient pour des espaces, et 33 documents de la fabrique sur
 * 36 sortaient autrement, à 119 chaînes près.
 */
const ESPACES = "\\t-\\r\\x1c-\\x20\\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000";
const BORDS = new RegExp(`^[${ESPACES}]+|[${ESPACES}]+$`, "g");

/** `str.strip()` : le texte sans les espaces du modèle de référence à ses bouts. */
function ebarber(texte) {
  return texte.replace(BORDS, "");
}

/**
 * Une espace pour toute suite d'espaces ordinaires ; UNE ESPACE INSÉCABLE pour
 * toute suite d'insécables (U+00A0, U+202F), et elle reste insécable. Un
 * document qui sépare ses milliers d'une fine insécable et ses cellules d'une
 * espace de position ne se découpe en nombres que si les deux restent
 * différentes.
 */
function normaliser(texte) {
  return ebarber(texte.replace(/[  ]+/g, " ")
    .replace(/[ \t\r\n\f\v]+/g, " "));
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
      // rendait « Prise en charge de cotisations » comme
      // « Priseenchargedecotisations », et surtout « 4 929 5 002 » comme
      // « 49295002 » — un nombre qui n'existe
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
    // LA DERNIÈRE LIGNE SE NORMALISE COMME LES AUTRES. Le modèle de référence
    // la rendait par `re.sub(r"\s+", " ", …).strip()`, qui fond aussi les
    // insécables en espaces : la dernière ligne d'un document, et celle de
    // chaque page, perdait la différence entre les milliers d'un nombre et les
    // cellules d'un tableau, et « 1 339 945 1 654 » ne s'y découpait plus.
    lignes.push(normaliser(courante.join("")));
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
 * Les fragments du document, page par page, de haut en bas : chacun
 * `[page, bande, ligne, colonne, texte]`. La fabrique en refait les lignes de
 * gauche à droite, cellule par cellule (`scripts/fetch/lecture_pdf.py`).
 */
export async function fragmentsParPage(octets) {
  return parPage(trier(await fragments(enChaine(octets)))).map(([, page]) => page);
}

/** Les fragments triés, groupés par page — le rang de leur flux —, dans l'ordre des rangs. */
function parPage(tous) {
  const pages = new Map();
  for (const fragment of tous) {
    if (!pages.has(fragment[0])) pages.set(fragment[0], []);
    pages.get(fragment[0]).push(fragment);
  }
  return [...pages.entries()].sort(([a], [b]) => a - b);
}

/**
 * Les mêmes lignes, mais groupées par page. Savoir où une page commence et
 * finit est ce qui permet de rattacher un tableau à sa tête — et un relevé de
 * carrière recommence souvent son tableau, et son régime, à chaque feuille.
 */
export async function lignesParPage(octets, tolerance = 3.0) {
  return (await fragmentsParPage(octets)).map((page) => assembler(page, tolerance));
}

/**
 * Les lignes de chaque page, comme `lignesParPage`, et les formulaires que
 * chacune pose : pour la i-ième page, les rangs, dans la même liste, des pages
 * qui sont ses formulaires, dans l'ordre où son contenu les pose par `Do`,
 * ceux qu'ils posent à leur tour compris.
 *
 * UN FORMULAIRE SE LIT À PART, comme une page à lui, que la liste range au
 * rang de son objet dans le fichier : ce rang ne dit rien de la page qui le
 * pose. Les rapports à la CCSS collent leurs tableaux depuis Excel, en
 * formulaires ; celui de 2018 range ceux d'une fiche juste après sa page,
 * celui de 2023 juste avant, si bien qu'à les chercher au voisinage de leur
 * titre, une fiche lisait les tableaux de sa voisine. La page, elle, les
 * nomme dans ses ressources.
 */
export async function pagesEtFormulaires(octets, tolerance = 3.0) {
  const lus = await lireObjets(enChaine(octets));
  const pages = parPage(trier(fragmentsDesObjets(lus)));
  const index = new Map(pages.map(([rang], i) => [rang, i]));
  const rangs = new Map([...lus.objets.keys()].map((numero, rang) => [numero, rang]));
  const formulaires = pages.map(() => []);
  for (const objet of lus.objets.values()) {
    const contenus = fluxDesContenus(objet, lus.objets);
    if (!contenus) continue;
    // Le texte d'une page se lit au rang du premier de ses flux.
    const i = index.get(Math.min(...contenus.numeros.map((n) => rangs.get(n) ?? Infinity)));
    if (i === undefined) continue;
    const contenu = contenus.numeros.map((n) => lus.flux.get(n) ?? "").join("\n");
    for (const numero of formulairesPoses(contenu, lus, ressourcesDe(objet, lus.objets), new Set())) {
      const j = index.get(rangs.get(numero));
      if (j !== undefined && !formulaires[i].includes(j)) formulaires[i].push(j);
    }
  }
  return { pages: pages.map(([, page]) => assembler(page, tolerance)), formulaires };
}

/** Les ressources d'une page : les siennes, ou celles qu'elle hérite de l'arbre des pages. */
function ressourcesDe(objet, objets) {
  for (let o = objet, n = 0; o && n < 32; n += 1) {
    const ressources = dictionnaire(o, "/Resources", objets);
    if (ressources) return ressources;
    const parent = /\/Parent[ \t\n\r\f\v]+(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R/.exec(o);
    o = parent ? objets.get(Number(parent[1])) : null;
  }
  return "";
}

/**
 * Les formulaires qu'un contenu pose par `Do`, dans son ordre, chacun suivi de
 * ceux qu'il pose à son tour ; un formulaire sans ressources à lui prend celles
 * de qui le pose.
 */
function formulairesPoses(contenu, lus, ressources, vus) {
  const noms = new Map([...dictionnaire(ressources, "/XObject", lus.objets)
    .matchAll(/\/([^ \t\n\r\f\v/<>[\]()]+)[ \t\n\r\f\v]+(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R/g)]
    .map((t) => [t[1], Number(t[2])]));
  const poses = [];
  for (const appel of contenu.matchAll(/\/([^ \t\n\r\f\v/<>[\]()]+)[ \t\n\r\f\v]*Do\b/g)) {
    const numero = noms.get(appel[1]);
    const forme = numero === undefined ? "" : lus.objets.get(numero) ?? "";
    if (vus.has(numero) || !/\/Subtype[ \t\n\r\f\v]*\/Form\b/.test(dictionnaireDuFlux(forme))) continue;
    vus.add(numero);
    const siennes = dictionnaire(dictionnaireDuFlux(forme), "/Resources", lus.objets);
    poses.push(numero, ...formulairesPoses(lus.flux.get(numero) ?? "", lus, siennes || ressources, vus));
  }
  return poses;
}

// -- les pages de l'arbre ------------------------------------------------------

/**
 * Les objets page du document, dans l'ordre de ses pages.
 *
 * LE RANG D'UN FLUX N'EST PAS CELUI DE SA PAGE. Les lectures de texte
 * numérotent les flux dans l'ordre du fichier : le jaune pensions du PLF 2027
 * en compte 265 pour 250 pages, et sa page 24 y est la 23e. Une page désignée
 * par son numéro se trouve donc en suivant l'arbre des pages depuis le
 * catalogue, `/Kids` après `/Kids`.
 */
function pagesDeLArbre(objets) {
  const catalogue = [...objets.values()].find((objet) => /\/Type[ \t\n\r\f\v]*\/Catalog\b/.test(objet));
  const racine = catalogue && /\/Pages[ \t\n\r\f\v]+(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R/.exec(catalogue);
  if (!racine) throw introuvable("le document n'a pas d'arbre des pages");
  const pages = [];
  const aVoir = [Number(racine[1])];
  const vus = new Set();
  while (aVoir.length) {
    const numero = aVoir.pop();
    if (vus.has(numero)) continue;
    vus.add(numero);
    const enfants = /\/Kids[ \t\n\r\f\v]*\[([^\]]*)\]/.exec(objets.get(numero) ?? "");
    if (enfants) {
      // Le dernier empilé sort le premier : les enfants s'empilent à rebours
      // pour se lire dans leur ordre.
      aVoir.push(...[...enfants[1].matchAll(/(\d+)[ \t\n\r\f\v]+0[ \t\n\r\f\v]+R/g)]
        .map((t) => Number(t[1])).reverse());
    } else {
      pages.push(numero);
    }
  }
  return pages;
}

/**
 * Les flux d'une page, bout à bout. `/Contents` désigne un flux, un tableau de
 * flux, ou — le jaune pensions du PLF 2027 — un objet qui n'est qu'un tableau
 * de flux : sa page 24 en pose trois, dont le premier ramène toute la feuille
 * à 99,88 % de sa taille. Un objet page absent n'a rien à dire.
 */
function contenuDeLObjetPage(objets, flux, numero) {
  const contenus = fluxDesContenus(objets.get(numero) ?? "", objets);
  if (!contenus) return "";
  return contenus.numeros.map((n) => flux.get(n)).filter(Boolean).join("\n");
}

/** Une erreur que la fabrique lit comme le `LookupError` du Python. */
function introuvable(message) {
  const erreur = new Error(message);
  erreur.name = "LookupError";
  return erreur;
}

/**
 * Le contenu de la page `page` du document, comptée à partir de 1 dans l'ordre
 * de son arbre des pages : ses flux dépliés, bout à bout, un caractère par
 * octet. La fabrique y lit les rectangles peints d'une figure
 * (`aplats_de_page`).
 */
export async function contenuDeLaPage(octets, page) {
  const { objets, flux } = await lireObjets(enChaine(octets));
  const pages = pagesDeLArbre(objets);
  if (!(page >= 1 && page <= pages.length)) {
    throw introuvable(`le document n'a pas de page ${page} (${pages.length} pages)`);
  }
  return contenuDeLObjetPage(objets, flux, pages[page - 1]);
}

export async function textePdf(octets) {
  return (await lignesPdf(octets)).join("\n");
}
