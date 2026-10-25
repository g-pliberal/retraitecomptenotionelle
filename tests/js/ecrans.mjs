/**
 * Le site vu par un vrai navigateur, à plusieurs largeurs d'écran.
 *
 *     node tests/js/ecrans.mjs <navigateur> <plan.json>   ->  JSON sur stdout
 *
 * Les témoins de pages disent ce que le site ÉCRIT ; ils ne disent rien de ce
 * qu'un écran en MONTRE : qu'un tableau déborde de 300 points, qu'un tracé se
 * réduise à des textes de six pixels, qu'une légende tombe deux écrans sous sa
 * courbe. Seul un moteur de rendu le sait. Ce pilote en lance un — Chromium,
 * sans fenêtre —, lui parle par le protocole des outils de développement, sur
 * le WebSocket que node porte en propre (aucune bibliothèque : le dépôt n'en a
 * pas, et n'en prendra pas pour ses tests), puis visite chaque page du plan à
 * chaque largeur, dépliants fermés puis ouverts, et rend ce qu'il a mesuré.
 * C'est `tests/test_ecrans.py` qui juge.
 *
 * Le plan :
 *
 *     {"adresse": "http://127.0.0.1:8000/index.html",
 *      "ecrans": [{"largeur": 390, "hauteur": 800}, ...],
 *      "routes": ["/", "/cout", "/simuler?naissance=…", ...],
 *      "retrecir": {"depuis": 1440, "vers": {"largeur": 1024, "hauteur": 768}}}
 *
 * `retrecir` rétrécit la fenêtre, sans changer d'adresse, sur une page qui
 * pose des schémas de front, et dit ce qu'elle a redessiné.
 *
 * Le paquet de données n'est chargé qu'une fois : on change de page par
 * l'ancre, comme le lecteur, et de largeur par l'émulation de l'écran.
 */

import { readFileSync } from "node:fs";

import { ouvrirLeNavigateur } from "./navigateur.mjs";

const [navigateur, cheminPlan] = process.argv.slice(2);
const plan = JSON.parse(readFileSync(cheminPlan, "utf-8"));

/** Le délai au-delà duquel une page qui ne se rend pas fait échouer la visite. */
const DELAI_RENDU = 30000;

// -- le navigateur -----------------------------------------------------------

// Une minute pour ouvrir son protocole, et un second lancement s'il s'est tu :
// à froid, sur GitHub, trente secondes n'y suffisaient pas (`navigateur.mjs`).
const { adresse: adresseDuProtocole, fermer } = await ouvrirLeNavigateur(navigateur);

// -- le protocole ------------------------------------------------------------

const ws = new WebSocket(adresseDuProtocole);
await new Promise((resoudre, rejeter) => {
  ws.onopen = resoudre;
  ws.onerror = () => rejeter(new Error("le WebSocket du navigateur ne s'ouvre pas"));
});
let numero = 0;
const enAttente = new Map();
const erreursDeLaPage = [];
ws.onmessage = (message) => {
  const recu = JSON.parse(message.data);
  if (recu.id && enAttente.has(recu.id)) {
    const { resoudre, rejeter } = enAttente.get(recu.id);
    enAttente.delete(recu.id);
    if (recu.error) { rejeter(new Error(`${recu.error.message} ${recu.error.data || ""}`)); }
    else { resoudre(recu.result); }
  } else if (recu.method === "Runtime.exceptionThrown") {
    erreursDeLaPage.push(recu.params.exceptionDetails?.exception?.description
      || recu.params.exceptionDetails?.text || "exception");
  }
};

function envoyer(methode, parametres = {}, session = undefined) {
  return new Promise((resoudre, rejeter) => {
    numero += 1;
    enAttente.set(numero, { resoudre, rejeter });
    ws.send(JSON.stringify({ id: numero, method: methode, params: parametres, sessionId: session }));
  });
}

// « Partager » enregistre l'image qu'il compose : le pilote la regarde se
// dessiner, et le navigateur n'écrit rien sur le disque.
await envoyer("Browser.setDownloadBehavior", { behavior: "deny" });
const { targetId } = await envoyer("Target.createTarget", { url: "about:blank" });
const { sessionId } = await envoyer("Target.attachToTarget", { targetId, flatten: true });
const page = (methode, parametres) => envoyer(methode, parametres, sessionId);
await page("Page.enable");
await page("Runtime.enable");

