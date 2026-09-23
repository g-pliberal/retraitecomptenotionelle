/**
 * Les bascules du simulateur, refaites au clic sur ce que le formulaire porte.
 *
 * Les liens des bascules — en activité ou à la retraite, l'unité, le net ou le
 * brut — sont écrits au rendu, depuis la saisie calculée. Ce qui a été tapé
 * depuis n'y est pas : le script de la page refait donc l'adresse au clic, par
 * `requeteBasculee`. Deux choses sont tenues ici. Formulaire intact, l'adresse
 * refaite est le lien du rendu, au caractère près. Formulaire changé, elle est
 * le lien qu'aurait écrit le rendu de la saisie changée : la traduction des
 * montants est la même, où qu'elle se fasse.
 *
 *     node --test tests/js/*.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { Contexte, Saisie, rendre, requeteBasculee } from "../../moteur/js/pages.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const contexte = new Contexte(paquet);

const ENTITES = { "&amp;": "&", "&quot;": '"', "&#x27;": "'", "&lt;": "<", "&gt;": ">" };

function enObjet(requete) {
  const objet = {};
  new URLSearchParams(requete).forEach((valeur, cle) => { objet[cle] = valeur; });
  return objet;
}

/** Les liens des bascules d'une page : `[légende, requête]`, dans l'ordre. */
function liensDesBascules(html) {
  const liens = [];
  const groupes = /<div class="bascule" role="group" aria-label="([^"]+)">(.*?)<\/div>/gs;
  for (const [, legende, corps] of html.matchAll(groupes)) {
    for (const [, requete] of corps.matchAll(/<a href="#\/simuler\?([^"]*)">/g)) {
      liens.push([legende, requete.replace(/&[a-z#0-9]+;/g, (entite) => ENTITES[entite])]);
    }
  }
  return liens;
}

/** Ce que le formulaire d'une saisie porte : la saisie, réécrite. */
function formulaireDe(parametres) {
  return enObjet(Saisie.depuisRequete(parametres).requete());
}

const BASE = {
  unite_revenu: "euros_mois", montants: "net", situation: "actif",
  saisie_par: "revenu", naissance: "1972-03-01", debut: "1993-09-01",
  statut: "salarie_prive_non_cadre", salaire: "3500", liquidation: "2036-04-01",
};

const SAISIES = {
  "euros nets": BASE,
  "euros bruts": { ...BASE, montants: "brut", salaire: "4400" },
  "multiples du salaire moyen": { ...BASE, unite_revenu: "moyen", salaire: "1.2" },
  "deux métiers": {
    ...BASE, metier2_debut: "2005-01-01", metier2_statut: "fonctionnaire_etat",
    metier2_salaire: "2900",
  },
  "retraité, par la pension": {
    ...BASE, situation: "retraite", saisie_par: "pension", pension: "1650",
    naissance: "1955-06-01", debut: "1975-09-01", liquidation: "2017-07-01",
  },
};

test("formulaire intact, la bascule refaite est le lien du rendu", () => {
  for (const [nom, parametres] of Object.entries(SAISIES)) {
    const liens = liensDesBascules(rendre(contexte, "/simuler", parametres)[1]);
    assert.ok(liens.length >= 2, `${nom} : aucune bascule trouvée`);
    for (const [legende, lien] of liens) {
      assert.equal(
        requeteBasculee(contexte, formulaireDe(parametres), enObjet(lien)), lien,
        `${nom}, bascule « ${legende} »`,
      );
    }
  }
});

test("formulaire changé, la bascule traduit ce qui vient d'être tapé", () => {
  const changements = {
    "euros nets": { salaire: "3333", naissance: "1980-05-10", debut: "2001-01-01" },
    "euros bruts": { salaire: "5100" },
    "multiples du salaire moyen": { salaire: "0.8" },
    "deux métiers": { metier2_salaire: "4100" },
    "retraité, par la pension": { pension: "2210" },
  };
  for (const [nom, parametres] of Object.entries(SAISIES)) {
    const avant = liensDesBascules(rendre(contexte, "/simuler", parametres)[1]);
    const tapee = { ...parametres, ...changements[nom] };
    const apres = liensDesBascules(rendre(contexte, "/simuler", tapee)[1]);
    assert.equal(avant.length, apres.length, `${nom} : la page n'a plus les mêmes bascules`);
    avant.forEach(([legende, lien], rang) => {
      const refaite = requeteBasculee(contexte, formulaireDe(tapee), enObjet(lien));
      assert.equal(refaite, apres[rang][1], `${nom}, bascule « ${legende} »`);
      assert.notEqual(refaite, lien, `${nom}, bascule « ${legende} » : rien n'a changé`);
    });
  }
});

test("une saisie qui ne se lit pas n'est pas traduite", () => {
  // Un départ à dix-sept ans, que le modèle refuse : il n'y a rien à
  // traduire, et le script de la page envoie alors la saisie telle quelle,
  // pour que le refus s'affiche.
  const refusee = { ...BASE, liquidation: "1990-01-01" };
  const [[, lien]] = liensDesBascules(rendre(contexte, "/simuler", BASE)[1]);
  assert.throws(() => requeteBasculee(contexte, refusee, enObjet(lien)), /Départ à la retraite/);
});
