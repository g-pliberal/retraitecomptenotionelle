/**
 * Le moteur JavaScript contre les cas-témoins du modèle Python.
 *
 * Le Python de ``src/`` reste la référence : il a été écrit contre les sources,
 * testé et documenté. Ce fichier vérifie que le JavaScript qui fait tourner le
 * site en retrouve les chiffres — et le HTML — sur un jeu de cas figé par
 * ``scripts/construire_temoins.py``. Toute divergence, sur n'importe quelle
 * valeur de l'un des cas, fait échouer le test.
 *
 *     node --test tests/js/*.test.js
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { Saisie } from "../../moteur/js/saisie.js";
import { Contexte } from "../../moteur/js/contexte.js";
import { rendre } from "../../moteur/js/pages.js";
import { Affiliations } from "../../moteur/js/regimes.js";
import {
  complementMinimum, majorationOuverte, plancherDuRegime, selonLaRegle,
} from "../../moteur/js/droit/completer.js";
import { appels } from "../../moteur/js/droit/liquidation.js";
import { moyenneSelonLaRegle } from "../../moteur/js/droit/liquider.js";
import * as ouvrir from "../../moteur/js/droit/ouvrir.js";
import { DonneesMacro } from "../../moteur/js/macro.js";
import { MinimumVieillesse } from "../../moteur/js/regimes.js";
import {
  avantLAspa, COUPLE, DEUX_ALLOCATAIRES, PERSONNE_SEULE,
} from "../../moteur/js/droit/foyer.js";
import { AnneeCarriere, limiterChomageNonIndemnise } from "../../moteur/js/carriere.js";
import * as gabarit from "../../moteur/js/gabarit.js";
import { Fiabilite, SerieAnnuelle } from "../../moteur/js/serie.js";
import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { DonneesMortalite } from "../../moteur/js/mortalite.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");

const lire = (chemin) => JSON.parse(readFileSync(join(RACINE, chemin), "utf8"));

const paquet = lire("moteur/donnees.json");
const temoinsSimulations = lire("tests/temoins/simulations.json");
const temoinsPages = lire("tests/temoins/pages.json");

/**
 * Tolérance relative. Python et JavaScript s'appuient sur la libm de leur
 * plateforme pour ``exp`` : deux implémentations correctes peuvent différer
 * d'un ulp, soit 1e-16 en relatif. On accepte 1e-9, six ordres de grandeur
 * au-dessus du bruit et six en dessous de ce qui se verrait à l'affichage.
 */
const TOLERANCE = 1e-9;

function comparer(obtenu, attendu, chemin, ecarts) {
  if (attendu === null) {
    // Le témoin écrit ``null`` là où Python produit NaN — écart non défini.
    if (!(obtenu === null || Number.isNaN(obtenu))) {
      ecarts.push(`${chemin} : attendu null, obtenu ${obtenu}`);
    }
    return;
  }
  if (typeof attendu === "number") {
    if (typeof obtenu !== "number") {
      ecarts.push(`${chemin} : attendu un nombre, obtenu ${typeof obtenu}`);
      return;
    }
    const ecart = Math.abs(obtenu - attendu);
    const relatif = attendu === 0 ? ecart : ecart / Math.abs(attendu);
    if (relatif > TOLERANCE) {
      ecarts.push(`${chemin} : python=${attendu} js=${obtenu} (écart ${relatif.toExponential(2)})`);
    }
    return;
  }
  if (Array.isArray(attendu)) {
    if (!Array.isArray(obtenu) || obtenu.length !== attendu.length) {
      ecarts.push(`${chemin} : tableau de ${attendu.length} attendu, obtenu ${
        Array.isArray(obtenu) ? obtenu.length : typeof obtenu}`);
      return;
    }
    attendu.forEach((valeur, i) => comparer(obtenu[i], valeur, `${chemin}[${i}]`, ecarts));
    return;
  }
  if (attendu !== null && typeof attendu === "object") {
    const clesAttendues = Object.keys(attendu).sort();
    const clesObtenues = Object.keys(obtenu ?? {}).sort();
    assert.deepEqual(clesObtenues, clesAttendues, `clés différentes en ${chemin}`);
    for (const cle of clesAttendues) {
      comparer(obtenu[cle], attendu[cle], `${chemin}.${cle}`, ecarts);
    }
    return;
  }
  if (obtenu !== attendu) {
    ecarts.push(`${chemin} : python=${JSON.stringify(attendu)} js=${JSON.stringify(obtenu)}`);
  }
}

test("les simulations retrouvent les chiffres du modèle Python", () => {
  const contexte = new Contexte(paquet);
  const ecarts = [];
  let cas = 0;
  for (const [nom, temoin] of Object.entries(temoinsSimulations)) {
    const saisie = Saisie.depuisRequete(temoin.requete, false, paquet.presomptions);
    const avant = appels();
    const obtenu = contexte.simuler(saisie).dictionnaire();
    // Le témoin déclare ses appels de `liquider`, liquidations d'essai
    // comprises (docs/architecture.md, § 7.8) : le portage fait les mêmes.
    if (appels() - avant !== temoin.appels_liquider) {
      ecarts.push(`${nom} : ${appels() - avant} appels de liquider, `
        + `le témoin en déclare ${temoin.appels_liquider}`);
    }
    comparer(obtenu, temoin.resultat, nom, ecarts);
    cas += 1;
  }
  assert.ok(cas > 50, `${cas} cas seulement : les témoins sont-ils à jour ?`);
  assert.deepEqual(ecarts, [], `${ecarts.length} écart(s) sur ${cas} cas`);
});

test("une faute de programme n'est pas présentée comme une faute de saisie", () => {
  // Le portage attrapait toute exception et affichait « Saisie refusée » : un
  // bug du moteur JavaScript accusait donc le lecteur. Ce test l'a vérifié
  // après coup sur un vrai bug — « serie.valeurs is not iterable » s'affichait
  // ainsi. Une saisie réellement invalide doit toujours donner sa phrase ; une
  // faute de programme doit remonter jusqu'à la page, qui dit « Le calcul a
  // échoué » sans mettre la faute sur personne.
  const contexte = new Contexte(paquet);
  const [, refus] = rendre(contexte, "/simuler", { liquidation: "12" });
  assert.match(refus, /Saisie refusée/, "une saisie invalide garde sa phrase");

  const prototype = Object.getPrototypeOf(contexte);
  const vrai = prototype.simuler;
  prototype.simuler = () => { throw new TypeError("bug interne simulé"); };
  try {
    assert.throws(
      () => rendre(contexte, "/simuler", { naissance: "1975", liquidation: "64" }),
      TypeError,
      "une faute de programme doit remonter, non être déguisée en refus",
    );
  } finally {
    prototype.simuler = vrai;
  }
});