/** Évalue une expression dans la page et rend sa valeur, promesse attendue. */
async function evaluer(expression) {
  const { result, exceptionDetails } = await page("Runtime.evaluate", {
    expression, returnByValue: true, awaitPromise: true,
  });
  if (exceptionDetails) {
    throw new Error(exceptionDetails.exception?.description || exceptionDetails.text);
  }
  return result.value;
}

/**
 * Attend que la page ait fini de se rendre. Un marqueur posé dans `#contenu`
 * avant de changer d'adresse disparaît quand le rendu remplace le contenu ;
 * la classe `calcul-en-cours` tombe quand il est fini.
 */
async function attendreLeRendu() {
  const fini = await evaluer(`new Promise((resoudre) => {
    const debut = Date.now();
    const sonder = () => {
      const contenu = document.getElementById("contenu");
      const pret = contenu && !document.getElementById("marqueur-ecrans")
        && !document.body.classList.contains("calcul-en-cours")
        && !contenu.hasAttribute("aria-busy") && contenu.children.length > 0
        && !contenu.querySelector(".chargement");
      if (pret) { resoudre(true); return; }
      if (Date.now() - debut > ${DELAI_RENDU}) { resoudre(false); return; }
      setTimeout(sonder, 40);
    };
    sonder();
  })`);
  if (!fini) { throw new Error("la page ne s'est pas rendue à temps"); }
  // Les polices et deux images : ce que le rendu peut encore déplacer.
  await evaluer("document.fonts.ready.then(() => new Promise((r) => "
    + "requestAnimationFrame(() => requestAnimationFrame(() => r(true)))))");
}

