/**
 * L'exponentielle, le logarithme et la puissance du portage, au bit près de
 * la libm de Linux (`moteur/js/libm.js`).
 *
 * Le moteur Python tient ses `math.exp`, `math.log` et `**` de la glibc ; le
 * portage les tenait de V8, dont les résultats en diffèrent au dernier bit
 * une fois sur dix. Le pont du coût (action 161, étape 5) veut des témoins et
 * des agrégats identiques à l'octet, quel que soit le moteur qui les calcule :
 * le portage refait donc les trois fonctions de la glibc. Chaque valeur
 * attendue ci-dessous est celle que la glibc 2.39 rend sur x86_64 avec FMA,
 * la machine de GitHub ; les entrées ordinaires sont prises là où V8 s'en
 * écarte. `tests/test_libm.py` confronte en plus le portage à la libm de la
 * plateforme, sur un grand échantillon, quand elle est cette glibc.
 *
 *     node --test tests/js/libm.test.js
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { exp, fma, log, pow } from "../../moteur/js/libm.js";

const FONCTIONS = { exp, log, pow };

/** Les 64 bits d'un flottant, en hexadécimal, comme les écrit la glibc. */
function bits(x) {
  const vue = new DataView(new ArrayBuffer(8));
  vue.setFloat64(0, x);
  return vue.getBigUint64(0).toString(16).padStart(16, "0");
}

/** Un NaN n'a ni signe ni charge que JavaScript garde : il suffit qu'il en soit un. */
function verifier(obtenu, attendu, quoi) {
  if (attendu.startsWith("7ff8") || attendu.startsWith("fff8")) {
    assert.ok(Number.isNaN(obtenu), `${quoi} : ${obtenu}, NaN attendu`);
  } else {
    assert.equal(bits(obtenu), attendu, `${quoi} : ${obtenu}`);
  }
}

// Là où V8 s'écarte de la glibc : les survies, les forces de mortalité et les
// capitalisations que le moteur calcule.
const ORDINAIRES = [
  ["exp", [-0.32701009865636005], "3fe7130ef14903c9"],
  ["exp", [-0.3338194866582757], "3fe6eaf8b7d52bf3"],
  ["exp", [-0.3408578387915477], "3fe6c1d29dfc2501"],
  ["exp", [-0.4250672881604242], "3fe4eb525c1aea8b"],
  ["exp", [-0.13700793789830243], "3febe71f968b2597"],
  ["exp", [-0.21541443125444837], "3fe9cc73276bb443"],
  ["exp", [-0.3324153825071887], "3fe6f337160e0525"],
  ["exp", [-0.34630291782291417], "3fe6a22fd673f9ff"],
  ["log", [0.9662963917857821], "bfa18dc28fef2ebb"],
  ["log", [0.9516748520481193], "bfa95c3ce87097b7"],
  ["log", [0.9591955208541763], "bfa55481362f06bb"],
  ["log", [0.942235920492544], "bfae76baed054b98"],
  ["log", [0.9524856627310027], "bfa8ec9d470d34bf"],
  ["log", [0.5204707767658223], "bfe4e58d6c263289"],
  ["log", [0.61421501433311], "bfdf31baa90587d1"],
  ["log", [0.5869421819243263], "bfe10cef528af649"],
  ["pow", [1.0139462506649801, 18.5], "3ff4ac331cb21def"],
  ["pow", [1.0315319305380042, 49.5], "401298efcf6d3125"],
  ["pow", [1.021801745860685, 51.5], "40084ae0623d3e4d"],
  ["pow", [1.0153599345080566, 27.5], "3ff854e37b9bcfef"],
  ["pow", [1.0160070459230306, 56.5], "40039f5d17fe161b"],
  ["pow", [1.0029276229495256, 42.5], "3ff21ddc32903d89"],
  ["pow", [1.0187774380425423, 13.5], "3ff49164784b5a3b"],
  ["pow", [1.0244719302696306, 37.5], "4003cede4cb424df"],
];

