/**
 * Les points de retraite proportionnelle des exploitants agricoles de 1981 à
 * 1989, au revenu cadastral (action 131).
 *
 * Décret n° 80-808 du 14 octobre 1980, article 8 (LEGIARTI000006769209, en
 * vigueur du 1er janvier 1981 au 21 septembre 1990) : « le nombre de points
 * acquis chaque année par les intéressés en fonction des cotisations versées
 * en application du 1°, b, de l'article 1123 du Code rural est déterminé
 * suivant le barème annexé au présent décret ». Annexe (LEGIARTI000006769235),
 * « revenu cadastral servant de base aux cotisations » : « au plus égal à
 * 1 180 F », 15 points ; « de 1 180 F à 5 571 F », 30 ; « de 5 571 F à
 * 9 830 F », 45 ; « supérieur à 9 830 F », 60. Repris tel quel par R. 732-69
 * du code rural (LEGIARTI000006597478), « pour les années 1981 et suivantes ».
 * La première ligne et la dernière rangent chaque seuil dans la tranche du
 * bas ; 5 571 F, que deux lignes nomment, se lit de même.
 *
 * Le simulateur n'a pas le revenu cadastral : il le déduit du revenu, à
 * « 5,54 F de revenu professionnel pour 1 F de revenu cadastral » (décret
 * n° 92-793 du 14 août 1992, article 20, LEGIARTI000006776481, écrit pour la
 * cotisation de solidarité de 1992). C'est une convention, décidée par le
 * propriétaire le 20 novembre 2026.
 *
 * Chaque valeur attendue est lue dans l'annexe, ou posée à la main.
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { Contexte } from "../../moteur/js/contexte.js";
import {
  pointsAuRevenuCadastral, revenuCadastralDeduit, FICHE_DES_POINTS_AU_REVENU_CADASTRAL,
} from "../../moteur/js/droit/acquerir.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const fiches = new Contexte(paquet).simulateur().scenarioActuel.fichesDatees;
const version = (annee) => fiches.versionAuxDates(
  FICHE_DES_POINTS_AU_REVENU_CADASTRAL, { "revenu.annee": `${annee}-01-01` });

test("le barème vaut de 1981 à 1989, et ses chiffres sont ceux de la fiche", () => {
  for (const annee of [1952, 1980, 1990, 2025]) {
    assert.equal(version(annee).parametres.existe, false, String(annee));
  }
  for (const annee of [1981, 1985, 1989]) {
    const { parametres } = version(annee);
    assert.equal(parametres.existe, true, String(annee));
    assert.deepEqual(parametres.seuils_en_francs, [1180, 5571, 9830]);
    assert.deepEqual(parametres.points, [15, 30, 45, 60]);
    assert.equal(parametres.revenu_professionnel_pour_un_franc_cadastral, 5.54);
  }
});

test("l'annexe du décret n° 80-808 : quatre tranches, chaque seuil dans celle du bas", () => {
  const { parametres } = version(1981);
  const points = (revenuCadastral) => pointsAuRevenuCadastral(parametres, revenuCadastral);
  assert.equal(points(0), 15);
  assert.equal(points(1180), 15);
  assert.equal(points(1180.01), 30);
  assert.equal(points(5571), 30);
  assert.equal(points(5571.01), 45);
  assert.equal(points(9830), 45);
  assert.equal(points(9831), 60);
  assert.equal(points(1_000_000), 60);
});

test("le revenu cadastral déduit du revenu : 5,54 F de revenu pour 1 F cadastral", () => {
  const { parametres } = version(1985);
  // 30 000 F de revenu, soit 4 573,47 € : 30 000 / 5,54 = 5 415,16 F.
  const lu = revenuCadastralDeduit(parametres, 30000 / 6.55957);
  assert.ok(Math.abs(lu - 5415.16) < 0.005, String(lu));
  assert.equal(pointsAuRevenuCadastral(parametres, lu), 30);
  // 35 000 F : 6 317,69 F, la tranche de 45 points.
  assert.equal(pointsAuRevenuCadastral(
    parametres, revenuCadastralDeduit(parametres, 35000 / 6.55957)), 45);
  assert.equal(revenuCadastralDeduit(parametres, 0), 0);
});
