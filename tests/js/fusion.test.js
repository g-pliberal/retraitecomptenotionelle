/**
 * La fusion des régimes, sur un catalogue posé à la main (action 161, les
 * lignes du portage qu'aucun test n'exécutait).
 *
 * La source est `docs/methodologie.md`, § 7 : le régime unique retient, par
 * paramètre, le cas le plus défavorable — l'âge d'ouverture et l'âge du taux
 * plein les plus élevés, la durée la plus longue, le salaire de référence le
 * moins avantageux —, et son taux fait exception : la somme des taux du statut
 * pivot, « modifiable par `RegleFusion.critere_taux` ». Le moteur du site ne
 * fusionne que sous la règle par défaut (`simulateur.js`) ; les autres
 * critères ne tournaient qu'en Python, pour la prose (`mesures_prose.py`,
 * « fusion?critere=… ») et pour l'étude `scripts/solde_fusion.py`.
 *
 * Aucune valeur attendue ne vient du moteur : le catalogue ci-dessous tient
 * en sept régimes dont chaque taux est rond, et chaque attendu se pose de
 * tête, écrit en commentaire à côté de son assertion.
 *
 *     node --test tests/js/fusion.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { CritereTaux, REGLE_FUSION_DEFAUT, fusionner } from "../../moteur/js/fusion.js";
import { CatalogueRegimes } from "../../moteur/js/regimes.js";
import { Fiabilite } from "../../moteur/js/serie.js";

const periode = (champs) => ({
  debut: 2000, fin: null, assiette: "plafonnee", age_ouverture: 62.0, age_taux_plein: 67.0,
  duree_requise_trimestres: null, salaire_reference: "sans_objet",
  taux_cotisation_retraite: 0.0, taux_cotisation_deplafonnee: 0.0, part_salariale: 0.0,
  part_salariale_deplafonnee: 0.0, avantages_non_contributifs: [], ...champs,
});

const regime = (code, famille, champs, ...periodes) => ({
  code, famille, creation: 1950, fermeture: null, extinction: null, hors_repartition: false,
  fiabilite: Fiabilite.CERTIFIEE, periodes, ...champs,
});

/** La tranche 1 de la complémentaire : 8 % en tout, dont 40 % au salarié. */
const TRANCHE_1 = periode({
  assiette: "tranche_1", taux_cotisation_retraite: 0.08, part_salariale: 0.4,
});
/** Sa tranche 2, écrite la première : 20 % au-dessus du plafond. */
const TRANCHE_2 = periode({
  assiette: "tranche_2", taux_cotisation_retraite: 0.20, part_salariale: 0.4,
});

const REGIMES = (...tranches) => [
  // 16 % plafonnés et 2 % déplafonnés : 18 % en tout ; le salarié en porte
  // 16 × 0,4 + 2 × 0,2 = 6,8 %.
  regime("regime_general", "base", {}, periode({
    duree_requise_trimestres: 172, salaire_reference: "25_meilleures_annees",
    taux_cotisation_retraite: 0.16, taux_cotisation_deplafonnee: 0.02,
    part_salariale: 0.4, part_salariale_deplafonnee: 0.2,
  })),
  regime("agirc_arrco", "complementaire", { fiabilite: Fiabilite.HAUTE }, ...tranches),
  // Le taux le plus élevé, 80 %, dont un dixième au fonctionnaire ; l'âge du
  // taux plein le plus élevé ; le salaire de référence le plus avantageux.
  regime("fonction_publique", "fonction_publique", {}, periode({
    age_taux_plein: 68.0, duree_requise_trimestres: 168, salaire_reference: "derniers_6_mois",
    taux_cotisation_retraite: 0.80, part_salariale: 0.1,
  })),
  // L'âge d'ouverture le plus élevé et la durée la plus longue ; 10 %, que
  // l'indépendant porte seul ; la fiabilité la plus basse des régimes fusionnés.
  regime("independants", "base", { fiabilite: Fiabilite.MOYENNE }, periode({
    age_ouverture: 64.0, duree_requise_trimestres: 176, salaire_reference: "10_meilleures_annees",
    taux_cotisation_retraite: 0.10, part_salariale: 1.0,
  })),
  // Trois régimes que la fusion ne lit pas, chacun plus défavorable que tous
  // les autres : éteint avant la bascule, en capitalisation, hors répartition.
  regime("eteint", "complementaire", { extinction: 2019, fiabilite: Fiabilite.ESTIMEE }, periode({
    age_ouverture: 70.0, age_taux_plein: 75.0, duree_requise_trimestres: 200,
    salaire_reference: "carriere_entiere", taux_cotisation_retraite: 0.90, part_salariale: 1.0,
  })),
  regime("capitalise", "additionnel_capitalise", { fiabilite: Fiabilite.ESTIMEE }, periode({
    age_ouverture: 70.0, age_taux_plein: 75.0, duree_requise_trimestres: 200,
    salaire_reference: "carriere_entiere", taux_cotisation_retraite: 0.01, part_salariale: 1.0,
  })),
  regime("a_part", "base", { hors_repartition: true, fiabilite: Fiabilite.ESTIMEE }, periode({
    age_ouverture: 70.0, age_taux_plein: 75.0, duree_requise_trimestres: 200,
    salaire_reference: "carriere_entiere", taux_cotisation_retraite: 0.95, part_salariale: 1.0,
  })),
];

