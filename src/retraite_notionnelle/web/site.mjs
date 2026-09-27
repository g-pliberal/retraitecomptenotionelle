/**
 * Le site, servi au Python : ses pages et ses modules, une ligne JSON par demande.
 *
 * Le texte du site n'est écrit qu'une fois, en JavaScript (docs/architecture.md,
 * § 8). Ce que le Python en lit — les pages que ses tests examinent, les
 * témoins de pages, les constantes que la prose cite — passe par ce programme,
 * que ``site.py`` lance et garde ouvert : le paquet n'est lu qu'une fois, et le
 * contexte garde ses agrégats d'une demande à l'autre, comme dans le
 * navigateur.
 *
 * Chaque ligne reçue est une demande, chaque ligne écrite sa réponse :
 *
 *     {"op": "rendre", "chemin": "/simuler", "requete": {...}}  ->  [titre, corps]
 *     {"op": "page", "chemin": "/", "requete": {}}              ->  la page entière
 *     {"op": "lire", "module": "pages", "nom": "TITRES"}        ->  sa valeur
 *     {"op": "appeler", "module": "gabarit", "nom": "pourcentage",
 *      "args": [0.25], "kwargs": {"decimales": 0}}               ->  ce qu'elle rend
 *
 * Une valeur qui n'est pas une donnée — une instance de classe, le contexte —
 * part par référence : le Python en reçoit un numéro, lit ses champs et appelle
 * ses méthodes à la demande, et peut la rendre en argument. Rien d'autre que les
 * réponses ne passe par la sortie standard.
 */

import { readFileSync } from "node:fs";
import { createInterface } from "node:readline";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const PORTAGE = join(RACINE, "moteur", "js");

const sortie = process.stdout;
for (const nom of ["log", "info", "warn", "debug"]) {
  console[nom] = (...morceaux) => process.stderr.write(`${morceaux.join(" ")}\n`);
}

const modules = new Map();
async function module(nom) {
  if (!/^[\w-]+(\/[\w-]+)*$/.test(nom)) {
    throw new Error(`module inconnu : ${nom}`);
  }
  if (!modules.has(nom)) {
    modules.set(nom, await import(pathToFileURL(join(PORTAGE, `${nom}.js`)).href));
  }
  return modules.get(nom);
}

let contexte = null;
async function leContexte() {
  if (contexte === null) {
    const { Contexte } = await module("contexte");
    contexte = new Contexte(JSON.parse(readFileSync(join(RACINE, "moteur", "donnees.json"), "utf8")));
  }
  return contexte;
}

// -- d'une langue à l'autre -----------------------------------------------------

const objets = [];

function estDonnee(valeur) {
  const prototype = Object.getPrototypeOf(valeur);
  return prototype === Object.prototype || prototype === null;
}

function versJson(valeur) {
  if (valeur === undefined || valeur === null) {
    return null;
  }
  if (typeof valeur === "number") {
    return Number.isFinite(valeur) ? valeur : { $nombre: String(valeur) };
  }
  if (typeof valeur === "string" || typeof valeur === "boolean") {
    return valeur;
  }
  if (typeof valeur === "bigint") {
    return Number(valeur);
  }
  if (typeof valeur === "function") {
    return { $fonction: valeur.name };
  }
  if (Array.isArray(valeur)) {
    return valeur.map(versJson);
  }
  if (valeur instanceof Set) {
    return { $ensemble: [...valeur].map(versJson) };
  }
  if (valeur instanceof Map) {
    return { $table: [...valeur].map(([cle, v]) => [versJson(cle), versJson(v)]) };
  }
  if (estDonnee(valeur)) {
    // Une donnée part avec ses champs, et garde sa référence : rendue en
    // argument, c'est elle qui revient — ses tables et ses ensembles compris,
    // que le JSON ne sait pas écrire.
    return {
      $donnee: Object.fromEntries(Object.entries(valeur).map(([cle, v]) => [cle, versJson(v)])),
      $ref: reference(valeur),
    };
  }
  // Une instance part par référence : ses champs se lisent à la demande, un
  // contexte portant tout le paquet.
  return { $ref: reference(valeur), $classe: valeur.constructor?.name ?? "" };
}

const references = new Map();
function reference(objet) {
  if (!references.has(objet)) {
    references.set(objet, objets.push(objet) - 1);
  }
  return references.get(objet);
}

async function depuisJson(valeur) {
  if (Array.isArray(valeur)) {
    return Promise.all(valeur.map(depuisJson));
  }
  if (valeur === null || typeof valeur !== "object") {
    return valeur;
  }
  if ("$ref" in valeur) {
    return objets[valeur.$ref];
  }
  if ("$nombre" in valeur) {
    return Number(valeur.$nombre);
  }
  const entrees = await Promise.all(
    Object.entries(valeur).map(async ([cle, v]) => [cle, await depuisJson(v)]));
  return Object.fromEntries(entrees);
}

/**
 * Un nom exporté, ou le membre d'un exporté : « Saisie.depuisRequete » est la
 * méthode statique de la classe, appelée avec la classe pour ``this``.
 */
async function resoudre(nom, exporte) {
  const espace = await module(nom);
  const [tete, ...suite] = exporte.split(".");
  if (!(tete in espace)) {
    return null;
  }
  let porteur = espace;
  let valeur = espace[tete];
  for (const membre of suite) {
    if (valeur === null || valeur === undefined || !(membre in Object(valeur))) {
      return null;
    }
    porteur = valeur;
    valeur = valeur[membre];
  }
  return { porteur, valeur };
}