async function allerA(route) {
  const change = await evaluer(`(() => {
    const ancre = ${JSON.stringify(`#${route}`)};
    if (location.hash === ancre) return false;
    const marqueur = document.createElement("i");
    marqueur.id = "marqueur-ecrans";
    document.getElementById("contenu")?.append(marqueur);
    location.hash = ancre;
    return true;
  })()`);
  if (change) { await attendreLeRendu(); }
}

// -- la mesure ---------------------------------------------------------------

/**
 * Ce qui se mesure dans la page, une fois rendue : ce qui dépasse la largeur
 * de l'écran, ce qui défile en largeur dans son cadre, et la place de ce qui
 * doit se voir ensemble — un tracé et sa légende, les quatre montants, les
 * schémas qu'une carte compare.
 */
const MESURER = (ecran) => `(() => {
  // La largeur de l'écran émulé, et non celle de la fenêtre : un téléphone
  // dont la page déborde la dézoome, et sa fenêtre s'élargit d'autant.
  const largeur = ${ecran.largeur};
  const hauteur = ${ecran.hauteur};
  const nommer = (el) => {
    let nom = el.tagName.toLowerCase();
    if (el.id) nom += "#" + el.id;
    const classes = typeof el.className === "string" ? el.className.trim() : "";
    if (classes) nom += "." + classes.split(/\\s+/).join(".");
    const parent = el.closest("figure, table, section, details");
    const ou = parent && parent !== el
      ? " dans " + parent.tagName.toLowerCase()
        + (parent.getAttribute("aria-label") ? " « " + parent.getAttribute("aria-label").slice(0, 60) + " »"
          : parent.className ? "." + String(parent.className).trim().split(/\\s+/)[0] : "")
      : "";
    const texte = (el.textContent || "").replace(/\\s+/g, " ").trim().slice(0, 50);
    return nom + ou + (texte ? " « " + texte + " »" : "");
  };
  const montre = (el) => {
    // Le contenu d'un dépliant fermé garde ses dimensions sous Chromium, qui
    // le cache sans le défaire : checkVisibility le sait.
    if (el.checkVisibility && !el.checkVisibility({ contentVisibilityAuto: true })) return false;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const style = getComputedStyle(n);
      if (style.display === "none" || style.visibility === "hidden") return false;
      // Les textes réservés aux synthèses vocales : un pixel, découpé.
      if (style.clipPath === "inset(50%)" || style.clip === "rect(0px, 0px, 0px, 0px)") return false;
    }
    const cadre = el.getBoundingClientRect();
    return cadre.width > 1 && cadre.height > 1;
  };
  const tous = [...document.body.querySelectorAll("*")];
  const defilants = [];
  const sortants = [];
  // Seul le plus haut de ce qui sort est nommé : un tableau trop large, et
  // non chacune de ses cases.
  const dejaSortis = new Set();
  for (const el of tous) {
    if (!montre(el)) continue;
    const style = getComputedStyle(el);
    if ((style.overflowX === "auto" || style.overflowX === "scroll")
        && el.scrollWidth > el.clientWidth + 1) {
      defilants.push(nommer(el) + " : " + el.scrollWidth + " pour " + el.clientWidth);
    }
    const cadre = el.getBoundingClientRect();
    if (cadre.right > largeur + 1 || cadre.left < -1) {
      dejaSortis.add(el);
      if (!dejaSortis.has(el.parentElement)) {
        sortants.push(nommer(el) + " : de " + Math.round(cadre.left) + " à " + Math.round(cadre.right));
      }
    }
  }
  const document_ = document.documentElement;

  // Un tracé et sa légende. La légende est le figcaption de la figure ; le
  // tracé, son SVG. Ils se touchent s'ils sont l'un au-dessus de l'autre à
  // moins de 24 pixels, ou côte à côte ; et l'on doit pouvoir les voir d'un
  // seul regard : leur boîte commune tient dans l'écran, sous le bandeau.
  const bandeau = document.querySelector("header.bandeau");
  const sousLeBandeau = bandeau && getComputedStyle(bandeau).position === "sticky"
    ? bandeau.getBoundingClientRect().height : 0;
  const traces = [];
  for (const figure of document.querySelectorAll("figure.graphique, figure.cascade, figure.frise")) {
    const svg = figure.querySelector("svg");
    const legende = figure.querySelector(":scope > figcaption");
    if (!svg || !legende || !montre(svg) || !montre(legende)) continue;
    const a = svg.getBoundingClientRect();
    const b = legende.getBoundingClientRect();
    const ecartVertical = Math.max(0, b.top - a.bottom, a.top - b.bottom);
    const coteACote = b.left >= a.right - 1 || a.left >= b.right - 1;
    const etendue = Math.max(a.bottom, b.bottom) - Math.min(a.top, b.top);
    traces.push({
      nom: figure.getAttribute("aria-label") || nommer(figure),
      ecart: Math.round(coteACote ? 0 : ecartVertical),
      etendue: Math.round(etendue),
      place: Math.round(hauteur - sousLeBandeau),
    });
  }

  // Les quatre montants du simulateur : les pensions que les quatre systèmes
  // promettent, à comparer d'un seul regard — du titre du premier système au
  // montant du dernier.
  const sommes = [...document.querySelectorAll(".scenario .chiffre.principal .somme")]
    .filter(montre).map((el) => el.getBoundingClientRect());
  const titres = [...document.querySelectorAll(".scenario .titre")]
    .filter(montre).map((el) => el.getBoundingClientRect());
  const montants = sommes.length ? {
    nombre: sommes.length,
    etendue: Math.round(Math.max(...sommes.map((s) => s.bottom))
      - Math.min(...sommes.map((s) => s.top), ...titres.map((t) => t.top))),
    place: Math.round(hauteur - sousLeBandeau),
  } : null;

  // Les valeurs courtes d'une rangée repliée — « aujourd'hui », « avec notre
  // programme » ; les sept générations d'une carrière type — se lisent
  // ensemble : deux par ligne au moins, jamais une par ligne. Courte : ce que
  // la case MONTRE tient en soixante signes, la longueur que le pli
  // d'index.html tient pour une phrase.
  const texteDe = (case_) => case_.innerText.replace(/\\s+/g, " ").trim();
  const lignesDe = (cases) => {
    const hauts = cases.map((case_) => case_.getBoundingClientRect().top).sort((a, b) => a - b);
    return hauts.filter((haut, rang) => rang === 0 || haut - hauts[rang - 1] > 1).length;
  };
  const empilees = [];
  for (const table of document.querySelectorAll("#contenu table[data-plie]")) {
    if (!montre(table)) continue;
    for (const ligne of [...table.tBodies].flatMap((corps) => [...corps.rows])) {
      const valeurs = [...ligne.cells].slice(1).filter(montre);
      if (valeurs.length < 2) continue;
      if (valeurs.some((case_) => texteDe(case_).length > 60)) continue;
      if (lignesDe(valeurs) > Math.ceil(valeurs.length / 2)) {
        empilees.push(nommer(ligne).slice(0, 140));
      }
    }
  }

  // Une grille — plus de trois colonnes de nombres courts sous des en-têtes
  // courts : les écarts de Carrières types, une génération par colonne — se
  // lit en colonnes. Repliée, une rangée met sur une ligne autant de valeurs
  // que la largeur en tient : chacune large comme la plus large, un demi-rem
  // entre deux.
  const grilles = [];
  const rem = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
  for (const table of document.querySelectorAll("#contenu table[data-plie]")) {
    if (!montre(table)) continue;
    const tete = table.tHead?.rows[table.tHead.rows.length - 1];
    const noms = [...(tete?.cells || [])].slice(1)
      .map((nom) => nom.textContent.replace(/\\s+/g, " ").trim());
    if (noms.length < 4 || noms.some((nom) => nom.length > 8)) continue;
    const rangees = [...table.tBodies].flatMap((corps) => [...corps.rows]).filter(montre);
    const valeursDe = (ligne) => [...ligne.cells].slice(1).filter(montre);
    if (rangees.some((ligne) => valeursDe(ligne).some((case_) =>
      !case_.classList.contains("nombre") || texteDe(case_).length > 8))) continue;
    for (const ligne of rangees) {
      const valeurs = valeursDe(ligne);
      const plusLarge = Math.max(...valeurs.map((case_) => {
        const etendue = document.createRange();
        etendue.selectNodeContents(case_);
        return etendue.getBoundingClientRect().width;
      }));
      const parLigne = Math.max(1, Math.floor(
        (ligne.getBoundingClientRect().width + rem / 2) / (plusLarge + rem / 2)));
      if (lignesDe(valeurs) > Math.ceil(valeurs.length / parLigne)) {
        grilles.push(nommer(ligne).slice(0, 140));
      }
    }
  }

  // Une case plus étroite que ce qu'elle porte : une valeur qui ne se coupe
  // pas passe sur la case voisine, et les deux se lisent l'une dans l'autre —
  // « 422 Md €13,9 % ». Ni la page ni le tableau n'en sont plus larges.
  const chevauchees = [];
  for (const case_ of document.querySelectorAll("#contenu table :is(th, td)")) {
    if (case_.scrollWidth <= case_.clientWidth + 1 || !montre(case_)) continue;
    chevauchees.push(nommer(case_).slice(0, 140) + " : " + case_.scrollWidth
      + " pour " + case_.clientWidth);
  }

  // Les cartes à publier : combien chaque grille en range de front, et la plus
  // petite taille de ce qu'on y lit, la phrase et le détail.
  const cartes = [...document.querySelectorAll("#contenu .cartes")].filter(montre)
    .map((grille) => {
      const figures = [...grille.children].filter((el) => el.tagName === "FIGURE" && montre(el));
      const tailles = [...grille.querySelectorAll(".carte-partage :is(.phrase, .detail)")]
        .filter(montre).map((el) => parseFloat(getComputedStyle(el).fontSize));
      return {
        colonnes: new Set(figures.map((el) => Math.round(el.getBoundingClientRect().left))).size,
        plusPetite: Math.round(Math.min(...tailles) * 10) / 10,
        largeur: Math.round(figures[0]?.getBoundingClientRect().width || 0),
      };
    });

  // Les schémas de Sankey qu'une carte compare : combien vont de front, et la
  // hauteur qu'ils prennent ensemble, du titre du premier au bas du dernier.
  const schemas = [...document.querySelectorAll("#contenu section.cle")]
    .map((carte) => [carte, [...carte.querySelectorAll("figure.sankey")].filter(montre)])
    .filter(([, figures]) => figures.length > 1)
    .map(([carte, figures]) => {
      const cadres = figures.map((el) => el.getBoundingClientRect());
      return {
        carte: carte.id || nommer(carte).slice(0, 60),
        nombre: figures.length,
        colonnes: new Set(cadres.map((cadre) => Math.round(cadre.left))).size,
        rangees: new Set(cadres.map((cadre) => Math.round(cadre.top))).size,
        etendue: Math.round(Math.max(...cadres.map((cadre) => cadre.bottom))
          - Math.min(...cadres.map((cadre) => cadre.top))),
        place: Math.round(hauteur - sousLeBandeau),
      };
    });

  // Les vides : l'écart vertical entre deux blocs voisins de la page, ceux
  // qui se suivent dans une même colonne. Seuls comptent les parents dont
  // tous les enfants sont des boîtes : entre deux blocs séparés par du texte
  // en ligne, l'écart n'est pas vide. Un dessin, et ce qui flotte hors du
  // flux, n'en sont pas non plus.
  const vides = [];
  const horsFlux = (el) => ["absolute", "fixed"].includes(getComputedStyle(el).position);
  const enLigne = (el) => ["inline", "contents"].includes(getComputedStyle(el).display);
  for (const parent of document.querySelectorAll("#contenu, #contenu *")) {
    if (parent.closest("svg") || !montre(parent)) continue;
    const texte = [...parent.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    // Dans l'ordre où l'œil les voit, et non dans celui du HTML : une rangée
    // flexible peut les réordonner.
    const enfants = [...parent.children].filter((el) => montre(el) && !horsFlux(el))
      .sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
    if (texte || enfants.some(enLigne)) continue;
    // Une grille de plusieurs colonnes aligne ses cases sur la plus haute de
    // sa rangée : le blanc d'une case voisine n'est pas un vide entre deux
    // blocs qui se suivent.
    const cadres = enfants.map((el) => el.getBoundingClientRect());
    if (cadres.some((a, rang) => rang > 0 && a.top < cadres[rang - 1].bottom - 1)) continue;
    for (let rang = 0; rang + 1 < enfants.length; rang += 1) {
      const a = enfants[rang].getBoundingClientRect();
      const b = enfants[rang + 1].getBoundingClientRect();
      if (b.top < a.bottom - 1 || b.left >= a.right - 1) continue;
      vides.push({ vide: Math.round(b.top - a.bottom),
        entre: nommer(enfants[rang]).slice(0, 60) + " et " + nommer(enfants[rang + 1]).slice(0, 80) });
    }
  }
  vides.sort((x, y) => y.vide - x.vide);

  // Le contraste de chaque texte sur son fond (WCAG 1.4.3 ; la règle
  // color-contrast d'axe, que joue Lighthouse, action 174) : la couleur du
  // texte, fondue sur le premier fond opaque de ses ancêtres, les voiles
  // translucides fondus en chemin, l'opacité des ancêtres comptée. Un fond
  // d'image ou de dégradé ne se calcule pas : le texte qui s'y pose est laissé
  // de côté, comme axe le laisse. Le texte d'un dessin non plus, ni celui d'un
  // champ désactivé, que WCAG exempte.
  const couleur = (texte) => {
    const lue = /^rgba?\\(([^)]+)\\)$/.exec(texte);
    if (!lue) return null;
    const [r, v, b, a = 1] = lue[1].split(/[\\s,/]+/).filter(Boolean).map(Number);
    return [r, v, b, a];
  };
  const fondu = (dessus, dessous) => [0, 1, 2]
    .map((i) => dessus[i] * dessus[3] + dessous[i] * (1 - dessus[3])).concat(1);
  const canal = (c) => (c / 255 <= 0.04045 ? c / 255 / 12.92 : ((c / 255 + 0.055) / 1.055) ** 2.4);
  const luminance = ([r, v, b]) => 0.2126 * canal(r) + 0.7152 * canal(v) + 0.0722 * canal(b);
  const fondDe = (el) => {
    const voiles = [];
    for (let n = el; n; n = n.parentElement) {
      const style = getComputedStyle(n);
      if (style.backgroundImage !== "none") return null;
      const teinte = couleur(style.backgroundColor);
      if (teinte === null) return null;
      if (teinte[3] > 0) voiles.push(teinte);
      if (teinte[3] >= 1) break;
    }
    if (!voiles.length || voiles[voiles.length - 1][3] < 1) return null;
    return voiles.reduceRight((dessous, dessus) => fondu(dessus, dessous));
  };
  const contrastes = [];
  for (const el of tous) {
    if (el.closest("svg") || el.matches(":disabled") || !montre(el)) continue;
    if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    const style = getComputedStyle(el);
    const encre = couleur(style.color);
    const fond = fondDe(el);
    if (encre === null || fond === null) continue;
    let opacite = 1;
    for (let n = el; n; n = n.parentElement) opacite *= Number(getComputedStyle(n).opacity);
    const lu = fondu([...encre.slice(0, 3), encre[3] * opacite], fond);
    const [clair, sombre] = [luminance(lu), luminance(fond)].sort((x, y) => y - x);
    const rapport = (clair + 0.05) / (sombre + 0.05);
    const taille = parseFloat(style.fontSize);
    const grand = taille >= 24 || (taille >= 18.66 && Number(style.fontWeight) >= 700);
    const seuil = grand ? 3 : 4.5;
    if (rapport < seuil) {
      contrastes.push(nommer(el) + " : " + rapport.toFixed(2) + " pour " + seuil
        + " (" + style.color + " sur rgb(" + fond.slice(0, 3).map(Math.round).join(", ") + "))");
    }
  }

  return {
    contrastes: contrastes.slice(0, 40), nombreContrastes: contrastes.length,
    vides: vides.slice(0, 12),
    deborde: document_.scrollWidth > largeur + 1 ? document_.scrollWidth : 0,
    defilants: defilants.slice(0, 40), nombreDefilants: defilants.length,
    sortants: sortants.slice(0, 40), nombreSortants: sortants.length,
    traces, montants, empilees: empilees.slice(0, 40), grilles: grilles.slice(0, 40),
    chevauchees: chevauchees.slice(0, 40), cartes, schemas,
  };
})()`;

/**
 * L'image que « Partager » compose pour la première carte qui compare des
 * schémas : la place de chaque schéma dans l'image, et sa taille. Le pilote
 * épie la toile — chaque tracé y entre par `drawImage`, en SVG —, clique, et
 * rend ce qu'il a vu quand l'image s'exporte. La feuille de partage du
 * système est écartée : seul l'enregistrement, refusé, reste.
 */
const IMAGE_DES_SCHEMAS = `new Promise((resoudre) => {
  const carte = [...document.querySelectorAll("#contenu section.cle")]
    .find((c) => c.querySelectorAll("figure.sankey").length > 1);
  const bouton = carte && carte.querySelector("button.partager");
  if (!bouton) { resoudre(null); return; }
  // La largeur de chaque dessin dans la page, dans l'ordre où l'image les prend.
  const dessins = [...carte.querySelectorAll("figure.sankey svg")]
    .map((svg) => Math.round(svg.viewBox.baseVal.width));
  const traces = [];
  const dessiner = CanvasRenderingContext2D.prototype.drawImage;
  const exporter = HTMLCanvasElement.prototype.toBlob;
  const finir = (image) => {
    CanvasRenderingContext2D.prototype.drawImage = dessiner;
    HTMLCanvasElement.prototype.toBlob = exporter;
    resoudre(image);
  };
  CanvasRenderingContext2D.prototype.drawImage = function (image, ...place) {
    if (image instanceof HTMLImageElement && image.src.startsWith("data:image/svg")) {
      const [x, y, largeur, hauteur] = place.map(Math.round);
      traces.push({ x, y, largeur, hauteur });
    }
    return dessiner.call(this, image, ...place);
  };
  HTMLCanvasElement.prototype.toBlob = function (...suite) {
    finir({ traces, dessins, largeur: this.width, hauteur: this.height });
    return exporter.apply(this, suite);
  };
  Object.defineProperty(navigator, "canShare", { value: () => false, configurable: true });
  bouton.click();
  setTimeout(() => finir({ traces, dessins, largeur: 0, hauteur: 0 }), ${DELAI_RENDU});
})`;

/** Pose l'écran émulé : ce que fait le lecteur qui tourne ou étire sa fenêtre. */
function poserLEcran(ecran) {
  return page("Emulation.setDeviceMetricsOverride", {
    width: ecran.largeur, height: ecran.hauteur, deviceScaleFactor: 1,
    mobile: ecran.largeur < 768,
  });
}

/**
 * Change l'écran de la page affichée, sans changer d'adresse, et attend
 * qu'elle se redessine sur place ; rend `false` si elle ne l'a pas fait dans
 * le délai d'un rendu. Le redessin attend un quart de seconde que la fenêtre
 * ne bouge plus, puis remplace le contenu, et le marqueur avec.
 */
async function changerDEcran(ecran) {
  await evaluer(`(() => {
    const marqueur = document.createElement("i");
    marqueur.id = "marqueur-ecrans";
    document.getElementById("contenu").append(marqueur);
    return true;
  })()`);
  await poserLEcran(ecran);
  return evaluer(`new Promise((resoudre) => {
    const debut = Date.now();
    const sonder = () => {
      if (!document.getElementById("marqueur-ecrans")
          && !document.body.classList.contains("calcul-en-cours")) { resoudre(true); return; }
      if (Date.now() - debut > ${DELAI_RENDU}) {
        document.getElementById("marqueur-ecrans")?.remove();
        resoudre(false);
        return;
      }
      setTimeout(sonder, 40);
    };
    sonder();
  })`);
}

/** Chaque schéma de la page : la largeur de son dessin, celle où il se montre. */
const SCHEMAS_DESSINES = `[...document.querySelectorAll("#contenu figure.sankey svg")]
  .map((svg) => ({ dessin: Math.round(svg.viewBox.baseVal.width),
    montre: Math.round(svg.getBoundingClientRect().width) }))`;

// -- la visite ---------------------------------------------------------------

const resultats = [];
try {
  let charge = false;
  for (const ecran of plan.ecrans) {
    await poserLEcran(ecran);
    if (!charge) {
      await page("Page.navigate", { url: `${plan.adresse}#/` });
      await attendreLeRendu();
      charge = true;
    }
    for (const route of plan.routes) {
      erreursDeLaPage.length = 0;
      // On passe par une autre page : une même adresse, redemandée, ne se
      // rend pas, et chaque page doit l'être à la largeur qu'on mesure.
      await allerA(route === "/partager" ? "/" : "/partager");
      await allerA(route);
      const replie = await evaluer(MESURER(ecran));
      await evaluer(`(() => {
        for (const d of document.querySelectorAll("#contenu details")) d.open = true;
        return true;
      })()`);
      await evaluer("new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(true))))");
      const deplie = await evaluer(MESURER(ecran));
      const image = replie.schemas.length ? await evaluer(IMAGE_DES_SCHEMAS) : null;
      // La fenêtre qu'on rétrécit, au large, sur une page qui pose des
      // schémas de front : ce qu'elle redessine. Puis l'écran de la visite.
      let retrecie = null;
      if (replie.schemas.length && plan.retrecir?.depuis === ecran.largeur) {
        const redessinee = await changerDEcran(plan.retrecir.vers);
        retrecie = { ...plan.retrecir.vers, redessinee, schemas: await evaluer(SCHEMAS_DESSINES) };
        await changerDEcran(ecran);
      }
      resultats.push({
        largeur: ecran.largeur, hauteur: ecran.hauteur, route,
        replie, deplie, image, retrecie, erreurs: [...erreursDeLaPage],
      });
    }
  }
  process.stdout.write(JSON.stringify(resultats));
} catch (erreur) {
  process.stderr.write(String(erreur?.stack || erreur));
  process.exitCode = 1;
} finally {
  ws.close();
  fermer();
}