// Les pages ne se rejouent pas toutes ici : leurs témoins sont rendus par ce
// même portage, sur ce même paquet (`scripts/construire_temoins.py`), et
// `test_les_temoins_du_portage_sont_a_jour` les rend de nouveau et les compare,
// titre et corps. Les rejouer ici refaisait cette comparaison, vingt secondes
// de plus (feuille de route, action 135, 10 octobre 2026).

test("un paquet d'avant les écarts médians ne fait pas tomber l'accueil", () => {
  // Un bilan écrit avant les écarts médians : l'accueil se tait sur le chiffre.
  // Le site lit son paquet en `force-cache` : un lecteur revenu après le
  // 23 septembre 2026 peut recevoir le nouveau code et l'ancien paquet, dont le
  // bilan ne porte pas les écarts médians. L'accueil ne doit pas en tomber ; il
  // retrouve la réponse d'avant, sans chiffre, et le tableau sa ligne d'avant.
  // Le Python l'exigeait aussi de son rendu, jusqu'à la phase 8 qui l'a retiré.
  const bilan = { ...paquet.bilan_equilibre };
  delete bilan.ecarts_medians;
  const [, corps] = rendre(new Contexte({ ...paquet, bilan_equilibre: bilan }), "/", {});
  const texte = corps.replace(/[ \n]+/g, " ");
  assert.ok(texte.includes("<strong>Le plus souvent, elle sera plus basse que ce "
    + "que le système actuel promet.</strong> Votre retraite vaudra"));
  assert.ok(!texte.includes("baisse médiane"));
  assert.ok(!texte.includes("Votre retraite</th>"));
  assert.ok(texte.includes("c'est une avance, reprise sur la succession. Pour votre cas"));
});

test("Pourquoi changer et Partager lisent le bilan figé, sans rien calculer", () => {
  // Elles ne prennent aucun réglage, et refaisaient le coût entier — cinq
  // secondes chez le lecteur — pour en lire quelques chiffres, plus trois
  // carrières d'exemple. Le paquet les porte depuis le 7 octobre 2026 : qu'une
  // de ces pages se remette à calculer, et ce test le dit.
  const contexte = new Contexte(paquet);
  contexte.cout = () => { throw new Error("la page a recalculé le coût agrégé"); };
  contexte.simuler = () => { throw new Error("la page a simulé une carrière"); };
  for (const chemin of ["/risque", "/partager"]) {
    assert.doesNotThrow(() => rendre(contexte, chemin, {}), chemin);
  }
});

test("un paquet d'avant les dépenses figées rend Pourquoi changer et Partager comme avant", () => {
  // Le site lit son paquet en `force-cache` : un lecteur peut recevoir le
  // nouveau code et un paquet d'avant le 7 octobre 2026, dont le bilan ne
  // porte ni la dépense ni le PIB de chaque année, ni les carrières d'exemple.
  // Les deux pages refont alors le calcul, et rendent la même page.
  const bilan = {
    ...paquet.bilan_equilibre,
    annees: paquet.bilan_equilibre.annees.map(({ depenses, pib, ...reste }) => reste),
  };
  delete bilan.exemples_risque;
  const contexte = new Contexte({ ...paquet, bilan_equilibre: bilan });
  for (const nom of ["risque", "partager"]) {
    const temoin = temoinsPages[nom];
    const rendu = sansBlocJson(rendre(contexte, temoin.chemin, temoin.parametres)[1]);
    assert.equal(temoin.formulaire_retire ? sansFormulaire(rendu) : rendu, recousu(temoin),
      `corps de la page « ${nom} »`);
  }
});

/**
 * Le HTML qu'un témoin a figé, en morceaux d'une ligne ou d'un élément
 * (`retraite_notionnelle/lignes.py`) : une page tenait sur des lignes de
 * centaines de milliers de caractères, que son diff rendait entières.
 */
function recousu(temoin) {
  return temoin.corps.join("");
}

/**
 * Le bloc JSON de la page reprend les chiffres déjà comparés un à un ; ne
 * subsisterait que l'écriture des flottants, que Python et JavaScript ne
 * formatent pas de la même façon. On le retire des deux côtés, comme le fait le
 * générateur de témoins.
 */
function sansBlocJson(html) {
  return html.replace(/(<pre class="json">)[\s\S]*?(<\/pre>)/g, "$1$2");
}

/**
 * Le formulaire d'une page dont il n'est pas le sujet : son témoin n'en fige
 * que la balise (`FORMULAIRE_ENTIER`, dans `scripts/construire_temoins.py`), et
 * la comparaison retire le même bloc.
 */
function sansFormulaire(html) {
  return html.replace(/(<form class="carte"[^>]*>)[\s\S]*?(<\/form>)/g, "$1$2");
}

/**
 * La liquidation unique des régimes alignés, portée dans le moteur du site.
 *
 * Les témoins figés ne la couvrent pas : ils balaient un statut à la fois, et
 * la Lura ne se voit que sur un polypensionné. Le tirage au hasard de
 * `test_le_portage_javascript_concorde…` ne la couvre pas davantage, pour la
 * même raison. Sans cet essai, le portage pourrait couper en deux une carrière
 * que le Python liquide d'un coup, et rien ne le dirait.
 */
test("les régimes alignés se liquident ensemble depuis juillet 2017", () => {
  const contexte = new Contexte(paquet);
  const simulateur = contexte.simulateur();
  const base = (naissance, moisNaissance, age) => {
    const carriere = simulateur.carriereParcours({
      annee_naissance: naissance,
      mois_naissance: moisNaissance,
      sexe: "H",
      age_liquidation: age,
      metiers: [
        { affiliation: "salarie_prive_non_cadre", age_debut: 22, niveau_salaire: 1 },
        { affiliation: "salarie_agricole", age_debut: 42, niveau_salaire: 1 },
      ],
    });
    return simulateur.scenarioActuel.calculer(carriere).pensions_par_regime
      .filter((p) => p.type_calcul !== "points" && p.montant > 0);
  };

  // Né en 1960, parti à 64 ans : une seule retraite de base, celle de la
  // caisse qui a le dossier, sur la carrière entière.
  const unique = base(1960, 1, 64);
  assert.equal(unique.length, 1);
  assert.match(unique[0].detail, /2 caisses liquidées ensemble/);
  assert.match(unique[0].detail, /167\/167/);

  // Né en 1950 : la loi ne le vise pas. Et la borne du 1er juillet 2017 est
  // opposée au mois près, comme en Python.
  assert.equal(base(1950, 1, 62).length, 2);
  assert.equal(base(1955, 1, 62).length, 2);
  assert.equal(base(1955, 9, 62).length, 1);
});