/** Ce que « lire » et « attribut » rendent tel quel : une réponse sur la valeur, non la valeur. */
function estMarqueur(resultat) {
  return resultat !== null && typeof resultat === "object" && estDonnee(resultat)
    && ("$appelable" in resultat || "$absent" in resultat || "$methode" in resultat);
}

/** Les noms des paramètres d'une fonction ou d'un constructeur, dans l'ordre. */
function parametres(fonction) {
  const source = Function.prototype.toString.call(fonction);
  let debut = source.indexOf("(");
  if (source.startsWith("class")) {
    const constructeur = source.search(/\bconstructor\s*\(/);
    if (constructeur < 0) {
      return [];
    }
    debut = source.indexOf("(", constructeur);
  }
  const noms = [];
  let profondeur = 0;
  let courant = "";
  for (let i = debut + 1; i < source.length; i += 1) {
    const c = source[i];
    if ("([{".includes(c)) {
      profondeur += 1;
    } else if (")]}".includes(c)) {
      if (profondeur === 0) {
        noms.push(courant);
        break;
      }
      profondeur -= 1;
    } else if (c === "," && profondeur === 0) {
      noms.push(courant);
      courant = "";
      continue;
    }
    courant += c;
  }
  return noms
    .map((morceau) => morceau.trim())
    .filter((morceau) => morceau !== "")
    .map((morceau) => (/^[A-Za-z_$][\w$]*/.exec(morceau.replace(/^\.\.\./, "")) ?? [null])[0]);
}

/** Les arguments nommés vont à la place du paramètre de même nom. */
function placer(fonction, args, kwargs) {
  const noms = Object.keys(kwargs ?? {});
  if (noms.length === 0) {
    return args;
  }
  const ordre = parametres(fonction);
  const places = [...args];
  for (const nom of noms) {
    const rang = ordre.indexOf(nom);
    if (rang < 0) {
      throw new Error(`${fonction.name} n'a pas de paramètre « ${nom} » (${ordre.join(", ")})`);
    }
    if (rang < args.length) {
      throw new Error(`${fonction.name} : « ${nom} » est déjà donné par position`);
    }
    while (places.length < rang) {
      places.push(undefined);
    }
    places[rang] = kwargs[nom];
  }
  return places;
}

// -- les demandes --------------------------------------------------------------

const operations = {
  async rendre({ chemin, requete }) {
    const { rendre } = await module("pages");
    return rendre(await leContexte(), chemin, requete ?? {});
  },

  async page({ chemin, requete }) {
    const { rendre } = await module("pages");
    const gabarit = await module("gabarit");
    const [, corps] = rendre(await leContexte(), chemin, requete ?? {});
    return gabarit.entete(chemin) + corps + gabarit.pied();
  },

  async lire({ module: nom, nom: exporte }) {
    const trouve = await resoudre(nom, exporte);
    if (trouve === null) {
      return { $absent: `moteur/js/${nom}.js n'exporte pas « ${exporte} »` };
    }
    if (typeof trouve.valeur === "function") {
      const classe = Function.prototype.toString.call(trouve.valeur).startsWith("class");
      return { $appelable: exporte, classe, parametres: parametres(trouve.valeur) };
    }
    return trouve.valeur;
  },

  async appeler({ module: nom, nom: exporte, args, kwargs }) {
    const trouve = await resoudre(nom, exporte);
    if (trouve === null || typeof trouve.valeur !== "function") {
      throw new Error(`moteur/js/${nom}.js n'exporte pas de fonction « ${exporte} »`);
    }
    const fonction = trouve.valeur;
    const arguments_ = placer(fonction, await depuisJson(args ?? []), await depuisJson(kwargs ?? {}));
    if (Function.prototype.toString.call(fonction).startsWith("class")) {
      return new fonction(...arguments_);
    }
    return fonction.apply(trouve.porteur, arguments_);
  },

  async attribut({ ref, noms }) {
    const objet = objets[ref];
    const nom = noms.find((candidat) => candidat in objet);
    if (nom === undefined) {
      return { $absent: `${objet.constructor?.name ?? "l'objet"} n'a pas « ${noms.join(" » ni « ")} »` };
    }
    if (typeof objet[nom] === "function") {
      return { $methode: nom };
    }
    return objet[nom];
  },

  async contexte() {
    return leContexte();
  },

  async methode({ ref, nom, args, kwargs }) {
    const objet = objets[ref];
    const fonction = objet[nom];
    return fonction.apply(objet, placer(fonction, await depuisJson(args ?? []),
      await depuisJson(kwargs ?? {})));
  },
};

const lignes = createInterface({ input: process.stdin, crlfDelay: Infinity });
for await (const ligne of lignes) {
  if (ligne.trim() === "") {
    continue;
  }
  let reponse;
  try {
    const demande = JSON.parse(ligne);
    const operation = operations[demande.op];
    if (operation === undefined) {
      throw new Error(`opération inconnue : ${demande.op}`);
    }
    const resultat = await operation(demande);
    reponse = { resultat: estMarqueur(resultat) ? resultat : versJson(resultat) };
  } catch (erreur) {
    reponse = { erreur: { nom: erreur?.constructor?.name ?? erreur?.name ?? "Error",
      message: String(erreur?.message ?? erreur),
      pile: String(erreur?.stack ?? "") } };
  }
  sortie.write(`${JSON.stringify(reponse)}\n`);
}