// Les bornes, les valeurs spéciales et les chemins de la glibc que le moteur
// ne prend pas : le dépassement, les sous-normaux, les entiers négatifs.
const SPECIAUX = [
  ["exp", [0.0], "3ff0000000000000"],
  ["exp", [-0.0], "3ff0000000000000"],
  ["exp", [1.0], "4005bf0a8b145769"],
  ["exp", [-Infinity], "0000000000000000"],
  ["exp", [Infinity], "7ff0000000000000"],
  ["exp", [NaN], "7ff8000000000000"],
  ["exp", [1e-300], "3ff0000000000000"],
  ["exp", [-1e-18], "3ff0000000000000"],
  ["exp", [709.7], "7fed75ae7a50ee14"],
  ["exp", [710.0], "7ff0000000000000"],
  ["exp", [-708.5], "000e6cf6d08897ac"],
  ["exp", [-740.0], "0000000000000055"],
  ["exp", [-745.2], "0000000000000000"],
  ["exp", [-800.0], "0000000000000000"],
  ["exp", [600.0], "76088a122d234b39"],
  ["exp", [-600.0], "09d4dd4d0d12c071"],
  ["log", [1.0], "0000000000000000"],
  ["log", [0.0], "fff0000000000000"],
  ["log", [-0.0], "fff0000000000000"],
  ["log", [-1.0], "fff8000000000000"],
  ["log", [Infinity], "7ff0000000000000"],
  ["log", [NaN], "7ff8000000000000"],
  ["log", [5e-324], "c0874385446d71c3"],
  ["log", [2.2250738585072014e-308], "c086232bdd7abcd2"],
  ["log", [1e-310], "c0864e69394d9508"],
  ["log", [1.7976931348623157e+308], "40862e42fefa39ef"],
  ["log", [0.9375], "bfb08598b59e3a07"],
  ["log", [1.064697265625], "3fb00c7c14184ec5"],
  ["log", [1.0000000000000002], "3cafffffffffffff"],
  ["log", [0.9999999999999999], "bca0000000000000"],
  ["pow", [2.0, 0.0], "3ff0000000000000"],
  ["pow", [NaN, 0.0], "3ff0000000000000"],
  ["pow", [1.0, NaN], "3ff0000000000000"],
  ["pow", [NaN, 1.0], "7ff8000000000000"],
  ["pow", [0.0, -1.0], "7ff0000000000000"],
  ["pow", [-0.0, -1.0], "fff0000000000000"],
  ["pow", [-0.0, 3.0], "8000000000000000"],
  ["pow", [0.0, 2.5], "0000000000000000"],
  ["pow", [-8.0, 0.3333333333333333], "fff8000000000000"],
  ["pow", [-2.0, 3.0], "c020000000000000"],
  ["pow", [-2.0, 2.0], "4010000000000000"],
  ["pow", [2.0, 1024.0], "7ff0000000000000"],
  ["pow", [0.5, 1100.0], "0000000000000000"],
  ["pow", [2.0, -1074.0], "0000000000000001"],
  ["pow", [2.0, -1075.0], "0000000000000000"],
  ["pow", [Infinity, -1.0], "0000000000000000"],
  ["pow", [-Infinity, 3.0], "fff0000000000000"],
  ["pow", [0.5, Infinity], "0000000000000000"],
  ["pow", [2.0, -Infinity], "0000000000000000"],
  ["pow", [-1.0, Infinity], "3ff0000000000000"],
  ["pow", [1.0000000001, 1e-70], "3ff0000000000000"],
  ["pow", [0.9999999, 1e-70], "3ff0000000000000"],
  ["pow", [3.0, 1e+19], "7ff0000000000000"],
  ["pow", [5e-324, 0.5], "1e60000000000000"],
  ["pow", [-1.5, 1e+20], "7ff0000000000000"],
  ["pow", [10.0, -2.0], "3f847ae147ae147b"],
  ["pow", [1.1, 0.5], "3ff0c7ebc96a56f6"],
];

// La multiplication-addition fusionnée, arrondie une seule fois : la valeur
// attendue est l'arrondi de a × b + c calculé en rationnels exacts. Des
// annulations, le `z × 1/c − 1` du logarithme, des polynômes, et des sommes
// tout près d'un milieu entre deux flottants.
const FUSIONNEES = [
  [1.2773151047993123, 1.3254996035399855, -1.6930806650071235, "3c82ee1fa914d9d8"],
  [0.8443412884529107, 1.8492072032569222, -1.5613619926143532, "3c85efe2dbdceec0"],
  [1.4552941053005857, 1.2198976468396425, -1.7753098545157875, "bc999fe6893a77b4"],
  [1.6316977097618777, 1.5514974340883674, -2.531574809903419, "bcaaefdf989b62a0"],
  [1.319568494981038, 0.75779856770135, -1.0, "bf013daf7ce4c971"],
  [0.7344034829912144, 1.362071019043551, -1.0, "3f344be960918080"],
  [1.03490583065958, 0.9665149337980393, -1.0, "3f3082dbcf2ab0b4"],
  [0.7522826009896769, 1.329235639792658, -1.0, "bf04875f17c2c1b3"],
  [0.0006288903221860938, -0.9801956700771661, 0.6732743935803267, "3fe58669fb617285"],
  [0.006184092875203681, 0.7777715491023478, 0.023545919001922044, "3f9d0948dc8f49d7"],
  [0.005298975015566542, -0.9927168418316588, -0.16777990171714596, "bfc6262f1b2cb63d"],
  [-0.006088308502084514, 0.5423871244562062, 0.027884000351090066, "3f992bf758509f29"],
  [1.0000011548399925, 1.4902606687407016, -0.49675412991777373, "3fefcad1d58995e3"],
  [1.0000056102871895, 1.3484167528712763, -0.44947477262550367, "3fecc431d6336dc3"],
  [1.000002034008503, 1.123052056303515, -0.37435144686698224, "3fe7f55fc560410d"],
  [1.0000023394823074, 1.087147363977603, -0.3623833024465422, "3fe73149bc27f5c5"],
];

test("exp, log et pow rendent la glibc là où V8 s'en écarte", () => {
  for (const [nom, entrees, attendu] of ORDINAIRES) {
    verifier(FONCTIONS[nom](...entrees), attendu, `${nom}(${entrees.join(", ")})`);
  }
});

test("exp, log et pow suivent la glibc aux bornes et sur les valeurs spéciales", () => {
  for (const [nom, entrees, attendu] of SPECIAUX) {
    verifier(FONCTIONS[nom](...entrees), attendu, `${nom}(${entrees.join(", ")})`);
  }
});

test("la multiplication-addition fusionnée n'arrondit qu'une fois", () => {
  for (const [a, b, c, attendu] of FUSIONNEES) {
    verifier(fma(a, b, c), attendu, `fma(${a}, ${b}, ${c})`);
  }
  // Les valeurs spéciales suivent la multiplication et l'addition ordinaires.
  assert.ok(Number.isNaN(fma(Infinity, 0.0, 1.0)));
  assert.equal(fma(Infinity, 2.0, 1.0), Infinity);
  assert.equal(fma(2.0, 3.0, -Infinity), -Infinity);
  assert.equal(fma(0.0, 5.0, 1.5), 1.5);
});
