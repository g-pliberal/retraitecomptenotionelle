/**
 * Les adresses du site (action 174) : la page dans le chemin, le lecteur
 * derrière le `#`.
 *
 * Une page a son dossier — `cout/`, `simuler/` —, l'accueil la racine du site.
 * Ce qui appartient au lecteur, sa carrière et ses réglages, reste derrière le
 * `#`, que le navigateur ne transmet à aucun serveur : `cout/#indexation=prix`,
 * `simuler/#naissance=1965-03-01&sexe=H`. Un mot sans `=` y désigne une section
 * de la page : `cout/#cout-depenses`, `simuler/#cumul&naissance=…`.
 *
 * L'ancienne forme portait tout derrière le `#`, la page en tête :
 * `#/cout?indexation=prix`. C'est celle des partages publiés avant le
 * changement ; elle se lit encore, et `ancienne` la signale.
 *
 * Le gabarit dit où va chaque page (`dossierDe`) et comment on y va depuis une
 * autre (`versLaPage`) ; ce module lit une adresse, et écrit la nouvelle forme
 * d'une ancienne. Il ne lit rien du texte des pages.
 */

import { PAGES, dossierDe } from "./gabarit.js";
import { CLES_MODELISATION } from "./cles.js";

/**
 * Les adresses de deux pages qui n'existent plus, et ce qu'elles montrent
 * désormais : la page, et la section à ouvrir. Le routeur la lit pour ouvrir
 * cette section.
 *
 * HUIT PAGES AU LIEU DE DIX, depuis le 23 septembre 2026 : « Cumul versé »
 * redisait, sur une page à elle, le dépliant « Ce que chaque système finit par
 * verser » des résultats — le même graphique, calculé par la même fonction ;
 * « Sources » répondait à la question que pose la page Méthode, « comment le
 * sait-on ? ». Leurs adresses restent valides — le site parent et des partages
 * les portent — et mènent à ce qui les a remplacées : les résultats du
 * simulateur, cumul ouvert, et la partie Sources de la page Méthode.
 */
export const ANCIENNES_ROUTES = {
  "/trajectoire": ["/simuler", "cumul"],
  "/donnees": ["/methode", "sources"],
};

/** Les paramètres d'une requête écrite, chacun à sa valeur. */
function parametresDe(requete) {
  const parametres = {};
  new URLSearchParams(requete).forEach((valeur, cle) => { parametres[cle] = valeur; });
  return parametres;
}

/**
 * Ce que désigne une adresse de l'ancienne forme, `#/page?requete`.
 *
 * Les adresses partagées avant que l'accueil ne devienne le programme
 * portaient la simulation sur « #/ » ; leur rendre le formulaire coûte une
 * ligne, et les perdre coûterait la simulation qu'elles décrivent.
 *
 * Une adresse qui ne porte que des RÈGLES n'en est pas une : depuis que les
 * réglages suivent le lecteur, tous les liens du site les portent, celui de
 * l'accueil compris. Sans cette réserve, cliquer « Programme » après avoir
 * changé l'indexation envoyait sur le simulateur.
 */
function lireAncienne(brut) {
  const separation = brut.indexOf("?");
  const route = (separation === -1 ? brut : brut.slice(0, separation)) || "/";
  const requete = separation === -1 ? "" : brut.slice(separation + 1);
  const parametres = parametresDe(requete);
  const [remplacante, section] = ANCIENNES_ROUTES[route] || [];
  if (remplacante) {
    return { chemin: remplacante, parametres, requete, section, ancienne: true };
  }
  const simulationDAccueil = route === "/" && Object.keys(parametres).some(
    (cle) => !CLES_MODELISATION.includes(cle),
  );
  return {
    chemin: simulationDAccueil ? "/simuler" : route, parametres, requete, section: "",
    ancienne: true,
  };
}

/**
 * Ce que désigne une adresse : la page, ce que le lecteur y porte, la section
 * à ouvrir.
 *
 * `chemin` est celui de la page, relatif à la racine du site — "" ou
 * "index.html" pour l'accueil, "cout/" ou "cout/index.html" pour une page —,
 * `ancre` ce qui suit le `#`. Rend `{ chemin, parametres, requete, section,
 * ancienne }` : la route de la page ("/cout"), les paramètres du lecteur, leur
 * requête telle qu'elle est écrite — la mémoire du simulateur la compare au
 * caractère près —, la section, et si l'adresse est de l'ancienne forme.
 */
export function lireAdresse(chemin, ancre) {
  const brut = String(ancre || "").replace(/^#/, "");
  if (brut.startsWith("/")) { return lireAncienne(brut); }
  const dossier = String(chemin || "").replace(/(^|\/)index\.html$/, "").replace(/\/+$/, "");
  const morceaux = brut ? brut.split("&") : [];
  const requete = morceaux.filter((morceau) => morceau.includes("=")).join("&");
  return {
    chemin: dossier ? `/${dossier.split("/").pop()}` : "/",
    parametres: parametresDe(requete),
    requete,
    section: morceaux.find((morceau) => morceau && !morceau.includes("=")) || "",
    ancienne: false,
  };
}

/**
 * L'adresse de la nouvelle forme qui désigne ce que désigne `adresse` (le
 * résultat de `lireAdresse`), relative à la racine du site : le dossier de la
 * page, puis ce que le lecteur y porte derrière le `#`, la section en tête.
 *
 * C'est la redirection d'une ancienne adresse (`#/cout?indexation=prix` devient
 * `cout/#indexation=prix`), mais elle écrit aussi bien une adresse déjà neuve.
 * Une page qui n'existe pas mène à l'accueil, comme le rendu la remplace : son
 * dossier n'existerait pas.
 */
export function ecrireAdresse({ chemin, requete, section }) {
  const fragment = [section, requete].filter(Boolean).join("&");
  return `${dossierDe(PAGES.includes(chemin) ? chemin : "/")}${fragment ? `#${fragment}` : ""}`;
}
