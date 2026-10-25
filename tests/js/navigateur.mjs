/**
 * Chromium sans fenêtre, lancé jusqu'à ce qu'il ouvre son protocole.
 *
 *     const { adresse, fermer } = await ouvrirLeNavigateur(chemin);
 *
 * `adresse` est celle du WebSocket du protocole des outils de développement,
 * que Chromium écrit sur sa sortie d'erreur ; `fermer()` le tue et efface son
 * profil. C'est le pilote des écrans (`tests/js/ecrans.mjs`) qui s'en sert.
 *
 * Sur GitHub, le premier Chromium d'une course démarre à froid, sur une
 * machine neuve : rien de lui n'a encore été lu du disque, ni son programme
 * ni ses polices, et trois autres processus de tests occupent les quatre
 * cœurs. Le 25 octobre 2026, deux courses de suite, il n'avait pas ouvert son
 * protocole au bout de trente secondes, quand il le fait ici en deux secondes
 * à froid, en deux dixièmes ensuite ; à la course 1000, il n'avait même rien
 * écrit. Un lancement suivant l'ouvrait, ce que les premiers avaient lu resté
 * en mémoire. Il a donc une minute ; muet passé ce délai, il est tué et
 * relancé, une fois, sur un profil neuf, que rien de ce que le mort a laissé
 * n'encombre. Absent ou cassé, il échoue aussitôt, avec son message : le
 * relancer n'y changerait rien. Les erreurs de D-Bus qu'il écrit en démarrant
 * ne disent rien d'un retard : il en écrit autant à chaque lancement, ici
 * comme sur GitHub.
 */

import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

/** Le délai, en millisecondes, dans lequel Chromium doit ouvrir son protocole. */
const DELAI_PROTOCOLE = 60000;

/** Les lancements tentés, le premier compris, tant que Chromium reste muet. */
const LANCEMENTS = 2;

/** Ce qu'on garde de ce qu'un lancement a écrit, pour le dire s'il échoue. */
const TAILLE_LUE = 1000;

/**
 * Lance Chromium sur un profil neuf. `adresse` dit l'issue de son démarrage :
 * l'adresse du protocole, ou une erreur, marquée `muet` s'il s'est seulement
 * tu jusqu'au délai ; `tuer()` l'arrête, attend qu'il soit parti et efface son
 * profil.
 */
function lancer(chemin, delai) {
  const profil = mkdtempSync(join(tmpdir(), "ecrans-"));
  const lance = new Date().toISOString().slice(11, 23);
  const chrome = spawn(chemin, [
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
  // Sans processus, quand il n'a pu se lancer, il n'y a rien à attendre.
  const parti = new Promise((resoudre) => {
    chrome.on("exit", resoudre);
    chrome.on("error", resoudre);
  });

  let lu = "";
  const adresse = new Promise((resoudre, rejeter) => {
    const minuterie = setTimeout(() => {
      const ecrit = lu.slice(-TAILLE_LUE).trim() || "rien";
      rejeter(Object.assign(new Error(`lancé à ${lance} UTC, il a écrit : ${ecrit}`), { muet: true }));
    }, delai);
    chrome.stderr.on("data", (morceau) => {
      lu = (lu + morceau.toString()).slice(-4 * TAILLE_LUE);
      const trouve = lu.match(/DevTools listening on (ws:\/\/\S+)/);
      if (trouve) { clearTimeout(minuterie); resoudre(trouve[1]); }
    });
    chrome.on("error", (erreur) => {
      clearTimeout(minuterie);
      rejeter(new Error(`le navigateur ne se lance pas : ${erreur.message}`));
    });
    chrome.on("exit", (code, signal) => {
      clearTimeout(minuterie);
      rejeter(new Error(`le navigateur s'est arrêté (${code ?? signal}) : ${lu.slice(-TAILLE_LUE)}`));
    });
  });

  async function tuer() {
    try { chrome.kill("SIGKILL"); } catch { /* déjà parti */ }
    await parti;
    process.off("exit", fermer);
    fermer();
  }
  return { adresse, fermer, tuer };
}

export async function ouvrirLeNavigateur(chemin, { delai = DELAI_PROTOCOLE } = {}) {
  const muets = [];
  for (let lancement = 1; lancement <= LANCEMENTS; lancement += 1) {
    const essai = lancer(chemin, delai);
    try {
      return { adresse: await essai.adresse, fermer: essai.fermer };
    } catch (erreur) {
      await essai.tuer();
      if (!erreur.muet) { throw erreur; }
      muets.push(erreur.message);
    }
  }
  throw new Error(`le navigateur n'a pas ouvert son protocole en ${delai / 1000} s, `
    + `à aucun de ses ${LANCEMENTS} lancements :\n— ${muets.join("\n— ")}`);
}