/**
 * Les âges des marins, portés dans le moteur du site : ancienneté à cinquante
 * ans pour vingt-cinq ans de services (R. 2), proportionnelle à cinquante-cinq,
 * spéciale à soixante sans autre pension (R. 5) ou avec l'autre pension de
 * base, levée du plafond de vingt-cinq annuités à cinquante-deux ans et demi
 * (R. 13 b), bonification dès deux enfants (R. 14). Aucun témoin figé ne tient
 * le polypensionné : cet essai le fait.
 */
test("les âges et la bonification des marins sont ceux du Python", () => {
  const contexte = new Contexte(paquet);
  const simulateur = contexte.simulateur();
  const scenario = simulateur.scenarioActuel;
  const parcours = (metiers, age, naissance = 1966, enfants = 0) =>
    simulateur.carriereParcours({
      annee_naissance: naissance, sexe: "H", age_liquidation: age,
      nombre_enfants: enfants, profil_carriere: "plat", metiers,
    });
  const marin = (debut, age, naissance = 1966, enfants = 0) => parcours(
    [{ affiliation: "marin", age_debut: debut, niveau_salaire: 1 }], age, naissance, enfants);

  assert.equal(scenario.calculer(marin(25, 50)).liquidation_ouverte, true);
  assert.equal(scenario.calculer(marin(25.25, 50)).liquidation_ouverte, false);
  assert.equal(ouvrir.ageOuvertureDroit(scenario, marin(30, 50)), 55);
  assert.equal(scenario.calculer(marin(49.75, 59.75)).liquidation_ouverte, false);
  assert.equal(scenario.calculer(marin(50, 60)).liquidation_ouverte, true);

  const poly = parcours([
    { affiliation: "marin", age_debut: 20, niveau_salaire: 1 },
    { affiliation: "salarie_prive_non_cadre", age_debut: 30, niveau_salaire: 1 },
  ], 55);
  assert.ok(ouvrir.ageOuvertureDroit(scenario, poly) > 60);
  assert.equal(scenario.calculer(poly).liquidation_ouverte, false);

  assert.match(scenario.calculer(marin(15.25, 52.5, 1970)).pensions_par_regime[0].detail, /100\/150/);
  assert.match(scenario.calculer(marin(15, 52.5, 1970)).pensions_par_regime[0].detail, /150\/150/);

  const taux = (enfants) => {
    const r = scenario.calculer(marin(25, 60, 1966, enfants));
    const majoration = r.avantages_appliques
      .filter((a) => a.code === "majoration_enfants")
      .reduce((somme, a) => somme + a.montant, 0);
    return majoration / r.pensions_par_regime.reduce((somme, p) => somme + p.montant, 0);
  };
  assert.equal(taux(1), 0);
  assert.ok(Math.abs(taux(2) - 0.05) < 1e-9);
  assert.ok(Math.abs(taux(5) - 0.15) < 1e-9);
});

/**
 * Les sections de santé (action 89, 23 septembre 2026) : minoration par l'âge
 * seul, à deux pentes à la CAVP, par génération à la CARCDSF de 2011 à 2023,
 * taux plein anticipé des mères, majoration pour trois enfants. Les témoins
 * figés n'ont ni mère ni enfant : cet essai rejoue ce que
 * `tests/test_sections_sante.py` tient côté Python.
 */