/** Le catalogue entier : la complémentaire y a ses deux tranches. */
const CATALOGUE = new CatalogueRegimes({ regimes: REGIMES(TRANCHE_2, TRANCHE_1) });
/** Le même, chaque régime n'y ayant qu'une période. */
const UNE_PERIODE = new CatalogueRegimes({ regimes: REGIMES(TRANCHE_1) });

const proche = (obtenu, attendu, quoi) => assert.ok(
  Math.abs(obtenu - attendu) < 1e-12, `${quoi} : ${obtenu}, attendu ${attendu}`);

const sous = (critere, champs = {}) => ({ ...REGLE_FUSION_DEFAUT, critere_taux: critere, ...champs });

test("le régime unique retient, par paramètre, le plus défavorable des régimes vivants en répartition", () => {
  const fusionne = fusionner(CATALOGUE, 2030);
  assert.equal(fusionne.annee_bascule, 2030);
  assert.equal(fusionne.age_ouverture, 64.0);
  assert.equal(fusionne.origines.age_ouverture, "independants");
  assert.equal(fusionne.age_taux_plein, 68.0);
  assert.equal(fusionne.origines.age_taux_plein, "fonction_publique");
  assert.equal(fusionne.duree_requise_trimestres, 176);
  assert.equal(fusionne.origines.duree_requise_trimestres, "independants");
  // Des trois salaires de référence qui en sont un, les vingt-cinq meilleures
  // années sont le moins avantageux ; « sans objet » n'en est pas un.
  assert.equal(fusionne.salaire_reference, "25_meilleures_annees");
  assert.equal(fusionne.origines.salaire_reference, "regime_general");
  assert.equal(fusionne.assiette, "deplafonnee");
  assert.deepEqual(fusionne.avantages_non_contributifs, []);
  assert.deepEqual(fusionne.regimes_fusionnes,
    ["agirc_arrco", "fonction_publique", "independants", "regime_general"]);
  assert.equal(fusionne.fiabilite, Fiabilite.MOYENNE);
});

test("le taux par défaut somme ceux du statut pivot, la complémentaire à sa tranche 1", () => {
  const fusionne = fusionner(CATALOGUE, 2030);
  // 18 % au régime général et 8 % à la tranche 1 ; 6,8 % et 8 × 0,4 = 3,2 % au salarié.
  proche(fusionne.taux_cotisation_retraite, 0.26, "le taux");
  proche(fusionne.taux_cotisation_salarie, 0.10, "la part du salarié");
});

test("« le plus élevé » retient le taux de la caisse la plus chère, à la répartition moyenne", () => {
  const fusionne = fusionner(CATALOGUE, 2030, sous(CritereTaux.LE_PLUS_ELEVE));
  assert.equal(fusionne.taux_cotisation_retraite, 0.80);
  assert.equal(fusionne.origines.taux_cotisation_retraite, "fonction_publique");
  // Cinq périodes fusionnées : (0,4 + 0,4 + 0,4 + 0,1 + 1) / 5 = 0,46 au salarié.
  proche(fusionne.taux_cotisation_salarie, 0.80 * 0.46, "la part du salarié");
  // Le critère ne change que le taux.
  assert.equal(fusionne.age_ouverture, 64.0);
  assert.equal(fusionne.duree_requise_trimestres, 176);
});

test("« le plus faible » retient le taux le plus bas, à la même répartition moyenne", () => {
  const fusionne = fusionner(CATALOGUE, 2030, sous(CritereTaux.LE_PLUS_FAIBLE));
  assert.equal(fusionne.taux_cotisation_retraite, 0.08);
  assert.equal(fusionne.origines.taux_cotisation_retraite, "agirc_arrco");
  proche(fusionne.taux_cotisation_salarie, 0.08 * 0.46, "la part du salarié");
});

test("la moyenne est celle des taux, et celle des parts que chaque salarié porte", () => {
  const fusionne = fusionner(UNE_PERIODE, 2030, sous(CritereTaux.MOYENNE_PONDEREE));
  // (18 + 8 + 80 + 10) / 4 = 29 % ; (6,8 + 3,2 + 8 + 10) / 4 = 7 % au salarié.
  proche(fusionne.taux_cotisation_retraite, 0.29, "le taux");
  proche(fusionne.taux_cotisation_salarie, 0.07, "la part du salarié");
  assert.equal(fusionne.origines.taux_cotisation_retraite, "moyenne des régimes");
});

