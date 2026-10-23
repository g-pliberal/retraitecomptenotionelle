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
 *      "routes": ["/", "/cout", "/simuler?naissance=…", ...]}
 *
 * Le paquet de données n'est chargé qu'une fois : on change de page par
 * l'ancre, comme le lecteur, et de largeur par l'émulation de l'écran.
 */

import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [navigateur, cheminPlan] = process.argv.slice(2);
const plan = JSON.parse(readFileSync(cheminPlan, "utf-8"));

/** Le délai au-delà duquel une page qui ne se rend pas fait échouer la visite. */
const DELAI_RENDU = 30000;

// -- le navigateur -----------------------------------------------------------

const profil = mkdtempSync(join(tmpdir(), "ecrans-"));
const chrome = spawn(navigateur, [
  "--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profil}`,
  "--no-first-run", "--no-default-browser-check", "--disable-gpu",
  "--disable-extensions", "--hide-scrollbars", "--mute-audio",
  // Le bac à sable de Chromium refuse de tourner sous root, ce que sont les
  // conteneurs des sessions ; la page servie est celle du dépôt, rien d'autre.
  "--no-sandbox",
  "about:blank",
], { stdio: ["ignore", "ignore", "pipe"] });

function fermer() {
  try { chrome.kill("SIGKILL"); } catch { /* déjà parti */ }
  try { rmSync(profil, { recursive: true, force: true }); } catch { /* tant pis */ }
}
process.on("exit", fermer);

/** L'adresse du WebSocket, que Chromium écrit sur sa sortie d'erreur. */
const adresseDuProtocole = await new Promise((resoudre, rejeter) => {
  let lu = "";
  const delai = setTimeout(() => rejeter(new Error(
    `le navigateur n'a pas ouvert son protocole : ${lu.slice(-500)}`)), 30000);
  chrome.stderr.on("data", (morceau) => {
    lu += morceau.toString();
    const trouve = lu.match(/DevTools listening on (ws:\/\/\S+)/);
    if (trouve) { clearTimeout(delai); resoudre(trouve[1]); }
  });
  chrome.on("exit", (code) => rejeter(new Error(
    `le navigateur s'est arrêté (${code}) : ${lu.slice(-500)}`)));
});

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
 * doit se voir ensemble — un tracé et sa légende, les quatre montants.
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

  return {
    vides: vides.slice(0, 12),
    deborde: document_.scrollWidth > largeur + 1 ? document_.scrollWidth : 0,
    defilants: defilants.slice(0, 40), nombreDefilants: defilants.length,
    sortants: sortants.slice(0, 40), nombreSortants: sortants.length,
    traces, montants,
  };
})()`;

// -- la visite ---------------------------------------------------------------

const resultats = [];
try {
  let charge = false;
  for (const ecran of plan.ecrans) {
    await page("Emulation.setDeviceMetricsOverride", {
      width: ecran.largeur, height: ecran.hauteur, deviceScaleFactor: 1,
      mobile: ecran.largeur < 768,
    });
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
      resultats.push({
        largeur: ecran.largeur, hauteur: ecran.hauteur, route,
        replie, deplie, erreurs: [...erreursDeLaPage],
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