test("les sections de santé minorent comme leurs règlements", () => {
  const contexte = new Contexte(paquet);
  const simulateur = contexte.simulateur();
  const scenario = simulateur.scenarioActuel;
  const calculer = (affiliation, naissance, age, sexe = "H", enfants = 0, debut = 21) =>
    scenario.calculer(simulateur.carriereParcours({
      annee_naissance: naissance, sexe, age_liquidation: age,
      nombre_enfants: enfants, profil_carriere: "ascendant",
      metiers: [{ affiliation, age_debut: debut, niveau_salaire: 1 }],
    }));
  const coefficient = (resultat, regime) => {
    const detail = resultat.pensions_par_regime.find((p) => p.regime === regime).detail;
    const lu = /coefficient (?:d'anticipation|de majoration) ([0-9.]+)/.exec(detail);
    return lu ? Number(lu[1]) : 1;
  };
  const proche = (a, b) => assert.ok(Math.abs(a - b) < 1e-9, `${a} ≠ ${b}`);

  const dentiste = "chirurgien_dentiste_ou_sage_femme";
  proche(coefficient(calculer(dentiste, 1945, 63.25), "carcdsf_complementaire"), 0.90);
  proche(coefficient(calculer(dentiste, 1955, 64), "carcdsf_complementaire"), 0.82);
  proche(coefficient(calculer(dentiste, 1953, 63), "carcdsf_complementaire"), 0.8375);
  proche(coefficient(calculer(dentiste, 1965, 63), "carcdsf_complementaire"), 0.85);
  proche(coefficient(calculer(dentiste, 1960, 65, "F", 2), "carcdsf_complementaire"), 1);
  proche(coefficient(calculer(dentiste, 1960, 64.75, "F", 2), "carcdsf_complementaire"), 0.8875);
  proche(coefficient(calculer(dentiste, 1960, 65, "H", 2), "carcdsf_complementaire"), 0.90);
  proche(coefficient(calculer(dentiste, 1957, 69), "carcdsf_complementaire"), 1.10);

  proche(coefficient(calculer("pharmacien", 1975, 64), "cavp_complementaire"), 0.91);
  proche(coefficient(calculer("pharmacien", 1954, 64), "cavp_complementaire"), 0.93);
  proche(coefficient(calculer("pharmacien", 1960, 62), "cavp_complementaire"), 0.81);
  proche(coefficient(calculer("veterinaire", 1945, 64), "carpv_complementaire"), 0.95);
  proche(coefficient(calculer("medecin_liberal", 1950, 62.5), "carmf_complementaire"), 0.85);
  proche(coefficient(calculer("auxiliaire_medical", 1958, 62, "H", 0, 30),
    "carpimko_complementaire"), 0.80);

  for (const statut of ["medecin_liberal", dentiste, "pharmacien", "auxiliaire_medical",
    "veterinaire"]) {
    const r = calculer(statut, 1960, 67, "F", 3);
    const majoration = r.avantages_appliques
      .filter((a) => a.code === "majoration_enfants")
      .reduce((somme, a) => somme + a.montant, 0);
    const pensions = r.pensions_par_regime.reduce((somme, p) => somme + p.montant, 0);
    proche(majoration / pensions, 0.10);
  }

  const officier = simulateur.carriereParcours({
    annee_naissance: 1955, sexe: "H", age_liquidation: 64, nombre_enfants: 0,
    profil_carriere: "ascendant",
    metiers: [{ affiliation: "officier_ministeriel", age_debut: 22, niveau_salaire: 1 }],
  });
  assert.equal(ouvrir.ageOuvertureDroit(scenario, officier), 62);
});

test("le seuil d'affiliation de l'élu local est lu comme en Python", () => {
  // L. 382-31 : le régime général n'est dû qu'au-dessus de la moitié du
  // plafond ; en deçà, l'élu n'a que l'Ircantec. Sans revenu, la liste des
  // régimes possibles est rendue telle quelle.
  const affiliations = new Affiliations(paquet);
  assert.deepEqual(affiliations.regimes("elu_local", 2020), ["regime_general", "ircantec"]);
  assert.deepEqual(affiliations.regimes("elu_local", 2020, null, 16000, 41136), ["ircantec"]);
  assert.deepEqual(
    affiliations.regimes("elu_local", 2020, null, 24000, 41136),
    ["regime_general", "ircantec"],
  );
  assert.deepEqual(affiliations.regimes("elu_local", 2010, null, 100000, 34620), ["ircantec"]);
  assert.deepEqual(
    affiliations.regimes("salarie_prive_non_cadre", 2020, null, 1, 41136),
    ["regime_general", "agirc_arrco"],
  );
});

/**
 * Une année non mesurée ne se dit pas certifiée.
 *
 * Le paquet porte l'interpolation de chaque série, et le navigateur
 * l'applique. Les témoins de pages ne peuvent pas couvrir ce chemin : le site
 * n'affiche aucune des années absentes en question. Un portage qui lirait une
 * série d'enquête en escalier rendrait la même VALEUR — donc le même HTML —
 * sous un niveau de fiabilité que le producteur n'a jamais accordé.
 */
test("une année non mesurée ne se dit pas certifiée", () => {
  const serie = paquet.depenses.droits_derives;
  assert.equal(serie.interpolation, "ponctuelle");

  // Un barème garde son niveau entre deux changements : c'est la loi qui le
  // dit, pas une interpolation.
  const barème = new SerieAnnuelle([2000, 2004], [1.0, 2.0], [3, 3], "barème");
  assert.equal(barème.brut(2002).fiabilite, 3);
  assert.equal(barème.brut(2002).valeur, 1.0);

  // Une enquête, non : la valeur reconduite est la même, le niveau tombe.
  const enquête = new SerieAnnuelle([2000, 2004], [1.0, 2.0], [3, 3], "enquête",
    "ponctuelle");
  assert.equal(enquête.brut(2002).valeur, 1.0);
  assert.equal(enquête.brut(2002).fiabilite, Fiabilite.ESTIMEE);
  // Les années publiées gardent le leur.
  assert.equal(enquête.brut(2000).fiabilite, 3);
  assert.equal(enquête.brut(2004).fiabilite, 3);
});

/**
 * La pyramide refuse l'année que l'INSEE ne projette pas.
 *
 * Les témoins de pages ne peuvent pas atteindre ce chemin : rien, dans le
 * site, ne demande la pyramide au-delà de 2070. C'est justement pourquoi il
 * faut un test — un portage qui emprunterait la dernière pyramide rendrait des
 * chiffres PLAUSIBLES, du bon ordre de grandeur, et sous le nom d'une cohorte
 * qui n'est pas la leur. Le Python refuse ; le JavaScript doit refuser de la
 * même façon, et sur les mêmes bornes.
 */
test("la pyramide refuse l'année que l'INSEE ne projette pas", () => {
  const population = new Contexte(paquet).population();
  const horizon = population.derniereAnnee;

  // En deçà, on emprunte : la dépense observée commence trois ans avant la
  // pyramide, et ces années-là prennent celle de 1962.
  assert.equal(population.effectif(80, 1959), population.effectif(80, 1962));
  assert.ok(population.effectif(80, horizon) > 0);

  // Au-delà, on refuse — y compris pour un âge hors plage, qui rendrait zéro
  // sans que la question ait eu de sens.
  assert.throws(() => population.effectif(85, horizon + 15), /au-delà/);
  assert.throws(() => population.effectif(200, horizon + 1), /au-delà/);
  // La tranche refuse aussi, VIDE comprise : déléguer le refus aux âges la
  // laisserait passer.
  assert.throws(() => population.effectifTranche(65, 80, horizon + 1), /au-delà/);
  assert.throws(() => population.effectifTranche(80, 65, horizon + 1), /au-delà/);
});

/**
 * Le ruban d'écart sur un trou de série.
 *
 * Les témoins de pages couvrent déjà tout ce que le ruban fait quand les deux
 * séries sont pleines — la page Coût en trace deux, dont les courbes se
 * croisent quatre fois, et le HTML est comparé caractère par caractère. Le
 * chemin qu'ils n'atteignent pas est celui d'une année manquante : là, le
 * ruban ne doit RIEN peindre, un écart interpolé par-dessus un trou affirmant
 * quelque chose que personne n'a mesuré.
 */
test("le ruban d'écart se tait sur une année manquante", () => {
  const pleine = new gabarit.Serie("A", [12.0, 11.0, 10.0], "var(--serie-5)");
  const trouee = new gabarit.Serie("B", [10.0, null, 12.0], "var(--serie-2)");
  const avec = gabarit.graphique("Essai", [2000, 2001, 2002], [pleine, trouee],
    "", false, 0, true, null, "", [], "Année", [0, 1]);
  assert.equal(avec.includes('class="ecart'), false);

  // Et, série pleine, il peint bien des deux côtés du croisement.
  const seconde = new gabarit.Serie("B", [10.0, 11.0, 12.0], "var(--serie-2)");
  const peint = gabarit.graphique("Essai", [2000, 2001, 2002], [pleine, seconde],
    "", false, 0, true, null, "", [], "Année", [0, 1]);
  assert.equal((peint.match(/class="ecart plus"/g) || []).length, 1);
  assert.equal((peint.match(/class="ecart moins"/g) || []).length, 1);
});

/**
 * La surcote et le minimum contributif, sur les exemples de la circulaire
 * Cnav 2018-04 (point 3.4) : le même calcul que le Python, chiffre pour
 * chiffre, y compris la règle d'avant avril 2009 qu'aucun témoin n'atteint.
 */
test("la surcote s'ajoute au minimum comme la circulaire le calcule", () => {
  const apres2009 = 621 * 1.025 + complementMinimum(621, 645.07, 1.025, [2009, 10]);
  assert.ok(Math.abs(apres2009 - 660.59) < 0.01, `${apres2009}`);
  const avant2009 = 621 * 1.015 + complementMinimum(621, 633.61, 1.015, [2008, 1]);
  assert.ok(Math.abs(avant2009 - 633.61) < 0.01, `${avant2009}`);
  assert.equal(complementMinimum(700, 645.07, 1.025, [2009, 10]), 0);
  assert.equal(complementMinimum(630, 633.61, 1.015, [2008, 1]), 0);
  assert.equal(complementMinimum(621, 645.07, 1.025, [2009, 3]),
    Math.max(0, 645.07 - 621 * 1.025));
});

/**
 * Les huit exemples chiffrés des circulaires Cnav 2005/30 et 2009/17, et la
 * majoration sans distinction de 2004 : le même calcul que le Python
 * (`test_les_exemples_des_circulaires_de_2005_et_2009_sont_rejoues`), dont les
 * témoins n'atteignent ni les polypensionnés ni 2004.
 */
test("le minimum se calcule comme les circulaires de 2005 et 2009", () => {
  const eligible = (regime, cotisee, proratisation, requis, autres = 0, cotiseeAutres = 0) => ({
    indice: 0, prorataAssurance: regime / proratisation,
    prorataCotise: Math.min(cotisee, proratisation) / proratisation, tauxPlein: true,
    dureeRegime: regime, cotiseeRegime: cotisee, proratisation, requis,
    dureeTousRegimes: regime + autres, cotiseeTousRegimes: cotisee + cotiseeAutres,
    porteAvpf: true,
  });
  const cas2005 = [
    [[162, 156, 0, 0], 6840.51], [[140, 140, 0, 0], 6218.63], [[140, 40, 0, 0], 6089.26],
    [[100, 90, 56, 54], 4428.94], [[60, 50, 140, 130], 2052.14], [[142, 110, 30, 30], 5632.43],
  ];
  for (const [[regime, cotisee, autres, cotiseeAutres], attendu] of cas2005) {
    const plancher = plancherDuRegime(eligible(regime, cotisee, 154, 160, autres, cotiseeAutres),
      6641.28, 6840.51, true, true);
    assert.ok(Math.abs(plancher - attendu) < 0.03, `${regime}/${cotisee} : ${plancher}`);
  }
  const regle = { majoration: "periodes_cotisees", seuil_trimestres_cotises: 120 };
  assert.ok(majorationOuverte(regle, 144));
  assert.ok(!majorationOuverte(regle, 118));
  assert.ok(Math.abs(plancherDuRegime(eligible(100, 90, 161, 161, 56, 54), 584.48, 638.68,
    true, true) - 393.32) < 0.01);
  assert.ok(Math.abs(plancherDuRegime(eligible(150, 118, 152, 160), 584.48, 638.68,
    false, true) - 576.78) < 0.01);
  // De janvier 2004 à juin 2005 : le majoré, au prorata de la durée d'assurance.
  const transitoire = { majoration: "sans_distinction" };
  const mono = selonLaRegle(eligible(140, 40, 152, 160), transitoire, 0);
  assert.ok(Math.abs(plancherDuRegime(mono, 6511.06, 6706.39, true, true)
    - 6706.39 * 140 / 152) < 1e-9);
  const poly = selonLaRegle(eligible(60, 10, 152, 160, 140, 130), transitoire, 0);
  assert.ok(Math.abs(plancherDuRegime(poly, 6511.06, 6706.39, true, true)
    - 6706.39 * 60 / 200) < 1e-9);
});

/**
 * Les limites de R. 351-12 au chômage non indemnisé, sur les cas du test
 * Python `test_le_chomage_non_indemnise_ne_valide_que_dans_les_limites_de_r_351_12` :
 * rien avant 1980, la première période à quatre trimestres avant 2011 et six
 * depuis, une période ultérieure à un an après un chômage indemnisé, cinq ans
 * pour le senior qui ne retravaille pas. Le témoin `fin_activite_chomage_non_indemnise`
 * n'atteint que la première période.
 */
test("le chômage non indemnisé ne valide que dans les limites de R. 351-12", () => {
  const carriere = (anneeNaissance, debut, fin, motifs) => {
    const lignes = [];
    for (let annee = debut; annee <= fin; annee += 1) {
      const motif = motifs[annee] ?? "emploi";
      lignes.push(new AnneeCarriere({
        annee, revenu: motif === "emploi" ? 30000 : 0,
        affiliation: "salarie_prive_non_cadre", type_periode: motif,
        trimestres_valides: 4, cotisations_versees: motif === "emploi",
      }));
    }
    const limitees = limiterChomageNonIndemnise(lignes, anneeNaissance);
    return Object.fromEntries(limitees.filter((l) => motifs[l.annee])
      .map((l) => [l.annee, l.trimestres_valides]));
  };
  const nonIndemnise = (debut, fin) => Object.fromEntries(
    Array.from({ length: fin - debut + 1 }, (_, i) => [debut + i, "chomage_non_indemnise"]));
  const somme = (valides) => Object.values(valides).reduce((a, b) => a + b, 0);

  assert.deepEqual(carriere(1955, 1975, 2018, nonIndemnise(1977, 1981)),
    { 1977: 0, 1978: 0, 1979: 0, 1980: 4, 1981: 0 });
  assert.equal(somme(carriere(1975, 1995, 2039, nonIndemnise(2012, 2015))), 6);
  assert.equal(somme(carriere(1975, 1995, 2039, nonIndemnise(2003, 2005))), 4);
  assert.deepEqual(carriere(1975, 1995, 2039, nonIndemnise(2009, 2012)),
    { 2009: 4, 2010: 0, 2011: 2, 2012: 0 });
  assert.deepEqual(carriere(1975, 1995, 2039,
    { 2003: "chomage_non_indemnise", ...nonIndemnise(2015, 2016) }),
  { 2003: 4, 2015: 2, 2016: 0 });
  assert.deepEqual(carriere(1975, 1995, 2039, {
    2003: "chomage_non_indemnise", 2008: "chomage_indemnise", ...nonIndemnise(2009, 2011),
  }), { 2003: 4, 2008: 4, 2009: 4, 2010: 0, 2011: 0 });
  const senior = {
    1990: "chomage_non_indemnise", 2012: "chomage_indemnise", ...nonIndemnise(2013, 2016),
  };
  const ulterieures = (valides) => [2013, 2014, 2015, 2016]
    .reduce((total, annee) => total + valides[annee], 0);
  assert.equal(ulterieures(carriere(1955, 1975, 2016, senior)), 16);
  assert.equal(ulterieures(carriere(1965, 1985, 2016, senior)), 4);
});

/**
 * Le plafond des primes du RAFP : « dans la limite de 20 % du traitement
 * indiciaire brut total » (décret n° 2004-569, art. 2). Deux agentes au même
 * traitement, primes au plafond pour l'une, au-delà pour l'autre : même
 * retraite additionnelle, même compartiment de capitalisation. Rejoue
 * `test_les_primes_au_dela_du_plafond_ne_cotisent_pas_au_rafp`.
 */
test("les primes cotisent au RAFP dans la limite de 20 % du traitement", () => {
  const contexte = new Contexte(paquet);
  const simulateur = contexte.simulateur();
  const periode = simulateur.catalogue.obtenir("rafp").periode(2026);
  assert.ok(Math.abs(periode.plafond_primes_traitement - 0.20) < 1e-12);
  assert.ok(Math.abs(periode.partDuRevenu(40000, 0.10) - 4000) < 1e-6);
  assert.ok(Math.abs(periode.partDuRevenu(40000, 0.25) - 6000) < 1e-6);

  const profil = {
    annee_naissance: 1975, sexe: "F", affiliation: "fonctionnaire_etat",
    age_debut: 23, age_liquidation: 64,
  };
  const retraiteAdditionnelle = (niveau, primes) => {
    const resultat = simulateur.simuler(simulateur.carriereSimple({
      ...profil, niveau_salaire: niveau, part_primes: primes,
    }));
    const pension = resultat.actuel.pensions_par_regime.find((p) => p.regime === "rafp");
    return [pension.montant, resultat.notionnel_retroactif.capital_capitalisation];
  };
  const [pension, capital] = retraiteAdditionnelle(0.9, 1 / 6);
  const [pensionAuDela, capitalAuDela] = retraiteAdditionnelle(1.0, 0.25);
  assert.ok(pension > 0 && capital > 0);
  assert.ok(Math.abs(pensionAuDela / pension - 1) < 1e-9, `${pensionAuDela} ≠ ${pension}`);
  assert.ok(Math.abs(capitalAuDela / capital - 1) < 1e-9, `${capitalAuDela} ≠ ${capital}`);
});

test("les adresses des pages parties rendent celles qui les ont remplacées", () => {
  // « Cumul versé » et « Sources » ne sont plus des pages (23 septembre
  // 2026) ; leurs adresses, que le site parent et des partages portent,
  // rendent les résultats du simulateur et la page Méthode et sources. Le
  // modèle Python le tient de son côté ; ici, le portage fait de même.
  const contexte = new Contexte(paquet);
  const carriere = { naissance: "1975-01-01", debut: "1996-01-01",
    liquidation: "2039-01-01", statut: "salarie_prive_non_cadre" };
  assert.deepEqual(rendre(contexte, "/donnees", {}), rendre(contexte, "/methode", {}));
  const cumul = rendre(contexte, "/trajectoire", carriere);
  assert.deepEqual(cumul, rendre(contexte, "/simuler", carriere));
  assert.match(cumul[1], /<details class="section" id="cumul">/);
});

/**
 * Les points gratuits de la RCO agricole : cent par année de chef d'avant
 * 2003, dans la limite de 37,5 ans moins les années de RCO (D. 732-154), au
 * taux plein — par la durée avant septembre 2023, par la durée ou l'âge depuis.
 * Même arithmétique que `test_le_chef_d_exploitation_recoit_ses_points_gratuits_de_rco`.
 */
test("le chef d'exploitation reçoit ses points gratuits de RCO", () => {
  const contexte = new Contexte(paquet);
  const simulateur = contexte.simulateur();
  const scenario = simulateur.scenarioActuel;
  // Des chefs nés le 1er janvier, qui partent au 1er janvier de l'année dite.
  const chef = (naissance, debut, depart) => simulateur.carriereSimple({
    annee_naissance: naissance, sexe: "H", affiliation: "exploitant_agricole",
    age_debut: debut, age_liquidation: depart, niveau_salaire: 0.5,
    jour_naissance: 1,
  });
  const rco = (resultat) => [
    resultat.pensions_par_regime.find((p) => p.regime === "msa_rco") ?? null,
    resultat.avantages_appliques.find((a) => a.code === "points_gratuits_rco") ?? null,
  ];

  const carriere = chef(1955, 20, 64);
  const resultat = scenario.calculer(carriere);
  const [pension, ligne] = rco(resultat);
  assert.ok(pension.detail.includes("(dont 2,150.00 points gratuits)"), pension.detail);
  const sansPoints = scenario.calculer(carriere, false, true, true, true, false);
  const [sans] = rco(sansPoints);
  assert.ok(!sans.detail.includes("gratuits"));
  // Le complément différentiel de la RCO s'ajoute aux points, et comble ce que
  // les points gratuits ne donnent plus : il se retire des deux côtés.
  const pointsSeuls = (calcul, pensionRco) => pensionRco.montant
    - calcul.avantages_appliques.filter((a) => a.code === "complement_differentiel_rco")
      .reduce((s, a) => s + a.montant, 0);
  assert.ok(Math.abs(ligne.montant
    - (pointsSeuls(resultat, pension) - pointsSeuls(sansPoints, sans))) < 1e-6);
  const somme = resultat.avantages_appliques.reduce((s, a) => s + a.montant, 0);
  assert.ok(Math.abs(resultat.pension_annuelle - resultat.total_contributif - somme) < 1e-6);
  const [contributif] = rco(scenario.calculer(carriere, false, false));
  assert.ok(Math.abs(contributif.montant - pointsSeuls(sansPoints, sans)) < 1e-9);

  const [depart2003] = rco(scenario.calculer(chef(1939, 20, 64)));
  assert.ok(depart2003.detail.startsWith("3,750.00 points"), depart2003.detail);
  const [parAge] = rco(scenario.calculer(chef(1958, 30, 67)));
  assert.ok(parAge.detail.includes("(dont 1,500.00 points gratuits)"), parAge.detail);
  const [avant2023, ligneAvant2023] = rco(scenario.calculer(chef(1955, 40, 64)));
  assert.ok(!avant2023.detail.includes("gratuits") && ligneAvant2023 === null);
});

/**
 * L'Arrco des cultes : depuis 2006, pour qui perçoit une rémunération
 * individuelle (L. 921-1), sur le forfait du SMIC que la CAVIMAC applique à
 * toutes ses cotisations. Même arithmétique que
 * `test_le_ministre_du_culte_remunere_cotise_a_l_arrco_sur_le_forfait`.
 */
test("le ministre du culte rémunéré cotise à l'Arrco sur le forfait", () => {
  const contexte = new Contexte(paquet);
  const simulateur = contexte.simulateur();
  assert.deepEqual(simulateur.affiliations.regimes("ministre_du_culte", 2005), ["cavimac"]);
  assert.deepEqual(simulateur.affiliations.regimes("ministre_du_culte", 2006),
    ["cavimac", "arrco_cultes"]);
  assert.deepEqual(simulateur.affiliations.regimes("membre_congregation", 2026), ["cavimac"]);
  // Né le 1er janvier 1961, il part le 1er janvier 2026.
  const rco = (statut, niveau) => simulateur.scenarioActuel.calculer(simulateur.carriereSimple({
    annee_naissance: 1961, sexe: "H", affiliation: statut, age_debut: 25,
    age_liquidation: 65, niveau_salaire: niveau, jour_naissance: 1,
  })).pensions_par_regime.find((p) => p.regime === "arrco_cultes") ?? null;
  assert.equal(rco("membre_congregation", 1.0), null);
  const pension = rco("ministre_du_culte", 0.5);
  assert.ok(pension.montant > 0);
  assert.ok(Math.abs(rco("ministre_du_culte", 2.0).montant - pension.montant) < 1e-9);
  assert.ok(pension.detail.startsWith("1,348.24 points"), pension.detail);
});

/**
 * Le salaire annuel moyen de la CAVIMAC est fait du forfait du SMIC, « une base
 * SMIC pour tous les assurés cultuels » : le revenu déclaré n'y entre pas. Même
 * arithmétique que `test_le_salaire_de_reference_des_cultes_est_fait_du_forfait`.
 */
test("le salaire de référence des cultes est fait du forfait", () => {
  const contexte = new Contexte(paquet);
  const simulateur = contexte.simulateur();
  const cavimac = (statut, niveau) => simulateur.scenarioActuel.calculer(
    simulateur.carriereSimple({
      annee_naissance: 1965, sexe: "H", affiliation: statut, age_debut: 25,
      age_liquidation: 65, niveau_salaire: niveau,
    }),
  ).pensions_par_regime.find((p) => p.regime === "cavimac");
  const reference = cavimac("ministre_du_culte", 1.0);
  for (const [statut, niveau] of [["ministre_du_culte", 0.3], ["ministre_du_culte", 1.5],
    ["membre_congregation", 2.0]]) {
    assert.ok(Math.abs(cavimac(statut, niveau).montant - reference.montant) < 1e-9);
  }
});

/**
 * Le portage de `test_les_quotients_projetes_remplacent_la_loi_aux_annees_projetees`
 * (tests/test_donnees.py) : de 2026 à 2125, la table de l'INSEE, âge par âge ;
 * au-delà, celle de 2125 ; en 2025, la loi.
 */
test("les quotients projetés de l'INSEE remplacent la loi aux années projetées", () => {
  const mortalite = new DonneesMortalite(paquet);
  const projetes = paquet.quotients_projetes;
  assert.deepEqual(mortalite.anneesProjetees, [2026, 2125]);
  for (const [annee, sexe, age] of [[2026, "F", 64], [2050, "H", 70], [2125, "F", 95]]) {
    assert.equal(mortalite.survieAnnuelle(age, annee, sexe),
      1 - projetes[`${annee}|${sexe}`][String(age)], `${annee} ${sexe} ${age}`);
  }
  assert.equal(mortalite.survieAnnuelle(90, 2140, "H"), 1 - projetes["2125|H"]["90"]);
  assert.equal(mortalite.survieAnnuelle(70, 2025, "H"), mortalite.loi(2025, "H").survie(70, 1));
});

test("le préfinancement du diviseur se rend sur la pension servie", () => {
  // Le portage de `test_le_prefinancement_du_diviseur_se_rend_sur_la_pension_servie`
  // (tests/test_moteur.py) : sous ν, la pension servie se revalorise au taux du
  // compte divisé par 1 + ν, comme la pension suédoise à 1,6 %.
  const contexte = new Contexte(paquet);
  const sans = contexte.simulateur({ ...PARAMETRES_DEFAUT }).revalorisationServie;
  const avec = contexte.simulateur(
    { ...PARAMETRES_DEFAUT, taux_anticipe_conversion: 0.016 }).revalorisationServie;
  for (const [liquidation, annee] of [[2000, 2001], [2010, 2025], [1990, 2026]]) {
    const attendu = sans.coefficient(liquidation, annee) / 1.016 ** (annee - liquidation);
    assert.ok(Math.abs(avec.coefficient(liquidation, annee) / attendu - 1) < 1e-12,
      `${liquidation} → ${annee} : ${avec.coefficient(liquidation, annee)} contre ${attendu}`);
  }
  assert.equal(avec.coefficient(2010, 2010), 1);
});

/**
 * Le portage de `test_la_moyenne_suit_la_version_de_la_date_d_effet`
 * (tests/test_salaire_annuel_moyen.py) : chaque version de la fiche
 * `salaire_annuel_moyen`, sur les mêmes quatre années.
 */
test("le salaire annuel moyen suit la version de sa date d'effet", () => {
  const valeurs = [[1960, 1000.0], [1961, 4000.0], [1962, 3000.0], [1963, 500.0]];
  const trimestres = new Map([[1960, [4, 0]], [1961, [2, 2]], [1962, [4, 0]], [1963, [0, 0]]]);
  const validantes = new Set([1960, 1961, 1962]);
  const regle = (parametres = {}) => ({
    selection: "meilleures", avant_la_liquidation: false, calcul: "annuel",
    trimestres_comptes: "cotises_et_assimiles", annees_assimilees_exclues: false,
    annees_sans_trimestre: "retenues", ...parametres,
  });
  const proche = (obtenu, attendu) => assert.ok(Math.abs(obtenu - attendu) < 1e-9,
    `${obtenu} contre ${attendu}`);
  proche(moyenneSelonLaRegle(regle({ annees_sans_trimestre: "exclues" }), valeurs,
    trimestres, validantes, 10, 9999), 8000 / 3);
  proche(moyenneSelonLaRegle(regle(), valeurs, trimestres, validantes, 10, 9999), 8500 / 4);
  assert.equal(moyenneSelonLaRegle(regle(), valeurs, trimestres, validantes, 2, 9999), 3500);
  proche(moyenneSelonLaRegle(regle({ calcul: "trimestriel" }), valeurs, trimestres,
    validantes, 10, 9999), 8500 * 4 / 12);
  const avant1948 = regle({
    selection: "dernieres", calcul: "trimestriel", trimestres_comptes: "cotises",
    annees_assimilees_exclues: true,
  });
  proche(moyenneSelonLaRegle(avant1948, valeurs, trimestres, validantes, 2, 1963), 2000);
  proche(moyenneSelonLaRegle({ ...avant1948, avant_la_liquidation: true }, valeurs,
    trimestres, validantes, 2, 1963), 3500);
});

/**
 * Le portage de `test_l_assiette_de_l_avpf_est_celle_de_la_cnav` et de
 * `test_la_colonne_de_revalorisation_est_celle_de_la_date_d_effet`
 * (tests/test_salaire_annuel_moyen.py).
 */
test("l'assiette de l'AVPF et la colonne de revalorisation sont celles de la Cnav", () => {
  const macro = new DonneesMacro(paquet);
  // Relatif : l'assiette s'écrit à six décimales dans le fichier de la Cnav.
  const proche = (obtenu, attendu) => assert.ok(Math.abs(obtenu / attendu - 1) < 1e-8,
    `${obtenu} contre ${attendu}`);
  assert.equal(macro.revenuAvpf(1971), 0);
  proche(macro.revenuAvpf(1972), 6 * 667.32 / 6.55957);
  proche(macro.revenuAvpf(2021), 12 * 1715.35);
  proche(macro.revenuAvpf(2026), 12 * 2031.38);
  proche(macro.revenuAvpf(2027), 2028 * 12.31);
  const lu = (depart, arrivee, mois) => macro.coefficientRevalorisationPorteeAuCompte(
    depart, arrivee, mois);
  proche(lu(1970, 1990, 1), 5.629);
  proche(lu(1947, 1949, 6), 1.6);
  proche(lu(1990, 2013, 5), 1.431);
  assert.equal(lu(1954, 1955, 2), 1);
});

/**
 * Le portage des montants de `test_avant_2007_le_minimum_vieillesse_tient_en_deux_etages`
 * (tests/test_liquidation.py) : les deux étages d'avant l'ASPA, sur la table du paquet.
 */
test("avant 2007, le minimum vieillesse tient en deux étages", () => {
  const macro = new DonneesMacro(paquet);
  const minimum = new MinimumVieillesse(paquet, macro);
  const francs = (montant) => montant / 6.55957;
  const proche = (obtenu, attendu) => assert.ok(Math.abs(obtenu - attendu) < 1e-6,
    `${obtenu} contre ${attendu}`);
  const en1970 = minimum.deuxEtages(1970);
  for (const [pension, attendu] of [[0, 3000], [2000, 1250], [3500, 1000], [4500, 0]]) {
    const [montant, plafond] = avantLAspa(en1970, PERSONNE_SEULE, francs(pension), 0);
    proche(montant, francs(attendu));
    proche(plafond, francs(4500));
  }
  const [premier, sansPlafond] = avantLAspa(minimum.deuxEtages(1950), PERSONNE_SEULE,
    francs(100), 0);
  proche(premier, francs(350));
  assert.equal(sansPlafond, null);
  const en1990 = minimum.deuxEtages(1990);
  proche(avantLAspa(en1990, DEUX_ALLOCATAIRES, 0, 0)[0],
    francs(14990 + (63110 - 29980) / 2));
  proche(avantLAspa(en1990, COUPLE, 0, francs(30000))[0], francs(14990 + 63110 - 44990));
  assert.equal(avantLAspa(en1990, COUPLE, 0, francs(70000))[0], 0);
  assert.equal(minimum.deuxEtages(2007), null);
});

/**
 * Le portage de `test_avant_1972_le_trimestre_se_valide_au_trimestre_de_l_avts`
 * (tests/test_salaire_annuel_moyen.py) : R. 351-9, 18 F de 1946 à 1948, puis le
 * trimestre de l'allocation aux vieux travailleurs salariés au 1er janvier.
 */
test("avant 1972, le trimestre se valide au trimestre de l'AVTS", () => {
  const macro = new DonneesMacro(paquet);
  const valides = (francs, annee) => macro.trimestresValides(francs / 6.55957, annee);
  assert.equal(valides(1, 1940), 4);
  assert.deepEqual([17.99, 18, 71.99, 72].map((f) => valides(f, 1946)), [0, 1, 3, 4]);
  assert.deepEqual([84.99, 85, 170].map((f) => valides(f, 1949)), [0, 1, 2]);
  assert.deepEqual([180.95, 723.79, 723.8].map((f) => valides(f, 1962)), [1, 3, 4]);
  assert.deepEqual([199.99, 200].map((f) => valides(f, 1963)), [0, 1]);
  assert.deepEqual([437.49, 437.5, 1749, 1750].map((f) => valides(f, 1971)), [0, 1, 3, 4]);
  assert.deepEqual([787, 788].map((f) => valides(f, 1972)), [0, 1]);
});