test("un régime pivot que le catalogue n'a pas est sauté, et aucun pivot est un refus", () => {
  const fusionne = fusionner(CATALOGUE, 2030,
    sous(CritereTaux.SOMME_PIVOT, { regimes_pivot: ["inconnu", "regime_general"] }));
  proche(fusionne.taux_cotisation_retraite, 0.18, "le taux");
  proche(fusionne.taux_cotisation_salarie, 0.068, "la part du salarié");
  assert.match(fusionne.origines.taux_cotisation_retraite, /^somme regime_general /);
  assert.throws(
    () => fusionner(CATALOGUE, 2030, sous(CritereTaux.SOMME_PIVOT, { regimes_pivot: ["inconnu"] })),
    /aucun régime pivot exploitable en 2030/);
});

test("une bascule d'avant tous les régimes est refusée", () => {
  assert.throws(() => fusionner(CATALOGUE, 1949), /aucun régime vivant en 1949 : fusion impossible/);
});

// -- le catalogue des fiches --------------------------------------------------
// Les sept tests de `tests/test_moteur.py` qui fusionnaient le catalogue réel
// du moteur Python, éprouvés sur celui du site (action 161, quatrième vague).
// Les attendus viennent des fiches et de `docs/methodologie.md`, § 7 : des
// bornes que chaque régime vivant doit respecter, la carrière entière comme
// salaire de référence le moins avantageux, la somme des taux du statut
// pivot relue période par période.

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur", "donnees.json"), "utf8"));
const FICHES = new CatalogueRegimes(paquet);

/** Comme `pytest.approx` : 10⁻⁶ relatif, 10⁻¹² absolu. */
const approx = (lu, attendu, quoi) => assert.ok(
  Math.abs(lu - attendu) <= Math.max(1e-12, 1e-6 * Math.abs(attendu)),
  `${quoi} : ${lu} au lieu de ${attendu}`);

/** Les périodes de 2026 des régimes vivants en répartition. */
const repartition2026 = () => [...FICHES]
  .filter((regime) => !regime.hors_repartition && regime.vivant(2026))
  .flatMap((regime) => regime.periodesActives(2026));

test("les fiches : le régime unique retient les âges les plus élevés", () => {
  const fusionne = fusionner(FICHES, 2026);
  const periodes = repartition2026();
  assert.ok(periodes.length > 0);
  for (const periode of periodes) {
    assert.ok(periode.age_ouverture <= fusionne.age_ouverture);
    assert.ok(periode.age_taux_plein <= fusionne.age_taux_plein);
  }
});

test("les fiches : la fusion supprime tous les avantages non contributifs", () => {
  assert.deepEqual([...fusionner(FICHES, 2026).avantages_non_contributifs], []);
});

test("les fiches : le salaire de référence le moins avantageux est la carrière entière", () => {
  assert.equal(fusionner(FICHES, 2026).salaire_reference, "carriere_entiere");
});

test("les fiches : l'assiette est déplafonnée", () => {
  assert.equal(fusionner(FICHES, 2026).assiette, "deplafonnee");
});

test("les fiches : le taux somme le statut pivot, cotisation déplafonnée comprise", () => {
  // L'assiette du régime unifié est déplafonnée : ce que le régime général
  // prélève sur la totalité du salaire y porte sur la même base que la part
  // plafonnée, et s'y ajoute. L'omettre faisait perdre au compte notionnel,
  // après la bascule, ce que la séparation des deux taux y portait avant elle.
  const fusionne = fusionner(FICHES, 2026);
  const base = FICHES.obtenir("regime_general").periode(2026);
  const tranches = FICHES.obtenir("agirc_arrco").periodesActives(2026);
  const complementaire = tranches.reduce((retenue, p) =>
    p.bornesAssietteEnPass()[0] < retenue.bornesAssietteEnPass()[0] ? p : retenue);
  const attendu = base.taux_cotisation_retraite + base.taux_cotisation_deplafonnee
    + complementaire.taux_cotisation_retraite + complementaire.taux_cotisation_deplafonnee;
  approx(fusionne.taux_cotisation_retraite, attendu, "le taux");
  assert.ok(base.taux_cotisation_deplafonnee > 0,
    "sans déplafonnée au régime général, ce test ne prouve plus rien");
});

test("les fiches : la capitalisation n'est pas fusionnée", () => {
  assert.ok(!fusionner(FICHES, 2026).regimes_fusionnes.includes("rafp"));
});

test("les fiches : « le plus élevé » retient le taux de la caisse la plus chère", () => {
  const fusionne = fusionner(FICHES, 2026, sous(CritereTaux.LE_PLUS_ELEVE));
  const maxima = Math.max(...repartition2026().map(
    (p) => p.taux_cotisation_retraite + p.taux_cotisation_deplafonnee));
  approx(fusionne.taux_cotisation_retraite, maxima, "le taux");
});
