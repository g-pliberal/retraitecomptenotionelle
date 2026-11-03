/**
 * La base forfaitaire des cultes, au SMIC de chaque mois (action 130, décision
 * 13 du propriétaire, 3 novembre 2026).
 *
 * R. 721-29 et R. 721-30 du code de la sécurité sociale, rédaction du 21 juin
 * 1998 : la base « est égale, par mois, à 169 fois le montant du salaire
 * minimum de croissance » ; rédaction du 26 février 2004, puis R. 382-89 et
 * R. 382-90 depuis le 1er novembre 2006 : « par mois, à la valeur horaire du
 * salaire minimum de croissance en vigueur, multipliée par le nombre légal
 * d'heures de travail mensuel en vigueur ». La caisse le fait : « A compter du
 * 1er novembre 2024, le montant brut du [SMIC] […] est porté à 1 802 €
 * mensuels », et les assiettes forfaitaires de la vieillesse et de la retraite
 * complémentaire « sont modifiées à compter de l'échéance du 15 décembre
 * 2024 » (circulaire de la CAVIMAC n° 2025/01 du 14 janvier 2025).
 *
 * Chaque valeur attendue est posée à la main, depuis les décrets et arrêtés
 * qui relèvent le SMIC, lus dans l'index JORF du dépôt (note
 * `docs/feuille_de_route/130/2026-11-03-base-des-cultes-au-smic-du-mois.md`).
 * Même arithmétique que `tests/test_cultes_smic_du_mois.py`.
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { Contexte } from "../../moteur/js/contexte.js";
import { assietteDeReference } from "../../moteur/js/droit/liquider.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));

/** Le SMIC horaire de chaque mois, posé à la main : [mois, valeur] par relèvement. */
const SMIC_DES_MOIS = {
  // Décret n° 98-518 (40,22 F au 1er juillet 1998), décret n° 99-546 (40,72 F
  // au 1er juillet 1999) : en euros, ceux de `macro/smic_horaire.csv`.
  1999: [[1, 6.131499], [7, 6.207724]],
  // Décret n° 2006-751 (8,27 € au 1er juillet 2006), n° 2007-1052 (8,44 € au
  // 1er juillet 2007).
  2007: [[1, 8.27], [7, 8.44]],
  // Arrêté du 25 avril 2008 (8,63 € au 1er mai), décret n° 2008-617 (8,71 € au
  // 1er juillet) : deux relèvements dans l'année.
  2008: [[1, 8.44], [5, 8.63], [7, 8.71]],
  // Décret n° 2015-1688 : 9,67 € au 1er janvier 2016, rien d'autre.
  2016: [[1, 9.67]],
  // Décret n° 2021-1741 (10,57 € au 1er janvier), arrêtés du 19 avril (10,85 €
  // au 1er mai) et du 29 juillet 2022 (11,07 € au 1er août).
  2022: [[1, 10.57], [5, 10.85], [8, 11.07]],
  // Décret n° 2023-1216 (11,65 € au 1er janvier), n° 2024-951 (11,88 € au
  // 1er novembre 2024).
  2024: [[1, 11.65], [11, 11.88]],
};

/** La moyenne des douze mois, posée à la main pour chaque année. */
const MOYENNES = {
  1999: (6 * 6.131499 + 6 * 6.207724) / 12,
  2007: (6 * 8.27 + 6 * 8.44) / 12,
  2008: (4 * 8.44 + 2 * 8.63 + 6 * 8.71) / 12,
  2016: 9.67,
  2022: (4 * 10.57 + 3 * 10.85 + 5 * 11.07) / 12,
  2024: (10 * 11.65 + 2 * 11.88) / 12,
};

/** La base d'une année entière, en euros, posée à la main. */
const BASES = {
  // 169 heures par mois : 169 × (6 × 40,22 + 6 × 40,72) F = 82 073,16 F.
  1999: 12511.97,
  // 151,67 heures par mois, 1 820 par an : 1 820 / 12 × (6 × 8,27 + 6 × 8,44).
  2007: 15206.10,
  // 1 820 / 12 × (4 × 8,44 + 2 × 8,63 + 6 × 8,71) = 1 820 / 12 × 103,28.
  2008: 15664.13,
  // 1 820 × 9,67.
  2016: 17599.40,
  // 1 820 / 12 × (4 × 10,57 + 3 × 10,85 + 5 × 11,07) = 1 820 / 12 × 130,18.
  2022: 19743.97,
  // 1 820 / 12 × (10 × 11,65 + 2 × 11,88) = 1 820 / 12 × 140,26.
  2024: 21272.77,
};

test("les mois posés à la main font la moyenne posée à la main", () => {
  for (const [annee, releves] of Object.entries(SMIC_DES_MOIS)) {
    let somme = 0;
    for (let mois = 1; mois <= 12; mois += 1) {
      somme += releves.filter(([debut]) => debut <= mois).at(-1)[1];
    }
    assert.ok(Math.abs(somme / 12 - MOYENNES[annee]) < 1e-12, annee);
  }
});

test("le SMIC horaire des mois est la moyenne des SMIC en vigueur chaque mois", () => {
  const macro = new Contexte(paquet).simulateur().macro;
  for (const [annee, moyenne] of Object.entries(MOYENNES)) {
    assert.ok(Math.abs(macro.smicHoraireDesMois(Number(annee)) - moyenne) < 1e-12, annee);
  }
  // Une année sans relèvement en cours d'année, même projetée : son SMIC de
  // janvier.
  for (const annee of [2016, 2017, 2040]) {
    assert.equal(macro.smicHoraireDesMois(annee), macro.smic_horaire.valeur(annee), annee);
  }
});

test("la base forfaitaire des cultes suit le SMIC de chaque mois", () => {
  const simulateur = new Contexte(paquet).simulateur();
  // Né le 1er janvier 1958, ministre du culte de 25 à 67 ans : 1983 à 2024
  // entières.
  const carriere = simulateur.carriereSimple({
    annee_naissance: 1958, sexe: "H", affiliation: "ministre_du_culte", age_debut: 25,
    age_liquidation: 67, niveau_salaire: 1.0, jour_naissance: 1,
  });
  const cavimac = simulateur.catalogue.obtenir("cavimac");
  for (const [annee, base] of Object.entries(BASES)) {
    const ligne = carriere.lignes.find((l) => l.annee === Number(annee));
    assert.equal(ligne.fraction_annee, 1.0, annee);
    const periode = cavimac.periode(Number(annee));
    assert.equal(periode.smic_du_mois, true, annee);
    const calculee = assietteDeReference(simulateur.scenarioActuel, periode, ligne);
    assert.ok(Math.abs(calculee - base) < 0.01, `${annee} : ${calculee} contre ${base}`);
  }
});

test("le forfait d'avant 1998 et l'assiette plancher gardent le SMIC de janvier", () => {
  const simulateur = new Contexte(paquet).simulateur();
  // Avant 1998, la cotisation des cultes est fixée par arrêté, sans SMIC ; la
  // complémentaire agricole n'est pas lue ici.
  assert.ok(!simulateur.catalogue.obtenir("cavimac").periode(1997).smic_du_mois);
  assert.ok(!simulateur.catalogue.obtenir("msa_rco").periode(2007).smic_du_mois);
  // L'Arrco des cultes prélève sur la même assiette forfaitaire (circulaire
  // n° 2025/01) : elle suit le SMIC de chaque mois.
  for (const annee of [2006, 2019, 2026]) {
    assert.equal(simulateur.catalogue.obtenir("arrco_cultes").periode(annee).smic_du_mois,
      true, annee);
  }
});
