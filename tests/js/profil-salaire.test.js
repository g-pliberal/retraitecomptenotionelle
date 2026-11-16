/**
 * Le profil de rémunération, sur les tables des fiches du site
 * (`moteur/donnees.json`) : action 161, quatrième vague, les tests de
 * `profil_salaire` et `_facteur_secteur` que `test_moteur.py` tenait sur le
 * module Python, éprouvés sur son portage, `profilSalaire` et
 * `facteurSecteur` de `moteur/js/carriere.js`.
 *
 * Les attendus sont ceux que l'INSEE et Eurostat publient, aux tolérances du
 * Python ; celui de l'interpolation se pose à la main, sur les décimales
 * publiées, écrit en commentaire à côté de son assertion.
 *
 *     node --test tests/js/profil-salaire.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import {
  ANNEE_FORME_CATEGORIE, facteurSecteur, profilSalaire,
} from "../../moteur/js/carriere.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur", "donnees.json"), "utf8"));

const proche = (valeur, attendu, ecart, message) =>
  assert.ok(Math.abs(valeur - attendu) <= ecart,
    `${message ?? ""} ${valeur} au lieu de ${attendu} ± ${ecart}`);

test("le profil salarial suit la génération", () => {
  // La prime à l'âge n'a pas été la même à toutes les époques : l'INSEE la
  // mesure à 1,19 entre les 51-60 ans et les 26-30 ans en 1962, 1,47 en 2000,
  // 1,35 en 2024. Les pentes observées : ×1,25 pour la génération 1940,
  // ×1,38 pour celle de 1960.
  const pente = (generation, profil = "ascendant") =>
    profilSalaire(paquet, profil, 55, generation + 55)
    / profilSalaire(paquet, profil, 26, generation + 26);

  assert.ok(pente(1940) < pente(1950) && pente(1950) < pente(1960));
  proche(pente(1940), 1.25, 0.05, "génération 1940 :");
  proche(pente(1960), 1.38, 0.05, "génération 1960 :");
  // Le profil plat ne doit rien à la génération : la convention qui ne
  // suppose rien.
  proche(pente(1940, "plat"), 1.0, 1e-12);
  proche(pente(1975, "plat"), 1.0, 1e-12);
});

test("le profil salarial ne doit rien à une droite inventée", () => {
  // L'INSEE observe ×1,30 de 26 à 55 ans pour un employé et ×1,86 pour un
  // cadre en 2024, l'année de la forme, où la modulation vaut un.
  const pente = (profil) =>
    profilSalaire(paquet, profil, 54.5, ANNEE_FORME_CATEGORIE)
    / profilSalaire(paquet, profil, 26, ANNEE_FORME_CATEGORIE);

  proche(pente("ascendant"), 1.30, 0.02, "ascendant :");
  proche(pente("fortement_ascendant"), 1.86, 0.03, "fortement ascendant :");
});

test("le facteur de secteur ne touche que les régimes spéciaux", () => {
  // L'enquête européenne ventile le salaire par âge et par section :
  // l'électricité-gaz est le champ des IEG, les transports celui de la SNCF.
  proche(facteurSecteur(paquet, "agent_ieg"), 1.38, 0.03, "IEG :");
  proche(facteurSecteur(paquet, "agent_sncf"), 0.93, 0.02, "SNCF :");
  // Tout le reste est à un, y compris les mines et les spectacles, où le
  // rapport ne tient pas d'une vague à l'autre.
  for (const affiliation of [
    "salarie_prive_non_cadre", "salarie_prive_cadre", "fonctionnaire_etat",
    "contractuel_public", "artisan", "mineur", "personnel_opera",
    "personnel_comedie_francaise"]) {
    assert.equal(facteurSecteur(paquet, affiliation), 1.0, affiliation);
  }
});

test("le profil s'interpole entre les valeurs publiées", () => {
  // Une profession intermédiaire de 33 ans, l'année de la forme, entre les
  // milieux de tranche 26 et 34,5 ans :
  // 0,7909 + (0,9922 − 0,7909) × (33 − 26) / (34,5 − 26)
  //   = 0,956 676 470 588 235 29…, dont le flottant le plus proche s'écrit
  // 0.9566764705882352. Le Python, qui multipliait avant de diviser, rendait
  // le flottant d'après, …354 (action 161, étape 6).
  assert.equal(
    profilSalaire(paquet, "profession_intermediaire", 33, ANNEE_FORME_CATEGORIE),
    0.9566764705882352);
});
